# Bind success feedback

Rev386 closes one tiny wording seam in the keymap-edit loop.

The editor already had explicit miss feedback for `showkey`, `binddoc`, `bindmodedoc`,
`unbind`, and `unbindmode`, and rev385 made successful removals typed too. But the
creation side of the same loop still used older bare success lines like:

- `bound Ctrl-h -> command:help`
- `bound Ctrl-g -> command:showkeymodes [mode nav]`
- `bound prefix z -> nav`
- `bound prefix z@nav -> tools`

Those lines were readable, but they hid the command family and made logs harder to scan
when a session mixed `bind`, `bindmode`, `binddoc`, `bindprefix`, and `unbind`.

Rev386 keeps the change deliberately small:

- `bind KEY ACTIONSPEC` -> `bind: KEY -> ACTIONSPEC`
- `bindmode MODE KEY ACTIONSPEC` -> `bindmode: KEY@MODE -> ACTIONSPEC`
- `bindprefix KEY MODE [DOC...]` -> `bindprefix: KEY -> MODE`
- `bindmodeprefix OWNERMODE KEY MODE [DOC...]` -> `bindmodeprefix: KEY@OWNERMODE -> MODE`

The intent is simple: keymap creation should speak as plainly as keymap removal, so
message logs, tests, and future LLM traces can follow small editing loops without
reconstructing which command produced each success line.
