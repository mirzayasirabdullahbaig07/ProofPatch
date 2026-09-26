"""pages/5_AI_Assistant.py — ProofPatch AI Assistant powered by Groq Llama 3 70B."""
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from proofpatch.llm import (
    GROQ_MODEL,
    get_api_key,
    call_groq,
    _SYSTEM_PROOFPATCH,   # re-use the shared system prompt
)
from nav import nav_sidebar

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Assistant — ProofPatch",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
  code, pre { font-family: 'JetBrains Mono', monospace !important; }
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1.2rem !important; max-width: 860px !important; }

  .page-header { background:linear-gradient(135deg,#1a1a2e,#0f0f1a); border:1px solid rgba(99,102,241,0.2); border-radius:14px; padding:28px 32px; margin-bottom:20px; }
  .page-header h1 { color:#e2e8f0; font-size:1.7rem; font-weight:800; margin:0 0 6px 0; }
  .page-header p  { color:#94a3b8; margin:0; font-size:0.92rem; line-height:1.6; }

  .key-box    { background:linear-gradient(135deg,rgba(249,115,22,0.08),transparent); border:1px solid rgba(249,115,22,0.3); border-radius:12px; padding:18px 22px; margin-bottom:20px; }
  .key-box-ok { background:linear-gradient(135deg,rgba(34,197,94,0.08),transparent);  border:1px solid rgba(34,197,94,0.3);  border-radius:12px; padding:14px 18px; margin-bottom:20px; }
  .key-title    { color:#fb923c; font-weight:700; font-size:0.95rem; margin-bottom:8px; }
  .key-title-ok { color:#4ade80; font-weight:700; font-size:0.9rem; }
  .key-hint { color:#94a3b8; font-size:0.83rem; line-height:1.6; }
  .key-link { color:#818cf8; font-weight:600; }

  .footer { border-top:1px solid rgba(99,102,241,0.1); padding:20px 0; text-align:center; color:#475569; font-size:0.8rem; margin-top:40px; }

  /* Sidebar nav button styles are injected by nav_sidebar() in nav.py */
</style>
""", unsafe_allow_html=True)

nav_sidebar("5_AI_Assistant.py")

# ─── PAGE HEADER ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <h1>🤖 AI Assistant</h1>
  <p>Powered by <strong>Groq · Llama 3 70B</strong> — Ask anything about the bug, the fix,
  the workflow, the evidence, or debugging best practices.</p>
</div>
""", unsafe_allow_html=True)

# ─── API KEY MANAGEMENT ───────────────────────────────────────────────────────
api_key = get_api_key(st.session_state)

if not api_key:
        st.markdown("""
        <div class="key-box">
            <div class="key-title">AI Assistant is not configured</div>
            <div class="key-hint">
                The app owner must configure <code>GROQ_API_KEY</code> as a server environment
                variable or Streamlit secret.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

# ── key is confirmed active ───────────────────────────────────────────────────
st.markdown(f'<div class="key-box-ok"><span class="key-title-ok">✓ Groq API key active · Model: {GROQ_MODEL}</span></div>', unsafe_allow_html=True)

# ─── CHAT STATE ───────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state["messages"] = []


def _send(user_text: str) -> None:
    """Append user message, call the API, append assistant reply, rerun."""
    st.session_state["messages"].append({"role": "user", "content": user_text})
    with st.spinner("Thinking..."):
        reply = call_groq(
            st.session_state["messages"],
            api_key=api_key,
            system_prompt=_SYSTEM_PROOFPATCH,
            temperature=0.65,
            max_tokens=1024,
        )
    st.session_state["messages"].append({"role": "assistant", "content": reply})
    st.rerun()


# ─── QUICK QUESTIONS ──────────────────────────────────────────────────────────
st.markdown("**Quick questions — click any to ask instantly:**")

QUICK = [
    ("🐛 What bug does ProofPatch fix?",           "What bug does ProofPatch fix?"),
    ("🔍 Why does baseline skip task ID 4?",        "Why does the baseline skip task ID 4?"),
    ("🔧 How does the composite cursor fix work?",  "How does the composite cursor fix work?"),
    ("⚗️ What is the bad_patch negative control?",  "What is the bad_patch negative control?"),
    ("📋 Explain the 7-step ProofPatch workflow",   "Explain the 7-step ProofPatch workflow"),
    ("📦 What does the evidence ZIP contain?",      "What does the evidence ZIP contain?"),
    ("🤖 What is IBM Bob's role in the project?",   "What is IBM Bob's role in the project?"),
    ("💻 How do I run the tests locally?",          "How do I run the tests locally?"),
]

cols = st.columns(4)
for i, (label, question) in enumerate(QUICK):
    with cols[i % 4]:
        if st.button(label, key=f"q_{i}", use_container_width=True):
            _send(question)

st.markdown("---")

# ─── CHAT DISPLAY ─────────────────────────────────────────────────────────────
if not st.session_state["messages"]:
    st.markdown(
        "<div style='text-align:center;padding:48px 20px;color:#475569;'>"
        "<div style='font-size:3rem;margin-bottom:12px;'>🤖</div>"
        "<div style='font-size:0.95rem;color:#64748b;'>Click a quick question above or type below to start chatting</div>"
        "</div>",
        unsafe_allow_html=True,
    )
else:
    for msg in st.session_state["messages"]:
        role = msg["role"]
        with st.chat_message(role, avatar="🧑" if role == "user" else "🤖"):
            # st.chat_message renders markdown natively — code blocks, headers, etc.
            content = msg["content"]
            if content.startswith("ERROR:"):
                st.error(content[len("ERROR:"):].strip())
            else:
                st.markdown(content)

# ─── CHAT INPUT ───────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask anything about ProofPatch, the bug, the fix, or the workflow…")
if user_input and user_input.strip():
    _send(user_input.strip())

# ─── CLEAR ────────────────────────────────────────────────────────────────────
if st.session_state["messages"]:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Clear conversation", use_container_width=False):
        st.session_state["messages"] = []
        st.rerun()

st.markdown(f'<div class="footer">ProofPatch AI Assistant · Groq {GROQ_MODEL} · IBM Bob 2.0 Hackathon</div>', unsafe_allow_html=True)
