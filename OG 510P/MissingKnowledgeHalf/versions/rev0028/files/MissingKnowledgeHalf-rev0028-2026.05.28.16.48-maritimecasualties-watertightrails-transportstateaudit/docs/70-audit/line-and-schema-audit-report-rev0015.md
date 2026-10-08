# rev0015 line and schema audit report

## Automated checks

- JSON parse: passed for all JSON files inspected.
- Promoted record index: passed; all indexed paths exist and all record IDs match their files.
- Record counts: unchanged from rev0014 / rev0013.
- Claim count: 294 record claims; 294 unique claim IDs.
- Source count: 140 source records.
- Claim references: 431 claim support references; 0 unknown references.
- Source permanence: all 140 sources have permanence ledger entries; source-permanence support lists now reconcile against source_payload.supports_record_ids.
- Source permanence support reconciliation: passed after repairing four early source entries.
- Jsonschema validation: added to lint in rev0015 for unified plus per-type schemas.

## Repairs made

1. Updated `schemas/source-record.schema.json` to validate actual source records.
2. Updated `schemas/unified-record.schema.json` so `links` can temporarily be either an array or a compact dictionary.
3. Added `schemas/pattern-record.schema.json`.
4. Added missing `unknowns` and `next_actions` to `MKH-MET-0006`, `MKH-NEG-0007`, `MKH-NEG-0014`, `MKH-NEG-0015`, `MKH-NEG-0016`, `MKH-INF-0024`, `MKH-INF-0025`, `MKH-INF-0026`, `MKH-INF-0027`, `MKH-INF-0028`, and `MKH-PAT-0013`.
5. Updated stale `WITNESS-VOCABULARY.json` revision and vocabulary.
6. Backfilled missing conversation receipts for rev0001, rev0004, rev0009, rev0010, and rev0013.
7. Reconciled four source-permanence support lists with their source records and added lint/audit checks for future drift.

## Unresolved debt

- 57 pattern/synthesis claim-support entries currently use the field name `source_id` while pointing to non-source records. This is not dangling, but it is semantically wrong enough to deserve migration.
- 10 claims use weak locator language such as search/snippet locators.
- 38 source records have weak or search/snippet-heavy locator extraction.
- Source `evidence_class` has 123 distinct tokens; source `permanence_token` has 20 distinct tokens. This is expressive but not yet query-stable.

## Interpretation

The cube is coherent enough to continue, but not clean enough to scale blindly. The next high-value work is not necessarily more cases. It is locator repair, graph-edge migration, pattern controls, and second review.

