# Evidence ledger schema

This file describes the fields future ledgers should converge toward even if old ledgers remain heterogeneous.

## Core fields
- `artifact_kind`
- `artifact_id`
- `created_at`
- `surface_key`
- `browser_lane`
- `workflow_keys`
- `path`
- `summary`

## Optional but highly useful fields
- `support_tier_hint`
- `drift_severity`
- `related_artifact_ids`
- `comparison_ref`
- `record_ref`
- `release_gate_ref`
- `action_id`
- `result`

## Normalization rule
Do not wait for every historical artifact to match this schema before using it. The goal is forward discipline and visible mapping, not immediate total migration.

## Why this matters
A future implementer should be able to answer:
- what artifact proves this claim?
- what surface and lane does it belong to?
- what workflow was being exercised?
- what related comparison or release-gate artifact exists?
