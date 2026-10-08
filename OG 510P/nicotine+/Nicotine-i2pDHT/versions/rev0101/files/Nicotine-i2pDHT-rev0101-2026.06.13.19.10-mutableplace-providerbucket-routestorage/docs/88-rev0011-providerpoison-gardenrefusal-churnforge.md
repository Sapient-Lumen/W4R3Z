# rev0011 — providerpoison / gardenrefusal / churnforge

This page is kept for lineage. The current public snapshot is `docs/88-rev0011-dualfront-risk-implementation.md`.

rev0011 starts implementing and testing high-risk DHT guesses from multiple directions:

```text
provider claims       -> semantic probes and local provider memory
garden capacity       -> signed bounded refusal, admission fairness, churn events
lookup frontier       -> family rotation and transcript digests
```

Strongest sentence:

```text
Valid signatures are observations, not acceptance.
```

Use `docs/92-python-surface-rev0011.md` for exact module names.
