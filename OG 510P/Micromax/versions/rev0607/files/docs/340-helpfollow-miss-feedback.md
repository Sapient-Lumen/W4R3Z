# Rev398 — `helpfollow` miss feedback keeps the action visible

## What changed

`helpfollow` now reports its two pre-target miss paths as:

- `helpfollow: not in a docs buffer`
- `helpfollow: no link under cursor`

instead of falling back to generic `help:` wording.

## Why it matters

This is tiny, but it sits on a high-frequency docs/navigation loop. When link
following fails before Micromax resolves an internal doc target or external URL,
people and future LLMs should still be able to tell *which action* failed
without reconstructing context from the surrounding prompt state.

That keeps docs navigation aligned with nearby typed surfaces such as:

- `helplinkcopy: ...`
- `helpjump: ...`
- `help docs: no such doc: ...`
- `urlopen: ...`

## Validation

Focused tests pin both typed miss paths directly in
`tests/test_editor_help_docs_navigation.py`.
