# 923. Source-byte host slices and priority-policy refactor

**Track:** Shared / source-byte completion / operator-routing refactor

**Revision:** `v885`  
**Status:** synthetic-release only; no live-pilot, legal, certification, source-currentness, source-byte cache completeness, or public-voter-instruction claim.

The riskiest unfinished lane is still source-byte completion. The count is not improved by this revision and should not be presented as improved: `118` pinned source-byte rows exist, `13` have valid receipts, and `105` remain receipt-missing. The point of this revision is to reduce the chance that the first unresolved batch stalls during real acquisition.

## What changed

`v885` adds host-scoped workpacks for current batch `01`:

- `artifacts/reports/source-byte-batch-host-slices-rev0885.json`
- `artifacts/source_byte_cache_intake/host_slices/`
- `scripts/build_source_byte_batch_host_slices.py`
- `scripts/check_source_byte_batch_host_slices.py`

The largest first slice is the same-host `www.eac.gov` group. That lets an operator run the highest-yield host group first, then route failures/retries by host without hand-editing the governed batch file. The slices are still strict `.sha256` expectation files; they fetch no network bytes, write no receipts, and bundle no third-party source bytes.

## Operator shape

Run a host slice on a network-capable host with an external cache directory:

```sh
python3 scripts/fetch_source_byte_batch.py \
  --batch-file artifacts/source_byte_cache_intake/host_slices/source-byte-cache-host-slice-rev0885-batch01-01-www.eac.gov.sha256 \
  --cache-dir /path/to/external-source-cache \
  --write-receipts \
  --write-report \
  --report-path artifacts/reports/source-byte-cache-host-slice-rev0885-batch01-01-www.eac.gov.fetch-report.json
```

After a partial host or full-batch attempt, keep using the unresolved-row follow-up builder rather than editing `.sha256` files by hand:

```sh
python3 scripts/build_source_byte_batch_followup.py \
  --attempt-report /path/to/attempt-report.json \
  --write
```

## Refactor performed

The source-byte priority policy was duplicated across the acquisition queue, intake-manifest builder, and external-cache receipt scanner. `v885` moves that policy into `tools/source_byte_priority.py` and routes those three surfaces through the shared function. That is a small code refactor, but it prevents a serious operational failure mode: queue order and batch handoff order drifting while every individual file still looks valid.

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
