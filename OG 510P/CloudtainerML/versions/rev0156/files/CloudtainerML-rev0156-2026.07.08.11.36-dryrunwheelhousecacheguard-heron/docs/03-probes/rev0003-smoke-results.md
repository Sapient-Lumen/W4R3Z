# rev0003 probe smoke results

These are smoke results, not conclusions. They confirm that the two first probes run and emit structured data.

## KV Wind Tunnel

Rows emitted: `78`  
Aggregate groups: `26`

Best low-hidden-error 2-bit variants under outlier strength 8.0:

```json
[
  {
    "variant": "hadamard_row",
    "bits": 2,
    "outlier_strength": 8.0,
    "n": 3,
    "n_tokens_mean": 96.0,
    "d_model_mean": 64.0,
    "steps_mean": 48.0,
    "outlier_strength_mean": 8.0,
    "bits_mean": 2.0,
    "approx_cache_bits_per_token_mean": 256.0,
    "k_rel_mse_mean": 0.5324601133664449,
    "v_rel_mse_mean": 0.5165639718373617,
    "k_row_scale_rel_error_mean_mean": 0.14787429571151733,
    "k_row_scale_rel_error_p95_mean": 0.25390790899594623,
    "k_row_scale_rel_error_max_mean": 0.3296526273091634,
    "mean_output_l2_mean": 1.3628880580266316,
    "max_output_l2_mean": 2.792545040448507,
    "final_hidden_l2_mean": 0.9641298254330953,
    "mean_hidden_l2_mean": 0.944644828637441,
    "mean_attention_tv_mean": 0.08158098037044208,
    "argmax_agreement_mean": 0.47222222222222215
  },
  {
    "variant": "varnorm",
    "bits": 2,
    "outlier_strength": 8.0,
    "n": 3,
    "n_tokens_mean": 96.0,
    "d_model_mean": 64.0,
    "steps_mean": 48.0,
    "outlier_strength_mean": 8.0,
    "bits_mean": 2.0,
    "approx_cache_bits_per_token_mean": 256.0,
    "k_rel_mse_mean": 0.7578938007354736,
    "v_rel_mse_mean": 0.8263241251309713,
    "k_row_scale_rel_error_mean_mean": 0.10454349964857101,
    "k_row_scale_rel_error_p95_mean": 0.2717949499686559,
    "k_row_scale_rel_error_max_mean": 0.3671045700709025,
    "mean_output_l2_mean": 1.2579678694407146,
    "max_output_l2_mean": 2.054025491078695,
    "final_hidden_l2_mean": 0.943220297495524,
    "mean_hidden_l2_mean": 0.968950609366099,
    "mean_attention_tv_mean": 0.0799038012822469,
    "argmax_agreement_mean": 0.2222222222222222
  },
  {
    "variant": "col",
    "bits": 2,
    "outlier_strength": 8.0,
    "n": 3,
    "n_tokens_mean": 96.0,
    "d_model_mean": 64.0,
    "steps_mean": 48.0,
    "outlier_strength_mean": 8.0,
    "bits_mean": 2.0,
    "approx_cache_bits_per_token_mean": 256.0,
    "k_rel_mse_mean": 0.35976821184158325,
    "v_rel_mse_mean": 0.6398146351178488,
    "k_row_scale_rel_error_mean_mean": 0.9154939452807108,
    "k_row_scale_rel_error_p95_mean": 1.0,
    "k_row_scale_rel_error_max_mean": 1.0,
    "mean_output_l2_mean": 1.327473262945811,
    "max_output_l2_mean": 2.088001330693563,
    "final_hidden_l2_mean": 1.0530711710453033,
    "mean_hidden_l2_mean": 1.065142293771108,
    "mean_attention_tv_mean": 0.08326728517810504,
    "argmax_agreement_mean": 0.3263888888888889
  },
  {
    "variant": "row",
    "bits": 2,
    "outlier_strength": 8.0,
    "n": 3
```

## Spectral associative recall

Rows emitted: `168`  
Aggregate groups: `56`

Top methods for n_items=96, correlation=0.75, query_noise=0.2:

```json
[
  {
    "method": "exact_attention",
    "n_items": 96,
    "correlation": 0.75,
    "query_noise": 0.2,
    "memory_rank": 96,
    "n": 3,
    "top1_accuracy_mean": 0.7465277777777777,
    "value_mse_mean": 0.012048648980756601,
    "mean_top_margin_mean": 0.3091692825158437
  },
  {
    "method": "ridge_full",
    "n_items": 96,
    "correlation": 0.75,
    "query_noise": 0.2,
    "memory_rank": 32,
    "n": 3,
    "top1_accuracy_mean": 0.14930555555555555,
    "value_mse_mean": 0.03953863928715388,
    "mean_top_margin_mean": 0.051149322340885796
  },
  {
    "method": "ridge_rank_16",
    "n_items": 96,
    "correlation": 0.75,
    "query_noise": 0.2,
    "memory_rank": 16,
    "n": 3,
    "top1_accuracy_mean": 0.1076388888888889,
    "value_mse_mean": 0.03955134252707163,
    "mean_top_margin_mean": 0.051336741695801415
  },
  {
    "method": "online_delta",
    "n_items": 96,
    "correlation": 0.75,
    "query_noise": 0.2,
    "memory_rank": 32,
    "n": 3,
    "top1_accuracy_mean": 0.06597222222222222,
    "value_mse_mean": 0.03689494480689367,
    "mean_top_margin_mean": 0.0516254131992658
  },
  {
    "method": "ridge_rank_8",
    "n_items": 96,
    "correlation": 0.75,
    "query_noise": 0.2,
    "memory_rank": 8,
    "n": 3,
    "top1_accuracy_mean": 0.05555555555555555,
    "value_mse_mean": 0.03787818054358164,
    "mean_top_margin_mean": 0.039404875288407006
  }
]
```

## Next code moves

- Add a region-wipeout retention simulator.
- Add a dormant-token sponsorship simulator.
- Add a pointer-chase depth/cache heatmap.
- Add plotting script once metrics stabilize.
