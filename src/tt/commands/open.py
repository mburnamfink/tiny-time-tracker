from __future__ import annotations

import click

from ..config import Config


@click.command("open")
def open_store():
    """Open the store file in your text editor.

    Uses the editor from `tt editor`, else $VISUAL / $EDITOR, else the platform default.
    """
    config = Config.load()
    path = config.store_path
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.touch()
    click.edit(filename=str(path), editor=config.editor)
