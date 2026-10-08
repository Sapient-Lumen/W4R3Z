# Crate Observability Surface Pack Kit fixtures

These fixtures exist to keep **P-0518** honest about five questions:

1. which signals are intentionally part of the crate’s support surface,
2. how another team actually activates them,
3. which route really carries them,
4. what semantic/schema posture they claim,
5. and where sensitivity review still begins.

The point is not to prove that a crate is "observable enough" in the abstract.
The point is to make emitted-signal claims reviewable instead of reconstructing them from `RUST_LOG`, README snippets, console setup, exporter glue, and backend dashboards.


The point is also to keep **route truth** separate from **delivery truth**. A crate can honestly say that a signal reaches `fmt`, `otel_trace`, or `otel_metric` while still needing to admit that the route is lossy, sampled, periodic, or flush-dependent.
