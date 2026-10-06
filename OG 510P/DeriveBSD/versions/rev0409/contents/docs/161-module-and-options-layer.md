# Module + options layer: NixOS-style composition without a Turing-complete core

Nix pros expect two things:
1) configuration that composes (many files, merged predictably)
2) discoverable **options** ("what can I set?", "where is it set?", "what wins?")

DeriveBSD should provide an equivalent **module + options layer** that compiles down to canonical Spec JSON.

## Model

- **Modules** are data fragments that contribute to a target Spec (host, microVM, devshell, user env).
- Modules merge via **stable, documented merge semantics** (no hidden code).
- The merge result is rendered as canonical JSON and becomes the authoritative Spec input.

## Options registry

An option is a schema-defined setting with:
- type and constraints
- documentation string
- default
- “merge strategy” (replace/append/union)
- provenance reporting (which module set it)

DeriveBSD should generate an **options registry** for each schema version.

## CLI expectations (v0)

- `derive options <target> --json` — emit options (docs + types + defaults)
- `derive config show <target> --json` — show the merged result
- `derive config trace <path> --json` — explain where a value came from (module path + overlay id)

These are core to explainability and LLM-assisted maintenance.

## Merge semantics (v0 recommendation)

Keep it small and explicit:
- scalars: last-wins
- maps: deep-merge, with explicit conflict reporting where unsafe
- lists: default replace, with explicit `append` form available

Every merge should produce a deterministic **trace** artifact (inputs → output).

## Relationship to frontends

Frontends (Pkl/CUE/Starlark/Nix-like) may exist as authoring layers, but the **module layer output** must be:
- schema-valid
- canonical JSON
- explainable via traces

## Non-goals (v0)

- arbitrary evaluation-time metaprogramming inside Derive core
- implicit IO (reading the filesystem during merge/eval)

Last updated: 2026-02-23
