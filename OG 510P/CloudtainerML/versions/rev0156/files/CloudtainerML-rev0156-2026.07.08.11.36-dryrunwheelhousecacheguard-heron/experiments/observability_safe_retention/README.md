# Observability-safe memory retention probe

A toy delayed-cost memory-retention simulator. Policies must choose a bounded set
of memory items using online features only; evaluation reveals future utility,
stale risk, reacquisition delay, and redundancy costs.

Run:

```bash
python experiments/observability_safe_retention/osmr_probe.py
```

Output:

```text
artifacts/probe-results/REV0009_OBSERVABILITY_SAFE_RETENTION_SMOKE.json
artifacts/probe-results/REV0009_OBSERVABILITY_SAFE_RETENTION_SMOKE.csv
```
