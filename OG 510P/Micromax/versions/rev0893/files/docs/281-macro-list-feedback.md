# Rev339: honest macro inventory

This is a tiny trust-first follow-up to rev338.

The editor already had real macro recording and playback, and rev338 made playback itself speak up. But the inventory path was still too vague: `macro list` only printed raw names, and because the editor always carries a default `last` slot, a fresh session could misleadingly imply that a saved macro already existed.

## What changed

- `macro list` now reports `macros: (none)` when there are no recorded steps yet
- saved macros now render as `name (N step[s])`
- the default empty `last` slot is omitted until it actually contains steps

## Why this matters

This is not about adding new macro power. It is about making tiny automation feel inspectable and boringly honest.

A trustworthy editor should not make users guess whether they have a real saved macro, an empty default slot, or two names pointing at the same recorded steps. Before future work adds richer macro inspection, editing, or persistence, the baseline inventory path should already tell the truth in one line.

## Verification

Focused coverage lives in:

- `tests/test_editor_macros_named.py`
- `tests/test_editor_core.py`

The new assertions pin down both the empty case (`macros: (none)`) and the ordinary saved case (`macros: a (1 step), last (1 step)`).
