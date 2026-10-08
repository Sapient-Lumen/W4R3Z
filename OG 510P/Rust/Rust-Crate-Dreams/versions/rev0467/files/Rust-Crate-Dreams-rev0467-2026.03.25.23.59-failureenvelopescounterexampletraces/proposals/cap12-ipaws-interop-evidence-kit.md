---
id: P-0345
title: CAP 1.2 + IPAWS Interop & Evidence Kit — profile-aware emergency-alert validation, redactable exchange bundles, and explainable warning-system diffs
status: idea
domains: [public-safety, emergency-alerting, cap, ipaws, xml, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2-os.html
  - https://docs.oasis-open.org/emergency/cap/v1.2/ipaws-profile/v1.0/cap-v1.2-ipaws-profile-v1.0.html
  - https://www.fema.gov/emergency-managers/practitioners/integrated-public-alert-warning-system/technology-developers/common-alerting-protocol
  - https://crates.io/crates/rasn-cap
  - https://github.com/willglynn/oasiscap
---

# Problem

Emergency-alerting systems still fail at the seam between **base CAP documents and profile-constrained operational networks**:

- alerts that are syntactically valid CAP but not acceptable to an IPAWS-style exchange,
- downstream systems that ingest the XML but disagree on event-code, geocode, parameter, or dissemination semantics,
- support workflows that are sensitive enough to resist easy sharing,
- and debugging that still relies on screenshots, copied XML, and tribal knowledge about profile quirks.

The worthy crate contribution is a **profile-aware interop and evidence kit** that makes CAP exchange behavior explainable, replayable, and safer to share.

# What it provides

- `cap-ir` — canonical IR for alert metadata, areas, geocodes, parameters, references, multilingual content, and dissemination/profile metadata.
- `cap-profile` — lockfiles pinning CAP version, IPAWS constraints, local/profile overlays, required codes, and redaction rules.
- `cap-verify` — normalized structural and profile-specific checks with explainable findings.
- `cap-diff` — semantic diffs such as “same hazard, different dissemination semantics”, “parameter set no longer profile-valid”, or “area targeting changed meaning”.
- `cap-redact` — deterministic redaction for contact details, free-text fields, or local identifiers when issue sharing is sensitive.
- `cargo cap-evidence` — emit `*.capbundle.zip` for certification rehearsal, incident triage, and inter-agency debugging.

# What the crate should provide other people

1. **A boring default for CAP profile validation** in Rust.
2. **Explainable profile failures** instead of opaque XML rejection.
3. **Redactable issue bundles** for sensitive or operationally restricted alerts.
4. **Semantic diffs** that focus on alert meaning and dissemination behavior.
5. **A bridge from schema validity to real exchange-network readiness**.

# Persona / who it’s for

- Alert-origination software vendors
- Public warning platform teams
- Government and broadcaster integration engineers
- QA/certification teams

# Users & user stories

- **Integrator**: “Tell me whether this alert is CAP-valid but IPAWS-invalid, and why.”
- **Support engineer**: “Redact sensitive fields but keep the failure reproducible.”
- **QA lead**: “Pin the exact profile and code requirements used in this test run.”
- **Operator**: “Diff the rejected alert against the accepted one in operational terms.”

# Prior art (and why it’s insufficient)

- OASIS CAP 1.2 defines the base format.
- OASIS publishes the CAP 1.2 IPAWS profile.
- FEMA documents CAP/IPAWS usage for technology developers.
- Rust has type/model substrate in `rasn-cap` and `oasiscap`.
- But Rust still lacks a shared **profile pack + explainable validator + semantic diff + redactable evidence bundle** layer.

# Design goals

1. **Profile-first** — CAP validity alone is not enough for real deployments.
2. **Operational explainability** — findings should map to alerting concepts, not just XML paths.
3. **Redaction-first evidence** — issue sharing must be safer by default.
4. **Network-neutral core** — useful for IPAWS and for adjacent CAP-profile ecosystems.
5. **Tiny, durable bundles** — suitable for audits and incident reviews.

# MVP surface

- Minimal types: `CapAlert`, `CapProfile`, `CapFinding`, `CapReport`, `RedactionPlan`
- Minimal functions:
  - `parse_alert()`
  - `verify_alert()`
  - `diff_alerts()`
  - `redact_alert()`
  - `write_bundle()`
- Feature flags:
  - `cap-1-2`
  - `ipaws`
  - `serde`
  - `redaction`

# Compatibility story

- MVP targets CAP 1.2 plus IPAWS-like profile overlays first.
- It should complement existing Rust CAP parsers/models rather than replace them.
- It intentionally avoids becoming a live alert-origination or dissemination platform.

# Conformance & fixtures

- Tiny public-domain alert examples and synthetic hazards.
- Profile-valid vs profile-invalid examples for areas, parameters, and event/reference usage.
- Redaction tests for contact blocks and free-text notes.
- Semantic diff cases for escalation, area changes, and dissemination changes.

# Path to boring stability

- Stabilize the profile pack format before broad ecosystem overlays.
- Keep validation findings explicit about CAP-base versus profile-specific failures.
- Freeze redaction semantics and bundle layout early.
- Record exact profile/hash versions in every artifact.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 24/30**

# Minimum lovable MVP

A validator and diff tool for CAP 1.2 alerts that pins an IPAWS-style profile, reports explainable findings, optionally redacts sensitive fields, and emits a portable `*.capbundle.zip`.

# De-risk plan

1. Limit MVP to the CAP 1.2 core plus one profile family.
2. Start with static XML validation and semantic findings, not transport/network integration.
3. Build the redaction model early.
4. Use synthetic alerts and public examples first.

# Non-goals

- Not a live broadcaster or emergency notification platform.
- Not a policy engine for who is authorized to send alerts.
- Not a replacement for operational certification processes.

# Architecture & API sketch

```rust
pub struct CapReport {
    pub profile_id: String,
    pub structural_findings: Vec<Finding>,
    pub profile_findings: Vec<Finding>,
    pub semantic_diffs: Vec<DiffFinding>,
}

pub fn verify_alert(profile: &CapProfile, alert: &CapAlert) -> CapReport;
```

Bundle draft: `profile.toml`, `alert.xml`, `normalized.json`, `findings.json`, `semantic-diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Deterministic redaction for sensitive free-text or local identifiers when requested.
- Guard XML parsing against resource abuse.
- Preserve structural evidence and code/value semantics after redaction.
- Record exact profile/version hashes.

# Maintenance & governance plan

- Ship profile packs as versioned data.
- Keep core focused on validation, diffs, and bundles.
- Encourage synthetic/public fixtures for tests.
- Treat redaction regressions as release blockers.

# Milestones

## 0.1
- CAP 1.2 parser adapters
- profile lockfiles
- explainable findings

## 0.2
- semantic diffs
- redaction support
- bundle writer

## 1.0
- stable `*.capbundle.zip`
- public fixture corpus
- documented profile-pack lifecycle

# Open questions

- How much local/jurisdiction-specific overlay logic belongs in the generic core?
- What is the right stable vocabulary for alert-semantic diffs?
- Should code-list bundles be embedded or referenced by hash?

# Sources

- OASIS CAP 1.2: https://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2-os.html
- OASIS CAP 1.2 IPAWS Profile: https://docs.oasis-open.org/emergency/cap/v1.2/ipaws-profile/v1.0/cap-v1.2-ipaws-profile-v1.0.html
- FEMA CAP/IPAWS developer guidance: https://www.fema.gov/emergency-managers/practitioners/integrated-public-alert-warning-system/technology-developers/common-alerting-protocol
- `rasn-cap`: https://crates.io/crates/rasn-cap
- `oasiscap`: https://github.com/willglynn/oasiscap
