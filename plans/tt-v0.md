# Plan: `tt` — terminal time tracker (v0)

> Source PRD: `docs/BUILD.md` (with `CONTEXT.md` glossary and `docs/adr/0001`, `0002`).

Personal, single-user, terminal-first, **write-only** time tracker. Retrospective logging
("I spent 2 hours on X") that must feel instant and work offline. v0 ships logging, undo,
and category listing — no reading/analysis. Off-machine backup is handled by keeping the store
in a Google Drive folder that syncs on its own timer, so there is no in-app sync command. Mirror
the sibling `review-cli` at `/home/michael/dev/book-review-site/review-cli` for layout, `Config`,
and `slugify`.

## Architectural decisions

Durable decisions that apply across all phases:

- **Command surface (Click)**: a `@click.group()` named `cli` in `src/tt/cli.py`; subcommands in
  `src/tt/commands/` registered flat via `cli.add_command(...)`. Commands: `log` (the default/primary
  command, invoked as `tt <hours> <category> [note...]`), `undo`, `cats`, `init`, `migrate`,
  `open`, `editor`.
- **Storage**: append-only JSONL, one entry per line, at `Config.store_path`. Key order per line is
  fixed: `day, hours, category, note, id, logged_at` (so a manual scan reads the human-meaningful
  fields first).
  ```json
  {"day":"2026-08-10","hours":2.0,"category":"book-review","note":"review of Dirty Dangerous Young","id":"<uuid4>","logged_at":"2026-08-10T14:03:11Z"}
  ```
- **Entry fields**: `day` (ISO `YYYY-MM-DD`, defaults today), `hours` (decimal float), `category`
  (kebab-case, normalised), `note` (free text, `""` if none), `id` (uuid4), `logged_at`
  (RFC 3339 UTC timestamp of when recorded).
- **Category model**: one flat namespace. The known set is **whatever normalised categories already
  exist in the JSONL** — no curated config list. Scanning the whole file on each command is fine.
- **Normalisation**: reuse the `slugify` pattern from `review-cli/src/review/slug.py` (NFKD → ASCII,
  lowercase, spaces/underscores → `-`, strip non-word, collapse repeated `-`).
- **Config**: a `Config` dataclass loading `~/.tt/config.toml` (mirror `review-cli`'s `Config`), with
  `Config.load()` / `Config.save()`. Fields: `store_path` (JSONL path; pointed at a Google Drive
  folder so the OS handles backup/sync; set via `tt init`) and `editor` (command `tt open` uses; set
  via `tt editor`, else falls back to `$VISUAL`/`$EDITOR`/platform default). Either can also be set by
  hand-editing the TOML. No command ever invokes git.
- **Path convention** (used by `tt init` and `tt migrate`): a path ending in `.jsonl` is the store
  file itself; any other path is a directory, and the store file is `<dir>/entries.jsonl`.
- **Packaging**: `src/`-layout, package + distribution name `tt`, hatchling build,
  `[project.scripts] tt = "tt.cli:cli"`, `[tool.hatch.build.targets.wheel] packages = ["src/tt"]`.
  Dep: `click>=8.0` (`rich` optional). Everything else stdlib. Tests: pytest, `pythonpath = ["src"]`.
  Python work uses the `~/work` uv venv; install packages via `uv pip install --python ~/work/bin/python`.

## Suggested module layout

```
src/tt/{__init__,cli,config,store,parsing,categories}.py
src/tt/commands/{log,undo,cats,init,migrate,open,editor}.py
tests/
```

---

## Phase 1: Log an entry, end-to-end and installed

**User stories**: log an entry (the primary command) with flexible hours and date input.

### What to build

The tracer bullet: a complete path from `tt <hours> <category> [note...]` to a correct appended
JSONL line, plus a real install so `tt` is on PATH. Stand up the package skeleton (`pyproject.toml`,
`src/tt`, `Config`, `Entry` model + JSONL append in `store.py`, `slugify` + input parsing in
`parsing.py`, the Click `cli` group, and the `log` command wired as the default). Logging normalises
the category, generates a fresh uuid4 and current UTC `logged_at`, and appends one line in the fixed
key order. Must return instantly.

Input parsing is complete in this phase:
- `hours` accepts `1.5` (decimal) **or** `1h30m` **or** `90m` — all resolve to the same decimal hours.
  No quarter-hour rounding; store what was given.
- `category` is a single positional token, normalised to kebab-case before storing.
- `note` is `nargs=-1`, greedy remainder joined with spaces; may be empty (`""`).
- `-d, --date` overrides `day`, accepting **only** a negative integer (days ago, e.g. `-2`) **or** an
  ISO 8601 date (`2026-08-09`); reject anything else. Default: today.

### Acceptance criteria

- [ ] `tt 2 book-review review of Dirty Dangerous Young` appends a correct JSONL line (fixed key order,
      valid uuid4, UTC `logged_at`) and returns instantly.
- [ ] `tt 90m admin`, `tt 1h30m admin`, and `tt 1.5 admin` all store `hours: 1.5`.
- [ ] `tt -d -1 1 cooking dinner` and `tt -d 2026-08-09 1 cooking dinner` set `day` correctly; other
      `-d` forms are rejected with an error.
- [ ] Category casing/spacing variants (`Book Review`, `BookReview`, `book_review`) all collapse to
      `book-review` on write.
- [ ] Empty note stores `""`; multi-word note is joined with spaces.
- [ ] `uv tool install --editable /home/michael/dev/time-tracking` puts a working `tt` on PATH
      (`~/.local/bin/tt`) that logs against the configured store; edits are live.
- [ ] Tests cover hours parsing (all three forms), date parsing (negative-int, ISO, rejected forms),
      slugify, and JSONL append.

---

## Phase 2: Category discovery — fuzzy warning + `tt cats`

**User stories**: warn on likely category typos without blocking; list known categories.

### What to build

A known-set scan (`categories.py`) over the JSONL — the distinct normalised categories present —
powering two behaviours:
- **Fuzzy check in the log path**: if the normalised category is not already known, run
  `difflib.get_close_matches(cat, known, n=3, cutoff=0.6)`. On a close match, print a non-blocking
  warning (e.g. `⚠ new category 'admyn' (did you mean 'admin'?) — logged anyway`), then log regardless.
  Never prompt, never block — one-shot instant logging is preserved.
- **`tt cats`**: print the distinct categories found in the JSONL, sorted (with counts as a
  nice-to-have).

### Acceptance criteria

- [ ] Logging a near-miss category prints the warning to stderr but still appends the entry.
- [ ] Logging an exactly-known category prints no warning.
- [ ] Logging a genuinely new category with no close match prints no warning and logs.
- [ ] `tt cats` lists the distinct categories, sorted; counts if included.
- [ ] Tests cover the fuzzy warning (fires on near-miss, silent on known/no-match).

---

## Phase 3: `tt undo`

**User stories**: remove the last-logged entry.

### What to build

`tt undo` reads the last line of the JSONL, prints that entry human-readably, and asks for
confirmation. On yes, rewrite the file without that last line. On no, do nothing.

### Acceptance criteria

- [ ] `tt undo` shows the last entry in human-readable form and prompts for confirmation.
- [ ] On yes, exactly the last line is removed and the rest of the file is unchanged.
- [ ] On no, the file is untouched.
- [ ] Behaves sanely on an empty/absent store (nothing to undo).
- [ ] Tests cover undo removing exactly the last line.

---

## Phase 4: `tt init` — set the storage location

**User stories**: choose where the store lives (e.g. a Google Drive folder) without hand-editing TOML.

### What to build

`tt init <path>` resolves the given path (expanding `~`), applies the path convention — ending in
`.jsonl` means the store file itself, otherwise a directory whose store file is `<dir>/entries.jsonl` —
and persists it to `~/.tt/config.toml` via `Config.save()`. Creates the store's parent directory.
Prints the resolved store path. Does **not** move or create entry data; use `tt migrate` for that.

Bare `tt init` (no path) prints the current store path and changes nothing.

### Acceptance criteria

- [ ] Bare `tt init` prints the current `store_path` and does not modify config.
- [ ] `tt init ~/notes/tt.jsonl` sets `store_path` to that file.
- [ ] `tt init ~/gdrive/.../time-tracking` (no `.jsonl`) sets `store_path` to `<dir>/entries.jsonl`.
- [ ] `~` is expanded; the store's parent directory is created.
- [ ] The resolved path is written to `~/.tt/config.toml` and echoed to the user.
- [ ] Tests cover the no-arg print, both the file-path and directory-path branches, and `~` expansion.

---

## Phase 5: `tt migrate` — relocate the store and its data

**User stories**: move the store to a new location, taking existing entries along.

### What to build

`tt migrate <path>` resolves the destination via the same path convention as `tt init`, **copies** the
current store file's contents verbatim to the destination, then sets `store_path` to the destination
via `Config.save()`. The copy is verbatim (byte-for-byte) so hand edits and formatting survive. The
original file is left in place as a backup — this is a copy, not a move. Refuses to overwrite a
destination that already exists with data, to avoid clobbering another store.

### Acceptance criteria

- [ ] `tt migrate <path>` copies all current entries to the resolved destination, byte-for-byte.
- [ ] After migrating, `store_path` in config points at the destination.
- [ ] The original store file still exists (copy, not move).
- [ ] Refuses (non-zero exit, no changes) when the destination already exists and is non-empty.
- [ ] Reasonable behaviour when the current store doesn't exist yet (nothing to copy).
- [ ] Tests cover the copy + path switch, the refuse-on-existing-destination guard, and that the
      source is preserved.

---

## Phase 6: `tt open` + `tt editor` — edit the log by hand

**User stories**: open the store in a text editor to fix or scan entries; configure which editor.

### What to build

`tt open` opens the store file in a text editor (via `click.edit(filename=..., editor=...)`),
resolving the editor as: configured `Config.editor` → `$VISUAL` → `$EDITOR` → platform default.
Ensures the store's parent directory exists and touches the file if missing so the editor opens
cleanly. `tt editor <cmd>` saves the editor to config (`Config.save()`); bare `tt editor` prints the
configured editor, or the `$VISUAL`/`$EDITOR` fallback, or an "unset" note.

### Acceptance criteria

- [ ] `tt open` launches the resolved editor on the store file, creating the file/parent dir if absent.
- [ ] `tt open` uses `Config.editor` when set, otherwise the `$VISUAL`/`$EDITOR`/default fallback.
- [ ] `tt editor <cmd>` persists the editor to `~/.tt/config.toml`.
- [ ] Bare `tt editor` prints the configured editor, the env fallback, or an unset message.
- [ ] Tests cover open launching the editor on the store (editor call captured) and editor set/print.

---

## Status & next step

The MVP is **feature-complete** — the write-and-curate surface (log with typo nudge, `undo`, `cats`,
`init`, `migrate`, `open`, `editor`) is built, installed, and tested. `tt sync` was dropped in favour
of keeping the store in a Google-Drive-synced folder.

**Next step: analytics** — the read side. The north-star output is the **Weeknote**: hours aggregated
by category over a date range (e.g. "Sixteen hours on Project Ludic. Six hours of admin."), and
eventually Paul Graham Raven-style weeknote prose. Deliberately deferred until the write side has been
lived with; the append-only JSONL with fixed keys is designed to make this straightforward to add.
This will be its own plan.
