from __future__ import annotations

import click

from ..config import Config
from ..store import read_entries, remove_last_entry


def _format_entry(e: dict) -> str:
    note = f"  {e['note']}" if e.get("note") else ""
    return f"{e['day']}  {e['hours']}h  {e['category']}{note}"


@click.command()
def undo():
    """Remove the last logged entry, after confirmation."""
    path = Config.load().store_path
    entries = read_entries(path)
    if not entries:
        click.echo("Nothing to undo — the store is empty.")
        return
    click.echo(_format_entry(entries[-1]))
    if not click.confirm("Remove this entry?", default=False):
        click.echo("Kept.")
        return
    remove_last_entry(path)
    click.echo("Removed.")
