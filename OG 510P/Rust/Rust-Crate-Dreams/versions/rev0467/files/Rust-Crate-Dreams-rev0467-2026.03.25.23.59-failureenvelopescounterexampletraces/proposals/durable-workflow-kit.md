---
id: P-0062
title: Durable Workflow Kit — app-embedded durable execution with deterministic replay
status: idea
domains: [distributed-systems, reliability, async]
last_reviewed: 2026-03-01
evidence:
  - https://github.com/iopsystems/durable
  - https://docs.rs/duroxide
  - https://restate.dev/blog/building-a-modern-durable-execution-engine-from-first-principles/
needs:
  - Teams need a *library* they can embed, not necessarily a new platform.
  - Local dev + testing must be first-class, or adoption stalls.
risks:
  - Competing with full workflow platforms instead of complementing them.
  - Getting determinism “almost right” and creating heisenbugs.
---

## Problem
Rust apps increasingly need **long-running, reliable workflows** (provisioning, billing, ETL, retries, sagas, human-in-the-loop approvals). Today, teams either:
- hand-roll state machines + cron + queues, or
- adopt an external platform (Temporal, etc.) that may be too heavy for smaller deployments.

Rust has multiple “durable execution” efforts, but there is no de-facto **crate-grade** kit with great ergonomics, storage adapters, and replay/testing UX.

## Users & user stories
- **SaaS backend**: “If my process crashes mid-workflow, I want it to resume deterministically without duplicate side effects.”
- **CLI / automation**: “I want durable tasks in a single binary with an embedded DB.”
- **Edge / on-prem**: “I want durability without depending on a separate workflow cluster.”

## Prior art (and why it’s insufficient)
- `durable` / “Flawless” style approaches demonstrate viability, but aren’t a stable, modular ecosystem substrate. https://github.com/iopsystems/durable
- `duroxide` provides durable execution primitives, but lacks a broadly standardized workflow surface + conformance/test story. https://docs.rs/duroxide
- Restate’s writeup illustrates the architectural space (event log, deterministic replay), but it’s a full engine/platform, not a small crate kit. https://restate.dev/blog/building-a-modern-durable-execution-engine-from-first-principles/

## Design goals / non-goals
**Goals**
- Deterministic replay model that is **auditable** and **testable**.
- Storage adapters: SQLite (embedded) + Postgres (shared) first.
- Clear **effect boundaries**: side effects must go through “activities” that can be recorded/deduped.
- Great local UX: run workflows locally, inspect history, time-travel debugging.

**Non-goals**
- Replacing full workflow platforms.
- Providing a proprietary service; the crate should be self-hostable.

## Architecture & API sketch
Core pieces:
- `WorkflowContext`: provides deterministic APIs (time, random, signals, state).
- `Activity<T>`: explicit boundary for side effects; results recorded in history.
- `WorkflowFn`: an async function that can be replayed from history.
- `HistoryStore`: trait for persisting event log + workflow metadata.
- `Runner`: executes workflows, polls for timers, dispatches activities.

Sketch:
```rust
async fn signup(ctx: WorkflowContext, user_id: UserId) -> Result<()> {
    let profile = ctx.activity(fetch_profile(user_id)).await?;
    ctx.sleep(Duration::from_secs(60)).await;
    ctx.activity(send_welcome_email(profile.email)).await?;
    Ok(())
}
```

### Determinism model
- Deterministic sources: `ctx.now()`, `ctx.rand()`, `ctx.uuid()` are replayed from history.
- All external IO must go through activities.
- Panic handling records failure and allows retry policies.

## Security / safety model
- History is an append-only log with checksums; detect tampering/corruption.
- Activity deduplication keys to prevent duplicate external effects.
- Optional encryption-at-rest for history stores.

## Maintenance & governance plan
- Keep core dependency-light; adapters live in separate crates.
- Conformance suite: “replay equivalence” fixtures + storage adapter tests.
- Publish “compat policy” for history format (versioned schema with migration tooling).

## Milestones
**0.1**
- Minimal runner + SQLite store + activities + timers + replay.
- CLI: `workflow inspect <id>` prints history.

**0.2**
- Postgres store + distributed worker mode for activities.
- Test harness: deterministic time + activity fakes.

**1.0**
- Stable history schema + migration tooling.
- Observability integration (`tracing`, OpenTelemetry hooks).

## Open questions
- How opinionated should the retry/backoff model be?
- How to support schema evolution for workflow inputs/outputs?
- How to expose cancellation/structured concurrency semantics cleanly?

## Sources
- https://github.com/iopsystems/durable
- https://docs.rs/duroxide
- https://restate.dev/blog/building-a-modern-durable-execution-engine-from-first-principles/
