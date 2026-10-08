# Rev0870: plugin clipboard unload cleanup

Rev0870 continues the plugin unload/recovery audit by treating the internal
clipboard as delayed paste/export state rather than inert scratch text.

Before this revision, a plugin could set the internal clipboard during load,
reload, lifecycle hooks, or deferred callbacks.  That payload remained after
`plugin unload NAME`, even though the plugin that authored it was gone.  A later
user paste, terminal OSC 52 export, or external clipboard export could then use
plugin-authored content that no longer belonged to any live approved plugin
surface.

## Change

- `Editor.remove_clipboard_group(group)` clears the internal clipboard when its
  authority group matches the unloaded plugin group.
- `Editor.retag_clipboard_group(old, new)` promotes staged reload clipboard
  authority from `plugin:NAME#reloadN` to the stable `plugin:NAME` group.
- `Editor.remove_plugin_clipboard_generation(root, generation)` prunes old
  committed-generation clipboard state before staged reload evaluation.
- Plugin unload and runtime cleanup now call the clipboard cleanup seam.
- Successful staged reload retags clipboard authority; failed staged reload
  restores the old clipboard contents and authority through the existing runtime
  transaction snapshot.

## Boundary

This is a lifecycle cleanup for an existing authority-stamped register, not a
new permission registry.  The internal clipboard is small, but it is also a
long-lived register that feeds later paste and export actions.  Plugin unload
should therefore remove plugin-owned clipboard payloads just as it removes
plugin-owned commands, keymodes, prompts, macros, recovery stacks, active search,
prompt history, file-navigation rows, and command-palette MRU rows.

Trusted/user clipboard contents remain outside unrelated plugin cleanup.

## Tests

Focused tests cover:

- plugin unload removes plugin-owned clipboard contents;
- plugin unload does not remove trusted/user clipboard contents;
- successful staged reload retags replacement clipboard authority to the stable
  plugin group so a later unload removes it;
- successful staged reload drops the old plugin clipboard when the replacement
  no longer recreates it;
- failed staged reload restores the old clipboard contents and authority.
