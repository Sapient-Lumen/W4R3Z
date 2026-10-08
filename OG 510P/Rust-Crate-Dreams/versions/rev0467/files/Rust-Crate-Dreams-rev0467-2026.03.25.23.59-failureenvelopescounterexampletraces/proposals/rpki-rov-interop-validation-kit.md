---
id: P-0207
title: RPKI / ROV Interop & Validation Kit — bundle-first route-origin validation replay and explanation
status: idea
domains: [networking, routing-security, rpki, validation, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://datatracker.ietf.org/doc/html/rfc6480
  - https://nlnetlabs.nl/projects/routing/routinator/
  - https://github.com/NLnetLabs/routinator
---
# P-0207: RPKI / ROV Interop + Evidence Kit

**One-liner:** A bundle-first toolkit to **validate, reproduce, and explain** RPKI Route Origin Validation (ROV) outcomes (and related routing-security workflows) across validators, caches, and policy regimes.

## Why this is missing (the gap)
Rust already has serious RPKI software (e.g., **Routinator** is an RPKI relying-party validator written in Rust). But teams still struggle to:
- reproduce “why was this route VALID/INVALID/UNKNOWN?” across **different validators / data snapshots / local policy**
- create **portable incident artifacts** (redactable) for postmortems, audits, and CI “known-bad” regression tests
- run conformance-ish checks over ROA repositories, RTR feeds, and validation pipelines without wiring bespoke glue

RPKI provides the infrastructure for improved routing security (RFC 6480). The ecosystem lacks a *developer-facing* crate that makes **ROV results inspectable and replayable** with minimal operational heavy-lifting.

## Target users
- ISPs / IXPs / enterprise netops doing ROV rollouts and incident response
- router vendors / control-plane teams
- researchers testing routing security assumptions
- CI/QA pipelines for routing policy tooling

## Core idea: evidence bundles
Introduce a portable artifact format: `*.rpkibundle.zip`

Contains (redactable):
- **inputs**: ROA/manifest/snapshot sources or pointers + fetch metadata, plus optional RTR cache dumps
- **policy**: local preferences (e.g., “prefer this cache”), max-age, trust-anchor config
- **observations**: routes (prefix, origin AS), timestamps, validator versions
- **outputs**: per-route verdicts with **explanations** + provenance links to source objects

The bundle should allow:
- deterministic “replay” of validation for a given route set
- semantic diffs between validators/policies (what changed and why)
- generating human-readable incident reports

## Crate shape (workspace)
- `rpki_bundle` — bundle schema, redaction, signing, normalization
- `rpki_fetch` — fetchers and snapshotter (HTTP rsync RRDP) with cache controls
- `rov_engine` — validator-agnostic ROV evaluation interface (traits), plus reference implementation adapters
- `rov_explain` — explanation graph: *which ROA, which certificate chain, which constraints*
- `rtr_client` — consume RFC 6810/8210-ish RTR feeds (optional; trait-first)
- `cli` (optional) — `rovkit` to build bundles, replay, diff, and print explanations

## MVP (4–8 weeks)
1. Bundle format v0.1 with: routes list + validator metadata + fetched ROA set snapshot manifest
2. Deterministic evaluator for route→(valid/invalid/unknown) with explanation stubs
3. “Diff two bundles” producing semantic deltas and a short report
4. Redaction presets (strip raw certs; keep hashes + minimal chain evidence)

## De-risk plan
- Start with “bundle builder” that can ingest:
  - a local Routinator JSON export or similar snapshot
  - a set of prefixes/origins
- Validate determinism with golden bundles in CI
- Add fetchers later; don’t block on full RRDP/rsync coverage

## Interop surface
- Pluggable adapters for existing validators / caches (Routinator first)
- Keep core crate `no_std`-friendly where possible (bundle parsing + hashing)

## Scorecard (0–5)
- Impact: 4
- Neglectedness: 4
- Feasibility: 3
- Adoptability: 4
- Sustainability: 3
- Differentiation: 5

## References
- IETF RPKI architecture: RFC 6480 — “An Infrastructure to Support Secure Internet Routing” (datatracker.ietf.org/doc/html/rfc6480)
- Routinator: Rust RPKI relying party validator (github.com/NLnetLabs/routinator; nlnetlabs.nl/projects/routing/routinator/)
