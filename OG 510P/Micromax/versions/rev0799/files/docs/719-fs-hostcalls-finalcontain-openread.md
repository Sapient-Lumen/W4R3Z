# Rev770 — filesystem hostcalls final containment and script-open parity

## Why this mattered

Rev769 pushed `cap.fs-root` down to scripted save/diff/revert and the low-level file writer/reader, but the older low-level filesystem hostcalls were still shaped like this:

1. resolve the requested path under `cap.fs-root`;
2. check that resolved path;
3. use that already-resolved `Path` for read/list/stat.

That is better than ambient access, but it leaves an avoidable gap for parent/symlink changes between the high-level check and the actual filesystem operation. It also meant ordinary scripted `open` did not quite share the same nominal-path + final-containment behavior as save/recovery. The risky part was not a typical user typo; it was a trust-boundary drift where some script-visible file surfaces had the new final recheck discipline and others did not.

## What changed

New module:

`src/micromax_editor/fs_hostcalls.py`

It owns the script-visible filesystem hostcall policy for:

- `ed.fs-read`;
- `ed.fs-list`;
- `ed.fs-stat`.

The bridge now handles VM stack plumbing and capability gating, then delegates to that module. The helper first validates the resolved target against `cap.fs-root`, but it returns the nominal absolute operation path. Immediately before `exists` / `stat` / `iterdir` / `read_text`, it re-runs the final `assert_path_within_root(...)` check against the nominal path. That lets a late symlink or parent-directory swap fail closed instead of using ambient authority outside the root.

Scripted `open` now follows the same pattern. `open` through `ed.command` and the `ed.open` hostcall validates the requested path, opens the nominal path, and passes `containment_root=` into `Editor.open_file(...)`. `Editor.open_file(...)` now reads existing files through `read_file_for_editor(..., containment_root=...)` instead of doing a raw `Path.read_bytes()` in the editor monolith.

The command-palette openpath execution path also uses the nominal path plus `containment_root=` when a filesystem sandbox root is active, so palette-driven script opens no longer drift from command/hostcall opens.

## Regression coverage

Focused regressions now cover late symlink/parent swaps for:

- `ed.fs-read`;
- `ed.fs-list`;
- `ed.fs-stat`;
- scripted command `open`;
- the `ed.open` hostcall.

The tests deliberately swap an authorized in-root symlink to an outside target after the early preflight has succeeded but before the final operation. The expected result is a refused operation with an `outside containment root` witness and no leaked outside text/rows/buffer content.

`tools/mxdoctor.py` now includes the filesystem hostcall files in the bounded preflight lane. This is a small expansion of the handoff gate, but it keeps the default doctor focused on high-risk trust boundaries rather than becoming a full-suite surrogate.

## Remaining risk

This remains a best-effort application-level containment check, not an OS sandbox. A determined same-host attacker can still race after the final check on platforms without descriptor-relative/no-follow enforcement. The important improvement is consistency: every script-visible file surface in the current editor path now rechecks the concrete target near the filesystem operation, and the code path is centralized enough to keep that discipline from drifting silently.

The next high-risk follow-on is not more registry trail. The save writer now has a POSIX directory-fd path, but script-visible read/list/stat/open surfaces still rely on final path rechecks rather than a descriptor-relative read/list backend. A broader audit of remaining ambient hostcalls such as `ed.require` and include/load behavior should also happen, because they may intentionally be powerful but should be documented and gated honestly if exposed to untrusted scripts.
