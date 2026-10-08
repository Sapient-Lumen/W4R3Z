# Dynamic state-merging probe

Symbolic/tensor simulator inspired by Dynamic Linear Attention (`arXiv:2606.10650`). It compares fixed block summaries to drift-aware dynamic boundaries plus capacity-bounded adjacent merging.

```bash
python experiments/dynamic_state_merging/dynamic_state_merging_probe.py \
  --out artifacts/probe-results/REV0005_DYNAMIC_STATE_MERGING_SMOKE.json \
  --csv artifacts/probe-results/REV0005_DYNAMIC_STATE_MERGING_SMOKE.csv
```
