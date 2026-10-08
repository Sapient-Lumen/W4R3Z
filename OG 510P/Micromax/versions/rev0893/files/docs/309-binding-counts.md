# Binding inventory counts (rev367)

The keymap discovery surface was already honest about *which* bindings were
reachable, but it still had one small structural wobble:

- empty `showbindings` / `whichkey` collapsed to `(none)`
- non-empty results jumped straight into binding rows
- users and future LLMs had to count rows by hand to infer size

Rev367 keeps the change tiny and local:

- `showbindings` now starts with `bindings active: N binding(s)` or
  `bindings MODE: N binding(s)`
- `whichkey` now starts with `whichkey: N binding(s)`
- existing binding row detail, one-shot `!` cues, and human descriptions stay
  exactly where they were after the new prefix

This is a trust/flow polish pass rather than a feature expansion. The point is
that keymap discovery should keep one inspectable dialect whether there are no
reachable bindings yet, one binding, or several.
