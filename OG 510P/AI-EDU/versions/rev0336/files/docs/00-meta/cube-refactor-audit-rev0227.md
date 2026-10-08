# Cube refactor audit rev0227

## Audit target

Rev0227 audits the JSON/schema plane. Rev0226 made the lint runner registry-backed, but schemas and
JSON examples still depended on scattered conventions: schema filenames, validator names, example
directories, and prose docs had to be mentally reassembled by the maintainer.

## Findings

| Finding | Risk | Treatment |
|---|---|---|
| Schemas existed without one registry that named their governed instances, validators, and prose surfaces. | A future schema or example could be added but not become part of the release-control plane. | Added `CUBE_SCHEMA_REGISTRY.json`, `schemas/schema-registry.schema.json`, and `tools/check_schema_registry.py`. |
| Root structured controls were not distinguished from ordinary example JSON by a schema registry. | Canonical maps such as branch family, toolchain, or schema registry could drift without a shared coverage rule. | Registered root controls explicitly and required root structured controls to have schema coverage. |
| JSON examples were covered by directory-specific validators, but no global rule said every `examples/**/*.json` must be covered exactly once. | A fixture could become invisible or be accidentally governed by two artifact families. | Added global example coverage and duplicate-coverage checks. |
| `tools/check_toolchain_registry.py` reused the global error list when deciding whether to skip individual rows. | An early revision mismatch could hide useful row-level coverage diagnostics. | Refactored row validation to use local `row_errors` flags. |

## Decision

The cube should treat schemas as first-class control-plane artifacts. A schema is not complete until
its instances, validator, human doc surface, and claim boundary are registered together.

## Non-changes

No service record was promoted. No real pilot data was imported. No synthetic example was upgraded.
No `FT-0181` closure state changed. No historical branch file was moved.

## Next maintenance posture

Future audit/refactor passes should prefer consolidation and drift prevention over new gates. A new
schema, validator, or JSON fixture should fail lint unless it is registered through both the schema
registry and the toolchain registry.
