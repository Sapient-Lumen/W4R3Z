# Rev0883 singleton/help group snapshots

Rev0883 narrows another part of runtime cleanup/retag rollback.  Clipboard,
active search, and help history no longer restore from whole-register or
whole-history snapshots during runtime-group cleanup guards.  They now capture
only state owned by the affected runtime group and restore only that state after
a failed cleanup or staged retag sweep.

## Why this matters

The cleanup guard is allowed to repair partial plugin unload/reload sweeps, but
it should not rewind unrelated user/trusted UI state merely because a later
cleanup surface failed.  Before this change, the guard snapshotted the entire
clipboard register, entire active-search register, and entire help-history
state.  That made rollback correct for plugin-owned state but too broad for
unrelated state that changed after the snapshot.

## What changed

- `RuntimeClipboardGroupSnapshot` captures the clipboard register only when its
authority matches the affected group.
- `RuntimeSearchGroupSnapshot` captures the active-search register only when its
authority matches the affected group.
- `RuntimeHelpHistoryGroupSnapshot` captures matching back/forward help-history
rows and the active help session only when their authority matches the affected
group.
- `RuntimeGroupStateSnapshot` now uses these helpers for cleanup/retag commit
guards.
- Restore removes current rows/registers for the affected groups, reinserts the
captured rows/registers with cloned authority, and leaves unrelated rows outside
the snapshot.
- `mxaudit` checks both the helper presence and the group-snapshot paths that use
them.

## Tests added

Focused regressions prove that:

- plugin-owned clipboard/search/help rows are captured, while trusted rows are
not;
- unrelated trusted clipboard/search/help state is not rewound when nothing was
captured for the target group;
- restore can reinsert captured plugin-owned singleton/help state without
rewinding unrelated trusted rows;
- a later retag failure restores clipboard, search, and help-history authorities
from the promoted group back to the staged group.

## Non-claims

This is still a rollback snapshot, not the complete typed effect journal.
Interaction state and recovery stacks still use broader group snapshots.
Generation-scoped cleanup still uses `RuntimeGenerationStateSnapshot` for macros,
clipboard, search, help history, recovery, and related delayed state.  Broad
plugin source/lifecycle/callback transactions still retain
`RuntimeRegistrationSnapshot`.  This revision does not add hostile-code
containment, process/Wasm isolation, durable cleanup logs, CI, dependency locks,
hosted provenance, or a complete aggregate test manifest.
