# Cooperation Benchmark Card Inventory

Generated from schema-valid cooperation benchmark cards and compact freeze/delta receipts found in the repository. Freeze and delta status both fail closed on receipt drift.

- card_count: 2
- claim_ready_card_count: 2
- frozen_card_count: 2
- freeze_drift_card_count: 0
- delta_drift_card_count: 0
- latest_known_card_count: 1
- freeze_receipt_count: 2
- verified_freeze_receipt_count: 2
- drifted_freeze_receipt_count: 0
- delta_receipt_count: 1
- verified_delta_receipt_count: 1
- drifted_delta_receipt_count: 0
- orphan_freeze_receipt_count: 0
- orphan_delta_receipt_count: 0

## Cards

| id | path | claim_ready | frozen | freeze_drift | delta_drift | latest_known | predecessors | successors |
|---|---|---:|---:|---:|---:|---:|---|---|
| `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer` | `examples/snapshots/cooperation_benchmark_card_example.json` | yes | yes | no | no | no | — | cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer-v2 |
| `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer-v2` | `examples/snapshots/cooperation_benchmark_card_example_v2.json` | yes | yes | no | no | yes | cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer | — |

## Freeze receipts

| receipt_path | card_id | card_path | claim_ready | matches_current_surface | drift_reason_codes |
|---|---|---|---:|---:|---|
| `examples/snapshots/cooperation_benchmark_card_example.freeze_receipt.json` | `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer` | `examples/snapshots/cooperation_benchmark_card_example.json` | yes | yes | — |
| `examples/snapshots/cooperation_benchmark_card_example_v2.freeze_receipt.json` | `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer-v2` | `examples/snapshots/cooperation_benchmark_card_example_v2.json` | yes | yes | — |

## Delta receipts

| receipt_path | old_card_id | new_card_id | claim_surface_changed | matches_current_surface | drift_reason_codes |
|---|---|---|---:|---:|---|
| `examples/snapshots/cooperation_benchmark_card_example.delta_receipt.json` | `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer` | `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer-v2` | yes | yes | — |

## Latest claim-ready cards

- `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer-v2`

