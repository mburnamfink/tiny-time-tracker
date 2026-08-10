"""Top-level ``tt`` command group.

The primary command is logging, invoked bare as ``tt <hours> <category> [note...]``.
A group can't do that natively, so :class:`DefaultGroup` injects the ``log`` command name
when the first token isn't a known subcommand (or is a leading option like ``-d``).
"""
from __future__ import annotations

import click

from .commands import cats as cats_cmd
from .commands import editor as editor_cmd
from .commands import init as init_cmd
from .commands import log as log_cmd
from .commands import migrate as migrate_cmd
from .commands import open as open_cmd
from .commands import undo as undo_cmd


class DefaultGroup(click.Group):
    def __init__(self, *args, default_command: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_command = default_command

    def parse_args(self, ctx, args):
        if (
            self.default_command
            and args
            and args[0] not in self.commands
            and args[0] not in ("-h", "--help")
        ):
            args = [self.default_command, *args]
        return super().parse_args(ctx, args)


@click.group(
    cls=DefaultGroup,
    default_command="log",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def cli():
    """Personal terminal-first time tracker. Log with: tt <hours> <category> [note...]."""


cli.add_command(log_cmd.log)
cli.add_command(cats_cmd.cats)
cli.add_command(undo_cmd.undo)
cli.add_command(init_cmd.init)
cli.add_command(migrate_cmd.migrate)
cli.add_command(open_cmd.open_store)
cli.add_command(editor_cmd.editor)
