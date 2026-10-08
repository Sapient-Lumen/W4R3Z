# rev0115 to rev0116 migration map

rev0116 is a validation and semantic-tightening revision. The TimeState core, profile catalog, transport catalog, evidence-class catalog, and public schema names remain stable.

## Stable surfaces

- No change to the six-field TimeState core.
- No change to profile identifiers or transport adapter identifiers.
- No new registry, authority repository, credential protocol, transparency-log client, or time-transfer protocol.
- Existing positive fixtures remain valid.

## New executable checks

- `tools/mutation_survivor_audit.py` runs focused wrong-bind probes from passing fixtures.
- Current discovery result wrapper digests must bind the expected artifact class for known result items.
- Discovery-returned `profile_compatibility_drift_decision` values are schema- and semantic-checked as nested artifacts.
- Policy lifecycle-equivalence revocation digests must bind revocation status.
- Lifecycle-authority renewal hint digests must bind lifecycle status.
- Aggregate lifecycle rollups must include an `aggregate_correction_authority_lifecycle_summary` digest binding.
- Scope-composition decision-matrix temporal observations must match `matrix_digest`.

## New negative coverage

- Fixture derivations `DF-0116-001` through `DF-0116-006`.
- Semantic vectors `TV-N318` through `TV-N323`.

Consumers that validate only the public JSON Schemas will see no incompatible schema-name change. Consumers that run the TimeSync semantic validator will now reject the newly covered wrong-bind survivors.
