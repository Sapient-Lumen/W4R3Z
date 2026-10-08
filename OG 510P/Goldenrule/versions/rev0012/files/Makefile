SHELL := /usr/bin/env bash

export TZ := UTC
export LANG := C
export LC_ALL := C
export PYTHONHASHSEED := 0
export TEST_SEED ?= 424242
export NO_NETWORK ?= 1

.PHONY: help doctor test-quick test-full clean-test-artifacts gate gate-strict \
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
	test-artifact-buckets test-research-docs test-claim-classes \
	update-claim-matrix test-claim-matrix test-claim-register \
	update-claim-register-summary test-claim-register-summary \
	test-risk-register update-risk-register-summary test-risk-register-summary \
	test-cache-plan-contract

help:
	@echo "Concord command surface"
	@echo "  make doctor"
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
	@echo "  make update-policy-inventory"
	@echo "  make test-policy-inventory"
	@echo "  make update-schema-inventory"
	@echo "  make test-schema-inventory"
	@echo "  make update-artifact-buckets"
	@echo "  make test-artifact-buckets"
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
gate: test-full test-timing-baseline test-timing-artifacts test-goldens test-spec-ledger test-spec-ledger-rollup test-spec-dates test-spec-evidence test-adr test-process-hygiene test-ci-smoke test-policy-json test-policy-expirations test-examples-json test-examples-unique-ids test-required-examples test-doc-links test-readme-commands test-docs-index test-research-docs test-claim-classes test-claim-matrix test-claim-register test-claim-register-summary test-risk-register test-risk-register-summary test-release-doc test-tranches test-tranche-status test-make-help test-scripts-exec test-scripts-compile test-schema-json test-hooks-contract test-artifact-layout test-artifact-gitkeeps test-bypass-log test-gitignore-policy test-formal-smoke test-formal-tools test-experiment-catalog test-command-inventory test-validator-inventory test-policy-inventory test-schema-inventory test-generated-docs test-security-allowlist test-security report-artifact-summary report-repro-bundle test-artifact-buckets test-reports-json test-cache-plan-contract
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
