---
id: P-0301
title: EBICS Banking Interop & Evidence Kit — bank-profile pinning, signature-aware transfers, and reproducible payment exchange bundles
status: idea
domains: [banking, payments, security, interoperability, compliance]
last_reviewed: 2026-03-06
evidence:
  - https://www.ebics.org/
  - https://docs.axway.com/bundle/EBICSClient_11_allOS_en_HTML5/page/the_ebics_standard.html
  - https://developer.gs.com/docs/services/transaction-banking/ebicsconnectivity/
---

# Problem

EBICS remains an operationally important corporate-to-bank communication standard in Europe, but the Rust ecosystem has no credible default crate stack for **profile-aware EBICS interoperability**. The missing pain-killer is not merely XML signing or HTTP transport; it is the combination of:

- bank-specific capability/profile differences,
- signature and order-type handling,
- test/replay of upload/download flows,
- reproducible diagnostics when one bank accepts a transfer and another rejects it,
- safe bug bundles for payment operations and bank integration teams.

EBICS is exactly the kind of protocol where “mostly works” is insufficient and where incident handling needs **shareable, replayable evidence**.

# What it provides

- `ebics-profile` — declarative bank/customer profile layer for capabilities, versions, order types, and certificate expectations.
- `ebics-canon` — canonical IR for requests, responses, signatures, order metadata, and transfer lifecycle events.
- `ebics-replay` — deterministic replay for upload/download/order-management flows.
- `ebics-fixtures` — simulated bank endpoints, golden exchanges, and negative test corpora.
- `ebics-diff` — semantic diffs for profile/certificate/order mismatches.
- `cargo ebics` — build `*.ebicsbundle.zip` artifacts for certification and incident exchange.

# Users & user stories

- **Treasury / ERP integration teams**: “Why does bank A reject our order while bank B accepts the same business flow?”
- **Fintech / banking API teams**: “Pin an exact bank profile and regression-test it in CI.”
- **Rust library authors**: “Compare signature/certificate behavior across fixtures and simulated banks.”
- **Ops / support teams**: “Send one redacted bundle with request/response timeline, signatures, and verdicts.”

# Prior art (and why it’s insufficient)

- Public EBICS information and vendor docs explain the protocol and its operational use, but not a Rust-native crate architecture.
- Existing open-source operational stacks are sparse and skew toward other languages, often embedded in broader commercial products.
- Rust has good crypto/XML/HTTP primitives, but no cohesive EBICS evidence stack.

# Design goals

1. **Profile pinning** — bank-specific differences must be explicit and versioned.
2. **Signature-aware diagnostics** — explain certificate, signature, and order-type failures clearly.
3. **Safe reproducibility** — payment artifacts need structured redaction and tokenization by default.
4. **Simulation-first onboarding** — allow teams to test against bank-like fixtures before real onboarding.
5. **Composable building blocks** — keep transport, crypto, profile, and evidence layers separable.

# Non-goals

- Not a full treasury workstation.
- Not an ERP.
- Not a replacement for every bank portal or payment workflow UI.

# Architecture & API sketch

```rust
pub struct EbicsReport {
    pub bank_profile: String,
    pub exchange_timeline: Vec<Event>,
    pub verdicts: Vec<Verdict>,
}

pub fn canonicalize_exchange(trace: &[u8]) -> Result<CanonicalExchange, Error>;
pub fn replay(bundle: &EbicsBundle, endpoint: &mut dyn EbicsEndpoint) -> Result<EbicsReport, Error>;
pub fn diff_profiles(a: &BankProfile, b: &BankProfile) -> ProfileDiff;
```

Bundle draft: `profile.toml`, `timeline.jsonl`, `signatures.json`, `orders.json`, `redaction-map.json`, `verdicts.json`, `notes.md`.

# Security / safety model

- Default redaction for account identifiers, partner IDs, transaction references, and payload bodies.
- Separate raw secrets and key material from issue bundles entirely.
- Treat XML/signature parsing and compression as hostile-input territory.

# Maintenance & governance plan

- Maintain a stable, additive canonical exchange IR.
- Keep country/bank profile packs out of the core crate where possible.
- Require recorded provenance for every fixture and simulated-bank behavior profile.

# Milestones

## 0.1
- Canonical exchange IR
- Basic simulated endpoint
- Redaction/tokenization support

## 0.2
- Bank profile packs
- Signature/certificate diagnostics
- `cargo ebics replay`

## 1.0
- Stable `*.ebicsbundle.zip`
- CI-ready onboarding packs
- Reusable incident bundles for bank/corporate debugging

# Open questions

- Which EBICS versions and order types should define the MVP boundary?
- How much XML signature/certificate handling should be delegated to companion crates?
- Can a neutral simulated-bank suite cover enough real onboarding pain to matter?

# Sources

- EBICS overview: https://www.ebics.org/
- Axway EBICS standard overview: https://docs.axway.com/bundle/EBICSClient_11_allOS_en_HTML5/page/the_ebics_standard.html
- Goldman Sachs developer overview: https://developer.gs.com/docs/services/transaction-banking/ebicsconnectivity/
- Example open-source operational stack (non-Rust): https://github.com/railslove/ebicsbox
