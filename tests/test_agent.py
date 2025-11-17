# tests/test_agent.py
from rag_pipeline.agent import Agent, Intent, classify_intent


def test_classify_intent_sales():
    intent = classify_intent("What is the price of your membership plans?")
    assert intent == Intent.SALES


def test_agent_collects_lead_questions():
    agent = Agent()
    answer, intent, lead_completed, payload = agent.process_turn(
        "I want to know about your packages",
        "We offer several membership tiers.",
    )
    assert intent == Intent.SALES
    assert "name" in answer.lower()
