"""Rev0023 access/publication-office validation facet.

Checks audience roles, publication tiers, permissions, misuse threats, minimization gates, export/media rules,
law-enforcement boundaries, denial reasons, receipt templates, fixtures, and refactor audits while `make lint` remains the stable entrypoint.
"""
from __future__ import annotations
from pathlib import Path
import json


def load(root: Path, rel: str):
    return json.loads((root / rel).read_text(encoding='utf-8'))


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    roles = load(root, 'data/access/rev0023_audience_roles.json').get('roles', [])
    tiers = load(root, 'data/access/rev0023_publication_tiers.json').get('publication_tiers', [])
    routes = load(root, 'data/access/rev0023_source_family_access_routes.json').get('routes', [])
    perms = load(root, 'data/access/rev0023_role_feature_permission_matrix.json').get('rows', [])
    gates = load(root, 'data/access/rev0023_data_minimization_gates.json').get('gates', [])
    threats = load(root, 'data/access/rev0023_misuse_threat_model.json').get('threats', [])
    bulk = load(root, 'data/access/rev0023_bulk_export_gates.json').get('gates', [])
    media = load(root, 'data/access/rev0023_sensitive_media_rules.json').get('rules', [])
    le = load(root, 'data/access/rev0023_law_enforcement_access_boundaries.json').get('boundaries', [])
    denials = load(root, 'data/access/rev0023_publication_denial_reasons.json').get('denial_reasons', [])
    receipts = load(root, 'data/access/rev0023_access_decision_receipt_templates.json').get('templates', [])
    fixtures = load(root, 'data/access/rev0023_synthetic_access_fixtures.json').get('fixtures', [])
    expected = [(roles,18,'audience roles'),(tiers,14,'publication tiers'),(routes,24,'source-family access routes'),(perms,288,'role-feature permission rows'),(gates,22,'data-minimization gates'),(threats,20,'misuse threats'),(bulk,16,'bulk export gates'),(media,14,'sensitive-media rules'),(le,14,'law-enforcement boundaries'),(denials,16,'publication denial reasons'),(receipts,12,'access decision receipt templates'),(fixtures,15,'synthetic access fixtures')]
    for arr, count, label in expected:
        if len(arr) != count:
            errors.append(f'rev0023 expected {count} {label}, found {len(arr)}')
    role_ids = {r.get('audience_role_id') for r in roles}
    role_keys = {r.get('role_key') for r in roles}
    tier_keys = {t.get('tier_key') for t in tiers}
    family_ids = {f.get('source_family_id') for f in load(root, 'data/source_families/rev0019_source_family_atlas.json').get('source_families', [])}
    for r in roles:
        if r.get('can_receive_raw_person_level_payloads_by_default_rev0023') is not False:
            errors.append(f"rev0023 role {r.get('audience_role_id')} can receive raw person payloads by default")
        if r.get('can_create_public_claims_by_role_rev0023') is not False:
            errors.append(f"rev0023 role {r.get('audience_role_id')} can create public claims")
        if r.get('public_claims_admitted_rev0023') != 0 or r.get('live_records_created_rev0023') != 0:
            errors.append(f"rev0023 role {r.get('audience_role_id')} admits claims or live records")
    if 'law_enforcement_agency_employer' not in role_keys or 'commercial_data_broker' not in role_keys:
        errors.append('rev0023 access roles must include law_enforcement_agency_employer and commercial_data_broker')
    for t in tiers:
        if t.get('requires_decision_receipt_before_publication') is not True:
            errors.append(f"rev0023 publication tier {t.get('publication_tier_id')} missing decision receipt requirement")
        if t.get('live_data_enabled_rev0023') is not False or t.get('public_claims_admitted_rev0023') != 0:
            errors.append(f"rev0023 publication tier {t.get('publication_tier_id')} enables live data or claims")
    for row in routes:
        if row.get('source_family_id') not in family_ids:
            errors.append(f"rev0023 access route {row.get('source_family_access_route_id')} references unknown source family")
        if row.get('default_publication_tier_key') not in tier_keys:
            errors.append(f"rev0023 access route {row.get('source_family_access_route_id')} references unknown publication tier")
        if row.get('live_data_allowed_rev0023') is not False or row.get('public_claims_admitted_rev0023') != 0:
            errors.append(f"rev0023 access route {row.get('source_family_access_route_id')} opens live data or claims")
    for row in perms:
        if row.get('audience_role_id') not in role_ids:
            errors.append(f"rev0023 permission {row.get('permission_row_id')} references unknown role")
        if row.get('raw_payload_access_enabled_rev0023') is not False or row.get('sensitive_media_access_enabled_rev0023') is not False or row.get('live_data_access_enabled_rev0023') is not False:
            errors.append(f"rev0023 permission {row.get('permission_row_id')} enables access")
        if row.get('public_claims_admitted_rev0023') != 0:
            errors.append(f"rev0023 permission {row.get('permission_row_id')} admits public claims")
    for collection, id_key in [(gates,'minimization_gate_id'),(threats,'misuse_threat_id'),(bulk,'bulk_export_gate_id'),(media,'sensitive_media_rule_id'),(le,'law_enforcement_boundary_id'),(denials,'publication_denial_reason_id'),(receipts,'access_decision_receipt_template_id')]:
        for row in collection:
            if row.get('public_claims_admitted_rev0023', 0) != 0 or row.get('live_records_created_rev0023', 0) != 0:
                errors.append(f"rev0023 row {row.get(id_key)} admits claims or live records")
    for row in bulk:
        if row.get('can_release_person_level_adverse_data_rev0023') is not False or row.get('can_release_raw_payload_rev0023') is not False or row.get('can_release_sensitive_media_rev0023') is not False:
            errors.append(f"rev0023 bulk gate {row.get('bulk_export_gate_id')} releases prohibited data")
    for row in media:
        if row.get('raw_payload_release_enabled_rev0023') is not False:
            errors.append(f"rev0023 media rule {row.get('sensitive_media_rule_id')} enables raw release")
    for row in le:
        if row.get('special_access_granted_rev0023') is not False:
            errors.append(f"rev0023 LE boundary {row.get('law_enforcement_boundary_id')} grants special access")
    for fx in fixtures:
        if fx.get('uses_live_people_or_real_incidents') is not False or fx.get('uses_live_source_payload') is not False:
            errors.append(f"rev0023 fixture {fx.get('fixture_id')} uses live data")
    return errors
