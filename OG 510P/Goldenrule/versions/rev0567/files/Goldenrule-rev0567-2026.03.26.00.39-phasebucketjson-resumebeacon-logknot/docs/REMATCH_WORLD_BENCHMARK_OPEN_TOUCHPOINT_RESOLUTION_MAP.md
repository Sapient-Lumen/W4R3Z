# Rematch-world benchmark open touchpoint resolution map

Focus: collapse the still-open rematch-world assumptions/questions/gap into one exact closure queue that maps each resolver onto affected claim families, bridge citations, and seed-local landing work where applicable

Generated compact closure map for the first endogenous rematch-world benchmark. Use it to turn the still-open assumptions/questions/gap into one small implementation queue: which claim families each touchpoint blocks, which native section it lands in, and which bridge surfaces remain sufficient until closure.

## Main findings

- 11 open rematch-world touchpoints collapse onto 6 actual closure targets.
- 5 closure targets are seed-local native fills covering 23 blocker slots and 28 required edits; the remaining target is the cross-section engine gap `SG-003`.
- Only 5 rows are pure interpretation disciplines; they now fold under the same 6 closure targets instead of floating separately in the caution surface.
- `RWC-008` stays outside this map because final package authority is already closed; this map only tracks the 6 claim families whose interpretation or publication path still depends on open rematch-world questions.

## Counts

- open_touchpoint_count: 11
- closure_target_count: 6
- native_question_target_count: 5
- cross_section_gap_target_count: 1
- folded_assumption_count: 5
- affected_claim_family_count: 6
- seed_local_blocker_slot_count: 23
- seed_local_required_edit_count: 28
- seed_local_section_status_flip_count: 5
- pending_native_section_count: 5

## Closure target matrix

| resolver_id | kind | closure_scope | native_section | affected_claims | dependent_assumptions | blocker_slots | required_edits | bridge_paths |
|---|---|---|---|---|---|---:|---:|---:|
| `SG-003` | `gap` | `cross_section_engine_gap` | — | `RWC-001`, `RWC-002`, `RWC-004` | `SA-003` | — | — | 4 |
| `SQ-012` | `question` | `seed_local_native_fill` | `world_semantics_contract` | `RWC-005` | `SA-011` | 6 | 7 | 1 |
| `SQ-013` | `question` | `seed_local_native_fill` | `matching_state_contract` | `RWC-006` | `SA-012` | 3 | 4 | 1 |
| `SQ-014` | `question` | `seed_local_native_fill` | `occupancy_accounting_contract` | `RWC-006` | `SA-013` | 5 | 6 | 1 |
| `SQ-015` | `question` | `seed_local_native_fill` | `turnover_tempo_contract` | `RWC-007` | — | 4 | 5 | 2 |
| `SQ-016` | `question` | `seed_local_native_fill` | `paired_ranking_views_contract` | `RWC-007` | `SA-015` | 5 | 6 | 2 |

## Closure target details

### SG-003

- resolver_kind: `gap`
- resolver_summary: The engine-level contract for endogenous rematching and world-aware strategy canonicalization is underspecified.
- closure_scope: `cross_section_engine_gap`
- closure_target_summary: Keep the copied decision bundle frozen and citation-first until the engine gap closes; the current seed-local publication floor still covers 24 blocker loci, but none of those edits alone replaces the missing world-aware canonicalization contract.
- affected_claim_family_ids: `RWC-001`, `RWC-002`, `RWC-004`
- dependent_assumption_ids: `SA-003`
- native_section: none (cross-section engine contract gap)
- dependency_reason: No single seed-local fill section removes this dependency; the copied phase-3 decision contract remains citation-first until the engine-level endogenous rematching and canonicalization contract exists.
- closure_target_paths: none (not a seed-local blocker list)
- current_bridge_paths:
  - `docs/REMATCH_WORLD_BENCHMARK_EXAMPLE_DELTA_LEDGER.md`
  - `docs/REMATCH_WORLD_BENCHMARK_NATIVE_FILL_MAP.md`
  - `docs/REMATCH_WORLD_BENCHMARK_WORLD_EMISSION_CARD.md`
  - `examples/snapshots/rematch_world_benchmark_publication_bundle_receipt.json`
- folded_assumption_summaries:
  - Until SG-003 resolves, treat fixed-dyad exit results as diagnostic and report rematch-world discoveries in canonicalized families rather than raw genotype counts when possible.

### SQ-012

- resolver_kind: `question`
- resolver_summary: How should rematch worlds assign roles and carry rematch-relevant state once asymmetric strategies or asymmetric environments are admitted?
- closure_scope: `seed_local_native_fill`
- closure_target_summary: Fill world_semantics_contract and flip `section_status.world_semantics_contract` to `filled`; this clears 6 seed-local blocker slots at stage 1 of the native landing ladder.
- affected_claim_family_ids: `RWC-005`
- dependent_assumption_ids: `SA-011`
- native_section: `world_semantics_contract`
- fill_order_index: 1
- blocker_slots: 6 total (6 template + 0 null)
- required_edit_count: 7 (cumulative `8`)
- section_status_gate: `section_status.world_semantics_contract`
- data_prefix: `world_semantics_contract`
- dependency_reason: Define role assignment plus carry/reset semantics before attaching quantitative benchmark rows to one institution.
- closure_target_paths:
  - `world_semantics_contract.asymmetry_trigger_policy`
  - `world_semantics_contract.rematch_state_carry_policy`
  - `world_semantics_contract.rematch_state_reset_policy`
  - `world_semantics_contract.role_assignment_policy`
  - `world_semantics_contract.role_swapped_companion_policy`
  - `world_semantics_contract.world_name`
- current_bridge_paths:
  - `docs/REMATCH_WORLD_BENCHMARK_WORLD_EMISSION_CARD.md`
- folded_assumption_summaries:
  - Until SQ-012 resolves, treat rematch-world claims as provisional unless they declare the role-assignment policy explicitly and include a role-swapped companion benchmark when asymmetry is in play.

### SQ-013

- resolver_kind: `question`
- resolver_summary: How should endogenous rematch worlds separate rematch delay/search dead-time from market thickness or matching efficiency, and what matched-vs-searching state must be tracked to make welfare claims comparable?
- closure_scope: `seed_local_native_fill`
- closure_target_summary: Fill matching_state_contract and flip `section_status.matching_state_contract` to `filled`; this clears 3 seed-local blocker slots at stage 2 of the native landing ladder.
- affected_claim_family_ids: `RWC-006`
- dependent_assumption_ids: `SA-012`
- native_section: `matching_state_contract`
- fill_order_index: 2
- blocker_slots: 3 total (2 template + 1 null)
- required_edit_count: 4 (cumulative `12`)
- section_status_gate: `section_status.matching_state_contract`
- data_prefix: `matching_state_contract`
- dependency_reason: Declare rematch delay versus matching-efficiency semantics before any dead-round or turnover comparison is interpreted.
- closure_target_paths:
  - `matching_state_contract.comparability_note`
  - `matching_state_contract.matching_efficiency_model`
  - `matching_state_contract.rematch_delay_rounds`
- current_bridge_paths:
  - `docs/REMATCH_WORLD_BENCHMARK_WORLD_EMISSION_CARD.md`
- folded_assumption_summaries:
  - Until SQ-013 resolves, treat exogenous-pool rematch-delay sweeps as delay-tax diagnostics only, not as full matching-market efficiency claims.

### SQ-014

- resolver_kind: `question`
- resolver_summary: What occupancy/accounting fields must every rematch-world benchmark expose so aggregate welfare can be decomposed into time spent matched versus payoff earned while matched?
- closure_scope: `seed_local_native_fill`
- closure_target_summary: Fill occupancy_accounting_contract and flip `section_status.occupancy_accounting_contract` to `filled`; this clears 5 seed-local blocker slots at stage 3 of the native landing ladder.
- affected_claim_family_ids: `RWC-006`
- dependent_assumption_ids: `SA-013`
- native_section: `occupancy_accounting_contract`
- fill_order_index: 3
- blocker_slots: 5 total (1 template + 4 null)
- required_edit_count: 6 (cumulative `18`)
- section_status_gate: `section_status.occupancy_accounting_contract`
- data_prefix: `occupancy_accounting_contract.policy_rows`
- dependency_reason: Populate aggregate-versus-in-match welfare decomposition only after the matching-state terms are concrete.
- closure_target_paths:
  - `occupancy_accounting_contract.policy_rows[0].aggregate_avg_payoff`
  - `occupancy_accounting_contract.policy_rows[0].dead_round_share`
  - `occupancy_accounting_contract.policy_rows[0].in_match_avg_payoff`
  - `occupancy_accounting_contract.policy_rows[0].matched_round_share`
  - `occupancy_accounting_contract.policy_rows[0].policy`
- current_bridge_paths:
  - `docs/REMATCH_WORLD_BENCHMARK_WORLD_EMISSION_CARD.md`
- folded_assumption_summaries:
  - Until SQ-014 resolves, treat rematch-world welfare claims as incomplete unless they disclose occupancy accounting (`matched_round_share`, `dead_round_share` or equivalent, and `in_match_avg_payoff`) alongside aggregate payoff.

### SQ-015

- resolver_kind: `question`
- resolver_summary: What persistence / turnover field must every rematch-world benchmark expose so fixed rematch-delay penalties can be normalized and compared across worlds or policies?
- closure_scope: `seed_local_native_fill`
- closure_target_summary: Fill turnover_tempo_contract and flip `section_status.turnover_tempo_contract` to `filled`; this clears 4 seed-local blocker slots at stage 4 of the native landing ladder.
- affected_claim_family_ids: `RWC-007`
- dependent_assumption_ids: none
- native_section: `turnover_tempo_contract`
- fill_order_index: 4
- blocker_slots: 4 total (2 template + 2 null)
- required_edit_count: 5 (cumulative `23`)
- section_status_gate: `section_status.turnover_tempo_contract`
- data_prefix: `turnover_tempo_contract.policy_rows`
- dependency_reason: Bind turnover metrics after the matching-state semantics and occupancy decomposition are already fixed.
- closure_target_paths:
  - `turnover_tempo_contract.policy_rows[0].avg_match_length`
  - `turnover_tempo_contract.policy_rows[0].delay_or_search_dead_time`
  - `turnover_tempo_contract.policy_rows[0].policy`
  - `turnover_tempo_contract.policy_rows[0].turnover_metric_label`
- current_bridge_paths:
  - `docs/REMATCH_WORLD_BENCHMARK_NATIVE_FILL_MAP.md`
  - `docs/REMATCH_WORLD_BENCHMARK_WORLD_EMISSION_CARD.md`
- folded_assumption_summaries: none

### SQ-016

- resolver_kind: `question`
- resolver_summary: What paired ranking views should rematch-world benchmarks publish so occupancy/tempo effects are distinguishable from genuine within-match strategic improvements?
- closure_scope: `seed_local_native_fill`
- closure_target_summary: Fill paired_ranking_views_contract and flip `section_status.paired_ranking_views_contract` to `filled`; this clears 5 seed-local blocker slots at stage 5 of the native landing ladder.
- affected_claim_family_ids: `RWC-007`
- dependent_assumption_ids: `SA-015`
- native_section: `paired_ranking_views_contract`
- fill_order_index: 5
- blocker_slots: 5 total (1 template + 4 null)
- required_edit_count: 6 (cumulative `29`)
- section_status_gate: `section_status.paired_ranking_views_contract`
- data_prefix: `paired_ranking_views_contract.leaderboard_rows`
- dependency_reason: Publish aggregate-versus-in-match leaderboards only after the underlying payoff decomposition has been filled.
- closure_target_paths:
  - `paired_ranking_views_contract.leaderboard_rows[0].aggregate_avg_payoff`
  - `paired_ranking_views_contract.leaderboard_rows[0].aggregate_rank`
  - `paired_ranking_views_contract.leaderboard_rows[0].in_match_avg_payoff`
  - `paired_ranking_views_contract.leaderboard_rows[0].in_match_rank`
  - `paired_ranking_views_contract.leaderboard_rows[0].policy`
- current_bridge_paths:
  - `docs/REMATCH_WORLD_BENCHMARK_NATIVE_FILL_MAP.md`
  - `docs/REMATCH_WORLD_BENCHMARK_WORLD_EMISSION_CARD.md`
- folded_assumption_summaries:
  - Until SQ-016 resolves, treat rematch-world leaderboards as incomplete unless they publish both aggregate welfare and an occupancy-normalized in-match ranking (or an equivalent paired view).

## Folded assumptions

| id | resolver_id | touched_by | summary |
|---|---|---|---|
| `SA-003` | `SG-003` | `RWC-004` | Until SG-003 resolves, treat fixed-dyad exit results as diagnostic and report rematch-world discoveries in canonicalized families rather than raw genotype counts when possible. |
| `SA-011` | `SQ-012` | `RWC-005` | Until SQ-012 resolves, treat rematch-world claims as provisional unless they declare the role-assignment policy explicitly and include a role-swapped companion benchmark when asymmetry is in play. |
| `SA-012` | `SQ-013` | `RWC-006` | Until SQ-013 resolves, treat exogenous-pool rematch-delay sweeps as delay-tax diagnostics only, not as full matching-market efficiency claims. |
| `SA-013` | `SQ-014` | `RWC-006` | Until SQ-014 resolves, treat rematch-world welfare claims as incomplete unless they disclose occupancy accounting (`matched_round_share`, `dead_round_share` or equivalent, and `in_match_avg_payoff`) alongside aggregate payoff. |
| `SA-015` | `SQ-016` | `RWC-007` | Until SQ-016 resolves, treat rematch-world leaderboards as incomplete unless they publish both aggregate welfare and an occupancy-normalized in-match ranking (or an equivalent paired view). |

## Recommended next move

- Use this map when deciding the next native rematch-world fill: land one resolver at a time in ladder order, cite only the listed bridge surfaces while it remains open, and do not treat the engine gap as solved merely because all five seed-local sections are filled.
