# Concurrency Contract Kit locality / driver plan — 2026-03-23

This note sharpens **P-0538 Concurrency Contract Kit** around one product question:

> if another engineer wants to know whether a concurrency surface is portable across threads, tied to a local executor, or dependent on explicit drive loops for progress, what should version `0.1` actually export?

## Main product judgment

The first lovable version should treat **execution-context legality**, **mobility/affinity**, and **driver-liveness** as related but distinct.

A surface may:
- be legal only inside a local executor,
- remain fixed to a single thread after spawn,
- require explicit `run`, `tick`, `run_until`, or `Runtime::block_on` to make progress,
- or offer a handle that can block or spawn without driving timers or I/O.

Those are not the same support statement.

## Two new reports now worth standardizing

### 1. `mobility-affinity.report.json`
Purpose:
- answer whether a task / executor / runtime / handle can move across threads or is tied to one thread or one local execution context.

Minimum fields:
- `surface`
- `mobility_class`
- `locality_scope`
- `spawn_context_requirements`
- `cross_thread_posture`
- `claim_basis`
- `claim_ceiling`

Recommended classes:
- `send_movable`
- `same_thread_local_only`
- `local_context_required`
- `runtime_thread_bound`
- `cpu_pinned_local`
- `manual_review_required`

### 2. `driver-liveness.report.json`
Purpose:
- answer what has to keep running for the advertised work to make progress.

Minimum fields:
- `surface`
- `liveness_class`
- `drive_requirements`
- `non_driving_handles`
- `background_progress_posture`
- `claim_basis`
- `claim_ceiling`

Recommended classes:
- `background_runtime_driven`
- `explicit_drive_required`
- `localset_drive_required`
- `handle_can_block_without_driving`
- `blocking_bridge_not_cancellable`
- `manual_review_required`

## Why this belongs in P-0538 instead of a new lane

This is still concurrency-contract work because the missing value is a **receiver-facing support bundle**.

The archive already has neighboring lanes for:
- channel delivery semantics,
- runtime topology and capability choice,
- general executor abstraction,
- and service/runtime handoff support.

What is still missing is the compact contract that says:
- where the work may live,
- what it is attached to,
- and what must actively drive the system for progress.

## Suggested crate split changes

Keep the earlier split, but extend `concurrency-contract-core` with two new report types:
- `MobilityAffinityReport`
- `DriverLivenessReport`

and extend `cargo-concurrency-contract` with:
- `cargo concurrency-contract doctor --locality`
- `cargo concurrency-contract doctor --liveness`

## Best first fixtures

1. Tokio `spawn_local`
2. Tokio `LocalSet`
3. Tokio `Handle::block_on` on `current_thread`
4. Tokio `LocalRuntime`
5. `async_executor::LocalExecutor`
6. glommio `spawn_local`
7. futures `LocalPool` (later, if the first set stabilizes well)

## What the crate should provide other people

Other engineers should get:

1. one answer for whether work is movable or thread-affine;
2. one answer for whether a local context is required;
3. one answer for whether a handle or call site actually drives timers / I/O / local tasks;
4. one explicit warning when a context is valid for spawn but not sufficient for progress;
5. one bundle that keeps locality truth distinct from fairness, cancellation, and recovery.

## Guardrails

- Do not collapse `!Send` support into “thread-safe enough”.
- Do not collapse local spawning into background progress.
- Do not collapse handle availability into driver availability.
- Do not turn this into a generic executor abstraction or benchmark lane.
