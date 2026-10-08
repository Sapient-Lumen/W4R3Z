---
id: P-0245
title: Attestation Interop & Evidence Kit — RATS/EAT-oriented bundles + verifiable traces + policy explain
status: idea
domains: [security, interop, reliability]
last_reviewed: 2026-03-05
evidence:
  - https://datatracker.ietf.org/doc/rfc9334/
  - https://www.rfc-editor.org/rfc/rfc9711.html
  - https://crates.io/crates/tss-esapi
  - https://crates.io/crates/cose-rust
---

## What it should provide others

A **pragmatic “attestation debugging & conformance” toolbox** that turns remote-attestation flows into **portable, redactable evidence bundles** and **repeatable CI checks**.

It should help teams answer:
- “What did the attester *claim* (EAT)?”
- “What evidence supports that claim (measurements, event logs)?”
- “What policy decided the verdict—and why?”
- “Can another team reproduce the verdict on a different verifier/stack?”

## Scope and design

### 1) Attestation bundle format
Define a `*.attbundle.zip` with:
- `claims/` — normalized EAT (CBOR/JWT) and decoded claims (canonical JSON)
- `evidence/` — optional TPM event logs / measurement lists / signed digests
- `verifier/` — verifier config + trust anchors + policy snapshot
- `verdict.json` — machine-readable verdict + reasons + references
- `redaction.json` — what was removed/hashed (privacy-by-default)

### 2) Policy and explainability
- Policy adapters (OPA/Rego-like, CEL-like, or a minimal native policy DSL)
- “Explain mode” that outputs:
  - which claims were evaluated
  - which rules fired
  - where trust anchors were used
  - what failed, with minimally sufficient traces

### 3) Interop adapters (start small)
- Parse/validate EAT and common COSE envelopes.
- Optional TPM evidence ingestion via `tss-esapi` for machines that have it.
- Provide a stable IR so multiple attestation stacks can plug in.

## MVP (6–8 weeks)

1. `attbundle` schema + CLI:
   - `attkit pack` / `attkit unpack`
   - `attkit verify --policy policy.json --explain`
2. EAT + COSE decode/verify path (happy path + common failures)
3. Policy evaluation with explain output + snapshotting
4. Redaction presets (device IDs, network IDs, key material)

## Non-goals

- Being a complete verifier for every TEEs/TPMs/firmware ecosystem.
- Replacing vendor-specific attestation services.

## Why this is “missing middle”

Rust has building blocks (TPM wrappers, COSE libs), but lacks a **shared evidence artifact** + **explainable verifier surface** that makes remote attestation *operationally debuggable and portable*.
