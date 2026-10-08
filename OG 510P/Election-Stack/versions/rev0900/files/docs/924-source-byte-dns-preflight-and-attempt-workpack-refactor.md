# 924. Source-byte DNS preflight and attempt-workpack refactor

**Track:** Shared / source-byte completion / operator-retry refactor

**Revision:** `v886`  
**Status:** synthetic-release only; no live-pilot, legal, certification, source-currentness, source-byte cache completeness, or public-voter-instruction claim.

The riskiest unfinished lane remains source-byte completion. The count is not improved by this revision: `118` pinned source-byte rows exist, `13` have valid receipts, and `105` remain receipt-missing. This revision attempted to move the first batch from plan to acquisition, but the cloudtainer resolver failed before HTTP fetch could begin.

## What changed

`v886` makes that failed acquisition attempt useful instead of opaque:

- `tools/source_byte_dns_preflight.py` now writes a current revision report instead of the old hard-coded `rev0875` path.
- `artifacts/reports/source-byte-dns-preflight-rev0886.json` records that all `8` hosts in current batch `01` failed DNS resolution in this cloudtainer.
- `artifacts/reports/source-byte-cache-host-slice-rev0886-batch01-07-www.stat.berkeley.edu.fetch-report.json` records one real fetch attempt that failed before byte retrieval with resolver error.
- `scripts/build_source_byte_batch_attempt_workpacks.py` classifies the current batch into retry workpacks rather than leaving it as one undifferentiated `20`-row batch.
- `scripts/check_source_byte_dns_preflight.py` and `scripts/check_source_byte_batch_attempt_workpacks.py` gate the shape without rerunning environment-specific DNS.

The resulting workpacks are strict `.sha256` files accepted by the real batch fetcher in plan-only mode:

- `artifacts/source_byte_cache_intake/attempt_workpacks/source-byte-attempt-workpack-rev0886-batch01-dns_blocked_fetch_error.sha256` (`1` source)
- `artifacts/source_byte_cache_intake/attempt_workpacks/source-byte-attempt-workpack-rev0886-batch01-dns_blocked_preflight.sha256` (`19` sources)

## Operator shape

The current cloudtainer is not a good place to finish this batch because DNS resolution failed for every batch `01` host. Run the classified workpacks from a network-capable operator machine with an external cache directory:

```sh
python3 scripts/fetch_source_byte_batch.py \
  --batch-file artifacts/source_byte_cache_intake/attempt_workpacks/source-byte-attempt-workpack-rev0886-batch01-dns_blocked_preflight.sha256 \
  --cache-dir /path/to/external-source-cache \
  --write-receipts \
  --write-report
```

After any real fetch/cache attempt, rebuild classified workpacks:

```sh
python3 scripts/build_source_byte_batch_attempt_workpacks.py --write
```

This keeps DNS failures, source drift, access denial, cache misses, and exact byte matches from collapsing into the same bucket.

## Refactor performed

The DNS preflight helper had a stale, hard-coded output path: `source-byte-dns-preflight-rev0875.json`. That meant a current operator could run the preflight successfully and still leave the current revision with no obvious current DNS observation. The helper now derives `rev####` from `VERSION`, checks that the source-byte queue matches the same archive version, and records explicit no-HTTP/no-receipt/no-third-party-byte boundaries.

The attempt-workpack builder is the paired accounting refactor. It consumes DNS/fetch observations and emits deterministic strict `.sha256` workpacks by next-action class. That is not source-byte completion, but it prevents a common completion failure mode: repeating the same doomed mixed batch from the same DNS-broken environment.

## What remains blocked

This revision still does not establish any of the following:

- source-byte cache completeness;
- current state/local authority;
- current voter instruction;
- legal reliance;
- public-release authorization;
- production signer authority;
- independent validation;
- certification;
- live-pilot readiness.
