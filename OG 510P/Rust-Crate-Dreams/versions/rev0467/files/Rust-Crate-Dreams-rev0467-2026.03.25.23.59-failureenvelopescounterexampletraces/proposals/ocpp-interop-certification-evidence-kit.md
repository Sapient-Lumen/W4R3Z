---
id: P-0302
title: OCPP 2.1 / 2.0.1 Interop, Certification, and Evidence Kit — profile-aware CS↔CSMS replay with redactable charging incident bundles
status: idea
domains: [energy, ev, protocols, interoperability, testing]
last_reviewed: 2026-03-06
evidence:
  - https://openchargealliance.org/protocols/open-charge-point-protocol/
  - https://openchargealliance.org/ocpp-2-1-is-now-available/
  - https://openchargealliance.org/new-editions-of-the-ocpp-2-1-and-2-0-1-now-available/
---

# Problem

Rust now has meaningful OCPP substrate — `rust-ocpp`, `ocpp-client`, and related work — but the operational pain in EV charging is not just “parse the messages.” It is:

- drifting behavior across OCPP 1.6 / 2.0.1 / 2.1 deployments,
- charger-vendor versus CSMS-specific interpretation differences,
- security and certificate onboarding failures,
- smart-charging / device-management / reservation edge cases that only surface in the field,
- certification and support workflows that still depend on screenshots, logs, and hand-edited JSON.

OCPP 2.1 is now the latest version, and recent editions add certification profiles and test cases. That makes the missing Rust opportunity look less like “another type crate” and more like a **profile-aware interop/certification workbench**.

# What it provides

A crate/workspace that other people can use to make EV charging compatibility **boring, reproducible, and supportable**:

- `ocpp-canon` — canonical IR for OCPP WebSocket exchanges, transaction/device-management flows, and certificate events.
- `ocpp-profile` — declarative charger / CSMS / deployment profiles for supported functional blocks, version constraints, and tolerated deviations.
- `ocpp-replay` — deterministic replay of captured sessions against charger or CSMS adapters.
- `ocpp-fixtures` — certification-style scenarios for boot, authorization, transactions, smart charging, offline recovery, and security events.
- `ocpp-diff` — semantic diffs for message meaning, state progression, and profile mismatches.
- `cargo ocpp` — emit `*.ocppbundle.zip` bundles for incident exchange, certification rehearsal, and regression testing.

# What the crate should provide other people

1. **A stable incident artifact** for field debugging between charger vendors, CSMS vendors, and operators.
2. **A versioned profile layer** so real deployments can pin “our OCPP surface” instead of vaguely claiming protocol support.
3. **Replayable certification rehearsal** for vendors that want to fail in CI before they fail in a lab or parking lot.
4. **A realistic adapter model** so the kit composes with existing Rust OCPP implementations instead of replacing them.
5. **Redaction-first sharing** so operators can exchange evidence without leaking contract IDs, RFID identifiers, customer details, or full billing data.

# Users & user stories

- **Charge-point vendors**: “Replay the exact smart-charging sequence that failed at a customer site.”
- **CSMS teams**: “Show the first semantic divergence between our expected profile and a field charger’s actual behavior.”
- **Fleet / operator SRE teams**: “Ship one redacted bundle to the vendor instead of five incompatible log formats.”
- **Certification/pre-cert labs**: “Run repeatable scenario packs against multiple implementations.”

# Prior art (and why it’s insufficient)

- `rust-ocpp` and related client crates provide protocol data types and some transport flow, which is valuable substrate.
- The Open Charge Alliance publishes the standard, certification profiles, and test case material, which proves the need for conformance-oriented tooling.
- But Rust still lacks a default **capture → canonicalize → replay → diff → bundle** path for real deployments.

# Design goals

1. **Version-aware from day one** — OCPP 1.6, 2.0.1, and 2.1 need explicit boundaries and migration helpers.
2. **Scenario-first** — model operational flows, not isolated messages only.
3. **Deployment realism** — support lossy links, reconnects, clock skew, and offline recovery.
4. **Certification adjacency** — align with published profile/test-case structure where practical.
5. **Composable security** — certificate and authorization diagnostics should integrate without turning the crate into a PKI monolith.

# Non-goals

- Not a full CSMS product.
- Not a charger firmware framework.
- Not a billing or roaming platform.

# Architecture & API sketch

```rust
pub struct OcppBundleReport {
    pub protocol_version: String,
    pub profile_id: String,
    pub verdicts: Vec<Verdict>,
    pub divergences: Vec<Divergence>,
}

pub trait OcppEndpointAdapter {
    fn send(&mut self, msg: CanonicalOcppMessage) -> Result<(), Error>;
    fn poll(&mut self) -> Result<Vec<CanonicalOcppEvent>, Error>;
}

pub fn replay(bundle: &OcppBundle, endpoint: &mut dyn OcppEndpointAdapter) -> Result<OcppBundleReport, Error>;
```

Bundle draft: `profile.toml`, `session.jsonl`, `state-trace.json`, `cert-events.json`, `redaction-map.json`, `verdicts.json`, `notes.md`.

# Security / safety model

- Default redaction for id tokens, RFID values, EVSE/contract identifiers, locations, and customer-linked payloads.
- Limit capture sizes and replay resource usage.
- Separate raw secrets/key material from evidence bundles entirely.
- Preserve enough certificate metadata for diagnostics without shipping private keys.

# Maintenance & governance plan

- Keep the canonical session IR additive and narrow.
- Publish a fixture-contribution guide aligned to OCPP functional blocks.
- Maintain first-party adapters only for the most active Rust OCPP crates.
- Record exact edition / errata assumptions in every profile pack.

# Milestones

## 0.1
- Canonical exchange IR
- Version/profile descriptors
- Redaction/tokenization defaults

## 0.2
- Replay harness
- Smart-charging + transaction scenario packs
- `cargo ocpp diff`

## 1.0
- Stable `*.ocppbundle.zip`
- Certification-rehearsal fixture packs
- Clear migration aids between 2.0.1 and 2.1 profiles

# Open questions

- How much of OCA certification semantics can be represented cleanly without copying the lab process itself?
- Should migration helpers between 2.0.1 and 2.1 live in core or companion crates?
- What is the right canonical state model for charger-side versus CSMS-side replay?

# Sources

- Open Charge Alliance OCPP overview: https://openchargealliance.org/protocols/open-charge-point-protocol/
- OCPP 2.0.1 overview: https://openchargealliance.org/protocols/ocpp-protocols/ocpp-2-0-1/
- OCPP 2.1 release: https://openchargealliance.org/ocpp-2-1-is-now-available/
- OCPP 2.1 and 2.0.1 new editions incl. test cases: https://openchargealliance.org/new-editions-of-the-ocpp-2-1-and-2-0-1-now-available/
- Rust crates: https://crates.io/crates/rust-ocpp ; https://crates.io/crates/ocpp-client
