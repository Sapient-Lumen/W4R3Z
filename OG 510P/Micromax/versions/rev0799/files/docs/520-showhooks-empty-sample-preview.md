# Rev578 — `showhooks` empty previews keep one visible hook sample

## Why

Micromax already had the right tiny state underneath plain `showhooks`:

- `hook_summary_rows(QUERY)` / `ed.hook-summary-rows` already exposed ordered
  `[name handler_count sample_handler|0 [file line col]|0]` rows for the live
  hook namespace
- query-time completion for `showhooks NAME` already reused those same summary
  rows while exact `showhook NAME` inspection reused `hook_detail_row(NAME)`
- plain `showhooks` already preferred the first non-empty hook as its sample
  when any handler was installed

But one tiny seam still lingered in the safest startup case. When every visible
hook had `0 handlers`, the no-arg command row collapsed back to bare counts and
threw away the first visible hook name Micromax already knew.

## What changed

- `_prompt_showhooks_command_row(...)` now remembers the first visible summary
  row as a fallback sample
- when no hook currently has handlers, the no-arg command row now keeps that
  first visible namespace witness instead of dropping back to counts-only
- the row stays intentionally small:
  - `7 hooks · 1 with handlers · ed.test.alpha: 1 handler (e.g. h1#cfg)`
  - `5 hooks · 0 with handlers · ed.on-action: 0 handlers`

## Why this shape

The broad hook entry point should stay calm and witnessable even in a fresh
editor with no plugin-installed handlers yet. Showing one visible hook name in
that all-empty case keeps the preview aligned with the shared summary register
Micromax already trusts after Enter, without widening the host boundary or
inventing a second hook snapshot path.

Future humans and LLMs can see that the hook namespace is not just “five vague
things exist” but exactly which visible built-in hook currently anchors the
register.

## Checks

Focused prompt-completion coverage now pins:

- populated `showhooks` command-row preview with total/non-empty/sample truth
- built-in-only `showhooks` command-row preview with the first visible empty
  hook sample preserved
