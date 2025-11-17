# ui/styling.py

APP_CSS = """
<style>

/* Global layout: light SaaS style */
html, body, [data-testid="stAppViewContainer"] {
  background: #F3F4F6;
  color: #111827;
  margin: 0 !important;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

/* Remove extra top padding */
[data-testid="stAppViewContainer"] > .main {
  padding-top: 0 !important;
}

/* Main container */
.main .block-container {
  padding-top: 0.8rem;
  padding-bottom: 1.6rem;
  max-width: 1180px;
}

/* Sidebar: light card */
[data-testid="stSidebar"] {
  background: #E5E7EB;
}

section[data-testid="stSidebar"] > div {
  background: #F9FAFB;
  border-radius: 18px;
  margin: 0.9rem 0.4rem 0.9rem 0.2rem;
  padding: 1.0rem 0.95rem 1.2rem 0.95rem;
  border: 1px solid #E5E7EB;
  box-shadow: 0 12px 30px rgba(15,23,42,0.06);
}

section[data-testid="stSidebar"] {
  color: #111827;
}

/* File uploader */
[data-testid="stFileUploaderDropzone"] {
  background: #F9FAFB !important;
  border-radius: 12px !important;
  border: 1px dashed #CBD5E1 !important;
  color: #111827 !important;
}

[data-testid="stFileUploaderDropzone"] * {
  color: #111827 !important;
}

/* Main shell */
.glass-shell {
  background: #F9FAFB;
  border-radius: 22px;
  padding: 1.4rem 1.6rem 1.6rem 1.6rem;
  border: 1px solid #E5E7EB;
  box-shadow:
    0 18px 40px rgba(15,23,42,0.04),
    0 0 0 1px rgba(148,163,184,0.20);
}

/* Top badge row */
.hero-kicker {
  font-size: 0.78rem;
  letter-spacing: 0.16em;
  color: #6B7280;
  text-transform: uppercase;
  margin-bottom: 0.25rem;
}

/* Headings */
h1, h2, h3 {
  color: #111827;
}

/* Stat cards */
.metric-card {
  padding: 0.7rem 0.9rem;
  border-radius: 14px;
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  box-shadow: 0 8px 20px rgba(15,23,42,0.04);
}

.metric-label {
  font-size: 0.78rem;
  color: #6B7280;
}

.metric-value {
  font-size: 1.15rem;
  font-weight: 600;
  color: #111827;
}

/* Tabs */
[data-baseweb="tab-list"] {
  gap: 0.25rem;
}

[data-baseweb="tab"] {
  color: #6B7280 !important;
  font-size: 0.85rem !important;
}

button[role="tab"][aria-selected="true"] {
  color: #1D4ED8 !important;
  font-weight: 600 !important;
}

/* Tab underline */
[data-baseweb="tab-highlight"] {
  background-color: #2563EB !important;
}

/* Chat bubbles */
div[data-testid="stChatMessage"][data-testid*="user"] {
  background: #2563EB;
  color: #F9FAFB;
  border-radius: 14px;
  border: none;
}

div[data-testid="stChatMessage"][data-testid*="assistant"] {
  background: #FFFFFF;
  color: #111827;
  border-radius: 14px;
  border: 1px solid #E5E7EB;
}

/* Chat input */
.stChatInputContainer {
  background: transparent;
  padding-top: 0.4rem;
}

div[data-testid="stChatInput"] textarea {
  background: #FFFFFF;
  border-radius: 999px;
  border: 1px solid #D1D5DB;
  padding: 0.75rem 0.9rem;
  color: #111827;
  box-shadow: 0 10px 24px rgba(15,23,42,0.06);
}

div[data-testid="stChatInput"] textarea:focus {
  outline: none;
  border-color: #2563EB;
  box-shadow:
    0 0 0 1px rgba(37,99,235,0.80),
    0 12px 28px rgba(37,99,235,0.20);
}

/* Sidebar buttons */
section[data-testid="stSidebar"] button {
  color: #111827 !important;
  background-color: #FFFFFF !important;
  border-radius: 999px !important;
  border: 1px solid #D1D5DB !important;
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
  color: #1F2937;
  border-radius: 12px;
  border: 1px solid #BFDBFE;
}

</style>
"""
