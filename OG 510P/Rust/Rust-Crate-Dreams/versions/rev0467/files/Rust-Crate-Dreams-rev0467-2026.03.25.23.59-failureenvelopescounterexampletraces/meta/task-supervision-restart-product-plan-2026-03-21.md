# Task Supervision & Restart Kit — product plan (2026-03-21)

This note sharpens **P-0095 Task Supervision & Restart Kit** into a more implementation-ready `0.1` shape.

## Core question

If somebody started building **P-0095** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

The first implementation should not become a new actor framework, a new async runtime, or a full distributed supervisor.
It should provide one boring, reviewable **supervision contract** above today's task groups, shutdown helpers, actor supervisors, and ad hoc keepalive loops.

`0.1` should make six things first-class:

1. **supervision topology** — membership shape, dependency/order basis, and restart blast radius;
2. **restart policy** — restart class, trigger classes, backoff, meltdown windows, and reset-after behavior;
3. **health / readiness basis** — how a child becomes stable and how hung work is detected;
4. **state reset basis** — whether restart begins from a template clone, a fresh factory, shared `Arc` state, or persisted rehydrate state;
5. **shutdown escalation** — stop signal, graceful phase, timeout aftermath, and blocking-work posture;
6. **failure bundle** — the attached receipts and timeline/log artifacts for support handoff.

## What `0.1` should provide other people

- one compact `supervision-topology.receipt.json`
- one compact `restart-policy.receipt.json`
- one compact `health-source.receipt.json`
- one compact `state-reset.receipt.json`
- one compact `shutdown-escalation.receipt.json`
- one compact `supervision-failure-bundle.manifest.json`
- one compact `restart.summary.md`
- one compact `restart.diff.json`
- one portable review/support bundle

## Commands worth shipping first

- `cargo supervise receipt`
- `cargo supervise inspect`
- `cargo supervise doctor`
- `cargo supervise diff`
- `cargo supervise bundle`

## What to import, not reinvent

- Tokio task-group facts from `JoinSet` / task handles when present
- Tokio graceful-shutdown facts from `CancellationToken` + `TaskTracker`
- `task-supervisor` restart/dead-task/backoff config when present
- `spry` readiness/startup conventions when present
- `ractor-supervisor` topology/meltdown strategy facts when present
- manual JSON/TOML descriptors for other frameworks instead of forcing one runtime model

## Suggested `0.1` doctor warnings

- `blast_radius_missing_for_shared_subsystem`
- `normal_exit_and_panic_share_same_restart_claim`
- `clone_restart_claims_state_retention_without_shared_state_basis`
- `hung_restart_claim_missing_health_basis`
- `timeout_claim_hides_blocking_task_escape`
- `shutdown_wait_claim_overstates_abort_guarantee`
- `meltdown_window_missing_for_restart_loop`

## First proving-ground scenarios

1. **A web stack with dependent HTTP and websocket children needs explicit restart blast radius, not generic “auto restart”.**
2. **A restart storm needs backoff and meltdown receipts, plus a small failure bundle for oncall review.**
3. **A clone-based task restart resets plain fields unless state is externalized.**
4. **A hung task detected by heartbeat/deadline is a different health basis from panic-only monitoring.**
5. **A graceful timeout can stop waiting while started blocking work keeps running.**

## What to leave for later

- distributed supervision across processes or hosts
- side-effect idempotence inference
- deep visual topology UIs
- universal runtime/framework adapters
- strong claims about exactly-once or transactional restart semantics
