---
id: P-0404
title: OpenPGP Discovery + WKD + Autocrypt Policy & Evidence Kit — trust-policy locks, discovery receipts, and mailbox-safe interoperability bundles
status: idea
domains: [security, email, cryptography, interoperability, policy, validation]
last_reviewed: 2026-03-06
evidence:
  - https://www.rfc-editor.org/rfc/rfc9580.html
  - https://docs.rs/sequoia-openpgp/latest/sequoia_openpgp/
  - https://docs.rs/sequoia-net/latest/sequoia_net/
  - https://docs.rs/sequoia-cert-store/latest/sequoia_cert_store/
  - https://docs.rs/sequoia-autocrypt/latest/sequoia_autocrypt/
  - https://docs.autocrypt.org/_/downloads/en/main/pdf/
---

# Problem

OpenPGP in Rust is no longer hypothetical. Sequoia is a serious RFC 9580 implementation, Rust has network/discovery substrate for HKP/WKD/update manifests, there are certificate-store abstractions, and there is working Autocrypt support for headers and setup messages. But real-world failures still cluster around discovery, trust policy, key replacement/update behavior, mailbox-driven heuristics, and support workflows that spill too much sensitive data.

The painful failures still happen at the seam between:

- **an RFC 9580 certificate and the discovery channel that surfaced it**,
- **WKD, local stores, keyservers, update manifests, and mailbox-derived Autocrypt hints**,
- **available key material and the trust policy that should or should not accept it**,
- **device/account setup flows and the exact Autocrypt or discovery evidence that justified them**,
- and **support/debugging workflows that still rely on screenshots, ad hoc CLI output, and raw key dumps.**

The missing Rust contribution is not another OpenPGP crypto library. It is a **policy-and-evidence kit** for discovery receipts, trust-policy locks, safe redaction, and explainable bundle artifacts.

# What it provides

- `openpgp-policy.lock` — pins policy choices for certificate validity, discovery precedence, update behavior, acceptable algorithms, and mailbox/privacy rules.
- `discovery-receipt` — records which certificates were found via local store, WKD, keyserver, update manifests, or Autocrypt-derived inputs.
- `policy-findings` — explains why a candidate cert was accepted, rejected, mistrusted, superseded, or deferred.
- `setup-receipt` — captures Autocrypt setup-message or multi-device transfer evidence without exposing unnecessary private material.
- `cargo openpgp-evidence` — emits `*.openpgpbundle.zip` with policy locks, findings, redacted cert summaries, and notes.

# What the crate should provide other people

1. **A boring artifact for OpenPGP discovery and trust decisions**.
2. **An explicit policy lock** instead of hidden local heuristics.
3. **Safe discovery receipts** for WKD, local stores, and Autocrypt-assisted flows.
4. **Mailbox-safe debugging bundles** that avoid shipping raw private material.
5. **A coordination layer above strong Rust crypto substrate.**

# Persona / who it’s for

- Rust email/security tool authors
- Teams building secure mail or key-discovery workflows
- Operators debugging OpenPGP rollout inside organizations
- Privacy-conscious support engineers reviewing trust failures

# Users & user stories

- **Security engineer**: “Show me which discovery channel produced this cert and why policy accepted or rejected it.”
- **Mail client author**: “Capture the Autocrypt setup or WKD lookup outcome without logging the world.”
- **Operator**: “Pin our trust and update policy so clients behave predictably across environments.”
- **Support engineer**: “Share one small redacted bundle instead of raw keyrings and screenshots.”

# Prior art (and why it’s insufficient)

- `sequoia-openpgp` is a serious RFC 9580 implementation.
- `sequoia-net` covers keyservers, WKD, and update-manifest surfaces.
- `sequoia-cert-store` gives Rust a certificate-store abstraction.
- `sequoia-autocrypt` covers Autocrypt headers and setup messages.

What Rust still lacks is a **boring default coordination artifact** for discovery ordering, trust-policy explanation, safe redaction, and portable support evidence.

# Design goals

1. **Policy-explicit** — trust and discovery choices must be pinned, not guessed.
2. **Discovery-honest** — WKD, keyserver, local, and mailbox hints stay distinguishable.
3. **Redaction-first** — bundles should be safe enough for real support handoff.
4. **Mailbox-aware** — Autocrypt and setup-message flows are first-class but optional.
5. **Crypto-library-neutral above Sequoia** — coordinate strong substrate rather than replace it.

# MVP surface

- Minimal types: `OpenPgpPolicyLock`, `DiscoveryReceipt`, `PolicyFinding`, `SetupReceipt`, `OpenPgpBundle`
- Minimal functions:
  - `discover_certs()`
  - `evaluate_policy()`
  - `capture_setup_receipt()`
  - `write_bundle()`
- Feature flags:
  - `wkd`
  - `keyserver`
  - `updates`
  - `autocrypt`
  - `cert-store`

# Compatibility story

- Starts above Sequoia crates instead of replacing them.
- Can run entirely offline over exported receipts and local stores.
- Treats drafts or ecosystem conventions (like WKD/update-manifest details or Autocrypt behavior) as pinned overlays, not invisible defaults.
- Keeps message encryption/signature UX out of the core crate’s responsibility.

# Conformance & fixtures

- Goldens for WKD advanced/direct fallback, multiple-cert returns, revoked-vs-replacement cases, and mailbox-derived Autocrypt hints.
- Tiny corpora for policy outcomes like “found but not trusted,” “trusted locally but superseded remotely,” and “setup message malformed.”
- Redaction fixtures proving bundles can preserve reasoning without shipping sensitive key material.
- Public mini-corpus of discovery scenarios and policy outcomes.

# Path to boring stability

- Stabilize `openpgp-policy.lock`, discovery receipts, and policy-findings schema first.
- Start with discovery/order/policy explanation before richer mailbox integrations.
- Keep private-key material out of artifacts by default.
- Treat future update drafts or PQ overlays as explicit additions.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 3/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 25/30**

# Minimum lovable MVP

A Rust library and CLI that pin OpenPGP trust/discovery policy, collect discovery receipts from Sequoia-backed sources, explain policy outcomes, and emit compact redacted `*.openpgpbundle.zip` artifacts.

# De-risk plan

1. Start with local store + WKD + explicit policy evaluation.
2. Add Autocrypt setup receipts next.
3. Keep keyserver/update-manifest adapters optional.
4. Pilot in support and rollout workflows before broader mail-client integration.

# Non-goals

- Not a full mail user agent.
- Not a replacement for `sequoia-openpgp`.
- Not a keyserver.
- Not a generic secret-backup product.

# Architecture & API sketch

```rust
pub struct OpenPgpPolicyLock {
    pub discovery_order: Vec<String>,
    pub allowed_algorithms: Vec<String>,
    pub accept_autocrypt_setup: bool,
    pub redact_private_material: bool,
}

pub fn discover_certs(policy: &OpenPgpPolicyLock, userid: &str) -> Result<DiscoveryReceipt>;
pub fn evaluate_policy(policy: &OpenPgpPolicyLock, receipt: &DiscoveryReceipt) -> Vec<PolicyFinding>;
pub fn capture_setup_receipt(msg: &[u8]) -> Result<SetupReceipt>;
```

Bundle draft: `openpgp-policy.lock`, `discovery-receipt.json`, `policy-findings.json`, `setup-receipt.json`, `cert-summary.json`, `notes.md`.

# Security / safety model

- Redact private keys and minimize certificate material by default.
- Preserve just enough metadata to reproduce policy reasoning.
- Separate discovery evidence from trust conclusions.
- Treat remote discovery results as untrusted until policy says otherwise.

# Maintenance & governance plan

- Keep the core about policy locks, receipts, and findings.
- Version draft/convention overlays explicitly.
- Publish a tiny public corpus of non-sensitive discovery cases.
- Resist drift into becoming a full mail stack.

# Milestones

## 0.1
- `openpgp-policy.lock`
- WKD/local-store discovery receipts
- policy findings

## 0.2
- Autocrypt setup receipts
- keyserver/update-manifest adapters
- public fixture corpus

## 1.0
- stable `*.openpgpbundle.zip`
- documented compatibility policy for discovery channels and overlays
- broader store integrations

# Open questions

- What is the right stable shape for discovery precedence when multiple channels disagree?
- How much of Autocrypt behavior belongs in the core versus optional mailbox overlays?
- What is the smallest redacted bundle that still preserves useful support/debug value?

# Sources

- RFC 9580 OpenPGP: https://www.rfc-editor.org/rfc/rfc9580.html
- `sequoia-openpgp`: https://docs.rs/sequoia-openpgp/latest/sequoia_openpgp/
- `sequoia-net`: https://docs.rs/sequoia-net/latest/sequoia_net/
- `sequoia-cert-store`: https://docs.rs/sequoia-cert-store/latest/sequoia_cert_store/
- `sequoia-autocrypt`: https://docs.rs/sequoia-autocrypt/latest/sequoia_autocrypt/
- Autocrypt specification PDF: https://docs.autocrypt.org/_/downloads/en/main/pdf/
