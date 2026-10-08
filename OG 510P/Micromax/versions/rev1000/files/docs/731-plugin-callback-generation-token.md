# Rev0777 — Plugin callback generation token

## Audit finding

Rev0775 and rev0776 made deferred plugin callbacks much safer by restoring the
plugin wordlist/root and by rolling back failed callback-time helper loads.  The
remaining provenance token was still mostly the plugin package root.  That was
not quite strong enough for long-lived editor sessions.

A plugin can be unloaded and reloaded from the same directory.  If an older
callback artifact survives outside the normal grouped cleanup path — for
example a macro step or a manually retained key/timer/hook row — root-only
matching can make that old artifact regain package-local load authority and the
new plugin wordlist after reload.  The callback is script-originated, but it
should not be able to silently become a callback for a later generation of the
same plugin just because the filesystem path is unchanged.

## Change

Rev0777 adds a monotonically increasing loaded-plugin generation token.

Changed surfaces:

- `Plugin.generation`
- `PluginManager._next_generation()`
- `plugin_load_root_context(..., generation=...)`
- `Editor.script_callback_origin_kwargs()`
- `Editor._plugin_callback_candidate(..., plugin_generation=...)`
- `Editor.plugin_callback_context(..., plugin_generation=...)`
- `Editor.run_script_origin_callback(..., plugin_generation=...)`
- `Binding.plugin_generation`
- `TimerTask.plugin_generation`
- `HookHandler.plugin_generation`
- `MacroStep.plugin_generation`

Plugin source and lifecycle execution now set both the package-local load root
and the current plugin generation on the VM.  Deferred registrations capture
both values.  Later callback execution restores plugin dictionary/root authority
only when the captured root and captured generation still match a currently
loaded plugin.

## Concrete guarantees

- A callback from a previous load generation does not borrow the wordlist/root
  of a later reload from the same directory.
- Current-generation plugin keybindings still keep package-local include roots
  without granting global `cap.fs-require`.
- Callback provenance no longer depends on a spoofable `plugin:*` group string
  or on a stable filesystem path alone.
- Embeddings without a plugin manager keep the older explicit
  `plugin_load_root_context(...)` low-level behavior for direct tests/hosts.

## Validation

Focused validation added regressions proving that a stale generation cannot load
`helper.mx` after reload while the current generation can, and that plugin
keybindings record the plugin generation they were created under.

The rev0777 handoff validation also reran the plugin/deferred macro/hook/timer
risk set and the readonly direct-hostcall boundary tests from
`docs/730-readonly-hostcall-edit-boundary.md`.

## Remaining risk

This is still an in-process application boundary.  The generation token makes
callback provenance fresher and less ambiguous; it does not turn plugin Python
objects or arbitrary side effects into a full transaction.  Persisted macro
formats also intentionally remain portable and do not expose private plugin
root/generation data; plugin authority is retained for live in-memory callback
artifacts rather than as a cross-session privilege.
