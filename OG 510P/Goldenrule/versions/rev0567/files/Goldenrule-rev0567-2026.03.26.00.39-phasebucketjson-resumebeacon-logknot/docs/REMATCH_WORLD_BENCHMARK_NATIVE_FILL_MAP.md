# Rematch-world benchmark native-fill map

Focus: collapse the exact editable prefixes, blocker loci, and publishability transitions for the first endogenous rematch-world benchmark into one inheritor-facing fill map

## Local result
- The retained seed still carries 24 explicit fill blockers: 13 template strings and 11 required telemetry fills.
- Publication adds 5 required world-section status flips plus 1 extra metadata transition (`artifact_state`), so the smallest publishable edit set is 30 concrete changes across 12 mutable prefixes.
- All world-dependent work still fits inside 5 native sections in the seed order world_semantics_contract, matching_state_contract, occupancy_accounting_contract, turnover_tempo_contract, paired_ranking_views_contract, while 3 copied compact-decision nulls remain explicitly allowed and should not be 'fixed'.
- The inheritor therefore needs one disciplined in-place fill pass, not new sidecar reports: bind benchmark identity, replace native placeholders/nulls, flip the five native section statuses, and leave the copied decision surface untouched.

## Minimum publishable mutation set

| category | count | note |
|---|---:|---|
| explicit fill blockers | `24` | template strings plus required telemetry fills inside the seed |
| template blockers | `13` | placeholders that must be replaced with concrete semantics or ids |
| null blockers | `11` | measured values still missing outside the copied compact decision bundle |
| world-section status flips | `5` | `pending_fill -> filled` across the five native sections |
| extra metadata transitions | `1` | required publishability moves that are not already counted as blocker rows |
| mutable prefixes | `12` | exact legal edit surface from the mutation guard |
| total required edits | `30` | blockers + status flips + nonblocking metadata transitions |

## Metadata actions

| prefix | kind | currently blocking | current value summary | why it changes |
|---|---|---|---|---|
| `artifact_state` | `metadata_transition` | no | `nonblocking_transition_required` | A publishable benchmark must transition from seed_template to filled_benchmark. |
| `benchmark_id` | `metadata_binding` | yes | `TEMPLATE_first_endogenous_rematch_world_benchmark` | The retained artifact should be bound to one concrete endogenous rematch benchmark identifier. |

## Native section execution map

| order | section | questions | data prefix | status prefix | blockers | templates | nulls |
|---|---|---|---|---|---:|---:|---:|
| 1 | `world_semantics_contract` | `SQ-012` | `world_semantics_contract` | `section_status.world_semantics_contract` | `6` | `6` | `0` |
| 2 | `matching_state_contract` | `SQ-013` | `matching_state_contract` | `section_status.matching_state_contract` | `3` | `2` | `1` |
| 3 | `occupancy_accounting_contract` | `SQ-014` | `occupancy_accounting_contract.policy_rows` | `section_status.occupancy_accounting_contract` | `5` | `1` | `4` |
| 4 | `turnover_tempo_contract` | `SQ-015` | `turnover_tempo_contract.policy_rows` | `section_status.turnover_tempo_contract` | `4` | `2` | `2` |
| 5 | `paired_ranking_views_contract` | `SQ-016` | `paired_ranking_views_contract.leaderboard_rows` | `section_status.paired_ranking_views_contract` | `5` | `1` | `4` |

## Exact blocker loci by section

### benchmark_metadata

- `benchmark_id` — currently `TEMPLATE_first_endogenous_rematch_world_benchmark` (`metadata_binding`)

### world_semantics_contract

- `world_semantics_contract.asymmetry_trigger_policy` — `template_string` / `TEMPLATE_declare_when_role_swapped_companion_runs_are_required`
- `world_semantics_contract.rematch_state_carry_policy` — `template_string` / `TEMPLATE_declare_which_state_persists_across_partnership_continuations`
- `world_semantics_contract.rematch_state_reset_policy` — `template_string` / `TEMPLATE_declare_when_new_partnerships_reset_state`
- `world_semantics_contract.role_assignment_policy` — `template_string` / `TEMPLATE_declare_how_roles_are_assigned_and_swapped`
- `world_semantics_contract.role_swapped_companion_policy` — `template_string` / `TEMPLATE_required_when_asymmetry_is_in_play`
- `world_semantics_contract.world_name` — `template_string` / `TEMPLATE_replace_with_world_name`

### matching_state_contract

- `matching_state_contract.comparability_note` — `template_string` / `TEMPLATE_explain_how_search_dead_time_is_reported_separately_from_matched_payoff`
- `matching_state_contract.matching_efficiency_model` — `template_string` / `TEMPLATE_describe_search_dead_time_separately_from_market_thickness`
- `matching_state_contract.rematch_delay_rounds` — `null_fill_required` / `null`

### occupancy_accounting_contract

- `occupancy_accounting_contract.policy_rows[0].aggregate_avg_payoff` — `null_fill_required` / `null`
- `occupancy_accounting_contract.policy_rows[0].dead_round_share` — `null_fill_required` / `null`
- `occupancy_accounting_contract.policy_rows[0].in_match_avg_payoff` — `null_fill_required` / `null`
- `occupancy_accounting_contract.policy_rows[0].matched_round_share` — `null_fill_required` / `null`
- `occupancy_accounting_contract.policy_rows[0].policy` — `template_string` / `TEMPLATE_replace_with_policy_id`

### turnover_tempo_contract

- `turnover_tempo_contract.policy_rows[0].avg_match_length` — `null_fill_required` / `null`
- `turnover_tempo_contract.policy_rows[0].delay_or_search_dead_time` — `null_fill_required` / `null`
- `turnover_tempo_contract.policy_rows[0].policy` — `template_string` / `TEMPLATE_replace_with_policy_id`
- `turnover_tempo_contract.policy_rows[0].turnover_metric_label` — `template_string` / `TEMPLATE_choose_avg_match_length_or_equivalent_turnover_metric`

### paired_ranking_views_contract

- `paired_ranking_views_contract.leaderboard_rows[0].aggregate_avg_payoff` — `null_fill_required` / `null`
- `paired_ranking_views_contract.leaderboard_rows[0].aggregate_rank` — `null_fill_required` / `null`
- `paired_ranking_views_contract.leaderboard_rows[0].in_match_avg_payoff` — `null_fill_required` / `null`
- `paired_ranking_views_contract.leaderboard_rows[0].in_match_rank` — `null_fill_required` / `null`
- `paired_ranking_views_contract.leaderboard_rows[0].policy` — `template_string` / `TEMPLATE_replace_with_policy_id`

## Allowed nulls that are not blockers

- `compact_decision_bundle.delay_contract.extortion_rows[0].predicted_nonnegative_delay_winner_intervals[2].end_delay` — open_ended_interval_from_copied_decision_contract
- `compact_decision_bundle.delay_contract.extortion_rows[1].predicted_nonnegative_delay_winner_intervals[2].end_delay` — open_ended_interval_from_copied_decision_contract
- `compact_decision_bundle.delay_contract.extortion_rows[2].predicted_nonnegative_delay_winner_intervals[2].end_delay` — open_ended_interval_from_copied_decision_contract

## Implementor takeaway

Fill the blocker loci in section order, flip `artifact_state` to `filled_benchmark` only when the blocker rows are cleared, then run the mutation guard and completion gate before any publication/prune/package steps.

