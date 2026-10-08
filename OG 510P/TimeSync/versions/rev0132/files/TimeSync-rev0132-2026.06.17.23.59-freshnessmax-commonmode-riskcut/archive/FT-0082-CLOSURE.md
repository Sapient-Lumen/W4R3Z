# FT-0082 closure — Aggregate correction authority, notification cadence, and portable correction chains

FT-0082 asked whether aggregate correction and reconciliation lineage should carry a bounded correction-authority and notification reference, and how correction chains should remain portable across compatible operators without exporting authority rosters, notification recipients, or repository topology.

rev0083 answers yes, but only as aggregate publication-interpretation metadata.

## Closed by

- `schema/aggregate-correction-authority-reference.schema.json`
- `schema/replay-transparency-audit.schema.json`
- `spec/46-aggregate-correction-authority-and-notification.md`
- `examples/evaluator/aggregate-verifier-audit-summary-p3-portable-correction-chain.json`
- `examples/discovery-request-with-aggregate-correction-authority-reference.json`
- `tools/validate_archive.py`

## Boundary decision

Correction-authority references can bind authorization, notification freshness, and compatible-operator correction-chain interpretation. They cannot export authority rosters, key material, repository topology, notification recipient identities, notification payload material, suppressed deltas, individual result identifiers, verifier identities, or external correction records as TimeSync provenance.

## Result

FT-0082 is closed in rev0083.
