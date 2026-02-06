from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from app.services.extraction.schemas import DocumentAnalysis
from app.services.vector_store import get_vector_store

def analyze_document_structure():
    """
    Retrieves relevant context (or the whole doc if small) and extracts structured data.
    """
    # Initialize Model with Structured Output capabilities
    llm = ChatMistralAI(model="mistral-large-latest", temperature=0)
    structured_llm = llm.with_structured_output(DocumentAnalysis)

    # Prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert legal analyst. Analyze the provided text and extract specific structured information."),
        ("human", "Analyze the following document content:\n\n{context}")
    ])

    chain = prompt | structured_llm
    
    # For analysis, we might want to look at specific chunks or the "whole" document text
    # (Be careful with context window limits).
    # Here, we fetch the first 50 chunks (approx 50k tokens) as a simple context
    vector_store = get_vector_store()
    results = vector_store.similarity_search("obligations deadlines risks cost payment", k=10)
    
    context_text = "\n\n".join([doc.page_content for doc in results])
    
    result = chain.invoke({"context": context_text})
    return result