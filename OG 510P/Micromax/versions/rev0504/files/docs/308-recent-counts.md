# Rev366 — plain `recent` inventory starts count-aware too

The plain `recent` command already became more honest in rev345: it stopped flattening MRU state to raw numbered paths and started showing active/open state, visible `dirty` / `readonly` flags, and the current cursor target for still-open entries.

One tiny structural mismatch still lingered. Empty recent-file inventory still fell back to `recent: (none)`, while non-empty inventory jumped straight into numbered entries without telling you the MRU count up front. That meant the same command quietly changed dialect exactly when the visible answer dropped to zero, and it also forced manual counting when the list was non-empty.

Rev366 keeps the change deliberately small:

- `recent` now says `recent: 0 recent file(s)` when the MRU is empty
- non-empty inventory now starts with `recent: N recent file(s), ...`
- the existing per-entry open/active/dirty/readonly/cursor detail stays intact
- the existing `... (+N more)` suffix still works the same way when the MRU exceeds the on-screen limit

This is a tiny trust/flow change, but it matters. MRU inspection should stay structurally glanceable at zero, one, or many instead of switching dialects at the empty edge.
