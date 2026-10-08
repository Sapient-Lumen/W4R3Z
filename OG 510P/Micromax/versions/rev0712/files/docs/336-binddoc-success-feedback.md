# Rev394: binddoc success should stay in the typed keymap-edit dialect

The editor already had the right keymap-description loop before this revision:

- `binddoc KEY DOC...` / `bindmodedoc MODE KEY DOC...` attached human labels
- missing targets failed plainly as `...: no such binding: ...`
- nearby successful edits already reported typed feedback (`bind: ...`, `bindmode: ...`, `unbind: ...`, `unbindmode: ...`)

But successful description edits still emitted older ad-hoc lines like
`binddoc Ctrl-x: quit editor`, which were readable but slightly out of dialect with
the rest of the small keymap-surgery surface.

This revision keeps the change intentionally tiny:

- `binddoc KEY DOC...` now reports `binddoc: KEY -> DOC...`
- `bindmodedoc MODE KEY DOC...` now reports `bindmodedoc: KEY@MODE -> DOC...`
- miss behavior and description storage stay unchanged

That makes the whole bind / describe / unbind loop easier to scan in logs, tests,
and future LLM traces without changing the underlying behavior at all.
