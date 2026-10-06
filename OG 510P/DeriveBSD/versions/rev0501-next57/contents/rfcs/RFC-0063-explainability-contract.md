# RFC-0063: Explainability contract (evidence-backed "why")

Status: draft

## Problem

DeriveBSD’s promise (“why/what/where-from”) is easy to market and hard to keep.
Without a contract, “explain” degenerates into:

- unverifiable narratives
- ad-hoc fields that drift across versions
- accidental inclusion of large blobs (logs, SBOMs) that bloat archives and outputs

We need a minimal, stable, evidence-backed shape for explanations.

## Proposal

Define `derive explain` as producing a canonical JSON object that is:

- **digest-bound** to the identity chain (Spec/Lock/Policy/Plan/Artifact)
- optionally **proof-bound** (closure proof identity + trust policy context)
- safe-by-default when inputs are unverified

Minimum evidence bindings:

- `spec_digest`
- `lock_digest`
- `policy_decision_digest`
- `plan_digest`
- `artifact_digest`
- `closure_manifest_digest`
- `closure_proof` identity (key id + issued/expires)

Output sections:

- `artifact`, `inputs`, `policy`, `provenance`, `closure`, `why`

## Verification semantics

`derive explain` must not invent trust.

- default behavior: mark output `unverified` if signatures/attestations/closure proofs do not validate
- `--require-verified`: fail hard

## Non-goals (v1)

- embedding full SBOM/provenance payloads (only references)
- producing a universal graph format for all backends
- guaranteeing semantic equivalence between two Plans

Pointers:
- `docs/95-explainability-contract.md`
- `docs/87-structured-output-contract.md`
- `docs/92-verification-matrix.md`
