# Rev374 — Plain key-binding miss feedback

Rev374 tightens one last small trust seam in the keymap-debugging loop.

The successful paths were already good:

- `showkey KEY` showed the resolved action, description, group, and provenance
- `binddoc` / `bindmodedoc` attached human descriptions to existing bindings
- `unbind` / `unbindmode` removed bindings cleanly

But the miss paths still collapsed to raw `(unbound)` placeholders, which hid
which command family failed and made absent-binding feedback speak a weaker
dialect than nearby plain-spoken command-bar failures.

Rev374 keeps the implementation tiny:

- `showkey KEY` now fails as `showkey: no such binding: KEY`
- `binddoc KEY DOC...` now fails as `binddoc: no such binding: KEY`
- `bindmodedoc MODE KEY DOC...` now fails as `bindmodedoc: no such binding: KEY@MODE`
- `unbind KEY` now fails as `unbind: no such binding: KEY`
- `unbindmode MODE KEY` now fails as `unbindmode: no such binding: KEY@MODE`
- the headless `:key KEY` REPL path now mirrors the same wording

This is intentionally small. The goal is not new keymap machinery; it is making
inspection and tiny keymap edits fail plainly, so humans and future LLMs do not
have to infer intent from a placeholder.
