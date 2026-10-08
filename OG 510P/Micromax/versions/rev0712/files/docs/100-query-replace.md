# Query replace (rev329)

Micromax-editor now has a tiny interactive **query replace** loop:

Micromax-editor's ordinary `replace` / `replaceall` commands now also report explicit replaced-count or `not found` feedback (rev329), but `qreplace` remains the small confirm-each path when you want to inspect each match before mutating text.

- `qreplace SEARCH VALUE [-l]`
- `queryreplace ...` (alias)

It is deliberately small and headless:

- finds the next match **from the current cursor**
- selects the current match (so the TUI can highlight it)
- asks you to confirm each replacement using a dedicated keymode

It also follows the editor's `ignorecase` option (the same setting used by `find`):
- when `ignorecase` is true, matches are case-insensitive in both literal and regex modes

During the loop, the status message includes a small progress hint like `match 3/17` when the total can be counted up front.

## Keys during query replace

| Key | Meaning |
|---|---|
| `y` / `Enter` | replace this match, go to next |
| `n` | skip this match, go to next |
| `a` | replace this and **all remaining** matches |
| `l` | replace this match and **quit** |
| `q` / `Esc` | quit |

This is intentionally reminiscent of “confirm each substitution” flows in tools
like Vim (`:s///c`) and Emacs (`M-%` / query-replace).

## Safety: capture keymode

During the loop, the editor pushes a capture keymode (`qreplace`) so **unbound
keys do not fall through to global bindings**. This prevents surprises like
triggering `Ctrl-q` (quit) or `Ctrl-s` (save) while you're answering y/n.

Implementation: `Editor.begin_query_replace()` and the `ActiveKeyMode.capture`
flag in `src/micromax_editor/editor.py`.
