# ui/styling.py

APP_CSS = """
<style>

/* Global background */
html, body, [data-testid="stAppViewContainer"] {
  background:
    radial-gradient(circle at 0% 0%, rgba(59,130,246,0.35), transparent 55%),
    radial-gradient(circle at 100% 100%, rgba(236,72,153,0.35), transparent 55%),
    #020617;
  color: #e5e7eb;
  margin: 0 !important;
}

/* Remove extra top padding/strip */
[data-testid="stAppViewContainer"] > .main {
  padding-top: 0 !important;
}

/* Main container */
.main .block-container {
  padding-top: 0.6rem;
  padding-bottom: 1.6rem;
  max-width: 1200px;
}

/* Sidebar shell */
[data-testid="stSidebar"] {
  background: transparent;
}

section[data-testid="stSidebar"] > div {
  background: rgba(15,23,42,0.96);
  backdrop-filter: blur(18px);
  border-radius: 20px;
  margin: 0.9rem 0.4rem 0.9rem 0.2rem;
  padding: 1.0rem 0.95rem 1.2rem 0.95rem;
  border: 1px solid rgba(148,163,184,0.5);
  box-shadow:
    0 18px 45px rgba(15,23,42,0.65),
    0 0 0 1px rgba(15,23,42,0.85);
}

section[data-testid="stSidebar"] {
  color: #e5e7eb;
}

/* File uploader */
[data-testid="stFileUploaderDropzone"] {
  background: rgba(15,23,42,0.96) !important;
  border-radius: 16px !important;
  border: 1px dashed rgba(148,163,184,0.85) !important;
  color: #e5e7eb !important;
}

[data-testid="stFileUploaderDropzone"] * {
  color: #e5e7eb !important;
}

/* Main glass card */
.glass-shell {
  background: radial-gradient(circle at 0 0, rgba(56,189,248,0.18), transparent 55%),
              radial-gradient(circle at 100% 100%, rgba(251,113,133,0.18), transparent 55%),
              rgba(15,23,42,0.92);
  backdrop-filter: blur(18px);
  border-radius: 26px;
  padding: 1.4rem 1.6rem 1.6rem 1.6rem;
  border: 1px solid rgba(148,163,184,0.7);
  box-shadow:
    0 26px 70px rgba(15,23,42,0.95),
    0 0 0 1px rgba(15,23,42,0.85);
}

/* Top badge row */
.hero-kicker {
  font-size: 0.78rem;
  letter-spacing: 0.16em;
  color: #9ca3af;
  text-transform: uppercase;
  margin-bottom: 0.25rem;
}

/* Headings */
h1 {
  font-size: 2.1rem;
  letter-spacing: 0.02em;
  color: #f9fafb;
}

h2, h3 {
  color: #e5e7eb;
}

/* Stat cards */
.metric-card {
  padding: 0.7rem 0.9rem;
  border-radius: 16px;
  background: rgba(15,23,42,0.95);
  border: 1px solid rgba(55,65,81,0.9);
  box-shadow: 0 16px 40px rgba(15,23,42,0.85);
}

.metric-label {
  font-size: 0.78rem;
  color: #9ca3af;
}

.metric-value {
  font-size: 1.2rem;
  font-weight: 600;
  color: #f9fafb;
}

/* Quick action pills */
.qa-pill {
  border-radius: 999px;
  padding: 0.45rem 0.8rem;
  border: 1px solid rgba(148,163,184,0.85);
  background: linear-gradient(135deg, rgba(15,23,42,1), rgba(30,64,175,0.85));
  color: #e5e7eb;
  font-size: 0.78rem;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  box-shadow: 0 14px 32px rgba(15,23,42,0.85);
}

/* Tabs list spacing */
[data-baseweb="tab-list"] {
  gap: 0.4rem;
}

/* Tabs text + active state */
[data-baseweb="tab"] {
  color: #9ca3af !important;
  font-size: 0.85rem !important;
}

button[role="tab"][aria-selected="true"] {
  color: #f9fafb !important;
  font-weight: 600 !important;
}

/* Tab underline */
[data-baseweb="tab-highlight"] {
  background-color: #f97316 !important;
}

/* Chat bubbles */
div[data-testid="stChatMessage"][data-testid*="user"] {
  background: linear-gradient(135deg, #4f46e5, #ec4899);
  color: #f9fafb;
  border-radius: 16px;
  border: none;
}

div[data-testid="stChatMessage"][data-testid*="assistant"] {
  background: rgba(15,23,42,0.95);
  color: #e5e7eb;
  border-radius: 16px;
  border: 1px solid rgba(55,65,81,0.9);
}

/* Chat input */
.stChatInputContainer {
  background: transparent;
  padding-top: 0.4rem;
}

div[data-testid="stChatInput"] textarea {
  background: rgba(15,23,42,0.98);
  border-radius: 14px;
  border: 1px solid rgba(55,65,81,0.95);
  padding: 0.75rem 0.9rem;
  color: #e5e7eb;
  box-shadow: 0 16px 40px rgba(15,23,42,0.95);
}

div[data-testid="stChatInput"] textarea:focus {
  outline: none;
  border-color: #4F46E5;
  box-shadow:
    0 0 0 1px rgba(79,70,229,1),
    0 18px 46px rgba(55,65,81,1);
}

/* Sidebar buttons */
section[data-testid="stSidebar"] button {
  color: #e5e7eb !important;
  background-color: rgba(15,23,42,0.98) !important;
  border-radius: 999px !important;
  border: 1px solid rgba(75,85,99,0.95) !important;
  padding: 0.45rem 0.2rem;
  font-weight: 600;
  box-shadow: 0 16px 36px rgba(15,23,42,0.9);
  transition: all 0.12s ease-out;
}

section[data-testid="stSidebar"] button:not(:disabled):hover {
  background-color: rgba(37,99,235,0.95) !important;
  border-color: rgba(129,140,248,1) !important;
  color: #f9fafb !important;
  transform: translateY(-1px);
  box-shadow: 0 20px 48px rgba(30,64,175,1);
}

section[data-testid="stSidebar"] button:disabled {
  background-color: rgba(31,41,55,0.98) !important;
  color: #6b7280 !important;
  border: 1px solid rgba(55,65,81,0.95) !important;
  box-shadow: none !important;
}

/* Source badges */
.source-badge {
    display: inline-block;
    padding: 0.15rem 0.55rem;
    border-radius: 6px;
    background: rgba(15,23,42,0.98);
    color: #e5e7eb;
    font-size: 0.68rem;
    margin-right: 0.25rem;
    margin-top: 0.18rem;
    border: 1px solid rgba(55,65,81,0.95);
}

/* Lists */
ul.custom-list {
  padding-left: 1.1rem;
  color: #d1d5db;
}

ul.custom-list li {
  margin-bottom: 0.22rem;
}

/* Info alerts */
div.stAlert {
  background-color: rgba(30,64,175,0.18);
  color: #e5e7eb;
  border-radius: 12px;
  border: 1px solid rgba(129,140,248,0.9);
}

</style>
"""
