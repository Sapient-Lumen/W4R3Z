# Rev0886 macro generation snapshots

Rev0886 removes the last intentional broad tail in generation-scoped delayed
cleanup rollback: macro state.

Previous generation cleanup already removed plugin-owned saved macros and active
recordings, but rollback around a failed cleanup copied the whole macro registry:
trusted slots, user slots, the default `last` slot, live recording buffers,
previous-last recovery, and playback flags.  That was safe enough for fail-closed
plugin unload/reload, but it was wasteful and could rewind unrelated macro work.

The new path adds a macro-specific generation snapshot:

- `RuntimeMacroGenerationSnapshot`
- `RuntimeMacroSlotGenerationEntry`
- `RuntimeMacroRecordingGenerationSnapshot`
- `snapshot_macro_generation_state()`
- `restore_macro_generation_state()`

When `PluginManager` supplies a committed plugin root and generation,
`snapshot_runtime_generation_state()` now captures only:

1. saved macro slots whose steps are wholly owned by that plugin generation;
2. the default `last` slot only when its steps are owned by that generation;
3. a live macro recording only when the recording authority names that same
   plugin generation.

Restore removes current saved macro slots owned by the selected generation and
reinserts only the captured plugin-owned slots near their old positions.  Trusted
or user macro slots are left alone, even if they changed after the snapshot and
before a later cleanup surface failed.

Live recording restore is also scoped.  A plugin-owned active recording restores
its target, buffer, previous-last shadow, and recording provenance.  A trusted or
user-owned recording is not captured by a plugin generation snapshot.

## What this fixes

A failed unload/reload generation cleanup can no longer restore the entire macro
registry just because a later recent-file, search, help, or other delayed cleanup
surface failed.  The cleanup guard still fails closed and keeps the old plugin
advertised when cleanup cannot be committed, but rollback no longer rewinds
unrelated macro slots.

## Non-claims

This is still in-process cleanup recovery, not hostile-code containment.  Macro
playback itself remains executable editor automation and still depends on the
existing macro authority checks.  The broader plugin source/lifecycle/callback
transaction snapshot still uses `RuntimeRegistrationSnapshot`; this revision only
narrows generation-cleanup rollback for macro delayed state.
