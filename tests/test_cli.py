from __future__ import annotations

import json
from datetime import date, timedelta

import pytest
from click.testing import CliRunner

from tt.cli import cli
from tt.config import Config


@pytest.fixture
def store(tmp_path, monkeypatch):
    path = tmp_path / "store" / "entries.jsonl"
    monkeypatch.setattr(Config, "load", classmethod(lambda cls: cls(store_path=path)))
    return path


def _lines(path):
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()]


def test_log_basic_entry(store):
    r = CliRunner().invoke(cli, ["2", "book-review", "review", "of", "Dirty", "Dangerous", "Young"])
    assert r.exit_code == 0, r.output
    (entry,) = _lines(store)
    assert entry["day"] == date.today().isoformat()
    assert entry["hours"] == 2.0
    assert entry["category"] == "book-review"
    assert entry["note"] == "review of Dirty Dangerous Young"
    assert list(entry.keys()) == ["day", "hours", "category", "note", "id", "logged_at"]


@pytest.mark.parametrize("hours", ["90m", "1h30m", "1.5"])
def test_log_hours_forms(store, hours):
    r = CliRunner().invoke(cli, [hours, "admin"])
    assert r.exit_code == 0, r.output
    assert _lines(store)[0]["hours"] == 1.5


def test_log_date_relative(store):
    r = CliRunner().invoke(cli, ["-d", "-1", "1", "cooking", "dinner"])
    assert r.exit_code == 0, r.output
    assert _lines(store)[0]["day"] == (date.today() - timedelta(days=1)).isoformat()


def test_log_date_iso(store):
    r = CliRunner().invoke(cli, ["-d", "2026-08-09", "1", "cooking", "dinner"])
    assert r.exit_code == 0, r.output
    assert _lines(store)[0]["day"] == "2026-08-09"


def test_log_date_rejects_bad_form(store):
    r = CliRunner().invoke(cli, ["-d", "2", "1", "cooking"])
    assert r.exit_code != 0
    assert not store.exists()


def test_log_category_normalised(store):
    for variant in ["Book Review", "BookReview", "book_review"]:
        CliRunner().invoke(cli, ["1", variant])
    cats = {e["category"] for e in _lines(store)}
    assert cats == {"book-review", "bookreview"}


def test_log_empty_note(store):
    CliRunner().invoke(cli, ["1", "admin"])
    assert _lines(store)[0]["note"] == ""
