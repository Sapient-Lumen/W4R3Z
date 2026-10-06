# Archive economy audit

This generated audit measures release-path mass, checker sprawl, large prose surfaces, path-length pressure, and queue sediment.
It exists to make the next deletion/refactor move concrete instead of adding another abstract governance layer.

## Counts

- Release-economy files: `849`
- Release-economy bytes: `14786620`
- Markdown files / words: `325` / `536492`
- Python files: `317`
- Validation tools: `217`
- Checker files / contract checkers: `217` / `170`
- Generator tools: `19`
- Max path length: `177`

## Risk flags
- `AE-RISK-0001` — `release_file_count_gt_700` = `849`; repair: compact or consolidate low-signal witness/checker surfaces before adding new families
- `AE-RISK-0002` — `markdown_words_gt_500k` = `536492`; repair: prefer deltas, generated indexes, and retired-history summaries over new long prose

## Largest files
- `DATACUBE-TRANSFER-LEDGER.json` — `853342` bytes
- `LEDGER-COLDSTORE.json` — `696953` bytes
- `FOREIGN-PRESSURE-LEDGER.json` — `598616` bytes
- `ASSUMPTION-LEDGER.json` — `484585` bytes
- `HOT-SURFACE-COMPACTION-ORIGINALS.json` — `479235` bytes
- `RESOLUTION-LEDGER.json` — `451317` bytes
- `OBLIGATION-LEDGER.json` — `411630` bytes
- `APPLICABILITY-LEDGER.json` — `395407` bytes
- `FOLLOWTHROUGH-QUEUE.json` — `364850` bytes
- `docs/00-meta/bibliography.md` — `338606` bytes
- `FIREBREAK-LEDGER.json` — `332211` bytes
- `SCHEMA-CONFORMANCE-AUDIT.json` — `330666` bytes

## Largest markdown by words
- `docs/00-meta/trajectory-map.md` — `36521` words
- `docs/00-meta/bibliography.md` — `33934` words
- `docs/20-constitution/open-question-registry.md` — `30118` words
- `docs/20-constitution/claim-registry.md` — `22063` words
- `CHANGELOG.md` — `14346` words
- `docs/50-promptcraft/prompt-pairs.md` — `11621` words
- `docs/10-method/method-overview.md` — `10779` words
- `docs/10-method/external-optimizer-loops-public-slow-weights-and-archive-write-gates.md` — `10175` words
- `docs/90-quarantine/wild-speculations-2026-03-08.md` — `9005` words
- `docs/20-constitution/prompt-pair-registry.md` — `7959` words
- `docs/10-method/operator-tokens-and-bootstrap-grammar.md` — `7681` words
- `docs/20-constitution/invariant-registry.md` — `7150` words

## Completed refactors
- `tools/check_declarative_witness_contract_batch.py` batches `36` formerly one-file declarative witness contracts.
- `tools/check_shadow_batch_contract.py` batches `29` formerly one-file shadow contract wrappers.
- `HOT-SURFACE-COMPACTION.json` compacts `4` hot markdown surfaces with word delta `-149284` and source bundle `HOT-SURFACE-COMPACTION-ORIGINALS.json`.
- `tools/check_hot_surface_source_roundtrip_contract.py` restores `4` pre-compaction targets from `HOT-SURFACE-COMPACTION-ORIGINALS.json` in a temporary tree.
- `tools/check_ledger_debt_guard.py` enforces live-ledger budgets and cross-field/cohort consistency: FOLLOWTHROUGH-QUEUE.json queued=164/180 (headroom 16), ASSUMPTION-LEDGER.json active=164/180 (headroom 16), OBLIGATION-LEDGER.json open=163/180 (headroom 17), RETROSPECTIVE-QUEUE.json cooling=152/180 (headroom 28); mirror mismatches `0`, orphaned cooling retrospectives `0`.
- `tools/check_ledger_coldstore_roundtrip_contract.py` verifies `1322` cold-stored historical ledger rows in `LEDGER-COLDSTORE.json` with net plaintext savings `530448` bytes.
- `tools/check_receipt_coldstore_roundtrip_contract.py` verifies `125` cold-stored historical receipt keys in `RECEIPT-COLDSTORE.json` with net plaintext savings `55680` bytes.
- `tools/check_gpustorming_late_search_family_batch_contract.py` batches `13` late-search GPustorming family contracts.
- `tools/check_gpustorming_standard_family_batch_contract.py` batches `40` standard GPustorming family contracts with no stored source payloads and `4` spec parts; max part bytes `33711`.
- `tools/check_gpu_witness_batch_contract.py` batches `54` GPU witness contracts with `4` spec parts; max part bytes `90999`.
- `tools/check_method_doc_ratchet_batch_contract.py` batches `18` method-doc prompt/runbook ratchet contracts with `2` spec parts; max part bytes `9783`.
- `tools/check_core_method_batch_contract.py` batches `20` core method/state contracts with `2` spec parts; max part bytes `8852`; source documents remain semantic surfaces.
- `PATH-ALIAS-LEDGER.json` records `4` batch alias groups covering `132` former checker paths without wrapper regrowth.
- `tools/check_release_integrity_contract.py` now delegates to `tools/release_integrity_contract_lib.py` and `tools/check_release_integrity_negative_canaries.py` covers `7` manifest/checksum/provenance mutations with failures `0`.
- `tools/package_release.py` now runs `tools/package_preflight_lib.py` before deterministic zip emission and again on a clean extracted artifact before verified sidecar writing; order `refresh-preflight-zip-artifact-smoke-verified-sidecar`; mutation canaries `6` with failures `0`; deterministic writer canaries `5` with failures `0`; sidecar canaries `5` with failures `0`.
- `tools/check_priority_zero_burden_gate_contract.py` checks `assays/priority-zero-burden-gate-2026-06-15.json`: hot Current additions `48` → `18`, decisions `4`, successor `OQ-0254`.

## Checker consolidation candidates
- `tools/check_external_metadata_contract.py` — `5` nonblank noncomment lines
- `tools/check_hot_surface_compaction_contract.py` — `5` nonblank noncomment lines
- `tools/check_shadow_batch_contract.py` — `5` nonblank noncomment lines
- `tools/check_release_integrity_contract.py` — `8` nonblank noncomment lines
- `tools/check_ledger_coldstore_roundtrip_contract.py` — `8` nonblank noncomment lines
- `tools/check_core_method_batch_contract.py` — `11` nonblank noncomment lines
- `tools/check_receipt_coldstore_roundtrip_contract.py` — `11` nonblank noncomment lines
- `tools/check_hot_surface_source_roundtrip_contract.py` — `13` nonblank noncomment lines
- `tools/check_json_schema_surface_contract.py` — `14` nonblank noncomment lines
- `tools/check_recovery_kernel_contract.py` — `14` nonblank noncomment lines
- `tools/check_link_integrity_policy_contract.py` — `14` nonblank noncomment lines
- `tools/check_prompt_pair_contract.py` — `16` nonblank noncomment lines

## Non-claim

Archive economy metrics are triage evidence only: not a deletion court, quality score, completeness proof, semantic authority, or permission to remove governing surfaces without ordinary review.
