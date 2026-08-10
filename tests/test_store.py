from __future__ import annotations

import json
import uuid
from datetime import date

from tt.store import Entry, append_entry


def test_entry_key_order():
    e = Entry.create(day=date(2026, 8, 10), hours=2.0, category="book-review", note="x")
    assert list(e.to_dict().keys()) == ["day", "hours", "category", "note", "id", "logged_at"]


def test_entry_create_provenance():
    e = Entry.create(day=date(2026, 8, 10), hours=2.0, category="admin", note="")
    assert e.day == "2026-08-10"
    uuid.UUID(e.id)  # valid uuid4-parseable
    assert e.logged_at.endswith("Z")


def test_append_entry(tmp_path):
    store = tmp_path / "sub" / "entries.jsonl"
    e1 = Entry.create(day=date(2026, 8, 10), hours=2.0, category="book-review", note="review of X")
    e2 = Entry.create(day=date(2026, 8, 9), hours=1.5, category="admin", note="")
    append_entry(store, e1)
    append_entry(store, e2)

    lines = store.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    assert first["day"] == "2026-08-10"
    assert first["hours"] == 2.0
    assert first["category"] == "book-review"
    assert first["note"] == "review of X"
    assert json.loads(lines[1])["note"] == ""
