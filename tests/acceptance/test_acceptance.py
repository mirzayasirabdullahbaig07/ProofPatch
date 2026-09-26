"""
Independent acceptance checks (Student B).

Written from spec/expected_behavior.md — NOT by reading the candidate
implementation. Apply equally to all three variants; never skip.

Variant is controlled by the PROOFPATCH_VARIANT environment variable.
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

FIXTURE_PATH = Path(__file__).resolve().parents[2] / "sample" / "data" / "tasks.json"
EXPECTED_IDS = [1, 2, 3, 4, 5, 6, 7, 8]


def load_fixture() -> list[dict]:
    with open(FIXTURE_PATH, "r", encoding="utf-8") as fh:
        records = json.load(fh)
    for r in records:
        if isinstance(r.get("created_at"), str):
            r["created_at"] = datetime.fromisoformat(r["created_at"])
            if r["created_at"].tzinfo is None:
                r["created_at"] = r["created_at"].replace(tzinfo=timezone.utc)
    return records


def make_task(id_: int, ts: str) -> dict:
    return {"id": id_, "title": f"Task {id_}", "created_at": datetime.fromisoformat(ts)}


# ---------------------------------------------------------------------------
# AC-1  Empty dataset
# ---------------------------------------------------------------------------

class TestEmptyDataset:
    def test_empty_export_returns_empty_list(self):
        result = export_all([], page_size=3)
        assert result == [], f"Expected [], got {result!r}"

    def test_list_tasks_empty_no_cursor(self):
        page, cursor = list_tasks([], None, page_size=3)
        assert page == []
        assert cursor is None


# ---------------------------------------------------------------------------
# AC-2  Unique timestamps
# ---------------------------------------------------------------------------

class TestUniqueTimestamps:
    def test_page_size_2(self):
        records = [make_task(i, f"2026-01-01T0{i}:00:00+00:00") for i in range(1, 6)]
        result = export_all(records, page_size=2)
        assert [r["id"] for r in result] == [1, 2, 3, 4, 5]

    def test_page_size_3(self):
        records = [make_task(i, f"2026-01-01T0{i}:00:00+00:00") for i in range(1, 9)]
        result = export_all(records, page_size=3)
        assert [r["id"] for r in result] == list(range(1, 9))


# ---------------------------------------------------------------------------
# AC-3  Tied timestamps (main fixture, multiple page sizes)
# ---------------------------------------------------------------------------

class TestTiedTimestamps:
    @pytest.mark.parametrize("page_size", [2, 3, 4])
    def test_all_ids_present(self, page_size):
        records = load_fixture()
        result = export_all(records, page_size=page_size)
        actual_ids = [r["id"] for r in result]
        missing = [i for i in EXPECTED_IDS if i not in actual_ids]
        assert missing == [], f"page_size={page_size}: missing {missing}, got {actual_ids!r}"

    @pytest.mark.parametrize("page_size", [2, 3, 4])
    def test_no_duplicates(self, page_size):
        records = load_fixture()
        result = export_all(records, page_size=page_size)
        actual_ids = [r["id"] for r in result]
        assert len(actual_ids) == len(set(actual_ids)), (
            f"page_size={page_size}: duplicates in {actual_ids!r}"
        )

    @pytest.mark.parametrize("page_size", [2, 3, 4])
    def test_stable_order(self, page_size):
        records = load_fixture()
        result = export_all(records, page_size=page_size)
        actual_ids = [r["id"] for r in result]
        assert actual_ids == EXPECTED_IDS, f"page_size={page_size}: got {actual_ids!r}"

    def test_ties_at_different_page_boundaries(self):
        t = [f"2026-01-01T09:0{i}:00+00:00" for i in range(3)]
        records = [
            make_task(1, t[0]), make_task(2, t[0]),
            make_task(3, t[1]), make_task(4, t[1]),
            make_task(5, t[2]), make_task(6, t[2]),
        ]
        for ps in [2, 3]:
            result = export_all(records, page_size=ps)
            assert [r["id"] for r in result] == [1, 2, 3, 4, 5, 6], (
                f"page_size={ps}: got {[r['id'] for r in result]!r}"
            )


# ---------------------------------------------------------------------------
# AC-4  Final partial page
# ---------------------------------------------------------------------------

class TestFinalPartialPage:
    def test_partial_page_retained(self):
        records = load_fixture()
        result = export_all(records, page_size=3)
        assert len(result) == 8, f"Expected 8 records, got {len(result)}"

    def test_single_record(self):
        records = [make_task(1, "2026-01-01T09:00:00+00:00")]
        result = export_all(records, page_size=3)
        assert [r["id"] for r in result] == [1]


# ---------------------------------------------------------------------------
# AC-5  Bounded termination
# ---------------------------------------------------------------------------

class TestBoundedTermination:
    def test_export_terminates(self):
        records = load_fixture()
        result = export_all(records, page_size=2)
        assert len(result) >= 1


# ---------------------------------------------------------------------------
# AC-6  Invalid page sizes
# ---------------------------------------------------------------------------

class TestInvalidPageSize:
    def test_list_tasks_raises_on_zero(self):
        with pytest.raises(ValueError):
            list_tasks([], None, page_size=0)

    def test_export_all_raises_on_zero(self):
        with pytest.raises(ValueError):
            export_all([], page_size=0)

    def test_list_tasks_raises_on_negative(self):
        with pytest.raises(ValueError):
            list_tasks([], None, page_size=-1)
