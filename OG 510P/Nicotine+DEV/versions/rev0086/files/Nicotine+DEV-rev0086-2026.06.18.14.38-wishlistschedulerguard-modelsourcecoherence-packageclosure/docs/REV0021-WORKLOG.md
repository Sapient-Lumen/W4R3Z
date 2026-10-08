# rev0021 worklog

## Target

The planned target was **SHARE-SCAN-CACHE-PROVENANCE / U-248**.

## Work completed

- Traced `shares.py` across `3.3.10`, `3.3.x`, and `master`.
- Built a maintainer-style pytest witness for the mtime-only cache reuse behavior.
- Ran the witness across all three archived source lanes.
- Performed public-overlap searching for share rescans, mtimes, cached metadata, and `old_mtimes`/`old_files` terms.
- Reclassified U-248 as public/direct-overlap rather than fresh.
- Refactored U-248 away from U-198/U-107/U-251 while preserving their coherent fix ordering.

## Result

```text
github-tag-3.3.10:   5 passed
github-branch-3.3.x: 5 passed
github-branch-master: 5 passed
```

U-248 is verified, but not strict-promoted. It is a public-overlap regression-hardening item and a supporting scanner-cache provenance fix.

## Next target

Move to **TRANSFER-COMPLETE-LIFETIME / U-269**. It was source-confirmed earlier but not maintainer-packaged as tightly as U-123/PB-01/Search/U-248. The narrow question is whether a successful advertised-size upload should keep an active upload slot/socket indefinitely if the downloader stops reading or refuses to close.
