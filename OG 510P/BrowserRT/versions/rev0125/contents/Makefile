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
