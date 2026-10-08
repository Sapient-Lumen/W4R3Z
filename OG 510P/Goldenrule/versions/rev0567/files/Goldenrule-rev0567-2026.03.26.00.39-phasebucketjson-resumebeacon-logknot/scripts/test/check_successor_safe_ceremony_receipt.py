#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / 'schemas' / 'successor_safe_ceremony_receipt.schema.json'
LOCATOR_SCHEMA_PATH = ROOT / 'schemas' / 'successor_safe_ceremony_receipt_locator.schema.json'
ASSESSMENT_SCHEMA_PATH = ROOT / 'schemas' / 'successor_safe_ceremony_receipt_assessment.schema.json'
DISPOSITION_SCHEMA_PATH = ROOT / 'schemas' / 'successor_safe_ceremony_receipt_disposition.schema.json'
REMEDIATION_SCHEMA_PATH = ROOT / 'schemas' / 'successor_safe_ceremony_receipt_remediation_plan.schema.json'
AUTHORIZATION_SCHEMA_PATH = ROOT / 'schemas' / 'successor_safe_ceremony_receipt_authorization.schema.json'
PROMOTION_SCHEMA_PATH = ROOT / 'schemas' / 'successor_safe_ceremony_receipt_promotion.schema.json'
REVIEW_WATCH_SCHEMA_PATH = ROOT / 'schemas' / 'successor_safe_ceremony_receipt_review_watch.schema.json'
REVIEW_VERDICT_SCHEMA_PATH = ROOT / 'schemas' / 'successor_safe_ceremony_receipt_review_verdict.schema.json'
CITATION_ADVISORY_SCHEMA_PATH = ROOT / 'schemas' / 'successor_safe_ceremony_receipt_citation_advisory.schema.json'
PACKAGE_MANIFEST_SCHEMA_PATH = ROOT / 'schemas' / 'successor_safe_ceremony_receipt_package_manifest.schema.json'
PACKAGE_SUPERSESSION_SCHEMA_PATH = ROOT / 'schemas' / 'successor_safe_ceremony_receipt_package_supersession.schema.json'
PACKAGE_LINEAGE_SCHEMA_PATH = ROOT / 'schemas' / 'successor_safe_ceremony_receipt_package_lineage.schema.json'
PACKAGE_HEAD_SCHEMA_PATH = ROOT / 'schemas' / 'successor_safe_ceremony_receipt_package_head.schema.json'
PACKAGE_STATUS_CARD_SCHEMA_PATH = ROOT / 'schemas' / 'successor_safe_ceremony_receipt_package_status_card.schema.json'
PACKAGE_REDIRECT_SCHEMA_PATH = ROOT / 'schemas' / 'successor_safe_ceremony_receipt_package_redirect.schema.json'
PACKAGE_CATALOG_SCHEMA_PATH = ROOT / 'schemas' / 'successor_safe_ceremony_receipt_package_catalog.schema.json'
PACKAGE_VERIFICATION_REPORT_SCHEMA_PATH = ROOT / 'schemas' / 'successor_safe_ceremony_receipt_package_verification_report.schema.json'
PACKAGE_CLAIM_SCOPE_SCHEMA_PATH = ROOT / 'schemas' / 'successor_safe_ceremony_receipt_package_claim_scope.schema.json'
PACKAGE_RELIANCE_CARD_SCHEMA_PATH = ROOT / 'schemas' / 'successor_safe_ceremony_receipt_package_reliance_card.schema.json'
EXAMPLE_JSON = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.json'
EXAMPLE_MD = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.md'
EXAMPLE_LOCATOR = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.locator.json'
EXAMPLE_ASSESSMENT = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.assessment.json'
EXAMPLE_DISPOSITION = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.disposition.json'
EXAMPLE_REMEDIATION = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.remediation.json'
EXAMPLE_AUTHORIZATION = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.authorization.json'
EXAMPLE_PLACEHOLDER = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_placeholder.json'
EXAMPLE_PROMOTION = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.promotion.json'
EXAMPLE_REVIEW_WATCH = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.review_watch.json'
EXAMPLE_REVIEW_VERDICT = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.review_verdict.json'
TOOL = ROOT / 'scripts' / 'tools' / 'successor_safe_ceremony_receipt.py'
EXAMPLE_CITATION_ADVISORY = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.citation_advisory.json'
EXAMPLE_PACKAGE_MANIFEST = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.package_manifest.json'
EXAMPLE_REVIEW_WATCH_REFRESHED = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.review_watch_refreshed.json'
EXAMPLE_REVIEW_VERDICT_REFRESHED = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.review_verdict_refreshed.json'
EXAMPLE_CITATION_ADVISORY_REFRESHED = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.citation_advisory_refreshed.json'
EXAMPLE_PACKAGE_MANIFEST_REFRESHED = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.package_manifest_refreshed.json'
EXAMPLE_PACKAGE_SUPERSESSION = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.package_supersession.json'
EXAMPLE_PACKAGE_LINEAGE = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.package_lineage.json'
EXAMPLE_PACKAGE_STATUS_CARD = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.package_status_card.json'
EXAMPLE_PACKAGE_HEAD = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.package_head.json'
EXAMPLE_PACKAGE_REDIRECT = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.package_redirect.json'
EXAMPLE_PACKAGE_CATALOG = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.package_catalog.json'
EXAMPLE_PACKAGE_VERIFICATION_REPORT = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.package_verification_report.json'
EXAMPLE_PACKAGE_CLAIM_SCOPE = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.package_claim_scope.json'
EXAMPLE_PACKAGE_RELIANCE_CARD = ROOT / 'examples' / 'snapshots' / 'successor_safe_ceremony_receipt_example.package_reliance_card.json'
TOOL = ROOT / 'scripts' / 'tools' / 'successor_safe_ceremony_receipt.py'


def fail(msg: str) -> int:
    print(f'successor-safe-ceremony-receipt: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def load_tool_module():
    spec = importlib.util.spec_from_file_location('successor_safe_ceremony_receipt_tool', TOOL)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    locator_schema = load_json(LOCATOR_SCHEMA_PATH)
    assessment_schema = load_json(ASSESSMENT_SCHEMA_PATH)
    disposition_schema = load_json(DISPOSITION_SCHEMA_PATH)
    remediation_schema = load_json(REMEDIATION_SCHEMA_PATH)
    authorization_schema = load_json(AUTHORIZATION_SCHEMA_PATH)
    promotion_schema = load_json(PROMOTION_SCHEMA_PATH)
    review_watch_schema = load_json(REVIEW_WATCH_SCHEMA_PATH)
    review_verdict_schema = load_json(REVIEW_VERDICT_SCHEMA_PATH)
    citation_advisory_schema = load_json(CITATION_ADVISORY_SCHEMA_PATH)
    package_manifest_schema = load_json(PACKAGE_MANIFEST_SCHEMA_PATH)
    package_supersession_schema = load_json(PACKAGE_SUPERSESSION_SCHEMA_PATH)
    package_lineage_schema = load_json(PACKAGE_LINEAGE_SCHEMA_PATH)
    package_head_schema = load_json(PACKAGE_HEAD_SCHEMA_PATH)
    package_status_card_schema = load_json(PACKAGE_STATUS_CARD_SCHEMA_PATH)
    package_redirect_schema = load_json(PACKAGE_REDIRECT_SCHEMA_PATH)
    package_catalog_schema = load_json(PACKAGE_CATALOG_SCHEMA_PATH)
    package_verification_report_schema = load_json(PACKAGE_VERIFICATION_REPORT_SCHEMA_PATH)
    package_claim_scope_schema = load_json(PACKAGE_CLAIM_SCOPE_SCHEMA_PATH)
    package_reliance_card_schema = load_json(PACKAGE_RELIANCE_CARD_SCHEMA_PATH)
    example = load_json(EXAMPLE_JSON)
    example_locator = load_json(EXAMPLE_LOCATOR)
    example_assessment = load_json(EXAMPLE_ASSESSMENT)
    example_disposition = load_json(EXAMPLE_DISPOSITION)
    example_remediation = load_json(EXAMPLE_REMEDIATION)
    example_authorization = load_json(EXAMPLE_AUTHORIZATION)
    example_placeholder = load_json(EXAMPLE_PLACEHOLDER)
    example_promotion = load_json(EXAMPLE_PROMOTION)
    example_review_watch = load_json(EXAMPLE_REVIEW_WATCH)
    example_review_verdict = load_json(EXAMPLE_REVIEW_VERDICT)
    tool = load_tool_module()
    example_citation_advisory = load_json(EXAMPLE_CITATION_ADVISORY)
    example_package_manifest = load_json(EXAMPLE_PACKAGE_MANIFEST)
    example_review_watch_refreshed = load_json(EXAMPLE_REVIEW_WATCH_REFRESHED)
    example_review_verdict_refreshed = load_json(EXAMPLE_REVIEW_VERDICT_REFRESHED)
    example_citation_advisory_refreshed = load_json(EXAMPLE_CITATION_ADVISORY_REFRESHED)
    example_package_manifest_refreshed = load_json(EXAMPLE_PACKAGE_MANIFEST_REFRESHED)
    example_package_supersession = load_json(EXAMPLE_PACKAGE_SUPERSESSION)
    example_package_lineage = load_json(EXAMPLE_PACKAGE_LINEAGE)
    example_package_status_card = load_json(EXAMPLE_PACKAGE_STATUS_CARD)
    example_package_head = load_json(EXAMPLE_PACKAGE_HEAD)
    example_package_redirect = load_json(EXAMPLE_PACKAGE_REDIRECT)
    example_package_catalog = load_json(EXAMPLE_PACKAGE_CATALOG)
    example_package_verification_report = load_json(EXAMPLE_PACKAGE_VERIFICATION_REPORT)
    example_package_claim_scope = load_json(EXAMPLE_PACKAGE_CLAIM_SCOPE)
    example_package_reliance_card = load_json(EXAMPLE_PACKAGE_RELIANCE_CARD)
    tool = load_tool_module()

    titles = {
        schema.get('title'): 'Successor-Safe Ceremony Receipt',
        locator_schema.get('title'): 'Successor-Safe Ceremony Receipt Locator',
        assessment_schema.get('title'): 'Successor-Safe Ceremony Receipt Assessment',
        disposition_schema.get('title'): 'Successor-Safe Ceremony Receipt Disposition',
        remediation_schema.get('title'): 'Successor-Safe Ceremony Receipt Remediation Plan',
        authorization_schema.get('title'): 'Successor-Safe Ceremony Receipt Authorization',
        promotion_schema.get('title'): 'Successor-Safe Ceremony Receipt Promotion',
        review_watch_schema.get('title'): 'Successor-Safe Ceremony Receipt Review Watch',
        review_verdict_schema.get('title'): 'Successor-Safe Ceremony Receipt Review Verdict',
        citation_advisory_schema.get('title'): 'Successor-Safe Ceremony Receipt Citation Advisory',
        package_manifest_schema.get('title'): 'Successor-Safe Ceremony Receipt Package Manifest',
        package_supersession_schema.get('title'): 'Successor-Safe Ceremony Receipt Package Supersession',
        package_lineage_schema.get('title'): 'Successor-Safe Ceremony Receipt Package Lineage',
        package_head_schema.get('title'): 'Successor-Safe Ceremony Receipt Package Head',
        package_status_card_schema.get('title'): 'Successor-Safe Ceremony Receipt Package Status Card',
        package_redirect_schema.get('title'): 'Successor-Safe Ceremony Receipt Package Redirect',
        package_catalog_schema.get('title'): 'Successor-Safe Ceremony Receipt Package Catalog',
        package_verification_report_schema.get('title'): 'Successor-Safe Ceremony Receipt Package Verification Report',
        package_claim_scope_schema.get('title'): 'Successor-Safe Ceremony Receipt Package Claim Scope',
        package_reliance_card_schema.get('title'): 'Successor-Safe Ceremony Receipt Package Reliance Card',
    }
    if len(titles) != 20 or any(k != v for k, v in titles.items()):
        return fail('one or more schema titles drifted')

    jsonschema.Draft202012Validator(schema).validate(example)
    jsonschema.Draft202012Validator(locator_schema).validate(example_locator)
    jsonschema.Draft202012Validator(assessment_schema).validate(example_assessment)
    jsonschema.Draft202012Validator(disposition_schema).validate(example_disposition)
    jsonschema.Draft202012Validator(remediation_schema).validate(example_remediation)
    jsonschema.Draft202012Validator(authorization_schema).validate(example_authorization)
    jsonschema.Draft202012Validator(schema).validate(example_placeholder)
    jsonschema.Draft202012Validator(promotion_schema).validate(example_promotion)
    jsonschema.Draft202012Validator(review_watch_schema).validate(example_review_watch)
    jsonschema.Draft202012Validator(review_verdict_schema).validate(example_review_verdict)
    jsonschema.Draft202012Validator(citation_advisory_schema).validate(example_citation_advisory)
    jsonschema.Draft202012Validator(package_manifest_schema).validate(example_package_manifest)
    jsonschema.Draft202012Validator(review_watch_schema).validate(example_review_watch_refreshed)
    jsonschema.Draft202012Validator(review_verdict_schema).validate(example_review_verdict_refreshed)
    jsonschema.Draft202012Validator(citation_advisory_schema).validate(example_citation_advisory_refreshed)
    jsonschema.Draft202012Validator(package_manifest_schema).validate(example_package_manifest_refreshed)
    jsonschema.Draft202012Validator(package_supersession_schema).validate(example_package_supersession)
    jsonschema.Draft202012Validator(package_lineage_schema).validate(example_package_lineage)
    jsonschema.Draft202012Validator(package_status_card_schema).validate(example_package_status_card)
    jsonschema.Draft202012Validator(package_head_schema).validate(example_package_head)
    jsonschema.Draft202012Validator(package_redirect_schema).validate(example_package_redirect)
    jsonschema.Draft202012Validator(package_catalog_schema).validate(example_package_catalog)
    jsonschema.Draft202012Validator(package_verification_report_schema).validate(example_package_verification_report)
    jsonschema.Draft202012Validator(package_claim_scope_schema).validate(example_package_claim_scope)
    jsonschema.Draft202012Validator(package_reliance_card_schema).validate(example_package_reliance_card)

    if example['journey_kind'] != 'presentation':
        return fail('example should use a presentation journey kind')
    if 'cross-device' not in example['ceremony_topology']['field_one']:
        return fail('example should explicitly preserve device split semantics')
    if 'wallet-native approval sheet' not in example['approval_surface']['field_one']:
        return fail('example should preserve trusted renderer semantics')
    if 'request_uri' not in example['delivery_path']['field_one']:
        return fail('example should preserve request carriage semantics')
    if example_placeholder['id'] != example['id']:
        return fail('placeholder should preserve the same receipt id for promotion comparisons')
    if example_promotion['promotion_decision'] != 'promoted_to_claim_ready_citation':
        return fail('worked promotion snapshot should show promotion to claim-ready citation')
    if example_promotion['closed_finding_codes'] != ['placeholder_free']:
        return fail('worked promotion snapshot should close the scaffold placeholder finding')
    if example_promotion['newly_opened_finding_codes'] != [] or example_promotion['failed_basis_codes'] != []:
        return fail('worked promotion snapshot should be clean')
    if example_review_watch['watch_status'] != 'active_watch' or example_review_watch['failed_basis_codes'] != []:
        return fail('worked review-watch snapshot should stay active and clean')
    if example_review_watch['reviewed_on'] != '2026-03-22' or example_review_watch['review_due_on'] != '2026-09-18':
        return fail('worked review-watch snapshot should preserve the reviewed and due dates')
    if example_review_verdict['review_decision'] != 'continue_claim_ready_citation' or example_review_verdict['citation_status'] != 'claim_ready_citable':
        return fail('worked review-verdict snapshot should preserve keep-citing semantics')
    if example_review_verdict['required_regeneration_sequence'] != []:
        return fail('worked review-verdict snapshot should not require regeneration')
    if example_citation_advisory['advisory_decision'] != 'keep_current_locator_citable' or example_citation_advisory['new_citations_action'] != 'cite_reviewed_locator':
        return fail('worked citation-advisory snapshot should preserve keep-citing semantics')
    if example_citation_advisory['required_follow_up'] != []:
        return fail('worked citation-advisory snapshot should not require follow-up regeneration')
    if example_package_manifest['current_claim_status'] != 'claim_ready_citable':
        return fail('worked package-manifest snapshot should preserve claim-ready status')
    if example_package_manifest_refreshed['current_claim_status'] != 'claim_ready_citable':
        return fail('refreshed package-manifest snapshot should preserve claim-ready status')
    if example_review_watch_refreshed['reviewed_on'] != '2026-09-10' or example_review_watch_refreshed['review_due_on'] != '2027-03-09':
        return fail('refreshed review-watch snapshot should preserve the rolled-forward review window')
    if example_package_supersession['active_receipt_locator_continuity']['continuity'] != 'same_receipt_locator':
        return fail('worked package-supersession snapshot should preserve same-locator continuity')
    if example_package_supersession['component_roles_replaced'] != ['citation_advisory', 'review_verdict', 'review_watch']:
        return fail('worked package-supersession snapshot should preserve the refreshed package roles')
    if example_package_lineage['authoritative_manifest']['path'] != 'examples/snapshots/successor_safe_ceremony_receipt_example.package_manifest_refreshed.json':
        return fail('worked package-lineage snapshot should point at the refreshed manifest as authoritative')
    if [row['path'] for row in example_package_lineage['manifest_chain']] != [
        'examples/snapshots/successor_safe_ceremony_receipt_example.package_manifest.json',
        'examples/snapshots/successor_safe_ceremony_receipt_example.package_manifest_refreshed.json',
    ]:
        return fail('worked package-lineage snapshot should preserve the ordered manifest chain')
    if [row['path'] for row in example_package_lineage['supersession_chain']] != [
        'examples/snapshots/successor_safe_ceremony_receipt_example.package_supersession.json',
    ]:
        return fail('worked package-lineage snapshot should preserve the ordered supersession chain')
    if example_package_lineage['lineage_continuity']['continuity'] != 'same_receipt_locator_across_chain':
        return fail('worked package-lineage snapshot should preserve same-locator continuity across the chain')
    if example_package_status_card['authoritative_manifest']['path'] != 'examples/snapshots/successor_safe_ceremony_receipt_example.package_manifest_refreshed.json':
        return fail('worked package-status-card snapshot should point at the refreshed manifest as authoritative')
    if example_package_status_card['currently_citable'] is not True:
        return fail('worked package-status-card snapshot should preserve current citable status')
    if example_package_status_card['current_review_window']['review_due_on'] != '2027-03-09':
        return fail('worked package-status-card snapshot should preserve the rolled-forward review window')
    if example_package_status_card['citation_guidance']['new_citations_action'] != 'cite_reviewed_locator':
        return fail('worked package-status-card snapshot should preserve keep-citing guidance for new citations')
    if [key for key in example_package_status_card['status_inputs'].keys()] != ['review_watch', 'review_verdict', 'citation_advisory']:
        return fail('worked package-status-card snapshot should preserve the live status input set')
    if example_package_verification_report['verification_decision'] != 'verified_python_lane_only':
        return fail('worked package-verification-report snapshot should preserve the python-lane-only verification decision in this cloudtainer')
    if example_package_verification_report['summary_counts'] != {'pass_count': 5, 'blocked_count': 2, 'fail_count': 0}:
        return fail('worked package-verification-report snapshot should preserve the expected pass/blocked/fail counts')
    if example_package_verification_report['environment_boundary']['missing_tools'] != ['cargo', 'junest']:
        return fail('worked package-verification-report snapshot should preserve the missing cargo/junest boundary')
    if [row['status'] for row in example_package_verification_report['checks']] != ['pass', 'pass', 'pass', 'pass', 'pass', 'blocked', 'blocked']:
        return fail('worked package-verification-report snapshot should preserve the expected local check status sequence')
    if example_package_claim_scope['claim_scope_decision'] != 'citation_allowed_non_runtime_claims_only':
        return fail('worked package-claim-scope snapshot should preserve the non-runtime claim-scope decision in this cloudtainer')
    if example_package_claim_scope['allowed_claim_classes'] != ['current_package_identity', 'current_locator_identity', 'current_citation_posture', 'current_review_window', 'python_integrity_results']:
        return fail('worked package-claim-scope snapshot should preserve the allowed non-runtime claim classes')
    if example_package_claim_scope['restricted_claim_classes'] != ['full_local_validation_profile', 'rust_execution_results', 'engine_behavior_runtime_claims']:
        return fail('worked package-claim-scope snapshot should preserve the restricted runtime claim classes')
    if example_package_claim_scope['broader_claims_requirements'] != ['rerun_doctor_after_cargo_available', 'rerun_quick_harness_after_junest_available']:
        return fail('worked package-claim-scope snapshot should preserve the blocked follow-up requirements for broader claims')
    if example_package_reliance_card['reliance_decision'] != 'rely_with_non_runtime_scope_only':
        return fail('worked package-reliance-card snapshot should preserve the non-runtime reliance decision in this cloudtainer')
    if example_package_reliance_card['verification_basis'] != {'verification_decision': 'verified_python_lane_only', 'pass_count': 5, 'blocked_count': 2, 'fail_count': 0, 'missing_tools': ['cargo', 'junest']}:
        return fail('worked package-reliance-card snapshot should preserve the current verification basis summary')
    if example_package_reliance_card['allowed_claim_classes'] != example_package_claim_scope['allowed_claim_classes']:
        return fail('worked package-reliance-card snapshot should preserve the claim-scope allowed claim classes')
    if example_package_reliance_card['restricted_claim_classes'] != example_package_claim_scope['restricted_claim_classes']:
        return fail('worked package-reliance-card snapshot should preserve the claim-scope restricted claim classes')
    if example_package_head['authoritative_manifest']['path'] != 'examples/snapshots/successor_safe_ceremony_receipt_example.package_manifest_refreshed.json':
        return fail('worked package-head snapshot should point at the refreshed manifest as authoritative')
    if example_package_head['current_reliance_card']['path'] != 'examples/snapshots/successor_safe_ceremony_receipt_example.package_reliance_card.json':
        return fail('worked package-head snapshot should point at the live package-reliance-card')
    if example_package_redirect['source_package_manifest']['path'] != 'examples/snapshots/successor_safe_ceremony_receipt_example.package_manifest.json':
        return fail('worked package-redirect snapshot should point at the superseded manifest as its source')
    if example_package_redirect['preferred_reference_target']['path'] != 'examples/snapshots/successor_safe_ceremony_receipt_example.package_head.json':
        return fail('worked package-redirect snapshot should point at the current package-head as the preferred reference target')
    if example_package_redirect['successor_package_manifest']['path'] != 'examples/snapshots/successor_safe_ceremony_receipt_example.package_manifest_refreshed.json':
        return fail('worked package-redirect snapshot should point at the refreshed manifest as the successor package')
    if example_package_redirect['supporting_status_card']['path'] != 'examples/snapshots/successor_safe_ceremony_receipt_example.package_status_card.json':
        return fail('worked package-redirect snapshot should point at the live package-status-card')
    if example_package_catalog['package_families'][0]['current_package_reliance_card']['path'] != 'examples/snapshots/successor_safe_ceremony_receipt_example.package_reliance_card.json':
        return fail('worked package-catalog snapshot should point at the live package-reliance-card for the family')
    if [row['rel'] for row in example_package_redirect['redirect_links']] != ['cite-as', 'successor-version', 'latest-version', 'status', 'describedby']:
        return fail('worked package-redirect snapshot should preserve the expected redirect link relations')
    if [row['target_kind'] for row in example_package_redirect['redirect_links']] != ['package_head', 'package_manifest', 'package_manifest', 'package_status_card', 'package_supersession']:
        return fail('worked package-redirect snapshot should preserve the expected redirect link targets')
    if example_package_catalog['catalog_summary']['package_family_count'] != 1 or example_package_catalog['catalog_summary']['superseded_redirect_count'] != 1:
        return fail('worked package-catalog snapshot should preserve one family and one superseded redirect')
    if example_package_catalog['package_families'][0]['current_package_head']['path'] != 'examples/snapshots/successor_safe_ceremony_receipt_example.package_head.json':
        return fail('worked package-catalog snapshot should point at the live package head')
    if example_package_catalog['package_families'][0]['current_citation_state'] != 'citable_now':
        return fail('worked package-catalog snapshot should preserve the current citable-now state')
    if example_package_catalog['package_families'][0]['superseded_redirect_count'] != 1:
        return fail('worked package-catalog snapshot should preserve one redirect for the worked family')
    if [row['rel'] for row in example_package_catalog['package_families'][0]['member_links']] != ['item', 'latest-version', 'version-history', 'status', 'describedby']:
        return fail('worked package-catalog snapshot should preserve family member link relations')
    if example_package_catalog['superseded_package_redirects'][0]['source_package_manifest']['path'] != 'examples/snapshots/successor_safe_ceremony_receipt_example.package_manifest.json':
        return fail('worked package-catalog snapshot should index the superseded package manifest')
    if example_package_catalog['superseded_package_redirects'][0]['redirect_artifact']['path'] != 'examples/snapshots/successor_safe_ceremony_receipt_example.package_redirect.json':
        return fail('worked package-catalog snapshot should index the package redirect artifact')
    if [row['rel'] for row in example_package_catalog['catalog_links']] != ['item']:
        return fail('worked package-catalog snapshot should preserve catalog-level item links')
    if example_package_head['current_status_card']['path'] != 'examples/snapshots/successor_safe_ceremony_receipt_example.package_status_card.json':
        return fail('worked package-head snapshot should point at the live package-status-card record')
    if example_package_head['current_verification_report']['path'] != 'examples/snapshots/successor_safe_ceremony_receipt_example.package_verification_report.json':
        return fail('worked package-head snapshot should point at the live package-verification-report record')
    if example_package_head['package_lineage']['path'] != 'examples/snapshots/successor_safe_ceremony_receipt_example.package_lineage.json':
        return fail('worked package-head snapshot should point at the lineage record')
    if [row['rel'] for row in example_package_head['discovery_links']] != ['latest-version', 'version-history', 'describedby', 'describedby', 'describedby', 'describedby', 'describedby', 'status', 'predecessor-version']:
        return fail('worked package-head snapshot should preserve the expected discovery link relations')
    if [row['target_kind'] for row in example_package_head['discovery_links']] != ['package_manifest', 'package_lineage', 'review_verdict', 'citation_advisory', 'package_verification_report', 'package_claim_scope', 'package_reliance_card', 'package_status_card', 'previous_package_manifest']:
        return fail('worked package-head snapshot should preserve the expected discovery link targets')
    if example_package_manifest['component_roles_present'] != [
        'receipt',
        'rendered_markdown',
        'locator',
        'assessment',
        'disposition',
        'remediation',
        'authorization',
        'promotion',
        'review_watch',
        'review_verdict',
        'citation_advisory',
    ]:
        return fail('worked package-manifest snapshot should preserve the full authoritative component set')

    required_codes = {
        'placeholder_free',
        'verifier_binding_explicit',
        'session_binding_explicit',
        'by_reference_request_integrity_named',
        'direct_post_session_mapping_named',
        'cross_device_participation_named',
        'dispatch_assurance_named',
        'trusted_renderer_named',
        'retained_evidence_fixity_named',
    }
    if {row['code'] for row in example_assessment['findings']} != required_codes:
        return fail('assessment finding set drift detected')

    placeholder_generated = tool.scaffold_receipt(example['id'], example['journey_kind'])
    if placeholder_generated != example_placeholder:
        return fail('placeholder scaffold drift detected; regenerate committed placeholder snapshot via the tooling script')

    scaffold = tool.scaffold_receipt('scaffold-example', 'authorization')
    jsonschema.Draft202012Validator(schema).validate(scaffold)
    if 'not applicable' not in scaffold['notes'].lower():
        return fail('scaffold notes should mention explicit not applicable handling')
    if 'replace with the explicit ceremony contract' not in scaffold['authoritative_request']['field_one']:
        return fail('scaffold should force explicit contract replacement language')

    if tool.render_markdown(example) != EXAMPLE_MD.read_text(encoding='utf-8'):
        return fail('rendered example markdown drift detected; regenerate snapshot via the tooling script')

    actual_locator = tool.make_locator(example, 'examples/snapshots/successor_safe_ceremony_receipt_example.json')
    if actual_locator != example_locator:
        return fail('locator snapshot drift detected; regenerate snapshot via the tooling script')

    actual_assessment = tool.assess_receipt(example, 'examples/snapshots/successor_safe_ceremony_receipt_example.json')
    if actual_assessment != example_assessment:
        return fail('assessment snapshot drift detected; regenerate snapshot via the tooling script')

    actual_disposition = tool.make_disposition(example_assessment, example_locator)
    if actual_disposition != example_disposition:
        return fail('disposition snapshot drift detected; regenerate snapshot via the tooling script')

    actual_remediation = tool.make_remediation_plan(example_assessment, example_locator, example_disposition)
    if actual_remediation != example_remediation:
        return fail('remediation snapshot drift detected; regenerate snapshot via the tooling script')

    actual_authorization = tool.make_authorization(example_assessment, example_locator, example_disposition, example_remediation)
    if actual_authorization != example_authorization:
        return fail('authorization snapshot drift detected; regenerate snapshot via the tooling script')

    placeholder_locator = tool.make_locator(example_placeholder, 'examples/snapshots/successor_safe_ceremony_receipt_placeholder.json')
    placeholder_assessment = tool.assess_receipt(example_placeholder, 'examples/snapshots/successor_safe_ceremony_receipt_placeholder.json')
    placeholder_disposition = tool.make_disposition(placeholder_assessment, placeholder_locator)
    placeholder_remediation = tool.make_remediation_plan(placeholder_assessment, placeholder_locator, placeholder_disposition)
    placeholder_authorization = tool.make_authorization(placeholder_assessment, placeholder_locator, placeholder_disposition, placeholder_remediation)
    actual_promotion = tool.make_promotion(placeholder_assessment, placeholder_locator, placeholder_authorization, example_assessment, example_locator, example_authorization)
    if actual_promotion != example_promotion:
        return fail('promotion snapshot drift detected; regenerate snapshot via the tooling script')

    actual_review_watch = tool.make_review_watch(example_authorization, example_promotion, reviewed_on='2026-03-22', max_review_interval_days=180)
    if actual_review_watch != example_review_watch:
        return fail('review-watch snapshot drift detected; regenerate snapshot via the tooling script')

    actual_review_verdict = tool.make_review_verdict(example_review_watch, as_of='2026-03-22')
    if actual_review_verdict != example_review_verdict:
        return fail('review-verdict snapshot drift detected; regenerate snapshot via the tooling script')

    actual_citation_advisory = tool.make_citation_advisory(example_review_verdict)
    if actual_citation_advisory != example_citation_advisory:
        return fail('citation-advisory snapshot drift detected; regenerate snapshot via the tooling script')

    actual_package_manifest = tool.make_package_manifest(
        receipt_path=EXAMPLE_JSON,
        rendered_markdown_path=EXAMPLE_MD,
        locator_path=EXAMPLE_LOCATOR,
        assessment_path=EXAMPLE_ASSESSMENT,
        disposition_path=EXAMPLE_DISPOSITION,
        remediation_path=EXAMPLE_REMEDIATION,
        authorization_path=EXAMPLE_AUTHORIZATION,
        promotion_path=EXAMPLE_PROMOTION,
        review_watch_path=EXAMPLE_REVIEW_WATCH,
        review_verdict_path=EXAMPLE_REVIEW_VERDICT,
        citation_advisory_path=EXAMPLE_CITATION_ADVISORY,
    )
    if actual_package_manifest != example_package_manifest:
        return fail('package-manifest snapshot drift detected; regenerate snapshot via the tooling script')

    actual_review_watch_refreshed = tool.make_review_watch(example_authorization, example_promotion, reviewed_on='2026-09-10', max_review_interval_days=180)
    if actual_review_watch_refreshed != example_review_watch_refreshed:
        return fail('refreshed review-watch snapshot drift detected; regenerate snapshot via the tooling script')

    actual_review_verdict_refreshed = tool.make_review_verdict(example_review_watch_refreshed, as_of='2026-09-10')
    if actual_review_verdict_refreshed != example_review_verdict_refreshed:
        return fail('refreshed review-verdict snapshot drift detected; regenerate snapshot via the tooling script')

    actual_citation_advisory_refreshed = tool.make_citation_advisory(example_review_verdict_refreshed)
    if actual_citation_advisory_refreshed != example_citation_advisory_refreshed:
        return fail('refreshed citation-advisory snapshot drift detected; regenerate snapshot via the tooling script')

    actual_package_manifest_refreshed = tool.make_package_manifest(
        receipt_path=EXAMPLE_JSON,
        rendered_markdown_path=EXAMPLE_MD,
        locator_path=EXAMPLE_LOCATOR,
        assessment_path=EXAMPLE_ASSESSMENT,
        disposition_path=EXAMPLE_DISPOSITION,
        remediation_path=EXAMPLE_REMEDIATION,
        authorization_path=EXAMPLE_AUTHORIZATION,
        promotion_path=EXAMPLE_PROMOTION,
        review_watch_path=EXAMPLE_REVIEW_WATCH_REFRESHED,
        review_verdict_path=EXAMPLE_REVIEW_VERDICT_REFRESHED,
        citation_advisory_path=EXAMPLE_CITATION_ADVISORY_REFRESHED,
    )
    if actual_package_manifest_refreshed != example_package_manifest_refreshed:
        return fail('refreshed package-manifest snapshot drift detected; regenerate snapshot via the tooling script')

    actual_package_supersession = tool.make_package_supersession(
        prior_manifest_path=EXAMPLE_PACKAGE_MANIFEST,
        current_manifest_path=EXAMPLE_PACKAGE_MANIFEST_REFRESHED,
        prior_review_watch_path=EXAMPLE_REVIEW_WATCH,
        current_review_watch_path=EXAMPLE_REVIEW_WATCH_REFRESHED,
        prior_review_verdict_path=EXAMPLE_REVIEW_VERDICT,
        current_review_verdict_path=EXAMPLE_REVIEW_VERDICT_REFRESHED,
        prior_citation_advisory_path=EXAMPLE_CITATION_ADVISORY,
        current_citation_advisory_path=EXAMPLE_CITATION_ADVISORY_REFRESHED,
    )
    if actual_package_supersession != example_package_supersession:
        return fail('package-supersession snapshot drift detected; regenerate snapshot via the tooling script')

    actual_package_lineage = tool.make_package_lineage(
        manifest_paths=[EXAMPLE_PACKAGE_MANIFEST, EXAMPLE_PACKAGE_MANIFEST_REFRESHED],
        supersession_paths=[EXAMPLE_PACKAGE_SUPERSESSION],
    )
    if actual_package_lineage != example_package_lineage:
        return fail('package-lineage snapshot drift detected; regenerate snapshot via the tooling script')

    actual_package_status_card = tool.make_package_status_card(
        manifest_path=EXAMPLE_PACKAGE_MANIFEST_REFRESHED,
        review_watch_path=EXAMPLE_REVIEW_WATCH_REFRESHED,
        review_verdict_path=EXAMPLE_REVIEW_VERDICT_REFRESHED,
        citation_advisory_path=EXAMPLE_CITATION_ADVISORY_REFRESHED,
    )
    if actual_package_status_card != example_package_status_card:
        return fail('package-status-card snapshot drift detected; regenerate snapshot via the tooling script')

    actual_package_verification_report = tool.make_package_verification_report(
        manifest_path=EXAMPLE_PACKAGE_MANIFEST_REFRESHED,
        status_card_path=EXAMPLE_PACKAGE_STATUS_CARD,
        as_of='2026-03-22',
    )
    if actual_package_verification_report != example_package_verification_report:
        return fail('package-verification-report snapshot drift detected; regenerate snapshot via the tooling script')

    actual_package_claim_scope = tool.make_package_claim_scope(
        manifest_path=EXAMPLE_PACKAGE_MANIFEST_REFRESHED,
        status_card_path=EXAMPLE_PACKAGE_STATUS_CARD,
        verification_report_path=EXAMPLE_PACKAGE_VERIFICATION_REPORT,
    )
    if actual_package_claim_scope != example_package_claim_scope:
        return fail('package-claim-scope snapshot drift detected; regenerate snapshot via the tooling script')

    actual_package_reliance_card = tool.make_package_reliance_card(
        manifest_path=EXAMPLE_PACKAGE_MANIFEST_REFRESHED,
        status_card_path=EXAMPLE_PACKAGE_STATUS_CARD,
        verification_report_path=EXAMPLE_PACKAGE_VERIFICATION_REPORT,
        claim_scope_path=EXAMPLE_PACKAGE_CLAIM_SCOPE,
    )
    if actual_package_reliance_card != example_package_reliance_card:
        return fail('package-reliance-card snapshot drift detected; regenerate snapshot via the tooling script')

    actual_package_head = tool.make_package_head(
        manifest_path=EXAMPLE_PACKAGE_MANIFEST_REFRESHED,
        lineage_path=EXAMPLE_PACKAGE_LINEAGE,
        review_verdict_path=EXAMPLE_REVIEW_VERDICT_REFRESHED,
        citation_advisory_path=EXAMPLE_CITATION_ADVISORY_REFRESHED,
        status_card_path=EXAMPLE_PACKAGE_STATUS_CARD,
        verification_report_path=EXAMPLE_PACKAGE_VERIFICATION_REPORT,
        claim_scope_path=EXAMPLE_PACKAGE_CLAIM_SCOPE,
        reliance_card_path=EXAMPLE_PACKAGE_RELIANCE_CARD,
    )
    if actual_package_head != example_package_head:
        return fail('package-head snapshot drift detected; regenerate snapshot via the tooling script')

    actual_package_redirect = tool.make_package_redirect(
        prior_manifest_path=EXAMPLE_PACKAGE_MANIFEST,
        supersession_path=EXAMPLE_PACKAGE_SUPERSESSION,
        current_head_path=EXAMPLE_PACKAGE_HEAD,
        current_status_card_path=EXAMPLE_PACKAGE_STATUS_CARD,
    )
    if actual_package_redirect != example_package_redirect:
        return fail('package-redirect snapshot drift detected; regenerate snapshot via the tooling script')

    actual_package_catalog = tool.make_package_catalog(
        head_paths=[EXAMPLE_PACKAGE_HEAD],
        redirect_paths=[EXAMPLE_PACKAGE_REDIRECT],
    )
    if actual_package_catalog != example_package_catalog:
        return fail('package-catalog snapshot drift detected; regenerate snapshot via the tooling script')

    scaffold_assessment = tool.assess_receipt(scaffold, 'tmp/scaffold.json')
    jsonschema.Draft202012Validator(assessment_schema).validate(scaffold_assessment)
    if scaffold_assessment['overall_status'] != 'fail' or scaffold_assessment['counts']['hard_fail_count'] < 1:
        return fail('scaffold assessment should fail because placeholders remain')

    scaffold_locator = tool.make_locator(scaffold, 'tmp/scaffold.json')
    scaffold_disposition = tool.make_disposition(scaffold_assessment, scaffold_locator)
    jsonschema.Draft202012Validator(disposition_schema).validate(scaffold_disposition)
    if scaffold_disposition['archive_admission'] != 'hold_for_remediation':
        return fail('scaffold disposition should hold for remediation')
    if scaffold_disposition['copy_forward_rule'] != 'hold_until_remediated':
        return fail('scaffold disposition should hold until remediated')

    scaffold_remediation = tool.make_remediation_plan(scaffold_assessment, scaffold_locator, scaffold_disposition)
    jsonschema.Draft202012Validator(remediation_schema).validate(scaffold_remediation)
    if scaffold_remediation['plan_status'] != 'open' or not scaffold_remediation['work_items']:
        return fail('scaffold remediation plan should be open and emit work items')
    if not any(item['finding_code'] == 'placeholder_free' and item['blocking'] for item in scaffold_remediation['work_items']):
        return fail('scaffold remediation plan should include a blocking placeholder work item')

    scaffold_authorization = tool.make_authorization(scaffold_assessment, scaffold_locator, scaffold_disposition, scaffold_remediation)
    jsonschema.Draft202012Validator(authorization_schema).validate(scaffold_authorization)
    if scaffold_authorization['authorization_decision'] != 'not_authorized_for_claim_ready_citation':
        return fail('scaffold authorization should not authorize claim-ready citation')
    if 'assessment_green' not in scaffold_authorization['failed_basis_codes']:
        return fail('scaffold authorization should fail the assessment_green basis check')
    if 'no_open_blocking_work_items' not in scaffold_authorization['failed_basis_codes']:
        return fail('scaffold authorization should fail the no_open_blocking_work_items basis check')

    scaffold_promotion = tool.make_promotion(scaffold_assessment, scaffold_locator, scaffold_authorization, scaffold_assessment, scaffold_locator, scaffold_authorization)
    jsonschema.Draft202012Validator(promotion_schema).validate(scaffold_promotion)
    if scaffold_promotion['promotion_decision'] != 'not_yet_promoted':
        return fail('self-compared scaffold package should remain not yet promoted')

    scaffold_review_watch = tool.make_review_watch(scaffold_authorization, scaffold_promotion, reviewed_on='2026-03-22', max_review_interval_days=180)
    jsonschema.Draft202012Validator(review_watch_schema).validate(scaffold_review_watch)
    if scaffold_review_watch['watch_status'] != 'reopen_now':
        return fail('scaffold review watch should reopen immediately')
    if 'current_authorized' not in scaffold_review_watch['failed_basis_codes']:
        return fail('scaffold review watch should fail the current_authorized basis check')

    scaffold_review_verdict = tool.make_review_verdict(scaffold_review_watch, as_of='2026-03-22')
    jsonschema.Draft202012Validator(review_verdict_schema).validate(scaffold_review_verdict)
    if scaffold_review_verdict['review_decision'] != 'reopen_and_suspend_claim_ready_citation':
        return fail('scaffold review verdict should suspend claim-ready citation')
    if 'watch_active_before_review' not in scaffold_review_verdict['failed_basis_codes']:
        return fail('scaffold review verdict should fail the watch_active_before_review basis check')

    triggered_review_verdict = tool.make_review_verdict(example_review_watch, as_of='2026-03-22', observed_trigger_codes=['retained_evidence_changed'])
    jsonschema.Draft202012Validator(review_verdict_schema).validate(triggered_review_verdict)
    if triggered_review_verdict['review_decision'] != 'reopen_and_suspend_claim_ready_citation':
        return fail('triggered review verdict should suspend claim-ready citation')
    if triggered_review_verdict['matched_reopen_trigger_codes'] != ['retained_evidence_changed']:
        return fail('triggered review verdict should preserve the matched reopen trigger code')

    triggered_citation_advisory = tool.make_citation_advisory(triggered_review_verdict)
    jsonschema.Draft202012Validator(citation_advisory_schema).validate(triggered_citation_advisory)
    if triggered_citation_advisory['advisory_decision'] != 'withdraw_current_locator_from_claim_ready_citation':
        return fail('triggered citation advisory should withdraw claim-ready use of the reviewed locator')
    if triggered_citation_advisory['existing_citations_action'] != 'flag_for_withdrawal':
        return fail('triggered citation advisory should flag existing citations for withdrawal')
    if triggered_citation_advisory['advisory_reason_codes'] != ['no_reopen_trigger_observed', 'retained_evidence_changed']:
        return fail('triggered citation advisory should preserve both the reopen trigger and failed review basis as reason codes')

    print('successor-safe-ceremony-receipt: ok')
    print(f'successor-safe-ceremony-receipt: validated {TOOL.relative_to(ROOT)} against receipt+locator+assessment+disposition+remediation+authorization+promotion+review-watch+review-verdict+citation-advisory+package-manifest+package-supersession+package-lineage+package-status-card+package-verification-report+package-head+package-redirect+package-catalog schemas and worked snapshots')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
