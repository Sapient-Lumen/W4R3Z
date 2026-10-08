# Rev599: filtered runtime plugin error lines keep concrete broken-target detail

## What changed

Filtered runtime `plugin info NAME` and `plugin errors NAME` no longer flatten a
known broken target back to a bare `errors: N` header.

They now keep the same tiny failure witness Micromax already knew:

- one error: `errors: missing dependency: missingdep`
- multiple errors: `errors: 2 load errors · last: secondary issue`

Both commands still keep the trailing per-error bullet lines underneath.

## Why it matters

Micromax had already taught the exact command-bar rows, runtime `showplugin
NAME`, and runtime `plugin reload NAME` to preserve concrete plugin failure
detail. The filtered runtime info/error paths were the odd ones out: they became
vaguer after Enter than the exact rows were before Enter.

This keeps the narrow exact runtime inspectors aligned with the surrounding
plugin inspection surfaces without widening the host boundary or inventing a new
plugin model.

## Guardrails

- healthy zero-error rows still stay compact
- available-but-unloaded zero-error rows still keep the explicit state witness
- multi-error targets still list individual bullet lines after the compact
  summary line
