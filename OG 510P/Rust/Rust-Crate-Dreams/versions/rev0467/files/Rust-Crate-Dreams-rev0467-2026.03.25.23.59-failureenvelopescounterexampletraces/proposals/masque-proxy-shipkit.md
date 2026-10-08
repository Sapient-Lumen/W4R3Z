---
id: P-0174
title: MASQUE Proxy ShipKit — CONNECT-UDP/CONNECT-IP proxying with qlog bundles, policies, and interop matrices
status: idea
domains: [networking, quic, http3, proxying, security, interoperability]
last_reviewed: 2026-03-05
evidence:
  - https://datatracker.ietf.org/doc/html/rfc9298
  - https://www.rfc-editor.org/info/rfc9298
  - https://datatracker.ietf.org/doc/draft-ietf-masque-connect-udp-listen/
---

## What it should provide others

A **production-ready Rust MASQUE proxy** (and client helpers) that makes modern proxying over HTTP/3 achievable without a pile of bespoke glue.

Deliverables:

- `masque` crate (server + client building blocks):
  - CONNECT-UDP implementation per RFC 9298. citeturn0search1turn0search10
  - Policy engine for destination allow/deny, rate limiting, and per-tenant quotas.
  - Observability hooks: `tracing` spans and optional qlog capture.
- `cargo masque doctor`:
  - validates QUIC/H3 config (ALPN, cipher suites, congestion control knobs),
  - checks MTU/PMTUD assumptions,
  - runs a small local interop harness.
- Evidence bundles:
  - `*.masquebundle.zip`: request metadata, negotiated params, qlog, normalized failure taxonomy, and replay scripts.

## Why this is still missing

MASQUE-style proxying is becoming a key primitive for privacy-preserving VPN-like experiences, UDP tunneling, and “proxy-as-a-service”, but Rust teams often face:

- implementation complexity around H3 and UDP datagrams,
- lack of standardized “what went wrong” artifacts (qlog + negotiated transport params),
- missing conformance matrices across client stacks.

## MVP scope

- CONNECT-UDP server (single target host/port) + client.
- Minimal interop scenarios: DNS-over-HTTPS-like UDP, simple game/voice UDP flows.
- Bundle + replay runner for failure reproduction.

## v1 roadmap

- Add support for “listen/multi-host within a flow” extensions where applicable. citeturn0search7
- Interop runner mode: run against a matrix of known implementations (when available).
- Add CONNECT-IP support (where standardized/available) with clear capability negotiation.

## Design principles

- **Debuggability > benchmarks-first**: ship with artifact capture on day one.
- **Policy-first**: operators need constraints (destinations, quotas, auth) baked in.
- **Interop-first**: conformance suites and scenario packs are part of the “crate”.

