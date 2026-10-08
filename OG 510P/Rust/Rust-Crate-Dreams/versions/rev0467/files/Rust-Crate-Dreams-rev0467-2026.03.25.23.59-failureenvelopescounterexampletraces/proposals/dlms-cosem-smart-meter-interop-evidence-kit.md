---
id: P-0310
title: DLMS/COSEM Smart Meter Interop & Evidence Kit — profile-pinned meter dialogues, object-model diagnostics, and utility-safe exchange bundles
status: idea
domains: [energy, utilities, smart-grid, interoperability, testing]
last_reviewed: 2026-03-06
evidence:
  - https://www.dlms.com/
  - https://www.dlms.com/core-specifications/
  - https://crates.io/crates/dlms_cosem
---

# Problem

DLMS/COSEM is central to smart-meter interoperability, but the painful work is not just decoding a few frames. Operators and vendors need to reason about:

- association setup and security/profile negotiation,
- object-list/model expectations,
- vendor and utility profile drift,
- reproducible meter/head-end failures that can be shared safely across organizations.

Rust has at least some substrate (`dlms_cosem`, smart-meter-oriented work), but no clear default for **canonical dialogues, profile pinning, replay, and evidence shipping**.

# What it provides

- `dlms-profile` — utility/vendor/security profile packs for interface classes, object lists, auth/security expectations, and transport assumptions.
- `dlms-canon` — canonical IR for associations, APDUs, object access, and verdict-relevant state transitions.
- `dlms-replay` — deterministic replay against simulators, lab meters, and head-end adapters.
- `dlms-diff` — semantic diffs for association failures, attribute mismatches, and object-model drift.
- `dlms-fixtures` — scenario packs for onboarding, readout, clock sync, disconnect/reconnect, and firmware-related compatibility checks.
- `cargo dlms` — emit `*.dlmsbundle.zip` for vendor escalation, lab repro, and acceptance testing.

# What the crate should provide other people

1. **A shared dialogue artifact** for meter↔head-end debugging.
2. **Utility-profile lockfiles** so procurement and rollout expectations are machine-readable.
3. **Explainable object-model diffs** when the meter and head-end disagree about the same device.
4. **Replayable acceptance tests** for staging labs and vendor qualification.
5. **Redacted bundles** that preserve evidence while limiting customer-sensitive metering data.

# Users & user stories

- **Utility integration teams**: “Replay the exact association and readout sequence that failed after a firmware update.”
- **Meter vendors**: “Compare our object-list/profile behavior against the utility’s expected pack.”
- **Lab / certification teams**: “Generate acceptance evidence without hand-annotating protocol traces.”
- **Field support teams**: “Share one bundle with the vendor instead of proprietary logs and screenshots.”

# Prior art (and why it’s insufficient)

- DLMS UA provides the canonical spec context and interoperability framing.
- Rust parsing libraries prove the ecosystem can read pieces of the protocol.
- The missing leverage is the **scenario/evidence layer** that turns field failures into portable, explainable artifacts.

# Design goals

1. **Profile-aware** — utility and vendor assumptions must be explicit.
2. **Object-model centric** — interface classes and attributes need first-class representation.
3. **Transport-agnostic core** — support multiple transport/adaptation environments over time.
4. **Field-safe sharing** — bundles should default to redacted meter data and bounded captures.
5. **Lab-friendly replay** — work with simulators and staged hardware.

# Non-goals

- Not a full head-end system.
- Not a meter fleet management platform.
- Not a billing engine.

# Architecture & API sketch

```rust
pub struct DlmsReport {
    pub profile_id: String,
    pub verdicts: Vec<Verdict>,
    pub object_diffs: Vec<ObjectDiff>,
    pub divergences: Vec<Divergence>,
}

pub fn replay(bundle: &DlmsBundle, adapter: &mut dyn DlmsEndpointAdapter) -> Result<DlmsReport, Error>;
```

Bundle draft: `profile.toml`, `session.jsonl`, `object-model.json`, `security-events.json`, `redaction-map.json`, `verdicts.json`, `notes.md`.

# Security / safety model

- Default redaction for customer-linked identifiers and sensitive consumption values.
- Separate security metadata from secret material.
- Bound replay attempts and capture sizes for field devices.
- Treat parsers and object-model handling as hostile-input surfaces.

# Maintenance & governance plan

- Keep canonical IR additive and narrow.
- Publish fixture packs for common utility acceptance stories.
- Track exact DLMS UA/profile assumptions per bundle.
- Prefer adapter-wrap approaches over attempts to become a monolithic meter stack.

# Milestones

## 0.1
- Canonical dialogue IR
- Profile packs and object-model summaries
- Redacted bundle format

## 0.2
- Replay harness
- Association/object-access scenario packs
- `cargo dlms diff`

## 1.0
- Stable `*.dlmsbundle.zip`
- Utility acceptance packs
- Cross-vendor object-model diagnostics

# Open questions

- Which profile differences deserve first-class schema rather than free-form metadata?
- How much simulator support belongs in core?
- What is the smallest useful field bundle that still supports vendor debugging?

# Sources

- DLMS UA overview: https://www.dlms.com/
- DLMS UA core specifications overview: https://www.dlms.com/core-specifications/
- `dlms_cosem` crate: https://crates.io/crates/dlms_cosem
- `smart_meter` crate: https://crates.io/crates/smart_meter
