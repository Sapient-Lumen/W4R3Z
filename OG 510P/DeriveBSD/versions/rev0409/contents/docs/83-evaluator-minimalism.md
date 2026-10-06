# Evaluator minimalism: keep “Derive” smaller than Nix

DeriveBSD’s central trap to avoid: a powerful evaluation language that becomes a second operating system.

## Baseline rule
**The Derive core does not execute user code during evaluation.**

Evaluation produces:
- Spec → Lock → Plan
as schema-validated, canonical JSON objects (see `docs/80-canonical-json-hashing-jcs.md`).

## Where computation can live (and how it stays safe)

### Frontend compilation
Turing-complete or richly expressive authoring is allowed **only** as an external compiler frontend that emits canonical Spec JSON. The core evaluator remains code-free.

The authoritative object remains canonical Spec JSON.
`frontend.compile.receipt` is the optional evidence object that records source/compiler provenance and traces.

v0 keeps the blessed in-tree path intentionally small:
- JSON
- HuJSON/JWCC normalization to canonical JSON

CUE/Pkl/Starlark/Nix-like frontends may still compile to canonical Spec JSON (see `docs/79-derive-spec-frontends.md` and `docs/495-frontend-source-compile-receipt-and-canonical-ir-boundary.md`), but they remain adapter lanes rather than part of the core evaluator.

This is explicit tooling with:
- tool digest pinned
- deterministic output
- no ambient IO by default
- compiler/source provenance preserved via `frontend.compile.receipt` when needed

### Resolvers (Lock phase)
Source resolution may require network (e.g. “latest tag”), but:
- happens only in `lock` phase
- uses strict allowlists, CA provenance, and logging
- result is a sealed, reviewable Lock file

### Builders (Artifact phase)
Builds happen in jails; deny network; treat builders hostile.

## Allowed abstractions (v1)
If we need templating:
- bounded, data-only templates (no loops beyond fixed schema expansions)
- deterministic interpolation only
- every expansion recorded in Plan “explain” output

## Why this matters
- Review diffs stay small
- LLMs can reason over schemas reliably
- evaluation stays auditable and reproducible

See ADR-0025.

Last updated: 2026-03-07r224
