# Cooperation Benchmark Card Control Plane

Generated fused status surface for compact cooperation benchmark cards. This is the one-shot inheritor reentry surface over the inventory, heads, review queue, citation surface, and handoff pack.

- verdict: `ready`
- lineage_count: 1
- citation_ready_lineage_count: 1
- unresolved_lineage_count: 0
- review_item_count: 0
- macro_review_lineage_count: 0
- handoff_ready_lineage_count: 1
- verified_freeze_receipt_count: 2
- verified_delta_receipt_count: 1
- scope_manifest_sha256: `aab567dd654ea003a86ed735c181cd0d76bbe23c18873f7e09797e7a6b4f89ea`
- scope_path_count: 137
- available_execution_lane_count: 1
- blocked_execution_lane_count: 1
- recommended_next_command: `./grpy ./scripts/test/check_cooperation_benchmark_card_control_plane.py`
- recommended_next_command_lane_id: `python-integrity`
- recommended_next_command_available: true
- focus_selector_kind: `review_item_count_then_warning_reason_count_then_citation_reason_count_then_lineage_id`
- focus_lineage_id: `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer`
- focus_operational_head_card_id: `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer-v2`
- focus_operational_head_card_path: `examples/snapshots/cooperation_benchmark_card_example_v2.json`
- focus_citation_head_card_id: `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer-v2`
- focus_citation_head_card_path: `examples/snapshots/cooperation_benchmark_card_example_v2.json`
- focus_primary_open_path: `examples/snapshots/cooperation_benchmark_card_example_v2.md`
- focus_primary_open_target: `examples/snapshots/cooperation_benchmark_card_example_v2.md` (`primary-open`, `citation-rendered-markdown`, `operational-rendered-markdown`)
- focus_primary_verify_command: `./grpy ./scripts/test/check_cooperation_benchmark_card_citation_surface.py`
- focus_primary_verify_target: `artifacts/reports/cooperation_benchmark_card_citation_surface.json` (`primary-verify-target`, `citation-surface-report`)
- focus_primary_verify_target_bytes: 1480
- focus_primary_verify_target_sha256: `067443d7a469974af5ed1aa0f8d988c577ae196c361d824cd6e0a06596fc9e9c`
- focus_primary_verify_target_citation_entry_count: 1
- focus_primary_verify_target_citation_lineage_count: 1
- focus_primary_verify_target_unresolved_lineage_count: 0
- focus_primary_verify_target_scale_summary: Citation surface report with citation_entry_count=1, citation_lineage_count=1, unresolved_lineage_count=0.
- focus_primary_verify_subject_role_code: `citation-surface-report`
- focus_primary_verify_intent_summary: Verify citation surface report.
- focus_primary_verify_outcome_summary: Expect clean validator exit for citation surface report.
- focus_primary_verify_effect_code: `read-only-check`
- focus_primary_refresh_command: `./grpy ./scripts/report/build_cooperation_benchmark_card_inventory.py --write`
- focus_primary_refresh_target: `artifacts/reports/cooperation_benchmark_card_inventory.json` (`primary-refresh-target`, `inventory-report`)
- focus_primary_refresh_target_bytes: 5630
- focus_primary_refresh_target_sha256: `f73e546359b15827da23c31e4e1f1bb763e781cde461c363e08f2624405f1cf5`
- focus_primary_refresh_target_card_count: 2
- focus_primary_refresh_target_verified_delta_receipt_count: 1
- focus_primary_refresh_target_latest_known_card_count: 1
- focus_primary_refresh_target_scale_summary: Inventory report with card_count=2, verified_delta_receipt_count=1, latest_known_card_count=1.
- focus_primary_refresh_subject_role_code: `inventory-report`
- focus_primary_refresh_intent_summary: Refresh inventory report.
- focus_primary_refresh_outcome_summary: Expect inventory report to be rewritten in place.
- focus_primary_refresh_effect_code: `in-place-report-rewrite`
- focus_open_targets: `examples/snapshots/cooperation_benchmark_card_example_v2.md` (`primary-open`, `citation-rendered-markdown`, `operational-rendered-markdown`); `examples/snapshots/cooperation_benchmark_card_example_v2.json` (`citation-card`, `operational-card`)
- focus_summary: Only retained lineage present; this is the first inspection target once the ready surface is verified.

## Lineage summary

| lineage_id | operational_head | citation_head | citation_ready | handoff_ready | review_items | review_reason_codes | warning_reason_codes | citation_reason_codes |
|---|---|---|---:|---:|---:|---|---|---|
| `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer` | `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer-v2` | `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer-v2` | true | true | 0 | — | — | — |

## Report bindings

| role | path | bytes | sha256 |
|---|---|---:|---|
| `inventory-report` | `artifacts/reports/cooperation_benchmark_card_inventory.json` | 5630 | `f73e546359b15827da23c31e4e1f1bb763e781cde461c363e08f2624405f1cf5` |
| `heads-report` | `artifacts/reports/cooperation_benchmark_card_heads.json` | 1872 | `ad22c77b27b232b63c01bf782d080f6df4a3612ac7b1e9133461f14ae149e193` |
| `review-queue-report` | `artifacts/reports/cooperation_benchmark_card_review_queue.json` | 422 | `85ddd1c89fab4bd32d00a7c0b61f9da298f3e7079fc10c2ab31f28902c527c04` |
| `macro-review-queue-report` | `artifacts/reports/cooperation_benchmark_card_macro_review_queue.json` | 490 | `54c999cb585f2d8ca505d290d90eeaeaf42542c57a88460f69032dd36c2fb2aa` |
| `citation-surface-report` | `artifacts/reports/cooperation_benchmark_card_citation_surface.json` | 1480 | `067443d7a469974af5ed1aa0f8d988c577ae196c361d824cd6e0a06596fc9e9c` |
| `handoff-pack-report` | `artifacts/reports/cooperation_benchmark_card_handoff_pack.json` | 12588 | `2347ed6eb6ef8222f704635a0ef078718d94c1d2706b3136b1ea54e5b496ae8f` |
| `execution-lanes-report` | `artifacts/reports/cooperation_benchmark_card_execution_lanes.json` | 3740 | `45c55918de5b055d3765a06c2bba1ea8345d08a9f53107c9372f739aa37ab5a3` |
| `taxonomy-report` | `artifacts/reports/cooperation_benchmark_card_taxonomy.json` | 26178 | `70db60f94d65d5cafac961758686c074d9e19dd5708af37d1b1509f276680698` |
| `scope-surface-report` | `artifacts/reports/cooperation_benchmark_card_scope_surface.json` | 49683 | `beee4faac05ef530fe7c1e7809d7d20d746ceacb856f30d798b7c10759f7ec47` |

## Recommended entrypoints

- `./grpy ./scripts/report/build_cooperation_benchmark_card_taxonomy.py --write`
- `./grpy ./scripts/report/build_cooperation_benchmark_card_scope_surface.py --write`
- `./grpy ./scripts/report/build_cooperation_benchmark_card_execution_lanes.py --write`
- `./grpy ./scripts/report/build_cooperation_benchmark_card_control_plane.py --write`
- `./grpy ./scripts/report/build_cooperation_benchmark_card_next_action_witness.py --write`
- `./grpy ./scripts/report/build_cooperation_benchmark_card_next_action.py --write`
- `./grpy ./scripts/report/build_cooperation_benchmark_card_review_queue.py --write`
- `./grpy ./scripts/report/build_cooperation_benchmark_card_macro_review_queue.py --write`
- `./grpy ./scripts/report/build_cooperation_benchmark_card_citation_surface.py --write`
- `./grpy ./scripts/report/build_cooperation_benchmark_card_handoff_pack.py --write`
- `./grpy ./scripts/test/check_cooperation_benchmark_card_taxonomy.py`
- `./grpy ./scripts/test/check_cooperation_benchmark_card_scope_surface.py`
- `./grpy ./scripts/test/check_cooperation_benchmark_card_execution_lanes.py`
- `./grpy ./scripts/test/check_cooperation_benchmark_card_control_plane.py`

## Per-lineage details

### `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer`

- benchmark_names: `Toy IPD fresh-partner transfer benchmark`, `Toy IPD fresh-partner transfer benchmark (toy-agent-v2)`
- operational_head_card_id: `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer-v2`
- citation_head_card_id: `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer-v2`
- citation_ready: true
- handoff_ready: true
- review_item_count: 0
- review_item_kinds: none
- review_reason_codes: none
- primary_review_command: none
- review_commands: none
- apply_commands: none
- warning_reason_codes: none
- citation_reason_codes: none
- citation_card_path: `examples/snapshots/cooperation_benchmark_card_example_v2.json`
- handoff_pack_id: `cooperation-benchmark-card-handoff:cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer:cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer-v2`

