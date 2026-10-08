## Activation-boundary contract sheet

### Purpose
Make the product say **when a change actually becomes real** before it says `saved`, `applied`, `restart if needed`, `loaded`, or `done`.

### The contract object
Each serious configuration, repair, or mode-change sentence renders these fields together:

- **Mutation locus**: runtime-only toggle, watched sidecar file, storage-folder file, config file, service manager, package manager, or unknown.
- **Activation rung**: live-now, next filesystem reread, next explicit rescan, next local process restart, next service restart, next cohort restart, successor cutover, or unknown.
- **Old-world debt**: none, pending in current runtime, pending in service runtime, pending in peer cache, pending in remembered route state, pending in successor world, or unknown.
- **Witness class**: UI reread, runtime watermark, process start witness, service-manager witness, observed behavior witness, or unknown.
- **Rollback rung**: live revert, next reread, next restart, successor re-cutover, or unknown.
- **Strongest honest sentence**: the strongest activation claim the product is currently willing to make.
- **Blocked stronger sentence**: the next stronger immediacy claim the product refuses to make.

### Default language rules
- `saved` is intentionally weaker than `active in runtime`.
- `restart recommended` is intentionally weaker than `restart is the first honest activation rung`.
- `config present on disk` is intentionally weaker than `the running process has adopted it`.
- `service restarted` is intentionally weaker than `all remembered route/cache debt is gone`.
- `hot reread` is intentionally weaker than `all peers now behave under the new rule`.

### Required persistent receipts
Any serious settings mutation, service edit, or repair action stores one durable receipt preserving mutation locus, activation rung, old-world debt, witness class, rollback rung, and the blocked stronger sentence.
