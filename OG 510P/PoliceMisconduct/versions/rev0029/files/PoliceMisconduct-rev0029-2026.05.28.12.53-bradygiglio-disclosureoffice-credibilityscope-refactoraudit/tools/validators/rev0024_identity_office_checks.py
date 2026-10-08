#!/usr/bin/env python3
from pathlib import Path
import json

REQUIRED = [
    'IDENTITY-RESOLUTION-KERNEL.json', 'IDENTITY-SIGNAL-TAXONOMY.json', 'MERGE-ABSTENTION-LEDGER.json',
    'UNMERGE-RECEIPT-GRAMMAR.json', 'IDENTITY-RISK-TIER-LEDGER.json', 'IDENTITY-PUBLIC-DISPLAY-GATE.json',
    'ALIAS-AND-IDENTIFIER-HANDLING-LEDGER.json', 'SOURCE-FAMILY-IDENTITY-ROUTING-LEDGER.json',
    'SYNTHETIC-IDENTITY-FIXTURE-LEDGER.json', 'IDENTITY-DECISION-RECEIPT-GRAMMAR.json',
    'data/identity/rev0024_entity_classes.json', 'data/identity/rev0024_identifier_types.json',
    'data/identity/rev0024_identity_signal_taxonomy.json', 'data/identity/rev0024_merge_state_machine.json',
    'data/identity/rev0024_merge_abstention_rules.json', 'data/identity/rev0024_unmerge_receipt_templates.json',
    'data/identity/rev0024_identity_risk_tiers.json', 'data/identity/rev0024_source_family_identity_routes.json',
    'data/identity/rev0024_public_identity_display_gates.json', 'data/identity/rev0024_synthetic_identity_fixtures.json',
    'data/identity/rev0024_identity_decision_receipt_templates.json',
]

def _load(root: Path, rel: str):
    return json.loads((root / rel).read_text(encoding='utf-8'))

def _zero(row, errors, label):
    if row.get('public_claims_admitted_rev0024', 0) != 0:
        errors.append(f'{label} admits public claims')
    if row.get('live_records_created_rev0024', 0) != 0:
        errors.append(f'{label} creates live records')

def validate(root: Path):
    errors = []
    for rel in REQUIRED:
        if not (root / rel).exists():
            errors.append(f'missing rev0024 identity file: {rel}')
    if errors:
        return errors

    entity = _load(root, 'data/identity/rev0024_entity_classes.json')
    entities = entity.get('entity_classes', [])
    if entity.get('entity_class_count') != len(entities) or len(entities) != 18:
        errors.append(f'rev0024 entity class count mismatch: {len(entities)}')
    entity_keys = {r.get('entity_class_key') for r in entities}
    for r in entities:
        _zero(r, errors, f"entity class {r.get('entity_class_id')}")
        if r.get('live_entity_creation_allowed_rev0024') is not False or r.get('canonical_record_creation_allowed_rev0024') is not False:
            errors.append(f"entity class {r.get('entity_class_id')} allows live/canonical creation")

    ident = _load(root, 'data/identity/rev0024_identifier_types.json')
    identifiers = ident.get('identifier_types', [])
    if ident.get('identifier_type_count') != len(identifiers) or len(identifiers) != 30:
        errors.append(f'rev0024 identifier type count mismatch: {len(identifiers)}')
    for r in identifiers:
        _zero(r, errors, f"identifier type {r.get('identifier_type_id')}")
        if r.get('can_support_name_only_merge_rev0024') is not False:
            errors.append(f"identifier type {r.get('identifier_type_id')} supports name-only merge")

    sig = _load(root, 'data/identity/rev0024_identity_signal_taxonomy.json')
    signals = sig.get('identity_signals', [])
    if sig.get('identity_signal_count') != len(signals) or len(signals) != 44:
        errors.append(f'rev0024 identity signal count mismatch: {len(signals)}')
    forbidden_found = False
    for r in signals:
        _zero(r, errors, f"identity signal {r.get('identity_signal_id')}")
        if r.get('can_directly_create_merge_rev0024') is not False or r.get('can_directly_create_public_identity_rev0024') is not False:
            errors.append(f"identity signal {r.get('identity_signal_id')} creates merge/display")
        if r.get('strength_class') == 'forbidden':
            forbidden_found = True
    if not forbidden_found:
        errors.append('rev0024 signal taxonomy lacks explicit forbidden signal')

    sm = _load(root, 'data/identity/rev0024_merge_state_machine.json')
    states = sm.get('states', [])
    transitions = sm.get('transitions', [])
    if sm.get('state_count') != len(states) or len(states) != 24:
        errors.append(f'rev0024 merge state count mismatch: {len(states)}')
    if sm.get('transition_count') != len(transitions) or len(transitions) != 40:
        errors.append(f'rev0024 merge transition count mismatch: {len(transitions)}')
    state_ids = {s.get('identity_state_id') for s in states}
    for s in states:
        _zero(s, errors, f"identity state {s.get('identity_state_id')}")
        if s.get('can_create_live_identity_record_rev0024') is not False or s.get('can_create_public_identity_display_rev0024') is not False:
            errors.append(f"identity state {s.get('identity_state_id')} allows live/display")
    for t in transitions:
        _zero(t, errors, f"identity transition {t.get('identity_transition_id')}")
        if t.get('from_state_id') not in state_ids or t.get('to_state_id') not in state_ids:
            errors.append(f"identity transition {t.get('identity_transition_id')} references unknown state")
        if t.get('creates_live_identity_record_rev0024') is not False or t.get('creates_public_identity_display_rev0024') is not False:
            errors.append(f"identity transition {t.get('identity_transition_id')} creates live/display")

    abst = _load(root, 'data/identity/rev0024_merge_abstention_rules.json')
    rules = abst.get('rules', [])
    if abst.get('abstention_rule_count') != len(rules) or len(rules) != 24:
        errors.append(f'rev0024 abstention rule count mismatch: {len(rules)}')
    if not any(r.get('rule_key') == 'name_only_match' for r in rules):
        errors.append('rev0024 abstention lacks name_only_match rule')
    for r in rules:
        _zero(r, errors, f"abstention rule {r.get('abstention_rule_id')}")
        if r.get('can_be_overridden_without_decision_receipt') is not False:
            errors.append(f"abstention rule {r.get('abstention_rule_id')} can be overridden without receipt")

    for rel, key, count_field, expected in [
        ('data/identity/rev0024_unmerge_receipt_templates.json','templates','template_count',12),
        ('data/identity/rev0024_identity_risk_tiers.json','risk_tiers','tier_count',10),
        ('data/identity/rev0024_public_identity_display_gates.json','gates','gate_count',18),
        ('data/identity/rev0024_identity_decision_receipt_templates.json','templates','template_count',12),
        ('data/identity/rev0024_synthetic_identity_fixtures.json','fixtures','fixture_count',18),
    ]:
        obj = _load(root, rel)
        rows = obj.get(key, [])
        if obj.get(count_field) != len(rows) or len(rows) != expected:
            errors.append(f'rev0024 {rel} count mismatch: {len(rows)} expected {expected}')
        if rel.endswith('public_identity_display_gates.json') and obj.get('public_identity_display_enabled_rev0024') is not False:
            errors.append('rev0024 public identity display gate enables display')
        for row in rows:
            _zero(row, errors, f"{rel} row")
            if rel.endswith('synthetic_identity_fixtures.json') and (row.get('uses_live_people_or_real_incidents') is not False or row.get('uses_live_source_payload') is not False):
                errors.append(f"rev0024 identity fixture {row.get('synthetic_identity_fixture_id')} uses live data")
            if rel.endswith('public_identity_display_gates.json') and row.get('public_display_enabled_rev0024') is not False:
                errors.append(f"rev0024 display gate {row.get('identity_public_display_gate_id')} enables display")
            if rel.endswith('identity_decision_receipt_templates.json') and (row.get('can_create_live_record_by_template_rev0024') is not False or row.get('can_create_public_display_by_template_rev0024') is not False):
                errors.append(f"rev0024 receipt template {row.get('identity_decision_receipt_template_id')} creates live/display")

    routes_obj = _load(root, 'data/identity/rev0024_source_family_identity_routes.json')
    routes = routes_obj.get('routes', [])
    sf_obj = _load(root, 'data/source_families/rev0019_source_family_atlas.json')
    sf_ids = {f.get('source_family_id') for f in sf_obj.get('source_families', [])}
    if routes_obj.get('route_count') != len(routes) or len(routes) != 24:
        errors.append(f'rev0024 source-family identity route count mismatch: {len(routes)}')
    for r in routes:
        _zero(r, errors, f"identity route {r.get('source_family_identity_route_id')}")
        if r.get('source_family_id') not in sf_ids:
            errors.append(f"identity route {r.get('source_family_identity_route_id')} references unknown source family")
        if r.get('live_identity_resolution_allowed_rev0024') is not False or r.get('canonical_record_creation_allowed_rev0024') is not False or r.get('public_identity_display_allowed_rev0024') is not False:
            errors.append(f"identity route {r.get('source_family_identity_route_id')} opens live/canonical/display")
        for cls in r.get('likely_entity_class_keys', []):
            if cls not in entity_keys:
                errors.append(f"identity route {r.get('source_family_identity_route_id')} references unknown entity class {cls}")

    manifest = _load(root, 'RELEASE-MANIFEST.json')
    for k in ['live_identity_records_created_rev0024','canonical_agency_records_created_rev0024','person_records_created_rev0024','officer_records_created_rev0024','civilian_records_created_rev0024','incident_records_created_rev0024','lawsuit_records_created_rev0024','settlement_records_created_rev0024','public_claims_admitted_rev0024','public_displays_admitted_rev0024','payload_captures_admitted_rev0024','payload_hashes_admitted_rev0024','destructive_moves_performed_rev0024']:
        if manifest.get(k, 0) != 0:
            errors.append(f'manifest {k} must be 0')
    for k in ['public_identity_displays_enabled_rev0024','bulk_exports_enabled_rev0024']:
        if manifest.get(k) is not False:
            errors.append(f'manifest {k} must be false')
    return errors
