# Macro root alias syntax

Rev655 closes one small trust/taste seam in the macro surface.

Micromax already accepted the short macro aliases at runtime and in completion:

- `record`, `rec`, `start`
- `stop`, `end`
- `cancel`, `abort`
- `play`, `run`
- `list`, `ls`
- `status`, `st`

But the umbrella entry point itself still understated that surface. Plain `macro` kept a canonical-only command doc row and a canonical-only no-arg usage hint, so the very first line a human or future LLM saw was slightly less truthful than the accepted syntax underneath it.

The rev655 fix stays deliberately small:

- `_MACRO_ROOT_DOC` centralizes the alias-aware command-bar/root-doc string
- `_MACRO_ROOT_USAGE` centralizes the alias-aware runtime usage hint
- plain `macro` command metadata and raw no-arg `macro` now reuse those same shared strings

The result is calmer and easier to trust:

- one shared root contract instead of slightly drifting copies
- the command bar now names the same macro alias surface the dispatcher really accepts
- raw `macro` no longer teaches a narrower syntax than the subcommands below it
