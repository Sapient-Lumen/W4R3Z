# meta-0454 — Special education continuity and auto-front-door refactor note

This maintenance note records the rev0753 change set.

## What changed

- Added notes 940 and 941 for special education, IEP, Section 504, early intervention, evaluation, related services, discipline, restraint/seclusion, dispute resolution, transition, and source-currentness continuity.
- Added `metadata/special_education_tests.json`, `schema/special_education_tests.schema.json`, and generated `SPECIAL_EDUCATION_TESTS.*` through the common matrix builder.
- Added source keys, source-health rows, claims, a case-packet entry, and a repaired gap-ledger entry for the special-education / disability-education domain.
- Refactored `tools/build_note_status.py` so current-revision canon roles are automatically routed into the front-door map from note metadata instead of requiring a hand-written entry every turn.
- Added a lint check that every front-door target in `generated/NOTE_STATUS.json` resolves to an existing archive or generated path.

## Governing rule

**No FAPE by IEP row.**

## Audit note

The front-door refactor is intentionally narrow. It does not rewrite the historic alias map or change stable reader keys. It only removes the high-risk current-revision chore that previously made every new substantive packet depend on remembering to edit a hard-coded front-door dictionary.
