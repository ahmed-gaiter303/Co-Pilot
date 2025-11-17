from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List


@dataclass
class QARecord:
    timestamp: str
    question: str
    answer: str
    intent: str
    retrieved_ids: List[str]


class AnalyticsStore:
    """
    Lightweight in-memory store for basic analytics and evaluation hooks.
    """

    def __init__(self) -> None:
        self.records: List[QARecord] = []

    def add_record(
        self,
        question: str,
        answer: str,
        intent: str,
        retrieved_ids: List[str],
    ) -> None:
        self.records.append(
            QARecord(
                timestamp=datetime.utcnow().isoformat(),
                question=question,
                answer=answer,
                intent=intent,
                retrieved_ids=retrieved_ids,
            )
        )

    def get_intent_counts(self) -> Dict[str, int]:
        return Counter(r.intent for r in self.records)

    def evaluate_response(self, record: QARecord) -> Dict[str, float]:
        """
        Placeholder for future evaluation (e.g. RAGAS / custom metrics).
        For now it returns a dummy score.
        """
        # TODO: integrate with RAGAS or custom eval later.
        return {"dummy_score": 1.0}
