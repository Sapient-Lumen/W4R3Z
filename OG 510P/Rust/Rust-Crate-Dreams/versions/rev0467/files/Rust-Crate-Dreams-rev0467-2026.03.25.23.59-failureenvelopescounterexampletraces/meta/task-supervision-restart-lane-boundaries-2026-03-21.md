# task-supervision-restart lane boundaries — 2026-03-21

This note keeps **P-0095 Task Supervision & Restart Kit** from collapsing into adjacent lanes.

## What this lane is for

This lane is for a **reviewable supervision contract** over long-lived async/background work.
It should answer:

- what restart blast radius exists,
- which failures or health signals trigger restart,
- what state resets versus survives,
- what shutdown timeout really means,
- and what bundle another reviewer gets when the supervision policy is exercised.

## Keep this distinct from nearby lanes

### Distinct from `P-0520 Crate Lifecycle Surface Pack Kit`

`P-0520` is the broader receiver-facing shutdown/lifecycle lane.
`P-0095` is specifically the restart/topology/health/state-reset lane for supervised work.

### Distinct from `P-0073 Async Replay Debugger Kit`

`P-0073` is the replay/debugging lane.
`P-0095` is the supervision/restart semantics lane.

### Distinct from `P-0532 Async Runtime Assurance Profile Kit`

`P-0532` is about runtime family, shutdown traits, allocation posture, and qualification basis.
`P-0095` is about application/task supervision above that runtime.

### Distinct from actor frameworks and worker libraries

Those are substrate.
`P-0095` is the boring review contract above them.

### Distinct from generic structured-concurrency / scoped-task crates

Cancellation structure is adjacent, but scoped child lifetime is not the same thing as restart policy, meltdown logic, or restart-state truth.

## Six truths this lane must keep separate

1. **supervision topology** — static/dynamic membership, dependency ordering, and restart blast radius;
2. **restart policy** — restart class, trigger classes, backoff, and meltdown windows;
3. **health / readiness basis** — stable-start criteria, liveness basis, and unresponsive-task action;
4. **state reset basis** — template clone, fresh factory, shared external state, persisted rehydrate, or manual review;
5. **shutdown escalation** — stop signal, graceful phase, timeout aftermath, and blocking-work posture;
6. **failure bundle** — the receipts and attachments exported for review/support.

## Ordinary mistakes future passes must resist

Do not let the archive treat any of the following as interchangeable:

- `JoinSet` membership and supervisor topology,
- panic restart and heartbeat/deadline restart,
- clone-on-restart and persisted/shared-state restart,
- waiting for shutdown and actually aborting work,
- a restart loop and a deliberate meltdown policy,
- or one actor framework's semantics and a shared supervision contract.

## Preferred artifact vocabulary

- `supervision-topology.receipt`
- `restart-policy.receipt`
- `health-source.receipt`
- `state-reset.receipt`
- `shutdown-escalation.receipt`
- `supervision-failure-bundle.manifest`

If a future pass adds more detail, it should extend one of those objects before inventing a vague new umbrella.
