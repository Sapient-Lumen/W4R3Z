# Probe: QKV projection sharing

Purpose: test whether independent Q/K/V projections matter on a tiny content-addressed lookup task.

Variants:

- `qkv`: independent projections; full K+V cache.
- `k_equals_v`: separate Q, shared K/V; half cache.
- `q_equals_k`: shared Q/K, separate V; no cache saving.
- `q_equals_k_equals_v`: one projection; half cache but symmetric and likely brittle.

Smoke command:

```bash
python experiments/qkv_projection_sharing/qkv_projection_probe.py --steps 120 --out artifacts/probe-results/REV0005_QKV_PROJECTION_SMOKE.json
```

Interpretation: this is a harness. A real test needs more seeds, more steps, and direction-sensitive tasks beyond simple key-value lookup.
