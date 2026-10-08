---
id: P-0419
title: SigMF + VITA-49 + SoapySDR Replay & Evidence Kit — RF capture locks, transport receipts, and device-portable signal bundles
status: idea
domains: [sdr, radio, signals, metadata, interoperability, testing, evidence]
last_reviewed: 2026-03-06
evidence:
  - https://sigmf.org/
  - https://github.com/sigmf/SigMF
  - https://www.vita.com/page-1855484
  - https://crates.io/crates/soapysdr
  - https://docs.rs/futuresdr
  - https://crates.io/crates/vita49
---

# Problem

Rust has credible SDR substrate now: FutureSDR exists, Rust bindings for SoapySDR exist, and early crates for SigMF and VITA-49 packet handling exist. SigMF itself is a mature-enough metadata contract, and VITA 49.2 exists for signal/context transport.

But RF workflows still fail at the seam between:

- **sample files and the metadata required to interpret them correctly**,
- **device driver settings and the actual over-the-wire transport or packetization a downstream system saw**,
- **lab captures and the replay artifacts another team can use without the original radio hardware**,
- **SigMF recordings, live VITA-49 streams, and the exact conversion assumptions between them**,
- and **“reproducible SDR bugs” that currently mean giant binary blobs with half-remembered center frequency and gain settings.**

The missing Rust contribution is not another SDR runtime. It is a **replay-and-evidence kit** that pins device settings, SigMF metadata, transport receipts, packet captures, derived manifests, and redaction-safe signal bundles together.

# What it provides

- `rf.lock` — pins sample format, sample rate, center frequency, gain chain, antenna path, device identity, and timing assumptions.
- `capture-receipt` — records how a capture was produced from a device or transport stream.
- `sigmf-bridge` — deterministic adapter between raw files and SigMF package metadata.
- `vrt-replay` — replay-friendly representation of VITA-49 signal/context traffic.
- `cargo rf-evidence` — emits `*.rfbundle.zip` with manifests, metadata, replay stubs, and receiver-safe notes.

# What the crate should provide other people

1. **A boring capture handoff artifact** for SDR debugging and research.
2. **A portable bridge between file-based and transport-based RF workflows**.
3. **An honest loss surface** when converting between SigMF recordings and VITA transport views.
4. **A device-agnostic evidence bundle** for bug reports, interop labs, and corpora.
5. **A Rust-native metadata core** that can sit above FutureSDR or SoapySDR without replacing them.

# Persona / who it’s for

- SDR / RF application engineers
- spectrum-monitoring and signal-intelligence tool builders
- lab/research teams building RF corpora
- interoperability and certification teams

# Users & user stories

- **Radio engineer**: “Package this failing capture with enough metadata that another lab can replay it.”
- **Runtime developer**: “Show me whether this mismatch is transport framing, metadata drift, or device-configuration drift.”
- **Researcher**: “Publish a redacted signal corpus with exact interpretation metadata.”
- **Interop tester**: “Convert a live VITA-49 stream into a portable evidence bundle without pretending no information was lost.”

# Prior art (and why it’s insufficient)

- SigMF defines file/metadata conventions for recordings.
- VITA 49.2 defines signal/context transport semantics.
- SoapySDR provides a hardware abstraction layer.
- FutureSDR provides a Rust runtime.

What Rust still lacks is a **portable artifact layer** that ties device settings, transport observations, sample files, and replay receipts together.

# Design goals

1. **Interpretation-proof** — sample format and RF metadata must be explicit.
2. **Transport-aware** — distinguish raw recording facts from stream-transport facts.
3. **Loss-honest** — show what survives or changes in SigMF↔VITA conversions.
4. **Device-portable** — bundles should outlive the original hardware setup.
5. **Corpus-friendly** — support redaction and partial publication.

# MVP surface

- Minimal types: `RfLock`, `CaptureReceipt`, `SigmfReceipt`, `VrtReplay`, `LossReport`, `RfBundle`
- Minimal functions:
  - `capture_device_config()`
  - `write_sigmf()`
  - `capture_vrt()`
  - `diff_captures()`
  - `write_bundle()`
- Feature flags:
  - `sigmf`
  - `vita49`
  - `soapysdr`
  - `futuresdr`
  - `redaction`

# Compatibility story

- Works above existing Rust SDR and metadata crates.
- Supports offline evidence capture from raw sample files.
- Treats transport receipts and file receipts as sibling views, not as one flattened representation.
- Leaves DSP processing graphs out of the core.

# Conformance & fixtures

- Goldens for sample-format mismatch, center-frequency drift, timestamp drift, and SigMF↔VITA loss boundaries.
- Tiny IQ corpora in multiple numeric formats.
- Replay fixtures for VITA signal and context packet subsets.
- Redacted example bundles for public issue trackers.

# Path to boring stability

- Stabilize `rf.lock`, loss reports, and bundle layout before deep runtime integration.
- Start with file + metadata capture and simple transport receipts.
- Keep vendor-specific device quirks in overlays.
- Resist drift into becoming a full DSP toolkit.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 3/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 25/30**

# Minimum lovable MVP

A Rust library and CLI that capture radio/device settings, bind them to SigMF metadata and optional VITA-49 replay receipts, and package the result into a compact `*.rfbundle.zip`.

# De-risk plan

1. Start with offline file + metadata bundles.
2. Add SoapySDR adapters before attempting every device family.
3. Treat VITA replay as optional evidence, not a required runtime path.
4. Publish tiny public corpora with careful redaction.

# Non-goals

- Not another SDR runtime.
- Not a replacement for SoapySDR.
- Not a radio-analysis GUI.
- Not a universal RF storage engine.

# Architecture & API sketch

```rust
pub struct RfLock {
    pub sample_format: String,
    pub sample_rate_hz: f64,
    pub center_frequency_hz: f64,
    pub gain_profile: Vec<String>,
    pub clock_source: Option<String>,
}

pub fn capture_device_config(dev: &SoapysdrDevice) -> Result<CaptureReceipt>;
pub fn write_sigmf(receipt: &CaptureReceipt, path: &std::path::Path) -> Result<SigmfReceipt>;
pub fn capture_vrt(path: &std::path::Path) -> Result<VrtReplay>;
pub fn diff_captures(a: &RfBundle, b: &RfBundle) -> LossReport;
```

Bundle draft: `rf.lock`, `capture-receipt.json`, `recording.sigmf-meta`, `transport.vrt.json`, `loss-report.json`, `manifests/`, `notes.md`.

# Security / safety model

- Support redaction of coordinates, timestamps, identifiers, and sensitive RF environment notes.
- Permit truncated sample excerpts instead of full raw captures.
- Keep inferred annotations separate from observed device/transport facts.
- Flag when a replay cannot preserve original timing or framing.

# Maintenance & governance plan

- Track SigMF and VITA family revisions explicitly.
- Keep device adapters thin and optional.
- Publish a tiny open corpus for regression testing.
- Avoid hardware-vendor-specific productization in the core.

# Milestones

## 0.1
- `rf.lock`
- SigMF bundle writer
- offline capture receipt schema

## 0.2
- VITA-49 replay receipt support
- loss-report engine
- redacted public corpus

## 1.0
- stable `*.rfbundle.zip`
- compatibility policy for metadata/transport revisions
- CI-friendly evidence gates

# Open questions

- What is the smallest useful common denominator between SigMF recordings and VITA transport receipts?
- Which device settings belong in the portable core versus adapter-specific overlays?
- How should the bundle represent partial or synthetic timing when replaying file captures as transport events?

# Sources

- SigMF home/spec index: https://sigmf.org/
- SigMF repository: https://github.com/sigmf/SigMF
- VITA Radio Transport overview: https://www.vita.com/page-1855484
- `soapysdr` crate: https://crates.io/crates/soapysdr
- `futuresdr` crate docs: https://docs.rs/futuresdr
- `vita49` crate: https://crates.io/crates/vita49
