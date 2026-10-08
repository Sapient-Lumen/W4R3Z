---
id: P-0173
title: JMAP Email Client/Server Workbench Kit — modern email APIs with reproducible sync + push + attachment flows
status: idea
domains: [email, networking, web, sync, security, interoperability]
last_reviewed: 2026-03-05
evidence:
  - https://datatracker.ietf.org/doc/html/rfc8620
  - https://www.iana.org/assignments/jmap/jmap.xhtml
  - https://en.wikipedia.org/wiki/JSON_Meta_Application_Protocol
---

## What it should provide others

A **batteries-included, protocol-correct path** for building JMAP clients and servers in Rust (including “SDK ergonomics”), with a strong focus on:

- **Efficient sync** (states, changes, query deltas) and fast resync as described in JMAP Core. citeturn0search0
- **Push / realtime updates** (WebSocket transport, Web Push extensions) with predictable reconnection semantics.
- **Binary blobs done right** (upload/download, chunking, limits), plus safe streaming APIs.

Core deliverables:

- `jmap-core` crate: typed request/response models, validated method calls, state tracking helpers.
- `jmap-sync` crate: opinionated “sync engine” that produces deterministic **sync plans** and yields a portable bundle:
  - `*.jmapbundle.zip`: request/response logs (redacted), state strings, method graph, and a normalized `report.json`.
- `cargo jmap doctor`: validates server profiles (capabilities, limits, auth modes), and client configuration.

## Why this is still missing

JMAP’s purpose is to modernize email access over JSON/HTTP, replacing many of the complexity and inefficiency pain points of older protocols. citeturn0search0  
But in Rust today, teams still end up with:

- partial type models without a durable “sync brain”,
- ad-hoc push reconnection and state resync logic,
- weak, non-portable bug reports when servers disagree on edge cases (limits, states, errors).

## MVP scope

MVP focuses on “email-only JMAP”:

1. **Core**: request/response types, method call builder with validation, canonical error mapping (including standard error types registered with IANA). citeturn0search6turn0search0
2. **Sync engine**: `state` tracking, `changes` consumption, query delta helpers, and replayable “sync plan” output.
3. **Bundles**: `jmapbundle.zip` with:
   - a redaction pipeline (headers, addresses, bodies),
   - deterministic replay runner,
   - minimal failing transcript extraction.

## v1 roadmap

- Add profiles: “mobile-friendly” sync (bandwidth/latency aware), “offline-first”.
- Add server-side helpers: capability negotiation, rate limits/backoff standardization, pagination utilities.
- Interop test corpus: known tricky cases (mailbox rename, concurrent message moves, quota edge cases).

## Design principles

- **Artifact-first debugging**: every protocol disagreement should produce a portable bundle.
- **Interop-first**: build around a corpus + vectors early, not as an afterthought.
- **Redaction by default**: bundles must be safe to share.

