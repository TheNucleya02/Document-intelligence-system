from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever # type: ignore
from app.services.vector_store import get_vector_store

def get_hybrid_retriever(k_vector=4, k_keyword=4):
    """
    Combines Semantic Search (Chroma) and Keyword Search (BM25).
    """
    vector_store = get_vector_store()
    
    # 1. Vector Retriever (Semantic)
    vector_retriever = vector_store.as_retriever(search_kwargs={"k": k_vector})
    
    # 2. BM25 Retriever (Keyword)
    # Note: BM25 needs to build an index from documents in memory. 
    # For large datasets, this must be optimized (e.g., using ElasticSearch).
    # Here we fetch all docs from Chroma to build the BM25 index on the fly (OK for small scale).
    
    all_docs = vector_store.get()["documents"] # Get raw text
    metadatas = vector_store.get()["metadatas"]
    
    # Convert back to Document objects for BM25
    from langchain_core.documents import Document
    docs_for_bm25 = [
        Document(page_content=txt, metadata=md) 
        for txt, md in zip(all_docs, metadatas)
    ]
    
    if not docs_for_bm25:
        # Return only vector retriever if no docs exist yet
        return vector_retriever

    bm25_retriever = BM25Retriever.from_documents(docs_for_bm25)
    bm25_retriever.k = k_keyword

    # 3. Ensemble (Weighted combination)
    # Weights: 0.7 for Semantic, 0.3 for Keyword
    ensemble_retriever = EnsembleRetriever(
        retrievers=[vector_retriever, bm25_retriever],
        weights=[0.7, 0.3]
    )
    
    return ensemble_retriever