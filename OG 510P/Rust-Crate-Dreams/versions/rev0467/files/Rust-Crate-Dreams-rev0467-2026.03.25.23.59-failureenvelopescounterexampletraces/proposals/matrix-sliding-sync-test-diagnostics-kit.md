---
id: P-0190
title: Matrix Sliding Sync Test & Diagnostics Kit — interop harness + evidence bundles for long-polling sync correctness
status: idea
domains: [matrix, chat, testing, interoperability, protocols]
last_reviewed: 2026-03-05
evidence:
  - https://matrix-org.github.io/matrix-rust-sdk/matrix_sdk/sliding_sync/index.html
  - https://github.com/matrix-org/matrix-rust-sdk/issues/1579
  - https://gitlab.futo.org/circles/matrix-rust-sdk/-/blob/matrix-sdk-crypto-js-0.1.4/testing/sliding-sync-integration-test/README.md
  - https://docs.rs/matrix-sdk/latest/matrix_sdk/
---

# Problem

Sliding Sync is designed for scalable room lists and timelines, but long-polling sync correctness is easy to regress:

- subtle ordering/position semantics,
- encryption-driven sorting constraints,
- reconnection behavior and backoff,
- state gaps, pagination, and timeline “holes”.

Developers need a way to **reproduce interop issues** across servers/proxies and clients, with portable artifacts.

# What it provides

A kit that makes Sliding Sync correctness testable, CI-friendly, and debuggable.

Deliverables:

- `matrix-sliding-sync-harness` crate: spin up a Matrix homeserver + sliding sync proxy + test client(s) as a programmable topology.
- `cargo matrix-sync test`: run scenario suites (room list paging, sorting, timeline backfill, reconnect loops).
- Artifact bundle: `*.slidingsync.zip` containing:
  - request/response transcripts,
  - timeline position graphs, pagination markers,
  - redacted event samples,
  - `report.json` with stable diffs and failure classification (“gap”, “rewind”, “ordering”, “E2EE sort mismatch”, etc.).
- Conformance packs:
  - “behavioral” expectations derived from spec + de-facto ecosystem behavior,
  - regression fixtures from real bugs.

# Users & user stories

- **Client dev**: “I want to test that paging and sorting stay stable across proxy/server upgrades.”
- **SDK maintainer**: “I need minimized repro bundles from bug reports.”
- **Homeserver/proxy operator**: “I want smoke tests to ensure sliding sync remains healthy after config changes.”

# Prior art (and why it’s insufficient)

- The Matrix Rust SDK documents Sliding Sync and has ongoing engineering meta-work, and there are integration test harnesses—but there isn’t a widely adopted, portable artifact format for sharing failures across teams.

# Design goals

- Artifact-first: every failure yields a shareable bundle.
- Deterministic scenario seeds to reduce flakiness.
- Redaction safe-by-default.
- Interop focus (server/proxy/client permutations).

# Non-goals

- A full Matrix spec test suite.
- Replacing end-to-end encryption correctness testing (but it can integrate signals).

# Architecture & API sketch

- `Topology`: server, proxy, client, network conditions.
- `Scenario`: operations + expected invariants.
- `Capture`: transcript + derived graphs + metrics.
- Adapters: different homeservers, different proxy implementations.

# Security / safety model

- Redaction policies for event content and user identifiers.
- Bundle format designed for safe sharing by default.

# Maintenance & governance plan

- Keep bundle schema versioned and stable.
- Accept scenario pack contributions via a curated process; document “known flaky” patterns.

# Milestones

1. MVP: harness + 8 scenarios + bundle emission + CI runner.
2. v0.5: failure minimization + derived graphs + “doctor” heuristics.
3. v1.0: interop matrix runner + curated scenario packs + publishable report.

# Open questions

- How to best represent timeline positions and gaps in a stable, diffable way?
- Default homeserver/proxy choices for the CI matrix?

# Sources

- https://matrix-org.github.io/matrix-rust-sdk/matrix_sdk/sliding_sync/index.html
- https://github.com/matrix-org/matrix-rust-sdk/issues/1579
- https://gitlab.futo.org/circles/matrix-rust-sdk/-/blob/matrix-sdk-crypto-js-0.1.4/testing/sliding-sync-integration-test/README.md
- https://docs.rs/matrix-sdk/latest/matrix_sdk/
