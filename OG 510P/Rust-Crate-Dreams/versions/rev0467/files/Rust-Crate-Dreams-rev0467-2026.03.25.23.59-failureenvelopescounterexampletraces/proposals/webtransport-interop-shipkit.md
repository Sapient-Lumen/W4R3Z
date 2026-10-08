---
id: P-0170
title: WebTransport Interop & ShipKit — “it just works” QUIC/HTTP3 transport for browsers + Rust servers
status: idea
domains: [networking, web, realtime, quic, http3, interop]
last_reviewed: 2026-03-05
evidence:
  - https://docs.rs/wtransport
  - https://crates.io/crates/wtransport
  - https://crates.io/keywords/webtransport
  - https://github.com/kixelated/webtransport-rs
---

## What it should provide others

A **production path** to ship WebTransport (browser ↔ Rust service) that is:

- **Interop-first**: reproducible traces and matrices across browsers/versions and QUIC stacks.
- **Operationally boring**: known-good TLS/ALPN/certs defaults; robust timeouts/backpressure; good errors.
- **Debuggable**: every failure yields a portable evidence bundle.

Deliverables (crate + cargo subcommand):

- `cargo webtransport doctor` — checks kernel/UDP, cert config, ALPN, HTTP/3 settings, MTU/PMTUD hints.
- `cargo webtransport capture` — emits `*.wtbundle.zip`:
  - minimal repro client/server,
  - negotiated params (ALPN, transport params),
  - qlog (if available),
  - normalized error taxonomy + timeline.

## Why this is still missing

Rust has building blocks, but teams keep re-inventing:

- WebTransport session setup, TLS/ALPN, and QUIC tuning.
- “Bug bundle” formats for filing issues upstream or cross-team.
- A small conformance matrix for the most common patterns (streams, datagrams, backpressure).

## Design principles

- **Adapter-based**: ship a small core around a stable “session + stream + datagram” API; provide adapters for `wtransport` and other implementations.
- **Evidence-first**: bundles + normalized reports are the collaboration unit.
- **Interop corpora**: keep a curated set of “known tricky” cases (datagram loss, stream resets, 0-RTT policy, idle timeouts).

## MVP

- A minimal server+client scaffold on top of `wtransport`.
- A `wtbundle.zip` schema + `report.json`.
- 10–15 scenario tests (streams + datagrams) and a CI job that runs them locally and in a headless browser (where feasible).

## v1

- Cross-implementation adapters; optional qlog ingestion; better minimization.
- Browser matrix runner integration points (not necessarily bundled).
- Compatibility/behavioral diffing between versions.

## Key risks / sharp edges

- Browser feature variance and evolving specs: treat the **scenario suite** as the stable product and keep adapters flexible.
- Debugging in production environments: keep capture lightweight and redactable.
