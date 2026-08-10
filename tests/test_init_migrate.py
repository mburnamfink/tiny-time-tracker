from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from tt.cli import cli
from tt.config import Config, resolve_store_path


@pytest.fixture
def cfg(tmp_path, monkeypatch):
    """Redirect the config file to a temp location so init/migrate round-trip in isolation."""
    monkeypatch.setattr("tt.config.CONFIG_PATH", tmp_path / "config.toml")
    return tmp_path


# --- resolve_store_path -----------------------------------------------------


def test_resolve_jsonl_is_file(tmp_path):
    p = tmp_path / "tt.jsonl"
    assert resolve_store_path(str(p)) == p


def test_resolve_dir_gets_entries_jsonl(tmp_path):
    assert resolve_store_path(str(tmp_path / "d")) == tmp_path / "d" / "entries.jsonl"


def test_resolve_expands_tilde():
    assert resolve_store_path("~/notes/tt.jsonl") == Path.home() / "notes" / "tt.jsonl"


# --- tt init ----------------------------------------------------------------


def test_init_no_arg_prints_current(cfg):
    Config(store_path=cfg / "here" / "entries.jsonl").save()
    r = CliRunner().invoke(cli, ["init"])
    assert r.exit_code == 0, r.output
    assert r.output.strip() == str(cfg / "here" / "entries.jsonl")


def test_init_no_arg_does_not_modify(cfg):
    Config(store_path=cfg / "here" / "entries.jsonl").save()
    before = (cfg / "config.toml").read_text()
    CliRunner().invoke(cli, ["init"])
    assert (cfg / "config.toml").read_text() == before


def test_init_file_path(cfg):
    dest = cfg / "notes" / "tt.jsonl"
    r = CliRunner().invoke(cli, ["init", str(dest)])
    assert r.exit_code == 0, r.output
    assert Config.load().store_path == dest
    assert dest.parent.is_dir()


def test_init_dir_path(cfg):
    r = CliRunner().invoke(cli, ["init", str(cfg / "gdrive")])
    assert r.exit_code == 0, r.output
    assert Config.load().store_path == cfg / "gdrive" / "entries.jsonl"


# --- tt migrate -------------------------------------------------------------


def _seed(path: Path, body: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def test_migrate_copies_and_switches(cfg):
    src = cfg / "old" / "entries.jsonl"
    body = '{"day":"2026-08-10","hours":1.0,"category":"a","note":""}\n{"day":"2026-08-10","hours":2.0,"category":"b","note":""}\n'
    _seed(src, body)
    Config(store_path=src).save()

    dest_dir = cfg / "new"
    r = CliRunner().invoke(cli, ["migrate", str(dest_dir)])
    assert r.exit_code == 0, r.output

    dest = dest_dir / "entries.jsonl"
    assert dest.read_text(encoding="utf-8") == body  # verbatim
    assert Config.load().store_path == dest
    assert src.exists()  # copy, not move
    assert "2 entries" in r.output


def test_migrate_refuses_existing_destination(cfg):
    src = cfg / "old" / "entries.jsonl"
    _seed(src, '{"day":"2026-08-10","hours":1.0,"category":"a","note":""}\n')
    Config(store_path=src).save()

    dest = cfg / "new" / "entries.jsonl"
    _seed(dest, '{"existing":"data"}\n')

    r = CliRunner().invoke(cli, ["migrate", str(cfg / "new")])
    assert r.exit_code != 0
    assert Config.load().store_path == src  # unchanged
    assert dest.read_text(encoding="utf-8") == '{"existing":"data"}\n'  # untouched


def test_migrate_no_existing_source(cfg):
    src = cfg / "old" / "entries.jsonl"  # never created
    Config(store_path=src).save()
    r = CliRunner().invoke(cli, ["migrate", str(cfg / "new")])
    assert r.exit_code == 0, r.output
    dest = cfg / "new" / "entries.jsonl"
    assert dest.exists()
    assert Config.load().store_path == dest
    assert "0 entries" in r.output
