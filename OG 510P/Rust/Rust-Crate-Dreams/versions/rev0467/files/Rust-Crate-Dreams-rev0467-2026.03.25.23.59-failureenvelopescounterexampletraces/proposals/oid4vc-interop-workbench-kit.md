---
id: P-0195
title: OID4VC Interop Workbench — OID4VP/OID4VCI + Presentation Exchange profiles with conformance bundles
status: idea
domains: [identity, security, oauth, interop, mobile, web]
last_reviewed: 2026-03-05
evidence:
  - https://openid.net/specs/openid-4-verifiable-presentations-1_0.html
  - https://openid.net/specs/openid-4-verifiable-credential-issuance-1_0.html
  - https://identity.foundation/presentation-exchange/spec/v2.0.0/
  - https://crates.io/crates/dif-presentation-exchange
  - https://github.com/spruceid/openid4vp
needs:
  - Interoperability kits for “VC flows” that are *profile-driven* and testable; today teams hand-roll glue and regressions are hard to reproduce.
  - Portable transcripts that can be shared for debugging without leaking PII.
risks:
  - Specs evolve; the crate must model profiles and versioning rather than hard-coding one flow.
  - Identity deployments are compliance-heavy; maintainers need strong security posture and clear threat model.
---

# Problem

OpenID4VP (presentations) and OpenID4VCI (issuance) are increasingly used to move verifiable credentials through OAuth-shaped flows, and Presentation Exchange is commonly used as a query language / presentation definition layer. In practice:

- implementations differ by profile (redirect vs device APIs, credential formats, holder binding)
- relying parties and wallets struggle to reproduce bugs (“works with vendor A, fails with B”)
- transcripts contain sensitive data, so teams can’t easily share debug artifacts

Rust has early implementations, but lacks an *interop-first* workbench that standardizes:
- profile declarations
- conformance test vectors
- redacted incident bundles

# Users & user stories

- **Wallet developers**: “I need to run conformance suites and quickly diagnose why a verifier rejects my VP token.”
- **Verifiers/Relying parties**: “I need to validate that my presentation definition requests are interoperable across wallets.”
- **Auditors**: “I need an evidence trail of what was requested, what was presented, and what checks were applied.”

# Prior art (and why it’s insufficient)

- OID4VP / OID4VCI specifications define flows, not test harnesses.
- DIF Presentation Exchange defines data formats; libraries exist but don’t provide conformance matrices.
- Rust implementations (`openid4vp`, `dif-presentation-exchange`) don’t standardize bundles + scenario corpora.

# Design goals / non-goals

**Goals**
- Provide a common “profile language” to declare supported features and constraints.
- Ship a conformance runner (wallet-mode and verifier-mode) with reproducible artifacts.
- Provide secure-by-default redaction rules for sharing failures.

**Non-goals**
- Define new identity standards.
- Provide a full wallet UI or verifier product.

# Architecture & API sketch

Workspace crates:

- `oid4vc-profiles`: declarative profile model (spec version, transport, formats, crypto suites).
- `oid4vc-conformance`: scenario runner and verdict engine.
- `oid4vc-bundles`: bundle format + redaction.
- `cargo oid4vc`: CLI
  - `cargo oid4vc doctor` — validate config, keys, endpoints
  - `cargo oid4vc run` — execute suites (wallet/verifier)
  - `cargo oid4vc replay` — replay a bundle and reproduce verdicts

Adapters:
- wallet/verifier adapters for existing libraries (e.g., `openid4vp`), plus optional hooks to `dif-presentation-exchange` for presentation definition evaluation.

# Bundle format: `*.oid4vcbundle.zip`

Top-level:
- `report.json` (schema_version, profile, verdicts, failures)
- `transcript/` (HTTP requests/responses with header allowlist; redirects; token envelopes)
- `inputs/` (presentation definitions, credential offers, DID/key material *references*, not secrets)
- `checks/` (normalized validation results: signature checks, nonce/state, binding, schema)

Redaction defaults:
- strip subject identifiers
- tokenize claims and store only structural hashes + minimal diagnostics
- store cryptographic material only as key IDs / JWK thumbprints

# Security / safety model

- Threat model explicitly documented (what the kit does *not* protect against).
- Reference validation routines; avoid “accept anything” modes.
- Fuzz/quickcheck for parsing token envelopes and PE structures.

# Maintenance & governance plan

- Versioned profiles; keep “profile packs” as data files with clear provenance.
- CI runs a matrix against sample wallets/verifiers (where possible) and recorded bundles.

# Milestones (0.1 / 0.2 / 1.0)

**0.1**
- profile schema + bundle schema + basic runner skeleton
- minimal suites for OID4VP redirect flow + PE v2 parsing

**0.2**
- add OID4VCI issuance flow scenarios
- add token-format profiles (SD-JWT VC, mdoc placeholders)

**1.0**
- stable bundle schema
- published conformance packs and compatibility guidance

# Open questions

- How to integrate with Digital Credentials API flows without binding to browser internals?
- Best abstraction to support multiple crypto providers while preserving reproducibility?

# Sources

- https://openid.net/specs/openid-4-verifiable-presentations-1_0.html
- https://openid.net/specs/openid-4-verifiable-credential-issuance-1_0.html
- https://identity.foundation/presentation-exchange/spec/v2.0.0/
- https://crates.io/crates/dif-presentation-exchange
- https://github.com/spruceid/openid4vp
