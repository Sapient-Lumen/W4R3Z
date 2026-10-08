# Rev0865 — plugin recovery stacks unload cleanup

Rev0864 cleaned plugin-owned saved macros, but another delayed-state surface still survived unload: selection-recovery stack rows and jumplist rows.  These rows are not executable, but they are durable navigation/recovery state.  A plugin could push them during load or a deferred callback, then `plugin unload NAME` would remove commands, keys, timers, hooks, prompts, and macros while leaving plugin-authored recovery rows in the current buffer.

Rev0865 gives those recovery rows the same lifecycle treatment as the other delayed plugin surfaces:

- `plugin unload NAME` removes selection-stack and jumplist rows whose authority group is `plugin:NAME`;
- staged reload retags selection/jump rows from the temporary staging group back to `plugin:NAME`;
- generation cleanup removes old plugin recovery rows before staged reload evaluation, so a replacement can recreate the same cursor snapshot instead of being suppressed by jumplist deduplication;
- failed staged reload restores the old recovery rows from the plugin transaction snapshot;
- trusted/user and mixed-origin recovery rows remain outside plugin-generation cleanup and continue to use the existing authority checks.

The narrow code seams are `Editor.remove_recovery_group()`, `Editor.retag_recovery_group()`, and `Editor.remove_plugin_recovery_generation()`.  The plugin manager still delegates cleanup through `cleanup_runtime_group()` and `PluginManager._cleanup_plugin_generation_state()` rather than inspecting buffer internals.

## Why this matters

Unload is a recovery command.  After it succeeds, plugin-authored delayed surfaces should not keep shaping future navigation or selection-recovery UX.  Leaving jumplist rows was especially subtle during reload: a staged replacement that pushed the same cursor snapshot could be deduplicated against the old row, then the old row would be removed, leaving no replacement row.  Generation-scoped precleanup plus transaction rollback fixes that without widening the plugin policy surface.

## Tests

Focused tests cover:

- unload removing plugin-owned saved-selection and jumplist rows;
- reload recreating same-shaped recovery rows under the new plugin generation;
- failed staged reload restoring the old recovery rows.

## Residual risk

This still does not undo ordinary buffer edits, file opens, recent-file rows, prompt history, or other user-visible effects that already happened while a plugin was loaded.  It closes one concrete class of delayed navigation/recovery state that was already provenance-stamped but not lifecycle-cleaned.
