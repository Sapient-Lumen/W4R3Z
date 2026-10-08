# CHANGELOG rev0369

## Added

- New front-door canon `576-nuclear-emergency-preparedness-requesttemplates-deadlineclock-hotpathbuilder-refactor-compact-canon.md`.
- Absolute deadline clock for public meeting capture, same-day intake, records request dispatch, 90-day FEMA-to-NRC evaluation watch, 120-day final report watch, EOF LER/no-LER lookback, ANS transition, AFN/transport, and CAP/retest watches.
- Sendable records-request templates for FEMA, PEMA/Pennsylvania channels, Beaver County, Columbiana/Ohio channels, NRC, Vistra/regulatory path, and public-meeting questions.
- Gap-to-request map tying every rev0368 closure blocker to request templates and proofcut classes.
- EOF corrective-action proof chain and alerting proof chain.
- Source review map update that formalizes rev0368 external IDs and adds records-routing sources without treating them as BVPS performance evidence.
- Reproducible hotpath builder for SQLite and capsule artifacts.

## Changed

- Active hotpath handling now starts from `cube/bvps-hotpath-source-list-rev0369.csv` rather than manually curated capsule contents.
- README, manifest, validation rules, index/file/file-core rows, table-column catalog, source maps, validation report, and structural audit updated to rev0369.

## Not changed

- No real or lawfully anonymized Beaver Valley evidence packet has been imported.
- No readiness, unreadiness, ANS success, EOF recovery, or siren-transition closure claim is made.
