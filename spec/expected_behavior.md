# Expected Behavior

## Function contract

Both `list_tasks` and `export_all` (and their module-level aliases) must obey
the following contract regardless of implementation variant.

### `list_tasks(records, cursor, page_size) -> (page, next_cursor)`

- `records`: list of task dicts, each with integer `id` and `datetime` `created_at`.
- `cursor`: `None` for the first page, or a dict returned by the previous call.
- `page_size`: positive integer (supported values: 2, 3, 4).
- Returns a tuple `(page, next_cursor)`.
  - `page` is a list of at most `page_size` task dicts.
  - `next_cursor` is `None` when no more records remain; otherwise a dict
    that can be passed to the next call.
- Must raise `ValueError` for `page_size < 1`.

### `export_all(records, page_size) -> list[dict]`

- Calls `list_tasks` repeatedly until `next_cursor` is `None`.
- Returns every task in `records` **exactly once**.
- Tasks are ordered stably by `(created_at, id)` ascending.
- The iteration is bounded; the function always terminates.
- Must raise `ValueError` for `page_size < 1`.

## Fixture

Eight tasks with IDs 1–8:

| ID | created_at (UTC)         | Note                                  |
|----|--------------------------|---------------------------------------|
| 1  | 2026-01-01 09:00:00+00   | Ordinary first record                 |
| 2  | 2026-01-01 09:01:00+00   | Tie group — crosses page boundary     |
| 3  | 2026-01-01 09:01:00+00   | Tie group                             |
| 4  | 2026-01-01 09:01:00+00   | Tie group — skipped by baseline       |
| 5  | 2026-01-01 09:02:00+00   | Ordinary following record             |
| 6  | 2026-01-01 09:03:00+00   | Second tie group                      |
| 7  | 2026-01-01 09:03:00+00   | Second tie group                      |
| 8  | 2026-01-01 09:04:00+00   | Final partial-page case               |

## Acceptance criteria

For **every supported page size** (2, 3, 4):

1. `export_all` returns exactly 8 records.
2. The returned IDs are `[1, 2, 3, 4, 5, 6, 7, 8]` in that order.
3. No ID appears more than once.
4. The function terminates (enforced by the iteration limit).

For an **empty record list**:

5. `export_all` returns an empty list without raising an exception.

For a **single record**:

6. `export_all` returns a list containing that one record.
