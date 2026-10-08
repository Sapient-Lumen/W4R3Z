# Headless REPL unknown-command feedback (rev381)

Rev380 made ordinary editor command-bar typos fail plainly as
`command: no such command: NAME`, but the tiny headless REPL still had one
older seam: an unrecognized top-level REPL line only printed `unknown command`.

That was understandable, but weaker than the editor-side dialect because it hid
what the user actually typed and did not say which surface rejected it.

## What changed

The headless REPL now reports:

- `repl: no such command: LINE`

Examples:

- `:bogus` -> `repl: no such command: :bogus`
- `bogus` -> `repl: no such command: bogus`

## Why this matters

Micromax is intentionally headless-first. The small REPL in
`python -m micromax_editor` is not the final UX, but it is part of the archive's
validation/debugging surface for humans and future LLMs. When a top-level REPL
command misses, the failure should still:

- keep the surface visible (`repl`)
- preserve the exact rejected input
- match the project's newer plain-spoken miss dialect

This is deliberately tiny. The REPL command set does not change; only the miss
feedback becomes more explicit.
