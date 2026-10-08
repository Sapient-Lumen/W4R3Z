---
id: P-0126
title: qlog Insights & Visualization Kit (analyze + diff + shareable bundles)
status: idea
domains: [networking, quic, http3, observability, devtools, standards]
last_reviewed: 2026-03-05
evidence:
  - https://datatracker.ietf.org/doc/draft-ietf-quic-qlog-main-schema/
  - https://crates.io/crates/qlog
  - https://github.com/quicwg/qlog
  - https://crates.io/crates/quiche
---

# Problem

qlog exists specifically to make network protocol logs **shareable and toolable**. citeturn1search7  
Rust now has an actively updated `qlog` implementation crate covering the main schema and QUIC/HTTP3/QPACK events. citeturn1search3  
Yet most Rust QUIC users still lack:

- a “default analysis toolchain” for qlog,
- portable, safe-to-share artifacts,
- and stable diffs that catch regressions (latency, loss recovery behavior, congestion control).

In practice, logs get stuck as ad-hoc JSON dumps, and analysis is bespoke.

# What it should provide other people

## 1) A portable artifact: `*.qloginsights.zip`

- `input/trace.qlog` (or multiple traces)
- `normalized/events.parquet` (optional; for big logs)
- `report.json` (key metrics + anomalies + schema versions)
- `graphs/` (SVG/JSON chart specs)
- `diff/` (optional baseline comparison)

## 2) A CLI + library: `qloginsights` + `cargo qlog`

- `cargo qlog capture` — capture qlog from known Rust stacks (quiche/quinn) via config hints
- `cargo qlog summarize` — canonical metrics (handshake RTT, loss bursts, PTOs, cwnd evolution)
- `cargo qlog diff` — compare two runs, output stable report + threshold gates
- `cargo qlog doctor` — validate schema, detect partial logs, suggest flags

## 3) A “common metrics” registry

A minimal curated set of metrics that are:
- cross-implementation meaningful,
- stable across versions,
- and actionable (point to likely causes).

# MVP (2–4 weeks)

- Robust ingestion for qlog main schema + QUIC events
- Emit `report.json` with a baseline set of metrics
- `diff` support for metric tables (not raw events)
- Validate against the qlog schema docs and event docs

# v1 (8–12 weeks)

- Optional pcap association (when present)
- Congestion-control specific lenses (e.g., BBR/CUBIC heuristics)
- Regression gates usable in CI for protocol stacks
- Plugin system: custom metrics without forking

# Conformance & testing

- Golden corpus from public qlog samples + synthesized traces
- Property tests: sorting/canonicalization invariants; robust handling of missing fields
- Cross-check schema versions against the IETF draft and `qlog` crate semantics citeturn1search7turn1search3

# Adoption plan

- Start as a standalone tool used by QUIC crate maintainers (quiche/quinn)
- Provide small integration snippets for “enable qlog + emit file”
- Encourage “attach `.qloginsights.zip` on bug reports” norm

# Risks / edge cases

- Large logs: need streaming ingestion + optional columnar materialization
- Multiple schema versions: must keep adapters + compatibility table
- Privacy: redact connection IDs/addresses by default; explicit unsafe modes
