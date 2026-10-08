# Structural audit — rev0281

## Scope

This audit checked the rev0280 package before adding the household-function and recovery-closeout layer.

## Findings

- Numbered files were continuous from `00` through `396`.
- `cube/index.csv` and `cube/schema.json` matched at 88 columns.
- All registered source IDs `S1`–`S713` resolved and were cited.
- No cube CSV parse defects were found.

## Revision action

rev0281 adds files `397`–`404`, adds eight new schema fields, and adds three household-function / closeout cube views. The new layer tests whether recovery reaches functional household outcomes rather than stopping at intake, referral, assistance award, or administrative case closure.

## New validation target

The rev0281 package should validate with:

- numbered Markdown files continuous from `00` through `404`;
- `cube/index.csv` containing 405 rows;
- `cube/schema.json` and `cube/index.csv` sharing the same 96 field names;
- source register continuous through `S725`;
- all new source IDs cited at least once;
- all numeric routes pointing to existing numbered files;
- all cube CSVs parseable.

---
Citations point to `sources/register.md`.
