# DOWNLOAD-INCOMPLETE-PROVENANCE-01 / rev0023

## Decision

**Verified audited-backlog packet; not promoted to the strict document.**

This family is real and now has a maintainer-style current-behavior witness across the three source lanes, but the practical boundary is local/sync/shared-incomplete-folder provenance, stale partial files, filesystem entry races, or already-existing local files. It is better presented as integrity/provenance and filesystem-safety hardening than as a fourth high-priority report-candidate.

## Rows covered

Canonical lead:

- **U-226** — incomplete-download resume trusts existing partial file by username/path and can promote stale bytes to finished without content provenance.

Support checks folded into the same packet:

- **U-230** — incomplete-download file path is opened with append/truncate semantics without no-follow regular-file or inode checks.
- **U-250** — download incomplete-file advisory lock failure is logged but ignored before writing remote data.
- **U-253** — incomplete-download filename construction has an ambiguous username/path boundary and can collide after basename truncation.
- **U-222** — existing-file same-size shortcut can mark a selected download as finished without content/source provenance.
- **U-249** — completed-download finalization relies on a pre-move existence check and `shutil.move` without destination file-entry revalidation.

## Current-behavior proof

Maintainer-style witness:

```text
maintainer_artifacts/download-incomplete-provenance-01/test_download_incomplete_provenance_reproducer.py
```

Run result:

```text
github-tag-3.3.10:   7 passed
github-branch-3.3.x: 7 passed
github-branch-master: 7 passed
```

## What was proven

```text
Exact-size stale incomplete file:
  Existing incomplete file bytes already equal advertised transfer size.
  FileTransferInit opens the incomplete path, seeks to EOF, sees offset >= size,
  and finishes/moves those stale bytes without emitting DownloadFile.

Partial stale incomplete file:
  Existing incomplete file bytes are trusted as the resume offset.
  DownloadFile.leftbytes is size - stale_prefix_length.

Incomplete path file-entry safety:
  A symlink at the deterministic incomplete path is followed by open(..., "ab+").
  The test safely writes through the opened handle and observes bytes in the target.

Advisory lock failure:
  Simulated fcntl.lockf failure is logged but the transfer continues and DownloadFile is emitted.

Identity/path collision:
  The incomplete filename prefix is based on md5(virtual_path + username).
  Two distinct username/path tuples with the same concatenation and long basename truncation
  can resolve to the same incomplete path.

Existing complete-file shortcut:
  If a completed destination basename already exists with the requested size,
  enqueue_download marks the transfer Finished without sending a peer request.

Final move race support:
  If a destination entry appears after basename selection and before shutil.move,
  the POSIX witness shows the destination can be replaced by the completed move.
```

## Source shape

The relevant source shape is consistent across all three lanes checked:

```text
get_complete_download_file_path():
  existing destination path + matching st_size -> file_exists=True.

get_incomplete_download_file_path():
  md5 input = virtual_path + username;
  suffix = cleaned and truncated basename.

_file_transfer_init():
  incomplete path is opened using "ab+";
  advisory lock failure is logged and ignored;
  EOF offset becomes resume offset;
  offset >= size triggers _finish_transfer().

_move_finished_transfer():
  conflict-avoiding basename selected before shutil.move();
  no immediate destination revalidation before move.
```

Full trace:

```text
evidence/rev0023-download-incomplete-provenance-source-trace.md
```

## Public-overlap result

This is not a clean novelty item. There is substantial public-adjacent and some direct symptom overlap around completed downloads stuck in the incomplete folder, files remaining with `INCOMPLETE...` names, incomplete-folder deletion safety, invalid incomplete filenames, and failed move retry behavior. The exact stale-byte provenance invariant was not found as a direct public report in this pass, but the family is too overlapped and filesystem-preconditioned for strict promotion.

Captured overlap packet:

```text
evidence/rev0023-web-public-overlap-download-incomplete.md
```

## Recommended fix shape

Treat this as a single coherent download-file provenance hardening task:

```text
- Store enough provenance with incomplete files to decide whether resume is safe:
  username, virtual path, expected size, request/generation, and optionally a lightweight sidecar.
- If provenance is absent or mismatched, fail closed, restart from zero, or require explicit user action.
- Replace ambiguous md5(virtual_path + username) with a delimited/structured identity.
- Open incomplete files with regular-file/no-follow semantics where supported.
- Treat exclusive-lock failure as terminal local-file/concurrency failure or a bounded retry state.
- Revalidate destination entry immediately before final move; prefer atomic create/replace policy that is explicit.
- Preserve compatibility with ordinary resume and cross-filesystem move behavior.
```

## Why it stays out of strict

- Not peer-only: the strongest paths need stale local incomplete files, local/sync/share-folder races, a shared incomplete directory, filesystem entry manipulation, or already-existing local files.
- Public overlap is significant in the same symptom area.
- The coherent fix is important, but it is a robust maintainer hardening packet rather than a high-priority standalone report.
