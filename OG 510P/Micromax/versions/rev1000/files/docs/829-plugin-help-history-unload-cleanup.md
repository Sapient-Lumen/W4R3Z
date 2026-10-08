# Rev0871: plugin help-history unload cleanup

Rev0871 continues the unload/recovery audit by treating local help-history state
as delayed navigation state.  Help history is not executable command text, but it
is replayable UI state: `helpback`, `helpforward`, and `helpresume` can carry a
plugin-authored docs target forward after the plugin has been unloaded or after a
staged reload has replaced the plugin generation.

Before this revision, help back/forward stacks and the dormant session-help target
were authority-stamped, but plugin lifecycle cleanup did not remove or retag
those rows.  A plugin could therefore leave stale help navigation behind after
`plugin unload NAME`, and staged reload could temporarily prune old session
history in a way that laundered the still-visible active help buffer into ambient
trusted history.

## Change

- `Editor.remove_help_history_group(group)` removes back-stack, forward-stack,
  and dormant session-help rows owned by one runtime group.
- `Editor.retag_help_history_group(old, new)` promotes staged reload help-history
  authority from `plugin:NAME#reloadN` to the stable `plugin:NAME` group.
- `Editor.remove_plugin_help_history_generation(root, generation)` prunes rows
  owned by one committed plugin generation before staged reload evaluation.
- Plugin transaction snapshots now include help-history stacks, stack authority,
  the session-help entry, and session authority, so failed load/reload/deinit and
  failed plugin callbacks restore the prior help trail.
- `Editor._help_current_authority()` now falls back to the active help buffer's
  authority when a session row has been intentionally pruned but the help buffer
  is still visible.  That prevents reload staging from laundering an old
  plugin-opened help page into trusted history.

## Boundary

This is a lifecycle cleanup for session-local navigation state, not a new
permission registry.  Unload does not close a visible help buffer and does not
pretend that built-in docs are secret; it only removes plugin-owned deferred
navigation rows so later `helpback`, `helpforward`, or `helpresume` actions do
not replay stale plugin-owned UI state.

Trusted/user help history remains outside unrelated plugin cleanup.

## Tests

Focused tests cover:

- plugin unload removes plugin-owned help back/forward/session history;
- plugin unload does not remove trusted/user help history;
- successful staged reload retags replacement help-history authority to the
  stable plugin group so a later unload removes it;
- failed staged reload restores the old help-history stacks and session entry;
- active help-buffer authority is used during reload pre-pruning so old
  plugin-owned docs targets are not silently converted into trusted history.
