# Compile Iteration Feedback Kit — generation-witness and mixed-generation plan (2026-03-23)

## Problem slice

The archive now has artifacts for edit scope, patch eligibility, barrier class, state continuity, activation boundary, and stale-code risk.
What it still lacked was one portable way to say:

1. **what code generation a route is on now**,
2. **what witness supports that claim**,
3. **how coarse that witness is**,
4. and **whether the process may still be running mixed generations at once**.

Current substrate makes this gap concrete:

- `subsecond` detours calls through a jump table to the latest function pointer but explicitly says pointer versioning metadata does not yet exist;
- `subsecond` nested `call` boundaries mean patch cut points are route-local rather than a global takeover switch;
- Chaud explicitly says old code can continue after reload via stored routes;
- `hot-lib-reloader` can name successive library loads with a `load_counter`, but that still identifies a library generation more readily than it proves whole-process route coverage.

## Desired product shape

### `generation-witness.report.json`

This artifact should answer:

- what subject is being described (`entrypoint`, `callback`, `task`, `dynamic_library`, `framework_state_bucket`, `route_family`);
- what generation identity exists (`load_counter`, `latest_detoured`, `static_build`, `opaque_new_generation`, `mixed_or_unknown`);
- what witness basis exists (`jump_table`, `shadow_dylib_name`, `framework adapter`, `manual inspection`, `route annotation`);
- how precise the witness is (`global`, `dynamic-library`, `call-wrapped`, `entrypoint-gated`, `unknown`);
- whether unchanged code can still look “new” under this witness model;
- what manual review caveats remain.

### `mixed-generation-risk.report.json`

This artifact should answer:

- whether mixed-generation execution is possible, expected, or already observed;
- what routes can remain old (`function_pointer`, `trait_object`, `running_task`, `thread_local_copy`, `framework cache`, `captured callback`);
- what routes are known to switch eagerly;
- whether the issue is bounded by a call site, reload event, framework pass, or explicit restart;
- what fallback action remains when homogeneous generation cannot be claimed honestly.

## Product boundary

The crate should not attempt to solve hot reloading itself.
It should stay above:

- watchers,
- patch engines,
- linkers,
- framework-specific adapters,
- and process supervisors.

Its job is to emit **reviewable receipts and reports** about generation identity and mixed-generation risk.

## MVP

- structs for `GenerationWitnessReport` and `MixedGenerationRiskReport`
- import adapters for Subsecond / Chaud / hot-lib-reloader facts
- doctor checks for “latest build” overclaims
- bundle writer that keeps generation truth separate from activation, continuity, and stale-code reachability

## Good first proving grounds

1. Subsecond route where the jump table proves latest detour but not stable unchanged-function identity.
2. Subsecond nested `call` example where the inner call updates before outer state is rebuilt.
3. Chaud case where entrypoint activation occurs but stored trait objects can still hit old code.
4. hot-lib-reloader case where `load_counter` names the new dylib generation but does not prove every callback/task switched.
5. Portable bundle manifest that lists activation, stale-code risk, generation witness, and mixed-generation risk separately.
