---
id: P-0185
title: Matrix Sliding Sync Interop Workbench Kit
status: idea
domains: [messaging, federation, web, tooling, conformance, reliability]
last_reviewed: 2026-03-05
evidence:
  - https://matrix-org.github.io/matrix-rust-sdk/matrix_sdk/sliding_sync/index.html
  - https://matrix.org/blog/2024/11/14/moving-to-native-sliding-sync/
  - https://gitlab.futo.org/circles/matrix-rust-sdk/-/tree/24e3ccfbb33b78bfbdc832e50acc43fa12b5a718/testing/sliding-sync-integration-test
---

# Problem

Matrix client/server sync is notoriously hard to make **bandwidth-efficient, correct, and debuggable**.
Sliding Sync raises the bar (fine-grained server filtering, UI-shaped APIs), but in practice it introduces:

- lots of server/client version skew,
- subtle “UI correctness” bugs (lists, room ordering, unread counts),
- and debugging pain because the raw sync surface is large and privacy-sensitive.

Rust has strong building blocks (notably the Matrix Rust SDK and its Sliding Sync module), but the ecosystem lacks a **portable interop lab** that turns failures into shareable artifacts.

# What it should provide

## A. A scenario harness that speaks “messenger UI”
A suite of named scenarios that reflect what real clients do:

- list virtualization (windowing), room list sorting/pinning,
- membership changes (invite/join/leave), device changes,
- unread counters, notification rules, and “mark read” semantics,
- incremental state vs full state recovery,
- multi-device concurrency (racey updates).

Each scenario produces a deterministic expected outcome (“UI snapshot”), not just protocol-level assertions.

## B. A portable `*.matrixbundle.zip` format

A shareable bundle that allows triage without leaking private content:

- `report.json` (scenario, versions, homeserver build info, pass/fail + normalized errors)
- `requests/` (captured Sliding Sync requests/responses, deterministic ordering)
- `redaction.json` + `redacted/` (proof of redaction; stable content hashing)
- `fixtures/` (synthetic rooms/users event generators, seeds)
- `replay/` (scripts to replay against a local Synapse/Dendrite test stack)

## C. `cargo matrix-interop …` UX (client + server focus)

- `cargo matrix-interop doctor` — checks server config and common failure modes (proxy vs native support, required endpoints).
- `cargo matrix-interop run --scenario roomlist-windowing` — runs harness locally or in CI.
- `cargo matrix-interop bundle` — emits `matrixbundle.zip` with redaction + reproducibility metadata.
- `cargo matrix-interop diff` — compares two bundles (regression detection across upgrades).

# MVP (ship in weeks)

- A Docker-compose “mini matrix” stack + a small seed generator (synthetic rooms + users).
- 5–8 scenarios focused on room list correctness and unread counts.
- Bundle format + redaction policy (hash-only for event bodies; keep structural fields).
- CI profile: sharded tests + summary `report.json`.

# v1 (ship in months)

- Multi-homeserver matrix (Synapse + Dendrite + Conduit) and version matrix support.
- “Known-bad” corpus of failures (regression tests) and minimization tooling.
- Public conformance dashboards and a compatibility matrix output.

# Design constraints / risks

- Privacy: redaction must be first-class; default to structural hashes, never plaintext.
- Flakiness: focus on deterministic seeds and timestamp control.
- Scope: keep “one thing”: Sliding Sync correctness + reproducible evidence.
