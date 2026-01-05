from langchain_mistralai import ChatMistralAI
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains import create_history_aware_retriever
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.services.vector_store import get_vector_store

# In-memory history (for production, consider Redis)
chat_histories = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in chat_histories:
        chat_histories[session_id] = ChatMessageHistory()
    return chat_histories[session_id]

def get_conversational_chain():
    model = ChatMistralAI(
        model="mistral-large-latest",
        temperature=0.4,
        max_retries=2,
    )
    
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})

    # Contextualize question prompt
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", "Given the chat history and the latest user question, formulate a standalone question that can be understood without the chat history. Do NOT answer the question, just reformulate it if needed."),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    
    history_aware_retriever = create_history_aware_retriever(
        model, retriever, contextualize_q_prompt
    )

    # QA prompt
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Keep the answer concise.\n\n{context}"),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    
    question_answer_chain = create_stuff_documents_chain(model, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    return RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )