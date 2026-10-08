---
id: P-0352
title: ISO 20022 + CBPR+ / HVPS+ / SEPA Conformance & Evidence Kit — schema/profile locks, market-practice validation, and replayable payment bug bundles
status: idea
domains: [payments, finance, standards, interoperability, testing]
last_reviewed: 2026-03-06
evidence:
  - https://www.iso20022.org/iso-20022-message-definitions
  - https://www.swift.com/standards/iso-20022/iso-20022-standards
  - https://docs.rs/open-payments-iso20022
  - https://docs.rs/iso20022
  - https://github.com/sebastienrousseau/pain
---

# Problem

Rust can already parse or generate parts of ISO 20022, but production interoperability failures usually do **not** happen at the raw XML boundary. They happen at the seam between:

- base ISO 20022 schemas,
- **market-practice overlays** like CBPR+, HVPS+, or SEPA,
- business/application headers and envelope expectations,
- code lists and usage guidelines that drift over time,
- and bank or market-infrastructure profile assumptions that are hard to version, diff, or share safely.

Teams can often validate against XSDs yet still fail network onboarding, return-message handling, or scheme-specific requirements. The missing Rust contribution is a **profile-pinned conformance and evidence kit** for ISO 20022 operations, not another one-off message model.

# What it provides

- `mx-ir` — canonical Rust IR for business messages, Business Application Header / apphdr context, scheme identifiers, and normalized party/account/agent fields.
- `practice-pack` — lockfiles for CBPR+, HVPS+, SEPA, or institution-specific overlays, including code-list and rule-pack versions.
- `xsd-adapter` — deterministic XSD validation and normalization of schema verdicts.
- `practice-check` — market-practice checks that sit above raw schema validity.
- `mx-diff` — semantic diffs such as “same pacs.008 structure, stricter address rule”, “BAH mismatch”, or “return path changed”.
- `cargo mx-evidence` — emit `*.iso20022bundle.zip` bundles for CI, bank onboarding, or incident handoff.

# What the crate should provide other people

1. **A boring default artifact for payment-message interoperability bugs**.
2. **One place to pin scheme assumptions in Git** instead of scattering them across PDFs, spreadsheets, and ticket comments.
3. **Explainable validation** that distinguishes schema failures from market-practice failures.
4. **Semantic diffs across rule-pack upgrades** so teams can rehearse November-style migrations or partner changes.
5. **Privacy-aware bundles** that help debug real traffic without shipping full customer payloads in the clear.

# Persona / who it’s for

- Payments platform engineers
- Treasury / bank integration teams
- PSPs and bank middleware maintainers
- Rust developers building payment gateways or reconciliation tooling
- QA teams rehearsing market-practice migrations

# Users & user stories

- **Bank-integration engineer**: “Tell me whether the message is XSD-valid but CBPR+-invalid, and give me a compact bundle I can send to the counterparty.”
- **Migration owner**: “Diff our current pacs / pain flows against a new market-practice release before rollout.”
- **Treasury-platform maintainer**: “Pin which ISO 20022 variants we support and gate CI on them.”
- **Incident responder**: “Redact a failing exchange but keep enough structure to reproduce the bug.”

# Prior art (and why it’s insufficient)

- ISO 20022 publishes the official **message definitions catalogue**.
- Swift documents **CBPR+** and related ISO 20022 market-practice surfaces.
- Rust has emerging substrate in `open-payments-iso20022`, `iso20022`, and focused crates like `pain`.
- But there is still no boring-default Rust crate family for **scheme lockfiles + market-practice checking + semantic diffs + portable evidence bundles**.

# Design goals

1. **Overlay-aware** — raw schema validity is necessary but not sufficient.
2. **Version-pinned** — every report must record exact schema and rule-pack versions.
3. **Explainable** — findings should map to business concepts, not only XPath or XSD noise.
4. **Privacy-aware** — evidence must support field-level hashing, omission, and reversible local redaction maps.
5. **Network-neutral core** — useful across banks, PSPs, and domestic or cross-border schemes.

# MVP surface

- Minimal types: `MxMessage`, `BusinessHeader`, `PracticePack`, `MxReport`, `MxDiffFinding`
- Minimal functions:
  - `load_message()`
  - `validate_xsd()`
  - `validate_practice_pack()`
  - `diff_reports()`
  - `write_bundle()`
- Feature flags:
  - `cbpr`
  - `hvps`
  - `sepa`
  - `serde`
  - `redaction`

# Compatibility story

- MVP should focus on a small set of high-friction payment families first: practical `pacs.*`, `pain.*`, and related headers.
- The crate should interoperate with existing Rust parsers/generators rather than replace them.
- Scheme-specific packs should stay optional and separately versioned.
- The core should remain useful even when some market-practice documentation is proprietary or semi-restricted.

# Conformance & fixtures

- Tiny public XML fixtures for valid / invalid `pacs.008`, `pacs.009`, and `pain.001` style flows.
- Goldens for “XSD-valid but profile-invalid”, header/body mismatches, forbidden codes, and return-path drift.
- Redaction fixtures proving that findings remain reproducible after masking sensitive values.
- Rule-pack fixtures that model version changes in usage guidelines or code lists.

# Path to boring stability

- Stabilize the IR and findings vocabulary before broadening message-family coverage.
- Keep early scope to a handful of message families and one or two overlay packs.
- Freeze bundle layout only after it works for CI, onboarding, and counterparty support cases.
- Add richer partner-policy packs only after the neutral core is well tested.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 3/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 25/30**

# Minimum lovable MVP

A library and CLI that load a small set of ISO 20022 payment messages, validate them against pinned schema plus one market-practice pack, normalize the findings, and emit a compact `*.iso20022bundle.zip` with redaction support.

# De-risk plan

1. Start with one message family plus one market-practice pack.
2. Normalize XSD and overlay findings before inventing new rule families.
3. Keep bundles small and text-first.
4. Treat institution-specific overlays as optional add-ons, not core guarantees.

# Non-goals

- Not a payment switch.
- Not a sanctions-screening engine.
- Not a bank-operations dashboard.
- Not a complete ISO 20022 implementation for every domain.

# Architecture & API sketch

```rust
pub struct MxReport {
    pub schema_version: String,
    pub practice_pack: String,
    pub findings: Vec<Finding>,
    pub diffs: Vec<MxDiffFinding>,
}

pub fn validate_practice_pack(pack: &PracticePack, msg: &MxMessage) -> Result<MxReport>;
pub fn write_bundle(report: &MxReport, out: impl std::io::Write) -> Result<()>;
```

Bundle draft: `profile.toml`, `message.xml`, `header.json`, `xsd-report.json`, `practice-report.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Treat incoming XML and attachments as untrusted.
- Default to redacting high-risk party/account/reference fields.
- Record exact schema, rule-pack, and code-list versions.
- Support deterministic hashing so support teams can correlate redacted fields across runs.

# Maintenance & governance plan

- Keep core focused on message IRs, findings normalization, and bundle formats.
- Version market-practice packs separately from the core crate.
- Build a small public corpus of safe fixtures for CI and onboarding rehearsal.
- Avoid coupling the project to one bank or scheme operator.

# Milestones

## 0.1
- XML loader
- XSD adapter
- one market-practice pack
- bundle writer

## 0.2
- semantic diffs
- redaction helpers
- additional payment-message families

## 1.0
- stable `*.iso20022bundle.zip`
- public fixture corpus
- documented upgrade policy for schema and rule-pack drift

# Open questions

- Which market-practice packs are open enough to ship as first-party fixtures?
- How should proprietary scheme rules be referenced without embedding restricted text?
- What minimum redacted payload is enough for useful counterparty debugging?

# Sources

- ISO 20022 message definitions: https://www.iso20022.org/iso-20022-message-definitions
- ISO 20022 catalogue of messages: https://www.iso20022.org/catalogue-messages
- Swift ISO 20022 standards / CBPR+ and HVPS+: https://www.swift.com/standards/iso-20022/iso-20022-standards
- `open-payments-iso20022`: https://docs.rs/open-payments-iso20022
- `iso20022`: https://docs.rs/iso20022
- `pain`: https://github.com/sebastienrousseau/pain
