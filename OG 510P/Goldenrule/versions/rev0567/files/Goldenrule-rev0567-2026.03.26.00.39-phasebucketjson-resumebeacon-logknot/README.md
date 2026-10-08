# Concord

Concord is a research lab for deterministic reciprocity experiments.

Core split:
- Rust (`crates/gr_engine`) for simulation and formalizable artifacts.
- Python (`grlab`) for orchestration, reporting, and workflow tooling.

Project scope is defined in [docs/PROJECT_CHARTER.md](docs/PROJECT_CHARTER.md).

Execution plan is tracked in [docs/SCIENCE_PLAN.md](docs/SCIENCE_PLAN.md).

## Operating Contract

- Behavioral rules for humans/agents: [AGENTS.md](AGENTS.md)
- Normative ground and project purpose: [COVENANT.md](COVENANT.md) ← read first
- Standing witnesses (qualitative pillar): [PARABLES.md](PARABLES.md)
- Governance and ops docs: [docs/README.md](docs/README.md)
- Implementation provenance: [docs/PROVENANCE.md](docs/PROVENANCE.md)

## Command Index

Primary repo controls run through `make`:

```bash
make doctor
make cloudtainer-shadow-pass
make cloudtainer-shadow-pass-list-budgets
make cloudtainer-shadow-pass-short
make cloudtainer-shadow-pass-medium
make cloudtainer-shadow-pass-long
make cloudtainer-shadow-pass-resume
make test-cloudtainer-shadow-pass-resume
make test-cloudtainer-shadow-pass-budget-profiles
make update-cloudtainer-shadow-pass-history
make test-cloudtainer-shadow-pass-history
make update-cloudtainer-shadow-pass-volatility
make test-cloudtainer-shadow-pass-volatility
make update-cloudtainer-shadow-pass-budget-card
make test-cloudtainer-shadow-pass-budget-card
make update-cloudtainer-rust-probe-oracles
make test-cloudtainer-rust-probe-oracles
make show-cloudtainer-userspace-rustup-plan
make update-cloudtainer-userspace-rustup-plan
make test-cloudtainer-userspace-rustup-plan
make update-cloudtainer-userspace-fetch-surface
make test-cloudtainer-userspace-fetch-surface
make update-cloudtainer-userspace-compile-surface
make test-cloudtainer-userspace-compile-surface
make update-cloudtainer-userspace-offline-proof-ladder
make test-cloudtainer-userspace-offline-proof-ladder
make update-cloudtainer-userspace-failure-resume-card
make test-cloudtainer-userspace-failure-resume-card
make update-cloudtainer-standing-bootstrap-delta
make test-cloudtainer-standing-bootstrap-delta
make update-archive-size-guardrail-card
make test-archive-size-guardrail-card
make update-archive-byte-triage-card
make test-archive-byte-triage-card
make update-archive-package-cut-card
make test-archive-package-cut-card
make update-archive-reentry-card
make test-archive-reentry-card
make update-archive-revision-cut-card
make test-archive-revision-cut-card
make update-archive-zip-lineage-card
make test-archive-zip-lineage-card
make update-archive-zip-chronology-card
make test-archive-zip-chronology-card
make update-archive-zip-authority-card
make test-archive-zip-authority-card
make update-archive-zip-digest-card
make test-archive-zip-digest-card
make plan-archive-revision-cut DESCRIPTOR=your-summary-slug
make cut-archive-revision DESCRIPTOR=your-summary-slug SUMMARY="one-line summary"
make settle-archive-truth
make update-archive-handoff-pack
make test-archive-handoff-pack
make verify-authoritative-archive-zip
make test-authoritative-archive-zip-verify-tool
make test-archive-truth-settle-tool
make test-quick
make test-full
make gate
make gate-strict
make clean-test-artifacts
make test-flake N=5
make test-soak N=2
make test-soak-async N=2
make check-soak-status
make test-formal-smoke
make test-formal-tools
make test-examples-json
make test-examples-unique-ids
make test-required-examples
make test-schema-json
make test-policy-json
make test-hooks-contract
make test-artifact-gitkeeps
make test-timing-artifacts
make test-generated-docs
make test-research-docs
make test-claim-classes
make update-claim-matrix
make test-claim-matrix
make test-claim-register
make update-claim-register-summary
make test-claim-register-summary
make test-risk-register
make update-risk-register-summary
make test-risk-register-summary
make test-doc-links
make test-readme-commands
make test-docs-index
make test-release-doc
make test-tranches
make update-tranche-status
make test-tranche-status
make test-ci-smoke
make test-policy-expirations
make test-spec-evidence
make test-make-help
make test-scripts-exec
make test-scripts-compile
make update-experiment-catalog
make test-experiment-catalog
make update-command-inventory
make test-command-inventory
make update-validator-inventory
make test-validator-inventory
make update-policy-inventory
make test-policy-inventory
make update-schema-inventory
make test-schema-inventory
make update-artifact-buckets
make test-artifact-buckets
make update-rust-surface-inventory
make test-rust-surface-inventory
make update-rust-restart-map
make test-rust-restart-map
make update-rust-test-contracts
make test-rust-test-contracts
make update-rust-test-scenario-coverage
make test-rust-test-scenario-coverage
make update-rust-gap-witness-queue
make test-rust-gap-witness-queue
make update-rust-gap-probe-seed-index
make test-rust-gap-probe-seed-index
make update-rust-external-test-queue
make test-rust-external-test-queue
make update-rust-seed-loader-readiness
make test-rust-seed-loader-readiness
make update-rust-lift-bundle-plan
make test-rust-lift-bundle-plan
make update-rust-external-test-patchset
make test-rust-external-test-patchset
make update-rust-external-test-patch-shards
make test-rust-external-test-patch-shards
make update-rust-external-test-patch-rehearsal
make test-rust-external-test-patch-rehearsal
make update-rust-standing-bootstrap-guard
make test-rust-standing-bootstrap-guard
make update-rust-standing-bootstrap-guard-rehearsal
make test-rust-standing-bootstrap-guard-rehearsal
make update-rust-standing-bootstrap-repair-patch
make test-rust-standing-bootstrap-repair-patch
make update-rust-standing-bootstrap-repair-rehearsal
make test-rust-standing-bootstrap-repair-rehearsal
make update-rust-standing-bootstrap-route-equivalence
make test-rust-standing-bootstrap-route-equivalence
make update-rust-standing-bootstrap-verification-ladder
make test-rust-standing-bootstrap-verification-ladder
make update-rust-standing-bootstrap-verification-ladder-rehearsal
make test-rust-standing-bootstrap-verification-ladder-rehearsal
make update-rust-standing-bootstrap-checkpoints
make test-rust-standing-bootstrap-checkpoints
make update-rust-standing-bootstrap-checkpoints-rehearsal
make test-rust-standing-bootstrap-checkpoints-rehearsal
make update-rust-standing-bootstrap-checkpoint-verifier
make test-rust-standing-bootstrap-checkpoint-verifier
make update-rust-standing-bootstrap-checkpoint-verifier-rehearsal
make test-rust-standing-bootstrap-checkpoint-verifier-rehearsal
make test-rust-standing-bootstrap-checkpoint-verifier-tool
make report-artifact-summary
make test-reports-json
make report-repro-bundle
make test-release-manifest-schema
make test-release-manifest-entries RELEASE_VERSION=dev
make test-release-checksums RELEASE_VERSION=dev
```

`make gate-strict` requires strict security tools (currently `cargo-audit` and `cargo-deny`).

Core legacy checks:

```bash
tools/check.sh
```

Domain CLI examples:

```bash
python3 -m grlab run examples/experiments/ipd_smoke.json
python3 -m grlab report runs/<run_id>
python3 -m grlab verify runs/<run_id>
python3 -m grlab gauntlet --candidate examples/strategies/tft.json --world examples/worlds/ipd_long.json
python3 -m grlab holdout --candidate examples/strategies/tft.json
python3 -m grlab search --world examples/worlds/ipd_long.json --opponent examples/strategies/extortion_chi3.json --trials 100 --out /tmp/search.json
```

## Baseline Layout

- `specs/`: normative spec and assumption ledger.
- `docs/`: governance and operational policy.
- `docs/FORMAL_METHODS.md`: formal invariants and solver posture.
- `docs/CLAIM_TAXONOMY.md`: claim classes and evidence obligations.
- `docs/CLAIM_MATRIX.md`: generated claim-class matrix.
- `docs/CLAIM_REGISTER.md`: generated claim register summary.
- `docs/RISK_REGISTER.md`: generated risk register summary.
- `docs/EXPERIMENT_CATALOG.md`: generated index of example scientific assets.
- `docs/RUST_RESTART_MAP.md`: generated restart-priority map for Rust-blocked sessions.
- `docs/RUST_TEST_CONTRACTS.md`: generated semantic-contract ledger showing what the Rust tests are trying to protect when the toolchain is blocked.
- `docs/RUST_TEST_SCENARIO_COVERAGE.md`: generated scenario-coverage ledger showing which world/strategy/assertion variants the Rust tests do and do not currently touch.
- `docs/RUST_GAP_WITNESS_QUEUE.md`: generated gap-to-witness queue showing which weak Rust scenarios already have seed fixtures or source anchors in the repo.
- `docs/RUST_GAP_PROBE_SEED_INDEX.md`: generated probe-seed index showing which weak Rust scenarios already have self-contained `examples/probes/*.json` anchors for future external Rust tests.
- `docs/RUST_EXTERNAL_TEST_QUEUE.md`: generated lift queue showing where each weak Rust probe seed should land first in the external Rust test surface once a real toolchain returns.
- `docs/RUST_SEED_LOADER_READINESS.md`: generated seed-loader audit proving whether those preferred lift-queue seeds are directly loadable `ProbeSpec` fixtures or still need translation.
- `docs/RUST_LIFT_BUNDLE_PLAN.md`: generated shared-fixture code bundle plan that collapses repeated weak-scenario rows into helper-backed Rust lift bundles.
- `docs/RUST_EXTERNAL_TEST_PATCHSET.md`: generated replayable unified patch that appends the first proposed external Rust comeback tests without editing the crate in-place during blocked sessions.
- `docs/RUST_EXTERNAL_TEST_PATCH_SHARDS.md`: generated ordered cumulative patch series that breaks that comeback into smaller replayable landing chunks.
- `docs/RUST_EXTERNAL_TEST_PATCH_REHEARSAL.md`: generated scratch-apply equivalence rehearsal proving the monolithic patchset and cumulative shard series land on the same final target files.
- `docs/RUST_STANDING_BOOTSTRAP_GUARD.md`: generated standalone Rust guard patch for the simple-standing bootstrap seam, asserting round-0 trace standing equals the declared `world.reputation.initial_standing` once that seam is repaired.
- `docs/RUST_STANDING_BOOTSTRAP_GUARD_REHEARSAL.md`: generated scratch-apply rehearsal proving the standalone bootstrap guard patch cleanly creates its dedicated Rust test file and that the landed bytes match the generated report.
- `docs/RUST_STANDING_BOOTSTRAP_REPAIR_PATCH.md`: generated minimal source-level Rust repair patch that makes probe-generated tasks honor declared `simple_standing.initial_standing` without broadening semantics for non-probe task ingress.
- `docs/RUST_STANDING_BOOTSTRAP_REPAIR_REHEARSAL.md`: generated scratch-apply sequence rehearsal proving the repair patch lands cleanly on `probe.rs` and that the standalone guard patch still layers on top afterward.
- `docs/RUST_STANDING_BOOTSTRAP_INTEGRATION_REHEARSAL.md`: generated compatibility rehearsal proving the narrow bootstrap repair and guard are operationally orthogonal to the larger Rust comeback patchset in both landing orders.
- `docs/RUST_STANDING_BOOTSTRAP_COMEBACK_BUNDLE.md`: generated clean-head convenience bundle that compresses `repair -> guard -> patchset` into one replayable Rust patch once a real toolchain returns.
- `docs/RUST_STANDING_BOOTSTRAP_COMEBACK_BUNDLE_REHEARSAL.md`: generated scratch-apply rehearsal proving that one-shot comeback bundle lands cleanly and matches the hashed final state from the layered sequence.
- `docs/RUST_STANDING_BOOTSTRAP_POST_PATCHSET_BUNDLE.md`: generated follow-on convenience bundle for the branch state where the monolithic comeback patchset has already landed, compressing `repair -> guard` into one additional apply step.
- `docs/RUST_STANDING_BOOTSTRAP_POST_PATCHSET_BUNDLE_REHEARSAL.md`: generated scratch-apply rehearsal proving that the monolithic patchset plus the post-patchset convenience bundle lands cleanly and matches the hashed final state from the already-proven `patchset -> repair -> guard` sequence.
- `docs/RUST_STANDING_BOOTSTRAP_STATE_SELECTOR.md`: generated exact-state selector card for the four bootstrap/comeback target files, showing which convenience bundle is safe for which branch state and where explicit layered continuation is required instead.
- `docs/RUST_STANDING_BOOTSTRAP_STATE_SELECTOR_REHEARSAL.md`: generated scratch-state rehearsal proving the selector recognizes all known exact branch states and fails closed on a deliberately drifted target-file state.
- `docs/RUST_STANDING_BOOTSTRAP_ROUTE_EQUIVALENCE.md`: generated route-exactness proof showing that the clean-head bundle, explicit layered landing, and patchset-plus-follow-on bundle converge to the same four-file final state.
- `docs/RUST_STANDING_BOOTSTRAP_EXECUTION_CARD.md`: generated branch-state execution card showing the smallest safe bootstrap apply sequence from each recognized exact branch state plus the exact final hash every route should converge to.
- `docs/RUST_STANDING_BOOTSTRAP_EXECUTION_REHEARSAL.md`: generated scratch-state rehearsal proving the execution-plan tool lands that same exact final hash from every recognized non-final state and fails closed on drift.
- `docs/RUST_STANDING_BOOTSTRAP_VERIFICATION_LADDER.md`: generated final-state verification ladder for the repaired bootstrap seam, starting with the dedicated guard file and then the three exact affected `probe_run` witnesses before broader smoke.
- `docs/RUST_STANDING_BOOTSTRAP_VERIFICATION_LADDER_REHEARSAL.md`: generated scratch-state rehearsal proving the verification ladder only emits after the checkout reaches exact `final_full` and otherwise routes back to apply sequencing.
- `docs/RUST_STANDING_BOOTSTRAP_CHECKPOINTS.md`: generated intermediate-checkpoint card showing the exact recognized state id and 4-file combined hash that should appear after each bootstrap apply step, so layered landings can pause safely between patches.
- `docs/RUST_STANDING_BOOTSTRAP_CHECKPOINTS_REHEARSAL.md`: generated scratch-state rehearsal proving those checkpoint state ids and combined hashes match the actual post-apply checkout after every emitted bootstrap patch command.
- `docs/RUST_STANDING_BOOTSTRAP_CHECKPOINT_VERIFIER.md`: generated exact verifier card for direct exact-state checks and per-step checkpoint verification after each bootstrap patch apply.
- `docs/RUST_STANDING_BOOTSTRAP_CHECKPOINT_VERIFIER_REHEARSAL.md`: generated scratch-state rehearsal proving the checkpoint verifier itself still succeeds, fails closed on drift, and rejects conflicting checkpoint expectations.
- `docs/RUST_PATCH_PREFIX_FRONTIER.md`: generated stopping-point frontier showing which cumulative shard prefixes give the cleanest partial comeback plateaus by rows covered versus added lines.
- `docs/RUST_COMEBACK_CARD.md`: generated one-page landing-order card that fuses queue, seed-loader, bundle, shard, rehearsal, and prefix-frontier signals for the first Rust-capable implementor.
- `docs/RUST_COMEBACK_EXECUTION_CARD.md`: generated first-machine apply/run card showing which exact witnesses and lane-smoke commands to run after each comeback plateau, including the final dual-lane coupling at full closure.
- `docs/CLOUDTAINER_SHADOW_PASS_FRONTIER.md`: generated budgeting frontier showing which interrupted blocked-session prefixes leave the best refreshed handoff surface before a later resume, plus the exact short/medium/long make commands for those cutpoints.
- `docs/CLOUDTAINER_SHADOW_PASS_HISTORY.md`: generated receipt-history view showing how the shadow pass widened over time and how stable the key budget cutpoints remain across completed receipts.
- `docs/CLOUDTAINER_SHADOW_PASS_VOLATILITY.md`: generated timing trust map showing which steps and frontier anchors are stable, watch-grade, or jittery across current-profile receipts.
- `docs/CLOUDTAINER_SHADOW_PASS_BUDGET_CARD.md`: generated fused budget card showing the exact short/medium/long commands plus buffered timing guidance from the frontier, history, and volatility reports.
- `docs/CLOUDTAINER_RUST_RECOVERY_CARD.md`: generated decision card showing whether Rust is recoverable inside the current cloudtainer, when to stop trying in place, and what the first quick foothold should be on the next Rust-capable machine.
- `docs/CLOUDTAINER_RUST_PROBE_ORACLES.md`: generated blocked-session oracle card giving exact path witnesses for deterministic comeback probe seeds and exact finite-horizon expectation witnesses for the current stochastic seeds.
- `docs/CLOUDTAINER_USERSPACE_RUSTUP_PLAN.md`: generated later-machine comeback card that emits one repo-local rustup/bootstrap/fetch/probe/prune sequence and keeps transient `.local` roots explicit so the archive does not quietly retain a userspace toolchain.
- `docs/CLOUDTAINER_USERSPACE_FETCH_SURFACE.md`: generated static dependency-surface companion to that comeback lane, showing the current lockfile source mix, workspace width, direct dependency counts, and the tripwires that would widen the next egress window.
- `docs/CLOUDTAINER_USERSPACE_COMPILE_SURFACE.md`: generated static compile-friction companion to the same lane, showing the current direct derive/codegen entry points, the absence or presence of local `build.rs` surfaces, and the native-helper watchlist that would turn the first compile witness into a host-tooling rescue job.
- `docs/CLOUDTAINER_USERSPACE_OFFLINE_PROOF_LADDER.md`: generated later-machine execution ladder that proves the warmed cache is sufficient offline before widening past the first exact probe witness.
- `docs/CLOUDTAINER_USERSPACE_FAILURE_RESUME_CARD.md`: generated later-machine failure decoder that maps common rustup/Cargo/patch/test logs back to the exact comeback phase and rerun command to resume from.
- `docs/CLOUDTAINER_STANDING_BOOTSTRAP_DELTA.md`: generated blocked-session delta card showing whether fixing the current simple-standing bootstrap seam would move the current comeback witnesses, and if so at which semantic layer.
- `docs/RUST_STANDING_BOOTSTRAP_REPAIR_PATCH.md`: the first-machine companion to that delta card, scoped to the actual probe-generated task path rather than a wider engine-wide default change.
- `docs/ARCHIVE_SIZE_GUARDRAIL_CARD.md`: generated package-boundary size card showing live byte pressure, growth since the older size snapshot, and whether PDFs or scratch leaked back into the revision boundary.
- `docs/ARCHIVE_BYTE_TRIAGE_CARD.md`: generated byte-saving decision card showing which large markdown surfaces to condense first before touching the compact blocked-session Rust/cloudtainer handoff stack.
- `docs/ARCHIVE_PACKAGE_CUT_CARD.md`: generated package-cut discipline card showing which mutating gates and fixed-point refresh steps must happen before the next revision zip, plus the canonical settle wrapper `make settle-archive-truth` and the canonical last-mile cutter `python3 scripts/tools/cut_archive_revision.py --descriptor ... --summary "..."`.
- `docs/ARCHIVE_REENTRY_CARD.md`: generated role-annotated archive head pointer showing the current archive identity plus the first open target and command for blocked cloudtainer work, the first Rust-capable machine, and the final package cut.
- `docs/ARCHIVE_HANDOFF_PACK.md`: generated hash-bearing blocked-session control-plane pack listing the exact doc/report pairs, hashes, and verify/refresh commands that future inheritors should trust first.
- `docs/ARCHIVE_REVISION_CUT_CARD.md`: generated naming-and-cutover card showing the next safe revision label, the filename contract, the planner command that emits the exact next root/zip stem, and the canonical one-command cutter for the final rename/changelog/zip step.
- `docs/ARCHIVE_ZIP_LINEAGE_CARD.md`: generated sibling-zip audit card showing whether the external package lane agrees with the live root, which zip is the immediate predecessor, and whether any revision labels were reused across sibling zip files.
- `docs/ARCHIVE_ZIP_CHRONOLOGY_CARD.md`: generated sibling-zip chronology card showing whether revision order remains timestamp-monotone, whether latest-by-revision and latest-by-timestamp still coincide, and why archive-head authority must prefer revision labels when they do not.
- `docs/ARCHIVE_ZIP_AUTHORITY_CARD.md`: generated sibling-zip reopen card showing the exact authoritative external zip path to reopen, the resolution rule, and the shell-safe commands for emitting that path or a matching unzip command.
- `docs/ARCHIVE_ZIP_DIGEST_CARD.md`: generated sibling-zip verification card showing the authoritative external zip's exact path, byte size, and SHA-256 so the reopened package bytes can be checked directly, plus the one-command verifier `python3 scripts/tools/verify_authoritative_archive_zip.py`.
- `docs/ARCHIVE_ZIP_SIZE_TRUTH_CARD.md`: generated card distinguishing the internal package-size proxy from the exact sibling zip bytes, calibrated against the immutable predecessor zip so the current head does not pretend to embed its own final size.
- `docs/REMATCH_WORLD_BENCHMARK_WORLD_EMISSION_CARD.md`: generated compact control surface for the first endogenous rematch-world benchmark, showing the five native fill targets, the eight copied frozen sections that must stay citation-first, the publication/prune/package ladder, and the durable-vs-transient retention split.
- `docs/REMATCH_WORLD_BENCHMARK_NATIVE_FILL_MAP.md`: generated exact fill-locus map for that same benchmark, showing the legal edit prefixes, per-section blocker rows, metadata/status transitions, and the smallest publishable edit set the eventual implementor must clear.
- `docs/REMATCH_WORLD_BENCHMARK_LANDING_LADDER.md`: generated exact 7-stage edit ladder plus 5-phase closeout ladder for the same publication path, so the first native landing order no longer has to be reconstructed from scattered receipts.
- `docs/REMATCH_WORLD_BENCHMARK_EXAMPLE_DELTA_LEDGER.md`: generated exact seed-to-compiled mutation ledger for the synthetic first rematch-world publication, separating the 30-path publication floor from the 3 optional row insertions while proving the copied handoff roots stay untouched.
- `docs/REMATCH_WORLD_BENCHMARK_CLOSEOUT_LIFECYCLE_LEDGER.md`: generated exact closeout lifecycle ledger for the same publication path, showing which six objects must persist, which four transient rows may exit, and which seven receipts provide guard, cleanup, zip-readiness, and final package authority.
- `docs/REMATCH_WORLD_BENCHMARK_CITATION_WITNESS_MATRIX.md`: generated minimal citation witness surface for the same benchmark, mapping each claim family to the smallest existing docs/receipts that should be cited and the open spec touchpoints that still keep interpretation provisional.
- `docs/REMATCH_WORLD_BENCHMARK_OPEN_TOUCHPOINT_RESOLUTION_MAP.md`: generated compact closure queue for the same benchmark, collapsing the 11 still-open rematch-world touchpoints into 6 actual closure targets with exact affected claim families, bridge citations, and seed-local blocker/edit counts where applicable.
- `docs/REMATCH_WORLD_BENCHMARK_CLAIM_FRONTIER.md`: generated claim-readiness frontier for the same benchmark, showing which claim families are already safe now, which unlock at 8/18/29 cumulative native edits, and which remain blocked by the unresolved cross-section engine gap.
- `docs/REMATCH_WORLD_BENCHMARK_STAGE_YIELD_LEDGER.md`: generated per-stage yield ledger for the same benchmark, showing which 7 ladder stages unlock claims, which are prerequisite-only resolver closures, and which final stage is metadata-only closeout.
- `docs/REMATCH_WORLD_BENCHMARK_PROOF_BUDGET_LEDGER.md`: generated byte-budget ledger for the same benchmark, showing the minimal proof-bundle size for each claim family and the full 7-surface citation library that keeps the archive small.
- `docs/QUALITY_ASSURANCE.md`: executable QA posture and gates.
- `docs/REPRODUCIBILITY.md`: deterministic replay and repro bundle rules.
- `docs/CI_POLICY.md`: CI smoke and deterministic enforcement.
- `docs/DEPENDENCY_POLICY.md`: dependency and allowlist posture.
- `schemas/`: validation schemas.
- `goldens/`: versioned reference artifacts.
- `artifacts/`: ephemeral run output (ignored from VCS).
- `scripts/`: automation and gate adapters.
- `tests/control/`: governance control tests.
