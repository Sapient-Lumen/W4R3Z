---
id: P-0278
title: ActivityPub Federation Interop & Evidence Kit — canonical federation traces, replay, and redaction-first bundles
status: idea
domains: [web, federation, social, activitypub, interoperability, testing]
last_reviewed: 2026-03-05
evidence:
  - https://www.w3.org/TR/activitypub/
  - https://www.w3.org/news/2018/activitypub-is-now-a-w3c-recommendation/
  - https://github.com/w3c/activitypub
  - https://crates.io/crates/activitypub-federation
---

## What it should provide others

A **federation debugging and conformance harness** that turns “it federates with Mastodon but not with X” into:
- a **canonical trace IR** (HTTP requests, signatures, inbox/outbox semantics, delivery retries)
- **privacy-safe evidence bundles** (`*.apubbundle.zip`) for bug reports
- a scenario runner that can test **server-server federation behaviors** across implementations

This should complement existing Rust federation frameworks (e.g., `activitypub-federation`) by providing **measurement, fixtures, and interop CI**, not another framework.

## Why it matters

ActivityPub is a W3C Recommendation and widely implemented, but real-world federation has “gray areas” (HTTP signature variations, JSON-LD quirks, retry behavior, moderation side-effects). Interop failures are expensive to debug because logs are:
- non-portable
- privacy-sensitive
- hard to compare across stacks

## Proposed crate shape (workspace)

- `apubkit-ir` — canonical IR for federation events (deliveries, derefs, signature verification outcomes, side-effects)
- `apubkit-capture` — middleware for common Rust web stacks (axum/hyper) to emit IR; pluggable signature-verifier hooks
- `apubkit-runner` — multi-server topology runner (docker-compose optional), scenario DSL
- `apubkit-diff` — semantic diff + “first divergence” explorer
- `apubkit-bundle` — `*.apubbundle.zip` IO + redaction profiles

### Bundle-first contract

An `apubbundle` is a shareable folder-in-a-zip:
- `topology.json` (roles/hosts)
- `requests/` canonicalized HTTP exchanges (headers normalized, bodies hashed)
- `events.jsonl` canonical IR stream
- `redaction.json` policy + what was removed
- `verdicts/` scenario outcomes

## Minimum lovable MVP (4–8 weeks)

1. `apubkit-bundle` + schema + deterministic canonicalization for HTTP exchanges
2. `apubkit-capture` middleware for axum/hyper
3. `apubkit-runner` with 3 baseline scenarios:
   - follow / accept
   - create note / deliver
   - delete / tombstone propagation

Deliverable: `cargo apubkit run --scenario follow --out run.apubbundle.zip`.

## De-risk plan

- Avoid JSON-LD “full expansion” in MVP; start with **stable canonicalization + hashing** and record raw payloads behind redaction.
- Ship an “interoperability matrix” report generator early; that’s high user value.

## Scorecard (0–5)

- Impact: 4
- Neglectedness: 4
- Feasibility: 3
- Adoptability: 4
- Sustainability: 3
- Differentiation: 5 (portable federation evidence bundles + semantic diff)
