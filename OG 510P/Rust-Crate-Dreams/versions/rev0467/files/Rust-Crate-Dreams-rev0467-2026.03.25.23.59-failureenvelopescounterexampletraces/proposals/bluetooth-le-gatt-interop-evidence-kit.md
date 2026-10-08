---
id: P-0223
title: Bluetooth LE GATT Interop & Evidence Kit — canonical GATT traces, profile fixtures, and repro bundles
status: idea
domains: [embedded, bluetooth, ble, gatt, iot, interop, conformance]
last_reviewed: 2026-03-05
evidence:
  - https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-54/out/en/host/generic-attribute-profile--gatt-.html
  - https://crates.io/crates/btleplug
needs:
  - A repeatable way to test BLE GATT behavior across OS stacks, chipsets, and device firmware (timeouts, MTU, notifications, bonding quirks).
  - A shareable, redactable evidence bundle for “this peripheral behaves differently on Android vs macOS”.
risks:
  - BLE platform APIs vary wildly; must be adapter-based with a common GATT trace IR.
  - Radio environment noise makes determinism hard; evidence capture must separate “RF chaos” from protocol invariants.
---

## Problem
BLE integrations fail in the messy middle: MTU negotiation edge cases, notification subscription behavior, bonding/security requirements, and vendor profile quirks. Today, teams capture ad-hoc logs and guess.

## What this crate provides
A **canonical GATT trace** + **profile fixture runner** + `*.gattbundle.zip` evidence artifacts so BLE bugs become comparable across:
- OS APIs (BlueZ, CoreBluetooth, Windows),
- client libraries (e.g., `btleplug`),
- and actual peripherals.

## Users
- IoT products shipping companion apps + Rust services.
- Embedded teams validating peripherals against expected GATT profiles.
- CI labs with device farms.

## Prior art (insufficient)
- `btleplug` gives cross-platform access, but not a standardized interop/conformance harness.
- Vendor mobile tools exist, but are not scriptable or diff-friendly.

## Design goals
- **GATT trace IR:** operations (discover services/characteristics, read/write, notify/indicate) with normalized timing and error taxonomy.
- **Profile fixtures:** declarative expected profiles (UUIDs, properties, security requirements) + behavioral tests.
- **Evidence bundles:** redact device identifiers and addresses by default.

Non-goals:
- Replacing `btleplug` or OS BLE stacks.
- RF-level debugging (sniffer integration optional).

## Architecture sketch
Workspace:
- `gattkit-core` — trace IR, canonicalization, diff, redaction.
- `gattkit-adapter-btleplug` — runner using `btleplug` as one backend.
- `gattkit-fixtures` — profile schemas + test library.
- `gattkit-cli` — `scan`, `probe`, `run`, `bundle`, `diff`.

### Bundle format: `*.gattbundle.zip`
- `manifest.json` (OS, adapter, device fingerprint hash, run parameters)
- `profile.json` (discovered services/characteristics; properties; security flags)
- `trace.jsonl` (canonicalized operations + timings)
- `verdict.json` (behavioral suite results)
- `notes.md`

## MVP (4–8 weeks)
1. `probe`: discover services/characteristics + export canonical profile.
2. A small behavioral suite: MTU negotiation, notify subscribe/unsubscribe, read/write with timeouts.
3. Bundle + diff between two runs (e.g., macOS vs Linux).

## De-risk plan
- Start with “virtual peripherals” where possible (or a small set of common dev boards).
- Add sniffer support later as an optional `pcapng` attachment by hash.

## Maintenance
- Keep the trace IR minimal and stable; version bundles.
- Encourage fixtures for common GATT profiles (Heart Rate, Battery, custom vendor patterns) with clear licensing.

## Sources
- Bluetooth Core Specification (GATT section).
- Rust BLE ecosystem: `btleplug`.
