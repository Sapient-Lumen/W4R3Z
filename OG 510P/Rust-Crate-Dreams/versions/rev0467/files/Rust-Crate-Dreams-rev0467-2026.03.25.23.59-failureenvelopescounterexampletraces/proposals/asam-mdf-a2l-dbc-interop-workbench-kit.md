---
id: P-0405
title: ASAM MDF + A2L + DBC Interop Workbench Kit — measurement locks, signal-mapping diffs, and calibration-grade evidence bundles
status: idea
domains: [automotive, embedded, telemetry, data, interoperability, validation]
last_reviewed: 2026-03-06
evidence:
  - https://www.asam.net/standards/detail/mdf/wiki/
  - https://www.asam.net/standards/detail/mcd-2-mc/
  - https://docs.rs/a2lfile
  - https://docs.rs/asammdf
  - https://docs.rs/can_decode
  - https://crates.io/crates/dbc-rs
---

# Problem

Rust has growing building blocks for automotive measurement and calibration workflows: crates for A2L parsing/editing, crates for MDF reading/writing, and crates that understand de facto DBC signal dictionaries well enough to decode CAN traffic. But the painful problems in real measurement pipelines are not just “can I parse file X?” They are about proving which metadata view was applied to which recording, which signal mapping was assumed, and what was lost or silently normalized between formats.

The painful failures still happen at the seam between:

- **an ASAM MDF recording and the exact A2L metadata used to interpret ECU measurements**,
- **bus traffic stored or summarized in measurement files and the DBC dictionary used to decode it**,
- **A2L-calibration semantics and DBC bus-signal semantics that look similar but are not the same contract**,
- **recordings, sidecar metadata, and support/debugging workflows that currently depend on notebooks, screenshots, and tribal knowledge**,
- and **file conversions that silently drop time-base assumptions, scaling, units, muxing, byte order, or channel provenance.**

The missing Rust contribution is not another parser. It is an **interop workbench** for pinned measurement bundles, signal-map diffs, conversion-loss accounting, and calibration-grade evidence artifacts.

# What it provides

- `measurement.lock` — pins MDF revision, A2L version/hash, DBC dictionaries, byte-order/scaling assumptions, time-base expectations, and decoding overlays.
- `signal-map` — normalized mapping of channels, ECU objects, bus messages, signals, units, scaling, and provenance.
- `semantic-diff` — explains what changed between two measurement/decode setups in operator language.
- `loss-report` — explicit accounting of what a conversion or export preserved, normalized, dropped, or guessed.
- `cargo measure-evidence` — emits `*.mcalbundle.zip` with locks, signal maps, sliced evidence files, and findings.

# What the crate should provide other people

1. **A boring artifact for measurement interpretation drift**.
2. **Pinned metadata sidecars** that make recordings reproducibly interpretable.
3. **Signal-map diffs** instead of improvised spreadsheet comparisons.
4. **Honest loss reporting** across MDF/A2L/DBC boundaries.
5. **Portable evidence bundles** small enough for calibration, testing, and support handoff.

# Persona / who it’s for

- Automotive tooling teams using Rust for measurement/calibration utilities
- Engineers decoding recorded ECU and bus data
- QA/release teams validating telemetry export pipelines
- Data platform teams importing automotive measurements into broader analytics stacks

# Users & user stories

- **Calibration engineer**: “Pin the exact A2L and decoding assumptions used for this MF4 slice.”
- **Bus analyst**: “Show me whether the discrepancy comes from the DBC, the scaling, or the recording itself.”
- **Tool maintainer**: “Emit a loss report when exporting or normalizing measurements.”
- **Support engineer**: “Share one compact bundle instead of an MF4 plus loose notes and guesswork.”

# Prior art (and why it’s insufficient)

- ASAM MDF and ASAM MCD-2 MC (A2L) provide serious standards surfaces for measurement and calibration.
- Rust has meaningful substrate in `a2lfile`, `asammdf`, and newer MDF crates.
- Rust also has de facto DBC crates for CAN signal parsing and encode/decode workflows.

What Rust still lacks is a **coordination layer** for pinned measurement metadata, signal-map normalization, loss accounting, and reviewable evidence bundles.

# Design goals

1. **Loss-explicit** — conversions and exports must say what changed.
2. **Metadata-pinned** — recordings without pinned sidecars are not reproducible enough.
3. **A2L/DBC boundary-honest** — similar-looking signal concepts must not be collapsed prematurely.
4. **Slice-friendly** — useful artifacts must work on small time windows, not only giant files.
5. **Calibration-grade** — units, scaling, provenance, and timestamp assumptions must be first-class.

# MVP surface

- Minimal types: `MeasurementLock`, `SignalMap`, `MeasurementFinding`, `LossReport`, `MeasurementBundle`
- Minimal functions:
  - `load_mdf()`
  - `load_a2l()`
  - `load_dbc()`
  - `build_signal_map()`
  - `write_bundle()`
- Feature flags:
  - `mdf`
  - `a2l`
  - `dbc`
  - `slice-export`

# Compatibility story

- Starts as an offline artifact workbench over source files and small slices.
- Supports ASAM standards as the normative core while treating DBC as a de facto overlay surface.
- Keeps transport/protocol logging stacks outside the MVP unless needed for evidence capture.
- Can later attach exporters to Arrow/Parquet or analytics workflows without changing the core lock model.

# Conformance & fixtures

- Goldens for channel/unit/scaling drift, byte-order mistakes, muxed CAN signals, and timestamp normalization.
- Fixtures pairing small MF4 slices with corresponding A2L and DBC files.
- Public examples of “same recording, different metadata, different interpretation.”
- Loss-report goldens for common export and normalization steps.

# Path to boring stability

- Stabilize `measurement.lock`, `signal-map`, and `loss-report` before chasing full conversion suites.
- Start with tiny slices and summaries rather than giant recordings.
- Keep DBC-specific assumptions clearly marked as de facto overlays.
- Treat broad analytics/export integration as a later layer.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 3/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 25/30**

# Minimum lovable MVP

A Rust library and CLI that pin MDF/A2L/DBC interpretation assumptions, build a normalized signal map for a small recording slice, compute semantic diffs and loss reports, and emit compact `*.mcalbundle.zip` artifacts.

# De-risk plan

1. Start with A2L + DBC + tiny measurement slices.
2. Add explicit loss accounting next.
3. Keep giant-file performance work secondary to artifact correctness.
4. Pilot with small, sanitized fixture corpora before claiming broad format coverage.

# Non-goals

- Not a full calibration suite.
- Not a DAQ system.
- Not a replacement for domain-specific analysis GUIs.
- Not a universal automotive protocol stack.

# Architecture & API sketch

```rust
pub struct MeasurementLock {
    pub mdf_version: String,
    pub a2l_hash: String,
    pub dbc_hashes: Vec<String>,
    pub timebase_profile: Option<String>,
}

pub fn load_mdf(path: &std::path::Path) -> Result<MeasurementSlice>;
pub fn build_signal_map(slice: &MeasurementSlice, a2l: &A2lIr, dbcs: &[DbcIr]) -> Result<SignalMap>;
pub fn diff_signal_maps(old: &SignalMap, new: &SignalMap) -> Vec<MeasurementFinding>;
```

Bundle draft: `measurement.lock`, `slice.mf4`, `ecu.a2l`, `signals.dbc`, `signal-map.json`, `loss-report.json`, `notes.md`.

# Security / safety model

- Support slicing, hashing, and redaction so bundles do not need to ship full proprietary recordings.
- Preserve source hashes for A2L/DBC provenance.
- Distinguish exact-source values from inferred or normalized values.
- Bound resource usage for large source files.

# Maintenance & governance plan

- Keep the core about locks, signal maps, diffs, and loss reports.
- Version ASAM and de facto overlays separately.
- Publish a tiny sanitized corpus of measurement fixtures.
- Resist drift into building a giant automotive platform.

# Milestones

## 0.1
- `measurement.lock`
- A2L/DBC-aware signal map
- small-slice evidence bundles

## 0.2
- loss reports
- MDF round-trip checks
- public fixture corpus

## 1.0
- stable `*.mcalbundle.zip`
- documented compatibility policy for ASAM vs de facto overlays
- broader exporter adapters

# Open questions

- What is the best neutral IR for signals that come from both ECU and bus metadata worlds?
- How much MDF structure belongs in the core versus adapter-specific views?
- Which conversion-loss categories should be warnings versus hard errors?

# Sources

- ASAM MDF wiki: https://www.asam.net/standards/detail/mdf/wiki/
- ASAM MCD-2 MC (A2L): https://www.asam.net/standards/detail/mcd-2-mc/
- `a2lfile`: https://docs.rs/a2lfile
- `asammdf`: https://docs.rs/asammdf
- `can_decode`: https://docs.rs/can_decode
- `dbc-rs`: https://crates.io/crates/dbc-rs
