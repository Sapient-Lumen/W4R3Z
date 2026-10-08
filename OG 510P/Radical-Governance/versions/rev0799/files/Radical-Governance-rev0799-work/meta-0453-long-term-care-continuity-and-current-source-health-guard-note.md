# meta-0453 — Long-term care continuity and current-source-health guard note

This maintenance note records the rev0752 change set.

## What changed

- Added notes 938 and 939 for long-term services and supports, nursing homes, HCBS, adult protective services, ombudsman routes, guardianship/fiduciary control, transfer/discharge, staffing, emergency relocation, and care continuity.
- Added `metadata/long_term_care_tests.json`, `schema/long_term_care_tests.schema.json`, and generated `LONG_TERM_CARE_TESTS.*` through the common matrix builder.
- Added source keys, source-health rows, claims, a case-packet entry, and a repaired gap-ledger entry for the LTSS / long-term care domain.
- Added a lint guard requiring every source key used by current-revision notes to have a manual source-health entry.

## Governing rule

**No care by facility row.**

## Audit note

The source-health guard is intentionally narrow. It does not demand that every historical source be manually classified, because that would turn the session into registry archaeology. It only prevents the highest-risk future failure: adding a new substantive packet with fresh source keys but no currentness, volatility, or source-boundary posture.
