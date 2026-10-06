REV := $(shell node -e "import('./src/browserrt.mjs').then(m=>process.stdout.write(m.REVISION))")
PFX := $(shell node -e "import('./src/browserrt.mjs').then(m=>process.stdout.write('REV'+m.REVISION.slice(3)))")

.PHONY: lint test test-fast test-release test-list test-resilience test-circuit-breaker-bulkhead audit-circuit-breaker-bulkhead test-circuit-breaker-bulkhead-model audit-circuit-breaker-bulkhead-model audit audit-cube audit-deep test-affected affected-dryrun test-full proof turn-start plan capability timing-history context-pack package-release verify-release test-browser test-browser-boot test-browser-opfs test-browser-opfs-sync test-browser-opfs-block-store test-browser-opfs-storage-lane test-browser-sab test-browser-sab-frame test-scheduler test-storage-lane-retry-budget-model test-provider-resilience-model audit-provider-resilience-model audit-opfs-provider audit-opfs-storage-lane

lint:
	python3 tools/check_cube.py
	node tools/run_tests.mjs --tier release --jobs 1 --json artifacts/validation/$(PFX)-TEST-HARNESS-RUN.json
	node tools/update_timing_history.mjs --report artifacts/validation/$(PFX)-TEST-HARNESS-RUN.json --out artifacts/validation/$(PFX)-TEST-TIMING-HISTORY.json
	python3 tools/check_cube.py

test: test-release

test-fast:
	node tools/run_tests.mjs --tier smoke --jobs auto

test-release:
	node tools/run_tests.mjs --tier release --jobs 1 --json artifacts/validation/$(PFX)-TEST-HARNESS-RUN.json

test-list:
	node tools/run_tests.mjs --list --tier release

test-resilience:
	node tools/run_tests.mjs --tier release --id scheduler:circuit-breaker-bulkhead-proof,scheduler:circuit-breaker-bulkhead-model-proof,facility:circuit-breaker-bulkhead-contract-audit,facility:circuit-breaker-bulkhead-model-contract-audit,scheduler:provider-resilience-history-proof,scheduler:provider-resilience-model-proof,facility:provider-resilience-history-contract-audit,facility:provider-resilience-model-contract-audit --jobs 1

test-circuit-breaker-bulkhead:
	node tools/circuit_breaker_bulkhead_probe.mjs --json artifacts/validation/$(PFX)-CIRCUIT-BREAKER-BULKHEAD-PROBE.json

audit-circuit-breaker-bulkhead:
	node tools/circuit_breaker_bulkhead_contract_audit.mjs --json artifacts/audit/$(PFX)-CIRCUIT-BREAKER-BULKHEAD-CONTRACT-AUDIT.json


test-circuit-breaker-bulkhead-model:
	node tools/circuit_breaker_bulkhead_model_probe.mjs --json artifacts/validation/$(PFX)-CIRCUIT-BREAKER-BULKHEAD-MODEL-PROBE.json

audit-circuit-breaker-bulkhead-model:
	node tools/circuit_breaker_bulkhead_model_contract_audit.mjs --json artifacts/audit/$(PFX)-CIRCUIT-BREAKER-BULKHEAD-MODEL-CONTRACT-AUDIT.json

test-scheduler:
	node tools/run_tests.mjs --tier release --id scheduler:adaptive-concurrency-proof,scheduler:priority-fairness-proof,scheduler:cross-lane-contract-proof,scheduler:cross-lane-model-walk-proof,scheduler:storage-lane-provider-proof,scheduler:storage-lane-model-walk-proof,scheduler:storage-lane-retry-policy-proof,scheduler:storage-lane-retry-budget-proof,scheduler:storage-lane-retry-budget-model-proof,scheduler:circuit-breaker-bulkhead-proof,scheduler:circuit-breaker-bulkhead-model-proof,facility:circuit-breaker-bulkhead-contract-audit,facility:circuit-breaker-bulkhead-model-contract-audit,scheduler:provider-resilience-history-proof,scheduler:provider-resilience-model-proof,facility:provider-resilience-history-contract-audit,facility:provider-resilience-model-contract-audit --jobs 1

test-storage-lane-retry-budget-model:
	node tools/storage_lane_retry_budget_model_probe.mjs --json artifacts/validation/$(PFX)-STORAGE-LANE-RETRY-BUDGET-MODEL-PROBE.json


test-provider-resilience-model:
	node tools/provider_resilience_model_probe.mjs --json artifacts/validation/$(PFX)-PROVIDER-RESILIENCE-MODEL-PROBE.json

audit-provider-resilience-model:
	node tools/provider_resilience_model_contract_audit.mjs --json artifacts/audit/$(PFX)-PROVIDER-RESILIENCE-MODEL-CONTRACT-AUDIT.json

audit:
	node tools/audit_cube_surfaces.mjs --json artifacts/audit/$(PFX)-CUBE-AUDIT.json
	node tools/deep_cube_audit.mjs --json artifacts/audit/$(PFX)-DEEP-CUBE-AUDIT.json

audit-cube: audit

audit-deep:
	node tools/deep_cube_audit.mjs --json artifacts/audit/$(PFX)-DEEP-CUBE-AUDIT.json

test-affected:
	@test -n "$(CHANGED)" || (echo "CHANGED is required, e.g. CHANGED=src/browserrt.mjs" && exit 1)
	node tools/run_tests.mjs --tier release --changed "$(CHANGED)" --only-affected --jobs auto

affected-dryrun:
	node tools/run_tests.mjs --tier release --changed tools/run_tests.mjs --only-affected --dry-run --json artifacts/validation/$(PFX)-AFFECTED-RUNNER-DRYRUN.json

test-full:
	node tools/run_tests.mjs --tier full --jobs auto

plan:
	node tools/plan_tests.mjs --tier release --changed src/opfs-storage-lane-adapter.mjs,tools/browser_opfs_storage_lane_adapter_probe.mjs,tools/opfs_storage_lane_adapter_contract_audit.mjs,test/manifest.json --json artifacts/validation/$(PFX)-TEST-PLAN-SANITY.json

capability:
	node tools/capability_survey.mjs --json artifacts/validation/$(PFX)-CAPABILITY-SURVEY.json

timing-history:
	node tools/update_timing_history.mjs --report artifacts/validation/$(PFX)-TEST-HARNESS-RUN.json --out artifacts/validation/$(PFX)-TEST-TIMING-HISTORY.json

proof:
	node tools/run_current_proof.mjs --write

turn-start:
	node tools/turn_bootstrap.mjs --write

context-pack:
	python3 tools/make_context_pack.py

package-release:
	@test -n "$(STAMP)" || (echo "STAMP is required: YYYY.MM.DD.HH.MM" && exit 1)
	@test -n "$(SLUG)" || (echo "SLUG is required" && exit 1)
	python3 tools/package_release.py --timestamp "$(STAMP)" --slug "$(SLUG)" --outdir /mnt/data

verify-release:
	@test -n "$(BUNDLE)" || (echo "BUNDLE is required" && exit 1)
	python3 tools/verify_release.py "$(BUNDLE)"

test-browser:
	node tools/run_tests.mjs --tier browser --id browser:worker-agent-proof --jobs 1

test-browser-boot:
	node tools/run_tests.mjs --tier browser --id browser:cdp-boot-report --jobs 1

test-browser-opfs:
	node tools/run_tests.mjs --tier browser --id browser:opfs-async-proof --jobs 1

test-browser-opfs-sync:
	node tools/run_tests.mjs --tier browser --id browser:opfs-sync-worker-proof --jobs 1

test-browser-opfs-block-store:
	node tools/run_tests.mjs --tier browser --id browser:opfs-block-store-proof --jobs 1

audit-opfs-provider:
	node tools/opfs_provider_contract_audit.mjs --json artifacts/audit/$(PFX)-OPFS-PROVIDER-CONTRACT-AUDIT.json

test-browser-opfs-storage-lane:
	node tools/run_tests.mjs --tier browser --id browser:opfs-storage-lane-adapter-proof --jobs 1

audit-opfs-storage-lane:
	node tools/opfs_storage_lane_adapter_contract_audit.mjs --json artifacts/audit/$(PFX)-OPFS-STORAGE-LANE-ADAPTER-CONTRACT-AUDIT.json

test-browser-sab:
	node tools/run_tests.mjs --tier browser --id browser:sab-ring-worker-proof --jobs 1

test-browser-sab-frame:
	node tools/run_tests.mjs --tier browser --id browser:sab-frame-ring-worker-proof --jobs 1


test-kernel-kit-usefulness:
	node tools/kernel_kit_usefulness_probe.mjs --json artifacts/validation/$(PFX)-KERNEL-KIT-USEFULNESS-PROBE.json

audit-kernel-kit-usefulness:
	node tools/kernel_kit_usefulness_contract_audit.mjs --json artifacts/audit/$(PFX)-KERNEL-KIT-USEFULNESS-CONTRACT-AUDIT.json
