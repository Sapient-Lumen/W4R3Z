# Derive Spec frontends (CUE / Pkl / Nickel / Starlark) vs core IR

DeriveBSD wants a “planned-from-scratch Nix successor” *without* inheriting:
- an overpowered evaluation language
- hidden effects and ad-hoc impure hooks
- un-reviewable diffs

This implies: **spec as data**, compiled to a typed core IR, with optional *frontends*.

## Core principle
**The authoritative Spec is a schema-versioned JSON document** (canonicalized for hashing; see `docs/80-canonical-json-hashing-jcs.md`).
Everything else is a frontend that compiles to that Spec.

## Why frontends exist
Humans and LLMs both benefit from:
- stronger typing/validation
- less boilerplate
- safer abstraction than “general-purpose code”
- better diagnostics (and ideally: evaluation traces)

## Frontend candidates

### CUE
Constraint-first data language: define schema + values together, unify constraints, validate, and render JSON.

Why it’s interesting:
- unified “types + values” model makes schema/boilerplate reduction less painful than JSON Schema alone
- native workflows for “validate existing JSON/YAML, then render canonical JSON”

### Pkl
Config-as-code language with strong typing/validation and multi-format output (JSON/YAML/etc).

Why it’s interesting:
- ergonomic “modules” with explicit imports
- can be treated as a compiler that emits the Spec IR

### Nickel
A generic configuration language for generating static config (JSON/YAML/etc), often described as “JSON with functions”, with a gradual type system.

Why it’s interesting:
- type contracts + merging are first-class, which maps naturally to a module/options layer
- can target JSON cleanly while still reducing boilerplate
- has a real ecosystem experimenting with “Nickel → Nix/NixOS”, which makes it a good stress-test of the “frontend as compiler” posture

### Starlark (optional)
A deliberately restricted, deterministic dialect used for build metadata in some ecosystems. If adopted:
- no filesystem access
- no network
- deterministic evaluation
- strict standard library

### Nix-like frontend (optional, compiled)
A Nix-inspired language can be a **power authoring layer** if (and only if) it is treated as a compiler:
- runs in a sandbox (no filesystem reads, no network)
- deterministic output for identical inputs
- compiler digest is pinned and recorded
- output is **only** Spec JSON (the signed/diffed/audited IR)

This preserves “extend it hard” ergonomics while keeping Derive core evaluation code-free.

## DeriveBSD posture (v1 recommendation)

- Ship v1 with **JSON Spec + strong schema validation**.
- Treat any frontend as an *adapter lane*:
  - the compiler itself is a pinned artifact (like any other toolchain component)
  - inputs and compiler version are explicit and hashable
  - outputs are canonical JSON IR
  - a frontend can optionally emit *value-provenance traces* for `derive explain`

Provide optional frontends later:
- CUE and/or Pkl as “authoring layers” compiled to Spec JSON
- Nickel as an operator-friendly “typed templating” alternative
- a small expression layer only if absolutely necessary, and only inside constrained, well-defined “template slots”

## LLM-centric tooling
Frontends must support:
- stable formatting
- stable diagnostics
- “explain why this field has this value” traces
- minimal diffs

See RFC-0052 and ADR-0023.

## References

- CUE (data validation use case): https://cuelang.org/docs/concept/data-validation-use-case/
- Pkl docs: https://pkl-lang.org/
- Nickel manual (intro): https://nickel-lang.org/user-manual/introduction/
- Nickel repo: https://github.com/nickel-lang/nickel
- Tweag: “Nix with; with Nickel” (interop lessons): https://tweag.io/blog/2023-01-24-nix-with-with-nickel/

Last updated: 2026-02-26

## Evaluator minimalism pointer

See `docs/83-evaluator-minimalism.md` (ADR-0025) for the rule that core Derive does not execute user code during evaluation.
