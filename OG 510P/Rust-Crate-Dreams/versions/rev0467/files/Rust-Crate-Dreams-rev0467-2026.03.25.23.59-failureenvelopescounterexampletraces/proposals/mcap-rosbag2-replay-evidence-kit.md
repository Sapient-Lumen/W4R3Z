---
id: P-0350
title: MCAP + rosbag2 Replay & Evidence Kit — schema/channel lockfiles, conversion audits, and reproducible robot-data bug bundles
status: idea
domains: [robotics, data-logging, autonomy, realtime-systems, packaging, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://mcap.dev/spec
  - https://docs.ros.org/en/iron/p/rosbag2_storage_mcap/
  - https://docs.rs/mcap
  - https://docs.rs/rosbags-rs
  - https://docs.rs/crate/rustbag/latest
  - https://docs.foxglove.dev/docs/sdk
---

# Problem

MCAP is now a serious interoperability surface for robotics and pub/sub logging, and Rust already has multiple ways to read or write it. But the expensive failures still happen **above raw file parsing**:

- a bag opens, but schema/channel metadata drift makes replay or downstream decoding unreliable,
- rosbag2 conversion technically succeeds while timestamps, channel metadata, or message schemas drift in ways that only show up later,
- teams can exchange a bag file but not a compact explanation of which topics, clocks, or schemas are incompatible,
- and day-two operations still rely on giant binary attachments instead of minimized, replayable evidence bundles.

The worthy missing crate is a **replay-and-evidence workbench** for MCAP and rosbag2 semantics, not another logger.

# What it provides

- `mcap-ir` — canonical Rust IR for MCAP headers, channels, schemas, chunk summaries, clock domains, and rosbag-style topic metadata.
- `bag-profile` — lockfiles pinning expected topics, encodings, QoS-ish metadata, clock assumptions, schema hashes, and conversion constraints.
- `bag-replay` — deterministic transcript replay for small excerpts and event timelines.
- `bag-diff` — semantic diffs such as “same topic name, changed schema hash”, “timestamps monotonic in source but not after conversion”, or “expected channel missing from excerpt”.
- `rosbag-convert-check` — verify rosbag2 ↔ MCAP conversion assumptions and produce actionable findings.
- `cargo mcap-evidence` — emit `*.mcapbundle.zip` for CI, vendor handoff, simulator-to-robot debugging, or dataset release QA.

# What the crate should provide other people

1. **A boring default bug-report artifact for robot logs**.
2. **One place to pin schema/topic/clock expectations** across teams and tools.
3. **Confidence checks around rosbag2 conversion and excerpting**.
4. **Small-share bundles** that preserve enough semantics to reproduce failures.
5. **A bridge between recording libraries and downstream analysis or visualization tools**.

# Persona / who it’s for

- Robotics platform engineers
- Simulation/replay infrastructure owners
- Dataset curators
- Tool authors integrating Foxglove or rosbag2 workflows
- Rust developers building robot-data utilities

# Users & user stories

- **Platform engineer**: “Show me whether this replay failure is due to missing schemas, channel drift, or clock issues.”
- **Dataset curator**: “Verify that the excerpt we published still preserves the message types and timing assumptions needed for downstream users.”
- **Vendor integrator**: “Ship a compact bundle that proves our MCAP logs are valid but the rosbag2 conversion changed semantics.”
- **CI owner**: “Gate merges if a bag corpus changed topic/schema/clock expectations in a breaking way.”

# Prior art (and why it’s insufficient)

- MCAP publishes an official public specification and Foxglove ships a Rust SDK capable of logging MCAP data.
- ROS 2 documents the `rosbag2_storage_mcap` storage plugin.
- Rust already has `mcap`, `rosbags-rs`, and `rustbag`.
- But there is still no boring-default Rust crate family for **schema/topic lockfiles + conversion audits + semantic diffs + portable robot-data evidence bundles**.

# Design goals

1. **Schema-aware correctness** — topic and schema identity must be first-class.
2. **Replay-first** — small excerpts should still support meaningful repro.
3. **Conversion-aware** — rosbag2 ↔ MCAP workflows deserve explicit checks.
4. **Tool-neutral** — useful across Foxglove, ROS tools, and private pipelines.
5. **Compact evidence** — prefer slices, manifests, and summaries over giant full-log attachments.

# MVP surface

- Minimal types: `BagSnapshot`, `ChannelSnapshot`, `SchemaSnapshot`, `ReplayTrace`, `BagProfile`, `BagReport`
- Minimal functions:
  - `scan_bag()`
  - `verify_profile()`
  - `diff_bags()`
  - `check_conversion()`
  - `write_bundle()`
- Feature flags:
  - `mcap`
  - `rosbag2`
  - `serde`
  - `zstd`
  - `redaction`

# Compatibility story

- MVP should target official **MCAP** files plus the public **rosbag2 MCAP storage** path first.
- The crate should complement `mcap`, `rosbags-rs`, `rustbag`, and Foxglove logging instead of replacing them.
- SQLite-backed rosbag2 input can be treated as an adapter edge, not core storage ambition.
- Schema-encoding support should be explicit and incremental.

# Conformance & fixtures

- Tiny public bags with a few topics, schemas, and known clock behaviors.
- Goldens for schema drift, missing topics, duplicate channels, and conversion drift.
- Replay fixtures that prove small excerpts still preserve debugging value.
- Cross-tool fixtures for direct MCAP write versus rosbag2-converted MCAP.

# Path to boring stability

- Stabilize profile locks and finding vocabulary before adding richer playback machinery.
- Keep first-class support to a narrow set of common encodings and adapters.
- Freeze bundle layout after proving it works in CI and vendor handoff.
- Add larger ecosystem adapters only after core semantics stop changing.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 24/30**

# Minimum lovable MVP

A CLI and library that scan an MCAP or rosbag2-derived MCAP file, verify topic/schema/clock expectations from a lockfile, compare it with a second bag or conversion output, and emit a compact `*.mcapbundle.zip`.

# De-risk plan

1. Start with manifests, schema hashes, and clock/topic checks before deeper playback semantics.
2. Limit early support to common encodings and public examples.
3. Prefer reduced excerpts and summaries over full-bag shipping.
4. Treat rosbag2 conversion as an adapter layer with explicit scope.

# Non-goals

- Not a full robotics middleware.
- Not a live visualization platform.
- Not a giant offline data lake for robot logs.

# Architecture & API sketch

```rust
pub struct BagReport {
    pub profile_id: String,
    pub schema_findings: Vec<Finding>,
    pub channel_findings: Vec<Finding>,
    pub replay_findings: Vec<Finding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn verify_profile(profile: &BagProfile, bag: &BagSnapshot) -> Result<BagReport>;
pub fn check_conversion(source: &BagSnapshot, converted: &BagSnapshot) -> Result<Vec<DiffFinding>>;
```

Bundle draft: `profile.toml`, `bag.json`, `channels.json`, `schemas.json`, `timeline.json`, `diff.json`, `excerpt.mcap`, `notes.md`.

# Security / safety model

- Treat log files and schemas as untrusted inputs.
- Default to excerpting and metadata-first bundles.
- Support topic-name and payload redaction maps.
- Capture hashes and offsets so reduced bundles still remain auditable.

# Maintenance & governance plan

- Keep core focused on IRs, profile packs, and evidence bundles.
- Let tool-specific integrations live in adapters.
- Grow a small public bag corpus and conversion tests.
- Avoid binding core success to one robotics vendor or visualization stack.

# Milestones

## 0.1
- bag scanner
- profile verifier
- bundle writer

## 0.2
- conversion audit
- semantic diffs
- replay excerpts

## 1.0
- stable `*.mcapbundle.zip`
- documented profile packs
- public multi-tool fixture corpus

# Open questions

- Which channel/schema fields need to be mandatory in profile locks?
- How should clock domains and simulated time be represented?
- Which rosbag2 conversion behaviors are worth standardizing in findings vocabulary?

# Sources

- MCAP specification: https://mcap.dev/spec
- ROS 2 `rosbag2_storage_mcap`: https://docs.ros.org/en/iron/p/rosbag2_storage_mcap/
- `mcap`: https://docs.rs/mcap
- `rosbags-rs`: https://docs.rs/rosbags-rs
- `rustbag`: https://docs.rs/crate/rustbag/latest
- Foxglove SDK: https://docs.foxglove.dev/docs/sdk
