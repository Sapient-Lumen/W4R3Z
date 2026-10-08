# Audited backlog addendum — rev0021

## SHARE-SCAN-CACHE-01 / U-248

**Status:** verified across `3.3.10`, `3.3.x`, and `master`; **not strict-promoted**; **not fresh**.

rev0021 converted U-248 from a queued target into a current-source maintainer-style witness. The behavior exists in all three archived source lanes: the share scanner reuses cached file metadata when `path + st_mtime` matches prior databases, without checking size or file identity.

The public-overlap result changed the presentation: this is no longer allowed to sit in a “fresh/no direct public mention” mental bucket. A public #2447 search result/comment directly overlaps the shares.py stat-reread/mtime behavior, and #2447 also reports adjacent upload-size/completion symptoms.

Recommended handling: keep as verified audited backlog and as support for a coherent transfer/file-provenance patch series. Do not include in the strict/high-priority document unless a separate stronger consequence is later proven.

## Strict document status

```text
3 promoted report-candidates
0 production-ready disclosure texts
0 new strict promotions in rev0021
```
