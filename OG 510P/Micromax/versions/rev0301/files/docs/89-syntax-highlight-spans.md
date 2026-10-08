# Syntax highlight spans (rev66)

Micromax-editor keeps rendering concerns out of the core. Instead of shipping a
theme or terminal colors in the headless model, the editor exposes a portable
**span model**.

## Data model

Highlight info is **per-line spans**.

A span is:

```
[start_col end_col tag]
```

- `start_col` / `end_col` are 0-based character columns (end exclusive)
- `tag` is a small string like `"comment"` or `"str"`

The current public tag vocabulary is:

- `comment`
- `str`
- `kw`
- `num`
- `def`

## Hostcalls

### `ed.highlight`

Stack effect:

```
( start count -- spans )
```

Returns `spans`, a list aligned with the requested range:

- `spans[0]` contains spans for line `start`
- `spans[1]` contains spans for line `start+1`
- ...

### `ed.highlight-tags`

Stack effect:

```
( -- tags )
```

Returns the list of known tag strings.

## Current implementation

- `src/micromax_editor/highlight.py` contains the implementation.
- Only `filetype=micromax` currently returns non-empty spans.
- The micromax highlighter is intentionally **line-local** (no multi-line
  string/comment state yet).

## Why this shape

A span model composes well:

- syntax highlighting
- pair matching / bracket highlight
- search match highlight
- trailing whitespace visualization
- diagnostics / lint underlines

…and it stays UI-independent.
