---
id: P-0389
title: FDC3 2.2 + Desktop Agent Bridging Interop Kit — intent locks, app-directory diffs, and portable desktop-workflow receipts
status: idea
domains: [desktop, finance, interoperability, workflow, messaging, validation]
last_reviewed: 2026-03-06
evidence:
  - https://fdc3.finos.org/docs/fdc3-standard
  - https://fdc3.finos.org/docs/api/spec
  - https://fdc3.finos.org/docs/agent-bridging/spec
  - https://fdc3.finos.org/docs/app-directory/overview
---

# Problem

FDC3 has become a real interoperability contract for the financial desktop: intents, context data, desktop-agent APIs, app directories, and now desktop-agent bridging. But there is still no boring Rust default for capturing and verifying what actually happened in a multi-app workflow.

The painful failures happen at the seam between:

- **intent declarations and the real app-resolution behavior observed at runtime**,
- **context schemas and app-specific assumptions about identifiers**,
- **local desktop-agent behavior and cross-agent bridging behavior**,
- **app-directory records and what applications actually advertise or accept**,
- and **compliance/debugging artifacts that currently depend on vendor screenshots and proprietary tooling**.

The missing Rust contribution is not another desktop agent. It is an **interop kit** for intent locks, app-directory diffs, bridge-aware receipts, and portable workflow evidence.

# What it provides

- `fdc3.lock` — pins FDC3 version, supported intents, allowed context types, bridging expectations, and app-directory schema assumptions.
- `workflow-receipt` — captures broadcasts, channels, intent resolution, app launches, and bridge crossings in one portable artifact.
- `appd-diff` — explains semantic differences between two app directories or between directory claims and observed runtime behavior.
- `context-lint` — validates whether a given context payload really matches the pinned intent/context contract.
- `cargo fdc3-evidence` — emits `*.fdc3bundle.zip` with receipts, directory snapshots, and findings.

# What the crate should provide other people

1. **A boring receipt for desktop workflow failures**.
2. **Intent and context locks** that make app interop testable.
3. **Bridge-aware diagnostics** for multi-agent deployments.
4. **Explainable app-directory diffs**.
5. **A vendor-neutral artifact for compliance, onboarding, and support.**

# Persona / who it’s for

- Desktop-agent/platform vendors experimenting with Rust components
- Financial application teams embedding Rust runtimes or services
- QA/integration teams testing desktop workflows
- Enterprise platform teams onboarding apps into an FDC3 ecosystem

# Users & user stories

- **QA engineer**: “Show me whether this failure is the app directory, the context payload, the agent, or the bridge.”
- **Platform operator**: “Capture a receipt for a cross-agent workflow without depending on one vendor’s proprietary console.”
- **App team**: “Pin which intents and context variants we actually support.”
- **Compliance reviewer**: “See a reproducible record of what app launched what and why.”

# Prior art (and why it’s insufficient)

- FDC3 standardizes API, context, app directory, and bridging surfaces.
- Existing implementations focus on agents, app containers, or JS-facing app code.

What Rust still lacks is an **evidence-grade coordination layer** for intent locks, app-directory comparison, and cross-agent workflow receipts.

# Design goals

1. **Workflow-first** — capture what happened across apps, not just single API calls.
2. **Directory-aware** — advertised capability and observed behavior must be comparable.
3. **Bridge-explicit** — bridging cannot be hidden inside a generic success/failure log.
4. **Vendor-neutral** — useful even in mixed-agent environments.
5. **Incrementally adoptable** — start with receipts and diffs before deeper runtime bindings.

# MVP surface

- Minimal types: `Fdc3Lock`, `WorkflowReceipt`, `AppDirectorySnapshot`, `ContextFinding`, `BridgeFinding`
- Minimal functions:
  - `capture_workflow()`
  - `diff_app_directories()`
  - `lint_context()`
  - `write_bundle()`
- Feature flags:
  - `intents`
  - `contexts`
  - `app-directory`
  - `bridging`

# Compatibility story

- Can start as a schema/receipt tool even where Rust is not the desktop-agent host language.
- Works with captured event streams, app-directory OpenAPI payloads, or thin runtime adapters.
- Treats agent bridging as an overlay, not the base contract.
- Keeps runtime bindings optional.

# Conformance & fixtures

- Tiny fixtures for ambiguous intent resolution, malformed context payloads, app-directory drift, duplicate app IDs, and bridge-routing disagreements.
- Goldens for “same workflow intent, different directory metadata”.
- Mock agent traces for single-agent and bridged-agent scenarios.
- Public JSON fixtures for context types and app-directory records.

# Path to boring stability

- Stabilize `fdc3.lock`, receipts, and directory diff schema before runtime integrations.
- Start with JSON/OpenAPI artifacts and simulated traces.
- Keep vendor-specific behavior in adapters, not the core schema.
- Make intent/context compatibility findings human-readable.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 2/5
- Adoptability: 2/5
- Sustainability: 3/5
- Differentiation: 4/5
- **Total: 20/30**

# Minimum lovable MVP

A Rust library and CLI that pin FDC3 intent/context assumptions, compare app directories, capture workflow receipts, and emit compact `*.fdc3bundle.zip` artifacts.

# De-risk plan

1. Start with offline artifacts: app directories, context payloads, and recorded traces.
2. Add bridge-aware receipts next.
3. Keep runtime adapters separate from the core schemas.
4. Pilot in QA/compliance workflows before deeper platform integration.

# Non-goals

- Not a desktop agent.
- Not a window/container framework.
- Not a financial symbology service.
- Not a generic desktop automation stack.

# Architecture & API sketch

```rust
pub struct Fdc3Lock {
    pub version: String,
    pub intents: Vec<String>,
    pub context_types: Vec<String>,
    pub bridging_profile: Option<String>,
}

pub fn capture_workflow(input: WorkflowInput) -> Result<WorkflowReceipt>;
pub fn diff_app_directories(a: &AppDirectorySnapshot, b: &AppDirectorySnapshot) -> Vec<BridgeFinding>;
pub fn lint_context(lock: &Fdc3Lock, payload: &serde_json::Value) -> Vec<ContextFinding>;
```

Bundle draft: `fdc3.lock`, `app-directory.json`, `workflow-receipt.json`, `findings.json`, `notes.md`.

# Security / safety model

- Support redaction of identifiers and proprietary app metadata.
- Treat runtime event captures as optional and bounded.
- Distinguish declared from observed capability in every bundle.
- Keep vendor-specific details namespaced and explicit.

# Maintenance & governance plan

- Keep the core about locks, receipts, and diffs.
- Publish a small neutral fixture corpus.
- Version app-directory and bridging overlays carefully.
- Resist drift into building a full agent or app container.

# Milestones

## 0.1
- `fdc3.lock`
- app-directory diffing
- context linting

## 0.2
- workflow receipts
- bridge-aware findings
- public fixture corpus

## 1.0
- stable `*.fdc3bundle.zip`
- documented compatibility policy for intent/context catalogs
- optional runtime adapters

# Open questions

- How much runtime integration is needed before the tool becomes useful?
- Which context-type registries should be bundled versus fetched?
- What is the smallest neutral event model for multi-agent workflows?

# Sources

- FDC3 2.2 standard: https://fdc3.finos.org/docs/fdc3-standard
- API overview: https://fdc3.finos.org/docs/api/spec
- Desktop Agent Bridging: https://fdc3.finos.org/docs/agent-bridging/spec
- App Directory overview: https://fdc3.finos.org/docs/app-directory/overview
