# Rev0800 — interaction capture rollback and query-replace edit boundary

Rev0800 keeps moving the cube along the runtime trust boundary instead of adding only registry entries.  The audit focus was delayed interactive state: prompts, capture keymodes, query-replace sessions, and external URL confirmations can outlive the callback or command that created them.  That makes them authority-bearing state, not disposable UI detail.

## Failure mode found

Failed deferred plugin callbacks already rolled back VM dictionary topology, command/key/hook/timer registrations, cursor state, message-log provenance, recent/prompt history, marks, and clipboard authority.  They did **not** restore interaction state.

That left a sharp partial-failure path:

1. a plugin command/key/timer/hook callback opens a command prompt or starts `qreplace`;
2. the callback then fails or returns false;
3. dictionary/registration rollback succeeds;
4. the editor is still left with a live prompt, capture keymode, URL confirmation, or query-replace session created by the failed callback.

For query-replace specifically, that could leave a capture mode active after the plugin callback had already been rejected.  For command prompts, a failed callback could leave delayed command text ready for a later submit under a different-looking UI moment.

## Code changes

`src/micromax_editor/plugin_runtime.py` now has an `EditorInteractionStateSnapshot` that captures:

- `prompt`;
- `qreplace`;
- `key_mode_stack`;
- `_pending_open_url` and `_pending_open_url_source`;
- the transient editor `input` scratch dictionary.

`RuntimeRegistrationSnapshot` includes that interaction snapshot, and `restore_runtime_registrations(...)` restores it along with the existing registry/cursor/history/clipboard state.  Failed plugin callbacks and failed plugin lifecycle transitions therefore put the visible interaction surface back where it was before the failed transition began.

`src/micromax_editor/editor.py` also gained a direct query-replace edit boundary.  `begin_query_replace(...)` already refused protected/read-only buffers, and ordinary key dispatch already has a mutating-action guard.  The direct `qreplace_yes()`, `qreplace_last()`, and `qreplace_all()` paths now recheck readonly/protected state at replacement time, so a buffer that becomes readonly after the session starts cannot still be modified by calling the query-replace methods directly.  `qreplace_all()` now breaks cleanly when a replacement is refused instead of looping on an unchanged current match.

## Tests added or repaired

New focused test:

- `tests/test_editor_qreplace_interaction_boundary.py`

Expanded plugin rollback tests:

- failed plugin command callback starts `qreplace`, returns false, and the editor restores `qreplace`, capture keymode, keymode stack, buffer text, and selection state;
- failed plugin command callback opens a command prompt, returns false, and the editor restores prompt/keymode state.

While broadening the query-replace run, `tests/test_editor_query_replace.py` also had stale imports/helpers for hostcall-boundary cases that were already present in the file.  Rev0800 repairs those imports so the whole file runs cleanly instead of only the older qreplace subset.

## Remaining risk

This is still an in-process rollback boundary, not a UI event sandbox.  Successful callbacks intentionally keep prompt/query-replace state they create.  The next related audit should look for any other delayed interaction objects that are stored outside `prompt`, `qreplace`, `_pending_open_url`, `key_mode_stack`, or `input`.

## Validation evidence

Focused validation performed during the rev0800 turn:

```text
PYTHONDONTWRITEBYTECODE=1 python -m py_compile \
  src/micromax_editor/plugin_runtime.py \
  src/micromax_editor/editor.py \
  tests/test_editor_qreplace_interaction_boundary.py \
  tests/test_editor_query_replace.py \
  tests/test_plugin_containment_and_caps.py \
  tools/mxdoctor.py
```

```text
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q \
  tests/test_editor_qreplace_interaction_boundary.py \
  tests/test_plugin_containment_and_caps.py \
  tests/test_editor_query_replace.py \
  tests/test_editor_deferred_authority.py \
  tests/test_editor_hostcall_boundary.py --durations=10

110 passed in 8.66s
```
