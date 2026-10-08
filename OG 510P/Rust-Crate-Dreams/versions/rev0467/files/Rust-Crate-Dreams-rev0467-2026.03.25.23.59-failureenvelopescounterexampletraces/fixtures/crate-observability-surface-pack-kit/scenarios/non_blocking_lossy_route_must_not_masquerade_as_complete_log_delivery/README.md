# Scenario family — nonblocking lossy log route must not masquerade as complete delivery

This fixture family exists for crates that publish a real `fmt`/file log route via `tracing_appender::non_blocking`, but where the route is explicitly configured in **lossy** mode.

It is meant to catch support drift such as:

- the crate advertises log delivery as part of its official support surface,
- but the chosen writer drops lines when the buffer fills,
- or the summary still sounds like a complete event stream,
- or the route depends on `WorkerGuard` while release notes and support docs forget to mention exit sensitivity.

A good observability pack should make four things explicit:

1. whether the route is blocking, buffered-lossy, or buffered-with-backpressure,
2. whether dropped-line counters exist and are part of the support story,
3. whether `WorkerGuard` is required for honest exit behavior,
4. and whether the completeness class remains `best_effort_buffered` rather than `attempted_all_events`.
