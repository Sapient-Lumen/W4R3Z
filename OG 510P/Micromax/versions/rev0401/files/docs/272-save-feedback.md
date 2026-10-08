# Save feedback

Rev330 is a small trust-first follow-up.

The editor's save path was already careful internally:

- readonly/protected buffers fail honestly
- `rmtrailingws`, `eofnewline`, and `mkparents` already stayed in the shared save path
- save-time cleanup remained undoable instead of being hidden in a renderer hook
- fileformat and encoding stayed buffer-local and explicit

But the success message still just said `saved`.

That was too vague for the current product direction. A trustworthy editor should make writes feel boring, and part of that is saying what actually happened.

## What rev330 changes

Successful `save` / `saveas` now report:

- the target path that was written
- any save-time normalization steps that also changed the live buffer

Examples:

- `saved: /tmp/note.txt`
- `saved: /tmp/note.txt (normalized: trim trailing whitespace, add eof newline)`

## Why this matters

This is not flashy, but it is exactly the kind of tiny trust win the repo says to prioritize first:

- users do not have to infer which file was written
- save-time cleanup stops being an invisible side effect
- future frontends/scripts can keep the same honest save summary instead of inventing their own vague success copy

The change deliberately stays small. It does **not** add a save dialog, backup system, or richer file-operation UI. It simply makes an existing honest save path speak more clearly.
