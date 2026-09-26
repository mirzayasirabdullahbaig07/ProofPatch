"""
pages/4_About.py — About ProofPatch, real team, contact
"""
import sys
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nav import nav_sidebar

st.set_page_config(
    page_title="About — ProofPatch",
    page_icon="ℹ️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
  code, pre { font-family: 'JetBrains Mono', monospace !important; }
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1.2rem !important; max-width: 1100px !important; }

  .hero { background:linear-gradient(135deg,#0f0f1a 0%,#1a1a3e 50%,#0d1b2a 100%); border:1px solid rgba(99,102,241,0.2); border-radius:20px; padding:56px 48px; margin-bottom:40px; text-align:center; }
  .hero h1 { font-size:2.6rem; font-weight:800; background:linear-gradient(135deg,#e2e8f0,#818cf8); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; margin:0 0 14px 0; }
  .hero p  { color:#94a3b8; font-size:1.05rem; line-height:1.7; max-width:680px; margin:0 auto; }
  .hero-badge { display:inline-block; background:rgba(99,102,241,0.15); border:1px solid rgba(99,102,241,0.35); color:#818cf8; padding:6px 18px; border-radius:100px; font-size:0.82rem; font-weight:700; letter-spacing:0.06em; text-transform:uppercase; margin-bottom:16px; }

  .section-title { font-size:1.5rem; font-weight:800; color:#e2e8f0; margin:40px 0 20px 0; }

  .pain-card { background:linear-gradient(135deg,rgba(239,68,68,0.07),transparent); border:1px solid rgba(239,68,68,0.2); border-radius:14px; padding:24px 28px; margin-bottom:12px; }
  .pain-card h4 { color:#f87171; font-size:0.95rem; font-weight:700; margin:0 0 8px 0; }
  .pain-card p  { color:#cbd5e1; font-size:0.9rem; line-height:1.6; margin:0; }

  .solution-card { background:linear-gradient(135deg,rgba(34,197,94,0.07),transparent); border:1px solid rgba(34,197,94,0.2); border-radius:14px; padding:24px 28px; margin-bottom:12px; }
  .solution-card h4 { color:#4ade80; font-size:0.95rem; font-weight:700; margin:0 0 8px 0; }
  .solution-card p  { color:#cbd5e1; font-size:0.9rem; line-height:1.6; margin:0; }

  .team-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:20px; margin-bottom:36px; }
  .team-card { background:#1a1a2e; border:1px solid rgba(99,102,241,0.15); border-radius:16px; padding:28px 20px; text-align:center; }
  .team-avatar { font-size:3rem; margin-bottom:14px; width:72px; height:72px; border-radius:50%; background:linear-gradient(135deg,#6366f1,#8b5cf6); display:flex; align-items:center; justify-content:center; margin:0 auto 14px auto; }
  .team-name { color:#e2e8f0; font-weight:800; font-size:1rem; margin-bottom:4px; }
  .team-role-badge { display:inline-block; background:rgba(99,102,241,0.12); color:#818cf8; padding:3px 12px; border-radius:100px; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:10px; }
  .team-desc { color:#64748b; font-size:0.84rem; line-height:1.5; }

  .value-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:16px; margin-bottom:32px; }
  .value-card { background:#1a1a2e; border:1px solid rgba(99,102,241,0.12); border-radius:12px; padding:22px; }
  .value-card h4 { color:#818cf8; font-weight:700; font-size:0.88rem; text-transform:uppercase; letter-spacing:0.05em; margin:0 0 8px 0; }
  .value-card p  { color:#94a3b8; font-size:0.87rem; line-height:1.6; margin:0; }

  .contact-card { background:#1a1a2e; border:1px solid rgba(99,102,241,0.15); border-radius:14px; padding:28px; margin-bottom:12px; }
  .contact-card h4 { color:#e2e8f0; font-weight:700; margin:0 0 10px 0; }
  .contact-card p  { color:#94a3b8; font-size:0.9rem; line-height:1.6; margin:0; }

  .disclaimer { background:rgba(99,102,241,0.05); border:1px solid rgba(99,102,241,0.15); border-radius:12px; padding:18px 22px; color:#64748b; font-size:0.83rem; line-height:1.6; margin-top:32px; }

  .footer { border-top:1px solid rgba(99,102,241,0.1); padding:24px 0; text-align:center; color:#475569; font-size:0.82rem; margin-top:48px; }

  /* Sidebar nav button styles are injected by nav_sidebar() in nav.py */
</style>
""", unsafe_allow_html=True)

nav_sidebar("4_About.py")

# ─── HERO ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-badge">IBM Bob 2.0 Hackathon</div>
  <h1>About ProofPatch</h1>
  <p>We built ProofPatch to solve a real developer frustration: bugs get "fixed" but the proof
  is scattered across chat logs, screenshots, and memory. ProofPatch makes every fix auditable
  before it's called done.</p>
</div>
""", unsafe_allow_html=True)

# ─── TEAM ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Our Team</div>', unsafe_allow_html=True)
st.markdown("""
<div class="team-grid">
  <div class="team-card">
    <div class="team-avatar" style="font-size:1.6rem;">MA</div>
    <div class="team-name">Mohammad Aazam</div>
    <div class="team-role-badge">Team Leader · Lead AI Engineer</div>
    <div class="team-desc">Leads the project strategy, AI workflow design, and IBM Bob integration. Responsible for the ProofPatch architecture and debugging workflow.</div>
  </div>
  <div class="team-card">
    <div class="team-avatar" style="font-size:1.4rem;">MY</div>
    <div class="team-name">Mirza Yasir Abdullah Baig</div>
    <div class="team-role-badge">AI Engineer</div>
    <div class="team-desc">Builds the AI-assisted repair pipeline, regression test generation, and verification runner. Works on sample service and evidence packaging.</div>
  </div>
  <div class="team-card">
    <div class="team-avatar" style="font-size:1.4rem;">FB</div>
    <div class="team-name">Faza E Badar</div>
    <div class="team-role-badge">DevOps Engineer</div>
    <div class="team-desc">Handles deployment, CI/CD, Streamlit Community Cloud hosting, media production, and final submission.</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── THE PROBLEM ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">The Problem We Solve</div>', unsafe_allow_html=True)
p1, p2 = st.columns(2)
with p1:
    st.markdown("""
    <div class="pain-card"><h4>Bug fixes without proof</h4>
    <p>A developer says "fixed." A reviewer asks "can you show me?" The answer is a chat log, a vague commit message, or "just trust me."</p></div>
    <div class="pain-card"><h4>Tests written after the fix</h4>
    <p>A test written to match a repair isn't a reproduction — it's a rubber stamp. There's no way to prove the test ever failed.</p></div>
    """, unsafe_allow_html=True)
with p2:
    st.markdown("""
    <div class="pain-card"><h4>Silent regressions</h4>
    <p>Without a locked regression test, the same bug silently returns in a refactor. Nobody notices until data is lost again.</p></div>
    <div class="pain-card"><h4>AI fixes with no audit trail</h4>
    <p>AI tools suggest fixes fast. But a fast fix with no test, no diff review, and no evidence package is just technical debt in disguise.</p></div>
    """, unsafe_allow_html=True)

# ─── OUR SOLUTION ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Our Solution</div>', unsafe_allow_html=True)
s1, s2 = st.columns(2)
with s1:
    st.markdown("""
    <div class="solution-card"><h4>Reproduce before you repair</h4>
    <p>IBM Bob creates a failing regression test first. If the test doesn't fail, the bug isn't reproduced — and the fix doesn't start.</p></div>
    <div class="solution-card"><h4>Hash-locked snapshots</h4>
    <p>SHA-256 hashes of the test file and source directory are recorded before the repair. Every evidence package is tied to the exact code it tested.</p></div>
    """, unsafe_allow_html=True)
with s2:
    st.markdown("""
    <div class="solution-card"><h4>Negative control proves the tests work</h4>
    <p>A deliberately wrong repair (<code>bad_patch</code>) demonstrates the test suite catches bad fixes — not just a green build.</p></div>
    <div class="solution-card"><h4>Downloadable evidence packages</h4>
    <p>Every run produces a ZIP with the report, diff, pytest output, and a plain-language summary. A reviewer can inspect it without running anything.</p></div>
    """, unsafe_allow_html=True)

# ─── BUSINESS VALUE ───────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Business Value</div>', unsafe_allow_html=True)
st.markdown("""
<div class="value-grid">
  <div class="value-card"><h4>Target User</h4><p>A developer or reviewer in a small software team who needs to prove a bug was real, fixed, and tested — without reconstructing the evidence from memory.</p></div>
  <div class="value-card"><h4>Value Hypothesis</h4><p>Less time reconstructing what happened, more consistent review evidence, and a reusable process that transfers across projects and team members.</p></div>
  <div class="value-card"><h4>IBM Bob's Role</h4><p>Bob reads repository context, creates the reproduction test, makes the minimal repair, and explains the diff. The workflow is reusable via a custom SKILL.md.</p></div>
  <div class="value-card"><h4>Differentiation</h4><p>ProofPatch is not ordinary AI debugging. The contribution is the process: reproduce first, preserve the test, verify with the same test, package evidence for human review.</p></div>
</div>
""", unsafe_allow_html=True)

# ─── CONTACT ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Contact & Links</div>', unsafe_allow_html=True)
cc1, cc2 = st.columns(2)
with cc1:
    st.markdown("""
    <div class="contact-card">
      <h4>Hackathon</h4>
      <p>IBM Bob 2.0 Hackathon on lablab.ai<br>
      Team: <strong style="color:#818cf8">ProofPatch</strong><br>
      Build window: 25–27 September 2026</p>
    </div>
    """, unsafe_allow_html=True)
with cc2:
    st.markdown("""
    <div class="contact-card">
      <h4>Repository & AI Assistant</h4>
      <p>Source code, tests, evidence packages, and the IBM Bob SKILL.md are in the public GitHub repository.<br><br>
      Use the <strong style="color:#818cf8">AI Assistant</strong> page to ask questions about the project.</p>
    </div>
    """, unsafe_allow_html=True)

# ─── CTA ──────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("▶  Run Live Verifier", type="primary", use_container_width=True):
        st.switch_page("pages/1_Verifier.py")
with c2:
    if st.button("🤖  AI Assistant", use_container_width=True):
        st.switch_page("pages/5_AI_Assistant.py")
with c3:
    if st.button("🔎  Browse Evidence", use_container_width=True):
        st.switch_page("pages/3_Evidence.py")
with c4:
    if st.button("📖  How It Works", use_container_width=True):
        st.switch_page("pages/2_How_It_Works.py")

# ─── DISCLAIMER ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="disclaimer">
  <strong>Honest disclosure:</strong> The task-export defect is a <em>synthetic demonstration</em> — not a real production incident.
  The fixture is deterministic and fully disclosed in this plan.
  The negative control (<code>bad_patch</code>) is a deliberately constructed wrong repair, not an IBM Bob mistake.
  All timing measurements are from actual tool execution.
  The repair is verified only against the listed test suite and explicitly awaits human review.
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="footer"><strong>ProofPatch</strong> · IBM Bob 2.0 Hackathon · Mohammad Aazam · Mirza Yasir Abdullah Baig · Faza E Badar</div>', unsafe_allow_html=True)
