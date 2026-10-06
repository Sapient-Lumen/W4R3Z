# RFC-0021: bhyve configuration mapping (Plan → bhyve)

Status: Draft

## Summary

Define how a DeriveBSD runtime manifest maps to a bhyve configuration in a deterministic, reviewable way.

See `docs/40-bhyve-config-mapping.md`.

## Goals

- Deterministic mapping: same runtime manifest → same bhyve config output.
- Mapped config is included in the artifact closure and is explainable.
- Mapping output is structured and hashable (canonical JSON).

## Non-goals

- Supporting every bhyve feature in v1.
