# Cooperation Benchmark Card Next Action Witness

Generated arbitration witness for compact-card first reentry. This preserves the live candidate family, winning priority bucket, tie set, stable selector, and current focus lineage so the recommended next command does not silently become more authoritative than its evidence.

- control_plane_verdict: `ready`
- candidate_count: 1
- winning_priority_bucket: 90
- winning_priority_label: `verify-ready-surface`
- winning_candidate_count: 1
- winner_uniqueness: `unique-highest-priority`
- selected_candidate_id: `verify_ready_surface`
- selected_next_command: `./grpy ./scripts/test/check_cooperation_benchmark_card_control_plane.py`
- selected_next_command_target: `artifacts/reports/cooperation_benchmark_card_control_plane.json` (`control-plane-report`)
- selected_next_command_open_path: `docs/COOPERATION_BENCHMARK_CARD_CONTROL_PLANE.md`
- selected_next_command_open_target: `docs/COOPERATION_BENCHMARK_CARD_CONTROL_PLANE.md` (`selected-next-command-open`)
- selected_next_command_open_target_bytes: 8374
- selected_next_command_open_target_sha256: `b6dd98560bbc3ccb61736ab295e5cc17f6241a70f08209ee8c31b7825b1cbb1c`
- selected_fallback_command: `./grpy ./scripts/test/check_cooperation_benchmark_card_citation_surface.py`
- selected_fallback_command_target: `artifacts/reports/cooperation_benchmark_card_citation_surface.json` (`citation-surface-report`)
- selected_fallback_command_subject_role_code: `citation-surface-report`
- selected_fallback_command_intent_summary: Verify citation surface report.
- selected_fallback_command_outcome_summary: Expect clean validator exit for citation surface report.
- selected_fallback_command_effect_code: `read-only-check`
- selected_fallback_command_open_path: `docs/COOPERATION_BENCHMARK_CARD_CITATION_SURFACE.md`
- selected_fallback_command_open_target: `docs/COOPERATION_BENCHMARK_CARD_CITATION_SURFACE.md` (`selected-fallback-command-open`)
- selected_fallback_command_open_target_bytes: 835
- selected_fallback_command_open_target_sha256: `5cefdcb187dcced2852d657bb88cad0f332ac75d288f585c77936a4a68e598c1`
- selected_fallback_command_target_bytes: 1480
- selected_fallback_command_target_sha256: `067443d7a469974af5ed1aa0f8d988c577ae196c361d824cd6e0a06596fc9e9c`
- selected_fallback_command_target_scale_summary: Citation surface report with citation_entry_count=1, citation_lineage_count=1, unresolved_lineage_count=0.
- selected_fallback_command_target_citation_entry_count: 1
- selected_fallback_command_target_citation_lineage_count: 1
- selected_fallback_command_target_unresolved_lineage_count: 0
- selected_next_command_target_bytes: 9736
- selected_next_command_target_sha256: `3865f057e7924edb8cec0b46f5983ca0e9eee4b8f94b6e6de385fec75b7f4000`
- selected_next_command_target_scale_summary: Control plane report with lineage_count=1, review_item_count=0, unresolved_lineage_count=0.
- selected_next_command_target_lineage_count: 1
- selected_next_command_target_review_item_count: 0
- selected_next_command_target_unresolved_lineage_count: 0
- selected_next_command_subject_role_code: `control-plane-report`
- selected_next_command_intent_summary: Verify control plane report.
- selected_next_command_outcome_summary: Expect clean validator exit for control plane report.
- selected_next_command_effect_code: `read-only-check`
- fallback_command: `./grpy ./scripts/report/build_cooperation_benchmark_card_control_plane.py --write`
- focus_selector_kind: `review_item_count_then_warning_reason_count_then_citation_reason_count_then_lineage_id`
- focus_lineage_id: `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer`
- focus_operational_head_card_path: `examples/snapshots/cooperation_benchmark_card_example_v2.json`
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

## Selected command ladder

### Step 1

- command: `./grpy ./scripts/test/check_cooperation_benchmark_card_control_plane.py`
- required_lane_id: `python-integrity`
- required_lane_available: true
- required_lane_summary: Build and verify the compact-card inventory, heads, citation, handoff, control-plane, next-action, and execution-lane surfaces.
- required_lane_blocking_reason_codes: none
- target: `artifacts/reports/cooperation_benchmark_card_control_plane.json` (`control-plane-report`)
- open_path: `docs/COOPERATION_BENCHMARK_CARD_CONTROL_PLANE.md`
- open_target: `docs/COOPERATION_BENCHMARK_CARD_CONTROL_PLANE.md` (`selected-command-ladder-open`)
- open_target_bytes: 8374
- open_target_sha256: `b6dd98560bbc3ccb61736ab295e5cc17f6241a70f08209ee8c31b7825b1cbb1c`
- target_bytes: 9736
- target_sha256: `3865f057e7924edb8cec0b46f5983ca0e9eee4b8f94b6e6de385fec75b7f4000`
- target_scale_summary: Control plane report with lineage_count=1, review_item_count=0, unresolved_lineage_count=0.
- target_lineage_count: 1
- target_review_item_count: 0
- target_unresolved_lineage_count: 0
- subject_role_code: `control-plane-report`
- intent_summary: Verify control plane report.
- outcome_summary: Expect clean validator exit for control plane report.
- effect_code: `read-only-check`

### Step 2

- command: `./grpy ./scripts/test/check_cooperation_benchmark_card_citation_surface.py`
- required_lane_id: `python-integrity`
- required_lane_available: true
- required_lane_summary: Build and verify the compact-card inventory, heads, citation, handoff, control-plane, next-action, and execution-lane surfaces.
- required_lane_blocking_reason_codes: none
- target: `artifacts/reports/cooperation_benchmark_card_citation_surface.json` (`citation-surface-report`)
- open_path: `docs/COOPERATION_BENCHMARK_CARD_CITATION_SURFACE.md`
- open_target: `docs/COOPERATION_BENCHMARK_CARD_CITATION_SURFACE.md` (`selected-command-ladder-open`)
- open_target_bytes: 835
- open_target_sha256: `5cefdcb187dcced2852d657bb88cad0f332ac75d288f585c77936a4a68e598c1`
- target_bytes: 1480
- target_sha256: `067443d7a469974af5ed1aa0f8d988c577ae196c361d824cd6e0a06596fc9e9c`
- target_scale_summary: Citation surface report with citation_entry_count=1, citation_lineage_count=1, unresolved_lineage_count=0.
- target_citation_entry_count: 1
- target_citation_lineage_count: 1
- target_unresolved_lineage_count: 0
- subject_role_code: `citation-surface-report`
- intent_summary: Verify citation surface report.
- outcome_summary: Expect clean validator exit for citation surface report.
- effect_code: `read-only-check`

### Step 3

- command: `./grpy ./scripts/test/check_cooperation_benchmark_card_handoff_pack.py`
- required_lane_id: `python-integrity`
- required_lane_available: true
- required_lane_summary: Build and verify the compact-card inventory, heads, citation, handoff, control-plane, next-action, and execution-lane surfaces.
- required_lane_blocking_reason_codes: none
- target: `artifacts/reports/cooperation_benchmark_card_handoff_pack.json` (`handoff-pack-report`)
- open_path: `docs/COOPERATION_BENCHMARK_CARD_HANDOFF_PACK.md`
- open_target: `docs/COOPERATION_BENCHMARK_CARD_HANDOFF_PACK.md` (`selected-command-ladder-open`)
- open_target_bytes: 10012
- open_target_sha256: `ee7c0fae239988486283ee5deed3ddb7ddbf6d7a48220376487775798e7085c3`
- target_bytes: 12588
- target_sha256: `2347ed6eb6ef8222f704635a0ef078718d94c1d2706b3136b1ea54e5b496ae8f`
- target_scale_summary: Handoff pack report with pack_count=1, total_file_count=17, unresolved_lineage_count=0.
- target_unresolved_lineage_count: 0
- target_pack_count: 1
- target_total_file_count: 17
- subject_role_code: `handoff-pack-report`
- intent_summary: Verify handoff pack report.
- outcome_summary: Expect clean validator exit for handoff pack report.
- effect_code: `read-only-check`

### Step 4

- command: `./grpy ./scripts/report/build_cooperation_benchmark_card_control_plane.py --write`
- required_lane_id: `python-integrity`
- required_lane_available: true
- required_lane_summary: Build and verify the compact-card inventory, heads, citation, handoff, control-plane, next-action, and execution-lane surfaces.
- required_lane_blocking_reason_codes: none
- target: `artifacts/reports/cooperation_benchmark_card_control_plane.json` (`control-plane-report`)
- open_path: `docs/COOPERATION_BENCHMARK_CARD_CONTROL_PLANE.md`
- open_target: `docs/COOPERATION_BENCHMARK_CARD_CONTROL_PLANE.md` (`selected-command-ladder-open`)
- open_target_bytes: 8374
- open_target_sha256: `b6dd98560bbc3ccb61736ab295e5cc17f6241a70f08209ee8c31b7825b1cbb1c`
- target_bytes: 9736
- target_sha256: `3865f057e7924edb8cec0b46f5983ca0e9eee4b8f94b6e6de385fec75b7f4000`
- target_scale_summary: Control plane report with lineage_count=1, review_item_count=0, unresolved_lineage_count=0.
- target_lineage_count: 1
- target_review_item_count: 0
- target_unresolved_lineage_count: 0
- subject_role_code: `control-plane-report`
- intent_summary: Refresh control plane report.
- outcome_summary: Expect control plane report to be rewritten in place.
- effect_code: `in-place-report-rewrite`

## Candidate summary

| candidate_id | action_kind | priority_bucket | lineage_id | selected | reason_codes | next_command |
|---|---|---:|---|---:|---|---|
| `verify_ready_surface` | `verify_ready_surface` | 90 | — | true | — | `./grpy ./scripts/test/check_cooperation_benchmark_card_control_plane.py` |

## Tie set

- `verify_ready_surface`

## Report bindings

| role | path | bytes | sha256 |
|---|---|---:|---|
| `control-plane-report` | `artifacts/reports/cooperation_benchmark_card_control_plane.json` | 9736 | `3865f057e7924edb8cec0b46f5983ca0e9eee4b8f94b6e6de385fec75b7f4000` |
| `macro-review-queue-report` | `artifacts/reports/cooperation_benchmark_card_macro_review_queue.json` | 490 | `54c999cb585f2d8ca505d290d90eeaeaf42542c57a88460f69032dd36c2fb2aa` |
| `execution-lanes-report` | `artifacts/reports/cooperation_benchmark_card_execution_lanes.json` | 3740 | `45c55918de5b055d3765a06c2bba1ea8345d08a9f53107c9372f739aa37ab5a3` |

## Candidate details

### `verify_ready_surface`

- action_kind: `verify_ready_surface`
- priority_bucket: 90
- priority_label: `verify-ready-surface`
- selected: true
- lineage_id: none
- summary: Compact-card citation and handoff surfaces are ready; verify the current fused surface before proceeding.
- next_command: `./grpy ./scripts/test/check_cooperation_benchmark_card_control_plane.py`
- reason_codes: none
- fallback_commands:
  - `./grpy ./scripts/test/check_cooperation_benchmark_card_control_plane.py`
  - `./grpy ./scripts/test/check_cooperation_benchmark_card_citation_surface.py`
  - `./grpy ./scripts/test/check_cooperation_benchmark_card_handoff_pack.py`
  - `./grpy ./scripts/report/build_cooperation_benchmark_card_control_plane.py --write`

