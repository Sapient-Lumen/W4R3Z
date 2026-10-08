# Value-outlier eviction probe

Toy probe for value-aware stochastic eviction: a small number of low-attention tokens carry large value norms and critical stabilizing information.

Run:

```bash
python experiments/value_outlier_eviction/value_outlier_probe.py --quick --out artifacts/probe-results/REV0004_VALUE_OUTLIER_SMOKE.json --csv artifacts/probe-results/REV0004_VALUE_OUTLIER_SMOKE.csv
```

This tests whether protecting value-norm outliers plus sampling for diversity beats pure attention top-k under tight budgets.
