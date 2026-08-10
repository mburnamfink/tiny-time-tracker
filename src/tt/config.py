from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import tomli_w

CONFIG_PATH = Path.home() / ".tt" / "config.toml"

_DEFAULT_STORE_PATH = Path.home() / ".tt" / "store" / "entries.jsonl"


def resolve_store_path(raw: str) -> Path:
    """Apply the path convention: a `.jsonl` path is the store file itself; any other path is a
    directory whose store file is `<dir>/entries.jsonl`. Expands `~`."""
    p = Path(raw).expanduser()
    if p.suffix == ".jsonl":
        return p
    return p / "entries.jsonl"


@dataclass
class Config:
    store_path: Path = field(default_factory=lambda: _DEFAULT_STORE_PATH)

    @classmethod
    def load(cls) -> "Config":
        if not CONFIG_PATH.exists():
            return cls()
        with open(CONFIG_PATH, "rb") as f:
            data = tomllib.load(f)
        store_path = Path(data.get("store_path", str(_DEFAULT_STORE_PATH)))
        return cls(store_path=store_path)

    def save(self) -> None:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        data: dict = {"store_path": str(self.store_path)}
        with open(CONFIG_PATH, "wb") as f:
            tomli_w.dump(data, f)
