# rev0091 audit — format assertion and temporal-window hardening

## Deep-read result

rev0090 was internally consistent: the validator passed, revision-reference lint passed, and fixture coverage was complete. The deeper issue was that several guarantees were implicit rather than executable.

## What was missing

1. JSON Schema `format: date-time` was present throughout the schema layer, but the validator did not pass a `FormatChecker`. In Python `jsonschema`, `format` is not asserted unless a checker is supplied. A malformed timestamp could therefore survive schema validation unless a later semantic check happened to parse that exact field.
2. `tests/semantic-test-vectors.yaml` had duplicate IDs (`TV-111` and `TV-112`). The old validator did not notice because it validated fixture paths and expectations, not vector identity.
3. `temporal_coherence` checked that observations were inside the declared evaluation window, but did not prove the observations happened no later than `guard.evaluated_at`.
4. `temporal_coherence` accepted declared `max_age_seconds` fields without enforcing them against `guard.evaluated_at`.

## What changed

- `tools/validate_archive.py` now validates schemas with `jsonschema.FormatChecker()`.
- `tools/validate_archive.py` now rejects duplicate semantic vector IDs.
- `tools/temporal_coherence.py` now rejects current-use input observations after guard evaluation.
- `tools/temporal_coherence.py` now rejects current-use input observations older than their declared `max_age_seconds`.
- Added negative fixtures for all three executable holes.

## What should change next

The next high-value work is still FT-0090: replace or formally constrain the Python digest canonicalization helper, reuse temporal-coherence helpers outside scope-composition guards, and split the large validator by concern. Fixture size should also be addressed by generating negative fixtures from base objects plus patches, because many large files differ by one semantic mutation.

## Boundary

rev0091 does not change TimeState, profiles, transport adapters, evidence classes, or the scope-composition guard schema version. It is a validation-hardening revision.
