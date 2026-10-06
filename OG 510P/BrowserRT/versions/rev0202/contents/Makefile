REV ?= rev0125
PFX ?= REV0125
SLUG ?= opfs-block-store-raw-composite-abort-signal-current-proof
STAMP ?= $(shell TZ=America/New_York date +%Y.%m.%d.%H.%M)
ZIP ?= /mnt/data/BrowserRT-$(REV)-$(STAMP)-$(SLUG).zip

.PHONY: check current browser release audit package verify

check:
	python3 tools/check_cube.py

current:
	node tools/run_tests.mjs --tier release --id opfs:block-store-raw-composite-abort-signal-proof,facility:opfs-block-store-raw-composite-abort-signal-contract-audit --jobs 1 --json artifacts/validation/$(PFX)-OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-RUN.json

browser:
	node tools/run_tests.mjs --tier browser --id browser:opfs-block-store-raw-composite-abort-signal-proof --jobs 1 --json artifacts/validation/$(PFX)-BROWSER-OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-RUN.json

release:
	node tools/run_tests.mjs --tier release --jobs auto --json artifacts/validation/$(PFX)-TEST-HARNESS-RUN.json

audit:
	node tools/opfs_block_store_raw_composite_abort_signal_contract_audit.mjs --json artifacts/audit/$(PFX)-OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-CONTRACT-AUDIT.json
	node tools/current_office_audit.mjs --json artifacts/audit/$(PFX)-CURRENT-OFFICE-AUDIT.json

package:
	python3 tools/package_release.py --timestamp $(STAMP) --slug $(SLUG) --outdir /mnt/data --reuse-validation

verify:
	python3 tools/verify_release.py $(ZIP)

audit-service-worker-waituntil-late-failure:
	node tools/run_tests.mjs --tier audit --id facility:service-worker-waituntil-late-failure-contract-audit --jobs 1 --json artifacts/validation/$(PFX)-SERVICE-WORKER-WAITUNTIL-LATE-FAILURE-AUDIT-RUN.json

test-browser-opfs-web-lock-service-worker-waituntil-late-failure:
	node tools/run_tests.mjs --tier browser --id browser:opfs-web-lock-service-worker-waituntil-late-failure-proof --jobs 1 --json artifacts/validation/$(PFX)-BROWSER-OPFS-WEB-LOCK-SERVICE-WORKER-WAITUNTIL-LATE-FAILURE-RUN.json

audit-service-worker-fetch-lifecycle:
	node tools/run_tests.mjs --tier audit --id facility:service-worker-fetch-lifecycle-contract-audit --jobs 1 --json artifacts/validation/$(PFX)-SERVICE-WORKER-FETCH-LIFECYCLE-AUDIT-RUN.json

test-browser-opfs-web-lock-service-worker-fetch-lifecycle:
	node tools/run_tests.mjs --tier browser --id browser:opfs-web-lock-service-worker-fetch-lifecycle-proof --jobs 1 --json artifacts/validation/$(PFX)-BROWSER-OPFS-WEB-LOCK-SERVICE-WORKER-FETCH-LIFECYCLE-RUN.json

audit-service-worker-update-race:
	node tools/run_tests.mjs --tier audit --id facility:service-worker-update-race-contract-audit --jobs 1 --json artifacts/validation/$(PFX)-SERVICE-WORKER-UPDATE-RACE-AUDIT-RUN.json

test-browser-opfs-web-lock-service-worker-update-race:
	node tools/run_tests.mjs --tier browser --id browser:opfs-web-lock-service-worker-update-race-proof --jobs 1 --json artifacts/validation/$(PFX)-BROWSER-OPFS-WEB-LOCK-SERVICE-WORKER-UPDATE-RACE-RUN.json

audit-service-worker-shutdown-boundary:
	node tools/run_tests.mjs --tier audit --id facility:service-worker-shutdown-boundary-contract-audit --jobs 1 --json artifacts/validation/$(PFX)-SERVICE-WORKER-SHUTDOWN-BOUNDARY-AUDIT-RUN.json

test-browser-opfs-web-lock-service-worker-shutdown-boundary:
	node tools/run_tests.mjs --tier browser --id browser:opfs-web-lock-service-worker-shutdown-boundary-proof --jobs 1 --json artifacts/validation/$(PFX)-BROWSER-OPFS-WEB-LOCK-SERVICE-WORKER-SHUTDOWN-BOUNDARY-RUN.json

audit-explicit-id-selection:
	node tools/explicit_id_selection_audit.mjs --json artifacts/audit/$(PFX)-EXPLICIT-ID-SELECTION-AUDIT.json

.PHONY: test-kernel-kit-support-bundle-risk-decision audit-kernel-kit-support-bundle-risk-decision

test-kernel-kit-support-bundle-risk-decision:
	node tools/run_tests.mjs --tier demo --id demo:kernel-kit-support-bundle-risk-decision-proof --jobs 1 --json artifacts/validation/REV0125-KERNEL-KIT-SUPPORT-BUNDLE-RISK-DECISION-RUN.json

audit-kernel-kit-support-bundle-risk-decision:
	node tools/run_tests.mjs --tier audit --id facility:kernel-kit-support-bundle-risk-decision-audit --jobs 1 --json artifacts/validation/REV0125-KERNEL-KIT-SUPPORT-BUNDLE-RISK-DECISION-AUDIT-RUN.json
