---
revision_current: rev0355
status: active_document
claim_kind: audit_report
---

# rev0338 evidence-debt source-anchor and measurement-fit refactor

## Priority finding

After rev0337 closed seed and seed-calibration status drift, the next hidden failure mode was active scoreboards that still carried unsourced evidence-debt rows. A scan found 10 rows without source anchors across five active scoreboards: Canada, India, United Kingdom, Vienna social housing, and the Federal Reserve quasi-fiscal case.

## What changed

This revision does not add cases or fields. It converts those 10 unsourced proof-debt rows into sourced proof obligations and refreshes the surrounding scorecard fields, certification gates, and gate-inventory rows where the evidence debt affects the verdict.

Targets hardened:

- `canada-rev0305`
- `india-rev0305`
- `united-kingdom-rev0305`
- `vienna-social-housing-rev0305`
- `federal-reserve-balance-sheet-quasi-fiscal-rev0318`

## Substantive changes

Canada now attaches parent-backed housing-entry evidence to the inter vivos transfer / parental guarantee row rather than leaving the issue as a bare reminder. India now attaches official AIDIS/SAS currentness and climate-debt evidence to the informal-debt washout row. The United Kingdom now ties top-tail and beneficial-owner measurement debt to ONS quality limitations, HMRC identified-wealth coverage, and distributional-accounting methodology. Vienna now ties rent-discount conversion debt to housing-cost/burden evidence rather than program-design evidence alone. The Fed case now attaches current balance-sheet, IORB, and H.4.1 reporting sources and shortens source refresh to 2026-09-30.

## Audit/refactor

Source-fit corrections:

- `S87`: ONS WAS total wealth source relabeled as quality-limited official statistics / direct-with-caveat.
- `S90`: Canada PBO top-tail source relabeled as official parliamentary report / direct.
- `S95`: City of Vienna housing source relabeled as official municipal policy / direct.
- `S96`: Climate and Community Institute Vienna source relabeled as nonprofit research / context.

Validator refactor:

- Added a rev0338 invariant: every `evidence_debt_register` row in every active scoreboard must have nonempty `source_ids`.
- Added source-fit locks for S87, S90, S95, and S96.
- Added target-source locks for the five hardened cases.
- Added a direct Fed refresh lock at `2026-09-30`.

## Counts

- New sources: 11 (`S476`-`S486`)
- New cases: 0
- New schema fields: 0
- Evidence-debt rows corrected: 10
- Remaining unsourced evidence-debt rows: 0
