from __future__ import annotations

# -------------------------------------------------------------------------
# Path fix so that "app", "rag_pipeline", "services", "ui" can be imported
# when Streamlit runs app/main_app.py directly.
# -------------------------------------------------------------------------
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]  # project root
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# -------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------
import logging
from typing import List, Dict

import streamlit as st

from app.config import load_config
from rag_pipeline.ingestion import IngestionEngine
from rag_pipeline.retrieval import VectorStore
from rag_pipeline.rag_chain import RAGChain
from rag_pipeline.agent import Agent
from services.llm_client import get_llm_client
from services.lead_store import LeadStore
from services.analytics import AnalyticsStore
from ui.styling import APP_CSS

# -------------------------------------------------------------------------
# Logging setup
# -------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------
# Streamlit page config
# -------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Sales & Support Co‑Pilot · Ahmed Gaiter",
    layout="wide",
    page_icon="💼",
)

# Inject global CSS
st.markdown(APP_CSS, unsafe_allow_html=True)

# -------------------------------------------------------------------------
# Load config + initialize core components
# -------------------------------------------------------------------------
cfg = load_config()
llm_client, llm_label = get_llm_client(cfg.llm)

ingestion_engine = IngestionEngine(cfg.paths, cfg.rag)
vector_store = VectorStore(cfg.paths, cfg.rag)
vector_store.load()  # safe even if index not built yet

rag_chain = RAGChain(llm_client, vector_store)
agent = Agent()
lead_store = LeadStore(cfg.paths.leads_csv)
analytics = AnalyticsStore()

# -------------------------------------------------------------------------
# Session state
# -------------------------------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history: List[Dict[str, str]] = []
if "questions_count" not in st.session_state:
    st.session_state.questions_count = 0
if "niche" not in st.session_state:
    st.session_state.niche = cfg.default_niche
if "theme" not in st.session_state:
    st.session_state.theme = cfg.default_theme

# -------------------------------------------------------------------------
# Sidebar · Controls
# -------------------------------------------------------------------------
with st.sidebar:
    st.markdown("#### Niche & theme")
    st.session_state.niche = st.selectbox("Business niche", cfg.niches, index=0)
    st.session_state.theme = st.selectbox("Theme (visual only)", cfg.themes, index=0)

    st.markdown("---")
    st.markdown("#### Upload business docs")
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

    st.caption("Use your pricing, services, and policy documents to power the assistant.")

    st.markdown("---")
    if st.button("⚙️ Index uploaded docs", use_container_width=True):
        if not uploaded_paths:
            st.error("Please upload at least one document to index.")
        else:
            with st.spinner("Indexing documents into the vector store..."):
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
    st.markdown("#### LLM backend")
    st.caption(f"{llm_label}")

# -------------------------------------------------------------------------
# Hero header
# -------------------------------------------------------------------------
st.markdown(
    f"""
<div class="hero-shell">
  <div class="hero-kicker">
    AI SALES & SUPPORT CO‑PILOT · {st.session_state.niche.upper()}
  </div>
  <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:1.5rem;">
    <div>
      <div class="hero-title">
        AI Sales & Support Co‑Pilot for {st.session_state.niche}
      </div>
      <p class="hero-subtitle">
        Convert chats into paying customers while you sleep. Let this assistant answer FAQs,
        handle support, and capture warm leads automatically.
      </p>
    </div>
    <div style="display:flex; flex-direction:column; gap:0.4rem; align-items:flex-end;">
      <div class="hero-badge-primary">
        LIVE PORTFOLIO DEMO
      </div>
      <div class="hero-badge-secondary">
        Designed & engineered by Ahmed Gaiter
      </div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------------------
# KPIs row
# -------------------------------------------------------------------------
lead_rows = lead_store.load_leads()
n_leads = len(lead_rows)
sales_count = sum(1 for r in analytics.records if r.intent == "sales")
support_count = sum(1 for r in analytics.records if r.intent == "support")

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(
        f"""
    <div class="metric-card">
      <div class="metric-label">Files indexed</div>
      <div class="metric-value">{len(vector_store.chunks)}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        f"""
    <div class="metric-card">
      <div class="metric-label">Leads captured</div>
      <div class="metric-value">{n_leads}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        f"""
    <div class="metric-card">
      <div class="metric-label">Sales questions</div>
      <div class="metric-value">{sales_count}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
with k4:
    st.markdown(
        f"""
    <div class="metric-card">
      <div class="metric-label">Support questions</div>
      <div class="metric-value">{support_count}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("")

# -------------------------------------------------------------------------
# Main dashboard row: chat (left) + snapshot (right)
# -------------------------------------------------------------------------
left_col, right_col = st.columns([2.4, 1.6], gap="large")

# ----- Left: chat panel -----
with left_col:
    st.markdown('<div class="dash-panel">', unsafe_allow_html=True)
    st.markdown(
        '<div class="panel-title">Chat co‑pilot</div>'
        '<div class="panel-caption">Ask anything about pricing, packages, policies, or support.</div>',
        unsafe_allow_html=True,
    )

    # previous messages
    for msg in st.session_state.chat_history:
        avatar = "🧑" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    user_message = st.chat_input(
        "Ask a sales or support question about your business..."
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

                # Store lead if completed
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
                    st.success(
                        "Lead captured and stored. Check it in the Leads CRM section below."
                    )

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

    st.markdown("</div>", unsafe_allow_html=True)

# ----- Right: snapshot panel -----
with right_col:
    st.markdown('<div class="dash-panel">', unsafe_allow_html=True)
    st.markdown(
        '<div class="panel-title">Session snapshot</div>'
        '<div class="panel-caption">Live overview of this assistant run.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(f"- **Niche:** {st.session_state.niche}")
    st.markdown(f"- **LLM backend:** {llm_label}")
    st.markdown(f"- **Indexed chunks:** {len(vector_store.chunks)}")
    st.markdown(f"- **Total leads:** {n_leads}")

    st.markdown("---")
    st.markdown("**Top intents in this session**")
    intent_counts = analytics.get_intent_counts()
    if intent_counts:
        for intent_name, count in intent_counts.items():
            st.markdown(f"- **{intent_name}**: {count}")
    else:
        st.caption("No questions yet. Start chatting to see intent analytics.")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("")

# -------------------------------------------------------------------------
# Bottom: Knowledge base & Leads CRM
# -------------------------------------------------------------------------
tab_kb, tab_leads = st.tabs(["📚 Knowledge base", "🧾 Leads CRM"])

with tab_kb:
    st.subheader("Business knowledge base")

    if vector_store.chunks:
        st.markdown("**Indexed documents**")
        docs: Dict[str, int] = {}
        for c in vector_store.chunks:
            docs.setdefault(c.source, 0)
            docs[c.source] += 1
        for name, count in docs.items():
            st.markdown(f"- {name} · {count} chunks")
    else:
        st.info("No documents indexed yet. Upload and index files from the sidebar.")

with tab_leads:
    st.subheader("Leads CRM")

    if lead_rows:
        st.dataframe(lead_rows, hide_index=True, use_container_width=True)
    else:
        st.caption(
            "No leads captured yet. Sales‑intent chats will automatically add leads here."
        )
