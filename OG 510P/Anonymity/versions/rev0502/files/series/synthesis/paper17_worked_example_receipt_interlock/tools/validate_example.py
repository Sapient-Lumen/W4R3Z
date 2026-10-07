#!/usr/bin/env python3
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts'
RELEASE_ID = 'worked-example-draft-194'
NOTE_VERSION = '1.94'


def extract_packet_family_basis(packet_like):
    if not isinstance(packet_like, dict):
        return {}

    def basis_from_excerpt(excerpt, fallback_contract_key=None):
        if isinstance(excerpt, dict):
            if 'covered_family_keys' in excerpt or 'covered_request_fulfillment_certificate_keys' in excerpt or 'family_completion_verdicts' in excerpt:
                return {
                    'public_request_contract_key': excerpt.get('public_request_contract_key', fallback_contract_key),
                    'covered_family_keys': excerpt.get('covered_family_keys', []),
                    'covered_request_fulfillment_certificate_keys': excerpt.get('covered_request_fulfillment_certificate_keys', []),
                    'family_completion_map': {
                        entry.get('family_key'): entry.get('completion_verdict')
                        for entry in excerpt.get('family_completion_verdicts', [])
                        if isinstance(entry, dict) and entry.get('family_key') is not None
                    },
                }
            if 'public_anchor_families' in excerpt:
                families_field = excerpt.get('public_anchor_families', {})
                if isinstance(families_field, dict):
                    covered_family_keys = sorted(families_field.keys())
                    covered_request_fulfillment_certificate_keys = []
                else:
                    covered_family_keys = [entry.get('family_key') for entry in families_field if isinstance(entry, dict) and entry.get('family_key') is not None]
                    covered_request_fulfillment_certificate_keys = sorted({
                        cert
                        for entry in families_field if isinstance(entry, dict)
                        for cert in entry.get('request_fulfillment_certificate_keys', [])
                    })
                return {
                    'public_request_contract_key': fallback_contract_key,
                    'covered_family_keys': covered_family_keys,
                    'covered_request_fulfillment_certificate_keys': covered_request_fulfillment_certificate_keys,
                    'family_completion_map': {},
                }
            nested = excerpt.get('selected_entry_excerpt')
            if nested is not None:
                basis = basis_from_excerpt(nested, fallback_contract_key)
                if basis and excerpt.get('public_request_response_packet_key'):
                    basis = {
                        'predecessor_public_request_response_packet_key': excerpt.get('public_request_response_packet_key'),
                        **basis,
                    }
                return basis
            return {}
        if isinstance(excerpt, list):
            families = []
            certs = []
            completion = {}
            contract_key = fallback_contract_key
            for entry in excerpt:
                if not isinstance(entry, dict):
                    continue
                family = entry.get('family_key')
                if family is not None:
                    families.append(family)
                cert = entry.get('request_fulfillment_certificate_key')
                if cert is not None:
                    certs.append(cert)
                if family is not None and entry.get('completion_verdict') is not None:
                    completion[family] = entry.get('completion_verdict')
                contract_key = entry.get('public_request_contract_key', contract_key)
            return {
                'public_request_contract_key': contract_key,
                'covered_family_keys': families,
                'covered_request_fulfillment_certificate_keys': certs,
                'family_completion_map': completion,
            }
        return {}

    return basis_from_excerpt(packet_like.get('selected_entry_excerpt'), packet_like.get('selected_object_key'))


def extract_packet_support_surface(packet_like):
    if not isinstance(packet_like, dict):
        return {}
    return {
        'basis_cite_path': packet_like.get('basis_cite_path'),
        'selected_object_path': packet_like.get('selected_object_path'),
        'packet_paths': packet_like.get('packet_paths', []),
        'required_public_paths': packet_like.get('required_public_paths', []),
        'required_validation_paths': packet_like.get('required_validation_paths', []),
    }


def extract_packet_manifest_cut(packet_like, manifest_index, manifest_id):
    if not isinstance(packet_like, dict):
        return {}

    def lookup(path):
        if path is None:
            return None
        if path in {'support_manifest.json', 'example_validation_report.json'}:
            return {'path': path, 'sha256': None}
        resolved = (ART / path).resolve()
        if resolved.exists() and resolved.is_file():
            return {'path': path, 'sha256': hashlib.sha256(resolved.read_bytes()).hexdigest()}
        entry = manifest_index.get(path)
        if entry is not None:
            return entry
        return {'path': path, 'sha256': None}

    def lookup_list(paths):
        return [lookup(path) for path in paths]

    packet_paths = packet_like.get('packet_paths', [])
    required_public_paths = packet_like.get('required_public_paths', [])
    required_validation_paths = packet_like.get('required_validation_paths', [])
    return {
        'support_manifest_id': manifest_id,
        'basis_cite_entry': lookup(packet_like.get('basis_cite_path')),
        'selected_object_entry': lookup(packet_like.get('selected_object_path')),
        'packet_entries': lookup_list(packet_paths),
        'required_public_entries': lookup_list(required_public_paths),
        'required_validation_entries': lookup_list(required_validation_paths),
    }


def extract_packet_inventory_cut(packet_like, inventory_index, inventory_id):
    if not isinstance(packet_like, dict):
        return {}

    def lookup(path):
        if path is None:
            return None
        normalized = path[3:] if isinstance(path, str) and path.startswith('../') else path
        entry = inventory_index.get(path) or inventory_index.get(normalized)
        if entry is None:
            return {
                'requested_path': path,
                'inventory_path': normalized if normalized != path else path,
                'group': None,
                'visibility': None,
                'role': None,
                'consumed_by': [],
            }
        return {
            'requested_path': path,
            'inventory_path': entry['path'],
            'group': entry.get('group'),
            'visibility': entry.get('visibility'),
            'role': entry.get('role'),
            'consumed_by': entry.get('consumed_by', []),
        }

    def lookup_list(paths):
        return [lookup(path) for path in paths]

    packet_paths = packet_like.get('packet_paths', [])
    required_public_paths = packet_like.get('required_public_paths', [])
    required_validation_paths = packet_like.get('required_validation_paths', [])
    return {
        'artifact_inventory_id': inventory_id,
        'basis_cite_entry': lookup(packet_like.get('basis_cite_path')),
        'selected_object_entry': lookup(packet_like.get('selected_object_path')),
        'packet_entries': lookup_list(packet_paths),
        'required_public_entries': lookup_list(required_public_paths),
        'required_validation_entries': lookup_list(required_validation_paths),
    }


def extract_disclosure_packet_support_surface(packet_like):
    if not isinstance(packet_like, dict):
        return {}
    return {
        'basis_cite_path': 'example_successor_challenge_answer_disclosure_packets.json',
        'selected_object_path': 'example_successor_challenge_answer_disclosure_packets.json',
        'request_packet_paths': packet_like.get('request_packet_paths', []),
        'validation_paths': packet_like.get('validation_paths', []),
        'public_anchor_paths': [path for path in [packet_like.get('start_path'), packet_like.get('minimal_path')] if path],
    }


def extract_disclosure_packet_manifest_cut(packet_like, manifest_index, manifest_id):
    return extract_packet_manifest_cut({
        'basis_cite_path': 'example_successor_challenge_answer_disclosure_packets.json',
        'selected_object_path': 'example_successor_challenge_answer_disclosure_packets.json',
        'packet_paths': packet_like.get('request_packet_paths', []),
        'required_public_paths': [path for path in [packet_like.get('start_path'), packet_like.get('minimal_path')] if path],
        'required_validation_paths': packet_like.get('validation_paths', []),
    }, manifest_index, manifest_id)


def extract_disclosure_packet_inventory_cut(packet_like, inventory_index, inventory_id):
    return extract_packet_inventory_cut({
        'basis_cite_path': 'example_successor_challenge_answer_disclosure_packets.json',
        'selected_object_path': 'example_successor_challenge_answer_disclosure_packets.json',
        'packet_paths': packet_like.get('request_packet_paths', []),
        'required_public_paths': [path for path in [packet_like.get('start_path'), packet_like.get('minimal_path')] if path],
        'required_validation_paths': packet_like.get('validation_paths', []),
    }, inventory_index, inventory_id)

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(name: str):
    path = ART / name
    data = path.read_bytes()
    return json.loads(data), sha256_bytes(data)


def extract_paper_version(text: str):
    m = re.search(r'Unified archive note v([0-9]+\.[0-9]+)', text)
    return m.group(1) if m else None


def main() -> None:
    compare_report, compare_report_digest = load_json('example_compare_report.json')
    compare_profile, _ = load_json('example_compare_profile.json')
    support_manifest, _ = load_json('support_manifest.json')
    artifact_inventory, artifact_inventory_digest = load_json('example_artifact_inventory.json')
    successor_derivation_graph, successor_derivation_graph_digest = load_json('example_successor_derivation_graph.json')
    successor_lineage_notice, successor_lineage_notice_digest = load_json('example_successor_lineage_notice.json')
    successor_continuity_verdict, _ = load_json('example_successor_continuity_verdict.json')
    release_obligation_profile, _ = load_json('example_release_obligation_profile.json')
    release_closure_ledger, _ = load_json('example_release_closure_ledger.json')
    successor_status_envelope, _ = load_json('example_successor_status_envelope.json')
    publication_closure_verdict, publication_closure_verdict_digest = load_json('example_publication_closure_verdict.json')
    release_spine, release_spine_digest = load_json('example_release_spine.json')
    release_stage_walkthrough, release_stage_walkthrough_digest = load_json('example_release_stage_walkthrough.json')
    public_request_contracts, public_request_contracts_digest = load_json('example_public_request_contracts.json')
    request_fulfillment_certificates, request_fulfillment_certificates_digest = load_json('example_request_fulfillment_certificates.json')
    public_request_status_envelope, public_request_status_envelope_digest = load_json('example_public_request_status_envelope.json')
    public_request_carryforward_envelope, public_request_carryforward_envelope_digest = load_json('example_public_request_carryforward_envelope.json')
    public_request_notice, public_request_notice_digest = load_json('example_public_request_notice.json')
    public_request_notice_normal_forms, public_request_notice_normal_forms_digest = load_json('example_public_request_notice_normal_forms.json')
    public_request_notice_selections, public_request_notice_selections_digest = load_json('example_public_request_notice_selections.json')
    public_request_response_menus, public_request_response_menus_digest = load_json('example_public_request_response_menus.json')
    public_request_response_packets, public_request_response_packets_digest = load_json('example_public_request_response_packets.json')
    public_request_response_packet_carryforward_profiles, public_request_response_packet_carryforward_profiles_digest = load_json('example_public_request_response_packet_carryforward_profiles.json')
    public_request_response_packet_delta_ledgers, public_request_response_packet_delta_ledgers_digest = load_json('example_public_request_response_packet_delta_ledgers.json')
    public_request_response_packet_refresh_notices, public_request_response_packet_refresh_notices_digest = load_json('example_public_request_response_packet_refresh_notices.json')
    public_request_response_packet_refresh_notice_normal_forms, public_request_response_packet_refresh_notice_normal_forms_digest = load_json('example_public_request_response_packet_refresh_notice_normal_forms.json')
    public_request_response_packet_refresh_notice_selections, public_request_response_packet_refresh_notice_selections_digest = load_json('example_public_request_response_packet_refresh_notice_selections.json')
    public_request_response_packet_refresh_response_menus, public_request_response_packet_refresh_response_menus_digest = load_json('example_public_request_response_packet_refresh_response_menus.json')
    public_request_response_packet_refresh_response_packets, public_request_response_packet_refresh_response_packets_digest = load_json('example_public_request_response_packet_refresh_response_packets.json')
    public_request_response_packet_refresh_response_packet_closure_verdicts, public_request_response_packet_refresh_response_packet_closure_verdicts_digest = load_json('example_public_request_response_packet_refresh_response_packet_closure_verdicts.json')
    series_spine, series_spine_digest = load_json('example_series_spine.json')
    question_routes, question_routes_digest = load_json('example_question_routes.json')
    answer_review_menus, _ = load_json('example_successor_challenge_answer_review_menus.json')
    answer_escalation_ladders, _ = load_json('example_successor_challenge_answer_escalation_ladders.json')
    answer_publication_profiles, _ = load_json('example_successor_challenge_answer_publication_profiles.json')
    answer_citation_dockets, _ = load_json('example_successor_challenge_answer_citation_dockets.json')
    answer_carrier_slots, _ = load_json('example_successor_challenge_answer_carrier_slots.json')
    answer_audit_trails, _ = load_json('example_successor_challenge_answer_audit_trails.json')
    answer_disclosure_packets, answer_disclosure_packets_digest = load_json('example_successor_challenge_answer_disclosure_packets.json')
    answer_cards, _ = load_json('example_successor_challenge_answer_cards.json')
    sentence_locks, _ = load_json('example_successor_sentence_locks.json')
    challenge_routes, _ = load_json('example_successor_challenge_routes.json')
    challenge_stop_profiles, _ = load_json('example_successor_challenge_stop_profiles.json')
    challenge_branches, _ = load_json('example_successor_challenge_branches.json')
    requestable_evidence_classes, _ = load_json('example_requestable_evidence_classes.json')

    checks = []

    def record(name: str, ok: bool, detail: str):
        checks.append({'name': name, 'ok': ok, 'detail': detail})

    paper_text = (ROOT / 'paper.tex').read_text(encoding='utf-8')
    paper_version = extract_paper_version(paper_text)
    readme_text = (ROOT / 'README.md').read_text(encoding='utf-8')

    record('paper version aligned', paper_version == NOTE_VERSION, f'paper_version={paper_version}; note_version={NOTE_VERSION}')
    expected_readme_cut = f'Current maintained cut: {RELEASE_ID} / note_version {NOTE_VERSION}'
    record('README current cut aligned', expected_readme_cut in readme_text, expected_readme_cut)
    record('support manifest identity', support_manifest.get('manifest_id') == 'worked-example-support-manifest-v1' and support_manifest.get('release_id') == RELEASE_ID and support_manifest.get('note_version') == NOTE_VERSION, f"manifest_id={support_manifest.get('manifest_id')}; release_id={support_manifest.get('release_id')}; note_version={support_manifest.get('note_version')}")

    manifest_paths = {entry['path']: entry['sha256'] for entry in support_manifest.get('files', [])}
    manifest_index = {path: {'path': path, 'sha256': sha} for path, sha in manifest_paths.items()}
    inventory_index = {entry['path']: {**entry, 'group': group.get('group'), 'visibility': group.get('visibility')} for group in artifact_inventory.get('groups', []) for entry in group.get('entries', [])}
    expected_digests = {
        'example_compare_report.json': compare_report_digest,
        'example_artifact_inventory.json': artifact_inventory_digest,
        'example_successor_derivation_graph.json': successor_derivation_graph_digest,
        'example_successor_lineage_notice.json': successor_lineage_notice_digest,
        'example_publication_closure_verdict.json': publication_closure_verdict_digest,
        'example_public_request_contracts.json': public_request_contracts_digest,
        'example_request_fulfillment_certificates.json': request_fulfillment_certificates_digest,
        'example_public_request_status_envelope.json': public_request_status_envelope_digest,
        'example_public_request_carryforward_envelope.json': public_request_carryforward_envelope_digest,
        'example_public_request_notice.json': public_request_notice_digest,
        'example_public_request_notice_normal_forms.json': public_request_notice_normal_forms_digest,
        'example_public_request_notice_selections.json': public_request_notice_selections_digest,
        'example_public_request_response_menus.json': public_request_response_menus_digest,
        'example_public_request_response_packets.json': public_request_response_packets_digest,
        'example_public_request_response_packet_carryforward_profiles.json': public_request_response_packet_carryforward_profiles_digest,
        'example_public_request_response_packet_delta_ledgers.json': public_request_response_packet_delta_ledgers_digest,
        'example_public_request_response_packet_refresh_notices.json': public_request_response_packet_refresh_notices_digest,
        'example_public_request_response_packet_refresh_notice_normal_forms.json': public_request_response_packet_refresh_notice_normal_forms_digest,
        'example_public_request_response_packet_refresh_notice_selections.json': public_request_response_packet_refresh_notice_selections_digest,
        'example_public_request_response_packet_refresh_response_menus.json': public_request_response_packet_refresh_response_menus_digest,
        'example_public_request_response_packet_refresh_response_packets.json': public_request_response_packet_refresh_response_packets_digest,
        'example_public_request_response_packet_refresh_response_packet_closure_verdicts.json': public_request_response_packet_refresh_response_packet_closure_verdicts_digest,
        'example_successor_challenge_answer_disclosure_packets.json': answer_disclosure_packets_digest,
        'example_series_spine.json': series_spine_digest,
        'example_release_spine.json': release_spine_digest,
        'example_release_stage_walkthrough.json': release_stage_walkthrough_digest,
        'example_question_routes.json': question_routes_digest,
    }
    manifest_ok = all(manifest_paths.get(k) == v for k, v in expected_digests.items())
    record('support manifest digest bindings', manifest_ok, 'manifest includes digests for compare report, inventory, release spine, release stage walkthrough, derivation graph, lineage notice, publication closure verdict, public request contract/certificate/status/carryforward/notice/notice-normal-form/notice-selection/response-menu/response-packet/response-packet-carryforward/response-packet-delta/response-packet-refresh-notice/packet-refresh-notice-normal-form/packet-refresh-notice-selection, packet-refresh-response-menu, packet-refresh-response-packet, packet-refresh-response-packet-closure-verdict, answer-disclosure-packet artifacts, series spine, and question-routing catalog')

    inventory_paths = {entry.get('path') for group in artifact_inventory.get('groups', []) for entry in group.get('entries', [])}
    record('artifact inventory includes new public request artifacts', {'example_public_request_status_envelope.json', 'example_public_request_carryforward_envelope.json', 'example_public_request_notice.json', 'example_public_request_notice_normal_forms.json', 'example_public_request_notice_selections.json', 'example_public_request_response_menus.json', 'example_public_request_response_packets.json', 'example_public_request_response_packet_carryforward_profiles.json', 'example_public_request_response_packet_delta_ledgers.json', 'example_public_request_response_packet_refresh_notices.json', 'example_public_request_response_packet_refresh_notice_normal_forms.json', 'example_public_request_response_packet_refresh_notice_selections.json', 'example_public_request_response_packet_refresh_response_menus.json', 'example_public_request_response_packet_refresh_response_packets.json', 'example_public_request_response_packet_refresh_response_packet_closure_verdicts.json', 'example_release_spine.json', 'example_release_stage_walkthrough.json', 'example_question_routes.json'}.issubset(inventory_paths), f'missing={sorted(set(["example_public_request_status_envelope.json", "example_public_request_carryforward_envelope.json", "example_public_request_notice.json", "example_public_request_notice_normal_forms.json", "example_public_request_notice_selections.json", "example_public_request_response_menus.json", "example_public_request_response_packets.json", "example_public_request_response_packet_carryforward_profiles.json", "example_public_request_response_packet_delta_ledgers.json", "example_public_request_response_packet_refresh_notices.json", "example_public_request_response_packet_refresh_notice_normal_forms.json", "example_public_request_response_packet_refresh_notice_selections.json", "example_public_request_response_packet_refresh_response_menus.json", "example_public_request_response_packet_refresh_response_packets.json", "example_public_request_response_packet_refresh_response_packet_closure_verdicts.json", "example_release_spine.json", "example_release_stage_walkthrough.json", "example_question_routes.json"]) - inventory_paths)}')

    claim_id = compare_report.get('claim_id')
    common_objs = [compare_report, compare_profile, artifact_inventory, release_spine, release_stage_walkthrough, successor_derivation_graph, successor_lineage_notice, successor_continuity_verdict, publication_closure_verdict, public_request_contracts, request_fulfillment_certificates, public_request_status_envelope, public_request_carryforward_envelope, public_request_notice, public_request_notice_normal_forms, public_request_notice_selections, public_request_response_menus, public_request_response_packets, public_request_response_packet_carryforward_profiles, public_request_response_packet_delta_ledgers, public_request_response_packet_refresh_notices, public_request_response_packet_refresh_notice_normal_forms, public_request_response_packet_refresh_notice_selections, public_request_response_packet_refresh_response_menus, public_request_response_packet_refresh_response_packets, public_request_response_packet_refresh_response_packet_closure_verdicts, answer_publication_profiles, answer_disclosure_packets, answer_cards, sentence_locks, series_spine, question_routes]
    record('claim id coherence', all(obj.get('claim_id') == claim_id for obj in common_objs), f'claim_id={claim_id}')
    record('release id coherence', all(obj.get('release_id') == RELEASE_ID for obj in common_objs if 'release_id' in obj), f'release_id={RELEASE_ID}')
    record('note version coherence', all(obj.get('note_version') == NOTE_VERSION for obj in [artifact_inventory, release_spine, release_stage_walkthrough, public_request_contracts, request_fulfillment_certificates, public_request_status_envelope, public_request_carryforward_envelope, public_request_notice, public_request_notice_normal_forms, public_request_notice_selections, public_request_response_menus, public_request_response_packet_carryforward_profiles, public_request_response_packet_delta_ledgers, public_request_response_packet_refresh_notices, public_request_response_packet_refresh_notice_normal_forms, public_request_response_packet_refresh_notice_selections, answer_publication_profiles, answer_disclosure_packets, series_spine, question_routes]), f'note_version={NOTE_VERSION}')

    expected_stable_ladder_keys = ['mechanism_justification', 'public_claim_identification', 'replay_verification', 'release_evolution_status', 'answer_side_archive_cut', 'referee_followup_packaging']
    stable_ladder = series_spine.get('stable_ladder', [])
    stable_ladder_ok = (
        [entry.get('task_key') for entry in stable_ladder] == expected_stable_ladder_keys
        and [entry.get('spine_segment') for entry in stable_ladder] == ['mathematical_root', 'receipt_anchor', 'replay_anchor', 'release_anchor', 'disclosure_packet_anchor', 'review_anchor']
        and all(entry.get('position') == i + 1 for i, entry in enumerate(stable_ladder))
        and all(entry.get('stop_when') and entry.get('widen_only_if') for entry in stable_ladder)
    )
    record('series spine stable ladder order', stable_ladder_ok, f"stable_ladder={[entry.get('task_key') for entry in stable_ladder]}")

    question_stable_ladder_ok = question_routes.get('stable_ladder') == stable_ladder
    record('question routing stable ladder mirror', question_stable_ladder_ok, f"question_stable_ladder={[entry.get('task_key') for entry in question_routes.get('stable_ladder', [])]}")

    expected_release_stage_order = ['diff', 'classify', 'obligate', 'close', 'summarize', 'support', 'cite', 'quote', 'clause']
    release_stage_order = release_spine.get('stage_order', [])
    release_stage_contracts = {entry.get('stage'): entry for entry in release_spine.get('stage_contracts', [])}
    walkthrough_rows = {entry.get('stage'): entry for entry in release_stage_walkthrough.get('stage_walk', [])}
    release_stage_order_ok = (
        release_spine.get('stage_order_fields') == ['stage', 'question', 'artifact', 'companion_artifact', 'object_id', 'release_stage_vocabulary_mode', 'stop_when', 'widen_only_if', 'why']
        and [entry.get('stage') for entry in release_stage_order] == expected_release_stage_order
        and all(entry.get('release_stage_vocabulary_mode') == 'owned_vocabulary_release_spine_stage_order' for entry in release_stage_order)
        and all(entry.get('stop_when') and entry.get('widen_only_if') and entry.get('why') for entry in release_stage_order)
        and all(entry.get('artifact') == release_stage_contracts.get(entry.get('stage'), {}).get('output_artifact') for entry in release_stage_order)
        and all(entry.get('artifact') == walkthrough_rows.get(entry.get('stage'), {}).get('output_artifact') for entry in release_stage_order)
    )
    record('release spine stage-order stop rules', release_stage_order_ok, f"stage_order={[entry.get('stage') for entry in release_stage_order]}")
    record('release spine stage-cut rule', bool(release_spine.get('stage_cut_rule') and 'Stop at the earliest sufficient release-local stage' in release_spine.get('stage_cut_rule', '')), release_spine.get('stage_cut_rule', ''))
    release_stage_walkthrough_ok = (
        release_stage_walkthrough.get('stage_walk_fields') == ['stage', 'output_artifact', 'owned_field_family', 'resolved_inputs', 'assertion_scope', 'handoff_rule', 'stage_summary', 'why_not_later']
        and [entry.get('stage') for entry in release_stage_walkthrough.get('stage_walk', [])] == expected_release_stage_order
        and all(release_stage_contracts.get(entry.get('stage'), {}).get('output_field_family') == entry.get('owned_field_family') for entry in release_stage_walkthrough.get('stage_walk', []))
    )
    record('release stage walkthrough coherence', release_stage_walkthrough_ok, f"stage_walk={[entry.get('stage') for entry in release_stage_walkthrough.get('stage_walk', [])]}")

    contract_entries = public_request_contracts.get('public_request_contracts', [])
    cert_entries = request_fulfillment_certificates.get('request_fulfillment_certificates', [])
    status_entries = public_request_status_envelope.get('public_request_status_envelopes', [])
    carry_entries = public_request_carryforward_envelope.get('public_request_carryforward_envelopes', [])
    notice_entries = public_request_notice.get('public_request_notices', [])
    notice_nf_entries = public_request_notice_normal_forms.get('public_request_notice_normal_forms', [])
    notice_selection_entries = public_request_notice_selections.get('public_request_notice_selections', [])
    response_menu_entries = public_request_response_menus.get('public_request_response_menus', [])
    response_packet_carryforward_entries = public_request_response_packet_carryforward_profiles.get('public_request_response_packet_carryforward_profiles', [])
    response_packet_delta_entries = public_request_response_packet_delta_ledgers.get('public_request_response_packet_delta_ledgers', [])
    response_packet_refresh_notice_entries = public_request_response_packet_refresh_notices.get('public_request_response_packet_refresh_notices', [])
    response_packet_refresh_notice_normal_form_entries = public_request_response_packet_refresh_notice_normal_forms.get('public_request_response_packet_refresh_notice_normal_forms', [])

    contract_ok = len(contract_entries) == 1 and contract_entries[0].get('public_request_contract_key') == 'worked_example_receipt_interlock_public_request_contract'
    if contract_ok:
        contract_ok = (
            public_request_contracts.get('contract', {}).get('public_anchor_family_fields') == ['family_key', 'question_key', 'audiences', 'public_paths', 'review_menu_keys', 'disclosure_packet_keys', 'evidence_class_keys', 'request_fulfillment_certificate_keys', 'public_anchor_family_vocabulary_mode', 'why']
            and bool(public_request_contracts.get('contract', {}).get('shared_public_anchor_family_vocabulary_rule'))
            and all(entry.get('public_anchor_family_vocabulary_mode') == 'imported_contract_vocabulary_contract_owned_basis' for entry in contract_entries[0].get('public_anchor_families', []))
        )
    record('public request contract identity', contract_ok, f'contract_count={len(contract_entries)}')
    public_anchor_family_mode_map = {entry.get('family_key'): entry.get('public_anchor_family_vocabulary_mode') for entry in (contract_entries[0].get('public_anchor_families', []) if contract_entries else [])}

    evidence_entries = requestable_evidence_classes.get('evidence_classes', [])
    evidence_by_key = {entry.get('evidence_class_key'): entry for entry in evidence_entries}
    expected_shared_family_keys = ['public_status_sentence_family', 'compact_diff_summary_family']
    evidence_ok = (
        len(evidence_entries) == 3
        and requestable_evidence_classes.get('contract', {}).get('evidence_class_fields') == ['evidence_class_key', 'public_anchor_family_keys', 'minimal_public_anchor_paths', 'canonical_support_paths', 'covered_disclosure_packet_keys', 'completion_scope', 'evidence_class_vocabulary_mode', 'shared_across_family_keys', 'why']
        and all(entry.get('evidence_class_vocabulary_mode') == 'imported_vocabulary_class_owned_meaning' for entry in evidence_entries)
        and evidence_by_key.get('bundle_identity_and_validator_companions', {}).get('completion_scope') == 'family_scoped_import'
        and evidence_by_key.get('bundle_identity_and_validator_companions', {}).get('shared_across_family_keys') == expected_shared_family_keys
        and evidence_by_key.get('public_status_lineage_and_closure_support', {}).get('completion_scope') == 'family_scoped_import'
        and evidence_by_key.get('public_status_lineage_and_closure_support', {}).get('shared_across_family_keys') == ['public_status_sentence_family']
        and evidence_by_key.get('compact_diff_compare_and_replay_support', {}).get('completion_scope') == 'family_scoped_import'
        and evidence_by_key.get('compact_diff_compare_and_replay_support', {}).get('shared_across_family_keys') == ['compact_diff_summary_family']
    )
    record('requestable evidence class shared-family split', evidence_ok, f'evidence_class_count={len(evidence_entries)}')

    cert_ok = len(cert_entries) == 2 and {e.get('request_fulfillment_certificate_key') for e in cert_entries} == {'public_status_sentence_request_fulfillment_certificate', 'compact_diff_summary_request_fulfillment_certificate'} and all(e.get('completion_verdict') == 'complete' for e in cert_entries) and all(e.get('completion_verdict_mode') == 'shared_vocabulary_family_scoped_verdict' for e in cert_entries)
    if cert_ok:
        cert_by_key = {entry.get('request_fulfillment_certificate_key'): entry for entry in cert_entries}
        cert_ok = (
            request_fulfillment_certificates.get('contract', {}).get('request_fulfillment_certificate_fields') == ['request_fulfillment_certificate_key', 'public_request_contract_key', 'family_key', 'covered_disclosure_packet_keys', 'covered_evidence_class_keys', 'shared_evidence_class_keys', 'family_specific_evidence_class_keys', 'delivered_public_paths', 'delivered_support_paths', 'validation_paths', 'completion_verdict', 'completion_verdict_mode', 'why']
            and cert_by_key['public_status_sentence_request_fulfillment_certificate'].get('shared_evidence_class_keys') == ['bundle_identity_and_validator_companions']
            and cert_by_key['public_status_sentence_request_fulfillment_certificate'].get('family_specific_evidence_class_keys') == ['public_status_lineage_and_closure_support']
            and cert_by_key['compact_diff_summary_request_fulfillment_certificate'].get('shared_evidence_class_keys') == ['bundle_identity_and_validator_companions']
            and cert_by_key['compact_diff_summary_request_fulfillment_certificate'].get('family_specific_evidence_class_keys') == ['compact_diff_compare_and_replay_support']
            and all(entry.get('covered_evidence_class_keys') == entry.get('shared_evidence_class_keys', []) + entry.get('family_specific_evidence_class_keys', []) for entry in cert_entries)
        )
    record('request fulfillment certificates content', cert_ok, f'certificate_count={len(cert_entries)}')

    status_ok = False
    if len(status_entries) == 1 and contract_ok and cert_ok:
        entry = status_entries[0]
        status_ok = (
            public_request_status_envelope.get('public_request_status_envelopes_id') == 'worked-example-public-request-status-envelopes-v1'
            and public_request_status_envelope.get('successor_public_request_contracts_id') == public_request_contracts.get('public_request_contracts_id')
            and public_request_status_envelope.get('request_fulfillment_certificates_id') == request_fulfillment_certificates.get('request_fulfillment_certificates_id')
            and entry.get('public_request_status_envelope_key') == 'worked_example_receipt_interlock_public_request_status_envelope'
            and entry.get('public_request_contract_key') == 'worked_example_receipt_interlock_public_request_contract'
            and entry.get('covered_family_keys') == ['public_status_sentence_family', 'compact_diff_summary_family']
            and entry.get('covered_request_fulfillment_certificate_keys') == ['public_status_sentence_request_fulfillment_certificate', 'compact_diff_summary_request_fulfillment_certificate']
            and entry.get('family_completion_verdicts') == [
                {'family_key': 'public_status_sentence_family', 'completion_verdict': 'complete'},
                {'family_key': 'compact_diff_summary_family', 'completion_verdict': 'complete'}
            ]
            and entry.get('public_request_status_token') == 'complete'
            and entry.get('public_request_status_token_mode') == 'shared_vocabulary_basis_scoped_status'
            and public_request_status_envelope.get('contract', {}).get('shared_family_completion_vocabulary_rule')
            and public_request_status_envelope.get('contract', {}).get('shared_status_token_vocabulary_rule')
        )
    record('public request status envelope content', status_ok, f'status_count={len(status_entries)}')

    carry_ok = False
    if len(carry_entries) == 1 and status_ok:
        entry = carry_entries[0]
        carry_ok = (
            public_request_carryforward_envelope.get('public_request_carryforward_envelopes_id') == 'worked-example-public-request-carryforward-envelopes-v1'
            and public_request_carryforward_envelope.get('successor_public_request_contracts_id') == public_request_contracts.get('public_request_contracts_id')
            and public_request_carryforward_envelope.get('successor_public_request_status_envelopes_id') == public_request_status_envelope.get('public_request_status_envelopes_id')
            and public_request_carryforward_envelope.get('publication_closure_verdict_id') == publication_closure_verdict.get('closure_verdict_id')
            and public_request_carryforward_envelope.get('successor_continuity_verdict_id') == successor_continuity_verdict.get('verdict_id')
            and entry.get('public_request_carryforward_envelope_key') == 'worked_example_receipt_interlock_public_request_carryforward_envelope'
            and entry.get('predecessor_public_request_status_envelope_key') == 'worked_example_receipt_interlock_public_request_status_envelope'
            and entry.get('successor_public_request_contract_key') == 'worked_example_receipt_interlock_public_request_contract'
            and entry.get('predecessor_public_request_status_token') == 'complete'
            and entry.get('successor_public_request_status_token') == 'complete'
            and entry.get('carryforward_token') == 'preserved_complete'
            and entry.get('changed_family_keys') == []
            and entry.get('reopened_family_keys') == []
            and entry.get('carryforward_token_mode') == 'shared_vocabulary_release_pair_scoped_verdict'
            and public_request_carryforward_envelope.get('contract', {}).get('shared_carryforward_token_vocabulary_rule')
        )
    record('public request carryforward envelope content', carry_ok, f'carryforward_count={len(carry_entries)}')

    notice_ok = False
    if len(notice_entries) == 2 and carry_ok:
        idx = {entry.get('public_request_notice_key'): entry for entry in notice_entries}
        status_notice = idx.get('worked_example_receipt_interlock_public_request_status_notice', {})
        carry_notice = idx.get('worked_example_receipt_interlock_public_request_carryforward_notice', {})
        notice_ok = (
            public_request_notice.get('public_request_notices_id') == 'worked-example-public-request-notices-v1'
            and public_request_notice.get('public_request_status_envelopes_id') == public_request_status_envelope.get('public_request_status_envelopes_id')
            and public_request_notice.get('public_request_carryforward_envelopes_id') == public_request_carryforward_envelope.get('public_request_carryforward_envelopes_id')
            and public_request_notice.get('successor_public_request_contracts_id') == public_request_contracts.get('public_request_contracts_id')
            and status_notice.get('notice_kind') == 'within_release'
            and status_notice.get('basis_artifact') == 'example_public_request_status_envelope.json'
            and status_notice.get('basis_key') == 'worked_example_receipt_interlock_public_request_status_envelope'
            and status_notice.get('public_request_status_token') == 'complete'
            and status_notice.get('carryforward_token') is None
            and carry_notice.get('notice_kind') == 'successor_carryforward'
            and carry_notice.get('basis_artifact') == 'example_public_request_carryforward_envelope.json'
            and carry_notice.get('basis_key') == 'worked_example_receipt_interlock_public_request_carryforward_envelope'
            and carry_notice.get('public_request_status_token') == 'complete'
            and carry_notice.get('carryforward_token') == 'preserved_complete'
        )
    record('public request notice content', notice_ok, f'notice_count={len(notice_entries)}')

    notice_nf_ok = False
    if len(notice_nf_entries) == 2 and notice_ok:
        idx_nf = {entry.get('public_request_notice_normal_form_key'): entry for entry in notice_nf_entries}
        within_nf = idx_nf.get('worked_example_receipt_interlock_within_release_complete_public_request_notice_normal_form', {})
        carry_nf = idx_nf.get('worked_example_receipt_interlock_successor_preserved_complete_public_request_notice_normal_form', {})
        notice_idx = {entry.get('public_request_notice_key'): entry for entry in notice_entries}
        status_notice = notice_idx.get('worked_example_receipt_interlock_public_request_status_notice', {})
        carry_notice = notice_idx.get('worked_example_receipt_interlock_public_request_carryforward_notice', {})
        notice_nf_ok = (
            public_request_notice_normal_forms.get('public_request_notice_normal_forms_id') == 'worked-example-public-request-notice-normal-forms-v1'
            and public_request_notice_normal_forms.get('successor_public_request_notices_id') == public_request_notice.get('public_request_notices_id')
            and public_request_notice_normal_forms.get('public_request_status_envelopes_id') == public_request_status_envelope.get('public_request_status_envelopes_id')
            and public_request_notice_normal_forms.get('public_request_carryforward_envelopes_id') == public_request_carryforward_envelope.get('public_request_carryforward_envelopes_id')
            and within_nf.get('notice_kind') == 'within_release'
            and within_nf.get('emitted_notice_key') == 'worked_example_receipt_interlock_public_request_status_notice'
            and within_nf.get('basis_key') == 'worked_example_receipt_interlock_public_request_status_envelope'
            and within_nf.get('allowed_public_request_status_tokens') == ['complete']
            and within_nf.get('allowed_carryforward_tokens') == []
            and within_nf.get('rendered_sentence') == status_notice.get('notice_sentence')
            and carry_nf.get('notice_kind') == 'successor_carryforward'
            and carry_nf.get('emitted_notice_key') == 'worked_example_receipt_interlock_public_request_carryforward_notice'
            and carry_nf.get('basis_key') == 'worked_example_receipt_interlock_public_request_carryforward_envelope'
            and carry_nf.get('allowed_public_request_status_tokens') == ['complete']
            and carry_nf.get('allowed_carryforward_tokens') == ['preserved_complete']
            and carry_nf.get('rendered_sentence') == carry_notice.get('notice_sentence')
        )
    record('public request notice normal forms content', notice_nf_ok, f'normal_form_count={len(notice_nf_entries)}')

    notice_selection_ok = False
    if len(notice_selection_entries) == 2 and notice_nf_ok:
        idx_sel = {entry.get('public_request_notice_selection_key'): entry for entry in notice_selection_entries}
        within_sel = idx_sel.get('worked_example_receipt_interlock_within_release_public_request_notice_selection', {})
        carry_sel = idx_sel.get('worked_example_receipt_interlock_successor_public_request_notice_selection', {})
        idx_nf = {entry.get('public_request_notice_normal_form_key'): entry for entry in notice_nf_entries}
        within_nf = idx_nf.get('worked_example_receipt_interlock_within_release_complete_public_request_notice_normal_form', {})
        carry_nf = idx_nf.get('worked_example_receipt_interlock_successor_preserved_complete_public_request_notice_normal_form', {})
        notice_idx = {entry.get('public_request_notice_key'): entry for entry in notice_entries}
        status_notice = notice_idx.get('worked_example_receipt_interlock_public_request_status_notice', {})
        carry_notice = notice_idx.get('worked_example_receipt_interlock_public_request_carryforward_notice', {})
        notice_selection_ok = (
            public_request_notice_selections.get('public_request_notice_selections_id') == 'worked-example-public-request-notice-selections-v1'
            and public_request_notice_selections.get('successor_public_request_notices_id') == public_request_notice.get('public_request_notices_id')
            and public_request_notice_selections.get('successor_public_request_notice_normal_forms_id') == public_request_notice_normal_forms.get('public_request_notice_normal_forms_id')
            and public_request_notice_selections.get('public_request_status_envelopes_id') == public_request_status_envelope.get('public_request_status_envelopes_id')
            and public_request_notice_selections.get('public_request_carryforward_envelopes_id') == public_request_carryforward_envelope.get('public_request_carryforward_envelopes_id')
            and within_sel.get('notice_kind') == 'within_release'
            and within_sel.get('basis_key') == 'worked_example_receipt_interlock_public_request_status_envelope'
            and within_sel.get('selector_inputs') == {'public_request_status_token': 'complete', 'carryforward_token': None}
            and within_sel.get('selected_public_request_notice_normal_form_key') == 'worked_example_receipt_interlock_within_release_complete_public_request_notice_normal_form'
            and within_sel.get('selected_emitted_notice_key') == 'worked_example_receipt_interlock_public_request_status_notice'
            and within_sel.get('rendered_sentence') == within_nf.get('rendered_sentence') == status_notice.get('notice_sentence')
            and carry_sel.get('notice_kind') == 'successor_carryforward'
            and carry_sel.get('basis_key') == 'worked_example_receipt_interlock_public_request_carryforward_envelope'
            and carry_sel.get('selector_inputs') == {'public_request_status_token': 'complete', 'carryforward_token': 'preserved_complete'}
            and carry_sel.get('selected_public_request_notice_normal_form_key') == 'worked_example_receipt_interlock_successor_preserved_complete_public_request_notice_normal_form'
            and carry_sel.get('selected_emitted_notice_key') == 'worked_example_receipt_interlock_public_request_carryforward_notice'
            and carry_sel.get('rendered_sentence') == carry_nf.get('rendered_sentence') == carry_notice.get('notice_sentence')
        )
    record('public request notice selections content', notice_selection_ok, f'selection_count={len(notice_selection_entries)}')
    response_menu_ok = False
    if len(response_menu_entries) == 2 and notice_selection_ok:
        idx_menu = {entry.get('public_request_response_menu_key'): entry for entry in response_menu_entries}
        within_menu = idx_menu.get('worked_example_receipt_interlock_within_release_public_request_response_menu', {})
        carry_menu = idx_menu.get('worked_example_receipt_interlock_successor_public_request_response_menu', {})
        status_entry = status_entries[0] if status_entries else {}
        carry_entry = carry_entries[0] if carry_entries else {}
        contract_entry = contract_entries[0] if contract_entries else {}
        cert_keys = ['public_status_sentence_request_fulfillment_certificate', 'compact_diff_summary_request_fulfillment_certificate']
        within_classes = [e.get('request_class') for e in within_menu.get('response_entries', [])]
        carry_classes = [e.get('request_class') for e in carry_menu.get('response_entries', [])]
        expected_classes = ['basis_token_check', 'visible_sentence_check', 'canonical_family_check', 'family_choice_check', 'request_scope_check', 'completion_rule_check']
        response_menu_ok = (
            public_request_response_menus.get('public_request_response_menus_id') == 'worked-example-public-request-response-menus-v1'
            and public_request_response_menus.get('successor_public_request_contracts_id') == public_request_contracts.get('public_request_contracts_id')
            and public_request_response_menus.get('successor_request_fulfillment_certificates_id') == request_fulfillment_certificates.get('request_fulfillment_certificates_id')
            and public_request_response_menus.get('public_request_status_envelopes_id') == public_request_status_envelope.get('public_request_status_envelopes_id')
            and public_request_response_menus.get('public_request_carryforward_envelopes_id') == public_request_carryforward_envelope.get('public_request_carryforward_envelopes_id')
            and public_request_response_menus.get('successor_public_request_notices_id') == public_request_notice.get('public_request_notices_id')
            and public_request_response_menus.get('successor_public_request_notice_normal_forms_id') == public_request_notice_normal_forms.get('public_request_notice_normal_forms_id')
            and public_request_response_menus.get('successor_public_request_notice_selections_id') == public_request_notice_selections.get('public_request_notice_selections_id')
            and within_menu.get('notice_kind') == 'within_release'
            and within_menu.get('followup_class_vocabulary_mode') == 'shared_vocabulary_notice_scoped_selection'
            and within_menu.get('basis_key') == status_entry.get('public_request_status_envelope_key')
            and within_menu.get('public_request_notice_key') == 'worked_example_receipt_interlock_public_request_status_notice'
            and within_menu.get('selected_public_request_notice_normal_form_key') == 'worked_example_receipt_interlock_within_release_complete_public_request_notice_normal_form'
            and within_menu.get('public_request_notice_selection_key') == 'worked_example_receipt_interlock_within_release_public_request_notice_selection'
            and within_menu.get('public_request_contract_key') == contract_entry.get('public_request_contract_key')
            and within_menu.get('covered_request_fulfillment_certificate_keys') == cert_keys
            and within_classes == expected_classes
            and carry_menu.get('notice_kind') == 'successor_carryforward'
            and carry_menu.get('followup_class_vocabulary_mode') == 'shared_vocabulary_notice_scoped_selection'
            and carry_menu.get('basis_key') == carry_entry.get('public_request_carryforward_envelope_key')
            and carry_menu.get('public_request_notice_key') == 'worked_example_receipt_interlock_public_request_carryforward_notice'
            and carry_menu.get('selected_public_request_notice_normal_form_key') == 'worked_example_receipt_interlock_successor_preserved_complete_public_request_notice_normal_form'
            and carry_menu.get('public_request_notice_selection_key') == 'worked_example_receipt_interlock_successor_public_request_notice_selection'
            and carry_menu.get('public_request_contract_key') == contract_entry.get('public_request_contract_key')
            and carry_menu.get('covered_request_fulfillment_certificate_keys') == cert_keys
            and carry_classes == expected_classes
        )
    record('public request response menus content', response_menu_ok, f'response_menu_count={len(response_menu_entries)}')
    response_menu_followup_mode_ok = all(entry.get('followup_class_vocabulary_mode') == 'shared_vocabulary_notice_scoped_selection' for entry in response_menu_entries)
    record('public request response menu followup vocabulary mode', response_menu_followup_mode_ok, f'modes={sorted({entry.get("followup_class_vocabulary_mode") for entry in response_menu_entries})}')
    response_packet_entries = public_request_response_packets.get('public_request_response_packets', [])
    packet_ok = len(response_packet_entries) == 12
    expected_packet_classes = {'basis_token_check', 'visible_sentence_check', 'canonical_family_check', 'family_choice_check', 'request_scope_check', 'completion_rule_check'}
    packet_classes_by_notice = {}
    for entry in response_packet_entries:
        packet_classes_by_notice.setdefault(entry.get('public_request_notice_key'), []).append(entry.get('request_class'))
        packet_ok = packet_ok and entry.get('packet_scope_mode') == 'notice_and_followup_scoped_packet'
        if entry.get('request_class') == 'completion_rule_check':
            packet_ok = packet_ok and 'example_request_fulfillment_certificates.json' in entry.get('packet_paths', []) and bool(entry.get('required_public_paths')) and bool(entry.get('required_validation_paths'))
        if entry.get('request_class') == 'request_scope_check':
            packet_ok = packet_ok and 'example_public_request_contracts.json' in entry.get('packet_paths', []) and bool(entry.get('required_validation_paths'))
        if entry.get('request_class') == 'family_choice_check':
            packet_ok = packet_ok and 'example_public_request_notice_normal_forms.json' in entry.get('packet_paths', [])
    packet_ok = packet_ok and all(set(v) == expected_packet_classes for v in packet_classes_by_notice.values())
    record('public request response packets content', packet_ok, f'response_packet_count={len(response_packet_entries)}')

    packet_carryforward_ok = len(response_packet_carryforward_entries) == len(response_packet_entries)
    packet_keys = {entry.get('public_request_response_packet_key') for entry in response_packet_entries}
    for entry in response_packet_carryforward_entries:
        packet_carryforward_ok = packet_carryforward_ok and (
            public_request_response_packet_carryforward_profiles.get('public_request_response_packet_carryforward_profiles_id') == 'worked-example-public-request-response-packet-carryforward-profiles-v1'
            and public_request_response_packet_carryforward_profiles.get('successor_public_request_response_packets_id') == public_request_response_packets.get('public_request_response_packets_id')
            and public_request_response_packet_carryforward_profiles.get('successor_public_request_carryforward_envelopes_id') == public_request_carryforward_envelope.get('public_request_carryforward_envelopes_id')
            and public_request_response_packet_carryforward_profiles.get('successor_public_request_response_menus_id') == public_request_response_menus.get('public_request_response_menus_id')
            and entry.get('predecessor_public_request_response_packet_key') in packet_keys
            and entry.get('successor_public_request_carryforward_envelope_key') == 'worked_example_receipt_interlock_public_request_carryforward_envelope'
            and entry.get('continuity_decision') == 'same_certified_interface_replayed_surfaces'
            and entry.get('response_packet_carryforward_token') == 'refresh_in_place'
            and entry.get('packet_maintenance_posture', {}).get('current_status') == entry.get('response_packet_carryforward_token')
            and entry.get('packet_maintenance_posture', {}).get('reissue_status') == 'refresh_then_reissue'
            and bool(entry.get('packet_maintenance_posture', {}).get('why'))
            and public_request_response_packet_carryforward_profiles.get('contract', {}).get('packet_maintenance_posture_fields') == ['current_status', 'reissue_status', 'why']
            and public_request_response_packet_carryforward_profiles.get('contract', {}).get('packet_maintenance_posture_rule')
            and public_request_response_packet_carryforward_profiles.get('contract', {}).get('public_request_response_packet_carryforward_profile_fields') == ['public_request_response_packet_carryforward_profile_key', 'predecessor_public_request_response_packet_key', 'public_request_notice_key', 'notice_kind', 'request_class', 'predecessor_selected_object_kind', 'predecessor_selected_object_key', 'predecessor_packet_paths', 'successor_public_request_carryforward_envelope_key', 'continuity_decision', 'response_packet_carryforward_token', 'packet_maintenance_posture', 'refreshable_field_families', 'refreshable_field_family_mode', 'changed_context_classes', 'why']
            and public_request_response_packet_carryforward_profiles.get('contract', {}).get('shared_vocabulary_rule')
            and entry.get('refreshable_field_families') == ['basis_companions', 'selected_entry_excerpt', 'digest_bindings']
            and entry.get('refreshable_field_family_mode') == 'shared_vocabulary_packet_scoped_verdict'
            and entry.get('changed_context_classes') == ['successor_release_binding', 'successor_digest_binding']
        )
    record('public request response packet carryforward profiles content', packet_carryforward_ok, f'carryforward_profile_count={len(response_packet_carryforward_entries)}')

    delta_ok = len(response_packet_delta_entries) == len(response_packet_entries)
    carryforward_profile_keys = {entry.get('public_request_response_packet_carryforward_profile_key') for entry in response_packet_carryforward_entries}
    packet_paths_by_key = {entry.get('public_request_response_packet_key'): entry.get('packet_paths', []) for entry in response_packet_entries}
    for entry in response_packet_delta_entries:
        field_families = [instr.get('field_family') for instr in entry.get('refresh_instructions', [])]
        delta_ok = delta_ok and (
            public_request_response_packet_delta_ledgers.get('public_request_response_packet_delta_ledgers_id') == 'worked-example-public-request-response-packet-delta-ledgers-v1'
            and public_request_response_packet_delta_ledgers.get('successor_public_request_response_packets_id') == public_request_response_packets.get('public_request_response_packets_id')
            and public_request_response_packet_delta_ledgers.get('successor_public_request_response_packet_carryforward_profiles_id') == public_request_response_packet_carryforward_profiles.get('public_request_response_packet_carryforward_profiles_id')
            and public_request_response_packet_delta_ledgers.get('successor_public_request_carryforward_envelopes_id') == public_request_carryforward_envelope.get('public_request_carryforward_envelopes_id')
            and entry.get('public_request_response_packet_carryforward_profile_key') in carryforward_profile_keys
            and entry.get('predecessor_public_request_response_packet_key') in packet_keys
            and entry.get('packet_reuse_status') == 'refresh_in_place'
            and entry.get('delta_token') == 'refresh_fields'
            and public_request_response_packet_delta_ledgers.get('contract', {}).get('public_request_response_packet_delta_fields') == ['public_request_response_packet_delta_key', 'public_request_response_packet_carryforward_profile_key', 'predecessor_public_request_response_packet_key', 'public_request_notice_key', 'notice_kind', 'request_class', 'packet_reuse_status', 'delta_token', 'reused_packet_paths', 'changed_field_family_mode', 'refresh_instructions', 'successor_context_key', 'successor_context_path', 'unchanged_owner_families', 'why']
            and public_request_response_packet_delta_ledgers.get('contract', {}).get('shared_vocabulary_rule')
            and entry.get('reused_packet_paths') == packet_paths_by_key.get(entry.get('predecessor_public_request_response_packet_key'))
            and entry.get('changed_field_family_mode') == 'shared_vocabulary_packet_scoped_instructions'
            and field_families == ['basis_companions', 'selected_entry_excerpt', 'digest_bindings']
            and entry.get('successor_context_key') == 'worked_example_receipt_interlock_public_request_carryforward_envelope'
            and entry.get('successor_context_path') == 'example_public_request_carryforward_envelope.json'
            and entry.get('unchanged_owner_families') == ['selected_owner', 'request_class', 'packet_paths']
        )
    record('public request response packet delta ledgers content', delta_ok, f'delta_ledger_count={len(response_packet_delta_entries)}')

    refresh_notice_ok = len(response_packet_refresh_notice_entries) == len(response_packet_entries)
    delta_keys = {entry.get('public_request_response_packet_delta_key') for entry in response_packet_delta_entries}
    for entry in response_packet_refresh_notice_entries:
        refresh_notice_ok = refresh_notice_ok and (
            public_request_response_packet_refresh_notices.get('public_request_response_packet_refresh_notices_id') == 'worked-example-public-request-response-packet-refresh-notices-v1'
            and public_request_response_packet_refresh_notices.get('successor_public_request_response_packets_id') == public_request_response_packets.get('public_request_response_packets_id')
            and public_request_response_packet_refresh_notices.get('successor_public_request_response_packet_delta_ledgers_id') == public_request_response_packet_delta_ledgers.get('public_request_response_packet_delta_ledgers_id')
            and public_request_response_packet_refresh_notices.get('successor_public_request_carryforward_envelopes_id') == public_request_carryforward_envelope.get('public_request_carryforward_envelopes_id')
            and entry.get('public_request_response_packet_delta_key') in delta_keys
            and entry.get('predecessor_public_request_response_packet_key') in packet_keys
            and entry.get('packet_reuse_status') == 'refresh_in_place'
            and entry.get('delta_token') == 'refresh_fields'
            and entry.get('changed_field_families') == ['basis_companions', 'selected_entry_excerpt', 'digest_bindings']
            and entry.get('unchanged_packet_paths') == packet_paths_by_key.get(entry.get('predecessor_public_request_response_packet_key'))
            and entry.get('reader_pointer_order') == ['example_public_request_response_packet_refresh_notices.json', 'example_public_request_response_packet_delta_ledgers.json', 'example_public_request_response_packet_carryforward_profiles.json', 'example_public_request_response_packets.json']
            and compare_report.get('successor_release_id') in entry.get('refresh_sentence', '')
        )
    record('public request response packet refresh notices content', refresh_notice_ok, f'refresh_notice_count={len(response_packet_refresh_notice_entries)}')

    refresh_notice_normal_form_ok = len(response_packet_refresh_notice_normal_form_entries) == len(response_packet_refresh_notice_entries)
    refresh_notice_keys = {entry.get('public_request_response_packet_refresh_notice_key') for entry in response_packet_refresh_notice_entries}
    for entry in response_packet_refresh_notice_normal_form_entries:
        refresh_notice_normal_form_ok = refresh_notice_normal_form_ok and (
            public_request_response_packet_refresh_notice_normal_forms.get('public_request_response_packet_refresh_notice_normal_forms_id') == 'worked-example-public-request-response-packet-refresh-notice-normal-forms-v1'
            and public_request_response_packet_refresh_notice_normal_forms.get('successor_public_request_response_packet_refresh_notices_id') == public_request_response_packet_refresh_notices.get('public_request_response_packet_refresh_notices_id')
            and public_request_response_packet_refresh_notice_normal_forms.get('successor_public_request_response_packet_delta_ledgers_id') == public_request_response_packet_delta_ledgers.get('public_request_response_packet_delta_ledgers_id')
            and entry.get('emitted_public_request_response_packet_refresh_notice_key') in refresh_notice_keys
            and entry.get('public_request_response_packet_delta_key') in delta_keys
            and entry.get('allowed_delta_tokens') == ['refresh_fields']
            and entry.get('rendered_sentence') in {n.get('refresh_sentence') for n in response_packet_refresh_notice_entries}
        )
    record('public request response packet refresh notice normal forms content', refresh_notice_normal_form_ok, f'refresh_notice_normal_form_count={len(response_packet_refresh_notice_normal_form_entries)}')

    response_packet_refresh_notice_selection_entries = public_request_response_packet_refresh_notice_selections.get('public_request_response_packet_refresh_notice_selections', [])
    refresh_notice_normal_form_keys = {entry.get('public_request_response_packet_refresh_notice_normal_form_key') for entry in response_packet_refresh_notice_normal_form_entries}
    refresh_notice_selection_ok = len(response_packet_refresh_notice_selection_entries) == len(response_packet_refresh_notice_entries)
    for entry in response_packet_refresh_notice_selection_entries:
        refresh_notice_selection_ok = refresh_notice_selection_ok and (
            public_request_response_packet_refresh_notice_selections.get('public_request_response_packet_refresh_notice_selections_id') == 'worked-example-public-request-response-packet-refresh-notice-selections-v1'
            and public_request_response_packet_refresh_notice_selections.get('successor_public_request_response_packet_refresh_notices_id') == public_request_response_packet_refresh_notices.get('public_request_response_packet_refresh_notices_id')
            and public_request_response_packet_refresh_notice_selections.get('successor_public_request_response_packet_refresh_notice_normal_forms_id') == public_request_response_packet_refresh_notice_normal_forms.get('public_request_response_packet_refresh_notice_normal_forms_id')
            and public_request_response_packet_refresh_notice_selections.get('successor_public_request_response_packet_delta_ledgers_id') == public_request_response_packet_delta_ledgers.get('public_request_response_packet_delta_ledgers_id')
            and entry.get('basis_key') in delta_keys
            and entry.get('selected_emitted_public_request_response_packet_refresh_notice_key') in refresh_notice_keys
            and entry.get('selected_public_request_response_packet_refresh_notice_normal_form_key') in refresh_notice_normal_form_keys
            and entry.get('selector_inputs', {}).get('delta_token') == 'refresh_fields'
            and entry.get('rendered_sentence') in {n.get('refresh_sentence') for n in response_packet_refresh_notice_entries}
        )
    record('public request response packet refresh notice selections content', refresh_notice_selection_ok, f'refresh_notice_selection_count={len(response_packet_refresh_notice_selection_entries)}')

    response_packet_refresh_response_menu_entries = public_request_response_packet_refresh_response_menus.get('public_request_response_packet_refresh_response_menus', [])
    refresh_response_menu_ok = len(response_packet_refresh_response_menu_entries) == len(response_packet_refresh_notice_selection_entries)
    packet_keys = {entry.get('public_request_response_packet_key') for entry in response_packet_entries}
    carry_keys = {entry.get('public_request_response_packet_carryforward_profile_key') for entry in response_packet_carryforward_entries}
    expected_refresh_menu_classes = ['packet_membership_check', 'packet_reuse_check', 'packet_delta_check', 'visible_refresh_sentence_check', 'canonical_refresh_family_check', 'refresh_family_choice_check']
    refresh_sentence_by_key = {entry.get('public_request_response_packet_refresh_notice_key'): entry.get('refresh_sentence') for entry in response_packet_refresh_notice_entries}
    for entry in response_packet_refresh_response_menu_entries:
        classes = [e.get('request_class') for e in entry.get('response_entries', [])]
        refresh_response_menu_ok = refresh_response_menu_ok and (
            public_request_response_packet_refresh_response_menus.get('public_request_response_packet_refresh_response_menus_id') == 'worked-example-public-request-response-packet-refresh-response-menus-v1'
            and public_request_response_packet_refresh_response_menus.get('successor_public_request_response_packets_id') == public_request_response_packets.get('public_request_response_packets_id')
            and public_request_response_packet_refresh_response_menus.get('successor_public_request_response_packet_carryforward_profiles_id') == public_request_response_packet_carryforward_profiles.get('public_request_response_packet_carryforward_profiles_id')
            and public_request_response_packet_refresh_response_menus.get('successor_public_request_response_packet_delta_ledgers_id') == public_request_response_packet_delta_ledgers.get('public_request_response_packet_delta_ledgers_id')
            and public_request_response_packet_refresh_response_menus.get('successor_public_request_response_packet_refresh_notices_id') == public_request_response_packet_refresh_notices.get('public_request_response_packet_refresh_notices_id')
            and public_request_response_packet_refresh_response_menus.get('successor_public_request_response_packet_refresh_notice_normal_forms_id') == public_request_response_packet_refresh_notice_normal_forms.get('public_request_response_packet_refresh_notice_normal_forms_id')
            and public_request_response_packet_refresh_response_menus.get('successor_public_request_response_packet_refresh_notice_selections_id') == public_request_response_packet_refresh_notice_selections.get('public_request_response_packet_refresh_notice_selections_id')
            and entry.get('public_request_response_packet_key') in packet_keys
            and entry.get('public_request_response_packet_carryforward_profile_key') in carry_keys
            and entry.get('public_request_response_packet_delta_key') in delta_keys
            and entry.get('public_request_response_packet_refresh_notice_key') in refresh_notice_keys
            and entry.get('selected_public_request_response_packet_refresh_notice_normal_form_key') in refresh_notice_normal_form_keys
            and entry.get('public_request_response_packet_refresh_notice_selection_key') in {e.get('public_request_response_packet_refresh_notice_selection_key') for e in response_packet_refresh_notice_selection_entries}
            and classes == expected_refresh_menu_classes
        )
        if refresh_response_menu_ok:
            basis_notice_key = entry.get('public_request_response_packet_refresh_notice_key')
            refresh_response_menu_ok = refresh_response_menu_ok and any(
                sub.get('request_class') == 'visible_refresh_sentence_check' and sub.get('selected_entry', {}).get('refresh_sentence') == refresh_sentence_by_key.get(basis_notice_key)
                for sub in entry.get('response_entries', [])
            )
    record('public request response packet refresh response menus content', refresh_response_menu_ok, f'refresh_response_menu_count={len(response_packet_refresh_response_menu_entries)}')
    response_packet_refresh_response_packet_entries = public_request_response_packet_refresh_response_packets.get('public_request_response_packet_refresh_response_packets', [])
    refresh_response_packet_keys = {entry.get('public_request_response_packet_refresh_response_packet_key') for entry in response_packet_refresh_response_packet_entries}
    expected_refresh_packet_count = sum(len(entry.get('response_entries', [])) for entry in response_packet_refresh_response_menu_entries)
    refresh_response_packet_ok = (
        public_request_response_packet_refresh_response_packets.get('public_request_response_packet_refresh_response_packets_id') == 'worked-example-public-request-response-packet-refresh-response-packets-v1'
        and public_request_response_packet_refresh_response_packets.get('successor_public_request_response_packet_refresh_response_menus_id') == public_request_response_packet_refresh_response_menus.get('public_request_response_packet_refresh_response_menus_id')
        and len(response_packet_refresh_response_packet_entries) == expected_refresh_packet_count
    )
    menu_by_key = {entry.get('public_request_response_packet_refresh_response_menu_key'): entry for entry in response_packet_refresh_response_menu_entries}
    expected_companions = {
        'packet_membership_check': ['example_public_request_response_packets.json', 'example_public_request_response_packet_refresh_notices.json'],
        'packet_reuse_check': ['example_public_request_response_packets.json', 'example_public_request_response_packet_carryforward_profiles.json', 'example_public_request_response_packet_refresh_notices.json'],
        'packet_delta_check': ['example_public_request_response_packets.json', 'example_public_request_response_packet_carryforward_profiles.json', 'example_public_request_response_packet_delta_ledgers.json', 'example_public_request_response_packet_refresh_notices.json'],
        'visible_refresh_sentence_check': ['example_public_request_response_packet_delta_ledgers.json', 'example_public_request_response_packet_refresh_notices.json'],
        'canonical_refresh_family_check': ['example_public_request_response_packet_delta_ledgers.json', 'example_public_request_response_packet_refresh_notices.json', 'example_public_request_response_packet_refresh_notice_normal_forms.json'],
        'refresh_family_choice_check': ['example_public_request_response_packet_delta_ledgers.json', 'example_public_request_response_packet_refresh_notices.json', 'example_public_request_response_packet_refresh_notice_normal_forms.json', 'example_public_request_response_packet_refresh_notice_selections.json'],
    }
    for entry in response_packet_refresh_response_packet_entries:
        menu_entry = menu_by_key.get(entry.get('public_request_response_packet_refresh_response_menu_key'))
        followup = entry.get('successor_followup_class')
        selected_entry = next((sub for sub in menu_entry.get('response_entries', []) if sub.get('request_class') == followup), None) if menu_entry else None
        refresh_response_packet_ok = refresh_response_packet_ok and bool(
            entry.get('public_request_response_packet_refresh_response_packet_key') in refresh_response_packet_keys
            and menu_entry is not None
            and selected_entry is not None
            and entry.get('selected_object_key') == selected_entry.get('object_key')
            and entry.get('selected_object_kind') == selected_entry.get('object_kind')
            and entry.get('selected_object_path') == selected_entry.get('cite_path')
            and entry.get('selected_entry_excerpt') == selected_entry.get('selected_entry')
            and entry.get('packet_paths') == expected_companions.get(followup)
            and entry.get('validation_capsule_mode') == ('public_only' if not entry.get('required_validation_paths') else 'shared_validation_companions')
            and entry.get('public_request_response_packet_refresh_notice_key') == menu_entry.get('public_request_response_packet_refresh_notice_key')
        )
    record('public request response packet refresh response packets content', refresh_response_packet_ok, f'refresh_response_packet_count={len(response_packet_refresh_response_packet_entries)}; expected={expected_refresh_packet_count}')

    response_packet_refresh_response_packet_closure_entries = public_request_response_packet_refresh_response_packet_closure_verdicts.get('public_request_response_packet_refresh_response_packet_closure_verdicts', [])
    closure_by_packet = {entry.get('public_request_response_packet_refresh_response_packet_key'): entry for entry in response_packet_refresh_response_packet_closure_entries}
    refresh_response_menu_key_lookup = {(entry.get('notice_kind'), entry.get('request_class')): entry.get('public_request_response_packet_refresh_response_menu_key') for entry in response_packet_refresh_response_menu_entries}
    response_packet_carryforward_key_lookup = {(entry.get('notice_kind'), entry.get('request_class')): entry.get('public_request_response_packet_carryforward_profile_key') for entry in response_packet_carryforward_entries}
    refresh_notice_selection_key_lookup = {(entry.get('notice_kind'), entry.get('request_class')): entry.get('public_request_response_packet_refresh_notice_selection_key') for entry in response_packet_refresh_notice_selection_entries}
    closure_ok = (
        public_request_response_packet_refresh_response_packet_closure_verdicts.get('public_request_response_packet_refresh_response_packet_closure_verdicts_id') == 'worked-example-public-request-response-packet-refresh-response-packet-closure-verdicts-v1'
        and public_request_response_packet_refresh_response_packet_closure_verdicts.get('successor_public_request_response_packet_refresh_response_packets_id') == public_request_response_packet_refresh_response_packets.get('public_request_response_packet_refresh_response_packets_id')
        and len(response_packet_refresh_response_packet_closure_entries) == len(response_packet_refresh_response_packet_entries)
    )
    for packet_entry in response_packet_refresh_response_packet_entries:
        closure_entry = closure_by_packet.get(packet_entry.get('public_request_response_packet_refresh_response_packet_key'))
        expected_reopen_owner_map = {
            'followup_taxonomy_expands': {
                'owner_object_kind': 'public_request_response_packet_refresh_response_menu',
                'owner_object_key': refresh_response_menu_key_lookup.get((packet_entry.get('notice_kind'), packet_entry.get('request_class'))),
                'owner_cite_path': 'example_public_request_response_packet_refresh_response_menus.json',
            },
            'packet_reuse_reopens': {
                'owner_object_kind': 'public_request_response_packet_carryforward_profile',
                'owner_object_key': response_packet_carryforward_key_lookup.get((packet_entry.get('notice_kind'), packet_entry.get('request_class'))),
                'owner_cite_path': 'example_public_request_response_packet_carryforward_profiles.json',
            },
            'visible_refresh_sentence_rebinds_to_new_delta_family': {
                'owner_object_kind': 'public_request_response_packet_refresh_notice_selection',
                'owner_object_key': refresh_notice_selection_key_lookup.get((packet_entry.get('notice_kind'), packet_entry.get('request_class'))),
                'owner_cite_path': 'example_public_request_response_packet_refresh_notice_selections.json',
            },
        }
        closure_owner_map = closure_entry.get('reopen_owner_map', {}) if closure_entry else {}
        closure_ok = closure_ok and bool(
            closure_entry is not None
            and closure_entry.get('closure_status') == 'closed_finite_basis'
            and closure_entry.get('selected_object_kind') == packet_entry.get('selected_object_kind')
            and closure_entry.get('selected_object_key') == packet_entry.get('selected_object_key')
            and closure_entry.get('selected_object_path') == packet_entry.get('selected_object_path')
            and closure_entry.get('closure_basis_scope') == 'public_paths_only'
            and closure_entry.get('validation_capsule_mode') == packet_entry.get('validation_capsule_mode')
            and closure_entry.get('closed_public_paths') == packet_entry.get('packet_paths') + packet_entry.get('required_public_paths', [])
            and closure_entry.get('outside_closure_validation_paths') == packet_entry.get('required_validation_paths', [])
            and closure_entry.get('successor_followup_class') == packet_entry.get('successor_followup_class')
            and {k: {kk: vv for kk, vv in (closure_owner_map.get(k) or {}).items() if kk != 'why'} for k in expected_reopen_owner_map} == expected_reopen_owner_map
        )
    record('public request response packet refresh response packet closure verdicts content', closure_ok, f'closure_verdict_count={len(response_packet_refresh_response_packet_closure_entries)}; expected={len(response_packet_refresh_response_packet_entries)}')

    topo = successor_derivation_graph.get('topological_order', [])
    lineage_paths = [entry.get('path') for entry in successor_lineage_notice.get('reader_pointer_order', [])]
    record('derivation graph includes new artifacts', 'example_public_request_status_envelope.json' in topo and 'example_public_request_carryforward_envelope.json' in topo and 'example_public_request_notice.json' in topo and 'example_public_request_notice_normal_forms.json' in topo and 'example_public_request_notice_selections.json' in topo and 'example_public_request_response_menus.json' in topo and 'example_public_request_response_packets.json' in topo and 'example_public_request_response_packet_carryforward_profiles.json' in topo and 'example_public_request_response_packet_delta_ledgers.json' in topo and 'example_public_request_response_packet_refresh_notices.json' in topo and 'example_public_request_response_packet_refresh_notice_normal_forms.json' in topo and 'example_public_request_response_packet_refresh_notice_selections.json' in topo and 'example_public_request_response_packet_refresh_response_menus.json' in topo and 'example_public_request_response_packet_refresh_response_packets.json' in topo and 'example_public_request_response_packet_refresh_response_packet_closure_verdicts.json' in topo and topo.index('example_public_request_status_envelope.json') < topo.index('example_public_request_carryforward_envelope.json') < topo.index('example_public_request_notice.json') < topo.index('example_public_request_notice_normal_forms.json') < topo.index('example_public_request_notice_selections.json') < topo.index('example_public_request_response_menus.json') < topo.index('example_public_request_response_packets.json') < topo.index('example_public_request_response_packet_carryforward_profiles.json') < topo.index('example_public_request_response_packet_delta_ledgers.json') < topo.index('example_public_request_response_packet_refresh_notices.json') < topo.index('example_public_request_response_packet_refresh_notice_normal_forms.json') < topo.index('example_public_request_response_packet_refresh_notice_selections.json') < topo.index('example_public_request_response_packet_refresh_response_menus.json') < topo.index('example_public_request_response_packet_refresh_response_packets.json') < topo.index('example_public_request_response_packet_refresh_response_packet_closure_verdicts.json'), 'topological order includes status then carryforward then notice then notice normal forms then notice selections then response menus then response packets then response-packet carryforward profiles then response-packet delta ledgers then response-packet refresh notices then packet-refresh-notice normal forms then packet-refresh-notice selections then packet-refresh response menus then packet-refresh response packets then packet-refresh response-packet closure verdicts')
    record('lineage pointer order includes new artifacts', 'example_public_request_status_envelope.json' in lineage_paths and 'example_public_request_carryforward_envelope.json' in lineage_paths and 'example_public_request_notice.json' in lineage_paths and 'example_public_request_notice_normal_forms.json' in lineage_paths and 'example_public_request_notice_selections.json' in lineage_paths and 'example_public_request_response_menus.json' in lineage_paths and 'example_public_request_response_packets.json' in lineage_paths and 'example_public_request_response_packet_carryforward_profiles.json' in lineage_paths and 'example_public_request_response_packet_delta_ledgers.json' in lineage_paths and 'example_public_request_response_packet_refresh_notices.json' in lineage_paths and 'example_public_request_response_packet_refresh_notice_normal_forms.json' in lineage_paths and 'example_public_request_response_packet_refresh_notice_selections.json' in lineage_paths and 'example_public_request_response_packet_refresh_response_menus.json' in lineage_paths and 'example_public_request_response_packet_refresh_response_packets.json' in lineage_paths and 'example_public_request_response_packet_refresh_response_packet_closure_verdicts.json' in lineage_paths and lineage_paths.index('example_public_request_status_envelope.json') < lineage_paths.index('example_public_request_carryforward_envelope.json') < lineage_paths.index('example_public_request_notice.json') < lineage_paths.index('example_public_request_notice_normal_forms.json') < lineage_paths.index('example_public_request_notice_selections.json') < lineage_paths.index('example_public_request_response_menus.json') < lineage_paths.index('example_public_request_response_packets.json') < lineage_paths.index('example_public_request_response_packet_carryforward_profiles.json') < lineage_paths.index('example_public_request_response_packet_delta_ledgers.json') < lineage_paths.index('example_public_request_response_packet_refresh_notices.json') < lineage_paths.index('example_public_request_response_packet_refresh_notice_normal_forms.json') < lineage_paths.index('example_public_request_response_packet_refresh_notice_selections.json') < lineage_paths.index('example_public_request_response_packet_refresh_response_menus.json') < lineage_paths.index('example_public_request_response_packet_refresh_response_packets.json') < lineage_paths.index('example_public_request_response_packet_refresh_response_packet_closure_verdicts.json'), 'reader pointer order includes status then carryforward then notice then notice normal forms then notice selections then response menus then response packets then response-packet carryforward profiles then response-packet delta ledgers then response-packet refresh notices then packet-refresh-notice normal forms then packet-refresh-notice selections then packet-refresh response menus then packet-refresh response packets then packet-refresh response-packet closure verdicts')

    record('series spine linkage', series_spine.get('successor_public_request_status_envelopes_id') == public_request_status_envelope.get('public_request_status_envelopes_id') and series_spine.get('successor_public_request_carryforward_envelopes_id') == public_request_carryforward_envelope.get('public_request_carryforward_envelopes_id') and series_spine.get('successor_public_request_notices_id') == public_request_notice.get('public_request_notices_id') and series_spine.get('successor_public_request_notice_normal_forms_id') == public_request_notice_normal_forms.get('public_request_notice_normal_forms_id') and series_spine.get('successor_public_request_notice_selections_id') == public_request_notice_selections.get('public_request_notice_selections_id') and series_spine.get('successor_public_request_response_menus_id') == public_request_response_menus.get('public_request_response_menus_id') and series_spine.get('successor_public_request_response_packets_id') == public_request_response_packets.get('public_request_response_packets_id') and series_spine.get('successor_public_request_response_packet_carryforward_profiles_id') == public_request_response_packet_carryforward_profiles.get('public_request_response_packet_carryforward_profiles_id') and series_spine.get('successor_public_request_response_packet_delta_ledgers_id') == public_request_response_packet_delta_ledgers.get('public_request_response_packet_delta_ledgers_id') and series_spine.get('successor_public_request_response_packet_refresh_notices_id') == public_request_response_packet_refresh_notices.get('public_request_response_packet_refresh_notices_id') and series_spine.get('successor_public_request_response_packet_refresh_notice_normal_forms_id') == public_request_response_packet_refresh_notice_normal_forms.get('public_request_response_packet_refresh_notice_normal_forms_id') and series_spine.get('successor_public_request_response_packet_refresh_notice_selections_id') == public_request_response_packet_refresh_notice_selections.get('public_request_response_packet_refresh_notice_selections_id') and series_spine.get('successor_public_request_response_packet_refresh_response_menus_id') == public_request_response_packet_refresh_response_menus.get('public_request_response_packet_refresh_response_menus_id') and series_spine.get('successor_public_request_response_packet_refresh_response_packets_id') == public_request_response_packet_refresh_response_packets.get('public_request_response_packet_refresh_response_packets_id') and series_spine.get('successor_public_request_response_packet_refresh_response_packet_closure_verdicts_id') == public_request_response_packet_refresh_response_packet_closure_verdicts.get('public_request_response_packet_refresh_response_packet_closure_verdicts_id') and series_spine.get('source_only_request_ladder') == question_routes.get('source_only_request_ladder'), 'series spine points at companion public-request status, carryforward, notice, notice-normal-form, notice-selection, response-menu, response-packet, response-packet-carryforward, response-packet-delta, response-packet-refresh-notice, packet-refresh-notice-normal-form, packet-refresh-notice-selection, packet-refresh-response-menu, and packet-refresh-response-packet owners')

    minimal_bridge_cuts = series_spine.get('minimal_bridge_cuts', [])
    minimal_bridge_index = {entry.get('task_key'): entry for entry in minimal_bridge_cuts}
    expected_cut_tasks = {
        'mechanism_justification': ('series_spine_segment', 'mathematical_root', None, 'example_line_item_owner_map.json'),
        'public_claim_identification': ('series_spine_segment', 'receipt_anchor', None, 'example_receipt.json'),
        'replay_verification': ('series_spine_segment', 'replay_anchor', None, 'example_replay_plans.json'),
        'release_evolution_status': ('series_spine_segment', 'release_anchor', None, 'example_release_spine.json'),
        'answer_side_archive_cut': ('series_spine_segment', 'disclosure_packet_anchor', None, 'example_successor_challenge_answer_disclosure_packets.json'),
        'referee_followup_packaging': ('series_spine_segment', 'review_anchor', None, 'example_successor_challenge_answer_review_menus.json'),
        'source_only_request_promise_and_notice': ('owner_bucket', None, 'paper_level_request_contracts_and_notice_choice', 'example_public_request_notice_selections.json'),
        'bounded_response_packet_and_reuse': ('owner_bucket', None, 'notice_keyed_response_packetization', 'example_public_request_response_packet_delta_ledgers.json'),
        'visible_refresh_notice_choice': ('owner_bucket', None, 'visible_refresh_notice_choice', 'example_public_request_response_packet_refresh_notice_selections.json'),
        'successor_refresh_response_packet_and_closure': ('owner_bucket', None, 'successor_refresh_response_packetization_and_closure', 'example_public_request_response_packet_refresh_response_packet_closure_verdicts.json'),
    }
    minimal_bridge_ok = set(minimal_bridge_index.keys()) == set(expected_cut_tasks.keys())
    for task_key, (stop_kind, spine_segment, bucket_key, artifact) in expected_cut_tasks.items():
        entry = minimal_bridge_index.get(task_key)
        minimal_bridge_ok = minimal_bridge_ok and bool(
            entry is not None
            and entry.get('stop_kind') == stop_kind
            and entry.get('spine_segment') == spine_segment
            and entry.get('bucket_key') == bucket_key
            and entry.get('artifact') == artifact
            and entry.get('canonical_owner')
            and entry.get('question')
        )
    record('series spine minimal bridge cuts', minimal_bridge_ok, f'minimal_bridge_cut_count={len(minimal_bridge_cuts)}; expected={len(expected_cut_tasks)}')

    owner_buckets = series_spine.get('source_only_owner_buckets', [])
    minimal_bridge_stop_rules_ok = all(entry.get('stop_when') and entry.get('widen_only_if') for entry in series_spine.get('minimal_bridge_cuts', []))
    record('series spine minimal bridge stop rules', minimal_bridge_stop_rules_ok, f"minimal_bridge_tasks={[entry.get('task_key') for entry in series_spine.get('minimal_bridge_cuts', [])]}")
    owner_bucket_stop_rules_ok = all(entry.get('stop_when') and entry.get('widen_only_if') for entry in owner_buckets)
    record('series spine owner-bucket stop rules', owner_bucket_stop_rules_ok, f"owner_buckets={[entry.get('bucket_key') for entry in owner_buckets]}")
    owner_bucket_index = {entry.get('bucket_key'): entry for entry in owner_buckets}

    source_only_request_ladder = series_spine.get('source_only_request_ladder', [])
    expected_source_only_ladder = [
        ('request_contract', 'paper_level_request_contracts_and_notice_choice', 'Synthesis~56', 'example_public_request_contracts.json'),
        ('requestable_evidence_class_typing', 'paper_level_request_contracts_and_notice_choice', 'Synthesis~57', 'example_requestable_evidence_classes.json'),
        ('request_fulfillment', 'paper_level_request_contracts_and_notice_choice', 'Synthesis~58', 'example_request_fulfillment_certificates.json'),
        ('request_status', 'paper_level_request_contracts_and_notice_choice', 'Synthesis~59', 'example_public_request_status_envelope.json'),
        ('request_carryforward', 'paper_level_request_contracts_and_notice_choice', 'Synthesis~60', 'example_public_request_carryforward_envelope.json'),
        ('request_notice', 'paper_level_request_contracts_and_notice_choice', 'Synthesis~61', 'example_public_request_notice.json'),
        ('request_notice_normal_form', 'paper_level_request_contracts_and_notice_choice', 'Synthesis~62', 'example_public_request_notice_normal_forms.json'),
        ('request_notice_selection', 'paper_level_request_contracts_and_notice_choice', 'Synthesis~63', 'example_public_request_notice_selections.json'),
        ('response_menu', 'notice_keyed_response_packetization', 'Synthesis~64', 'example_public_request_response_menus.json'),
        ('response_packet', 'notice_keyed_response_packetization', 'Synthesis~65', 'example_public_request_response_packets.json'),
        ('response_packet_carryforward', 'notice_keyed_response_packetization', 'Synthesis~66', 'example_public_request_response_packet_carryforward_profiles.json'),
        ('response_packet_delta', 'notice_keyed_response_packetization', 'Synthesis~67', 'example_public_request_response_packet_delta_ledgers.json'),
        ('refresh_notice', 'visible_refresh_notice_choice', 'Synthesis~68', 'example_public_request_response_packet_refresh_notices.json'),
        ('refresh_notice_normal_form', 'visible_refresh_notice_choice', 'Synthesis~69', 'example_public_request_response_packet_refresh_notice_normal_forms.json'),
        ('refresh_notice_selection', 'visible_refresh_notice_choice', 'Synthesis~70', 'example_public_request_response_packet_refresh_notice_selections.json'),
        ('refresh_response_menu', 'successor_refresh_response_packetization_and_closure', 'Synthesis~71', 'example_public_request_response_packet_refresh_response_menus.json'),
        ('refresh_response_packet', 'successor_refresh_response_packetization_and_closure', 'Synthesis~72', 'example_public_request_response_packet_refresh_response_packets.json'),
        ('refresh_response_packet_closure', 'successor_refresh_response_packetization_and_closure', 'Synthesis~73', 'example_public_request_response_packet_refresh_response_packet_closure_verdicts.json'),
    ]
    source_only_ladder_ok = (
        len(source_only_request_ladder) == len(expected_source_only_ladder)
        and all(entry.get('position') == i + 1 for i, entry in enumerate(source_only_request_ladder))
        and all((entry.get('task_key'), entry.get('bucket_key'), entry.get('note_range'), entry.get('artifact')) == expected_source_only_ladder[i] for i, entry in enumerate(source_only_request_ladder))
        and all(entry.get('canonical_owner') and entry.get('label') and entry.get('question') and entry.get('stop_when') and entry.get('widen_only_if') and entry.get('why') for entry in source_only_request_ladder)
    )
    record('series spine source-only request ladder', source_only_ladder_ok, f"source_only_request_ladder={[entry.get('task_key') for entry in source_only_request_ladder]}")

    question_source_only_ladder_ok = question_routes.get('source_only_request_ladder') == source_only_request_ladder
    record('question routing source-only request ladder mirror', question_source_only_ladder_ok, f"question_source_only_request_ladder={[entry.get('task_key') for entry in question_routes.get('source_only_request_ladder', [])]}")

    def note_range_bounds(note_range: str):
        note_range = note_range or ''
        if not note_range.startswith('Synthesis~'):
            return None
        payload = note_range.split('~', 1)[1]
        if '--' in payload:
            lo, hi = payload.split('--', 1)
        else:
            lo = hi = payload
        try:
            return int(lo), int(hi)
        except ValueError:
            return None

    source_only_ladder_bucket_alignment_ok = all(
        (
            owner_bucket_index.get(entry.get('bucket_key'), {}).get('note_range')
            and entry.get('artifact') in owner_bucket_index.get(entry.get('bucket_key'), {}).get('artifacts', [])
            and note_range_bounds(owner_bucket_index.get(entry.get('bucket_key'), {}).get('note_range')) is not None
            and note_range_bounds(entry.get('note_range')) is not None
            and note_range_bounds(owner_bucket_index.get(entry.get('bucket_key'), {}).get('note_range'))[0]
                <= note_range_bounds(entry.get('note_range'))[0]
                <= note_range_bounds(owner_bucket_index.get(entry.get('bucket_key'), {}).get('note_range'))[1]
        )
        for entry in source_only_request_ladder
    )
    record('source-only request ladder bucket alignment', source_only_ladder_bucket_alignment_ok, 'source-only ladder entries align with their coarse owner buckets')

    expected_owner_buckets = {
        'paper_level_request_contracts_and_notice_choice': {
            'note_range': 'Synthesis~56--63',
            'artifacts': ['example_public_request_contracts.json', 'example_requestable_evidence_classes.json', 'example_request_fulfillment_certificates.json', 'example_public_request_status_envelope.json', 'example_public_request_carryforward_envelope.json', 'example_public_request_notice.json', 'example_public_request_notice_normal_forms.json', 'example_public_request_notice_selections.json'],
        },
        'notice_keyed_response_packetization': {
            'note_range': 'Synthesis~64--67',
            'artifacts': ['example_public_request_response_menus.json', 'example_public_request_response_packets.json', 'example_public_request_response_packet_carryforward_profiles.json', 'example_public_request_response_packet_delta_ledgers.json'],
        },
        'visible_refresh_notice_choice': {
            'note_range': 'Synthesis~68--70',
            'artifacts': ['example_public_request_response_packet_refresh_notices.json', 'example_public_request_response_packet_refresh_notice_normal_forms.json', 'example_public_request_response_packet_refresh_notice_selections.json'],
        },
        'successor_refresh_response_packetization_and_closure': {
            'note_range': 'Synthesis~71--73',
            'artifacts': ['example_public_request_response_packet_refresh_response_menus.json', 'example_public_request_response_packet_refresh_response_packets.json', 'example_public_request_response_packet_refresh_response_packet_closure_verdicts.json'],
        },
    }
    owner_bucket_ok = set(owner_bucket_index.keys()) == set(expected_owner_buckets.keys())
    for bucket_key, spec in expected_owner_buckets.items():
        entry = owner_bucket_index.get(bucket_key)
        owner_bucket_ok = owner_bucket_ok and bool(
            entry is not None
            and entry.get('note_range') == spec['note_range']
            and entry.get('artifacts') == spec['artifacts']
            and entry.get('first_question')
            and entry.get('why')
        )
    record('series spine source-only owner buckets', owner_bucket_ok, f'owner_bucket_count={len(owner_buckets)}; expected={len(expected_owner_buckets)}')

    generic_routes = question_routes.get('generic_question_routes', [])
    generic_route_index = {entry.get('route_key'): entry for entry in generic_routes}
    generic_route_ok = set(generic_route_index.keys()) == set(expected_cut_tasks.keys())
    for task_key, bridge_entry in minimal_bridge_index.items():
        route = generic_route_index.get(task_key)
        generic_route_ok = generic_route_ok and bool(
            route is not None
            and route.get('stop_kind') == bridge_entry.get('stop_kind')
            and route.get('spine_segment') == bridge_entry.get('spine_segment')
            and route.get('bucket_key') == bridge_entry.get('bucket_key')
            and route.get('first_stop_owner') == bridge_entry.get('canonical_owner')
            and route.get('first_stop_artifact') == bridge_entry.get('artifact')
            and route.get('question_examples')
        )
    record('question routing generic routes', generic_route_ok, f'generic_route_count={len(generic_routes)}; expected={len(expected_cut_tasks)}')

    audience_routes = question_routes.get('audience_question_routes', [])
    answer_spines = series_spine.get('answer_spines', [])
    answer_spine_index = {(entry.get('audience'), entry.get('question_key')): entry for entry in answer_spines}
    review_menu_index = {entry.get('answer_review_menu_key'): entry for entry in answer_review_menus.get('answer_review_menus', [])}
    escalation_ladder_index = {entry.get('answer_escalation_ladder_key'): entry for entry in answer_escalation_ladders.get('answer_escalation_ladders', [])}
    publication_profile_index = {entry.get('answer_publication_profile_key'): entry for entry in answer_publication_profiles.get('answer_publication_profiles', [])}
    citation_docket_index = {entry.get('answer_citation_docket_key'): entry for entry in answer_citation_dockets.get('answer_citation_dockets', [])}
    answer_carrier_slot_index = {entry.get('carrier_slot_key'): entry for entry in answer_carrier_slots.get('answer_carrier_slots', [])}
    answer_audit_trail_index = {entry.get('audit_trail_key'): entry for entry in answer_audit_trails.get('answer_audit_trails', [])}
    answer_card_index = {entry.get('answer_card_key'): entry for entry in answer_cards.get('answer_cards', [])}
    sentence_lock_index = {entry.get('lock_key'): entry for entry in sentence_locks.get('locks', [])}
    sentence_lock_posture_ok = all(
        entry.get('comparison_anchor', {}).get('maintenance_posture', {}).get('current_status') == 'carryforward'
        and entry.get('comparison_anchor', {}).get('maintenance_posture', {}).get('recheck_status') == 'refresh_only_after_recheck'
        and entry.get('comparison_anchor', {}).get('maintenance_posture', {}).get('regenerate_status') == 'retire_and_reissue'
        and entry.get('comparison_anchor', {}).get('maintenance_posture', {}).get('why')
        for entry in sentence_locks.get('locks', [])
    ) and sentence_locks.get('lock_contract', {}).get('maintenance_posture_fields') == ['current_status', 'recheck_status', 'regenerate_status', 'why']
    record('sentence lock maintenance posture', sentence_lock_posture_ok, f"lock_count={len(sentence_locks.get('locks', []))}")
    contract_entry = public_request_contracts.get('public_request_contracts', [{}])[0]
    status_token_mode_map = {entry.get('public_request_status_envelope_key'): entry.get('public_request_status_token_mode') for entry in public_request_status_envelope.get('public_request_status_envelopes', [])}
    carryforward_token_mode_map = {entry.get('public_request_carryforward_envelope_key'): entry.get('carryforward_token_mode') for entry in public_request_carryforward_envelope.get('public_request_carryforward_envelopes', [])}
    notice_key_map = {entry.get('notice_kind'): entry.get('public_request_notice_key') for entry in public_request_notice.get('public_request_notices', [])}
    notice_normal_form_map = {entry.get('notice_kind'): entry.get('public_request_notice_normal_form_key') for entry in public_request_notice_normal_forms.get('public_request_notice_normal_forms', [])}
    notice_selection_map = {entry.get('notice_kind'): entry.get('public_request_notice_selection_key') for entry in public_request_notice_selections.get('public_request_notice_selections', [])}
    response_menu_map = {entry.get('notice_kind'): entry.get('public_request_response_menu_key') for entry in public_request_response_menus.get('public_request_response_menus', [])}
    response_menu_followup_class_mode_map = {entry.get('notice_kind'): entry.get('followup_class_vocabulary_mode') for entry in public_request_response_menus.get('public_request_response_menus', [])}
    response_handoff_map = {
        entry.get('notice_kind'): {response_entry.get('request_class'): response_entry.get('selected_entry') for response_entry in entry.get('response_entries', [])}
        for entry in public_request_response_menus.get('public_request_response_menus', [])
    }
    response_owner_map = {
        entry.get('notice_kind'): {
            response_entry.get('request_class'): {
                'owner_object_kind': response_entry.get('object_kind'),
                'owner_object_key': response_entry.get('object_key'),
                'owner_cite_path': response_entry.get('cite_path'),
                'selected_object_kind': ((response_entry.get('selected_entry') or {}) if isinstance(response_entry.get('selected_entry'), dict) else {}).get('object_kind'),
                'selected_object_key': ((response_entry.get('selected_entry') or {}) if isinstance(response_entry.get('selected_entry'), dict) else {}).get('object_key'),
                'why': response_entry.get('why'),
            }
            for response_entry in entry.get('response_entries', [])
        }
        for entry in public_request_response_menus.get('public_request_response_menus', [])
    }
    response_packet_map = {}
    response_packet_scope_mode_map = {}
    response_packet_family_basis_map = {}
    response_packet_support_surface_map = {}
    response_packet_manifest_cut_map = {}
    response_packet_inventory_cut_map = {}
    for packet in public_request_response_packets.get('public_request_response_packets', []):
        response_packet_map.setdefault(packet.get('notice_kind'), {})[packet.get('request_class')] = packet.get('public_request_response_packet_key')
        response_packet_scope_mode_map.setdefault(packet.get('notice_kind'), {})[packet.get('request_class')] = packet.get('packet_scope_mode')
        response_packet_family_basis_map.setdefault(packet.get('notice_kind'), {})[packet.get('request_class')] = extract_packet_family_basis(packet)
        response_packet_support_surface_map.setdefault(packet.get('notice_kind'), {})[packet.get('request_class')] = extract_packet_support_surface(packet)
        response_packet_manifest_cut_map.setdefault(packet.get('notice_kind'), {})[packet.get('request_class')] = extract_packet_manifest_cut(packet, manifest_index, support_manifest.get('manifest_id'))
        response_packet_inventory_cut_map.setdefault(packet.get('notice_kind'), {})[packet.get('request_class')] = extract_packet_inventory_cut(packet, inventory_index, artifact_inventory.get('inventory_id'))
    response_packet_carryforward_profile_map = {}
    response_packet_reuse_status_map = {}
    response_packet_refresh_family_mode_map = {}
    for profile in public_request_response_packet_carryforward_profiles.get('public_request_response_packet_carryforward_profiles', []):
        response_packet_carryforward_profile_map.setdefault(profile.get('notice_kind'), {})[profile.get('request_class')] = profile.get('public_request_response_packet_carryforward_profile_key')
        response_packet_reuse_status_map.setdefault(profile.get('notice_kind'), {})[profile.get('request_class')] = (profile.get('packet_maintenance_posture') or {}).get('current_status')
        response_packet_refresh_family_mode_map.setdefault(profile.get('notice_kind'), {})[profile.get('request_class')] = profile.get('refreshable_field_family_mode')
    response_packet_delta_map = {}
    response_packet_delta_family_mode_map = {}
    for delta in public_request_response_packet_delta_ledgers.get('public_request_response_packet_delta_ledgers', []):
        response_packet_delta_map.setdefault(delta.get('notice_kind'), {})[delta.get('request_class')] = delta.get('public_request_response_packet_delta_key')
        response_packet_delta_family_mode_map.setdefault(delta.get('notice_kind'), {})[delta.get('request_class')] = delta.get('changed_field_family_mode')
    refresh_notice_map = {}
    for notice in public_request_response_packet_refresh_notices.get('public_request_response_packet_refresh_notices', []):
        refresh_notice_map.setdefault(notice.get('notice_kind'), {})[notice.get('request_class')] = notice.get('public_request_response_packet_refresh_notice_key')
    refresh_notice_normal_form_map = {}
    for normal_form in public_request_response_packet_refresh_notice_normal_forms.get('public_request_response_packet_refresh_notice_normal_forms', []):
        refresh_notice_normal_form_map.setdefault(normal_form.get('notice_kind'), {})[normal_form.get('request_class')] = normal_form.get('public_request_response_packet_refresh_notice_normal_form_key')
    refresh_notice_selection_map = {}
    for selection in public_request_response_packet_refresh_notice_selections.get('public_request_response_packet_refresh_notice_selections', []):
        refresh_notice_selection_map.setdefault(selection.get('notice_kind'), {})[selection.get('request_class')] = selection.get('public_request_response_packet_refresh_notice_selection_key')
    refresh_response_menu_map = {}
    for menu in public_request_response_packet_refresh_response_menus.get('public_request_response_packet_refresh_response_menus', []):
        refresh_response_menu_map.setdefault(menu.get('notice_kind'), {})[menu.get('request_class')] = menu.get('public_request_response_packet_refresh_response_menu_key')
    refresh_followup_handoff_map = {}
    refresh_followup_owner_map = {}
    for menu in public_request_response_packet_refresh_response_menus.get('public_request_response_packet_refresh_response_menus', []):
        refresh_followup_handoff_map.setdefault(menu.get('notice_kind'), {})[menu.get('request_class')] = {
            response_entry.get('request_class'): response_entry.get('selected_entry')
            for response_entry in menu.get('response_entries', [])
        }
        refresh_followup_owner_map.setdefault(menu.get('notice_kind'), {})[menu.get('request_class')] = {
            response_entry.get('request_class'): {
                'owner_object_kind': response_entry.get('object_kind'),
                'owner_object_key': response_entry.get('object_key'),
                'owner_cite_path': response_entry.get('cite_path'),
                'selected_object_kind': ((response_entry.get('selected_entry') or {}) if isinstance(response_entry.get('selected_entry'), dict) else {}).get('object_kind'),
                'selected_object_key': ((response_entry.get('selected_entry') or {}) if isinstance(response_entry.get('selected_entry'), dict) else {}).get('object_key'),
                'why': response_entry.get('why'),
            }
            for response_entry in menu.get('response_entries', [])
        }
    refresh_response_packet_map = {}
    refresh_response_packet_family_basis_map = {}
    refresh_response_packet_support_surface_map = {}
    refresh_response_packet_manifest_cut_map = {}
    refresh_response_packet_inventory_cut_map = {}
    refresh_response_packet_validation_mode_map = {}
    for packet in public_request_response_packet_refresh_response_packets.get('public_request_response_packet_refresh_response_packets', []):
        refresh_response_packet_map.setdefault(packet.get('notice_kind'), {}).setdefault(packet.get('request_class'), {})[packet.get('successor_followup_class')] = packet.get('public_request_response_packet_refresh_response_packet_key')
        refresh_response_packet_family_basis_map.setdefault(packet.get('notice_kind'), {}).setdefault(packet.get('request_class'), {})[packet.get('successor_followup_class')] = extract_packet_family_basis(packet)
        refresh_response_packet_support_surface_map.setdefault(packet.get('notice_kind'), {}).setdefault(packet.get('request_class'), {})[packet.get('successor_followup_class')] = extract_packet_support_surface(packet)
        refresh_response_packet_manifest_cut_map.setdefault(packet.get('notice_kind'), {}).setdefault(packet.get('request_class'), {})[packet.get('successor_followup_class')] = extract_packet_manifest_cut(packet, manifest_index, support_manifest.get('manifest_id'))
        refresh_response_packet_inventory_cut_map.setdefault(packet.get('notice_kind'), {}).setdefault(packet.get('request_class'), {})[packet.get('successor_followup_class')] = extract_packet_inventory_cut(packet, inventory_index, artifact_inventory.get('inventory_id'))
        refresh_response_packet_validation_mode_map.setdefault(packet.get('notice_kind'), {}).setdefault(packet.get('request_class'), {})[packet.get('successor_followup_class')] = packet.get('validation_capsule_mode')
    refresh_response_packet_closure_map = {}
    refresh_response_packet_closure_status_map = {}
    refresh_response_packet_closure_scope_map = {}
    refresh_response_packet_reopen_trigger_map = {}
    refresh_response_packet_reopen_owner_map = {}
    for verdict in public_request_response_packet_refresh_response_packet_closure_verdicts.get('public_request_response_packet_refresh_response_packet_closure_verdicts', []):
        refresh_response_packet_closure_map.setdefault(verdict.get('notice_kind'), {}).setdefault(verdict.get('request_class'), {})[verdict.get('successor_followup_class')] = verdict.get('public_request_response_packet_refresh_response_packet_closure_verdict_key')
        refresh_response_packet_closure_status_map.setdefault(verdict.get('notice_kind'), {}).setdefault(verdict.get('request_class'), {})[verdict.get('successor_followup_class')] = verdict.get('closure_status')
        refresh_response_packet_closure_scope_map.setdefault(verdict.get('notice_kind'), {}).setdefault(verdict.get('request_class'), {})[verdict.get('successor_followup_class')] = verdict.get('closure_basis_scope')
        refresh_response_packet_reopen_trigger_map.setdefault(verdict.get('notice_kind'), {}).setdefault(verdict.get('request_class'), {})[verdict.get('successor_followup_class')] = verdict.get('reopen_trigger_tokens', [])
        refresh_response_packet_reopen_owner_map.setdefault(verdict.get('notice_kind'), {}).setdefault(verdict.get('request_class'), {})[verdict.get('successor_followup_class')] = verdict.get('reopen_owner_map', {})
    disclosure_packet_index = {entry.get('answer_disclosure_packet_key'): entry for entry in answer_disclosure_packets.get('answer_disclosure_packets', [])}
    disclosure_packet_support_surface_map = {key: extract_disclosure_packet_support_surface(packet) for key, packet in disclosure_packet_index.items()}
    disclosure_packet_manifest_cut_map = {key: extract_disclosure_packet_manifest_cut(packet, manifest_index, support_manifest.get('manifest_id')) for key, packet in disclosure_packet_index.items()}
    disclosure_packet_inventory_cut_map = {key: extract_disclosure_packet_inventory_cut(packet, inventory_index, artifact_inventory.get('inventory_id')) for key, packet in disclosure_packet_index.items()}
    audience_route_ok = len(audience_routes) == len(answer_spines)
    audience_route_failures = []
    challenge_route_index = {(entry.get('audience'), entry.get('question_key')): entry for entry in challenge_routes.get('routes', [])}
    stop_profile_keys = {entry.get('stop_profile_key') for entry in challenge_stop_profiles.get('profiles', [])}
    branch_route_keys = {entry.get('route_key') for entry in challenge_branches.get('branches', [])}
    for route in audience_routes:
        key = (route.get('audience'), route.get('question_key'))
        answer = answer_spine_index.get(key)
        review_menu = review_menu_index.get(route.get('answer_review_menu_key'))
        challenge_route = challenge_route_index.get(key)
        publication_profile = publication_profile_index.get(route.get('publication_profile_key'))
        docket = citation_docket_index.get(route.get('citation_docket_key'))
        answer_carrier_slot = answer_carrier_slot_index.get(route.get('answer_carrier_slot_key'))
        answer_audit_trail = answer_audit_trail_index.get(route.get('answer_audit_trail_key'))
        answer_card = answer_card_index.get(route.get('answer_card_key'))
        sentence_lock = sentence_lock_index.get(route.get('sentence_lock_key'))
        default_inline_profile = (sentence_lock or {}).get('comparison_anchor', {}).get('default_inline_profile', {})
        default_visible_fields = next((entry.get('visible_fields', []) for entry in (sentence_lock or {}).get('comparison_anchor', {}).get('inline_provenance_profiles', []) if entry.get('profile_key') == default_inline_profile.get('profile_key')), [])
        expected_budget_map = {
            'brief_inline': (publication_profile or {}).get('default_inline_entry'),
            'expanded_inline': (publication_profile or {}).get('expanded_inline_entry'),
            'exact_location': (publication_profile or {}).get('exact_location_entry'),
            'full_audit': (publication_profile or {}).get('full_audit_entry'),
        }
        review_entry_index = {entry.get('request_class'): entry.get('selected_entry') for entry in (review_menu or {}).get('review_entries', [])}
        ladder = escalation_ladder_index.get(route.get('escalation_ladder_key'))
        answer_escalation_step_mode_map = {entry.get('step_key'): entry.get('escalation_step_vocabulary_mode') for entry in (ladder or {}).get('ordered_steps', [])}
        review_owner_index = {
            entry.get('request_class'): {
                'owner_object_kind': entry.get('object_kind'),
                'owner_object_key': entry.get('object_key'),
                'owner_cite_path': entry.get('cite_path'),
                'selected_object_kind': (entry.get('selected_entry') or {}).get('object_kind'),
                'selected_object_key': (entry.get('selected_entry') or {}).get('object_key'),
                'why': entry.get('why'),
            }
            for entry in (review_menu or {}).get('review_entries', [])
        }
        release_stage_vocabulary_mode_map = {entry.get('stage'): entry.get('release_stage_vocabulary_mode') for entry in release_stage_order if entry.get('stage') in route.get('release_stage_families', [])}
        route_checks = [
            ('answer_spine_present', answer is not None),
            ('review_menu_present', review_menu is not None),
            ('challenge_route_present', challenge_route is not None),
            ('publication_profile_present', publication_profile is not None),
            ('citation_docket_present', docket is not None),
            ('answer_carrier_slot_present', answer_carrier_slot is not None),
            ('answer_audit_trail_present', answer_audit_trail is not None),
            ('answer_card_present', answer_card is not None),
            ('sentence_lock_present', sentence_lock is not None),
            ('challenge_route_key', route.get('challenge_route_key') == (answer or {}).get('challenge_route_key') == (challenge_route or {}).get('route_key')),
            ('stop_profile_key', route.get('stop_profile_key') == (answer or {}).get('stop_profile_key') == (challenge_route or {}).get('stop_profile_key')),
            ('stop_profile_member', route.get('stop_profile_key') in stop_profile_keys),
            ('branch_route_member', route.get('challenge_route_key') in branch_route_keys),
            ('minimal_public_anchor_path', route.get('minimal_public_anchor_path') == (answer or {}).get('start_path')),
            ('sentence_family', route.get('sentence_family') == (answer or {}).get('sentence_family') == (answer_card or {}).get('sentence_family')),
            ('answer_card_key', route.get('answer_card_key') == (answer or {}).get('answer_card_key') == (publication_profile or {}).get('answer_card_key') == (answer_card or {}).get('answer_card_key')),
            ('sentence_lock_key', route.get('sentence_lock_key') == (answer or {}).get('sentence_lock_key') == (answer_card or {}).get('sentence_lock_key') == (sentence_lock or {}).get('lock_key')),
            ('sentence_reuse_status', route.get('sentence_reuse_status') == (answer or {}).get('sentence_reuse_status') == (publication_profile or {}).get('sentence_reuse_status') == (answer_card or {}).get('sentence_reuse_status') == ((sentence_lock or {}).get('comparison_anchor') or {}).get('maintenance_posture', {}).get('current_status')),
            ('default_inline_profile_key', route.get('default_inline_profile_key') == (answer or {}).get('default_inline_profile_key') == default_inline_profile.get('profile_key')),
            ('default_visible_provenance_fields', route.get('default_visible_provenance_fields') == (answer or {}).get('default_visible_provenance_fields') == default_visible_fields == (answer_card or {}).get('visible_provenance_fields')),
            ('publication_profile_key', route.get('publication_profile_key') == (answer or {}).get('publication_profile_key') == (publication_profile or {}).get('answer_publication_profile_key')),
            ('publication_budget_map', route.get('publication_budget_map') == (answer or {}).get('publication_budget_map') == expected_budget_map),
            ('answer_escalation_step_mode_map', route.get('answer_escalation_step_mode_map') == (answer or {}).get('answer_escalation_step_mode_map') == answer_escalation_step_mode_map),
            ('brief_inline_entry', route.get('publication_budget_map', {}).get('brief_inline') == review_entry_index.get('brief_inline_check')),
            ('expanded_inline_entry', route.get('publication_budget_map', {}).get('expanded_inline') == review_entry_index.get('expanded_inline_check')),
            ('exact_location_entry', route.get('publication_budget_map', {}).get('exact_location') == review_entry_index.get('exact_location_check')),
            ('full_audit_entry', route.get('publication_budget_map', {}).get('full_audit') == review_entry_index.get('full_audit_check')),
            ('request_class_handoff_map', route.get('request_class_handoff_map') == (answer or {}).get('request_class_handoff_map') == review_entry_index),
            ('request_class_owner_map', route.get('request_class_owner_map') == (answer or {}).get('request_class_owner_map') == review_owner_index),
            ('release_obligation_profile_id', route.get('release_obligation_profile_id') == (answer or {}).get('release_obligation_profile_id') == release_obligation_profile.get('obligation_profile_id')),
            ('release_closure_ledger_id', route.get('release_closure_ledger_id') == (answer or {}).get('release_closure_ledger_id') == release_closure_ledger.get('closure_ledger_id')),
            ('publication_closure_verdict_id', route.get('publication_closure_verdict_id') == (answer or {}).get('publication_closure_verdict_id') == publication_closure_verdict.get('closure_verdict_id')),
            ('publication_closure_status', route.get('publication_closure_status') == (answer or {}).get('publication_closure_status') == publication_closure_verdict.get('closure_status')),
            ('successor_status_envelope_id', route.get('successor_status_envelope_id') == (answer or {}).get('successor_status_envelope_id') == successor_status_envelope.get('status_envelope_id')),
            ('successor_public_status_token', route.get('successor_public_status_token') == (answer or {}).get('successor_public_status_token') == successor_status_envelope.get('public_status')),
            ('successor_lineage_notice_id', route.get('successor_lineage_notice_id') == (answer or {}).get('successor_lineage_notice_id') == successor_lineage_notice.get('notice_id')),
            ('public_request_contract_key', route.get('public_request_contract_key') == (answer or {}).get('public_request_contract_key') == contract_entry.get('public_request_contract_key')),
            ('source_only_public_anchor_family_mode_map', route.get('source_only_public_anchor_family_mode_map') == (answer or {}).get('source_only_public_anchor_family_mode_map') == public_anchor_family_mode_map),
            ('source_only_request_fulfillment_certificate_keys', route.get('source_only_request_fulfillment_certificate_keys') == (answer or {}).get('source_only_request_fulfillment_certificate_keys') == [entry.get('request_fulfillment_certificate_key') for entry in request_fulfillment_certificates.get('request_fulfillment_certificates', [])]),
            ('source_only_family_completion_map', route.get('source_only_family_completion_map') == (answer or {}).get('source_only_family_completion_map') == {entry.get('family_key'): entry.get('completion_verdict') for entry in request_fulfillment_certificates.get('request_fulfillment_certificates', [])}),
            ('source_only_family_completion_mode_map', route.get('source_only_family_completion_mode_map') == (answer or {}).get('source_only_family_completion_mode_map') == {entry.get('family_key'): entry.get('completion_verdict_mode') for entry in request_fulfillment_certificates.get('request_fulfillment_certificates', [])}),
            ('source_only_evidence_class_mode_map', route.get('source_only_evidence_class_mode_map') == (answer or {}).get('source_only_evidence_class_mode_map') == {entry.get('evidence_class_key'): entry.get('evidence_class_vocabulary_mode') for entry in requestable_evidence_classes.get('evidence_classes', [])}),
            ('source_only_status_envelope_key', route.get('source_only_status_envelope_key') == (answer or {}).get('source_only_status_envelope_key') == 'worked_example_receipt_interlock_public_request_status_envelope'),
            ('source_only_status_token', route.get('source_only_status_token') == (answer or {}).get('source_only_status_token') == 'complete'),
            ('source_only_status_token_mode_map', route.get('source_only_status_token_mode_map') == (answer or {}).get('source_only_status_token_mode_map') == status_token_mode_map),
            ('source_only_carryforward_envelope_key', route.get('source_only_carryforward_envelope_key') == (answer or {}).get('source_only_carryforward_envelope_key') == 'worked_example_receipt_interlock_public_request_carryforward_envelope'),
            ('source_only_carryforward_token', route.get('source_only_carryforward_token') == (answer or {}).get('source_only_carryforward_token') == 'preserved_complete'),
            ('source_only_carryforward_token_mode_map', route.get('source_only_carryforward_token_mode_map') == (answer or {}).get('source_only_carryforward_token_mode_map') == carryforward_token_mode_map),
            ('source_only_notice_key_map', route.get('source_only_notice_key_map') == (answer or {}).get('source_only_notice_key_map') == notice_key_map),
            ('source_only_notice_normal_form_map', route.get('source_only_notice_normal_form_map') == (answer or {}).get('source_only_notice_normal_form_map') == notice_normal_form_map),
            ('source_only_notice_selection_keys', route.get('source_only_notice_selection_keys') == (answer or {}).get('source_only_notice_selection_keys') == notice_selection_map),
            ('source_only_response_menu_keys', route.get('source_only_response_menu_keys') == (answer or {}).get('source_only_response_menu_keys') == response_menu_map),
            ('source_only_response_menu_followup_class_mode_map', route.get('source_only_response_menu_followup_class_mode_map') == (answer or {}).get('source_only_response_menu_followup_class_mode_map') == response_menu_followup_class_mode_map),
            ('source_only_request_class_handoff_map', route.get('source_only_request_class_handoff_map') == (answer or {}).get('source_only_request_class_handoff_map') == response_handoff_map),
            ('source_only_request_class_owner_map', route.get('source_only_request_class_owner_map') == (answer or {}).get('source_only_request_class_owner_map') == response_owner_map),
            ('source_only_response_packet_map', route.get('source_only_response_packet_map') == (answer or {}).get('source_only_response_packet_map') == response_packet_map),
            ('source_only_response_packet_scope_mode_map', route.get('source_only_response_packet_scope_mode_map') == (answer or {}).get('source_only_response_packet_scope_mode_map') == response_packet_scope_mode_map),
            ('source_only_response_packet_family_basis_map', route.get('source_only_response_packet_family_basis_map') == (answer or {}).get('source_only_response_packet_family_basis_map') == response_packet_family_basis_map),
            ('source_only_response_packet_support_surface_map', route.get('source_only_response_packet_support_surface_map') == (answer or {}).get('source_only_response_packet_support_surface_map') == response_packet_support_surface_map),
            ('source_only_response_packet_manifest_cut_map', route.get('source_only_response_packet_manifest_cut_map') == (answer or {}).get('source_only_response_packet_manifest_cut_map') == response_packet_manifest_cut_map),
            ('source_only_response_packet_inventory_cut_map', route.get('source_only_response_packet_inventory_cut_map') == (answer or {}).get('source_only_response_packet_inventory_cut_map') == response_packet_inventory_cut_map),
            ('source_only_response_packet_carryforward_profile_map', route.get('source_only_response_packet_carryforward_profile_map') == (answer or {}).get('source_only_response_packet_carryforward_profile_map') == response_packet_carryforward_profile_map),
            ('source_only_response_packet_reuse_status_map', route.get('source_only_response_packet_reuse_status_map') == (answer or {}).get('source_only_response_packet_reuse_status_map') == response_packet_reuse_status_map),
            ('source_only_response_packet_refresh_family_mode_map', route.get('source_only_response_packet_refresh_family_mode_map') == (answer or {}).get('source_only_response_packet_refresh_family_mode_map') == response_packet_refresh_family_mode_map),
            ('source_only_response_packet_delta_map', route.get('source_only_response_packet_delta_map') == (answer or {}).get('source_only_response_packet_delta_map') == response_packet_delta_map),
            ('source_only_response_packet_delta_family_mode_map', route.get('source_only_response_packet_delta_family_mode_map') == (answer or {}).get('source_only_response_packet_delta_family_mode_map') == response_packet_delta_family_mode_map),
            ('source_only_refresh_notice_map', route.get('source_only_refresh_notice_map') == (answer or {}).get('source_only_refresh_notice_map') == refresh_notice_map),
            ('source_only_refresh_notice_normal_form_map', route.get('source_only_refresh_notice_normal_form_map') == (answer or {}).get('source_only_refresh_notice_normal_form_map') == refresh_notice_normal_form_map),
            ('source_only_refresh_notice_selection_map', route.get('source_only_refresh_notice_selection_map') == (answer or {}).get('source_only_refresh_notice_selection_map') == refresh_notice_selection_map),
            ('source_only_refresh_response_menu_map', route.get('source_only_refresh_response_menu_map') == (answer or {}).get('source_only_refresh_response_menu_map') == refresh_response_menu_map),
            ('source_only_refresh_followup_handoff_map', route.get('source_only_refresh_followup_handoff_map') == (answer or {}).get('source_only_refresh_followup_handoff_map') == refresh_followup_handoff_map),
            ('source_only_refresh_followup_owner_map', route.get('source_only_refresh_followup_owner_map') == (answer or {}).get('source_only_refresh_followup_owner_map') == refresh_followup_owner_map),
            ('source_only_refresh_response_packet_map', route.get('source_only_refresh_response_packet_map') == (answer or {}).get('source_only_refresh_response_packet_map') == refresh_response_packet_map),
            ('source_only_refresh_response_packet_family_basis_map', route.get('source_only_refresh_response_packet_family_basis_map') == (answer or {}).get('source_only_refresh_response_packet_family_basis_map') == refresh_response_packet_family_basis_map),
            ('source_only_refresh_response_packet_support_surface_map', route.get('source_only_refresh_response_packet_support_surface_map') == (answer or {}).get('source_only_refresh_response_packet_support_surface_map') == refresh_response_packet_support_surface_map),
            ('source_only_refresh_response_packet_manifest_cut_map', route.get('source_only_refresh_response_packet_manifest_cut_map') == (answer or {}).get('source_only_refresh_response_packet_manifest_cut_map') == refresh_response_packet_manifest_cut_map),
            ('source_only_refresh_response_packet_inventory_cut_map', route.get('source_only_refresh_response_packet_inventory_cut_map') == (answer or {}).get('source_only_refresh_response_packet_inventory_cut_map') == refresh_response_packet_inventory_cut_map),
            ('source_only_refresh_response_packet_validation_mode_map', route.get('source_only_refresh_response_packet_validation_mode_map') == (answer or {}).get('source_only_refresh_response_packet_validation_mode_map') == refresh_response_packet_validation_mode_map),
            ('source_only_refresh_response_packet_closure_map', route.get('source_only_refresh_response_packet_closure_map') == (answer or {}).get('source_only_refresh_response_packet_closure_map') == refresh_response_packet_closure_map),
            ('source_only_refresh_response_packet_closure_status_map', route.get('source_only_refresh_response_packet_closure_status_map') == (answer or {}).get('source_only_refresh_response_packet_closure_status_map') == refresh_response_packet_closure_status_map),
            ('source_only_refresh_response_packet_closure_scope_map', route.get('source_only_refresh_response_packet_closure_scope_map') == (answer or {}).get('source_only_refresh_response_packet_closure_scope_map') == refresh_response_packet_closure_scope_map),
            ('source_only_refresh_response_packet_reopen_trigger_map', route.get('source_only_refresh_response_packet_reopen_trigger_map') == (answer or {}).get('source_only_refresh_response_packet_reopen_trigger_map') == refresh_response_packet_reopen_trigger_map),
            ('source_only_refresh_response_packet_reopen_owner_map', route.get('source_only_refresh_response_packet_reopen_owner_map') == (answer or {}).get('source_only_refresh_response_packet_reopen_owner_map') == refresh_response_packet_reopen_owner_map),
            ('source_only_request_ladder', route.get('source_only_request_ladder') == (answer or {}).get('source_only_request_ladder') == question_routes.get('source_only_request_ladder')),
            ('citation_docket_key', route.get('citation_docket_key') == (answer or {}).get('citation_docket_key') == (review_menu or {}).get('answer_citation_docket_key') == (docket or {}).get('answer_citation_docket_key')),
            ('answer_carrier_slot_key', route.get('answer_carrier_slot_key') == (answer or {}).get('answer_carrier_slot_key') == (((docket or {}).get('exact_carrier_entry') or {}).get('object_key')) == (answer_carrier_slot or {}).get('carrier_slot_key')),
            ('answer_audit_trail_key', route.get('answer_audit_trail_key') == (answer or {}).get('answer_audit_trail_key') == (((docket or {}).get('full_audit_entry') or {}).get('object_key')) == (answer_audit_trail or {}).get('audit_trail_key')),
            ('carrier_slot_from_docket_matches_card', (answer_carrier_slot or {}).get('answer_card_key') == route.get('answer_card_key') == (answer_card or {}).get('answer_card_key')),
            ('audit_trail_starts_at_carrier_slot', (answer_audit_trail or {}).get('answer_carrier_slot_key') == route.get('answer_carrier_slot_key')),
            ('audit_trail_matches_card', (answer_audit_trail or {}).get('answer_card_key') == route.get('answer_card_key')),
            ('disclosure_packet_key', route.get('disclosure_packet_key') == (answer or {}).get('disclosure_packet_key') == (review_menu or {}).get('answer_disclosure_packet_key')),
            ('disclosure_packet_support_surface', route.get('disclosure_packet_support_surface') == (answer or {}).get('disclosure_packet_support_surface') == disclosure_packet_support_surface_map.get(route.get('disclosure_packet_key'))),
            ('disclosure_packet_manifest_cut', route.get('disclosure_packet_manifest_cut') == (answer or {}).get('disclosure_packet_manifest_cut') == disclosure_packet_manifest_cut_map.get(route.get('disclosure_packet_key'))),
            ('disclosure_packet_inventory_cut', route.get('disclosure_packet_inventory_cut') == (answer or {}).get('disclosure_packet_inventory_cut') == disclosure_packet_inventory_cut_map.get(route.get('disclosure_packet_key'))),
            ('evidence_class_keys', route.get('evidence_class_keys') == (answer or {}).get('evidence_class_keys')),
            ('escalation_ladder_key', route.get('escalation_ladder_key') == (answer or {}).get('escalation_ladder_key') == (review_menu or {}).get('answer_escalation_ladder_key')),
            ('supporting_line_item_names', route.get('supporting_line_item_names') == (answer or {}).get('supporting_line_item_names')),
            ('release_stage_families', route.get('release_stage_families') == (answer or {}).get('release_stage_families')),
            ('release_stage_vocabulary_mode_map', route.get('release_stage_vocabulary_mode_map') == (answer or {}).get('release_stage_vocabulary_mode_map') == release_stage_vocabulary_mode_map),
            ('available_request_classes', route.get('available_request_classes') == [entry.get('request_class') for entry in (review_menu or {}).get('review_entries', [])]),
            ('why', bool(route.get('why'))),
        ]
        route_ok = all(ok for _, ok in route_checks)
        audience_route_ok = audience_route_ok and route_ok
        if not route_ok:
            audience_route_failures.append({
                'audience': route.get('audience'),
                'question_key': route.get('question_key'),
                'failed_checks': [name for name, ok in route_checks if not ok],
            })
    route_detail = f'audience_route_count={len(audience_routes)}; expected={len(answer_spines)}'
    if audience_route_failures:
        route_detail += f'; failures={audience_route_failures}'
    record('question routing audience routes', audience_route_ok, route_detail)

    question_contract = question_routes.get('contract', {})
    record('question routing contract fields', bool(question_routes.get('question_routes_id') == 'worked-example-question-routes-v1' and question_routes.get('series_spine_id') == series_spine.get('series_spine_id') and question_routes.get('successor_challenge_answer_review_menus_id') == answer_review_menus.get('challenge_answer_review_menus_id') and question_routes.get('successor_challenge_routes_id') == challenge_routes.get('challenge_routes_id') and question_routes.get('successor_challenge_stop_profiles_id') == challenge_stop_profiles.get('challenge_stop_profiles_id') and question_routes.get('successor_challenge_branches_id') == challenge_branches.get('challenge_branches_id') and question_routes.get('requestable_evidence_classes_id') == requestable_evidence_classes.get('requestable_evidence_classes_id') and question_routes.get('source_only_request_ladder') == series_spine.get('source_only_request_ladder') and question_contract.get('generic_question_route_fields') == ['route_key', 'question_examples', 'stop_kind', 'spine_segment', 'bucket_key', 'first_stop_owner', 'first_stop_artifact', 'next_route_keys_if_scope_widens', 'why'] and question_contract.get('audience_question_route_fields') == ['route_key', 'audience', 'question_key', 'challenge_route_key', 'stop_profile_key', 'minimal_public_anchor_path', 'sentence_family', 'answer_card_key', 'sentence_lock_key', 'sentence_reuse_status', 'default_inline_profile_key', 'default_visible_provenance_fields', 'answer_review_menu_key', 'publication_profile_key', 'publication_budget_map', 'answer_review_request_class_mode_map', 'answer_escalation_step_mode_map', 'paired_terminal_answer_reopen_request_classes', 'paired_terminal_cutover_mode', 'paired_terminal_widen_condition', 'paired_terminal_request_reopen_triggers', 'request_class_handoff_map', 'request_class_owner_map', 'release_obligation_profile_id', 'release_closure_ledger_id', 'publication_closure_verdict_id', 'publication_closure_status', 'successor_status_envelope_id', 'successor_public_status_token', 'successor_lineage_notice_id', 'public_request_contract_key', 'source_only_public_anchor_family_mode_map', 'source_only_request_fulfillment_certificate_keys', 'source_only_family_completion_map', 'source_only_family_completion_mode_map', 'source_only_evidence_class_mode_map', 'source_only_status_envelope_key', 'source_only_status_token', 'source_only_status_token_mode_map', 'source_only_carryforward_envelope_key', 'source_only_carryforward_token', 'source_only_carryforward_token_mode_map', 'source_only_notice_key_map', 'source_only_notice_normal_form_map', 'source_only_notice_selection_keys', 'source_only_response_menu_keys', 'source_only_response_menu_followup_class_mode_map', 'source_only_request_class_handoff_map', 'source_only_request_class_owner_map', 'source_only_response_packet_map', 'source_only_response_packet_scope_mode_map', 'source_only_response_packet_family_basis_map', 'source_only_response_packet_support_surface_map', 'source_only_response_packet_manifest_cut_map', 'source_only_response_packet_inventory_cut_map', 'source_only_response_packet_carryforward_profile_map', 'source_only_response_packet_reuse_status_map', 'source_only_response_packet_refresh_family_mode_map', 'source_only_response_packet_delta_map', 'source_only_response_packet_delta_family_mode_map', 'source_only_refresh_notice_map', 'source_only_refresh_notice_normal_form_map', 'source_only_refresh_notice_selection_map', 'source_only_refresh_response_menu_map', 'source_only_refresh_followup_handoff_map', 'source_only_refresh_followup_owner_map', 'source_only_refresh_response_packet_map', 'source_only_refresh_response_packet_family_basis_map', 'source_only_refresh_response_packet_support_surface_map', 'source_only_refresh_response_packet_manifest_cut_map', 'source_only_refresh_response_packet_inventory_cut_map', 'source_only_refresh_response_packet_validation_mode_map', 'source_only_refresh_response_packet_closure_map', 'source_only_refresh_response_packet_closure_status_map', 'source_only_refresh_response_packet_closure_scope_map', 'source_only_refresh_response_packet_reopen_trigger_map', 'source_only_refresh_response_packet_reopen_owner_map', 'source_only_request_ladder', 'citation_docket_key', 'answer_carrier_slot_key', 'answer_audit_trail_key', 'disclosure_packet_key', 'disclosure_packet_support_surface', 'disclosure_packet_manifest_cut', 'disclosure_packet_inventory_cut', 'evidence_class_keys', 'escalation_ladder_key', 'supporting_line_item_names', 'release_stage_families', 'release_stage_vocabulary_mode_map', 'available_request_classes', 'why'] and question_contract.get('stable_ladder_fields') == ['position', 'task_key', 'spine_segment', 'label', 'canonical_owner', 'artifact', 'question', 'stop_when', 'widen_only_if', 'why'] and question_contract.get('source_only_request_ladder_fields') == ['position', 'task_key', 'bucket_key', 'label', 'canonical_owner', 'note_range', 'artifact', 'question', 'stop_when', 'widen_only_if', 'why'] and question_contract.get('widening_rule') and question_contract.get('public_anchor_rule') and question_contract.get('audience_stop_rule')), 'question routing catalog links the series spine, stop profiles, answer cards, sentence locks, publication-budget maps, six-class request handoff maps, mirrored answer-review request-class / answer-escalation-step / release-stage vocabulary posture maps, six-class request owner maps, route-side release-obligation-profile / release-closure-ledger / publication-closure-verdict / successor-status-envelope / successor-lineage-notice bindings plus the imported public-status token, the paper-level source-only request contract, route-side public-anchor-family-vocabulary / fulfillment-certificate / family-completion-vocabulary / evidence-class-vocabulary / status-token / carryforward-token bridges plus status-token / carryforward-token vocabulary maps, source-only notice / canonical-notice-family / notice-selection surfaces, notice-keyed source-only response menus plus source-only response-menu followup-vocabulary maps, source-only request-class handoff / owner maps, exact bounded source-only response packets plus response-packet-scope / packet-family-basis / packet-support-surface / packet-manifest-cut / packet-inventory-cut maps together with packet-reuse / packet-family-mode / packet-delta / packet-delta-family-mode / refresh-family-mode bridges, successor refresh-notice / canonical-refresh-family / refresh-notice-selection / refresh-response-menu / successor-followup handoff / owner maps, exact successor packets plus successor-packet-family-basis / successor-packet-support-surface / successor-packet-manifest-cut / successor-packet-inventory-cut / successor-packet-validation-posture / closure / closure-status / closure-scope / reopen-trigger / reopen-owner maps, citation dockets, answer carrier slots, answer audit trails, disclosure packets plus disclosure-packet support-surface / manifest-cut / inventory-cut bindings, escalation ladders, branch maps, review menus, evidence classes, and both route-field contracts')

    contract = series_spine.get('series_spine_contract', {})
    record('series spine contract fields', bool(contract.get('answer_spine_fields') == ['audience', 'question_key', 'challenge_route_key', 'stop_profile_key', 'answer_review_menu_key', 'start_path', 'sentence_family', 'answer_card_key', 'sentence_lock_key', 'sentence_reuse_status', 'default_inline_profile_key', 'default_visible_provenance_fields', 'supporting_line_item_names', 'release_stage_families', 'release_stage_vocabulary_mode_map', 'publication_profile_key', 'publication_budget_map', 'answer_review_request_class_mode_map', 'answer_escalation_step_mode_map', 'paired_terminal_answer_reopen_request_classes', 'paired_terminal_cutover_mode', 'paired_terminal_widen_condition', 'paired_terminal_request_reopen_triggers', 'request_class_handoff_map', 'request_class_owner_map', 'release_obligation_profile_id', 'release_closure_ledger_id', 'publication_closure_verdict_id', 'publication_closure_status', 'successor_status_envelope_id', 'successor_public_status_token', 'successor_lineage_notice_id', 'public_request_contract_key', 'source_only_public_anchor_family_mode_map', 'source_only_request_fulfillment_certificate_keys', 'source_only_family_completion_map', 'source_only_family_completion_mode_map', 'source_only_evidence_class_mode_map', 'source_only_status_envelope_key', 'source_only_status_token', 'source_only_status_token_mode_map', 'source_only_carryforward_envelope_key', 'source_only_carryforward_token', 'source_only_carryforward_token_mode_map', 'source_only_notice_key_map', 'source_only_notice_normal_form_map', 'source_only_notice_selection_keys', 'source_only_response_menu_keys', 'source_only_response_menu_followup_class_mode_map', 'source_only_request_class_handoff_map', 'source_only_request_class_owner_map', 'source_only_response_packet_map', 'source_only_response_packet_scope_mode_map', 'source_only_response_packet_family_basis_map', 'source_only_response_packet_support_surface_map', 'source_only_response_packet_manifest_cut_map', 'source_only_response_packet_inventory_cut_map', 'source_only_response_packet_carryforward_profile_map', 'source_only_response_packet_reuse_status_map', 'source_only_response_packet_refresh_family_mode_map', 'source_only_response_packet_delta_map', 'source_only_response_packet_delta_family_mode_map', 'source_only_refresh_notice_map', 'source_only_refresh_notice_normal_form_map', 'source_only_refresh_notice_selection_map', 'source_only_refresh_response_menu_map', 'source_only_refresh_followup_handoff_map', 'source_only_refresh_followup_owner_map', 'source_only_refresh_response_packet_map', 'source_only_refresh_response_packet_family_basis_map', 'source_only_refresh_response_packet_support_surface_map', 'source_only_refresh_response_packet_manifest_cut_map', 'source_only_refresh_response_packet_inventory_cut_map', 'source_only_refresh_response_packet_validation_mode_map', 'source_only_refresh_response_packet_closure_map', 'source_only_refresh_response_packet_closure_status_map', 'source_only_refresh_response_packet_closure_scope_map', 'source_only_refresh_response_packet_reopen_trigger_map', 'source_only_refresh_response_packet_reopen_owner_map', 'source_only_request_ladder', 'citation_docket_key', 'answer_carrier_slot_key', 'answer_audit_trail_key', 'disclosure_packet_key', 'disclosure_packet_support_surface', 'disclosure_packet_manifest_cut', 'disclosure_packet_inventory_cut', 'evidence_class_keys', 'escalation_ladder_key', 'why'] and contract.get('stable_ladder_fields') == ['position', 'task_key', 'spine_segment', 'label', 'canonical_owner', 'artifact', 'question', 'stop_when', 'widen_only_if', 'why'] and contract.get('source_only_request_ladder_fields') == ['position', 'task_key', 'bucket_key', 'label', 'canonical_owner', 'note_range', 'artifact', 'question', 'stop_when', 'widen_only_if', 'why'] and contract.get('minimal_bridge_cut_fields') == ['task_key', 'stop_kind', 'spine_segment', 'bucket_key', 'canonical_owner', 'artifact', 'question', 'stop_when', 'widen_only_if', 'why'] and contract.get('source_only_owner_bucket_fields') == ['bucket_key', 'note_range', 'first_question', 'artifacts', 'stop_when', 'widen_only_if', 'why'] and contract.get('adjacent_owner_bucket_rule')), 'series spine contract names answer-spine fields, publication-budget-map fields, six-class request handoff-map fields, mirrored answer-escalation-step vocabulary fields, mirrored release-stage-vocabulary posture-map fields, six-class request owner-map fields, release-obligation / closure-ledger / closure-verdict / status-envelope / lineage-notice bridge fields, public-request-contract / public-anchor-family-vocabulary / fulfillment-certificate / family-completion-vocabulary / evidence-class-vocabulary / status-token / carryforward-token / status-token-vocabulary / carryforward-token-vocabulary / notice / canonical-notice-family / notice-normal-form / notice-selection / response-menu / response-menu-followup-vocabulary / source-only request-class handoff / source-only request-class owner / bounded-response-packet / response-packet-scope / packet-family-basis / packet-support-surface / packet-manifest-cut / packet-inventory-cut / packet-carryforward / packet-family-mode / packet-delta / delta-family-mode / refresh-notice / canonical-refresh-family / refresh-normal-form / refresh-selection / refresh-response-menu / successor-followup handoff / successor-followup owner / successor-packet / successor-packet-family-basis / successor-packet-support-surface / successor-packet-manifest-cut / successor-packet-inventory-cut / successor-packet-validation-posture / closure / closure-status / closure-scope / reopen-trigger / reopen-owner fields, disclosure-packet support-surface / disclosure-packet manifest-cut / disclosure-packet inventory-cut fields, minimal-bridge-cut fields, source-only-owner-bucket fields, and the adjacent owner-bucket stop rule plus the explicit source-only-request-ladder field contract')

    ok = all(c['ok'] for c in checks)
    report = {
        'validation_report_id': 'worked-example-validation-report-v1',
        'claim_id': claim_id,
        'release_id': RELEASE_ID,
        'note_version': NOTE_VERSION,
        'support_manifest_id': support_manifest.get('manifest_id'),
        'artifact_inventory_id': artifact_inventory.get('inventory_id'),
        'ok': ok,
        'checks': checks,
        'warnings': [],
        'note': 'Validation report for the worked example support bundle, including the theorem-to-review series-spine routing cuts, question-routing catalog, emitted-answer / sentence-lock reuse bindings, route-side citation-docket / disclosure-packet / disclosure-packet support-surface / disclosure-packet manifest-cut / disclosure-packet inventory-cut / escalation-ladder bindings, imported six-class request handoff maps, route-side release-obligation-profile / release-closure-ledger / publication-closure-verdict / successor-status-envelope / successor-lineage-notice bindings plus the imported public-status token, source-only owner buckets, the route-side notice / canonical-notice-family / notice-normal-form / selection bridge, the route-side successor packet-reuse posture / delta / refresh-notice / canonical-refresh-family / refresh-normal-form / refresh-selection / refresh-response-menu / successor-packet / successor-packet-family-basis / successor-packet-support-surface / successor-packet-manifest-cut / successor-packet-inventory-cut / successor-packet-validation-posture / closure maps, and the public-request fulfillment-certificate, family-completion-vocabulary, status, carryforward, status-token-vocabulary, carryforward-token-vocabulary, notice, notice-normal-form, notice-selection, response-menu, response-packet, response-packet-carryforward, response-packet-delta, packet-refresh-notice, packet-refresh-notice-normal-form, packet-refresh-notice-selection, packet-refresh-response-menu, packet-refresh-response-packet, packet-refresh-response-packet-closure-verdict, and route-level response-menu followup-vocabulary / response-packet-scope / packet-reuse posture / closure-status / closure-scope / reopen-trigger / packet-manifest-cut / packet-inventory-cut / disclosure-packet manifest-cut / disclosure-packet inventory-cut bindings now mirrored beside the explicit source-only successor-packet validation-posture bridge, including the shared-versus-family-local source-only evidence split, the mirrored source-only evidence-class-vocabulary map, the mirrored source-only response-menu-followup-vocabulary and response-packet-scope maps, the mirrored source-only packet-family-mode and packet-delta-family-mode maps, explicit stop-here / widen-only-if bridge rules for both the release-spine stage-order rows, the six-stop stable ladder, and the eighteen-step source-only request ladder, the answer-side disclosure-packet first-stop route, the mirrored source-only packet reuse status map, the mirrored visible-refresh branch closure status map, the mirrored visible-refresh branch closure scope map, the mirrored visible-refresh reopen-trigger map, the mirrored visible-refresh reopen-owner map, and the README current-cut guard.'
    }
    (ART / 'example_validation_report.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    if not ok:
        failed = [c['name'] for c in checks if not c['ok']]
        print('validation failed:', '; '.join(failed), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
