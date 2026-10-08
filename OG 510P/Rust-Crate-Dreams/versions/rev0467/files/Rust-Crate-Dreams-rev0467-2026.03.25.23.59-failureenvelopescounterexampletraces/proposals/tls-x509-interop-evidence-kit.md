---
id: P-0283
title: TLS 1.3 + X.509 Path Validation Interop & Evidence Kit — canonical handshakes, chain verdict diffs, and redaction-safe repro bundles
status: idea
domains: [security, cryptography, networking, interoperability, testing, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://datatracker.ietf.org/doc/html/rfc8446
  - https://datatracker.ietf.org/doc/html/rfc5280
  - https://crates.io/crates/rustls
  - https://crates.io/crates/webpki
---
## What it should provide others

A **bundle-first interop lab** for TLS 1.3 handshakes and X.509 chain validation that produces:
- canonical, redactable **handshake transcripts** (events + key schedule metadata without secrets)
- **chain input snapshots** (certs/roots/intermediates/CRLs/OCSP staples) with safe redaction tooling
- **explainable verdict diffs** across stacks: “why does A accept and B reject?”

This is not “another TLS implementation”. It is the missing layer for **reproducible debugging** and **cross-implementation conformance**.

## Core crate shape (workspace)

- `tls-evidence-core` — transcript/event model, canonicalization, hashing, redaction rules
- `tls-adapters` — adapters for `rustls` and (optionally) other stacks via capture hooks / custom verifiers
- `x509-why` — explainable path building + policy evaluation report format (RFC 5280-oriented)
- `tls-lab` — scenario runner + matrix harness + bundle IO

## Bundle format: `*.tlsbundle.zip`

Minimum contents:
- `manifest.json` — bundle version, scenario id, host fingerprints (sanitized), timestamps
- `trace.jsonl` — canonical event stream: ClientHello/ServerHello, extensions, alerts, cert chain events
- `x509_inputs/` — DER certs; optional revocation artifacts; roots snapshot
- `verdicts/` — per-run verdict + structured “reasons” (policy nodes, critical extension handling, EKU, name constraints, etc.)
- `redaction.toml` — redaction policy used (so others can reproduce the same sanitization)

## MVP (4–8 weeks)

1. Implement transcript/event IR + canonicalization + `tlsbundle` IO.
2. Rustls adapter:
   - capture handshake milestones
   - plug-in verifier to emit structured path-validation explanation
3. Two “golden” suites:
   - name constraints / SAN edge cases
   - critical extension + EKU policy deltas
4. `tlsbundle diff` CLI that pinpoints first divergence.

## De-risk plan

- Start with **read-only** capture + explain output; do not attempt to “fix TLS”.
- Use a strict, versioned IR so other adapters can plug in later.
- Include redaction presets for common compliance needs (PII, internal hostnames, private PKI roots).
