from __future__ import annotations

import os

import click

from ..config import Config


@click.command()
@click.argument("command", required=False)
def editor(command: str | None):
    """Show or set the text editor `tt open` uses.

    With no argument, prints the configured editor (or the $VISUAL / $EDITOR fallback).
    With an argument, saves it — e.g. `tt editor "code -w"` or `tt editor vim`.
    """
    config = Config.load()
    if command is None:
        if config.editor:
            click.echo(config.editor)
        elif os.environ.get("VISUAL") or os.environ.get("EDITOR"):
            fallback = os.environ.get("VISUAL") or os.environ.get("EDITOR")
            click.echo(f"{fallback} (from $VISUAL/$EDITOR)")
        else:
            click.echo("(unset — falls back to your platform default)")
        return
    config.editor = command
    config.save()
    click.echo(f"Editor set to {command}")
