---
id: P-0156
title: Time Sync & Clock Discipline Kit
status: idea
domains: [systems, networking, observability, embedded, devtools, conformance]
last_reviewed: 2026-03-05
evidence:
  - https://github.com/pendulum-project/ntpd-rs
  - https://crates.io/crates/ntpd
  - https://linuxptp.sourceforge.net/
  - https://tsn.readthedocs.io/timesync.html
  - https://crates.io/crates/ntp_usg-client
  - https://www.rfc-editor.org/rfc/rfc5905.html
  - https://datatracker.ietf.org/doc/html/rfc7822
  - https://datatracker.ietf.org/doc/html/rfc8915
  - https://www.rfc-editor.org/rfc/rfc9769
---
# Problem

Time is a dependency for almost everything (security, telemetry, distributed systems), yet “getting good time” remains operationally fragile:

- NTP vs NTS (security) vs PTP/gPTP (precision)
- PHC vs system clock discipline
- Different environments: cloud VMs, bare metal, embedded/TSN, lab rigs
- Debugging drift/jitter often requires bespoke logs and hardware-specific tribal knowledge

Rust has several solid components (NTP/NTS implementations and Linux PTP tooling exists in the wider ecosystem), but lacks a **coherent, testable, portable kit** for time synchronization workflows.

# What it should provide

## 1) A unified “time source → discipline → verify” abstraction

A crate/workspace that provides:

- **Time source adapters**: NTP, NTS, PTP/gPTP profiles, “manual” lab sources
- **Clock targets**: system clock, Linux PHC, mock clocks for tests
- **Discipline models**: PLL/FLL-like policies, holdover strategies, step/slew rules
- **Verification hooks**: statistics, alarms, “time quality grade” output

This is not “replace chrony/linuxptp”; it’s the **Rust-native integration and test harness layer**.

## 2) Portable evidence bundles for drift incidents

A `timesyncbundle.zip` (shareable, redactable) containing:

- `manifest.json` (kernel/time APIs, NIC timestamps capability, feature flags)
- `sources/` (server addresses redacted, NTS cert fingerprints)
- `measurements.jsonl` (offset, delay, dispersion, jitter, frequency adjustment)
- `discipline.json` (policy config)
- `events.jsonl` (step/slew, leap, loss of sync, holdover enter/exit)
- `phc/` optional: phc2sys/ptp4l-like summaries (normalized)
- `report.json` (derived SLOs: max offset, time-to-lock, holdover quality)

## 3) Conformance and simulation packs

High leverage packs:

- **Protocol conformance**: NTP era/Y2036 handling, interleaved mode, NTS handshake edge cases
- **Profile packs**: gPTP/802.1AS-style constraints (where applicable), TSN-oriented checks
- **Simulation**: controlled jitter, asymmetric delay, packet loss bursts; mock PHC drift models

# MVP → v1 plan

### MVP
- Evidence bundle schema + collector library
- NTP/NTS client integration path (start with ntpd-rs / ntpd crate as adapters)
- Minimal “discipline + verify” runner that produces stable `report.json`

### v1
- PTP/gPTP observability adapter (normalize ptp4l/phc2sys signals)
- Deterministic simulation harness (inject network + oscillator models)
- CI gating mode: “time quality regression” checks on hardware-in-the-loop rigs

# Why this matters

A shared kit makes time issues *actionable* for library authors and operators: you can attach a `timesyncbundle.zip` to an issue and others can replay, diff, and understand what changed—without reproducing your lab.
