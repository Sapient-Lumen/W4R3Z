# Scenario family — OpenTelemetry bridge route drops logs without explicit extra glue

This fixture family exists for crates that present `tracing` + OpenTelemetry as if one bridge automatically covers every signal family.

It is meant to catch support drift such as:

- the crate correctly exports traces,
- maybe also exports metrics,
- but still implies that log-style events automatically reach OpenTelemetry collectors through the same route,
- or release notes forget to mark the boundary between trace/metric routes and log routes.

A good observability pack should make four things explicit:

1. which signal families are intended to ride trace, metric, or log routes,
2. whether each route is directly supported, indirectly supported with extra glue, or absent,
3. which activation recipe proves the route,
4. and where manual review begins when the route is only collector-side or backend-specific.

This family keeps “we use OpenTelemetry somewhere” separate from “all of our observability signals reach OpenTelemetry the same way”.
