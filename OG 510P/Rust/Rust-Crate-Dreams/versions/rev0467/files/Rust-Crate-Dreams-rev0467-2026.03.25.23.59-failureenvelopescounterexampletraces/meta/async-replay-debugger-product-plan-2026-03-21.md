
# Async Replay Debugger Kit — product plan (2026-03-21)

This note sharpens **P-0073 Async Replay Debugger Kit** into a more implementation-ready `0.1` shape.

## Core question

If somebody started building **P-0073** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

The first implementation should not try to become a new async runtime, a universal debugger, or a full-system record/replay engine.
It should provide one boring, reviewable **async incident replay contract** above today's tracing, live console telemetry, paused-time tests, schedule-control tools, and narrow effect cassettes.

`0.1` should make five things first-class:

1. **schedule basis** — whether replay authority comes from an exhaustive model, a recorded schedule, a seed, or only a live trace;
2. **time basis** — whether time is paused Tokio test time, synthetic timeline playback, imported timestamps, or live wall clock;
3. **instrumentation coverage** — which tasks, spans, wakes, and spawned futures are actually covered;
4. **effect boundary** — which nondeterministic effect classes were captured, stubbed, seeded, or left live;
5. **replay fidelity** — the strongest honest claim the bundle can make.

## What `0.1` should provide other people

- one compact `schedule-basis.receipt.json`
- one compact `time-basis.receipt.json`
- one compact `instrumentation-coverage.report.json`
- one compact `effect-boundary.receipt.json`
- one compact `replay-fidelity.report.json`
- one compact `async-incident-bundle.manifest.json`
- one compact `replay.summary.md`
- one compact `replay.diff.json`
- a portable review/support bundle

## Commands worth shipping first

- `cargo async-replay receipt`
- `cargo async-replay import-tokio-console`
- `cargo async-replay import-shuttle`
- `cargo async-replay import-stream-cassette`
- `cargo async-replay doctor`
- `cargo async-replay diff`
- `cargo async-replay bundle`
- `cargo async-replay inspect`

## What to import, not reinvent

- `console-subscriber` / `tokio-console` trace facts when present
- `tracing` span/event lineage and explicit `Instrument` / `in_current_span()` usage where observable
- paused Tokio-time facts and runtime flavor metadata for tests
- Shuttle schedules/seeds and Loom model metadata when the user already has them
- narrow effect cassettes such as stream recordings instead of pretending to own every transport-specific format
- build/runtime provenance only as imported facts, not a bespoke build system

## Suggested `0.1` doctor warnings

- `live_console_trace_claimed_as_replay`
- `paused_tokio_time_claimed_as_wall_clock_incident`
- `spawn_lineage_gap_missing_coverage_warning`
- `seeded_schedule_without_effect_receipt`
- `stream_cassette_claimed_as_whole_program_replay`
- `tokio_specific_coverage_presented_as_runtime_agnostic`
- `fidelity_claim_missing_manual_review_caveat`

## First proving-ground scenarios

1. **Tokio console telemetry is rich enough to justify an inspection bundle, but not a whole-incident replay claim by itself.**
2. **A spawned future without lineage propagation downgrades causal coverage, even when the surrounding trace looks good.**
3. **Paused Tokio time on `current_thread` is an explicit time basis, not a generic production-clock replay.**
4. **A Shuttle seed or schedule is a strong local schedule basis, but it still needs an effect-boundary receipt for whole-incident claims.**
5. **A stream cassette can be precise and still remain a slice-level replay surface.**

## What to leave for later

- universal runtime interception for every async runtime
- whole-system OS/network/process replay
- IDE-specific time-travel UX
- hosted incident portals and dashboards
- ambitious automatic cassette adapters for every ecosystem crate
- “exact production replay” claims outside clearly declared bounds
