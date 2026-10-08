---
id: P-0150
title: BLE Interop & GATT Conformance Kit
status: idea
domains: [iot, bluetooth, networking, mobile, conformance, devtools, testing]
last_reviewed: 2026-03-05
evidence:
  - https://docs.rs/btleplug
  - https://docs.rs/bluer/latest/bluer/
  - https://lib.rs/crates/bluest
  - https://crates.io/crates/btleplug
  - https://crates.io/crates/bluer
---

# Problem

Rust has solid building blocks for Bluetooth LE (BLE) on host platforms (Windows/macOS/Linux) and Linux stack integration (BlueZ), but real deployments repeatedly hit the same pain:

- “Works on my laptop” ≠ “works on *phones + OS versions + chipsets*”.
- Interop bugs are hard to report (timing-sensitive, logs are non-portable, captures are inconsistent).
- GATT profile implementations are rarely conformance-tested in a reusable way.

We’re missing an ecosystem-level **interop + conformance harness** that makes BLE debugging and profile correctness *shareable* and *repeatable*.

# What it should provide

## 1) A standard evidence bundle: `blebundle.zip`

Include:

- `manifest.json` (OS, adapter chipset, BlueZ version, permissions, pairing mode)
- `pcapng/` optional capture (where available)
- `gatt/` service/characteristic snapshot (UUIDs, properties, descriptors)
- `events.jsonl` normalized event stream (scan results, connects, MTU, notifications)
- `timing.json` latency histograms (connect time, notify jitter, RSSI trends)
- `repro.md` “how to rerun” and a minimal script
- `privacy.json` redaction map (device addresses, names)

## 2) A portable test harness for GATT profiles

A crate that lets you define profile expectations:

- Services/characteristics must exist (and properties match)
- Read/write/notify semantics (including CCCD behavior)
- Edge cases: MTU negotiation, long writes, disconnect/reconnect persistence
- Timing bounds and retry policies

Expose:
- `BleScenario` trait (setup → actions → assertions)
- `ProfileSpec` schema (JSON/YAML) for non-Rust authors

## 3) `cargo ble` workflow

- `cargo ble doctor` — permissions, adapter sanity, BlueZ config, platform pitfalls
- `cargo ble capture` — run scenario while capturing normalized logs
- `cargo ble conformance` — execute profile specs, emit `ble-report.json`
- `cargo ble minimize` — reduce flaky sequences into smaller repro scripts

## 4) Adapter abstraction (pragmatic)

- Use existing crates (`btleplug`, `bluer`, `bluest`) as backends.
- Provide a “capability matrix” (supports advertisements parsing, extended adv, L2CAP CoC, etc.)
- Keep “lowest common denominator” core, but allow backend-specific extensions.

# MVP scope (2–4 weeks)

- `blebundle.zip` schema v0 + generator
- One backend (Linux via `bluer` *or* cross-platform central via `btleplug`)
- A small set of scenarios:
  - Scan + connect + read characteristic
  - Subscribe notifications + measure jitter
  - Write-with-response and long write
- Redaction tooling + clear safety defaults

# v1 scope (2–3 months)

- Add at least two backends (e.g., `btleplug` + `bluer`)
- ProfileSpec schema with test vectors
- CI-friendly mode:
  - run against a simulator / “loopback” peripheral (software peripheral where possible)
  - or allow “hardware-in-the-loop” runners for labs
- Failure clustering: group similar failures by normalized traces

# Why it’s a worthy crate contribution

It turns BLE from “hardware + OS + timing chaos” into **portable evidence bundles** and **profile conformance** that maintainers can reproduce. That helps every Rust BLE crate and every downstream device team: fewer heisenbugs, more shared diagnostics, and higher confidence in GATT correctness.
