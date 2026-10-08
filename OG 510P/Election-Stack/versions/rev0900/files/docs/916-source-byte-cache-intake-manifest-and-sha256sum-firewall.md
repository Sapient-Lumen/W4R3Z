# 916 — Source-byte cache intake manifest and sha256sum firewall

**Track:** Shared

## Purpose

`v878` moves the source-byte completion lane one step closer to execution without inventing source evidence in a DNS-blocked cloudtainer.

Earlier revisions created a receipt pack, an acquisition queue, single-file cache receipts, and batch cache ingest. The remaining risk was operator handoff: a network-capable maintainer still had to translate the JSON queue into concrete files to fetch and verify.

This revision adds a sha256sum-ready intake manifest:

- `scripts/build_source_byte_cache_intake_manifest.py`
- `scripts/check_source_byte_cache_intake_manifest.py`
- `artifacts/reports/source-byte-cache-intake-manifest-rev0878.json`
- `artifacts/source_byte_cache_intake/source-byte-cache-missing-receipts-rev0878.sha256`

The `.sha256` file contains one line per receipt-missing pinned source:

```text
<expected lockfile sha256>  <safe local cache filename>
```

A maintainer can use it outside the release archive with a populated source cache:

```bash
cd /path/to/external-source-cache
sha256sum -c /path/to/source-byte-cache-missing-receipts-rev0878.sha256
```

Only after exact SHA-256 matches should the archive-side batch receipt helper be run:

```bash
python3 scripts/source_byte_receipts_from_cache_batch.py \
  --cache-dir /path/to/external-source-cache \
  --write-receipts
```

## Gate behavior

`scripts/check_source_byte_cache_intake_manifest.py` verifies that the current intake report and sha256sum file are generated from the current lockfile, receipt report, and acquisition queue. It also checks that:

- every entry uses a safe basename only;
- the entry count equals the receipt-missing pinned-source count;
- the next batch matches `artifacts/reports/source-byte-acquisition-queue.json`;
- the current batch-ingest candidate count agrees;
- the shipped manifest carries no-network/no-bundled-bytes/non-instruction boundaries;
- `sha256sum -c` against an empty cache fails as missing external bytes, not as a false pass;
- wrong bytes under a real intake filename are reported as a mismatch and cannot become a receipt.

## Boundary

The intake manifest is an expectation file, not source-byte evidence. It does not fetch the network, does not bundle third-party bytes, does not prove source-byte cache completeness, and is not current voter instruction, not legal advice, not public-release authorization, and not live-pilot approval.
