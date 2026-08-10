# Local-first append-only JSONL store, synced via git

Entries are stored as an append-only JSONL file kept in a git-synced folder, rather than
written to a Google Sheet via its API.

The primary path — typing `tt` in a terminal — must feel instant and work offline. A per-entry
Sheets API round-trip (1–3s, OAuth refresh, rate limits, online-only) fights that directly.
JSONL is grep/jq/pandas-friendly, trivially extensible (add a field and old rows still parse),
and portable across any implementation language. Multi-device access is handled by folder sync
(git to begin with); a thin personal web API for occasional phone entry is deferred as a future
project. A Google Sheet, if used at all, is only an optional export/view target, never the
source of truth.

## Consequences

- Concurrent edits from two devices can produce git merge conflicts on the JSONL file;
  append-only structure keeps them trivial to resolve.
- Phone entry is deliberately clunky (edit the synced file) until the web API exists.
