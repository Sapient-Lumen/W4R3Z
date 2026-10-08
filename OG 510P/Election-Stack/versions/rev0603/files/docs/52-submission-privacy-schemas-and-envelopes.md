# 52 — Submission privacy schemas & envelopes — draft

**Track:** B (Remote return / hard-mode research)



> **Deployment honesty:** Track B documents are **exploratory** and are **not deployment guidance**.
> Before reading, review [`docs/167` non-claims](167-non-claims-and-boundaries.md) (especially **N-2**) and the [`Track B → Track A promotion protocol`](229-experiment-to-spec-promotion-protocol.md).

This document defines message envelopes used by `49-anonymous-submission-layer-ohttp-odoh.md`
and `50-anonymous-rate-limiting-and-ddos.md`.

## Envelope invariants
- Fixed-size buckets (e.g., 4 KB / 16 KB / 64 KB) with deterministic padding rules.
- Content addressability for evidence bundles (hash of canonical JSON).
- Context binding: every envelope MUST include `election_id` and `gateway_id`.

## Objects
- `RelayEnvelope` (schema: `schemas/RelayEnvelope.json`)
- `RateLimitToken` (schema: `schemas/RateLimitToken.json`)