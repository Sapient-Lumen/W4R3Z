# Changelog rev0310

Created: 2026-06-04T05:40:00-04:00  
Base revision: rev0309

## Added

- `517-nuclear-emergency-preparedness-evidence-ingest-blocker-burndown-and-public-claim-gating-compact-canon.md`
- Synthetic closure sprint plan, evidence packets, retest records, postclosure local evidence, postclosure scorecard, readiness deltas, blocker ledger, no-average-away safeguard, public claim gate, ingest contract, normalization table, redaction rules and traceability audits.
- Scoped `cube/datacube-rev0310-emergency.sqlite` with postclosure emergency-readiness tables and views.

## High-risk correction

- Closed 323 selected synthetic local-evidence rows. Open synthetic P0 rows fall from 580 to 282; open synthetic P1 rows fall from 233 to 214.
- Added a no-average-away rule so blocker rows cap maturity even when the average readiness score looks high.

## Not changed

- Legacy universal nuclear crossproduct tables remain for compatibility and are not canonical emergency-readiness evidence.
- Rev0310 closure data are synthetic fixture data, not real plant or jurisdiction evidence.
