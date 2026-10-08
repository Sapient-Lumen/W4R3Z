# 918 — Source-byte batch resume and selected cache-ingest firewall

**Track:** Shared

## Purpose

`v880` closes a practical completion gap in the source-byte lane. The release already had six sha256sum batch handoff files, but the receipt-writing helper still defaulted to scanning every receipt-missing pinned source. That made incremental work more error-prone: an operator trying to finish batch 01 could accidentally scan a larger cache and write receipts for unrelated rows.

This revision adds selected-batch resume behavior to the existing receipt writer:

- `scripts/source_byte_receipts_from_cache_batch.py --batch-file <batch.sha256>` limits scanning and receipt writing to the exact expected-hash/local-filename entries in that batch file.
- `scripts/check_source_byte_cache_batch_resume.py` proves the selected-batch path is current, reject-on-mismatch, and fail-closed for unsafe or non-lockfile batch entries.
- `artifacts/reports/source-byte-cache-batch-resume-rev0880.json` is the current clean-release batch01 readiness report generated without inspecting release-local cache bytes.

## Operator path

A network-capable or externally populated cache environment can now process one batch and write only that batch's receipts:

```bash
python3 scripts/source_byte_receipts_from_cache_batch.py \
  --cache-dir /path/to/external-source-cache \
  --batch-file artifacts/source_byte_cache_intake/batches/source-byte-cache-missing-receipts-rev0880-batch01.sha256 \
  --write-receipts
```

The batch file must be strict `sha256sum -c` input:

```text
<expected lockfile sha256>  <safe local cache filename>
```

The helper rejects malformed lines, unsafe filenames, duplicate batch entries, and entries whose expected hash/local filename pair does not match a pinned lockfile row. A valid cache file outside the selected batch must not become a receipt during that run.

## Gate behavior

`scripts/check_source_byte_cache_batch_resume.py` checks three things:

1. The shipped `source-byte-cache-batch-resume-rev0880.json` report is regenerated from current batch01, current `VERSION`, and `--assume-empty-cache`.
2. A temporary selected-batch smoke writes exactly one matching receipt, blocks one selected mismatch, and ignores one valid cache file outside the selected batch.
3. Tampered batch files with wrong expected hashes or unsafe filenames fail instead of producing partial reports or receipts.

## Boundary

Selected-batch resume is an operator-control improvement, not source evidence by itself. It performs no network I/O, bundles no third-party bytes, does not prove source-byte cache completeness, and is not current voter instruction, not legal advice, not public-release authorization, and not live-pilot approval.
