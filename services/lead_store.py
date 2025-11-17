from __future__ import annotations

import csv
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)


@dataclass
class Lead:
    timestamp: str
    source: str
    name: str
    email: str
    phone: str
    interest: str
    conversation_summary: str


class LeadStore:
    """
    Simple CSV-backed lead store.
    Designed so it can be swapped for Google Sheets / Airtable later.
    """

    def __init__(self, csv_path: Path):
        self.csv_path = csv_path
        self._ensure_file()

    def _ensure_file(self) -> None:
        if not self.csv_path.exists():
            logger.info("Creating leads CSV at %s", self.csv_path)
            self.csv_path.parent.mkdir(parents=True, exist_ok=True)
            with self.csv_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["timestamp", "source", "name", "email", "phone", "interest", "conversation_summary"]
                )

    def append_lead(
        self,
        source: str,
        name: str,
        email: str,
        phone: str,
        interest: str,
        conversation_summary: str,
    ) -> Lead:
        lead = Lead(
            timestamp=datetime.utcnow().isoformat(),
            source=source,
            name=name,
            email=email,
            phone=phone,
            interest=interest,
            conversation_summary=conversation_summary,
        )
        with self.csv_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    lead.timestamp,
                    lead.source,
                    lead.name,
                    lead.email,
                    lead.phone,
                    lead.interest,
                    lead.conversation_summary,
                ]
            )
        logger.info("Lead appended: %s", lead)
        return lead

    def load_leads(self) -> List[Dict[str, str]]:
        if not self.csv_path.exists():
            return []
        with self.csv_path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
