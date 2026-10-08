# Rev0866: plugin active-search unload cleanup

Rev0866 continues the plugin unload/recovery audit by treating the active search
register as delayed navigation state.

Before this revision, a plugin could set the editor's active search query during
load or a callback, then be unloaded.  Runtime registrations, prompts, macros,
and recovery stacks were cleaned, but `find-next` / `find-prev` still used the
plugin-authored search register.  That made plugin unload incomplete: a removed
plugin could still shape later navigation through state that was no longer
owned by any live plugin surface.

## Change

- `Editor.remove_search_group(group)` clears the active search register when its
  authority group matches the unloaded plugin group.
- `Editor.retag_search_group(old, new)` promotes staged reload search state to
  the stable `plugin:NAME` group on successful reload.
- `Editor.remove_plugin_search_generation(root, generation)` clears search state
  owned by the old committed generation before staged reload evaluation.
- Plugin reload transaction snapshots already include search state, so failed
  staged load/deinit restores the old register.
- Trusted/user active search state is not removed by unloading an unrelated
  plugin.

## Boundary

This is not a new capability system.  It is a cleanup guarantee for one already
stamped editor register.  The active search query can contain sensitive text and
can drive later cursor movement, so plugin unload should remove plugin-owned
search just as it removes plugin-owned keymodes, prompts, macros, marks, and
recovery rows.

## Tests

Focused tests cover:

- plugin unload clears plugin-owned active search;
- plugin unload does not clear user-owned active search;
- plugin reload retags staged search state to the stable group;
- failed staged reload restores the old search register and generation.
