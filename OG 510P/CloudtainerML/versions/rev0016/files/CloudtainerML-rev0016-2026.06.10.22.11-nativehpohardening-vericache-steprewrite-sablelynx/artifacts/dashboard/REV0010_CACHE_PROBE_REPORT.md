# Cache/memory probe report — rev0010

Artifacts: **32**
Schema-ready: **32**

## Family counts

- **attention architecture**: 7 artifacts; 7 schema-ready
- **bounded memory**: 9 artifacts; 9 schema-ready
- **quantization**: 2 artifacts; 2 schema-ready
- **retention/eviction**: 6 artifacts; 6 schema-ready
- **routing/indexing**: 6 artifacts; 6 schema-ready
- **runtime/depth**: 2 artifacts; 2 schema-ready

## Compact winners

| family | probe | rows | metric | compact result |
|---|---|---:|---|---|
| quantization | kv_wind_tunnel | 78 | relative_error |  |
| bounded memory | spectral_assoc_recall | 168 | accuracy |  |
| retention/eviction | dormant_sponsorship | 320 | target_value_retention |  |
| retention/eviction | region_wipeout_cache | 240 | coverage_success |  |
| retention/eviction | value_outlier_eviction | 216 | critical_value_retention |  |
| attention architecture | depth_value_mixing | 240 | mean_error |  |
| bounded memory | dynamic_state_merging | 160 | transition_preservation |  |
| attention architecture | entmax_support_recovery | 0 | output_error |  |
| retention/eviction | moment_directional_gap | 2880 | reconstruction_error |  |
| attention architecture | qkv_projection_sharing | 750 | relative_error |  |
| attention architecture | qkv_projection_sharing | 0 | relative_error |  |
| bounded memory | tensor_cache_l1_l2 | 0 | retrieval_error |  |
| runtime/depth | attention_runtime_termination | 0 | relative_error |  |
| attention architecture | bank_of_values | 0 | prediction_accuracy |  |
| bounded memory | blurry_window_attention | 880 | reconstruction_error |  |
| routing/indexing | branch_cache_sharing | 336 | state_match |  |
| bounded memory | hierarchical_fademem_cache | 1260 | reconstruction_error |  |
| attention architecture | qk_restore_amnesia | 80 | recall_accuracy | qk_restore:3 |
| routing/indexing | reasoning_wave_budget | 80 | retained_mass | oracle_step:3 |
| quantization | token_precision_frontier | 80 | quality_score | mixed_salience_8_4_2:7; few_8bit_attention:5; many_2bit_attention:1; more_4bit_attention:1; semantic_sponsor_4bit:1 |
| attention architecture | hist_window_order | 1440 | outgoing_accuracy | delta_exact:4 |
| retention/eviction | intent_kv_pruning | 3072 | critical_retention_purity_minus_stale_error | oracle_critical:4 |
| runtime/depth | latent_reasoning_router | 4608 | utility | oracle_router:2; all_flow_latent:1; all_latent:1 |
| routing/indexing | pcaf_sparse_memory | 5376 | mean_exact_success_minus_error_cost | semantic_topk_oracle:4 |
| routing/indexing | shared_routing_once | 2688 | support_recall_minus_bad_layers_and_cost | per_layer_score:3; consensus_shared:1 |
| routing/indexing | forecast_sparse_routing | 18900 | mass_recall | forecast_next_layer:15 |
| bounded memory | latent_context_compression | 400 | output_rel_error | compressed_then_expand_top2:4; random_expand_top1:1 |
| retention/eviction | observability_safe_retention | 840 | score | stale_averse:7; recency:3; risk_aware_oas:3; online_salience:2 |
| routing/indexing | evidence_aligned_ttt | 2160 | answer_accuracy | ease_ttt_softmix:12; ease_ttt_topk:10; full_context_base:9; retrieval_only_topk:9; random_qttt:5 |
| bounded memory | parametric_kv_memory | 3000 | rouge_l_proxy | adapter_when_cache_miss:15; context_only:5; adapter_only:4; gated_context_adapter:1 |
| bounded memory | smt_transition_training | 900 | query_accuracy | ridge_supervised_update:15 |
| bounded memory | still_compactor | 4500 | reconstruction_error | centroid_slots:23; attention_topk:4; hybrid_latent_plus_topk:3 |

## Audit note

This report is deliberately a comparison surface, not a unified leaderboard. The next refactor should add per-family comparable metrics and graph specs.
