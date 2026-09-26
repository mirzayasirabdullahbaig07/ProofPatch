"""
proofpatch/llm.py — Shared Groq LLM client for the ProofPatch Streamlit app.  # noqa: E501

Provides:
  - api_key_from_session(st)     : resolve the active Groq API key (hardcoded > session)
  - call_groq(messages, ...)     : single-shot chat completion via Groq REST API
  - analyse_run(result, st)      : generate an AI verdict for a verification run result
  - analyse_bug_report(text, st) : produce a ProofPatch-structured breakdown of any bug report

All functions that call the API accept `api_key` explicitly so they are
testable without Streamlit.  Functions that integrate with Streamlit widgets
take `st` as a parameter to keep them side-effect–free by default.

Security:
  - No shell calls.  HTTP only via stdlib urllib.
  - API key never written to disk or logs.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GROQ_MODEL = "llama3-70b-8192"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Set this once for a private/local deployment. Prefer an environment variable
# or Streamlit secret for shared repositories and hosted deployments.
GROQ_API_KEY_CONFIG = ""  # Example: "gsk_your_key_here"

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

_SYSTEM_PROOFPATCH = """You are the ProofPatch AI Assistant — an expert in software debugging,
bug reproduction, test-driven repair, and the ProofPatch workflow.

ProofPatch is an IBM Bob 2.0 Hackathon project. IBM Bob drives a 7-step workflow:
1. Understand — read the bug report and locate the defective line
2. Clarify    — ask one focused question if information is missing; otherwise continue
3. Reproduce  — create a FAILING regression test in tests/repro/ before any repair
4. Preserve   — SHA-256 hash the test file and baseline source before touching anything
5. Repair     — patch only sample/candidate/ with the SMALLEST correct change
6. Verify     — run regression + acceptance tests; report failure honestly
7. Package    — produce a downloadable ZIP: report.json, summary.md, diff, hashes, logs

THE BUG: The pagination cursor stores only created_at. When tasks share a timestamp,
the filter `created_at > last_ts` silently skips records at page boundaries.
With page_size=3 and tasks 2,3,4 at 09:01:00 — page 1 returns [1,2,3], cursor = 09:01:00,
next page filters out task 4 forever. Export returns 7 records instead of 8.

THE FIX: Composite cursor (created_at, id).
Filter: (r["created_at"], r["id"]) > (last_ts, last_id)
Cursor: {"created_at": page[-1]["created_at"], "id": page[-1]["id"]}

THREE VARIANTS:
- baseline  : original buggy code — missing ID 4 with page_size=3 — status: Reproduced
- candidate : Bob's repair — all 8 IDs correct for every page size — status: Verified
- bad_patch : deliberate negative control — uses >= causing duplicates — status: Reproduced (caught by tests)

TEAM: Mohammad Aazam (Lead), Mirza Yasir Abdullah Baig (AI Engineer), Faza E Badar (DevOps)

Answer questions about the bug, fix, workflow, test results, evidence packages, or general
debugging best practices. Format code with markdown fences. Be concise and technical."""

_SYSTEM_RUN_ANALYST = """You are an automated test-run analyst for the ProofPatch debugging workflow.
Your job is to interpret a JSON verification run result and produce a clear, structured verdict
for a developer or judge reviewing the fix.

Write in plain English. Structure your response with these sections (use ## headers):
## Verdict
One sentence stating pass/fail and why.
## What happened
2-3 sentences describing the test counts, which IDs were returned, and what the status means.
## Root cause (if failed)
If any tests failed, explain the root cause in plain language. Skip this section if all passed.
## Evidence integrity
One sentence about the SHA-256 hashes and what they prove.
## Next step
One actionable sentence for the reviewer.

Keep the whole response under 220 words. Use inline code for IDs and file names."""

_SYSTEM_BUG_ANALYST = """You are a bug triage specialist trained in the ProofPatch reproduce-first workflow.
Given a free-text bug report, extract and structure it for a ProofPatch debugging session.

Respond with these sections (use ## headers):

## Summary
One sentence — what breaks and when.

## Observable symptom
What the user sees (wrong output, exception, wrong count, etc.).

## Reproduction conditions
Specific inputs, configuration, and environment details that trigger the bug.

## Expected vs actual behaviour
| | Value |
|---|---|
| Expected | … |
| Actual | … |

## Suspected root cause
Your hypothesis about what code is responsible and why.

## Regression test sketch
A short Python pytest function (just the assertion logic, no imports needed) that would
FAIL on buggy code and PASS on fixed code. Use assert statements only.

## Minimal fix suggestion
The smallest code change you would try first — one or two lines of pseudocode or real code.

## Missing information (if any)
List anything the report lacks that would be needed to reproduce the bug.

Be concise. If the report is too vague to produce any of the above sections, say so explicitly."""

# ---------------------------------------------------------------------------
# API key resolution
# ---------------------------------------------------------------------------


def get_api_key(session_state: Any | None = None) -> str:
    """Return the active Groq API key."""
    configured_key = GROQ_API_KEY_CONFIG.strip()
    if configured_key:
        return configured_key

    environment_key = os.getenv("GROQ_API_KEY", "").strip()
    if environment_key:
        return environment_key

    try:
        import streamlit as st

        secret_key = str(st.secrets.get("GROQ_API_KEY", "")).strip()
        if not secret_key:
            groq_section = st.secrets.get("groq", {})
            if hasattr(groq_section, "get"):
                secret_key = str(groq_section.get("api_key", "")).strip()
        if secret_key:
            return secret_key
    except (FileNotFoundError, KeyError):
        pass

    if session_state is not None and session_state.get("_groq_key"):
        return str(session_state["_groq_key"]).strip()
    return ""


# ---------------------------------------------------------------------------
# Core HTTP call
# ---------------------------------------------------------------------------


def call_groq(
    messages: list[dict],
    api_key: str,
    system_prompt: str = _SYSTEM_PROOFPATCH,
    model: str = GROQ_MODEL,
    temperature: float = 0.55,
    max_tokens: int = 1024,
) -> str:
    """
    Send a chat-completion request to the Groq API.

    Returns the assistant reply text, or an error string prefixed with "ERROR:".
    The caller can check `reply.startswith("ERROR:")` to detect failures.
    """
    if not api_key:
        return "ERROR: No API key set. Enter your Groq key in the sidebar."

    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        GROQ_API_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="ignore")[:300]
        if exc.code == 401:
            return "ERROR: Invalid API key. Click **Change API key** and enter a valid Groq key."
        if exc.code == 429:
            return "ERROR: Rate limit hit. Wait a moment and try again."
        return f"ERROR: Groq API {exc.code} — {raw}"
    except Exception as exc:  # network error, timeout, etc.
        return f"ERROR: Request failed — {exc}"


# ---------------------------------------------------------------------------
# High-level helpers
# ---------------------------------------------------------------------------


def analyse_run(result: dict, api_key: str) -> str:
    """
    Ask the LLM to produce a plain-language verdict for a verification run.

    `result` is the dict returned by runner.run_verification().
    Returns the AI narrative, or an error string.
    """
    # Build a compact summary for the LLM — avoid dumping the full stdout
    junit = result.get("junit", {})
    summary = {
        "variant": result.get("variant"),
        "status": result.get("status"),
        "page_size": result.get("page_size"),
        "expected_ids": result.get("expected_ids", []),
        "actual_ids": result.get("actual_ids", []),
        "missing_ids": result.get("missing_ids", []),
        "duplicate_ids": result.get("duplicate_ids", []),
        "tests_total": junit.get("total", 0),
        "tests_passed": junit.get("passed", 0),
        "tests_failed": junit.get("failed", 0),
        "tests_errors": junit.get("errors", 0),
        "elapsed_seconds": result.get("elapsed_seconds"),
        "exit_code": result.get("exit_code"),
        "failure_messages": [
            f["message"][:200] for f in junit.get("failures", [])[:3]
        ],
    }
    prompt = (
        "Here is the JSON result of a ProofPatch verification run. "
        "Analyse it and produce a structured verdict.\n\n"
        f"```json\n{json.dumps(summary, indent=2)}\n```"
    )
    return call_groq(
        [{"role": "user", "content": prompt}],
        api_key=api_key,
        system_prompt=_SYSTEM_RUN_ANALYST,
        temperature=0.3,
        max_tokens=512,
    )


def analyse_bug_report(report_text: str, api_key: str) -> str:
    """
    Ask the LLM to produce a ProofPatch-structured breakdown of a bug report.

    `report_text` is raw free-text from the user.
    Returns the structured analysis, or an error string.
    """
    prompt = (
        "Analyse the following bug report and produce a ProofPatch-structured breakdown.\n\n"
        f"--- BEGIN REPORT ---\n{report_text.strip()}\n--- END REPORT ---"
    )
    return call_groq(
        [{"role": "user", "content": prompt}],
        api_key=api_key,
        system_prompt=_SYSTEM_BUG_ANALYST,
        temperature=0.4,
        max_tokens=900,
    )
