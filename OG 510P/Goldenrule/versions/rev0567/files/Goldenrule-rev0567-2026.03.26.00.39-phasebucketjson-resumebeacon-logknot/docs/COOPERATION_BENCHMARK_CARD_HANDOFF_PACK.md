# Cooperation Benchmark Card Handoff Pack

Generated minimal citation handoff manifest for compact cooperation-card lineages. Each pack is fail-closed to one unique current citation head and carries the exact ancestry basis, file hashes, and local verification / refresh commands needed by inheritors.

- lineage_count: 1
- pack_count: 1
- unresolved_lineage_count: 0
- total_file_count: 17
- total_bytes: 146956
- scope_manifest_sha256: `aab567dd654ea003a86ed735c181cd0d76bbe23c18873f7e09797e7a6b4f89ea`

## Packs

| lineage_id | citation_head | ancestry_cards | delta_receipts | file_count | pack_bytes | basis_manifest_sha256 |
|---|---|---:|---:|---:|---:|---|
| `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer` | `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer-v2` | 2 | 1 | 17 | 146956 | `c7d966859d48f7fca9efa5f290a2966b045bde8da5112c9d0b42af847c1b88f5` |

## Per-pack details

### `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer`

- pack_id: `cooperation-benchmark-card-handoff:cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer:cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer-v2`
- benchmark_name: `Toy IPD fresh-partner transfer benchmark (toy-agent-v2)`
- citation_head_card_id: `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer-v2`
- citation_head_card_path: `examples/snapshots/cooperation_benchmark_card_example_v2.json`
- operational_head_card_id: `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer-v2`
- operational_head_card_path: `examples/snapshots/cooperation_benchmark_card_example_v2.json`
- primary_open_path: `examples/snapshots/cooperation_benchmark_card_example_v2.md`
- primary_open_target: `examples/snapshots/cooperation_benchmark_card_example_v2.md` (`primary-open`, `citation-rendered-markdown`, `operational-rendered-markdown`)
- entry_targets: `examples/snapshots/cooperation_benchmark_card_example_v2.md` (`primary-open`, `citation-rendered-markdown`, `operational-rendered-markdown`); `examples/snapshots/cooperation_benchmark_card_example_v2.json` (`citation-card`, `operational-card`); `examples/snapshots/cooperation_benchmark_card_example_v2.freeze_receipt.json` (`citation-freeze-receipt`)
- ancestry_card_ids: `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer`, `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer-v2`
- delta_receipt_paths: `examples/snapshots/cooperation_benchmark_card_example.delta_receipt.json`
- claim_surface_change_count: 1
- metadata_only_change_count: 0
- basis_manifest_sha256: `c7d966859d48f7fca9efa5f290a2966b045bde8da5112c9d0b42af847c1b88f5`
- must_read_paths:
  - `docs/BENCHMARK_PROGRAM.md`
  - `examples/snapshots/cooperation_benchmark_card_example_v2.md`
  - `examples/snapshots/cooperation_benchmark_card_example_v2.json`
  - `examples/snapshots/cooperation_benchmark_card_example_v2.freeze_receipt.json`
  - `docs/COOPERATION_BENCHMARK_CARD_CITATION_SURFACE.md`
  - `docs/COOPERATION_BENCHMARK_CARD_HEADS.md`
  - `docs/COOPERATION_BENCHMARK_CARD_INVENTORY.md`
  - `docs/COOPERATION_BENCHMARK_CARD_REVIEW_QUEUE.md`
  - `docs/COOPERATION_BENCHMARK_CARD_MACRO_REVIEW_QUEUE.md`
  - `docs/COOPERATION_BENCHMARK_CARD_NEXT_ACTION_WITNESS.md`
  - `docs/COOPERATION_BENCHMARK_CARD_NEXT_ACTION.md`
  - `docs/COOPERATION_BENCHMARK_CARD_EXECUTION_LANES.md`
  - `docs/COOPERATION_BENCHMARK_CARD_TAXONOMY.md`
  - `docs/COOPERATION_BENCHMARK_CARD_SCOPE_SURFACE.md`
- primary_verify_command: `./grpy ./scripts/test/check_cooperation_benchmark_card_citation_surface.py`
- primary_verify_target: `artifacts/reports/cooperation_benchmark_card_citation_surface.json` (`primary-verify-target`, `citation-surface-report`)
- primary_verify_target_bytes: 1480
- primary_verify_target_sha256: `067443d7a469974af5ed1aa0f8d988c577ae196c361d824cd6e0a06596fc9e9c`
- primary_verify_target_citation_entry_count: 1
- primary_verify_target_citation_lineage_count: 1
- primary_verify_target_unresolved_lineage_count: 0
- primary_verify_target_scale_summary: Citation surface report with citation_entry_count=1, citation_lineage_count=1, unresolved_lineage_count=0.
- primary_verify_subject_role_code: `citation-surface-report`
- primary_verify_intent_summary: Verify citation surface report.
- primary_verify_outcome_summary: Expect clean validator exit for citation surface report.
- verify_commands:
  - `./grpy ./scripts/test/check_cooperation_benchmark_card_citation_surface.py`
  - `./grpy ./scripts/test/check_cooperation_benchmark_card_macro_review_queue.py`
  - `./grpy ./scripts/test/check_cooperation_benchmark_card_next_action_witness.py`
  - `./grpy ./scripts/test/check_cooperation_benchmark_card_next_action.py`
  - `./grpy ./scripts/test/check_cooperation_benchmark_card_taxonomy.py`
  - `./grpy ./scripts/test/check_cooperation_benchmark_card_scope_surface.py`
  - `./grpy ./scripts/test/check_cooperation_benchmark_card_execution_lanes.py`
  - `./grpy ./scripts/test/check_cooperation_benchmark_card_handoff_pack.py`
  - `./grpy ./scripts/tools/cooperation_benchmark_card.py render examples/snapshots/cooperation_benchmark_card_example_v2.json`
- primary_refresh_command: `./grpy ./scripts/report/build_cooperation_benchmark_card_inventory.py --write`
- primary_refresh_target: `artifacts/reports/cooperation_benchmark_card_inventory.json` (`primary-refresh-target`, `inventory-report`)
- primary_refresh_target_bytes: 5630
- primary_refresh_target_sha256: `f73e546359b15827da23c31e4e1f1bb763e781cde461c363e08f2624405f1cf5`
- primary_refresh_target_card_count: 2
- primary_refresh_target_verified_delta_receipt_count: 1
- primary_refresh_target_latest_known_card_count: 1
- primary_refresh_target_scale_summary: Inventory report with card_count=2, verified_delta_receipt_count=1, latest_known_card_count=1.
- primary_refresh_subject_role_code: `inventory-report`
- primary_refresh_intent_summary: Refresh inventory report.
- primary_refresh_outcome_summary: Expect inventory report to be rewritten in place.
- refresh_commands:
  - `./grpy ./scripts/report/build_cooperation_benchmark_card_inventory.py --write`
  - `./grpy ./scripts/report/build_cooperation_benchmark_card_heads.py --write`
  - `./grpy ./scripts/report/build_cooperation_benchmark_card_review_queue.py --write`
  - `./grpy ./scripts/report/build_cooperation_benchmark_card_macro_review_queue.py --write`
  - `./grpy ./scripts/report/build_cooperation_benchmark_card_citation_surface.py --write`
  - `./grpy ./scripts/report/build_cooperation_benchmark_card_next_action_witness.py --write`
  - `./grpy ./scripts/report/build_cooperation_benchmark_card_next_action.py --write`
  - `./grpy ./scripts/report/build_cooperation_benchmark_card_taxonomy.py --write`
  - `./grpy ./scripts/report/build_cooperation_benchmark_card_scope_surface.py --write`
  - `./grpy ./scripts/report/build_cooperation_benchmark_card_execution_lanes.py --write`
  - `./grpy ./scripts/report/build_cooperation_benchmark_card_handoff_pack.py --write`
- files:
  - `schemas/cooperation_benchmark_card.schema.json` (card-schema, 9615 bytes, sha256 `4c73b5ad7c0a76c079864c8ec9035c1bf7595e553bbb3f8cb4517ab296e05b25`)
  - `scripts/tools/cooperation_benchmark_card.py` (card-tool, 20182 bytes, sha256 `85740c85f6e31e176a716d58a1f3ce51508d3511fa3caccabd66465d85dfc7b0`)
  - `examples/snapshots/cooperation_benchmark_card_example_v2.json` (citation-card, 6924 bytes, sha256 `a2f5c4aa0ee8263d3d24d24ad1fe6ef69b421ddaff6718c4a7cfea57862db6db`)
  - `examples/snapshots/cooperation_benchmark_card_example_v2.freeze_receipt.json` (citation-freeze-receipt, 1375 bytes, sha256 `faecd1ec68b9793884670d29d49bbb5b519ac1d8f44326d4d06825d61f38e4b4`)
  - `examples/snapshots/cooperation_benchmark_card_example_v2.md` (citation-rendered-markdown, 6680 bytes, sha256 `ef9d265d3059aed17cc2607c6cb9d74f7f31e1be952e37463903e3d3a7d3d1c9`)
  - `artifacts/reports/cooperation_benchmark_card_citation_surface.json` (citation-surface-report, 1480 bytes, sha256 `067443d7a469974af5ed1aa0f8d988c577ae196c361d824cd6e0a06596fc9e9c`)
  - `schemas/cooperation_benchmark_card_delta_receipt.schema.json` (delta-receipt-schema, 1918 bytes, sha256 `230165dfd3d73553faf9868f44238f8ae646f84aed0c2cda1f4356916ec6a5c5`)
  - `artifacts/reports/cooperation_benchmark_card_execution_lanes.json` (execution-lanes-report, 3740 bytes, sha256 `45c55918de5b055d3765a06c2bba1ea8345d08a9f53107c9372f739aa37ab5a3`)
  - `schemas/cooperation_benchmark_card_freeze_receipt.schema.json` (freeze-receipt-schema, 2553 bytes, sha256 `d5507138230c506d84cd85af34a6ed1d3b9da6f9fb30a38f5b064cdf3b92aefd`)
  - `artifacts/reports/cooperation_benchmark_card_heads.json` (heads-report, 1872 bytes, sha256 `ad22c77b27b232b63c01bf782d080f6df4a3612ac7b1e9133461f14ae149e193`)
  - `artifacts/reports/cooperation_benchmark_card_inventory.json` (inventory-report, 5630 bytes, sha256 `f73e546359b15827da23c31e4e1f1bb763e781cde461c363e08f2624405f1cf5`)
  - `examples/snapshots/cooperation_benchmark_card_example.json` (lineage-basis-card, 6891 bytes, sha256 `e033c1d6dd6970f7ed1ffd9a178e92e094cb14c0bdd02f03751e04bae131e8ee`)
  - `examples/snapshots/cooperation_benchmark_card_example.delta_receipt.json` (lineage-delta-receipt, 1323 bytes, sha256 `c98e0e9b9336579afcd617ae733c199b6a44f44df3726578756892c37192cc72`)
  - `artifacts/reports/cooperation_benchmark_card_macro_review_queue.json` (macro-review-queue-report, 490 bytes, sha256 `54c999cb585f2d8ca505d290d90eeaeaf42542c57a88460f69032dd36c2fb2aa`)
  - `artifacts/reports/cooperation_benchmark_card_review_queue.json` (review-queue-report, 422 bytes, sha256 `85ddd1c89fab4bd32d00a7c0b61f9da298f3e7079fc10c2ab31f28902c527c04`)
  - `artifacts/reports/cooperation_benchmark_card_scope_surface.json` (scope-surface-report, 49683 bytes, sha256 `beee4faac05ef530fe7c1e7809d7d20d746ceacb856f30d798b7c10759f7ec47`)
  - `artifacts/reports/cooperation_benchmark_card_taxonomy.json` (taxonomy-report, 26178 bytes, sha256 `70db60f94d65d5cafac961758686c074d9e19dd5708af37d1b1509f276680698`)

