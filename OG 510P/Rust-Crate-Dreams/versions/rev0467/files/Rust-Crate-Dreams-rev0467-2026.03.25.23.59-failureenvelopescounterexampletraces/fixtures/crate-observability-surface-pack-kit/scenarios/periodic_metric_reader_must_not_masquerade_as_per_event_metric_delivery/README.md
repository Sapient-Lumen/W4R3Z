# Scenario family — periodic metric reader must not masquerade as per-event delivery

This fixture family exists for crates that expose useful metrics through OpenTelemetry metrics routes.

It is meant to catch support drift such as:

- the crate advertises metric telemetry as if every measurement appears downstream as a one-to-one event,
- but the actual route aggregates measurements in memory and exports them periodically,
- or route summaries make counter/histogram support sound more immediate than it is,
- or sampled traces and aggregated metrics are described with the same completeness language.

A good observability pack should make four things explicit:

1. whether the route is periodic and aggregate-oriented,
2. whether export interval or aggregation temporality changes what operators will see,
3. whether the route is still official even though it is not a per-event stream,
4. and whether the completeness class is `aggregated_window` rather than `attempted_all_events`.
