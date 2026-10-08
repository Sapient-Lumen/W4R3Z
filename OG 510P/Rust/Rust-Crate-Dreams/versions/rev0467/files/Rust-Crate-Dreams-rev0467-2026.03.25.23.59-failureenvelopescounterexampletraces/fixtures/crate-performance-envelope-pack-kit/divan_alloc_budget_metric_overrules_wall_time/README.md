# divan_alloc_budget_metric_overrules_wall_time

A crate uses Divan to inspect both throughput and allocation behavior for a small parsing workload.
The maintainer’s actual public promise is an **allocation budget**, not the fastest wall-clock number.

The fixture exists to force the pack to record that:

- a scenario may emit several useful metrics,
- allocation profiling can perturb timing,
- and the authoritative metric should still be the one matching the user-facing promise.
