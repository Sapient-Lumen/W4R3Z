---
id: P-0137
title: Matter Certification & Interop Kit — a pragmatic Rust “device + controller” test harness and evidence bundle workflow
status: idea
domains: [embedded, iot, networking, security, devtools]
last_reviewed: 2026-03-05
evidence:
  - https://github.com/project-chip/rs-matter
  - https://crates.io/crates/rs-matter
  - https://crates.io/crates/matter-rs
  - https://docs.rs/matc
needs:
  - A repeatable way to validate Matter behavior across **device implementations** and **controllers** without needing vendor-only certification labs for every iteration.
  - A portable, shareable failure artifact (“this commissioning flow failed on this firmware + controller + transport”) that maintainers can reproduce.
  - A test-first bridge between no_std embedded targets and host-based integration testing (Linux/macOS/Windows CI), with realistic transports (BLE, IP) and timeouts.
non_goals:
  - Replacing official CSA/Matter certification; the goal is “make pre-cert and regression testing boring”.
  - A full controller ecosystem; this kit focuses on test harnesses, interop fixtures, and evidence bundles.
---

## What this crate should provide

### 1) A standard evidence bundle
Define a `*.matterbundle.zip` that contains:

- `manifest.json` (schema version, device build info, controller build info, target/platform, timestamps)
- Transcripts (commissioning / CASE / PASE, cluster interactions, errors)
- Transport captures (optional): BLE logs, pcap/pcapng for IP, timing traces
- Normalized “expected vs observed” assertions (attributes, events, TLV payload summaries)
- Repro recipe: `cargo matter-test replay ./bundle.matterbundle.zip`

Why: `rs-matter` positions itself as a toolkit across MCU → Linux; this kit turns “toolkit” into *portable reproducibility*.

### 2) A harness layer that can run anywhere
- Host runner: Tokio-based async harness for controllers and simulated devices.
- Embedded runner: a minimal “probe” API (no_std-friendly) to emit the same transcript format.
- Adapter traits:
  - `Transport` (BLE, UDP/IP)
  - `Clock` (mockable time)
  - `Crypto` (for HW-backed keys; optional)
  - `Storage` (NVS / flash; optional)

### 3) Interop profiles (MVP)
Ship a set of “profiles” that are realistically useful:
- Commissioning over IP (happy path + common failure modes)
- Basic interaction model: read/write attributes, invoke commands
- Robustness: timeouts, retransmissions, power-cycle mid-commissioning, bad certificates

### 4) Conformance vectors
Curate a small, versioned corpus of “known tricky flows”:
- invalid TLV edge cases
- replay detection
- session resumption corner cases
- attribute/event ordering sensitivities

## MVP plan (4–6 weeks of focused work)
- Implement the `matterbundle` schema + CLI (`cargo matter-test`)
- Build a host-only runner that can:
  1) drive a device under test (DUT) over IP
  2) run a controller flow using a controller adapter (start with `matc`)
  3) emit a bundle on failure (and optionally on success for baselines)
- Provide 10–20 integration tests that produce bundles and snapshot the normalized transcript.

## v1 plan (next)
- Add BLE capture adapters (start with “log-only”, then optional packet capture where available)
- Add an embedded “bundle emitter” (no_std) for DUT firmwares
- Add a “matrix runner” for CI (device list × controller list × profile list)

## Adoption strategy
- Start by making `rs-matter` and `matc` users’ lives easier (drop-in harness + evidence).
- Provide small adapters for popular embedded HAL stacks (feature-gated).
- Keep the core format stable and versioned: bundles must remain readable for years.

## Risks and mitigations
- **Hardware variability**: mitigate with the bundle format; normalize timings and allow tolerant assertions.
- **Spec churn**: keep “profiles” versioned and tied to a manifest schema version.
- **Too big**: aggressively modularize; `matterbundle-core` (schema + reader/writer) should be tiny and stable.
