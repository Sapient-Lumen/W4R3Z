# Scenario — Tokio runtime shutdown timeout unblocks caller but blocking work survives

This scenario keeps one ordinary runtime lie visible:

> `shutdown_timeout` returned, therefore the service is fully stopped.

That claim is too strong.
Tokio documents that started `spawn_blocking` work cannot be aborted once running, and runtime `shutdown_timeout` can unblock the caller while outstanding work and threads keep running.

The lifecycle lane should therefore emit both:

- a `shutdown-phase.report` showing that the stop path reached `runtime_wait_abandoned` rather than a stronger drain phase,
- and a `timeout-aftermath.receipt` showing that blocking work still survives after timeout returns.
