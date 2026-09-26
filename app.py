"""
app.py — ProofPatch Landing Page
"""
import sys
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nav import nav_sidebar

st.set_page_config(
    page_title="ProofPatch — Fix bugs. Show proof.",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
  code, pre { font-family: 'JetBrains Mono', monospace !important; }
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 0 !important; max-width: 1100px !important; }

  .hero-section {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a3e 40%, #0d1b2a 100%);
    padding: 64px 40px 48px 40px;
    border-radius: 0 0 28px 28px;
    margin-bottom: 40px;
  }
  .hero-badge { display:inline-block; background:rgba(99,102,241,0.15); border:1px solid rgba(99,102,241,0.4); color:#818cf8; padding:6px 16px; border-radius:100px; font-size:13px; font-weight:600; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:20px; }
  .hero-title { font-size:3.4rem; font-weight:800; line-height:1.1; background:linear-gradient(135deg,#e2e8f0 30%,#818cf8 80%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; margin-bottom:8px; }
  .hero-sub-title { font-size:1.8rem; font-weight:700; color:#818cf8; margin-bottom:20px; }
  .hero-desc { font-size:1.1rem; color:#94a3b8; line-height:1.7; max-width:680px; margin-bottom:8px; }

  .stat-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:40px; }
  .stat-card { background:#1a1a2e; border:1px solid rgba(99,102,241,0.15); border-radius:12px; padding:20px; text-align:center; }
  .stat-num { font-size:2rem; font-weight:800; color:#818cf8; line-height:1; }
  .stat-label { font-size:0.75rem; color:#64748b; margin-top:5px; font-weight:600; text-transform:uppercase; letter-spacing:0.05em; }

  .problem-card { background:linear-gradient(135deg,rgba(239,68,68,0.08),transparent); border:1px solid rgba(239,68,68,0.22); border-radius:14px; padding:24px 28px; margin-bottom:12px; }
  .problem-card h3 { color:#f87171; font-size:1rem; font-weight:700; margin:0 0 8px 0; }
  .problem-card p  { color:#cbd5e1; line-height:1.65; margin:0; font-size:0.93rem; }
  .fix-card { background:linear-gradient(135deg,rgba(34,197,94,0.08),transparent); border:1px solid rgba(34,197,94,0.22); border-radius:14px; padding:24px 28px; margin-bottom:12px; }
  .fix-card h3 { color:#4ade80; font-size:1rem; font-weight:700; margin:0 0 8px 0; }
  .fix-card p  { color:#cbd5e1; line-height:1.65; margin:0; font-size:0.93rem; }

  .feature-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin-bottom:40px; }
  .feature-card { background:#1a1a2e; border:1px solid rgba(99,102,241,0.15); border-radius:14px; padding:24px 20px; }
  .feature-icon { font-size:1.8rem; margin-bottom:12px; }
  .feature-card h3 { color:#e2e8f0; font-size:0.95rem; font-weight:700; margin-bottom:7px; }
  .feature-card p  { color:#94a3b8; font-size:0.87rem; line-height:1.6; margin:0; }

  .step-row { display:flex; gap:18px; align-items:flex-start; background:#1a1a2e; border:1px solid rgba(99,102,241,0.12); border-radius:12px; padding:20px 22px; margin-bottom:10px; }
  .step-num { background:linear-gradient(135deg,#6366f1,#8b5cf6); color:white; min-width:34px; height:34px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:0.88rem; flex-shrink:0; }
  .step-row h4 { color:#e2e8f0; font-size:0.93rem; font-weight:700; margin:0 0 4px 0; }
  .step-row p  { color:#94a3b8; font-size:0.86rem; line-height:1.6; margin:0; }

  .code-win { background:#0d1117; border:1px solid rgba(99,102,241,0.18); border-radius:12px; overflow:hidden; margin-bottom:28px; }
  .code-bar { background:#161b22; padding:9px 14px; display:flex; align-items:center; gap:6px; border-bottom:1px solid rgba(99,102,241,0.1); }
  .dot { width:11px; height:11px; border-radius:50%; display:inline-block; }
  .dr { background:#ff5f57; } .dy { background:#febc2e; } .dg { background:#28c840; }
  .code-fn { color:#6b7280; font-size:0.78rem; margin-left:8px; font-family:'JetBrains Mono',monospace; }
  .code-bd { padding:18px 20px; }

  .section-hdr { margin:36px 0 20px 0; }
  .section-badge { display:inline-block; background:rgba(99,102,241,0.1); color:#818cf8; padding:3px 10px; border-radius:100px; font-size:10px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:8px; }
  .section-title { font-size:1.6rem; font-weight:800; color:#e2e8f0; margin:0 0 6px 0; }
  .section-desc  { color:#94a3b8; font-size:0.95rem; line-height:1.6; margin:0; }

  .cta-box { background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(139,92,246,0.06)); border:1px solid rgba(99,102,241,0.22); border-radius:18px; padding:44px 36px; text-align:center; margin-bottom:28px; }
  .cta-box h2 { font-size:1.7rem; font-weight:800; color:#e2e8f0; margin:0 0 10px 0; }
  .cta-box p  { color:#94a3b8; font-size:0.97rem; margin:0 0 24px 0; }

  .footer { border-top:1px solid rgba(99,102,241,0.1); padding:24px 0; text-align:center; color:#475569; font-size:0.82rem; margin-top:48px; }

  /* Sidebar nav button styles are injected by nav_sidebar() in nav.py */
</style>
""", unsafe_allow_html=True)

nav_sidebar("app.py")

# ─── HERO ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
  <div class="hero-badge">IBM Bob 2.0 Hackathon</div>
  <div class="hero-title">ProofPatch</div>
  <div class="hero-sub-title">Fix bugs. Show proof.</div>
  <p class="hero-desc">
    A structured debugging workflow powered by <strong style="color:#818cf8">IBM Bob</strong> that
    reproduces a bug, preserves a regression test, repairs the code, and packages executable evidence —
    so every fix is verifiable, not just claimed.
  </p>
</div>
""", unsafe_allow_html=True)

col_cta1, col_cta2, col_cta3 = st.columns([2, 2, 5])
with col_cta1:
    if st.button("▶  Run Live Verifier", type="primary", use_container_width=True):
        st.switch_page("pages/1_Verifier.py")
with col_cta2:
    if st.button("📖  How It Works", use_container_width=True):
        st.switch_page("pages/2_How_It_Works.py")

st.markdown("<br>", unsafe_allow_html=True)

# ─── STATS ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="stat-grid">
  <div class="stat-card"><div class="stat-num">8</div><div class="stat-label">Tasks in Fixture</div></div>
  <div class="stat-card"><div class="stat-num">3</div><div class="stat-label">Variants Verified</div></div>
  <div class="stat-card"><div class="stat-num">7</div><div class="stat-label">Workflow Steps</div></div>
  <div class="stat-card"><div class="stat-num">23</div><div class="stat-label">Tests Run</div></div>
</div>
""", unsafe_allow_html=True)

# ─── THE PROBLEM ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr"><div class="section-badge">The Problem</div><div class="section-title">Silent data loss in task exports</div><p class="section-desc">When tasks share the same creation timestamp, a cursor that only tracks <code>created_at</code> silently skips records at page boundaries. No error. No warning.</p></div>', unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a:
    st.markdown("""
    <div class="problem-card">
      <h3>Before the fix — Baseline</h3>
      <p>With <code>page_size=3</code>, tasks 2, 3, 4 share timestamp <code>09:01:00</code>.
      Export returns <strong style="color:#f87171">[1, 2, 3, 5, 6, 7, 8]</strong>.
      Task 4 is permanently lost.</p>
    </div>
    """, unsafe_allow_html=True)
with col_b:
    st.markdown("""
    <div class="fix-card">
      <h3>After the fix — Bob Repair</h3>
      <p>Composite cursor <code>(created_at, id)</code> breaks ties correctly.
      Export returns <strong style="color:#4ade80">[1, 2, 3, 4, 5, 6, 7, 8]</strong> for every page size.</p>
    </div>
    """, unsafe_allow_html=True)

# ─── CODE DIFF ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="code-win">
  <div class="code-bar">
    <span class="dot dr"></span><span class="dot dy"></span><span class="dot dg"></span>
    <span class="code-fn">sample/baseline/pagination.py  -->  sample/candidate/pagination.py</span>
  </div>
  <div class="code-bd">
    <pre style="margin:0;color:#e2e8f0;font-size:0.84rem;line-height:1.75"><span style="color:#f87171">- last_ts = cursor["created_at"]</span>
<span style="color:#f87171">- filtered = [r for r in sorted_records if r["created_at"] > last_ts]</span>
<span style="color:#f87171">- next_cursor = {"created_at": page[-1]["created_at"]}</span>

<span style="color:#4ade80">+ last_ts, last_id = cursor["created_at"], cursor["id"]</span>
<span style="color:#4ade80">+ filtered = [r for r in sorted_records</span>
<span style="color:#4ade80">+             if (r["created_at"], r["id"]) &gt; (last_ts, last_id)]</span>
<span style="color:#4ade80">+ next_cursor = {"created_at": page[-1]["created_at"], "id": page[-1]["id"]}</span></pre>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── FEATURES ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr"><div class="section-badge">What We Built</div><div class="section-title">More than just a fix</div></div>', unsafe_allow_html=True)
st.markdown("""
<div class="feature-grid">
  <div class="feature-card"><div class="feature-icon">🔬</div><h3>Reproduce First</h3><p>IBM Bob creates a regression test before any repair. The test must fail on the original code. No reproduction = no fix.</p></div>
  <div class="feature-card"><div class="feature-icon">🔒</div><h3>Locked Evidence</h3><p>SHA-256 hashes bind every run report to exact source and test snapshots. You know precisely what was tested.</p></div>
  <div class="feature-card"><div class="feature-icon">⚗️</div><h3>Negative Control</h3><p>A deliberately wrong repair (<code>bad_patch</code>) proves the test suite catches bad fixes — not just a green CI light.</p></div>
  <div class="feature-card"><div class="feature-icon">📦</div><h3>Downloadable Package</h3><p>Every run produces a ZIP with report.json, summary.md, logs, source files, and test files for human review.</p></div>
  <div class="feature-card"><div class="feature-icon">🤖</div><h3>IBM Bob Workflow</h3><p>A reusable SKILL.md guides Bob through all 7 steps — from reading the bug report to packaging evidence.</p></div>
  <div class="feature-card"><div class="feature-icon">🌐</div><h3>Live Public Verifier</h3><p>Judges can re-run real tests against all three variants — no credentials, no setup, no prerecorded results.</p></div>
</div>
""", unsafe_allow_html=True)

# ─── WORKFLOW STEPS ──────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr"><div class="section-badge">The Workflow</div><div class="section-title">7-step structured process</div></div>', unsafe_allow_html=True)
steps = [
    ("Understand", "Bob reads the bug report and identifies the defective file and line before touching anything."),
    ("Clarify",    "If information is missing, Bob asks one focused question and stops — no guessing."),
    ("Reproduce",  "Bob creates a failing regression test under <code>tests/repro/</code> asserting externally visible behavior."),
    ("Preserve",   "The test is committed and SHA-256 hashed before any repair. Hashes prove no post-hoc test writing."),
    ("Repair",     "Bob patches only <code>sample/candidate/</code> — the smallest clear change satisfying the spec."),
    ("Verify",     "The same regression + acceptance tests run on the candidate. A zero-test count is always an error."),
    ("Package",    "A downloadable ZIP with report, diff, logs, hashes, and a plain-language summary — ready for review."),
]
for i, (title, desc) in enumerate(steps, 1):
    st.markdown(f'<div class="step-row"><div class="step-num">{i}</div><div><h4>{title}</h4><p>{desc}</p></div></div>', unsafe_allow_html=True)

# ─── CTA ─────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="cta-box"><h2>Ready to see it live?</h2><p>Run the real test suite against all three variants — original, repaired, and deliberately wrong.</p></div>', unsafe_allow_html=True)

col_f1, col_f2, col_f3 = st.columns([2, 2, 5])
with col_f1:
    if st.button("▶  Open Live Verifier", type="primary", use_container_width=True, key="cta_verifier"):
        st.switch_page("pages/1_Verifier.py")
with col_f2:
    if st.button("🔎  Browse Evidence", use_container_width=True, key="cta_evidence"):
        st.switch_page("pages/3_Evidence.py")

st.markdown('<div class="footer"><strong>ProofPatch</strong> · IBM Bob 2.0 Hackathon · Synthetic demonstration fixture · Real pytest execution · No credentials required</div>', unsafe_allow_html=True)
