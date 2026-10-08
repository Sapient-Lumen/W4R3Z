# Rev0781 — Direct-save digest witness and direct-edit preflight

## Audit finding

Rev0780 made the legacy `save.atomic=false` lane open the target before
truncating it and compare the opened file descriptor against the expected stat
witness.  That closed the ordinary race where a target was replaced or modified
between path-level freshness and final truncation.

A narrower data-loss seam remained: Micromax already records a small-file
content digest for save freshness, but the new opened-fd recheck only compared
stat fields.  An adversarial or unlucky same-inode, same-size, same-mtime update
between the path freshness check and final direct open could still pass the fd
stat comparison and then be truncated.  The default atomic writer already
rechecked the digest near commit; the compatibility direct writer needed the same
content witness on the exact fd it is about to truncate.

I also audited the adjacent direct text-edit hostcalls.  Rev0777 made them obey
readonly/protected-buffer policy before consuming operation arguments, but normal
type errors still used raw VM pops in several paths.  A failed typed edit request
could therefore eat the bad argument while leaving the buffer unchanged, making a
script/debug session less inspectable than the newer structured file hostcalls.

## Change

`src/micromax_editor/file_write.py` now has an opened-fd content digest helper for
the direct writer.  When `expected_state.content_hash` is present and the hash
budget is positive, the direct writer opens the target read/write, hashes that
same fd before `ftruncate`, and raises `FileFreshnessConflict` if the digest no
longer matches.  Missing-target creates still use exclusive-create semantics and
skip the digest path because the new fd intentionally has no prior content.

Both direct writer implementations use the new boundary:

- the dir-fd direct writer used on POSIX-capable hosts;
- the portable path fallback used when dir-fd I/O is unavailable.

`src/micromax_editor/micromax_bridge.py` now routes direct text-mutating hostcall
argument handling through non-consuming preflight helpers before deleting the
validated stack slice:

- `ed.set-text`
- `ed.replace-range`
- `ed.delete-range`
- `ed.replace-selections`

Readonly/protected-buffer denial still happens before argument consumption, and
now ordinary typed argument failures preserve their operation evidence too.


During validation, the default doctor lane also exposed a cloudtainer-waste issue:
combined pytest children could be killed even when their member files passed
when run directly.  `tools/mxdoctor.py` now keeps the bounded preflight selected
risk files as singleton pytest children.  That costs a little process-launch
overhead, but it turns the handoff command back into a diagnostic lane instead
of a large-child stress test.

## Concrete guarantees

- A direct non-atomic save refuses a same-stat content race after path freshness
  but before truncation when the buffer carries a small-file content witness.
- The same guarantee holds for the path fallback, not only the dir-fd path.
- The direct writer still does not claim crash-safety; `save.atomic=true` remains
  the safe default.
- Direct text-edit hostcalls preserve VM stack evidence on type errors as well as
  on readonly/protected-buffer denials.

## Validation

Focused regressions added/updated:

- `tests/test_editor_fs_open_save.py::test_direct_file_writer_rechecks_opened_fd_content_hash_before_truncate`
- `tests/test_editor_fs_open_save.py::test_direct_file_writer_path_fallback_rechecks_opened_fd_content_hash`
- `tests/test_editor_readonly_option.py::test_direct_text_mutating_hostcall_type_errors_preserve_args`

Representative validation for this lane:

- `tests/test_editor_fs_open_save.py`
- `tests/test_editor_readonly_option.py`
- `python tools/mxdoctor.py`

## Remaining risk

The direct writer is still a compatibility lane.  It now binds truncation to the
opened fd's stat and optional digest witnesses, but a crash during the direct
write can still leave a partial file.  Future work should keep new data-loss
prevention in the atomic path first and continue treating `save.atomic=false` as
a narrow legacy surface with explicit race regressions.
