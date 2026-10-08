# Archive Reentry Card

Compact reentry pointer for future inheritors: identify the current archive head, confirm whether the changelog head agrees, and give one primary open target plus first commands for the blocked cloudtainer, the first Rust-capable machine, and the final package cut.

## Headline findings

- Current archive head is `Goldenrule-rev0565-2026.03.25.23.58-offlineproofladder-cachetruth-nightsignal` and the changelog head is `rev0565` on 2026-03-25; alignment=True.
- This cloudtainer remains `junest_binary_missing` with mode=`stay_static_here`, so the local first move is `make cloudtainer-shadow-pass-medium` rather than more in-place Rust recovery poking.
- The first Rust-capable foothold is still one apply + one exact witness: `git apply artifacts/patches/rust_external_test_shards/01_fsm_grim_trigger_probe.patch` then `cargo test -p gr_engine --test probe_run lift_fsm_strategy_family_lift_first_seed -- --exact`.
- The final Rust comeback closure still requires the dual-lane shard `artifacts/patches/rust_external_test_shards/10_scaling_prefix_stability_probe_seed.patch`, so full probe closure and full queue closure coincide at prefix 10.
- Package-cut posture remains ready=True with pdf_count=0 and scratch_file_count=0; the canonical settle wrapper is `make settle-archive-truth`, the external reopen resolver is `python3 scripts/tools/resolve_authoritative_archive_zip.py --emit zip-path`, the normalized next-name planner is `python3 scripts/tools/plan_archive_revision_cut.py --descriptor your-summary-slug`, the canonical cutter is `python3 scripts/tools/cut_archive_revision.py --descriptor your-summary-slug --summary "one-line summary"`, and the first byte-diet open target stays `docs/ARCHIVE_BYTE_TRIAGE_CARD.md`.

## Current archive head

- root_name: `Goldenrule-rev0565-2026.03.25.23.58-offlineproofladder-cachetruth-nightsignal`
- revision_label: `rev0565`
- timestamp_iso_minute: `2026-03-25T23:58`
- descriptor_slug: `offlineproofladder-cachetruth-nightsignal`
- changelog_aligned_to_root: `True`
- latest_recorded_revision: `rev0565` (2026-03-25)
- immediate_predecessor_revision: `rev0564` (2026-03-25)

Recent changelog chain tail:

- `rev0560` (2026-03-24)
- `rev0561` (2026-03-25)
- `rev0562` (2026-03-25)
- `rev0563` (2026-03-25)
- `rev0564` (2026-03-25)
- `rev0564` (2026-03-25)
- `rev0565` (2026-03-25)

## Blocked cloudtainer role

- primary_open_doc: `docs/CLOUDTAINER_RUST_RECOVERY_CARD.md`
- current_state_code: `junest_binary_missing`
- mode: `stay_static_here`
- primary_command: `make cloudtainer-shadow-pass-medium`
- budget_seconds: `38.141`
- preferred_lane_id: `python-integrity`
- blocking_reason_codes: `junest-binary-missing, native-cargo-missing, native-rustc-missing`
- reason: The documented in-place recovery ladder is blocked before setup/install because the JuNest binary itself is absent or the wrapper state is nonstandard.
- followup_commands:
  - `make cloudtainer-shadow-pass-resume`
  - `make update-rust-comeback-execution-card`

## First Rust-capable machine role

- primary_open_doc: `docs/RUST_COMEBACK_EXECUTION_CARD.md`
- quick_foothold_prefix: `1`
- primary_apply_hint: `git apply artifacts/patches/rust_external_test_shards/01_fsm_grim_trigger_probe.patch`
- primary_exact_witness_command: `cargo test -p gr_engine --test probe_run lift_fsm_strategy_family_lift_first_seed -- --exact`
- lane_smoke_command: `cargo test -p gr_engine --test probe_run`
- refresh_command: `make update-rust-comeback-execution-card`
- final_dual_lane_shard_path: `artifacts/patches/rust_external_test_shards/10_scaling_prefix_stability_probe_seed.patch`
- full_closure_prefix: `10`
- full_closure_dual_lane: `True`

## Package-cut steward role

- primary_open_doc: `docs/ARCHIVE_PACKAGE_CUT_CARD.md`
- primary_settle_command: `make settle-archive-truth`
- handoff_pack_open_doc: `docs/ARCHIVE_HANDOFF_PACK.md`
- handoff_pack_verify_command: `make test-archive-handoff-pack`
- handoff_pack_integrity_command: `python3 scripts/tools/verify_archive_handoff_pack.py`
- handoff_pack_refresh_command: `make update-archive-handoff-pack`
- external_digest_verify_command: `python3 scripts/tools/verify_authoritative_archive_zip.py`
- revision_planner_open_doc: `docs/ARCHIVE_REVISION_CUT_CARD.md`
- revision_planner_command: `python3 scripts/tools/plan_archive_revision_cut.py --descriptor your-summary-slug`
- canonical_cut_command: `python3 scripts/tools/cut_archive_revision.py --descriptor your-summary-slug --summary "one-line summary"`
- package_boundary_ready: `True`
- primary_gate_command: `make test-quick`
- inventory_commands:
  - `make update-command-inventory`
  - `make update-validator-inventory`
  - `make update-artifact-buckets`
- fixed_point_pair:
  - `make update-archive-size-guardrail-card`
  - `make update-archive-byte-triage-card`
- final_validation_commands:
  - `make test-archive-size-guardrail-card`
  - `make test-archive-byte-triage-card`
  - `make test-archive-package-cut-card`
  - `make test-archive-reentry-card`
  - `make test-archive-handoff-pack`
  - `make test-archive-handoff-pack-verify-tool`
  - `make test-authoritative-archive-zip-verify-tool`
  - `make test-archive-revision-cut-card`
  - `make test-archive-zip-lineage-card`
  - `make test-archive-zip-chronology-card`
  - `make test-archive-zip-authority-card`
  - `make test-archive-zip-digest-card`
  - `make test-archive-zip-size-truth-card`
- diet_first_open_doc: `docs/ARCHIVE_BYTE_TRIAGE_CARD.md`
- diet_first_paths:
  - `docs/AGENT_LOG.md`
  - `CHANGELOG.md`
  - `docs/RESEARCH_SOURCES.md`
  - `artifacts/process/2026-03-21-research-pass.md`

## Source surfaces

- `artifacts/reports/cloudtainer_rust_recovery_card.json`
- `artifacts/reports/rust_comeback_execution_card.json`
- `artifacts/reports/archive_package_cut_card.json`
- `artifacts/reports/archive_size_guardrail_card.json`
- `artifacts/reports/archive_byte_triage_card.json`
- `artifacts/reports/archive_handoff_pack.json`
- `artifacts/reports/archive_zip_size_truth_card.json`
- `docs/CLOUDTAINER_RUST_RECOVERY_CARD.md`
- `docs/RUST_COMEBACK_EXECUTION_CARD.md`
- `docs/ARCHIVE_PACKAGE_CUT_CARD.md`
- `docs/ARCHIVE_HANDOFF_PACK.md`
- `docs/ARCHIVE_ZIP_AUTHORITY_CARD.md`
- `docs/ARCHIVE_ZIP_SIZE_TRUTH_CARD.md`
- `docs/ARCHIVE_REVISION_CUT_CARD.md`
- `docs/ARCHIVE_BYTE_TRIAGE_CARD.md`
- `CHANGELOG.md`
