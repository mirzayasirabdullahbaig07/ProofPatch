"""
Pagination module (BASELINE — contains the known defect).

Defect: the cursor tracks only created_at, so when several tasks share the
same timestamp the query `created_at > last_timestamp` skips all remaining
tasks in that group after the first page boundary.
"""
from __future__ import annotations

from datetime import datetime


def list_tasks(records: list[dict], cursor: dict | None, page_size: int) -> tuple[list[dict], dict | None]:
    """Return one page of tasks and the next cursor.

    cursor shape: {"created_at": <datetime>}   ← baseline ignores id on purpose.
    Records are sorted by (created_at, id) for consistent ordering, but the
    cursor only advances by created_at, causing records to be skipped.
    """
    if page_size < 1:
        raise ValueError(f"page_size must be >= 1, got {page_size!r}")

    sorted_records = sorted(records, key=lambda r: (r["created_at"], r["id"]))

    if cursor is None:
        filtered = sorted_records
    else:
        last_ts = cursor["created_at"]
        # BUG: uses strictly-greater-than on timestamp only; ties after a
        # page boundary are silently dropped.
        filtered = [r for r in sorted_records if r["created_at"] > last_ts]

    page = filtered[:page_size]

    if not page:
        return page, None

    next_cursor = {"created_at": page[-1]["created_at"]}
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
