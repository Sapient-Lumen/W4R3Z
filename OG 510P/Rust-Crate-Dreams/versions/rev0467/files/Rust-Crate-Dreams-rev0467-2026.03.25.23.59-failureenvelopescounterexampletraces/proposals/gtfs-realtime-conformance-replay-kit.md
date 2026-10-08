---
id: P-0313
title: GTFS + GTFS Realtime Conformance & Replay Kit — schedule-aware transit feeds, semantic trip diffs, and public-shareable evidence bundles
status: idea
domains: [transit, mobility, gtfs, realtime, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://gtfs.org/documentation/realtime/reference/
  - https://gtfs.org/documentation/realtime/realtime-best-practices/
  - https://crates.io/crates/gtfs-realtime
  - https://crates.io/crates/gtfs-rt
---

# Problem

GTFS Realtime looks deceptively simple because it is “just protobuf over HTTP,” but real production pain lives elsewhere:

- realtime entities must be interpreted relative to the static GTFS schedule,
- freshness and timestamp quality matter,
- detours, cancellations, added trips, and vehicle/trip mismatches create semantic rather than syntactic failures,
- public agencies and app developers still debug incidents through screenshots, dashboards, and one-off protobuf dumps.

A worthy Rust contribution would be a **schedule-aware conformance and replay kit** that makes transit feed failures reproducible, semantically explainable, and safe to share with downstream consumers.

# What it provides

- `gtfsrt-ir` — canonical IR that joins static GTFS context with realtime feed entities.
- `gtfsrt-verify` — checks freshness, entity validity, stop-time coherence, trip matching, alert semantics, and common best-practice failures.
- `gtfsrt-replay` — deterministic replay of feed snapshots against a pinned schedule.
- `gtfsrt-diff` — semantic diffs for “what changed for riders/operators” instead of byte-level protobuf noise.
- `gtfsrt-redact` — remove agency-private annotations while preserving timing and route/trip meaning.
- `cargo gtfsrt` — emit `*.gtfsrtbundle.zip` for agency QA, integrator support, and consumer-vendor debugging.

# What the crate should provide other people

1. **A transit-quality diagnostic artifact** that combines static and realtime context.
2. **Schedule-pinned replay** so old incidents can be reproduced after feed producers change.
3. **Best-practice enforcement** that catches stale or semantically misleading feeds before they hit riders.
4. **Semantic diffs** that help app teams understand rider-visible impact quickly.
5. **A neutral QA tool** for agencies, consultants, and feed consumers.

# Users & user stories

- **Transit agencies**: “Tell us whether our trip updates are internally coherent against the published schedule.”
- **Passenger-information vendors**: “Replay yesterday’s bad alert feed against our parser after the patch.”
- **Open-data consumers**: “Show exactly why this feed is formally valid protobuf but operationally misleading.”
- **Consultants / QA teams**: “Compare candidate realtime generators before procurement or rollout.”

# Prior art (and why it’s insufficient)

- GTFS Realtime has solid official documentation and best-practice guidance, which means a Rust crate can ground itself in published expectations.
- Rust has parsers and generators, but they do not by themselves solve **schedule-aware validation, semantic diffing, or incident portability**.
- Many current tools are agency- or vendor-specific and do not produce a common artifact that another party can replay.

# Design goals

1. **Static + realtime together** — never validate RT in a vacuum.
2. **Semantics before protobuf bytes** — rider-visible meaning matters most.
3. **Freshness-aware** — stale data should be diagnosed explicitly.
4. **Public-shareable** — bundles should be redactable enough for issue trackers and community QA.
5. **Incremental adoption** — usable first as a verifier/CLI before deeper embedding.

# Non-goals

- Not a trip-planning engine.
- Not a prediction model.
- Not a one-size-fits-all transit analytics platform.

# Architecture & API sketch

```rust
pub struct GtfsRtReport {
    pub schedule_id: String,
    pub verdicts: Vec<Verdict>,
    pub rider_visible_changes: Vec<SemanticChange>,
    pub freshness_findings: Vec<FreshnessFinding>,
}

pub fn verify_feed(schedule: &GtfsSchedule, feed: &FeedSnapshot) -> GtfsRtReport;
```

Bundle draft: `schedule.zip`, `feed.pb`, `normalized.json`, `verdicts.json`, `freshness.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Allow removal of internal URLs, contact fields, and agency-private annotations.
- Preserve timing provenance and source timestamps.
- Bound bundle size for long replay windows.
- Make timezone and service-date assumptions explicit.

# Maintenance & governance plan

- Pin GTFS and GTFS Realtime reference snapshots in fixture packs.
- Ship canonical examples for trip updates, vehicle positions, alerts, added trips, canceled trips, and detours.
- Keep schedule loading and verification engine independent from transit-app presentation logic.
- Publish a stable “common failure taxonomy” for agencies and consumers.

# Milestones

## 0.1
- Static+RT normalized IR
- Freshness + schedule-coherence checks
- `gtfsrtbundle` draft format

## 0.2
- Semantic diff engine
- Rider-visible change reporting
- Redaction presets and common fixture pack

## 1.0
- Stable `*.gtfsrtbundle.zip`
- Replay workflows for CI and vendor handoff
- Procurement/comparison scenario packs

# Open questions

- How much schedule normalization should be cached in bundle form?
- Which best-practice rules should be hard errors versus warnings?
- Should experimental support for GTFS-RT v2 features stay behind profiles initially?

# Sources

- GTFS Realtime reference: https://gtfs.org/documentation/realtime/reference/
- GTFS Realtime best practices: https://gtfs.org/documentation/realtime/realtime-best-practices/
- `gtfs-realtime`: https://crates.io/crates/gtfs-realtime
- `gtfs-rt`: https://crates.io/crates/gtfs-rt
