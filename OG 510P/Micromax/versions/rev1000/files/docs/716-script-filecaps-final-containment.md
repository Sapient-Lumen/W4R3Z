# Rev769 — script file caps final containment

## Why this mattered

Rev767 and rev768 moved scripted save/diff/revert through capability-gated helpers and anchored relative buffer paths under `cap.fs-root`.  That fixed the obvious ambient-cwd bug, but the remaining risky edge was lower: the helper could validate one resolved path and then the low-level read/write could follow a different concrete path if a symlink changed between preflight and the filesystem operation.

That is not a perfect sandbox problem; it is a practical trust problem.  If a scripted file operation says it is bounded by `cap.fs-root`, the final read/write boundary should re-resolve the path it is about to touch rather than assuming the earlier preflight still describes reality.

## What changed

`src/micromax_editor/file_write.py` now exposes a small final-check seam:

- `FileContainmentError`
- `assert_path_within_root(path, root)`
- a `containment_root=` parameter on `write_file_bytes(...)`

The writer follows the final symlink target, checks that resolved target against the containment root, and checks again immediately before atomic `os.replace(...)`.  The direct-write path uses the same final check.  This preserves the intended symlink behavior for normal saves while refusing symlink targets that escape the script capability root.

`src/micromax_editor/file_recovery.py` mirrors the write side with `containment_root=` on `read_file_for_editor(...)`, so scripted `diff` and `revert` cannot use a preflighted path as an ambient read oracle after a late symlink swap.

`Editor.save(...)`, `Editor.save_as(...)`, `Editor.disk_diff_lines(...)`, and `Editor.revert_buffer_from_disk(...)` now accept `containment_root=`.  `src/micromax_editor/file_scriptops.py` passes the active `cap.fs-root` down to those editor methods after its existing capability preflight.

## Regression coverage

Focused tests now cover:

- atomic writer refusal when a symlink inside the root points outside the root;
- direct writer refusal for the same escape;
- read/recovery refusal for the same escape;
- scripted `save` with a relative buffer path where the symlink is swapped after capability preflight but before the editor writer runs.

The late-swap scripted test is the important behavioral witness: both the original inside file and the outside file remain unchanged, the buffer stays dirty, and the script-visible command fails with an `outside containment root` error.

## Remaining risk

This is still a best-effort capability boundary, not OS-level confinement.  A hostile same-user process can race many filesystem facts.  The value of this revision is narrower and concrete: the Micromax script surface no longer trusts an early path decision when the final read/write can cheaply re-resolve and fail closed.
