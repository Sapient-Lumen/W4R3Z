# 921. Priority-risk source-byte batch fetch and measurement-helper fail-closed refactor

**Track:** Shared / source-byte completion / measurement helper safety

**Revision:** `v883`  
**Status:** synthetic-release only; no live-pilot, legal, certification, source-currentness, or public-voter-instruction claim.

This revision deliberately favors executable risk reduction over additional registry surface. The riskiest unfinished lane is still source-byte completion: `118` pinned sources exist, `13` have valid receipts, and `105` still lack source-byte receipts. The first incomplete handoff remains batch `1` at:

- `artifacts/source_byte_cache_intake/batches/source-byte-cache-missing-receipts-rev0883-batch01.sha256`

## What changed

`v883` adds `scripts/fetch_source_byte_batch.py`, a network-capable counterpart to the existing offline cache scanner. It consumes one strict `.sha256` batch file, selects only matching `evidence/lock/external-sources.toml` rows, fetches bytes into an external cache, verifies exact SHA-256 before cache/receipt writes, and can also run cache-only to issue receipts for already-present exact-match bytes.

The release gate exercises only offline paths:

- plan-only selection against the current batch;
- exact-match temporary cache receipt writing with no network;
- refusal to use a release-governed cache directory outside `evidence/cache/`.

Current plan report:

- `artifacts/reports/source-byte-batch-fetch-plan-rev0883.json`

Current status from that plan: `20` selected batch candidates, status counts `{'plan_only': 20}`.

## Operator execution shape

On a network-capable host with an external cache directory:

```sh
python3 scripts/fetch_source_byte_batch.py \
  --batch-file artifacts/source_byte_cache_intake/batches/source-byte-cache-missing-receipts-rev0883-batch01.sha256 \
  --cache-dir /path/to/external-source-cache \
  --write-receipts \
  --write-report
```

For an already-populated cache, use `--cache-only` to avoid network I/O and write receipts only for exact hash matches. Existing receipts are skipped unless `--force` is supplied.

The helper does **not** vendor third-party bytes into the release ZIP. It also does not prove source currentness, legal authority, public-release readiness, or live-pilot approval.

## Audit/refactor performed

Two measurement helpers were too easy to misuse as evidence-shaped placeholders. This revision refactors them into fail-closed research prototypes:

- `tools/atlas_urp_generator.py` now emits a deterministic, non-empty RIPE Atlas create-payload draft during dry-run and blocks active creation unless the operator passes both `--create` and `--operator-reviewed-payload` after ethics/plan validation.
- `tools/ooni_corroborator.py` now defaults to no-network, schema-shaped output containing a window, filters, bounded summary metadata, and pointers. It does not embed raw measurement bodies.
- `scripts/check_measurement_tool_boundaries.py` gates those fail-closed properties.

The docs were updated in `docs/117-automated-unreachability-proofs-ripe-atlas.md`, `docs/119-ooni-corroboration.md`, and `tools/README.md` to keep the operator-facing surface aligned with the code.

## Waste/refactor correction

This revision also compacts stale, non-current generated JSON report row bodies that were consuming byte budget without improving the current gates. The compaction report preserves original SHA-256 digests, original sizes, compacted sizes, and selected summary counts for each affected stale report:

- `artifacts/reports/rev0883-stale-generated-report-compaction.json`

Current `v883` source-byte, trust-policy, Example County, no-go, and handoff reports remain un-compacted and gate-readable.

## Remaining highest-risk work

1. Execute batch01 outside this DNS-limited cloudtainer, then import only exact-match receipts.
2. Repeat batches in order until the source-byte receipt gap is closed or a pinned source has a documented acquisition failure.
3. Review freshness/currentness separately; SHA-256 receipts prove observed bytes, not current law, current voter instruction, or jurisdictional authority.
4. Apply the same fail-closed refactor pattern to remaining explicit skeleton tools before moving any of them toward operator/evidence-safe maturity.

Machine-readable report:

- `artifacts/reports/risk-priority-forward-motion-rev0883.json`
