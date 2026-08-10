# Time Tracking

A personal, single-user tool for self-insight into how working time is spent. Time is
logged in coarse increments against categories from a terminal and summarised weekly, in the
style of Paul Graham Raven's weeknotes. No billing, no other users.

## Language

**Weeknote**:
The weekly summary of hours spent per category, e.g. "Sixteen hours on Project Ludic. Six
hours of admin." The north-star output the whole tool exists to produce.
_Avoid_: report, digest, summary

**Entry**:
A single retrospectively-logged unit of time: a duration at quarter-hour fidelity attributed
to one category, plus an optional free-text note carrying the detail. Always typed by hand
after the fact — never derived from a live timer.
_Avoid_: record, log, session, event

**Category**:
The single kebab-case label an entry's time is attributed to (e.g. admin, book-review,
parenting, cooking). One flat namespace — no project-vs-activity split. The set of categories
is whatever has been logged so far — discovered organically, not chosen from a fixed
enumerated list — and expected to stay small and stable.
_Avoid_: tag, project, bucket, label

**Note**:
The optional free text on an entry that records what was actually done ("review of Dirty
Dangerous Young"). Where the detail lives and what you grep later; ignored by the Weeknote,
which aggregates by Category only.
_Avoid_: description, comment, memo
