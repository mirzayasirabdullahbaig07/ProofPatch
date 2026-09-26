"""
Repository module: load task records from a JSON file.
"""
import json
from datetime import datetime, timezone


def load_tasks(path: str) -> list[dict]:
    """Load tasks from a JSON file. Each record must have id and created_at."""
    with open(path, "r", encoding="utf-8") as fh:
        records = json.load(fh)
    for r in records:
        if isinstance(r.get("created_at"), str):
            r["created_at"] = datetime.fromisoformat(r["created_at"])
            if r["created_at"].tzinfo is None:
                r["created_at"] = r["created_at"].replace(tzinfo=timezone.utc)
    return records
