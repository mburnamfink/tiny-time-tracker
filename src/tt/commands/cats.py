from __future__ import annotations

import click

from ..categories import category_counts
from ..config import Config


@click.command()
def cats():
    """List known categories with entry counts, sorted."""
    counts = category_counts(Config.load().store_path)
    if not counts:
        click.echo("No categories logged yet.")
        return
    width = max(len(c) for c in counts)
    for cat in sorted(counts):
        click.echo(f"{cat:<{width}}  {counts[cat]}")
