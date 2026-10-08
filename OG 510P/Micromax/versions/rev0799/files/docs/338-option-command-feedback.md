# Rev396 — typed feedback for option-edit commands

## What changed

The tiny option-edit commands in the editor command bar now report typed,
self-identifying success messages instead of bare value lines:

- `set OPTION VALUE` → `set: OPTION=VALUE`
- `setlocal OPTION VALUE` → `setlocal: OPTION(local)=VALUE`
- `toggle OPTION` → `toggle: OPTION=VALUE`
- `togglelocal OPTION` → `togglelocal: OPTION(local)=VALUE`

Examples:

- `set hlsearch on` → `set: hlsearch=True`
- `toggle hlsearch` → `toggle: hlsearch=False`
- `setlocal readonly true` → `setlocal: readonly(local)=True`
- `togglelocal readonly` → `togglelocal: readonly(local)=False`

## Why

Micromax already treats options as a small shared headless-first control surface:
`set`, `setlocal`, `toggle`, `togglelocal`, command completion, Micromax
hostcalls, and capability refresh all go through the same option registry.

But successful edits still fell back to bare `name=value` lines. That was
readable in the moment, yet weak in logs, tests, and future LLM traces because
it hid whether the change came from `set`, `toggle`, or a local variant.

This pass keeps the implementation deliberately tiny while making configuration
edits easier to attribute and search.

## Scope

Small wording-only follow-up:

- no option semantics changed
- no new options were added
- capability refresh behavior stays the same
- `show` output stays unchanged

## Validation

Focused coverage lives in:

- `tests/test_editor_core.py`
- `tests/test_editor_main_cli.py`
- `tests/test_mxcontext.py`
- `tests/test_mkrevzip.py`
