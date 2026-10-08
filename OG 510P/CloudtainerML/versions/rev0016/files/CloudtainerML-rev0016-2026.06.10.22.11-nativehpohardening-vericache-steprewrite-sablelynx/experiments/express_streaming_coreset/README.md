# Express Streaming Coreset Probe

A C++17 CPU-only smoke probe inspired by Express / Thinformer Express. This is not a reproduction of the paper; it asks whether a tiny streaming weighted cache object is even a useful baseline in the CloudtainerML cache/memory arena.

Run:

```bash
cd experiments/express_streaming_coreset
make run
```

Output:

```text
artifacts/probe-results/REV0014_EXPRESS_STREAMING_CORESET_SMOKE.json
```

Policies:

- `recent`: last-B cache rows.
- `uniform`: evenly spaced retained rows.
- `salience_oracle`: query-aware top-B upper anchor.
- `express_toy`: dependency-free streaming weighted halving surrogate.

The target metric is mean MSE to full causal attention output. The point is to decide whether compiled streaming coreset probes deserve a larger arena.
