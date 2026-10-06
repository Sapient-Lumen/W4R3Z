# Reproducible generations and determinism checks

**Tier:** C (optional lane)
**Profiles:** A, B, C, D
**Pillars:** reproducibility, supply-chain, operability

DeriveBSD already pushes reproducible builds at the package/artifact level.
A greenfield OS can go further:

> Treat *the whole system generation* as reproducible, and make failures explainable.

This is less about ideology and more about:
- catching supply-chain compromise
- catching accidental non-determinism
- making “why does my fleet differ?” cheap to answer

## Problem statement

Even if individual packages are reproducible, **system assemblies** can drift:
- file ordering/timestamps in images
- initrd composition
- boot capsule construction
- host activation scripts
- embedded metadata

We want a normal workflow that can say:

- “This generation is reproducible within these tolerated impurities.”
- “This is what differed (diffoscope report).”

## Proposal: a determinism check lane (Plan → Receipt)

Add an optional pipeline lane that rebuilds a *target generation* and compares key digests.

Artifacts:

- `repro.check.plan` — how to rebuild and what to compare.
  - Schema: `spec/repro.check.plan.schema.json`
  - Example: `spec/examples/repro.check.plan.json`

- `repro.check.receipt` — what was rebuilt, what digests differed, and what evidence explains it.
  - Schema: `spec/repro.check.receipt.schema.json`
  - Example: `spec/examples/repro.check.receipt.json`

Receipts should attach **explainability evidence** on mismatch:
- a digest pointer to diffoscope output (HTML/JSON)
- build records (`.buildinfo` lessons) where applicable
- witness rebuild statements (optional)

This composes with:
- promotion gates: `docs/166-test-receipts-and-promotion-gates.md`
- cache witness quorums: `docs/190-cache-witness-quorums-trustix.md`
- drift bundles as the review funnel: `docs/395-drift-bundles-and-review-summaries.md`

## Policy hooks

- Promotion gates can require `repro.check.receipt.result == match` for selected targets.
- Policies can allow `known_impurity` results, but only with:
  - explicit impurity ids (reviewable exceptions)
  - attached diff evidence
  - manual approval (or a tightly-scoped auto-approval policy)

Make “known impurity” non-ambient:
- maintain an explicit allowlist policy: `impurity.waiver.policy`
- treat drift as a gateable review surface: `impurity.waiver.policy.diff`

See: `docs/445-impurity-waiver-policy-diff-as-review-surface.md`.

## Impurity taxonomy (keep it honest)

Not all targets will be perfectly reproducible on day 1.
Treat “known impurities” as **typed, reviewable exceptions**:

- host kernel build-id variability
- firmware blobs
- hardware-specific microcode payloads
- non-deterministic upstream build systems in the ports adapter lane

See: `docs/158-ports-impurity-taxonomy.md`, `docs/92-verification-matrix.md`.

## Tooling references

- Reproducible Builds project tooling overview: https://reproducible-builds.org/tools/
- diffoscope (deep, recursive artifact diffs): https://diffoscope.org/
- Debian’s reproducible builds efforts (practical lessons + .buildinfo culture): https://wiki.debian.org/ReproducibleBuilds

## Why this is “ecosystem” and not just “CI”

If DeriveBSD makes determinism *visible* and *receiptable*:
- third-party repos can publish reproducibility receipts
- users can choose trust policies that incorporate reproducibility
- incident response has a factual artifact for “what differed?”

This is a leverage point for a greenfield platform.

Last updated: 2026-02-28r166
