from __future__ import annotations

from datetime import date

import pytest
from click.testing import CliRunner

from tt.categories import category_counts, known_categories
from tt.cli import cli
from tt.config import Config
from tt.store import Entry, append_entry


@pytest.fixture
def store(tmp_path, monkeypatch):
    path = tmp_path / "store" / "entries.jsonl"
    monkeypatch.setattr(Config, "load", classmethod(lambda cls: cls(store_path=path)))
    return path


def _seed(path):
    for cat in ["admin", "book-review", "admin", "cooking"]:
        append_entry(path, Entry.create(day=date.today(), hours=1.0, category=cat, note=""))


def test_known_categories_distinct_sorted(store):
    _seed(store)
    assert known_categories(store) == ["admin", "book-review", "cooking"]


def test_category_counts(store):
    _seed(store)
    assert category_counts(store)["admin"] == 2


def test_known_categories_empty_store(store):
    assert known_categories(store) == []


def test_cats_command_lists_sorted_with_counts(store):
    _seed(store)
    r = CliRunner().invoke(cli, ["cats"])
    assert r.exit_code == 0, r.output
    lines = r.output.splitlines()
    assert lines[0].startswith("admin") and lines[0].endswith("2")
    assert [l.split()[0] for l in lines] == ["admin", "book-review", "cooking"]


def test_cats_command_empty(store):
    r = CliRunner().invoke(cli, ["cats"])
    assert r.exit_code == 0
    assert "No categories" in r.output
