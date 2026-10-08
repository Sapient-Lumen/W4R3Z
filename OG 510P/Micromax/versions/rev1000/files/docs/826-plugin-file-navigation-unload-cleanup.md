# Rev0868: plugin file-navigation unload cleanup

Rev0868 continues the plugin unload/recovery audit by treating recent-file MRU
rows and saved cursor rows as delayed navigation state rather than inert
preferences.

Before this revision, a plugin could open a file or save a cursor position during
load, reload, lifecycle hooks, or deferred callbacks.  The plugin could then be
unloaded, but the recent-file row and savecursor row stayed behind.  Because both
stores can be persisted, plugin-authored file navigation could survive the
plugin lifecycle boundary and reappear after restart.

## Change

- `Editor.remove_recent_files_group(group)` removes recent-file rows whose
  authority group matches the unloaded plugin group and best-effort persists the
  pruned MRU list when recent-file persistence is enabled.
- `Editor.retag_recent_files_group(old, new)` promotes staged reload recent-file
  rows from `plugin:NAME#reloadN` to the stable `plugin:NAME` group.
- `Editor.remove_plugin_recent_files_generation(root, generation)` prunes old
  committed-generation recent-file rows before staged reload evaluation.
- `Editor.remove_saved_cursor_group(group)` removes savecursor rows whose
  authority group matches the unloaded plugin group and best-effort persists the
  pruned cursor map when savecursor persistence is enabled.
- `Editor.retag_saved_cursor_group(old, new)` promotes staged reload savecursor
  authority to the stable plugin group.
- `Editor.remove_plugin_saved_cursor_generation(root, generation)` prunes old
  committed-generation savecursor rows before staged reload evaluation.
- The existing plugin transaction snapshot already covers recent-file and
  savecursor authority sidecars, so failed staged reload restores the old rows.

## Boundary

This is lifecycle cleanup for two existing authority-stamped stores, not a new
permission registry.  Recent-file MRU and savecursor rows can steer later file
navigation and can persist across sessions.  Plugin unload should therefore
remove plugin-owned rows just as it removes plugin-owned commands, keymodes,
prompts, macros, recovery stacks, active search, and prompt history.

Trusted/user recent-file and savecursor rows remain outside unrelated plugin
cleanup.

## Tests

Focused tests cover:

- plugin unload removes plugin-owned persisted recent-file and savecursor rows;
- failed staged reload restores old recent-file and savecursor rows and their
  plugin generation authority;
- successful staged reload retags new file-navigation rows to the stable plugin
  group so a later unload removes them.
