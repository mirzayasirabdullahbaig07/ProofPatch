"""
proofpatch/runner.py — Shared verification runner.

run_verification(variant, fixture_id, page_size) -> dict

Launches pytest in a subprocess, parses JUnit XML, records hashes, and
returns a structured result dictionary that the Streamlit app displays.

Security:
- Only the three hard-coded variants are accepted.
- No shell=True; no arbitrary paths from the browser.
- Each run uses a fresh temporary directory.
- Subprocess is bounded to SUBPROCESS_TIMEOUT seconds.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import subprocess
import sys
import tempfile
import time
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALLOWED_VARIANTS = ("baseline", "candidate", "bad_patch")
ALLOWED_PAGE_SIZES = (2, 3, 4)
ALLOWED_FIXTURE_IDS = ("main",)
SUBPROCESS_TIMEOUT = 15  # seconds

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "sample" / "data" / "tasks.json"

# ---------------------------------------------------------------------------
# Bootstrap proofpatch.sample namespace (mirrors conftest.py for direct calls)
# ---------------------------------------------------------------------------
# NOTE: conftest.py at the project root performs the same registration for
# pytest.  This function is needed only for in-process calls made by the
# Streamlit app (where pytest does not run and conftest.py is not executed).
# Keep both in sync if the sample/ path structure changes.
# ---------------------------------------------------------------------------

def _ensure_sample_namespace() -> None:
    """Register proofpatch.sample as a namespace pointing at ROOT/sample/ so
    that importlib.import_module('proofpatch.sample.<variant>.pagination')
    works whether or not pytest's conftest.py has already set it up."""
    import types
    import proofpatch  # noqa: F401

    if "proofpatch.sample" not in sys.modules:
        _pkg = types.ModuleType("proofpatch.sample")
        _pkg.__path__ = [str(ROOT / "sample")]  # type: ignore[assignment]
        _pkg.__package__ = "proofpatch.sample"
        _pkg.__spec__ = None  # type: ignore[assignment]
        sys.modules["proofpatch.sample"] = _pkg
        proofpatch.sample = _pkg  # type: ignore[attr-defined]


_ensure_sample_namespace()

# ---------------------------------------------------------------------------
# Status labels
# ---------------------------------------------------------------------------

STATUS_REPRODUCED = "Reproduced"
STATUS_VERIFIED = "Verified against this test suite"
STATUS_REJECTED = "Repair rejected"
STATUS_EXEC_ERROR = "Execution error"
STATUS_NEEDS_INFO = "Needs information"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_error_result(variant: str, error: str, run_id: str | None = None) -> dict:
    """Return a minimal error result dict for early-exit paths."""
    return {
        "run_id": run_id or str(uuid.uuid4()),
        "variant": variant,
        "status": STATUS_EXEC_ERROR,
        "error": error,
    }


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _dir_sha256(directory: Path) -> str:
    """Deterministic hash of all .py files in a directory, sorted by path."""
    h = hashlib.sha256()
    for p in sorted(directory.rglob("*.py")):
        h.update(str(p.relative_to(directory)).encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def _parse_junit(xml_path: Path) -> dict:
    """Parse a JUnit XML report and return summary counts + failures."""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        suite = root if root.tag == "testsuite" else root.find("testsuite")
        if suite is None:
            return {"error": "No testsuite element found", "total": 0, "passed": 0,
                    "failed": 0, "errors": 0, "skipped": 0, "failures": []}
        total = int(suite.get("tests", 0))
        failed = int(suite.get("failures", 0))
        errors = int(suite.get("errors", 0))
        skipped = int(suite.get("skipped", 0))
        passed = total - failed - errors - skipped
        failures = []
        for tc in suite.iter("testcase"):
            for child in tc:
                if child.tag in ("failure", "error"):
                    failures.append({
                        "test": f"{tc.get('classname','')}.{tc.get('name','')}",
                        "type": child.tag,
                        "message": child.get("message", ""),
                        "text": (child.text or "")[:800],
                    })
        return {
            "total": total, "passed": passed, "failed": failed,
            "errors": errors, "skipped": skipped, "failures": failures,
        }
    except Exception as exc:
        return {"error": str(exc), "total": 0, "passed": 0,
                "failed": 0, "errors": 0, "skipped": 0, "failures": []}


def _load_fixture(fixture_id: str) -> list[dict]:
    with open(FIXTURE_PATH, "r", encoding="utf-8") as fh:
        records = json.load(fh)
    for r in records:
        if isinstance(r.get("created_at"), str):
            r["created_at"] = datetime.fromisoformat(r["created_at"])
            if r["created_at"].tzinfo is None:
                r["created_at"] = r["created_at"].replace(tzinfo=timezone.utc)
    return records


def _run_export(variant: str, page_size: int) -> dict:
    """Run the export directly in-process and return ids/missing/duplicates."""
    try:
        pagination = importlib.import_module(f"proofpatch.sample.{variant}.pagination")
        records = _load_fixture("main")
        result = pagination.export_all(records, page_size=page_size)
        actual_ids = [r["id"] for r in result]
        expected_ids = [1, 2, 3, 4, 5, 6, 7, 8]
        missing = [i for i in expected_ids if i not in actual_ids]
        seen: set = set()
        duplicates = []
        for i in actual_ids:
            if i in seen:
                duplicates.append(i)
            seen.add(i)
        return {
            "expected_ids": expected_ids,
            "actual_ids": actual_ids,
            "missing_ids": missing,
            "duplicate_ids": duplicates,
        }
    except Exception as exc:
        return {
            "expected_ids": [1, 2, 3, 4, 5, 6, 7, 8],
            "actual_ids": [],
            "missing_ids": [],
            "duplicate_ids": [],
            "export_error": str(exc),
            # ensure key is always present on the success path too (set to "" there)
        }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_verification(variant: str, fixture_id: str = "main", page_size: int = 3) -> dict:
    """
    Run the full verification suite for the given variant.

    Returns a dict with keys:
        run_id, variant, fixture_id, page_size,
        status, expected_ids, actual_ids, missing_ids, duplicate_ids,
        source_hash, test_hash,
        junit (parsed XML summary), stdout, stderr, exit_code,
        elapsed_seconds, timestamp, error
    """
    if variant not in ALLOWED_VARIANTS:
        return _make_error_result(variant, f"Invalid variant {variant!r}. Allowed: {ALLOWED_VARIANTS}")
    if fixture_id not in ALLOWED_FIXTURE_IDS:
        return _make_error_result(variant, f"Invalid fixture_id {fixture_id!r}.")
    if page_size not in ALLOWED_PAGE_SIZES:
        return _make_error_result(variant, f"page_size must be one of {ALLOWED_PAGE_SIZES}, got {page_size!r}.")

    run_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    source_dir = ROOT / "sample" / variant
    test_repro_dir = ROOT / "tests" / "repro"
    test_accept_dir = ROOT / "tests" / "acceptance"

    source_hash = _dir_sha256(source_dir)
    test_hash = _dir_sha256(test_repro_dir)

    # Run export in-process for the ID comparison table
    export_result = _run_export(variant, page_size)

    # Launch pytest in a subprocess
    with tempfile.TemporaryDirectory() as tmpdir:
        junit_path = Path(tmpdir) / "junit.xml"
        env = {**os.environ, "PROOFPATCH_VARIANT": variant}
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_repro_dir),
            str(test_accept_dir),
            f"--junitxml={junit_path}",
            "-v", "--tb=short",
            f"--rootdir={ROOT}",
        ]
        t0 = time.monotonic()
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT,
                env=env,
                cwd=str(ROOT),
            )
            elapsed = time.monotonic() - t0
            stdout = proc.stdout
            stderr = proc.stderr
            exit_code = proc.returncode
            junit = _parse_junit(junit_path) if junit_path.exists() else {
                "error": "No JUnit XML produced",
                "total": 0, "passed": 0, "failed": 0, "errors": 0, "skipped": 0,
                "failures": [],
            }
        except subprocess.TimeoutExpired:
            elapsed = SUBPROCESS_TIMEOUT
            stdout = ""
            stderr = f"Subprocess timed out after {SUBPROCESS_TIMEOUT}s."
            exit_code = -1
            junit = {
                "error": "Timeout", "total": 0, "passed": 0, "failed": 0,
                "errors": 0, "skipped": 0, "failures": [],
            }
        except Exception as exc:
            elapsed = time.monotonic() - t0
            stdout = ""
            stderr = str(exc)
            exit_code = -1
            junit = {
                "error": str(exc), "total": 0, "passed": 0, "failed": 0,
                "errors": 0, "skipped": 0, "failures": [],
            }

    # Classify result
    if exit_code == -1 or junit.get("error"):
        status = STATUS_EXEC_ERROR
    elif junit["total"] == 0:
        status = STATUS_EXEC_ERROR  # Zero tests ran — never claim success
    elif variant == "baseline":
        # Baseline should fail the regression test
        if junit["failed"] > 0 or junit["errors"] > 0:
            status = STATUS_REPRODUCED
        else:
            status = STATUS_NEEDS_INFO
    elif variant == "candidate":
        if junit["failed"] == 0 and junit["errors"] == 0 and junit["skipped"] == 0:
            status = STATUS_VERIFIED
        else:
            status = STATUS_REJECTED
    else:  # bad_patch — tests are EXPECTED to fail (negative control)
        if junit["failed"] > 0 or junit["errors"] > 0:
            # Tests caught the bad fix — this is the desired outcome for bad_patch
            status = STATUS_REPRODUCED
        else:
            # Bad patch passed all tests — the test suite failed to catch it
            status = STATUS_NEEDS_INFO

    return {
        "run_id": run_id,
        "variant": variant,
        "fixture_id": fixture_id,
        "page_size": page_size,
        "status": status,
        **export_result,
        "export_error": export_result.get("export_error", ""),
        "source_hash": source_hash,
        "test_hash": test_hash,
        "junit": junit,
        "stdout": stdout[:4000],
        "stderr": stderr[:2000],
        "exit_code": exit_code,
        "elapsed_seconds": round(elapsed, 2),
        "timestamp": timestamp,
        "error": junit.get("error", ""),
    }
