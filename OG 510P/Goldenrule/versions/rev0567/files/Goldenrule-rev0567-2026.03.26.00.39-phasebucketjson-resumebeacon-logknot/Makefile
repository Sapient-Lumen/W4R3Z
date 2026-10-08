SHELL := /usr/bin/env bash

export TZ := UTC
export LANG := C
export LC_ALL := C
export PYTHONHASHSEED := 0
export TEST_SEED ?= 424242
export NO_NETWORK ?= 1

.PHONY: help doctor cloudtainer-shadow-pass cloudtainer-shadow-pass-list-budgets cloudtainer-shadow-pass-short cloudtainer-shadow-pass-medium cloudtainer-shadow-pass-long cloudtainer-shadow-pass-resume test-cloudtainer-shadow-pass-resume test-cloudtainer-shadow-pass-budget-profiles update-cloudtainer-shadow-pass-frontier test-cloudtainer-shadow-pass-frontier update-cloudtainer-shadow-pass-history test-cloudtainer-shadow-pass-history update-cloudtainer-shadow-pass-volatility test-cloudtainer-shadow-pass-volatility update-cloudtainer-shadow-pass-budget-card test-cloudtainer-shadow-pass-budget-card update-cloudtainer-rust-recovery-card test-cloudtainer-rust-recovery-card update-cloudtainer-rust-probe-oracles test-cloudtainer-rust-probe-oracles update-cloudtainer-standing-bootstrap-delta test-cloudtainer-standing-bootstrap-delta show-cloudtainer-userspace-rustup-plan update-cloudtainer-userspace-rustup-plan test-cloudtainer-userspace-rustup-plan update-cloudtainer-userspace-fetch-surface test-cloudtainer-userspace-fetch-surface update-cloudtainer-userspace-compile-surface test-cloudtainer-userspace-compile-surface update-cloudtainer-userspace-offline-proof-ladder test-cloudtainer-userspace-offline-proof-ladder update-cloudtainer-userspace-failure-resume-card test-cloudtainer-userspace-failure-resume-card update-archive-size-guardrail-card test-archive-size-guardrail-card update-archive-byte-triage-card test-archive-byte-triage-card update-archive-package-cut-card test-archive-package-cut-card update-archive-reentry-card test-archive-reentry-card update-archive-handoff-pack test-archive-handoff-pack verify-archive-handoff-pack test-archive-handoff-pack-verify-tool verify-authoritative-archive-zip test-authoritative-archive-zip-verify-tool update-archive-revision-cut-card test-archive-revision-cut-card update-archive-zip-lineage-card test-archive-zip-lineage-card update-archive-zip-chronology-card test-archive-zip-chronology-card update-archive-zip-authority-card test-archive-zip-authority-card update-archive-zip-digest-card test-archive-zip-digest-card update-archive-zip-size-truth-card test-archive-zip-size-truth-card update-rematch-world-benchmark-world-emission-card test-rematch-world-benchmark-world-emission-card update-rematch-world-benchmark-native-fill-map test-rematch-world-benchmark-native-fill-map update-rematch-world-benchmark-example-delta-ledger test-rematch-world-benchmark-example-delta-ledger update-rematch-world-benchmark-closeout-lifecycle-ledger test-rematch-world-benchmark-closeout-lifecycle-ledger update-rematch-world-benchmark-citation-witness-matrix test-rematch-world-benchmark-citation-witness-matrix update-rematch-world-benchmark-open-touchpoint-resolution-map test-rematch-world-benchmark-open-touchpoint-resolution-map update-rematch-world-benchmark-claim-frontier test-rematch-world-benchmark-claim-frontier update-rematch-world-benchmark-stage-yield-ledger test-rematch-world-benchmark-stage-yield-ledger update-rematch-world-benchmark-proof-budget-ledger test-rematch-world-benchmark-proof-budget-ledger plan-archive-revision-cut cut-archive-revision settle-archive-truth test-archive-truth-settle-tool test-archive-revision-cut-tool test-quick test-full clean-test-artifacts gate gate-strict \
	test-goldens test-spec-ledger test-adr test-security test-security-strict \
	test-flake test-soak test-soak-async check-soak-status stop-soak-async \
	test-process-hygiene test-format-check test-spec-ledger-rollup \
	test-security-allowlist test-timing-baseline release-manifest \
	test-release-hygiene install-hooks test-examples-json test-doc-links \
	test-artifact-layout test-bypass-log test-gitignore-policy test-spec-dates \
	test-formal-smoke test-formal-tools update-experiment-catalog \
	test-experiment-catalog report-artifact-summary test-examples-unique-ids \
	test-scripts-exec test-scripts-compile test-readme-commands \
	test-docs-index test-tranches update-tranche-status test-tranche-status \
	test-release-manifest-schema test-release-checksums report-repro-bundle \
	test-ci-smoke test-policy-expirations test-spec-evidence test-release-doc \
	test-make-help test-required-examples test-reports-json update-command-inventory \
	test-command-inventory update-validator-inventory test-validator-inventory \
	update-policy-inventory test-policy-inventory test-schema-json \
	test-policy-json test-hooks-contract test-artifact-gitkeeps \
	test-release-manifest-entries test-timing-artifacts test-generated-docs \
	update-schema-inventory test-schema-inventory update-artifact-buckets \
	test-artifact-buckets update-rust-surface-inventory test-rust-surface-inventory \
	update-rust-restart-map test-rust-restart-map \
	update-rust-test-contracts test-rust-test-contracts \
	update-rust-test-scenario-coverage test-rust-test-scenario-coverage \
	update-rust-gap-witness-queue test-rust-gap-witness-queue \
	update-rust-gap-probe-seed-index test-rust-gap-probe-seed-index \
	update-rust-external-test-queue test-rust-external-test-queue \
	update-rust-seed-loader-readiness test-rust-seed-loader-readiness \
	update-rust-lift-bundle-plan test-rust-lift-bundle-plan \
	update-rust-external-test-patchset test-rust-external-test-patchset \
	update-rust-external-test-patch-shards test-rust-external-test-patch-shards \
	update-rust-external-test-patch-rehearsal test-rust-external-test-patch-rehearsal \
	update-rust-patch-prefix-frontier test-rust-patch-prefix-frontier \
	update-rust-comeback-card test-rust-comeback-card \
	update-rust-comeback-execution-card test-rust-comeback-execution-card \
	test-research-docs test-successor-safe-ceremony-receipt test-claim-classes \
	update-claim-matrix test-claim-matrix test-claim-register \
	update-claim-register-summary test-claim-register-summary \
	test-risk-register update-risk-register-summary test-risk-register-summary \
	test-cache-plan-contract

help:
	@echo "Concord command surface"
	@echo "  make doctor"
	@echo "  make cloudtainer-shadow-pass"
	@echo "  make cloudtainer-shadow-pass-list-budgets"
	@echo "  make cloudtainer-shadow-pass-short"
	@echo "  make cloudtainer-shadow-pass-medium"
	@echo "  make cloudtainer-shadow-pass-long"
	@echo "  make cloudtainer-shadow-pass-resume"
	@echo "  make test-cloudtainer-shadow-pass-resume"
	@echo "  make test-cloudtainer-shadow-pass-budget-profiles"
	@echo "  make update-cloudtainer-shadow-pass-frontier"
	@echo "  make test-cloudtainer-shadow-pass-frontier"
	@echo "  make update-cloudtainer-shadow-pass-history"
	@echo "  make test-cloudtainer-shadow-pass-history"
	@echo "  make update-cloudtainer-shadow-pass-volatility"
	@echo "  make test-cloudtainer-shadow-pass-volatility"
	@echo "  make update-cloudtainer-rust-recovery-card"
	@echo "  make test-cloudtainer-rust-recovery-card"
	@echo "  make update-cloudtainer-rust-probe-oracles"
	@echo "  make test-cloudtainer-rust-probe-oracles"
	@echo "  make show-cloudtainer-userspace-rustup-plan"
	@echo "  make update-cloudtainer-userspace-rustup-plan"
	@echo "  make test-cloudtainer-userspace-rustup-plan"
	@echo "  make update-cloudtainer-userspace-fetch-surface"
	@echo "  make test-cloudtainer-userspace-fetch-surface"
	@echo "  make update-cloudtainer-userspace-compile-surface"
	@echo "  make test-cloudtainer-userspace-compile-surface"
	@echo "  make update-cloudtainer-userspace-offline-proof-ladder"
	@echo "  make test-cloudtainer-userspace-offline-proof-ladder"
	@echo "  make update-cloudtainer-userspace-failure-resume-card"
	@echo "  make test-cloudtainer-userspace-failure-resume-card"
	@echo "  make update-cloudtainer-standing-bootstrap-delta"
	@echo "  make test-cloudtainer-standing-bootstrap-delta"
	@echo "  make update-archive-size-guardrail-card"
	@echo "  make test-archive-size-guardrail-card"
	@echo "  make update-archive-byte-triage-card"
	@echo "  make test-archive-byte-triage-card"
	@echo "  make update-archive-package-cut-card"
	@echo "  make test-archive-package-cut-card"
	@echo "  make update-archive-reentry-card"
	@echo "  make test-archive-reentry-card"
	@echo "  make update-archive-handoff-pack"
	@echo "  make test-archive-handoff-pack"
	@echo "  make verify-archive-handoff-pack"
	@echo "  make test-archive-handoff-pack-verify-tool"
	@echo "  make verify-authoritative-archive-zip"
	@echo "  make test-authoritative-archive-zip-verify-tool"
	@echo "  make update-archive-revision-cut-card"
	@echo "  make test-archive-revision-cut-card"
	@echo "  make update-archive-zip-lineage-card"
	@echo "  make test-archive-zip-lineage-card"
	@echo "  make update-archive-zip-chronology-card"
	@echo "  make test-archive-zip-chronology-card"
	@echo "  make update-archive-zip-authority-card"
	@echo "  make test-archive-zip-authority-card"
	@echo "  make update-archive-zip-digest-card"
	@echo "  make test-archive-zip-digest-card"
	@echo "  make update-archive-zip-size-truth-card"
	@echo "  make test-archive-zip-size-truth-card"
	@echo "  make plan-archive-revision-cut DESCRIPTOR=your-summary-slug"
	@echo "  make cut-archive-revision DESCRIPTOR=your-summary-slug SUMMARY=\"one-line summary\""
	@echo "  make settle-archive-truth"
	@echo "  make test-archive-truth-settle-tool"
	@echo "  make test-quick"
	@echo "  make test-full"
	@echo "  make gate"
	@echo "  make gate-strict"
	@echo "  make test-flake N=5"
	@echo "  make test-soak N=2"
	@echo "  make test-soak-async N=2"
	@echo "  make check-soak-status"
	@echo "  make test-spec-ledger-rollup"
	@echo "  make test-security-allowlist"
	@echo "  make test-examples-json"
	@echo "  make test-examples-unique-ids"
	@echo "  make test-required-examples"
	@echo "  make test-schema-json"
	@echo "  make test-policy-json"
	@echo "  make test-hooks-contract"
	@echo "  make test-artifact-gitkeeps"
	@echo "  make test-timing-artifacts"
	@echo "  make test-generated-docs"
	@echo "  make test-research-docs"
	@echo "  make test-successor-safe-ceremony-receipt"
	@echo "  make test-claim-classes"
	@echo "  make update-claim-matrix"
	@echo "  make test-claim-matrix"
	@echo "  make test-claim-register"
	@echo "  make update-claim-register-summary"
	@echo "  make test-claim-register-summary"
	@echo "  make test-risk-register"
	@echo "  make update-risk-register-summary"
	@echo "  make test-risk-register-summary"
	@echo "  make test-cache-plan-contract"
	@echo "  make test-zero-noise-rule-contract"
	@echo "  make test-doc-links"
	@echo "  make test-readme-commands"
	@echo "  make test-docs-index"
	@echo "  make test-release-doc"
	@echo "  make test-tranches"
	@echo "  make update-tranche-status"
	@echo "  make test-tranche-status"
	@echo "  make test-ci-smoke"
	@echo "  make test-policy-expirations"
	@echo "  make test-spec-evidence"
	@echo "  make test-make-help"
	@echo "  make test-scripts-exec"
	@echo "  make test-scripts-compile"
	@echo "  make test-artifact-layout"
	@echo "  make test-bypass-log"
	@echo "  make test-gitignore-policy"
	@echo "  make test-spec-dates"
	@echo "  make test-formal-smoke"
	@echo "  make test-formal-tools"
	@echo "  make update-experiment-catalog"
	@echo "  make test-experiment-catalog"
	@echo "  make update-command-inventory"
	@echo "  make test-command-inventory"
	@echo "  make update-validator-inventory"
	@echo "  make test-validator-inventory"
	@echo "  make update-rematch-world-benchmark-world-emission-card"
	@echo "  make test-rematch-world-benchmark-world-emission-card"
	@echo "  make update-rematch-world-benchmark-native-fill-map"
	@echo "  make test-rematch-world-benchmark-native-fill-map"
	@echo "  make update-rematch-world-benchmark-example-delta-ledger"
	@echo "  make test-rematch-world-benchmark-example-delta-ledger"
	@echo "  make update-rematch-world-benchmark-closeout-lifecycle-ledger"
	@echo "  make test-rematch-world-benchmark-closeout-lifecycle-ledger"
	@echo "  make update-rematch-world-benchmark-citation-witness-matrix"
	@echo "  make test-rematch-world-benchmark-citation-witness-matrix"
	@echo "  make update-rematch-world-benchmark-open-touchpoint-resolution-map"
	@echo "  make test-rematch-world-benchmark-open-touchpoint-resolution-map"
	@echo "  make update-rematch-world-benchmark-claim-frontier"
	@echo "  make test-rematch-world-benchmark-claim-frontier"
	@echo "  make update-rematch-world-benchmark-stage-yield-ledger"
	@echo "  make test-rematch-world-benchmark-stage-yield-ledger"
	@echo "  make update-rematch-world-benchmark-proof-budget-ledger"
	@echo "  make test-rematch-world-benchmark-proof-budget-ledger"
	@echo "  make update-policy-inventory"
	@echo "  make test-policy-inventory"
	@echo "  make update-schema-inventory"
	@echo "  make test-schema-inventory"
	@echo "  make update-artifact-buckets"
	@echo "  make test-artifact-buckets"
	@echo "  make update-rust-surface-inventory"
	@echo "  make test-rust-surface-inventory"
	@echo "  make update-rust-restart-map"
	@echo "  make test-rust-restart-map"
	@echo "  make update-rust-test-contracts"
	@echo "  make test-rust-test-contracts"
	@echo "  make update-rust-test-scenario-coverage"
	@echo "  make test-rust-test-scenario-coverage"
	@echo "  make update-rust-gap-witness-queue"
	@echo "  make test-rust-gap-witness-queue"
	@echo "  make update-rust-gap-probe-seed-index"
	@echo "  make test-rust-gap-probe-seed-index"
	@echo "  make update-rust-external-test-queue"
	@echo "  make test-rust-external-test-queue"
	@echo "  make update-rust-seed-loader-readiness"
	@echo "  make test-rust-seed-loader-readiness"
	@echo "  make update-rust-lift-bundle-plan"
	@echo "  make test-rust-lift-bundle-plan"
	@echo "  make update-rust-external-test-patchset"
	@echo "  make test-rust-external-test-patchset"
	@echo "  make update-rust-external-test-patch-shards"
	@echo "  make test-rust-external-test-patch-shards"
	@echo "  make update-rust-external-test-patch-rehearsal"
	@echo "  make test-rust-external-test-patch-rehearsal"
	@echo "  make update-rust-standing-bootstrap-guard"
	@echo "  make test-rust-standing-bootstrap-guard"
	@echo "  make update-rust-standing-bootstrap-guard-rehearsal"
	@echo "  make test-rust-standing-bootstrap-guard-rehearsal"
	@echo "  make update-rust-standing-bootstrap-repair-patch"
	@echo "  make test-rust-standing-bootstrap-repair-patch"
	@echo "  make update-rust-standing-bootstrap-repair-rehearsal"
	@echo "  make test-rust-standing-bootstrap-repair-rehearsal"
	@echo "  make update-rust-standing-bootstrap-integration-rehearsal"
	@echo "  make test-rust-standing-bootstrap-integration-rehearsal"
	@echo "  make update-rust-standing-bootstrap-comeback-bundle"
	@echo "  make test-rust-standing-bootstrap-comeback-bundle"
	@echo "  make update-rust-standing-bootstrap-comeback-bundle-rehearsal"
	@echo "  make test-rust-standing-bootstrap-comeback-bundle-rehearsal"
	@echo "  make update-rust-standing-bootstrap-post-patchset-bundle"
	@echo "  make test-rust-standing-bootstrap-post-patchset-bundle"
	@echo "  make update-rust-standing-bootstrap-post-patchset-bundle-rehearsal"
	@echo "  make test-rust-standing-bootstrap-post-patchset-bundle-rehearsal"
	@echo "  make update-rust-standing-bootstrap-state-selector"
	@echo "  make test-rust-standing-bootstrap-state-selector"
	@echo "  make update-rust-standing-bootstrap-state-selector-rehearsal"
	@echo "  make test-rust-standing-bootstrap-state-selector-rehearsal"
	@echo "  make update-rust-standing-bootstrap-route-equivalence"
	@echo "  make test-rust-standing-bootstrap-route-equivalence"
	@echo "  make update-rust-standing-bootstrap-verification-ladder"
	@echo "  make test-rust-standing-bootstrap-verification-ladder"
	@echo "  make update-rust-standing-bootstrap-verification-ladder-rehearsal"
	@echo "  make test-rust-standing-bootstrap-verification-ladder-rehearsal"
	@echo "  make update-rust-standing-bootstrap-checkpoints"
	@echo "  make test-rust-standing-bootstrap-checkpoints"
	@echo "  make update-rust-standing-bootstrap-checkpoints-rehearsal"
	@echo "  make test-rust-standing-bootstrap-checkpoints-rehearsal"
	@echo "  make update-rust-standing-bootstrap-checkpoint-verifier"
	@echo "  make test-rust-standing-bootstrap-checkpoint-verifier"
	@echo "  make update-rust-standing-bootstrap-checkpoint-verifier-rehearsal"
	@echo "  make test-rust-standing-bootstrap-checkpoint-verifier-rehearsal"
	@echo "  make test-rust-standing-bootstrap-checkpoint-verifier-tool"
	@echo "  make update-rust-patch-prefix-frontier"
	@echo "  make test-rust-patch-prefix-frontier"
	@echo "  make update-rust-comeback-card"
	@echo "  make test-rust-comeback-card"
	@echo "  make update-rust-comeback-execution-card"
	@echo "  make test-rust-comeback-execution-card"
	@echo "  make report-artifact-summary"
	@echo "  make test-reports-json"
	@echo "  make report-repro-bundle"
	@echo "  make test-release-manifest-schema"
	@echo "  make test-release-manifest-entries RELEASE_VERSION=dev"
	@echo "  make test-release-checksums RELEASE_VERSION=dev"
	@echo "  make test-timing-baseline MODE=full"
	@echo "  make release-manifest RELEASE_VERSION=dev"
	@echo "  make test-release-hygiene RELEASE_VERSION=dev"
	@echo "  make install-hooks"
	@echo "  make clean-test-artifacts"

# Environment + toolchain diagnostics.
doctor:
	@./scripts/doctor.sh

cloudtainer-shadow-pass:
	@python3 ./scripts/tools/cloudtainer_shadow_pass.py

cloudtainer-shadow-pass-list-budgets:
	@python3 ./scripts/tools/cloudtainer_shadow_pass.py --list-budget-profiles

cloudtainer-shadow-pass-short:
	@python3 ./scripts/tools/cloudtainer_shadow_pass.py --budget-profile short_budget

cloudtainer-shadow-pass-medium:
	@python3 ./scripts/tools/cloudtainer_shadow_pass.py --budget-profile medium_budget

cloudtainer-shadow-pass-long:
	@python3 ./scripts/tools/cloudtainer_shadow_pass.py --budget-profile long_budget

cloudtainer-shadow-pass-resume:
	@python3 ./scripts/tools/cloudtainer_shadow_pass.py --resume

test-cloudtainer-shadow-pass-resume:
	@python3 ./scripts/test/check_cloudtainer_shadow_pass_resume.py

test-cloudtainer-shadow-pass-budget-profiles:
	@python3 ./scripts/test/check_cloudtainer_shadow_pass_budget_profiles.py

update-cloudtainer-shadow-pass-frontier:
	@python3 ./scripts/report/build_cloudtainer_shadow_pass_frontier.py --write

test-cloudtainer-shadow-pass-frontier:
	@python3 ./scripts/report/build_cloudtainer_shadow_pass_frontier.py

update-cloudtainer-shadow-pass-history:
	@python3 ./scripts/report/build_cloudtainer_shadow_pass_history.py --write

test-cloudtainer-shadow-pass-history:
	@python3 ./scripts/test/check_cloudtainer_shadow_pass_history.py

update-cloudtainer-shadow-pass-volatility:
	@python3 ./scripts/report/build_cloudtainer_shadow_pass_volatility.py --write

test-cloudtainer-shadow-pass-volatility:
	@python3 ./scripts/test/check_cloudtainer_shadow_pass_volatility.py

update-cloudtainer-shadow-pass-budget-card:
	@python3 ./scripts/report/build_cloudtainer_shadow_pass_budget_card.py --write

test-cloudtainer-shadow-pass-budget-card:
	@python3 ./scripts/test/check_cloudtainer_shadow_pass_budget_card.py

update-cloudtainer-rust-recovery-card:
	@python3 ./scripts/report/build_cloudtainer_rust_recovery_card.py --write

test-cloudtainer-rust-recovery-card:
	@python3 ./scripts/test/check_cloudtainer_rust_recovery_card.py

update-cloudtainer-rust-probe-oracles:
	@python3 ./scripts/report/build_cloudtainer_rust_probe_oracles.py --write

test-cloudtainer-rust-probe-oracles:
	@python3 ./scripts/test/check_cloudtainer_rust_probe_oracles.py

show-cloudtainer-userspace-rustup-plan:
	@python3 ./scripts/tools/plan_userspace_rustup_comeback.py --emit shell

update-cloudtainer-userspace-rustup-plan:
	@python3 ./scripts/report/build_cloudtainer_userspace_rustup_plan.py --write

test-cloudtainer-userspace-rustup-plan:
	@python3 ./scripts/test/check_cloudtainer_userspace_rustup_plan.py

update-cloudtainer-userspace-fetch-surface:
	@python3 ./scripts/report/build_cloudtainer_userspace_fetch_surface.py --write

test-cloudtainer-userspace-fetch-surface:
	@python3 ./scripts/test/check_cloudtainer_userspace_fetch_surface.py

update-cloudtainer-userspace-compile-surface:
	@python3 ./scripts/report/build_cloudtainer_userspace_compile_surface.py --write

test-cloudtainer-userspace-compile-surface:
	@python3 ./scripts/test/check_cloudtainer_userspace_compile_surface.py

update-cloudtainer-userspace-offline-proof-ladder:
	@python3 ./scripts/report/build_cloudtainer_userspace_offline_proof_ladder.py --write

test-cloudtainer-userspace-offline-proof-ladder:
	@python3 ./scripts/test/check_cloudtainer_userspace_offline_proof_ladder.py

update-cloudtainer-userspace-failure-resume-card:
	@python3 ./scripts/report/build_cloudtainer_userspace_failure_resume_card.py --write

test-cloudtainer-userspace-failure-resume-card:
	@python3 ./scripts/test/check_cloudtainer_userspace_failure_resume_card.py

update-cloudtainer-standing-bootstrap-delta:
	@python3 ./scripts/report/build_cloudtainer_standing_bootstrap_delta.py --write

test-cloudtainer-standing-bootstrap-delta:
	@python3 ./scripts/test/check_cloudtainer_standing_bootstrap_delta.py

update-archive-size-guardrail-card:
	@python3 ./scripts/report/build_archive_size_guardrail_card.py --write

test-archive-size-guardrail-card:
	@python3 ./scripts/test/check_archive_size_guardrail_card.py

update-archive-byte-triage-card:
	@python3 ./scripts/report/build_archive_size_guardrail_card.py --write
	@python3 ./scripts/report/build_archive_byte_triage_card.py --write

test-archive-byte-triage-card:
	@python3 ./scripts/test/check_archive_byte_triage_card.py

update-archive-package-cut-card:
	@python3 ./scripts/report/build_archive_package_cut_card.py --write

test-archive-package-cut-card:
	@python3 ./scripts/test/check_archive_package_cut_card.py

update-archive-reentry-card:
	@python3 ./scripts/report/build_archive_reentry_card.py --write

test-archive-reentry-card:
	@python3 ./scripts/test/check_archive_reentry_card.py

update-archive-handoff-pack:
	@python3 ./scripts/report/build_archive_handoff_pack.py --write

test-archive-handoff-pack:
	@python3 ./scripts/test/check_archive_handoff_pack.py

verify-archive-handoff-pack:
	@python3 ./scripts/tools/verify_archive_handoff_pack.py

test-archive-handoff-pack-verify-tool:
	@python3 ./scripts/test/check_archive_handoff_pack_verify_tool.py

verify-authoritative-archive-zip:
	@python3 ./scripts/tools/verify_authoritative_archive_zip.py

test-authoritative-archive-zip-verify-tool:
	@python3 ./scripts/test/check_authoritative_archive_zip_verify_tool.py

update-archive-revision-cut-card:
	@python3 ./scripts/report/build_archive_revision_cut_card.py --write

test-archive-revision-cut-card:
	@python3 ./scripts/test/check_archive_revision_cut_card.py

update-archive-zip-lineage-card:
	@python3 ./scripts/report/build_archive_zip_lineage_card.py --write

test-archive-zip-lineage-card:
	@python3 ./scripts/test/check_archive_zip_lineage_card.py

update-archive-zip-chronology-card:
	@python3 ./scripts/report/build_archive_zip_chronology_card.py --write

test-archive-zip-chronology-card:
	@python3 ./scripts/test/check_archive_zip_chronology_card.py

update-archive-zip-authority-card:
	@python3 ./scripts/report/build_archive_zip_authority_card.py --write

test-archive-zip-authority-card:
	@python3 ./scripts/test/check_archive_zip_authority_card.py

update-archive-zip-digest-card:
	@python3 ./scripts/report/build_archive_zip_digest_card.py


test-archive-zip-digest-card:
	@python3 ./scripts/test/check_archive_zip_digest_card.py

update-archive-zip-size-truth-card:
	@python3 ./scripts/report/build_archive_zip_size_truth_card.py


test-archive-zip-size-truth-card:
	@python3 ./scripts/test/check_archive_zip_size_truth_card.py

plan-archive-revision-cut:
	@args=(--descriptor "$${DESCRIPTOR:-your-summary-slug}"); \
	if [[ -n "$${STAMP:-}" ]]; then args+=(--timestamp "$${STAMP}"); fi; \
	python3 ./scripts/tools/plan_archive_revision_cut.py "$${args[@]}"

cut-archive-revision:
	@test -n "$${DESCRIPTOR:-}" || (echo "cut-archive-revision: DESCRIPTOR is required" >&2; exit 1)
	@test -n "$${SUMMARY:-}" || (echo "cut-archive-revision: SUMMARY is required" >&2; exit 1)
	@args=(--descriptor "$${DESCRIPTOR}" --summary "$${SUMMARY}"); \
	if [[ -n "$${STAMP:-}" ]]; then args+=(--timestamp "$${STAMP}"); fi; \
	if [[ -n "$${ZIP_DIR:-}" ]]; then args+=(--zip-dir "$${ZIP_DIR}"); fi; \
	python3 ./scripts/tools/cut_archive_revision.py "$${args[@]}"

settle-archive-truth:
	@python3 -u ./scripts/tools/settle_archive_truth.py

test-archive-truth-settle-tool:
	@python3 ./scripts/test/check_archive_truth_settle_tool.py

test-archive-revision-cut-tool:
	@python3 ./scripts/test/check_archive_revision_cut_tool.py

# Fast feedback loop. Designed to stay cheap and deterministic.
test-quick:
	@./scripts/test/run_harness.sh quick

# Full local confidence loop (still deterministic).
test-full:
	@./scripts/test/run_harness.sh full

# Safe artifact cleanup (dry-run by default unless overridden).
clean-test-artifacts:
	@./scripts/cleanup_artifacts.sh --dry-run

test-goldens:
	@python3 ./scripts/validate_golden_registry.py

test-spec-ledger:
	@python3 ./scripts/validate_spec_ledger.py

test-spec-ledger-rollup:
	@python3 ./scripts/report/check_spec_ledger_rollup.py

test-examples-json:
	@python3 ./scripts/test/check_examples_json.py

test-examples-unique-ids:
	@python3 ./scripts/test/check_examples_unique_ids.py

test-required-examples:
	@python3 ./scripts/test/check_required_examples.py

test-schema-json:
	@python3 ./scripts/test/check_schema_json_valid.py

test-policy-json:
	@python3 ./scripts/test/check_policy_json_valid.py

test-hooks-contract:
	@python3 ./scripts/test/check_hooks_contract.py

test-artifact-gitkeeps:
	@python3 ./scripts/test/check_artifact_gitkeeps.py

test-timing-artifacts:
	@python3 ./scripts/test/check_timing_artifacts_presence.py

test-generated-docs:
	@python3 ./scripts/test/check_generated_docs_presence.py

test-doc-links:
	@python3 ./scripts/test/check_markdown_links.py

test-readme-commands:
	@python3 ./scripts/test/check_readme_command_surface.py

test-docs-index:
	@python3 ./scripts/test/check_docs_index_core.py

test-research-docs:
	@python3 ./scripts/test/check_research_docs.py

test-successor-safe-ceremony-receipt:
	@python3 ./scripts/test/check_successor_safe_ceremony_receipt.py

test-claim-classes:
	@python3 ./scripts/test/check_claim_classes.py

update-claim-matrix:
	@python3 ./scripts/report/build_claim_matrix.py --write

test-claim-matrix:
	@python3 ./scripts/report/build_claim_matrix.py

test-claim-register:
	@python3 ./scripts/test/check_claim_register.py

update-claim-register-summary:
	@python3 ./scripts/report/build_claim_register_summary.py --write

test-claim-register-summary:
	@python3 ./scripts/report/build_claim_register_summary.py

test-risk-register:
	@python3 ./scripts/test/check_risk_register.py

update-risk-register-summary:
	@python3 ./scripts/report/build_risk_register_summary.py --write

test-risk-register-summary:
	@python3 ./scripts/report/build_risk_register_summary.py

test-cache-plan-contract:
	@python3 ./scripts/test/check_rematch_cache_plan_contract.py

test-zero-noise-rule-contract:
	@python3 ./scripts/test/check_rematch_zero_noise_rule_contract.py

test-release-doc:
	@python3 ./scripts/test/check_release_doc_commands.py

test-tranches:
	@python3 ./scripts/test/check_tranches_complete.py

update-tranche-status:
	@python3 ./scripts/report/build_tranche_status.py --write

test-tranche-status:
	@python3 ./scripts/report/build_tranche_status.py

test-ci-smoke:
	@python3 ./scripts/test/check_ci_smoke.py

test-policy-expirations:
	@python3 ./scripts/test/check_policy_expirations.py

test-spec-evidence:
	@python3 ./scripts/test/check_spec_evidence_links.py

test-make-help:
	@python3 ./scripts/test/check_make_help_surface.py

test-scripts-exec:
	@python3 ./scripts/test/check_scripts_executable.py

test-scripts-compile:
	@python3 ./scripts/test/check_scripts_compile.py

test-artifact-layout:
	@python3 ./scripts/test/check_artifact_layout.py

test-bypass-log:
	@python3 ./scripts/test/check_bypass_log.py

test-gitignore-policy:
	@python3 ./scripts/test/check_gitignore_artifacts_policy.py

test-spec-dates:
	@python3 ./scripts/test/check_spec_dates.py

test-adr:
	@python3 ./scripts/validate_adr.py

test-process-hygiene:
	@./scripts/procctl.sh hygiene

test-format-check:
	@./scripts/tools/format_check

# Non-strict security checks via adapter interface.
test-security:
	@./scripts/tools/security_scan
	@./scripts/tools/license_check

# Strict flavor: same adapters, but expected to fail if policy is violated.
test-security-strict:
	@STRICT=1 ./scripts/tools/security_scan
	@STRICT=1 ./scripts/tools/license_check

test-security-allowlist:
	@python3 ./scripts/security/check_allowlist.py

test-timing-baseline:
	@MODE=$${MODE:-full}; python3 ./scripts/test/check_timing_regression.py "$$MODE"

test-formal-smoke:
	@python3 ./scripts/formal/check_certify_invariants.py

test-formal-tools:
	@python3 ./scripts/formal/check_formal_tooling.py

update-experiment-catalog:
	@python3 ./scripts/report/build_experiment_catalog.py --write

test-experiment-catalog:
	@python3 ./scripts/report/build_experiment_catalog.py

update-command-inventory:
	@python3 ./scripts/report/build_command_inventory.py --write

test-command-inventory:
	@python3 ./scripts/report/build_command_inventory.py

update-validator-inventory:
	@python3 ./scripts/report/build_validator_inventory.py --write

test-validator-inventory:
	@python3 ./scripts/report/build_validator_inventory.py

update-policy-inventory:
	@python3 ./scripts/report/build_policy_inventory.py --write

test-policy-inventory:
	@python3 ./scripts/report/build_policy_inventory.py

update-schema-inventory:
	@python3 ./scripts/report/build_schema_inventory.py --write

test-schema-inventory:
	@python3 ./scripts/report/build_schema_inventory.py

update-artifact-buckets:
	@python3 ./scripts/report/build_artifact_bucket_inventory.py --write

test-artifact-buckets:
	@python3 ./scripts/report/build_artifact_bucket_inventory.py

update-rematch-world-benchmark-world-emission-card:
	@python3 ./scripts/report/build_rematch_world_benchmark_world_emission_card.py

test-rematch-world-benchmark-world-emission-card:
	@python3 ./scripts/test/check_rematch_world_benchmark_world_emission_card.py

update-rematch-world-benchmark-native-fill-map:
	@python3 ./scripts/report/build_rematch_world_benchmark_native_fill_map.py

test-rematch-world-benchmark-native-fill-map:
	@python3 ./scripts/test/check_rematch_world_benchmark_native_fill_map.py

update-rematch-world-benchmark-example-delta-ledger:
	@python3 ./scripts/report/build_rematch_world_benchmark_example_delta_ledger.py

test-rematch-world-benchmark-example-delta-ledger:
	@python3 ./scripts/test/check_rematch_world_benchmark_example_delta_ledger.py

update-rematch-world-benchmark-closeout-lifecycle-ledger:
	@python3 ./scripts/report/build_rematch_world_benchmark_closeout_lifecycle_ledger.py

test-rematch-world-benchmark-closeout-lifecycle-ledger:
	@python3 ./scripts/test/check_rematch_world_benchmark_closeout_lifecycle_ledger.py

update-rematch-world-benchmark-citation-witness-matrix:
	@python3 ./scripts/report/build_rematch_world_benchmark_citation_witness_matrix.py

test-rematch-world-benchmark-citation-witness-matrix:
	@python3 ./scripts/test/check_rematch_world_benchmark_citation_witness_matrix.py

update-rematch-world-benchmark-open-touchpoint-resolution-map:
	@python3 ./scripts/report/build_rematch_world_benchmark_open_touchpoint_resolution_map.py

test-rematch-world-benchmark-open-touchpoint-resolution-map:
	@python3 ./scripts/test/check_rematch_world_benchmark_open_touchpoint_resolution_map.py

update-rematch-world-benchmark-claim-frontier:
	@python3 ./scripts/report/build_rematch_world_benchmark_claim_frontier.py

test-rematch-world-benchmark-claim-frontier:
	@python3 ./scripts/test/check_rematch_world_benchmark_claim_frontier.py

update-rematch-world-benchmark-stage-yield-ledger:
	@python3 ./scripts/report/build_rematch_world_benchmark_stage_yield_ledger.py

test-rematch-world-benchmark-stage-yield-ledger:
	@python3 ./scripts/test/check_rematch_world_benchmark_stage_yield_ledger.py

update-rematch-world-benchmark-proof-budget-ledger:
	@python3 ./scripts/report/build_rematch_world_benchmark_proof_budget_ledger.py

test-rematch-world-benchmark-proof-budget-ledger:
	@python3 ./scripts/test/check_rematch_world_benchmark_proof_budget_ledger.py

update-rust-surface-inventory:
	@python3 ./scripts/report/build_rust_surface_inventory.py --write

test-rust-surface-inventory:
	@python3 ./scripts/report/build_rust_surface_inventory.py

update-rust-restart-map:
	@python3 ./scripts/report/build_rust_restart_map.py --write

test-rust-restart-map:
	@python3 ./scripts/report/build_rust_restart_map.py

update-rust-test-contracts:
	@python3 ./scripts/report/build_rust_test_contracts.py --write

test-rust-test-contracts:
	@python3 ./scripts/report/build_rust_test_contracts.py

update-rust-test-scenario-coverage:
	@python3 ./scripts/report/build_rust_test_scenario_coverage.py --write

test-rust-test-scenario-coverage:
	@python3 ./scripts/report/build_rust_test_scenario_coverage.py

update-rust-gap-witness-queue:
	@python3 ./scripts/report/build_rust_gap_witness_queue.py --write

test-rust-gap-witness-queue:
	@python3 ./scripts/report/build_rust_gap_witness_queue.py

update-rust-gap-probe-seed-index:
	@python3 ./scripts/report/build_rust_gap_probe_seed_index.py --write

test-rust-gap-probe-seed-index:
	@python3 ./scripts/report/build_rust_gap_probe_seed_index.py

update-rust-external-test-queue:
	@python3 ./scripts/report/build_rust_external_test_queue.py --write

test-rust-external-test-queue:
	@python3 ./scripts/report/build_rust_external_test_queue.py

update-rust-seed-loader-readiness:
	@python3 ./scripts/report/build_rust_seed_loader_readiness.py --write

test-rust-seed-loader-readiness:
	@python3 ./scripts/report/build_rust_seed_loader_readiness.py

update-rust-lift-bundle-plan:
	@python3 ./scripts/report/build_rust_lift_bundle_plan.py --write

test-rust-lift-bundle-plan:
	@python3 ./scripts/report/build_rust_lift_bundle_plan.py

update-rust-external-test-patchset:
	@python3 ./scripts/report/build_rust_external_test_patchset.py --write

test-rust-external-test-patchset:
	@python3 ./scripts/report/build_rust_external_test_patchset.py

update-rust-external-test-patch-shards:
	@python3 ./scripts/report/build_rust_external_test_patch_shards.py --write

test-rust-external-test-patch-shards:
	@python3 ./scripts/report/build_rust_external_test_patch_shards.py

update-rust-external-test-patch-rehearsal:
	@python3 ./scripts/report/build_rust_external_test_patch_rehearsal.py --write

test-rust-external-test-patch-rehearsal:
	@python3 ./scripts/report/build_rust_external_test_patch_rehearsal.py

update-rust-standing-bootstrap-guard:
	@python3 ./scripts/report/build_rust_standing_bootstrap_guard.py --write

test-rust-standing-bootstrap-guard:
	@python3 ./scripts/report/build_rust_standing_bootstrap_guard.py

update-rust-standing-bootstrap-guard-rehearsal:
	@python3 ./scripts/report/build_rust_standing_bootstrap_guard_rehearsal.py --write

test-rust-standing-bootstrap-guard-rehearsal:
	@python3 ./scripts/report/build_rust_standing_bootstrap_guard_rehearsal.py

update-rust-standing-bootstrap-repair-patch:
	@python3 ./scripts/report/build_rust_standing_bootstrap_repair_patch.py --write

test-rust-standing-bootstrap-repair-patch:
	@python3 ./scripts/report/build_rust_standing_bootstrap_repair_patch.py

update-rust-standing-bootstrap-repair-rehearsal:
	@python3 ./scripts/report/build_rust_standing_bootstrap_repair_rehearsal.py --write

test-rust-standing-bootstrap-repair-rehearsal:
	@python3 ./scripts/report/build_rust_standing_bootstrap_repair_rehearsal.py

update-rust-standing-bootstrap-integration-rehearsal:
	@python3 ./scripts/report/build_rust_standing_bootstrap_integration_rehearsal.py --write

test-rust-standing-bootstrap-integration-rehearsal:
	@python3 ./scripts/report/build_rust_standing_bootstrap_integration_rehearsal.py

update-rust-standing-bootstrap-comeback-bundle:
	@python3 ./scripts/report/build_rust_standing_bootstrap_comeback_bundle.py --write

test-rust-standing-bootstrap-comeback-bundle:
	@python3 ./scripts/report/build_rust_standing_bootstrap_comeback_bundle.py

update-rust-standing-bootstrap-comeback-bundle-rehearsal:
	@python3 ./scripts/report/build_rust_standing_bootstrap_comeback_bundle_rehearsal.py --write

test-rust-standing-bootstrap-comeback-bundle-rehearsal:
	@python3 ./scripts/report/build_rust_standing_bootstrap_comeback_bundle_rehearsal.py

update-rust-standing-bootstrap-post-patchset-bundle:
	@python3 ./scripts/report/build_rust_standing_bootstrap_post_patchset_bundle.py --write

test-rust-standing-bootstrap-post-patchset-bundle:
	@python3 ./scripts/report/build_rust_standing_bootstrap_post_patchset_bundle.py

update-rust-standing-bootstrap-post-patchset-bundle-rehearsal:
	@python3 ./scripts/report/build_rust_standing_bootstrap_post_patchset_bundle_rehearsal.py --write

test-rust-standing-bootstrap-post-patchset-bundle-rehearsal:
	@python3 ./scripts/report/build_rust_standing_bootstrap_post_patchset_bundle_rehearsal.py

update-rust-standing-bootstrap-state-selector:
	@python3 ./scripts/report/build_rust_standing_bootstrap_state_selector.py --write

test-rust-standing-bootstrap-state-selector:
	@python3 ./scripts/report/build_rust_standing_bootstrap_state_selector.py

update-rust-standing-bootstrap-state-selector-rehearsal:
	@python3 ./scripts/report/build_rust_standing_bootstrap_state_selector_rehearsal.py --write

test-rust-standing-bootstrap-state-selector-rehearsal:
	@python3 ./scripts/report/build_rust_standing_bootstrap_state_selector_rehearsal.py

update-rust-standing-bootstrap-route-equivalence:
	@python3 ./scripts/report/build_rust_standing_bootstrap_route_equivalence.py --write

test-rust-standing-bootstrap-route-equivalence:
	@python3 ./scripts/report/build_rust_standing_bootstrap_route_equivalence.py

update-rust-standing-bootstrap-execution-card:
	@python3 ./scripts/report/build_rust_standing_bootstrap_execution_card.py --write

test-rust-standing-bootstrap-execution-card:
	@python3 ./scripts/report/build_rust_standing_bootstrap_execution_card.py

update-rust-standing-bootstrap-execution-rehearsal:
	@python3 ./scripts/report/build_rust_standing_bootstrap_execution_rehearsal.py --write

test-rust-standing-bootstrap-execution-rehearsal:
	@python3 ./scripts/report/build_rust_standing_bootstrap_execution_rehearsal.py

update-rust-standing-bootstrap-verification-ladder:
	@python3 ./scripts/report/build_rust_standing_bootstrap_verification_ladder.py --write

test-rust-standing-bootstrap-verification-ladder:
	@python3 ./scripts/report/build_rust_standing_bootstrap_verification_ladder.py

update-rust-standing-bootstrap-verification-ladder-rehearsal:
	@python3 ./scripts/report/build_rust_standing_bootstrap_verification_ladder_rehearsal.py --write

test-rust-standing-bootstrap-verification-ladder-rehearsal:
	@python3 ./scripts/report/build_rust_standing_bootstrap_verification_ladder_rehearsal.py

update-rust-standing-bootstrap-checkpoints:
	@python3 ./scripts/report/build_rust_standing_bootstrap_checkpoints.py --write

test-rust-standing-bootstrap-checkpoints:
	@python3 ./scripts/report/build_rust_standing_bootstrap_checkpoints.py

update-rust-standing-bootstrap-checkpoints-rehearsal:
	@python3 ./scripts/report/build_rust_standing_bootstrap_checkpoints_rehearsal.py --write

test-rust-standing-bootstrap-checkpoints-rehearsal:
	@python3 ./scripts/report/build_rust_standing_bootstrap_checkpoints_rehearsal.py

update-rust-standing-bootstrap-checkpoint-verifier:
	@python3 ./scripts/report/build_rust_standing_bootstrap_checkpoint_verifier.py --write

test-rust-standing-bootstrap-checkpoint-verifier:
	@python3 ./scripts/report/build_rust_standing_bootstrap_checkpoint_verifier.py

update-rust-standing-bootstrap-checkpoint-verifier-rehearsal:
	@python3 ./scripts/report/build_rust_standing_bootstrap_checkpoint_verifier_rehearsal.py --write

test-rust-standing-bootstrap-checkpoint-verifier-rehearsal:
	@python3 ./scripts/report/build_rust_standing_bootstrap_checkpoint_verifier_rehearsal.py

test-rust-standing-bootstrap-checkpoint-verifier-tool:
	@python3 ./scripts/test/check_rust_standing_bootstrap_checkpoint_verifier_tool.py

update-rust-patch-prefix-frontier:
	@python3 ./scripts/report/build_rust_patch_prefix_frontier.py --write

test-rust-patch-prefix-frontier:
	@python3 ./scripts/report/build_rust_patch_prefix_frontier.py

update-rust-comeback-card:
	@python3 ./scripts/report/build_rust_comeback_card.py --write

test-rust-comeback-card:
	@python3 ./scripts/test/check_rust_comeback_card.py

update-rust-comeback-execution-card:
	@python3 ./scripts/report/build_rust_comeback_execution_card.py --write

test-rust-comeback-execution-card:
	@python3 ./scripts/test/check_rust_comeback_execution_card.py

report-artifact-summary:
	@python3 ./scripts/report/summarize_artifacts.py

test-reports-json:
	@python3 ./scripts/test/check_reports_json_valid.py

report-repro-bundle:
	@python3 ./scripts/report/build_repro_bundle_index.py

release-manifest:
	@VER=$${RELEASE_VERSION:-dev}; ./scripts/release/generate_manifest.sh "$$VER"

test-release-hygiene:
	@VER=$${RELEASE_VERSION:-dev}; RELEASE_VERSION="$$VER" ./scripts/release/check_release_hygiene.sh

test-release-manifest-schema:
	@python3 ./scripts/release/check_release_manifest_schema.py

test-release-manifest-entries:
	@VER=$${RELEASE_VERSION:-dev}; python3 ./scripts/test/check_release_manifest_entries.py "$$VER"

test-release-checksums:
	@VER=$${RELEASE_VERSION:-dev}; python3 ./scripts/release/check_release_checksums.py "$$VER"

install-hooks:
	@./scripts/hooks/install.sh

# M1 integration gate: deterministic tests + governance + non-strict security.
gate: test-full test-timing-baseline test-timing-artifacts test-goldens test-spec-ledger test-spec-ledger-rollup test-spec-dates test-spec-evidence test-adr test-process-hygiene test-ci-smoke test-policy-json test-policy-expirations test-examples-json test-examples-unique-ids test-required-examples test-doc-links test-readme-commands test-docs-index test-research-docs test-successor-safe-ceremony-receipt test-claim-classes test-claim-matrix test-claim-register test-claim-register-summary test-risk-register test-risk-register-summary test-release-doc test-tranches test-tranche-status test-make-help test-scripts-exec test-scripts-compile test-schema-json test-hooks-contract test-artifact-layout test-artifact-gitkeeps test-bypass-log test-gitignore-policy test-formal-smoke test-formal-tools test-experiment-catalog test-command-inventory test-validator-inventory test-policy-inventory test-schema-inventory test-generated-docs test-security-allowlist test-security report-artifact-summary report-repro-bundle test-artifact-buckets test-reports-json test-cache-plan-contract
	@echo "gate: ok"

# M2-ready strict gate (kept lean until release posture is required).
gate-strict: gate test-security-strict test-release-manifest-schema
	@./scripts/tools/sbom_generate
	@echo "gate-strict: ok"

test-flake:
	@N=$${N:-5}; ./scripts/test/flake_loop.sh "$${N}" quick

test-soak:
	@N=$${N:-2}; ./scripts/test/soak_loop.sh "$${N}" full

test-soak-async:
	@mkdir -p artifacts/timing
	@N=$${N:-2}; nohup ./scripts/test/soak_loop.sh "$${N}" full > artifacts/timing/soak_async.log 2>&1 & echo $$! > artifacts/timing/soak_async.pid
	@echo "started soak async pid=$$(cat artifacts/timing/soak_async.pid)"

check-soak-status:
	@./scripts/test/check_async_status.sh artifacts/timing/soak_async.pid artifacts/timing/soak_async.log

stop-soak-async:
	@./scripts/test/stop_async.sh artifacts/timing/soak_async.pid
