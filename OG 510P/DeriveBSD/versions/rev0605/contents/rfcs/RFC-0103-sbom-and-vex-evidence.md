# RFC-0103: SBOM + VEX as evidence objects

Status: Draft

## Summary

Standardize signed `sbom.statement` and `vex.statement` evidence objects bound to `plan_digest` and `artifact_digest`.

## Motivation

- CycloneDX is standardized as ECMA-424 and has broad tooling adoption.
- VEX semantics are increasingly expected; CISA documents minimum requirements.
- SPDX 3.0.1 includes a Security profile with explicit vulnerability modeling.

## Design

- Default SBOM predicate: CycloneDX JSON.
- Optional SBOM predicate: SPDX JSON.
- VEX predicate: CycloneDX vulnerability/VEX shapes preferred.
- Both are DSSE + in-toto Statements.
- VEX binds to:
  - vuln DB snapshot digest
  - policy decision record digest

## Non-goals

- inventing a new SBOM/VEX format
- forcing SBOM/VEX in v0 for all artifacts (policy decides)

## References

- CycloneDX standard page: https://ecma-international.org/publications-and-standards/standards/ecma-424/
- CycloneDX overview: https://cyclonedx.org/specification/overview/
- CycloneDX VEX capability: https://cyclonedx.org/capabilities/vex/
- CISA VEX minimum requirements: https://www.cisa.gov/sites/default/files/2023-04/minimum-requirements-for-vex-508c.pdf
- SPDX 3.0.1 spec: https://spdx.github.io/spdx-spec/v3.0.1/

