# 📚 Document Q&A Application  

A powerful **Document Question-Answering System** built with **FastAPI (Backend)** and **Streamlit (Frontend)**.  
Upload your PDFs or DOCX files and interact with them using **Mistral AI** with **AstraDB vector storage**.  

---

## 🚀 Features  

- 📂 **Upload Documents** – Supports **PDF & DOCX** formats  
- 🤖 **AI-Powered Q&A** – Ask questions and get context-aware answers using **Mistral AI**  
- 💾 **Vector Database** – Store and query document embeddings with **AstraDB**  
- 💬 **Conversational Memory** – Keep track of chat history while querying  
- 🎨 **Modern UI** – Clean, simple, and interactive interface with **Streamlit**  
- 🔗 **FastAPI Backend** – Provides REST API endpoints for document operations  
- 🛠 **Extensible** – Easy to add new LLMs or vector stores in the future  

---

## 🛠 Tech Stack  

- **Frontend:** [Streamlit](https://streamlit.io/)  
- **Backend:** [FastAPI](https://fastapi.tiangolo.com/)  
- **Vector DB:** [AstraDB](https://www.datastax.com/astra-db)  
- **Embeddings & LLM:** [Mistral AI](https://mistral.ai/)  
- **Deployment:** Render / Local  

---

## Screenshots
<img width="1428" height="818" alt="Screenshot 2025-08-21 at 12 53 24 AM" src="https://github.com/user-attachments/assets/36895dca-e964-42da-834d-0ed9ef977705" />



## ⚡ Quick Start  

### 1️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Set up environment variables  
Create a `.env` file in the root directory:  
```ini
ASTRA_DB_API_ENDPOINT=your_astra_db_endpoint
ASTRA_DB_APPLICATION_TOKEN=your_astra_db_token
MISTRAL_API_KEY=your_mistral_api_key
```

### 3️⃣ Run the Application  

#### Manually in separate terminals  
```bash
# Terminal 1 - Backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend
streamlit run frontend/app.py --server.port 8501
```

---

## 📡 API Endpoints  

| Method | Endpoint             | Description                       |
|--------|----------------------|-----------------------------------|
| GET    | `/`                  | Root health check                 |
| GET    | `/health`            | Backend status                    |
| POST   | `/upload-documents`  | Upload and process documents      |
| POST   | `/ask-question`      | Ask a question about documents    |
| GET    | `/collections`       | List available document collections |

---

## 📁 Project Structure  

```
.
├── backend/
│   ├── main.py          # FastAPI app
│
├── frontend/
│   └── app.py           # Streamlit UI
│
├── run.py               # Helper to run backend & frontend
├── requirements.txt     # Dependencies
├── .env                 # Environment variables
└── README.md            # Documentation
```

---

## 🔮 Future Enhancements  

- 📊 **Analytics Dashboard** – Track document usage & query patterns  
- 🌍 **Multi-language support** – Query docs in multiple languages  
- 🗂 **Multi-file chat sessions** – Interact with multiple docs at once  
- 🔐 **User Authentication** – Secure access with login/signup  
- ☁️ **Cloud Deployments** – Deploy to AWS, GCP, or Azure seamlessly  

---

## 🤝 Contributing  

Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.  

---

## 📜 License  

MIT License © 2025  

---
