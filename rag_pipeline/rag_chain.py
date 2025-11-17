from __future__ import annotations

import logging
from typing import List, Dict, Tuple

from services.llm_client import BaseLLMClient
from rag_pipeline.retrieval import VectorStore, RetrievedChunk

logger = logging.getLogger(__name__)


class RAGChain:
    """
    RAG pipeline:
      - reformulate question (lightweight)
      - retrieve relevant chunks
      - generate grounded answer with attributions
    """

    def __init__(self, llm: BaseLLMClient, vector_store: VectorStore):
        self.llm = llm
        self.vs = vector_store

    # ----- helpers -----

    def _rewrite_question(self, question: str, chat_history: List[Dict[str, str]]) -> str:
        # Simple placeholder; in production you might call the LLM here.
        return question.strip()

    def _build_system_prompt(self, rewritten_question: str, retrieved: List[RetrievedChunk]) -> str:
        context_lines = []
        for rc in retrieved:
            meta = rc.metadata
            label = f"{meta.source}"
            if meta.page:
                label += f", page {meta.page}"
            context_lines.append(f"[{meta.id}] ({label})\n{meta.content}")

        context_text = "\n\n".join(context_lines)
        sources_list = ", ".join({rc.metadata.source for rc in retrieved})

        return (
            "You are an AI sales & support assistant for a small business.\n"
            "Answer the user's question using ONLY the information from the provided context.\n"
            "If an answer is not covered in the context, say you are not sure and suggest contacting the business.\n"
            "Always be concise, friendly, and conversion‑oriented.\n\n"
            f"User question (rewritten): {rewritten_question}\n\n"
            f"Context from the business documents (sources: {sources_list}):\n{context_text}\n\n"
            "When you respond:\n"
            "- Cite up to 2–3 sources in natural language, for example: "
            "\"According to Pricing.pdf, page 2, ...\".\n"
            "- If the question is about prices, booking, or packages, gently guide the user towards sharing their contact details "
            "so the business can follow up.\n"
        )

    # ----- public API -----

    def answer(
        self,
        question: str,
        chat_history: List[Dict[str, str]],
    ) -> Tuple[str, List[RetrievedChunk], List[str]]:
        if not self.vs.is_ready():
            return (
                "No knowledge base is indexed yet. Please upload and index business documents first.",
                [],
                [],
            )

        rewritten = self._rewrite_question(question, chat_history)
        retrieved = self.vs.search(rewritten)

        retrieved_ids = [rc.metadata.id for rc in retrieved]

        system_prompt = self._build_system_prompt(rewritten, retrieved)
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": question}]

        try:
            answer = self.llm.generate(messages, max_tokens=512)
        except Exception as e:
            logger.error("Error calling LLM in RAGChain: %s", e, exc_info=True)
            answer = (
                "There was an error contacting the language model. "
                "Here are the most relevant passages from your docs instead:\n\n"
            )
            for rc in retrieved:
                meta = rc.metadata
                answer += f"- {meta.source}"
                if meta.page:
                    answer += f", page {meta.page}"
                answer += f": {meta.content[:250]}...\n"

        return answer, retrieved, retrieved_ids
