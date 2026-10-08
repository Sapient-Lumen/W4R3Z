---
id: P-0165
title: Automotive Diagnostics & ISO-TP Workbench Kit — CAN + ISO-TP + UDS evidence bundles and replay
status: idea
domains: [automotive, canbus, diagnostics, embedded, linux, dx]
last_reviewed: 2026-03-05
evidence:
  - https://crates.io/crates/socketcan
  - https://docs.rs/socketcan/latest/socketcan/
  - https://crates.io/crates/socketcan-isotp
  - https://docs.rs/socketcan-isotp
  - https://crates.io/keywords/isotp
---

# Problem
Rust can talk to SocketCAN and ISO-TP, but *end-to-end diagnostics workflows* are fragmented: frame capture, ISO-TP segmentation, UDS request/response, DBC decoding, timeouts, and “what exactly happened on the bus?” debugging remain bespoke.

# What this crate should provide (to other people)
A workbench that turns bus debugging into a reproducible artifact:

- `auto-diag-kit` library + `cargo auto-diag`:
  - record CAN traffic + ISO-TP streams
  - normalize timestamps, arbitration IDs, and flow control
  - optional DBC decode adapters
- A stable `autodiag-bundle.zip`:
  - `report.json` (vehicle profile, kernel, interface params, errors)
  - `can.pcapng`/`candump.log` (or normalized JSONL)
  - `isotp.jsonl` (reassembled payloads + segmentation events)
  - optional `uds.jsonl` (service IDs, NRCs, timing)
- `cargo auto-diag replay`:
  - replay a bundle into an emulated ECU target (or a harness) to reproduce bugs.

# Prior art (and why it’s insufficient)
- `socketcan` makes CAN on Linux accessible, but stops at frames. citeturn0search1turn0search25
- `socketcan-isotp` adds ISO-TP but doesn’t deliver an ops/debug “bundle + replay” workflow. citeturn0search2turn0search29
- ISO-TP/UDS is common enough to warrant a standardized Rust “diagnostics incident” artifact. citeturn0search6

# Design goals
- **Reproducibility**: every bug report can ship a bundle with enough context to replay.
- **Pluggable**: works with different capture formats, DBC libraries, and async runtimes.
- **Safety**: never sends on-bus traffic by default; “active” modes are opt-in with explicit gating.
- **Deterministic parsing**: identical bundle → identical decoded stream.

# Architecture
- `auto-diag-core`: event model + stable schemas + redaction
- `auto-diag-can`: SocketCAN capture + pcapng/candump adapters
- `auto-diag-isotp`: reassembly + flow control telemetry
- `auto-diag-uds` (optional): UDS primitives (service IDs, NRC parsing, timing windows)
- `auto-diag-cli`: record, bundle, replay, doctor

# Bundle schema sketch
- `report.json`: interface, bitrate, filters, kernel/module versions, errors
- `events/can.jsonl`: raw frames + timestamps
- `events/isotp.jsonl`: reassembled payloads + segmentation metadata
- `events/uds.jsonl` (optional): request/response, NRCs, timings
- `redaction.toml`: identifiers stripped (VIN, serials) per policy

# Conformance & testing
- Include reference corpora for ISO-TP reassembly edge cases (FC timing, STmin, wrap).
- Property tests for segmentation/reassembly.
- Optional “virtual ECU” harness for deterministic replay.

# Milestones
- 0.1: CAN capture + normalized JSONL + bundle writer
- 0.2: ISO-TP reassembly + isotp JSONL
- 0.3: UDS decoding + timing diagnostics
- 0.4: replay harness + conformance corpus
