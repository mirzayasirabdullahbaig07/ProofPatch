"""
pages/3_Evidence.py — Evidence browser: inspect source code, tests, fixture, diff, and bug analyser
"""
import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from proofpatch.llm import get_api_key, analyse_bug_report
from nav import nav_sidebar

st.set_page_config(
    page_title="Evidence — ProofPatch",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
  code, pre { font-family: 'JetBrains Mono', monospace !important; }
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1.5rem !important; max-width: 1200px !important; }

  .page-hero { background: linear-gradient(135deg, #1a1a2e, #0f0f1a); border: 1px solid rgba(99,102,241,0.2); border-radius: 16px; padding: 36px 40px 28px; margin-bottom: 28px; }
  .page-hero h1 { color: #e2e8f0; font-size: 1.9rem; font-weight: 800; margin: 0 0 8px 0; }
  .page-hero p  { color: #94a3b8; margin: 0; font-size: 0.95rem; line-height: 1.6; }

  .tab-pill-row { display: flex; gap: 8px; margin-bottom: 24px; flex-wrap: wrap; }
  .section-label { font-size: 0.78rem; font-weight: 700; color: #818cf8; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 8px; }

  .file-card { background: #1a1a2e; border: 1px solid rgba(99,102,241,0.15); border-radius: 12px; padding: 20px 22px; margin-bottom: 14px; }
  .file-card h4 { color: #e2e8f0; font-size: 0.95rem; font-weight: 700; margin: 0 0 6px 0; }
  .file-card p  { color: #94a3b8; font-size: 0.86rem; margin: 0; line-height: 1.6; }

  .diff-add { color: #4ade80; background: rgba(34,197,94,0.06); display: block; }
  .diff-del { color: #f87171; background: rgba(239,68,68,0.06); display: block; }
  .diff-hdr { color: #818cf8; display: block; }

  .fixture-chip { display: inline-block; background: #1a1a2e; border: 1px solid rgba(99,102,241,0.2); border-radius: 8px; padding: 10px 14px; margin: 4px; font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; }
  .chip-id   { color: #818cf8; font-weight: 700; }
  .chip-ts   { color: #94a3b8; }
  .chip-note { color: #f87171; font-size: 0.75rem; }

  .footer { border-top: 1px solid rgba(99,102,241,0.12); padding: 24px 0; text-align: center; color: #475569; font-size: 0.82rem; margin-top: 48px; }
  .footer a { color: #6366f1; text-decoration: none; }
</style>
""", unsafe_allow_html=True)

nav_sidebar("3_Evidence.py")

st.markdown("""
<div class="page-hero">
  <h1>🔎 Evidence Browser</h1>
  <p>Inspect every artifact: the fixture data, the defective and repaired source code, the regression test,
  the diff, and the acceptance suite — exactly as stored in the repository.</p>
</div>
""", unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab_fix, tab_src, tab_diff, tab_tests, tab_spec, tab_analyse = st.tabs([
    "📊 Fixture Data",
    "💾 Source Code",
    "📝 Patch Diff",
    "🧪 Tests",
    "📋 Specification",
    "🤖 Bug Report Analyser",
])

# ── TAB 1: FIXTURE ────────────────────────────────────────────────────────────
with tab_fix:
    st.markdown("### Deterministic Test Fixture")
    st.markdown("Eight tasks with deliberate timestamp ties that expose the pagination defect.")

    fixture_path = ROOT / "sample" / "data" / "tasks.json"
    try:
        tasks = json.loads(fixture_path.read_text(encoding="utf-8"))
    except Exception as e:
        tasks = []
        st.error(f"Could not load fixture: {e}")

    NOTES = {
        1: "Ordinary first record",
        2: "Tie group — crosses page boundary",
        3: "Tie group",
        4: "Tie group — skipped by baseline!",
        5: "Ordinary following record",
        6: "Second tie group",
        7: "Second tie group",
        8: "Final partial-page case",
    }

    # Visual table
    cols = st.columns([1, 1, 2, 3])
    cols[0].markdown("**ID**")
    cols[1].markdown("**Timestamp (UTC)**")
    cols[2].markdown("**Title**")
    cols[3].markdown("**Note**")

    for task in tasks:
        tid = task["id"]
        note = NOTES.get(tid, "")
        is_problem = "skipped by baseline" in note
        c0, c1, c2, c3 = st.columns([1, 1, 2, 3])
        c0.markdown(f"`{tid}`")
        c1.markdown(f"`{task['created_at'][11:19]}`")
        c2.markdown(task["title"])
        if is_problem:
            c3.markdown(f"🔴 **{note}**")
        else:
            c3.markdown(note)

    st.markdown("---")
    st.markdown("**Page-size=3 trace through baseline:**")
    st.markdown("""
| Page | Filter | Records returned | Cursor after |
|------|--------|-----------------|-------------|
| 1 | `cursor=None` → all | IDs 1, 2, 3 | `created_at=09:01:00` |
| 2 | `created_at > 09:01:00` | IDs 5, 6, 7 | `created_at=09:03:00` ← **ID 4 skipped!** |
| 3 | `created_at > 09:03:00` | ID 8 | `None` |
| — | — | **Total: 7** | **ID 4 lost forever** |
    """)

    with st.expander("Raw JSON"):
        st.code(fixture_path.read_text(encoding="utf-8"), language="json")

# ── TAB 2: SOURCE CODE ────────────────────────────────────────────────────────
with tab_src:
    variant_choice = st.radio(
        "Select variant",
        ["baseline", "candidate", "bad_patch"],
        format_func=lambda v: {
            "baseline":  "🔴 Baseline (buggy)",
            "candidate": "🟢 Candidate (Bob repair)",
            "bad_patch": "🟠 Bad Patch (negative control)",
        }[v],
        horizontal=True,
    )

    variant_dir = ROOT / "sample" / variant_choice
    py_files = sorted(variant_dir.glob("*.py"))
    for f in py_files:
        if f.name == "__init__.py":
            continue
        with st.expander(f"📄 `{variant_choice}/{f.name}`", expanded=(f.name == "pagination.py")):
            st.code(f.read_text(encoding="utf-8"), language="python")

# ── TAB 3: DIFF ───────────────────────────────────────────────────────────────
with tab_diff:
    st.markdown("### Patch Diff — baseline → candidate")
    st.markdown("IBM Bob made this change to `sample/candidate/pagination.py`.")

    # Build a manual diff of the key changed lines
    st.markdown("""
```diff
--- a/sample/baseline/pagination.py
+++ b/sample/candidate/pagination.py
@@ -22,12 +22,14 @@
     if cursor is None:
         filtered = sorted_records
     else:
-        last_ts = cursor["created_at"]
-        # BUG: uses strictly-greater-than on timestamp only; ties after a
-        # page boundary are silently dropped.
-        filtered = [r for r in sorted_records if r["created_at"] > last_ts]
+        last_ts = cursor["created_at"]
+        last_id = cursor["id"]
+        # FIX: compare the full (created_at, id) pair so no record in a
+        # tie group is skipped.
+        filtered = [
+            r for r in sorted_records
+            if (r["created_at"], r["id"]) > (last_ts, last_id)
+        ]

     page = filtered[:page_size]

     if not page:
         return page, None

-    next_cursor = {"created_at": page[-1]["created_at"]}
+    next_cursor = {"created_at": page[-1]["created_at"], "id": page[-1]["id"]}
     return page, next_cursor
```
""")

    st.markdown("### Why this works")
    st.markdown("""
Python tuple comparison is lexicographic:

```python
(created_at_A, id_A) > (created_at_B, id_B)
```

- If `created_at_A > created_at_B` → True (later timestamp, include)
- If `created_at_A == created_at_B` and `id_A > id_B` → True (same timestamp, use ID to break tie)
- If `created_at_A == created_at_B` and `id_A == id_B` → False (same record, exclude)
- If `created_at_A < created_at_B` → False (earlier timestamp, exclude)

This ensures every record in a tie group that comes after the cursor is included.
    """)

    st.markdown("### What the bad patch does wrong")
    st.markdown("""
```diff
--- a/sample/baseline/pagination.py
+++ b/sample/bad_patch/pagination.py
@@ -26,7 +26,7 @@
         last_ts = cursor["created_at"]
-        filtered = [r for r in sorted_records if r["created_at"] > last_ts]
+        filtered = [r for r in sorted_records if r["created_at"] >= last_ts]
```

Changing `>` to `>=` means the last record of every page (whose timestamp equals the cursor)
is **re-included** on the next page. This causes duplicates and the export can loop indefinitely
without the hard iteration limit.
    """)

# ── TAB 4: TESTS ──────────────────────────────────────────────────────────────
with tab_tests:
    st.markdown("### Regression Test (`tests/repro/`)")
    st.markdown("""
Created by IBM Bob **before** the repair was made.
This test must:
- ❌ **Fail** on `baseline`
- ✅ **Pass** on `candidate`
- ❌ **Fail** on `bad_patch` (due to duplicate check)
    """)
    repro_file = ROOT / "tests" / "repro" / "test_missing_tasks.py"
    if repro_file.exists():
        with st.expander("📄 `tests/repro/test_missing_tasks.py`", expanded=True):
            st.code(repro_file.read_text(encoding="utf-8"), language="python")

    st.markdown("### Acceptance Suite (`tests/acceptance/`)")
    st.markdown("""
Written independently of the regression test.
Covers edge cases: empty input, unique timestamps, tied timestamps at different page boundaries,
final partial pages, and bounded termination.
    """)
    accept_file = ROOT / "tests" / "acceptance" / "test_acceptance.py"
    if accept_file.exists():
        with st.expander("📄 `tests/acceptance/test_acceptance.py`", expanded=False):
            st.code(accept_file.read_text(encoding="utf-8"), language="python")

# ── TAB 5: SPEC ───────────────────────────────────────────────────────────────
with tab_spec:
    st.markdown("### Expected Behavior Specification")
    spec_file = ROOT / "spec" / "expected_behavior.md"
    if spec_file.exists():
        st.markdown(spec_file.read_text(encoding="utf-8"))
    else:
        st.warning("spec/expected_behavior.md not found")

    st.markdown("---")
    st.markdown("### Bug Report")
    issue_file = ROOT / "issues" / "missing_tasks.md"
    if issue_file.exists():
        st.markdown(issue_file.read_text(encoding="utf-8"))
    else:
        st.warning("issues/missing_tasks.md not found")

# ── TAB 6: BUG REPORT ANALYSER ────────────────────────────────────────────────
with tab_analyse:
    st.markdown("### 🤖 Bug Report Analyser")
    st.markdown(
        "Paste any bug report below and Llama 3 will structure it using the "
        "**ProofPatch reproduce-first framework** — extracting the observable symptom, "
        "reproduction conditions, expected vs actual behaviour, a regression test sketch, "
        "and a minimal fix suggestion."
    )

    # ── API key ──────────────────────────────────────────────────────────────
    api_key = get_api_key(st.session_state)
    if not api_key:
        key_input = st.text_input(
            "Groq API key",
            type="password",
            placeholder="gsk_… (free at console.groq.com/keys)",
            key="_groq_key_evidence",
        )
        if key_input.strip():
            st.session_state["_groq_key"] = key_input.strip()
            api_key = key_input.strip()
            st.rerun()
        else:
            st.info(
                "Enter a Groq API key above to use the analyser. "
                "Free keys (no credit card) at [console.groq.com](https://console.groq.com/keys).",
                icon="🔑",
            )

    # ── Pre-loaded example ───────────────────────────────────────────────────
    EXAMPLE_REPORTS = {
        "ProofPatch demo bug": (ROOT / "issues" / "missing_tasks.md").read_text(encoding="utf-8")
        if (ROOT / "issues" / "missing_tasks.md").exists() else "",
        "Blank — type your own": "",
    }

    preset = st.selectbox(
        "Load example report",
        options=list(EXAMPLE_REPORTS.keys()),
        key="analyser_preset",
    )
    default_text = EXAMPLE_REPORTS[preset]

    report_input = st.text_area(
        "Bug report text",
        value=default_text,
        height=220,
        placeholder=(
            "Paste a bug report here — any format, any detail level.\n\n"
            "Example:\n"
            "When I export tasks with page_size=3 I get 7 records instead of 8. "
            "Task ID 4 is always missing."
        ),
        label_visibility="collapsed",
        key="analyser_input",
    )

    analyse_btn = st.button(
        "✨ Analyse Bug Report",
        type="primary",
        use_container_width=False,
        disabled=not api_key,
    )

    if analyse_btn and report_input.strip():
        cache_key = f"_analysis_{hash(report_input.strip())}"
        cached = st.session_state.get(cache_key)
        if cached:
            analysis = cached
        else:
            with st.spinner("Llama 3 is structuring the report…"):
                analysis = analyse_bug_report(report_input.strip(), api_key)
            if not analysis.startswith("ERROR:"):
                st.session_state[cache_key] = analysis

        st.markdown("---")
        st.markdown("#### Structured Analysis")
        if analysis.startswith("ERROR:"):
            st.error(analysis)
        else:
            st.markdown(analysis)

            # Quick actions
            st.markdown("---")
            col_copy, col_chat = st.columns([2, 5])
            with col_copy:
                st.download_button(
                    "⬇ Download analysis (.md)",
                    data=analysis,
                    file_name="bug_analysis.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            with col_chat:
                st.info(
                    "Take this analysis to the **AI Assistant** page to dive deeper, "
                    "ask follow-up questions, or generate a full regression test.",
                    icon="💡",
                )

    elif analyse_btn and not report_input.strip():
        st.warning("Please paste a bug report before clicking Analyse.")

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  <strong>ProofPatch</strong> · IBM Bob 2.0 Hackathon ·
  <a href="/">Home</a> · <a href="/Verifier">Live Verifier</a> · <a href="/About">About</a>
</div>
""", unsafe_allow_html=True)
