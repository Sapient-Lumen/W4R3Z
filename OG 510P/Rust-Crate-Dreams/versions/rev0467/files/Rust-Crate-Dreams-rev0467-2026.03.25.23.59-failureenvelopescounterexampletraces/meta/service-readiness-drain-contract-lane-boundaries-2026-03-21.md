# service-readiness-drain-contract lane boundaries — 2026-03-21

This note keeps **P-0534 Service Readiness & Drain Contract Kit** from collapsing into adjacent lanes.

## What this lane is for

This lane is for a **reviewable service-transition contract** over startup, readiness, health exposure, drain, and shutdown aftermath.
It should answer:

- when a service is safe to advertise,
- which readiness/health surfaces exist,
- what begins drain,
- how new work is refused,
- and what happens to accepted work during drain and timeout.

## Keep this distinct from nearby lanes

### Distinct from `P-0520 Crate Lifecycle Surface Pack Kit`

`P-0520` is the broader crate-authored lifecycle/background-work lane.
`P-0534` is specifically the service-facing startup/readiness/health/drain contract for listeners and requests.

### Distinct from `P-0095 Task Supervision & Restart Kit`

`P-0095` is about restart topology, restart policy, health basis for supervised children, and failure bundles.
`P-0534` is about traffic admission, external health surfaces, and request fate during drain.

### Distinct from `P-0529 Channel Surface Contract Kit`

`P-0529` is about message delivery/backpressure semantics.
`P-0534` is about service/listener/request transition semantics.

### Distinct from framework-specific graceful-shutdown helpers

Those are substrate.
`P-0534` is the boring review contract above them.

### Distinct from deployment/control-plane products

This lane may import load-balancer or deploy hooks, but it is not a rollout orchestrator.
It describes service-transition truth; it does not schedule the rollout.

## Six truths this lane must keep separate

1. **activation gate** — listener bound, dependency warmup, stable background work, manual operator flip, or composite;
2. **readiness surface** — internal admission readiness versus external ready/not-ready surface;
3. **health channel** — liveness, readiness, gRPC health, admin-only or internal-only signals;
4. **shutdown trigger** — signal, admin request, subsystem failure, deploy hook, idle timeout, or manual review;
5. **drain policy** — accept/refuse semantics, grace budget, keepalive behavior, and timeout aftermath;
6. **in-flight fate** — accepted request fate during drain, timeout, and client-visible failure posture.

## Ordinary mistakes future passes must resist

Do not let the archive treat any of the following as interchangeable:

- `poll_ready` and “safe to put behind a load balancer”,
- liveness and readiness,
- gRPC health and HTTP admission,
- listener bind and activation completion,
- graceful shutdown and explicit timeout aftermath,
- or accepted-request completion and retry-safe client behavior.

## Preferred artifact vocabulary

- `activation-gate.receipt`
- `readiness-surface.receipt`
- `health-channel.receipt`
- `shutdown-trigger.receipt`
- `drain-policy.receipt`
- `inflight-fate.report`
- `service-transition-bundle.manifest`

If a future pass adds more detail, it should extend one of those objects before inventing a vague new umbrella.
