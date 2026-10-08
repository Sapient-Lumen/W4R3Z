# Rev0783 — Direct fsync and selection/cursor argument boundary

## Audit finding

Rev0781 closed the more dangerous direct-save content race for `save.atomic=false`,
and rev0782 closed delayed keymode authority laundering.  Two smaller but still
trust-relevant seams remained near those changes.

First, the direct non-atomic writer still treated `save.fsync=true` as a false
promise.  The atomic writer fsynced its temp file and directory when requested;
the compatibility direct writer opened, checked, truncated, and wrote the file
but never flushed/fsynced the final descriptor or parent directory before
returning success.  Direct writes remain less crash-safe than atomic replace, but
an explicit fsync request should not silently disappear.

Second, rev0781 only migrated direct text-edit hostcalls to non-consuming type
preflight.  Cursor, selection, line/range, and cursorstate hostcalls still had
raw VM pop paths or partial mutation during validation.  A malformed script call
could consume the stack evidence that explained the failure, or `ed.set-selections`
could update earlier cursors before rejecting a later malformed row.

## Change

`src/micromax_editor/file_write.py` now threads `fsync` through the direct writer
branches.  After the opened-fd freshness/digest check and write, direct writers
flush and fsync the file descriptor when requested.  The dir-fd path also fsyncs
the opened parent directory fd; the path fallback fsyncs the parent directory by
path.  `FileWriteResult.fsync` now reports the requested/direct success state
instead of always returning `False` on the direct lane.

`src/micromax_editor/hostcall_boundary.py` now has list argument preflight helpers
for hostcalls that accept portable list-shaped editor state:

- `peek_list_arg(...)`
- `pop_list_arg(...)`

`src/micromax_editor/micromax_bridge.py` now applies peek-then-commit semantics to
higher-risk cursor/selection/range surfaces:

- `ed.line`
- `ed.lines`
- `ed.range-text`
- `ed.set-cursor`
- `ed.set-cursors`
- `ed.set-primary`
- `ed.set-selection-range`
- `ed.set-selections`
- `ed.replace-selections`
- `ed.set-cursorstate`

`ed.set-selections` now builds the replacement cursor/anchor model completely
before touching live editor state.  `ed.set-cursorstate` validates the whole
portable state object before deleting the stack argument or allocating new cursor
IDs.

The bounded doctor lane keeps the new state-hostcall regression file and drops
`tests/test_prompt_rank.py` from the default risk set to avoid widening the
handoff preflight merely because one more runtime-boundary file was added.

## Concrete guarantees

- `save.atomic=false` honors `save.fsync=true` on the successful direct-write
  path.
- Direct-write metadata reports `fsync=true` when that direct save completed with
  fsync requested.
- Cursor/line/range hostcall type errors preserve the original VM-stack
  arguments.
- Malformed `ed.set-selections` requests preserve existing cursor/selection state.
- Malformed `ed.replace-selections` requests preserve the replacement table and
  buffer text.
- Malformed `ed.set-cursorstate` requests preserve stack evidence and do not
  advance the cursor-id allocator during failed validation.

## Validation

Focused regressions added/updated:

- `tests/test_editor_fs_open_save.py::test_direct_file_writer_honors_fsync_when_atomic_disabled`
- `tests/test_editor_hostcall_state_argument_boundary.py`
- `tests/test_mxdoctor.py` bounded-lane selector expectations

Representative local checks:

```text
16 passed in 0.73s
95 passed in 3.25s
```

Those runs covered direct fsync, cursor/selection stack preservation, readonly
hostcall argument preservation, structured hostcall boundaries, and the bounded
doctor selector contract.

## Remaining risk

`save.atomic=false` is still a compatibility lane.  It now has opened-fd
freshness/digest checks and explicit fsync handling, but a crash during direct
write can still leave a partial file.  The default should remain atomic save.

The hostcall surface still has lower-risk navigation/display helpers using raw
VM pops.  The important next audit is not to eliminate every pop immediately, but
to continue migrating any hostcall that mutates editor state, host state, or
long-lived runtime registries to explicit preflight-then-commit semantics.
