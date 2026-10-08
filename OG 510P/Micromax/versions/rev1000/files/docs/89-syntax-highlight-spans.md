# Syntax highlight spans (rev0967)

Micromax keeps tokenization separate from renderer attributes. The editor owns a
portable span model; the compact screen contract and reference TUI consume a
bounded visible projection of that same model. No terminal colors or theme
registry live in the tokenizer.

## Data model

Full-line highlight information is a list of half-open character spans:

```text
[start_col end_col tag]
```

Columns are zero-based Python-character coordinates. The current tag vocabulary
is `comment`, `str`, `kw`, `num`, and `def`. Only
`filetype=micromax` currently returns non-empty spans, and tokenization remains
line-local.

## Hostcalls

`ed.highlight` has stack effect `( start count -- spans )` and returns one span
list per requested logical line. `ed.highlight-tags` has stack effect
`( -- tags )` and returns the known tag strings. These full-line script surfaces
retain their existing semantics.

## Visible consumers

For an ordinary screen snapshot, `editor.py` scans each visible Micromax logical
line once from column zero through the furthest visible source column, capped at
4096 characters. `project_highlight_spans()` clips the result into the same
fragment-local coordinates used by search, diagnostics, and selection. Text
beyond the cap remains plain, and `syntax_truncated_rows` reports the loss.

The internal viewport model exposes `[start, end, tag]` rows.
`micromax.screen.v1` projects them to compatible cue-token values such as
`syntax-kw` and `syntax-comment`; the curses renderer maps the stable tags to a
restrained attribute fallback and optional existing color pairs.

## Boundaries

- Coordinates are Python code points, not terminal cells or grapheme clusters.
- Multiline lexical state, embedded languages, incremental parsing, and a public
  theme API are deliberately absent.
- Unknown or malformed projected tags are ignored rather than becoming renderer
  input.

The current end-to-end landing and precedence are documented in
`docs/923-visible-selection-syntax-hierarchy.md`.
