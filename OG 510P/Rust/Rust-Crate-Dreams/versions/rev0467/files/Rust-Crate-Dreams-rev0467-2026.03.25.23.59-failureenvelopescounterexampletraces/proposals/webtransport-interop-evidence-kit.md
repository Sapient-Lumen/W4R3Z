---
id: P-0265
title: WebTransport Interop & Evidence Kit — canonical transcripts + replay bundles for WebTransport over HTTP/3
status: idea
domains: [networking, web, http3, quic, testing, interoperability]
last_reviewed: 2026-03-05
evidence:
  - https://www.w3.org/TR/webtransport/
  - https://datatracker.ietf.org/doc/draft-ietf-webtrans-http3/
  - https://github.com/w3c/webtransport/blob/main/explainer.md
  - https://crates.io/crates/web-transport-quinn
  - https://github.com/kixelated/webtransport-rs
---

## What it should provide others

A **portable, redactable evidence workflow** for diagnosing and reproducing WebTransport failures across browsers, servers, and Rust implementations.

The crate should give users:

- **Capture → canonicalize → diff** of WebTransport sessions (handshake + stream/datagram events) into a stable IR.
- **Replay harness** for server-side regression tests (and optional client-side playback for wasm/browser).
- **Shareable repro bundles** (`*.wtbundle.zip`) with privacy-preserving redaction presets.
- **Interop matrices** across combinations of:
  - protocol modes (streams vs datagrams),
  - HTTP/3 settings and caps,
  - browser implementations,
  - Rust server stacks (e.g., Quinn-based).

## Why it is missing / worth building

WebTransport sits on top of HTTP/3/QUIC and must remain consistent with the browser security model; when it breaks, raw packet captures are often too heavy and too privacy-sensitive to share. A bundle format that is **lighter than pcap**, but **more faithful than logs**, is a missing middle.

Rust already has partial building blocks (Quinn + early WebTransport crates), but not a **conformance/evidence layer** that makes failures reproducible across stacks.

## Non-goals

- Not a full QUIC or HTTP/3 implementation.
- Not a browser automation framework (it should integrate with existing runners rather than replacing them).

## Proposed design

### Workspace layout

- `webtransport-evidence-core`: canonical IR + redaction + bundle I/O
- `webtransport-capture`:
  - adapters for Rust servers (quinn/h3/web-transport-quinn)
  - optional qlog correlation hooks (if available)
- `webtransport-replay`:
  - deterministic “server playback” runner
  - golden test runner
- `webtransport-matrix`:
  - scenario DSL + matrix runner

### Canonical IR sketch

- `SessionStart { url, origin, alpn, settings, cert_fingerprint? }`
- `H3Settings { … }`
- `StreamOpen { id, dir, reliable }`
- `Datagram { size, checksum?, redacted_payload_ref }`
- `Close { code, reason_hash }`

### Bundle format (`wtbundle.zip`)

- `manifest.json` (schema + tool versions + hash tree)
- `session.ir.jsonl` (canonical event stream)
- `redaction.toml` (what was removed/how)
- `attachments/` (optional: small qlog snippets, error stacks)

## MVP (4–8 weeks)

1. Server-side capture + canonical IR for streams + close reasons
2. Bundle writer/reader + basic redaction presets
3. Replay runner that reproduces server-side state machine failures
4. One interop matrix against a reference browser client (wasm wrapper allowed)

## Maintenance plan

- Keep core IR stable; evolve via versioned schemas.
- Maintain adapter crates separately so ecosystem churn doesn’t break the core.
