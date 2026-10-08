---
id: P-0331
title: CCSDS CFDP Interop & Evidence Kit — mission-profiled transaction replay, fault-handler diagnostics, and portable space-link file-transfer bundles
status: idea
domains: [space, aerospace, ccsds, cfdp, networking, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://ccsds.org/Pubs/727x0b5e1.pdf
  - https://ccsds.org/publications/bluebooks/
  - https://ccsds.org/publications/sis/
  - https://crates.io/crates/cfdp-rs
  - https://crates.io/crates/cfdp-simplified
  - https://crates.io/crates/spacepackets
---

# Problem

Rust now has early but real CCSDS CFDP substrate, yet mission teams still debug file-transfer failures the hard way. The painful problems are not “can I decode a PDU?” but the **transaction, mission-profile, and fault-handling seam**:

- Class 1/Class 2 assumptions drifting between endpoints,
- closure, EOF, Finished, and report semantics behaving differently than teams expect,
- intermittent links making transactions look flaky without a portable timeline,
- mission-specific entity-ID and filestore conventions being implied rather than pinned,
- and anomaly reports that still move around as partial logs, packet captures, and oral history.

The worthy crate contribution is a **CFDP interop and evidence kit** that makes transactions deterministic, diffable, replayable, and shareable across mission partners.

# What it provides

- `cfdp-ir` — canonical IR for transactions, PDUs, entity IDs, transaction IDs, file metadata, filestore requests, reports, and fault outcomes.
- `mission-profile` — lockfiles pinning Issue 5 assumptions, class/closure policy, entity-ID widths, checksum policy, timer behavior, and local filestore constraints.
- `cfdp-verify` — semantic checks for transaction correctness, state progression, fault-handler behavior, and cross-endpoint profile compatibility.
- `cfdp-replay` — deterministic replay of transaction timelines from PDU captures and implementation logs.
- `cfdp-diff` — explainable diffs: “closure policy changed”, “report cadence diverged”, “fault escalated to abandon”, “EOF/Finished path regressed”.
- `cargo cfdp` — emit `*.cfdpbundle.zip` for mission rehearsal, interop debugging, or vendor/ground-system escalation.

# What the crate should provide other people

1. **A boring default artifact for CFDP incidents** instead of raw packet snippets and ad hoc notes.
2. **Mission-profile pinning** so teams know exactly which transfer semantics were assumed.
3. **Transaction-level replay** for intermittent-link and timing-sensitive bugs.
4. **Semantic diffs** that explain CFDP behavior rather than forcing users to inspect raw PDUs manually.
5. **A neutral evidence layer** across multiple Rust and non-Rust CFDP implementations.

# Persona / who it’s for

- Spaceflight software teams
- Ground-system engineers
- Mission-integration teams
- CCSDS protocol implementers
- Rust developers building mission networking and telemetry infrastructure

# Users & user stories

- **Mission integrator**: “Tell me why this transaction completed on one endpoint and abandoned on the other.”
- **Ground-system engineer**: “Replay the exact PDU timeline that led to this anomaly, with the mission profile pinned.”
- **Implementation author**: “Diff my transaction behavior against a known-good trace without reading every packet manually.”
- **Operations team**: “Redact filenames and mission IDs but preserve enough semantics for outside debugging.”

# Prior art (and why it’s insufficient)

- CCSDS publishes the CFDP Issue 5 Blue Book, and CCSDS keeps an active revisions working group for future changes.
- Rust substrate now exists in `cfdp-rs`, `cfdp-simplified`, and `spacepackets`.
- But there is still no boring-default Rust crate family for **mission-profile lockfiles + transaction replay + semantic diffs + portable interop bundles** around CFDP workflows.

# Design goals

1. **Transaction-first** — the transaction timeline is the unit of meaning.
2. **Mission explicitness** — local conventions must be pinned rather than inferred.
3. **Fault visibility** — reports should make fault-handler semantics obvious.
4. **Transport-neutral** — core should not care whether captures came from lab links, simulated links, or flight-like infrastructure.
5. **Scope discipline** — CFDP evidence first, not a whole mission-control platform.

# MVP surface

- Minimal types: `TransactionTrace`, `MissionProfile`, `PduEvent`, `TransactionReport`
- Minimal functions:
  - `load_trace()`
  - `verify_transaction()`
  - `diff_transactions()`
  - `write_bundle()`
- Feature flags:
  - `issue5`
  - `class2`
  - `redaction`
  - `serde`
  - `filestore`

# Compatibility story

- MVP should target **CCSDS 727.0-B-5** semantics first.
- It should ingest traces from `cfdp-rs`, `cfdp-simplified`, and other implementations through adapters.
- It should intentionally avoid taking ownership of the underlying link, packetization, or mission scheduling stack.
- MVP should not become a complete CCSDS protocol suite.

# Conformance & fixtures

- Synthetic transaction fixtures for Class 1 vs Class 2 behavior, closure/no-closure behavior, fault escalation, cancellation, suspension/resumption, and report timing.
- Golden traces for successful and failing transactions with semantic verdicts.
- Adapter fixtures from real Rust implementation logs and PDU captures.
- Optional comparison packs for future revision-candidate features, kept outside core stability promises.

# Path to boring stability

- First stabilize PDU/transaction IR and verdict vocabulary on synthetic traces.
- Then prove replay quality against at least two implementation outputs.
- Freeze bundle layout only after redaction keeps anomaly reports useful to third parties.
- Keep future-revision experimentation clearly separated from Issue 5 stable support.

# Scorecard

- Impact: 3/5
- Neglectedness: 4/5
- Feasibility: 3/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 4/5
- **Total: 21/30**

# Minimum lovable MVP

A CLI and library that ingest one CFDP transaction trace, validate it against a pinned mission profile, replay the transaction timeline, diff it against a prior known-good trace, and emit a redactable `*.cfdpbundle.zip`.

# De-risk plan

1. Start offline with trace replay only.
2. Keep core narrowly focused on Issue 5 transaction semantics.
3. Treat live transport capture and link simulation as adapters.
4. Use synthetic traces to settle terminology before touching real mission logs.

# Non-goals

- Not a complete spacecraft networking stack.
- Not a mission scheduler or ground-system UI.
- Not an attempt to replace actual CCSDS standards or mission operations procedures.

# Architecture & API sketch

```rust
pub struct TransactionReport {
    pub profile_id: String,
    pub findings: Vec<Finding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn verify_transaction(profile: &MissionProfile, trace: &TransactionTrace) -> TransactionReport;
pub fn diff_transactions(before: &TransactionTrace, after: &TransactionTrace) -> Vec<DiffFinding>;
```

Bundle draft: `profile.toml`, `trace.jsonl`, `pdus.bin`, `verdicts.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Redact mission names, internal file paths, entity identifiers, and private metadata where needed.
- Bound trace sizes and prevent accidental inclusion of unrelated telemetry.
- Preserve transaction ordering and semantic meaning after redaction.
- Record verifier/profile hashes for reproducibility.

# Maintenance & governance plan

- Keep mission-profile data external and versioned.
- Separate stable Issue 5 support from future revision experiments.
- Encourage small redacted anomaly traces as fixtures.
- Keep transport adapters optional and community-owned.

# Milestones

## 0.1
- Transaction IR
- Mission profiles
- Replay and bundle draft

## 0.2
- Semantic diffs
- Redaction support
- Multi-implementation adapters

## 1.0
- Stable `*.cfdpbundle.zip`
- Cross-implementation replay corpus
- CI-ready interop regression workflows

# Open questions

- How much filestore-request semantics belongs in MVP?
- Should report timing and timer policy be modeled as first-class profile data from day one?
- How should future CFDP revision work be staged without destabilizing Issue 5 workflows?

# Sources

- CFDP Blue Book Issue 5: https://ccsds.org/Pubs/727x0b5e1.pdf
- CCSDS Blue Books index: https://ccsds.org/publications/bluebooks/
- CCSDS SIS area / CFDP revisions WG: https://ccsds.org/publications/sis/
- `cfdp-rs`: https://crates.io/crates/cfdp-rs
- `cfdp-simplified`: https://crates.io/crates/cfdp-simplified
- `spacepackets`: https://crates.io/crates/spacepackets
