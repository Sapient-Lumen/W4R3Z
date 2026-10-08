# 914 — Source-byte cache batch ingest and mismatch firewall

**Track:** B

## Purpose

`v876` converts the source-byte lane from one-at-a-time receipt work into a batchable operator path. The remaining receipt gap is too large to close by hand-copying source IDs through individual commands. Operators need a single scan over an external cache directory that can safely identify three cases:

1. the cache file is missing;
2. the cache file exists but does not match the lockfile SHA-256;
3. the cache file exists, matches the lockfile SHA-256, and can become an `operator_cache_file` receipt.

The new batch helper is `scripts/source_byte_receipts_from_cache_batch.py`. It performs no network I/O and does not copy source bytes into the release tree. It only reads an external cache directory and writes small JSON receipts for exact SHA-256 matches.

## Release-gated readiness

The release-gated report is `artifacts/reports/source-byte-cache-batch-ingest-rev0876.json`. It is generated with `--assume-empty-cache`, so it is deterministic in clean release environments and cannot silently depend on an operator's local `evidence/cache/` contents.

The gate `scripts/check_source_byte_cache_batch_ingest.py` verifies that the shipped readiness report matches the current `VERSION`, current source-byte acquisition queue, and current receipt-validation report. It also smoke-tests a temporary lockfile/cache pair where one file matches and one file mismatches. The matching file must produce an `operator_cache_file` receipt; the mismatched file must not produce a receipt.

## Operator workflow outside the release ZIP

The intended batch workflow is:

```bash
python3 scripts/source_byte_receipts_from_cache_batch.py \
  --cache-dir /path/to/source-cache \
  --json
```

After reviewing missing and mismatched rows, an operator can write receipts for exact matches:

```bash
python3 scripts/source_byte_receipts_from_cache_batch.py \
  --cache-dir /path/to/source-cache \
  --write-receipts \
  --retrieved-at-utc 2026-06-13T00:00:00Z \
  --json
```

The cache directory must stay outside release ZIP scope. Release manifests exclude `evidence/cache/`, but operators should still prefer an external cache path when source files are large.

## Boundaries

This lane proves only byte identity against pinned rows in `evidence/lock/external-sources.toml`. It is not current voter instruction, not legal advice, not source-byte cache completeness, not public-release authorization, and not live-pilot approval.

For quarantined state/local examples, byte capture alone is still insufficient. Adopter-specific responsible office, public help route, jurisdiction scope, conflict review, and human approval evidence remain required before any public-answer promotion can be considered.
