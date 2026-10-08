# Whitespace-only autoindent cleanup (`keepautoindent`) (rev192)

Rev192 adds a tiny shared `keepautoindent` option to the editor core.

## Option

- `keepautoindent` (bool, default `false`)

Micromax already autoindents on `InsertNewline` by reusing the current line's
leading whitespace. `keepautoindent` controls one narrow but important follow-up
case: what to do when you press Enter again on a line that only contains that
autoindent whitespace.

Current rule:

- with the default `keepautoindent=false`, if the *original* line was only spaces/tabs and `InsertNewline` autoindents the next line, the previous line is cleared back to empty
- with `set keepautoindent true`, that previous whitespace-only line is kept
- ordinary mixed-content lines keep their existing split behavior

This stays deliberately small and shared-core:

- no provenance tracking for manually typed indentation
- no save-time trimming hook
- the same behavior applies in the headless editor core and any future UI that calls `InsertNewline`
