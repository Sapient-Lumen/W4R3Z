# Design: Dataflow Surface pilot program

## Goal
Turn the new **Dataflow Surface Kit** into a ranked execution plan instead of a vague “Rust streaming/dataflow needs better tooling” sentiment.

Read this together with [`design/dataflow-surface-lane-map.md`](./dataflow-surface-lane-map.md). The pilot should prove that the archive can preserve engine-family lanes and cross-cutting source/time/state/progress lanes at the same time.

This pilot program should prove that Rust can export and review **dataflow surface truth** without pretending one engine, one connector model, one watermark policy, one checkpointing scheme, or one materialization strategy owns the whole problem.

## Why this pilot order
The point is to begin where the ecosystem is already undeniably real:
- Arroyo already makes distributed streaming SQL, event time, watermarks, state, and checkpoints concrete;
- Fluvio + SDF already make connectors, SmartModules/WASM, and stateful streaming composition concrete;
- Timely already makes graph/progress/replay truth concrete;
- RisingWave already makes streaming-database materialization, backfill, checkpointing, and job catalogs concrete;
- DataFusion already gives Rust a reusable query/planning foundation for data-centric and streaming systems.

So the pilots should begin with **single-lane honesty**, then add cross-cutting source/time/state/progress evidence, and only then broaden to downstream imports.

## Ranked first pilots

### 1) SQL-planned / relational-stream lane
**Why first**
- It is the cheapest lane that still proves the kit is real.
- It forces the archive to say what the supported source/sink/time/state boundary actually is.
- It avoids starting from fake universality.

**Good opening candidate**
- one concrete Arroyo pipeline.

**What must be explicit**
- sources and sinks in scope
- event-time assignment and watermark policy
- window/lateness posture
- state/checkpoint semantics
- selected runtime/backend assumptions

**Success bar**
A project can publish a reviewable dataflow boundary for one concrete streaming-SQL lane without hiding behind engine-specific UI or SQL files alone.

### 2) Connector-programmable / inline-transform lane
**Why second**
- This is where transform/runtime/deployment diversity becomes visible quickly.
- Connectors and SmartModules prove that source/sink truth and transform truth should not stay trapped inside one platform runtime.

**Good opening candidate**
- one Fluvio + SDF dataflow with at least one connector and one SmartModule or Rust+WASM logic stage.

**What must be explicit**
- connector identities and deployment posture
- SmartModule/WASM or custom-logic attachments
- watermark/grace/idleness semantics
- topic/materialization boundaries
- Hub/shareability or extension posture where relevant

**Success bar**
A project can export source/transform/materialization truth without pretending the platform runtime is the whole product contract.

### 3) Custom graph / progress-replay lane
**Why third**
- Timely-style systems make progress and replay semantics impossible to ignore.
- This is where the kit proves it is not secretly only “streaming SQL metadata.”

**Good opening candidate**
- one Timely dataflow example or internal graph subject.

**What must be explicit**
- graph/operator identity
- scope/key/progress assumptions
- probe/frontier evidence
- capture/replay attachments
- intentionally missing higher-level guarantees called out honestly

**Success bar**
A project can export graph/progress/replay truth that advanced Rust systems programmers can review without flattening it into SQL-only language.

### 4) Streaming-database / materialized-serving lane
**Why fourth**
- Streaming databases surface the hardest product questions: shared-source progress, backfill, materialized views, query freshness, checkpoints, and job status.
- This is where the kit proves it can talk about serving/materialization rather than only ingestion and operators.

**Good opening candidate**
- one RisingWave subject with sources, materialized views, and at least one sink or query consumer.

**What must be explicit**
- shared-source or independent-consumption posture
- backfill semantics and monitoring surface
- checkpoint/recovery semantics
- materialized-view / sink freshness claims
- catalog/job/fragment evidence attachments

**Success bar**
A project can attach materialization and progress truth without pretending a streaming database is just a broker plus SQL.

### 5) Consumer-import / bounded-view lane
**Why fifth**
- This is where the kit becomes ecosystem infrastructure instead of a local crate tool.
- Dataflow systems become more useful when data/search/scientific/service/support consumers can import them rather than recreate them.

**What must be explicit**
- which consumers import which dataflow truths
- which facts are gating versus advisory
- freshness/expiry posture for imported evidence
- support/release/incident attachment rules
- public vs internal consumer boundaries

**Success bar**
A downstream consumer can import dataflow evidence without flattening it into one fake green check or another engine-specific dashboard.

## Pilots to defer
These matter later, but are weaker opening bets:
- **one universal stream-processing abstraction** — too likely to erase real runtime differences;
- **one mega-schema for every dashboard metric and every engine detail** — too broad before narrow reviewable subsets stabilize;
- **policy-first maturity scoring** — too brittle before exported truth is stable;
- **hosted control planes or ops consoles** — too likely to hide the portable boundary.

## Immediate archive consequences
Read this file together with:
- `design/dataflow-surface-kit.md`
- `gaps/streaming-dataflows-sources-time-state-materialization-and-progress-contracts.md`
- `proposals/epic-dataflow-surface-kit.md`
- `design/event-surface-kit.md`
- `design/dataset-surface-kit.md`
- `design/runtime-settings-kit.md`
- `design/observability-kit.md`
- `design/data-productization-stack.md`
- `design/search-productization-stack.md`
- `design/scientific-productization-stack.md`

The archive should now prefer:
- **single-lane honesty before universality**,
- **time semantics before benchmark theater**,
- **state/checkpoint truth before exactly-once marketing**,
- **materialization/progress evidence instead of dashboard folklore**,
- and **consumer imports** over prose-only streaming-readiness claims.

## What should wait
Do **not** start with:
- a new stream-processing engine,
- a new streaming SQL dialect,
- a universal connector marketplace,
- or a fake aggregate “real-time maturity” score.

Those may become overlays or consumers later.
They are not the missing substrate.
