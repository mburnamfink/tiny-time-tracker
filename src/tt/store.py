from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

# Emit keys in this order so hand-scanning the JSONL reads day / hours / category / note first.
_KEY_ORDER = ("day", "hours", "category", "note", "id", "logged_at")


@dataclass
class Entry:
    day: str
    hours: float
    category: str
    note: str
    id: str
    logged_at: str

    @classmethod
    def create(cls, day: date, hours: float, category: str, note: str) -> "Entry":
        """Build an entry with a fresh uuid4 and current UTC logged_at provenance."""
        logged_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return cls(
            day=day.isoformat(),
            hours=hours,
            category=category,
            note=note,
            id=str(uuid.uuid4()),
            logged_at=logged_at,
        )

    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in _KEY_ORDER}

    def to_json_line(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


def append_entry(path: Path, entry: Entry) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(entry.to_json_line() + "\n")


def read_entries(path: Path) -> list[dict]:
    """Read the whole store as a list of raw dicts. Empty list if it doesn't exist yet."""
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            entries.append(json.loads(line))
    return entries


def remove_last_entry(path: Path) -> str | None:
    """Drop the last non-blank line, preserving every other line verbatim (the file may be
    hand-edited). Returns the removed line, or None if there was nothing to remove."""
    if not path.exists():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    idx = next((i for i in range(len(lines) - 1, -1, -1) if lines[i].strip()), None)
    if idx is None:
        return None
    removed = lines[idx]
    del lines[idx]
    text = "\n".join(lines)
    if text:
        text += "\n"
    path.write_text(text, encoding="utf-8")
    return removed
