---
status: active
revision_current: rev0355
base_revision: rev0323
route_role: unrouted
route_refs: [unrouted]
---

# rev0324 deep audit: semantic currentness invariants and cloudtainer waste map

Generated: `2026-06-12T21:25:25Z`  
Codename: `semantic-currentness-invariants-and-cloudtainer-waste-map`

## Bottom line

rev0323 was directionally right: it recognized that wealth-datacube claims around current law, dynastic vehicles, beneficial ownership, and charitable subsidies age faster than ordinary framework notes. The severe failure is that the archive could pass its validator while contradicting that doctrine in its own metadata and currentness ledger.

The failure mode is not mainly bad facts. It is a governance failure: release surfaces, source ledgers, duplicate audits, and case/source recertification can drift independently while the validation report stays green.

## What went severely wrong

1. `docs/00-meta/currentness-ledger.json` used `statistical_or_vehicle_reporting_release` in case rows but did not declare that class in `currentness_classes`.
2. `SOURCES.json` had `source_count: 440` but stale release metadata: `source_range: S01-S426` and `current_revision: rev0322`.
3. `beneficial-ownership-trust-entity-visibility-rollback-rev0323-scoreboard.json` had `source_refresh_due: 2026-12-31` even though controlling BOI sources S432/S433 refresh on `2026-09-30`.
4. `docs/00-meta/source-duplicate-audit.json` was still labeled `rev0321` and reported 12 duplicate URL groups / 11 duplicate title groups, while the current source ledger contains 19 duplicate URL groups / 16 duplicate title groups.
5. Historical validation reports exist only through rev0320; this overlay adds the current report but leaves a documented backlog for rev0321-rev0323 and rev0304.
6. Eleven source rows had access-date strings in the publication `date` field. This overlay normalizes them to `date: undated` and preserves the original access marker in `date_notes`.

## What was missing

### Source-level currentness rows

rev0323 said every volatile case and source needed snapshot, refresh, and recertification triggers. Only case rows existed. This revision adds `source_rows` for all 440 sources so the validator can compare case refreshes against the minimum refresh due date of cited sources.

### Semantic validator checks

The old validator confirmed that keys existed. It did not ask whether a currentness class was declared, whether source-level rows existed, whether `source_range` matched the actual source ID span, whether duplicate audits were stale, or whether a case-level refresh date was later than one of its controlling cited sources. Those checks are now present.

### Retirement and consolidation pressure

The archive has no byte-identical duplicate files, but it has highly compressible generated ledgers. `cases/EVIDENCE_LEDGER.json` is the largest file and compresses to a tiny fraction of its raw size. That is a sign of repeated edge structure, not necessarily a storage crisis. The real cost is cognitive: reviewers must wade through repeated derived artifacts that can be regenerated.

### Certification tiers

The portfolio count says 95 cases, but not every case has equal evidentiary depth. Some case memos are short seed/stress memos. The release should distinguish `certified`, `working`, `seed`, and `quarantined` cases in a portfolio-level table so counts do not overstate mature coverage.

## What should change next

1. Treat release metadata as a hard invariant: `VERSION`, `REVISION-RECEIPT`, `ARCHIVE_INDEX`, `SOURCES`, field ledgers, route ledgers, source-use register, duplicate audit, and currentness ledger must all agree on the current revision.
2. Make stale generated audits fail validation. If an audit file reports counts, the validator should recompute those counts from canonical ledgers.
3. Promote `source_rows` from optional audit material to canonical release machinery.
4. Add a case-certification ledger with explicit tiers and retirement triggers.
5. Move very large generated ledgers to a reproducible build path or store compact canonical edges plus build scripts; keep full derived ledgers only when they are being reviewed.
6. Add a `known_backlog` section to every validation report: missing historical reports, stale duplicate groups, shallow memos, and sources requiring external recertification.

## Speculative diagnosis

This cloudtainer appears to have crossed the line from “knowledge cube” into “append-only governance theater.” Each revision adds more routing, fields, and ledgers, but some ledgers are generated from older states and not made accountable to canonical data. Over time, the cube will become harder to trust unless each new doctrine creates a validator check or a retirement rule. The best corrective path is not more cases. It is fewer release claims, stronger invariants, and explicit demotion of weak surfaces.

## Patches applied in this overlay

- Corrected `SOURCES.json` release metadata.
- Added the missing currentness class.
- Added source-level currentness rows for every source.
- Shortened the BOI rollback case refresh date to match cited source volatility.
- Refreshed duplicate-source counts.
- Hardened the validator against the specific semantic drift that rev0323 missed.
- Added this audit report and `reports/cloudtainer-waste-report-rev0324.json`.

## Remaining backlog

- Build a historical validation report backfill for rev0304 and rev0321-rev0323.
- Resolve or alias duplicate URL groups instead of merely listing them.
- Review the four apparently unused source rows in `cloudtainer-waste-report-rev0324.json`.
- Add a certification-tier ledger to distinguish mature cases from seed/stress cases.
- Decide whether non-day publication dates such as `YYYY-MM` and ranges such as `2024-2025` should remain accepted or be split into `date`, `date_precision`, and `coverage_period`.
