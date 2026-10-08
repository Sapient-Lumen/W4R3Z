---
id: P-0395
title: GA4GH DRS + TES + WES Portability Evidence Kit — object locks, run receipts, and cloud-genomics handoff bundles
status: idea
domains: [bioinformatics, cloud, workflows, interoperability, reproducibility, data-access]
last_reviewed: 2026-03-06
evidence:
  - https://www.ga4gh.org/product/data-repository-service-drs/
  - https://www.ga4gh.org/product/task-execution-service-tes/
  - https://www.ga4gh.org/product/workflow-execution-service-wes/
  - https://www.ga4gh.org/our-products/implementations/
  - https://github.com/ga4gh/ga4gh-sdk/issues
---

# Problem

GA4GH’s cloud standards now form a real portability stack: DRS standardizes data retrieval, TES standardizes task execution, and WES standardizes workflow execution. GA4GH’s own implementation pages show these standards being used together in real projects and platforms.

But for Rust users the painful gap is still the missing middle between:

- **a DRS object identifier and the concrete access material actually used by a workflow or task runner**,
- **WES-level workflow state and TES-level task receipts**,
- **portability claims across clouds, HPC systems, and institutional environments**,
- **sensitive dataset references, auth context, and reproducibility artifacts that are hard to share safely**,
- and **thin or in-progress Rust substrate where teams still need a stable evidence layer more than a giant all-in-one implementation**.

The missing Rust contribution is not “rebuild the whole GA4GH cloud stack in Rust.” It is a **portability evidence kit** that captures object references, workflow/task receipts, and cross-environment drift in one reproducible artifact.

# What it provides

- `ga4gh.lock` — pins DRS/TES/WES versions, auth assumptions, workflow type, object-resolution policy, and redaction rules.
- `run-ir` — neutral representation of DRS objects, WES runs, TES tasks, state transitions, and associated access material.
- `handoff-receipt` — explicit evidence showing how a workflow moved from registry/input identifiers to concrete execution steps.
- `object-proof` — compact evidence for DRS object identity, checksums, access-method selection, and resolution failures.
- `cargo ga4gh-evidence` — emits `*.ga4ghbundle.zip` with lockfile, run receipts, object proofs, task logs, findings, and notes.

# What the crate should provide other people

1. **A boring handoff artifact** for cross-environment workflow failures.
2. **Pinned versions and policies** for DRS/TES/WES interactions.
3. **Explainable object-resolution receipts** instead of opaque cloud glue.
4. **A reproducibility surface** that survives movement between institutions or platforms.
5. **A narrow evidence layer** that remains useful even while Rust SDK support is still filling in.

# Persona / who it’s for

- Rust teams building genomics workflow tooling, gateways, or orchestration helpers
- Platform engineers integrating with GA4GH cloud APIs
- Research computing groups debugging cross-site portability failures
- Maintainers of thin Rust SDK/CLI layers who need shareable failure artifacts

# Users & user stories

- **Workflow operator**: “Show me whether the failure happened in object resolution, workflow dispatch, or task execution.”
- **Cross-site integrator**: “Pin the exact DRS/TES/WES behavior used in a successful run so another site can reproduce it.”
- **SDK maintainer**: “Capture a bug while Rust support is still incomplete without pretending the SDK layer is finished.”
- **Research partner**: “Share a redacted bundle that proves what ran and what object identities were used without disclosing the whole dataset.”

# Prior art (and why it’s insufficient)

- GA4GH publishes DRS, TES, and WES as formal products with versioning and implementation references.
- The implementations page shows that these APIs are used together in real ecosystems.
- Rust support exists in thin or in-progress form, but that still does not solve portability evidence.

What Rust still lacks is a **single, boring artifact surface** for object locks, workflow/task receipts, and redacted portability debugging.

# Design goals

1. **Object-to-run traceability** — connect identifiers, access methods, and execution steps explicitly.
2. **Cross-environment honesty** — record cloud/HPC/provider differences instead of smoothing them over.
3. **Redaction-first** — bundles must be safe enough to share.
4. **Thin-substrate-friendly** — useful even before rich Rust implementations exist for every endpoint.
5. **Workflow- and task-aware** — WES and TES must stay distinct in the model.

# MVP surface

- Minimal types: `Ga4ghLock`, `RunBundle`, `ObjectProof`, `HandoffReceipt`, `Ga4ghEvidence`
- Minimal functions:
  - `capture_drs_object()`
  - `capture_wes_run()`
  - `capture_tes_task_set()`
  - `write_bundle()`
- Feature flags:
  - `drs`
  - `wes`
  - `tes`
  - `checksums`
  - `redaction`

# Compatibility story

- Works above thin Rust SDK/CLI layers and raw HTTP traces.
- Supports partial bundles when only DRS or only WES/TES evidence is available.
- Keeps workflow-level and task-level receipts distinct while linking them in one IR.
- Can start read-only and remain valuable before broader execution tooling exists.

# Conformance & fixtures

- Tiny fixtures for DRS access-method selection, missing checksums, expired auth, WES run-state drift, and TES retry/failure semantics.
- Goldens for “same workflow, different environment assumptions”.
- Public sample bundles using synthetic object references and toy workflows.
- Redaction fixtures for sensitive identifiers and cloud/provider tokens.

# Path to boring stability

- Stabilize the lockfile, object proof, and handoff receipt schema first.
- Start with capture and explanation rather than orchestration or execution.
- Keep provider-specific behavior in explicit overlays.
- Avoid turning the project into a new workflow runner.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 3/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 5/5
- **Total: 23/30**

# Minimum lovable MVP

A library and CLI that capture DRS object references plus WES/TES run receipts, pin the exact portability assumptions in `ga4gh.lock`, and emit compact `*.ga4ghbundle.zip` artifacts.

# De-risk plan

1. Start read-only with capture from existing endpoints and logs.
2. Keep auth and token handling out of the stable public bundle format.
3. Treat provider quirks as overlay packs.
4. Delay registry/TRS integration until DRS/TES/WES evidence is solid.

# Non-goals

- Not a new workflow engine.
- Not a cloud scheduler.
- Not a giant GA4GH mega-SDK.
- Not a replacement for institutional auth systems.

# Architecture & API sketch

```rust
pub struct Ga4ghLock {
    pub drs_version: String,
    pub wes_version: String,
    pub tes_version: String,
    pub workflow_type: String,
    pub resolution_policy: String,
}

pub fn capture_drs_object(id: &str) -> Result<ObjectProof>;
pub fn capture_wes_run(id: &str) -> Result<RunBundle>;
pub fn capture_tes_task_set(run: &RunBundle) -> Result<Vec<HandoffReceipt>>;
```

Bundle draft: `ga4gh.lock`, `objects.json`, `wes-run.json`, `tes-tasks.json`, `handoff.json`, `findings.json`, `notes.md`.

# Security / safety model

- Default to checksum- and metadata-focused evidence instead of raw dataset export.
- Allow token/access-method scrubbing and identifier hashing.
- Record redactions and omitted access material explicitly.
- Keep bundle contents deterministic and bounded for review and CI.

# Maintenance & governance plan

- Keep the core about object proofs, run receipts, and portability findings.
- Version provider overlays independently.
- Publish a tiny synthetic corpus rather than relying on real protected data.
- Resist scope creep into workflow authoring or cloud orchestration.

# Milestones

## 0.1
- DRS object proof capture
- WES run receipts
- lockfile format

## 0.2
- TES task linkage
- redacted public fixtures
- portability diffs

## 1.0
- stable `*.ga4ghbundle.zip`
- documented compatibility policy for DRS/TES/WES revisions
- stronger Rust adapter story above existing SDK work

# Open questions

- Which DRS access-method details belong in stable bundles versus private overlays?
- How should the crate represent mixed WES/TES implementations that disagree about state boundaries?
- What is the smallest public synthetic corpus that still demonstrates portability bugs credibly?

# Sources

- Data Repository Service (DRS): https://www.ga4gh.org/product/data-repository-service-drs/
- Task Execution Service (TES): https://www.ga4gh.org/product/task-execution-service-tes/
- Workflow Execution Service (WES): https://www.ga4gh.org/product/workflow-execution-service-wes/
- GA4GH implementations page: https://www.ga4gh.org/our-products/implementations/
- GA4GH SDK issues (Rust support in progress): https://github.com/ga4gh/ga4gh-sdk/issues
