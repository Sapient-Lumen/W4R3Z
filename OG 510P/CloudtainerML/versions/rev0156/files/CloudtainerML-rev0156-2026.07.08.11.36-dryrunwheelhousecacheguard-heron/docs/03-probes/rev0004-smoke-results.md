# rev0004 probe smoke results

These are smoke results, not conclusions. They confirm the new probes run and emit structured data.

## Region-wipeout retention

Rows emitted: `240`  
Aggregate groups: `30`

Top success rates:

```json
[
  {
    "policy": "even_region_quota",
    "n_regions": 6,
    "budget": 32,
    "n": 8,
    "success_rate": 1.0,
    "coverage_mean": 1.0,
    "empty_region_fraction_mean": 0.0,
    "retained_vital_fraction_mean": 0.8958333333333333
  },
  {
    "policy": "even_region_quota",
    "n_regions": 10,
    "budget": 32,
    "n": 8,
    "success_rate": 1.0,
    "coverage_mean": 1.0,
    "empty_region_fraction_mean": 0.0,
    "retained_vital_fraction_mean": 0.8875
  },
  {
    "policy": "vital_oracle",
    "n_regions": 6,
    "budget": 8,
    "n": 8,
    "success_rate": 1.0,
    "coverage_mean": 1.0,
    "empty_region_fraction_mean": 0.0,
    "retained_vital_fraction_mean": 0.5
  },
  {
    "policy": "vital_oracle",
    "n_regions": 6,
    "budget": 16,
    "n": 8,
    "success_rate": 1.0,
    "coverage_mean": 1.0,
    "empty_region_fraction_mean": 0.0,
    "retained_vital_fraction_mean": 1.0
  },
  {
    "policy": "vital_oracle",
    "n_regions": 6,
    "budget": 32,
    "n": 8,
    "success_rate": 1.0,
    "coverage_mean": 1.0,
    "empty_region_fraction_mean": 0.0,
    "retained_vital_fraction_mean": 1.0
  },
  {
    "policy": "vital_oracle",
    "n_regions": 10,
    "budget": 16,
    "n": 8,
    "success_rate": 1.0,
    "coverage_mean": 1.0,
    "empty_region_fraction_mean": 0.0,
    "retained_vital_fraction_mean": 0.5
  },
  {
    "policy": "vital_oracle",
    "n_regions": 10,
    "budget": 32,
    "n": 8,
    "success_rate": 1.0,
    "coverage_mean": 1.0,
    "empty_region_fraction_mean": 0.0,
    "retained_vital_fraction_mean": 1.0
  },
  {
    "policy": "even_region_quota",
    "n_regions": 6,
    "budget": 16,
    "n": 8,
    "success_rate": 0.75,
    "coverage_mean": 0.9583333333333334,
    "empty_region_fraction_mean": 0.0,
    "retained_vital_fraction_mean": 0.7708333333333333
  }
]
```

## Dormant-token sponsorship

Rows emitted: `320`  
Aggregate groups: `20`

Top target-value retention rates:

```json
[
  {
    "policy": "semantic_sponsor",
    "budget": 32,
    "n": 16,
    "target_value_retention_rate": 1.0,
    "target_anchor_retention_rate": 1.0,
    "value_retained_fraction_mean": 1.0,
    "anchor_retained_fraction_mean": 1.0,
    "ordinary_retained_fraction_mean": 0.0020687061183550653
  },
  {
    "policy": "semantic_sponsor",
    "budget": 64,
    "n": 16,
    "target_value_retention_rate": 1.0,
    "target_anchor_retention_rate": 1.0,
    "value_retained_fraction_mean": 1.0,
    "anchor_retained_fraction_mean": 1.0,
    "ordinary_retained_fraction_mean": 0.017395937813440322
  },
  {
    "policy": "oracle_target",
    "budget": 8,
    "n": 16,
    "target_value_retention_rate": 1.0,
    "target_anchor_retention_rate": 1.0,
    "value_retained_fraction_mean": 0.08333333333333333,
    "anchor_retained_fraction_mean": 0.09895833333333333,
    "ordinary_retained_fraction_mean": 0.0028209628886659978
  },
  {
    "policy": "oracle_target",
    "budget": 16,
    "n": 16,
    "target_value_retention_rate": 1.0,
    "target_anchor_retention_rate": 1.0,
    "value_retained_fraction_mean": 0.08333333333333333,
    "anchor_retained_fraction_mean": 0.109375,
    "ordinary_retained_fraction_mean": 0.0067389669007021065
  },
  {
    "policy": "oracle_target",
    "budget": 32,
    "n": 16,
    "target_value_retention_rate": 1.0,
    "target_anchor_retention_rate": 1.0,
    "value_retained_fraction_mean": 0.08333333333333333,
    "anchor_retained_fraction_mean": 0.11979166666666666,
    "ordinary_retained_fraction_mean": 0.014292878635907722
  },
  {
    "policy": "oracle_target",
    "budget": 64,
    "n": 16,
    "target_value_retention_rate": 1.0,
    "target_anchor_retention_rate": 1.0,
    "value_retained_fraction_mean": 0.08333333333333333,
    "anchor_retained_fraction_mean": 0.13541666666666666,
    "ordinary_retained_fraction_mean": 0.02987086258776329
  },
  {
    "policy": "semantic_sponsor",
    "budget": 16,
    "n": 16,
    "target_value_retention_rate": 0.25,
    "target_anchor_retention_rate": 1.0,
    "value_retained_fraction_mean": 0.3125,
    "anchor_retained_fraction_mean": 1.0,
    "ordinary_retained_fraction_mean": 6.268806419257773e-05
  },
  {
    "policy": "recency_topk",
    "budget": 64,
    "n": 16,
    "target_value_retention_rate": 0.0625,
    "target_anchor_retention_rate": 0.0625,
    "value_retained_fraction_mean": 0.026041666666666664,
    "anchor_retained_fraction_mean": 0.026041666666666664,
    "ordinary_retained_fraction_mean": 0.03125
  }
]
```

## Value-outlier eviction

Rows emitted: `216`  
Aggregate groups: `18`

Top critical retention rates:

```json
[
  {
    "policy": "value_norm_topk",
    "budget": 16,
    "n": 12,
    "critical_retention_rate_mean": 1.0,
    "all_critical_retained_rate": 1.0,
    "critical_segment_coverage_mean": 1.0,
    "segment_diversity_mean": 0.7916666666666666
  },
  {
    "policy": "value_norm_topk",
    "budget": 32,
    "n": 12,
    "critical_retention_rate_mean": 1.0,
    "all_critical_retained_rate": 1.0,
    "critical_segment_coverage_mean": 1.0,
    "segment_diversity_mean": 0.9375
  },
  {
    "policy": "value_norm_topk",
    "budget": 64,
    "n": 12,
    "critical_retention_rate_mean": 1.0,
    "all_critical_retained_rate": 1.0,
    "critical_segment_coverage_mean": 1.0,
    "segment_diversity_mean": 1.0
  },
  {
    "policy": "vase_toy",
    "budget": 16,
    "n": 12,
    "critical_retention_rate_mean": 1.0,
    "all_critical_retained_rate": 1.0,
    "critical_segment_coverage_mean": 1.0,
    "segment_diversity_mean": 0.875
  },
  {
    "policy": "vase_toy",
    "budget": 32,
    "n": 12,
    "critical_retention_rate_mean": 1.0,
    "all_critical_retained_rate": 1.0,
    "critical_segment_coverage_mean": 1.0,
    "segment_diversity_mean": 0.9791666666666666
  },
  {
    "policy": "vase_toy",
    "budget": 64,
    "n": 12,
    "critical_retention_rate_mean": 1.0,
    "all_critical_retained_rate": 1.0,
    "critical_segment_coverage_mean": 1.0,
    "segment_diversity_mean": 1.0
  },
  {
    "policy": "critical_oracle",
    "budget": 16,
    "n": 12,
    "critical_retention_rate_mean": 1.0,
    "all_critical_retained_rate": 1.0,
    "critical_segment_coverage_mean": 1.0,
    "segment_diversity_mean": 0.7708333333333334
  },
  {
    "policy": "critical_oracle",
    "budget": 32,
    "n": 12,
    "critical_retention_rate_mean": 1.0,
    "all_critical_retained_rate": 1.0,
    "critical_segment_coverage_mean": 1.0,
    "segment_diversity_mean": 0.9305555555555555
  }
]
```

## Next code moves

- Add L1/L2 Tensor Cache to the spectral associative recall probe.
- Add entmax/sparsemax support-recovery tensor probe.
- Train the first tiny transformer only after at least one symbolic trap is stable and visually interesting.
