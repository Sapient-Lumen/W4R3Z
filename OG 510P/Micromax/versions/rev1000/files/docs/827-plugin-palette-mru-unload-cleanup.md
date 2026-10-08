# Rev0869: plugin command-palette MRU unload cleanup

Rev0869 continues the plugin unload/recovery audit by treating command-palette
MRU rows as delayed command/action selection state rather than inert UI trivia.

Before this revision, a plugin could open the command palette during load,
reload, lifecycle hooks, or deferred callbacks and submit a command or action
selection.  That row stayed in the palette MRU after `plugin unload NAME`, even
though the plugin-owned command/action surface might already be gone.  The row
could keep steering later palette ordering toward stale plugin-authored choices
and could survive failed reload attempts unless the broader transaction happened
to restore it.

## Change

- `Editor.remove_palette_recent_group(group)` removes command-palette MRU rows
  whose authority group matches the unloaded plugin group.
- `Editor.retag_palette_recent_group(old, new)` promotes staged reload MRU rows
  from `plugin:NAME#reloadN` to the stable `plugin:NAME` group.
- `Editor.remove_plugin_palette_recent_generation(root, generation)` prunes old
  committed-generation MRU rows before staged reload evaluation.
- Plugin unload and runtime cleanup now call the palette MRU cleanup seam.
- Successful staged reload retags command-palette MRU authority; failed staged
  reload restores the old rows through the existing runtime-registration
  transaction snapshot.

## Boundary

This is a lifecycle cleanup for an existing authority-stamped UI register, not a
new permission registry.  Palette MRU rows are small, session-local state, but
they influence which command or action the user sees and submits first.  Plugin
unload should therefore remove plugin-owned rows just as it removes plugin-owned
commands, keymodes, prompts, macros, recovery stacks, active search, prompt
history, and file-navigation rows.

Trusted/user palette MRU rows remain outside unrelated plugin cleanup.

## Tests

Focused tests cover:

- plugin unload removes plugin-owned command-palette MRU rows;
- plugin unload does not remove trusted/user palette MRU rows;
- successful staged reload retags replacement palette MRU rows to the stable
  plugin group so a later unload removes them;
- failed staged reload restores the old palette MRU row and authority.
