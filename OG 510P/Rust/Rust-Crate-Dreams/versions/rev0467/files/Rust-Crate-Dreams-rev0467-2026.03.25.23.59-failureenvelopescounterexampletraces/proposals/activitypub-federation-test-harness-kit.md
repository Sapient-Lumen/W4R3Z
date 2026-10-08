---
id: P-0188
title: ActivityPub Federation Test Harness Kit — reproducible Fediverse interop, conformance, and bug bundles
status: idea
domains: [fediverse, activitypub, testing, interoperability, protocols]
last_reviewed: 2026-03-05
evidence:
  - https://www.w3.org/wiki/ActivityPub/Primer/Testing
  - https://www.sovereign.tech/tech/activitypub-test-suite
  - https://github.com/go-fed/testsuite
  - https://github.com/bonfire-networks/bonfire-app/wiki/ActivityPub-automated-test-suites
---

# Problem

ActivityPub implementations are hard to test because **correctness is emergent across federation** (multiple servers, async delivery, retries, signatures, inbox/outbox behavior, blocking rules, etc.). The common “spin up two servers and click around” approach is slow, non-reproducible, and doesn’t create portable artifacts that maintainers can triage.

# What it provides

A crate + CLI that turns federation testing into **portable, replayable evidence**.

Deliverables:

- `fediharness` crate: a programmable harness to stand up **multi-instance test topologies** (N servers, N users, proxy nodes).
- `cargo fediverse test`: run scenario suites locally or in CI.
- A standard artifact bundle: `*.fedibundle.zip` containing:
  - HTTP request/response transcripts (redacted), signature/verification traces, delivery timelines,
  - deterministic seeds and scenario manifests,
  - minimized failing scenario reproduction steps,
  - `report.json` with stable, diffable metrics (delivery latency percentiles, retry counts, signature failures, etc.).
- Conformance suite runner: map scenarios to normative requirements, but **also** test real-world interop quirks (pagination, redirects, blocked domains, inbox dedupe).
- “Interop matrix” mode: run scenario suites across a set of implementations and produce an interop report (suitable for publishable dashboards).

# Users & user stories

- **Fediverse server implementer**: “I want to know if my inbox handling breaks Mastodon/Pleroma/PeerTube-like behavior before I ship.”
- **Maintainer**: “I want a single zip a reporter can attach that reproduces the federation bug deterministically.”
- **Hosted operator**: “I want CI gates for federation regressions (signature verification, delivery timeouts, queue growth).”

# Prior art (and why it’s insufficient)

- Community discussions and partial test suite efforts exist, but are fragmented and often not “artifact-first”.
- Existing tools often focus on a single implementation or are not designed to yield minimized, shareable bug bundles.

# Design goals

- **Artifact-first** debugging (every failure yields a bundle).
- Determinism where possible (seeded schedulers, recorded time).
- Redaction-by-default (PII-safe sharing).
- Scenario-based conformance + real-world interop behavior.

# Non-goals

- Becoming “the” authoritative ActivityPub spec test suite overnight.
- Testing UI clients (initially); focus on server federation correctness.

# Architecture & API sketch

- Harness core:
  - `Topology` (nodes, users, routing rules)
  - `Scenario` (steps, assertions, invariants)
  - `Capture` (redacted transcript + metrics)
- Adapters:
  - “black box” adapter: drive servers via HTTP endpoints and standard ActivityPub routes
  - optional “white box” hooks for implementations that want richer internal traces

# Security / safety model

- Redaction policy must run before bundle emission.
- Bundles should be safe to share publicly by default (no bearer tokens, no private inbox URLs unless opted in).

# Maintenance & governance plan

- Maintain a small core of stable scenario semantics; allow implementations to contribute scenario packs.
- Compatibility policy for bundle format: versioned schema with forward-compatible parsing.

# Milestones

1. MVP: 2-node topology, 10 core scenarios, bundle emission, deterministic seed runner.
2. v0.3: redaction policies + minimization (reduce scenario steps / isolate failing interaction).
3. v1.0: interop matrix runner + publishable report format; curated scenario packs.

# Open questions

- How to best model eventual consistency (retries/backoff) without flakiness?
- How to encode normative requirements vs “de-facto interop expectations”?

# Sources

- https://www.w3.org/wiki/ActivityPub/Primer/Testing
- https://www.sovereign.tech/tech/activitypub-test-suite
- https://github.com/go-fed/testsuite
- https://github.com/bonfire-networks/bonfire-app/wiki/ActivityPub-automated-test-suites
