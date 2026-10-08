---
id: P-0388
title: DIDComm v2 + Out-of-Band + Mediation Interop & Evidence Kit — profile locks, routing receipts, and redactable message bundles
status: idea
domains: [identity, messaging, security, interoperability, wallets, protocols]
last_reviewed: 2026-03-06
evidence:
  - https://identity.foundation/didcomm-messaging/spec/v2.0/
  - https://didcomm.org/out-of-band/2.0/
  - https://didcomm.org/coordinate-mediation/2.0/
  - https://crates.io/crates/didcomm
---

# Problem

DIDComm gives Rust a real standard surface for secure decentralized messaging, and there is already working Rust substrate. But the operational failures rarely happen at the level of “can I encrypt a message at all?” They happen at the seam between:

- **packed-envelope correctness and delivery/routing assumptions**,
- **Out-of-Band invitation semantics and real device/app onboarding flows**,
- **coordinate-mediation configuration and the actual forwarding path used in production**,
- **attachment handling, return-route behavior, and transport metadata**,
- and **debugging artifacts that are currently too sensitive or too incomplete to share**.

The missing Rust contribution is not another wallet or cloud mediator. It is an **interop/evidence kit** for profile locks, routing receipts, mediator negotiation, and redactable bug bundles.

# What it provides

- `didcomm.profile.lock` — pins DIDComm version/profile, cryptographic envelope expectations, routing assumptions, mediator protocol versions, attachment policy, and return-route behavior.
- `message-ir` — neutral IR for packed messages, unpack metadata, routing hops, attachments, acknowledgements, and redaction markers.
- `routing-receipt` — records which routing and mediation assumptions were actually used.
- `interop-diff` — explains where two parties disagree: keys, DID docs, invitation metadata, mediator state, attachment policy, or return-route expectations.
- `cargo didcomm-evidence` — emits `*.didbundle.zip` with safe manifests, redacted payload digests, protocol findings, and optional transport logs.

# What the crate should provide other people

1. **A boring artifact for DIDComm interop bugs**.
2. **Profile locks** so teams can pin exactly what “supported DIDComm” means.
3. **Routing receipts** that make mediation and forwarding behavior explainable.
4. **Safe redaction modes** that still preserve debugging value.
5. **Fixture-driven conformance** for invitations, mediation, attachments, and envelope handling.

# Persona / who it’s for

- Wallet and agent developers
- SSI platform teams
- Mediator operators
- Security engineers reviewing message-flow assumptions

# Users & user stories

- **Wallet developer**: “Show me whether the failure is in invitation parsing, DID resolution, packing, routing, or mediation negotiation.”
- **Mediator operator**: “Capture the forwarding assumptions and receipts without leaking full message contents.”
- **Integration engineer**: “Pin which attachment types and return-route modes our deployment supports.”
- **Support engineer**: “Share a small, redactable bundle instead of raw encrypted traffic and screenshots.”

# Prior art (and why it’s insufficient)

- DIDComm v2 specifies the messaging model.
- Out-of-Band and Coordinate Mediation define important protocol overlays.
- Rust DIDComm implementations already exist.

What Rust still lacks is a **single coordination layer** for profile locks, routing receipts, interop fixtures, and safe incident artifacts.

# Design goals

1. **Envelope-aware** — cryptographic and routing metadata are first-class.
2. **Profile-first** — “supported DIDComm” must become explicit and testable.
3. **Redaction-native** — evidence must work even when plaintext cannot be shared.
4. **Transport-neutral** — useful across HTTP/WebSocket/mediated delivery.
5. **Operator-usable** — mediation failures must become explainable to non-cryptographers.

# MVP surface

- Minimal types: `DidcommProfileLock`, `PackedMessageRecord`, `RoutingReceipt`, `InteropFinding`, `DidBundle`
- Minimal functions:
  - `capture_exchange()`
  - `diff_profiles()`
  - `record_routing()`
  - `write_bundle()`
- Feature flags:
  - `didcomm`
  - `oob`
  - `mediation`
  - `redaction`

# Compatibility story

- Builds above existing DIDComm Rust libraries instead of replacing them.
- Accepts packed/unpacked metadata from multiple implementations.
- Treats transport capture as optional.
- Keeps mediation, attachments, and invitation semantics explicit in one lockfile.

# Conformance & fixtures

- Tiny fixtures for invitation parsing, mediator grants/denials, attachment-size policy, return-route modes, key-rotation edge cases, and forwarding mismatches.
- Goldens for “same business intent, different envelope/routing shape”.
- Public safe fixtures with digest-only payload evidence.
- Optional interop adapters for mediator implementations.

# Path to boring stability

- Stabilize profile lock and bundle schema before adding many transports.
- Start with invitation/mediation/envelope correctness, not end-user wallet UX.
- Keep redaction mandatory-by-default for shared artifacts.
- Version mediation and profile overlays explicitly.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 3/5
- Adoptability: 3/5
- Sustainability: 3/5
- Differentiation: 4/5
- **Total: 21/30**

# Minimum lovable MVP

A Rust library and CLI that pin DIDComm profile assumptions, capture invitation/mediation/routing evidence, explain interop failures, and emit compact `*.didbundle.zip` artifacts.

# De-risk plan

1. Start with envelope metadata and Out-of-Band fixtures.
2. Add coordinate-mediation receipts next.
3. Keep transports and DID resolution adapters pluggable.
4. Support digest-only payloads from day one.

# Non-goals

- Not a DIDComm agent framework.
- Not a hosted mediator.
- Not a wallet UX toolkit.
- Not a generalized DID resolver stack.

# Architecture & API sketch

```rust
pub struct DidcommProfileLock {
    pub didcomm_version: String,
    pub envelope_profile: String,
    pub mediation_profile: String,
    pub attachment_policy: Vec<String>,
}

pub fn capture_exchange(input: CaptureInput) -> Result<DidBundle>;
pub fn diff_profiles(a: &DidcommProfileLock, b: &DidcommProfileLock) -> Vec<InteropFinding>;
pub fn record_routing(bundle: &mut DidBundle, receipt: RoutingReceipt);
```

Bundle draft: `didcomm.profile.lock`, `messages/manifest.json`, `routing.json`, `findings.json`, `redactions.json`, `notes.md`.

# Security / safety model

- Support digest-only and header-only modes.
- Never require plaintext retention for a useful bundle.
- Record key IDs, mediator metadata, and transport hints explicitly.
- Bound artifact size and attachment inclusion.

# Maintenance & governance plan

- Keep the core about profile locks, receipts, and evidence.
- Version protocol overlays independently if needed.
- Publish a small interop corpus with safe fixtures.
- Resist scope creep into agent hosting and credential workflows.

# Milestones

## 0.1
- profile lock
- envelope metadata capture
- OOB fixture corpus

## 0.2
- mediation receipts
- interop diffing
- redaction modes

## 1.0
- stable `*.didbundle.zip`
- documented profile policy
- optional mediator adapters

# Open questions

- Which DID resolution assumptions belong in MVP versus adapters?
- What is the best digest-only strategy for attachments?
- How much transport metadata is safe and useful by default?

# Sources

- DIDComm Messaging v2.0: https://identity.foundation/didcomm-messaging/spec/v2.0/
- Out Of Band 2.0: https://didcomm.org/out-of-band/2.0/
- Coordinate Mediation 2.0: https://didcomm.org/coordinate-mediation/2.0/
- Rust DIDComm crate: https://crates.io/crates/didcomm
