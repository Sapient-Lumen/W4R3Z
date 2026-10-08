# Gap: Rust dataflow systems still lack one portable boundary above sources/sinks, event-time semantics, state/checkpoint truth, materialization/freshness, and progress evidence

## What is missing
Rust now has credible ingredients for serious streaming SQL systems, stateful dataflow runtimes, programmable event/data pipelines, and streaming databases, but it still lacks a **boring portable contract** for the thing users actually need to review: the supported **dataflow surface**. The archive also needed an explicit lane map so it would stop flattening SQL-planned, connector-programmable, custom-progress, and streaming-database subjects into one fake “streaming support” bucket. See [`design/dataflow-surface-lane-map.md`](../design/dataflow-surface-lane-map.md).

Today teams can separately:
- declare topics, sources, tables, sinks, or connectors;
- choose streaming engines, runtime topologies, storage backends, or object stores;
- attach event-time, watermarks, windows, grace periods, and backfill policies;
- expose materialized views, query surfaces, progress dashboards, or job UIs;
- and document support claims around exactly-once, checkpointing, or recovery.

What is still missing is the shared layer that answers:
- what sources, sinks, connectors, and graph stages are actually part of the supported surface;
- what event-time, processing-time, watermark, window, lateness, and idleness semantics are promised;
- what state, checkpoint, barrier, replay, recovery, and scaling semantics are claimed versus merely inherited from one engine;
- what materializations, freshness windows, serving/query surfaces, and downstream sinks are part of the product rather than accidental byproducts;
- what runtime, storage, catalog, object-store, partitioning, or parallelism settings materially change behavior;
- and what support, release, incident, data, search, or scientific consumers may later import without reverse-engineering SQL, connector config, dashboards, catalogs, and tribal memory.

## Why it matters
Streaming and dataflow systems fail in ways that ordinary APIs or bounded datasets do not.

The hard questions are not only:
- whether a connector compiled,
- whether a query produced some rows,
- or whether a topic had messages.

The hard questions are:
- whether event-time and watermark assumptions match real source behavior,
- whether late data is dropped, repaired, or folded into a grace period,
- whether backfill and live processing are consistent with each other,
- whether state snapshots and restore semantics actually preserve correctness,
- whether materialized outputs are merely “recent” or are meant to be supportable freshness contracts,
- and whether progress, lag, or checkpoint evidence is portable enough for release/support/incident review.

Today those truths are usually scattered across SQL files, Rust operators, connector YAML, object-store settings, cluster dashboards, job catalogs, and release notes.

## Existing building blocks worth composing
- The 2025 State of Rust survey still says online documentation remains the canonical reference surface. That raises the value of machine-readable dataflow artifacts over dashboard archaeology and README prose.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Apache DataFusion now explicitly says it aims to be the query engine of choice for databases, dataframe libraries, machine learning, and **streaming applications**. That makes it a real Rust-side foundation for the category rather than a batch-only side tool.
  https://datafusion.apache.org/user-guide/introduction.html
  https://datafusion.apache.org/blog/2025/11/25/datafusion-51.0.0/
- Arroyo already makes the streaming-engine lane concrete: it is a distributed stream-processing engine written in Rust; its concept docs make event time, watermarks, stateful processing, and remote checkpointing first-class; its SQL support is built on DataFusion; and its release/docs now surface exactly-once Kafka/Kinesis lanes and source/sink contracts.
  https://doc.arroyo.dev/
  https://doc.arroyo.dev/concepts/
  https://www.arroyo.dev/
  https://doc.arroyo.dev/releases/v0.5.0/
- Fluvio and Stateful Dataflows make a different but equally real lane concrete: Fluvio documents itself as a programmable streaming platform written in Rust; SDF documents Rust+WebAssembly dataflows, event-driven composition, connectors, stateful processing, watermarks, grace periods, and idleness; SmartModules give Fluvio a reusable in-cluster transform surface; and the Hub/connector docs make connectors, SmartModules, and dataflows shareable deployment artifacts.
  https://docs.rs/fluvio/latest/fluvio/
  https://www.fluvio.io/sdf/
  https://www.fluvio.io/sdf/concepts/window-processing/
  https://www.fluvio.io/docs/smartmodules/overview/
  https://www.fluvio.io/docs/0.17.2/connectors/developers/overview/
  https://fluvio.io/docs/0.14.1/hub/use-the-hub/
- Timely Dataflow remains the strongest custom-computation lane: it explicitly frames itself as a system for implementing distributed streaming computation, documents probes as the way to understand progress in computations that may never finish, and documents capture/replay as portable streaming interop primitives.
  https://timelydataflow.github.io/timely-dataflow/
  https://timelydataflow.github.io/timely-dataflow/chapter_3/chapter_3_2.html
  https://timelydataflow.github.io/timely-dataflow/chapter_4/chapter_4_4.html
- RisingWave makes the streaming-database lane concrete: it documents streaming jobs over sources/tables/materialized views/sinks, shared-source progress and backfill behavior, consistent checkpoint snapshots via barriers, and catalogs/jobs metadata for reviewing system state and job status. Its current release notes also now expose runtime-inspection surfaces like `EXPLAIN ANALYZE` and `DESCRIBE FRAGMENTS` for streaming jobs.
  https://risingwave.com/
  https://docs.risingwave.com/reference/key-concepts
  https://docs.risingwave.com/get-started/architecture
  https://docs.risingwave.com/sql/commands/sql-create-source
  https://docs.risingwave.com/sql/system-catalogs/rw-catalog
  https://docs.risingwave.com/changelog/release-notes

## Why existing tools are not yet the whole answer
The ecosystem has **real dataflow point tools**, but not the **shared surface contract / diff / evidence layer**:
- DataFusion owns one extensible query-execution foundation lane.
- Arroyo owns one distributed streaming-SQL and stateful-checkpointing lane.
- Fluvio owns one programmable streaming platform lane, while SDF owns one Rust+WASM stateful-pipeline lane above it.
- Timely owns one custom operator/progress/replay computation lane.
- RisingWave owns one streaming-database and materialized-view lane.

Teams still have to invent their own answers for:
- stable dataflow subject identity,
- portable source/sink/connector catalogs,
- explicit event-time/watermark/window/lateness posture,
- diffable state/checkpoint/backfill/recovery assumptions,
- portable progress/freshness/materialization evidence,
- and downstream handoffs for support, release review, incident response, search/data/science attachment, or adoption guidance.

## Target outcome
A project should be able to say:
- “this is the dataflow surface this crate/binary/service/release actually supports,”
- “these are the sources, sinks, time semantics, state assumptions, and materializations that define it,”
- “these are the runtime/storage/catalog/object-store/parallelism settings that materially shape correctness,”
- “these are the progress, checkpoint, lag, backfill, and recovery artifacts that justify the claim,”
- and “this is the portable bundle downstream service/data/search/scientific/support/release tooling may consume later.”

That would be a worthy contribution because it would make Rust dataflow systems feel less like bespoke stream-processing folklore and more like reviewable interfaces.
