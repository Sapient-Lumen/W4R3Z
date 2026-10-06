REV ?= rev0100
PFX ?= REV0100
SLUG ?= opfs-block-store-rollback-valid-block-preserve-current-proof
STAMP ?= $(shell TZ=America/New_York date +%Y.%m.%d.%H.%M)
ZIP ?=

turn-start:
	node tools/turn_bootstrap.mjs --write

check:
	python3 tools/check_cube.py

current:
	node tools/run_tests.mjs --tier release --id opfs:block-store-rollback-valid-block-preserve-proof,facility:opfs-block-store-rollback-valid-block-preserve-contract-audit --jobs 1 --json artifacts/validation/$(PFX)-OPFS-BLOCK-STORE-ROLLBACK-VALID-BLOCK-PRESERVE-RUN.json

browser:
	node tools/run_tests.mjs --tier browser --id browser:opfs-block-store-rollback-valid-block-preserve-proof --jobs 1 --json artifacts/validation/$(PFX)-BROWSER-OPFS-BLOCK-STORE-ROLLBACK-VALID-BLOCK-PRESERVE-RUN.json

release:
	node tools/run_tests.mjs --tier release --jobs auto --quiet --json artifacts/validation/$(PFX)-TEST-HARNESS-RUN.json

audit:
	node tools/opfs_block_store_rollback_valid_block_preserve_contract_audit.mjs --json artifacts/audit/$(PFX)-OPFS-BLOCK-STORE-ROLLBACK-VALID-BLOCK-PRESERVE-CONTRACT-AUDIT.json
	node tools/current_office_audit.mjs --json artifacts/audit/$(PFX)-CURRENT-OFFICE-AUDIT.json

package:
	python3 tools/package_release.py --timestamp "$(STAMP)" --slug $(SLUG) --outdir /mnt/data --reuse-validation

verify:
	@test -n "$(ZIP)" || (echo "Set ZIP=/mnt/data/BrowserRT-$(REV)-YYYY.MM.DD.HH.MM-$(SLUG).zip or run make package first" && exit 1)
	python3 tools/verify_release.py "$(ZIP)"

replay-status-transition:
	npm run replay:quarantine-status-transition-import

replay-receipt-restore:
	npm run replay:quarantine-receipt-restore-integrity

replay-provenance-binding:
	npm run replay:quarantine-clearance-receipt-provenance-binding
