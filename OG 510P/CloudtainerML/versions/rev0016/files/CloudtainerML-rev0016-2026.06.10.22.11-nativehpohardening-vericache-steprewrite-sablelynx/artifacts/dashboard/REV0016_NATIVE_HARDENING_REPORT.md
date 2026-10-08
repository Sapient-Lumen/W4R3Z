# Native hardening report — rev0016

- artifacts: 12

| artifact | probe | rows | metric | winners |
|---|---|---:|---|---|
| `artifacts/probe-results/REV0016_MEMORY_PROVENANCE_PHASE_SMOKE.json` | memory_provenance_phase | 336 | mean_utility / higher_is_better | correction_linked_memory:746; provenance_balanced_memory:188; skeptical_highstakes_memory:19; belief_snippet_memory:7 |
| `artifacts/probe-results/REV0016_NATIVE_HPO_PHASE_SMOKE.json` | native_hpo_phase | 80 | mean_regret_to_dense_grid_optimum / lower_is_better | domain_prior:85; grid:60; random:46; centaur_state_prior:35; cross_entropy:30 |
| `artifacts/probe-results/REV0016_NATIVE_TOKEN_PRECISION_FRONTIER_SMOKE.json` | native_token_precision_frontier | 105 | mean_output_rel_error / lower_is_better | mixed_8_4_2:5; few_8bit_attention:4; many_2bit_attention:3; more_4bit_attention:3 |
| `artifacts/probe-results/REV0016_PERIODIC_CACHE_REWRITE_SMOKE.json` | periodic_cache_rewrite | 25 | mean_utility / higher_is_better | attention_reconsolidate:334; continuous_eviction:113; fixed_periodic_rewrite:19; step_boundary_rewrite:14 |
| `artifacts/probe-results/REV0016_QUERY_MOVE_PHASE_SCAN_SMOKE.json` | query_move_phase_boundary | 4608 | latency_us / lower_is_better | index_then_fetch:746; move_query:262; recompute_local:144 |
| `artifacts/probe-results/REV0016_RESIDUAL_KV_SENSITIVITY_SMOKE.json` | native_residual_kv_sensitivity | 300 | score / lower_is_better | residual_checkpoint_recompute:48; lowrank_residual_sketch:12 |
| `artifacts/probe-results/REV0016_TEST2_token_precision_frontier.json` | native_token_precision_frontier | 105 | mean_output_rel_error / lower_is_better | mixed_8_4_2:5; few_8bit_attention:4; many_2bit_attention:3; more_4bit_attention:3 |
| `artifacts/probe-results/REV0016_TEST_memory_provenance_phase.json` | memory_provenance_phase | 336 | mean_utility / higher_is_better | correction_linked_memory:746; provenance_balanced_memory:188; skeptical_highstakes_memory:19; belief_snippet_memory:7 |
| `artifacts/probe-results/REV0016_TEST_native_hpo_phase.json` | native_hpo_phase | 80 | mean_regret_to_dense_grid_optimum / lower_is_better | domain_prior:85; grid:60; random:46; centaur_state_prior:35; cross_entropy:30 |
| `artifacts/probe-results/REV0016_TEST_residual_kv_sensitivity.json` | native_residual_kv_sensitivity | 300 | score / lower_is_better | residual_checkpoint_recompute:48; lowrank_residual_sketch:12 |
| `artifacts/probe-results/REV0016_TEST_token_precision_frontier.json` | native_token_precision_frontier | 105 | mean_output_rel_error / lower_is_better | mixed_8_4_2:5; few_8bit_attention:4; many_2bit_attention:3; more_4bit_attention:3 |
| `artifacts/probe-results/REV0016_VERICACHE_GUARD_SMOKE.json` | vericache_guard | 35 | mean_utility / higher_is_better | full_kv:237; vericache_toy_guard:163 |
