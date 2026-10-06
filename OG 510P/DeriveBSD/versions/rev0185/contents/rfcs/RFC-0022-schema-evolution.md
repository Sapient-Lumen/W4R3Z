# RFC-0022: Schema evolution (versioning rules)

Status: Draft

## Summary

Define how JSON schemas evolve without breaking automation.

See `docs/42-schema-evolution.md`.

## Goals

- Backward compatibility within major versions.
- Explicit deprecation windows.
- Stable canonicalization for digesting.

## Non-goals

- Supporting arbitrary serialization formats (JSON only).
