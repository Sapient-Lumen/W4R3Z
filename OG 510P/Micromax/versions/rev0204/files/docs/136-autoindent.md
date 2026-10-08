# Shared newline indentation toggle (`autoindent`) (rev195)

Rev195 turns Micromax's existing copy-indent-on-newline behavior into a real
shared editor option: `autoindent`.

## Option

- `autoindent` (bool, default `true`)

## Behavior

When `autoindent` is enabled, `InsertNewline` reuses the current line's leading
whitespace on the newly inserted line. This stays the same conservative rule
Micromax already used before rev195:

- splitting at end-of-line copies the line's leading spaces/tabs
- splitting inside the indent prefix only keeps the prefix up to the split point
- the behavior lives in the shared headless editor core, so REPL, TUI, command-driven, and scripted paths stay aligned

When `autoindent` is disabled, `InsertNewline` inserts a plain newline without
copying indentation.

## Relationship to `keepautoindent`

`keepautoindent` only matters when `autoindent` actually added indentation for
you. If `autoindent` is off, pressing Enter on a whitespace-only line leaves the
existing whitespace in place and creates an empty next line.

## Tests

- `tests/test_editor_autoindent_tabs.py`
