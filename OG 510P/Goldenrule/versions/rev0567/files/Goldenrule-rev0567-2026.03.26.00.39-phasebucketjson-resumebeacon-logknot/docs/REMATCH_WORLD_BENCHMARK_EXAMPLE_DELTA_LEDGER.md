# Rematch-world benchmark example delta ledger

Focus: derive one exact seed-to-compiled change ledger for the synthetic first rematch-world publication so the eventual implementor can see the concrete mutation shape without reopening the seed, compiled artifact, and native-fill map separately

## Local result
- The synthetic compiled artifact changes exactly 33 real JSON paths relative to the standing seed: 30 are the minimum publication changes and 3 are purely optional second-row insertions.
- Every changed path stays inside the already-allowed mutable prefixes from the native-fill map; no copied handoff root and no compact decision-contract content changes at all.
- The exact required part of the example matches the landing ladder’s publication floor of 30 edits, while the extra occupancy / turnover / paired-ranking row insertions show how larger policy sets fit inside the same legal edit surface.
- Because the compiled example is rebuilt live from the evidence-packet toolchain before diffing, this ledger doubles as a stale-snapshot guard rather than only another prose summary.

## Change counts

| category | count | note |
|---|---:|---|
| total changed paths | `33` | exact seed-to-compiled JSON paths, excluding redundant list-length pseudo-diffs |
| required publication changes | `30` | matches the standing publication floor from the native-fill map / landing ladder |
| optional changes | `3` | extra second-row insertions inside already-allowed mutable arrays |
| metadata binding | `1` | exact class count in the synthetic compiled example |
| metadata transition | `1` | exact class count in the synthetic compiled example |
| optional row insertion | `3` | exact class count in the synthetic compiled example |
| section status flip | `5` | exact class count in the synthetic compiled example |
| world fill blocker clear | `23` | exact class count in the synthetic compiled example |

## Section delta summary

| section | required | optional | linked questions |
|---|---:|---:|---|
| `benchmark_metadata` | `2` | `0` | — |
| `world_semantics_contract` | `7` | `0` | `SQ-012` |
| `matching_state_contract` | `4` | `0` | `SQ-013` |
| `occupancy_accounting_contract` | `6` | `1` | `SQ-014` |
| `turnover_tempo_contract` | `5` | `1` | `SQ-015` |
| `paired_ranking_views_contract` | `6` | `1` | `SQ-016` |

## Exact changed paths

| # | path | class | required | before | after |
|---:|---|---|---|---|---|
| 1 | `artifact_state` | `metadata_transition` | yes | `seed_template` | `filled_benchmark` |
| 2 | `benchmark_id` | `metadata_binding` | yes | `TEMPLATE_first_endogenous_rematch_world_benchmark` | `synthetic_rematch_world_example_benchmark_v1` |
| 3 | `matching_state_contract.comparability_note` | `world_fill_blocker_clear` | yes | `TEMPLATE_explain_how_search_dead_time_is_reported_separately_from_matched_payoff` | `report search dead time separately from matched payoff so aggregate averages span all rounds ...` |
| 4 | `matching_state_contract.matching_efficiency_model` | `world_fill_blocker_clear` | yes | `TEMPLATE_describe_search_dead_time_separately_from_market_thickness` | `count search dead time as unmatched waiting rounds and do not fold it into average match leng...` |
| 5 | `matching_state_contract.rematch_delay_rounds` | `world_fill_blocker_clear` | yes | `null` | `2` |
| 6 | `section_status.matching_state_contract` | `section_status_flip` | yes | `pending_fill` | `filled` |
| 7 | `occupancy_accounting_contract.policy_rows[0].aggregate_avg_payoff` | `world_fill_blocker_clear` | yes | `null` | `2.31` |
| 8 | `occupancy_accounting_contract.policy_rows[0].dead_round_share` | `world_fill_blocker_clear` | yes | `null` | `0.11` |
| 9 | `occupancy_accounting_contract.policy_rows[0].in_match_avg_payoff` | `world_fill_blocker_clear` | yes | `null` | `2.59` |
| 10 | `occupancy_accounting_contract.policy_rows[0].matched_round_share` | `world_fill_blocker_clear` | yes | `null` | `0.89` |
| 11 | `occupancy_accounting_contract.policy_rows[0].policy` | `world_fill_blocker_clear` | yes | `TEMPLATE_replace_with_policy_id` | `reciprocal_anchor` |
| 12 | `section_status.occupancy_accounting_contract` | `section_status_flip` | yes | `pending_fill` | `filled` |
| 13 | `paired_ranking_views_contract.leaderboard_rows[0].aggregate_avg_payoff` | `world_fill_blocker_clear` | yes | `null` | `2.31` |
| 14 | `paired_ranking_views_contract.leaderboard_rows[0].aggregate_rank` | `world_fill_blocker_clear` | yes | `null` | `1` |
| 15 | `paired_ranking_views_contract.leaderboard_rows[0].in_match_avg_payoff` | `world_fill_blocker_clear` | yes | `null` | `2.59` |
| 16 | `paired_ranking_views_contract.leaderboard_rows[0].in_match_rank` | `world_fill_blocker_clear` | yes | `null` | `1` |
| 17 | `paired_ranking_views_contract.leaderboard_rows[0].policy` | `world_fill_blocker_clear` | yes | `TEMPLATE_replace_with_policy_id` | `reciprocal_anchor` |
| 18 | `section_status.paired_ranking_views_contract` | `section_status_flip` | yes | `pending_fill` | `filled` |
| 19 | `section_status.turnover_tempo_contract` | `section_status_flip` | yes | `pending_fill` | `filled` |
| 20 | `turnover_tempo_contract.policy_rows[0].avg_match_length` | `world_fill_blocker_clear` | yes | `null` | `6.7` |
| 21 | `turnover_tempo_contract.policy_rows[0].delay_or_search_dead_time` | `world_fill_blocker_clear` | yes | `null` | `1.2` |
| 22 | `turnover_tempo_contract.policy_rows[0].policy` | `world_fill_blocker_clear` | yes | `TEMPLATE_replace_with_policy_id` | `reciprocal_anchor` |
| 23 | `turnover_tempo_contract.policy_rows[0].turnover_metric_label` | `world_fill_blocker_clear` | yes | `TEMPLATE_choose_avg_match_length_or_equivalent_turnover_metric` | `avg_match_length` |
| 24 | `section_status.world_semantics_contract` | `section_status_flip` | yes | `pending_fill` | `filled` |
| 25 | `world_semantics_contract.asymmetry_trigger_policy` | `world_fill_blocker_clear` | yes | `TEMPLATE_declare_when_role_swapped_companion_runs_are_required` | `treat payoff asymmetry as active whenever role order changes realized payoffs or continuation...` |
| 26 | `world_semantics_contract.rematch_state_carry_policy` | `world_fill_blocker_clear` | yes | `TEMPLATE_declare_which_state_persists_across_partnership_continuations` | `carry forward bilateral continuation state inside the same partnership but not unmatched sear...` |
| 27 | `world_semantics_contract.rematch_state_reset_policy` | `world_fill_blocker_clear` | yes | `TEMPLATE_declare_when_new_partnerships_reset_state` | `reset bilateral continuation state whenever a policy forms a new partnership after search` |
| 28 | `world_semantics_contract.role_assignment_policy` | `world_fill_blocker_clear` | yes | `TEMPLATE_declare_how_roles_are_assigned_and_swapped` | `assign roles by ordered policy pair and emit a companion run whenever the payoff function is ...` |
| 29 | `world_semantics_contract.role_swapped_companion_policy` | `world_fill_blocker_clear` | yes | `TEMPLATE_required_when_asymmetry_is_in_play` | `require one role-swapped companion run for each ordered pair whenever role-sensitive payoffs ...` |
| 30 | `world_semantics_contract.world_name` | `world_fill_blocker_clear` | yes | `TEMPLATE_replace_with_world_name` | `synthetic_pairwise_search_world_v1` |
| 31 | `occupancy_accounting_contract.policy_rows[1]` | `optional_row_insertion` | no | `null` | `dict(keys=aggregate_avg_payoff, dead_round_share, in_match_avg_payoff, ...)` |
| 32 | `paired_ranking_views_contract.leaderboard_rows[1]` | `optional_row_insertion` | no | `null` | `dict(keys=aggregate_avg_payoff, aggregate_rank, in_match_avg_payoff, ...)` |
| 33 | `turnover_tempo_contract.policy_rows[1]` | `optional_row_insertion` | no | `null` | `dict(keys=avg_match_length, delay_or_search_dead_time, policy, ...)` |

## Frozen roots that stay untouched

- `canonicalization_planner_contract`
- `winner_triage_handoff`
- `delta_shortlist_handoff`
- `paired_ranking_interpretation_handoff`
- `matching_state_interpretation_handoff`
- `turnover_tempo_interpretation_handoff`
- `world_semantics_interpretation_handoff`
- `compact_decision_bundle`

## Implementor takeaway

Use this ledger as the smallest concrete mutation witness when the first real native fill starts: follow the 30 required paths first, then decide deliberately whether any second-row additions are worth retaining beyond that publication floor.

