---
id: P-0215
title: QUIC + HTTP/3 Interop & qlog Evidence Lab Kit — scenario runner, canonical traces, and repro bundles
status: idea
domains: [networking, quic, http3, interop, observability, conformance]
last_reviewed: 2026-03-05
evidence:
  - https://datatracker.ietf.org/doc/html/rfc9000
  - https://datatracker.ietf.org/doc/html/rfc9114
  - https://datatracker.ietf.org/doc/draft-ietf-quic-qlog-main-schema/
  - https://quicwg.org/qlog/draft-ietf-quic-qlog-h3-events.html
needs:
  - A shared, Rust-native way to reproduce QUIC/HTTP3 interop failures across endpoints (handshake, 0-RTT, migration, datagrams, prioritization).
  - Canonical trace formats and diffs (qlog-first) so failures become shareable artifacts instead of “works on my network”.
  - A scenario DSL + runner that can drive multiple QUIC stacks and emit portable evidence bundles for CI triage.
risks:
  - QUIC stacks differ in feature coverage and draft support; must pin to profiles and produce explainable diffs.
  - qlog specifications are still evolving; must version schemas and support forward-compatible parsing.
---

## Problem

Interoperability bugs in QUIC/HTTP/3 are expensive because they often depend on timing, loss, and endpoint feature negotiation. QUIC v1 is specified in RFC 9000 and HTTP/3 in RFC 9114.
Source: https://datatracker.ietf.org/doc/html/rfc9000
Source: https://datatracker.ietf.org/doc/html/rfc9114

The ecosystem has good QUIC stacks, but lacks a **standardized interop lab crate** that:
- drives scenarios consistently,
- captures structured traces,
- diffs them deterministically,
- and emits **portable repro bundles**.

qlog provides a structured logging schema for QUIC, with separate event definitions including HTTP/3.
Source: https://datatracker.ietf.org/doc/draft-ietf-quic-qlog-main-schema/
Source: https://quicwg.org/qlog/draft-ietf-quic-qlog-h3-events.html

## What this crate should provide

### 1) `quic-lab` scenario DSL + runner
- A minimal declarative DSL (YAML/JSON) describing:
  - endpoint roles (client/server), ALPN, versions
  - congestion control profile
  - features (0-RTT, migration, datagrams, ext CONNECT, prioritization)
  - impairment profile (loss, delay, reordering) via pluggable backends
- Runner that can execute against adapters:
  - Rust stacks (native API adapters)
  - CLI adapters (drive external binaries) to broaden coverage

### 2) qlog capture + canonicalization
- Ingest qlog from endpoints (file/stdout/socket)
- Canonicalize to a stable “diffable” form:
  - stable ordering, normalized timestamps (relative timelines), stable connection IDs labeling
  - schema-version metadata and warnings

### 3) Differential analysis (“what changed?”)
- Compare two runs (or two stacks) and produce:
  - handshake transcript diffs
  - stream state machine diffs
  - HTTP/3 frame stream diffs
  - perf-ish summaries (RTT estimates, loss events) *without* claiming benchmark precision

### 4) Repro bundles: `*.qbundle.zip`
Bundle structure (redaction-first):
- `scenario.json`
- `endpoints.json` (versions, features, commit hashes)
- `netenv.json` (OS, kernel, tc/netem, container image)
- `client.qlog`, `server.qlog`
- `canon/client.json`, `canon/server.json`
- `diff/report.md`, `diff/report.json`
- optional: `pcapng` (if permitted)

### 5) Tooling UX
- `cargo quic-lab run scenario.yaml --adapter quinn --adapter msquic-cli`
- `cargo quic-lab diff a.qbundle.zip b.qbundle.zip`
- `cargo quic-lab triage *.qbundle.zip` (summarize likely causes)

## Prior art (and why it’s insufficient)

- QUIC and HTTP/3 are standardized (RFC 9000, RFC 9114), but testing remains fragmented across stacks.
  Source: https://datatracker.ietf.org/doc/html/rfc9000
  Source: https://datatracker.ietf.org/doc/html/rfc9114
- qlog provides structured logging, but teams still need runner orchestration, canonicalization, and reproducible bundles.
  Source: https://datatracker.ietf.org/doc/draft-ietf-quic-qlog-main-schema/

## MVP plan (4–8 weeks)

1. Define `scenario.json` schema + minimal runner that can:
   - start client/server processes
   - apply an impairment backend (initially “none” + `tc netem` adapter)
2. qlog ingestion + canonicalizer v0 (stable ordering + relative time)
3. `*.qbundle.zip` emitter + `diff` skeleton (handshake + stream open/close)
4. First fixture pack with 10 scenarios:
   - handshake, resumption, 0-RTT, stream reset, idle timeout, basic HTTP/3 GET

## Scorecard (0–5)
- Impact: 4
- Neglectedness: 4
- Feasibility: 3
- Adoptability: 4
- Sustainability: 3
- Differentiation: 5 (bundle-first qlog canonical diffs across stacks)
