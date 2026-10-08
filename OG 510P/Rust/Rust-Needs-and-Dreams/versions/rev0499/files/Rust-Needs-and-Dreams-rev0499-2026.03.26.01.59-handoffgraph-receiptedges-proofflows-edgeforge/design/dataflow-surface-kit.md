# Design: Dataflow Surface Kit (`cargo dataflowcheck`, `dataflow-pack/v0`)

## Goal
Define a portable contract for declaring, validating, diffing, and reviewing a Rust project’s supported **dataflow surface**: source/sink identities, graph shape, event-time and window semantics, state/checkpoint posture, materialization/freshness claims, runtime attachments, and progress evidence.

This should **not** replace DataFusion, Arroyo, Fluvio, Stateful Dataflows, Timely/Differential, RisingWave, Kafka/Flink-like platforms, dashboards, or hosted control planes.
It should make them compose better and make support claims reviewable.

Read this together with:
- [`design/dataflow-surface-lane-map.md`](./dataflow-surface-lane-map.md)
- [`design/dataflow-surface-pilot-program.md`](./dataflow-surface-pilot-program.md)
- [`proposals/epic-dataflow-surface-kit.md`](../proposals/epic-dataflow-surface-kit.md)

## References (signals)
- The 2025 State of Rust survey still says online documentation remains the canonical reference surface.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- DataFusion explicitly aims to be the query engine of choice for databases, dataframe libraries, machine learning, and streaming applications.
  https://datafusion.apache.org/user-guide/introduction.html
  https://datafusion.apache.org/blog/2025/11/25/datafusion-51.0.0/
- Arroyo documents distributed streaming dataflows, event time, watermarks, stateful processing, DataFusion-backed SQL planning, remote checkpoints, and exactly-once source/sink lanes.
  https://doc.arroyo.dev/concepts/
  https://doc.arroyo.dev/releases/v0.5.0/
- Fluvio documents a programmable streaming platform in Rust, while SDF documents stateful Rust+WASM dataflows with watermarks, grace periods, idleness, connectors, and SmartModules.
  https://docs.rs/fluvio/latest/fluvio/
  https://www.fluvio.io/sdf/
  https://www.fluvio.io/sdf/concepts/window-processing/
  https://www.fluvio.io/docs/smartmodules/overview/
  https://www.fluvio.io/docs/0.17.2/connectors/developers/overview/
  https://fluvio.io/docs/0.14.1/hub/use-the-hub/
- Timely Dataflow explicitly treats distributed streaming computation, probes/progress, and capture/replay as first-class.
  https://timelydataflow.github.io/timely-dataflow/
  https://timelydataflow.github.io/timely-dataflow/chapter_3/chapter_3_2.html
  https://timelydataflow.github.io/timely-dataflow/chapter_4/chapter_4_4.html
- RisingWave documents streaming jobs, shared-source consumption progress, backfilling, barrier-based checkpointing, catalogs/job status, and runtime-inspection surfaces for streaming plans.
  https://docs.risingwave.com/reference/key-concepts
  https://docs.risingwave.com/get-started/architecture
  https://docs.risingwave.com/sql/commands/sql-create-source
  https://docs.risingwave.com/sql/system-catalogs/rw-catalog
  https://docs.risingwave.com/changelog/release-notes

## The missing seam
Rust now has several serious but non-equivalent **dataflow lanes**, but they are still too loosely connected in the archive. The repo already knew it needed one portable review boundary above sources, time semantics, state, and progress, but it still needed a clearer map of the **different lanes** Rust is actually using:
- SQL-planned / relational-stream systems,
- connector-programmable / inline-transform systems,
- custom graph / progress-replay systems,
- streaming-database / materialized-serving systems,
- plus cross-cutting source, temporal, state/recovery, materialization/progress, and consumer-import truths.

That lane-correction note in [`design/dataflow-surface-lane-map.md`](./dataflow-surface-lane-map.md) should be treated as normative guidance for how this kit names engine family, source posture, temporal semantics, recovery guarantees, progress evidence, and downstream consumer power.

What is still missing is one boring substrate that says:
1. which dataflow lane is this subject actually in?
2. which source/sink, time, state, and progress truths define it?
3. which runtime or cluster attachments materially change its meaning?
4. what remains partial, inferred, or engine-private?
5. which downstream consumers may import which conclusions?

Without that, every dataflow system keeps re-inventing its own support story in SQL, connector YAML, dashboards, and release notes.

## Core components

### 1) `dataflow-surface/v0`
A design-time declaration of the supported continuous-computation boundary for a crate/binary/workspace.

Required ideas:
- stable dataflow subject identity
- boundary kind:
  - distributed stream-processing job
  - streaming SQL / materialized-view pipeline
  - programmable event/dataflow pipeline
  - custom Rust dataflow graph
  - streaming database job family
- intended consumers:
  - internal operations
  - product/runtime serving
  - analytics / metrics / alerting
  - downstream search / features / ML
  - data synchronization / CDC
- support class:
  - official
  - checked subset
  - experimental
  - internal
  - deprecated
- graph summary:
  - sources
  - transforms/operators
  - stateful stages
  - materializations/sinks
- top-level guarantee notes:
  - best-effort
  - at-least-once
  - effectively-once
  - exactly-once (scoped and justified)
  - no durability claim

This is the thing humans review before trusting automation.

### 2) `source-sink-catalog/v0`
A machine-readable description of ingress/egress and graph-boundary assumptions.

Required ideas:
- source identities and families:
  - topic/stream/queue
  - CDC source
  - table/object-store/file source
  - HTTP/webhook/socket source
  - generated/test source
- sink/materialization identities:
  - topic/stream sink
  - table/object-store/file sink
  - materialized view / query surface
  - index/search attachment
  - service/webhook/export sink
- connector/runtime/plugin references
- startup and offset posture
- retention and replay assumptions
- source-sharing or independent-consumption posture
- partitioning/keying notes where they affect semantics
- unsupported or illustrative-only lanes

Design rule: preserve raw source/sink truth instead of flattening every engine into one fake “input/output” model.

### 3) `time-window-profile/v0`
A declaration of the temporal semantics that matter for correctness.

Required ideas:
- time basis:
  - event time
  - processing time
  - ingestion time
  - mixed / imported timestamp posture
- timestamp assignment/extraction rules
- watermark strategy
- allowed lateness / grace period
- idleness handling
- window families:
  - tumbling
  - sliding/hopping
  - session
  - custom
  - no windows
- temporal join/aggregation notes where relevant
- late-data posture:
  - drop
  - include within grace
  - side output / DLQ
  - engine-specific unknown

This is how the kit stays honest when “real-time” or “windowed” means materially different things across engines.

### 4) `state-checkpoint-profile/v0`
A machine-readable description of state and durability posture.

Required ideas:
- stateful operator/stage identities
- state location:
  - in-memory only
  - local disk
  - remote object store
  - engine-managed storage
  - external/state-store attachment
- checkpoint/barrier/snapshot posture
- recovery/restore semantics
- scale-out / repartition / code-update posture
- idempotency or deduplication notes where relevant
- exactly-once / at-least-once scope boundaries
- retained raw evidence references (checkpoint metadata, logs, manifests, state summaries)

Design rule: preserve state truth and checkpoint truth separately from source/sink truth and separately from high-level support claims.

### 5) `materialization-progress-profile/v0`
A declaration of what the dataflow actually exposes and how progress is interpreted.

Required ideas:
- materialized-view / table / index / cache / sink outputs
- freshness posture:
  - synchronous / up-to-watermark
  - bounded staleness
  - best effort
  - manual/query-time only
- progress evidence families:
  - watermarks
  - probes/frontiers
  - lag metrics
  - backfill status
  - job/fragment/catalog status
  - explain/analyze attachments
- serving/query attachment notes
- downstream consumer references
- unsupported or local-only observability lanes

This is where “the dataflow runs” stops being enough and “the dataflow’s visible outputs are reviewable” begins.

### 6) `dataflow-check-plan/v0`
A concrete declaration of what is checked.

Required ideas:
- extraction sources: SQL, engine metadata, runtime catalogs, connector configs, graph introspection, explain plans, dashboards/log exports
- selected profiles and environments
- checks performed:
  - source/sink extraction
  - time/window extraction
  - state/checkpoint extraction
  - materialization/progress extraction
  - compatibility or support checks
  - replay/backfill checks
  - diff checks against prior packs
- intentionally omitted lanes and why

This is where the kit stops pretending “the query compiled” means “the dataflow surface is reviewed.”

### 7) `dataflow-check-report/v0`
Evidence from extraction, compatibility checks, and runtime review.

Possible contents:
- extracted graph/source/sink summary
- temporal-semantics findings
- state/checkpoint/recovery findings
- materialization/freshness/progress findings
- unsupported or partially-supported lane findings
- drift from prior review point
- linked raw artifacts: SQL, graph plans, job catalogs, checkpoint metadata, watermark/probe snapshots, lag metrics, explain/analyze outputs, connector manifests

### 8) `dataflow-diff-report/v0` (optional)
For compatibility-sensitive change review:
- source/sink/connectors widened/narrowed
- timestamp assignment or watermark policy changed
- window/lateness/idleness semantics changed
- checkpoint/storage/recovery posture changed
- materialization/freshness/serving posture changed
- runtime/backend/object-store/parallelism posture changed
- support class widened/narrowed

Should distinguish:
- additive changes
- compatibility-sensitive changes
- runtime-only drift
- evidence-only refreshes
- documentation-only updates

### 9) `dataflow-pack/v0`
Bundle format containing:
- `dataflow-surface/v0`
- `source-sink-catalog/v0`
- `time-window-profile/v0`
- `state-checkpoint-profile/v0`
- `materialization-progress-profile/v0`
- one or more `dataflow-check-report/v0`
- optional `dataflow-diff-report/v0`
- optional raw attachments: SQL, graph exports, connector manifests, checkpoint metadata, catalog dumps, progress snapshots, and explain/analyze outputs

This is the unit that should travel through CI, release review, incident archaeology, and later domain-specific consumers.

### 10) `cargo dataflowcheck`
Reference UX:
- `cargo dataflowcheck init`
- `cargo dataflowcheck inspect`
- `cargo dataflowcheck runtime`
- `cargo dataflowcheck progress`
- `cargo dataflowcheck diff`
- `cargo dataflowcheck pack`

`cargo dataflowcheck` should begin as an adapter / explainer / packer.
It should not pretend to be the one true streaming engine, connector marketplace, or dashboard.

## Default policy
- **Separate source/sink truth, temporal semantics, state/checkpoint posture, and materialization/progress evidence.**
- **Preserve raw engine truth** from SQL, graph plans, connector manifests, runtime catalogs, checkpoint metadata, and progress outputs instead of flattening everything into one fake streaming model.
- **Treat durability and exactly-once claims as scoped capability statements, not a single boolean badge.**
- **Keep bounded dataflow outputs distinct from bounded dataset publication.**
- **Prefer bounded evidence** (catalog snapshots, explain plans, progress snapshots, checkpoint metadata, small fixtures) over giant runtime dumps.
- **Make runtime/storage/catalog/object-store assumptions explicit** whenever they materially affect correctness.

## What the kit should provide to others
- **Event Surface Kit:** attach channel/event/replay truth to continuous dataflow subjects without absorbing event identity into operator graphs.
- **Dataset Surface Kit:** attach bounded dataset/materialization outputs without pretending continuous dataflow semantics and bounded dataset publication are the same thing.
- **Data Productization / Search / Scientific work:** import source/time/state/materialization truths instead of re-deriving them from engine-specific docs.
- **Runtime Settings + Observability:** remain the activation/evidence attachment lanes rather than becoming new dataflow authorities.
- **Support Envelope / Release / Incident work:** attach support and archaeology truth to a stable reviewed dataflow subject.

## Overlap boundaries
- **Not another streaming engine:** DataFusion, Arroyo, Fluvio, Timely, and RisingWave remain execution/runtime lanes.
- **Not Event Surface Kit:** Event Surface owns channel/message/envelope/delivery truth; Dataflow Surface owns continuous graph/time/state/materialization/progress truth.
- **Not Dataset Surface Kit:** Dataset Surface owns bounded dataset/layout/storage publication truth; Dataflow Surface owns live unbounded or continuously-updated computation truth.
- **Not Workflow Productization Stack:** workflow work owns job/workflow/schedule and durable business-process truth; dataflow work owns continuous data-transformation and materialization truth.
- **Not another dashboard or control plane:** dashboards remain consumers or evidence producers, not the canonical surface owner.
