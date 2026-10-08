# Rev0884 recovery/interaction group snapshots

Rev0884 narrows the last broad runtime-group cleanup snapshots called out in
rev0883. Selection/jump recovery stacks and delayed interaction state no longer
piggyback on full all-buffer cursor snapshots or whole prompt/capture snapshots
inside cleanup/retag commit guards. They now capture only rows owned by the
affected runtime group and restore only those rows after a failed cleanup or
staged retag sweep.

## Why this matters

Plugin cleanup can fail after earlier surfaces have already removed or retagged
state. The commit guard must put plugin-owned state back, but it should not also
rewind unrelated recovery registers, prompts, trusted keymodes, pending URL
confirmations, or ordinary cursor state. Before this change, recovery cleanup
used the all-buffer cursor snapshot and interaction cleanup used the broad
callback prompt snapshot. Those were correct but wasteful and had a larger blast
radius than the cleanup operation itself.

Rev0884 also fixes a concrete interaction cleanup edge: removing a plugin-owned
query-replace or open-url interaction no longer deletes trusted active keymodes
merely because they share the internal names `qreplace` or `openurl`. Cleanup
now filters those keymodes by both name and runtime group.

## What changed

- `RuntimeRecoveryGroupSnapshot` captures only selection-stack and jumplist rows
  whose authority matches the affected cleanup/retag group.
- `RuntimeInteractionGroupSnapshot` captures only matching active keymodes,
  prompt state, query-replace state, pending open-URL state, and the one active
  buffer cursor/selection state needed to repair query-replace cleanup.
- `RuntimeGroupStateSnapshot` now uses the recovery and interaction group
  helpers instead of `capture_cursor_state(ed)` and
  `snapshot_editor_interaction_state(ed)`.
- Restore removes current rows for the affected group, reinserts captured rows
  at their prior indices with cloned authority, and leaves unrelated rows
  outside the snapshot.
- `remove_interaction_group()` now preserves trusted `qreplace` and `openurl`
  keymodes when removing plugin-owned interactions.
- `mxaudit` checks helper presence, runtime-group wiring, and the absence of the
  broad cursor/interaction snapshot calls in the group cleanup snapshot path.

## Tests added

Focused regressions prove that:

- plugin-owned recovery-stack rows are captured while trusted rows are not;
- recovery restore reinserts plugin-owned selection/jump rows without rewinding
  unrelated trusted rows;
- plugin-owned prompt/query/open-URL/keymode interaction state is captured while
  unrelated trusted interaction state is skipped;
- unrelated trusted interaction state is not rewound when nothing was captured
  for the target group;
- removing plugin-owned query-replace/open-URL interactions does not drop trusted
  active keymodes with the same internal names;
- a later retag failure restores recovery and interaction authorities from the
  promoted group back to the staged group.

## Non-claims

This is still a rollback snapshot, not the complete typed effect journal.
Generation-scoped cleanup still uses `RuntimeGenerationStateSnapshot` for macros,
clipboard, search, help history, recovery, and related delayed state. Broad
plugin source/lifecycle/callback transactions still retain
`RuntimeRegistrationSnapshot`. This revision does not add hostile-code
containment, process/Wasm isolation, durable cleanup logs, CI, dependency locks,
hosted provenance, or a complete aggregate test manifest.
