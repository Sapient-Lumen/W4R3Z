---
id: P-0122
title: QUIC + HTTP/3 Interop & Capture Kit (qlog/pcap bundles)
status: idea
domains: [networking, http3, quic, devtools, standards]
last_reviewed: 2026-03-05
evidence:
  - https://github.com/quic-interop/quic-interop-runner
  - https://interop.seemann.io/
  - https://datatracker.ietf.org/doc/draft-ietf-quic-qlog-main-schema/
  - https://quicwg.org/implementations
  - https://github.com/quinn-rs/quinn
---

# Problem

Rust has strong QUIC implementations, but “it works on my machine” is not interop.
Teams debugging QUIC/HTTP/3 issues routinely juggle:

- per-impl logging formats and ad-hoc flags,
- packet captures that are hard to share safely,
- lack of repeatable, CI-friendly interop smoke tests,
- drift between protocol features (0-RTT, migration, H3 SETTINGS, WebTransport, etc.).

Meanwhile, the ecosystem has **automated interop matrices** and **standard logging formats** (qlog),
but Rust users lack a *batteries-included* crate + workflow that makes interop and debugging routine.

# What it should provide other people

## 1) A standard shareable artifact: `*.quicbundle.zip`

A “bug bundle” format designed for sharing with maintainers, vendors, and CI artifacts:

- `meta.json` (versions, build flags, OS, CPU, runtime, feature flags),
- `qlog/` traces (client + server),
- optional `pcapng` (with documented capture rules),
- `tls/` (optional key log file redaction strategy),
- `h3/` decoded events (where possible),
- `repro/` scripts (single command “replay” on docker/podman),
- `summary.md` (human notes),
- `report.json` (machine summary: handshake, streams, errors, timings).

The focus: **portable debugging with least-surprise privacy defaults**.

## 2) `cargo quic-interop` workflows

A cargo subcommand that makes the common loops easy:

- `cargo quic-interop run` — run local client/server tests and emit a bundle.
- `cargo quic-interop matrix` — run against known docker images (interop-runner style).
- `cargo quic-interop verify` — validate that a bundle is complete, versioned, reproducible.
- `cargo quic-interop doctor` — suggest missing kernel settings, MTU issues, UDP blocked, etc.

## 3) A conformance suite and profiles

Profiles (similar to “lint levels”) with increasing cost:

- `smoke`: handshake + 1 request + close cleanly
- `compat`: ALPN/H3 settings compatibility, flow control edges
- `mobility`: NAT rebinding, path migration scenarios
- `resumption`: 0-RTT vs 1-RTT behavior and safety checks
- `webtransport`: basic session tests (optional)

Each test emits structured events and a stable result schema.

# Design sketch

## Core crates

- `quicbundle` (format + validation)
- `quic-interop-harness` (scenario DSL + runner)
- `cargo-quic-interop` (UX)

## Integration strategy

- “Connector traits” for QUIC engines (Quinn-first, but pluggable).
- Optional adapters for:
  - docker-based interop-runner orchestration,
  - qlog generation (pass-through if impl already emits qlog),
  - pcap capture (platform-specific adapters, off by default).

# MVP (credible in 2–6 weeks)

- Bundle schema + validator + bundle writer.
- Quinn harness adapter (client+server minimal).
- 3–5 core scenarios: handshake, H3 GET, stream reset, idle timeout, close.
- `cargo quic-interop run` and `doctor` (basic).

# v1 scope (what makes it epic)

- Multi-impl adapters (Quinn + at least one more Rust impl or rustls/UDP stack integration).
- Docker matrix runner compatible with the community interop runner conventions.
- “Bundle scrubber” mode: redact hostnames, IPs, headers, key logs.
- Stable JSON report schema + golden fixtures for CI regressions.

# Testing and correctness

- Deterministic scenario inputs (seeded).
- Continuous fuzzing for bundle parser/validator.
- Golden bundles checked into repo as fixtures (small, sanitized).

# Risks and non-goals

- Not a full protocol verifier: it is **interop regression tooling**.
- pcap/key handling is sensitive: default safe, opt-in for deep traces.
- Avoid hard binding to any single runtime (Tokio/async-std) where feasible.

# Adoption path

1) Start as a devtool + bundle format.
2) Encourage QUIC implementers to emit qlog by default behind flags.
3) Grow connectors and an “interop badge” (publishable CI output).
