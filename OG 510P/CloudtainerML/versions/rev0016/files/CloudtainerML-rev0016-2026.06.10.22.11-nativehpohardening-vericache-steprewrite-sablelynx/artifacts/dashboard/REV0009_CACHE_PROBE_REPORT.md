# Cache/memory probe report — rev0009

Artifacts: **28**
Schema-ready: **8**

## Family counts

- **attention architecture**: 7 artifacts; 1 schema-ready
- **bounded memory**: 6 artifacts; 1 schema-ready
- **other**: 1 artifacts; 0 schema-ready
- **quantization**: 2 artifacts; 0 schema-ready
- **retention/eviction**: 6 artifacts; 2 schema-ready
- **routing/indexing**: 4 artifacts; 3 schema-ready
- **runtime/depth**: 2 artifacts; 1 schema-ready

## Compact winners

| family | probe | rows | metric | compact result |
|---|---|---:|---|---|
| quantization | kv_wind_tunnel | 78 | undeclared |  |
| bounded memory | spectral_assoc_recall | 168 | undeclared |  |
| retention/eviction | dormant_sponsorship | 320 | undeclared |  |
| retention/eviction | region_wipeout_cache | 240 | undeclared |  |
| retention/eviction | value_outlier_eviction | 216 | undeclared |  |
| attention architecture | depth_value_mixing | 240 | undeclared |  |
| bounded memory | dynamic_state_merging | 160 | undeclared |  |
| attention architecture | entmax_support_recovery | 0 | undeclared |  |
| retention/eviction | moment_directional_gap | 2880 | undeclared |  |
| attention architecture | qkv_projection_sharing | 750 | undeclared |  |
| attention architecture | qkv_projection_sharing | 0 | undeclared |  |
| bounded memory | tensor_cache_l1_l2 | 0 | undeclared |  |
| runtime/depth | attention_runtime_termination | 0 | undeclared |  |
| attention architecture | bank_of_values | 0 | undeclared |  |
| bounded memory | blurry_window_attention | 880 | undeclared |  |
| other | branch_cache_sharing | 336 | undeclared |  |
| bounded memory | hierarchical_fademem_cache | 1260 | undeclared |  |
| attention architecture | qk_restore_amnesia | 80 | undeclared | qk_restore:3 |
| routing/indexing | reasoning_wave_budget | 80 | undeclared | oracle_step:3 |
| quantization | token_precision_frontier | 80 | undeclared | mixed_salience_8_4_2:7; few_8bit_attention:5; many_2bit_attention:1; more_4bit_attention:1; semantic_sponsor_4bit:1 |
| attention architecture | hist_window_order | 1440 | outgoing_accuracy | delta_exact:4 |
| retention/eviction | intent_kv_pruning | 3072 | critical_retention_purity_minus_stale_error | oracle_critical:4 |
| runtime/depth | latent_reasoning_router | 4608 | utility | oracle_router:2; all_flow_latent:1; all_latent:1 |
| routing/indexing | pcaf_sparse_memory | 5376 | mean_exact_success_minus_error_cost | semantic_topk_oracle:4 |
| routing/indexing | shared_routing_once | 2688 | support_recall_minus_bad_layers_and_cost | per_layer_score:3; consensus_shared:1 |
| routing/indexing | forecast_sparse_routing | 18900 | mass_recall | forecast_next_layer:15 |
| bounded memory | latent_context_compression | 400 | output_rel_error | compressed_then_expand_top2:4; random_expand_top1:1 |
| retention/eviction | observability_safe_retention | 840 | score | stale_averse:7; recency:3; risk_aware_oas:3; online_salience:2 |

## Audit note

This report is deliberately a comparison surface, not a unified leaderboard. The next refactor should add per-family comparable metrics and graph specs.
