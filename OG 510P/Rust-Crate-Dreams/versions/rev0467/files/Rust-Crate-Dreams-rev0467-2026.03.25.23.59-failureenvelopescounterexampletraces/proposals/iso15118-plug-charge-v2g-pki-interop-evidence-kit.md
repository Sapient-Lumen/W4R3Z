---
id: P-0407
title: ISO 15118 Plug & Charge + V2G PKI Interop & Evidence Kit — session locks, certificate-chain receipts, and explainable EV↔EVSE failures
status: idea
domains: [ev, charging, interoperability, security, pki, mobility, evidence]
last_reviewed: 2026-03-06
evidence:
  - https://www.charin.global/technology/iso15118
  - https://www.charin.global/technology/plug-charge
  - https://www.charin.global/technology/knowledge-base
  - https://github.com/EcoG-io/iso15118
  - https://github.com/tux-evse/iso15118-encoders-rs
---

# Problem

EV charging interoperability is increasingly constrained by a seam that is **much nastier than “can the socket talk?”**. ISO 15118 now sits at the center of Plug & Charge, certificate-based onboarding, and bidirectional/V2G expectations; CharIN explicitly frames ISO 15118 as the communication backbone for interoperable charging and highlights Plug & Charge plus ISO 15118-20-backed V2G as strategic ecosystem surfaces.

Rust can already reach pieces of this world through open implementations and lower-level bindings, but the painful failures still happen at the seam between:

- **session negotiation and the exact certificate / PKI assumptions in force**,
- **fielded vehicle / charger behavior and the intended profile or implementation guide**,
- **service discovery / transport / EXI message semantics and the human story support engineers tell about them**,
- **Plug & Charge policy expectations and real-world certificate-chain state**, 
- and **interoperability reports that still arrive as packet captures, screenshots, and vendor lore instead of one boring artifact.**

The missing Rust contribution is not “yet another full ISO 15118 stack.” It is an **evidence-grade coordination crate** for session locks, certificate-chain receipts, profile overlays, and replayable interop bundles.

# What it provides

- `evcc-secc.lock` — pins ISO 15118 family target, profile overlays, PKI assumptions, transport expectations, and selected feature flags (Plug & Charge, V2G, AC/DC scope).
- `session-receipt` — normalized artifact for SDP/TLS/EXI/session setup metadata, role, negotiated options, and message flow anchors.
- `pki-receipt` — certificate-chain, trust-anchor, contract-certificate, provisioning, and validation findings without dumping raw secrets.
- `interop-findings` — structured explanations for profile mismatch, chain failure, unsupported message paths, and renegotiation / state-machine drift.
- `cargo iso15118-evidence` — emits `*.evchargebundle.zip` with locks, redacted traces, receipts, and notes.

# What the crate should provide other people

1. **A boring artifact for EV↔EVSE interoperability incidents**.
2. **Profile-aware session locks** that pin what the parties thought they were doing.
3. **Certificate-chain receipts** instead of vague “PnC failed” debugging.
4. **Replayable, redactable evidence** for vendors, labs, and integrators.
5. **A coordination layer above existing implementations**, not a rewrite of them.

# Persona / who it’s for

- EVSE software teams
- vehicle-side protocol implementers
- lab / certification / interoperability engineers
- fleet operators and support engineers debugging Plug & Charge failures

# Users & user stories

- **Charging-platform engineer**: “Tell me whether this failure is trust-chain, message-sequence, or profile mismatch.”
- **Vehicle implementer**: “Pin the exact assumptions under which this charger was considered compatible.”
- **Interoperability lab**: “Ship a redacted bundle to the other vendor without sending the whole private PKI setup.”
- **Program manager**: “Compare two firmware revisions and see whether the interop breakage was normative drift or a field quirk.”

# Prior art (and why it’s insufficient)

- CharIN’s public materials and implementation guidance make clear that Plug & Charge and V2G are no longer side curiosities; they are ecosystem-defining surfaces.
- Open implementations such as EcoG’s ISO 15118 project show there is real substrate and real operational complexity already in the wild.
- Rust-side work such as `iso15118-encoders-rs` and network bindings demonstrates that some protocol substrate exists.

What Rust still lacks is a **lockfile + receipt + replay artifact** that can sit above stacks, field traces, and implementation guides.

# Design goals

1. **Profile-explicit** — base standard versus implementation-guide overlays must be pinned separately.
2. **PKI-honest** — trust anchors, contract certificates, and validation outcomes must be first-class evidence.
3. **Transport-separated** — discovery, TLS, and EXI/message semantics must remain distinguishable.
4. **Redaction-first** — useful debugging without irresponsible key or certificate leakage.
5. **Ops-credible** — bundles should help actual incident handling, not only demos.

# MVP surface

- Minimal types: `EvChargeLock`, `SessionReceipt`, `PkiReceipt`, `InteropFinding`, `EvChargeBundle`
- Minimal functions:
  - `capture_session()`
  - `capture_pki_state()`
  - `evaluate_profile()`
  - `write_bundle()`
- Feature flags:
  - `iso15118-2`
  - `iso15118-20`
  - `plug-charge`
  - `v2g`
  - `redaction`

# Compatibility story

- Works above existing protocol implementations and packet/message capture paths.
- Treats profile guides and regional/operator overlays as explicit metadata, not invisible assumptions.
- Supports offline evaluation from captured traces and certificate material summaries.
- Keeps private keys and full sensitive payloads out of the stable artifact format.

# Conformance & fixtures

- Goldens for contract-certificate failure, trust-anchor mismatch, unsupported feature negotiation, and state-machine divergence.
- Mini corpora for AC/DC and Plug & Charge vs non-PnC flows.
- Fixtures for “same nominal feature, different PKI/profile assumptions”.
- Public redacted bundles usable in CI and issue reports.

# Path to boring stability

- Stabilize the lockfile and receipt schema before deep live adapters.
- Start with offline evidence capture and evaluation.
- Keep base standard, implementation-guide overlays, and live field quirks separate.
- Resist drift into becoming a full EV charging platform.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 3/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A Rust library and CLI that pin ISO 15118 session assumptions, capture redacted session + PKI receipts, classify common Plug & Charge / V2G failures, and emit compact `*.evchargebundle.zip` artifacts.

# De-risk plan

1. Start with receipt schemas and offline trace evaluation.
2. Add adapters for one open implementation and one capture format next.
3. Keep certificate material summarized/redacted by default.
4. Pilot with lab-style fixtures before promising production “doctor” automation.

# Non-goals

- Not a full EVCC or SECC implementation.
- Not a billing or CSMS backend.
- Not a certificate authority.
- Not a replacement for standards bodies or certification programs.

# Architecture & API sketch

```rust
pub struct EvChargeLock {
    pub iso15118_family: String,
    pub profile_overlays: Vec<String>,
    pub pki_profile: String,
    pub transport_expectations: Vec<String>,
}

pub fn capture_session(input: SessionCaptureInput) -> Result<SessionReceipt>;
pub fn capture_pki_state(input: PkiCaptureInput) -> Result<PkiReceipt>;
pub fn evaluate_profile(lock: &EvChargeLock, receipt: &SessionReceipt) -> Vec<InteropFinding>;
```

Bundle draft: `evcc-secc.lock`, `session-receipt.json`, `pki-receipt.json`, `findings.json`, `notes.md`.

# Security / safety model

- Default to hashing or summarizing sensitive certificate/key material.
- Distinguish normative validation failure from implementation-specific policy failure.
- Preserve enough chain/session data for reproducibility.
- Treat bundles as potentially infrastructure-sensitive operational artifacts.

# Maintenance & governance plan

- Keep the core about locks, receipts, and findings.
- Version stable targets and future overlays separately.
- Publish a tiny redacted fixture corpus.
- Resist scope creep into complete charge-session orchestration.

# Milestones

## 0.1
- `evcc-secc.lock`
- session receipt schema
- PKI receipt schema

## 0.2
- profile evaluation
- redacted bundle format
- public fixture corpus

## 1.0
- stable `*.evchargebundle.zip`
- documented compatibility policy for profile overlays and PKI assumptions
- CI-friendly regression artifacts

# Open questions

- Which session trace shape is smallest while still being diagnostically useful?
- How should regional/operator overlays be represented without hard-coding vendor politics into the core model?
- Which certificate-chain details can be safely summarized while preserving reproducibility?

# Sources

- CharIN ISO 15118 overview: https://www.charin.global/technology/iso15118
- CharIN Plug & Charge overview: https://www.charin.global/technology/plug-charge
- CharIN knowledge base / implementation guidance: https://www.charin.global/technology/knowledge-base
- EcoG open implementation: https://github.com/EcoG-io/iso15118
- Rust encoder bindings: https://github.com/tux-evse/iso15118-encoders-rs

