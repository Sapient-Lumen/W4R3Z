.PHONY: manifest package check scorecard audit zip

scorecard:
	python3 tools/render_scorecard.py . > docs/10-framework/proposal-scorecard.md

manifest:
	python3 tools/build_manifest.py .

audit:
	python3 tools/audit_cube.py .
	python3 tools/audit_source_currentness.py .
	python3 tools/audit_remedy_profiles.py .
	python3 tools/audit_case_contracts.py .
	python3 tools/audit_policy_action_profiles.py .
	python3 tools/audit_actor_accountability_profiles.py .

check:
	python3 tools/check_archive.py .

package: scorecard manifest check zip
	@echo "archive ready"

zip:
	python3 tools/package_release.py .
