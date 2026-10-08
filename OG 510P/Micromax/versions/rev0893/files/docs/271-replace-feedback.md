# Honest replace feedback (rev329)

Before rev329, ordinary `replace` / `replaceall` already worked, but they were too quiet for a trust-first editor.

A successful replace could change text without saying how much changed, and a no-op run could simply return `False` with no user-facing explanation. That is technically workable, but it is not the kind of behavior that makes an editor feel boringly honest.

## What changed

Rev329 keeps the surface intentionally small:

- `replace` now reports `replace: replaced N occurrence(s) from cursor` on success.
- `replaceall` now reports `replaceall: replaced N occurrence(s)` on success.
- both commands now report `...: not found` instead of failing silently when nothing matches.

The commands still behave the same semantically: they mutate text in the same cases, keep the same literal/regex rules, still honor `ignorecase`, and still record one undo entry for the edit.

Rev457 tightens one small adjacent trust seam in that same loop: `replaceall`
now preserves its own command identity on read-only / invalid-regex failures,
and undo/redo after bulk replace now report `replaceall` instead of collapsing
back to generic `replace`.

Rev720 tightens the command-line boundary around that same replace family:
unknown trailing flags now fail with `replace: unknown flag: ...`,
`replaceall: unknown flag: ...`, or `qreplace: unknown flag: ...` before any
buffer mutation or capture prompt begins.

## Why this matters

This is not the final search/replace UX. The repo still wants fuller preview and diff-style confidence for bulk edits. But explicit post-action feedback is still a meaningful trust improvement:

- it tells the user whether anything happened
- it tells the user roughly how much happened
- it keeps command-bar editing from feeling silent or ambiguous
- it makes future TUIs, scripts, and LLM-driven workflows easier to reason about because the default interaction already reports the outcome in plain language

In other words: before we build richer replace previews, the editor should at least tell the truth clearly after a text-changing command runs.
