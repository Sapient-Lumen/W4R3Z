---
id: P-0315
title: DCSA eBL + PINT Interop & Evidence Kit — cross-platform bill-of-lading exchange, legal-profile pinning, and portable dispute bundles
status: idea
domains: [shipping, trade, logistics, standards, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://dcsa.org/our-mission/ebl-interoperability-platform
  - https://dcsa.org/standards/bill-of-lading
  - https://dcsa.org/newsroom/ebl-interoperability-milestone
---

# Problem

Electronic bills of lading are one of those standards domains where “a parser” barely matters compared with the real problem:

- multiple platforms must exchange legally meaningful documents,
- interoperability depends on both payloads and bilateral/API/legal assumptions,
- operators need compact evidence when a transfer, endorsement, or handoff fails,
- the ecosystem is moving from theory to real interoperable production events.

This makes DCSA eBL / PINT a strong candidate for an epic Rust crate contribution: a **cross-platform interop and evidence workbench** that turns document handoff incidents into reproducible, redactable artifacts.

# What it provides

- `ebl-profile` — lockfiles for DCSA bill-of-lading version, PINT API expectations, annex/legal/profile assumptions, and partner capabilities.
- `ebl-canon` — normalized document/event IR for issue, transfer, surrender, update, and supporting-document exchange.
- `ebl-verify` — checks profile compatibility, event sequencing, document identity continuity, and API-contract expectations.
- `ebl-replay` — deterministic replay of cross-platform exchange incidents.
- `ebl-diff` — explainable diffs for “why this eBL handoff or endorsement chain diverged”.
- `cargo ebl` — emit `*.eblbundle.zip` for platform support, carrier/platform onboarding, and legal/operations triage.

# What the crate should provide other people

1. **A neutral incident bundle** for all parties in a digital-trade dispute or onboarding flow.
2. **Profile/legal/version pinning** so implementers can state exactly what interop contract they support.
3. **Cross-platform replay** that reduces finger-pointing between providers.
4. **Redactable evidence shipping** that preserves chain-of-custody and document identity without over-sharing.
5. **A Rust foothold in a genuinely important trade digitization layer**.

# Users & user stories

- **eBL platform providers**: “Replay a failed cross-platform transfer using the exact partner profile.”
- **Carrier / shipper integration teams**: “Prove whether the mismatch is API behavior, document state, or profile/legal assumptions.”
- **Operations / support teams**: “Produce a small bundle for escalation instead of forwarding giant logs and screenshots.”
- **Auditors / program teams**: “Archive passing interop runs as a release gate.”

# Prior art (and why it’s insufficient)

- DCSA now offers a concrete interoperability story built around PINT and associated legal/framework components.
- The first live standards-based interoperable eBL transaction shows this is no longer hypothetical market theater.
- Yet Rust does not have an obvious boring default for **version pinning, event-chain verification, replay, and portable evidence** in this domain.

# Design goals

1. **Interop-first** — optimize for cross-platform handoff, not document authoring bells and whistles.
2. **Version/legal/profile explicitness** — assumptions must be pinned, not tribal knowledge.
3. **Portable dispute artifacts** — bundles should survive handoff between organizations.
4. **Redaction by design** — commercial sensitivity is unavoidable.
5. **Spec-adjacent, not platform-ambitious** — help implementations communicate and debug.

# Non-goals

- Not a full trade-document SaaS platform.
- Not legal advice or a substitute for contractual governance.
- Not a generic PDF/document-management system.

# Architecture & API sketch

```rust
pub struct EblInteropReport {
    pub profile_id: String,
    pub verdicts: Vec<Verdict>,
    pub chain_findings: Vec<ChainFinding>,
    pub divergences: Vec<Divergence>,
}

pub fn verify_exchange(profile: &Profile, exchange: &ExchangeBundle) -> EblInteropReport;
```

Bundle draft: `profile.toml`, `events.jsonl`, `documents/`, `api-transcript.json`, `identity-map.json`, `redaction-map.json`, `verdicts.json`, `notes.md`.

# Security / safety model

- Strong selective disclosure for counterparties, prices, references, and attached documents.
- Preserve document-identity continuity and event ordering across redaction.
- Keep cryptographic/signature hooks pluggable because deployments will vary.
- Make legal/profile metadata explicit so bundles remain interpretable later.

# Maintenance & governance plan

- Pin exact DCSA B/L and PINT snapshot versions in profiles and fixtures.
- Publish vendor-neutral exchange scenarios for issuance, transfer, surrender, amendment, and failure cases.
- Keep core event-chain model separate from organization-specific workflow adapters.
- Encourage “known divergence” catalogs so future implementers learn from recurring incidents.

# Milestones

## 0.1
- Canonical exchange IR
- Profile lockfiles
- Replayable minimal handoff bundle

## 0.2
- Chain-of-custody / sequencing diagnostics
- Redaction presets and fixture packs
- Partner-profile comparison tooling

## 1.0
- Stable `*.eblbundle.zip`
- Cross-provider release-gate workflows
- Evidence/report export for audits and escalations

# Open questions

- How much legal-framework metadata belongs in portable bundles?
- Which attached/supporting-document formats deserve first-class normalization?
- Should the MVP begin with PINT transfer flows before broader B/L lifecycle coverage?

# Sources

- DCSA eBL interoperability platform: https://dcsa.org/our-mission/ebl-interoperability-platform
- DCSA Bill of Lading standard: https://dcsa.org/standards/bill-of-lading
- DCSA interoperability milestone: https://dcsa.org/newsroom/ebl-interoperability-milestone
