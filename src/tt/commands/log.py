from __future__ import annotations

from datetime import date

import click

from ..config import Config
from ..parsing import parse_date, parse_hours, slugify
from ..store import Entry, append_entry


@click.command()
@click.argument("hours")
@click.argument("category")
@click.argument("note", nargs=-1)
@click.option("-d", "--date", "date_", default=None, help="Day the work happened: a negative integer (days ago) or an ISO date. Default: today.")
def log(hours: str, category: str, note: tuple[str, ...], date_: str | None):
    """Log a time entry: tt <hours> <category> [note...]."""
    try:
        parsed_hours = parse_hours(hours)
    except ValueError as e:
        raise click.BadParameter(str(e), param_hint="hours")

    try:
        day = parse_date(date_) if date_ is not None else date.today()
    except ValueError as e:
        raise click.BadParameter(str(e), param_hint="-d/--date")

    cat = slugify(category)
    entry = Entry.create(day=day, hours=parsed_hours, category=cat, note=" ".join(note))

    config = Config.load()
    append_entry(config.store_path, entry)
