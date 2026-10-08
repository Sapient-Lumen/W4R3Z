# 915 — Current-revision fixture sweep and source-byte ratchet

**Track:** Shared

## Purpose

`v877` removes two repeat failure modes from the release path:

1. rev-specific fixtures existed for the previous revision but not the current `VERSION`;
2. source-byte receipt coverage could accidentally regress because the gate floor was lower than the achieved receipt count.

The new gate `scripts/check_current_revision_fixture_sweep.py` checks the current revision surfaces that have repeatedly drifted during rapid release work:

- `artifacts/reports/source-byte-cache-batch-ingest-rev0877.json`;
- `artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev0877.json`;
- `artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev0877.publication-receipt.json`;
- `artifacts/templates/packet-verification-report-example.json`;
- `artifacts/examples/evidence_packet_packet_verification_report_minimal/`;
- Example County scenario, smoke, evidence-map, and evaluator-scorecard outputs.

It writes `artifacts/reports/current-revision-fixture-sweep-rev0877.json` and fails if those files do not match `VERSION` or if the current policy receipt does not bind the current policy bytes.

## Source-byte ratchet

`v877` also tightens `scripts/check_source_byte_receipt_pack.py` to the actual current floor: `13` valid receipts and `10,421,893` observed bytes. This is not enough to claim source-cache completeness, but it prevents a future cleanup or compaction pass from silently dropping existing source-byte evidence.

The current receipt-missing queue remains the high-risk completion lane. `v877` does not invent source-byte receipts in the DNS-blocked cloudtainer. The batch cache helper still writes receipts only when operator-provided bytes exactly match the pinned SHA-256 in `evidence/lock/external-sources.toml`.

## Batch-cache overwrite guard

The v877 batch-ingest gate extends the temporary-cache smoke test. It now proves three behaviors:

1. exact matching bytes can create one `operator_cache_file` receipt;
2. mismatched bytes do not create a receipt;
3. an existing receipt is skipped without `--force`, so repeated operator runs do not overwrite evidence by accident.

## Boundaries

This revision is still synthetic-only. The fixture sweep, source-byte ratchet, and cache overwrite guard are drift controls; they are not current voter instruction, not legal advice, not source-byte cache completeness, not public-release authorization, and not live-pilot approval.
