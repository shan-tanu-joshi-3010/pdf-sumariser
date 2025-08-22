# PDF Summariser

PDF Summariser is a simple tool that allows you to upload PDF documents and receive concise summaries of their content. This project is designed to make understanding lengthy PDFs faster and easier, whether you're a student, researcher, or professional.

## Features

- **Upload PDF files:** Easily select and upload your PDF documents.
- **Automatic summarization:** Get a clear, short summary of your PDF’s main points using state-of-the-art language models.
- **User-friendly interface:** Intuitive design for quick and easy use.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/shan-tanu-joshi-3010/pdf-sumariser.git
   cd pdf-sumariser
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the application:**
   ```bash
   python app.py
   ```
2. **Open your web browser** and go to `http://localhost:5000`.
3. **Upload a PDF file** and click "Summarise" to get your summary.

## Publishing Your App Over The Internet Using Ngrok

Ngrok allows you to expose your locally running app to the internet with a public URL.

1. **Download and install ngrok:**  
   Visit [ngrok.com](https://ngrok.com/download) and download the version for your system.

2. **Run your PDF Summariser app locally** (see above).

3. **Expose your local server (port 5000) using ngrok:**
   ```bash
   ngrok http 5000 --host-header="localhost:5000"
   ```

4. **Copy the public URL** shown in your terminal (e.g., `https://abcdefg.ngrok.io`) and share it.  
   Anyone with this link will be able to access your PDF Summariser app over the internet.

**Note:** The ngrok tunnel will only be active while ngrok is running. Restart ngrok each time you restart your app, and you will get a new public URL.

## Technologies Used

- Python
- Flask (or your web framework)
- PDF parsing libraries (e.g., PyPDF2, pdfplumber)
- NLP libraries (e.g., Hugging Face Transformers, OpenAI GPT)
- Ngrok (for tunneling and internet publishing)

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.

## Contact

For questions or suggestions, reach out to [shan-tanu-joshi-3010](https://github.com/shan-tanu-joshi-3010).
