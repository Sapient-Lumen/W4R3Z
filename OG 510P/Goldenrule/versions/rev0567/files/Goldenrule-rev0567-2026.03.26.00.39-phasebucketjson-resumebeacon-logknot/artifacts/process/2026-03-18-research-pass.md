# 2026-03-18 Research Pass

## What changed

- Executed the standing cited exact-file compaction frontier on the live tree again:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `119721` raw report bytes from the current manifest frontier,
  - refreshed `examples/snapshots/rematch_world_benchmark_package_receipt.json`,
  - refreshed `examples/snapshots/archive_report_{hotspot,semantic_handle,compaction_candidate,compaction_gap,compaction_manifest,compaction_rehearsal,compaction_stage,compaction_execution}_receipt.json`,
  - refreshed `artifacts/reports/{artifact_summary.json,artifact_bucket_inventory.json,archive_size_profile_snapshot_20260316.json,archive_size_profile_snapshot_20260316.md}`,
  - and refreshed `docs/ARTIFACT_BUCKETS.md`.
- Added one compact inheritor-facing benchmark note:
  - `docs/LIBRARY/topics/benchmark_interoperability_should_separate_partner_environment_and_institution_generalization.md`
- Extended `docs/RESEARCH_SOURCES.md` with three current interoperability / zero-shot-cooperation references:
  - `RS-GR-036` OGC,
  - `RS-GR-037` CEC,
  - `RS-GR-038` SocialJax.

## Main local result

- The retained report bucket shrank by another `119721` raw bytes without minting a new durable compaction note family.
- The compact interoperability note sharpens Phase C benchmarking without widening the archive: the next inheritor should score partner, environment, and institution novelty separately inside one small retained summary rather than by adding more benchmark sidecars.
- The current container still does not clear the Rust lane in `make test-quick` because `junest` is missing at `/run/sandworm/toolroot/bin/junest`; the Python-side unit slice passed before that environment failure.

## Inheritor guidance

- For archive size: start from the refreshed manifest / rehearsal / stage receipts on the smaller tree; do not reopen the already executed frontier.
- For benchmark design: do not collapse cross-partner, cross-environment, and cross-institution novelty into one blended holdout score.
- For local validation: treat the `junest` failure as environment drift first; recheck the Rust lane in a fuller Sandworm-equipped environment before interpreting it as code regression.

## Additional pass — Twentieth canonical trim + reputation contract reclosure

### What changed

- Added one compact inheritor-facing contract note:
  - `docs/LIBRARY/topics/rematch_worlds_should_publish_reputation_assessment_and_diffusion_rules_as_a_world_contract.md`
- Extended `docs/RESEARCH_SOURCES.md` with `RS-GR-041` so reputation-bearing rematch or partner-choice worlds publish one compact reputation contract instead of hiding gossip mechanics in controller detail.
- Reclosed the refreshed current and projected frontier without retaining new report pairs:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `4` additional aliases for suffix counters, strict predecessor backsteps, benchmark fill-status templates, and packed scalar atoms.
- Executed one more cited exact-file compaction frontier on the live tree:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `101936` raw report bytes from the pre-trim frontier,
  - refreshed `examples/snapshots/rematch_world_benchmark_package_receipt.json`,
  - refreshed `examples/snapshots/archive_report_{hotspot,semantic_handle,compaction_candidate,compaction_gap,compaction_manifest,compaction_rehearsal,compaction_stage,compaction_execution}_receipt.json`,
  - refreshed `artifacts/reports/{artifact_summary.json,artifact_bucket_inventory.json,archive_size_profile_snapshot_20260316.json,archive_size_profile_snapshot_20260316.md}`,
  - and refreshed `docs/ARTIFACT_BUCKETS.md`.

### Main local result

- The semantic-handle receipt now recovers `4` alias-backed families covering `64419` report-bucket bytes.
- The current gap receipt reports `0` hotspot handle gaps and the refreshed rehearsal reports `0` projected next-frontier handle gaps.
- The refreshed next manifest covers `97717` raw bytes across `6` families and `12` retained report files.
- The live tree measures `1538` retained files, `10624446` raw bytes, and an approximate revision zip of `2985819` bytes.
- The refreshed execution receipt passes `26/26` checks and proves the `101936`-byte cited trim executed on the live archive.

### Local validation

- `python3 scripts/test/check_reports_json_valid.py`
- `python3 scripts/test/check_research_docs.py`
- `make test-quick` still clears the Python slice (`6` tests, `OK`) and then stops in the Rust lane because `junest` is missing at `/run/sandworm/toolroot/bin/junest`; treat that as environment drift first rather than archive regression.



## Additional pass — Twenty-first canonical trim + adaptation contract + frontier reclosure

### What changed

- Added one compact inheritor-facing contract note:
  - `docs/LIBRARY/topics/rematch_worlds_should_publish_starting_policy_and_adaptation_rules_as_a_world_contract.md`
- Extended `docs/RESEARCH_SOURCES.md` with `RS-GR-042` so rematch worlds that evaluate test-time adaptation from a standing strategic prior publish the starting-policy source, adaptation rule, state-carry rule, and adaptation budget as world-contract metadata.
- Executed one more cited exact-file compaction frontier on the live tree:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `88278` raw report bytes from the pre-trim frontier,
  - refreshed `examples/snapshots/rematch_world_benchmark_package_receipt.json`,
  - refreshed `examples/snapshots/archive_report_{hotspot,semantic_handle,compaction_candidate,compaction_gap,compaction_manifest,compaction_rehearsal,compaction_stage,compaction_execution}_receipt.json`,
  - and kept the archive package-ready, PDF-free, scratch-free, and pycache-free after the trim.
- Reclosed the refreshed live hotspot and projected next frontier without retaining new report pairs:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `5` additional aliases for preference half-spaces, fixed-policy regret, grouped repeated weight atoms, shared decision-packet provenance profiles, and hazard-preference regimes.

### Main local result

- The retained tree now measures `1503` files, `10336101` raw bytes, and an approximate revision zip of `2917539` bytes.
- The live report bucket now measures `220` files / `1142504` raw bytes.
- The semantic-handle receipt now recovers `5` alias-backed families covering `69081` report-bucket bytes.
- The current gap receipt reports `0` hotspot handle gaps and the refreshed rehearsal reports `0` projected next-frontier handle gaps.
- The refreshed next manifest covers `83154` raw bytes across `6` families and `12` retained report files.
- The refreshed execution receipt passes `26/26` checks and proves the `88278`-byte cited trim executed on the live archive.

### Local validation

- `python3 scripts/test/check_reports_json_valid.py`
- `python3 scripts/test/check_research_docs.py`
- `python3 scripts/test/check_archive_report_semantic_handle_receipt.py`
- `python3 scripts/test/check_archive_report_compaction_candidate_receipt.py`
- `python3 scripts/test/check_archive_report_compaction_gap_receipt.py`
- `python3 scripts/test/check_archive_report_compaction_manifest_receipt.py`
- `python3 scripts/test/check_archive_report_compaction_rehearsal_receipt.py`
- `python3 scripts/test/check_archive_report_compaction_stage_receipt.py`
- `python3 scripts/test/check_archive_report_compaction_execution_receipt.py`
- `make test-quick` still clears the Python slice (`6` tests, `OK`) and then stops in the Rust lane because `junest` is missing at `/run/sandworm/toolroot/bin/junest`; treat that as environment drift first rather than archive regression.


## Additional pass — Twenty-second canonical trim + governance contract + source register repair

### What changed

- Repaired the source register so the standing adaptation-contract note now cites a real numbered source row:
  - restored `RS-GR-042` in `docs/RESEARCH_SOURCES.md` for Luo et al. (2026).
- Added one compact inheritor-facing contract note:
  - `docs/LIBRARY/topics/rematch_worlds_should_publish_sanction_and_restoration_graphs_as_a_world_contract.md`
- Extended `docs/RESEARCH_SOURCES.md` with `RS-GR-043` so rematch or benchmark worlds that move agents through sanctions / restoration paths publish that governance graph as explicit world-contract metadata.
- Executed one more cited exact-file compaction frontier on the live tree:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `83154` raw report bytes from the pre-trim frontier,
  - refreshed `examples/snapshots/rematch_world_benchmark_package_receipt.json`,
  - refreshed `examples/snapshots/archive_report_{hotspot,semantic_handle,compaction_candidate,compaction_gap,compaction_manifest,compaction_rehearsal,compaction_stage,compaction_execution}_receipt.json`,
  - refreshed `artifacts/reports/{artifact_summary.json,artifact_bucket_inventory.json,archive_size_profile_snapshot_20260316.json,archive_size_profile_snapshot_20260316.md}`,
  - and refreshed `docs/ARTIFACT_BUCKETS.md`.
- Updated the targeted validators so the refreshed smaller-tree frontier is checked against the new current live surface:
  - `scripts/test/check_archive_report_semantic_handle_receipt.py`
  - `scripts/test/check_archive_report_compaction_candidate_receipt.py`
  - `scripts/test/check_archive_report_compaction_manifest_receipt.py`
  - `scripts/test/check_archive_report_compaction_rehearsal_receipt.py`
  - `scripts/test/check_archive_report_compaction_stage_receipt.py`

### Main local result

- The retained tree now measures `1492` files, `10263114` raw bytes, and an approximate revision zip of `2897646` bytes.
- The live report bucket now measures `208` files / `1059350` raw bytes.
- The semantic-handle receipt now recovers `2` alias-backed families covering `27318` report-bucket bytes.
- The current gap receipt reports `0` hotspot handle gaps and the refreshed rehearsal reports `0` projected next-frontier handle gaps.
- The refreshed next manifest covers `80703` raw bytes across `6` families and `12` retained report files.
- The refreshed execution receipt passes `26/26` checks and proves the `83154`-byte cited trim executed on the live archive.

### Local validation

- `python3 scripts/test/check_reports_json_valid.py`
- `python3 scripts/test/check_research_docs.py`
- `python3 scripts/test/check_archive_report_hotspot_receipt.py`
- `python3 scripts/test/check_archive_report_semantic_handle_receipt.py`
- `python3 scripts/test/check_archive_report_compaction_candidate_receipt.py`
- `python3 scripts/test/check_archive_report_compaction_gap_receipt.py`
- `python3 scripts/test/check_archive_report_compaction_manifest_receipt.py`
- `python3 scripts/test/check_archive_report_compaction_rehearsal_receipt.py`
- `python3 scripts/test/check_archive_report_compaction_stage_receipt.py`
- `python3 scripts/test/check_archive_report_compaction_execution_receipt.py`
- `python3 scripts/test/check_rematch_world_benchmark_package_receipt.py`
- `make test-quick` still clears the Python slice (`6` tests, `OK`) and then stops in the Rust lane because `junest` is missing at `/run/sandworm/toolroot/bin/junest`; treat that as environment drift first rather than archive regression.
