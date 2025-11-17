from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class Intent(str, Enum):
    SALES = "sales"
    SUPPORT = "support"
    GENERAL = "general"
    CHITCHAT = "chit-chat"


SALES_KEYWORDS = [
    "price",
    "pricing",
    "cost",
    "membership",
    "package",
    "plan",
    "offer",
    "discount",
    "book",
    "booking",
    "reserve",
    "signup",
    "sign up",
]
SUPPORT_KEYWORDS = [
    "problem",
    "issue",
    "error",
    "cancel",
    "refund",
    "help",
    "support",
]


def classify_intent(message: str) -> Intent:
    text = message.lower()
    if any(k in text for k in SALES_KEYWORDS):
        return Intent.SALES
    if any(k in text for k in SUPPORT_KEYWORDS):
        return Intent.SUPPORT
    if any(w in text for w in ["hi", "hello", "how are you", "thanks"]):
        return Intent.CHITCHAT
    return Intent.GENERAL


@dataclass
class LeadState:
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    interest: str | None = None

    def is_complete(self) -> bool:
        return bool(self.name and self.email and self.phone and self.interest)


class Agent:
    """
    Lightweight agent that:
      - classifies intent
      - tracks lead info across turns
      - decides when to ask follow-up questions
    """

    def __init__(self):
        self.lead_state: LeadState = LeadState()

    def update_from_user_message(self, message: str) -> None:
        """
        Very lightweight extraction: just looks for obvious patterns.
        In production you would call the LLM to parse structured info.
        """
        text = message.strip()

        if "@gmail.com" in text or "@" in text:
            self.lead_state.email = text

        if any(ch.isdigit() for ch in text) and len(text) >= 8 and not self.lead_state.phone:
            self.lead_state.phone = text

        # If the user writes something like "My name is X"
        lowered = text.lower()
        if "my name is" in lowered:
            try:
                name = text.split("is", 1)[1].strip()
                if name:
                    self.lead_state.name = name
            except Exception:
                pass

    def next_lead_question(self) -> str | None:
        if self.lead_state.name is None:
            return "To help our team follow up, may I have your name?"
        if self.lead_state.email is None:
            return "What is the best email address to reach you?"
        if self.lead_state.phone is None:
            return "Do you have a phone or WhatsApp number we can contact?"
        if self.lead_state.interest is None:
            return "Which service or package are you most interested in?"
        return None

    def process_turn(
        self,
        user_message: str,
        rag_answer: str,
    ) -> Tuple[str, Intent, bool, Dict[str, str] | None]:
        """
        Returns:
          final_answer_text,
          intent,
          lead_completed_flag,
          lead_payload (if completed)
        """
        intent = classify_intent(user_message)
        logger.info("Classified intent '%s' for user message: %s", intent, user_message)

        self.update_from_user_message(user_message)

        lead_payload: Dict[str, str] | None = None
        lead_completed = False
        final_answer = rag_answer

        # Only push for leads on sales-focused messages
        if intent == Intent.SALES:
            if not self.lead_state.interest:
                # treat last user message as potential interest if they mention plan/package
                self.lead_state.interest = user_message

            if self.lead_state.is_complete():
                lead_completed = True
                lead_payload = {
                    "name": self.lead_state.name or "",
                    "email": self.lead_state.email or "",
                    "phone": self.lead_state.phone or "",
                    "interest": self.lead_state.interest or "",
                }
                final_answer += (
                    "\n\nIt looks like we have enough details to contact you. "
                    "Our team will follow up shortly with the best offer."
                )
                # Reset state for next lead
                self.lead_state = LeadState()
            else:
                q = self.next_lead_question()
                if q:
                    final_answer += "\n\n" + q

        return final_answer, intent, lead_completed, lead_payload
