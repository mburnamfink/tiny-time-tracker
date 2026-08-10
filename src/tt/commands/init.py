from __future__ import annotations

import click

from ..config import Config, resolve_store_path


@click.command()
@click.argument("path", required=False)
def init(path: str | None):
    """Set the storage location, or print the current one.

    PATH ending in .jsonl is the store file itself; any other PATH is a directory
    whose store file is <dir>/entries.jsonl. Does not move existing entries (use `tt migrate`).
    """
    config = Config.load()
    if path is None:
        click.echo(str(config.store_path))
        return
    store_path = resolve_store_path(path)
    store_path.parent.mkdir(parents=True, exist_ok=True)
    config.store_path = store_path
    config.save()
    click.echo(f"Store path set to {store_path}")
