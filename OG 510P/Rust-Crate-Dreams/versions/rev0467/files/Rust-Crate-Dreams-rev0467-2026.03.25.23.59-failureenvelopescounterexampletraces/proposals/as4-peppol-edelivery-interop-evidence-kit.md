---
id: P-0307
title: AS4 + Peppol eDelivery Interop & Evidence Kit — partner-profiled message exchange, SMP/SML diagnostics, and reproducible onboarding bundles
status: idea
domains: [b2b, e-invoicing, procurement, interoperability, security]
last_reviewed: 2026-03-06
evidence:
  - https://ec.europa.eu/digital-building-blocks/sites/x/voA4O
  - https://docs.peppol.eu/edelivery/as4/specification/
  - https://ec.europa.eu/digital-building-blocks/sites/pages/viewpage.action?pageId=467118022
---

# Problem

Europe-scale B2B exchange increasingly lives at the intersection of **AS4, ebMS3, SMP/SML discovery, Peppol constraints, certificates, and business-document onboarding**. Rust has useful XML, HTTP, TLS, and signing ingredients, and there is even fresh invoice-generation momentum, but it still lacks a boring default for the painful part:

- pinning which AS4/eDelivery/Peppol profile a gateway actually supports,
- debugging discovery failures across SMP/SML and certificate layers,
- reproducing signed/encrypted exchanges without shipping raw business payloads,
- comparing “message accepted” versus “message was deliverable under network rules”.

The worthy crate is not “another XML stack.” It is a **partner-onboarding and incident-evidence workbench**.

# What it provides

- `as4-profile` — encode Peppol/eDelivery partner assumptions, algorithm policy, receipts, reliability, and transport restrictions.
- `edelivery-discovery` — canonical lookup flow for participant identifiers, SMP metadata, endpoint selection, and trust anchors.
- `as4-canon` — canonical IR for SOAP/WS-Security/AS4 metadata, receipts, and delivery state.
- `as4-replay` — deterministic sender/receiver harness for onboarding, migration rehearsal, and regression testing.
- `as4-diff` — semantic diffs for discovery mistakes, certificate/trust mismatches, and profile drift.
- `cargo as4` — emit `*.as4bundle.zip` bundles for partner onboarding, operator support, and certification-adjacent testing.

# What the crate should provide other people

1. **A portable onboarding artifact** that makes trading-partner bring-up reproducible instead of tribal.
2. **Profile pinning** for Peppol/eDelivery behavior so teams can state exactly what they support.
3. **Discovery-aware diagnostics** that explain SMP/SML and endpoint-selection failures, not just transport exceptions.
4. **Evidence bundles with redaction** so invoices and procurement payloads do not have to be mailed around in cleartext.
5. **Adapter surfaces** for existing Rust XML/signature/HTTP crates and external AS4 endpoints, rather than a monolithic gateway rewrite.

# Users & user stories

- **Access point operators**: “Show why this participant lookup succeeded but endpoint delivery still failed.”
- **ERP / procurement integrators**: “Replay the exact signed/encrypted onboarding exchange in CI before partner go-live.”
- **Platform security teams**: “Audit certificate and trust-profile assumptions without re-reading SOAP dumps by hand.”
- **Managed service providers**: “Ship one redactable bundle to a partner instead of screenshots, logs, and XML snippets.”

# Prior art (and why it’s insufficient)

- The EU eDelivery AS4 profile and Peppol AS4 profile are mature and operationally important, which is exactly why silent interpretation drift is expensive.
- Existing stacks outside Rust prove the problem is solvable, but Rust does not yet have a cohesive **discovery + exchange + evidence** workbench.
- New Rust invoice-generation substrate such as `faktura` is useful, but it does not solve network interoperability or supportability.

# Design goals

1. **Discovery-first** — SMP/SML and endpoint metadata are first-class, not side notes.
2. **Profile-aware** — every bundle records the exact profile/algorithm/trust assumptions.
3. **Payload-minimizing** — preserve hashes, schemas, metadata, and verdicts before cleartext business documents.
4. **Operational explainability** — certificate, signature, receipt, and routing errors should produce human-usable verdicts.
5. **Gateway-neutral** — compose with existing access points instead of insisting on one runtime.

# Non-goals

- Not a full procurement platform.
- Not a UBL/CII document-modeling suite.
- Not a hosted Peppol access point service.

# Architecture & API sketch

```rust
pub struct As4BundleReport {
    pub partner_profile: String,
    pub discovery_verdicts: Vec<Verdict>,
    pub exchange_verdicts: Vec<Verdict>,
    pub divergences: Vec<Divergence>,
}

pub trait As4EndpointAdapter {
    fn send(&mut self, msg: CanonicalAs4Message) -> Result<(), Error>;
    fn poll(&mut self) -> Result<Vec<CanonicalAs4Event>, Error>;
}
```

Bundle draft: `profile.toml`, `discovery.json`, `soap-trace.jsonl`, `receipts.json`, `certs.json`, `redaction-map.json`, `verdicts.json`, `notes.md`.

# Security / safety model

- Default to hashed or encrypted payload references, not cleartext business data.
- Treat XML parsing/signature verification as hostile-input surfaces.
- Support separate “internal full-fidelity” and “external redacted” bundle views.
- Keep private keys and raw secrets outside the evidence bundle entirely.

# Maintenance & governance plan

- Track exact eDelivery / Peppol profile versions in bundle metadata.
- Keep canonical IR narrow and additive.
- Publish a fixture-contribution guide for onboarding, rollover, receipt, and discovery cases.
- Maintain adapters for generic HTTP/XML/signature stacks before any gateway-specific integrations.

# Milestones

## 0.1
- Discovery model + partner profile format
- Canonical message/receipt IR
- Redacted evidence writer

## 0.2
- Replay harness
- SMP/SML + receipt diagnostics
- `cargo as4 doctor`

## 1.0
- Stable `*.as4bundle.zip`
- Onboarding scenario packs
- Clear Peppol/eDelivery profile packs

# Open questions

- How much of Peppol-specific validation belongs in core versus add-on packs?
- What is the right boundary between XML canonicalization helpers and AS4 semantics?
- Should simulated SMP/SML services ship in-tree or as companion fixtures?

# Sources

- EU eDelivery AS4 profile 1.16: https://ec.europa.eu/digital-building-blocks/sites/x/voA4O
- Peppol AS4 profile: https://docs.peppol.eu/edelivery/as4/specification/
- EU eDelivery SMP profile: https://ec.europa.eu/digital-building-blocks/sites/pages/viewpage.action?pageId=467118022
- `faktura` crate (invoice-generation substrate, not interop): https://crates.io/crates/faktura
