"""
pages/1_Verifier.py — Live Verification Runner
"""
import io
import json
import sys
import zipfile
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from proofpatch.runner import run_verification, ALLOWED_PAGE_SIZES
from proofpatch.llm import get_api_key, analyse_run
from nav import nav_sidebar

st.set_page_config(page_title="Verifier — ProofPatch", page_icon="▶", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
  code, pre { font-family: 'JetBrains Mono', monospace !important; }
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1.2rem !important; max-width: 1200px !important; }

  .page-header { background:linear-gradient(135deg,#1a1a2e,#0f0f1a); border:1px solid rgba(99,102,241,0.2); border-radius:14px; padding:28px 32px; margin-bottom:24px; }
  .page-header h1 { color:#e2e8f0; font-size:1.7rem; font-weight:800; margin:0 0 6px 0; }
  .page-header p  { color:#94a3b8; margin:0; font-size:0.92rem; line-height:1.6; }

  .status-verified   { background:linear-gradient(135deg,rgba(34,197,94,0.1),rgba(34,197,94,0.04));  border:1px solid rgba(34,197,94,0.3);  border-radius:14px; padding:20px 24px; }
  .status-reproduced { background:linear-gradient(135deg,rgba(239,68,68,0.1),rgba(239,68,68,0.04));  border:1px solid rgba(239,68,68,0.3);  border-radius:14px; padding:20px 24px; }
  .status-rejected   { background:linear-gradient(135deg,rgba(249,115,22,0.1),rgba(249,115,22,0.04));border:1px solid rgba(249,115,22,0.3); border-radius:14px; padding:20px 24px; }
  .status-error      { background:linear-gradient(135deg,rgba(239,68,68,0.07),rgba(0,0,0,0.08));     border:1px solid rgba(239,68,68,0.2);  border-radius:14px; padding:20px 24px; }
  .status-info       { background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(99,102,241,0.04));border:1px solid rgba(99,102,241,0.3); border-radius:14px; padding:20px 24px; }
  .status-title { font-size:1.35rem; font-weight:800; margin:0 0 4px 0; }
  .status-sub   { font-size:0.88rem; color:#94a3b8; margin:0; }

  .id-grid { display:flex; flex-wrap:wrap; gap:7px; margin:10px 0; }
  .id-chip { padding:5px 12px; border-radius:100px; font-size:0.82rem; font-weight:700; font-family:'JetBrains Mono',monospace; }
  .id-ok   { background:rgba(34,197,94,0.14);  color:#4ade80; border:1px solid rgba(34,197,94,0.28); }
  .id-miss { background:rgba(239,68,68,0.14);  color:#f87171; border:1px solid rgba(239,68,68,0.28); }
  .id-dup  { background:rgba(249,115,22,0.14); color:#fb923c; border:1px solid rgba(249,115,22,0.28);}

  .ai-verdict-box { background:linear-gradient(135deg,rgba(99,102,241,0.08),rgba(139,92,246,0.04)); border:1px solid rgba(99,102,241,0.25); border-radius:14px; padding:22px 26px; margin-top:4px; }
  .ai-verdict-label { font-size:0.72rem; font-weight:800; color:#818cf8; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:10px; }

  .footer { border-top:1px solid rgba(99,102,241,0.1); padding:20px 0; text-align:center; color:#475569; font-size:0.8rem; margin-top:40px; }

  /* Sidebar nav button styles are injected by nav_sidebar() in nav.py */
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
nav_sidebar("1_Verifier.py")

VARIANT_META = {
    "baseline":  ("🔴", "Original (buggy)",  "Cursor tracks only created_at — silently skips tied records."),
    "candidate": ("🟢", "Bob Repair",         "Composite (created_at, id) cursor — all 8 records returned."),
    "bad_patch": ("🟠", "Incorrect Repair",   "Negative control: >= timestamp causes duplicate records."),
}

with st.sidebar:
    st.markdown("---")
    variant = st.selectbox(
        "Implementation variant",
        options=list(VARIANT_META.keys()),
        format_func=lambda v: f"{VARIANT_META[v][0]} {VARIANT_META[v][1]}",
        key="variant_select",
    )
    icon_v, label_v, desc_v = VARIANT_META[variant]
    st.caption(desc_v)
    page_size = st.selectbox("Page size", options=list(ALLOWED_PAGE_SIZES), index=1, key="ps_select")
    st.markdown("---")
    run_btn = st.button("▶  Run verification", type="primary", use_container_width=True)

    # ── AI Verdict toggle ──────────────────────────────────────────────────────
    st.markdown("---")
    ai_verdict_enabled = st.toggle(
        "🤖 AI Verdict after run",
        value=True,
        help="Ask Llama 3 to interpret the run result in plain language. Requires a Groq API key.",
    )
    if ai_verdict_enabled:
        groq_key_sidebar = st.text_input(
            "Groq API key",
            type="password",
            placeholder="gsk_… (free at console.groq.com)",
            value=st.session_state.get("_groq_key", ""),
            key="_groq_key_verifier",
            help="Key stays in your session only. Leave blank if set in llm.py.",
        )
        if groq_key_sidebar:
            st.session_state["_groq_key"] = groq_key_sidebar
    st.markdown("---")
    st.markdown("**Runs:**\n- `tests/repro/` regression test\n- `tests/acceptance/` suite\n\n**Does NOT** invoke IBM Bob or use cached results.")

# ─── Clear stale result when selectors change ─────────────────────────────────
sel_key = (variant, page_size)
if st.session_state.get("_vsel") != sel_key:
    st.session_state.pop("_vresult", None)
    st.session_state.pop("_vverdict", None)
    st.session_state["_vsel"] = sel_key

# ─── Run ──────────────────────────────────────────────────────────────────────
if run_btn:
    with st.spinner(f"Running pytest against **{label_v}** (page_size={page_size})..."):
        result = run_verification(variant=variant, fixture_id="main", page_size=page_size)
    st.session_state["_vresult"] = result
    st.session_state.pop("_vverdict", None)  # clear stale AI verdict

# ─── PAGE HEADER ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <h1>▶ Live Verification Runner</h1>
  <p>Select a variant and page size in the sidebar, then click <strong>Run verification</strong>.
  Real pytest suites execute against the included implementations — no prerecorded results.</p>
</div>
""", unsafe_allow_html=True)

result = st.session_state.get("_vresult")

if result is None:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div style="background:#1a1a2e;border:1px solid rgba(239,68,68,0.3);border-radius:14px;padding:24px;text-align:center;"><div style="font-size:2rem;margin-bottom:8px;">🔴</div><div style="font-weight:700;color:#f87171;">Original (Baseline)</div><p style="color:#94a3b8;font-size:0.84rem;margin:8px 0 0;">Contains the known defect. Regression test fails here.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div style="background:#1a1a2e;border:1px solid rgba(34,197,94,0.3);border-radius:14px;padding:24px;text-align:center;"><div style="font-size:2rem;margin-bottom:8px;">🟢</div><div style="font-weight:700;color:#4ade80;">Bob Repair (Candidate)</div><p style="color:#94a3b8;font-size:0.84rem;margin:8px 0 0;">IBM Bob\'s fix. All 8 tasks returned correctly.</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div style="background:#1a1a2e;border:1px solid rgba(249,115,22,0.3);border-radius:14px;padding:24px;text-align:center;"><div style="font-size:2rem;margin-bottom:8px;">🟠</div><div style="font-weight:700;color:#fb923c;">Bad Patch (Negative Control)</div><p style="color:#94a3b8;font-size:0.84rem;margin:8px 0 0;">Deliberately wrong fix. Produces duplicates.</p></div>', unsafe_allow_html=True)
    st.info("Select a variant and page size in the sidebar, then click **Run verification**.")
    st.stop()

# ─── STATUS BANNER ────────────────────────────────────────────────────────────
status = result.get("status", "Unknown")
VARIANT_STATUS_MAP = {
    # (variant, status) → (css_class, display_title, subtitle)
    ("baseline",  "Reproduced"):                        ("status-reproduced", "🔴 Defect Reproduced",                    "Regression assertion fails on baseline — as expected."),
    ("candidate", "Verified against this test suite"):  ("status-verified",   "🟢 Verified against this test suite",     "All regression and acceptance checks pass."),
    ("candidate", "Repair rejected"):                   ("status-rejected",   "🟠 Repair Rejected",                      "Candidate failed one or more required checks."),
    ("bad_patch", "Reproduced"):                        ("status-verified",   "🟢 Negative Control Confirmed",           "Test suite caught the bad fix — as expected. The repair process is sound."),
    ("bad_patch", "Needs information"):                 ("status-info",       "🔵 Bad Patch Passed (Unexpected)",        "Bad patch passed all tests — the suite may not be catching this defect."),
}
GENERIC_STATUS_MAP = {
    "Verified against this test suite": ("status-verified",   "🟢 Verified against this test suite", "All regression and acceptance checks pass."),
    "Reproduced":                        ("status-reproduced", "🔴 Defect Reproduced",                "Regression assertion fails — as expected."),
    "Repair rejected":                   ("status-rejected",   "🟠 Repair Rejected",                  "One or more required checks failed."),
    "Execution error":                   ("status-error",      "⛔ Execution Error",                   "Subprocess timeout, import failure, or no test output."),
    "Needs information":                 ("status-info",       "🔵 Needs Information",                "Report lacks reproducible expected behavior."),
}
css_cls, title_txt, sub_txt = (
    VARIANT_STATUS_MAP.get((result.get("variant"), status))
    or GENERIC_STATUS_MAP.get(status)
    or ("status-info", status, "")
)
st.markdown(f'<div class="{css_cls}"><div class="status-title">{title_txt}</div><p class="status-sub">{sub_txt}</p></div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ─── METRICS ──────────────────────────────────────────────────────────────────
junit = result.get("junit", {})
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total Tests", junit.get("total", 0))
m2.metric("Passed",      junit.get("passed", 0))
m3.metric("Failed",      junit.get("failed", 0))
m4.metric("Errors",      junit.get("errors", 0))
m5.metric("Elapsed",     f"{result.get('elapsed_seconds','?')}s")

st.markdown("---")

# ─── AI VERDICT ───────────────────────────────────────────────────────────────
if ai_verdict_enabled:
    api_key = get_api_key(st.session_state)
    verdict_col, _ = st.columns([3, 1])
    with verdict_col:
        st.markdown("### 🤖 AI Verdict")

        # Use cached verdict if the run hasn't changed
        cached_verdict = st.session_state.get("_vverdict")
        if cached_verdict and cached_verdict.get("run_id") == result.get("run_id"):
            verdict_text = cached_verdict["text"]
            with st.container():
                st.markdown('<div class="ai-verdict-label">Llama 3 · Groq</div>', unsafe_allow_html=True)
                st.markdown(verdict_text)
        else:
            if not api_key:
                st.info(
                    "Enter a Groq API key in the sidebar to enable the AI Verdict. "
                    "Free keys (no credit card) at [console.groq.com](https://console.groq.com/keys).",
                    icon="🔑",
                )
            else:
                gen_btn = st.button(
                    "✨ Generate AI Verdict",
                    key="gen_verdict",
                    type="secondary",
                    use_container_width=False,
                )
                if gen_btn:
                    with st.spinner("Asking Llama 3 to analyse the run..."):
                        verdict_text = analyse_run(result, api_key)
                    if verdict_text.startswith("ERROR:"):
                        st.error(verdict_text)
                    else:
                        st.session_state["_vverdict"] = {
                            "run_id": result.get("run_id"),
                            "text": verdict_text,
                        }
                        st.rerun()

    st.markdown("---")

# ─── ID COMPARISON ────────────────────────────────────────────────────────────
st.markdown("### Task ID Comparison")
col_exp, col_act = st.columns(2)
expected_ids = result.get("expected_ids", [])
actual_ids   = result.get("actual_ids",   [])
missing_ids  = result.get("missing_ids",  [])
dup_ids      = set(result.get("duplicate_ids", []))

with col_exp:
    st.markdown("**Expected IDs**")
    chips = "".join(f'<span class="id-chip id-ok">#{i}</span>' for i in expected_ids)
    st.markdown(f'<div class="id-grid">{chips}</div>', unsafe_allow_html=True)

with col_act:
    st.markdown("**Actual IDs Returned**")
    display_ids = actual_ids[:30]
    chips = ""
    for i in display_ids:
        cls = "id-dup" if i in dup_ids else ("id-miss" if i in missing_ids else "id-ok")
        chips += f'<span class="id-chip {cls}">#{i}</span>'
    if len(actual_ids) > 30:
        chips += f'<span class="id-chip" style="color:#64748b;border:1px solid rgba(100,116,139,0.3);background:transparent;">+{len(actual_ids)-30} more</span>'
    _fallback = '<em style="color:#64748b">none</em>'
    st.markdown(f'<div class="id-grid">{chips if chips else _fallback}</div>', unsafe_allow_html=True)

col_miss, col_dup_col = st.columns(2)
with col_miss:
    st.error(f"Missing IDs: {missing_ids}") if missing_ids else st.success("No missing IDs")
with col_dup_col:
    st.error("Duplicate IDs detected (bad cursor)") if dup_ids else st.success("No duplicate IDs")

st.markdown("---")

# ─── FAILURES ─────────────────────────────────────────────────────────────────
if junit.get("failures"):
    with st.expander("Test Failures & Errors", expanded=True):
        for f in junit["failures"]:
            st.markdown(f"**{f['type'].upper()}** — `{f['test']}`")
            if f.get("message"):
                st.markdown(f"> {f['message'][:300]}")
            if f.get("text"):
                st.code(f["text"][:600], language="text")

with st.expander("Source & Test Hashes"):
    hc1, hc2 = st.columns(2)
    with hc1:
        st.markdown(f"**Source hash** (`sample/{result.get('variant')}/`)")
        st.code(result.get("source_hash", "—"), language="text")
    with hc2:
        st.markdown("**Test hash** (`tests/repro/`)")
        st.code(result.get("test_hash", "—"), language="text")
    st.caption(f"Run ID: `{result.get('run_id','—')}` · {result.get('timestamp','—')}")

with st.expander("Raw pytest stdout"):
    st.code(result.get("stdout", "(empty)"), language="text")

if result.get("stderr"):
    with st.expander("stderr"):
        st.code(result.get("stderr", ""), language="text")

with st.expander("Recorded IBM Bob Session"):
    st.info("IBM Bob performs the repair **locally**. This app re-runs tests only.")
    st.markdown("""
| Step | Action | File |
|------|--------|------|
| Understand | Read bug report, identified cursor-only defect | `issues/missing_tasks.md` |
| Reproduce  | Created failing regression test, confirmed on baseline | `tests/repro/test_missing_tasks.py` |
| Repair     | Changed single-field cursor to composite (created_at, id) | `sample/candidate/pagination.py` |
| Verify     | All regression + acceptance tests pass on candidate | `tests/acceptance/test_acceptance.py` |
    """)

# ─── DOWNLOAD ─────────────────────────────────────────────────────────────────
st.markdown("### Download Evidence Package")

def build_zip(r: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # Include the AI verdict in the package if one was generated
        ai_verdict = st.session_state.get("_vverdict", {})
        report = {k: v for k, v in r.items() if k not in ("stdout", "stderr")}
        if ai_verdict.get("run_id") == r.get("run_id") and ai_verdict.get("text"):
            report["ai_verdict"] = ai_verdict["text"]
        zf.writestr("report.json", json.dumps(report, default=str, indent=2))
        zf.writestr("stdout.txt", r.get("stdout", ""))
        if r.get("stderr"):
            zf.writestr("stderr.txt", r.get("stderr", ""))
        for f in sorted((ROOT / "sample" / r.get("variant", "baseline")).glob("*.py")):
            zf.write(f, f"source/{f.name}")
        for f in sorted((ROOT / "tests" / "repro").glob("*.py")):
            zf.write(f, f"tests/repro/{f.name}")
        verdict_section = ""
        if ai_verdict.get("run_id") == r.get("run_id") and ai_verdict.get("text"):
            verdict_section = f"\n## AI Verdict\n\n{ai_verdict['text']}\n"
        lines = [
            "# ProofPatch Evidence Summary", "",
            f"Run ID:    {r.get('run_id','—')}", f"Variant:   {r.get('variant','—')}",
            f"Page size: {r.get('page_size','—')}", f"Status:    {r.get('status','—')}",
            f"Timestamp: {r.get('timestamp','—')}", "",
            f"Expected IDs:  {r.get('expected_ids',[])}",
            f"Actual IDs:    {r.get('actual_ids',[])[:20]}", f"Missing IDs:   {r.get('missing_ids',[])}",
            f"Source hash: {r.get('source_hash','—')}", f"Test hash:   {r.get('test_hash','—')}", "",
            f"Tests: total={r.get('junit',{}).get('total',0)}  passed={r.get('junit',{}).get('passed',0)}  failed={r.get('junit',{}).get('failed',0)}",
            verdict_section,
            "This repair is verified only against the listed tests and awaits human review.",
        ]
        zf.writestr("summary.md", "\n".join(lines))
    return buf.getvalue()

st.download_button(
    label="⬇  Download evidence package (.zip)",
    data=build_zip(result),
    file_name=f"proofpatch_{result.get('variant','unknown')}_{result.get('run_id','')[:8]}.zip",
    mime="application/zip",
    use_container_width=True,
)
st.caption("Contains: report.json · summary.md · stdout.txt · source .py files · test .py files · AI verdict (if generated)")
st.markdown('<div class="footer">ProofPatch · IBM Bob 2.0 Hackathon · Live verification</div>', unsafe_allow_html=True)
