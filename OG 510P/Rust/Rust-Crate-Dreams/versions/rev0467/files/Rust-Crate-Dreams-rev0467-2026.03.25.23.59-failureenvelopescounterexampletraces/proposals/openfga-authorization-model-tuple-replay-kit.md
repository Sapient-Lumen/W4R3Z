---
id: P-0409
title: OpenFGA Authorization Model + Tuple Replay Kit — model locks, tuple-change receipts, and explainable ReBAC regressions
status: idea
domains: [authorization, security, policy, rebac, testing, operations, evidence]
last_reviewed: 2026-03-06
evidence:
  - https://openfga.dev/docs/fga
  - https://openfga.dev/docs/configuration-language
  - https://openfga.dev/docs/getting-started/immutable-models
  - https://openfga.dev/docs/interacting/contextual-tuples
  - https://openfga.dev/docs/modeling/testing
  - https://openfga.dev/docs/modeling/store-file-format
  - https://docs.rs/openfga-client
  - https://docs.rs/crate/openfga-rs/latest
---

# Problem

Relationship-based authorization is no longer a purely academic or “Google-scale only” concern. OpenFGA has matured into a real ecosystem: it is CNCF-hosted, has a defined configuration language, immutable model versions, contextual tuples, store-file testing, and multiple Rust clients.

Yet the painful failures still happen at the seam between:

- **an authorization model revision and the tuple set people think it was evaluated against**,
- **persisted tuples and ephemeral contextual tuples**,
- **high-level product entitlements and the low-level ReBAC graph actually checked in production**,
- **model tests in `.fga.yaml` and the real-world tuple-change streams that caused an incident**,
- and **debugging stories that still arrive as screenshots from the playground instead of one portable artifact.**

The missing Rust contribution is not another OpenFGA client. It is a **model-and-tuple replay kit** for immutable model locks, tuple-change receipts, explainable decision diffs, and shareable evidence bundles.

# What it provides

- `fga.lock` — pins store/model IDs, configuration-language version, conditions usage, and assumptions about contextual tuples or external data.
- `tuple-receipt` — normalized record of persisted tuples, tuple-change windows, and grouped test fixtures.
- `decision-replay` — replay artifact for `check`, `expand`, `list-objects`, and `list-users` against a pinned model + tuple view.
- `authz-diff` — structured explanation of why a decision changed across model or tuple revisions.
- `cargo fga-evidence` — emits `*.fgabundle.zip` with lockfiles, tuple receipts, replays, and notes.

# What the crate should provide other people

1. **A boring artifact for authorization regressions**.
2. **Pinned model-version receipts** that respect OpenFGA’s immutable model semantics.
3. **A clean separation between persisted tuples and contextual/request-time tuples**.
4. **Replayable authz diffs** that help engineers explain “why did access change?”
5. **A Rust-native test/evidence layer above existing clients and CLI workflows.**

# Persona / who it’s for

- platform and authorization engineers
- product teams adopting ReBAC / entitlement models
- CI and release engineers gating model changes
- incident responders debugging access-control regressions

# Users & user stories

- **Authorization engineer**: “Pin the exact model ID and tuple view used to reproduce this incident.”
- **App team**: “See whether this regression came from tuples, model logic, or contextual inputs.”
- **Reviewer**: “Compare model vN and vN+1 with the same tests and get an explainable diff.”
- **Maintainer**: “Capture a small store fixture instead of asking people to rebuild the whole environment.”

# Prior art (and why it’s insufficient)

- OpenFGA’s docs explicitly emphasize immutable models, contextual tuples, configuration-language semantics, and model testing via `.fga.yaml`.
- Rust already has `openfga-client` and generated SDK crates for API access.
- The official tooling helps define, test, and deploy models.

What Rust still lacks is a **portable evidence layer** for model-version pinning, tuple-change receipts, replayable decisions, and semantic diffs that survive handoff.

# Design goals

1. **Version-honest** — immutable model IDs must be first-class in every artifact.
2. **State-layer explicit** — persisted tuples, contextual tuples, and external condition inputs must never be collapsed together.
3. **Decision-focused** — explain authorization changes in human terms, not raw graph noise.
4. **CLI-compatible** — interoperate with `.fga.yaml` and official workflows rather than compete with them.
5. **Safe by default** — avoid leaking PII or overcapturing application data.

# MVP surface

- Minimal types: `FgaLock`, `TupleReceipt`, `DecisionReplay`, `AuthzDiff`, `FgaBundle`
- Minimal functions:
  - `capture_store_file()`
  - `capture_tuple_changes()`
  - `replay_decision()`
  - `diff_authorization()`
  - `write_bundle()`
- Feature flags:
  - `check`
  - `expand`
  - `list-objects`
  - `conditions`
  - `redaction`

# Compatibility story

- Works above existing Rust OpenFGA clients or captured CLI/store-file artifacts.
- Supports both offline fixtures and live tuple-change windows.
- Keeps contextual tuples and external condition input as explicit overlays.
- Does not require a custom OpenFGA server.

# Conformance & fixtures

- Goldens for immutable-model drift, tuple-change regression, contextual tuple mismatch, and condition-input errors.
- Tiny corpora for `check`/`expand`/`list-objects` replay.
- Fixtures derived from `.fga.yaml` store files.
- Public redacted bundles for CI and bug reports.

# Path to boring stability

- Stabilize the lockfile and replay schema before richer visualizations.
- Start with store-file capture and decision replay.
- Keep authz diffs small, explainable, and model-version aware.
- Resist drift into becoming a new policy engine.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A Rust library and CLI that pin OpenFGA model versions, capture tuple/test fixtures, replay decisions, explain authorization diffs, and emit compact `*.fgabundle.zip` artifacts.

# De-risk plan

1. Start with offline `.fga.yaml` and tuple fixtures.
2. Add live tuple-change capture only after the receipt model is stable.
3. Keep contextual tuples and condition inputs explicit from day one.
4. Pilot in CI/review workflows before promising production incident automation.

# Non-goals

- Not a new authorization engine.
- Not a full visual graph explorer.
- Not a replacement for the OpenFGA CLI or playground.
- Not a generic ABAC/RBAC framework unrelated to OpenFGA semantics.

# Architecture & API sketch

```rust
pub struct FgaLock {
    pub store_id: String,
    pub authorization_model_id: String,
    pub schema_version: String,
    pub feature_overlays: Vec<String>,
}

pub fn capture_store_file(path: &std::path::Path) -> Result<TupleReceipt>;
pub fn replay_decision(lock: &FgaLock, case: &DecisionCase) -> Result<DecisionReplay>;
pub fn diff_authorization(a: &DecisionReplay, b: &DecisionReplay) -> AuthzDiff;
```

Bundle draft: `fga.lock`, `store.fga.yaml`, `tuple-receipt.json`, `decision-replays.jsonl`, `authz-diff.json`, `notes.md`.

# Security / safety model

- Redact or hash user/object identifiers when needed.
- Avoid storing PII in tuple artifacts by default.
- Distinguish persisted store state from per-request contextual data.
- Preserve enough evidence to reproduce the decision boundary.

# Maintenance & governance plan

- Keep the core about locks, replays, and diffs.
- Track OpenFGA language/test-format evolution explicitly.
- Publish a tiny public fixture corpus for CI.
- Resist scope creep into general-purpose policy authoring UX.

# Milestones

## 0.1
- `fga.lock`
- `.fga.yaml` import/export support
- decision replay schema

## 0.2
- tuple-change receipts
- authz diff engine
- redacted public corpus

## 1.0
- stable `*.fgabundle.zip`
- documented compatibility policy for model/store-file evolution
- CI-friendly approval gates

# Open questions

- How much tuple history is enough before receipts become too large for routine code review?
- What is the best stable schema for “why this authorization changed” explanations?
- Which external condition inputs deserve first-class modeling versus opaque attachments?

# Sources

- OpenFGA overview: https://openfga.dev/docs/fga
- Configuration language: https://openfga.dev/docs/configuration-language
- Immutable models: https://openfga.dev/docs/getting-started/immutable-models
- Contextual tuples: https://openfga.dev/docs/interacting/contextual-tuples
- Testing models: https://openfga.dev/docs/modeling/testing
- Store file format: https://openfga.dev/docs/modeling/store-file-format
- `openfga-client`: https://docs.rs/openfga-client
- `openfga-rs`: https://docs.rs/crate/openfga-rs/latest

