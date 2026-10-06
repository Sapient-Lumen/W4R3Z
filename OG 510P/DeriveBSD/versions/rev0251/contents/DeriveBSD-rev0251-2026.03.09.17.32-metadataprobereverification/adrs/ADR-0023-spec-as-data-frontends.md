# ADR-0023: Spec is data; frontends compile to core IR (proposed)

- Status: proposed
- Date: 2026-02-23

## Decision
DeriveBSD’s authoritative Spec is a typed, schema-versioned JSON IR.
CUE/Pkl/Starlark (if supported) are *frontends* that compile to this IR.

## Consequences
- review diffs remain stable and small
- evaluation remains deterministic and effect-free
- multiple authoring experiences are possible without fragmenting the core
