# rev0103 to rev0104 migration map

rev0104 narrows FT-0090 by extracting local assessment temporal/actionability checks from the validator and making assessment-time ordering executable.

## What changed

| rev0103 | rev0104 |
| --- | --- |
| Policy-acceptance and validity-horizon checks lived inline in `tools/validate_archive.py`. | They are delegated to `tools/assessment_temporal.py`. |
| A policy acceptance check could predate `assessment_time` without a targeted semantic failure. | `assessment_time > policy_acceptance.checked_at` is rejected. |
| A validity-horizon evaluation could predate `assessment_time`. | `assessment_time > validity_horizon.evaluated_at` is rejected. |
| `assessment_time_binding: profile_assessment_time` did not prove the horizon covered the assessment time. | The helper rejects `assessment_time` before `not_before` or after `not_after`. |
| 297 semantic vectors. | 300 semantic vectors. |

## Compatibility

The positive fixtures remain valid. Existing consumers that already perform policy and validity checks at or after assessment time should not need to change.

Negative fixtures were added only for newly rejected stale-actionability patterns.

## Boundary preservation

The new helper does not promote policy acceptance or validity horizon metadata into TimeState provenance, freshness, transport authentication, or profile evidence. It is an ordering check for local assessment interpretation only.
