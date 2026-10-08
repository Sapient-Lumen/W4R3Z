# 925. Source-byte operator workplan and workpack-parser refactor

**Track:** Shared / source-byte completion / operator-workplan refactor

**Revision:** `v887`  
**Status:** synthetic-release only; no live-pilot, legal, certification, source-currentness, source-byte cache completeness, or public-voter-instruction claim.

The riskiest unfinished lane remains source-byte completion. This revision does not claim evidence acquisition progress: the current count remains `118` pinned source-byte rows, `13` valid receipts, and `105` receipt-missing rows. The practical move is to reduce the chance that the remaining work stalls because the cloudtainer cannot resolve batch `01` hosts.

## What changed

`v887` adds a current operator workplan:

- `scripts/build_source_byte_operator_workplan.py`
- `scripts/check_source_byte_operator_workplan.py`
- `artifacts/reports/source-byte-operator-workplan-rev0887.json`

The report joins the current receipt status, batch manifests, DNS preflight, host slices, classified attempt workpacks, and exact-cache return commands. It is explicitly no-network and writes no receipts; it tells a network-capable operator what to run outside this DNS-blocked cloudtainer and how to return only exact-SHA-256-matching cache files into receipts.

The highest-yield first move is the largest same-host slice:

```sh
python3 scripts/fetch_source_byte_batch.py \
  --batch-file artifacts/source_byte_cache_intake/host_slices/source-byte-cache-host-slice-rev0887-batch01-01-www.eac.gov.sha256 \
  --cache-dir /path/to/external-source-cache \
  --write-receipts \
  --write-report \
  --report-path artifacts/reports/source-byte-cache-host-slice-rev0887-batch01-01-www.eac.gov.fetch-report.json
```

After bytes are present in an external cache, receipt import remains exact-hash-gated:

```sh
python3 scripts/source_byte_receipts_from_cache_batch.py \
  --batch-file artifacts/source_byte_cache_intake/batches/source-byte-cache-missing-receipts-rev0887-batch01.sha256 \
  --cache-dir /path/to/external-source-cache \
  --write-receipts \
  --write-report
```

## Audit/refactor performed

Strict `.sha256` workpack parsing was duplicated across source-byte handoff builders. That was a real maintenance risk: one parser could accept an unsafe or stale workpack while another rejected it. This revision adds:

- `tools/source_byte_workpack_common.py`
- `scripts/check_source_byte_workpack_common.py`

The shared parser rejects unsafe basenames, duplicate lines, duplicate local filenames, empty workpacks, and entries not pinned in the external-source lockfile. The host-slice builder and attempt-workpack builder now use this shared parser.

## Remaining blocker

The current cloudtainer still cannot prove source-byte completion. A valid receipt requires the exact bytes named by the lockfile and an observed SHA-256 match. Browser snippets, rendered text, partial downloads, or URL liveness checks are not receipts. Until the `105` missing rows are fetched or cache-verified by exact hash, the no-go remains unchanged.

## Non-claims

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
