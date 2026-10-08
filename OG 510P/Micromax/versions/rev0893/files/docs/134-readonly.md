# Buffer protection via `readonly` (rev193)

Rev193 makes the editor's existing protected-buffer behavior available through
the normal option system too.

## Option

- `readonly` (bool, default `false`)

This is intentionally small and shared-core:

- when enabled, mutating editor actions reject edits in that buffer
- `save` and capability-gated `ed.save` also refuse to write
- the status model reports the buffer as `protected` / `readonly`
- help/docs buffers still use the same local protected flag, so the existing
  internal-buffer behavior does not fork into a separate code path

## Scope

`readonly` now behaves like an ordinary option, so you can use either:

- `setlocal readonly true` for one buffer (the most natural fit)
- `set readonly true` for a broader default, with `setlocal readonly false` as a local override

That tradeoff keeps the implementation tiny: one shared effective-readonly rule
for mutating actions, saves, statusline/reporting, and script-visible hostcalls,
instead of another bespoke “protect this buffer” command surface.


## Rev777 hostcall boundary

Rev777 closes a direct-hostcall gap: `ed.set-text`, `ed.replace-range`,
`ed.delete-range`, and `ed.replace-selections` now share the same protected-buffer
edit guard as mutating actions and saves.  The guard runs before those hostcalls
consume their operation arguments, so a failed readonly call leaves useful stack
evidence for debugging while still refusing the edit.
