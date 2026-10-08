# SHARE-SCAN-CACHE-01 maintainer hardening skeleton

## Summary

The share scanner currently reuses cached file metadata when a path exists in the previous share database and `st_mtime` matches, without validating `st_size`, inode/device, ctime, or another cache-generation marker. This can leave advertised size/quality/duration stale after a same-path replacement or size change that preserves mtime.

## Current behavior witness

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus pytest -q maintainer_artifacts/share-scan-cache-01/test_share_rescan_mtime_cache_reproducer.py
```

Expected current output across archived lanes:

```text
github-tag-3.3.10:   5 passed
github-branch-3.3.x: 5 passed
github-branch-master: 5 passed
```

## Fix target

A fixed behavior should preserve the performance benefit of mtime-based rescans, but should not reuse stale metadata when a cheap stat comparison shows size or file identity changed.

Suggested fixed-behavior assertions:

```text
- same path + same mtime + changed st_size recomputes metadata;
- same path + same mtime + changed inode/device recomputes metadata when available;
- mtime change still recomputes metadata;
- rebuild=True still recomputes metadata;
- virtual share-name migration updates the virtual path without mutating stale cache records unexpectedly.
```

## Public-overlap note

This should not be framed as a new/unmentioned issue. Public #2447 discussion/search material already overlaps the `shares.py` mtime/stat reuse behavior. Treat this as a regression-hardening test and a supporting piece for transfer/file-provenance cleanup.
