# Fresh hunt digest — rev0006

New emphasis: cache/memory as an interface with multiple granularities, not a flat token buffer.

## Newly promoted questions

- Can modular trained KV memories compose, or do independently trained modules collide?
- Can cache-as-recurrence preserve facts across hundreds of chunk folds without retraining?
- Can tiny models be trained to make their own KV states more compressible?
- Is equal-byte cache quality better improved by retaining more low-bit tokens or fewer high-bit tokens?
- Do tree/branch workloads require ancestor-aware cache policy rather than token-level recency?

## Code already in this revision

- `experiments/hierarchical_fademem_cache/fademem_hierarchy_probe.py`
- `experiments/bank_of_values/bov_probe.py`
- `experiments/blurry_window_attention/blurry_window_probe.py`
- `experiments/branch_cache_sharing/branch_cache_sharing_probe.py`
- `experiments/attention_runtime_termination/art_probe.py`

## Best next tiny code targets

1. `CELL-072` token-precision frontier, because it extends existing KV quantization work.
2. `CELL-069` cache-compressibility training, because it tests whether compressibility is learned.
3. `CELL-068` KV-Fold drift plateau, because it probes cache as recurrent state.
