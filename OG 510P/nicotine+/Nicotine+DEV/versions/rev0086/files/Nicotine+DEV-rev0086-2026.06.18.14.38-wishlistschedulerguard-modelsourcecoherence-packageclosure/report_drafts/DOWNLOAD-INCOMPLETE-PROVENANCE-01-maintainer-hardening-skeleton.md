# Maintainer hardening skeleton — DOWNLOAD-INCOMPLETE-PROVENANCE-01

## Summary

Nicotine+ currently treats deterministic incomplete-download files as resumable/finishable based on username, virtual path, and size/offset state, without binding the local partial file to a request generation, local file-entry identity, or stored provenance. A stale exact-size incomplete file can be moved to the completed-download destination at `FileTransferInit` time without receiving any new bytes from the peer.

This is not proposed as a high-priority vulnerability report. It is a robustness/integrity hardening packet with public-adjacent incomplete-download symptoms and local/sync/shared-folder preconditions.

## Reproducer

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest -q \
  maintainer_artifacts/download-incomplete-provenance-01/test_download_incomplete_provenance_reproducer.py
```

Expected current behavior on the rev0003 source lanes:

```text
github-tag-3.3.10:   7 passed
github-branch-3.3.x: 7 passed
github-branch-master: 7 passed
```

## Current behavior covered

1. Exact-size stale incomplete file is promoted to finished without new download bytes.
2. Partial stale incomplete file is trusted as resume offset.
3. Symlink at the incomplete path is followed by `open(..., "ab+")`.
4. Advisory lock failure is logged but the transfer continues.
5. `md5(virtual_path + username)` plus basename truncation can collide for distinct tuples.
6. Existing completed file with matching size is treated as already downloaded.
7. Destination appearing after final basename decision can be replaced by `shutil.move()` on POSIX.

## Suggested direction

A coherent fix should avoid treating these as six independent patches. Consider a download-local provenance policy:

```text
- Store a sidecar/provenance record for incomplete files.
- Bind partial bytes to structured username/path/size/generation fields.
- Delimit the hash input or hash structured bytes rather than raw concatenation.
- Restart, fail closed, or ask the user when provenance is missing or mismatched.
- Use no-follow/regular-file checks where supported.
- Treat lock failure as a terminal or retryable local-file error, not a warning-only event.
- Revalidate the completed destination at the final move boundary.
```

## Compatibility caution

Do not break ordinary interrupted downloads, cross-filesystem moves, filename conflict avoidance, or manual recovery workflows.
