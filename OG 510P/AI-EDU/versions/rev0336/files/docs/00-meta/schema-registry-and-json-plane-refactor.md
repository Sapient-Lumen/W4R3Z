# Schema registry and JSON-plane refactor

Rev0227 adds `CUBE_SCHEMA_REGISTRY.json` as the machine-readable map for structured cube artifacts; rev0229 makes that map executable by validating every registered instance against its declared schema. Rev0230 keeps that gate intact while redirecting substantive work toward the first real `FT-0181` packet rather than more schema bureaucracy.
The archive already had many schemas, validators, and example records, but the relationship between
those pieces was distributed across filenames and maintainer memory.

## Problem found in the audit

The lint/toolchain plane became explicit in rev0226, but the JSON/schema plane remained implicit.
That created four drift risks:

1. a new `schemas/*.schema.json` file could be added without a validator path;
2. a new `examples/**/*.json` fixture could sit outside schema coverage;
3. a root control file could look canonical without a registered shape contract;
4. a validator could exist, but the prose surface explaining its artifact family could be hard to
   find;
5. a fixture could be registered to a schema but still violate that schema because only coverage, not conformance, was checked.

Those are integrity risks, not evidence risks. They do not close `FT-0181`, but they affect whether a
future real pilot import can be traced cleanly through source data, schema shape, validator, prose
surface, and release claim boundary.

## New registry surfaces

| Surface | Role |
|---|---|
| `CUBE_SCHEMA_REGISTRY.json` | Maps schemas to instance globs, validators, prose surfaces, status, and closure boundaries. |
| `schemas/schema-registry.schema.json` | Shape contract for the registry itself. |
| `tools/check_schema_registry.py` | Fails if schemas, examples, root structured controls, validators, or prose surfaces drift out of coverage, and fails if matched instances violate their declared schemas. |
| `docs/00-meta/cube-refactor-audit-rev0227.md` | Audit note explaining the JSON-plane refactor and the toolchain-checker bug fixed during the pass. |

## Refactor rule

When adding a structured artifact family:

- add or reuse a schema under `schemas/`;
- add the instance path or glob to `CUBE_SCHEMA_REGISTRY.json`;
- wire the validator into `CUBE_TOOLCHAIN_REGISTRY.json`;
- point the registry row to a human-readable doc surface;
- state the closure boundary, especially when an example can be mistaken for evidence;
- update source-status declarations if the artifact is an example or fixture.

When adding a JSON example, do not rely on directory naming alone. The example must be covered by
exactly one schema registry row, validate against that row's schema, and pass the relevant validator.

## What this does not prove

Schema coverage proves structured-artifact governance. It does not prove service quality, learning
outcomes, fairness, access, safety, compliance, workload reduction, or real pilot import completion.
It does not upgrade `realistic_example` records into source evidence and does not close `FT-0181`.
