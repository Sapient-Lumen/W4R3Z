---
id: P-0073
title: Async Replay Debugger Kit — schedule-basis receipts, time-basis receipts, effect-boundary capture, and replay-fidelity reports
status: idea
domains: [async, debugging, determinism, tooling, tracing, tokio, replay]
last_reviewed: 2026-03-21
evidence:
  - https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
  - https://docs.rs/console-subscriber/latest/console_subscriber/
  - https://docs.rs/crate/tokio-console/latest
  - https://docs.rs/tokio/latest/tokio/task/
  - https://docs.rs/tokio/latest/tokio/time/fn.pause.html
  - https://tokio.rs/tokio/topics/testing
  - https://docs.rs/tracing/latest/tracing/
  - https://docs.rs/tracing/latest/tracing/trait.Instrument.html
  - https://docs.rs/loom/latest/loom/
  - https://docs.rs/shuttle/latest/shuttle/
  - https://docs.rs/sturgeon/latest/sturgeon/
---

# Problem

Rust still lacks a **boring, reviewable async incident replay contract** for the bugs that only happen under one schedule, one timing profile, or one unlucky interaction between runtime state and external effects.

The substrate is real, but fragmented:

- the Rust project now explicitly says first-class support for debugging `async` code is still missing from the overall debugging experience;
- `tokio-console` and `console-subscriber` provide rich **live** telemetry over runtime-emitted `tracing` data, but that path is Tokio-specific today and still depends on experimental runtime instrumentation;
- `tracing` provides structured spans/events and explicit future instrumentation, but coverage depends on whether spans are actually propagated into spawned tasks;
- Tokio exposes cooperative task scheduling and paused/auto-advanced test time, which is useful but is not the same thing as full schedule capture or wall-clock replay;
- `loom` explores many valid concurrent executions exhaustively under its model, while `shuttle` controls schedules and can reproduce failing schedules deterministically from saved schedules/seeds;
- `sturgeon` shows that some effect slices, such as async streams with timing, can already be recorded and replayed with useful fidelity.

What is still missing is one crate lane that helps another team answer, with portable artifacts:

1. **What schedule authority exists?**
2. **What time basis is being replayed?**
3. **What instrumentation coverage actually exists?**
4. **Which external effects were captured, stubbed, or left live?**
5. **What replay fidelity is honestly justified by the artifact?**

The missing contribution is therefore **not** another executor, **not** a universal debugger, and **not** just another test harness.
It is an **Async Replay Debugger Kit**: one receiver-facing contract for async incident bundles above `tracing`, `tokio-console`, paused Tokio time, schedule-control tools, and narrow effect recorders.

# Main judgment

This lane is worthy because async failures are still among the hardest Rust failures to make portable.
A live console view, a saved random seed, a paused test clock, and a stream cassette are all useful — but they are not the same truth.

A worthy crate should help other people review five separate questions before they trust a replay claim:

1. **schedule basis** — whether the incident is being replayed from an exhaustive model, a recorded/seeded scheduler, a best-effort runtime trace, or no true schedule authority at all;
2. **time basis** — whether time is wall-clock, paused Tokio time, synthetic timeline playback, imported timestamps, or manual review only;
3. **instrumentation coverage** — which tasks, spans, wakes, resources, and spawned futures are actually covered by telemetry;
4. **effect boundary** — which external inputs (HTTP, streams, files, clocks, RNG, environment, DB calls, user events) were captured, replaced, or left live;
5. **replay fidelity** — whether the bundle supports live-only inspection, timeline reconstruction, local deterministic replay, minimized schedule repro, or only partial/manual replay.

# What it provides

- `schedule-basis.receipt.json` — runtime family, schedule authority, seed/schedule provenance, and whether replay is exhaustive, seeded, recorded, or best-effort.
- `time-basis.receipt.json` — wall clock vs paused test time vs synthetic timeline vs imported timestamps, plus advancement rules and caveats.
- `instrumentation-coverage.report.json` — runtime telemetry source, span propagation posture, task coverage, effect-hook coverage, and known blind spots.
- `effect-boundary.receipt.json` — which effect classes were captured, stubbed, recorded as cassettes, or left live.
- `replay-fidelity.report.json` — the strongest honest replay claim, strictness level, minimization status, and manual-review caveats.
- `async-incident-bundle.manifest.json` — hashes, scenario id, build/runtime facts, attached receipts, attachments, and redaction notes.
- `replay.summary.md` — one short handoff note for support, oncall, or code review.
- `replay.diff.json` — compares two bundles and classifies `schedule_basis_changed`, `time_basis_changed`, `coverage_changed`, `effect_boundary_changed`, `fidelity_changed`, and `manual_review_required`.
- `cargo async-replay receipt` — emits the receipts from a test or incident bundle.
- `cargo async-replay doctor` — warns when a claim overstates replay authority.
- `cargo async-replay bundle` — emits one small review/support archive.
- `cargo async-replay inspect` — summarizes what can and cannot be replayed before execution begins.

# What the crate should provide other people

1. **Schedule honesty** so “reproducible with seed 4129” is clearly separated from exhaustive schedule exploration and from live telemetry only.
2. **Time honesty** so paused Tokio time, imported timestamps, and real wall-clock behavior stop being blurred together.
3. **Coverage honesty** so a trace with missing spawned-task lineage is not presented as a complete causal narrative.
4. **Effect-boundary honesty** so HTTP cassettes, stream replays, RNG seeds, and live dependencies do not masquerade as one full replay surface.
5. **Fidelity honesty** so teams can tell the difference between “inspect what happened”, “replay a narrow slice”, and “deterministically reproduce the failure locally”.
6. **One boring review vocabulary** that runtime authors, app teams, oncall responders, and tool builders can share.

# Personas / who it’s for

- service teams trying to turn async incident reports into something another engineer can replay;
- runtime/tool authors who want a stable bundle vocabulary rather than an all-in-one debugger;
- oncall/support engineers who need to know whether a bundle is truly replayable or only inspectable;
- library maintainers who need to state whether their async hooks support schedule/time/effect capture;
- platform teams standardizing support bundles across async services and developer tools.

# Users & user stories

- **Oncall engineer:** “I have a stuck-task incident bundle. Before I run anything, tell me whether this is live telemetry, schedule replay, or just a timeline reconstruction.”
- **Tool author:** “I want to import Tokio console traces, Shuttle schedules, and narrow stream cassettes without claiming they are equivalent.”
- **Runtime maintainer:** “If my runtime only supports live telemetry, I still want a first-class receipt instead of pretending I support replay.”
- **App maintainer:** “If I captured HTTP and stream inputs but left DB calls live, the bundle should say that plainly.”
- **Reviewer:** “If spans were not propagated into spawned tasks, I want a coverage report that says the causal view is partial.”

# Prior art (and why it’s insufficient)

- `tokio-console` / `console-subscriber` are strong **live** diagnostics tooling, but they require runtime-emitted `tracing` data and currently only Tokio implements the required instrumentation surface.
- `tracing` gives structured events/spans and explicit future instrumentation, but it does not by itself tell another team whether spawned work, effects, or replay authority were complete.
- Tokio paused time is useful for tests, but its docs are explicit that it applies to the `current_thread` runtime and auto-advances under specific conditions; that is a narrower truth than replaying production time behavior.
- `loom` is powerful for exhaustive concurrency testing, but it is a model/exploration substrate rather than a receiver-facing async incident bundle format.
- `shuttle` offers controlled scheduling with deterministic reproduction from schedules/seeds, but that still leaves effect-boundary and coverage truth to other tools.
- `sturgeon` proves narrow stream timing replay is useful, but a stream cassette is not the same thing as whole-application async replay.

What remains missing is the **schedule basis + time basis + instrumentation coverage + effect boundary + replay fidelity** layer above today’s individual tools.

# Design goals

1. **Contract-first, not debugger-first.** Start from what another team can review.
2. **Tokio-first, but not Tokio-only in vocabulary.** Import Tokio console and paused-time facts without making Tokio the only conceptual model.
3. **Coverage honesty.** Missing span propagation or missing runtime hooks must survive export.
4. **Effect-boundary exactness.** Captured HTTP, replayed streams, seeded RNG, and live DB calls must remain distinct.
5. **Fidelity honesty.** Do not let “replay” over-claim what the bundle can actually reproduce.
6. **Import, don’t replace.** Build above `tracing`, `tokio-console`, `loom`, `shuttle`, and narrow cassette tools.
7. **Loss-aware adapters.** A timeline reconstruction, a schedule seed, and an exhaustive model are not interchangeable.
8. **Manual-review over fake certainty.** When the tool cannot prove a claim, emit `manual_review_required`.
9. **Small bundles.** `0.1` should fit code review, CI artifacts, and support handoff.

# MVP surface

- Minimal types:
  - `ScheduleBasisReceipt`
  - `TimeBasisReceipt`
  - `InstrumentationCoverageReport`
  - `EffectBoundaryReceipt`
  - `ReplayFidelityReport`
  - `AsyncIncidentBundleManifest`
  - `ReplayDiff`
- Minimal functions:
  - `capture_async_replay_receipts()`
  - `import_tokio_console_trace()`
  - `import_shuttle_schedule()`
  - `import_stream_recording()`
  - `diff_async_replay_contract()`
  - `bundle_async_incident()`
- Feature flags:
  - `serde`
  - `tracing-import`
  - `tokio-console-import`
  - `shuttle-import`
  - `stream-cassette-import`
  - `cli`

# First-class review objects

## `schedule-basis.receipt`

Captures:
- runtime family (`tokio`, `shuttle_harness`, `loom_model`, `custom_executor`, `mixed`, `manual_review_required`);
- schedule authority (`exhaustive_model`, `recorded_schedule`, `seeded_scheduler`, `live_trace_only`, `manual_review_required`);
- provenance (`saved_schedule`, `seed_only`, `trace_derived`, `manual_review_required`);
- execution topology (`single_thread`, `multi_thread`, `model_only`, `manual_review_required`);
- notes about whether the replay is intended for local debugging, CI repro, or model exploration.

## `time-basis.receipt`

Captures:
- clock class (`wall_clock_live`, `tokio_paused_time`, `synthetic_timeline`, `imported_timestamps`, `manual_review_required`);
- advancement rule (`runtime_auto_advance`, `recorded_delta_playback`, `external_clock`, `manual_step`, `manual_review_required`);
- scope (`current_thread_only`, `runtime_specific`, `effect_slice_only`, `manual_review_required`);
- caveats about drift, clock gaps, and whether the captured time is causal or merely presentational.

## `instrumentation-coverage.report`

Captures:
- telemetry source (`tokio_console`, `tracing_spans_events`, `runtime_internal_hooks`, `mixed`, `manual_review_required`);
- task coverage (`complete_for_instrumented_tasks`, `spawn_lineage_partial`, `resource_only`, `manual_review_required`);
- span propagation posture (`explicit_instrument`, `in_current_span_propagated`, `partial`, `missing`, `manual_review_required`);
- effect hook coverage (`http`, `streams`, `rng`, `db`, `files`, `custom_events`);
- known blind spots and whether the resulting view is support-safe or review-only.

## `effect-boundary.receipt`

Captures:
- effect classes and posture (`captured_cassette`, `seeded`, `stubbed`, `live`, `not_applicable`, `manual_review_required`);
- which classes are in scope: `http`, `streams`, `rng`, `clock`, `filesystem`, `database`, `env`, `user_input`, `custom`;
- cassette lineage or import path when present;
- redaction/sensitivity posture for exported artifacts.

## `replay-fidelity.report`

Captures:
- strongest honest claim (`live_inspection_only`, `timeline_reconstruction`, `narrow_effect_replay`, `local_deterministic_replay`, `minimized_schedule_repro`, `manual_review_required`);
- strictness (`exact_within_declared_bounds`, `best_effort`, `analysis_only`, `manual_review_required`);
- whether the incident was minimized or merely captured;
- whether replay requires the same runtime, same feature set, same platform, or manual adapter work.

# Suggested `0.1` doctor warnings

- `live_trace_claimed_as_deterministic_replay`
- `paused_test_time_claimed_as_wall_clock_incident_replay`
- `spawn_lineage_gap_hidden_by_summary`
- `schedule_seed_present_without_effect_boundary_receipt`
- `stream_cassette_claimed_as_whole_application_replay`
- `tokio_only_telemetry_presented_as_runtime_agnostic`
- `replay_fidelity_missing_manual_review_caveat`

# First proving-ground scenarios

1. **A Tokio console trace provides rich live telemetry, but without effect cassettes it should stay a timeline/inspection bundle rather than a full replay bundle.**
2. **A spawned future missing `in_current_span()` or equivalent lineage propagation should downgrade the causal-coverage claim.**
3. **Paused Tokio time on `current_thread` is useful, but it must not masquerade as wall-clock capture or multi-thread schedule authority.**
4. **A Shuttle seed/schedule can replay scheduling locally, but still needs an effect-boundary receipt before claiming whole-incident replay.**
5. **A `sturgeon` stream cassette is valuable and precise for one stream, but it is still a slice-level replay surface, not the whole program.**

# Lane boundaries

- Distinct from **P-0009 Deterministic Async Lab**: that lane is the harness/minimization lab; **P-0073** is the receiver-facing incident replay contract.
- Distinct from **P-0097 Determinism Lab Kit**: that lane is broader capture/minimize/replay workflow; **P-0073** owns async support-bundle exactness around schedule/time/coverage/effects/fidelity.
- Distinct from **P-0239 DetTrace Spec Kit**: that lane is the general artifact spec; **P-0073** is the app-support/review contract above imported traces.
- Distinct from **P-0057 Run Record Kit** and **P-0106 Test Run Artifact Standard Kit**: those lanes are generic run/test artifacts, not async incident replay truth.
- Distinct from **P-0532 Async Runtime Assurance Profile Kit**: runtime assurance is about runtime choice and evidence, not replay/debugging fidelity.

# What to leave for later

- a universal runtime shim for every async runtime;
- system-wide record/replay for arbitrary OS/network effects;
- a hosted incident portal;
- deep IDE integration;
- automatic importers for every cassette or tracing ecosystem crate;
- a claim of “full production replay” outside clearly declared bounds.

# Open questions

- Which minimum imported artifact should be enough to justify `timeline_reconstruction` rather than only `live_inspection_only`?
- Should `0.1` ship a dedicated `spawn_lineage` helper for common `tracing` propagation gaps?
- How much redaction policy belongs in the core bundle format versus attachment-specific adapters?
- When a bundle mixes one deterministic slice and one live effect, should the summary surface a single overall fidelity or a per-effect matrix?

# Sources

See front matter links.
