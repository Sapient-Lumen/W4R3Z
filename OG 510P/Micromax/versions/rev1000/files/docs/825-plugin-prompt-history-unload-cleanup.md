# Rev0867: plugin prompt-history unload cleanup

Rev0867 continues the plugin unload/recovery audit by treating prompt history as
replayable delayed state instead of inert text.

Before this revision, a plugin could call `ed.command` or otherwise append to the
command/find prompt history during load, lifecycle hooks, or callbacks.  The
plugin could then be unloaded, but the history row stayed behind.  A later user
or same-origin script history recall could put the plugin-authored command text
back into the prompt after the plugin surface was supposedly removed.

## Change

- `Editor.remove_prompt_history_group(group)` removes prompt-history rows whose
  authority group matches the unloaded plugin group.
- `Editor.retag_prompt_history_group(old, new)` promotes staged reload history
  rows from `plugin:NAME#reloadN` to the stable `plugin:NAME` group.
- `Editor.remove_plugin_prompt_history_generation(root, generation)` prunes rows
  from the old committed generation before staged reload evaluation.
- The existing plugin transaction snapshot already covers prompt-history rows and
  authority sidecars, so failed staged load/deinit restores the old history.
- When prompt-history persistence is enabled, pruning plugin-owned rows performs
  a best-effort save so stale plugin-authored command text is not immediately
  reintroduced from `history.json` on the next startup.

## Boundary

This is deliberately not a new permission registry.  It is lifecycle cleanup for
one existing authority-stamped store.  Prompt history can replay executable
command text; plugin unload should therefore remove plugin-owned history just as
it removes plugin-owned commands, keymodes, prompts, macros, recovery rows, and
active search state.

Trusted/user history rows remain outside unrelated plugin cleanup.

## Tests

Focused tests cover:

- plugin unload removes plugin-owned command history;
- plugin unload does not remove trusted/user command history;
- prompt-history persistence is pruned when enabled;
- successful staged reload prunes old-generation history and retags replacement
  history to the stable plugin group;
- failed staged reload restores the old prompt-history row and generation.
