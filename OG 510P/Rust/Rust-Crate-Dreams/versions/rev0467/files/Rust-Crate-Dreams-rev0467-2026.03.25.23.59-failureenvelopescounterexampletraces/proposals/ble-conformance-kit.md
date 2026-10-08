---
id: P-0064
title: BLE Conformance Kit — capability model + cross-platform test harness for Bluetooth LE apps
status: idea
domains: [hardware, mobile, iot]
last_reviewed: 2026-03-01
evidence:
  - https://github.com/deviceplug/btleplug
  - https://github.com/alexmoon/bluest
  - https://nonpolynomial.com/2023/10/30/how-to-beg-borrow-steal-your-way-to-a-cross-platform-bluetooth-le-library/
needs:
  - Developers need to know what *works on which platform* and why it fails.
  - A conformance suite reduces ecosystem fragmentation more than “one more BLE crate”.
risks:
  - Hardware variation makes tests flaky without careful design.
  - Platform APIs differ enough that a single high-level API can become lowest-common-denominator.
---

## Problem
Rust has cross-platform BLE host crates, but teams still hit:
- platform-specific permission and scanning behavior,
- inconsistent MTU/notify semantics,
- connection stability differences,
- “it works on Linux but not on macOS/Windows”.

We lack a **capability model** and a **shared conformance harness** that BLE crates and apps can target, to converge on predictable behavior.

## Users & user stories
- **Mobile app**: “I want one API and a report: iOS supports X, Windows lacks Y, here’s the workaround.”
- **IoT gateway**: “I need reliable scanning and reconnect, with timeouts and backoff that behave consistently.”
- **Library author**: “I want a test suite that proves my backend meets baseline semantics.”

## Prior art (and why it’s insufficient)
- `btleplug`: cross-platform async BLE, but historically uneven platform maturity and no standardized conformance layer. https://github.com/deviceplug/btleplug
- `bluest`: newer cross-platform BLE crate, still without ecosystem-wide semantic contracts. https://github.com/alexmoon/bluest
- “Beg/Borrow/Steal…” writeup highlights how many BLE crates die and how hard cross-platform is — conformance is the missing multiplier. https://nonpolynomial.com/2023/10/30/how-to-beg-borrow-steal-your-way-to-a-cross-platform-bluetooth-le-library/

## Design goals / non-goals
**Goals**
- Define a **capability model** (scan filters, extended ads, MTU control, GATT write-without-response, etc.).
- Provide a **conformance test suite** (host-side, deterministic where possible).
- Provide **profile helpers** (standard services/characteristics, UUID catalogs, encoding helpers).
- Provide adapters for existing backends (start with btleplug; add bluest).

**Non-goals**
- Replacing backend crates; focus on contracts, tests, and adapters.
- Guaranteeing support for every BLE feature on every OS.

## Architecture & API sketch
- `ble-conformance-core`
  - `BleBackend` trait (scan/connect/gatt/notify)
  - `Capabilities` bitset + structured capability descriptions
  - `Profile` helpers (UUID registry + codecs)
- `ble-conformance-btleplug` adapter
- `ble-conformance-bluest` adapter
- `ble-conformance-cli`
  - `ble doctor` prints capabilities and runs baseline tests
  - `ble test --target <device>` runs hardware-in-loop tests

Conformance suite design:
- **Tier 0**: pure host semantics (timeouts, cancellation, event ordering)
- **Tier 1**: loopback/virtual devices when available
- **Tier 2**: hardware-in-loop with reference peripheral (cheap dev board)

## Security / safety model
- No implicit permission escalations; surface required permissions and prompts explicitly.
- Avoid leaking device identifiers in logs by default (redaction modes).

## Maintenance & governance plan
- Keep tests and capability docs as first-class artifacts.
- Accept backend adapters as separate crates to avoid dependency bloat.
- Publish a compatibility matrix generated from CI/hardware runs.

## Milestones
**0.1**
- Capability model v0 + btleplug adapter + CLI “doctor”.
- Tier 0 tests.

**0.2**
- Profile helpers for a few common services (Battery, Device Info, Heart Rate).
- Hardware reference peripheral + Tier 2 recipe.

**1.0**
- bluest adapter + published compatibility matrix for major OS versions.

## Open questions
- What’s the minimal “reference peripheral” that’s cheap and globally available?
- How to handle platform-specific permission flows without exploding API surface?

## Sources
- https://github.com/deviceplug/btleplug
- https://github.com/alexmoon/bluest
- https://nonpolynomial.com/2023/10/30/how-to-beg-borrow-steal-your-way-to-a-cross-platform-bluetooth-le-library/
