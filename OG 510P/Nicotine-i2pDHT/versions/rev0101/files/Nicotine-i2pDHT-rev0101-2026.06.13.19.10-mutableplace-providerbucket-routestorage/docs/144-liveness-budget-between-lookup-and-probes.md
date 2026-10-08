# Liveness budget between lookup and probes

`adaptivealpha.py` can say: widen, hold, quarantine, or accept. `privateprovider.py` can say: probe these providers with this raw-key/commitment/decoy shape. The risky gap is the handoff.

`livenessbudget.py` adds a local report:

```text
lookup_queries = alpha * beta
metadata_points = query_cost + commitment_probe_cost + raw_probe_cost + decoy_cost
raw_key_exposures = count(real raw-key probes)
real_probe_families = families receiving real probes
decoy_ratio = decoys / all probes
```

The first policies are intentionally simple:

- stop if the lookup/probe combination exceeds local metadata points;
- reduce exposure before chasing liveness if raw keys exceed budget;
- back off on useful refusals instead of flooding generous nodes;
- quarantine captured fast windows even if the plan is otherwise cheap;
- require real provider probes to cross enough families;
- require decoys when the user elected a decoy-shaped budget.

This does not make provider confirmation private. It prevents the cube from pretending provider confirmation is free.
