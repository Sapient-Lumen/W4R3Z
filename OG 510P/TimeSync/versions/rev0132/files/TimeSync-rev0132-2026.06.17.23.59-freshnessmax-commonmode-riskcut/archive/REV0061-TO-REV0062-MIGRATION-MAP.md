# Migration map — rev0061 to rev0062

## What stayed stable

- The six-field TimeState remains the invariant core.
- Wire claims remain thinner than local assessed state.
- `profile_conformance` remains scoped by `assessed_profile`.
- Fallback still requires an explicit non-stronger applicability boundary.
- Historical assessment validity remains separate from current-policy acceptance.

## What became more concrete

| rev0061 area | rev0062 addition |
|---|---|
| profile applicability was described abstractly | `profiles/profile-catalog.json` and per-profile applicability maps |
| fallback was a semantic rule | fallback mappings are executable profile-local objects |
| schemas were shape checks | semantic validator checks interval order, profile labels, fallback target validity, required/default item presence, and manifest hashes |
| examples covered a few cases | fixtures now cover P1-P6, multiple assessments, policy rejection, and negative cases |
| FT-0061 was open | FT-0061 is closed; FT-0062 opens transport/adapter binding |

## Migration guidance

Existing rev0061 local assessed state examples remain valid if their `applicability` label appears in the relevant rev0062 profile map. Implementations that previously used local strings should either:

1. add those strings to the relevant profile-local map, or
2. map them to an existing profile-local label before export.

Do not move local labels into a global registry merely to make migration convenient.
