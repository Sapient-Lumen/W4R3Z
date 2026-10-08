# Deferred plugin callback scoped rollback (rev0888)

Rev0887 left the largest remaining rollback pressure in broad plugin
source/lifecycle/callback transactions.  Rev0888 takes the first safe slice:
failed **live plugin callbacks** no longer need the full
`RuntimeRegistrationSnapshot` when the callback can be tied to a currently loaded
plugin root, generation, and stable runtime group.

## What changed

`snapshot_plugin_callback_state()` now accepts explicit callback identity:

- `group` — the loaded plugin's stable runtime group;
- `plugin_load_root` — the package-local root captured at load time;
- `plugin_generation` — the loaded generation token.

When all three are present, the callback snapshot stores:

- `VmDictionarySnapshot` for callback-time definitions/includes;
- `RuntimeGroupStateSnapshot` for plugin-group runtime registrations and delayed
  group state;
- `RuntimeGenerationStateSnapshot` for plugin-generation delayed rows, registers,
  saved macro slots, and active macro recording;
- option state, because ordinary option writes are not grouped;
- cursor state, because failed prompt/query-replace/open-url style callbacks must
  restore selection/capture consequences;
- execution stacks and message evidence.

The broad `RuntimeRegistrationSnapshot` remains the fallback when a low-level
embedding calls the helper without live plugin identity.

## Why this is safe

Live plugin callbacks already run through `Editor.plugin_callback_context()`,
which resolves the loaded plugin from the captured package root, runtime group,
and generation.  That context sets the plugin wordlist, current hook/editor
runtime group, and package-local load root before invoking the callback.

Existing mutation guards still prevent lower-authority plugin code from
modifying trusted or other-plugin registrations.  Therefore failed callback
rollback can focus on the callback's own group/generation rows while preserving
unrelated trusted state that may have changed outside the plugin-owned surfaces.

## Regression coverage

The focused tests prove that scoped callback rollback:

- restores an existing plugin-owned command and removes a new plugin-owned
  command created during the failed callback;
- does not rewind an unrelated trusted command changed after the callback
  snapshot was taken;
- restores plugin-generation saved macro slots;
- does not rewind unrelated trusted macro slots;
- still falls back to `RuntimeRegistrationSnapshot` when no plugin identity is
  supplied;
- preserves the existing query-replace/cursor rollback behavior that previously
  depended on the broad snapshot.

## Non-claims

This does not remove `RuntimeRegistrationSnapshot`.  Failed plugin source
loading, lifecycle hooks, discarded deinit mutations, and legacy callback
embeddings still use the broad snapshot.  The new path is a scoped live-callback
rollback boundary, not hostile-code containment, process isolation, or rollback
for external effects.
