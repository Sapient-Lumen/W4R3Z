# rev0087 to rev0088 migration map

rev0088 is additive for producers and stricter for consumers that compose multiple portability surfaces.

## Added

- `schema/scope-composition-guard.schema.json`
- `schema/scope-composition-decision-matrix.schema.json`
- `tests/mixed-layer-scope-composition.yaml`
- `examples/scope-composition-guard-rev0088.json`
- `examples/discovery-request-with-scope-composition-guard.json`
- `scope_composition_guard_summary` evidence class

## Required consumer behavior

Consumers that combine profile drift, discovery downgrade, digest binding, aggregate lifecycle, lifecycle rollup, and transparency-policy lifecycle metadata must either evaluate the rev0088 guard semantics or fail closed.

## Profile digest change

Profile normative digests changed because `scope_composition_guard_summary` is now listed as non-satisfying profile-obligation evidence.
