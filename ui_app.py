# ui_app.py
import streamlit as st
import asyncio
import tempfile
from pathlib import Path
from script import process_pdf_async  # Import your backend script functions

st.set_page_config(page_title="PDF Research Paper Summarizer", layout="wide")

st.title("📄 Research Paper Summarizer & Flashcard Generator")
st.write("Upload a PDF research paper, and this tool will summarize it and create detailed flashcards with real-world examples.")

uploaded_pdf = st.file_uploader("Upload your PDF", type=["pdf"])

if uploaded_pdf is not None:
    # Save uploaded PDF to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_pdf.read())
        temp_pdf_path = tmp_file.name

    if st.button("Process PDF"):
        with st.spinner("⏳ Processing your PDF... This may take a few minutes..."):
            try:
                # Run backend
                summary, explanation = asyncio.run(process_pdf_async(temp_pdf_path))

                # Show results
                st.subheader("📌 Summary")
                st.write(summary)

                st.subheader("📝 Flashcards (Detailed Concepts & Examples)")
                st.write(explanation)

                # Save to file
                output_file = Path("output_summary.txt")
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write("=== Summary ===\n")
                    f.write(summary + "\n\n=== Flashcards ===\n")
                    f.write(explanation)

                st.success(f"✅ Processing complete! Results saved to {output_file.resolve()}")
                st.download_button("📥 Download Results", data=open(output_file, "rb").read(), file_name="output_summary.txt")

            except Exception as e:
                st.error(f"❌ An error occurred: {e}")
