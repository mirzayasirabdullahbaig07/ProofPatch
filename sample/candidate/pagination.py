"""
Pagination module (CANDIDATE — repaired by Bob).

Fix: the cursor now tracks both created_at and id so that ties are broken
correctly.  The filter uses (created_at, id) > (last_ts, last_id), which
preserves every record in a tie group after a page boundary.
"""
from __future__ import annotations

from datetime import datetime


def list_tasks(records: list[dict], cursor: dict | None, page_size: int) -> tuple[list[dict], dict | None]:
    """Return one page of tasks and the next cursor.

    cursor shape: {"created_at": <datetime>, "id": <int>}
    Sorting and filtering both use (created_at, id) so tied timestamps are
    handled correctly.
    """
    if page_size < 1:
        raise ValueError(f"page_size must be >= 1, got {page_size!r}")

    sorted_records = sorted(records, key=lambda r: (r["created_at"], r["id"]))

    if cursor is None:
        filtered = sorted_records
    else:
        last_ts = cursor["created_at"]
        last_id = cursor["id"]
        # FIX: compare the full (created_at, id) pair so no record in a
        # tie group is skipped.
        filtered = [
            r for r in sorted_records
            if (r["created_at"], r["id"]) > (last_ts, last_id)
        ]

    page = filtered[:page_size]

    if not page:
        return page, None

    next_cursor = {"created_at": page[-1]["created_at"], "id": page[-1]["id"]}
    return page, next_cursor


def export_all(records: list[dict], page_size: int, _max_iterations: int = 100) -> list[dict]:
    """Collect all pages. Hard iteration limit prevents infinite loops."""
    if page_size < 1:
        raise ValueError(f"page_size must be >= 1, got {page_size!r}")

    results: list[dict] = []
    cursor = None
    for _ in range(_max_iterations):
        page, cursor = list_tasks(records, cursor, page_size)
        results.extend(page)
        if cursor is None:
            break
    return results
