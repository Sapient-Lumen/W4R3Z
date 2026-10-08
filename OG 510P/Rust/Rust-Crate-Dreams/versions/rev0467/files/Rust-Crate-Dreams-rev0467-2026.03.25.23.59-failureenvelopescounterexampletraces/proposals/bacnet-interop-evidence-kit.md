---
id: P-0282
title: BACnet/BACnet-IP Interop & Evidence Kit — device simulation matrices, canonical traces, and replayable building-automation bundles
status: idea
domains: [industrial, iot, building-automation, networking, interoperability, testing, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://bacnet.org/about-bacnet-standard/
  - https://www.ashrae.org/technical-resources/bookstore/bacnet
  - https://crates.io/crates/bacnet-rs
  - https://crates.io/crates/bacnet-emb
  - https://crates.io/crates/mabi-bacnet
---
## What it should provide others

A **practical interop lab** for BACnet ecosystems:
- canonical BACnet trace IR (Who-Is/I-Am, ReadProperty, COV, alarming, etc.)
- scenario runner + device simulator matrix
- privacy-safe, replayable `*.bacnetbundle.zip` artifacts for CI and field debugging

The gap is not “a BACnet stack”; it’s the tooling that lets vendors and integrators answer:
- “Which controllers interoperate with this device profile?”
- “Where did the session diverge (segmentation, APDU sizing, timing, object discovery)?”
- “Can we reproduce the field failure without shipping a whole building’s network captures?”

## Why now (ecosystem gap)

BACnet is widely used for building automation and exists across heterogeneous devices; interoperability issues are common and expensive. A kit that standardizes capture/replay/diff and produces shareable evidence bundles would help:
- open-source BACnet stacks in Rust gain real-world compatibility faster
- integrators build reliable test harnesses for deployments
- reduce “it works on my controller” debugging cycles

## Proposed crate shape (workspace)

- `bacnetkit-core` — canonical event model + normalization
- `bacnetkit-capture` — adapters:
  - decode from pcap / UDP traces (BACnet/IP)
  - hook-based capture for Rust BACnet stacks
- `bacnetkit-sim` — device simulator DSL (objects/properties, timing, COV behavior)
- `bacnetkit-runner` — matrix orchestration (client/server/device profiles)
- `bacnetkit-diff` — semantic diff + explain (first divergence)
- `bacnetkit-bundle` — `*.bacnetbundle.zip` schema + redaction + signing hooks
- `cargo-bacnetkit` — CLI

### Evidence bundle sketch

- `topology.json` (devices, addresses, roles)
- `profiles/` (device profile declarations)
- `events.ndjson` (canonical APDU-level events; stable IDs)
- `pcap/` (optional, redacted or truncated)
- `verdict.json` + `explain.md` (capability matrix results)

## Minimum lovable MVP (4–8 weeks)

1. Canonical decoder for a minimal but high-value subset:
   - device discovery (Who-Is/I-Am)
   - ReadProperty / ReadPropertyMultiple
2. Simulator for a small “device profile” set (e.g., a thermostat + sensor)
3. Bundle format + diff tool that points to divergence at the APDU/object-property level

Deliverable: `cargo bacnetkit matrix --profiles profiles/*.yaml --out results.bacnetbundle.zip`.

## De-risk plan

- Start with BACnet/IP UDP decoding + simulation; leave MS/TP for later.
- Keep simulator deterministic and scriptable; add fuzz/minimization after IR stabilizes.
- Focus on **capability matrices** as the “killer feature” that attracts adopters.

## Scorecard (0–5)

- Impact: 4
- Neglectedness: 5
- Feasibility: 3
- Adoptability: 3
- Sustainability: 3
- Differentiation: 5 (interop lab + simulator + evidence bundles)
