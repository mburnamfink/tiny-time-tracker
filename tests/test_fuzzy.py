from __future__ import annotations

from datetime import date

import pytest
from click.testing import CliRunner

from tt.categories import suggest_similar
from tt.cli import cli
from tt.config import Config
from tt.store import Entry, append_entry, read_entries


@pytest.fixture
def store(tmp_path, monkeypatch):
    path = tmp_path / "store" / "entries.jsonl"
    monkeypatch.setattr(Config, "load", classmethod(lambda cls: cls(store_path=path)))
    return path


# --- suggest_similar --------------------------------------------------------


def test_suggest_near_miss():
    assert suggest_similar("admyn", ["admin", "cooking"]) == ["admin"]


def test_suggest_known_category_is_silent():
    assert suggest_similar("admin", ["admin", "cooking"]) == []


def test_suggest_no_close_match():
    assert suggest_similar("parenting", ["admin", "cooking"]) == []


def test_suggest_empty_known():
    assert suggest_similar("admin", []) == []


# --- log path integration ---------------------------------------------------


def _seed(path):
    append_entry(path, Entry.create(day=date.today(), hours=1.0, category="admin", note=""))


def test_log_near_miss_warns_but_appends(store):
    _seed(store)
    r = CliRunner().invoke(cli, ["1", "admyn"])
    assert r.exit_code == 0, r.output
    assert "did you mean 'admin'" in r.output
    cats = [e["category"] for e in read_entries(store)]
    assert cats == ["admin", "admyn"]  # logged regardless


def test_log_known_category_no_warning(store):
    _seed(store)
    r = CliRunner().invoke(cli, ["2", "admin"])
    assert r.exit_code == 0
    assert "did you mean" not in r.output


def test_log_brand_new_category_no_warning(store):
    _seed(store)
    r = CliRunner().invoke(cli, ["1", "parenting"])
    assert r.exit_code == 0
    assert "did you mean" not in r.output
    assert read_entries(store)[-1]["category"] == "parenting"


def test_log_first_ever_category_no_warning(store):
    r = CliRunner().invoke(cli, ["1", "admin"])
    assert r.exit_code == 0
    assert "did you mean" not in r.output
