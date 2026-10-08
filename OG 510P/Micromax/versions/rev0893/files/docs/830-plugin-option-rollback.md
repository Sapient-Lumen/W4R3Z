# Rev0872: plugin option rollback

Rev0872 continues the plugin lifecycle audit by treating ordinary option writes
as transactional plugin side effects.  This is not an unload-cleanup registry:
it is a rollback guard for plugin source, lifecycle hooks, and deferred plugin
callbacks that fail before their side effects can be considered committed.

Before this revision, a plugin that failed during `init`, staged reload, deinit,
or a command callback could still leave ordinary option mutations behind.  The
script-option policy already prevents lower-authority scripts from changing
capability bits and host-adjacent protected knobs, but safe-looking UI/editor
options such as `tabsize` could survive a failed plugin transaction even though
the plugin itself was not loaded or the callback failed.

## Change

- `Editor._snapshot_option_state()` captures global option values and live
  buffer-local option maps.
- `Editor._restore_option_state(snapshot)` restores those values and refreshes
  derived host state such as capability advertisements and fast-dirty mode.
- `plugin_runtime.RuntimeRegistrationSnapshot` now carries option state beside
  existing command/key/hook/timer/register snapshots.
- Failed plugin load, failed staged reload, failed deinit, and failed deferred
  plugin callbacks restore option state through the existing plugin transaction
  machinery.
- Successful plugin loads still keep their explicit option changes.  This
  revision does not introduce option ownership and does not attempt to revert
  already-committed plugin configuration on `plugin unload NAME`.

## Boundary

The boundary is deliberately narrow.  Capability options and protected host
policy knobs remain guarded by `option_policy.py`; rev0872 handles the remaining
ordinary option writes that are allowed during script/plugin execution but should
not leak out of failed plugin transactions.

This keeps rollback semantics honest without inventing a broad option registry
or claiming that successful plugin configuration is reversible after the fact.

## Tests

Focused tests cover:

- failed plugin load rolls back a global option mutation;
- failed plugin load rolls back a buffer-local option mutation;
- failed staged plugin reload restores the prior option state;
- failed plugin command callbacks roll back option mutations;
- plugin deinit option mutations are discarded during successful unload because
  deinit is cleanup code, not a dictionary or configuration-definition API.
