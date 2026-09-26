"""
Export module: assemble pages into a final export list.
"""
from proofpatch.sample.candidate.pagination import export_all


def export_tasks(records: list[dict], page_size: int) -> list[dict]:
    """Return every task exactly once, ordered by (created_at, id)."""
    return export_all(records, page_size)
