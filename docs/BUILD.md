# `tt` — Build Spec

A personal, single-user, terminal-first time tracker for self-insight (Paul Graham Raven-style
weeknotes). No billing, no multi-user, no live timer. Logging is **retrospective** ("I spent 2
hours on X"), must feel **instant**, and must work **offline**. This document is self-contained:
it is enough to implement `tt` from a cold start. See `../CONTEXT.md` for the glossary and
`adr/` for the two decisions behind this shape.

## Scope of v0

**In:** logging an entry, undoing the last entry, git-syncing the store, listing categories.
**Out (deferred):** all reading/analysis (weeknotes, date ranges, PGR prose, aggregation),
`tt edit <id>`, and any phone/web entry path. **v0 is write-only** — you read the raw JSONL in
an editor until the analysis layer is designed.

## Storage

Append-only JSONL, one entry per line. Path comes from config (below). Each line:

```json
{"day":"2026-08-10","hours":2.0,"category":"book-review","note":"review of Dirty Dangerous Young","id":"<uuid4>","logged_at":"2026-08-10T14:03:11Z"}
```

- `day` — ISO date (`YYYY-MM-DD`) the work happened; defaults to today. No wall-clock time (retrospective logging makes it meaningless).
- `hours` — decimal float.
- `category` — kebab-case string (normalised, see below).
- `note` — free text; empty string if none.
- `id` — uuid4, so entries are addressable for a future `tt edit`. Placed near the end so it doesn't clog a manual scan.
- `logged_at` — RFC 3339 UTC timestamp of when the entry was *recorded* (provenance). Also at the end.

Emit keys in the order above so hand-scanning the file in an editor reads `day / hours / category / note` first.

## Command surface

Built on **Click**. A `@click.group()` named `cli` in `tt/cli.py`; subcommands live in
`tt/commands/` and are registered flat via `cli.add_command(...)` (mirror the sibling
`review-cli` layout at `/home/michael/dev/book-review-site/review-cli`).

### `tt <hours> <category> [note...]` — log an entry (the default/primary command)
- `hours` (positional): accept `1.5` (decimal hours) **or** `1h30m` **or** `90m` — all resolve to the same decimal hours. Do **not** enforce quarter-hour rounding; store what was given.
- `category` (positional, single token): normalise to kebab-case before storing (see below).
- `note` (`nargs=-1`): greedy remainder joined with spaces; may be empty.
- `-d, --date`: override `day`. Accept **only** a negative integer (days ago, e.g. `-2`) **or** an ISO 8601 date (`2026-08-09`). Reject anything else. Default: today.
- Behaviour: normalise category, run the fuzzy check (may print a warning, never blocks), append one JSONL line with a fresh uuid4 and current UTC `logged_at`. Must not touch git (git is never in the logging hot path).

### `tt undo` — remove the last entry
Print the last line's entry (human-readable), ask for confirmation, and on yes rewrite the file
without that last line. On no, do nothing.

### `tt sync` — off-machine backup via git (manual only)
Run the full git workflow against the store's repo: `git pull --rebase`, `git add`,
`git commit` (with a generated message), `git push`. This is the *only* place `tt` invokes git.
Its purpose is a backup that is not this computer. Append-only structure keeps merge conflicts trivial.

### `tt cats` — list known categories
Print the distinct categories found in the JSONL (with counts is a nice-to-have), sorted.

## Category normalisation & fuzzy matching

1. **Normalise** the supplied category with a slugify step (NFKD → ASCII, lowercase, spaces/underscores → `-`, strip non-word chars, collapse repeated `-`). So `Book Review`, `BookReview`, `book_review` all become `book-review`. (Reuse the `slug.py` pattern from `review-cli`; note `review` itself does *not* normalise its tags — this is a deliberate addition for `tt`.)
2. **Known set** = the distinct normalised categories already present in the JSONL. There is **no** curated config list. Scanning the whole file is fine (thousands of entries = sub-millisecond).
3. **Fuzzy check**: if the normalised category is not already known, run `difflib.get_close_matches(cat, known, n=3, cutoff=0.6)`. If there are close matches, print a non-blocking warning, e.g. `⚠ new category 'admyn' (did you mean 'admin'?) — logged anyway`, then log it regardless. **Never prompt, never block** — this preserves instant one-shot logging. (Typos are rare and cheap to fix via `tt undo` or editing the file; a curated canonical list is a possible additive upgrade later.)

## Config

A `Config` dataclass loading `~/.tt/config.toml` (mirror `review-cli`'s `Config`). Fields:
- `store_path` — path to the JSONL file. Default it to a sensible location inside a git-synced folder.
- `git_remote` / repo location used by `tt sync`.

`Config.load()` reads the TOML if present, else uses defaults; provide `Config.save()` for writes.

## Packaging & install (twin of `review-cli`)

- `src/`-layout, package name `tt`, distribution name `tt`.
- `pyproject.toml` with `build-system` = hatchling, `[project.scripts] tt = "tt.cli:cli"`, `[tool.hatch.build.targets.wheel] packages = ["src/tt"]`.
- Dependencies: `click>=8.0` (+ `rich` if you want pretty output, optional). Everything else is stdlib (`difflib`, `uuid`, `json`, `datetime`, `pathlib`, `tomllib`/`tomli-w`).
- Install: `uv tool install --editable /home/michael/dev/time-tracking/<pkg-dir>` → symlink in `~/.local/bin/tt`, on PATH from any terminal, edits live.
- Python work in this repo uses the `~/work` uv venv per the user's global rule; install packages with `uv pip install --python ~/work/bin/python <pkg>`.

## Suggested package layout

```
time-tracking/
├── CONTEXT.md
├── docs/
│   ├── BUILD.md
│   └── adr/{0001,0002}-*.md
├── pyproject.toml
├── src/tt/
│   ├── __init__.py
│   ├── cli.py            # Click group + add_command wiring
│   ├── config.py         # Config dataclass, ~/.tt/config.toml
│   ├── store.py          # JSONL append/read/rewrite, Entry model
│   ├── parsing.py        # hours + date parsing, slugify
│   ├── categories.py     # known-set scan + difflib fuzzy check
│   └── commands/
│       ├── log.py        # the default log command
│       ├── undo.py
│       ├── sync.py
│       └── cats.py
└── tests/                # pytest, pythonpath = ["src"]
```

## Definition of done (v0)

- `tt 2 book-review review of Dirty Dangerous Young` appends a correct JSONL line and returns instantly.
- `tt 90m admin` and `tt 1h30m admin` and `tt 1.5 admin` all store `hours: 1.5`.
- `tt -d -1 1 cooking dinner` and `tt -d 2026-08-09 1 cooking dinner` set `day` correctly; other `-d` forms are rejected.
- Category casing/spacing variants collapse to one kebab-case category; a near-miss prints a warning but still logs.
- `tt undo` shows the last entry, confirms, and removes exactly that line.
- `tt sync` performs pull-rebase/add/commit/push; no other command touches git.
- `tt cats` lists distinct categories.
- Tests cover parsing (hours/date), slugify, the fuzzy warning, append, and undo.
```
