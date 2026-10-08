---
id: P-0425
title: A2A Protocol Conformance, Transcript & Capability Kit — agent-card locks, task receipts, and explainable multi-agent traces
status: idea
domains: [ai, agents, protocol, conformance, replay, evidence]
last_reviewed: 2026-03-06
evidence:
  - https://a2aprotocol.ai/
  - https://a2aprotocol.ai/docs/guide/how-to-use-a2a-protocol-validator
  - https://a2aprotocol.ai/docs/guide/a2a-roadmap
  - https://github.com/a2aproject/a2a-tck
  - https://docs.rs/a2a
  - https://docs.rs/a2a-rs-core/latest/a2a_rs_core/
---

# Problem

A2A is moving quickly from “interesting idea” toward a real interoperability surface. That is precisely when a useful Rust contribution should avoid yet another SDK race and instead stabilize the boring coordination layer:

- **what capability set an agent card actually promised at test time**,
- **which task states and streaming events were observed on the wire**,
- **which transport/auth assumptions were in effect**,
- **which failures were protocol violations versus application failures**,
- and **how to reproduce a multi-agent interaction without replaying a full LLM session.**

Rust already has multiple A2A implementations and type crates. The missing contribution is a **conformance/transcript/capability kit** that can pin agent cards, task traces, push-notification assumptions, and compliance findings into one portable artifact.

# What it provides

- `a2a.lock` — pins protocol release, transport/auth assumptions, agent-card digest, and optional capability claims.
- `agent-card.receipt.json` — captures discovery, signatures/digests, interfaces, skills, and declared capabilities.
- `task.transcript.ndjson` — normalized request, event, artifact, and status timeline.
- `compliance.report.json` — maps observed behavior to mandatory/optional capability checks.
- `replay.stub.json` — a redacted replay bundle for protocol-level regression tests.
- `cargo a2a-evidence` — emits `*.a2abundle.zip` with locks, transcripts, capability receipts, and compliance notes.

# What the crate should provide other people

1. **A boring artifact for protocol-level agent debugging**.
2. **Capability and agent-card locks** that make claimed behavior reviewable.
3. **Protocol-aware transcripts** that separate wire behavior from application content.
4. **Reusable compliance receipts** across test tools, inspectors, and CI.
5. **A Rust evidence core** that can survive SDK churn.

# Persona / who it’s for

- agent-platform and infrastructure engineers
- interoperability test authors
- AI framework teams implementing A2A
- security and reliability reviewers of multi-agent deployments

# Users & user stories

- **Protocol implementer**: “Show me whether my server failed capability negotiation, task lifecycle semantics, or streaming behavior.”
- **Infra engineer**: “Package one agent-card snapshot plus task transcript to reproduce an issue without shipping prompts or private model output.”
- **QA team**: “Compare two agent builds and see which A2A capabilities changed.”
- **Integrator**: “Prove that a failure was app-level rather than protocol-level.”

# Prior art (and why it’s insufficient)

- Official A2A documentation, validator tooling, and TCK work already exist.
- Rust has live A2A protocol/type/client/server crates.
- Inspectors and SDKs can exercise real agents.

What Rust still lacks is a **portable transcript-and-capability artifact layer** that other tools can reuse regardless of which SDK or framework generated the traffic.

# Design goals

1. **Capability-explicit** — agent-card claims must be pinned, not inferred later.
2. **Transcript-first** — protocol timelines should be replayable without private model state.
3. **Compliance-aware** — distinguish mandatory failures from unsupported optional features.
4. **Redaction-safe** — preserve protocol evidence while allowing content minimization.
5. **SDK-neutral** — the core schema should outlast individual framework fashions.

# MVP surface

- Minimal types: `A2ALock`, `AgentCardReceipt`, `TaskTranscript`, `ComplianceReport`, `ReplayStub`, `A2ABundle`
- Minimal functions:
  - `fetch_agent_card()`
  - `capture_transcript()`
  - `classify_compliance()`
  - `diff_capabilities()`
  - `write_bundle()`
- Feature flags:
  - `http`
  - `sse`
  - `push`
  - `auth`
  - `redaction`

# Compatibility story

- Treats the official protocol/TCK/validator ecosystem as the normative and ecosystem overlay layers to pin explicitly.
- Supports capture from existing SDKs and proxies.
- Distinguishes protocol receipts from app-level content and model semantics.
- Keeps agent frameworks and orchestration products out of scope.

# Conformance & fixtures

- Tiny corpora for agent discovery, task submission, streaming updates, artifact emission, push notification config, and cancellation/error handling.
- Goldens for mandatory-vs-optional capability checks.
- Replay stubs that retain wire shape while redacting payload content.
- Capability-diff fixtures for agent-card evolution.

# Path to boring stability

- Stabilize `a2a.lock`, `agent-card.receipt.json`, and transcript schema before broad transport work.
- Start with HTTP/SSE capture and offline classification.
- Make content redaction a first-class feature.
- Avoid becoming another agent runtime or chat UI.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 5/5
- **Total: 25/30**

# Minimum lovable MVP

A Rust library and CLI that fetch one agent card, capture one task transcript, classify a small conformance subset, and write a redaction-safe A2A evidence bundle.

# De-risk plan

1. Start with protocol-level receipts, not full semantic replay.
2. Focus first on capability locking and transcript normalization.
3. Reuse official validator/TCK vocabulary where possible.
4. Keep transports modular.

# Non-goals

- Not another full A2A SDK.
- Not a general agent runtime.
- Not a prompt-recording system.
- Not a model-evaluation harness.

# Architecture & API sketch

```rust
pub struct A2ALock {
    pub protocol_release: String,
    pub transport: String,
    pub agent_card_digest: String,
    pub auth_profile: Option<String>,
}

pub fn fetch_agent_card(base_url: &str) -> Result<AgentCardReceipt>;
pub fn capture_transcript(session: &SessionCapture) -> Result<TaskTranscript>;
pub fn classify_compliance(card: &AgentCardReceipt, transcript: &TaskTranscript) -> ComplianceReport;
pub fn diff_capabilities(old: &AgentCardReceipt, new: &AgentCardReceipt) -> CapabilityDiff;
pub fn write_bundle(bundle: &A2ABundle, out: &std::path::Path) -> Result<()>;
```

Bundle draft: `a2a.lock`, `agent-card.receipt.json`, `task.transcript.ndjson`, `compliance.report.json`, `replay.stub.json`, `notes.md`.

# Security / safety model

- Support redaction of prompts, file content, and application payloads while preserving envelope structure.
- Treat auth and webhook details as sensitive and separably redactable.
- Distinguish protocol evidence from model-evaluation claims.
- Hash referenced artifacts so traces remain useful after content minimization.

# Maintenance & governance plan

- Track protocol release candidates and stable releases explicitly.
- Keep compliance vocab aligned with official validator/TCK language where feasible.
- Publish a tiny public transcript corpus focused on protocol boundaries.
- Avoid coupling the core schema to one vendor SDK.

# Milestones

## 0.1
- `a2a.lock`
- agent-card receipt
- task transcript capture

## 0.2
- compliance classifier
- capability diff
- redacted replay stubs

## 1.0
- stable `*.a2abundle.zip`
- CI-friendly protocol regression gates
- importers for multiple Rust A2A implementations

# Open questions

- What is the smallest transcript schema that still supports useful conformance classification?
- How should optional capabilities and transport fallbacks be expressed in the lockfile?
- Which artifact and push-notification fields should be preserved verbatim versus summarized?

# Sources

- A2A protocol home: https://a2aprotocol.ai/
- Official validator guide: https://a2aprotocol.ai/docs/guide/how-to-use-a2a-protocol-validator
- A2A roadmap / validation notes: https://a2aprotocol.ai/docs/guide/a2a-roadmap
- Official A2A TCK repository: https://github.com/a2aproject/a2a-tck
- Rust A2A crate docs: https://docs.rs/a2a
- Rust A2A core types aligned to proto spec: https://docs.rs/a2a-rs-core/latest/a2a_rs_core/
