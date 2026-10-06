# Derive Spec frontends (CUE / Pkl / Nickel / Starlark) vs core IR

DeriveBSD wants a “planned-from-scratch Nix successor” *without* inheriting:
- an overpowered evaluation language
- hidden effects and ad-hoc impure hooks
- un-reviewable diffs

This implies: **spec as data**, compiled to a typed core IR, with optional *frontends*.

## Core principle
**The authoritative Spec/policy object is a schema-versioned canonical JSON document** (see `docs/80-canonical-json-hashing-jcs.md`).
Everything else is an authoring frontend that compiles to that object.

The standard provenance object for that compilation step is now:

- `frontend.compile.receipt`

That receipt is evidence-only.
It records source/compiler provenance and optional traces, but it does not replace the compiled JSON object as authority.

## Why frontends exist
Humans and LLMs both benefit from:
- stronger typing/validation
- less boilerplate
- safer abstraction than “general-purpose code”
- better diagnostics (and ideally: evaluation traces)

## v0 product posture

DeriveBSD now makes one conservative hard decision:

- **blessed in-tree:** canonical JSON
- **blessed in-tree:** HuJSON/JWCC-style human JSON normalization to canonical JSON
- **adapter lanes only:** CUE, Pkl, Nickel, Starlark, Nix-like frontends, and similar rich authoring layers

This keeps the base product coherent and small while still leaving room for richer authoring ergonomics later.

## Frontend candidates

### CUE
Constraint-first data language: define schema + values together, unify constraints, validate, and render JSON.

Why it’s interesting:
- unified “types + values” model makes schema/boilerplate reduction less painful than JSON Schema alone
- native workflows for “validate existing JSON/YAML, then render canonical JSON”

### Pkl
Config-as-code language with strong typing/validation and multi-format output (JSON/YAML/etc).

Why it’s interesting:
- ergonomic modules with explicit imports
- can be treated as a compiler that emits the Spec IR

### Nickel
A generic configuration language for generating static config (JSON/YAML/etc), often described as “JSON with functions”, with a gradual type system.

Why it’s interesting:
- type contracts + merging are first-class, which maps naturally to a module/options layer
- can target JSON cleanly while still reducing boilerplate
- has a real ecosystem experimenting with “Nickel → Nix/NixOS”, which makes it a good stress-test of the “frontend as compiler” posture

### Starlark (optional)
A deliberately restricted, deterministic dialect used for build metadata in some ecosystems.
It is attractive specifically because it foregrounds deterministic, hermetic execution.

## Adapter-lane rules

Treat any rich frontend as an **adapter lane**:

- the compiler itself is a pinned artifact
- inputs and compiler posture are explicit and hashable
- outputs are canonical JSON IR
- `frontend.compile.receipt` carries source digests, compiler/tool digest, invocation profile, and output digest
- optional explain/value-provenance traces may be carried by digest, but they remain evidence rather than authority

This keeps frontend ergonomics real without letting the frontend runtime become the Derive core.

## Why the posture is conservative

Modern frontend tools are increasingly capable.
That is good for ergonomics and bad for boundaries.
Module imports, file embedding, and external readers are exactly the features that turn “nice authoring” into a second evaluator/runtime.

So the v0 default is simple:

- JSON/HuJSON are the official in-tree path
- richer frontends can exist, but they stay out of the core contract
- high-assurance shapes should default to hermetic/no-ambient-IO compiler posture

## LLM-centric tooling
Frontends must support:
- stable formatting
- stable diagnostics
- “explain why this field has this value” traces
- minimal diffs

See also:
- `docs/495-frontend-source-compile-receipt-and-canonical-ir-boundary.md`
- `docs/149-human-policy-hujson-and-canonicalization.md`
- `docs/83-evaluator-minimalism.md`
- ADR-0023

## References

- CUE (data validation use case): https://cuelang.org/docs/concept/data-validation-use-case/
- Pkl language site/docs: https://pkl-lang.org/
- Nickel manual (intro): https://nickel-lang.org/user-manual/introduction/
- Nickel repo: https://github.com/nickel-lang/nickel
- Tweag: “Nix with; with Nickel” (interop lessons): https://tweag.io/blog/2023-01-24-nix-with-with-nickel/

Last updated: 2026-03-07r224

## Evaluator minimalism pointer

See `docs/83-evaluator-minimalism.md` (ADR-0025) for the rule that core Derive does not execute user code during evaluation.
