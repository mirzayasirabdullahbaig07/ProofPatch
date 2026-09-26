"""
Regression test: reproduces the missing-records defect in the baseline.

This test MUST FAIL on sample/baseline and PASS on sample/candidate.

The selected variant is controlled by the PROOFPATCH_VARIANT environment
variable (values: baseline, candidate, bad_patch).  When run directly it
defaults to 'baseline' so the failure is immediately visible.

Do NOT modify this file after it has been committed and preserved.
"""
import importlib
import os
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Variant selection
# ---------------------------------------------------------------------------

VARIANT = os.environ.get("PROOFPATCH_VARIANT", "baseline")
ALLOWED = {"baseline", "candidate", "bad_patch"}

if VARIANT not in ALLOWED:
    raise ValueError(f"PROOFPATCH_VARIANT must be one of {ALLOWED}, got {VARIANT!r}")

pagination = importlib.import_module(f"proofpatch.sample.{VARIANT}.pagination")
list_tasks = pagination.list_tasks
export_all = pagination.export_all

# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

FIXTURE_PATH = Path(__file__).resolve().parents[2] / "sample" / "data" / "tasks.json"


def load_fixture() -> list[dict]:
    with open(FIXTURE_PATH, "r", encoding="utf-8") as fh:
        records = json.load(fh)
    for r in records:
        if isinstance(r.get("created_at"), str):
            r["created_at"] = datetime.fromisoformat(r["created_at"])
            if r["created_at"].tzinfo is None:
                r["created_at"] = r["created_at"].replace(tzinfo=timezone.utc)
    return records


EXPECTED_IDS = [1, 2, 3, 4, 5, 6, 7, 8]

# ---------------------------------------------------------------------------
# Regression test — this is the preservable reproduction assertion
# ---------------------------------------------------------------------------


class TestMissingTasksRegression:
    """
    Primary regression test for the missing-records defect.

    Baseline MUST fail this test.
    Candidate MUST pass this test.
    """

    def test_page_size_3_returns_all_ids(self):
        """
        With page_size=3 the baseline skips ID 4 (tied at 09:01:00).
        This is the exact scenario described in issues/missing_tasks.md.
        """
        records = load_fixture()
        result = export_all(records, page_size=3)
        actual_ids = [r["id"] for r in result]

        # Assert all expected IDs are present — this fails on baseline
        missing = [i for i in EXPECTED_IDS if i not in actual_ids]
        assert missing == [], (
            f"Export is missing task IDs: {missing}. "
            f"Got {actual_ids!r}. "
            f"Variant: {VARIANT!r}. "
            "This is the known pagination defect: cursor uses only created_at, "
            "so tasks with tied timestamps after a page boundary are skipped."
        )

    def test_page_size_3_no_duplicates(self):
        """Export must not return any task more than once."""
        records = load_fixture()
        result = export_all(records, page_size=3)
        actual_ids = [r["id"] for r in result]
        seen = set()
        duplicates = []
        for i in actual_ids:
            if i in seen:
                duplicates.append(i)
            seen.add(i)
        assert duplicates == [], (
            f"Export contains duplicate IDs: {duplicates}. Got {actual_ids!r}."
        )

    def test_page_size_3_stable_order(self):
        """IDs must appear in (created_at, id) ascending order."""
        records = load_fixture()
        result = export_all(records, page_size=3)
        actual_ids = [r["id"] for r in result]
        present = [i for i in EXPECTED_IDS if i in actual_ids]
        assert actual_ids == present, (
            f"Order is wrong. Expected {present!r}, got {actual_ids!r}."
        )
