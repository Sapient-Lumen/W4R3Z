---
id: P-0412
title: CWL + Workflow Run RO-Crate Conformance & Evidence Kit — portable run receipts, profile locks, and replayable workflow provenance
status: idea
domains: [workflows, reproducibility, science, provenance, metadata, testing, evidence]
last_reviewed: 2026-03-06
evidence:
  - https://www.commonwl.org/v1.2/
  - https://www.commonwl.org/user_guide/
  - https://www.researchobject.org/workflow-run-crate/
  - https://www.researchobject.org/workflow-run-crate/profiles/provenance_run_crate/
  - https://docs.rs/commonwl/latest/commonwl/
  - https://docs.rs/cwl_engine/latest/cwl_engine/
---

# Problem

The Common Workflow Language is no longer hypothetical. CWL v1.2.1 exists, the user guide treats v1.2 as the latest line, Workflow Run RO-Crate has multiple provenance profiles, and Rust now has real CWL object-model and execution crates.

But the painful failures still happen at the seam between:

- **the CWL document people think ran and the preprocessed document that actually ran**,
- **a workflow definition and the exact input object / parameter materialization it was evaluated with**,
- **a runner’s local execution trace and the portable provenance artifact another team can inspect**,
- **declared workflow structure and the files, directories, and intermediate outputs that actually appeared**,
- and **a “reproducible workflow” story that still collapses into screenshots, tarballs, and runner-specific logs.**

The missing Rust contribution is not another CWL runner. It is a **conformance-and-evidence kit** for pinning workflow documents, runner assumptions, input realizations, output manifests, and Workflow Run RO-Crate receipts in one boring bundle.

# What it provides

- `cwl.lock` — pins CWL version, preprocessing assumptions, imported documents, runner identity, container hints, and profile overlays.
- `input-receipt` — normalized record of realized parameters, file/directory materialization, checksums, and default resolution.
- `run-replay` — compact artifact for replaying a run against a pinned document + input view.
- `rocrate-bridge` — deterministic export to Workflow Run / Provenance Run RO-Crate profiles with explicit partial-support receipts.
- `cargo cwl-evidence` — emits `*.cwlbundle.zip` with lockfiles, manifests, traces, and provenance artifacts.

# What the crate should provide other people

1. **A boring handoff artifact for workflow reproducibility**.
2. **Profile-aware provenance export** that does not pretend every runner captured the same granularity.
3. **A stable way to diff runs** when a workflow document, runner version, or input object changed.
4. **A Rust-native bridge between CWL substrate and RO-Crate provenance expectations**.
5. **A compact public bundle format** for CI, publications, and incident/debug handoff.

# Persona / who it’s for

- workflow-engine and platform engineers
- research-software and reproducibility teams
- bioinformatics / scientific pipeline maintainers
- archive/FAIR tooling maintainers

# Users & user stories

- **Workflow maintainer**: “Pin the exact imported/preprocessed CWL document that produced these outputs.”
- **Reviewer**: “See whether this change altered the workflow graph, the realized inputs, or just the execution environment.”
- **Research software engineer**: “Export a Workflow Run RO-Crate artifact without hand-assembling JSON-LD.”
- **Incident responder**: “Capture one compact bundle instead of runner-local logs and a pile of scratch files.”

# Prior art (and why it’s insufficient)

- CWL already defines portable workflow/tool descriptions.
- Workflow Run RO-Crate already defines profiles for execution provenance.
- Rust now has `commonwl` and `cwl_engine` substrate.

What Rust still lacks is a **portable evidence layer** that pins the workflow document, input realization, output manifest, and RO-Crate export assumptions together.

# Design goals

1. **Version-honest** — treat CWL version, imported docs, and preprocessing as first-class.
2. **Runner-explicit** — do not pretend a local runner trace is the same thing as portable provenance.
3. **File-aware** — file and directory materialization must be recorded explicitly.
4. **Profile-aware** — support Workflow Run / Provenance Run RO-Crate without flattening them into one blob.
5. **Publication-safe** — make redaction and partial-public bundles normal.

# MVP surface

- Minimal types: `CwlLock`, `InputReceipt`, `RunReplay`, `RoCrateReceipt`, `CwlBundle`
- Minimal functions:
  - `capture_cwl_document()`
  - `capture_inputs()`
  - `capture_outputs()`
  - `export_rocrate()`
  - `diff_runs()`
  - `write_bundle()`
- Feature flags:
  - `rocrate`
  - `provenance-run`
  - `redaction`
  - `directory-manifests`

# Compatibility story

- Works above existing Rust CWL object-model / execution crates.
- Supports offline evidence capture from completed runs.
- Treats Workflow Run / Provenance Run RO-Crate export as an adapter, not a new provenance ontology.
- Leaves remote scheduler / TES / WES integration for follow-on layers.

# Conformance & fixtures

- Goldens for import/preprocess drift, default-resolution drift, file-manifest mismatch, and partial provenance export.
- Tiny CWL corpora with command-line tools, subworkflows, directories, and optional inputs.
- Round-trip fixtures to Workflow Run RO-Crate and Provenance Run RO-Crate profiles.
- Redacted public bundles for CI and issue reports.

# Path to boring stability

- Stabilize the lockfile and bundle schema before deep runner integration.
- Start with offline capture and deterministic export.
- Keep runner-specific traces as overlays, not the core format.
- Resist drift into becoming a workflow platform.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 25/30**

# Minimum lovable MVP

A Rust library and CLI that pin a CWL document and realized inputs, capture outputs and run metadata, emit Workflow Run RO-Crate-compatible receipts, and package everything into a compact `*.cwlbundle.zip`.

# De-risk plan

1. Start with offline bundles from completed local runs.
2. Export Workflow Run RO-Crate before attempting richer provenance details.
3. Keep runner adapters thin and optional.
4. Pilot with small public workflows and redacted input/output corpora.

# Non-goals

- Not a replacement for `cwltool` or another full CWL runner.
- Not a generic workflow scheduler.
- Not a FAIR-data portal.
- Not a universal provenance ontology.

# Architecture & API sketch

```rust
pub struct CwlLock {
    pub cwl_version: String,
    pub entrypoint: String,
    pub imports: Vec<String>,
    pub runner: String,
    pub profile_overlays: Vec<String>,
}

pub fn capture_cwl_document(path: &std::path::Path) -> Result<CwlLock>;
pub fn capture_inputs(path: &std::path::Path) -> Result<InputReceipt>;
pub fn export_rocrate(bundle: &CwlBundle) -> Result<RoCrateReceipt>;
pub fn diff_runs(a: &RunReplay, b: &RunReplay) -> RunDiff;
```

Bundle draft: `cwl.lock`, `workflow.cwlpack`, `inputs.json`, `input-receipt.json`, `outputs.manifest.json`, `run-replay.json`, `ro-crate-metadata.json`, `notes.md`.

# Security / safety model

- Redact sensitive paths, tokens, and private data-object URLs.
- Support hashing or placeholdering large input files.
- Keep container/runtime credentials out of default bundles.
- Distinguish observed facts from inferred provenance.

# Maintenance & governance plan

- Keep the core focused on locks, manifests, replays, and profile export.
- Track CWL and Workflow Run RO-Crate revisions explicitly.
- Publish a tiny public corpus for regression tests.
- Avoid runner-specific feature creep in the core schema.

# Milestones

## 0.1
- `cwl.lock`
- input/output receipt schema
- offline bundle writer

## 0.2
- Workflow Run RO-Crate export
- diff engine for workflow + inputs + outputs
- redacted public corpus

## 1.0
- stable `*.cwlbundle.zip`
- provenance profile compatibility policy
- CI-friendly approval gates

# Open questions

- How should the bundle represent preprocessed/import-expanded CWL without losing authoring intent?
- Which runner facts belong in the portable core versus optional overlays?
- What is the smallest useful common denominator across Workflow Run and Provenance Run RO-Crate exports?

# Sources

- CWL standards v1.2.1: https://www.commonwl.org/v1.2/
- CWL user guide: https://www.commonwl.org/user_guide/
- Workflow Run RO-Crate working group: https://www.researchobject.org/workflow-run-crate/
- Provenance Run Crate profile: https://www.researchobject.org/workflow-run-crate/profiles/provenance_run_crate/
- `commonwl`: https://docs.rs/commonwl/latest/commonwl/
- `cwl_engine`: https://docs.rs/cwl_engine/latest/cwl_engine/
