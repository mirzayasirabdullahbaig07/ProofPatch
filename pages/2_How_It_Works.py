"""
pages/2_How_It_Works.py — Workflow explanation and architecture deep-dive
"""
import sys
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nav import nav_sidebar

st.set_page_config(
    page_title="How It Works — ProofPatch",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
  code, pre { font-family: 'JetBrains Mono', monospace !important; }
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1.5rem !important; max-width: 1100px !important; }

  .page-hero {
    background: linear-gradient(135deg, #1a1a2e, #0f0f1a);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 16px; padding: 40px 40px 32px; margin-bottom: 36px;
  }
  .page-hero h1 { color: #e2e8f0; font-size: 2rem; font-weight: 800; margin: 0 0 10px 0; }
  .page-hero p  { color: #94a3b8; margin: 0; font-size: 1rem; line-height: 1.7; }

  .step-big {
    display: flex; gap: 24px; align-items: flex-start;
    background: #1a1a2e; border: 1px solid rgba(99,102,241,0.15);
    border-radius: 16px; padding: 28px 28px; margin-bottom: 14px;
  }
  .step-big:hover { border-color: rgba(99,102,241,0.4); }
  .num-badge {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white; min-width: 48px; height: 48px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 1.1rem; flex-shrink: 0;
  }
  .step-content h3 { color: #e2e8f0; font-size: 1.05rem; font-weight: 700; margin: 0 0 6px 0; }
  .step-content p  { color: #94a3b8; font-size: 0.9rem; line-height: 1.7; margin: 0; }
  .step-content code { background: rgba(99,102,241,0.12); color: #a5b4fc; padding: 2px 6px; border-radius: 4px; font-size: 0.85rem; }

  .arch-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 32px; }
  .arch-box { background: #1a1a2e; border: 1px solid rgba(99,102,241,0.15); border-radius: 14px; padding: 24px; }
  .arch-box h4 { color: #818cf8; font-size: 0.9rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; margin: 0 0 12px 0; }
  .arch-box ul { color: #94a3b8; font-size: 0.88rem; line-height: 1.8; margin: 0; padding-left: 18px; }
  .arch-box li code { background: rgba(99,102,241,0.1); color: #a5b4fc; padding: 1px 5px; border-radius: 3px; }

  .code-win { background: #0d1117; border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; overflow: hidden; margin: 16px 0 24px 0; }
  .code-bar { background: #161b22; padding: 10px 16px; display: flex; align-items: center; gap: 6px; border-bottom: 1px solid rgba(99,102,241,0.1); }
  .dot { width: 11px; height: 11px; border-radius: 50%; }
  .dr { background: #ff5f57; } .dy { background: #febc2e; } .dg { background: #28c840; }
  .code-fn { color: #6b7280; font-size: 0.78rem; margin-left: 8px; font-family: 'JetBrains Mono', monospace; }
  .code-bd  { padding: 18px 22px; }

  .callout {
    display: flex; gap: 14px; align-items: flex-start;
    background: rgba(99,102,241,0.06); border-left: 3px solid #6366f1;
    border-radius: 0 10px 10px 0; padding: 16px 20px; margin: 20px 0;
  }
  .callout-icon { font-size: 1.3rem; flex-shrink: 0; }
  .callout p { color: #94a3b8; font-size: 0.9rem; line-height: 1.6; margin: 0; }

  .section-title { font-size: 1.4rem; font-weight: 800; color: #e2e8f0; margin: 36px 0 20px 0; }
  .badge { display: inline-block; background: rgba(99,102,241,0.12); color: #818cf8; padding: 3px 10px; border-radius: 100px; font-size: 11px; font-weight: 700; letter-spacing: 0.07em; text-transform: uppercase; margin-right: 6px; }

  .table-wrap table { width: 100%; border-collapse: collapse; }
  .table-wrap th { background: #1a1a2e; color: #818cf8; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.06em; padding: 10px 14px; text-align: left; border-bottom: 1px solid rgba(99,102,241,0.2); }
  .table-wrap td { color: #94a3b8; font-size: 0.87rem; padding: 10px 14px; border-bottom: 1px solid rgba(99,102,241,0.08); }
  .table-wrap td code { color: #a5b4fc; background: rgba(99,102,241,0.08); padding: 2px 6px; border-radius: 4px; font-size: 0.82rem; }

  .footer { border-top: 1px solid rgba(99,102,241,0.12); padding: 24px 0; text-align: center; color: #475569; font-size: 0.82rem; margin-top: 48px; }
  .footer a { color: #6366f1; text-decoration: none; }
</style>
""", unsafe_allow_html=True)

nav_sidebar("2_How_It_Works.py")

# ─── HERO ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-hero">
  <h1>📖 How ProofPatch Works</h1>
  <p>A 7-step structured workflow that uses IBM Bob to go from a bug report to verified, packaged evidence —
  so reviewers inspect <em>proof</em>, not just claims.</p>
</div>
""", unsafe_allow_html=True)

# ─── 7 STEPS ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">The 7-Step Workflow</div>', unsafe_allow_html=True)

steps = [
    ("Understand", "🔍",
     "Bob reads <code>issues/missing_tasks.md</code>, <code>spec/expected_behavior.md</code>, and the baseline source. "
     "It identifies the exact file and line responsible for the defect before touching any code. "
     "If the report is missing information, Bob asks a focused question and stops."),

    ("Clarify", "💬",
     "When the report lacks an observable expected result or reproduction conditions, Bob asks for exactly the missing information: "
     "What is the input? What result is observed? What result is expected? Under what conditions? "
     "No guessing. No silent assumptions."),

    ("Reproduce", "🧪",
     "Bob creates a failing regression test under <code>tests/repro/</code> asserting <em>externally visible</em> behavior — "
     "expected IDs, no duplicates, correct ordering, and bounded termination. "
     "The test must fail on the baseline. A passing test does not reproduce the bug."),

    ("Preserve", "🔒",
     "Before any repair begins, the test is committed and its SHA-256 hash is recorded. "
     "The baseline source directory is also hashed. "
     "These hashes appear in every evidence package and prove the test was written before the fix."),

    ("Repair", "🔧",
     "Bob patches only <code>sample/candidate/</code> — the smallest clear change that satisfies the behavioral contract. "
     "Public function interfaces (<code>list_tasks</code>, <code>export_all</code>) and the fixture must not change. "
     "Bob explains the diff in plain language before applying it."),

    ("Verify", "✅",
     "The same regression test plus the full acceptance suite run against the candidate. "
     "All must pass. A zero-test count is always an error, never a success. "
     "Failed checks are reported as-is — completion is never claimed for a failing run."),

    ("Package", "📦",
     "A downloadable ZIP is produced containing <code>report.json</code>, <code>summary.md</code>, "
     "pytest stdout, source files, test files, and SHA-256 hashes. "
     "No credentials or machine-specific paths are included. "
     "The summary explicitly states the repair awaits human review."),
]

for i, (title, emoji, desc) in enumerate(steps, 1):
    st.markdown(f"""
    <div class="step-big">
      <div class="num-badge">{i}</div>
      <div class="step-content">
        <h3>{emoji} {title}</h3>
        <p>{desc}</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─── ARCHITECTURE ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Architecture</div>', unsafe_allow_html=True)

st.markdown("""
<div class="arch-grid">
  <div class="arch-box">
    <h4>Sample Service</h4>
    <ul>
      <li><code>sample/baseline/</code> — original defective code</li>
      <li><code>sample/candidate/</code> — Bob's repair target</li>
      <li><code>sample/bad_patch/</code> — negative control</li>
      <li><code>sample/data/tasks.json</code> — deterministic fixture</li>
    </ul>
  </div>
  <div class="arch-box">
    <h4>Tests</h4>
    <ul>
      <li><code>tests/repro/</code> — Bob-created regression test</li>
      <li><code>tests/acceptance/</code> — independent behavioral suite</li>
      <li>Controlled via <code>PROOFPATCH_VARIANT</code> env variable</li>
      <li>JUnit XML output parsed by the runner</li>
    </ul>
  </div>
  <div class="arch-box">
    <h4>Runner</h4>
    <ul>
      <li><code>proofpatch/runner.py</code> — <code>run_verification()</code></li>
      <li>Launches pytest in a subprocess, 15s timeout</li>
      <li>Parses JUnit XML with stdlib <code>xml.etree</code></li>
      <li>Computes SHA-256 hashes of source + test dirs</li>
    </ul>
  </div>
  <div class="arch-box">
    <h4>Web Interface</h4>
    <ul>
      <li><code>app.py</code> — landing page</li>
      <li><code>pages/1_Verifier.py</code> — live runner</li>
      <li><code>pages/2_How_It_Works.py</code> — this page</li>
      <li>No Bob credentials required for the hosted app</li>
    </ul>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── THE BUG ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">The Defect in Detail</div>', unsafe_allow_html=True)

st.markdown("""
<div class="callout">
  <div class="callout-icon">🐛</div>
  <p>The baseline pagination cursor stores only <code>created_at</code>. After page [1, 2, 3] the cursor holds
  <code>09:01:00</code>. The next filter is <code>created_at > 09:01:00</code>, which permanently skips task 4
  (also at <code>09:01:00</code>). No exception is raised. The export silently returns 7 records instead of 8.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="code-win">
  <div class="code-bar">
    <span class="dot dr"></span><span class="dot dy"></span><span class="dot dg"></span>
    <span class="code-fn">sample/baseline/pagination.py  (lines 26-36, defective)</span>
  </div>
  <div class="code-bd">
    <pre style="margin:0;color:#e2e8f0;font-size:0.84rem;line-height:1.75">    if cursor is None:
        filtered = sorted_records
    else:
        last_ts = cursor["created_at"]
<span style="color:#f87171;background:rgba(239,68,68,0.08);display:block;margin:0 -22px;padding:0 22px">        # BUG: ties after a page boundary are silently dropped
        filtered = [r for r in sorted_records if r["created_at"] > last_ts]</span>
    page = filtered[:page_size]
    if not page:
        return page, None
<span style="color:#f87171;background:rgba(239,68,68,0.08);display:block;margin:0 -22px;padding:0 22px">    next_cursor = {"created_at": page[-1]["created_at"]}  # id ignored!</span>
    return page, next_cursor</pre>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="code-win">
  <div class="code-bar">
    <span class="dot dr"></span><span class="dot dy"></span><span class="dot dg"></span>
    <span class="code-fn">sample/candidate/pagination.py  (Bob's repair)</span>
  </div>
  <div class="code-bd">
    <pre style="margin:0;color:#e2e8f0;font-size:0.84rem;line-height:1.75">    if cursor is None:
        filtered = sorted_records
    else:
        last_ts = cursor["created_at"]
        last_id = cursor["id"]
<span style="color:#4ade80;background:rgba(34,197,94,0.08);display:block;margin:0 -22px;padding:0 22px">        # FIX: compare the full (created_at, id) pair — no record is skipped
        filtered = [
            r for r in sorted_records
            if (r["created_at"], r["id"]) > (last_ts, last_id)
        ]</span>
    page = filtered[:page_size]
    if not page:
        return page, None
<span style="color:#4ade80;background:rgba(34,197,94,0.08);display:block;margin:0 -22px;padding:0 22px">    next_cursor = {"created_at": page[-1]["created_at"], "id": page[-1]["id"]}</span>
    return page, next_cursor</pre>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── RESULT CLASSIFICATION ───────────────────────────────────────────────────
st.markdown('<div class="section-title">Result Classification</div>', unsafe_allow_html=True)

st.markdown("""
<div class="table-wrap">
<table>
  <tr><th>Status</th><th>Meaning</th><th>Trigger</th></tr>
  <tr><td>🟢 Verified against this test suite</td><td>Baseline fails, candidate passes all checks, evidence matches snapshots</td><td><code>variant=candidate</code>, all tests pass</td></tr>
  <tr><td>🔴 Reproduced</td><td>The regression assertion fails on the original code — as expected</td><td><code>variant=baseline</code>, test fails</td></tr>
  <tr><td>🟠 Repair rejected</td><td>Candidate or bad_patch fails a required check</td><td>Any test failure on candidate / bad_patch</td></tr>
  <tr><td>⛔ Execution error</td><td>Subprocess timeout, import failure, or no JUnit XML produced</td><td><code>exit_code=-1</code> or zero tests ran</td></tr>
  <tr><td>🔵 Needs information</td><td>Baseline somehow passes all tests (unexpected — warrants investigation)</td><td>Baseline passes when it should fail</td></tr>
</table>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="callout" style="margin-top:20px;">
  <div class="callout-icon">⚠️</div>
  <p>A zero test count is <strong>always</strong> classified as an execution error — never as a pass.
  Skipped required tests are incomplete. The runner defaults to an error or unresolved state when evidence is missing.</p>
</div>
""", unsafe_allow_html=True)

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  <strong>ProofPatch</strong> · IBM Bob 2.0 Hackathon ·
  <a href="/">Home</a> · <a href="/Verifier">Live Verifier</a> · <a href="/About">About</a>
</div>
""", unsafe_allow_html=True)
