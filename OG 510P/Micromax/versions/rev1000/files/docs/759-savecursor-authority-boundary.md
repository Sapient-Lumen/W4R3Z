# Rev0801 — savecursor authority boundary

Rev0801 finishes the high-risk persistence audit that was left open after the recent history, undo/redo, clipboard, and interaction-state work.  `savecursor` is not just a convenience preference: it is a delayed navigation register.  A cursor restored later can change what a script reads, edits, replaces, or saves after opening a file.  That means persisted/user saved-cursor rows need the same provenance treatment as other long-lived recovery registers.

## Failure mode found

Before this revision, saved cursor rows were keyed only by normalized path:

- trusted/user cursor positions, persisted cursor positions, and script-created cursor positions were indistinguishable;
- script-origin `open_file(...)` could restore a trusted or persisted cursor landing by default;
- script-origin buffer switching/closing could overwrite a trusted saved cursor as an incidental side effect;
- plugin callback rollback covered recent files, prompt history, clipboard, marks, cursor state, and interaction state, but not the saved-cursor register.

The dangerous shape was quiet: a script with file-open authority did not need to ask for a cursor register.  It could simply open a file and inherit where the user last worked in that file.  It could also switch/close buffers and poison the row that an interactive user would later rely on.

## Code changes

`Editor` now keeps a parallel saved-cursor authority map:

- `_saved_cursors_authority: dict[str, RuntimeRegistrationAuthority]`;
- `_normalize_saved_cursor_authority()`;
- `_snapshot_saved_cursor_authority()`;
- `_restore_saved_cursor_authority(...)`;
- `_guard_saved_cursor_entry(...)`.

Rows loaded from disk through `load_saved_cursors()` are stamped with persisted provenance using the same lower-authority pattern already used for persisted recent-file and prompt-history rows.  Legacy in-memory rows with no authority sidecar default to trusted/user authority, so older direct tests and simple embeddings stay conservative.

`_restore_cursor_for_buffer(...)` now refuses lower-authority script replay of trusted, persisted, or other-origin cursor rows by default.  `_remember_cursor_for_buffer(...)` now refuses lower-authority script overwrites of protected rows; incidental buffer switching/closing skips the saved-cursor write instead of failing the user-visible operation.  Idempotent same-position repeats remain no-ops and do not downgrade the row owner.

A new explicit unsafe capability was added:

- feature: `ed.cursor-restore`;
- option: `cap.cursor-restore`.

That capability lets trusted hosts opt scripts into replaying protected saved-cursor rows.  It does **not** let scripts overwrite protected rows; restoring a delayed navigation target and mutating the register are kept separate.

## Rollback and transaction coverage

The saved-cursor register is now included in two rollback seams:

- `MacroReplaySnapshot` / buffer transaction snapshots carry saved-cursor rows and provenance sidecars; rev0801 also makes the transaction change predicate notice saved-cursor-only and saved-cursor-authority-only changes so `ed.with-undo` can record and replay those register updates.
- `RuntimeRegistrationSnapshot` in `plugin_runtime.py` captures and restores saved-cursor rows plus authority during failed plugin callback/lifecycle rollback.

That means a failed lower-authority plugin callback cannot leave behind a partially poisoned saved-cursor register while the rest of its runtime state is rolled back.

## Tests added

Expanded `tests/test_editor_persistence_cap_persist.py` covers:

- script-origin open does not replay a trusted saved cursor by default;
- script-origin close/switch does not overwrite a trusted saved cursor as an incidental side effect;
- same-origin script rows can still be replayed;
- persisted saved-cursor rows are not script-replayed by default;
- `cap.cursor-restore` allows replay but not overwrite;
- plugin callback rollback restores saved-cursor rows and authority;
- buffer transaction restore preserves saved-cursor authority;
- savecursor-only and savecursor-authority-only transaction deltas produce undo/redo evidence.

`tests/test_editor_capabilities_registry.py` now verifies `ed.cursor-restore` feature advertisement.

## Remaining risk

This revision deliberately avoids a broad “script can write anyone's cursor register” override.  If a real automation use case needs that, it should be a separate, clearly named destructive capability rather than overloading `cap.cursor-restore`.

The next audit should continue looking for remaining mutable editor registers that outlive the immediate command and are still stored without provenance sidecars.

## Validation evidence

Focused validation performed during the rev0801 turn:

```text
PYTHONDONTWRITEBYTECODE=1 python -m py_compile \
  src/micromax_editor/editor.py \
  src/micromax_editor/plugin_runtime.py \
  src/micromax_editor/options_default.py \
  src/micromax_editor/capabilities.py \
  tests/test_editor_persistence_cap_persist.py \
  tests/test_editor_capabilities_registry.py \
  tools/mxcontext.py
```

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python -m pytest -q \
  tests/test_editor_persistence_cap_persist.py \
  tests/test_editor_capabilities_registry.py \
  tests/test_editor_hostcall_transactions.py \
  tests/test_editor_with_undo_transaction.py --durations=10

41 passed in 3.82s
```

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python -m pytest -q \
  tests/test_plugin_reload_recovery.py \
  tests/test_plugin_containment_and_caps.py \
  tests/test_editor_deferred_authority.py \
  tests/test_editor_keybinding_docs.py \
  tests/test_editor_macros_named.py \
  tests/test_editor_persistence_cap_persist.py --durations=10

143 passed in 6.92s
```

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python -m pytest -q \
  tests/test_revision_index.py \
  tests/test_mxcontext.py \
  tests/test_mxdoctor.py --durations=10

17 passed in 8.90s
```

`mxlint` and `mxcontext --check` passed.  The current `mxtest` plan collected 1998 tests across eight segment chunks: `250, 250, 250, 250, 250, 250, 249, 249`.

The default doctor aggregate timed out in this cloudtainer after several bounded child groups had passed; the remaining bounded target files were run directly and passed as a 135-test group.  No default-doctor aggregate pass or full-suite pass is claimed.
