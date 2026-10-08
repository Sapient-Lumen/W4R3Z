# rev0021 web/public-overlap — SHARE-SCAN-CACHE-01 / U-248

## Conclusion

U-248 is **not** a clean fresh/unmentioned item. It has strong public overlap with Nicotine+ issue #2447.

The hard-search pass found a public GitHub result for issue #2447 with the relevant direct statement: a commenter had inspected `shares.py` and concluded that Nicotine+ does not reread file stats when the containing directory's mtime has not changed. The same issue reports visible upload-completion/abort symptoms around size/state mismatches. This does not exactly package the rev0021 regression-test shape (`path + same st_mtime + changed st_size/inode`), but it is close enough to prevent any novelty claim.

## Search strings used

```text
site:github.com/nicotine-plus/nicotine-plus share rescan mtime size inode cache metadata
site:github.com/nicotine-plus/nicotine-plus shares.py old_mtimes old_files mtime size
site:github.com/nicotine-plus/nicotine-plus "mtimes" "old_files" "shares"
site:github.com/nicotine-plus/nicotine-plus "rescan" "mtime" "shares" "size"
"Nicotine+" "rescan" "metadata" "mtime"
"Nicotine+" "shared" "mtime" "metadata"
"Nicotine+" "rescan" "shares" "file size"
"Nicotine+" "share scanner" "mtime"
site:github.com/nicotine-plus/nicotine-plus/issues "old_mtimes"
site:github.com/nicotine-plus/nicotine-plus/issues "publicmtimes.dbn"
site:github.com/nicotine-plus/nicotine-plus/issues "mtime" "shares.py"
site:github.com/nicotine-plus/nicotine-plus/issues "mtime hasn" "Nicotine"
```

## Public matches / adjacency

- **Direct/strong overlap:** Nicotine+ issue #2447 search result includes a public comment summarizing the `shares.py` mtime/stat reuse behavior. Treat U-248 as known/public-overlap even though rev0021 adds current-lane pytest coverage.
- **Symptom adjacency:** Issue #2447 reports uploads listed as complete locally while recipients see aborts around 99% and requeue/0% state.
- **Share-state symptom adjacency:** Issue #1686 reports files/folders showing incorrectly or empty in shares.
- **Rescan-performance adjacency:** Issue #3458 reports severe slowdown caused by rescan-on-startup, which is relevant to fix-shape caution: a naive “full stat+metadata parse every time” can regress performance.

## Cube decision

- Verified across all source lanes, but **do not present as a new problem**.
- Keep as a known/public-overlap maintainer regression-hardening packet.
- Use U-248 as a supporting provenance input for U-198/U-107/U-251 and future share-cache tests, not as a strict/front-lane disclosure candidate.
