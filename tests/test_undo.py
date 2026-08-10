from __future__ import annotations

from datetime import date

import pytest
from click.testing import CliRunner

from tt.cli import cli
from tt.config import Config
from tt.store import Entry, append_entry, remove_last_entry


@pytest.fixture
def store(tmp_path, monkeypatch):
    path = tmp_path / "store" / "entries.jsonl"
    monkeypatch.setattr(Config, "load", classmethod(lambda cls: cls(store_path=path)))
    return path


def _seed(path, n=2):
    for i in range(n):
        append_entry(path, Entry.create(day=date.today(), hours=float(i + 1), category=f"cat{i}", note=""))


def test_remove_last_entry_preserves_others_verbatim(store):
    store.parent.mkdir(parents=True)
    hand_edited = '{"day": "2026-08-01", "hours": 3.0, "category": "kept", "note": "verbatim"}'
    store.write_text(hand_edited + "\n" + '{"day":"2026-08-02","hours":1.0,"category":"gone","note":""}\n', encoding="utf-8")
    removed = remove_last_entry(store)
    assert '"category":"gone"' in removed
    assert store.read_text(encoding="utf-8") == hand_edited + "\n"


def test_remove_last_entry_empty_store(store):
    assert remove_last_entry(store) is None


def test_undo_confirms_and_removes_last(store):
    _seed(store, 2)
    r = CliRunner().invoke(cli, ["undo"], input="y\n")
    assert r.exit_code == 0, r.output
    lines = store.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert "cat0" in lines[0] and "cat1" not in lines[0]


def test_undo_declined_leaves_file_untouched(store):
    _seed(store, 2)
    before = store.read_text(encoding="utf-8")
    r = CliRunner().invoke(cli, ["undo"], input="n\n")
    assert r.exit_code == 0
    assert store.read_text(encoding="utf-8") == before


def test_undo_empty_store(store):
    r = CliRunner().invoke(cli, ["undo"])
    assert r.exit_code == 0
    assert "Nothing to undo" in r.output


def test_undo_shows_entry_before_prompt(store):
    _seed(store, 1)
    r = CliRunner().invoke(cli, ["undo"], input="n\n")
    assert "cat0" in r.output
