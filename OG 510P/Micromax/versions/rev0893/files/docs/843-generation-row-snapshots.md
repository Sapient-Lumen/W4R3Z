# Rev0885 generation row snapshots

Rev0885 narrows the generation-scoped delayed-cleanup rollback path. Runtime
cleanup/retag already used touched-group snapshots; generation cleanup still
used broad `RuntimeGenerationStateSnapshot` fields for many durable editor
sidecars. That meant a failed plugin unload/reload generation cleanup could copy
and restore unrelated recent-file, palette, prompt-history, saved-cursor,
clipboard, search, help-history, and recovery state.

The new path keeps generation cleanup fail-closed, but captures non-macro
delayed state by **plugin load root plus plugin generation**:

- recovery stack rows;
- recent-file MRU rows;
- command-palette MRU rows;
- prompt-history rows;
- saved-cursor rows;
- clipboard register;
- active-search register;
- help-history rows and current help session.

`PluginManager` now passes the committed plugin root/generation into
`snapshot_runtime_generation_state()`. When those selector fields are present,
non-macro generation rollback uses generation-specific row/register snapshots
and leaves the older broad fields unset. `restore_runtime_generation_state()`
then removes current rows for that generation and reinserts the captured rows
near their original positions, leaving unrelated rows outside the snapshot.

Macro rollback intentionally remains broader in this revision. Saved macros,
`last`, live recording buffers, previous-last recovery, and playback state are
coupled enough that splitting them safely deserves a separate macro-specific
journal pass.

## Tests and audit

Focused tests cover:

- generation snapshots do not populate the old broad recent-file or cursor
  fields when a concrete plugin root/generation is supplied;
- only rows owned by the selected generation are captured for MRU/history,
  saved-cursor, help-history, and recovery sidecars;
- restore brings back generation-owned rows/registers after failure without
  recreating unrelated rows removed after the snapshot;
- unload and reload generation-cleanup failures still keep the old plugin
  advertised and restore the known safe runtime state.

`mxaudit` now reports `generation-rows=True` and checks that generation cleanup
snapshots are called with plugin root/generation selectors and that the
non-macro generation helpers remain wired into restore.

## Non-claims

This is still not the full typed effect journal. Macro generation cleanup still
uses broader snapshot fields. Singleton restore for clipboard/search/help can
only restore one active register/session, so future work should make those
commit boundaries explicit. This revision does not add hostile-code containment,
process/Wasm isolation, durable cleanup logs, dependency locking, CI, hosted
provenance, or a complete aggregate test manifest.
