# `tt` — a tiny time tracker

`tt` is a simple, terminal-first time tracker for personal self-insight — how your working
time actually gets spent. You log time **retrospectively** ("I spent 2 hours on X"), in one
short command, and it appends a line to a plain-text file.

**Everything is local.** No accounts, no server, no cloud API, no live timer. Your data is a
single append-only [JSONL](https://jsonlines.org/) file you fully own and can read or edit in
any editor. Backup/sync is your call — see the `tt init` note about Google Drive below.

```
$ tt 2 book-review review of Dirty Dangerous Young
$ tt 90m admin
$ tt -d -1 1 cooking dinner        # -d -1 = yesterday
```

Each entry records the day, decimal hours, a category, an optional free-text note, plus a
uuid and a UTC timestamp of when it was logged:

```json
{"day":"2026-08-10","hours":2.0,"category":"book-review","note":"review of Dirty Dangerous Young","id":"…","logged_at":"2026-08-10T14:03:11Z"}
```

## Install

`tt` installs with [uv](https://docs.astral.sh/uv/).

**1. If you don't have `uv`** (macOS/Linux):

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

(Restart your shell afterwards so `uv` is on `PATH`. On Windows, see
[On macOS and Windows](#on-macos-and-windows) below.)

**2. Install `tt`** from a clone of this repo — run this from the repo root:

```sh
uv tool install --editable .
```

This puts a `tt` executable on your `PATH` (at `~/.local/bin/tt` on macOS/Linux). `--editable`
means edits to the source are picked up live, with no reinstall.

**3. Choose where your data lives** with `tt init`:

```sh
tt init "~/gdrive/Life Management/time-tracking"
```

If the path ends in `.jsonl` it's treated as the store file; otherwise it's a directory and the
store becomes `<dir>/entries.jsonl`. Run `tt init` with no argument to print the current path.

> I keep my store in a **Google Drive** folder. That's all "backup/sync" means here — Drive syncs
> the file on its own timer, so the same append-only log is safe off-machine and available on any
> computer where the folder is mounted. `tt` itself never touches the network.

Already have data somewhere and want to move it? `tt migrate <path>` copies the current store to
the new location (verbatim, leaving the original as a backup) and switches to it.

### On macOS and Windows

`tt` is pure Python and runs the same on all three platforms — `uv` even fetches the right Python
for you. Only three things differ:

- **Installing `uv` on Windows** (PowerShell):

  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

  macOS is the same as Linux (`curl … | sh`, or `brew install uv`).

- **Getting `tt` on `PATH`.** `uv tool install --editable .` is identical everywhere, but the
  executable lands in a platform-specific spot (`~/.local/bin/tt` on macOS/Linux; a `tt.exe` under
  uv's tools dir on Windows). If your shell can't find `tt` afterwards, run `uv tool update-shell`
  and reopen the terminal.

- **Where Google Drive lives**, for `tt init`:
  - macOS: `~/Library/CloudStorage/GoogleDrive-<account>/My Drive/…` (or a `~/Google Drive` alias)
  - Windows: a drive letter, e.g. `tt init "G:\My Drive\time-tracking"`

The store file itself is portable JSONL; on Windows it's written with `\r\n` line endings, which
`tt` reads back transparently.

## Commands

| Command | What it does |
| --- | --- |
| `tt <hours> <category> [note…]` | Log an entry (the default command). |
| `tt undo` | Show the last entry and, on confirmation, remove it. |
| `tt cats` | List the categories you've used, with counts. |
| `tt init [path]` | Print the store path, or set it. |
| `tt migrate <path>` | Copy the store to a new location and switch to it. |

**Hours** accept decimals or `h`/`m` forms — `1.5`, `1h30m`, and `90m` all mean the same thing.
Nothing is rounded; whatever you type is stored.

**`-d/--date`** overrides the day. Use a negative integer for days-ago (`-d -2`) or an ISO date
(`-d 2026-08-09`). Anything else is rejected. The default is today.

## How categories work

A **category** is a single kebab-case label an entry's time is attributed to (`admin`,
`book-review`, `cooking`, `parenting`). It's one flat namespace — no projects-vs-activities
split, and no hierarchy.

- **You don't configure a list.** The set of known categories is simply whatever you've logged so
  far — the vocabulary grows organically as you use the tool. `tt cats` shows you what exists.
- **Labels are normalised** before they're stored, so casing and separators don't fragment a
  category: `Book Review`, `book_review`, and `book review` all collapse to `book-review`.
  (One caveat: normalisation can't split runs-together words — `BookReview` becomes `bookreview`,
  not `book-review`. Put a space, dash, or underscore between words.)
- **Typos are cheap to fix.** If you fat-finger a category you can `tt undo` the entry, or just
  edit the JSONL file directly.

Categories are meant to stay small and stable — a handful of buckets you actually think in, not
a sprawling tag cloud. The notes are where the detail lives.
