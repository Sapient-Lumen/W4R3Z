---
id: P-0364
title: HL7 v2.x + MLLP + Message Profile Conformance & Replay Kit — ACK semantics, profile locks, and shareable hospital-interface bug bundles
status: idea
domains: [healthcare, messaging, standards, interoperability, validation, tooling]
last_reviewed: 2026-03-06
evidence:
  - https://www.hl7.eu/refactored/transport01mllp.html
  - https://www.hl7.eu/refactored/profile.html
  - https://www.hl7.eu/HL7v2x/v282/std282/ch02b.html
  - https://docs.rs/rumtk-hl7-v2/latest/rumtk_hl7_v2/hl7_v2_mllp/index.html
  - https://docs.rs/mllp-rs/
  - https://crates.io/crates/rumtk-hl7-v2
---

# Problem

Rust now has enough HL7 v2 and MLLP substrate to parse and transport messages, but the real interoperability failures still happen at the seam between:

- site-specific message-profile expectations,
- MLLP framing and ACK/commit-ACK behavior,
- character-set and encoding assumptions,
- table/value-set and optionality/cardinality drift,
- and bug reports that arrive as screenshots or logs instead of portable failing cases.

The missing Rust contribution is not another interface engine. It is a **profile-and-replay workbench** that makes HL7 v2 failures small, reproducible, and discussable across vendors and hospital teams.

# What it provides

- `profile-lock` — lockfiles pinning HL7 version, message structure, trigger event, profile constraints, MLLP/ACK semantics, charset, and local table overlays.
- `hl7-ir` — a neutral IR for parsed messages, normalized ACK outcomes, profile findings, and transport transcripts.
- `ack-replay` — replay for MLLP exchanges with timing, framing, resend, and commit/application ACK distinctions.
- `hl7-diff` — semantic diffs such as “same message, different cardinality interpretation” or “transport success but profile failure”.
- `cargo hl7-evidence` — emits `*.hl7bundle.zip` with profile locks, redacted messages, normalized transcripts, and explainable findings.

# What the crate should provide other people

1. **A boring default artifact for hospital-interface bugs**.
2. **Pinned profile and transport expectations** that survive interface-engine and vendor upgrades.
3. **Normalized ACK and ERR diagnostics** instead of ad hoc log interpretation.
4. **Replayable MLLP failures** for CI and vendor tickets.
5. **A bridge from Rust HL7 parser/transport crates to evidence-grade interoperability workflows**.

# Persona / who it’s for

- Hospital integration teams
- HL7 interface-engine and middleware authors
- Vendors maintaining HL7 v2 device or EHR integrations
- Teams migrating older integration logic into Rust services

# Users & user stories

- **Interface analyst**: “Tell me whether this is a framing issue, a profile violation, or an application-level ACK problem.”
- **Vendor maintainer**: “Replay the exact failing exchange and compare our ACK behavior to the working site.”
- **Migration team**: “Lock the message profile we actually support before replacing a legacy engine.”
- **Support engineer**: “Produce a redacted issue bundle instead of emailing raw PHI-laden logs.”

# Prior art (and why it’s insufficient)

- HL7 v2 documentation already covers conformance/profile concepts and MLLP framing behavior.
- Rust has real substrate in `rumtk-hl7-v2` and `mllp-rs`.
- But there is still no boring-default Rust crate for **profile locks + MLLP replay + normalized ACK findings + portable evidence bundles**.

# Design goals

1. **Profile-first** — model the contract that real interface teams debug.
2. **Transport-aware** — distinguish framing/transport failures from semantic/profile failures.
3. **Redaction-first** — make bundles safe enough for operational sharing.
4. **Version-explicit** — pin the exact HL7 version and local overlay assumptions.
5. **Message-small** — diagnostics should get sharper as the bundle gets smaller.

# MVP surface

- Minimal types: `ProfileLock`, `Hl7Bundle`, `AckFinding`, `ProfileFinding`, `TranscriptDiffFinding`
- Minimal functions:
  - `normalize_message()`
  - `validate_against_profile()`
  - `replay_mllp_exchange()`
  - `diff_ack_reports()`
  - `write_bundle()`
- Feature flags:
  - `mllp`
  - `profiles`
  - `tables`
  - `redaction`

# Compatibility story

- MVP should target common ER7 + MLLP workflows with explicit room for local overlays.
- The crate should complement parser and transport crates rather than replace them.
- Site-specific table/profile packs can live outside the core lockfile/report schemas.
- ACK semantics must remain explicit enough to support both simple and richer deployments.

# Conformance & fixtures

- Tiny ADT, ORM, ORU, and ACK message fixtures.
- Cases for framing errors, bad field cardinality, table/code mismatches, and ACK timing/semantics drift.
- Goldens for “transport success but application reject” and “profile mismatch but same trigger event”.
- Redaction tests for names, identifiers, and free-text segments.

# Path to boring stability

- Stabilize the profile lockfile and transcript bundle before broadening message coverage.
- Start with ER7 + MLLP rather than every encoding/transport combination.
- Keep findings phrased for interface analysts, not protocol purists alone.
- Build a public corpus from tiny messages and synthetic transcripts.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 25/30**

# Minimum lovable MVP

A library and CLI that pin a message profile, replay an MLLP exchange, validate the message against the locked profile, and emit a compact `*.hl7bundle.zip` with normalized ACK and profile findings.

# De-risk plan

1. Start with ER7 + MLLP and a narrow set of message families.
2. Treat redaction and ACK normalization as the hardest early UX problems.
3. Keep local-table overlays optional in the initial release.
4. Use tiny synthetic fixtures before production-derived corpora.

# Non-goals

- Not a replacement for hospital interface engines.
- Not a full EHR integration platform.
- Not a clinical terminology server.
- Not a generic healthcare event bus.

# Architecture & API sketch

```rust
pub struct ProfileLock {
    pub hl7_version: String,
    pub message_type: String,
    pub ack_mode: AckMode,
}

pub fn validate_against_profile(lock: &ProfileLock, message: &NormalizedMessage) -> Result<Hl7Report>;
pub fn replay_mllp_exchange(lock: &ProfileLock, transcript: &[u8]) -> Result<Hl7Report>;
```

Bundle draft: `profile.toml`, `message.hl7`, `transcript.bin`, `report.json`, `ack-report.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Treat messages and transcripts as untrusted input.
- Support PHI-aware redaction of identifiers, names, and free-text payloads.
- Record exact profile/version assumptions and local overlays.
- Keep bundles deterministic enough for tickets, regressions, and incident review.

# Maintenance & governance plan

- Keep the core centered on profile locks, normalized findings, diffs, and bundle format.
- Version transport and site-specific adapters separately.
- Publish a small public corpus around common ACK/profile failure modes.
- Avoid locking the crate to one integration engine or one EHR vendor.

# Milestones

## 0.1
- ER7 normalization
- profile lockfile
- MLLP replay report

## 0.2
- semantic diffs
- optional local-table overlays
- redaction support

## 1.0
- stable `*.hl7bundle.zip`
- public fixture corpus
- documented compatibility policy for supported HL7 v2 families

# Open questions

- Which minimum profile surface is enough for a compelling first release?
- How much ACK/ERR detail belongs in the stable core report schema?
- What is the smallest useful redacted transcript that still resolves real support incidents?

# Sources

- HL7 v2+ MLLP transport page: https://www.hl7.eu/refactored/transport01mllp.html
- HL7 v2+ conformance/profile page: https://www.hl7.eu/refactored/profile.html
- HL7 v2.8.2 chapter 2B: https://www.hl7.eu/HL7v2x/v282/std282/ch02b.html
- `rumtk-hl7-v2` MLLP docs: https://docs.rs/rumtk-hl7-v2/latest/rumtk_hl7_v2/hl7_v2_mllp/index.html
- `mllp-rs`: https://docs.rs/mllp-rs/
- `rumtk-hl7-v2`: https://crates.io/crates/rumtk-hl7-v2
