---
id: P-0276
title: Modbus RTU/TCP Interop & Evidence Kit — canonical PDUs + modbusbundle.zip
status: idea
domains: [industrial, networking, iot, embedded, interoperability, testing]
last_reviewed: 2026-03-05
evidence:
  - https://www.modbus.org/file/secure/modbusprotocolspecification.pdf
  - https://www.modbus.org/modbus-specifications
  - https://crates.io/crates/tokio-modbus
  - https://crates.io/crates/modbus-rs
---

## What it should provide others

A conformance + interop harness for Modbus that produces **small, shareable repro artifacts** instead of megabyte packet captures.

It should provide:

- Canonical Modbus **PDU/ADU IR** (RTU/ASCII/TCP) and semantic diff tooling.
- **Fixture corpora** for function codes and edge cases (addresses, exception codes, endian quirks).
- A **matrix runner** that can drive:
  - Rust clients/servers (`tokio-modbus`, embedded stacks),
  - hardware gateways / PLC simulators (via TCP/serial adapters),
  - third-party simulators.
- **Evidence bundles** (`*.modbusbundle.zip`) with request/response traces, timing, and device fingerprints.

## Why it is missing / worth building

The Modbus application protocol is stable and widely deployed; Rust crates exist, but teams integrating with industrial devices still spend time chasing vendor quirks and subtle PDU interpretation differences. A “missing middle” is a **shared conformance corpus + canonical trace format** so that a bug report can be “here’s the bundle” rather than “it fails sometimes”.

## Non-goals

- Not a new Modbus implementation (reuse existing crates).
- Not a full PLC simulator (integrate with existing ones).

## Proposed design

### Workspace layout

- `modbus-evidence-core`
  - canonical IR + bundle I/O + redaction (serial numbers, IPs)
- `modbus-fixtures`
  - function-code corpora with expected responses (including exception cases)
- `modbus-adapters`
  - `tokio-modbus` adapter
  - serial adapter (RTU) via `tokio-serial`
  - pcap/wireshark export adapter (optional)
- `modbus-matrix`
  - scenario DSL + runner + compatibility matrix generator

### Canonical IR sketch

- `Request { transport, unit_id, function, addr, quantity, data_ref }`
- `Response { ok|exception(code), data_ref, timing }`
- `TransportMeta { rtu_crc_ok, tcp_tid, framing_errors }`

### Evidence bundle (`*.modbusbundle.zip`)

- `manifest.json` (device fingerprints, adapter versions)
- `trace.jsonl` (canonical IR events)
- `expectations/` (optional fixture expectations)
- `report.md` (semantic diff + likely cause notes)

## Minimum lovable MVP (4–8 weeks)

1. Canonical IR + bundle format + diff renderer.
2. `tokio-modbus` adapter + 30–50 fixture cases (read coils/regs + exceptions).
3. Matrix runner that can compare 2 targets (e.g., Rust server vs device).

## De-risk plan

- Start with TCP first (easier automation), then add RTU framing.
- Keep fixtures narrowly focused: high-value function codes + exceptions.
- Validate IR against the Modbus Application Protocol spec early.

## Scorecard (0–5)

- Impact: 4
- Neglectedness: 3
- Feasibility: 4
- Adoptability: 4
- Sustainability: 4
- Differentiation: 3
