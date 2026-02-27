# RAG Document Chatbot

A Streamlit-based Retrieval-Augmented Generation (RAG) chatbot that allows users to securely log in, upload documents (PDF, TXT, DOCX, Images), and query them via natural language.

## Features
- **Firebase Auth & DB:** Secure login and persistent chat history.
- **Fast Local Vector Search:** In-memory ChromaDB with `BAAI/bge-base-en-v1.5` embeddings.
- **Streaming LLM:** Instant, typed-out responses via Groq (`llama-3.1-8b-instant`).
- **Web Search Fallback:** Automatically searches the web (via SerpApi) if document context lacks the answer, using **BM25 algorithm** to rank and extract the most relevant snippet.
- **Tesseract OCR:** Extracts text from uploaded `.png`/`.jpg` files.

## Setup

1. **Install dependencies:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r Requirements.txt
   ```

2. **Environment Variables (`.env`):**
   Create a `.env` file with these keys:
   ```env
   GROQ_API_KEY="..."
   Huggingface_API="..."
   SERPAPI_API_KEY="..."
   FIREBASE_API_KEY="..."
   FIREBASE_AUTH_DOMAIN="..."
   FIREBASE_PROJECT_ID="..."
   FIREBASE_STORAGE_BUCKET="..."
   FIREBASE_MESSAGING_SENDER_ID="..."
   FIREBASE_APP_ID="..."
   FIREBASE_DATABASE_URL="..."
   ```

3. **Firebase Key:**
   Save your Firebase service account key as `firebase_key.json` in the root folder.

4. **Run Application:**
   ```bash
   streamlit run app.py
   ```
