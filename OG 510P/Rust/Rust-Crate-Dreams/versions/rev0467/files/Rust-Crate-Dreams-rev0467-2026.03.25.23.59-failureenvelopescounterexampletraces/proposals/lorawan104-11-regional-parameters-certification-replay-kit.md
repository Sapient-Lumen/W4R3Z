---
id: P-0397
title: LoRaWAN 1.0.4 / 1.1 + Regional Parameters + Certification Replay Kit — region/profile locks, MAC-command receipts, and portable field-debug bundles
status: idea
domains: [iot, embedded, wireless, interoperability, validation, certification, networking]
last_reviewed: 2026-03-06
evidence:
  - https://resources.lora-alliance.org/technical-specifications/ts001-1-0-4-lorawan-l2-1-0-4-specification
  - https://resources.lora-alliance.org/technical-specifications/lorawan-specification-v1-1
  - https://resources.lora-alliance.org/technical-specifications/rp002-1-0-5-lorawan-regional-parameters
  - https://lora-alliance.org/lorawan-certification/
  - https://docs.rs/lorawan-device
  - https://docs.rs/lora-phy/latest/lora_phy/
---

# Problem

LoRaWAN is already a real deployed ecosystem, not a speculative one. The standards surface is layered: L2 protocol versions, regional parameter packs, certification requirements, device classes, MAC-command behavior, and the very practical seam between a device stack and a radio implementation.

Rust already has meaningful substrate here. `lorawan`, `lorawan-device`, and `lora-phy` cover message parsing, device-state handling, and radio-facing plumbing. But the painful failures still cluster at the boundaries between:

- **LoRaWAN 1.0.4 versus 1.1 assumptions**, especially around join/session/security behavior,
- **regional parameter packs and real deployed channel plans**,
- **what certification cases are trying to prove and what field logs actually show**,
- **MAC-command traces, ADR behavior, RX1/RX2 expectations, and fragmented vendor logs**,
- and **bug reports that still arrive as screenshots, hex dumps, and “works on network A but not network B.”**

The missing Rust contribution is not another end-device stack. It is a **replay and evidence kit** that turns LoRaWAN certification and field-debug work into boring, version-pinned artifacts.

# What it provides

- `lorawan.lock` — pins L2 version, regional-parameter version, class assumptions, join mode, crypto/profile expectations, and known network overlays.
- `mac-trace` IR — transport-neutral representation of uplinks, downlinks, MAC commands, joins, accepts, ADR changes, and receive-window expectations.
- `region-pack` — explicit channel-plan and data-rate overlay packs keyed to official regional-parameter revisions.
- `cert-case-map` — maps captured traces to certification requirements and expected findings.
- `cargo lorawan-evidence` — emits `*.lorawanbundle.zip` with lockfile, traces, findings, and replay notes.

# What the crate should provide other people

1. **A boring incident bundle for LoRaWAN interoperability failures**.
2. **Explicit version pinning** for L2 and regional-parameter assumptions.
3. **Certification-aware receipts** instead of lab-specific spreadsheets and screenshots.
4. **Explainable MAC-command and timing findings**.
5. **A reusable fixture corpus** for device authors, labs, and network integrators.

# Persona / who it’s for

- Embedded Rust teams building LoRaWAN end devices
- Certification/self-test labs and QA engineers
- Network/server integrators diagnosing join or ADR behavior
- Firmware teams maintaining regional variants of the same product

# Users & user stories

- **Device maintainer**: “Show me whether this failure is L2-version drift, regional-parameter drift, or a timing/mac-command bug.”
- **Certification engineer**: “Turn this trace into a reusable receipt keyed to the official requirement it passed or failed.”
- **Integrator**: “Explain why the same device works in EU868 but not US915 without diffing raw hex by hand.”
- **Sustaining engineer**: “Compare a field incident against the exact assumptions that passed pre-certification.”

# Prior art (and why it’s insufficient)

- The LoRa Alliance publishes the normative protocol, regional-parameter, and certification surfaces.
- Rust crates already implement meaningful pieces of the protocol stack.
- Vendors and labs have internal certification/debug flows.

What Rust still lacks is a **single coordination artifact** for version pinning, certification-case mapping, trace normalization, and replayable evidence.

# Design goals

1. **Layer-aware** — protocol version, regional parameters, and certification overlays must stay separate.
2. **Trace-first** — bundles should preserve what actually happened, not just final status.
3. **Field-to-lab continuity** — the same artifact should help both certification and production debugging.
4. **Embedded-friendly** — digest/summarized modes must work on constrained devices.
5. **Server-neutral** — do not assume one network server or vendor console.

# MVP surface

- Minimal types: `LorawanLock`, `MacTrace`, `RegionPack`, `CertificationFinding`, `LorawanBundle`
- Minimal functions:
  - `capture_trace()`
  - `normalize_mac_events()`
  - `map_certification_findings()`
  - `write_bundle()`
- Feature flags:
  - `class-a`
  - `class-b`
  - `class-c`
  - `certification`
  - `radio-timing`

# Compatibility story

- Works above existing crates like `lorawan-device` and `lora-phy` instead of replacing them.
- Can ingest over-the-air captures, device-side event logs, or lab-exported traces.
- Keeps regional overlays separate from base protocol semantics.
- Supports redacted/digest-only evidence when payload confidentiality matters.

# Conformance & fixtures

- Goldens for OTAA joins, receive-window timing, ADR state changes, RXParamSetup, LinkADRReq/Ans, and CFList handling.
- Region fixtures for EU868, US915, AU915, and AS923-family differences.
- Certification-case annotations that map trace segments to expected checks.
- Tiny failure corpora for DevNonce reuse, channel-mask misunderstandings, and malformed downlink handling.

# Path to boring stability

- Stabilize the lockfile and trace IR before broad adapter work.
- Treat regional packs as versioned overlays with explicit dates/revisions.
- Keep certification mapping readable and conservative.
- Delay broad network-server overlays until the core replay shape is stable.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A Rust library and CLI that pin LoRaWAN version/region assumptions, normalize MAC traces, map findings to certification expectations, and emit compact `*.lorawanbundle.zip` artifacts.

# De-risk plan

1. Start with Class A, 1.0.4/1.1, and a small set of regional packs.
2. Support offline traces before live capture adapters.
3. Make timing/receive-window evidence explicit and bounded.
4. Keep certification overlays separate from vendor/network overlays.

# Non-goals

- Not a new LoRaWAN network server.
- Not a new end-device stack.
- Not a radio HAL.
- Not a certification lab management system.

# Architecture & API sketch

```rust
pub struct LorawanLock {
    pub l2_version: String,
    pub regional_params: String,
    pub class_profile: String,
    pub overlay_packs: Vec<String>,
}

pub fn capture_trace(input: CaptureInput) -> Result<MacTrace>;
pub fn normalize_mac_events(trace: &MacTrace, lock: &LorawanLock) -> Result<LorawanBundle>;
pub fn map_certification_findings(bundle: &LorawanBundle) -> Vec<CertificationFinding>;
```

Bundle draft: `lorawan.lock`, `trace.json`, `region-pack.json`, `cert-map.json`, `findings.json`, `notes.md`.

# Security / safety model

- Default to metadata, MAC-command, and timing summaries over raw application payload retention.
- Support hashing/redacting join identifiers and payload bytes.
- Record which data was omitted so redaction is not confused with radio loss.
- Keep evidence deterministic enough for CI and support handoff.

# Maintenance & governance plan

- Version regional packs and certification overlays independently.
- Keep the core about receipts, not device runtime ownership.
- Publish a tiny public corpus of redacted traces and expected findings.
- Resist scope creep into full network simulation.

# Milestones

## 0.1
- `lorawan.lock`
- MAC-trace IR
- Class A trace normalization

## 0.2
- certification-case mapping
- regional packs
- public fixture corpus

## 1.0
- stable `*.lorawanbundle.zip`
- documented compatibility policy for L2/region overlays
- richer live-capture adapters

# Open questions

- How should roaming/network-specific behavior be represented without polluting the core lockfile?
- Which timing evidence is sufficient for useful replay on constrained devices?
- How much of certification mapping can be automated without embedding proprietary lab assumptions?

# Sources

- LoRaWAN L2 1.0.4 specification: https://resources.lora-alliance.org/technical-specifications/ts001-1-0-4-lorawan-l2-1-0-4-specification
- LoRaWAN 1.1 specification: https://resources.lora-alliance.org/technical-specifications/lorawan-specification-v1-1
- LoRaWAN Regional Parameters RP002-1.0.5: https://resources.lora-alliance.org/technical-specifications/rp002-1-0-5-lorawan-regional-parameters
- LoRaWAN Certification overview: https://lora-alliance.org/lorawan-certification/
- `lorawan-device`: https://docs.rs/lorawan-device
- `lora-phy`: https://docs.rs/crate/lora-phy/latest
