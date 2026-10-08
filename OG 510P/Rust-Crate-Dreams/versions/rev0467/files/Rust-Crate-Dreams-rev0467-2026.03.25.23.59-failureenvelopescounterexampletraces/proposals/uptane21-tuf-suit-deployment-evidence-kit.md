---
id: P-0370
title: Uptane 2.1 + TUF / SUIT Deployment & Evidence Kit — role-aware campaign locks, ECU replay, and explainable OTA failure bundles
status: idea
domains: [security, embedded, automotive, iot, updates, standards, interoperability, validation, tooling]
last_reviewed: 2026-03-06
evidence:
  - https://uptane.org/docs/2.1.0/standard/uptane-standard
  - https://uptane.org/docs/2.1.0/deployment/best-practices
  - https://crates.io/crates/tough
  - https://crates.io/crates/tuf
  - https://crates.io/crates/tuftool
  - https://crates.io/crates/suit_validator
  - https://datatracker.ietf.org/doc/html/rfc9124
---

# Problem

Rust already has real TUF and update-related building blocks, but the painful operational failures in secure update systems still happen at the seam between:

- Uptane roles and repository topology,
- deployment-time policy choices such as director/image repository behavior, delegations, key rotation, and ECU grouping,
- campaign execution evidence from real update attempts,
- optional constrained-device manifest layers such as `SUIT`,
- and incident reports that arrive as “the update should have worked but this ECU rejected it” with no compact, reviewable evidence bundle.

The missing Rust contribution is not another updater. It is a **deployment-and-evidence workbench** that makes secure-update assumptions explicit and OTA failures replayable.

# What it provides

- `update-lock` — lockfiles pinning Uptane roles, repository mapping assumptions, threshold/signing policy, ECU classes, target metadata expectations, and optional SUIT-manifest assumptions.
- `ota-irx` — a neutral IR for repositories, metadata chains, targets, campaigns, ECU verdicts, and failure reasons.
- `campaign-replay` — replay a captured update attempt against a locked policy and record exactly where verification or policy diverged.
- `role-diff` — semantic diffs such as “same target image, different delegation path”, “same metadata, expired at replay time”, or “same payload, blocked by ECU policy or hardware constraints”.
- `cargo ota-evidence` — emits `*.otabundle.zip` with metadata snapshots, lockfile, replay transcript, redaction-aware device facts, and notes.

# What the crate should provide other people

1. **A boring default artifact for secure-update failures**.
2. **Role-aware locks** so teams can pin the actual deployment policy, not just the abstract standard.
3. **Replayable OTA evidence** for CI, certification rehearsal, supplier debugging, and incident review.
4. **Explainable diffs** across campaigns, metadata snapshots, and ECU verdicts.
5. **A bridge from Rust TUF/SUIT libraries to evidence-grade deployment workflows**.

# What the crate should provide in theory and in practice

In theory, the crate should separate **stable standards surfaces** from deployment overlays: Uptane and TUF define the trust and repository model; SUIT should remain an optional, clearly bounded manifest layer rather than quietly becoming required everywhere.

In practice, that means the crate should:
- make the Uptane/TUF policy lockfile stable first,
- treat captured campaigns and replay evidence as first-class artifacts,
- and support SUIT only where it sharpens the explanation of constrained-device update behavior.

# Persona / who it’s for

- Automotive and IoT platform teams operating secure update systems
- Rust engineers building OTA services, repository tooling, or verification paths
- Device vendors and integrators debugging update campaigns
- Security reviewers who need portable evidence for why an update succeeded or failed

# Users & user stories

- **OTA operator**: “Explain whether this failure is metadata trust, delegation, expiry, rollback protection, or ECU policy.”
- **Integrator**: “Pin exactly what repository and ECU policy we ship so environment drift becomes visible.”
- **Incident responder**: “Open one bundle and replay the failure without needing the whole production backend.”
- **Tool maintainer**: “Compare two campaigns and show the meaningful trust/policy differences.”

# Prior art (and why it’s insufficient)

- Uptane 2.1.0 and its deployment best practices document define a rich and practical standards surface.
- Rust has serious TUF substrate in `tuf`, `tough`, and `tuftool`, plus fresh SUIT-related parsing/validation substrate.
- But Rust still lacks a boring-default crate for **deployment policy locks + campaign replay + ECU verdict diffs + portable evidence bundles**.

# Design goals

1. **Deployment-first** — the value is in the configured system, not only the abstract standard.
2. **Role-aware** — delegations, thresholds, and repository relationships must remain visible.
3. **Replayable** — bundles must make “why it failed” portable.
4. **Layer-honest** — keep Uptane/TUF core and optional SUIT overlays clearly separated.
5. **Redaction-safe** — allow sharing update evidence without leaking full fleet or proprietary hardware details.

# MVP surface

- Minimal types: `UpdateLock`, `CampaignProfile`, `OtaBundle`, `EcuVerdict`, `RoleDiffFinding`
- Minimal functions:
  - `snapshot_metadata()`
  - `replay_campaign()`
  - `diff_campaigns()`
  - `write_bundle()`
- Feature flags:
  - `tuf`
  - `uptane`
  - `suit`
  - `redaction`

# Compatibility story

- MVP should target Uptane/TUF deployment evidence first.
- The crate should complement `tuf`, `tough`, `tuftool`, and SUIT parsers rather than replace them.
- SUIT integration should remain optional and explicitly scoped to constrained-device manifest surfaces.
- Real update installation mechanics should stay out of the core unless they are necessary for replay evidence.

# Conformance & fixtures

- Tiny metadata snapshots for expiration, delegation, threshold, and rollback scenarios.
- ECU-profile fixtures for hardware mismatch, target gating, and campaign-policy differences.
- Goldens for “same metadata, different replay time”, “same target, different delegation path”, and “same payload, rejected by policy”.
- Optional SUIT fixtures for manifest parsing and verification assumptions where relevant.

# Path to boring stability

- Stabilize the lockfile and replay-report schema before broadening device or transport coverage.
- Start with metadata/campaign evidence rather than full live-update orchestration.
- Use tiny public fixtures that exercise failure causes cleanly.
- Keep hardware- and vendor-specific adapters outside the stable core when possible.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 3/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 24/30**

# Minimum lovable MVP

A library and CLI that pin an Uptane/TUF deployment profile, replay one captured campaign against that profile, and emit a compact `*.otabundle.zip` with metadata snapshots, ECU verdicts, and semantic diffs.

# De-risk plan

1. Start with TUF/Uptane metadata replay before any live orchestration ideas.
2. Keep SUIT optional until the core policy and bundle format are stable.
3. Build around tiny metadata/campaign fixtures rather than full vehicle stacks.
4. Treat expiry, delegation, and policy explanation quality as the key adoption driver.

# Non-goals

- Not a new OTA backend.
- Not a firmware build system.
- Not a full vehicle digital-twin platform.
- Not a replacement for standards conformance programs or production key-management systems.

# Architecture & API sketch

```rust
pub struct UpdateLock {
    pub tuf_profile: String,
    pub uptane_profile: String,
    pub suit_profile: Option<String>,
}

pub fn replay_campaign(lock: &UpdateLock, input: &CampaignCapture) -> Result<CampaignReport>;
pub fn diff_campaigns(a: &CampaignReport, b: &CampaignReport) -> CampaignDiff;
```

Bundle draft: `profile.toml`, `metadata/`, `campaign.json`, `ecu-facts.json`, `report.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Treat metadata, manifests, and campaign captures as untrusted input.
- Support redaction of serial numbers, inventory topology, and proprietary hardware annotations.
- Record exact policy, replay time, and library versions in every bundle.
- Keep outputs deterministic enough for security review, certification rehearsal, and regression tracking.

# Maintenance & governance plan

- Keep the core centered on policy locks, replay reports, diffs, and bundle format.
- Version vendor-specific adapters and hardware profiles separately.
- Publish a small public fixture corpus around trust-chain and campaign-policy edge cases.
- Avoid turning the crate into a general-purpose updater.

# Milestones

## 0.1
- policy lockfile
- metadata snapshot ingestion
- single-campaign replay report

## 0.2
- campaign diffing
- redaction support
- optional SUIT profile support

## 1.0
- stable `*.otabundle.zip`
- public fixture corpus
- documented compatibility policy for supported Uptane/TUF surfaces

# Open questions

- What smallest deployment profile is enough to make replay evidence useful without dragging in full infrastructure?
- Which ECU facts belong in the stable core schema versus adapter-specific extensions?
- How should optional SUIT evidence be represented without making the crate feel IoT-only?

# Sources

- Uptane Standard for Design and Implementation 2.1.0: https://uptane.org/docs/2.1.0/standard/uptane-standard
- Uptane deployment best practices 2.1.0: https://uptane.org/docs/2.1.0/deployment/best-practices
- `tough`: https://crates.io/crates/tough
- `tuf`: https://crates.io/crates/tuf
- `tuftool`: https://crates.io/crates/tuftool
- `suit_validator`: https://crates.io/crates/suit_validator
- RFC 9124: https://datatracker.ietf.org/doc/html/rfc9124
