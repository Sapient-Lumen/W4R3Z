# Rev770 — dir-fd save parent-swap containment

## Why this mattered

Rev769 pushed script file capability roots down to the final read/write helpers, but the default POSIX save writer still had a narrower race: after it prepared the atomic-save temporary file, the parent path used for final cleanup or commit could be swapped. A late parent-directory symlink/swap is uncommon in normal editing, but it is exactly the kind of trust-boundary gap that makes a capability-style save policy look stronger than it really is.

The severe version of the bug is not just a failed save. It is a save that validates one directory, creates a temporary file there, then performs a later cleanup or commit through a pathname that now names a different parent.

## What changed

`src/micromax_editor/file_write.py` now uses an opened parent directory file descriptor on capable POSIX hosts for the default atomic-save path. Temp creation, freshness checks, temp cleanup, and final `os.replace(...)` are bound to that opened parent fd when the platform exposes the required `dir_fd` operations.

Before committing, the writer rechecks both:

- that the opened parent still resolves within `containment_root`, when a containment root is active;
- that the current pathname parent still identifies the same directory as the opened parent fd.

If the parent was swapped after temp creation, the writer raises `FileContainmentError`, leaves the destination untouched, and removes the abandoned temp file through the original directory fd rather than through the swapped path.

The direct non-atomic writer follows the same parent-fd containment/freshness discipline where available. Hosts without the needed `dir_fd` support still use the path-based fallback, which remains best-effort but portable.

## Regression coverage

Focused save tests cover parent-directory swaps after temp-file creation and verify that:

- the save fails closed;
- the outside/swapped destination is not written;
- the abandoned temp file is cleaned from the original parent;
- direct-write mode applies the same parent-fd containment check on capable POSIX hosts.

The bounded `mxdoctor` risk lane includes the file-save tests that exercise this surface so a future writer refactor does not silently fall back to stale-parent path commits.

## Remaining risk

This is still an application-level filesystem containment check, not an OS sandbox. On platforms without descriptor-relative operations, the project keeps the portable path-based behavior and the associated best-effort caveat. The practical improvement is that the common POSIX cloudtainer path no longer commits or cleans atomic-save state through a stale parent pathname.
