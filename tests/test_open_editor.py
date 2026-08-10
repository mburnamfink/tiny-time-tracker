from __future__ import annotations

import click
import pytest
from click.testing import CliRunner

from tt.cli import cli
from tt.config import Config


@pytest.fixture
def cfg(tmp_path, monkeypatch):
    """Isolate the config file so editor round-trips don't touch the real one."""
    monkeypatch.setattr("tt.config.CONFIG_PATH", tmp_path / "config.toml")
    return tmp_path


# --- tt open ----------------------------------------------------------------


def test_open_launches_editor_on_store(tmp_path, monkeypatch):
    store = tmp_path / "store" / "entries.jsonl"
    monkeypatch.setattr(Config, "load", classmethod(lambda cls: cls(store_path=store, editor="myed")))
    calls = {}
    monkeypatch.setattr("click.edit", lambda filename=None, editor=None: calls.update(filename=filename, editor=editor))

    r = CliRunner().invoke(cli, ["open"])
    assert r.exit_code == 0, r.output
    assert calls["filename"] == str(store)
    assert calls["editor"] == "myed"
    assert store.exists()  # created if missing so the editor opens cleanly


def test_open_creates_parent_dir(tmp_path, monkeypatch):
    store = tmp_path / "deep" / "nested" / "entries.jsonl"
    monkeypatch.setattr(Config, "load", classmethod(lambda cls: cls(store_path=store)))
    monkeypatch.setattr("click.edit", lambda filename=None, editor=None: None)
    r = CliRunner().invoke(cli, ["open"])
    assert r.exit_code == 0, r.output
    assert store.parent.is_dir()


# --- tt editor --------------------------------------------------------------


def test_editor_set_and_persist(cfg):
    r = CliRunner().invoke(cli, ["editor", "code -w"])
    assert r.exit_code == 0, r.output
    assert Config.load().editor == "code -w"


def test_editor_print_configured(cfg):
    Config(store_path=cfg / "s.jsonl", editor="vim").save()
    r = CliRunner().invoke(cli, ["editor"])
    assert r.exit_code == 0
    assert r.output.strip() == "vim"


def test_editor_print_env_fallback(cfg, monkeypatch):
    monkeypatch.setenv("VISUAL", "nano")
    r = CliRunner().invoke(cli, ["editor"])
    assert r.exit_code == 0
    assert "nano" in r.output and "VISUAL" in r.output


def test_editor_print_unset(cfg, monkeypatch):
    monkeypatch.delenv("VISUAL", raising=False)
    monkeypatch.delenv("EDITOR", raising=False)
    r = CliRunner().invoke(cli, ["editor"])
    assert r.exit_code == 0
    assert "unset" in r.output
