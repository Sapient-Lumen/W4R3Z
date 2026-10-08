# Design: Dataflow Surface lane map (SQL-planned, connector-programmable, custom-progress, streaming-database, source, temporal, state/recovery, materialization/progress, and consumer-import lanes)

## Goal
Sharpen **Dataflow Surface Kit** so the archive stops treating “streaming support” or “real-time support” as one bucket.

Rust’s present-tense dataflow world already spans materially different lanes:
- SQL-planned streaming pipelines,
- connector-led programmable pipelines with in-line transforms,
- custom operator/progress/replay graphs,
- streaming-database jobs with materialized-view and serving posture,
- plus cross-cutting source, time, state, progress, and consumer-import claims.

The archive should therefore keep dataflow review grounded in an explicit lane map instead of one flattened “supports streaming” story.

## Signals from the current ecosystem
- DataFusion says it aims to be the query engine of choice for databases, dataframe libraries, machine learning, and **streaming applications**, and its feature list includes a vectorized multithreaded streaming execution engine plus Substrait support. That is direct evidence that Rust’s dataflow substrate is no longer batch-only.  https://datafusion.apache.org/user-guide/introduction.html
- Arroyo’s concept docs describe a distributed dataflow DAG, DataFusion-backed streaming SQL, event-time semantics, watermarks, and checkpointed state that can recover identically after failures. That makes SQL-planned/event-time dataflow a real first-class lane today.  https://doc.arroyo.dev/concepts/
- Fluvio SDF documents Rust+WebAssembly event-driven dataflows above Fluvio’s connectors and persistence, while its window-processing docs make watermark grace periods, idleness, assign-timestamp hooks, and keyed state explicit. Fluvio SmartModules and the Connector Development Kit then keep transform deployment and connector publication explicit rather than implicit.  https://www.fluvio.io/sdf/  https://www.fluvio.io/sdf/concepts/window-processing/  https://www.fluvio.io/docs/smartmodules/overview/  https://www.fluvio.io/docs/0.17.2/connectors/developers/overview/
- Timely Dataflow explicitly presents itself as a system for distributed streaming computation, documents probes as progress monitors over potentially never-ending computations, and documents capture/replay as portable streaming interop primitives. That proves custom graph/progress/replay is its own lane, not a hidden implementation detail of SQL engines.  https://timelydataflow.github.io/timely-dataflow/  https://timelydataflow.github.io/timely-dataflow/chapter_3/chapter_3_2.html  https://timelydataflow.github.io/timely-dataflow/chapter_2/chapter_2_1.html
- RisingWave documents a PostgreSQL-compatible streaming database with streaming jobs over sources/tables/materialized views/sinks, distinct serving/streaming/meta/compactor nodes, and recent release notes that expose watermark propagation, backfill controls, shared-source posture, and fragment-progress catalogs. That makes streaming-database materialization/progress a distinct dataflow lane rather than just “SQL plus Kafka.”  https://docs.risingwave.com/reference/key-concepts  https://docs.risingwave.com/get-started/architecture  https://docs.risingwave.com/changelog/release-notes
- The 2025 State of Rust survey says online docs remain the preferred canonical reference surface. For dataflow systems, that raises the value of attachable machine-readable packs because the truths that matter are otherwise scattered across SQL, connector config, runtime catalogs, checkpoint metadata, and dashboards.  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## The lanes

### 1) SQL-planned / relational-stream lane
This is the lane where the user-facing story starts from SQL or relational plans that are compiled into a streaming dataflow.

What defines it:
- SQL or relational-planning surface is first-class
- source definitions, event-time columns, joins, windows, and sinks are part of the authored subject
- planner and graph/runtime are related but not identical
- explain-plan or logical-plan attachments often matter

Why it deserves a separate lane:
- SQL-planned streaming is not the same thing as connector-first or custom-operator dataflow
- DataFusion + Arroyo prove that Rust now has a serious planned-dataflow lane
- hiding the planner/runtime split makes support claims much harder to review

Design rule:
- preserve SQL/planner truth separately from runtime/state/progress truth

### 2) Connector-programmable / inline-transform lane
This is the lane where the primary surface is composed from connectors, in-line transformations, SmartModules, or Rust/WASM stages rather than from a relational plan alone.

What defines it:
- connectors are explicit product surface
- transforms may run in-line on producers, consumers, or connector paths
- deployment/shareability of transforms and connectors matters
- topic routing and connector lifecycle are part of the real contract

Why it deserves a separate lane:
- Fluvio + SDF + SmartModules prove that programmable connector pipelines are a real Rust lane right now
- “has connectors” and “has programmable in-line transform stages” are not the same claim
- the composition/deployment surface can drift independently of time and checkpoint semantics

Design rule:
- preserve connector identity, transform identity, and share/deploy posture separately from engine runtime claims

### 3) Custom graph / progress-replay lane
This is the lane where the primary surface is an explicit dataflow graph with custom operators, scopes, progress tracking, and optional capture/replay.

What defines it:
- graph/operator identity is first-class
- timestamps/frontiers/probes or equivalent progress artifacts are part of correctness
- replay/capture or bespoke operator semantics matter
- there may be no SQL or connector catalog at all

Why it deserves a separate lane:
- Timely proves that progress and replay are first-class truths, not just observability add-ons
- this lane would be erased if the archive treated all dataflow as SQL metadata
- some advanced Rust systems care most about graph/progress semantics and only secondarily about sources and sinks

Design rule:
- preserve graph/progress/replay truth separately from relational and connector surfaces

### 4) Streaming-database / materialized-serving lane
This is the lane where the system exposes continuously updated tables, materialized views, sinks, and query surfaces as part of the supported product boundary.

What defines it:
- materialized views/tables/serving/query surfaces are explicit
- job catalogs, fragments, or cluster/runtime topology often matter
- backfill and live-stream interaction is part of the correctness story
- users review freshness and serving posture, not only ingestion posture

Why it deserves a separate lane:
- streaming databases are not just brokers plus SQL
- RisingWave makes materialization, serving, and cluster/job state explicit
- downstream consumers usually care about outputs and freshness, not only sources and operators

Design rule:
- preserve serving/materialization truth separately from ingestion and runtime-only claims

### 5) Source-boundary / connector-consumption lane
This is the lane where the question is: what ingress and egress boundaries are actually part of the supported surface?

What defines it:
- source and sink identities
- startup/offset/replay posture
- shared-source versus independent-consumption posture
- partitioning/keying notes where they affect semantics
- connector/runtime/plugin references

Why it deserves a separate lane:
- source truth is not an implementation footnote to plans or views
- replay/startup/shared-consumption behavior can change user-visible semantics before time/window or state logic even begins
- source/sink boundary claims often drift independently from graph logic

Design rule:
- preserve source/sink boundary truth separately from planner, temporal, and checkpoint truth

### 6) Temporal-semantics lane
This is the lane where the question is: which notion of time, watermarking, windowing, lateness, and idleness actually governs correctness?

What defines it:
- event/processing/ingestion/mixed time basis
- timestamp assignment/extraction rules
- watermark strategy
- grace-period or lateness posture
- idleness handling
- window and temporal-join semantics

Why it deserves a separate lane:
- “streaming” does not imply event-time correctness or any particular late-data policy
- Arroyo and SDF both make event-time and watermark details public; RisingWave’s release notes keep watermark/backfill behavior moving independently
- the hardest user-facing bugs often come from hidden temporal assumptions rather than from connectivity failures

Design rule:
- preserve temporal semantics separately from source identity and separately from state/recovery claims

### 7) State / checkpoint / recovery lane
This is the lane where the question is: what durable state, checkpointing, backfill, replay, recovery, and scaling behavior is actually claimed?

What defines it:
- stateful stage identity
- state location and storage backend posture
- checkpoint/barrier/snapshot policy
- backfill/replay/recovery semantics
- scale-out or repartition implications
- exactly-once or deduplication scope boundaries

Why it deserves a separate lane:
- “exactly once” often hides state-store, checkpoint, and replay assumptions
- Arroyo and RisingWave both surface checkpoint/backfill machinery; Timely exposes replay more directly; SDF exposes stateful windowing separately from connector setup
- this lane often matters more to operators than the authored graph itself

Design rule:
- preserve state/checkpoint/backfill/recovery truth separately from temporal semantics and separately from materialization claims

### 8) Materialization / progress / freshness lane
This is the lane where the question is: what output surfaces are exposed, and what progress/freshness evidence justifies them?

What defines it:
- materialized views, tables, indices, caches, topics, or exports
- freshness posture (`up-to-watermark`, bounded staleness, best effort, manual/query-time only)
- progress evidence such as probes/frontiers, lag metrics, backfill status, job/fragment status, or explain/analyze attachments
- serving/query attachment notes

Why it deserves a separate lane:
- a running job is not the same thing as a reviewable output contract
- streaming systems often surface progress through very engine-specific mechanisms that still need portable interpretation
- this is the lane most likely to get collapsed into vague “real-time” marketing

Design rule:
- preserve output/freshness/progress evidence separately from ingestion, planner, and state truth

### 9) Consumer-import / bounded-view lane
This is the lane where dataflow truth is compressed for support, release review, incidents, adoption guidance, or downstream data/search/science/service consumers.

What defines it:
- consumer class and permitted conclusions
- freshness/expiry or import validity rules
- links back to source/time/state/progress evidence
- forbidden automatic inferences

Why it deserves a separate lane:
- consumer summaries are where the ecosystem is most tempted to create one fake “real-time readiness” verdict
- different consumers need different compressions of the same pack
- downstream imports should remain explicitly bounded instead of silently becoming new canon

Design rule:
- keep consumer views thin, explainable, and downstream of the canonical dataflow lanes

## Cross-lane adapter risks
The archive should make at least these risks explicit:
1. **SQL-planned ↔ connector-programmable**   - relational plans do not fully describe connector lifecycle, transform publication, or in-line WASM logic.
2. **SQL-planned ↔ custom graph/progress**   - graph/progress/replay truth should not vanish just because one engine can expose SQL.
3. **source boundary ↔ temporal semantics**   - startup/replay/shared-consumption posture is not the same thing as watermark/window/lateness policy.
4. **temporal semantics ↔ state/recovery**   - event-time correctness does not imply checkpoint/backfill/recovery integrity.
5. **state/recovery ↔ materialization/progress**   - exactly-once or checkpoint claims do not automatically justify freshness or serving claims.
6. **engine/runtime topology ↔ consumer summary**   - dashboard/job/catalog language should not silently become the public support contract.
7. **any canonical lane ↔ downstream import**   - search/support/incident/assistant summaries must stay attached to the pack they summarize.

## What should change elsewhere in the archive
- **Dataflow Surface Kit** should cite this lane map as the rule for what must stay separate.
- **Event Surface**, **Dataset Surface**, **Runtime Settings**, and **Observability** should remain adjacent inputs/consumers instead of swallowing continuous graph/time/state/progress truth.
- **Data Productization**, **Search Productization**, **Scientific Productization**, and **Workflow Productization** should import bounded dataflow packs rather than re-owning streaming semantics.
- **Incident**, **Release Truth**, **Support Envelope**, and future atlas/adoption layers should consume bounded summaries instead of reverse-engineering dashboards and SQL files.

## Worthy contribution, sharpened
The worthy contribution here is **not** another engine, connector marketplace, SQL dialect, control plane, or “real-time maturity” score.
It is a thin `cargo dataflowcheck` / `dataflow-pack/v0` layer whose lane catalogs, source/time/state/materialization profiles, progress evidence attachments, diffs, and bounded consumer summaries let Rust teams compare dataflow claims honestly across SQL-planned, connector-programmable, custom-progress, and streaming-database lanes without semantic collapse.
