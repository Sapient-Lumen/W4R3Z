# Leading-indent cursor stepping via `tabmovement` (rev194)

Rev194 adds a tiny shared `tabmovement` option to the editor core.

## Option

- `tabmovement` (bool, default `false`)

This mirrors micro's conservative rule closely when `tabstospaces` is also on:

- `CursorLeft` / `CursorRight` treat leading runs of exactly `tabsize` spaces as one tab stop
- only the **leading indentation** participates
- the chunk must be all spaces, not mixed whitespace
- outside leading indentation, movement stays character-wise
- `SelectLeft` / `SelectRight` reuse the same stepping rule

## Why this shape

Micromax already had the important substrate:

- horizontal cursor motion lives in shared headless actions
- selections are built from those same actions
- `tabsize` / `tabstospaces` already existed as ordinary options

That makes `tabmovement` a good fit for one tiny shared movement rule instead of
another frontend-only convenience.

## Intentional limits

The first pass stays deliberately narrow:

- it does not try to reinterpret literal ``\t`` characters
- it does not change insert/delete behavior
- it does not treat mid-line spaces like indentation
- it keeps future UIs/scripts honest because they all inherit the same cursor semantics automatically
