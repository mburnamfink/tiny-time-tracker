# Click for the CLI, not Typer or argparse

`tt` is built on Click, matching the existing `review` tool (`/home/michael/dev/book-review-site/review-cli`).

Typer would be marginally terser (type-hint-driven), and argparse would add zero dependencies.
Both were rejected in favour of consistency: `review` is already a Click app — same Click group +
`add_command` subcommand pattern, same `src/`-layout package, same hatchling build, same
`uv tool install --editable` deployment. Sharing one mental model and one packaging recipe across
both personal CLIs is worth more than Typer's brevity or argparse's dependency-freedom for a
single-maintainer tool.
