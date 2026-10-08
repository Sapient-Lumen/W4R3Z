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

# Agent Log

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

