---
id: P-0189
title: Certificate Transparency Ops & Migration Kit — monitor, verify, and transition CT ecosystems with evidence bundles
status: idea
domains: [security, tls, transparency, operations, supply-chain]
last_reviewed: 2026-03-05
evidence:
  - https://www.rfc-editor.org/rfc/rfc6962.html
  - https://datatracker.ietf.org/doc/draft-ietf-trans-rfc6962-bis/42/
  - https://letsencrypt.org/2025/08/14/rfc-6962-logs-eol
  - https://github.com/rustls/ct-logs
  - https://crates.io/crates/sigsum
---

# Problem

Certificate Transparency is operationally critical, but in practice teams struggle with:

- **Log ecosystem churn** (APIs, log lists, operator policies, deprecations).
- Building **reproducible incident artifacts** when SCTs, log proofs, or inclusion checks fail.
- Integrating CT verification and monitoring into Rust services and CI in a way that is both secure and debuggable.

Recent ecosystem moves (e.g., planned shutdown timelines for RFC 6962-style logs) raise the importance of migration planning and robust tooling.

# What it provides

A “CT ops toolbox” that is intentionally artifact-first.

Deliverables:

- `ctops` library: verify SCTs, fetch inclusion proofs, validate STH consistency, and normalize errors.
- `cargo ct` subcommands:
  - `cargo ct verify <certchain>` (local verification and explanations),
  - `cargo ct fetch <log>` (diagnostics + caching),
  - `cargo ct monitor` (watch domains/issuers for unexpected certs).
- Standard artifact bundle: `*.ctbundle.zip` containing:
  - cert chain, SCTs, log list snapshot, fetch transcripts,
  - STHs, inclusion proofs, consistency proofs,
  - `report.json` (stable, diffable summary + failure classification).
- A log-list strategy that can ingest multiple sources and explain provenance (and cope with paused/archived efforts).

Optional (but powerful):

- **Transparency-agnostic adapter** layer so CT can be paired with “general transparency logs” (e.g., Sigsum) for adjacent ecosystems (keys, binaries, configs).

# Users & user stories

- **Service operator**: “My TLS endpoint is failing browser CT expectations; I need a reproducible bundle to debug quickly.”
- **CA / PKI engineer**: “I want to monitor for misissuance and produce audit-ready evidence.”
- **Rust TLS library maintainer**: “I need stable tests and fixtures for CT verification logic.”

# Prior art (and why it’s insufficient)

- CT is standardized and widely implemented, but Rust ecosystem pieces are fragmented and some efforts have paused (e.g., archived log-list crates), leaving gaps in ops-grade workflows.

# Design goals

- Make every failure **explainable** and **shareable**.
- Separate “policy decisions” from “mechanics” (verification and proof fetching).
- Provide **deterministic** fixtures and replay harnesses for CI.

# Non-goals

- Replacing browser CT policy engines.
- Becoming a CA log operator.

# Architecture & API sketch

- Core:
  - `LogListSource` (versioned snapshots, provenance)
  - `Verifier` (SCT validation, timestamp rules)
  - `ProofClient` (inclusion/consistency)
  - `BundleWriter/Reader`
- Conformance:
  - fixture packs keyed by RFC requirements + common operational failure modes.

# Security / safety model

- Strong input validation and size limits (logs can be adversarial).
- Redaction modes for incident bundles (strip private keys, internal hostnames where needed).

# Maintenance & governance plan

- Explicit compatibility guarantees for bundle schema and verifier API.
- Log-list updates and provenance tracked in the repo (audit-friendly).

# Milestones

1. MVP: SCT verify + inclusion proof fetch + `ctbundle.zip` format.
2. v0.5: monitoring tool + alert rules + replayable fixture packs.
3. v1.0: conformance suite + policy hooks + optional transparency-log adapter.

# Open questions

- Best default log list sources and update cadence for Rust projects?
- How to encode migration timelines and deprecation signals into tooling UX?

# Sources

- https://www.rfc-editor.org/rfc/rfc6962.html
- https://datatracker.ietf.org/doc/draft-ietf-trans-rfc6962-bis/42/
- https://letsencrypt.org/2025/08/14/rfc-6962-logs-eol
- https://github.com/rustls/ct-logs
- https://crates.io/crates/sigsum
