# Rematch-world benchmark stage-yield ledger

Focus: show what each native fill stage actually buys for the first rematch-world publication: blocker work cleared, touchpoints resolved, claim families unlocked, and the stages that are prerequisites or metadata-only rather than immediate claim unlocks

Generated stage-by-stage yield ledger for the first endogenous rematch-world benchmark. Use it to see what each native fill stage actually buys: which blocker work it clears, which open touchpoints it resolves, which claim families become safe, and which stages are prerequisites or metadata-only rather than immediate claim unlocks.

## Main findings

- Only 3 of the 7 edit stages directly unlock any new claim family; 2 stages are prerequisite-only question closures, 1 is a benchmark-id anchor, and the final stage is metadata-only closeout.
- The two easy-to-miss prerequisite-only stages are `matching_state_contract` at 12 cumulative edits and `turnover_tempo_contract` at 23 cumulative edits: they clear real blocker work and open questions even though the safe-claim count does not move immediately.
- After 18 cumulative edits, 4 of the 8 claim families are already safe and 3 of the 5 seed-local touchpoints are closed; after 29 edits, 5 claim families are safe and all 5 seed-local touchpoints are closed.
- The final `artifact_state` flip at 30 cumulative edits changes no claim family and closes no touchpoint; it only converts the fully filled seed into a publishable filled-benchmark artifact while the 3 `SG-003` claim families remain citation-first.

## Counts

- stage_count: 7
- claim_unlock_stage_count: 3
- resolver_only_prerequisite_stage_count: 2
- benchmark_anchor_stage_count: 1
- metadata_closeout_stage_count: 1
- safe_to_cite_now_claim_family_count: 2
- max_safe_claim_family_count_after_seed_local_fill: 5
- seed_local_touchpoint_count: 5
- max_resolved_seed_touchpoint_count: 5
- remaining_engine_gap_claim_family_count: 3

## Utility buckets

| stage_utility_kind | stage_count | stage_keys | summary |
|---|---:|---|---|
| `benchmark_anchor` | 1 | `benchmark_id_binding` | Anchors the artifact to one concrete benchmark id before any world-native rows are publishable. |
| `claim_unlock` | 3 | `world_semantics_contract`, `occupancy_accounting_contract`, `paired_ranking_views_contract` | Directly makes at least one additional claim family safe once this stage lands. |
| `resolver_only_prerequisite` | 2 | `matching_state_contract`, `turnover_tempo_contract` | Closes real native blocker work and an open seed-local question, but does not immediately unlock a claim family on its own. |
| `metadata_closeout` | 1 | `artifact_state_transition` | Does not clear a new native question or claim family; it only marks the artifact as filled after every blocker is already gone. |

## Stage yield matrix

| order | stage_key | required_edits | cumulative_edits | touchpoints_closed_now | claims_unlocked_now | cumulative_safe_claims | remaining_seed_touchpoints | utility |
|---:|---|---:|---:|---|---|---:|---:|---|
| 1 | `benchmark_id_binding` | 1 | 1 | — | — | 2 | 5 | `benchmark_anchor` |
| 2 | `world_semantics_contract` | 7 | 8 | `SQ-012` | `RWC-005` | 3 | 4 | `claim_unlock` |
| 3 | `matching_state_contract` | 4 | 12 | `SQ-013` | — | 3 | 3 | `resolver_only_prerequisite` |
| 4 | `occupancy_accounting_contract` | 6 | 18 | `SQ-014` | `RWC-006` | 4 | 2 | `claim_unlock` |
| 5 | `turnover_tempo_contract` | 5 | 23 | `SQ-015` | — | 4 | 1 | `resolver_only_prerequisite` |
| 6 | `paired_ranking_views_contract` | 6 | 29 | `SQ-016` | `RWC-007` | 5 | 0 | `claim_unlock` |
| 7 | `artifact_state_transition` | 1 | 30 | — | — | 5 | 0 | `metadata_closeout` |

## Stage details

### Stage 1 — bind benchmark identity

- stage_key: `benchmark_id_binding`
- stage_utility_kind: `benchmark_anchor`
- stage_utility_summary: Anchors the artifact to one concrete benchmark id before any world-native rows are publishable.
- required_edit_count: 1
- cumulative_required_edit_count: 1
- blocker_clear_count: 1
- section_status_flip_count: 0
- changed_prefixes: `benchmark_id`
- linked_question_ids: none
- newly_resolved_touchpoint_ids: none
- newly_unlocked_claim_family_ids: none
- cumulative_safe_claim_family_count: 2 (2/8)
- cumulative_resolved_seed_touchpoint_count: 0/5
- remaining_native_stage_unlock_claim_count: 3
- remaining_seed_touchpoint_count: 5
- remaining_engine_gap_claim_family_count: 3
- dependency_reason: Anchor the retained artifact to one concrete benchmark id before publishing native rows or package receipts against it.

### Stage 2 — fill world_semantics_contract

- stage_key: `world_semantics_contract`
- stage_utility_kind: `claim_unlock`
- stage_utility_summary: Directly makes at least one additional claim family safe once this stage lands.
- required_edit_count: 7
- cumulative_required_edit_count: 8
- blocker_clear_count: 6
- section_status_flip_count: 1
- changed_prefixes: `world_semantics_contract`, `section_status.world_semantics_contract`
- linked_question_ids: `SQ-012`
- newly_resolved_touchpoint_ids: `SQ-012`
- newly_unlocked_claim_family_ids: `RWC-005`
- cumulative_safe_claim_family_count: 3 (3/8)
- cumulative_resolved_seed_touchpoint_count: 1/5
- remaining_native_stage_unlock_claim_count: 2
- remaining_seed_touchpoint_count: 4
- remaining_engine_gap_claim_family_count: 3
- dependency_reason: Define role assignment plus carry/reset semantics before attaching quantitative benchmark rows to one institution.

### Stage 3 — fill matching_state_contract

- stage_key: `matching_state_contract`
- stage_utility_kind: `resolver_only_prerequisite`
- stage_utility_summary: Closes real native blocker work and an open seed-local question, but does not immediately unlock a claim family on its own.
- required_edit_count: 4
- cumulative_required_edit_count: 12
- blocker_clear_count: 3
- section_status_flip_count: 1
- changed_prefixes: `matching_state_contract`, `section_status.matching_state_contract`
- linked_question_ids: `SQ-013`
- newly_resolved_touchpoint_ids: `SQ-013`
- newly_unlocked_claim_family_ids: none
- cumulative_safe_claim_family_count: 3 (3/8)
- cumulative_resolved_seed_touchpoint_count: 2/5
- remaining_native_stage_unlock_claim_count: 2
- remaining_seed_touchpoint_count: 3
- remaining_engine_gap_claim_family_count: 3
- dependency_reason: Declare rematch delay versus matching-efficiency semantics before any dead-round or turnover comparison is interpreted.

### Stage 4 — fill occupancy_accounting_contract

- stage_key: `occupancy_accounting_contract`
- stage_utility_kind: `claim_unlock`
- stage_utility_summary: Directly makes at least one additional claim family safe once this stage lands.
- required_edit_count: 6
- cumulative_required_edit_count: 18
- blocker_clear_count: 5
- section_status_flip_count: 1
- changed_prefixes: `occupancy_accounting_contract.policy_rows`, `section_status.occupancy_accounting_contract`
- linked_question_ids: `SQ-014`
- newly_resolved_touchpoint_ids: `SQ-014`
- newly_unlocked_claim_family_ids: `RWC-006`
- cumulative_safe_claim_family_count: 4 (4/8)
- cumulative_resolved_seed_touchpoint_count: 3/5
- remaining_native_stage_unlock_claim_count: 1
- remaining_seed_touchpoint_count: 2
- remaining_engine_gap_claim_family_count: 3
- dependency_reason: Populate aggregate-versus-in-match welfare decomposition only after the matching-state terms are concrete.

### Stage 5 — fill turnover_tempo_contract

- stage_key: `turnover_tempo_contract`
- stage_utility_kind: `resolver_only_prerequisite`
- stage_utility_summary: Closes real native blocker work and an open seed-local question, but does not immediately unlock a claim family on its own.
- required_edit_count: 5
- cumulative_required_edit_count: 23
- blocker_clear_count: 4
- section_status_flip_count: 1
- changed_prefixes: `turnover_tempo_contract.policy_rows`, `section_status.turnover_tempo_contract`
- linked_question_ids: `SQ-015`
- newly_resolved_touchpoint_ids: `SQ-015`
- newly_unlocked_claim_family_ids: none
- cumulative_safe_claim_family_count: 4 (4/8)
- cumulative_resolved_seed_touchpoint_count: 4/5
- remaining_native_stage_unlock_claim_count: 1
- remaining_seed_touchpoint_count: 1
- remaining_engine_gap_claim_family_count: 3
- dependency_reason: Bind turnover metrics after the matching-state semantics and occupancy decomposition are already fixed.

### Stage 6 — fill paired_ranking_views_contract

- stage_key: `paired_ranking_views_contract`
- stage_utility_kind: `claim_unlock`
- stage_utility_summary: Directly makes at least one additional claim family safe once this stage lands.
- required_edit_count: 6
- cumulative_required_edit_count: 29
- blocker_clear_count: 5
- section_status_flip_count: 1
- changed_prefixes: `paired_ranking_views_contract.leaderboard_rows`, `section_status.paired_ranking_views_contract`
- linked_question_ids: `SQ-016`
- newly_resolved_touchpoint_ids: `SQ-016`
- newly_unlocked_claim_family_ids: `RWC-007`
- cumulative_safe_claim_family_count: 5 (5/8)
- cumulative_resolved_seed_touchpoint_count: 5/5
- remaining_native_stage_unlock_claim_count: 0
- remaining_seed_touchpoint_count: 0
- remaining_engine_gap_claim_family_count: 3
- dependency_reason: Publish aggregate-versus-in-match leaderboards only after the underlying payoff decomposition has been filled.

### Stage 7 — flip artifact state

- stage_key: `artifact_state_transition`
- stage_utility_kind: `metadata_closeout`
- stage_utility_summary: Does not clear a new native question or claim family; it only marks the artifact as filled after every blocker is already gone.
- required_edit_count: 1
- cumulative_required_edit_count: 30
- blocker_clear_count: 0
- section_status_flip_count: 0
- changed_prefixes: `artifact_state`
- linked_question_ids: none
- newly_resolved_touchpoint_ids: none
- newly_unlocked_claim_family_ids: none
- cumulative_safe_claim_family_count: 5 (5/8)
- cumulative_resolved_seed_touchpoint_count: 5/5
- remaining_native_stage_unlock_claim_count: 0
- remaining_seed_touchpoint_count: 0
- remaining_engine_gap_claim_family_count: 3
- dependency_reason: Only mark the artifact `filled_benchmark` after every blocking native locus has been replaced with concrete content.

## Recommended next move

- Use this ledger when sequencing native work: do not drop the 12-edit or 23-edit stages just because the safe-claim total holds flat there, and treat the 30th edit as publication-state closeout rather than as a new evidentiary unlock.
