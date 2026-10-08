# Rev0882 delayed-state group snapshots

Rev0882 moves four delayed-state sidecars inside `RuntimeGroupStateSnapshot` from
full-surface rollback to touched-row rollback:

- recent-file MRU rows;
- command-palette MRU rows;
- prompt-history rows;
- saved-cursor rows.

These stores are durable or replayable UI state.  A plugin-created row can
outlive a failed unload/reload cleanup sweep and later reopen a path, suggest a
command, replay prompt text, or restore a cursor.  Earlier revisions removed the
rows on cleanup, but the cleanup commit guard still snapshotted the whole
sidecar.  A failed later cleanup surface could therefore restore unrelated user
or trusted rows to an older shape.

Rev0882 adds typed row snapshots for the affected sidecars:

- `RuntimeRecentFilesGroupSnapshot`;
- `RuntimePaletteRecentGroupSnapshot`;
- `RuntimePromptHistoryGroupSnapshot`;
- `RuntimeSavedCursorGroupSnapshot`.

Each helper captures only rows whose authority belongs to the affected cleanup or
retag group.  Restore removes current rows for those groups and reinserts the
captured rows with cloned authority.  Rows outside the affected groups are not
stored in the snapshot and are not restored if they changed after the snapshot.

This keeps the rev0875 fail-closed behavior and the rev0876 narrow group-sweep
boundary, while reducing the amount of durable UI state copied for every cleanup
or retag commit guard.

## What this guarantees

- Failed cleanup/retag still restores plugin-owned recent, palette, prompt, and
  saved-cursor rows that were already pruned or retagged before a later surface
  failed.
- Unrelated rows outside the affected runtime groups are not copied into these
  delayed-state snapshots.
- Restore of these four sidecars no longer rewinds unrelated trusted/user rows.
- `mxaudit` checks that the delayed row snapshot helpers exist and are wired into
  `RuntimeGroupStateSnapshot` capture/restore.

## What this does not claim

- Generation-scoped cleanup still uses the broader `RuntimeGenerationStateSnapshot`.
- Clipboard, active search, help history, recovery stacks, and interaction state
  are not migrated by this revision.
- These helpers are rollback snapshots, not the full typed effect journal.
- They do not contain document edits, buffers, saves, URL/shell effects, external
  clipboard exports, blocking calls, memory exhaustion, native code, or process
  compromise.
- Cleanup diagnostics remain session-retained and bounded, not durable signed
  provenance.
