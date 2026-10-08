# Product plan — Async Runtime Assurance Profile Kit (2026-03-21)

## Why this lane is worth opening now

The new evidence is unusually direct.
The March 2026 Rust challenges post says async remains painful and that runtime lock-in is still a real ecosystem problem.
The January 2026 safety-critical post says teams immediately ask for runtime quality/process artifacts and explicitly recommends defining requirements for a safety-case-friendly async runtime.

At the same time, today's runtime substrate is rich enough to compare concretely:

- Tokio exposes a joined runtime with I/O driver, scheduler, timer, blocking pool, runtime/task metrics, and sharply documented shutdown behavior.
- Embassy exposes no-`alloc`, static tasks, compile-time RAM fit, integrated timers, fairness, and optional multi-priority executors.
- RTIC exposes interrupt-priority scheduling, timer queues, compile-time deadlock-freedom claims, shared-stack memory posture, and WCET/scheduling-analysis-friendly structure.

That means the missing crate is not another runtime implementation.
It is a **runtime-choice and runtime-support contract**.

## Main `0.1` product

The first lovable product should be a small cargo subcommand + library pair that lets a team emit one reviewable runtime-support pack.

### Command surface

- `cargo runtime-assurance init`
- `cargo runtime-assurance capture`
- `cargo runtime-assurance check`
- `cargo runtime-assurance doctor`
- `cargo runtime-assurance summary`
- `cargo runtime-assurance diff <old> <new>`
- `cargo runtime-assurance pack`

### Core artifacts

- `async-runtime-profile.toml`
- `runtime-profile.receipt.json`
- `shutdown-behavior.report.json`
- `qualification-basis.receipt.json`
- `runtime-choice.summary.md`
- `runtime-profile-diff.report.json`

## What `0.1` should actually classify

### `runtime-profile.receipt.json`

This is the compact answer to: “what class of runtime are we depending on?”

It should classify at least:

- runtime family,
- scheduler model,
- allocation posture,
- preemption posture,
- timer authority,
- blocking posture,
- host/target notes,
- and manual-review zones.

### `shutdown-behavior.report.json`

This is the compact answer to: “what does stopping this runtime really mean?”

It should classify at least:

- async-task cancellation posture,
- blocking-work shutdown posture,
- timeout aftermath,
- panic visibility,
- post-shutdown resource posture,
- and any imported framework/runtime caveats.

### `qualification-basis.receipt.json`

This is the compact answer to: “why should anyone trust the above claim?”

It should classify at least:

- docs-only basis,
- docs + instrumentation basis,
- docs + on-target measurement basis,
- imported assurance-artifact basis,
- target scope,
- open assumptions,
- and explicit manual-review posture.

## Discovery order

Prefer conservative imports in this order:

1. **declared profile**
   - `async-runtime-profile.toml`
2. **manifest/runtime signals**
   - dependency presence (`tokio`, `embassy-executor`, `rtic`, adapters)
   - obvious feature flags / runtime-family markers
3. **framework/runtime docs import**
   - imported runtime-family defaults and caveats
4. **local observations**
   - runtime metrics instrumentation present or absent
   - target-specific notes or board/RTOS notes
5. **manual annotations**
   - safety/assurance notes, imported evidence refs, manual-review overrides

Anything uncertain should remain `manual_review_required`.

## Recommended proving grounds

### Tokio profile

The first hosted/runtime proving ground should be Tokio because the docs already make several support-sensitive facts explicit:

- runtime includes I/O, scheduler, timer, and blocking pool;
- tasks spawned with `spawn` are not guaranteed to run to completion during shutdown;
- `spawn_blocking` work can continue running and may outlive timeout-based shutdown;
- bound resources fail after runtime drop;
- metrics are instrumentable through `Runtime::metrics` and `tokio-metrics`.

### Embassy profile

The first embedded-async proving ground should be Embassy because the docs already make several qualification-shaped facts explicit:

- no `alloc` / no heap needed;
- tasks are statically allocated;
- RAM-fit failure is compile-time/link-time visible;
- fair polling is claimed;
- integrated timer queue exists;
- multiple executor instances can represent priority levels.

### RTIC profile

The first real-time proof point should be RTIC because it prevents the crate from pretending all runtime choices are executor/threadpool variants.

The docs/readme already expose:

- tasks as the concurrency unit,
- timer queues,
- interrupt-priority scheduling,
- compile-time deadlock-freedom claims,
- no hard dependency on a dynamic allocator,
- and WCET/scheduling-analysis-friendly structure.

## Boundaries to keep sharp

- This lane is **not** the same as lifecycle/shutdown support generally.
- This lane is **not** channel semantics.
- This lane is **not** resource boundedness.
- This lane is **not** target-support/toolchain support.
- This lane is **not** a full assurance-case workbench.

The product is the **joined runtime-choice artifact** above those imports.

## Recommended workspace split

- `runtime_assurance_model`
- `runtime_assurance_discovery`
- `runtime_assurance_check`
- `runtime_assurance_pack`
- `cargo-runtime-assurance`

Adapters later:

- `runtime_assurance_tokio`
- `runtime_assurance_embassy`
- `runtime_assurance_rtic`

## `0.1` adoption story

A good first-user story should look like this:

1. maintainer writes `async-runtime-profile.toml`,
2. tool imports obvious runtime family facts,
3. maintainer marks any remaining manual-review zones,
4. `capture` emits a compact pack,
5. `doctor` warns when claims are stronger than evidence,
6. `summary` renders a short runtime-support note for docs/review,
7. `diff` makes runtime-support drift visible across releases.

That is small enough to ship, but still answers a real cross-domain pain point.


## 2026-03-22 addendum — artifact completeness and bundle shape

The next serious `0.1` implementation step should promote three more artifacts:

- `qualification-basis.receipt.json`
- `runtime-profile-diff.report.json`
- `runtime-assurance-bundle.manifest.json`

These matter because the receiver-facing question is no longer just “which runtime family are we on?”
It is also:

- why should anyone believe that claim,
- did the runtime/support meaning change across revisions,
- and what exact multi-lane bundle should a reviewer open first when host-side Tokio and target-side Embassy/RTIC both exist?

A good `0.1` pack should therefore let a reviewer distinguish:

1. same runtime, stronger evidence;
2. same runtime, changed shutdown/support meaning;
3. genuinely different runtime/concurrency model;
4. mixed host/target stack that must remain multi-lane.
