# Frontier salience snapshot — 2026-03-21-155

This pass did **not** add another web framework, another probe endpoint helper, or another deployment control plane.
It added **P-0534 Service Readiness & Drain Contract Kit**.

## Why this frontier moved up

The current substrate now makes the missing layer much sharper:

- Tower makes **admission readiness** concrete via `poll_ready` / `ready`, but that is not the same as external readiness or startup completion;
- hyper documents graceful shutdown as “stop allowing new requests while allowing currently in-flight requests to complete”, but not a portable contract layer above that;
- axum exposes server-level graceful shutdown support, but does not join activation gates, health routes, and timeout aftermath into one review artifact;
- tonic-health proves that a real health channel exists for gRPC services, but not that all service readiness surfaces are unified;
- Tokio shutdown guidance and `TaskTracker` make stop-and-wait semantics concrete, but not a cross-framework service-transition bundle;
- partial crates like `tokio-graceful-shutdown` prove appetite for structure, while still leaving readiness and in-flight-fate truth fragmented.

That combination means “supports graceful shutdown and health checks” is now too vague as a crate claim.
A worthy crate in this frontier should publish at least:

1. **activation gate** truth,
2. **readiness surface** truth,
3. **health channel** truth,
4. **shutdown trigger** truth,
5. **drain policy** truth,
6. **in-flight fate** truth.

## Main conclusion

Promote **P-0534** quickly, but keep it narrow.
The sharper next move is not another framework and not another endpoint macro.
It is a boring contract that keeps **activation**, **readiness**, **health**, **triggers**, **drain**, and **request fate** separately reviewable.

## Ranked near-term frontier from this pass

1. **P-0534 Service Readiness & Drain Contract Kit** — strengthened because real substrate exists but the contract layer is still missing.
2. **P-0095 Task Supervision & Restart Kit** — remains adjacent because service drain often depends on supervised background work, without becoming the same lane.
3. **P-0520 Crate Lifecycle Surface Pack Kit** — remains strong because service drain truth is still a specialized slice of the broader lifecycle frontier.
4. **P-0532 Async Runtime Assurance Profile Kit** — remains adjacent because runtime choice and service-transition truth are related but distinct.
5. **P-0529 Channel Surface Contract Kit** — remains adjacent because backpressure/delivery semantics influence readiness without replacing it.

## Keep these boundaries sharp

- **P-0534** is activation gate + readiness surface + health channel + shutdown trigger + drain policy + in-flight fate.
- framework-specific helpers are separate.
- deployment/orchestration systems are separate.
- supervisor/restart policy is separate.
- channel semantics are separate.

Do not let “service readiness support” flatten those into one fake crate.
