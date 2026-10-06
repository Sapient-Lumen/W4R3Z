.PHONY: lint test test-fast test-release test-affected test-full test-list proof turn-start plan capability timing-history context-pack package-release verify-release

lint:
	python3 tools/check_cube.py
	node tools/run_tests.mjs --tier release --jobs auto --json artifacts/validation/REV0005-TEST-HARNESS-RUN.json
	node tools/update_timing_history.mjs --report artifacts/validation/REV0005-TEST-HARNESS-RUN.json --out artifacts/validation/REV0005-TEST-TIMING-HISTORY.json
	python3 tools/check_cube.py

test: test-release

test-fast:
	node tools/run_tests.mjs --tier smoke --jobs auto

test-release:
	node tools/run_tests.mjs --tier release --jobs auto --json artifacts/validation/REV0005-TEST-HARNESS-RUN.json

test-affected:
	@test -n "$(CHANGED)" || (echo "CHANGED is required, e.g. CHANGED=src/browserrt.mjs" && exit 1)
	node tools/run_tests.mjs --tier release --changed "$(CHANGED)" --only-affected --jobs auto

test-full:
	node tools/run_tests.mjs --tier full --jobs auto

test-list:
	node tools/run_tests.mjs --list --tier release

plan:
	node tools/plan_tests.mjs --tier release --changed src/browserrt.mjs,tools/run_tests.mjs --json artifacts/validation/REV0005-TEST-PLAN-SANITY.json

capability:
	node tools/capability_survey.mjs --json artifacts/validation/REV0005-CAPABILITY-SURVEY.json

timing-history:
	node tools/update_timing_history.mjs --report artifacts/validation/REV0005-TEST-HARNESS-RUN.json --out artifacts/validation/REV0005-TEST-TIMING-HISTORY.json

proof:
	node tools/run_rev0005_proof.mjs --write

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
