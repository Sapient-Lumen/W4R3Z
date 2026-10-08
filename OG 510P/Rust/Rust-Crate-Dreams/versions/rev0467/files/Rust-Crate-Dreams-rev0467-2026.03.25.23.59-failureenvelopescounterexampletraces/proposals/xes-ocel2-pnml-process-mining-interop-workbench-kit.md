---
id: P-0368
title: XES + OCEL 2.0 + PNML Process-Mining Interop Workbench Kit — log/model locks, loss-aware transforms, and replayable conformance bundles
status: idea
domains: [data, analytics, process-mining, workflows, standards, interoperability, validation, tooling]
last_reviewed: 2026-03-06
evidence:
  - https://www.xes-standard.org/
  - https://www.ocel-standard.org/specification/overview/
  - https://www.pnml.org/
  - https://docs.rs/process_mining
  - https://crates.io/crates/process_mining
  - https://publications.rwth-aachen.de/record/1002213/files/1002213.pdf
---

# Problem

Rust now has surprising depth in process-mining substrate, but operator pain still concentrates at the seam between:

- event-log standards (`XES`) and object-centric event-log standards (`OCEL 2.0`),
- execution data and process-model interchange (`PNML`),
- extension/profile assumptions and what downstream tools actually preserve,
- discovery/conformance outputs that are hard to compare after log normalization or format conversion,
- and “this log/model worked in tool A but not tool B” bug reports with no compact, replayable artifact.

The missing Rust contribution is not another mining algorithm library. It is a **loss-aware interop workbench** that makes process-mining format boundaries explicit, testable, and shareable.

# What it provides

- `pm-lock` — lockfiles pinning XES extension sets, OCEL object/event qualifiers, PNML net class assumptions, timestamps, identifiers, and conversion policy.
- `pm-irx` — a neutral IR for logs, objects, models, traces, conformance findings, and loss-accounting records.
- `xform-check` — validates a log/model pair against a locked profile and records what survives, changes, or is lost during normalization or conversion.
- `semantic-diff` — diffs such as “same event data, different case interpretation”, “same object graph, different qualifier semantics”, or “same Petri net topology, different conformance outcome”.
- `cargo pm-evidence` — emits `*.pmbundle.zip` with log/model inputs, lockfile, normalized IR, conversion-loss reports, replay configs, and notes.

# What the crate should provide other people

1. **A boring default artifact for process-mining interop bugs**.
2. **Loss-aware locks** so teams can state exactly what semantics they expect to survive conversion or replay.
3. **Small public fixture packs** for discovery, replay, and conformance workflows.
4. **Explainable diffs** between XES-centric, OCEL-centric, and PNML-centric tools.
5. **A bridge from Rust process-mining crates to evidence-grade research and production workflows**.

# Persona / who it’s for

- Researchers building process-mining pipelines in Rust
- Data-platform teams exchanging event logs and models across tools
- Authors of mining, replay, and conformance-checking utilities
- Teams who need reproducible bug reports around event-log conversion and model replay

# Users & user stories

- **Research engineer**: “Show me exactly what meaning was lost when we converted this OCEL to a more traditional event-log view.”
- **Tool maintainer**: “Replay this same bundle in two tools and diff the semantic findings, not just the raw files.”
- **Data engineer**: “Pin our accepted XES extensions and timestamp/identifier policy in CI.”
- **Reviewer**: “Open one compact bundle and understand whether the disagreement is about the log, the model, or the conversion policy.”

# Prior art (and why it’s insufficient)

- XES, OCEL 2.0, and PNML are real standard surfaces with distinct semantics and communities.
- Rust’s `process_mining` crate already provides serious XES, OCEL 2.0, and PNML support.
- Rust4PM shows that the ecosystem is strong enough for larger workflows.
- But Rust still lacks a boring-default crate for **semantic locks + conversion-loss accounting + replayable conformance bundles + cross-tool diffs**.

# Design goals

1. **Boundary-first** — the sharp value is at the seams between logs, objects, models, and tool assumptions.
2. **Loss-accounting** — transformations must say what changed, what was inferred, and what was dropped.
3. **Research-grade but boring** — useful for papers, CI, and production support without becoming a full mining platform.
4. **Deterministic bundles** — evidence artifacts must be reviewable and stable enough for regression testing.
5. **Format-neutral core** — no single standard should dominate the IR or lockfile.

# MVP surface

- Minimal types: `PmLock`, `SemanticProfile`, `PmBundle`, `LossRecord`, `ConformanceDiffFinding`
- Minimal functions:
  - `normalize_log()`
  - `normalize_model()`
  - `check_transform()`
  - `diff_conformance_reports()`
  - `write_bundle()`
- Feature flags:
  - `xes`
  - `ocel2`
  - `pnml`
  - `redaction`

# Compatibility story

- MVP should support XES, OCEL 2.0, and PNML surfaces that already have public specs and Rust substrate.
- The crate should complement `process_mining` and other libraries rather than replace them.
- Discovery/replay adapters can sit on top of a stable IR and lockfile rather than living in the core.
- Conversion policy must remain explicit: same semantics, inferred semantics, and lossy views cannot be flattened together.

# Conformance & fixtures

- Tiny event-log fixtures covering classic XES logs, OCEL object qualifiers, and timestamp edge cases.
- Tiny model fixtures for PNML topologies and conformance/replay expectations.
- Goldens for “same business process, different case notion”, “same log, different extension policy”, and “same model, different replay diagnosis”.
- Loss-accounting tests for log normalization and log↔model handoff.

# Path to boring stability

- Stabilize the lockfile and loss-report schema before adding many discovery algorithms.
- Start with import/normalize/diff/replay artifact seams, not new mining methods.
- Use tiny public fixtures that are semantically revealing and easy to review.
- Keep adapters and algorithm-specific outputs in optional packs.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 3/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 24/30**

# Minimum lovable MVP

A library and CLI that pin a log/model profile across XES, OCEL 2.0, and PNML, run normalization and replay checks, and emit a compact `*.pmbundle.zip` with loss-aware diffs and conformance findings.

# De-risk plan

1. Start with lockfile + normalization + loss accounting before any ambitious replay matrix.
2. Build around tiny public fixtures instead of giant benchmark corpora.
3. Keep algorithm-specific adapters out of the stable core until the artifact format proves itself.
4. Treat “case notion drift” and “object qualifier drift” as first-class explanation problems.

# Non-goals

- Not a new process-mining platform.
- Not a BI dashboard product.
- Not a giant collection of mining algorithms.
- Not a replacement for every existing academic or commercial tool.

# Architecture & API sketch

```rust
pub struct PmLock {
    pub xes_extensions: Vec<String>,
    pub ocel_profile: Option<String>,
    pub pnml_profile: Option<String>,
}

pub fn check_transform(lock: &PmLock, input: &PmArtifact) -> Result<TransformReport>;
pub fn diff_conformance_reports(a: &PmReport, b: &PmReport) -> ConformanceDiff;
```

Bundle draft: `profile.toml`, `log.xes`, `log.ocel.json`, `model.pnml`, `normalized/`, `report.json`, `losses.json`, `diff.json`, `notes.md`.

# Security / safety model

- Treat logs and models as untrusted input.
- Support redaction of identifiers, free-text attributes, and organization-specific labels.
- Record exact profile, extension, and conversion-policy assumptions in every bundle.
- Keep outputs deterministic enough for research review and CI regression tracking.

# Maintenance & governance plan

- Keep the core centered on locks, IR, loss accounting, diffs, and bundle format.
- Version algorithm- or tool-specific adapters separately.
- Publish a small public fixture corpus organized around semantic boundary cases.
- Avoid coupling the workbench to one mining methodology or one research group’s conventions.

# Milestones

## 0.1
- log/model lockfile
- normalization pipeline
- single-bundle report writer

## 0.2
- loss accounting
- conformance diffing
- redaction support

## 1.0
- stable `*.pmbundle.zip`
- public fixture corpus
- documented compatibility policy for supported XES/OCEL/PNML surfaces

# Open questions

- What smallest shared semantic core across XES, OCEL 2.0, and PNML is worth stabilizing?
- Which transformation losses should be first-class schema elements versus human-readable notes?
- How should tool-specific replay verdicts be normalized without pretending they are identical?

# Sources

- XES standard: https://www.xes-standard.org/
- OCEL 2.0 specification overview: https://www.ocel-standard.org/specification/overview/
- PNML reference site: https://www.pnml.org/
- `process_mining` docs: https://docs.rs/process_mining
- `process_mining` crate: https://crates.io/crates/process_mining
- Rust4PM paper: https://publications.rwth-aachen.de/record/1002213/files/1002213.pdf
