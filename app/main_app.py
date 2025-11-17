from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Dict

import streamlit as st

from app.config import load_config
from rag_pipeline.ingestion import IngestionEngine
from rag_pipeline.retrieval import VectorStore
from rag_pipeline.rag_chain import RAGChain
from rag_pipeline.agent import Agent, Intent
from services.llm_client import get_llm_client
from services.lead_store import LeadStore
from services.analytics import AnalyticsStore

# ---------- Logging ----------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ---------- Load config & init singletons ----------

cfg = load_config()
llm_client, llm_label = get_llm_client(cfg.llm)

ingestion_engine = IngestionEngine(cfg.paths, cfg.rag)
vector_store = VectorStore(cfg.paths, cfg.rag)
vector_store.load()

rag_chain = RAGChain(llm_client, vector_store)
agent = Agent()
lead_store = LeadStore(cfg.paths.leads_csv)
analytics = AnalyticsStore()


# ---------- Streamlit helpers ----------

from ui.layout import render_footer  # noqa: E402 (import after config)
from ui import __init__ as _ui_init  # noqa: F401 (just to mark package)


st.set_page_config(
    page_title="RAG Talent & Docs Assistant · Ahmed Gaiter",
    layout="wide",
    page_icon="💼",
)

# CSS is injected from APP_CSS defined in this file's top part in your project;
# in this snippet we assume it's already injected in the same way shown earlier.


# ---------- Session state ----------

if "chat_history" not in st.session_state:
    st.session_state.chat_history: List[Dict[str, str]] = []
if "questions_count" not in st.session_state:
    st.session_state.questions_count = 0
if "niche" not in st.session_state:
    st.session_state.niche = cfg.default_niche
if "theme" not in st.session_state:
    st.session_state.theme = cfg.default_theme


# ---------- Sidebar ----------

with st.sidebar:
    st.markdown("#### 🎯 Niche & theme")
    st.session_state.niche = st.selectbox("Business niche", cfg.niches, index=0)
    st.session_state.theme = st.selectbox("Theme", cfg.themes, index=0)

    st.markdown("#### 📂 Upload CV / Docs")
    uploaded_files = st.file_uploader(
        "PDF / TXT / MD",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    uploaded_paths: List[Path] = []
    if uploaded_files:
        for uf in uploaded_files:
            save_path = cfg.paths.uploads_dir / uf.name
            with save_path.open("wb") as f:
                f.write(uf.getbuffer())
            uploaded_paths.append(save_path)

    st.markdown("---")

    if st.button("⚙️ Index uploaded docs", use_container_width=True):
        if not uploaded_paths:
            st.error("Please upload at least one document to index.")
        else:
            with st.spinner("Indexing documents..."):
                n_chunks = ingestion_engine.ingest_files(uploaded_paths)
                if n_chunks > 0:
                    vector_store.load()
                    st.success(f"Indexed {len(uploaded_paths)} file(s) into {n_chunks} chunks.")
                else:
                    st.warning("No chunks were produced. Check that your docs contain text.")

    if st.button("🧹 Clear chat history", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.questions_count = 0
        st.experimental_rerun()

    st.markdown("---")
    st.markdown("#### 🤖 LLM status")
    st.caption(f"Backend: {llm_label}")


# ---------- Header ----------

from app.main_app import APP_CSS  # if CSS is moved here; otherwise import from ui.styling
st.markdown(APP_CSS, unsafe_allow_html=True)

st.markdown(
    f"""
<div class="hero-kicker">
  AI SALES & SUPPORT CO‑PILOT · {st.session_state.niche.upper()}
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("<div class='glass-shell'>", unsafe_allow_html=True)

st.markdown(
    f"""
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
  <div>
    <h2 style="margin:0;">AI Sales & Support Co‑Pilot for {st.session_state.niche}</h2>
    <p style="margin:0.25rem 0 0; font-size:0.93rem; max-width:520px;">
      Convert chats into paying customers while you sleep. Let this assistant answer FAQs, handle support, and capture warm leads automatically.
    </p>
  </div>
  <div style="display:flex; flex-direction:column; gap:0.4rem; align-items:flex-end;">
    <div style="
      padding:0.3rem 0.8rem;
      border-radius:999px;
      background:linear-gradient(135deg,#22c55e,#16a34a);
      color:#ecfdf5;
      font-size:0.75rem;
      box-shadow:0 12px 32px rgba(22,163,74,0.9);
    ">
      LIVE · PORTFOLIO DEMO
    </div>
    <div style="
      padding:0.25rem 0.75rem;
      border-radius:999px;
      border:1px solid rgba(148,163,184,0.85);
      background:rgba(15,23,42,0.96);
      font-size:0.72rem;
      color:#e5e7eb;
    ">
      Designed & engineered by Ahmed Gaiter
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# Stats
from services.lead_store import LeadStore as _LS  # just to reuse class for counts
lead_rows = lead_store.load_leads()
n_leads = len(lead_rows)
sales_count = sum(1 for r in analytics.records if r.intent == "sales")
support_count = sum(1 for r in analytics.records if r.intent == "support")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Files indexed", len(vector_store.chunks))
with c2:
    st.metric("Leads captured", n_leads)
with c3:
    st.metric("Sales / Support questions", f"{sales_count} / {support_count}")


# ---------- Tabs ----------

tab_chat, tab_kb = st.tabs(["💬 Chat Co‑Pilot", "📚 Knowledge & Leads"])

# ---------- Chat tab ----------

with tab_chat:
    left_col, right_col = st.columns([2.2, 1], gap="large")

    with left_col:
        st.subheader("Chat console")

        for msg in st.session_state.chat_history:
            avatar = "🧑" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

        user_message = st.chat_input(
            "Ask a sales or support question about your business (pricing, packages, policies, etc.)..."
        )

        if user_message:
            st.session_state.chat_history.append({"role": "user", "content": user_message})
            st.session_state.questions_count += 1

            with st.chat_message("user", avatar="🧑"):
                st.markdown(user_message)

            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Thinking with your business docs..."):
                    answer, retrieved, retrieved_ids = rag_chain.answer(
                        user_message, st.session_state.chat_history
                    )
                    final_answer, intent, lead_completed, lead_payload = agent.process_turn(
                        user_message, answer
                    )

                    analytics.add_record(
                        question=user_message,
                        answer=final_answer,
                        intent=intent.value,
                        retrieved_ids=retrieved_ids,
                    )

                    # Store lead if ready
                    if lead_completed and lead_payload is not None:
                        summary = f"Lead from chat · niche={st.session_state.niche}"
                        lead_store.append_lead(
                            source="chat",
                            name=lead_payload["name"],
                            email=lead_payload["email"],
                            phone=lead_payload["phone"],
                            interest=lead_payload["interest"],
                            conversation_summary=summary,
                        )
                        st.success("Lead captured and stored. You can review it on the Knowledge & Leads page.")

                    st.markdown(final_answer)

                    # Sources panel
                    if retrieved:
                        with st.expander("Sources used in this answer"):
                            for rc in retrieved:
                                meta = rc.metadata
                                label = f"{meta.source}"
                                if meta.page:
                                    label += f", page {meta.page}"
                                st.markdown(f"- **{label}**  \nScore: {rc.score:.2f}")

    with right_col:
        st.subheader("Session snapshot")
        st.markdown(f"- **Niche:** {st.session_state.niche}")
        st.markdown(f"- **LLM backend:** {llm_label}")
        st.markdown(f"- **Indexed chunks:** {len(vector_store.chunks)}")
        st.markdown(f"- **Total leads so far:** {n_leads}")
        st.markdown("---")
        st.subheader("Top intents this session")
        intent_counts = analytics.get_intent_counts()
        if intent_counts:
            for intent_name, count in intent_counts.items():
                st.markdown(f"- **{intent_name}**: {count}")
        else:
            st.caption("No questions yet. Start chatting to see analytics.")


# ---------- Knowledge & Leads tab ----------

with tab_kb:
    st.subheader("Knowledge base")

    if vector_store.chunks:
        st.markdown("**Indexed documents**")
        docs = {}
        for c in vector_store.chunks:
            docs.setdefault(c.source, 0)
            docs[c.source] += 1
        for name, count in docs.items():
            st.markdown(f"- {name} · {count} chunks")
    else:
        st.info("No documents indexed yet. Upload and index files from the sidebar.")

    st.markdown("---")
    st.subheader("Captured leads")

    if lead_rows:
        st.dataframe(lead_rows, hide_index=True, use_container_width=True)
    else:
        st.caption("No leads captured yet. Sales-intent chats will automatically append leads here.")

    st.markdown("---")
    render_footer()

st.markdown("</div>", unsafe_allow_html=True)
