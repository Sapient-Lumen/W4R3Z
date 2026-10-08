---
id: P-0299
title: IPP Everywhere Interop & Conformance Kit — driverless printing profiles, canonical jobs, and certification bundles
status: idea
domains: [printing, protocols, interoperability, devices, testing]
last_reviewed: 2026-03-06
evidence:
  - https://www.pwg.org/ipp/everywhere.html
  - https://www.pwg.org/ippeveselfcert/
  - https://docs.rs/ipp
---

# Problem

Rust has a useful `ipp` crate and enough HTTP/TLS substrate to talk to printers, but it still lacks a **driverless-printing conformance workbench**. The hard part in real deployments is not just serializing IPP attributes; it is proving interoperability across:

- discovery/capability assumptions,
- IPP Everywhere profile constraints,
- document-format and finisher quirks,
- job-state and error reporting differences,
- support incidents where users only know “this printer works on macOS but not in our Rust app.”

The PWG explicitly runs IPP Everywhere self-certification tooling, which means the missing Rust opportunity is a crate/workspace that turns printing into **profile-aware, replayable, certifiable evidence** rather than bespoke ad hoc troubleshooting.

# What it provides

- `ipp-canon` — canonical IR for printer attributes, jobs, documents, and event traces.
- `ipp-profile` — IPP Everywhere / vendor / fleet policy profiles with capability expectations.
- `ipp-replay` — deterministic replay of job submissions and query flows against real or simulated devices.
- `ipp-fixtures` — printer/device simulators, golden job corpora, and self-cert-style checks.
- `ipp-diff` — semantic diff for capability reports and job outcomes.
- `cargo ipp` — build `*.ippbundle.zip` artifacts for certification and incident reports.

# Users & user stories

- **Desktop / enterprise app teams**: “Why does our Rust app fail on this supposedly IPP Everywhere printer?”
- **Device / firmware teams**: “Run a stable, machine-readable certification subset in CI.”
- **Print-fleet operators**: “Compare capabilities and regressions across firmware versions.”
- **Open-source spooler / service authors**: “Generate one redacted bundle that captures printer behavior without shipping whole documents.”

# Prior art (and why it’s insufficient)

- `ipp` is a strong protocol substrate but only a partial operations surface, not a conformance harness.
- PWG’s IPP Everywhere self-certification tools target certification workflows, but they are not a small Rust library or canonical evidence format.
- CUPS and OS-native stacks are useful operational references, but they do not give Rust developers a reusable evidence crate.

# Design goals

1. **Profile-aware driverless printing** — speak in terms users actually feel: document formats, capabilities, job states.
2. **Minimal leaked content** — issue bundles should hash or subset print documents by default.
3. **Real-device and simulator parity** — same bundle format should work for both.
4. **Explainable capability diffs** — distinguish missing required profile features from optional niceties.
5. **Fleet-friendly** — compare firmware versions and printer families reproducibly.

# Non-goals

- Not a full print spooler replacement.
- Not a GUI print dialog toolkit.
- Not a vendor-specific driver SDK.

# Architecture & API sketch

```rust
pub struct PrinterReport {
    pub profile_id: String,
    pub capabilities: CapabilityMatrix,
    pub verdicts: Vec<Verdict>,
}

pub fn inspect_printer(endpoint: &Url) -> Result<CanonicalPrinter, Error>;
pub fn replay_job(bundle: &IppBundle, transport: &mut dyn IppTransport) -> Result<JobOutcome, Error>;
pub fn diff_capabilities(a: &CanonicalPrinter, b: &CanonicalPrinter) -> CapabilityDiff;
```

Bundle draft: `printer.json`, `profile.toml`, `job.ir.json`, `document.hashes.json`, `events.jsonl`, `verdicts.json`, `notes.md`.

# Security / safety model

- Hash or subset documents by default; never require raw office/PDF uploads for triage.
- Harden all parsers for hostile printers and oversized attribute sets.
- Separate network/TLS diagnosis from document-format diagnosis in verdicts.

# Maintenance & governance plan

- Track PWG/IPP Everywhere profile revisions explicitly.
- Keep the core bundle format independent of any single printer vendor.
- Encourage community-maintained simulator/device packs rather than a monolithic test lab.

# Milestones

## 0.1
- Printer capability inspector
- Canonical attribute IR
- Job replay + semantic diff

## 0.2
- IPP Everywhere profile packs
- Device simulator hooks
- `cargo ipp bundle`

## 1.0
- Stable `*.ippbundle.zip`
- CI-friendly certification subset
- Capability-regression dashboards over bundle outputs

# Open questions

- Which document formats should the MVP treat as first-class golden fixtures?
- How much DNS-SD / discovery logic should be in scope versus left to companion crates?
- Should self-cert mapping live in-tree or in separate profile packs?

# Sources

- PWG IPP Everywhere overview: https://www.pwg.org/ipp/everywhere.html
- PWG IPP workgroup overview: https://www.pwg.org/ipp/
- PWG self-certification tools: https://www.pwg.org/ippeveselfcert/ ; https://github.com/istopwg/ippeveselfcert
- Rust `ipp` crate docs: https://docs.rs/ipp ; https://crates.io/crates/ipp
- RFC 8010 / 8011 entry points: https://datatracker.ietf.org/doc/html/rfc8010 ; https://datatracker.ietf.org/doc/html/rfc8011
