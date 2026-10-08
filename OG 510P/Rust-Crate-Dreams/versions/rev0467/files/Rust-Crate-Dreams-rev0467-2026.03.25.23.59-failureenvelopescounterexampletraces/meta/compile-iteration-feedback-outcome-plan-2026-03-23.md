# Compile Iteration Feedback outcome plan (2026-03-23)

## Main judgment

The next implementation-ready slice for **P-0537 Compile Iteration Feedback Kit** is a compact artifact layer for **observed live-update outcome** and **current degraded iteration mode**.

The archive already knows how to say:

- what changed,
- what fast path was theoretically available,
- when fresh code became reachable,
- what old code might still survive,
- what generation a route seems to run,
- and whether older work has drained.

It still needs an honest answer to a different question:

> after a live-update attempt, what actually happened, and what mode is the process in now?

## Why the seam is real now

Current substrate is specific enough to support these artifacts without inventing a new patch engine:

- `subsecond` exposes patch-application failure as a public enum and still separates stale-call unwind/retry from successful patch application.
- Chaud says many things can go wrong, and its documented log levels already separate unrecoverable failure from degraded-but-possibly-running states.
- `hot-lib-reloader` documents combinations that likely crash or corrupt behavior and provides reload lifecycle markers that are weaker than full post-reload health.

That means the missing crate can stay receiver-facing and artifact-first.

## Proposed artifacts

### `live-update-outcome.report.json`

Purpose: describe the observed result of one attempted live update.

Minimum fields:
- subject
- attempted_route
- observed_outcome.class
- observed_outcome.new_code_reachable
- observed_outcome.old_code_may_still_run
- observed_outcome.process_state
- evidence_basis
- confidence
- caveats
- manual_review_required

Suggested outcome classes:
- `applied_and_observed`
- `applied_but_incomplete`
- `rejected_before_switch`
- `failed_to_apply`
- `reverted_to_old_code`
- `restart_required`
- `crashed_or_inconsistent`
- `unknown`

### `degraded-iteration-mode.report.json`

Purpose: describe the current operating posture of the live-edit session after warnings, failed attempts, or known-danger combinations.

Minimum fields:
- subject
- mode_class
- trigger_basis
- limitations
- operator_guidance.recommendation
- operator_guidance.visibility
- manual_review_required

Suggested mode classes:
- `healthy_live_update`
- `degraded_live_update`
- `observe_only`
- `relink_only`
- `restart_only`
- `disabled_due_to_error`
- `crashed_or_unknown`

## What this should provide other people

A worthy crate should give another engineer:

1. one honest answer to whether a particular attempted live update actually stuck;
2. one explicit statement of whether the process is still safe enough to continue iterating in-place;
3. one separation between theoretical patchability and observed outcome;
4. one separation between degraded mode and the fallback plan that would recover from it;
5. one compact bundle that can be attached to issues, benchmarks, framework docs, or local DX guides.

## Good first proving grounds

1. **Subsecond patch application failure** — patch route remains conceptually valid, but the current attempt failed and old code may still be the only honest story.
2. **Chaud warn/error posture** — log surface distinguishes degraded live update from fully broken live update.
3. **hot-lib-reloader signature / tracing cases** — restart-required or disable-live-update posture is stronger than pretending further reloads are healthy.
4. **Portable bundle separation** — manifest inventory keeps eligibility, outcome, degraded mode, and fallback plan distinct.

## Non-goals

- Not a replacement for framework/runtime logging.
- Not a universal crash detector.
- Not an automated supervisor that restarts processes for the user.
- Not proof that the process is semantically correct after a reload.
