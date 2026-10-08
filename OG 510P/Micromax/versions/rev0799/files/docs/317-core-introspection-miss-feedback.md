# Core introspection miss feedback (rev375)

## What changed

Micromax core introspection now fails plainly when a requested word is absent:

- `help foo` -> `help: no such word: foo`
- `see foo` -> `see: no such word: foo`
- `where foo` -> `where: no such word: foo`

Instead of older placeholder lines like `foo: (unknown)` or `foo: (not found)`, the miss now keeps the command family visible.

## Why it matters

This is tiny, but it improves the exact loop humans and future LLMs use when they are feeling around inside the VM from the REPL or from embedded scripting:

- the failing tool is obvious from the first word of the message
- VM-side introspection now matches the editor's recent plain-spoken inspection cleanup
- the miss reads like an action failure, not like a mysterious formatted placeholder

## Scope

This change is deliberately narrow:

- successful `help`, `see`, and `where` output stays unchanged
- only the missing-word paths change
- focused regression coverage lives in `tests/test_features.py`
