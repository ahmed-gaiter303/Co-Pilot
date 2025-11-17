# ui/styling.py

APP_CSS = """
<style>

/* Root layout: bright SaaS dashboard */
html, body, [data-testid="stAppViewContainer"] {
  background: #F1F5F9;
  color: #0F172A;
  margin: 0 !important;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

/* Remove extra top padding */
[data-testid="stAppViewContainer"] > .main {
  padding-top: 0 !important;
}

/* Main container */
.main .block-container {
  padding-top: 0.75rem;
  padding-bottom: 1.6rem;
  max-width: 1200px;
}

/* Sidebar: vertical control panel */
[data-testid="stSidebar"] {
  background: #E2E8F0;
}

section[data-testid="stSidebar"] > div {
  background: #FFFFFF;
  border-radius: 18px;
  margin: 0.9rem 0.4rem 0.9rem 0.2rem;
  padding: 1.0rem 0.95rem 1.2rem 0.95rem;
  border: 1px solid #E2E8F0;
  box-shadow: 0 12px 30px rgba(15,23,42,0.06);
}

section[data-testid="stSidebar"] {
  color: #0F172A;
}

/* File uploader */
[data-testid="stFileUploaderDropzone"] {
  background: #F8FAFC !important;
  border-radius: 12px !important;
  border: 1px dashed #CBD5E1 !important;
  color: #0F172A !important;
}

[data-testid="stFileUploaderDropzone"] * {
  color: #0F172A !important;
}

/* Top hero bar card */
.hero-shell {
  background: #FFFFFF;
  border-radius: 20px;
  padding: 1.1rem 1.4rem;
  border: 1px solid #E2E8F0;
  box-shadow:
    0 14px 32px rgba(15,23,42,0.06),
    0 0 0 1px rgba(148,163,184,0.14);
}

/* Tag above title */
.hero-kicker {
  font-size: 0.75rem;
  letter-spacing: 0.16em;
  color: #64748B;
  text-transform: uppercase;
  margin-bottom: 0.35rem;
}

/* Hero title / subtitle */
.hero-title {
  font-size: 1.55rem;
  font-weight: 650;
  letter-spacing: 0.01em;
  color: #020617;
}

.hero-subtitle {
  font-size: 0.9rem;
  color: #475569;
  max-width: 520px;
}

/* Pill badges on the right */
.hero-badge-primary {
  padding: 0.25rem 0.7rem;
  border-radius: 999px;
  background: linear-gradient(90deg,#2563EB,#22C55E);
  color: #F9FAFB;
  font-size: 0.75rem;
  box-shadow: 0 12px 26px rgba(37,99,235,0.50);
}

.hero-badge-secondary {
  padding: 0.25rem 0.7rem;
  border-radius: 999px;
  border: 1px solid #CBD5E1;
  background: #F8FAFC;
  color: #0F172A;
  font-size: 0.75rem;
}

/* KPI cards row */
.metric-card {
  padding: 0.65rem 0.9rem;
  border-radius: 14px;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  box-shadow: 0 10px 24px rgba(15,23,42,0.04);
}

.metric-label {
  font-size: 0.78rem;
  color: #64748B;
}

.metric-value {
  font-size: 1.2rem;
  font-weight: 600;
  color: #0F172A;
}

/* Two main panels: chat + right column */
.dash-panel {
  background: #FFFFFF;
  border-radius: 18px;
  border: 1px solid #E2E8F0;
  box-shadow: 0 14px 32px rgba(15,23,42,0.06);
  padding: 0.9rem 1.1rem 1.1rem 1.1rem;
}

/* Panel titles */
.panel-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #0F172A;
  margin-bottom: 0.2rem;
}

.panel-caption {
  font-size: 0.78rem;
  color: #94A3B8;
  margin-bottom: 0.4rem;
}

/* Tabs */
[data-baseweb="tab-list"] {
  gap: 0.25rem;
}

[data-baseweb="tab"] {
  color: #64748B !important;
  font-size: 0.85rem !important;
}

button[role="tab"][aria-selected="true"] {
  color: #2563EB !important;
  font-weight: 600 !important;
}

[data-baseweb="tab-highlight"] {
  background-color: #2563EB !important;
}

/* Chat bubbles */
div[data-testid="stChatMessage"][data-testid*="user"] {
  background: #2563EB;
  color: #F9FAFB;
  border-radius: 12px;
  border: none;
}

div[data-testid="stChatMessage"][data-testid*="assistant"] {
  background: #F8FAFC;
  color: #0F172A;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
}

/* Chat input */
.stChatInputContainer {
  background: transparent;
  padding-top: 0.4rem;
}

div[data-testid="stChatInput"] textarea {
  background: #FFFFFF;
  border-radius: 999px;
  border: 1px solid #CBD5E1;
  padding: 0.75rem 0.9rem;
  color: #0F172A;
  box-shadow: 0 12px 28px rgba(15,23,42,0.06);
}

div[data-testid="stChatInput"] textarea:focus {
  outline: none;
  border-color: #2563EB;
  box-shadow:
    0 0 0 1px rgba(37,99,235,0.90),
    0 14px 32px rgba(37,99,235,0.25);
}

/* Sidebar buttons */
section[data-testid="stSidebar"] button {
  color: #0F172A !important;
  background-color: #FFFFFF !important;
  border-radius: 999px !important;
  border: 1px solid #CBD5E1 !important;
  padding: 0.45rem 0.2rem;
  font-weight: 600;
  box-shadow: 0 10px 24px rgba(15,23,42,0.06);
  transition: all 0.12s ease-out;
}

section[data-testid="stSidebar"] button:not(:disabled):hover {
  background-color: #2563EB !important;
  border-color: #1D4ED8 !important;
  color: #F9FAFB !important;
  transform: translateY(-1px);
  box-shadow: 0 16px 32px rgba(37,99,235,0.28);
}

section[data-testid="stSidebar"] button:disabled {
  background-color: #F3F4F6 !important;
  color: #9CA3AF !important;
  border: 1px solid #E5E7EB !important;
  box-shadow: none !important;
}

/* Source badges */
.source-badge {
    display: inline-block;
    padding: 0.12rem 0.55rem;
    border-radius: 999px;
    background: #EFF6FF;
    color: #1D4ED8;
    font-size: 0.68rem;
    margin-right: 0.25rem;
    margin-top: 0.18rem;
    border: 1px solid #BFDBFE;
}

/* Lists */
ul.custom-list {
  padding-left: 1.1rem;
  color: #4B5563;
}

ul.custom-list li {
  margin-bottom: 0.22rem;
}

/* Info alerts */
div.stAlert {
  background-color: #DBEAFE;
  color: #111827;
  border-radius: 12px;
  border: 1px solid #BFDBFE;
}

</style>
"""
