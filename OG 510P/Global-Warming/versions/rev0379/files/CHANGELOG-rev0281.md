# CHANGELOG — rev0281

Created: 2026-05-25T08:30:00-04:00

## Theme

Household-function recovery and nonrecurrence closeout.

## Added

- `397` — functional recovery outcomes and long-tail case closure.
- `398` — household balance-sheet repair, credit, debt, forbearance, and asset-loss prevention.
- `399` — tenancy stability, renter return rights, fair housing, and anti-displacement recovery.
- `400` — wage replacement, disaster unemployment, payroll, safe work, and livelihood return.
- `401` — recovery mobility to jobs, schools, clinics, benefits, food, repair, and legal help.
- `402` — essential personal property, appliances, devices, DME, assistive technology, and contents.
- `403` — document, phone, account, MFA, and digital-identity recovery.
- `404` — recovery closeout, residual risk, nonrecurrence, and lessons applied.

## Added cube artifacts

- `cube/household-function-recovery-ledger.csv`
- `cube/digital-identity-and-document-recovery-register.csv`
- `cube/recovery-closeout-and-nonrecurrence-register.csv`
- `cube/structural-audit-rev0281.md`

## Updated

- Expanded `cube/schema.json` to 96 fields.
- Expanded `cube/index.csv` to 405 rows.
- Added household-function rows to stabilization, service-floor, interdependency, scenario, and query-view cube files.
- Added rev0281 open questions `150`–`157`.
- Updated core thesis, ranked stack, minimum sufficient solution, front-door router, critical-services packet, scoring packet, query-view packet, stabilization pathway, and benefit-sequencing packet.
- Added sources `S714`–`S725`.

## Validation target

- continuous numbered files `00`–`404`;
- source register continuous through `S725`;
- no unresolved or unused source IDs;
- all numeric routes point to existing numbered files;
- all cube CSVs parse;
- ZIP integrity passes.
