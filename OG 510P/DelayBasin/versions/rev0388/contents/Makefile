PYTHON ?= env PYTHONDONTWRITEBYTECODE=1 python -S

.PHONY: lint context-pack package-release handoff-release prepare-external-custody score-external-response validation-index validation-toolchain lint-idempotence schema-coverage basis-provenance

lint:
	@$(PYTHON) tools/run_lint_suite.py

context-pack:
	@$(PYTHON) tools/gen_all_generated_surfaces.py

package-release:
	@test -n "$(STAMP)" || (echo "STAMP required (YYYY.MM.DD.HH.MM)"; exit 1)
	@test -n "$(SLUG)" || (echo "SLUG required (lowercase-dash slug)"; exit 1)
	@$(PYTHON) tools/package_release.py --timestamp "$(STAMP)" --slug "$(SLUG)"

prepare-external-custody:
	@test -n "$(RESPONSE)" || (echo "RESPONSE required (path to frozen response JSON)"; exit 1)
	@test -n "$(CUSTODIAN_ID)" || (echo "CUSTODIAN_ID required"; exit 1)
	@test -n "$(EXPOSURE_NOTES)" || (echo "EXPOSURE_NOTES required"; exit 1)
	@test -n "$(EVIDENCE_OUT)" || (echo "EVIDENCE_OUT required"; exit 1)
	@test "$(ATTEST_CLEAN_PREANSWER)" = "yes" || (echo "ATTEST_CLEAN_PREANSWER=yes required"; exit 1)
	@$(PYTHON) tools/prepare_priority_zero_clean_response_custody_record.py "$(RESPONSE)" \
		--custodian-id "$(CUSTODIAN_ID)" \
		--pre-response-exposure-notes "$(EXPOSURE_NOTES)" \
		--attest-clean-preanswer \
		--out "$(EVIDENCE_OUT)"

score-external-response:
	@test -n "$(RESPONSE)" || (echo "RESPONSE required (path to frozen response JSON)"; exit 1)
	@test -n "$(EVIDENCE)" || (echo "EVIDENCE required (path to frozen custody record JSON)"; exit 1)
	@test -n "$(SCORE_SHEET)" || (echo "SCORE_SHEET required (path to completed post-response score sheet JSON)"; exit 1)
	@if [ -n "$(SUMMARY_OUT)" ]; then \
		$(PYTHON) tools/score_priority_zero_external_replay_response.py --evidence-record "$(EVIDENCE)" --score-sheet "$(SCORE_SHEET)" --summary-out "$(SUMMARY_OUT)" "$(RESPONSE)"; \
	else \
		$(PYTHON) tools/score_priority_zero_external_replay_response.py --evidence-record "$(EVIDENCE)" --score-sheet "$(SCORE_SHEET)" "$(RESPONSE)"; \
	fi

handoff-release:
	@test -n "$(STAMP)" || (echo "STAMP required (YYYY.MM.DD.HH.MM)"; exit 1)
	@test -n "$(SLUG)" || (echo "SLUG required (lowercase-dash slug)"; exit 1)
	$(MAKE) context-pack
	$(MAKE) lint
	$(MAKE) package-release STAMP="$(STAMP)" SLUG="$(SLUG)"

validation-index:
	@$(PYTHON) tools/gen_validation_index.py

validation-toolchain:
	@$(PYTHON) tools/gen_validation_toolchain_manifest.py

lint-idempotence:
	@$(PYTHON) tools/gen_lint_idempotence_audit.py

schema-coverage:
	@$(PYTHON) tools/gen_schema_coverage_audit.py


basis-provenance:
	@$(PYTHON) tools/gen_basis_provenance_audit.py
