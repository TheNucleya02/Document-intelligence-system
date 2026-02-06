from typing import List, Dict, Any, Optional
from app.models import ChatSession, ChatMessage, Document
from app.services.retrieval.retriever import retrieve_chunks
from app.services.llm import LLMClient


def get_or_create_session(
    db,
    user_id: str,
    session_id: Optional[str],
    document_ids: List[str],
) -> ChatSession:
    if session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id,
        ).first()
        if not session:
            raise ValueError("Chat session not found")
        if sorted(session.document_ids or []) != sorted(document_ids):
            raise ValueError("Chat session document set does not match request")
        return session

    session = ChatSession(
        user_id=user_id,
        document_ids=document_ids,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def fetch_chat_history(db, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()
    )
    ordered = list(reversed(messages))
    return [{"role": m.role, "content": m.content} for m in ordered]


def save_message(
    db,
    session_id: str,
    role: str,
    content: str,
    sources: Optional[List[Dict[str, Any]]] = None,
) -> None:
    msg = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        sources=sources,
    )
    db.add(msg)
    db.commit()


def ensure_owned_documents(db, user_id: str, document_ids: List[str]) -> List[str]:
    if not document_ids:
        return []
    docs = (
        db.query(Document)
        .filter(Document.owner_id == user_id, Document.id.in_(document_ids))
        .all()
    )
    owned_ids = [d.id for d in docs]
    if sorted(owned_ids) != sorted(document_ids):
        raise ValueError("One or more documents are not owned by the user")
    return owned_ids


def answer_question(
    db,
    user_id: str,
    question: str,
    session_id: Optional[str],
    document_ids: Optional[List[str]],
) -> Dict[str, Any]:
    if session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id,
        ).first()
        if not session:
            raise ValueError("Chat session not found")
        if document_ids is None:
            document_ids = session.document_ids or []
        elif sorted(document_ids) != sorted(session.document_ids or []):
            raise ValueError("Chat session document set does not match request")
    else:
        if document_ids is None:
            docs = db.query(Document).filter(Document.owner_id == user_id).all()
            document_ids = [d.id for d in docs]

    if not document_ids:
        raise ValueError("No documents available for this user")

    ensure_owned_documents(db, user_id, document_ids)
    session = get_or_create_session(db, user_id, session_id, document_ids)

    history = fetch_chat_history(db, session.id)
    save_message(db, session.id, "user", question)

    retrieved_chunks = retrieve_chunks(question, document_ids, user_id)

    if not retrieved_chunks:
        answer = "I don't know based on the provided documents."
    else:
        llm = LLMClient()
        answer = llm.generate_answer(
            instruction="Answer using only the retrieved chunks. Cite sources.",
            retrieved_chunks=retrieved_chunks,
            chat_history=history,
            question=question,
        )

        citations = []
        for chunk in retrieved_chunks:
            citations.append(
                f"{chunk.get('document_name')} (chunk {chunk.get('chunk_index')}, page {chunk.get('page_number')})"
            )
        if citations:
            answer = f"{answer}\n\nSources:\n- " + "\n- ".join(citations)

    save_message(db, session.id, "assistant", answer, sources=retrieved_chunks)

    return {
        "answer": answer,
        "sources": retrieved_chunks,
        "session_id": session.id,
    }
