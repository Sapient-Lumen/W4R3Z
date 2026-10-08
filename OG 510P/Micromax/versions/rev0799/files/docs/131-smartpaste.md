# Smartpaste (rev190)

Micromax now supports a tiny shared `smartpaste` option for `Paste`.

This is inspired by micro's `smartpaste` option: when pasting multiple lines, an editor can reuse the current indentation level so an otherwise-unindented block lands somewhere sensible instead of forcing immediate manual reindent.

## What Micromax does

When `smartpaste` is enabled, `Paste` will best-effort reuse the current line's existing whitespace prefix **only** when all of the following are true:

- the pasted payload contains multiple lines
- the insertion point is still inside leading whitespace on the current line
- the pasted block still has at least one non-empty line with zero leading indentation

If those conditions hold, Micromax prefixes each non-empty continuation line with the existing whitespace prefix before inserting the text.

Example:

```text
current line before paste: "    |"
clipboard payload:         "if x:
    y
z"
result:                    "    if x:
        y
    z"
```

## What it deliberately does *not* do

This first pass is intentionally conservative:

- no language-aware reindent or formatting
- no mid-line paste rewriting inside ordinary text
- no extra indentation when the pasted block is already indented on every non-empty line
- no separate TUI-only behavior; the rule lives in the shared editor core

## Why this shape

Micromax already had the important substrate: `Paste` is a shared editor action used by the headless core, the curses TUI, internal clipboard paste, external clipboard import, and multi-cursor per-item paste. That makes `smartpaste` a good fit for one tiny shared rule rather than another frontend-specific convenience.

## Related surfaces

- `docs/56-editor-selection-clipboard.md`
- `docs/87-editor-config.md`
- `tests/test_editor_core.py`
