# Structural audit — rev0282

Created: 2026-05-25T10:15:00-04:00

## Theme

Risk-reduction pipeline and no-new-risk governance after household-function recovery.

## What changed

- Added numbered canon files `405`–`412`.
- Added cube artifacts for risk-reduction pipelines, no-new-risk / future-condition gates, and mitigation performance / maintenance.
- Expanded `cube/schema.json` and `cube/index.csv` with eight risk-reduction conversion fields.
- Added source IDs `S726`–`S740`.
- Extended open questions with `158`–`165`.

## Defect addressed

rev0281 could close recovery with household-function outcomes and nonrecurrence language, but it did not yet force the next operational handoff: convert closeout findings into risk-reduction projects, prevent new exposure, govern future-condition data, and verify that completed mitigation performs over time.

## Expected validation

- numbered files continuous from `00` through `412`;
- `cube/index.csv` has 413 rows and 104 columns;
- source register continuous through `S740`;
- no unresolved or unused source IDs;
- numeric `routes_to` targets point to existing numbered files;
- all cube CSVs parse;
- all numbered files have front matter, H1, and terminal citation footer.
