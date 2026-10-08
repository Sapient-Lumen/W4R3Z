---
id: P-0306
title: OpenADR 3.0 Demand-Response Interop & Evidence Kit — VEN↔VTN profile packs, scenario replay, and grid-event repro bundles
status: idea
domains: [energy, grid, protocols, interoperability, operations]
last_reviewed: 2026-03-06
evidence:
  - https://www.openadr.org/openadr-3-0
  - https://lfenergy.org/projects/openleadr/
  - https://github.com/OpenLEADR/openleadr-rs
---

# Problem

OpenADR is one of the standards that matters precisely when conditions are stressful: dynamic pricing, demand response, curtailment, and flexibility events. Rust now has notable momentum through LF Energy’s OpenLEADR Rust implementation (`openleadr-wire`, `openleadr-client`, `openleadr-vtn`) and the broader OpenLEADR project. But the high-value missing layer is still:

- reproducible VEN↔VTN scenario replay,
- profile-aware diagnostics for supported programs and payloads,
- event lifecycle and acknowledgement evidence,
- safe exchange of incident bundles between utilities, aggregators, and device/platform vendors,
- CI-grade conformance/certification rehearsal.

So the epic opportunity is not “start OpenADR from scratch.” It is to build the **interop and evidence layer** that makes emerging Rust implementations operationally trustworthy.

# What it provides

- `openadr-profile` — declarative VEN/VTN capability, program, and payload profiles.
- `openadr-canon` — canonical IR for event publication, acknowledgement, report exchanges, and state transitions.
- `openadr-replay` — deterministic scenario replay across client and server adapters.
- `openadr-fixtures` — scenario packs for registration, report delivery, event opt-in/out, timing windows, and error cases.
- `openadr-diff` — semantic diffs for event handling, schedules, report semantics, and profile mismatches.
- `cargo openadr` — emit `*.oadrbundle.zip` artifacts for integration testing and field incident exchange.

# What the crate should provide other people

1. **A neutral scenario language** for demand-response workflows.
2. **Profile pinning** so utilities, aggregators, and device vendors can state what they actually support.
3. **Evidence bundles** that capture event timing and verdicts instead of vague prose about missed DR events.
4. **Adapters over existing Rust implementations** rather than a winner-take-all rewrite.
5. **Operational diagnostics** that map behavior to schedules, event windows, and acknowledgement semantics.

# Users & user stories

- **Utilities / aggregators**: “Replay the event sequence that a fleet mishandled during yesterday’s curtailment.”
- **Device and gateway vendors**: “Verify that our VEN behavior matches the VTN profile before field rollout.”
- **Grid software teams**: “Diff two VTN implementations or two VEN builds using the same scenario pack.”
- **Support engineers**: “Send one bundle with redacted event/report evidence instead of raw logs.”

# Prior art (and why it’s insufficient)

- The OpenADR Alliance defines the standard and certification context.
- LF Energy OpenLEADR and the Rust crates prove that protocol substrate is becoming real.
- But the ecosystem still lacks a default **capture/replay/diff/bundle** workflow for actual OpenADR operations.

# Design goals

1. **Scenario and timing aware** — event windows and acknowledgements are first-class.
2. **Profile-as-code** — supported programs, reports, and capabilities must be versioned.
3. **VEN/VTN symmetry** — test both sides using the same core IR.
4. **Field-safe bundles** — redact customer/site identifiers and operationally sensitive metadata.
5. **Alignment with certification direction** — remain useful for rehearsal without trying to impersonate the entire formal program.

# Non-goals

- Not an energy market platform.
- Not a DER optimizer.
- Not a full utility operations product.

# Architecture & API sketch

```rust
pub struct OpenAdrReport {
    pub profile_id: String,
    pub event_timeline: Vec<Event>,
    pub verdicts: Vec<Verdict>,
}

pub trait OpenAdrEndpoint {
    fn request(&mut self, req: CanonicalOpenAdrRequest) -> Result<CanonicalOpenAdrResponse, Error>;
}

pub fn replay(bundle: &OpenAdrBundle, endpoint: &mut dyn OpenAdrEndpoint) -> Result<OpenAdrReport, Error>;
```

Bundle draft: `profile.toml`, `timeline.jsonl`, `events.json`, `reports.json`, `redaction-map.json`, `verdicts.json`, `notes.md`.

# Security / safety model

- Default redaction for site/customer identifiers, utility account references, and program metadata not needed for debugging.
- Treat wire payloads and external callbacks as hostile input.
- Support bounded-time simulation of schedules and timing windows.

# Maintenance & governance plan

- Keep canonical IR separate from specific VEN/VTN adapters.
- Let utilities or projects publish profile packs independently from the core crate.
- Record exact OpenADR version/profile assumptions in every fixture set.

# Milestones

## 0.1
- Canonical event/report IR
- Profile format
- Basic replay harness

## 0.2
- Scenario packs for common DR flows
- Timing-aware diffs
- `cargo openadr replay`

## 1.0
- Stable `*.oadrbundle.zip`
- Cross-implementation scenario matrices
- CI-friendly pre-cert and incident workflows

# Open questions

- Which certification-adjacent scenario families deserve first-class support?
- How much time simulation should be embedded in core versus companion crates?
- What is the smallest useful profile language for real deployments?

# Sources

- OpenADR 3.0 overview: https://www.openadr.org/openadr-3-0
- LF Energy OpenLEADR project: https://lfenergy.org/projects/openleadr/
- OpenLEADR Rust implementation: https://github.com/OpenLEADR/openleadr-rs
- Rust crates: https://crates.io/crates/openleadr-wire ; https://crates.io/crates/openleadr-client ; https://lib.rs/crates/openleadr-vtn
