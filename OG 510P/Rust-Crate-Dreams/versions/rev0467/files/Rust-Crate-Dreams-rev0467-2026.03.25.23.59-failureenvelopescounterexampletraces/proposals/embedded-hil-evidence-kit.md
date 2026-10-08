---
id: P-0159
title: Embedded HIL Evidence Kit
status: idea
domains: [embedded, devtools, testing, conformance, observability]
last_reviewed: 2026-03-05
evidence:
  - https://crates.io/crates/probe-rs
  - https://probe.rs/
  - https://embassy.dev/
  - https://github.com/embassy-rs/embassy
  - https://docs.rs/probe-rs
---
# Problem

Embedded Rust is thriving (Embassy for async embedded; probe-rs for modern debug tooling), but the “last mile” for reliability is still fragile:

- HIL (hardware-in-the-loop) failures are hard to reproduce across labs and boards.
- Logs/trace, probe configuration, target descriptions, and firmware builds aren’t packaged as a single shareable unit.
- CI and maintainers need **portable evidence** that a test run happened on *which* silicon, with *which* debug transport, and *what* signal-level behavior.

# What it should provide

A crate + tooling standard for **reproducible embedded test evidence**.

## 1) A portable test-run bundle: `hilbundle.zip`

A shareable, redaction-aware artifact containing:
- firmware binary + build metadata (git SHA, features, profile),
- target description fingerprint + probe info + transport settings,
- captured RTT/defmt logs (or serial), timestamps, and test assertions,
- optional SWD/JTAG trace summaries and core registers at failure,
- a “replay recipe” (flash + run + capture settings).

## 2) A probe/runner abstraction layer

- Backend adapters:
  - probe-rs (baseline),
  - optional vendor tools as “external runners” (shell adapters).
- A stable “session manifest” schema: what was connected, how, and with what permissions.

## 3) Cargo-native workflows

- `cargo hil test`: flash, run, capture, assert.
- `cargo hil bundle`: emit a `hilbundle.zip` for a failing run.
- `cargo hil doctor`: sanity-check USB permissions/udev, probe access, target pack presence.

## 4) Conformance packs for common peripherals

A community-owned set of test packs for:
- UART, I2C, SPI,
- GPIO timing assumptions,
- low-power sleep/wakeup,
- bootloader/OTA staging paths (optional).

# MVP plan (0.1)

- Define `hilbundle.zip` manifest schema + minimal bundle producer.
- Integrate probe-rs flashing + RTT log capture.
- Provide one reference harness for Embassy (timer + GPIO + UART loopback).

# v1 plan

- Multi-board matrix runner (same suite across multiple MCUs).
- Optional “logic trace” adapter layer (when labs have hardware).
- A corpus of anonymized failure bundles for regression tests of the tooling itself.

# Design constraints & sharp edges

- Don’t make this a test framework replacement; it’s an evidence + transport layer.
- Privacy matters: first-class redaction (serial numbers, internal paths, secrets in logs).
- Keep bundle size bounded; prefer summarized traces + optional raw attachments.

# Why this is epic

It makes embedded Rust feel like “real software engineering” at scale: when something fails, you can hand maintainers a single `hilbundle.zip` and they can reproduce or at least inspect exactly what happened.
