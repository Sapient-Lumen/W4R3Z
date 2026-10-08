# Rev560 — `showhooks` command-bar preview reuses live hook summary

## Why

Micromax already had the right tiny state underneath plain `showhooks`:

- the command itself already printed a count-aware live hook summary after Enter
- `hook_summary_rows(QUERY)` / `ed.hook-summary-rows` already exposed that same
  summary register headlessly
- `showhooks NAME` prompt completion already reused those tiny rows while exact
  `showhook NAME` inspection already reused one-hook detail

But the exact no-arg command row still fell back to generic command metadata.
That meant the broadest live-hook inspection entry point stayed less honest than
its nearby query-time and exact-hook siblings.

## What changed

- added `_prompt_showhooks_command_row(...)`
- exact command completion for plain `showhooks` now reuses
  `hook_summary_rows("")`
- the row stays intentionally small:
  - `7 hooks · 1 with handlers · ed.test.alpha: 1 handler (e.g. h1#cfg)`
  - `5 hooks · 0 with handlers`

## Why this shape

Micromax always has a small live hook namespace, so a naive first-row preview can
waste the sample on an empty internal hook. This landing keeps the summary more
useful by always surfacing the total hook count, explicitly counting how many
hooks currently have handlers, and only sampling the first non-empty hook when
one exists.

That keeps the command bar aligned with Micromax's existing headless-first
summary register instead of inventing one more bespoke hook snapshot path.
Future humans and LLMs can see the same live hook-namespace truth before Enter
that the command and hostcall already trust after Enter.

## Checks

Focused prompt-completion coverage now pins:

- populated `showhooks` command-row preview with total/non-empty/sample truth
- built-in-only `showhooks` command-row preview when no handlers are installed
