---
id: P-0318
title: OGC SensorThings API + MQTT Conformance & Replay Kit — geospatial IoT profile lockfiles, observation semantics, and portable incident bundles
status: idea
domains: [geospatial, iot, sensorthings, mqtt, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://www.ogc.org/standards/sensorthings/
  - https://docs.ogc.org/is/18-088/18-088.html
  - https://docs.ogc.org/is/15-078r6/15-078r6.html
  - https://crates.io/crates/sensorthings-validator
  - https://developers.sensorup.com/docs/
---

# Problem

SensorThings already gives the ecosystem a strong standard surface: OData-flavored REST, geospatial metadata, observations, and MQTT-based publish/subscribe behavior. But real deployments still fail in the same annoying ways:

- observation payloads are syntactically valid yet semantically wrong,
- timestamp/freshness assumptions drift,
- pagination/query behavior differs across servers,
- MQTT topics and update semantics are hard to replay,
- and operators share screenshots and ad hoc curls instead of reproducible artifacts.

The worthy Rust crate contribution is not a generic “IoT platform.” It is a **SensorThings conformance and replay kit** that makes server/client behavior testable, diffable, and portable.

# What it provides

- `sta-ir` — canonical IR for Things, Datastreams, Observations, FeaturesOfInterest, query expansions, paging, and MQTT update events.
- `sta-profile` — lockfiles for API capabilities, query expectations, paging rules, observed-property assumptions, and MQTT bindings.
- `sta-verify` — semantic checks for observations, geospatial references, time windows, entity relationships, and query result stability.
- `sta-replay` — deterministic replay for REST and MQTT traces.
- `sta-diff` — explainable diffs: “phenomenonTime outside profile window”, “entity link missing”, “MQTT update omits required relation context”, “query expansion changed cardinality”.
- `cargo sensorthings` — emit `*.stabundle.zip` for field incidents, public-data feed QA, and interoperability labs.

# What the crate should provide other people

1. **A portable incident and conformance artifact** for SensorThings servers and clients.
2. **Profile lockfiles** for exact query/paging/MQTT expectations.
3. **Replayable observation traces** that can be used in CI and vendor escalations.
4. **Semantic diagnostics** grounded in IoT/geospatial concepts instead of raw HTTP/MQTT logs.
5. **A bridge from today’s validator and server/client substrate to a repeatable interoperability discipline**.

# Users & user stories

- **Smart-city / public-sector operators**: “Validate yesterday’s feed against the profile we actually promised app developers.”
- **IoT platform vendors**: “Replay this failing MQTT sequence against the patched implementation.”
- **Mapping / analytics app teams**: “Prove whether the break came from timestamps, expansions, paging, or observation semantics.”
- **Research deployments**: “Archive a known-good evidence bundle for a public SensorThings endpoint.”

# Prior art (and why it’s insufficient)

- OGC’s SensorThings standard is mature and explicitly connects REST, JSON, OData conventions, and MQTT.
- There is now Rust validator substrate (`sensorthings-validator`) and real deployed platform documentation to build against.
- But the current gap is still **cross-implementation replay, profile pinning, semantic diffs, and portable failure bundles**.

# Design goals

1. **Observation-semantic first** — don’t stop at schema validity.
2. **REST + MQTT together** — treat the API and pub/sub surfaces as one operational system.
3. **Profile-aware** — capability and query assumptions must be explicit.
4. **Public-data friendly** — encourage Git-friendly bundles and synthetic fixtures.
5. **Adapter-friendly** — work with existing validators, servers, and clients.

# Non-goals

- Not a full IoT platform.
- Not a geospatial visualization product.
- Not a time-series database.

# Architecture & API sketch

```rust
pub struct StaReport {
    pub profile_id: String,
    pub verdicts: Vec<Verdict>,
    pub query_findings: Vec<QueryFinding>,
    pub observation_findings: Vec<ObservationFinding>,
    pub mqtt_findings: Vec<MqttFinding>,
}

pub fn verify_session(profile: &StaProfile, session: &StaSession) -> StaReport;
```

Bundle draft: `profile.toml`, `http/*.json`, `mqtt/*.jsonl`, `entities/*.json`, `verdicts.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Support redaction of exact coordinates, sensor identifiers, credentials, and broker endpoints.
- Make raw MQTT payload retention optional.
- Bound trace sizes for long-lived public feeds.
- Track profile, validator, and normalizer versions for reproducibility.

# Maintenance & governance plan

- Pin exact OGC standard snapshots and profile packs.
- Publish scenario packs for stale observations, pagination drift, entity-link breakage, and MQTT update ordering.
- Encourage public-demo and synthetic datasets first.
- Keep IR extensible for tasking overlays later without forcing them into MVP.

# Milestones

## 0.1
- Canonical SensorThings IR
- Profile lockfiles
- REST validation + bundle format

## 0.2
- MQTT replay
- Semantic observation checks
- Query/pagination diffing

## 1.0
- Stable `*.stabundle.zip`
- Adapters for validators and common server/client stacks
- CI-ready public-feed compatibility workflows

# Open questions

- How much OData nuance belongs in core versus adapters?
- Should tasking stay out of scope until sensing is stable?
- Can geospatial normalization stay lightweight enough for Git-friendly review?

# Sources

- OGC SensorThings overview: https://www.ogc.org/standards/sensorthings/
- SensorThings Part 1: Sensing v1.1: https://docs.ogc.org/is/18-088/18-088.html
- SensorThings Part 1 reference with MQTT note: https://docs.ogc.org/is/15-078r6/15-078r6.html
- `sensorthings-validator`: https://crates.io/crates/sensorthings-validator
- SensorThings platform docs: https://developers.sensorup.com/docs/
