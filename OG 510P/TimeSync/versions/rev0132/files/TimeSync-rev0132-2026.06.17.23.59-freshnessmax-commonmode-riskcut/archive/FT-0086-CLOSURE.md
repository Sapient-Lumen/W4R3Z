# FT-0086 closure — compatibility drift, downgrade proofs, and portability threat tests

rev0087 closes FT-0086.

## Closed question

Should TimeSync add an executable compatibility-drift matrix for profile references, aggregate lifecycle portability, and discovery-negotiated downgrade paths so cross-operator reuse can fail closed when a newer or weaker profile surface is encountered?

## Answer

Yes. rev0087 adds a matrix and validator checks that separate equivalent, stricter-or-equal, weaker, unknown, incomparable, digest-rollover-compatible, and digest-rollover-without-equivalence cases.

## Changes

- Added `schema/profile-compatibility-drift-matrix.schema.json`.
- Added `schema/profile-compatibility-drift-decision.schema.json`.
- Added `tests/profile-compatibility-drift-matrix.yaml`.
- Added `compatibility_drift` to profile compatibility statements.
- Added downgrade-proof metadata to discovery result `version_negotiation`.
- Added downgrade-proof policy to `semantic-version-negotiation`.
- Added negative fixtures for weaker/unknown drift, unproven digest rollover, missing drift for named portability workflows, missing downgrade proof, and weaker downgrade semantics.

## Boundary preserved

Drift and downgrade decisions update only compatibility or discovery interpretation. They do not update TimeState, profile conformance, profile evidence, current actionability, replay visibility, or TimeSync provenance.
