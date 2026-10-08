---
id: P-0354
title: WMO GRIB2 + BUFR Interop & Evidence Kit — table/version locks, ecCodes normalization, and replayable meteorology bug bundles
status: idea
domains: [meteorology, science-data, binary-formats, interoperability, testing]
last_reviewed: 2026-03-06
evidence:
  - https://community.wmo.int/about-manual-codes-volume-i2
  - https://codes.wmo.int/codeform/grib2
  - https://github.com/ecmwf/eccodes
  - https://docs.rs/grib
  - https://docs.rs/eccodes
---

# Problem

Rust can already decode pieces of GRIB and interface with ecCodes, but operational meteorology failures usually happen at the seam between:

- **WMO code-form versions and table updates**,
- local centre-specific tables or conventions,
- GRIB / BUFR message semantics that are hard to diff meaningfully,
- and opaque tool output that is difficult to turn into a stable CI artifact.

A file can parse and still be wrong for the actual table version, local definition set, or downstream workflow. The missing Rust contribution is a **table-pinned interop and evidence kit** for GRIB2 / BUFR workflows, not another low-level decoder.

# What it provides

- `metcode-ir` — canonical Rust IR for selected GRIB2 and BUFR message metadata, descriptors, tables, and normalized key/value views.
- `table-lock` — lockfiles pinning WMO table versions, local tables, and ecCodes definition-set assumptions.
- `eccodes-adapter` — stable import of ecCodes findings and normalized key extracts.
- `message-check` — bounded checks for edition/table mismatches, missing local definitions, unsupported descriptors, and message-shape drift.
- `metcode-diff` — semantic diffs such as “same field values, different table interpretation” or “local table dependency introduced”.
- `cargo metcode-evidence` — emit `*.gribbufrbundle.zip` for CI, operational triage, or data-provider handoff.

# What the crate should provide other people

1. **A boring default artifact for GRIB/BUFR interoperability bugs**.
2. **Pinned table and definition-set expectations** that survive WMO/ecCodes churn.
3. **Explainable differences** between raw parse success and semantic incompatibility.
4. **Small evidence bundles** that avoid attaching giant forecast products to every ticket.
5. **A bridge from ecCodes output to reusable Rust-native CI fixtures**.

# Persona / who it’s for

- Meteorology and climate-data engineers
- Weather-data platform teams
- Rust developers building forecast or observation pipelines
- Operations teams integrating multiple providers
- QA teams pinning decoding behavior across table updates

# Users & user stories

- **Data-ingest maintainer**: “Tell me whether this failure comes from a table update, a missing local definition, or a genuine parser bug.”
- **Provider integrator**: “Send a small bundle that proves our feed depends on a local table or unsupported descriptor.”
- **CI owner**: “Gate decoder upgrades on stable semantic findings instead of raw stdout changes from external tools.”
- **Archive engineer**: “Diff two meteorological products semantically, not just bytewise.”

# Prior art (and why it’s insufficient)

- WMO maintains the **Manual on Codes** and GRIB2 / BUFR code-form registries.
- ECMWF’s **ecCodes** remains the practical reference toolchain for decoding and encoding these formats.
- Rust has substrate in `grib` and `eccodes`.
- But there is still no boring-default Rust crate family for **table locks + ecCodes normalization + semantic diffs + portable evidence bundles**.

# Design goals

1. **Table-first** — always record which tables and definitions were assumed.
2. **Tool-adapter first** — complement ecCodes instead of competing with it immediately.
3. **Semantic diffs** — distinguish byte drift from meaning drift.
4. **Bounded scope** — start with metadata and message-structure correctness.
5. **Operationally shareable** — bundles should stay small and text-heavy by default.

# MVP surface

- Minimal types: `MetMessage`, `DefinitionLock`, `MetcodeProfile`, `MetReport`, `MetDiffFinding`
- Minimal functions:
  - `inspect_message()`
  - `run_eccodes()`
  - `validate_tables()`
  - `diff_reports()`
  - `write_bundle()`
- Feature flags:
  - `grib2`
  - `bufr`
  - `eccodes`
  - `serde`
  - `redaction`

# Compatibility story

- MVP should target **GRIB edition 2** and modern BUFR workflows first.
- The crate should work alongside existing Rust readers and ecCodes-based integrations.
- Local-table packs should remain optional and separately versioned.
- The core should stay metadata/message-structure focused, not full scientific interpretation.

# Conformance & fixtures

- Tiny public GRIB2 and BUFR messages with pinned table versions.
- Goldens for table-version drift, missing local definitions, unsupported descriptors, and ecCodes-verdict drift.
- Sample bundles with extracted keys and descriptor trees rather than full operational feeds.
- Fixtures that show how the same bytes can decode differently under different definition assumptions.

# Path to boring stability

- Stabilize the IR and findings model before broadening parameter coverage.
- Freeze lockfile format only after it works across a few real providers and table versions.
- Keep early checks metadata-first and deterministic.
- Add richer semantic overlays only after core table/version reproducibility is solid.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 3/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 23/30**

# Minimum lovable MVP

A CLI and library that inspect GRIB2 or BUFR messages, run ecCodes with pinned definition assumptions, normalize the results, and emit a compact `*.gribbufrbundle.zip` that makes table/version bugs reproducible.

# De-risk plan

1. Start with inspection and normalization, not custom decoding of everything.
2. Use only tiny public fixtures at first.
3. Treat local-table support as optional profile packs.
4. Keep scientific-content validation outside the early core.

# Non-goals

- Not a weather-model post-processing engine.
- Not a visualization stack.
- Not a replacement for ecCodes.
- Not a full meteorological-analysis toolkit.

# Architecture & API sketch

```rust
pub struct MetReport {
    pub format: String,
    pub table_lock: String,
    pub findings: Vec<Finding>,
    pub diffs: Vec<MetDiffFinding>,
}

pub fn validate_tables(lock: &DefinitionLock, msg: &MetMessage) -> Result<MetReport>;
pub fn run_eccodes(msg: &MetMessage) -> Result<Vec<Finding>>;
```

Bundle draft: `profile.toml`, `message.bin`, `keys.json`, `tables.json`, `eccodes.json`, `diff.json`, `notes.md`.

# Security / safety model

- Treat all meteorological messages as untrusted binary inputs.
- Record exact ecCodes and definition-set versions.
- Default to including excerpts and normalized metadata, not full products.
- Support hashing of external definition assets when they affect results.

# Maintenance & governance plan

- Keep core focused on lockfiles, findings, and bundle formats.
- Version local-table packs separately.
- Maintain a small public corpus spanning a few representative GRIB2 / BUFR cases.
- Avoid overpromising scientific interpretation beyond message semantics.

# Milestones

## 0.1
- message inspector
- ecCodes adapter
- bundle writer

## 0.2
- table locks
- semantic diffs
- local-table packs

## 1.0
- stable `*.gribbufrbundle.zip`
- public fixture corpus
- documented policy for table/version drift

# Open questions

- Which local-table ecosystems deserve first-party packs?
- How much BUFR descriptor interpretation belongs in core versus adapters?
- What minimum excerpt is enough to debug operational ingest issues without shipping large products?

# Sources

- WMO Manual on Codes Volume I.2 overview: https://community.wmo.int/about-manual-codes-volume-i2
- WMO GRIB2 registry: https://codes.wmo.int/codeform/grib2
- WMO version tables: https://community.wmo.int/previous-versions
- ECMWF ecCodes: https://github.com/ecmwf/eccodes
- `grib`: https://docs.rs/grib
- `eccodes`: https://docs.rs/eccodes
