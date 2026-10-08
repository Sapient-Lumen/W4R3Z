# Cooperation Benchmark Card Next Action

Generated first-reentry surface for compact cooperation benchmark cards. This takes the fused control plane plus the arbitration witness and emits one typed next command for inheritors who need an authoritative repair-or-verify answer.

- status: `ready`
- primary_action.id: `verify_ready_surface`
- primary_action.action_kind: `verify_ready_surface`
- primary_action.lineage_id: none
- primary_action.selection_status: `unique-highest-priority`
- primary_action.required_lane_id: `python-integrity`
- primary_action.required_lane_available: true
- primary_action.required_lane_summary: Build and verify the compact-card inventory, heads, citation, handoff, control-plane, next-action, and execution-lane surfaces.
- primary_action.required_lane_blocking_reason_codes: none
- next_command: `./grpy ./scripts/test/check_cooperation_benchmark_card_control_plane.py`
- primary_action.target: `artifacts/reports/cooperation_benchmark_card_control_plane.json` (`control-plane-report`)
- primary_action.target_open_path: `docs/COOPERATION_BENCHMARK_CARD_CONTROL_PLANE.md`
- primary_action.target_open_target: `docs/COOPERATION_BENCHMARK_CARD_CONTROL_PLANE.md` (`selected-next-command-open`)
- primary_action.target_open_target_bytes: 8374
- primary_action.target_open_target_sha256: `b6dd98560bbc3ccb61736ab295e5cc17f6241a70f08209ee8c31b7825b1cbb1c`
- primary_action.fallback_command: `./grpy ./scripts/test/check_cooperation_benchmark_card_citation_surface.py`
- primary_action.fallback_target: `artifacts/reports/cooperation_benchmark_card_citation_surface.json` (`citation-surface-report`)
- primary_action.fallback_open_path: `docs/COOPERATION_BENCHMARK_CARD_CITATION_SURFACE.md`
- primary_action.fallback_open_target: `docs/COOPERATION_BENCHMARK_CARD_CITATION_SURFACE.md` (`selected-fallback-command-open`)
- primary_action.fallback_open_target_bytes: 835
- primary_action.fallback_open_target_sha256: `5cefdcb187dcced2852d657bb88cad0f332ac75d288f585c77936a4a68e598c1`
- primary_action.command_ladder_length: 4
- primary_action.fallback_subject_role_code: `citation-surface-report`
- primary_action.fallback_intent_summary: Verify citation surface report.
- primary_action.fallback_outcome_summary: Expect clean validator exit for citation surface report.
- primary_action.fallback_effect_code: `read-only-check`
- primary_action.fallback_target_bytes: 1480
- primary_action.fallback_target_sha256: `067443d7a469974af5ed1aa0f8d988c577ae196c361d824cd6e0a06596fc9e9c`
- primary_action.fallback_target_scale_summary: Citation surface report with citation_entry_count=1, citation_lineage_count=1, unresolved_lineage_count=0.
- primary_action.fallback_target_citation_entry_count: 1
- primary_action.fallback_target_citation_lineage_count: 1
- primary_action.fallback_target_unresolved_lineage_count: 0
- primary_action.target_bytes: 9736
- primary_action.target_sha256: `3865f057e7924edb8cec0b46f5983ca0e9eee4b8f94b6e6de385fec75b7f4000`
- primary_action.target_scale_summary: Control plane report with lineage_count=1, review_item_count=0, unresolved_lineage_count=0.
- primary_action.target_lineage_count: 1
- primary_action.target_review_item_count: 0
- primary_action.target_unresolved_lineage_count: 0
- primary_action.subject_role_code: `control-plane-report`
- primary_action.intent_summary: Verify control plane report.
- primary_action.outcome_summary: Expect clean validator exit for control plane report.
- primary_action.effect_code: `read-only-check`
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

## Primary action

- summary: Compact-card citation and handoff surfaces are ready; verify the current fused surface before proceeding.
- target: `artifacts/reports/cooperation_benchmark_card_control_plane.json` (`control-plane-report`)
- target_open_path: `docs/COOPERATION_BENCHMARK_CARD_CONTROL_PLANE.md`
- target_open_target: `docs/COOPERATION_BENCHMARK_CARD_CONTROL_PLANE.md` (`selected-next-command-open`)
- target_open_target_bytes: 8374
- target_open_target_sha256: `b6dd98560bbc3ccb61736ab295e5cc17f6241a70f08209ee8c31b7825b1cbb1c`
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
- fallback_target: `artifacts/reports/cooperation_benchmark_card_citation_surface.json` (`citation-surface-report`)
- fallback_open_path: `docs/COOPERATION_BENCHMARK_CARD_CITATION_SURFACE.md`
- fallback_open_target: `docs/COOPERATION_BENCHMARK_CARD_CITATION_SURFACE.md` (`selected-fallback-command-open`)
- fallback_open_target_bytes: 835
- fallback_open_target_sha256: `5cefdcb187dcced2852d657bb88cad0f332ac75d288f585c77936a4a68e598c1`
- fallback_target_bytes: 1480
- fallback_target_sha256: `067443d7a469974af5ed1aa0f8d988c577ae196c361d824cd6e0a06596fc9e9c`
- fallback_target_scale_summary: Citation surface report with citation_entry_count=1, citation_lineage_count=1, unresolved_lineage_count=0.
- fallback_target_citation_entry_count: 1
- fallback_target_citation_lineage_count: 1
- fallback_target_unresolved_lineage_count: 0
- reason_codes: none
- selected_via_witness_candidate_id: `verify_ready_surface`
- fallback_commands:
  - `./grpy ./scripts/test/check_cooperation_benchmark_card_control_plane.py`
  - `./grpy ./scripts/test/check_cooperation_benchmark_card_citation_surface.py`
  - `./grpy ./scripts/test/check_cooperation_benchmark_card_handoff_pack.py`
  - `./grpy ./scripts/report/build_cooperation_benchmark_card_control_plane.py --write`

## Primary action command ladder

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

## Entrypoint commands

- `./grpy ./scripts/report/build_cooperation_benchmark_card_next_action.py --write`
- `./grpy ./scripts/report/build_cooperation_benchmark_card_next_action_witness.py --write`
- `./grpy ./scripts/report/build_cooperation_benchmark_card_execution_lanes.py --write`
- `./grpy ./scripts/report/build_cooperation_benchmark_card_control_plane.py --write`
- `./grpy ./scripts/test/check_cooperation_benchmark_card_next_action.py`

## Verification commands

- `./grpy ./scripts/test/check_cooperation_benchmark_card_next_action.py`
- `./grpy ./scripts/test/check_cooperation_benchmark_card_next_action_witness.py`
- `./grpy ./scripts/test/check_cooperation_benchmark_card_execution_lanes.py`
- `./grpy ./scripts/test/check_cooperation_benchmark_card_control_plane.py`

## Report bindings

| role | path | bytes | sha256 |
|---|---|---:|---|
| `control-plane-report` | `artifacts/reports/cooperation_benchmark_card_control_plane.json` | 9736 | `3865f057e7924edb8cec0b46f5983ca0e9eee4b8f94b6e6de385fec75b7f4000` |
| `macro-review-queue-report` | `artifacts/reports/cooperation_benchmark_card_macro_review_queue.json` | 490 | `54c999cb585f2d8ca505d290d90eeaeaf42542c57a88460f69032dd36c2fb2aa` |
| `next-action-witness-report` | `artifacts/reports/cooperation_benchmark_card_next_action_witness.json` | 15392 | `646524a8a278ff20ea8bd9a20bd50bd7197e34688ee4d2f236841ada22e634bc` |
| `execution-lanes-report` | `artifacts/reports/cooperation_benchmark_card_execution_lanes.json` | 3740 | `45c55918de5b055d3765a06c2bba1ea8345d08a9f53107c9372f739aa37ab5a3` |
