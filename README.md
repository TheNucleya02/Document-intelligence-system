# PDF_QnA_app
📚 QnA PDF App with RAG

An interactive web application built using Streamlit that lets you upload PDF documents and ask questions based on their content using Retrieval-Augmented Generation (RAG).

This app integrates:

🧠 LangChain for chaining components

🤗 HuggingFace Embeddings for semantic search

📦 AstraDB vector store for storing document embeddings

💬 MistralAI LLM for generating answers

🚀 Features

Upload PDF documents via the sidebar

Click "Upload & Process" to extract, chunk, and embed the content

Ask natural language questions about your PDF

Instant, intelligent answers using RAG pipeline

Clean, aesthetic UI with smooth animations

🛠️ Setup Instructions

1. Clone the Repository

git clone https://github.com/TheNucleya02/PDF_QnA_app.git
cd PDF_QnA_app

2. Install Dependencies

pip install -r requirements.txt

3. Add API Keys

Replace the following in streamlit_app.py (or your main file):

ASTRA_DB_API_ENDPOINT = "<your_astra_endpoint>"
ASTRA_DB_APPLICATION_TOKEN = "<your_astra_token>"
MISTRAL_API_KEY = "<your_mistral_api_key>"

4. Run the App

streamlit run streamlit_app.py

🧠 How It Works

PDF Processing:

Extracts text from uploaded PDF using PyPDFLoader

Splits text into chunks using RecursiveCharacterTextSplitter

Embeds text using HuggingFace model

Stores them in AstraDB Vector Store

Question Answering:

Retrieves relevant chunks based on question

Feeds them into MistralAI via a LangChain retrieval chain

Displays generated answer

📸 Screenshot



📄 License

This project is licensed under the MIT License.

🙌 Acknowledgements

LangChain

HuggingFace

MistralAI

Streamlit

AstraDB

Made with ❤️ by Aman

