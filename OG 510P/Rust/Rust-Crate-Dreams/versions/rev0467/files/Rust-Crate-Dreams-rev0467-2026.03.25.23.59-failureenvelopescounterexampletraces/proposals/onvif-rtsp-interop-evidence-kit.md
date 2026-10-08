---
id: P-0309
title: ONVIF + RTSP Interop & Evidence Kit — profile-aware camera discovery, streaming diagnostics, and reproducible surveillance bundles
status: idea
domains: [video, cameras, physical-security, interoperability, testing]
last_reviewed: 2026-03-06
evidence:
  - https://www.onvif.org/
  - https://www.onvif.org/profiles/profile-s/
  - https://www.onvif.org/profiles/conformance/device-test-2/
---

# Problem

The physical-security world is full of **almost-compatible cameras, NVRs, discovery flows, PTZ quirks, media-profile mismatches, broken timestamps, and RTSP edge cases**. Rust has real camera-facing substrate now — `retina`, `onvif-cam-rs`, `onvif-rs`, `gst-plugin-onvif`, and RTSP work — but what is still missing is the operational layer that makes compatibility boring:

- pinning which ONVIF profiles/features a device or client actually supports,
- reproducing discovery + control + streaming issues across devices,
- diffing capability claims against observed RTSP/media behavior,
- shipping one redactable support bundle instead of packet captures plus screenshots.

The worthy crate is a **profile-aware interop and evidence kit**, not just another media client.

# What it provides

- `onvif-profile` — device/client capability descriptors keyed to ONVIF profiles and tolerated deviations.
- `onvif-canon` — canonical IR for discovery, device-management, media, PTZ, event, and replay interactions.
- `rtsp-check` — normalize RTSP negotiation, stream setup, timing, and keepalive behavior.
- `camera-replay` — deterministic scenario replay across real cameras, simulators, and NVR-side adapters.
- `camera-diff` — semantic diffs between claimed profile support and observed behavior.
- `cargo onvif` — emit `*.cambundle.zip` for field debugging, procurement bake-offs, and CI regression suites.

# What the crate should provide other people

1. **An evidence format for camera compatibility** that survives vendor boundaries.
2. **Profile-aware procurement/testing** so teams can compare devices against real use cases, not just spec sheets.
3. **A canonical troubleshooting path** for discovery, auth, media-profile, PTZ, and timestamp drift failures.
4. **Adapter hooks** for existing Rust ONVIF/RTSP crates and GStreamer-based stacks.
5. **Redaction and privacy controls** for site addresses, credentials, and sensitive scene metadata.

# Users & user stories

- **NVR / VMS teams**: “Replay the exact camera session that broke recording after reconnect.”
- **Device vendors**: “Compare our profile claims with observed ONVIF and RTSP behavior in a repeatable lab run.”
- **Physical-security integrators**: “Generate a compatibility matrix from real scenario bundles before a rollout.”
- **Support/SRE teams**: “Ship one redacted bundle to the vendor instead of ad hoc packet captures.”

# Prior art (and why it’s insufficient)

- ONVIF publishes profiles and conformance/device test specifications, which strongly suggests a conformance-first Rust layer could align to real industry practice.
- Existing Rust crates are useful substrate, but do not provide a shared **capture → canonicalize → replay → diff → bundle** workflow.
- RTSP behavior in the field is famously quirky; transport success alone does not prove usable interoperability.

# Design goals

1. **Profile-first** — device claims and observed capability must be comparable.
2. **Media-realistic** — timing, keepalives, reconnects, and stream peculiarities matter.
3. **Hardware-friendly** — support physical cameras, simulators, and recorded traces.
4. **Operator-usable** — reports should answer “what failed and what to try next?”.
5. **Privacy-preserving** — no default shipping of credentials or full scene payloads.

# Non-goals

- Not a general video analytics stack.
- Not a full VMS/NVR product.
- Not a transcoding framework.

# Architecture & API sketch

```rust
pub struct CameraInteropReport {
    pub profile_id: String,
    pub verdicts: Vec<Verdict>,
    pub stream_findings: Vec<StreamFinding>,
    pub divergences: Vec<Divergence>,
}

pub trait CameraAdapter {
    fn probe(&mut self, scenario: ProbeScenario) -> Result<ProbeTrace, Error>;
}
```

Bundle draft: `profile.toml`, `discovery.json`, `control.jsonl`, `rtsp.jsonl`, `media-summary.json`, `redaction-map.json`, `verdicts.json`, `notes.md`.

# Security / safety model

- Default redaction for credentials, IPs/hostnames, and deployment-site metadata.
- Allow media payload omission while preserving timing and stream-shape evidence.
- Bound capture size and replay durations.
- Treat camera firmware behavior as hostile input.

# Maintenance & governance plan

- Keep core bundle format independent of any one vendor.
- Start with Profile S-oriented scenarios, then expand cautiously.
- Publish fixture packs for discovery, auth, stream setup, reconnect, PTZ, and clock/timestamp edge cases.
- Track exact ONVIF profile and test-tool assumptions in profiles.

# Milestones

## 0.1
- Discovery + media-profile probe IR
- RTSP timing/check utilities
- Redacted bundle writer

## 0.2
- Replay harness and compatibility matrix generator
- PTZ and reconnect scenario packs
- `cargo onvif doctor`

## 1.0
- Stable `*.cambundle.zip`
- Claimed-vs-observed profile diffs
- Procurement/regression fixture packs

# Open questions

- How much media payload needs to be retained for useful debugging?
- Should ONVIF eventing land in the MVP or a follow-on crate?
- What is the thinnest adapter boundary that still supports GStreamer and pure-Rust stacks?

# Sources

- ONVIF home: https://www.onvif.org/
- ONVIF Profile S: https://www.onvif.org/profiles/profile-s/
- ONVIF device test specifications: https://www.onvif.org/profiles/conformance/device-test-2/
- `retina` crate: https://crates.io/crates/retina
- `onvif-cam-rs` crate: https://crates.io/crates/onvif-cam-rs
