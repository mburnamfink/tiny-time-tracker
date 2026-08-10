from __future__ import annotations

import shutil

import click

from ..config import Config, resolve_store_path
from ..store import read_entries


@click.command()
@click.argument("path")
def migrate(path: str):
    """Copy entries to a new store location and switch to it.

    PATH follows the same convention as `tt init`. The current store is copied verbatim
    (the original is left in place as a backup); config is then pointed at the new location.
    """
    config = Config.load()
    src = config.store_path
    dest = resolve_store_path(path)

    if dest == src:
        raise click.ClickException("Destination is the same as the current store path.")
    if dest.exists() and dest.stat().st_size > 0:
        raise click.ClickException(f"Refusing to overwrite existing store at {dest}.")

    dest.parent.mkdir(parents=True, exist_ok=True)
    count = len(read_entries(src))
    if src.exists():
        shutil.copyfile(src, dest)
    else:
        dest.touch()

    config.store_path = dest
    config.save()
    click.echo(f"Copied {count} entries to {dest} and set it as the store.")
