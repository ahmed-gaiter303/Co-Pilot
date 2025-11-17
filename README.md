# AI Sales & Support Co‑Pilot (Agentic RAG · Streamlit)

An **AI Sales & Support Co‑Pilot** for small businesses (gyms, clinics, online courses, restaurants, etc.).  
It answers customer FAQs from your own documents, handles basic support, and automatically captures hot leads into a CSV file.

## What it does

- Upload PDFs / TXT / MD with pricing, services, and policies.
- The app builds a **local RAG knowledge base** using FAISS + sentence‑transformer embeddings.
- A chat‑style **Sales & Support Co‑Pilot**:
  - Answers questions grounded in your docs.
  - Classifies each message as sales / support / general / chit‑chat.
  - For sales‑oriented messages (pricing, bookings, packages…), it gently collects lead info (name, email, phone, interest).
- Captured leads are appended to `data/leads.csv`, ready to sync to Google Sheets or a CRM.
- A **Knowledge & Leads** page shows:
  - Indexed documents.
  - Captured leads table.
  - Basic stats (intent counts, total leads).

## Tech stack

- Python 3.10+
- Streamlit
- FAISS + sentence‑transformers (RAG)
- Abstract LLM interface (`services/llm_client.py`) – works with OpenAI or a dummy fallback.
- Modular architecture with clear separation of concerns.

## Running locally

1. Clone the repo and create a virtual environment.

python -m v
