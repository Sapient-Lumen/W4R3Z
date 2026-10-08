# Epic proposal: Dataflow Surface Kit

## Proposal
Build a thin `cargo dataflowcheck` / `dataflow-pack/v0` layer for Rust dataflow and streaming systems.

## Why this is worthy
Rust dataflow reality is no longer just “a few crates can read streams.”
The ecosystem now has:
- a reusable query/planning substrate in DataFusion;
- a distributed streaming-SQL engine in Arroyo;
- a programmable streaming platform plus Rust+WASM stateful dataflows in Fluvio + SDF;
- a custom distributed streaming-computation lane in Timely;
- and a streaming-database/materialized-view lane in RisingWave.

But it still lacks one **honest review boundary** above those pieces.

## The contribution
The worthy move is not another engine, connector wrapper, streaming SQL fork, or dashboard.
It is a portable pack that keeps these truths separate:
- dataflow subject identity;
- source/sink/connector boundaries;
- event-time, watermark, window, lateness, and idleness semantics;
- state, checkpoint, recovery, and exactly-once scope claims;
- materialization, freshness, backfill, and progress evidence;
- imported runtime, observability, and downstream consumer attachments.

## Suggested artifact family
- `dataflow-surface/v0`
- `source-sink-catalog/v0`
- `time-window-profile/v0`
- `state-checkpoint-profile/v0`
- `materialization-progress-profile/v0`
- `dataflow-check-report/v0`
- `dataflow-diff-report/v0`
- `dataflow-pack/v0`

## Who this helps
- engine and platform authors who want reviewable support claims;
- product teams shipping real-time or continuously-updated features;
- support/release/incident reviewers who need portable evidence instead of dashboard memory;
- downstream data/search/scientific/service tooling that needs to import streaming truth honestly;
- future higher-level streaming-productization work.

## First execution path
Treat [`design/dataflow-surface-lane-map.md`](../design/dataflow-surface-lane-map.md), [`design/dataflow-surface-kit.md`](../design/dataflow-surface-kit.md), and [`design/dataflow-surface-pilot-program.md`](../design/dataflow-surface-pilot-program.md) as the immediate execution set. The lane map should stay normative so SQL-planned, connector-programmable, custom-progress, streaming-database, source, temporal, state/recovery, materialization/progress, and consumer-import truths remain distinct.

## Anti-goals
- not a winner-take-all streaming runtime;
- not a mandatory replacement for SQL or Rust-graph APIs;
- not an excuse to collapse source truth, time semantics, state truth, and materialization/progress truth into one story.
