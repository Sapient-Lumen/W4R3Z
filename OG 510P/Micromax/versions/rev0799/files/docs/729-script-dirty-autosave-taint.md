# Rev776 script-dirty autosave taint

Rev776 also closes a delayed-write hole that remained after the script option-policy guard.

A lower-authority script should not be able to turn a buffer edit into a disk write merely because trusted user state already had `autosave` enabled.  That is a different failure mode from `set autosave 1`: even when the script cannot mutate protected options, it can still dirty a path-backed buffer and let a later editor-owned autosave pass run outside `script_context()`.

The fix adds a small per-buffer witness:

- `EditorBuffer.script_dirty_since_sync`

The witness is set when a buffer is changed while `Editor.in_script_context()` is true.  It is cleared only at explicit synchronization boundaries such as successful save, revert, or a clean/open state.  Autosave refuses a script-tainted dirty buffer while `cap.fs-save` is false, even when `autosave` was enabled by trusted user code.

Direct text-mutating hostcalls now report the same dirty-origin signal through the shared editor notifier:

- `ed.set-text`
- `ed.replace-selections`
- `ed.replace-range`
- `ed.delete-range`
- `ed.with-undo`

Command-level replacement and `qreplace` completion also call the same notifier.  This avoids a split-brain model where action-based edits are tracked but direct VM/editor hostcalls can quietly bypass autosave tainting.

Regression coverage proves:

- script context cannot enable `autosave` directly;
- script context cannot disable `save.checkexternal`;
- script context cannot clear `readonly`;
- script-tainted edits are not autosaved without `cap.fs-save`, even when a trusted user enabled autosave first;
- direct script `ed.set-text` hostcalls taint the buffer and do not autosave without save authority.

This remains application-level authority separation inside one Python process, not an OS sandbox.  The important guarantee is narrower and concrete: editor-owned autosave no longer becomes a delayed `cap.fs-save` bypass for script-originated buffer edits.
