"""Rev0024 civilian/family dignity-office validation facet.

Checks civilian role taxonomy, family-packet ladder, consent/preference gates, minimization matrix,
death-in-custody gates, witness risks, trauma-media rules, community routes, family contact boundaries,
source-family dignity crosswalks, audience/civilian visibility matrix, synthetic fixtures, and audit/refactor rows.
"""
from __future__ import annotations
from pathlib import Path
import json


def load(root: Path, rel: str):
    return json.loads((root / rel).read_text(encoding='utf-8'))


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    role_obj = load(root, 'data/civilian_dignity/rev0024_civilian_role_taxonomy.json')
    roles = role_obj.get('roles', [])
    ladder_obj = load(root, 'data/civilian_dignity/rev0024_family_packet_ladder.json')
    ladder = ladder_obj.get('states', [])
    consent = load(root, 'data/civilian_dignity/rev0024_consent_preference_gates.json').get('gates', [])
    minimization = load(root, 'data/civilian_dignity/rev0024_sensitive_identity_minimization.json').get('rules', [])
    dic = load(root, 'data/civilian_dignity/rev0024_death_in_custody_family_packet_gates.json').get('gates', [])
    witness = load(root, 'data/civilian_dignity/rev0024_witness_retaliation_risks.json').get('risks', [])
    media = load(root, 'data/civilian_dignity/rev0024_trauma_media_handling_rules.json').get('rules', [])
    consult = load(root, 'data/civilian_dignity/rev0024_community_consultation_routes.json').get('routes', [])
    contacts = load(root, 'data/civilian_dignity/rev0024_family_contact_boundaries.json').get('boundaries', [])
    cross = load(root, 'data/civilian_dignity/rev0024_source_family_dignity_crosswalk.json').get('rows', [])
    visibility = load(root, 'data/civilian_dignity/rev0024_audience_civilian_visibility_matrix.json').get('rows', [])
    fixtures = load(root, 'data/civilian_dignity/rev0024_synthetic_civilian_dignity_fixtures.json').get('fixtures', [])
    principles = load(root, 'data/civilian_dignity/rev0024_dignity_principles.json').get('principles', [])
    expected = [
        (principles, 16, 'dignity principles'), (roles, 26, 'civilian roles'), (ladder, 14, 'family packet states'),
        (consent, 18, 'consent/preference gates'), (minimization, 24, 'minimization rules'),
        (dic, 18, 'death-in-custody gates'), (witness, 14, 'witness risks'), (media, 16, 'trauma-media rules'),
        (consult, 12, 'community routes'), (contacts, 12, 'family contact boundaries'),
        (cross, 24, 'source-family dignity crosswalk rows'), (visibility, 216, 'audience/civilian visibility rows'),
        (fixtures, 16, 'synthetic civilian dignity fixtures')]
    for arr, count, label in expected:
        if len(arr) != count:
            errors.append(f'rev0024 expected {count} {label}, found {len(arr)}')
    role_keys = {r.get('role_key') for r in roles}
    for required in ['decedent','minor','sexual_assault_survivor','mental_health_crisis_subject','witness','family_member','unknown_or_unresolved_civilian_role']:
        if required not in role_keys:
            errors.append(f'rev0024 missing civilian role {required}')
    for r in roles:
        if r.get('default_public_name_display_allowed_rev0024') is not False:
            errors.append(f"rev0024 role {r.get('civilian_role_id')} allows public name display")
        if r.get('live_person_record_created_rev0024') is not False:
            errors.append(f"rev0024 role {r.get('civilian_role_id')} creates live person record")
        if r.get('public_claims_admitted_rev0024') != 0 or r.get('live_records_created_rev0024') != 0:
            errors.append(f"rev0024 role {r.get('civilian_role_id')} admits claims/live records")
    for s in ladder:
        if s.get('public_display_enabled_rev0024') is not False or s.get('live_family_packet_created_rev0024') is not False:
            errors.append(f"rev0024 family ladder {s.get('family_packet_state_id')} opens display or live packet")
    for g in consent:
        if g.get('live_contact_enabled_rev0024') is not False:
            errors.append(f"rev0024 consent gate {g.get('consent_preference_gate_id')} enables live contact")
    for rule in minimization:
        if rule.get('raw_payload_release_allowed_rev0024') is not False or rule.get('person_level_display_allowed_rev0024') is not False:
            errors.append(f"rev0024 minimization rule {rule.get('minimization_rule_id')} permits raw/person display")
    for gate in dic:
        if gate.get('packet_publication_blocked_rev0024') is not True or gate.get('live_packet_created_rev0024') is not False:
            errors.append(f"rev0024 death gate {gate.get('death_in_custody_gate_id')} not blocked")
    for risk in witness:
        if risk.get('default_identity_display_allowed_rev0024') is not False:
            errors.append(f"rev0024 witness risk {risk.get('witness_risk_id')} allows identity display")
    for rule in media:
        if rule.get('default_public_release_allowed_rev0024') is not False or rule.get('raw_payload_release_allowed_rev0024') is not False:
            errors.append(f"rev0024 media rule {rule.get('trauma_media_rule_id')} enables release")
    for route in consult:
        if route.get('consultation_opened_rev0024') is not False or route.get('does_not_create_claim_or_veto') is not True:
            errors.append(f"rev0024 consultation route {route.get('community_consultation_route_id')} unsafe state")
    for boundary in contacts:
        if boundary.get('contact_enabled_rev0024') is not False:
            errors.append(f"rev0024 contact boundary {boundary.get('family_contact_boundary_id')} enables contact")
    family_ids = {f.get('source_family_id') for f in load(root, 'data/source_families/rev0019_source_family_atlas.json').get('source_families', [])}
    if {row.get('source_family_id') for row in cross} != family_ids:
        errors.append('rev0024 source-family dignity crosswalk must cover exactly the rev0019 source families')
    for row in cross:
        if row.get('live_intake_enabled_rev0024') is not False or row.get('public_claims_admitted_rev0024') != 0:
            errors.append(f"rev0024 source-family dignity row {row.get('source_family_dignity_crosswalk_id')} opens intake/claims")
    for row in visibility:
        if row.get('enabled_rev0024') is not False or row.get('public_claims_admitted_rev0024') != 0:
            errors.append(f"rev0024 visibility row {row.get('visibility_row_id')} enables display/claims")
    for fx in fixtures:
        if fx.get('uses_live_people_or_real_incidents') is not False or fx.get('uses_live_source_payload') is not False:
            errors.append(f"rev0024 fixture {fx.get('fixture_id')} uses live data")
    for path, key, count_field in [
        ('data/refactor/rev0024_privacy_surface_term_audit.json','rows','surface_count'),
        ('data/refactor/rev0024_civilian_namespace_shadow_manifest.json','rows','root_surface_count'),
        ('data/refactor/rev0024_civilian_schema_linkage_audit.json','rows','row_count'),
        ('data/refactor/rev0024_validator_facet_smoke_report.json','rows','smoke_row_count'),
    ]:
        obj = load(root, path)
        arr = obj.get(key, [])
        if obj.get(count_field) != len(arr):
            errors.append(f'rev0024 {path} count mismatch')
        if obj.get('destructive_moves_performed_rev0024', 0) != 0:
            errors.append(f'rev0024 {path} performed destructive move')
    if not any(row.get('module_path') == 'tools/validators/rev0024_civilian_family_dignity_checks.py' and row.get('has_validate_function') is True for row in load(root, 'data/refactor/rev0024_validator_facet_smoke_report.json').get('rows', [])):
        errors.append('rev0024 civilian/family validator facet missing from smoke report')
    return errors

