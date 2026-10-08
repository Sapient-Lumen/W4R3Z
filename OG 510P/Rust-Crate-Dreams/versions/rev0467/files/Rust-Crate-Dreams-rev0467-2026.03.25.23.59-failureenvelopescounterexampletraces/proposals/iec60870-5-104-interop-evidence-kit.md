---
id: P-0284
title: IEC 60870-5-104 Interop & Evidence Kit — canonical ASDU traces, timing checks, and replayable SCADA repro bundles
status: idea
domains: [industrial, scada, networking, interoperability, testing, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://www.openmuc.org/iec-60870-5-104/
  - https://github.com/Fraunhofer-FIT-DIEN/iec104-python
  - https://crates.io/crates/iec104
  - https://crates.io/crates/iec60870-5-104
---
## What it should provide others

A **PCAP-first** and **scenario-first** toolkit for IEC 60870-5-104 interoperability:
- canonical, diffable **ASDU/IOA-level traces**
- timing/sequence checks (t1/t2/t3 style, sequence numbers, confirm behaviors)
- replayable, redactable **`*.iec104bundle.zip`** repro artifacts for vendor bugs and CI

This fills a gap between “protocol libraries exist” and “we can reliably diagnose interop failures across devices and gateways”.

## Core crate shape (workspace)

- `iec104-ir` — canonical ASDU IR, normalization rules, stable hashing
- `iec104-pcap` — decode from pcap/pcapng to IR (with packet timing preserved)
- `iec104-runner` — scenario runner (master/slave roles), deterministic transcript recording
- `iec104bundle` — bundle IO + redaction (IP/hostnames) + signing hooks (optional)

## Bundle format: `*.iec104bundle.zip`

- `manifest.json` — device roles, timing model, capture provenance
- `trace.jsonl` — canonical APDU/ASDU events + timestamps
- `pcap/` — optional original capture (or redacted capture)
- `checks/` — machine-readable check results (sequence, timeouts, malformed ASDUs, unexpected confirmations)
- `replay/` — minimal scenario spec + seeds for deterministic runner

## MVP (4–8 weeks)

1. IR + pcap decoder producing stable `trace.jsonl`.
2. 10–20 conformance checks that catch common field failures.
3. Minimal runner that can:
   - connect as master
   - issue general interrogation + time sync
   - record everything into a bundle
4. `iec104bundle diff` CLI (first divergence + timing drift report).

## De-risk plan

- Anchor on open, well-understood behaviors; avoid promising “full certification”.
- Make pcap decode the first-class path; runner is for reproduction, not replacement.
- Provide adapter hooks so users can integrate vendor devices without embedding secrets.
