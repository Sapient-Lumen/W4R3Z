# meta-0452 — Custody/reentry continuity and front-door guard note

This maintenance note records the rev0751 change set.

## What changed

- Added notes 936 and 937 for detention, corrections, health care, death-in-custody, release calculation, Medicaid reentry, ID documents, RRC/home-confinement, housing, supervision, and reentry continuity.
- Added custody/reentry continuity tests and registered them through the common test-matrix builder.
- Added source keys, source-health rows, claims, a case-packet entry, and a repaired gap-ledger entry for the custody/reentry domain.
- Refactored front-door lint so current-revision policy and applied case-packet canon roles must appear in `generated/NOTE_STATUS.json`.

## Governing rule

**No liberty by custody row.**

## Audit note

The refactor is intentionally narrow. It does not try to redesign the older hard-coded front-door map; it only prevents the highest-risk current failure mode, where a new substantive packet passes lint but lacks its routable canon role.
