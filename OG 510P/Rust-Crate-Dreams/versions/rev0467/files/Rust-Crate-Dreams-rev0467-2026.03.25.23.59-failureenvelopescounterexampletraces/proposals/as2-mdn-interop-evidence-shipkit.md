---
id: P-0294
title: AS2 + MDN Interop & Evidence ShipKit — signed/encrypted EDI transport with replayable receipts and partner profiles
status: idea
domains: [edi, supply-chain, security, messaging, enterprise]
last_reviewed: 2026-03-06
evidence:
  - https://www.rfc-editor.org/rfc/rfc4130.html
  - https://datatracker.ietf.org/doc/html/rfc5402
  - https://datatracker.ietf.org/doc/html/rfc3798
---

# Problem

AS2 is still operationally critical in B2B supply chains, but Rust has no widely recognized **AS2 interoperability toolkit**. The protocol surface is awkward because it composes HTTP(S), MIME/S/MIME, certificates, receipts (MDNs), optional compression, partner-specific quirks, and long-tail operational expectations.

The worthy crate is not “just parse AS2 headers.” It is a **replayable partner-integration shipkit**.

# What it provides

- `as2-core` — strict/lenient parsing for AS2 headers, MIC computation, MDN validation, and partner profiles.
- `as2-evidence` — bundle schema for redacted request/response/MDN exchanges.
- `as2-replay` — deterministic sender/receiver harness for partner certification and incident repro.
- `as2-smime-adapters` — composable S/MIME helpers over existing Rust crypto/mail crates.
- `cargo as2` — `doctor`, `send-test`, `verify-mdn`, `bundle`, and `diff` commands.

# Users & user stories

- **B2B platform teams**: “Prove our receiver handled sync and async MDNs correctly.”
- **ERP / logistics integrators**: “Compare our partner profile with a known-good exchange before a costly cutover.”
- **Security / compliance teams**: “Share a redacted evidence bundle without leaking payload business data.”
- **Managed EDI vendors**: “Regression-test certificate rollover, MIC rules, compression, and MDN edge cases.”

# Prior art (and why it’s insufficient)

- Java ecosystems such as `phase2` show that AS2 can be made production-grade, but that maturity has not been translated into a cohesive Rust crate stack.
- Existing Rust MIME, CMS, TLS, and HTTP crates are useful ingredients, not an opinionated AS2 operational toolkit.
- The current AS2 modernization draft underlines how many conformance details are easy to get subtly wrong.

# Design goals

1. **Partner-profile driven** — encode trading-partner quirks explicitly.
2. **Receipt correctness first** — MDN verification must be explainable and deterministic.
3. **Crypto boundary hygiene** — keep S/MIME plumbing replaceable.
4. **Redaction-first artifacts** — payload bodies are optional, receipts and metadata are primary.
5. **Operational doctor tooling** — certificate expiry, MIC mismatch, async MDN callback failures, and compression mistakes should produce actionable diagnostics.

# Non-goals

- Not a full EDI mapping engine for X12/EDIFACT payload semantics.
- Not a generic mail stack replacement.
- Not a hosted B2B network.

# Architecture & API sketch

```rust
pub struct PartnerProfile {
    pub as2_id: String,
    pub mdn_mode: MdnMode,
    pub signing: SigningPolicy,
    pub encryption: EncryptionPolicy,
    pub compression: CompressionPolicy,
}

pub struct ExchangeVerdict {
    pub mic: Option<String>,
    pub mdn_verified: bool,
    pub warnings: Vec<String>,
}

pub fn verify_exchange(profile: &PartnerProfile, trace: &As2Trace) -> ExchangeVerdict;
```

Bundle draft: `profile.toml`, `http.json`, `mime.json`, `mdn.json`, `certs/`, `verdicts.json`, `notes.md`.

# Security / safety model

- Default to storing hashes, sizes, and MIME metadata instead of cleartext payloads.
- Separate partner identity material from message bodies.
- Mark legacy algorithms and SHA-1-era interop as “legacy-only” with loud warnings.
- Keep async MDN callback testing sandboxed and time-bounded.

# Maintenance & governance plan

- Publish a small set of canonical partner profiles as examples.
- Keep crypto adapters decoupled from the protocol core.
- Maintain corpora for sync MDN, async MDN, compression, and certificate rollover cases.
- Treat RFC updates / modernization drafts as tracked compatibility inputs, not silent behavior changes.

# Milestones

## 0.1
- Header/parser core
- MIC computation + MDN verification
- Redacted bundle format

## 0.2
- Replay harness for sync/async MDNs
- Compression and certificate rollover cases
- `cargo as2 doctor`

## 1.0
- Stable `*.as2bundle.zip`
- Partner profile format
- Reference fixture corpus for common interop traps

# Open questions

- Which Rust crypto stack gives the cleanest S/MIME integration story?
- How much leniency should the verifier allow for legacy partner behavior?
- Should partner-profile rules be data-only or allow pluggable code hooks?

# Sources

- RFC 4130 (AS2): https://www.rfc-editor.org/rfc/rfc4130.html
- RFC 5402 (AS compression): https://datatracker.ietf.org/doc/html/rfc5402
- RFC 3798 (MDN): https://datatracker.ietf.org/doc/html/rfc3798
- AS2 modernization draft: https://drummondgroup.github.io/draft-petta-rfc4130bis/draft-petta-rfc4130bis.html
- phax/phase2 reference implementation: https://github.com/phax/phase2
