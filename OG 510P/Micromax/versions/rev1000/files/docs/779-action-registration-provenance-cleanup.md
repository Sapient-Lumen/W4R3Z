# Rev820 — Action registration provenance and plugin cleanup

## Why this mattered

Rev818 sealed action metadata reads and direct dynamic-action execution, but the
registry itself still behaved like an older raw Python dictionary.  That left a
runtime-lifecycle hole beside the protected-register work: a plugin or script
could directly call `ed.actions.register(...)`, but the resulting action did not
carry script/plugin provenance, runtime group metadata, or generation evidence.

That was risky in three ways:

1. same-origin script/plugin actions were over-protected because the action row
   looked like trusted/user state rather than the lower-authority row that
   created it;
2. plugin-owned dynamic Python callbacks could survive ordinary plugin unload
   because group cleanup did not include the action registry;
3. failed deferred plugin callbacks could half-register a lazy action and leave
   that executable callback in the editor even though dictionary/command/key/hook
   rollback succeeded.

The last two are executable-state leaks, not just metadata leaks.

## What changed

`src/micromax_editor/commands.py` now gives `Action` the same small provenance
shape used by the other runtime registers:

- `group`
- `script_context`
- `plugin_load_root`
- `plugin_generation`
- `script_origin_id`

`ActionRegistry` remains compatible with old direct callers, but it can now ask
an owner for registration context and mutation policy.  `Editor.__init__` wires
that owner callback so direct `ed.actions.register(...)` calls inherit the
current script/plugin root, generation, and editor group.

New editor helpers:

- `Editor._action_registration_context()`
- `Editor._action_authority(...)`
- `Editor._guard_action_registration_mutation(...)`
- `Editor.register_action_checked(...)`
- `Editor.remove_action_checked(...)`

The action read/run policy now compares against the action's real provenance
instead of treating every dynamic action as trusted/user state.

## Runtime cleanup and rollback

`src/micromax_editor/plugin_runtime.py` now includes the action registry in the
runtime registration snapshot.  Failed plugin load/reload/deferred-callback
rollback restores actions together with commands, keybindings, hooks, timers,
marks, messages, search state, prompt/capture state, and VM dictionary state.

Runtime group cleanup and staged group promotion now include actions:

- `cleanup_runtime_group(...)` removes actions with the plugin group;
- `retag_runtime_group(...)` promotes staged reload actions from
  `plugin:name#reloadN` to `plugin:name`.

That means plugin-created Python callbacks are no longer orphaned after unload,
and a failed plugin callback cannot leave behind a half-registered action.

## Compatibility decision

The old `ed.actions.register(...)` API still works.  Trusted Python/tests that
register actions outside script context get trusted dynamic actions as before.
Inside script/plugin context, direct registration is now safer because the action
inherits the caller's lower-authority provenance instead of becoming either
ambient trusted state or permanently inaccessible to its creator.

Built-in core actions remain public UI vocabulary, preserving help, completion,
keybinding, and palette compatibility from rev818.

## Validation

Focused tests in `tests/test_editor_action_authority.py` now cover:

- same-origin script actions being visible/runnable to their creator;
- independent script origins being unable to inspect/run those actions;
- script-origin direct action registration being unable to overwrite trusted core
  actions;
- plugin-group cleanup removing directly registered plugin actions on unload;
- failed deferred plugin callbacks rolling back direct action registration.

This revision also fixed a packaging/context mismatch in the carried rev819
keymode policy lane: `keymode_policy.py` now exports the compatibility
`keymode_access_policy` name that editor imports expected.

## Remaining risk

Dynamic action registration now has the same group/provenance/rollback footing as
commands, keys, hooks, timers, and marks.  Remaining audit work should look for
runtime state that still stores callable/editor data outside these shared
snapshot and authority seams.  Full-suite confidence still belongs to a complete
chunked `mxtest` aggregate manifest.
