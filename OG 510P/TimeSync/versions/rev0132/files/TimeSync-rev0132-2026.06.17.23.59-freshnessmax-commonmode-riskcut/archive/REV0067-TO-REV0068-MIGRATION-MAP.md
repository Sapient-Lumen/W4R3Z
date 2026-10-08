# Migration map — rev0067 to rev0068

## Added

- `profile_assessments[*].validity_horizon`.
- `schema/validity-horizon.schema.json`.
- `validity_horizon_summary` evidence class.
- `spec/31-profile-assessment-validity-horizon.md`.
- Positive P2 validity-horizon fixture.
- Negative fixtures for outside-window actionability, policy/actionability mismatch, export-time freshness promotion, and malformed discovery-returned validity horizon.

## Profile obligation changes

- P1/P4: `validity_horizon` is requestable.
- P2/P3/P5/P6: `validity_horizon` is profile-default.
- P2/P3/P5/P6 evidence minimum summaries include `assessment.validity_horizon`.

## Digest impact

All six profile normative digests changed because obligation placement is normative.

## Compatibility

rev0067 consumers can ignore the new field when using rev0067 profiles. rev0068 satisfied assessments for P2/P3/P5/P6 require `validity_horizon` when evaluated against the rev0068 profile catalog.
