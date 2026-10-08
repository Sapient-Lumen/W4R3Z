---
id: P-0378
title: FIDO Device Onboard 2.0 / 1.1 Interop & Certification Evidence Kit — ownership-voucher locks, serviceinfo replay, and safe onboarding incident bundles
status: idea
domains: [iot, security, device-onboarding, interoperability, validation, provisioning, enterprise]
last_reviewed: 2026-03-06
evidence:
  - https://fidoalliance.org/specs/FDO/FIDO-Device-Onboard-WD-v2.0-20250617/FIDO-Device-Onboard-WD-v2.0-20250617.html
  - https://fidoalliance.org/specs/FDO/FIDO-Device-Onboard-RD-v1.1-20211214/FIDO-device-onboard-spec-v1.1-rd-20211214.pdf
  - https://fidoalliance.org/get-certified-fdo/
  - https://github.com/fdo-rs/fido-device-onboard-rs
  - https://github.com/fdo-rs
---

# Problem

Rust already has a serious FDO implementation in `fdo-rs`, and the FIDO Alliance now has both an established 1.1 specification and a newer 2.0 working draft. But the painful failures still happen at the seam between:

- **manufacturing artifacts and ownership-voucher transfer**,
- **rendezvous information and real network reachability**,
- **device credentials / attestation posture and onboarding policy**,
- **serviceinfo exchanges and what the device actually does next**,
- and **certification/self-validation claims that are hard to reproduce outside one lab**.

The missing Rust contribution is not another full FDO stack. It is a **version-aware interop and certification evidence kit** that makes onboarding failures portable, redactable, and explainable.

# What it provides

- `fdo-profile.lock` — pins spec/profile assumptions, rendezvous policy, ownership-voucher shape, device-key expectations, and serviceinfo modules in scope.
- `fdo-irx` — a neutral IR for onboarding traces, ownership-voucher metadata, rendezvous directives, serviceinfo exchanges, and redaction boundaries.
- `trace-normalizer` — canonicalizes logs and message traces from device, rendezvous, manufacturing, and owner/onboarding services.
- `cert-rehearsal` — runs narrow self-validation / conformance scenarios and emits comparable evidence.
- `cargo fdo-evidence` — emits `*.fdobundle.zip` with lockfile, normalized traces, voucher summaries, replay hints, and notes.

# What the crate should provide other people

1. **A boring default artifact for FDO onboarding incidents**.
2. **Spec/profile locks** instead of vague “supports FDO”.
3. **Replayable serviceinfo and onboarding traces** that survive handoff across vendors or teams.
4. **Certification rehearsal artifacts** that are small enough for CI and support workflows.
5. **Safe redaction** for secrets, voucher payloads, and production network details.

# Persona / who it’s for

- Device manufacturers and integrators using FDO for zero-touch onboarding
- Rust maintainers building or extending FDO infrastructure
- Edge / IoT platform teams debugging failed ownership transfer or onboarding
- Security and certification teams collecting evidence for conformance workflows

# Users & user stories

- **Platform owner**: “Tell me whether the device failed because of voucher content, rendezvous policy, serviceinfo, or owner-service behavior.”
- **Integrator**: “Produce a bug bundle I can share with another vendor without disclosing live credentials.”
- **Maintainer**: “Run one public fixture corpus against multiple FDO services and profile overlays.”
- **Certification engineer**: “Capture comparable evidence from self-validation runs rather than ad hoc screenshots and logs.”

# Prior art (and why it’s insufficient)

- FDO 1.1 is specified and implemented in Rust by `fdo-rs`.
- FDO 2.0 is already evolving in public working-draft form.
- FIDO certification guidance explicitly points implementers toward conformance testing and results submission.

What Rust still lacks is a **boring default evidence layer** for version-aware traces, ownership-voucher summaries, serviceinfo replay, and safe incident bundles above the implementation substrate.

# Design goals

1. **Version-aware** — 1.1 and 2.0 assumptions must be explicit.
2. **Message-boundary honest** — preserve enough protocol structure to explain failures.
3. **Redaction-safe** — bundles should be shareable without leaking secrets.
4. **Certification-aligned** — useful both for local rehearsal and cross-team debugging.
5. **Implementation-neutral** — complement `fdo-rs` and future stacks rather than replacing them.

# MVP surface

- Minimal types: `FdoProfileLock`, `VoucherSummary`, `ServiceInfoFinding`, `FdoBundle`
- Minimal functions:
  - `inspect_trace()`
  - `normalize_onboarding_logs()`
  - `replay_serviceinfo()`
  - `write_bundle()`
- Feature flags:
  - `fdo11`
  - `fdo20`
  - `serviceinfo`
  - `voucher-summary`
  - `redaction`

# Compatibility story

- Works above existing `fdo-rs` deployments rather than replacing them.
- Can ingest traces/logs/artifacts generated externally.
- Treats certification or self-validation adapters as optional modules around one stable evidence format.
- Keeps cross-version differences explicit in lockfiles instead of hidden heuristics.

# Conformance & fixtures

- Tiny fixtures for malformed or mismatched ownership vouchers, rendezvous resolution issues, serviceinfo negotiation errors, and version/profile mismatches.
- Goldens for “same voucher, different onboarding result” and “same trace, different normalization outcome”.
- Public fixture packs for owner/onboarding/serviceinfo sequences with safe dummy credentials.
- Replay adapters that can compare expected versus observed serviceinfo phases.

# Path to boring stability

- Stabilize trace schema, lockfile, and redaction policy before broadening adapters.
- Start with voucher/serviceinfo/reachability failure modes because they explain a large share of onboarding pain.
- Keep the first release aimed at evidence shipping and certification rehearsal, not a new provisioning product.
- Preserve exact spec/profile version references in every bundle.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 3/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 5/5
- **Total: 23/30**

# Minimum lovable MVP

A library and CLI that ingest FDO onboarding traces and artifacts, pin an explicit version/profile lock, summarize ownership-voucher and serviceinfo behavior, and emit a compact `*.fdobundle.zip` for debugging or rehearsal.

# De-risk plan

1. Start with artifact normalization and replay rather than a new FDO runtime.
2. Keep secrets/redaction policy explicit and testable.
3. Use public dummy fixture corpora for onboarding scenarios.
4. Avoid coupling the core too tightly to one service implementation.

# Non-goals

- Not a replacement for `fdo-rs`.
- Not a full device-management platform.
- Not a new PKI or secure-element stack.
- Not a certification portal product.

# Architecture & API sketch

```rust
pub struct FdoProfileLock {
    pub spec_version: String,
    pub rendezvous_policy: String,
    pub serviceinfo_modules: Vec<String>,
}

pub fn inspect_trace(input: &[u8]) -> Result<OnboardingReport>;
pub fn replay_serviceinfo(report: &OnboardingReport, lock: &FdoProfileLock) -> ReplayResult;
```

Bundle draft: `fdo-profile.lock`, `trace.json`, `voucher-summary.json`, `serviceinfo-findings.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Treat all onboarding traces and artifacts as sensitive until redacted.
- Support structural summaries of vouchers and protocol steps without preserving raw secrets.
- Record exact implementation, profile, and normalization versions in every bundle.
- Prefer deterministic, append-only bundle generation for audits and CI.

# Maintenance & governance plan

- Keep the core centered on version/profile locks, neutral traces, replay findings, and bundle format.
- Version certification adapters separately where needed.
- Publish a public fixture corpus that avoids real credentials and infrastructure.
- Resist scope creep into full lifecycle/device fleet management.

# Milestones

## 0.1
- trace ingestion
- profile lockfile
- voucher/serviceinfo summaries

## 0.2
- replay helpers
- redaction support
- certification rehearsal adapters

## 1.0
- stable `*.fdobundle.zip`
- public fixture corpus
- documented compatibility policy across supported versions/profiles

# Open questions

- How much of 2.0 belongs in MVP versus a strict 1.1-first release with version overlays?
- What is the smallest safe redaction model that still makes debugging possible?
- Which certification/self-validation outputs are worth normalizing first?

# Sources

- FDO 2.0 working draft: https://fidoalliance.org/specs/FDO/FIDO-Device-Onboard-WD-v2.0-20250617/FIDO-Device-Onboard-WD-v2.0-20250617.html
- FDO 1.1 specification: https://fidoalliance.org/specs/FDO/FIDO-Device-Onboard-RD-v1.1-20211214/FIDO-device-onboard-spec-v1.1-rd-20211214.pdf
- FDO certification guidance: https://fidoalliance.org/get-certified-fdo/
- `fdo-rs` implementation: https://github.com/fdo-rs/fido-device-onboard-rs
- `fdo-rs` organization overview: https://github.com/fdo-rs
