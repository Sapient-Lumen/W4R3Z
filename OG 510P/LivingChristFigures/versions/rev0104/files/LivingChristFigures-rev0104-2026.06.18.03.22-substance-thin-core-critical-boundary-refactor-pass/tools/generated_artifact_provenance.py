#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, json, sys
from pathlib import Path

FIELDS=['artifact_path','generator','input_paths','artifact_sha256','input_fingerprint','row_count','status','note']

ARTIFACTS = [
    ('META/Public-Export-Eligibility-current.csv','tools/public_export_eligibility.py',['Candidate-Ledger-current.csv','Source-Registry-current.csv','GOVERNANCE/Family-Consent-and-Case-Name-Use-Ledger-current.csv','SCHEMA/Public-Allowed-Claim-Shapes-current.csv','tools/public_template_policy.py']),
    ('META/Public-Source-Link-Review-current.csv','tools/public_source_link_review.py',['Source-Registry-current.csv','SCHEMA/Public-Link-Policy-current.csv','SCHEMA/Harm-Proximity-Controlled-Vocabulary-current.csv']),
    ('META/Source-Freshness-Preservation-current.csv','tools/source_freshness_preservation.py',['Source-Registry-current.csv']),
    ('META/Source-Preservation-Status-current.csv','tools/source_preservation_status.py',['Source-Registry-current.csv']),
    ('META/Source-Manual-Preservation-Decision-current.csv','tools/source_manual_preservation_decision.py',['Source-Registry-current.csv','META/Public-Source-Link-Review-current.csv','SCHEMA/Source-Manual-Preservation-Decision-Fields-current.csv']),
    ('META/Source-Maintenance-Priority-current.csv','tools/source_maintenance_priority.py',['Source-Registry-current.csv','META/Public-Source-Link-Review-current.csv']),
    ('META/Source-Metadata-Backfill-current.csv','tools/source_metadata_backfill_log.py',['Source-Registry-current.csv','META/Source-Maintenance-Priority-current.csv','SCHEMA/Source-Metadata-Backfill-Fields-current.csv']),
    ('META/Source-Backfill-Coverage-Audit-current.csv','tools/source_backfill_coverage_audit.py',['Source-Registry-current.csv','META/Source-Metadata-Backfill-current.csv','SCHEMA/Source-Backfill-Coverage-Audit-Fields-current.csv']),
    ('META/Source-Safety-Nearmiss-Audit-current.csv','tools/source_safety_nearmiss_audit.py',['Source-Registry-current.csv','META/Public-Source-Link-Review-current.csv','SCHEMA/Source-Safety-Nearmiss-Audit-Fields-current.csv']),
    ('META/Family-Profile-Consent-Boundary-Audit-current.csv','tools/family_profile_consent_audit.py',['Source-Registry-current.csv','META/Public-Source-Link-Review-current.csv','GOVERNANCE/Family-Consent-and-Case-Name-Use-Ledger-current.csv','Claim-Ledger-current.csv','SCHEMA/Family-Profile-Consent-Boundary-Audit-Fields-current.csv']),
    ('META/Border-Route-Referral-Boundary-Audit-current.csv','tools/border_route_referral_audit.py',['Candidate-Ledger-current.csv','Claim-Ledger-current.csv','Source-Registry-current.csv','META/Public-Source-Link-Review-current.csv','META/Public-Claim-Quarantine-current.csv','SCHEMA/Border-Route-Referral-Boundary-Audit-Fields-current.csv']),
    ('META/Pacific-GBV-Service-Capacity-Boundary-Audit-current.csv','tools/pacific_gbv_service_capacity_audit.py',['Candidate-Ledger-current.csv','Claim-Ledger-current.csv','Source-Registry-current.csv','META/Public-Source-Link-Review-current.csv','META/Public-Claim-Quarantine-current.csv','SCHEMA/Pacific-GBV-Service-Capacity-Boundary-Audit-Fields-current.csv']),
    ('META/Suicide-Crisis-Operational-Boundary-Audit-current.csv','tools/suicide_crisis_operational_boundary_audit.py',['Candidate-Ledger-current.csv','Claim-Ledger-current.csv','Source-Registry-current.csv','META/Public-Source-Link-Review-current.csv','META/Public-Claim-Quarantine-current.csv','SCHEMA/Suicide-Crisis-Operational-Boundary-Audit-Fields-current.csv']),
    ('META/Source-URL-Integrity-Audit-current.csv','tools/source_url_integrity_audit.py',['Source-Registry-current.csv','SCHEMA/Source-URL-Integrity-Audit-Fields-current.csv']),
    ('PUBLIC/Candidate-Index-public.csv','tools/render_public_safe_index.py',['Candidate-Ledger-current.csv','META/Public-Export-Eligibility-current.csv','PUBLIC/Public-Safe-Prose-Templates-current.md','tools/public_template_policy.py']),
    ('META/Public-Release-Lint-current.csv','tools/public_release_lint.py',['PUBLIC/Candidate-Index-public.csv','PUBLIC/Candidate-Index-public.json','PUBLIC/Candidate-Index-public.md','PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json','PUBLIC/Public-Redaction-Policy-current.md','PUBLIC/Public-Safe-Prose-Templates-current.md','PUBLIC/README-public-edition.md','PUBLIC/PUBLIC-BUNDLE-MANIFEST-current.json']),
    ('META/Sensitive-Surface-Inventory-current.csv','tools/sensitive_surface_inventory.py',['Candidate-Ledger-current.csv','Claim-Ledger-current.csv','Source-Registry-current.csv','PUBLIC/Candidate-Index-public.csv']),
    ('META/Claim-Evidence-Strength-current.csv','tools/evidence_lifecycle.py',['Claim-Ledger-current.csv','Source-Registry-current.csv','META/Claim-Type-Taxonomy-current.csv']),
    ('META/Refresh-Priority-Queue-current.csv','tools/evidence_lifecycle.py',['Claim-Ledger-current.csv','Candidate-Ledger-current.csv','META/Claim-Evidence-Strength-current.csv']),
    ('META/Candidate-Governance-Snapshot-current.csv','tools/candidate_governance_snapshot.py',['Candidate-Ledger-current.csv','META/Public-Export-Eligibility-current.csv','META/Public-Source-Link-Review-current.csv','META/Claim-Evidence-Strength-current.csv','GOVERNANCE/Family-Consent-and-Case-Name-Use-Ledger-current.csv']),
    ('META/Governance-Review-Queue-current.csv','tools/candidate_governance_snapshot.py',['META/Candidate-Governance-Snapshot-current.csv']),
    ('META/Redaction-Risk-Scan-current.csv','tools/redaction_scan.py',['tools/redaction_scan.py']),
    ('META/Redaction-Risk-Open-Findings-current.csv','tools/redaction_scan.py',['META/Redaction-Risk-Scan-current.csv']),
    ('META/Rule46-Scan-current.csv','tools/rule46_scan.py',['CANDIDATES/Bridget-Tolley-FSIS-MMIWG-Canada.txt','LONGFORM/Boundary-004-Family-Led-Search-Is-Not-A-Case-List.txt','PUBLIC/Candidate-Index-public.csv']),
    ('SCHEMA/Row-Validation-Report-current.csv','tools/row_validate.py',['SCHEMA/Row-Validation-Contract-current.json','SCHEMA/Ledger-Contract-current.json','Candidate-Ledger-current.csv','Claim-Ledger-current.csv','Source-Registry-current.csv']),
    ('META/Revision-Surface-Audit-current.csv','tools/revision_surface_audit.py',['manifest.json','CURRENT-SPINE.md','CUBE-MAP.md','CUBE-RULES.txt','PUBLIC/README-public-edition.md','PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json','SCHEMA/Package-Release-Contract-current.json']),
    ('META/Public-Index-Parity-current.csv','tools/public_index_parity.py',['PUBLIC/Candidate-Index-public.csv','PUBLIC/Candidate-Index-public.json','PUBLIC/Candidate-Index-public.md','PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json','META/Public-Export-Eligibility-current.csv','tools/public_template_policy.py']),
    ('META/Public-Index-Semantic-Audit-current.csv','tools/public_index_semantic_audit.py',['Candidate-Ledger-current.csv','META/Public-Export-Eligibility-current.csv','PUBLIC/Candidate-Index-public.csv','tools/public_template_policy.py','SCHEMA/Public-Index-Semantic-Audit-Fields-current.csv']),
    ('META/Governance-Consistency-Audit-current.csv','tools/governance_consistency_audit.py',['Candidate-Ledger-current.csv','Source-Registry-current.csv','META/Public-Export-Eligibility-current.csv','META/Public-Source-Link-Review-current.csv','META/Candidate-Governance-Snapshot-current.csv','META/Governance-Review-Queue-current.csv','GOVERNANCE/Family-Consent-and-Case-Name-Use-Ledger-current.csv','GOVERNANCE/Governance-Decision-Ledger-current.csv','PUBLIC/Candidate-Index-public.csv']),
    ('META/Version-Lineage-Audit-current.csv','tools/version_lineage_audit.py',['manifest.json','PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json','SCHEMA/Package-Release-Contract-current.json','META/Previous-Release-Fingerprint-current.json','Refresh-Index-current.csv']),
    ('META/Handoff-Review-Digest-current.csv','tools/handoff_review_digest.py',['manifest.json','META/Package-Delta-Manifest-current.csv','META/Version-Lineage-Audit-current.csv','META/Cross-Report-Reference-Audit-current.csv','META/Package-Identity-Audit-current.csv','META/Dependency-Cycle-Audit-current.csv','META/Handoff-Notice-Audit-current.csv','META/Current-Surface-Registry-current.csv','META/Release-Gate-Attestation-current.csv','META/Helper-Adoption-Audit-current.csv']),
    ('META/Regeneration-Coverage-Audit-current.csv','tools/regeneration_coverage_audit.py',['tools/regeneration_coverage_audit.py','tools/generated_artifact_provenance.py','META/Regeneration-Sequence-Plan-current.csv','META/Report-Contract-Registry-current.csv','SCHEMA/Regeneration-Coverage-Audit-Fields-current.csv']),
    ('META/Current-Surface-Freshness-Audit-current.csv','tools/current_surface_freshness_audit.py',['manifest.json','datapackage.json','BUILD-PROVENANCE-current.json','PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json','SCHEMA/Package-Release-Contract-current.json','META/Handoff-Review-Digest-current.csv','META/Previous-Release-Fingerprint-current.json','META/Previous-Release-Fingerprint-current.md','000-START-HERE.txt','CURRENT-SPINE.md','DATA-CARD-current.md','META/Data-Card-current.md','CUBE-MAP.md','LivingChristFigures.txt','PUBLIC/README-public-edition.md','PUBLIC/PUBLIC-BUNDLE-MANIFEST-current.json']),
    ('META/Preservation-Transfer-Readiness-current.csv','tools/preservation_transfer_readiness.py',['manifest.json','ro-crate-metadata.json','META/Archive-Member-Manifest-current.csv','META/Archive-Build-Manifest-current.csv','META/Archive-Roundtrip-Audit-current.csv','META/Current-Surface-Freshness-Audit-current.csv','META/Public-Release-Lint-current.csv','META/Package-Dependency-Graph-current.csv','META/Regeneration-Sequence-Plan-current.csv','BUILD-PROVENANCE-current.json','SCHEMA/Package-Release-Contract-current.json','RIGHTS-AND-USE-LIMITS.md','GOVERNANCE/Handoff-Use-Limits-and-Reviewer-Notice-current.md','GOVERNANCE/Review-Role-and-Handoff-Boundaries-current.md','tools/make_bagit_transfer_copy.py']),
    ('META/Package-Delta-Manifest-current.csv','tools/package_delta_manifest.py',['META/Previous-Release-Fingerprint-current.json','tools/package_delta_manifest.py']),
    ('META/Cross-Report-Reference-Audit-current.csv','tools/cross_report_reference_audit.py',['manifest.json','META/Previous-Release-Fingerprint-current.json','000-START-HERE.txt','CURRENT-SPINE.md','CUBE-MAP.md','PUBLIC/README-public-edition.md','PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json','SCHEMA/Package-Release-Contract-current.json','SCHEMA/README-schema-current.md','tools/README.md']),
    ('META/Package-Dependency-Graph-current.csv','tools/package_dependency_graph.py',['tools/generated_artifact_provenance.py','SCHEMA/Package-Release-Contract-current.json','SCHEMA/Ledger-Contract-current.json','SCHEMA/Frontmatter-Contract-current.json','tools/README.md']),
    ('META/CSV-JSON-Mirror-Audit-current.csv','tools/csv_json_mirror_audit.py',['SCHEMA/Ledger-Contract-current.json','SCHEMA/Package-Release-Contract-current.json','tools/lib_cube.py']),
    ('META/Schema-Coverage-Audit-current.csv','tools/schema_coverage_audit.py',['SCHEMA/Ledger-Contract-current.json','SCHEMA/Package-Release-Contract-current.json','SCHEMA/README-schema-current.md','tools/lib_cube.py']),
    ('META/Field-Schema-Consistency-Audit-current.csv','tools/field_schema_consistency.py',['SCHEMA/README-schema-current.md','SCHEMA/Field-Schema-Consistency-Audit-Fields-current.csv','tools/lib_cube.py']),
    ('META/Path-Reference-Audit-current.csv','tools/path_reference_audit.py',['manifest.json','SCHEMA/Package-Release-Contract-current.json','PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json','GOVERNANCE/README-governance-current.md','tools/README.md']),
    ('META/Rule-Gate-Traceability-current.csv','tools/rule_gate_traceability.py',['META/Boundary-Rule-Coverage-current.csv','tools/qa_cube.py','tools/release_gate_attestation.py','tools/rule_gate_traceability.py']),
    ('META/Tool-Run-Matrix-current.csv','tools/tool_run_matrix.py',['tools/generated_artifact_provenance.py','META/Package-Dependency-Graph-current.csv','tools/release_gate_attestation.py','tools/qa_cube.py']),
    ('META/Required-Document-Coverage-current.csv','tools/required_document_coverage.py',['manifest.json','SCHEMA/Package-Release-Contract-current.json','PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json','tools/required_document_coverage.py']),
    ('META/Package-File-Inventory-current.csv','tools/package_file_inventory.py',['manifest.json','SCHEMA/Package-Release-Contract-current.json','tools/generated_artifact_provenance.py']),
    ('META/Audit-Selftest-current.csv','tools/audit_selftest.py',['tools/audit_selftest.py','tools/public_release_lint.py','tools/csv_json_mirror_audit.py','tools/revision_surface_audit.py','tools/path_reference_audit.py','tools/row_validate.py','tools/public_contract_check.py','tools/public_index_semantic_audit.py','tools/public_template_policy.py','PUBLIC/README-public-edition.md','PUBLIC/Candidate-Index-public.csv','Candidate-Ledger-current.csv','Candidate-Ledger-current.json','000-START-HERE.txt','CURRENT-SPINE.md','SCHEMA/Package-Release-Contract-current.json']),
    ('META/Rebuild-Readiness-Audit-current.csv','tools/rebuild_readiness_audit.py',['tools/generated_artifact_provenance.py','tools/rebuild_readiness_audit.py','tools/README.md']),
    ('META/Policy-Assertion-Matrix-current.csv','tools/policy_assertion_matrix.py',['CURRENT-SPINE.md','PUBLIC/README-public-edition.md','SCHEMA/Package-Release-Contract-current.json','META/Public-Release-Lint-current.csv','META/Sensitive-Surface-Inventory-current.csv','META/Rule46-Scan-current.csv','META/Public-Index-Parity-current.csv','META/Public-Index-Semantic-Audit-current.csv','META/Governance-Consistency-Audit-current.csv','META/Public-Source-Link-Review-current.csv','META/Rebuild-Readiness-Audit-current.csv']),
    ('META/Regeneration-Sequence-Plan-current.csv','tools/regeneration_sequence_plan.py',['tools/generated_artifact_provenance.py','tools/README.md','SCHEMA/Package-Release-Contract-current.json']),
    ('META/Archive-Build-Manifest-current.csv','tools/archive_build_manifest.py',['manifest.json','SCHEMA/Package-Release-Contract-current.json']),
    ('META/Selftest-Coverage-Matrix-current.csv','tools/selftest_coverage_matrix.py',['META/Audit-Selftest-current.csv','tools/audit_selftest.py','tools/release_gate_attestation.py']),
    ('META/Checksum-Scope-Audit-current.csv','tools/checksum_scope_audit.py',['tools/checksum_scope_audit.py','tools/lib_cube.py']),
    ('META/Public-Negative-Corpus-current.csv','tools/public_negative_corpus.py',['tools/public_negative_corpus.py','tools/public_release_lint.py']),
    ('META/Helper-Adoption-Audit-current.csv','tools/helper_adoption_audit.py',['tools/helper_adoption_audit.py','tools/lib_cube.py','tools/csv_json_mirror_audit.py','tools/schema_coverage_audit.py','tools/field_schema_consistency.py','tools/checksum_scope_audit.py','META/CSV-JSON-Mirror-Audit-current.csv','META/Schema-Coverage-Audit-current.csv','META/Field-Schema-Consistency-Audit-current.csv','META/Checksum-Scope-Audit-current.csv']),

    ('META/Archive-Roundtrip-Audit-current.csv','tools/archive_roundtrip_audit.py',['manifest.json','tools/archive_roundtrip_audit.py','META/Unicode-Path-Audit-current.csv']),
    ('META/Current-Pointer-Coherence-Audit-current.csv','tools/current_pointer_coherence_audit.py',['manifest.json','PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json','SCHEMA/Package-Release-Contract-current.json','Refresh-Index-current.csv','000-START-HERE.txt','CURRENT-SPINE.md','CUBE-MAP.md']),
    ('META/Public-Lint-Allowed-Contexts-current.csv','tools/rev0065_governance_surfaces.py',['SCHEMA/Public-Lint-Allowed-Contexts-Fields-current.csv']),
    ('META/Evidence-Debt-Sprint-current.csv','tools/rev0065_governance_surfaces.py',['Evidence-Debt-current.csv','Claim-Ledger-current.csv','Candidate-Ledger-current.csv']),
    ('GOVERNANCE/Permission-State-Ledger-current.csv','tools/rev0065_governance_surfaces.py',['Candidate-Ledger-current.csv']),
    ('META/Office-Accountability-current.csv','tools/rev0065_governance_surfaces.py',['Candidate-Ledger-current.csv','Office-Card-Index-current.csv']),
    ('META/Controlled-Vocabulary-Normalization-current.csv','tools/ledger_code_overlay.py',['Candidate-Ledger-current.csv','Claim-Ledger-current.csv','Source-Registry-current.csv','GOVERNANCE/Permission-State-Ledger-current.csv','META/Public-Export-Eligibility-current.csv','SCHEMA/Harm-Proximity-Controlled-Vocabulary-current.csv']),
    ('META/Helper-Adoption-Scope-current.csv','tools/rev0065_governance_surfaces.py',['tools/lib_cube.py','META/Helper-Adoption-Audit-current.csv']),
    ('META/Archive-Member-Manifest-current.csv','tools/archive_member_manifest.py',['manifest.json','tools/archive_member_manifest.py']),
    ('META/Unicode-Path-Audit-current.csv','tools/unicode_path_audit.py',['tools/unicode_path_audit.py']),
    ('META/Package-Identity-Audit-current.csv','tools/package_identity_audit.py',['manifest.json','PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json','SCHEMA/Package-Release-Contract-current.json','Refresh-Index-current.csv','META/Archive-Build-Manifest-current.csv','META/Archive-Member-Manifest-current.csv','META/Checksum-Scope-Audit-current.csv','META/Unicode-Path-Audit-current.csv']),
    ('META/Dependency-Cycle-Audit-current.csv','tools/dependency_cycle_audit.py',['tools/generated_artifact_provenance.py','META/Package-Dependency-Graph-current.csv']),
    ('META/Handoff-Notice-Audit-current.csv','tools/handoff_notice_audit.py',['GOVERNANCE/Handoff-Use-Limits-and-Reviewer-Notice-current.md','000-START-HERE.txt','CURRENT-SPINE.md','PUBLIC/README-public-edition.md','GOVERNANCE/README-governance-current.md']),
    ('META/Current-Surface-Registry-current.csv','tools/current_surface_registry.py',['tools/generated_artifact_provenance.py','SCHEMA/Ledger-Contract-current.json','SCHEMA/README-schema-current.md']),

    ('META/Report-Contract-Registry-current.csv','tools/report_contract_registry.py',['tools/report_contract_registry.py','tools/lib_cube.py','SCHEMA/Ledger-Contract-current.json','META/Current-Surface-Registry-current.csv','SCHEMA/Report-Contract-Registry-Fields-current.csv']),
    ('META/Report-Contract-Audit-current.csv','tools/report_contract_registry.py',['tools/report_contract_registry.py','tools/lib_cube.py','SCHEMA/Ledger-Contract-current.json','META/Current-Surface-Registry-current.csv','SCHEMA/Report-Contract-Audit-Fields-current.csv','META/Report-Contract-Registry-current.csv']),
    ('META/Manifest-Semantic-Coherence-Audit-current.csv','tools/manifest_semantic_coherence_audit.py',['manifest.json','PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json','SCHEMA/Package-Release-Contract-current.json','Refresh-Index-current.csv','000-START-HERE.txt','CURRENT-SPINE.md','DATA-CARD-current.md','LivingChristFigures.txt','PUBLIC/README-public-edition.md','META/Data-Card-current.md','CUBE-MAP.md']),
    ('META/JSON-Key-Uniqueness-Audit-current.csv','tools/json_key_uniqueness_audit.py',['tools/json_key_uniqueness_audit.py']),
    ('META/Review-Role-Boundary-Audit-current.csv','tools/review_role_boundary_audit.py',['GOVERNANCE/Review-Role-and-Handoff-Boundaries-current.md','GOVERNANCE/Handoff-Use-Limits-and-Reviewer-Notice-current.md','000-START-HERE.txt','CURRENT-SPINE.md','PUBLIC/README-public-edition.md','GOVERNANCE/README-governance-current.md','SCHEMA/Package-Release-Contract-current.json']),
    ('META/Helper-Golden-Output-Audit-current.csv','tools/helper_golden_output_audit.py',['tools/helper_golden_output_audit.py','tools/lib_cube.py']),
    ('SCHEMA/Boundary-Governance-Controlled-Vocabulary-current.csv','tools/ledger_code_overlay.py',['GOVERNANCE/Permission-State-Ledger-current.csv','META/Controlled-Vocabulary-Normalization-current.csv']),
    ('SCHEMA/Normalized-Code-Overlay-current.csv','tools/ledger_code_overlay.py',['SCHEMA/Boundary-Governance-Controlled-Vocabulary-current.csv','SCHEMA/Harm-Proximity-Controlled-Vocabulary-current.csv','META/Controlled-Vocabulary-Normalization-current.csv']),
    ('META/Normalized-Code-Overlay-current.csv','tools/ledger_code_overlay.py',['Candidate-Ledger-current.csv','Claim-Ledger-current.csv','Source-Registry-current.csv','GOVERNANCE/Permission-State-Ledger-current.csv','META/Public-Export-Eligibility-current.csv','SCHEMA/Boundary-Governance-Controlled-Vocabulary-current.csv','SCHEMA/Harm-Proximity-Controlled-Vocabulary-current.csv','META/Controlled-Vocabulary-Normalization-current.csv']),
    ('META/Normalized-Code-Overlay-Audit-current.csv','tools/ledger_code_overlay.py',['META/Normalized-Code-Overlay-current.csv','SCHEMA/Boundary-Governance-Controlled-Vocabulary-current.csv','SCHEMA/Harm-Proximity-Controlled-Vocabulary-current.csv','META/Controlled-Vocabulary-Normalization-current.csv']),
    ('META/Evidence-Debt-Execution-Queue-current.csv','tools/evidence_debt_execution_queue.py',['Evidence-Debt-current.csv','Candidate-Ledger-current.csv','Claim-Ledger-current.csv','META/Claim-Evidence-Strength-current.csv','META/Public-Claim-Quarantine-current.csv','META/Evidence-Debt-Sprint-current.csv','SCHEMA/Evidence-Debt-Execution-Queue-Fields-current.csv']),
    ('META/Evidence-Debt-Execution-Audit-current.csv','tools/evidence_debt_execution_queue.py',['META/Evidence-Debt-Execution-Queue-current.csv','Evidence-Debt-current.csv','Candidate-Ledger-current.csv','SCHEMA/Evidence-Debt-Execution-Audit-Fields-current.csv']),
    ('SCHEMA/Evidence-Debt-Execution-Queue-Fields-current.csv','tools/evidence_debt_execution_queue.py',['tools/evidence_debt_execution_queue.py']),
    ('SCHEMA/Evidence-Debt-Execution-Audit-Fields-current.csv','tools/evidence_debt_execution_queue.py',['tools/evidence_debt_execution_queue.py']),
    ('META/Evidence-Debt-Work-Packet-current.csv','tools/evidence_debt_work_packets.py',['META/Evidence-Debt-Execution-Queue-current.csv','Evidence-Debt-current.csv','Claim-Ledger-current.csv','SCHEMA/Evidence-Debt-Work-Packet-Fields-current.csv']),
    ('META/Evidence-Debt-Work-Packet-Audit-current.csv','tools/evidence_debt_work_packets.py',['META/Evidence-Debt-Work-Packet-current.csv','META/Evidence-Debt-Execution-Queue-current.csv','SCHEMA/Evidence-Debt-Work-Packet-Audit-Fields-current.csv']),
    ('SCHEMA/Evidence-Debt-Work-Packet-Fields-current.csv','tools/evidence_debt_work_packets.py',['tools/evidence_debt_work_packets.py']),
    ('SCHEMA/Evidence-Debt-Work-Packet-Audit-Fields-current.csv','tools/evidence_debt_work_packets.py',['tools/evidence_debt_work_packets.py']),
    ('META/Evidence-Debt-Critical-Path-Work-Order-current.csv','tools/evidence_debt_critical_path_work_order.py',['META/Evidence-Debt-Work-Packet-current.csv','META/Evidence-Debt-Execution-Queue-current.csv','Evidence-Debt-current.csv','SCHEMA/Evidence-Debt-Critical-Path-Work-Order-Fields-current.csv']),
    ('META/Evidence-Debt-Work-Packet-Trace-current.csv','tools/evidence_debt_critical_path_work_order.py',['META/Evidence-Debt-Critical-Path-Work-Order-current.csv','META/Evidence-Debt-Work-Packet-current.csv','META/Evidence-Debt-Execution-Queue-current.csv','Evidence-Debt-current.csv','SCHEMA/Evidence-Debt-Work-Packet-Trace-Fields-current.csv']),
    ('META/Evidence-Debt-Critical-Path-Audit-current.csv','tools/evidence_debt_critical_path_work_order.py',['META/Evidence-Debt-Critical-Path-Work-Order-current.csv','META/Evidence-Debt-Work-Packet-Trace-current.csv','META/Evidence-Debt-Work-Packet-current.csv','META/Evidence-Debt-Execution-Queue-current.csv','SCHEMA/Evidence-Debt-Critical-Path-Audit-Fields-current.csv']),
    ('SCHEMA/Evidence-Debt-Critical-Path-Work-Order-Fields-current.csv','tools/evidence_debt_critical_path_work_order.py',['tools/evidence_debt_critical_path_work_order.py']),
    ('SCHEMA/Evidence-Debt-Work-Packet-Trace-Fields-current.csv','tools/evidence_debt_critical_path_work_order.py',['tools/evidence_debt_critical_path_work_order.py']),
    ('SCHEMA/Evidence-Debt-Critical-Path-Audit-Fields-current.csv','tools/evidence_debt_critical_path_work_order.py',['tools/evidence_debt_critical_path_work_order.py']),
    ('META/Release-Change-Review-current.csv','tools/release_change_review.py',['META/Package-Delta-Manifest-current.csv','manifest.json','SIGNATURE-STATUS-current.md','SIGNATURE-READINESS-current.md','SCHEMA/Release-Change-Review-Fields-current.csv']),
    ('SCHEMA/Ledger-Relationship-Audit-Fields-current.csv','tools/ledger_relationship_audit.py',['tools/ledger_relationship_audit.py']),

    ('PUBLIC/PUBLIC-BUNDLE-MANIFEST-current.json','tools/public_export_surface_audit.py',['manifest.json','SCHEMA/Package-Release-Contract-current.json','PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json','tools/public_export_surface_audit.py']),
    ('SCHEMA/Public-Export-Surface-Audit-Fields-current.csv','tools/public_export_surface_audit.py',['tools/public_export_surface_audit.py']),
    ('META/Public-Export-Surface-Audit-current.csv','tools/public_export_surface_audit.py',['manifest.json','PUBLIC/PUBLIC-BUNDLE-MANIFEST-current.json','PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json','SCHEMA/Package-Release-Contract-current.json','PUBLIC/Candidate-Index-public.csv','SCHEMA/Public-Export-Surface-Audit-Fields-current.csv']),
    ('META/Ledger-Relationship-Audit-current.csv','tools/ledger_relationship_audit.py',['Candidate-Ledger-current.csv','Claim-Ledger-current.csv','Source-Registry-current.csv','Office-Card-Index-current.csv','Evidence-Debt-current.csv','Refresh-Index-current.csv','GOVERNANCE/Permission-State-Ledger-current.csv','META/Public-Export-Eligibility-current.csv','META/Candidate-Governance-Snapshot-current.csv','META/Public-Claim-Quarantine-current.csv','META/Public-Claim-Release-Ledger-current.csv','META/Claim-Evidence-Strength-current.csv','META/Claim-Source-Boundary-Matrix-current.csv','META/Candidate-Discovery-Log-current.csv','META/Normalized-Code-Overlay-current.csv','SCHEMA/Ledger-Relationship-Audit-Fields-current.csv']),

    ('META/Boundary-Domain-Registry-current.csv','tools/boundary_domain_map.py',['Candidate-Ledger-current.csv','META/Public-Export-Eligibility-current.csv','GOVERNANCE/Permission-State-Ledger-current.csv','META/Office-Accountability-current.csv']),
    ('META/Candidate-Boundary-Domain-Map-current.csv','tools/boundary_domain_map.py',['Candidate-Ledger-current.csv','META/Public-Export-Eligibility-current.csv','GOVERNANCE/Permission-State-Ledger-current.csv','META/Office-Accountability-current.csv','Claim-Ledger-current.csv','Source-Registry-current.csv']),
    ('META/Boundary-Domain-Coverage-Audit-current.csv','tools/boundary_domain_map.py',['Candidate-Ledger-current.csv','META/Public-Export-Eligibility-current.csv','GOVERNANCE/Permission-State-Ledger-current.csv','META/Candidate-Boundary-Domain-Map-current.csv']),
    ('META/Tool-Executability-Audit-current.csv','tools/tool_executability_audit.py',['tools/generated_artifact_provenance.py','tools/lib_cube.py']),
    ('META/Identifier-Registry-current.csv','tools/identifier_namespace_audit.py',['Candidate-Ledger-current.csv','Office-Card-Index-current.csv','Source-Registry-current.csv','Claim-Ledger-current.csv','Evidence-Debt-current.csv','Refresh-Index-current.csv','META/Boundary-Domain-Registry-current.csv','META/Release-Gate-Attestation-current.csv','META/Policy-Assertion-Matrix-current.csv','META/Selftest-Coverage-Matrix-current.csv']),
    ('META/Identifier-Convention-Audit-current.csv','tools/identifier_namespace_audit.py',['META/Identifier-Registry-current.csv','Candidate-Ledger-current.csv','Office-Card-Index-current.csv','Source-Registry-current.csv','Claim-Ledger-current.csv','Evidence-Debt-current.csv','Refresh-Index-current.csv','META/Candidate-Boundary-Domain-Map-current.csv','META/Evidence-Debt-Sprint-current.csv','META/Policy-Assertion-Matrix-current.csv']),
    ('META/Candidate-Discovery-Intake-Audit-current.csv','tools/candidate_discovery_intake_audit.py',['META/Candidate-Discovery-Log-current.csv','Candidate-Ledger-current.csv','Source-Registry-current.csv','Office-Card-Index-current.csv','META/Claim-Evidence-Strength-current.csv','META/Public-Claim-Quarantine-current.csv','SCHEMA/Candidate-Discovery-Intake-Audit-Fields-current.csv']),
    ('META/Candidate-Source-Diversity-Audit-current.csv','tools/candidate_source_diversity_audit.py',['META/Candidate-Discovery-Log-current.csv','Candidate-Ledger-current.csv','Source-Registry-current.csv','Claim-Ledger-current.csv','SCHEMA/Candidate-Source-Diversity-Audit-Fields-current.csv']),
    ('META/Claim-Source-Boundary-Matrix-current.csv','tools/claim_source_boundary_audit.py',['Claim-Ledger-current.csv','Candidate-Ledger-current.csv','Source-Registry-current.csv','META/Public-Source-Link-Review-current.csv']),
    ('META/Claim-Source-Boundary-Audit-current.csv','tools/claim_source_boundary_audit.py',['Claim-Ledger-current.csv','Candidate-Ledger-current.csv','Source-Registry-current.csv','META/Public-Source-Link-Review-current.csv','META/Claim-Source-Boundary-Matrix-current.csv']),

]

def sha(path: Path) -> str:
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()

def csv_count(path: Path) -> int:
    if not path.exists() or path.suffix.lower()!='.csv': return 0
    with path.open(encoding='utf-8', newline='') as f:
        return max(0, sum(1 for _ in csv.reader(f))-1)

def fingerprint(root: Path, rels: list[str]) -> str:
    h=hashlib.sha256()
    for rel in sorted(rels):
        p=root/rel
        h.update(rel.encode('utf-8')+b'\0')
        if p.exists(): h.update(sha(p).encode('ascii'))
        else: h.update(b'MISSING')
    return h.hexdigest()

def run(root: Path):
    rows=[]
    for artifact, gen, inputs in ARTIFACTS:
        ap=root/artifact; gp=root/gen
        missing=[x for x in [artifact, gen, *inputs] if not (root/x).exists()]
        status='pass' if not missing else 'missing_dependency_or_artifact'
        note='inputs present; hash recorded' if not missing else 'missing: '+ '; '.join(missing[:8])
        rows.append({
            'artifact_path':artifact,
            'generator':gen,
            'input_paths':'|'.join(inputs),
            'artifact_sha256':sha(ap) if ap.exists() else '',
            'input_fingerprint':fingerprint(root, inputs+[gen]),
            'row_count':str(csv_count(ap)),
            'status':status,
            'note':note,
        })
    return rows

def write_reports(root: Path, rows):
    out=root/'META'; out.mkdir(exist_ok=True)
    with (out/'Generated-Artifact-Provenance-current.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows([{k:r.get(k,'') for k in FIELDS} for r in rows])
    (out/'Generated-Artifact-Provenance-current.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    bad=[r for r in rows if r.get('status')!='pass']
    lines=['# Generated Artifact Provenance — current','', 'Generated by `tools/generated_artifact_provenance.py`.', '', f'Artifacts tracked: {len(rows)}', f'Non-pass rows: {len(bad)}', '', '| artifact_path | generator | row_count | status |', '| --- | --- | ---: | --- |']
    for r in rows:
        lines.append(f"| {r['artifact_path']} | {r['generator']} | {r['row_count']} | {r['status']} |")
    (out/'Generated-Artifact-Provenance-current.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def verify(root: Path, rows=None):
    rows = rows if rows is not None else read_rows(root/'META/Generated-Artifact-Provenance-current.csv')
    findings=[]
    for r in rows:
        ap=root/r.get('artifact_path','')
        if not ap.exists():
            findings.append(f"missing artifact {r.get('artifact_path')}"); continue
        if sha(ap) != r.get('artifact_sha256'):
            findings.append(f"artifact hash drift {r.get('artifact_path')}")
        inputs=split(r.get('input_paths',''))+[r.get('generator','')]
        if fingerprint(root, inputs) != r.get('input_fingerprint'):
            findings.append(f"input fingerprint drift {r.get('artifact_path')}")
    return findings

def split(s: str): return [x for x in (s or '').split('|') if x]
def read_rows(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--verify', action='store_true'); ap.add_argument('--fail-on-drift', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve()
    if args.verify:
        drift=verify(root)
        if drift:
            for d in drift: print('DRIFT '+d)
            if args.fail_on_drift: sys.exit(1)
        else: print('PASS generated artifact provenance hashes and input fingerprints')
        return
    rows=run(root)
    if args.write_report: write_reports(root, rows)
    for r in rows: print(f"{r['status'].upper()} {r['artifact_path']} <- {r['generator']}")
    if args.fail_on_drift and any(r.get('status')!='pass' for r in rows): sys.exit(1)
if __name__=='__main__': main()
