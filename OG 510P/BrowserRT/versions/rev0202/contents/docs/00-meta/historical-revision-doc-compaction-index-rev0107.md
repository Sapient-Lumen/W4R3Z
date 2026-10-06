# Historical revision doc compaction index — rev0107

Status: passed.

This linked package compacted old revision-suffixed docs that are not explicitly referenced by tool sources. Current `rev0107` docs and historical docs named directly by executable audits were preserved.

- historical rev docs scanned: 226
- tombstoned docs: 213
- preserved referenced docs: 13
- original tombstoned bytes: 570601
- tombstone bytes: 125922
- estimated savings: 444679

Compacted receipt counts, samples, and a digest of the original per-file receipt set live in `artifacts/datacube-audit/REV0107-HISTORICAL-REVISION-DOC-COMPACTION.json`.

Non-claim: tombstones preserve path continuity and hash receipts, not original prose.
