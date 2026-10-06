# Evaluator minimalism: keep “Derive” smaller than Nix

DeriveBSD’s central trap to avoid: a powerful evaluation language that becomes a second operating system.

## Baseline rule
**The Derive core does not execute user code during evaluation.**

Evaluation produces:
- Spec → Lock → Plan
as schema-validated, canonical JSON objects (see `docs/80-canonical-json-hashing-jcs.md`).

## Where computation can live (and how it stays safe)

### Frontend compilation
Turing-complete authoring is allowed **only** as an external compiler frontend that emits canonical Spec JSON. The core evaluator remains code-free.

CUE/Pkl/Starlark/Nix-like frontends may compile to Spec JSON (docs/79).
This is explicit tooling with:
- tool digest pinned
- deterministic output
- no ambient IO

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

Last updated: 2026-02-23
