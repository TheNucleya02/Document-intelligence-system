
# 📚 Document QnA App with RAG (PDF, DOCX, Images)

An interactive Streamlit app to upload and index documents (PDF, DOCX, images via OCR) and ask questions using Retrieval-Augmented Generation (RAG).

This app integrates:

🧠 LangChain for chaining components

🧭 MistralAI Embeddings for semantic search

📦 AstraDB vector store for storing document embeddings

💬 MistralAI LLM for generating answers

# 🚀 Features

1. Upload documents (PDF, DOCX, images) via the sidebar

2. Choose chunking strategy (Recursive or Semantic), then click "Upload & Process" to extract, chunk, and embed the content

3. Ask natural language questions about your documents

4. Instant, intelligent answers using RAG pipeline

5. Clean, aesthetic UI with smooth animations

# 🛠️ Setup

1. Clone the Repository

git clone https://github.com/TheNucleya02/PDF_QnA_app.git \n
cd PDF_QnA_app

2. Install Dependencies

pip install -r requirements.txt

3. Add API Keys

Create a `.env` file with the following:

ASTRA_DB_API_ENDPOINT=<your_astra_endpoint>
ASTRA_DB_APPLICATION_TOKEN=<your_astra_token>
MISTRAL_API_KEY=<your_mistral_api_key>

4. Run the App

streamlit run main.py

# 🧠 How It Works

## Ingestion & Processing

Supports:

- PDF via `PyPDFLoader`
- DOCX via `Docx2txtLoader`
- Images (PNG/JPG/TIFF/BMP) via OCR (`pytesseract`)

Chunking strategies:

- Recursive character splitter (configurable size/overlap)
- Semantic chunking (via `langchain-experimental` SemanticChunker) when available

Embeddings & storage:

- MistralAI `mistral-embed`
- AstraDB Vector Store

OCR prerequisites:

- Install Tesseract on macOS: `brew install tesseract`
- On Linux: `sudo apt-get install tesseract-ocr`

## Question Answering

Retrieves relevant chunks using MMR retriever and generates concise answers with Mistral `mistral-large-latest` using a history-aware RAG chain.

# 📸 Screenshot

<img width="1381" alt="Screenshot 2025-04-06 at 11 48 25 PM" src="https://github.com/user-attachments/assets/9f2fb45e-3eac-4b75-96ae-61f65b464d3c" />


# 📄 License

This project is licensed under the MIT License.

# 🙌 Acknowledgements

LangChain

HuggingFace

MistralAI

Streamlit

AstraDB

## Made with ❤️ by Aman

