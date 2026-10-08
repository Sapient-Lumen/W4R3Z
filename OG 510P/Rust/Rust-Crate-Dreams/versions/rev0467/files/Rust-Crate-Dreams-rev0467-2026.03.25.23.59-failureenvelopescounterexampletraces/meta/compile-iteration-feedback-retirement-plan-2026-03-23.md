# Compile Iteration Feedback Kit — retirement-boundary and old-generation-drain plan (2026-03-23)

## Problem slice

The archive now has artifacts for edit scope, patch eligibility, barrier class, state continuity, activation boundary, stale-code risk, generation witness, and mixed-generation risk.
What it still lacked was one portable way to say:

1. **when old-generation code is expected to retire**,
2. **what boundary cuts it off**,
3. **whether pre-reload work has actually drained**,
4. and **how strong the witness for that claim really is**.

Current substrate makes this gap concrete:

- `subsecond` can unwind to the next hot anchor and retry there, which gives route-local retirement boundaries rather than a global cutover claim;
- `subsecond` nested `call` boundaries mean one stack can switch generations while other routes may still predate that switch;
- Chaud explicitly says a hot reload can complete while older code keeps running indefinitely if no hot entrypoint is called;
- `hot-lib-reloader` exposes `about_to_reload` / `wait_for_reload` hooks and explicit serialization handoff, but those are lifecycle markers rather than proofs that all old callbacks/tasks/routes drained.

## Desired product shape

### `retirement-boundary.report.json`

This artifact should answer:

- what subject is being described (`call_stack`, `entrypoint_family`, `request_class`, `task_family`, `callback_registry`, `dynamic_library`, `whole_process`);
- what retirement class is claimed (`after_unwind_to_anchor`, `after_next_entrypoint_return`, `manual_drain_required`, `unbounded_or_unknown`, `immediate_library_swap_only`);
- what anchor or boundary is relevant (`next subsecond::call`, `#[chaud::hot]` entrypoint, reload observer pair, explicit restart hook);
- whether the claim is stack-scoped, route-family-scoped, library-scoped, or process-scoped;
- what caveats still require manual review.

### `old-generation-drain.report.json`

This artifact should answer:

- what work class is being discussed (`call_stack`, `request`, `callback_queue`, `task_set`, `dynamic_library`, `whole_process`);
- whether older work is `drained_observed`, `anchor_scoped_rewind_observed`, `reload_only_no_drain_proof`, `mixed_inflight_possible`, or `unknown`;
- what witness basis exists (`stack_unwind`, `reload_observer`, `entrypoint_reinvocation`, `manual inspection`, `framework adapter`);
- whether older work may still remain in callbacks/tasks/trait-object routes;
- what fallback action remains when drain completeness cannot be proven honestly.

## Product boundary

The crate should not attempt to solve hot reloading itself.
It should stay above:

- watchers,
- patch engines,
- linkers,
- framework-specific adapters,
- and process supervisors.

Its job is to emit **reviewable receipts and reports** about retirement boundaries and old-generation drain honesty.

## MVP

- structs for `RetirementBoundaryReport` and `OldGenerationDrainReport`
- import adapters for Subsecond / Chaud / hot-lib-reloader facts
- doctor checks for “reload complete” overclaims
- bundle writer that keeps retirement and drain truth separate from activation, generation, and stale-code reachability

## Good first proving grounds

1. Subsecond route where unwind-to-anchor retires one call path without proving whole-process retirement.
2. Chaud case where a hot reload completes but old code remains unbounded until a hot entrypoint is called.
3. hot-lib-reloader case where before/after reload events surround a library swap without proving callback/task drain.
4. Portable bundle manifest that lists activation, generation witness, retirement boundary, and old-generation drain separately.
