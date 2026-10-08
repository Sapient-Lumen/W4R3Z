# Rev0864 — plugin saved macro cleanup and rollback

Saved macros are delayed executable state.  A plugin-created macro can outlive the command, key, timer, hook, prompt, or keymode that created it, and later replay command steps after `plugin unload NAME` has reported success.

Rev0864 closes that recovery gap without adding a new registry:

- plugin transaction snapshots now include the macro registry, active macro recording state, and macro playback state;
- failed plugin load, staged reload, deinit, and callback transactions restore macro state along with dictionary/runtime registrations;
- `plugin unload NAME` removes saved/live macro state whose recorded steps belong to the unloaded plugin root and generation;
- staged reload temporarily prunes old-generation plugin macros under the transaction snapshot, allowing same-named macro replacement while preserving rollback if the staged load fails;
- user/trusted macros, empty slots, and mixed-origin macro slots are left alone and continue to fail closed under the existing macro authority policy.

The narrow code seam is `Editor.remove_plugin_macro_generation()`, backed by the expanded `RuntimeRegistrationSnapshot` in `plugin_runtime.py`.  Plugin lifecycle code still delegates cleanup through `PluginManager._cleanup_plugin_generation_state()` instead of inspecting macro internals.

## Tests

Focused tests cover:

- failed plugin load rolling back a macro side effect;
- unload removing a plugin-owned saved macro;
- reload pruning the old generation while keeping the staged generation;
- same-named macro replacement during staged reload;
- failed staged reload restoring the old macro;
- failing deinit rolling back macro mutations.

## Residual risk

This does not undo buffer edits, prompt history, or arbitrary user-visible effects that already happened while a plugin was loaded.  It prevents one concrete class of delayed executable state from surviving cleanup or failed lifecycle transactions.
