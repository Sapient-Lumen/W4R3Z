---
id: P-0330
title: ASAM OpenDRIVE 1.8.1 + OpenSCENARIO Replay & Conformance Kit — road/scenario lockfiles, semantic diffs, and simulator-neutral evidence bundles
status: idea
domains: [automotive, simulation, adas, opendrive, openscenario, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://publications.pages.asam.net/standards/ASAM_OpenDRIVE/ASAM_OpenDRIVE_Specification/latest/specification/index.html
  - https://www.asam.net/standards/detail/openscenario/v200/
  - https://www.asam.net/standards/detail/openscenario-xml/
  - https://www.asam.net/standards/asam-quality-checker/
  - https://github.com/asam-ev/qc-opendrive
  - https://github.com/asam-ev/qc-openscenarioxml
  - https://crates.io/crates/opendrive
  - https://github.com/ashfaqfarooqui/openscenario-rs
---

# Problem

Rust has started to grow real OpenDRIVE/OpenSCENARIO footholds, but road-network and scenario interoperability is still dominated by non-Rust toolchains and ad hoc debugging. The painful failures happen at the **map/scenario/simulator seam**:

- OpenDRIVE road descriptions that load differently across tools,
- scenarios that are syntactically valid but mismatched to the road, entities, or timing assumptions they depend on,
- conversion pipelines that silently drop semantics,
- checker outputs that prove “a rule failed” without giving a portable, replayable bug bundle,
- and support cases that still travel as `*.xodr`, `*.xosc`, screenshots, and simulator videos.

The worthy crate contribution is a **replay and conformance kit** that turns roads, scenarios, checker results, and scenario executions into deterministic, diffable, simulator-neutral evidence bundles.

# What it provides

- `road-ir` — canonical IR for OpenDRIVE roads, lanes, junctions, signals, and reference-line geometry.
- `scenario-ir` — canonical IR for entities, maneuvers, triggers, actions, catalogs, parameters, and timing expectations.
- `asam-profile` — lockfiles pinning exact OpenDRIVE/OpenSCENARIO assumptions, simulator constraints, checker versions, and local policy rules.
- `asam-verify` — semantic checks for road/scenario compatibility, reference resolution, geometry sanity, and rule-pack conformance.
- `asam-replay` — deterministic replay metadata for scenario runs, checker invocations, and simulator-neutral timelines.
- `asam-diff` — explainable diffs: “lane reference broke”, “signal moved”, “trigger timing changed”, “catalog reference lost”, “checker verdict regressed”.
- `cargo asam` — emit `*.asambundle.zip` for CI, simulator comparison, or vendor escalation.

# What the crate should provide other people

1. **A boring default artifact for simulation interoperability bugs** instead of file dumps plus videos.
2. **Profile pinning** for the exact road/scenario/checker assumptions under test.
3. **Semantic diffs** that talk in road and scenario terms rather than generic XML deltas.
4. **Replayable evidence** that helps compare simulator behavior and validation results.
5. **A neutral Rust layer** above official ASAM checkers and simulator-specific stacks.

# Persona / who it’s for

- ADAS/AV simulation engineers
- Scenario-library maintainers
- HD-map and simulation-tool integrators
- CI/validation teams
- Rust developers building automotive-toolchain infrastructure

# Users & user stories

- **Scenario engineer**: “Show me whether this scenario failure is really caused by a road-model change or by a checker-policy change.”
- **Tool integrator**: “Diff these two OpenDRIVE/OpenSCENARIO pairs semantically before I feed them into a simulator.”
- **Validation lead**: “Bundle the road, scenario, checker verdicts, and timeline metadata into one reproducible artifact.”
- **Vendor support**: “Redact proprietary labels and parameters but keep the failure explainable.”

# Prior art (and why it’s insufficient)

- ASAM publishes current OpenDRIVE and OpenSCENARIO standards, and ASAM has now released an official Quality Checker Framework plus checker bundles for OpenDRIVE and OpenSCENARIO XML.
- Rust has an `opendrive` crate and at least early `openscenario-rs` substrate.
- But there is still no boring-default Rust crate family for **lockfiles + checker adapters + road/scenario semantic diffs + replayable evidence bundles**.

# Design goals

1. **Road + scenario together** — neither side is meaningful alone for real interop debugging.
2. **Checker-aware** — official checker outputs should be normalized, not ignored.
3. **Simulator-neutral** — evidence should survive beyond a single simulator product.
4. **Version explicitness** — every report must record exact spec/checker assumptions.
5. **Scope discipline** — conformance and replay first, not a full simulator engine.

# MVP surface

- Minimal types: `RoadSnapshot`, `ScenarioSnapshot`, `AsamProfile`, `RunTimeline`, `AsamReport`
- Minimal functions:
  - `load_road()`
  - `load_scenario()`
  - `verify_pair()`
  - `import_checker_report()`
  - `diff_pair()`
  - `write_bundle()`
- Feature flags:
  - `opendrive`
  - `openscenario-xml`
  - `checker-adapters`
  - `redaction`
  - `serde`

# Compatibility story

- MVP should target **OpenDRIVE 1.8.1** and **OpenSCENARIO XML** first.
- OpenSCENARIO 2.x should initially be handled as profile metadata and future companion parsing rather than full first-pass support.
- It should integrate official checker outputs where possible instead of re-implementing everything from scratch.
- MVP should intentionally avoid becoming a simulator, converter hub, or full map editor.

# Conformance & fixtures

- Synthetic roads and scenarios with known-good and known-bad compatibility relations.
- Fixture packs for lane-link issues, signal-reference issues, parameter binding, trigger timing, and catalog-reference breakage.
- Golden imports from official ASAM checker bundles.
- Optional replay metadata adapters from simulator logs, without hard-coding a single simulator format into core.

# Path to boring stability

- First stabilize IR and semantic verdict vocabulary on synthetic fixtures.
- Then prove checker import and diff usefulness across at least two toolchains.
- Freeze bundle format only after redaction and replay survive real cross-vendor incidents.
- Keep version and checker metadata explicit and immutable inside bundles.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 3/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 4/5
- **Total: 22/30**

# Minimum lovable MVP

A CLI and library that ingest one `*.xodr` plus one `*.xosc`, validate them against a pinned profile, normalize official checker findings, produce a semantic diff against a prior pair, and emit a redactable `*.asambundle.zip`.

# De-risk plan

1. Start with static compatibility and checker import before runtime replay.
2. Keep OpenSCENARIO XML first-class and defer full 2.x DSL support.
3. Use official checker results as anchors for early credibility.
4. Add simulator-specific adapters only after the generic bundle format is stable.

# Non-goals

- Not a vehicle-dynamics or traffic simulator.
- Not a full OpenDRIVE or OpenSCENARIO editor.
- Not a generic conversion platform for every automotive standard.

# Architecture & API sketch

```rust
pub struct AsamReport {
    pub profile_id: String,
    pub compatibility_findings: Vec<Finding>,
    pub checker_findings: Vec<Finding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn verify_pair(profile: &AsamProfile, road: &RoadSnapshot, scenario: &ScenarioSnapshot) -> AsamReport;
pub fn import_checker_report(report: &[u8]) -> Vec<Finding>;
```

Bundle draft: `profile.toml`, `road.xodr`, `scenario.xosc`, `normalized/road.json`, `normalized/scenario.json`, `checker/`, `timeline.jsonl`, `verdicts.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Redact proprietary labels, catalog identifiers, and internal filenames when needed.
- Bound XML parsing and external-resource resolution by default.
- Preserve reference integrity after redaction.
- Record checker and profile versions for reproducibility.

# Maintenance & governance plan

- Treat checker adapters as optional crates layered on a stable IR.
- Ship fixture packs and version pins alongside the library.
- Keep 2.x support incremental rather than letting the DSL explode MVP scope.
- Encourage cross-tool redacted incident bundles as community fixtures.

# Milestones

## 0.1
- OpenDRIVE + OpenSCENARIO XML IR subset
- Pair verification
- Bundle writer and checker import

## 0.2
- Semantic diffs
- Redaction support
- Basic replay timeline support

## 1.0
- Stable `*.asambundle.zip`
- Multi-tool checker/simulator fixture corpus
- CI-ready regression workflows

# Open questions

- How much OpenSCENARIO 2.x belongs in the same crate family versus a companion parser/adapter?
- Can road/scenario diffs stay generic enough across simulator products?
- Should runtime trajectory assertions live in core or in simulator adapters?

# Sources

- ASAM OpenDRIVE 1.8.1 spec: https://publications.pages.asam.net/standards/ASAM_OpenDRIVE/ASAM_OpenDRIVE_Specification/latest/specification/index.html
- ASAM OpenSCENARIO 2.x: https://www.asam.net/standards/detail/openscenario/v200/
- ASAM OpenSCENARIO XML: https://www.asam.net/standards/detail/openscenario-xml/
- ASAM Quality Checker: https://www.asam.net/standards/asam-quality-checker/
- `qc-opendrive`: https://github.com/asam-ev/qc-opendrive
- `qc-openscenarioxml`: https://github.com/asam-ev/qc-openscenarioxml
- `opendrive`: https://crates.io/crates/opendrive
- `openscenario-rs`: https://github.com/ashfaqfarooqui/openscenario-rs
