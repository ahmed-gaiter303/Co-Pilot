from __future__ import annotations

import streamlit as st


def render_footer():
    st.markdown(
        "<p style='text-align:center; font-size:0.75rem; color:#6b7280;'>"
        "Built as a portfolio demo · AI Sales & Support Co‑Pilot"
        "</p>",
        unsafe_allow_html=True,
    )
