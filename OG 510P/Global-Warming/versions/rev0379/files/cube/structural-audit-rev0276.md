# Structural audit — rev0276

Date: 2026-05-22 16:25 America/New_York  
Archive focus: readiness scoring, owner accountability, evidence freshness, fiscal / insurance-market stress, cross-border aid, transboundary basin cooperation, and informal habitation / labour protection.

## What this pass found

rev0275 completed a major rebuild-authority pass. It made title, tenure, procurement, reimbursement, codes, worker sustainment, shared housing, and unmet-needs closure visible. The next defect was not simply missing sectors. The cube had become good at naming service floors but still weak at answering six operational questions:

1. Is the floor actually ready under a named loadcase?
2. Who owns it and who takes over when that owner fails?
3. Is the evidence current enough for the claim being made?
4. Can the public balance sheet pay before reimbursement or debt stress bites?
5. Are insurance, mortgage, property-value, and tax-base signals already showing market retreat?
6. Do borders, basins, informal settlements, camps, and migrant labour break the assumed access path?

## Changes made

- Added files `356`–`363`.
- Added readiness, owner, evidence, fiscal-market, cross-border, basin, and informal-labour fields to `cube/schema.json` and `cube/index.csv`.
- Added five operational CSVs:
  - `readiness-scoring-model.csv`
  - `owner-accountability-matrix.csv`
  - `evidence-freshness-dashboard.csv`
  - `market-fiscal-risk-register.csv`
  - `cross-border-and-basin-dependency-register.csv`
- Extended service-floor, interdependency, scarcity, and scenario CSVs.
- Added sources `S637`–`S652`.
- Added open questions `109`–`116`.

## Structural rule added

No future service-floor packet should be admitted as operationally mature unless it has:

1. a readiness grade tied to a named loadcase;
2. an owner-of-record and backup owner;
3. a freshness class and review date for implementation-sensitive claims;
4. a financing / liquidity path where the floor requires public or household cash;
5. a market-exit signal check where insurance, credit, housing, or tax base are affected;
6. cross-border or basin cooperation checks where the hazard, supply, water, people, or assistance crosses boundaries;
7. an excluded-user journey that includes informal, undocumented, unbanked, disabled, remote, or employer-controlled users where relevant.

## Next likely gaps

The cube is now ready for a more automated phase: duplicate-source collapse, machine-generated `used_by` indexes, stale-source timers, route-query examples, and scored sample jurisdictions. Future content gaps remain, but rev0277 should probably add **query views and dashboards** before admitting many more canon notes.

---
Citations point to `sources/register.md`.
