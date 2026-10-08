---
id: P-0186
title: Certificate Transparency v2 Ops & Monitor Kit
status: idea
domains: [security, pki, web, tooling, observability, conformance]
last_reviewed: 2026-03-05
evidence:
  - https://www.rfc-editor.org/rfc/rfc6962.html
  - https://datatracker.ietf.org/doc/draft-ietf-trans-rfc6962-bis/
  - https://letsencrypt.org/2025/08/14/rfc-6962-logs-eol
---

# Problem

Certificate Transparency (CT) is critical infrastructure for Web PKI auditing.
But CT is still operationally painful for most Rust teams because:

- toolchains are fragmented (SCT parsing, inclusion/consistency proofs, log monitoring),
- ecosystems are shifting from RFC 6962 APIs toward CT v2 / newer log APIs,
- and “what went wrong?” evidence is hard to capture and share safely.

Rust has crypto primitives and X.509 tooling, but lacks an opinionated, ops-friendly **CT monitor + evidence bundle** crate suite.

# What it should provide

## A. A unified CT “workbench” API

- Parse/validate SCTs (embedded, TLS extension, OCSP stapling).
- Verify inclusion proofs, consistency proofs, and log signatures.
- Log list management with policy (trusted logs, disallowed logs, “read-only” logs).
- A monitoring engine that supports:
  - domain watchlists,
  - CA/operator watchlists,
  - “newly seen precert” alerts,
  - and anomaly detection (e.g., too-fast tree growth, signature irregularities).

## B. A portable `*.ctbundle.zip` incident artifact format

- `report.json` (what was checked, log identifiers, verdicts)
- `sct/` (SCTs captured, with redaction controls for leaf data)
- `proofs/` (inclusion/consistency proofs, Merkle audit paths)
- `logmeta/` (log public keys, operator metadata, API endpoints)
- `replay/` (scripts to re-verify proofs offline)

Goal: make it easy to paste a single bundle into an issue and have others reproduce the verification.

## C. Cargo UX

- `cargo ct doctor` — checks log list freshness, endpoint reachability, clock skew.
- `cargo ct verify --bundle out.ctbundle.zip <cert>` — emits a bundle and verdict.
- `cargo ct monitor --watch example.com` — runs monitors and writes bundles for alerts.

# MVP (ship in weeks)

- RFC 6962 SCT parsing + signature verification.
- Inclusion proof verification for a provided leaf + STH.
- `ctbundle.zip` schema + replay scripts (offline verify).
- Minimal monitor that polls logs for a small watchlist.

# v1 (ship in months)

- CT v2 support (draft → final), including log API discovery.
- Built-in log list sources + rotation strategy.
- “bundle minimization” to strip unnecessary data while preserving repro.
- Conformance suite against known test vectors and public logs.

# Design constraints / risks

- Standards churn: design adapters so RFC 6962 and CT v2 coexist.
- Privacy: bundles should default to minimal leaf exposure (hashes + SAN redaction).
- Operational safety: never encourage abusive scraping; rate limits and caching.
