import fitz  # PyMuPDF
import asyncio
import aiohttp
import re
import time
import google.generativeai as genai

# ======= CONFIG =======
GROQ_API_KEY = "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"
GEMINI_API_KEY = "AIzaSyAbQ2NESP_kwIXdAYHeaPtJpE9DRoubv-o"
GROQ_MODEL = "llama-3.1-8b-instant"  # current supported Groq model
GEMINI_MODEL = "gemini-1.5-flash"

CHUNK_SIZE_WORDS = 250  # ~350 tokens per chunk
MAX_CONCURRENT_REQUESTS = 1
MAX_RETRIES = 3

# This controls how many summaries to combine per hierarchical batch
HIERARCHICAL_BATCH_SIZE = 5
# ======================

def extract_pdf_text(path):
    doc = fitz.open(path)
    return "\n".join(page.get_text() for page in doc)

def chunk_text(text, chunk_size=CHUNK_SIZE_WORDS):
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def extract_wait_time(resp_json):
    msg = resp_json.get("error", {}).get("message", "")
    match = re.search(r"(\d+\.\d+)s", msg)
    return float(match.group(1)) if match else 10.0

async def groq_summarize(session, text, attempt=1):
    # url = "https://6b4249c8a16c.ngrok-free.app/chat"
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    json_data = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": f"Summarize this clearly:\n\n{text}"}],
        "temperature": 0.3,
    }

    try:
        async with session.post(url, headers=headers, json=json_data) as resp:
            resp_json = await resp.json()

            if "error" in resp_json:
                if resp_json["error"].get("code") == "rate_limit_exceeded":
                    wait = extract_wait_time(resp_json)
                    print(f"⚠ Rate limit exceeded. Waiting {wait:.1f}s before retrying...")
                    await asyncio.sleep(wait)
                    if attempt < MAX_RETRIES:
                        return await groq_summarize(session, text, attempt + 1)
                print(f"⚠ Groq API error (attempt {attempt}): {resp_json}")
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(2 * attempt)
                    return await groq_summarize(session, text, attempt + 1)
                return "[ERROR: Failed to summarize chunk]"

            if "choices" in resp_json:
                return resp_json["choices"][0]["message"]["content"]

            print(f"⚠ Unexpected Groq response (attempt {attempt}): {resp_json}")
            if attempt < MAX_RETRIES:
                await asyncio.sleep(2 * attempt)
                return await groq_summarize(session, text, attempt + 1)
            return "[ERROR: Unexpected Groq response]"

    except Exception as e:
        print(f"❌ Exception (attempt {attempt}): {e}")
        if attempt < MAX_RETRIES:
            await asyncio.sleep(2 * attempt)
            return await groq_summarize(session, text, attempt + 1)
        return "[ERROR: Network failure]"

def gemini_explain_and_questions(summary):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    prompt = (
        f"give detailed explanation of each concept in detail with real world example. \n"
       f"Create detailed flashcards for the following content. For each key concept, provide:\n"
        f"1. A clear and concise explanation of the core concept.\n"
        f"2. A relevant real-world example that illustrates the concept.\n\n"
        f"Do not include any questions. Present each flashcard as a separate section with the concept title, explanation, and example.\n"
        f"---\n\nCONTENT:\n{summary}"
    )
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"[ERROR with Gemini API: {e}]"

async def hierarchical_summarize(session, summaries, batch_size=HIERARCHICAL_BATCH_SIZE):
    # Base case: If summaries fit into a single batch, summarize and return
    if len(summaries) <= batch_size:
        combined_text = "\n\n".join(summaries)
        return await groq_summarize(session, combined_text)

    # Otherwise, summarize summaries in batches recursively
    new_summaries = []
    for i in range(0, len(summaries), batch_size):
        batch = summaries[i:i+batch_size]
        combined_text = "\n\n".join(batch)
        print(f"Hierarchical summarization batch: Summarizing batch of {len(batch)} summaries...")
        batch_summary = await groq_summarize(session, combined_text)
        new_summaries.append(batch_summary)

    # Recursive call on the new smaller summary list
    return await hierarchical_summarize(session, new_summaries, batch_size)

async def process_pdf_async(path):
    print("Extracting PDF text...")
    pdf_text = extract_pdf_text(path)

    print("Chunking text...")
    chunks = chunk_text(pdf_text, CHUNK_SIZE_WORDS)
    print(f"Total chunks: {len(chunks)}")

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    async with aiohttp.ClientSession() as session:

        async def limited_summarize(chunk):
            async with semaphore:
                return await groq_summarize(session, chunk)

        # First pass: summarize each chunk
        chunk_summaries = []
        for i, chunk in enumerate(chunks, start=1):
            print(f"Summarizing chunk {i}/{len(chunks)}...")
            summary = await limited_summarize(chunk)
            chunk_summaries.append(summary)

        # Second pass: hierarchical summarization of all chunk summaries
        print("Creating final paper summary with hierarchical summarization...")
        final_summary = await hierarchical_summarize(session, chunk_summaries)

    print("Generating explanation and questions with Gemini...")
    explanation_and_questions = gemini_explain_and_questions(final_summary)

    return final_summary, explanation_and_questions

if __name__ == "__main__":
    import sys
    import time

    if len(sys.argv) < 2:
        print("Usage: python script.py <research_paper.pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    start = time.time()
    summary, explanation = asyncio.run(process_pdf_async(pdf_path))
    total_time = time.time() - start

    with open("output_summary.txt", "w", encoding="utf-8") as f:
        f.write("=== Summary ===\n")
        f.write(summary + "\n\n=== Explanation & Questions ===\n")
        f.write(explanation)

    print(f"✅ Done in {total_time:.1f}s. Output saved to output_summary.txt")
