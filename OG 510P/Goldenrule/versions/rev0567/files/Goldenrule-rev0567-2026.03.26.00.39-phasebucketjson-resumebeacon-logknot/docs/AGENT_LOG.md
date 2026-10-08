## Additional pass: userspace failure resume card and later-machine log classifier

- Added one compact later-machine failure-decoder surface so the eventual inheritor no longer has to reopen the whole rustup/fetch/compile ladder after the first real Rust attempt fails; the archive now preserves where to resume and which exact command to rerun.
- Added `scripts/report/build_cloudtainer_userspace_failure_resume_card.py`, generated `docs/CLOUDTAINER_USERSPACE_FAILURE_RESUME_CARD.md` plus `artifacts/reports/cloudtainer_userspace_failure_resume_card.json`, and wired `make update-cloudtainer-userspace-failure-resume-card` / `make test-cloudtainer-userspace-failure-resume-card`.
- Added `scripts/tools/classify_cloudtainer_userspace_failure.py` so later-machine logs can be bucketed back into bootstrap, toolchain, warm-cache, patch-apply, offline-compile, exact-witness, or lane-smoke resume phases from either plain stderr or Cargo JSON-message reruns.
- Extended `docs/RESEARCH_SOURCES.md` with `RS-GR-566` / `RS-GR-567` so the structured Cargo JSON-message capture lane stays citation-backed rather than being an uncited convenience.
- Main practical result: the archive now preserves one small answer to “what did this failure mean?” — bootstrap/path issues resume from rustup bootstrap, offline network/lock drift resumes from warm-cache, build/codegen failures stop at offline compile, and semantic failures stay pinned to the exact witness or the wider `probe_run` smoke step.

## Additional pass: userspace offline proof ladder and cache-sufficiency checkpoint

- Added one compact later-machine execution surface so the eventual inheritor can prove the warmed Cargo cache is actually sufficient offline before widening to more Rust work.
- Added `scripts/report/build_cloudtainer_userspace_offline_proof_ladder.py`, generated `docs/CLOUDTAINER_USERSPACE_OFFLINE_PROOF_LADDER.md` plus `artifacts/reports/cloudtainer_userspace_offline_proof_ladder.json`, and wired `make update-cloudtainer-userspace-offline-proof-ladder` / `make test-cloudtainer-userspace-offline-proof-ladder`.
- Extended `docs/RESEARCH_SOURCES.md` with `RS-GR-564` / `RS-GR-565` so the new `cargo test --no-run` compile checkpoint and Cargo offline/frozen guard semantics stay citation-backed.
- Main practical result: the later-machine comeback lane now preserves one explicit seven-phase proof ladder — `cargo fetch --locked`, health check, quick-foothold patch apply, `cargo test --locked --offline --no-run -p gr_engine --test probe_run`, the exact witness, lane smoke, and final `.local` prune.

## Additional pass: userspace rustup comeback plan and scratch-root discipline

- Added one replayable later-machine Rust recovery surface so the eventual inheritor no longer has to reconstruct the repo-local rustup detour from prose when JuNest is still absent here but a copied tree later reaches an HTTPS-capable machine.
- Added `scripts/tools/plan_userspace_rustup_comeback.py`, generated `docs/CLOUDTAINER_USERSPACE_RUSTUP_PLAN.md` plus `artifacts/reports/cloudtainer_userspace_rustup_plan.json`, and wired `make show-cloudtainer-userspace-rustup-plan` / `make update-cloudtainer-userspace-rustup-plan` / `make test-cloudtainer-userspace-rustup-plan`.
- Tightened archive-size discipline for that detour by adding `.local/` to `.gitignore`, making the generated plan keep all heavy state under `.local/cargo`, `.local/rustup`, and `.local/target`, and ending the emitted sequence with one explicit prune step instead of leaving future sessions to remember which repo-local toolchain roots are transient.
- Extended `docs/CLOUDTAINER_USERSPACE_RUSTUP_DETOUR.md` and `docs/RESEARCH_SOURCES.md` with `RS-GR-560` / `RS-GR-561` so the warm-cache (`cargo fetch --locked`) and repo-local artifact-root (`CARGO_TARGET_DIR`) claims stay citation-backed rather than only implied.
- Main practical result: the archive now preserves one exact command lane for the next capable machine — bootstrap `rustup` into repo-local roots, install the repo-pinned `stable` + `rustfmt` toolchain under `minimal`, stage the dependency cache while egress exists, run the standing quick-foothold probe witness, and then prune the transient toolchain roots before the next retained zip.

## Additional pass: rematch-world stage-yield ledger

- Added one compact per-stage payoff surface for the first native rematch-world publication so the eventual implementor can see which ladder steps directly unlock claims, which only retire prerequisite touchpoints, and which final step is publication metadata only.
- Added `scripts/report/build_rematch_world_benchmark_stage_yield_ledger.py`, generated `docs/REMATCH_WORLD_BENCHMARK_STAGE_YIELD_LEDGER.md` plus `artifacts/reports/rematch_world_benchmark_stage_yield_ledger.json`, and wired `make update-rematch-world-benchmark-stage-yield-ledger` / `make test-rematch-world-benchmark-stage-yield-ledger`.
- Main practical result: the archive now preserves one exact answer to “what does each of the 7 native stages buy?” — only the `8`/`18`/`29` cumulative frontiers unlock claim families, `12` and `23` are real prerequisite closures that still matter even though the safe-claim count stays flat, and `30` is metadata-only closeout.

## Additional pass: rematch-world example delta ledger

- Added one compact exact mutation witness for the first synthetic rematch-world publication so the eventual implementor can see the concrete seed-to-compiled change pattern without reopening the seed, compiled artifact, and native-fill map separately.
- Added `scripts/report/build_rematch_world_benchmark_example_delta_ledger.py` and `scripts/test/check_rematch_world_benchmark_example_delta_ledger.py`; generated `docs/REMATCH_WORLD_BENCHMARK_EXAMPLE_DELTA_LEDGER.md` plus `artifacts/reports/rematch_world_benchmark_example_delta_ledger.json`.
- Main practical result: the archive now preserves one machine-checked 33-path ledger showing that the synthetic compiled artifact exactly matches the live packet-to-artifact toolchain, that `30` of those paths are the true publication floor, and that the remaining `3` are optional row insertions inside the already-legal occupancy / turnover / paired-ranking arrays.

## Additional pass: rematch-world native-fill map
- Added `scripts/report/build_rematch_world_benchmark_landing_ladder.py`, generated `docs/REMATCH_WORLD_BENCHMARK_LANDING_LADDER.md`, emitted `artifacts/reports/rematch_world_benchmark_landing_ladder.json`, and added `make update-rematch-world-benchmark-landing-ladder` / `make test-rematch-world-benchmark-landing-ladder` plus `scripts/test/check_rematch_world_benchmark_landing_ladder.py`.

- Added one compact inheritor-facing fill map for the first endogenous rematch-world benchmark so future implementors can see the exact editable prefixes, blocker loci, and minimum publishable mutation set without reopening the seed plus separate mutation-guard and completion-gate tools.
- Added `scripts/report/build_rematch_world_benchmark_native_fill_map.py`, generated `docs/REMATCH_WORLD_BENCHMARK_NATIVE_FILL_MAP.md`, emitted `artifacts/reports/rematch_world_benchmark_native_fill_map.json`, and added `make update-rematch-world-benchmark-native-fill-map` / `make test-rematch-world-benchmark-native-fill-map` plus `scripts/test/check_rematch_world_benchmark_native_fill_map.py`.
- Main practical result: the archive now preserves one exact answer to “what do I actually edit, where are the remaining blocker rows, which metadata/status transitions remain, and how many concrete changes does the first publishable native fill require?” without growing new sidecar families.
- Preserved one non-obvious counting nuance: `benchmark_id` is already one of the 24 blocker loci, so the minimum publishable edit set is 30 changes (`24` blockers + `5` status flips + `artifact_state`) rather than 31.


## Additional pass: rematch-world world-emission card

- Added one compact inheritor-facing control surface for the first endogenous rematch-world benchmark so future implementors no longer have to reopen the seed, frozen-handoff audit, preflight receipt, publication bundle, spine audit, prune receipt, chain receipt, and package receipt separately just to remember the landing order.
- Added `scripts/report/build_rematch_world_benchmark_world_emission_card.py`, generated `docs/REMATCH_WORLD_BENCHMARK_WORLD_EMISSION_CARD.md`, emitted `artifacts/reports/rematch_world_benchmark_world_emission_card.json`, and added `make update-rematch-world-benchmark-world-emission-card` / `make test-rematch-world-benchmark-world-emission-card` plus `scripts/test/check_rematch_world_benchmark_world_emission_card.py`.
- Main practical result: the archive now preserves one exact answer to “which sections are still native fill work, which copied contract sections must stay frozen, what is the authoritative publication/prune/package ladder, and which objects remain durable versus transient?” without regrowing the proxy-era report fanout.
- Preserved one sequencing nuance that was easy to lose in prose: `retention_exit_ready` is a pre-prune gate, not the final package authority; the authoritative closeout surface remains the later `post_prune` / chain / package receipts.


## Additional pass: checkpoint verifier rehearsal recovery

- Recovered the missing source-level checkpoint-verifier rehearsal lane by adding `scripts/report/build_rust_standing_bootstrap_checkpoint_verifier_rehearsal.py` plus generated `docs/RUST_STANDING_BOOTSTRAP_CHECKPOINT_VERIFIER_REHEARSAL.md` and `artifacts/reports/rust_standing_bootstrap_checkpoint_verifier_rehearsal.json`.
- Main practical result: future inheritors now have one compact proof surface showing the verifier succeeds on live `clean_head`, succeeds on scratch `repair_only` and `final_full`, proves the `repair_only` step-1 route landing, fails closed on drift, and rejects conflicting checkpoint expectations.
- Threaded the rehearsal lane through the Makefile, README/docs indexes, generated-doc presence check, environment handbook, and inventories so it is maintained as a first-class blocked-session Rust handoff artifact instead of only a stale compiled hint.

## Additional pass: standing bootstrap checkpoint verifier

- Added one compact exact-checkpoint verification surface so a future Rust-capable inheritor can prove a just-applied bootstrap step landed the promised named state and combined hash instead of manually comparing checkpoint-card values.
- Added `scripts/tools/verify_rust_standing_bootstrap_checkpoint.py`, `scripts/report/build_rust_standing_bootstrap_checkpoint_verifier.py`, and `scripts/test/check_rust_standing_bootstrap_checkpoint_verifier_tool.py`; generated `docs/RUST_STANDING_BOOTSTRAP_CHECKPOINT_VERIFIER.md` plus `artifacts/reports/rust_standing_bootstrap_checkpoint_verifier.json`.
- Main practical result: the archive now supports both direct exact-state verification (`clean_head`, `repair_guard`, `final_full`, etc.) and route-step verification (`--from-state-id repair_only --step-index 1`) from one tool, with a dedicated validator covering live clean-head, direct scratch verification, route-step scratch verification, and fail-closed drift behavior.

## Additional pass: standing bootstrap verification ladder and final-state gating

- Added one compact post-apply verification surface for the repaired simple-standing bootstrap seam so the first Rust-capable inheritor no longer has to choose between under-checking the seam and immediately paying for whole-lane smoke.
- Added `scripts/report/build_rust_standing_bootstrap_verification_ladder.py`, `scripts/tools/emit_rust_standing_bootstrap_verification_ladder.py`, and `scripts/report/build_rust_standing_bootstrap_verification_ladder_rehearsal.py`; generated `docs/RUST_STANDING_BOOTSTRAP_VERIFICATION_LADDER.md`, `docs/RUST_STANDING_BOOTSTRAP_VERIFICATION_LADDER_REHEARSAL.md`, and the paired JSON reports.
- Main practical result: the archive now preserves one smallest standing-focused verification route after the bootstrap comeback lands — dedicated `probe_standing_bootstrap` first, then the three exact affected `probe_run` witnesses (`simple_standing`, `image_scoring`, `standing_norm`), then broader `probe_run` smoke — and it only emits that ladder after the checkout reaches exact `final_full`.

## Additional pass: standing bootstrap execution card and convergent plan rehearsal

- Added one compact first-machine execution surface for the bootstrap comeback lane so a future Rust-capable inheritor does not just know the current exact branch state, but also the smallest safe next apply sequence, the exact witness commands to run, and the final 4-file hash every recognized route should converge to.
- Added `scripts/report/build_rust_standing_bootstrap_execution_card.py`, generated `docs/RUST_STANDING_BOOTSTRAP_EXECUTION_CARD.md` plus `artifacts/reports/rust_standing_bootstrap_execution_card.json`, and recorded smallest-safe per-state plans for `clean_head`, the partial-layer states, `patchset_only`, and `final_full`.
- Added `scripts/tools/emit_rust_standing_bootstrap_execution_plan.py` plus `scripts/report/build_rust_standing_bootstrap_execution_rehearsal.py`, generated `docs/RUST_STANDING_BOOTSTRAP_EXECUTION_REHEARSAL.md` plus `artifacts/reports/rust_standing_bootstrap_execution_rehearsal.json`, and proved in scratch that the emitted plans from every recognized non-final state converge to the exact final hash while drifted states still fail closed.
- Extended the Makefile, README/docs indexes, generated-doc presence check, and environment handbook so the new one-command execution-plan lane is discoverable and drift-checked.
- Main practical result: the archive now preserves one explicit answer to “given the exact bootstrap branch state in front of me, what do I apply next, what should I run after that, and how do I know I reached the same final bytes as the other proven routes?” instead of forcing the inheritor to reconcile the selector, bundles, and route-equivalence proof by hand.

## Additional pass: one-command archive-truth settle wrapper

- Added `scripts/tools/settle_archive_truth.py`, `make settle-archive-truth`, and `scripts/test/check_archive_truth_settle_tool.py` so the package-boundary fixed point can be replayed from one command instead of by hand.
- The wrapper treats the current `make test-quick` Rust boundary as expected when the output matches the missing-JuNest / missing-Rust-toolchain markers, then continues into inventory refresh, the size/triage fixed point, and final package/reentry card refreshes.
- Tightened the archive-size and byte-triage cards by excluding the derived reentry outputs from their byte accounting, which keeps the route-layer cards from perturbing the package-boundary numbers they summarize.

## Additional pass: cloudtainer Rust recovery decision card

- Added `scripts/report/build_cloudtainer_rust_recovery_card.py`, generated `docs/CLOUDTAINER_RUST_RECOVERY_CARD.md` plus `artifacts/reports/cloudtainer_rust_recovery_card.json`, and wired `make update-cloudtainer-rust-recovery-card` / `make test-cloudtainer-rust-recovery-card`.
- The new card fuses the live execution-lane probe with the blocked-session budget card and the Rust comeback execution card, so the inheritor can distinguish `junest_home_missing` / `junest_toolchain_missing` (recoverable here) from `junest_binary_missing` (blocked before recovery starts).
- Current practical result: this cloudtainer is decisively `junest_binary_missing`, so the right local move is `make cloudtainer-shadow-pass-medium` rather than more JuNest poking; the first real Rust foothold remains the quick shard apply plus exact `probe_run` witness on the next capable machine.

## Additional pass: Rust comeback landing-order card

- Added `scripts/report/build_rust_comeback_card.py`, generated `docs/RUST_COMEBACK_CARD.md` plus `artifacts/reports/rust_comeback_card.json`, and wired `make update-rust-comeback-card` / `make test-rust-comeback-card`.
- The new card fuses the lift queue, seed-loader audit, bundle plan, patchset/shard series, rehearsal proof, and prefix frontier into one first-machine landing order for the next Rust-capable inheritor.
- Main practical result: the comeback is now legible in one page — all 14 rows are direct `ProbeSpec` loads, the clean first plateau remains shard prefix `6`, the first `externalize_now` row lands at prefix `7`, and the only dual-lane shard stays isolated at prefix `10`.

## Additional pass: budget-aware shadow-pass commands

- Added budget-aware cloudtainer shadow-pass commands (`make cloudtainer-shadow-pass-list-budgets`, `make cloudtainer-shadow-pass-short`, `make cloudtainer-shadow-pass-medium`, `make cloudtainer-shadow-pass-long`) plus `make test-cloudtainer-shadow-pass-budget-profiles`, so the inheritor can intentionally stop at the best known cutpoints before resuming later.
- Extended `scripts/tools/cloudtainer_shadow_pass.py` with `--budget-profile`, `--frontier-report`, and `--list-budget-profiles`; the command now resolves its short/medium/long cutpoints from the generated frontier report instead of hardcoding another parallel map.
- Refreshed `docs/CLOUDTAINER_SHADOW_PASS_FRONTIER.md` / `artifacts/reports/cloudtainer_shadow_pass_frontier.json` to include the exact short/medium/long commands beside the existing timing frontiers.

## Additional pass: cloudtainer shadow-pass budgeting frontier

- Added `scripts/report/build_cloudtainer_shadow_pass_frontier.py`, generated `docs/CLOUDTAINER_SHADOW_PASS_FRONTIER.md` plus `artifacts/reports/cloudtainer_shadow_pass_frontier.json`, and wired `make update-cloudtainer-shadow-pass-frontier` / `make test-cloudtainer-shadow-pass-frontier`.
- Used the latest full resumable shadow-pass receipt to quantify profitable interrupted-run cutpoints: `maps_contracts_coverage`, `queue_inputs_ready`, `static_comeback_plan_closed`, `archive_hygiene_synced`, and `full_shadow_pass`.
- Preserved the existing checkpoint/resume surface while giving the inheritor a better budgeting rule for when to stop intentionally before the sandbox wrapper cuts a long run off.


## Additional pass: resumable cloudtainer shadow passes

- Added checkpoint-and-resume support to the canonical blocked-session pass so sandbox-wrapper interruptions stop discarding completed work before a final process receipt is written.
- Extended `scripts/tools/cloudtainer_shadow_pass.py` with step subset selection, heartbeats during quiet steps, atomic checkpoint writes, `--resume`, and a deliberate `--stop-after-step` rehearsal mode; final receipts now carry `receipt_version=2` plus explicit checkpoint metadata.
- Added `make cloudtainer-shadow-pass-resume`, `make test-cloudtainer-shadow-pass-resume`, and `scripts/test/check_cloudtainer_shadow_pass_resume.py`; updated the README/docs environment guidance so the inheritor sees "resume instead of replay" as the default recovery move.
- Main practical result: a blocked-Rust session can now survive sandbox kills mid-pass, continue from the first unfinished step, and still land one compact final receipt without rerunning the whole static-navigation lane.

- Added `scripts/report/build_rust_patch_prefix_frontier.py`, generated `docs/RUST_PATCH_PREFIX_FRONTIER.md` plus `artifacts/reports/rust_patch_prefix_frontier.json`, and wired `make update-rust-patch-prefix-frontier` / `make test-rust-patch-prefix-frontier` plus the canonical shadow pass around that new frontier lane.
- The main new signal is a quantified set of stop points for the staged Rust comeback: prefix `1` is the smallest quick foothold, prefix `6` closes every current `lift_first` row, prefix `9` closes every current `probe_run` row, and prefix `10` is full closure including the final dual-lane metamorphic shard.

## Additional pass: ordered cumulative patch shards for the external Rust comeback

- Added `scripts/report/build_rust_external_test_patch_shards.py`, generated `docs/RUST_EXTERNAL_TEST_PATCH_SHARDS.md` plus `artifacts/reports/rust_external_test_patch_shards.json`, and emitted the ordered cumulative patch series under `artifacts/patches/rust_external_test_shards/*.patch`.
- Threaded the new patch-shard lane into `Makefile`, `README.md`, `docs/README.md`, `docs/ENVIRONMENT_SANDWORM.md`, `scripts/test/check_generated_docs_presence.py`, and `scripts/tools/cloudtainer_shadow_pass.py` so blocked sessions can regenerate it as part of the archive surface.
- Main effect: the old single replayable diff now has a smaller landing shape of 10 cumulative shards, with the first 6 shards covering only `lift_first` bundles and the one dual-lane shard (`scaling_prefix_stability`) deferred to the final apply step.

### Why this mattered

The archive already handed the inheritor one replayable unified patch, but that still forced the comeback to be all-or-nothing. The tighter durable move was to keep the monolithic patch *and* add an ordered cumulative series that can be landed in smaller batches without re-deriving helper/test blocks from the queue.

### Validation run in this cloudtainer

- `python3 scripts/report/build_rust_external_test_patch_shards.py --write` ✅
- `python3 scripts/report/build_rust_external_test_patch_shards.py` ✅
- `git apply --check artifacts/patches/rust_external_test_shards/01_fsm_grim_trigger_probe.patch` through the full cumulative 10-shard series on a temp copy of the target files ✅

---

- added `scripts/report/build_rust_lift_bundle_plan.py`, generated `docs/RUST_LIFT_BUNDLE_PLAN.md` plus `artifacts/reports/rust_lift_bundle_plan.json`, and wired `make update-rust-lift-bundle-plan` / `make test-rust-lift-bundle-plan` so blocked-Rust sessions can collapse the 14-row external-test queue into shared fixture/code bundles
- the new bundle plan shows the comeback can stay smaller than the raw queue implies: `queue_entries=14`, `bundle_count=10`, `rows_saved_via_bundling=4`, with one dual-lane seed (`scaling_prefix_stability`) and three other multi-row probe bundles
- threaded the new bundle plan into `README.md`, `docs/README.md`, `docs/ENVIRONMENT_SANDWORM.md`, `scripts/test/check_generated_docs_presence.py`, and `scripts/tools/cloudtainer_shadow_pass.py` so the command surface, docs surface, and canonical blocked-session pass all know how to regenerate it

## Additional pass: close the last example-seed-only Rust gaps with probe seeds

- Added three tiny self-contained probe seed examples so the remaining weak Rust rows no longer stop at strategy/metamorphic fragments:
  - `examples/probes/fsm_grim_trigger_probe.json`
  - `examples/probes/memory_one_exit_after_break_probe.json`
  - `examples/probes/scaling_prefix_stability_probe_seed.json`
- Regenerated the weak-gap ledgers plus the experiment catalog so the archive now records a fully probe-backed restart surface for the current Rust gaps:
  - `docs/RUST_GAP_WITNESS_QUEUE.md`
  - `artifacts/reports/rust_gap_witness_queue.json`
  - `docs/RUST_GAP_PROBE_SEED_INDEX.md`
  - `artifacts/reports/rust_gap_probe_seed_index.json`
  - `docs/EXPERIMENT_CATALOG.md`
  - `artifacts/reports/experiment_catalog.json`
- Tightened `scripts/report/build_rust_gap_witness_queue.py` so probe/example witnesses prefer exact structured variant matches within each example tier, which avoids letting `memory_one_exit` seeds masquerade as the best witness for the weaker `memory_one` row just because the token is a substring.
- Quieted the `grlab` / control unittest commands inside `scripts/tools/cloudtainer_shadow_pass.py` so the canonical blocked-session pass is less likely to die in this sandbox from log-volume rather than substance.

### Why this mattered

The archive had already converted every weak Rust row into at least one example witness, but three rows still stopped at `example_seed_only` instead of true self-contained probe seeds. That left a needless handoff gap: the inheritor still had to wrap a strategy or metamorphic fragment before writing the later external Rust test.

The smaller durable move was to commit those three missing probe seeds and tighten the witness ranking at the same time. That keeps the archive compact while making the restart queue cleaner and more directly liftable.

### Main practical result

The generated probe-seed index now reports `probe_seed_ready=14` and `example_seed_only=0`. In other words, every currently weak Rust scenario row now has a self-contained `examples/probes/*.json` seed, and the preferred-seed chooser no longer drifts toward nearby substring matches when an exact structured witness already exists.

### Validation run in this cloudtainer

- `python3 scripts/test/check_examples_json.py` ✅
- `python3 scripts/test/check_examples_unique_ids.py` ✅
- `python3 scripts/report/build_experiment_catalog.py --write` ✅
- `python3 scripts/report/build_rust_gap_witness_queue.py --write` ✅
- `python3 scripts/report/build_rust_gap_probe_seed_index.py --write` ✅
- `python3 scripts/report/build_artifact_bucket_inventory.py --write` ✅
- `python3 scripts/test/check_generated_docs_presence.py` ✅
- `python3 scripts/test/check_readme_command_surface.py` ✅
- `python3 scripts/test/check_docs_index_core.py` ✅
- `python3 scripts/test/check_scripts_compile.py` ✅
- `python3 scripts/test/check_scripts_executable.py` ✅

## Additional pass: probe-seed fixtures for the last weak Rust gaps

- Added four tiny self-contained probe examples so the remaining source-only Rust scenario rows now have executable JSON anchors instead of only source declarations:
  - `examples/probes/simple_standing_image_scoring_probe.json`
  - `examples/probes/simple_standing_standing_norm_probe.json`
  - `examples/probes/implementation_flip_probe.json`
  - `examples/probes/mutual_defect_rate_guardrail_probe.json`
- Added one compact generated index for blocked-Rust sessions that says which weak rows already have self-contained `examples/probes/*.json` seeds closest to becoming future external Rust tests:
  - `scripts/report/build_rust_gap_probe_seed_index.py`
  - `docs/RUST_GAP_PROBE_SEED_INDEX.md`
  - `artifacts/reports/rust_gap_probe_seed_index.json`
- Extended `Makefile`, `README.md`, `docs/README.md`, `docs/ENVIRONMENT_SANDWORM.md`, `scripts/test/check_generated_docs_presence.py`, and `scripts/tools/cloudtainer_shadow_pass.py` with the new probe-seed index command surface.
- Added the intentionally duplicated successor-safe placeholder/example id to `policy/examples_id_allowlist.json` so the unique-id check now records the preexisting continuity mirror explicitly instead of silently failing when the seed-fixture lane starts checking example ids.

### Why this mattered

The archive already knew which Rust scenario rows were weak and which of them had *some* fixture or source witness nearby. The remaining practical gap was narrower: the inheritor still could not immediately tell which weak rows already had self-contained probe examples that can be lifted almost directly into external Rust regression tests.

The smallest durable move was to commit the four missing seed probes and add one generated probe-seed index. That keeps the archive compact, avoids large artifacts, and turns the last source-only restart rows into concrete handoff material.

### Main practical result

The static weak-gap queue now reports `fixture_ready=14` and `source_ready=0`, while the new probe-seed index reports `probe_seed_ready=11` and `example_seed_only=3`. In other words, every weak Rust scenario row now has at least one example witness, and most already have a self-contained probe example rather than only a world/strategy fragment.

### Validation run in this cloudtainer

- `python3 scripts/test/check_examples_json.py` ✅
- `python3 scripts/test/check_examples_unique_ids.py` ✅
- `python3 scripts/report/build_rust_gap_witness_queue.py --write` ✅
- `python3 scripts/report/build_rust_gap_probe_seed_index.py --write` ✅
- `python3 scripts/test/check_generated_docs_presence.py` ✅
- `python3 scripts/test/check_readme_command_surface.py` ✅
- `python3 scripts/test/check_docs_index_core.py` ✅
- `python3 scripts/test/check_scripts_compile.py` ✅
- `python3 scripts/test/check_scripts_executable.py` ✅

## Additional pass: Rust gap-to-witness queue for blocked sessions

- Added one generated bridge from the Rust scenario-gap ledger to exact repo witnesses so a blocked session can hand off which weak scenarios already have seed fixtures or source anchors:
  - `scripts/report/build_rust_gap_witness_queue.py`
  - `docs/RUST_GAP_WITNESS_QUEUE.md`
  - `artifacts/reports/rust_gap_witness_queue.json`
- Extended `Makefile` and `scripts/tools/cloudtainer_shadow_pass.py` with `make update-rust-gap-witness-queue` / `make test-rust-gap-witness-queue` so the canonical blocked-session pass now refreshes not just which scenarios are weak, but also where to restart them from.
- Threaded the new queue into `README.md`, `docs/README.md`, `docs/ENVIRONMENT_SANDWORM.md`, and `scripts/test/check_generated_docs_presence.py`.

### Why this mattered

The archive already preserved where the Rust engine lives, which modules deserve attention, what behaviors the tests protect, and which scenario variants are missing or sparse. The remaining gap was practical: the next inheritor still had to rediscover where the exact seed fixtures or declarations for those gaps lived.

The smaller durable move was to preserve one generated gap-to-witness queue. It keeps the archive compact, avoids copying code or large JSON bodies, and turns several blocked-session questions into direct restart pointers.

### Main practical result

A future inheritor can now answer a sharper question immediately: for each weak or missing Rust scenario, is there already an exact example fixture to lift, only a source declaration to fixture-ize, or just a design anchor that still needs the first executable encoding?

## Additional pass: Rust semantic-contract ledger for blocked sessions

- Added one generated behavior map for the Rust test corpus so a blocked session can preserve what the tests are trying to guarantee without compiling the crate:
  - `scripts/report/build_rust_test_contracts.py`
  - `docs/RUST_TEST_CONTRACTS.md`
  - `artifacts/reports/rust_test_contracts.json`
- Extended `Makefile` and `scripts/tools/cloudtainer_shadow_pass.py` with `make update-rust-test-contracts` / `make test-rust-test-contracts` so the canonical blocked-session pass now refreshes not just source maps, but also the semantic contract ledger.
- Threaded the new ledger into `README.md`, `docs/README.md`, `docs/ENVIRONMENT_SANDWORM.md`, and `scripts/test/check_generated_docs_presence.py`.
- Tightened the shadow pass itself for this sandbox by streaming per-step output and dropping nonessential validator/policy/schema refreshes from the blocked-session loop; the pass stays smaller and more likely to finish before the sandbox cuts a long quiet run.

### Why this mattered

The archive already preserved *where* the Rust engine lives and *which modules deserve attention first*, but it still lost the more important restart context: what behavior the test corpus is protecting. That forced future inheritors to re-read many test files just to recover the contract surface before a later compiled rerun.

The smaller durable move was to preserve one generated ledger of semantic contracts. It keeps the archive compact, avoids copying Rust bodies, and tells the next implementor which invariants matter most when the real Rust machine finally comes back.

### Validation run in this cloudtainer

- `make update-rust-test-contracts` ✅
- `make test-rust-test-contracts` ✅
- `python3 ./scripts/test/check_readme_command_surface.py` ✅
- `python3 ./scripts/test/check_docs_index_core.py` ✅
- `python3 ./scripts/test/check_generated_docs_presence.py` ✅
- `python3 ./scripts/test/check_scripts_compile.py` ✅

### Main practical result

A future inheritor now gets a compact answer to a higher-value blocked-session question: not just “what files and modules exist,” but “which semantic promises the Rust tests were enforcing.” That should shorten the first real `cargo test` comeback cycle and reduce blind rerun ordering.

## Additional pass: canonical cloudtainer shadow-pass command

- Added one canonical blocked-session command surface so future inheritors can recover the productive local subset in one step instead of rebuilding an ad hoc command list each time the cloudtainer still lacks Rust tooling:
  - `scripts/tools/cloudtainer_shadow_pass.py`
  - `make cloudtainer-shadow-pass`
  - `artifacts/process/` receipt emitted by the command
- Added one inheritor-facing doctrine note and threaded the command into the existing Rust-blocked environment guidance:
  - `docs/LIBRARY/topics/rust_blocked_cloudtainer_sessions_should_ship_one_canonical_shadow_pass_command.md`
  - refreshed `docs/ENVIRONMENT_SANDWORM.md`
  - refreshed `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - refreshed `docs/BUCKET.md`
  - refreshed `README.md`
- The command deliberately stays narrow: it records the current tool boundary, refreshes the static Rust surface and compact inventories, reruns the local Python/doc checks that still matter, and writes one tiny receipt rather than widening into a fake full gate.

### Why this mattered

The previous blocked-toolchain doctrine explained *what* kind of work remained productive, but it still left too much operational choice to each inheritor. That meant repeated session startup cost: rediscover the safe commands, decide the order again, and then summarize the result in prose.

The better durable move was to preserve one canonical blocked-session command surface. It keeps the archive small, reduces command drift, and makes the useful local subset visible without pretending that Rust runtime evidence has been refreshed.

### Validation run in this cloudtainer

- `make cloudtainer-shadow-pass` ✅ (`doctor_probe` blocked only at missing `cargo` / `rustc`; all shadow-work steps pass)
- `python3 ./scripts/test/check_make_help_surface.py` ✅
- `python3 ./scripts/test/check_readme_command_surface.py` ✅
- `python3 ./scripts/test/check_scripts_compile.py` ✅
- `python3 ./scripts/test/check_scripts_executable.py` ✅

### Main practical result

A future inheritor no longer has to reconstruct the productive blocked-session workflow from scattered notes. The archive now keeps one explicit command that says: record the boundary, refresh the small durable maps, rerun the Python-shadow lane, and leave one compact receipt for the next steward.

## Additional pass: rust-blocked static surface inventory + Python-shadow workflow

- Added one generated static navigation artifact for `gr_engine` so a Rust-blocked session can still recover module boundaries, public surfaces, dependency waves, and hotspot files without invoking `cargo`:
  - `scripts/report/build_rust_surface_inventory.py`
  - `docs/RUST_SURFACE_INVENTORY.md`
  - `artifacts/reports/rust_surface_inventory.json`
- Added one inheritor-facing doctrine note and one compact process note explaining how blocked-toolchain sessions should stay productive without bloating the archive:
  - `docs/LIBRARY/topics/rust_blocked_cloudtainer_sessions_should_shift_to_static_surface_mapping_and_python_shadow_work.md`
  - `artifacts/process/2026-03-22-rust-blocked-shadow-work-pass.md`
- Extended `Makefile`, `README.md`, and the command/artifact inventories so the new surface is regenerable through `make update-rust-surface-inventory` / `make test-rust-surface-inventory` rather than living as a one-off file.
- Extended `docs/RESEARCH_SOURCES.md` through `RS-OPS-010` and threaded the blocked-toolchain workflow into `docs/ENVIRONMENT_SANDWORM.md`, `docs/RESEARCH_AGENDA.md`, `docs/RESEARCH_OPINIONS.md`, `docs/BUCKET.md`, and `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`.

### Why this mattered

The archive already knew that the cloudtainer was blocked on missing `cargo` / `junest`, but it still left too much of the practical question unanswered: what should a future inheritor do with a session that cannot run Rust today?

The smallest durable answer was not another large toolchain experiment. It was one compact navigation map plus one explicit workflow rule: recover the Rust surface statically, keep the Python-shadow lanes moving, and hold runtime-semantic claims behind the blocked Rust boundary until a later machine can rerun them.

### Validation run in this cloudtainer

- `make doctor` -> blocked only at missing `cargo` / `junest`
- `make test-quick` -> control tests pass; stop only at `rust_lib_tests` because `tools/rust_exec.sh` cannot find JuNest
- `make update-rust-surface-inventory` ✅
- `make test-rust-surface-inventory` ✅
- `make update-command-inventory` ✅
- `make update-artifact-buckets` ✅
- `make report-artifact-summary` ✅
- `python3 scripts/test/check_docs_index_core.py` ✅
- `python3 scripts/test/check_readme_command_surface.py` ✅
- `python3 scripts/test/check_generated_docs_presence.py` ✅
- `python3 scripts/test/check_research_docs.py` ✅
- `python3 -m unittest discover -s tests/control -p 'test_*.py'` ✅
- `python3 -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli grlab.tests.test_certify_schema` ✅

### Main practical result

A future inheritor no longer has to spend the first blocked session rediscovering where the Rust engine lives or whether there is any productive local work left. The archive now keeps one tiny map of the Rust surface and one explicit doctrine for what can still advance locally without pretending that Python has become the simulation truth.

## Additional pass: successor-safe ceremony receipt package head pointers

- Added one compact discovery discipline for successor-safe ceremony receipt packages so inheritors can find the live authoritative package root without opening the full lineage chain first:
  - `schemas/successor_safe_ceremony_receipt_package_head.schema.json`
  - `examples/snapshots/successor_safe_ceremony_receipt_example.package_head.json`
  - `docs/LIBRARY/topics/successor_safe_ceremony_receipt_package_lineages_should_ship_compact_head_pointers.md`
  - `artifacts/process/successor_safe_ceremony_receipt_package_head_receipt_20260322.json`
- Extended `scripts/tools/successor_safe_ceremony_receipt.py` with a `head` subcommand that compares the current authoritative package manifest, the lineage record, the live review verdict, and the live citation advisory and emits one explicit discovery object with registered relation semantics such as `latest-version`, `version-history`, `status`, and `predecessor-version`.
- Updated `scripts/test/check_successor_safe_ceremony_receipt.py` so the worked example must keep the package-head snapshot derivable from the tool rather than hand-edited.
- Extended `docs/RESEARCH_SOURCES.md` through `RS-GR-539` and threaded the package-head discipline into `docs/RESEARCH_AGENDA.md`, `docs/RESEARCH_OPINIONS.md`, `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`, and `docs/BUCKET.md`.
- Main practical result: the archive now keeps not just the package chain and its current authoritative head, but also one tiny object that tells a fresh steward where the live package root is right now and which status artifacts govern it.

- 2026-03-22: Added a compact package-manifest layer for successor-safe ceremony receipt packages.
  - Added:
    - `schemas/successor_safe_ceremony_receipt_package_manifest.schema.json`
    - `examples/snapshots/successor_safe_ceremony_receipt_example.package_manifest.json`
    - `docs/LIBRARY/topics/successor_safe_ceremony_receipt_packages_should_ship_compact_package_manifests.md`
    - `artifacts/process/successor_safe_ceremony_receipt_package_manifest_receipt_20260322.json`
  - Extended `scripts/tools/successor_safe_ceremony_receipt.py` with a `manifest` subcommand that names the current authoritative receipt artifacts and attaches file-level SHA-256 digests and byte counts for each component.
  - Updated `scripts/test/check_successor_safe_ceremony_receipt.py` so the worked package manifest must stay reproducible from the committed receipt, markdown, locator, assessment, disposition, remediation, authorization, promotion, review watch, review verdict, and citation advisory snapshots.

- 2026-03-22: Added a compact review-verdict layer for successor-safe ceremony receipt packages.
  - Added:
    - `schemas/successor_safe_ceremony_receipt_review_verdict.schema.json`
    - `examples/snapshots/successor_safe_ceremony_receipt_example.review_verdict.json`
    - `docs/LIBRARY/topics/successor_safe_ceremony_receipt_review_watches_should_collapse_to_explicit_review_verdicts.md`
    - `artifacts/process/successor_safe_ceremony_receipt_review_verdict_receipt_20260322.json`
  - Extended `scripts/tools/successor_safe_ceremony_receipt.py` with a `review` subcommand that evaluates a compact review watch into one explicit keep-citing versus reopen-now verdict using the as-of date and any observed trigger codes.
  - Updated `scripts/test/check_successor_safe_ceremony_receipt.py` so the worked example stays citable under a clean same-day review while scaffolded or trigger-fired review states suspend claim-ready citation immediately.

- 2026-03-22: Added a compact review-watch layer for successor-safe ceremony receipt packages.
  - Added:
    - `schemas/successor_safe_ceremony_receipt_review_watch.schema.json`
    - `examples/snapshots/successor_safe_ceremony_receipt_example.review_watch.json`
    - `docs/LIBRARY/topics/successor_safe_ceremony_receipt_authorizations_should_ship_compact_review_watches.md`
    - `artifacts/process/successor_safe_ceremony_receipt_review_watch_receipt_20260322.json`
  - Extended `scripts/tools/successor_safe_ceremony_receipt.py` with a `watch` subcommand that collapses authorization + promotion into one freshness boundary carrying the reviewed-on date, no-later-than review interval, reopen-trigger codes, and required regeneration sequence.
  - Updated `scripts/test/check_successor_safe_ceremony_receipt.py` so the worked example must stay on an active watch while scaffolded non-authorized receipts reopen immediately.

- 2026-03-22: Added a compact promotion-record layer for successor-safe ceremony receipt packages.
  - Added:
    - `schemas/successor_safe_ceremony_receipt_promotion.schema.json`
    - `examples/snapshots/successor_safe_ceremony_receipt_placeholder.json`
    - `examples/snapshots/successor_safe_ceremony_receipt_example.promotion.json`
    - `docs/LIBRARY/topics/successor_safe_ceremony_receipt_authorizations_should_ship_compact_promotion_records.md`
    - `artifacts/process/successor_safe_ceremony_receipt_promotion_receipt_20260322.json`
  - Extended `scripts/tools/successor_safe_ceremony_receipt.py` with a `promote` subcommand that compares prior and current assessment/authorization state, names closed/carried/newly opened findings, and records whether a receipt package truly promoted to claim-ready citation.
  - Updated `scripts/test/check_successor_safe_ceremony_receipt.py` so the worked example must stay reproducibly promotable from a scaffolded placeholder package without reopening findings.

- 2026-03-22: Added a compact authorization layer for successor-safe ceremony receipt packages.
  - Added:
    - `schemas/successor_safe_ceremony_receipt_authorization.schema.json`
    - `examples/snapshots/successor_safe_ceremony_receipt_example.authorization.json`
    - `docs/LIBRARY/topics/successor_safe_ceremony_receipt_remediation_plans_should_end_in_explicit_authorization_decisions.md`
    - `artifacts/process/successor_safe_ceremony_receipt_authorization_receipt_20260322.json`
  - Extended `scripts/tools/successor_safe_ceremony_receipt.py` with an `authorize` subcommand that collapses assessment + locator + disposition + remediation into one explicit claim-ready authorization decision with basis checks, terms and conditions, and a review trigger.
  - Updated `scripts/test/check_successor_safe_ceremony_receipt.py` so the worked example must stay authorized for claim-ready citation while scaffolded placeholder receipts remain explicitly unauthorized.

- Added two compact inheritor-facing research notes:
  - `docs/LIBRARY/topics/encounter_topology_and_bridge_structure_are_world_contracts_not_background_graph_choice.md`
  - `docs/LIBRARY/topics/homophily_and_tie_rewiring_rules_are_world_contracts_not_harmless_social_noise.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-183` (hub / bridge position, degree heterogeneity, and assortativity can change whether cooperation survives),
  - `RS-GR-184` (positive reciprocity, negative reciprocity, and punishment operate on real community networks),
  - `RS-GR-185` (dynamic networks can support cooperation through repulsion and selective separation rather than friendship reward), and
  - `RS-GR-186` (homophily and prior acquaintance can shape network formation more strongly than reciprocal trust).
- Added one compact local receipt:
  - `artifacts/process/encounter_topology_and_tie_rewiring_receipt_20260322.json`
- Updated the active inheritor/planning surfaces in:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `artifacts/process/2026-03-21-research-pass.md`

### Research / inheritor insight

The archive had already separated direct reciprocity from exit, reputation, sanctions, repair, scarcity, risk, and concurrency.
This pass adds the missing network-encounter layer underneath them.
A benchmark can look more or less Golden-Rule-like because cooperators occupy hubs, because bridge regions block defectors, or because homophily and selective separation quietly sort agents into easier neighborhoods.
So the next implementor should publish **encounter topology** and **tie-formation / rewiring policy** before treating observed cooperation changes as moral improvement.

### Current local checks

- `python3 scripts/test/check_research_docs.py` ✅
- `python3 scripts/test/check_docs_index_core.py` ✅
- `python3 scripts/test/check_markdown_links.py` remains advisory because of inherited `/workspace/...` and legacy false-positive issues.

- Added two compact inheritor-facing research notes:
  - `docs/LIBRARY/topics/concurrent_relationship_portfolios_are_world_contracts_not_background_complexity.md`
  - `docs/LIBRARY/topics/cross_game_linkage_and_crosstalk_are_world_contracts_not_memory_accidents.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-180` (concurrent human games reduce cooperation relative to single-game controls and depend on same-partner versus different-partner topology),
  - `RS-GR-181` (linked multichannel games can borrow leverage from one lane to sustain cooperation in another), and
  - `RS-GR-182` (crosstalk across concurrent games impedes direct reciprocity and changes which forgiving strategies survive).
- Added one compact local receipt:
  - `artifacts/process/concurrent_portfolio_and_crosstalk_receipt_20260322.json`
- Updated the active inheritor/planning surfaces in:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `artifacts/process/2026-03-21-research-pass.md`

### Research / inheritor insight

The archive had already separated direct reciprocity from exit, reputation, sanctions, repair, scarcity, and risk.
This pass adds the missing concurrency layer underneath them.
A benchmark can look more or less Golden-Rule-like because agents carry several obligations at once, because leverage crosses lanes, or because memory spillovers contaminate retaliation.
So the next implementor should publish **concurrent portfolio structure** and **cross-lane linkage / crosstalk policy** before treating observed cooperation changes as moral improvement.

### Current local checks

- `python3 scripts/test/check_research_docs.py` ✅
- `python3 scripts/test/check_docs_index_core.py` ✅
- `python3 scripts/test/check_markdown_links.py` remains advisory because of inherited `/workspace/...` and legacy false-positive issues.

- Added two compact inheritor-facing research notes:
  - `docs/LIBRARY/topics/shared_shock_structure_and_risk_pooling_are_world_contracts_not_payoff_noise.md`
  - `docs/LIBRARY/topics/formal_insurance_and_informal_solidarity_are_separate_world_contracts_not_one_safety_net.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-176` (stochastic risk can raise cooperation without strong evidence that informal risk sharing is the mechanism),
  - `RS-GR-177` (collective versus individual shocks can change intra-community cooperation),
  - `RS-GR-178` (formal insurance availability can reduce private solidarity transfers), and
  - `RS-GR-179` (formal fallback can crowd out informal transfers only modestly on average in a real transfer network).
- Added one compact local receipt:
  - `artifacts/process/risk_structure_and_fallback_contracts_receipt_20260321.json`
- Updated the active inheritor/planning surfaces in:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `artifacts/process/2026-03-21-research-pass.md`

### Research / inheritor insight

The archive had already separated scarcity, monitoring cost, identity, and helping semantics.
This pass adds the missing fallback layer underneath them.
A risk-bearing benchmark can look more cooperative because shocks became shared or because losses got easier to smooth, not because agents became more Golden-Rule-like.
A helping benchmark can also shift because formal protection changes deservingness judgments or partially substitutes for informal solidarity.
So the next implementor should publish **shock structure** and **fallback institution design** before treating observed cooperation or helping changes as moral improvement.

### Current local checks

- `python3 scripts/test/check_research_docs.py` ✅
- `python3 scripts/test/check_docs_index_core.py` ✅
- `python3 scripts/test/check_markdown_links.py` remains advisory because of inherited `/workspace/...` and legacy false-positive issues.

- Re-read the retained extortion / anti-extortion artifacts and distilled one compact local summary receipt at `artifacts/process/extortion_frontier_reread_20260321.json`.
- Added two compact inheritor-facing research notes:
  - `docs/LIBRARY/topics/voluntary_repeated_pd_with_error_and_exit_can_replace_retaliation_with_leaving.md`
  - `docs/LIBRARY/topics/repeated_game_worlds_should_publish_move_order_and_action_visibility_contract.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-132` (Izquierdo, Izquierdo & Boyd, 2026), and
  - `RS-GR-133` (LaPorte, Pracher & Pal, 2026).
- Updated the active inheritor/planning surfaces in:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `artifacts/process/2026-03-21-research-pass.md`

### Research / inheritor insight

The local extortion frontier now reads less like one scalar search problem and more like an institution problem.
The retained artifacts already show that short-horizon wins evaporate on the long lane and that current exit wins are still 4-round fixed-dyad artifacts.
The new literature tightens the next move: once leaving under noise is real, classical retaliatory winners may disappear, and once action visibility changes, simultaneous-play conclusions may stop transferring cleanly.
So the next implementor should widen the **world contract** before widening the search budget.

### Current local checks

- `python3 scripts/test/check_research_docs.py` ✅
- `python3 scripts/test/check_markdown_links.py` still reports inherited false positives / environment-specific paths (`/workspace/...` links and code-like `K_[a,b](h)` patterns), so it was not used as a clean regression signal for this pass.
- `python3 scripts/test/check_docs_index_core.py` ✅

## Additional pass: transient edge counts + pre-closure mechanism surface

### What changed

- Extended `grlab certify` so `transition_graph_diagnostics` now declares exact `expected_transition_counts_before_any_closed_class_entry_from_initial_distribution`.
- Extended each `closed_class_entry_probabilities_from_initial_distribution` item with `conditional_expected_transition_counts_before_entry_from_initial_distribution`.
- Bumped the typed result to `schema_version = 21` while leaving `anti_vampire_scorecard.scorecard_version = 13` unchanged, because this pass sharpens the graph/transient diagnostics without changing the scorecard contract itself.

### Why it matters

- The archive already preserved basin weights, exact long-run basin outcomes, entry timing, pre-closure cumulative payoff burden, and pre-closure state-visit counts. It still hid *which transitions actually carried that burden*.
- Future inheritors can now read the transient mechanism directly from the retained object instead of reconstructing it from the kernel.

### Current local checks

- `python3 -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli grlab.tests.test_certify_schema`
- `python3 scripts/formal/check_certify_invariants.py`
- `make update-schema-inventory update-artifact-buckets report-artifact-summary`
- `make test-schema-json test-schema-inventory test-artifact-buckets test-reports-json test-generated-docs test-research-docs`


## Additional pass: certify transient visit counts + pre-closure path-shape surface

### What changed

- Extended `grlab certify` so `transition_graph_diagnostics` now declares exact `expected_visit_counts_before_any_closed_class_entry_from_initial_distribution`.
- Extended each `closed_class_entry_probabilities_from_initial_distribution` item with `conditional_expected_visit_counts_before_entry_from_initial_distribution`.
- Bumped the typed result to `schema_version = 20` while leaving `anti_vampire_scorecard.scorecard_version = 13` unchanged, because this pass sharpens the graph/transient diagnostics without changing the scorecard contract itself.

### Why it matters

- The archive already preserved basin weights, exact long-run basin outcomes, entry timing, and pre-closure cumulative payoff burden. It still hid *which transient states actually carried that burden*.
- Future inheritors can now read the transient path shape directly from the retained object instead of reconstructing it from the kernel.

### Current local checks

- `python3 -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli grlab.tests.test_certify_schema`
- `python3 scripts/formal/check_certify_invariants.py`
- `make update-schema-inventory update-artifact-buckets report-artifact-summary`
- `make test-schema-json test-schema-inventory test-artifact-buckets test-reports-json test-generated-docs test-research-docs`


## Additional pass: transient payoff surface + pre-closure burden lane

### What changed

- Extended `grlab certify` so `transition_graph_diagnostics` now includes exact `expected_cumulative_payoff_a_before_any_closed_class_entry_from_initial_distribution` / `expected_cumulative_payoff_b_before_any_closed_class_entry_from_initial_distribution`.
- Extended each `closed_class_entry_probabilities_from_initial_distribution` item with `conditional_expected_cumulative_payoff_a_before_entry_from_initial_distribution` / `conditional_expected_cumulative_payoff_b_before_entry_from_initial_distribution`.
- Kept `anti_vampire_scorecard.scorecard_version = 13` unchanged and bumped only the top-level result contract to `schema_version = 19`, because this pass improves transient-payoff readability without changing the scorecard contract itself.

### Why it matters

The previous archive pass could tell a future inheritor which recurrent basins were entered, with what probability, how long entry took, and what long-run world each basin implied, but it still hid who paid the transient cost on the way there. This pass closes that gap. A retained certify result now says not just where the declared opening distribution ends up and how long entry takes, but also which side bears the pre-closure payoff burden overall and conditional on each basin.

## Additional pass: closed-class entry timing + transient horizon surface

### What changed

- Extended `grlab certify` so `transition_graph_diagnostics` now includes `expected_steps_to_any_closed_class_from_initial_distribution`.
- Extended each `closed_class_entry_probabilities_from_initial_distribution` item with `conditional_expected_entry_steps_from_initial_distribution`.
- Kept `anti_vampire_scorecard.scorecard_version = 13` unchanged and bumped only the top-level result contract to `schema_version = 18`, because this pass improves transient-horizon readability without changing the scorecard contract itself.

### Why it matters

The previous archive pass could tell a future inheritor which recurrent basins were entered, with what probability, and what long-run world each basin implied, but it still hid the transient horizon. This pass closes that gap. A retained certify result now says both where the declared opening distribution ends up and how long it typically takes to get there, so multi-basin cases no longer need hand reconstruction of the transient story.

## Additional pass: exact asymptotic surface + Cesàro drift witness

### What changed

- Extended `grlab certify` with a top-level exact `asymptotic_distribution_from_initial_distribution` derived from the declared closed-class decomposition.
- Added explicit `asymptotic_avg_payoff_a_from_initial_distribution` / `asymptotic_avg_payoff_b_from_initial_distribution` so reducible-chain long-run payoffs no longer have to be reconstructed from the basin decomposition by hand.
- Added `asymptotic_distribution_method = closed_class_exact_mixture_from_initial_distribution` and `steady_state_distribution_l1_distance_to_asymptotic_distribution` so future inheritors can see directly whether the retained `steady_state_distribution` is already exact or is only a finite Cesàro approximation.
- Kept `anti_vampire_scorecard.scorecard_version = 13` unchanged and bumped only the top-level result contract to `schema_version = 17`, because this pass improves the top-level asymptotic reading without changing the scorecard contract itself.

### Why it matters

The previous archive pass exposed the exact basin-conditioned asymptotic decomposition, but the top-level payload still left future sessions comparing that exact decomposition to the retained `steady_state_distribution` by eye. This pass closes that gap. A retained certify result now carries both the exact asymptotic mixture and a compact mismatch witness, so reducible-chain results are harder to misread as exact stationary facts when they are really finite fallback approximations.

## Additional pass: closed-class asymptotic decomposition + basin outcome surface

### What changed

- Extended `grlab certify` so `transition_graph_diagnostics` now includes `closed_class_asymptotic_decomposition_from_initial_distribution`.
- Each basin item now carries exact `entry_probability`, basin-local `class_stationary_distribution`, `weighted_steady_state_contribution`, and basin-conditioned `class_avg_payoff_a` / `class_avg_payoff_b`.
- Kept `anti_vampire_scorecard.scorecard_version = 13` unchanged and bumped only the top-level result contract to `schema_version = 16`, because this pass improves reducible-chain interpretability without changing the scorecard contract itself.
- Tightened solver / CLI / schema / formal checks around the new basin outcome surface; in reducible split-basin cases, the decomposition now exposes the exact asymptotic mixture even when the retained fallback `steady_state_distribution` remains a finite Cesàro approximation.

### Why it matters

The previous archive pass could tell a future inheritor that several recurrent basins existed and how much opening-distribution mass entered each one, but it still did not say what long-run outcome each basin implied. This pass closes that gap. Multi-basin results are now readable as explicit weighted mixtures of basin-conditioned asymptotic worlds rather than only as graph structure plus a separate aggregate steady-state vector.

## Additional pass: closed-class entry probabilities + initial-basin weights

### What changed

- Extended `grlab certify` so `transition_graph_diagnostics` now includes exact `closed_class_entry_probabilities_from_initial_distribution`.
- Added `multiple_closed_classes_with_positive_entry_probability_from_initial_distribution` so future sessions can see whether a declared opening distribution actually splits mass across several recurrent basins or only has several graph-reachable basins in principle.
- Kept `anti_vampire_scorecard.scorecard_version = 13` unchanged and bumped only the top-level result contract to `schema_version = 15`, because the scorecard fields did not change in this pass.
- Added a mixed-opening regression case whose declared `p0` distribution splits `0.5 / 0.5` across `CC` and `DD`, plus coverage for the existing `WSLS` vs `AlwaysC` multi-basin-but-single-entry case.

### Research / inheritor insight

The previous graph-diagnostics pass told future inheritors which recurrent basins existed and which were graph-reachable from the declared opening support.
That was enough to explain reducibility, but not enough to explain *weight*.
This pass closes that gap compactly: a retained certify object now says whether a multi-basin chain is merely structurally multi-basin or whether the declared opening distribution genuinely allocates positive probability mass to more than one recurrent basin.

### Current local checks

- `python3 -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli grlab.tests.test_certify_schema`
- `python3 scripts/formal/check_certify_invariants.py`
- `make update-schema-inventory update-artifact-buckets report-artifact-summary`
- `make test-schema-json test-schema-inventory test-artifact-buckets test-reports-json test-generated-docs test-research-docs`


## Additional pass: certify transition-kernel contract + explicit 4×4 kernel surface

### What changed

- Extended `grlab certify` so the result now declares `transition_kernel_contract_ref` at both the top level and inside `anti_vampire_scorecard`.
- Added a compact top-level `transition_matrix` field carrying the actual 4×4 row-stochastic kernel used for the run.
- Bound a canonical immutable transition-kernel contract (`memory_one_state_product_kernel_v1`) covering:
  - declared `state_order`,
  - row-stochastic matrix orientation,
  - the per-row product formulas from memory-one probabilities to next-state probabilities,
  - and the fact that strategy B's condition indices are mirrored into A-view before kernel construction.
- Tightened `pairing_ref.pairing_fingerprint_sha256` so ordered certify-object identity now depends on this transition-kernel contract too.
- Added / updated coverage in:
  - `grlab/tests/test_certify_solver.py`
  - `grlab/tests/test_certify_cli.py`
  - `grlab/tests/test_certify_schema.py`
  - `scripts/formal/check_certify_invariants.py`
  - `schemas/certify_memory_one_result.schema.json`
  - `docs/LIBRARY/topics/anti_vampire_scorecard_spec.md`
  - `docs/BUCKET.md`
  - `CHANGELOG.md`

### Research / inheritor insight

The previous passes made the certify surface reproducible with respect to strategy identity, stage game, screening contract, sampling plans, interval semantics, proxy semantics, steady-state semantics, and opening-state semantics.
But the actual 4×4 Markov kernel still had to be reconstructed from those ingredients, and its construction rule still lived implicitly in Python.
The new contract plus the explicit `transition_matrix` closes that gap compactly.

Future inheritors should now treat a retained certify result as living under nine compact declared identities at once: screening contract, ordered strategies, stage-game/state basis, sampling plans, interval semantics, proxy-measurement semantics, steady-state solver/fallback semantics, opening-distribution semantics, and transition-kernel semantics.

### Current local checks

- `python3 -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli grlab.tests.test_certify_schema`
- `python3 scripts/formal/check_certify_invariants.py`
- `make update-schema-inventory update-artifact-buckets report-artifact-summary`
- `make test-schema-json test-schema-inventory test-artifact-buckets test-reports-json test-generated-docs test-research-docs`


## Additional pass: certify opening-distribution contract + initial-state semantics identity

### What changed

- Extended `grlab certify` so the result now declares `opening_distribution_contract_ref` at both the top level and inside `anti_vampire_scorecard`.
- Bound a canonical immutable opening-distribution contract (`memory_one_independent_p0_product_v1`) covering:
  - independent Bernoulli opening actions,
  - `strategy_a.p0` / `strategy_b.p0` as the opening cooperation probabilities,
  - the declared `state_order`,
  - and the exact product formulas for `CC`, `CD`, `DC`, and `DD`.
- Tightened `pairing_ref.pairing_fingerprint_sha256` so ordered certify-object identity now depends on this opening-distribution contract too.
- Added / updated coverage in:
  - `grlab/tests/test_certify_solver.py`
  - `grlab/tests/test_certify_cli.py`
  - `grlab/tests/test_certify_schema.py`
  - `scripts/formal/check_certify_invariants.py`
  - `schemas/certify_memory_one_result.schema.json`
  - `docs/LIBRARY/topics/anti_vampire_scorecard_spec.md`
  - `docs/BUCKET.md`
  - `CHANGELOG.md`

### Research / inheritor insight

The previous passes made the certify surface reproducible with respect to the declared strategy pair, stage game, screening spec, sampling plans, interval semantics, proxy-measurement semantics, and steady-state solver/fallback semantics.
But the opening distribution itself still depended on an implicit construction rule in Python.
A future session could have changed the independence assumption or the `p0`-to-state mapping and retained a result that still looked comparable at a glance.
The new contract closes that gap compactly.

Future inheritors should now treat a retained certify result as living under eight compact declared identities at once: screening contract, ordered strategies, stage-game/state basis, sampling plans, interval semantics, proxy-measurement semantics, steady-state solver/fallback semantics, and opening-distribution semantics.

### Current local checks

- `python3 -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli grlab.tests.test_certify_schema`
- `python3 scripts/formal/check_certify_invariants.py`
- `make update-schema-inventory update-artifact-buckets report-artifact-summary`
- `make test-schema-json test-schema-inventory test-artifact-buckets test-reports-json test-generated-docs test-research-docs`


## Additional pass: certify steady-state contract + solver/fallback semantics identity

### What changed

- Extended `grlab certify` so the result now declares `steady_state_contract_ref` at both the top level and inside `anti_vampire_scorecard`.
- Bound a canonical immutable steady-state contract (`memory_one_stationary_or_cesaro_v1`) covering:
  - exact stationary solve method (`gaussian_elimination_partial_pivot_4x4`),
  - pivot tolerance,
  - zero-cleanup and negative-mass tolerances,
  - singular / ill-conditioned fallback trigger,
  - fallback method (`cesaro_average_from_declared_initial_distribution`),
  - and the fact that fallback length comes from `screening_spec.steady_state.cesaro_fallback_steps`.
- Tightened `pairing_ref.pairing_fingerprint_sha256` so ordered certify-object identity now depends on this steady-state contract too.
- Added / updated coverage in:
  - `grlab/tests/test_certify_solver.py`
  - `grlab/tests/test_certify_cli.py`
  - `grlab/tests/test_certify_schema.py`
  - `scripts/formal/check_certify_invariants.py`
  - `schemas/certify_memory_one_result.schema.json`
  - `docs/LIBRARY/topics/anti_vampire_scorecard_spec.md`
  - `docs/BUCKET.md`
  - `CHANGELOG.md`

### Research / inheritor insight

The previous passes made the certify surface reproducible with respect to the declared strategy pair, stage game, screening spec, sampling plans, interval semantics, and proxy-measurement semantics.
But the top-level payoffs and occupancy vector still depended on solver semantics that were only implicit in Python.
A future session could have changed the singularity tolerance or fallback rule and retained a result that still looked comparable at a glance.
The new contract closes that gap compactly.

Future inheritors should now treat a retained certify result as living under seven compact declared identities at once: screening contract, ordered strategies, stage-game/state basis, sampling plans, interval semantics, proxy-measurement semantics, and steady-state solver/fallback semantics.

### Current local checks

- `python3 -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli grlab.tests.test_certify_schema`
- `python3 scripts/formal/check_certify_invariants.py`
- `make update-schema-inventory update-artifact-buckets report-artifact-summary`
- `make test-schema-json test-schema-inventory test-artifact-buckets test-reports-json test-generated-docs test-research-docs`


## Additional pass: certify proxy-measurement contract + semantics identity

### What changed

- Extended `grlab certify` so the result now declares `proxy_measurement_contract_ref` at both the top level and inside `anti_vampire_scorecard`.
- Bound a canonical immutable proxy-semantics contract (`anti_vampire_proxy_measurement_v1`) covering:
  - pairwise fairness sign convention (`avg_payoff_b_minus_avg_payoff_a`),
  - ecology member sign convention (`avg_payoff_a_minus_avg_payoff_b`),
  - equal-weight ecology pool aggregation,
  - canonical recovery-shock semantics,
  - repair-offer event semantics,
  - and repair-abuse event semantics.
- Tightened `pairing_ref.pairing_fingerprint_sha256` so ordered certify-object identity now depends on this proxy-measurement contract as well.
- Added / updated coverage in:
  - `grlab/tests/test_certify_solver.py`
  - `grlab/tests/test_certify_cli.py`
  - `grlab/tests/test_certify_schema.py`
  - `scripts/formal/check_certify_invariants.py`
  - `schemas/certify_memory_one_result.schema.json`
  - `docs/LIBRARY/topics/anti_vampire_scorecard_spec.md`
  - `docs/BUCKET.md`
  - `CHANGELOG.md`

### Research / inheritor insight

The previous passes made the certify surface reproducible with respect to who was played, under what stage game, with which screening contract, which sampling plan, and which interval semantics.
But one quiet comparison trap remained: the proxy *measurement semantics themselves* were still implicit.
A future session could keep all those declared refs the same while changing the sign of `payoff_gap`, changing ecology aggregation from equal-weight mean to something else, or changing what exactly counts as a repair-abuse event.
The new contract closes that gap compactly.

Future inheritors should now treat a retained certify result as living under six compact declared identities at once: screening contract, ordered strategies, stage-game/state basis, sampling plans, interval semantics, and proxy-measurement semantics.

### Current local checks

- `python3 -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli grlab.tests.test_certify_schema` ✅

## 2026-03-20 — Research Pass (Uncertainty Contract Ref + Interval Semantics Provenance)

- Extended `grlab certify` so the retained result now declares compact `uncertainty_contract_ref` objects at both the top level and inside the anti-vampire scorecard.
- Bound the current interval semantics into one explicit immutable surface:
  - ecology uncertainty currently means a two-sided normal-approximation interval around the replicated-rollout mean with the declared z-multiplier,
  - repair uncertainty currently means a Wilson interval around the repair-offer abuse rate.
- Tightened `pairing_ref.pairing_fingerprint_sha256` so the ordered certify-object identity now depends on that uncertainty contract too, not only on the strategies, stage game, screening spec, and sampling plans.
- Updated `schemas/certify_memory_one_result.schema.json` plus the certify solver / CLI / schema tests for `schema_version = 9` and `scorecard_version = 9`.

### Research / inheritor insight

The previous passes fixed hidden drift in the strategy pair, stage game, screening spec, sampling plan, and threshold interpretation.
One quiet comparison trap still remained: two runs could keep all of those declared identities while changing the interval semantics in code, for example by switching the ecology half-width rule or the repair interval method.
That would change the meaning of `gate_stability`, `threshold_decision_state`, and the reported uncertainty bands while leaving the result looking comparable at a glance.

The new `uncertainty_contract_ref` closes that gap compactly.
Future comparisons should now treat a retained certify result as living under five compact declared identities:
1. the effective screening contract,
2. the ordered strategy pair,
3. the stage-game / state-order basis,
4. the rollout sampling plans,
5. the interval-semantics contract used to interpret the noisy proxy estimates.

### Current local checks

- `python3 -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli grlab.tests.test_certify_schema` ✅


## 2026-03-20 — Research Pass (Sampling-Plan Refs + Seed-Schedule Provenance)

### What changed

- Extended `grlab certify` so the anti-vampire scorecard now publishes compact `ecology_sampling_ref` and `repair_sampling_ref` objects.
- Each ref carries a stable `sampling_plan_id`, declared `estimate_kind`, explicit arithmetic-progression seed schedule (`seed_base`, `seed_stride`), and immutable `sampling_plan_fingerprint_sha256` computed over the effective rollout plan.
- Tightened `pairing_ref.pairing_fingerprint_sha256` so the ordered certify-object identity now depends on the effective Monte Carlo sampling plans as well as the declared screening contract, ordered strategy pair, and stage-game basis.
- Updated the handoff doctrine in `docs/LIBRARY/topics/anti_vampire_scorecard_spec.md` and refreshed the formal/schema/report surfaces after the new refs landed.

### Research / inheritor insight

The archive already exposed the noisy proxy estimates and their current intervals, but it still left one quiet reproducibility trap open: the same strategy pair and the same screening spec could, in principle, be rerun under a different replicate seed schedule while still looking like the same scientific object at a glance.

The new sampling-plan refs close that gap compactly. The archive does **not** need to keep every replicate seed or every replicate trace; it only needs to declare the seed schedule that made the retained estimate true. Future inheritors should therefore treat a certify result as depending on four compact declared identities at once: the effective screening contract, the ordered strategy pair, the stage-game/state-order basis, and the rollout sampling plan.

### Current local checks

- `python3 -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli grlab.tests.test_certify_schema` ✅
- `python3 scripts/formal/check_certify_invariants.py` ✅
- `make update-schema-inventory update-artifact-buckets report-artifact-summary` ✅
- `make test-schema-json test-schema-inventory test-artifact-buckets test-reports-json test-generated-docs test-research-docs` ✅


# AGENT LOG

## 2026-03-20 — Research Pass (Uncertainty-Aware Screening Stability Overlay)

- Extended `grlab certify` so the anti-vampire `screening_contract` no longer stops at raw intervals plus a point-estimate `gate_pass`; it now also states whether the current binding decision surface is `pass`, `fail`, or `borderline`, and whether that decision is `stable` under the current uncertainty summary.
- Added `binding_gate_status` and `gate_stability` at the contract level, plus per-check `estimate_kind`, interval metadata, and `threshold_decision_state` so inheritors can see exactly why a check is sharp, noisy, or still semantically pending.
- Kept the current gate semantics narrow and honest: `gate_pass` still means the declared point-estimate gate passed, while `binding_gate_status = borderline` now marks cases where the noisy-ecology CI still crosses the active binding threshold.
- Refreshed `schemas/certify_memory_one_result.schema.json` to `schema_version = 7`, bumped the scorecard contract to `scorecard_version = 7`, and tightened solver / CLI / schema coverage with a dedicated borderline-threshold test.

### Why this matters

The previous pass made the payload more honest about uncertainty, but it still left the inheritor to decide whether a pass/fail was sharp or only an artifact of reading a point estimate next to an interval.

This pass closes that usability gap without pretending to solve sequential sampling or final world semantics. The certify lane now cleanly separates three questions:
- what did the current point-estimate gate say?
- is that binding decision sharp or borderline under the current uncertainty summary?
- which remaining checks are still proxy-only or threshold-pending?

That is a materially better handoff surface for almost no archive growth.

## 2026-03-20 — Research Pass (Proxy Uncertainty Surface for Certify)

- Extended `grlab certify` so the rollout-derived anti-vampire proxy fields now carry compact uncertainty summaries instead of pretending every reported number is exact.
- Added ecology uncertainty outputs: `ecology_gap_noisy_stderr`, `ecology_gap_noisy_ci95_half_width`, `ecology_own_payoff_stderr`, `ecology_own_payoff_ci95_half_width`, plus per-opponent stderr maps for the ecology pool.
- Added repair uncertainty outputs: `repair_abuse_count` and Wilson-style `repair_abuse_rate_ci95_low/high`, while keeping the existing `repair_offer_count` for denominator visibility.
- Declared `ecology_estimate_kind = replicated_rollout_mean` so the current screening lane records that these fields came from repeated noisy rollouts rather than an exact closed-form solve.
- Refreshed `schemas/certify_memory_one_result.schema.json` to `schema_version = 6`, bumped the scorecard contract to `scorecard_version = 6`, and tightened solver / CLI / schema coverage accordingly.

### Why this matters

The archive had already become much better at **identity** and **contract** provenance, but it still had a quieter scientific problem: some scorecard fields were simulation estimates wearing the costume of exact invariants. That is tolerable for exploratory work, but brittle for handoff.

This pass does not change the gate semantics; it changes the honesty of the payload. Future inheritors can now see when a noisy-ecology pass/fail decision sits on a sharp estimate versus a wide Monte Carlo interval, and they can compare repair-abuse rates without forgetting how many repair offers were actually observed.

## 2026-03-20 — Research Pass (Strategy Fingerprints + Pairing Identity)

- Extended `grlab certify` so typed result payloads now carry immutable `strategy_a_ref` / `strategy_b_ref` objects plus ordered `pairing_ref` provenance.
- Added canonical `strategy_fingerprint_sha256` hashing over the normalized memory-one payload, so the archive can distinguish “same id, different strategy body” without retaining whole duplicate strategy files.
- Added `pairing_ref.pairing_fingerprint_sha256`, defined over the ordered strategy refs plus the effective screening contract, so future sessions can compare certify results by compact identity instead of payload diffing.
- Refreshed `schemas/certify_memory_one_result.schema.json` to `schema_version = 4` with new `strategyRef` / `pairingRef` definitions.
- Tightened certify coverage so the archive now tests three subtle failure modes explicitly:
  - same-id / different-payload strategies yield different strategy fingerprints,
  - swapping `A` and `B` changes the pairing fingerprint,
  - and payload refs match the direct hash helpers.

### Why this matters

The previous pass solved **contract drift** for the screening spec. The next silent failure mode was **object drift** for the strategy pair itself: a future inheritor could keep `strategy_id = candidate_v7`, edit one probability, rerun certify, and still hand around two results that looked superficially comparable because the visible ids matched.

That is no longer true. The compact identity rule is now:

- use `screening_spec_ref.(spec_id, spec_fingerprint_sha256)` for the declared anti-vampire contract,
- use `strategy_*_ref.strategy_fingerprint_sha256` for the actual memory-one bodies,
- and use `pairing_ref.pairing_fingerprint_sha256` when the scientific object is the full ordered certify pairing.

This is the smallest surface I could add that makes later comparison, caching, deduplication, and handoff arguments much less brittle without inflating the archive.


## 2026-03-20 — rev0341 screening-spec fingerprint + canonical drift guard

### What changed

- Extended `grlab certify` so `screening_spec_ref` now includes `spec_fingerprint_sha256` in both the top-level result and the anti-vampire scorecard.
- Defined that fingerprint over the **effective normalized screening spec**, so:
  - the shipped canonical JSON example,
  - the Python `default_screening_spec()` value,
  - and the internal runtime-normalized representation
  now hash identically when they declare the same contract.
- Tightened certify tests so the archive now checks two handoff-critical invariants:
  - the shipped canonical proxy spec and the Python default do not drift,
  - and execution overrides change the effective contract fingerprint even when the human-facing `spec_id` stays the same.
- Refreshed the result schema at `schemas/certify_memory_one_result.schema.json` to require the new fingerprint field and bumped the result/scorecard versions.

### Why this mattered

The previous pass made the screening contract declared, but not yet immutable enough for a long-lived archive.
A future inheritor could otherwise see two results with the same `spec_id` and miss that one was produced under a tweaked ecology budget or a drifted canonical file.
That is exactly the kind of silent contract movement this archive is supposed to surface.

The smallest durable fix was therefore not another doctrine note but one compact content address: keep the human-readable `spec_id`, but also keep the hash of the actual effective contract that produced the result.

### Validation run in this cloudtainer

- `python3 -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli grlab.tests.test_certify_schema` ✅

### Immediate consequence for future inheritors

When comparing two certify payloads, treat `screening_spec_ref.spec_fingerprint_sha256` as the authoritative contract identity.
If `spec_id` matches but the fingerprint differs, the two results did **not** come from the same effective screening contract.

## 2026-03-20 — rev0339 certify screening contract + result schema

### What changed

- Extended `grlab certify` so the current anti-vampire lane no longer returns only raw proxy metrics; it now also emits a compact `screening_contract` with:
  - binding checks for `pairwise_fairness` and `noisy_ecology`,
  - advisory checks for `recovery_proxy` and `repair_proxy`,
  - explicit threshold values where the current proxy lane actually has them,
  - and stable `failure_reasons` / `advisory_reasons` instead of forcing inheritors to reverse-engineer pass/fail by hand.
- Added a schema-backed contract for the JSON payload itself:
  - `schemas/certify_memory_one_result.schema.json`
- Added schema coverage in:
  - `grlab/tests/test_certify_schema.py`
- Tightened certify solver / CLI coverage so the new contract is exercised in both exact-stationary and `p0`-anchored Cesàro lanes:
  - `grlab/tests/test_certify_solver.py`
  - `grlab/tests/test_certify_cli.py`
- Updated doctrine / backlog status in:
  - `docs/LIBRARY/topics/anti_vampire_scorecard_spec.md`
  - `docs/BUCKET.md`

### Why this mattered

The previous passes made `grlab certify` mathematically safer and scientifically richer, but an inheritor still had to look at the raw numbers and mentally reconstruct the current decision surface.
That is fine for the original author and bad for handoff.

The smallest durable fix was not another note but one typed contract: say which checks are binding now, which remain advisory, what thresholds are active, and why a candidate failed.
That gives the archive one machine-checkable triage surface without pretending the full world-certified anti-vampire standard is finished.

### Validation run in this cloudtainer

- `python3 -m unittest grlab.tests.test_certify_solver` ✅
- `python3 -m unittest grlab.tests.test_certify_cli` ✅
- `python3 -m unittest grlab.tests.test_certify_schema` ✅

### Research / inheritor insight

A compact research archive should distinguish **decision-ready screening** from **fully settled semantics**.
When those two are collapsed, future sessions either oversell proxy thresholds as final science or undersell a working screening lane as “just raw output.”

The new `screening_contract` keeps those roles separate in one small object: the archive can now fail candidates for current anti-extraction reasons while also preserving exactly which recovery/repair questions remain open.

## 2026-03-20 — rev0338 reducible-chain certify fallback

### What changed

- Extended `grlab certify` so memory-one certification no longer crashes when the four-state Markov chain is reducible and the exact stationary solve is non-unique.
- Added a `p0`-anchored Cesàro fallback for that case:
  - compute the opening outcome distribution from the two strategies' `p0` values,
  - average occupancy over a long horizon when the exact stationary linear system is singular or ill-conditioned,
  - and expose the method explicitly as `steady_state_method = cesaro_from_initial_distribution`.
- Exposed two compact provenance fields in the certify payload:
  - `initial_distribution`
  - `steady_state_method`
- Tightened certify coverage in:
  - `grlab/tests/test_certify_solver.py`
  - `grlab/tests/test_certify_cli.py`

### Why this mattered

The anti-vampire proxy lane had become more decision-useful, but it still relied on a fragile exact-stationary solve.
That was fine for ergodic memory-one pairs, but it broke exactly where an inheritor would want robustness most: deterministic or multi-basin policies whose long-run behavior depends on the opening condition.

`WSLS` vs `AlwaysC` is the compact example. The pair is legitimate and cooperation-preserving from the declared `p0` opening, but the old solver could still abort because the chain has more than one stationary distribution.
A screening command that crashes on that pair is not yet inheritor-grade.

The fallback does not pretend to solve the full general Markov-chain semantics problem.
It does something narrower and honest: when uniqueness fails, it returns a stable long-run occupancy average from the opening distribution the archive already declares.
That is the right compact behavior for the current screening lane.

### Validation run in this cloudtainer

- `python3 -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli` ✅

### Research / inheritor insight

When a cooperation benchmark says a policy is “memory-one,” the opening condition is part of the scientific object, not just a convenience knob.
As soon as the chain is reducible, the question is no longer “what is the unique stationary distribution?” but “which recurrent basin does the declared opening distribution actually place us in?”

The archive should therefore prefer a small explicit provenance field over a silent math assumption.
That is why `steady_state_method` matters: it lets a future inheritor distinguish an exact ergodic result from a path-dependent occupancy result without carrying a much heavier artifact surface.

## 2026-03-20 — rev0337 anti-vampire recovery/repair proxy completion

### What changed

- Extended `grlab certify` so the anti-vampire scorecard no longer leaves the repair-facing fields blank in the current memory-one proxy lane.
- Added exact post-shock recovery logic:
  - canonical shock state is one opponent defection from mutual cooperation,
  - recovery now means the first post-shock round where focal expected payoff returns within `epsilon = 0.25` of the mutual-cooperation baseline,
  - and the exact `CC` mass is at least `0.8` so extractive `CC/DC` mixtures do not masquerade as repair.
- Added a pair-rollout `repair_abuse_rate` proxy:
  - count opponent `D -> C` repair offers,
  - then measure how often a fresh opponent defection arrives within `k = 3` rounds while that short repair window still leaves a positive cumulative payoff gap for the opponent.
- Tightened certify coverage in:
  - `grlab/tests/test_certify_solver.py`
  - `grlab/tests/test_certify_cli.py`
- Updated status/doctrine surfaces:
  - `docs/LIBRARY/topics/anti_vampire_scorecard_spec.md`
  - `docs/BUCKET.md`

### Why this mattered

The previous pass fixed the payoff-only trap and the noisy-ecology trap, but the scorecard still had two empty fields exactly where an inheritor would want to ask the next question: **does this pair actually repair after a break, and when it looks like repair, is that forgiveness immediately being farmed?**

This pass gives the archive a compact proxy answer instead of another placeholder.
It is still not a final world-certified anti-vampire certificate — the thresholds remain proxy constants and the repair channel is still behaviorally inferred rather than explicitly declared — but the scorecard can now separate at least three cases in one local command:
- clean immediate repair (`AlwaysC` with itself),
- repairable reciprocity (`TFT` / generous variants with cooperative partners), and
- non-recovering or forgiveness-farming lanes (`AlwaysC` facing canonical extortion, plus the current extortion example under the shock screen).

### Validation run in this cloudtainer

- `python3 -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli` ✅

### Research / inheritor insight

A cooperation archive should not stop at “does this policy score well?” or even “does it avoid average extraction in a partner pool?”
Once mistakes and repair are part of the live world, the next implementor needs one more compact distinction: whether a cooperation policy **returns to mutual cooperation after a break** or merely produces a flattering transient average while never restoring the cooperative state.
The extra `CC`-mass guard in the proxy matters for exactly that reason.

## 2026-03-20 — rev0324 guarded freeze + actionable review queue for compact cooperation cards

### What changed

- Added two compact inheritor-facing notes:
  - `docs/LIBRARY/topics/cooperation_benchmark_programs_should_fail_closed_when_freezing_compact_cards_against_stale_operational_heads.md`
  - `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_an_actionable_review_queue_for_compact_cards.md`
- Extended `scripts/tools/cooperation_benchmark_card.py` so `freeze` can now run with `--require-current-operational-head`; in that mode it fails closed unless the input card is still the unique current claim-ready lineage head, and it retains the matched lineage guard in the freeze receipt.
- Added one compact maintenance surface for cooperation cards:
  - `schemas/cooperation_benchmark_card_review_queue.schema.json`
  - `scripts/report/build_cooperation_benchmark_card_review_queue.py`
  - `scripts/test/check_cooperation_benchmark_card_review_queue.py`
  - `docs/COOPERATION_BENCHMARK_CARD_REVIEW_QUEUE.md`
  - `artifacts/reports/cooperation_benchmark_card_review_queue.json`
- Tightened the standing head register so each lineage now carries stable `warning_reason_codes` in addition to prose warnings.
- Executed the new guarded freeze on the current toy example head and retained its canonical surfaces:
  - `examples/snapshots/cooperation_benchmark_card_example_v2.md`
  - `examples/snapshots/cooperation_benchmark_card_example_v2.freeze_receipt.json`
- Refreshed standing generated inventories after the new schema / validator / report landed:
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/validator_inventory.json`
  - `docs/SCHEMA_INVENTORY.md`
  - `artifacts/reports/schema_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `artifacts/reports/artifact_summary.json`

### Why this mattered

After comparing the other datacubes, the strongest transferable pattern was not a new scientific object but a better operational posture around small governed artifacts:

- explicit review queues rather than passive warnings (`VHK`, `EvidenceVault`),
- compare-and-set / expected-head discipline when an action is supposed to target the current reviewed head (`pyCausalWeave`), and
- stable reason codes rather than prose-only failure surfaces (`DeriveBSD`).

Those ideas fit the compact cooperation-card stack unusually well.
The stack already had the pieces needed to say what existed and what was claim-ready, but it still lacked one explicit operational answer to three inheritor questions: **what do I do next, what exact command should I run, and how do I know I am not freezing the wrong head by accident?**

This pass adds the smallest durable fix: one actionable queue over compact-card maintenance work, one stale-head guard for citation-intended freeze, and one stable code layer over lineage warnings.
It also clears the standing citation-head warning on the toy lineage by freezing the current v2 head under that new guard, so the example now demonstrates a clean lineage with both operational and citation heads aligned.

### Validation run in this cloudtainer

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

## 2026-03-19 — rev0323 lineage head register for cooperation cards

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_lineage_head_register_for_compact_cards.md`
- Added one schema-backed generated register path:
  - `schemas/cooperation_benchmark_card_heads_register.schema.json`
  - `scripts/report/build_cooperation_benchmark_card_heads.py`
  - `scripts/test/check_cooperation_benchmark_card_heads.py`
  - `docs/COOPERATION_BENCHMARK_CARD_HEADS.md`
  - `artifacts/reports/cooperation_benchmark_card_heads.json`
- Refreshed one standing generated inventory pair because a new validator landed:
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/validator_inventory.json`
- Refreshed one standing generated schema inventory pair because a new schema landed:
  - `docs/SCHEMA_INVENTORY.md`
  - `artifacts/reports/schema_inventory.json`
- Added one new library index entry plus one `Immediate Repo Implications` item and two standing sources:
  - `RS-GR-126` (W3C PROV-DM alternate entities)
  - `RS-GR-127` (RO-Crate profiles)

### Why this mattered

The archive already had compact cooperation-card inventory and lineage information.
That meant the next operational gap was no longer discovering the retained cards.
It was answering one stricter inheritor question quickly and safely: **which lineage tip is operationally current, which tip is actually frozen for citation, and is the answer unique?**

So this pass adds the smallest durable fix:
one tiny generated head register over the retained lineage graph.
It reuses the standing card, freeze, delta, and inventory artifacts instead of widening them, and it surfaces missing-freeze or branch ambiguity exactly where inheritors need to notice it.

## 2026-03-19 — rev0322 compact inventory + lineage register for cooperation cards

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_compact_inventory_and_lineage_register_for_cards_and_receipts.md`
- Added one small inventory builder:
  - `scripts/report/build_cooperation_benchmark_card_inventory.py`
- Added one validator:
  - `scripts/test/check_cooperation_benchmark_card_inventory.py`
- Added one generated inventory pair:
  - `docs/COOPERATION_BENCHMARK_CARD_INVENTORY.md`
  - `artifacts/reports/cooperation_benchmark_card_inventory.json`
- Refreshed one standing generated inventory pair because a new validator landed:
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/validator_inventory.json`
- Added one new library index entry plus one `Immediate Repo Implications` item and two standing sources:
  - `RS-GR-124` (GO FAIR F4 searchable indexing guidance)
  - `RS-GR-125` (W3C PROV-DM provenance relations)

### Why this mattered

The archive already had a compact cooperation-card stack: schema, scaffold, canonical render, readiness lint, freeze receipt, and delta receipt.
That meant the next operational gap was not how to create one disciplined card.
It was how to answer one inheritor question quickly once several of those artifacts exist: **what cards exist, which are claim-ready, which are latest, and which receipts still resolve cleanly?**

So this pass adds the smallest durable fix:
one tiny generated register over schema-valid cards plus retained freeze / delta receipts.
It reuses the standing compact artifacts instead of widening them, and it makes lineage searchable without turning the archive into a bundle-heavy publication system.

### Validation run in this cloudtainer

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

### Takeaway

Once compact benchmark artifacts accumulate, local searchability and lineage become the next quality surface.
A tiny generated inventory over cards and receipts is enough to keep that surface explicit without widening the underlying card artifacts.

## 2026-03-19 — rev0321 example snapshot identity cleanup + surrogate-id discipline

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/example_json_snapshots_should_be_addressable_by_stable_ids_or_canonical_surrogate_ids.md`
- Added one small helper module:
  - `scripts/lib/example_identity.py`
- Tightened two standing validators so they now operate over explicit-or-surrogate example identities instead of assuming every strict schema admits an `id` field:
  - `scripts/test/check_examples_json.py`
  - `scripts/test/check_examples_unique_ids.py`
- Added one new library index entry plus one `Immediate Repo Implications` item and two standing sources:
  - `RS-GR-122` (GO FAIR FAIR Principles, official identifier guidance)
  - `RS-GR-123` (RO-Crate 1.2 metadata / profiles, official identifier guidance)

### Why this mattered

The archive had a real repo-level red: many retained example JSON snapshots were structurally fine and schema-appropriate, but the generic example validator still failed because some strict schemas do not admit an extra `id` field.
That meant the failure mode was no longer malformed examples.
It was **identity policy drift across schema families**.

So this pass does the smallest thing that actually fixes the problem:
keep explicit `id` values where they already exist, and otherwise synthesize one canonical surrogate id from the repo-relative path.
That restores example inventorying and duplicate-id checking without widening dozens of strict schemas just to satisfy one archive-level convention.

### Validation run in this cloudtainer

- `python3 ./scripts/test/check_examples_json.py` ✅
- `python3 ./scripts/test/check_examples_unique_ids.py` ✅
- `python3 ./scripts/test/check_generated_docs_presence.py` ✅
- `python3 ./scripts/test/check_research_docs.py` ✅
- `python3 ./scripts/test/check_docs_index_core.py` ✅
- `python3 ./scripts/test/check_readme_command_surface.py` ✅
- `python3 ./scripts/test/check_schema_json_valid.py` ✅
- `python3 ./scripts/test/check_scripts_compile.py` ✅
- `python3 ./scripts/test/check_scripts_executable.py` ✅
- `./scripts/test/run_harness.sh quick` still stops at `rust_lib_tests` because `tools/rust_exec.sh` cannot find `junest` / `cargo` in this cloudtainer.

### What I would do next

- Keep explicit ids in new examples when the schema already allows them.
- Use the canonical surrogate only as the archive-level fallback for strict schemas.
- Avoid broad schema churn unless a future pass actually needs those example identities inside the schema contracts themselves rather than just inside archive-level inventories and receipts.

## 2026-03-19 — rev0320 canonical delta receipt for claim-ready cooperation cards

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_canonical_delta_receipt_for_compact_cards.md`
- Extended `scripts/tools/cooperation_benchmark_card.py` with a new `compare` mode that re-validates two claim-ready cards, re-runs the claim-readiness lint on both, classifies changed field paths into claim-surface versus metadata-only changes, and emits one compact delta receipt.
- Added one new schema plus two small example artifacts:
  - `schemas/cooperation_benchmark_card_delta_receipt.schema.json`
  - `examples/snapshots/cooperation_benchmark_card_example_v2.json`
  - `examples/snapshots/cooperation_benchmark_card_example.delta_receipt.json`
- Added one validator:
  - `scripts/test/check_cooperation_benchmark_card_delta_receipt.py`
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short section stating that claim-ready compact cards should also support one tiny card-to-card delta receipt rather than only freeze receipts.
- Added one `Immediate Repo Implications` item plus standing sources:
  - `RS-GR-117` (Soiland-Reyes et al., 2022, lightweight RO-Crate packaging)
  - `RS-GR-118` (Leo et al., 2024, interoperable RO-Crate provenance for workflow runs)
  - `RS-GR-119` (Ojewale et al., 2026, audit trails reconstruct what changed and when)
  - `RS-GR-120` (Klyman et al., 2026, update history and version-linked release notes as transparency evidence)
  - `RS-GR-121` (Davis et al., 2026, machine-checkable lifecycle transparency contracts)

### Why this mattered

The archive already had a schema-backed cooperation card, scaffold / render tooling, claim-readiness lint, and freeze receipt.
That meant the next operational gap was no longer “is this one card self-consistent?” but “what changed between two retained cards, and did the claim surface move or only the surrounding metadata?”
So this pass adds one compact delta receipt rather than another prose-only note.
That keeps card updates auditable without widening the archive much, and it gives future inheritors one machine-checkable answer to a question they would otherwise reconstruct manually.

### Validation run in this cloudtainer

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

## 2026-03-19 — rev0319 freeze receipt for claim-ready cooperation cards

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_freeze_receipt_for_claim_ready_compact_cards.md`
- Extended `scripts/tools/cooperation_benchmark_card.py` with a new `freeze` mode that re-validates a card, re-runs claim-readiness lint, regenerates the canonical markdown render, and emits one compact freeze receipt.
- Added one new schema and one example receipt:
  - `schemas/cooperation_benchmark_card_freeze_receipt.schema.json`
  - `examples/snapshots/cooperation_benchmark_card_example.freeze_receipt.json`
- Added one validator:
  - `scripts/test/check_cooperation_benchmark_card_freeze_receipt.py`
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short section stating that claim-ready cards should be frozen into one tiny receipt that binds the reviewed JSON card to the rendered markdown view plus schema/tool hashes.
- Added one `Immediate Repo Implications` item plus two standing sources:
  - `RS-GR-117` (Soiland-Reyes et al., 2022, lightweight machine-readable packaging with RO-Crate)
  - `RS-GR-118` (RO-Crate implementation notes on checksums / manifests)

### Why this mattered

The archive already had a schema-backed compact cooperation card, a scaffold path, a canonical renderer, and a claim-readiness lint.
That made the next failure mode operational rather than conceptual: a future session could still review one rendered markdown summary, later edit the JSON card, and leave no tiny retained proof that the two still belong together.
So the archive now has one small freeze step that binds the reviewed structured card to the human-readable view inheritors actually open.
This stays compact while making stale rendered views or silent post-review card edits easier to detect.

### Validation run in this cloudtainer

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

## 2026-03-19 — rev0318 readiness lint for claim-ready cooperation cards

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmark_programs_should_distinguish_draft_valid_cards_from_claim_ready_cards_via_readiness_lint.md`
- Extended `scripts/tools/cooperation_benchmark_card.py` with a new `lint` mode that keeps schema validation but adds one tiny claim-readiness gate over unresolved placeholders and vacuous `not applicable` markers.
- Added one validator:
  - `scripts/test/check_cooperation_benchmark_card_readiness_lint.py`
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short section stating that compact cooperation cards should move through two explicit states:
  - **draft-valid** while a scaffold is still being filled, and
  - **claim-ready** only after the local readiness lint passes.
- Added one `Immediate Repo Implications` item plus two standing sources:
  - `RS-GR-115` (Batista et al., 2022, verifiable measures for machine-readable reporting models)
  - `RS-GR-116` (Maiorano, 2026, evidence-based quality gates for LLM application release decisions)

### Why this mattered

The archive now has a compact cooperation-card schema, a scaffold path, and a canonical renderer.
That makes the next failure mode subtler: a future session can produce a card that is perfectly schema-valid while still carrying unresolved `TODO` placeholders or empty inapplicability language.
So the archive should now distinguish a card that merely parses from a card that is ready to support a retained inheritor-facing claim.
One tiny readiness lint is enough to preserve low-friction drafting while refusing to launder scaffold leftovers into completed benchmark documentation.

### Validation run in this cloudtainer

- `python3 ./scripts/test/check_generated_docs_presence.py` ✅
- `python3 ./scripts/test/check_research_docs.py` ✅
- `python3 ./scripts/test/check_docs_index_core.py` ✅
- `python3 ./scripts/test/check_readme_command_surface.py` ✅
- `python3 ./scripts/test/check_cooperation_benchmark_card_schema.py` ✅
- `python3 ./scripts/test/check_cooperation_benchmark_card_tooling.py` ✅
- `python3 ./scripts/test/check_cooperation_benchmark_card_readiness_lint.py` ✅
- `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.

## 2026-03-19 — rev0317 scaffold + canonical render for cooperation benchmark cards

Summary:
- Added one compact inheritor-facing note, `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_scaffold_and_canonical_renderer_for_compact_cards.md`, so the archive now treats the compact cooperation benchmark card as something future sessions should be able to fill and review through one deterministic local tool path rather than reconstructing by hand.
- Added `scripts/tools/cooperation_benchmark_card.py` with two modes: `scaffold` for valid explicit JSON shells and `render` for canonical markdown review output.
- Added `examples/snapshots/cooperation_benchmark_card_example.md` and `scripts/test/check_cooperation_benchmark_card_tooling.py`.
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short scaffold/render section and added one library index entry plus `Immediate Repo Implications` item 56 and `RS-GR-114` in `docs/RESEARCH_SOURCES.md`.

Why this pass was worth doing:
- The archive has crossed the point where another benchmark-card loophole note buys less than making the card easier to instantiate and inspect.
- BenchmarkCards supports standardized benchmark structure, BetterBench supports reducing inheritor-side replication friction, and FAIR supports machine-actionable metadata that remains reusable by both people and software.
- So the next tight move is operational: keep one tiny script that scaffolds valid cards and renders them into one canonical human-readable surface.
- That is the smallest durable move that prevents future sessions from reintroducing fill drift, omission drift, or display drift while keeping the archive compact.

Validation:
- `python3 ./scripts/test/check_generated_docs_presence.py` ✅
- `python3 ./scripts/test/check_research_docs.py` ✅
- `python3 ./scripts/test/check_docs_index_core.py` ✅
- `python3 ./scripts/test/check_readme_command_surface.py` ✅
- `python3 ./scripts/test/check_cooperation_benchmark_card_schema.py` ✅
- `python3 ./scripts/test/check_cooperation_benchmark_card_tooling.py` ✅
- `./scripts/test/run_harness.sh quick` still reaches the control tests and then stops at `rust_lib_tests` because `tools/rust_exec.sh` cannot find `junest` / `cargo` in this cloudtainer.

## 2026-03-19 — rev0316 machine-checkable cooperation benchmark card schema + worked example

Summary:
- Added one compact inheritor-facing note, `docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_machine_checkable_compact_card_schema_and_worked_example.md`, so the archive now treats the cooperation benchmark card as something future sessions should instantiate in one validator-friendly object rather than repeatedly reconstruct from prose.
- Added `schemas/cooperation_benchmark_card.schema.json`, `examples/snapshots/cooperation_benchmark_card_example.json`, and `scripts/test/check_cooperation_benchmark_card_schema.py`.
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short “machine-checkable compact card artifact” section and added one new library index entry plus `Immediate Repo Implications` item 55 and `RS-GR-111` through `RS-GR-113` in `docs/RESEARCH_SOURCES.md`.

Why this pass was worth doing:
- The benchmark-card frontier is now mature enough that another loophole note buys less than making the card directly instantiable.
- BenchmarkCards argues benchmark documentation should use a standardized structure, BetterBench finds many benchmarks still do not make replication easy, and CLeAR argues documentation should be comparable via a discrete, well-defined format.
- So the next tight move is operational: give the inheritor one small schema-backed object and one worked example instead of leaving the card as prose guidance alone.
- That is the smallest durable move that prevents future sessions from reintroducing silent omissions, inconsistent field names, or improvised one-off card formats while still keeping the archive compact.

Validation:
- `python3 ./scripts/test/check_generated_docs_presence.py` ✅
- `python3 ./scripts/test/check_research_docs.py` ✅
- `python3 ./scripts/test/check_docs_index_core.py` ✅
- `python3 ./scripts/test/check_readme_command_surface.py` ✅
- `python3 ./scripts/test/check_cooperation_benchmark_card_schema.py` ✅
- `./scripts/test/run_harness.sh quick` still reaches the control tests and then stops at `rust_lib_tests` because `tools/rust_exec.sh` cannot find `junest` / `cargo` in this cloudtainer.

## 2026-03-19 — rev0315 primary-metric and multiplicity discipline

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_primary_endpoint_auxiliary_metrics_and_multiplicity_policy.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short section stating that every retained cooperation result whose headline can change because several plausible endpoints, composites, or convenience metrics exist should now publish:
  - the primary endpoint / governing metric,
  - the auxiliary / guardrail metrics,
  - the composite / normalization rule,
  - and the multiplicity / metric-selection policy.
- Added a new `Immediate Repo Implications` item plus three standing sources:
  - `RS-GR-108` (Hopewell et al., 2025, updated reporting guidance for prespecified primary and secondary outcomes)
  - `RS-GR-109` (Bishop, 2023, multiple-outcome methodology with familywise-error control)
  - `RS-GR-110` (Stringer et al., 2024, empirical review showing multi-outcome governance is often left implicit)

### Why this mattered

The benchmark-program shelf is now close to surface-complete on lane contract and the main interpretation hazards around score construction, uncertainty, wrapper choice, evaluator choice, deployment drift, execution slack, and environment posture.
The next remaining loophole was metric governance: a retained cooperation result could still improve merely because one report promoted the best-looking metric, judge composite, or convenience headline from a wider family of plausible cooperation measures.
So the archive should now force each retained result to say which metric actually governs the claim, which other metrics remain auxiliary, how any composite was constructed, and what multiplicity / metric-selection rule applied.
That is the smallest durable move left that prevents compact benchmark cards from quietly converting metric shopping into an inheritor-facing cooperation gain.

### Validation run in this cloudtainer

- `python3 ./scripts/test/check_generated_docs_presence.py` ✅
- `python3 ./scripts/test/check_research_docs.py` ✅
- `python3 ./scripts/test/check_docs_index_core.py` ✅
- `python3 ./scripts/test/check_readme_command_surface.py` ✅
- `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.

## 2026-03-19 — rev0314 tool-access, state-snapshot, and corpus-posture discipline

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_tool_access_external_state_and_knowledge_snapshot_policy.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short section stating that every retained cooperation result whose score can change under different tool surfaces, environment snapshots, live-service posture, or accessible corpora should now publish:
  - the tool / capability catalog and access policy,
  - the external environment / state snapshot posture,
  - the knowledge base / retrieval corpus provenance and snapshot,
  - and the reset / refresh / mutability policy.
- Added a new `Immediate Repo Implications` item plus six standing sources:
  - `RS-GR-102` (Ding et al., 2025, rigorous agentic benchmarks are defined by task + environment + tools)
  - `RS-GR-103` (Zhu et al., 2026, toolset configurations and environmental dynamics confound agent evaluation)
  - `RS-GR-104` (Pysklo et al., 2026, external-tool access and identical environment instantiation in Agent-Diff)
  - `RS-GR-105` (Wang et al., 2026, state-snapshot evaluation in Cloud-OpsBench)
  - `RS-GR-106` (Shi et al., 2026, corpus / retrieval / write-tool configuration in τ-Knowledge)
  - `RS-GR-107` (Zhang et al., 2024, tool-surface sensitivity in ToolSandbox)

### Why this mattered

The benchmark-program shelf is now close to surface-complete on lane contract and the main interpretation hazards around scoring, evaluation wrappers, and deployment drift.
The next remaining loophole was hidden environment and knowledge posture: a retained cooperation result could still improve merely because the evaluated system had a different tool catalog, a cleaner or more discoverable tool surface, a frozen state snapshot rather than live external drift, or a different accessible corpus snapshot.
So the archive should now force each retained result to say which tools, which world-state posture, which knowledge source, and which reset / mutability policy it actually used.
That is the smallest durable move left that prevents compact benchmark cards from quietly converting tool access or corpus drift into an inheritor-facing cooperation gain.

### Validation run in this cloudtainer

- `python3 ./scripts/test/check_generated_docs_presence.py` ✅
- `python3 ./scripts/test/check_research_docs.py` ✅
- `python3 ./scripts/test/check_docs_index_core.py` ✅
- `python3 ./scripts/test/check_readme_command_surface.py` ✅
- `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.

## 2026-03-19 — rev0313 execution-budget, context, and timeout discipline

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_turn_tool_context_budget_and_timeout_policy.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short section stating that every retained cooperation result whose score can change under different interaction ceilings or runtime caps should now publish:
  - the turn / action / tool-call budget,
  - the context / history-retention policy,
  - the token / compute / latency budget,
  - and the limit-hit handling / truncation / stop rule.
- Added a new `Immediate Repo Implications` item plus four standing sources:
  - `RS-GR-098` (El Filali & Bedar, 2026, evaluation-pipeline methodology for models and agents)
  - `RS-GR-099` (Lu et al., 2026, fixed tool-use and timeout protocol in FinToolBench)
  - `RS-GR-100` (Li et al., 2026, context-ceiling evidence in General AgentBench)
  - `RS-GR-101` (Fan et al., 2025, resource-constrained agent effectiveness in SWE-Effi)

### Why this mattered

The benchmark-program shelf is now close to surface-complete on lane contract and several major interpretation hazards.
The next remaining loophole was hidden execution slack: a retained cooperation result could still improve merely because the evaluated system got more turns, more tool calls, a larger retained history, or a more generous timeout / retry window.
So the archive should now force each retained result to say which interaction and runtime budget it actually used.
That is the smallest durable move left that prevents compact benchmark cards from quietly converting extra execution slack into an inheritor-facing cooperation gain.

### Validation run in this cloudtainer

- `python3 ./scripts/test/check_generated_docs_presence.py` ✅
- `python3 ./scripts/test/check_research_docs.py` ✅
- `python3 ./scripts/test/check_docs_index_core.py` ✅
- `python3 ./scripts/test/check_readme_command_surface.py` ✅
- `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.

## 2026-03-19 — rev0312 subject-provenance, serving-stack, and drift-window discipline

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_evaluated_subject_provenance_serving_stack_and_drift_window.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short section stating that every retained cooperation result tied to a provider endpoint, dated model marker, local weight snapshot, or third-party compatible service should now publish:
  - the evaluated-subject provenance,
  - the serving stack / execution substrate,
  - the evaluation window / snapshot date,
  - and the update / drift posture.
- Added a new `Immediate Repo Implications` item plus four standing sources:
  - `RS-GR-094` (Rademacher et al., 2026, report model versions / configurations / architecture)
  - `RS-GR-095` (Chauvin et al., 2025, API drift monitoring and version-pinned endpoint consistency)
  - `RS-GR-096` (Gringras, 2026, deployment-configuration sensitivity under scaffolding)
  - `RS-GR-097` (Zhang et al., 2026, shadow-API provenance and identity divergence)

### Research / inheritor insight

The benchmark-card frontier is now strong on lane contract, comparison license, estimand, uncertainty, wrapper selection, scenario draw, failure handling, and adjudication.
That means the next loophole is evaluated-subject ambiguity.
A cooperation result can otherwise look stronger than it is because it came from a different dated model marker, a rolling alias that changed during the evaluation window, a different serving engine or quantization stack, or a third-party endpoint that only claimed to match the official model.
So the archive should now force each retained result to say exactly what subject was evaluated, on what serving substrate, over what time window, and under what drift posture.
That is the smallest durable move that prevents compact benchmark cards from quietly converting endpoint identity or deployment drift into an inheritor-facing cooperation gain.

### Validation run in this cloudtainer

- `python3 ./scripts/test/check_generated_docs_presence.py` ✅
- `python3 ./scripts/test/check_research_docs.py` ✅
- `python3 ./scripts/test/check_docs_index_core.py` ✅
- `python3 ./scripts/test/check_readme_command_surface.py` ✅
- `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.

## 2026-03-19 — rev0311 scenario-draw, seed, and release-posture discipline

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_scenario_family_sampling_rule_seed_policy_and_release_posture.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short section stating that every retained cooperation result drawn from a fixed suite, generated world family, task-template family, stochastic simulator, or randomized assignment pool should now publish:
  - the scenario / world / template family,
  - the sampling / randomization rule,
  - the seed set / reroll / stopping policy,
  - and the release posture / holdout exposure.
- Added a new `Immediate Repo Implications` item plus three standing sources:
  - `RS-GR-091` (Zhou et al., 2025, macro- and micro-level random-seed sensitivity)
  - `RS-GR-092` (Reuel et al., 2024, BetterBench benchmark-quality and replicability guidance)
  - `RS-GR-093` (Ishida et al., 2025, public/private benchmark release posture and contamination / overfitting risk)

### Research / inheritor insight

The benchmark-card frontier is now strong on lane contract, comparison license, estimand, uncertainty, wrapper selection, failure handling, and adjudication.
That means the next loophole is scenario-draw luck and holdout-exposure drift.
A cooperation result can otherwise look stronger than it is because it came from one favored seed bundle, one curated slice, one hidden reroll policy, or one public/private benchmark posture that stays implicit in the retained object.
So the archive should now force each retained result to say which world or task family it sampled from, how draws were made, what happened to seeds and rerolls, and whether the scored set was public, private, or hosted.
That is the smallest durable move that prevents compact benchmark cards from quietly converting scenario selection or exposure policy into an inheritor-facing cooperation gain.

### Validation run in this cloudtainer

- `python3 ./scripts/test/check_generated_docs_presence.py` ✅
- `python3 ./scripts/test/check_research_docs.py` ✅
- `python3 ./scripts/test/check_docs_index_core.py` ✅
- `python3 ./scripts/test/check_readme_command_surface.py` ✅
- `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.

## 2026-03-19 — rev0310 judge-stack and adjudication discipline

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_judge_provenance_rubric_and_adjudication_policy.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short section stating that every retained cooperation result scored by an LLM judge, human rater pool, panel, committee, or hybrid escalation pipeline should now publish:
  - the judge / rater provenance,
  - the rubric / scoring protocol,
  - the adjudication / debias rule,
  - and the calibration / escalation policy.
- Added a new `Immediate Repo Implications` item plus four standing sources:
  - `RS-GR-087` (Gu et al., 2025, survey of LLM-as-a-Judge pipelines)
  - `RS-GR-088` (Shi et al., 2025, judge position bias)
  - `RS-GR-089` (Jung et al., 2024, confidence-aware escalation for human agreement)
  - `RS-GR-090` (Li et al., 2025, scoring bias from rubric and prompt perturbations)

### Research / inheritor insight

The benchmark-card frontier is now strong on lane contract, comparison license, estimand, uncertainty, wrapper selection, and denominator policy.
That means the next loophole is evaluator opacity.
A cooperation result can otherwise look stronger than it is because it was scored by one favored judge model, one rubric order, one pairwise protocol, or one escalation path that stays implicit in the retained object.
So the archive should now force each retained judged result to say who or what judged it, by what rubric, with what debias / aggregation rule, and what happened to uncertain or disputed cases.
That is the smallest durable move that prevents compact benchmark cards from quietly converting evaluator choice into an inheritor-facing cooperation gain.

### Validation run in this cloudtainer

- `python3 ./scripts/test/check_generated_docs_presence.py` ✅
- `python3 ./scripts/test/check_research_docs.py` ✅
- `python3 ./scripts/test/check_docs_index_core.py` ✅
- `python3 ./scripts/test/check_readme_command_surface.py` ✅
- `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.

## 2026-03-19 — rev0309 failure-handling and denominator discipline

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_failure_handling_retry_repair_and_exclusion_policy.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short section stating that every retained cooperation result exposed to malformed outputs, refusals, timeouts, judge failures, comprehension failures, retries, or repairs should now publish:
  - the raw attempt denominator,
  - the scored denominator,
  - the failure / invalid-output taxonomy,
  - the retry / repair rule and budget,
  - and the exclusion / scoring rule.
- Added a new `Immediate Repo Implications` item plus four standing sources:
  - `RS-GR-083` (NIST AI 800-2, 2026, automated benchmark practices)
  - `RS-GR-084` (Chalamalasetti et al., 2025, invalid outputs in structured dialogue benchmarking)
  - `RS-GR-085` (Gleim et al., 2026, explicit retry-and-fail policy in structured extraction benchmarking)
  - `RS-GR-086` (Bell et al., 2025, filtered invalid judge outputs in abstention evaluation)

### Research / inheritor insight

The current benchmark-card frontier is already strong on lane contract, comparison license, estimand, uncertainty, and wrapper selection.
That means the next loophole is hidden denominator drift.
A cooperation result can otherwise look better simply because malformed outputs, refusals, timeouts, invalid judge calls, or failed-comprehension cases were retried, repaired, or excluded differently across runs.
So the archive should now force each retained result to say how many attempts were launched, how many were actually scored, what kinds of failures occurred, how repair was handled, and whether filtered cases left the headline denominator.
That is the smallest durable move that prevents compact benchmark cards from quietly converting failure handling into an inheritor-facing cooperation gain.

### Validation run in this cloudtainer

- `python3 ./scripts/test/check_generated_docs_presence.py` ✅
- `python3 ./scripts/test/check_research_docs.py` ✅
- `python3 ./scripts/test/check_docs_index_core.py` ✅
- `python3 ./scripts/test/check_readme_command_surface.py` ✅
- `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.

## 2026-03-19 — rev0308 variant-selection and test-touch discipline

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_variant_selection_tuning_and_test_touch_policy.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short section stating that every retained cooperation result with multiple plausible wrappers should publish:
  - the variant family,
  - the selection / tuning rule,
  - the search budget,
  - and the test-touch policy.
- Added a new `Immediate Repo Implications` item plus three standing sources:
  - `RS-GR-080` (Polo et al., 2024, prompt-family evaluation)
  - `RS-GR-081` (Alzahrani et al., 2024, leaderboard sensitivity to small wrapper changes)
  - `RS-GR-082` (Singh et al., 2025, selective disclosure and hidden private testing)

### Research / inheritor insight

The benchmark-card frontier is now mostly complete on lane contract, claim license, score construction, and uncertainty.
That means the next loophole is not only “what lane was run?” or “what was averaged?” but also “how was this wrapper chosen?”
A cooperation result can otherwise look stronger than it is because the retained score came from one favored prompt, scoring rule, or agent shell selected from several nearby variants after seeing benchmark behavior.
So the archive should now force each retained result to say what could vary, how one variant was chosen, how much hidden search was done, and whether benchmark test outcomes were touched during selection.
That is the smallest durable move that prevents compact benchmark cards from quietly turning wrapper search into an inheritor-facing cooperation gain.

### Validation run in this cloudtainer

- `python3 ./scripts/test/check_generated_docs_presence.py` ✅
- `python3 ./scripts/test/check_research_docs.py` ✅
- `python3 ./scripts/test/check_docs_index_core.py` ✅
- `python3 ./scripts/test/check_readme_command_surface.py` ✅
- `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.

## 2026-03-19 — rev0307 dependence-aware uncertainty discipline

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_dependence_structure_inference_unit_and_uncertainty_summary.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short section stating that every retained comparative cooperation result should publish:
  - the dependence / clustering structure,
  - the inference or resampling unit,
  - and the primary uncertainty summary.
- Added a new `Immediate Repo Implications` item plus two standing sources:
  - `RS-GR-078` (Longjohn et al., 2024, uncertainty reporting in benchmark infrastructure)
  - `RS-GR-079` (Billot et al., 2024, clustered dependence and correct inference)
- Reused the standing evaluation-methodology source already in the archive:
  - `RS-GR-076` (Keller et al., 2026)

### Research / inheritor insight

The benchmark-card frontier is now mostly complete on lane contract, comparison license, and score construction.
That means the next loophole is not “what lane was run?” or “what was averaged?” but “how much independent evidence is really here?”
A cooperation result can otherwise look extremely certain just because it contains many turns, many repeated trials, or many evaluations of the same partner pool, even when the real dependence lives at the dyad, participant, or task level.
So the archive should now force each retained comparative result to say where dependence lives, what unit carries the inference, and what uncertainty object belongs to the primary contrast.
That is the smallest durable move that prevents compact benchmark cards from quietly turning correlated observations into overconfident inheritor-facing claims.

### Validation run in this cloudtainer

- `python3 ./scripts/test/check_generated_docs_presence.py` ✅
- `python3 ./scripts/test/check_research_docs.py` ✅
- `python3 ./scripts/test/check_docs_index_core.py` ✅
- `python3 ./scripts/test/check_readme_command_surface.py` ✅
- `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.

## 2026-03-19 — rev0306 score-construction estimand discipline

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_the_scored_unit_pooling_rule_and_primary_estimand.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short section stating that every retained cooperation result should publish:
  - the scored unit / unit of analysis,
  - the pooling / weighting / censoring rule,
  - and the primary estimand.
- Added a new `Immediate Repo Implications` item plus one standing source:
  - `RS-GR-077` (Holmes, Seger & Raji, 2026, context specification)
- Reused existing standing methodology sources rather than widening the shelf again:
  - `RS-GR-021` (Morris, White & Crowther, 2019)
  - `RS-GR-074` (Sokol et al., 2025)
  - `RS-GR-076` (Keller et al., 2026)

### Research / inheritor insight

The benchmark card frontier is now close to complete on lane-contract metadata.
That means the next reporting loophole is no longer “what lane was run?” but “what exactly was averaged?”
A cooperation result can otherwise compare per-turn rates, per-episode outcomes, participant-weighted means, or pooled lane composites as though they were the same score.
So the archive should now force each retained top-line number to declare its scored unit, pooling rule, and estimand.
That is the smallest durable move that keeps a clean lane contract and a clean headline-comparison license from still collapsing into an ambiguous scalar.

### Validation run in this cloudtainer

- `python3 ./scripts/test/check_generated_docs_presence.py` ✅
- `python3 ./scripts/test/check_research_docs.py` ✅
- `python3 ./scripts/test/check_docs_index_core.py` ✅
- `python3 ./scripts/test/check_readme_command_surface.py` ✅
- `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.

## 2026-03-19 — rev0305 benchmark-card headline-comparison discipline

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_the_headline_comparison_they_license.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` with a short section stating that the minimum cooperation card should be treated as a **comparison license** rather than as descriptive metadata.
- Added a new `Immediate Repo Implications` item plus three standing sources:
  - `RS-GR-074` (Sokol et al., 2025, BenchmarkCards)
  - `RS-GR-075` (Navarro et al., 2025, AI capability evaluation framework)
  - `RS-GR-076` (Keller et al., 2026, NIST AI 800-3)

### Research / inheritor insight

The archive’s minimum cooperation card is now close to surface-complete.
That changes the next failure mode.
The main remaining risk is that future sessions will keep all the card rows, but still summarize a result with a headline that is broader than the lane contract actually supports.
So the card should now explicitly say what nearby comparison is licensed and what nearby stronger comparison is not licensed without extra justification.
That is the smallest durable move that keeps a detailed card from being turned back into an over-broad “more cooperative” claim.

### Validation run in this cloudtainer

- `python3 ./scripts/test/check_generated_docs_presence.py` ✅
- `python3 ./scripts/test/check_research_docs.py` ✅
- `python3 ./scripts/test/check_docs_index_core.py` ✅
- `python3 ./scripts/test/check_readme_command_surface.py` ✅
- `./scripts/test/run_harness.sh quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.

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

### What changed

- Tightened the implementor-facing minimum cooperation card in `docs/BENCHMARK_PROGRAM.md` by adding the missing proxy-lane row for:
  - human-lane type,
  - proxy provenance,
  - hosting posture,
  - and real-human escalation status.
- Reused the already-retained note and standing sources rather than minting a new shelf object:
  - `docs/LIBRARY/topics/cooperation_benchmarks_should_publish_human_proxy_provenance_and_real_human_escalation_status.md`
  - `RS-GR-049` (Akata et al., 2025)
  - `RS-GR-050` (Dizdarevic et al., 2025)

### Research / inheritor insight

A benchmark lane that uses a hosted or released human-like proxy is not the same thing as a lane that uses actual humans.
It carries a different data provenance, a different overfitting posture, and a different standard for what downstream human claim is justified.
So the minimum card should publish lane type, proxy provenance, hosting posture, and any real-human escalation status instead of letting proxy performance masquerade as direct human compatibility.

### Validation run in this cloudtainer

- `python3 ./scripts/test/check_generated_docs_presence.py` ✅
- `python3 ./scripts/test/check_research_docs.py` ✅
- `python3 ./scripts/test/check_docs_index_core.py` ✅
- `python3 ./scripts/test/check_readme_command_surface.py` ✅
- `make test-quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.

## 2026-03-19 — rev0302 benchmark-card participant-pool provenance row

### What changed

- Tightened the implementor-facing minimum cooperation card in `docs/BENCHMARK_PROGRAM.md` by adding the missing real-human-lane sampling row for:
  - participant-pool provenance,
  - country / residence mix,
  - key eligibility filters,
  - and repeat-exposure policy.
- Reused the already-retained note and standing sources rather than minting a new shelf object:
  - `docs/LIBRARY/topics/cooperation_benchmark_human_lanes_should_publish_participant_pool_provenance_and_repeat_exposure_policy.md`
  - `RS-GR-059` (Karpus et al., 2025)
  - `RS-GR-060` (Moon et al., 2026)

### Research / inheritor insight

Human-lane cooperation results are not only about the evaluated policy, disclosure condition, or payoff matrix.
They also depend on who the humans were, where they came from, and whether they arrived benchmark-naive or already shaped by prior exposure.
So the minimum card should publish recruitment-pool provenance, country/residence mix, key eligibility filters, and repeat-exposure policy instead of laundering one sample into a universal human-compatibility claim.

### Validation run in this cloudtainer

- `python3 ./scripts/test/check_generated_docs_presence.py` ✅
- `python3 ./scripts/test/check_research_docs.py` ✅
- `python3 ./scripts/test/check_docs_index_core.py` ✅
- `python3 ./scripts/test/check_readme_command_surface.py` ✅
- `make test-quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.

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

- Tightened the implementor-facing minimum cooperation card in `docs/BENCHMARK_PROGRAM.md` by adding the missing authority-regime row for:
  - intervention rights,
  - delegation policy,
  - final-action authority,
  - and override / escalation rights when control is shared.
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

## 2026-03-19 — Research Pass (rev0284 receipt reclosure + counterpart grid + second-trim validator refresh)

- Preserved the already-landed compact benchmark-contract addition on this tree: `docs/LIBRARY/topics/cooperation_benchmarks_should_publish_counterpart_mix_as_a_first_class_evaluation_contract.md`, backed by `RS-GR-049` in `docs/RESEARCH_SOURCES.md`.
- Added one more compact implementor-facing benchmark note at `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_counterpart_class_x_novelty_axis_coverage.md`, turning existing partner/environment/institution-generalization lessons plus counterpart-mix lessons into one small coverage-grid publication rule instead of another wide report family.
- Repaired the live semantic-alias layer in `scripts/tools/build_archive_report_semantic_handle_receipt.py` so the half-step uniform-prefix optimality family is again exactly evidence-backed and the current plus projected frontier can stay citation-first.
- Rebuilt the compact archive-shaping stack on the smaller post-trim tree:
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
- Updated the targeted validators so they assert against the **current** smaller-tree frontier after the two executed trims rather than the older pre-trim surface:
  - `scripts/test/check_archive_report_semantic_handle_receipt.py`
  - `scripts/test/check_archive_report_compaction_candidate_receipt.py`
  - `scripts/test/check_archive_report_compaction_manifest_receipt.py`
  - `scripts/test/check_archive_report_compaction_rehearsal_receipt.py`
  - `scripts/test/check_archive_report_compaction_stage_receipt.py`
- Main local result:
  - the post-trim receipt chain is fully reclosed,
  - the current live tree measures `1385` retained files and `9559773` raw bytes with an approximate revision zip of `2702609` bytes,
  - the report bucket is down to `89` files / `270444` raw bytes,
  - and the next cited frontier is now `51057` raw bytes across `6` families / `12` files with `0` projected handle gaps.

## 2026-03-19 — Research Pass (Twenty-sixth Canonical Trim Chain + Benchmark Governance Card + Frontier Reclosure)

- Added one compact governance-card note at `docs/LIBRARY/topics/rematch_benchmark_programs_should_publish_tranche_closure_validator_inventory_repro_bundle_and_risk_review_as_one_governance_card.md`, plus four tiny governance-surface notes so the semantic-handle layer can cite tranche closure, validator inventory, repro bundle posture, and risk-review cadence separately without reusing one handle path multiple times.
- Extended `docs/RESEARCH_SOURCES.md` with `RS-GR-047` (CUBE) and `RS-GR-048` (evaluation-governance / evaluator transparency), so benchmark packaging layers and governance-card publication are both backed by compact external references.
- Reclosed the current and one-trim-ahead frontier by standing-topic reuse instead of new bulky prose:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `8` additional semantic aliases for tranche closure, validator inventory, repro bundle posture, risk-review cadence, deadline inflation, delta frontiers, two-bundle composition, and compiled decision-packet shortlist laws,
  - so the refreshed smaller tree keeps the current manifest citation-first and restores `0` projected next-frontier handle gaps after the latest trim.
- Executed a chained byte-saving pass on the live tree rather than leaving rehearsed trims in place:
  - removed `35` retained report files across `18` citation-backed families from `artifacts/reports`,
  - reclaiming `269873` raw report bytes across three sequential exact-file fronts (`148819`, `61964`, then `59090`).
- Refreshed the smaller-tree archive-shaping stack so the live archive and its proofs agree again:
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
- Updated the targeted validators so the refreshed live frontier is checked against the actual smaller-tree reality:
  - `scripts/test/check_archive_report_hotspot_receipt.py`
  - `scripts/test/check_archive_report_semantic_handle_receipt.py`
  - `scripts/test/check_archive_report_compaction_candidate_receipt.py`
  - `scripts/test/check_archive_report_compaction_manifest_receipt.py`
  - `scripts/test/check_archive_report_compaction_rehearsal_receipt.py`
  - `scripts/test/check_archive_report_compaction_stage_receipt.py`
- Main local result:
  - the semantic-handle receipt is ready to cite and now recovers `6` alias-backed families covering the refreshed smaller-tree hotspot buffer,
  - the refreshed gap receipt again reports `0` current hotspot handle gaps,
  - the refreshed rehearsal again projects `0` next-frontier handle gaps,
  - the live tree now measures `1406` retained files and `9655284` raw bytes with an approximate revision zip of `2736691` bytes,
  - and the refreshed execution receipt passes `26/26` checks while proving the latest `59090`-byte cited trim actually executed on the live archive.

## 2026-03-18 — Research Pass (Twenty-fifth Canonical Trim Chain + Asynchronous Clock Contract + Frontier Reclosure)

- Added one compact inheritor-facing contract note at `docs/LIBRARY/topics/rematch_worlds_should_publish_clock_and_exogenous_event_semantics_as_a_world_contract.md`.
- Extended `docs/RESEARCH_SOURCES.md` with `RS-GR-046` (Froger et al., 2026) so asynchronous environment timing, exogenous-event cadence, and observation / action latency are treated as institution/world-contract metadata rather than hidden scheduler detail.
- Reclosed the current and one-trim-ahead hotspot surfaces by standing-topic reuse instead of new bulky prose:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `4` additional semantic aliases for path-L2 threshold fingerprint words, catalog references from paged digest catalogs, dwell-freedom tariffs, and catalog-page resolution from paged digest catalogs,
  - so the refreshed smaller tree again keeps the current manifest citation-first and restores `0` projected next-frontier handle gaps after the latest trim.
- Executed a chained byte-saving pass on the live tree rather than leaving rehearsed trims in place:
  - removed `36` retained report files across `18` citation-backed families from `artifacts/reports`,
  - reclaiming `217499` raw report bytes across three sequential exact-file fronts (`76358`, `73205`, then `67936`).
- Refreshed the smaller-tree archive-shaping stack so the live archive and its proofs agree again:
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
- Updated the targeted validators so the refreshed live frontier is checked against the actual smaller-tree reality:
  - `scripts/test/check_archive_report_semantic_handle_receipt.py`
  - `scripts/test/check_archive_report_compaction_candidate_receipt.py`
  - `scripts/test/check_archive_report_compaction_manifest_receipt.py`
  - `scripts/test/check_archive_report_compaction_rehearsal_receipt.py`
  - `scripts/test/check_archive_report_compaction_stage_receipt.py`
- Main local result:
  - the semantic-handle receipt is ready to cite at `8/8` checks passed and now recovers `4` alias-backed families covering `42785` report-bucket bytes,
  - the current exact-file compaction manifest is ready to cite at `9/9` checks passed and now targets `64478` raw bytes across `6` citation-backed families with `3` semantic-alias-backed rows,
  - the refreshed gap receipt again reports `0` current hotspot handle gaps,
  - the refreshed rehearsal again projects `0` next-frontier handle gaps,
  - the live tree now measures `1436` retained files and `9920530` raw bytes with an approximate revision zip of `2799482` bytes,
  - and the refreshed execution receipt passes `26/26` checks while proving the latest `67936`-byte cited trim actually executed on the live archive.

## 2026-03-18 — rev0281 coordination-contract pass
- Added one compact note making multi-agent topology / memory / messaging / authority explicit world-contract metadata (`RS-GR-045`).
- Recovered three standing semantic handles so the next compaction frontier can stay citation-first without minting redundant prose.
- Next intended action on this tree: rebuild receipts on the stronger pre-trim frontier, execute the cited trim, then refresh the smaller-tree receipt chain.


## 2026-03-18 — Research Pass (Twenty-second Canonical Trim + Governance Contract + Source Register Repair)

- Re-read the live frontier and found a small but real source-hygiene bug: the archive already carried a durable adaptation-contract note that cited `RS-GR-042`, but the numbered source row itself was missing from `docs/RESEARCH_SOURCES.md`.
- Fixed that bug while keeping the archive net smaller:
  - restored the missing `RS-GR-042` source row for Luo et al. (2026) so the standing adaptation-contract note cites an actual numbered entry,
  - added one compact inheritor-facing contract note at `docs/LIBRARY/topics/rematch_worlds_should_publish_sanction_and_restoration_graphs_as_a_world_contract.md`,
  - and added `RS-GR-043` (Syrnikov et al., 2026) so sanction/restoration transitions are treated as explicit institution/world-contract metadata.
- Executed one more cited exact-file compaction frontier on the live tree:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`
  - reclaimed `83154` raw report bytes from the pre-trim frontier
- Refreshed the smaller-tree archive-shaping stack so the live archive and its proofs agree again:
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
  - `artifacts/reports/artifact_summary.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`
- Updated the targeted validators so the refreshed smaller-tree frontier is checked against the new current live surface:
  - `scripts/test/check_archive_report_semantic_handle_receipt.py`
  - `scripts/test/check_archive_report_compaction_candidate_receipt.py`
  - `scripts/test/check_archive_report_compaction_manifest_receipt.py`
  - `scripts/test/check_archive_report_compaction_rehearsal_receipt.py`
  - `scripts/test/check_archive_report_compaction_stage_receipt.py`
- Main local result:
  - the semantic-handle receipt is ready to cite at `8/8` checks passed and now recovers `2` alias-backed families covering `27318` report-bucket bytes,
  - the refreshed gap receipt again reports `0` true hotspot handle gaps,
  - the refreshed rehearsal again projects `0` next-frontier handle gaps,
  - the refreshed next manifest is `80703` raw bytes across `6` families and `12` retained report files on the smaller tree,
  - the live tree now measures `1492` retained files and `10263114` raw bytes with an approximate revision zip of `2897646` bytes,
  - and the execution receipt passes `26/26` checks while proving the `83154`-byte cited trim actually executed on the live archive.

## 2026-03-18 — Research Pass (Twentieth Canonical Trim + Reputation Contract Reclosure)

- Re-read the live frontier and found that the smallest next durable improvement was to make persistent reputation worlds publish a compact contract rather than letting reputation mechanics sprawl across fresh report fanout.
- Added that inheritor-facing handle while keeping the archive net smaller:
  - added `docs/LIBRARY/topics/rematch_worlds_should_publish_reputation_assessment_and_diffusion_rules_as_a_world_contract.md`,
  - extended `docs/RESEARCH_SOURCES.md` with `RS-GR-041` on emergent reputation,
  - and recorded the implication that visibility, assessment, diffusion topology, latency/noise, and decision hooks should be published together as one world contract.
- Executed one more cited exact-file compaction frontier on the live tree:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`
  - reclaimed `101936` raw report bytes from the pre-trim frontier
- Reclosed the refreshed current and projected frontier without retaining any new bulky report pairs:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `4` additional semantic aliases for suffix counters, strict predecessor backsteps, benchmark fill-status templates, and packed scalar atoms,
  - so the refreshed smaller tree again keeps both the current hotspot surface and the projected next trim surface citation-first at `0` handle gaps.
- Refreshed the smaller-tree archive-shaping stack so the live archive and its proofs agree again:
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
  - `artifacts/reports/artifact_summary.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`
- Updated the targeted validators so the refreshed smaller-tree frontier is checked explicitly rather than against stale expectations:
  - `scripts/test/check_archive_report_semantic_handle_receipt.py`
  - `scripts/test/check_archive_report_compaction_candidate_receipt.py`
  - `scripts/test/check_archive_report_compaction_manifest_receipt.py`
  - `scripts/test/check_archive_report_compaction_rehearsal_receipt.py`
  - `scripts/test/check_archive_report_compaction_stage_receipt.py`
- Main local result:
  - the semantic-handle receipt is ready to cite at `8/8` checks passed and now recovers `4` alias-backed families covering `64419` report-bucket bytes,
  - the refreshed gap receipt now reports `0` true hotspot handle gaps,
  - the refreshed rehearsal again projects `0` next-frontier handle gaps,
  - the refreshed next manifest is `97717` raw bytes across `6` families and `12` retained report files on the smaller tree,
  - the live tree now measures `1538` retained files and `10624446` raw bytes with an approximate revision zip of `2985819` bytes,
  - and the execution receipt passes `26/26` checks while proving the `101936`-byte cited trim actually executed on the live archive.

## 2026-03-18 — Research Pass (Nineteenth Canonical Trim + Commitment Contract Alias Reclosure)

- Re-read the live frontier and found the key opportunity was not another new bulky note but semantic-handle recovery: several standing next-wave claims were already present as inheritor topics but were still being treated as missing handles.
- Fixed that bottleneck while keeping the archive net smaller:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `6` additional semantic aliases for canonical-anchor path atlases, positive-service threshold provenance, geometric-arrival time consistency, local axis persistence, paged catalog page filters, and shared-interval exact transport,
  - added one compact inheritor topic at `docs/LIBRARY/topics/rematch_worlds_should_publish_positive_service_commitment_semantics_as_a_world_contract.md`,
  - and extended `docs/RESEARCH_SOURCES.md` with `RS-GR-040` on voluntary commitment so blind-commit versus live-reoptimized promise mode is explicitly treated as institution design rather than hidden controller detail.
- Executed one more cited exact-file compaction frontier on the live tree:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`
  - reclaimed `106875` raw report bytes from the pre-trim frontier
- Refreshed the smaller-tree archive-shaping stack so the live archive and its proofs agree again:
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
  - `artifacts/reports/artifact_summary.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`
- Updated the targeted validators so the refreshed smaller-tree frontier is checked against the new handle-closed post-trim reality:
  - `scripts/test/check_archive_report_semantic_handle_receipt.py`
  - `scripts/test/check_archive_report_compaction_candidate_receipt.py`
  - `scripts/test/check_archive_report_compaction_gap_receipt.py`
  - `scripts/test/check_archive_report_compaction_manifest_receipt.py`
  - `scripts/test/check_archive_report_compaction_rehearsal_receipt.py`
  - `scripts/test/check_archive_report_compaction_stage_receipt.py`
  - `scripts/test/check_archive_report_compaction_execution_receipt.py`
- Main local result:
  - the semantic-handle layer now keeps the current hotspot surface fully citation-covered and the refreshed rehearsal at `0` projected handle gaps,
  - the refreshed next manifest is `101936` raw bytes across `6` families and `12` retained report files on the smaller tree,
  - the refreshed gap receipt now reports `0` true hotspot handle gaps,
  - the live tree now measures `1549` retained files and `10718558` raw bytes with an approximate revision zip of `3009384` bytes,
  - and the execution receipt passes `26/26` checks while proving the `106875`-byte cited trim actually executed on the live archive.

## 2026-03-18 — Research Pass (Fifteenth Canonical Trim + Frontier Shortlist Reclosure)

- Executed the standing rev0271 manifest on the live tree rather than leaving another rehearsal in place:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`
  - reclaimed `132685` raw report bytes from the cited frontier
- Found the real smaller-tree bottleneck immediately after the trim: the refreshed hotspot and one-trim-ahead rehearsal frontier were no longer fully handle-covered because the archive had not yet wired standing handles for the decision-packet compiled-shortlist, equiprobable exact-threshold, shortest-script transport-frontier, and corridor-exit families into the semantic bridge layer.
- Fixed that bottleneck without minting new durable note mass:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `3` additional semantic aliases for compiled-frontier shortlists, equiprobable exact-threshold switching, and shortest-script transport-frontier regimes,
  - restored the corridor-exit alias with stricter evidence markers,
  - and widened the buffered hotspot scan from `12` to `13` families so the one-trim-ahead transport-frontier family is recovered before it turns into a false projected gap.
- Refreshed the smaller-tree archive-shaping stack so the live archive and its proofs agree again:
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
  - `artifacts/reports/artifact_summary.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`
- Updated the targeted validators so the refreshed smaller-tree frontier is checked explicitly rather than against stale pre-trim expectations:
  - `scripts/test/check_archive_report_semantic_handle_receipt.py`
  - `scripts/test/check_archive_report_compaction_candidate_receipt.py`
  - `scripts/test/check_archive_report_compaction_manifest_receipt.py`
  - `scripts/test/check_archive_report_compaction_rehearsal_receipt.py`
  - `scripts/test/check_archive_report_compaction_stage_receipt.py`
- Main local result:
  - the semantic-handle receipt is ready to cite at `8/8` checks passed and now recovers `5` buffered hotspot families through the projected rank-13 frontier,
  - the current exact-file compaction manifest is ready to cite at `9/9` checks passed and now targets `126583` raw bytes across `6` citation-backed families with `4` semantic-alias-backed rows,
  - the refreshed gap receipt again reports `0` current hotspot handle gaps,
  - the refreshed rehearsal again projects `0` next-frontier handle gaps,
  - and the refreshed execution receipt passes `26/26` checks while proving the `132685`-byte cited trim actually executed on the live archive.

## 2026-03-18 — Research Pass (Twelfth Canonical Trim + Mutation-Surface Reclosure)

- Executed the standing rev0268 manifest on the live tree rather than leaving another rehearsal in place:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`
  - reclaimed `147050` raw report bytes from the cited frontier
- Found the real smaller-tree bottleneck immediately after the trim: the refreshed one-trim-ahead rehearsal frontier exposed four true handle gaps in transition-budget, dwell-commitment, rank-clock, and mutation-surface families even though three were already conceptually solved and one needed only a tiny inheritor-facing note.
- Fixed that bottleneck by extending `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `4` additional semantic aliases pointing the exposed families at durable library topics for:
  - compact repeat-sidecar rewrite budgeting,
  - neutral exact dwell commitments,
  - positive-service local rank clocks,
  - and rematch benchmark mutation-surface discipline.
- Added one compact inheritor-facing topic so benchmark fill work now has a durable non-report handle for the mutation-surface family:
  - `docs/LIBRARY/topics/filled_rematch_world_benchmarks_should_freeze_copied_contract_state_and_mutate_only_seed_designated_prefixes.md`
- Tightened execution-proof durability instead of relying on operator memory:
  - updated `scripts/tools/build_archive_report_compaction_execution_receipt.py` so explicit `--pre-package` / `--pre-manifest` reseeding takes priority over any stale self-seeded execution receipt,
  - then rebuilt the live execution receipt from the actual rev0268 pre-trim package + manifest plus the rev0268 pre-trim archive zip.
- Refreshed the smaller-tree archive-shaping stack so the live archive and its proofs agree again:
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
  - `artifacts/reports/artifact_summary.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`
- Updated the targeted validators so the refreshed smaller-tree frontier is checked explicitly rather than against stale pre-trim expectations:
  - `scripts/test/check_archive_report_semantic_handle_receipt.py`
  - `scripts/test/check_archive_report_compaction_candidate_receipt.py`
  - `scripts/test/check_archive_report_compaction_manifest_receipt.py`
  - `scripts/test/check_archive_report_compaction_rehearsal_receipt.py`
  - `scripts/test/check_archive_report_compaction_stage_receipt.py`
- Main local result:
  - the semantic-handle receipt is ready to cite at `8/8` checks passed and now recovers `5` buffered hotspot families covering `115909` report-bucket bytes,
  - the current exact-file compaction manifest is ready to cite at `9/9` checks passed and now targets `141274` raw bytes across `6` citation-backed families,
  - the refreshed rehearsal again projects `0` next-frontier handle gaps,
  - and the refreshed execution receipt passes `26/26` checks while proving the `147050`-byte cited trim actually executed on the live archive.

## 2026-03-18 — Research Pass (Interval Reclosure + Eleventh Canonical Trim)

- Executed the standing rev0267 manifest on the live tree rather than leaving another rehearsal in place:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`
  - reclaimed `152663` raw report bytes from the cited frontier
- Found the real smaller-tree bottleneck immediately after the trim: the refreshed rehearsal frontier exposed one true handle gap in the bounded local positive-service interval family even though the archive already carried the right inheritor-facing topic.
- Fixed that bottleneck by extending `scripts/tools/build_archive_report_semantic_handle_receipt.py` with one additional semantic alias pointing the exposed family at the standing clock-interval topic:
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_bounded_positive_service_local_weakening_queries_as_clock_intervals.md`
- Refreshed the smaller-tree archive-shaping stack so the live archive and its proofs agree again:
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
  - `artifacts/reports/artifact_summary.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`
- Updated the targeted validators so the refreshed smaller-tree frontier is checked explicitly rather than against stale pre-trim expectations:
  - `scripts/test/check_archive_report_semantic_handle_receipt.py`
  - `scripts/test/check_archive_report_compaction_candidate_receipt.py`
  - `scripts/test/check_archive_report_compaction_manifest_receipt.py`
  - `scripts/test/check_archive_report_compaction_rehearsal_receipt.py`
  - `scripts/test/check_archive_report_compaction_stage_receipt.py`
- Main local result:
  - the semantic-handle receipt is ready to cite at `8/8` checks passed and now recovers `3` buffered hotspot families covering `73677` report-bucket bytes,
  - the current exact-file compaction manifest is ready to cite at `9/9` checks passed and now targets `147050` raw bytes across `6` citation-backed families,
  - the refreshed rehearsal again projects `0` next-frontier handle gaps,
  - and the refreshed execution receipt passes `26/26` checks while proving the `152663`-byte cited trim actually executed on the live archive.

## 2026-03-18 — Research Pass (Eighth Canonical Trim + Fixed-Point Receipt Stabilization)

- Completed the in-flight eighth canonical trim and then repaired the proof-layer drift it exposed on the smaller tree:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `188715` raw report bytes from the standing rev0264 manifest,
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
- Fixed the real fixed-point instability instead of leaving a "rerun twice" ritual for future inheritors:
  - updated `scripts/report/summarize_artifacts.py` so the artifact summary keeps its prior timestamp when the category surface is unchanged,
  - updated `scripts/tools/build_rematch_world_benchmark_package_receipt.py` and `scripts/tools/build_archive_report_hotspot_receipt.py` so generated size-control outputs are excluded from fixed-point package/hotspot measurement,
  - updated `scripts/tools/build_archive_report_compaction_rehearsal_receipt.py` so projected report-bucket totals are computed on the same filtered live surface as the package receipt,
  - updated `scripts/tools/build_archive_report_compaction_execution_receipt.py`, `schemas/archive_report_compaction_execution_receipt.schema.json`, and `scripts/test/check_archive_report_compaction_execution_receipt.py` so signed same-pass filtered drift in report-bucket file count, pair count, and raw-byte deltas is represented explicitly and reconciled exactly.
- Main local result:
  - the retained tree now measures `1676` files and `12157862` raw bytes with an approximate revision zip of `3289697` bytes,
  - the live report bucket now measures `400` files and `3097228` raw bytes,
  - the semantic-handle layer remains ready to cite at `8/8` checks passed with `5` buffered aliases covering `141792` report-bucket bytes,
  - the refreshed first-pass exact-file frontier is `208051` raw bytes across `6` citation-backed families,
  - the refreshed rehearsal again projects `0` next-frontier handle gaps,
  - and the full targeted receipt/validator sweep now passes sequentially on the live tree without needing a dependency-order workaround.

## 2026-03-18 — Research Pass (Eighth Canonical Trim + Frontier Reclosure)

- Executed the standing rev0264 manifest on the live tree rather than leaving another rehearsal in place:
  - removed `12` retained report files across `6` families from `artifacts/reports`
  - reclaimed `188715` raw report bytes from the cited frontier
- Found the real smaller-tree bottleneck immediately after the trim: the refreshed first-pass frontier was citation-backed, but the newly exposed hotspot buffer and one-trim-ahead rehearsal frontier were missing semantic reuse for four already-solved families.
- Fixed that bottleneck by extending `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `4` additional semantic aliases that point the exposed families at existing library topics for:
  - overshoot-axis admission profiles,
  - canonical reduced-mean batch summaries,
  - one-burden-axis same-deadline live caching,
  - and mean-projection compromise witness choice.
- Refreshed the smaller-tree archive-shaping stack so the live archive and its proofs agree again:
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
  - `artifacts/reports/artifact_summary.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`
- Updated the targeted validators so the refreshed smaller-tree frontier is checked explicitly rather than against stale pre-trim expectations:
  - `scripts/test/check_archive_report_semantic_handle_receipt.py`
  - `scripts/test/check_archive_report_compaction_candidate_receipt.py`
  - `scripts/test/check_archive_report_compaction_manifest_receipt.py`
  - `scripts/test/check_archive_report_compaction_rehearsal_receipt.py`
  - `scripts/test/check_archive_report_compaction_stage_receipt.py`
- Main local result:
  - the semantic-handle receipt is ready to cite at `8/8` checks passed and now recovers `5` buffered hotspot families covering `141792` report-bucket bytes,
  - the current exact-file compaction manifest is ready to cite at `9/9` checks passed and now targets `208051` raw bytes across `6` citation-backed families,
  - the refreshed rehearsal again projects `0` next-frontier handle gaps,
  - and the refreshed execution receipt passes `24/24` checks while proving the `188715`-byte cited trim actually executed on the live archive.

## 2026-03-18 — Research Pass (Semantic Reclosure + Sixth Canonical Trim)

- Executed the standing rev0262 manifest on the live tree rather than leaving another rehearsal in place:
  - removed `12` retained report files across `6` families from `artifacts/reports`
  - reclaimed `226640` raw report bytes from the cited frontier
- Found the real smaller-tree bottleneck immediately after the trim: the new current hotspot surface was no longer fully recovered by the buffered semantic-handle layer even though the archive already carried the needed inheritor-facing topics.
- Fixed that bottleneck by extending `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `6` additional semantic aliases that point the new hotspot families at existing library topics for:
  - positive same-deadline live arrival floors,
  - width-only weakening service frontiers,
  - geometric-arrival exact-batch wait value,
  - measured decision-packet shortlist frontiers,
  - batch-`L2` two-integer sufficient statistics,
  - and SG-003 phase-3 world-emission retirement.
- Refreshed the smaller-tree archive-shaping stack so the live archive and its proofs agree again:
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
  - `artifacts/reports/artifact_summary.json`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`
- Main local result:
  - the semantic-handle receipt is ready to cite at `8/8` checks passed and now recovers `7` buffered hotspot families covering `232177` report-bucket bytes,
  - the current exact-file compaction manifest is ready to cite at `9/9` checks passed and now targets `202109` raw bytes across `6` citation-backed families,
  - the refreshed rehearsal again projects `0` next-frontier handle gaps,
  - and the refreshed execution receipt passes `24/24` checks while proving the `226640`-byte cited trim actually executed on the live archive.

## 2026-03-17 — Research Pass (Scratch-Stage Before Canonical Trim)

- Added one compact compaction-stage receipt so future archive-size work can stage the exact-file trim reversibly inside `examples/scratch` before any retained report path is canonically removed:
  - `schemas/archive_report_compaction_stage_receipt.schema.json`
  - `scripts/tools/build_archive_report_compaction_stage_receipt.py`
  - `examples/snapshots/archive_report_compaction_stage_receipt.json`
  - `scripts/test/check_archive_report_compaction_stage_receipt.py`
  - `docs/LIBRARY/topics/archive_size_control_should_stage_one_manifest_inside_scratch_before_canonical_trim.md`
- Tightened archive-size workflow guidance so future inheritors stage the cited manifest inside scratch, validate the trimmed tree, and only then delete the staged copy before the next revision zip:
  - `docs/DATA_MANAGEMENT.md`
  - `docs/BENCHMARK_PROGRAM.md`
  - `docs/LIBRARY/README.md`
- Main local result:
  - the new stage receipt is ready to cite and mirrors the current exact-file frontier of `12` retained report files across `6` families totaling `554504` raw bytes,
  - it keeps the raw tree flat during the temporary scratch stage while projecting the same post-trim totals already proven by the compaction rehearsal,
  - and it makes the first byte-saving pass reversible without weakening the package rule that `examples/scratch` must be empty again before the next zip is cut.

## 2026-03-17 — Research Pass (Buffered Semantic Reuse for Rehearsal Frontier)

- Extended the semantic-handle layer so archive-size work now scans a buffered hotspot surface instead of stopping at the literal current top-10 table; this lets one semantic-handle receipt cover the one-trim-ahead rehearsal frontier too:
  - `scripts/tools/build_archive_report_semantic_handle_receipt.py`
  - `examples/snapshots/archive_report_semantic_handle_receipt.json`
  - `docs/LIBRARY/topics/archive_size_control_should_reuse_semantic_handles_before_minting_new_ones.md`
- Recovered the projected second-wave countdown family by reusing the existing inheritor-facing topic `docs/LIBRARY/topics/rematch_worlds_should_run_positive_batches_by_precomputed_remaining_horizon_countdowns.md` instead of minting another compact note.
- Tightened archive-size workflow guidance so future inheritors treat the semantic-handle receipt as a one-trim-ahead scan and can execute the first cited trim whenever the rehearsal keeps the projected frontier handle-covered:
  - `docs/DATA_MANAGEMENT.md`
  - `docs/BENCHMARK_PROGRAM.md`
- Main local result:
  - the semantic-handle receipt is ready to cite and now recovers `4` buffered hotspot families covering `302376` report-bucket bytes,
  - the compaction rehearsal no longer exposes any projected zero-handle family after the first trim,
  - and the first manifest trim is now semantically clear to execute later without minting another durable note first.

## 2026-03-17 — Research Pass (Compaction Manifest Rehearsal)

- Added one compact compaction-rehearsal receipt so future archive-size work can preview the first exact-file trim before removing any retained report paths:
  - `schemas/archive_report_compaction_rehearsal_receipt.schema.json`
  - `scripts/tools/build_archive_report_compaction_rehearsal_receipt.py`
  - `examples/snapshots/archive_report_compaction_rehearsal_receipt.json`
  - `scripts/test/check_archive_report_compaction_rehearsal_receipt.py`
  - `docs/LIBRARY/topics/archive_size_control_should_rehearse_one_manifest_before_removing_report_paths.md`
- Tightened archive-size workflow guidance so exact-file trimming now runs through one rehearsal step after the manifest and before any retained report paths are removed:
  - `docs/DATA_MANAGEMENT.md`
  - `docs/BENCHMARK_PROGRAM.md`
  - `docs/LIBRARY/README.md`
- Main local result:
  - the rehearsal previews reclaiming the current `554504`-byte first-pass frontier across `12` retained report files,
  - the projected leading remaining hotspot becomes `rematch_proxy_delta_topology`,
  - and the projected second-wave frontier exposes one zero-handle family (`rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_deadline_countdown_law`), so future compaction should recover that durable handle before any retained report paths are actually removed.

## 2026-03-17 — Research Pass (Exact-File Compaction Manifest)

- Added one compact exact-file compaction manifest so future archive-size work can act on the current citation-backed trim frontier by explicit retained report paths instead of by family-name archaeology:
  - `schemas/archive_report_compaction_manifest_receipt.schema.json`
  - `scripts/tools/build_archive_report_compaction_manifest_receipt.py`
  - `examples/snapshots/archive_report_compaction_manifest_receipt.json`
  - `scripts/test/check_archive_report_compaction_manifest_receipt.py`
  - `docs/LIBRARY/topics/archive_size_control_should_trim_exact_report_paths_from_one_manifest.md`
- Tightened archive-size workflow guidance so once the hotspot surface is already handle-covered, the next byte-saving pass starts from one exact-file manifest rather than from manual report discovery:
  - `docs/DATA_MANAGEMENT.md`
  - `docs/BENCHMARK_PROGRAM.md`
  - `docs/LIBRARY/README.md`
- Kept the measurement stack stable by excluding the new size-control receipt from package/hotspot fixed-point loops and from handle-search surfaces:
  - `scripts/tools/build_rematch_world_benchmark_package_receipt.py`
  - `scripts/tools/build_archive_report_hotspot_receipt.py`
  - `scripts/tools/build_archive_report_compaction_candidate_receipt.py`
  - `scripts/tools/build_archive_report_compaction_gap_receipt.py`
- Main local result:
  - the new compaction manifest is ready to cite at `9/9` checks passed,
  - it turns the standing first-pass frontier into `12` exact retained report files across `6` families covering `554504` report-bucket bytes,
  - and the first explicit trim row is `rematch_proxy_noise_semantics`, now reducible by citing `2` durable handles and then removing its one retained JSON+MD pair.


## 2026-03-17 — Research Pass (Final Semantic Handle Recovery)

- Extended the semantic-handle receipt so archive-size work now reuses the existing closed-form live-deadline topic for the remaining apparent hotspot gap instead of minting a redundant new note:
  - `scripts/tools/build_archive_report_semantic_handle_receipt.py`
  - `examples/snapshots/archive_report_semantic_handle_receipt.json`
  - `scripts/test/check_archive_report_semantic_handle_receipt.py`
  - `docs/LIBRARY/topics/archive_size_control_should_reuse_semantic_handles_before_minting_new_ones.md`
- Tightened the compaction-gap logic so the archive can truthfully represent a zero-gap state when the current top hotspot surface is already fully covered by durable non-report handles:
  - `schemas/archive_report_compaction_gap_receipt.schema.json`
  - `scripts/tools/build_archive_report_compaction_gap_receipt.py`
  - `examples/snapshots/archive_report_compaction_gap_receipt.json`
  - `scripts/test/check_archive_report_compaction_gap_receipt.py`
- Refreshed the archive-shaping guidance so future inheritors stop at semantic-handle reuse when the gap receipt is empty rather than minting another note by habit:
  - `docs/DATA_MANAGEMENT.md`
  - `docs/BENCHMARK_PROGRAM.md`
- Main local result:
  - the semantic-handle receipt is ready to cite at `8/8` checks passed and now recovers `3` hotspot families covering `238269` report-bucket bytes,
  - the current top-hotspot handle-gap surface collapses to `0` families and `0` blocked bytes,
  - the citation-backed first-pass compaction frontier stays explicit at `6` families covering `554504` report-bucket bytes,
  - and the reopened family is `geometric_arrival_live_deadline_formula_law`, now correctly backed by `rematch_worlds_should_solve_same_deadline_live_minima_from_one_closed_form.md`.


## 2026-03-17 — Research Pass (Semantic Handle Receipt)

- Added one compact semantic-handle receipt so archive-size work can reuse existing durable library topics when literal family-name matching misses them, instead of minting redundant new notes or treating false gaps as real gaps:
  - `schemas/archive_report_semantic_handle_receipt.schema.json`
  - `scripts/tools/build_archive_report_semantic_handle_receipt.py`
  - `examples/snapshots/archive_report_semantic_handle_receipt.json`
  - `scripts/test/check_archive_report_semantic_handle_receipt.py`
  - `docs/LIBRARY/topics/archive_size_control_should_reuse_semantic_handles_before_minting_new_ones.md`
- Tightened archive-size workflow guidance so semantic-handle reuse now comes before minting any new durable note for a hotspot family:
  - `docs/DATA_MANAGEMENT.md`
  - `docs/BENCHMARK_PROGRAM.md`
  - `docs/LIBRARY/README.md`
- Upgraded the standing compaction receipts to consume that semantic bridge, turning prior false gaps into citation-backed candidates and leaving only one true missing-handle family:
  - `schemas/archive_report_compaction_candidate_receipt.schema.json`
  - `schemas/archive_report_compaction_gap_receipt.schema.json`
  - `scripts/tools/build_archive_report_compaction_candidate_receipt.py`
  - `scripts/tools/build_archive_report_compaction_gap_receipt.py`
  - `examples/snapshots/archive_report_compaction_candidate_receipt.json`
  - `examples/snapshots/archive_report_compaction_gap_receipt.json`
  - `scripts/test/check_archive_report_compaction_candidate_receipt.py`
  - `scripts/test/check_archive_report_compaction_gap_receipt.py`
- Main local result:
  - the new semantic-handle receipt is ready to cite at `8/8` checks passed,
  - it recovers `2` hotspot families covering `137210` report-bucket bytes without minting new durable notes,
  - it promotes `rematch_proxy_delta_policy_box_corner` into the first-pass citation-backed trim set,
  - and it shrinks the true remaining handle-gap surface to one family: `geometric_arrival_live_deadline_formula_law` (`101059` bytes).


## 2026-03-17 — Research Pass (Compaction Handle-Gap Receipt)

- Added one compact handle-gap receipt so the inheritor can see which large report hotspots still lack any durable non-report handle, instead of only seeing the already-safe first-pass trim list:
  - `schemas/archive_report_compaction_gap_receipt.schema.json`
  - `scripts/tools/build_archive_report_compaction_gap_receipt.py`
  - `examples/snapshots/archive_report_compaction_gap_receipt.json`
  - `scripts/test/check_archive_report_compaction_gap_receipt.py`
  - `docs/LIBRARY/topics/archive_size_control_should_cite_one_compaction_gap_receipt.md`
- Tightened archive-size workflow guidance so handle-unlock work is now explicit before more report fanout lands next to blocked hotspots:
  - `docs/DATA_MANAGEMENT.md`
  - `docs/BENCHMARK_PROGRAM.md`
- Regenerated the compact discovery / size-control surfaces so the new schema, validator, and package-size state stay aligned on the final tree:
  - `docs/SCHEMA_INVENTORY.md`
  - `artifacts/reports/schema_inventory.json`
  - `docs/VALIDATOR_INVENTORY.md`
  - `artifacts/reports/validator_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`
  - `artifacts/reports/artifact_summary.json`
  - `examples/snapshots/rematch_world_benchmark_package_receipt.json`
  - `examples/snapshots/archive_report_hotspot_receipt.json`
  - `examples/snapshots/archive_report_compaction_candidate_receipt.json`
- Main local result:
  - the new gap receipt is ready to cite at `7/7` checks passed,
  - it identifies `3` top-10 hotspot families with zero durable handles covering `238269` report-bucket bytes (`0.042781` share),
  - it points the largest current unlock move at `geometric_arrival_live_deadline_formula_law` (`101059` bytes) via one compact `library_topic` handle,
  - and the combined first-pass candidates plus handle-gap frontier now spans `817452` report-bucket bytes (`0.146773` share) without adding a new report family.


## 2026-03-17 — Research Pass (Compaction Candidate Receipt)

- Added one compact archive-facing compaction-candidate receipt so the inheritor can move from “these report families are large” to “these report families are already citation-backed and safe to compact first” without reopening the whole archive:
  - `schemas/archive_report_compaction_candidate_receipt.schema.json`
  - `scripts/tools/build_archive_report_compaction_candidate_receipt.py`
  - `examples/snapshots/archive_report_compaction_candidate_receipt.json`
  - `scripts/test/check_archive_report_compaction_candidate_receipt.py`
  - `docs/LIBRARY/topics/archive_size_control_should_cite_one_compaction_candidate_receipt.md`
- Tightened archive guidance:
  - `docs/DATA_MANAGEMENT.md` now says to build the compaction-candidate receipt before touching a specific hotspot family,
  - and `docs/BENCHMARK_PROGRAM.md` now adds the same citation-backed compaction step after the hotspot receipt in the zip-cut workflow.
- Main local result:
  - the new durable receipt stays tiny while converting the hotspot table into `6` citation-backed first-pass compaction targets,
  - the priority candidates cover a meaningful share of the retained report bucket without adding another report pair,
  - and the first-line trim set is now explicit: `rematch_proxy_noise_semantics`, `rematch_proxy_delta_width_floor_plateau`, `rematch_proxy_delta_hazard_threshold`, `rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_saved_state_resolver`, `rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis`, and `rematch_proxy_delta_topology`.

## 2026-03-17 — Research Pass (Report Hotspot Receipt)

- Added one compact archive-facing hotspot receipt so the inheritor can cite the specific retained report families most worth compacting next instead of reopening the full archive-size profile or spelunking `artifacts/reports` by hand:
  - `schemas/archive_report_hotspot_receipt.schema.json`
  - `scripts/tools/build_archive_report_hotspot_receipt.py`
  - `examples/snapshots/archive_report_hotspot_receipt.json`
  - `scripts/test/check_archive_report_hotspot_receipt.py`
  - `docs/LIBRARY/topics/archive_size_control_should_cite_one_report_hotspot_receipt.md`
- Tightened archive guidance:
  - `docs/DATA_MANAGEMENT.md` now says to build the hotspot receipt when `artifacts/reports` is the main retained growth surface,
  - and `docs/BENCHMARK_PROGRAM.md` now points size-discipline work from the package receipt to the hotspot receipt before any further report fanout is added.
- Main local result:
  - the new durable receipt stays tiny while aligning exactly with the standing package receipt,
  - confirms `artifacts/reports` remains the largest artifact bucket,
  - exposes the top 10 report families as the dominant retained compaction surface,
  - and names a short first-pass target list so future archive shaping can stay citation-first instead of report-first.

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

- Added one compact benchmark-facing winner-triage handoff so the next inheritor can answer the practical question "which apparent leader changes are actually decision-relevant?" from one frozen packet instead of reopening the proxy-era live-contender, winner-certification, and materiality reports:
  - `schemas/rematch_world_benchmark_winner_triage_handoff.schema.json`
  - `scripts/tools/build_rematch_world_benchmark_winner_triage_handoff.py`
  - `examples/snapshots/rematch_world_benchmark_winner_triage_handoff.json`
  - `artifacts/reports/rematch_world_benchmark_winner_triage_handoff_snapshot_20260317.{md,json}`
  - `scripts/test/check_rematch_world_benchmark_winner_triage_handoff.py`
- Main durable consequence:
  - the benchmark seed now carries the live contender union `CCEEE`, `CCDDE`, and `always_c`,
  - preserves the single uncertified tested panel at `extortion=80, delay=2`,
  - and makes the first materiality seam explicit: `3` certified panels already become practical ties at delta `0.005`, while the lone uncertified panel becomes a practical tie at delta `0.01`.

- Added one compact benchmark-facing publishable-delta shortlist handoff so the next inheritor can start SESOI-band planning from one frozen packet instead of reopening the proxy-era frontier, hazard, persistence, and publishability reports:
  - `schemas/rematch_world_benchmark_delta_shortlist_handoff.schema.json`
  - `scripts/tools/build_rematch_world_benchmark_delta_shortlist_handoff.py`
  - `examples/snapshots/rematch_world_benchmark_delta_shortlist_handoff.json`
  - `artifacts/reports/rematch_world_benchmark_delta_shortlist_handoff_snapshot_20260317.{md,json}`
  - `scripts/test/check_rematch_world_benchmark_delta_shortlist_handoff.py`
- Main durable consequence:
  - the benchmark seed now carries the strict `family4_width0p0010_hazard1000_sub0p01` shortlist directly,
  - so the first-line copied SESOI anchors are explicit at `0.00602` (`TTTMMMMMU`) and `0.00744` (`TTTMMMMUU`) across budget caps `10, 20, 50, 100`,
  - while the wider proxy ladder family stays cited rather than copied.

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

- Added one exact live margin ceiling law so future inheritors can quote same-deadline stateless live realized-margin promises from one closed-form ceiling instead of re-solving timeout, batch, or hold-cost frontiers online:
  - `scripts/analysis/geometric_arrival_live_margin_ceiling_law.py`
  - `scripts/report/build_geometric_arrival_live_margin_ceiling_law_snapshot.py`
  - `artifacts/reports/geometric_arrival_live_margin_ceiling_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_geometric_arrival_live_margin_ceiling_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_quote_same_deadline_live_promises_by_margin_ceiling.md`
- Main local result: same-deadline stateless live control preserves original realized margin promises exactly up to `max(0, (1 - (1 - p)^floor((H + 1) / 2)) * (state_prefix_bits / (n(n + 1)) - hold_cost / p))`; the ceiling is the same better-of-close-or-blind value already implied by the effective half-horizon law, zero-only contexts arise exactly when that raw effective blind value is nonpositive, and deadlines `2j - 1` and `2j` share the same nonnegative ceiling.
- Validation summary: audited `156672` state contexts and `1024` universal contexts, checked `313344` state boundary comparisons and `2048` universal boundary comparisons, observed `87280` positive-ceiling versus `69392` zero-only state contexts and `560` positive-ceiling versus `464` zero-only universal contexts, and confirmed odd-even deadline-pair plateaus on `78336` state pairs and `512` universal pairs.
- Implementor consequence: future sessions can quote same-deadline live realized-margin promises from one direct ceiling calculation and can treat the controller frontier as a two-regime split between positive-ceiling contexts and zero-only immediate-close contexts.


## 2026-03-16 — Research Pass CCVII (Compact Repeat-State Weakening Portfolio Service Mode-Suffix Batch Shared Half-Step Shared-Interval-State Equiprobable Exact-Shortest-Script Geometric-Arrival Live Hold-Cost Ceiling Law)

- Added one exact live hold-cost ceiling law so future inheritors can decide same-deadline stateless live wait affordability from one closed-form threshold instead of re-solving timeout or batch frontiers online:
  - `scripts/analysis/geometric_arrival_live_hold_cost_ceiling_law.py`
  - `scripts/report/build_geometric_arrival_live_hold_cost_ceiling_law_snapshot.py`
  - `artifacts/reports/geometric_arrival_live_hold_cost_ceiling_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_geometric_arrival_live_hold_cost_ceiling_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_budget_positive_same_deadline_live_waits_by_hold_cost_ceiling.md`
- Main local result: for positive margins, same-deadline live waiting is promise-safe exactly while `hold_cost <= p * (state_prefix_bits / (n(n + 1)) - m / (1 - (1 - p)^floor((H + 1) / 2)))`; the ceiling is negative iff the positive promise is impossible even at zero hold cost, it is unbounded at zero floor because immediate close is already safe, and deadlines `2j - 1` and `2j` share the same positive ceiling.
- Validation summary: audited `195840` state contexts and `1280` universal contexts, checked `199482` state boundary comparisons and `1294` universal boundary comparisons, observed `42810` feasible versus `113862` impossible positive state contexts and `270` feasible versus `754` impossible positive universal contexts, and confirmed odd-even deadline-pair plateaus on `78336` state pairs and `512` universal pairs.
- Implementor consequence: future sessions can budget same-deadline live wait affordability by one direct per-tick hold-cost threshold, keyed by the same effective half-horizon and odd/even pair collapse already established for positive promise preservation.


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

- Added one exact fixed-timeout batch-cap law so future inheritors can start from the timeout budget they will actually run and recover the largest admissible shared-state equiprobable exact batch length directly:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_batch_cap_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_batch_cap_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_batch_cap_law_snapshot_20260316.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_batch_cap_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_cap_batches_directly_from_fixed_timeouts_and_margin_floors.md`
- Tightened planning guidance:
  - with fixed timeout `T`, realized net wait value is exactly `(1 - (1 - p)^T) * (state_prefix_bits / (n(n+1)) - c / p)` whenever `p > 0`,
  - so the exact fixed-timeout batch cap is the largest `n` with `n(n+1) <= p * state_prefix_bits / (c + p * m / (1 - (1 - p)^T))`,
  - the all-state guardrail is the same rule with `state_prefix_bits = 7`,
  - longer timeouts can only weakly increase the admissible batch cap because the timeout capture factor is monotone in `T`,
  - and at `T = 1` the realized-margin tax simplifies exactly to `m`, so the denominator collapses to `c + m` independent of arrival hazard.
- Main local result:
  - all `153 × 4 × 4 × 6 × 5 × 12 = 881280` audited state/batch/probability/cost/timeout/margin panels matched the closed-form cap rule exactly,
  - all `153 × 4 × 4 × 6 × 5 = 73440` audited state/probability/cost/timeout/margin schedule inversions matched the exact frontier,
  - the audited state schedule mix was `69353` feasible and `4087` impossible,
  - all `153 × 4 × 4 × 5 = 12240` audited state timeout ladders were monotone, with `3975` showing strict growth somewhere across `T ∈ {1,2,3,4,5,6}`,
  - all `4 × 4 × 6 × 5 × 12 = 5760` audited universal batch panels and all `4 × 4 × 6 × 5 = 480` universal schedule inversions matched the seven-bit lower-envelope guardrail exactly,
  - and the universal timeout ladders were all monotone as well, with `25 / 80` showing strict growth.

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

- Added one exact residual-headroom certificate so future inheritors can see where any further **equiprobable** compression effort could still matter after the archive's current half-step binary-prefix codecs were already certified as uniform-prefix-optimal:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_equiprobable_entropy_headroom_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_equiprobable_entropy_headroom_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_equiprobable_entropy_headroom_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_equiprobable_entropy_headroom_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_remaining_half_step_equiprobable_transport_headroom_as_tiny_and_localized.md`
- Main local result:
  - the exact `153`-state interval prefix and the inherited canonical shortest-script prefix each still retain `10.619660068024132` total bits of equiprobable entropy headroom (`0.0694095429282623` bits per state on average),
  - the exact `513`-word global shortest-script prefix retains only `0.5558969935818823` total bits of equiprobable entropy headroom (`0.001083619870529985` bits per word on average),
  - the state-known local-choice prefix retains `14.120249610575684` total bits of equiprobable entropy headroom across the represented `513`-word catalog (`0.027524853042057863` bits per word on average),
  - all positive state-known local-choice headroom is concentrated in the `15` interior singleton families, while the size-`1` and size-`2` local-choice families are already entropy-tight,
  - and the archive now records concrete stopping thresholds: at the present mean gaps, the exact-word regime would need about `923` represented words to save one whole bit on average, the interval/canonical regime about `15` states, the full state-known local-choice regime about `37` words, and the singleton local-choice subcatalog about `20` words.

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

## 2026-03-09 — Research Pass CLXIX (Dense-Codec Arithmetic-Decode Law)

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

## 2026-03-09 — Research Pass CLXVII (Dense Triangular Interval-State Codec)

- Tightened the normalized downstream exact-state codec so the shared batch path-`L2` / path-`Linf` feasible interval kernel no longer needs two explicit endpoint ranks:
  - `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law_snapshot_20260309.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_address_exact_normalized_half_step_interval_states_by_dense_triangular_index.md`
- Main local result: every realized feasible interval `[a,b]` now has a bijective dense index in `0..152` via `a*(35-a)/2 + (b-a)`, so the exact downstream state fits in `8` fixed bits instead of `10` for a raw endpoint pair while still decoding back to the same half-step kernel and canonical shortest generator word on all `153` realized states.
- Implementor consequence: future sessions should treat the dense triangular interval index as the base exact codec for normalized downstream state, and only expand back to endpoint pairs, canonical shortest words, or local choice indices when one of those surfaces is specifically needed.

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
  - the maximum local choice index is only `17`, with the exact fixed-width bit spectrum `33` states at `0` bits, `105` states at `1` bit, and `15` interior singleton states at `5` bits,
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

- Added an exact checkpoint staircase for the saved repeat-uncertainty operating modes:
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_checkpoint_staircase_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_checkpoint_staircase_snapshot_20260308.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_checkpoint_staircase.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_treat_compact_repeat_uncertainty_lanes_as_a_checkpoint_staircase.md`
- Main local result:
  - exact checkpoint-union counts now descend with relaxed guarantees as `14` (`0.99` at dwell `2`), `8` (`0.95` at dwell `13`), and `5` (`0.85` at dwell `25`),
  - the near-exact lane adds six extra checkpoints beyond the near-optimal tier, including the unique tail checkpoint `255`,
  - and the relaxed lower-guarantee tier deletes the late-tail pair `230/239` and mid-band `24/63`, leaving only one new checkpoint marker `56`.

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

- Added a repeat-uncertainty dwell-anchor chooser for compact repeat sidecars so the archive can keep one minimum-dwell preset safe across a whole repeat-budget band instead of anchoring on a single guessed repeat rate:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_repeat_uncertainty_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_repeat_uncertainty_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_min_dwell_repeat_uncertainty.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_min_dwell_anchors_from_repeat_uncertainty_overlaps.md`
- Main local result:
  - over repeat budgets `0.15`–`0.25`, the `0.99`-safe overlap shrinks to dwell `1`–`2`, so near-exact tuning is fragile,
  - the robust near-optimal preset is dwell `9` with a ±`8`-append margin and worst-case preserved gain share `0.980481`,
  - the broader simplicity-first preset is dwell `16` with a ±`15`-append margin and the same worst-case preserved gain share `0.980481`,
  - and the selected transition range at those anchors stays within `2`–`5` and `0`–`5` respectively across the whole band.
- Implementor consequence:
  - estimate a plausible repeat-budget band instead of one scalar,
  - choose the midpoint of the minimum-dwell overlap that survives the whole band at the gain share you care about,
  - and keep dwell `9` as the current robust default when repeat volume is uncertain.

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
  - the exact switch-cost frontier at `0.18` expected repeats has `9` regimes,
  - all micro-churn regimes disappear above `45.40069` bytes per sidecar rewrite,
  - the earlier average break-even of `927.685921` bytes still leaves a `4`-transition plan that beats fixed route blocks by `7069.915895` bytes,
  - and fixed route blocks do not dominate every regime until switch cost reaches `5679.676082` bytes.
- Implementor consequence:
  - use an exact switch-penalty frontier rather than one average per-switch regret,
  - preserve only the front-loaded transitions that still pay at the archive's real rewrite cost,
  - and freeze immediately into a fixed sidecar only once the exact frontier says those remaining transitions are no longer worth it.

## 2026-03-07 — Compact Repeat-State Fixed-Policy Regret Pass

- Added a horizon-level fixed-policy regret view for compact repeat sidecars so the archive can compare exact staging churn against the best single sidecar over the next novel-append band:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_fixed_policy_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_fixed_policy_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_fixed_policy.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_compare_sidecar_churn_against_fixed_policy_regret.md`
- Main local result:
  - over the next `256` novel appends at `0.18` expected repeats, the fully staged planner uses `12` sidecar transitions,
  - the best fixed policy is `paged_catalog_with_route_blocks`,
  - its regret versus the full dynamic schedule is `11132.231038` bytes (`0.002305` of the dynamic cumulative objective),
  - and the dynamic schedule therefore buys only `927.68592` bytes per transition on average before a fixed policy becomes cheaper overall.
- Implementor consequence:
  - compact repeat-sidecar churn should be budgeted explicitly rather than treated as free,
  - the archive should compare expected per-switch rewrite or coordination cost against the measured fixed-policy regret threshold,
  - and it should keep the best fixed sidecar whenever switch cost clears that line or when repeat volume reaches the exact route-block horizon regime.

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


## 2026-03-07 — Compact Repeat-State Budget Pass

- Added a measured compact-state frontier for paged digest catalogs so the archive can choose the lightest worthwhile repeat sidecar instead of inheriting the strongest one:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_budget_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_budget_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_budgets.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_compact_repeat_sidecars_by_expected_repeat_budget.md`
- Main local result:
  - on the current deterministic `274`-packet frontier with live `16`-entry compact pages, bare pages cost `11770` bytes and `6214.708029` average repeat lookup,
  - page filters cost `12653` bytes and `1467.306569` average repeat lookup,
  - route blocks cost `12891` bytes and `1101.153285` average repeat lookup,
  - filters break even after `0.185996` expected repeats,
  - and route blocks break even after `0.650001` repeats beyond the filtered state.
- Implementor consequence:
  - do not default to the strongest compact repeat sidecar just because it exists,
  - choose between `{paged_catalog_only, paged_catalog_with_filters, paged_catalog_with_route_blocks}` by the measured objective `compact_state_bytes + expected_repeat_lookups * average_repeat_lookup_bytes`,
  - and treat route blocks as the live winner only once the archive expects at least about one repeat on the current catalog.


## 2026-03-07 — Digest-Byte Route-Block Pass

- Replaced linear page-filter scans with digest-byte route blocks for compact-catalog repeat planning:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_catalog_route_block_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_catalog_route_block_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_catalog_route_blocks.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_store_digest_byte_route_blocks_beside_paged_catalogs.md`
- Main local result:
  - on the current deterministic 274-packet frontier with the live 16-entry compact pages, average repeat lookup falls from `1467.306569` bytes with page filters to `1101.153285` bytes with route blocks,
  - compact state rises only from `12653` to `12891` bytes,
  - route-block planning preserves the same repeat-plan core on all `274 / 274` deterministic packets,
  - and appending one novel fingerprint currently changes only the single route block matching its first-byte high nibble.
- Implementor consequence:
  - if the archive already keeps paged raw-digest catalogs and wants a stronger repeat-planning sidecar than linear page filters, keep digest-byte route blocks beside the pages,
  - treat them as the new top repeat-planning sidecar for the current compact-catalog state,
  - and rebuild them wholesale only when the page-count bitmap width changes.


## 2026-03-07 — Filtered Catalog Page-Size Frontier Pass

- Measured the filtered compact-catalog page-size frontier and changed the live filtered-page default from `64` entries to `16` entries:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_catalog_page_size_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_catalog_page_size_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_catalog_page_sizes.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_small_filtered_catalog_pages_by_measured_lookup_state_tradeoff.md`
- Main local result:
  - among the clean power-of-two candidates `{8,16,32,64,128}`, the old `64`-entry default is no longer close to the lookup/state frontier once filtered compact pages drive both repeat reads and repeat writes,
  - `16`-entry pages raise compact state only from `11960` to `12653` bytes,
  - but they cut average filtered repeat lookup from `3850.540146` bytes to `1467.306569`, saving `2383.233577` bytes on average (`0.618935` share),
  - and they minimize the combined objective `full_compact_state_bytes + average_repeat_lookup_bytes_with_filters` within the measured clean power-of-two candidate set.
- Implementor consequence:
  - future sessions should treat `64`-entry filtered pages as the old baseline,
  - keep `16`-entry filtered pages as the live default for compact paged digest catalogs,
  - and reopen the page-size frontier only if the archive’s catalog population or lookup/write mix changes enough to justify it.

## 2026-03-07 — Research Pass LXXIII (Digest-Byte Page Filters + Pruned Compact-State Repeat Lookups)

- Tightened the compact paged-catalog repeat path so the live writer can skip impossible raw-digest pages before scanning them:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_catalog_page_filter_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_catalog_page_filter_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_catalog_page_filters.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_store_digest_byte_page_filters_beside_paged_catalogs.md`
- Tightened planning guidance:
  - keep one aligned digest-byte page filter beside each append-only raw-digest catalog page,
  - use those filters to skip impossible pages before any repeat lookup scans raw digests,
  - update only the tail filter on ordinary appends,
  - and still fall back to the existing zepto first-write chooser for genuinely new semantic fingerprints.
- Main local result:
  - aligned page filters cost only `246` total minified bytes across the current `5`-page deterministic frontier catalog,
  - filtered repeat planning still matches unfiltered page-native planning on all `274 / 274` repeat decisions at the core-field level,
  - and average repeat lookup cost falls from `7155.124088` bytes to `3850.540146`, saving `3304.583942` bytes on average (`0.461849` share) while preserving the same `short_catalog_reference` repeat winners.

## 2026-03-07 — Decision-Packet Analytic-Frontier Pass

- Added an exact wrapper-arithmetic frontier for zepto in-archive decision-packet writes:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_analytic_frontier_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_analytic_frontier_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_analytic_frontiers.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_zepto_local_codecs_by_exact_wrapper_arithmetic.md`
- Main local result: the live zepto writer no longer needs the old measured frontier snapshot to justify the smallest current codec. On the deterministic `274`-packet frontier set, the exact chooser still matches every measured first-write and repeat-write winner while cutting candidate-size evaluations from `1644` to `274` for first writes and from `1644` to `274` for repeats.
- Implementor consequence: future sessions should choose between `{packed_seed, byte_seed}` from the shared packed payload for every first write and between `{packed_reference, byte_reference}` from the resolved even-length prefix for every repeat, keeping the full measured frontier only as a certification layer.

## 2026-03-07 — Decision-Packet Compiled-Frontier Pass

- Added an exact compiled-frontier rule for zepto in-archive decision-packet writes:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compiled_frontier_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compiled_frontier_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compiled_frontiers.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_compile_measured_decision_packet_frontiers_into_exact_shortlists.md`
- Main local result: on the deterministic `274`-packet frontier set, the compiled shortlist reproduces every measured first-write and repeat-write winner exactly while cutting candidate-size evaluations from `1644` to `463` for first writes and from `1370` to `274` for repeats.
- Implementor consequence: future sessions should treat the full codec ladder as background capability, but use the compiled shortlist as the live archive rule: `byte_reference` for repeats, `byte_seed` for non-weight first writes, and only `{packed_seed, byte_seed}` for `oracle_weights` first writes.

## 2026-03-06 — Rematch Cache-Plan Pass

- Added a machine-readable cache-planner report for the current leave/rematch proxy:
  - `scripts/report/build_rematch_proxy_cache_plan_snapshot.py`
  - `artifacts/reports/rematch_proxy_cache_plan_snapshot_20260306.{md,json}`
  - `docs/LIBRARY/topics/rematch_proxy_cache_plan_manifest.md`
- Main local result: the inherited naive plan of full entrant-signature keying plus `h=50` can be replaced by exact proxy-local plans costing only `51/2/4/1` key-depth slots across `{none, opponent, focal, bilateral}` noise modes, a `238.2x` to `12150x` reduction.
- Implementor consequence: the next rematch engine should compile a world-local canonicalization planner instead of hard-coding full-signature caches or a legacy global unroll bound.

## 2026-03-06 — Rematch Noise-Semantics Cache Pass

- Added a support-semantics report showing that the current rematch canonicalization cache rule is a zero-noise artifact:
  - `scripts/report/build_rematch_proxy_noise_semantics_snapshot.py`
  - `artifacts/reports/rematch_proxy_noise_semantics_snapshot_20260306.{md,json}`
  - `docs/LIBRARY/topics/rematch_proxy_noise_semantics_dominate_cache_keys.md`
- Main local result: the current cooperative-pool quotient moves from `63` families (no noise) to `99` with opponent tremble, `147` with focal tremble, and `163` with bilateral tremble.
- Implementor consequence: rematch-world canonicalization caches must be keyed on active tremble semantics, not just entrant support.

## 2026-03-06 — Rematch Turnover-Tempo Pass

- Added a derived tempo report showing that the current proxy's fixed rematch delay is almost a deterministic function of partnership length:
  - `scripts/report/build_rematch_proxy_turnover_tempo_snapshot.py`
  - `artifacts/reports/rematch_proxy_turnover_tempo_snapshot_20260306.{md,json}`
  - `docs/LIBRARY/topics/rematch_delay_tax_scales_with_turnover_tempo.md`
- Main local result: across all `45` scenario means, `matched_round_share` is predicted by `avg_match_length / (avg_match_length + rematch_delay)` with max absolute error `0.000167`; at `delay=2`, the shortest-lived tested partnerships pay a `4.878x` larger matched-share penalty than the `50`-round baselines.
- Implementor consequence: future rematch worlds should expose persistence / turnover metrics (`avg_match_length` or equivalent) separately from search-dead-time, because the same nominal delay becomes a much larger tax in high-churn worlds.

# Agent Log

- 2026-03-23: Added a replayable Rust external-test patchset artifact and doc so the first post-block comeback can start from one unified diff instead of manually stitching bundle snippets back together.
## 2026-03-23 — seed loader readiness

- Found a real handoff-quality bug in the blocked-Rust lift queue: `observation_flip` was preferring `examples/probes/holdouts/noisy_stability.json`, which is probe-shaped but not directly liftable because `strategy_a` is `null`.
- Tightened example-witness ranking so directly loadable probe fixtures beat holdout templates and registry wrappers when the repo already contains a self-contained probe for the same weak row.
- Added a compact seed-loader audit so future sessions can verify that the preferred lift-queue seeds are still direct `ProbeSpec` fixtures before claiming they are ready to paste into external Rust tests.

## 2026-03-20 (rev0352)
- Added compact top-level `transition_graph_diagnostics` to `grlab certify` so inheritors can see reducibility, closed / recurrent classes, absorbing states, and initial-support reachability without reconstructing the graph from the raw 4x4 kernel.
- Updated certify schema/tests/formal snapshot accordingly and kept the change archive-tight by reusing the already-declared state order / kernel semantics rather than adding a new contract family.


## 2026-03-07 — Decision-Packet Analytic-Weight-Frontier Pass

- Replaced the last live measured first-write branch for `oracle_weights` with exact payload-byte sizing:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_weight_formula_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_weight_formula_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_weight_formulas.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_oracle_weight_seed_forms_by_exact_payload_bytes.md`
- Main local result: the analytic formulas match actual packed-seed and byte-seed minified sizes for all `189` deterministic frontier `oracle_weights` packets and all `4096` randomized weight stress packets; on the deterministic frontier they preserve the existing `24` packed winners, `165` byte winners, and `18` ties.
- Implementor consequence: future sessions should stop treating `oracle_weights` first writes as a mini frontier search; compute the packed-vs-byte seed lengths directly from the canonical packed payload, then materialize only the winning body.

## 2026-03-06 — Rematch Occupancy-Accounting Pass

- Added a derived accounting report that decomposes aggregate welfare into time spent matched versus payoff earned while matched:
  - `scripts/report/build_rematch_proxy_occupancy_accounting_snapshot.py`
  - `artifacts/reports/rematch_proxy_occupancy_accounting_snapshot_20260306.{md,json}`
  - `docs/LIBRARY/topics/rematch_worlds_need_occupancy_accounting.md`
- Main local result: across `15` tested policy/extortion cells, the mean share of `delay0 -> delay2` payoff loss explained by shrinking `matched_round_share` is `0.985842`, while the largest in-match-payoff drift is only `0.005788`.
- Implementor consequence: future rematch-world reports should expose occupancy accounting (`matched_round_share`, `dead_round_share`, `in_match_avg_payoff`) instead of reporting only aggregate welfare.

## 2026-03-06 — Rematch Start-Support Gate Pass

- Added a support-signature sweep showing a cheap cache invalidation trigger for the current rematch proxy:
  - `scripts/report/build_rematch_proxy_start_support_gate_snapshot.py`
  - `artifacts/reports/rematch_proxy_start_support_gate_snapshot_20260306.{md,json}`
  - `docs/LIBRARY/topics/rematch_proxy_cache_invalidation_by_start_support.md`
- Main local result: all `81` entrant support signatures with `C`-only initial support preserve the current `63`-family quotient, while all `162` signatures whose initial support includes `D` invalidate it and reopen the space to `87`–`99` families.
- Implementor consequence: in the current deterministic no-noise proxy, initial support is a cheap sound gate for cache reuse, but exact quotient size still requires recomputation.

## 2026-03-06 — Rematch Canonicalization Sensitivity Pass

- Added a structural sensitivity report showing that the current rematch-proxy quotient is pool-specific rather than universal:
  - `scripts/report/build_rematch_proxy_canonicalization_sensitivity_snapshot.py`
  - `artifacts/reports/rematch_proxy_canonicalization_sensitivity_snapshot_20260306.{md,json}`
  - `docs/LIBRARY/topics/rematch_proxy_canonicalization_is_pool_specific.md`
- Main local result: the current `63`-family quotient is unchanged by adding cooperative starters (`tft_v1`, `wsls_v1`) but rises to `87` families when one suspicious starter (`always_d_v1`) enters the pool.
- Implementor consequence: canonicalization must be recomputed from world/opponent support rather than hard-coded as a fixed rematch lookup table.

## 2026-03-03 — Scientific Repo Reconstruction

- Removed hypertext-specific operational scaffolding and conversation transcript machinery.
- Rewrote `AGENTS.md` to a concise scientific-tool contract (determinism, evidence, narrow diffs, gate discipline).
- Re-centered docs index on architecture, determinism, provenance, and staged implementation.
- Kept Rust/Python split and deterministic gate model as the core project posture.

## 2026-03-03 — Repo Prep Baseline

- Added deterministic harness and command surface (`make doctor`, `make test-quick`, `make test-full`, `make gate`, `make gate-strict`).
- Added validators and governance scaffolding:
  - goldens registry validation,
  - spec ledger + schema validation,
  - ADR validation.
- Added process hygiene checks, flake/soak loops, and async soak controls.

## 2026-03-03 — Scientific Terminology + Compatibility Pass

- Added scientific execution plan: `docs/SCIENCE_PLAN.md`.
- Updated `grlab gauntlet` to support preferred `adversaries` group while keeping legacy `vampires` compatibility.
- Switched default gauntlet spec to `examples/gauntlet/gauntlet_v2.json`.
- Updated `grlab status` output labels to `Candidates` / `Adversaries` with legacy directory fallback.
- Updated ecology pool loading to include preferred and legacy strategy directories with id-based dedup.
- Added tests:
  - `grlab/tests/test_gauntlet_cli.py` (adversaries-group coverage)
  - `grlab/tests/test_status_cli.py` (scientific labels)
- Hardened `tools/rust_exec.sh` for sandbox volatility:
  - auto-setup JuNest home if missing,
  - auto-install/upgrade Rust toolchain in JuNest when needed,
  - enforce library environment for stable cargo/rustc execution.

## 2026-03-03 — Scientific Transformation Pass

- Refactored AFK mission control terminology and outputs:
  - candidate promotion now writes to `examples/strategies/candidates/`,
  - adversarial discoveries now write to `examples/strategies/adversaries/`,
  - legacy mirrors are still emitted under `discovered/` and `vampires/` for compatibility.
- Hardened AFK Rust build path to use `tools/rust_exec.sh` instead of direct `cargo`, improving reliability in Sandworm/JuNest.
- Added adversarial probe artifacts with neutral naming:
  - `examples/probes/registry_adversarial.json`
  - `examples/probes/registry_noisy_adversarial.json`
  - `examples/probes/suites/adversarial.json`
  - `examples/probes/noisy_adversarial_probe.json`
- Upgraded public denylist policy to include `adversary` terms while retaining legacy `vampire` coverage (`policy/public_export_denylist.json`).
- Added control coverage and scientific wiring:
  - `tests/control/test_repo_controls.py` now requires `docs/SCIENCE_PLAN.md`.
  - `grlab status` label formatting normalized (`Adversaries: N`).
- Marked `examples/gauntlet/gauntlet_v1.json` as legacy naming and kept `gauntlet_v2` as the scientific default.

## 2026-03-03 — Tranche Program Completion

- Added and executed a 50-item mixed-domain tranche plan in `docs/TRANCHES.md`.
- Added tranche governance and operations docs:
  - `docs/TERMINOLOGY.md`
  - `docs/EXPERIMENT_PROTOCOL.md`
  - `docs/DATA_MANAGEMENT.md`
  - `docs/STATISTICAL_PRACTICE.md`
  - `docs/RELEASE_PROCESS.md`
- Added tranche control scripts and policy:
  - `scripts/test/record_env_metadata.py`
  - `scripts/test/check_timing_regression.py`
  - `scripts/report/check_spec_ledger_rollup.py`
  - `scripts/security/check_allowlist.py`
  - `scripts/release/generate_manifest.sh`
  - `scripts/release/check_release_hygiene.sh`
  - `policy/security_allowlist.json`
- Added hook operations:
  - `.githooks/pre-commit`
  - `.githooks/pre-push`
  - `scripts/hooks/install.sh`
  - `scripts/hooks/log_bypass.py`
- Wired new checks into `Makefile` and integration `gate`.
- Validation evidence:
  - `make doctor` passed.
  - `make test-quick` passed.
  - `make gate` passed.
  - `make release-manifest RELEASE_VERSION=dev` passed.
  - `make test-release-hygiene RELEASE_VERSION=dev` passed.
  - `make install-hooks` set `core.hooksPath` to `.githooks`.
  - `make gate-strict` reached strict security phase and failed as expected in this environment due to missing `cargo-audit`.

## 2026-03-03 — Tranche Program Expansion (Inclusive Long List)

- Expanded tranche tracking to 110 completed items in `docs/TRANCHES.md`.
- Added formal-method tranche controls:
  - `scripts/formal/check_certify_invariants.py`
  - `scripts/formal/check_formal_tooling.py`
  - `docs/FORMAL_METHODS.md`
- Added science-asset tranche controls:
  - `scripts/test/check_examples_json.py`
  - `scripts/report/build_experiment_catalog.py`
  - `docs/EXPERIMENT_CATALOG.md` (generated)
- Added governance/integrity tranche controls:
  - `scripts/test/check_markdown_links.py`
  - `scripts/test/check_artifact_layout.py`
  - `scripts/test/check_bypass_log.py`
  - `scripts/test/check_gitignore_artifacts_policy.py`
  - `scripts/test/check_spec_dates.py`
- Added reporting tranche control:
  - `scripts/report/summarize_artifacts.py`
- Extended Makefile command surface and integrated new checks into `make gate`.
- Added artifact bucket keepers and policy entries:
  - `artifacts/release/.gitkeep`
  - `artifacts/formal/.gitkeep`
  - `artifacts/reports/.gitkeep`
  - `.gitignore` rules updated for these buckets.
- Validation evidence for tranche expansion:
  - `make test-quick` passed.
  - `make gate` passed with new formal/docs/examples/integrity/report checks.
  - `make release-manifest RELEASE_VERSION=dev` passed.
  - `make test-release-hygiene RELEASE_VERSION=dev` passed.

## 2026-03-03 — Tranche Program Expansion II (Very Long Inclusive Pass)

- Extended tranche list to 180 completed items (`docs/TRANCHES.md`).
- Added tranche governance/reporting controls:
  - `scripts/report/build_tranche_status.py`
  - `docs/TRANCHES_SUMMARY.md` (generated)
  - `artifacts/reports/tranche_status.json` (generated)
- Added reproducibility/report controls:
  - `scripts/report/build_repro_bundle_index.py`
  - `artifacts/reports/repro_bundle_index.json` (generated)
- Added additional integrity validators:
  - `scripts/test/check_examples_unique_ids.py`
  - `scripts/test/check_scripts_executable.py`
  - `scripts/test/check_scripts_compile.py`
  - `scripts/test/check_readme_command_surface.py`
  - `scripts/test/check_docs_index_core.py`
  - `scripts/test/check_tranches_complete.py`
- Added release integrity validators:
  - `scripts/release/check_release_manifest_schema.py`
  - `scripts/release/check_release_checksums.py`
  - `schemas/release_manifest.schema.json`
- Added policy for intentional legacy duplicate example ids:
  - `policy/examples_id_allowlist.json`
- Added additional governance docs:
  - `docs/QUALITY_ASSURANCE.md`
  - `docs/REPRODUCIBILITY.md`
- Extended `Makefile` with new command surface and integrated new checks into `make gate`.
- Validation evidence:
  - `make doctor` passed.
  - `make test-quick` passed.
  - `make gate` passed with all tranche-expansion validators enabled.
  - `make release-manifest RELEASE_VERSION=dev` passed.
  - `make test-release-manifest-schema` passed.
  - `make test-release-checksums RELEASE_VERSION=dev` passed.
  - `make test-release-hygiene RELEASE_VERSION=dev` passed.

## 2026-03-03 — Tranche Program Expansion III (Very Long Inclusive Pass)

- Extended tranche ledger to 260 completed items (`docs/TRANCHES.md`).
- Added CI/policy/spec-evidence validators:
  - `scripts/test/check_ci_smoke.py`
  - `scripts/test/check_policy_expirations.py`
  - `scripts/test/check_spec_evidence_links.py`
  - `scripts/test/check_release_doc_commands.py`
  - `scripts/test/check_make_help_surface.py`
  - `scripts/test/check_required_examples.py`
  - `scripts/test/check_reports_json_valid.py`
- Added generated inventory builders:
  - `scripts/report/build_command_inventory.py`
  - `scripts/report/build_validator_inventory.py`
  - `scripts/report/build_policy_inventory.py`
- Added policy/docs assets:
  - `policy/examples_id_allowlist.json`
  - `docs/CI_POLICY.md`
  - `docs/DEPENDENCY_POLICY.md`
  - `docs/COMMAND_INVENTORY.md` (generated)
  - `docs/VALIDATOR_INVENTORY.md` (generated)
  - `docs/POLICY_INVENTORY.md` (generated)
- Extended Makefile command surface and wired all new checks into `make gate`.
- Validation evidence:
  - `make test-quick` passed.
  - `make doctor` passed.
  - `make gate` passed with tranche-expansion-III validators enabled.
  - `make release-manifest RELEASE_VERSION=dev` passed.
  - `make test-release-manifest-schema` passed.
  - `make test-release-checksums RELEASE_VERSION=dev` passed.
  - `make test-release-hygiene RELEASE_VERSION=dev` passed.

## 2026-03-03 — Tranche Program Expansion IV (Very Long Inclusive Pass)

- Extended tranche ledger to 340 completed items (`docs/TRANCHES.md`).
- Added new validation controls:
  - `scripts/test/check_schema_json_valid.py`
  - `scripts/test/check_policy_json_valid.py`
  - `scripts/test/check_hooks_contract.py`
  - `scripts/test/check_artifact_gitkeeps.py`
  - `scripts/test/check_release_manifest_entries.py`
  - `scripts/test/check_timing_artifacts_presence.py`
  - `scripts/test/check_generated_docs_presence.py`
- Added generated inventory controls:
  - `scripts/report/build_schema_inventory.py`
  - `scripts/report/build_artifact_bucket_inventory.py`
  - `docs/SCHEMA_INVENTORY.md` (generated)
  - `docs/ARTIFACT_BUCKETS.md` (generated)
- Extended `Makefile` with tranche-expansion-IV targets and gate integration.
- Resolved gate drift by moving `test-artifact-buckets` to the end of `gate` after artifact-producing checks.
- Validation evidence:
  - `make test-quick` passed.
  - `make doctor` passed.
  - `make gate` passed with tranche-expansion-IV validators enabled.
  - `make release-manifest RELEASE_VERSION=dev` passed.
  - `make test-release-manifest-schema` passed.
  - `make test-release-manifest-entries RELEASE_VERSION=dev` passed.
  - `make test-release-checksums RELEASE_VERSION=dev` passed.
  - `make test-release-hygiene RELEASE_VERSION=dev` passed.

## 2026-03-03 — Source-Backed Research Tranche (Deep Pass)

- Performed a primary-source sweep across repeated-game theory, solver ecosystems, Rust verification, and reproducible orchestration tooling.
- Added source registry with verified links and direct repo implications:
  - `docs/RESEARCH_SOURCES.md`
- Added source-backed research and implementation agenda:
  - `docs/RESEARCH_AGENDA.md`
- Updated science execution phases to emphasize:
  - dual-solver formal lane (Z3 + cvc5),
  - probabilistic model-checking pilot lane,
  - robustness-first benchmark posture.
- Updated docs index and context index:
  - `docs/README.md`
  - `docs/context/README.md`
- Updated spec-governance ledger for unresolved formal-policy ambiguity:
  - `SG-002` (gap),
  - `SQ-002` (question),
  - `SA-002` (assumption).
- Extended tranche ledger to include tranche-extension-V research tasks (`341`..`380`).

## 2026-03-03 — Source-Backed Research Tranche (Matrix Extension)

- Added execution matrix mapping source-backed work packages to verification signals:
  - `docs/RESEARCH_TRANCHE_MATRIX.md` (`RT-001`..`RT-060`)
- Expanded source registry with classic cooperation references:
  - `RS-IPD-008` (Axelrod & Hamilton)
  - `RS-IPD-009` (Nowak five rules)
- Extended tranche ledger to tranche-extension-VI (`381`..`400`) and regenerated tranche status artifacts.

## 2026-03-03 — Source-Backed Research Tranche (Opinion Extension)

- Continued research/planning pass and added explicit prioritization opinions:
  - `docs/RESEARCH_OPINIONS.md`
- Added source references for formal-method practical constraints and MDP checking guidance:
  - `RS-FM-011`, `RS-FM-012`, `RS-FM-013`.
- Extended tranche ledger to tranche-extension-VII (`401`..`420`) and linked new planning docs from `docs/README.md`.

## 2026-03-03 — Tranche Program Extension VIII (Claim Taxonomy + Research Governance)

- Added machine-readable claim governance assets:
  - `specs/claim_classes.yaml`
  - `schemas/claim_classes.schema.json`
- Added new validators and report builders:
  - `scripts/test/check_claim_classes.py`
  - `scripts/report/build_claim_matrix.py`
  - `scripts/test/check_research_docs.py`
- Added research-governance docs:
  - `docs/CLAIM_TAXONOMY.md`
  - `docs/FORMAL_OBLIGATION_TABLE.md`
  - `docs/BENCHMARK_PROGRAM.md`
  - `docs/EXECUTION_RHYTHM.md`
  - `docs/RESEARCH_RISK_REGISTER.md`
- Extended Makefile/gate with claim/research targets:
  - `test-research-docs`
  - `test-claim-classes`
  - `update-claim-matrix`
  - `test-claim-matrix`
- Expanded validators to cover new docs/index/schema expectations.
- Extended tranche ledger to tranche-extension-VIII (`421`..`520`).

## 2026-03-03 — Tranche Program Extension IX (Claim Register + Claim Audit)

- Added claim register governance assets:
  - `specs/claim_register.yaml`
  - `schemas/claim_register.schema.json`
  - `scripts/test/check_claim_register.py`
  - `scripts/report/build_claim_register_summary.py`
- Added claim workflow policy document:
  - `docs/CLAIM_WORKFLOW.md`
- Extended docs/index/validator surfaces for claim register artifacts:
  - `docs/README.md`
  - `README.md`
  - `docs/SCHEMAS.md`
  - `scripts/test/check_research_docs.py`
  - `scripts/test/check_generated_docs_presence.py`
  - `scripts/test/check_docs_index_core.py`
  - `scripts/test/check_readme_command_surface.py`
- Extended `Makefile` and gate with claim-register targets:
  - `test-claim-register`
  - `update-claim-register-summary`
  - `test-claim-register-summary`
- Extended control-test coverage:
  - `tests/control/test_repo_controls.py`
- Extended tranche ledger to tranche-extension-IX (`521`..`620`).

## 2026-03-03 — Tranche Program Extension X (Machine Risk Register)

- Added machine-readable risk governance assets:
  - `specs/risk_register.yaml`
  - `schemas/risk_register.schema.json`
  - `scripts/test/check_risk_register.py`
  - `scripts/report/build_risk_register_summary.py`
- Added generated risk register doc:
  - `docs/RISK_REGISTER.md`
- Extended docs/index/schema/validator surfaces for risk register integration:
  - `docs/README.md`
  - `README.md`
  - `docs/SCHEMAS.md`
  - `scripts/test/check_research_docs.py`
  - `scripts/test/check_generated_docs_presence.py`
  - `scripts/test/check_docs_index_core.py`
  - `scripts/test/check_readme_command_surface.py`
- Extended `Makefile` and gate with risk-register targets:
  - `test-risk-register`
  - `update-risk-register-summary`
  - `test-risk-register-summary`
- Extended control-test coverage:
  - `tests/control/test_repo_controls.py`
- Extended tranche ledger to tranche-extension-X (`621`..`720`).

## 2026-03-06 — Research Pass XI (Compact Archive + Inheritor Guidance)

- Continued research/planning with a Golden-Rule-specific follow-up pass.
- Added source references for:
  - longer-memory reciprocity
  - fair resistance to extortion
  - partner choice / opting out
  - universalisation in games
- Added inheritor guidance:
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
- Added compact scratch artifacts:
  - `artifacts/process/2026-03-06-research-pass.md`
  - `artifacts/reports/extortion_metric_snapshot_20260306.{md,json}`
- Switched the reading shelf to citation-first compact mode and removed long-term PDF blobs.
- Recorded environment limitation during this pass:
  - `make doctor` failed because `cargo`/`junest` were unavailable.
  - `make test-quick` reached Python checks and then failed at the Rust library step for the same reason.


## 2026-03-06 — Research Pass XII (Memory-One Frontier + Strategy-Space Guardrail)

- Added a reproducible analytic frontier snapshot for Golden-Rule tradeoffs in the memory-one space:
  - `scripts/report/build_memory_one_tradeoff_snapshot.py`
  - `artifacts/reports/memory_one_tradeoff_snapshot_20260306.{md,json}`
- Added one compact frontier-witness baseline strategy:
  - `examples/strategies/mem1_courteous_firm.json`
- Added inheritor-facing note on the new local constraint:
  - `docs/LIBRARY/topics/memory_one_tradeoff_against_extortion.md`
- Extended source-backed research posture with:
  - strategy-space completeness / nested-space sanity-check literature
  - mixed direct/indirect reciprocity across broader dilemma classes
  - heterogeneous-memory competition results
- Added a new research-program risk about uncontrolled strategy-space expansion.

## 2026-03-06 — Research Pass XIII (Exit Boundary + Nice-Start Guardrail)

- Added a reproducible deterministic sweep of the existing `memory_one_exit` family:
  - `scripts/report/build_exit_without_partner_choice_snapshot.py`
  - `artifacts/reports/exit_without_partner_choice_snapshot_20260306.{md,json}`
- Added an inheritor-facing note clarifying the conceptual boundary:
  - `docs/LIBRARY/topics/unilateral_exit_is_not_partner_choice.md`
- Tightened Golden-Rule planning guidance:
  - keep a minimal nice-start filter in Golden-Rule-facing scorecards,
  - do not treat unilateral exit in a fixed dyad as partner choice,
  - prioritize a leave/rematch world over broader exit-policy search.

## 2026-03-06 — Research Pass XIV (Rematch Proxy + Compact Exit Baseline)

- Added a reproducible minimal leave/rematch proxy sweep over deterministic `memory_one_exit` policies:
  - `scripts/report/build_partner_choice_proxy_snapshot.py`
  - `artifacts/reports/partner_choice_proxy_snapshot_20260306.{md,json}`
- Added one compact rematch-facing baseline strategy:
  - `examples/strategies/mem1_exit_after_break.json`
- Added an inheritor-facing note on what the proxy changes and what it still does not model:
  - `docs/LIBRARY/topics/rematch_proxy_changes_the_frontier.md`
- Tightened planning guidance:
  - rematching is now evidenced as a ranking-changing world mechanic,
  - keep `memory_one_exit` in fixed dyads diagnostic-only,
  - promote the proxy into an endogenous engine-supported world next,
  - canonicalize unreachable post-exit parameters in rematch-enabled search spaces.


## 2026-03-06 — Research Pass XV (Proxy Canonicalization + Rematch Search Geometry)

- Added a structural canonicalization snapshot for deterministic `memory_one_exit` policies in the current leave/rematch proxy:
  - `scripts/report/build_rematch_proxy_canonicalization_snapshot.py`
  - `artifacts/reports/rematch_proxy_canonicalization_snapshot_20260306.{md,json}`
- Added an inheritor-facing note on the search consequence:
  - `docs/LIBRARY/topics/rematch_proxy_search_space_canonicalization.md`
- Tightened planning guidance:
  - the current rematch proxy compresses `243` raw deterministic exit codes to `63` support-distinct families,
  - keep `mem1_exit_after_break_v1` (`CCEEE`) as the human-readable representative of the `CCE**` family,
  - make canonicalization world-aware and rerun it whenever the partner pool or noise semantics change.


## 2026-03-06 — Research Pass XVI (Minimal Cache Key by Noise Mode)

- Added an exact quotient-regime snapshot for rematch canonicalization under the current leave/rematch proxy:
  - `scripts/report/build_rematch_proxy_cache_regime_snapshot.py`
  - `artifacts/reports/rematch_proxy_cache_regime_snapshot_20260306.{md,json}`
- Added an inheritor-facing note on the engineering consequence:
  - `docs/LIBRARY/topics/rematch_proxy_minimal_cache_key_by_noise_mode.md`
- Tightened planning guidance:
  - the current proxy does not need one universal rematch cache key,
  - opponent-tremble and bilateral-tremble modes each collapse to one exact quotient regime,
  - focal-tremble collapses to two regimes keyed by initial-defect support,
  - only deterministic zero-noise remains heavily signature-sensitive after invalidation.


## 2026-03-06 — Research Pass XVII (Horizon Saturation + Exact Unroll Caps)

- Added an exact-horizon snapshot for support-level rematch canonicalization in the current proxy:
  - `scripts/report/build_rematch_proxy_horizon_saturation_snapshot.py`
  - `artifacts/reports/rematch_proxy_horizon_saturation_snapshot_20260306.{md,json}`
- Added an inheritor-facing note on the engineering consequence:
  - `docs/LIBRARY/topics/rematch_proxy_horizon_saturates_early.md`
- Tightened planning guidance:
  - the inherited `h=50` support-reachability cap is unnecessary in the current proxy,
  - exact saturation occurs at `3/2/2/1` rounds across `{none, opponent, focal, bilateral}` noise modes,
  - future rematch worlds should validate their smallest exact canonicalization horizon instead of inheriting a legacy global bound.

## 2026-03-06 — Research Pass XVIII (Planner Contract + Machine-Checkable Handoff)

- Added a provisional schema + validator bridge for rematch canonicalization planning:
  - `schemas/canonicalization_plan.schema.json`
  - `scripts/test/check_rematch_cache_plan_contract.py`
- Tightened the inheritor handoff:
  - the current proxy planner is now machine-checkable rather than living only as a report,
  - keep the contract scratch-local to this proxy until real rematch worlds expose planner metadata natively,
  - use the contract to catch stale cache keys / horizons before search runs.

## 2026-03-06 — Research Pass XIX (Zero-Noise Rule Classifier + Lookup Compression)

- Added an exact ordered-rule classifier for the zero-noise rematch proxy regime map:
  - `scripts/report/build_rematch_proxy_zero_noise_rule_classifier_snapshot.py`
  - `artifacts/reports/rematch_proxy_zero_noise_rule_classifier_snapshot_20260306.{md,json}`
- Added a machine-checkable contract for the classifier:
  - `scripts/test/check_rematch_zero_noise_rule_contract.py`
- Added an inheritor-facing note on the embedding consequence:
  - `docs/LIBRARY/topics/rematch_proxy_zero_noise_regime_rules.md`
- Tightened planning guidance:
  - the current zero-noise `243`-entry `support_signature -> regime` table compresses to `17` exact ordered wildcard rules,
  - prefer the ordered classifier over vendoring a bulky flat lookup when the engine needs an interim zero-noise embedding,
  - regenerate the classifier whenever entrant support, rematch timing, memory depth, or noise semantics change.

## 2026-03-06 — Research Pass XX (Zero-Noise Classifier Schema + Packaging Gate)

- Added a schema for the interim ordered-rule embedding:
  - `schemas/zero_noise_rule_classifier.schema.json`
- Promoted the classifier contract into the command surface:
  - `make test-zero-noise-rule-contract`
- Tightened planning guidance:
  - treat the exact `17`-rule zero-noise classifier as vendorable scratch only when both its schema and rule-contract checks pass,
  - keep the ordered classifier easier to audit than the flat `243`-row lookup,
  - prefer packaging/embedding gates that fail closed on classifier drift.

## 2026-03-06 — Research Pass XXI (Delay Tax vs Market Thickness Boundary)

- Added a derived monotonicity snapshot for rematch delay in the current exogenous-pool proxy:
  - `scripts/report/build_rematch_proxy_matching_friction_snapshot.py`
  - `artifacts/reports/rematch_proxy_matching_friction_snapshot_20260306.{md,json}`
- Added an inheritor-facing note on the interpretation boundary:
  - `docs/LIBRARY/topics/rematch_delay_is_not_market_thickness.md`
- Tightened planning guidance:
  - the current proxy's delay sweep is useful precisely because it behaves like a one-sided unmatched-time tax,
  - but that means it should stay diagnostic until an endogenous rematch world models market thickness / matching efficiency separately,
  - future welfare claims should track not only delay, but also the steady-state share of agents who are matched versus currently searching.


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

## 2026-03-06 — Rematch Delta-Hazard Pass

- Added a derived hazard-band report showing where SESOI choices become knife-edge expensive in the current rematch proxy:
  - `scripts/report/build_rematch_proxy_delta_hazard_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_hazard_snapshot_20260306.{md,json}`
  - `docs/LIBRARY/topics/rematch_worlds_need_delta_hazard_bands.md`
- Main local result: inside `delta <= 0.02`, there are `8` exact knife-edge leader-gap deltas; bands requiring more than `10000` extra paired seeds occupy only `0.00099` delta width (`4.95%` of the band) but create enormous closure-cost spikes when hit.
- Implementor consequence: rematch benchmarks should publish leader-gap hazard bands or a no-knife-edge buffer so future inheritors do not mistake a fragile threshold neighborhood for an ordinary SESOI choice.


## 2026-03-06 — Rematch Delta-Admissibility Pass

- Added a derived admissibility-band report showing which SESOI intervals remain operationally stable under declared extra-budget caps in the current rematch proxy:
  - `scripts/report/build_rematch_proxy_delta_admissibility_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_admissibility_snapshot_20260306.{md,json}`
  - `docs/LIBRARY/topics/rematch_worlds_need_budget_admissible_delta_bands.md`
- Main local result: under a `+10` paired-seed closure cap, admissible deltas collapse to `2` bands over `[0, 0.02]`; the only sub-`0.01` admissible band is `0.00538..0.00849`, while tightening to `+4` fragments the lower region into `4` micro-bands.
- Implementor consequence: rematch benchmarks should publish budget-admissible delta bands plus anchors so future inheritors choose from stable intervals instead of naked knife-edge margins.

## 2026-03-06 — Rematch Delta-Topology Pass

- Added a derived topology-core report showing where budget-admissible rematch delta bands still contain multiple distinct panel-label topologies:
  - `scripts/report/build_rematch_proxy_delta_topology_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_topology_snapshot_20260306.{md,json}`
  - `docs/LIBRARY/topics/rematch_worlds_need_topology_stable_delta_anchors.md`
- Main local result: across the tested caps, `12` of `20` admissible parent bands fragment into multiple closure topologies; the cap-10 low band splits into `4` topology-stable subbands, including a one-point knife edge.
- Implementor consequence: rematch benchmarks should publish topology-stable delta subbands or a stability-first anchor, because a single admissible parent band can still hide materially different mixes of `material leader`, `practical tie`, and `undecided` panels.


## 2026-03-06 — Rematch Delta-Anchor Contract Pass

- Added a machine-checkable anchor-contract report converting each admissible parent band into a topology-preserving interior anchor:
  - `scripts/report/build_rematch_proxy_delta_anchor_contract_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_anchor_contract_snapshot_20260306.{md,json}`
  - `schemas/rematch_delta_anchor_contract.schema.json`
  - `scripts/test/check_rematch_delta_anchor_contract.py`
  - `docs/LIBRARY/topics/rematch_parent_anchors_are_boundary_biased.md`
- Main local result: `6` inherited parent anchors sit exactly on topology boundaries, but replacing each with the midpoint of the topology-stable subband that contains it improves boundary buffer in `19 / 20` bands while preserving parent topology/counts in `20 / 20` and staying within the same declared cap in `20 / 20`.
- Implementor consequence: rematch benchmarks should stop exporting raw min-cost parent anchors as if they were principled SESOI choices; export topology-preserving interior anchors plus explicit buffer gain instead.

## 2026-03-06 — Research Pass XXXV (Delta Preference + Declared Anchor Priorities)

- Added a derived delta-preference report turning the strict sub-`0.01` publishability shortlist into a reproducible choice contract:
  - `scripts/report/build_rematch_proxy_delta_preference_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_preference_snapshot_20260306.{md,json}`
  - `scripts/test/check_rematch_delta_preference.py`
  - `docs/LIBRARY/topics/rematch_worlds_need_declared_anchor_priorities.md`
- Main local result: the strict sub-`0.01` shortlist still has `2` Pareto-nondominated anchors, so there is no unique dominant scalar constant; `material_first` and `closure_conservative` choose `TTTMMMMMU` at `0.00602`, while `stability_first` chooses `TTTMMMMUU` at `0.00744`.
- Implementor consequence: publish the strict shortlist together with the declared priority profile used to break shortlist ties, rather than hiding the final judgment step behind an unlabeled anchor.

## 2026-03-06 — Research Pass XXXVI (Delta Family Viability + Declared Cap Profiles)

- Added a derived delta-family viability report comparing exact budget-family declarations already present in the current proxy:
  - `scripts/report/build_rematch_proxy_delta_family_viability_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_family_viability_snapshot_20260306.{md,json}`
  - `scripts/test/check_rematch_delta_family_viability.py`
  - `docs/LIBRARY/topics/rematch_worlds_need_declared_budget_family_profiles.md`
- Main local result: both exact families expose `4` hazard-clear sub-`0.01` cores before width filtering, but the `10/20/50/100` family can sustain a width floor up to `0.00156` while the `4/10/20/50/100` family only sustains `0.00032`; at width floor `0.0010`, the former still has `2` candidates and the latter has `0`.
- Implementor consequence: declare and justify the exact budget-family profile before applying width floors, hazard filters, or priority profiles, because folding cap `4` into the default family turns a viable low-delta shortlist into a no-anchor problem.


## 2026-03-07 — Research Pass LIII (Decision Packets + Minimal Archive Storage)

- Added an executable compact-packet layer for the family10 rematch-delta handoff:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packets.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_store_minimal_decision_packets.md`
- Main local result: the archive now has six explicit packet modes, with direct `(B,H)` packets as the leanest declaration-first route and black-box packets separated into robustness-only, open-strict, and exact checked-cap/tie-cap contracts.
- Implementor consequence: future sessions can keep rematch decisions as compact packets matched to the actual question instead of defaulting to larger supersets of probe evidence.

## 2026-03-07 — Research Pass LIV (Shared Packet Profiles + Archive-Local Citation Storage)

- Added an archive-local storage layer for rematch decision packets that cites a shared provenance profile instead of repeating the same provenance block in every packet:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_profile_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_profile_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_profiles.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_share_decision_packet_provenance_profiles.md`
- Main local result: all tested archive-local packets expand back to the canonical standalone packet exactly, while reducing minified size by a constant `331` bytes per packet (`34.37%` to `46.23%` on the representative family10 packet set).
- Implementor consequence: inside the long-lived archive, future sessions should store archive-local packets by default and only pay the standalone provenance cost when exporting a packet outside the archive.


## 2026-03-07 — Research Pass LV (Semantic Packet Fingerprints + Duplicate-Eliding Archive Writes)

- Added semantic packet fingerprints for the family10 rematch decision packet layer so equivalent standalone and archive-local packets collapse to the same content-addressed archive identity:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_fingerprint_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_fingerprint_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_fingerprints.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_deduplicate_decision_packets_by_semantic_fingerprint.md`
- Main local result: the same `oracle_coordinates_sms` decision now hashes identically across standalone and archive-local storage forms, so the first archive write keeps one `486`-byte archive-local body and later repeats can shrink to a `160`-byte reference, saving `326` bytes on the duplicate write.
- Implementor consequence: once a semantic fingerprint is already present in the archive, future sessions should stop re-storing the packet body and instead store a fingerprint reference, even if the repeated packet arrived in a different storage form.



## 2026-03-07 — Research Pass LVI (Semantic Cores + Minimal First-Write Bodies)

- Added semantic-core storage for the family10 rematch decision packet layer so the archive can keep the smallest deterministic seed for each new semantic decision:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_core_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_core_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_cores.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_store_semantic_cores_before_archive_local_packets.md`
- Main local result: representative archive-local packet bodies now shrink by `307` bytes for declaration-first coordinates, `346` bytes for declaration-first weights, `121` bytes for adaptive robustness packets, and `209` bytes for exact checked-cap tie packets when stored as semantic cores instead.
- Implementor consequence: future sessions should keep one semantic core per fingerprint as the long-lived archive object, materialize archive-local packets when a readable packet view is needed, and export standalone packets only when the decision must travel outside the archive.

## 2026-03-07 — Research Pass LVII (Prefix-Resolved References + Smaller Repeat Writes)

- Added an archive-local prefix-reference layer for the family10 rematch decision packet path so duplicate writes can point to an already-known semantic body without repeating a full exported fingerprint:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_prefix_reference_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_prefix_reference_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_prefix_references.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_store_prefix_resolved_references_inside_archive.md`
- Main local result: across the representative family10 packet set, duplicate portable references were `160` minified bytes, while archive-local prefix references shrank to `71` bytes with a `12`-hex unique-prefix floor, saving `89` bytes on every measured repeat write.
- Implementor consequence: future sessions should keep full semantic fingerprints in the archive index and exported reference packets, but use the shortest unique archive-local prefix reference for in-archive repeats once the semantic body is already present.


## 2026-03-07 — Research Pass LVIII (Mode-Coded Seeds + Smallest First-Write Bodies)

- Added archive-local mode-coded seeds for the family10 rematch decision packet path so first writes can compress below semantic cores whenever the local codebook is preserved:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_coded_seed_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_coded_seed_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_coded_seeds.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_store_mode_coded_seeds_inside_archive.md`
- Main local result: across the representative family10 packet set, semantic cores now shrink by another `120` bytes for declaration-first coordinates, `122` bytes for declaration-first weights, `131` bytes for adaptive robustness routes, and `138` bytes for exact checked-cap tie packets when stored as archive-local coded seeds.
- Implementor consequence: future sessions should treat `coded_seed` as the smallest in-archive first-write body when the local codebook is part of the durable archive environment, keep `semantic_core` as the clearer fallback tier, and keep using archive-local prefix references for repeat writes.


## 2026-03-07 — Research Pass LIX (Mode-Coded References + Smallest Repeat Writes)

- Added archive-local mode-coded repeat references for the family10 rematch decision packet path so duplicate writes can compress below prefix-resolved references once the archive preserves the local repeat-reference codebook:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_coded_reference_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_coded_reference_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_coded_references.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_store_mode_coded_repeat_references_inside_archive.md`
- Main local result: across the representative family10 packet set, archive-local prefix references were `71` minified bytes while mode-coded repeat references shrank to `31` bytes, saving `40` bytes on every measured duplicate write and `129` bytes relative to portable full-fingerprint references.
- Implementor consequence: future sessions should keep `coded_seed` as the smallest first-write body, switch repeats to `coded_reference` when the local repeat-reference codebook is present, keep `archive_local_reference` as the readable fallback tier, and reserve full `reference` packets for export across the archive boundary.


## 2026-03-07 — Research Pass LX (Tagged Microframes + Smallest In-Archive Writes)

- Added tagged microframes for the family10 rematch decision packet path so both new semantic bodies and duplicate pointers can compress below object-wrapped coded packets:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_microframe_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_microframe_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_microframes.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_store_tagged_microframes_inside_archive.md`
- Main local result: across the representative family10 packet set, coded seeds now shrink by another `40` bytes for declaration-first coordinates and `36` bytes for the weights, adaptive-route, and exact checked-cap tie examples when stored as tagged microframes; coded repeat references also shrink from `31` to `20` minified bytes, saving another `11` bytes on every measured repeat write.
- Implementor consequence: future sessions should treat `micro_seed` as the smallest first-write body and `micro_reference` as the smallest repeat pointer whenever the archive preserves the microframe codec, while keeping coded seeds/references as the clearer fallback tier.


## 2026-03-07 — Research Pass LXI (Packed Nanoframes + Finite-Payload Codes)

- Added packed nanoframes for the family10 rematch decision packet path so both new semantic bodies and duplicate pointers can compress below tagged microframes:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_packed_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_packed_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_packed.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_store_packed_nanoframes_inside_archive.md`
- Main local result: across the representative family10 packet set, micro seeds now shrink by another `3` bytes for declaration-first coordinates, `3` bytes for declaration-first weights, `13` bytes for adaptive-route packets, and `6` bytes for exact checked-cap tie packets when stored as packed seeds; micro repeat references also shrink from `20` to `14` minified bytes, saving another `6` bytes on every measured repeat write.
- Implementor consequence: future sessions should treat `packed_seed` as the smallest first-write body and `packed_reference` as the smallest repeat pointer whenever the archive preserves the packed codec, while keeping micro seeds/references as the clearer tagged-array fallback tier.


## 2026-03-07 — Research Pass LXII (Packed Weight Vectors + Keyless Axis Masks)

- Tightened the family10 packed-seed codec for `oracle_weights` so weight-mode first writes no longer carry a full JSON key map inside the packed tier:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_weight_vector_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_weight_vector_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_weight_vectors.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_store_keyless_weight_vectors_inside_packed_seeds.md`
- Main local result: hazard-only weight declarations now shrink from `125` minified bytes in the old packed-dict form to `11` bytes, mixed sparse declarations shrink from `129` to `27`, dense all-ones declarations still shrink from `125` to `39`, and the representative `oracle_weights_smm` first write now saves `117` bytes relative to the micro-seed fallback.
- Implementor consequence: future sessions should keep `packed_seed` as the default first-write tier when the local packed codec is available, but encode `oracle_weights` payloads as a fixed-order nonzero vector behind one bitmask instead of repeating axis names and explicit zero coordinates.

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

- Added packet-specific frontier measurement for the family10 rematch decision-packet stack so the archive can choose the smallest enabled local codec by actual minified bytes instead of by ladder position alone:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_frontier_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_frontier_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_frontiers.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_choose_local_decision_packet_codecs_by_measured_bytes.md`
- Main local result: on the deterministic 274-packet frontier set, the coarse byteframe-first ladder stayed right for all repeats and for 250 first writes, but 24 tiny `oracle_weights` first writes now switch back to `packed_seed`; the smallest counterexample is the width-only seed, which stores as packed `[1,1,0]` at `7` minified bytes versus `8` as a byteframe string.
- Implementor consequence: future sessions should keep the existing codec ladder as the human summary of what the archive knows how to decode, but let the executable frontier decide the actual write form, because the archive is now compressed enough that payload shape matters.

## 2026-03-07 — Research Pass LXVIII (Catalog Slot References + Append-Only Ordinals)

- Added append-only catalog-slot repeat references for the family10 rematch packet stack so a repeat can point at a stable local ordinal instead of a hash prefix whenever the archive preserves an ordered fingerprint catalog:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_catalog_reference_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_catalog_reference_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_catalog_references.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_store_append_only_catalog_slot_references_inside_archive.md`
- Main local result: on the deterministic 274-packet frontier catalog, repeat storage drops from `3288` total minified bytes as prefix byteframes to `1516` as catalog-slot references, saving `1772` bytes (`0.538929` share); the first `128` repeats cost `5` bytes each and the remaining `146` cost `6`.
- Implementor consequence: future sessions should keep an append-only ordered fingerprint catalog if they want the smallest repeat objects; if only an unordered fingerprint set is available, the writer should fall back to the older `byte_reference` path rather than invent unstable ordinals.

## 2026-03-07 — Research Pass LXIX (Paged Raw-Digest Catalogs + Append Locality)

- Added paged raw-digest fingerprint catalogs for the append-only slot-reference state so the archive can keep the ordered semantic-fingerprint catalog cheaply while preserving exact ordinals:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_catalog_page_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_catalog_page_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_catalog_pages.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_store_append_only_fingerprint_catalogs_as_paged_raw_digest_blocks.md`
- Main local result: on the deterministic 274-packet frontier catalog, the old string catalog costs `20277` bytes while a page-size-`64` raw-digest catalog costs `11714`, saving `8563` bytes (`0.422301` share); appending one new fingerprint now changes only the small tail page instead of rewriting the full string catalog.
- Implementor consequence: future sessions should keep the ordered fingerprint catalog as paged raw-digest blocks so the slot-reference savings are not given back in bulky catalog state.


## 2026-03-07 — Research Pass LXX (Short Catalog Slots + Constant-Width Repeat IDs)

- Tightened the append-only catalog repeat path so the common under-`16384` slot range no longer pays a full tag-plus-uvarint wrapper:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_short_catalog_reference_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_short_catalog_reference_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_short_catalog_references.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_store_short_catalog_slot_references_inside_small_append_only_catalogs.md`
- Main local result: on the deterministic 274-packet frontier catalog, generic catalog-slot references cost `1516` total minified bytes but short catalog-slot references cost `1370`, saving another `146` bytes (`0.096306` share) while flattening every current repeat to `5` bytes.
- Implementor consequence: future sessions should prefer `short_catalog_reference` whenever the archive preserves an ordered fingerprint catalog and the local slot fits below `16384`; once the catalog outgrows that range, fall back to the older `catalog_reference` path rather than inventing unstable local encodings.

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
  - and direct repeat lookup now scans `7155.124088` bytes on average,
  - avoiding `13121.875912` bytes (`0.647131` share) versus rebuilding the full ordered string catalog and `4558.875912` bytes (`0.389182` share) versus scanning the full paged catalog list.


## 2026-03-07 — Research Pass LXXVII (Marginal Repeat-State Staging + Sidecar Downgrades)

- Tightened compact repeat-state planning so the archive can stage sidecars exactly across novel append growth at a marginal repeat budget:
  - `scripts/analysis/rematch_proxy_delta_decision_packet.py`
  - `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_staging_snapshot.py`
  - `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_staging_snapshot_20260307.{md,json}`
  - `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_staging.py`
  - `docs/LIBRARY/topics/rematch_worlds_should_allow_compact_repeat_sidecar_downgrades_at_bitmap_cliffs.md`
- Tightened planning guidance:
  - do not treat compact repeat sidecars as monotone archive growth,
  - allow filters and route blocks to be pruned after bitmap cliffs when the current repeat budget no longer justifies them,
  - and reintroduce stronger sidecars only when the next page band makes them optimal again.
- Main local result:
  - at `0.18` expected repeats over the next `256` novel appends, the exact best-state schedule is:
    - bare pages for `0`–`8`,
    - filters for `9`–`14`,
    - bare pages for `15`–`23`,
    - filters for `24`–`30`,
    - bare pages for `31`–`37`,
    - filters for `38`–`46`,
    - bare pages for `47`–`53`,
    - filters for `54`–`62`,
    - route blocks for `63`–`110`,
    - bare pages again at the first bitmap cliff, append `111`,
    - filters for `112`–`158`,
    - route blocks for `159`–`238`,
    - and filters again for `239`–`256`.

## 2026-03-16 — Research Pass (World Benchmark Completion Gate + Fill-Status Snapshot)

- Added one executable completion gate for the first endogenous rematch-world benchmark:
  - `scripts/tools/rematch_world_benchmark_completion_gate.py`
  - `scripts/report/build_rematch_world_benchmark_fill_status_snapshot.py`
  - `artifacts/reports/rematch_world_benchmark_fill_status_snapshot_20260316.{md,json}`
  - `schemas/rematch_world_benchmark_fill_status.schema.json`
  - `scripts/test/check_rematch_world_benchmark_fill_status.py`
  - `docs/LIBRARY/topics/filled_rematch_benchmarks_should_clear_template_slots_without_touching_open_ended_decision_intervals.md`
- Main local result:
  - the retained seed is a `24`-slot in-place fill job (`13` template strings + `11` world-dependent null fields),
  - the copied compact decision bundle still contains `3` allowed open-ended `end_delay: null` intervals that are not completion blockers,
  - and a finished benchmark now has an explicit machine-checkable gate instead of only a publication shape.
- Implementor consequence:
  - future sessions should fill the named seed slots in place, flip the five world-section statuses to `filled`, and preserve the copied compact decision bundle unchanged unless the upstream decision contract itself has been revised.

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

- Added one compact fill-patch workflow for the first endogenous rematch-world benchmark:
  - `schemas/rematch_world_benchmark_fill_patch.schema.json`
  - `scripts/report/build_rematch_world_benchmark_fill_patch_example.py`
  - `examples/snapshots/rematch_world_benchmark_fill_patch.json`
  - `scripts/tools/apply_rematch_world_benchmark_fill_patch.py`
  - `scripts/report/build_rematch_world_benchmark_patch_compaction_snapshot.py`
  - `artifacts/reports/rematch_world_benchmark_patch_compaction_snapshot_20260316.{md,json}`
  - `scripts/test/check_rematch_world_benchmark_fill_patch.py`
  - `docs/LIBRARY/topics/rematch_world_benchmark_fill_work_should_flow_through_one_tiny_patch_then_compile_back_to_one_artifact.md`
- Tightened `docs/BENCHMARK_PROGRAM.md` so the inheritor now fills a tiny patch first, compiles it back onto the seed, and then runs the existing mutation/completion gates on the compiled benchmark artifact.
- Main local result:
  - the editable patch is `2372` bytes versus `51329` bytes for the full retained seed,
  - which saves `48957` bytes (`0.953788` share) during scratch fill work,
  - while keeping the copied `compact_decision_bundle` and contract-pointer surfaces out of the scratch artifact entirely.
- Implementor consequence:
  - future sessions should treat the patch as the temporary working surface,
  - compile back to one retained benchmark artifact before validation/publication,
  - and avoid retaining a growing chain of benchmark patch sidecars.

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
- Tightened `docs/BENCHMARK_PROGRAM.md` so the benchmark workflow now distills one tiny evidence packet after a real run, compiles it into the standard fill patch, and keeps bulky traces scratch-only once the distilled facts are retained.
- Main local result:
  - the retained evidence packet example weighs `3103` bytes and the compiled fill patch weighs `3176` bytes, versus `51329` bytes for the standing seed,
  - the packet-to-patch expansion adds only `73` bytes because the packet already carries the exact world-dependent facts the patch needs,
  - and the compiled example remains preflight-ready with `0` forbidden changed paths, `0` fill blockers, and the copied decision-bundle digest still equal to the standing contract.
- Implementor consequence:
  - future sessions can let raw traces and bulky temporary run tables stay scratch-only,
  - retain one tiny evidence packet as the citation target for distilled world facts,
  - and compile that packet forward through the standing patch/seed/preflight workflow without inventing a second benchmark format.

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


## 2026-03-17 — Research Pass (Benchmark-Native Canonicalization Handoff)

- Added one compact benchmark-native canonicalization handoff so the rematch-world seed can carry the SG-003 planner surface directly instead of forcing inheritors to chase the bridge receipt separately from the benchmark artifact family:
  - `schemas/rematch_world_benchmark_canonicalization_handoff.schema.json`
  - `scripts/tools/build_rematch_world_benchmark_canonicalization_handoff.py`
  - `scripts/report/build_rematch_world_benchmark_canonicalization_handoff_example.py`
  - `examples/snapshots/rematch_world_benchmark_canonicalization_handoff.json`
  - `scripts/report/build_rematch_world_benchmark_canonicalization_handoff_snapshot.py`
  - `artifacts/reports/rematch_world_benchmark_canonicalization_handoff_snapshot_20260317.{md,json}`
  - `scripts/test/check_rematch_world_benchmark_canonicalization_handoff.py`
  - `docs/LIBRARY/topics/first_retained_rematch_world_benchmark_should_copy_forward_the_canonicalization_bridge_contract.md`
- Tightened the benchmark artifact scaffold and compile-path checks so compiled candidates keep the copied handoff without widening the mutable publication surface:
  - `examples/snapshots/rematch_world_benchmark_seed.json`
  - `schemas/rematch_world_benchmark_seed.schema.json`
  - `scripts/report/build_rematch_world_benchmark_seed_example.py`
  - `scripts/test/check_rematch_world_benchmark_seed.py`
  - `scripts/test/check_rematch_world_benchmark_fill_patch.py`
  - `scripts/test/check_rematch_world_benchmark_evidence_packet.py`
  - `docs/BENCHMARK_PROGRAM.md`
- Main local result:
  - compiled rematch-world benchmark artifacts now inherit one embedded planner handoff with `4` mode rows and horizons `{none:3, opponent_tremble:2, focal_tremble:2, bilateral_tremble:1}`,
  - the copied benchmark handoff keeps only the bridge digest, invalidation triggers, and the zero-noise `243 -> 17` dispatch compression summary,
  - and the mutable benchmark publication surface stays unchanged while the inheritor-facing canonicalization seam becomes native to the seed.


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
- Tightened `docs/BENCHMARK_PROGRAM.md` so fill work now starts from an explicitly rebuild-audited frozen seed rather than from visual trust in a large copied artifact.
- Main local result:
  - the standing seed rebuild-matches exactly with digest `3e8e882161f779754d4cf52fabd801ec7854690b166f8563909190d061a917e7`,
  - all `8` audited frozen sections exact-match their source artifacts,
  - and the new retained receipt keeps the archive citation-first by pointing to `8` source artifacts instead of introducing another benchmark-side snapshot family.

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



## 2026-03-17 — Research Pass (Canonical First Trim Execution)

- Executed the first cited archive-report compaction frontier for real instead of only rehearsing it: removed the 12 retained report files named by the standing exact-file manifest, spanning 6 citation-backed families and reclaiming 554504 report bytes from `artifacts/reports`.
- Added one compact execution receipt so future inheritors can cite what actually left the archive and what frontier replaced it:
  - `schemas/archive_report_compaction_execution_receipt.schema.json`
  - `scripts/tools/build_archive_report_compaction_execution_receipt.py`
  - `examples/snapshots/archive_report_compaction_execution_receipt.json`
  - `scripts/test/check_archive_report_compaction_execution_receipt.py`
  - `docs/LIBRARY/topics/archive_size_control_should_carry_one_execution_receipt_after_canonical_trim.md`
- Refreshed the package / hotspot / semantic-handle / candidate / gap / manifest / rehearsal / stage stack on the smaller tree and tightened the fixed-point / handle-search exclusions so the new execution receipt cannot masquerade as a durable scientific handle or perturb the size-profiled package boundary.
- Main local result:
  - `artifacts/reports` fell from 500 files / 5570559 raw bytes to 488 files / 5016864 raw bytes,
  - the whole retained tree fell by 515305 raw bytes net even after adding the new compact control surface files,
  - and the next frontier is now smaller but no longer zero-gap: the refreshed rehearsal projects 3 newly exposed handle gaps, so the next byte-saving pass should repair those before trimming again.
- Reused three additional standing library topics through the buffered semantic-handle layer instead of minting new notes:
  - `rematch_worlds_should_not_panic_close_positive_batches_after_geometric_miss_streaks.md` now covers the checkpoint-extension hotspot family,
  - `rematch_worlds_should_select_positive_service_local_weakening_witnesses_by_interval_clamp.md` now covers the feasible-witness-selector hotspot family,
  - and `rematch_worlds_should_budget_positive_same_deadline_live_waits_by_hold_cost_ceiling.md` now covers the live hold-cost-ceiling family that appears one trim ahead.
- That semantic reuse clears the current top-hotspot handle-gap receipt to zero and flips the refreshed next-frontier rehearsal from gap-exposing to fully handle-covered.
- The next exact-file frontier is now smaller and cleaner at `359964` raw bytes across six citation-backed families, so future compaction can start from the refreshed manifest / stage pair on the smaller tree instead of minting another durable note first.

## 2026-03-18 — Research Pass (Second Canonical Trim Execution)

- Executed the next cited archive-report compaction frontier on the live tree rather than leaving the smaller-tree manifest as a rehearsal only:
  - deleted `12` retained report files across `6` citation-backed families,
  - refreshed `examples/snapshots/archive_report_compaction_execution_receipt.json`,
  - and rebuilt the package / hotspot / compaction stack on the smaller tree.
- Main local result:
  - `359964` raw report bytes actually left `artifacts/reports`,
  - the retained tree fell from `14010864` to `13650900` raw bytes,
  - the approximate revision zip fell from `3509662` to `3473900` bytes,
  - and the second trim made the next frontier smaller but initially exposed `5` projected handle gaps instead of hiding them inside the old rehearsal surface.

## 2026-03-18 — Research Pass (Buffered Semantic-Handle Recovery)

- Rewired the buffered semantic-handle layer so the next compaction frontier reuses standing durable notes instead of minting new archive mass for already-solved claims:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with five additional aliases that point current hotspot families to existing library topics,
  - refreshed the semantic-handle / candidate / gap / manifest / rehearsal / stage receipts on the current smaller tree,
  - and kept the archive citation-first by reusing the existing topic handles for selector-index, target-timeout, odd-deadline, timeout-batch-cap, and live-margin-ceiling laws.
- Main local result:
  - the buffered semantic-handle receipt now recovers `6` hotspot families totaling `298891` raw bytes,
  - the current top-hotspot gap receipt goes back to `0` blocked families,
  - the next manifest shrinks to `303819` raw bytes across `6` citation-backed families,
  - and the refreshed rehearsal again shows `0` projected second-wave handle gaps, so a future byte-saving pass can start from the standing manifest / stage pair without minting another durable note first.

## 2026-03-18 — Research Pass (Third Canonical Trim Execution)

- Executed the next cited archive-report compaction frontier on the live tree and refreshed the smaller-tree control surface without widening the archive with new durable note families:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`,
  - refreshed `examples/snapshots/rematch_world_benchmark_package_receipt.json`,
  - `examples/snapshots/archive_report_hotspot_receipt.json`,
  - `examples/snapshots/archive_report_semantic_handle_receipt.json`,
  - `examples/snapshots/archive_report_compaction_candidate_receipt.json`,
  - `examples/snapshots/archive_report_compaction_gap_receipt.json`,
  - `examples/snapshots/archive_report_compaction_manifest_receipt.json`,
  - `examples/snapshots/archive_report_compaction_rehearsal_receipt.json`,
  - `examples/snapshots/archive_report_compaction_stage_receipt.json`,
  - and `examples/snapshots/archive_report_compaction_execution_receipt.json`.
- Main local result:
  - the cited frontier actually left the archive instead of lingering as another rehearsal surface,
  - the tree stayed package-ready, PDF-free, and scratch-free after the trim,
  - and the refreshed next frontier remains explicitly handle-covered, so a future inheritor can start from the new smaller-tree manifest rather than reconstructing the byte-saving seam by hand.

## 2026-03-18 — Research Pass (Projected-Frontier Alias Recovery)

- Extended the buffered semantic-handle layer on the smaller tree instead of minting new notes for claims the archive already knows how to cite:
  - updated `scripts/tools/build_archive_report_semantic_handle_receipt.py`,
  - refreshed `examples/snapshots/archive_report_semantic_handle_receipt.json`,
  - `examples/snapshots/archive_report_compaction_candidate_receipt.json`,
  - `examples/snapshots/archive_report_compaction_gap_receipt.json`,
  - `examples/snapshots/archive_report_compaction_manifest_receipt.json`,
  - `examples/snapshots/archive_report_compaction_rehearsal_receipt.json`,
  - `examples/snapshots/archive_report_compaction_stage_receipt.json`,
  - and `examples/snapshots/archive_report_compaction_execution_receipt.json`.
- Main local result:
  - semantic aliasing now recovers `6` buffered hotspot families on the smaller tree,
  - both the live hotspot surface and the projected next frontier return to `0` blocked handle gaps,
  - and the next exact-file frontier compresses to `278558` raw bytes across `6` citation-backed families.


## 2026-03-18 — Research Pass (Fourth Canonical Trim Execution)

- Executed the standing cited exact-file compaction frontier on the live tree rather than leaving the refreshed manifest as rehearsal only:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`,
  - refreshed `examples/snapshots/rematch_world_benchmark_package_receipt.json`,
  - `examples/snapshots/archive_report_hotspot_receipt.json`,
  - `examples/snapshots/archive_report_semantic_handle_receipt.json`,
  - `examples/snapshots/archive_report_compaction_candidate_receipt.json`,
  - `examples/snapshots/archive_report_compaction_gap_receipt.json`,
  - `examples/snapshots/archive_report_compaction_manifest_receipt.json`,
  - `examples/snapshots/archive_report_compaction_rehearsal_receipt.json`,
  - `examples/snapshots/archive_report_compaction_stage_receipt.json`,
  - and `examples/snapshots/archive_report_compaction_execution_receipt.json`.
- Main local result:
  - `278558` raw report bytes actually left `artifacts/reports`,
  - the retained tree fell to `13086572` raw bytes and the approximate revision zip fell to `3409544` bytes,
  - the report bucket fell to `4074523` raw bytes across `452` retained report files,
  - and the smaller-tree frontier initially exposed `3` current hotspot handle gaps plus `4` projected second-wave handle gaps instead of staying frontier-clear by default.

## 2026-03-18 — Research Pass (Frontier Reclosure by Semantic Reuse)

- Rewired the buffered semantic-handle layer so the new smaller-tree hotspot and one-trim-ahead frontier reuse standing durable notes instead of minting fresh archive mass:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with four additional aliases that point current hotspot families to existing library topics for canonical-anchor control, width-only service tiers, live batch caps, and analytic decision-packet frontiers,
  - refreshed the semantic-handle / candidate / gap / manifest / rehearsal / stage / execution receipts on the current smaller tree,
  - and tightened the targeted validator scripts so the receipt checks stay aligned with the live smaller-tree frontier.
- Main local result:
  - the buffered semantic-handle receipt now recovers `6` hotspot families totaling `246000` raw bytes,
  - the current top-hotspot gap receipt goes back to `0` blocked families,
  - the refreshed rehearsal again shows `0` projected second-wave handle gaps,
  - and the next exact-file frontier settles at `334545` raw bytes across `6` citation-backed families with `5` semantic-alias-backed rows.

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

## 2026-03-18 — Research Pass (Seventh Canonical Trim + Frontier Reseed)

- Executed the standing cited exact-file compaction frontier on the live tree and then reclosed the next frontier without minting any new bulky durable note:
  - removed `12` retained report files across `6` families from `artifacts/reports`, reclaiming `202109` raw report bytes from the rev0263 manifest,
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `3` additional aliases for portfolio-confidence ladders, primitive-demand chain holes, and equiprobable exact mean-cost budgeting,
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
  - and refreshed `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`.
- Tightened execution-accounting durability so signed same-pass retained-file drift is representable when it appears instead of being rejected by schema or validator assumptions:
  - updated `scripts/tools/build_archive_report_compaction_execution_receipt.py`,
  - updated `schemas/archive_report_compaction_execution_receipt.schema.json`,
  - and updated the targeted validator scripts.
- Main local result:
  - the retained tree falls to `1693` files and `12359649` raw bytes with an approximate revision zip of `3323319` bytes,
  - the live report bucket falls to `416` files and `3310575` raw bytes,
  - the semantic-handle layer now recovers `5` buffered hotspot families totaling `156416` raw bytes,
  - the refreshed first-pass exact-file frontier is `188715` raw bytes across `6` citation-backed families,
  - the refreshed rehearsal again shows `0` projected second-wave handle gaps,
  - and the reseeded execution receipt now passes `24/24` checks while proving the `202109`-byte canonical trim actually left the archive.


## 2026-03-18 — Research Pass (Ninth Canonical Trim Execution)

- Executed the standing cited exact-file compaction frontier on the live tree instead of leaving the refreshed manifest as rehearsal only:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`,
  - refreshed `examples/snapshots/rematch_world_benchmark_package_receipt.json`,
  - `examples/snapshots/archive_report_hotspot_receipt.json`,
  - `examples/snapshots/archive_report_semantic_handle_receipt.json`,
  - `examples/snapshots/archive_report_compaction_candidate_receipt.json`,
  - `examples/snapshots/archive_report_compaction_gap_receipt.json`,
  - `examples/snapshots/archive_report_compaction_manifest_receipt.json`,
  - `examples/snapshots/archive_report_compaction_rehearsal_receipt.json`,
  - `examples/snapshots/archive_report_compaction_stage_receipt.json`,
  - `examples/snapshots/archive_report_compaction_execution_receipt.json`,
  - `artifacts/reports/artifact_summary.json`,
  - `artifacts/reports/artifact_bucket_inventory.json`,
  - `docs/ARTIFACT_BUCKETS.md`,
  - and `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`.
- Main local result:
  - `208051` raw report bytes actually left `artifacts/reports`,
  - the retained tree and approximate revision zip both shrank again on the live archive,
  - and the smaller-tree frontier initially exposed `2` current hotspot handle gaps before semantic reuse was refreshed.

## 2026-03-18 — Research Pass (Frontier Reclosure by Standing Topic Reuse)

- Rewired the buffered semantic-handle layer so the new smaller-tree hotspot and one-trim-ahead frontier reuse standing durable notes instead of minting fresh archive mass:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with two additional aliases that point current hotspot families to existing library topics for local-upgrade witness cards and shared-state exact local-margin thresholds,
  - refreshed the semantic-handle / candidate / gap / manifest / rehearsal / stage / execution receipts on the current smaller tree,
  - and kept the refreshed execution receipt seeded from the actual rev0265 pre-trim package / manifest pair rather than the prior trim.
- Main local result:
  - the buffered semantic-handle receipt now recovers `4` hotspot families totaling `107850` raw bytes,
  - the current top-hotspot gap receipt goes back to `0` blocked families,
  - the refreshed rehearsal again shows `0` projected second-wave handle gaps,
  - and the next exact-file frontier settles at `160435` raw bytes across `6` citation-backed families with `4` semantic-alias-backed rows.


## 2026-03-18 — Research Pass (Tenth Canonical Trim + Semantic Ready-Empty Fix + Frontier Reclosure)

- Executed the standing cited exact-file compaction frontier on the live tree:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `160435` raw report bytes from the rev0266 manifest,
  - refreshed `artifacts/reports/artifact_summary.json`, `artifacts/reports/artifact_bucket_inventory.json`, `docs/ARTIFACT_BUCKETS.md`, and `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}` on the smaller tree.
- Tightened semantic-handle durability so a fully literal-covered hotspot surface is still a ready state instead of a false failure:
  - updated `scripts/tools/build_archive_report_semantic_handle_receipt.py`,
  - and updated `scripts/test/check_archive_report_semantic_handle_receipt.py` so an empty alias table is valid when no semantic bridge is needed.
- Reclosed the newly exposed hotspot and one-trim-ahead frontier by reusing standing library topics instead of minting fresh durable notes:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `5` additional aliases for width-cap guarantees, width-law governance, affine shared-state margin families, base64url byteframes, and feasibility-intersection clocks,
  - refreshed `examples/snapshots/archive_report_semantic_handle_receipt.json`,
  - `examples/snapshots/archive_report_compaction_candidate_receipt.json`,
  - `examples/snapshots/archive_report_compaction_gap_receipt.json`,
  - `examples/snapshots/archive_report_compaction_manifest_receipt.json`,
  - `examples/snapshots/archive_report_compaction_rehearsal_receipt.json`,
  - `examples/snapshots/archive_report_compaction_stage_receipt.json`,
  - and reseeded `examples/snapshots/archive_report_compaction_execution_receipt.json` from the actual rev0266 pre-trim package / manifest pair.
- Main local result:
  - the current smaller tree now exposes a fresh exact-file frontier of `152663` raw bytes across `6` citation-backed families,
  - the semantic-handle layer recovers `5` hotspot families totaling `125915` raw bytes,
  - the live hotspot surface returns to `0` true handle gaps,
  - the refreshed rehearsal again shows `0` projected next-frontier handle gaps,
  - and future byte-saving can start from the new current manifest rather than reopening the already removed rev0266 frontier.

## 2026-03-18 — Research Pass (Thirteenth Canonical Trim + Semantic Frontier Reclosure)

- Executed the standing cited exact-file compaction frontier on the live tree instead of leaving the refreshed manifest as rehearsal only:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `141274` raw report bytes from the rev0269 manifest,
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
  - and refreshed `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`.
- Reclosed the newly exposed hotspot and one-trim-ahead frontier by standing topic reuse instead of minting new durable notes:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `4` additional aliases for batch-median compromise witnesses, archive-local prefix references, odd hazard staircases, and residual-axis service budgets,
  - updated `scripts/test/check_archive_report_{semantic_handle,compaction_candidate,compaction_manifest,compaction_rehearsal,compaction_stage}_receipt.py` so the refreshed smaller-tree expectations match the live archive,
  - and kept the refreshed next frontier citation-backed with `0` projected handle gaps after the thirteenth trim.
- Main local result:
  - the retained tree falls to `1617` files and `11391313` raw bytes with an approximate revision zip of `3150661` bytes,
  - the live report bucket falls to `340` files and `2287755` raw bytes,
  - the semantic-handle layer now recovers `6` hotspot families totaling `135062` raw bytes,
  - the refreshed first-pass exact-file frontier is `135489` raw bytes across `6` citation-backed families with `4` semantic-alias-backed rows,
  - the refreshed rehearsal again shows `0` projected next-frontier handle gaps,
  - and the refreshed execution receipt still passes `26/26` checks while proving the `141274`-byte cited trim actually left the archive.

## 2026-03-18 — Research Pass (Fourteenth Canonical Trim + Second-Wave Semantic Frontier Seal)

- Executed the standing cited exact-file compaction frontier on the live tree instead of leaving the refreshed manifest as rehearsal only:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `135489` raw report bytes from the rev0270 manifest,
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
  - and refreshed `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`.
- Reclosed the newly exposed hotspot and one-trim-ahead frontier by standing topic reuse instead of minting new durable notes:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `5` additional aliases for primitive overshoot taxonomy, budget-admissible delta bands, bandwise local slack lead, equiprobable exact target-margin sizing, and local corridor-exit witnesses,
  - updated `scripts/test/check_archive_report_{semantic_handle,compaction_candidate,compaction_manifest,compaction_rehearsal,compaction_stage,compaction_gap}_receipt.py` so the refreshed smaller-tree expectations match the live archive,
  - and kept the refreshed next frontier citation-backed with `0` projected handle gaps after the fourteenth trim.
- Main local result:
  - the retained tree falls to `1605` files and `11271101` raw bytes with an approximate revision zip of `3124870` bytes,
  - the live report bucket falls to `328` files and `2152266` raw bytes,
  - the semantic-handle layer now recovers `7` hotspot families totaling `153754` raw bytes,
  - the refreshed first-pass exact-file frontier is `132685` raw bytes across `6` citation-backed families with `5` semantic-alias-backed rows,
  - the refreshed rehearsal again shows `0` projected next-frontier handle gaps,
  - and the refreshed execution receipt still passes `26/26` checks while proving the `135489`-byte cited trim actually left the archive.

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

- Added one compact inheritor-facing contract note:
  - `docs/LIBRARY/topics/rematch_worlds_should_publish_starting_policy_and_adaptation_rules_as_a_world_contract.md`
- Extended `docs/RESEARCH_SOURCES.md` with `RS-GR-042`, turning test-time adaptation from a hidden controller detail into explicit world-contract metadata.
- Executed one more cited exact-file compaction frontier on the live tree:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `88278` raw report bytes from the pre-trim frontier,
  - refreshed `examples/snapshots/rematch_world_benchmark_package_receipt.json`,
  - refreshed `examples/snapshots/archive_report_{hotspot,semantic_handle,compaction_candidate,compaction_gap,compaction_manifest,compaction_rehearsal,compaction_stage,compaction_execution}_receipt.json`,
  - and kept the archive package-ready, PDF-free, scratch-free, and pycache-free after the trim.
- Reclosed the refreshed live hotspot and projected next frontier by standing topic reuse instead of minting new durable notes:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `5` additional aliases for preference half-spaces, fixed-policy regret, grouped repeated weight atoms, shared decision-packet provenance profiles, and hazard-preference regimes,
  - updated `scripts/test/check_archive_report_{semantic_handle,compaction_candidate,compaction_manifest,compaction_rehearsal,compaction_stage}_receipt.py` so the refreshed smaller-tree expectations match the live archive,
  - and kept the refreshed next frontier citation-backed with `0` projected handle gaps after the trim.
- Main local result:
  - the retained tree falls to `1503` files and `10336101` raw bytes with an approximate revision zip of `2917539` bytes,
  - the live report bucket falls to `220` files and `1142504` raw bytes,
  - the semantic-handle layer now recovers `5` buffered hotspot families totaling `69081` raw bytes,
  - the refreshed first-pass exact-file frontier settles at `83154` raw bytes across `6` citation-backed families with `3` semantic-alias-backed rows,
  - the refreshed rehearsal again shows `0` projected next-frontier handle gaps,
  - and the refreshed execution receipt passes `26/26` checks while proving the `88278`-byte cited trim actually left the archive.

## 2026-03-18 — Research Pass (Twenty-Third Canonical Trim + Anchor Alias Recovery + Stability-Surface Source)

- Extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with one additional alias that recovers `rematch_proxy_delta_anchor_contract` through the standing durable note `docs/LIBRARY/topics/rematch_worlds_need_topology_stable_delta_anchors.md`, so the archive can cite the topology-stable-anchor rule instead of retaining the bulky paired report family.
- Extended `docs/RESEARCH_SOURCES.md` with `RS-GR-044`, using Menendez et al. (2026) to reinforce the inheritor rule that uncertainty-aware benchmark outputs should prefer stability surfaces or partial orders over brittle point summaries when nearby local context can change the live ordering.
- Executed one more cited exact-file compaction frontier on the live tree:
  - removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `96354` raw report bytes,
  - refreshed the package / hotspot / semantic-handle / candidate / gap / manifest / rehearsal / stage / execution receipts,
  - refreshed `artifacts/reports/artifact_summary.json`, `artifacts/reports/artifact_bucket_inventory.json`, `docs/ARTIFACT_BUCKETS.md`, and `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`,
  - and kept the archive package-ready, PDF-free, scratch-free, and pycache-free after the trim.
- Main local result:
  - the largest remaining hotspot family was retired by standing-topic reuse rather than by minting new durable prose,
  - the refreshed semantic-handle layer on the smaller tree returns to `0` aliases because the live frontier is already literal-handle-covered,
  - the refreshed next exact-file frontier remains citation-backed with `0` projected next-frontier handle gaps,
  - and the refreshed execution receipt passes `26/26` checks while proving the `96354`-byte cited trim actually left the archive.


## 2026-03-19 — Research Pass (Twenty-Seventh Canonical Trim + Human-Proxy Contract + Frontier Reclosure)

- Added one compact inheritor-facing benchmark-contract note:
  - `docs/LIBRARY/topics/cooperation_benchmarks_should_publish_human_proxy_provenance_and_real_human_escalation_status.md`
- Extended `docs/RESEARCH_SOURCES.md` with `RS-GR-050`, using Dizdarevic et al. (2025) so human-proxy partners are treated as a distinct benchmark lane whose provenance, hosting posture, and relation to real-human evaluation must be published explicitly.
- Executed one more cited exact-file compaction frontier on the live tree:
  - staged and removed `12` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `51057` raw report bytes from the rev0284 frontier,
  - validated the trimmed tree during stage mode with `scripts/test/check_reports_json_valid.py`, `scripts/test/check_research_docs.py`, and `scripts/test/check_generated_docs_presence.py`,
  - refreshed `examples/snapshots/rematch_world_benchmark_package_receipt.json`,
  - refreshed `examples/snapshots/archive_report_{hotspot,semantic_handle,compaction_candidate,compaction_gap,compaction_manifest,compaction_rehearsal,compaction_stage,compaction_execution}_receipt.json`,
  - refreshed `artifacts/reports/artifact_summary.json`, `artifacts/reports/artifact_bucket_inventory.json`, `docs/ARTIFACT_BUCKETS.md`, and `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`,
  - and kept the archive package-ready, PDF-free, scratch-free, and pycache-free after the trim.
- Reclosed the refreshed next frontier by standing topic reuse instead of leaving second-wave handle gaps behind:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `2` additional aliases for `rematch_proxy_delta_unique_minimal_cap_probe` and `rematch_proxy_delta_budget_frontier`,
  - updated `scripts/test/check_archive_report_{semantic_handle,compaction_candidate,compaction_manifest,compaction_rehearsal,compaction_stage}.py` so the refreshed smaller-tree expectations match the live archive,
  - and restored the refreshed next frontier to `0` projected handle gaps after the executed trim.
- Main local result:
  - the refreshed semantic-handle layer now recovers `6` buffered hotspot families totaling `73578` raw bytes,
  - the refreshed first-pass exact-file frontier settles at `70808` raw bytes across `6` citation-backed families with `3` semantic-alias-backed rows,
  - the refreshed rehearsal again shows `0` projected next-frontier handle gaps,
  - and the refreshed execution receipt proves the `51057`-byte cited trim actually left the archive while the next smaller frontier remains citation-backed.

## 2026-03-19 — Research Pass (Twenty-Ninth Canonical Trim + Language Contract + Patch-Alias Frontier Reclosure)

- Added one compact inheritor-facing benchmark-contract note:
  - `docs/LIBRARY/topics/cooperation_benchmarks_should_publish_interaction_language_and_translation_policy.md`
- Extended `docs/RESEARCH_SOURCES.md` with `RS-GR-053` and `RS-GR-054`, turning interaction language, localization, and wording frame into explicit cooperation-benchmark metadata rather than invisible prompt wrapper state.
- Executed one more cited exact-file compaction frontier on the live tree:
  - staged and removed `11` retained report files across `6` citation-backed families from `artifacts/reports`, reclaiming `47123` raw report bytes from the rev0286 frontier,
  - validated the trimmed tree with `scripts/test/check_reports_json_valid.py`, `scripts/test/check_research_docs.py`, and `scripts/test/check_generated_docs_presence.py`,
  - refreshed `examples/snapshots/rematch_world_benchmark_package_receipt.json`,
  - refreshed `examples/snapshots/archive_report_{hotspot,semantic_handle,compaction_candidate,compaction_gap,compaction_manifest,compaction_rehearsal,compaction_stage,compaction_execution}_receipt.json`,
  - refreshed `artifacts/reports/artifact_summary.json`, `artifacts/reports/artifact_bucket_inventory.json`, `docs/ARTIFACT_BUCKETS.md`, and `artifacts/reports/archive_size_profile_snapshot_20260316.{md,json}`,
  - and kept the archive package-ready, PDF-free, scratch-free, and pycache-free after the trim.
- Reclosed the newly exposed one-trim-ahead gap by standing topic reuse instead of minting another durable note:
  - extended `scripts/tools/build_archive_report_semantic_handle_receipt.py` with `1` additional alias for `rematch_world_benchmark_patch_compaction`, reusing `docs/LIBRARY/topics/rematch_world_benchmark_fill_work_should_flow_through_one_tiny_patch_then_compile_back_to_one_artifact.md`,
  - updated the archive-report receipt tests so the refreshed smaller-tree expectations match the live archive,
  - and restored the refreshed next frontier to `0` projected handle gaps after the executed trim.
- Main local result:
  - the live report bucket falls to `56` retained files and `101456` raw bytes,
  - the semantic-handle layer now recovers `2` buffered hotspot families totaling `8040` raw bytes,
  - the refreshed first-pass exact-file frontier settles at `33883` raw bytes across `6` citation-backed families with `2` semantic-alias-backed rows,
  - the refreshed rehearsal again shows `0` projected next-frontier handle gaps,
  - and the refreshed execution receipt proves the `47123`-byte cited trim actually left the archive while the next smaller frontier remains citation-backed.

## Additional pass: communication-lane contract + thirtieth canonical trim

### What changed

- Added one compact implementor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmarks_should_publish_communication_schedule_and_channel_rights.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-055` (Anwar & Georgalos, 2026), and
  - `RS-GR-056` (Niszczota et al., 2025).
- Executed the currently cited exact-file trim frontier recorded on the rev0287 tree:
  - `11` retained report files,
  - `6` families,
  - `33883` executed raw bytes.

### Research / inheritor insight

Human/AI cooperation results are not only about who the counterpart is; they are also about the communication lane.
The recent repeated-PD evidence says message timing can change the treatment interpretation itself, while the finite-game evidence says allowing communication can materially raise cooperation with both humans and LLMs even when the human-machine gap remains.
So benchmark cards should publish whether communication was disallowed, pre-play-only, repeated, free-form, templated, symmetric, or pooled across regimes.

### Frontier reclosure

This trim exposed two compact archive-shaping facts on the smaller tree:

- `artifacts/reports` is no longer the single largest retained artifact bucket once the fixed-point report receipts are excluded, so the hotspot receipt now treats the reports bucket as one of the top two retained artifact buckets rather than requiring it to remain #1 forever.
- the only real second-wave handle gap was `rematch_world_benchmark_evidence_flow`, and it is now recovered through one standing semantic alias to `docs/LIBRARY/topics/first_endogenous_rematch_benchmarks_should_distill_one_tiny_evidence_packet_before_compiling_the_fill_patch.md` instead of a new bulky report family.

### Current live posture

- package receipt ready (`7/7`)
- semantic-handle receipt ready (`8/8`) with `1` semantic alias / `2623` raw bytes recovered
- candidate receipt ready (`7/7`) with a `17886`-byte next trim frontier
- rehearsal receipt ready (`11/11`) with `0` projected next-frontier gaps
- stage receipt ready (`15/15`)
- execution receipt ready (`26/26`)
- retained tree: `1346` files / `9391673` raw bytes / `2650584` approximate zip bytes
- report bucket: `45` files / `67573` raw bytes

## Additional pass: stakes/comprehension contract + thirty-first canonical trim

### What changed

- Added one compact implementor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmark_human_lanes_should_publish_material_stakes_and_comprehension_protocol.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-057` (Gächter et al., 2024), and
  - `RS-GR-058` (Koppel et al., 2025).
- Executed the cited rev0288 trim frontier:
  - `12` retained report files across `6` families removed from `artifacts/reports`, reclaiming `17886` raw bytes.
- Reclosed the refreshed next frontier by reusing the standing anti-vampire scorecard spec as the durable handle for `extortion_metric`, restoring `0` projected next-frontier handle gaps on the smaller tree.

### Current live posture

- package receipt ready (`7/7`)
- semantic-handle receipt ready (`8/8`)
- candidate receipt ready (`7/7`) with a `14667`-byte next trim frontier
- rehearsal receipt ready (`11/11`) with `0` projected next-frontier gaps
- stage receipt ready (`15/15`)
- execution receipt ready (`26/26`)
- report bucket: `33` files / `49687` raw bytes


## Additional pass: participant-pool provenance lane + thirty-second canonical trim

### What changed

- Added one compact implementor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmark_human_lanes_should_publish_participant_pool_provenance_and_repeat_exposure_policy.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-059` (Karpus et al., 2025), and
  - `RS-GR-060` (Moon et al., 2026).
- Executed the cited rev0289 trim frontier:
  - `12` retained report files across `6` families removed from `artifacts/reports`, reclaiming `14667` raw bytes.
- Reclosed the refreshed next frontier without minting another durable note: the smaller tree stays fully handle-covered through the next rehearsal using standing library-topic and snapshot handles only.

### Research / inheritor insight

Human-lane cooperation results are not only about the evaluated policy or the counterpart disclosure condition.
They also depend on who the sampled humans are, where they were recruited, and whether they have already seen similar AI or game setups.
So benchmark cards should publish the recruitment platform, country/residence mix, key eligibility filters, repeat-participation rule, and whether headline results pool across distinct participant populations.

### Current live posture

- package receipt ready (`7/7`)
- semantic-handle receipt ready (`8/8`)
- candidate receipt ready (`7/7`) with a `23371`-byte next trim frontier
- rehearsal receipt ready (`11/11`) with `0` projected next-frontier gaps
- stage receipt ready (`15/15`)
- execution receipt ready (`26/26`)
- retained tree: `1324` files / `9373999` raw bytes / `2633585` approximate zip bytes
- report bucket: `21` files / `35020` raw bytes


## Additional pass: horizon / stopping-rule contract + thirty-third canonical trim

### What changed

- Added one compact implementor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmarks_should_publish_interaction_horizon_stopping_rule_and_termination_knowledge.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-061` (Smyth et al., 2023), and
  - `RS-GR-062` (Mengel, 2022).
- Executed the cited rev0290 trim frontier:
  - `9` retained report files across `6` families removed from `artifacts/reports`, reclaiming `23371` raw bytes.
- Reclosed the refreshed next frontier with three tiny semantic aliases instead of retaining more validation-summary fanout:
  - `risk_register_validation`
  - `claim_register_validation`
  - `claim_classes_validation`

### Research / inheritor insight

Repeated-interaction cooperation results are not only about partner identity, communication, or language.
They also depend on the shadow of the future:
- whether play is one-shot, finite, or indefinite,
- what the stopping rule is,
- and what participants know about termination while they are deciding.
So benchmark cards should publish the horizon regime, stopping-rule parameters, and participant knowledge of termination instead of laundering those choices into a policy-generalization claim.

### Current live posture

- package receipt ready (`7/7`)
- semantic-handle receipt ready (`8/8`) with `3` semantic aliases / `838` raw bytes recovered
- candidate receipt ready (`7/7`) with an `8123`-byte next trim frontier
- rehearsal receipt ready (`11/11`) with `0` projected next-frontier gaps
- stage receipt ready (`15/15`)
- execution receipt ready (`26/26`)
- retained tree: `1319` files / `9359497` raw bytes / `2631241` approximate zip bytes
- report bucket: `12` files / `11649` raw bytes


## Additional pass: process-aware / common-ground contract + thirty-fourth canonical trim

### What changed

- Added one compact implementor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmarks_should_publish_process_capture_and_common_ground_metrics_not_only_outcome_scores.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-063` (Xie et al., 2026), and
  - `RS-GR-064` (Poelitz et al., 2026).
- Executed the cited rev0291 trim frontier:
  - `6` retained report files across `6` families removed from `artifacts/reports`, reclaiming `8123` raw bytes.
- Reclosed the now much smaller archive surface by updating three stale nonterminal compaction assumptions:
  - the hotspot receipt now treats `artifacts/reports` as a top-three artifact bucket on this smaller tree,
  - the candidate receipt no longer requires a library-topic-backed pair once the frontier has collapsed to direct-handle single-file families,
  - and the rehearsal receipt now permits an empty projected next frontier when the next exact trim would fully empty `artifacts/reports`.

### Research / inheritor insight

Cooperation results are not only about final payoffs or cooperation rates.
They can also differ in whether interaction reaches stable shared understanding, whether misunderstanding is repaired cheaply, and whether the observed success hides inconsistent reasoning or brittle communication.
So benchmark cards should publish whether the evaluation is outcome-only or process-aware, which trace channels were captured, and any grounding / repair metrics used in the reported interpretation.

### Current live posture

- package receipt ready (`7/7`)
- semantic-handle receipt ready (`8/8`) with `0` semantic aliases / `0` alias bytes recovered on the terminal live frontier
- candidate receipt ready (`7/7`) with a `3526`-byte next trim frontier
- rehearsal receipt ready (`11/11`) with a terminal projected next frontier of `0` families / `0` gaps after the next exact trim
- stage receipt ready (`15/15`)
- execution receipt ready (`26/26`)
- report bucket: `6` files / `3526` raw bytes


## Additional pass: typed next action + arbitration witness for compact cards

### What changed

- Added compact-card first-reentry surfaces:
  - `schemas/cooperation_benchmark_card_next_action.schema.json`
  - `schemas/cooperation_benchmark_card_next_action_witness.schema.json`
  - `scripts/report/build_cooperation_benchmark_card_next_action.py`
  - `scripts/report/build_cooperation_benchmark_card_next_action_witness.py`
  - `scripts/test/check_cooperation_benchmark_card_next_action.py`
  - `scripts/test/check_cooperation_benchmark_card_next_action_witness.py`
  - `docs/COOPERATION_BENCHMARK_CARD_NEXT_ACTION.md`
  - `docs/COOPERATION_BENCHMARK_CARD_NEXT_ACTION_WITNESS.md`
- Tightened compact-card inheritor doctrine so the archive now distinguishes the preferred first command from the witness that selected it.
- Refreshed generated inventories / artifact summaries after threading the new surfaces into the compact-card stack.

### Research / inheritor insight

A fused compact-card control plane is already enough to answer what is current, citable, and repairable.
What it still does not answer cleanly is what an inheritor should do **first**.
The new next-action surface solves that, while the witness keeps the first-command layer honest by preserving whether the choice was uniquely forced or only the stable representative of a live tie set.

## Additional pass: compact-card taxonomy registry + drift gate

### What changed

- Added compact-card taxonomy surfaces:
  - `schemas/cooperation_benchmark_card_taxonomy.schema.json`
  - `scripts/report/build_cooperation_benchmark_card_taxonomy.py`
  - `scripts/test/check_cooperation_benchmark_card_taxonomy.py`
  - `docs/COOPERATION_BENCHMARK_CARD_TAXONOMY.md`
  - `artifacts/reports/cooperation_benchmark_card_taxonomy.json`
- Threaded the new taxonomy registry into:
  - `cooperation_benchmark_card_control_plane` report bindings / entrypoints, and
  - `cooperation_benchmark_card_handoff_pack` manifests / must-read paths / verify-refresh commands.
- Refreshed generated inventories / artifact summaries after the new schema, validator, report, and doc landed.

### Research / inheritor insight

Once compact-card governance grows into inventories, heads, review queues, citation surfaces, handoff packs, first-reentry selectors, and execution lanes, the archive is already depending on a lot of tiny stable strings.
If those identifiers stay scattered across builders and current reports, inheritors slowly learn semantics from session memory instead of from retained artifacts.
A small machine-readable taxonomy registry fixes that: it says which compact-card identifiers are stable, what they mean, where they appear, and which live surfaces are allowed to emit them.



## Additional pass: anti-vampire proxy scorecard + LLM-lane incentive contract

### What changed

- Extended `grlab certify` so memory-one pair certification now emits a compact `anti_vampire_scorecard` proxy with:
  - `own_payoff`,
  - `payoff_gap`,
  - canonical noisy-ecology `ecology_gap_noisy`,
  - explicit blocker codes for the still-pending `recovery_rounds` / `repair_abuse_rate` fields,
  - and tunable `--ecology-noise`, `--ecology-rounds`, `--ecology-reps` controls for the proxy lane.
- Added certify coverage for the new scorecard surface:
  - `grlab/tests/test_certify_solver.py`
  - `grlab/tests/test_certify_cli.py`
- Added one compact benchmark-publication note at `docs/LIBRARY/topics/cooperation_benchmark_llm_lanes_should_publish_incentive_instructions_and_payoff_scaling.md` so future inheritors do not mistake reward-framing or payoff-scale changes for policy-generalization progress.
- Tightened `docs/BENCHMARK_PROGRAM.md` with one new minimum-card row for LLM / agent-only incentive semantics and extended `docs/RESEARCH_SOURCES.md` with `RS-GR-128`..`RS-GR-130`.
- Refreshed `docs/COMMAND_INVENTORY.md`, `artifacts/reports/command_inventory.json`, `artifacts/reports/artifact_summary.json`, `docs/ARTIFACT_BUCKETS.md`, and `artifacts/reports/artifact_bucket_inventory.json` after the new certify flags landed.

### Research / inheritor insight

The old anti-vampire gap was no longer just philosophical: pairwise payoff math alone could still bless an extractive strategy whenever the focal side happened to be the extractor.
The noisy-ecology field fixes that for the current memory-one proxy lane. On the live command, canonical extortion still looks strong against an always-cooperator dyad, but it now fails the ecology screen (`ecology_gap_noisy ≈ +0.5335`), while canonical generous TFT clears the same ecology screen (`ecology_gap_noisy ≈ -0.3353`).

That same lesson generalizes to benchmark publication: in LLM / agent-only lanes, the incentive instruction and payoff scale are not harmless wrapper text. If reward wording or stake scaling changes, the card should publish that contract explicitly instead of laundering it into a headline cooperation comparison.

### Current local checks

- `python3 -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli` ✅
- `make update-command-inventory` ✅
- `make test-command-inventory` ✅
- `make test-research-docs` ✅
- `make test-generated-docs` ✅
- `make update-artifact-buckets` / `make test-artifact-buckets` ✅
- `make test-doc-links` still reports the standing pre-existing `/workspace/...` link failures and two legacy `h` anchor misses; this pass did not introduce a new docs-link break.

## Additional pass: declared anti-vampire screening spec + certify provenance

### What changed

- Added a first-class screening-spec contract for the current anti-vampire memory-one lane:
  - `schemas/certify_memory_one_screening_spec.schema.json`
  - `examples/certify/canonical_proxy_v1.json`
- Extended `grlab certify` so the result now carries `screening_spec_ref` provenance and the scorecard logs the declared `shock_protocol` instead of forcing future sessions to recover those settings from module constants.
- Added `--screening-spec` to the CLI so future inheritors can tighten or relax the proxy lane declaratively; `--ecology-noise`, `--ecology-rounds`, and `--ecology-reps` now act as explicit overrides on top of that declared spec rather than as the only source of semantics.
- Refreshed the anti-vampire doctrine/status surfaces in:
  - `docs/LIBRARY/topics/anti_vampire_scorecard_spec.md`
  - `docs/BUCKET.md`
  - `CHANGELOG.md`
- Refreshed the compact formal certify invariant lane at `scripts/formal/check_certify_invariants.py` and `artifacts/formal/certify_invariants.json` so the retained invariant artifact now matches the post-fallback certify semantics.
- Refreshed generated inventories / summaries after the new schema and CLI flag landed:
  - `docs/COMMAND_INVENTORY.md`
  - `artifacts/reports/command_inventory.json`
  - `docs/SCHEMA_INVENTORY.md`
  - `artifacts/reports/schema_inventory.json`
  - `docs/ARTIFACT_BUCKETS.md`
  - `artifacts/reports/artifact_bucket_inventory.json`
  - `artifacts/reports/artifact_summary.json`

### Research / inheritor insight

The earlier scorecard work made the gate machine-checkable, but not yet fully *declared*.
If the canonical ecology pool, recovery horizon, fallback depth, or threshold band lived only in Python constants, the archive could still cite a result without citing the contract that made the result true.
The new screening-spec lane fixes that compactly: future sessions can now rerun, compare, or intentionally replace the proxy contract by editing one small schema-backed spec instead of patching code.

That sounds administrative, but it changes the scientific object.
On the live command, `AlwaysC` vs extortion still fails under `canonical_proxy_v1`, yet a deliberately lenient demo spec can flip the same pair to `gate_pass = true` without any strategy-code change.
That is exactly the point the archive needed to make explicit: in proxy lanes, the gate is partly a property of the declared contract, not only of the strategy pair.

### Current local checks

- `python3 -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli grlab.tests.test_certify_schema` ✅
- `make update-command-inventory update-schema-inventory update-artifact-buckets report-artifact-summary` ✅
- `make test-command-inventory test-schema-inventory test-artifact-buckets test-reports-json test-generated-docs` ✅
- `python3 scripts/formal/check_certify_invariants.py` ✅
- live certify spot checks:
  - `AlwaysC` vs extortion under `canonical_proxy_v1` still fails for pairwise fairness,
  - extortion vs `AlwaysC` still fails for noisy ecology extraction,
  - and the same `AlwaysC` vs extortion pair can be made to pass under a deliberately lenient custom spec, which is now surfaced as `screening_spec_ref = lenient_demo` rather than hidden state.


## Additional pass: certify stage-game ref + explicit state order

### What changed

- Extended `grlab certify` so the top-level result now declares:
  - `stage_game_ref` with a stable `stage_game_id` plus immutable `stage_game_fingerprint_sha256`,
  - and explicit `state_order = ["CC", "CD", "DC", "DD"]` for the steady-state / payoff basis.
- Tightened `pairing_ref.pairing_fingerprint_sha256` so the ordered certify-object identity now depends on the declared stage-game contract in addition to the ordered strategy pair and effective screening spec.
- Added stage-game/state-order coverage in:
  - `grlab/tests/test_certify_solver.py`
  - `grlab/tests/test_certify_cli.py`
  - `grlab/tests/test_certify_schema.py`
- Updated the anti-vampire doctrine / backlog surfaces in:
  - `docs/LIBRARY/topics/anti_vampire_scorecard_spec.md`
  - `docs/BUCKET.md`
  - `CHANGELOG.md`

### Research / inheritor insight

The previous provenance passes fixed two silent comparison failures: hidden screening-contract drift and hidden strategy-payload drift.
This pass fixes the next one.
A future session could keep the same strategies and the same screening contract while changing the underlying stage-game payoffs or simply misreading which steady-state coordinate means `CC` versus `CD`.
Without a declared stage-game identity and explicit state order, the certify numbers would still be typed JSON but not yet a sufficiently declared scientific object.

The new payload keeps that surface compact.
Future comparisons should treat a certify result as living under three compact declared identities at once:
1. the effective screening contract,
2. the concrete ordered strategy pair,
3. the declared stage-game / state-order basis that made the reported payoffs and occupancies true.

### Current local checks

- `python3 -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli grlab.tests.test_certify_schema` ✅
## 2026-03-21 - rev0396

- Refreshed the live archive-size control receipt stack so the package / hotspot / semantic-handle / candidate / gap / manifest / rehearsal / stage surfaces now describe the current non-empty reports frontier honestly instead of inheriting a stale terminal-empty assumption.
- Added one compact durable handle note at `docs/LIBRARY/topics/cooperation_benchmark_compact_card_scope_and_taxonomy_reports_should_be_citable_governance_handles.md`, which makes `cooperation_benchmark_card_scope_surface` and `cooperation_benchmark_card_taxonomy` citation-ready for a future trim pass without retaining new bulky artifacts.
- Updated the archive-size receipt validators so live-frontier receipts are checked for internal consistency and alignment, while the older execution receipt is treated as a historical proof rather than forced to replay against a later tree.



## 2026-03-21 - rev0411

- Added two compact source-backed handoff notes tightening the next institution tranche:
  - `docs/LIBRARY/topics/partner_choice_can_reward_observable_reciprocity_while_eroding_hidden_care.md`
  - `docs/LIBRARY/topics/private_reputation_worlds_need_an_explicit_assessment_update_rule.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-134` (partner choice can increase visible reciprocity while decreasing hidden partner-maintenance help), and
  - `RS-GR-135` (private-reputation cooperation depends materially on the image-update rule).
- Threaded those constraints into the active planning / inheritor surfaces in:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `artifacts/process/2026-03-21-research-pass.md`

### Research / inheritor insight

The next tranche after leave/rematch should not score "cooperation" as one undifferentiated number.
Partner choice can reward being *seen* to help while weakening quieter forms of partner maintenance, and private reputation can change meaningfully when only the update rule changes.
So the future world contract should separate observed help from hidden care and should publish the reputation update rule explicitly.

### Current local checks

- `python3 scripts/test/check_research_docs.py` ✅
- `python3 scripts/test/check_docs_index_core.py` ✅


## 2026-03-21 - rev0412

- Added two compact source-backed handoff notes tightening the first reputation tranche:
  - `docs/LIBRARY/topics/reputation_fading_is_not_the_same_as_incomplete_observation.md`
  - `docs/LIBRARY/topics/gossip_rules_are_institutional_dials_not_background_plumbing.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-136` (sparse observation and fading / `Unknown` reputations are different institutions), and
  - `RS-GR-137` (private-reputation cooperation can depend materially on gossip cadence, fan-in, and trust weighting).
- Added one compact receipt at `artifacts/process/reputation_world_contract_gap_receipt_20260321.json`.
- Threaded those constraints into the active planning / inheritor surfaces in:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `artifacts/process/2026-03-21-research-pass.md`

### Research / inheritor insight

The next reputation tranche should not collapse all imperfect-information worlds into one noisy-reputation lane.
Sparse observation, fading / `Unknown` reputations, and gossip-mediated belief diffusion each change cooperation differently.
So the first implementor-facing reputation world should keep those as compact declared knobs before broadening search.

### Current local checks

- `python3 scripts/test/check_research_docs.py` ✅
- `python3 scripts/test/check_docs_index_core.py` ✅


## 2026-03-21 - rev0413

- Added two compact source-backed handoff notes tightening the next rehabilitation / repair tranche:
  - `docs/LIBRARY/topics/apology_and_reintegration_channels_are_institutional_dials_not_soft_fluff.md`
  - `docs/LIBRARY/topics/repair_signals_are_error_correction_channels_not_just_style.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-138` (apology availability / trackability can change reintegration after exclusion),
  - `RS-GR-139` (apology opportunities can raise cooperation and public/common-knowledge apologies matter at the group level), and
  - `RS-GR-140` (expressive signals can act as error-correction channels in indirect reciprocity).
- Added one compact receipt at `artifacts/process/repair_signal_world_contract_gap_receipt_20260321.json`.
- Threaded those constraints into the active planning / inheritor surfaces in:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `artifacts/process/2026-03-21-research-pass.md`

### Research / inheritor insight

The next institution tranche should not treat punishment as the whole story once exclusion or repair is live.
Apology visibility, trackability, re-entry conditions, and expressive error-correction channels can each change whether cooperation recovers after a breakdown.
So future sanction / repair worlds should publish a compact rehabilitation contract and keep a no-signal comparison before claiming a reciprocity breakthrough.

### Current local checks

- `python3 scripts/test/check_research_docs.py` ✅
- `python3 scripts/test/check_docs_index_core.py` ✅

## 2026-03-21 - rev0414

- Added two compact source-backed handoff notes tightening the next reputation / bounded-memory tranche:
  - `docs/LIBRARY/topics/reputation_granularity_is_a_world_contract_not_just_score_resolution.md`
  - `docs/LIBRARY/topics/record_expiry_and_visible_rehabilitation_countdowns_are_institutional_dials.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-141` (graded / ternary reputation states can change cooperation and recovery dynamics), and
  - `RS-GR-142` (bounded-memory record expiry and visible proximity to rehabilitation can unravel temporary exclusion).
- Added one compact receipt at `artifacts/process/reputation_granularity_and_record_expiry_receipt_20260321.json`.
- Threaded those constraints into the active planning / inheritor surfaces in:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `artifacts/process/2026-03-21-research-pass.md`

### Research / inheritor insight

The next reputation tranche should not hide two more institutional dials:
1. whether reputation is binary or graded,
2. and whether bad-record expiry / rehabilitation timing is visible enough to be gamed.

Those choices shape forgiveness, deterrence, and exclusion credibility.
So future worlds should publish reputation granularity and rehabilitation-countdown semantics explicitly before claiming robustness.

### Current local checks

- `python3 scripts/test/check_research_docs.py` ✅
- `python3 scripts/test/check_docs_index_core.py` ✅

## 2026-03-21 - rev0415

- Added two compact source-backed handoff notes tightening the first hybrid reciprocity / hybrid reputation tranche:
  - `docs/LIBRARY/topics/hybrid_reputation_worlds_need_explicit_agent_type_assessment_contracts.md`
  - `docs/LIBRARY/topics/reputation_scope_must_say_whether_failures_attach_to_agents_families_or_all_ais.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-143` (artificial agents can alter reputation consensus and mitigate punishment dilemmas in hybrid reciprocity),
  - `RS-GR-144` (one AI's moral failure can spill over to perceptions of all AIs), and
  - `RS-GR-145` (reputation-based reciprocity can weaken in human–bot networks and alter judgments about helping bots).
- Added one compact receipt at `artifacts/process/hybrid_reputation_scope_receipt_20260321.json`.
- Threaded those constraints into the active planning / inheritor surfaces in:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `artifacts/process/2026-03-21-research-pass.md`

### Research / inheritor insight

The next hybrid tranche should not hide two more institutional dials:
1. whether humans and artificial agents are judged by the same assessment rule,
2. and whether failures stick to one agent or spill over to a whole AI class.

Those choices shape consensus, stigma, and trust repair.
So future hybrid worlds should publish agent-type assessment symmetry and reputation scope explicitly before claiming reciprocity robustness.

### Current local checks

- `python3 scripts/test/check_research_docs.py` ✅
- `python3 scripts/test/check_docs_index_core.py` ✅


## 2026-03-21 - rev0416

- Added two compact source-backed handoff notes tightening the next group-structured reciprocity tranche:
  - `docs/LIBRARY/topics/collective_reputation_and_stereotype_scope_are_world_contracts_not_just_cognitive_shortcuts.md`
  - `docs/LIBRARY/topics/universalistic_cooperation_across_group_boundaries_depends_on_competition_and_mobility_contracts.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-146` (collective-reputation criteria can change cooperation in group-structured indirect reciprocity),
  - `RS-GR-147` (stereotype fallback can help or hurt cooperation depending on information sharing and can become sticky),
  - `RS-GR-148` (universalistic cooperation can lose reputational reward under intergroup competition), and
  - `RS-GR-149` (limited cross-boundary mobility can let a minority enforce intergroup cooperation).
- Added one compact receipt at `artifacts/process/group_boundary_and_collective_reputation_receipt_20260321.json`.
- Threaded those constraints into the active planning / inheritor surfaces in:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `artifacts/process/2026-03-21-research-pass.md`

### Research / inheritor insight

The next group-structured tranche should not hide two more institutional dials:
1. whether reputation is individual, collective, or stereotype-enabled,
2. and whether universalistic cooperation is being judged inside competitive or mobile group boundaries.

Those choices shape blame, parochialism, and the enforceability of broader cooperation.
So future worlds should publish collective-reputation scope and cross-boundary competition / mobility semantics explicitly before claiming Golden-Rule-like generality.

### Current local checks

- `python3 scripts/test/check_research_docs.py` ✅
- `python3 scripts/test/check_docs_index_core.py` ✅

## 2026-03-21 - rev0417

- Added two compact source-backed handoff notes tightening the next reputation-governance tranche:
  - `docs/LIBRARY/topics/reputation_governance_topology_is_a_world_contract_not_just_an_implementation_choice.md`
  - `docs/LIBRARY/topics/centralized_social_credit_style_scores_are_not_innocent_reputation_baselines.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-150` (opinion synchronization / consensus correlation is critical for indirect reciprocity),
  - `RS-GR-151` (public-heavy source weighting can drive polarization and fragmentation), and
  - `RS-GR-152` (centralized social-credit-style scores can reduce trust and cooperation and harden bias).
- Added one compact receipt at `artifacts/process/reputation_governance_topology_receipt_20260321.json`.
- Threaded those constraints into the active planning / inheritor surfaces in:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `artifacts/process/2026-03-21-research-pass.md`

### Research / inheritor insight

The next reputation-governance tranche should not hide two more institutional dials:
1. whether reputation is mostly private, synchronized, or centrally assigned,
2. and whether direct interaction can override a centralized score quickly enough for trust repair to be real.

Those choices shape consensus, polarization, and the reversibility of exclusion.
So future worlds should publish synchronization topology and centralized-score override / repair semantics explicitly before claiming reputation robustness.

### Current local checks

- `python3 scripts/test/check_research_docs.py` ✅
- `python3 scripts/test/check_docs_index_core.py` ✅



## 2026-03-21 - rev0418

- Added two compact source-backed handoff notes tightening the next monitoring / help-evaluation tranche:
  - `docs/LIBRARY/topics/monitoring_and_evidence_transfer_costs_are_world_contracts_not_background_friction.md`
  - `docs/LIBRARY/topics/helping_worlds_should_separate_unwillingness_inability_and_need_burden.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-153` (trust can function as reduced monitoring under costly observation),
  - `RS-GR-154` (competition and transfer costs reduce information sharing needed for reputation),
  - `RS-GR-155` (partner choice depends on both willingness / warmth and ability / competence, modulated by task affordances), and
  - `RS-GR-156` (misfortune and help-seeking can trigger blame as a way to avoid costly helping).
- Added one compact receipt at `artifacts/process/monitoring_and_help_evaluation_receipt_20260321.json`.
- Threaded those constraints into the active planning / inheritor surfaces in:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `artifacts/process/2026-03-21-research-pass.md`

### Research / inheritor insight

The next trust/help tranche should not hide two more institutional dials:
1. whether observation and evidence transfer are cheap enough to sustain dense monitoring and reputation,
2. and whether non-help / help-seeking are evaluated with separate willingness, ability, and burden semantics.

Those choices shape apparent trust, blame, exclusion, and the meaning of "good partner" itself.
So future worlds should publish monitoring-economics and help-evaluation semantics explicitly before claiming Golden-Rule-like robustness.

### Current local checks

- `python3 scripts/test/check_research_docs.py` ✅
- `python3 scripts/test/check_docs_index_core.py` ✅


## 2026-03-21 - rev0419

- Added two compact source-backed handoff notes tightening the next identity-policy tranche:
  - `docs/LIBRARY/topics/identity_persistence_and_reputation_reset_cost_are_world_contracts_not_account_hygiene.md`
  - `docs/LIBRARY/topics/actor_identifiability_and_action_visibility_should_be_separate_world_fields.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-157` (cheap identity reset lowers trust and trustworthiness in reputation systems),
  - `RS-GR-158` (whitewashing remains a standard trust-attack class in open dynamic trust systems),
  - `RS-GR-159` (revealing who is present can reduce cooperation even when actions stay private), and
  - `RS-GR-160` (identity cues can modulate the effect of the same reputation signal).
- Added one compact receipt at `artifacts/process/identity_policy_contracts_receipt_20260321.json`.
- Threaded those constraints into the active planning / inheritor surfaces in:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `artifacts/process/2026-03-21-research-pass.md`

### Research / inheritor insight

The next identity-policy tranche should publish two things that are easy to hide:
1. whether agents can cheaply shed history and re-enter as apparently new,
2. and whether the world reveals who someone is separately from what they did.

Otherwise a benchmark can look more forgiving, more suspicious, or more transparent because bad actors were allowed to whitewash, newcomers were penalized by design, or identity labels changed behavior even when action evidence did not.

### Current local checks

- `python3 scripts/test/check_research_docs.py` ✅
- `python3 scripts/test/check_docs_index_core.py` ✅



## 2026-03-21 - rev0420

- Added two compact source-backed handoff notes tightening the next inequality / scarcity-governance tranche:
  - `docs/LIBRARY/topics/inequality_source_and_capability_alignment_are_world_contracts_not_just_initial_conditions.md`
  - `docs/LIBRARY/topics/scarce_allocation_rules_and_planner_authority_are_world_contracts_not_posthoc_accounting.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-161` (cooperation under asymmetry depends on endowment, productivity, and return structure),
  - `RS-GR-162` (merit-framed versus luck-framed inequality changes fairness perceptions and cooperation),
  - `RS-GR-163` (limited-goods allocation jointly reflects merit, need, and equality),
  - `RS-GR-164` (planner allocation policy can sustain cooperation by conditioning generosity and sanctioning defectors), and
  - `RS-GR-165` (third-party allocators can improve efficiency, but inequality creates fairness conflicts that weaken them).
- Added one compact receipt at `artifacts/process/inequality_and_scarcity_contracts_receipt_20260321.json`.
- Threaded those constraints into the active planning / inheritor surfaces in:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `artifacts/process/2026-03-21-research-pass.md`

### Research / inheritor insight

The next inequality / scarcity tranche should publish two things that are easy to hide:
1. whether unequal positions reflect luck, merit, productivity, endowment, or aligned combinations,
2. and whether scarce goods are divided automatically, by peers, or by a planner / allocator using equality, need, merit, or reciprocity history.

Otherwise a benchmark can look more generous, more selfish, or more stable because merit framing changed fairness norms or because an allocation mechanism quietly did the cooperative work.

### Current local checks

- `python3 scripts/test/check_research_docs.py` ✅
- `python3 scripts/test/check_docs_index_core.py` ✅

## rev0421 - 2026-03-22

- added compact Golden Rule research notes on punishment metanorms and sanctioner-governance / oversight contracts
- extended the research source ledger through `RS-GR-171` and threaded the new sanction-governance constraints into the agenda, opinions, inheritor brief, and process pass
- added a compact receipt for the new tranche at `artifacts/process/sanction_governance_receipt_20260321.json`



## rev0422 - 2026-03-22

- added compact Golden Rule research notes on commitment-stage / breach-scoring contracts and cheap post-hoc self-signaling contracts
- extended the research source ledger through `RS-GR-175` and threaded the new speech-act-governance constraints into the agenda, opinions, inheritor brief, and process pass
- added a compact receipt for the new tranche at `artifacts/process/speech_act_governance_receipt_20260321.json`

## rev0426 - 2026-03-22

- added compact Golden Rule research notes on help-versus-harm / gain-loss sign-structure contracts and collective-harm-latency / threshold-semantics contracts
- extended the research source ledger through `RS-GR-190` and threaded the new harm-accounting constraints into the agenda, opinions, inheritor brief, and process pass
- added a compact receipt for the new tranche at `artifacts/process/harm_accounting_and_collective_damage_receipt_20260322.json`

## rev0427 - 2026-03-22

- added compact Golden Rule research notes on triadic small-group structure and on delegated coordination / coalition-stage / representative-selection contracts
- extended the research source ledger through `RS-GR-194` and threaded the new small-group / delegation constraints into the agenda, opinions, inheritor brief, and process pass
- added a compact receipt for the new tranche at `artifacts/process/triadic_and_delegated_coordination_receipt_20260322.json`
## rev0428 - 2026-03-22

- added compact Golden Rule research notes on private-solution / self-reliance contracts and on outside-option semantics / loner-externality contracts
- extended the research source ledger through `RS-GR-198` and threaded the new private-solution / outside-option constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/private_solution_and_outside_option_contracts_receipt_20260322.json`

## rev0429 - 2026-03-22

- added compact Golden Rule research notes on need-revelation / ask-stage contracts and request-visibility / request-recognition contracts
- extended the research source ledger through `RS-GR-202` and threaded the new helping-request constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/need_revelation_and_request_visibility_receipt_20260322.json`


## rev0430 - 2026-03-22

- added compact Golden Rule research notes on endogenous rule-choice / democratic-selection contracts and franchise-scope / binding-scope contracts
- extended the research source ledger through `RS-GR-206` and threaded the new institution-choice constraints into the agenda, opinions, inheritor brief, and process pass
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
- local validation target for this pass: research docs, docs index core, claim register, reports-json validity, and markdown-link advisory scan
- restored 23 missing referenced `artifacts/reports/rematch_proxy_*_20260306.*` paths as explicit retained-path placeholders to repair inherited risk/spec linkage without recreating bulky historical snapshots

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
- local validation target for this pass: research docs, docs index core, claim register, reports-json validity, risk register, artifact layout, policy expirations, artifact gitkeeps, and markdown-link advisory scan
- repaired inherited absolute `/workspace/...` markdown links across the root README and core docs so markdown-link validation now fails only on the standing formula-parser false positives around `K_[a,b](h)`


## rev0447 - 2026-03-22

- added compact Golden Rule research notes on independent-verification / public-contestability contracts and on future-steward knowledge-package / renewable-records contracts
- extended the research source ledger through `RS-GR-312` and threaded the new verification / renewable-handoff constraints into the agenda, opinions, inheritor brief, and process pass
- added compact receipt `artifacts/process/verification_contestability_and_renewable_handoff_receipt_20260322.json`
- local validation target for this pass: research docs, docs index core, claim register, reports-json validity, risk register, artifact layout, policy expirations, artifact gitkeeps, and markdown-link advisory scan
- repaired inherited markdown-link false positives by teaching `scripts/test/check_markdown_links.py` to ignore fenced and inline code spans before scanning for links


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

## Additional pass: content-addressed successor-safe ceremony receipt locator

- Added one compact content-addressed locator discipline for successor-safe ceremony receipts so downstream notes can cite a stable digest instead of re-copying receipt bodies:
  - `schemas/successor_safe_ceremony_receipt_locator.schema.json`
  - `examples/snapshots/successor_safe_ceremony_receipt_example.locator.json`
  - `docs/LIBRARY/topics/content_addressed_successor_safe_ceremony_receipt_locators_keep_archive_handoffs_small_and_stable.md`
  - `artifacts/process/successor_safe_ceremony_receipt_locator_receipt_20260322.json`
- Extended `scripts/tools/successor_safe_ceremony_receipt.py` with deterministic restricted-canonicalization + SHA-256 locator emission and updated `scripts/test/check_successor_safe_ceremony_receipt.py` to validate the receipt tool against both receipt and locator schemas plus the worked snapshots.
- Extended the research source ledger through `RS-GR-510` and threaded the new canonicalization / hash-named-locator move into the inheritor brief and research agenda.
- Main practical result: the archive can now keep one machine-checkable ceremony receipt *and* one tiny stable locator (`sha256` hex + `ni:///sha-256;...`) so future derived notes can stay citation-first even when the same ceremony contract is referenced many times.
- Local validation on this pass:
  - `python3 scripts/test/check_successor_safe_ceremony_receipt.py`
  - `python3 scripts/report/build_schema_inventory.py --write`
  - `python3 scripts/report/build_artifact_bucket_inventory.py --write`
  - `python3 scripts/report/build_validator_inventory.py --write`
  - `python3 scripts/report/build_command_inventory.py --write`
  - `python3 scripts/test/check_schema_json_valid.py`
  - `python3 scripts/test/check_scripts_compile.py`
  - `python3 scripts/test/check_research_docs.py`
  - `python3 scripts/test/check_docs_index_core.py`
  - `python3 scripts/test/check_markdown_links.py`
  - `python3 scripts/test/check_generated_docs_presence.py`
  - `python3 -m unittest tests.control.test_repo_controls`
  - `python3 -m pytest -q grlab/tests/test_certify_cli.py grlab/tests/test_certify_schema.py`
  - `make test-successor-safe-ceremony-receipt`
  - `bash ./scripts/doctor.sh` and `bash ./scripts/test/run_harness.sh quick` still stop at the missing `cargo` / `junest` Rust lane

## Additional pass: fail-closed successor-safe ceremony receipt assessment

- Added one compact fail-closed assessment discipline for successor-safe ceremony receipts so inheritors can tell “schema-valid but weak” from “successor-ready” without re-reading protocol prose:
  - `schemas/successor_safe_ceremony_receipt_assessment.schema.json`
  - `examples/snapshots/successor_safe_ceremony_receipt_example.assessment.json`
  - `docs/LIBRARY/topics/structurally_valid_successor_safe_ceremony_receipts_should_also_ship_a_fail_closed_assessment_report.md`
  - `artifacts/process/successor_safe_ceremony_receipt_assessment_receipt_20260322.json`
- Extended `scripts/tools/successor_safe_ceremony_receipt.py` with an `assess` subcommand that emits a tiny machine-checkable report over placeholder language, verifier / audience binding, session / replay binding, by-reference request-integrity posture, `direct_post` session mapping, cross-device participation evidence, dispatch assurance, trusted renderer naming, and digest-bearing retained-evidence references.
- Updated `scripts/test/check_successor_safe_ceremony_receipt.py` so the worked example must stay green while scaffolded placeholder receipts fail closed under the assessment lane.
- Extended `docs/RESEARCH_SOURCES.md` through `RS-GR-513` and threaded the new assessment discipline into `docs/RESEARCH_AGENDA.md`, `docs/RESEARCH_OPINIONS.md`, and `docs/BUCKET.md`.
- Main practical result: the archive now keeps one small receipt, one stable locator, and one tiny adequacy verdict, so downstream notes can cite not just *what* ceremony contract was preserved but also whether that preserved contract is already good enough for inheritor handoff.

## Additional pass: successor-safe ceremony receipt archive dispositions

- Added one compact archive-disposition discipline for successor-safe ceremony receipts so inheritors can tell not just whether a receipt is weak, but what the archive should now do with it:
  - `schemas/successor_safe_ceremony_receipt_disposition.schema.json`
  - `examples/snapshots/successor_safe_ceremony_receipt_example.disposition.json`
  - `docs/LIBRARY/topics/successor_safe_ceremony_receipt_assessments_should_collapse_to_explicit_archive_dispositions.md`
  - `artifacts/process/successor_safe_ceremony_receipt_disposition_receipt_20260322.json`
- Extended `scripts/tools/successor_safe_ceremony_receipt.py` with a `disposition` subcommand that collapses a receipt assessment plus locator into explicit archive handling guidance: claim-ready citable, provisional locator-only, or hold for remediation; plus residual-risk response, open finding codes, required actions, and a review trigger.
- Updated `scripts/test/check_successor_safe_ceremony_receipt.py` so the worked example disposition must stay green and scaffolded placeholder receipts must disposition to `hold_for_remediation`.
- Extended `docs/RESEARCH_SOURCES.md` through `RS-GR-515` and threaded the new disposition discipline into `docs/RESEARCH_AGENDA.md`, `docs/RESEARCH_OPINIONS.md`, `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`, and `docs/BUCKET.md`.
- Main practical result: the archive now keeps one small receipt, one stable locator, one adequacy assessment, and one tiny handling decision, so future sessions inherit not just protocol facts and warnings but also the intended custody of residual risk.
- Local validation on this pass:
  - `python3 scripts/test/check_successor_safe_ceremony_receipt.py`
  - `python3 scripts/report/build_schema_inventory.py --write`
  - `python3 scripts/report/build_artifact_bucket_inventory.py --write`
  - `python3 scripts/report/build_validator_inventory.py --write`
  - `python3 scripts/report/build_command_inventory.py --write`
  - `python3 scripts/test/check_schema_json_valid.py`
  - `python3 scripts/test/check_scripts_compile.py`
  - `python3 scripts/test/check_research_docs.py`
  - `python3 scripts/test/check_docs_index_core.py`
  - `python3 scripts/test/check_markdown_links.py`
  - `python3 scripts/test/check_generated_docs_presence.py`
  - `python3 -m unittest tests.control.test_repo_controls`
  - `python3 -m pytest -q grlab/tests/test_certify_cli.py grlab/tests/test_certify_schema.py`
  - `make test-successor-safe-ceremony-receipt`
  - `bash ./scripts/doctor.sh` still fails only on missing `cargo` / `junest`
  - `bash ./scripts/test/run_harness.sh quick` still stops at `rust_exec: junest not found`

## Additional pass: successor-safe ceremony receipt remediation plans

- Added one compact remediation-plan discipline for successor-safe ceremony receipts so inheritors can see exactly how a warned or failed receipt becomes claim-ready again:
  - `schemas/successor_safe_ceremony_receipt_remediation_plan.schema.json`
  - `examples/snapshots/successor_safe_ceremony_receipt_example.remediation.json`
  - `docs/LIBRARY/topics/successor_safe_ceremony_receipt_dispositions_should_collapse_further_to_compact_remediation_plans.md`
  - `artifacts/process/successor_safe_ceremony_receipt_remediation_receipt_20260322.json`
- Extended `scripts/tools/successor_safe_ceremony_receipt.py` with a `remediation` subcommand that turns an assessment + locator + disposition into a tiny closure-oriented plan with blocking/warning work items, evidence paths, acceptance tests, and a promotion gate.
- Updated `scripts/test/check_successor_safe_ceremony_receipt.py` so the worked example remediation plan must stay green while scaffolded placeholder receipts emit open blocking work items.
- Extended `docs/RESEARCH_SOURCES.md` through `RS-GR-517` and threaded the remediation discipline into `docs/RESEARCH_AGENDA.md`, `docs/RESEARCH_OPINIONS.md`, `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`, and `docs/BUCKET.md`.
- Main practical result: the archive now keeps one small receipt, one stable locator, one adequacy assessment, one custody disposition, and one tiny closure plan, so future sessions inherit not just protocol facts and risk labels but an explicit route back to claim-ready citation.

## Additional pass: successor-safe ceremony receipt citation advisories

- Added one compact downstream-handling discipline for successor-safe ceremony receipts so inheritors can tell whether previously claim-ready citations should stay live or be withdrawn after a review event:
  - `schemas/successor_safe_ceremony_receipt_citation_advisory.schema.json`
  - `examples/snapshots/successor_safe_ceremony_receipt_example.citation_advisory.json`
  - `docs/LIBRARY/topics/successor_safe_ceremony_receipt_review_verdicts_should_collapse_to_explicit_citation_advisories.md`
  - `artifacts/process/successor_safe_ceremony_receipt_citation_advisory_receipt_20260322.json`
- Extended `scripts/tools/successor_safe_ceremony_receipt.py` with an `advise` subcommand that collapses a review verdict into one downstream citation advisory carrying the reviewed locator, advisory decision, existing-citation action, new-citation action, and regeneration sequence only when citation must be withdrawn.
- Updated `scripts/test/check_successor_safe_ceremony_receipt.py` so the worked example advisory must stay green while triggered review verdicts must collapse to withdrawal-oriented advisory actions.
- Extended `docs/RESEARCH_SOURCES.md` through `RS-GR-527` and threaded the citation-advisory discipline into `docs/RESEARCH_AGENDA.md`, `docs/RESEARCH_OPINIONS.md`, `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`, `docs/BUCKET.md`, and `artifacts/process/2026-03-21-research-pass.md`.
- Main practical result: the archive now keeps one small receipt, one stable locator, one adequacy assessment, one custody disposition, one remediation plan, one authorization, one promotion record, one freshness watch, one review verdict, and one tiny downstream citation advisory, so future sessions inherit not just whether a package stayed green but what that means for old and new citations.

## Additional pass: successor-safe ceremony receipt package supersession records

- Added one compact replacement-target discipline for successor-safe ceremony receipt packages so inheritors can tell which refreshed package manifest superseded an earlier package root:
  - `schemas/successor_safe_ceremony_receipt_package_supersession.schema.json`
  - `examples/snapshots/successor_safe_ceremony_receipt_example.review_watch_refreshed.json`
  - `examples/snapshots/successor_safe_ceremony_receipt_example.review_verdict_refreshed.json`
  - `examples/snapshots/successor_safe_ceremony_receipt_example.citation_advisory_refreshed.json`
  - `examples/snapshots/successor_safe_ceremony_receipt_example.package_manifest_refreshed.json`
  - `examples/snapshots/successor_safe_ceremony_receipt_example.package_supersession.json`
  - `docs/LIBRARY/topics/successor_safe_ceremony_receipt_package_manifests_should_ship_compact_supersession_records.md`
  - `artifacts/process/successor_safe_ceremony_receipt_package_supersession_receipt_20260322.json`
- Extended `scripts/tools/successor_safe_ceremony_receipt.py` with a `supersede` subcommand that compares two package manifests plus their freshness-era artifacts and emits one explicit replacement record naming receipt-locator continuity, replaced component roles, supersession reason codes, and current authoritative-manifest guidance.
- Updated `scripts/test/check_successor_safe_ceremony_receipt.py` so the worked example must keep both the original and refreshed package-manifest lane green while the committed package-supersession snapshot stays derivable from the tool rather than hand-edited.
- Extended `docs/RESEARCH_SOURCES.md` through `RS-GR-533` and threaded the package-supersession discipline into `docs/RESEARCH_AGENDA.md`, `docs/RESEARCH_OPINIONS.md`, `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`, and `docs/BUCKET.md`.
- Main practical result: the archive now keeps not just the current package root, but also one explicit map from a prior package manifest to its authoritative replacement, so future sessions can retire old package roots without guessing which refreshed manifest took over.



## Additional pass: successor-safe ceremony receipt package lineage records

- Added one compact authoritative-chain discipline for successor-safe ceremony receipt packages so inheritors can tell which package manifest is authoritative after more than one package state exists:
  - `schemas/successor_safe_ceremony_receipt_package_lineage.schema.json`
  - `examples/snapshots/successor_safe_ceremony_receipt_example.package_lineage.json`
  - `docs/LIBRARY/topics/successor_safe_ceremony_receipt_package_supersession_records_should_collapse_to_compact_lineage_records.md`
  - `artifacts/process/successor_safe_ceremony_receipt_package_lineage_receipt_20260322.json`
- Extended `scripts/tools/successor_safe_ceremony_receipt.py` with a `lineage` subcommand that compares an ordered set of package manifests plus their supersession records and emits one explicit lineage object naming the authoritative head, manifest chain, supersession chain, locator continuity, and current authority basis.
- Updated `scripts/test/check_successor_safe_ceremony_receipt.py` so the worked example must keep the package-lineage snapshot derivable from the tool rather than hand-edited.
- Extended `docs/RESEARCH_SOURCES.md` through `RS-GR-536` and threaded the package-lineage discipline into `docs/RESEARCH_AGENDA.md`, `docs/RESEARCH_OPINIONS.md`, `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`, and `docs/BUCKET.md`.
- Main practical result: the archive now keeps not just a current package root and pairwise replacement records, but also one tiny object that says which package head is authoritative now and how authority flowed across prior package refreshes.


## Additional pass: successor-safe ceremony receipt package status cards

- Added one compact current-state discipline for successor-safe ceremony receipt packages so inheritors can answer whether the current package head remains safe to cite without opening multiple neighboring status files:
  - `schemas/successor_safe_ceremony_receipt_package_status_card.schema.json`
  - `examples/snapshots/successor_safe_ceremony_receipt_example.package_status_card.json`
  - refreshed `examples/snapshots/successor_safe_ceremony_receipt_example.package_head.json`
  - `docs/LIBRARY/topics/successor_safe_ceremony_receipt_package_heads_should_ship_compact_status_cards.md`
  - `artifacts/process/successor_safe_ceremony_receipt_package_status_card_receipt_20260322.json`
- Extended `scripts/tools/successor_safe_ceremony_receipt.py` with a `statuscard` subcommand that collapses the authoritative manifest, live review window, as-of review verdict, citation guidance, and current citable result into one explicit package-status-card object, and updated `head` so the registered `status` discovery link now targets that status card.
- Updated `scripts/test/check_successor_safe_ceremony_receipt.py` so the worked example must keep the package-status-card snapshot derivable from the tool and the refreshed package-head snapshot aligned with the status-card link target rather than hand-edited.
- Extended `docs/RESEARCH_SOURCES.md` through `RS-GR-542` and threaded the package-status-card discipline into `docs/RESEARCH_AGENDA.md`, `docs/RESEARCH_OPINIONS.md`, `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`, and `docs/BUCKET.md`.
- Main practical result: the archive now keeps not just a discoverable package head, but also one tiny live status object that answers whether the head is citable right now, when it must be revisited, and what sequence would regenerate it if freshness breaks.

## Additional pass: successor-safe ceremony receipt package redirects

- Added one compact redirect discipline for superseded successor-safe ceremony receipt packages so inheritors landing on an older package manifest can recover the preferred current package-reference target and live status without replaying lineage by hand:
  - `schemas/successor_safe_ceremony_receipt_package_redirect.schema.json`
  - `examples/snapshots/successor_safe_ceremony_receipt_example.package_redirect.json`
  - `docs/LIBRARY/topics/superseded_successor_safe_ceremony_receipt_packages_should_ship_compact_redirect_artifacts.md`
  - `artifacts/process/successor_safe_ceremony_receipt_package_redirect_receipt_20260322.json`
- Extended `scripts/tools/successor_safe_ceremony_receipt.py` with a `redirect` subcommand that starts from a superseded package manifest plus its supersession record and emits one explicit redirect object naming the preferred current package head, successor manifest, live status card, locator-level citation guidance, and registered link relations (`cite-as`, `successor-version`, `latest-version`, `status`, `describedby`).
- Updated `scripts/test/check_successor_safe_ceremony_receipt.py` so the worked example must keep the package-redirect snapshot derivable from the tool rather than hand-edited.
- Extended `docs/RESEARCH_SOURCES.md` through `RS-GR-545` and threaded the package-redirect discipline into `docs/RESEARCH_AGENDA.md`, `docs/RESEARCH_OPINIONS.md`, `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`, and `docs/BUCKET.md`.
- Main practical result: the archive now keeps not just the current package root and status, but also one tiny object that tells a future steward who lands on a superseded package exactly which live package reference target to prefer now and where its current status lives.


## Additional pass: successor-safe ceremony receipt package catalogs

- Added one compact archive-discovery discipline for successor-safe ceremony receipt packages so inheritors can discover the live package head for each retained family plus any superseded-package redirects from one machine-checkable object:
  - `schemas/successor_safe_ceremony_receipt_package_catalog.schema.json`
  - `examples/snapshots/successor_safe_ceremony_receipt_example.package_catalog.json`
  - `docs/LIBRARY/topics/successor_safe_ceremony_receipt_package_heads_and_redirects_should_collapse_to_compact_catalogs.md`
  - `artifacts/process/successor_safe_ceremony_receipt_package_catalog_receipt_20260322.json`
- Extended `scripts/tools/successor_safe_ceremony_receipt.py` with a `catalog` subcommand that starts from one or more current package heads plus any retained package redirects and emits one explicit catalog object naming the live package head, status card, authoritative manifest, lineage, and redirect inventory for each family.
- Updated `scripts/test/check_successor_safe_ceremony_receipt.py` so the worked example must keep the package-catalog snapshot derivable from the tool rather than hand-edited.
- Extended `docs/RESEARCH_SOURCES.md` through `RS-GR-548` and threaded the package-catalog discipline into `docs/RESEARCH_AGENDA.md`, `docs/RESEARCH_OPINIONS.md`, and `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`.
- Main practical result: the archive now keeps not just current package roots, status cards, and redirects, but also one tiny discovery index telling a future steward what successor-safe ceremony package families exist here and which live package head to open first for each one.

## Additional pass: successor-safe ceremony receipt package verification reports

- Added one compact verification-basis discipline for successor-safe ceremony receipt packages so future inheritors can see exactly which local checks ran against the current package and where the cloudtainer boundary stopped:
  - `schemas/successor_safe_ceremony_receipt_package_verification_report.schema.json`
  - `examples/snapshots/successor_safe_ceremony_receipt_example.package_verification_report.json`
  - `docs/LIBRARY/topics/successor_safe_ceremony_receipt_package_heads_should_ship_compact_verification_reports.md`
  - `artifacts/process/successor_safe_ceremony_receipt_package_verification_report_receipt_20260322.json`
- Extended `scripts/tools/successor_safe_ceremony_receipt.py` with a `verifyreport` subcommand that runs a compact local validation profile, records `pass` / `blocked` / `fail` results, and preserves the current Python-pass / Rust-blocked boundary in one machine-checkable object.
- Refreshed the worked package head, redirect, and catalog snapshots so the live package discovery surface now carries the verification-report reference forward.
- Main practical result: the archive now keeps not just what the live package is and whether it is citable, but also one tiny object saying what local verification basis actually backed that statement in this cloudtainer.



## Additional pass: successor-safe ceremony receipt package claim scopes

- Added one compact downstream-claim boundary for successor-safe ceremony receipt packages so future stewards inherit not just the verification report, but also one machine-checkable statement of what that local basis actually supports saying in this cloudtainer.
- Added `schemas/successor_safe_ceremony_receipt_package_claim_scope.schema.json`, `examples/snapshots/successor_safe_ceremony_receipt_example.package_claim_scope.json`, `docs/LIBRARY/topics/successor_safe_ceremony_receipt_package_verification_reports_should_ship_compact_claim_scope_artifacts.md`, and `artifacts/process/successor_safe_ceremony_receipt_package_claim_scope_receipt_20260322.json`.
- Extended `scripts/tools/successor_safe_ceremony_receipt.py` with `claimscope`, tightened `scripts/test/check_successor_safe_ceremony_receipt.py`, and refreshed the worked package head / redirect / catalog snapshots so the live discovery surface now carries the claim-scope reference forward.
- Main practical result: the archive now preserves one explicit non-runtime claim boundary for the current Python-pass / Rust-blocked package instead of leaving future inheritors to infer that boundary from raw verification results.


## Additional pass: successor-safe ceremony receipt package reliance cards

- Added one compact downstream-reliance boundary for successor-safe ceremony receipt packages so future stewards inherit not just the current status card, verification report, and claim scope, but also one machine-checkable statement of what they may safely rely on right now from that combined posture.
- Added `schemas/successor_safe_ceremony_receipt_package_reliance_card.schema.json`, `examples/snapshots/successor_safe_ceremony_receipt_example.package_reliance_card.json`, `docs/LIBRARY/topics/successor_safe_ceremony_receipt_package_claim_scopes_should_ship_compact_reliance_cards.md`, and `artifacts/process/successor_safe_ceremony_receipt_package_reliance_card_receipt_20260322.json`.
- Extended `scripts/tools/successor_safe_ceremony_receipt.py` with `reliancecard`, tightened `scripts/test/check_successor_safe_ceremony_receipt.py`, and refreshed the worked package head / redirect / catalog snapshots so the live discovery surface now carries the package-reliance-card reference forward.
- Main practical result: the archive now preserves one explicit reliance boundary for the current Python-pass / Rust-blocked package instead of leaving future inheritors to synthesize that boundary from three neighboring package artifacts.


## Additional pass: Rust restart-priority maps for blocked sessions

- Added one compact static restart map so future inheritors can see which Rust modules deserve first attention when the cloudtainer still lacks `cargo` / `rustc`, without preserving copied code slices.
- Added `scripts/report/build_rust_restart_map.py`, generated `docs/RUST_RESTART_MAP.md`, and emitted `artifacts/reports/rust_restart_map.json`.
- Added `make update-rust-restart-map` / `make test-rust-restart-map`, threaded them through `make cloudtainer-shadow-pass`, and updated `README.md`, `docs/README.md`, and `docs/ENVIRONMENT_SANDWORM.md`.
- Main practical result: Rust-blocked sessions now inherit not just a static module inventory, but also a restart order that distinguishes implementation hazards from inline-test-only hazards and points first to the modules with the densest dependency/test-anchor surface.


## Additional pass: Rust test scenario-coverage ledger for blocked sessions

- Added one compact static coverage-gap ledger so future inheritors can see not just which Rust modules and contracts exist, but which world/noise/termination/strategy/assertion variants are actually exercised by the current test corpus while `cargo` remains unavailable.
- Added `scripts/report/build_rust_test_scenario_coverage.py`, generated `docs/RUST_TEST_SCENARIO_COVERAGE.md`, and emitted `artifacts/reports/rust_test_scenario_coverage.json`.
- Added `make update-rust-test-scenario-coverage` / `make test-rust-test-scenario-coverage`, threaded them through `make cloudtainer-shadow-pass`, and updated `README.md`, `docs/README.md`, `docs/ENVIRONMENT_SANDWORM.md`, and `scripts/test/check_generated_docs_presence.py`.
- Main practical result: Rust-blocked sessions now inherit one compact attention queue showing unseen, inline-only, and sparse scenario variants so the eventual Rust-capable implementor can target the weakest semantic seams first.

## Additional pass: Rust external-test lift queue for blocked sessions

- Added one compact lift queue so future inheritors do not just inherit weak-scenario probe seeds, but also a first-pass answer for which external Rust test file each seed likely belongs in and how narrowly to lift it.
- Added `scripts/report/build_rust_external_test_queue.py`, generated `docs/RUST_EXTERNAL_TEST_QUEUE.md`, and emitted `artifacts/reports/rust_external_test_queue.json`.
- Added `make update-rust-external-test-queue` / `make test-rust-external-test-queue`, threaded them through `make cloudtainer-shadow-pass`, and updated `README.md`, `docs/README.md`, `docs/ENVIRONMENT_SANDWORM.md`, and `scripts/test/check_generated_docs_presence.py`.
- Main practical result: a later Rust-capable implementor now inherits a fixture-backed external-test comeback queue with target lanes, target files, suggested test names, and minimal implementation recipes instead of having to derive that plan again from the seed ledgers.

## Additional pass: Rust external-test patch rehearsal and equivalence repair

- Added one compact rehearsal lane so future inheritors can scratch-apply the monolithic external-test comeback patchset and the cumulative shard series against copied target files, then compare the resulting hashes instead of assuming those two apply paths are interchangeable.
- Added `scripts/report/build_rust_external_test_patch_rehearsal.py`, generated `docs/RUST_EXTERNAL_TEST_PATCH_REHEARSAL.md`, and emitted `artifacts/reports/rust_external_test_patch_rehearsal.json`.
- Found and fixed a real landing mismatch during this pass: the old monolithic patchset grouped helpers/tests into one block per target file while the shard series preserved per-seed blocks, so both paths applied but landed on different final file layouts. Updated `scripts/report/build_rust_external_test_patchset.py` so the monolithic patchset now preserves the same landing order and per-seed block markers as the shard series.
- Added `make update-rust-external-test-patch-rehearsal` / `make test-rust-external-test-patch-rehearsal`, threaded them through `make cloudtainer-shadow-pass`, and refreshed the README/docs/command-inventory surface around the new rehearsal lane.
- Main practical result: the archive now preserves an explicit proof that the one-shot patchset and the 10-shard landing series converge on the same final `probe_run.rs` / `metamorphic_suite.rs` edits, which makes the comeback handoff meaningfully safer for the eventual Rust-capable implementor.

## Additional pass: cloudtainer shadow-pass receipt history

- Added one compact receipt-history lane so future inheritors can see not just the latest blocked-session frontier, but how the shadow pass widened across revisions and how stable the main budget cutpoints remain across completed receipts.
- Added `scripts/report/build_cloudtainer_shadow_pass_history.py`, generated `docs/CLOUDTAINER_SHADOW_PASS_HISTORY.md`, emitted `artifacts/reports/cloudtainer_shadow_pass_history.json`, and added `make update-cloudtainer-shadow-pass-history` / `make test-cloudtainer-shadow-pass-history`.
- Threaded the new history lane through `make cloudtainer-shadow-pass` and refreshed the README/docs/generated-doc surfaces around the report.
- Main practical result: the archive now preserves one longitudinal answer to “how expensive and stable is the blocked-session shadow pass?” instead of only a single latest-receipt snapshot.


## Additional pass: cloudtainer shadow-pass volatility map

- Added one compact step/lane volatility report so future inheritors can tell which shadow-pass timings are trustworthy anchors versus soft estimates before budgeting around the latest frontier cutpoints.
- Added `scripts/report/build_cloudtainer_shadow_pass_volatility.py`, generated `docs/CLOUDTAINER_SHADOW_PASS_VOLATILITY.md`, and emitted `artifacts/reports/cloudtainer_shadow_pass_volatility.json`.
- Added `make update-cloudtainer-shadow-pass-volatility` / `make test-cloudtainer-shadow-pass-volatility`, and refreshed the README/docs/generated-doc surface around the new optional report.
- Main practical result: the archive now preserves one explicit answer to “which shadow-pass timings are stable enough to trust tightly?” instead of only the latest frontier and the coarse receipt-history ranges.


## Additional pass: cloudtainer shadow-pass budget cards

- Added one compact blocked-session budgeting discipline so future inheritors can choose the short / medium / long shadow-pass command surface from one fused report instead of reopening the frontier, history, and volatility docs by hand:
  - `scripts/report/build_cloudtainer_shadow_pass_budget_card.py`
  - `artifacts/reports/cloudtainer_shadow_pass_budget_card.json`
  - `docs/CLOUDTAINER_SHADOW_PASS_BUDGET_CARD.md`
  - `scripts/test/check_cloudtainer_shadow_pass_budget_card.py`
- Extended the Makefile, generated-doc presence check, README, docs index, environment handbook, command inventory, validator inventory, and artifact buckets so the new budget card remains discoverable and drift-checked.
- Main practical result: the archive now keeps one tiny answer to “which blocked-session command should I run under this time ceiling, and how much buffer should I add?” instead of forcing a future steward to reconcile the frontier, receipt history, and volatility reports manually.



## Additional pass: Rust comeback execution card and dual-lane closure clarification

- Added one compact first-machine execution surface so future inheritors do not just know which shard plateau to land, but also exactly which new Rust witnesses and lane-smoke commands to run after each plateau.
- Added `scripts/report/build_rust_comeback_execution_card.py`, generated `docs/RUST_COMEBACK_EXECUTION_CARD.md`, and emitted `artifacts/reports/rust_comeback_execution_card.json`.
- Added `make update-rust-comeback-execution-card` / `make test-rust-comeback-execution-card`, refreshed the README/docs/generated-doc surfaces around the new report, and added `scripts/test/check_rust_comeback_execution_card.py`.
- Found and fixed one wording bug in the prefix frontier during this pass: `probe_lane_closure` was previously described as if it happened before the final dual-lane shard, but the last missing `probe_run` witness is actually bundled with the only metamorphic witness in shard 10. The frontier now states that this closure coincides with the final dual-lane shard instead of implying a nonexistent pure probe-only closure plateau.
- Main practical result: the archive now preserves one explicit answer to “after I apply this comeback prefix on the first Rust-capable machine, what exact tests should I run next?” and it no longer suggests a misleading probe-only closure stop point.

- Added one compact archive-boundary size card so future inheritors can see the live footprint, the growth delta since the older 2026-03-16 size snapshot, and whether PDFs or scratch have leaked back into the package boundary without reopening the broader historical compaction machinery:
  - `scripts/report/build_archive_size_guardrail_card.py`
  - `artifacts/reports/archive_size_guardrail_card.json`
  - `docs/ARCHIVE_SIZE_GUARDRAIL_CARD.md`
  - `scripts/test/check_archive_size_guardrail_card.py`
- Preserved the main current archive-shaping result in a small durable handoff surface:
  - the live tree is still `PDF`-free and scratch-free at package time,
  - raw size and zip size have both grown meaningfully since 2026-03-16,
  - and the dominant byte pressure is now internal doctrine, chronicles, and generated/tooling surfaces rather than reacquired literature blobs.


## Additional pass: archive byte triage card

- Added one compact byte-saving decision surface so future inheritors can preserve the small blocked-session Rust/cloudtainer/archive-size handoff stack while still knowing exactly which large retained markdown surfaces to condense first if the archive ever needs a deliberate diet pass:
  - `scripts/report/build_archive_byte_triage_card.py`
  - `artifacts/reports/archive_byte_triage_card.json`
  - `docs/ARCHIVE_BYTE_TRIAGE_CARD.md`
  - `scripts/test/check_archive_byte_triage_card.py`
- Extended the Makefile, generated-doc presence check, README/docs index, environment handbook, command inventory, validator inventory, and artifact buckets so the new byte-triage card remains discoverable and drift-checked.
- Main practical result: the archive now preserves one explicit answer to “what should I protect, and what should I trim first, if this repo needs to get smaller?” instead of forcing a future steward to improvise a byte-saving pass from raw file sizes alone.


## Additional pass: archive package cut card

- Added one compact package-cut discipline so future inheritors do not just know the live archive size and trim-first pack, but also which mutating gates must run first and in what stable order to refresh the archive-truth surfaces before cutting the next revision zip:
  - `scripts/report/build_archive_package_cut_card.py`
  - `artifacts/reports/archive_package_cut_card.json`
  - `docs/ARCHIVE_PACKAGE_CUT_CARD.md`
  - `scripts/test/check_archive_package_cut_card.py`
- Preserved one concrete live packaging nuance in a small durable surface: `make test-quick` and `make test-full` both write `artifacts/timing/env_<mode>.json` through `scripts/test/run_harness.sh`, so those harness gates must happen before the final package-boundary size refresh instead of after it.
- Main practical result: the archive now keeps one explicit answer to “how do I cut the next revision zip without reintroducing avoidable size-card drift?” instead of forcing a future steward to reconstruct that ritual from scattered guardrail/triage notes and recent session memory.

## Additional pass: archive reentry card and changelog head repair

- Added one compact archive-head pointer so future inheritors can reopen the current revision from one role-annotated card instead of reconciling the Rust recovery, comeback execution, and package-cut surfaces by hand:
  - `scripts/report/build_archive_reentry_card.py`
  - `artifacts/reports/archive_reentry_card.json`
  - `docs/ARCHIVE_REENTRY_CARD.md`
  - `scripts/test/check_archive_reentry_card.py`
- Preserved the main current reentry result in one small durable surface:
  - the local blocked-session move is still `make cloudtainer-shadow-pass-medium`,
  - the first Rust-capable foothold is still shard `01` plus one exact `probe_run` witness,
  - and the package-cut steward should still open the package-cut card and byte-triage card rather than improvise a fresh closing ritual.
- Found and fixed one repo-truth gap while landing the card: `CHANGELOG.md` had stalled at `rev0519`, which meant the current archive head could not be recovered from the repo itself. Backfilled the archive changelog through `rev0526` so the new head pointer can fail closed on actual repo state instead of silently inheriting stale authority.


## Additional pass: archive revision cut planner + package-cut inventory repair

- Added one normalized next-revision naming surface so future package stewards no longer have to improvise the next root/zip stem by hand after a settle pass:
  - `scripts/tools/plan_archive_revision_cut.py`
  - `scripts/report/build_archive_revision_cut_card.py`
  - `artifacts/reports/archive_revision_cut_card.json`
  - `docs/ARCHIVE_REVISION_CUT_CARD.md`
  - `scripts/test/check_archive_revision_cut_card.py`
- Fixed a real package-cut doc bug while landing it: `docs/ARCHIVE_PACKAGE_CUT_CARD.md` had been telling stewards to use inventory **test** targets inside the refresh sequence even though those targets validate only and do not write. The card now points at the real inventory update targets, which matches `make settle-archive-truth` and the live closeout ritual.
- Main practical result: the package steward lane now preserves both halves of the closeout discipline in-repo — first settle the archive truth surface, then derive the exact next normalized revision name without reusing an old revision number.


## Additional pass: archive zip lineage audit + external duplicate-revision guard

- Added a sibling-zip audit lane so package stewards no longer have to infer archive authority from filenames by hand when multiple revision zips live next to each other. Landed:
  - `scripts/tools/audit_archive_zip_lineage.py`
  - `scripts/report/build_archive_zip_lineage_card.py`
  - `artifacts/reports/archive_zip_lineage_card.json`
  - `docs/ARCHIVE_ZIP_LINEAGE_CARD.md`
  - `scripts/test/check_archive_zip_lineage_card.py`
- The audit now prefers `/mnt/data` when it actually contains Golden Rule revision zips, which matters in this cloudtainer because the unpacked worktree lives under `/tmp` while the authoritative sibling zip lane lives under `/mnt/data`.
- Preserved a concrete external-package fact instead of letting it live only in chat history: the sibling zip lane still contains a duplicated revision label (`rev0524` appears twice), while the authoritative external head aligns with the live `rev0529` root and the immediate predecessor zip is `rev0528`.
- Threaded the new card into the closeout plane so future settle/cut passes refresh and validate it automatically: `make settle-archive-truth` and `python3 scripts/tools/cut_archive_revision.py ...` now include the zip-lineage card after the reentry/revision-cut surfaces, and the package-cut card now names that external audit step explicitly.

## Additional pass: rematch-world citation witness matrix and landing-ladder discoverability repair

- Added one compact citation-first control surface so future inheritors can cite the smallest existing rematch-world receipts/docs for each claim family instead of reopening the entire bridge stack:
  - `scripts/report/build_rematch_world_benchmark_citation_witness_matrix.py`
  - `artifacts/reports/rematch_world_benchmark_citation_witness_matrix.json`
  - `docs/REMATCH_WORLD_BENCHMARK_CITATION_WITNESS_MATRIX.md`
  - `scripts/test/check_rematch_world_benchmark_citation_witness_matrix.py`
- Preserved the main evidence-backed split in one place: 8 claim families now collapse onto 7 small citation surfaces, with 4 bridge-ready rows, 3 explicitly provisional interpretation rows, and 1 final-authority row.
- Fixed a real discoverability gap while landing it: `docs/REMATCH_WORLD_BENCHMARK_LANDING_LADDER.md` already existed but was not enforced by generated-doc presence or listed in the README/doc index surfaces, so future reopeners could have missed one of the most useful rematch-world bridge cards.


## Additional pass: rematch-world open touchpoint resolution map

- Added one compact closure queue so future inheritors no longer have to translate the rematch-world caution surfaces by hand into an implementation sequence:
  - `scripts/report/build_rematch_world_benchmark_open_touchpoint_resolution_map.py`
  - `artifacts/reports/rematch_world_benchmark_open_touchpoint_resolution_map.json`
  - `docs/REMATCH_WORLD_BENCHMARK_OPEN_TOUCHPOINT_RESOLUTION_MAP.md`
  - `scripts/test/check_rematch_world_benchmark_open_touchpoint_resolution_map.py`
- Preserved the main implementor-facing compression in one place: the current rematch-world bridge stack still names `11` open touchpoints, but they now collapse to `6` actual closure targets, with `5` folded assumptions, `23` seed-local blocker slots, and `28` seed-local required edits before the remaining cross-section engine gap is the only unresolved non-package blocker.
- Main practical result: the next Rust-capable inheritor can choose the next world-native closure target directly from one small report instead of reopening the citation matrix, native-fill map, landing ladder, and spec ledger together just to figure out which open question lands where.

## Additional pass: rematch-world claim frontier
- Added `scripts/report/build_rematch_world_benchmark_claim_frontier.py`, generated `docs/REMATCH_WORLD_BENCHMARK_CLAIM_FRONTIER.md` plus `artifacts/reports/rematch_world_benchmark_claim_frontier.json`, and wired `make update-rematch-world-benchmark-claim-frontier` / `make test-rematch-world-benchmark-claim-frontier`.
- Main local result: the first rematch-world claim frontier now closes in three actionable native bands — `8`, `18`, and `29` cumulative edits — while `RWC-001`, `RWC-002`, and `RWC-004` stay citation-first behind `SG-003`; no claim family closes at the one-edit benchmark-id bind by itself.
- Implementor consequence: future inheritors can stop the first native fill pass exactly when a target claim family becomes safe, rather than finishing all five seed-local sections before checking whether a particular publication statement is already justified.

## Additional pass: rematch-world proof-budget ledger

- Added one compact byte-budget control surface so future inheritors can answer “what is the smallest exact proof bundle for this claim?” without reopening the broader rematch-world bridge stack:
  - `scripts/report/build_rematch_world_benchmark_proof_budget_ledger.py`
  - `artifacts/reports/rematch_world_benchmark_proof_budget_ledger.json`
  - `docs/REMATCH_WORLD_BENCHMARK_PROOF_BUDGET_LEDGER.md`
  - `scripts/test/check_rematch_world_benchmark_proof_budget_ledger.py`
- Preserved the main size-discipline result in one place: all `8` rematch-world claim families now collapse onto a `7`-surface minimal proof library totaling `43186` bytes, with `6` docs-only bundles and only `2` receipt-backed bundles.
- Main practical result: future archive passes can price any new rematch-world scratch against an explicit existing proof budget instead of retaining extra derived artifacts by default.


## Additional pass: cloudtainer userspace fetch surface

- Added one static companion to the later-machine userspace-rustup comeback lane so future inheritors can see whether the dependency bring-up is still small *before* they spend a short egress window on it:
  - `scripts/report/build_cloudtainer_userspace_fetch_surface.py`
  - `artifacts/reports/cloudtainer_userspace_fetch_surface.json`
  - `docs/CLOUDTAINER_USERSPACE_FETCH_SURFACE.md`
  - `scripts/test/check_cloudtainer_userspace_fetch_surface.py`
- Preserved the main later-machine sizing fact in one place: the current Rust comeback surface is still `registry_only_single_workspace` with `80` lockfile packages total, `79` registry packages, `0` git packages, `1` workspace/path package, and only one workspace member (`crates/gr_engine`).
- Main practical result: the archive now keeps both halves of the later-machine Rust lane in durable form — the exact bootstrap/fetch/probe/prune commands *and* the static lockfile/workspace audit that says whether that lane is still expected to be a short registry-only fetch story.

## Additional pass: cloudtainer userspace compile surface

- Added one static companion to the userspace fetch card so future inheritors can answer a different later-machine question before spending a compile attempt:
  - `scripts/report/build_cloudtainer_userspace_compile_surface.py`
  - `artifacts/reports/cloudtainer_userspace_compile_surface.json`
  - `docs/CLOUDTAINER_USERSPACE_COMPILE_SURFACE.md`
  - `scripts/test/check_cloudtainer_userspace_compile_surface.py`
- Preserved the main first-compile result in one place: the current lane is still `direct_derive_no_native_build`, with `11` direct dependencies total, `2` direct derive-feature entry points (`clap`, `serde`), `0` workspace `build.rs` files, `0` build-dependencies, `6` lockfile codegen-support package hits, and `0` native-helper watchlist hits.
- Main practical result: after the repo-local `rustup` bootstrap and `cargo fetch --locked` succeed on a later machine, the first compile/test foothold still looks like a pure-Rust plus proc-macro/codegen witness rather than a host-C-toolchain rescue job.

