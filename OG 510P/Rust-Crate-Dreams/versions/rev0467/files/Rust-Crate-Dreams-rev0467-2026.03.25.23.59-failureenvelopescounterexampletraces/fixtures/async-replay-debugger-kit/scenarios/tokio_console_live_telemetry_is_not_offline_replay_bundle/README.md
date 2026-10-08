# tokio-console live telemetry is not an offline replay bundle

This scenario captures a service instrumented with `console-subscriber` and viewed with `tokio-console`.
The important truth is that the task/resource telemetry is rich and useful, but the bundle still needs an honest fidelity claim.

What the receipts should prove:

- which runtime telemetry source produced the data,
- whether task and span lineage are complete or partial,
- and that this artifact supports inspection/timeline reconstruction rather than bluffing deterministic replay.
