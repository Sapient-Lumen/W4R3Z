# Rev0780 — Direct-save fd freshness and structured hostcall preflight

## Audit finding

The rev0765–rev0778 save work made the default atomic writer and script
capability lanes much safer, but the legacy direct-write lane still had one
high-risk race.  When `save.atomic=false`, the direct writer checked path
freshness and then opened the target with truncation enabled.  A file changed or
replaced between those two steps could be truncated before the writer noticed.

That is rarer than the default atomic-save path, but it is precisely the sort of
legacy escape hatch that can become a data-loss surprise later: a user disables
atomic saves for compatibility, and the stale-write guard silently becomes a
path-only preflight instead of a commit boundary.

I also found a smaller hostcall-boundary drift.  The original rev0778 stack
preflight protected denied path/URL/shell hostcalls, but the newer structured
file-recovery hostcalls still used raw VM pops for integer/string arguments.
Type errors on `ed.diff`, `ed.revert`, `ed.save-info`, `ed.save-as-info`, and
`ed.disk-states` could consume the bad argument before raising, making the
failed operation harder to inspect from a script/debugging session.

## Change

`src/micromax_editor/file_write.py` now opens direct-write targets without
`O_TRUNC`, rechecks the opened file descriptor's stat witness against the
expected freshness state, and only then truncates and writes.  Missing-target
creates still use exclusive creation.  The path-fallback direct writer now uses
the same open-before-truncate pattern rather than `Path.open("wb")`.

This does not make non-atomic writes atomic.  A crash during direct write can
still leave a partial file, which is why `save.atomic=true` remains the default.
It does, however, close the avoidable race where the direct writer itself
truncated a file that changed after the caller's freshness check.

`src/micromax_editor/hostcall_boundary.py` now has integer stack-peek/pop helpers,
and `src/micromax_editor/file_hostcalls.py` uses those helpers for structured
file hostcalls.  Type preflight failures preserve the operation arguments on the
VM stack.  Normal structured error returns keep their documented `(ok value err)`
shape.

## Concrete fixes

- `write_file_bytes(..., atomic=False, expected_state=...)` refuses a target that
  changes after the path freshness check but before the final direct write.
- The direct writer raises `FileFreshnessConflict` before truncating the changed
  file.
- Missing-target direct creates continue to fail closed if another process creates
  the target first.
- Structured file hostcall type errors preserve arguments for `ed.disk-states`,
  `ed.diff`, `ed.revert`, `ed.save-info`, and `ed.save-as-info`.

## Validation evidence

Focused tests added/updated:

- `tests/test_editor_fs_open_save.py::test_direct_file_writer_rechecks_opened_fd_before_truncate`
- `tests/test_editor_hostcall_boundary.py::test_structured_file_hostcall_type_errors_preserve_arguments`

Validation run during the turn:

- `82 passed` for `tests/test_editor_fs_open_save.py` plus `tests/test_editor_hostcall_boundary.py`
- `14 passed` for macro/deferred-authority focused checks inherited from the rev0779 content
- `python tools/mxdoctor.py` passed with `386` bounded preflight tests

## Remaining risk

The direct writer remains the compatibility lane, not the safest lane.  It now
binds truncation to the opened fd freshness witness, but it cannot provide the
crash-safety of a same-directory temp file plus atomic replace.  Future save work
should keep `save.atomic=true` as the recommended default and treat direct writes
as a legacy/compatibility path that needs narrow tests around every race it keeps.
