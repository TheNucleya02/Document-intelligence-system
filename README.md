
# 📚 QnA PDF App with RAG

An interactive web application built using Streamlit that lets you upload PDF documents and ask questions based on their content using Retrieval-Augmented Generation (RAG).

This app integrates:

🧠 LangChain for chaining components

🤗 HuggingFace Embeddings for semantic search

📦 AstraDB vector store for storing document embeddings

💬 MistralAI LLM for generating answers

# 🚀 Features

1. Upload PDF documents via the sidebar

2. Click "Upload & Process" to extract, chunk, and embed the content

3. Ask natural language questions about your PDF

4. Instant, intelligent answers using RAG pipeline

5. Clean, aesthetic UI with smooth animations

# 🛠️ Setup Instructions

1. Clone the Repository

git clone https://github.com/TheNucleya02/PDF_QnA_app.git \n
cd PDF_QnA_app

2. Install Dependencies

pip install -r requirements.txt

3. Add API Keys

Replace the following in streamlit_app.py (or your main file):

ASTRA_DB_API_ENDPOINT = "<your_astra_endpoint>" \n
ASTRA_DB_APPLICATION_TOKEN = "<your_astra_token>" \n
MISTRAL_API_KEY = "<your_mistral_api_key>"\n

4. Run the App

streamlit run streamlit_app.py

# 🧠 How It Works

## PDF Processing:

Extracts text from uploaded PDF using PyPDFLoader

Splits text into chunks using RecursiveCharacterTextSplitter

Embeds text using HuggingFace model

Stores them in AstraDB Vector Store

## Question Answering:

Retrieves relevant chunks based on question

Feeds them into MistralAI via a LangChain retrieval chain

Displays generated answer

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

