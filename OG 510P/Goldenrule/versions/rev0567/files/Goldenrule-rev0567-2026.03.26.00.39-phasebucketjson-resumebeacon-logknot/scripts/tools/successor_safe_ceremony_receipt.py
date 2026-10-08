#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import subprocess
from datetime import date, timedelta
from pathlib import Path
from typing import Any

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

SECTIONS = [
    ("authoritative_request", "Authoritative request"),
    ("verifier_targeting", "Verifier targeting"),
    ("delivery_path", "Delivery path"),
    ("approval_surface", "Approval surface"),
    ("ceremony_topology", "Ceremony topology"),
    ("linkability_and_retention", "Linkability and retention"),
    ("retained_evidence", "Retained evidence"),
]

PLACEHOLDER_MARKERS = [
    'not yet specified',
    'replace with the explicit ceremony contract',
    'placeholder',
    'todo',
    'tbd',
]

TRUSTED_RENDERER_MARKERS = [
    'wallet-native',
    'wallet native',
    'wallet chrome',
    'browser chrome',
    'user-agent chrome',
    'user agent chrome',
    'authorization-server ui',
    'authorization server ui',
    'trusted renderer',
]

REMEDIATION_LIBRARY = {
    'placeholder_free': {
        'closure_goal': 'Replace all scaffold or placeholder language with explicit ceremony facts before retention.',
        'acceptance_test': 'A regenerated assessment reports placeholder_free as pass.',
        'recommended_actions': [
            'Rewrite every placeholder-bearing field with concrete request, targeting, delivery, approval, topology, linkability, and evidence details.',
            'Regenerate the assessment and disposition after the rewritten receipt is saved.'
        ],
    },
    'verifier_binding_explicit': {
        'closure_goal': 'Name the concrete verifier, audience, origin, or relying-party scope that made the ceremony admissible.',
        'acceptance_test': 'The receipt explicitly names verifier or audience binding and the finding flips to pass.',
        'recommended_actions': [
            'Record the intended verifier identity, client_id, audience, origin, or relying-party scope in verifier_targeting.',
            'Retain or cite the policy material that fixed that verifier scope at decision time.'
        ],
    },
    'session_binding_explicit': {
        'closure_goal': 'Preserve the nonce, challenge, state, transcript, or replay-window material that tied the ceremony to one live session.',
        'acceptance_test': 'The receipt states the live-session or replay binding and the finding flips to pass.',
        'recommended_actions': [
            'Name the nonce, challenge, state, transcript, or replay-window semantics in verifier_targeting.',
            'Retain a digest-bearing reference to any session-correlation artifact when one exists.'
        ],
    },
    'by_reference_request_integrity_named': {
        'closure_goal': 'For any request_uri or equivalent indirection, state the integrity regime that protected the authoritative request.',
        'acceptance_test': 'The receipt names PAR, JAR, signed request objects, or another protected fetch regime and the finding flips to pass.',
        'recommended_actions': [
            'Record whether by-reference request carriage relied on PAR, JAR, signed request objects, or another authenticated integrity regime.',
            'Retain a request digest or protected-fetch reference that lets a future steward verify the authoritative ask.'
        ],
    },
    'direct_post_session_mapping_named': {
        'closure_goal': 'State how any direct_post response mapped back to the verifier session.',
        'acceptance_test': 'The receipt names the callback, state, nonce, or verifier-side mapping material and the finding flips to pass.',
        'recommended_actions': [
            'Describe the verifier-side session-correlation material for direct_post or equivalent body-return flows.',
            'Retain a digest-bearing reference to the callback or response-correlation evidence when policy permits.'
        ],
    },
    'cross_device_participation_named': {
        'closure_goal': 'For cross-device journeys, name the claimant participation or proximity evidence that linked the displayed request to the responding device.',
        'acceptance_test': 'The receipt names scan, BLE, manual code, or another cross-device participation proof and the finding flips to pass.',
        'recommended_actions': [
            'Record the active claimant participation, co-presence, or proximity proof used in the cross-device ceremony.',
            'Mark the field explicitly not applicable only when the journey truly was not cross-device.'
        ],
    },
    'dispatch_assurance_named': {
        'closure_goal': 'Explain the destination-binding assurance of the invocation route, especially for custom-scheme dispatch.',
        'acceptance_test': 'The receipt either records stronger app-link assurance or justifies the custom-scheme route and the finding flips to pass.',
        'recommended_actions': [
            'Record whether invocation used a claimed HTTPS app link, universal link, app link, or a weaker custom scheme.',
            'If only a custom scheme was available, explain why that route remained acceptable for the ceremony.'
        ],
    },
    'trusted_renderer_named': {
        'closure_goal': 'Name the trusted approval renderer rather than leaving the final consent surface implicit.',
        'acceptance_test': 'The receipt explicitly names wallet-native, browser chrome, authorization-server UI, or another trusted renderer and the finding flips to pass.',
        'recommended_actions': [
            'Record which runtime owned the final approval surface and which content sources could influence it.',
            'Note any anti-redressing or render-to-backend comparison posture relevant to that surface.'
        ],
    },
    'retained_evidence_fixity_named': {
        'closure_goal': 'Make retained evidence references fixity-bearing so future stewards can verify what was kept.',
        'acceptance_test': 'Retained evidence references include a digest, ni URI, or another fixity handle and the finding flips to pass.',
        'recommended_actions': [
            'Add digest-bearing references for authoritative request, approval or response artifacts, and policy or validation material.',
            'Prefer compact locators over copying bulky evidence into downstream notes.'
        ],
    },
}


def scaffold_receipt(receipt_id: str, journey_kind: str) -> dict[str, Any]:
    placeholder = "not yet specified: replace with the explicit ceremony contract before claim-ready retention"
    return {
        "schema_version": 1,
        "id": receipt_id,
        "journey_kind": journey_kind,
        "authoritative_request": {
            "field_one": "request shape and authorized scope: " + placeholder,
            "field_two": "satisfaction mapping or claim route: " + placeholder,
            "field_three": "transaction or presentation binding: " + placeholder,
        },
        "verifier_targeting": {
            "field_one": "intended verifier and audience: " + placeholder,
            "field_two": "nonce, challenge, or session binding: " + placeholder,
            "field_three": "holder binding and replay window: " + placeholder,
        },
        "delivery_path": {
            "field_one": "request carriage route: " + placeholder,
            "field_two": "response return route: " + placeholder,
            "field_three": "plaintext observer surface: " + placeholder,
        },
        "approval_surface": {
            "field_one": "trusted renderer and display owner: " + placeholder,
            "field_two": "locale and field-order contract: " + placeholder,
            "field_three": "user activation and redressing posture: " + placeholder,
        },
        "ceremony_topology": {
            "field_one": "device split: " + placeholder,
            "field_two": "invocation route: " + placeholder,
            "field_three": "dispatch assurance and destination binding: " + placeholder,
            "field_four": "proximity or cross-channel participation: not applicable unless the journey was multi-device",
        },
        "linkability_and_retention": {
            "field_one": "subject identifier scope: " + placeholder,
            "field_two": "proof linkability and status observers: " + placeholder,
            "field_three": "retention and disclosure intent: " + placeholder,
        },
        "retained_evidence": {
            "field_one": "authoritative request digest or reference: " + placeholder,
            "field_two": "approval or response artifact digest or reference: " + placeholder,
            "field_three": "policy snapshot and validation material reference: " + placeholder,
        },
        "notes": "Use explicit not applicable language where a section truly does not apply; do not omit decisive ceremony facts.",
    }


def render_markdown(receipt: dict[str, Any]) -> str:
    lines = [
        f"# Successor-Safe Ceremony Receipt — {receipt['id']}",
        "",
        f"- journey_kind: `{receipt['journey_kind']}`",
        f"- schema_version: `{receipt['schema_version']}`",
    ]
    if receipt.get("notes"):
        lines.append(f"- notes: {receipt['notes']}")
    lines.append("")
    for key, heading in SECTIONS:
        block = receipt[key]
        lines.append(f"## {heading}")
        lines.append("")
        for name in ["field_one", "field_two", "field_three", "field_four"]:
            value = block.get(name)
            if value is None:
                continue
            pretty = name.replace("_", " ")
            lines.append(f"- **{pretty}**: {value}")
        lines.append("")
    return "\n".join(lines)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def load_schema() -> dict[str, Any]:
    return load_json(SCHEMA_PATH)


def load_locator_schema() -> dict[str, Any]:
    return load_json(LOCATOR_SCHEMA_PATH)


def load_assessment_schema() -> dict[str, Any]:
    return load_json(ASSESSMENT_SCHEMA_PATH)


def load_disposition_schema() -> dict[str, Any]:
    return load_json(DISPOSITION_SCHEMA_PATH)


def load_remediation_schema() -> dict[str, Any]:
    return load_json(REMEDIATION_SCHEMA_PATH)


def load_authorization_schema() -> dict[str, Any]:
    return load_json(AUTHORIZATION_SCHEMA_PATH)


def load_promotion_schema() -> dict[str, Any]:
    return load_json(PROMOTION_SCHEMA_PATH)


def load_review_watch_schema() -> dict[str, Any]:
    return load_json(REVIEW_WATCH_SCHEMA_PATH)


def load_review_verdict_schema() -> dict[str, Any]:
    return load_json(REVIEW_VERDICT_SCHEMA_PATH)


def load_citation_advisory_schema() -> dict[str, Any]:
    return load_json(CITATION_ADVISORY_SCHEMA_PATH)


def load_package_manifest_schema() -> dict[str, Any]:
    return load_json(PACKAGE_MANIFEST_SCHEMA_PATH)


def load_package_supersession_schema() -> dict[str, Any]:
    return load_json(PACKAGE_SUPERSESSION_SCHEMA_PATH)


def load_package_lineage_schema() -> dict[str, Any]:
    return load_json(PACKAGE_LINEAGE_SCHEMA_PATH)


def load_package_head_schema() -> dict[str, Any]:
    return load_json(PACKAGE_HEAD_SCHEMA_PATH)


def load_package_status_card_schema() -> dict[str, Any]:
    return load_json(PACKAGE_STATUS_CARD_SCHEMA_PATH)

def load_package_redirect_schema() -> dict[str, Any]:
    return load_json(PACKAGE_REDIRECT_SCHEMA_PATH)


def load_package_catalog_schema() -> dict[str, Any]:
    return load_json(PACKAGE_CATALOG_SCHEMA_PATH)


def load_package_verification_report_schema() -> dict[str, Any]:
    return load_json(PACKAGE_VERIFICATION_REPORT_SCHEMA_PATH)


def load_package_claim_scope_schema() -> dict[str, Any]:
    return load_json(PACKAGE_CLAIM_SCOPE_SCHEMA_PATH)


def load_package_reliance_card_schema() -> dict[str, Any]:
    return load_json(PACKAGE_RELIANCE_CARD_SCHEMA_PATH)


def validate_receipt(receipt: dict[str, Any]) -> None:
    schema = load_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(receipt, schema)


def validate_locator(locator: dict[str, Any]) -> None:
    schema = load_locator_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(locator, schema)


def validate_assessment(assessment: dict[str, Any]) -> None:
    schema = load_assessment_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(assessment, schema)


def validate_disposition(disposition: dict[str, Any]) -> None:
    schema = load_disposition_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(disposition, schema)


def validate_remediation_plan(plan: dict[str, Any]) -> None:
    schema = load_remediation_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(plan, schema)


def validate_authorization(authorization: dict[str, Any]) -> None:
    schema = load_authorization_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(authorization, schema)


def validate_promotion(promotion: dict[str, Any]) -> None:
    schema = load_promotion_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(promotion, schema)


def validate_review_watch(review_watch: dict[str, Any]) -> None:
    schema = load_review_watch_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(review_watch, schema)


def validate_review_verdict(review_verdict: dict[str, Any]) -> None:
    schema = load_review_verdict_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(review_verdict, schema)


def validate_citation_advisory(citation_advisory: dict[str, Any]) -> None:
    schema = load_citation_advisory_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(citation_advisory, schema)


def validate_package_manifest(package_manifest: dict[str, Any]) -> None:
    schema = load_package_manifest_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(package_manifest, schema)


def validate_package_supersession(package_supersession: dict[str, Any]) -> None:
    schema = load_package_supersession_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(package_supersession, schema)


def validate_package_lineage(package_lineage: dict[str, Any]) -> None:
    schema = load_package_lineage_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(package_lineage, schema)


def validate_package_head(package_head: dict[str, Any]) -> None:
    schema = load_package_head_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(package_head, schema)


def validate_package_status_card(package_status_card: dict[str, Any]) -> None:
    schema = load_package_status_card_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(package_status_card, schema)

def validate_package_redirect(package_redirect: dict[str, Any]) -> None:
    schema = load_package_redirect_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(package_redirect, schema)


def validate_package_catalog(package_catalog: dict[str, Any]) -> None:
    schema = load_package_catalog_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(package_catalog, schema)


def validate_package_verification_report(package_verification_report: dict[str, Any]) -> None:
    schema = load_package_verification_report_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(package_verification_report, schema)


def validate_package_claim_scope(package_claim_scope: dict[str, Any]) -> None:
    schema = load_package_claim_scope_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(package_claim_scope, schema)


def validate_package_reliance_card(package_reliance_card: dict[str, Any]) -> None:
    schema = load_package_reliance_card_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(package_reliance_card, schema)


def canonicalize_receipt(receipt: dict[str, Any]) -> bytes:
    validate_receipt(receipt)
    return json.dumps(
        receipt,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def make_locator(receipt: dict[str, Any], source_path: str) -> dict[str, Any]:
    canonical = canonicalize_receipt(receipt)
    digest = hashlib.sha256(canonical).digest()
    digest_hex = digest.hex()
    digest_b64url = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    locator = {
        "schema_version": 1,
        "locator_kind": "successor_safe_ceremony_receipt_locator",
        "receipt_id": receipt["id"],
        "canonicalization_profile": "restricted_jcs_utf8_v1",
        "digest_algorithm": "sha-256",
        "digest_hex": digest_hex,
        "ni_uri": f"ni:///sha-256;{digest_b64url}",
        "canonical_utf8_bytes": len(canonical),
        "source_path": source_path,
        "size_discipline_note": "Cite this locator or the receipt path+digest rather than copying the receipt body into downstream notes unless the ceremony contract itself changed.",
    }
    validate_locator(locator)
    return locator


def normalized_text(value: Any) -> str:
    if value is None:
        return ''
    if isinstance(value, dict):
        return ' '.join(normalized_text(v) for v in value.values())
    if isinstance(value, list):
        return ' '.join(normalized_text(v) for v in value)
    return str(value).strip().lower()


def contains_any(text: str, markers: list[str]) -> bool:
    return any(marker in text for marker in markers)


def make_finding(code: str, severity: str, status: str, summary: str, evidence_paths: list[str]) -> dict[str, Any]:
    return {
        'code': code,
        'severity': severity,
        'status': status,
        'summary': summary,
        'evidence_paths': evidence_paths,
    }


def assess_receipt(receipt: dict[str, Any], source_path: str) -> dict[str, Any]:
    validate_receipt(receipt)
    findings: list[dict[str, Any]] = []

    full_text = normalized_text(receipt)
    targeting_text = normalized_text(receipt['verifier_targeting'])
    delivery_text = normalized_text(receipt['delivery_path'])
    approval_text = normalized_text(receipt['approval_surface'])
    topology_text = normalized_text(receipt['ceremony_topology'])
    evidence_text = normalized_text(receipt['retained_evidence'])

    placeholder_found = contains_any(full_text, PLACEHOLDER_MARKERS)
    findings.append(make_finding(
        code='placeholder_free',
        severity='error' if placeholder_found else 'info',
        status='fail' if placeholder_found else 'pass',
        summary='Receipt must replace scaffold placeholders before claim-ready retention.' if placeholder_found else 'No scaffold placeholder language detected.',
        evidence_paths=['/notes', '/authoritative_request', '/verifier_targeting', '/delivery_path', '/approval_surface', '/ceremony_topology', '/linkability_and_retention', '/retained_evidence'],
    ))

    verifier_ok = contains_any(targeting_text, ['client_id', 'audience', 'origin', 'verifier', 'relying party'])
    findings.append(make_finding(
        code='verifier_binding_explicit',
        severity='error' if not verifier_ok else 'info',
        status='fail' if not verifier_ok else 'pass',
        summary='Receipt should name the intended verifier or audience binding explicitly.' if not verifier_ok else 'Intended verifier or audience binding is named explicitly.',
        evidence_paths=['/verifier_targeting/field_one'],
    ))

    session_ok = contains_any(targeting_text, ['nonce', 'challenge', 'session', 'transcript', 'state', 'replay'])
    findings.append(make_finding(
        code='session_binding_explicit',
        severity='error' if not session_ok else 'info',
        status='fail' if not session_ok else 'pass',
        summary='Receipt should state how the ceremony was bound to one live session or replay window.' if not session_ok else 'Session or replay binding language is present.',
        evidence_paths=['/verifier_targeting/field_two', '/verifier_targeting/field_three'],
    ))

    uses_request_uri = 'request_uri' in delivery_text or 'request uri' in delivery_text
    request_integrity_ok = contains_any(
        normalized_text(receipt['authoritative_request']) + ' ' + delivery_text,
        ['protected', 'signed', 'encrypted', 'jar', 'par', 'pushed', 'integrity', 'authenticated', 'request object'],
    )
    findings.append(make_finding(
        code='by_reference_request_integrity_named',
        severity='warning' if uses_request_uri and not request_integrity_ok else 'info',
        status='warn' if uses_request_uri and not request_integrity_ok else 'pass',
        summary='By-reference request carriage is present but the receipt does not name a request-integrity regime.' if uses_request_uri and not request_integrity_ok else 'By-reference request carriage either is absent or names an integrity regime.',
        evidence_paths=['/delivery_path/field_one', '/authoritative_request/field_three'],
    ))

    uses_direct_post = 'direct post' in delivery_text or 'direct_post' in delivery_text
    direct_post_session_ok = contains_any(targeting_text + ' ' + evidence_text, ['state', 'session', 'mapping', 'nonce', 'callback'])
    findings.append(make_finding(
        code='direct_post_session_mapping_named',
        severity='warning' if uses_direct_post and not direct_post_session_ok else 'info',
        status='warn' if uses_direct_post and not direct_post_session_ok else 'pass',
        summary='direct_post is named but the receipt does not say how requests map back to the verifier session.' if uses_direct_post and not direct_post_session_ok else 'direct_post handling either is absent or names session-mapping material.',
        evidence_paths=['/delivery_path/field_two', '/verifier_targeting/field_two', '/retained_evidence/field_two'],
    ))

    cross_device = 'cross-device' in topology_text or 'cross device' in topology_text or 'hybrid' in topology_text
    field_four_text = normalized_text(receipt['ceremony_topology'].get('field_four', ''))
    participation_ok = contains_any(topology_text, ['scan', 'ble', 'proximity', 'co-presence', 'co presence', 'participant', 'participation', 'manual entry', 'user code']) and 'not applicable' not in field_four_text
    findings.append(make_finding(
        code='cross_device_participation_named',
        severity='error' if cross_device and not participation_ok else 'info',
        status='fail' if cross_device and not participation_ok else 'pass',
        summary='Cross-device receipt should name the claimant-participation or proximity evidence that linked the requesting and responding devices.' if cross_device and not participation_ok else 'Cross-device participation or proximity evidence is either not needed or is named explicitly.',
        evidence_paths=['/ceremony_topology/field_one', '/ceremony_topology/field_four'],
    ))

    custom_scheme = contains_any(topology_text, ['custom scheme', 'private-use uri', 'private use uri', 'custom url scheme'])
    claimed_link = contains_any(topology_text, ['claimed https', 'universal link', 'app link', 'app-claimed https', 'app claimed https'])
    findings.append(make_finding(
        code='dispatch_assurance_named',
        severity='warning' if custom_scheme and not claimed_link else 'info',
        status='warn' if custom_scheme and not claimed_link else 'pass',
        summary='Receipt uses custom-scheme dispatch without naming stronger destination binding such as a claimed HTTPS app link.' if custom_scheme and not claimed_link else 'Dispatch assurance is either stronger than a bare custom scheme or not custom-scheme based.',
        evidence_paths=['/ceremony_topology/field_two', '/ceremony_topology/field_three'],
    ))

    trusted_renderer_ok = contains_any(approval_text, TRUSTED_RENDERER_MARKERS)
    findings.append(make_finding(
        code='trusted_renderer_named',
        severity='warning' if not trusted_renderer_ok else 'info',
        status='warn' if not trusted_renderer_ok else 'pass',
        summary='Receipt should name a trusted approval renderer rather than leaving the render surface implicit.' if not trusted_renderer_ok else 'Trusted approval renderer is named explicitly.',
        evidence_paths=['/approval_surface/field_one'],
    ))

    digest_ok = contains_any(evidence_text, ['sha256:', 'ni:///sha-256;', 'digest'])
    findings.append(make_finding(
        code='retained_evidence_fixity_named',
        severity='warning' if not digest_ok else 'info',
        status='warn' if not digest_ok else 'pass',
        summary='Retained evidence references should include a digest or other fixity handle.' if not digest_ok else 'Retained evidence includes digest-bearing or fixity-oriented references.',
        evidence_paths=['/retained_evidence/field_one', '/retained_evidence/field_two', '/retained_evidence/field_three'],
    ))

    hard_fail_count = sum(1 for row in findings if row['status'] == 'fail')
    warning_count = sum(1 for row in findings if row['status'] == 'warn')
    overall_status = 'fail' if hard_fail_count else 'warn' if warning_count else 'pass'

    advice: list[str] = []
    if hard_fail_count:
        advice.append('Repair all fail findings before treating the receipt as inheritor-ready.')
    if any(row['code'] == 'by_reference_request_integrity_named' and row['status'] == 'warn' for row in findings):
        advice.append('Name whether request carriage relied on PAR, JAR, or another authenticated integrity regime when using request_uri-style indirection.')
    if any(row['code'] == 'direct_post_session_mapping_named' and row['status'] == 'warn' for row in findings):
        advice.append('For direct_post journeys, record how the verifier mapped the wallet response back to the live session, such as state or callback correlation.')
    if any(row['code'] == 'dispatch_assurance_named' and row['status'] == 'warn' for row in findings):
        advice.append('When invocation relies on a custom scheme, record why that route remained acceptable or prefer claimed HTTPS app-link routing.')
    if any(row['code'] == 'cross_device_participation_named' and row['status'] == 'fail' for row in findings):
        advice.append('Cross-device journeys should say what active claimant participation or proximity proof linked the displayed request to the responding device.')
    if not advice and warning_count:
        advice.append('Receipt is structurally strong but still has warning-level follow-up before it is maximally successor-safe.')
    elif not advice:
        advice.append('Assessment is green; downstream notes can cite the receipt locator instead of re-explaining the ceremony prose.')

    assessment = {
        'schema_version': 1,
        'assessment_kind': 'successor_safe_ceremony_receipt_assessment',
        'receipt_id': receipt['id'],
        'journey_kind': receipt['journey_kind'],
        'source_path': source_path,
        'overall_status': overall_status,
        'counts': {
            'finding_count': len(findings),
            'hard_fail_count': hard_fail_count,
            'warning_count': warning_count,
        },
        'findings': findings,
        'advice': advice,
    }
    validate_assessment(assessment)
    return assessment


def make_disposition(assessment: dict[str, Any], locator: dict[str, Any]) -> dict[str, Any]:
    validate_assessment(assessment)
    validate_locator(locator)
    if assessment['receipt_id'] != locator['receipt_id']:
        raise ValueError('assessment and locator must point at the same receipt id')

    blocking = sorted(row['code'] for row in assessment['findings'] if row['status'] == 'fail')
    warnings = sorted(row['code'] for row in assessment['findings'] if row['status'] == 'warn')

    if assessment['overall_status'] == 'pass':
        archive_admission = 'claim_ready_citable'
        risk_response = 'accept'
        copy_forward_rule = 'cite_locator_only'
        rationale = 'Assessment is green, so downstream notes can treat the receipt as claim-ready evidence while citing the compact locator instead of re-copying the receipt body.'
        next_review_trigger = 'Reassess only if the ceremony contract, protocol surface, retained evidence, or archive retention policy changes.'
    elif assessment['overall_status'] == 'warn':
        archive_admission = 'provisional_locator_only'
        risk_response = 'mitigate'
        copy_forward_rule = 'cite_locator_until_remediated'
        rationale = 'Receipt is structurally usable for context, but warning-level gaps mean it should not be treated as settled claim-ready evidence until the cited follow-up actions are repaired.'
        next_review_trigger = 'Reassess before any inheritor-facing claim relies on this receipt as settled ceremony evidence.'
    else:
        archive_admission = 'hold_for_remediation'
        risk_response = 'mitigate'
        copy_forward_rule = 'hold_until_remediated'
        rationale = 'Hard-fail findings mean the archive preserved a receipt shape without preserving a dependable successor-safe ceremony contract.'
        next_review_trigger = 'Reassess immediately after remediation; do not treat the receipt as inheritor-ready before then.'

    disposition = {
        'schema_version': 1,
        'disposition_kind': 'successor_safe_ceremony_receipt_disposition',
        'receipt_id': assessment['receipt_id'],
        'journey_kind': assessment['journey_kind'],
        'receipt_locator': {
            'ni_uri': locator['ni_uri'],
            'digest_hex': locator['digest_hex'],
            'source_path': locator['source_path'],
        },
        'assessment_overall_status': assessment['overall_status'],
        'archive_admission': archive_admission,
        'residual_risk_response': risk_response,
        'copy_forward_rule': copy_forward_rule,
        'blocking_finding_codes': blocking,
        'warning_finding_codes': warnings,
        'required_actions': assessment['advice'],
        'rationale': rationale,
        'next_review_trigger': next_review_trigger,
    }
    validate_disposition(disposition)
    return disposition


def make_remediation_plan(assessment: dict[str, Any], locator: dict[str, Any], disposition: dict[str, Any]) -> dict[str, Any]:
    validate_assessment(assessment)
    validate_locator(locator)
    validate_disposition(disposition)
    if assessment['receipt_id'] != locator['receipt_id'] or assessment['receipt_id'] != disposition['receipt_id']:
        raise ValueError('assessment, locator, and disposition must point at the same receipt id')

    relevant = [row for row in assessment['findings'] if row['status'] in {'fail', 'warn'}]
    work_items: list[dict[str, Any]] = []
    for row in relevant:
        template = REMEDIATION_LIBRARY.get(row['code'], {
            'closure_goal': 'Replace the weak or missing ceremony detail with an explicit retained contract.',
            'acceptance_test': 'Regenerated assessment marks this finding as pass.',
            'recommended_actions': ['Repair the cited fields and regenerate the receipt assessment plus disposition.'],
        })
        work_items.append({
            'finding_code': row['code'],
            'priority': 'high' if row['status'] == 'fail' else 'medium',
            'blocking': row['status'] == 'fail',
            'closure_goal': template['closure_goal'],
            'acceptance_test': template['acceptance_test'],
            'recommended_actions': template['recommended_actions'],
            'evidence_paths': row['evidence_paths'],
        })

    if not work_items:
        plan_status = 'monitor_only'
        promotion_gate = 'No remediation work is currently required; keep citing the locator unless a future review trigger or receipt change reopens the plan.'
        completion_rule = 'Reopen only if the ceremony contract, retained evidence, or policy context changes and then regenerate locator, assessment, disposition, and remediation plan together.'
    else:
        plan_status = 'open'
        promotion_gate = 'Promote to claim_ready_citable only after every blocking work item closes and the regenerated assessment/disposition show the intended archive admission.'
        completion_rule = 'Close the plan only after repairing the receipt, regenerating assessment plus disposition, and confirming that remaining warnings are either cleared or intentionally re-dispositioned.'

    plan = {
        'schema_version': 1,
        'plan_kind': 'successor_safe_ceremony_receipt_remediation_plan',
        'receipt_id': assessment['receipt_id'],
        'journey_kind': assessment['journey_kind'],
        'receipt_locator': {
            'ni_uri': locator['ni_uri'],
            'digest_hex': locator['digest_hex'],
            'source_path': locator['source_path'],
        },
        'assessment_overall_status': assessment['overall_status'],
        'archive_admission': disposition['archive_admission'],
        'residual_risk_response': disposition['residual_risk_response'],
        'copy_forward_rule': disposition['copy_forward_rule'],
        'plan_status': plan_status,
        'work_items': work_items,
        'promotion_gate': promotion_gate,
        'completion_rule': completion_rule,
        'review_trigger': disposition['next_review_trigger'],
    }
    validate_remediation_plan(plan)
    return plan


def make_authorization(assessment: dict[str, Any], locator: dict[str, Any], disposition: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    validate_assessment(assessment)
    validate_locator(locator)
    validate_disposition(disposition)
    validate_remediation_plan(plan)
    if len({assessment['receipt_id'], locator['receipt_id'], disposition['receipt_id'], plan['receipt_id']}) != 1:
        raise ValueError('assessment, locator, disposition, and remediation plan must point at the same receipt id')

    blocking_open = any(item['blocking'] for item in plan['work_items'])
    checks = [
        {
            'code': 'assessment_green',
            'passed': assessment['overall_status'] == 'pass',
            'summary': 'Assessment is green and therefore does not currently report warning or fail findings.' if assessment['overall_status'] == 'pass' else 'Assessment is not green, so the current package still carries warning or fail findings.',
        },
        {
            'code': 'no_open_blocking_work_items',
            'passed': not blocking_open,
            'summary': 'Remediation plan has no open blocking work items.' if not blocking_open else 'Remediation plan still has open blocking work items that must close before claim-ready citation.',
        },
        {
            'code': 'claim_ready_archive_admission',
            'passed': disposition['archive_admission'] == 'claim_ready_citable',
            'summary': 'Disposition already admits the receipt as claim-ready citable.' if disposition['archive_admission'] == 'claim_ready_citable' else 'Disposition does not currently admit the receipt as claim-ready citable.',
        },
        {
            'code': 'locator_only_copy_forward',
            'passed': disposition['copy_forward_rule'] == 'cite_locator_only',
            'summary': 'Copy-forward rule is locator-only, so downstream notes can cite the compact handle instead of re-copying the receipt body.' if disposition['copy_forward_rule'] == 'cite_locator_only' else 'Copy-forward rule still restricts downstream use, so the receipt is not yet in the locator-only claim-ready state.',
        },
    ]
    failed = [row['code'] for row in checks if not row['passed']]

    if not failed:
        decision = 'authorized_for_claim_ready_citation'
        terms = [
            'Cite the receipt locator rather than re-copying the full receipt body in downstream notes.',
            'Regenerate locator, assessment, disposition, remediation, and authorization together if the ceremony contract, retained evidence, or policy context changes.',
        ]
        next_step = 'Receipt is authorized for claim-ready citation under the current package; keep citing the locator and reopen only on the stated review trigger.'
    else:
        decision = 'not_authorized_for_claim_ready_citation'
        terms = [
            'Do not treat the receipt as claim-ready evidence until the failed basis checks are repaired and the package is regenerated.',
            'Keep any downstream references at or below the currently declared copy-forward rule until authorization turns green.',
        ]
        next_step = 'Close blocking remediation items or regenerate the assessment/disposition package before attempting claim-ready citation again.'

    authorization = {
        'schema_version': 1,
        'authorization_kind': 'successor_safe_ceremony_receipt_authorization',
        'receipt_id': assessment['receipt_id'],
        'journey_kind': assessment['journey_kind'],
        'receipt_locator': {
            'ni_uri': locator['ni_uri'],
            'digest_hex': locator['digest_hex'],
            'source_path': locator['source_path'],
        },
        'assessment_overall_status': assessment['overall_status'],
        'archive_admission': disposition['archive_admission'],
        'residual_risk_response': disposition['residual_risk_response'],
        'copy_forward_rule': disposition['copy_forward_rule'],
        'plan_status': plan['plan_status'],
        'authorization_decision': decision,
        'basis_checks': checks,
        'failed_basis_codes': failed,
        'terms_and_conditions': terms,
        'review_trigger': plan['review_trigger'],
        'recommended_next_step': next_step,
    }
    validate_authorization(authorization)
    return authorization


def make_promotion(prior_assessment: dict[str, Any], prior_locator: dict[str, Any], prior_authorization: dict[str, Any], current_assessment: dict[str, Any], current_locator: dict[str, Any], current_authorization: dict[str, Any]) -> dict[str, Any]:
    validate_assessment(prior_assessment)
    validate_locator(prior_locator)
    validate_authorization(prior_authorization)
    validate_assessment(current_assessment)
    validate_locator(current_locator)
    validate_authorization(current_authorization)
    if len({prior_assessment['receipt_id'], prior_locator['receipt_id'], prior_authorization['receipt_id'], current_assessment['receipt_id'], current_locator['receipt_id'], current_authorization['receipt_id']}) != 1:
        raise ValueError('all prior/current artifacts must point at the same receipt id')

    prior_findings = {row['code']: row['status'] for row in prior_assessment['findings']}
    current_findings = {row['code']: row['status'] for row in current_assessment['findings']}
    all_codes = sorted(set(prior_findings) | set(current_findings))

    closed = sorted(code for code in all_codes if prior_findings.get(code, 'pass') in {'warn', 'fail'} and current_findings.get(code, 'pass') == 'pass')
    carried = sorted(code for code in all_codes if prior_findings.get(code, 'pass') in {'warn', 'fail'} and current_findings.get(code, 'pass') in {'warn', 'fail'})
    newly_opened = sorted(code for code in all_codes if prior_findings.get(code, 'pass') == 'pass' and current_findings.get(code, 'pass') in {'warn', 'fail'})

    current_authorized = current_authorization['authorization_decision'] == 'authorized_for_claim_ready_citation'
    prior_authorized = prior_authorization['authorization_decision'] == 'authorized_for_claim_ready_citation'
    prior_nonpass = sorted(code for code, status in prior_findings.items() if status in {'warn', 'fail'})
    all_prior_nonpass_closed = all(code in closed for code in prior_nonpass)

    basis_checks = [
        {
            'code': 'current_authorized',
            'passed': current_authorized,
            'summary': 'Current package is authorized for claim-ready citation.' if current_authorized else 'Current package is not yet authorized for claim-ready citation.',
        },
        {
            'code': 'prior_not_authorized',
            'passed': not prior_authorized,
            'summary': 'Prior package was not yet authorized, so a promotion would represent a real state change.' if not prior_authorized else 'Prior package was already authorized, so there is no fresh promotion to explain.',
        },
        {
            'code': 'all_prior_nonpass_findings_closed',
            'passed': all_prior_nonpass_closed,
            'summary': 'Every prior warning or fail finding now closes in the current assessment.' if all_prior_nonpass_closed else 'Some prior warning or fail findings remain open in the current assessment.',
        },
        {
            'code': 'no_newly_opened_findings',
            'passed': not newly_opened,
            'summary': 'No new warning or fail findings opened while promoting the receipt.' if not newly_opened else 'The current receipt opened new warning or fail findings during the attempted promotion.',
        },
    ]
    failed_basis = [row['code'] for row in basis_checks if not row['passed']]

    if current_authorized and not prior_authorized and not newly_opened and all_prior_nonpass_closed:
        decision = 'promoted_to_claim_ready_citation'
        summary = 'Receipt moved from not authorized to authorized-for-claim-ready citation with all prior non-pass findings closed and no newly opened findings.'
        next_step = 'Keep citing the current locator and regenerate the promotion record only if a later reassessment or authorization change reopens the package.'
    elif current_authorized and prior_authorized and not newly_opened:
        decision = 'already_claim_ready'
        summary = 'Receipt remained claim-ready across both prior and current package states; promotion evidence mainly documents continuity rather than a new admission event.'
        next_step = 'Keep citing the current locator and regenerate only if a later review trigger changes the package state.'
    elif prior_authorized and not current_authorized:
        decision = 'regressed_from_claim_ready'
        summary = 'Receipt lost claim-ready authorization between the prior and current package states.'
        next_step = 'Treat the current package as regressed; close newly opened findings or regenerate remediation before restoring claim-ready citation.'
    else:
        decision = 'not_yet_promoted'
        summary = 'Receipt has not yet reached a promoted claim-ready state across the compared package states.'
        next_step = 'Close remaining non-pass findings and regenerate authorization before attempting promotion again.'

    promotion = {
        'schema_version': 1,
        'promotion_kind': 'successor_safe_ceremony_receipt_promotion',
        'receipt_id': current_assessment['receipt_id'],
        'journey_kind': current_assessment['journey_kind'],
        'prior_receipt_locator': {
            'ni_uri': prior_locator['ni_uri'],
            'digest_hex': prior_locator['digest_hex'],
            'source_path': prior_locator['source_path'],
        },
        'current_receipt_locator': {
            'ni_uri': current_locator['ni_uri'],
            'digest_hex': current_locator['digest_hex'],
            'source_path': current_locator['source_path'],
        },
        'prior_assessment_overall_status': prior_assessment['overall_status'],
        'current_assessment_overall_status': current_assessment['overall_status'],
        'prior_authorization_decision': prior_authorization['authorization_decision'],
        'current_authorization_decision': current_authorization['authorization_decision'],
        'closed_finding_codes': closed,
        'carried_finding_codes': carried,
        'newly_opened_finding_codes': newly_opened,
        'promotion_decision': decision,
        'basis_checks': basis_checks,
        'failed_basis_codes': failed_basis,
        'status_change_summary': summary,
        'review_trigger': current_authorization['review_trigger'],
        'recommended_next_step': next_step,
    }
    validate_promotion(promotion)
    return promotion



def make_review_watch(authorization: dict[str, Any], promotion: dict[str, Any], reviewed_on: str, max_review_interval_days: int = 180) -> dict[str, Any]:
    validate_authorization(authorization)
    validate_promotion(promotion)
    if authorization['receipt_id'] != promotion['receipt_id']:
        raise ValueError('authorization and promotion must point at the same receipt id')
    if max_review_interval_days < 1:
        raise ValueError('max_review_interval_days must be positive')

    reviewed = date.fromisoformat(reviewed_on)
    due = reviewed + timedelta(days=max_review_interval_days)

    promotion_clean = promotion['promotion_decision'] in {'promoted_to_claim_ready_citation', 'already_claim_ready'}
    review_trigger_present = bool(str(authorization['review_trigger']).strip())
    checks = [
        {
            'code': 'current_authorized',
            'passed': authorization['authorization_decision'] == 'authorized_for_claim_ready_citation',
            'summary': 'Current package is authorized for claim-ready citation.' if authorization['authorization_decision'] == 'authorized_for_claim_ready_citation' else 'Current package is not authorized for claim-ready citation and therefore must reopen now.',
        },
        {
            'code': 'promotion_clean_or_continuity',
            'passed': promotion_clean,
            'summary': 'Promotion state is either a fresh promotion or clean continuity.' if promotion_clean else 'Promotion state is regressed or not yet promoted, so freshness watch must reopen now.',
        },
        {
            'code': 'review_due_after_reviewed_on',
            'passed': due > reviewed,
            'summary': 'Periodic review due date lands after the reviewed-on date.' if due > reviewed else 'Computed due date does not land after the reviewed-on date.',
        },
        {
            'code': 'explicit_review_trigger_present',
            'passed': review_trigger_present,
            'summary': 'Authorization package names an explicit review trigger.' if review_trigger_present else 'Authorization package omitted an explicit review trigger.',
        },
    ]
    failed = [row['code'] for row in checks if not row['passed']]

    if not failed:
        watch_status = 'active_watch'
        summary = 'Receipt package is currently claim-ready but must reopen if any event trigger fires or if the periodic review interval elapses.'
    else:
        watch_status = 'reopen_now'
        summary = 'Receipt package is not in a clean claim-ready watch state; regenerate the package immediately before further citation.'

    watch = {
        'schema_version': 1,
        'review_watch_kind': 'successor_safe_ceremony_receipt_review_watch',
        'receipt_id': authorization['receipt_id'],
        'journey_kind': authorization['journey_kind'],
        'current_receipt_locator': {
            'ni_uri': authorization['receipt_locator']['ni_uri'],
            'digest_hex': authorization['receipt_locator']['digest_hex'],
            'source_path': authorization['receipt_locator']['source_path'],
        },
        'authorization_decision': authorization['authorization_decision'],
        'promotion_decision': promotion['promotion_decision'],
        'reviewed_on': reviewed.isoformat(),
        'max_review_interval_days': max_review_interval_days,
        'review_due_on': due.isoformat(),
        'watch_status': watch_status,
        'review_trigger': authorization['review_trigger'],
        'event_trigger_codes': [
            'ceremony_contract_changed',
            'protocol_surface_changed',
            'retained_evidence_changed',
            'retention_policy_changed',
            'new_nonpass_findings',
            'authorization_terms_changed',
            'review_interval_elapsed',
        ],
        'required_regeneration_sequence': [
            'locator',
            'assessment',
            'disposition',
            'remediation',
            'authorization',
            'promotion',
            'review_watch',
        ],
        'basis_checks': checks,
        'failed_basis_codes': failed,
        'watch_summary': summary,
    }
    validate_review_watch(watch)
    return watch



def make_review_verdict(review_watch: dict[str, Any], as_of: str, observed_trigger_codes: list[str] | None = None) -> dict[str, Any]:
    validate_review_watch(review_watch)
    current = date.fromisoformat(as_of)
    due = date.fromisoformat(review_watch['review_due_on'])
    observed = list(observed_trigger_codes or [])
    allowed_codes = set(review_watch['event_trigger_codes'])
    invalid = [code for code in observed if code not in allowed_codes]
    if invalid:
        raise ValueError(f'unknown observed trigger code(s): {", ".join(sorted(set(invalid)))}')
    observed = sorted(set(observed))
    matched = [code for code in review_watch['event_trigger_codes'] if code in observed]

    if current < due:
        timeliness_status = 'within_interval'
    elif current == due:
        timeliness_status = 'due_today'
    else:
        timeliness_status = 'overdue'

    checks = [
        {
            'code': 'watch_active_before_review',
            'passed': review_watch['watch_status'] == 'active_watch',
            'summary': 'Review watch was active before this review verdict was generated.' if review_watch['watch_status'] == 'active_watch' else 'Review watch had already reopened before this review verdict was generated.',
        },
        {
            'code': 'within_review_interval',
            'passed': current <= due,
            'summary': 'Current review date is still within the declared no-later-than review interval.' if current <= due else 'Current review date lands after the declared no-later-than review interval.',
        },
        {
            'code': 'no_reopen_trigger_observed',
            'passed': not matched,
            'summary': 'No declared reopen trigger was observed at review time.' if not matched else 'One or more declared reopen triggers were observed at review time.',
        },
        {
            'code': 'prior_package_authorized',
            'passed': review_watch['authorization_decision'] == 'authorized_for_claim_ready_citation',
            'summary': 'Watched package was previously authorized for claim-ready citation.' if review_watch['authorization_decision'] == 'authorized_for_claim_ready_citation' else 'Watched package was not authorized for claim-ready citation when the watch was created.',
        },
    ]
    failed = [row['code'] for row in checks if not row['passed']]

    continue_clean = not failed
    if continue_clean:
        review_decision = 'continue_claim_ready_citation'
        citation_status = 'claim_ready_citable'
        next_steps: list[str] = []
        summary = 'Review verdict keeps the receipt package claim-ready because the watch remained active, no reopen trigger fired, and the review interval has not elapsed.'
    else:
        review_decision = 'reopen_and_suspend_claim_ready_citation'
        citation_status = 'suspended_pending_regeneration'
        next_steps = review_watch['required_regeneration_sequence']
        if matched:
            summary = 'Review verdict suspends claim-ready citation because at least one declared reopen trigger fired; regenerate the package before further inheritor-facing citation.'
        elif current > due:
            summary = 'Review verdict suspends claim-ready citation because the declared review interval elapsed; regenerate the package before further inheritor-facing citation.'
        else:
            summary = 'Review verdict suspends claim-ready citation because the watched package was not in a clean active-watch state; regenerate the package before further inheritor-facing citation.'

    verdict = {
        'schema_version': 1,
        'review_verdict_kind': 'successor_safe_ceremony_receipt_review_verdict',
        'receipt_id': review_watch['receipt_id'],
        'journey_kind': review_watch['journey_kind'],
        'current_receipt_locator': {
            'ni_uri': review_watch['current_receipt_locator']['ni_uri'],
            'digest_hex': review_watch['current_receipt_locator']['digest_hex'],
            'source_path': review_watch['current_receipt_locator']['source_path'],
        },
        'watch_reviewed_on': review_watch['reviewed_on'],
        'watch_review_due_on': review_watch['review_due_on'],
        'as_of': current.isoformat(),
        'observed_trigger_codes': observed,
        'matched_reopen_trigger_codes': matched,
        'timeliness_status': timeliness_status,
        'prior_watch_status': review_watch['watch_status'],
        'review_decision': review_decision,
        'citation_status': citation_status,
        'basis_checks': checks,
        'failed_basis_codes': failed,
        'required_regeneration_sequence': next_steps,
        'review_summary': summary,
    }
    validate_review_verdict(verdict)
    return verdict

def make_citation_advisory(review_verdict: dict[str, Any]) -> dict[str, Any]:
    validate_review_verdict(review_verdict)

    clean = review_verdict['review_decision'] == 'continue_claim_ready_citation'
    if clean:
        advisory_decision = 'keep_current_locator_citable'
        reviewed_locator_status = 'citable'
        existing_citations_action = 'keep'
        new_citations_action = 'cite_reviewed_locator'
        advisory_reason_codes = ['review_clean']
        required_follow_up: list[str] = []
        summary = 'Citation advisory keeps the reviewed locator claim-ready because the review verdict stayed green and no reopen condition was triggered.'
    else:
        advisory_decision = 'withdraw_current_locator_from_claim_ready_citation'
        reviewed_locator_status = 'withdrawn'
        existing_citations_action = 'flag_for_withdrawal'
        new_citations_action = 'suspend_until_regenerated'
        advisory_reason_codes = sorted(set(review_verdict['matched_reopen_trigger_codes'] + review_verdict['failed_basis_codes'])) or ['review_reopened']
        required_follow_up = review_verdict['required_regeneration_sequence']
        if review_verdict['matched_reopen_trigger_codes']:
            summary = 'Citation advisory withdraws claim-ready use of the reviewed locator because one or more reopen triggers fired at review time; regenerate before further inheritor-facing citation.'
        elif review_verdict['timeliness_status'] == 'overdue':
            summary = 'Citation advisory withdraws claim-ready use of the reviewed locator because the declared review interval elapsed; regenerate before further inheritor-facing citation.'
        else:
            summary = 'Citation advisory withdraws claim-ready use of the reviewed locator because the review verdict did not remain in a clean keep-citing state.'

    advisory = {
        'schema_version': 1,
        'citation_advisory_kind': 'successor_safe_ceremony_receipt_citation_advisory',
        'receipt_id': review_verdict['receipt_id'],
        'journey_kind': review_verdict['journey_kind'],
        'reviewed_receipt_locator': {
            'ni_uri': review_verdict['current_receipt_locator']['ni_uri'],
            'digest_hex': review_verdict['current_receipt_locator']['digest_hex'],
            'source_path': review_verdict['current_receipt_locator']['source_path'],
        },
        'source_review_verdict': {
            'as_of': review_verdict['as_of'],
            'review_decision': review_verdict['review_decision'],
            'citation_status': review_verdict['citation_status'],
        },
        'advisory_decision': advisory_decision,
        'reviewed_locator_status': reviewed_locator_status,
        'advisory_reason_codes': advisory_reason_codes,
        'matched_reopen_trigger_codes': review_verdict['matched_reopen_trigger_codes'],
        'failed_review_basis_codes': review_verdict['failed_basis_codes'],
        'existing_citations_action': existing_citations_action,
        'new_citations_action': new_citations_action,
        'required_follow_up': required_follow_up,
        'advisory_summary': summary,
    }
    validate_citation_advisory(advisory)
    return advisory


def _normalized_component_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _file_component(role: str, path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    media_type = 'text/markdown' if path.suffix == '.md' else 'application/json'
    return {
        'role': role,
        'path': _normalized_component_path(path),
        'media_type': media_type,
        'sha256_hex': hashlib.sha256(data).hexdigest(),
        'bytes': len(data),
    }


def make_package_manifest(
    *,
    receipt_path: str | Path,
    rendered_markdown_path: str | Path,
    locator_path: str | Path,
    assessment_path: str | Path,
    disposition_path: str | Path,
    remediation_path: str | Path,
    authorization_path: str | Path,
    promotion_path: str | Path,
    review_watch_path: str | Path,
    review_verdict_path: str | Path,
    citation_advisory_path: str | Path,
) -> dict[str, Any]:
    receipt_path = Path(receipt_path)
    rendered_markdown_path = Path(rendered_markdown_path)
    locator_path = Path(locator_path)
    assessment_path = Path(assessment_path)
    disposition_path = Path(disposition_path)
    remediation_path = Path(remediation_path)
    authorization_path = Path(authorization_path)
    promotion_path = Path(promotion_path)
    review_watch_path = Path(review_watch_path)
    review_verdict_path = Path(review_verdict_path)
    citation_advisory_path = Path(citation_advisory_path)

    receipt = load_json(receipt_path)
    locator = load_json(locator_path)
    assessment = load_json(assessment_path)
    disposition = load_json(disposition_path)
    remediation = load_json(remediation_path)
    authorization = load_json(authorization_path)
    promotion = load_json(promotion_path)
    review_watch = load_json(review_watch_path)
    review_verdict = load_json(review_verdict_path)
    citation_advisory = load_json(citation_advisory_path)

    validate_receipt(receipt)
    validate_locator(locator)
    validate_assessment(assessment)
    validate_disposition(disposition)
    validate_remediation_plan(remediation)
    validate_authorization(authorization)
    validate_promotion(promotion)
    validate_review_watch(review_watch)
    validate_review_verdict(review_verdict)
    validate_citation_advisory(citation_advisory)

    receipt_id = receipt['id']
    journey_kind = receipt['journey_kind']
    for obj_name, obj in [
        ('locator', locator),
        ('assessment', assessment),
        ('disposition', disposition),
        ('remediation', remediation),
        ('authorization', authorization),
        ('promotion', promotion),
        ('review_watch', review_watch),
        ('review_verdict', review_verdict),
        ('citation_advisory', citation_advisory),
    ]:
        if obj['receipt_id'] != receipt_id:
            raise ValueError(f'{obj_name} receipt_id does not match receipt')
    for obj_name, obj in [
        ('assessment', assessment),
        ('disposition', disposition),
        ('remediation', remediation),
        ('authorization', authorization),
        ('promotion', promotion),
        ('review_watch', review_watch),
        ('review_verdict', review_verdict),
        ('citation_advisory', citation_advisory),
    ]:
        if obj.get('journey_kind') != journey_kind:
            raise ValueError(f'{obj_name} journey_kind does not match receipt')

    if locator['digest_hex'] != citation_advisory['reviewed_receipt_locator']['digest_hex']:
        raise ValueError('citation advisory must describe the current locator digest in the package manifest')
    if locator['ni_uri'] != citation_advisory['reviewed_receipt_locator']['ni_uri']:
        raise ValueError('citation advisory must describe the current locator ni URI in the package manifest')
    if locator['digest_hex'] != review_verdict['current_receipt_locator']['digest_hex']:
        raise ValueError('review verdict must describe the current locator digest in the package manifest')
    if locator['digest_hex'] != promotion['current_receipt_locator']['digest_hex']:
        raise ValueError('promotion must point at the current locator digest in the package manifest')
    if locator['digest_hex'] != authorization['receipt_locator']['digest_hex']:
        raise ValueError('authorization must point at the current locator digest in the package manifest')

    roles_and_paths = [
        ('receipt', receipt_path),
        ('rendered_markdown', rendered_markdown_path),
        ('locator', locator_path),
        ('assessment', assessment_path),
        ('disposition', disposition_path),
        ('remediation', remediation_path),
        ('authorization', authorization_path),
        ('promotion', promotion_path),
        ('review_watch', review_watch_path),
        ('review_verdict', review_verdict_path),
        ('citation_advisory', citation_advisory_path),
    ]
    components = [_file_component(role, path) for role, path in roles_and_paths]
    component_roles_present = [row['role'] for row in components]

    current_claim_status = citation_advisory['source_review_verdict']['citation_status']
    manifest_summary = (
        'Package manifest names the current authoritative successor-safe ceremony receipt artifacts and their file-level fixity so future stewards can find the package root without inferring membership from neighboring files.'
        if current_claim_status == 'claim_ready_citable'
        else 'Package manifest names the current successor-safe ceremony receipt artifacts and their file-level fixity while the package remains suspended pending regeneration.'
    )

    package_manifest = {
        'schema_version': 1,
        'package_manifest_kind': 'successor_safe_ceremony_receipt_package_manifest',
        'receipt_id': receipt_id,
        'journey_kind': journey_kind,
        'current_claim_status': current_claim_status,
        'active_receipt_locator': {
            'ni_uri': locator['ni_uri'],
            'digest_hex': locator['digest_hex'],
            'source_path': locator['source_path'],
        },
        'package_state': {
            'authorization_decision': authorization['authorization_decision'],
            'promotion_decision': promotion['promotion_decision'],
            'review_decision': review_verdict['review_decision'],
            'advisory_decision': citation_advisory['advisory_decision'],
        },
        'component_roles_present': component_roles_present,
        'components': components,
        'manifest_summary': manifest_summary,
    }
    validate_package_manifest(package_manifest)
    return package_manifest


def _json_file_reference(path: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    ref_path = Path(path)
    data = ref_path.read_bytes()
    return {
        'path': _normalized_component_path(ref_path),
        'sha256_hex': hashlib.sha256(data).hexdigest(),
        'current_claim_status': payload['current_claim_status'],
    }


def _sha256_file_reference(path: str | Path) -> dict[str, str]:
    ref_path = Path(path)
    data = ref_path.read_bytes()
    return {
        'path': _normalized_component_path(ref_path),
        'sha256_hex': hashlib.sha256(data).hexdigest(),
    }


def make_package_supersession(
    *,
    prior_manifest_path: str | Path,
    current_manifest_path: str | Path,
    prior_review_watch_path: str | Path,
    current_review_watch_path: str | Path,
    prior_review_verdict_path: str | Path,
    current_review_verdict_path: str | Path,
    prior_citation_advisory_path: str | Path,
    current_citation_advisory_path: str | Path,
) -> dict[str, Any]:
    prior_manifest_path = Path(prior_manifest_path)
    current_manifest_path = Path(current_manifest_path)
    prior_review_watch_path = Path(prior_review_watch_path)
    current_review_watch_path = Path(current_review_watch_path)
    prior_review_verdict_path = Path(prior_review_verdict_path)
    current_review_verdict_path = Path(current_review_verdict_path)
    prior_citation_advisory_path = Path(prior_citation_advisory_path)
    current_citation_advisory_path = Path(current_citation_advisory_path)

    prior_manifest = load_json(prior_manifest_path)
    current_manifest = load_json(current_manifest_path)
    prior_review_watch = load_json(prior_review_watch_path)
    current_review_watch = load_json(current_review_watch_path)
    prior_review_verdict = load_json(prior_review_verdict_path)
    current_review_verdict = load_json(current_review_verdict_path)
    prior_citation_advisory = load_json(prior_citation_advisory_path)
    current_citation_advisory = load_json(current_citation_advisory_path)

    validate_package_manifest(prior_manifest)
    validate_package_manifest(current_manifest)
    validate_review_watch(prior_review_watch)
    validate_review_watch(current_review_watch)
    validate_review_verdict(prior_review_verdict)
    validate_review_verdict(current_review_verdict)
    validate_citation_advisory(prior_citation_advisory)
    validate_citation_advisory(current_citation_advisory)

    if prior_manifest['receipt_id'] != current_manifest['receipt_id']:
        raise ValueError('package manifests must point at the same receipt id')
    if prior_manifest['journey_kind'] != current_manifest['journey_kind']:
        raise ValueError('package manifests must point at the same journey kind')

    receipt_id = current_manifest['receipt_id']
    journey_kind = current_manifest['journey_kind']
    if prior_review_watch['receipt_id'] != receipt_id or current_review_watch['receipt_id'] != receipt_id:
        raise ValueError('review watches must point at the same receipt id as the package manifests')
    if prior_review_verdict['receipt_id'] != receipt_id or current_review_verdict['receipt_id'] != receipt_id:
        raise ValueError('review verdicts must point at the same receipt id as the package manifests')
    if prior_citation_advisory['receipt_id'] != receipt_id or current_citation_advisory['receipt_id'] != receipt_id:
        raise ValueError('citation advisories must point at the same receipt id as the package manifests')

    prior_components = {row['role']: row for row in prior_manifest['components']}
    current_components = {row['role']: row for row in current_manifest['components']}
    changed_roles = sorted(
        role
        for role in current_manifest['component_roles_present']
        if prior_components[role]['sha256_hex'] != current_components[role]['sha256_hex']
        or prior_components[role]['path'] != current_components[role]['path']
        or prior_components[role]['bytes'] != current_components[role]['bytes']
    )
    if not changed_roles:
        raise ValueError('package supersession requires at least one changed component role')

    reasons: list[str] = []
    prior_locator = prior_manifest['active_receipt_locator']
    current_locator = current_manifest['active_receipt_locator']
    continuity = 'same_receipt_locator' if prior_locator['digest_hex'] == current_locator['digest_hex'] else 'rekeyed_receipt_locator'
    if continuity == 'same_receipt_locator' and prior_review_watch['review_due_on'] != current_review_watch['review_due_on']:
        reasons.append('review_window_renewed')
    if any(role in changed_roles for role in ['review_watch', 'review_verdict', 'citation_advisory']):
        reasons.append('freshness_artifacts_replaced')
    if prior_manifest['current_claim_status'] != current_manifest['current_claim_status']:
        reasons.append('claim_status_changed')
    if prior_manifest['package_state'] != current_manifest['package_state']:
        reasons.append('package_state_changed')
    if continuity == 'rekeyed_receipt_locator':
        reasons.append('receipt_locator_rekeyed')
    reasons = sorted(dict.fromkeys(reasons))

    if current_manifest['current_claim_status'] == 'claim_ready_citable':
        replacement_guidance = 'Treat the current package manifest as the authoritative package root for future claim-ready citation and keep the prior manifest only as package history.'
    else:
        replacement_guidance = 'Treat the current package manifest as the authoritative suspended package root and do not resume claim-ready citation until a later manifest restores a keep-citing state.'

    if continuity == 'same_receipt_locator':
        summary = 'Package supersession records that the current manifest replaces the prior manifest while preserving the same receipt locator, so future stewards can update freshness-era package state without rediscovering the authoritative replacement target.'
    else:
        summary = 'Package supersession records that the current manifest replaces the prior manifest and also rotates the active receipt locator, so future stewards can withdraw the old package root and cite only the replacement package.'

    package_supersession = {
        'schema_version': 1,
        'package_supersession_kind': 'successor_safe_ceremony_receipt_package_supersession',
        'receipt_id': receipt_id,
        'journey_kind': journey_kind,
        'prior_package_manifest': _json_file_reference(prior_manifest_path, prior_manifest),
        'current_package_manifest': _json_file_reference(current_manifest_path, current_manifest),
        'active_receipt_locator_continuity': {
            'continuity': continuity,
            'prior_digest_hex': prior_locator['digest_hex'],
            'current_digest_hex': current_locator['digest_hex'],
        },
        'supersession_reason_codes': reasons or ['package_state_changed'],
        'component_roles_replaced': changed_roles,
        'package_transition': {
            'supersession_decision': 'current_manifest_supersedes_prior_manifest',
            'prior_review_decision': prior_review_verdict['review_decision'],
            'current_review_decision': current_review_verdict['review_decision'],
            'prior_advisory_decision': prior_citation_advisory['advisory_decision'],
            'current_advisory_decision': current_citation_advisory['advisory_decision'],
        },
        'replacement_guidance': replacement_guidance,
        'supersession_summary': summary,
    }
    validate_package_supersession(package_supersession)
    return package_supersession


def _package_manifest_ref(manifest_path: str | Path, manifest: dict[str, Any]) -> dict[str, Any]:
    ref_path = Path(manifest_path)
    data = ref_path.read_bytes()
    return {
        'path': _normalized_component_path(ref_path),
        'sha256_hex': hashlib.sha256(data).hexdigest(),
        'current_claim_status': manifest['current_claim_status'],
    }


def _package_supersession_ref(supersession_path: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    ref_path = Path(supersession_path)
    data = ref_path.read_bytes()
    return {
        'path': _normalized_component_path(ref_path),
        'sha256_hex': hashlib.sha256(data).hexdigest(),
        'prior_manifest_path': payload['prior_package_manifest']['path'],
        'current_manifest_path': payload['current_package_manifest']['path'],
        'continuity': payload['active_receipt_locator_continuity']['continuity'],
        'supersession_reason_codes': payload['supersession_reason_codes'],
    }


def make_package_lineage(*, manifest_paths: list[str | Path], supersession_paths: list[str | Path] | None = None) -> dict[str, Any]:
    manifest_paths = [Path(p) for p in manifest_paths]
    supersession_paths = [Path(p) for p in (supersession_paths or [])]
    if not manifest_paths:
        raise ValueError('package lineage requires at least one package manifest')

    manifests = [load_json(path) for path in manifest_paths]
    supersessions = [load_json(path) for path in supersession_paths]

    for manifest in manifests:
        validate_package_manifest(manifest)
    for supersession in supersessions:
        validate_package_supersession(supersession)

    receipt_ids = {manifest['receipt_id'] for manifest in manifests}
    journey_kinds = {manifest['journey_kind'] for manifest in manifests}
    if len(receipt_ids) != 1 or len(journey_kinds) != 1:
        raise ValueError('all package manifests in a lineage must point at one receipt id and one journey kind')
    receipt_id = next(iter(receipt_ids))
    journey_kind = next(iter(journey_kinds))

    manifest_refs = [_package_manifest_ref(path, manifest) for path, manifest in zip(manifest_paths, manifests)]
    manifest_by_path = {ref['path']: manifest for ref, manifest in zip(manifest_refs, manifests)}
    manifest_ref_by_path = {ref['path']: ref for ref in manifest_refs}
    if len(manifest_by_path) != len(manifests):
        raise ValueError('package lineage manifest paths must be unique')

    supersession_refs = []
    incoming: dict[str, str] = {}
    outgoing: dict[str, str] = {}
    for path, supersession in zip(supersession_paths, supersessions):
        if supersession['receipt_id'] != receipt_id or supersession['journey_kind'] != journey_kind:
            raise ValueError('all package supersessions in a lineage must point at the same receipt id and journey kind as the manifests')
        prior_path = supersession['prior_package_manifest']['path']
        current_path = supersession['current_package_manifest']['path']
        if prior_path not in manifest_by_path or current_path not in manifest_by_path:
            raise ValueError('package supersession references a manifest path that is not present in the lineage manifest set')
        if manifest_ref_by_path[prior_path]['sha256_hex'] != supersession['prior_package_manifest']['sha256_hex']:
            raise ValueError('prior package manifest sha256 does not match the supersession record')
        if manifest_ref_by_path[current_path]['sha256_hex'] != supersession['current_package_manifest']['sha256_hex']:
            raise ValueError('current package manifest sha256 does not match the supersession record')
        if current_path in incoming:
            raise ValueError('package lineage requires each manifest to have at most one prior predecessor')
        if prior_path in outgoing:
            raise ValueError('package lineage requires each manifest to have at most one superseding successor')
        incoming[current_path] = prior_path
        outgoing[prior_path] = current_path
        supersession_refs.append(_package_supersession_ref(path, supersession))

    if len(manifests) == 1:
        if supersession_refs:
            raise ValueError('a single-manifest package lineage cannot carry supersession records')
        chain_paths = [manifest_refs[0]['path']]
    else:
        if len(supersession_refs) != len(manifests) - 1:
            raise ValueError('a multi-manifest package lineage must be fully linked by supersession records')
        roots = [path for path in manifest_by_path if path not in incoming]
        heads = [path for path in manifest_by_path if path not in outgoing]
        if len(roots) != 1 or len(heads) != 1:
            raise ValueError('package lineage must form one simple chain with exactly one root and one authoritative head')
        chain_paths = []
        current = roots[0]
        seen = set()
        while True:
            if current in seen:
                raise ValueError('package lineage contains a cycle')
            seen.add(current)
            chain_paths.append(current)
            if current not in outgoing:
                break
            current = outgoing[current]
        if len(chain_paths) != len(manifest_by_path):
            raise ValueError('package lineage must include every manifest exactly once in the authoritative chain')

    ordered_manifest_entries = []
    locator_digests = []
    for position, entry_path in enumerate(chain_paths, start=1):
        manifest = manifest_by_path[entry_path]
        ordered_manifest_entries.append({
            'position': position,
            'path': entry_path,
            'sha256_hex': manifest_ref_by_path[entry_path]['sha256_hex'],
            'current_claim_status': manifest['current_claim_status'],
            'review_decision': manifest['package_state']['review_decision'],
            'advisory_decision': manifest['package_state']['advisory_decision'],
            'active_receipt_locator_digest_hex': manifest['active_receipt_locator']['digest_hex'],
        })
        locator_digests.append(manifest['active_receipt_locator']['digest_hex'])

    supersession_by_prior = {ref['prior_manifest_path']: ref for ref in supersession_refs}
    ordered_supersession_entries = []
    for position, prior_path in enumerate(chain_paths[:-1], start=1):
        ref = supersession_by_prior[prior_path]
        ordered_supersession_entries.append({
            'position': position,
            'path': ref['path'],
            'sha256_hex': ref['sha256_hex'],
            'prior_manifest_path': ref['prior_manifest_path'],
            'current_manifest_path': ref['current_manifest_path'],
            'continuity': ref['continuity'],
            'supersession_reason_codes': ref['supersession_reason_codes'],
        })

    changed_roles = sorted({
        role
        for earlier_path, later_path in zip(chain_paths[:-1], chain_paths[1:])
        for role in manifest_by_path[later_path]['component_roles_present']
        if {row['role']: row for row in manifest_by_path[earlier_path]['components']}[role]['sha256_hex'] != {row['role']: row for row in manifest_by_path[later_path]['components']}[role]['sha256_hex']
        or {row['role']: row for row in manifest_by_path[earlier_path]['components']}[role]['path'] != {row['role']: row for row in manifest_by_path[later_path]['components']}[role]['path']
        or {row['role']: row for row in manifest_by_path[earlier_path]['components']}[role]['bytes'] != {row['role']: row for row in manifest_by_path[later_path]['components']}[role]['bytes']
    })

    authoritative_path = chain_paths[-1]
    authoritative_manifest = manifest_by_path[authoritative_path]
    distinct_locator_digests = sorted(dict.fromkeys(locator_digests))
    continuity = 'same_receipt_locator_across_chain' if len(distinct_locator_digests) == 1 else 'rekeyed_within_chain'

    lineage = {
        'schema_version': 1,
        'package_lineage_kind': 'successor_safe_ceremony_receipt_package_lineage',
        'receipt_id': receipt_id,
        'journey_kind': journey_kind,
        'authoritative_manifest': {
            'path': authoritative_path,
            'sha256_hex': manifest_ref_by_path[authoritative_path]['sha256_hex'],
            'current_claim_status': authoritative_manifest['current_claim_status'],
        },
        'manifest_chain': ordered_manifest_entries,
        'supersession_chain': ordered_supersession_entries,
        'lineage_continuity': {
            'continuity': continuity,
            'distinct_locator_digest_count': len(distinct_locator_digests),
            'distinct_locator_digest_hexes': distinct_locator_digests,
        },
        'current_authority_basis': {
            'chain_status': 'authoritative_head_identified',
            'head_position': len(chain_paths),
            'current_review_decision': authoritative_manifest['package_state']['review_decision'],
            'current_advisory_decision': authoritative_manifest['package_state']['advisory_decision'],
        },
        'changed_component_roles_across_chain': changed_roles,
        'lineage_summary': (
            'Package lineage names the authoritative package head and its ordered supersession chain so future stewards can recover the current package root, the older manifests it displaced, and whether the active receipt locator stayed stable across refreshes.'
            if len(chain_paths) > 1
            else 'Package lineage names the sole authoritative package manifest so future stewards do not need to infer package authority from neighboring files.'
        ),
    }
    validate_package_lineage(lineage)
    return lineage



def make_package_status_card(
    *,
    manifest_path: str | Path,
    review_watch_path: str | Path,
    review_verdict_path: str | Path,
    citation_advisory_path: str | Path,
) -> dict[str, Any]:
    manifest_path = Path(manifest_path)
    review_watch_path = Path(review_watch_path)
    review_verdict_path = Path(review_verdict_path)
    citation_advisory_path = Path(citation_advisory_path)

    manifest = load_json(manifest_path)
    review_watch = load_json(review_watch_path)
    review_verdict = load_json(review_verdict_path)
    citation_advisory = load_json(citation_advisory_path)

    validate_package_manifest(manifest)
    validate_review_watch(review_watch)
    validate_review_verdict(review_verdict)
    validate_citation_advisory(citation_advisory)

    receipt_id = manifest['receipt_id']
    journey_kind = manifest['journey_kind']
    if review_watch['receipt_id'] != receipt_id or review_verdict['receipt_id'] != receipt_id or citation_advisory['receipt_id'] != receipt_id:
        raise ValueError('package status card inputs must point at the same receipt id')
    if review_watch['journey_kind'] != journey_kind or review_verdict['journey_kind'] != journey_kind or citation_advisory['journey_kind'] != journey_kind:
        raise ValueError('package status card inputs must point at the same journey kind')

    manifest_ref = _json_file_reference(manifest_path, manifest)
    review_watch_ref = _sha256_file_reference(review_watch_path)
    review_verdict_ref = _sha256_file_reference(review_verdict_path)
    citation_advisory_ref = _sha256_file_reference(citation_advisory_path)

    if manifest['package_state']['review_decision'] != review_verdict['review_decision']:
        raise ValueError('package status card review verdict must match the manifest package state')
    if manifest['package_state']['advisory_decision'] != citation_advisory['advisory_decision']:
        raise ValueError('package status card citation advisory must match the manifest package state')
    if review_watch['watch_status'] == 'active_watch' and review_verdict['review_decision'] != 'continue_claim_ready_citation':
        raise ValueError('active review watches must continue claim-ready citation in the package status card')
    if review_watch['watch_status'] == 'reopen_now' and review_verdict['review_decision'] != 'reopen_and_suspend_claim_ready_citation':
        raise ValueError('reopen-now review watches must suspend claim-ready citation in the package status card')
    if review_verdict['review_decision'] == 'continue_claim_ready_citation' and citation_advisory['advisory_decision'] != 'keep_current_locator_citable':
        raise ValueError('keep-citing review verdicts must map to keep-current-locator citation advisories')
    if review_verdict['review_decision'] == 'reopen_and_suspend_claim_ready_citation' and citation_advisory['advisory_decision'] != 'withdraw_current_locator_from_claim_ready_citation':
        raise ValueError('reopen review verdicts must map to withdrawal citation advisories')

    currently_citable = review_verdict['citation_status'] == 'claim_ready_citable' and citation_advisory['new_citations_action'] == 'cite_reviewed_locator'

    status_card = {
        'schema_version': 1,
        'package_status_card_kind': 'successor_safe_ceremony_receipt_package_status_card',
        'receipt_id': receipt_id,
        'journey_kind': journey_kind,
        'authoritative_manifest': {
            'path': manifest_ref['path'],
            'sha256_hex': manifest_ref['sha256_hex'],
            'current_claim_status': manifest['current_claim_status'],
        },
        'active_receipt_locator_digest_hex': manifest['active_receipt_locator']['digest_hex'],
        'current_review_window': {
            'watch_status': review_watch['watch_status'],
            'reviewed_on': review_watch['reviewed_on'],
            'review_due_on': review_watch['review_due_on'],
            'max_review_interval_days': review_watch['max_review_interval_days'],
        },
        'current_review_state': {
            'as_of': review_verdict['as_of'],
            'review_decision': review_verdict['review_decision'],
            'failed_basis_codes': review_verdict['failed_basis_codes'],
            'observed_trigger_codes': review_verdict['observed_trigger_codes'],
            'matched_reopen_trigger_codes': review_verdict['matched_reopen_trigger_codes'],
        },
        'citation_guidance': {
            'advisory_decision': citation_advisory['advisory_decision'],
            'existing_citations_action': citation_advisory['existing_citations_action'],
            'new_citations_action': citation_advisory['new_citations_action'],
        },
        'currently_citable': currently_citable,
        'required_regeneration_sequence': citation_advisory['required_follow_up'],
        'status_inputs': {
            'review_watch': review_watch_ref,
            'review_verdict': review_verdict_ref,
            'citation_advisory': citation_advisory_ref,
        },
        'status_summary': (
            'Package status card collapses the live review window, as-of review verdict, and downstream citation guidance into one compact status object so future stewards can tell whether the current package head remains claim-ready citable, until when, and what would reopen it.'
            if currently_citable
            else 'Package status card collapses the live review window, as-of review verdict, and downstream citation guidance into one compact status object so future stewards can tell that the current package head is suspended pending regeneration and which follow-up sequence must run before claim-ready citation resumes.'
        ),
    }
    validate_package_status_card(status_card)
    return status_card


VERIFICATION_CHECK_SPECS = [
    {
        'check_id': 'research_docs',
        'lane': 'python_integrity',
        'command': ['python3', 'scripts/test/check_research_docs.py'],
        'success_summary': 'research-docs: ok',
    },
    {
        'check_id': 'schema_json_valid',
        'lane': 'python_integrity',
        'command': ['python3', 'scripts/test/check_schema_json_valid.py'],
        'success_summary': 'schema-json: ok',
    },
    {
        'check_id': 'scripts_compile',
        'lane': 'python_integrity',
        'command': ['python3', 'scripts/test/check_scripts_compile.py'],
        'success_summary': 'scripts-compile: ok',
    },
    {
        'check_id': 'repo_controls',
        'lane': 'python_integrity',
        'command': ['python3', '-m', 'unittest', 'tests.control.test_repo_controls'],
        'success_summary': 'repo-controls: ok',
    },
    {
        'check_id': 'python_certify_tests',
        'lane': 'python_integrity',
        'command': ['python3', '-m', 'pytest', '-q', 'grlab/tests/test_certify_cli.py', 'grlab/tests/test_certify_schema.py'],
        'success_summary': 'python-certify-tests: ok',
    },
    {
        'check_id': 'doctor_rust_probe',
        'lane': 'rust_boundary',
        'command': ['bash', './scripts/doctor.sh'],
        'blocked_summary': 'doctor blocked missing cargo',
    },
    {
        'check_id': 'quick_harness_rust_lane',
        'lane': 'rust_boundary',
        'command': ['bash', './scripts/test/run_harness.sh', 'quick'],
        'blocked_summary': 'quick harness blocked missing junest',
    },
]


def _truncate_summary(text: str, *, limit: int = 180) -> str:
    cleaned = ' '.join(text.strip().split())
    if not cleaned:
        return ''
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1] + '…'


def _classify_blocked_outcome(output: str) -> tuple[str, list[str]] | None:
    lowered = output.lower()
    blockers: list[str] = []
    if 'cargo unavailable' in lowered or 'cargo not found' in lowered or 'cargo may still function via wrapper' in lowered:
        blockers.append('missing_cargo')
    if 'junest not found' in lowered:
        blockers.append('missing_junest')
    if not blockers:
        return None
    return ('blocked_missing_toolchain', sorted(set(blockers)))


def _run_verification_check(spec: dict[str, Any]) -> dict[str, Any]:
    completed = subprocess.run(
        spec['command'],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=240,
        check=False,
    )
    output = '\n'.join(part for part in [completed.stdout, completed.stderr] if part).strip()
    summary = _truncate_summary(output.splitlines()[-1] if output else '')
    if completed.returncode == 0:
        return {
            'check_id': spec['check_id'],
            'lane': spec['lane'],
            'command': ' '.join(spec['command']),
            'status': 'pass',
            'outcome_code': 'ok',
            'summary': spec.get('success_summary', summary or 'ok'),
        }
    blocked = _classify_blocked_outcome(output)
    if blocked is not None:
        outcome_code, blockers = blocked
        return {
            'check_id': spec['check_id'],
            'lane': spec['lane'],
            'command': ' '.join(spec['command']),
            'status': 'blocked',
            'outcome_code': outcome_code,
            'summary': spec.get('blocked_summary', summary or 'blocked by missing toolchain components'),
            'blocker_codes': blockers,
        }
    return {
        'check_id': spec['check_id'],
        'lane': spec['lane'],
        'command': ' '.join(spec['command']),
        'status': 'fail',
        'outcome_code': 'command_failed',
        'summary': summary or f"command exited {completed.returncode}",
    }


def make_package_verification_report(
    *,
    manifest_path: str | Path,
    status_card_path: str | Path,
    as_of: str,
) -> dict[str, Any]:
    manifest_path = Path(manifest_path)
    status_card_path = Path(status_card_path)

    manifest = load_json(manifest_path)
    status_card = load_json(status_card_path)

    validate_package_manifest(manifest)
    validate_package_status_card(status_card)

    receipt_id = manifest['receipt_id']
    journey_kind = manifest['journey_kind']
    if status_card['receipt_id'] != receipt_id:
        raise ValueError('package verification report inputs must point at the same receipt id')
    if status_card['journey_kind'] != journey_kind:
        raise ValueError('package verification report inputs must point at the same journey kind')
    manifest_ref = _json_file_reference(manifest_path, manifest)
    if status_card['authoritative_manifest']['path'] != manifest_ref['path']:
        raise ValueError('package verification report requires the supplied manifest to match the status card authoritative manifest path')
    if status_card['authoritative_manifest']['sha256_hex'] != manifest_ref['sha256_hex']:
        raise ValueError('package verification report requires the supplied manifest to match the status card authoritative manifest sha256')

    checks = [_run_verification_check(spec) for spec in VERIFICATION_CHECK_SPECS]
    pass_count = sum(1 for row in checks if row['status'] == 'pass')
    blocked_count = sum(1 for row in checks if row['status'] == 'blocked')
    fail_count = sum(1 for row in checks if row['status'] == 'fail')
    missing_tools = sorted({code.removeprefix('missing_') for row in checks for code in row.get('blocker_codes', []) if code.startswith('missing_')})

    if fail_count:
        verification_decision = 'verification_failed'
        rust_lane_status = 'failed_other'
    elif blocked_count == 0:
        verification_decision = 'verified_full_stack'
        rust_lane_status = 'available'
    elif all(row['status'] != 'blocked' or row['lane'] == 'rust_boundary' for row in checks):
        verification_decision = 'verified_python_lane_only'
        rust_lane_status = 'blocked_missing_toolchain'
    else:
        verification_decision = 'verification_failed'
        rust_lane_status = 'failed_other'

    blocked_follow_up = []
    if rust_lane_status == 'blocked_missing_toolchain':
        if 'cargo' in missing_tools:
            blocked_follow_up.append('rerun_doctor_after_cargo_available')
        if 'junest' in missing_tools:
            blocked_follow_up.append('rerun_quick_harness_after_junest_available')

    current_citation_state = 'citable_now' if status_card['currently_citable'] else 'suspended_pending_regeneration'
    verification_report = {
        'schema_version': 1,
        'package_verification_report_kind': 'successor_safe_ceremony_receipt_package_verification_report',
        'receipt_id': receipt_id,
        'journey_kind': journey_kind,
        'as_of': as_of,
        'authoritative_manifest': {
            'path': manifest_ref['path'],
            'sha256_hex': manifest_ref['sha256_hex'],
            'current_claim_status': manifest['current_claim_status'],
        },
        'active_receipt_locator_digest_hex': manifest['active_receipt_locator']['digest_hex'],
        'current_citation_state': current_citation_state,
        'verification_scope': {
            'package_status_card': {
                'path': _normalized_component_path(status_card_path),
                'sha256_hex': _sha256_file_reference(status_card_path)['sha256_hex'],
                'currently_citable': status_card['currently_citable'],
            },
            'validation_profile_id': 'successor_safe_ceremony_receipt_package_python_lane_plus_rust_boundary_v1',
        },
        'checks': checks,
        'summary_counts': {
            'pass_count': pass_count,
            'blocked_count': blocked_count,
            'fail_count': fail_count,
        },
        'verification_decision': verification_decision,
        'environment_boundary': {
            'rust_lane_status': rust_lane_status,
            'missing_tools': missing_tools,
            'blocked_follow_up': blocked_follow_up,
        },
        'verification_summary': (
            'Package verification report records that the local Python integrity lane passed for the current authoritative package while the Rust execution lane remained blocked only by missing cargo/junest in this cloudtainer.'
            if verification_decision == 'verified_python_lane_only'
            else 'Package verification report records that the current authoritative package passed the full local validation profile, including the Rust execution lane.'
            if verification_decision == 'verified_full_stack'
            else 'Package verification report records that the current authoritative package did not clear the local validation profile and should not be treated as fully verified until the failing checks are rerun cleanly.'
        ),
    }
    validate_package_verification_report(verification_report)
    return verification_report



def make_package_claim_scope(
    *,
    manifest_path: str | Path,
    status_card_path: str | Path,
    verification_report_path: str | Path,
) -> dict[str, Any]:
    manifest_path = Path(manifest_path)
    status_card_path = Path(status_card_path)
    verification_report_path = Path(verification_report_path)

    manifest = load_json(manifest_path)
    status_card = load_json(status_card_path)
    verification_report = load_json(verification_report_path)

    validate_package_manifest(manifest)
    validate_package_status_card(status_card)
    validate_package_verification_report(verification_report)

    receipt_id = manifest['receipt_id']
    journey_kind = manifest['journey_kind']
    if status_card['receipt_id'] != receipt_id or verification_report['receipt_id'] != receipt_id:
        raise ValueError('package claim scope inputs must point at the same receipt id')
    if status_card['journey_kind'] != journey_kind or verification_report['journey_kind'] != journey_kind:
        raise ValueError('package claim scope inputs must point at the same journey kind')

    manifest_ref = _json_file_reference(manifest_path, manifest)
    status_card_ref = _sha256_file_reference(status_card_path)
    verification_report_ref = _sha256_file_reference(verification_report_path)

    if status_card['authoritative_manifest']['path'] != manifest_ref['path'] or status_card['authoritative_manifest']['sha256_hex'] != manifest_ref['sha256_hex']:
        raise ValueError('package claim scope requires the supplied manifest to match the status card authoritative manifest')
    if verification_report['authoritative_manifest']['path'] != manifest_ref['path'] or verification_report['authoritative_manifest']['sha256_hex'] != manifest_ref['sha256_hex']:
        raise ValueError('package claim scope requires the supplied manifest to match the verification report authoritative manifest')

    verification_decision = verification_report['verification_decision']
    currently_citable = status_card['currently_citable']

    if not currently_citable:
        claim_scope_decision = 'citation_suspended_pending_regeneration'
        allowed_claims = ['current_package_identity', 'current_locator_identity']
        restricted_claims = ['current_citation_posture', 'current_review_window', 'python_integrity_results', 'full_local_validation_profile', 'rust_execution_results', 'engine_behavior_runtime_claims']
        required_qualifiers = [
            'Do not cite the current package as claim-ready until the required regeneration sequence completes.',
            'Treat the current package as retained-for-repair state rather than a live verified citation target.',
        ]
        broader_requirements = status_card['required_regeneration_sequence']
        summary = 'Package claim scope records that the current package is not presently citable and should not be used for downstream verified claims until regeneration completes.'
    elif verification_decision == 'verified_full_stack':
        claim_scope_decision = 'citation_allowed_full_stack_claims'
        allowed_claims = ['current_package_identity', 'current_locator_identity', 'current_citation_posture', 'current_review_window', 'python_integrity_results', 'full_local_validation_profile', 'rust_execution_results']
        restricted_claims = []
        required_qualifiers = ['Cite the reviewed locator or package head when making full-stack verification claims.']
        broader_requirements = []
        summary = 'Package claim scope records that the current package is citable and the full local validation profile, including the Rust execution lane, cleared successfully.'
    elif verification_decision == 'verified_python_lane_only':
        claim_scope_decision = 'citation_allowed_non_runtime_claims_only'
        allowed_claims = ['current_package_identity', 'current_locator_identity', 'current_citation_posture', 'current_review_window', 'python_integrity_results']
        restricted_claims = ['full_local_validation_profile', 'rust_execution_results', 'engine_behavior_runtime_claims']
        broader_requirements = verification_report['environment_boundary']['blocked_follow_up']
        required_qualifiers = [
            'Current claim-ready citation is supported for ceremony-contract, locator, freshness, and Python-integrity statements only.',
            'Do not claim Rust execution, end-to-end runtime behavior, or full-stack local validation in this cloudtainer until the blocked follow-up steps complete.',
        ]
        summary = 'Package claim scope records that the current package is citable for contract, locator, freshness, and Python-integrity statements, but not for Rust execution or end-to-end runtime claims because the Rust lane is still blocked in this cloudtainer.'
    else:
        claim_scope_decision = 'citation_requires_reverification'
        allowed_claims = ['current_package_identity', 'current_locator_identity']
        restricted_claims = ['current_citation_posture', 'current_review_window', 'python_integrity_results', 'full_local_validation_profile', 'rust_execution_results', 'engine_behavior_runtime_claims']
        broader_requirements = verification_report['environment_boundary']['blocked_follow_up']
        required_qualifiers = ['Do not treat the package as verified beyond identity-level discovery until the verification report is rerun cleanly.']
        summary = 'Package claim scope records that the current package needs reverification before downstream verified-claim statements should be made.'

    package_claim_scope = {
        'schema_version': 1,
        'package_claim_scope_kind': 'successor_safe_ceremony_receipt_package_claim_scope',
        'receipt_id': receipt_id,
        'journey_kind': journey_kind,
        'authoritative_manifest': {
            'path': manifest_ref['path'],
            'sha256_hex': manifest_ref['sha256_hex'],
            'current_claim_status': manifest['current_claim_status'],
        },
        'active_receipt_locator_digest_hex': manifest['active_receipt_locator']['digest_hex'],
        'scope_inputs': {
            'package_status_card': {
                'path': status_card_ref['path'],
                'sha256_hex': status_card_ref['sha256_hex'],
                'currently_citable': currently_citable,
            },
            'package_verification_report': {
                'path': verification_report_ref['path'],
                'sha256_hex': verification_report_ref['sha256_hex'],
                'verification_decision': verification_decision,
            },
        },
        'claim_scope_decision': claim_scope_decision,
        'allowed_claim_classes': allowed_claims,
        'restricted_claim_classes': restricted_claims,
        'required_qualifiers': required_qualifiers,
        'broader_claims_requirements': broader_requirements,
        'scope_summary': summary,
    }
    validate_package_claim_scope(package_claim_scope)
    return package_claim_scope


def make_package_reliance_card(
    *,
    manifest_path: str | Path,
    status_card_path: str | Path,
    verification_report_path: str | Path,
    claim_scope_path: str | Path,
) -> dict[str, Any]:
    manifest_path = Path(manifest_path)
    status_card_path = Path(status_card_path)
    verification_report_path = Path(verification_report_path)
    claim_scope_path = Path(claim_scope_path)

    manifest = load_json(manifest_path)
    status_card = load_json(status_card_path)
    verification_report = load_json(verification_report_path)
    claim_scope = load_json(claim_scope_path)

    validate_package_manifest(manifest)
    validate_package_status_card(status_card)
    validate_package_verification_report(verification_report)
    validate_package_claim_scope(claim_scope)

    receipt_id = manifest['receipt_id']
    journey_kind = manifest['journey_kind']
    for label, obj in (
        ('status card', status_card),
        ('verification report', verification_report),
        ('claim scope', claim_scope),
    ):
        if obj['receipt_id'] != receipt_id:
            raise ValueError(f'package reliance card {label} must match the manifest receipt id')
        if obj['journey_kind'] != journey_kind:
            raise ValueError(f'package reliance card {label} must match the manifest journey kind')
        if obj['authoritative_manifest']['path'] != _json_file_reference(manifest_path, manifest)['path']:
            raise ValueError(f'package reliance card {label} authoritative manifest path must match the manifest path')
        if obj['authoritative_manifest']['sha256_hex'] != _json_file_reference(manifest_path, manifest)['sha256_hex']:
            raise ValueError(f'package reliance card {label} authoritative manifest sha256 must match the manifest sha256')

    if status_card['active_receipt_locator_digest_hex'] != manifest['active_receipt_locator']['digest_hex']:
        raise ValueError('package reliance card status card locator digest must match the manifest locator digest')
    if verification_report['active_receipt_locator_digest_hex'] != manifest['active_receipt_locator']['digest_hex']:
        raise ValueError('package reliance card verification report locator digest must match the manifest locator digest')
    if claim_scope['active_receipt_locator_digest_hex'] != manifest['active_receipt_locator']['digest_hex']:
        raise ValueError('package reliance card claim scope locator digest must match the manifest locator digest')
    if claim_scope['scope_inputs']['package_status_card']['path'] != _sha256_file_reference(status_card_path)['path']:
        raise ValueError('package reliance card claim scope must reference the same status card path')
    if claim_scope['scope_inputs']['package_verification_report']['path'] != _sha256_file_reference(verification_report_path)['path']:
        raise ValueError('package reliance card claim scope must reference the same verification report path')

    manifest_ref = _json_file_reference(manifest_path, manifest)
    status_card_ref = _sha256_file_reference(status_card_path)
    verification_report_ref = _sha256_file_reference(verification_report_path)
    claim_scope_ref = _sha256_file_reference(claim_scope_path)

    if not status_card['currently_citable'] or claim_scope['claim_scope_decision'] == 'citation_suspended_pending_regeneration':
        reliance_decision = 'do_not_rely_until_regenerated'
    elif claim_scope['claim_scope_decision'] == 'citation_allowed_non_runtime_claims_only':
        reliance_decision = 'rely_with_non_runtime_scope_only'
    elif claim_scope['claim_scope_decision'] == 'citation_allowed_full_stack_claims':
        reliance_decision = 'rely_for_full_stack_claims'
    else:
        reliance_decision = 'rely_only_after_reverification'

    package_reliance_card = {
        'schema_version': 1,
        'package_reliance_card_kind': 'successor_safe_ceremony_receipt_package_reliance_card',
        'receipt_id': receipt_id,
        'journey_kind': journey_kind,
        'authoritative_manifest': {
            'path': manifest_ref['path'],
            'sha256_hex': manifest_ref['sha256_hex'],
            'current_claim_status': manifest['current_claim_status'],
        },
        'active_receipt_locator_digest_hex': manifest['active_receipt_locator']['digest_hex'],
        'reliance_inputs': {
            'package_status_card': {
                'path': status_card_ref['path'],
                'sha256_hex': status_card_ref['sha256_hex'],
                'currently_citable': status_card['currently_citable'],
            },
            'package_verification_report': {
                'path': verification_report_ref['path'],
                'sha256_hex': verification_report_ref['sha256_hex'],
                'verification_decision': verification_report['verification_decision'],
            },
            'package_claim_scope': {
                'path': claim_scope_ref['path'],
                'sha256_hex': claim_scope_ref['sha256_hex'],
                'claim_scope_decision': claim_scope['claim_scope_decision'],
            },
        },
        'reliance_decision': reliance_decision,
        'currently_citable': status_card['currently_citable'],
        'allowed_claim_classes': claim_scope['allowed_claim_classes'],
        'restricted_claim_classes': claim_scope['restricted_claim_classes'],
        'required_qualifiers': claim_scope['required_qualifiers'],
        'broader_claims_requirements': claim_scope['broader_claims_requirements'],
        'verification_basis': {
            'verification_decision': verification_report['verification_decision'],
            'pass_count': verification_report['summary_counts']['pass_count'],
            'blocked_count': verification_report['summary_counts']['blocked_count'],
            'fail_count': verification_report['summary_counts']['fail_count'],
            'missing_tools': verification_report['environment_boundary']['missing_tools'],
        },
        'reliance_summary': (
            'Package reliance card collapses the current citable posture, local verification basis, and allowed-versus-restricted claim classes into one compact downstream reliance object so future stewards can tell what they may safely rely on right now without reconciling the status card, verification report, and claim scope by hand.'
            if status_card['currently_citable']
            else 'Package reliance card collapses the current not-citable posture, local verification basis, and blocked claim classes into one compact downstream reliance object so future stewards can tell that reuse must wait for regeneration rather than inferring it from neighboring package artifacts.'
        ),
    }
    validate_package_reliance_card(package_reliance_card)
    return package_reliance_card


def make_package_head(
    *,
    manifest_path: str | Path,
    lineage_path: str | Path,
    review_verdict_path: str | Path,
    citation_advisory_path: str | Path,
    status_card_path: str | Path,
    verification_report_path: str | Path,
    claim_scope_path: str | Path,
    reliance_card_path: str | Path,
) -> dict[str, Any]:
    manifest_path = Path(manifest_path)
    lineage_path = Path(lineage_path)
    review_verdict_path = Path(review_verdict_path)
    citation_advisory_path = Path(citation_advisory_path)
    status_card_path = Path(status_card_path)
    verification_report_path = Path(verification_report_path)
    claim_scope_path = Path(claim_scope_path)
    reliance_card_path = Path(reliance_card_path)

    manifest = load_json(manifest_path)
    lineage = load_json(lineage_path)
    review_verdict = load_json(review_verdict_path)
    citation_advisory = load_json(citation_advisory_path)
    status_card = load_json(status_card_path)
    verification_report = load_json(verification_report_path)
    claim_scope = load_json(claim_scope_path)
    reliance_card = load_json(reliance_card_path)

    validate_package_manifest(manifest)
    validate_package_lineage(lineage)
    validate_review_verdict(review_verdict)
    validate_citation_advisory(citation_advisory)
    validate_package_status_card(status_card)
    validate_package_verification_report(verification_report)
    validate_package_claim_scope(claim_scope)
    validate_package_reliance_card(reliance_card)

    receipt_id = manifest['receipt_id']
    journey_kind = manifest['journey_kind']
    if lineage['receipt_id'] != receipt_id or review_verdict['receipt_id'] != receipt_id or citation_advisory['receipt_id'] != receipt_id or status_card['receipt_id'] != receipt_id or verification_report['receipt_id'] != receipt_id or claim_scope['receipt_id'] != receipt_id:
        raise ValueError('package head inputs must point at the same receipt id')
    if lineage['journey_kind'] != journey_kind or review_verdict['journey_kind'] != journey_kind or citation_advisory['journey_kind'] != journey_kind or status_card['journey_kind'] != journey_kind or verification_report['journey_kind'] != journey_kind or claim_scope['journey_kind'] != journey_kind:
        raise ValueError('package head inputs must point at the same journey kind')

    manifest_ref = _json_file_reference(manifest_path, manifest)
    lineage_ref = _sha256_file_reference(lineage_path)
    review_verdict_ref = _sha256_file_reference(review_verdict_path)
    citation_advisory_ref = _sha256_file_reference(citation_advisory_path)
    status_card_ref = _sha256_file_reference(status_card_path)
    verification_report_ref = _sha256_file_reference(verification_report_path)
    claim_scope_ref = _sha256_file_reference(claim_scope_path)
    reliance_card_ref = _sha256_file_reference(reliance_card_path)

    if lineage['authoritative_manifest']['path'] != manifest_ref['path']:
        raise ValueError('package head requires the supplied manifest to be the lineage authoritative manifest')
    if lineage['authoritative_manifest']['sha256_hex'] != manifest_ref['sha256_hex']:
        raise ValueError('package head manifest sha256 does not match lineage authoritative manifest sha256')
    if lineage['authoritative_manifest']['current_claim_status'] != manifest['current_claim_status']:
        raise ValueError('package head manifest claim status does not match the lineage authoritative manifest claim status')
    if manifest['package_state']['review_decision'] != review_verdict['review_decision']:
        raise ValueError('package head review verdict must match the manifest package state')
    if manifest['package_state']['advisory_decision'] != citation_advisory['advisory_decision']:
        raise ValueError('package head citation advisory must match the manifest package state')
    if lineage['current_authority_basis']['current_review_decision'] != review_verdict['review_decision']:
        raise ValueError('package head review verdict must match the lineage head review decision')
    if lineage['current_authority_basis']['current_advisory_decision'] != citation_advisory['advisory_decision']:
        raise ValueError('package head advisory must match the lineage head advisory decision')
    if status_card['authoritative_manifest']['path'] != manifest_ref['path'] or status_card['authoritative_manifest']['sha256_hex'] != manifest_ref['sha256_hex']:
        raise ValueError('package head status card must point at the same authoritative manifest')
    if status_card['current_review_state']['review_decision'] != review_verdict['review_decision']:
        raise ValueError('package head status card must match the review verdict decision')
    if status_card['citation_guidance']['advisory_decision'] != citation_advisory['advisory_decision']:
        raise ValueError('package head status card must match the citation advisory decision')
    if verification_report['authoritative_manifest']['path'] != manifest_ref['path'] or verification_report['authoritative_manifest']['sha256_hex'] != manifest_ref['sha256_hex']:
        raise ValueError('package head verification report must point at the same authoritative manifest')
    if claim_scope['authoritative_manifest']['path'] != manifest_ref['path'] or claim_scope['authoritative_manifest']['sha256_hex'] != manifest_ref['sha256_hex']:
        raise ValueError('package head claim scope must point at the same authoritative manifest')
    if claim_scope['scope_inputs']['package_status_card']['path'] != status_card_ref['path'] or claim_scope['scope_inputs']['package_status_card']['sha256_hex'] != status_card_ref['sha256_hex']:
        raise ValueError('package head claim scope must point at the same package status card')
    if claim_scope['scope_inputs']['package_verification_report']['path'] != verification_report_ref['path'] or claim_scope['scope_inputs']['package_verification_report']['sha256_hex'] != verification_report_ref['sha256_hex']:
        raise ValueError('package head claim scope must point at the same package verification report')
    if reliance_card['authoritative_manifest']['path'] != manifest_ref['path'] or reliance_card['authoritative_manifest']['sha256_hex'] != manifest_ref['sha256_hex']:
        raise ValueError('package head reliance card must point at the same authoritative manifest')
    if reliance_card['reliance_inputs']['package_status_card']['path'] != status_card_ref['path'] or reliance_card['reliance_inputs']['package_status_card']['sha256_hex'] != status_card_ref['sha256_hex']:
        raise ValueError('package head reliance card must point at the same package status card')
    if reliance_card['reliance_inputs']['package_verification_report']['path'] != verification_report_ref['path'] or reliance_card['reliance_inputs']['package_verification_report']['sha256_hex'] != verification_report_ref['sha256_hex']:
        raise ValueError('package head reliance card must point at the same package verification report')
    if reliance_card['reliance_inputs']['package_claim_scope']['path'] != claim_scope_ref['path'] or reliance_card['reliance_inputs']['package_claim_scope']['sha256_hex'] != claim_scope_ref['sha256_hex']:
        raise ValueError('package head reliance card must point at the same package claim scope')

    links = [
        {
            'rel': 'latest-version',
            'target_kind': 'package_manifest',
            'path': manifest_ref['path'],
            'sha256_hex': manifest_ref['sha256_hex'],
        },
        {
            'rel': 'version-history',
            'target_kind': 'package_lineage',
            'path': lineage_ref['path'],
            'sha256_hex': lineage_ref['sha256_hex'],
        },
        {
            'rel': 'describedby',
            'target_kind': 'review_verdict',
            'path': review_verdict_ref['path'],
            'sha256_hex': review_verdict_ref['sha256_hex'],
        },
        {
            'rel': 'describedby',
            'target_kind': 'citation_advisory',
            'path': citation_advisory_ref['path'],
            'sha256_hex': citation_advisory_ref['sha256_hex'],
        },
        {
            'rel': 'describedby',
            'target_kind': 'package_verification_report',
            'path': verification_report_ref['path'],
            'sha256_hex': verification_report_ref['sha256_hex'],
        },
        {
            'rel': 'describedby',
            'target_kind': 'package_claim_scope',
            'path': claim_scope_ref['path'],
            'sha256_hex': claim_scope_ref['sha256_hex'],
        },
        {
            'rel': 'describedby',
            'target_kind': 'package_reliance_card',
            'path': reliance_card_ref['path'],
            'sha256_hex': reliance_card_ref['sha256_hex'],
        },
        {
            'rel': 'status',
            'target_kind': 'package_status_card',
            'path': status_card_ref['path'],
            'sha256_hex': status_card_ref['sha256_hex'],
        },
    ]

    if len(lineage['manifest_chain']) > 1:
        predecessor = lineage['manifest_chain'][-2]
        links.append({
            'rel': 'predecessor-version',
            'target_kind': 'previous_package_manifest',
            'path': predecessor['path'],
            'sha256_hex': predecessor['sha256_hex'],
        })

    package_head = {
        'schema_version': 1,
        'package_head_kind': 'successor_safe_ceremony_receipt_package_head',
        'receipt_id': receipt_id,
        'journey_kind': journey_kind,
        'authoritative_manifest': {
            'path': manifest_ref['path'],
            'sha256_hex': manifest_ref['sha256_hex'],
            'current_claim_status': manifest['current_claim_status'],
        },
        'package_lineage': {
            'path': lineage_ref['path'],
            'sha256_hex': lineage_ref['sha256_hex'],
            'head_position': lineage['current_authority_basis']['head_position'],
            'chain_length': len(lineage['manifest_chain']),
        },
        'active_receipt_locator_digest_hex': manifest['active_receipt_locator']['digest_hex'],
        'current_package_state': {
            'current_claim_status': manifest['current_claim_status'],
            'review_decision': review_verdict['review_decision'],
            'advisory_decision': citation_advisory['advisory_decision'],
            'verification_decision': verification_report['verification_decision'],
            'claim_scope_decision': claim_scope['claim_scope_decision'],
        },
        'current_status_card': {
            'path': status_card_ref['path'],
            'sha256_hex': status_card_ref['sha256_hex'],
        },
        'current_verification_report': {
            'path': verification_report_ref['path'],
            'sha256_hex': verification_report_ref['sha256_hex'],
        },
        'current_claim_scope': {
            'path': claim_scope_ref['path'],
            'sha256_hex': claim_scope_ref['sha256_hex'],
        },
        'current_reliance_card': {
            'path': reliance_card_ref['path'],
            'sha256_hex': reliance_card_ref['sha256_hex'],
        },
        'discovery_links': links,
        'package_head_summary': 'Package head points at the current authoritative package manifest, its lineage record, one compact status card, one compact verification report, one compact claim-scope object, and one compact reliance card so future stewards can discover the live package root, its citable posture, what validation actually ran here, which downstream claims that validation supports, and what they may safely rely on without replaying the full chain.',
    }
    validate_package_head(package_head)
    return package_head

def make_package_redirect(
    *,
    prior_manifest_path: str | Path,
    supersession_path: str | Path,
    current_head_path: str | Path,
    current_status_card_path: str | Path,
) -> dict[str, Any]:
    prior_manifest_path = Path(prior_manifest_path)
    supersession_path = Path(supersession_path)
    current_head_path = Path(current_head_path)
    current_status_card_path = Path(current_status_card_path)

    prior_manifest = load_json(prior_manifest_path)
    supersession = load_json(supersession_path)
    current_head = load_json(current_head_path)
    current_status_card = load_json(current_status_card_path)

    validate_package_manifest(prior_manifest)
    validate_package_supersession(supersession)
    validate_package_head(current_head)
    validate_package_status_card(current_status_card)

    receipt_id = prior_manifest['receipt_id']
    journey_kind = prior_manifest['journey_kind']
    if supersession['receipt_id'] != receipt_id or current_head['receipt_id'] != receipt_id or current_status_card['receipt_id'] != receipt_id:
        raise ValueError('package redirect inputs must point at the same receipt id')
    if supersession['journey_kind'] != journey_kind or current_head['journey_kind'] != journey_kind or current_status_card['journey_kind'] != journey_kind:
        raise ValueError('package redirect inputs must point at the same journey kind')

    prior_manifest_ref = _json_file_reference(prior_manifest_path, prior_manifest)
    supersession_ref = _sha256_file_reference(supersession_path)
    current_head_ref = _sha256_file_reference(current_head_path)
    current_status_card_ref = _sha256_file_reference(current_status_card_path)

    if supersession['prior_package_manifest']['path'] != prior_manifest_ref['path']:
        raise ValueError('package redirect prior manifest must match the supersession prior manifest path')
    if supersession['prior_package_manifest']['sha256_hex'] != prior_manifest_ref['sha256_hex']:
        raise ValueError('package redirect prior manifest sha256 must match the supersession prior manifest sha256')

    successor_manifest = supersession['current_package_manifest']
    if current_head['authoritative_manifest']['path'] != successor_manifest['path']:
        raise ValueError('package redirect requires the current head authoritative manifest to match the supersession current manifest path')
    if current_head['authoritative_manifest']['sha256_hex'] != successor_manifest['sha256_hex']:
        raise ValueError('package redirect requires the current head authoritative manifest sha256 to match the supersession current manifest sha256')
    if current_status_card['authoritative_manifest']['path'] != successor_manifest['path']:
        raise ValueError('package redirect requires the current status card authoritative manifest to match the supersession current manifest path')
    if current_status_card['authoritative_manifest']['sha256_hex'] != successor_manifest['sha256_hex']:
        raise ValueError('package redirect requires the current status card authoritative manifest sha256 to match the supersession current manifest sha256')
    if current_status_card['current_review_state']['review_decision'] != current_head['current_package_state']['review_decision']:
        raise ValueError('package redirect current status card review decision must match the current head package state')
    if current_status_card['citation_guidance']['advisory_decision'] != current_head['current_package_state']['advisory_decision']:
        raise ValueError('package redirect current status card advisory decision must match the current head package state')

    preferred_reference_action = (
        'use_current_package_head_for_package_reference'
        if current_status_card['currently_citable']
        else 'consult_current_package_head_before_reuse'
    )

    redirect = {
        'schema_version': 1,
        'package_redirect_kind': 'successor_safe_ceremony_receipt_package_redirect',
        'receipt_id': receipt_id,
        'journey_kind': journey_kind,
        'source_package_manifest': {
            'path': prior_manifest_ref['path'],
            'sha256_hex': prior_manifest_ref['sha256_hex'],
            'current_claim_status': prior_manifest['current_claim_status'],
        },
        'preferred_reference_target': {
            'target_kind': 'package_head',
            'path': current_head_ref['path'],
            'sha256_hex': current_head_ref['sha256_hex'],
            'reference_action': preferred_reference_action,
        },
        'successor_package_manifest': successor_manifest,
        'supporting_status_card': {
            'path': current_status_card_ref['path'],
            'sha256_hex': current_status_card_ref['sha256_hex'],
            'currently_citable': current_status_card['currently_citable'],
        },
        'redirect_basis': {
            'supersession_path': supersession_ref['path'],
            'supersession_sha256_hex': supersession_ref['sha256_hex'],
            'continuity': supersession['active_receipt_locator_continuity']['continuity'],
            'supersession_reason_codes': supersession['supersession_reason_codes'],
            'current_review_decision': current_status_card['current_review_state']['review_decision'],
            'current_advisory_decision': current_status_card['citation_guidance']['advisory_decision'],
        },
        'ceremony_locator_guidance': {
            'preferred_locator_digest_hex': current_status_card['active_receipt_locator_digest_hex'],
            'existing_citations_action': current_status_card['citation_guidance']['existing_citations_action'],
            'new_citations_action': current_status_card['citation_guidance']['new_citations_action'],
        },
        'redirect_links': [
            {
                'rel': 'cite-as',
                'target_kind': 'package_head',
                'path': current_head_ref['path'],
                'sha256_hex': current_head_ref['sha256_hex'],
            },
            {
                'rel': 'successor-version',
                'target_kind': 'package_manifest',
                'path': successor_manifest['path'],
                'sha256_hex': successor_manifest['sha256_hex'],
            },
            {
                'rel': 'latest-version',
                'target_kind': 'package_manifest',
                'path': successor_manifest['path'],
                'sha256_hex': successor_manifest['sha256_hex'],
            },
            {
                'rel': 'status',
                'target_kind': 'package_status_card',
                'path': current_status_card_ref['path'],
                'sha256_hex': current_status_card_ref['sha256_hex'],
            },
            {
                'rel': 'describedby',
                'target_kind': 'package_supersession',
                'path': supersession_ref['path'],
                'sha256_hex': supersession_ref['sha256_hex'],
            },
        ],
        'redirect_summary': (
            'Package redirect lets a steward who lands on a superseded package manifest discover the preferred current package-reference target, the successor package manifest, and the live package status card without replaying the full lineage.'
            if current_status_card['currently_citable']
            else 'Package redirect lets a steward who lands on a superseded package manifest discover the current package head and live package status card even when claim-ready citation is presently suspended, so replacement and regeneration decisions come from one compact redirect object instead of local guesswork.'
        ),
    }
    validate_package_redirect(redirect)
    return redirect


def make_package_catalog(
    *,
    head_paths: list[str | Path],
    redirect_paths: list[str | Path] | None = None,
) -> dict[str, Any]:
    if not head_paths:
        raise ValueError('package catalog requires at least one package head')

    redirect_paths = redirect_paths or []
    family_entries: list[dict[str, Any]] = []
    heads_by_receipt: dict[str, dict[str, Any]] = {}

    for head_path in head_paths:
        head_path = Path(head_path)
        head = load_json(head_path)
        validate_package_head(head)

        status_card_path = ROOT / head['current_status_card']['path']
        lineage_path = ROOT / head['package_lineage']['path']
        reliance_card_path = ROOT / head['current_reliance_card']['path']
        status_card = load_json(status_card_path)
        lineage = load_json(lineage_path)
        reliance_card = load_json(reliance_card_path)
        validate_package_status_card(status_card)
        validate_package_lineage(lineage)
        validate_package_reliance_card(reliance_card)

        if status_card['receipt_id'] != head['receipt_id'] or lineage['receipt_id'] != head['receipt_id'] or reliance_card['receipt_id'] != head['receipt_id']:
            raise ValueError('package catalog head inputs must agree on receipt id')
        if status_card['journey_kind'] != head['journey_kind'] or lineage['journey_kind'] != head['journey_kind'] or reliance_card['journey_kind'] != head['journey_kind']:
            raise ValueError('package catalog head inputs must agree on journey kind')
        if status_card['authoritative_manifest']['path'] != head['authoritative_manifest']['path']:
            raise ValueError('package catalog status card authoritative manifest must match the package head authoritative manifest path')
        if status_card['authoritative_manifest']['sha256_hex'] != head['authoritative_manifest']['sha256_hex']:
            raise ValueError('package catalog status card authoritative manifest sha256 must match the package head authoritative manifest sha256')
        if lineage['authoritative_manifest']['path'] != head['authoritative_manifest']['path']:
            raise ValueError('package catalog lineage authoritative manifest must match the package head authoritative manifest path')
        if lineage['authoritative_manifest']['sha256_hex'] != head['authoritative_manifest']['sha256_hex']:
            raise ValueError('package catalog lineage authoritative manifest sha256 must match the package head authoritative manifest sha256')

        head_ref = _sha256_file_reference(head_path)
        status_card_ref = _sha256_file_reference(status_card_path)
        lineage_ref = _sha256_file_reference(lineage_path)
        reliance_card_ref = _sha256_file_reference(reliance_card_path)
        if reliance_card['authoritative_manifest']['path'] != head['authoritative_manifest']['path']:
            raise ValueError('package catalog reliance card authoritative manifest must match the package head authoritative manifest path')
        if reliance_card['authoritative_manifest']['sha256_hex'] != head['authoritative_manifest']['sha256_hex']:
            raise ValueError('package catalog reliance card authoritative manifest sha256 must match the package head authoritative manifest sha256')

        family_entry = {
            'family_key': head['receipt_id'],
            'receipt_id': head['receipt_id'],
            'journey_kind': head['journey_kind'],
            'current_package_head': head_ref,
            'current_package_status_card': {
                'path': status_card_ref['path'],
                'sha256_hex': status_card_ref['sha256_hex'],
                'currently_citable': status_card['currently_citable'],
            },
            'current_package_reliance_card': {
                'path': reliance_card_ref['path'],
                'sha256_hex': reliance_card_ref['sha256_hex'],
                'reliance_decision': reliance_card['reliance_decision'],
            },
            'authoritative_manifest': head['authoritative_manifest'],
            'package_lineage': {
                'path': lineage_ref['path'],
                'sha256_hex': lineage_ref['sha256_hex'],
                'chain_length': len(lineage['manifest_chain']),
            },
            'active_receipt_locator_digest_hex': head['active_receipt_locator_digest_hex'],
            'current_citation_state': 'citable_now' if status_card['currently_citable'] else 'suspended_pending_regeneration',
            'superseded_redirect_count': 0,
            'member_links': [
                {
                    'rel': 'item',
                    'target_kind': 'package_head',
                    'path': head_ref['path'],
                    'sha256_hex': head_ref['sha256_hex'],
                },
                {
                    'rel': 'latest-version',
                    'target_kind': 'package_manifest',
                    'path': head['authoritative_manifest']['path'],
                    'sha256_hex': head['authoritative_manifest']['sha256_hex'],
                },
                {
                    'rel': 'version-history',
                    'target_kind': 'package_lineage',
                    'path': lineage_ref['path'],
                    'sha256_hex': lineage_ref['sha256_hex'],
                },
                {
                    'rel': 'status',
                    'target_kind': 'package_status_card',
                    'path': status_card_ref['path'],
                    'sha256_hex': status_card_ref['sha256_hex'],
                },
                {
                    'rel': 'describedby',
                    'target_kind': 'package_reliance_card',
                    'path': reliance_card_ref['path'],
                    'sha256_hex': reliance_card_ref['sha256_hex'],
                },
            ],
        }
        family_entries.append(family_entry)
        heads_by_receipt[head['receipt_id']] = family_entry

    redirect_entries: list[dict[str, Any]] = []
    for redirect_path in redirect_paths:
        redirect_path = Path(redirect_path)
        redirect = load_json(redirect_path)
        validate_package_redirect(redirect)
        redirect_ref = _sha256_file_reference(redirect_path)

        family_entry = heads_by_receipt.get(redirect['receipt_id'])
        if family_entry is None:
            raise ValueError('package catalog redirect receipt id must match one of the package heads')
        if family_entry['authoritative_manifest']['path'] != redirect['successor_package_manifest']['path']:
            raise ValueError('package catalog redirect successor manifest must match the current authoritative manifest for that receipt')
        if family_entry['authoritative_manifest']['sha256_hex'] != redirect['successor_package_manifest']['sha256_hex']:
            raise ValueError('package catalog redirect successor manifest sha256 must match the current authoritative manifest sha256 for that receipt')

        family_entry['superseded_redirect_count'] += 1
        redirect_entries.append({
            'receipt_id': redirect['receipt_id'],
            'journey_kind': redirect['journey_kind'],
            'source_package_manifest': redirect['source_package_manifest'],
            'redirect_artifact': redirect_ref,
            'successor_package_manifest': redirect['successor_package_manifest'],
            'current_status': 'claim_ready_citable' if redirect['supporting_status_card']['currently_citable'] else 'suspended_pending_regeneration',
            'reference_action': redirect['preferred_reference_target']['reference_action'],
        })

    family_entries.sort(key=lambda row: (row['receipt_id'], row['current_package_head']['path']))
    redirect_entries.sort(key=lambda row: (row['receipt_id'], row['source_package_manifest']['path']))

    package_catalog = {
        'schema_version': 1,
        'package_catalog_kind': 'successor_safe_ceremony_receipt_package_catalog',
        'catalog_id': 'successor-safe-ceremony-receipt-packages',
        'catalog_summary': {
            'package_family_count': len(family_entries),
            'authoritative_head_count': len(family_entries),
            'superseded_redirect_count': len(redirect_entries),
        },
        'package_families': family_entries,
        'superseded_package_redirects': redirect_entries,
        'catalog_links': [
            {
                'rel': 'item',
                'target_kind': 'package_head',
                'path': row['current_package_head']['path'],
                'sha256_hex': row['current_package_head']['sha256_hex'],
            }
            for row in family_entries
        ],
        'catalog_purpose': 'Package catalog gives future stewards one compact archive entry point listing the current authoritative package head for each retained successor-safe ceremony receipt family plus any superseded-package redirects, so they do not need to browse individual lineage and redirect files just to discover what package roots exist and which one is live now.',
    }
    validate_package_catalog(package_catalog)
    return package_catalog

def write_json(path: Path, obj: dict[str, Any]) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def cmd_scaffold(args: argparse.Namespace) -> int:
    receipt = scaffold_receipt(receipt_id=args.id, journey_kind=args.journey_kind)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_json(out, receipt)
    print(f"successor-safe-ceremony-receipt: wrote scaffold to {out}")
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    path = Path(args.input)
    receipt = load_json(path)
    validate_receipt(receipt)
    rendered = render_markdown(receipt)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(rendered, encoding="utf-8")
    print(f"successor-safe-ceremony-receipt: wrote markdown to {out}")
    return 0


def cmd_locate(args: argparse.Namespace) -> int:
    path = Path(args.input)
    receipt = load_json(path)
    locator = make_locator(receipt, source_path=args.source_path or path.as_posix())
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_json(out, locator)
    print(f"successor-safe-ceremony-receipt: wrote locator to {out}")
    return 0


def cmd_assess(args: argparse.Namespace) -> int:
    path = Path(args.input)
    receipt = load_json(path)
    assessment = assess_receipt(receipt, source_path=args.source_path or path.as_posix())
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_json(out, assessment)
    print(f"successor-safe-ceremony-receipt: wrote assessment to {out}")
    return 0


def cmd_disposition(args: argparse.Namespace) -> int:
    assessment = load_json(Path(args.assessment))
    locator = load_json(Path(args.locator))
    disposition = make_disposition(assessment, locator)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_json(out, disposition)
    print(f"successor-safe-ceremony-receipt: wrote disposition to {out}")
    return 0


def cmd_remediation(args: argparse.Namespace) -> int:
    assessment = load_json(Path(args.assessment))
    locator = load_json(Path(args.locator))
    disposition = load_json(Path(args.disposition))
    plan = make_remediation_plan(assessment, locator, disposition)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_json(out, plan)
    print(f"successor-safe-ceremony-receipt: wrote remediation plan to {out}")
    return 0


def cmd_authorize(args: argparse.Namespace) -> int:
    assessment = load_json(Path(args.assessment))
    locator = load_json(Path(args.locator))
    disposition = load_json(Path(args.disposition))
    plan = load_json(Path(args.remediation))
    authorization = make_authorization(assessment, locator, disposition, plan)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_json(out, authorization)
    print(f"successor-safe-ceremony-receipt: wrote authorization to {out}")
    return 0


def cmd_promote(args: argparse.Namespace) -> int:
    prior_assessment = load_json(Path(args.prior_assessment))
    prior_locator = load_json(Path(args.prior_locator))
    prior_authorization = load_json(Path(args.prior_authorization))
    current_assessment = load_json(Path(args.current_assessment))
    current_locator = load_json(Path(args.current_locator))
    current_authorization = load_json(Path(args.current_authorization))
    promotion = make_promotion(prior_assessment, prior_locator, prior_authorization, current_assessment, current_locator, current_authorization)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_json(out, promotion)
    print(f"successor-safe-ceremony-receipt: wrote promotion to {out}")
    return 0


def cmd_watch(args: argparse.Namespace) -> int:
    authorization = load_json(Path(args.authorization))
    promotion = load_json(Path(args.promotion))
    review_watch = make_review_watch(authorization, promotion, reviewed_on=args.reviewed_on, max_review_interval_days=args.max_review_interval_days)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_json(out, review_watch)
    print(f"successor-safe-ceremony-receipt: wrote review watch to {out}")
    return 0


def cmd_review(args: argparse.Namespace) -> int:
    review_watch = load_json(Path(args.review_watch))
    verdict = make_review_verdict(review_watch, as_of=args.as_of, observed_trigger_codes=args.trigger)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_json(out, verdict)
    print(f"successor-safe-ceremony-receipt: wrote review verdict to {out}")
    return 0


def cmd_advise(args: argparse.Namespace) -> int:
    review_verdict = load_json(Path(args.review_verdict))
    advisory = make_citation_advisory(review_verdict)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_json(out, advisory)
    print(f"successor-safe-ceremony-receipt: wrote citation advisory to {out}")
    return 0


def cmd_manifest(args: argparse.Namespace) -> int:
    manifest = make_package_manifest(
        receipt_path=args.receipt,
        rendered_markdown_path=args.rendered_markdown,
        locator_path=args.locator,
        assessment_path=args.assessment,
        disposition_path=args.disposition,
        remediation_path=args.remediation,
        authorization_path=args.authorization,
        promotion_path=args.promotion,
        review_watch_path=args.review_watch,
        review_verdict_path=args.review_verdict,
        citation_advisory_path=args.citation_advisory,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_json(out, manifest)
    print(f"successor-safe-ceremony-receipt: wrote package manifest to {out}")
    return 0


def cmd_supersede(args: argparse.Namespace) -> int:
    package_supersession = make_package_supersession(
        prior_manifest_path=args.prior_manifest,
        current_manifest_path=args.current_manifest,
        prior_review_watch_path=args.prior_review_watch,
        current_review_watch_path=args.current_review_watch,
        prior_review_verdict_path=args.prior_review_verdict,
        current_review_verdict_path=args.current_review_verdict,
        prior_citation_advisory_path=args.prior_citation_advisory,
        current_citation_advisory_path=args.current_citation_advisory,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_json(out, package_supersession)
    print(f"successor-safe-ceremony-receipt: wrote package supersession to {out}")
    return 0


def cmd_lineage(args: argparse.Namespace) -> int:
    package_lineage = make_package_lineage(
        manifest_paths=args.manifest,
        supersession_paths=args.supersession,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_json(out, package_lineage)
    print(f"successor-safe-ceremony-receipt: wrote package lineage to {out}")
    return 0


def cmd_statuscard(args: argparse.Namespace) -> int:
    package_status_card = make_package_status_card(
        manifest_path=args.manifest,
        review_watch_path=args.review_watch,
        review_verdict_path=args.review_verdict,
        citation_advisory_path=args.citation_advisory,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_json(out, package_status_card)
    print(f"successor-safe-ceremony-receipt: wrote package status card to {out}")
    return 0


def cmd_verifyreport(args: argparse.Namespace) -> int:
    package_verification_report = make_package_verification_report(
        manifest_path=args.manifest,
        status_card_path=args.status_card,
        as_of=args.as_of,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_json(out, package_verification_report)
    print(f"successor-safe-ceremony-receipt: wrote package verification report to {out}")
    return 0


def cmd_claimscope(args: argparse.Namespace) -> int:
    package_claim_scope = make_package_claim_scope(
        manifest_path=args.manifest,
        status_card_path=args.status_card,
        verification_report_path=args.verification_report,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_json(out, package_claim_scope)
    print(f"successor-safe-ceremony-receipt: wrote package claim scope to {out}")
    return 0


def cmd_head(args: argparse.Namespace) -> int:
    package_head = make_package_head(
        manifest_path=args.manifest,
        lineage_path=args.lineage,
        review_verdict_path=args.review_verdict,
        citation_advisory_path=args.citation_advisory,
        status_card_path=args.status_card,
        verification_report_path=args.verification_report,
        claim_scope_path=args.claim_scope,
        reliance_card_path=args.reliance_card,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_json(out, package_head)
    print(f"successor-safe-ceremony-receipt: wrote package head to {out}")
    return 0



def cmd_redirect(args: argparse.Namespace) -> int:
    package_redirect = make_package_redirect(
        prior_manifest_path=args.prior_manifest,
        supersession_path=args.supersession,
        current_head_path=args.current_head,
        current_status_card_path=args.current_status_card,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_json(out, package_redirect)
    print(f"successor-safe-ceremony-receipt: wrote package redirect to {out}")
    return 0

def cmd_catalog(args: argparse.Namespace) -> int:
    package_catalog = make_package_catalog(
        head_paths=args.head,
        redirect_paths=args.redirect,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_json(out, package_catalog)
    print(f"successor-safe-ceremony-receipt: wrote package catalog to {out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scaffold or render a compact successor-safe ceremony receipt.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_scaffold = sub.add_parser("scaffold", help="create a scaffold receipt")
    p_scaffold.add_argument("--id", required=True)
    p_scaffold.add_argument(
        "--journey-kind",
        required=True,
        choices=["presentation", "authorization", "authentication", "issuance", "other"],
    )
    p_scaffold.add_argument("--output", required=True)
    p_scaffold.set_defaults(func=cmd_scaffold)

    p_render = sub.add_parser("render", help="render a receipt as markdown")
    p_render.add_argument("input")
    p_render.add_argument("--output", required=True)
    p_render.set_defaults(func=cmd_render)

    p_locate = sub.add_parser("locate", help="emit a compact content-addressed locator for a receipt")
    p_locate.add_argument("input")
    p_locate.add_argument("--output", required=True)
    p_locate.add_argument("--source-path", default="")
    p_locate.set_defaults(func=cmd_locate)

    p_assess = sub.add_parser('assess', help='emit a compact assessment report for a receipt')
    p_assess.add_argument('input')
    p_assess.add_argument('--output', required=True)
    p_assess.add_argument('--source-path', default='')
    p_assess.set_defaults(func=cmd_assess)

    p_disposition = sub.add_parser('disposition', help='emit archive handling guidance from a receipt assessment + locator')
    p_disposition.add_argument('assessment')
    p_disposition.add_argument('locator')
    p_disposition.add_argument('--output', required=True)
    p_disposition.set_defaults(func=cmd_disposition)

    p_remediation = sub.add_parser('remediation', help='emit a compact remediation plan from a receipt assessment + locator + disposition')
    p_remediation.add_argument('assessment')
    p_remediation.add_argument('locator')
    p_remediation.add_argument('disposition')
    p_remediation.add_argument('--output', required=True)
    p_remediation.set_defaults(func=cmd_remediation)

    p_authorize = sub.add_parser('authorize', help='emit an explicit claim-ready authorization decision from a receipt package')
    p_authorize.add_argument('assessment')
    p_authorize.add_argument('locator')
    p_authorize.add_argument('disposition')
    p_authorize.add_argument('remediation')
    p_authorize.add_argument('--output', required=True)
    p_authorize.set_defaults(func=cmd_authorize)

    p_promote = sub.add_parser('promote', help='emit a compact promotion record that explains why a receipt became claim-ready or did not')
    p_promote.add_argument('prior_assessment')
    p_promote.add_argument('prior_locator')
    p_promote.add_argument('prior_authorization')
    p_promote.add_argument('current_assessment')
    p_promote.add_argument('current_locator')
    p_promote.add_argument('current_authorization')
    p_promote.add_argument('--output', required=True)
    p_promote.set_defaults(func=cmd_promote)

    p_watch = sub.add_parser('watch', help='emit a compact freshness / review watch for a claim-ready receipt package')
    p_watch.add_argument('authorization')
    p_watch.add_argument('promotion')
    p_watch.add_argument('--reviewed-on', required=True)
    p_watch.add_argument('--max-review-interval-days', type=int, default=180)
    p_watch.add_argument('--output', required=True)
    p_watch.set_defaults(func=cmd_watch)

    p_review = sub.add_parser('review', help='evaluate a compact review watch into an explicit keep-citing versus reopen-now verdict')
    p_review.add_argument('review_watch')
    p_review.add_argument('--as-of', required=True)
    p_review.add_argument('--trigger', action='append', default=[])
    p_review.add_argument('--output', required=True)
    p_review.set_defaults(func=cmd_review)

    p_advise = sub.add_parser('advise', help='collapse a review verdict into one downstream citation advisory')
    p_advise.add_argument('review_verdict')
    p_advise.add_argument('--output', required=True)
    p_advise.set_defaults(func=cmd_advise)

    p_manifest = sub.add_parser('manifest', help='emit a compact package manifest naming the authoritative receipt artifacts and their file fixity')
    p_manifest.add_argument('--receipt', required=True)
    p_manifest.add_argument('--rendered-markdown', required=True)
    p_manifest.add_argument('--locator', required=True)
    p_manifest.add_argument('--assessment', required=True)
    p_manifest.add_argument('--disposition', required=True)
    p_manifest.add_argument('--remediation', required=True)
    p_manifest.add_argument('--authorization', required=True)
    p_manifest.add_argument('--promotion', required=True)
    p_manifest.add_argument('--review-watch', required=True)
    p_manifest.add_argument('--review-verdict', required=True)
    p_manifest.add_argument('--citation-advisory', required=True)
    p_manifest.add_argument('--output', required=True)
    p_manifest.set_defaults(func=cmd_manifest)

    p_supersede = sub.add_parser('supersede', help='emit a compact supersession record that names which package manifest replaced an older one')
    p_supersede.add_argument('--prior-manifest', required=True)
    p_supersede.add_argument('--current-manifest', required=True)
    p_supersede.add_argument('--prior-review-watch', required=True)
    p_supersede.add_argument('--current-review-watch', required=True)
    p_supersede.add_argument('--prior-review-verdict', required=True)
    p_supersede.add_argument('--current-review-verdict', required=True)
    p_supersede.add_argument('--prior-citation-advisory', required=True)
    p_supersede.add_argument('--current-citation-advisory', required=True)
    p_supersede.add_argument('--output', required=True)
    p_supersede.set_defaults(func=cmd_supersede)

    p_lineage = sub.add_parser('lineage', help='emit a compact lineage record naming the authoritative package head and its supersession chain')
    p_lineage.add_argument('--manifest', action='append', required=True)
    p_lineage.add_argument('--supersession', action='append', default=[])
    p_lineage.add_argument('--output', required=True)
    p_lineage.set_defaults(func=cmd_lineage)

    p_statuscard = sub.add_parser('statuscard', help='emit a compact status card summarizing whether the current package head remains citable, until when, and what would reopen it')
    p_statuscard.add_argument('--manifest', required=True)
    p_statuscard.add_argument('--review-watch', required=True)
    p_statuscard.add_argument('--review-verdict', required=True)
    p_statuscard.add_argument('--citation-advisory', required=True)
    p_statuscard.add_argument('--output', required=True)
    p_statuscard.set_defaults(func=cmd_statuscard)

    p_verifyreport = sub.add_parser('verifyreport', help='emit a compact verification report recording which local validation checks ran for the current package and where the environment boundary stopped')
    p_verifyreport.add_argument('--manifest', required=True)
    p_verifyreport.add_argument('--status-card', required=True)
    p_verifyreport.add_argument('--as-of', required=True)
    p_verifyreport.add_argument('--output', required=True)
    p_verifyreport.set_defaults(func=cmd_verifyreport)

    p_claimscope = sub.add_parser('claimscope', help='emit a compact downstream claim-scope object describing what the current package verification basis actually supports')
    p_claimscope.add_argument('--manifest', required=True)
    p_claimscope.add_argument('--status-card', required=True)
    p_claimscope.add_argument('--verification-report', required=True)
    p_claimscope.add_argument('--output', required=True)
    p_claimscope.set_defaults(func=cmd_claimscope)

    p_reliancecard = sub.add_parser('reliancecard', help='emit a compact downstream reliance card summarizing the live citable posture, verification basis, and safe claim boundary for the current package')
    p_reliancecard.add_argument('--manifest', required=True)
    p_reliancecard.add_argument('--status-card', required=True)
    p_reliancecard.add_argument('--verification-report', required=True)
    p_reliancecard.add_argument('--claim-scope', required=True)
    p_reliancecard.add_argument('--output', required=True)
    p_reliancecard.set_defaults(func=cmd_reliancecard)

    p_head = sub.add_parser('head', help='emit a compact authority pointer naming the current authoritative package root and where to discover its status and history')
    p_head.add_argument('--manifest', required=True)
    p_head.add_argument('--lineage', required=True)
    p_head.add_argument('--review-verdict', required=True)
    p_head.add_argument('--citation-advisory', required=True)
    p_head.add_argument('--status-card', required=True)
    p_head.add_argument('--verification-report', required=True)
    p_head.add_argument('--claim-scope', required=True)
    p_head.add_argument('--reliance-card', required=True)
    p_head.add_argument('--output', required=True)
    p_head.set_defaults(func=cmd_head)

    p_redirect = sub.add_parser('redirect', help='emit a compact redirect for a superseded package manifest that points future stewards at the preferred current package-reference target and live status')
    p_redirect.add_argument('--prior-manifest', required=True)
    p_redirect.add_argument('--supersession', required=True)
    p_redirect.add_argument('--current-head', required=True)
    p_redirect.add_argument('--current-status-card', required=True)
    p_redirect.add_argument('--output', required=True)
    p_redirect.set_defaults(func=cmd_redirect)

    p_catalog = sub.add_parser('catalog', help='emit a compact archive catalog listing current package heads and any superseded package redirects')
    p_catalog.add_argument('--head', action='append', required=True)
    p_catalog.add_argument('--redirect', action='append', default=[])
    p_catalog.add_argument('--output', required=True)
    p_catalog.set_defaults(func=cmd_catalog)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
