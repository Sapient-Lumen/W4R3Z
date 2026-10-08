# `showcmd` / `showword` miss feedback

`showcmd NAME` and `showword NAME` are first-stop inspection commands for this archive.
They already had the right successful paths:

- `showcmd NAME` exposed command docs plus optional registration-group / provenance detail
- `showword NAME` exposed visible Micromax kind/effect/doc/provenance detail from the current search order

But one tiny trust seam still lingered on lookup failure. A missing command or word fell back to a raw placeholder string:

- `name: (unknown command)`
- `name: (unknown word)`

That was technically accurate, but it hid the command family that failed and spoke a weaker dialect than nearby plain-spoken failures like `plugin reload: no such plugin: NAME` or `prevbuf: no previous buffer`.

## What changed

Missing lookups now fail plainly as:

- `showcmd: no such command: NAME`
- `showword: no such word: NAME`

The success paths stay unchanged.

## Why this matters

These commands are a common first move for humans and future LLMs exploring the repo:

- `showcmd` is the obvious way to inspect command-bar behavior and plugin-registered commands
- `showword` is the obvious bridge into live Micromax dictionary metadata

When a lookup misses, the message should still say exactly what family of thing was being inspected. Small inspection failures are part of the product's trust surface too.

## Validation

Focused coverage now pins down both miss cases alongside the existing success paths:

- `tests/test_editor_registration_groups.py`
- `tests/test_editor_mx_commands_and_completion.py`

## Related

- rev34: grouped command/key registration provenance
- rev47: `showword` dictionary inspection
- rev369: count-aware hook inspection
- rev372: plain `prevbuf` empty feedback
