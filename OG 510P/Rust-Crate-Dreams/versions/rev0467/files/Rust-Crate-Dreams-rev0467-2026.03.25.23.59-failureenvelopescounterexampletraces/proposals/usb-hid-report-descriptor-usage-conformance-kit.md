---
id: P-0381
title: USB HID Report Descriptor + Usage Tables Conformance Kit — descriptor locks, host-quirk diffs, and portable firmware evidence bundles
status: idea
domains: [usb, embedded, hardware, interoperability, validation, tooling, firmware]
last_reviewed: 2026-03-06
evidence:
  - https://www.usb.org/hid
  - https://usb.org/document-library/hid-usage-tables-17
  - https://docs.rs/usbd-hid
  - https://docs.rs/hidparser
  - https://github.com/rust-osdev/usb
  - https://docs.rs/hid-report
---

# Problem

Rust already has useful HID substrate: there are descriptor generators, descriptor parsers, and embedded HID device implementations. But the painful failures still happen at the seam between:

- **what the descriptor claims and what firmware actually emits**,
- **usage-table evolution and stale local constants/codegen**,
- **boot protocol, report IDs, and host-specific interpretation quirks**,
- **descriptor parsing success and real cross-host behavior**,
- and **“works on Linux but not on Windows/macOS/Android” bug reports with no portable artifact**.

The missing Rust contribution is not another HID device class crate. It is a **descriptor and host-behavior conformance kit** that turns report descriptors and small traces into reviewable, replayable evidence.

# What it provides

- `hid-profile.lock` — pins HID spec/usage-table revision, protocol assumptions, report-ID policy, and optional host-profile overlays.
- `hid-irx` — a neutral IR for report descriptors, report streams, parsed usages, logical/physical bounds, and host findings.
- `descriptor-diff` — semantic diffs such as “same usages, different report-ID layout”, “boot-compatible on one profile only”, or “descriptor legal but host-fragile”.
- `usage-sync` — a generated, versioned usage-table layer so crates can pin exact usage-table revisions.
- `cargo hid-evidence` — emits `*.hidbundle.zip` with lockfile, descriptor summary, host findings, and notes.

# What the crate should provide other people

1. **A boring default artifact for HID interoperability bugs**.
2. **Explicit descriptor/profile locks** instead of vague “USB HID compatible”.
3. **Usage-table version pinning** so parser/generator behavior stays reviewable.
4. **Portable host-quirk evidence** from small report traces and descriptor summaries.
5. **A shared conformance surface** for Rust embedded USB and host-side HID tooling.

# Persona / who it’s for

- Embedded Rust developers building HID firmware
- Maintainers of Rust HID parser/generator libraries
- OS/device integration teams debugging host-specific HID behavior
- Hardware teams validating descriptors in CI before flashing devices

# Users & user stories

- **Firmware author**: “Catch descriptor/usage/report-ID problems before I test on every host manually.”
- **Maintainer**: “Run one public corpus across parser and generator crates.”
- **Support engineer**: “Share a compact descriptor/report artifact instead of asking for a whole firmware image.”
- **Integrator**: “Tell me whether this is a spec violation, a host quirk, or a boot/report protocol mismatch.”

# Prior art (and why it’s insufficient)

- USB-IF continues to publish HID specifications, tools, and updated Usage Tables.
- HID Usage Tables 1.7 was published in early 2026.
- Rust has `usbd-hid`, `hidparser`, `hid-report`, and the `rust-osdev/usb` utilities.

What Rust still lacks is a **boring default conformance workbench** for usage-table pinning, descriptor diffs, host-profile overlays, and portable evidence bundles.

# Design goals

1. **Descriptor-first** — the descriptor remains the core review surface.
2. **Host-aware** — a descriptor can be “legal” and still operationally brittle.
3. **Version-pinned** — usage-table and profile revisions must be explicit.
4. **Tiny-artifact friendly** — bundles should stay small enough for firmware workflows.
5. **Reuse existing crates** — do not replace generators/parsers unless necessary.

# MVP surface

- Minimal types: `HidProfileLock`, `DescriptorReport`, `HostFinding`, `HidBundle`
- Minimal functions:
  - `inspect_descriptor()`
  - `compare_host_profiles()`
  - `diff_descriptors()`
  - `write_bundle()`
- Feature flags:
  - `usage-db`
  - `boot-protocol`
  - `report-stream`
  - `host-profiles`
  - `embedded`

# Compatibility story

- Builds above existing parser/generator/device-class crates rather than replacing them.
- Can ingest raw descriptors and tiny captured report sequences from external tools.
- Treats host-profile rules as overlays around a stable evidence core.
- Keeps usage-table revisions explicit so generated code and findings stay reviewable.

# Conformance & fixtures

- Tiny fixtures for bad logical/physical bounds, report-ID collisions, malformed collections, boot/report-protocol mismatches, and stale usage-table assumptions.
- Goldens for “descriptor parses but host profile rejects” and “same usages, different layout semantics”.
- Public host-profile packs for narrow cross-host behavior checks.
- Round-trip tests for descriptor generation → parse → normalized diff.

# Path to boring stability

- Stabilize usage-table schema, descriptor IR, and finding categories before adding many host adapters.
- Start with descriptor + tiny report-trace evidence rather than large integration environments.
- Keep the first release focused on explainable interop and CI ergonomics.
- Prefer deterministic pretty-printing, hashing, and diff output.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 24/30**

# Minimum lovable MVP

A library and CLI that inspect a HID report descriptor, pin a usage/profile lock, run narrow host-profile checks, and emit a compact `*.hidbundle.zip` with explainable findings.

# De-risk plan

1. Start with descriptors and tiny report traces before trying to emulate full host stacks.
2. Keep usage-table synchronization explicit and generated.
3. Reuse existing Rust parser/generator crates as adapters.
4. Resist scope creep into full USB stack development.

# Non-goals

- Not a new USB stack.
- Not a replacement for `usbd-hid` or every HID parser.
- Not a full host emulator.
- Not a firmware framework.

# Architecture & API sketch

```rust
pub struct HidProfileLock {
    pub hid_spec: String,
    pub usage_table_rev: String,
    pub host_profiles: Vec<String>,
}

pub fn inspect_descriptor(bytes: &[u8]) -> Result<DescriptorReport>;
pub fn compare_host_profiles(report: &DescriptorReport, lock: &HidProfileLock) -> Vec<HostFinding>;
```

Bundle draft: `hid-profile.lock`, `descriptor.json`, `usage-report.json`, `host-findings.json`, `report-traces/`, `notes.md`.

# Security / safety model

- Treat descriptors and report traces as untrusted input.
- Support redaction of device-identifying strings or vendor/product metadata where needed.
- Record exact parser/generator/usage-db versions in every bundle.
- Keep outputs deterministic for CI and bug-report exchange.

# Maintenance & governance plan

- Keep the core centered on locks, neutral IR, findings, and bundle format.
- Version usage-table generation and host overlays independently.
- Publish a small public corpus of descriptor edge cases.
- Avoid trying to become a complete USB validation laboratory.

# Milestones

## 0.1
- descriptor inspection
- usage/profile lockfile
- normalized finding writer

## 0.2
- host-profile overlays
- descriptor semantic diffs
- report-trace support

## 1.0
- stable `*.hidbundle.zip`
- public fixture corpus
- documented compatibility policy across supported profiles

# Open questions

- Which host profiles deserve first-class MVP support?
- How much report-stream evidence is needed before bundles become noisy?
- Should usage-table sync be generated at build time, release time, or both?

# Sources

- USB HID specs and tools: https://www.usb.org/hid
- HID Usage Tables 1.7: https://usb.org/document-library/hid-usage-tables-17
- `usbd-hid`: https://docs.rs/usbd-hid
- `hidparser`: https://docs.rs/hidparser
- `rust-osdev/usb`: https://github.com/rust-osdev/usb
- `hid-report`: https://docs.rs/hid-report
