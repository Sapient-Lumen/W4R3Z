# Option inventory rows

Micromax already had the important tiny option loop before rev424: one explicit option registry, typed `set` / `setlocal` / `toggle` / `togglelocal` feedback, prompt-completion metadata that knew option kinds/defaults, and plain `show` for direct human inspection.

The remaining seam was not option storage; it was **host-boundary symmetry** and one small honesty gap.
Humans could inspect effective option state through `show`, but that surface was still assembled ad hoc and hid whether the current buffer was seeing a local override. Scripts and future UIs had to rediscover the same register by iterating option specs and calling `ed.opt-get` one name at a time.

Rev424 adds one deliberately small shared inventory surface instead of a bigger config subsystem:

- `option_inventory_rows()` returns ordered canonical rows inside the editor
- `ed.option-inventory-rows` exposes the same rows to Micromax scripts and future UIs
- plain `show` now reuses that same row surface so command output and host data stay aligned

The rows stay intentionally tiny:

- `name` — canonical option name
- `value` — effective current value text for the active buffer context
- `default` — canonical default value text
- `kind` — tiny type label (`bool`, `int`, `str`, or `enum[...]`)
- `local_override` — `1` when the active buffer is currently overriding the global value

Plain `show` also now marks those local overrides explicitly as `(local)` instead of making humans infer that scope split from surrounding state.

This deliberately complements the lower-level `ed.opt-get` / `ed.opt-set` / `ed.opt-set-local` path instead of replacing it.
The design goal is simple: if current option state already matters to humans and scripts, it should live behind one tiny honest register.
