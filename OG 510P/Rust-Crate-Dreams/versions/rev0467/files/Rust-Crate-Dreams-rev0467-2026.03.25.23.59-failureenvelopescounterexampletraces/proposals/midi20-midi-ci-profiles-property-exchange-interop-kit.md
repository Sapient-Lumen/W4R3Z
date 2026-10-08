---
id: P-0398
title: MIDI 2.0 + MIDI-CI + Profiles + Property Exchange Interop Kit — UMP traces, capability-negotiation receipts, and profile/property conformance bundles
status: idea
domains: [audio, music, protocol, interoperability, tooling, validation]
last_reviewed: 2026-03-06
evidence:
  - https://amei.or.jp/midistandardcommittee/MIDI2.0/MIDI2.0-DOCS/M2-100-U_v1-1_MIDI_2-0_Specification_Overview.pdf
  - https://midi.org/details-about-midi-2-0-midi-ci-profiles-and-property-exchange-updated-june-2023
  - https://midi.org/midi-2-0-property-exchange
  - https://docs.rs/midi2
  - https://docs.rs/midi20
  - https://github.com/m-hilgendorf/midi20
---

# Problem

MIDI 2.0 is not just “higher-resolution note messages.” The real compatibility surface spans Universal MIDI Packets, protocol negotiation, function blocks, MIDI-CI, profiles, and Property Exchange. Once devices start discovering capabilities and exchanging JSON properties, interoperability failures stop looking like simple byte-level parse bugs.

Rust already has meaningful substrate. `midi2` and `midi20` cover important parts of MIDI 2.0/UMP, and the ecosystem is active enough that missing pieces are now visible rather than hypothetical. But the painful failures still happen at the seam between:

- **UMP parsing and actual device-level capability negotiation**,
- **MIDI-CI discovery/identification and the profile state a peer really enables**,
- **Property Exchange resource schemas and what devices actually return**,
- **transport-specific observations (USB, virtual endpoints, RTP/other bridges) and the same logical session**,
- and **bug reports that still amount to ad hoc sysex logs, vendor apps, or “this synth works in host A but not host B.”**

The missing Rust contribution is not another DAW toolkit. It is an **interop kit** for capability locks, UMP/MIDI-CI receipts, profile/property evidence, and deterministic fixture playback.

# What it provides

- `midi2.lock` — pins UMP revision assumptions, MIDI-CI features, profile packs, Property Exchange resources, and transport notes.
- `ump-trace` IR — transport-neutral session model for discovery, negotiation, profile changes, and property GET/SET flows.
- `ci-receipt` — capability-negotiation receipt with MUID relationships, function blocks, and supported profile/property surfaces.
- `profile-pack` — explicit profile and capability overlays keyed to profile/common-rules revisions.
- `cargo midi2-evidence` — emits `*.midi2bundle.zip` with traces, findings, and notes.

# What the crate should provide other people

1. **A boring receipt for MIDI 2.0 compatibility bugs**.
2. **Capability and profile pinning** instead of relying on vendor memory.
3. **Explainable Property Exchange findings** around missing, malformed, or partial resources.
4. **A stable fixture corpus** for hosts, devices, and protocol libraries.
5. **A path for Rust audio/device authors to debug interoperability without writing a full vendor workbench.**

# Persona / who it’s for

- Rust audio/MIDI library authors
- Embedded developers building MIDI 2.0-capable hardware/firmware
- Host/plug-in/device integrators testing across platforms
- QA engineers and maintainers debugging interoperability regressions

# Users & user stories

- **Device author**: “Show me whether the failure is UMP framing, MIDI-CI negotiation, profile activation, or property-resource semantics.”
- **Host maintainer**: “Capture one portable receipt for the session instead of shipping raw sysex and screenshots.”
- **Library maintainer**: “Pin the capability surface my crate supports and compare it across releases.”
- **QA engineer**: “Replay a tiny corpus of profile/property negotiation cases against multiple devices.”

# Prior art (and why it’s insufficient)

- The MIDI Association has published the core MIDI 2.0, profile, and Property Exchange materials.
- Rust crates already expose strong message-level types.
- Vendor/device tools exist, but they are fragmented and not portable.

What Rust still lacks is a **single evidence-grade coordination layer** above message parsing: lockfiles, capability receipts, property-resource fixtures, and explainable diffs.

# Design goals

1. **Negotiation-first** — interoperability is about what peers agree to, not just what bytes decode.
2. **Transport-neutral** — USB/virtual/network transports should map into one comparable session IR.
3. **Profile/property-aware** — these cannot be bolted on as opaque blobs.
4. **Fixture-friendly** — tiny public corpora should be easy to share and replay.
5. **Library-adapter, not host-platform rewrite** — stay above existing Rust message crates.

# MVP surface

- Minimal types: `Midi2Lock`, `UmpTrace`, `CapabilityReceipt`, `ProfileFinding`, `PropertyFinding`, `Midi2Bundle`
- Minimal functions:
  - `capture_session()`
  - `normalize_ump_trace()`
  - `diff_capabilities()`
  - `write_bundle()`
- Feature flags:
  - `ump`
  - `midi-ci`
  - `profiles`
  - `property-exchange`
  - `transport-adapters`

# Compatibility story

- Works above `midi2`, `midi20`, and future transport adapters.
- Supports offline capture from sysex/UMP logs before live host integration.
- Treats transport adapters as optional overlays, not the semantic core.
- Keeps vendor-private properties and identifiers redactable.

# Conformance & fixtures

- Goldens for protocol negotiation, profile enable/disable, Profile Details Inquiry, and Property Exchange GET/SET flows.
- Tiny fixtures for MUID collisions, malformed resource bodies, unsupported profiles, and partial capability disclosure.
- Public fixture bundles that separate message capture from semantic findings.
- Optional digest-only mode for proprietary device properties.

# Path to boring stability

- Stabilize the lockfile and session IR before chasing every transport.
- Keep the first release focused on negotiation/profile/property receipts.
- Version profile packs and property-resource schemas explicitly.
- Delay platform-specific host integrations until the neutral bundle shape is solid.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 3/5
- Adoptability: 3/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 24/30**

# Minimum lovable MVP

A Rust library and CLI that capture a MIDI 2.0 / MIDI-CI session, pin profile/property assumptions, compute capability findings, and emit compact `*.midi2bundle.zip` artifacts.

# De-risk plan

1. Start with offline UMP + MIDI-CI transcript support.
2. Add profiles and Property Exchange fixtures next.
3. Keep transport adapters and platform APIs out of the core crate.
4. Allow digest-only evidence for proprietary resources.

# Non-goals

- Not a DAW.
- Not a full device editor/librarian.
- Not a USB stack.
- Not a generic audio framework.

# Architecture & API sketch

```rust
pub struct Midi2Lock {
    pub ump_revision: String,
    pub midi_ci_revision: String,
    pub profile_packs: Vec<String>,
    pub property_resources: Vec<String>,
}

pub fn capture_session(input: CaptureInput) -> Result<UmpTrace>;
pub fn normalize_ump_trace(trace: &UmpTrace, lock: &Midi2Lock) -> Result<Midi2Bundle>;
pub fn diff_capabilities(bundle: &Midi2Bundle) -> Vec<CapabilityReceipt>;
```

Bundle draft: `midi2.lock`, `trace.json`, `capabilities.json`, `profiles.json`, `properties.json`, `findings.json`, `notes.md`.

# Security / safety model

- Support redaction of vendor/product identifiers and proprietary property payloads.
- Preserve message ordering and negotiation semantics even when payload bodies are hashed.
- Keep public fixtures tiny and deterministic.
- Make transport-specific metadata explicit rather than implicit.

# Maintenance & governance plan

- Keep the core about receipts, diffs, and fixtures.
- Version profile packs and Property Exchange resources independently.
- Publish a small public corpus that exercises negotiation/profile/property edges.
- Resist drift into full-featured host/device-control software.

# Milestones

## 0.1
- `midi2.lock`
- UMP/MIDI-CI session IR
- capability receipt prototype

## 0.2
- profile/property fixtures
- redaction support
- public corpus

## 1.0
- stable `*.midi2bundle.zip`
- compatibility policy for profile/resource overlays
- broader transport adapters

# Open questions

- Which property resources should be treated as stable public corpora versus device-private overlays?
- How much of MIDI-CI state needs to be explicit in the lockfile to make diffs trustworthy?
- What is the smallest credible transport-neutral session model across USB and non-USB paths?

# Sources

- MIDI 2.0 Specification Overview v1.1: https://amei.or.jp/midistandardcommittee/MIDI2.0/MIDI2.0-DOCS/M2-100-U_v1-1_MIDI_2-0_Specification_Overview.pdf
- MIDI 2.0 / MIDI-CI / Profiles / Property Exchange overview: https://midi.org/details-about-midi-2-0-midi-ci-profiles-and-property-exchange-updated-june-2023
- Property Exchange overview: https://midi.org/midi-2-0-property-exchange
- `midi2`: https://docs.rs/midi2
- `midi20`: https://docs.rs/midi20
- `midi20` repository (noting missing MIDI-CI / Property Exchange work): https://github.com/m-hilgendorf/midi20
