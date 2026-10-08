# 919 — Source-byte batch status and stale-batch firewall

**Track:** Shared

## Purpose

`v881` adds a current progress view for the source-byte cache completion lane. The archive already had source-byte receipts, an acquisition queue, a master sha256sum intake file, per-batch sha256sum files, and selected-batch resume mode. What was missing was a small report that joins those lanes and says which batch is actually next, while failing if batch handoffs silently become stale after receipts are added.

This revision adds:

- `scripts/build_source_byte_cache_batch_status.py`, which joins the receipt validation report, acquisition queue, and current batch manifests.
- `scripts/check_source_byte_cache_batch_status.py`, which makes that joined status a release-gate artifact.
- `artifacts/reports/source-byte-cache-batch-status-rev0881.json`, which records the current first incomplete batch and per-batch missing counts.

## Current completion status

The current report records:

- `13` valid source-byte receipts retained.
- `105` pinned sources still missing receipts.
- `6` current batch files.
- `batch01` as the first incomplete batch.
- `0` bundled third-party source bytes.

The report is intentionally small: it keeps per-batch counts, the batch file path, the first and last missing source id in each batch, and priority/family summaries. It does not duplicate the full source queue.

## Stale-batch firewall

When a future operator finishes a batch and writes receipts, the batch files and intake manifests must be regenerated. Otherwise a release could keep advertising completed source ids as receipt-missing work.

The new gate fails if:

- Any receipt-present source id remains in a receipt-missing batch file.
- Any receipt-missing source id is absent from the batch files.
- Any batch file source id is not currently receipt-missing.
- Batch files contain duplicate source ids.
- The status report is stale relative to the live receipt pack, queue, or batch manifest builders.

## Operator path

The next concrete source-byte action remains batch-scoped:

```bash
python3 scripts/source_byte_receipts_from_cache_batch.py \
  --cache-dir /path/to/external-source-cache \
  --batch-file artifacts/source_byte_cache_intake/batches/source-byte-cache-missing-receipts-rev0881-batch01.sha256 \
  --write-receipts
```

After matching receipts are written, rerun the source-byte report builders and gates so the first incomplete batch advances and completed rows leave the receipt-missing batch files.

## Boundary

Batch status is progress accounting, not source evidence by itself. It performs no network I/O, bundles no third-party bytes, is not source-byte cache completeness, and is not current voter instruction, not legal advice, not public-release authorization, and not live-pilot approval.
