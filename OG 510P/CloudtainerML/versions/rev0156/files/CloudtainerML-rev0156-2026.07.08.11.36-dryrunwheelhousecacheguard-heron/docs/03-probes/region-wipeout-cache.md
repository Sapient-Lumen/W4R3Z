# Probe: region-wipeout cache retention

Runnable: `experiments/region_wipeout_cache/region_wipeout_probe.py`

Question: can token-level global top-k preserve high-scoring tokens while deleting complete reasoning regions?

Policies:

- `global_topk`
- `recency_topk`
- `even_region_quota`
- `mass_segmented`
- `vital_oracle`

Primary metric: success rate where every required region retains at least one vital token.

Escalation: replace symbolic scores with attention logs from a tiny transformer trained on pointer-chase or proof-region tasks.
