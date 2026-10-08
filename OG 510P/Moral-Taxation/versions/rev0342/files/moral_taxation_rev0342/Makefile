.PHONY: manifest package check scorecard profile-index audit zip

scorecard:
	python3 tools/render_scorecard.py . > docs/10-framework/proposal-scorecard.md

manifest:
	python3 tools/build_manifest.py .

profile-index:
	python3 tools/build_route_profile_index.py .

audit:
	PYTHONDONTWRITEBYTECODE=1 python3 tools/run_semantic_audits.py .
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	@# tools/audit_cube.py
	@# tools/audit_axis_hygiene.py
	@# tools/audit_prose_bloat.py
	@# tools/audit_waste_signals.py
	@# tools/audit_source_currentness.py
	@# tools/audit_external_attestation_verifier.py
	@# tools/audit_procurement_risk.py
	@# tools/audit_remedy_profiles.py
	@# tools/audit_case_contracts.py
	@# tools/audit_route_profile_index.py
	@# tools/audit_answer_skeletons.py
	@# tools/audit_claim_provenance.py
	@# tools/audit_precedence_resolution.py
	@# tools/audit_disposition_synthesis.py
	@# tools/audit_decision_adapters.py
	@# tools/audit_adapter_execution.py
	@# tools/audit_evidence_producer_contracts.py
	@# tools/audit_evidence_producer_execution.py
	@# tools/audit_model_input_bundles.py
	@# tools/audit_model_input_source_manifests.py
	@# tools/build_authority_intake_source_manifest.py
	@# tools/build_authority_intake_bundle.py
	@# tools/audit_authority_evidence_bundles.py
	@# tools/build_evidence_replay_ledger.py
	@# tools/audit_evidence_replay_ledger.py
	@# tools/audit_decision_promotion_gate.py
	@# tools/audit_positive_external_evidence_path.py
	@# tools/audit_decision_review_bundle.py
	@# tools/audit_decision_output_packets.py
	@# tools/audit_release_lineage.py
	@# tools/audit_policy_action_profiles.py
	@# tools/audit_actor_accountability_profiles.py

check:
	python3 tools/check_archive.py .

package: scorecard profile-index audit manifest check zip
	@echo "archive ready"

zip:
	python3 tools/package_release.py .
