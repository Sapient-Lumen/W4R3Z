# Rev652: macro unknown-subcommand completion stays visible

## Why

Runtime `macro nope` was already honest: Micromax said `macro: no such subcommand: nope`.
But before Enter, typed `macro nope` could still disappear from completion entirely,
or collapse back to a generic `macro action` row if the typed token was forced
through exact-row plumbing. That made a typo harder to inspect exactly where the
command bar is supposed to help the user decide whether Enter is safe.

## What changed

- `_prompt_macro_command_row(...)` now treats unknown subcommands as explicit
  misses and returns:
  - menu: `missing subcommand`
  - info: `no such subcommand: NAME`
- `_prompt_command_token_candidates(...)` now preserves a typed unknown
  `macro NAME` token as an exact fallback candidate when no real subcommand
  matches.
- prompt-complete still behaves normally with a lone exact candidate: selecting
  the miss inserts `macro nope `, but the row helper and candidate plumbing keep
  the miss visible and reviewable.

## Why this is the right size

This is a tiny trust-first cleanup, not a new macro feature. It does not add new
subcommands, alter runtime semantics, or widen the command language. It simply
keeps the pre-Enter command surface as explicit as the post-Enter error path.

## Tests

Focused prompt tests cover:

- exact unknown-subcommand row text
- exact-candidate fallback for `macro NAME`
- end-to-end `prompt_complete()` insertion for a lone unknown macro subcommand
