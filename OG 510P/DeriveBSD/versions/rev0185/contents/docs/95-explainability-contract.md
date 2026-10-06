# Explainability contract (why/what/where-from)

DeriveBSD’s headline promise is that every deployed bit is **explainable**:

- **what** is running (exact bytes)
- **where it came from** (inputs + toolchain pins)
- **why it was allowed** (policy decision)
- **why it depends on X** (closure graph)

The crucial rule: **explanations must be evidence-backed**.
`derive explain` is not a best-effort narrative; it is a structured report whose fields are derived from verified objects.

## Evidence chain (minimum)

For a host generation or microVM bundle, an explanation MUST bind to these digests:

1) **Spec digest**
2) **Lock digest**
3) **Policy decision digest** (`docs/93-policy-decision-records.md`)
4) **Plan digest**
5) **Artifact digest**
6) **Closure manifest digest** + **closure proof** (`docs/90-closure-proof.md`)

Optional (when applicable):
- **Deployment digest** (host BE / workload revision as a signed unit; `docs/100`)
- **Compat mapping record digest** (foreign binaries; `docs/105`)
- **Approval bundle digests** (two-person integrity; `docs/107`)

All “explain” output is reducible to those objects.

## Surfaces

`derive explain` produces a canonical JSON object (see `docs/87-structured-output-contract.md`) with these top-level sections:

- `artifact`: digests, target kind, store roots
- `inputs`: source identities (commit/digest) + lock pins
- `policy`: policy decision record digest + optional signature identity
- `provenance`: provenance/attestation references if present
- `closure`: closure manifest digest + closure proof identity + closure members
- `why`: dependency trace(s) explaining a selected path (see `derive why-depends`)

When applicable, `derive explain` also includes:
- `deployment`: deployment ref + signatures
- `compat`: compat mapping evidence
- `blast_radius`: a pointer to the last computed blast-radius diff for the deployment (if recorded)
- `authority`: a pointer to the generation-scoped authority graph snapshot (if recorded)

The output may contain **pointers** to other objects (store paths, bundle paths), but it must not embed large bodies of data.

## Verification gate

If verification fails, `derive explain` MUST degrade safely:

- by default: emit `status: "unverified"` and include only *local* digests (no trust claims)
- under `--require-verified`: fail hard

This prevents “explain” from laundering untrusted artifacts into authoritative-looking reports.

## Relationship to trust policy

The trust policy (keys, namespaces, required attestations) determines what `derive verify` considers sufficient evidence.
See: `docs/57-namespaces-channels-trust.md` and `spec/trust.policy.schema.json`.

## Why this matters

Explainability is how DeriveBSD minimizes blast radius *after* incidents:

- identify affected closures quickly
- prove which policy environment permitted the artifact
- rollback to a known-good generation (host) or bundle digest (microVM)

Pointers:
- identity chain: `docs/02-derive-core.md`
- verification checklist: `docs/92-verification-matrix.md`

Last updated: 2026-02-23
