# Entmax support-recovery probe

Code: `experiments/entmax_support_recovery/entmax_support_probe.py`

Inspired by support-aware decoding for entmax attention. The probe compares page policies by whether they recover the exact sparse support and how much probability mass they drop.

Run:

```bash
python experiments/entmax_support_recovery/entmax_support_probe.py \
  --out artifacts/probe-results/REV0005_ENTMAX_SUPPORT_SMOKE.json \
  --csv artifacts/probe-results/REV0005_ENTMAX_SUPPORT_SMOKE.csv
```

Key outputs: exact support rate, dropped mass, output error, support coverage.
