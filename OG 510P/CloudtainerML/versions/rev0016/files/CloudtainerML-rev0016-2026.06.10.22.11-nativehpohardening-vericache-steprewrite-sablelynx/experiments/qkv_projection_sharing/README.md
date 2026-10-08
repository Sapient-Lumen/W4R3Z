# QKV projection sharing mini-arena

Tiny CPU probe inspired by the 2026 QKV projection-sharing paper. It trains four small attention variants on synthetic key-value lookup:

- `qkv`: independent Q, K, V projections
- `k_equals_v`: independent Q, shared K/V projection
- `q_equals_k`: shared Q/K, independent V
- `q_equals_k_equals_v`: one projection for Q/K/V

The smoke run is intentionally small. Treat it as a harness and sanity-check, not a reproduction of the ICML-scale paper.

Run:

```bash
python experiments/qkv_projection_sharing/qkv_projection_probe.py --steps 120 --out artifacts/probe-results/REV0005_QKV_PROJECTION_SMOKE.json
```
