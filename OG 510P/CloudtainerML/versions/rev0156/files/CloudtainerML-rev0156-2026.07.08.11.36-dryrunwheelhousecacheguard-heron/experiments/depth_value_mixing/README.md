# Depth-value mixing probe

Geometry probe inspired by Depth-Attention (`arXiv:2606.05014`). It simulates useful information living at different depths and compares last-layer, uniform/residual-style averaging, query-conditioned depth mixing, and an oracle.

```bash
python experiments/depth_value_mixing/depth_value_mixing_probe.py \
  --out artifacts/probe-results/REV0005_DEPTH_VALUE_MIXING_SMOKE.json \
  --csv artifacts/probe-results/REV0005_DEPTH_VALUE_MIXING_SMOKE.csv
```
