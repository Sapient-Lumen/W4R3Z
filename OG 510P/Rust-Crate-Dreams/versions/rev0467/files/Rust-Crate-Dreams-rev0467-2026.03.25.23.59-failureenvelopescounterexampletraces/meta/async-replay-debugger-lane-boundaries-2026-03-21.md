
# async-replay-debugger lane boundaries — 2026-03-21

This note keeps **P-0073 Async Replay Debugger Kit** from collapsing into adjacent lanes.

## What this lane is for

This lane is for a **reviewable async incident replay contract** over one captured bug bundle or debugging workflow.
It should answer:

- what schedule authority exists,
- what time basis is being replayed,
- what instrumentation coverage actually exists,
- which effects were captured versus left live,
- and what replay fidelity is honestly justified.

## Keep this distinct from nearby lanes

### Distinct from `P-0009 Deterministic Async Lab`

`P-0009` is the harness/minimization lane.
`P-0073` is the support/review contract that describes what an async incident bundle can honestly replay.

### Distinct from `P-0097 Determinism Lab Kit`

`P-0097` is the broader capture/minimize/replay workflow lane.
`P-0073` is specifically the async-incident support contract around schedule, time, coverage, effects, and fidelity.

### Distinct from `P-0239 DetTrace Spec Kit`

`P-0239` is the shared trace/cassette artifact-spec lane.
`P-0073` is the receiver-facing contract above imported traces.

### Distinct from `P-0057 Run Record Kit` and `P-0106 Test Run Artifact Standard Kit`

Those lanes are generic run/test artifact contracts.
`P-0073` is specifically about async incident replay truth.

### Distinct from `P-0532 Async Runtime Assurance Profile Kit`

`P-0532` is the runtime-choice / shutdown / qualification lane.
`P-0073` is the replay/debugging lane.

### Distinct from raw `tracing`, `tokio-console`, `loom`, `shuttle`, and narrow cassettes

Those tools are substrate.
`P-0073` is the boring review contract above them.

## Five truths this lane must keep separate

1. **schedule basis** — exhaustive model, recorded schedule, seeded scheduler, live trace only, or manual review;
2. **time basis** — wall clock, paused Tokio test time, synthetic timeline, imported timestamps, or manual review;
3. **instrumentation coverage** — task/resource/span coverage, lineage propagation, and blind spots;
4. **effect boundary** — which nondeterministic effect classes were captured, stubbed, seeded, or left live;
5. **replay fidelity** — inspection only, timeline reconstruction, narrow replay, deterministic local replay, minimized schedule repro, or manual review.

## Ordinary mistakes future passes must resist

Do not let the archive treat any of the following as interchangeable:

- a saved seed and an exhaustive model,
- paused Tokio time and wall-clock incident replay,
- a pretty task timeline and complete spawned-task lineage,
- one stream cassette and whole-application replay,
- a deterministic local test harness and a production incident replay bundle,
- or “supports tracing” and “supports replay”.

## Preferred artifact vocabulary

- `schedule-basis.receipt`
- `time-basis.receipt`
- `instrumentation-coverage.report`
- `effect-boundary.receipt`
- `replay-fidelity.report`
- `async-incident-bundle.manifest`

If a future pass adds more detail, it should extend one of those objects before inventing a vague new umbrella.
