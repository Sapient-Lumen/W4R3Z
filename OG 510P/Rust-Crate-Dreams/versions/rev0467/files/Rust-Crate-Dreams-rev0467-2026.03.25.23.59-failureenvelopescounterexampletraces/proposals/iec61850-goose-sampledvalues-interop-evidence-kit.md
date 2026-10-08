---
id: P-0228
title: IEC 61850 GOOSE/Sampled Values Interop & Evidence Kit
status: idea
domains: [industrial, power-systems, networking, interop, pcap]
last_reviewed: 2026-03-05
evidence:
  - https://www.megger.com/en-us/type/relay/iec61850-solutions
  - https://www.omicronenergy.com/en/products/svscout/
---

# Problem

IEC 61850 digital substation deployments depend on **GOOSE** and **Sampled Values** streams behaving correctly under real network conditions. In practice, teams spend significant time debugging:

- misconfigurations in datasets, VLAN priorities, sampling rates, and message formats,
- timing/latency and replay issues,
- vendor-specific interpretations and tooling gaps.

Today’s ecosystem has strong proprietary tooling, but Rust lacks an open, reproducible, **pcap-first interop kit** that can:

- normalize and interpret captures,
- validate common profile expectations,
- produce **shareable evidence bundles** for CI/regression and field investigations.

# What it provides

1. Workspace crates:
   - `iec61850-wire`: frame parsing for relevant Ethernet profiles and common fields needed for diagnostics.
   - `iec61850-profiles`: profile validators (sampling sets, dataset expectations, sanity checks).
   - `iec61850-trace`: capture ingest + canonicalization (pcap/pcapng → normalized IR).
   - `iec61850-diff`: semantic diffs across traces (what changed and why it matters).
   - `iec61850-cli`: `ingest|canon|validate|diff|report`.

2. Evidence bundle format: `*.iec61850bundle.zip`
   - `pcap/` (optional, size-capped)
   - `normalized/trace.jsonl` (canonical IR)
   - `reports/` (validator outputs, timing histograms)
   - `redaction.json` (what was removed)

3. “Field-to-CI bridge” workflows
   - minimal bundle that an IED developer can attach to a bug report,
   - CI regression tests that assert “GOOSE/SV behavior stayed equivalent”.

# Users & user stories

- **Protection engineers / substation integrators**: “We need to confirm a GOOSE/SV issue is configuration vs device vs network—and share evidence with a vendor quickly.”
- **IED developers**: “We need stable regression corpora for protocol edge cases without shipping huge pcaps.”
- **Lab/test teams**: “We want automated validation against profile expectations for releases.”

# Prior art (and why it’s insufficient)

- Commercial tools emphasize monitoring and testing; they highlight that small misconfigurations in GOOSE/SV can cause operational failures and that dedicated tooling is required.
- Rust has general pcap/network crates, but not an IEC 61850 **interop-first diagnostic stack** with canonical IR + diffs + reproducible bundles.

# Design goals

- **Capture-first**: start from pcap/pcapng and emit a stable IR.
- **Canonicalization**: stable ordering, normalized timestamps, deterministic summaries.
- **Profile-first validation**: common checks that match how engineers debug.
- **Operational ergonomics**: one command to create a redacted bundle.

# Non-goals

- Becoming a full IEC 61850 engineering/SCADA suite.
- Replacing vendor tools in accredited certification labs.

# Architecture & API sketch

```rust
pub struct TraceEvent { /* normalized fields */ }

pub fn ingest_pcap(path: &Path) -> Result<impl Iterator<Item=TraceEvent>>;

pub trait Profile {
  fn validate(&self, events: &[TraceEvent]) -> ValidationReport;
}

pub fn diff(a: &[TraceEvent], b: &[TraceEvent]) -> DiffReport;

pub fn bundle_from_capture(cfg: BundleCfg) -> Result<PathBuf>;
```

# Security / safety model

- Bundles default to **redaction** (MACs, IPs where applicable, identifiers) and strict size caps.
- Clear “unsafe to share” flags when payload content could be sensitive.

# Maintenance & governance plan

- Begin with a minimal normalized IR + a handful of high-value validations (timing sanity, stream continuity, sampling rate checks).
- Keep profiles modular; accept community-contributed profile packs.

# Milestones

1. **MVP (4–8 weeks)**
   - pcap ingest → normalized event stream
   - canonical summary + timing histograms
   - bundle writer + schema placeholder
   - diff tool over normalized traces

2. **Interop suite (next)**
   - profile library expansion (common datasets + sanity checks)
   - fuzz corpora for frame decoding

# Open questions

- Which “minimal IR” fields best support debugging across vendors without overfitting?
- Best defaults for redaction and sampling down traces.

# Sources

- Megger overview emphasizes IEC 61850 tooling for configuration verification, GOOSE analysis, and Sampled Values testing, and notes misconfigurations can cause failures. https://www.megger.com/en-us/type/relay/iec61850-solutions
- OMICRON SVScout describes a dedicated tool for visualizing IEC 61850 Sampled Values streams and highlights the domain’s testing/measurement needs. https://www.omicronenergy.com/en/products/svscout/
