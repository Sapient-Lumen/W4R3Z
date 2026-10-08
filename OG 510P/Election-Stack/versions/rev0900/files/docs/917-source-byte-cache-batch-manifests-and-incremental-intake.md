# 917 — Source-byte cache batch manifests and incremental intake

**Track:** Shared

## Purpose

`v879` keeps the source-byte completion lane focused on execution rather than more policy text. The remaining receipt-missing pinned-source queue is still too large to handle safely as one manual operation, so this revision splits the current sha256sum intake handoff into deterministic operator batches.

New files:

- `scripts/build_source_byte_cache_batch_manifests.py`
- `scripts/check_source_byte_cache_batch_manifests.py`
- `artifacts/reports/source-byte-cache-batch-manifests-rev0879.json`
- `artifacts/source_byte_cache_intake/batches/source-byte-cache-missing-receipts-rev0879-batch01.sha256`
- `artifacts/source_byte_cache_intake/batches/source-byte-cache-missing-receipts-rev0879-batch02.sha256`
- `artifacts/source_byte_cache_intake/batches/source-byte-cache-missing-receipts-rev0879-batch03.sha256`
- `artifacts/source_byte_cache_intake/batches/source-byte-cache-missing-receipts-rev0879-batch04.sha256`
- `artifacts/source_byte_cache_intake/batches/source-byte-cache-missing-receipts-rev0879-batch05.sha256`
- `artifacts/source_byte_cache_intake/batches/source-byte-cache-missing-receipts-rev0879-batch06.sha256`

Each batch file uses the same `sha256sum -c` line format as the master intake file:

```text
<expected lockfile sha256>  <safe local cache filename>
```

## Operator path

A network-capable or out-of-band acquisition environment can process one batch at a time:

```bash
cd /path/to/external-source-cache
sha256sum -c /path/to/source-byte-cache-missing-receipts-rev0879-batch01.sha256
```

After exact byte matches exist in the external cache, the archive-side batch receipt helper remains the only receipt-writing path:

```bash
python3 scripts/source_byte_receipts_from_cache_batch.py \
  --cache-dir /path/to/external-source-cache \
  --write-receipts
```

Mismatched, missing, unsafe, duplicate, or unreadable cache files remain blocked and must not become receipts.

## Gate behavior

`scripts/check_source_byte_cache_batch_manifests.py` verifies that the shipped batch report and batch files are current for `VERSION`, reconstruct the master intake file exactly, cover each receipt-missing pinned source once, carry no-network/no-bundled-bytes boundaries, and use contiguous current-revision batch filenames.

The current-revision fixture sweep also checks this batch-manifest surface so a future version bump cannot leave stale batch handoff files behind.

## Boundary

These batch files are expectation manifests, not source evidence. They perform no network I/O, bundle no third-party bytes, do not prove source-byte cache completeness, and are not current voter instruction, not legal advice, not public-release authorization, and not live-pilot approval.
