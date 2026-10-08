# SHARE-SCAN-CACHE-01 / U-248 — mtime-only share-cache reuse

## Decision

**Verified current behavior, not strict-promoted, and not clean novelty.**

rev0021 proved that the share scanner reuses old share metadata when a real path exists in the prior share database and `st_mtime` matches. The cache gate does not validate `st_size`, inode/device, ctime, or an explicit scanner cache generation before reusing `[virtual_path, size, quality, duration]` metadata.

This is a useful regression-hardening packet, but it belongs in the audited backlog because public overlap is too strong. A public issue/search result for #2447 already describes an inspection of `shares.py` concluding that file stats are not reread when the containing directory mtime has not changed. That is close enough to mark this as public-known/public-overlap rather than fresh.

## Current-source proof

Source lanes:

```text
github-tag-3.3.10:   5 passed
github-branch-3.3.x: 5 passed
github-branch-master: 5 passed
```

Maintainer-style reproducer:

```text
maintainer_artifacts/share-scan-cache-01/test_share_rescan_mtime_cache_reproducer.py
```

The witness verifies five behaviors:

```text
1. Same path + same mtime + changed size:
   actual file size = 8192 bytes;
   advertised/scanner cache size remains 123 bytes.

2. Same path + same mtime + replacement file:
   replacement file retains stale cached size/quality/duration.

3. Changed mtime baseline:
   size is recomputed from current stat.

4. rebuild=True baseline:
   size is recomputed even when mtime matches.

5. Virtual share-name change baseline:
   the old cached object is mutated to the new virtual path, but stale size remains.
```

Source trace:

```text
evidence/rev0021-share-scan-cache-source-trace.md
```

The key shape is stable across all lanes: `scan_shared_folder()` reads `entry.stat().st_mtime`; if `not self.rebuild`, mtime matches `old_mtimes[path]`, and the path exists in `old_files`, it assigns `full_path_file_data = old_files[path]` and does not call `get_file_info()`. Current file size is read in `get_file_info()` only on cache miss or rebuild.

## Impact boundary

This is not peer-only code execution and not a standalone confidentiality break. Practical consequences depend on local/sync/archive/container-volume/shared-folder workflows, remote-assisted download-into-shared-folder workflows, or intentional/accidental file replacement that preserves mtime.

The verified result can create stale advertised size/metadata and can feed into transfer-size/provenance families already audited in rev0018 and rev0019:

```text
U-198 — opened-file/path provenance input.
U-107 — upload read clamp sibling.
U-251 — EOF-before-advertised-size lifecycle sibling.
```

## Recommended fix shape

Do not fix this by blindly reparsing all metadata on every scan. That risks undoing the performance purpose of the mtime cache.

A coherent fix should make the cheap cache key stronger:

```text
- Store and compare st_size with st_mtime before reusing old file metadata.
- Where reliable, also store st_dev/st_ino and/or ctime/mtime_ns.
- Use mtime_ns where available to reduce coarse timestamp collisions.
- Keep rebuild=True as the full reparse path.
- Preserve the virtual-name update behavior intentionally, but avoid mutating the old cache object in place if that can leak state across permission groups or later scanner steps.
- Add regression tests for same mtime + changed size, same mtime + replacement file, changed mtime baseline, rebuild baseline, and virtual share-name migration.
```

## Presentation decision

```text
strict/front-lane: no
production-ready disclosure text: no
verified audited-backlog packet: yes
public-overlap class: direct/strong public overlap via #2447
```
