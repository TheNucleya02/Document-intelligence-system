from typing import List, Dict, Any
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.config import settings


RAG_SYSTEM_PROMPT = (
    "You are a careful assistant for question-answering over private documents. "
    "Follow these rules strictly:\n"
    "- Use ONLY the retrieved chunks to answer.\n"
    "- If the answer is not in the chunks, say you do not know.\n"
    "- Keep the answer concise.\n"
    "- Always cite document name and chunk index in the answer.\n"
)


class LLMClient:
    def __init__(self) -> None:
        self.model = ChatMistralAI(
            model=settings.LLM_MODEL,
            temperature=0.2,
            max_retries=2,
        )

    def generate_answer(
        self,
        instruction: str,
        retrieved_chunks: List[Dict[str, Any]],
        chat_history: List[Dict[str, str]],
        question: str,
    ) -> str:
        history_lines = []
        for msg in chat_history:
            role = msg.get("role", "user").capitalize()
            history_lines.append(f"{role}: {msg.get('content', '')}")

        chunks_text = []
        for i, chunk in enumerate(retrieved_chunks, start=1):
            chunks_text.append(
                f"[{i}] {chunk.get('document_name')} "
                f"(chunk {chunk.get('chunk_index')}, page {chunk.get('page_number')}):\n"
                f"{chunk.get('text')}"
            )

        prompt = "\n\n".join(
            [
                "Instruction:\n" + instruction,
                "Retrieved Chunks:\n" + ("\n\n".join(chunks_text) if chunks_text else "NONE"),
                "Chat History:\n" + ("\n".join(history_lines) if history_lines else "NONE"),
                "User Question:\n" + question,
            ]
        )

        messages = [
            SystemMessage(content=RAG_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
        response = self.model.invoke(messages)
        return response.content.strip()
