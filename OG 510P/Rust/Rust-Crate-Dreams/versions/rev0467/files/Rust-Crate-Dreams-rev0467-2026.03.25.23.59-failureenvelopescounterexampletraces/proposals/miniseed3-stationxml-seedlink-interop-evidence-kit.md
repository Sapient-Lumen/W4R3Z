---
id: P-0349
title: FDSN miniSEED 3 + StationXML + SeedLink Interop & Evidence Kit — waveform/inventory alignment, realtime replay, and transport-aware seismology bug bundles
status: idea
domains: [seismology, earth-science, scientific-data, realtime-systems, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://docs.fdsn.org/projects/miniseed3
  - https://docs.fdsn.org/projects/stationxml
  - https://docs.fdsn.org/projects/seedlink
  - https://docs.rs/stationxml-rs
  - https://docs.rs/crate/seedlink/latest
  - https://docs.rs/mseedio
---

# Problem

Seismological data exchange is not just one file format. The painful failures usually happen across **waveform records, metadata inventories, and realtime delivery**:

- miniSEED records arrive but cannot be interpreted correctly because StationXML inventory assumptions drifted,
- a SeedLink stream is “up” yet operationally wrong because selectors, identifiers, record versions, or metadata expectations disagree,
- archive and realtime paths disagree on what a station/stream actually means,
- and debugging often requires sending raw windows, XML inventories, and ad-hoc notes without a single evidence artifact tying them together.

Rust now has real format and protocol footholds, but it still lacks a boring-default crate for **FDSN waveform/inventory/transport conformance as one replayable surface**.

# What it provides

- `seis-ir` — canonical Rust IR for miniSEED windows, StationXML inventory snapshots, stream identifiers, and SeedLink session transcripts.
- `inventory-lock` — lockfiles pinning station/channel/instrument-response expectations, selector syntax, record-version assumptions, and time-window coverage.
- `seedlink-replay` — deterministic replay of subscription and packet flows with semantic checks over stream continuity and selector behavior.
- `inventory-diff` — semantic diffs like “same station code, different response chain”, “waveform present but inventory missing channel metadata”, or “selector matches unexpected stream IDs”.
- `waveform-check` — lightweight integrity and continuity checks over miniSEED3 windows linked to inventory context.
- `cargo seis-evidence` — emit `*.seisbundle.zip` for network operations, vendor debugging, or archive/realtime mismatch triage.

# What the crate should provide other people

1. **A boring default evidence bundle for seismology interoperability bugs**.
2. **One place to pin the relationship between waveform data, station inventory, and realtime selectors**.
3. **Replayable transport diagnostics** that travel with the bug report.
4. **Inventory-aware waveform findings** instead of isolated XML or binary-file complaints.
5. **A shared vocabulary for archive-versus-realtime drift**.

# Persona / who it’s for

- Seismic network operators
- Data-center and archive engineers
- Instrument / telemetry vendors
- Scientific software maintainers
- Rust developers working on seismology tooling

# Users & user stories

- **Network operator**: “Explain whether this outage is missing data, wrong selectors, or metadata drift.”
- **Archive engineer**: “Compare realtime packets and archived miniSEED windows for the same station and report mismatches.”
- **Vendor integrator**: “Ship a small replay bundle that proves our digitizer emits valid miniSEED3 but the downstream inventory is stale.”
- **Research software author**: “Verify that the waveform windows I load are interpretable under the pinned StationXML inventory.”

# Prior art (and why it’s insufficient)

- FDSN publishes active documentation for **miniSEED 3**, **StationXML**, and **SeedLink**.
- Rust now has meaningful substrate in `stationxml-rs`, `seedlink`, and `mseedio` / miniSEED crates.
- But there is still no boring-default Rust crate family for **inventory locks + waveform checks + realtime replay + portable interop bundles** across these layers.

# Design goals

1. **Cross-surface correctness** — waveform, inventory, and transport must be linked explicitly.
2. **Realtime-aware but archive-friendly** — evidence should explain both live and archived incidents.
3. **FDSN-first** — stick close to standard identifiers and semantics.
4. **Small-share bundles** — enough data to reproduce the failure without shipping full observatory archives.
5. **Implementation neutrality** — useful across Rust, C, Python, or Java downstream stacks.

# MVP surface

- Minimal types: `WaveformWindow`, `InventorySnapshot`, `SeedLinkTranscript`, `SeisProfile`, `SeisReport`
- Minimal functions:
  - `load_inventory()`
  - `scan_waveform_window()`
  - `replay_seedlink()`
  - `diff_inventory()`
  - `write_bundle()`
- Feature flags:
  - `miniseed3`
  - `stationxml`
  - `seedlink`
  - `serde`
  - `redaction`

# Compatibility story

- MVP should target **miniSEED 3**, current **StationXML** docs/schema usage, and the current public **SeedLink** documentation.
- The crate should complement existing libraries and services rather than replace a data center stack.
- It should support partial inventories and partial windows as long as it can report what is missing.
- Server-specific SeedLink quirks should live in optional profile packs.

# Conformance & fixtures

- Tiny synthetic waveform windows with intentional gaps, overlaps, and identifier mismatches.
- Small StationXML inventories with known response-chain and channel-coverage cases.
- SeedLink transcript fixtures for normal subscription, wrong selector, and mixed-version behavior.
- Goldens for archive/realtime mismatches and inventory drift.

# Path to boring stability

- Stabilize identifiers, profile packs, and findings vocabulary before broadening into signal processing.
- Keep waveform checks structural/integrity-focused rather than analytical.
- Freeze bundle layout only after proving it covers real operations incidents.
- Add richer vendor adapters later.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 3/5
- Adoptability: 3/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 24/30**

# Minimum lovable MVP

A CLI and library that load a StationXML inventory, inspect one or more miniSEED3 windows, optionally replay a SeedLink transcript, and emit a `*.seisbundle.zip` explaining selector, identifier, and inventory mismatches.

# De-risk plan

1. Start with identifiers, inventory coverage, and transcript semantics before deeper response/physics logic.
2. Use tiny synthetic fixtures and a few public educational examples.
3. Keep partial-data behavior explicit rather than pretending missing context does not matter.
4. Separate server quirks into profile packs.

# Non-goals

- Not a seismic processing/analysis framework.
- Not a waveform visualization suite.
- Not a replacement for full data-center infrastructure.

# Architecture & API sketch

```rust
pub struct SeisReport {
    pub profile_id: String,
    pub waveform_findings: Vec<Finding>,
    pub inventory_findings: Vec<Finding>,
    pub transport_findings: Vec<Finding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn scan_waveform_window(profile: &SeisProfile, window: &WaveformWindow) -> Result<SeisReport>;
pub fn replay_seedlink(profile: &SeisProfile, tx: &SeedLinkTranscript) -> Result<Vec<Finding>>;
```

Bundle draft: `profile.toml`, `inventory.xml`, `windows/`, `seedlink-transcript.jsonl`, `findings.json`, `diff.json`, `notes.md`.

# Security / safety model

- Treat XML and binary inputs as untrusted.
- Default to small excerpt windows and identifier/redaction support.
- Preserve hashes and timing metadata even when payload excerpts are reduced.
- Record exact parser/library versions used during validation.

# Maintenance & governance plan

- Keep the core focused on IRs, profile packs, and evidence bundles.
- Version findings vocabulary carefully because scientific archives are long-lived.
- Prefer public synthetic fixtures and openly licensed examples.
- Encourage collaboration with domain users before widening scope.

# Milestones

## 0.1
- inventory loader
- waveform window scan
- bundle writer

## 0.2
- SeedLink replay
- semantic diffs
- profile packs

## 1.0
- stable `*.seisbundle.zip`
- public fixture corpus
- documented archive/realtime interoperability policy

# Open questions

- How much response/instrument modeling belongs in core?
- How should partial inventories be represented in findings?
- Which SeedLink version quirks deserve first-class profile support?

# Sources

- FDSN miniSEED 3 docs: https://docs.fdsn.org/projects/miniseed3
- FDSN StationXML docs: https://docs.fdsn.org/projects/stationxml
- FDSN SeedLink docs: https://docs.fdsn.org/projects/seedlink
- `stationxml-rs`: https://docs.rs/stationxml-rs
- `seedlink`: https://docs.rs/crate/seedlink/latest
- `mseedio`: https://docs.rs/mseedio
