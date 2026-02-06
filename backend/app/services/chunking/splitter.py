from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from app.core.config import settings

def intelligent_chunk_documents(documents: List[Document]) -> List[Document]:
    """
    Splits documents based on structure (Markdown headers) first, 
    then falls back to recursive character splitting.
    """
    
    # 1. Define headers to split on (for Markdown/structured text)
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    
    # 2. Recursive splitter for content inside headers
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        keep_separator=True
    )

    final_chunks = []
    
    for doc in documents:
        # If the doc content looks like markdown (or we converted it to markdown)
        # simplistic check; usually you'd convert PDF->Markdown before this
        if "#" in doc.page_content:
            md_chunks = markdown_splitter.split_text(doc.page_content)
            # Transfer metadata (source, file_name) to new chunks
            for chunk in md_chunks:
                chunk.metadata.update(doc.metadata)
            
            # Further split large sections
            final_chunks.extend(text_splitter.split_documents(md_chunks))
        else:
            # Fallback for plain text
            final_chunks.extend(text_splitter.split_documents([doc]))

    return [chunk for chunk in final_chunks if chunk.page_content.strip()]
