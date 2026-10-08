# Rev0818 research notes

Research informed the boundary but is not represented as a portability claim.

- Linux `rename(2)` documents atomic replacement of an existing destination and
  directory-relative `renameat` resolution. This supports using same-directory
  rename as the namespace linearization point, not as a complete power-loss
  durability proof: <https://man7.org/linux/man-pages/man2/rename.2.html>
- The POSIX/Linux `openat` family exists in part to bind relative operations to
  an already-open directory descriptor and avoid prefix races: <https://man7.org/linux/man-pages/man3/openat.3p.html>
- Linux `openat2(2)` distinguishes `RESOLVE_NO_SYMLINKS` (all components) from
  `O_NOFOLLOW` (final component). AnonSync retains a portable component walk
  rather than making Linux 5.6 `openat2` a baseline requirement:
  <https://man7.org/linux/man-pages/man2/openat2.2.html>
- The C++ working draft specifies that `throw_with_nested` produces a type
  derived from both the supplied exception and `nested_exception` only when the
  supplied class is non-final. This directly explains the retained 87/96
  negative run: <https://eel.is/c++draft/support#except.nested>
- SQLite's durability documentation reinforces the conceptual separation
  between logical atomicity and persistence across power loss; sync policy and
  filesystem behavior remain part of the protocol rather than incidental I/O:
  <https://sqlite.org/pragma.html#pragma_synchronous> and
  <https://sqlite.org/howtocorrupt.html>

## Speculation and next experiments

A Linux-specific optional backend could compare the current portable walk with
`openat2(RESOLVE_NO_SYMLINKS|RESOLVE_BENEATH)` and fail closed on semantic
disagreement. A deeper crash oracle should interpose write, fsync, rename, close,
and directory-sync operations in a disposable process and then evaluate the
filesystem plus any higher-level receipt/checkpoint artifacts as one protocol.
A residue reaper remains a separate authority problem: recognizable names alone
are not deletion authority.
