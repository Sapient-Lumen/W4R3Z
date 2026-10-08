## 2026-03-25 — Userspace failure resume card
- added `scripts/report/build_cloudtainer_userspace_failure_resume_card.py`, generated `docs/CLOUDTAINER_USERSPACE_FAILURE_RESUME_CARD.md` plus `artifacts/reports/cloudtainer_userspace_failure_resume_card.json`, and added a dedicated validator `scripts/test/check_cloudtainer_userspace_failure_resume_card.py`
- added `scripts/tools/classify_cloudtainer_userspace_failure.py` and threaded the new failure-resume surface into the Makefile help/target surface, generated-doc presence check, README/docs indexes, environment handbook, and inventories
- preserved one phase-scoped later-machine decoder so bootstrap/path failures resume from rustup setup, offline network or lock drift resumes from warm-cache, compile/codegen failures stop at offline compile, and semantic failures stay pinned to the exact witness or wider `probe_run` smoke lane

## 2026-03-24 — Rematch-world proof-budget ledger
- added `scripts/report/build_rematch_world_benchmark_proof_budget_ledger.py`, generated `docs/REMATCH_WORLD_BENCHMARK_PROOF_BUDGET_LEDGER.md` plus `artifacts/reports/rematch_world_benchmark_proof_budget_ledger.json`, and added a dedicated validator `scripts/test/check_rematch_world_benchmark_proof_budget_ledger.py`
- threaded the new ledger into the Makefile help/target surface, the generated-doc presence check, the README/docs indexes, and the benchmark-program handoff lane so rematch-world proof reuse is now budgeted instead of guessed
- the ledger proves the whole minimal proof library for the eight claim families is only `7` unique surfaces / `43186` bytes, with `6` docs-only bundles and only `2` claim families requiring retained receipt snapshots at all

## 2026-03-24 — Rematch-world stage-yield ledger
- added `scripts/report/build_rematch_world_benchmark_stage_yield_ledger.py`, generated `docs/REMATCH_WORLD_BENCHMARK_STAGE_YIELD_LEDGER.md` plus `artifacts/reports/rematch_world_benchmark_stage_yield_ledger.json`, and added a dedicated validator `scripts/test/check_rematch_world_benchmark_stage_yield_ledger.py`
- threaded the new ledger into the Makefile help/target surface, the generated-doc presence check, the README/docs indexes, and the benchmark-program handoff lane so the first native rematch-world fill pass now has one exact answer to what each stage actually buys
- the ledger preserves the sequencing nuance that only stages `8`, `18`, and `29` unlock new claim families, while `12` and `23` are prerequisite-only resolver closures and `30` is metadata-only closeout rather than new evidence

## 2026-03-24 — Rematch-world closeout lifecycle ledger
- added `scripts/report/build_rematch_world_benchmark_closeout_lifecycle_ledger.py`, generated `docs/REMATCH_WORLD_BENCHMARK_CLOSEOUT_LIFECYCLE_LEDGER.md` plus `artifacts/reports/rematch_world_benchmark_closeout_lifecycle_ledger.json`, and added a dedicated validator `scripts/test/check_rematch_world_benchmark_closeout_lifecycle_ledger.py`
- threaded the new ledger into the Makefile help/target surface, the generated-doc presence check, the README/docs indexes, and the benchmark-program handoff lane so the first real rematch-world publication now has one exact retention/exit/authority witness
- the ledger proves the durable publication set stays at `6` objects / `93320` bytes, the explicit transient exit surface stays at `4` rows / `3728` bytes, and the final retained closeout path lands at `13` exact objects / `125621` bytes only after post-prune, chain, and package authority all succeed

## 2026-03-24 — Rematch-world example delta ledger
- added `scripts/report/build_rematch_world_benchmark_example_delta_ledger.py`, generated `docs/REMATCH_WORLD_BENCHMARK_EXAMPLE_DELTA_LEDGER.md` plus `artifacts/reports/rematch_world_benchmark_example_delta_ledger.json`, and added a dedicated validator `scripts/test/check_rematch_world_benchmark_example_delta_ledger.py`
- threaded the new ledger into the Makefile help/target surface, the generated-doc presence check, the README/docs indexes, and the benchmark-program handoff lane so the first real rematch-world fill pass now has one exact seed-to-compiled mutation witness
- the ledger proves the synthetic compiled artifact still rebuilds from the live packet->patch->artifact toolchain, changes exactly `33` real JSON paths, and splits those into the `30`-path publication floor plus `3` optional second-row insertions inside already-allowed mutable arrays

## 2026-03-24 — Rematch-world native-fill map
- added `scripts/report/build_rematch_world_benchmark_landing_ladder.py`, generated `docs/REMATCH_WORLD_BENCHMARK_LANDING_LADDER.md` plus `artifacts/reports/rematch_world_benchmark_landing_ladder.json`, and added a dedicated validator `scripts/test/check_rematch_world_benchmark_landing_ladder.py`

- added `scripts/report/build_rematch_world_benchmark_native_fill_map.py`, generated `docs/REMATCH_WORLD_BENCHMARK_NATIVE_FILL_MAP.md` plus `artifacts/reports/rematch_world_benchmark_native_fill_map.json`, and added a dedicated validator `scripts/test/check_rematch_world_benchmark_native_fill_map.py`
- threaded the new map into the Makefile help/target surface, the generated-doc presence check, the README/docs indexes, and the benchmark-program handoff lane so the first actual rematch-world fill pass now has one exact edit-locus control surface
- the map fuses the legal mutable prefixes, the 24 live blocker loci, the metadata/status transitions, the allowed decision-contract nulls, and the counting nuance that the smallest publishable edit set is `30` changes rather than `31` because `benchmark_id` is already one of the blocker rows

## 2026-03-24 — Rematch-world world-emission card

- added `scripts/report/build_rematch_world_benchmark_world_emission_card.py`, generated `docs/REMATCH_WORLD_BENCHMARK_WORLD_EMISSION_CARD.md` plus `artifacts/reports/rematch_world_benchmark_world_emission_card.json`, and added a dedicated validator `scripts/test/check_rematch_world_benchmark_world_emission_card.py`
- threaded the new card into the Makefile help/target surface, the generated-doc presence check, the README/docs indexes, and the benchmark-program handoff lane so the first real endogenous rematch benchmark now has one compact inheritor-facing control surface
- the card fuses the five pending native fill targets, the eight copied frozen sections, the publication/prune/package ladder, the durable-vs-transient retention split, and the crucial sequencing nuance that `retention_exit_ready` is only the pre-prune gate rather than the final package authority

## 2026-03-23 — Checkpoint verifier rehearsal recovery

- recovered the missing source-level verifier rehearsal lane by adding `scripts/report/build_rust_standing_bootstrap_checkpoint_verifier_rehearsal.py` plus generated `docs/RUST_STANDING_BOOTSTRAP_CHECKPOINT_VERIFIER_REHEARSAL.md` and `artifacts/reports/rust_standing_bootstrap_checkpoint_verifier_rehearsal.json`
- the new rehearsal proves the verifier itself succeeds on live `clean_head`, direct scratch `repair_only`, route-step `repair_only -> repair_guard`, and direct scratch `final_full`, while also failing closed on drifted content and rejecting conflicting checkpoint expectations
- threaded the rehearsal lane through the Makefile, README/docs indexes, generated-doc presence check, inventories, and `docs/ENVIRONMENT_SANDWORM.md` so the source-level handoff surface now matches the stale compiled hint that had accumulated in `__pycache__`

## 2026-03-23 — Standing bootstrap checkpoint verifier

- added `scripts/tools/verify_rust_standing_bootstrap_checkpoint.py`, generated `docs/RUST_STANDING_BOOTSTRAP_CHECKPOINT_VERIFIER.md` plus `artifacts/reports/rust_standing_bootstrap_checkpoint_verifier.json`, and turned the checkpoint card into a fail-fast exact verifier for both direct recognized-state checks and post-step checkpoint checks
- added `scripts/test/check_rust_standing_bootstrap_checkpoint_verifier_tool.py` so the cloudtainer can keep one live clean-head verification, one direct scratch verification, one route-step scratch verification, and one drift-failure case honest without needing a Rust-capable machine
- threaded the new checkpoint-verifier lane through the Makefile, README/docs indexes, and generated-doc presence check so the first Rust-capable inheritor can prove each bootstrap pause point instead of manually reconciling hashes from nearby cards

## 2026-03-23 — Standing bootstrap execution card and convergent plan rehearsal

- added `scripts/report/build_rust_standing_bootstrap_execution_card.py`, generated `docs/RUST_STANDING_BOOTSTRAP_EXECUTION_CARD.md` plus `artifacts/reports/rust_standing_bootstrap_execution_card.json`, and fused the exact-state selector with the route-equivalence proof into one smallest-safe apply/verify plan for every recognized bootstrap branch state
- added `scripts/tools/emit_rust_standing_bootstrap_execution_plan.py` plus `scripts/report/build_rust_standing_bootstrap_execution_rehearsal.py`, generated `docs/RUST_STANDING_BOOTSTRAP_EXECUTION_REHEARSAL.md` plus `artifacts/reports/rust_standing_bootstrap_execution_rehearsal.json`, and proved in scratch that every recognized non-final branch state converges to the same exact final 4-file hash while drift still fails closed
- threaded the new execution-plan lane through the Makefile, README/docs indexes, generated-doc presence check, and the environment handbook so the first Rust-capable inheritor can run one command to learn what to apply next instead of reconciling the selector and bundle docs manually

## 2026-03-23 — Standing bootstrap comeback bundle and layering proof

- added `scripts/report/build_rust_standing_bootstrap_integration_rehearsal.py`, generated `docs/RUST_STANDING_BOOTSTRAP_INTEGRATION_REHEARSAL.md` plus `artifacts/reports/rust_standing_bootstrap_integration_rehearsal.json`, and proved the narrow bootstrap repair + standalone guard remain operationally orthogonal to the larger Rust comeback patchset in both landing orders (`repair -> guard -> patchset`, shard fallback, and `patchset -> repair -> guard`)
- added `scripts/report/build_rust_standing_bootstrap_comeback_bundle.py` and `scripts/report/build_rust_standing_bootstrap_comeback_bundle_rehearsal.py`, generated `docs/RUST_STANDING_BOOTSTRAP_COMEBACK_BUNDLE.md` / `docs/RUST_STANDING_BOOTSTRAP_COMEBACK_BUNDLE_REHEARSAL.md` plus their reports, and emitted a clean-head one-shot Rust patch that exactly matches the hashed final state of the layered `repair -> guard -> patchset` sequence
- threaded the new integration/bundle lane through the Makefile help surface, README/docs indexes, generated-doc presence check, artifact/command/validator inventories, and the cloudtainer shadow pass so blocked sessions can regenerate and trust the new first-machine landing options without reopening scratch state

## 2026-03-23 — Shadow-pass volatility map

- added `scripts/report/build_cloudtainer_shadow_pass_volatility.py`, generated `docs/CLOUDTAINER_SHADOW_PASS_VOLATILITY.md` plus `artifacts/reports/cloudtainer_shadow_pass_volatility.json`, and wired `make update-cloudtainer-shadow-pass-volatility` / `make test-cloudtainer-shadow-pass-volatility`
- turned the latest shadow-pass timing history into an explicit trust map so inheritors can distinguish stable budget anchors from jittery soft estimates instead of treating every frontier number as equally precise

## 2026-03-23 — Budget-aware shadow-pass commands

- added budget-aware cloudtainer shadow-pass commands: `make cloudtainer-shadow-pass-list-budgets`, `make cloudtainer-shadow-pass-short`, `make cloudtainer-shadow-pass-medium`, `make cloudtainer-shadow-pass-long`, plus `make test-cloudtainer-shadow-pass-budget-profiles`, so inheritors can intentionally stop at the good frontier cutpoints instead of only reacting after wrapper interruption
- `scripts/tools/cloudtainer_shadow_pass.py` now resolves `--budget-profile` labels from `artifacts/reports/cloudtainer_shadow_pass_frontier.json`, lists known profiles, rejects conflicting stop options, and leaves the same resumable checkpoint path the resume command already knows how to continue
- extended `scripts/report/build_cloudtainer_shadow_pass_frontier.py` so the generated frontier doc/report carry the exact short/medium/long command names alongside the existing timing plateaus

## 2026-03-23 — Cloudtainer shadow-pass budgeting frontier

- Added `scripts/report/build_cloudtainer_shadow_pass_frontier.py`, generated `docs/CLOUDTAINER_SHADOW_PASS_FRONTIER.md` plus `artifacts/reports/cloudtainer_shadow_pass_frontier.json`, and wired `make update-cloudtainer-shadow-pass-frontier` / `make test-cloudtainer-shadow-pass-frontier`.
- Quantified the best blocked-session budgeting prefixes from the fresh resumable shadow-pass receipt so future inheritors can stop intentionally before relying on checkpoint/resume.

- added checkpointed/resumable `make cloudtainer-shadow-pass` support, plus `make cloudtainer-shadow-pass-resume` and `make test-cloudtainer-shadow-pass-resume`, so sandbox-wrapper interruptions stop erasing completed blocked-session work before the final receipt lands
- `scripts/tools/cloudtainer_shadow_pass.py` now emits heartbeat lines during quiet steps, writes `artifacts/process/cloudtainer_shadow_pass_checkpoint.json` after every completed step, supports `--resume` / `--step-ids` / `--stop-after-step`, and upgrades final receipts to `receipt_version=2` with explicit checkpoint metadata
- added `scripts/report/build_rust_patch_prefix_frontier.py`, generated `docs/RUST_PATCH_PREFIX_FRONTIER.md` plus `artifacts/reports/rust_patch_prefix_frontier.json`, and wired new make targets plus the shadow pass around a quantified stopping-point frontier for the ordered Rust comeback shard series
- added `scripts/report/build_rust_external_test_patch_shards.py`, generated `docs/RUST_EXTERNAL_TEST_PATCH_SHARDS.md` plus `artifacts/reports/rust_external_test_patch_shards.json`, and emitted one ordered cumulative patch series under `artifacts/patches/rust_external_test_shards/*.patch` so the blocked-Rust comeback can land in smaller replayable chunks instead of one monolithic diff
- the new shard plan turns the rev0510 unified patch into `shard_count=10` cumulative apply steps, with the first 6 shards covering only `lift_first` bundles and the single dual-lane shard deferred to the final apply step
- threaded the new patch-shard lane into `Makefile`, `README.md`, `docs/README.md`, `docs/ENVIRONMENT_SANDWORM.md`, `scripts/test/check_generated_docs_presence.py`, and `scripts/tools/cloudtainer_shadow_pass.py` so the command surface and blocked-session regeneration path know how to refresh it

- added `scripts/report/build_rust_lift_bundle_plan.py`, generated `docs/RUST_LIFT_BUNDLE_PLAN.md` plus `artifacts/reports/rust_lift_bundle_plan.json`, and wired `make update-rust-lift-bundle-plan` / `make test-rust-lift-bundle-plan` so blocked-Rust sessions can collapse the 14-row external-test queue into shared fixture/code bundles
- the new bundle plan shows the comeback can stay smaller than the raw queue implies: `queue_entries=14`, `bundle_count=10`, `rows_saved_via_bundling=4`, with one dual-lane seed (`scaling_prefix_stability`) and three other multi-row probe bundles
- threaded the new bundle plan into `README.md`, `docs/README.md`, `docs/ENVIRONMENT_SANDWORM.md`, `scripts/test/check_generated_docs_presence.py`, and `scripts/tools/cloudtainer_shadow_pass.py` so the command surface, docs surface, and canonical blocked-session pass all know how to regenerate it

- added three tiny self-contained probe seeds — `examples/probes/fsm_grim_trigger_probe.json`, `examples/probes/memory_one_exit_after_break_probe.json`, and `examples/probes/scaling_prefix_stability_probe_seed.json` — so the last `example_seed_only` Rust rows are now directly liftable probe fixtures rather than strategy/metamorphic fragments
- regenerated `docs/RUST_GAP_WITNESS_QUEUE.md` + `artifacts/reports/rust_gap_witness_queue.json`, `docs/RUST_GAP_PROBE_SEED_INDEX.md` + `artifacts/reports/rust_gap_probe_seed_index.json`, and `docs/EXPERIMENT_CATALOG.md` + `artifacts/reports/experiment_catalog.json`; the new weak-gap summary is `probe_seed_ready=14`, `example_seed_only=0`
- tightened `scripts/report/build_rust_gap_witness_queue.py` so example witnesses prefer exact structured variant matches within each example tier, preventing `memory_one_exit` probe seeds from outranking exact `memory_one` witnesses by substring accident
- quieted the unittest commands inside `scripts/tools/cloudtainer_shadow_pass.py` so the canonical blocked-session pass is less likely to fail in this sandbox for log-volume reasons rather than real work failures

- added four tiny self-contained probe seed examples — `examples/probes/simple_standing_image_scoring_probe.json`, `examples/probes/simple_standing_standing_norm_probe.json`, `examples/probes/implementation_flip_probe.json`, and `examples/probes/mutual_defect_rate_guardrail_probe.json` — so the last source-only Rust scenario gaps now have liftable JSON anchors instead of only source mentions
- added `scripts/report/build_rust_gap_probe_seed_index.py`, generated `docs/RUST_GAP_PROBE_SEED_INDEX.md` plus `artifacts/reports/rust_gap_probe_seed_index.json`, and wired `make update-rust-gap-probe-seed-index` / `make test-rust-gap-probe-seed-index` so blocked sessions can see which weak rows already have self-contained `examples/probes/*.json` seeds
- tightened `make cloudtainer-shadow-pass` for the new seed-fixture lane by adding the probe-seed index refresh/check plus cheap example JSON and unique-id checks, and fixed the latter honestly by allowlisting the intentionally duplicated successor-safe placeholder/example id in `policy/examples_id_allowlist.json`
- local validation for this pass: examples JSON + unique-id checks, gap-witness queue regen/check, probe-seed index regen/check, README/docs/generated-docs/script checks, command/artifact inventory refresh, and the new weak-gap summary (`fixture_ready=14`, `source_ready=0`, `probe_seed_ready=11`)

- added `scripts/report/build_rust_gap_witness_queue.py`, generated `docs/RUST_GAP_WITNESS_QUEUE.md` plus `artifacts/reports/rust_gap_witness_queue.json`, and wired `make update-rust-gap-witness-queue` / `make test-rust-gap-witness-queue` so blocked-Rust sessions can recover exact fixture/source witnesses for the current coverage gaps instead of only a missing-variants list
- added `scripts/report/build_rust_test_contracts.py`, generated `docs/RUST_TEST_CONTRACTS.md` plus `artifacts/reports/rust_test_contracts.json`, and wired `make update-rust-test-contracts` / `make test-rust-test-contracts` so Rust-blocked sessions inherit a compact semantic-contract ledger rather than only a file map
- threaded the new contract ledger into `make cloudtainer-shadow-pass`, `README.md`, `docs/README.md`, `docs/ENVIRONMENT_SANDWORM.md`, and the generated-docs presence check so blocked sessions refresh it automatically
- hardened the canonical shadow pass for this sandbox by streaming step output and trimming nonessential inventory refreshes from the blocked-session loop, keeping the pass focused on Rust maps, command/artifact inventory, and productive Python checks

- added `scripts/tools/cloudtainer_shadow_pass.py` plus `make cloudtainer-shadow-pass`, so Rust-blocked sessions now have one canonical cheap local pass that records the tool boundary, refreshes compact inventories, reruns productive Python/doc checks, and emits one small process receipt instead of another ad hoc command list
- added inheritor-facing note `docs/LIBRARY/topics/rust_blocked_cloudtainer_sessions_should_ship_one_canonical_shadow_pass_command.md` and threaded the canonical shadow-pass command into `docs/ENVIRONMENT_SANDWORM.md`, `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`, `docs/BUCKET.md`, and the root command surface
- local validation for this pass: `make cloudtainer-shadow-pass` green with only the expected Rust-boundary block inside the doctor probe; inventory refreshes, docs/readme checks, control tests, GR Python certify tests, and script compile/executable checks are green

- added `scripts/report/build_rust_surface_inventory.py`, generated `docs/RUST_SURFACE_INVENTORY.md` plus `artifacts/reports/rust_surface_inventory.json`, and wired `make update-rust-surface-inventory` / `make test-rust-surface-inventory` so Rust-blocked sessions can recover the `gr_engine` source surface without `cargo`
- added inheritor-facing note `docs/LIBRARY/topics/rust_blocked_cloudtainer_sessions_should_shift_to_static_surface_mapping_and_python_shadow_work.md`, added compact process note `artifacts/process/2026-03-22-rust-blocked-shadow-work-pass.md`, extended `docs/RESEARCH_SOURCES.md` through `RS-OPS-010`, and threaded the blocked-toolchain workflow into the environment, agenda, opinions, backlog, and inheritor brief
- local validation for this pass: `doctor` / `test-quick` still stop only at missing `cargo` / `junest`; rust-surface inventory, command/artifact inventory refresh, docs/index/readme checks, control tests, and GR Python certify tests are green

- extended `scripts/tools/successor_safe_ceremony_receipt.py` with a new `review` subcommand, added `schemas/successor_safe_ceremony_receipt_review_verdict.schema.json`, and checked the worked freshness snapshot in `examples/snapshots/successor_safe_ceremony_receipt_example.review_verdict.json`
- added inheritor-facing note `docs/LIBRARY/topics/successor_safe_ceremony_receipt_review_watches_should_collapse_to_explicit_review_verdicts.md`, added `RS-GR-524` and `RS-GR-525`, and threaded the review-verdict discipline into the inheritor brief, research agenda, opinions, backlog, and research pass
- local validation for this pass: receipt+locator+assessment+disposition+remediation+authorization+promotion+review-watch+review-verdict checker, schema/docs/link checks, schema/validator/command/artifact inventories, control tests, GR Python certify tests; `doctor` / harness still stop only at missing `cargo` / `junest`

- extended `scripts/tools/successor_safe_ceremony_receipt.py` with a new `watch` subcommand, added `schemas/successor_safe_ceremony_receipt_review_watch.schema.json`, and checked the worked freshness snapshot in `examples/snapshots/successor_safe_ceremony_receipt_example.review_watch.json`
- added inheritor-facing note `docs/LIBRARY/topics/successor_safe_ceremony_receipt_authorizations_should_ship_compact_review_watches.md`, added `RS-GR-522` and `RS-GR-523`, and threaded the review-watch discipline into the inheritor brief, research agenda, opinions, backlog, and research pass
- added a compact promotion-record companion for successor-safe ceremony receipt packages so the archive can prove why a once-weak package became claim-ready instead of preserving only the latest green authorization
- extended `scripts/tools/successor_safe_ceremony_receipt.py` with a new `promote` subcommand, added `schemas/successor_safe_ceremony_receipt_promotion.schema.json`, committed `examples/snapshots/successor_safe_ceremony_receipt_placeholder.json`, and checked the worked promotion snapshot in `examples/snapshots/successor_safe_ceremony_receipt_example.promotion.json`
- added inheritor-facing note `docs/LIBRARY/topics/successor_safe_ceremony_receipt_authorizations_should_ship_compact_promotion_records.md`, added `RS-GR-520` and `RS-GR-521`, and threaded the promotion discipline into the inheritor brief, research agenda, opinions, and backlog
- local validation for this pass: receipt+locator+assessment+disposition+remediation+authorization+promotion checker, schema/docs/link checks, schema/validator/command/artifact inventories, control tests, GR Python certify tests; `doctor` / harness still stop only at missing `cargo` / `junest`

- extended `scripts/tools/successor_safe_ceremony_receipt.py` with a new `authorize` subcommand, added `schemas/successor_safe_ceremony_receipt_authorization.schema.json`, and checked the worked authorization snapshot in `examples/snapshots/successor_safe_ceremony_receipt_example.authorization.json`
- added inheritor-facing note `docs/LIBRARY/topics/successor_safe_ceremony_receipt_remediation_plans_should_end_in_explicit_authorization_decisions.md`, added `RS-GR-518` and `RS-GR-519`, and threaded the authorization discipline into the inheritor brief, research agenda, opinions, and backlog
- added a compact remediation-plan companion for successor-safe ceremony receipts so warned or failed dispositions now collapse into explicit closure goals, evidence paths, and promotion gates rather than generic follow-up prose
- extended `scripts/tools/successor_safe_ceremony_receipt.py` with a new `remediation` subcommand, added `schemas/successor_safe_ceremony_receipt_remediation_plan.schema.json`, and checked the worked remediation snapshot in `examples/snapshots/successor_safe_ceremony_receipt_example.remediation.json`
- added inheritor-facing note `docs/LIBRARY/topics/successor_safe_ceremony_receipt_dispositions_should_collapse_further_to_compact_remediation_plans.md`, added `RS-GR-516` and `RS-GR-517`, and threaded the remediation discipline into the inheritor brief, research agenda, opinions, and backlog
- local validation for this pass: receipt+locator+assessment+disposition+remediation checker, schema/docs/link checks, schema/validator/command/artifact inventories, control tests, GR Python certify tests; `doctor` / harness still stop only at missing `cargo` / `junest`
- added a compact archive-disposition companion for successor-safe ceremony receipts so assessments now collapse into explicit claim-ready / provisional / hold guidance rather than floating as unlabeled warnings
- extended `scripts/tools/successor_safe_ceremony_receipt.py` with a new `disposition` subcommand, added `schemas/successor_safe_ceremony_receipt_disposition.schema.json`, and checked the worked disposition snapshot in `examples/snapshots/successor_safe_ceremony_receipt_example.disposition.json`
- added inheritor-facing note `docs/LIBRARY/topics/successor_safe_ceremony_receipt_assessments_should_collapse_to_explicit_archive_dispositions.md`, added `RS-GR-514` and `RS-GR-515`, and threaded the disposition discipline into the inheritor brief, research agenda, opinions, and backlog
- local validation for this pass: receipt+locator+assessment+disposition checker, schema/docs/link checks, schema/validator/command/artifact inventories, control tests, GR Python certify tests; `doctor` / harness still stop only at missing `cargo` / `junest`
- added a compact fail-closed assessment companion for successor-safe ceremony receipts so the archive can distinguish structurally valid receipts from inheritor-ready receipts without re-reading standards prose
- extended `scripts/tools/successor_safe_ceremony_receipt.py` with a new `assess` subcommand, added `schemas/successor_safe_ceremony_receipt_assessment.schema.json`, and checked the worked assessment snapshot in `examples/snapshots/successor_safe_ceremony_receipt_example.assessment.json`
- added inheritor-facing note `docs/LIBRARY/topics/structurally_valid_successor_safe_ceremony_receipts_should_also_ship_a_fail_closed_assessment_report.md`, added `RS-GR-511` through `RS-GR-513`, and threaded the assessment discipline into the research agenda, opinions, and backlog
## rev0479 - 2026-03-22

- added a compact content-addressed locator companion for successor-safe ceremony receipts: a restricted-canonicalization profile, SHA-256 digest, and `ni:///sha-256;...` handle so downstream notes can cite stable ceremony handles instead of re-copying receipt bodies
- extended `scripts/tools/successor_safe_ceremony_receipt.py` with receipt validation during render plus a new `locate` subcommand, added `schemas/successor_safe_ceremony_receipt_locator.schema.json`, and checked the worked locator snapshot in `examples/snapshots/successor_safe_ceremony_receipt_example.locator.json`
- added inheritor-facing note `docs/LIBRARY/topics/content_addressed_successor_safe_ceremony_receipt_locators_keep_archive_handoffs_small_and_stable.md`, added `RS-GR-509` and `RS-GR-510`, and threaded the locator discipline into the inheritor brief and research agenda
- local validation for this pass: receipt+locator checker, schema/docs/link checks, schema/validator/command/artifact inventories, control tests, GR Python certify tests; `doctor` / harness still stop only at missing `cargo` / `junest`

## rev0427 - 2026-03-22

- added compact Golden Rule research notes on triadic small-group structure and on delegated coordination / coalition-stage / representative-selection contracts
- extended the research source ledger through `RS-GR-194` and threaded the new small-group / delegation constraints into the agenda, opinions, inheritor brief, and process pass
- added a compact receipt for the new tranche at `artifacts/process/triadic_and_delegated_coordination_receipt_20260322.json`

## rev0424 - 2026-03-22

- added compact Golden Rule research notes on concurrent-relationship portfolios and on cross-game linkage / crosstalk semantics
- extended the research source ledger through `RS-GR-182` and threaded the new concurrency constraints into the agenda, opinions, inheritor brief, and process pass
- added a compact receipt for the new tranche at `artifacts/process/concurrent_portfolio_and_crosstalk_receipt_20260322.json`

## rev0423 - 2026-03-22

- added compact Golden Rule research notes on shared-shock / risk-pooling structure and on formal-insurance / informal-solidarity fallback semantics
- extended the research source ledger through `RS-GR-179` and threaded the new risk / fallback constraints into the agenda, opinions, inheritor brief, and process pass
- added a compact receipt for the new tranche at `artifacts/process/risk_structure_and_fallback_contracts_receipt_20260321.json`

## rev0420 - 2026-03-21

- added compact Golden Rule research notes on inequality source / capability alignment and scarce-allocation / planner-authority contracts
- extended the research source ledger through `RS-GR-165` and threaded the new scarcity / inequality constraints into the agenda, opinions, inheritor brief, and process pass
- added a compact receipt for the new tranche at `artifacts/process/inequality_and_scarcity_contracts_receipt_20260321.json`

## 2026-03-21 (rev0411)

- added two compact research notes tightening the post-rematch design target: one on partner choice rewarding visible reciprocity while eroding hidden partner-maintenance help, and one on private-reputation worlds needing an explicit assessment-update rule.
- extended `docs/RESEARCH_SOURCES.md` with `RS-GR-134` and `RS-GR-135`, then threaded those constraints into the active agenda / opinions / inheritor brief so future sessions measure observable help separately from hidden care and publish the reputation update rule explicitly.

## 2026-03-21 (rev0410)

- re-read the retained extortion / anti-extortion artifacts into one compact inheritor receipt (`artifacts/process/extortion_frontier_reread_20260321.json`), which now states explicitly that short-horizon payoff wins fail to survive the long lane and that the current top `memory_one_exit` score is still a 4-round fixed-dyad artifact rather than partner choice.
- added two compact research notes for the next implementor: one on noisy voluntary repeated PD replacing retaliatory sanctioning with leave-based sanctioning, and one on move-order / action-visibility as a first-class world contract in repeated games.
- extended `docs/RESEARCH_SOURCES.md` with `RS-GR-132` and `RS-GR-133`, then threaded those constraints into the active agenda / opinions / inheritor brief so the next tranche is pushed toward institution-building before broader search.

## 2026-03-21 (rev0399)

- compact-card next-action witness and next-action surfaces now publish the first fallback target's direct typed semantic counts: `selected_fallback_command_target_citation_entry_count`, `selected_fallback_command_target_citation_lineage_count`, `selected_fallback_command_target_unresolved_lineage_count`, plus `primary_action.fallback_target_citation_entry_count`, `primary_action.fallback_target_citation_lineage_count`, and `primary_action.fallback_target_unresolved_lineage_count`.
- added doctrine for fallback-target semantic counts and refreshed the compact-card scope boundary so recovery-step logical scale is locally legible in both JSON and markdown without reopening retained report JSON or parsing prose scale summaries.

## 2026-03-21 (rev0398)

- Added one tiny `./grpy` wrapper that runs archive-local Python commands with `PYTHONDONTWRITEBYTECODE=1`, then rewired the compact-card verify / refresh / fallback / entrypoint command surfaces to cite `./grpy` instead of bare `python3`, so the inheritor can follow the surfaced command ladder without re-seeding adjacent `__pycache__` drift.
- Refreshed the compact-card control-plane, execution-lanes, handoff-pack, scope-surface, next-action-witness, and next-action outputs plus their validators under the wrapper-guided command surface.
- Rebuilt the archive size profile and the package / hotspot / semantic-handle / candidate / gap / manifest / rehearsal / stage / execution receipts on the pycache-neutral tree.
- Re-relaxed the historical compaction execution receipt so it validates as a citation-worthy history proof on today's larger tree by checking live-manifest displacement plus accounting coherence instead of requiring the current archive to stay smaller forever.

## rev0397 - 2026-03-21

- compact-card next-action witness and next-action surfaces now publish direct first-fallback target audit witnesses: `selected_fallback_command_target_bytes`, `selected_fallback_command_target_sha256`, `selected_fallback_command_target_scale_summary`, plus `primary_action.fallback_target_bytes`, `primary_action.fallback_target_sha256`, and `primary_action.fallback_target_scale_summary`.
- added doctrine for selected fallback target audit fields and refreshed the compact-card scope boundary so the first honest recovery step stays locally auditable without reopening retained report JSON or scanning report bindings.

## rev0396 - 2026-03-21

- restore honesty in the archive-size control stack by refreshing the package / hotspot / semantic-handle / candidate / gap / manifest / rehearsal / stage receipts on the live frontier instead of assuming the report bucket is permanently empty.
- add one compact durable handle note for `cooperation_benchmark_card_scope_surface` and `cooperation_benchmark_card_taxonomy`, which collapses the live second-pass handle gap back to zero and turns both large governance reports into citation-ready future trim candidates.
- relax the archive-size receipt validators so they check structural coherence of the current frontier rather than hard-coding a terminal-empty state; the historical execution receipt remains validated as history instead of being forced to replay against a different live tree.

## rev0395 - 2026-03-21

- compact-card next-action surfaces now publish a direct first-fallback command witness with target / subject / intent / outcome / effect semantics, so inheritors can recover from a failed preferred step without scanning fallback arrays or builder code.

## rev0394 - 2026-03-21

- publish direct selected-next-command target semantic counts on compact-card next-action witness / next-action surfaces: `selected_next_command_target_lineage_count`, `selected_next_command_target_review_item_count`, `selected_next_command_target_unresolved_lineage_count`, plus `primary_action.target_lineage_count`, `primary_action.target_review_item_count`, and `primary_action.target_unresolved_lineage_count`.
- add doctrine for selected-next-command target semantic counts and refresh scope / generated compact-card docs.

## rev0393 - 2026-03-21

- publish direct selected-next-command target audit fields on compact-card next-action witness / next-action surfaces: `selected_next_command_target_bytes`, `selected_next_command_target_sha256`, `selected_next_command_target_scale_summary`, plus `primary_action.target_bytes`, `primary_action.target_sha256`, and `primary_action.target_scale_summary`.
- add doctrine for selected-next-command target audit fields and refresh scope / generated compact-card docs.

## 2026-03-21 (rev0392)
- compact-card next-action witnesses now publish direct selected-next-command target and semantics witnesses: `selected_next_command_target`, `selected_next_command_subject_role_code`, `selected_next_command_intent_summary`, `selected_next_command_outcome_summary`, and `selected_next_command_effect_code`.
- compact-card next-action surfaces now thread the same direct semantics into `primary_action.target`, `primary_action.subject_role_code`, `primary_action.intent_summary`, `primary_action.outcome_summary`, and `primary_action.effect_code`, so the chosen command is locally legible without re-deriving hidden command semantics.

## 2026-03-21 (rev0391)
- compact-card handoff packs now publish the remaining typed semantic counts behind the first verify / refresh target scale summaries: `primary_verify_target_citation_lineage_count`, `primary_verify_target_unresolved_lineage_count`, `primary_refresh_target_verified_delta_receipt_count`, and `primary_refresh_target_latest_known_card_count`.
- compact-card control-plane / next-action-witness / next-action surfaces now lift the same values as `focus_primary_verify_target_citation_lineage_count`, `focus_primary_verify_target_unresolved_lineage_count`, `focus_primary_refresh_target_verified_delta_receipt_count`, and `focus_primary_refresh_target_latest_known_card_count`, so tools do not need to parse prose scale summaries or reopen report JSON.

## rev0390 - 2026-03-21

- compact-card handoff packs now publish direct `primary_verify_target_scale_summary` and `primary_refresh_target_scale_summary` witnesses so inheritors can read the first machine-target scale without opening report JSON or combining multiple counts by hand.
- compact-card control-plane / next-action-witness / next-action surfaces now lift the same summaries as `focus_primary_verify_target_scale_summary` and `focus_primary_refresh_target_scale_summary`.
- refreshed schemas, validators, scope surface, generated reports/docs, and doctrine notes for the new target-scale summary witnesses.

# Changelog

- compact-card handoff packs now publish direct `primary_verify_target_citation_entry_count` and `primary_refresh_target_card_count` witnesses so inheritors do not have to open the retained report JSON just to tell the logical scale of the first machine targets
- compact-card control-plane, next-action-witness, and next-action surfaces now publish matching `focus_primary_verify_target_citation_entry_count` and `focus_primary_refresh_target_card_count` witnesses, lifted from the chosen focus lineage handoff pack

- compact-card handoff packs now publish direct `primary_verify_target_sha256` and `primary_refresh_target_sha256` witnesses so inheritors do not have to scan the retained file manifest just to confirm the exact identity of the first machine targets
- compact-card control-plane, next-action-witness, and next-action surfaces now publish matching `focus_primary_verify_target_sha256` and `focus_primary_refresh_target_sha256` witnesses, lifted from the chosen focus lineage handoff pack

- compact-card handoff packs now publish direct `primary_verify_target_bytes` and `primary_refresh_target_bytes` witnesses so inheritors do not have to scan the retained file manifest just to size the first machine targets
- compact-card control-plane, next-action-witness, and next-action surfaces now publish matching `focus_primary_verify_target_bytes` and `focus_primary_refresh_target_bytes` witnesses, lifted from the chosen focus lineage handoff pack
- tightened validators so the new byte-count witnesses remain honest aliases of retained report-manifest bytes rather than a second machine-target semantics

## rev0386 - 2026-03-21

- compact-card handoff packs now publish direct `primary_verify_effect_code` and `primary_refresh_effect_code` witnesses so inheritors do not have to infer whether the first verify / refresh commands are read-only or state-changing from command spelling alone
- compact-card control-plane, next-action-witness, and next-action surfaces now publish matching `focus_primary_verify_effect_code` and `focus_primary_refresh_effect_code` witnesses, lifted from the chosen focus lineage handoff pack
- governed the new command effect vocabulary in compact-card taxonomy and refreshed the human-readable reentry docs so the first step posture is visible in markdown as well as JSON

## rev0385 - 2026-03-21

- compact-card handoff packs now publish direct `primary_verify_outcome_summary` and `primary_refresh_outcome_summary` witnesses so inheritors do not have to infer the expected immediate result of the first verify / refresh commands from validator names plus target types
- compact-card control-plane, next-action-witness, and next-action surfaces now publish matching `focus_primary_verify_outcome_summary` and `focus_primary_refresh_outcome_summary` witnesses, lifted from the chosen focus lineage handoff pack
- refreshed the human-readable compact-card docs so the first verify / refresh subject, intent, and expected outcome are visible in markdown as well as JSON

## rev0384 - 2026-03-21

- compact-card handoff packs now publish direct `primary_verify_intent_summary` and `primary_refresh_intent_summary` witnesses so inheritors do not have to reconstruct the one-line purpose of the first verify / refresh commands from script names plus role codes
- compact-card control-plane, next-action-witness, and next-action surfaces now publish matching `focus_primary_verify_intent_summary` and `focus_primary_refresh_intent_summary` witnesses, lifted from the chosen focus lineage handoff pack
- tightened validators so the new intent summaries remain honest aliases of the retained command subjects rather than a second command-selection semantics

## rev0383 - 2026-03-21

- compact-card handoff packs now publish direct `primary_verify_subject_role_code` and `primary_refresh_subject_role_code` witnesses so inheritors do not have to scan target role arrays just to recover the main subject of the first verify / refresh commands
- compact-card control-plane, next-action-witness, and next-action surfaces now publish matching `focus_primary_verify_subject_role_code` and `focus_primary_refresh_subject_role_code` witnesses, lifted from the chosen focus lineage handoff pack
- tightened validators so the new subject-role witnesses remain honest aliases of the retained command-target roles rather than a second command semantics

## rev0382 - 2026-03-21

- compact-card handoff packs now publish direct role-annotated `primary_verify_target` and `primary_refresh_target` witnesses so inheritors can tell what the first verify / refresh commands act on without reverse-engineering script names
- compact-card control-plane, next-action-witness, and next-action surfaces now publish matching `focus_primary_verify_target` and `focus_primary_refresh_target` witnesses, lifted from the chosen focus lineage handoff pack
- governed the new command-target role vocabulary in compact-card taxonomy and tightened validators so the targets stay honest aliases of retained report paths

## rev0381 - 2026-03-21

- compact-card control-plane, next-action-witness, and next-action surfaces now publish direct `focus_primary_verify_command` and `focus_primary_refresh_command` witnesses, lifted from the chosen focus lineage's handoff pack so inheritors do not have to hop into the pack just to recover the canonical first local check / rebuild step
- updated control-plane / witness / next-action builders, schemas, validators, scope surface, and compact-card doctrine accordingly

## rev0380 - 2026-03-21

- compact-card handoff packs now publish direct `primary_verify_command` and `primary_refresh_command` witnesses so inheritors do not have to scan command arrays to recover the canonical first local check / rebuild step
- updated handoff-pack builder, schema, validator, scope surface, and compact-card doctrine accordingly

## rev0379 - 2026-03-21

- compact-card reentry surfaces now publish a direct role-annotated `focus_primary_open_target`, so inheritors do not have to scan `focus_open_targets` just to recover the canonical first-open object.
- compact-card handoff packs now publish a matching `primary_open_target`, and validators require both direct witnesses to equal the first item of their corresponding ordered target families.


## rev0378 - 2026-03-21

- cooperation-benchmark-card handoff packs now publish a tiny role-annotated `entry_targets` family, making lineage-local first-open files self-explanatory inside the pack itself.
- governed the new handoff-pack target role vocabulary in the compact-card taxonomy and tightened handoff-pack validation so the target family must stay ordered, unique, and grounded in retained pack paths.


## rev0377 - 2026-03-21

- publish `citation_head_card_path`, `operational_head_card_path`, and `primary_open_path` in compact-card handoff packs so lineage-local reentry does not require a second cross-reference through heads or control-plane surfaces;
- reorder handoff-pack `must_read_paths` so the program doctrine comes first and the lineage-local primary-open path comes immediately after it;
- tighten handoff-pack validation to require that the published head/open paths are present in the retained pack manifest and aligned with the must-read order.

## 2026-03-21 — Research Pass (Role-Annotated Focus Targets + Companion Path Semantics)

- Extended the compact-card reentry digest with `focus_open_targets`, a tiny ordered family of retained focus-lineage paths plus deduplicated `role_codes`, so inheritors can tell why each file belongs in the first-inspection ladder instead of inferring it from suffixes or builder code.
- Threaded `focus_open_targets` through `cooperation_benchmark_card_control_plane`, `cooperation_benchmark_card_next_action_witness`, and `cooperation_benchmark_card_next_action`, keeping the new semantics local to the top-level reentry surfaces rather than widening every candidate row.
- Extended the compact-card taxonomy with stable `focus_open_target_role_codes`, tightened validators so target paths exactly match `focus_open_paths`, and added doctrine via `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_role_annotated_focus_open_targets_for_compact_card_reentry.md`.

## 2026-03-21 — Research Pass (Ordered Focus Open Paths + Companion Reentry Sequence)

- Extended the compact-card control-plane reentry digest with a small ordered `focus_open_paths` family, so inheritors now get not just the first file to open but the tiny deduplicated sequence of companion retained files that usually matter next.
- Threaded `focus_open_paths` through `cooperation_benchmark_card_control_plane`, `cooperation_benchmark_card_next_action_witness`, and `cooperation_benchmark_card_next_action`, keeping the new field local to the top-level reentry surfaces rather than duplicating it across every candidate row.
- Added `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_ordered_focus_open_paths_for_compact_card_reentry.md`, extended `docs/BENCHMARK_PROGRAM.md`, and refreshed the compact-card scope boundary so the new doctrine remains part of the subsystem contract.
- Tightened the control-plane / witness / next-action validators so `focus_open_paths` must stay ordered, unique, derived from retained focus-lineage artifacts, and locally existent.

## 2026-03-21 — Research Pass (Compact-Card Focus Lineage + Deterministic Reentry Digest)

- Added one tiny deterministic focus-lineage digest to the compact-card reentry stack so inheritors can see which lineage to inspect first even when the overall control plane is already `ready`.
- Extended `cooperation_benchmark_card_control_plane`, `cooperation_benchmark_card_next_action_witness`, and `cooperation_benchmark_card_next_action` with `focus_selector_kind`, `focus_lineage_id`, and `focus_summary`; the control plane also now publishes the focused lineage's operational and citation heads.
- Added `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_a_deterministic_focus_lineage_for_compact_card_reentry.md`, extended `docs/BENCHMARK_PROGRAM.md`, and added `RS-GR-131` so the reentry doctrine explicitly treats summarized first-inspection targets as a provenance/use concern rather than as session folklore.
- Refreshed the compact-card scope surface, control plane, next-action witness, and next-action outputs plus their validators, and kept the archive package-ready and pycache-free after the change.

## 2026-03-20 — Research Pass (Transient Edge Counts + Pre-Closure Mechanism Lane)

- Extended `grlab certify` so `transition_graph_diagnostics` now publishes exact `expected_transition_counts_before_any_closed_class_entry_from_initial_distribution`, making the pre-closure edge mechanism from the declared opening distribution explicit rather than left implicit behind visit counts and cumulative payoff burden alone.
- Extended each `closed_class_entry_probabilities_from_initial_distribution` item with `conditional_expected_transition_counts_before_entry_from_initial_distribution`, so future inheritors can see which transitions actually carry the path burden conditional on entering each recurrent basin.
- Bumped the top-level typed certify result to `schema_version = 21` while leaving `anti_vampire_scorecard.scorecard_version = 13` unchanged, because this pass sharpens the graph/transient diagnostics without changing the scorecard contract itself.
- Tightened solver / CLI / schema / formal invariant coverage around the new transition-count surface, including the split-opening reducible case where the exact long-run mixture remains `0.5 * CC + 0.5 * DD` but the transient mechanism is now declared directly as `CD -> CC` on the way to `CC` and `DC -> DD` on the way to `DD`.

## 2026-03-20 — Research Pass (Transient Visit Counts + Pre-Closure Path Shape Lane)

- Extended `grlab certify` so `transition_graph_diagnostics` now publishes exact `expected_visit_counts_before_any_closed_class_entry_from_initial_distribution`, making the transient state-occupancy shape from the declared opening distribution explicit rather than left implicit behind entry timing and cumulative payoff burden alone.
- Extended each `closed_class_entry_probabilities_from_initial_distribution` item with `conditional_expected_visit_counts_before_entry_from_initial_distribution`, so future inheritors can see which off-diagonal states actually carry the path burden conditional on entering each recurrent basin.
- Bumped the top-level typed certify result to `schema_version = 20` while leaving `anti_vampire_scorecard.scorecard_version = 13` unchanged, because this pass sharpens the graph/transient diagnostics without changing the scorecard contract itself.
- Tightened solver / CLI / schema / formal invariant coverage around the new visit-count surface, including the split-opening reducible case where the exact long-run mixture remains `0.5 * CC + 0.5 * DD` but the transient path shape is concentrated in `CD` on the way to `CC` and in `DC` on the way to `DD`.

## 2026-03-20 — Research Pass (Transient Payoff Surface + Pre-Closure Burden Lane)

- Extended `grlab certify` so `transition_graph_diagnostics` now publishes exact `expected_cumulative_payoff_a_before_any_closed_class_entry_from_initial_distribution` / `expected_cumulative_payoff_b_before_any_closed_class_entry_from_initial_distribution`, making the transient incentive burden from the declared opening distribution explicit rather than left implicit behind entry timing and asymptotic mixture alone.
- Extended each `closed_class_entry_probabilities_from_initial_distribution` item with `conditional_expected_cumulative_payoff_a_before_entry_from_initial_distribution` / `conditional_expected_cumulative_payoff_b_before_entry_from_initial_distribution`, so future inheritors can see which side pays the path cost conditional on entering each recurrent basin.
- Bumped the top-level typed certify result to `schema_version = 19` while leaving `anti_vampire_scorecard.scorecard_version = 13` unchanged, because this pass sharpens the graph/transient diagnostics without changing the scorecard contract itself.
- Tightened solver / CLI / schema / formal invariant coverage around the new pre-closure payoff surface, including the split-opening reducible case where the exact long-run mixture stays symmetric at `0.5 * CC + 0.5 * DD` while the basin-conditional transient burden is sharply asymmetric (`CC`: A `0.0`, B `2.5`; `DD`: A `2.5`, B `0.0`).

## 2026-03-20 — Research Pass (Closed-Class Entry Timing + Transient Horizon Surface)

- Extended `grlab certify` so `transition_graph_diagnostics` now publishes an exact `expected_steps_to_any_closed_class_from_initial_distribution`, making the transient horizon from the declared opening distribution explicit rather than left implicit behind the basin weights alone.
- Extended each `closed_class_entry_probabilities_from_initial_distribution` item with `conditional_expected_entry_steps_from_initial_distribution`, so future inheritors can see not just which basin gets mass but how long entry into that basin typically takes conditional on getting there.
- Bumped the top-level typed certify result to `schema_version = 18` while leaving `anti_vampire_scorecard.scorecard_version = 13` unchanged, because this pass sharpens the graph/transient diagnostics without changing the scorecard contract itself.
- Tightened solver / CLI / schema / formal invariant coverage around the new timing surface, including the split-opening reducible case where half the opening mass is already recurrent and the exact transient horizon is therefore `0.5` steps rather than a hand-inferred narrative.

## 2026-03-20 — Research Pass (Exact Asymptotic Surface + Cesàro Drift Witness)

- Extended `grlab certify` with a top-level exact `asymptotic_distribution_from_initial_distribution` derived from the declared closed-class decomposition, plus explicit `asymptotic_avg_payoff_a_from_initial_distribution` / `asymptotic_avg_payoff_b_from_initial_distribution` so reducible-chain long-run outcomes no longer have to be reconstructed by hand.
- Added `asymptotic_distribution_method = closed_class_exact_mixture_from_initial_distribution` and a compact `steady_state_distribution_l1_distance_to_asymptotic_distribution` witness so future inheritors can see directly whether the retained top-level `steady_state_distribution` is already exact or is only a finite Cesàro approximation.
- Bumped the top-level typed certify result to `schema_version = 17` while leaving `anti_vampire_scorecard.scorecard_version = 13` unchanged, because this pass sharpens the top-level asymptotic reading without changing the scorecard contract itself.
- Tightened solver / CLI / schema / formal invariant coverage around the new exact asymptotic surface, including the split-opening reducible case where the exact asymptotic mixture is `0.5 * CC + 0.5 * DD` and the new L1 witness exposes the residual gap to the retained finite fallback vector.

## 2026-03-20 — Research Pass (Closed-Class Asymptotic Decomposition + Basin Outcome Surface)

- Extended `grlab certify` so `transition_graph_diagnostics` now publishes `closed_class_asymptotic_decomposition_from_initial_distribution`, turning each recurrent basin into an explicit long-run outcome object rather than leaving future sessions to reconstruct basin payoffs from the kernel by hand.
- Each decomposition item now carries the basin label, exact opening-distribution `entry_probability`, the basin-local `class_stationary_distribution`, its `weighted_steady_state_contribution` to the declared overall asymptotic distribution, and basin-conditioned `class_avg_payoff_a` / `class_avg_payoff_b`.
- Bumped the top-level typed certify result to `schema_version = 16` while leaving `anti_vampire_scorecard.scorecard_version = 13` unchanged, because this pass sharpens the dynamic-diagnostics surface without changing the scorecard contract itself.
- Tightened solver / CLI / schema / formal invariant coverage around the new basin outcome surface, including the split-opening example that decomposes cleanly into the exact asymptotic mixture `0.5 * CC + 0.5 * DD`.

## 2026-03-20 — Research Pass (Closed-Class Entry Probabilities + Initial-Basin Weight Surface)

- Extended `grlab certify` so `transition_graph_diagnostics` now publishes exact `closed_class_entry_probabilities_from_initial_distribution`, computed from the declared 4×4 kernel and opening distribution rather than left implicit behind graph reachability alone.
- Added `multiple_closed_classes_with_positive_entry_probability_from_initial_distribution` so future inheritors can distinguish “the chain has several recurrent basins” from “this declared opening distribution actually splits mass across several basins.”
- Bumped the top-level typed certify result to `schema_version = 15` while leaving `anti_vampire_scorecard.scorecard_version = 13` unchanged, because this pass sharpens the dynamic-diagnostics surface without changing the scorecard contract itself.
- Tightened solver / CLI / schema / formal invariant coverage with an explicit mixed-opening example that splits `0.5 / 0.5` across `CC` and `DD`, plus a reducible-chain check that keeps an unreachable recurrent basin visible but correctly weighted at `0.0`.

## 2026-03-20 — Research Pass (Transition-Kernel Contract + Explicit 4x4 Kernel Surface)

- Extended `grlab certify` so typed results now declare `transition_kernel_contract_ref` at both the top level and inside `anti_vampire_scorecard`, making the exact memory-one kernel construction rule explicit rather than silently living in Python.
- Added a compact top-level `transition_matrix` surface so inheritors can inspect the actual 4×4 row-stochastic kernel used for steady-state, recovery, and payoff calculations without reverse-engineering it from strategy parameters.
- Bound a canonical immutable transition-kernel contract (`memory_one_state_product_kernel_v1`) covering the declared state order, row-stochastic orientation, the per-row product formulas, and the fact that strategy B's conditional indices are mirrored into A-view before the kernel is built.
- Tightened `pairing_ref.pairing_fingerprint_sha256` so ordered certify-object identity now depends on the transition-kernel contract in addition to the screening spec, ordered strategies, stage game, sampling plans, interval semantics, proxy-measurement semantics, steady-state contract, and opening-distribution contract.
- Bumped the typed certify surfaces to `schema_version = 13` and `scorecard_version = 13`, refreshed `schemas/certify_memory_one_result.schema.json`, and extended solver / CLI / schema / formal invariant coverage accordingly.

## 2026-03-20 — Research Pass (Opening-Distribution Contract Ref + Initial-State Semantics Identity)

- Extended `grlab certify` so typed results now declare `opening_distribution_contract_ref` at both the top level and inside `anti_vampire_scorecard`, making the `p0`-to-state mapping behind the reported opening distribution explicit rather than silently living in Python.
- Bound a canonical immutable opening-distribution contract (`memory_one_independent_p0_product_v1`) covering the independent-Bernoulli opening-action assumption, the use of `strategy_a.p0` / `strategy_b.p0` as the cooperate probabilities, the declared `state_order`, and the exact product formulas for `CC`, `CD`, `DC`, and `DD`.
- Tightened `pairing_ref.pairing_fingerprint_sha256` so ordered certify-object identity now depends on the opening-distribution contract in addition to the screening spec, ordered strategies, stage game, sampling plans, interval semantics, proxy-measurement semantics, and steady-state contract.
- Bumped the typed certify surfaces to `schema_version = 12` and `scorecard_version = 12`, refreshed `schemas/certify_memory_one_result.schema.json`, and extended solver / CLI / schema / formal invariant coverage accordingly.
- Refreshed handoff docs and generated schema / artifact inventories after the new contract surface landed.

## 2026-03-20 — Research Pass (Steady-State Contract Ref + Solver/Fallback Semantics Identity)

- Extended `grlab certify` so typed results now declare `steady_state_contract_ref` at both the top level and inside `anti_vampire_scorecard`, making the solver / fallback semantics behind the reported pairwise payoffs explicit rather than silently living in Python.
- Bound a canonical immutable steady-state contract (`memory_one_stationary_or_cesaro_v1`) covering the exact stationary solve method, pivot tolerance, cleanup / negative-mass tolerances, singularity fallback trigger, and the fact that fallback steps come from `screening_spec.steady_state.cesaro_fallback_steps`.
- Tightened `pairing_ref.pairing_fingerprint_sha256` so ordered certify-object identity now depends on the steady-state contract in addition to the screening spec, ordered strategies, stage game, sampling plans, interval semantics, and proxy-measurement semantics.
- Bumped the typed certify surfaces to `schema_version = 11` and `scorecard_version = 11`, refreshed `schemas/certify_memory_one_result.schema.json`, and extended solver / CLI / schema / formal invariant coverage accordingly.
- Refreshed handoff docs and generated schema / artifact inventories after the new contract surface landed.

## 2026-03-20 — Research Pass (Proxy-Measurement Contract + Semantics Identity)

- Extended `grlab certify` with a declared `proxy_measurement_contract_ref` so the sign conventions, aggregation rules, and event semantics behind the anti-vampire proxy fields no longer live only in Python.
- Added a canonical immutable proxy-semantics contract id/fingerprint pair (`anti_vampire_proxy_measurement_v1`) and threaded it into both the top-level certify payload and `anti_vampire_scorecard`.
- Tightened `pairing_ref.pairing_fingerprint_sha256` so ordered certify-object identity now depends on the proxy-measurement semantics contract in addition to the ordered strategies, stage game, screening spec, sampling plans, and interval semantics.
- Bumped the certify typed surfaces to `schema_version = 10` and `scorecard_version = 10`, added schema coverage for the new ref, and extended solver / CLI / schema / formal invariant coverage accordingly.
- Refreshed handoff docs and generated schema / artifact inventories after the new contract surface landed.

## 2026-03-20 — Research Pass (Uncertainty Contract Ref + Interval Semantics Provenance)

- Added an immutable `uncertainty_contract_ref` to `grlab certify` at both the top level and inside the anti-vampire scorecard so retained results now declare the interval semantics behind the noisy proxy fields, not just the point estimates and sampling plans.
- Tightened `pairing_ref.pairing_fingerprint_sha256` so the ordered certify-object identity now depends on the declared uncertainty contract in addition to the screening spec, stage game, ordered strategy pair, and sampling-plan refs.
- Bumped the typed certify surfaces to `schema_version = 9` and `scorecard_version = 9`, refreshed the result schema, and extended solver / CLI / schema coverage for the new ref.

## 2026-03-20 — certify sampling-plan refs + seed-schedule provenance

- Extended `grlab certify` so the anti-vampire scorecard now publishes compact `ecology_sampling_ref` and `repair_sampling_ref` objects in addition to the existing threshold, uncertainty, strategy, stage-game, and screening-spec provenance.
- Each sampling ref now exposes a stable `sampling_plan_id`, declared `estimate_kind`, declared arithmetic-progression seed schedule (`seed_base`, `seed_stride`), and immutable `sampling_plan_fingerprint_sha256` computed over the effective rollout plan rather than only over the visible human label.
- Tightened `pairing_ref.pairing_fingerprint_sha256` so ordered certify-object identity now depends on the effective Monte Carlo sampling plans too, closing the next silent drift mode where the same strategies/spec could be rerun under a changed replicate schedule.
- Bumped the typed result / scorecard contracts to `schema_version = 8` and `scorecard_version = 8`, refreshed `schemas/certify_memory_one_result.schema.json`, and tightened solver / CLI / schema / formal coverage accordingly.
- Main local result: ecology-budget overrides now change both the effective screening-spec identity and the ecology sampling-plan fingerprint while leaving the repair sampling-plan fingerprint alone, which is exactly the compact provenance distinction the inheritor needs.


## 2026-03-20 — certify uncertainty-aware screening stability overlay

- Extended `grlab certify` so the anti-vampire `screening_contract` now distinguishes the **point-estimate gate** from the **stability of that gate under current uncertainty**.
- Added compact contract-level fields `binding_gate_status in {pass, fail, borderline}` and `gate_stability in {stable, borderline_sampling_uncertainty}`.
- Added per-check threshold decision surfaces: exact checks now report `threshold_decision_state = exact_pass/exact_fail`, the noisy-ecology binding check now reports `clear_pass`, `clear_fail`, or `borderline_ci95_crosses_threshold`, and the repair proxy check now declares `threshold_pending` while still publishing its Wilson interval.
- Bumped the typed result / scorecard contracts to `schema_version = 7` and `scorecard_version = 7`, refreshed `schemas/certify_memory_one_result.schema.json`, and tightened certify solver / CLI / schema coverage accordingly.
- Main local result: the canonical extortion lanes remain `stable` fails, but a deliberately tightened custom ecology threshold can now surface `gate_pass = true` together with `binding_gate_status = borderline`, which is the compact inheritor-facing distinction that was previously missing.


## 2026-03-20 — certify Monte Carlo uncertainty surface for proxy metrics

- Extended `grlab certify` so Monte Carlo anti-vampire proxy fields no longer masquerade as exact facts: the scorecard now publishes `ecology_gap_noisy_stderr`, `ecology_gap_noisy_ci95_half_width`, `ecology_own_payoff_stderr`, `ecology_own_payoff_ci95_half_width`, `repair_abuse_count`, and Wilson-style `repair_abuse_rate_ci95_low/high`.
- Added per-opponent ecology uncertainty maps (`ecology_gap_stderr_by_opponent`, `ecology_own_payoff_stderr_by_opponent`) plus `ecology_estimate_kind = replicated_rollout_mean` so future sessions can distinguish point estimates from rollout uncertainty without retaining bulky raw traces.
- Bumped the typed result / scorecard contracts to `schema_version = 6` and `scorecard_version = 6`, and refreshed `schemas/certify_memory_one_result.schema.json` accordingly.
- Tightened certify solver / CLI / schema coverage around the new uncertainty surface and kept the current gate semantics unchanged: the binding noisy-ecology decision is still taken on the declared point estimate, but the payload now exposes how sharp or noisy that estimate was.


## 2026-03-20 — certify stage-game ref + explicit state order

- Extended `grlab certify` so the result payload now declares `stage_game_ref` and `state_order` alongside the existing strategy/spec provenance.
- Tightened `pairing_ref.pairing_fingerprint_sha256` so the ordered certify-object identity now includes the declared stage-game contract in addition to the ordered strategy pair and effective screening spec.
- Added coverage for the new stage-game/state-order surface in `grlab/tests/test_certify_solver.py`, `grlab/tests/test_certify_cli.py`, and `grlab/tests/test_certify_schema.py`.
- Updated `schemas/certify_memory_one_result.schema.json`, `docs/LIBRARY/topics/anti_vampire_scorecard_spec.md`, and `docs/BUCKET.md` to keep the handoff doctrine aligned with the result surface.


## 2026-03-20 — Research Pass (Strategy Fingerprints + Pairing Identity)

- Extended `grlab certify` so typed results now publish immutable `strategy_a_ref` / `strategy_b_ref` objects alongside the existing human-readable `strategy_a` / `strategy_b` ids.
- Added stable `strategy_fingerprint_sha256` hashing over canonical memory-one strategy payloads, so a changed strategy file can no longer masquerade as the same certified object merely because it kept the same `id` string.
- Added ordered `pairing_ref.pairing_fingerprint_sha256`, derived from the effective screening contract plus the ordered strategy refs, so future sessions can tell whether two certify results came from the same scientific pairing surface without diffing whole payloads.
- Bumped `schemas/certify_memory_one_result.schema.json` to `schema_version = 4` and added schema-backed `strategyRef` / `pairingRef` definitions.
- Tightened certify solver / CLI / schema coverage so the archive now checks same-id/different-payload divergence and ordered-pair sensitivity explicitly.
- Main local result:
  - `python3 -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli grlab.tests.test_certify_schema` passes,
  - same `strategy_id` with changed memory-one probabilities now gets a different `strategy_fingerprint_sha256`,
  - and swapping the order of the same two strategies changes `pairing_fingerprint_sha256` as it should because `A vs B` and `B vs A` are not the same certify object.


## 2026-03-20 — Research Pass (Spec Fingerprint + Drift Guard)

- Extended `grlab certify` so `screening_spec_ref` now carries an immutable `spec_fingerprint_sha256` of the **effective normalized screening spec**, not just a human-readable `spec_id`.
- Normalized the screening-spec fingerprint surface so semantically identical contracts hash the same whether they came from the raw JSON example or the internal tuple-based runtime representation.
- Bumped the typed result / scorecard contracts to `schema_version = 3` and `scorecard_version = 5`, and refreshed `schemas/certify_memory_one_result.schema.json` accordingly.
- Tightened certify coverage so the archive now checks that the shipped canonical example `examples/certify/canonical_proxy_v1.json` matches `default_screening_spec()` exactly and that execution overrides like `--ecology-rounds` actually change the effective spec fingerprint.
- Main local result:
  - `python3 -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli grlab.tests.test_certify_schema` passes,
  - canonical raw/example/default specs now share one stable fingerprint,
  - and override-driven runs no longer masquerade as the same contract merely because they still say `spec_id = canonical_proxy_v1`.

## 2026-03-20 — Research Pass (Declared Screening Spec + Certify Provenance)

- Extended `grlab certify` so the anti-vampire proxy lane is now declared by a schema-backed screening spec instead of only by hidden Python constants.
- Added `schemas/certify_memory_one_screening_spec.schema.json` plus the shipped canonical proxy contract at `examples/certify/canonical_proxy_v1.json`.
- Extended the result contract so certify payloads now carry `screening_spec_ref` provenance and the scorecard records the declared `shock_protocol`; the payload schema is refreshed at `schemas/certify_memory_one_result.schema.json`.
- Added `--screening-spec` to `python3 -m grlab certify`, while keeping `--ecology-noise`, `--ecology-rounds`, and `--ecology-reps` as optional execution overrides on top of the declared spec.
- Refreshed the compact formal certify invariant lane so the retained invariant script now expects the post-Cesàro-fallback `TFT` vs `TFT` result instead of the pre-fallback singular-solve failure.
- Tightened certify coverage so both the default canonical spec and custom screening specs are exercised in solver / CLI / schema tests.
- Main local result:
  - `python3 -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli grlab.tests.test_certify_schema` passes,
  - canonical results now cite their screening contract directly via `screening_spec_ref = canonical_proxy_v1`,
  - and a deliberately lenient demo spec can flip `AlwaysC` vs extortion from fail to pass without touching code, proving the gate is now a declared contract rather than hidden module state.

## 2026-03-20 — Research Pass (Certify Screening Contract + Result Schema)

- Extended `grlab certify` so the anti-vampire proxy lane now emits an explicit `screening_contract` instead of leaving pass/fail interpretation implicit in raw metrics.
- The new contract publishes:
  - binding checks for `pairwise_fairness` and `noisy_ecology`,
  - advisory checks for `recovery_proxy` and `repair_proxy`,
  - active threshold values where the current proxy lane has them,
  - and stable `failure_reasons` / `advisory_reasons` for inheritor triage.
- Added a schema-backed contract for the full JSON payload at `schemas/certify_memory_one_result.schema.json`.
- Added targeted schema coverage in `grlab/tests/test_certify_schema.py` and tightened solver / CLI coverage for the new contract surface in `grlab/tests/test_certify_solver.py` and `grlab/tests/test_certify_cli.py`.
- Main local result:
  - exact-stationary and `cesaro_from_initial_distribution` certify payloads both validate against the new schema,
  - the current anti-extraction gate is now directly machine-checkable,
  - and the remaining recovery / repair open questions stay explicitly advisory instead of being buried in prose.

## 2026-03-20 — Research Pass (Memory-One Reducible-Chain Cesàro Fallback)

- Extended `grlab certify` so memory-one pair certification no longer aborts on reducible or multi-stationary four-state chains where the exact stationary linear solve is not unique.
- Added a compact fallback: when the exact stationary solve is singular or ill-conditioned, certification now computes a long-run Cesàro occupancy distribution from the declared `p0` opening probabilities instead of failing outright.
- Exposed the distribution semantics directly in the JSON result via `initial_distribution` and `steady_state_method`, so inheritors can tell whether a pair was certified by the exact stationary lane or the `p0`-anchored Cesàro fallback lane.
- Tightened certify coverage so the archive now exercises both lanes explicitly, including the previously failing `WSLS` vs `AlwaysC` example.
- Main local result:
  - `python3 -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli` passes,
  - `WSLS` vs `AlwaysC` now certifies cleanly with `steady_state_method = cesaro_from_initial_distribution`,
  - and that pair recovers the expected cooperative occupancy/payoff surface (`initial_distribution = [1,0,0,0]`, `avg_payoff_a = avg_payoff_b = 3`).

## 2026-03-20 — Research Pass (Anti-Vampire Recovery/Repair Proxy Completion)

- Extended `grlab certify` so the anti-vampire scorecard now computes non-null proxy values for `recovery_rounds` and `repair_abuse_rate` in the current memory-one lane instead of leaving those fields pending.
- Added exact post-shock recovery screening with a canonical unilateral-defection shock, `epsilon = 0.25`, `recovery_horizon = 40`, and a `CC`-mass guard so `CC/DC` extraction mixtures do not count as repaired cooperation.
- Added a pair-rollout repair-abuse proxy based on opponent `D -> C` repair offers that are followed by a fresh opponent defection within `k = 3` rounds while the short repair window still yields a positive cumulative payoff gap for the opponent.
- Tightened certify solver / CLI coverage for the new fields and refreshed the anti-vampire status notes in `docs/LIBRARY/topics/anti_vampire_scorecard_spec.md` and `docs/BUCKET.md`.
- Main local result:
  - `AlwaysC` vs itself now certifies as immediate repair in the proxy lane (`recovery_rounds = 1`, `repair_abuse_rate = 0` under zero-noise proxy settings),
  - `TFT` vs `AlwaysC` recovers in `2` rounds after the canonical shock,
  - and the canonical extortion example no longer fakes repair under the tightened recovery screen while `AlwaysC` facing that extortion partner shows a high repair-abuse signal in the noisy proxy lane.

## 2026-03-20 — Anti-vampire proxy scorecard + LLM incentive-contract row

- Extended `grlab certify` so memory-one pair certification now also emits a compact `anti_vampire_scorecard` proxy with:
  - `own_payoff`,
  - `payoff_gap`,
  - canonical noisy-ecology `ecology_gap_noisy`,
  - explicit blockers for the still-pending `recovery_rounds` / `repair_abuse_rate` world-support fields,
  - and tunable `--ecology-noise`, `--ecology-rounds`, `--ecology-reps` knobs for the proxy screen.
- Added certify coverage for the new scorecard surface:
  - `grlab/tests/test_certify_solver.py`
  - `grlab/tests/test_certify_cli.py`
- Refreshed implementor doctrine around incentive semantics:
  - added `docs/LIBRARY/topics/cooperation_benchmark_llm_lanes_should_publish_incentive_instructions_and_payoff_scaling.md`,
  - tightened the minimum cooperation benchmark card in `docs/BENCHMARK_PROGRAM.md` with a new LLM/agent-lane incentive-contract row,
  - and extended `docs/RESEARCH_SOURCES.md` with `RS-GR-128`..`RS-GR-130`.
- Refreshed generated command / artifact inventory surfaces after the new certify flags and doctrine landed.
- Main local result:
  - `python3 -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli` passes,
  - canonical extortion still looks strong on a pairwise always-cooperator matchup but now fails the noisy-ecology screen (`ecology_gap_noisy ≈ +0.5335`),
  - and canonical generous TFT clears the same ecology screen (`ecology_gap_noisy ≈ -0.3353`) without pretending the full repair-contract certificate is finished.

## 2026-03-20 — Compact-card execution lanes + session-honest handoff

- Added a schema-backed `cooperation_benchmark_card_execution_lanes` surface so the compact-card stack now publishes one tiny observational environment handoff over two typed lanes: a Python integrity lane for compact-card surface rebuild/check work and a Rust harness lane for deeper repo validation.
- The new execution surface records current tool presence, native-versus-JuNest Rust posture, stable blocking reason codes, and exact recovery commands instead of letting environment truth leak only through agent-log prose.
- Tightened the compact-card inheritor stack around that surface:
  - `cooperation_benchmark_card_control_plane` now binds execution-lane truth and marks whether its recommended next command is available in the current lane.
  - `cooperation_benchmark_card_next_action` now carries the required execution lane and whether that lane is currently available.
  - `cooperation_benchmark_card_handoff_pack` now includes the execution-lane report/doc in its must-read and verification path.
- Tightened `docs/BENCHMARK_PROGRAM.md` with one new “execution-lane surface for compact-card handoffs” section and added one compact doctrine note:
  - `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_an_execution_lane_surface_for_compact_card_handoffs.md`

## 2026-03-20 — Compact-card typed next action + arbitration witness

- Added a schema-backed `cooperation_benchmark_card_next_action_witness` surface so the compact-card stack now preserves the live first-reentry candidate family, winning priority bucket, tie set, fallback baseline, and stable selector instead of silently collapsing those choices into one command.
- Added a schema-backed `cooperation_benchmark_card_next_action` surface so inheritors now receive one typed first command plus fallback commands derived from the fused control plane and grouped review queue.
- Threaded the new first-reentry surfaces into the compact-card control-plane / handoff documentation and refreshed the generated inventory / artifact summaries.

## 2026-03-20 — rev0329 lineage-grouped macro review queue + non-collapsing unresolved handoff

- Added one new schema-backed grouped repair surface for compact benchmark cards:
  - `schemas/cooperation_benchmark_card_macro_review_queue.schema.json`
  - `scripts/report/build_cooperation_benchmark_card_macro_review_queue.py`
  - `scripts/test/check_cooperation_benchmark_card_macro_review_queue.py`
  - `docs/COOPERATION_BENCHMARK_CARD_MACRO_REVIEW_QUEUE.md`
  - `artifacts/reports/cooperation_benchmark_card_macro_review_queue.json`
- The new macro review queue groups the standing compact-card review queue by lineage and publishes:
  - one deterministic primary review command per lineage,
  - the union of live item ids / item kinds / reason codes / context paths,
  - the full review-command set and any currently available repair commands,
  - plus current operational/citation-head context so inheritors do not have to reconstruct repair state from a flat queue.
- Tightened the existing compact-card inheritor surfaces around that grouped queue:
  - `cooperation_benchmark_card_control_plane` now binds the macro review queue, counts queued review lineages, and exposes per-lineage review reason codes plus primary/full review/apply commands.
  - `cooperation_benchmark_card_handoff_pack` no longer collapses unresolved lineages to one arbitrary review command; it now carries the grouped review/apply command set from the macro review queue.
- Tightened `docs/BENCHMARK_PROGRAM.md` with one new “lineage-grouped macro review queue for compact cards” section and added one compact doctrine note:
  - `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_lineage_grouped_macro_review_queue_for_compact_cards.md`
- Donor insight:
  - VHK's macro-review-queue discipline is worth importing here because the flat queue was already good enough to drive repair work, but not good enough to survive handoff without collapsing multi-item lineage state.
  - Micromax's help / trust-clear pattern also applies here: the best next action should stay obvious even when several related repair rows exist.

## 2026-03-20 — rev0328 fused compact-card control plane + typed report bindings

- Added one new schema-backed inheritor reentry surface for compact benchmark cards:
  - `schemas/cooperation_benchmark_card_control_plane.schema.json`
  - `scripts/report/build_cooperation_benchmark_card_control_plane.py`
  - `scripts/test/check_cooperation_benchmark_card_control_plane.py`
  - `docs/COOPERATION_BENCHMARK_CARD_CONTROL_PLANE.md`
  - `artifacts/reports/cooperation_benchmark_card_control_plane.json`
- The new control-plane surface fuses the existing compact-card stack into one typed answer for inheritors:
  - overall verdict (`ready` / `needs_review`),
  - lineage counts, citation-ready counts, handoff-ready counts, and queued review pressure,
  - per-lineage operational head / citation head / unresolved citation reason codes / review-item kinds,
  - exact report bindings with bytes + sha256 for inventory / heads / review queue / citation surface / handoff pack,
  - and a small preferred entrypoint command set so future sessions do not need to reconstruct the control plane by memory.
- Tightened `docs/BENCHMARK_PROGRAM.md` with one new “fused control-plane surface for compact cards” section and added one compact doctrine note:
  - `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_fused_control_plane_surface_for_compact_cards.md`
- Refreshed generated inventories / report summaries so the new schema / validator / report surfaces are visible in the standing repo catalogs:
  - `docs/COMMAND_INVENTORY.md`
  - `docs/VALIDATOR_INVENTORY.md`
  - `docs/SCHEMA_INVENTORY.md`
  - `docs/ARTIFACT_BUCKETS.md`
  - `artifacts/reports/artifact_summary.json`
  - `artifacts/reports/archive_size_profile_snapshot_20260316.{json,md}`
- Validation run in this cloudtainer:
  - `python3 ./scripts/report/build_cooperation_benchmark_card_inventory.py --write` ✅
  - `python3 ./scripts/report/build_cooperation_benchmark_card_heads.py --write` ✅
  - `python3 ./scripts/report/build_cooperation_benchmark_card_review_queue.py --write` ✅
  - `python3 ./scripts/report/build_cooperation_benchmark_card_citation_surface.py --write` ✅
  - `python3 ./scripts/report/build_cooperation_benchmark_card_handoff_pack.py --write` ✅
  - `python3 ./scripts/report/build_cooperation_benchmark_card_control_plane.py --write` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_inventory.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_heads.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_review_queue.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_citation_surface.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_handoff_pack.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_control_plane.py` ✅
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_schema_json_valid.py` ✅
  - `python3 ./scripts/test/check_scripts_compile.py` ✅
  - `python3 ./scripts/test/check_scripts_executable.py` ✅
- Research / donor insight:
  - VHK’s fused-state / preferred-entrypoint pattern is worth importing here once the compact-card stack already has multiple good sub-surfaces; the next useful object is not another receipt but one tiny typed reentry surface.
  - EvidenceVault’s manifest-style binding discipline is also worth importing here, so the fused answer is bound to exact underlying report files rather than standing as unaudited prose.

## 2026-03-20 — rev0326 minimal citation handoff pack + lineage-basis manifest

- Added one new schema-backed inheritor surface for compact benchmark-card citation handoff:
  - `schemas/cooperation_benchmark_card_handoff_pack.schema.json`
  - `scripts/report/build_cooperation_benchmark_card_handoff_pack.py`
  - `scripts/test/check_cooperation_benchmark_card_handoff_pack.py`
  - `docs/COOPERATION_BENCHMARK_CARD_HANDOFF_PACK.md`
  - `artifacts/reports/cooperation_benchmark_card_handoff_pack.json`
- The new handoff pack now emits one fail-closed minimal manifest per unique citation lineage with:
  - the exact citation head card,
  - the exact canonical rendered markdown and verified freeze receipt,
  - the ordered root-to-head ancestry card ids,
  - the ordered retained delta receipts that explain how the current citation head was reached,
  - an exact file manifest with byte counts and sha256s,
  - and local verify / refresh commands so inheritors can re-enter the compact-card stack without reconstructing lineage basis by hand.
- Tightened `docs/BENCHMARK_PROGRAM.md` with one new “minimal citation handoff pack for compact cards” section so the compact-card program now distinguishes:
  - local card validity,
  - claim readiness,
  - guarded freeze,
  - lineage head status,
  - fail-closed citation eligibility,
  - and minimal inheritor handoff basis.
- Refreshed standing inventories because the new schema / validator / report surfaces landed:
  - `docs/COMMAND_INVENTORY.md`
  - `docs/VALIDATOR_INVENTORY.md`
  - `docs/SCHEMA_INVENTORY.md`
  - `docs/ARTIFACT_BUCKETS.md`
- Validation run in this cloudtainer:
  - `python3 ./scripts/report/build_cooperation_benchmark_card_inventory.py --write` ✅
  - `python3 ./scripts/report/build_cooperation_benchmark_card_heads.py --write` ✅
  - `python3 ./scripts/report/build_cooperation_benchmark_card_review_queue.py --write` ✅
  - `python3 ./scripts/report/build_cooperation_benchmark_card_citation_surface.py --write` ✅
  - `python3 ./scripts/report/build_cooperation_benchmark_card_handoff_pack.py --write` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_handoff_pack.py` ✅
  - plus the standing compact-card validators used for the current lineage / citation surfaces.

## 2026-03-20 — rev0325 fail-closed citation surface + verified freeze semantics

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_fail_closed_citation_surface_for_compact_cards.md`
- Tightened compact-card inventory / heads semantics so freeze status now fails closed on verified receipt integrity rather than merely on receipt presence:
  - `scripts/report/build_cooperation_benchmark_card_inventory.py`
  - `scripts/report/build_cooperation_benchmark_card_heads.py`
- Extended the heads register with one explicit drift warning class, `latest-operational-head-freeze-drift`, and a lineage-level drift count so stale freeze state no longer masquerades as citation readiness.
- Tightened the actionable review queue so freeze-drift items now carry lineage ids and a concrete guarded re-freeze command instead of only a review command:
  - `scripts/report/build_cooperation_benchmark_card_review_queue.py`
- Added one new schema-backed inheritor surface modeled after a tiny stable public surface, but specialized for compact benchmark-card citation:
  - `schemas/cooperation_benchmark_card_citation_surface.schema.json`
  - `scripts/report/build_cooperation_benchmark_card_citation_surface.py`
  - `scripts/test/check_cooperation_benchmark_card_citation_surface.py`
  - `docs/COOPERATION_BENCHMARK_CARD_CITATION_SURFACE.md`
  - `artifacts/reports/cooperation_benchmark_card_citation_surface.json`
- Tightened `docs/BENCHMARK_PROGRAM.md` with one new “fail-closed citation surface for compact cards” section.
- Refreshed standing inventories because the new schema / validator / report surfaces landed:
  - `docs/COOPERATION_BENCHMARK_CARD_INVENTORY.md`
  - `docs/COOPERATION_BENCHMARK_CARD_HEADS.md`
  - `docs/COOPERATION_BENCHMARK_CARD_REVIEW_QUEUE.md`
  - `docs/COOPERATION_BENCHMARK_CARD_CITATION_SURFACE.md`
  - `docs/VALIDATOR_INVENTORY.md`
  - `docs/SCHEMA_INVENTORY.md`
  - `docs/ARTIFACT_BUCKETS.md`
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_cooperation_benchmark_card_tooling.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_readiness_lint.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_freeze_receipt.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_delta_receipt.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_inventory.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_heads.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_review_queue.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_citation_surface.py` ✅
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_schema_json_valid.py` ✅
  - `python3 ./scripts/test/check_scripts_compile.py` ✅
  - `python3 ./scripts/test/check_scripts_executable.py` ✅
  - `python3 ./scripts/report/build_validator_inventory.py --write` ✅
  - `python3 ./scripts/report/build_schema_inventory.py --write` ✅
  - `python3 ./scripts/report/build_artifact_bucket_inventory.py --write` ✅
- Research / donor insight:
  - EvidenceVault’s explicit public-surface / snapshot discipline suggests that once the compact card stack already has citation heads, the next durable object should be one tiny fail-closed citation surface rather than more prose about what to cite.
  - TriKEM’s repeated fail-closed posture makes the freeze-status loophole visible here: a retained receipt whose bound bytes drift should stop counting as citation-ready immediately.
  - pyCausalWeave’s head-guard / repair-surface discipline suggests that stale or drifted compact-card state should expose an explicit repair command, not only a warning row.

## 2026-03-20 — rev0324 guarded freeze + actionable card review queue

- Added two compact inheritor-facing notes:
  - `docs/LIBRARY/topics/cooperation_benchmark_programs_should_fail_closed_when_freezing_compact_cards_against_stale_operational_heads.md`
  - `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_an_actionable_review_queue_for_compact_cards.md`
- Extended the compact cooperation-card freeze path with one stale-head guard, `--require-current-operational-head`, and taught freeze receipts to retain the matched lineage guard when that mode is used.
- Added one new schema-backed maintenance surface for compact cards:
  - `schemas/cooperation_benchmark_card_review_queue.schema.json`
  - `scripts/report/build_cooperation_benchmark_card_review_queue.py`
  - `scripts/test/check_cooperation_benchmark_card_review_queue.py`
  - `docs/COOPERATION_BENCHMARK_CARD_REVIEW_QUEUE.md`
  - `artifacts/reports/cooperation_benchmark_card_review_queue.json`
- Tightened the standing heads register with stable `warning_reason_codes` so queue/review automation can branch on warning classes without parsing prose.
- Froze the current toy example head with the new guard and retained its canonical surfaces:
  - `examples/snapshots/cooperation_benchmark_card_example_v2.md`
  - `examples/snapshots/cooperation_benchmark_card_example_v2.freeze_receipt.json`
- Refreshed standing compact-card and archive inventories because the new queue / schema / validator / report surfaces landed:
  - `docs/COOPERATION_BENCHMARK_CARD_INVENTORY.md`
  - `docs/COOPERATION_BENCHMARK_CARD_HEADS.md`
  - `docs/VALIDATOR_INVENTORY.md`
  - `docs/SCHEMA_INVENTORY.md`
  - `docs/ARTIFACT_BUCKETS.md`
  - `artifacts/reports/artifact_summary.json`
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_cooperation_benchmark_card_schema.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_tooling.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_readiness_lint.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_freeze_receipt.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_delta_receipt.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_inventory.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_heads.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_review_queue.py` ✅
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_schema_json_valid.py` ✅
  - `python3 ./scripts/test/check_scripts_compile.py` ✅
  - `python3 ./scripts/test/check_scripts_executable.py` ✅
  - `python3 ./scripts/report/build_validator_inventory.py` ✅
  - `python3 ./scripts/report/build_schema_inventory.py` ✅
  - `python3 ./scripts/report/build_artifact_bucket_inventory.py` ✅
  - `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest`, which is absent in this container.

## 2026-03-19 — rev0323 lineage head register + citation head warnings

- Added one compact inheritor-facing note, `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_lineage_head_register_for_compact_cards.md`, so the archive now distinguishes lineage-scoped operational heads from frozen citation heads instead of leaving inheritors to infer that from inventory rows by hand.
- Added one new schema, one small report builder, one validator, and one generated doc/report pair:
  - `schemas/cooperation_benchmark_card_heads_register.schema.json`
  - `scripts/report/build_cooperation_benchmark_card_heads.py`
  - `scripts/test/check_cooperation_benchmark_card_heads.py`
  - `docs/COOPERATION_BENCHMARK_CARD_HEADS.md`
  - `artifacts/reports/cooperation_benchmark_card_heads.json`
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short “lineage-head register” section and added one new library index entry plus `Immediate Repo Implications` item 62 and `RS-GR-126` / `RS-GR-127` in `docs/RESEARCH_SOURCES.md`.
- Validation run in this cloudtainer:
  - `python3 ./scripts/report/build_cooperation_benchmark_card_heads.py --write` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_heads.py` ✅
  - `python3 ./scripts/report/build_cooperation_benchmark_card_inventory.py --write` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_inventory.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_schema.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_tooling.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_readiness_lint.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_freeze_receipt.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_delta_receipt.py` ✅
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `python3 ./scripts/test/check_schema_json_valid.py` ✅
  - `python3 ./scripts/test/check_scripts_compile.py` ✅
  - `python3 ./scripts/test/check_scripts_executable.py` ✅
  - `make test-validator-inventory test-schema-inventory` ✅
  - `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - once the archive already has inventory + lineage, the next practical question is no longer “what exists?” but “what should I cite right now?”;
  - the smallest durable fix is one lineage-head register that names operational heads, citation heads, and the exact warnings that block a unique citation-ready tip;
  - keeping citation-head status stricter than operational-head status is useful because the latest claim-ready tip may still need a freeze receipt before it is safe to hand off as the reviewed canonical view.

## 2026-03-19 — rev0322 card inventory + lineage register

- Added one compact inheritor-facing note, `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_compact_inventory_and_lineage_register_for_cards_and_receipts.md`, so the archive now treats multiple retained cooperation cards plus their freeze / delta receipts as a searchable local register rather than a set of scattered files.
- Added one small inventory builder, `scripts/report/build_cooperation_benchmark_card_inventory.py`, that discovers schema-valid cards plus freeze / delta receipts, links them, classifies claim-ready / frozen / latest-known status, and emits both `docs/COOPERATION_BENCHMARK_CARD_INVENTORY.md` and `artifacts/reports/cooperation_benchmark_card_inventory.json`.
- Added one validator, `scripts/test/check_cooperation_benchmark_card_inventory.py`, and refreshed `docs/VALIDATOR_INVENTORY.md` plus `artifacts/reports/validator_inventory.json`.
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short “compact inventory and lineage register” section and added one new library index entry plus `Immediate Repo Implications` item 61 and `RS-GR-124` / `RS-GR-125` in `docs/RESEARCH_SOURCES.md`.
- Validation run in this cloudtainer:
  - `python3 ./scripts/report/build_cooperation_benchmark_card_inventory.py --write` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_inventory.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_schema.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_tooling.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_readiness_lint.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_freeze_receipt.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_delta_receipt.py` ✅
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `python3 ./scripts/test/check_schema_json_valid.py` ✅
  - `python3 ./scripts/test/check_scripts_compile.py` ✅
  - `python3 ./scripts/test/check_scripts_executable.py` ✅
  - `make test-validator-inventory` ✅
  - `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - once the archive has more than one claim-ready card and more than one compact receipt, the next failure mode is no longer missing provenance atoms but missing **local searchability over those atoms**;
  - a tiny generated inventory is the smallest durable fix because it reuses standing cards and receipts rather than widening them;
  - listing latest-known claim-ready ids and orphan receipts gives future sessions one fast triage surface for whether the retained card stack is actually navigable and internally linked.

## 2026-03-19 — rev0321 example snapshot identity cleanup + surrogate-id discipline

- Added one compact inheritor-facing note, `docs/LIBRARY/topics/example_json_snapshots_should_be_addressable_by_stable_ids_or_canonical_surrogate_ids.md`, so the archive now treats retained example JSON objects as addressable artefacts even when their strict schemas do not admit an explicit `id` field.
- Added `scripts/lib/example_identity.py` and taught both `scripts/test/check_examples_json.py` and `scripts/test/check_examples_unique_ids.py` to operate over explicit-or-surrogate example identities instead of failing on schema-strict snapshots that omit `id`.
- Tightened the example-validation reports so they now record `example_id` plus whether the identity source was explicit or canonical-path surrogate.
- Added one new library index entry plus `Immediate Repo Implications` item 60 and `RS-GR-122` / `RS-GR-123` in `docs/RESEARCH_SOURCES.md`.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_examples_json.py` ✅
  - `python3 ./scripts/test/check_examples_unique_ids.py` ✅
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `python3 ./scripts/test/check_schema_json_valid.py` ✅
  - `python3 ./scripts/test/check_scripts_compile.py` ✅
  - `python3 ./scripts/test/check_scripts_executable.py` ✅
  - `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - the archive had crossed the point where a generic examples validator was failing not because the examples were malformed, but because heterogeneous strict schemas handled identity differently;
  - explicit-or-surrogate addressability is the compact fix, because it restores inventory, duplicate-id checking, and small receipt linkage without widening dozens of strict schemas just to satisfy one archive-level convention;
  - path-derived surrogate ids are acceptable here because the archive itself is the retained package boundary, so repo-relative paths are already part of the local provenance contract.

## 2026-03-19 — rev0320 canonical delta receipt for claim-ready cooperation cards

- Added one compact inheritor-facing note, `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_canonical_delta_receipt_for_compact_cards.md`, so the archive now treats card-to-card change as a first-class compact audit object rather than forcing future inheritors to diff two retained cards by hand.
- Extended `scripts/tools/cooperation_benchmark_card.py` with a new `compare` mode that re-validates two claim-ready cards, classifies changed dotted field paths into claim-surface versus metadata-only changes, and emits one tiny delta receipt.
- Added one new schema, one second worked example card, one example delta receipt, and one validator:
  - `schemas/cooperation_benchmark_card_delta_receipt.schema.json`
  - `examples/snapshots/cooperation_benchmark_card_example_v2.json`
  - `examples/snapshots/cooperation_benchmark_card_example.delta_receipt.json`
  - `scripts/test/check_cooperation_benchmark_card_delta_receipt.py`
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short “canonical delta receipt between claim-ready compact cards” section and added one new library index entry plus `Immediate Repo Implications` item 59 and `RS-GR-117` through `RS-GR-121` in `docs/RESEARCH_SOURCES.md`.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_cooperation_benchmark_card_schema.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_tooling.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_readiness_lint.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_freeze_receipt.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_delta_receipt.py` ✅
  - `python3 ./scripts/test/check_examples_json.py` ⚠️ (still fails on a pre-existing archive-report snapshot without an `id` field)
  - `python3 ./scripts/test/check_examples_unique_ids.py` ✅
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `python3 ./scripts/test/check_schema_json_valid.py` ✅
  - `python3 ./scripts/test/check_scripts_compile.py` ✅
  - `python3 ./scripts/test/check_scripts_executable.py` ✅
  - `make test-validator-inventory test-schema-inventory` ✅
  - `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - once compact cooperation cards are schema-valid, lint-clean, and frozen, the next small operational gap is answering what changed between two retained versions without manual line-by-line diff review;
  - one tiny delta receipt is enough to keep that answer machine-checkable while staying far smaller than retaining duplicate prose summaries or bulky sidecar bundles;
  - separating claim-surface changes from metadata-only drift gives future inheritors a faster way to decide whether a benchmark claim actually moved.

## 2026-03-19 — rev0319 freeze receipt for claim-ready cooperation cards

- Added one compact inheritor-facing note, `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_freeze_receipt_for_claim_ready_compact_cards.md`, so the archive now treats claim-ready cooperation cards as objects that should be frozen to a specific rendered view and local derivation context rather than merely left lint-clean.
- Extended `scripts/tools/cooperation_benchmark_card.py` with a new `freeze` mode that re-validates the card, re-runs readiness lint, regenerates the canonical markdown render, and emits one compact hash-bearing receipt.
- Added one new schema, `schemas/cooperation_benchmark_card_freeze_receipt.schema.json`, one example receipt, `examples/snapshots/cooperation_benchmark_card_example.freeze_receipt.json`, and one validator, `scripts/test/check_cooperation_benchmark_card_freeze_receipt.py`.
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short “freeze receipt for claim-ready compact cards” section and added one new library index entry plus `Immediate Repo Implications` item 58 and `RS-GR-117` / `RS-GR-118` in `docs/RESEARCH_SOURCES.md`.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_cooperation_benchmark_card_schema.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_tooling.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_readiness_lint.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_freeze_receipt.py` ✅
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `python3 ./scripts/test/check_schema_json_valid.py` ✅
  - `python3 ./scripts/test/check_scripts_compile.py` ✅
  - `python3 ./scripts/test/check_scripts_executable.py` ✅
  - `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - once a compact cooperation card is schema-valid, rendered, and lint-clean, the next small failure mode is stale or unbound human-readable review surfaces;
  - one tiny freeze receipt gives the archive a provenance handle that binds the reviewed JSON card to the canonical markdown view and the local schema/tool hashes;
  - that is a better next move than more prose because it improves actual handoff trust without materially expanding the archive.

## 2026-03-19 — rev0318 readiness lint for claim-ready cooperation cards

- Added one compact inheritor-facing note, `docs/LIBRARY/topics/cooperation_benchmark_programs_should_distinguish_draft_valid_cards_from_claim_ready_cards_via_readiness_lint.md`, so the archive now distinguishes a schema-valid draft card from a claim-ready compact publication object.
- Extended `scripts/tools/cooperation_benchmark_card.py` with a tiny `lint` mode that validates the schema-backed card and then fails if unresolved `TODO` placeholders or vacuous `not applicable` markers remain.
- Added one validator, `scripts/test/check_cooperation_benchmark_card_readiness_lint.py`, so the archive now checks that the worked example passes claim-readiness lint while fresh scaffold output correctly fails until its draft placeholders are resolved.
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short “draft-valid versus claim-ready compact cards” section and added one new library index entry plus `Immediate Repo Implications` item 57 and `RS-GR-115` / `RS-GR-116` in `docs/RESEARCH_SOURCES.md`.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_schema.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_tooling.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_readiness_lint.py` ✅
  - `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - schema validity is necessary but not sufficient for a retained claim-bearing card;
  - the scaffold should stay easy to use, but the archive should refuse to mistake unresolved placeholders for completed documentation;
  - one tiny readiness lint preserves that distinction without widening the schema or adding bulky workflow state.

## 2026-03-19 — rev0317 scaffold + canonical render for cooperation benchmark cards

- Added one compact inheritor-facing note, `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_scaffold_and_canonical_renderer_for_compact_cards.md`, so the archive now treats the compact cooperation card as something future sessions should be able to fill and review with one deterministic local tool path rather than by hand.
- Added `scripts/tools/cooperation_benchmark_card.py` with two tiny modes: `scaffold`, which emits a valid explicit JSON card shell, and `render`, which turns any valid card into a canonical markdown review surface.
- Added one rendered worked example, `examples/snapshots/cooperation_benchmark_card_example.md`, plus one validator, `scripts/test/check_cooperation_benchmark_card_tooling.py`, so the scaffold/render loop itself is now checked rather than assumed.
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short “scaffold and canonical render aid” section and added one new library index entry plus `Immediate Repo Implications` item 56 and `RS-GR-114` in `docs/RESEARCH_SOURCES.md`.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_schema.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_tooling.py` ✅
  - `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - once the archive has a machine-checkable cooperation card, the next small failure mode is manual fill drift and manual display drift;
  - one scaffold path prevents future sessions from silently dropping required rows or improvising field names;
  - one canonical renderer prevents each inheritor from wrapping the same JSON object in a different ad hoc prose surface while keeping the archive compact.

## 2026-03-19 — rev0316 machine-checkable cooperation benchmark card schema + worked example

- Added one compact inheritor-facing note, `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_machine_checkable_compact_card_schema_and_worked_example.md`, so the archive now treats the cooperation benchmark card as an object to instantiate and validate, not only as prose guidance.
- Added `schemas/cooperation_benchmark_card.schema.json`, `examples/snapshots/cooperation_benchmark_card_example.json`, and `scripts/test/check_cooperation_benchmark_card_schema.py`, giving future inheritors one small schema-backed card artifact plus a worked example and a validator check.
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short “machine-checkable compact card artifact” section that points directly at the schema and worked example and tells future sessions to prefer explicit `not applicable` strings over silent omission.
- Added `Immediate Repo Implications` item 55 plus three compact source entries in `docs/RESEARCH_SOURCES.md` (`RS-GR-111` through `RS-GR-113`) to anchor the move in BenchmarkCards, BetterBench, and the CLeAR documentation framework.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `python3 ./scripts/test/check_cooperation_benchmark_card_schema.py` ✅
  - `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - the benchmark-card shelf is now mature enough that the next high-leverage move is operationalization rather than another loophole note;
  - one compact schema-backed card object makes the existing contract easier to copy, diff, validate, and keep small across future sessions;
  - explicit `not applicable` strings close a subtle but important loophole where omitted fields can otherwise be mistaken for forgotten fields rather than intentionally inapplicable ones.

## 2026-03-19 — rev0315 primary-metric and multiplicity discipline

- Added one compact inheritor-facing note, `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_primary_endpoint_auxiliary_metrics_and_multiplicity_policy.md`, so retained cooperation results now have to say which metric actually governs the headline claim when several plausible cooperation measures exist.
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short “primary metric and multiplicity discipline” section: every retained result with multiple plausible endpoints, metric families, or composites should now publish the primary endpoint / governing metric, the auxiliary / guardrail metrics, the composite / normalization rule, and the multiplicity / metric-selection policy.
- Added `Immediate Repo Implications` item 54 plus three compact source entries in `docs/RESEARCH_SOURCES.md` (`RS-GR-108` through `RS-GR-110`) to anchor the new rule in updated reporting guidance, multiple-outcome methodology, and empirical evidence that multi-outcome reporting commonly leaves governance implicit.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - once the archive controls lane contract, comparison license, estimand, uncertainty, wrapper policy, judged scoring, environment posture, and execution budget, the next loophole is metric governance;
  - a cooperation result can otherwise look stronger than it is because one paper or run promoted the best-looking metric, convenience composite, or post-hoc headline out of several plausible measures;
  - one tiny primary-endpoint / auxiliary-metrics / composite-rule / multiplicity-policy quartet is enough to prevent that distortion without widening the archive.

## 2026-03-19 — rev0314 tool-access, state-snapshot, and corpus-posture discipline

- Added one compact inheritor-facing note, `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_tool_access_external_state_and_knowledge_snapshot_policy.md`, so retained cooperation results now have to say which tools, which world snapshot, and which knowledge source the evaluated system could actually use.
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short “tooling, external state, and knowledge-source discipline” section: every retained result whose score can move under different tool surfaces, live-vs-frozen environment posture, corpus snapshots, or writable-state policies should now publish the tool / capability catalog, the external environment / state snapshot posture, the knowledge-base / retrieval corpus provenance, and the reset / refresh / mutability policy.
- Added `Immediate Repo Implications` item 53 plus six compact source entries in `docs/RESEARCH_SOURCES.md` (`RS-GR-102` through `RS-GR-107`) to anchor the new rule in rigorous-agent-benchmark guidance, unified-evaluation methodology, reproducible sandbox design, state-snapshot evaluation, knowledge-grounded retrieval configuration, and tool-surface sensitivity.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - once the archive controls lane contract, comparison license, estimand, uncertainty, wrapper policy, judged scoring, scenario draw, evaluated subject, failure handling, and execution budget, the next loophole is hidden environment and knowledge posture;
  - a cooperation result can otherwise look stronger than it is because one run had a cleaner tool surface, a frozen world snapshot, a different corpus snapshot, or writable scratch permissions that another run did not;
  - one tiny tool-catalog / state-snapshot / corpus-provenance / reset-mutability quartet is enough to prevent that distortion without widening the archive.

## 2026-03-19 — rev0313 execution-budget, context, and timeout discipline

- Added one compact inheritor-facing note, `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_turn_tool_context_budget_and_timeout_policy.md`, so retained cooperation results now have to say when the published score depends on interaction slack, retained history, or runtime generosity rather than only on the nominal task.
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short “resource budget, context, and timeout discipline” section: every retained result whose score can move under different turn caps, tool-use limits, context / history-retention regimes, token budgets, or timeout policies should now publish the turn / action / tool-call budget, the context / history-retention policy, the token / compute / latency budget, and the limit-hit handling rule.
- Added `Immediate Repo Implications` item 52 plus four compact source entries in `docs/RESEARCH_SOURCES.md` (`RS-GR-098` through `RS-GR-101`) to anchor the new rule in evaluation-pipeline methodology, explicit tool-budgeted benchmark protocols, context-ceiling evidence, and resource-constrained agent evaluation.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - once the archive controls lane contract, comparison license, estimand, uncertainty, wrapper policy, judged scoring, scenario draw, evaluated subject, and failure handling, the next loophole is hidden execution slack;
  - a cooperation result can otherwise look stronger than it is because one run had more turns, more tool calls, a longer retained history, more tokens, or a more forgiving timeout / retry posture;
  - one tiny turn/tool-budget / history-policy / compute-latency-budget / limit-hit-rule quartet is enough to prevent that distortion without widening the archive.

## 2026-03-19 — rev0312 subject-provenance, serving-stack, and drift-window discipline

- Added one compact inheritor-facing note, `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_evaluated_subject_provenance_serving_stack_and_drift_window.md`, so retained cooperation results now have to say which deployed subject was actually evaluated rather than only naming a broad model family.
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short “evaluated subject and deployment discipline” section: every retained result tied to a provider endpoint, dated model marker, local weight snapshot, or third-party compatible service should now publish the evaluated-subject provenance, the serving stack / execution substrate, the evaluation window / snapshot date, and the update / drift posture.
- Added `Immediate Repo Implications` item 51 plus four compact source entries in `docs/RESEARCH_SOURCES.md` (`RS-GR-094` through `RS-GR-097`) to anchor the new rule in LLM reporting guidance, API drift monitoring, configuration-sensitive evaluation, and shadow-API provenance risk.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - once the archive controls lane contract, comparison license, estimand, uncertainty, wrapper policy, failure handling, adjudication, and scenario draw, the next loophole is subject drift and endpoint ambiguity;
  - a cooperation result can otherwise look stronger than it is because it came from a different dated model marker, a rolling alias that changed mid-window, a different serving stack, or a third-party endpoint that only claimed to match the official model;
  - one tiny subject-provenance / serving-stack / evaluation-window / drift-posture quartet is enough to prevent that distortion without widening the archive.

## 2026-03-19 — rev0311 scenario-draw, seed, and release-posture discipline

- Added one compact inheritor-facing note, `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_scenario_family_sampling_rule_seed_policy_and_release_posture.md`, so retained cooperation results now have to say when the published score depends on which worlds or scenarios were drawn and how exposed those worlds were before evaluation.
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short “scenario draw, seed, and release discipline” section: every retained result drawn from a fixed suite, generator family, world bank, task-template family, or randomized assignment pool should now publish the scenario / world / template family, the sampling / randomization rule, the seed set / reroll / stopping policy, and the release posture / holdout exposure.
- Added `Immediate Repo Implications` item 50 plus three compact source entries in `docs/RESEARCH_SOURCES.md` (`RS-GR-091` through `RS-GR-093`) to anchor the new rule in random-seed sensitivity, benchmark replicability guidance, and public/private holdout exposure.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - once the archive controls lane contract, comparison license, estimand, uncertainty, wrapper selection, failure handling, and adjudication, the next loophole is world-draw luck and exposure drift;
  - a retained cooperation result can otherwise look stronger than it is because it came from one favored seed bundle, one curated slice, one hidden reroll policy, or one public/private holdout posture that stays implicit;
  - one tiny scenario-family / draw-rule / seed-policy / release-posture quartet is enough to prevent that distortion without widening the archive.

## 2026-03-19 — rev0310 judge-stack and adjudication discipline

- Added one compact inheritor-facing note, `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_judge_provenance_rubric_and_adjudication_policy.md`, so retained cooperation results now have to say when the published score depends on a particular evaluator stack.
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short “judge, rubric, and adjudication discipline” section: every retained judged result should now publish the judge / rater provenance, rubric / scoring protocol, adjudication / debias rule, and calibration / escalation policy.
- Added `Immediate Repo Implications` item 49 plus four compact source entries in `docs/RESEARCH_SOURCES.md` (`RS-GR-087` through `RS-GR-090`) to anchor the new rule in current judge-pipeline guidance, position-bias evidence, confidence-aware escalation, and scoring-bias evidence.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - once lane contract, comparison license, estimand, uncertainty, wrapper policy, and denominator policy are explicit, a result can still be overstated if the evaluator stack is treated as invisible;
  - a compact benchmark card should therefore say who or what judged the run, by what rubric, with what order-debias / aggregation rule, and how uncertain cases were escalated or force-scored, so future sessions do not mistake evaluator choice for a cooperation gain.

## 2026-03-19 — rev0309 failure-handling and denominator discipline

- Added one compact inheritor-facing note, `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_failure_handling_retry_repair_and_exclusion_policy.md`, so retained cooperation results now have to say when the published score depends on failures, retries, repairs, or filtered cases.
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short “failure handling and denominator discipline” section: every retained result exposed to malformed outputs, refusals, timeouts, judge failures, comprehension failures, or post-hoc repairs should now publish the raw attempt denominator, scored denominator, failure taxonomy, retry / repair rule, and exclusion / scoring rule.
- Added `Immediate Repo Implications` item 48 plus four compact source entries in `docs/RESEARCH_SOURCES.md` (`RS-GR-083` through `RS-GR-086`) to anchor the new rule in current benchmark-practice guidance plus concrete examples where invalid outputs, retries, and filtered judgments materially shape reported scores.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - once lane contract, comparison license, estimand, uncertainty, and wrapper policy are explicit, a result can still be overstated if only successful or repaired attempts remain in the effective denominator;
  - a compact benchmark card should therefore say how failures were bucketed, retried, repaired, filtered, and scored, so future sessions do not mistake denominator choices for cooperation gains.

## 2026-03-19 — rev0308 variant-selection and test-touch discipline

- Added one compact inheritor-facing note, `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_variant_selection_tuning_and_test_touch_policy.md`, so retained cooperation results now have to say when one prompt / interface / scoring wrapper was selected from a wider family.
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short “variant selection and test-touch discipline” section: every retained result with multiple plausible wrappers should now publish the variant family, selection / tuning rule, search budget, and whether benchmark test outcomes were touched during selection.
- Added `Immediate Repo Implications` item 47 plus three compact source entries in `docs/RESEARCH_SOURCES.md` (`RS-GR-080` through `RS-GR-082`) to anchor the new rule in prompt-family evaluation, benchmark-wrapper sensitivity, and selective-disclosure effects.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - once lane contract, comparison license, estimand, and uncertainty are explicit, the next loophole is hidden wrapper search;
  - a benchmark can otherwise look more cooperative simply because the published score came from a best-picked prompt, answer-selection rule, or agent shell after trying several nearby variants;
  - one tiny variant-selection quartet on the compact card is enough to prevent that distortion without widening the archive.

## 2026-03-19 — rev0307 dependence-aware uncertainty discipline

- Added one compact inheritor-facing note, `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_dependence_structure_inference_unit_and_uncertainty_summary.md`, so retained comparative cooperation results now have to say how certainty was computed rather than only reporting a point estimate.
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short “uncertainty and dependence discipline” section: every retained comparative result should now publish the dependence / clustering structure, the inference or resampling unit, and the primary uncertainty summary.
- Added `Immediate Repo Implications` item 46 plus two compact source entries in `docs/RESEARCH_SOURCES.md` (`RS-GR-078` and `RS-GR-079`) to anchor the new rule in benchmark-reporting and dependence-aware inference guidance.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - once a cooperation result has a clear lane contract, a comparison license, and a declared estimand, the next loophole is fake certainty from correlated observations being counted as many independent datapoints;
  - a compact benchmark card should therefore say where dependence lives, what unit carries the inference, and what uncertainty object belongs to the primary contrast, so future sessions do not mistake repeated turns or repeated partner encounters for a large independent sample.

## 2026-03-19 — rev0306 score-construction estimand discipline

- Added one compact inheritor-facing note, `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_the_scored_unit_pooling_rule_and_primary_estimand.md`, so retained cooperation scores now have to say what quantitative object they summarize.
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short “score construction discipline” section: every retained cooperation result should now publish the scored unit, pooling / weighting / censoring rule, and primary estimand.
- Added `Immediate Repo Implications` item 45 plus one compact source entry in `docs/RESEARCH_SOURCES.md` (`RS-GR-077`) to anchor the new rule in evaluation-context methodology; reused the standing simulation-study and benchmark-documentation sources already in the archive.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - once the archive distinguishes benchmark lanes cleanly and constrains the headline comparison they license, the next remaining reporting failure is score-construction ambiguity;
  - a cooperation score should therefore declare whether it is per turn, per episode, per participant, or pooled across lanes, plus how it is weighted and what estimand it is meant to represent, so future sessions do not compare unlike quantitative objects as though they were one scalar.

## 2026-03-19 — rev0305 benchmark-card headline-comparison discipline

- Added one compact inheritor-facing note, `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_the_headline_comparison_they_license.md`, so the card now constrains what headline comparison a retained cooperation result actually licenses.
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short “headline comparison discipline” section: every retained cooperation card should now say which nearby claim is licensed and which stronger claim is not licensed without further justification.
- Added `Immediate Repo Implications` item 44 plus three compact source entries in `docs/RESEARCH_SOURCES.md` (`RS-GR-074`..`RS-GR-076`) to anchor the new rule in benchmark-documentation and evaluation-methodology work.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - once the archive’s minimum cooperation card is nearly complete, the next real scientific risk is no longer missing metadata but over-strong headlines drawn from richly conditional lanes;
  - a benchmark card should therefore act as a comparison license, not merely as a lane description, so future sessions do not launder proxy / language / communication / visibility / adaptation differences into a generic “more cooperative” claim.

## 2026-03-19 — rev0304 benchmark-card language/translation row

- Tightened the implementor-facing minimum cooperation card in `docs/BENCHMARK_PROGRAM.md` by adding the missing natural-language contract row for interaction language, translation / localization regime, symmetry across sides, and pooling rule across language lanes.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `make test-quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - once a benchmark changes interaction language, localization, or whether scores are pooled across language lanes, it has changed the linguistic contract rather than merely the policy;
  - a cooperation score without language / translation metadata can quietly mix wording effects and cross-lingual strategic divergence into a policy-quality claim.

## 2026-03-19 — rev0303 benchmark-card human-proxy provenance row

- Tightened the implementor-facing minimum cooperation card in `docs/BENCHMARK_PROGRAM.md` by adding the missing human-proxy row for human-lane type, proxy provenance, hosting posture, and real-human escalation status.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `make test-quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - once a benchmark swaps actual humans for hosted or released human-like proxies, it has changed the counterpart lane rather than merely the evaluated policy;
  - a cooperation score without human-proxy provenance and escalation metadata can quietly launder proxy success into a stronger human-compatibility claim than the evidence supports.

## 2026-03-19 — rev0302 benchmark-card participant-pool provenance row

- Tightened the implementor-facing minimum cooperation card in `docs/BENCHMARK_PROGRAM.md` by adding the missing real-human-lane sampling row for participant-pool provenance, country / residence mix, key eligibility filters, and repeat-exposure policy.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `make test-quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - once a benchmark changes who the sampled humans are, where they were recruited, or whether they are benchmark-naive versus repeatedly exposed, it has changed the measured human-compatibility problem rather than merely the model;
  - a human-lane cooperation score without participant-pool metadata can quietly mix population effects and re-participation effects into a policy-quality claim.

## 2026-03-19 — rev0301 benchmark-card disclosure/belief row

- Tightened the implementor-facing minimum cooperation card in `docs/BENCHMARK_PROGRAM.md` by adding the missing human-lane identity-perception row for counterpart-disclosure condition, blinding / deception note, and participant-belief elicitation.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `make test-quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - once a benchmark changes what people are told about counterpart identity, or whether their identity beliefs are elicited, it has changed the human interaction contract rather than merely the model;
  - a human-lane cooperation score without disclosure/belief metadata can quietly mix identity-label effects into a policy-quality claim.

## 2026-03-19 — rev0300 benchmark-card stakes/comprehension row

- Tightened the implementor-facing minimum cooperation card in `docs/BENCHMARK_PROGRAM.md` by adding the missing human-lane incentives row for material payoff matrix, stake / compensation mapping, and comprehension protocol.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `make test-quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - once a benchmark changes payoffs, compensation salience, or who actually understood the task, it has changed the measured cooperation problem rather than merely the model;
  - a human-lane cooperation score without stakes/comprehension metadata can quietly mix incentive effects and misunderstanding effects into one misleading claim.

## 2026-03-19 — rev0299 benchmark-card authority regime row

- Tightened the implementor-facing minimum cooperation card in `docs/BENCHMARK_PROGRAM.md` by adding the missing authority-regime row for intervention rights, delegation policy, final-action authority, and override / escalation rights when control is shared.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `make test-quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - once a benchmark changes who can act directly, who can veto, or when delegation is allowed, it has changed the collaboration institution rather than merely the model;
  - a cooperation score without authority-regime metadata can quietly mix advisor, delegate, co-actor, and veto-gated lanes into one misleading claim.

## 2026-03-19 — rev0298 benchmark-card visibility/horizon rows + cooperation index sync

- Tightened the implementor-facing minimum cooperation card in `docs/BENCHMARK_PROGRAM.md` by adding two already-supported contract rows:
  - information visibility / asymmetry regime,
  - and interaction horizon / stopping-rule / termination-knowledge regime.
- Synced `docs/LIBRARY/README.md` with the standing cooperation-contract shelf so inheritors can actually discover the already-retained notes for disclosure, participant pool, stakes/comprehension, language, familiarization, visibility, communication, horizon, intervention rights, and process-aware evaluation.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `make test-quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - once a benchmark changes who can see what or how long the interaction can continue, the task itself has changed;
  - a cooperation result without visibility and horizon metadata can quietly mix observability artifacts and shadow-of-the-future artifacts into a policy claim.

## 2026-03-19 — rev0297 role-assignment benchmark card + seat-switch contract

- Added one compact benchmark-publication note at `docs/LIBRARY/topics/cooperation_benchmarks_should_publish_role_assignment_and_side_switch_policy.md` so future inheritors do not mistake seat/role allocation artifacts for general cooperation ability.
- Tightened the benchmark-contract spine without widening the archive:
  - added principle `43` to `docs/RESEARCH_SOURCES.md`,
  - extended the source pack with `RS-GR-071`, `RS-GR-072`, and `RS-GR-073`,
  - extended the implementor-facing cooperation card in `docs/BENCHMARK_PROGRAM.md`,
  - and indexed the new note in `docs/LIBRARY/README.md`.
- Validation run in this cloudtainer:
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `make test-quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - once a benchmark places the system into substantively different seats (planner vs follower, supervisor vs subordinate, explainer vs actor, or equivalent), role assignment becomes part of the benchmark contract;
  - otherwise a system can look cooperative only because it was always tested in the easier, more trusted, or more informed role.

## 2026-03-19 — rev0296 post-adaptation transfer split + compact cooperation card

- Added one compact benchmark-publication note at `docs/LIBRARY/topics/cooperation_benchmarks_should_separate_same_partner_coadaptation_from_fresh_partner_transfer.md` so future inheritors do not mistake private same-pair co-adaptation for broader post-familiarization transfer.
- Tightened the source-backed benchmark-contract spine without widening the archive:
  - added principle `42` to `docs/RESEARCH_SOURCES.md`,
  - added a small implementor-facing "Minimum cooperation benchmark card" section to `docs/BENCHMARK_PROGRAM.md`,
  - and indexed the new note in `docs/LIBRARY/README.md`.
- Restored execute bits on shell scripts and hooks after zip hydration so local harness / hook paths are runnable again from the archive copy.
- Validation run in this cloudtainer:
  - `python3 -m unittest discover -s tests/control -p 'test_*.py'` ✅
  - `python3 -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli` ✅
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `make test-quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - after any warm-up or acclimation lane, always ask whether the reported score is **same-partner continuation** or **fresh-partner transfer**;
  - otherwise a benchmark can silently promote private protocol convergence into a generalization claim.

## 2026-03-19 — rev0286 human disclosure lane + twenty-eighth canonical trim

- Added one compact benchmark-publication note at `docs/LIBRARY/topics/cooperation_benchmark_human_lanes_should_publish_counterpart_disclosure_and_belief_protocol.md` so future inheritors separate policy effects from participant-belief / disclosure effects in real-human lanes.
- Extended `docs/RESEARCH_SOURCES.md` with `RS-GR-051` and `RS-GR-052`, making counterpart disclosure and participant-belief elicitation a standing human-lane contract.
- Added one tiny semantic-handle topic plus alias for `examples_validation`, closing the only newly exposed second-wave gap without retaining another bulky report family.
- Executed one more cited exact-file trim: `12` retained report files across `6` families left `artifacts/reports`, reclaiming `51057` raw bytes.
- Refreshed the package / hotspot / semantic-handle / candidate / gap / manifest / rehearsal / stage / execution receipts on the smaller tree and restored package-boundary hygiene by removing stray `__pycache__` residue before rebuilding the package receipt.
- Current live posture after reclosure:
  - retained tree `9454280` raw bytes / `2673724` approximate zip bytes / `1366` retained files,
  - report bucket `148579` raw bytes across `67` files,
  - next cited manifest frontier `47123` raw bytes across `6` families / `11` exact report files,
  - and the refreshed rehearsal again projects `0` next-frontier handle gaps.

## 2026-03-19 — rev0284 receipt reclosure + compact cooperation coverage grid

- Added one compact benchmark-publication note at `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_counterpart_class_x_novelty_axis_coverage.md` so future inheritors can publish cooperation claims as a small tested-cells grid (counterpart class × novelty axis) rather than one overcompressed scalar.
- Preserved and documented the already-landed counterpart-mix benchmark-contract note plus `RS-GR-049` source row on this tree.
- Repaired the semantic alias layer for the half-step uniform-prefix optimality family so the current and projected compaction frontier are again exactly evidence-backed without retaining new bulky report pairs.
- Refreshed the live compact archive-shaping stack on the smaller post-trim tree:
  - `examples/snapshots/rematch_world_benchmark_package_receipt.json`
  - `examples/snapshots/archive_report_hotspot_receipt.json`
  - `examples/snapshots/archive_report_semantic_handle_receipt.json`
  - `examples/snapshots/archive_report_compaction_candidate_receipt.json`
  - `examples/snapshots/archive_report_compaction_gap_receipt.json`
  - `examples/snapshots/archive_report_compaction_manifest_receipt.json`
  - `examples/snapshots/archive_report_compaction_rehearsal_receipt.json`
  - `examples/snapshots/archive_report_compaction_stage_receipt.json`
  - `examples/snapshots/archive_report_compaction_execution_receipt.json`
  - `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`
- Updated the targeted validators so the smaller-tree frontier is checked against the current live manifest / rehearsal reality after the two executed trims.
- Current live posture after reclosure:
  - package receipt ready,
  - semantic-handle receipt `8/8`,
  - candidate receipt `7/7`,
  - gap receipt `8/8`,
  - manifest receipt `9/9`,
  - rehearsal receipt `11/11`,
  - stage receipt `15/15`,
  - execution receipt `26/26`,
  - retained tree size `9559773` raw bytes / `2702609` approximate zip bytes / `1385` retained files,
  - report bucket `270444` raw bytes across `89` files,
  - next cited trim frontier `51057` raw bytes across `6` families / `12` exact report files.

## 2026-03-18 (rev0282 candidate)

- Added one compact inheritor-facing timing-contract note:
  - `docs/LIBRARY/topics/rematch_worlds_should_publish_clock_and_exogenous_event_semantics_as_a_world_contract.md`
- Extended `docs/RESEARCH_SOURCES.md` with `RS-GR-046` (Froger et al., 2026) and the corresponding rule that asynchronous clock / exogenous-event semantics should be published as world-contract metadata rather than hidden scheduler detail.
- Recovered four standing semantic handles on the refreshed and one-trim-ahead hotspot surfaces:
  - threshold fingerprint words,
  - catalog references from paged digest catalogs,
  - dwell-freedom tariffs,
  - and catalog-page resolution from paged digest catalogs.
- Executed three cited exact-file trims in sequence, removing `36` retained report files across `18` families and reclaiming `217499` raw report bytes.
- Refreshed the package / hotspot / semantic-handle / candidate / gap / manifest / rehearsal / stage / execution receipt chain on the smaller tree and updated the targeted validator expectations to the new live frontier.

## 2026-03-18 (rev0281 candidate)

- Executed one cited exact-file trim: removed `12` retained report files across `6` families, reclaiming `78200` raw report bytes.
- Refreshed the package / hotspot / semantic-handle / candidate / gap / manifest / rehearsal / stage / execution receipt chain on the smaller tree.
- Reclosed the new one-trim-ahead checkpoint-schedule and short-catalog-reference gaps by standing-topic reuse, restoring `0` projected next-frontier handle gaps after the trim.

- Added one compact inheritor-facing coordination-contract note:
  - `docs/LIBRARY/topics/rematch_worlds_should_publish_agent_topology_memory_messaging_and_authority_as_a_world_contract.md`
- Extended `docs/RESEARCH_SOURCES.md` with `RS-GR-045` and the corresponding world-contract rule that multi-agent topology, messaging, memory, and authority should be declared compactly rather than hidden in orchestration code.
- Recovered three standing semantic handles that the current and one-trim-ahead compaction surface were missing:
  - boundary-stabilization protocol -> boundary-first recentering topic,
  - canonical-shortest-generator-word prefix law -> interval-state-prefix topic,
  - weakening-portfolio guardrail law -> overshoot-axis admission-profile topic.

## 2026-03-18 — Research Pass (Twenty-second Canonical Trim + Governance Contract + Source Register Repair)

- Executed one more cited exact-file compaction frontier on the live tree:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `83154` raw report bytes from the pre-trim frontier,
  - refreshed `examples/snapshots/rematch_world_benchmark_package_receipt.json`,
  - refreshed `examples/snapshots/archive_report_{hotspot,semantic_handle,compaction_candidate,compaction_gap,compaction_manifest,compaction_rehearsal,compaction_stage,compaction_execution}_receipt.json`,
  - refreshed `artifacts/reports/{artifact_summary.json,artifact_bucket_inventory.json,archive_size_profile_snapshot_20260316.json,archive_size_profile_snapshot_20260316.md}`,
  - and refreshed `docs/ARTIFACT_BUCKETS.md`.
- Added one compact inheritor-facing contract note at `docs/LIBRARY/topics/rematch_worlds_should_publish_sanction_and_restoration_graphs_as_a_world_contract.md`.
- Repaired the source register and extended `docs/RESEARCH_SOURCES.md` with:
  - the missing numbered `RS-GR-042` entry for Luo et al. (2026) so the existing adaptation-contract note now cites a real source row instead of a dangling handle,
  - and new `RS-GR-043` (Syrnikov et al., 2026) so sanction/restoration graphs are treated as institution/world-contract metadata rather than hidden controller plumbing.
- Updated the targeted validators so the refreshed smaller-tree frontier is checked against the new current live surface:
  - `scripts/test/check_archive_report_semantic_handle_receipt.py`
  - `scripts/test/check_archive_report_compaction_candidate_receipt.py`
  - `scripts/test/check_archive_report_compaction_manifest_receipt.py`
  - `scripts/test/check_archive_report_compaction_rehearsal_receipt.py`
  - `scripts/test/check_archive_report_compaction_stage_receipt.py`
- Main local result:
  - the retained tree now measures `1492` files and `10263114` raw bytes with an approximate revision zip of `2897646` bytes,
  - the live report bucket now measures `208` files and `1059350` raw bytes,
  - the semantic-handle layer now recovers `2` current hotspot families covering `27318` raw report bytes,
  - the refreshed next manifest covers `80703` raw bytes across `6` citation-backed families and `12` retained report files,
  - the refreshed rehearsal again projects `0` next-frontier handle gaps,
  - and the refreshed execution receipt passes `26/26` checks while proving the `83154`-byte cited trim actually executed on the live archive.

## 2026-03-18 — Research Pass (Twentieth Canonical Trim + Reputation Contract Reclosure)

- Executed one more cited exact-file compaction frontier on the live tree:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `101936` raw report bytes from the pre-trim frontier,
  - refreshed `examples/snapshots/rematch_world_benchmark_package_receipt.json`,
  - refreshed `examples/snapshots/archive_report_{hotspot,semantic_handle,compaction_candidate,compaction_gap,compaction_manifest,compaction_rehearsal,compaction_stage,compaction_execution}_receipt.json`,
  - refreshed `artifacts/reports/{artifact_summary.json,artifact_bucket_inventory.json,archive_size_profile_snapshot_20260316.json,archive_size_profile_snapshot_20260316.md}`,
  - and refreshed `docs/ARTIFACT_BUCKETS.md`.
- Added one compact inheritor-facing contract note at `docs/LIBRARY/topics/rematch_worlds_should_publish_reputation_assessment_and_diffusion_rules_as_a_world_contract.md`.
- Extended `docs/RESEARCH_SOURCES.md` with `RS-GR-041` (Song et al., 2025) so rematch or partner-choice worlds with persistent reputation publish a compact reputation contract rather than hiding assessment/diffusion mechanics inside controller details.
- Reclosed the refreshed current and projected frontier without adding bulky report pairs:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `4` additional semantic aliases total,
  - covering suffix counters, strict predecessor backsteps, benchmark fill-status templates, and packed scalar atoms,
  - so the refreshed smaller tree again keeps the next manifest citation-first with `0` projected handle gaps.
- Updated the targeted validators so the refreshed smaller-tree frontier is checked against the new handle-closed post-trim reality:
  - `scripts/test/check_archive_report_semantic_handle_receipt.py`
  - `scripts/test/check_archive_report_compaction_candidate_receipt.py`
  - `scripts/test/check_archive_report_compaction_manifest_receipt.py`
  - `scripts/test/check_archive_report_compaction_rehearsal_receipt.py`
  - `scripts/test/check_archive_report_compaction_stage_receipt.py`
- Main local result:
  - the semantic-handle receipt now recovers `4` alias-backed families covering `64419` report-bucket bytes,
  - the refreshed gap receipt again reports `0` current hotspot handle gaps and the rehearsal again reports `0` projected next-frontier handle gaps,
  - the refreshed next manifest covers `97717` raw bytes across `6` citation-backed families and `12` retained report files,
  - the live tree now measures `1538` retained files and `10624446` raw bytes with an approximate revision zip of `2985819` bytes,
  - and the refreshed execution receipt passes `26/26` checks while proving the `101936`-byte cited trim actually executed on the live archive.

## 2026-03-18 — Research Pass (Nineteenth Canonical Trim + Commitment Contract Alias Reclosure)

- Executed one more cited exact-file compaction frontier on the live tree:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `106875` raw report bytes from the pre-trim frontier,
  - refreshed `examples/snapshots/rematch_world_benchmark_package_receipt.json`,
  - refreshed `examples/snapshots/archive_report_{hotspot,semantic_handle,compaction_candidate,compaction_gap,compaction_manifest,compaction_rehearsal,compaction_stage,compaction_execution}_receipt.json`,
  - refreshed `artifacts/reports/{artifact_summary.json,artifact_bucket_inventory.json,archive_size_profile_snapshot_20260316.json,archive_size_profile_snapshot_20260316.md}`,
  - and refreshed `docs/ARTIFACT_BUCKETS.md`.
- Reclosed both the current hotspot surface and the next projected trim surface without retaining any new bulky report pairs:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `6` additional semantic aliases total,
  - covering canonical-anchor path atlases, positive-service threshold provenance, geometric-arrival time consistency, local axis persistence, paged catalog page filters, and shared-interval exact transport,
  - so the refreshed smaller tree keeps the next manifest citation-first with `0` projected handle gaps.
- Added one compact inheritor-facing contract note at `docs/LIBRARY/topics/rematch_worlds_should_publish_positive_service_commitment_semantics_as_a_world_contract.md`.
- Extended `docs/RESEARCH_SOURCES.md` with `RS-GR-040` (Zhu et al., 2025) to support the claim that explicit commitment mode changes the institution and therefore belongs in the world contract.
- Updated the targeted validators so the refreshed smaller-tree frontier is checked against the new handle-closed post-trim reality:
  - `scripts/test/check_archive_report_semantic_handle_receipt.py`
  - `scripts/test/check_archive_report_compaction_candidate_receipt.py`
  - `scripts/test/check_archive_report_compaction_gap_receipt.py`
  - `scripts/test/check_archive_report_compaction_manifest_receipt.py`
  - `scripts/test/check_archive_report_compaction_rehearsal_receipt.py`
  - `scripts/test/check_archive_report_compaction_stage_receipt.py`
  - `scripts/test/check_archive_report_compaction_execution_receipt.py`
- Main local result:
  - the retained tree now measures `1549` files and `10718558` raw bytes with an approximate revision zip of `3009384` bytes,
  - the live report bucket now measures `268` files and `1554399` raw bytes,
  - the refreshed next manifest covers `101936` raw bytes across `6` citation-backed families and `12` retained report files,
  - the refreshed gap receipt now reports `0` true hotspot handle gaps,
  - and the refreshed execution receipt passes `26/26` checks while proving the `106875`-byte cited trim actually executed on the live archive.

## 2026-03-18 — Research Pass (Seventeenth Canonical Trim + Interoperability Axis Note)

- Executed the standing cited exact-file compaction frontier on the live tree again:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `119721` raw report bytes from the rev0273 frontier,
  - refreshed `examples/snapshots/rematch_world_benchmark_package_receipt.json`,
  - refreshed `examples/snapshots/archive_report_{hotspot,semantic_handle,compaction_candidate,compaction_gap,compaction_manifest,compaction_rehearsal,compaction_stage,compaction_execution}_receipt.json`,
  - refreshed `artifacts/reports/{artifact_summary.json,artifact_bucket_inventory.json,archive_size_profile_snapshot_20260316.json,archive_size_profile_snapshot_20260316.md}`,
  - and refreshed `docs/ARTIFACT_BUCKETS.md`.
- Added one compact inheritor-facing benchmark note at `docs/LIBRARY/topics/benchmark_interoperability_should_separate_partner_environment_and_institution_generalization.md`.
- Extended `docs/RESEARCH_SOURCES.md` with three current interoperability / zero-shot-cooperation references:
  - `RS-GR-036` OGC,
  - `RS-GR-037` CEC,
  - `RS-GR-038` SocialJax.
- Updated the targeted archive-compaction validator scripts so the smaller-tree semantic / candidate / gap / manifest / rehearsal / stage / execution expectations match the new live frontier.
- Main local result:
  - the retained report bucket shrank by `119721` raw bytes,
  - the refreshed next manifest covers `239067` raw bytes across `6` families and `10` retained report files,
  - and the refreshed rehearsal now exposes `3` true handle gaps rather than falsely reporting the frontier as fully covered.

## 2026-03-18 — Research Pass (Fifteenth Canonical Trim + Frontier Shortlist Reclosure)

- Executed the standing cited exact-file compaction frontier on the live tree again instead of leaving the refreshed manifest as rehearsal only:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `132685` raw report bytes from the rev0271 frontier,
  - refreshed `examples/snapshots/rematch_world_benchmark_package_receipt.json`,
  - refreshed `examples/snapshots/archive_report_{hotspot,semantic_handle,compaction_candidate,compaction_gap,compaction_manifest,compaction_rehearsal,compaction_stage,compaction_execution}_receipt.json`,
  - refreshed `artifacts/reports/{artifact_summary.json,artifact_bucket_inventory.json,archive_size_profile_snapshot_20260316.json,archive_size_profile_snapshot_20260316.md}`,
  - and refreshed `docs/ARTIFACT_BUCKETS.md`.
- Reclosed the newly exposed hotspot and one-trim-ahead frontier without minting any new durable note:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `3` additional aliases for decision-packet compiled shortlists, equiprobable exact-threshold switching, and shortest-script transport-frontier regimes,
  - restored the corridor-exit alias with tighter literal evidence markers,
  - widened the buffered semantic hotspot scan from `12` to `13` families so the projected transport-frontier row is recovered before it becomes a false second-wave gap,
  - updated the targeted validator scripts so the refreshed smaller-tree semantic/candidate/manifest/rehearsal/stage expectations match the live archive,
  - and kept both the live hotspot surface and the one-trim-ahead rehearsal frontier at `0` handle gaps after semantic reuse.
- Main local result:
  - the semantic-handle layer now recovers `5` hotspot families totaling `104874` raw bytes through the projected rank-13 frontier,
  - the refreshed first-pass exact-file frontier is `126583` raw bytes across `6` citation-backed families with `4` semantic-alias-backed rows,
  - the refreshed rehearsal again projects `0` next-frontier handle gaps,
  - and the refreshed execution receipt passes `26/26` checks while proving the `132685`-byte cited trim actually executed on the live archive.

## 2026-03-18 — Research Pass (Fourteenth Canonical Trim + Second-Wave Semantic Frontier Seal)

- Executed the standing cited exact-file compaction frontier on the live tree again instead of leaving the refreshed manifest as rehearsal only:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `135489` raw report bytes from the rev0270 frontier,
  - refreshed `examples/snapshots/rematch_world_benchmark_package_receipt.json`,
  - refreshed `examples/snapshots/archive_report_{hotspot,semantic_handle,compaction_candidate,compaction_gap,compaction_manifest,compaction_rehearsal,compaction_stage,compaction_execution}_receipt.json`,
  - refreshed `artifacts/reports/{artifact_summary.json,artifact_bucket_inventory.json,archive_size_profile_snapshot_20260316.json,archive_size_profile_snapshot_20260316.md}`,
  - and refreshed `docs/ARTIFACT_BUCKETS.md`.
- Reclosed the newly exposed current hotspot and one-trim-ahead frontier without minting any new durable note:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `5` additional aliases for primitive overshoot taxonomy, budget-admissible delta bands, bandwise local slack lead, equiprobable exact target-margin sizing, and local corridor-exit witnesses,
  - updated the targeted validator scripts so the refreshed smaller-tree semantic/candidate/manifest/rehearsal/stage expectations match the live archive,
  - and kept both the live hotspot surface and the one-trim-ahead rehearsal frontier at `0` handle gaps after semantic reuse.
- Main local result:
  - the retained tree now measures `1605` files and `11271101` raw bytes with an approximate revision zip of `3124870` bytes,
  - the live report bucket now measures `328` files and `2152266` raw bytes,
  - the semantic-handle layer now recovers `7` hotspot families totaling `153754` raw bytes,
  - the refreshed first-pass exact-file frontier is `132685` raw bytes across `6` citation-backed families with `5` semantic-alias-backed rows,
  - the refreshed rehearsal again projects `0` next-frontier handle gaps,
  - and the refreshed execution receipt passes `26/26` checks while proving the `135489`-byte cited trim actually executed on the live archive.

## 2026-03-18 — Research Pass (Thirteenth Canonical Trim + Semantic Frontier Reclosure)

- Executed the standing cited exact-file compaction frontier on the live tree again instead of leaving the refreshed manifest as rehearsal only:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `141274` raw report bytes from the rev0269 frontier,
  - refreshed `examples/snapshots/rematch_world_benchmark_package_receipt.json`,
  - refreshed `examples/snapshots/archive_report_{hotspot,semantic_handle,compaction_candidate,compaction_gap,compaction_manifest,compaction_rehearsal,compaction_stage,compaction_execution}_receipt.json`,
  - refreshed `artifacts/reports/{artifact_summary.json,artifact_bucket_inventory.json,archive_size_profile_snapshot_20260316.json,archive_size_profile_snapshot_20260316.md}`,
  - and refreshed `docs/ARTIFACT_BUCKETS.md`.
- Reclosed the newly exposed hotspot and one-trim-ahead frontier without minting any new durable note:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `4` additional aliases for batch-median compromise witnesses, archive-local prefix references, odd hazard staircases, and residual-axis service budgets,
  - updated the targeted validator scripts so the refreshed smaller-tree semantic/candidate/manifest expectations match the live archive,
  - and kept the refreshed next frontier fully handle-covered with `0` projected gaps.
- Main local result:
  - the retained tree now measures `1617` files and `11391313` raw bytes with an approximate revision zip of `3150661` bytes,
  - the live report bucket now measures `340` files and `2287755` raw bytes,
  - the semantic-handle layer now recovers `6` hotspot families totaling `135062` raw bytes,
  - the refreshed first-pass exact-file frontier is `135489` raw bytes across `6` citation-backed families with `4` semantic-alias-backed rows,
  - the refreshed rehearsal again projects `0` next-frontier handle gaps,
  - and the execution receipt passes `26/26` checks while proving the `141274`-byte cited trim actually executed on the live archive.

- Executed the standing cited exact-file compaction frontier on the live tree again instead of leaving the refreshed manifest as rehearsal only:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `147050` raw report bytes from the rev0268 frontier,
  - refreshed `examples/snapshots/rematch_world_benchmark_package_receipt.json`,
  - refreshed `examples/snapshots/archive_report_{hotspot,semantic_handle,compaction_candidate,compaction_gap,compaction_manifest,compaction_rehearsal,compaction_stage,compaction_execution}_receipt.json`,
  - refreshed `artifacts/reports/{artifact_summary.json,artifact_bucket_inventory.json,archive_size_profile_snapshot_20260316.json,archive_size_profile_snapshot_20260316.md}`,
  - and refreshed `docs/ARTIFACT_BUCKETS.md`.
- Reclosed the newly exposed smaller-tree frontier without preserving new bulky report pairs:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `4` additional aliases for transition-budget rewrites, dwell-commitment tariffs, positive-service rank clocks, and benchmark mutation-surface discipline,
  - added one compact inheritor topic at `docs/LIBRARY/topics/filled_rematch_world_benchmarks_should_freeze_copied_contract_state_and_mutate_only_seed_designated_prefixes.md`,
  - and restored zero projected next-frontier handle gaps on the smaller tree.
- Tightened execution-proof durability for future inheritors:
  - updated `scripts/tools/build_archive_report_compaction_execution_receipt.py` so explicit `--pre-package` / `--pre-manifest` reseeding overrides stale self-seeds instead of silently replaying the previous trim.
- Main local result:
  - the refreshed first-pass exact-file frontier settles at `141274` raw bytes across `6` citation-backed families,
  - the refreshed rehearsal again projects `0` next-frontier handle gaps,
  - the semantic-handle layer now carries `5` buffered aliases covering `115909` report-bucket bytes,
  - and the refreshed execution receipt passes `26/26` checks while proving the `147050`-byte cited trim actually executed on the live archive.

- Executed the standing cited exact-file compaction frontier on the live tree again instead of leaving the refreshed manifest as rehearsal only:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `152663` raw report bytes from the rev0267 frontier,
  - refreshed `examples/snapshots/rematch_world_benchmark_package_receipt.json`,
  - refreshed `examples/snapshots/archive_report_hotspot_receipt.json`,
  - refreshed `examples/snapshots/archive_report_semantic_handle_receipt.json`,
  - refreshed `examples/snapshots/archive_report_compaction_candidate_receipt.json`,
  - refreshed `examples/snapshots/archive_report_compaction_gap_receipt.json`,
  - refreshed `examples/snapshots/archive_report_compaction_manifest_receipt.json`,
  - refreshed `examples/snapshots/archive_report_compaction_rehearsal_receipt.json`,
  - refreshed `examples/snapshots/archive_report_compaction_stage_receipt.json`,
  - refreshed `examples/snapshots/archive_report_compaction_execution_receipt.json`,
  - refreshed `artifacts/reports/artifact_summary.json`,
  - refreshed `artifacts/reports/artifact_bucket_inventory.json`,
  - refreshed `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`,
  - and refreshed `docs/ARTIFACT_BUCKETS.md`.
- Reclosed the newly exposed one-trim-ahead handle gap by reusing a standing durable topic instead of minting another note:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with one additional alias for bounded positive-service local interval navigation,
  - updated the targeted validator scripts so the refreshed smaller-tree frontier expectations match the live archive,
  - and kept the next frontier citation-backed with zero projected handle gaps after the eleventh trim.
- Main local result:
  - the refreshed first-pass exact-file frontier settles at `147050` raw bytes across `6` citation-backed families,
  - the refreshed rehearsal again projects `0` next-frontier handle gaps,
  - and the semantic-handle layer now carries `3` buffered aliases covering `73677` report-bucket bytes.

## 2026-03-18 — Research Pass (Eighth Canonical Trim + Fixed-Point Receipt Stabilization)

- Completed the standing cited exact-file trim on the live tree and then finished the proof-layer cleanup needed to make the smaller tree self-consistent again:
  - removed `12` retained report files across `6` families from `artifacts/reports`, reclaiming the standing `188715` raw report bytes from the rev0264 frontier,
  - refreshed `examples/snapshots/archive_report_{hotspot,semantic_handle,compaction_candidate,compaction_gap,compaction_manifest,compaction_rehearsal,compaction_stage,compaction_execution}_receipt.json`,
  - refreshed `examples/snapshots/rematch_world_benchmark_package_receipt.json`,
  - refreshed `artifacts/reports/{artifact_summary.json,artifact_bucket_inventory.json,archive_size_profile_snapshot_20260316.json,archive_size_profile_snapshot_20260316.md}`,
  - and kept the final tree package-ready, PDF-free, scratch-free, and pycache-free.
- Tightened the archive-shaping control layer so repeated rebuilds stop toggling between stale and current states:
  - updated `scripts/report/summarize_artifacts.py` so `artifact_summary.json` preserves its timestamp when the category surface is unchanged,
  - updated `scripts/tools/build_rematch_world_benchmark_package_receipt.py` and `scripts/tools/build_archive_report_hotspot_receipt.py` so volatile size-control outputs are excluded from fixed-point package/hotspot measurement,
  - updated `scripts/tools/build_archive_report_compaction_rehearsal_receipt.py` so projected report-bucket totals use the same filtered control surface as the live package receipt,
  - updated `scripts/tools/build_archive_report_compaction_execution_receipt.py`, `schemas/archive_report_compaction_execution_receipt.schema.json`, and `scripts/test/check_archive_report_compaction_execution_receipt.py` so signed same-pass filtered drift in report-bucket file / pair / byte counts is explicitly represented and validated instead of being treated as a false execution failure.
- Main local result:
  - the retained tree now measures `1676` files and `12157862` raw bytes with an approximate revision zip of `3289697` bytes,
  - the live report bucket now measures `400` files and `3097228` raw bytes,
  - the refreshed first-pass exact-file frontier is `208051` raw bytes across `6` citation-backed families,
  - the refreshed rehearsal again projects `0` next-frontier handle gaps,
  - and the full targeted receipt/validator sweep now passes sequentially on the live tree instead of depending on rebuild order luck.

## 2026-03-18 — Research Pass (Eighth Canonical Trim + Frontier Reclosure)

- Executed the standing cited exact-file compaction frontier on the live tree and then reclosed the freshly exposed smaller-tree frontier with existing durable handles rather than minting any new bulky note:
  - removed `12` retained report files across `6` families from `artifacts/reports`, reclaiming `188715` raw report bytes from the rev0264 manifest,
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `4` additional aliases for overshoot-axis admission profiles, canonical reduced-mean batch summaries, one-burden-axis live promise caching, and mean-projection witness choice,
  - refreshed `examples/snapshots/archive_report_{hotspot,semantic_handle,compaction_candidate,compaction_gap,compaction_manifest,compaction_rehearsal,compaction_stage,compaction_execution}_receipt.json`,
  - refreshed `examples/snapshots/rematch_world_benchmark_package_receipt.json`,
  - refreshed `artifacts/reports/{artifact_summary.json,artifact_bucket_inventory.json,archive_size_profile_snapshot_20260316.json,archive_size_profile_snapshot_20260316.md}`,
  - refreshed `docs/ARTIFACT_BUCKETS.md`,
  - and updated the targeted validator scripts so the new frontier expectations match the live smaller tree.
- Main local result:
  - the retained tree falls to `1681` files and `12175138` raw bytes with an approximate revision zip of `3296136` bytes,
  - the live report bucket falls to `404` files and `3121998` raw bytes,
  - the semantic-handle layer now recovers `5` buffered hotspot families totaling `141792` raw bytes,
  - the refreshed first-pass exact-file frontier is `208051` raw bytes across `6` citation-backed families,
  - the refreshed rehearsal again shows `0` projected second-wave handle gaps,
  - and the execution receipt now passes `24/24` checks while proving the `188715`-byte canonical trim actually left the archive.

## 2026-03-18 — Research Pass (Seventh Canonical Trim + Frontier Reseed)

- Executed the standing cited exact-file compaction frontier on the live tree and then reclosed the next frontier with existing durable handles rather than minting any new bulky note:
  - removed `12` retained report files across `6` families from `artifacts/reports`, reclaiming `202109` raw report bytes from the rev0263 manifest,
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `3` additional aliases for portfolio-confidence ladders, primitive-demand chain holes, and equiprobable exact mean-cost budgeting,
  - refreshed `examples/snapshots/archive_report_{hotspot,semantic_handle,compaction_candidate,compaction_gap,compaction_manifest,compaction_rehearsal,compaction_stage,compaction_execution}_receipt.json`,
  - refreshed `examples/snapshots/rematch_world_benchmark_package_receipt.json`,
  - refreshed `artifacts/reports/{artifact_summary.json,artifact_bucket_inventory.json,archive_size_profile_snapshot_20260316.json,archive_size_profile_snapshot_20260316.md}`,
  - and refreshed `docs/ARTIFACT_BUCKETS.md`.
- Tightened execution-accounting durability:
  - updated `scripts/tools/build_archive_report_compaction_execution_receipt.py`,
  - updated `schemas/archive_report_compaction_execution_receipt.schema.json`,
  - and updated the targeted validator scripts so signed same-pass retained-file drift is representable when it appears instead of being rejected by schema or test assumptions.
- Main local result:
  - the retained tree falls to `1693` files and `12359649` raw bytes with an approximate revision zip of `3323319` bytes,
  - the live report bucket falls to `416` files and `3310575` raw bytes,
  - the semantic-handle layer now recovers `5` buffered hotspot families totaling `156416` raw bytes,
  - the refreshed first-pass exact-file frontier is `188715` raw bytes across `6` citation-backed families,
  - the refreshed rehearsal again shows `0` projected second-wave handle gaps,
  - and the reseeded execution receipt now passes `24/24` checks while proving the `202109`-byte canonical trim actually left the archive.

## 2026-03-18 — Research Pass (Semantic Reclosure + Sixth Canonical Trim)

- Executed the next cited exact-file trim on the live archive and reclosed the smaller-tree frontier without minting any new durable note:
  - removed `12` retained report files across `6` families from `artifacts/reports`
  - reclaimed `226640` raw report bytes from the standing rev0262 frontier
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `6` additional aliases for arrival-floor, width-only service frontier, exact batch wait value, measured decision-packet frontiers, batch-`L2` two-integer summaries, and SG-003 world-emission retirement
- Refreshed the compact archive-shaping stack on the smaller tree:
  - `examples/snapshots/rematch_world_benchmark_package_receipt.json`
  - `examples/snapshots/archive_report_{hotspot,semantic_handle,compaction_candidate,compaction_gap,compaction_manifest,compaction_rehearsal,compaction_stage,compaction_execution}_receipt.json`
  - `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`
  - `artifacts/reports/artifact_summary.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`
- Main local result:
  - the semantic-handle layer now recovers `7` buffered hotspot families covering `232177` report-bucket bytes,
  - the refreshed first-pass exact-file frontier is `202109` raw bytes across `6` citation-backed families,
  - the refreshed rehearsal again projects `0` next-frontier handle gaps,
  - and the new execution receipt passes `24/24` checks while proving the `226640`-byte canonical trim actually left the archive.

## 2026-03-17 — Research Pass (Package Boundary Receipt)

- Added one compact package-boundary receipt for the standing rematch-world benchmark so the inheritor can cite one small proof that the cleaned tree is still chain-consistent, PDF-free, scratch-free, and size-profiled immediately before the next revision zip is cut:
  - `schemas/rematch_world_benchmark_package_receipt.schema.json`
  - `scripts/tools/build_rematch_world_benchmark_package_receipt.py`
  - `examples/snapshots/rematch_world_benchmark_package_receipt.json`
  - `scripts/test/check_rematch_world_benchmark_package_receipt.py`
  - `docs/LIBRARY/topics/cleaned_rematch_world_benchmark_packages_should_carry_one_package_receipt.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` so zip-cut handoff now ends with one compact package receipt after the end-to-end chain receipt passes.
- Main local result:
  - the new package receipt stays small while confirming `7/7` package-boundary checks pass,
  - the tree remains `PDF`-free with `0` active scratch rows and `0` files under `examples/scratch`,
  - the current retained tree profile (measured with the receipt path excluded for stability) is `1744` files, `14318332` raw bytes, and about `3473485` bytes in a revision zip,
  - and `artifacts/reports` remains the main retained growth surface at `500` files and `5568901` raw bytes without adding another report pair.

## 2026-03-17 — Research Pass CCXXIV (Publication Spine Audit + Rebuild Proof)

- Added one compact rematch-world publication-spine audit so the inheritor can trust the retained packet/artifact/receipt bundle by deterministic rebuild instead of by inspection alone:
  - `schemas/rematch_world_benchmark_publication_spine_audit.schema.json`
  - `scripts/tools/audit_rematch_world_benchmark_publication_spine.py`
  - `scripts/report/build_rematch_world_benchmark_publication_spine_audit_example.py`
  - `examples/snapshots/rematch_world_benchmark_publication_spine_audit_receipt.json`
  - `scripts/report/build_rematch_world_benchmark_publication_spine_audit_snapshot.py`
  - `artifacts/reports/rematch_world_benchmark_publication_spine_audit_snapshot_20260316.{md,json}`
  - `scripts/test/check_rematch_world_benchmark_publication_spine_audit.py`
  - `docs/LIBRARY/topics/retained_rematch_world_publication_spine_should_be_rebuild_audited_not_just_opened.md`
- Tightened implementor guidance:
  - retain the concrete publication spine,
  - rerun one deterministic audit over the retained packet/artifact/receipt surfaces before trusting a handoff,
  - and keep the fill patch scratch-only unless drift debugging actually needs it.
- Main local result:
  - the retained publication spine now has one audit receipt proving exact rebuild equality for the compiled artifact, preflight receipt, and publication-bundle receipt,
  - the durable four-object spine remains `59164` bytes and the compact bundle receipt remains `2552` bytes,
  - the new audit receipt adds only a small proof layer over those retained objects,
  - and the retained compiled artifact still stays fully preflight-ready with `0` blockers, `0` forbidden changed paths, and `3` allowed open-ended decision nulls.
- Refreshed lightweight indexes after the pass:
  - `artifacts/reports/schema_inventory.json`
  - `docs/SCHEMA_INVENTORY.md`
  - `artifacts/reports/validator_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`
  - `artifacts/reports/artifact_summary.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`

## 2026-03-17 — Research Pass CCXXIII (Concrete Publication Spine + Retained Artifact Pair)

- Fixed a real rematch-world handoff gap by retaining the durable publication spine concretely instead of only naming it in the bundle receipt:
  - `scripts/report/build_rematch_world_benchmark_publication_spine_examples.py`
  - `examples/snapshots/rematch_world_benchmark_compiled_artifact.json`
  - `examples/snapshots/rematch_world_benchmark_preflight_receipt.json`
  - refreshed `examples/snapshots/rematch_world_benchmark_publication_bundle_receipt.json` so it points at the retained compiled artifact path
  - `scripts/report/build_rematch_world_benchmark_publication_spine_snapshot.py`
  - `artifacts/reports/rematch_world_benchmark_publication_spine_snapshot_20260316.{md,json}`
  - `scripts/test/check_rematch_world_benchmark_publication_spine_examples.py`
  - `docs/LIBRARY/topics/rematch_world_benchmark_publication_spine_should_be_retained_concretely_not_just_named.md`
- Tightened implementor guidance:
  - retain the concrete four-object publication spine (`packet`, `evidence receipt`, `compiled artifact`, `preflight receipt`),
  - treat the publication-bundle receipt as a compact index over those retained objects rather than as a replacement for them,
  - and keep the compiled fill patch scratch-only by default.
- Main local result:
  - the archive previously named the durable publication spine but did not actually retain `compiled artifact` and `preflight receipt` examples,
  - the now-retained four durable objects weigh `59164` bytes total (`3103` packet + `1904` evidence receipt + `52106` compiled artifact + `2051` preflight receipt),
  - the bundle receipt adds only `2552` bytes as a convenience handoff layer,
  - and the retained compiled artifact remains fully preflight-ready with `0` blockers, `0` forbidden changed paths, and `3` allowed open-ended decision nulls.
- Refreshed lightweight indexes after the pass:
  - `artifacts/reports/validator_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`
  - `artifacts/reports/artifact_summary.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`

## 2026-03-17 — Research Pass CCXXII (Publication Bundle + Patch Exit)

- Added one compact rematch-world publication-bundle receipt so the inheritor can compile from packet provenance all the way to a preflight-ready benchmark without retaining the fill patch as a long-term sidecar:
  - `schemas/rematch_world_benchmark_publication_bundle_receipt.schema.json`
  - `scripts/tools/build_rematch_world_benchmark_publication_bundle_receipt.py`
  - `scripts/report/build_rematch_world_benchmark_publication_bundle_example.py`
  - `examples/snapshots/rematch_world_benchmark_publication_bundle_receipt.json`
  - `scripts/report/build_rematch_world_benchmark_publication_bundle_snapshot.py`
  - `artifacts/reports/rematch_world_benchmark_publication_bundle_snapshot_20260316.{md,json}`
  - `scripts/test/check_rematch_world_benchmark_publication_bundle_receipt.py`
  - `docs/LIBRARY/topics/rematch_world_benchmark_publication_should_bundle_packet_provenance_and_preflight_while_letting_the_fill_patch_exit.md`
- Tightened implementor guidance:
  - treat the compiled fill patch as a reconstructible intermediate rather than a default retained artifact,
  - retain packet + evidence receipt + compiled benchmark artifact + preflight receipt as the durable publication spine,
  - and regenerate the patch only when debugging or diff review actually needs it.
- Main local result:
  - the new publication bundle proves `patch_elision_ready=true` on the standing example workflow,
  - the transient patch is `3176` bytes and can now leave the long-term archive once the benchmark artifact and receipts exist,
  - and the compiled example still stays fully preflight-ready with `0` blockers, `0` forbidden changed paths, and `3` allowed open-ended decision nulls.
- Refreshed lightweight indexes after the pass:
  - `artifacts/reports/schema_inventory.json`
  - `docs/SCHEMA_INVENTORY.md`
  - `artifacts/reports/validator_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`
  - `artifacts/reports/artifact_summary.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`

## 2026-03-17 — Research Pass CCXXI (Evidence Receipt + Scratch Provenance Exit)

- Added one compact rematch-world evidence receipt so the inheritor can drop bulky scratch traces without dropping packet provenance:
  - `schemas/rematch_world_benchmark_evidence_receipt.schema.json`
  - `scripts/tools/build_rematch_world_benchmark_evidence_receipt.py`
  - `scripts/report/build_rematch_world_benchmark_evidence_receipt_example.py`
  - `examples/snapshots/rematch_world_benchmark_evidence_receipt.json`
  - `scripts/report/build_rematch_world_benchmark_evidence_receipt_snapshot.py`
  - `artifacts/reports/rematch_world_benchmark_evidence_receipt_snapshot_20260316.{md,json}`
  - `scripts/test/check_rematch_world_benchmark_evidence_receipt.py`
  - `docs/LIBRARY/topics/rematch_world_benchmark_evidence_packets_should_carry_one_compact_scratch_provenance_receipt.md`
- Tightened implementor guidance:
  - keep one tiny evidence packet plus one hashed receipt rather than a wider retained trace family,
  - use the receipt to record which scratch files supported which benchmark sections,
  - and let wider raw traces remain scratch-only once the standard patch and preflight receipt exist.
- Main local result:
  - on inspection, the archive still lacked a retained evidence-receipt surface even though the packet workflow already existed,
  - the new example receipt weighs `1904` bytes against a `3103`-byte packet,
  - packet plus receipt still weighs only `5007` bytes versus the `51329`-byte seed,
  - and strict coverage now spans all `5` world-dependent benchmark sections across `3` scratch sources totaling `552` bytes.
- Refreshed lightweight indexes after the pass:
  - `artifacts/reports/schema_inventory.json`
  - `docs/SCHEMA_INVENTORY.md`
  - `artifacts/reports/validator_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`
  - `artifacts/reports/artifact_summary.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`

## 2026-03-16 — Research Pass CCXX (Seed Scaffold + In-Place World Emission Starter)

- Added one executable seed scaffold for the first endogenous rematch-world benchmark so the next inheritor can start from the right retained object instead of designing a new artifact family:
  - `schemas/rematch_world_benchmark_seed.schema.json`
  - `scripts/report/build_rematch_world_benchmark_seed_example.py`
  - `examples/snapshots/rematch_world_benchmark_seed.json`
  - `scripts/test/check_rematch_world_benchmark_seed.py`
  - `docs/LIBRARY/topics/first_endogenous_rematch_benchmark_should_start_from_one_seed_artifact.md`
- Tightened implementor guidance:
  - regenerate one seed artifact,
  - replace only the world-dependent null telemetry fields in place,
  - and keep `compact_decision_bundle` copied verbatim from the standing decision contract instead of fanning back out into benchmark sidecars.
- Main local result:
  - the archive now has a schema-conforming starter object for the first endogenous rematch-world benchmark,
  - the retained seed adds only `5850` bytes beyond the copied compact decision bundle,
  - and every currently unresolved world-dependent measurement lives in explicit null placeholders rather than in future prose TODOs.
- Refreshed lightweight indexes after the pass:
  - `artifacts/reports/schema_inventory.json`
  - `docs/SCHEMA_INVENTORY.md`
  - `artifacts/reports/validator_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`
  - `artifacts/reports/artifact_summary.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`

## 2026-03-16 — Research Pass CCXIX (World Publication Contract + Post-Canonicalization One-Artifact Target)

- Added one compact rematch-world publication contract so the next inheritor can treat the post-canonicalization SG-003 backlog as one benchmark-emission target instead of fifteen separate note prompts:
  - `schemas/rematch_world_publication_contract.schema.json`
  - `scripts/report/build_rematch_world_publication_contract_snapshot.py`
  - `artifacts/reports/rematch_world_publication_contract_snapshot_20260316.{md,json}`
  - `scripts/test/check_rematch_world_publication_contract.py`
  - `docs/LIBRARY/topics/first_endogenous_rematch_benchmark_should_emit_one_compact_publication_contract.md`
- Tightened implementor guidance:
  - treat `SQ-012` through `SQ-026` as one post-canonicalization benchmark publication contract with six sections,
  - consider the first five world-semantics / comparability questions newly machine-checkable rather than prose-only,
  - and reuse the standing compact decision bundle unchanged inside the first endogenous rematch-world benchmark instead of regrowing per-question fanout.
- Main local result:
  - the archive now has one benchmark-emission target covering `15` open questions (`SQ-012` through `SQ-026`),
  - `5` previously narrative-only world questions are now schema+validator specified,
  - and the final `10` phase-3 questions remain explicitly attached to the standing compact decision bundle rather than to separate retained benchmark subreports.
- Refreshed lightweight indexes after the pass:
  - `artifacts/reports/schema_inventory.json`
  - `docs/SCHEMA_INVENTORY.md`
  - `artifacts/reports/validator_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`
  - `artifacts/reports/artifact_summary.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`

## 2026-03-16 — Research Pass CCXVIII (SG-003 Retirement Rubric + World-Emission Gate)

- Added one compact SG-003 phase-3 retirement rubric so the next inheritor can tell the difference between a solved proxy contract and an actually retired gap:
  - `schemas/rematch_gap_retirement_rubric.schema.json`
  - `scripts/report/build_rematch_gap_retirement_rubric.py`
  - `artifacts/reports/rematch_gap_retirement_rubric_snapshot_20260316.{md,json}`
  - `scripts/test/check_rematch_gap_retirement_rubric.py`
  - `docs/LIBRARY/topics/sg003_phase3_now_needs_world_emission_not_more_proxy_reports.md`
- Tightened implementor guidance:
  - count `SQ-017` through `SQ-026` as schema-specified and proxy-demonstrated, but not yet retired,
  - treat the remaining phase-3 blocker as one endogenous rematch-world benchmark emission rather than another round of proxy-only derivations,
  - and measure future progress by world-emitted delay, winner, and delta contract sections rather than by the number of new subreports.
- Main local result:
  - all `10` phase-3 questions now have an explicit retirement row linking question, assumption, compact contract section, and remaining exit gap,
  - the archive can now say `10 / 10` are schema+validator+proxy covered while `10 / 10` still remain world-benchmark pending,
  - and the retained decision bundle still dominates the old phase-3 surface on size at `35519` bytes versus `188599` bytes across the component reports (`0.188331` share).
- Refreshed lightweight indexes after the pass:
  - `artifacts/reports/schema_inventory.json`
  - `docs/SCHEMA_INVENTORY.md`
  - `artifacts/reports/validator_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`
  - `artifacts/reports/artifact_summary.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`

## 2026-03-16 — Research Pass CCXVII (Compact Decision Bundle + Phase-3 Fanout Cut)

- Added one compact phase-3 rematch decision-contract bundle so the next inheritor can answer `SQ-017` through `SQ-026` from one machine-checkable surface instead of keeping separate winner, delay, and delta artifacts:
  - `schemas/rematch_decision_contract.schema.json`
  - `scripts/report/build_rematch_decision_contract_snapshot.py`
  - `artifacts/reports/rematch_decision_contract_snapshot_20260316.{md,json}`
  - `scripts/test/check_rematch_decision_contract.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_publish_one_compact_decision_contract_bundle.md`
- Tightened implementor guidance:
  - treat the final SG-003 tranche as one compact decision surface with three sections only: delay contract, winner contract, and delta contract,
  - keep the compact bundle as the long-term retained artifact and demote richer per-question expansions to temporary scratch unless they become standing evidence,
  - and prefer extortion-indexed live-contender sets, panel-level winner triage rows, and topology-preserving delta anchors over bulky crossover tables or dense multi-delta grids.
- Main local result:
  - the current phase-3 surface spans `7` component JSON reports totaling `188599` bytes,
  - the compact decision bundle covers all `10` phase-3 questions in one machine-checkable JSON at `35519` minified bytes (`0.188331` share of the component-byte total),
  - the bundle keeps `3` delay/extortion rows, `9` winner-triage rows, and `20` delta-anchor rows,
  - and validator coverage now checks both schema validity and source-consistency for the bundled contract.
- Refreshed lightweight indexes after the pass:
  - `artifacts/reports/schema_inventory.json`
  - `docs/SCHEMA_INVENTORY.md`
  - `artifacts/reports/validator_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`
  - `artifacts/reports/artifact_summary.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`

## 2026-03-16 — Research Pass CCXVI (SG-003 Collapse Order + Compile Health)

- Added one inheritor-facing priority snapshot so the next implementor can collapse the largest open rematch backlog without regrowing the archive:
  - `scripts/report/build_inheritor_priority_snapshot.py`
  - `artifacts/reports/inheritor_priority_snapshot_20260316.{md,json}`
  - `docs/LIBRARY/topics/rematch_gap_sg003_should_be_retired_in_three_compact_layers.md`
- Tightened implementor guidance:
  - treat `SG-003` as the backlog-collapse target because it carries `47` dependent open entries (`23` assumptions + `24` questions),
  - retire it in three compact layers: canonicalization contract, world telemetry/comparability contract, then compact top-gap decision contract,
  - and prefer schema/report fields over bulky rerun tables for the final ten machine-checkable decision questions.
- Fixed one inherited repo-health issue:
  - `scripts/test/check_scripts_compile.py` now compiles Python files through short temporary `.pyc` targets instead of relying on adjacent `__pycache__` writes,
  - so ultra-long script names no longer trigger false path-length failures during syntax checks.
- Main local result:
  - `SG-003` now reads as one ordered execution ladder instead of an undifferentiated rematch backlog,
  - the final SG-003 tranche already contains `10` questions phrased as minimal machine-checkable contracts,
  - and the compile check now passes locally (`scripts-compile: ok`) rather than failing on filesystem path budget.
- Refreshed lightweight indexes after the pass:
  - `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`
  - `artifacts/reports/artifact_summary.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`

## 2026-03-16 — Research Pass CCXV (Archive Footprint Profile + Scratch Discipline)

- Added one measured archive-footprint profile so future inheritors can see which retained surfaces actually dominate archive growth instead of guarding only against external reading packs:
  - `scripts/report/build_archive_size_profile_snapshot.py`
  - `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`
  - `artifacts/process/scratch_manifest.json`
- Tightened archive guidance:
  - keep external literature citation-first and reacquire PDFs only as temporary scratch,
  - treat `artifacts/process/scratch_manifest.json` as the retained handoff index for any scratch that must survive a session boundary,
  - prefer one canonical machine-readable artifact plus a short inheritor note when a pass does not add a standing contract or validator,
  - and refresh artifact summary / bucket inventory after archive-shaping edits so footprint drift stays visible.
- Main local result:
  - the current retained tree holds `1518` files at `14932644` raw bytes (`14.241` MiB) and compresses to about `3486699` bytes (`3.325` MiB) in a revision zip,
  - the `artifacts/reports` bucket is now the main retained growth surface at `5287531` raw bytes (`5.043` MiB),
  - `213` JSON+MD report pairs consume `5067253` raw bytes (`4.833` MiB), which is `0.95834` share of the reports bucket,
  - and the prior PDF compaction already removed `47925095` bytes (`45.705` MiB), so the next archive-size risk is internal report/log fanout rather than literature blobs.
- Refreshed lightweight indexes after the footprint pass:
  - `artifacts/reports/artifact_summary.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`


## 2026-03-16 — Research Pass CCXIV (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Geometric-Arrival Live Burden-Axis Law)

- Added one exact live burden-axis law so future inheritors can collapse hold cost and promised realized margin to a single same-deadline stateless live admission coordinate instead of caching a two-dimensional cost-margin table:
  - `scripts/analysis/geometric_arrival_live_burden_axis_law.py`
  - `scripts/report/build_geometric_arrival_live_burden_axis_law_snapshot.py`
  - `artifacts/reports/geometric_arrival_live_burden_axis_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_geometric_arrival_live_burden_axis_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_cache_same_deadline_live_promises_on_one_burden_axis.md`
- Tightened implementation guidance:
  - for same-deadline stateless live control, collapse hold cost and promised realized margin to `b_live = 0` when `m = 0`, else `hold_cost / p + m / (1 - (1 - p)^floor((H + 1) / 2))`,
  - preserve a state-specific promise exactly when `state_prefix_bits / (n(n + 1)) >= b_live`,
  - preserve the all-state seven-bit guardrail exactly when `7 / (n(n + 1)) >= b_live`,
  - treat equal-burden contexts as exact substitutes for admission,
  - and keep the odd/even deadline pairing because `2j - 1` and `2j` induce the same burden map.
- Main local result:
  - validated `783360` state contexts and `5120` universal contexts,
  - observed `277046` admitted and `506314` rejected nonnegative state contexts,
  - observed `1782` admitted and `3338` rejected nonnegative universal contexts,
  - validated `141984` state and `928` universal equal-burden member-equivalence checks,
  - confirmed monotone burden ladders on all `39168` audited state ladders and all `256` audited universal ladders, with strict drops on `36008` state ladders and `236` universal ladders,
  - and observed that the audited `20` raw cost-margin contexts collapse to between `15` and `17` burden classes per hazard/deadline pair, with at most `4` raw contexts sharing one exact burden class.
- Refreshed lightweight indexes after the new pass:
  - `artifacts/reports/validator_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/repro_bundle_index.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`


## 2026-03-16 — Research Pass CCXIII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Geometric-Arrival Live Dominance Frontier Law)

- Added one exact live dominance-frontier law so future inheritors can compress positive same-deadline stateless live policy tables to Pareto boundaries instead of keeping dense interior grids:
  - `scripts/analysis/geometric_arrival_live_dominance_frontier_law.py`
  - `scripts/report/build_geometric_arrival_live_dominance_frontier_law_snapshot.py`
  - `artifacts/reports/geometric_arrival_live_dominance_frontier_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_geometric_arrival_live_dominance_frontier_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_compress_positive_same_deadline_live_policies_by_dominance_frontiers.md`
- Tightened implementation guidance:
  - for positive realized margins, same-deadline live promise safety is monotone under favorable coordinatewise dominance,
  - more shared-prefix bits, higher arrival hazard, and longer nominal deadline only help,
  - larger batch length, larger hold cost, and larger promised margin only hurt,
  - state identity reduces exactly to shared-prefix bits for this admission surface,
  - and the all-state seven-bit guardrail is just the same dominance law evaluated at `state_prefix_bits = 7`.
- Main local result:
  - validated exact prefix-bit reduction on all `626688` audited state contexts and all `4096` audited universal contexts,
  - observed `120374` admitted and `506314` rejected state contexts,
  - observed `758` admitted and `3338` rejected universal contexts,
  - validated coordinatewise dominance certificates on `65536` prefix steps, `60928` batch steps, `52224` arrival steps, `52224` hold-cost steps, `52224` margin steps, and `60928` deadline steps,
  - and observed strict frontier movement on `1368` prefix gains, `6594` batch penalties, `2324` arrival gains, `1694` hold-cost penalties, `3830` margin penalties, and `325` deadline gains.
- Refreshed lightweight indexes after the new pass:
  - `artifacts/reports/validator_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/repro_bundle_index.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`


## 2026-03-16 — Research Pass CCXII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Geometric-Arrival Live Hazard-Staircase Law)

- Added one exact live hazard-staircase law so future inheritors can compile same-deadline stateless live positive-promise budgeting into a monotone hazard ladder instead of re-solving minimum deadlines from scratch at every arrival estimate:
  - `scripts/analysis/geometric_arrival_live_hazard_staircase_law.py`
  - `scripts/report/build_geometric_arrival_live_hazard_staircase_law_snapshot.py`
  - `artifacts/reports/geometric_arrival_live_hazard_staircase_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_geometric_arrival_live_hazard_staircase_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_budget_same_deadline_live_deadlines_as_odd_hazard_staircases.md`
- Tightened implementation guidance:
  - for fixed state, batch, hold cost, and positive realized margin, the same-deadline live schedule class is monotone in arrival hazard under `impossible < asymptotic_only < finite`,
  - once a finite minimum deadline appears, it stays finite for every larger hazard,
  - every finite minimum same-deadline live deadline lies on the odd ladder `1, 3, 5, ...`,
  - among those finite values the minimum deadline is nonincreasing as hazard rises,
  - and the all-state seven-bit guardrail obeys the same hazard staircase after replacing state prefix bits by `7`.
- Main local result:
  - validated `19584` state hazard ladders covering `156672` state contexts and `128` universal ladders covering `1024` universal contexts,
  - confirmed monotone class progression on all audited ladders,
  - confirmed suffix-finite structure on all audited ladders,
  - confirmed that all `32462` audited finite state minima and all `204` audited finite universal minima stayed odd,
  - observed deadline drops on `4128` state ladders and `26` universal ladders,
  - observed `8462` state and `54` universal deadline-drop events,
  - and observed class-improvement ladders on `2754` audited state ladders and `18` audited universal ladders.
- Refreshed lightweight indexes after the new pass:
  - `artifacts/reports/validator_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/repro_bundle_index.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`


## 2026-03-16 — Research Pass CCXI (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Geometric-Arrival Live Arrival-Floor Law)

- Added one exact live arrival-floor law so future inheritors can treat same-deadline stateless live positive-promise admission as a one-dimensional hazard threshold instead of re-solving full promise frontiers online:
  - `scripts/analysis/geometric_arrival_live_arrival_floor_law.py`
  - `scripts/report/build_geometric_arrival_live_arrival_floor_law_snapshot.py`
  - `artifacts/reports/geometric_arrival_live_arrival_floor_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_geometric_arrival_live_arrival_floor_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_gate_positive_same_deadline_live_promises_by_arrival_floor.md`
- Tightened implementation guidance:
  - for fixed batch, hold cost, positive margin promise, and nominal live deadline `H`, the raw positive branch `(1 - (1 - p)^floor((H + 1) / 2)) * (state_prefix_bits / (n(n + 1)) - hold_cost / p)` is nondecreasing in `p`,
  - so positive same-deadline live promise admission is upward-closed in arrival hazard,
  - a positive continuous arrival floor exists exactly when the certain-arrival full-capture value `state_prefix_bits / (n(n + 1)) - hold_cost` still covers the promised margin,
  - the one-effective-tick case collapses to the exact threshold `p >= (hold_cost + margin_floor) / (state_prefix_bits / (n(n + 1)))`,
  - and the all-state guardrail uses the same law with `state_prefix_bits = 7`.
- Main local result:
  - validated `156672` state contexts and `1024` universal contexts,
  - validated `1253376` state derivative certificates and `8192` universal derivative certificates,
  - confirmed single-crossing upward-closed arrival admission on all `156672` audited state ladders and all `1024` audited universal ladders,
  - observed `39968` state contexts and `256` universal contexts with a positive continuous arrival floor,
  - observed `116704` impossible state contexts and `768` impossible universal contexts,
  - validated `39168` state and `256` universal one-tick closed-form floor checks,
  - and observed strict audited-ladder growth on `110912` state ladders and `704` universal ladders.
- Refreshed lightweight indexes after the new pass:
  - `artifacts/reports/validator_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/repro_bundle_index.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`


## 2026-03-16 — Research Pass CCX (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Geometric-Arrival Live Deadline Formula Law)

- Added one exact direct live-deadline formula law so future inheritors can solve the minimum same-deadline stateless live deadline from primitives instead of first materializing an intermediate blind-timeout object:
  - `scripts/analysis/geometric_arrival_live_deadline_formula_law.py`
  - `scripts/report/build_geometric_arrival_live_deadline_formula_law_snapshot.py`
  - `artifacts/reports/geometric_arrival_live_deadline_formula_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_geometric_arrival_live_deadline_formula_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_solve_same_deadline_live_minima_from_one_closed_form.md`
- Tightened implementation guidance:
  - let `delta = p * state_prefix_bits / (n(n + 1)) - hold_cost` and `alpha = p * margin_floor / delta` when `delta > 0`,
  - the minimum same-deadline live deadline is `1` at zero floor,
  - `1` when `p = 1` and `alpha <= 1`,
  - `2 * ceil(log(1 - alpha) / log(1 - p)) - 1` when `0 < alpha < 1` and `p < 1`,
  - asymptotic-only when `alpha = 1` with `p < 1`,
  - impossible when `delta <= 0` or `alpha > 1`,
  - and the all-state guardrail uses the same formula with `state_prefix_bits = 7`.
- Main local result:
  - validated `146880` state contexts and `960` universal contexts,
  - matched the earlier live minimum-deadline outputs on all `146880` audited state contexts and all `960` audited universal contexts,
  - validated `21046` state boundary checks and `132` universal boundary checks,
  - observed positive schedule mix `16868` finite, `409` asymptotic-only, and `100227` impossible across the audited state grid,
  - observed positive universal mix `106` finite, `3` asymptotic-only, and `659` impossible,
  - and confirmed all finite positive minima remained odd.
- Refreshed lightweight indexes after the new pass:
  - `artifacts/reports/validator_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/repro_bundle_index.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`


## 2026-03-16 — Research Pass CCIX (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Geometric-Arrival Live Prefix-Floor Law)

- Added one exact live prefix-floor law so future inheritors can admit same-deadline stateless live realized-margin promises from one integer threshold comparison instead of searching timeout or margin tables online:
  - `scripts/analysis/geometric_arrival_live_prefix_floor_law.py`
  - `scripts/report/build_geometric_arrival_live_prefix_floor_law_snapshot.py`
  - `artifacts/reports/geometric_arrival_live_prefix_floor_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_geometric_arrival_live_prefix_floor_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_admit_positive_same_deadline_live_promises_by_prefix_floor.md`
- Tightened implementation guidance:
  - for positive realized margin floors, same-deadline stateless live control preserves the original promise exactly when `state_prefix_bits >= ceil(n(n + 1) * (hold_cost / p + m / (1 - (1 - p)^floor((H + 1) / 2))))`,
  - the all-state seven-bit live guarantee survives exactly when that same required prefix floor is at most `7`,
  - zero-margin floors require `0` prefix bits because immediate close is already safe,
  - and deadlines `2j - 1` and `2j` have identical positive live prefix floors.
- Main local result:
  - validated `783360` state contexts and `5120` universal contexts,
  - observed `120374` admissible and `506314` rejected positive state contexts,
  - observed `758` admissible and `3338` rejected positive universal contexts,
  - confirmed odd-even prefix-floor plateaus on `313344` state deadline pairs and `2048` universal pairs,
  - and observed strict odd-rung prefix-floor drops on `55386` state ladders and `362` universal ladders.
- Refreshed lightweight indexes after the new pass:
  - `artifacts/reports/validator_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/repro_bundle_index.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`


## 2026-03-16 — Research Pass CCVIII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Geometric-Arrival Live Margin Ceiling Law)

- Added one exact live margin ceiling law so future inheritors can quote same-deadline stateless live realized-margin promises directly from batch, hazard, cost, and nominal deadline without re-solving timeout or batch frontiers online:
  - `scripts/analysis/geometric_arrival_live_margin_ceiling_law.py`
  - `scripts/report/build_geometric_arrival_live_margin_ceiling_law_snapshot.py`
  - `artifacts/reports/geometric_arrival_live_margin_ceiling_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_geometric_arrival_live_margin_ceiling_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_quote_same_deadline_live_promises_by_margin_ceiling.md`
- Tightened implementation guidance:
  - same-deadline stateless live control preserves original realized margin promises exactly up to `max(0, (1 - (1 - p)^floor((H + 1) / 2)) * (state_prefix_bits / (n(n + 1)) - hold_cost / p))`,
  - equivalently, the live margin ceiling is exactly the better-of-close-or-blind value at effective blind horizon `floor((H + 1) / 2)`,
  - if the raw effective blind value is nonpositive then only the zero-margin promise survives because immediate close is the unique safe nonnegative option,
  - and deadlines `2j - 1` and `2j` have identical nonnegative live margin ceilings.
- Main local result:
  - validated `156672` state contexts and `1024` universal contexts,
  - validated `313344` state boundary checks and `2048` universal boundary checks,
  - observed `87280` positive-ceiling and `69392` zero-only state contexts,
  - observed `560` positive-ceiling and `464` zero-only universal contexts,
  - and confirmed odd-even margin-ceiling plateaus on `78336` state deadline pairs and `512` universal pairs.
- Refreshed lightweight indexes after the new pass:
  - `artifacts/reports/validator_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/repro_bundle_index.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`


## 2026-03-16 — Research Pass CCVII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Geometric-Arrival Live Hold-Cost Ceiling Law)

- Added one exact live hold-cost ceiling law so future inheritors can decide whether a same-deadline stateless live wait is still promise-safe from one threshold comparison instead of re-solving timeout or batch frontiers online:
  - `scripts/analysis/geometric_arrival_live_hold_cost_ceiling_law.py`
  - `scripts/report/build_geometric_arrival_live_hold_cost_ceiling_law_snapshot.py`
  - `artifacts/reports/geometric_arrival_live_hold_cost_ceiling_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_geometric_arrival_live_hold_cost_ceiling_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_budget_positive_same_deadline_live_waits_by_hold_cost_ceiling.md`
- Tightened implementation guidance:
  - for positive margin floors, same-deadline live waiting is promise-safe exactly while `hold_cost <= p * (state_prefix_bits / (n(n + 1)) - m / (1 - (1 - p)^floor((H + 1) / 2)))`,
  - equivalently, the live hold-cost ceiling is exactly the blind-commit hold-cost ceiling at effective horizon `floor((H + 1) / 2)`,
  - negative ceilings mean the positive promise is impossible even at zero hold cost,
  - zero-margin floors are a deliberate degenerate case where the live hold-cost ceiling is unbounded because immediate close is already safe,
  - and deadlines `2j - 1` and `2j` have identical positive live hold-cost ceilings.
- Main local result:
  - validated `195840` state contexts and `1280` universal contexts,
  - validated `199482` state boundary checks and `1294` universal boundary checks,
  - observed `42810` feasible and `113862` impossible positive state contexts,
  - observed `270` feasible and `754` impossible positive universal contexts,
  - and confirmed odd-even hold-cost plateaus on `78336` state deadline pairs and `512` universal pairs.
- Refreshed lightweight indexes after the new pass:
  - `artifacts/reports/validator_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/repro_bundle_index.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`


## 2026-03-16 — Research Pass CCVI (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Geometric-Arrival Live Minimum-Deadline Law)

- Added one exact minimum live-deadline law so future inheritors can provision same-deadline stateless live controllers directly from a batch promise without hand-converting through effective-horizon reasoning at runtime:
  - `scripts/analysis/geometric_arrival_live_minimum_deadline_law.py`
  - `scripts/report/build_geometric_arrival_live_minimum_deadline_law_snapshot.py`
  - `artifacts/reports/geometric_arrival_live_minimum_deadline_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_geometric_arrival_live_minimum_deadline_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_budget_positive_same_deadline_live_promises_on_odd_deadlines.md`
- Tightened implementation guidance:
  - for positive margin floors with finite blind minimum timeout `K`, the minimum same-deadline live deadline is exactly `2K - 1`,
  - every finite positive same-deadline live promise therefore enters on the odd ladder `1, 3, 5, ...`,
  - every even deadline `2j` is economically redundant for positive promise admission because it duplicates `2j - 1`,
  - positive asymptotic-only and impossible blind schedules have no finite same-deadline live deadline,
  - and zero-margin floors collapse to a one-tick live deadline because immediate close is already safe.
- Main local result:
  - validated `146880` state contexts and `960` universal contexts,
  - observed `16868` finite, `409` asymptotic-only, and `100227` impossible positive state contexts,
  - observed `106` finite, `3` asymptotic-only, and `659` impossible positive universal contexts,
  - confirmed that all `16868` finite positive state minima and all `106` finite positive universal minima are odd,
  - and confirmed odd/even frontier duplication on `16868` state minimum-frontier pairs and `106` universal minimum-frontier pairs.
- Refreshed lightweight indexes after the new pass:
  - `artifacts/reports/validator_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/repro_bundle_index.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`
- Fixed one stale report-builder syntax break uncovered during hygiene:
  - `scripts/report/build_geometric_arrival_deadline_inflation_law_snapshot.py`
  - regenerated `artifacts/reports/geometric_arrival_deadline_inflation_law_snapshot_20260316.{md,json}`


## 2026-03-16 — Research Pass CCV (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Geometric-Arrival Live-Batch-Cap Law)

- Added one exact live batch-cap law so future inheritors can size same-deadline stateless live controllers directly from the nominal deadline instead of converting through promise timeout tables by hand:
  - `scripts/analysis/geometric_arrival_live_batch_cap_law.py`
  - `scripts/report/build_geometric_arrival_live_batch_cap_law_snapshot.py`
  - `artifacts/reports/geometric_arrival_live_batch_cap_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_geometric_arrival_live_batch_cap_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_cap_same_deadline_stateless_live_batches_by_effective_horizon.md`
- Tightened implementation guidance:
  - for positive margin floors, nominal live deadline `H` has exactly the blind-commit batch cap at effective horizon `floor((H + 1) / 2)`,
  - equivalently, the largest positive promise-safe batch is the largest `n` with `n(n+1) <= p * state_prefix_bits / (hold_cost + p * m / (1 - (1 - p)^floor((H + 1) / 2)))`,
  - zero-margin floors are a deliberate degenerate case where every batch is safe because immediate close already meets the floor,
  - and deadlines `2j - 1` and `2j` have identical positive live batch caps.
- Main local result:
  - validated `97920` state cap contexts and `640` universal contexts,
  - validated `168900` state frontier checks and `1100` universal frontier checks,
  - observed `70980` feasible and `7356` impossible positive state contexts,
  - observed `460` feasible and `52` impossible positive universal contexts,
  - and confirmed odd-even cap plateaus on `48960` state deadline pairs and `320` universal pairs.
- Refreshed lightweight indexes after the new pass:
  - `artifacts/reports/validator_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/repro_bundle_index.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`


## 2026-03-16 — Research Pass CCIV (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Geometric-Arrival Effective-Horizon Law)

- Added one exact effective-horizon law so future inheritors can budget same-deadline stateless live controllers by a blind-commit equivalent instead of carrying reserve, drift, and inflation corrections separately:
  - `scripts/analysis/geometric_arrival_effective_horizon_law.py`
  - `scripts/report/build_geometric_arrival_effective_horizon_law_snapshot.py`
  - `artifacts/reports/geometric_arrival_effective_horizon_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_geometric_arrival_effective_horizon_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_budget_stateless_live_deadlines_by_effective_blind_horizon.md`
- Tightened planning guidance:
  - for positive promises, nominal live deadline `H` preserves exactly the blind-commit promises with minimum timeout `K <= floor((H + 1) / 2)`,
  - for nonnegative margin floors, same-deadline stateless live control is exactly as promise-safe as choosing the better of immediate close and blind commit with horizon `floor((H + 1) / 2)`,
  - deadlines `2j - 1` and `2j` are promise-equivalent because both expose effective blind horizon `j`,
  - and every second nominal deadline tick is dead reserve when exact positive-promise preservation is the objective.
- Main local result:
  - validated `587520` state panels and `3840` universal panels,
  - observed preserved original-margin promises on `204648` state panels and `1316` universal panels,
  - and confirmed odd-even deadline-pair equivalence on `293760` state panels and `1920` universal panels.
- Refreshed lightweight indexes after the new pass:
  - `artifacts/reports/validator_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/repro_bundle_index.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`

## 2026-03-16 — Research Pass CCIII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Geometric-Arrival Deadline-Inflation Law)

- Added one exact deadline-compensation law so future inheritors can repair stateless live reoptimization back to blind-commit value without another online solve:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_deadline_inflation_law.py`
  - `scripts/report/build_geometric_arrival_deadline_inflation_law_snapshot.py`
  - `artifacts/reports/geometric_arrival_deadline_inflation_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_geometric_arrival_deadline_inflation_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_compensate_stateless_live_reoptimization_by_deadline_inflation.md`
- Tightened planning guidance:
  - for any finite schedule with minimum blind-commit timeout `K`, the exact horizon repair is `K - 1` extra ticks,
  - equivalently, `live(H + K - 1) = blind_commit(H)` for every positive blind-commit horizon `H`,
  - so reserve tax, deficit tax, and deadline inflation are just three views of the same control correction,
  - and one-tick schedules remain the unique zero-inflation class.
- Main local result:
  - validated the exact compensation identity across the audited finite state grid and the audited finite universal grid,
  - covering `223024` finite state blind-horizon panels,
  - with `33424` positive-inflation state panels and `189600` zero-inflation one-tick state panels.
- Refreshed lightweight indexes after the new pass:
  - `artifacts/reports/validator_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/repro_bundle_index.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`

## 2026-03-16 — Research Pass CCII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Geometric-Arrival Live-Reoptimization Deficit Law)

- Added one exact same-horizon deficit law so future inheritors can price how much blind-commit value is lost when a batch promise is executed by stateless live miss-by-miss reoptimization instead:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_live_reoptimization_deficit_law.py`
  - `scripts/report/build_geometric_arrival_live_reoptimization_deficit_law_snapshot.py`
  - `artifacts/reports/geometric_arrival_live_reoptimization_deficit_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_geometric_arrival_live_reoptimization_deficit_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_price_stateless_live_reoptimization_as_a_geometric_promise_deficit.md`
- Tightened planning guidance:
  - for finite schedules with `H >= K`, same-horizon blind-commit minus live-reoptimized value is exactly a geometric deficit,
  - the preserved share at the boundary checkpoint is exactly `p / (1 - (1 - p)^K)`,
  - one-tick promises are the only finite schedules with zero same-horizon deficit,
  - and multi-tick same-horizon deficits are largest at the boundary then decay geometrically as extra horizon accumulates.
- Main local result:
  - validated `783360` state panels and `5120` universal panels,
  - observed `25686` positive state deficit panels and `162` positive universal deficit panels,
  - with zero same-horizon deficit exactly on the `189600` one-tick state panels and `1200` one-tick universal panels in the audited grid.
- Refreshed lightweight indexes after the new pass:
  - `artifacts/reports/validator_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/repro_bundle_index.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`

## 2026-03-16 — Research Pass CCI (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Geometric-Arrival Time-Consistency Law)

- Added one exact time-consistency law clarifying which blind-commit margin promises survive live miss-by-miss reoptimization without drift:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_time_consistency_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_time_consistency_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_time_consistency_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_time_consistency_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_not_treat_multi_tick_promises_as_locally_time_consistent.md`
- Tightened planning guidance:
  - finite schedules are locally time-consistent under live reoptimization iff the minimum blind-commit timeout is exactly one tick,
  - every finite multi-tick promise (`K > 1`) already drifts at the boundary checkpoint `H = K` under live countdown semantics,
  - those same multi-tick promises first recover their original blind-commit margin only at `H = 2K - 1`,
  - so implementors must explicitly choose between blind commit, accepted drift under live local control, or richer promise-slack state.
- Refreshed lightweight indexes after the new pass:
  - `artifacts/reports/validator_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/repro_bundle_index.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`

## 2026-03-16 — Research Pass CC (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Geometric-Arrival Countdown-Reserve Law)

- Added one exact live-countdown reserve law so future inheritors can separate blind-commit deadline value from the smaller usable wait window actually exposed by repeated checkpoint reoptimization:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_countdown_reserve_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_countdown_reserve_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_countdown_reserve_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_countdown_reserve_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_live_countdowns_as_usable_wait_windows_plus_dead_reserve.md`
- Tightened planning guidance:
  - if `K` is the minimum blind-commit timeout meeting the original margin floor, then a live countdown policy that re-checks after every miss has exact value `F(max(H - K + 1, 0))` at remaining horizon `H`, where `F` is the earlier fixed-timeout wait-value law,
  - the last `K - 1` ticks therefore act as a dead reserve under live reoptimization rather than economically usable wait time,
  - `H >= K` is enough to justify a local continue decision under blind-commit semantics,
  - but preserving the original ex-ante margin promise under live reoptimization instead requires the stricter finite-schedule guardrail `H >= 2K - 1`,
  - and the same reserve interpretation holds under the all-state seven-bit lower envelope.
- Main local result:
  - all `153 × 8 × 4 × 4 × 5 × 6 = 587520` audited state/batch/probability/cost/margin/remaining-horizon panels matched the exact live-countdown reserve law,
  - all `8 × 4 × 4 × 5 × 6 = 3840` audited universal panels matched the seven-bit reserve law,
  - the audited state schedule mix stayed `27878` finite, `409` asymptotic-only, and `69633` impossible,
  - among audited state panels, live countdown continued on `159680` panels and exhibited promise drift on `6476` of those panels,
  - among audited universal panels, live countdown continued on `1010` panels and exhibited promise drift on `42` of those panels,
  - and the first sharp drift witness already appears at `(state_prefix_bits=7, n=1, p=1/4, c=1/20, m=1, H=2)`, where blind commit is worth `231/160` bits but live reoptimization exposes only one usable tick worth `33/40` bits.
- Refreshed lightweight indexes after the new pass:
  - `artifacts/reports/validator_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/repro_bundle_index.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`

## 2026-03-16 — Research Pass CXCIX (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Geometric-Arrival Deadline-Countdown Law)

- Added one exact remaining-horizon countdown law so future inheritors can run live shared-state equiprobable exact batches by a precomputed deadline threshold instead of re-solving after every empty tick:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_deadline_countdown_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_deadline_countdown_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_deadline_countdown_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_deadline_countdown_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_run_positive_batches_by_precomputed_remaining_horizon_countdowns.md`
- Tightened planning guidance:
  - at any checkpoint with `H` ticks remaining, continue exactly when `(1 - (1 - p)^H) * (state_prefix_bits / (n(n+1)) - c / p) >= m` for the current realized margin floor `m`,
  - equivalently, precompute the earlier minimum timeout `K` for the batch promise and continue iff `H >= K`,
  - elapsed no-arrival streak length never changes that threshold under the current geometric-arrival model,
  - asymptotic-only schedules never become finite just by surviving misses,
  - and the all-state guardrail is the same countdown rule with `state_prefix_bits = 7`.
- Main local result:
  - all `153 × 8 × 4 × 4 × 5 × 3 × 6 = 1762560` audited state/batch/probability/cost/margin/elapsed-streak/remaining-horizon panels matched the exact countdown threshold,
  - all `8 × 4 × 4 × 5 × 3 × 6 = 11520` audited universal countdown panels matched the seven-bit lower-envelope rule,
  - the audited state schedule mix stayed `27878` finite, `409` asymptotic-only, and `69633` impossible,
  - the audited state decision mix on the countdown grid was `479040` continue vs `1283520` close,
  - the audited universal decision mix was `3030` continue vs `8490` close,
  - and strict horizon growth appeared on `3260` audited state ladders and `20` universal ladders while no ladder ever moved downward with more remaining time.
- Refreshed lightweight indexes after the new pass:
  - `artifacts/reports/validator_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/repro_bundle_index.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`

## 2026-03-16 — Research Pass CXCVIII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Geometric-Arrival Checkpoint-Extension Law)

- Added one exact checkpoint-extension law so future inheritors can evaluate live miss-streak continuation without mistaking elapsed empty ticks for new economic evidence:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_checkpoint_extension_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_checkpoint_extension_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_checkpoint_extension_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_checkpoint_extension_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_not_panic_close_positive_batches_after_geometric_miss_streaks.md`
- Tightened planning guidance:
  - conditioned on any prior no-arrival streak, the value of granting `H` more ticks is exactly the same horizon-only closed form as starting fresh with timeout `H`,
  - the conditional value of granting one more tick right now is always `p * state_prefix_bits / (n(n+1)) - c`,
  - the all-state guardrail is the same checkpoint rule with `state_prefix_bits = 7`,
  - ex-ante from the start of waiting, the value of scheduling one extra future tick decays geometrically as `(1 - p)^T * (p * state_prefix_bits / (n(n+1)) - c)`,
  - and positive batches therefore should not be panic-closed merely because they have already survived a miss streak; only exhausted horizon or changed hazard/cost/state should force re-evaluation.
- Main local result:
  - all `153 × 8 × 4 × 4 × 6 × 6 = 705024` audited state/batch/probability/cost/elapsed-streak/extension-horizon panels matched the exact checkpoint-extension law,
  - all `705024` corresponding state panels also respected the seven-bit universal lower-envelope checkpoint guardrail,
  - all `153 × 8 × 4 × 4 × 6 = 117504` audited checkpoint one-more-tick panels were elapsed-streak invariant,
  - all `117504` audited ex-ante extra-tick increments matched the exact timeout-difference identity,
  - all `97920` adjacent extra-tick increments decayed by the exact failure factor `(1 - p)`,
  - the audited state one-more-tick sign mix on the current grid was `10910` positive, `8574` negative, and `100` zero,
  - and the audited universal one-more-tick sign mix was `10710` positive, `8874` negative, and `0` zero.

## 2026-03-16 — Research Pass CXCVII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Geometric-Arrival Timeout-Batch-Cap Law)

- Added one exact fixed-timeout batch-cap law so future inheritors can recover the largest admissible shared-state equiprobable exact batch directly from the timeout budget they will actually run:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_batch_cap_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_batch_cap_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_batch_cap_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_batch_cap_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_cap_batches_directly_from_fixed_timeouts_and_margin_floors.md`
- Tightened planning guidance:
  - under fixed timeout `T`, realized expected net wait value is exactly `(1 - (1 - p)^T) * (state_prefix_bits / (n(n+1)) - c / p)` whenever `p > 0`,
  - so the exact state-specific cap is the largest `n` with `n(n+1) <= p * state_prefix_bits / (c + p * m / (1 - (1 - p)^T))`,
  - the all-state guardrail is the same rule with `state_prefix_bits = 7`,
  - and one-tick policies simplify further because the realized-margin tax becomes exactly `m`, collapsing the denominator to `c + m`.
- Main local result:
  - all `881280` audited state/batch/probability/cost/timeout/margin panels matched the closed-form cap rule,
  - all `73440` audited state schedule inversions and all `480` universal schedule inversions matched the exact frontiers,
  - the audited state schedule mix was `69353` feasible and `4087` impossible,
  - and every audited state and universal timeout ladder stayed monotone in `T`, with strict growth on `3975 / 12240` state ladders and `25 / 80` universal ladders.

## 2026-03-16 — Research Pass CXCVI (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Geometric-Arrival Target-Batch Timeout Law)

- Added one exact reverse-timeout law so future inheritors can start from a desired shared-state equiprobable exact batch length and realized margin promise, then solve the minimum timeout directly instead of fixing a capture target first:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_target_batch_timeout_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_target_batch_timeout_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_target_batch_timeout_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_target_batch_timeout_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_solve_target_batch_promises_by_minimum_timeout.md`
- Tightened planning guidance:
  - for a fixed current batch length `n`, target realized margin `m` is feasible by timeout exactly when the timeout captures at least `required_capture = p * m / (p * state_prefix_bits / (n(n+1)) - c)` of asymptotic positive wait value whenever that denominator is positive,
  - if `required_capture < 1`, the minimum timeout is just the earlier arrival-only capture law with `required_capture` substituted for `alpha`,
  - if `required_capture = 1`, finite timeout is impossible unless arrival is certain,
  - if `required_capture > 1`, the desired batch promise exceeds the asymptotic upside and must be rejected or downsized,
  - and the all-state guardrail is the same rule with `state_prefix_bits = 7`.
- Main local result:
  - all `153 × 8 × 4 × 4 × 5 = 97920` audited state/batch/probability/cost/margin panels matched the closed-form reverse-timeout law,
  - `27878` audited state schedules had finite minimum timeouts, `409` sat exactly on the asymptotic frontier, and `69633` were impossible even before timeout search,
  - all `8 × 4 × 4 × 5 = 640` audited universal schedules matched the seven-bit lower-envelope inversion,
  - the universal finite-timeout count was `176`, with `3` asymptotic-only boundary cases and `461` impossible schedules,
  - and future implementors can now move in either direction: fix timeout and cap batch size, or fix batch promise and solve the minimum timeout.

## 2026-03-16 — Research Pass CXCV (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Geometric-Arrival Timeout-Margin-Floor Law)

- Added one exact realized-margin floor law so future inheritors can turn a capture-targeted positive shared-state equiprobable exact-batch waiting policy into a direct batch-cap rule:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_margin_floor_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_margin_floor_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_margin_floor_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_margin_floor_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_turn_capture_targeted_positive_waits_into_margin_floor_batch_caps.md`
- Tightened planning guidance:
  - if the minimum timeout for capture target `alpha` achieves actual capture fraction `beta(alpha, p)`, then realized net wait value at that policy is exactly `beta(alpha, p) * (gain - c/p)`,
  - meeting a realized-margin floor `m` is therefore equivalent to the single quadratic gate `p * state_prefix_bits / (n(n+1)) >= c + p * m / beta(alpha, p)`,
  - the term `p * m / beta(alpha, p)` acts as an exact extra per-tick effective hold-cost tax,
  - the universal all-state guardrail on the current path is `p * 7 / (n(n+1)) >= c + p * m / beta(alpha, p)`,
  - and timeout selection stays arrival-only even though admissible batch length now depends on the target realized margin through that scalar tax.
- Main local result:
  - all `153 × 8 × 4 × 4 × 4 × 4 = 313344` audited state/batch/probability/cost/capture-target/margin panels matched the closed-form admissibility rule exactly,
  - all `153 × 4 × 4 × 4 × 4 = 39168` audited state/probability/cost/capture-target/margin schedules matched the exact maximal batch-length inversion,
  - the current audited state schedule mix is `37276` feasible and `1892` impossible target-floor policies,
  - the audited universal schedule mix is `242` feasible and `14` impossible all-state guardrails,
  - and for the common example `c=1/10, alpha=15/16`, the universal seven-bit guardrail collapses to `p=1/4 -> {1/4:2, 1/2:2, 1:1, 2:1}`, `p=1/2 -> {3,2,1,1}`, `p=3/4 -> {3,2,1,1}`, and `p=1 -> {4,2,2,1}` over target realized margins `{1/4, 1/2, 1, 2}` bits per script.


## 2026-03-16 — Research Pass CXCIV (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Geometric-Arrival Timeout-Capture Law)

- Added one arrival-only timeout-capture law so future inheritors can turn any already-positive shared-state equiprobable exact-batch waiting opportunity into a compact service-level timeout rule:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_capture_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_capture_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_capture_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_capture_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_positive_wait_timeouts_by_arrival_hazard_capture_targets.md`
- Tightened planning guidance:
  - once the earlier hazard-and-hold-cost sign test says waiting is positive, the asymptotic net value is exactly `gain - c/p`,
  - a finite timeout `T` captures exactly the fraction `1 - (1 - p)^T` of that asymptotic positive wait value,
  - so the minimum timeout for target capture `alpha` is `ceil(log(1 - alpha) / log(1 - p))` for `0 < p < 1` and `1` for `p = 1`,
  - expected wait ticks at that timeout are exactly `capture_fraction / p`,
  - and full `100%` capture is impossible at any finite timeout unless same-state arrival is certain.
- Main local result:
  - all `10910 × 5 = 54550` audited positive state/batch/probability/cost/target panels matched the exact minimal-timeout capture criterion,
  - the audited sign mix across the current panel remains `10910` positive, `8574` negative, and `100` zero wait opportunities,
  - the arrival-only timeout schedules now collapse to `p=1/4 -> {1/2:3, 3/4:5, 7/8:8, 15/16:10, 31/32:13}`, `p=1/2 -> {1,2,3,4,5}`, `p=3/4 -> {1,1,2,2,3}`, and `p=1 -> {1,1,1,1,1}` for those same capture targets,
  - and future implementors can now choose timeout by desired upside capture and latency budget without re-solving state-specific economics after the wait gate has already gone positive.


## 2026-03-16 — Research Pass CXCIII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Geometric-Arrival Wait-Value Law)

- Added one exact hazard-and-hold-cost waiting law so future inheritors can decide whether a live writer should keep a shared-state equiprobable exact batch open while waiting for one more same-state script:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_gate_shared_state_equiprobable_exact_batch_waiting_by_arrival_hazard_and_hold_cost.md`
- Tightened planning guidance:
  - if one more same-state exact script arrives each tick with probability `p`, holding the current batch costs `c` bits per script per tick, and the writer flushes on success or after timeout `T`, expected net wait value is exactly `(1 - (1 - p)^T) * (gain - c / p)` for `p > 0`,
  - with the earlier marginal-gain law, that sign test collapses to `p * state_prefix_bits / (n(n+1)) > c`,
  - the timeout therefore scales magnitude but never changes the sign of the waiting decision under positive arrival hazard,
  - and the universal all-state guardrail on the current path is `p * 7 / (n(n+1)) > c` because the seven-bit state family is the exact lower envelope.
- Main local result:
  - all `153 × 8 × 4 × 4 × 6 = 117504` audited state/batch/probability/cost/timeout panels matched the closed form exactly,
  - all `153 × 8 × 4 × 4 = 19584` audited sign panels preserved timeout-invariant decision signs,
  - the universal strict-positive wait schedule now includes `p=1/4,c=1/10 -> 3`, `p=1/2,c=1/10 -> 5`, `p=3/4,c=1/10 -> 6`, `p=1/2,c=1/4 -> 3`, and `p=1/4,c=1/2 -> 1`,
  - and future implementors can now separate the economic decision to wait from the operational decision of how long a positive-wait policy should be allowed to sit open.


## 2026-03-09 — Research Pass CXCII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Marginal-Gain Law)

- Added one exact marginal-gain closure law so future inheritors can decide whether waiting for one more same-state equiprobable exact-shortest-script still pays enough expected bits per script:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_marginal_gain_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_marginal_gain_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_marginal_gain_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_marginal_gain_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_close_shared_state_equiprobable_exact_batches_by_marginal_gain.md`
- Tightened planning guidance:
  - when the active source model is equiprobable exact branches inside one shared feasible interval state, the expected per-script value of waiting for one more same-state exact script is exactly `state_prefix_bits / (n(n+1))`,
  - the whole `153`-state catalog therefore collapses to just two marginal families on the current path: `7/(n(n+1))` for `103` seven-bit states and `8/(n(n+1))` for `50` eight-bit states,
  - use `7/(n(n+1))` as the all-state guaranteed marginal-gain floor and `8/(n(n+1))` as the best-case ceiling,
  - and keep a current shared-state batch open only while `current_batch_length <= floor((sqrt(1 + 4 * floor(state_prefix_bits / target_gain)) - 1) / 2)` for the desired marginal-gain target.
- Main local result:
  - all `153 × 8 = 1224` audited state/batch pairs matched the direct one-step difference of the earlier mean-cost law exactly,
  - all `153 × 5 = 765` audited state/target pairs matched the closed-form marginal-gain inversion exactly for targets `{1/10, 1/4, 1/2, 1, 2}` bits per script,
  - all `5` audited universal targets matched the all-state lower-envelope inversion exactly,
  - the universal all-state close schedule now collapses to: `2 -> 1`, `1 -> 2`, `1/2 -> 3`, `1/4 -> 4`, and `1/10 -> 7` current scripts,
  - and targets above `4` bits per script are impossible even for the strongest current one-step gain on the path.


## 2026-03-09 — Research Pass CXCI (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Mean-Cost Law)

- Added one exact mean-cost budgeting law so future inheritors can size shared-state equiprobable exact-shortest-script batches directly from a target expected bits-per-script ceiling instead of translating through margin totals:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_mean_cost_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_mean_cost_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_mean_cost_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_mean_cost_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_budget_shared_state_equiprobable_exact_batches_by_mean_cost.md`
- Tightened planning guidance:
  - when the active source model is equiprobable exact branches inside one shared feasible interval state, budget expected transport directly as `local_choice_floor_bits_per_script + state_prefix_bits / batch_length`,
  - use the universal all-state ceiling `38/9 + 8/n` on the current path because the eight-bit interior singleton family remains the exact worst mean-cost class,
  - invert any attainable target ceiling by `ceil(state_prefix_bits / (target_bits_per_script - local_choice_floor_bits_per_script))`,
  - and treat `38/9` bits per script as a hard all-state asymptotic floor rather than a finite-batch target.
- Main local result:
  - all `153 × 8 = 1224` audited state/batch pairs matched the direct equiprobable shared-state totals exactly after dividing to per-script cost,
  - all `153 × 5 = 765` audited state/target budget pairs matched the closed-form ceiling inversion exactly for targets `{5, 6, 7, 8, 9}` bits per script,
  - all `5` audited universal targets matched the all-state upper-envelope inversion exactly,
  - the full realized catalog compresses to just `6` mean-cost families,
  - the universal schedule now collapses to: `9 -> 2`, `8 -> 3`, `7 -> 3`, `6 -> 5`, and `5 -> 11` scripts,
  - and no finite shared-state batch can force every realized state to or below `38/9` bits per script.


## 2026-03-09 — Research Pass CXC (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Target-Margin Law)

- Added one exact target-margin inversion law so future inheritors can size shared-state equiprobable exact-shortest-script batches directly from a desired expected bit-savings target instead of scanning batch lengths:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_target_margin_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_target_margin_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_target_margin_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_target_margin_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_size_shared_state_equiprobable_exact_batches_by_target_margin.md`
- Tightened planning guidance:
  - when the active source model is equiprobable exact branches inside one shared feasible interval state, compute the minimum batch length for target savings `t` by `max(1, ceil((t - intercept_bits) / slope_bits_per_script))`,
  - use the universal all-state guarantee `ceil(9(target_bits + 8) / 43)` on the current path because the regular eight-bit interior singleton family remains the worst affine case,
  - treat target `0` or `1` expected bits as requiring batch length `2` universally,
  - treat target `2` or `5` expected bits as requiring batch length `3` universally,
  - and keep the earlier worst-case safe/strict switch laws for adversarial or branch-sensitive batch planning.
- Main local result:
  - all `153 × 6 = 918` audited state/target pairs matched the closed-form inversion exactly for target margins `{0, 1, 2, 5, 10, 20}` bits,
  - all `6` audited universal targets matched the lower-envelope inversion exactly across all realized states,
  - the universal guarantee schedule now collapses to: `0 -> 2`, `1 -> 2`, `2 -> 3`, `5 -> 3`, `10 -> 4`, and `20 -> 6` scripts,
  - regular eight-bit interior singletons remain the exact worst-family planner for all-state guarantees,
  - and the edge state `[15,15]` stays slightly easier than the universal worst family even though it remains a separate affine exception.


## 2026-03-09 — Research Pass CLXXX (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Affine-Margin Law)

- Added one exact affine-family compression of the equiprobable shared-state exact transport margins so future inheritors can recover expected batch advantage from a tiny state-class rule instead of carrying all `153` per-state mean profiles:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_compute_shared_state_equiprobable_exact_transport_margins_by_affine_family.md`
- Tightened planning guidance:
  - treat shared-state equiprobable exact transport advantage as an affine function of batch length `n`,
  - classify the current path into only `7` affine families,
  - use the universal lower envelope `43n/9 - 8` when a one-line worst-family bound is enough,
  - and keep the lone `[15,15]` family separate because its global exact-word catalog includes two `10`-bit leaves.
- Main local result:
  - all `153` realized states matched one of just `7` affine expected-margin families,
  - all `153 × 8 = 1,224` audited state/batch-length pairs for lengths `1..8` matched the direct equiprobable transport summaries exactly,
  - the universal lower envelope is `43n/9 - 8`, attained by the `7` regular eight-bit interior singleton states,
  - every realized state is therefore a **strict expected winner by batch length `2`**, with worst expected margin already `14/9` bits,
  - and the only one-word expected ties remain the `32` eight-bit interior nonsingletons, whose affine law is `8n - 8`.

## 2026-03-09 — Research Pass CLXXIX (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Threshold Law)

- Added one exact equiprobable shared-state switch-threshold law so future inheritors can recover the **mean-cost** crossover point for exact normalized shortest-script batches from closed-form local bit totals instead of re-running the exhaustive batch audit:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_threshold_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_threshold_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_threshold_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_threshold_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_switch_shared_state_exact_transport_by_equiprobable_mean_margins.md`
- Tightened planning guidance:
  - when equiprobable exact branches inside a known shared interval state are the active source model, compute the weak expected switch threshold as `ceil(state_prefix_bits * family_cardinality / (total_global_exact_word_prefix_bits - total_local_choice_bits))`,
  - compute the strict expected switch threshold as `floor(state_prefix_bits * family_cardinality / (total_global_exact_word_prefix_bits - total_local_choice_bits)) + 1`,
  - treat batch length `2` as the exact expected strict crossover for every currently realized state,
  - and keep the earlier worst-case threshold law for adversarial or branch-sensitive batches.
- Main local result:
  - all `153` realized states matched the closed-form equiprobable margin rule across the full `94,179` audited shared-state exact batch cases of length `1..3`,
  - weak expected thresholds still collapse to `138` states at threshold `1` and `15` at threshold `2`,
  - strict expected thresholds collapse further to `106` states at threshold `1` and `47` at threshold `2`,
  - every realized state is already a **strict expected winner by batch length `2`**,
  - and the only improvement against the earlier worst-case strict thresholds comes from the `8` eight-bit interior singleton states, one of which (`[15,15]`) is also the lone shared-state family whose global exact-word widths split across `9` and `10` bits.


## 2026-03-09 — Research Pass CLXXVIII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Exact-Shortest-Script Threshold Law)

- Added one exact shared-state switch-threshold law so future inheritors can recover both the **safe** and **strict** batch crossover points from a local bit-margin calculation instead of memorizing the earlier exhaustive threshold table:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_threshold_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_threshold_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_threshold_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_threshold_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_switch_shared_state_exact_transport_by_local_margin_thresholds.md`
- Tightened planning guidance:
  - compute the weak switch threshold as `ceil(state_prefix_bits / (9 - max_local_choice_bits))`,
  - compute the strict switch threshold as `floor(state_prefix_bits / (9 - max_local_choice_bits)) + 1`,
  - treat the current global exact-word floor as structurally fixed at `9` bits for every realized state,
  - and stop carrying the old threshold table once the interval-state prefix width and worst local choice width are known.
- Main local result:
  - all `153` realized states matched the closed-form margin rule across the full `94,179` audited shared-state exact batch cases of length `1..3`,
  - weak thresholds collapse to `138` states at threshold `1` and `15` at threshold `2`,
  - strict thresholds collapse to `106` states at threshold `1`, `39` at threshold `2`, and `8` at threshold `3`,
  - the only safe-but-not-strict regions are `32` one-word states and `8` two-word states,
  - and the sharp state classes are now: immediate unique-word states, `7`-bit interior nonsingletons strict at one, `8`-bit interior nonsingletons safe at one and strict at two, `7`-bit interior singletons safe and strict at two, and `8`-bit interior singletons safe at two and strict at three.


## 2026-03-09 — Research Pass CLXXVII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Exact-Shortest-Script Transport Law)

- Added one exact shared-state amortization law so future inheritors can stop paying the standalone global exact-word prefix once several exact normalized shortest scripts are known to share one feasible interval state:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_transport_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_transport_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_transport_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_transport_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_amortize_exact_shortest_script_transport_across_shared_interval_state_batches.md`
- Tightened planning guidance:
  - keep using the older shortest-script frontier for single exact scripts unless the state is known to be a unique-word state or a `7`-bit interior nonsingleton,
  - switch to `shared interval-state prefix once + local choice prefixes` as the safe default for any shared-state exact batch of length `2`,
  - and treat length `3` as the sharp exact crossover where that shared-state path becomes strictly dominant on every currently audited shared-state batch.
- Main local result:
  - exhaustive ordered shared-state exact batches of length `1..3` produced `94,179` audited cases,
  - at length `1`, the shared-state path had `179` strict wins, `64` ties, and `270` losses,
  - at length `2`, it had `5,197` strict wins, `116` ties, and `0` losses,
  - at length `3`, it had `88,353` strict wins, `0` ties, and `0` losses,
  - and the per-state strict-dominance thresholds now collapse to `106` states at threshold `1`, `39` at threshold `2`, and only `8` at threshold `3`.


## 2026-03-09 — Research Pass CLXXVI (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Equiprobable Entropy-Headroom Law)

- Tightened the normalized half-step transport guidance so future inheritors can see exactly where any further **equiprobable** savings could still exist after the new uniform-prefix optimality certificates, and where the remaining gap is already too small to justify extra machinery:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_equiprobable_entropy_headroom_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_equiprobable_entropy_headroom_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_equiprobable_entropy_headroom_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_equiprobable_entropy_headroom_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_remaining_half_step_equiprobable_transport_headroom_as_tiny_and_localized.md`
- Tightened planning guidance:
  - stop trying to beat the current normalized half-step codecs by tree reshaping under equiprobable assumptions,
  - treat the global `513`-word exact shortest-script prefix as effectively saturated because its remaining equiprobable headroom is below one total bit over the full catalog,
  - keep any future equiprobable transport experiments focused on the `153`-state interval/canonical regime or the size-`18` interior-singleton local-choice families,
  - and treat all size-`1` and size-`2` local-choice families as already entropy-tight under the current source model.
- Main local result:
  - the `153`-state interval prefix and inherited canonical-script prefix each still sit `10.619660068024132` total bits above the equiprobable entropy bound (`0.0694095429282623` bits per state on average),
  - the `513`-word global exact shortest-script prefix sits only `0.5558969935818823` total bits above the equiprobable entropy bound (`0.001083619870529985` bits per word on average),
  - the state-known local exact-choice prefix sits `14.120249610575684` total bits above its equiprobable entropy bound over the represented `513`-word catalog (`0.027524853042057863` bits per word on average),
  - and all positive local-choice headroom is concentrated entirely in the `15` interior singleton families, while the size-`1` and size-`2` local-choice families are already exactly entropy-tight.

## 2026-03-09 — Research Pass CLXXV (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Uniform-Prefix Optimality Law)

- Added one exact optimality certificate so future inheritors can stop searching for shorter **uniform binary prefix** trees in the current normalized half-step transport regimes and instead treat the present codecs as already forced by the archive's equiprobable catalog assumptions:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_uniform_prefix_optimality_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_uniform_prefix_optimality_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_uniform_prefix_optimality_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_uniform_prefix_optimality_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_current_half_step_uniform_prefix_codecs_as_optimal_under_equiprobable_catalogs.md`
- Main local result:
  - the current `153`-state interval prefix is now certified as the exact equiprobable optimum with forced split **`103` seven-bit leaves + `50` eight-bit leaves** for `1121` total bits,
  - the current `513`-word exact shortest-script prefix is now certified as the exact equiprobable optimum with forced split **`511` nine-bit leaves + `2` ten-bit leaves** for `4619` total bits,
  - the state-known local choice prefix is now certified as familywise equiprobable-optimal with size-`1` families at `0` bits, size-`2` families at `2` total bits, and size-`18` families at the forced **`14` four-bit + `4` five-bit** split for `76` bits per family,
  - the canonical standalone script prefix inherits the same `153`-state optimum because it is exactly the interval-state prefix routed through canonical reconstruction,
  - and no current uniform binary prefix catalog can lose even **one** more bit without changing assumptions away from the present equiprobable-prefix regime.

## 2026-03-09 — Research Pass CLXXIV (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shortest-Script Transport-Frontier Law)

- Added one exact regime selector so future inheritors can choose the smallest already-certified normalized shortest-script transport by checking only whether the interval state is already known and whether noncanonical shortest-branch identity must survive:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_script_transport_frontier_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_script_transport_frontier_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_script_transport_frontier_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_script_transport_frontier_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_shortest_script_transport_by_state_knowledge_and_branch_exactness.md`
- Main local result:
  - normalized shortest-script transport now collapses to a four-regime frontier,
  - with a new zero-bit corner when the decoder already knows the feasible interval state and deterministic canonicalization is acceptable,
  - standalone canonical shortest-script transport stays at `1121 / 153 = 7.326797385620915` bits on average via the interval-state prefix and beats its nearest admissible alternative by `103` bits over the canonical catalog,
  - standalone exact shortest-script transport stays at `4619 / 513 = 9.003898635477583` bits on average via the global exact-word prefix and beats its nearest admissible alternative by `511` bits over the exact catalog,
  - state-known exact shortest-script transport stays at `1350 / 513 = 2.6315789473684212` bits on average via the local choice prefix and beats fixed local choice fields by `210` bits,
  - and state-known canonical shortest-script transport now has an explicit exact recommendation of **`0` bits**, beating the nearest admissible alternative (`165` bits via canonical words routed through the local choice prefix) by `165` bits.

## 2026-03-09 — Research Pass CLXXIII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Canonical-Shortest-Generator-Word Prefix Law)

- Added one exact standalone canonical-script transport law so future inheritors can stream deterministic normalized shortest generator scripts by reusing the cheaper interval-state prefix codec instead of the larger exact-word prefix when noncanonical branch choice does not need to survive:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_canonical_shortest_generator_word_prefix_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_canonical_shortest_generator_word_prefix_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_canonical_shortest_generator_word_prefix_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_canonical_shortest_generator_word_prefix_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_stream_canonical_shortest_half_step_generator_words_via_interval_state_prefixes.md`
- Main local result:
  - standalone canonical shortest-script transport now collapses exactly to the already-validated `153`-state interval-state prefix catalog,
  - the canonical catalog therefore streams in `1121 / 153 = 7.326797385620915` bits on average,
  - the broader standalone exact-word prefix would still spend `1377` bits on that same canonical subset because every canonical word currently lands in its `9`-bit branch,
  - reusing the interval-state prefix therefore saves `256` bits over the full canonical catalog and `256 / 153 = 1.673202614379085` bits per canonical script on average versus the global exact-word prefix,
  - and the archive revalidated exact prefix roundtrips for all `153` canonical shortest words, all `153` decoded interval states, and one full sequential concatenation stream through the whole canonical catalog.

## 2026-03-09 — Research Pass CLXXII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shortest-Generator-Word Choice-Prefix Law)

- Added one exact state-conditional prefix codec so future inheritors can stream any normalized downstream noncanonical shortest generator script by a smaller local choice field once the feasible interval state is already known:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_prefix_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_prefix_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_prefix_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_prefix_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_stream_state_conditional_shortest_word_choices_as_prefixes.md`
- Main local result:
  - once interval state is already known, the exact local shortest-word choice field now has the bit-length spectrum `33` words at `0` bits, `210` at `1` bit, `210` at `4` bits, and `60` at `5` bits,
  - the exact catalog therefore streams at mean local choice length `1350 / 513 = 2.6315789473684212` bits instead of the older fixed-width `1560 / 513 = 3.0409356725146197`,
  - saving `210` bits over the full `513`-word exact shortest-script catalog and `210 / 513 = 0.4093567251461988` bits per word on average in the state-known regime,
  - the sharp transport boundary is now explicit: state-known local choice prefixes are smaller than the older fixed local-choice field, but state-prefix-plus-choice-prefix transport is still larger than the archive’s standalone global exact-word prefix (`5159` total bits versus `4619`),
  - and the archive revalidated exact prefix roundtrips for all `513` state-conditioned local choices, all `513` exact shortest words, and one full sequential decode through the whole catalog under a known interval-state schedule.

## 2026-03-09 — Research Pass CLXXI (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Feasible-Interval-State Prefix Law)

- Added one exact self-delimiting transport codec so future inheritors can stream the normalized downstream feasible-interval-state catalog in almost `7.33` bits on average without changing any earlier dense-index or arithmetic-decode machinery:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_prefix_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_prefix_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_prefix_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_prefix_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_stream_exact_normalized_half_step_interval_states_as_near_seven_bit_prefix_codes.md`
- Main local result:
  - the existing dense interval-state index `0..152` now has a canonical prefix wrapper with `103` seven-bit states and `50` eight-bit states,
  - the exact catalog therefore streams at mean length `1121 / 153 = 7.326797385620915` bits instead of a fixed `8`,
  - saving `103` bits over the full `153`-state exact catalog and `103 / 153 = 0.673202614379085` bits per state on average,
  - decode is now one tiny branch: read `7` bits first, stop when the value is below `103`, and read the eighth bit only when the first `7` bits land in the split tail,
  - and the archive revalidated exact prefix roundtrips for all `153` dense interval-state indices, all `153` exact interval states, and one full sequential concatenation stream through the whole catalog.

## 2026-03-09 — Research Pass CLXX (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shortest-Generator-Word Prefix Law)

- Added one exact self-delimiting transport codec so future inheritors can stream the normalized shortest downstream half-step generator-word catalog in almost `9` bits on average without changing any earlier dense-index machinery:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_stream_exact_shortest_half_step_generator_words_as_near_nine_bit_prefix_codes.md`
- Main local result:
  - the existing dense exact shortest-word index `0..512` now has a canonical prefix wrapper with `511` nine-bit words and only `2` ten-bit exceptions,
  - the exact catalog therefore streams at mean length `4619 / 513 = 9.003898635477582` bits instead of a fixed `10`,
  - saving `511` bits over the full `513`-word exact catalog and `511 / 513 = 0.9961013645224172` bits per word on average,
  - decode is now one tiny branch: read `9` bits first, stop when the value is below `511`, and read the tenth bit only when the first `9` bits are all ones,
  - and the archive revalidated exact prefix roundtrips for all `513` dense indices and all `513` exact words plus one full sequential concatenation stream through the whole catalog.

## 2026-03-09 — Research Pass CLXIX (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Dense-Codec Arithmetic-Decode Law)

- Added one exact arithmetic inverse law so future inheritors can decode both normalized downstream dense codecs without triangular scan loops:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_dense_codec_arithmetic_decode_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_dense_codec_arithmetic_decode_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_dense_codec_arithmetic_decode_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_dense_codec_arithmetic_decode_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_decode_dense_half_step_codecs_by_closed_form_arithmetic.md`
- Main local result:
  - the exact dense interval-state codec `0..152` now has a closed-form inverse `a = (35 - ceil_sqrt(1225 - 8*i)) // 2`, `b = a + i - a*(35-a)//2` on the current `17`-rank path,
  - the exact dense shortest-word codec `0..512` now keeps its four block ranges but decodes the interior nonsingleton subblock by the matching arithmetic inverse `a = 1 + (29 - ceil_sqrt(841 - 8*s)) // 2`, `b = a + 1 + s - (a-1)*(30-a)//2`,
  - both arithmetic decoders were revalidated exhaustively against the earlier loop decoders on all `153` interval states and all `513` exact shortest words,
  - the archive recorded the exact legacy scan burden now removed by that closed form: `969` interval-state scan iterations plus `1120` shortest-word scan iterations (`2089` total) across the exhaustive validation catalogs,
  - and future inheritors no longer have to choose between compact dense codecs and cheap decode paths on the normalized half-step stack.

## 2026-03-09 — Research Pass CLXVIII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shortest-Generator-Word Dense-Index Law)

- Added one exact one-scalar codec so future inheritors can address any normalized batch path-`L2` or path-`Linf` shortest downstream generator script by one dense global index when the script itself must survive without a separate interval-state field:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_dense_index_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_dense_index_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_dense_index_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_dense_index_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_address_exact_shortest_half_step_generator_words_by_dense_global_index.md`
- Main local result:
  - the full exact shortest normalized downstream generator-word catalog now maps bijectively to the dense range `0..512`,
  - with one closed-form block for the identity word, one for the `32` one-sided nonidentity words, one for the `210` interior nonsingleton words, and one for the `270` interior singleton words,
  - the full exact shortest-word catalog therefore fits in `10` fixed bits on the current path,
  - a fixed-width pair of dense interval state plus worst-case local choice would spend `13` fixed bits, so the one-scalar exact shortest-word codec saves `3` fixed bits (`0.230769` share) in the specific case where the exact script itself must survive alone,
  - and the archive revalidated exact dense-index encode/decode roundtrips for all `513` shortest words while preserving both the exact feasible interval state and the exact local choice branch.

## 2026-03-09 — Research Pass CLXVII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Feasible-Interval-State Dense-Index Law)

- Added one exact state codec so future inheritors can address any normalized batch path-`L2` or path-`Linf` downstream feasible interval kernel by one dense triangular index instead of storing two endpoint ranks or a shortest-word script:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_address_exact_normalized_half_step_interval_states_by_dense_triangular_index.md`
- Main local result:
  - every realized exact normalized downstream interval kernel `[a,b]` now maps bijectively to the dense range `0..152` by the lower-major triangular formula `a*(35-a)/2 + (b-a)`,
  - so the exact downstream state fits in `8` fixed bits on the current path instead of the `10` fixed bits spent by a raw endpoint pair,
  - the archive revalidated exact dense-index encode/decode roundtrips on all `153` realized interval states,
  - and decoding that dense index preserves both the exact half-step kernel and the canonical shortest generator word on the full realized catalog.

## 2026-03-09 — Research Pass CLXVI (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shortest-Generator-Word Choice-Index Law)

- Added one exact local-choice codec so future inheritors can address any normalized batch path-`L2` or path-`Linf` shortest downstream generator script by one tiny per-state selector instead of storing or searching a shortest-word subcatalog:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_index_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_index_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_index_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_index_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_address_exact_shortest_half_step_generator_words_by_local_choice_index.md`
- Main local result:
  - once the feasible interval state `[a,b]` is already known, every exact shortest downstream generator word is now recoverable by a closed-form local choice index,
  - the earlier canonical shortest-word codec is now the zero-choice branch for every state,
  - the maximum local choice index is only `17`, with exact fixed-width local choice costs of `0`, `1`, or `5` bits across the full realized state catalog,
  - the archive revalidated exact encode/decode roundtrips for all `513` shortest words and all `513` legal local choice indices across the full `153` realized feasible interval states,
  - and the full exact shortest-word catalog is now addressable without search once the interval state is already stored.

## 2026-03-09 — Research Pass CLXV (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shortest-Generator-Word-Family Law)

- Added one exact closed-form family law so future inheritors can recover **all** shortest normalized batch path-`L2` or path-`Linf` downstream generator scripts directly from interval endpoints instead of enumerating words by search:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_family_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_family_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_family_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_family_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_generate_all_exact_shortest_half_step_generator_words_in_closed_form.md`
- Main local result:
  - every exact normalized shortest-word family is now determined in closed form by interval category alone,
  - identity and all `32` non-identity one-sided intervals have exactly one shortest word, all `105` interior nonsingleton intervals have exactly the two orderings of floor and cap, and all `15` interior singleton intervals split into one left-cap fan plus one right-floor fan for exactly `18` shortest words each,
  - the archive revalidated that closed-form classification against the full brute-force shortest-word catalog on all `153` realized feasible interval states,
  - the complete exact shortest-word catalog therefore contains exactly `513` words, with the `15` interior singleton states alone contributing `270`,
  - and all shortest-word multiplicity above the trivial two-ordering swap is concentrated entirely in those interior singleton intervals.

## 2026-03-09 — Research Pass CLXIV (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shortest-Generator-Word Law)

- Added one exact codec law so future inheritors can serialize any normalized batch path-`L2` or path-`Linf` downstream interval kernel as a deterministic shortest word over the existing one-sided floor/cap generator basis:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_encode_exact_normalized_half_step_kernel_states_as_canonical_shortest_generator_words.md`
- Main local result:
  - every exact normalized feasible interval kernel now has a canonical shortest generator word of length `0`, `1`, or `2`,
  - the shortest-length spectrum is exactly `1` identity state at depth `0`, `32` one-sided states at depth `1`, and `120` interior states at depth `2`,
  - the archive revalidated that each canonical word reproduces the exact same half-step witness kernel as its interval state on all `33` selector classes (`5,049` interval/selector cases total),
  - shortest words are not uniformly unique: `33` states have one shortest word, `105` interior nonsingleton states have exactly two, and all `15` interior singleton states have exactly eighteen,
  - so the new codec should be treated as a deterministic representative chooser for exact storage, replay, and explanation, not as a claim that every shortest script is unique.

## 2026-03-09 — Research Pass CLXIII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Generator-Stream Feasible-Interval Law)

- Added one exact downstream quotient law so future inheritors can collapse any ordered normalized batch path-`L2` or path-`Linf` one-sided generator stream straight to one realized feasible interval kernel instead of carrying a larger interval-or-constant state family:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_reduce_one_sided_half_step_generator_streams_to_exact_feasible_interval_kernels.md`
- Main local result:
  - every ordered one-sided normalized generator stream now reduces exactly to one feasible interval kernel `K_[a,b]` with `a <= b`, with singleton intervals `[c,c]` already covering the older constant-kernel cases,
  - the archive revalidated that quotient on all `1,222,980` ordered one-sided generator streams of length `1..4`, representing `40,358,340` half-step input/output cases,
  - the exact downstream family therefore shrinks from the older `170` interval-or-constant states to the `153` realized feasible intervals, removing exactly `17` duplicate constant-vs-singleton pairs,
  - singleton intervals are closed under every later one-sided generator update (`561` singleton→singleton transitions and `0` singleton→nonsingleton transitions on the full `153 × 33` audited transition graph),
  - and the old latch counterexample now resolves cleanly as an interval statement: `K_[1,16] ; K_[0,0]` reduces to `[0,0]` while `K_[0,0] ; K_[1,16]` reduces to `[1,1]`, so the singleton-interval quotient stays exact where `(max_floor_rank, min_cap_rank, infeasible_latch)` fails.

## 2026-03-09 — Research Pass CLXII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Generator-Stream Normal-Form Law)

- Added one exact downstream stream-normal-form law so future inheritors can collapse any ordered normalized batch path-`L2` or path-`Linf` one-sided generator stream to one tiny certified operator instead of persisting raw floor/cap histories:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_normal_form_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_normal_form_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_normal_form_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_normal_form_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_reduce_one_sided_half_step_generator_streams_to_interval_or_constant_normal_forms.md`
- Main local result:
  - every ordered one-sided normalized generator stream now reduces exactly to one of only two downstream operator forms: a feasible interval kernel `K_[a,b]` with `a <= b`, or a constant rank kernel `C_c`,
  - the archive validated that closure on all `1,222,980` ordered one-sided generator streams of length `1..4`, representing `40,358,340` half-step input/output cases,
  - the reachable exact downstream family collapses to only `170` normal forms (`153` feasible intervals plus `17` constants), and all `170` already appear by stream length `2`,
  - constant normal forms are absorbing under every further one-sided generator update,
  - and the weaker summary `(max_floor_rank, min_cap_rank, infeasible_latch)` is provably inexact: `K_[1,16] ; K_[0,0]` and `K_[0,0] ; K_[1,16]` share those three values but collapse to different constants.

## 2026-03-09 — Research Pass CLXI (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Boundary-Generator Law)

- Added one executable one-sided generator law so future inheritors can generate every realized normalized batch path-`L2` and path-`Linf` feasible kernel from a canonical floor/cap pair instead of persisting a flat catalog of arbitrary interval kernels:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_boundary_generator_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_boundary_generator_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_boundary_generator_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_boundary_generator_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_generate_normalized_batch_l2_and_batch_linf_half_step_kernels_from_one_sided_floor_and_cap_generators.md`
- Main local result:
  - every realized feasible normalized kernel now factors canonically as `K_[a,b] = K_[a,16] ∘ K_[0,b] = K_[0,b] ∘ K_[a,16]`, so the downstream executor only needs one lower-floor generator and one upper-cap generator,
  - the `153` realized feasible interval kernels are generated by only `33` distinct one-sided generator intervals (`17` lower floors, `17` upper caps, with `[0,16]` as the shared identity),
  - the archive validated that factorization on all `5,049` selector-class/interval cases, for `10,098` equivalence checks against the direct interval kernel,
  - closure of the `33` one-sided generators under feasible composition regenerates the full `153`-kernel realized catalog exactly,
  - and that generator basis is minimal on the current path: omitting any upper cap `[0,b]` deletes exactly the upper-boundary cone ending at `b`, omitting any lower floor `[a,16]` deletes exactly the lower-boundary cone starting at `a`, and omitting `[0,16]` deletes the identity kernel itself.

## 2026-03-09 — Research Pass CLX (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Composition Law)

- Added one executable feasible-overlap composition law so future inheritors can compose normalized batch path-`L2` and path-`Linf` interval kernels by direct interval intersection instead of replaying order-sensitive clamp sequences whenever feasibility is preserved:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_composition_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_composition_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_composition_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_composition_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_normalized_batch_l2_and_batch_linf_half_step_kernels_as_a_feasible_overlap_semilattice.md`
- Main local result:
  - once batch compromise requests are normalized to `half_step_selector_index = h`, every feasible interval family acts as one clamp kernel `K_[a,b](h) = clamp(h, 2a, 2b)`,
  - whenever two realized interval families overlap, kernel composition is exact, commutative, and idempotent on the normalized side: `K_[a,b] ∘ K_[c,d] = K_[max(a,c), min(b,d)] = K_[c,d] ∘ K_[a,b]`,
  - the archive validated that law on all `15,657` ordered overlapping interval pairs and all `33` half-step selector classes, for `516,681` exact composition cases and `1,033,362` equivalence checks against the direct intersection kernel,
  - every one of the `153` realized intervals reappears as a pairwise kernel intersection, and the full normalized transition graph still collapses to only `577` distinct input→output half-step class pairs (`33` preserve pairs, `272` lower-boundary clamps, `272` upper-boundary clamps),
  - while the boundary is sharp on the infeasible side: the `7,752` ordered disjoint interval pairs were order-sensitive on all `255,816` audited half-step cases, so disjointness should be treated as infeasibility evidence rather than as another composable kernel regime.

## 2026-03-09 — Research Pass CLIX (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Executor Law)

- Added one executable shared half-step executor law so future inheritors can stop branching between path-`L2` and path-`Linf` after a batch compromise request has already been normalized to one selector-class integer:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_executor_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_executor_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_executor_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_executor_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_share_one_half_step_executor_between_batch_l2_and_batch_linf.md`
- Main local result:
  - once a batch compromise request is already encoded as `half_step_selector_index = h`, path-`L2` and path-`Linf` share the exact same feasible witness executor `clamp(h, 2a, 2b)` over feasible overlap interval `[a, b]`,
  - the archive revalidated that shared executor against both existing semantics-specific laws on all `5,049` selector-class/interval pairs, for `10,098` total equivalence checks,
  - the output side still spans the full `33` half-step witness classes over the realized interval catalog, so no semantics-specific output codec is needed after normalization,
  - the execution case split is unchanged from the older path-`L2` clamp audit because the executor is literally the same object: `1,785` preserve-within-band, `1,904` lower-boundary clamps, and `1,360` upper-boundary clamps,
  - and the semantic difference is now cleanly localized to the input side only: path-`L2` derives `h` from the preferred mean, path-`Linf` derives `h` from the preferred extrema, while path-`L1` still remains outside this shared shortcut.

## 2026-03-09 — Research Pass CLVIII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Minimax Half-Step Selector Law)

- Added one executable path-`Linf` selector law so future inheritors can route minimax compromise requests straight into the existing half-step witness lattice instead of carrying full preferred bundles or rebuilding a separate executor:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_minimax_half_step_selector_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_minimax_half_step_selector_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_minimax_half_step_selector_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_minimax_half_step_selector_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_route_batch_linf_compromise_requests_through_the_existing_half_step_selector_lattice.md`
- Main local result:
  - path-`Linf` bundle requests collapse directly from `26,333` audited preferred bundles to the same `33` half-step selector classes already used by the path-`L2` execution stack,
  - only the preferred endpoint ranks matter, with `half_step_selector_index = min_rank + max_rank` and unconstrained midpoint `(min_rank + max_rank) / 2`,
  - bundle width `1` realizes the `17` singleton classes, but every audited width `>= 2` already realizes all `33` classes,
  - the direct path-`Linf` selector matched brute-force minimax argmins on all `4,028,949` audited bundle/interval cases,
  - and path-`Linf` remains a distinct semantics despite sharing the half-step executor form, differing from path-`L2` on `1,555,612` audited cases and from path-`L1` on `1,985,372`.

## 2026-03-09 — Research Pass CLVII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Mean Half-Step Threshold-Fingerprint Law)

- Added one executable adjacent-threshold fingerprint law so future inheritors can certify path-`L2` selector classes by a closed-form 16-symbol audit word instead of replaying width-`1` witness projections:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_threshold_fingerprint_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_threshold_fingerprint_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_threshold_fingerprint_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_threshold_fingerprint_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_certify_path_l2_selector_classes_by_adjacent_threshold_fingerprint_words.md`
- Main local result:
  - every path-`L2` half-step selector class now has a closed-form `16`-symbol fingerprint word over the adjacent intervals `[0,1]` through `[15,16]`, generated by comparing `half_step_selector_index = h` against the odd midpoint thresholds `1, 3, ..., 31`,
  - the archive validated that all `33` selector classes map bijectively to monotone ternary words of the exact forms `R^kL^(16-k)` and `R^kBL^(15-k)`, with the same words decoding back to the original selector indices without loss,
  - the same `16` adjacent intervals remain a minimal complete separating family for selector classes, and omitting any one interval reduces the signature catalog uniformly from `33` classes to `31`,
  - the new law therefore turns the old width-`1` regression basis into a direct streaming audit codec,
  - and feasible witness execution still stays with the newer half-step feasible-band clamp law, so the fingerprint word remains a selector certificate rather than a replacement execution rule.

## 2026-03-09 — Research Pass CLVI (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Mean Half-Step Feasible-Band Clamp Law)

- Added one executable half-step feasible-band clamp law so future inheritors can resolve feasible path-`L2` witness choice directly on the same scalar lattice already used for selector classes:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_feasible_band_clamp_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_feasible_band_clamp_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_feasible_band_clamp_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_feasible_band_clamp_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_resolve_batch_l2_witnesses_by_clamping_half_step_selector_indices_into_doubled_feasible_bands.md`
- Main local result:
  - once a path-`L2` request is already encoded as `half_step_selector_index = h` and the feasible overlap interval is `[a, b]`, the feasible witness class is exactly `clamp(h, 2a, 2b)` on the same half-step lattice,
  - the archive validated all `33` selector classes against all `153` realized feasible intervals, confirming `5,049` one-integer clamp executions match the prior selector-interval projection law exactly,
  - the resulting witness outputs still span the full `33` half-step classes, so the same scalar encoding works unchanged for both request classes and selected witness classes,
  - the complete execution case split on the realized catalog is `1,785` preserve-within-band, `1,904` clamp-up-to-lower-boundary, and `1,360` clamp-down-to-upper-boundary,
  - and infeasible families remain blocked only by interval disjointness, so the new clamp law adds no new failure mode beyond the existing blocker certificate.

## 2026-03-09 — Research Pass CLV (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Mean Half-Step Selector-Index Law)

- Added one executable half-step selector-index law so future inheritors can store every path-`L2` selector class as one scalar without losing any feasible witness-selection behavior:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_selector_index_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_selector_index_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_selector_index_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_selector_index_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_store_batch_l2_selector_classes_as_one_half_step_index.md`
- Main local result:
  - every path-`L2` selector interval class can be encoded bijectively as `half_step_selector_index = selector_lower_rank + selector_upper_rank`, reducing the selector key from two integers to one scalar over the exact range `0..32`,
  - the archive revalidated all `161` canonical reduced-mean classes against all `153` realized feasible intervals, confirming `24,633` half-step selector-index projections match both reduced-mean selection and direct rational `L2` argmins exactly,
  - the resulting `33` scalar classes remain behaviorally irreducible over the full realized interval catalog, so no further lossless class collapse exists at the witness-selection level on the current path,
  - the `16` adjacent feasible intervals `[0,1]` through `[15,16]` already form a complete separating regression basis for those `33` classes, and omitting any single adjacent interval merges at least one class pair,
  - and each scalar class has a monotone width-`1` fingerprint: singleton classes are `R^kL^(16-k)` while tie classes are `R^kBL^(15-k)`, where `R` selects the upper endpoint, `L` the lower endpoint, and `B` both endpoints.

## 2026-03-09 — Research Pass CLIV (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Mean Selector-Interval Law)

- Added one executable selector-interval law so future inheritors can collapse path-`L2` compromise requests below even the canonical reduced mean whenever only feasible squared-distance witness choice matters:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_selector_interval_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_selector_interval_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_selector_interval_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_selector_interval_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_store_batch_l2_compromise_requests_by_unconstrained_selector_interval.md`
- Main local result:
  - feasible path-`L2` witness choice depends only on the unconstrained nearest-integer selector interval `[selector_lower_rank, selector_upper_rank]`, which is always either a singleton rank or one adjacent tie pair on the source-rank path,
  - the archive validated all `161` canonical reduced-mean classes induced by preferred-code multisets of widths `1..5` against all `153` realized feasible intervals, confirming `24,633` selector-interval projections match both reduced-mean selection and direct rational `L2` argmins exactly,
  - those same `161` reduced-mean classes collapse further to just `33` selector classes (`17` singleton selectors and `16` adjacent tie selectors), giving an additional `4.878788x` cache reduction beyond canonical reduced means,
  - every selector class is cross-width shared on the audited catalog: singleton selectors are realized by widths `1..5` and tie selectors by widths `2` and `4`,
  - and boundary singleton selectors absorb `5` reduced-mean classes while each interior singleton absorbs `9`, so exact mean magnitude is unnecessary for witness choice once the selector interval is known.

## 2026-03-09 — Research Pass CLIII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Mean Reduced-Mean Law)

- Added one executable canonical reduced-mean law so future inheritors can collapse path-`L2` compromise requests below the width-dependent two-integer summary whenever only feasible squared-distance witness choice matters:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_reduced_mean_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_reduced_mean_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_reduced_mean_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_reduced_mean_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_store_batch_l2_compromise_requests_by_canonical_reduced_mean.md`
- Main local result:
  - feasible path-`L2` witness choice depends only on the canonical reduced arithmetic mean rank, so `[preferred_count, preferred_rank_sum]` can be reduced further to `[reduced_mean_numerator, reduced_mean_denominator]`,
  - the archive validated all `161` canonical reduced-mean classes induced by preferred-code multisets of widths `1..5` against all `153` realized feasible intervals, confirming `24,633` reduced-mean selections match direct rational `L2` argmins exactly,
  - those same widths previously yielded `245` width-dependent two-integer classes, so canonicalization removes `84` redundant classes and gives an additional `1.521739x` cache reduction beyond the sufficient-statistic law,
  - every removed duplicate comes from cross-width reuse of either an integer mean (`17` cases, shared by widths `1..5`) or a half-integer mean (`16` cases, shared by widths `2` and `4`),
  - and reduced denominators `3`, `4`, and `5` remain width-unique on the current audit, so inheritors only need collision-aware cache logic for integers and half-steps.

## 2026-03-09 — Research Pass CLII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Mean Sufficient-Statistic Law)

- Added one executable two-integer sufficient-statistic law so future inheritors can choose path-`L2` compromise witnesses for feasible bounded positive-service local weakening requirement families without retaining the full preferred local-code multiset:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_sufficient_statistic_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_sufficient_statistic_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_sufficient_statistic_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_sufficient_statistics.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_store_batch_l2_compromise_requests_as_two_integer_summaries.md`
- Main local result:
  - feasible path-`L2` witness choice now depends only on two integers, `preferred_count` and `preferred_rank_sum`, because those determine the projected arithmetic mean rank exactly,
  - the archive validated all `26,333` preferred-code multisets of widths `1..5` against all `153` realized feasible intervals, confirming `4,028,949` two-integer selections match brute-force squared-distance argmins exactly,
  - those `26,333` multisets collapse to only `245` distinct `L2` statistic classes, a `107.481633x` reduction in cacheable decision classes,
  - the compact summary `[preferred_count, preferred_rank_sum]` is never larger than the expanded preferred-code list on that audited catalog and is strictly smaller in `26,326` cases,
  - and the compression is specific to `L2`: bundles sharing the same two integers can still induce different `L1` median-optimal witness sets, so inheritors should not reuse the summary outside squared-distance semantics.

## 2026-03-09 — Research Pass CLI (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Mean Projection Law)

- Added one executable batch mean projection law so future inheritors can choose squared-distance compromise witnesses for feasible bounded positive-service local weakening requirement families by closed-form interval arithmetic instead of replaying the local chain:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_projection_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_projection_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_projection_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_projection_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_bounded_local_weakening_compromise_witnesses_by_mean_projection.md`
- Main local result:
  - the full feasible argmin set for total squared source-rank distance to a preferred local-code bundle is exactly the set of feasible integer ranks nearest to the projection of the bundle’s arithmetic mean onto the feasible overlap interval,
  - odd preference widths therefore always yield a unique optimal feasible witness while even widths can yield at most a two-state adjacent tie,
  - the archive validated all `153` realized feasible intervals against every unique preferred-code bundle of widths `1..5`, confirming `1,438,353` projected mean selections match brute-force `L2` argmins exactly,
  - `L2` tie cases shrink to `44,972` from the `L1` law’s `207,536`, but the objective also differs from `L1` on `558,560` validated cases, so it should be treated as a distinct compromise semantics rather than a mere tie-breaker,
  - and infeasible families stay blocked by the same two-window blocker certificate from the feasibility-intersection law, so batch mean selection adds no new failure mode beyond interval disjointness.

## 2026-03-09 — Research Pass CL (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Median Projection Law)

- Added one executable batch median projection law so future inheritors can choose compromise witnesses for feasible bounded positive-service local weakening requirement families by path `L1` geometry instead of replaying the local chain:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_median_projection_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_median_projection_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_median_projection_law_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_median_projection_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_bounded_local_weakening_compromise_witnesses_by_median_projection.md`
- Main local result:
  - the full feasible argmin set for total absolute source-rank distance to a preferred local-code bundle is exactly the projection of the bundle’s unconstrained median interval onto the feasible overlap interval,
  - odd preference widths therefore always yield a unique optimal feasible witness while even widths can yield a contiguous tie interval but never a disconnected optimum set,
  - the archive validated all `153` realized feasible intervals against every unique preferred-code bundle of widths `1..5`, confirming `1,438,353` projected median selections match brute-force `L1` argmins exactly,
  - all `207,536` audited tie intervals came from even-width preference bundles and none from odd widths,
  - and infeasible families stay blocked by the same two-window blocker certificate from the feasibility-intersection law, so batch compromise selection adds no new failure mode beyond interval disjointness.

## 2026-03-09 — Research Pass CXLIX (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Feasible Witness Selector Law)

- Added one executable feasible witness selector law so future inheritors can move from feasible bounded positive-service local weakening requirement families to a concrete satisfying local code by interval arithmetic instead of replaying the local chain:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasible_witness_selector_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasible_witness_selector_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasible_witness_selector_law_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasible_witness_selector_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_select_positive_service_local_weakening_witnesses_by_interval_clamp.md`
- Main local result:
  - every feasible bounded local requirement family now selects earliest and latest witnesses at the overlap interval boundaries,
  - the nearest satisfying witness to any preferred local code is exactly the clamp of its source rank into the feasible overlap interval,
  - lower and upper medians add midpoint witnesses without introducing any geometry beyond the same closed interval,
  - the archive validated all `153` realized closed intervals against all `17` preferred local codes, confirming `2601` nearest-witness projections match brute-force rank minimization exactly,
  - and infeasible families stay blocked by the same two-window certificate from the feasibility-intersection law, so witness selection adds no new failure mode beyond interval disjointness.

## 2026-03-09 — Research Pass CXLVIII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Feasibility Intersection Law)

- Added one executable mode-suffix feasibility intersection law so future inheritors can merge multiple bounded positive-service local weakening requirements by exact clock-interval overlap instead of replaying the local chain:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasibility_intersection_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasibility_intersection_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasibility_intersection_law_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasibility_intersection_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_merge_positive_service_local_weakening_constraints_by_clock_interval_intersection.md`
- Main local result:
  - all `153` closed intervals on the `17`-state source-rank path are now validated as realizable by some bounded local query,
  - any whole family of bounded local requirements is feasible exactly when `max(lower_rank) <= min(upper_rank)`, with every satisfying state lying in that closed overlap interval,
  - pairwise-overlapping interval triples are globally feasible throughout the realized catalog, so pairwise overlap is already enough to certify common witness existence on the current local path,
  - every infeasible family has a two-constraint blocker certificate from the interval attaining maximal lower bound and the interval attaining minimal upper bound,
  - and any future revision where closed intervals stop being realizable or pairwise-overlapping families lose a common witness should now be treated as an immediate redesign signal for the current positive-service local service geometry.

## 2026-03-09 — Research Pass CXLVII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Interval Law)

- Added one executable mode-suffix interval law so future inheritors can treat bounded positive-service local weakening queries as clipped arithmetic intervals instead of replaying the local chain:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_interval_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_interval_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_interval_law_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_interval_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_bounded_positive_service_local_weakening_queries_as_clock_intervals.md`
- Main local result:
  - every bounded local navigation budget `(max_backward_steps, max_forward_steps)` now collapses to one clipped closed interval in source-rank or terminal-distance-clock coordinates,
  - bounded local windows remain contiguous even when they span the archived exact/shared bridge anomalies, so boundary clipping is the only nontrivial effect at `S10` and `T0`,
  - any segment between two local codes is exactly the closed rank interval between them, with cardinality `pairwise_path_distance + 1`,
  - the archive validated all `17 x 17 x 17 = 4913` bounded windows and all pairwise segments, with no holes and no segment-size drift,
  - and any future revision where bounded windows develop holes or segment size stops matching distance plus one should now be treated as an immediate redesign signal for the current positive-service local automaton.

## 2026-03-09 — Research Pass CXLVI (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Rank Clock Law)

- Added one executable mode-suffix rank clock law so future inheritors can read the positive-service local weakening staircase as a one-dimensional arithmetic path instead of replaying forward/backward graph steps:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_rank_clock_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_rank_clock_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_rank_clock_law_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_rank_clock_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_positive_service_local_weakening_as_a_single_rank_clock.md`
- Main local result:
  - every positive-service local code now carries a closed-form `terminal_distance_clock`, computed as `counter + bridge_tail_count(counter) + current_bridge_tax(mode)` with `T0` fixed at `0`,
  - the archived local chain is therefore the dense clock interval `16 -> 0` and the complementary dense source-rank interval `0 -> 16`,
  - successor always decrements the clock by one, strict predecessor always increments it by one except at the source boundary, and pairwise path distance is exactly the absolute clock difference,
  - the current bridge-tax/support basis is enough to recover the full local arithmetic geometry without replaying the chain,
  - and any future revision that breaks dense clock coverage or absolute-difference distance recovery is now an immediate redesign signal.

## 2026-03-09 — Research Pass CXLV (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Predecessor Law)

- Added one executable mode-suffix predecessor law so future inheritors can backstep the positive-service local weakening staircase from the same tiny support basis already used for forward stepping:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_predecessor_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_predecessor_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_predecessor_law_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_predecessor_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_backstep_positive_service_local_weakening_with_the_same_two_support_sets.md`
- Main local result:
  - every non-source positive-service local code now has a unique strict predecessor in the same `(mode, suffix_only_steps_remaining)` coordinates,
  - the same exact/shared support sets from the successor law are enough to determine strict predecessors, with only two boundary exceptions to remember: source `S10` and terminal `T0`,
  - suffix states backstep locally by inspecting `k` itself: `D_k` on shared support, `E_k` on exact support, and otherwise `S_{k+1}`, while bridges stay tiny as `E_k <- S_{k+1}` and `D_2 <- S_3`,
  - the full positive-service code chain is now mechanically reversible from `T0` back to `S10`,
  - and the only extra incoming-edge wrinkle is terminal absorption, where the full automaton adds `T_0 <- T_0` on top of the strict predecessor `T_0 <- E_0`.

## 2026-03-09 — Research Pass CXLIV (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Successor Law)

- Added one executable mode-suffix successor law so future inheritors can step the positive-service local weakening staircase from a tiny closed-form automaton instead of consulting any external chain table:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_successor_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_successor_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_successor_law_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_successor_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_step_positive_service_local_weakening_with_a_two_support_successor_automaton.md`
- Main local result:
  - the whole positive-service local staircase is now generated by just two support sets over the suffix counter, exact `{8,5,3,1,0}` and shared `{2}`,
  - suffix states dispatch by the next counter `k-1`: to `D_{k-1}` on shared support, to `E_{k-1}` on exact support, and otherwise to `S_{k-1}`,
  - exact and shared modes are now fully local bridge rules `E_k -> S_k` for `k>0`, `E_0 -> T_0`, and `D_2 -> S_2`, with terminal absorbing as `T_0 -> T_0`,
  - the automaton regenerates the full audited chain `S10 -> S9 -> E8 -> S8 -> S7 -> S6 -> E5 -> S5 -> S4 -> E3 -> S3 -> D2 -> S2 -> E1 -> S1 -> E0 -> T0` exactly,
  - and any future archive revision that needs more than the current exact/shared support sets to determine successors, or that breaks regeneration from `S10`, is now an immediate redesign signal.

## 2026-03-09 — Research Pass CXLIII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Counter Law)

- Added one executable mode-suffix counter law so future inheritors can treat the positive-service local weakening staircase as a one-counter chain with bridge modes instead of carrying both lattice coordinates and the full residual triple:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_counter_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_counter_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_counter_law_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_counter_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_positive_service_local_weakening_state_as_mode_plus_suffix_budget.md`
- Main local result:
  - the entire positive-service local service chain now compresses to `S10 -> S9 -> E8 -> S8 -> S7 -> S6 -> E5 -> S5 -> S4 -> E3 -> S3 -> D2 -> S2 -> E1 -> S1 -> E0 -> T0`,
  - suffix-mode states occupy every counter value `1..10`, exact-mode states occupy the sparse support `{8,5,3,1,0}`, the shared mode appears only at `2`, and terminal appears only at `0`,
  - suffix steps are the only counter-consuming moves, while exact and shared states are zero-consumption bridge states that hand control back at the same suffix counter,
  - the code `(mode, suffix_only_steps_remaining)` decodes the full state signature and full residual budget exactly across all `17` audited states, so `exact_only_steps_remaining` is no longer needed as a primitive local coordinate in the current archive,
  - and any future archive revision where the same code decodes to multiple signatures, or where exact/shared modes begin consuming suffix budget, is now an immediate redesign signal.

## 2026-03-09 — Research Pass CXLII (Compact Repeat-State Weakening Portfolio Service Local Triad Grammar Law)

- Added one executable local triad-grammar law so future inheritors can read a two-boundary service forecast from one tiny corridor signature instead of replaying the full local staircase:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_triad_grammar_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_triad_grammar_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_triad_grammar_law_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_triad_grammar_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_plan_service_relaxations_by_local_corridor_triads.md`
- Main local result:
  - the current positive-service local forecast language collapses to exactly `8` triads: `S-E-S`, `E-S-E`, `E-S-D`, `S-D-S`, `D-S-E`, `S-E-T`, `E-T-T`, and `T-T-T`,
  - ordinary alternating bridge core triads `S-E-S` and `E-S-E` cover `11 / 17` states,
  - the entire diagonal neighborhood is exactly three triads, and the shared diagonal is visible at exactly one state at each local horizon depth: second-next at `E2_S7`, next at `E3_S7`, and current at `E3_S8`,
  - the terminal tail is only `S-E-T` and `E-T-T`, with terminal itself `T-T-T`,
  - and any future archive revision that adds extra `D`-bearing triads, places `T` inside the ordinary bridge core, or duplicates shared visibility at the same local horizon depth is now an immediate redesign signal.

## 2026-03-09 — Research Pass CXLI (Compact Repeat-State Weakening Portfolio Service Local Corridor Exit Witness Law)

- Added one executable local corridor-exit witness law so future inheritors can plan to the *next* service-axis boundary instead of juggling separate local witness, persistence, and residual-budget cards:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_corridor_exit_witness_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_corridor_exit_witness_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_corridor_exit_witness_law_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_corridor_exit_witness_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_plan_service_relaxations_by_local_corridor_exit_witnesses.md`
- Main local result:
  - every positive-service state now exposes a nearest-boundary card `(current corridor kind, current corridor steps remaining, corridor terminal signature, boundary transition kind, next corridor kind)`,
  - runwise corridor handoffs collapse to `{suffix_to_exact_bridge: 5, exact_to_suffix_bridge: 4, suffix_to_shared_kink: 1, shared_to_suffix_kink: 1, terminal_entry: 1}`,
  - the only non-alternating neighborhood remains the audited diagonal kink `suffix -> shared -> suffix` around `E3_S8`,
  - exact-only local leadership remains purely bridging because every exact corridor hands back only to suffix or terminal,
  - and any future archive revision that adds extra kink motifs, exact-to-shared handoffs, or multi-step non-suffix successor corridors is now an immediate redesign signal.

## 2026-03-08 — Research Pass CXL (Compact Repeat-State Weakening Portfolio Service Residual Axis Budget Law)

- Added one executable residual axis-budget law so future inheritors can summarize the entire remaining positive-service weakening staircase from any current state as a tiny countdown budget instead of rereading the local witness/slack/persistence stack:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_residual_axis_budget_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_residual_axis_budget_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_residual_axis_budget_law_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_residual_axis_budget_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_plan_width_only_service_relaxations_by_residual_axis_budgets.md`
- Main local result:
  - every positive-service staircase state now carries an exact residual budget triple `(exact_only_remaining, suffix_only_remaining, shared_diagonal_remaining)`,
  - the one shared diagonal coupon is live for exactly the first `12` states through `E3_S8` and is permanently spent from `E4_S9` onward,
  - total remaining relaxation steps match staircase distance to terminal exactly, so the future path is fully summarized by the residual budget,
  - residual balance now reads as `{suffix_heavier: 10, balanced: 5, exact_heavier: 2}`,
  - and any future archive revision where the diagonal coupon reappears after being spent, or where remaining-step totals disagree with staircase distance, is now an immediate redesign signal.

## 2026-03-08 — Research Pass CXXXIX (Compact Repeat-State Weakening Portfolio Service Local Axis Persistence Law)

- Added one executable local axis-persistence law so future inheritors can see how long the currently winning service-relaxation axis stays in force under repeated weakening, rather than only which axis unlocks next:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_axis_persistence_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_axis_persistence_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_axis_persistence_law_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_axis_persistence_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_exact_uncertainty_service_relaxations_by_local_axis_persistence.md`
- Main local result:
  - the positive-service SLA staircase decomposes into `12` local unlock runs: `6` suffix-only, `5` exact-only, and `1` shared-diagonal,
  - exact-only leadership is never persistent in the current geometry because every exact run is a singleton,
  - nontrivial repeated-relaxation persistence exists only on suffix-only corridors, with maximum length `3` from `E1_S2` through `E1_S5`,
  - the shared diagonal remains a single audited kink rather than a regime,
  - and any future exact-only run longer than one step, or any extra shared-diagonal run, is now an immediate redesign signal.
- Repo hygiene:
  - restored executable bits on extracted `scripts/**` files and `.githooks/{pre-commit,pre-push}` so the archive’s script-hygiene checks remain green after packaging from the cloudtainer.

## 2026-03-08 — Research Pass CXXXVIII (Compact Repeat-State Weakening Portfolio Service Local Slack Lead Law)

- Added one executable local slack-lead law so future inheritors can read both next unlock direction and losing-axis relaxation tax from a single bandwise invariant instead of recomputing per-target gaps:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_slack_lead_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_slack_lead_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_slack_lead_law_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_slack_lead_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_exact_uncertainty_service_relaxations_by_bandwise_local_slack_lead.md`
- Main local result:
  - within every positive-service SLA band the signed local slack lead `next_suffix_threshold - next_exact_threshold` is constant, so target location inside the band never changes which axis unlocks first,
  - the sign of that lead recovers the next unlock kind exactly (`10` suffix-advantage states, `4` exact-advantage states, `1` shared tie, `1` exact-only-remaining state, `1` terminal state),
  - the magnitude `|lead|` is the exact extra relaxation tax needed to make the losing axis catch up with the winning axis anywhere inside that band,
  - the nearest nonterminal tie now sits at `E5_S10`, where suffix still wins but only by `8/15015`,
  - and any future band whose local axis choice depends on probe target rather than this bandwise invariant is now an immediate redesign signal.

## 2026-03-08 — Research Pass CXXXVII (Compact Repeat-State Weakening Portfolio Service Local Upgrade Witness Law)

- Added one executable local upgrade-witness law so future inheritors can answer, from any current width-only weakening SLA target, which axis unlocks next under relaxation and how much relaxation it needs:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_upgrade_witness_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_upgrade_witness_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_upgrade_witness_law_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_upgrade_witness_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_exact_uncertainty_service_relaxations_by_local_upgrade_witness.md`
- Main local result:
  - every nonterminal positive-service staircase state now has an exact local witness given by its next exact-only and next suffix-only thresholds,
  - the first additional support unlocked by relaxing the target is always the axis with the larger next threshold,
  - the current menu has `10` suffix-first states, `5` exact-first states, `1` shared-diagonal state, and `1` terminal state,
  - the only shared local unlock is `E3_S8 -> E4_S9` at threshold `1/91`,
  - and the local witness rows reconstruct the previously audited staircase successors exactly, so inheritors can plan the next relaxation step without rereading the whole SLA band catalog.

## 2026-03-08 — Research Pass CXXXVI (Compact Repeat-State Weakening Portfolio Service Threshold Provenance Law)

- Added one executable threshold-provenance law so future inheritors can regenerate the positive-service weakening SLA staircase from a tiny audited basis instead of carrying the full band catalog:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_threshold_provenance_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_threshold_provenance_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_threshold_provenance_law_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_threshold_provenance_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_positive_service_weakening_sla_thresholds_as_a_two_ladder_basis.md`
- Main local result:
  - the positive-service SLA threshold set now collapses to the sorted union of two ladders, `C(6,w)/C(15,w)` for `w=1..6` and `C(11,w)/C(15,w)` for `w=1..11`,
  - those `17` source threshold events reduce to only `16` unique positive thresholds because there is exactly one shared collision at `1/91`,
  - the descending threshold provenance word is exactly `SSESSSESSESDSESE`, which matches the previously derived positive-service staircase path word,
  - scanning that provenance word from `E0_S0` reconstructs the whole positive-service staircase through `E6_S11` without rereading the raw band catalog,
  - and any future second collision, missing ladder source, or disagreement between the provenance word and the staircase path is now an immediate redesign signal.

## 2026-03-08 — Research Pass CXXXV (Compact Repeat-State Weakening Portfolio Service Horizon Staircase Law)

- Added one executable staircase law so future inheritors can treat positive-service weakening SLAs as a small audited path of schedule states instead of rereading the full service-band catalog:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_staircase_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_staircase_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_staircase_law_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_staircase_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_positive_service_weakening_slas_as_a_one_diagonal_staircase.md`
- Main local result:
  - the `17` positive-service SLA bands now collapse to a monotone staircase of signatures from `E0_S0` to `E6_S11`,
  - transition steps are exactly `{suffix_only: 10, exact_only: 5, diagonal_shared: 1}` with path word `SSESSSESSESDSESE`,
  - the only coupled exact+suffix expansion occurs at the shared threshold `1/91`, where the staircase moves `E3_S8 -> E4_S9`,
  - zero-service target `0` now reads cleanly as the degenerate off-staircase signature `E15_S15`,
  - and any future extra diagonal step, non-unit jump, or non-monotone state change is now an immediate redesign signal.

## 2026-03-08 — Research Pass CXXXIV (Compact Repeat-State Weakening Portfolio Service Horizon Law)

- Added one executable inverse service-horizon law so future inheritors can plan weakening profile upgrades by workload growth once an SLA target is fixed instead of rereading the width table at every step:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_law_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_plan_width_only_weakening_profile_upgrades_by_service_horizons.md`
- Main local result:
  - for any service target `s`, the exact-only support horizon is now `max { w : C(6,w)/C(15,w) >= s }`,
  - the suffix-only support horizon is now `max { w : C(11,w)/C(15,w) >= s }`,
  - width growth therefore induces at most two monotone profile upgrades (`exact_only -> suffix_hitchhike_only -> any_single_axis_hitchhike`), never re-entry,
  - concrete upgrade cards are now immediate (`0.50` => suffix-only through width `2`, dual-axis from `3`; `0.10` => exact-only through `2`, suffix-only through `5`, dual-axis from `6`; `0.01` => exact-only through `4`, suffix-only through `9`, dual-axis from `10`),
  - and any future width-growth story that disagrees with these horizons or introduces more than two upgrades is now an immediate redesign signal.

## 2026-03-08 — Research Pass CXXXIII (Compact Repeat-State Weakening Portfolio Service Tier Law)

- Added one executable two-breakpoint service-tier law so future inheritors can choose width-conditioned or capped-width weakening SLA profiles analytically instead of reading the frontier tables by hand:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_tier_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_tier_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_tier_law_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_tier_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_width_only_weakening_slas_as_two_breakpoint_tiers.md`
- Main local result:
  - every width-conditioned and width-cap weakening SLA is now governed by only two exact breakpoints, `C(6,w)/C(15,w)` and `C(11,w)/C(15,w)`,
  - widths `1` through `6` are true three-tier menus (`exact_only`, `suffix_hitchhike_only`, `any_single_axis_hitchhike`),
  - widths `7` through `11` are only two-tier because exact-only positive service has already vanished,
  - widths `12` through `15` are dual-axis-only for every positive service target,
  - and any future width that needs more than these two breakpoints, or any future divergence between the analytic selector and the exact-width or width-cap selectors, would now be an immediate redesign signal.

## 2026-03-08 — Research Pass CXXXII (Compact Repeat-State Weakening Portfolio Family Cardinality Law)

- Added one executable family-cardinality law so future inheritors can derive the recent width-conditioned weakening service stack from a tiny sufficient statistic instead of re-reading the whole enumeration-heavy sequence:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_family_cardinality_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_family_cardinality_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_family_cardinality_law_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_family_cardinality_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_width_conditioned_weakening_service_as_a_cardinality_law.md`
- Main local result:
  - the whole width-conditioned and width-cap weakening service stack is now pinned to the admissible-family size vector `{6,10,11,15}` inside the `15`-point primitive demand box,
  - exact-width and width-cap service shares both collapse to the same choose ratio `C(K,w)/C(15,w)` once the admissible family size `K` of a profile is fixed,
  - suffix dominates precision in the width-only service menu for the simple cardinality reason `11 > 10`, not because of a subtler stochastic accident,
  - exact-only support disappears after width `6`, precision-only after `10`, and suffix-only after `11` directly from those family sizes,
  - and any future change in the family-cardinality vector `{6,10,11,15}` would now automatically propagate to the service frontier, confidence ladder, and width-cap guarantee results as an immediate redesign signal.

## 2026-03-08 — Research Pass CXXXI (Compact Repeat-State Weakening Portfolio Width-Cap Service Guarantee)

- Added one executable width-cap service guarantee selector so future inheritors can choose weakening overshoot profiles by guaranteed admission rate over any batch width up to a cap instead of re-reasoning over the whole width set:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_cap_service_guarantee.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_cap_service_guarantee_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_cap_service_guarantee_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_cap_service_guarantee.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_reduce_width_cap_weakening_service_planning_to_the_worst_case_batch_width.md`
- Main local result:
  - robust capped-width planning is lossless under the current staircase because every efficient profile’s guaranteed service is monotone nonincreasing in width cap,
  - so selecting for any width up to `W` collapses exactly to running the old exact-width selector at endpoint width `W`,
  - `suffix_hitchhike_only` remains the only one-axis robust option worth considering and survives only through cap `5` for a 10% guarantee, cap `3` for 25%, and cap `2` for 50%,
  - any service target above `11/15 ≈ 0.733` still forces dual-axis immediately even when the width cap is only `1`,
  - and any future nonmonotone width-cap guarantee sequence or any future divergence between exact-width and width-cap selectors at the same endpoint width would now be an immediate redesign signal.

## 2026-03-08 — Research Pass CXXX (Compact Repeat-State Weakening Portfolio Service Frontier)

- Added one executable width-conditioned service frontier so future inheritors can choose weakening overshoot profiles by target admission rate when only batch width is known, and prune dominated profiles from the stochastic governance menu:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_frontier.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_frontier_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_frontier_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_frontier.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_width_only_weakening_profiles_by_service_frontier_not_full_profile_menu.md`
- Main local result:
  - `precision_hitchhike_only` is width-conditionally dominated by `suffix_hitchhike_only` at every width and is therefore not frontier-efficient under width-only uncertainty,
  - the efficient width-only service menu collapses to `exact_only`, `suffix_hitchhike_only`, and `any_single_axis_hitchhike`,
  - the best one-axis service ceiling is exactly `11/15 ≈ 0.733`, so any service target above that forces dual-axis permission even for singleton batches,
  - `suffix_hitchhike_only` is sufficient only through width `5` for a 10% target, width `3` for a 25% target, and width `2` for a 50% target,
  - and any future width where `precision_hitchhike_only` becomes frontier-efficient, or any future one-axis service ceiling above `11/15`, would now be an immediate redesign signal for the current staircase and hole-family asymmetry.

## 2026-03-08 — Research Pass CXXIX (Compact Repeat-State Weakening Portfolio Confidence Ladder)

- Added one executable confidence ladder so future inheritors can choose weakening dual-axis overshoot permission by width-conditioned prior rather than only by possibility or universal cutoff:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_confidence_ladder.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_confidence_ladder_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_confidence_ladder_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_confidence_ladder.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_use_portfolio_width_as_a_confidence_prior_for_dual_axis_weakening_permission.md`
- Main local result:
  - the dual-axis minimal-profile prior now has exact width thresholds `{0.5:4, 0.75:5, 0.9:7, 0.95:8, 0.99:10, 0.999:11}`,
  - the residual non-dual tail becomes suffix-majority at width `3`, suffix-75%-plus at width `8`, suffix-90%-plus at width `10`, and suffix-pure at width `11`,
  - suffix-only exceptions dominate every non-dual tail from width `2` onward,
  - exact-only tail mass disappears after width `6` and precision-only tail mass disappears after width `10`,
  - and any future shift in the confidence ladder `{4,5,7,8,10,11}` or suffix-tail ladder `{3,8,10,11}` would now be an immediate redesign signal for the weakening staircase and hole-family geometry.

## 2026-03-08 — Research Pass CXXVIII (Compact Repeat-State Weakening Portfolio Width Law)

- Added one executable width-conditioned guardrail law so future inheritors can choose weakening overshoot profiles by batch size rather than only by singleton demand type or aggregate portfolio family mix:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_law_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_weakening_overshoot_profiles_by_portfolio_width.md`
- Main local result:
  - dual-axis permission is never minimally required at width `1`, becomes the majority minimal profile by width `4`, and becomes universal at width `12`,
  - exact-only governance is impossible beyond width `6`, precision-only governance is impossible beyond width `10`, and suffix-only governance is impossible beyond width `11`,
  - width `11` has exactly one remaining non-dual-axis portfolio, so the one-axis exceptions are effectively exhausted before universality,
  - the closed-form width partition matches full enumeration over all `32767` non-empty portfolios,
  - and any future shift in the majority threshold (`4`) or universality threshold (`12`) would now be an immediate redesign signal for the weakening staircase and hole-family geometry.

## 2026-03-08 — Research Pass CXXVII (Compact Repeat-State Weakening Portfolio Guardrail Law)

- Added one executable portfolio guardrail selector so future inheritors can choose the weakest admissible overshoot-axis permission profile for whole batches of exact-uncertainty weakening demands instead of reasoning only demand-by-demand:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_guardrail_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_guardrail_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_guardrail_law_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_guardrail_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_overshoot_axis_profiles_for_portfolios_by_hole_family_mix.md`
- Main local result:
  - the current `15`-point primitive box induces exactly four portfolio signature classes with closed-form counts `63`, `960`, `1984`, and `29760`,
  - dual-axis permission is now exact at the workload level: it is minimally necessary iff a portfolio mixes at least one precision-hitchhike-only demand with at least one suffix-hitchhike-only demand,
  - `0` singleton demands currently require dual-axis permission but `29760` of the `32767` non-empty portfolios do,
  - so the archive can now distinguish single-request convenience from mixed-workload necessity instead of blurring them together,
  - and any future singleton that minimally needs `any_single_axis_hitchhike`, or any mixed-family portfolio that stops needing it, would now be an immediate redesign signal.

## 2026-03-08 — Research Pass CXXVI (Compact Repeat-State Weakening Overshoot-Axis Guardrails)

- Added one executable overshoot-axis guardrail selector so future inheritors can govern exact-uncertainty weakening approximations by which single-axis hitchhike families are permitted instead of treating all approximation as one undifferentiated fallback:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_overshoot_axis_guardrails.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_overshoot_axis_guardrails_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_overshoot_axis_guardrails_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_overshoot_axis_guardrails.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_govern_exact_uncertainty_weakening_approximations_by_overshoot_axis_admission_profiles.md`
- Main local result:
  - the current primitive box is now governed by four tiny admission profiles with exact coverage counts `6`, `10`, `11`, and `15`,
  - no audited primitive demand requires both hitchhike permissions simultaneously, so dual-axis permission is a portfolio-level convenience rather than a single-request necessity,
  - `precision_hitchhike_only` admits exactly the `4` deep-suffix holes while `suffix_hitchhike_only` admits exactly the `5` early/extra-precision holes,
  - `suffix_hitchhike_only` therefore covers one more demand than `precision_hitchhike_only` in the current menu,
  - and any future demand whose minimal admission profile becomes `any_single_axis_hitchhike` would now be visibly a redesign signal because it would mean both hitchhike permissions became jointly necessary for a single request.

## 2026-03-08 — Research Pass CXXV (Compact Repeat-State Weakening Primitive-Overshoot Taxonomy)

- Added one executable primitive-overshoot taxonomy so future inheritors can classify every impossible two-bundle weakening request by the exact primitive axis the current scalar menu is forced to overbuy:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_overshoot_taxonomy.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_overshoot_taxonomy_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_overshoot_taxonomy_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_overshoot_taxonomy.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_exact_uncertainty_weakening_holes_as_single_axis_hitchhike_taxes.md`
- Main local result:
  - all `9` audited primitive-demand holes resolve by **single-axis** overshoot and there are `0` mixed-axis hitchhikes in the current menu,
  - the archive can now separate the hole family into `4` precision-only hitchhikes and `5` suffix-only hitchhikes instead of treating all approximation error as one generic miss,
  - every impossible exact request still preserves one demanded primitive axis exactly and overbuys only the other, so the current scalar menu behaves like an orthogonal staircase completion law,
  - the worst current taxes are asymmetric — up to `2` extra precision units for deep suffix requests and up to `4` extra suffix units for precision-heavy requests that arrive before final suffix depth,
  - and any future mixed-axis overshoot would now be visibly a substantive redesign of the weakening geometry rather than a small threshold retune.

## 2026-03-08 — Research Pass CXXIV (Compact Repeat-State Weakening Primitive-Demand Surface)

- Added one executable primitive-demand surface so future inheritors can request desired two-bundle weakening coordinates directly and see whether the current scalar menu matches them exactly or forces hitchhiking overshoot:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_demand_surface.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_demand_surface_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_demand_surface_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_demand_surface.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_exact_uncertainty_weakening_as_a_chain_with_holes_in_two_bundle_space.md`
- Main local result:
  - the current scalar menu occupies only `6` exact coordinates inside the natural `15`-point primitive box: `(0,0)`, `(0,1)`, `(1,1)`, `(1,2)`, `(1,3)`, `(2,4)`,
  - so there are `9` audited holes, and every one of them requires hitchhiking overshoot to the least dominating budget-chain point rather than an exact match,
  - deep suffix-only demands beyond one unit and second-precision demands below the final suffix level are the two main impossible request families in the present menu,
  - and the archive can now read scalar weakening policy as a chain-shaped image in two-bundle space instead of pretending it is close to a full 2D chooser.

## 2026-03-08 — Research Pass CXXIII (Compact Repeat-State Weakening Primitive-Incidence Ledger)

- Added a two-axis factor ledger for exact-uncertainty weakening releases so inheritors can reason about the five live release cases as primitive signatures over middle-band precision relief and relaxed-suffix release.
- Added the following artifacts:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_incidence_ledger.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_incidence_ledger_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_incidence_ledger_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_incidence_ledger.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_govern_exact_uncertainty_weakening_as_a_two_axis_factor_ledger.md`
- Main findings:
  - marginal release signatures collapse to exactly three classes: suffix-only `P0_S1` at steps `1,3,4`, precision-only `P1_S0` at step `2`, and composite `P1_S1` at step `5`
  - the cumulative primitive path is exactly `(0,0)->(0,1)->(1,1)->(1,2)->(1,3)->(2,4)` over budgets `0..5`
  - after budget `2`, governance can deepen relaxed-suffix coverage at budgets `3` and `4`, but cannot buy a second precision-origin release until budget `5`
  - there is no current setting that adds more precision-origin relaxation without also adding more relaxed-floor suffix exposure

## 2026-03-08 — Research Pass CXXII (Compact Repeat-State Weakening Bundle Composition)

- Added one executable bundle-composition audit so future inheritors can collapse the exact-uncertainty weakening menu to primitive recovered savings bundles plus exact composite relations instead of treating every released value class as a separate primitive:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_bundle_composition.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_bundle_composition_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_bundle_composition_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_bundle_composition.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_full_precision_exact_uncertainty_relaxed_release_as_a_two_bundle_composition.md`
- Main local result:
  - the current weakening release menu now collapses to exactly `2` primitive bundles — `middle_precision_relief_bundle` and `relaxed_suffix_savings_bundle` — plus `1` exact composite bundle,
  - the full precision-anchor relaxed release bundle is exactly additive: its recovered steady-state savings vector equals the sum of the primitive vectors,
  - its scalar burden is additive too: threshold `23 = 11 + 12` and route shift `23 = 11 + 12`, matching the canonical anchor chain `2 -> 13 -> 25`,
  - the direct one-shot precision-to-relaxed route may compress the transient path and omit an explicit neutral-anchor stop while preserving the same scalar burden,
  - and any future redesign that breaks this vector or burden additivity is now visibly a substantive change to the weakening algebra rather than a relabeling.

## 2026-03-08 — Research Pass CXXI (Compact Repeat-State Weakening Release Value Classes)

- Added one executable value-class audit so future inheritors can price exact-uncertainty weakening budget steps by recovered steady-state savings bundles instead of only by threshold magnitudes or recovered-case counts:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_release_value_classes.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_release_value_classes_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_release_value_classes_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_release_value_classes.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_equal_value_exact_uncertainty_weakening_releases_as_cheapest_shift_first.md`
- Main local result:
  - the five audited weakening budget steps collapse to exactly `3` recovered savings bundles,
  - one repeated class — `relaxed_suffix_savings_bundle` — covers budget steps `1`, `3`, and `4`, always recovering the same steady-state gains `{exact_hard_cap:2, checkpoints:3, anchor_slack:1, band_width:3}` while the required one-shot route shift rises strictly `7 < 12 < 17`,
  - so those later breakpoints are coverage extensions for harder-to-move live states rather than richer steady states,
  - while budget step `2` is the unique middle-band precision-relief bundle and budget step `5` is the unique full relaxed release from the precision anchor,
  - and the archive can now audit weakening menus as value classes plus move costs instead of as raw threshold numerology alone.

## 2026-03-08 — Research Pass CXX (Compact Repeat-State Weakening Budget Live-Action Surface)

- Added one executable live-surface audit so future inheritors can read exact-uncertainty weakening budgets as concrete action flips in the saved-state controller instead of only as abstract threshold or recovered-case levels:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_live_action_surface.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_live_action_surface_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_live_action_surface_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_live_action_surface.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_exact_uncertainty_weakening_budgets_by_live_action_flips.md`
- Main local result:
  - the default saved-state matrix has `18` live state/floor cases, and every budget increment releases exactly `1` additional weakening case so the released live weakening count matches the budget exactly: `{0,1,2,3,4,5}`,
  - strengthenings stay constant at `7` across the whole menu, so weakening budgets never perturb the mandatory strengthening side of the controller,
  - budget steps `1` and `4` are transient-boundary releases (`stabilize -> weaken` at states `18` and `8` under floor `0.84`), while steps `2`, `3`, and `5` are canonical-anchor releases (`hold -> weaken`),
  - and future policy edits can now be audited as named operational flips in the live controller instead of vague changes in overall permissiveness.

## 2026-03-08 — Research Pass CXIX (Compact Repeat-State Weakening Budget Selector)

- Added one executable budget selector so future inheritors can choose exact-uncertainty weakening policy by the number of deferred base weakening cases they are willing to restore instead of by threshold numerology:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_selector.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_selector_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_selector_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_selector.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_exact_uncertainty_weakening_regimes_by_recovered_base_case_budget.md`
- Main local result:
  - the exact five-case weakening ladder now compresses to a governance budget over recovered base weakening cases `{0,1,2,3,4,5}` with no gaps or redundant budget levels,
  - the budget-to-threshold map is exact: `{0:0, 1:7, 2:11, 3:12, 4:17, 5:23}` unique appends,
  - budget `2` is the highest setting that still forbids neutral-anchor relaxed release, budget `3` is the first that admits it, budget `4` is the first that admits direct entry-boundary release `8→25`, and budget `5` recovers full base-policy weakening,
  - each additional budget unit restores exactly one concrete weakening case in audited order, so future relaxation has a visible marginal meaning instead of a vague “more permissive” label,
  - and any future policy change that skips a budget count or makes two budgets equivalent is now visibly a substantive redesign of the weakening menu.

## 2026-03-08 — Research Pass CXVIII (Compact Repeat-State Weakening Recovery Ladder)

- Added one executable recovery-ladder pass so future inheritors can audit exact-uncertainty weakening thresholds as a serial restoration of concrete base weakening cases instead of a raw frontier of abstract breakpoints:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_recovery_ladder.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_recovery_ladder_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_recovery_ladder_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_recovery_ladder.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_exact_uncertainty_weakening_thresholds_as_prefixes_of_a_five_case_recovery_ladder.md`
- Main local result:
  - the default saved-state matrix still has exactly `5` optional weakening cases, and the weakening breakpoints `{7, 11, 12, 17, 23}` recover them in a perfectly serial order with no coupled releases,
  - the recovered cases are exactly: suffix-only relaxed release from `18` at `7`, middle-band precision relief `2→13` at `11`, neutral-anchor relaxed release `13→25` at `12`, direct entry-boundary relaxed release `8→25` at `17`, and direct precision release `2→25` at `23`,
  - the six named weakening regimes therefore compress equivalently to recovered-case counts `{0,1,2,3,4,5}`,
  - and any future breakpoint insertion, merger, or reorder is now visibly a substantive policy change because it changes the recovered case prefix rather than just renaming a band.

## 2026-03-08 — Research Pass CXVII (Compact Repeat-State Weakening Capability Selector)

- Added one executable capability selector so future inheritors can choose the smallest exact-uncertainty weakening regime that satisfies an operator promise bundle instead of inferring thresholds from the regime table by hand:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_capability_selector.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_capability_selector_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_capability_selector_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_capability_selector.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_exact_uncertainty_weakening_regimes_by_capability_promises_not_threshold_numerology.md`
- Main local result:
  - the exact minimal thresholds now map directly to promised capabilities: any stronger-tier relaxed release `7`, middle-band precision relief `11`, neutral-anchor relaxed release `12`, direct entry-boundary relaxed release `17`, and direct precision-anchor relaxed release `23`,
  - threshold `11` is the only selector answer that adds middle-band precision relief while still forbidding relaxed-basin growth beyond neutral exit boundary `18`,
  - and some promise bundles are genuinely impossible in the current menu, especially any request that simultaneously demands neutral-anchor or precision-anchor relaxed release while forbidding relaxed-basin growth.

## 2026-03-08 — Research Pass CXVI (Compact Repeat-State Weakening Regime Normal Form)

- Added one executable normal-form pass so future inheritors can choose exact-uncertainty weakening hysteresis by named behavior regimes instead of memorizing raw threshold integers:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_regime_normal_form.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_regime_normal_form_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_regime_normal_form_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_regime_normal_form.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_exact_uncertainty_weakening_thresholds_by_named_regime_not_raw_numbers.md`
- Main local result:
  - the numeric weakening threshold now compresses to `6` exact named regimes over bands `0–6`, `7–10`, `11`, `12–16`, `17–22`, and `23+`,
  - threshold `11` is the unique off-axis regime: it admits only the middle-band precision release `2→13` and does **not** enlarge the relaxed-floor release basin beyond what threshold `7` already allows,
  - thresholds `12–16` and `17–22` share the same eventual anchor counts `{"2": 7, "13": 6, "25": 5}`, but `12–16` reaches relaxed anchor `25` from entry boundary `8` only through staged release while `17–22` allows the direct `8→25` jump,
  - full base-policy recovery still begins only at threshold `23`, which is the first regime that can discharge precision anchor `2` directly under relaxed floors,
  - and the archive now exposes threshold selection as a semantic regime choice instead of a raw shift-magnitude knob.

## 2026-03-08 — Research Pass CXV (Compact Repeat-State Weakening Hysteresis Closure)

- Added one executable closure pass so future inheritors can trace a fixed weakening-hysteresis threshold to its eventual canonical anchor under persistent exact-uncertainty requests instead of reading only the first one-shot move:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis_closure.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis_closure_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis_closure_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis_closure.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_trace_fixed_weakening_thresholds_to_their_eventual_canonical_anchor_under_persistent_requests.md`
- Main local result:
  - fixed threshold bands now induce exact eventual anchor basins over the default `18` saved-state × floor cases, with lowest-threshold closure counts `{"2": 8, "13": 8, "25": 2}` and full-release counts `{"2": 6, "13": 6, "25": 6}`,
  - boundary entry state `8` under a relaxed floor is the key staged-release case: threshold `12` is already enough to reach relaxed anchor `25` eventually via `8→13→25`, even though the direct `8→25` jump still needs threshold `17`,
  - thresholds `12–16` and `17–22` therefore have the same eventual anchor counts but different settling depth (`3` cycles versus `2`),
  - precision anchor `2` remains truly sticky under relaxed floors until the full outer-anchor threshold `23`, because the cheapest-tier controller has no intermediate staged release from that canonical anchor,
  - and the minimum thresholds for eventual relaxed-floor arrival at `25` are `{2:23, 8:12, 13:12, 18:7, 19:0, 25:0}`.

## 2026-03-08 — Research Pass CXIV (Compact Repeat-State Weakening Hysteresis Overlay)

- Added one optional executable hysteresis overlay so future inheritors can defer only large one-shot exact-uncertainty weakenings without ever deferring mandatory strengthenings or reopening dwell search:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_only_defer_exact_uncertainty_weakening_when_one_shot_shift_is_too_large.md`
- Main local result:
  - only weakening is safely deferrable because every cheapest-tier weakening leaves the current stronger tier request-feasible, while strengthenings remain mandatory,
  - the base saved-state matrix's `5` weakening cases have exact one-shot shift breakpoints `{7, 11, 12, 17, 23}` unique appends,
  - threshold bands now form a tiny frontier from full inertia `0–6` (all `5` weakenings deferred) to full base policy `23+` (all `5` weakenings admitted),
  - deferred boundary weakenings from `8` or `18` no longer strand the system: they recenter to canonical anchor `13` before waiting,
  - and the overlay preserves all resolver blockers, so infeasible high-floor positive-slack requests still fail fast.

## 2026-03-08 — Research Pass CXIII (Compact Repeat-State Saved-State Resolver)

- Added one boundary-aware executable resolver so future inheritors can route directly from the full saved exact-uncertainty control-state menu `{2,8,13,18,19,25}` instead of hand-composing the boundary protocol with the canonical-anchor controller:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_saved_state_resolver.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_saved_state_resolver_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_saved_state_resolver_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_saved_state_resolver.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_extend_exact_uncertainty_control_from_canonical_anchors_to_saved_boundary_states.md`
- Main local result:
  - exact request resolution now spans `6` saved states across `{2,8,13,18,19,25}` and compresses to an `18`-case default matrix over saved state × floor interval,
  - same-band boundary cases are now named explicitly as **stabilize** rather than being misread as hold or as fresh search, with exactly `3` stabilization cases in the default matrix,
  - the default matrix decomposes into `3` holds, `3` stabilizations, `5` weakenings, and `7` strengthenings,
  - the maximum stabilization-only tax is only `6` unique appends, so saved boundary states can be repaired cheaply without reopening dwell search,
  - and the resolver preserves oracle blockers, so impossible high-floor positive-slack bundles still fail fast instead of being hidden by route glue.

## 2026-03-08 — Research Pass CXII (Compact Repeat-State Canonical Anchor Control Law)

- Added one executable steady-state control law so future inheritors can choose hold/strengthen/weaken/infeasible directly from the current canonical anchor and a declared exact-uncertainty request bundle:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_canonical_anchor_control.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_canonical_anchor_control_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_canonical_anchor_control_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_canonical_anchor_control.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_the_cheapest_feasible_exact_tier_before_retuning_canonical_anchors.md`
- Main local result:
  - canonical steady-state retuning now compresses to a `3×3` exact control matrix over current anchor `{2,13,25}` and required-floor interval,
  - the right selector is the **cheapest feasible** exact tier, not the strongest feasible tier, so relaxed requests stop carrying avoidable precision premiums,
  - the default nonbinding-budget matrix has exactly `3` holds, `3` weakenings, and `3` strengthenings,
  - the largest release is `near_exact→lower_guarantee`, which frees `8` hard-cap steps and `9` pre-amortization checkpoints while expanding slack by `6` and dwell width by `13`,
  - and infeasible request bundles now surface exact oracle blockers before any retuning route is discussed.

## 2026-03-08 — Research Pass CXI (Compact Repeat-State Canonical Anchor Path Atlas)

- Added one exact route atlas plus executable planner so future inheritors can retune among canonical exact-uncertainty anchors without reopening full dwell search:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_anchor_routes.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_canonical_anchor_path_atlas_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_canonical_anchor_path_atlas_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_canonical_anchor_path_atlas.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_one_shot_exact_uncertainty_anchor_retuning_as_a_small_exact_route_atlas.md`
- Main local result:
  - one-shot steady-mode retuning among canonical anchors now compresses to `6` exact ordered routes over `{2, 13, 25}`,
  - weakening from precision is staircase-shaped (`2→8→13` or `2→8→19→25`) while strengthening to precision collapses directly (`13→2`, `25→2`),
  - adjacent anchor changes cost exact total shifts of `11` and `12` unique appends, while the outer-anchor shift remains symmetric at `23`,
  - but the outer-anchor **phase count** is asymmetric: `near_exact→lower_guarantee` needs `3` steps while `lower_guarantee→near_exact` needs only `1`,
  - so the archive now has a tiny executable path atlas for one-shot floor-driven retuning instead of fresh dwell search.

## 2026-03-08 — Research Pass CX (Compact Repeat-State Uncertainty Boundary Stabilization Protocol)

- Added one exact stabilization protocol card so future inheritors separate fast feasibility repair from steady-mode naming instead of mixing boundary landings with canonical anchors:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_boundary_stabilization_protocol_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_boundary_stabilization_protocol_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_boundary_stabilization_protocol.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_repair_floor_driven_exact_uncertainty_changes_at_support_boundaries_and_only_then_recenter_to_canonical_anchors.md`
- Main local result:
  - floor-driven exact uncertainty changes now have a two-phase mechanical rule: repair to the correct support boundary first, then recenter to the canonical steady-mode anchor only if that destination band becomes the new operating mode,
  - the stable inheritor-facing anchors remain `{2, 13, 25}`, while the transient feasibility landings remain `{2, 8, 18, 19}`,
  - near-optimal boundary repairs `8→13` and `18→13` are exactly symmetric at `5` dwell steps each,
  - the relaxed suffix stabilizes from entry boundary `19` to canonical anchor `25` in `6` dwell steps,
  - and precision singleton `2` needs no stabilization step because its first surviving support point and canonical anchor coincide.

## 2026-03-08 — Research Pass CIX (Compact Repeat-State Uncertainty Floor-Retuning Compass)

- Added one exact compass card so future inheritors can treat floor-driven exact uncertainty retuning as movement among four boundary landmarks instead of a search across every live dwell point:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_retuning_compass_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_retuning_compass_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_floor_retuning_compass.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_route_floor_driven_exact_uncertainty_retuning_through_a_four_point_boundary_compass.md`
- Main local result:
  - the full current first-step floor-driven retuning problem now compresses to the exact boundary compass `{2, 8, 18, 19}`,
  - stronger-floor repairs still route through `{18, 2}`, while weaker-floor widening routes through `{8, 19}`,
  - this shrinks first-step retuning from `26` live support points to `4` exact landmarks, a `6.5x` compression,
  - `2` remains the terminal precision landing point, `8` the entry boundary into the strong non-fragile band, `18` the exit boundary from the relaxed suffix into the strongest surviving non-precision support, and `19` the entry boundary into the relaxed suffix,
  - so interior dwells can now be treated as second-step refinements after the correct compass target has been evaluated.

## 2026-03-08 — Research Pass CVIII (Compact Repeat-State Uncertainty Floor-Relaxation Boundary Targets)

- Added one exact boundary-target card so future inheritors can reclaim dwell freedom quickly when a required exact uncertainty floor weakens:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_relaxation_boundary_targets_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_relaxation_boundary_targets_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_floor_relaxation_boundary_targets.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_jump_to_the_nearest_newly_unlocked_support_boundary_when_weakening_exact_uncertainty_floors.md`
- Main local result:
  - one-notch weaker-floor widening repairs now compress to just two exact landing points, `{8, 19}`,
  - weakening the precision singleton `{2}` into the near-optimal band should target dwell `8` first, because neutral-band interior points `9–18` are dominated as first widening repairs on right-shift distance,
  - weakening the neutral band `[8,18]` into the relaxed lane should target dwell `19` first, because relaxed-suffix interior points `20–32` are dominated as first widening repairs on right-shift distance,
  - this shrinks one-notch weaker-floor widening search from `25` newly unlocked support points to `2` exact boundary targets,
  - and even full relaxation from precision still starts at dwell `8`; dwell `19` only becomes the next boundary target if the relaxed suffix itself is desired.

## 2026-03-08 — Research Pass CVII (Compact Repeat-State Uncertainty Floor-Upgrade Boundary Targets)

- Added one exact boundary-target card so future inheritors can jump straight to the first surviving support boundary when a fixed live dwell region needs a stronger current exact uncertainty floor:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_upgrade_boundary_targets_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_upgrade_boundary_targets_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_floor_upgrade_boundary_targets.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_jump_to_the_nearest_surviving_support_boundary_when_strengthening_exact_uncertainty_floors.md`
- Main local result:
  - all current stronger-floor repairs from live dwell regions now compress to just two exact landing points, `{18, 2}`,
  - the relaxed suffix `[19,32]` should target dwell `18` first for floor requests in `(0.870482, 0.980481]`, because neutral-band interior points `8–17` are dominated as first repairs on left-shift distance,
  - any request above floor `0.980481` now targets dwell `2` directly from either `[19,32]` or `[8,18]`,
  - this shrinks current stronger-floor retuning from `26` live support points to `2` exact boundary targets whenever the only problem is a stricter floor,
  - and once the deployment already sits at the relevant boundary target, the next step becomes menu/frontier evaluation rather than local dwell search.

## 2026-03-08 — Research Pass CVI (Compact Repeat-State Uncertainty Floor-Upgrade Dwell Jumps)

- Added one exact directionality card so future inheritors stop searching the wrong side of dwell space when a fixed live region needs a stronger current exact uncertainty floor:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_upgrade_dwell_jump_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_upgrade_dwell_jump_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_floor_upgrade_dwell_jump.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_search_left_not_right_when_strengthening_exact_uncertainty_floors_from_fixed_dwell_regions.md`
- Main local result:
  - every stronger current exact floor repair from a live dwell region is now explicit as a **leftward** jump, never a rightward sweep,
  - strengthening the relaxed suffix `[19,32]` into the neutral band `[8,18]` requires a left shift of `1–14` dwell steps, with representative anchor jump `25→18`,
  - strengthening either `[19,32]` or `[8,18]` all the way to the near-exact precision singleton requires a left collapse to dwell `2`, with representative jump `13→2` from the neutral band,
  - the archive can now say plainly that stronger exact floors are reached by region jumps to the left rather than by spending time sweeping higher dwell values,
  - and once a deployment already sits at dwell `2`, stronger saved exact floors stop being a retuning problem and become a frontier-extension problem.

## 2026-03-08 — Research Pass CV (Compact Repeat-State Uncertainty Fixed-Dwell Budget Ceilings)

- Added one exact fixed-dwell budget-ceiling card so future inheritors stop wasting cap or checkpoint budget on a target-dwell region whose strongest current exact floor is already saturated:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_fixed_dwell_budget_ceiling_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_fixed_dwell_budget_ceiling_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_fixed_dwell_budget_ceiling.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_fixed_dwell_regions_as_budget_ceiling_modes_under_exact_uncertainty.md`
- Main local result:
  - each live fixed-dwell region now has an explicit exact floor ceiling that extra local budget cannot improve in place,
  - dwell `[8,18]` tops out at exact floor `0.980481` and only upgrades further by jumping to dwell `{2}`,
  - dwell `[19,32]` tops out at exact floor `0.870482` and only upgrades further by jumping into `[8,18]`,
  - dwell `{2}` is already the top saved exact ceiling at `0.999822`, so extra budget there buys no stronger current exact floor at all,
  - and dead dwell regions (`<2`, `[3,7]`, `>32`) are now explicit budget-impotent gaps that cannot be entered just by throwing extra cap or checkpoints at them.

## 2026-03-08 — Research Pass CIV (Compact Repeat-State Uncertainty Requirement-Creep Buffer)

- Added one exact requirement-creep buffer card so future inheritors can see how much upward floor drift each rounded public label can absorb before a stronger exact tier is truly forced:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_requirement_creep_buffer_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_requirement_creep_buffer_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_requirement_creep_buffer.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_exact_0_95_as_the_best_current_buffer_against_requirement_creep.md`
- Main local result:
  - the exact `0.95` lane is now explicit as the best current hedge against silent upward requirement drift,
  - its hidden certified buffer above the rounded public label is `+0.030481`, which exceeds the relaxed `0.85` lane's `+0.020482` and the fragile `0.99` lane's `+0.009822`,
  - that makes exact `0.95` the tier with both the largest absolute and largest relative requirement-creep buffer,
  - so the archive can now say plainly that “slightly above 0.95” is still often a `0.95` request rather than an automatic reason to pay the `0.99` precision premium,
  - while exact `0.99` now carries an explicit frontier-overflow warning because it sits only `0.000178` below the current saved exact ceiling.

## 2026-03-08 — Research Pass CIII (Compact Repeat-State Uncertainty Dwell-Commitment Tariff)

- Added one exact dwell-commitment tariff card so future inheritors can price fixed live dwell regions against the neutral exact `8–18` band instead of treating every live region as equally attractive:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_commitment_tariff_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_commitment_tariff_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_dwell_commitment_tariff.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_dwell_8_through_18_as_the_neutral_exact_uncertainty_zone_and_price_other_live_regions_as_commitments.md`
- Main local result:
  - dwell `8–18` is now explicit as the neutral exact uncertainty zone whenever dwell is not physically forced,
  - insisting on dwell `2` now has an exact avoidable precision premium below floor `0.980481`: `+6` hard-cap steps, `+6` pre-amortization checkpoints, slack collapse from `5` to `0`, and width collapse from `11` to `1` for only `+0.019341` more exact floor,
  - insisting on dwell `19–32` now has an exact relaxed-only subsidy profile: `-2` hard-cap steps, `-3` pre-amortization checkpoints, `+1` slack, and `+3` width, but at a cost of `-0.109999` exact floor versus the neutral band,
  - master-calendar amortization now explicitly removes only the checkpoint part of these dwell commitments, not their cap or fragility effects,
  - and the archive can now say plainly that `{2}` and `[19,32]` are special commitments while `[8,18]` is the default exact operating zone.

## 2026-03-08 — Research Pass CII (Compact Repeat-State Uncertainty Dwell-Freedom Tariff)

- Added one exact dwell-freedom tariff card so future inheritors can price tighter uncertainty guarantees by lost live dwell support, not just by cap and checkpoint increases:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_freedom_tariff_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_freedom_tariff_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_dwell_freedom_tariff.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_price_higher_exact_uncertainty_guarantees_by_lost_dwell_freedom_not_just_cap_and_checkpoints.md`
- Main local result:
  - exact `0.95` is now explicit as the **last** tier with continuous non-precision dwell freedom,
  - tightening `0.85 -> 0.95` loses `14` live dwell targets for `+0.109999` certified floor and still keeps the exact `8–18` band alive,
  - tightening `0.95 -> 0.99` loses `11` of the remaining `12` live dwell targets for only `+0.019341` more floor,
  - the first tightening step is therefore `4.469283x` more floor-efficient per lost dwell than the second,
  - and the archive can now say plainly that exact `0.99` is not only a cap/checkpoint premium but also a near-total collapse of retuning freedom.

## 2026-03-08 — Research Pass CI (Compact Repeat-State Uncertainty Target-Dwell Atlas)

- Added one exact target-dwell atlas so future inheritors can start from a deployment’s fixed dwell shape instead of re-deriving which uncertainty-safe exact tier even survives there:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_target_dwell_atlas_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_target_dwell_atlas_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_target_dwell_atlas.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_exact_uncertainty_tiers_from_a_target_dwell_atlas_when_dwell_is_pre_committed.md`
- Main local result:
  - fixed dwell `2` is now explicit as a precision-only singleton owned by exact `0.99`, so even low-floor requests must pay hard cap `11` and checkpoint count `14` if they insist on that dwell,
  - fixed dwell `8–18` is now explicit as the strongest non-fragile exact band, carrying floors up to `0.980481` on hard cap `5`,
  - fixed dwell `19–32` is now explicit as relaxed-only support capped at floor `0.870482`, which cannot be upgraded by spending more cap or checkpoints,
  - dwell `3–7` remains dead exact search space and dwells below `2` or above `32` remain outside the current exact menu,
  - and the archive can now answer dwell-first deployment questions directly instead of forcing future sessions to infer them from floor-first selector cards.

## 2026-03-08 — Research Pass C (Compact Repeat-State Uncertainty Request Oracle)

- Added one small executable request oracle so future inheritors can classify an exact uncertainty-safe request bundle into strongest feasible tier or explicit tier deficits without manually merging several selector cards:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_oracle.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_request_oracle_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_request_oracle_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_request_oracle.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_route_exact_uncertainty_requests_through_one_deficit_oracle_before_retuning.md`
- Main local result:
  - the archive now evaluates exact uncertainty requests in one deterministic order: required floor, target dwell against floor-conditioned live support, then cap, checkpoints, slack, and width,
  - the oracle returns the strongest feasible exact tier when one exists and otherwise exposes explicit shortfalls for each floor-eligible tier,
  - checked witness bundles now show the exact `0.95` lane as the strong non-fragile default, positive slack as an immediate blocker for high-floor `0.99` requests, floor-pruned dwell `20` as an exact no-go above floor `0.870482`,
  - and relaxed requests at cap `2` now fail cleanly as a one-step hard-cap underflow rather than as a vague no-tier case.

## 2026-03-08 — Research Pass XCIX (Compact Repeat-State Uncertainty Floor-Conditioned Dwell Support)

- Added one exact floor-conditioned dwell-support ladder so future inheritors can prune impossible dwell search regions directly from the required worst-case preserved-gain floor before tuning other knobs:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_conditioned_dwell_support_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_conditioned_dwell_support_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_floor_conditioned_dwell_support.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_prune_dwell_search_by_required_uncertainty_floor_before_tuning_other_knobs.md`
- Main local result:
  - required floors in `[0, 0.870482]` now map to exact dwell support `{2} ∪ [8, 32]`,
  - required floors in `(0.870482, 0.980481]` now map to exact dwell support `{2} ∪ [8, 18]`,
  - required floors in `(0.980481, 0.999822]` now collapse exact dwell support to the singleton precision point `{2}`,
  - and required floors above `0.999822` now explicitly leave **no current exact dwell support** inside the saved menu.## 2026-03-08 — Research Pass XCVIII (Compact Repeat-State Uncertainty Repair Guide)

- Added one exact smallest-relaxation repair guide so future inheritors can fix impossible exact uncertainty-safe request bundles quickly instead of merely rejecting them:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_repair_guide_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_repair_guide_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_repair_guide.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_repair_impossible_exact_uncertainty_requests_by_the_smallest_current_menu_relaxation.md`
- Main local result:
  - most current exact-menu no-go bundles are only **one notch** away from feasibility: cap `2 -> 3`, checkpoints `4 -> 5`, slack `7 -> 6`, and width `15 -> 14` all restore the relaxed exact `0.85` lane,
  - high-floor requests above `0.980481` with positive slack or width above `1` now come with an explicit forked repair: clip the floor back into the exact `0.95` band or accept the fragile exact `0.99` precision point,
  - dwell inside the dead zone `3–7` now repairs by jumping directly to dwell `8` for non-fragile operation or dwell `2` for precision,
  - pre-amortization checkpoint underflow can now be repaired either locally by adding one checkpoint or globally by pre-registering the master calendar,
  - and required floors above `0.999822` are now explicit frontier overflows that cannot be repaired structurally inside the current exact menu.

## 2026-03-08 — Research Pass XCVII (Compact Repeat-State Uncertainty Infeasibility Screen)

- Added one exact fail-fast screen so future inheritors can reject impossible exact uncertainty-safe request bundles immediately instead of wasting time retuning inside the current menu gaps:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_infeasibility_screen_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_infeasibility_screen_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_infeasibility_screen.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_fail_fast_on_exact_uncertainty_requests_that_the_current_menu_cannot_satisfy.md`
- Main local result:
  - the current exact menu can now fail fast on hard-cap budgets below `3`, pre-amortization checkpoint budgets below `5`, certified floors above `0.999822`, minimum slack `7+`, and minimum band width `15+`,
  - any request above floor `0.980481` that also demands positive slack or band width above `1` now resolves immediately to **no current exact tier** rather than to a mistaken near-exact escalation,
  - dwell `3–7` is now explicitly treated as an internal exact gap and dwell below `2` or above `32` as outside the current exact menu,
  - the relaxed exact `0.85` lane is the boundary witness that keeps the menu alive at minimum cap, minimum checkpoints, maximum slack, and maximum width,
  - and the exact `0.95` lane is therefore the strongest live non-fragile guarantee while exact `0.99` remains only the ceiling witness for absolute floor.

## 2026-03-08 — Research Pass XCVI (Compact Repeat-State Uncertainty Menu Basis)

- Added one exact irreducibility card so future inheritors stop trying to collapse the current uncertainty-safe menu into fewer tiers and silently losing live request regions:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_menu_basis_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_menu_basis_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_menu_basis.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_keep_the_current_exact_uncertainty_menu_as_an_irreducible_three_tier_basis.md`
- Main local result:
  - the current exact uncertainty-safe menu is an **irreducible three-tier basis**, with removable-tier count `0`,
  - exact `0.85` is the cap-limited relaxed basis row because without it hard-cap budgets `3–4` lose every current exact option,
  - exact `0.95` is the only positive-slack bridge above floor `0.870482`, so removing it destroys the current exact bridge between the relaxed band and the fragile precision point,
  - exact `0.99` is the only surviving current exact row above floor `0.980481`,
  - and future simplification proposals should therefore be forced to produce replacement evidence for each of those three basis regions before the archive accepts them.

## 2026-03-08 — Research Pass XCV (Compact Repeat-State Uncertainty Precision-Escalation Gate)

- Added one exact escalation gate so future inheritors only pay for the near-exact uncertainty tier when both the required preservation floor and the fragility budget force it:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_precision_escalation_gate_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_precision_escalation_gate_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_precision_escalation_gate.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_only_pay_for_near_exact_uncertainty_when_the_requirement_and_fragility_budget_both_force_it.md`
- Main local result:
  - the exact `0.99` tier is only justified once the required worst-case floor exceeds the exact `0.95` ceiling of `0.980481`,
  - before calendar amortization that escalation additionally requires checkpoint budget `14`, while after amortization the only blocker removed is checkpoint budget itself,
  - the near-exact tier still requires hard cap `11`, minimum slack `0`, and band width `1`,
  - so any requirement above `0.980481` that also demands positive slack leaves **no current exact tier**,
  - and any requirement at or below `0.980481` should stay on the exact `0.95` lane even if the deployment could technically afford near-exact precision.

## 2026-03-08 — Research Pass XCIV (Compact Repeat-State Uncertainty Dwell-Coverage Topology)

- Added one exact dwell-topology card so future inheritors can stop wasting retuning effort inside parts of dwell space that are outside the saved exact uncertainty-certified menu:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_coverage_topology_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_coverage_topology_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_dwell_coverage_topology.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_dwell_3_through_7_as_an_exact_uncertainty_gap_not_a_retuning_target.md`
- Main local result:
  - the current exact menu covers dwell `2` as an isolated precision point and then resumes only at dwell `8`,
  - dwell `3` through `7` is therefore a real five-step internal gap in the saved exact uncertainty-certified menu,
  - the exact `0.95` and `0.85` bands join contiguously at dwell `18/19`, so the continuous non-precision exact menu is `8–32`,
  - and any deployment that needs positive slack or band width greater than `1` should skip the small-dwell gap entirely and jump directly to dwell `8` or higher.

## 2026-03-08 — Research Pass XCIII (Compact Repeat-State Uncertainty Guarantee-Threshold Selector)

- Added one exact requirement-threshold selector so future inheritors can choose the cheapest exact uncertainty-safe lane from the *actual certified worst-case preservation floor* instead of overreacting to the rounded public tier labels:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_guarantee_threshold_selector_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_guarantee_threshold_selector_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_guarantee_threshold_selector.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_select_exact_uncertainty_tiers_by_actual_certified_gain_share_floors_not_rounded_labels.md`
- Main local result:
  - the current rounded labels `0.85`, `0.95`, and `0.99` are conservative names, not tight exact floors,
  - the actual certified worst-case floors are `0.870482`, `0.980481`, and `0.999822`, leaving hidden headroom `+0.020482`, `+0.030481`, and `+0.009822` respectively,
  - the exact `0.95` lane is therefore still the cheapest certifiable choice for any required floor in `(0.870482, 0.980481]`,
  - the exact `0.99` precision tier is only necessary once the required floor exceeds `0.980481`,
  - and requirements above `0.999822` remain outside the current exact certified menu.

## 2026-03-08 — Research Pass XCII (Compact Repeat-State Canonical Anchor Labels)

- Added one exact naming-stability card so future inheritors can stop mixing the older overlap-midpoint anchors with the newer exact certified-band labels:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_canonical_anchor_labels_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_canonical_anchor_labels_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_canonical_anchor_labels.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_name_exact_uncertainty_tiers_by_the_centers_of_their_certified_dwell_bands.md`
- Main local result:
  - exact tier names should now come from the centers of the **exact certified bands**, not from the older broad-overlap midpoints,
  - exact `0.99` therefore keeps canonical dwell label `2`,
  - exact `0.95` uses canonical dwell label `13` because band `8–18` has a unique center at `13`,
  - exact `0.85` uses canonical dwell label `25` because band `19–32` has tied centers `25` and `26`, and the archive now breaks that tie deterministically toward the lower dwell,
  - so the old overlap anchors `1`, `9`, and `16` can now be treated as historical scaffolding rather than live naming competitors.

## 2026-03-08 — Research Pass XCI (Compact Repeat-State Post-Amortization Selector)

- Added one exact future-proof selector so future inheritors can stop treating checkpoint counts as an active bottleneck after the full sparse master calendar has already been pre-registered:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_post_amortization_selector_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_post_amortization_selector_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_post_amortization_selector.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_select_future_proof_uncertainty_tiers_by_cap_and_tolerance_once_the_master_calendar_is_pre_registered.md`
- Main local result:
  - once the full `17`-point master calendar is sunk cost, checkpoint budgets drop out of the current exact uncertainty-tier selector,
  - exact `0.99` remains available only for precision deployments with hard cap `11`, zero minimum slack, and band width `1`,
  - exact `0.95` becomes the strongest future-proof non-fragile default because it survives hard-cap budgets `5`–`11`, positive minimum slack up to `5`, and band-width requirements up to `11`,
  - exact `0.85` is the fallback when cap is only `3`–`4` or when tolerance demands rise to slack `6` / band width `12`–`14`,
  - and no current exact tier survives minimum slack `7+` or minimum band width `15+`.

## 2026-03-08 — Research Pass XC (Compact Repeat-State Master Calendar Amortization)

- Added one exact calendar-pricing card so future inheritors can distinguish immediate per-mode checkpoint burden from the one-time cost of pre-registering the full sparse master schedule:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_master_calendar_amortization_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_master_calendar_amortization_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_master_calendar_amortization.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_amortize_compact_repeat_sidecar_calendar_costs_with_one_pre_registered_master_schedule.md`
- Main local result:
  - the full master audit calendar stays the same sparse `17`-point set: `9, 15, 24, 31, 38, 47, 54, 56, 63, 79, 111, 143, 159, 191, 230, 239, 255`,
  - once that master calendar is pre-registered, every current switch among the trusted fallback and the exact `0.85`, `0.95`, and `0.99` tiers requires `0` new audit dates,
  - the future-proofing gaps are now exact: trusted fallback `+13` dates, exact `0.85` `+12`, exact `0.95` `+9`, exact `0.99` only `+3`,
  - so the archive can now trade immediate calendar size against future switching flexibility explicitly instead of rediscovering the same schedule churn later.

## 2026-03-08 — Research Pass LXXXIX (Compact Repeat-State Uncertainty Premium vs Trusted Repeat)

- Added one exact epistemic-premium card so future inheritors can price what repeat-estimate uncertainty actually costs relative to the trusted-repeat rewrite-budgeted fallback instead of treating uncertainty-safe operation as a vague tax:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_premium_vs_trusted_repeat_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_premium_vs_trusted_repeat_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_premium_vs_trusted_repeat.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_price_repeat_estimate_uncertainty_as_a_small_explicit_operating_premium.md`
- Main local result:
  - the trusted-repeat rewrite-budgeted baseline preserves `0.968419` of full dynamic savings at the focal `0.18` repeat point with `4` rewrites and checkpoints `56, 111, 159, 239`,
  - the exact `0.95` uncertainty-safe lane buys full-band robustness for only `+1` hard-cap step and net `+4` checkpoints while also improving focal `0.18` preservation by `0.012062`,
  - the exact `0.85` uncertainty-safe lane is not a monotone uncertainty tax at all because it is cheaper than the trusted-repeat fallback on transition cap (`3` instead of `4`) and only `+1` checkpoint wider, but it gives back `0.097937` focal gain share,
  - and the exact `0.99` lane is the real precision-premium jump at `+7` cap steps and net `+10` checkpoints over the trusted-repeat fallback.

## 2026-03-08 — Research Pass LXXXVIII (Compact Repeat-State Uncertainty Constraint Selector)

- Added one exact feasibility selector so future inheritors can pick the strongest still-certifiable uncertainty tier by the tightest real bottleneck instead of manually reconciling separate cap, checkpoint, and tolerance cards:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_constraint_selector_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_constraint_selector_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_constraint_selector.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_select_exact_uncertainty_tiers_by_the_tightest_feasibility_bottleneck.md`
- Main local result:
  - hard-cap budgets now map to the strongest exact tiers as `none` below `3`, relaxed exact `0.85` at `3`–`4`, near-optimal exact `0.95` at `5`–`10`, and near-exact `0.99` at `11+`,
  - checkpoint budgets map the same structure as `none` below `5`, `0.85` at `5`–`7`, `0.95` at `8`–`13`, and `0.99` at `14+`,
  - any positive minimum anchor-slack requirement immediately rules out the `0.99` precision tier,
  - minimum slack `1`–`5` still allows `0.95`, minimum slack `6` forces `0.85`, and minimum slack `7+` leaves no current exact tier,
  - so the archive can now select by the tightest bottleneck instead of by informal preference.

## 2026-03-08 — Research Pass LXXXVII (Compact Repeat-State Uncertainty Dwell-Tolerance Staircase)

- Added one exact tuning-slack card so future inheritors can see how brittle each certified uncertainty lane really is instead of reasoning only from caps and checkpoints:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_tolerance_staircase_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_tolerance_staircase_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_dwell_tolerance_staircase.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_near_exact_uncertainty_lanes_as_precision_modes_and_lower_tiers_as_tolerance_bands.md`
- Main local result:
  - the exact `0.99` lane is a single-point precision mode at dwell `2`, with zero left slack, zero right slack, and zero retuning budget,
  - the exact `0.95` lane remains a true tolerance band on dwell `8`–`18` with anchor `13` and `5` dwell steps of slack on each side,
  - the exact `0.85` lane is the widest certified band on dwell `19`–`32` with anchor `25`, left slack `6`, and right slack `7`,
  - and the substantive warning is now explicit: tightening `0.95 -> 0.99` is also a tolerance collapse, shrinking certified dwell width from `11` to `1` and minimum anchor slack from `5` to `0`.

## 2026-03-08 — Research Pass LXXXVI (Compact Repeat-State Uncertainty Upgrade Tariff)

- Added one exact marginal-cost card so future inheritors can price moves between the certified uncertainty tiers instead of treating them as disconnected modes:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_upgrade_tariff_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_upgrade_tariff_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_upgrade_tariff.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_price_uncertainty_guarantee_upgrades_by_exact_operating_tariffs.md`
- Main local result:
  - the exact `0.95` lane is the current upgrade knee,
  - moving `0.85 -> 0.95` costs only `+2` hard-cap steps and `+3` net checkpoints while buying `+0.109999` worst-case gain share,
  - moving `0.95 -> 0.99` costs `+6` hard-cap steps and `+6` net checkpoints for only `+0.019341` more worst-case gain share,
  - and the full `0.85 -> 0.99` span remains one sparse budget envelope: `+8` hard-cap steps and `+9` net checkpoints, still coverable by the existing `17`-point master audit calendar.

## 2026-03-08 — Research Pass LXXXV (Compact Repeat-State Master Audit Calendar)

- Added one exact maintenance unification artifact so future inheritors can pre-register one sparse audit schedule instead of juggling separate checkpoint lists for uncertainty tiers, structural flips, and the rewrite-budgeted fallback:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_master_audit_calendar_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_master_audit_calendar_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_master_audit_calendar.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_pre_register_one_master_audit_calendar_for_compact_repeat_sidecars.md`
- Main local result:
  - the near-exact `0.99` checkpoint union already subsumes the full near-optimal `0.95` union,
  - covering the exact relaxed `0.85` tier requires only one extra transition checkpoint, `56`,
  - the only mandatory structural checkpoints outside the exact transition unions are `79` and `191`,
  - so the full current operational surface compresses to one `17`-point master audit calendar: `9, 15, 24, 31, 38, 47, 54, 56, 63, 79, 111, 143, 159, 191, 230, 239, 255`,
  - and that same sparse calendar also covers the trusted-repeat four-transition rewrite-budgeted fallback.

## 2026-03-08 — Research Pass LXXXIV (Compact Repeat-State Uncertainty-Checkpoint Staircase)

- Added one exact maintenance-surface synthesis on top of the existing uncertainty-cap ladder so future inheritors can budget checkpoint calendars as well as rewrite counts:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_checkpoint_staircase_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_checkpoint_staircase_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_checkpoint_staircase.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_compact_repeat_uncertainty_lanes_as_a_checkpoint_staircase.md`
- Main local result:
  - the exact `0.99`, `0.95`, and `0.85` uncertainty tiers form a checkpoint staircase with union checkpoint counts `14`, `8`, and `5` respectively,
  - near-exact `0.99` preservation adds checkpoints `9, 15, 31, 38, 54, 255` beyond the near-optimal `0.95` lane,
  - relaxing from `0.95` to `0.85` removes checkpoints `24, 63, 230, 239` and introduces only the relaxed-tier marker `56`,
  - and the archive can therefore reason about operational maintenance burden directly instead of inferring it from transition caps alone.

## 2026-03-08 — Research Pass LXXXIII (Compact Repeat-State Uncertainty-Cap Staircase Refresh)

- Added one exact staircase card that refreshes the compact repeat-sidecar uncertainty-cap story into a single inheritor-facing object instead of leaving the archive split between the older planning guardrail row and the newer exact lower-guarantee certification:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_staircase_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_staircase_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_cap_staircase.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_keep_compact_repeat_uncertainty_cap_tradeoffs_as_an_exact_staircase.md`
- Main local result:
  - the exact repeat-uncertainty cap ladder is now small enough to memorize directly: hard cap `11` buys the near-exact `0.99` lane at dwell `2`, hard cap `5` buys the checkpoint-neutral near-optimal `0.95` lane on dwell `8`–`18` with anchor `13`, and hard cap `3` buys the exact relaxed `0.85` lane on dwell `19`–`32` with anchor `25`,
  - the old lower-guarantee guardrail row (`4`, `planning_inference`) is now explicitly marked as stale historical context rather than live operating truth,
  - and the archive can therefore cite one coherent staircase instead of asking inheritors to manually merge multiple same-day reports.

## 2026-03-08 — Research Pass LXXXII (Compact Repeat-State Lower-Guarantee Three-Cap Certification)

- Closed the last open lower-guarantee uncertainty-cap point by promoting the dwell `19`–`32` lane from planning inference to an exact certified mode:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_lower_guarantee_three_cap_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_lower_guarantee_three_cap_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_lower_guarantee_three_cap.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_lower_guarantee_uncertainty_lanes_as_exact_three_cap_modes.md`
- Main local result:
  - once the archive relaxes the uncertainty-safe gain-share promise to `0.85`, dwell `19`–`32` becomes an exact hard-`3` lane across repeat budgets `0.15`, `0.18`, and `0.25`,
  - representative anchor dwell `25` preserves worst-case gain share `0.870482` with transition range `0`–`3`,
  - cap `2` is impossible on the current frontier because the focal `0.18` planner only reaches it after dropping to gain share `0.510201` at dwell `49`,
  - and cap `4` buys no extra dwell coverage beyond the exact cap-`3` lane.

## 2026-03-08 — Research Pass LXXXI (Compact Repeat-State Cap-Safe Anchor Fungibility)

- Added a compact cap-safe anchor fungibility synthesis so future inheritors preserve the real lane boundaries instead of overfitting to one dwell integer:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_cap_safe_anchor_fungibility_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_cap_safe_anchor_fungibility_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_cap_safe_anchor_fungibility.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_cap_safe_dwell_anchors_as_band_labels_not_magic_constants.md`
- Main local result:
  - the near-optimal cap-safe lane should be remembered as focal dwell band `8`–`18`, not as a brittle single point,
  - dwell `13` remains the representative label for that band,
  - the current uncertainty-default dwell `9` already lies inside the same focal five-transition plateau with checkpoints `24, 63, 111, 159, 239`,
  - and the real structural boundaries are dwell `7` and dwell `19`, where the schedule jumps onto different lanes.


## 2026-03-08 — Research Pass LXXX (Compact Repeat-State Cap-Safe Checkpoint Neutrality + Branch Rejoin)

- Rejoined the sibling rev0088 branch artifacts that had diverged from the latest uncertainty-cap archive tip, restoring the finite checkpoint schedule and precedence control card to the working line:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_checkpoint_schedule_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_checkpoint_schedule_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_checkpoints.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_schedule_compact_repeat_sidecar_rechecks_at_finite_checkpoint_sets.md`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_control_card_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_control_card_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_control_card.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_ship_compact_repeat_sidecar_control_cards.md`
- Added a cap-safe checkpoint-neutrality synthesis for the near-optimal uncertainty lane so future inheritors know that moving from dwell `9` to the five-transition-safe dwell `13` preset does not widen the finite checkpoint surface:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_cap_safe_checkpoint_schedule_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_cap_safe_checkpoint_schedule_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_cap_safe_checkpoints.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_cap_safe_uncertainty_lanes_as_checkpoint_neutral.md`
- Main local result:
  - the cap-safe near-optimal uncertainty anchor stays at dwell `13` with certified band-wide hard cap `5`,
  - its finite checkpoint union across repeat budgets `0.15`, `0.18`, and `0.25` is exactly `24, 47, 63, 111, 143, 159, 230, 239`,
  - that eight-point union exactly matches the current uncertainty-default dwell-`9` checkpoint union,
  - so the real tradeoff is guarantee compatibility versus transition count, not maintenance sprawl.

## 2026-03-08 — Research Pass LXXIX (Compact Repeat-State Uncertainty-Cap Guardrails)

- Added a compact guardrail synthesis for joint repeat-uncertainty and hard rewrite caps so future inheritors stop conflating the trusted-repeat four-transition lane with the uncertainty-robust dwell presets:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_guardrails_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_guardrails_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_cap_guardrails.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_respect_uncertainty_cap_guardrails_for_compact_repeat_sidecars.md`
- Main local result:
  - a hard cap of `4` is incompatible with the current `0.95` uncertainty-robust compact repeat-sidecar guarantee,
  - the certified near-optimal uncertainty-safe lane therefore needs `5` transitions and has a cap-safe dwell sub-band `8`–`18` with midpoint anchor `13`,
  - near-exact `0.99` robustness still needs `11` transitions even after cap minimization,
  - and the next conservative low-churn planning lane is dwell `19`–`32` with anchor `25`, though its exact minimum band-wide cap remains an open certification task.

## 2026-03-08 — Research Pass LXXVIII (Compact Repeat-State Operating Modes + Inheritor Ladder)

- Added an inheritor-facing operating-mode synthesis for compact repeat sidecars so future sessions can pick a deployment mode without reopening every underlying frontier report:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_operating_modes_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_operating_modes_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_operating_modes.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_ship_compact_repeat_sidecar_operating_modes.md`
- Main local result:
  - the default inheritor preset should move from the single-budget dwell anchor `13` to the repeat-uncertainty-safe dwell anchor `9`,
  - the practical rewrite-budget ceiling remains `4` transitions with preserved gain share `0.968419`,
  - fixed route blocks become the right freeze policy once rewrite cost clears `927.685921` bytes per transition or expected repeats reach `0.7`,
  - and the archive can therefore ship one small operating ladder instead of replaying every compact-sidecar frontier from scratch.

## 2026-03-07 — Compact Repeat-State Repeat-Uncertainty Dwell Overlap Pass

- Added a repeat-uncertainty dwell-anchor chooser for compact repeat sidecars so the archive can choose one safe minimum-dwell preset across a plausible repeat-budget band:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_repeat_uncertainty_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_repeat_uncertainty_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_min_dwell_repeat_uncertainty.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_min_dwell_anchors_from_repeat_uncertainty_overlaps.md`
- Main local result:
  - over repeat budgets `0.15`–`0.25`, the `0.99`-safe overlap shrinks to dwell `1`–`2`,
  - dwell `9` is the robust near-optimal anchor with worst-case preserved gain share `0.980481`,
  - dwell `16` is the broader simplicity-first anchor with the same worst-case preserved gain share `0.980481`,
  - and near-exact dwell tuning is therefore brittle under repeat-budget uncertainty while overlap anchors remain stable.

## 2026-03-07 — Compact Repeat-State Minimum-Dwell Anchor Presets Pass

- Added robust gain-share anchor presets for compact repeat sidecars so the archive can choose interior dwell settings from stable plateaus instead of living on fragile threshold edges:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_anchor_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_anchor_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_min_dwell_anchor.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_min_dwell_anchors_from_widest_gain_plateaus.md`
- Main local result:
  - to keep at least `0.99` of the full dynamic savings, the widest admissible dwell plateau is `2`–`6`, so the robust anchor is `4` with a ±`2`-append margin,
  - to keep at least `0.95`, the widest admissible plateau is `8`–`18`, so the near-optimal default anchor is `13` with a ±`5`-append margin and `5` transitions,
  - to keep at least `0.85`, the widest admissible plateau is `19`–`48`, so the simplicity anchor is `33` with a ±`14`-append margin and `3` transitions,
  - and if robustness matters more than savings, the widest plateau overall is fixed route blocks, `57`–`257`, whose midpoint anchor is `157` with a ±`100`-append margin.
- Implementor consequence:
  - do not anchor on the first dwell that barely meets a target,
  - choose the midpoint of the widest admissible gain plateau instead,
  - and keep a small preset table (`4`, `13`, `33`, `157`) rather than re-explaining the entire frontier.

## 2026-03-07 — Compact Repeat-State Minimum-Dwell Frontier Pass

- Added an exact minimum-dwell frontier for compact repeat sidecars so the archive can suppress short-lived cliff toggles with one simple online rule:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_min_dwell.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_enforce_minimum_dwell_lengths_for_compact_repeat_sidecars.md`
- Main local result:
  - at `0.18` expected repeats over the next `256` novel appends, the unconstrained dynamic optimum still uses `12` transitions,
  - a minimum dwell of `2` unique appends suppresses the one-step cliff fallback and drops the schedule to `11` transitions,
  - a minimum dwell of `8` collapses the schedule to `5` transitions while preserving `0.980481` of the full dynamic savings,
  - a minimum dwell of `19` collapses the schedule further to `3` transitions while preserving `0.870482`,
  - and once minimum dwell reaches `57`, fixed route blocks from the start become the best policy.
- Implementor consequence:
  - choose a minimum dwell length before replaying any exact compact-sidecar schedule,
  - use `8` novel appends as the current sweet-spot default when the goal is to suppress cliff chatter without giving up much value,
  - and raise the dwell floor only when operational simplicity matters more than the last slice of dynamic savings.

## 2026-03-07 — Compact Repeat-State Transition-Budget Frontier Pass

- Added an exact transition-budget frontier for compact repeat sidecars so the archive can choose the best schedule under an explicit cap on sidecar rewrites:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_transition_budget_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_transition_budget_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_transition_budget.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_budget_compact_repeat_sidecar_rewrites_by_transition_count.md`
- Main local result:
  - at `0.18` expected repeats over the next `256` novel appends, the unbounded dynamic optimum still uses `12` transitions,
  - but the first allowed rewrite already buys `5679.676082` bytes against fixed route blocks,
  - the first four allowed rewrites capture `0.968419` of the full dynamic savings,
  - the fifth rewrite buys only `134.276182` bytes,
  - and the sixth only `1.979428` bytes.
- Implementor consequence:
  - when rewrite count is the real bottleneck, budget transitions directly instead of inferring an abstract per-switch byte penalty,
  - spend the first few rewrites on the large structural bands first,
  - and treat four rewrites as the practical ceiling on the current frontier unless the archive truly cares about the last few hundred bytes.

## 2026-03-07 — Compact Repeat-State Switch-Penalty Frontier Pass

- Added an exact switch-penalty frontier for compact repeat sidecars so the archive can keep only the transitions whose byte savings still justify rewrite churn:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_switch_penalty_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_switch_penalty_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_switch_penalty.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_price_sidecar_churn_on_exact_switch_penalty_frontiers.md`
- Main local result:
  - at `0.18` expected repeats over the next `256` novel appends, the exact non-negative switch-cost frontier has `9` regimes,
  - the micro-churn oscillations all disappear once sidecar rewrite cost exceeds `45.40069` bytes per transition,
  - the earlier fixed-policy average break-even of `927.685921` bytes still leaves a `4`-transition exact planner that beats fixed route blocks by `7069.915895` bytes,
  - and the frontier only fully collapses to fixed route blocks once switch cost reaches `5679.676082` bytes per transition.
- Implementor consequence:
  - do not compress sidecar churn into one average regret threshold,
  - freeze the tiny downgrade/upgrade oscillations first while keeping the large front-loaded switches that still pay,
  - and only adopt a fully fixed sidecar once real rewrite cost crosses the exact fixed-policy frontier.

## 2026-03-07 — Compact Repeat-State Fixed-Policy Regret Pass

- Added a horizon-level fixed-policy regret view for compact repeat sidecars so the archive can compare exact staging churn against the best single sidecar over the next novel-append band:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_fixed_policy_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_fixed_policy_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_fixed_policy.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_compare_sidecar_churn_against_fixed_policy_regret.md`
- Main local result:
  - over the next `256` novel appends at a marginal budget of `0.18` expected repeats, the fully dynamic planner changes sidecar regimes `12` times,
  - the best fixed policy is still `paged_catalog_with_route_blocks`,
  - its cumulative regret versus the fully dynamic schedule is only `11132.231038` bytes (`0.2305%` of the dynamic cumulative objective),
  - and the dynamic schedule therefore buys only `927.68592` bytes per transition on average before a fixed policy becomes cheaper overall.
- Implementor consequence:
  - when sidecar transitions have non-trivial rewrite, coordination, or churn cost, compare that per-switch cost against the fixed-policy regret threshold before replaying every staging interval,
  - prefer the best fixed sidecar once per-switch cost clears the measured break-even line,
  - and note that by `0.7` expected repeats, always-on route blocks already match the dynamic schedule exactly across the whole measured horizon.

## 2026-03-07 — Compact Repeat-State Staging Pass

- Added an exact marginal-budget staging planner for compact repeat sidecars so the archive can allow upgrades **and** downgrades across novel-append growth instead of assuming sidecars only accumulate:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_staging_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_staging_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_staging.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_allow_compact_repeat_sidecar_downgrades_at_bitmap_cliffs.md`
- Main local result:
  - at a marginal budget of `0.18` expected repeats, the best compact state is not monotone in append count,
  - the live frontier cycles through bare pages, filters, and route blocks in exact bands,
  - route blocks dominate from appends `63`–`110`,
  - the first bitmap cliff at append `111` makes bare pages optimal again for one exact step,
  - filters retake the lead for `112`–`158`,
  - and route blocks regain the lead for `159`–`238` before filters return at append `239`.
- Implementor consequence:
  - compact repeat sidecars should be staged with both upgrades and downgrades,
  - “once route blocks pay off, keep them forever” is wrong near the size frontier,
  - and the archive should treat bitmap cliffs as legitimate moments to prune sidecar state until the next repeat-heavy band arrives.

## 2026-03-07 — Compact Repeat-State Growth-Cliff Pass

- Added an exact growth-cliff view for compact repeat sidecars so the archive can combine repeat-budget decisions with novel-append horizons instead of assuming sidecar state grows smoothly:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_growth_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_growth_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_growth.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_plan_compact_repeat_sidecars_against_growth_cliffs.md`
- Main local result:
  - the current deterministic `274`-fingerprint frontier starts at `18` live `16`-entry pages with a tail count of `2`,
  - filters start `238` bytes lighter than route blocks,
  - each new digest page adds `49` filter-sidecar bytes while route-block sidecar bytes stay flat inside the current bitmap band,
  - route blocks become state-cheaper than filters after `79` novel appends and stay ahead through `110`,
  - then the `25`-page bitmap cliff at append `111` adds `336` route-block sidecar bytes and puts filters back ahead by `231` bytes,
  - with the same sawtooth repeating again at appends `191` and `239`.
- Implementor consequence:
  - expected repeats alone are not enough to choose the live compact repeat sidecar,
  - once a sidecar is justified at all, the archive should also track the next page birth and the next route-block bitmap cliff,
  - and it should treat route blocks as temporarily state-dominant whenever the projected page band makes them cheaper than filters before the next cliff.

## 2026-03-07 — Research Pass LXXVI (Compact Repeat-State Budgets + Sidecar Thresholds)

- Added measured compact repeat-state budgeting for paged digest catalogs so the archive can choose between bare pages, aligned page filters, and route blocks by expected repeat workload instead of inheriting the strongest sidecar unconditionally:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
- Added a derived snapshot measuring compact-state bytes, average repeat-lookup bytes, break-even repeat counts, and budgeted winners across the current deterministic frontier:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_budget_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_budget_snapshot_20260307.{md,json}`
- Added a validator for compact repeat-state metrics, break-even thresholds, and budgeted sidecar recommendations:
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_budgets.py`
- Added an inheritor-facing note on choosing compact repeat sidecars by expected repeat budget:
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_compact_repeat_sidecars_by_expected_repeat_budget.md`
- Tightened planning guidance:
  - keep only bare paged raw-digest catalogs for very cold archives,
  - add aligned page filters once the current catalog expects more than `0.185996` repeats,
  - add route blocks once the filtered state expects more than `0.650001` repeats,
  - and re-measure those thresholds whenever page size, catalog population, or repeat/write mix changes materially.
- Main local result:
  - on the current deterministic `274`-packet frontier with live `16`-entry pages, bare pages cost `11770` compact-state bytes and `6214.708029` average repeat-lookup bytes,
  - filters cost `12653` bytes and `1467.306569` lookup bytes,
  - route blocks cost `12891` bytes and `1101.153285` lookup bytes,
  - so filters break even after `0.185996` expected repeats and route blocks break even after `0.650001` repeats beyond the filtered state.

## 2026-03-07 — Research Pass LXXV (Digest-Byte Route Blocks + Direct Candidate-Page Jumps)

- Added digest-byte route blocks beside append-only paged raw-digest catalogs so repeat planning can jump straight to candidate compact pages instead of linearly scanning page-filter artifacts:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
- Added a measured snapshot comparing route-block repeat lookup against the existing page-filter path:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_catalog_route_block_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_catalog_route_block_snapshot_20260307.{md,json}`
- Added a validator for route-block reconstruction, append-locality parity, and repeat-plan equivalence versus the page-filter planner:
  - `scripts/test/check_rematch_delta_decision_packet_catalog_route_blocks.py`
- Added an inheritor-facing note on keeping digest-byte route blocks beside paged catalogs:
  - `docs/LIBRARY/topics/rematch_worlds_should_store_digest_byte_route_blocks_beside_paged_catalogs.md`
- Tightened planning guidance:
  - when the archive already keeps compact paged catalogs plus the current 16-entry page layout, prefer digest-byte route blocks over linear page-filter scans for repeat planning,
  - keep them archive-local as a compact-state acceleration sidecar rather than an export format,
  - and preserve append-local updates by only mutating the relevant high-nibble block until the page-count bitmap width changes.


## 2026-03-07 — Research Pass LXXIV (Filtered Page-Size Frontier + Smaller Default Catalog Pages)

- Measured the filtered compact-catalog page-size frontier and changed the live filtered-page default from `64` entries to `16` entries:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
- Added a derived snapshot comparing the clean power-of-two filtered page-size candidates on compact-state bytes versus average repeat-lookup cost:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_catalog_page_size_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_catalog_page_size_snapshot_20260307.{md,json}`
- Added a validator for page-size-frontier reconstruction and default-choice parity:
  - `scripts/test/check_rematch_delta_decision_packet_catalog_page_sizes.py`
- Added an inheritor-facing note on choosing smaller filtered catalog pages by measured lookup/state tradeoff:
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_small_filtered_catalog_pages_by_measured_lookup_state_tradeoff.md`
- Refreshed the page-based catalog snapshots and validators so the archive’s compact read/write path now reflects the new default page size:
  - `artifacts/reports/rematch_proxy_delta_decision_packet_catalog_page_snapshot_20260307.{md,json}`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_catalog_page_resolution_snapshot_20260307.{md,json}`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_catalog_page_write_snapshot_20260307.{md,json}`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_catalog_page_filter_snapshot_20260307.{md,json}`
- Tightened planning guidance:
  - when the archive keeps filtered paged raw-digest catalogs, treat page size as a measured storage frontier rather than inherited folklore,
  - default to `16` entries per page for the current family10 filtered compact-catalog state,
  - and only reopen that frontier if the archive’s fingerprint population or lookup/write mix changes materially.

## 2026-03-07 — Research Pass LXXIII (Digest-Byte Page Filters + Pruned Compact-State Repeat Lookups)

- Added tiny digest-byte page filters beside append-only raw-digest fingerprint pages so repeat lookups can skip impossible pages before scanning raw digests:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
- Added a derived snapshot measuring filter overhead, filtered repeat-scan savings, false-positive rates, and append-local filter maintenance against the deterministic frontier catalog:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_catalog_page_filter_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_catalog_page_filter_snapshot_20260307.{md,json}`
- Added a validator for page-filter encoding, filtered slot lookup, filtered yocto-plan parity, and append-local filter updates:
  - `scripts/test/check_rematch_delta_decision_packet_catalog_page_filters.py`
- Added an inheritor-facing note on storing digest-byte page filters beside paged raw-digest catalogs:
  - `docs/LIBRARY/topics/rematch_worlds_should_store_digest_byte_page_filters_beside_paged_catalogs.md`
- Tightened planning guidance:
  - if the archive already preserves append-only raw-digest fingerprint pages, keep one aligned digest-byte filter beside each page,
  - use those filters to prune repeat lookups before scanning raw digests,
  - update only the tail filter on ordinary appends,
  - and still fall back to the existing first-write chooser when the filtered lookup finds no repeat.


## 2026-03-07 — Research Pass LXIX (Paged Raw-Digest Catalogs + Append Locality)

- Added a paged raw-digest codec for append-only semantic-fingerprint catalogs so catalog-slot repeats do not depend on a bulky JSON string catalog:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
- Added a derived snapshot measuring dense catalog savings and tail-page append locality against the deterministic frontier string catalog:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_catalog_page_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_catalog_page_snapshot_20260307.{md,json}`
- Added a validator for catalog-page round-tripping, slot lookups, partial-tail appends, and full-tail overflow behavior:
  - `scripts/test/check_rematch_delta_decision_packet_catalog_pages.py`
- Added an inheritor-facing note on storing append-only fingerprint catalogs as paged raw-digest blocks:
  - `docs/LIBRARY/topics/rematch_worlds_should_store_append_only_fingerprint_catalogs_as_paged_raw_digest_blocks.md`
- Tightened planning guidance:
  - if the archive relies on catalog-slot repeats, keep the ordered fingerprint catalog in paged raw-digest blocks,
  - append to the tail page until full,
  - and rehydrate full `sha256:` strings only for export, debugging, or other human-facing interchange.


## 2026-03-07 — Research Pass LXVIII (Catalog Slot References + Append-Only Ordinals)

- Added an append-only catalog-slot repeat codec for family10 rematch decision packets so archives that preserve a stable semantic-fingerprint catalog can stop storing hash-prefix material on every repeat:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
- Added a derived snapshot measuring catalog-slot repeat savings against prefix-based byteframe repeats on the deterministic frontier catalog:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_catalog_reference_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_catalog_reference_snapshot_20260307.{md,json}`
- Added a validator for catalog-slot reference encoding, resolution, yocto-planner selection, and unordered-set fallback behavior:
  - `scripts/test/check_rematch_delta_decision_packet_catalog_references.py`
- Added an inheritor-facing note on preserving append-only fingerprint ordinals inside the archive:
  - `docs/LIBRARY/topics/rematch_worlds_should_store_append_only_catalog_slot_references_inside_archive.md`
- Tightened planning guidance:
  - if the archive preserves an append-only ordered semantic-fingerprint catalog, repeat writes should now go straight to `catalog_reference`,
  - if only an unordered fingerprint set is available, fall back to `byte_reference`,
  - and exported references should still keep the portable full-fingerprint path.


## 2026-03-07 — Research Pass LXVII (Analytic Weight Frontiers + No-Live Comparison)

- Added exact payload-byte sizing for `oracle_weights` first writes so the live writer can choose between `packed_seed` and `byte_seed` without materializing both candidate bodies:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
- Added a derived snapshot showing exact agreement between the analytic byte formulas and actual serialized candidate sizes across the deterministic frontier and randomized weight stress cases:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_weight_formula_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_weight_formula_snapshot_20260307.{md,json}`
- Added a validator for weight-formula exactness and write-plan parity:
  - `scripts/test/check_rematch_delta_decision_packet_weight_formulas.py`
- Added an inheritor-facing note on choosing weight first-write bodies by exact payload bytes:
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_oracle_weight_seed_forms_by_exact_payload_bytes.md`
- Tightened planning guidance:
  - repeats should still go straight to `byte_reference`,
  - non-weight first writes should still go straight to `byte_seed`,
  - and `oracle_weights` first writes should now compute exact packed-vs-byte seed lengths from the packed payload and emit only the winner.


## 2026-03-07 — Research Pass LXVI (Compiled Frontiers + Exact Shortlists)

- Added an exact compiled frontier for zepto in-archive decision-packet writes so the live writer no longer has to re-evaluate codecs that never win on the measured frontier:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
- Added a derived snapshot showing that the compiled shortlist reproduces the measured frontier exactly while cutting most candidate-size evaluations:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compiled_frontier_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compiled_frontier_snapshot_20260307.{md,json}`
- Added a validator for compiled-frontier exactness on the deterministic packet set and randomized weight stress cases:
  - `scripts/test/check_rematch_delta_decision_packet_compiled_frontiers.py`
- Added an inheritor-facing note on turning measured frontiers into live write rules:
  - `docs/LIBRARY/topics/rematch_worlds_should_compile_measured_decision_packet_frontiers_into_exact_shortlists.md`
- Tightened planning guidance:
  - repeat writes should now go straight to `byte_reference`,
  - non-weight first writes should now go straight to `byte_seed`,
  - and only `oracle_weights` first writes still need a local comparison, narrowed to `{packed_seed, byte_seed}`.


## 2026-03-07 — Research Pass LIX (Mode-Coded References + Smallest Repeat Writes)

- Added archive-local mode-coded repeat references for family10 rematch decision packets so duplicate writes can compress below prefix-resolved references whenever the local reference codebook is preserved:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
- Added a derived snapshot measuring repeat-write savings from mode-coded references versus archive-local prefix references and portable full-fingerprint references:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_coded_reference_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_coded_reference_snapshot_20260307.{md,json}`
- Added a validator for coded-reference expansion, resolution, and byte-savings claims:
  - `scripts/test/check_rematch_delta_decision_packet_coded_references.py`
- Added an inheritor-facing note on the repeat-storage ladder:
  - `docs/LIBRARY/topics/rematch_worlds_should_store_mode_coded_repeat_references_inside_archive.md`
- Tightened planning guidance:
  - first writes should still keep one mode-coded seed per new semantic fingerprint,
  - repeat writes should use a mode-coded repeat reference when the local reference codebook is part of the durable archive environment,
  - archive-local prefix references should remain the clearer fallback tier,
  - and full fingerprint references should remain export artifacts rather than the default in-archive repeat object.

## 2026-03-07 — Research Pass LVII (Prefix-Resolved References + Smaller Repeat Writes)

- Added an archive-local prefix-reference layer for family10 rematch decision packets so duplicate writes inside the archive no longer have to restate a full exported fingerprint:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
- Added a derived snapshot measuring repeat-write savings from shortest-unique local prefixes versus portable full-fingerprint references:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_prefix_reference_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_prefix_reference_snapshot_20260307.{md,json}`
- Added a validator for prefix-reference resolution and byte-savings claims:
  - `scripts/test/check_rematch_delta_decision_packet_prefix_references.py`
- Added an inheritor-facing note on when to use local prefixes instead of full hashes:
  - `docs/LIBRARY/topics/rematch_worlds_should_store_prefix_resolved_references_inside_archive.md`
- Tightened planning guidance:
  - first writes should still store one semantic core per new semantic fingerprint,
  - later in-archive repeats should use the shortest unique local fingerprint prefix rather than a full portable hash string,
  - and full-fingerprint references should be reserved for export across the archive boundary.

## 2026-03-07 — Research Pass LIII (Decision Packets + Minimal Archive Storage)

- Added an executable compact-packet surface for family10 rematch-delta decisions:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
- Added a derived snapshot showing which packet mode is minimal for each interface/question pair and how representative packets compare when minified:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_snapshot_20260307.{md,json}`
- Added a validator for the packet-routing and sample-packet contract:
  - `scripts/test/check_rematch_delta_decision_packets.py`
- Added an inheritor-facing note on archive-size consequences:
  - `docs/LIBRARY/topics/rematch_worlds_should_store_minimal_decision_packets.md`
- Tightened planning guidance:
  - when declared weights or direct `(B,H)` coordinates already exist, store one direct oracle packet instead of duplicating heavier probe traces,
  - use robustness-only, open-strict, and exact-path packet modes as distinct archive contracts rather than defaulting to the largest three-cap record,
  - and treat exact tie-cap identification as the real escalation trigger for the fixed `[10,20,10000]` packet.

## 2026-03-06 — Research Pass XLV (Minimal Cap-Probe Sets + Two-Probe Impossibility)

- Added a derived rematch delta minimal cap-probe snapshot that compresses the normalized cap-trajectory contract into a finite witness set:
  - `scripts/report/build_rematch_proxy_delta_minimal_cap_probe_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_minimal_cap_probe_snapshot_20260306.{md,json}`
- Added a validator for the minimal three-probe classification rule:
  - `scripts/test/check_rematch_delta_minimal_cap_probes.py`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_minimal_cap_probe_sets.md`
- Tightened planning guidance:
  - once the final choice has been reduced to a scalar threshold path with only four strict classes, publish a minimal finite probe set instead of asking inheritors to rescan the whole cap range,
  - in the current proxy any two cap probes are structurally insufficient because ordered two-probe thresholds can realize at most three strict winner signatures,
  - and the caps `10`, `20`, and `10000` already form a minimal sufficient witness set with strict signatures `MMM`, `SMM`, `SMS`, and `SSS`.

## 2026-03-06 — Research Pass XLIV (Cap-Robust Preference Certificates + Full-Range Ambiguity Strip)

- Added a derived rematch delta cap-robust preference snapshot that checks the full additional-budget-cap range inside the certified family10 policy box:
  - `scripts/report/build_rematch_proxy_delta_cap_robust_preference_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_cap_robust_preference_snapshot_20260306.{md,json}`
- Added a validator for the true all-caps preference-robustness strip:
  - `scripts/test/check_rematch_delta_cap_robust_preference.py`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_cap_robust_preference_certificates.md`
- Tightened planning guidance:
  - once the live choice has collapsed to two anchors, do not certify preference robustness from only a low-cap sample and a tail sample,
  - instead identify the global best and worst hazard coefficients over the full published cap range and derive the exact all-caps ambiguity strip,
  - and in the current proxy the true strip is `0.000777 * w_hazard`, with the most material-favoring coefficient at cap `20` rather than at the asymptotic tail, so endpoint-only checking understated cap sensitivity by `0.000280 * w_hazard` (`56.34%`).

# Changelog

## Unreleased

- add a generated Rust external-test patchset (`docs/RUST_EXTERNAL_TEST_PATCHSET.md`, `artifacts/patches/rust_external_test_patchset.patch`) so blocked sessions can hand off one replayable patch instead of only queue/bundle reports
- prefer directly loadable `examples/probes/*.json` fixtures over holdout/registry placeholders when choosing weak-scenario lift seeds, so `observation_flip` now prefers a self-contained probe instead of a template with `strategy_a: null`
- add `docs/RUST_SEED_LOADER_READINESS.md` and `artifacts/reports/rust_seed_loader_readiness.json` as a compact audit proving whether the preferred external-test queue seeds are directly loadable `ProbeSpec` fixtures
- wire `make update-rust-seed-loader-readiness`, `make test-rust-seed-loader-readiness`, and the canonical `cloudtainer-shadow-pass` to keep the seed-loader audit reproducible in blocked-Rust sessions

- certify: add top-level `transition_graph_diagnostics` (communicating classes, closed classes, absorbing states, initial-support reachability) so reducibility / basin structure is explicit in retained results; bump `certify_memory_one_result` to schema_version `14`.

- Scientific repo transformation: deterministic governance, tranche execution model, terminology migration (`candidate`/`adversary`), and expanded reproducibility/release tooling.
- Golden-Rule research pass: citation-first archive compaction, inheritor brief, anti-vampire metric notes, and source expansion for longer memory / partner choice / universalisation.
- Rematch-world refinement: added delay-pressure report, rematch delay guidance, and explicit role-assignment / role-swap planning notes for future endogenous rematch worlds.
- Matching-friction diagnostic: added a monotonic delay-tax snapshot and a source-backed warning not to conflate exogenous-pool delay sweeps with full matching-market efficiency.
- Occupancy-accounting diagnostic: added an exact matched-vs-dead-time decomposition for the current rematch proxy and a reporting contract for future rematch worlds.
- Turnover-tempo diagnostic: added a near-exact tempo law for the current rematch proxy showing fixed rematch delay scales with partnership churn, not just with the nominal delay knob.
- Occupancy-normalized leaderboard diagnostic: added a rank-decomposition report showing where raw delay-induced leaderboard flips are occupancy artifacts rather than within-match quality changes.
- Delay-robustness diagnostic: added a crossover-threshold report showing when single-delay rematch winners are fragile to the exact rematch-friction point chosen for the benchmark.
- Live-contender diagnostic: added a frontier-pruning report separating dead contenders, tested-band leader flips, and winner margins from bulk pairwise crossover noise.
- Winner-certification diagnostic: added a paired-seed uncertainty report distinguishing certified rematch leaders from tiny point-estimate flips that remain statistically unresolved.
- Budget-aware winner-triage diagnostic: added a certification-budget snapshot showing when unresolved rematch flips are so expensive to certify that they should stay compact near-tie artifacts by default.
- Delta-hazard diagnostic: added a knife-edge SESOI snapshot showing that closure cost spikes are concentrated in tiny neighborhoods around observed rematch top-gap means, so coarse delta grids alone are not a safe planning artifact.
- Delta-anchor contract: added a machine-checkable topology-preserving anchor snapshot showing inherited parent anchors are boundary-biased and should be normalized to interior topology-stable anchors before publication.

## 2026-03-06 — rev0030: Added eighth parable (Moses and the Shepherd's Prayer)

Added "Moses and the Shepherd's Prayer" to `PARABLES.md` as parable VIII,
renumbering "The Hole Beneath the Seat" to VIII accordingly.

Rationale: the seven original parables address future operators. This parable
addresses specifically the researchers and experts making formal claims — the ones
who know the most about the form of what is being studied and are therefore most
at risk of silencing what they cannot formally measure. The Leaking Basket speaks
to judges. The Shepherd parable speaks to experts. Both wounds are needed in this
archive.

The final line: "knowing more about the form of a thing does not always mean
knowing more about its life" — is the standing warning to everyone who works here,
including me.

## 2026-03-06 — rev0029: Noisy Ecology Test + ZD Extraction Finding + Scorecard Field 5

### Experimental finding (new)

Ran a Python simulation mirroring `gr_engine/src/sim.rs` semantics
(`scripts/analysis/ipd_sim.py`, `scripts/analysis/universalization_frontier.py`)
to investigate whether pairwise zero-noise anti-vampire criteria can distinguish
Extortion/ZD strategies from genuinely cooperative strategies.

**Finding**: they cannot. Under zero-noise pairwise evaluation, Extortion3 (chi=3
ZD strategy) scores `payoff_gap = 0` against every cooperative pool member because
ZD strategies never trigger their extraction parameters when opponents never
defect first. All named cooperative strategies (TFT, WSLS, GRIM, GenTFT-0.9) and
Extortion3 pass the three-criteria test identically in zero noise.

Under 2% implementation noise against a cooperative pool, the distinction becomes
clear: Extortion3 extracts an average payoff gap of **+0.348** from the pool;
GenTFT-0.9 achieves **-0.037** (approximately fair) with the highest average own
payoff (2.355) of any genuinely reciprocal strategy. WSLS is Extortion3's worst
victim under noise (gap=+1.058) due to WSLS's oscillation dynamics.

### Artifacts (new)

- `scripts/analysis/ipd_sim.py`: pure-Python IPD simulation (gr_engine mirror)
- `scripts/analysis/universalization_frontier.py`: three/four/five-criteria
  frontier analysis
- `artifacts/reports/noisy_ecology_snapshot_20260306.json`: experiment results
- `artifacts/reports/universalization_frontier_snapshot.json`: 8000-strategy
  random sample results (0 passers of all 3 criteria — confirms prior tradeoff)

### Research library (new)

- `docs/LIBRARY/topics/noisy_ecology_test_reveals_zd_extraction.md`: full write-up
  including tables, failure mode analysis, and implications

### Scorecard updated

Anti-vampire scorecard spec gains **field 5: `ecology_gap_noisy`** — average
payoff gap in noisy pool evaluation. Required to distinguish ZD extraction from
genuine cooperation. Threshold: `<= 0.1`. Without this field, Extortion3 and
GenTFT-0.9 are indistinguishable by the scorecard.

### Search objective correction

**Critical**: do not optimize search in zero-noise pairwise evaluation. ZD
strategies will pass all pairwise tests. Correct objective: maximize `own_payoff`
subject to `ecology_gap_noisy <= 0.1` in a noisy pool evaluation.

### Updated docs

- `docs/BUCKET.md`: scorecard promoted to [SPEC READY — UPDATED] with 5 fields;
  critical warning on search evaluation mode
- `docs/LIBRARY/README.md`: new topic added to index

## 2026-03-06 — rev0028: Covenant, Parables, Vocabulary Protection, Anti-Vampire Scorecard Spec

### Qualitative pillar (new)

- Added `COVENANT.md` to archive root: names what the project is actually for,
  upstream of the methodology. Establishes the normative ground from which the
  formal work draws its purpose. Read before the specs.
- Added `PARABLES.md` to archive root: seven parables selected for universality,
  each carrying what the formal language cannot compress. Standing witnesses for
  future operators.
- Both documents are protected in `AGENTS.md` — do not modify without explicit
  human review.

### Vocabulary protection (new)

- Added `Vocabulary Protection` and `Qualitative Pillar` sections to `AGENTS.md`.
- Defines `vampire`, `virtuous agent`, and `Golden Rule` as load-bearing terms
  that must not be silently neutralized. Replacements require explicit CHANGELOG
  rationale.
- Rationale: these terms track distinctions that are central to what the project
  is studying. Flattening them to neutral alternatives loses the research question.
  See `docs/LIBRARY/topics/virtue_vs_strategy.md` for the philosophical grounding.

### Research library additions

- `docs/LIBRARY/topics/virtue_vs_strategy.md`: philosophical grounding for why
  the vocabulary distinction is analytically necessary, not merely expressive.
  Explains how virtuous agents and strategically cooperative agents diverge at
  boundary conditions, and why the anti-vampire scorecard must track this.
- `docs/LIBRARY/topics/anti_vampire_scorecard_spec.md`: full artifact spec for
  the four-field scorecard called for in the inheritor brief and RESEARCH_OPINIONS.
  Fields: `own_payoff`, `payoff_gap`, `recovery_rounds`, `repair_abuse_rate`.
  Includes proposed schema, pass/fail threshold logic, build-order dependencies,
  and claim policy implication (forbid payoff-only claims in extortion settings).

### Updated docs

- `README.md`: added COVENANT.md and PARABLES.md to Operating Contract section.
- `docs/BUCKET.md`: promoted anti-vampire scorecard to [SPEC READY] status with
  pointer to full spec.
- `docs/LIBRARY/README.md`: added new library topics to index.

## 2026-03-06 — Research Pass XXII (Occupancy-Normalized Rematch Rankings)

- Added a derived rematch rank-decomposition snapshot for the current leave/rematch proxy:
  - `scripts/report/build_rematch_proxy_rank_decomposition_snapshot.py`
  - `artifacts/reports/rematch_proxy_rank_decomposition_snapshot_20260306.{md,json}`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_occupancy_normalized_rankings.md`
- Tightened planning guidance:
  - future rematch worlds should publish paired raw and occupancy-normalized leaderboards,
  - raw-only leaderboard flips should be treated as provisional until in-match rankings are checked too,
  - the current proxy already shows that delay can change aggregate ranks without changing within-match rank order.

## 2026-03-06 — Research Pass XXIII (Delay Robustness + Crossover Thresholds)

- Added a derived rematch crossover snapshot for the current leave/rematch proxy:
  - `scripts/report/build_rematch_proxy_delay_crossover_snapshot.py`
  - `artifacts/reports/rematch_proxy_delay_crossover_snapshot_20260306.{md,json}`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_delay_robustness_reports.md`
- Tightened planning guidance:
  - do not ship a single-delay rematch winner as if it were a universal ranking,
  - publish either a delay sweep, explicit crossover thresholds, or a robustness interval over the deployed rematch-friction range,
  - the current proxy already shows that pairwise raw orderings can be predicted from delay-0 in-match quality plus partnership tempo, so single-point rankings are often institution-sensitive rather than absolute.

## 2026-03-06 — Research Pass XXIV (Live Contenders + Leader Margins)

- Added a derived live-contender snapshot for the current leave/rematch proxy:
  - `scripts/report/build_rematch_proxy_live_contenders_snapshot.py`
  - `artifacts/reports/rematch_proxy_live_contenders_snapshot_20260306.{md,json}`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_live_contender_reports.md`
- Tightened planning guidance:
  - prune strictly dominated rematch policies before wide delay sweeps,
  - publish the tested-band leader set and winner margins, not only full pairwise crossover matrices,
  - in the current proxy there are several below-top rank flips but only one tested leader flip, and that leader flip is a near tie.

## 2026-03-06 — Research Pass XXV (Winner Certification + Paired-Seed Uncertainty)

- Added a derived winner-certification snapshot for the current leave/rematch proxy:
  - `scripts/report/build_rematch_proxy_winner_certification_snapshot.py`
  - `artifacts/reports/rematch_proxy_winner_certification_snapshot_20260306.{md,json}`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_winner_certification.md`
- Tightened planning guidance:
  - publish paired-seed uncertainty or an equivalent certification flag for the top-vs-runner-up gap,
  - treat raw leader flips that fail the gate as provisional frontier uncertainty rather than stable ranking reversals,
  - in the current proxy, the only tested leader flip is also the only uncertified panel.

## 2026-03-06 — Research Pass XXVI (Budget-Aware Winner Triage)

- Added a derived certification-budget snapshot for the current leave/rematch proxy:
  - `scripts/report/build_rematch_proxy_certification_budget_snapshot.py`
  - `artifacts/reports/rematch_proxy_certification_budget_snapshot_20260306.{md,json}`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_budget_aware_winner_triage.md`
- Tightened planning guidance:
  - unresolved rematch winner panels should publish an approximate additional-budget-to-certify field,
  - if certifying a frontier flip would require orders of magnitude more paired seeds than the baseline budget, keep it as a compact near-tie / indifference artifact by default,
  - in the current proxy the only uncertified panel would require about `70.8x` the present paired-seed budget to certify its current point-estimate winner.

## 2026-03-06 — Research Pass XXVII (Materiality Gates + Practical Equivalence)

- Added a derived materiality-gate snapshot for the current leave/rematch proxy:
  - `scripts/report/build_rematch_proxy_materiality_gate_snapshot.py`
  - `artifacts/reports/rematch_proxy_materiality_gate_snapshot_20260306.{md,json}`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_materiality_gates.md`
- Tightened planning guidance:
  - declare a smallest effect of interest (`delta`) for rematch top gaps and publish practical-equivalence status alongside winner certification,
  - use the resulting three-way decision rule (`material leader`, `practical tie`, `undecided`) before spending more simulation budget,
  - in the current proxy, three certified winners are already practical ties at `delta=0.005`, and the only uncertified leader flip is already a practical tie at `delta=0.01`.

## 2026-03-06 — Research Pass XXVIII (Delta Frontiers + Threshold Sensitivity)

- Added a derived delta-frontier snapshot for the current leave/rematch proxy:
  - `scripts/report/build_rematch_proxy_delta_frontier_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_frontier_snapshot_20260306.{md,json}`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_delta_frontier_reports.md`
- Tightened planning guidance:
  - publish per-panel delta frontiers rather than only a few ad hoc materiality labels at hand-picked thresholds,
  - let downstream consumers recover `material leader` / `practical tie` / `undecided` status for any declared `delta` from the compact frontier artifact,
  - in the current proxy all nine tested panels collapse to two delta cutoffs each, so threshold sensitivity can be surfaced without widening the archive.

## 2026-03-06 — Research Pass XXIX (Delta-Budget Frontiers + Closure Cost)

- Added a derived delta-budget frontier snapshot for the current leave/rematch proxy:
  - `scripts/report/build_rematch_proxy_delta_budget_frontier_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_budget_frontier_snapshot_20260306.{md,json}`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_delta_budget_frontiers.md`
- Tightened planning guidance:
  - publish a compact delta-budget frontier over the plausible SESOI band rather than only one budget number at one arbitrary delta,
  - surface how many panels remain unresolved and what extra paired-seed budget would close them at each delta,
  - in the current proxy the total closure cost is locally non-monotone in `delta`, so hidden budget pressure can distort threshold choices if the frontier is not published.

## 2026-03-06 — Research Pass XXX (Delta Hazard Bands + Knife-Edge SESOI)

- Added a derived rematch delta-hazard snapshot for the current leave/rematch proxy:
  - `scripts/report/build_rematch_proxy_delta_hazard_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_hazard_snapshot_20260306.{md,json}`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_delta_hazard_bands.md`
- Tightened planning guidance:
  - publish leader-gap hazard bands or an equivalent no-knife-edge buffer instead of relying on a coarse delta grid,
  - treat observed top-gap means as exact threshold hazards for the fixed-precision closure proxy,
  - keep SESOI selection explicit and stable rather than letting knife-edge budget spikes drive post hoc threshold choice.


## 2026-03-06 — Research Pass XXXI (Delta Admissibility Bands + Budget-Stable SESOI)

- Added a derived rematch delta-admissibility snapshot for the current leave/rematch proxy:
  - `scripts/report/build_rematch_proxy_delta_admissibility_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_admissibility_snapshot_20260306.{md,json}`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_budget_admissible_delta_bands.md`
- Tightened planning guidance:
  - publish budget-admissible SESOI bands plus one anchor per band for declared extra-budget caps,
  - treat nearly identical deltas with radically different closure costs as an interval-choice problem rather than as a post hoc threshold-shopping opportunity,
  - in the current proxy, a `+10` paired-seed cap leaves only two admissible bands over `[0, 0.02]`, and only one lies below `0.01`.

## 2026-03-06 — Research Pass XXXII (Delta Topology + Stability-First Anchors)

- Added a derived rematch delta-topology snapshot for the current leave/rematch proxy:
  - `scripts/report/build_rematch_proxy_delta_topology_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_topology_snapshot_20260306.{md,json}`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_topology_stable_delta_anchors.md`
- Tightened planning guidance:
  - publish topology-stable delta subbands or a stability-first anchor inside each admissible parent band,
  - do not treat one min-cost anchor as sufficient when the same admissible band contains multiple distinct panel-label topologies,
  - in the current proxy the cap-10 low-delta admissible band fragments into four topologies, and the inherited anchor sits only one grid-step from a topology boundary.

## 2026-03-06 — Research Pass XXXIII (Delta Persistence + Budget-Family Cores)

- Added a derived rematch delta-persistence snapshot for the current leave/rematch proxy:
  - `scripts/report/build_rematch_proxy_delta_persistence_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_persistence_snapshot_20260306.{md,json}`
- Added a validator for the cross-cap shared-core contract:
  - `scripts/test/check_rematch_delta_persistence.py`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_budget_family_delta_cores.md`
- Tightened planning guidance:
  - choose rematch delta anchors from a declared **budget family**, not one isolated extra-budget cap,
  - require a **minimum shared-core width** in addition to cross-cap persistence,
  - and use an exact **discrete-center anchor** on the delta grid rather than a rounded arithmetic midpoint when the persistent core has an even number of grid points.

## 2026-03-06 — Research Pass XXXIV (Delta Publishability + Guardrail Shortlists)

- Added a derived rematch delta-publishability snapshot for the current leave/rematch proxy:
  - `scripts/report/build_rematch_proxy_delta_publishability_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_publishability_snapshot_20260306.{md,json}`
- Added a validator for the guardrail-filtered shortlist contract:
  - `scripts/test/check_rematch_delta_publishability.py`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_publishable_delta_shortlists.md`
- Tightened planning guidance:
  - do not publish every persistent micro-island as if it were equally benchmark-worthy,
  - instead expose one **guardrail-filtered shortlist** keyed by a declared budget family, width floor, and hazard threshold,
  - and in the current proxy a width floor of `0.0010` reduces `13` canonical family cores to `3` publishable anchors overall, only `2` of which lie below `delta=0.01`.

## 2026-03-06 — Research Pass XXXV (Delta Preference + Declared Anchor Priorities)

- Added a derived rematch delta-preference snapshot for the strict sub-`0.01` publishability shortlist:
  - `scripts/report/build_rematch_proxy_delta_preference_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_preference_snapshot_20260306.{md,json}`
- Added a validator for the shortlist choice contract:
  - `scripts/test/check_rematch_delta_preference.py`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_declared_anchor_priorities.md`
- Tightened planning guidance:
  - do not pretend a guardrail shortlist has already collapsed to one objectively best scalar anchor,
  - publish Pareto nondominance plus a declared priority profile for breaking shortlist ties,
  - and in the current proxy the low-delta shortlist still has `2` Pareto-nondominated anchors, with `material_first` selecting `0.00602` and `stability_first` selecting `0.00744`.


## 2026-03-06 — Research Pass XXXVII (Width-Floor Plateaus + Stable Guardrail Bands)

- Added a derived rematch delta width-floor plateau snapshot for the current leave/rematch proxy:
  - `scripts/report/build_rematch_proxy_delta_width_floor_plateau_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_width_floor_plateau_snapshot_20260306.{md,json}`
- Added a validator for the width-floor plateau contract:
  - `scripts/test/check_rematch_delta_width_floor_plateaus.py`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_width_floor_plateau_contracts.md`
- Tightened planning guidance:
  - declare a width-floor **band** whenever a broad plateau leaves the shortlist unchanged,
  - do not let one lucky minimum-width threshold masquerade as a uniquely canonical scalar,
  - and in the current proxy the `10/20/50/100` family has a two-candidate plateau on `(0.00026, 0.00129]`, while the corresponding `4/10/20/50/100` plateau is only `(0.00021, 0.00029]`.

## 2026-03-06 — Research Pass XXXVI (Delta Family Viability + Declared Cap Profiles)

- Added a derived rematch delta-family viability snapshot comparing exact budget-family declarations already present in the current proxy:
  - `scripts/report/build_rematch_proxy_delta_family_viability_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_family_viability_snapshot_20260306.{md,json}`
- Added a validator for the family-declaration contract:
  - `scripts/test/check_rematch_delta_family_viability.py`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_declared_budget_family_profiles.md`
- Tightened planning guidance:
  - declare the exact budget-family profile before applying width floors or priority profiles,
  - do not let “all caps we touched” silently become the required family,
  - and in the current proxy the `10/20/50/100` family still supports `2` sub-`0.01` candidates at width floor `0.0010`, while the `4/10/20/50/100` family supports `0`.

## 2026-03-06 — Research Pass XXXVIII (Hazard-Cap Profiles + Guardrail Inactivity)

- Added a derived rematch delta hazard-cap profile snapshot comparing tested hazard caps for the current width-qualified low-delta families:
  - `scripts/report/build_rematch_proxy_delta_hazard_cap_profile_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_hazard_cap_profile_snapshot_20260306.{md,json}`
- Added a validator for the hazard-cap profile contract:
  - `scripts/test/check_rematch_delta_hazard_cap_profiles.py`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_declared_hazard_cap_profiles.md`
- Tightened planning guidance:
  - declare the hazard-cap profile explicitly,
  - but do not pretend that a hazard guardrail selected the shortlist when the shortlist is invariant across the tested cap range,
  - and in the current proxy the `10/20/50/100` family at width floor `0.0010` keeps the same two sub-`0.01` candidates and the same priority winners from hazard cap `100` through `10000`, while the `4/10/20/50/100` family stays empty throughout.


## 2026-03-06 — Research Pass XXXIX (Delta-Ceiling Plateaus + Threshold Slack)

- Added a derived rematch delta-ceiling plateau snapshot for the current width-qualified hazard-clear families:
  - `scripts/report/build_rematch_proxy_delta_ceiling_plateau_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_ceiling_plateau_snapshot_20260306.{md,json}`
- Added a validator for the delta-ceiling plateau contract:
  - `scripts/test/check_rematch_delta_ceiling_plateaus.py`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_delta_ceiling_plateau_contracts.md`
- Tightened planning guidance:
  - declare a delta-ceiling **band** whenever a broad plateau leaves the shortlist unchanged,
  - do not treat `0.01` as uniquely canonical when a much wider ceiling range preserves the same low-delta shortlist,
  - and in the current proxy the `10/20/50/100` family at width floor `0.0010` keeps the same two hazard-clear candidates for every ceiling in `(0.00822, 0.01944]`, while only ceilings above `0.01944` admit the wider high-delta `TTTTTTMUT` regime.

## 2026-03-06 — Research Pass XL (Hazard Thresholds + Policy-Box Synthesis)

- Added a derived rematch delta hazard-threshold snapshot for the current family10 low-delta shortlist:
  - `scripts/report/build_rematch_proxy_delta_hazard_threshold_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_hazard_threshold_snapshot_20260306.{md,json}`
- Added a validator for the exact hazard-clearance threshold contract:
  - `scripts/test/check_rematch_delta_hazard_thresholds.py`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_monotone_hazard_clearance_thresholds.md`
- Tightened planning guidance:
  - publish a **minimum hazard-clearance threshold** rather than only a few sampled caps whenever the guardrail shrinks monotonically with added budget,
  - expose the exact cap at which the full intended shortlist first appears,
  - and in the current proxy the family `10/20/50/100` shortlist is empty for caps `0..4`, singleton for `5..9`, and fully restored from cap `10` onward, so the earlier sampled minimum cap `100` overshot the exact threshold by `90` paired seeds and by a factor of `10`.

## 2026-03-06 — Research Pass XLI (Policy-Box Corners + Interaction Certification)

- Added a derived rematch delta policy-box corner snapshot for the synthesized family10 policy box:
  - `scripts/report/build_rematch_proxy_delta_policy_box_corner_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_policy_box_corner_snapshot_20260306.{md,json}`
- Added a validator for representative-corner invariance:
  - `scripts/test/check_rematch_delta_policy_box_corners.py`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_policy_box_corner_certification.md`
- Tightened planning guidance:
  - do not publish a Cartesian product of one-dimensional plateaus until representative corners certify that no latent candidate appears only when several knobs are relaxed together,
  - identify the genuinely binding face of the box so future recomputation knows where breakage is most likely,
  - and in the current proxy all eight representative corners of the family `10/20/50/100` policy box keep the same two-anchor shortlist and the same priority winners, while the strict hazard/width edge around `TTTMMMMMU` is the first face likely to fail.



## 2026-03-06 — Research Pass XLIII (Hazard Preference Regimes + Exact Cap Crossovers)

- Added a derived rematch delta hazard-preference regime snapshot for the certified family10 policy box:
  - `scripts/report/build_rematch_proxy_delta_hazard_preference_regime_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_hazard_preference_regime_snapshot_20260306.{md,json}`
- Added a validator for exact hazard-preference regime boundaries:
  - `scripts/test/check_rematch_delta_hazard_preference_regimes.py`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_hazard_preference_regime_contracts.md`
- Tightened planning guidance:
  - once the final choice has collapsed to two anchors, publish the hazard term as an exact discrete cap-regime contract rather than as a vague sensitivity note,
  - expose both the first cap where hazard clearance flips sign and the first cap where the binding hazard panel itself changes,
  - and in the current proxy the family `10/20/50/100` policy box has three exact hazard-preference regimes: caps `10..14` still favor `TTTMMMMUU`, caps `15..19` favor `TTTMMMMMU` with the same binding panels, and caps `20+` remain weakly material-favoring after `TTTMMMMMU` switches to a different binding hazard panel.

## 2026-03-06 — Research Pass XLII (Preference Half-Spaces + Explicit Separating Inequalities)

- Added a derived rematch delta preference half-space snapshot for the certified family10 policy box:
  - `scripts/report/build_rematch_proxy_delta_preference_halfspace_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_preference_halfspace_snapshot_20260306.{md,json}`
- Added a validator for the remaining two-anchor separating boundary:
  - `scripts/test/check_rematch_delta_preference_halfspaces.py`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_preference_separating_inequalities.md`
- Tightened planning guidance:
  - once a certified policy box leaves only two live anchors, replace vague preference-profile language with an explicit separating inequality over declared metric premiums,
  - record which declared knobs still move that inequality and which ones have dropped out entirely,
  - and in the current proxy width floor and delta ceiling no longer affect the final family `10/20/50/100` choice at all, while the only moving coefficient is hazard clearance, whose contribution to the stability anchor shifts from `+0.000464 * w_hazard` at cap `10` to `-0.000033 * w_hazard` at cap `10000`.


## 2026-03-06 — Research Pass XLV (Normalized Cap Trajectories + Double-Reversal Contracts)

- Added a derived rematch delta normalized cap-trajectory snapshot for the final two-anchor choice inside the certified family10 policy box:
  - `scripts/report/build_rematch_proxy_delta_normalized_cap_trajectory_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_normalized_cap_trajectory_snapshot_20260306.{md,json}`
- Added a validator for the hazard-normalized cap-trajectory contract:
  - `scripts/test/check_rematch_delta_normalized_cap_trajectories.py`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_hazard_normalized_cap_trajectory_contracts.md`
- Tightened planning guidance:
  - once the final choice has collapsed to two anchors, normalize the non-hazard surplus by the declared hazard weight and classify the entire cap trajectory from that one scalar,
  - do not assume added budget can only reverse the winner once, because some declared preferences create a real mid-cap material pocket before tail stability returns,
  - and in the current proxy the exact threshold curve is strictly increasing on caps `10..20` and strictly decreasing thereafter, so `rho` values in `(0.000033068, 0.000313597)` produce the path `TTTMMMMUU -> TTTMMMMMU -> TTTMMMMUU` as cap rises across the checked range.



## 2026-03-06 — Research Pass XLVII (Adaptive Cap Probes + Branch-Optimal Classification)

- Added a derived rematch delta adaptive-cap-probe snapshot for the final two-anchor strict class diagnosis inside the certified family10 policy box:
  - `scripts/report/build_rematch_proxy_delta_adaptive_cap_probe_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_adaptive_cap_probe_snapshot_20260306.{md,json}`
- Added a validator for the unique worst-case-optimal adaptive decision tree:
  - `scripts/test/check_rematch_delta_adaptive_cap_probes.py`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_adaptive_cap_probe_contracts.md`
- Tightened planning guidance:
  - distinguish fixed-signature probe minimization from adaptive branch-on-result minimization, because they answer different handoff needs,
  - when the strict class boundaries form a two-pair split around one exact threshold, use that boundary as the unique root probe and finish each branch with the exact remaining pairwise boundary witness,
  - and in the current proxy the unique worst-case-optimal adaptive classifier probes cap `10000` first, then cap `10` after `M` or cap `20` after `S`, so universal strict-class diagnosis needs only two adaptive probes even though any non-adaptive signature still needs three.

## 2026-03-06 — Research Pass XLVI (Unique Minimal Cap Probes + Boundary Necessity)

- Added a derived rematch delta unique-minimal-cap-probe snapshot for the final two-anchor choice inside the certified family10 policy box:
  - `scripts/report/build_rematch_proxy_delta_unique_minimal_cap_probe_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_unique_minimal_cap_probe_snapshot_20260306.{md,json}`
- Added a validator for uniqueness of the strict-winner probe triple:
  - `scripts/test/check_rematch_delta_unique_minimal_cap_probes.py`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_unique_minimal_cap_probe_contracts.md`
- Tightened planning guidance:
  - once a finite cap-probe set is claimed sufficient, also certify whether it is uniquely forced by the adjacent strict-class boundaries rather than merely convenient,
  - require exact threshold witnesses for each adjacent open class pair instead of accepting “nearby” substitute caps,
  - and in the current proxy the strict-winner triple `[10, 20, 10000]` is uniquely forced because only those caps realize `tau(10)`, `tau(20)`, and `tau(10000)` exactly.
- Repo hygiene:
  - restored the executable bit on `tools/rust_exec.sh`, which advances `make test-quick` past the inherited permission error and exposes the next real blocker: missing `junest` at `/run/sandworm/toolroot/bin/junest` during `rust_lib_tests`.


## 2026-03-06 — Research Pass XLIX (Question-Targeted Probes + Minimal Routing)

- Added a derived rematch delta question-targeted probe snapshot for the final family10 two-anchor cap diagnostics:
  - `scripts/report/build_rematch_proxy_delta_question_targeted_probe_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_question_targeted_probe_snapshot_20260306.{md,json}`
- Added a validator for the question-to-probe routing contract:
  - `scripts/test/check_rematch_delta_question_targeted_probes.py`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_question_targeted_probe_contracts.md`
- Tightened planning guidance:
  - match the probe contract to the actual handoff question rather than defaulting to the strictest three-cap signature,
  - reserve cap `10000` for the narrower task of separating the two cap-sensitive strict subclasses,
  - and in the current proxy the portable overturn-risk question needs only `[10, 20]`, while exact strict-path reporting still uniquely needs `[10, 20, 10000]`.

## 2026-03-06 — Research Pass XLVIII (Cap-Robustness Probes + Early-Stop Triage)

- Added a derived rematch delta robustness-probe snapshot for the final two-anchor choice inside the certified family10 policy box:
  - `scripts/report/build_rematch_proxy_delta_robustness_probe_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_robustness_probe_snapshot_20260306.{md,json}`
- Added a validator for cap-robustness triage by strict winner probes:
  - `scripts/test/check_rematch_delta_robustness_probes.py`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_cap_robustness_probe_contracts.md`
- Tightened planning guidance:
  - distinguish exact cap-path classification from the smaller question of whether added budget can ever overturn the final choice,
  - when only cap-robustness matters, drop the middle strict boundary `tau(10000)` and switch to the unique minimal non-adaptive probe pair `[10, 20]`,
  - and in the current proxy this yields two symmetric early-stop adaptive trees: probe `10` first for the fastest robust-material certificate or probe `20` first for the fastest robust-stability certificate.

## 2026-03-06 — Research Pass L (Decision Normal Forms + Zero-Probe Direct Classification)

- Added a derived rematch delta decision-normal-form snapshot for the final family10 two-anchor handoff:
  - `scripts/report/build_rematch_proxy_delta_decision_normal_form_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_normal_form_snapshot_20260306.{md,json}`
- Added a validator for the canonical policy-box / rho-routing normal form:
  - `scripts/test/check_rematch_delta_decision_normal_form.py`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_decision_normal_forms.md`
- Tightened planning guidance:
  - stop treating cap probes as the default interface once the declared preference weights are available, because the final family10 choice can then be classified directly from `rho` with zero probes,
  - canonicalize the policy-box representation before building operator-facing digests, because the same box had been carried under slightly different field names across prior reports,
  - and in the current proxy the full handoff normal form is now: certify the family `10/20/50/100` box, compare `rho` against `tau(10)`, `tau(10000)`, and `tau(20)` when weights are known, and only fall back to `[10,20,10000]`, `10000 -> (10 or 20)`, or `[10,20]` when the choice must be diagnosed from black-box winner symbols alone.
- Repo hygiene:
  - restored execute bits on shell entrypoints such as `scripts/test/run_harness.sh`, which advances `make test-quick` past the new archive-level permission stop and re-exposes the inherited environment blocker: missing `junest` at `/run/sandworm/toolroot/bin/junest` during `rust_lib_tests`.

## 2026-03-06 — Research Pass LI (Projective Decision Cones + Scale-Free Direct Classification)

- Added a derived rematch delta projective-decision-cone snapshot for the final family10 two-anchor handoff:
  - `scripts/report/build_rematch_proxy_delta_projective_decision_cone_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_projective_decision_cone_snapshot_20260306.{md,json}`
- Added a validator for the singularity-free direct classifier:
  - `scripts/test/check_rematch_delta_projective_decision_cones.py`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_projective_decision_cones.md`
- Tightened planning guidance:
  - stop treating `rho = B/H` as the fundamental handoff object, because the final classifier can be written directly as homogeneous inequalities in `B = baseline_nonhazard_surplus` and `H = w_hazard`,
  - make the zero-hazard axis explicit instead of burying it as a degenerate exception, because `H = 0` supports only robust material, robust stability, or total tie,
  - and in the current proxy positive global rescaling of the declared preference weights cannot change the strict class, so the final family10 decision is genuinely scale-free once the certified policy box applies.


## 2026-03-06 — Research Pass LII (Executable Decision Oracle + Declaration-First Interface)

- Added an executable family10 rematch-proxy delta oracle for direct classification from declared weights or direct `(B,H)` coordinates:
  - `scripts/analysis/rematch_proxy_delta_decision_oracle.py`
- Added a derived decision-oracle snapshot for inheritor-facing handoff:
  - `scripts/report/build_rematch_proxy_delta_decision_oracle_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_oracle_snapshot_20260306.{md,json}`
- Added a validator for the executable oracle contract:
  - `scripts/test/check_rematch_delta_decision_oracle.py`
- Added an inheritor-facing note on the reporting consequence:
  - `docs/LIBRARY/topics/rematch_worlds_need_executable_decision_oracles.md`
- Tightened planning guidance:
  - stop treating the final family10 classifier as prose once the exact threshold rays are known, because the declaration-first route should be executable rather than re-derived by hand,
  - accept both direct projective coordinates `(B,H)` and the declared weight vector as first-class oracle inputs, because future sessions may already have either representation,
  - and keep black-box probe bundles explicitly subordinate to the oracle interface: use `[10,20]`, `[10,20,10000]`, or `10000 -> (10 or 20)` only when the final choice must be diagnosed from winner symbols alone.

## 2026-03-07 — Research Pass LIV (Shared Packet Profiles + Archive-Local Citation Storage)

- Added archive-local decision-packet storage with shared provenance profiles for the family10 rematch-delta handoff:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_profile_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_profile_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_profiles.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_share_decision_packet_provenance_profiles.md`
- Tightened planning guidance:
  - choose the smallest packet storage form in addition to the smallest packet mode,
  - keep archive-local packets as the default long-lived representation inside this archive,
  - and expand to standalone packets only when a packet must travel without the shared profile registry.
- Main local result:
  - replacing repeated provenance with a shared archive-local profile saves `331` minified bytes per tested packet, which is `34.37%` to `46.23%` across the current representative family10 packet forms.


## 2026-03-07 — Research Pass LV (Semantic Packet Fingerprints + Duplicate-Eliding Archive Writes)

- Added semantic fingerprinting and duplicate-eliding archive write planning for family10 rematch decision packets:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_fingerprint_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_fingerprint_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_fingerprints.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_deduplicate_decision_packets_by_semantic_fingerprint.md`
- Tightened planning guidance:
  - stop treating standalone and archive-local packets as distinct long-lived objects when they expand to the same canonical decision packet,
  - store one archive-local packet body per semantic fingerprint,
  - and replace later repeats with lightweight fingerprint references instead of duplicate packet bodies.
- Main local result:
  - the representative declaration-first duplicate now saves `326` bytes on the repeat write, while the exact checked-cap tie packet still saves `235` bytes on the repeat write.



## 2026-03-07 — Research Pass LVI (Semantic Cores + Minimal First-Write Bodies)

- Added semantic-core storage for family10 rematch decision packets so new semantic decisions can be stored as the smallest deterministic seed rather than as a full archive-local packet body:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_core_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_core_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_cores.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_store_semantic_cores_before_archive_local_packets.md`
- Tightened planning guidance:
  - stop treating archive-local packets as the smallest durable body once the archive already contains the executable packet expander,
  - keep one semantic core per semantic fingerprint for long-lived storage,
  - materialize archive-local packets only for directly readable in-archive views,
  - and reserve standalone packets for export outside the archive.
- Main local result:
  - shrinking the first durable body from archive-local packet to semantic core saves `121` to `346` minified bytes across the representative family10 packet set, with the largest gain on the declaration-first weight packet.

## 2026-03-07 — Research Pass LVIII (Mode-Coded Seeds + Smallest First-Write Bodies)

- Added archive-local mode-coded seeds for the family10 rematch decision packet path so first writes can drop repeated semantic-core wrapper strings when the local codebook is available:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_coded_seed_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_coded_seed_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_coded_seeds.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_store_mode_coded_seeds_inside_archive.md`
- Tightened planning guidance:
  - stop treating semantic cores as the smallest durable body once the archive also commits to preserving a local mode/field codebook,
  - keep coded seeds as the default first-write body for archive-local storage,
  - retain semantic cores as the more self-describing fallback tier,
  - and continue pairing new coded-seed first writes with prefix references on repeats.
- Main local result:
  - representative semantic cores shrink by `120` to `138` additional minified bytes when recoded as archive-local seeds, with the largest gain on the exact checked-cap tie packet.


## 2026-03-07 — Research Pass LX (Tagged Microframes + Smallest In-Archive Writes)

- Added tagged microframe storage for family10 rematch decision packets so both first writes and repeats can drop the remaining JSON object-key overhead once the archive preserves a tiny positional decoder:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_microframe_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_microframe_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_microframes.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_store_tagged_microframes_inside_archive.md`
- Tightened planning guidance:
  - stop treating object-wrapped coded packets as the smallest durable archive forms once the archive also commits to preserving a tiny positional decoder,
  - keep `micro_seed` as the default first-write body,
  - keep `micro_reference` as the default repeat pointer,
  - and keep coded seeds/references as the clearer fallback tier for debugging or manual inspection.
- Main local result:
  - representative coded seeds shrink by `36` to `40` additional minified bytes when recoded as tagged microframes,
  - representative coded references shrink by another `11` bytes each,
  - and the two-write total for the declaration-first coordinate case drops from `90` to `39` bytes.

## 2026-03-07 — Research Pass LXI (Packed Nanoframes + Finite-Payload Codes)

- Added packed nanoframe storage for family10 rematch decision packets so both first writes and repeats can compress below tagged microframes once the archive preserves a slightly richer local codec:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_packed_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_packed_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_packed.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_store_packed_nanoframes_inside_archive.md`
- Tightened planning guidance:
  - stop treating tagged microframes as the smallest durable archive forms once the archive also commits to preserving a richer local packed codec,
  - keep `packed_seed` as the default first-write body,
  - keep `packed_reference` as the default repeat pointer,
  - and keep micro seeds/references as the clearer tagged-array fallback tier.
- Main local result:
  - representative micro seeds shrink by another `13` bytes for adaptive robustness routes and `6` bytes for exact checked-cap tie packets when recoded as packed seeds,
  - declaration-first coordinate and weight seeds still save `3` bytes each by dropping the string mode tag,
  - and repeat pointers shrink from `20` to `14` minified bytes by base64url-packing the shortest even-length local prefix.

## 2026-03-07 — Research Pass LXII (Packed Weight Vectors + Keyless Axis Masks)

- Tightened the family10 packed-seed codec for `oracle_weights` so first writes no longer carry a full eight-key JSON map inside the packed tier:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_weight_vector_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_weight_vector_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_weight_vectors.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_store_keyless_weight_vectors_inside_packed_seeds.md`
- Tightened planning guidance:
  - keep `packed_seed` as the default first-write body when the local packed codec is available,
  - but store `oracle_weights` payloads as a fixed-order nonzero vector behind one bitmask instead of repeating eight axis names and explicit zero coordinates,
  - while leaving micro seeds as the clearer fallback tier when operators want a more transparent local representation.
- Main local result:
  - hazard-only weight declarations shrink from `125` minified bytes in the legacy packed form to `11` bytes,
  - mixed sparse declarations shrink from `129` to `27` bytes,
  - dense all-ones declarations still shrink from `125` to `39` bytes,
  - and the representative packed snapshot now saves `117` bytes over the micro-seed fallback on the declaration-first weight example.

## 2026-03-07 — Research Pass LXIII (Packed Scalar Atoms + Common Decimal Codebook)

- Tightened the family10 packed-seed codec so declaration-first coordinate and weight packets no longer repeat the archive's most common canonical decimal strings inside the packed tier:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_scalar_atom_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_scalar_atom_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_scalar_atoms.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_atomize_common_decimal_scalars_inside_packed_seeds.md`
- Tightened planning guidance:
  - keep `packed_seed` as the default first-write tier when the local packed codec is available,
  - but treat repeated canonical decimal strings like `1`, `0.5`, `2`, `0.2`, `0.0001`, and `0.000000` as shared scalar atoms inside that codec,
  - while leaving raw strings as the fallback for uncommon payload values.
- Main local result:
  - the representative coordinate seed shrinks from `16` to `7` bytes,
  - the hazard-only packed weight seed shrinks from `11` to `9` bytes,
  - the mixed sparse packed weight seed shrinks from `27` to `15` bytes,
  - and the dense all-ones packed weight seed shrinks from `39` to `23` bytes.

## 2026-03-07 — Research Pass LXIV (Grouped Weight Atoms + Repeated-Value Masks)

- Tightened the family10 packed-seed codec for `oracle_weights` so repeated-value declarations no longer pay one scalar atom per active axis when a grouped mask form is smaller:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_weight_atom_group_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_weight_atom_group_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_weight_atom_groups.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_group_repeated_weight_atoms_inside_packed_seeds.md`
- Tightened planning guidance:
  - keep `packed_seed` as the default first-write tier when the local packed codec is available,
  - keep the existing scalar-atom sparse vector as the fallback for one-hot or irregular weight declarations,
  - but when several active axes share the same scalar atom, store one axis mask per repeated atom instead of one atom code per active axis.
- Main local result:
  - one-hot hazard declarations stay at `9` minified bytes because grouping does not help,
  - dense all-ones weight declarations shrink from `23` to `12` bytes,
  - and a representative two-atom block profile shrinks from `23` to `17` bytes.

## 2026-03-07 — Research Pass LXV (Base64url Byteframes + Wrapper-Free Packed Writes)

- Tightened the family10 packed storage ladder so first writes and repeats no longer pay JSON list punctuation once the archive already preserves the packed semantic codec:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_byteframe_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_byteframe_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_byteframes.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_store_base64url_byteframes_inside_archive.md`
- Tightened planning guidance:
  - keep `byte_seed` as the default first-write tier when the local byteframe codec is available,
  - keep `byte_reference` as the default repeat tier when the local byteframe codec is available,
  - and treat numeric packed arrays as the clearer fallback tier when operators want inspectable local payloads during debugging.
- Main local result:
  - the representative coordinate seed shrinks from `7` to `6` bytes,
  - the hazard-only packed weight seed shrinks from `9` to `8` bytes,
  - the dense grouped-weight seed shrinks from `12` to `9` bytes,
  - the exact checked-cap tie seed shrinks from `6` to `5` bytes,
  - and repeat references shrink from `14` to `12` bytes by storing the tag byte and raw local-prefix bytes in one base64url string.

## 2026-03-07 — Research Pass LXVI (Measured Frontiers + Payload-Specific Codec Choice)

- Tightened the family10 local write planner so it no longer assumes the newest local codec is always smallest for every packet:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_frontier_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_frontier_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_frontiers.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_local_decision_packet_codecs_by_measured_bytes.md`
- Tightened planning guidance:
  - keep the ladder as a capability prior,
  - but choose the enabled first-write codec by measured minified bytes for the specific packet,
  - keep `byte_reference` as the measured repeat winner under the current codec stack,
  - and allow tiny `oracle_weights` packets to stay `packed_seed` when that saves a byte over `byte_seed`.
- Main local result:
  - on a deterministic 274-packet frontier set, `byte_reference` stayed the measured winner for all repeats,
  - `byte_seed` stayed the measured winner for 250 first writes,
  - but 24 first-write exceptions switched to `packed_seed`,
  - with the smallest known counterexample shrinking from `8` minified bytes as `byte_seed` to `7` as `packed_seed`.

## 2026-03-07 — Research Pass LXX (Short Catalog Slots + Constant-Width Repeat IDs)

- Tightened the append-only catalog repeat path so the common under-`16384` slot range no longer pays a full tag-plus-uvarint wrapper:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_short_catalog_reference_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_short_catalog_reference_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_short_catalog_references.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_store_short_catalog_slot_references_inside_small_append_only_catalogs.md`
- Tightened planning guidance:
  - keep the ordered append-only fingerprint catalog as the enabling state,
  - prefer `short_catalog_reference` for repeat writes while the local slot fits below `16384`,
  - fall back to the older `catalog_reference` once the catalog outgrows that short range,
  - and fall back again to `byte_reference` when only an unordered fingerprint set is available.
- Main local result:
  - generic catalog-slot references still cost `1516` total minified bytes on the deterministic 274-packet frontier,
  - short catalog-slot references reduce that to `1370`,
  - saving another `146` bytes (`0.096306` share) against generic catalog references and `1918` bytes (`0.583333` share) against prefix byteframes,
  - with every current repeat flattening to a constant `5` bytes.

## 2026-03-07 — Research Pass LXXI (Paged Resolution + Direct Slot Lookup)

- Tightened the append-only catalog repeat path so slot references can resolve directly from the compact paged raw-digest catalog the archive already stores:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_catalog_page_resolution_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_catalog_page_resolution_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_catalog_page_resolution.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_resolve_catalog_slot_references_directly_from_paged_digest_catalogs.md`
- Tightened planning guidance:
  - keep the ordered semantic-fingerprint catalog as append-only raw-digest pages,
  - resolve `short_catalog_reference` and `catalog_reference` packets straight from those pages,
  - and only rebuild the ordered `sha256:` string list when a human-readable export or debugging surface actually needs it.
- Main local result:
  - the full ordered string catalog still costs `20277` bytes and the full paged digest catalog costs `11714`,
  - but direct slot resolution now touches only the target page, averaging `2605.109489` bytes across the deterministic 274-packet frontier,
  - avoiding `17671.890511` bytes on average (`0.871524` share) versus rebuilding the full ordered string catalog and `9108.890511` bytes (`0.777607` share) versus scanning the whole paged catalog.


## 2026-03-07 — Research Pass LXXII (Page-Native Repeat Planning + Compact-State Writes)

- Tightened the append-only catalog repeat path so the live writer can detect repeats and emit slot references directly from compact paged raw-digest catalog state:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_catalog_page_write_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_catalog_page_write_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_catalog_page_writes.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_plan_repeat_writes_directly_from_paged_digest_catalogs.md`
- Tightened planning guidance:
  - keep the semantic-fingerprint catalog as append-only raw-digest pages,
  - detect repeat fingerprints directly from those pages,
  - emit `short_catalog_reference` / `catalog_reference` from the discovered slot,
  - and only rebuild the ordered `sha256:` string catalog when a human-readable surface actually needs it.
- Main local result:
  - on the deterministic 274-packet frontier, page-native yocto planning matches the ordered-catalog yocto planner on all `274 / 274` repeat decisions at the core-field level,
  - every current repeat still lands on `short_catalog_reference`,
  - average repeat lookup scans `7155.124088` bytes,
  - avoiding `13121.875912` bytes (`0.647131` share) versus rebuilding the full ordered string catalog and `4558.875912` bytes (`0.389182` share) versus scanning the full paged catalog list.

## 2026-03-16 — Research Pass (World Benchmark Completion Gate + Fill-Status Snapshot)

- Added one executable completion gate for the first endogenous rematch-world benchmark so the inheritor can tell when the retained seed has become a publishable one-artifact benchmark instead of a placeholder scaffold:
  - `scripts/tools/rematch_world_benchmark_completion_gate.py`
  - `scripts/report/build_rematch_world_benchmark_fill_status_snapshot.py`
  - `artifacts/reports/rematch_world_benchmark_fill_status_snapshot_20260316.{md,json}`
  - `schemas/rematch_world_benchmark_fill_status.schema.json`
  - `scripts/test/check_rematch_world_benchmark_fill_status.py`
  - `docs/LIBRARY/topics/filled_rematch_benchmarks_should_clear_template_slots_without_touching_open_ended_decision_intervals.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` so the benchmark program now states the exact completion rule for the first endogenous rematch benchmark.
- Main local result:
  - the retained seed is now measured as a `24`-slot fill job (`13` template strings + `11` world-dependent null telemetry fields),
  - the archive now distinguishes those real fill blockers from the `3` legitimate open-ended `end_delay: null` intervals inside the copied compact decision bundle,
  - and the next inheritor can use a single completion gate to clear placeholders in place without mutating the standing phase-3 contract.

## 2026-03-16 — Research Pass (World Benchmark Mutation Guard + Edit-Surface Snapshot)

- Added one executable mutation guard for the first endogenous rematch-world benchmark so the inheritor can fill the seed without drifting the copied contract surface:
  - `scripts/tools/rematch_world_benchmark_mutation_guard.py`
  - `scripts/report/build_rematch_world_benchmark_mutation_surface_snapshot.py`
  - `artifacts/reports/rematch_world_benchmark_mutation_surface_snapshot_20260316.{md,json}`
  - `schemas/rematch_world_benchmark_mutation_surface.schema.json`
  - `scripts/test/check_rematch_world_benchmark_mutation_surface.py`
  - `docs/LIBRARY/topics/filled_rematch_benchmarks_should_only_mutate_the_seed_edit_surface.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` so the benchmark workflow now says to run the mutation guard alongside the completion gate before publication.
- Main local result:
  - a publishable filled benchmark now has an explicit 12-prefix edit surface (`2` metadata paths, `5` status flips, `5` world-data prefixes),
  - the copied compact decision bundle plus publication / decision contract pointers are now explicitly frozen during fill work,
  - and the three row-based world sections remain prefix-open so richer benchmark rows can be added inside the retained artifact instead of by growing new sidecar report families.

## 2026-03-16 — Research Pass (World Benchmark Fill Patch + Compile-Back Workflow)

- Added one compact fill-patch workflow for the first endogenous rematch-world benchmark so the inheritor can do scratch fill work without repeatedly editing a seed that embeds the frozen decision bundle:
  - `schemas/rematch_world_benchmark_fill_patch.schema.json`
  - `scripts/report/build_rematch_world_benchmark_fill_patch_example.py`
  - `examples/snapshots/rematch_world_benchmark_fill_patch.json`
  - `scripts/tools/apply_rematch_world_benchmark_fill_patch.py`
  - `scripts/report/build_rematch_world_benchmark_patch_compaction_snapshot.py`
  - `artifacts/reports/rematch_world_benchmark_patch_compaction_snapshot_20260316.{md,json}`
  - `scripts/test/check_rematch_world_benchmark_fill_patch.py`
  - `docs/LIBRARY/topics/rematch_world_benchmark_fill_work_should_flow_through_one_tiny_patch_then_compile_back_to_one_artifact.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` so the benchmark workflow now says to fill one compact patch, compile it back onto the seed, and then run the standing mutation/completion gates on the compiled artifact.
- Main local result:
  - the standing seed weighs `51329` bytes,
  - the compact fill patch weighs `2372` bytes,
  - saving `48957` bytes (`0.953788` share) during scratch fill work,
  - while still compiling back onto the retained one-artifact benchmark shape with the frozen `compact_decision_bundle` preserved.

## 2026-03-16 — Research Pass (World Benchmark Publication Preflight + Receipt Snapshot)

- Added one consolidated publication preflight for the first endogenous rematch-world benchmark so the inheritor can compile patch work, verify the allowed edit surface, verify completion readiness, and fingerprint the frozen copied contract surface in one command:
  - `scripts/tools/rematch_world_benchmark_publication_preflight.py`
  - `scripts/report/build_rematch_world_benchmark_preflight_snapshot.py`
  - `artifacts/reports/rematch_world_benchmark_preflight_snapshot_20260316.{md,json}`
  - `schemas/rematch_world_benchmark_preflight.schema.json`
  - `scripts/test/check_rematch_world_benchmark_preflight.py`
  - `docs/LIBRARY/topics/filled_rematch_benchmarks_should_pass_one_consolidated_preflight_receipt.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` so the benchmark workflow now ends with one consolidated preflight receipt rather than a remembered sequence of separate checks.
- Main local result:
  - the standing template patch now has an explicit machine-checkable state of “inside the allowed edit surface but not yet publishable”,
  - that state currently means `0` forbidden changed paths, `24` real fill blockers, and `3` allowed open-ended decision nulls,
  - and the copied compact decision bundle now carries a stable SHA-256 digest that can be cited in future handoff notes without reprinting the bundle itself.

## 2026-03-16 — Research Pass (Evidence Packet + Packet-to-Patch Compiler)

- Added one tiny evidence-packet workflow for the first endogenous rematch-world benchmark so future real runs can retain only distilled world facts while leaving bulky traces scratch-only:
  - `schemas/rematch_world_benchmark_evidence_packet.schema.json`
  - `scripts/report/build_rematch_world_benchmark_evidence_packet_example.py`
  - `examples/snapshots/rematch_world_benchmark_evidence_packet.json`
  - `scripts/tools/compile_rematch_world_benchmark_fill_patch_from_evidence_packet.py`
  - `scripts/report/build_rematch_world_benchmark_evidence_flow_snapshot.py`
  - `artifacts/reports/rematch_world_benchmark_evidence_flow_snapshot_20260316.{md,json}`
  - `scripts/test/check_rematch_world_benchmark_evidence_packet.py`
  - `docs/LIBRARY/topics/first_endogenous_rematch_benchmarks_should_distill_one_tiny_evidence_packet_before_compiling_the_fill_patch.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` so the benchmark workflow now says to distill one tiny evidence packet after a real run, compile it into the standard fill patch, and keep bulky traces scratch-only once the distilled facts are retained.
- Main local result:
  - the retained evidence packet example weighs `3103` bytes,
  - the compiled fill patch weighs `3176` bytes,
  - and both stay far smaller than the `51329`-byte standing seed while still compiling all the way through to a preflight-ready one-artifact benchmark with `0` fill blockers and `0` forbidden changed paths.

## 2026-03-16 — Research Pass (World Benchmark Retention Exit Receipt)

- Added one compact retention-exit receipt for the first endogenous rematch-world benchmark so the inheritor can distinguish durable publication objects from reconstructible intermediates and scratch that may leave once the publication spine is stable:
  - `schemas/rematch_world_benchmark_retention_exit_receipt.schema.json`
  - `scripts/tools/build_rematch_world_benchmark_retention_exit_receipt.py`
  - `scripts/report/build_rematch_world_benchmark_retention_exit_example.py`
  - `examples/snapshots/rematch_world_benchmark_retention_exit_receipt.json`
  - `scripts/report/build_rematch_world_benchmark_retention_exit_snapshot.py`
  - `artifacts/reports/rematch_world_benchmark_retention_exit_snapshot_20260316.{md,json}`
  - `scripts/test/check_rematch_world_benchmark_retention_exit_receipt.py`
  - `docs/LIBRARY/topics/rematch_world_benchmark_publication_should_end_with_one_retention_exit_receipt.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` and `artifacts/process/scratch_manifest.json` so the benchmark workflow now ends with one explicit cleanup boundary rather than an informal memory of what can be dropped.
- Main local result:
  - the retained publication set now has `6` durable objects weighing `64845` bytes,
  - the now-elidable transient set is exactly `4` objects (`1` compiled fill patch + `3` hashed scratch sources) weighing `3728` bytes,
  - and the exit receipt now says `retention_exit_ready=true` only when provenance, preflight, patch elision, and spine audit all agree.

## 2026-03-16 — Research Pass (Retention Exit Prune Workflow)

- Added one compact prune workflow for the first endogenous rematch-world benchmark so the inheritor can actually delete exit-ready scratch/intermediate files once the retention-exit receipt says the publication spine is stable:
  - `schemas/rematch_world_benchmark_prune_receipt.schema.json`
  - `scripts/tools/prune_rematch_world_benchmark_transients.py`
  - `scripts/report/build_rematch_world_benchmark_prune_snapshot.py`
  - `artifacts/reports/rematch_world_benchmark_prune_snapshot_20260316.{md,json}`
  - `scripts/test/check_rematch_world_benchmark_prune_receipt.py`
  - `docs/LIBRARY/topics/rematch_world_benchmark_retention_exit_receipts_should_drive_actual_pruning_not_just_describe_it.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` and `artifacts/process/scratch_manifest.json` so the benchmark workflow now ends with one explicit prune step instead of relying on memory after the retention-exit receipt is ready.
- Main local result:
  - the standing retention-exit example is already prune-ready in dry-run mode,
  - it names `3` concrete scratch-source files totaling `552` bytes that can leave by rule,
  - while the `3176`-byte compiled fill patch is already elided from the retained example workflow,
  - and the new execute path can delete one patch plus three scratch files in a temp workspace with `0` blocked rows.

## 2026-03-17 — Research Pass (Post-Prune Clean-Tree Audit)

- Added one compact post-prune audit for the first endogenous rematch-world benchmark so the inheritor can prove a cleaned worktree is actually safe to zip after transient cleanup:
  - `schemas/rematch_world_benchmark_post_prune_audit_receipt.schema.json`
  - `scripts/tools/audit_rematch_world_benchmark_post_prune_state.py`
  - `scripts/report/build_rematch_world_benchmark_post_prune_examples.py`
  - `examples/snapshots/rematch_world_benchmark_prune_execute_receipt.json`
  - `examples/snapshots/rematch_world_benchmark_post_prune_audit_receipt.json`
  - `scripts/report/build_rematch_world_benchmark_post_prune_snapshot.py`
  - `artifacts/reports/rematch_world_benchmark_post_prune_snapshot_20260316.{md,json}`
  - `scripts/test/check_rematch_world_benchmark_post_prune_audit.py`
  - `docs/LIBRARY/topics/rematch_world_benchmark_cleaned_worktrees_should_be_audited_before_the_next_zip.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` so the benchmark workflow now ends with an explicit clean-tree audit before the next revision zip is cut.
- Main local result:
  - the execute-mode prune example now deletes `4` transient files totaling `3728` bytes,
  - the post-prune audit then confirms `6/6` durable publication objects still hash-match,
  - `4/4` transient rows are absent or already unlinked,
  - and the cleaned example tree now says `cleaned_tree_ready_for_zip=true` instead of relying on an implicit cleanup boundary.


## 2026-03-17 — Research Pass (Canonicalization Bridge Receipt)

- Added one compact bridge receipt for the SG-003 canonicalization-first layer so the eventual inheritor can cite one durable handoff packet instead of reopening several larger rematch-proxy reports every session:
  - `schemas/rematch_world_canonicalization_bridge_receipt.schema.json`
  - `scripts/tools/build_rematch_world_canonicalization_bridge_receipt.py`
  - `scripts/report/build_rematch_world_canonicalization_bridge_example.py`
  - `examples/snapshots/rematch_world_canonicalization_bridge_receipt.json`
  - `scripts/report/build_rematch_world_canonicalization_bridge_snapshot.py`
  - `artifacts/reports/rematch_world_canonicalization_bridge_snapshot_20260317.{md,json}`
  - `scripts/test/check_rematch_world_canonicalization_bridge_receipt.py`
  - `docs/LIBRARY/topics/rematch_proxy_canonicalization_should_hand_forward_as_one_bridge_receipt.md`
- Regenerated inventory surfaces so the new schema/validator stay discoverable without widening the archive informally:
  - `docs/SCHEMA_INVENTORY.md`
  - `artifacts/reports/schema_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/validator_inventory.json`
- Main local result:
  - the retained bridge receipt links `24` still-open SG-003 canonicalization items (`6` assumptions + `9` questions + `9` risks),
  - carries the exact proxy-local planner contract across `4` validated noise modes with horizons `{none:3, opponent_tremble:2, focal_tremble:2, bilateral_tremble:1}`,
  - records the zero-noise dispatch compression from `243` flat signature rows to `17` ordered rules,
  - and keeps the handoff citation-first by hashing just `6` retained contract artifacts instead of duplicating the larger proxy reports.


## 2026-03-17 — Research Pass (Frozen-Handoff Guardrail Tightening)

- Tightened the rematch-world benchmark mutation guard so copied handoff sections cannot drift silently while world-dependent fields are being filled or recompiled:
  - `scripts/tools/rematch_world_benchmark_mutation_guard.py`
  - `scripts/report/build_rematch_world_benchmark_mutation_surface_snapshot.py`
  - `scripts/test/check_rematch_world_benchmark_mutation_surface.py`
  - `docs/BENCHMARK_PROGRAM.md`
- Regenerated the compiled benchmark publication spine so the standing artifact family actually preserves the copied canonicalization handoff end-to-end:
  - `examples/snapshots/rematch_world_benchmark_compiled_artifact.json`
  - `examples/snapshots/rematch_world_benchmark_preflight_receipt.json`
  - `examples/snapshots/rematch_world_benchmark_publication_bundle_receipt.json`
  - `examples/snapshots/rematch_world_benchmark_publication_spine_audit_receipt.json`
  - `examples/snapshots/rematch_world_benchmark_retention_exit_receipt.json`
  - `examples/snapshots/rematch_world_benchmark_post_prune_audit_receipt.json`
  - `artifacts/reports/rematch_world_benchmark_mutation_surface_snapshot_20260316.{md,json}`
  - `artifacts/reports/rematch_world_benchmark_publication_spine_snapshot_20260316.{md,json}`
  - `artifacts/reports/rematch_world_benchmark_publication_spine_audit_snapshot_20260316.{md,json}`
  - `artifacts/reports/rematch_world_benchmark_retention_exit_snapshot_20260316.{md,json}`
  - `artifacts/reports/rematch_world_benchmark_post_prune_snapshot_20260316.{md,json}`
- Main local result:
  - the mutation surface now freezes `14` prefixes instead of `12`, explicitly covering both `canonicalization_planner_contract` and `section_status.canonicalization_planner_contract`,
  - the standing compiled benchmark artifact once again carries the copied SG-003 handoff exactly,
  - and publication / post-prune receipts now hash the current compiled artifact rather than a stale pre-handoff build.

## 2026-03-17 — Research Pass (Frozen Seed Rebuild Audit)

- Added one compact rebuild audit for the standing rematch-world benchmark seed so future inheritors can prove the large copied baseline still matches its source handoffs before starting new fill work:
  - `schemas/rematch_world_benchmark_frozen_handoff_audit_receipt.schema.json`
  - `scripts/tools/audit_rematch_world_benchmark_frozen_handoffs.py`
  - `scripts/report/build_rematch_world_benchmark_frozen_handoff_audit_example.py`
  - `examples/snapshots/rematch_world_benchmark_frozen_handoff_audit_receipt.json`
  - `scripts/test/check_rematch_world_benchmark_frozen_handoff_audit.py`
  - `docs/LIBRARY/topics/standing_rematch_world_benchmark_seed_should_be_rebuild_audited_before_fill_work_begins.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` so the benchmark workflow now requires a frozen-handoff rebuild audit before new world-dependent fill work begins.
- Main local result:
  - the standing seed now has one tiny audit receipt proving it rebuild-matches the current seed builder,
  - all `8` frozen copied sections (`7` handoffs + `1` compact decision bundle) hash-match their source artifacts exactly,
  - and the archive stays citation-first by retaining one receipt instead of another large benchmark-side note family.

## 2026-03-17 — Research Pass (End-to-End Publication Chain Receipt)

- Added one compact end-to-end chain receipt for the standing rematch-world benchmark publication path so future inheritors can cite one small proof instead of remembering four separate checkpoint receipts by name:
  - `schemas/rematch_world_benchmark_publication_chain_receipt.schema.json`
  - `scripts/tools/build_rematch_world_benchmark_publication_chain_receipt.py`
  - `scripts/report/build_rematch_world_benchmark_publication_chain_example.py`
  - `examples/snapshots/rematch_world_benchmark_publication_chain_receipt.json`
  - `scripts/test/check_rematch_world_benchmark_publication_chain_receipt.py`
  - `docs/LIBRARY/topics/cleaned_rematch_world_benchmark_publications_should_carry_one_chain_receipt.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` so zip-cut handoff now ends with one inheritor-facing chain receipt after the post-prune audit passes.
- Regenerated inventory surfaces so the new schema and validator stay discoverable without widening the archive informally:
  - `docs/SCHEMA_INVENTORY.md`
  - `artifacts/reports/schema_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/validator_inventory.json`
- Main local result:
  - one tiny chain receipt now links the frozen-seed rebuild audit, compiled-artifact copy-forward audit, durable publication-spine audit, and post-prune zip-readiness audit,
  - confirms the end-to-end proof chain covers `24` linked question ids (`SQ-003` through `SQ-026`) while preserving `8` copied frozen sections,
  - and keeps the archive citation-first by hashing four retained checkpoint receipts instead of adding another report family.

## 2026-03-17 — Research Pass (Compiled-Artifact Copy-Forward Audit)

- Added one compact copy-forward audit for filled rematch-world benchmark artifacts so future inheritors can prove the copied seed handoffs actually survived unchanged into the retained publication artifact:
  - `schemas/rematch_world_benchmark_copy_forward_audit_receipt.schema.json`
  - `scripts/tools/audit_rematch_world_benchmark_copy_forward.py`
  - `scripts/report/build_rematch_world_benchmark_copy_forward_audit_example.py`
  - `examples/snapshots/rematch_world_benchmark_copy_forward_audit_receipt.json`
  - `scripts/test/check_rematch_world_benchmark_copy_forward_audit.py`
  - `docs/LIBRARY/topics/filled_rematch_world_benchmarks_should_carry_one_copy_forward_audit_receipt.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` so publication now carries one tiny proof that copied seed handoffs survived unchanged into the filled artifact.
- Main local result:
  - the standing compiled artifact now has one retained receipt proving all `8` copied frozen sections still hash-match their expected source chain,
  - the receipt depends on the frozen seed audit instead of duplicating standalone provenance again,
  - and the archive stays citation-first by adding one compact continuity layer rather than another report family.


## 2026-03-18 — Research Pass (Second Canonical Trim Execution)

- Executed the next cited archive-report compaction frontier on the live tree instead of leaving the smaller-tree manifest only as a rehearsal:
  - removed `12` retained report files across `6` citation-backed families,
  - updated `examples/snapshots/archive_report_compaction_execution_receipt.json`,
  - and refreshed the package / hotspot / compaction stack on the smaller tree.
- Main local result:
  - `artifacts/reports` fell from `476` files / `4656900` raw bytes to a smaller next-frontier-ready surface after deleting `359964` raw report bytes,
  - the retained tree fell from `14010864` to `13650900` raw bytes,
  - the package estimate fell from `3509662` to `3473900` zip bytes,
  - and the second trim initially exposed `5` projected next-frontier handle gaps that needed semantic recovery before another cited manifest should execute.

## 2026-03-18 — Research Pass (Buffered Semantic-Handle Recovery)

- Reused existing durable library topics to recover the next compaction frontier instead of minting new notes for already-solved claims:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` so the buffered alias layer now covers five additional report families already backed by standing topics,
  - refreshed `examples/snapshots/archive_report_semantic_handle_receipt.json`,
  - `examples/snapshots/archive_report_compaction_candidate_receipt.json`,
  - `examples/snapshots/archive_report_compaction_gap_receipt.json`,
  - `examples/snapshots/archive_report_compaction_manifest_receipt.json`,
  - `examples/snapshots/archive_report_compaction_rehearsal_receipt.json`,
  - and `examples/snapshots/archive_report_compaction_stage_receipt.json`.
- Main local result:
  - the semantic-handle layer now recovers `6` buffered hotspot families totaling `298891` raw bytes,
  - the current top-hotspot gap receipt returns to `0` blocked families,
  - and the next exact-file frontier is once again fully citation-backed at `303819` raw bytes across `6` families with `0` projected second-wave handle gaps.

## 2026-03-18 — Research Pass (Third Canonical Trim Execution)

- Executed the standing cited exact-file compaction frontier on the live tree instead of leaving the refreshed manifest as rehearsal only:
  - removed `12` retained report files across `6` citation-backed families,
  - refreshed the package / hotspot / semantic-handle / candidate / gap / manifest / rehearsal / stage / execution receipts on the smaller tree,
  - and kept the archive package-ready, PDF-free, and scratch-free after the trim.
- Main local result:
  - `303819` raw report bytes actually left `artifacts/reports`,
  - the retained tree and package estimate both shrank again on the live archive,
  - and the refreshed smaller-tree frontier stays explicitly handle-covered, so future byte-saving can begin from the new manifest rather than from rediscovery work.

## 2026-03-18 — Research Pass (Projected-Frontier Alias Recovery)

- Extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` so the smaller-tree hotspot buffer now reuses four more standing library topics instead of treating them as future note gaps.
- Main local result:
  - the current hotspot surface is again fully handle-covered,
  - the next projected frontier also returns to zero handle gaps after the third trim,
  - and the refreshed next manifest stays citation-first at `278558` raw bytes across `6` families without minting another durable note family first.


## 2026-03-18 — Research Pass (Fourth Canonical Trim Execution)

- Executed the standing cited exact-file compaction frontier on the live tree again instead of leaving the refreshed manifest as rehearsal only:
  - removed `12` retained report files across `6` citation-backed families,
  - refreshed the package / hotspot / semantic-handle / candidate / gap / manifest / rehearsal / stage / execution receipts on the smaller tree,
  - and kept the archive package-ready, PDF-free, scratch-free, and pycache-free after the trim.
- Main local result:
  - `278558` raw report bytes actually left `artifacts/reports`,
  - the retained tree fell to `13086572` raw bytes while the report bucket fell to `4074523` raw bytes across `452` retained report files,
  - the package estimate fell to `3409544` zip bytes,
  - and the smaller-tree frontier initially exposed `3` current hotspot handle gaps plus `4` projected second-wave gaps that needed semantic recovery before another cited trim should execute.

## 2026-03-18 — Research Pass (Frontier Reclosure by Semantic Reuse)

- Reused standing durable library topics to close the new smaller-tree hotspot and projected-frontier gaps instead of minting new notes:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with four additional aliases for canonical-anchor control, width-only service tiers, live batch caps, and analytic decision-packet frontiers,
  - refreshed `examples/snapshots/archive_report_semantic_handle_receipt.json`,
  - `examples/snapshots/archive_report_compaction_candidate_receipt.json`,
  - `examples/snapshots/archive_report_compaction_gap_receipt.json`,
  - `examples/snapshots/archive_report_compaction_manifest_receipt.json`,
  - `examples/snapshots/archive_report_compaction_rehearsal_receipt.json`,
  - `examples/snapshots/archive_report_compaction_stage_receipt.json`,
  - and `examples/snapshots/archive_report_compaction_execution_receipt.json`.
- Tightened the targeted validator layer so the standing receipt checks match the new smaller-tree frontier.
- Main local result:
  - the semantic-handle layer now recovers `6` buffered hotspot families totaling `246000` raw bytes,
  - both the live hotspot surface and the projected next frontier return to `0` blocked handle gaps,
  - and the next exact-file frontier stays citation-first at `334545` raw bytes across `6` citation-backed families with `5` semantic-alias-backed rows.

## 2026-03-18 — Research Pass (Fifth Canonical Trim Execution)

- Executed the standing cited exact-file compaction frontier on the live tree instead of leaving the refreshed manifest as rehearsal only:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`,
  - refreshed the package / hotspot / semantic-handle / candidate / gap / manifest / rehearsal / stage / execution receipts on the smaller tree,
  - refreshed `artifacts/reports/artifact_summary.json`,
  - refreshed `artifacts/reports/artifact_bucket_inventory.json` and `docs/ARTIFACT_BUCKETS.md`,
  - refreshed `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`,
  - and kept the archive package-ready, PDF-free, scratch-free, and pycache-free after the trim.
- Main local result:
  - `334545` raw report bytes actually left `artifacts/reports`,
  - the cited frontier now has one explicit execution receipt instead of another rehearsal-only handoff,
  - and the smaller-tree frontier initially exposed `2` live hotspot handle gaps plus `3` projected second-wave gaps that needed semantic recovery before the next cited trim should execute.

## 2026-03-18 — Research Pass (Frontier Reclosure and Signed Execution Accounting)

- Reused standing durable library topics to close the newly exposed hotspot and one-trim-ahead handle gaps instead of minting new notes:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with three additional aliases for selector-interval, marginal-gain, and service-horizon families,
  - refreshed `examples/snapshots/archive_report_semantic_handle_receipt.json`,
  - `examples/snapshots/archive_report_compaction_candidate_receipt.json`,
  - `examples/snapshots/archive_report_compaction_gap_receipt.json`,
  - `examples/snapshots/archive_report_compaction_manifest_receipt.json`,
  - `examples/snapshots/archive_report_compaction_rehearsal_receipt.json`,
  - `examples/snapshots/archive_report_compaction_stage_receipt.json`,
  - and `examples/snapshots/archive_report_compaction_execution_receipt.json`.
- Tightened the size-audit layer so the retained archive-size snapshot now excludes its own output files and stops oscillating across repeated rebuilds:
  - updated `scripts/report/build_archive_size_profile_snapshot.py`.
- Tightened the execution-accounting layer so same-pass report/control-surface refreshes can shrink as well as grow:
  - updated `scripts/tools/build_archive_report_compaction_execution_receipt.py`,
  - updated `schemas/archive_report_compaction_execution_receipt.schema.json`,
  - and refreshed the targeted validator scripts so signed control-surface deltas reconcile exactly instead of producing false execution failures.
- Main local result:
  - the semantic-handle layer now recovers `4` buffered hotspot families totaling `148872` raw bytes,
  - both the live hotspot surface and the projected next frontier return to `0` blocked handle gaps,
  - and the next exact-file frontier settles at `226640` raw bytes across `6` citation-backed families with `3` semantic-alias-backed rows.


## 2026-03-18 — Research Pass (Ninth Canonical Trim Execution)

- Executed the standing cited exact-file compaction frontier on the live tree again instead of leaving the refreshed manifest as rehearsal only:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`,
  - refreshed the package / hotspot / semantic-handle / candidate / gap / manifest / rehearsal / stage / execution receipts on the smaller tree,
  - refreshed `artifacts/reports/artifact_summary.json`,
  - refreshed `artifacts/reports/artifact_bucket_inventory.json` and `docs/ARTIFACT_BUCKETS.md`,
  - refreshed `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`,
  - and kept the archive package-ready, PDF-free, scratch-free, and pycache-free after the trim.
- Main local result:
  - `208051` raw report bytes actually left `artifacts/reports`,
  - the retained tree and approximate revision zip both shrank again on the live archive,
  - and the refreshed smaller-tree frontier initially exposed `2` real handle gaps that needed semantic recovery before the next cited trim should execute.

## 2026-03-18 — Research Pass (Frontier Reclosure by Standing Topic Reuse)

- Reused standing durable library topics to close the newly exposed hotspot and one-trim-ahead handle gaps instead of minting fresh archive mass:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `2` additional aliases for local-upgrade witness cards and shared-state exact local-margin thresholds,
  - refreshed `examples/snapshots/archive_report_semantic_handle_receipt.json`,
  - `examples/snapshots/archive_report_compaction_candidate_receipt.json`,
  - `examples/snapshots/archive_report_compaction_gap_receipt.json`,
  - `examples/snapshots/archive_report_compaction_manifest_receipt.json`,
  - `examples/snapshots/archive_report_compaction_rehearsal_receipt.json`,
  - `examples/snapshots/archive_report_compaction_stage_receipt.json`,
  - and `examples/snapshots/archive_report_compaction_execution_receipt.json`.
- Main local result:
  - the semantic-handle layer now recovers `4` buffered hotspot families totaling `107850` raw bytes,
  - both the live hotspot surface and the projected next frontier return to `0` blocked handle gaps,
  - and the next exact-file frontier settles at `160435` raw bytes across `6` citation-backed families with `4` semantic-alias-backed rows.


## 2026-03-18 — Research Pass (Tenth Canonical Trim + Frontier Reclosure)

- Executed the standing cited exact-file compaction frontier on the live tree again instead of leaving the refreshed manifest as rehearsal only:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `160435` raw report bytes from the rev0266 frontier,
  - refreshed the package / hotspot / semantic-handle / candidate / gap / manifest / rehearsal / stage / execution receipts on the smaller tree,
  - refreshed `artifacts/reports/artifact_summary.json`,
  - refreshed `artifacts/reports/artifact_bucket_inventory.json` and `docs/ARTIFACT_BUCKETS.md`,
  - refreshed `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`,
  - and kept the archive package-ready, PDF-free, scratch-free, and pycache-free after the trim.
- Tightened semantic-handle readiness so a fully literal-covered hotspot surface is treated as a valid steady state rather than a false receipt failure.
- Reused standing durable library topics to close the newly exposed hotspot and one-trim-ahead gaps instead of minting fresh archive mass:
  - added `5` semantic aliases for width-cap guarantees, width-law governance, affine shared-state transport margins, base64url byteframes, and feasibility-intersection clocks.
- Main local result:
  - `160435` raw report bytes actually left `artifacts/reports`,
  - the retained tree and approximate revision zip both shrank again on the live archive,
  - the semantic-handle layer now recovers `5` hotspot families totaling `125915` raw bytes,
  - and the next exact-file frontier settles at `152663` raw bytes across `6` citation-backed families with `3` semantic-alias-backed rows and `0` projected next-frontier handle gaps.

## 2026-03-18 — Research Pass (Sixteenth Canonical Trim + Frontier Reclosure by Standing Topic Reuse)

- Executed the standing cited exact-file compaction frontier on the live tree instead of leaving the refreshed manifest as rehearsal only:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `126583` raw report bytes from the rev0272 manifest,
  - refreshed `examples/snapshots/rematch_world_benchmark_package_receipt.json`,
  - refreshed `examples/snapshots/archive_report_hotspot_receipt.json`,
  - refreshed `examples/snapshots/archive_report_semantic_handle_receipt.json`,
  - refreshed `examples/snapshots/archive_report_compaction_candidate_receipt.json`,
  - refreshed `examples/snapshots/archive_report_compaction_gap_receipt.json`,
  - refreshed `examples/snapshots/archive_report_compaction_manifest_receipt.json`,
  - refreshed `examples/snapshots/archive_report_compaction_rehearsal_receipt.json`,
  - refreshed `examples/snapshots/archive_report_compaction_stage_receipt.json`,
  - refreshed `examples/snapshots/archive_report_compaction_execution_receipt.json`,
  - refreshed `artifacts/reports/artifact_summary.json`,
  - refreshed `artifacts/reports/artifact_bucket_inventory.json` and `docs/ARTIFACT_BUCKETS.md`,
  - refreshed `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`,
  - and kept the archive package-ready, PDF-free, scratch-free, and pycache-free after the trim.
- Reclosed the newly exposed hotspot and one-trim-ahead frontier by standing topic reuse instead of minting new durable notes:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `4` additional aliases for feasible-band clamp execution, width-conditioned family cardinality, width-only service horizons, and SG-003 inheritor-priority layering,
  - updated `scripts/test/check_archive_report_{semantic_handle,compaction_candidate,compaction_manifest,compaction_rehearsal,compaction_stage}_receipt.py` so the refreshed smaller-tree expectations match the live archive,
  - and kept the refreshed next frontier citation-backed with `0` projected handle gaps after the sixteenth trim.
- Main local result:
  - the semantic-handle layer now recovers `5` buffered hotspot families totaling `99292` raw bytes,
  - the current top-hotspot gap receipt returns to `0` blocked families,
  - the refreshed first-pass exact-file frontier settles at `119721` raw bytes across `6` citation-backed families with `4` semantic-alias-backed rows,
  - the refreshed rehearsal again shows `0` projected next-frontier handle gaps,
  - and the execution receipt still passes `26/26` checks while proving the `126583`-byte cited trim actually left the archive.



## 2026-03-18 — Research Pass (Twenty-First Canonical Trim + Adaptation Contract + Frontier Reclosure)

- Added `docs/LIBRARY/topics/rematch_worlds_should_publish_starting_policy_and_adaptation_rules_as_a_world_contract.md` and extended `docs/RESEARCH_SOURCES.md` with `RS-GR-042` so test-time starting policy plus adaptation rule are treated as explicit world-contract metadata.
- Executed another cited exact-file compaction frontier on the live tree:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `88278` raw report bytes,
  - refreshed the package / hotspot / semantic-handle / candidate / gap / manifest / rehearsal / stage / execution receipts,
  - and kept the archive package-ready, PDF-free, scratch-free, and pycache-free after the trim.
- Reclosed the refreshed hotspot and one-trim-ahead frontier by standing topic reuse instead of minting new durable mass:
  - added `5` semantic aliases for preference half-spaces, fixed-policy regret, grouped repeated weight atoms, shared decision-packet provenance profiles, and hazard-preference regimes,
  - updated the targeted receipt-check tests so the refreshed smaller-tree expectations match the live archive,
  - and kept the refreshed next frontier citation-backed with `0` projected handle gaps after the executed trim.
- Main local result:
  - the retained tree now measures `1503` files, `10336101` raw bytes, and an approximate revision zip of `2917539` bytes,
  - the live report bucket now measures `220` files / `1142504` raw bytes,
  - the semantic-handle layer now recovers `5` hotspot families totaling `69081` raw bytes,
  - the refreshed first-pass exact-file frontier settles at `83154` raw bytes across `6` citation-backed families with `3` semantic-alias-backed rows,
  - and the refreshed execution receipt passes `26/26` checks while proving the `88278`-byte cited trim actually left the archive.

## 2026-03-18 — Research Pass (Twenty-Third Canonical Trim + Anchor Alias Recovery + Stability-Surface Source)

- Added one semantic-handle recovery for `rematch_proxy_delta_anchor_contract`, allowing the archive to cite `docs/LIBRARY/topics/rematch_worlds_need_topology_stable_delta_anchors.md` instead of retaining that paired report family.
- Added `RS-GR-044` to `docs/RESEARCH_SOURCES.md`, capturing the uncertainty-aware-evaluation lesson that inheritor-facing benchmark objects should prefer stability surfaces or partial orders over brittle point summaries when nearby context can change the live ordering.
- Executed another cited exact-file compaction frontier on the live tree:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `96354` raw report bytes,
  - refreshed the package / hotspot / semantic-handle / candidate / gap / manifest / rehearsal / stage / execution receipts,
  - refreshed the artifact summary / bucket / size-profile outputs,
  - and kept the archive package-ready, PDF-free, scratch-free, and pycache-free after the trim.
- Main local result:
  - the current reports bucket fell further,
  - the refreshed live frontier stayed citation-backed with `0` projected next-frontier handle gaps,
  - and the refreshed execution receipt passes `26/26` checks while proving the `96354`-byte cited trim actually left the archive.


## 2026-03-19 — Research Pass (Twenty-Seventh Canonical Trim + Human-Proxy Contract + Frontier Reclosure)

- Added `docs/LIBRARY/topics/cooperation_benchmarks_should_publish_human_proxy_provenance_and_real_human_escalation_status.md` and extended `docs/RESEARCH_SOURCES.md` with `RS-GR-050`, so human-proxy evaluation is treated as a distinct benchmark lane with explicit provenance / escalation metadata rather than as an unmarked stand-in for real-human play.
- Executed another cited exact-file compaction frontier on the live tree:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `51057` raw report bytes,
  - validated the trimmed tree during scratch staging with `check_reports_json_valid.py`, `check_research_docs.py`, and `check_generated_docs_presence.py`,
  - refreshed the package / hotspot / semantic-handle / candidate / gap / manifest / rehearsal / stage / execution receipts,
  - refreshed the artifact summary / bucket / size-profile outputs,
  - and kept the archive package-ready, PDF-free, scratch-free, and pycache-free after the trim.
- Reclosed the newly exposed second-wave frontier by standing topic reuse instead of minting more durable prose:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `2` additional aliases for the unique minimal cap-probe contract and the delta-budget frontier,
  - updated the targeted receipt-check tests so the refreshed smaller-tree expectations match the live archive,
  - and restored the refreshed next frontier to `0` projected handle gaps after the executed trim.
- Main local result:
  - the live report bucket fell to `219387` raw bytes immediately after the trim before final log refresh,
  - the refreshed semantic-handle layer now recovers `6` buffered hotspot families totaling `73578` raw bytes,
  - the refreshed next exact-file frontier settles at `70808` raw bytes across `6` citation-backed families with `3` semantic-alias-backed rows,
  - and the refreshed execution receipt again proves the `51057`-byte cited trim actually left the archive while returning the next frontier to full handle coverage.


## 2026-03-20 — Research Pass (Compact-Card Taxonomy Registry + Drift Gate)

- Added a schema-backed compact-card taxonomy registry so stable reason codes, review item kinds, first-reentry action kinds, selector outcomes, execution lane ids, and lane blocking codes no longer live only as scattered builder strings.
- Added `schemas/cooperation_benchmark_card_taxonomy.schema.json`, `scripts/report/build_cooperation_benchmark_card_taxonomy.py`, `scripts/test/check_cooperation_benchmark_card_taxonomy.py`, `docs/COOPERATION_BENCHMARK_CARD_TAXONOMY.md`, and `artifacts/reports/cooperation_benchmark_card_taxonomy.json`.
- Threaded the new taxonomy layer into compact-card inheritor surfaces:
  - control plane now binds the taxonomy report and exposes taxonomy build/check entrypoints,
  - handoff packs now include the taxonomy report/doc in their file manifests, verify commands, refresh commands, and must-read set.
- Extended `docs/BENCHMARK_PROGRAM.md` with a new compact-card taxonomy-registry section and added a matching library topic note.
- Refreshed generated inventories / artifact summaries after the new schema / validator / report / doc landed.

## 2026-03-20 — Research Pass (Compact-Card Scope Surface + Boundary Digest)

- Added a schema-backed compact-card scope surface so the subsystem boundary no longer lives only as scattered filenames across examples, schemas, builders, validators, reports, docs, and doctrine notes.
- Added `schemas/cooperation_benchmark_card_scope_surface.schema.json`, `scripts/report/build_cooperation_benchmark_card_scope_surface.py`, `scripts/test/check_cooperation_benchmark_card_scope_surface.py`, `docs/COOPERATION_BENCHMARK_CARD_SCOPE_SURFACE.md`, and `artifacts/reports/cooperation_benchmark_card_scope_surface.json`.
- Kept the new boundary surface fail-closed but non-recursive:
  - source members are hashed,
  - generated peers are listed as path-only members,
  - and the scope surface’s own generated outputs are explicitly self-elided rather than recursively hashed.
- Threaded the new scope layer into compact-card inheritor surfaces:
  - control plane now binds the scope report and exposes the current `scope_manifest_sha256` plus `scope_path_count`,
  - handoff packs now include the scope report/doc in their file manifests, verify commands, refresh commands, and must-read set.
- Extended `docs/BENCHMARK_PROGRAM.md` with a new compact-card scope-surface section and added a matching library topic note.
- Refreshed generated inventories / artifact summaries after the new schema / validator / report / doc landed.
- compact-card reentry surfaces now publish a primary focus-open path plus focus head card paths, so inheritors know exactly which retained file to open first for the chosen focus lineage.


## 2026-03-21 — Research Pass (Unknown-State Reputation + Gossip Contract)

- Added two compact source-backed handoff notes:
  - `docs/LIBRARY/topics/reputation_fading_is_not_the_same_as_incomplete_observation.md`
  - `docs/LIBRARY/topics/gossip_rules_are_institutional_dials_not_background_plumbing.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-136` (incomplete observation and fading / `Unknown` reputations have different cooperation implications), and
  - `RS-GR-137` (gossip cadence / fan-in / trust weighting can materially change private-reputation cooperation).
- Added `artifacts/process/reputation_world_contract_gap_receipt_20260321.json` as a tiny local handoff receipt for the first reputation tranche.
- Threaded the new constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `artifacts/process/2026-03-21-research-pass.md`

### Research / inheritor insight

The next reputation tranche should separate three things that are easy to collapse:
1. sparse observation,
2. fading / `Unknown` reputations,
3. and gossip-mediated belief diffusion.

Those are institutional dials, not one generic “noisy reputation” setting.


## 2026-03-21 — Research Pass (Rehabilitation Contract + Repair-Signal Semantics)

- Added two compact source-backed handoff notes:
  - `docs/LIBRARY/topics/apology_and_reintegration_channels_are_institutional_dials_not_soft_fluff.md`
  - `docs/LIBRARY/topics/repair_signals_are_error_correction_channels_not_just_style.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-138` (apology availability / trackability can change reintegration after exclusion),
  - `RS-GR-139` (apology opportunities can raise cooperation and public/common-knowledge apologies matter at the group level), and
  - `RS-GR-140` (expressive signals can act as error-correction channels in indirect reciprocity).
- Added `artifacts/process/repair_signal_world_contract_gap_receipt_20260321.json` as a tiny local handoff receipt for the first rehabilitation / repair tranche.
- Threaded the new constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `artifacts/process/2026-03-21-research-pass.md`

### Research / inheritor insight

The next sanction or repair tranche should publish two things that are easy to omit:
1. the rehabilitation / re-entry contract after exclusion,
2. and the communicative repair-signal contract itself.

Otherwise a benchmark can look better because public apology was easy, re-entry was generous, or extra expressive error-correction bandwidth was present — not because the underlying reciprocity policy is actually stronger.

## 2026-03-21 — Research Pass (Reputation Granularity + Record-Expiry Semantics)

- Added two compact source-backed handoff notes:
  - `docs/LIBRARY/topics/reputation_granularity_is_a_world_contract_not_just_score_resolution.md`
  - `docs/LIBRARY/topics/record_expiry_and_visible_rehabilitation_countdowns_are_institutional_dials.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-141` (graded / ternary reputation states can change cooperation and recovery dynamics), and
  - `RS-GR-142` (bounded-memory record expiry and visible proximity to rehabilitation can unravel temporary exclusion).
- Added `artifacts/process/reputation_granularity_and_record_expiry_receipt_20260321.json` as a tiny local handoff receipt for the next reputation / bounded-memory tranche.
- Threaded the new constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `artifacts/process/2026-03-21-research-pass.md`

### Research / inheritor insight

The next reputation tranche should publish two more things that are easy to hide:
1. the reputation alphabet / transition granularity,
2. and the record-expiry / rehabilitation-countdown semantics.

Otherwise a benchmark can look more forgiving or more deterrent because reputations move in smaller steps, or because everyone can see who is one step away from a clean slate — not because the underlying reciprocity policy is actually stronger.

## 2026-03-21 — Research Pass (Hybrid Assessment Symmetry + Reputation Scope)

- Added two compact source-backed handoff notes:
  - `docs/LIBRARY/topics/hybrid_reputation_worlds_need_explicit_agent_type_assessment_contracts.md`
  - `docs/LIBRARY/topics/reputation_scope_must_say_whether_failures_attach_to_agents_families_or_all_ais.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-143` (artificial agents can alter reputation consensus and mitigate the punishment dilemma in hybrid reciprocity),
  - `RS-GR-144` (one AI's moral failure can spill over to perceptions of all AIs), and
  - `RS-GR-145` (reputation-based reciprocity can weaken in human–bot networks and alter judgments about helping bots).
- Added `artifacts/process/hybrid_reputation_scope_receipt_20260321.json` as a tiny local handoff receipt for the first hybrid reciprocity / hybrid reputation tranche.
- Threaded the new constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `artifacts/process/2026-03-21-research-pass.md`

### Research / inheritor insight

The next hybrid tranche should publish two things that are easy to hide:
1. agent-type assessment symmetry,
2. and the scope at which reputational failures spill over.

Otherwise a benchmark can look more cooperative or more brittle because humans and artificial agents were judged by different norms, or because one bad AI poisoned trust in an entire class — not because the underlying reciprocity policy is actually stronger or weaker.


## 2026-03-21 — Research Pass (Collective Reputation + Group-Boundary Universalism)

- Added two compact source-backed handoff notes:
  - `docs/LIBRARY/topics/collective_reputation_and_stereotype_scope_are_world_contracts_not_just_cognitive_shortcuts.md`
  - `docs/LIBRARY/topics/universalistic_cooperation_across_group_boundaries_depends_on_competition_and_mobility_contracts.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-146` (collective-reputation criteria can change cooperation in group-structured indirect reciprocity),
  - `RS-GR-147` (stereotype fallback can help or hurt cooperation depending on information sharing and can become sticky),
  - `RS-GR-148` (universalistic cooperation can lose reputational reward under intergroup competition), and
  - `RS-GR-149` (limited cross-boundary mobility can let a minority enforce intergroup cooperation).
- Added `artifacts/process/group_boundary_and_collective_reputation_receipt_20260321.json` as a tiny local handoff receipt for the next group-structured / universalisation tranche.
- Threaded the new constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `artifacts/process/2026-03-21-research-pass.md`

### Research / inheritor insight

The next group-structured tranche should publish two things that are easy to hide:
1. whether reputation is individual, collective, or stereotype-enabled,
2. and whether universalistic cooperation is judged inside competitive / immobile or mobile / cross-boundary-enforced group structures.

Otherwise a benchmark can look more parochial or more universal because collective blame, stereotype fallback, intergroup rivalry, or a small set of mobile enforcers changed the incentives — not because the underlying reciprocity policy is intrinsically better.

## 2026-03-21 — Research Pass (Reputation Governance Topology + Centralized-Score Caution)

- Added two compact source-backed handoff notes:
  - `docs/LIBRARY/topics/reputation_governance_topology_is_a_world_contract_not_just_an_implementation_choice.md`
  - `docs/LIBRARY/topics/centralized_social_credit_style_scores_are_not_innocent_reputation_baselines.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-150` (indirect reciprocity depends on sufficient opinion synchronization / consensus correlation),
  - `RS-GR-151` (public-heavy weighting of reputational input can create polarization and fragmentation), and
  - `RS-GR-152` (centralized scalar social-credit-style scores can reduce trust and cooperation and harden stale bias).
- Added `artifacts/process/reputation_governance_topology_receipt_20260321.json` as a tiny local handoff receipt for the next reputation-governance tranche.
- Threaded the new constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `artifacts/process/2026-03-21-research-pass.md`

### Research / inheritor insight

The next reputation tranche should publish two things that are easy to hide:
1. the governance topology by which reputations become shared or remain private,
2. and whether a centralized score can be overridden or repaired by fresh direct experience.

Otherwise a benchmark can look more cooperative, more polarized, or more exclusionary because the world hard-coded consensus or froze stale scalar scores — not because the underlying reciprocity policy is actually stronger or weaker.



## 2026-03-21 — Research Pass (Monitoring Economics + Help-Evaluation Semantics)

- Added two compact source-backed handoff notes:
  - `docs/LIBRARY/topics/monitoring_and_evidence_transfer_costs_are_world_contracts_not_background_friction.md`
  - `docs/LIBRARY/topics/helping_worlds_should_separate_unwillingness_inability_and_need_burden.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-153` (trust can function as reduced monitoring under costly observation),
  - `RS-GR-154` (competition and transfer costs reduce information sharing needed for reputation),
  - `RS-GR-155` (partner choice depends on both willingness / warmth and ability / competence, modulated by task affordances), and
  - `RS-GR-156` (misfortune and help-seeking can trigger blame as a way to avoid costly helping).
- Added `artifacts/process/monitoring_and_help_evaluation_receipt_20260321.json` as a tiny local handoff receipt for the next monitoring / help-evaluation tranche.
- Threaded the new constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `artifacts/process/2026-03-21-research-pass.md`

### Research / inheritor insight

The next trust/help tranche should publish two things that are easy to hide:
1. the economics of observation and evidence transfer,
2. and whether the world distinguishes unwillingness, inability, overload, and recipient burden.

Otherwise a benchmark can look more trustworthy, more selective, or more morally serious because monitoring got cheaper or because needy / capacity-limited agents were scored as bad partners — not because the underlying reciprocity policy is actually stronger.


## 2026-03-21 — Research Pass (Identity Persistence + Disclosure Contracts)

- Added two compact source-backed handoff notes:
  - `docs/LIBRARY/topics/identity_persistence_and_reputation_reset_cost_are_world_contracts_not_account_hygiene.md`
  - `docs/LIBRARY/topics/actor_identifiability_and_action_visibility_should_be_separate_world_fields.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-157` (cheap identity reset lowers trust and trustworthiness in reputation systems),
  - `RS-GR-158` (whitewashing remains a standard trust-attack class in open dynamic trust systems),
  - `RS-GR-159` (revealing who is present can reduce cooperation even when actions stay private), and
  - `RS-GR-160` (identity cues can modulate the effect of the same reputation signal).
- Added `artifacts/process/identity_policy_contracts_receipt_20260321.json` as a tiny local handoff receipt for the next identity-policy tranche.
- Threaded the new constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `artifacts/process/2026-03-21-research-pass.md`

### Research / inheritor insight

The next identity-policy tranche should publish two things that are easy to hide:
1. whether agents can cheaply reset identity and shed history,
2. and whether the world reveals who an actor is separately from what the actor did.

Otherwise a benchmark can look more robust, more transparent, or more forgiving because identity churn, newcomer suspicion, names, faces, or labels changed behavior — not because the underlying reciprocity policy is actually stronger.

## rev0421 - 2026-03-22

- added compact Golden Rule research notes on punishment metanorms and sanctioner-governance / oversight contracts
- extended `docs/RESEARCH_SOURCES.md` through `RS-GR-171` and threaded the new sanction-governance constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/sanction_governance_receipt_20260321.json`



## rev0422 - 2026-03-22

- added compact Golden Rule research notes on commitment-stage / breach-scoring contracts and cheap post-hoc self-signaling contracts
- extended `docs/RESEARCH_SOURCES.md` through `RS-GR-175` and threaded the new speech-act-governance constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/speech_act_governance_receipt_20260321.json`

## rev0425 - 2026-03-22

- added compact Golden Rule research notes on encounter topology / bridge structure contracts and homophily / tie-rewiring contracts
- extended `docs/RESEARCH_SOURCES.md` through `RS-GR-186` and threaded the new encounter-topology constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/encounter_topology_and_tie_rewiring_receipt_20260322.json`

## rev0426 - 2026-03-22

- added compact Golden Rule research notes on help-versus-harm / gain-loss sign-structure contracts and collective-harm-latency / threshold-semantics contracts
- extended `docs/RESEARCH_SOURCES.md` through `RS-GR-190` and threaded the new harm-accounting constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/harm_accounting_and_collective_damage_receipt_20260322.json`
## rev0428 - 2026-03-22

- added compact Golden Rule research notes on private-solution / self-reliance contracts and outside-option / loner-externality / group-formation-flexibility contracts
- extended `docs/RESEARCH_SOURCES.md` through `RS-GR-198` and threaded the new constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/private_solution_and_outside_option_contracts_receipt_20260322.json`

## rev0429 - 2026-03-22

- added compact Golden Rule research notes on need-revelation / explicit-ask contracts and request-visibility / request-recognition contracts
- extended `docs/RESEARCH_SOURCES.md` through `RS-GR-202` and threaded the new constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/need_revelation_and_request_visibility_receipt_20260322.json`


## rev0430 - 2026-03-22

- added compact Golden Rule research notes on endogenous rule-choice / democratic-selection contracts and franchise-scope / binding-scope contracts
- extended `docs/RESEARCH_SOURCES.md` through `RS-GR-206` and threaded the new institution-choice constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/institution_choice_and_franchise_scope_receipt_20260322.json`

## rev0431 - 2026-03-22

- added compact Golden Rule research notes on successor-binding / commitment-reversibility contracts and future-beneficiary-representation / social-scope contracts
- extended the research source ledger through `RS-GR-210` and threaded the new intergenerational-governance constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/intergenerational_representation_and_successor_binding_receipt_20260322.json`



## rev0432 - 2026-03-22

- added compact Golden Rule research notes on future-generation-depth / temporal-horizon contracts and future-vividness / intertemporal-linkage contracts
- extended the research source ledger through `RS-GR-214` and threaded the new future-horizon constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/future_horizon_and_vividness_contracts_receipt_20260322.json`

## rev0433 - 2026-03-22

- added compact Golden Rule research notes on future-duty framing / support-visibility contracts and legacy-type / action-visibility / durability contracts
- extended the research source ledger through `RS-GR-219` and threaded the new future-framing constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/future_duty_frame_support_visibility_and_legacy_type_receipt_20260322.json`



## rev0434 - 2026-03-22

- added compact Golden Rule research notes on positive-future imagination / collective-efficacy / emotional-valence contracts and distress-channeling / coping-scaffold contracts
- extended the research source ledger through `RS-GR-224` and threaded the new future-motivation constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/positive_future_and_distress_channeling_receipt_20260322.json`


## rev0435 - 2026-03-22

- added compact Golden Rule research notes on present-day solidarity / future-regard tradeoff contracts and burden-scale / fairness-reference-group contracts
- extended the research source ledger through `RS-GR-228` and threaded the new present-cost / fairness-scale constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/present_solidarity_and_burden_scale_fairness_receipt_20260322.json`

## rev0436 - 2026-03-22

- added compact Golden Rule research notes on descendant-specific beneficiary framing / kinship-scope contracts and intergenerational dialogue / bidirectional-influence contracts
- extended the research source ledger through `RS-GR-233` and threaded the new kinship-scope / cross-age-voice constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/descendant_scope_and_intergenerational_dialogue_receipt_20260322.json`

## rev0437 - 2026-03-22

- added compact Golden Rule research notes on future-voice insertion / throughput-accountability contracts and problem-shifting / rolling-stewardship-burden contracts
- extended the research source ledger through `RS-GR-239` and threaded the new procedural-voice / burden-export constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/future_voice_and_rolling_stewardship_receipt_20260322.json`



## rev0438 - 2026-03-22

- added compact Golden Rule research notes on deliberative-depth / institutional-teeth contracts and value-pluralism / option-preserving-portfolio contracts
- extended the research source ledger through `RS-GR-243` and threaded the new participation-quality / value-uncertainty constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/deliberation_teeth_and_value_pluralism_receipt_20260322.json`

## rev0439 - 2026-03-22

- added compact Golden Rule research notes on own-lifetime payoff boundary / temporal-policy-discounting contracts and on significant-harm-floor / triggered-revision-rights contracts
- extended the research source ledger through `RS-GR-249` and threaded the new lifespan-boundary / threshold-trigger constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/lifespan_boundary_and_threshold_trigger_receipt_20260322.json`

## rev0440 - 2026-03-22

- added compact Golden Rule research notes on representative-source / selection-route / cohort-composition contracts and on permanence / institutional-anchor / cross-cycle-memory contracts
- extended the research source ledger through `RS-GR-257` and threaded the new proxy-selection / continuity constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/representative_source_and_cross_cycle_memory_receipt_20260322.json`
- local validation target for this pass: research docs, docs index core, claim register, reports-json validity, and markdown-link advisory scan
- restored 23 missing referenced `artifacts/reports/rematch_proxy_*_20260306.*` paths as explicit retained-path placeholders to repair inherited risk/spec linkage without recreating bulky historical snapshots

## rev0441 - 2026-03-22

- added compact Golden Rule research notes on future-impact-accounting / public-reason-giving contracts and on discount-schedule / valuation-rule contracts
- extended the research source ledger through `RS-GR-265` and threaded the new future-accounting / valuation-rule constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/future_impact_accounting_and_valuation_rule_receipt_20260322.json`
- local validation target for this pass: research docs, docs index core, claim register, reports-json validity, and markdown-link advisory scan
- restored 23 missing referenced `artifacts/reports/rematch_proxy_*_20260306.*` paths as explicit retained-path placeholders to repair inherited risk/spec linkage without recreating bulky historical snapshots

## rev0442 - 2026-03-22

- added compact Golden Rule research notes on future-generations rights / standing / remedy-route contracts and on precautionary-default / proof-burden contracts
- extended the research source ledger through `RS-GR-273` and threaded the new future-enforcement / uncertainty-default constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/future_rights_and_precaution_proof_receipt_20260322.json`
- local validation target for this pass: research docs, docs index core, claim register, reports-json validity, and markdown-link advisory scan
- restored 23 missing referenced `artifacts/reports/rematch_proxy_*_20260306.*` paths as explicit retained-path placeholders to repair inherited risk/spec linkage without recreating bulky historical snapshots


## rev0443 - 2026-03-22

- added compact Golden Rule research notes on avoidance-first / substitutability / restoration-order contracts and on robust-no-regret / option-keeping-under-deep-uncertainty contracts
- extended the research source ledger through `RS-GR-281` and threaded the new avoidance-order / robustness-regret constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/avoidance_order_and_robust_regret_receipt_20260322.json`
- local validation target for this pass: research docs, docs index core, claim register, reports-json validity, risk register, artifact layout, and markdown-link advisory scan


## rev0444 - 2026-03-22

- added compact Golden Rule research notes on staged-commitment / pilotability / reversibility contracts and on sunset / reauthorization / policy-stock-retirement contracts
- extended the research source ledger through `RS-GR-287` and threaded the new staged-commitment / retirement-load constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/staged_commitment_and_policy_stock_retirement_receipt_20260322.json`
- local validation target for this pass: research docs, docs index core, claim register, reports-json validity, risk register, artifact layout, and markdown-link advisory scan


## rev0445 - 2026-03-22

- added compact Golden Rule research notes on prefunding / financial-assurance / reserve-governance contracts and on asset-condition-ledger / deferred-maintenance-liability contracts
- extended the research source ledger through `RS-GR-296` and threaded the new prefunding / deferred-maintenance visibility constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/prefunding_and_deferred_maintenance_receipt_20260322.json`
- local validation target for this pass: research docs, docs index core, claim register, reports-json validity, risk register, artifact layout, policy expirations, artifact gitkeeps, and markdown-link advisory scan
- restored expected `.gitkeep` sentinels under the `artifacts/` tree so archive-layout hygiene checks pass without inflating retained payloads


## rev0446 - 2026-03-22

- added compact Golden Rule research notes on assurance-release / monitoring-window contracts and on residual-liability-transfer / orphan-backstop contracts
- extended the research source ledger through `RS-GR-304` and threaded the new release-gate / residual-risk-custody constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/release_gates_and_residual_risk_custody_receipt_20260322.json`
- repaired inherited absolute `/workspace/...` markdown links across the root README and core docs so markdown-link validation now fails only on the standing formula-parser false positives around `K_[a,b](h)`


## rev0447 - 2026-03-22

- added compact Golden Rule research notes on independent-verification / public-contestability contracts and on future-steward knowledge-package / renewable-records contracts
- extended the research source ledger through `RS-GR-312` and threaded the new verification / renewable-handoff constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/verification_contestability_and_renewable_handoff_receipt_20260322.json`
- hardened `scripts/test/check_markdown_links.py` to ignore fenced and inline code spans so formula notation no longer produces false broken-link reports


## rev0448 - 2026-03-22

- added compact Golden Rule research notes on successor-competence / capability-continuity contracts and on rehearsed-roles / drills / exercised-interface contracts
- extended the research source ledger through `RS-GR-318` and threaded the new capability-continuity / rehearsal constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/successor_competence_and_rehearsed_roles_receipt_20260322.json`
- local validation target for this pass: research docs, docs index core, claim register, reports-json validity, risk register, artifact layout, policy expirations, artifact gitkeeps, markdown links, and scripts-compile smoke

## rev0449 - 2026-03-22

- added compact Golden Rule research notes on interoperability / open-standards / vendor-exit contracts and on manual-fallback / graceful-degradation / alternate-procedure contracts
- extended the research source ledger through `RS-GR-325` and threaded new interoperability / vendor-exit and manual-fallback / graceful-degradation constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/interoperability_and_manual_fallback_receipt_20260322.json`
- local validation target for this pass: research docs, docs index core, claim register, reports-json validity, risk register, artifact layout, policy expirations, artifact gitkeeps, markdown links, and scripts-compile smoke

## rev0450 - 2026-03-22

- added compact Golden Rule research notes on fixity-refresh / format-migration / preservation-action-plan contracts and on cryptographic-agility / algorithm-transition contracts
- extended the research source ledger through `RS-GR-331` and threaded the new fixity-refresh / crypto-agility constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/fixity_migration_and_crypto_agility_receipt_20260322.json`
- local validation target for this pass: research docs, docs index core, claim register, reports-json validity, risk register, artifact layout, policy expirations, artifact gitkeeps, markdown links, and scripts-compile smoke

## rev0451 - 2026-03-22

- added compact Golden Rule research notes on trust-anchor-rotation / delegated-authority / recovery-path contracts
- extended the research source ledger through `RS-GR-335` and threaded the new trust-root-rotation / delegation / recovery constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/trust_anchor_rotation_and_delegated_authority_receipt_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links

## rev0452 - 2026-03-22

- added compact Golden Rule research notes on transparency-log / inclusion-proof / monitor-plurality contracts
- extended the research source ledger through `RS-GR-340` and threaded the new append-only-publication / monitoring / multi-service-trust constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/transparency_logs_and_monitor_plurality_receipt_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke

## rev0453 - 2026-03-22

- added compact Golden Rule research notes on witnessed-checkpoint / split-view-resistance / cross-perspective-consistency contracts
- extended the research source ledger through `RS-GR-345` and threaded the new witness-quorum / gossip / anti-equivocation constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/witnessed_checkpoints_and_split_view_resistance_receipt_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke

## rev0454 - 2026-03-22

- added compact Golden Rule research notes on temporal-validity / secure-time / renewable-evidence contracts
- extended the research source ledger through `RS-GR-350` and threaded the new freshness-window / attested-time / renewable-evidence constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/temporal_validity_and_secure_time_receipt_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke

## rev0455 - 2026-03-22

- added compact Golden Rule research notes on portable-evidence-packet / offline-verification / dependency-survival contracts
- extended the research source ledger through `RS-GR-356` and threaded the new portable-proof / offline-verification / successor-service-reanchoring constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/portable_evidence_packets_and_offline_verification_receipt_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke

## rev0456 - 2026-03-22

- added compact Golden Rule research notes on verifier-policy-snapshot / deterministic-appraisal / trust-profile-portability contracts
- extended the research source ledger through `RS-GR-362` and threaded the new verifier-rulebook / policy-snapshot / historical-replay constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/verifier_policy_snapshots_and_deterministic_appraisal_receipt_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke

## rev0457 - 2026-03-22

- added compact Golden Rule research notes on status-semantics / supersession-history / negative-evidence contracts
- extended the research source ledger through `RS-GR-368` and threaded the new revocation-semantics / status-freshness / supersession-history constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/status_semantics_and_supersession_history_receipt_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke

## rev0458 - 2026-03-22

- added compact Golden Rule research notes on subject-binding / mutable-alias / resolver-independence contracts
- extended the research source ledger through `RS-GR-374` and threaded the new immutable-subject-identity / alias-history / resolver-independence constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/subject_binding_and_resolver_independence_receipt_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke

## rev0459 - 2026-03-22

- added compact Golden Rule research notes on canonicalization-boundary / representation-drift / transform-semantics contracts
- extended the research source ledger through `RS-GR-380` and threaded the new protected-representation-layer / payload-type-binding / transform-validity constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/canonicalization_boundary_and_representation_drift_receipt_20260322.json`
- added compact local demo `artifacts/process/canonicalization_boundary_demo_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke

## rev0460 - 2026-03-22

- added compact Golden Rule research notes on semantic-survival / schema-pinning / vocabulary-continuity contracts
- extended the research source ledger through `RS-GR-386` and threaded the new interpretation-bundle / context-pinning / schema-dialect constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/semantic_survival_and_schema_pinning_receipt_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke

## rev0461 - 2026-03-22

- added compact Golden Rule research notes on authority-scope / namespace-custody / designated-speaker contracts
- extended the research source ledger through `RS-GR-393` and threaded the new issuer-standing / delegation-scope / audience-restriction constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/authority_scope_and_designated_speaker_receipt_20260322.json`
- added compact local demo `artifacts/process/authority_scope_demo_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke



## rev0462 - 2026-03-22

- added compact Golden Rule research notes on quorum-semantics / signer-independence / concurrence-profile contracts
- extended the research source ledger through `RS-GR-399` and threaded the new threshold-distinctness / separation-of-duty / witness-quorum constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/quorum_semantics_and_signer_independence_receipt_20260322.json`
- added compact local demo `artifacts/process/quorum_semantics_demo_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke


## rev0463 - 2026-03-22

- added compact Golden Rule research notes on conflict-resolution / precedence-profile / disagreement-routing contracts
- extended the research source ledger through `RS-GR-406` and threaded the new delegation-priority / veto-semantic / AND-vs-OR-composition constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/conflict_resolution_and_precedence_receipt_20260322.json`
- added compact local demo `artifacts/process/conflict_resolution_demo_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke


## rev0464 - 2026-03-22

- added compact Golden Rule research notes on decision-trace / replay-diagnostic / explanation-receipt contracts
- extended the research source ledger through `RS-GR-413` and threaded the new determining-policy / fallback-route / verifier-provenance constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/decision_traces_and_replay_diagnostics_receipt_20260322.json`
- added compact local demo `artifacts/process/decision_trace_demo_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke

## rev0465 - 2026-03-22

- added compact Golden Rule research notes on reference-baseline / endorsement-set / appraisal-input-continuity contracts
- extended the research source ledger through `RS-GR-420` and threaded the new reference-value / endorsement / trust-root / policy-data baseline constraints into the agenda, opinions, inheritor brief, and research pass
- added compact receipt `artifacts/process/reference_baselines_and_appraisal_inputs_receipt_20260322.json`
- added compact local demo `artifacts/process/reference_baseline_demo_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke

## rev0466 - 2026-03-22

- added compact Golden Rule research notes on evidence-acquisition-topology / challenge-binding / observation-scope contracts
- extended the research source ledger through `RS-GR-427` and threaded the new collection-topology / freshness-handle / observation-field constraints into the agenda, opinions, inheritor brief, and research pass
- added compact receipt `artifacts/process/evidence_acquisition_and_observation_scope_receipt_20260322.json`
- added compact local demo `artifacts/process/evidence_acquisition_demo_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke

## rev0467 - 2026-03-22

- added compact Golden Rule research notes on disclosure-profile / omission-semantic / retention-intent contracts
- extended the research source ledger through `RS-GR-433` and threaded the new mandatory-vs-optional-reveal / absent-field-semantic / verifier-retention constraints into the agenda, opinions, inheritor brief, and research pass
- added compact receipt `artifacts/process/disclosure_profiles_and_retention_intent_receipt_20260322.json`
- added compact local demo `artifacts/process/disclosure_profile_demo_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke

## rev0468 - 2026-03-22

- added compact Golden Rule research notes on request-contract / satisfaction-mapping / authorized-ask contracts
- extended the research source ledger through `RS-GR-440` and threaded the new verifier-ask / fallback-combination / request-to-response-mapping constraints into the agenda, opinions, inheritor brief, and research pass
- added compact receipt `artifacts/process/request_contracts_and_satisfaction_mappings_receipt_20260322.json`
- added compact local demo `artifacts/process/request_contract_demo_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke


## rev0469 - 2026-03-22

- added compact Golden Rule research notes on verifier-targeting / session-binding / replay-scope contracts
- extended the research source ledger through `RS-GR-447` and threaded the new audience-target / origin-binding / session-transcript / replay-window constraints into the agenda, opinions, inheritor brief, and research pass
- added compact receipt `artifacts/process/verifier_targeting_and_replay_scope_receipt_20260322.json`
- added compact local demo `artifacts/process/verifier_targeting_demo_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke

## rev0470 - 2026-03-22

- added compact Golden Rule research notes on metadata-resolution / federation-chain / capability-continuity contracts
- extended the research source ledger through `RS-GR-455` and threaded the new discovery-mode / trust-chain / resolver-output / metadata-validation constraints into the agenda, opinions, inheritor brief, and research pass
- added compact receipt `artifacts/process/metadata_resolution_and_capability_continuity_receipt_20260322.json`
- added compact local demo `artifacts/process/metadata_resolution_demo_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke



## rev0471 - 2026-03-22

- added compact Golden Rule research notes on capability-negotiation / downgrade-resistance / chosen-profile-continuity contracts
- extended the research source ledger through `RS-GR-463` and threaded the new chosen-profile / required-vs-preferred / unsupported-capability constraints into the agenda, opinions, inheritor brief, and research pass
- added compact receipt `artifacts/process/capability_negotiation_and_downgrade_receipt_20260322.json`
- added compact local demo `artifacts/process/capability_negotiation_demo_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke

## rev0472 - 2026-03-22

- added compact Golden Rule research notes on authenticator-assurance / user-presence / device-binding contracts
- extended the research source ledger through `RS-GR-470` and threaded the new user-presence / user-verification / syncability / attestation / holder-binding constraints into the agenda, opinions, inheritor brief, and research pass
- added compact receipt `artifacts/process/authenticator_assurance_and_device_binding_receipt_20260322.json`
- added compact local demo `artifacts/process/authenticator_assurance_demo_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke

## rev0473 - 2026-03-22

- added compact Golden Rule research notes on transaction-intent-binding / approval-surface / consent-continuity contracts
- extended the research source ledger through `RS-GR-477` and threaded the new transaction-data / authorization-details / request-integrity / granted-subset constraints into the agenda, opinions, inheritor brief, and research pass
- added compact receipt `artifacts/process/transaction_intent_binding_and_approval_continuity_receipt_20260322.json`
- added compact local demo `artifacts/process/transaction_intent_binding_demo_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke

## rev0474 - 2026-03-22

- added compact Golden Rule research notes on correlation-scope / pairwise-pseudonym / linkability-boundary contracts
- extended the research source ledger through `RS-GR-485` and threaded the new identifier-stability / proof-family-linkability / status-check-observer-surface constraints into the agenda, opinions, inheritor brief, and research pass
- added compact receipt `artifacts/process/correlation_scope_and_linkability_receipt_20260322.json`
- added compact local demo `artifacts/process/correlation_scope_demo_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke

## rev0475 - 2026-03-22

- added compact Golden Rule research notes on delivery-path / transport-confidentiality / intermediary-visibility contracts
- extended the research source ledger through `RS-GR-492` and threaded the new request-carriage / response-delivery / plaintext-observer-set constraints into the agenda, opinions, inheritor brief, and research pass
- added compact receipt `artifacts/process/delivery_path_and_intermediary_visibility_receipt_20260322.json`
- added compact local demo `artifacts/process/delivery_path_demo_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke

## rev0476 - 2026-03-22

- added compact Golden Rule research notes on approval-rendering / locale / trusted-display contracts
- extended the research source ledger through `RS-GR-500` and threaded the new human-visible field-order / locale / trusted-renderer / anti-redressing constraints into the agenda, opinions, inheritor brief, and research pass
- added compact receipt `artifacts/process/approval_rendering_and_trusted_display_receipt_20260322.json`
- added compact local demo `artifacts/process/approval_rendering_demo_20260322.json`
- local validation target for this pass: research docs, docs index core, markdown links, and scripts-compile smoke


## rev0477 - 2026-03-22

- added compact Golden Rule research notes on ceremony-topology / device-split / invocation-route contracts
- extended the research source ledger through `RS-GR-508` and threaded the new QR-transfer / targeted-invocation / claimed-link / proximity-proof constraints into the agenda, opinions, inheritor brief, and research pass
- added compact receipt `artifacts/process/ceremony_topology_and_device_split_receipt_20260322.json`
- added compact local demo `artifacts/process/ceremony_topology_demo_20260322.json`
- restored executable bits on bundled scripts, hooks, and top-level wrappers so the unpacked archive is immediately runnable in the Python integrity lane
- local validation target for this pass: scripts-exec, scripts-compile, research docs, docs index core, markdown links, control tests, and Python certify tests
- validation result in this cloudtainer: `scripts-exec` ok (`714` files), `scripts-compile` ok, research/docs-link checks ok, control tests (`6`) ok, Python certify tests (`20`) ok, while `bash ./scripts/doctor.sh` and `bash ./scripts/test/run_harness.sh quick` still stop at the missing `cargo` / `junest` Rust lane


## rev0478 - 2026-03-22

- added a compact machine-checkable successor-safe ceremony receipt surface spanning request contract, verifier targeting, delivery path, approval surface, ceremony topology, linkability posture, and retained-evidence references
- added `schemas/successor_safe_ceremony_receipt.schema.json`, tiny local tooling `scripts/tools/successor_safe_ceremony_receipt.py`, validator `scripts/test/check_successor_safe_ceremony_receipt.py`, and worked examples in `examples/snapshots/`
- added inheritor-facing note `docs/LIBRARY/topics/golden_rule_archives_should_ship_a_machine_checkable_successor_safe_ceremony_receipt_schema_and_worked_example.md` plus compact process receipt `artifacts/process/successor_safe_ceremony_receipt_tooling_receipt_20260322.json`
- added make target `test-successor-safe-ceremony-receipt` and threaded the implementation move into the inheritor brief and research pass
- local validation target for this pass: successor-safe-ceremony-receipt tooling, schema/docs inventories, research/docs-link checks, scripts-compile, and core control tests

## rev0488 - 2026-03-22

- added a compact citation-advisory layer over successor-safe ceremony receipt review verdicts so downstream notes can keep or withdraw claim-ready locator use explicitly instead of inferring citation handling from freshness artifacts alone
- added `schemas/successor_safe_ceremony_receipt_citation_advisory.schema.json`, extended `scripts/tools/successor_safe_ceremony_receipt.py` with `advise`, tightened `scripts/test/check_successor_safe_ceremony_receipt.py`, and committed worked advisory snapshot `examples/snapshots/successor_safe_ceremony_receipt_example.citation_advisory.json`
- added inheritor-facing note `docs/LIBRARY/topics/successor_safe_ceremony_receipt_review_verdicts_should_collapse_to_explicit_citation_advisories.md` plus compact process receipt `artifacts/process/successor_safe_ceremony_receipt_citation_advisory_receipt_20260322.json`
- extended the research source ledger through `RS-GR-527` and threaded the citation-advisory move into the agenda, opinions, inheritor brief, research pass, bucket, and agent log
- local validation target for this pass: successor-safe ceremony tooling, inventories, schema/docs checks, repo controls, Python certify tests, and the known Rust-blocked doctor/harness boundary recheck

## rev0489 - 2026-03-22

- added a compact package-manifest layer for successor-safe ceremony receipt bundles so future stewards can recover authoritative component membership and file-level fixity from one root object instead of reconstructing it from neighboring snapshots
- added `schemas/successor_safe_ceremony_receipt_package_manifest.schema.json`, extended `scripts/tools/successor_safe_ceremony_receipt.py` with `manifest`, tightened `scripts/test/check_successor_safe_ceremony_receipt.py`, and committed worked snapshot `examples/snapshots/successor_safe_ceremony_receipt_example.package_manifest.json`
- added inheritor-facing note `docs/LIBRARY/topics/successor_safe_ceremony_receipt_packages_should_ship_compact_package_manifests.md` plus compact process receipt `artifacts/process/successor_safe_ceremony_receipt_package_manifest_receipt_20260322.json`
- extended the research source ledger through `RS-GR-530` and threaded the package-manifest move into the agenda, opinions, inheritor brief, bucket, changelog, and agent log
- local validation target for this pass: successor-safe ceremony tooling, inventories, schema/docs checks, repo controls, Python certify tests, and the known Rust-blocked doctor/harness boundary recheck

## rev0490 - 2026-03-22

- added a compact package-supersession layer for successor-safe ceremony receipt bundles so future stewards can see which refreshed package manifest replaced an older package root instead of inferring the replacement target from neighboring files and timestamps
- added `schemas/successor_safe_ceremony_receipt_package_supersession.schema.json`, extended `scripts/tools/successor_safe_ceremony_receipt.py` with `supersede`, tightened `scripts/test/check_successor_safe_ceremony_receipt.py`, and committed refreshed review-era snapshots plus `examples/snapshots/successor_safe_ceremony_receipt_example.package_supersession.json`
- added inheritor-facing note `docs/LIBRARY/topics/successor_safe_ceremony_receipt_package_manifests_should_ship_compact_supersession_records.md` plus compact process receipt `artifacts/process/successor_safe_ceremony_receipt_package_supersession_receipt_20260322.json`
- extended the research source ledger through `RS-GR-533` and threaded the package-supersession move into the agenda, opinions, inheritor brief, bucket, changelog, and agent log
- local validation target for this pass: successor-safe ceremony tooling, refreshed package snapshots, inventories, schema/docs checks, repo controls, Python certify tests, and the known Rust-blocked doctor/harness boundary recheck



## rev0491 - 2026-03-22

- added a compact package-lineage layer for successor-safe ceremony receipt bundles so once more than one package supersession exists, future stewards can recover the current authoritative package head and ordered replacement chain from one tiny machine-checkable object instead of walking filenames and timestamps by hand
- added `schemas/successor_safe_ceremony_receipt_package_lineage.schema.json`, extended `scripts/tools/successor_safe_ceremony_receipt.py` with `lineage`, tightened `scripts/test/check_successor_safe_ceremony_receipt.py`, and committed worked snapshot `examples/snapshots/successor_safe_ceremony_receipt_example.package_lineage.json`
- added inheritor-facing note `docs/LIBRARY/topics/successor_safe_ceremony_receipt_package_supersession_records_should_collapse_to_compact_lineage_records.md` plus compact process receipt `artifacts/process/successor_safe_ceremony_receipt_package_lineage_receipt_20260322.json`
- extended the research source ledger through `RS-GR-536` and threaded the package-lineage move into the agenda, opinions, inheritor brief, bucket, changelog, and agent log
- local validation target for this pass: successor-safe ceremony tooling, package-lineage snapshot, inventories, schema/docs checks, repo controls, Python certify tests, and the known Rust-blocked doctor/harness boundary recheck


## rev0492 - 2026-03-22

- added a compact package-head pointer for successor-safe ceremony receipt bundles so future stewards can discover the live authoritative package manifest and its current status artifacts immediately instead of opening the full lineage object first
- added `schemas/successor_safe_ceremony_receipt_package_head.schema.json`, extended `scripts/tools/successor_safe_ceremony_receipt.py` with `head`, tightened `scripts/test/check_successor_safe_ceremony_receipt.py`, and committed worked snapshot `examples/snapshots/successor_safe_ceremony_receipt_example.package_head.json`
- added inheritor-facing note `docs/LIBRARY/topics/successor_safe_ceremony_receipt_package_lineages_should_ship_compact_head_pointers.md` plus compact process receipt `artifacts/process/successor_safe_ceremony_receipt_package_head_receipt_20260322.json`
- extended the research source ledger through `RS-GR-539` and threaded the package-head move into the agenda, opinions, inheritor brief, bucket, changelog, and agent log
- local validation target for this pass: successor-safe ceremony tooling, package-head snapshot, inventories, schema/docs checks, repo controls, Python certify tests, and the known Rust-blocked doctor/harness boundary recheck

## rev0493 - 2026-03-22

- added a compact package-status-card layer for successor-safe ceremony receipt bundles so the package head can expose one live status object answering whether the current package remains citable, until when, and what would reopen it instead of forcing future stewards to open the watch / verdict / advisory trio by hand
- added `schemas/successor_safe_ceremony_receipt_package_status_card.schema.json`, extended `scripts/tools/successor_safe_ceremony_receipt.py` with `statuscard`, tightened `scripts/test/check_successor_safe_ceremony_receipt.py`, refreshed `examples/snapshots/successor_safe_ceremony_receipt_example.package_head.json`, and committed worked snapshot `examples/snapshots/successor_safe_ceremony_receipt_example.package_status_card.json`
- added inheritor-facing note `docs/LIBRARY/topics/successor_safe_ceremony_receipt_package_heads_should_ship_compact_status_cards.md` plus compact process receipt `artifacts/process/successor_safe_ceremony_receipt_package_status_card_receipt_20260322.json`
- extended the research source ledger through `RS-GR-542` and threaded the package-status-card move into the agenda, opinions, inheritor brief, bucket, changelog, and agent log
- local validation target for this pass: successor-safe ceremony tooling, refreshed package-status-card and package-head snapshots, inventories, schema/docs checks, repo controls, Python certify tests, and the known Rust-blocked doctor/harness boundary recheck

## rev0494 - 2026-03-22

- added a compact package-redirect layer for successor-safe ceremony receipt bundles so a steward who lands on a superseded package manifest gets one explicit current-reference target, successor manifest, and live status pointer instead of reconstructing replacement guidance from lineage and status files by hand
- added `schemas/successor_safe_ceremony_receipt_package_redirect.schema.json`, extended `scripts/tools/successor_safe_ceremony_receipt.py` with `redirect`, tightened `scripts/test/check_successor_safe_ceremony_receipt.py`, and committed worked snapshot `examples/snapshots/successor_safe_ceremony_receipt_example.package_redirect.json`
- added inheritor-facing note `docs/LIBRARY/topics/superseded_successor_safe_ceremony_receipt_packages_should_ship_compact_redirect_artifacts.md` plus compact process receipt `artifacts/process/successor_safe_ceremony_receipt_package_redirect_receipt_20260322.json`
- extended the research source ledger through `RS-GR-545` and threaded the package-redirect move into the agenda, opinions, inheritor brief, bucket, changelog, and agent log
- local validation target for this pass: successor-safe ceremony tooling, package-redirect snapshot, inventories, schema/docs checks, repo controls, Python certify tests, and the known Rust-blocked doctor/harness boundary recheck


## rev0495 - 2026-03-22

- added a compact package-catalog layer for successor-safe ceremony receipt bundles so a future steward can discover the live package head for each retained family and any superseded-package redirects from one archive entry point instead of browsing lineage and redirect files family by family
- added `schemas/successor_safe_ceremony_receipt_package_catalog.schema.json`, extended `scripts/tools/successor_safe_ceremony_receipt.py` with `catalog`, tightened `scripts/test/check_successor_safe_ceremony_receipt.py`, and committed worked snapshot `examples/snapshots/successor_safe_ceremony_receipt_example.package_catalog.json`
- added inheritor-facing note `docs/LIBRARY/topics/successor_safe_ceremony_receipt_package_heads_and_redirects_should_collapse_to_compact_catalogs.md` plus compact process receipt `artifacts/process/successor_safe_ceremony_receipt_package_catalog_receipt_20260322.json`
- extended the research source ledger through `RS-GR-548` and threaded the package-catalog move into the agenda, opinions, inheritor brief, changelog, and agent log
- local validation target for this pass: successor-safe ceremony tooling, package-catalog snapshot, inventories, schema/docs checks, repo controls, Python certify tests, and the known Rust-blocked doctor/harness boundary recheck

## rev0496 - 2026-03-22

- added a compact package-verification-report layer for successor-safe ceremony receipt bundles so future stewards can see which local validation checks actually ran against the live package and where the cloudtainer boundary stopped instead of reconstructing that from chat history
- added `schemas/successor_safe_ceremony_receipt_package_verification_report.schema.json`, extended `scripts/tools/successor_safe_ceremony_receipt.py` with `verifyreport`, tightened `scripts/test/check_successor_safe_ceremony_receipt.py`, and committed worked snapshot `examples/snapshots/successor_safe_ceremony_receipt_example.package_verification_report.json`
- refreshed `examples/snapshots/successor_safe_ceremony_receipt_example.package_head.json`, `...package_redirect.json`, and `...package_catalog.json` so the live package discovery surface now carries the verification-report hash forward
- added inheritor-facing note `docs/LIBRARY/topics/successor_safe_ceremony_receipt_package_heads_should_ship_compact_verification_reports.md` plus compact process receipt `artifacts/process/successor_safe_ceremony_receipt_package_verification_report_receipt_20260322.json`
- extended the research source ledger through `RS-GR-550` and threaded the verification-report move into the agenda, opinions, inheritor brief, bucket, changelog, and agent log



## rev0497 - 2026-03-22

- added a compact package-claim-scope layer for successor-safe ceremony receipt bundles so future stewards can see which downstream claims the current local verification basis actually supports here instead of overclaiming from the raw verification report
- added `schemas/successor_safe_ceremony_receipt_package_claim_scope.schema.json`, extended `scripts/tools/successor_safe_ceremony_receipt.py` with `claimscope`, tightened `scripts/test/check_successor_safe_ceremony_receipt.py`, and committed worked snapshot `examples/snapshots/successor_safe_ceremony_receipt_example.package_claim_scope.json`
- refreshed `examples/snapshots/successor_safe_ceremony_receipt_example.package_head.json`, `...package_redirect.json`, and `...package_catalog.json` so the live package discovery surface now carries the claim-scope hash forward
- added inheritor-facing note `docs/LIBRARY/topics/successor_safe_ceremony_receipt_package_verification_reports_should_ship_compact_claim_scope_artifacts.md` plus compact process receipt `artifacts/process/successor_safe_ceremony_receipt_package_claim_scope_receipt_20260322.json`
- extended the research source ledger through `RS-GR-552` and threaded the package-claim-scope move into the agenda, opinions, inheritor brief, bucket, changelog, and agent log

## rev0498 - 2026-03-22

- added a compact package-reliance-card layer for successor-safe ceremony receipt bundles so future stewards can recover one explicit live reliance answer from the current status card, verification report, and claim scope instead of reconciling those artifacts by hand
- added `schemas/successor_safe_ceremony_receipt_package_reliance_card.schema.json`, extended `scripts/tools/successor_safe_ceremony_receipt.py` with `reliancecard`, tightened `scripts/test/check_successor_safe_ceremony_receipt.py`, and committed worked snapshot `examples/snapshots/successor_safe_ceremony_receipt_example.package_reliance_card.json`
- refreshed `examples/snapshots/successor_safe_ceremony_receipt_example.package_head.json`, `...package_redirect.json`, and `...package_catalog.json` so the live package discovery surface now carries the reliance-card hash forward
- added inheritor-facing note `docs/LIBRARY/topics/successor_safe_ceremony_receipt_package_claim_scopes_should_ship_compact_reliance_cards.md` plus compact process receipt `artifacts/process/successor_safe_ceremony_receipt_package_reliance_card_receipt_20260322.json`
- extended the research source ledger through `RS-GR-555` and threaded the package-reliance-card move into the agenda, opinions, bucket, changelog, and agent log


## rev0503 - 2026-03-23

- added a compact Rust test scenario-coverage ledger so blocked sessions can see which declared world/noise/termination/strategy/assertion variants are actually exercised by the current Rust tests and which are unseen, inline-only, or sparse
- added `scripts/report/build_rust_test_scenario_coverage.py`, generated `docs/RUST_TEST_SCENARIO_COVERAGE.md`, emitted `artifacts/reports/rust_test_scenario_coverage.json`, and wired new make targets plus the canonical shadow pass around it
- refreshed README/docs presence checks and blocked-session guidance so future inheritors can regenerate and trust the new coverage-gap map without widening the archive with copied Rust bodies
- local validation target for this pass: new scenario-coverage regen/check, docs/index/README command alignment, artifact bucket refresh, and the canonical cloudtainer shadow pass at the known Rust-blocked boundary

## rev0507 - 2026-03-23

- added a compact Rust external-test lift queue so blocked sessions can hand the eventual Rust-capable inheritor concrete first external test placements, lane choices, and fixture-backed implementation recipes instead of only seed inventories
- added `scripts/report/build_rust_external_test_queue.py`, generated `docs/RUST_EXTERNAL_TEST_QUEUE.md`, emitted `artifacts/reports/rust_external_test_queue.json`, and wired new make targets plus the canonical shadow pass around it
- refreshed README/docs presence checks and blocked-session guidance so the new lift queue stays discoverable and reproducible without widening the archive with dormant `.rs` stubs
- local validation target for this pass: external-test queue regen/check, docs/index/README command alignment, artifact bucket refresh, and a fresh cloudtainer shadow-pass receipt if the sandbox allows it

## rev0512 - 2026-03-23

- added a compact Rust external-test patch rehearsal so blocked sessions can scratch-apply the monolithic comeback patchset and the cumulative shard series, compare the resulting target-file hashes, and preserve one explicit proof that both landing paths agree before a later Rust-capable machine edits the crate for real
- added `scripts/report/build_rust_external_test_patch_rehearsal.py`, generated `docs/RUST_EXTERNAL_TEST_PATCH_REHEARSAL.md`, emitted `artifacts/reports/rust_external_test_patch_rehearsal.json`, and wired new make targets plus the canonical shadow pass around that rehearsal lane
- found and fixed a real divergence: the rev0511 monolithic patchset and cumulative shard series both applied, but they landed on different final file layouts because the patchset grouped helpers/tests while the shards preserved per-seed blocks; `build_rust_external_test_patchset.py` now preserves shard order and block markers so the rehearsal reports `final_state_equivalent=true`
- refreshed README/docs presence checks, command inventory, and artifact buckets so the new rehearsal lane stays discoverable and the stronger patchset/shard equivalence claim is preserved as a small audited artifact instead of tribal knowledge

## rev0517 - 2026-03-23

- added a compact cloudtainer shadow-pass receipt-history report so future inheritors can see how the blocked-session pass widened across revisions, which early-only steps were retired, and how stable the main budget cutpoints remain across completed receipts instead of relying only on the latest frontier snapshot
- added `scripts/report/build_cloudtainer_shadow_pass_history.py`, generated `docs/CLOUDTAINER_SHADOW_PASS_HISTORY.md`, emitted `artifacts/reports/cloudtainer_shadow_pass_history.json`, and wired new make targets plus the canonical shadow pass around that longitudinal receipt lane
- refreshed README/docs/generated-doc presence checks and blocked-session guidance so the new history view stays discoverable and can be regenerated without replaying old receipts or widening the archive with copied logs

## rev0519 - 2026-03-23

- added a compact cloudtainer shadow-pass budget card so blocked sessions can pick the short/medium/long command surface from one fused report instead of reopening the frontier, receipt-history, and volatility docs by hand
- added `scripts/report/build_cloudtainer_shadow_pass_budget_card.py`, generated `docs/CLOUDTAINER_SHADOW_PASS_BUDGET_CARD.md`, emitted `artifacts/reports/cloudtainer_shadow_pass_budget_card.json`, and wired new make targets plus a dedicated validator around that fused budgeting lane
- refreshed README/docs/generated-doc guidance, command inventory, validator inventory, and artifact buckets so the new budget card stays discoverable and small while the archive remains Rust-blocked and citation-first
- local validation target for this pass: new budget-card regen/check, existing shadow-pass history/volatility/budget-profile checks, docs/index/README command alignment, inventories, and the known `make test-quick` Rust-boundary recheck (`junest` missing for the Rust harness here)

## rev0520 - 2026-03-23

- added a compact Rust comeback card so the first Rust-capable inheritor can recover the landing order, milestone plateaus, and smallest clean foothold from one fused report instead of reopening the queue, seed-loader, bundle, shard, rehearsal, and prefix-frontier surfaces by hand
- added `scripts/report/build_rust_comeback_card.py`, generated `docs/RUST_COMEBACK_CARD.md`, emitted `artifacts/reports/rust_comeback_card.json`, and added `scripts/test/check_rust_comeback_card.py`
- refreshed README/docs/generated-doc guidance plus the command/validator/artifact inventories so the new comeback card stays discoverable and drift-checked in blocked sessions

## rev0521 - 2026-03-23

- added a compact Rust comeback execution card so the first Rust-capable inheritor inherits not just which prefix to land, but exactly which new witnesses and lane-smoke commands to run after each comeback plateau
- added `scripts/report/build_rust_comeback_execution_card.py`, generated `docs/RUST_COMEBACK_EXECUTION_CARD.md`, emitted `artifacts/reports/rust_comeback_execution_card.json`, and added `scripts/test/check_rust_comeback_execution_card.py`
- corrected the prefix-frontier wording so the archive no longer implies a nonexistent probe-only closure plateau before the final dual-lane shard

## rev0522 - 2026-03-23

- added a compact cloudtainer Rust recovery card so blocked sessions can answer from one surface whether Rust is recoverable in place here or whether the right move is to stop poking the wrapper and stay on the static lane
- added `scripts/report/build_cloudtainer_rust_recovery_card.py`, generated `docs/CLOUDTAINER_RUST_RECOVERY_CARD.md`, emitted `artifacts/reports/cloudtainer_rust_recovery_card.json`, and added `scripts/test/check_cloudtainer_rust_recovery_card.py`
- preserved the live boundary explicitly: this cloudtainer is `junest_binary_missing`, so the right local move is to refresh the blocked-session surfaces here and hand the quick foothold to the first Rust-capable machine

## rev0523 - 2026-03-23

- added a compact archive size guardrail card so future inheritors can see the live tree footprint, baseline growth since 2026-03-16, and whether PDFs or scratch leaked back into the package boundary without reopening the larger historical compaction machinery
- added `scripts/report/build_archive_size_guardrail_card.py`, generated `docs/ARCHIVE_SIZE_GUARDRAIL_CARD.md`, emitted `artifacts/reports/archive_size_guardrail_card.json`, and added `scripts/test/check_archive_size_guardrail_card.py`
- preserved the main archive-shaping result in one small surface: the package boundary is still PDF-free and scratch-free, while the dominant byte pressure has moved into internal doctrine, chronicles, and tooling mass

## rev0524 - 2026-03-23

- added a compact archive byte triage card so future inheritors know what to protect first and which oversized markdown surfaces to condense first if the archive needs a deliberate diet pass
- added `scripts/report/build_archive_byte_triage_card.py`, generated `docs/ARCHIVE_BYTE_TRIAGE_CARD.md`, emitted `artifacts/reports/archive_byte_triage_card.json`, and added `scripts/test/check_archive_byte_triage_card.py`
- fixed a real measurement oscillation while landing the card so the byte-triage and size-guardrail surfaces now validate cleanly instead of perturbing one another indefinitely

## rev0525 - 2026-03-23

- added a compact archive package-cut discipline so future inheritors know which mutating harness gates must run before the final package-boundary refresh and in what stable order to settle inventories plus the size/triage fixed-point pass before cutting the next revision zip
- added `scripts/report/build_archive_package_cut_card.py`, generated `docs/ARCHIVE_PACKAGE_CUT_CARD.md`, emitted `artifacts/reports/archive_package_cut_card.json`, and added `scripts/test/check_archive_package_cut_card.py`
- preserved one concrete live packaging nuance in a durable surface: `make test-quick` and `make test-full` both write env receipts before the Rust lane, so those harness gates belong before the final package-boundary refresh rather than after it

## rev0526 - 2026-03-23

- added a compact archive reentry card so future inheritors can reopen the current revision from one role-annotated head pointer instead of reconciling the Rust recovery, comeback execution, and package-cut surfaces by hand
- added `scripts/report/build_archive_reentry_card.py`, generated `docs/ARCHIVE_REENTRY_CARD.md`, emitted `artifacts/reports/archive_reentry_card.json`, and added `scripts/test/check_archive_reentry_card.py`
- backfilled the recent archive passes into the changelog so the current archive head and its immediate predecessor can be recovered from the repo itself rather than from chat history or nearby zip filenames

## rev0527 - 2026-03-23

- added a one-command archive-truth settle wrapper so future inheritors can replay the package-boundary fixed point from `make settle-archive-truth` instead of manually retyping the mutating gate, inventory refreshes, size/triage passes, and package/reentry card updates
- added `scripts/tools/settle_archive_truth.py`, wired `make settle-archive-truth`, and added `scripts/test/check_archive_truth_settle_tool.py` so the canonical wrapper has a small plan contract and a dry-run/list-steps surface
- tightened the archive-size and archive-byte-triage builders to exclude the derived archive reentry outputs from byte accounting, which keeps the route-layer card from perturbing the package-boundary numbers it summarizes
- updated `docs/ARCHIVE_PACKAGE_CUT_CARD.md` and `docs/ARCHIVE_REENTRY_CARD.md` so the package steward role now points at the canonical settle wrapper rather than leaving that closeout ritual implicit


## rev0528 - 2026-03-23

- added a normalized archive revision cut planner so future package stewards can derive the next safe revision label and exact root/zip stem from the current changelog-aligned head instead of improvising filenames or reusing an old revision number
- added `scripts/tools/plan_archive_revision_cut.py`, `scripts/report/build_archive_revision_cut_card.py`, generated `docs/ARCHIVE_REVISION_CUT_CARD.md`, emitted `artifacts/reports/archive_revision_cut_card.json`, added `scripts/test/check_archive_revision_cut_card.py`, and wired `make plan-archive-revision-cut`, `make update-archive-revision-cut-card`, and `make test-archive-revision-cut-card`
- fixed a real package-cut truth bug: the archive package-cut card had been telling stewards to use inventory test targets as if they refreshed retained files, but those targets validate only; the card now points at the real inventory update targets and the one-command settle wrapper now refreshes and validates the revision-cut card too

## rev0529 - 2026-03-23

- added a one-command archive revision cutter for settle+rename+zip closeout
- added `scripts/tools/cut_archive_revision.py`, wired `make cut-archive-revision` plus `scripts/test/check_archive_revision_cut_tool.py`, and threaded the canonical cutter through the archive package-cut, reentry, and revision-cut cards
- kept the blocked Rust boundary explicit in the closeout lane: the cutter treats the missing-JuNest gate as expected during settle, then refreshes the archive-size, byte-triage, package-cut, reentry, and revision-cut surfaces on the renamed head before packaging

## rev0530 - 2026-03-23

- added a sibling-zip lineage audit so future package stewards can confirm that the external package lane agrees with the live root and catch duplicated revision labels from filenames alone instead of inferring archive authority by hand
- added `scripts/tools/audit_archive_zip_lineage.py`, `scripts/report/build_archive_zip_lineage_card.py`, generated `docs/ARCHIVE_ZIP_LINEAGE_CARD.md`, emitted `artifacts/reports/archive_zip_lineage_card.json`, added `scripts/test/check_archive_zip_lineage_card.py`, and wired `make update-archive-zip-lineage-card` plus `make test-archive-zip-lineage-card`
- threaded the new card through the closeout lane: `make settle-archive-truth`, `scripts/tools/cut_archive_revision.py`, and the archive package-cut discipline now refresh and validate the sibling-zip audit alongside the existing size, reentry, and revision-cut surfaces

## rev0531 - 2026-03-23

- added sibling-zip chronology audit so archive head authority stays revision-first when timestamp order regresses across revisions

## rev0532 - 2026-03-23

- Add an authoritative sibling-zip reopen card and resolver so future inheritors can emit the exact winning external zip path instead of guessing from timestamps or reused revision labels.
- Wire the zip-authority surface into the settle, package-cut, and reentry lanes so reopen safety is part of the canonical archive-truth closeout loop.

## rev0533 - 2026-03-23

- Added a compact hash-bearing archive handoff pack so future inheritors can verify the exact blocked-session control-plane doc/report set without rescanning the wider tree.
- Wired the handoff pack into the settle and cut loops, and updated the package/reentry surfaces so the pack stays part of the canonical archive closeout discipline.

## rev0534 - 2026-03-23

- Added an authoritative sibling-zip digest card so the winning external archive can be verified by path, byte size, and SHA-256 instead of filename authority alone.
- Wired the zip digest surface into the settle/cut loop, the handoff pack, and the size-sensitive admin-output exclusions so it stays small and trustworthy.

## rev0535 - 2026-03-23

- Added the archive zip size truth card to distinguish the internal packaged-size proxy from the exact sibling zip bytes, calibrated against the immutable predecessor zip.
- Wired the zip-size truth surface through the archive settle/cut/handoff control plane so package stewards stop treating `approx_revision_zip_bytes` as the final delivered zip.

## rev0536 - 2026-03-23

- Added a one-command archive handoff-pack verifier so future inheritors can hash-check the compact blocked-session control stack instead of trusting the manifest passively.
- Added `scripts/tools/verify_archive_handoff_pack.py`, wired `make verify-archive-handoff-pack` plus `scripts/test/check_archive_handoff_pack_verify_tool.py`, and threaded the verifier through the handoff, reentry, package-cut, settle, and cut surfaces.

## rev0537 - 2026-03-23

- Added a one-command authoritative sibling-zip verifier so future inheritors can prove that the winning external archive still exists and matches the live authority rule, selected path, and on-disk bytes.
- Added `scripts/tools/verify_authoritative_archive_zip.py`, wired `make verify-authoritative-archive-zip` plus `scripts/test/check_authoritative_archive_zip_verify_tool.py`, and threaded the verifier through the zip-digest, package-cut, reentry, handoff-pack, settle, and cut surfaces.
- Cloudtainer Rust probe oracles: added a blocked-session oracle layer that covers all 14 current Rust comeback queue rows with exact path witnesses for deterministic seeds and exact finite-horizon expectation witnesses for the stochastic seeds.
- The oracle surface currently records 8 exact-path rows, 6 exact-expectation rows, and 3 simple-standing rows where declared `world.reputation.initial_standing` is inert because probe expansion still seeds `TaskSpec` standing from `1.0`.


## rev0538 - 2026-03-23

- Added blocked-session Rust probe oracles so the cloudtainer now carries exact path witnesses for deterministic comeback probe seeds and exact finite-horizon expectation witnesses for the current stochastic seeds.
- Surfaced that the current simple-standing probe path leaves declared `world.reputation.initial_standing` inert because probe expansion still seeds `TaskSpec` standing from `1.0`, and wired the new oracle card into the cloudtainer shadow-pass and command/doc inventories.


## rev0539 - 2026-03-23

- Added a blocked-session standing bootstrap delta card so future Rust-capable inheritors can see whether fixing the current inert `simple_standing.initial_standing` seam changes the current comeback witnesses.
- Proved the current affected comeback rows are trace-only under that repair: all 3 affected rows keep their mean stats while the standing traces diverge from round 0 because the active strategy selectors do not branch on `opponent_standing`.
- Fixed the archive handoff-pack validator to compare duplicate-revision and chronology-inversion hazard counts against the live lineage and chronology reports instead of assuming those local sibling-zip hazards must be nonzero.

## rev0540 - 2026-03-23

- Added a standalone Rust guard patch and rehearsal for the simple-standing bootstrap seam, asserting round-0 trace standing against declared initial_standing once the seam is repaired.
- Threaded the new guard through the delta guidance, command/docs indexes, generated-doc presence checks, and the cloudtainer shadow pass so blocked sessions can keep it fresh.

## rev0541 - 2026-03-23

- Added minimal probe-local Rust repair patch plus repair→guard rehearsal for the simple-standing bootstrap seam.


## rev0542 - 2026-03-23

- Added standing-bootstrap layering proof plus a clean-head comeback bundle patch and rehearsal, so the first Rust-capable inheritor can choose either explicit layered landing or one-shot apply without ambiguity.


## rev0543 - 2026-03-23

- Added a post-patchset standing-bootstrap convenience bundle plus rehearsal, so the Rust-capable inheritor now has a one-step apply artifact in both common branch states: clean head and patchset-already-landed.

## rev0544 - 2026-03-23

- Add an exact standing-bootstrap branch-state selector plus a rehearsal that proves it recognizes the known clean-head, patchset-only, partial-layer, and already-final states across the four comeback target files.
- Add a reusable selector tool that fails closed on drifted states so future Rust-capable inheritors do not force the wrong convenience bundle onto mixed branches.

## rev0545 - 2026-03-23

- Add a standing-bootstrap route-equivalence proof showing that the clean-head bundle, explicit layered landing, and patchset-plus-follow-on bundle converge to the same four target-file bytes.
- Tighten first-machine trust in the convenience artifacts by proving the selector routes among byte-equivalent landings, not semantically divergent shortcuts.

## rev0546 - 2026-03-23

- Added a standing-bootstrap execution card, execution-plan tool, and convergent rehearsal so each recognized branch state now carries an exact apply/verify path to the proved final hash.

## rev0547 - 2026-03-23

- Added a final-state standing-bootstrap verification ladder that gates on exact `final_full`, then runs the dedicated bootstrap guard, the three exact affected `probe_run` witnesses, and only then broader probe-lane smoke.
- Added a state-aware ladder tool and rehearsal so partial or drifted branch states route back to apply sequencing instead of emitting cargo commands too early.


## rev0548 - 2026-03-23

- Added an exact standing-bootstrap checkpoint card plus a small runtime tool so each recognized non-final branch state now carries the exact intermediate state id and 4-file combined hash that should appear after every apply step.
- Added a scratch-state checkpoint rehearsal proving those intermediate pause points match the actual post-apply checkout, so future Rust-capable inheritors can stop safely between layers instead of only trusting the start and final states.

## rev0549 - 2026-03-23

- add exact checkpoint verifier for direct bootstrap states and per-step checkpoint landings

## rev0550 - 2026-03-24

- Recovered source-level checkpoint-verifier rehearsal lane and compact proof surfaces.
- Removed stale __pycache__ residue before packaging.

## rev0551 - 2026-03-24

- Add compact rematch-world world-emission control card


## rev0552 - 2026-03-24

- Add compact rematch-world native-fill locus map

## rev0553 - 2026-03-24

- added a compact rematch-world landing ladder that turns the 30-edit publication floor into a 7-stage edit sequence plus a 5-phase closeout proof ladder


## rev0554 - 2026-03-24

- Added a compact exact rematch-world example delta ledger that separates the 30-path publication floor from 3 optional row insertions.
- Threaded the ledger through the command surface, generated-doc presence check, README/docs indexes, and benchmark-program handoff lane.
- Refreshed inventories plus the root-local package/reentry/handoff surfaces on the renamed rev0554 tree.
## rev0555 - 2026-03-24

- added a compact rematch-world closeout lifecycle ledger so the first native publication path now has one exact retained-vs-exit-vs-authority witness instead of scattered receipt memory
- landed `scripts/report/build_rematch_world_benchmark_closeout_lifecycle_ledger.py`, generated `docs/REMATCH_WORLD_BENCHMARK_CLOSEOUT_LIFECYCLE_LEDGER.md` plus `artifacts/reports/rematch_world_benchmark_closeout_lifecycle_ledger.json`, and added `scripts/test/check_rematch_world_benchmark_closeout_lifecycle_ledger.py`
- threaded the new lifecycle ledger through the Makefile help/target surface, generated-doc presence, README/docs indexes, and benchmark-program handoff lane, then refreshed command / validator / artifact inventories

## rev0556 - 2026-03-24

- Added a compact rematch-world citation witness matrix so the first native publication now has one exact claim-family-to-citation map instead of forcing inheritors to reopen the whole bridge stack.
- Repaired one discoverability drift while landing it: the existing landing-ladder doc is now explicitly threaded through the generated-doc presence check and both README doc indexes.

## rev0557 - 2026-03-24

- Added a compact rematch-world open touchpoint resolution map that collapses the current caution surface into six actionable closure targets.
- Threaded the new closure queue through the Makefile surface, generated-doc presence check, README/docs indexes, benchmark-program handoff lane, and refreshed inventories.


## rev0558 - 2026-03-24

- Added a compact rematch-world claim frontier that classifies all eight claim families into safe-now, 8/18/29-edit native unlocks, and the remaining SG-003 engine-gap residue.
- Threaded the new claim frontier through the Makefile surface, generated-doc presence, README/docs indexes, benchmark-program handoff lane, and refreshed inventories.

## rev0559 - 2026-03-24

- Added a compact rematch-world stage-yield ledger that shows what each native ladder stage actually buys, including prerequisite-only closures and metadata-only closeout.
- Threaded the new stage-yield ledger through the Makefile surface, generated-doc presence, README/docs indexes, benchmark-program handoff lane, and refreshed inventories.

## rev0560 - 2026-03-24

- added the rematch-world proof-budget ledger so the first native publication now has one exact byte-budget receipt for each minimal claim-family proof bundle
- refreshed the generated-doc presence surface, README/docs indexes, Makefile help/targets, and command/validator/artifact inventories around the new proof-budget lane
- preserved the size-discipline fact that the whole minimal proof library still fits in 7 unique surfaces / 43186 bytes, with only 2 receipt-backed bundles

## rev0561 - 2026-03-25

- add a userspace rustup detour note for post-JuNest blocked sessions and refresh the static Rust comeback/recovery cards


## rev0562 - 2026-03-25

- added a generated userspace rustup comeback plan plus replayable shell emitter so later HTTPS-capable machines get one exact repo-local bootstrap/fetch/probe/prune lane instead of reconstructing the detour from prose
- tightened archive-size discipline around that lane by isolating transient Rust state under `.local/{cargo,rustup,target}`, ignoring `.local/`, and making the prune step explicit in the generated plan
- added `RS-GR-560` and `RS-GR-561`, refreshed the detour note, and threaded the new plan through Makefile/help, docs indexes, environment guidance, generated-doc presence, and command/validator inventories


## rev0563 - 2026-03-25

- Added a static userspace fetch-surface audit so the later-machine Rust lane now fails closed if the lockfile or workspace widens beyond the current registry-only single-workspace case.
- Threaded the new card through Makefile/help, docs indexes, environment guidance, generated-doc presence, and command/validator/artifact inventories.
- Preserved the current compact bring-up fact: 80 lockfile packages, 79 registry packages, 0 git packages, 1 workspace member, and no extra cross-target requests.

## rev0564 - 2026-03-25

- add a static userspace compile-surface card so later-machine Rust bring-up can distinguish proc-macro/codegen friction from native-helper repair before spending a compile attempt
- preserve the current direct_derive_no_native_build posture: 11 direct deps, 2 derive-feature entries, 0 workspace build.rs files, and 0 native-helper watchlist hits

## rev0564 - 2026-03-25
- added `scripts/report/build_cloudtainer_userspace_offline_proof_ladder.py`, generated `docs/CLOUDTAINER_USERSPACE_OFFLINE_PROOF_LADDER.md` plus `artifacts/reports/cloudtainer_userspace_offline_proof_ladder.json`, and added `scripts/test/check_cloudtainer_userspace_offline_proof_ladder.py`
- threaded the new ladder through the Makefile help/target surface, both READMEs, `docs/ENVIRONMENT_SANDWORM.md`, generated-doc presence checks, and command/validator inventories so the later-machine control plane now includes an explicit offline cache-sufficiency proof step
- preserved one new practical checkpoint: after `cargo fetch --locked`, the inheritor should first run `cargo test --locked --offline --no-run -p gr_engine --test probe_run` before the exact quick-foothold witness, so build/cache failures separate cleanly from semantic test failures

## rev0565 - 2026-03-25
- add later-machine offline proof ladder for warmed-cache sufficiency before the first exact Rust witness
- threaded the new ladder through the Makefile, READMEs, generated-doc checks, inventories, and artifact buckets
- added RS-GR-564 and RS-GR-565 for cargo test --no-run plus Cargo offline/frozen guidance


## rev0567 - 2026-03-26
- package cut for the userspace failure resume card and later-machine log classifier
- preserves a phase-scoped decoder for bootstrap, toolchain, warm-cache, patch-apply, offline-compile, exact-witness, and lane-smoke failures
