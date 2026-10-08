---
id: P-0374
title: Jupyter Notebook Format + Messaging + Kernel Replay Workbench Kit — notebook/profile locks, protocol traces, and reproducible kernel bug bundles
status: idea
domains: [jupyter, notebooks, data-science, interactive-computing, protocols, testing, developer-tools]
last_reviewed: 2026-03-06
evidence:
  - https://nbformat.readthedocs.io/en/latest/format_description.html
  - https://jupyter-client.readthedocs.io/en/stable/messaging.html
  - https://jupyter-client.readthedocs.io/en/stable/kernels.html
  - https://docs.jupyter.org/en/stable/projects/kernels.html
  - https://crates.io/crates/jupyter-protocol
  - https://crates.io/crates/nbformat
  - https://docs.rs/crate/runtimelib/latest
---

# Problem

Rust now has meaningful Jupyter substrate for notebooks, message types, and kernel interaction, but notebook interoperability bugs still arrive as loose `.ipynb` files, frontend screenshots, and handwavy claims like “the kernel hung” or “widgets stopped working”. The real failures sit at the seam between:

- notebook JSON structure and permissive metadata,
- kernelspec assumptions and startup/transport details,
- wire-protocol messages across shell/iopub/control channels,
- front-end expectations versus kernel replies,
- and replayable behavior versus one-off interactive sessions.

The missing Rust contribution is not yet another Jupyter frontend. It is a **notebook-and-protocol replay workbench** that turns kernel incidents into stable, redactable evidence.

# What it provides

- `notebook-lock` — pins nbformat expectations, kernelspec details, protocol version assumptions, metadata handling policy, and replay mode.
- `jupyter-irx` — a neutral IR for notebook cells, mimebundles, execution events, message envelopes, channel traces, and redaction boundaries.
- `session-pack` — compact reproducible sessions covering execute, complete, inspect, history, comms, interruptions, and restart flows.
- `kernel-bridge` — adapters for Rust kernels/clients and recorded sessions that normalize results into one evidence shape.
- `cargo jupyter-evidence` — emits `*.jupyterbundle.zip` with notebook snapshot, kernelspec, protocol traces, normalized findings, and human notes.

# What the crate should provide other people

1. **A boring default artifact for Jupyter interoperability bugs**.
2. **Notebook/profile locks** instead of implicit frontend/kernel assumptions.
3. **Replayable kernel sessions** for CI and postmortems.
4. **Redactable protocol traces** that preserve causality without leaking notebook contents wholesale.
5. **A bridge between Rust notebook crates and real kernel debugging workflows**.

# Persona / who it’s for

- Rust kernel authors
- Teams building notebook processing or publishing pipelines
- Tooling authors working on notebook conversion, validation, or execution
- Platform engineers embedding Jupyter-style execution into products

# Users & user stories

- **Kernel author**: “Replay the exact request/response trace that broke completion or execution.”
- **Notebook platform engineer**: “Validate that this notebook structure and kernelspec still behave the same after an upgrade.”
- **Pipeline maintainer**: “Package a failing notebook/conversion case without leaking sensitive outputs.”
- **Client implementer**: “Compare what one frontend expects against what the kernel actually emitted.”

# Prior art (and why it’s insufficient)

- Jupyter defines an authoritative messaging protocol and notebook format.
- Kernelspec and kernel-launch behavior are well documented.
- Rust now has crates for notebook parsing, protocol types, and kernel interaction.

What is still missing is a **portable Rust-native workbench** for notebook/profile locks, protocol replay, semantic diffs, and safe evidence bundles.

# Design goals

1. **Protocol-first** — message causality matters more than raw logs.
2. **Notebook-aware** — the notebook structure and the live protocol must be traceable together.
3. **Replayable** — sessions should be runnable against kernels or replay adapters.
4. **Redaction-safe** — preserve timing/order/shape while hiding notebook secrets.
5. **Frontend-neutral** — focus on portable artifacts, not one UI.

# MVP surface

- Minimal types: `NotebookLock`, `KernelSession`, `MessageTrace`, `KernelFinding`, `JupyterBundle`
- Minimal functions:
  - `inspect_notebook()`
  - `capture_session()`
  - `replay_session()`
  - `write_bundle()`
- Feature flags:
  - `nbformat`
  - `zeromq`
  - `recording`
  - `comms`
  - `redaction`

# Compatibility story

- Works with notebooks and kernelspecs produced elsewhere.
- Adapters can sit above existing Rust crates for protocol handling and runtime management.
- The bundle format should remain stable even if transport/runtime integrations evolve.
- The MVP can exclude widgets and rich custom extensions while keeping room for them later.

# Conformance & fixtures

- Tiny notebooks for markdown/raw/code cells, attachments, mimebundles, and metadata edge cases.
- Trace fixtures for execute/complete/inspect/history and kernel interruption flows.
- Goldens for “same notebook, different protocol trace” and “same trace, different notebook metadata assumptions”.
- Redaction tests for cell sources, outputs, and metadata while preserving message ordering and channel shape.

# Path to boring stability

- Stabilize notebook lockfile, trace schema, and replay semantics before broadening transport/features.
- Keep the core centered on evidence and replay, not notebook UX.
- Publish a tiny corpus of public notebook/session fixtures.
- Make channel ordering, timing tolerance, and redaction policy explicit.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 5/5
- **Total: 24/30**

# Minimum lovable MVP

A library and CLI that inspect a notebook, capture or replay a narrow kernel session, and emit a `*.jupyterbundle.zip` containing notebook/profile locks, normalized message traces, and replay findings.

# De-risk plan

1. Start with the core notebook format and message protocol, not widget ecosystems.
2. Keep the first replay surface narrow: execute, complete, interrupt, restart.
3. Treat redaction of notebook cells and outputs as a first-class requirement.
4. Keep adapters thin over existing Rust protocol/runtime crates.

# Non-goals

- Not a Jupyter frontend.
- Not a full notebook execution service.
- Not a widget framework.
- Not a replacement for the canonical Jupyter docs/specs.

# Architecture & API sketch

```rust
pub struct NotebookLock {
    pub nbformat: u32,
    pub protocol_version: String,
    pub kernel_name: String,
}

pub fn capture_session(conn: &ConnectionInfo, plan: &ReplayPlan) -> Result<KernelSession>;
pub fn replay_session(session: &KernelSession, adapter: &mut dyn KernelAdapter) -> Result<ReplayReport>;
```

Bundle draft: `notebook.ipynb.json`, `kernelspec.json`, `lock.toml`, `messages.ndjson`, `report.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Treat notebooks, mimebundles, and protocol messages as untrusted input.
- Support redaction of cell content, outputs, file paths, auth tokens, and metadata.
- Record protocol/runtime versions and transport mode in every bundle.
- Keep bundle generation deterministic enough for CI and issue reports.

# Maintenance & governance plan

- Keep the core focused on locks, traces, replay, and bundle semantics.
- Version transport/runtime adapters independently where practical.
- Publish a small fixture corpus spanning notebook structure and protocol behaviors.
- Avoid drifting into a full notebook platform.

# Milestones

## 0.1
- notebook inspection
- kernelspec/profile lock
- trace capture schema

## 0.2
- replay runner
- semantic diffs
- redaction support

## 1.0
- stable `*.jupyterbundle.zip`
- public notebook/session corpus
- documented compatibility policy

# Open questions

- How much timing information belongs in a stable replay artifact?
- Which protocol extensions deserve first-class MVP support versus adapter notes?
- What is the right default redaction policy for notebook outputs and metadata?

# Sources

- Notebook format description: https://nbformat.readthedocs.io/en/latest/format_description.html
- Messaging in Jupyter: https://jupyter-client.readthedocs.io/en/stable/messaging.html
- Making kernels for Jupyter: https://jupyter-client.readthedocs.io/en/stable/kernels.html
- Jupyter kernels overview: https://docs.jupyter.org/en/stable/projects/kernels.html
- `jupyter-protocol`: https://crates.io/crates/jupyter-protocol
- `nbformat`: https://crates.io/crates/nbformat
- `runtimelib`: https://docs.rs/crate/runtimelib/latest
