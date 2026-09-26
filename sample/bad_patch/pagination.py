"""
Pagination module (BAD_PATCH — deliberately incorrect repair).

This is a NEGATIVE CONTROL constructed to demonstrate what a wrong fix looks
like.  Changing `>` to `>=` on the timestamp alone causes records at a page
boundary to be repeated on every subsequent page, producing duplicates.

This is NOT a Bob mistake.  It is a labelled negative control.
"""
from __future__ import annotations

from datetime import datetime


def list_tasks(records: list[dict], cursor: dict | None, page_size: int) -> tuple[list[dict], dict | None]:
    """Return one page of tasks and the next cursor.

    cursor shape: {"created_at": <datetime>}
    WRONG: uses >= on timestamp, so the last record of every page is repeated.
    """
    if page_size < 1:
        raise ValueError(f"page_size must be >= 1, got {page_size!r}")

    sorted_records = sorted(records, key=lambda r: (r["created_at"], r["id"]))

    if cursor is None:
        filtered = sorted_records
    else:
        last_ts = cursor["created_at"]
        # INTENTIONAL BUG (negative control): >= repeats records whose
        # created_at equals the cursor timestamp.
        filtered = [r for r in sorted_records if r["created_at"] >= last_ts]

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
