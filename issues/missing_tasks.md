# Bug Report: Export silently loses records when tasks share a creation time

**Reporter:** Team lead / mentor  
**Date filed:** 2026-09-22  
**Severity:** High — silent data loss  
**Status:** Open — reproducing test to be created before repair

---

## Observed behavior

Exporting all tasks sometimes returns fewer records than exist.  
The problem occurs when several tasks have the same `created_at` timestamp.

### Steps to reproduce

1. Load the eight-task fixture from `sample/data/tasks.json`.
2. Call `export_all(records, page_size=3)`.
3. Collect the returned task IDs.

**Expected:** `[1, 2, 3, 4, 5, 6, 7, 8]` — all eight IDs, each once.  
**Actual:** `[1, 2, 3, 5, 6, 7, 8]` — ID 4 is missing (seven records).

### Explanation of the defect

The pagination cursor stores only `created_at`. After returning page
`[1, 2, 3]` the cursor holds `created_at = 09:01:00`. The next page filter is
`created_at > 09:01:00`, which excludes task 4 (also at `09:01:00`), so it is
permanently skipped.

The same class of defect applies to any tie group that straddles a page
boundary.

---

## Required repair behavior

- Export must return every task **exactly once**.
- Stable ordering: sort by `(created_at, id)` ascending.
- Page-size limit must be respected.
- The public function interfaces (`list_tasks`, `export_all`) must not change.
- The fixture and regression test must not change.

## Files involved

| File | Role |
|------|------|
| `sample/baseline/pagination.py` | Contains the defect (preserve, do not repair) |
| `sample/candidate/pagination.py` | Target for Bob's repair |
| `sample/data/tasks.json` | Shared deterministic fixture |
| `spec/expected_behavior.md` | Full contract |

## Out of scope

- Database integration  
- HTTP server  
- Authentication  
- Any change to `sample/baseline/`  
