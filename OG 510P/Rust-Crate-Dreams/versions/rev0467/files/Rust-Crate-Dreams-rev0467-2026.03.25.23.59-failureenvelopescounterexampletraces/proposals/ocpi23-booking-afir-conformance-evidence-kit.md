---
id: P-0383
title: OCPI 2.3.0 + Booking + AFIR Conformance & Evidence Kit — roaming-partner bundles, tariff receipts, and extension-aware diffs
status: idea
domains: [ev-charging, mobility, interoperability, billing, compliance, validation, transport]
last_reviewed: 2026-03-06
evidence:
  - https://evroaming.org/ocpi/
  - https://evroaming.org/wp-content/uploads/2025/02/OCPI-2.3.0.pdf
  - https://evroaming.org/ocpi-downloads/
  - https://evroaming.org/evroaming-test-tool/
  - https://docs.rs/ocpi
  - https://crates.io/crates/ocpi-tariffs
---

# Problem

Rust already has protocol substrate for OCPI roles and real tariff-calculation tooling. The EV roaming ecosystem also has an actively maintained spec line, 2.3.0 extensions such as Booking, and a clear regulatory/compliance backdrop around AFIR/NAP-style data mapping.

But the costly failures still happen at the seam between:

- **partner-to-partner interpretation of the same JSON payloads**,
- **tariffs, charging sessions, and CDR receipts that look plausible but disagree semantically**,
- **extension keys and open enums that one side tolerates and the other side rejects**,
- **2.2.1 versus 2.3.0 assumptions around hubs, bookings, taxes, and identifiers**,
- and **compliance or onboarding evidence that still lives in screenshots, Postman exports, and long email threads**.

The missing Rust contribution is not another CPO/eMSP platform. It is an **interop and evidence kit** for partner onboarding, tariff/session/CDR reasoning, extension-aware diffs, and regulatory mapping receipts.

# What it provides

- `ocpi-profile.lock` — pins version, role pair, module set, extension policy, locale/currency assumptions, and AFIR mapping scope.
- `ocpi-irx` — neutral IR for versions, credentials exchange, locations, tariffs, sessions, commands, CDRs, bookings, and hub semantics.
- `receipt-engine` — produces explainable tariff/session/CDR receipts from canonicalized traces.
- `extension-lint` — flags open-enum and custom-field usage against explicit policy.
- `cargo ocpi-evidence` — emits `*.ocpibundle.zip` with lockfile, request/response traces, semantic diffs, and compliance notes.

# What the crate should provide other people

1. **A boring default bundle for partner onboarding and roaming disputes**.
2. **Explainable receipts** for tariffs, sessions, and CDR outcomes.
3. **Version/profile pinning** instead of vague “supports OCPI”.
4. **Extension-aware diffs** that separate benign custom fields from real contract drift.
5. **Compliance mapping artifacts** for AFIR/NAP or internal reporting obligations.

# Persona / who it’s for

- EV roaming platform teams
- CPO and eMSP integrators
- Billing/reconciliation engineers
- Compliance and operations teams debugging public-data mismatches

# Users & user stories

- **Integrator**: “Show exactly why my partner accepted the session but rejected the CDR.”
- **Tariff engineer**: “Produce a human-readable receipt for this OCPI tariff/session combination and explain taxes or step-size effects.”
- **Platform maintainer**: “Pin my open-enum and extension policy so a partner can test against it.”
- **Compliance analyst**: “Map OCPI 2.3.0 fields to AFIR/NAP reporting expectations and show which fields are lossy or non-equivalent.”

# Prior art (and why it’s insufficient)

- The EV Roaming Foundation publishes the OCPI spec and actively evolves 2.3.0, booking extensions, and 3.0 work.
- The EVRoaming test tool covers predefined test scenarios.
- Rust already has `ocpi` API substrate and `ocpi-tariffs` for tariff calculations.

What Rust still lacks is a **portable evidence layer** for semantic partner diffs, explainable receipts, explicit extension policy, and compliance mapping.

# Design goals

1. **Role-aware** — CPO/eMSP/hub semantics must be explicit.
2. **Receipt-first** — tariff/session/CDR outcomes need human-readable explanations.
3. **Extension-aware** — custom fields and open enums are modeled, not hand-waved.
4. **Version-honest** — 2.2.1, 2.3.0, and booking overlays must be pinned.
5. **Compliance-friendly** — reporting mappings and redaction are first-class.

# MVP surface

- Minimal types: `OcpiProfileLock`, `TariffReceipt`, `PartnerDiff`, `OcpiBundle`
- Minimal functions:
  - `normalize_exchange()`
  - `explain_receipt()`
  - `lint_extensions()`
  - `write_bundle()`
- Feature flags:
  - `booking`
  - `hub`
  - `receipt`
  - `afir-map`
  - `redaction`

# Compatibility story

- Sits above existing OCPI client/server crates.
- Can ingest HTTP transcripts, JSON captures, and synthetic scenario fixtures.
- Keeps partner-specific extension policy in overlay files rather than hidden code paths.
- Models receipt differences without assuming one single billing product.

# Conformance & fixtures

- Tiny fixtures for credentials bootstrap, mismatched party IDs, status drift, signed-data length edge cases, and booking workflows.
- Goldens for “same tariff, different session timeline” and “same CDR fields, different semantic outcome”.
- Extension-policy corpora showing tolerated versus rejected custom fields/open enums.
- AFIR/NAP mapping fixtures that make lossy field matches explicit.

# Path to boring stability

- Stabilize the lockfile, receipt schema, and extension policy format before broadening adapters.
- Start with tariff/session/CDR/onboarding pain points.
- Keep partner traces small and redactable.
- Treat 3.0 as a future overlay, not a moving MVP target.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 25/30**

# Minimum lovable MVP

A library and CLI that pin an OCPI profile, normalize partner exchanges, produce explainable receipts for tariffs/sessions/CDRs, and emit compact `*.ocpibundle.zip` artifacts for onboarding and dispute resolution.

# De-risk plan

1. Start with normalization and receipt explanation, not a full roaming simulator.
2. Keep extensions explicit and policy-driven.
3. Separate AFIR/NAP mapping from protocol-core correctness.
4. Use public dummy scenarios with fake IDs and currencies first.

# Non-goals

- Not a replacement for OCPP or charger control.
- Not a full CPO/eMSP platform.
- Not a generic payment processor.
- Not a tax engine for every jurisdiction.

# Architecture & API sketch

```rust
pub struct OcpiProfileLock {
    pub version: String,
    pub role_pair: String,
    pub modules: Vec<String>,
    pub extension_policy: String,
}

pub fn normalize_exchange(input: &[u8]) -> Result<OcpiTrace>;
pub fn explain_receipt(trace: &OcpiTrace, lock: &OcpiProfileLock) -> Result<TariffReceipt>;
pub fn lint_extensions(trace: &OcpiTrace, lock: &OcpiProfileLock) -> Vec<Finding>;
```

Bundle draft: `ocpi-profile.lock`, `trace.json`, `receipt.json`, `partner-diff.json`, `mapping-notes.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Treat tokens, credentials, personal data, and signed data as sensitive by default.
- Prefer structural summaries over raw payload retention.
- Record exact version/module/extension assumptions in every bundle.
- Support deterministic receipt generation for CI and audits.

# Maintenance & governance plan

- Keep the core focused on locks, receipts, semantic diffs, and bundle format.
- Version region- or partner-specific policy packs separately.
- Publish a public corpus of dummy partner traces.
- Resist scope creep into dispatch, payment orchestration, or fleet UX.

# Milestones

## 0.1
- exchange normalization
- receipt engine
- profile lockfile

## 0.2
- extension linting
- booking fixtures
- AFIR/NAP mapping helpers

## 1.0
- stable `*.ocpibundle.zip`
- public fixture corpus
- documented compatibility policy across supported versions/modules

# Open questions

- Which extension-policy format best balances strictness with the open-enum reality of OCPI 2.3.0?
- How much AFIR mapping belongs in core versus optional overlays?
- What is the minimum scenario set needed to catch most real roaming disputes?

# Sources

- OCPI overview/current version: https://evroaming.org/ocpi/
- OCPI 2.3.0 specification: https://evroaming.org/wp-content/uploads/2025/02/OCPI-2.3.0.pdf
- OCPI downloads and booking module: https://evroaming.org/ocpi-downloads/
- EVRoaming test tool: https://evroaming.org/evroaming-test-tool/
- Rust `ocpi` crate: https://docs.rs/ocpi
- Rust `ocpi-tariffs` crate: https://crates.io/crates/ocpi-tariffs
