---
id: P-0326
title: LTI 1.3 + LTI Advantage Conformance & Evidence Kit — profile-pinned launches, service replay, and LMS/tool interoperability bundles
status: idea
domains: [education, lti, oauth, oidc, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://www.1edtech.org/standards/lti
  - https://www.imsglobal.org/spec/lti/v1p3
  - https://www.1edtech.org/certification/lti
  - https://github.com/atomicjolt-com/atomic-forge
  - https://docs.rs/atomic-lti-tool
  - https://docs.rs/atomic-lti-tool-axum
---

# Problem

Rust finally has credible LTI 1.3 substrate, but the real pain for schools, LMS vendors, and tool vendors is not “can I decode a JWT?” It is the seam between launch, registration, and service behavior:

- OIDC initiation and launch flows that work in one LMS and fail subtly in another,
- AGS/NRPS/deep-linking support that is present but not profile-consistent,
- institution-specific registration and deployment assumptions drifting over time,
- certification work that still becomes screenshots, copied JWTs, and brittle local test rigs,
- and security-sensitive evidence that is hard to share safely.

The worthy crate contribution is a **LTI 1.3 + LTI Advantage conformance and evidence kit** that turns launches and service interactions into replayable, redactable, profile-pinned artifacts.

# What it provides

- `lti-ir` — canonical IR for registrations, deployments, OIDC init, launch claims, deep-linking payloads, AGS/NRPS interactions, and dynamic-registration events.
- `lti-profile` — lockfiles pinning spec surfaces, enabled services, LMS quirks, required claims, and certification expectations.
- `lti-verify` — semantic verification for launch flows, claim sets, nonce/state handling, service permissions, and response shapes.
- `lti-replay` — deterministic replay of launch and service exchanges with secrets redacted.
- `lti-diff` — explainable diffs: “launch claim set changed”, “role mapping changed”, “AGS scopes missing”, “deep-link response no longer matches platform expectations”.
- `cargo lti` — emit `*.ltibundle.zip` for certification rehearsal, vendor escalations, and regression CI.

# What the crate should provide other people

1. **A portable launch/support artifact** for LMS-tool compatibility bugs.
2. **Pinned profiles** for the exact services and claims a deployment assumes.
3. **Replayable certification-style traces** without moving raw secrets around.
4. **Explainable diffs** for platform migrations and LTI service enablement changes.
5. **A shared conformance layer above current Rust LTI libraries**.

# Persona / who it’s for

- Tool vendors building LTI integrations
- LMS/platform implementers
- Institutions validating third-party tools
- QA teams preparing certification submissions
- Rust framework/library authors serving edtech stacks

# Users & user stories

- **Tool engineer**: “Replay the exact launch that Canvas accepted and Moodle rejected.”
- **Platform team**: “Pin the service and claim requirements for our institutional integration profile.”
- **Certification prep team**: “Generate a bundle we can rerun before submitting test results.”
- **Security reviewer**: “Inspect the evidence without exposing raw tokens, names, or grades.”

# Prior art (and why it’s insufficient)

- 1EdTech’s LTI standard and certification process make conformance and diagnostics central.
- Rust substrate now exists in Atomic Forge and related crates such as `atomic-lti-tool` and `atomic-lti-tool-axum`.
- This means Rust is no longer missing the entire foundation.
- What it still lacks is a boring-default **profile lockfile + replay + semantic diff + redactable evidence bundle** workflow for real LMS/tool interoperability.

# Design goals

1. **Flow-first** — correctness lives in sequences, not only individual requests.
2. **Secret-safe evidence** — redaction and token minimization are mandatory.
3. **Profile-pinned** — every integration should state exactly which claims/services matter.
4. **Certification-adjacent** — useful before, during, and after formal testing.
5. **Framework-neutral** — adapters for Axum/Actix/etc. without forcing one stack.

# MVP surface

- Minimal types: `LtiLaunchTrace`, `LtiProfile`, `ServiceCall`, `LtiReport`, `RedactionPlan`
- Minimal functions:
  - `capture_launch()`
  - `verify_launch()`
  - `verify_service_call()`
  - `diff_trace()`
  - `write_bundle()`
- Feature flags:
  - `core`
  - `deep-linking`
  - `ags`
  - `nrps`
  - `dynamic-registration`
  - `redaction`

# Compatibility story

- Interoperates with LTI 1.3 core launches and selected LTI Advantage services first.
- Adapters should sit above existing Rust libraries rather than replace them.
- Intentionally avoids becoming a full LMS, gradebook, or course tool platform.

# Conformance & fixtures

- Synthetic launch traces for success and failure cases.
- Service-call fixtures for AGS, NRPS, and deep linking.
- Redaction-preservation tests.
- Optional adapters for certification-prep outputs and Atomic Forge test fixtures.

# Path to boring stability

- Freeze the launch IR before broadening service coverage.
- Keep profiles explicit about required claims and scopes.
- Prove replay and redaction on multiple LMS-style fixture families.
- Add services incrementally; do not pretend “LTI Advantage” is one uniform surface.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 24/30**

# Minimum lovable MVP

A library/CLI that captures one LTI 1.3 launch plus one Advantage service interaction, verifies them against a pinned profile, redacts sensitive material, and emits a replayable `*.ltibundle.zip`.

# De-risk plan

1. Start with launches and AGS/NRPS coverage, not the full service universe.
2. Reuse existing Rust launch and claim-validation substrate where possible.
3. Keep redaction and replay in scope from day one.
4. Add LMS-specific profile packs only after a generic baseline stabilizes.

# Non-goals

- Not a complete LMS or tool runtime.
- Not a general OAuth/OIDC framework.
- Not a grading product or analytics platform.

# Architecture & API sketch

```rust
pub struct LtiReport {
    pub profile_id: String,
    pub verdicts: Vec<Verdict>,
    pub launch_findings: Vec<LaunchFinding>,
    pub service_findings: Vec<ServiceFinding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn verify_trace(profile: &LtiProfile, trace: &LtiLaunchTrace) -> LtiReport;
```

Bundle draft: `profile.toml`, `launch/init.json`, `launch/claims.json`, `services/*.json`, `verdicts.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Redact JWTs, subject identifiers, deployment IDs, names, emails, and grades by default.
- Preserve claim structure and service semantics after redaction.
- Record which cryptographic validations were performed and with which keys/metadata snapshot.
- Bound retention of raw request/response bodies.

# Maintenance & governance plan

- Ship base profiles for generic LTI 1.3 core plus opt-in service packs.
- Keep LMS-specific quirks as profile modules, not hard-coded logic.
- Publish synthetic traces rather than real student data.
- Encourage test-fixture adapters from existing Rust LTI projects.

# Milestones

## 0.1
- Launch IR
- Profile lockfiles
- Core launch verification and bundle format

## 0.2
- AGS/NRPS support
- Diff engine
- Redaction-preserving replay

## 1.0
- Stable `*.ltibundle.zip`
- Multiple LMS profile packs
- CI-ready certification rehearsal workflows

# Open questions

- Which LTI Advantage services are essential for MVP versus adapters?
- How much dynamic registration belongs in core?
- Can LMS-specific quirks remain data-driven enough to avoid framework creep?

# Sources

- 1EdTech LTI overview: https://www.1edtech.org/standards/lti
- LTI 1.3 spec: https://www.imsglobal.org/spec/lti/v1p3
- LTI certification process: https://www.1edtech.org/certification/lti
- Atomic Forge: https://github.com/atomicjolt-com/atomic-forge
- `atomic-lti-tool`: https://docs.rs/atomic-lti-tool
- `atomic-lti-tool-axum`: https://docs.rs/atomic-lti-tool-axum
