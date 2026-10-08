---
id: P-0134
title: spiffe-identity-kit — identity-source receipts, trust-domain policy, peer-identity extraction, and rotation-state bundles for Rust workload identity
status: idea
domains: [security, networking, identity, zero-trust, rustls, tower]
last_reviewed: 2026-03-20
evidence:
  - https://spiffe.io/docs/latest/deploying/libraries/
  - https://spiffe.io/docs/latest/spiffe-specs/spiffe/
  - https://spiffe.io/docs/latest/spiffe-specs/spiffe_workload_api/
  - https://spiffe.io/docs/latest/spiffe-specs/spiffe_federation/
  - https://docs.rs/crate/spiffe/latest
  - https://docs.rs/spiffe-rustls/latest/spiffe_rustls/
  - https://docs.rs/spiffe-rustls-tokio/latest/spiffe_rustls_tokio/
  - https://docs.rs/crate/spire-api/latest
---

# Problem

Rust now has credible SPIFFE/SPIRE substrate:

- official SPIFFE docs point Rust users to `spiffe` for Workload API access and `spiffe-rustls` for TLS/mTLS integration,
- the `spiffe` crate now provides typed SPIFFE IDs, Workload API clients, X.509/JWT sources, and automatic reconnection/rotation handling,
- `spiffe-rustls` provides live `rustls` builders backed by `X509Source`,
- `spiffe-rustls-tokio` can return `(TlsStream, PeerIdentity)` after a successful handshake,
- and `spire-api` now exposes SPIRE’s Delegated Identity API for constrained environments.

That means the ecosystem gap is no longer “Rust cannot speak SPIFFE”.
The gap is that downstream users still do not get one boring, reviewable answer to the questions they actually care about:

- Is this service using a **live Workload API source**, a **delegated identity source**, or a **static dev/test identity**?
- Do new handshakes actually pick up rotated SVIDs and trust bundles, and what is the runtime posture if the agent disappears or falls behind?
- Under federation, are we accepting **all bundles in the set**, a **specific allowlist**, or **local-only** trust?
- Does the application receive an explicit **peer identity object**, or is authorization hidden inside TLS configuration with no app-visible handoff?
- What portable, redacted bundle can another team inspect when identity or mTLS fails?

That is a different problem from another protocol crate.
The missing layer is a **receiver-facing workload-identity contract**.

# What it provides

A support-first crate family above the current SPIFFE/SPIRE substrate:

1. **Identity-source receipts**
- capture whether a subject uses:
  - live SPIFFE Workload API identity,
  - delegated identity from SPIRE,
  - static development identity,
  - or another narrower source mode
- record endpoint kind, socket/TCP route class, X.509 vs JWT path, and intended rotation behavior

2. **Trust-domain-policy receipts**
- capture whether verification accepts:
  - any trust domain present in the current bundle set,
  - a bounded allowlist,
  - local-only trust,
  - or an app-defined narrower policy
- keep federation posture separate from peer-ID authorization posture

3. **Peer-identity receipts**
- capture whether peer SPIFFE IDs are:
  - extracted and returned to application code,
  - verified but not surfaced,
  - or only partially surfaced through framework-specific adapters
- record where authorization runs: verifier-only, post-handshake authorizer, or application middleware/layer

4. **Rotation-state reports**
- capture whether new handshakes use updated SVIDs/bundles,
- whether rotation is watch-driven or periodic refresh,
- and what the crate claims when the identity source becomes unavailable

5. **Diff + bundle tooling**
- compare two captures and explain whether the change was about source basis, trust-domain scope, peer-identity surface, or rotation/failure posture
- emit a compact `.spiffesurfacebundle.zip`

# What the crate should provide other people

1. **A boring identity-source vocabulary** instead of “we use SPIFFE somehow”.
2. **Reviewable trust-domain policy** instead of vague federation/security claims.
3. **Explicit peer-identity handoff truth** so application code knows whether identity is available after TLS succeeds.
4. **Rotation-state honesty** so “supports rotation” does not hide stale-handshake or agent-loss ambiguity.
5. **A compact debug-bundle surface** that other teams can inspect without private keys or raw credentials.
6. **Diffable release/config changes** so a workload-identity change is reviewable like API or policy drift.

# Persona / who it’s for

- platform/security teams rolling out workload identity
- Rust service teams using `hyper`, `tonic`, `tower`, `axum`, or raw `tokio-rustls`
- library authors who want to publish a stable workload-identity support contract
- incident/debugging teams who need redacted artifacts for failed mTLS or missing-identity incidents

# Users & user stories

- **Platform engineer**: “Tell me whether this service is agent-backed, delegated, or static, and whether new handshakes actually pick up rotations.”
- **Service owner**: “Show me whether peer SPIFFE IDs are visible to my application or only enforced inside TLS.”
- **Security reviewer**: “Under federation, are we trusting every bundle from the Workload API or only a reviewed allowlist?”
- **Incident responder**: “Give me one redacted bundle explaining why identity issuance or peer authorization failed.”
- **Upgrade reviewer**: “Diff the identity surface between two releases and tell me whether the change widened trust domains, changed source basis, or altered peer-identity visibility.”

# Prior art (and why it’s insufficient)

- `spiffe` provides typed SPIFFE identifiers plus Workload API clients, watch semantics, and high-level X.509/JWT sources.
- `spiffe-rustls` provides live `rustls` integration with post-verification SPIFFE-ID authorization and federation-aware trust-domain bundle selection.
- `spiffe-rustls-tokio` provides tokio-native accept/connect helpers that can return `PeerIdentity`.
- `spire-api` provides SPIRE-specific APIs such as Delegated Identity.
- SPIFFE specifications define the Workload API, federation model, and trust semantics.

What remains missing is the joined, maintainer-authored artifact that says:

- which identity source the subject really uses,
- whether credential freshness is watch/live or static/staged,
- which trust domains are accepted,
- whether peer identity is returned to application code,
- what the failure posture is when the source disappears,
- and how those facts changed across releases or deployment modes.

That is a different lane from:

- inventing another identity protocol,
- building a full service mesh,
- replacing `rustls` or the SPIFFE crates,
- or building a general zero-trust policy platform.

# Design goals

1. **Source-first** — classify where identity material really comes from before promising anything about mTLS.
2. **Rotation-honest** — make freshness and source-loss posture explicit.
3. **Peer-handoff explicit** — distinguish verified identity from application-visible identity.
4. **Federation-aware** — keep bundle-set scope and trust-domain narrowing first-class.
5. **Debug-bundle first** — optimize for portable, redacted issue artifacts.
6. **Join, don’t replace** — import from `spiffe`, `spiffe-rustls`, `spiffe-rustls-tokio`, and SPIRE APIs instead of forking them.
7. **Diffable** — support release/config/deployment review.

# Non-goals

- Replacing SPIRE or defining a new workload-identity standard.
- Building a full mesh control plane.
- Acting as the sole certificate authority or secret manager.
- Hiding all policy under one “secure by default” score.

# Architecture & API sketch

Crates:
- `spiffe_surface_model`: shared types for source basis, trust-domain policy, peer-identity handoff, rotation state, and diffs
- `spiffe_surface_capture`: import helpers for `spiffe`, `spiffe-rustls`, `spiffe-rustls-tokio`, and config/env routes
- `spiffe_surface_check`: validation, narrowing checks, and downgrade rules
- `cargo-spiffe-surface`: CLI / cargo subcommand

Core outputs:
- `identity-source.receipt.json`
- `trust-domain-policy.receipt.json`
- `peer-identity.receipt.json`
- `rotation-state.report.json`
- `spiffe-surface-check.report.json`
- `spiffe-surface-diff.report.json`

# Minimum lovable MVP

A small library and CLI that can:

1. inspect one Rust workload-identity subject,
2. emit an identity-source receipt,
3. emit a trust-domain-policy receipt,
4. emit a peer-identity receipt,
5. emit a rotation-state report,
6. diff two captures,
7. and bundle the results into a compact archive.

# De-risk plan

1. Start with **capture + check + diff**, not with framework takeover.
2. Treat Workload API, delegated identity, and static-dev sources as different first-class modes.
3. Keep federation narrowing and peer-ID authorization separate.
4. Keep debug bundles aggressively redacted and deterministic.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 24/30**

# Milestones

## 0.1
- identity-source receipts
- trust-domain-policy receipts
- peer-identity receipts
- rotation-state reports
- diff + bundle CLI

## 0.2
- SPIRE delegated-identity capture lane
- framework adapters for `tower`, `tonic`, and `hyper`
- failure-posture and debug-bundle normalization

## 1.0
- stable bundle/report formats
- public fixture corpus
- documented compatibility and redaction policy

# Open questions

- How much source-loss/failure posture can be inferred mechanically versus declared by the maintainer?
- What is the smallest shared vocabulary for peer-identity visibility across `rustls`, `tower`, `hyper`, and `tonic`?
- How should delegated identity subjects be normalized so they stay distinct from direct workload-issued identities?

# Sources

- SPIFFE library usage page: https://spiffe.io/docs/latest/deploying/libraries/
- SPIFFE core spec: https://spiffe.io/docs/latest/spiffe-specs/spiffe/
- SPIFFE Workload API spec: https://spiffe.io/docs/latest/spiffe-specs/spiffe_workload_api/
- SPIFFE Federation spec: https://spiffe.io/docs/latest/spiffe-specs/spiffe_federation/
- `spiffe` crate docs: https://docs.rs/crate/spiffe/latest
- `spiffe-rustls` crate docs: https://docs.rs/spiffe-rustls/latest/spiffe_rustls/
- `spiffe-rustls-tokio` crate docs: https://docs.rs/spiffe-rustls-tokio/latest/spiffe_rustls_tokio/
- `spire-api` crate docs: https://docs.rs/crate/spire-api/latest
