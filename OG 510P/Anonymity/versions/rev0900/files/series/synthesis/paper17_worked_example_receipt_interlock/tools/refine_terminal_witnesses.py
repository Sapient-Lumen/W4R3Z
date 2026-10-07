#!/usr/bin/env python3
import gzip
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts'
TERMINAL_ID = 'worked-example-successor-challenge-terminal-witnesses-v1'
COVERAGE_WITNESS_PACKS_ID = 'worked-example-successor-challenge-coverage-witness-packs-v1'
COVERAGE_WITNESS_SLICES_ID = 'worked-example-successor-challenge-coverage-witness-slices-v1'
COVERAGE_WITNESS_CORES_ID = 'worked-example-successor-challenge-coverage-witness-cores-v1'
ANSWER_CAPSULES_ID = 'worked-example-successor-challenge-answer-capsules-v1'
ANSWER_SHEETS_ID = 'worked-example-successor-challenge-answer-sheets-v1'
ANSWER_CARDS_ID = 'worked-example-successor-challenge-answer-cards-v1'
ANSWER_CARRIER_SLOTS_ID = 'worked-example-successor-challenge-answer-carrier-slots-v1'
ANSWER_AUDIT_TRAILS_ID = 'worked-example-successor-challenge-answer-audit-trails-v1'
ANSWER_CITATION_DOCKETS_ID = 'worked-example-successor-challenge-answer-citation-dockets-v1'
ANSWER_PUBLICATION_PROFILES_ID = 'worked-example-successor-challenge-answer-publication-profiles-v1'
ANSWER_DISCLOSURE_PACKETS_ID = 'worked-example-successor-challenge-answer-disclosure-packets-v1'
ANSWER_ESCALATION_LADDERS_ID = 'worked-example-successor-challenge-answer-escalation-ladders-v1'
ANSWER_REVIEW_MENUS_ID = 'worked-example-successor-challenge-answer-review-menus-v1'
PUBLIC_REQUEST_CONTRACTS_ID = 'worked-example-public-request-contracts-v1'
REQUESTABLE_EVIDENCE_CLASSES_ID = 'worked-example-requestable-evidence-classes-v1'
REQUEST_FULFILLMENT_CERTIFICATES_ID = 'worked-example-request-fulfillment-certificates-v1'
PUBLIC_REQUEST_STATUS_ENVELOPES_ID = 'worked-example-public-request-status-envelopes-v1'
PUBLIC_REQUEST_CARRYFORWARD_ENVELOPES_ID = 'worked-example-public-request-carryforward-envelopes-v1'
PUBLIC_REQUEST_NOTICES_ID = 'worked-example-public-request-notices-v1'
PUBLIC_REQUEST_NOTICE_NORMAL_FORMS_ID = 'worked-example-public-request-notice-normal-forms-v1'
PUBLIC_REQUEST_NOTICE_SELECTIONS_ID = 'worked-example-public-request-notice-selections-v1'
PUBLIC_REQUEST_RESPONSE_MENUS_ID = 'worked-example-public-request-response-menus-v1'
PUBLIC_REQUEST_RESPONSE_PACKETS_ID = 'worked-example-public-request-response-packets-v1'
PUBLIC_REQUEST_RESPONSE_PACKET_CARRYFORWARD_PROFILES_ID = 'worked-example-public-request-response-packet-carryforward-profiles-v1'
PUBLIC_REQUEST_RESPONSE_PACKET_DELTA_LEDGERS_ID = 'worked-example-public-request-response-packet-delta-ledgers-v1'
PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_NOTICES_ID = 'worked-example-public-request-response-packet-refresh-notices-v1'
PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_NOTICE_NORMAL_FORMS_ID = 'worked-example-public-request-response-packet-refresh-notice-normal-forms-v1'
PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_NOTICE_SELECTIONS_ID = 'worked-example-public-request-response-packet-refresh-notice-selections-v1'
PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_RESPONSE_MENUS_ID = 'worked-example-public-request-response-packet-refresh-response-menus-v1'
PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_RESPONSE_PACKETS_ID = 'worked-example-public-request-response-packet-refresh-response-packets-v1'
PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_RESPONSE_PACKET_CLOSURE_VERDICTS_ID = 'worked-example-public-request-response-packet-refresh-response-packet-closure-verdicts-v1'
SERIES_SPINE_ID = 'worked-example-series-spine-v1'
QUESTION_ROUTES_ID = 'worked-example-question-routes-v1'
POINTER_FORMAT = 'worked-example-json-payload-pointer-v1'
OFFLOADED_JSON_ARTIFACTS = {
    'example_public_request_response_packet_refresh_response_menus.json',
    'example_public_request_response_packet_refresh_response_packet_closure_verdicts.json',
    'example_public_request_response_packet_refresh_response_packets.json',
    'example_question_routes.json',
    'example_series_spine.json',
    'example_successor_challenge_answer_review_menus.json',
    'example_verifier_report.json',
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def logical_artifact_bytes(name: str) -> bytes:
    """Read logical JSON bytes through a deterministic payload pointer."""
    path = ART / name
    data = path.read_bytes()
    try:
        pointer = json.loads(data)
    except Exception:
        return data
    if not (isinstance(pointer, dict) and pointer.get('offloaded_payload_pointer') is True):
        return data
    if pointer.get('pointer_format') != POINTER_FORMAT or pointer.get('logical_path') != name:
        raise ValueError(f'offloaded payload pointer identity mismatch for {name}')
    payload = (ART / str(pointer.get('payload_path', ''))).read_bytes()
    if sha256_bytes(payload) != pointer.get('payload_sha256'):
        raise ValueError(f'offloaded payload storage digest mismatch for {name}')
    if pointer.get('encoding') != 'gzip-json-utf8-mtime0':
        raise ValueError(f'unsupported offloaded payload encoding for {name}')
    logical = gzip.decompress(payload)
    if sha256_bytes(logical) != pointer.get('logical_sha256'):
        raise ValueError(f'offloaded payload logical digest mismatch for {name}')
    if len(logical) != int(pointer.get('logical_bytes', -1)):
        raise ValueError(f'offloaded payload logical byte count mismatch for {name}')
    return logical


def deterministic_gzip(data: bytes) -> bytes:
    buffer = io.BytesIO()
    with gzip.GzipFile(filename='', mode='wb', fileobj=buffer, compresslevel=9, mtime=0) as handle:
        handle.write(data)
    return buffer.getvalue()


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
            if resolved.parent == ART.resolve() and resolved.suffix == '.json':
                return {'path': path, 'sha256': sha256_bytes(logical_artifact_bytes(resolved.name))}
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

def read_json(name: str):
    return json.loads(logical_artifact_bytes(name))


# These generated support artifacts are very large machine surfaces.  Keep
# human-scale JSON pretty-printed, but write the high-volume routing/spine
# payloads in canonical compact form so fixed-point rebuilds do not recreate
# megabytes of whitespace-only archive mass.
COMPACT_JSON_ARTIFACTS = {
    'example_public_request_response_packet_refresh_response_menus.json',
    'example_public_request_response_packet_refresh_response_packet_closure_verdicts.json',
    'example_public_request_response_packet_refresh_response_packets.json',
    'example_question_routes.json',
    'example_series_spine.json',
}


def json_payload(name: str, obj) -> str:
    if name in COMPACT_JSON_ARTIFACTS:
        return json.dumps(obj, sort_keys=True, separators=(',', ':')) + '\n'
    return json.dumps(obj, indent=2, sort_keys=True) + '\n'


def write_json(name: str, obj):
    data = json_payload(name, obj).encode('utf-8')
    logical_sha = sha256_bytes(data)
    if name in OFFLOADED_JSON_ARTIFACTS:
        payload_dir = ART / 'offloaded_payloads'
        payload_dir.mkdir(exist_ok=True)
        payload_rel = f'offloaded_payloads/{name}.gz'
        payload = deterministic_gzip(data)
        (ART / payload_rel).write_bytes(payload)
        pointer = {
            'encoding': 'gzip-json-utf8-mtime0',
            'logical_bytes': len(data),
            'logical_path': name,
            'logical_sha256': logical_sha,
            'offloaded_payload_pointer': True,
            'payload_bytes': len(payload),
            'payload_path': payload_rel,
            'payload_sha256': sha256_bytes(payload),
            'pointer_format': POINTER_FORMAT,
            'publication_authorized': False,
            'storage_reason': 'Paper17 high-volume generated JSON is kept out of the hot edit path while preserving the original logical byte digest for validator and support-manifest checks.',
        }
        (ART / name).write_text(json.dumps(pointer, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    else:
        (ART / name).write_bytes(data)
    return logical_sha


def manifest_entry(path, sha):
    if path.startswith('../'):
        base = 'paper_root'
        repo_rel = (ROOT / path[3:]).relative_to(ROOT.parents[2]).as_posix()
    else:
        base = 'artifact_root'
        repo_rel = (ART / path).relative_to(ROOT.parents[2]).as_posix()
    return {'path': path, 'base': base, 'repo_relative_path': repo_rel, 'sha256': sha}


def upsert_manifest_entry(files, path, sha):
    row = manifest_entry(path, sha)
    for entry in files:
        if entry.get('path') == path:
            entry.update(row)
            return
    files.append(row)


def decorate_payload_pointer_manifest(manifest):
    rows = [
        row for row in manifest.get('files', [])
        if not (isinstance(row, dict) and str(row.get('path', '')).startswith('offloaded_payloads/'))
    ]
    by_path = {str(row.get('path')): row for row in rows if isinstance(row, dict)}
    summaries = []
    for name in sorted(OFFLOADED_JSON_ARTIFACTS):
        pointer_path = ART / name
        if not pointer_path.exists():
            continue
        try:
            pointer = json.loads(pointer_path.read_text(encoding='utf-8'))
        except Exception:
            continue
        if not (isinstance(pointer, dict) and pointer.get('offloaded_payload_pointer') is True and pointer.get('pointer_format') == POINTER_FORMAT):
            continue
        payload_rel = str(pointer['payload_path'])
        logical_row = by_path.get(name)
        if logical_row is None:
            logical_row = manifest_entry(name, str(pointer['logical_sha256']))
            rows.append(logical_row)
            by_path[name] = logical_row
        logical_row.update({
            'sha256': pointer['logical_sha256'],
            'logical_bytes': pointer['logical_bytes'],
            'payload_pointer_format': POINTER_FORMAT,
            'storage_path': payload_rel,
            'storage_bytes': pointer['payload_bytes'],
            'storage_sha256': pointer['payload_sha256'],
        })
        payload_row = manifest_entry(payload_rel, str(pointer['payload_sha256']))
        payload_row.update({
            'logical_bytes': pointer['logical_bytes'],
            'logical_path': name,
            'logical_sha256': pointer['logical_sha256'],
            'payload_pointer_format': POINTER_FORMAT,
            'role': f'offloaded gzip payload for logical artifact {name}',
        })
        rows.append(payload_row)
        summaries.append({
            'byte_reduction_on_hot_path': int(pointer['logical_bytes']) - pointer_path.stat().st_size,
            'logical_bytes': pointer['logical_bytes'],
            'logical_path': name,
            'logical_sha256': pointer['logical_sha256'],
            'payload_bytes': pointer['payload_bytes'],
            'payload_path': payload_rel,
            'payload_sha256': pointer['payload_sha256'],
        })
    manifest['files'] = sorted(rows, key=lambda row: str(row.get('path', '')))
    manifest['payload_pointer_policy'] = {
        'format': POINTER_FORMAT,
        'logical_digest_rule': 'For pointer rows, the file row sha256 remains the SHA-256 of the decompressed logical JSON bytes, not the small pointer file.',
        'publication_authorized': False,
        'storage_digest_rule': 'Payload files are listed separately with their gzip byte SHA-256.',
    }
    manifest['offloaded_payload_summary'] = sorted(summaries, key=lambda row: (-int(row['byte_reduction_on_hot_path']), row['logical_path']))


def ensure_inventory_entry(inv, path, role, consumed_by):
    for group in inv.get('groups', []):
        for entry in group.get('entries', []):
            if entry.get('path') == path:
                entry['role'] = role
                entry['consumed_by'] = consumed_by
                return
    target = next((g for g in inv.get('groups', []) if g.get('group') == 'guard_and_compare_adjuncts'), None)
    if target is None:
        return
    target.setdefault('entries', []).append({'path': path, 'role': role, 'consumed_by': consumed_by})
    target['entries'] = sorted(target['entries'], key=lambda x: x['path'])


def insert_pointer_after(paths, pointer, after_path):
    seq = [p.get('path') for p in paths]
    if pointer['path'] in seq:
        return paths
    if after_path in seq:
        paths.insert(seq.index(after_path) + 1, pointer)
    else:
        paths.append(pointer)
    return paths


def insert_topo_after(topo, item, after_item):
    if item in topo:
        return topo
    if after_item in topo:
        topo.insert(topo.index(after_item) + 1, item)
    else:
        topo.append(item)
    return topo


def main() -> None:
    compare_report = read_json('example_compare_report.json')
    lineage = read_json('example_successor_lineage_notice.json')
    graph = read_json('example_successor_derivation_graph.json')
    coverage = read_json('example_successor_challenge_coverage.json')
    surface_hooks = read_json('example_successor_challenge_surface_hooks.json')
    stop_profiles = read_json('example_successor_challenge_stop_profiles.json')
    routes = read_json('example_successor_challenge_routes.json')
    branches = read_json('example_successor_challenge_branches.json')
    normal_form = read_json('example_successor_normal_form.json')
    support_manifest = read_json('support_manifest.json')
    support_manifest_index = {entry['path']: {'path': entry['path'], 'sha256': entry['sha256']} for entry in support_manifest.get('files', [])}
    inventory = read_json('example_artifact_inventory.json')
    inventory_index = {entry['path']: {**entry, 'group': group.get('group'), 'visibility': group.get('visibility')} for group in inventory.get('groups', []) for entry in group.get('entries', [])}
    successor_continuity_verdict = read_json('example_successor_continuity_verdict.json')
    publication_closure_verdict = read_json('example_publication_closure_verdict.json')
    obligation_profile = read_json('example_release_obligation_profile.json')
    successor_status_envelope = read_json('example_successor_status_envelope.json')
    quote_map = read_json('example_successor_quote_map.json')
    sentence_locks = read_json('example_successor_sentence_locks.json')
    closure_ledger = read_json('example_release_closure_ledger.json')
    clause_pack = read_json('example_successor_clause_pack.json')
    line_item_owner_map = read_json('example_line_item_owner_map.json')
    release_spine = read_json('example_release_spine.json')
    replay_plans = read_json('example_replay_plans.json')
    support_bundle_map = read_json('example_support_bundle_map.json')

    terminal_witnesses = {
        'challenge_terminal_witnesses_id': TERMINAL_ID,
        'claim_id': coverage['claim_id'],
        'base_release_id': coverage['base_release_id'],
        'release_id': coverage['release_id'],
        'successor_release_id': coverage['successor_release_id'],
        'compare_profile_id': coverage['compare_profile_id'],
        'compare_report_id': coverage['compare_report_id'],
        'successor_normal_form_id': coverage['successor_normal_form_id'],
        'successor_challenge_stop_profiles_id': coverage['successor_challenge_stop_profiles_id'],
        'successor_challenge_branches_id': coverage['successor_challenge_branches_id'],
        'successor_challenge_coverage_id': coverage['challenge_coverage_id'],
        'successor_challenge_surface_hooks_id': surface_hooks['challenge_surface_hooks_id'],
        'successor_challenge_coverage_witness_slices_id': COVERAGE_WITNESS_SLICES_ID,
        'note_version': coverage['note_version'],
        'terminal_witness_contract': {
            'terminal_witness_fields': ['terminal_witness_key', 'sentence_family', 'normal_form_example_key', 'piece_key', 'witness_mode', 'linked_surface_hook_keys', 'required_branch_keys', 'terminal_target_keys', 'approved_terminal_fields', 'why'],
            'witness_mode_values': ['surface', 'support_only'],
            'surface_link_rule': 'If witness_mode is surface, every listed surface hook key must exist in the companion surface-hook ledger for the same sentence family and piece.',
            'branch_rule': 'Every listed branch key must witness the same route-plus-piece pair and terminate at one of the approved terminal fields named here.',
            'normal_form_target_rule': 'If witness_mode is surface, every listed terminal target key must exist in the companion downstream normal form for the same sentence family and piece.',
            'support_only_rule': 'If witness_mode is support_only, linked_surface_hook_keys and terminal_target_keys must both be empty even though approved terminal fields remain mandatory.',
            'stop_profile_rule': 'Approved terminal fields named here must belong to the companion stop profile for the same question family and piece.'
        },
        'terminal_witnesses': [
            {
                'terminal_witness_key': 'public_status_sentence_continuity_piece_terminal',
                'sentence_family': 'public_status_sentence',
                'normal_form_example_key': 'public_status_sentence',
                'piece_key': 'continuity_piece',
                'witness_mode': 'surface',
                'linked_surface_hook_keys': ['public_status_sentence_continuity_piece_surface'],
                'required_branch_keys': ['release_note_public_status_sentence_continuity_piece', 'referee_public_status_sentence_continuity_piece'],
                'terminal_target_keys': ['continuity_decision_target'],
                'approved_terminal_fields': [{'path': 'example_successor_continuity_verdict.json', 'field': 'continuity_decision'}],
                'why': 'The continuity half of the public wrapper terminates at the certified-interface continuity token.'
            },
            {
                'terminal_witness_key': 'public_status_sentence_closure_piece_terminal',
                'sentence_family': 'public_status_sentence',
                'normal_form_example_key': 'public_status_sentence',
                'piece_key': 'closure_piece',
                'witness_mode': 'surface',
                'linked_surface_hook_keys': ['public_status_sentence_closure_piece_surface'],
                'required_branch_keys': ['release_note_public_status_sentence_closure_piece', 'referee_public_status_sentence_closure_piece'],
                'terminal_target_keys': ['closure_status_target'],
                'approved_terminal_fields': [{'path': 'example_publication_closure_verdict.json', 'field': 'closure_status'}],
                'why': 'The closure half of the public wrapper terminates at the package-closure token.'
            },
            {
                'terminal_witness_key': 'compact_numeric_diff_diff_delta_piece_terminal',
                'sentence_family': 'compact_numeric_diff',
                'normal_form_example_key': 'compact_numeric_diff',
                'piece_key': 'diff_delta_piece',
                'witness_mode': 'surface',
                'linked_surface_hook_keys': ['compact_numeric_diff_diff_delta_piece_surface'],
                'required_branch_keys': ['release_note_compact_diff_diff_delta_piece', 'auditor_compact_diff_diff_delta_piece'],
                'terminal_target_keys': ['numeric_delta_target'],
                'approved_terminal_fields': [{'path': 'example_compare_report.json', 'field': 'observed_diffs'}],
                'why': 'The compact diff numeric piece terminates at the compare-report delta field.'
            },
            {
                'terminal_witness_key': 'compact_numeric_diff_changed_family_piece_terminal',
                'sentence_family': 'compact_numeric_diff',
                'normal_form_example_key': 'compact_numeric_diff',
                'piece_key': 'changed_family_piece',
                'witness_mode': 'surface',
                'linked_surface_hook_keys': ['compact_numeric_diff_changed_family_piece_surface'],
                'required_branch_keys': ['release_note_compact_diff_changed_family_piece', 'auditor_compact_diff_changed_family_piece'],
                'terminal_target_keys': ['changed_family_target'],
                'approved_terminal_fields': [{'path': 'example_successor_continuity_verdict.json', 'field': 'changed_line_items'}],
                'why': 'The changed-family piece terminates at the narrow changed-line-items slice even though its surface spans are shared with numeric deltas.'
            },
            {
                'terminal_witness_key': 'compact_numeric_diff_recompute_piece_terminal',
                'sentence_family': 'compact_numeric_diff',
                'normal_form_example_key': 'compact_numeric_diff',
                'piece_key': 'recompute_piece',
                'witness_mode': 'support_only',
                'linked_surface_hook_keys': [],
                'required_branch_keys': ['release_note_compact_diff_recompute_piece', 'auditor_compact_diff_recompute_piece'],
                'terminal_target_keys': [],
                'approved_terminal_fields': [{'path': 'example_verifier_report.json', 'field': 'recomputed'}],
                'why': 'The recomputation witness remains off-surface but still has one exact terminal owner.'
            }
        ],
        'note': 'Derived terminal-witness ledger for one concrete successor comparison. It says which narrow terminal targets and approved stop fields belong to each piece hook, keeping terminal ownership separate from both audience coverage and surface realization.'
    }

    compare_report['successor_challenge_terminal_witnesses_id'] = TERMINAL_ID
    compare_report['successor_challenge_coverage_witness_cores_id'] = COVERAGE_WITNESS_CORES_ID
    compare_report['successor_challenge_coverage_witness_packs_id'] = COVERAGE_WITNESS_PACKS_ID
    compare_report['successor_challenge_coverage_witness_slices_id'] = COVERAGE_WITNESS_SLICES_ID
    compare_report['successor_challenge_answer_capsules_id'] = ANSWER_CAPSULES_ID
    compare_report['successor_challenge_answer_sheets_id'] = ANSWER_SHEETS_ID
    compare_report['successor_challenge_answer_cards_id'] = ANSWER_CARDS_ID
    compare_report['successor_challenge_answer_carrier_slots_id'] = ANSWER_CARRIER_SLOTS_ID
    compare_report['successor_challenge_answer_audit_trails_id'] = ANSWER_AUDIT_TRAILS_ID
    compare_report['successor_challenge_answer_citation_dockets_id'] = ANSWER_CITATION_DOCKETS_ID
    compare_report['successor_challenge_answer_publication_profiles_id'] = ANSWER_PUBLICATION_PROFILES_ID
    compare_report['successor_challenge_answer_disclosure_packets_id'] = ANSWER_DISCLOSURE_PACKETS_ID
    compare_report['successor_challenge_answer_escalation_ladders_id'] = ANSWER_ESCALATION_LADDERS_ID
    compare_report['successor_challenge_answer_review_menus_id'] = ANSWER_REVIEW_MENUS_ID
    compare_report['successor_public_request_contracts_id'] = PUBLIC_REQUEST_CONTRACTS_ID
    compare_report['successor_request_fulfillment_certificates_id'] = REQUEST_FULFILLMENT_CERTIFICATES_ID
    compare_report['successor_public_request_status_envelopes_id'] = PUBLIC_REQUEST_STATUS_ENVELOPES_ID
    compare_report['successor_public_request_carryforward_envelopes_id'] = PUBLIC_REQUEST_CARRYFORWARD_ENVELOPES_ID
    compare_report['successor_public_request_notice_normal_forms_id'] = PUBLIC_REQUEST_NOTICE_NORMAL_FORMS_ID
    compare_report['successor_public_request_notice_selections_id'] = PUBLIC_REQUEST_NOTICE_SELECTIONS_ID
    compare_report['successor_public_request_response_menus_id'] = PUBLIC_REQUEST_RESPONSE_MENUS_ID
    compare_report['successor_public_request_response_packets_id'] = PUBLIC_REQUEST_RESPONSE_PACKETS_ID
    compare_report['successor_public_request_response_packet_carryforward_profiles_id'] = PUBLIC_REQUEST_RESPONSE_PACKET_CARRYFORWARD_PROFILES_ID
    compare_report['successor_public_request_response_packet_delta_ledgers_id'] = PUBLIC_REQUEST_RESPONSE_PACKET_DELTA_LEDGERS_ID
    compare_report['successor_public_request_response_packet_refresh_notices_id'] = PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_NOTICES_ID
    compare_report['successor_public_request_response_packet_refresh_notice_normal_forms_id'] = PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_NOTICE_NORMAL_FORMS_ID
    compare_report['successor_public_request_response_packet_refresh_notice_selections_id'] = PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_NOTICE_SELECTIONS_ID
    compare_report['successor_public_request_response_packet_refresh_response_menus_id'] = PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_RESPONSE_MENUS_ID
    compare_report['successor_public_request_response_packet_refresh_response_packets_id'] = PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_RESPONSE_PACKETS_ID
    compare_report['successor_public_request_response_packet_refresh_response_packet_closure_verdicts_id'] = PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_RESPONSE_PACKET_CLOSURE_VERDICTS_ID

    coverage['successor_challenge_terminal_witnesses_id'] = TERMINAL_ID
    coverage['successor_challenge_coverage_witness_cores_id'] = COVERAGE_WITNESS_CORES_ID
    coverage['successor_challenge_coverage_witness_packs_id'] = COVERAGE_WITNESS_PACKS_ID
    coverage['successor_challenge_coverage_witness_slices_id'] = COVERAGE_WITNESS_SLICES_ID
    coverage['coverage_contract'] = {
        'sentence_family_fields': ['sentence_family', 'normal_form_example_key', 'question_key', 'required_audiences', 'coverage_entries', 'why'],
        'coverage_entry_fields': ['coverage_entry_key', 'piece_key', 'coverage_mode', 'why'],
        'support_only_rule': 'If coverage_mode is support_only, the sentence family certifies continued audit availability of that piece without claiming any visible surface realization.',
        'family_audience_rule': 'required_audiences names exactly the audiences for whom the sentence family counts as a certified carrier.',
        'witness_core_rule': 'Every coverage entry must resolve in the companion coverage-witness-core ledger to the audience-invariant proving keys for that semantic claim.',
        'witness_pack_rule': 'Every coverage entry must resolve in the companion coverage-witness-pack ledger to the exact aggregate route-and-branch bundle for that semantic claim.'
    }
    coverage['note'] = 'Derived sentence-family challenge-coverage certificate for one concrete successor comparison. It says which semantic pieces count as covered for which audiences and which support-only hooks remain auditable, while audience-invariant proving keys live in the companion coverage-witness-core ledger and exact aggregate route-and-branch dependencies live in the companion coverage-witness-pack ledger.'

    coverage_witness_cores = {
        'challenge_coverage_witness_cores_id': COVERAGE_WITNESS_CORES_ID,
        'claim_id': coverage['claim_id'],
        'base_release_id': coverage['base_release_id'],
        'release_id': coverage['release_id'],
        'successor_release_id': coverage['successor_release_id'],
        'compare_profile_id': coverage['compare_profile_id'],
        'compare_report_id': coverage['compare_report_id'],
        'successor_challenge_coverage_id': coverage['challenge_coverage_id'],
        'successor_challenge_terminal_witnesses_id': TERMINAL_ID,
        'successor_challenge_surface_hooks_id': surface_hooks['challenge_surface_hooks_id'],
        'successor_challenge_coverage_witness_packs_id': COVERAGE_WITNESS_PACKS_ID,
        'successor_challenge_coverage_witness_slices_id': COVERAGE_WITNESS_SLICES_ID,
        'note_version': coverage['note_version'],
        'witness_core_contract': {
            'witness_core_fields': ['witness_core_key', 'coverage_entry_key', 'sentence_family', 'normal_form_example_key', 'piece_key', 'coverage_mode', 'required_terminal_witness_keys', 'required_surface_hook_keys', 'why'],
            'audience_invariance_rule': 'Every listed terminal witness and every listed surface hook must resolve to the same sentence family and piece independent of audience route.',
            'surface_support_rule': 'If coverage_mode is surface, required_surface_hook_keys must be nonempty; if coverage_mode is support_only, required_surface_hook_keys must be empty while terminal witnesses remain mandatory.',
            'factorization_rule': 'Witness packs and witness slices must reference one shared core for audience-invariant terminal/surface proving keys rather than restating them inline.'
        },
        'witness_cores': [],
        'note': 'Derived coverage-witness-core ledger for one concrete successor comparison. It keeps the audience-invariant proving keys for each sentence-family coverage claim separate from both semantic coverage and audience-specific route/branch obligations.'
    }

    coverage_witness_packs = {
        'challenge_coverage_witness_packs_id': COVERAGE_WITNESS_PACKS_ID,
        'claim_id': coverage['claim_id'],
        'base_release_id': coverage['base_release_id'],
        'release_id': coverage['release_id'],
        'successor_release_id': coverage['successor_release_id'],
        'compare_profile_id': coverage['compare_profile_id'],
        'compare_report_id': coverage['compare_report_id'],
        'successor_challenge_coverage_id': coverage['challenge_coverage_id'],
        'successor_challenge_coverage_witness_cores_id': COVERAGE_WITNESS_CORES_ID,
        'successor_challenge_routes_id': coverage['successor_challenge_routes_id'],
        'successor_challenge_branches_id': coverage['successor_challenge_branches_id'],
        'successor_challenge_coverage_witness_slices_id': COVERAGE_WITNESS_SLICES_ID,
        'note_version': coverage['note_version'],
        'witness_pack_contract': {
            'witness_pack_fields': ['witness_pack_key', 'witness_core_key', 'coverage_entry_key', 'sentence_family', 'normal_form_example_key', 'piece_key', 'coverage_mode', 'required_route_keys', 'required_branch_keys', 'why'],
            'core_factor_rule': 'Every witness pack must reference exactly one shared witness core carrying the audience-invariant terminal and surface proving keys for that coverage claim.',
            'route_branch_rule': 'Every listed branch must witness one listed route-plus-piece pair for the same sentence family and piece.',
            'slice_union_rule': 'For one coverage entry, the union of all audience slices must recover exactly the route and branch sets declared by the companion witness pack.'
        },
        'witness_packs': [],
        'note': 'Derived coverage-witness-pack ledger for one concrete successor comparison. It keeps the exact aggregate route-and-branch proving bundle for each sentence-family coverage claim separate from both the semantic coverage certificate and the audience-invariant witness core.'
    }

    coverage_witness_slices = {
        'challenge_coverage_witness_slices_id': COVERAGE_WITNESS_SLICES_ID,
        'claim_id': coverage['claim_id'],
        'base_release_id': coverage['base_release_id'],
        'release_id': coverage['release_id'],
        'successor_release_id': coverage['successor_release_id'],
        'compare_profile_id': coverage['compare_profile_id'],
        'compare_report_id': coverage['compare_report_id'],
        'successor_challenge_coverage_id': coverage['challenge_coverage_id'],
        'successor_challenge_coverage_witness_cores_id': COVERAGE_WITNESS_CORES_ID,
        'successor_challenge_routes_id': coverage['successor_challenge_routes_id'],
        'successor_challenge_branches_id': coverage['successor_challenge_branches_id'],
        'successor_challenge_coverage_witness_packs_id': COVERAGE_WITNESS_PACKS_ID,
        'note_version': coverage['note_version'],
        'witness_slice_contract': {
            'witness_slice_fields': ['witness_slice_key', 'witness_pack_key', 'witness_core_key', 'coverage_entry_key', 'sentence_family', 'normal_form_example_key', 'piece_key', 'coverage_mode', 'audience', 'required_route_key', 'required_branch_keys', 'why'],
            'audience_minimality_rule': 'Each slice must name exactly one route key, that route must belong to the stated audience, and every listed branch must witness that same route-plus-piece pair.',
            'core_factor_rule': 'Every witness slice must reference the shared witness core for that coverage entry rather than restating terminal or surface proving keys inline.',
            'pack_union_rule': 'For one coverage entry, the union of all audience slices must recover exactly the route and branch sets declared by the companion witness pack while relying on the companion witness core for audience-invariant keys.'
        },
        'witness_slices': [],
        'note': 'Derived coverage-witness-slice ledger for one concrete successor comparison. It keeps the audience-specific route-and-branch proving delta for one audience-specific use of one coverage claim separate from both the aggregate witness pack and the shared witness core for that claim.'
    }

    route_by_key = {route['route_key']: route for route in routes.get('routes', [])}

    branches_by_key = {branch['branch_key']: branch for branch in branches.get('branches', [])}

    for family in coverage['sentence_families']:
        new_entries = []
        for entry in family['coverage_entries']:
            piece = entry['piece_key']
            coverage_entry_key = entry.get('coverage_entry_key', f"{family['sentence_family']}_{piece}_coverage")
            witness_core_key = f"{family['sentence_family']}_{piece}_witness_core"
            witness_pack_key = f"{family['sentence_family']}_{piece}_witness_pack"
            required_surface_hook_keys = entry.get('required_surface_hook_keys')
            if required_surface_hook_keys is None:
                required_surface_hook_keys = [f"{family['sentence_family']}_{piece}_surface"] if entry['coverage_mode'] == 'surface' else []
            required_route_keys = entry.get('required_route_keys')
            if required_route_keys is None:
                required_route_keys = [
                    route['route_key']
                    for route in routes.get('routes', [])
                    if route.get('question_key') == family.get('question_key') and route.get('audience') in family.get('required_audiences', [])
                ]
            required_branch_keys = entry.get('required_branch_keys')
            if required_branch_keys is None:
                required_branch_keys = [
                    branch['branch_key']
                    for branch in branches.get('branches', [])
                    if branch.get('route_key') in required_route_keys and branch.get('piece_key') == piece
                ]
            coverage_witness_cores['witness_cores'].append({
                'witness_core_key': witness_core_key,
                'coverage_entry_key': coverage_entry_key,
                'sentence_family': family['sentence_family'],
                'normal_form_example_key': family['normal_form_example_key'],
                'piece_key': piece,
                'coverage_mode': entry['coverage_mode'],
                'required_terminal_witness_keys': [f"{family['sentence_family']}_{piece}_terminal"],
                'required_surface_hook_keys': required_surface_hook_keys,
                'why': entry['why'],
            })
            pack = {
                'witness_pack_key': witness_pack_key,
                'witness_core_key': witness_core_key,
                'coverage_entry_key': coverage_entry_key,
                'sentence_family': family['sentence_family'],
                'normal_form_example_key': family['normal_form_example_key'],
                'piece_key': piece,
                'coverage_mode': entry['coverage_mode'],
                'required_route_keys': required_route_keys,
                'required_branch_keys': required_branch_keys,
                'why': entry['why'],
            }
            coverage_witness_packs['witness_packs'].append(pack)
            for route_key in pack['required_route_keys']:
                route = route_by_key[route_key]
                coverage_witness_slices['witness_slices'].append({
                    'witness_slice_key': f"{coverage_entry_key}_{route['audience']}_slice",
                    'witness_pack_key': witness_pack_key,
                    'witness_core_key': witness_core_key,
                    'coverage_entry_key': coverage_entry_key,
                    'sentence_family': family['sentence_family'],
                    'normal_form_example_key': family['normal_form_example_key'],
                    'piece_key': piece,
                    'coverage_mode': entry['coverage_mode'],
                    'audience': route['audience'],
                    'required_route_key': route_key,
                    'required_branch_keys': [bk for bk in pack['required_branch_keys'] if branches_by_key[bk]['route_key'] == route_key],
                    'why': entry['why'],
                })
            new_entries.append({
                'coverage_entry_key': coverage_entry_key,
                'piece_key': piece,
                'coverage_mode': entry['coverage_mode'],
                'why': entry['why'],
            })
        family['coverage_entries'] = new_entries

    terminal_by_key = {entry['terminal_witness_key']: entry for entry in terminal_witnesses['terminal_witnesses']}
    surface_hook_by_key = {entry['surface_hook_key']: entry for entry in surface_hooks.get('surface_hooks', [])}
    stop_profile_by_key = {entry['stop_profile_key']: entry for entry in stop_profiles.get('profiles', [])}
    answer_capsules = {
        'challenge_answer_capsules_id': ANSWER_CAPSULES_ID,
        'claim_id': coverage['claim_id'],
        'base_release_id': coverage['base_release_id'],
        'release_id': coverage['release_id'],
        'successor_release_id': coverage['successor_release_id'],
        'compare_profile_id': coverage['compare_profile_id'],
        'compare_report_id': coverage['compare_report_id'],
        'successor_challenge_routes_id': coverage['successor_challenge_routes_id'],
        'successor_challenge_stop_profiles_id': coverage['successor_challenge_stop_profiles_id'],
        'successor_challenge_branches_id': coverage['successor_challenge_branches_id'],
        'successor_challenge_coverage_id': coverage['challenge_coverage_id'],
        'successor_challenge_terminal_witnesses_id': TERMINAL_ID,
        'successor_challenge_surface_hooks_id': surface_hooks['challenge_surface_hooks_id'],
        'successor_challenge_coverage_witness_cores_id': COVERAGE_WITNESS_CORES_ID,
        'successor_challenge_coverage_witness_slices_id': COVERAGE_WITNESS_SLICES_ID,
        'note_version': coverage['note_version'],
        'answer_capsule_contract': {
            'answer_capsule_fields': ['capsule_key', 'audience', 'question_key', 'sentence_family', 'normal_form_example_key', 'piece_key', 'coverage_mode', 'route_key', 'stop_profile_key', 'branch_key', 'coverage_entry_key', 'witness_core_key', 'witness_slice_key', 'terminal_witness_keys', 'surface_hook_keys', 'approved_terminal_fields', 'start_path', 'minimal_path', 'why'],
            'question_piece_rule': 'Each capsule must bind exactly one audience, one question family, one semantic piece, one audience route, and one route-plus-piece branch.',
            'coverage_factor_rule': 'Each capsule must resolve to one already-declared coverage entry, one shared witness core, and one audience-specific witness slice for that same sentence-family piece.',
            'surface_support_rule': 'If coverage_mode is surface, surface_hook_keys must be nonempty and agree with the shared witness core; if coverage_mode is support_only, surface_hook_keys must be empty even though terminal_witness_keys remain mandatory.',
            'terminal_rule': 'approved_terminal_fields and terminal_witness_keys must agree with the companion stop profile and terminal-witness ledger for the same semantic piece.'
        },
        'answer_capsules': [],
        'note': 'Derived audience-question answer-capsule ledger for one concrete successor comparison. Each capsule assembles the smallest challenge bundle for one audience-specific use of one already-certified sentence-family piece, without letting any one companion object silently swallow route, stop, surface, or terminal ownership.'
    }
    for slice_entry in coverage_witness_slices['witness_slices']:
        route = route_by_key[slice_entry['required_route_key']]
        stop_profile = stop_profile_by_key[route['stop_profile_key']]
        piece = slice_entry['piece_key']
        branch_key = slice_entry['required_branch_keys'][0]
        core = next(entry for entry in coverage_witness_cores['witness_cores'] if entry['witness_core_key'] == slice_entry['witness_core_key'])
        answer_capsules['answer_capsules'].append({
            'capsule_key': f"{slice_entry['coverage_entry_key']}_{route['audience']}_answer",
            'audience': route['audience'],
            'question_key': route['question_key'],
            'sentence_family': slice_entry['sentence_family'],
            'normal_form_example_key': slice_entry['normal_form_example_key'],
            'piece_key': piece,
            'coverage_mode': slice_entry['coverage_mode'],
            'route_key': route['route_key'],
            'stop_profile_key': route['stop_profile_key'],
            'branch_key': branch_key,
            'coverage_entry_key': slice_entry['coverage_entry_key'],
            'witness_core_key': slice_entry['witness_core_key'],
            'witness_slice_key': slice_entry['witness_slice_key'],
            'terminal_witness_keys': core['required_terminal_witness_keys'],
            'surface_hook_keys': core['required_surface_hook_keys'],
            'approved_terminal_fields': [entry for entry in stop_profile['approved_stop_fields'] if entry['piece_key'] == piece],
            'start_path': route['start_path'],
            'minimal_path': route['minimal_path'],
            'why': slice_entry['why'],
        })

    answer_sheets = {
        'challenge_answer_sheets_id': ANSWER_SHEETS_ID,
        'claim_id': coverage['claim_id'],
        'base_release_id': coverage['base_release_id'],
        'release_id': coverage['release_id'],
        'successor_release_id': coverage['successor_release_id'],
        'compare_profile_id': coverage['compare_profile_id'],
        'compare_report_id': coverage['compare_report_id'],
        'successor_challenge_routes_id': coverage['successor_challenge_routes_id'],
        'successor_challenge_stop_profiles_id': coverage['successor_challenge_stop_profiles_id'],
        'successor_challenge_answer_capsules_id': ANSWER_CAPSULES_ID,
        'note_version': coverage['note_version'],
        'answer_sheet_contract': {
            'answer_sheet_fields': ['answer_sheet_key', 'audience', 'question_key', 'sentence_family', 'normal_form_example_key', 'route_key', 'stop_profile_key', 'piece_keys', 'ordered_capsule_keys', 'surface_capsule_keys', 'support_only_capsule_keys', 'start_path', 'minimal_path', 'why'],
            'audience_question_rule': 'Each answer sheet must bind exactly one audience and one question family through one declared audience route and one stop profile.',
            'piece_completeness_rule': 'piece_keys must match the semantic-piece order declared by the companion stop profile, and ordered_capsule_keys must contribute exactly one capsule for each listed piece and no others.',
            'capsule_factor_rule': 'Answer sheets group imported answer capsules instead of restating their branch, coverage, witness-core, witness-slice, terminal-owner, or surface-hook payloads inline.',
            'surface_support_partition_rule': 'surface_capsule_keys and support_only_capsule_keys must partition ordered_capsule_keys according to the coverage_mode of the imported capsules.'
        },
        'answer_sheets': [],
        'note': 'Derived audience-question answer-sheet ledger for one concrete successor comparison. Each sheet groups the ordered piece-complete answer-capsule set for one audience/question pair while keeping all proving payload factored into the imported capsules.'
    }
    capsules_by_audience_question = {}
    for capsule in answer_capsules['answer_capsules']:
        capsules_by_audience_question.setdefault((capsule['audience'], capsule['question_key']), []).append(capsule)
    for (audience, question_key), capsules in sorted(capsules_by_audience_question.items()):
        route = route_by_key[capsules[0]['route_key']]
        stop_profile = stop_profile_by_key[capsules[0]['stop_profile_key']]
        piece_keys = [entry['piece_key'] for entry in stop_profile.get('semantic_pieces', [])]
        caps_by_piece = {cap['piece_key']: cap for cap in capsules}
        ordered_capsules = [caps_by_piece[piece_key] for piece_key in piece_keys]
        answer_sheets['answer_sheets'].append({
            'answer_sheet_key': f"{audience}_{question_key}_answer_sheet",
            'audience': audience,
            'question_key': question_key,
            'sentence_family': ordered_capsules[0]['sentence_family'],
            'normal_form_example_key': ordered_capsules[0]['normal_form_example_key'],
            'route_key': route['route_key'],
            'stop_profile_key': stop_profile['stop_profile_key'],
            'piece_keys': piece_keys,
            'ordered_capsule_keys': [cap['capsule_key'] for cap in ordered_capsules],
            'surface_capsule_keys': [cap['capsule_key'] for cap in ordered_capsules if cap['coverage_mode'] == 'surface'],
            'support_only_capsule_keys': [cap['capsule_key'] for cap in ordered_capsules if cap['coverage_mode'] == 'support_only'],
            'start_path': route['start_path'],
            'minimal_path': route['minimal_path'],
            'why': 'This sheet gives one piece-complete audience/question handoff by grouping the already-certified answer capsules in stop-profile order.'
        })

    sentence_locks_by_key = {entry['lock_key']: entry for entry in sentence_locks.get('locks', [])}
    answer_capsules_by_key = {entry['capsule_key']: entry for entry in answer_capsules['answer_capsules']}
    answer_cards_by_key = {}
    answer_cards = {
        'challenge_answer_cards_id': ANSWER_CARDS_ID,
        'claim_id': coverage['claim_id'],
        'base_release_id': coverage['base_release_id'],
        'release_id': coverage['release_id'],
        'successor_release_id': coverage['successor_release_id'],
        'compare_profile_id': coverage['compare_profile_id'],
        'compare_report_id': coverage['compare_report_id'],
        'successor_challenge_answer_sheets_id': ANSWER_SHEETS_ID,
        'successor_sentence_locks_id': sentence_locks['sentence_locks_id'],
        'successor_normal_form_id': normal_form['normal_form_id'],
        'successor_quote_map_id': quote_map['quote_map_id'],
        'note_version': coverage['note_version'],
        'answer_card_contract': {
            'answer_card_fields': ['answer_card_key', 'audience', 'question_key', 'sentence_family', 'normal_form_example_key', 'answer_sheet_key', 'sentence_lock_key', 'sentence_reuse_status', 'selected_inline_profile', 'visible_provenance_fields', 'surface_text', 'surface_piece_keys', 'support_only_piece_keys', 'start_path', 'minimal_path', 'cite_path', 'why'],
            'sheet_lock_rule': 'Each answer card must bind exactly one imported answer sheet and one imported sentence lock for the same audience/question sentence family.',
            'inline_profile_rule': 'selected_inline_profile must be the default inline-provenance profile declared by the imported sentence lock, sentence_reuse_status must mirror that lock\'s maintained reuse posture exactly, and visible_provenance_fields must match that profile\'s visible fields exactly.',
            'surface_text_rule': 'surface_text and cite_path must agree with the imported sentence lock rather than being rewritten independently.',
            'piece_partition_rule': 'surface_piece_keys and support_only_piece_keys must agree with the partition induced by the imported answer sheet and its ordered answer capsules.'
        },
        'answer_cards': [],
        'note': 'Derived audience-question answer-card ledger for one concrete successor comparison. Each card binds one piece-complete answer sheet to one shipped sentence lock, its mirrored current sentence-reuse posture, and one default visible-provenance mode, so later notes can cite one emitted answer object instead of pairing a whole-question handoff with a separate sentence-reuse policy object by hand.'
    }
    for sheet in answer_sheets['answer_sheets']:
        lock = sentence_locks_by_key[sheet['normal_form_example_key']]
        default_profile = lock['comparison_anchor']['default_inline_profile']['profile_key']
        profile = next(entry for entry in lock['comparison_anchor']['inline_provenance_profiles'] if entry['profile_key'] == default_profile)
        ordered_capsules = [answer_capsules_by_key[key] for key in sheet['ordered_capsule_keys']]
        card = {
            'answer_card_key': sheet['answer_sheet_key'].replace('_answer_sheet', '_answer_card'),
            'audience': sheet['audience'],
            'question_key': sheet['question_key'],
            'sentence_family': sheet['sentence_family'],
            'normal_form_example_key': sheet['normal_form_example_key'],
            'answer_sheet_key': sheet['answer_sheet_key'],
            'sentence_lock_key': lock['lock_key'],
            'sentence_reuse_status': lock.get('comparison_anchor', {}).get('maintenance_posture', {}).get('current_status'),
            'selected_inline_profile': default_profile,
            'visible_provenance_fields': profile.get('visible_fields', []),
            'surface_text': lock['surface_text'],
            'surface_piece_keys': [cap['piece_key'] for cap in ordered_capsules if cap['coverage_mode'] == 'surface'],
            'support_only_piece_keys': [cap['piece_key'] for cap in ordered_capsules if cap['coverage_mode'] == 'support_only'],
            'start_path': sheet['start_path'],
            'minimal_path': sheet['minimal_path'],
            'cite_path': lock['cite_path'],
            'why': 'This card binds one whole-question handoff to one shipped sentence lock and its default visible-provenance mode, giving later notes one emitted audience/question answer object to cite.'
        }
        answer_cards['answer_cards'].append(card)
        answer_cards_by_key[card['answer_card_key']] = card

    clauses_by_key = {entry['clause_key']: entry for entry in clause_pack.get('clauses', [])}
    closure_rows_by_role = {entry['role']: entry for entry in closure_ledger.get('role_rows', [])}
    answer_carrier_slots = {
        'challenge_answer_carrier_slots_id': ANSWER_CARRIER_SLOTS_ID,
        'claim_id': coverage['claim_id'],
        'base_release_id': coverage['base_release_id'],
        'release_id': coverage['release_id'],
        'successor_release_id': coverage['successor_release_id'],
        'compare_profile_id': coverage['compare_profile_id'],
        'compare_report_id': coverage['compare_report_id'],
        'successor_challenge_answer_cards_id': ANSWER_CARDS_ID,
        'successor_lineage_notice_id': lineage['notice_id'],
        'successor_clause_pack_id': clause_pack['clause_pack_id'],
        'release_closure_ledger_id': closure_ledger['closure_ledger_id'],
        'note_version': coverage['note_version'],
        'answer_carrier_slot_contract': {
            'answer_carrier_slot_fields': ['carrier_slot_key', 'audience', 'question_key', 'answer_card_key', 'sentence_family', 'carrier_artifact', 'carrier_kind', 'carrier_locator', 'carrier_channel', 'closure_role', 'surface_text', 'selected_inline_profile', 'visible_provenance_fields', 'why'],
            'exact_carrier_rule': 'surface_text must agree exactly with the text named by the declared carrier artifact and carrier locator.',
            'card_factor_rule': 'Each answer carrier slot must reference exactly one imported answer card and exactly one already-owned shipped field or reusable clause as its carrier.',
            'closure_role_rule': 'If closure_role is non-null, the named closure role must be satisfied in the companion release-closure ledger for the same shipped artifact.'
        },
        'answer_carrier_slots': [],
        'note': 'Derived audience-question answer-carrier-slot ledger for one concrete successor comparison. Each slot binds one emitted answer card to one exact shipped field or reusable clause, so later notes can cite where the released answer actually lives without re-owning semantics, sentence reuse, or visible-provenance policy.'
    }
    slot_specs = [
        {
            'carrier_slot_key': 'release_note_public_status_sentence_answer_carrier_slot',
            'answer_card_key': 'release_note_public_status_sentence_answer_card',
            'carrier_artifact': 'example_successor_lineage_notice.json',
            'carrier_kind': 'field',
            'carrier_locator': 'status_summary',
            'carrier_channel': 'public_wrapper',
            'closure_role': 'fresh_successor_lineage_notice',
            'surface_text': lineage['status_summary'],
            'why': 'The release note carries the public-status answer directly in the shipped lineage-notice wrapper field.'
        },
        {
            'carrier_slot_key': 'referee_public_status_sentence_answer_carrier_slot',
            'answer_card_key': 'referee_public_status_sentence_answer_card',
            'carrier_artifact': 'example_successor_clause_pack.json',
            'carrier_kind': 'clause',
            'carrier_locator': 'public_status_sentence',
            'carrier_channel': 'reusable_clause',
            'closure_role': None,
            'surface_text': clauses_by_key['public_status_sentence']['text'],
            'why': 'The referee-facing reusable public-status clause carries the same released answer text without depending on the wrapper field.'
        },
        {
            'carrier_slot_key': 'release_note_compact_diff_summary_answer_carrier_slot',
            'answer_card_key': 'release_note_compact_diff_summary_answer_card',
            'carrier_artifact': 'example_successor_clause_pack.json',
            'carrier_kind': 'clause',
            'carrier_locator': 'compact_diff_clause',
            'carrier_channel': 'reusable_clause',
            'closure_role': None,
            'surface_text': clauses_by_key['compact_diff_clause']['text'],
            'why': 'The release-note compact-diff answer is carried by the checked reusable compact-diff clause.'
        },
        {
            'carrier_slot_key': 'auditor_compact_diff_summary_answer_carrier_slot',
            'answer_card_key': 'auditor_compact_diff_summary_answer_card',
            'carrier_artifact': 'example_successor_clause_pack.json',
            'carrier_kind': 'clause',
            'carrier_locator': 'compact_diff_clause',
            'carrier_channel': 'reusable_clause',
            'closure_role': None,
            'surface_text': clauses_by_key['compact_diff_clause']['text'],
            'why': 'The auditor-facing compact-diff answer reuses the same checked compact-diff clause as its exact shipped carrier.'
        },
    ]
    for spec in slot_specs:
        card = answer_cards_by_key[spec['answer_card_key']]
        if spec['closure_role'] is not None:
            row = closure_rows_by_role.get(spec['closure_role'], {})
            assert row.get('status') == 'satisfied', spec['closure_role']
            assert spec['carrier_artifact'] in row.get('bound_artifacts', []), spec['carrier_artifact']
        answer_carrier_slots['answer_carrier_slots'].append({
            'carrier_slot_key': spec['carrier_slot_key'],
            'audience': card['audience'],
            'question_key': card['question_key'],
            'answer_card_key': card['answer_card_key'],
            'sentence_family': card['sentence_family'],
            'carrier_artifact': spec['carrier_artifact'],
            'carrier_kind': spec['carrier_kind'],
            'carrier_locator': spec['carrier_locator'],
            'carrier_channel': spec['carrier_channel'],
            'closure_role': spec['closure_role'],
            'surface_text': spec['surface_text'],
            'selected_inline_profile': card['selected_inline_profile'],
            'visible_provenance_fields': card['visible_provenance_fields'],
            'why': spec['why'],
        })

    branch_by_key = {entry['branch_key']: entry for entry in branches.get('branches', [])}
    answer_audit_trails = {
        'challenge_answer_audit_trails_id': ANSWER_AUDIT_TRAILS_ID,
        'claim_id': coverage['claim_id'],
        'base_release_id': coverage['base_release_id'],
        'release_id': coverage['release_id'],
        'successor_release_id': coverage['successor_release_id'],
        'compare_profile_id': coverage['compare_profile_id'],
        'compare_report_id': coverage['compare_report_id'],
        'successor_challenge_answer_carrier_slots_id': ANSWER_CARRIER_SLOTS_ID,
        'successor_challenge_answer_cards_id': ANSWER_CARDS_ID,
        'successor_challenge_answer_sheets_id': ANSWER_SHEETS_ID,
        'successor_challenge_answer_capsules_id': ANSWER_CAPSULES_ID,
        'successor_challenge_branches_id': coverage['successor_challenge_branches_id'],
        'successor_challenge_terminal_witnesses_id': TERMINAL_ID,
        'note_version': coverage['note_version'],
        'answer_audit_trail_contract': {
            'answer_audit_trail_fields': ['audit_trail_key', 'audience', 'question_key', 'sentence_family', 'answer_carrier_slot_key', 'answer_card_key', 'answer_sheet_key', 'start_path', 'minimal_path', 'carrier_artifact', 'carrier_locator', 'trace_order', 'ordered_piece_keys', 'piece_traces', 'why'],
            'carrier_to_terminal_rule': 'Each answer audit trail must start at exactly one imported answer carrier slot and retain that slot\'s exact carrier artifact and locator before moving leftward through the imported answer card, answer sheet, one-piece capsules, branches, and terminal owners.',
            'piece_completeness_rule': 'ordered_piece_keys and piece_traces must follow the imported answer sheet order exactly, with one and only one piece trace for each declared semantic piece.',
            'piece_trace_rule': 'Every piece trace must reference exactly one imported answer capsule and one imported branch for that audience/question piece, and its declared terminal fields and terminal-witness keys must agree with the imported capsule and terminal-witness ledger.',
            'stop_rule': 'Audit may stop only at the approved narrow terminal field named by the imported branch endpoint for that semantic piece; the trail may not terminate at the wrapper carrier slot.'
        },
        'answer_audit_trails': [],
        'note': 'Derived audience-question answer-audit-trail ledger for one concrete successor comparison. Each trail starts at one exact shipped answer carrier slot and spells out the leftward walk through the emitted answer card, whole-question sheet, one-piece capsules, piece branches, and narrow terminal owners, so later notes can cite one maintained audit path instead of reassembling that walk by hand.'
    }
    terminal_by_key = {entry['terminal_witness_key']: entry for entry in terminal_witnesses['terminal_witnesses']}
    answer_sheets_by_key = {entry['answer_sheet_key']: entry for entry in answer_sheets['answer_sheets']}
    answer_capsules_by_key = {entry['capsule_key']: entry for entry in answer_capsules['answer_capsules']}
    for slot in answer_carrier_slots['answer_carrier_slots']:
        card = answer_cards_by_key[slot['answer_card_key']]
        sheet = answer_sheets_by_key[card['answer_sheet_key']]
        piece_traces = []
        ordered_piece_keys = []
        for capsule_key in sheet['ordered_capsule_keys']:
            capsule = answer_capsules_by_key[capsule_key]
            piece = capsule['piece_key']
            ordered_piece_keys.append(piece)
            branch = branch_by_key[capsule['branch_key']]
            terminals = [terminal_by_key[key] for key in capsule['terminal_witness_keys']]
            piece_traces.append({
                'piece_key': piece,
                'coverage_mode': capsule['coverage_mode'],
                'capsule_key': capsule['capsule_key'],
                'route_key': capsule['route_key'],
                'stop_profile_key': capsule['stop_profile_key'],
                'branch_key': capsule['branch_key'],
                'coverage_entry_key': capsule['coverage_entry_key'],
                'witness_core_key': capsule['witness_core_key'],
                'witness_slice_key': capsule['witness_slice_key'],
                'terminal_witness_keys': capsule['terminal_witness_keys'],
                'surface_hook_keys': capsule['surface_hook_keys'],
                'approved_terminal_fields': capsule['approved_terminal_fields'],
                'branch_start_path': branch['start_path'],
                'escalation_sequence': branch['escalation_sequence'],
                'terminal_stop_field': branch['terminal_stop_field'],
                'why': capsule['why'],
            })
        answer_audit_trails['answer_audit_trails'].append({
            'audit_trail_key': slot['carrier_slot_key'].replace('_answer_carrier_slot', '_answer_audit_trail'),
            'audience': slot['audience'],
            'question_key': slot['question_key'],
            'sentence_family': slot['sentence_family'],
            'answer_carrier_slot_key': slot['carrier_slot_key'],
            'answer_card_key': card['answer_card_key'],
            'answer_sheet_key': sheet['answer_sheet_key'],
            'start_path': card['start_path'],
            'minimal_path': card['minimal_path'],
            'carrier_artifact': slot['carrier_artifact'],
            'carrier_locator': slot['carrier_locator'],
            'trace_order': ['carrier', 'card', 'sheet', 'capsules', 'branch', 'terminal'],
            'ordered_piece_keys': ordered_piece_keys,
            'piece_traces': piece_traces,
            'why': 'This trail records one maintained leftward audit walk from the exact shipped answer carrier to the narrow terminal owners for each semantic piece of the audience/question answer.'
        })

    surface_hooks['successor_challenge_terminal_witnesses_id'] = TERMINAL_ID
    surface_hooks['successor_challenge_coverage_witness_cores_id'] = COVERAGE_WITNESS_CORES_ID
    surface_hooks['successor_challenge_coverage_witness_packs_id'] = COVERAGE_WITNESS_PACKS_ID
    surface_hooks['successor_challenge_coverage_witness_slices_id'] = COVERAGE_WITNESS_SLICES_ID
    shc = surface_hooks['surface_hook_contract']
    shc['surface_hook_fields'] = ['surface_hook_key', 'sentence_family', 'normal_form_example_key', 'piece_key', 'binding_kind', 'segment_keys', 'carried_claim_classes', 'why']
    shc.pop('terminal_target_rule', None)
    shc['claim_class_rule'] = 'Every carried claim class must be a claim class carried by at least one listed segment. Exact terminal ownership is imported from the companion terminal-witness ledger.'
    surface_hooks['note'] = 'Derived sentence-family surface-hook ledger for one concrete successor comparison. It says exactly which emitted segments realize each covered semantic piece, including when the same segment family is shared across multiple pieces; audience-invariant proving keys live in the companion coverage-witness-core ledger, exact aggregate route/branch proving bundles live in the companion coverage-witness-pack ledger, and exact narrow terminal ownership lives in the companion terminal-witness ledger.'
    for hook in surface_hooks['surface_hooks']:
        hook.pop('terminal_target_keys', None)

    for entry in quote_map.get('quote_targets', []):
        if entry.get('quote_key') == 'maintenance_order':
            entry.setdefault('target', {})['value'] = graph.get('topological_order', [])

    lineage['successor_challenge_terminal_witnesses_id'] = TERMINAL_ID
    lineage['successor_challenge_coverage_witness_cores_id'] = COVERAGE_WITNESS_CORES_ID
    lineage['successor_challenge_coverage_witness_packs_id'] = COVERAGE_WITNESS_PACKS_ID
    lineage['successor_challenge_coverage_witness_slices_id'] = COVERAGE_WITNESS_SLICES_ID
    answer_citation_dockets = {
        'challenge_answer_citation_dockets_id': ANSWER_CITATION_DOCKETS_ID,
        'claim_id': coverage['claim_id'],
        'base_release_id': coverage['base_release_id'],
        'release_id': coverage['release_id'],
        'successor_release_id': coverage['successor_release_id'],
        'compare_profile_id': coverage['compare_profile_id'],
        'compare_report_id': coverage['compare_report_id'],
        'successor_challenge_answer_capsules_id': ANSWER_CAPSULES_ID,
        'successor_challenge_answer_sheets_id': ANSWER_SHEETS_ID,
        'successor_challenge_answer_cards_id': ANSWER_CARDS_ID,
        'successor_challenge_answer_carrier_slots_id': ANSWER_CARRIER_SLOTS_ID,
        'successor_challenge_answer_audit_trails_id': ANSWER_AUDIT_TRAILS_ID,
        'note_version': coverage['note_version'],
        'answer_citation_docket_contract': {
            'answer_citation_docket_fields': ['answer_citation_docket_key', 'audience', 'question_key', 'sentence_family', 'piece_keys', 'piece_citation_entries', 'whole_question_entry', 'emitted_answer_entry', 'exact_carrier_entry', 'full_audit_entry', 'start_path', 'minimal_path', 'why'],
            'smallest_sufficient_rule': 'Each docket entry must name the smallest maintained late-stage answer object sufficient for the stated downstream need: one-piece citation uses a capsule, whole-question handoff uses a sheet, emitted-answer identity uses a card, exact shipped location uses a carrier slot, and full leftward audit uses an audit trail.',
            'audience_question_rule': 'Each docket must bind exactly one audience and one downstream question, and every imported object key must belong to that same audience/question pair.',
            'piece_rule': 'piece_citation_entries must follow the imported answer-sheet piece order exactly and must reference the matching imported answer capsules for those pieces.',
            'location_rule': 'exact_carrier_entry and full_audit_entry must preserve the carrier artifact and locator declared by the imported carrier slot and audit trail.'
        },
        'answer_citation_dockets': [],
        'note': 'Derived audience-question answer-citation-docket ledger for one concrete successor comparison. Each docket says which already-maintained late-stage answer object is the smallest sufficient citation target for common downstream reuse intents, without turning that selection layer into a new semantic stage.'
    }

    trails_by_key = {entry['audit_trail_key']: entry for entry in answer_audit_trails['answer_audit_trails']}
    slots_by_key = {entry['carrier_slot_key']: entry for entry in answer_carrier_slots['answer_carrier_slots']}
    for sheet in answer_sheets['answer_sheets']:
        card = next(entry for entry in answer_cards['answer_cards'] if entry['answer_sheet_key'] == sheet['answer_sheet_key'])
        slot = next(entry for entry in answer_carrier_slots['answer_carrier_slots'] if entry['answer_card_key'] == card['answer_card_key'])
        trail = next(entry for entry in answer_audit_trails['answer_audit_trails'] if entry['answer_carrier_slot_key'] == slot['carrier_slot_key'])
        ordered_capsules = [answer_capsules_by_key[key] for key in sheet['ordered_capsule_keys']]
        answer_citation_dockets['answer_citation_dockets'].append({
            'answer_citation_docket_key': f"{sheet['audience']}_{sheet['question_key']}_answer_citation_docket",
            'audience': sheet['audience'],
            'question_key': sheet['question_key'],
            'sentence_family': sheet['sentence_family'],
            'piece_keys': sheet['piece_keys'],
            'piece_citation_entries': [
                {
                    'piece_key': capsule['piece_key'],
                    'object_kind': 'answer_capsule',
                    'object_key': capsule['capsule_key'],
                    'cite_path': 'example_successor_challenge_answer_capsules.json',
                    'when': f"Need the smallest sufficient answer object for the {capsule['piece_key']} of this audience/question answer.",
                    'why': 'A capsule is the minimal maintained one-piece answer bundle.'
                }
                for capsule in ordered_capsules
            ],
            'whole_question_entry': {
                'object_kind': 'answer_sheet',
                'object_key': sheet['answer_sheet_key'],
                'cite_path': 'example_successor_challenge_answer_sheets.json',
                'when': 'Need the whole downstream answer for this audience/question, piece-complete but not yet bound to one emitted sentence.',
                'why': 'The answer sheet is the smallest maintained whole-question handoff.'
            },
            'emitted_answer_entry': {
                'object_kind': 'answer_card',
                'object_key': card['answer_card_key'],
                'cite_path': 'example_successor_challenge_answer_cards.json',
                'sentence_lock_key': card['sentence_lock_key'],
                'selected_inline_profile': card['selected_inline_profile'],
                'when': 'Need the released audience/question answer object itself, including its shipped sentence identity and default visible-provenance mode.',
                'why': 'The answer card is the smallest maintained emitted-answer object.'
            },
            'exact_carrier_entry': {
                'object_kind': 'answer_carrier_slot',
                'object_key': slot['carrier_slot_key'],
                'cite_path': 'example_successor_challenge_answer_carrier_slots.json',
                'carrier_artifact': slot['carrier_artifact'],
                'carrier_locator': slot['carrier_locator'],
                'when': 'Need to point at the exact shipped field or reusable clause that carries the emitted answer.',
                'why': 'The carrier slot is the smallest maintained exact-location object.'
            },
            'full_audit_entry': {
                'object_kind': 'answer_audit_trail',
                'object_key': trail['audit_trail_key'],
                'cite_path': 'example_successor_challenge_answer_audit_trails.json',
                'carrier_artifact': trail['carrier_artifact'],
                'carrier_locator': trail['carrier_locator'],
                'when': 'Need the full leftward reader walk from the exact carrier slot to the narrow terminal owners for every semantic piece.',
                'why': 'The audit trail is the smallest maintained full-audit object.'
            },
            'start_path': sheet['start_path'],
            'minimal_path': sheet['minimal_path'],
            'why': 'This docket answers the late-stage citation-selection question for one audience/question pair without widening any imported answer object.'
        })

    answer_publication_profiles = {
        'challenge_answer_publication_profiles_id': ANSWER_PUBLICATION_PROFILES_ID,
        'claim_id': coverage['claim_id'],
        'base_release_id': coverage['base_release_id'],
        'release_id': coverage['release_id'],
        'successor_release_id': coverage['successor_release_id'],
        'compare_profile_id': coverage['compare_profile_id'],
        'compare_report_id': coverage['compare_report_id'],
        'successor_challenge_answer_cards_id': ANSWER_CARDS_ID,
        'successor_challenge_answer_citation_dockets_id': ANSWER_CITATION_DOCKETS_ID,
        'successor_challenge_answer_carrier_slots_id': ANSWER_CARRIER_SLOTS_ID,
        'successor_challenge_answer_audit_trails_id': ANSWER_AUDIT_TRAILS_ID,
        'successor_sentence_locks_id': sentence_locks['sentence_locks_id'],
        'note_version': coverage['note_version'],
        'answer_publication_profile_contract': {
            'answer_publication_profile_fields': ['answer_publication_profile_key', 'audience', 'question_key', 'sentence_family', 'answer_card_key', 'answer_citation_docket_key', 'sentence_reuse_status', 'default_inline_entry', 'expanded_inline_entry', 'exact_location_entry', 'full_audit_entry', 'start_path', 'minimal_path', 'why'],
            'budget_locality_rule': 'default_inline_entry must be the smallest declared inline publication form later notes should inherit, while expanded_inline_entry must reuse the same emitted answer card under a strictly larger declared inline-provenance mode from the same sentence lock.',
            "inherited_visibility_rule": "Every inline entry must name one declared inline-provenance profile from the imported sentence lock and must copy that profile\'s visible fields exactly.",
            "escalation_companion_rule": "exact_location_entry and full_audit_entry must agree exactly with the imported citation docket\'s exact-carrier and full-audit entries for the same audience/question pair.",
            'non_semantic_rule': 'Publication profiles may package reuse modes and escalation choices, but they may not create new sentence text, new answer semantics, or new citation owners.'
        },
        'answer_publication_profiles': [],
        'note': 'Derived audience-question publication-profile ledger for one concrete successor comparison. Each profile packages the emitted answer card, its mirrored current sentence-reuse posture, the declared brief/expanded inline-provenance modes from the sentence lock, and the exact-location/full-audit escalation choices imported from the citation docket, without turning publication policy into a new answer stage.'
    }
    dockets_by_key = {entry['answer_citation_docket_key']: entry for entry in answer_citation_dockets['answer_citation_dockets']}
    for card in answer_cards['answer_cards']:
        docket_key = f"{card['audience']}_{card['question_key']}_answer_citation_docket"
        docket = dockets_by_key[docket_key]
        lock = sentence_locks_by_key[card['sentence_lock_key']]
        profiles_by_key = {entry['profile_key']: entry for entry in lock.get('comparison_anchor', {}).get('inline_provenance_profiles', [])}
        default_profile_key = lock.get('comparison_anchor', {}).get('default_inline_profile', {}).get('profile_key', card['selected_inline_profile'])
        expanded_profile_key = 'capsule' if 'capsule' in profiles_by_key else default_profile_key
        answer_publication_profiles['answer_publication_profiles'].append({
            'answer_publication_profile_key': f"{card['audience']}_{card['question_key']}_answer_publication_profile",
            'audience': card['audience'],
            'question_key': card['question_key'],
            'sentence_family': card['sentence_family'],
            'answer_card_key': card['answer_card_key'],
            'answer_citation_docket_key': docket_key,
            'sentence_reuse_status': card.get('sentence_reuse_status'),
            'default_inline_entry': {
                'display_mode': 'default_inline',
                'object_kind': 'answer_card',
                'object_key': card['answer_card_key'],
                'cite_path': 'example_successor_challenge_answer_cards.json',
                'sentence_lock_key': card['sentence_lock_key'],
                'selected_inline_profile': default_profile_key,
                'visible_provenance_fields': profiles_by_key[default_profile_key].get('visible_fields', []),
                'surface_text': card['surface_text'],
                'when': 'Use the emitted answer in a space-tight publication under the archive-default inline-provenance mode.',
                'why': 'This is the smallest declared inline publication form for the emitted answer card.'
            },
            'expanded_inline_entry': {
                'display_mode': 'expanded_inline',
                'object_kind': 'answer_card',
                'object_key': card['answer_card_key'],
                'cite_path': 'example_successor_challenge_answer_cards.json',
                'sentence_lock_key': card['sentence_lock_key'],
                'selected_inline_profile': expanded_profile_key,
                'visible_provenance_fields': profiles_by_key[expanded_profile_key].get('visible_fields', []),
                'surface_text': card['surface_text'],
                'when': 'Use the same emitted answer but show a larger declared inline-provenance bundle at the reuse site.',
                'why': 'This keeps the emitted answer fixed while expanding only the already-declared visible-provenance mode.'
            },
            'exact_location_entry': docket['exact_carrier_entry'],
            'full_audit_entry': docket['full_audit_entry'],
            'start_path': docket['start_path'],
            'minimal_path': docket['minimal_path'],
            'why': 'This profile fixes the common brief, expanded, exact-location, and full-audit publication forms for one audience/question pair without re-deciding citation or visible-provenance policy at every reuse site.'
        })

    answer_disclosure_packets = {
        'challenge_answer_disclosure_packets_id': ANSWER_DISCLOSURE_PACKETS_ID,
        'claim_id': coverage['claim_id'],
        'base_release_id': coverage['base_release_id'],
        'release_id': coverage['release_id'],
        'successor_release_id': coverage['successor_release_id'],
        'compare_profile_id': coverage['compare_profile_id'],
        'compare_report_id': coverage['compare_report_id'],
        'successor_challenge_answer_publication_profiles_id': ANSWER_PUBLICATION_PROFILES_ID,
        'successor_challenge_answer_citation_dockets_id': ANSWER_CITATION_DOCKETS_ID,
        'successor_challenge_answer_audit_trails_id': ANSWER_AUDIT_TRAILS_ID,
        'successor_challenge_answer_carrier_slots_id': ANSWER_CARRIER_SLOTS_ID,
        'support_manifest_id': support_manifest['manifest_id'],
        'artifact_inventory_id': inventory['inventory_id'],
        'note_version': coverage['note_version'],
        'answer_disclosure_packet_contract': {
            'answer_disclosure_packet_fields': ['answer_disclosure_packet_key', 'audience', 'question_key', 'sentence_family', 'answer_publication_profile_key', 'answer_citation_docket_key', 'public_inline_entry', 'expanded_inline_entry', 'exact_location_entry', 'full_audit_entry', 'evidence_class_keys', 'request_packet_paths', 'validation_paths', 'start_path', 'minimal_path', 'why'],
            'public_anchor_rule': "public_inline_entry must agree exactly with the imported publication profile's default-inline entry, while expanded_inline_entry must agree exactly with its declared expanded-inline entry for the same emitted answer.",
            'escalation_preservation_rule': 'exact_location_entry and full_audit_entry must agree exactly with the imported publication profile and citation docket for the same audience/question pair.',
            'requestable_archive_rule': 'request_packet_paths must be support-manifest-listed artifacts sufficient to recover the emitted answer, the exact carrier slot, the full audit trail, the supporting late-stage answer ledgers, and the narrow terminal owner paths named by that audit trail.',
            'validator_rule': 'validation_paths must include support_manifest.json, example_artifact_inventory.json, example_validation_report.json, and ../tools/validate_example.py so an on-request reviewer can identify and recheck the maintained bundle cut.',
            'non_semantic_rule': 'Disclosure packets package public citation and requestable archive slices; they do not create new answer semantics, new carrier owners, or new audit routes.'
        },
        'answer_disclosure_packets': [],
        'note': 'Derived audience-question answer-disclosure-packet ledger for one concrete successor comparison. Each packet pairs the brief public answer form with the exact requestable audit slice to hand over when a reader asks for the deeper archive support omitted from a space-limited paper.'
    }

    publication_profiles_by_key = {entry['answer_publication_profile_key']: entry for entry in answer_publication_profiles['answer_publication_profiles']}
    for profile in answer_publication_profiles['answer_publication_profiles']:
        docket = dockets_by_key[profile['answer_citation_docket_key']]
        trail = trails_by_key[docket['full_audit_entry']['object_key']]
        request_paths = []

        def add_request_path(path):
            if path and path not in request_paths:
                request_paths.append(path)

        add_request_path(profile['minimal_path'])
        add_request_path(profile['start_path'])
        for path in [
            'example_successor_challenge_answer_publication_profiles.json',
            'example_successor_challenge_answer_citation_dockets.json',
            'example_successor_challenge_answer_cards.json',
            'example_successor_sentence_locks.json',
            'example_successor_challenge_answer_carrier_slots.json',
            'example_successor_challenge_answer_audit_trails.json',
            'example_successor_challenge_answer_sheets.json',
            'example_successor_challenge_answer_capsules.json',
            'example_successor_challenge_branches.json',
            'example_successor_challenge_terminal_witnesses.json',
            'example_compare_report.json',
            trail['carrier_artifact'],
        ]:
            add_request_path(path)
        for piece_trace in trail.get('piece_traces', []):
            for step in piece_trace.get('escalation_sequence', []):
                add_request_path(step.get('path'))
            for field in piece_trace.get('approved_terminal_fields', []):
                add_request_path(field.get('path'))
        for path in ['example_artifact_inventory.json', 'example_validation_report.json']:
            add_request_path(path)
        if profile['question_key'] == 'public_status_sentence':
            add_request_path('example_release_closure_ledger.json')

        evidence_class_keys = ['bundle_identity_and_validator_companions']
        if profile['question_key'] == 'public_status_sentence':
            evidence_class_keys.append('public_status_lineage_and_closure_support')
        else:
            evidence_class_keys.append('compact_diff_compare_and_replay_support')

        answer_disclosure_packets['answer_disclosure_packets'].append({
            'answer_disclosure_packet_key': f"{profile['audience']}_{profile['question_key']}_answer_disclosure_packet",
            'audience': profile['audience'],
            'question_key': profile['question_key'],
            'sentence_family': profile['sentence_family'],
            'answer_publication_profile_key': profile['answer_publication_profile_key'],
            'answer_citation_docket_key': profile['answer_citation_docket_key'],
            'public_inline_entry': profile['default_inline_entry'],
            'expanded_inline_entry': profile['expanded_inline_entry'],
            'exact_location_entry': profile['exact_location_entry'],
            'full_audit_entry': profile['full_audit_entry'],
            'evidence_class_keys': evidence_class_keys,
            'request_packet_paths': request_paths,
            'validation_paths': ['support_manifest.json', 'example_artifact_inventory.json', 'example_validation_report.json', '../tools/validate_example.py'],
            'start_path': profile['start_path'],
            'minimal_path': profile['minimal_path'],
            'why': 'This packet fixes both the public citation form and the exact requestable audit slice for one audience/question answer, so a brief paper can stay terse without improvising the deeper archive handoff when a referee asks for more.'
        })

    answer_escalation_ladders = {
        'challenge_answer_escalation_ladders_id': ANSWER_ESCALATION_LADDERS_ID,
        'claim_id': coverage['claim_id'],
        'base_release_id': coverage['base_release_id'],
        'release_id': coverage['release_id'],
        'successor_release_id': coverage['successor_release_id'],
        'compare_profile_id': coverage['compare_profile_id'],
        'compare_report_id': coverage['compare_report_id'],
        'successor_challenge_answer_publication_profiles_id': ANSWER_PUBLICATION_PROFILES_ID,
        'successor_challenge_answer_citation_dockets_id': ANSWER_CITATION_DOCKETS_ID,
        'successor_challenge_answer_disclosure_packets_id': ANSWER_DISCLOSURE_PACKETS_ID,
        'note_version': coverage['note_version'],
        'answer_escalation_ladder_contract': {
            'answer_escalation_ladder_fields': ['answer_escalation_ladder_key', 'audience', 'question_key', 'sentence_family', 'answer_publication_profile_key', 'answer_citation_docket_key', 'answer_disclosure_packet_key', 'ordered_steps', 'start_path', 'minimal_path', 'why'],
            'monotone_reveal_rule': 'ordered_steps must reveal weakly more support in the fixed order default_inline -> expanded_inline -> exact_location -> full_audit -> request_packet, without changing the emitted answer identity for the same audience/question pair.',
            'import_rule': 'The first two steps must agree exactly with the imported publication profile, the exact-location and full-audit steps must agree exactly with the imported citation docket, and the final request-packet step must agree exactly with the imported disclosure packet.',
            'identity_rule': 'Every ordered step in one ladder must resolve to the same audience/question pair and to the same emitted answer card whenever the step remains on the answer side of the series.',
            'shared_escalation_vocabulary_rule': 'Repeated step labels may recur in later review menus or series-spine mirrors only as imported escalation-ladder vocabulary; the concrete reveal order remains owned by the audience/question ladder.',
            'non_semantic_rule': 'Escalation ladders own only the ordered reveal policy for one already-maintained answer; they may not create new sentence text, new citation owners, or new audit routes.'
        },
        'answer_escalation_ladders': [],
        'note': 'Derived audience-question answer-escalation-ladder ledger for one concrete successor comparison. Each ladder fixes the ordered brief-to-audit reveal policy for one audience/question answer so later notes can move from terse public wording to exact carrier location, full audit, and on-request archive handoff without improvising that escalation sequence.'
    }

    disclosure_packets_by_key = {entry['answer_disclosure_packet_key']: entry for entry in answer_disclosure_packets['answer_disclosure_packets']}
    for profile in answer_publication_profiles['answer_publication_profiles']:
        docket = dockets_by_key[profile['answer_citation_docket_key']]
        packet_key = f"{profile['audience']}_{profile['question_key']}_answer_disclosure_packet"
        packet = disclosure_packets_by_key[packet_key]
        answer_escalation_ladders['answer_escalation_ladders'].append({
            'answer_escalation_ladder_key': f"{profile['audience']}_{profile['question_key']}_answer_escalation_ladder",
            'audience': profile['audience'],
            'question_key': profile['question_key'],
            'sentence_family': profile['sentence_family'],
            'answer_publication_profile_key': profile['answer_publication_profile_key'],
            'answer_citation_docket_key': profile['answer_citation_docket_key'],
            'answer_disclosure_packet_key': packet_key,
            'ordered_steps': [
                {
                    'step_rank': 1,
                    'step_key': 'default_inline',
                    'escalation_step_vocabulary_mode': 'imported_vocabulary_ladder_owned_order',
                    **profile['default_inline_entry']
                },
                {
                    'step_rank': 2,
                    'step_key': 'expanded_inline',
                    'escalation_step_vocabulary_mode': 'imported_vocabulary_ladder_owned_order',
                    **profile['expanded_inline_entry']
                },
                {
                    'step_rank': 3,
                    'step_key': 'exact_location',
                    'escalation_step_vocabulary_mode': 'imported_vocabulary_ladder_owned_order',
                    **docket['exact_carrier_entry']
                },
                {
                    'step_rank': 4,
                    'step_key': 'full_audit',
                    'escalation_step_vocabulary_mode': 'imported_vocabulary_ladder_owned_order',
                    **docket['full_audit_entry']
                },
                {
                    'step_rank': 5,
                    'step_key': 'request_packet',
                    'escalation_step_vocabulary_mode': 'imported_vocabulary_ladder_owned_order',
                    'object_kind': 'answer_disclosure_packet',
                    'object_key': packet['answer_disclosure_packet_key'],
                    'cite_path': 'example_successor_challenge_answer_disclosure_packets.json',
                    'public_inline_entry': packet['public_inline_entry'],
                    'expanded_inline_entry': packet['expanded_inline_entry'],
                    'exact_location_entry': packet['exact_location_entry'],
                    'full_audit_entry': packet['full_audit_entry'],
                    'request_packet_paths': packet['request_packet_paths'],
                    'validation_paths': packet['validation_paths'],
                    'evidence_class_keys': packet['evidence_class_keys'],
                    'when': 'Need the maintained public-on-request handoff after the reader has already outgrown inline, exact-location, and full-audit escalation.',
                    'why': 'The disclosure packet is the maintained final handoff target once the deeper archive slice itself must be shipped.'
                }
            ],
            'start_path': profile['start_path'],
            'minimal_path': profile['minimal_path'],
            'why': 'This ladder fixes the ordered reveal policy for one audience/question answer under space pressure: brief public sentence first, deeper support only as the reader asks for more.'
        })


    answer_review_menus = {
        'challenge_answer_review_menus_id': ANSWER_REVIEW_MENUS_ID,
        'claim_id': coverage['claim_id'],
        'base_release_id': coverage['base_release_id'],
        'release_id': coverage['release_id'],
        'successor_release_id': coverage['successor_release_id'],
        'compare_profile_id': coverage['compare_profile_id'],
        'compare_report_id': coverage['compare_report_id'],
        'successor_challenge_answer_publication_profiles_id': ANSWER_PUBLICATION_PROFILES_ID,
        'successor_challenge_answer_citation_dockets_id': ANSWER_CITATION_DOCKETS_ID,
        'successor_challenge_answer_disclosure_packets_id': ANSWER_DISCLOSURE_PACKETS_ID,
        'successor_challenge_answer_escalation_ladders_id': ANSWER_ESCALATION_LADDERS_ID,
        'note_version': coverage['note_version'],
        'answer_review_menu_contract': {
            'answer_review_menu_fields': ['answer_review_menu_key', 'audience', 'question_key', 'sentence_family', 'answer_publication_profile_key', 'answer_citation_docket_key', 'answer_disclosure_packet_key', 'answer_escalation_ladder_key', 'answer_side_terminal_citation_normal_form', 'answer_side_terminal_sentence_normal_form', 'review_entries', 'start_path', 'minimal_path', 'why'],
            'request_class_rule': 'review_entries must cover exactly the common referee request classes brief_inline_check, expanded_inline_check, exact_location_check, full_audit_check, request_packet_check, and reveal_order_check for the same audience/question pair.',
            'shared_review_vocabulary_rule': 'Repeated review request-class labels may recur across later routes or series-spine mirrors only as imported review-menu vocabulary; the concrete handoff choice for each label remains owned by the audience/question review menu.',
            'smallest_sufficient_rule': 'Each review entry must point at the smallest sufficient already-maintained object for that request class: inline checks use the publication profile, exact-location and full-audit checks use the citation docket entries, request-packet checks use the disclosure packet, and reveal-order checks use the escalation ladder.',
            'import_rule': 'Inline entries must agree exactly with the imported publication profile, exact-location and full-audit entries must agree exactly with the imported citation docket, the request-packet entry must agree exactly with the imported disclosure packet, and the reveal-order entry must agree exactly with the imported escalation ladder.',
            'non_semantic_rule': 'Review menus own only request-class response selection for one already-maintained audience/question answer; they may not create new answer text, new carrier locations, or new audit paths.'
        },
        'answer_review_menus': [],
        'note': 'Derived audience-question answer-review-menu ledger for one concrete successor comparison. Each menu answers the referee-sized follow-up question of what exact maintained object should be handed over for one request class, so terse papers can stay brief without improvising the response bundle when a reader asks for more.'
    }

    ladders_by_key = {entry['answer_escalation_ladder_key']: entry for entry in answer_escalation_ladders['answer_escalation_ladders']}
    for profile in answer_publication_profiles['answer_publication_profiles']:
        docket = dockets_by_key[profile['answer_citation_docket_key']]
        packet_key = f"{profile['audience']}_{profile['question_key']}_answer_disclosure_packet"
        ladder_key = f"{profile['audience']}_{profile['question_key']}_answer_escalation_ladder"
        packet = disclosure_packets_by_key[packet_key]
        ladder = ladders_by_key[ladder_key]
        menu_key = f"{profile['audience']}_{profile['question_key']}_answer_review_menu"
        answer_card_key = profile.get('answer_card_key')
        answer_side_terminal_citation_normal_form = {
            'anchor_order': ['public_anchor', 'checked_answer_card', 'answer_disclosure_packet', 'answer_review_menu'],
            'anchors': [
                {
                    'anchor_kind': 'public_anchor',
                    'cite_path': profile['start_path'],
                    'object_kind': 'public_anchor',
                    'object_key': profile['start_path'],
                },
                {
                    'anchor_kind': 'checked_answer_card',
                    'cite_path': 'example_successor_challenge_answer_cards.json',
                    'object_kind': 'answer_card',
                    'object_key': answer_card_key,
                },
                {
                    'anchor_kind': 'answer_disclosure_packet',
                    'cite_path': 'example_successor_challenge_answer_disclosure_packets.json',
                    'object_kind': 'answer_disclosure_packet',
                    'object_key': packet_key,
                },
                {
                    'anchor_kind': 'answer_review_menu',
                    'cite_path': 'example_successor_challenge_answer_review_menus.json',
                    'object_kind': 'answer_review_menu',
                    'object_key': menu_key,
                },
            ],
            'default_inline_profile_key': profile.get('default_inline_entry', {}).get('selected_inline_profile'),
            'default_visible_provenance_fields': profile.get('default_inline_entry', {}).get('visible_provenance_fields', []),
            'reopen_if_request_classes': ['exact_location_check', 'full_audit_check', 'reveal_order_check'],
            'widen_only_if': 'leave_answer_archive_cut_for_adjacent_source_only_branch',
            'why': 'This is the smallest maintained four-anchor checked-answer stop for the audience/question pair: public anchor, exact checked answer, exact answer-side omitted-support cut, and exact terminal referee handoff owner.',
        }
        answer_side_terminal_sentence_normal_form = {
            'surface_text': f"For the checked-answer path, stop at: {profile['start_path']} -> {answer_card_key} -> {packet_key} -> {menu_key}.",
            'anchor_order': ['public_anchor', 'checked_answer_card', 'answer_disclosure_packet', 'answer_review_menu'],
            'reopen_if_request_classes': ['exact_location_check', 'full_audit_check', 'reveal_order_check'],
            'widen_only_if': 'leave_answer_archive_cut_for_adjacent_source_only_branch',
            'why': 'This sentence adds no new owner; it is only the one-clause rendering of the already-owned four-anchor answer-side terminal citation normal form.',
        }
        answer_review_menus['answer_review_menus'].append({
            'answer_review_menu_key': menu_key,
            'audience': profile['audience'],
            'question_key': profile['question_key'],
            'sentence_family': profile['sentence_family'],
            'answer_publication_profile_key': profile['answer_publication_profile_key'],
            'answer_citation_docket_key': profile['answer_citation_docket_key'],
            'answer_disclosure_packet_key': packet_key,
            'answer_escalation_ladder_key': ladder_key,
            'answer_side_terminal_citation_normal_form': answer_side_terminal_citation_normal_form,
            'answer_side_terminal_sentence_normal_form': answer_side_terminal_sentence_normal_form,
            'review_entries': [
                {
                    'request_class': 'brief_inline_check',
                    'review_request_class_vocabulary_mode': 'imported_vocabulary_menu_owned_selection',
                    'object_kind': 'answer_publication_profile',
                    'object_key': profile['answer_publication_profile_key'],
                    'cite_path': 'example_successor_challenge_answer_publication_profiles.json',
                    'selected_entry': profile['default_inline_entry'],
                    'when': 'Need the smallest inline answer form that a terse public paper should print by default for this audience/question pair.',
                    'why': 'The publication profile owns the smallest maintained inline presentation choice.'
                },
                {
                    'request_class': 'expanded_inline_check',
                    'review_request_class_vocabulary_mode': 'imported_vocabulary_menu_owned_selection',
                    'object_kind': 'answer_publication_profile',
                    'object_key': profile['answer_publication_profile_key'],
                    'cite_path': 'example_successor_challenge_answer_publication_profiles.json',
                    'selected_entry': profile['expanded_inline_entry'],
                    'when': 'Need the larger inline answer form that stays within the same emitted answer but prints more visible provenance.',
                    'why': 'The publication profile owns the maintained expanded inline presentation for the same answer card.'
                },
                {
                    'request_class': 'exact_location_check',
                    'review_request_class_vocabulary_mode': 'imported_vocabulary_menu_owned_selection',
                    'object_kind': 'answer_citation_docket',
                    'object_key': docket['answer_citation_docket_key'],
                    'cite_path': 'example_successor_challenge_answer_citation_dockets.json',
                    'selected_entry': docket['exact_carrier_entry'],
                    'when': 'Need the exact shipped field or reusable clause carrying the emitted answer once inline support is no longer enough.',
                    'why': 'The citation docket already selects the smallest maintained exact-location object.'
                },
                {
                    'request_class': 'full_audit_check',
                    'review_request_class_vocabulary_mode': 'imported_vocabulary_menu_owned_selection',
                    'object_kind': 'answer_citation_docket',
                    'object_key': docket['answer_citation_docket_key'],
                    'cite_path': 'example_successor_challenge_answer_citation_dockets.json',
                    'selected_entry': docket['full_audit_entry'],
                    'when': 'Need the full leftward reader walk to the narrow terminal owners for every semantic piece of the answer.',
                    'why': 'The citation docket already selects the smallest maintained full-audit object.'
                },
                {
                    'request_class': 'request_packet_check',
                    'review_request_class_vocabulary_mode': 'imported_vocabulary_menu_owned_selection',
                    'object_kind': 'answer_disclosure_packet',
                    'object_key': packet['answer_disclosure_packet_key'],
                    'cite_path': 'example_successor_challenge_answer_disclosure_packets.json',
                    'selected_entry': {
                        'public_inline_entry': packet['public_inline_entry'],
                        'expanded_inline_entry': packet['expanded_inline_entry'],
                        'exact_location_entry': packet['exact_location_entry'],
                        'full_audit_entry': packet['full_audit_entry'],
                        'request_packet_paths': packet['request_packet_paths'],
                        'validation_paths': packet['validation_paths'],
                        'evidence_class_keys': packet['evidence_class_keys']
                    },
                    'when': 'Need the exact requestable archive slice and validator companions that should be handed over once a referee asks for omitted support.',
                    'why': 'The disclosure packet owns the maintained public-on-request handoff bundle.'
                },
                {
                    'request_class': 'reveal_order_check',
                    'review_request_class_vocabulary_mode': 'imported_vocabulary_menu_owned_selection',
                    'object_kind': 'answer_escalation_ladder',
                    'object_key': ladder['answer_escalation_ladder_key'],
                    'cite_path': 'example_successor_challenge_answer_escalation_ladders.json',
                    'selected_entry': {'ordered_steps': ladder['ordered_steps']},
                    'when': 'Need the maintained order in which the already-owned support forms should be revealed under space pressure.',
                    'why': 'The escalation ladder owns the brief-to-audit reveal order for this same answer.'
                }
            ],
            'start_path': profile['start_path'],
            'minimal_path': profile['minimal_path'],
            'why': 'This menu turns common referee follow-up requests into explicit smallest-sufficient handoff choices for one audience/question answer without widening any imported answer artifact.'
        })

    lineage['successor_challenge_answer_capsules_id'] = ANSWER_CAPSULES_ID
    lineage['successor_challenge_answer_sheets_id'] = ANSWER_SHEETS_ID
    lineage['successor_challenge_answer_cards_id'] = ANSWER_CARDS_ID
    lineage['successor_challenge_answer_carrier_slots_id'] = ANSWER_CARRIER_SLOTS_ID
    lineage['successor_challenge_answer_audit_trails_id'] = ANSWER_AUDIT_TRAILS_ID
    lineage['successor_challenge_answer_citation_dockets_id'] = ANSWER_CITATION_DOCKETS_ID
    lineage['successor_challenge_answer_publication_profiles_id'] = ANSWER_PUBLICATION_PROFILES_ID
    lineage['successor_challenge_answer_disclosure_packets_id'] = ANSWER_DISCLOSURE_PACKETS_ID
    lineage['successor_challenge_answer_escalation_ladders_id'] = ANSWER_ESCALATION_LADDERS_ID
    lineage['successor_challenge_answer_review_menus_id'] = ANSWER_REVIEW_MENUS_ID
    lineage['successor_requestable_evidence_classes_id'] = REQUESTABLE_EVIDENCE_CLASSES_ID
    lineage['successor_public_request_contracts_id'] = PUBLIC_REQUEST_CONTRACTS_ID
    lineage['successor_request_fulfillment_certificates_id'] = REQUEST_FULFILLMENT_CERTIFICATES_ID
    lineage['successor_public_request_status_envelopes_id'] = PUBLIC_REQUEST_STATUS_ENVELOPES_ID
    lineage['successor_public_request_carryforward_envelopes_id'] = PUBLIC_REQUEST_CARRYFORWARD_ENVELOPES_ID
    lineage['successor_public_request_notice_normal_forms_id'] = PUBLIC_REQUEST_NOTICE_NORMAL_FORMS_ID
    lineage['successor_public_request_notice_selections_id'] = PUBLIC_REQUEST_NOTICE_SELECTIONS_ID
    lineage['successor_public_request_response_menus_id'] = PUBLIC_REQUEST_RESPONSE_MENUS_ID
    lineage['successor_public_request_response_packets_id'] = PUBLIC_REQUEST_RESPONSE_PACKETS_ID
    lineage['successor_public_request_response_packet_carryforward_profiles_id'] = PUBLIC_REQUEST_RESPONSE_PACKET_CARRYFORWARD_PROFILES_ID
    lineage['successor_public_request_response_packet_delta_ledgers_id'] = PUBLIC_REQUEST_RESPONSE_PACKET_DELTA_LEDGERS_ID
    lineage['successor_public_request_response_packet_refresh_notices_id'] = PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_NOTICES_ID
    lineage['successor_public_request_response_packet_refresh_notice_normal_forms_id'] = PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_NOTICE_NORMAL_FORMS_ID
    lineage['successor_public_request_response_packet_refresh_notice_selections_id'] = PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_NOTICE_SELECTIONS_ID
    lineage['successor_public_request_response_packet_refresh_response_menus_id'] = PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_RESPONSE_MENUS_ID
    lineage['successor_public_request_response_packet_refresh_response_packets_id'] = PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_RESPONSE_PACKETS_ID
    lineage['reader_pointer_order'] = insert_pointer_after(
        lineage.get('reader_pointer_order', []),
        {'path': 'example_successor_challenge_terminal_witnesses.json', 'why': 'piece-hook terminal-witness ledger showing the exact narrow terminal owners for each covered or support-only semantic piece'},
        'example_successor_challenge_coverage.json'
    )
    lineage['reader_pointer_order'] = insert_pointer_after(
        lineage.get('reader_pointer_order', []),
        {'path': 'example_successor_challenge_coverage_witness_cores.json', 'why': 'per-entry audience-invariant proving bundle showing the exact terminal witnesses and any shared surface hooks every certified audience reuses for that claim'},
        'example_successor_challenge_coverage.json'
    )
    lineage['reader_pointer_order'] = insert_pointer_after(
        lineage.get('reader_pointer_order', []),
        {'path': 'example_successor_challenge_coverage_witness_packs.json', 'why': 'per-entry aggregate route-and-branch bundle showing the exact audience routes and branches that certify one coverage claim as a whole'},
        'example_successor_challenge_coverage_witness_cores.json'
    )
    lineage['reader_pointer_order'] = insert_pointer_after(
        lineage.get('reader_pointer_order', []),
        {'path': 'example_successor_challenge_coverage_witness_slices.json', 'why': 'audience-specific route-and-branch bundle showing the single route and route-specific branches one audience contributes for one coverage claim while reusing the shared witness core'},
        'example_successor_challenge_coverage_witness_packs.json'
    )
    lineage['reader_pointer_order'] = insert_pointer_after(
        lineage.get('reader_pointer_order', []),
        {'path': 'example_successor_challenge_answer_capsules.json', 'why': 'audience-question answer capsules assembling one minimal route/stop/branch/core bundle for a single contested sentence-family piece'},
        'example_successor_challenge_coverage_witness_slices.json'
    )
    lineage['reader_pointer_order'] = insert_pointer_after(
        lineage.get('reader_pointer_order', []),
        {'path': 'example_successor_challenge_answer_sheets.json', 'why': 'audience-question answer sheets grouping the ordered piece-complete capsule set for one whole downstream question'},
        'example_successor_challenge_answer_capsules.json'
    )
    lineage['reader_pointer_order'] = insert_pointer_after(
        lineage.get('reader_pointer_order', []),
        {'path': 'example_successor_challenge_answer_cards.json', 'why': 'audience-question answer cards binding one whole-question handoff to one shipped sentence and one default visible-provenance mode'},
        'example_successor_challenge_answer_sheets.json'
    )
    insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_successor_challenge_answer_carrier_slots.json', 'why': 'audience-question answer carrier slots binding one emitted answer card to one exact shipped field or reusable clause'},
        'example_successor_challenge_answer_cards.json'
    )
    insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_successor_challenge_answer_audit_trails.json', 'why': 'audience-question answer audit trails spelling out the leftward walk from one exact carrier slot through the card, sheet, capsules, branches, and narrow terminal owners'},
        'example_successor_challenge_answer_carrier_slots.json'
    )
    insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_successor_challenge_answer_citation_dockets.json', 'why': 'audience-question answer citation dockets selecting the smallest sufficient late-stage answer object for common downstream reuse goals'},
        'example_successor_challenge_answer_audit_trails.json'
    )
    insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_successor_challenge_answer_publication_profiles.json', 'why': 'audience-question answer publication profiles packaging the default and expanded inline answer forms together with exact-location and full-audit escalation targets'},
        'example_successor_challenge_answer_citation_dockets.json'
    )
    insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_successor_challenge_answer_disclosure_packets.json', 'why': 'audience-question answer-disclosure packets pairing the brief public answer form with the exact requestable audit slice to hand over when deeper archive support is requested'},
        'example_successor_challenge_answer_publication_profiles.json'
    )
    insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_successor_challenge_answer_escalation_ladders.json', 'why': 'audience-question answer-escalation ladders fixing the ordered brief-to-audit reveal path from terse inline answer through exact location, full audit, and the requestable packet'},
        'example_successor_challenge_answer_disclosure_packets.json'
    )
    insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_successor_challenge_answer_review_menus.json', 'why': 'audience-question answer-review menus mapping common referee follow-up requests to the smallest sufficient maintained handoff object for that same answer'},
        'example_successor_challenge_answer_escalation_ladders.json'
    )
    insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_requestable_evidence_classes.json', 'why': 'stable evidence-class ledger naming the omitted-support families behind the worked note\'s source-only request cuts'},
        'example_successor_challenge_answer_review_menus.json'
    )
    insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_public_request_contracts.json', 'why': "paper-facing source-only public request contracts tying public anchor families to the exact maintained packet/menu/validator cut behind the worked note's public request sentence"},
        'example_requestable_evidence_classes.json'
    )
    insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_request_fulfillment_certificates.json', 'why': "family-scoped completion certificates stating when the worked note's promised source-only support cuts have been fully satisfied"},
        'example_public_request_contracts.json'
    )
    insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_public_request_status_envelope.json', 'why': "paper-level source-only request-status envelope compressing the worked note's family-scoped fulfillment certificates to one public status token"},
        'example_request_fulfillment_certificates.json'
    )
    insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_public_request_carryforward_envelope.json', 'why': "successor-release carryforward envelope stating whether that paper-level source-only status token survives unchanged or reopens under the canned successor release"},
        'example_public_request_status_envelope.json'
    )
    insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_public_request_notice.json', 'why': "outward-facing source-only public-request notices wrapping the within-release status token and successor carryforward verdict into the exact short sentences readers should see"},
        'example_public_request_carryforward_envelope.json'
    )
    insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_public_request_notice_normal_forms.json', 'why': 'canonical source-only public-request notice normal forms factoring the emitted wrapper sentences into maintained templates and explicit slot bindings'},
        'example_public_request_notice.json'
    )
    insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_public_request_notice_selections.json', 'why': 'token-keyed source-only public-request notice selections choosing which canonical notice normal form applies for the shipped within-release or successor-facing notice basis'},
        'example_public_request_notice_normal_forms.json'
    )
    insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_public_request_response_menus.json', 'why': 'notice-keyed source-only public-request response menus mapping concrete follow-up classes to the smallest sufficient maintained handoff object for that visible sentence while recording that the six class labels are shared vocabulary across notices'},
        'example_public_request_notice_selections.json'
    )
    insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_public_request_response_packets.json', 'why': 'notice-and-follow-up keyed source-only response packets fixing the exact bounded handoff slice after one response-menu choice has been made and recording that packet identity stays attached to one concrete notice/follow-up pair'},
        'example_public_request_response_menus.json'
    )
    insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_public_request_response_packet_carryforward_profiles.json', 'why': 'successor-facing source-only response-packet carryforward profiles classifying whether one exact bounded handoff slice may be reused as-is, refreshed in place, or must reopen under the canned successor release'},
        'example_public_request_response_packets.json'
    )
    insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_public_request_response_packet_delta_ledgers.json', 'why': 'successor-facing source-only response-packet delta ledgers recording which release-bound field families actually refresh when one reusable bounded handoff slice is reissued under the canned successor release'},
        'example_public_request_response_packet_carryforward_profiles.json'
    )
    lineage['reader_pointer_order'] = insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_public_request_response_packet_refresh_notices.json', 'why': 'successor-facing source-only response-packet refresh notices emitting the exact visible reissue sentence for one reusable bounded handoff slice after packet-local refresh instructions have already been fixed'},
        'example_public_request_response_packet_delta_ledgers.json'
    )
    lineage['reader_pointer_order'] = insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_public_request_response_packet_refresh_notice_normal_forms.json', 'why': 'canonical source-only response-packet refresh-notice normal forms factoring the emitted visible reissue sentences into maintained templates and explicit slot bindings'},
        'example_public_request_response_packet_refresh_notices.json'
    )
    lineage['reader_pointer_order'] = insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_public_request_response_packet_refresh_notice_selections.json', 'why': 'token-keyed selector ledger choosing which canonical source-only packet-refresh notice family applies for one emitted visible reissue sentence under the shipped successor packet-delta basis'},
        'example_public_request_response_packet_refresh_notice_normal_forms.json'
    )
    lineage['reader_pointer_order'] = insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_public_request_response_packet_refresh_response_menus.json', 'why': 'successor-facing response menus mapping concrete follow-up classes about one emitted packet-refresh sentence to the smallest sufficient already-owned packet, carryforward, delta, sentence, canonical-family, or family-choice owner'},
        'example_public_request_response_packet_refresh_notice_selections.json'
    )
    lineage['reader_pointer_order'] = insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_public_request_response_packet_refresh_response_packets.json', 'why': 'successor-facing response packets freezing the exact bounded handoff slice that should travel after one concrete follow-up class about an emitted packet-refresh sentence has already chosen the right owner'},
        'example_public_request_response_packet_refresh_response_menus.json'
    )
    lineage['reader_pointer_order'] = insert_pointer_after(
        lineage['reader_pointer_order'],
        {'path': 'example_public_request_response_packet_refresh_response_packet_closure_verdicts.json', 'why': 'successor-facing closure verdicts certifying that one exact packet-refresh handoff slice already closes the visible reissue branch under the shipped follow-up taxonomy unless a named reopen trigger fires'},
        'example_public_request_response_packet_refresh_response_packets.json'
    )

    graph['successor_challenge_terminal_witnesses_id'] = TERMINAL_ID
    graph['successor_challenge_coverage_witness_cores_id'] = COVERAGE_WITNESS_CORES_ID
    graph['successor_challenge_coverage_witness_packs_id'] = COVERAGE_WITNESS_PACKS_ID
    graph['successor_challenge_coverage_witness_slices_id'] = COVERAGE_WITNESS_SLICES_ID
    graph['successor_challenge_answer_capsules_id'] = ANSWER_CAPSULES_ID
    graph['successor_challenge_answer_sheets_id'] = ANSWER_SHEETS_ID
    graph['successor_challenge_answer_cards_id'] = ANSWER_CARDS_ID
    graph['successor_challenge_answer_carrier_slots_id'] = ANSWER_CARRIER_SLOTS_ID
    graph['successor_challenge_answer_audit_trails_id'] = ANSWER_AUDIT_TRAILS_ID
    graph['successor_challenge_answer_citation_dockets_id'] = ANSWER_CITATION_DOCKETS_ID
    graph['successor_challenge_answer_publication_profiles_id'] = ANSWER_PUBLICATION_PROFILES_ID
    graph['successor_challenge_answer_disclosure_packets_id'] = ANSWER_DISCLOSURE_PACKETS_ID
    graph['successor_challenge_answer_escalation_ladders_id'] = ANSWER_ESCALATION_LADDERS_ID
    graph['successor_challenge_answer_review_menus_id'] = ANSWER_REVIEW_MENUS_ID
    graph['successor_requestable_evidence_classes_id'] = REQUESTABLE_EVIDENCE_CLASSES_ID
    graph['successor_public_request_contracts_id'] = PUBLIC_REQUEST_CONTRACTS_ID
    graph['successor_request_fulfillment_certificates_id'] = REQUEST_FULFILLMENT_CERTIFICATES_ID
    graph['successor_public_request_status_envelopes_id'] = PUBLIC_REQUEST_STATUS_ENVELOPES_ID
    graph['successor_public_request_carryforward_envelopes_id'] = PUBLIC_REQUEST_CARRYFORWARD_ENVELOPES_ID
    graph['successor_public_request_notices_id'] = PUBLIC_REQUEST_NOTICES_ID
    graph['successor_public_request_notice_normal_forms_id'] = PUBLIC_REQUEST_NOTICE_NORMAL_FORMS_ID
    graph['successor_public_request_notice_selections_id'] = PUBLIC_REQUEST_NOTICE_SELECTIONS_ID
    graph['successor_public_request_response_menus_id'] = PUBLIC_REQUEST_RESPONSE_MENUS_ID
    graph['successor_public_request_response_packets_id'] = PUBLIC_REQUEST_RESPONSE_PACKETS_ID
    graph['successor_public_request_response_packet_carryforward_profiles_id'] = PUBLIC_REQUEST_RESPONSE_PACKET_CARRYFORWARD_PROFILES_ID
    graph['successor_public_request_response_packet_delta_ledgers_id'] = PUBLIC_REQUEST_RESPONSE_PACKET_DELTA_LEDGERS_ID
    graph['successor_public_request_response_packet_refresh_notices_id'] = PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_NOTICES_ID
    graph['successor_public_request_response_packet_refresh_notice_normal_forms_id'] = PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_NOTICE_NORMAL_FORMS_ID
    graph['successor_public_request_response_packet_refresh_notice_selections_id'] = PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_NOTICE_SELECTIONS_ID
    graph['successor_public_request_response_packet_refresh_response_menus_id'] = PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_RESPONSE_MENUS_ID
    graph['successor_public_request_response_packet_refresh_response_packets_id'] = PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_RESPONSE_PACKETS_ID
    graph['successor_public_request_response_packet_refresh_response_packet_closure_verdicts_id'] = PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_RESPONSE_PACKET_CLOSURE_VERDICTS_ID
    topo = graph.get('topological_order', [])
    topo = insert_topo_after(topo, 'example_successor_challenge_terminal_witnesses.json', 'example_successor_challenge_coverage.json')
    topo = insert_topo_after(topo, 'example_successor_challenge_coverage_witness_cores.json', 'example_successor_challenge_surface_hooks.json')
    topo = insert_topo_after(topo, 'example_successor_challenge_coverage_witness_packs.json', 'example_successor_challenge_coverage_witness_cores.json')
    topo = insert_topo_after(topo, 'example_successor_challenge_coverage_witness_slices.json', 'example_successor_challenge_coverage_witness_packs.json')
    topo = insert_topo_after(topo, 'example_successor_challenge_answer_capsules.json', 'example_successor_challenge_coverage_witness_slices.json')
    topo = insert_topo_after(topo, 'example_successor_challenge_answer_sheets.json', 'example_successor_challenge_answer_capsules.json')
    topo = insert_topo_after(topo, 'example_successor_challenge_answer_cards.json', 'example_successor_sentence_locks.json')
    topo = insert_topo_after(topo, 'example_successor_challenge_answer_carrier_slots.json', 'example_successor_challenge_answer_cards.json')
    topo = insert_topo_after(topo, 'example_successor_challenge_answer_audit_trails.json', 'example_successor_challenge_answer_carrier_slots.json')
    topo = insert_topo_after(topo, 'example_successor_challenge_answer_citation_dockets.json', 'example_successor_challenge_answer_audit_trails.json')
    topo = insert_topo_after(topo, 'example_successor_challenge_answer_publication_profiles.json', 'example_successor_challenge_answer_citation_dockets.json')
    topo = insert_topo_after(topo, 'example_successor_challenge_answer_disclosure_packets.json', 'example_successor_challenge_answer_publication_profiles.json')
    topo = insert_topo_after(topo, 'example_successor_challenge_answer_escalation_ladders.json', 'example_successor_challenge_answer_disclosure_packets.json')
    topo = insert_topo_after(topo, 'example_successor_challenge_answer_review_menus.json', 'example_successor_challenge_answer_escalation_ladders.json')
    topo = insert_topo_after(topo, 'example_requestable_evidence_classes.json', 'example_successor_challenge_answer_review_menus.json')
    topo = insert_topo_after(topo, 'example_public_request_contracts.json', 'example_requestable_evidence_classes.json')
    topo = insert_topo_after(topo, 'example_request_fulfillment_certificates.json', 'example_public_request_contracts.json')
    topo = insert_topo_after(topo, 'example_public_request_status_envelope.json', 'example_request_fulfillment_certificates.json')
    topo = insert_topo_after(topo, 'example_public_request_carryforward_envelope.json', 'example_public_request_status_envelope.json')
    topo = insert_topo_after(topo, 'example_public_request_notice.json', 'example_public_request_carryforward_envelope.json')
    topo = insert_topo_after(topo, 'example_public_request_notice_normal_forms.json', 'example_public_request_notice.json')
    topo = insert_topo_after(topo, 'example_public_request_notice_selections.json', 'example_public_request_notice_normal_forms.json')
    topo = insert_topo_after(topo, 'example_public_request_response_menus.json', 'example_public_request_notice_selections.json')
    topo = insert_topo_after(topo, 'example_public_request_response_packets.json', 'example_public_request_response_menus.json')
    topo = insert_topo_after(topo, 'example_public_request_response_packet_carryforward_profiles.json', 'example_public_request_response_packets.json')
    topo = insert_topo_after(topo, 'example_public_request_response_packet_delta_ledgers.json', 'example_public_request_response_packet_carryforward_profiles.json')
    topo = insert_topo_after(topo, 'example_public_request_response_packet_refresh_notices.json', 'example_public_request_response_packet_delta_ledgers.json')
    topo = insert_topo_after(topo, 'example_public_request_response_packet_refresh_notice_normal_forms.json', 'example_public_request_response_packet_refresh_notices.json')
    topo = insert_topo_after(topo, 'example_public_request_response_packet_refresh_notice_selections.json', 'example_public_request_response_packet_refresh_notice_normal_forms.json')
    topo = insert_topo_after(topo, 'example_public_request_response_packet_refresh_response_menus.json', 'example_public_request_response_packet_refresh_notice_selections.json')
    topo = insert_topo_after(topo, 'example_public_request_response_packet_refresh_response_packets.json', 'example_public_request_response_packet_refresh_response_menus.json')
    topo = insert_topo_after(topo, 'example_public_request_response_packet_refresh_response_packet_closure_verdicts.json', 'example_public_request_response_packet_refresh_response_packets.json')
    graph['topological_order'] = topo
    for entry in quote_map.get('quote_targets', []):
        if entry.get('quote_key') == 'maintenance_order':
            entry.setdefault('target', {})['value'] = graph['topological_order']
    for entry in clause_pack.get('clauses', []):
        if entry.get('clause_key') == 'maintenance_order_clause':
            entry['text'] = 'Maintenance order: ' + ' -> '.join(graph['topological_order']) + '.'
    nodes = graph.get('nodes', [])
    if not any(n.get('path') == 'example_successor_challenge_terminal_witnesses.json' for n in nodes):
        nodes.append({'path': 'example_successor_challenge_terminal_witnesses.json', 'kind': 'piece_terminal_witnesses', 'object_id': TERMINAL_ID})
    if not any(n.get('path') == 'example_successor_challenge_coverage_witness_cores.json' for n in nodes):
        nodes.append({'path': 'example_successor_challenge_coverage_witness_cores.json', 'kind': 'coverage_witness_cores', 'object_id': COVERAGE_WITNESS_CORES_ID})
    if not any(n.get('path') == 'example_successor_challenge_coverage_witness_packs.json' for n in nodes):
        nodes.append({'path': 'example_successor_challenge_coverage_witness_packs.json', 'kind': 'coverage_witness_packs', 'object_id': COVERAGE_WITNESS_PACKS_ID})
    if not any(n.get('path') == 'example_successor_challenge_coverage_witness_slices.json' for n in nodes):
        nodes.append({'path': 'example_successor_challenge_coverage_witness_slices.json', 'kind': 'coverage_witness_slices', 'object_id': COVERAGE_WITNESS_SLICES_ID})
    if not any(n.get('path') == 'example_successor_challenge_answer_capsules.json' for n in nodes):
        nodes.append({'path': 'example_successor_challenge_answer_capsules.json', 'kind': 'challenge_answer_capsules', 'object_id': ANSWER_CAPSULES_ID})
    if not any(n.get('path') == 'example_successor_challenge_answer_sheets.json' for n in nodes):
        nodes.append({'path': 'example_successor_challenge_answer_sheets.json', 'kind': 'challenge_answer_sheets', 'object_id': ANSWER_SHEETS_ID})
    if not any(n.get('path') == 'example_successor_challenge_answer_cards.json' for n in nodes):
        nodes.append({'path': 'example_successor_challenge_answer_cards.json', 'kind': 'challenge_answer_cards', 'object_id': ANSWER_CARDS_ID})
    if not any(n.get('path') == 'example_successor_challenge_answer_carrier_slots.json' for n in nodes):
        nodes.append({'path': 'example_successor_challenge_answer_carrier_slots.json', 'kind': 'challenge_answer_carrier_slots', 'object_id': ANSWER_CARRIER_SLOTS_ID})
    if not any(n.get('path') == 'example_successor_challenge_answer_audit_trails.json' for n in nodes):
        nodes.append({'path': 'example_successor_challenge_answer_audit_trails.json', 'kind': 'challenge_answer_audit_trails', 'object_id': ANSWER_AUDIT_TRAILS_ID})
    if not any(n.get('path') == 'example_successor_challenge_answer_citation_dockets.json' for n in nodes):
        nodes.append({'path': 'example_successor_challenge_answer_citation_dockets.json', 'kind': 'challenge_answer_citation_dockets', 'object_id': ANSWER_CITATION_DOCKETS_ID})
    if not any(n.get('path') == 'example_successor_challenge_answer_publication_profiles.json' for n in nodes):
        nodes.append({'path': 'example_successor_challenge_answer_publication_profiles.json', 'kind': 'challenge_answer_publication_profiles', 'object_id': ANSWER_PUBLICATION_PROFILES_ID})
    if not any(n.get('path') == 'example_successor_challenge_answer_disclosure_packets.json' for n in nodes):
        nodes.append({'path': 'example_successor_challenge_answer_disclosure_packets.json', 'kind': 'challenge_answer_disclosure_packets', 'object_id': ANSWER_DISCLOSURE_PACKETS_ID})
    if not any(n.get('path') == 'example_successor_challenge_answer_escalation_ladders.json' for n in nodes):
        nodes.append({'path': 'example_successor_challenge_answer_escalation_ladders.json', 'kind': 'challenge_answer_escalation_ladders', 'object_id': ANSWER_ESCALATION_LADDERS_ID})
    if not any(n.get('path') == 'example_successor_challenge_answer_review_menus.json' for n in nodes):
        nodes.append({'path': 'example_successor_challenge_answer_review_menus.json', 'kind': 'challenge_answer_review_menus', 'object_id': ANSWER_REVIEW_MENUS_ID})
    if not any(n.get('path') == 'example_requestable_evidence_classes.json' for n in nodes):
        nodes.append({'path': 'example_requestable_evidence_classes.json', 'kind': 'requestable_evidence_classes', 'object_id': REQUESTABLE_EVIDENCE_CLASSES_ID})
    if not any(n.get('path') == 'example_public_request_contracts.json' for n in nodes):
        nodes.append({'path': 'example_public_request_contracts.json', 'kind': 'public_request_contracts', 'object_id': PUBLIC_REQUEST_CONTRACTS_ID})
    if not any(n.get('path') == 'example_request_fulfillment_certificates.json' for n in nodes):
        nodes.append({'path': 'example_request_fulfillment_certificates.json', 'kind': 'request_fulfillment_certificates', 'object_id': REQUEST_FULFILLMENT_CERTIFICATES_ID})
    if not any(n.get('path') == 'example_public_request_status_envelope.json' for n in nodes):
        nodes.append({'path': 'example_public_request_status_envelope.json', 'kind': 'public_request_status_envelope', 'object_id': PUBLIC_REQUEST_STATUS_ENVELOPES_ID})
    if not any(n.get('path') == 'example_public_request_carryforward_envelope.json' for n in nodes):
        nodes.append({'path': 'example_public_request_carryforward_envelope.json', 'kind': 'public_request_carryforward_envelope', 'object_id': PUBLIC_REQUEST_CARRYFORWARD_ENVELOPES_ID})
    if not any(n.get('path') == 'example_public_request_notice.json' for n in nodes):
        nodes.append({'path': 'example_public_request_notice.json', 'kind': 'public_request_notice', 'object_id': PUBLIC_REQUEST_NOTICES_ID})
        nodes.append({'path': 'example_public_request_notice_normal_forms.json', 'kind': 'public_request_notice_normal_forms', 'object_id': PUBLIC_REQUEST_NOTICE_NORMAL_FORMS_ID})
    if not any(n.get('path') == 'example_public_request_notice_selections.json' for n in nodes):
        nodes.append({'path': 'example_public_request_notice_selections.json', 'kind': 'public_request_notice_selections', 'object_id': PUBLIC_REQUEST_NOTICE_SELECTIONS_ID})
    if not any(n.get('path') == 'example_public_request_response_menus.json' for n in nodes):
        nodes.append({'path': 'example_public_request_response_menus.json', 'kind': 'public_request_response_menus', 'object_id': PUBLIC_REQUEST_RESPONSE_MENUS_ID})
    if not any(n.get('path') == 'example_public_request_response_packets.json' for n in nodes):
        nodes.append({'path': 'example_public_request_response_packets.json', 'kind': 'public_request_response_packets', 'object_id': PUBLIC_REQUEST_RESPONSE_PACKETS_ID})
    if not any(n.get('path') == 'example_public_request_response_packet_carryforward_profiles.json' for n in nodes):
        nodes.append({'path': 'example_public_request_response_packet_carryforward_profiles.json', 'kind': 'public_request_response_packet_carryforward_profiles', 'object_id': PUBLIC_REQUEST_RESPONSE_PACKET_CARRYFORWARD_PROFILES_ID})
    if not any(n.get('path') == 'example_public_request_response_packet_delta_ledgers.json' for n in nodes):
        nodes.append({'path': 'example_public_request_response_packet_delta_ledgers.json', 'kind': 'public_request_response_packet_delta_ledgers', 'object_id': PUBLIC_REQUEST_RESPONSE_PACKET_DELTA_LEDGERS_ID})
    if not any(n.get('path') == 'example_public_request_response_packet_refresh_notices.json' for n in nodes):
        nodes.append({'path': 'example_public_request_response_packet_refresh_notices.json', 'kind': 'public_request_response_packet_refresh_notices', 'object_id': PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_NOTICES_ID})
    if not any(n.get('path') == 'example_public_request_response_packet_refresh_notice_normal_forms.json' for n in nodes):
        nodes.append({'path': 'example_public_request_response_packet_refresh_notice_normal_forms.json', 'kind': 'public_request_response_packet_refresh_notice_normal_forms', 'object_id': PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_NOTICE_NORMAL_FORMS_ID})
    if not any(n.get('path') == 'example_public_request_response_packet_refresh_notice_selections.json' for n in nodes):
        nodes.append({'path': 'example_public_request_response_packet_refresh_notice_selections.json', 'kind': 'public_request_response_packet_refresh_notice_selections', 'object_id': PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_NOTICE_SELECTIONS_ID})
    if not any(n.get('path') == 'example_public_request_response_packet_refresh_response_menus.json' for n in nodes):
        nodes.append({'path': 'example_public_request_response_packet_refresh_response_menus.json', 'kind': 'public_request_response_packet_refresh_response_menus', 'object_id': PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_RESPONSE_MENUS_ID})
    if not any(n.get('path') == 'example_public_request_response_packet_refresh_response_packets.json' for n in nodes):
        nodes.append({'path': 'example_public_request_response_packet_refresh_response_packets.json', 'kind': 'public_request_response_packet_refresh_response_packets', 'object_id': PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_RESPONSE_PACKETS_ID})
    if not any(n.get('path') == 'example_public_request_response_packet_refresh_response_packet_closure_verdicts.json' for n in nodes):
        nodes.append({'path': 'example_public_request_response_packet_refresh_response_packet_closure_verdicts.json', 'kind': 'public_request_response_packet_refresh_response_packet_closure_verdicts', 'object_id': PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_RESPONSE_PACKET_CLOSURE_VERDICTS_ID})
    graph['nodes'] = nodes
    edges = graph.get('edges', [])
    wanted_edges = [
        {'from': 'example_successor_normal_form.json', 'to': 'example_successor_challenge_terminal_witnesses.json', 'why': 'terminal-witness ledger imports sentence-family terminal-target keys from the downstream normal form when a piece is surface-realized'},
        {'from': 'example_successor_challenge_stop_profiles.json', 'to': 'example_successor_challenge_terminal_witnesses.json', 'why': 'terminal-witness ledger imports approved stop fields from the question-keyed stop profiles'},
        {'from': 'example_successor_challenge_branches.json', 'to': 'example_successor_challenge_terminal_witnesses.json', 'why': 'terminal-witness ledger binds each piece hook to the exact branch endpoints that terminate at those approved stop fields'},
        {'from': 'example_successor_challenge_coverage.json', 'to': 'example_successor_challenge_terminal_witnesses.json', 'why': 'terminal-witness ledger instantiates only the sentence-family/piece obligations the coverage certificate says must remain auditable'},
        {'from': 'example_successor_challenge_terminal_witnesses.json', 'to': 'example_successor_challenge_surface_hooks.json', 'why': 'surface-hook ledger stays separate from terminal ownership but points to the companion piece-hook terminal witnesses'},
        {'from': 'example_successor_challenge_coverage.json', 'to': 'example_successor_challenge_coverage_witness_cores.json', 'why': 'coverage-witness cores instantiate the audience-invariant terminal and surface proving keys for each certified coverage entry'},
        {'from': 'example_successor_challenge_terminal_witnesses.json', 'to': 'example_successor_challenge_coverage_witness_cores.json', 'why': 'coverage-witness cores import the exact piece-hook terminal owners that every certified audience reuses'},
        {'from': 'example_successor_challenge_surface_hooks.json', 'to': 'example_successor_challenge_coverage_witness_cores.json', 'why': 'coverage-witness cores import any exact surface hooks shared by every certified audience of a surface-carried claim'},
        {'from': 'example_successor_challenge_coverage.json', 'to': 'example_successor_challenge_coverage_witness_packs.json', 'why': 'coverage-witness packs instantiate one aggregate route-and-branch bundle for each certified coverage entry'},
        {'from': 'example_successor_challenge_coverage_witness_cores.json', 'to': 'example_successor_challenge_coverage_witness_packs.json', 'why': 'coverage-witness packs reference the shared audience-invariant proving core for that claim'},
        {'from': 'example_successor_challenge_routes.json', 'to': 'example_successor_challenge_coverage_witness_packs.json', 'why': 'coverage-witness packs name the exact audience routes that certify each coverage claim'},
        {'from': 'example_successor_challenge_branches.json', 'to': 'example_successor_challenge_coverage_witness_packs.json', 'why': 'coverage-witness packs bind each claim to the exact route-plus-piece branches that discharge it'},
        {'from': 'example_successor_challenge_coverage_witness_packs.json', 'to': 'example_successor_challenge_coverage_witness_slices.json', 'why': 'audience-specific witness slices project each aggregate route-and-branch bundle down to one audience at a time'},
        {'from': 'example_successor_challenge_coverage_witness_cores.json', 'to': 'example_successor_challenge_coverage_witness_slices.json', 'why': 'coverage-witness slices reuse the shared audience-invariant proving core for that claim'},
        {'from': 'example_successor_challenge_routes.json', 'to': 'example_successor_challenge_coverage_witness_slices.json', 'why': 'coverage-witness slices name exactly one audience route for one audience-specific use of a coverage claim'},
        {'from': 'example_successor_challenge_branches.json', 'to': 'example_successor_challenge_coverage_witness_slices.json', 'why': 'coverage-witness slices keep only the branch keys witnessed by that single audience route'},
        {'from': 'example_successor_challenge_coverage_witness_cores.json', 'to': 'example_successor_challenge_answer_capsules.json', 'why': 'answer capsules import the shared audience-invariant proving core for one certified sentence-family piece'},
        {'from': 'example_successor_challenge_coverage_witness_slices.json', 'to': 'example_successor_challenge_answer_capsules.json', 'why': 'answer capsules import the audience-minimal route-and-branch delta for one audience-specific use of that claim'},
        {'from': 'example_successor_challenge_stop_profiles.json', 'to': 'example_successor_challenge_answer_capsules.json', 'why': 'answer capsules keep their approved terminal fields synchronized with the question-keyed stop semantics'},
        {'from': 'example_successor_challenge_terminal_witnesses.json', 'to': 'example_successor_challenge_answer_capsules.json', 'why': 'answer capsules import the exact terminal owners that the audience-specific answer may stop at'},
        {'from': 'example_successor_challenge_answer_capsules.json', 'to': 'example_successor_challenge_answer_sheets.json', 'why': 'answer sheets group the already-certified one-piece capsules into one audience-question handoff'},
        {'from': 'example_successor_challenge_routes.json', 'to': 'example_successor_challenge_answer_sheets.json', 'why': 'answer sheets name the single audience route serving that whole downstream question'},
        {'from': 'example_successor_challenge_stop_profiles.json', 'to': 'example_successor_challenge_answer_sheets.json', 'why': 'answer sheets preserve the stop-profile piece order for that downstream question'},
        {'from': 'example_successor_challenge_answer_sheets.json', 'to': 'example_successor_challenge_answer_cards.json', 'why': 'answer cards import one piece-complete audience-question handoff rather than reassembling the capsule set'},
        {'from': 'example_successor_sentence_locks.json', 'to': 'example_successor_challenge_answer_cards.json', 'why': 'answer cards import one shipped sentence lock and its default visible-provenance mode for that audience/question handoff'},
        {'from': 'example_successor_challenge_answer_cards.json', 'to': 'example_successor_challenge_answer_carrier_slots.json', 'why': 'answer carrier slots bind each emitted answer object to one exact shipped field or reusable clause'},
        {'from': 'example_successor_lineage_notice.json', 'to': 'example_successor_challenge_answer_carrier_slots.json', 'why': 'answer carrier slots may use the public wrapper field as the exact carrier of one emitted answer'},
        {'from': 'example_successor_clause_pack.json', 'to': 'example_successor_challenge_answer_carrier_slots.json', 'why': 'answer carrier slots may use a reusable checked clause as the exact carrier of one emitted answer'},
        {'from': 'example_release_closure_ledger.json', 'to': 'example_successor_challenge_answer_carrier_slots.json', 'why': 'answer carrier slots optionally import a satisfied closure role when the carrier is a shipped release wrapper field'},
        {'from': 'example_successor_challenge_answer_carrier_slots.json', 'to': 'example_successor_challenge_answer_audit_trails.json', 'why': 'answer audit trails start at one exact shipped carrier slot before walking leftward through the answer bundle'},
        {'from': 'example_successor_challenge_answer_cards.json', 'to': 'example_successor_challenge_answer_audit_trails.json', 'why': 'answer audit trails retain the emitted answer object while walking leftward from the exact carrier slot'},
        {'from': 'example_successor_challenge_answer_sheets.json', 'to': 'example_successor_challenge_answer_audit_trails.json', 'why': 'answer audit trails preserve the whole-question piece order while expanding the leftward walk'},
        {'from': 'example_successor_challenge_answer_capsules.json', 'to': 'example_successor_challenge_answer_audit_trails.json', 'why': 'answer audit trails import the one-piece audience/question bundles for each semantic piece of the answer'},
        {'from': 'example_successor_challenge_branches.json', 'to': 'example_successor_challenge_answer_audit_trails.json', 'why': 'answer audit trails import the exact route-plus-piece escalation walk for each semantic piece'},
        {'from': 'example_successor_challenge_terminal_witnesses.json', 'to': 'example_successor_challenge_answer_audit_trails.json', 'why': 'answer audit trails terminate only at the already-owned narrow terminal witnesses for each semantic piece'},
        {'from': 'example_successor_challenge_answer_capsules.json', 'to': 'example_successor_challenge_answer_citation_dockets.json', 'why': 'answer citation dockets select one-piece capsules when later notes need the smallest sufficient piece-level answer object'},
        {'from': 'example_successor_challenge_answer_sheets.json', 'to': 'example_successor_challenge_answer_citation_dockets.json', 'why': 'answer citation dockets select whole-question sheets when later notes need the complete audience/question handoff'},
        {'from': 'example_successor_challenge_answer_cards.json', 'to': 'example_successor_challenge_answer_citation_dockets.json', 'why': 'answer citation dockets select emitted answer cards when later notes need the released answer object itself'},
        {'from': 'example_successor_challenge_answer_carrier_slots.json', 'to': 'example_successor_challenge_answer_citation_dockets.json', 'why': 'answer citation dockets select carrier slots when later notes need the exact shipped answer location'},
        {'from': 'example_successor_challenge_answer_audit_trails.json', 'to': 'example_successor_challenge_answer_citation_dockets.json', 'why': 'answer citation dockets select audit trails when later notes need the full leftward reader walk'},
        {'from': 'example_successor_challenge_answer_cards.json', 'to': 'example_successor_challenge_answer_publication_profiles.json', 'why': 'answer publication profiles package common brief and expanded publication forms for one emitted answer card'},
        {'from': 'example_successor_sentence_locks.json', 'to': 'example_successor_challenge_answer_publication_profiles.json', 'why': 'answer publication profiles import the declared inline-provenance modes from the sentence lock for that emitted answer'},
        {"from": "example_successor_challenge_answer_citation_dockets.json", "to": "example_successor_challenge_answer_publication_profiles.json", "why": "answer publication profiles reuse the citation docket\'s exact-location and full-audit escalation choices"},
        {'from': 'example_successor_challenge_answer_publication_profiles.json', 'to': 'example_successor_challenge_answer_disclosure_packets.json', 'why': "answer disclosure packets reuse the publication profile's brief and expanded public answer forms"},
        {'from': 'example_successor_challenge_answer_citation_dockets.json', 'to': 'example_successor_challenge_answer_disclosure_packets.json', 'why': 'answer disclosure packets preserve the same exact-location and full-audit escalation companions used by the publication profile'},
        {'from': 'example_successor_challenge_answer_audit_trails.json', 'to': 'example_successor_challenge_answer_disclosure_packets.json', 'why': 'answer disclosure packets name the exact leftward audit slice whose terminal-owner paths must be handed over on request'},
        {'from': 'example_successor_challenge_answer_publication_profiles.json', 'to': 'example_successor_challenge_answer_escalation_ladders.json', 'why': 'answer escalation ladders import the already-declared brief and expanded inline answer forms for one audience/question pair'},
        {'from': 'example_successor_challenge_answer_citation_dockets.json', 'to': 'example_successor_challenge_answer_escalation_ladders.json', 'why': 'answer escalation ladders import the exact-location and full-audit escalation companions for that same answer'},
        {'from': 'example_successor_challenge_answer_disclosure_packets.json', 'to': 'example_successor_challenge_answer_escalation_ladders.json', 'why': 'answer escalation ladders terminate at the maintained requestable-packet handoff once the reader asks for the omitted archive slice'},
        {'from': 'example_successor_challenge_answer_publication_profiles.json', 'to': 'example_successor_challenge_answer_review_menus.json', 'why': 'answer review menus reuse the publication profile when a referee asks for the smallest or expanded inline support form'},
        {'from': 'example_successor_challenge_answer_citation_dockets.json', 'to': 'example_successor_challenge_answer_review_menus.json', 'why': 'answer review menus reuse the citation docket when a referee asks for exact location or full audit for the same answer'},
        {'from': 'example_successor_challenge_answer_disclosure_packets.json', 'to': 'example_successor_challenge_answer_review_menus.json', 'why': 'answer review menus reuse the disclosure packet when a referee asks for the exact on-request bundle to hand over'},
        {'from': 'example_successor_challenge_answer_escalation_ladders.json', 'to': 'example_successor_challenge_answer_review_menus.json', 'why': 'answer review menus reuse the escalation ladder when a referee asks for the maintained reveal order itself'},
        {'from': 'example_successor_challenge_answer_disclosure_packets.json', 'to': 'example_requestable_evidence_classes.json', 'why': 'requestable evidence classes type the omitted-support families already covered by the maintained disclosure packets'},
        {'from': 'example_requestable_evidence_classes.json', 'to': 'example_public_request_contracts.json', 'why': 'public request contracts import stable evidence-class names for the omitted-support families behind the worked note\'s source-only sentence'},
        {'from': 'example_successor_challenge_answer_review_menus.json', 'to': 'example_public_request_contracts.json', 'why': "public request contracts import the maintained review-menu choices behind the worked note's source-only public sentence"},
        {'from': 'example_successor_challenge_answer_disclosure_packets.json', 'to': 'example_public_request_contracts.json', 'why': "public request contracts import the maintained disclosure packets behind the worked note's source-only public sentence"},
        {'from': 'example_public_request_contracts.json', 'to': 'example_request_fulfillment_certificates.json', 'why': 'request fulfillment certificates certify completion for each family named by the companion public request contract'},
        {'from': 'example_requestable_evidence_classes.json', 'to': 'example_request_fulfillment_certificates.json', 'why': 'request fulfillment certificates certify completion for the typed omitted-support families imported by the public request contract'},
        {'from': 'example_successor_challenge_answer_disclosure_packets.json', 'to': 'example_request_fulfillment_certificates.json', 'why': 'request fulfillment certificates certify completion against the exact maintained disclosure packets that must be handed over on request'},
        {'from': 'example_public_request_contracts.json', 'to': 'example_public_request_status_envelope.json', 'why': 'the paper-level public request status envelope compresses only the families already owned by the public request contract'},
        {'from': 'example_request_fulfillment_certificates.json', 'to': 'example_public_request_status_envelope.json', 'why': 'the paper-level public request status envelope compresses the family-scoped completion certificates to one public token'},
        {'from': 'example_public_request_status_envelope.json', 'to': 'example_public_request_carryforward_envelope.json', 'why': 'the carryforward envelope imports the paper-level public request status token it summarizes across releases'},
        {'from': 'example_public_request_contracts.json', 'to': 'example_public_request_carryforward_envelope.json', 'why': 'the carryforward envelope checks whether the successor contract keeps the same promised families or reopens them'},
        {'from': 'example_compare_report.json', 'to': 'example_public_request_carryforward_envelope.json', 'why': 'the carryforward envelope is keyed to the same concrete base-to-successor release transition as the compare report'},
        {'from': 'example_publication_closure_verdict.json', 'to': 'example_public_request_carryforward_envelope.json', 'why': 'the carryforward envelope records the shipped successor closure context used by the current public status token'},
        {'from': 'example_public_request_status_envelope.json', 'to': 'example_public_request_notice.json', 'why': 'the within-release public-request notice wraps the paper-level status token rather than re-owning it'},
        {'from': 'example_public_request_carryforward_envelope.json', 'to': 'example_public_request_notice.json', 'why': 'the successor-carryforward public-request notice wraps the cross-release carryforward verdict rather than re-owning it'},
        {'from': 'example_public_request_contracts.json', 'to': 'example_public_request_notice.json', 'why': 'public-request notices point readers back to the exact paper-facing source-only contract behind the short sentence they saw'},
        {'from': 'example_request_fulfillment_certificates.json', 'to': 'example_public_request_notice.json', 'why': 'public-request notices point readers back to the family-scoped completion certificates when the visible sentence is challenged'},
        {'from': 'example_public_request_status_envelope.json', 'to': 'example_public_request_notice_selections.json', 'why': 'within-release notice selections import the paper-level public status token that determines which canonical wrapper family applies'},
        {'from': 'example_public_request_carryforward_envelope.json', 'to': 'example_public_request_notice_selections.json', 'why': 'successor-facing notice selections import the carryforward verdict whose token pair determines which canonical wrapper family applies'},
        {'from': 'example_public_request_notice.json', 'to': 'example_public_request_notice_selections.json', 'why': 'notice selections point to the concrete emitted notice instance whose sentence must agree with the selected canonical family'},
        {'from': 'example_public_request_notice_normal_forms.json', 'to': 'example_public_request_notice_selections.json', 'why': 'notice selections choose one maintained canonical notice normal form rather than rephrasing token-to-sentence choice inline'},
        {'from': 'example_public_request_notice_selections.json', 'to': 'example_public_request_response_menus.json', 'why': 'response menus import the emitted notice together with the canonical family selector so each follow-up class points to one already-owned object'},
        {'from': 'example_public_request_response_menus.json', 'to': 'example_public_request_response_packets.json', 'why': 'response packets start from a specific response-menu choice and then freeze the exact bounded handoff slice for that follow-up class'},
        {'from': 'example_public_request_response_packets.json', 'to': 'example_public_request_response_packet_carryforward_profiles.json', 'why': 'packet carryforward profiles classify whether one already-cut source-only response packet may be reused or must reopen under the successor release'},
        {'from': 'example_public_request_response_packet_carryforward_profiles.json', 'to': 'example_public_request_response_packet_delta_ledgers.json', 'why': 'packet delta ledgers refine refresh-in-place reuse verdicts into exact packet-local successor refresh instructions without changing the bounded slice'},
        {'from': 'example_public_request_response_packet_delta_ledgers.json', 'to': 'example_public_request_response_packet_refresh_notices.json', 'why': 'packet refresh notices compress packet-local successor refresh instructions into the exact visible reissue sentence for that reusable bounded handoff slice'},
        {'from': 'example_public_request_response_packet_refresh_notices.json', 'to': 'example_public_request_response_packet_refresh_notice_normal_forms.json', 'why': 'packet-refresh-notice normal forms factor those emitted visible reissue sentences into canonical templates and explicit slot bindings'},
        {'from': 'example_public_request_response_packet_refresh_notice_normal_forms.json', 'to': 'example_public_request_response_packet_refresh_notice_selections.json', 'why': 'packet-refresh-notice selections choose which canonical refresh-notice family was licensed by the shipped successor packet-delta basis for each emitted reissue sentence'},
        {'from': 'example_public_request_response_packet_refresh_notice_selections.json', 'to': 'example_public_request_response_packet_refresh_response_menus.json', 'why': 'packet-refresh response menus import the emitted refresh sentence together with the canonical-family selector so each successor follow-up class points to one already-owned object'},
        {'from': 'example_public_request_response_packet_refresh_response_menus.json', 'to': 'example_public_request_response_packet_refresh_response_packets.json', 'why': 'packet-refresh response packets freeze the exact bounded successor-facing handoff slice after one concrete follow-up class about an emitted packet-refresh sentence has already chosen the right owner'},
        {'from': 'example_public_request_response_packet_refresh_response_packets.json', 'to': 'example_public_request_response_packet_refresh_response_packet_closure_verdicts.json', 'why': 'packet-closure verdicts certify that one exact successor-facing packet already closes the refreshed visible-handoff branch under the shipped follow-up taxonomy'},
        {'from': 'example_public_request_response_packet_refresh_response_packet_closure_verdicts.json', 'to': 'example_series_spine.json', 'why': 'the series spine may import the maintained capstone verdict that exact successor-facing packetization already closes this visible-handoff branch'},
        {'from': 'example_public_request_response_packet_refresh_response_packets.json', 'to': 'example_series_spine.json', 'why': 'the series spine may import the exact bounded successor-facing handoff slice after packet-refresh follow-up choice has already been fixed'},
        {'from': 'example_public_request_notice_selections.json', 'to': 'example_series_spine.json', 'why': 'the series spine imports the token-keyed normal-form selector so public-request notice choice stays explicit across the release-evolution bridge'},
        {'from': 'example_requestable_evidence_classes.json', 'to': 'example_series_spine.json', 'why': 'the series spine imports stable omitted-support family names so answer spines can stay terse while still characterizing the requestable support behind one review handoff'},
    ]
    existing = {(e.get('from'), e.get('to')) for e in edges}
    for e in wanted_edges:
        if (e['from'], e['to']) not in existing:
            edges.append(e)
    graph['edges'] = edges

    ensure_inventory_entry(inventory, 'example_successor_challenge_terminal_witnesses.json', 'piece-hook terminal-witness ledger for one successor comparison', ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_successor_challenge_coverage_witness_cores.json', 'coverage witness-core ledger for one successor comparison', ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_successor_challenge_coverage_witness_packs.json', 'coverage witness-pack ledger for one successor comparison', ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_successor_challenge_coverage_witness_slices.json', 'coverage witness-slice ledger for one successor comparison', ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_successor_challenge_answer_capsules.json', 'audience-question answer-capsule ledger for one successor comparison', ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_successor_challenge_answer_sheets.json', 'audience-question answer-sheet ledger for one successor comparison', ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_successor_challenge_answer_cards.json', 'audience-question answer-card ledger for one successor comparison', ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_successor_challenge_answer_carrier_slots.json', 'audience-question answer-carrier-slot ledger for one successor comparison', ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_successor_challenge_answer_audit_trails.json', 'audience-question answer-audit-trail ledger for one successor comparison', ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_successor_challenge_answer_citation_dockets.json', 'audience-question answer-citation-docket ledger for one successor comparison', ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_successor_challenge_answer_publication_profiles.json', 'audience-question answer-publication-profile ledger for one successor comparison', ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_successor_challenge_answer_disclosure_packets.json', 'audience-question answer-disclosure-packet ledger for one successor comparison', ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_successor_challenge_answer_escalation_ladders.json', 'audience-question answer-escalation-ladder ledger for one successor comparison', ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_successor_challenge_answer_review_menus.json', 'audience-question answer-review-menu ledger for one successor comparison', ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_requestable_evidence_classes.json', 'stable evidence-class ledger for the worked note\'s omitted-support families', ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_public_request_contracts.json', 'paper-facing source-only handoff contract for the worked note', ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_request_fulfillment_certificates.json', "family-scoped completion certificates for the worked note's source-only request promises", ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_public_request_status_envelope.json', "paper-level source-only request-status envelope for the worked note", ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_public_request_carryforward_envelope.json', "successor-release carryforward envelope for the worked note's source-only request status", ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_public_request_notice.json', 'outward-facing source-only public-request notices for the worked note', ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_public_request_notice_normal_forms.json', 'canonical source-only public-request notice normal forms for the worked note', ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_public_request_notice_selections.json', 'token-keyed selector ledger choosing the canonical source-only public-request notice normal form for the worked note', ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_public_request_response_menus.json', "notice-keyed response-menu ledger for the worked note's source-only public-request follow-up classes", ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_public_request_response_packets.json', "notice-and-follow-up keyed response-packet ledger for the worked note's source-only public-request handoffs", ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_public_request_response_packet_carryforward_profiles.json', "successor-release carryforward-profile ledger for the worked note's exact source-only response packets", ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_public_request_response_packet_delta_ledgers.json', "successor-release delta ledger for the worked note's reusable exact source-only response packets", ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_public_request_response_packet_refresh_notices.json', "successor-release visible refresh-notice ledger for the worked note's reusable exact source-only response packets", ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_public_request_response_packet_refresh_notice_normal_forms.json', "canonical successor-release refresh-notice normal-form ledger for the worked note's reusable exact source-only response packets", ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_public_request_response_packet_refresh_notice_selections.json', "token-keyed successor-release refresh-notice selection ledger for the worked note's reusable exact source-only response packets", ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_public_request_response_packet_refresh_response_menus.json', "successor-facing response-menu ledger for concrete follow-up classes about the worked note's visible packet-refresh notices", ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_public_request_response_packet_refresh_response_packets.json', "successor-facing response-packet ledger for exact bounded handoff slices about the worked note's visible packet-refresh notices", ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_public_request_response_packet_refresh_response_packet_closure_verdicts.json', "successor-facing closure-verdict ledger certifying stable finite basis for exact bounded handoff slices about the worked note's visible packet-refresh notices", ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_series_spine.json', 'theorem-to-review bridge for the worked line items and shipped audience/question answers', ['maintainer', 'referee', 'release_note', 'auditor'])
    ensure_inventory_entry(inventory, 'example_question_routes.json', 'question-to-first-stop routing catalog for the worked line items and shipped audience/question answers', ['maintainer', 'referee', 'release_note', 'auditor'])
    # Refresh after ensure_inventory_entry mutations so later route-side inventory cuts
    # see maintained group / visibility / role metadata rather than fallback stubs.
    inventory_index = {
        entry['path']: {**entry, 'group': group.get('group'), 'visibility': group.get('visibility')}
        for group in inventory.get('groups', [])
        for entry in group.get('entries', [])
    }

    replay_plan_index = {entry.get('plan_id'): entry for entry in replay_plans.get('plans', [])}
    support_bundle_index = {entry.get('bundle_id'): entry for entry in support_bundle_map.get('bundles', [])}
    answer_menu_index = {(entry.get('audience'), entry.get('question_key')): entry for entry in answer_review_menus.get('answer_review_menus', [])}
    line_item_release_questions = {
        'primary_path_declaration': [('release_note', 'public_status_sentence'), ('referee', 'public_status_sentence')],
        'fallback_contact_surface': [('release_note', 'compact_diff_summary'), ('auditor', 'compact_diff_summary')],
        'fallback_tiered_vector': [('release_note', 'compact_diff_summary'), ('auditor', 'compact_diff_summary')],
        'path_selection_indicator': [('release_note', 'compact_diff_summary'), ('auditor', 'compact_diff_summary')],
        'profiling_equalization': [('referee', 'public_status_sentence'), ('auditor', 'compact_diff_summary')],
    }
    line_item_release_stage_hints = {
        'primary_path_declaration': ['diff', 'classify', 'summarize', 'support', 'cite', 'quote', 'clause'],
        'fallback_contact_surface': ['diff', 'classify', 'support', 'cite', 'quote', 'clause'],
        'fallback_tiered_vector': ['diff', 'classify', 'support', 'cite', 'quote', 'clause'],
        'path_selection_indicator': ['diff', 'classify', 'support', 'cite', 'quote', 'clause'],
        'profiling_equalization': ['diff', 'classify', 'obligate', 'close', 'summarize', 'support', 'cite', 'quote', 'clause'],
    }
    owner_map_spine_only_current_cut = {
        'retry_schedule_packet',
        'runtime_conformance_packet',
        'calibration_recipe_packet',
        'congestion_epoch_contract',
        'pscq_mechanism_packet',
        'bossfight_dialsheet_packet',
        'bossfight_verifier_bundle',
        'routing_signature_manifest',
    }
    line_item_spines = []
    for entry in line_item_owner_map.get('entries', []):
        is_owner_map_only = (
            entry.get('name') in owner_map_spine_only_current_cut
            or entry.get('materialization_status') == 'owner_map_spine_only_current_cut'
        )
        review_refs = []
        for audience, question in line_item_release_questions.get(entry.get('name'), []):
            menu = answer_menu_index.get((audience, question))
            if menu is not None:
                review_refs.append({
                    'audience': audience,
                    'question_key': question,
                    'answer_review_menu_key': menu.get('answer_review_menu_key'),
                    'answer_review_menu_artifact': 'example_successor_challenge_answer_review_menus.json',
                    'start_path': menu.get('start_path'),
                    'sentence_family': menu.get('sentence_family'),
                })
        plan = replay_plan_index.get(entry.get('replay_plan_id'), {})
        if is_owner_map_only:
            receipt_anchor = {
                'artifact': 'example_line_item_owner_map.json',
                'line_item_name': entry.get('name'),
                'exposure_nf_id': entry.get('exposure_nf_id'),
                'public_objects': entry.get('public_objects', []),
                'public_objects_status': entry.get('public_objects_status'),
                'materialization_status': 'owner_map_spine_only_current_cut',
                'not_materialized_in': entry.get('not_materialized_as_packet_in', ['example_receipt.json']),
            }
            replay_anchor = {
                'artifact': 'example_series_spine.json',
                'plan_id': entry.get('replay_plan_id'),
                'plan_spec_id': None,
                'artifact_bundle': None,
                'evidence_id': entry.get('evidence_id'),
                'plan_catalog_status': 'not_materialized_current_cut',
                'replay_plan_id_status': entry.get('replay_plan_id_status'),
                'not_materialized_in': [
                    path for path in entry.get('not_materialized_as_packet_in', ['example_replay_plans.json', 'example_support_bundle_map.json'])
                    if path in {'example_replay_plans.json', 'example_support_bundle_map.json', 'example_verifier_report.json'}
                ],
            }
            surface_text = f"For the owner-map / series-spine ladder {entry.get('name')}, stop at the maintained owner-map route row while the live issue is still this route split; this current cut does not emit a receipt line item, plan-catalog row, support-bundle route, or verifier packet for it."
            stop_when = 'The live issue is this owner-map / series-spine route row rather than an emitted receipt/support/verifier packet, so the route split already answers the question without reopening a concrete audience/question route.'
            why_text = 'One maintained owner-map / series-spine bridge from mathematical root to the downstream review owners most likely to be cited for this family; packet materialization is explicitly absent in this cut.'
        else:
            carrier_artifact = entry.get('receipt_file') or entry.get('verifier_report_file') or 'example_receipt.json'
            bundle_id = entry.get('support_bundle_id') or plan.get('artifact_bundle')
            bundle = support_bundle_index.get(bundle_id, {}) if bundle_id else {}
            receipt_anchor = {
                'artifact': carrier_artifact,
                'line_item_name': entry.get('name'),
                'exposure_nf_id': entry.get('exposure_nf_id'),
                'materialization_status': entry.get('materialization_status', 'base_receipt_current_cut'),
                'receipt_file': entry.get('receipt_file'),
                'verifier_report_file': entry.get('verifier_report_file'),
                'support_bundle_id': bundle_id,
                'public_objects': entry.get('public_objects', []),
            }
            replay_anchor = {
                'artifact': 'example_replay_plans.json',
                'plan_id': entry.get('replay_plan_id'),
                'plan_spec_id': entry.get('plan_spec_id') or plan.get('plan_spec_id'),
                'artifact_bundle': bundle_id,
                'support_bundle_id': bundle_id,
                'evidence_id': entry.get('evidence_id'),
            }
            support_anchor = {
                'artifact': 'example_support_bundle_map.json',
                'support_bundle_id': bundle_id,
                'required_artifacts': entry.get('support_required_artifacts', bundle.get('required_artifacts', [])),
                'support_pointers': entry.get('support_pointers', bundle.get('support_pointers', [])),
            }
            surface_text = f"For the packet-local ladder {entry.get('name')}, stop at the maintained line-item bridge while the live issue is still this one exact carried line item together with its immediate mathematical, receipt, replay, and release neighbors."
            stop_when = 'The live issue is this one exact carried line item together with its immediate mathematical, receipt, replay, and release neighbors, so the packet-local ladder already answers the question without reopening a concrete audience/question route.'
            why_text = 'One maintained line-item bridge from mathematical root through receipt and replay to the downstream review objects most likely to be cited for this family.'
        spine_entry = {
            'line_item_name': entry.get('name'),
            'math_roots': {'owner_notes': entry.get('owner_notes', []), 'backbone_wikilinks': entry.get('backbone_wikilinks', [])},
            'receipt_anchor': receipt_anchor,
            'replay_anchor': replay_anchor,
            'release_anchor': {'artifact': 'example_release_spine.json', 'stage_order': release_spine.get('stage_order', []), 'stages_most_likely_to_move': line_item_release_stage_hints.get(entry.get('name'), []), 'compare_artifact': 'example_compare_report.json', 'continuity_artifact': 'example_successor_continuity_verdict.json'},
            'review_anchor': review_refs,
            'packet_local_sentence_normal_form': {
                'line_item_name': entry.get('name'),
                'surface_text': surface_text,
                'reopen_artifact': 'example_question_routes.json',
                'why': 'This sentence is only the one-clause rendering of the already-owned local ladder; it does not re-own the fuller audience/question route.'
            },
            'stop_when': stop_when,
            'widen_only_if': 'Widen only if the live issue becomes exact checked-answer wording, the first bounded omitted-support packet, or the stop/widen/reopen judgment for one maintained audience/question route in example_question_routes.json.',
            'route_local_reopen_artifact': 'example_question_routes.json',
            'route_local_reopen_rule': 'If exact checked-answer wording, the first bounded omitted-support packet, or the stop/widen/reopen judgment for one maintained audience/question route becomes live, reopen example_question_routes.json and stop at the first sufficient audience/question route instead of staying at the local ladder.',
            'why': why_text
        }
        if not is_owner_map_only:
            spine_entry['support_anchor'] = support_anchor
        line_item_spines.append(spine_entry)
    support_bundle_index = {entry.get('bundle_id'): entry for entry in support_bundle_map.get('bundles', [])}
    optional_variant_spines = []
    for entry in line_item_owner_map.get('variant_entries', []):
        plan = replay_plan_index.get(entry.get('replay_plan_id'), {})
        bundle = support_bundle_index.get(entry.get('support_bundle_id'), {})
        receipt_variant_file = entry.get('receipt_variant_file')
        line_item_name = entry.get('name')
        public_objects = entry.get('public_objects', [])
        variant_sentence = {
            'line_item_name': line_item_name,
            'surface_text': (
                f"For the optional variant receipt {line_item_name}, stop at {receipt_variant_file} "
                "and the matching variant owner-map row only while the live issue is the declared profiling variant itself."
            ),
            'receipt_variant_file': receipt_variant_file,
            'reopen_artifact': 'example_question_routes.json',
            'why': 'This is a variant-receipt shortcut, not a base-receipt ladder and not an owner-map-only route label.'
        }
        optional_variant_spine = {
            'line_item_name': line_item_name,
            'materialization_status': entry.get('materialization_status'),
            'receipt_variant_file': receipt_variant_file,
            'evidence_id': entry.get('evidence_id'),
            'receipt_anchor': {
                'artifact': receipt_variant_file,
                'line_item_name': line_item_name,
                'exposure_nf_id': entry.get('exposure_nf_id'),
                'materialization_status': entry.get('materialization_status'),
                'public_objects': public_objects,
            },
            'owner_map_anchor': {
                'artifact': 'example_line_item_owner_map.json',
                'section': 'variant_entries',
                'line_item_name': line_item_name,
                'plan_spec_id': entry.get('plan_spec_id') or plan.get('plan_spec_id'),
                'support_bundle_id': entry.get('support_bundle_id'),
                'support_required_artifacts': entry.get('support_required_artifacts', bundle.get('required_artifacts', [])),
                'support_pointers': entry.get('support_pointers', bundle.get('support_pointers', [])),
                'coarsening_map_id': entry.get('coarsening_map_id'),
            },
            'replay_anchor': {
                'artifact': 'example_replay_plans.json',
                'plan_id': entry.get('replay_plan_id'),
                'plan_spec_id': entry.get('plan_spec_id') or plan.get('plan_spec_id'),
                'artifact_bundle': entry.get('support_bundle_id'),
                'support_bundle_id': entry.get('support_bundle_id'),
                'evidence_id': entry.get('evidence_id'),
            },
            'support_anchor': {
                'artifact': 'example_support_bundle_map.json',
                'support_bundle_id': entry.get('support_bundle_id'),
                'required_artifacts': entry.get('support_required_artifacts', bundle.get('required_artifacts', [])),
                'support_pointers': entry.get('support_pointers', bundle.get('support_pointers', [])),
            },
            'variant_sentence_normal_form': variant_sentence,
            'stop_when': 'The live issue is this optional profiling variant receipt and its declared evidence/replay/support row, not the base profiling receipt or a nonmaterialized route label.',
            'widen_only_if': 'Widen only if the live issue leaves the variant receipt itself for the base profiling contract, the coarsening/selection theorem, or a concrete audience/question route.',
            'route_local_reopen_artifact': 'example_question_routes.json',
            'route_local_reopen_rule': 'If the variant receipt shortcut is no longer sufficient, reopen example_question_routes.json or the named owner note for the base profiling/coarsening theorem before citing the variant row again.',
            'why': 'Optional profiling variants are materialized receipt variants in this cut, so they need a mechanically quotable spine distinct from both base line-item spines and owner-map-only boundary rows.',
        }
        if entry.get('coarsening_map_id') is not None:
            optional_variant_spine['coarsening_map_id'] = entry.get('coarsening_map_id')
        optional_variant_spines.append(optional_variant_spine)

    answer_support_map = {
        ('release_note', 'public_status_sentence'): ['primary_path_declaration', 'profiling_equalization'],
        ('referee', 'public_status_sentence'): ['primary_path_declaration', 'profiling_equalization'],
        ('release_note', 'compact_diff_summary'): ['fallback_contact_surface', 'fallback_tiered_vector', 'path_selection_indicator'],
        ('auditor', 'compact_diff_summary'): ['fallback_contact_surface', 'fallback_tiered_vector', 'path_selection_indicator', 'profiling_equalization'],
    }
    challenge_route_index = {(entry.get('audience'), entry.get('question_key')): entry for entry in routes.get('routes', [])}
    answer_cards_by_key = {entry['answer_card_key']: entry for entry in answer_cards.get('answer_cards', [])}
    publication_profiles_by_key = {entry['answer_publication_profile_key']: entry for entry in answer_publication_profiles.get('answer_publication_profiles', [])}
    citation_dockets_by_key = {entry['answer_citation_docket_key']: entry for entry in answer_citation_dockets.get('answer_citation_dockets', [])}
    sentence_locks_by_key = {entry['lock_key']: entry for entry in sentence_locks.get('locks', [])}
    answer_spines = []
    for menu in answer_review_menus.get('answer_review_menus', []):
        key = (menu.get('audience'), menu.get('question_key'))
        challenge_route = challenge_route_index.get(key, {})
        publication_profile = publication_profiles_by_key[menu.get('answer_publication_profile_key')]
        citation_docket = citation_dockets_by_key[menu.get('answer_citation_docket_key')]
        answer_card = answer_cards_by_key[publication_profile.get('answer_card_key')]
        sentence_lock = sentence_locks_by_key[answer_card.get('sentence_lock_key')]
        default_inline_profile = sentence_lock.get('comparison_anchor', {}).get('default_inline_profile', {})
        publication_budget_map = {
            'brief_inline': publication_profile.get('default_inline_entry'),
            'expanded_inline': publication_profile.get('expanded_inline_entry'),
            'exact_location': publication_profile.get('exact_location_entry'),
            'full_audit': publication_profile.get('full_audit_entry'),
        }
        request_class_handoff_map = {entry.get('request_class'): entry.get('selected_entry') for entry in menu.get('review_entries', [])}
        answer_review_request_class_mode_map = {entry.get('request_class'): entry.get('review_request_class_vocabulary_mode') for entry in menu.get('review_entries', [])}
        ladder = ladders_by_key[menu.get('answer_escalation_ladder_key')]
        answer_escalation_step_mode_map = {entry.get('step_key'): entry.get('escalation_step_vocabulary_mode') for entry in ladder.get('ordered_steps', [])}
        release_stage_vocabulary_mode_map = {entry.get('stage'): entry.get('release_stage_vocabulary_mode') for entry in release_spine.get('stage_order', []) if entry.get('stage') in (['summarize', 'support', 'cite', 'quote', 'clause'] if menu.get('question_key') == 'public_status_sentence' else ['diff', 'classify', 'support', 'cite', 'quote', 'clause'])}
        request_class_owner_map = {
            entry.get('request_class'): {
                'owner_object_kind': entry.get('object_kind'),
                'owner_object_key': entry.get('object_key'),
                'owner_cite_path': entry.get('cite_path'),
                'selected_object_kind': (entry.get('selected_entry') or {}).get('object_kind'),
                'selected_object_key': (entry.get('selected_entry') or {}).get('object_key'),
                'why': entry.get('why'),
            }
            for entry in menu.get('review_entries', [])
        }
        answer_side_terminal_first_reopen_owner_map = {
            request_class: request_class_owner_map[request_class]
            for request_class in ['exact_location_check', 'full_audit_check', 'reveal_order_check']
            if request_class in request_class_owner_map
        }
        answer_spines.append({
            'audience': menu.get('audience'),
            'question_key': menu.get('question_key'),
            'challenge_route_key': challenge_route.get('route_key'),
            'answer_side_terminal_citation_normal_form': menu.get('answer_side_terminal_citation_normal_form'),
            'answer_side_terminal_sentence_normal_form': menu.get('answer_side_terminal_sentence_normal_form'),
            'answer_side_terminal_stop_when': 'The live question is still exhausted by the checked answer, its answer-side disclosure-packet cut, and the review-menu handoff, so exact-location, full-audit, reveal-order, or a genuine crossing into the adjacent source-only branch has not yet become the live issue.',
            'answer_side_terminal_widen_only_if': 'Widen only if the live question has genuinely crossed the answer-side archive cut into the adjacent source-only branch and the first sufficient adjacent owner bucket has already been fixed.',
            'answer_side_terminal_reopen_artifact': 'example_question_routes.json',
            'answer_side_terminal_first_reopen_owner_map': answer_side_terminal_first_reopen_owner_map,
            'answer_side_terminal_reopen_rule': 'If exact-location, full-audit, or reveal-order becomes live, reopen example_question_routes.json and follow answer_side_terminal_first_reopen_owner_map to the first sufficient imported answer-side owner instead of staying at the terminal sentence.',
            'stop_profile_key': challenge_route.get('stop_profile_key') or menu.get('question_key'),
            'answer_review_menu_key': menu.get('answer_review_menu_key'),
            'start_path': menu.get('start_path'),
            'sentence_family': menu.get('sentence_family'),
            'answer_card_key': answer_card.get('answer_card_key'),
            'sentence_lock_key': answer_card.get('sentence_lock_key'),
            'sentence_reuse_status': answer_card.get('sentence_reuse_status'),
            'default_inline_profile_key': default_inline_profile.get('profile_key'),
            'default_visible_provenance_fields': next((entry.get('visible_fields', []) for entry in sentence_lock.get('comparison_anchor', {}).get('inline_provenance_profiles', []) if entry.get('profile_key') == default_inline_profile.get('profile_key')), []),
            'supporting_line_item_names': answer_support_map.get(key, []),
            'release_stage_families': ['summarize', 'support', 'cite', 'quote', 'clause'] if menu.get('question_key') == 'public_status_sentence' else ['diff', 'classify', 'support', 'cite', 'quote', 'clause'],
            'release_stage_vocabulary_mode_map': release_stage_vocabulary_mode_map,
            'publication_profile_key': menu.get('answer_publication_profile_key'),
            'publication_budget_map': publication_budget_map,
            'answer_review_request_class_mode_map': answer_review_request_class_mode_map,
            'answer_escalation_step_mode_map': answer_escalation_step_mode_map,
            'paired_terminal_answer_reopen_request_classes': ['exact_location_check', 'full_audit_check', 'reveal_order_check'],
            'paired_terminal_cutover_mode': 'answer_first_then_adjacent_request_capstone_else_reopen_named_owner',
            'paired_terminal_widen_condition': 'leave_answer_archive_cut_for_adjacent_source_only_branch',
            'paired_terminal_request_reopen_triggers': ['followup_taxonomy_expands', 'packet_reuse_reopens', 'visible_refresh_sentence_rebinds_to_new_delta_family'],
            'paired_terminal_cutover_sentence_normal_form': {
                'surface_text': 'For the paired-terminal cutover, stop at the answer-side terminal form while the checked-answer path still exhausts the live question; widen exactly once to the adjacent request-side terminal form only after the live question has crossed the answer-side archive cut, the first sufficient adjacent owner bucket and exact request rung are already fixed, and the shipped request-side closure still stands; otherwise fail closed and reopen the named owner.',
                'request_terminal_artifact': 'example_public_request_response_packet_refresh_response_packet_closure_verdicts.json',
                'reopen_artifact': 'example_question_routes.json',
                'why': 'This is the smallest maintained cutover card for later terse papers: it does not re-own either terminal form, but it states when the paired shortcut still stops, when it may widen once, and when it must fail closed.'
            },
            'paired_terminal_stop_when': 'The live issue is the cutover judgment itself: whether one branch still stops at the answer-side terminal form, may widen exactly once to the adjacent request-side terminal form, or must fail closed to a reopened owner.',
            'paired_terminal_request_terminal_artifact': 'example_public_request_response_packet_refresh_response_packet_closure_verdicts.json',
            'paired_terminal_request_terminal_kind': 'public_request_response_packet_refresh_response_packet_closure_verdict',
            'paired_terminal_request_terminal_widen_only_if': 'Widen only if the live question has already fixed the first sufficient adjacent owner bucket and the first sufficient exact request rung, and the shipped request-side closure still stands with no named request-side reopen trigger fired.',
            'paired_terminal_reopen_artifact': 'example_question_routes.json',
            'paired_terminal_fail_closed_reopen_rule': "If exact-location, full-audit, reveal-order, followup_taxonomy_expands, packet_reuse_reopens, or visible_refresh_sentence_rebinds_to_new_delta_family becomes live, reopen example_question_routes.json and follow the answer-side first-reopen owner or the request-side closure verdict's reopen-owner map instead of citing a terminal shortcut.",
            'request_class_handoff_map': request_class_handoff_map,
            'request_class_owner_map': request_class_owner_map,
            'citation_docket_key': menu.get('answer_citation_docket_key'),
            'answer_carrier_slot_key': citation_docket.get('exact_carrier_entry', {}).get('object_key'),
            'answer_audit_trail_key': citation_docket.get('full_audit_entry', {}).get('object_key'),
            'disclosure_packet_key': menu.get('answer_disclosure_packet_key'),
            'evidence_class_keys': disclosure_packets_by_key[menu.get('answer_disclosure_packet_key')].get('evidence_class_keys', []),
            'escalation_ladder_key': menu.get('answer_escalation_ladder_key'),
            'why': 'One maintained answer bridge from its public anchor through the governing stop profile, emitted answer, sentence lock, inherited brief/expanded/exact/full-audit publication forms, the imported six-class request handoff map, the mirrored answer-review request-class vocabulary posture map, the mirrored answer-escalation-step vocabulary posture map, the mirrored release-stage-vocabulary posture map, the imported six-class request owner map, the mirrored paired-terminal cutover contract naming when later terse papers may stop, widen, or fail closed, including a quotable cutover sentence, request-side floor, widening precondition, and fail-closed reopen rule, together with the answer-side terminal stop/widen/reopen contract plus its first-reopen-owner map, and the exact citation-docket / answer-carrier-slot / answer-audit-trail handoff seam, and the exact review menu for that audience/question handoff.'
        })
    requestable_evidence_classes = {
        'requestable_evidence_classes_id': REQUESTABLE_EVIDENCE_CLASSES_ID,
        'claim_id': compare_report['claim_id'],
        'base_release_id': compare_report['base_release_id'],
        'release_id': compare_report['release_id'],
        'successor_release_id': compare_report['successor_release_id'],
        'compare_profile_id': compare_report['compare_profile_id'],
        'compare_report_id': compare_report['report_id'],
        'support_manifest_id': support_manifest['manifest_id'],
        'artifact_inventory_id': inventory['inventory_id'],
        'successor_challenge_answer_disclosure_packets_id': answer_disclosure_packets['challenge_answer_disclosure_packets_id'],
        'note_version': compare_report['note_version'],
        'contract': {
            'evidence_class_fields': ['evidence_class_key', 'public_anchor_family_keys', 'minimal_public_anchor_paths', 'canonical_support_paths', 'covered_disclosure_packet_keys', 'completion_scope', 'evidence_class_vocabulary_mode', 'shared_across_family_keys', 'why'],
            'family_binding_rule': 'Every public_anchor_family_key must resolve to one family in the companion public request contract and every minimal public anchor path must be one of that family\'s public paths.',
            'packet_binding_rule': 'Every covered disclosure packet key must resolve to one maintained disclosure packet whose request_packet_paths cover the canonical support paths for that class, up to the shared validator companions listed by the bundle-identity class.',
            'contract_binding_rule': 'Every family named by the companion public request contract must import at least one evidence class and the union of those classes must cover both validator companions and the family-specific omitted-support slice.'
        },
        'evidence_classes': [
            {
                'evidence_class_key': 'bundle_identity_and_validator_companions',
                'public_anchor_family_keys': ['public_status_sentence_family', 'compact_diff_summary_family'],
                'minimal_public_anchor_paths': ['example_successor_lineage_notice.json', 'example_compare_report.json'],
                'canonical_support_paths': ['support_manifest.json', 'example_artifact_inventory.json', 'example_validation_report.json', '../tools/validate_example.py'],
                'covered_disclosure_packet_keys': [
                    'release_note_public_status_sentence_answer_disclosure_packet',
                    'referee_public_status_sentence_answer_disclosure_packet',
                    'release_note_compact_diff_summary_answer_disclosure_packet',
                    'auditor_compact_diff_summary_answer_disclosure_packet'
                ],
                'completion_scope': 'family_scoped_import',
                'evidence_class_vocabulary_mode': 'imported_vocabulary_class_owned_meaning',
                'shared_across_family_keys': ['public_status_sentence_family', 'compact_diff_summary_family'],
                'why': 'Every on-request handoff must preserve bundle identity and the recheck hook, regardless of which public anchor family the reader starts from.'
            },
            {
                'evidence_class_key': 'public_status_lineage_and_closure_support',
                'public_anchor_family_keys': ['public_status_sentence_family'],
                'minimal_public_anchor_paths': ['example_successor_lineage_notice.json', 'example_successor_claim_support_map.json'],
                'canonical_support_paths': ['example_successor_lineage_notice.json', 'example_successor_claim_support_map.json', 'example_successor_continuity_verdict.json', 'example_publication_closure_verdict.json', 'example_release_closure_ledger.json'],
                'covered_disclosure_packet_keys': [
                    'release_note_public_status_sentence_answer_disclosure_packet',
                    'referee_public_status_sentence_answer_disclosure_packet'
                ],
                'completion_scope': 'family_scoped_import',
                'evidence_class_vocabulary_mode': 'imported_vocabulary_class_owned_meaning',
                'shared_across_family_keys': ['public_status_sentence_family'],
                'why': 'The public-status family needs the continuity and closure slice that makes the outward-facing lineage sentence auditable.'
            },
            {
                'evidence_class_key': 'compact_diff_compare_and_replay_support',
                'public_anchor_family_keys': ['compact_diff_summary_family'],
                'minimal_public_anchor_paths': ['example_compare_report.json', 'example_successor_clause_pack.json'],
                'canonical_support_paths': ['example_compare_report.json', 'example_successor_clause_pack.json', 'example_successor_continuity_verdict.json', 'example_verifier_report.json'],
                'covered_disclosure_packet_keys': [
                    'release_note_compact_diff_summary_answer_disclosure_packet',
                    'auditor_compact_diff_summary_answer_disclosure_packet'
                ],
                'completion_scope': 'family_scoped_import',
                'evidence_class_vocabulary_mode': 'imported_vocabulary_class_owned_meaning',
                'shared_across_family_keys': ['compact_diff_summary_family'],
                'why': 'The compact-diff family needs the compare and replay slice that makes the terse changed-fields sentence auditable.'
            }
        ],
        'note': 'Derived requestable-evidence-class ledger for the worked note. It gives stable names to the omitted-support families that disclosure packets and paper-facing public request contracts already hand over, while making explicit which classes are shared across families and still completed only through family-scoped certificates.'
    }

    public_request_contracts = {
        'public_request_contracts_id': PUBLIC_REQUEST_CONTRACTS_ID,
        'claim_id': compare_report['claim_id'],
        'base_release_id': compare_report['base_release_id'],
        'release_id': compare_report['release_id'],
        'successor_release_id': compare_report['successor_release_id'],
        'compare_profile_id': compare_report['compare_profile_id'],
        'compare_report_id': compare_report['report_id'],
        'support_manifest_id': support_manifest['manifest_id'],
        'artifact_inventory_id': inventory['inventory_id'],
        'successor_challenge_answer_review_menus_id': answer_review_menus['challenge_answer_review_menus_id'],
        'successor_challenge_answer_disclosure_packets_id': answer_disclosure_packets['challenge_answer_disclosure_packets_id'],
        'requestable_evidence_classes_id': requestable_evidence_classes['requestable_evidence_classes_id'],
        'question_routes_id': QUESTION_ROUTES_ID,
        'successor_request_fulfillment_certificates_id': REQUEST_FULFILLMENT_CERTIFICATES_ID,
        'note_version': compare_report['note_version'],
        'contract': {
            'public_request_contract_fields': ['public_request_contract_key', 'paper_key', 'paper_path', 'policy_anchor', 'public_anchor_families', 'covered_review_menu_keys', 'covered_disclosure_packet_keys', 'covered_evidence_class_keys', 'covered_request_fulfillment_certificate_keys', 'validation_paths', 'request_phrase', 'why'],
            'policy_anchor_fields': ['cite_key', 'paper_path', 'why'],
            'public_anchor_family_fields': ['family_key', 'question_key', 'audiences', 'public_paths', 'review_menu_keys', 'disclosure_packet_keys', 'evidence_class_keys', 'request_fulfillment_certificate_keys', 'public_anchor_family_vocabulary_mode', 'why'],
            'shared_public_anchor_family_vocabulary_rule': 'Repeated public-anchor-family keys may recur in later evidence-class ledgers, fulfillment certificates, routes, and series-spine mirrors only as imported contract vocabulary; those later objects do not thereby re-own the public-path, review-menu, or disclosure-packet basis attached to that family.',
            'maintained_cut_rule': 'Every listed review menu, disclosure packet, and validation path must already exist in the maintained worked release and remain bound in the support manifest and artifact inventory.'
        },
        'public_request_contracts': [
            {
                'public_request_contract_key': 'worked_example_receipt_interlock_public_request_contract',
                'paper_key': 'worked_example_receipt_interlock',
                'paper_path': 'series/synthesis/paper17_worked_example_receipt_interlock/paper.tex',
                'policy_anchor': {'cite_key': 'series:artifactpolicy', 'paper_path': 'series/synthesis/paper6_artifact_policy/paper.tex', 'why': 'The worked note imports the archive-wide source-only artifact policy rather than restating it.'},
                'public_anchor_families': [
                    {
                        'family_key': 'public_status_sentence_family',
                        'question_key': 'public_status_sentence',
                        'audiences': ['release_note', 'referee'],
                        'public_paths': ['example_successor_lineage_notice.json', 'example_successor_claim_support_map.json'],
                        'review_menu_keys': ['release_note_public_status_sentence_answer_review_menu', 'referee_public_status_sentence_answer_review_menu'],
                        'disclosure_packet_keys': ['release_note_public_status_sentence_answer_disclosure_packet', 'referee_public_status_sentence_answer_disclosure_packet'],
                        'evidence_class_keys': ['bundle_identity_and_validator_companions', 'public_status_lineage_and_closure_support'],
                        'request_fulfillment_certificate_keys': ['public_status_sentence_request_fulfillment_certificate'],
                        'public_anchor_family_vocabulary_mode': 'imported_contract_vocabulary_contract_owned_basis',
                        'why': "The public status family is the outward-facing source-only anchor for the worked note's continuity/closure sentence and its referee-facing follow-up path."
                    },
                    {
                        'family_key': 'compact_diff_summary_family',
                        'question_key': 'compact_diff_summary',
                        'audiences': ['release_note', 'auditor'],
                        'public_paths': ['example_compare_report.json', 'example_successor_clause_pack.json'],
                        'review_menu_keys': ['release_note_compact_diff_summary_answer_review_menu', 'auditor_compact_diff_summary_answer_review_menu'],
                        'disclosure_packet_keys': ['release_note_compact_diff_summary_answer_disclosure_packet', 'auditor_compact_diff_summary_answer_disclosure_packet'],
                        'evidence_class_keys': ['bundle_identity_and_validator_companions', 'compact_diff_compare_and_replay_support'],
                        'request_fulfillment_certificate_keys': ['compact_diff_summary_request_fulfillment_certificate'],
                        'public_anchor_family_vocabulary_mode': 'imported_contract_vocabulary_contract_owned_basis',
                        'why': 'The compact diff family is the terse changed-fields anchor whose on-request meaning must stay synchronized with the maintained audit slice.'
                    }
                ],
                'covered_review_menu_keys': [
                    'release_note_public_status_sentence_answer_review_menu',
                    'referee_public_status_sentence_answer_review_menu',
                    'release_note_compact_diff_summary_answer_review_menu',
                    'auditor_compact_diff_summary_answer_review_menu'
                ],
                'covered_disclosure_packet_keys': [
                    'release_note_public_status_sentence_answer_disclosure_packet',
                    'referee_public_status_sentence_answer_disclosure_packet',
                    'release_note_compact_diff_summary_answer_disclosure_packet',
                    'auditor_compact_diff_summary_answer_disclosure_packet'
                ],
                'covered_evidence_class_keys': [
                    'bundle_identity_and_validator_companions',
                    'public_status_lineage_and_closure_support',
                    'compact_diff_compare_and_replay_support'
                ],
                'covered_request_fulfillment_certificate_keys': [
                    'public_status_sentence_request_fulfillment_certificate',
                    'compact_diff_summary_request_fulfillment_certificate'
                ],
                'validation_paths': ['support_manifest.json', 'example_artifact_inventory.json', 'example_validation_report.json', '../tools/validate_example.py'],
                'request_phrase': 'This paper is source-only; supporting artifacts are available on request.',
                'why': "One maintained paper-facing contract for the worked note's source-only public request sentence."
            }
        ],
        'note': "Derived paper-facing public request contract ledger for the worked note. It ties public anchor families to the exact maintained disclosure packets, review menus, and validator companions behind the note's source-only public request sentence."
    }


    request_fulfillment_certificates = {
        'request_fulfillment_certificates_id': REQUEST_FULFILLMENT_CERTIFICATES_ID,
        'claim_id': compare_report['claim_id'],
        'base_release_id': compare_report['base_release_id'],
        'release_id': compare_report['release_id'],
        'successor_release_id': compare_report['successor_release_id'],
        'compare_profile_id': compare_report['compare_profile_id'],
        'compare_report_id': compare_report['report_id'],
        'support_manifest_id': support_manifest['manifest_id'],
        'artifact_inventory_id': inventory['inventory_id'],
        'successor_challenge_answer_disclosure_packets_id': answer_disclosure_packets['challenge_answer_disclosure_packets_id'],
        'requestable_evidence_classes_id': requestable_evidence_classes['requestable_evidence_classes_id'],
        'successor_public_request_contracts_id': public_request_contracts['public_request_contracts_id'],
        'note_version': compare_report['note_version'],
        'contract': {
            'request_fulfillment_certificate_fields': ['request_fulfillment_certificate_key', 'public_request_contract_key', 'family_key', 'covered_disclosure_packet_keys', 'covered_evidence_class_keys', 'shared_evidence_class_keys', 'family_specific_evidence_class_keys', 'delivered_public_paths', 'delivered_support_paths', 'validation_paths', 'completion_verdict', 'completion_verdict_mode', 'why'],
            'family_completion_rule': 'Each certificate must bind one public request contract family to the exact disclosure packets and evidence classes whose union makes that family complete.',
            'validator_companion_rule': 'validation_paths must include support_manifest.json, example_artifact_inventory.json, example_validation_report.json, and ../tools/validate_example.py so an on-request reviewer can recheck the maintained bundle cut.',
            'shared_completion_verdict_vocabulary_rule': 'The same family completion verdict name may recur in later status envelopes, notices, routes, and spine mirrors only as imported family-scoped vocabulary; the truth of that verdict remains owned by the concrete fulfillment certificate that emits it.',
            'shared_class_discharge_rule': 'Any shared evidence class is discharged only as imported into the family-scoped certificate that names it; shared vocabulary therefore does not create a freestanding cross-family completion verdict.',
            'contract_satisfaction_rule': 'A source-only family promise is complete exactly when the delivered_public_paths and delivered_support_paths cover the public request contract family, its imported evidence classes, and the request packet plus validation companions of the covered disclosure packets.'
        },
        'request_fulfillment_certificates': [
            {
                'request_fulfillment_certificate_key': 'public_status_sentence_request_fulfillment_certificate',
                'public_request_contract_key': 'worked_example_receipt_interlock_public_request_contract',
                'family_key': 'public_status_sentence_family',
                'covered_disclosure_packet_keys': ['release_note_public_status_sentence_answer_disclosure_packet', 'referee_public_status_sentence_answer_disclosure_packet'],
                'covered_evidence_class_keys': ['bundle_identity_and_validator_companions', 'public_status_lineage_and_closure_support'],
                'shared_evidence_class_keys': ['bundle_identity_and_validator_companions'],
                'family_specific_evidence_class_keys': ['public_status_lineage_and_closure_support'],
                'delivered_public_paths': ['example_successor_lineage_notice.json', 'example_successor_claim_support_map.json'],
                'delivered_support_paths': [
                    'example_successor_challenge_answer_publication_profiles.json',
                    'example_successor_challenge_answer_citation_dockets.json',
                    'example_successor_challenge_answer_carrier_slots.json',
                    'example_successor_challenge_answer_audit_trails.json',
                    'example_successor_challenge_answer_cards.json',
                    'example_successor_challenge_answer_sheets.json',
                    'example_successor_challenge_answer_capsules.json',
                    'example_successor_challenge_branches.json',
                    'example_successor_challenge_terminal_witnesses.json',
                    'example_successor_challenge_surface_hooks.json',
                    'example_successor_lineage_notice.json',
                    'example_successor_claim_support_map.json',
                    'example_compare_report.json',
                    'example_successor_clause_pack.json',
                    'example_successor_sentence_locks.json',
                    'example_successor_continuity_verdict.json',
                    'example_release_closure_ledger.json',
                    'example_publication_closure_verdict.json',
                    'support_manifest.json',
                    'example_artifact_inventory.json',
                    'example_validation_report.json',
                    '../tools/validate_example.py'
                ],
                'validation_paths': ['support_manifest.json', 'example_artifact_inventory.json', 'example_validation_report.json', '../tools/validate_example.py'],
                'completion_verdict': 'complete',
                'completion_verdict_mode': 'shared_vocabulary_family_scoped_verdict',
                'why': 'The public-status family is complete when its public lineage/closure anchors, its family-local support slice, and the shared validator/bundle-identity class are all delivered together through this family-scoped certificate.'
            },
            {
                'request_fulfillment_certificate_key': 'compact_diff_summary_request_fulfillment_certificate',
                'public_request_contract_key': 'worked_example_receipt_interlock_public_request_contract',
                'family_key': 'compact_diff_summary_family',
                'covered_disclosure_packet_keys': ['release_note_compact_diff_summary_answer_disclosure_packet', 'auditor_compact_diff_summary_answer_disclosure_packet'],
                'covered_evidence_class_keys': ['bundle_identity_and_validator_companions', 'compact_diff_compare_and_replay_support'],
                'shared_evidence_class_keys': ['bundle_identity_and_validator_companions'],
                'family_specific_evidence_class_keys': ['compact_diff_compare_and_replay_support'],
                'delivered_public_paths': ['example_compare_report.json', 'example_successor_clause_pack.json'],
                'delivered_support_paths': [
                    'example_successor_challenge_answer_publication_profiles.json',
                    'example_successor_challenge_answer_citation_dockets.json',
                    'example_successor_challenge_answer_carrier_slots.json',
                    'example_successor_challenge_answer_audit_trails.json',
                    'example_successor_challenge_answer_cards.json',
                    'example_successor_challenge_answer_sheets.json',
                    'example_successor_challenge_answer_capsules.json',
                    'example_successor_challenge_branches.json',
                    'example_successor_challenge_terminal_witnesses.json',
                    'example_successor_challenge_surface_hooks.json',
                    'example_compare_report.json',
                    'example_successor_clause_pack.json',
                    'example_successor_sentence_locks.json',
                    'example_verifier_report.json',
                    'example_successor_continuity_verdict.json',
                    'support_manifest.json',
                    'example_artifact_inventory.json',
                    'example_validation_report.json',
                    '../tools/validate_example.py'
                ],
                'validation_paths': ['support_manifest.json', 'example_artifact_inventory.json', 'example_validation_report.json', '../tools/validate_example.py'],
                'completion_verdict': 'complete',
                'completion_verdict_mode': 'shared_vocabulary_family_scoped_verdict',
                'why': 'The compact-diff family is complete when its public compare anchors, its family-local compare/replay slice, and the shared validator/bundle-identity class are all delivered together through this family-scoped certificate.'
            }
        ],
        'note': "Derived family-scoped completion certificates for the worked note. They say when the note's source-only public request promise has been fully satisfied for each public anchor family, including the shared bundle-identity class as imported into that family rather than through a standalone cross-family verdict, and they record that repeated completion verdict names remain imported family-scoped vocabulary rather than new paper-level or wrapper ownership."
    }
    public_request_status_envelope = {
        'public_request_status_envelopes_id': PUBLIC_REQUEST_STATUS_ENVELOPES_ID,
        'claim_id': compare_report['claim_id'],
        'base_release_id': compare_report['base_release_id'],
        'release_id': compare_report['release_id'],
        'successor_release_id': compare_report['successor_release_id'],
        'compare_profile_id': compare_report['compare_profile_id'],
        'compare_report_id': compare_report['report_id'],
        'support_manifest_id': support_manifest['manifest_id'],
        'artifact_inventory_id': inventory['inventory_id'],
        'successor_public_request_contracts_id': public_request_contracts['public_request_contracts_id'],
        'request_fulfillment_certificates_id': request_fulfillment_certificates['request_fulfillment_certificates_id'],
        'note_version': compare_report['note_version'],
        'contract': {
            'public_request_status_envelope_fields': ['public_request_status_envelope_key', 'public_request_contract_key', 'covered_family_keys', 'covered_request_fulfillment_certificate_keys', 'family_completion_verdicts', 'public_request_status_token', 'public_request_status_token_mode', 'why'],
            'family_compression_rule': 'The paper-level public token is complete exactly when every covered family-scoped completion verdict is complete; it is open exactly when none are complete; otherwise it is partial.',
            'shared_status_token_vocabulary_rule': 'The same paper-level status token name may recur across many later notices, notice families, selectors, routes, and series-spine mirrors only as imported basis vocabulary; the truth of that token remains owned by the concrete status envelope that emits it.',
            'shared_family_completion_vocabulary_rule': 'Repeated family completion verdict names imported into later status envelopes, notices, routes, and series-spine mirrors remain family-scoped certificate vocabulary rather than new paper-level status ownership.',
            'non_reownership_rule': 'The status envelope may compress only families already owned by the imported public request contract and may not change packet paths, evidence-class names, or family completion verdicts.'
        },
        'public_request_status_envelopes': [
            {
                'public_request_status_envelope_key': 'worked_example_receipt_interlock_public_request_status_envelope',
                'public_request_contract_key': 'worked_example_receipt_interlock_public_request_contract',
                'covered_family_keys': ['public_status_sentence_family', 'compact_diff_summary_family'],
                'covered_request_fulfillment_certificate_keys': ['public_status_sentence_request_fulfillment_certificate', 'compact_diff_summary_request_fulfillment_certificate'],
                'family_completion_verdicts': [
                    {'family_key': 'public_status_sentence_family', 'completion_verdict': 'complete'},
                    {'family_key': 'compact_diff_summary_family', 'completion_verdict': 'complete'}
                ],
                'public_request_status_token': 'complete',
                'public_request_status_token_mode': 'shared_vocabulary_basis_scoped_status',
                "why": "Every family-scoped source-only request promise covered by the worked note's public request contract is complete in the maintained bundle, so the paper-level public token is complete."
            }
        ],
        "note": "Derived paper-level status envelope for the worked note's source-only request promise. It compresses family-scoped completion certificates to one public token without re-owning the narrower completion rules, and records that the token remains shared basis vocabulary rather than visible-wrapper ownership."
    }
    public_request_carryforward_envelope = {
        'public_request_carryforward_envelopes_id': PUBLIC_REQUEST_CARRYFORWARD_ENVELOPES_ID,
        'claim_id': compare_report['claim_id'],
        'base_release_id': compare_report['base_release_id'],
        'release_id': compare_report['release_id'],
        'successor_release_id': compare_report['successor_release_id'],
        'compare_profile_id': compare_report['compare_profile_id'],
        'compare_report_id': compare_report['report_id'],
        'support_manifest_id': support_manifest['manifest_id'],
        'artifact_inventory_id': inventory['inventory_id'],
        'successor_public_request_contracts_id': public_request_contracts['public_request_contracts_id'],
        'successor_public_request_status_envelopes_id': public_request_status_envelope['public_request_status_envelopes_id'],
        'publication_closure_verdict_id': publication_closure_verdict['closure_verdict_id'],
        'successor_continuity_verdict_id': successor_continuity_verdict['verdict_id'],
        'note_version': compare_report['note_version'],
        'contract': {
            'public_request_carryforward_envelope_fields': ['public_request_carryforward_envelope_key', 'predecessor_public_request_status_envelope_key', 'successor_public_request_contract_key', 'predecessor_public_request_status_token', 'successor_public_request_status_token', 'continuity_decision', 'publication_closure_status', 'changed_family_keys', 'reopened_family_keys', 'carryforward_token', 'carryforward_token_mode', 'why'],
            'family_stability_rule': 'The carryforward envelope may name only family keys already carried by the successor public request contract and may mark a family reopened only if the successor status is no longer preserved for that family.',
            'carryforward_rule': 'The carryforward token is preserved_complete exactly when predecessor and successor public tokens are both complete and no family reopens; it is preserved_noncomplete when the same non-complete status persists without reopening; it is advanced when the successor public token is strictly stronger; and it is reopened when a predecessor-complete promise becomes non-complete or any changed family is reopened.',
            'shared_carryforward_token_vocabulary_rule': 'The same carryforward token name may recur across many later notices, notice families, selectors, routes, and series-spine mirrors only as imported release-pair vocabulary; the truth of that token remains owned by the concrete carryforward envelope that emits it.'
        },
        'public_request_carryforward_envelopes': [
            {
                'public_request_carryforward_envelope_key': 'worked_example_receipt_interlock_public_request_carryforward_envelope',
                'predecessor_public_request_status_envelope_key': 'worked_example_receipt_interlock_public_request_status_envelope',
                'successor_public_request_contract_key': 'worked_example_receipt_interlock_public_request_contract',
                'predecessor_public_request_status_token': 'complete',
                'successor_public_request_status_token': 'complete',
                'continuity_decision': successor_continuity_verdict['continuity_decision'],
                'publication_closure_status': publication_closure_verdict['closure_status'],
                'changed_family_keys': [],
                'reopened_family_keys': [],
                'carryforward_token': 'preserved_complete',
                'carryforward_token_mode': 'shared_vocabulary_release_pair_scoped_verdict',
                "why": "The canned successor keeps the worked note's source-only public request promise complete, with no family reopened, so the paper-level public status token carries forward unchanged."
            }
        ],
        "note": "Derived successor-release carryforward envelope for the worked note's source-only request status. It states whether the paper-level public token survives, advances, or reopens across the concrete release transition, and records that the carryforward token remains shared release-pair vocabulary rather than visible-wrapper ownership."
    }
    public_request_notice = {
        'public_request_notices_id': PUBLIC_REQUEST_NOTICES_ID,
        'claim_id': compare_report['claim_id'],
        'base_release_id': compare_report['base_release_id'],
        'release_id': compare_report['release_id'],
        'successor_release_id': compare_report['successor_release_id'],
        'compare_profile_id': compare_report['compare_profile_id'],
        'compare_report_id': compare_report['report_id'],
        'successor_public_request_contracts_id': public_request_contracts['public_request_contracts_id'],
        'request_fulfillment_certificates_id': request_fulfillment_certificates['request_fulfillment_certificates_id'],
        'public_request_status_envelopes_id': public_request_status_envelope['public_request_status_envelopes_id'],
        'public_request_carryforward_envelopes_id': public_request_carryforward_envelope['public_request_carryforward_envelopes_id'],
        'note_version': compare_report['note_version'],
        'contract': {
            'public_request_notice_fields': ['public_request_notice_key', 'notice_kind', 'basis_artifact', 'basis_key', 'public_request_status_token', 'carryforward_token', 'notice_sentence', 'reader_pointer_order', 'why'],
            'basis_first_rule': 'The first reader pointer must be the imported status or carryforward owner whose visible sentence is being wrapped.',
            'no_new_semantics_rule': 'A public-request notice may compress only tokens and meanings already present in its imported basis object and the narrower owner artifacts named in its reader-pointer order.',
            'pointer_scope_rule': 'After the imported basis object, reader pointers may move only to already-owned source-only request artifacts that make the wrapped sentence auditable.'
        },
        'public_request_notices': [
            {
                'public_request_notice_key': 'worked_example_receipt_interlock_public_request_status_notice',
                'notice_kind': 'within_release',
                'basis_artifact': 'example_public_request_status_envelope.json',
                'basis_key': 'worked_example_receipt_interlock_public_request_status_envelope',
                'public_request_status_token': 'complete',
                'carryforward_token': None,
                'notice_sentence': 'For this source-only release, the worked note\'s paper-level public request promise is complete and supporting artifacts remain available on request.',
                'reader_pointer_order': [
                    {'path': 'example_public_request_status_envelope.json', 'why': 'the paper-level public token is the narrow owner of the within-release status claim'},
                    {'path': 'example_request_fulfillment_certificates.json', 'why': 'family-scoped completion certificates discharge the family-level proof behind that paper-level token'},
                    {'path': 'example_public_request_contracts.json', 'why': 'the paper-facing source-only contract fixes the exact maintained cut behind the visible sentence'}
                ],
                'why': 'The worked note needs one short within-release sentence that readers may cite without re-owning the underlying family completion semantics.'
            },
            {
                'public_request_notice_key': 'worked_example_receipt_interlock_public_request_carryforward_notice',
                'notice_kind': 'successor_carryforward',
                'basis_artifact': 'example_public_request_carryforward_envelope.json',
                'basis_key': 'worked_example_receipt_interlock_public_request_carryforward_envelope',
                'public_request_status_token': 'complete',
                'carryforward_token': 'preserved_complete',
                'notice_sentence': 'Across the canned successor release, that complete paper-level public request status carries forward unchanged.',
                'reader_pointer_order': [
                    {'path': 'example_public_request_carryforward_envelope.json', 'why': 'the carryforward envelope is the narrow owner of the cross-release verdict'},
                    {'path': 'example_public_request_status_envelope.json', 'why': 'the carryforward verdict imports the within-release paper-level status token it summarizes across releases'},
                    {'path': 'example_public_request_contracts.json', 'why': 'the successor contract fixes the promised family set whose stability is being summarized'},
                    {'path': 'example_request_fulfillment_certificates.json', 'why': 'family-scoped completion certificates remain the narrower proof if the carryforward sentence is challenged'}
                ],
                'why': 'The worked note needs one short successor-facing sentence that readers may cite when the public request promise survives the canned successor cut unchanged.'
            }
        ],
        'note': 'Derived outward-facing source-only public-request notices for the worked note. They wrap the within-release public status token and the successor carryforward verdict into exact short sentences plus first-pointer order.'
    }
    public_request_notice_normal_forms = {
        'public_request_notice_normal_forms_id': PUBLIC_REQUEST_NOTICE_NORMAL_FORMS_ID,
        'claim_id': compare_report['claim_id'],
        'base_release_id': compare_report['base_release_id'],
        'release_id': compare_report['release_id'],
        'successor_release_id': compare_report['successor_release_id'],
        'compare_profile_id': compare_report['compare_profile_id'],
        'compare_report_id': compare_report['report_id'],
        'successor_public_request_notices_id': public_request_notice['public_request_notices_id'],
        'public_request_status_envelopes_id': public_request_status_envelope['public_request_status_envelopes_id'],
        'public_request_carryforward_envelopes_id': public_request_carryforward_envelope['public_request_carryforward_envelopes_id'],
        'note_version': compare_report['note_version'],
        'contract': {
            'public_request_notice_normal_form_fields': ['public_request_notice_normal_form_key', 'notice_kind', 'emitted_notice_key', 'basis_key', 'allowed_public_request_status_tokens', 'allowed_carryforward_tokens', 'template', 'slot_bindings', 'rendered_sentence', 'why'],
            'basis_compatibility_rule': 'A public-request notice normal form may realize only a notice kind and token pair that already appear in the imported status or carryforward basis object.',
            'slot_realization_rule': 'Every non-literal semantic phrase in the rendered sentence must come from an explicit slot whose source field is named in slot_bindings, and the rendered sentence must equal the emitted notice sentence exactly.',
            'emitted_notice_inheritance_rule': 'A notice normal form may factor one emitted notice into a canonical template-and-slot family, but it may not replace the emitted notice key or its reader-pointer order.'
        },
        'public_request_notice_normal_forms': [
            {
                'public_request_notice_normal_form_key': 'worked_example_receipt_interlock_within_release_complete_public_request_notice_normal_form',
                'notice_kind': 'within_release',
                'emitted_notice_key': 'worked_example_receipt_interlock_public_request_status_notice',
                'basis_key': 'worked_example_receipt_interlock_public_request_status_envelope',
                'allowed_public_request_status_tokens': ['complete'],
                'allowed_carryforward_tokens': [],
                'template': [
                    {"literal": "For this source-only release, the worked note's paper-level public request promise is "},
                    {'slot': 'public_request_status_token'},
                    {'literal': ' and supporting artifacts remain available on request.'}
                ],
                'slot_bindings': [
                    {'slot': 'public_request_status_token', 'source_artifact': 'example_public_request_status_envelope.json', 'source_field': 'public_request_status_token'}
                ],
                "rendered_sentence": "For this source-only release, the worked note's paper-level public request promise is complete and supporting artifacts remain available on request.",
                "why": "One canonical within-release sentence family for the worked note's visible complete-status source-only notice."
            },
            {
                'public_request_notice_normal_form_key': 'worked_example_receipt_interlock_successor_preserved_complete_public_request_notice_normal_form',
                'notice_kind': 'successor_carryforward',
                'emitted_notice_key': 'worked_example_receipt_interlock_public_request_carryforward_notice',
                'basis_key': 'worked_example_receipt_interlock_public_request_carryforward_envelope',
                'allowed_public_request_status_tokens': ['complete'],
                'allowed_carryforward_tokens': ['preserved_complete'],
                'template': [
                    {'literal': 'Across the canned successor release, that '},
                    {'slot': 'public_request_status_token'},
                    {'literal': ' paper-level public request status carries forward '},
                    {'slot': 'carryforward_phrase'},
                    {'literal': '.'}
                ],
                'slot_bindings': [
                    {'slot': 'public_request_status_token', 'source_artifact': 'example_public_request_carryforward_envelope.json', 'source_field': 'successor_public_request_status_token'},
                    {'slot': 'carryforward_phrase', 'source_artifact': 'example_public_request_carryforward_envelope.json', 'source_field': 'carryforward_token', 'render_map': {'preserved_complete': 'unchanged'}}
                ],
                'rendered_sentence': 'Across the canned successor release, that complete paper-level public request status carries forward unchanged.',
                "why": "One canonical successor-facing sentence family for the worked note's visible preserved-complete source-only carryforward notice."
            }
        ],
        "note": "Derived canonical sentence families for the worked note's source-only public-request notices. They factor the emitted within-release and successor-facing notice sentences into explicit template-and-slot forms without re-owning the notice instances."
    }

    public_request_notice_selections = {
        'public_request_notice_selections_id': PUBLIC_REQUEST_NOTICE_SELECTIONS_ID,
        'claim_id': compare_report['claim_id'],
        'base_release_id': compare_report['base_release_id'],
        'release_id': compare_report['release_id'],
        'successor_release_id': compare_report['successor_release_id'],
        'compare_profile_id': compare_report['compare_profile_id'],
        'compare_report_id': compare_report['report_id'],
        'successor_public_request_notices_id': public_request_notice['public_request_notices_id'],
        'successor_public_request_notice_normal_forms_id': public_request_notice_normal_forms['public_request_notice_normal_forms_id'],
        'public_request_status_envelopes_id': public_request_status_envelope['public_request_status_envelopes_id'],
        'public_request_carryforward_envelopes_id': public_request_carryforward_envelope['public_request_carryforward_envelopes_id'],
        'note_version': compare_report['note_version'],
        'contract': {
            'public_request_notice_selection_fields': ['public_request_notice_selection_key', 'notice_kind', 'basis_key', 'selector_inputs', 'selected_public_request_notice_normal_form_key', 'selected_emitted_notice_key', 'selection_decision', 'rendered_sentence', 'why'],
            'selector_totality_rule': 'For every imported emitted public-request notice, the selector must map its basis-token combination to exactly one maintained canonical notice normal form.',
            'normal_form_choice_rule': 'A selection may choose only a canonical notice normal form whose allowed token set matches the imported basis object and whose rendered sentence agrees with the emitted notice sentence.',
            'no_sentence_reownership_rule': 'The selector may choose among already-owned notice normal forms and emitted notices, but it may not rewrite the rendered sentence or pointer order they already own.'
        },
        'public_request_notice_selections': [
            {
                'public_request_notice_selection_key': 'worked_example_receipt_interlock_within_release_public_request_notice_selection',
                'notice_kind': 'within_release',
                'basis_key': 'worked_example_receipt_interlock_public_request_status_envelope',
                'selector_inputs': {'public_request_status_token': 'complete', 'carryforward_token': None},
                'selected_public_request_notice_normal_form_key': 'worked_example_receipt_interlock_within_release_complete_public_request_notice_normal_form',
                'selected_emitted_notice_key': 'worked_example_receipt_interlock_public_request_status_notice',
                'selection_decision': 'select_within_release_complete_notice_normal_form',
                'rendered_sentence': "For this source-only release, the worked note's paper-level public request promise is complete and supporting artifacts remain available on request.",
                'why': 'The within-release basis token is complete, so the selector chooses the complete-status canonical source-only notice family rather than a different within-release wrapper.'
            },
            {
                'public_request_notice_selection_key': 'worked_example_receipt_interlock_successor_public_request_notice_selection',
                'notice_kind': 'successor_carryforward',
                'basis_key': 'worked_example_receipt_interlock_public_request_carryforward_envelope',
                'selector_inputs': {'public_request_status_token': 'complete', 'carryforward_token': 'preserved_complete'},
                'selected_public_request_notice_normal_form_key': 'worked_example_receipt_interlock_successor_preserved_complete_public_request_notice_normal_form',
                'selected_emitted_notice_key': 'worked_example_receipt_interlock_public_request_carryforward_notice',
                'selection_decision': 'select_successor_preserved_complete_notice_normal_form',
                'rendered_sentence': 'Across the canned successor release, that complete paper-level public request status carries forward unchanged.',
                'why': 'The successor-facing basis tokens are complete plus preserved-complete, so the selector chooses the preserved-complete carryforward notice family rather than a reopen or advance wrapper.'
            }
        ],
        "note": "Derived selector ledger for the worked note's source-only public-request notices. It chooses which maintained canonical notice normal form applies to each emitted within-release or successor-facing notice given the imported status/carryforward basis tokens."
    }




    public_request_response_menus = {
        'public_request_response_menus_id': PUBLIC_REQUEST_RESPONSE_MENUS_ID,
        'claim_id': compare_report['claim_id'],
        'base_release_id': compare_report['base_release_id'],
        'release_id': compare_report['release_id'],
        'successor_release_id': compare_report['successor_release_id'],
        'compare_profile_id': compare_report['compare_profile_id'],
        'compare_report_id': compare_report['report_id'],
        'successor_public_request_contracts_id': public_request_contracts['public_request_contracts_id'],
        'successor_request_fulfillment_certificates_id': request_fulfillment_certificates['request_fulfillment_certificates_id'],
        'public_request_status_envelopes_id': public_request_status_envelope['public_request_status_envelopes_id'],
        'public_request_carryforward_envelopes_id': public_request_carryforward_envelope['public_request_carryforward_envelopes_id'],
        'successor_public_request_notices_id': public_request_notice['public_request_notices_id'],
        'successor_public_request_notice_normal_forms_id': public_request_notice_normal_forms['public_request_notice_normal_forms_id'],
        'successor_public_request_notice_selections_id': public_request_notice_selections['public_request_notice_selections_id'],
        'note_version': compare_report['note_version'],
        'contract': {
            'public_request_response_menu_fields': ['public_request_response_menu_key', 'notice_kind', 'followup_class_vocabulary_mode', 'basis_key', 'basis_cite_path', 'public_request_notice_key', 'selected_public_request_notice_normal_form_key', 'public_request_notice_selection_key', 'public_request_contract_key', 'covered_request_fulfillment_certificate_keys', 'response_entries', 'why'],
            'request_class_rule': 'response_entries must cover exactly the common paper-facing follow-up classes basis_token_check, visible_sentence_check, canonical_family_check, family_choice_check, request_scope_check, and completion_rule_check for the same emitted notice.',
            'shared_followup_vocabulary_rule': 'Those six class labels are shared request-handling vocabulary across emitted notices, but the selected owner for each label remains notice-scoped to the concrete menu entry that imports it.',
            'smallest_sufficient_rule': 'Basis-token checks use the imported status or carryforward envelope, visible-sentence checks use the emitted notice, canonical-family checks use the notice normal form, family-choice checks use the notice selection, request-scope checks use the public request contract, and completion-rule checks use the request-fulfillment-certificate ledger.',
            'import_rule': 'Each response entry must copy the imported token bundle, rendered sentence, canonical family, family choice, contract cut, or completion entries exactly; the menu may not create new source-only semantics while pretending only to select a handoff object.',
            'non_semantic_rule': 'Response menus own only follow-up-class response selection for one already-maintained source-only notice.'
        },
        'public_request_response_menus': [],
        'note': "Derived notice-keyed response-menu ledger for the worked note's source-only public-request follow-up classes. Each menu says which already-owned object is the smallest sufficient handoff for one concrete question about a visible source-only notice."
    }

    contract_entry = public_request_contracts['public_request_contracts'][0]
    cert_entries_by_key = {entry['request_fulfillment_certificate_key']: entry for entry in request_fulfillment_certificates['request_fulfillment_certificates']}
    notice_entries_by_key = {entry['public_request_notice_key']: entry for entry in public_request_notice['public_request_notices']}
    notice_nf_by_key = {entry['public_request_notice_normal_form_key']: entry for entry in public_request_notice_normal_forms['public_request_notice_normal_forms']}
    notice_sel_by_key = {entry['public_request_notice_selection_key']: entry for entry in public_request_notice_selections['public_request_notice_selections']}
    status_entry = public_request_status_envelope['public_request_status_envelopes'][0]
    carry_entry = public_request_carryforward_envelope['public_request_carryforward_envelopes'][0]
    response_specs = [
        {
            'menu_key': 'worked_example_receipt_interlock_within_release_public_request_response_menu',
            'notice_kind': 'within_release',
            'basis_key': status_entry['public_request_status_envelope_key'],
            'basis_object_kind': 'public_request_status_envelope',
            'basis_cite_path': 'example_public_request_status_envelope.json',
            'basis_entry': status_entry,
            'notice_key': 'worked_example_receipt_interlock_public_request_status_notice',
            'normal_form_key': 'worked_example_receipt_interlock_within_release_complete_public_request_notice_normal_form',
            'selection_key': 'worked_example_receipt_interlock_within_release_public_request_notice_selection',
            'why': 'The within-release response menu answers follow-up about the emitted complete-status source-only notice without collapsing token, sentence, family, family-choice, contract, and completion ownership into one object.'
        },
        {
            'menu_key': 'worked_example_receipt_interlock_successor_public_request_response_menu',
            'notice_kind': 'successor_carryforward',
            'basis_key': carry_entry['public_request_carryforward_envelope_key'],
            'basis_object_kind': 'public_request_carryforward_envelope',
            'basis_cite_path': 'example_public_request_carryforward_envelope.json',
            'basis_entry': carry_entry,
            'notice_key': 'worked_example_receipt_interlock_public_request_carryforward_notice',
            'normal_form_key': 'worked_example_receipt_interlock_successor_preserved_complete_public_request_notice_normal_form',
            'selection_key': 'worked_example_receipt_interlock_successor_public_request_notice_selection',
            'why': 'The successor-facing response menu answers follow-up about the preserved-complete carryforward notice while keeping the carryforward basis separate from wording, family choice, contract scope, and completion criteria.'
        }
    ]
    for spec in response_specs:
        notice_entry = notice_entries_by_key[spec['notice_key']]
        nf_entry = notice_nf_by_key[spec['normal_form_key']]
        sel_entry = notice_sel_by_key[spec['selection_key']]
        cert_keys = contract_entry['covered_request_fulfillment_certificate_keys']
        public_request_response_menus['public_request_response_menus'].append({
            'public_request_response_menu_key': spec['menu_key'],
            'notice_kind': spec['notice_kind'],
            'followup_class_vocabulary_mode': 'shared_vocabulary_notice_scoped_selection',
            'basis_key': spec['basis_key'],
            'basis_cite_path': spec['basis_cite_path'],
            'public_request_notice_key': spec['notice_key'],
            'selected_public_request_notice_normal_form_key': spec['normal_form_key'],
            'public_request_notice_selection_key': spec['selection_key'],
            'public_request_contract_key': contract_entry['public_request_contract_key'],
            'covered_request_fulfillment_certificate_keys': cert_keys,
            'response_entries': [
                {
                    'request_class': 'basis_token_check',
                    'object_kind': spec['basis_object_kind'],
                    'object_key': spec['basis_key'],
                    'cite_path': spec['basis_cite_path'],
                    'selected_entry': spec['basis_entry'],
                    'when': 'Need the narrow paper-level token or successor carryforward verdict that makes the visible source-only notice true.',
                    'why': 'The basis owner is the smallest maintained object that says which token combination is actually true.'
                },
                {
                    'request_class': 'visible_sentence_check',
                    'object_kind': 'public_request_notice',
                    'object_key': spec['notice_key'],
                    'cite_path': 'example_public_request_notice.json',
                    'selected_entry': {'notice_sentence': notice_entry['notice_sentence'], 'reader_pointer_order': notice_entry['reader_pointer_order']},
                    'when': 'Need the exact outward-facing short sentence and first-pointer order that readers actually saw.',
                    'why': 'The emitted notice is the smallest maintained object that owns the visible wrapper sentence.'
                },
                {
                    'request_class': 'canonical_family_check',
                    'object_kind': 'public_request_notice_normal_form',
                    'object_key': spec['normal_form_key'],
                    'cite_path': 'example_public_request_notice_normal_forms.json',
                    'selected_entry': {'template': nf_entry['template'], 'slot_bindings': nf_entry['slot_bindings'], 'rendered_sentence': nf_entry['rendered_sentence']},
                    'when': 'Need the reusable canonical sentence family and explicit slot bindings behind the visible notice.',
                    'why': 'The normal-form owner is the smallest maintained object that fixes the reusable sentence family rather than just the wrapper instance.'
                },
                {
                    'request_class': 'family_choice_check',
                    'object_kind': 'public_request_notice_selection',
                    'object_key': spec['selection_key'],
                    'cite_path': 'example_public_request_notice_selections.json',
                    'selected_entry': {'selector_inputs': sel_entry['selector_inputs'], 'selected_public_request_notice_normal_form_key': sel_entry['selected_public_request_notice_normal_form_key'], 'selected_emitted_notice_key': sel_entry['selected_emitted_notice_key'], 'rendered_sentence': sel_entry['rendered_sentence']},
                    'when': 'Need to know why this canonical notice family was chosen for the shipped token combination rather than another family.',
                    'why': 'The selector is the smallest maintained object that owns token-to-family choice.'
                },
                {
                    'request_class': 'request_scope_check',
                    'object_kind': 'public_request_contract',
                    'object_key': contract_entry['public_request_contract_key'],
                    'cite_path': 'example_public_request_contracts.json',
                    'selected_entry': {'request_phrase': contract_entry['request_phrase'], 'public_anchor_families': contract_entry['public_anchor_families'], 'validation_paths': contract_entry['validation_paths']},
                    'when': 'Need the exact maintained packet/menu/validator cut that sits behind the public available-on-request sentence.',
                    'why': 'The public request contract is the smallest maintained object that owns paper-level request scope.'
                },
                {
                    'request_class': 'completion_rule_check',
                    'object_kind': 'request_fulfillment_certificates',
                    'object_key': request_fulfillment_certificates['request_fulfillment_certificates_id'],
                    'cite_path': 'example_request_fulfillment_certificates.json',
                    'selected_entry': [cert_entries_by_key[key] for key in cert_keys],
                    'when': 'Need the exact family-scoped completion entries that discharge the promised source-only cut.',
                    'why': 'The request-fulfillment-certificate ledger is the smallest maintained object that owns completion of the promised families.'
                }
            ],
            'why': spec['why']
        })


    def make_response_packet(menu_entry, menu_key, notice_key, notice_kind, basis_cite_path, basis_key):
        request_class = menu_entry['request_class']
        packet_paths = [menu_entry['cite_path']]
        required_public_paths = []
        required_validation_paths = []
        selected = menu_entry['selected_entry']
        if request_class == 'basis_token_check':
            packet_paths.append(basis_cite_path)
            if notice_kind == 'within_release':
                packet_paths.append('example_request_fulfillment_certificates.json')
            else:
                packet_paths.extend(['example_public_request_status_envelope.json', 'example_request_fulfillment_certificates.json'])
        elif request_class == 'visible_sentence_check':
            packet_paths.append(basis_cite_path)
        elif request_class == 'canonical_family_check':
            packet_paths.extend([basis_cite_path, 'example_public_request_notice.json'])
        elif request_class == 'family_choice_check':
            packet_paths.extend([basis_cite_path, 'example_public_request_notice_normal_forms.json', 'example_public_request_notice.json'])
        elif request_class == 'request_scope_check':
            required_validation_paths = list(selected.get('validation_paths', []))
            packet_paths.extend(required_validation_paths)
        elif request_class == 'completion_rule_check':
            cert_entries = selected if isinstance(selected, list) else [selected]
            for cert in cert_entries:
                required_public_paths.extend(cert.get('delivered_public_paths', []))
                required_validation_paths.extend(cert.get('validation_paths', []))
            packet_paths.extend(required_public_paths)
            packet_paths.extend(required_validation_paths)
        packet_paths = sorted(dict.fromkeys(packet_paths))
        required_public_paths = sorted(dict.fromkeys(required_public_paths))
        required_validation_paths = sorted(dict.fromkeys(required_validation_paths))
        return {
            'public_request_response_packet_key': f"{menu_key}__{request_class}",
            'public_request_notice_key': notice_key,
            'notice_kind': notice_kind,
            'packet_scope_mode': 'notice_and_followup_scoped_packet',
            'basis_cite_path': basis_cite_path,
            'basis_key': basis_key,
            'public_request_response_menu_key': menu_key,
            'request_class': request_class,
            'selected_object_kind': menu_entry['object_kind'],
            'selected_object_key': menu_entry['object_key'],
            'selected_object_path': menu_entry['cite_path'],
            'selected_entry_excerpt': selected,
            'required_public_paths': required_public_paths,
            'required_validation_paths': required_validation_paths,
            'packet_paths': packet_paths,
            'when': menu_entry['when'],
            'why': {
                'basis_token_check': 'The basis-token packet includes the exact basis owner plus the narrower completion support needed to justify the paper-level token without widening to unrelated source-only owners.',
                'visible_sentence_check': 'The visible-sentence packet includes the emitted notice together with its imported basis owner so the exact sentence and its narrow truth carrier travel together.',
                'canonical_family_check': 'The canonical-family packet includes the normal-form owner together with the emitted notice and basis owner so family identity stays separate from visible wording and token truth.',
                'family_choice_check': 'The family-choice packet includes the selector together with the canonical family and basis owner so the choice of family is auditable without re-reading the whole source-only tail.',
                'request_scope_check': 'The request-scope packet includes the paper-facing contract and its shared validation companions so the exact maintained cut behind the public sentence is bounded and checkable.',
                'completion_rule_check': 'The completion-rule packet includes the family completion entries together with the public anchor paths and shared validator companions those entries say must travel together.'
            }[request_class]
        }

    public_request_response_packets = {
        'public_request_response_packets_id': PUBLIC_REQUEST_RESPONSE_PACKETS_ID,
        'claim_id': compare_report['claim_id'],
        'base_release_id': compare_report['base_release_id'],
        'release_id': compare_report['release_id'],
        'successor_release_id': compare_report['successor_release_id'],
        'compare_profile_id': compare_report['compare_profile_id'],
        'compare_report_id': compare_report['report_id'],
        'successor_public_request_response_menus_id': public_request_response_menus['public_request_response_menus_id'],
        'successor_public_request_contracts_id': public_request_contracts['public_request_contracts_id'],
        'successor_request_fulfillment_certificates_id': request_fulfillment_certificates['request_fulfillment_certificates_id'],
        'successor_public_request_status_envelopes_id': public_request_status_envelope['public_request_status_envelopes_id'],
        'successor_public_request_carryforward_envelopes_id': public_request_carryforward_envelope['public_request_carryforward_envelopes_id'],
        'successor_public_request_notices_id': public_request_notice['public_request_notices_id'],
        'successor_public_request_notice_normal_forms_id': public_request_notice_normal_forms['public_request_notice_normal_forms_id'],
        'successor_public_request_notice_selections_id': public_request_notice_selections['public_request_notice_selections_id'],
        'note_version': compare_report['note_version'],
        'contract': {
            'public_request_response_packet_fields': ['public_request_response_packet_key', 'public_request_notice_key', 'notice_kind', 'packet_scope_mode', 'basis_cite_path', 'basis_key', 'public_request_response_menu_key', 'request_class', 'selected_object_kind', 'selected_object_key', 'selected_object_path', 'selected_entry_excerpt', 'required_public_paths', 'required_validation_paths', 'packet_paths', 'when', 'why'],
            'owner_packet_rule': 'Every response packet must import exactly one response-menu choice and freeze one bounded entry excerpt from that selected owner.',
            'followup_vocabulary_import_rule': 'Repeated follow-up-class labels in response packets are shared imported vocabulary from the response menus; exact packet identity remains attached to the concrete notice/follow-up pair.',
            'packet_scoping_rule': 'Each response packet stays attached to one concrete notice/follow-up pair even when many notices reuse the same follow-up-class label.',
            'bounded_companion_rule': 'Additional packet paths may be added only when they are the imported basis path, the public anchor paths explicitly required by the selected completion entries, or the shared validation companions already named by the selected contract/certificate owner.',
            'minimality_rule': 'A response packet may not widen to unrelated source-only families or owners once the response-menu choice for that follow-up class has been fixed.'
        },
        'public_request_response_packets': [],
        'note': 'Derived notice-and-follow-up keyed response-packet ledger for the worked note. Each packet freezes the exact bounded handoff slice that should travel once one source-only response-menu entry has been chosen.'
    }
    for menu in public_request_response_menus['public_request_response_menus']:
        for entry in menu['response_entries']:
            public_request_response_packets['public_request_response_packets'].append(make_response_packet(
                entry,
                menu['public_request_response_menu_key'],
                menu['public_request_notice_key'],
                menu['notice_kind'],
                menu['basis_cite_path'],
                menu['basis_key']
            ))


    def packet_maintenance_posture(token):
        return {
            'current_status': token,
            'reissue_status': {
                'preserved': 'reuse_same_packet',
                'refresh_in_place': 'refresh_then_reissue',
                'reopened': 'reroute_from_narrower_owners',
            }[token],
            'why': {
                'preserved': 'The exact bounded packet may travel again without packet-local edits because the selected owner, companion paths, and release-bound fields all remain current.',
                'refresh_in_place': 'The same bounded packet still governs, but release-bound basis companions, copied excerpts, or digest bindings must be refreshed before reissue.',
                'reopened': 'The predecessor packet no longer remains the smallest sufficient bounded handoff, so maintainers must return to narrower owners instead of reusing it.'
            }[token]
        }


    public_request_response_packet_carryforward_profiles = {
        'public_request_response_packet_carryforward_profiles_id': PUBLIC_REQUEST_RESPONSE_PACKET_CARRYFORWARD_PROFILES_ID,
        'claim_id': compare_report['claim_id'],
        'base_release_id': compare_report['base_release_id'],
        'release_id': compare_report['release_id'],
        'successor_release_id': compare_report['successor_release_id'],
        'compare_profile_id': compare_report['compare_profile_id'],
        'compare_report_id': compare_report['report_id'],
        'successor_public_request_response_packets_id': public_request_response_packets['public_request_response_packets_id'],
        'successor_public_request_carryforward_envelopes_id': public_request_carryforward_envelope['public_request_carryforward_envelopes_id'],
        'successor_public_request_response_menus_id': public_request_response_menus['public_request_response_menus_id'],
        'note_version': compare_report['note_version'],
        'contract': {
            'public_request_response_packet_carryforward_profile_fields': ['public_request_response_packet_carryforward_profile_key', 'predecessor_public_request_response_packet_key', 'public_request_notice_key', 'notice_kind', 'request_class', 'predecessor_selected_object_kind', 'predecessor_selected_object_key', 'predecessor_packet_paths', 'successor_public_request_carryforward_envelope_key', 'continuity_decision', 'response_packet_carryforward_token', 'packet_maintenance_posture', 'refreshable_field_families', 'refreshable_field_family_mode', 'changed_context_classes', 'why'],
            'preservation_rule': 'preserved may be emitted only when the selected owner, bounded companion set, and packet meaning remain unchanged and no release-bound field requires refresh under the successor context.',
            'refresh_in_place_rule': 'refresh_in_place may be emitted only when the selected owner and bounded slice remain sufficient but release-bound basis companions, packet excerpts, or digest bindings must be refreshed without rerouting the handoff.',
            'shared_vocabulary_rule': 'Repeated refreshable-field-family labels may recur across many packet carryforward profiles only as imported packet-maintenance vocabulary; the reuse verdict itself remains attached to the concrete predecessor packet named by the profile.',
            'reopen_rule': 'reopened must be emitted whenever the successor context changes the selected owner, the required companion set, or family completion enough that the predecessor packet is no longer the smallest sufficient bounded handoff.',
            'packet_maintenance_posture_fields': ['current_status', 'reissue_status', 'why'],
            'packet_maintenance_posture_rule': 'The packet carryforward owner must record the current packet reuse posture once, and later delta / refresh-notice / successor-packet / route owners must mirror that posture exactly rather than reconstructing it ad hoc from the carryforward token.'
        },
        'public_request_response_packet_carryforward_profiles': [],
        'note': "Derived successor-release carryforward profiles for the worked note's exact source-only response packets. Each profile classifies whether one already-cut packet may be reused unchanged, refreshed in place, or must reopen under the canned successor release."
    }
    carry_entry = public_request_carryforward_envelope['public_request_carryforward_envelopes'][0]
    for packet in public_request_response_packets['public_request_response_packets']:
        public_request_response_packet_carryforward_profiles['public_request_response_packet_carryforward_profiles'].append({
            'public_request_response_packet_carryforward_profile_key': f"{packet['public_request_response_packet_key']}__carryforward",
            'predecessor_public_request_response_packet_key': packet['public_request_response_packet_key'],
            'public_request_notice_key': packet['public_request_notice_key'],
            'notice_kind': packet['notice_kind'],
            'request_class': packet['request_class'],
            'predecessor_selected_object_kind': packet['selected_object_kind'],
            'predecessor_selected_object_key': packet['selected_object_key'],
            'predecessor_packet_paths': packet['packet_paths'],
            'successor_public_request_carryforward_envelope_key': carry_entry['public_request_carryforward_envelope_key'],
            'continuity_decision': carry_entry['continuity_decision'],
            'response_packet_carryforward_token': 'refresh_in_place',
            'packet_maintenance_posture': packet_maintenance_posture('refresh_in_place'),
            'refreshable_field_families': ['basis_companions', 'selected_entry_excerpt', 'digest_bindings'],
            'refreshable_field_family_mode': 'shared_vocabulary_packet_scoped_verdict',
            'changed_context_classes': ['successor_release_binding', 'successor_digest_binding'],
            'why': 'The canned successor preserves the same source-only follow-up owner choice and bounded handoff slice, but the packet remains release-bound and therefore must refresh successor-facing basis companions and digest bindings before reuse.'
        })

    packet_by_key = {entry['public_request_response_packet_key']: entry for entry in public_request_response_packets['public_request_response_packets']}
    public_request_response_packet_delta_ledgers = {
        'public_request_response_packet_delta_ledgers_id': PUBLIC_REQUEST_RESPONSE_PACKET_DELTA_LEDGERS_ID,
        'claim_id': compare_report['claim_id'],
        'base_release_id': compare_report['base_release_id'],
        'release_id': compare_report['release_id'],
        'successor_release_id': compare_report['successor_release_id'],
        'compare_profile_id': compare_report['compare_profile_id'],
        'compare_report_id': compare_report['report_id'],
        'successor_public_request_response_packets_id': public_request_response_packets['public_request_response_packets_id'],
        'successor_public_request_response_packet_carryforward_profiles_id': public_request_response_packet_carryforward_profiles['public_request_response_packet_carryforward_profiles_id'],
        'successor_public_request_carryforward_envelopes_id': public_request_carryforward_envelope['public_request_carryforward_envelopes_id'],
        'note_version': compare_report['note_version'],
        'contract': {
            'public_request_response_packet_delta_fields': ['public_request_response_packet_delta_key', 'public_request_response_packet_carryforward_profile_key', 'predecessor_public_request_response_packet_key', 'public_request_notice_key', 'notice_kind', 'request_class', 'packet_reuse_status', 'delta_token', 'reused_packet_paths', 'changed_field_family_mode', 'refresh_instructions', 'successor_context_key', 'successor_context_path', 'unchanged_owner_families', 'why'],
            'refresh_instruction_fields': ['field_family', 'owner_path', 'owner_key', 'refresh_mode', 'refreshed_fields', 'why'],
            'packet_locality_rule': 'A response-packet delta ledger may name only packet paths already present in the imported predecessor packet and only field families already declared refreshable by the imported packet-carryforward profile.',
            'refresh_detail_rule': 'refresh_fields may be emitted only when the imported packet-carryforward profile emits refresh_in_place, and each listed refresh instruction must name the exact packet-local owner path, owner key, and release-bound field family being refreshed.',
            'shared_vocabulary_rule': 'Repeated changed-field-family labels may recur across many delta ledgers only as packet-local maintenance vocabulary already declared by the carryforward profile; the exact refresh instruction rows remain attached to the concrete owner path/key pairs listed in the ledger.',
            'reopen_fallback_rule': 'reopen may be emitted only when the imported packet-carryforward profile emits reopened; reopened packets list no refresh instructions and instead force a return to the narrower owners.',
            "mirrored_packet_reuse_rule": "packet_reuse_status must mirror the imported packet-carryforward profile's current packet maintenance posture exactly so later owners can cite one explicit reuse tag rather than re-reading the profile token."
        },
        'public_request_response_packet_delta_ledgers': [],
        'note': "Derived successor-facing delta ledger for the worked note's exact source-only response packets. Each entry records the exact packet-local refresh instructions that apply when a reusable predecessor packet is reissued under the canned successor release."
    }
    for profile in public_request_response_packet_carryforward_profiles['public_request_response_packet_carryforward_profiles']:
        packet = packet_by_key[profile['predecessor_public_request_response_packet_key']]
        token = profile['response_packet_carryforward_token']
        delta_token = {'preserved': 'no_change', 'refresh_in_place': 'refresh_fields', 'reopened': 'reopen'}[token]
        refresh_instructions = []
        if delta_token == 'refresh_fields':
            refresh_instructions = [
                {
                    'field_family': 'basis_companions',
                    'owner_path': packet['basis_cite_path'],
                    'owner_key': packet['basis_key'],
                    'refresh_mode': 'rebind_release_context',
                    'refreshed_fields': ['release_id', 'successor_release_id'],
                    'why': 'The packet keeps the same basis owner path and key, but its release-bound context fields must be refreshed when the successor release becomes the current maintenance cut.'
                },
                {
                    'field_family': 'selected_entry_excerpt',
                    'owner_path': packet['selected_object_path'],
                    'owner_key': packet['selected_object_key'],
                    'refresh_mode': 'refresh_release_bound_excerpt_fields',
                    'refreshed_fields': ['release_id', 'successor_release_id', 'compare_report_id'],
                    'why': 'The exact selected owner stays fixed, but any release-bound excerpt fields copied into the packet must be refreshed in place under successor maintenance.'
                },
                {
                    'field_family': 'digest_bindings',
                    'owner_path': 'support_manifest.json',
                    'owner_key': support_manifest['manifest_id'],
                    'refresh_mode': 'refresh_digest_bindings',
                    'refreshed_fields': ['sha256'],
                    'why': 'Reissuing the packet under successor maintenance refreshes the digest bindings that tie the bounded handoff slice back to the current maintained support bundle.'
                }
            ]
        public_request_response_packet_delta_ledgers['public_request_response_packet_delta_ledgers'].append({
            'public_request_response_packet_delta_key': f"{packet['public_request_response_packet_key']}__delta",
            'public_request_response_packet_carryforward_profile_key': profile['public_request_response_packet_carryforward_profile_key'],
            'predecessor_public_request_response_packet_key': packet['public_request_response_packet_key'],
            'public_request_notice_key': packet['public_request_notice_key'],
            'notice_kind': packet['notice_kind'],
            'request_class': packet['request_class'],
            'packet_reuse_status': profile['packet_maintenance_posture']['current_status'],
            'delta_token': delta_token,
            'reused_packet_paths': packet['packet_paths'],
            'changed_field_family_mode': 'shared_vocabulary_packet_scoped_instructions',
            'refresh_instructions': refresh_instructions,
            'successor_context_key': carry_entry['public_request_carryforward_envelope_key'],
            'successor_context_path': 'example_public_request_carryforward_envelope.json',
            'unchanged_owner_families': ['selected_owner', 'request_class', 'packet_paths'],
            'why': 'The packet remains the same bounded follow-up slice under the canned successor release, so only the listed release-bound field families refresh while packet-local ownership and path membership stay fixed.' if delta_token == 'refresh_fields' else ('The carryforward profile preserves the exact packet unchanged.' if delta_token == 'no_change' else 'The carryforward profile reopens this packet, so no packet-local refresh instructions are sufficient.')
        })


    public_request_response_packet_refresh_notices = {
        'public_request_response_packet_refresh_notices_id': PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_NOTICES_ID,
        'claim_id': compare_report['claim_id'],
        'base_release_id': compare_report['base_release_id'],
        'release_id': compare_report['release_id'],
        'successor_release_id': compare_report['successor_release_id'],
        'compare_profile_id': compare_report['compare_profile_id'],
        'compare_report_id': compare_report['report_id'],
        'successor_public_request_response_packets_id': public_request_response_packets['public_request_response_packets_id'],
        'successor_public_request_response_packet_delta_ledgers_id': public_request_response_packet_delta_ledgers['public_request_response_packet_delta_ledgers_id'],
        'successor_public_request_carryforward_envelopes_id': public_request_carryforward_envelope['public_request_carryforward_envelopes_id'],
        'note_version': compare_report['note_version'],
        'contract': {
            'public_request_response_packet_refresh_notice_fields': ['public_request_response_packet_refresh_notice_key', 'public_request_response_packet_delta_key', 'predecessor_public_request_response_packet_key', 'public_request_notice_key', 'notice_kind', 'request_class', 'packet_reuse_status', 'delta_token', 'refresh_sentence', 'changed_field_families', 'unchanged_packet_paths', 'reader_pointer_order', 'why'],
            'visible_sentence_rule': 'A packet refresh notice emits the exact outward-facing sentence a maintainer may use to summarize the reissue status of one reusable source-only response packet under successor maintenance.',
            'sentence_locality_rule': 'A packet refresh notice may summarize only the imported packet delta ledger and may not widen the packet, add new owner families, or change the already-fixed packet paths.',
            'refresh_notice_rule': 'refresh_fields sentences may be emitted only when the imported packet delta ledger emits refresh_fields; they must name the unchanged bounded slice and the exact field families that refreshed in place.',
            "mirrored_packet_reuse_rule": "packet_reuse_status must mirror the imported packet-delta ledger's packet reuse posture exactly, so visible reissue wrappers cannot silently drift away from the bounded packet's successor-maintenance class."
        },
        'public_request_response_packet_refresh_notices': [],
        'note': "Derived successor-facing visible refresh notices for the worked note's reusable exact source-only response packets. Each entry compresses one packet delta ledger into the exact reissue sentence maintainers can surface without rederiving packet-local refresh semantics by hand."
    }
    request_label_map = {
        'basis_token_check': 'basis-token check',
        'visible_sentence_check': 'visible-sentence check',
        'canonical_family_check': 'canonical-family check',
        'family_choice_check': 'family-choice check',
        'request_scope_check': 'request-scope check',
        'completion_rule_check': 'completion-rule check',
    }
    field_family_label_map = {
        'basis_companions': 'basis companions',
        'selected_entry_excerpt': 'selected entry excerpts',
        'digest_bindings': 'digest bindings',
    }
    for entry in public_request_response_packet_delta_ledgers['public_request_response_packet_delta_ledgers']:
        field_families = [instr['field_family'] for instr in entry.get('refresh_instructions', [])]
        visible_field_families = [field_family_label_map.get(name, name.replace('_', ' ')) for name in field_families]
        if len(visible_field_families) > 1:
            visible_family_phrase = ', '.join(visible_field_families[:-1]) + ', and ' + visible_field_families[-1]
        elif visible_field_families:
            visible_family_phrase = visible_field_families[0]
        else:
            visible_family_phrase = ''
        request_label = request_label_map.get(entry['request_class'], entry['request_class'])
        if entry['delta_token'] == 'refresh_fields':
            refresh_sentence = (
                f"Under successor release {compare_report['successor_release_id']}, the {request_label} response packet for this {entry['notice_kind'].replace('_', '-')} source-only notice remains the same bounded handoff slice; only the {visible_family_phrase} families refresh in place."
            )
        elif entry['delta_token'] == 'no_change':
            refresh_sentence = (
                f"Under successor release {compare_report['successor_release_id']}, the {request_label} response packet for this {entry['notice_kind'].replace('_', '-')} source-only notice is reissued unchanged as the same bounded handoff slice."
            )
        else:
            refresh_sentence = (
                f"Under successor release {compare_report['successor_release_id']}, the {request_label} response packet for this {entry['notice_kind'].replace('_', '-')} source-only notice reopens and must be rebuilt from the narrower owners."
            )
        public_request_response_packet_refresh_notices['public_request_response_packet_refresh_notices'].append({
            'public_request_response_packet_refresh_notice_key': f"{entry['public_request_response_packet_delta_key']}__refresh_notice",
            'public_request_response_packet_delta_key': entry['public_request_response_packet_delta_key'],
            'predecessor_public_request_response_packet_key': entry['predecessor_public_request_response_packet_key'],
            'public_request_notice_key': entry['public_request_notice_key'],
            'notice_kind': entry['notice_kind'],
            'request_class': entry['request_class'],
            'packet_reuse_status': entry['packet_reuse_status'],
            'delta_token': entry['delta_token'],
            'refresh_sentence': refresh_sentence,
            'changed_field_families': field_families,
            'unchanged_packet_paths': entry['reused_packet_paths'],
            'reader_pointer_order': [
                'example_public_request_response_packet_refresh_notices.json',
                'example_public_request_response_packet_delta_ledgers.json',
                'example_public_request_response_packet_carryforward_profiles.json',
                'example_public_request_response_packets.json',
            ],
            'why': 'The exact bounded packet stays the same reusable follow-up slice, so this visible notice compresses only the already-owned packet delta into one sentence that says what remained fixed and which release-bound field families refreshed.' if entry['delta_token'] == 'refresh_fields' else ('The exact bounded packet remains unchanged under successor maintenance, so this visible notice compresses only that preserved reuse verdict.' if entry['delta_token'] == 'no_change' else 'Packet reuse failed under successor maintenance, so this visible notice says the bounded packet must be reopened from the narrower owners.')
        })


    public_request_response_packet_refresh_notice_normal_forms = {
        'public_request_response_packet_refresh_notice_normal_forms_id': PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_NOTICE_NORMAL_FORMS_ID,
        'claim_id': compare_report['claim_id'],
        'base_release_id': compare_report['base_release_id'],
        'release_id': compare_report['release_id'],
        'successor_release_id': compare_report['successor_release_id'],
        'compare_profile_id': compare_report['compare_profile_id'],
        'compare_report_id': compare_report['report_id'],
        'successor_public_request_response_packet_refresh_notices_id': public_request_response_packet_refresh_notices['public_request_response_packet_refresh_notices_id'],
        'successor_public_request_response_packet_delta_ledgers_id': public_request_response_packet_delta_ledgers['public_request_response_packet_delta_ledgers_id'],
        'note_version': compare_report['note_version'],
        'contract': {
            'public_request_response_packet_refresh_notice_normal_form_fields': ['public_request_response_packet_refresh_notice_normal_form_key', 'emitted_public_request_response_packet_refresh_notice_key', 'public_request_response_packet_delta_key', 'notice_kind', 'request_class', 'allowed_delta_tokens', 'template', 'slot_bindings', 'rendered_sentence', 'why'],
            'delta_compatibility_rule': 'A packet-refresh-notice normal form may realize only a delta token already emitted by the imported packet-refresh notice and its packet-delta-ledger basis.',
            'slot_realization_rule': 'Every non-literal semantic phrase in the rendered packet-refresh sentence must come from an explicit slot whose source field is named in slot_bindings, and the rendered sentence must equal the emitted refresh notice sentence exactly.',
            'emitted_notice_inheritance_rule': 'A packet-refresh-notice normal form may factor one emitted visible reissue sentence into a canonical template-and-slot family, but it may not replace the emitted refresh notice key or its reader-pointer order.'
        },
        'public_request_response_packet_refresh_notice_normal_forms': [],
        'note': "Derived canonical visible reissue wrapper families for the worked note's reusable exact source-only response packets. Each entry factors one emitted packet-refresh notice into an explicit template-and-slot form without re-owning the emitted sentence or the narrower packet-local delta."
    }
    request_render_map = {
        'basis_token_check': 'basis-token check',
        'visible_sentence_check': 'visible-sentence check',
        'canonical_family_check': 'canonical-family check',
        'family_choice_check': 'family-choice check',
        'request_scope_check': 'request-scope check',
        'completion_rule_check': 'completion-rule check',
    }
    notice_kind_render_map = {
        'within_release': 'within-release',
        'successor_carryforward': 'successor-carryforward',
    }
    for entry in public_request_response_packet_refresh_notices['public_request_response_packet_refresh_notices']:
        public_request_response_packet_refresh_notice_normal_forms['public_request_response_packet_refresh_notice_normal_forms'].append({
            'public_request_response_packet_refresh_notice_normal_form_key': f"{entry['public_request_response_packet_refresh_notice_key']}__normal_form",
            'emitted_public_request_response_packet_refresh_notice_key': entry['public_request_response_packet_refresh_notice_key'],
            'public_request_response_packet_delta_key': entry['public_request_response_packet_delta_key'],
            'notice_kind': entry['notice_kind'],
            'request_class': entry['request_class'],
            'allowed_delta_tokens': [entry['delta_token']],
            'template': [
                {'literal': 'Under successor release '},
                {'slot': 'successor_release_id'},
                {'literal': ', the '},
                {'slot': 'request_label'},
                {'literal': ' response packet for this '},
                {'slot': 'notice_kind_label'},
                {'literal': ' source-only notice remains the same bounded handoff slice; only the '},
                {'slot': 'changed_field_family_phrase'},
                {'literal': ' families refresh in place.'}
            ],
            'slot_bindings': [
                {'slot': 'successor_release_id', 'source_artifact': 'example_compare_report.json', 'source_field': 'successor_release_id'},
                {'slot': 'request_label', 'source_artifact': 'example_public_request_response_packet_refresh_notices.json', 'source_field': 'request_class', 'render_map': request_render_map},
                {'slot': 'notice_kind_label', 'source_artifact': 'example_public_request_response_packet_refresh_notices.json', 'source_field': 'notice_kind', 'render_map': notice_kind_render_map},
                {'slot': 'changed_field_family_phrase', 'source_artifact': 'example_public_request_response_packet_refresh_notices.json', 'source_field': 'changed_field_families', 'render_map': field_family_label_map, 'join_rule': 'comma_then_and'}
            ],
            'rendered_sentence': entry['refresh_sentence'],
            'why': 'The emitted visible reissue sentence is a refresh-in-place wrapper, so this normal form records the canonical template-and-slot family behind that already-owned sentence.'
        })

    public_request_response_packet_refresh_notice_selections = {
        'public_request_response_packet_refresh_notice_selections_id': PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_NOTICE_SELECTIONS_ID,
        'claim_id': compare_report['claim_id'],
        'base_release_id': compare_report['base_release_id'],
        'release_id': compare_report['release_id'],
        'successor_release_id': compare_report['successor_release_id'],
        'compare_profile_id': compare_report['compare_profile_id'],
        'compare_report_id': compare_report['report_id'],
        'successor_public_request_response_packet_refresh_notices_id': public_request_response_packet_refresh_notices['public_request_response_packet_refresh_notices_id'],
        'successor_public_request_response_packet_refresh_notice_normal_forms_id': public_request_response_packet_refresh_notice_normal_forms['public_request_response_packet_refresh_notice_normal_forms_id'],
        'successor_public_request_response_packet_delta_ledgers_id': public_request_response_packet_delta_ledgers['public_request_response_packet_delta_ledgers_id'],
        'note_version': compare_report['note_version'],
        'contract': {
            'public_request_response_packet_refresh_notice_selection_fields': ['public_request_response_packet_refresh_notice_selection_key', 'basis_key', 'notice_kind', 'request_class', 'selector_inputs', 'selected_public_request_response_packet_refresh_notice_normal_form_key', 'selected_emitted_public_request_response_packet_refresh_notice_key', 'selection_decision', 'rendered_sentence', 'why'],
            'basis_token_rule': 'selector_inputs may import only delta_token plus the emitted notice kind and request class already owned by the packet-refresh notice and packet-delta ledger basis.',
            'family_choice_rule': 'A packet-refresh-notice selection must choose exactly one canonical packet-refresh-notice normal form whose allowed delta tokens, notice kind, and request class match the imported emitted notice.',
            'emitted_agreement_rule': 'The selector rendered sentence must match both the emitted packet-refresh sentence and the rendered sentence of the selected canonical normal form exactly.'
        },
        'public_request_response_packet_refresh_notice_selections': [],
        'note': "Derived selector ledger for the worked note's successor-facing source-only response-packet refresh notices. It chooses which already-owned canonical visible reissue family applies given the imported packet-local delta token, notice kind, and request class."
    }

    refresh_notice_nf_by_basis = {(entry['notice_kind'], entry['request_class'], tuple(entry.get('allowed_delta_tokens', []))): entry for entry in public_request_response_packet_refresh_notice_normal_forms['public_request_response_packet_refresh_notice_normal_forms']}
    for entry in public_request_response_packet_refresh_notices['public_request_response_packet_refresh_notices']:
        nf_entry = refresh_notice_nf_by_basis[(entry['notice_kind'], entry['request_class'], (entry['delta_token'],))]
        public_request_response_packet_refresh_notice_selections['public_request_response_packet_refresh_notice_selections'].append({
            'public_request_response_packet_refresh_notice_selection_key': f"{entry['public_request_response_packet_refresh_notice_key']}__selection",
            'basis_key': entry['public_request_response_packet_delta_key'],
            'notice_kind': entry['notice_kind'],
            'request_class': entry['request_class'],
            'selector_inputs': {
                'delta_token': entry['delta_token'],
                'notice_kind': entry['notice_kind'],
                'request_class': entry['request_class'],
            },
            'selected_public_request_response_packet_refresh_notice_normal_form_key': nf_entry['public_request_response_packet_refresh_notice_normal_form_key'],
            'selected_emitted_public_request_response_packet_refresh_notice_key': entry['public_request_response_packet_refresh_notice_key'],
            'selection_decision': f"select_{entry['notice_kind']}_{entry['request_class']}_{entry['delta_token']}_packet_refresh_notice_normal_form",
            'rendered_sentence': entry['refresh_sentence'],
            'why': 'The selector chooses the matching canonical visible reissue family from the imported packet-local delta token, request class, and notice kind rather than leaving packet-refresh family choice implicit in prose.'
        })


    public_request_response_packet_refresh_response_menus = {
        'public_request_response_packet_refresh_response_menus_id': PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_RESPONSE_MENUS_ID,
        'claim_id': compare_report['claim_id'],
        'base_release_id': compare_report['base_release_id'],
        'release_id': compare_report['release_id'],
        'successor_release_id': compare_report['successor_release_id'],
        'compare_profile_id': compare_report['compare_profile_id'],
        'compare_report_id': compare_report['report_id'],
        'successor_public_request_response_packets_id': public_request_response_packets['public_request_response_packets_id'],
        'successor_public_request_response_packet_carryforward_profiles_id': public_request_response_packet_carryforward_profiles['public_request_response_packet_carryforward_profiles_id'],
        'successor_public_request_response_packet_delta_ledgers_id': public_request_response_packet_delta_ledgers['public_request_response_packet_delta_ledgers_id'],
        'successor_public_request_response_packet_refresh_notices_id': public_request_response_packet_refresh_notices['public_request_response_packet_refresh_notices_id'],
        'successor_public_request_response_packet_refresh_notice_normal_forms_id': public_request_response_packet_refresh_notice_normal_forms['public_request_response_packet_refresh_notice_normal_forms_id'],
        'successor_public_request_response_packet_refresh_notice_selections_id': public_request_response_packet_refresh_notice_selections['public_request_response_packet_refresh_notice_selections_id'],
        'note_version': compare_report['note_version'],
        'contract': {
            'public_request_response_packet_refresh_response_menu_fields': ['public_request_response_packet_refresh_response_menu_key', 'notice_kind', 'request_class', 'public_request_response_packet_key', 'public_request_response_packet_carryforward_profile_key', 'public_request_response_packet_delta_key', 'public_request_response_packet_refresh_notice_key', 'selected_public_request_response_packet_refresh_notice_normal_form_key', 'public_request_response_packet_refresh_notice_selection_key', 'response_entries', 'why'],
            'request_class_rule': 'response_entries must cover exactly the concrete successor-facing follow-up classes packet_membership_check, packet_reuse_check, packet_delta_check, visible_refresh_sentence_check, canonical_refresh_family_check, and refresh_family_choice_check for the same emitted packet-refresh notice.',
            'smallest_sufficient_rule': 'Packet-membership checks use the imported response packet, packet-reuse checks use the imported packet-carryforward profile, packet-delta checks use the imported packet-delta ledger, visible-refresh-sentence checks use the emitted packet-refresh notice, canonical-refresh-family checks use the packet-refresh-notice normal form, and refresh-family-choice checks use the packet-refresh-notice selection.',
            'import_rule': 'Each response entry must copy imported packet membership, reuse verdict, delta fields, rendered sentence, canonical family, or family choice exactly; the menu may not create new successor-facing packet semantics while pretending only to select a handoff object.',
            'non_semantic_rule': 'Packet-refresh response menus own only follow-up-class response selection for one already-maintained emitted packet-refresh notice.'
        },
        'public_request_response_packet_refresh_response_menus': [],
        'note': "Derived successor-facing response-menu ledger for concrete follow-up classes about the worked note's emitted packet-refresh notices. Each menu says which already-owned object is the smallest sufficient handoff for one concrete question about a visible reissue sentence."
    }

    response_packet_by_key = {entry['public_request_response_packet_key']: entry for entry in public_request_response_packets['public_request_response_packets']}
    response_packet_carryforward_by_key = {entry['public_request_response_packet_carryforward_profile_key']: entry for entry in public_request_response_packet_carryforward_profiles['public_request_response_packet_carryforward_profiles']}
    response_packet_delta_by_key = {entry['public_request_response_packet_delta_key']: entry for entry in public_request_response_packet_delta_ledgers['public_request_response_packet_delta_ledgers']}
    response_packet_refresh_notice_by_key = {entry['public_request_response_packet_refresh_notice_key']: entry for entry in public_request_response_packet_refresh_notices['public_request_response_packet_refresh_notices']}
    response_packet_refresh_nf_by_key = {entry['public_request_response_packet_refresh_notice_normal_form_key']: entry for entry in public_request_response_packet_refresh_notice_normal_forms['public_request_response_packet_refresh_notice_normal_forms']}
    for sel_entry in public_request_response_packet_refresh_notice_selections['public_request_response_packet_refresh_notice_selections']:
        notice_entry = response_packet_refresh_notice_by_key[sel_entry['selected_emitted_public_request_response_packet_refresh_notice_key']]
        delta_entry = response_packet_delta_by_key[notice_entry['public_request_response_packet_delta_key']]
        carry_entry = response_packet_carryforward_by_key[delta_entry['public_request_response_packet_carryforward_profile_key']]
        packet_entry = response_packet_by_key[delta_entry['predecessor_public_request_response_packet_key']]
        nf_entry = response_packet_refresh_nf_by_key[sel_entry['selected_public_request_response_packet_refresh_notice_normal_form_key']]
        public_request_response_packet_refresh_response_menus['public_request_response_packet_refresh_response_menus'].append({
            'public_request_response_packet_refresh_response_menu_key': f"{sel_entry['public_request_response_packet_refresh_notice_selection_key']}__response_menu",
            'notice_kind': sel_entry['notice_kind'],
            'request_class': sel_entry['request_class'],
            'public_request_response_packet_key': packet_entry['public_request_response_packet_key'],
            'public_request_response_packet_carryforward_profile_key': carry_entry['public_request_response_packet_carryforward_profile_key'],
            'public_request_response_packet_delta_key': delta_entry['public_request_response_packet_delta_key'],
            'public_request_response_packet_refresh_notice_key': notice_entry['public_request_response_packet_refresh_notice_key'],
            'selected_public_request_response_packet_refresh_notice_normal_form_key': nf_entry['public_request_response_packet_refresh_notice_normal_form_key'],
            'public_request_response_packet_refresh_notice_selection_key': sel_entry['public_request_response_packet_refresh_notice_selection_key'],
            'response_entries': [
                {'request_class': 'packet_membership_check', 'object_kind': 'public_request_response_packet', 'object_key': packet_entry['public_request_response_packet_key'], 'cite_path': 'example_public_request_response_packets.json', 'selected_entry': packet_entry, 'when': 'Need the exact bounded source-only handoff slice that the visible refresh sentence is talking about.', 'why': 'The response packet is the smallest maintained object that freezes exact packet membership for this successor-facing reissue sentence.'},
                {'request_class': 'packet_reuse_check', 'object_kind': 'public_request_response_packet_carryforward_profile', 'object_key': carry_entry['public_request_response_packet_carryforward_profile_key'], 'cite_path': 'example_public_request_response_packet_carryforward_profiles.json', 'selected_entry': carry_entry, 'when': 'Need the narrow successor verdict saying whether that exact packet survived, refreshed in place, or reopened.', 'why': 'The packet-carryforward profile is the smallest maintained object that owns packet reuse classification.'},
                {'request_class': 'packet_delta_check', 'object_kind': 'public_request_response_packet_delta_ledger', 'object_key': delta_entry['public_request_response_packet_delta_key'], 'cite_path': 'example_public_request_response_packet_delta_ledgers.json', 'selected_entry': delta_entry, 'when': 'Need the exact packet-local field families that refreshed while that bounded slice stayed the same.', 'why': 'The delta ledger is the smallest maintained object that names the refreshed field families without re-cutting the packet.'},
                {'request_class': 'visible_refresh_sentence_check', 'object_kind': 'public_request_response_packet_refresh_notice', 'object_key': notice_entry['public_request_response_packet_refresh_notice_key'], 'cite_path': 'example_public_request_response_packet_refresh_notices.json', 'selected_entry': notice_entry, 'when': 'Need the exact outward-facing successor reissue sentence that readers actually saw.', 'why': 'The emitted packet-refresh notice is the smallest maintained object that owns the visible wrapper sentence.'},
                {'request_class': 'canonical_refresh_family_check', 'object_kind': 'public_request_response_packet_refresh_notice_normal_form', 'object_key': nf_entry['public_request_response_packet_refresh_notice_normal_form_key'], 'cite_path': 'example_public_request_response_packet_refresh_notice_normal_forms.json', 'selected_entry': nf_entry, 'when': 'Need the reusable canonical visible wrapper family and explicit slot bindings behind that emitted refresh sentence.', 'why': 'The normal-form owner is the smallest maintained object that fixes the reusable packet-refresh wrapper family rather than just one wrapper instance.'},
                {'request_class': 'refresh_family_choice_check', 'object_kind': 'public_request_response_packet_refresh_notice_selection', 'object_key': sel_entry['public_request_response_packet_refresh_notice_selection_key'], 'cite_path': 'example_public_request_response_packet_refresh_notice_selections.json', 'selected_entry': sel_entry, 'when': 'Need to know why this canonical visible reissue family was chosen for the shipped successor-facing token basis rather than another family.', 'why': 'The selector is the smallest maintained object that owns token-to-family choice for one emitted packet-refresh sentence.'}
            ],
            'why': 'This successor-facing response menu answers concrete follow-up about one emitted packet-refresh sentence without collapsing packet membership, reuse verdict, delta, visible wrapper, canonical family, and family-choice ownership into one object.'
        })


    public_request_response_packet_refresh_response_packets = {
        'public_request_response_packet_refresh_response_packets_id': PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_RESPONSE_PACKETS_ID,
        'claim_id': compare_report['claim_id'],
        'base_release_id': compare_report['base_release_id'],
        'release_id': compare_report['release_id'],
        'successor_release_id': compare_report['successor_release_id'],
        'compare_profile_id': compare_report['compare_profile_id'],
        'compare_report_id': compare_report['report_id'],
        'successor_public_request_response_packet_refresh_response_menus_id': public_request_response_packet_refresh_response_menus['public_request_response_packet_refresh_response_menus_id'],
        'contract': {
            'public_request_response_packet_refresh_response_packet_fields': ['public_request_response_packet_refresh_response_packet_key', 'notice_kind', 'request_class', 'successor_followup_class', 'public_request_response_packet_refresh_response_menu_key', 'selected_object_kind', 'selected_object_key', 'selected_object_path', 'selected_entry_excerpt', 'basis_cite_path', 'basis_key', 'packet_reuse_status', 'packet_paths', 'required_public_paths', 'required_validation_paths', 'public_request_response_packet_refresh_notice_key', 'why', 'when'],
            'owner_packet_rule': 'Each packet imports exactly one response-menu choice for the same emitted packet-refresh notice and successor follow-up class and copies only the selected entry excerpt from that owner.',
            'bounded_companion_rule': 'Added paths beyond the selected owner path are limited to the emitted packet-refresh notice path plus the narrower packet, carryforward, delta, or canonical-family basis paths the selected successor owner already needs for auditability.',
            'minimality_rule': 'No packet path may come from an unrelated source-only family once the emitted packet-refresh notice and successor follow-up class have been fixed.',
            "mirrored_packet_reuse_rule": "packet_reuse_status must mirror the emitted refresh notice's packet reuse posture exactly, so successor-facing packets keep the same explicit reuse class as the bounded slice they package."
        },
        'public_request_response_packet_refresh_response_packets': [],
        'note': 'Derived successor-facing response-packet ledger for exact bounded handoff slices about the worked note\'s visible packet-refresh notices. Each packet freezes the exact owner excerpt and only the narrower companion paths that the selected successor-facing owner already requires.'
    }

    refresh_response_packet_path_map = {
        'packet_membership_check': ['example_public_request_response_packets.json', 'example_public_request_response_packet_refresh_notices.json'],
        'packet_reuse_check': ['example_public_request_response_packets.json', 'example_public_request_response_packet_carryforward_profiles.json', 'example_public_request_response_packet_refresh_notices.json'],
        'packet_delta_check': ['example_public_request_response_packets.json', 'example_public_request_response_packet_carryforward_profiles.json', 'example_public_request_response_packet_delta_ledgers.json', 'example_public_request_response_packet_refresh_notices.json'],
        'visible_refresh_sentence_check': ['example_public_request_response_packet_delta_ledgers.json', 'example_public_request_response_packet_refresh_notices.json'],
        'canonical_refresh_family_check': ['example_public_request_response_packet_delta_ledgers.json', 'example_public_request_response_packet_refresh_notices.json', 'example_public_request_response_packet_refresh_notice_normal_forms.json'],
        'refresh_family_choice_check': ['example_public_request_response_packet_delta_ledgers.json', 'example_public_request_response_packet_refresh_notices.json', 'example_public_request_response_packet_refresh_notice_normal_forms.json', 'example_public_request_response_packet_refresh_notice_selections.json'],
    }
    refresh_response_packet_why_map = {
        'packet_membership_check': 'The packet-membership successor packet includes the exact predecessor packet together with the emitted refresh notice so the visible reissue sentence and the bounded slice it points at travel together.',
        'packet_reuse_check': 'The packet-reuse successor packet includes the carryforward profile together with the exact predecessor packet and emitted refresh notice so reuse classification stays tied to the visible successor-facing question.',
        'packet_delta_check': 'The packet-delta successor packet includes the delta ledger together with the carryforward profile, exact predecessor packet, and emitted refresh notice so changed field families are auditable without widening to the whole successor tail.',
        'visible_refresh_sentence_check': 'The visible-refresh-sentence successor packet includes the emitted refresh notice together with the packet-delta basis it compresses so outward wording and packet-local change basis travel together.',
        'canonical_refresh_family_check': 'The canonical-refresh-family successor packet includes the normal-form owner together with the emitted refresh notice and packet-delta basis so canonical wrapper family identity stays separate from one emitted sentence instance.',
        'refresh_family_choice_check': 'The refresh-family-choice successor packet includes the selector together with the chosen normal form, emitted refresh notice, and packet-delta basis so family choice is auditable without re-reading unrelated owners.'
    }
    refresh_response_packet_when_map = {
        'packet_membership_check': 'Need the exact bounded predecessor handoff slice that this visible successor reissue sentence is talking about.',
        'packet_reuse_check': 'Need the narrow successor verdict saying whether that exact bounded packet survived, refreshed in place, or reopened.',
        'packet_delta_check': 'Need the exact packet-local field families that refreshed while that bounded packet stayed the same.',
        'visible_refresh_sentence_check': 'Need the exact outward-facing successor reissue sentence plus the packet-delta basis it compresses.',
        'canonical_refresh_family_check': 'Need the reusable canonical visible reissue family and explicit slot bindings behind that emitted refresh sentence.',
        'refresh_family_choice_check': 'Need to know why this canonical visible reissue family was chosen for the shipped successor packet-delta basis rather than another family.'
    }
    basis_key_map = {
        'packet_membership_check': ('example_public_request_response_packet_refresh_notices.json', 'public_request_response_packet_refresh_notice_key'),
        'packet_reuse_check': ('example_public_request_response_packet_refresh_notices.json', 'public_request_response_packet_refresh_notice_key'),
        'packet_delta_check': ('example_public_request_response_packet_refresh_notices.json', 'public_request_response_packet_refresh_notice_key'),
        'visible_refresh_sentence_check': ('example_public_request_response_packet_delta_ledgers.json', 'public_request_response_packet_delta_key'),
        'canonical_refresh_family_check': ('example_public_request_response_packet_delta_ledgers.json', 'public_request_response_packet_delta_key'),
        'refresh_family_choice_check': ('example_public_request_response_packet_delta_ledgers.json', 'public_request_response_packet_delta_key'),
    }

    for menu_entry in public_request_response_packet_refresh_response_menus['public_request_response_packet_refresh_response_menus']:
        for response_entry in menu_entry['response_entries']:
            followup_class = response_entry['request_class']
            basis_path, basis_field = basis_key_map[followup_class]
            public_request_response_packet_refresh_response_packets['public_request_response_packet_refresh_response_packets'].append({
                'public_request_response_packet_refresh_response_packet_key': f"{menu_entry['public_request_response_packet_refresh_response_menu_key']}__{followup_class}",
                'notice_kind': menu_entry['notice_kind'],
                'request_class': menu_entry['request_class'],
                'successor_followup_class': followup_class,
                'public_request_response_packet_refresh_response_menu_key': menu_entry['public_request_response_packet_refresh_response_menu_key'],
                'selected_object_kind': response_entry['object_kind'],
                'selected_object_key': response_entry['object_key'],
                'selected_object_path': response_entry['cite_path'],
                'selected_entry_excerpt': response_entry['selected_entry'],
                'basis_cite_path': basis_path,
                'basis_key': menu_entry[basis_field],
                'packet_reuse_status': notice_entry['packet_reuse_status'],
                'packet_paths': refresh_response_packet_path_map[followup_class],
                'required_public_paths': [],
                'required_validation_paths': [],
                'validation_capsule_mode': 'public_only',
                'public_request_response_packet_refresh_notice_key': menu_entry['public_request_response_packet_refresh_notice_key'],
                'when': refresh_response_packet_when_map[followup_class],
                'why': refresh_response_packet_why_map[followup_class],
            })

    refresh_response_menu_key_map = {
        (entry['notice_kind'], entry['request_class']): entry['public_request_response_packet_refresh_response_menu_key']
        for entry in public_request_response_packet_refresh_response_menus['public_request_response_packet_refresh_response_menus']
    }
    response_packet_carryforward_key_map = {
        (entry['notice_kind'], entry['request_class']): entry['public_request_response_packet_carryforward_profile_key']
        for entry in public_request_response_packet_carryforward_profiles['public_request_response_packet_carryforward_profiles']
    }
    refresh_notice_selection_key_map = {
        (entry['notice_kind'], entry['request_class']): entry['public_request_response_packet_refresh_notice_selection_key']
        for entry in public_request_response_packet_refresh_notice_selections['public_request_response_packet_refresh_notice_selections']
    }

    public_request_response_packet_refresh_response_packet_closure_verdicts = {
        'public_request_response_packet_refresh_response_packet_closure_verdicts_id': PUBLIC_REQUEST_RESPONSE_PACKET_REFRESH_RESPONSE_PACKET_CLOSURE_VERDICTS_ID,
        'claim_id': compare_report['claim_id'],
        'base_release_id': compare_report['base_release_id'],
        'release_id': compare_report['release_id'],
        'successor_release_id': compare_report['successor_release_id'],
        'compare_profile_id': compare_report['compare_profile_id'],
        'compare_report_id': compare_report['report_id'],
        'successor_public_request_response_packet_refresh_response_packets_id': public_request_response_packet_refresh_response_packets['public_request_response_packet_refresh_response_packets_id'],
        'contract': {
            'public_request_response_packet_refresh_response_packet_closure_verdict_fields': ['public_request_response_packet_refresh_response_packet_closure_verdict_key', 'notice_kind', 'request_class', 'successor_followup_class', 'public_request_response_packet_refresh_response_packet_key', 'selected_object_kind', 'selected_object_key', 'selected_object_path', 'closure_status', 'closure_basis_scope', 'validation_capsule_mode', 'closed_public_paths', 'outside_closure_validation_paths', 'reopen_trigger_tokens', 'reopen_owner_map', 'why', 'when'],
            'terminal_basis_rule': 'Each closure verdict imports exactly one exact successor-facing response packet and certifies closure only when that packet already contains the selected owner excerpt and every narrower companion path the selected owner requires.',
            'closure_scope_rule': 'closure_basis_scope must stay public_paths_only: closure certifies the exact public packet basis and may mirror any shared validation companions only as outside_closure_validation_paths rather than silently absorbing them into the finite public basis.',
            'no_hidden_successor_owner_rule': 'A closure verdict may declare closed_finite_basis only when no additional successor-facing public-request owner remains unresolved for the same emitted packet-refresh notice and shipped follow-up class.',
            'reopen_trigger_rule': 'Every listed reopen trigger must be branch-local: shipped follow-up taxonomy expansion, packet reuse reopening, or a future rewrite in which the emitted visible sentence no longer compresses the same packet-local delta family.',
            'reopen_owner_rule': 'Every listed reopen trigger must name the first maintained owner that regains authority when that trigger fires: the successor follow-up response menu for taxonomy expansion, the predecessor packet carryforward profile for packet reuse reopening, or the refresh-notice selection for visible-family rebinding.'
        },
        'public_request_response_packet_refresh_response_packet_closure_verdicts': [],
        'note': 'Derived successor-facing closure-verdict ledger certifying when one exact bounded packet-refresh handoff slice already closes the visible reissue branch under the shipped follow-up taxonomy and may therefore serve as a stable finite public basis until a named reopen trigger fires.'
    }

    for packet_entry in public_request_response_packet_refresh_response_packets['public_request_response_packet_refresh_response_packets']:
        public_request_response_packet_refresh_response_packet_closure_verdicts['public_request_response_packet_refresh_response_packet_closure_verdicts'].append({
            'public_request_response_packet_refresh_response_packet_closure_verdict_key': f"{packet_entry['public_request_response_packet_refresh_response_packet_key']}__closure",
            'notice_kind': packet_entry['notice_kind'],
            'request_class': packet_entry['request_class'],
            'successor_followup_class': packet_entry['successor_followup_class'],
            'public_request_response_packet_refresh_response_packet_key': packet_entry['public_request_response_packet_refresh_response_packet_key'],
            'selected_object_kind': packet_entry['selected_object_kind'],
            'selected_object_key': packet_entry['selected_object_key'],
            'selected_object_path': packet_entry['selected_object_path'],
            'closure_status': 'closed_finite_basis',
            'closure_basis_scope': 'public_paths_only',
            'validation_capsule_mode': packet_entry['validation_capsule_mode'],
            'closed_public_paths': packet_entry['packet_paths'] + packet_entry.get('required_public_paths', []),
            'outside_closure_validation_paths': packet_entry.get('required_validation_paths', []),
            'reopen_trigger_tokens': ['followup_taxonomy_expands', 'packet_reuse_reopens', 'visible_refresh_sentence_rebinds_to_new_delta_family'],
            'reopen_owner_map': {
                'followup_taxonomy_expands': {
                    'owner_object_kind': 'public_request_response_packet_refresh_response_menu',
                    'owner_object_key': refresh_response_menu_key_map[(packet_entry['notice_kind'], packet_entry['request_class'])],
                    'owner_cite_path': 'example_public_request_response_packet_refresh_response_menus.json',
                    'why': 'If the shipped successor follow-up taxonomy expands, the first maintained owner to reopen is the successor follow-up response menu that selects the smallest sufficient owner for the newly added class.'
                },
                'packet_reuse_reopens': {
                    'owner_object_kind': 'public_request_response_packet_carryforward_profile',
                    'owner_object_key': response_packet_carryforward_key_map[(packet_entry['notice_kind'], packet_entry['request_class'])],
                    'owner_cite_path': 'example_public_request_response_packet_carryforward_profiles.json',
                    'why': 'If packet reuse itself flips back to reopen, the first maintained owner to regain authority is the predecessor packet carryforward profile that decides whether any same-slice successor branch remains at all.'
                },
                'visible_refresh_sentence_rebinds_to_new_delta_family': {
                    'owner_object_kind': 'public_request_response_packet_refresh_notice_selection',
                    'owner_object_key': refresh_notice_selection_key_map[(packet_entry['notice_kind'], packet_entry['request_class'])],
                    'owner_cite_path': 'example_public_request_response_packet_refresh_notice_selections.json',
                    'why': 'If the emitted visible refresh sentence now compresses a different delta family, the first maintained owner to reopen is the refresh-notice selection that re-chooses the canonical family for that successor-facing basis.'
                }
            },
            'when': 'Need an explicit capstone verdict that this exact successor-facing packet already closes the refreshed visible-handoff branch under the shipped follow-up taxonomy.',
            'why': 'Once the exact successor-facing packet has been cut, no additional successor-facing public-request owner remains on this branch for the shipped follow-up taxonomy; later terse papers may therefore cite this closure verdict instead of extending the chain by implication.'
        })

    minimal_bridge_cuts = [
        {
            'task_key': 'mechanism_justification',
            'stop_kind': 'series_spine_segment',
            'spine_segment': 'mathematical_root',
            'canonical_owner': 'Synthesis~24 (+ cited backbone)',
            'artifact': 'example_line_item_owner_map.json',
            'question': 'Which theorem or lower bound justifies the mechanism content?',
            'why': 'Stop at the theorem root when no public claim, replay, or release-maintenance question is being asked.'
        },
        {
            'task_key': 'public_claim_identification',
            'stop_kind': 'series_spine_segment',
            'spine_segment': 'receipt_anchor',
            'canonical_owner': 'Synthesis~12 / receipt-facing owner note',
            'artifact': 'example_receipt.json',
            'question': 'Where does that content land on the public receipt surface?',
            'why': 'The receipt anchor owns the released claim surface and should answer identification questions without widening into replay or review policy.'
        },
        {
            'task_key': 'replay_verification',
            'stop_kind': 'series_spine_segment',
            'spine_segment': 'replay_anchor',
            'canonical_owner': 'Synthesis~20 (+ replay adjuncts)',
            'artifact': 'example_replay_plans.json',
            'question': 'How can the declared claim be checked or replayed?',
            'why': 'Replay questions should stop at the replay anchor rather than drifting into successor wording or review packaging.'
        },
        {
            'task_key': 'release_evolution_status',
            'stop_kind': 'series_spine_segment',
            'spine_segment': 'release_anchor',
            'canonical_owner': 'Synthesis~32',
            'artifact': 'example_release_spine.json',
            'question': 'Which successor-maintenance stage family must move if this claim drifts?',
            'why': 'Release-evolution questions stop at the maintained release-stage owner before any downstream wrapper prose or review menu is consulted.'
        },
        {
            'task_key': 'answer_side_archive_cut',
            'stop_kind': 'series_spine_segment',
            'spine_segment': 'disclosure_packet_anchor',
            'canonical_owner': 'Synthesis~52',
            'artifact': 'example_successor_challenge_answer_disclosure_packets.json',
            'question': 'What exact paper-facing archive slice should travel when omitted support is requested?',
            'why': 'The disclosure packet is the first sufficient answer-side owner for the public-on-request archive cut before any wider review or source-only machinery is consulted.'
        },
        {
            'task_key': 'referee_followup_packaging',
            'stop_kind': 'series_spine_segment',
            'spine_segment': 'review_anchor',
            'canonical_owner': 'Synthesis~54',
            'artifact': 'example_successor_challenge_answer_review_menus.json',
            'question': 'What is the smallest sufficient handoff for one concrete referee follow-up class after that archive cut?',
            'why': 'Once the task widens past the paper-facing archive cut into follow-up packaging, the maintained review menu is the first sufficient owner.'
        },
        {
            'task_key': 'source_only_request_promise_and_notice',
            'stop_kind': 'owner_bucket',
            'bucket_key': 'paper_level_request_contracts_and_notice_choice',
            'canonical_owner': 'Synthesis~56--63',
            'artifact': 'example_public_request_notice_selections.json',
            'question': 'What exactly was promised to readers, and what visible status/notice family was emitted?',
            'why': 'These are adjacent source-only request owners, not extra spine segments; the routing rule is to stop at their first sufficient bucket rather than stretch the theorem-to-review bridge.'
        },
        {
            'task_key': 'bounded_response_packet_and_reuse',
            'stop_kind': 'owner_bucket',
            'bucket_key': 'notice_keyed_response_packetization',
            'canonical_owner': 'Synthesis~64--67',
            'artifact': 'example_public_request_response_packet_delta_ledgers.json',
            'question': 'Once one follow-up class is fixed, which bounded handoff slice travels and how may it be reused?',
            'why': 'This is the first source-only bucket that owns concrete packet cuts and their reuse/delta rules.'
        },
        {
            'task_key': 'visible_refresh_notice_choice',
            'stop_kind': 'owner_bucket',
            'bucket_key': 'visible_refresh_notice_choice',
            'canonical_owner': 'Synthesis~68--70',
            'artifact': 'example_public_request_response_packet_refresh_notice_selections.json',
            'question': 'If that reused packet survives the successor cut, what visible reissue sentence/family/selection is licensed?',
            'why': 'Visible refresh wording belongs to its own owner bucket before any successor-facing follow-up choice is made.'
        },
        {
            'task_key': 'successor_refresh_response_packet_and_closure',
            'stop_kind': 'owner_bucket',
            'bucket_key': 'successor_refresh_response_packetization_and_closure',
            'canonical_owner': 'Synthesis~71--73',
            'artifact': 'example_public_request_response_packet_refresh_response_packet_closure_verdicts.json',
            'question': 'After one concrete follow-up about that refreshed visible sentence, which successor-facing packet closes the branch?',
            'why': 'This final adjacent bucket owns the successor-facing follow-up choice, exact packet cut, and capstone closure verdict.'
        }
    ]


    generic_question_examples = {
        'mechanism_justification': ['Which theorem or lower bound justifies the fallback-vector claim?'],
        'public_claim_identification': ['Where on the public receipt does the fallback contact-surface claim land?'],
        'replay_verification': ['What exact replay plan should be rerun to recompute the fallback vector?'],
        'release_evolution_status': ['If the contact surface drifts, what release-stage family must move and did the successor package close?'],
        'answer_side_archive_cut': ['What exact archive slice should travel when omitted support is requested about that shipped answer?'],
        'referee_followup_packaging': ['What is the smallest sufficient maintained handoff once a referee asks for more support after that archive cut?'],
        'source_only_request_promise_and_notice': ['What source-only promise was made to readers, and what visible notice family was emitted?'],
        'bounded_response_packet_and_reuse': ['After one follow-up-class choice, which bounded response packet travels and how may it be reused?'],
        'visible_refresh_notice_choice': ['If that reused packet survives the successor cut, which visible refresh sentence/family may be surfaced?'],
        'successor_refresh_response_packet_and_closure': ['After one concrete follow-up about the refreshed visible sentence, which successor-facing packet closes the branch?'],
    }
    stop_rule_map = {
        'mechanism_justification': {
            'stop_when': 'The task is theorem or lower-bound justification for the mechanism content.',
            'widen_only_if': 'Widen only if the question becomes public-claim identification rather than mathematical provenance.'
        },
        'public_claim_identification': {
            'stop_when': 'The task is locating the released claim on the public receipt surface.',
            'widen_only_if': 'Widen only if the question becomes replay, release drift, or later follow-up packaging.'
        },
        'replay_verification': {
            'stop_when': 'The task is checking or recomputing the declared claim.',
            'widen_only_if': 'Widen only if the question becomes release evolution or later handoff policy rather than replay.'
        },
        'release_evolution_status': {
            'stop_when': 'The task is deciding which maintained stage family must move after drift.',
            'widen_only_if': 'Widen only if the question becomes the exact public-on-request archive cut or later follow-up packaging.'
        },
        'answer_side_archive_cut': {
            'stop_when': 'The task is the exact paper-facing archive slice that should travel on request.',
            'widen_only_if': 'Widen only if the question becomes one concrete referee follow-up class or leaves the answer side for the source-only request tail.'
        },
        'referee_followup_packaging': {
            'stop_when': 'The task is the smallest sufficient handoff for one concrete referee follow-up class after that archive cut.',
            'widen_only_if': 'Widen only if the question becomes a source-only request or successor-refresh packet owner question rather than answer-side follow-up packaging.'
        },
        'source_only_request_promise_and_notice': {
            'stop_when': 'The task is the exact paper-level source-only request-contract / evidence-class / fulfillment-certificate / status-envelope / carryforward-envelope / notice / canonical-notice-family / notice-normal-form / notice-selection chain.',
            'widen_only_if': 'Widen only if one follow-up class is fixed and the question becomes the exact response-menu / request-class-owner / response-packet / packet-scope / packet-family-basis / packet-support-surface / packet-manifest-cut / packet-inventory-cut / packet-carryforward-profile / packet-delta-ledger chain.'
        },
        'bounded_response_packet_and_reuse': {
            'stop_when': 'The task is the exact source-only response-menu / request-class-owner / response-packet / packet-scope / packet-family-basis / packet-support-surface / packet-manifest-cut / packet-inventory-cut / packet-carryforward-profile / packet-delta-ledger chain after one follow-up class is fixed.',
            'widen_only_if': 'Widen only if the question becomes the visible refresh-notice / canonical-refresh-family / refresh-normal-form / refresh-selection chain for a reused packet.'
        },
        'visible_refresh_notice_choice': {
            'stop_when': 'The task is the exact visible refresh-notice / canonical-refresh-family / refresh-normal-form / refresh-selection chain licensed for a reused packet.',
            'widen_only_if': 'Widen only if the question becomes a successor-facing follow-up packet or closure question.'
        },
        'successor_refresh_response_packet_and_closure': {
            'stop_when': 'The task is the exact successor-facing refresh-response-menu / successor-followup-owner / successor-facing packet / validation-posture / closure-verdict / closure-scope chain.',
            'widen_only_if': 'Do not widen unless the shipped follow-up taxonomy itself changes.'
        },
    }
    bridge_cut_sentence_map = {
        'mechanism_justification': 'Stop at the maintained theorem-root bridge card when the live issue is only which published mathematics root justifies the mechanism content.',
        'public_claim_identification': 'Stop at the maintained receipt-anchor bridge card when the live issue is only where the public claim lands on the receipt surface.',
        'replay_verification': 'Stop at the maintained replay-anchor bridge card when the live issue is only how the declared claim is checked or replayed.',
        'release_evolution_status': 'Stop at the maintained release-anchor bridge card when the live issue is only which release-stage family must move after drift.',
        'answer_side_archive_cut': 'Stop at the maintained archive-cut bridge card when the live issue is only which paper-facing archive slice should travel on request.',
        'referee_followup_packaging': 'Stop at the maintained review-anchor bridge card when the live issue is only the first sufficient referee follow-up package after that archive cut.',
        'source_only_request_promise_and_notice': 'Stop at the maintained first source-only owner-bucket bridge card when the live issue is only what source-only promise and visible notice family were emitted.',
        'bounded_response_packet_and_reuse': 'Stop at the maintained packetization bridge card when the live issue is only which bounded response packet travels and how it may be reused.',
        'visible_refresh_notice_choice': 'Stop at the maintained visible-refresh bridge card when the live issue is only which refresh sentence/family may be surfaced.',
        'successor_refresh_response_packet_and_closure': 'Stop at the maintained successor-closure bridge card when the live issue is only which successor-facing packet closes the refreshed branch.'
    }
    bridge_cut_reopen_artifact_map = {entry['task_key']: 'example_question_routes.json' for entry in minimal_bridge_cuts}
    bridge_cut_reopen_rule_map = {
        'mechanism_justification': 'Reopen to example_question_routes.json only if the live issue ceases to be theorem provenance and becomes receipt, replay, release, or later handoff routing.',
        'public_claim_identification': 'Reopen to example_question_routes.json only if the live issue ceases to be receipt placement and becomes replay, release, or later handoff routing.',
        'replay_verification': 'Reopen to example_question_routes.json only if the live issue ceases to be replay and becomes release evolution or later handoff routing.',
        'release_evolution_status': 'Reopen to example_question_routes.json only if the live issue ceases to be release-stage evolution and becomes the exact paper-facing archive cut or later handoff routing.',
        'answer_side_archive_cut': 'Reopen to example_question_routes.json only if the live issue ceases to be the archive cut itself and becomes one concrete answer-side follow-up or source-only routing question.',
        'referee_followup_packaging': 'Reopen to example_question_routes.json only if the live issue ceases to be the first sufficient referee package and becomes a source-only request or successor-refresh routing question.',
        'source_only_request_promise_and_notice': 'Reopen to example_question_routes.json only if one follow-up class is fixed and the live issue becomes the exact bounded response packet chain rather than the first request/notice bucket.',
        'bounded_response_packet_and_reuse': 'Reopen to example_question_routes.json only if the live issue ceases to be bounded packetization/reuse and becomes visible refresh-family choice.',
        'visible_refresh_notice_choice': 'Reopen to example_question_routes.json only if the live issue ceases to be visible refresh-family choice and becomes a successor-facing packet or closure question.',
        'successor_refresh_response_packet_and_closure': 'Reopen to example_question_routes.json only if the shipped follow-up taxonomy itself changes or the exact reopened owner becomes live.'
    }
    for entry in minimal_bridge_cuts:
        entry.update(stop_rule_map[entry['task_key']])
        entry['bridge_cut_sentence_normal_form'] = bridge_cut_sentence_map[entry['task_key']]
        entry['bridge_cut_reopen_artifact'] = bridge_cut_reopen_artifact_map[entry['task_key']]
        entry['bridge_cut_reopen_rule'] = bridge_cut_reopen_rule_map[entry['task_key']]
    stable_bridge_ladder = [
        {
            'position': index + 1,
            'task_key': entry['task_key'],
            'spine_segment': entry['spine_segment'],
            'label': {
                'mathematical_root': 'theorem_root',
                'receipt_anchor': 'receipt_anchor',
                'replay_anchor': 'replay_anchor',
                'release_anchor': 'release_anchor',
                'disclosure_packet_anchor': 'disclosure_packet_anchor',
                'review_anchor': 'review_anchor',
            }[entry['spine_segment']],
            'canonical_owner': entry['canonical_owner'],
            'artifact': entry['artifact'],
            'question': entry['question'],
            'stop_when': entry['stop_when'],
            'widen_only_if': entry['widen_only_if'],
            'why': entry['why'],
        }
        for index, entry in enumerate(minimal_bridge_cuts)
        if entry.get('stop_kind') == 'series_spine_segment'
    ]

    widening_transitions = {
        'mechanism_justification': ['public_claim_identification'],
        'public_claim_identification': ['replay_verification'],
        'replay_verification': ['release_evolution_status'],
        'release_evolution_status': ['answer_side_archive_cut'],
        'answer_side_archive_cut': ['referee_followup_packaging', 'source_only_request_promise_and_notice'],
        'referee_followup_packaging': ['source_only_request_promise_and_notice'],
        'source_only_request_promise_and_notice': ['bounded_response_packet_and_reuse'],
        'bounded_response_packet_and_reuse': ['visible_refresh_notice_choice'],
        'visible_refresh_notice_choice': ['successor_refresh_response_packet_and_closure'],
        'successor_refresh_response_packet_and_closure': [],
    }

    source_only_owner_buckets = [
        {
            'bucket_key': 'paper_level_request_contracts_and_notice_choice',
            'note_range': 'Synthesis~56--63',
            'first_question': 'What exactly was promised to readers, and what visible status/notice family was emitted?',
            'artifacts': [
                'example_public_request_contracts.json',
                'example_requestable_evidence_classes.json',
                'example_request_fulfillment_certificates.json',
                'example_public_request_status_envelope.json',
                'example_public_request_carryforward_envelope.json',
                'example_public_request_notice.json',
                'example_public_request_notice_normal_forms.json',
                'example_public_request_notice_selections.json'
            ],
            'bucket_sentence_normal_form': 'After leaving the answer-side archive cut, stop first at the source-only owner bucket paper_level_request_contracts_and_notice_choice (Synthesis~56--63).',
            'route_local_reopen_artifact': 'example_question_routes.json',
            'route_local_first_rung_owner': 'Synthesis~56',
            'route_local_first_rung_artifact': 'example_public_request_contracts.json',
            'route_local_reopen_rule': 'If the bucket label is too coarse for the live question, reopen example_question_routes.json and stop at the first sufficient ladder rung that still sits inside paper_level_request_contracts_and_notice_choice before widening further.',
            'why': 'The exact paper-level request-contract / evidence-class / fulfillment-certificate / status-envelope / carryforward-envelope / notice / canonical-notice-family / notice-normal-form / notice-selection chain before any follow-up class is fixed.'
        },
        {
            'bucket_key': 'notice_keyed_response_packetization',
            'note_range': 'Synthesis~64--67',
            'first_question': 'Once one follow-up class is fixed, which bounded handoff slice travels and how may it be reused?',
            'artifacts': [
                'example_public_request_response_menus.json',
                'example_public_request_response_packets.json',
                'example_public_request_response_packet_carryforward_profiles.json',
                'example_public_request_response_packet_delta_ledgers.json'
            ],
            'bucket_sentence_normal_form': 'After one follow-up class is fixed, stop first at the source-only owner bucket notice_keyed_response_packetization (Synthesis~64--67).',
            'route_local_reopen_artifact': 'example_question_routes.json',
            'route_local_first_rung_owner': 'Synthesis~64',
            'route_local_first_rung_artifact': 'example_public_request_response_menus.json',
            'route_local_reopen_rule': 'If the bucket label is too coarse for the live question, reopen example_question_routes.json and stop at the first sufficient ladder rung that still sits inside notice_keyed_response_packetization before widening further.',
            'why': 'The exact source-only response-menu / request-class-owner / response-packet / packet-scope / packet-family-basis / packet-support-surface / packet-manifest-cut / packet-inventory-cut / packet-carryforward-profile / packet-delta-ledger chain once one notice-keyed follow-up class is fixed.'
        },
        {
            'bucket_key': 'visible_refresh_notice_choice',
            'note_range': 'Synthesis~68--70',
            'first_question': 'If that reused packet survives the successor cut, what visible reissue sentence/family/selection is licensed?',
            'artifacts': [
                'example_public_request_response_packet_refresh_notices.json',
                'example_public_request_response_packet_refresh_notice_normal_forms.json',
                'example_public_request_response_packet_refresh_notice_selections.json'
            ],
            'bucket_sentence_normal_form': 'If packet reuse is already fixed but the visible reissue wording is still the live question, stop first at the source-only owner bucket visible_refresh_notice_choice (Synthesis~68--70).',
            'route_local_reopen_artifact': 'example_question_routes.json',
            'route_local_first_rung_owner': 'Synthesis~68',
            'route_local_first_rung_artifact': 'example_public_request_response_packet_refresh_notices.json',
            'route_local_reopen_rule': 'If the bucket label is too coarse for the live question, reopen example_question_routes.json and stop at the first sufficient ladder rung that still sits inside visible_refresh_notice_choice before widening further.',
            'why': 'The exact visible refresh-notice / canonical-refresh-family / refresh-normal-form / refresh-selection chain for a reused packet, still before any successor-facing follow-up choice is fixed.'
        },
        {
            'bucket_key': 'successor_refresh_response_packetization_and_closure',
            'note_range': 'Synthesis~71--73',
            'first_question': 'After one concrete follow-up about that refreshed visible sentence, which successor-facing packet closes the branch?',
            'artifacts': [
                'example_public_request_response_packet_refresh_response_menus.json',
                'example_public_request_response_packet_refresh_response_packets.json',
                'example_public_request_response_packet_refresh_response_packet_closure_verdicts.json'
            ],
            'bucket_sentence_normal_form': 'Once one refreshed visible-sentence follow-up is fixed, stop first at the source-only owner bucket successor_refresh_response_packetization_and_closure (Synthesis~71--73).',
            'route_local_reopen_artifact': 'example_question_routes.json',
            'route_local_first_rung_owner': 'Synthesis~71',
            'route_local_first_rung_artifact': 'example_public_request_response_packet_refresh_response_menus.json',
            'route_local_reopen_rule': 'If the bucket label is too coarse for the live question, reopen example_question_routes.json and stop at the first sufficient ladder rung that still sits inside successor_refresh_response_packetization_and_closure before widening further.',
            'why': 'The exact successor-facing refresh-response-menu / successor-followup-owner / exact bounded successor packet / validation-posture / closure-verdict / closure-scope chain for the refreshed visible sentence branch.'
        }
    ]
    bucket_rule_map = {
        'paper_level_request_contracts_and_notice_choice': stop_rule_map['source_only_request_promise_and_notice'],
        'notice_keyed_response_packetization': stop_rule_map['bounded_response_packet_and_reuse'],
        'visible_refresh_notice_choice': stop_rule_map['visible_refresh_notice_choice'],
        'successor_refresh_response_packetization_and_closure': stop_rule_map['successor_refresh_response_packet_and_closure'],
    }
    for bucket in source_only_owner_buckets:
        bucket.update(bucket_rule_map[bucket['bucket_key']])

    source_only_request_ladder = [
        {
            'position': 1,
            'task_key': 'request_contract',
            'bucket_key': 'paper_level_request_contracts_and_notice_choice',
            'label': 'public_request_contract',
            'canonical_owner': 'Synthesis~56',
            'note_range': 'Synthesis~56',
            'artifact': 'example_public_request_contracts.json',
            'question': 'What exact paper-level source-only promise does the public sentence make?',
            'stop_when': 'The task is the exact paper-level source-only promise and its maintained packet/menu/validator cut.',
            'widen_only_if': 'Widen only if the question becomes omitted-support family naming, fulfillment/completion, or visible notice realization.',
            'why': 'The public request contract is the first sufficient owner for what the paper promised and which maintained cut stands behind that promise.'
        },
        {
            'position': 2,
            'task_key': 'requestable_evidence_class_typing',
            'bucket_key': 'paper_level_request_contracts_and_notice_choice',
            'label': 'requestable_evidence_classes',
            'canonical_owner': 'Synthesis~57',
            'note_range': 'Synthesis~57',
            'artifact': 'example_requestable_evidence_classes.json',
            'question': 'Which omitted-support family names does that promise actually cover?',
            'stop_when': 'The task is naming or typing the omitted-support families behind the paper-level promise.',
            'widen_only_if': 'Widen only if the question becomes whether one such family has been fully supplied or how it is compressed publicly.',
            'why': 'Evidence classes stabilize the support-family names without re-owning packet cuts or status compression.'
        },
        {
            'position': 3,
            'task_key': 'request_fulfillment',
            'bucket_key': 'paper_level_request_contracts_and_notice_choice',
            'label': 'request_fulfillment_certificates',
            'canonical_owner': 'Synthesis~58',
            'note_range': 'Synthesis~58',
            'artifact': 'example_request_fulfillment_certificates.json',
            'question': 'Has one promised omitted-support family actually been fully supplied?',
            'stop_when': 'The task is whether a promised omitted-support family has been fully satisfied.',
            'widen_only_if': 'Widen only if the question becomes paper-level status compression or cross-release carryforward.',
            'why': 'Fulfillment certificates are the first sufficient owner for family-scoped completion rather than mere family naming.'
        },
        {
            'position': 4,
            'task_key': 'request_status',
            'bucket_key': 'paper_level_request_contracts_and_notice_choice',
            'label': 'public_request_status_envelope',
            'canonical_owner': 'Synthesis~59',
            'note_range': 'Synthesis~59',
            'artifact': 'example_public_request_status_envelope.json',
            'question': 'What is the within-release paper-level public status of the overall source-only promise?',
            'stop_when': 'The task is the within-release paper-level status token for the overall source-only promise.',
            'widen_only_if': 'Widen only if the question becomes successor carryforward or visible notice wording.',
            'why': 'The status envelope compresses fulfilled families to one paper-level public token without re-owning the certificates beneath it.'
        },
        {
            'position': 5,
            'task_key': 'request_carryforward',
            'bucket_key': 'paper_level_request_contracts_and_notice_choice',
            'label': 'public_request_carryforward_envelope',
            'canonical_owner': 'Synthesis~60',
            'note_range': 'Synthesis~60',
            'artifact': 'example_public_request_carryforward_envelope.json',
            'question': 'Does that paper-level source-only request status persist, advance, or reopen across the successor release?',
            'stop_when': 'The task is cross-release carryforward of the paper-level source-only request status token.',
            'widen_only_if': 'Widen only if the question becomes the exact outward-facing notice sentence or canonical family choice.',
            'why': 'Carryforward is the first sufficient owner for successor persistence or reopening of the paper-level request promise.'
        },
        {
            'position': 6,
            'task_key': 'request_notice',
            'bucket_key': 'paper_level_request_contracts_and_notice_choice',
            'label': 'public_request_notice',
            'canonical_owner': 'Synthesis~61',
            'note_range': 'Synthesis~61',
            'artifact': 'example_public_request_notice.json',
            'question': 'What exact outward-facing source-only notice sentence and pointer order were emitted?',
            'stop_when': 'The task is the exact outward-facing source-only notice sentence and its reader-pointer order.',
            'widen_only_if': 'Widen only if the question becomes the canonical notice family or slot structure behind that sentence.',
            'why': 'The notice is the first sufficient owner for what readers actually saw at paper level.'
        },
        {
            'position': 7,
            'task_key': 'request_notice_normal_form',
            'bucket_key': 'paper_level_request_contracts_and_notice_choice',
            'label': 'public_request_notice_normal_form',
            'canonical_owner': 'Synthesis~62',
            'note_range': 'Synthesis~62',
            'artifact': 'example_public_request_notice_normal_forms.json',
            'question': 'Which canonical notice family and slot structure sits behind that emitted source-only notice?',
            'stop_when': 'The task is the canonical notice family and slot structure behind the emitted source-only notice.',
            'widen_only_if': 'Widen only if the question becomes which canonical family was selected for this release.',
            'why': 'Normal forms own the reusable notice family rather than the emitted sentence instance.'
        },
        {
            'position': 8,
            'task_key': 'request_notice_selection',
            'bucket_key': 'paper_level_request_contracts_and_notice_choice',
            'label': 'public_request_notice_selection',
            'canonical_owner': 'Synthesis~63',
            'note_range': 'Synthesis~63',
            'artifact': 'example_public_request_notice_selections.json',
            'question': 'Which canonical source-only notice family was actually selected for the current release?',
            'stop_when': 'The task is which canonical source-only notice family was actually selected for this release.',
            'widen_only_if': 'Widen only if one follow-up class is fixed and the question becomes the exact response-menu / request-class-owner / response-packet / packet-scope / packet-family-basis / packet-support-surface / packet-manifest-cut / packet-inventory-cut / packet-carryforward-profile / packet-delta-ledger chain.',
            'why': 'The selection ledger is the last paper-level source-only owner before one concrete follow-up class is fixed.'
        },
        {
            'position': 9,
            'task_key': 'response_menu',
            'bucket_key': 'notice_keyed_response_packetization',
            'label': 'public_request_response_menu',
            'canonical_owner': 'Synthesis~64',
            'note_range': 'Synthesis~64',
            'artifact': 'example_public_request_response_menus.json',
            'question': 'Once one follow-up class is fixed, which maintained owner is the smallest sufficient handoff?',
            'stop_when': 'The task is the notice-keyed follow-up owner choice after one concrete follow-up class is fixed.',
            'widen_only_if': 'Widen only if the question becomes the exact bounded packet slice that should travel or the packet-carryforward-profile / packet-delta-ledger chain beneath it.',
            'why': 'The response menu is the first sufficient owner once the question leaves paper-level notice choice and fixes a follow-up class.'
        },
        {
            'position': 10,
            'task_key': 'response_packet',
            'bucket_key': 'notice_keyed_response_packetization',
            'label': 'public_request_response_packet',
            'canonical_owner': 'Synthesis~65',
            'note_range': 'Synthesis~65',
            'artifact': 'example_public_request_response_packets.json',
            'question': 'What exact bounded source-only handoff slice should travel for that follow-up class?',
            'stop_when': 'The task is the exact bounded response packet that should travel for the selected follow-up class.',
            'widen_only_if': 'Widen only if the question becomes whether that exact packet may be reused or which fields refresh.',
            'why': 'The response packet is the first sufficient owner for the concrete bounded handoff slice itself.'
        },
        {
            'position': 11,
            'task_key': 'response_packet_carryforward',
            'bucket_key': 'notice_keyed_response_packetization',
            'label': 'public_request_response_packet_carryforward',
            'canonical_owner': 'Synthesis~66',
            'note_range': 'Synthesis~66',
            'artifact': 'example_public_request_response_packet_carryforward_profiles.json',
            'question': 'May that exact bounded response packet be reused unchanged, refreshed, or must it reopen in the successor release?',
            'stop_when': 'The task is whether an already-cut bounded response packet survives, refreshes, or reopens across the successor release.',
            'widen_only_if': 'Widen only if the question becomes which packet-local field families refresh inside a reusable packet.',
            'why': 'The carryforward profile is the first sufficient owner for packet reuse posture across releases.'
        },
        {
            'position': 12,
            'task_key': 'response_packet_delta',
            'bucket_key': 'notice_keyed_response_packetization',
            'label': 'public_request_response_packet_delta',
            'canonical_owner': 'Synthesis~67',
            'note_range': 'Synthesis~67',
            'artifact': 'example_public_request_response_packet_delta_ledgers.json',
            'question': 'If a response packet is reused, what exact packet-local field families refresh?',
            'stop_when': 'The task is the exact packet-local refresh delta for a reusable bounded response packet.',
            'widen_only_if': 'Widen only if the question becomes the visible successor-facing refresh sentence or family built on that delta.',
            'why': 'The delta ledger is the last notice-keyed packet owner before visible refresh wording begins.'
        },
        {
            'position': 13,
            'task_key': 'refresh_notice',
            'bucket_key': 'visible_refresh_notice_choice',
            'label': 'public_request_response_packet_refresh_notice',
            'canonical_owner': 'Synthesis~68',
            'note_range': 'Synthesis~68',
            'artifact': 'example_public_request_response_packet_refresh_notices.json',
            'question': 'What exact visible reissue sentence may be surfaced for a reusable response packet?',
            'stop_when': 'The task is the exact visible refresh sentence for a reusable bounded response packet.',
            'widen_only_if': 'Widen only if the question becomes the canonical visible refresh family or the selection among such families.',
            'why': 'The refresh notice is the first sufficient owner for what readers may visibly see when a packet is reissued.'
        },
        {
            'position': 14,
            'task_key': 'refresh_notice_normal_form',
            'bucket_key': 'visible_refresh_notice_choice',
            'label': 'public_request_response_packet_refresh_notice_normal_form',
            'canonical_owner': 'Synthesis~69',
            'note_range': 'Synthesis~69',
            'artifact': 'example_public_request_response_packet_refresh_notice_normal_forms.json',
            'question': 'Which canonical visible reissue wrapper family sits behind that emitted refresh sentence?',
            'stop_when': 'The task is the canonical visible refresh wrapper family and slot structure.',
            'widen_only_if': 'Widen only if the question becomes which visible refresh family was selected for this packet.',
            'why': 'Normal forms own the reusable visible reissue family rather than the emitted sentence instance.'
        },
        {
            'position': 15,
            'task_key': 'refresh_notice_selection',
            'bucket_key': 'visible_refresh_notice_choice',
            'label': 'public_request_response_packet_refresh_notice_selection',
            'canonical_owner': 'Synthesis~70',
            'note_range': 'Synthesis~70',
            'artifact': 'example_public_request_response_packet_refresh_notice_selections.json',
            'question': 'Which canonical visible refresh family was selected for the current reusable packet?',
            'stop_when': 'The task is which canonical visible refresh family was selected for the current reusable packet.',
            'widen_only_if': 'Widen only if the question becomes a successor-facing follow-up choice or closure question about that visible sentence.',
            'why': 'The selection ledger is the last visible-refresh owner before a successor-facing follow-up is fixed.'
        },
        {
            'position': 16,
            'task_key': 'refresh_response_menu',
            'bucket_key': 'successor_refresh_response_packetization_and_closure',
            'label': 'public_request_response_packet_refresh_response_menu',
            'canonical_owner': 'Synthesis~71',
            'note_range': 'Synthesis~71',
            'artifact': 'example_public_request_response_packet_refresh_response_menus.json',
            'question': 'After one concrete follow-up about the visible refresh sentence, which successor-facing owner is first sufficient?',
            'stop_when': 'The task is the successor-facing follow-up owner choice after one concrete question about a visible refresh sentence.',
            'widen_only_if': 'Widen only if the question becomes the exact successor-facing packet cut or whether that branch is already closed.',
            'why': 'The successor-facing response menu is the first sufficient owner once one visible-refresh follow-up class is fixed.'
        },
        {
            'position': 17,
            'task_key': 'refresh_response_packet',
            'bucket_key': 'successor_refresh_response_packetization_and_closure',
            'label': 'public_request_response_packet_refresh_response_packet',
            'canonical_owner': 'Synthesis~72',
            'note_range': 'Synthesis~72',
            'artifact': 'example_public_request_response_packet_refresh_response_packets.json',
            'question': 'What exact successor-facing bounded packet should travel for that visible-refresh follow-up?',
            'stop_when': 'The task is the exact successor-facing bounded packet cut for the selected visible-refresh follow-up.',
            'widen_only_if': 'Widen only if the question becomes whether that refreshed visible branch is already closed under the shipped taxonomy.',
            'why': 'The successor-facing response packet is the first sufficient owner for the concrete refreshed handoff slice itself.'
        },
        {
            'position': 18,
            'task_key': 'refresh_response_packet_closure',
            'bucket_key': 'successor_refresh_response_packetization_and_closure',
            'label': 'public_request_response_packet_refresh_response_packet_closure',
            'canonical_owner': 'Synthesis~73',
            'note_range': 'Synthesis~73',
            'artifact': 'example_public_request_response_packet_refresh_response_packet_closure_verdicts.json',
            'question': 'Does that successor-facing refresh-response packet already close the branch, and what would reopen it?',
            'stop_when': 'The task is whether the successor-facing refresh-response packet already closes the branch and which local triggers would reopen it.',
            'widen_only_if': 'Do not widen unless the shipped follow-up taxonomy itself changes or a listed reopen trigger fires.',
            'why': 'The closure verdict is the capstone owner for terminal-stop posture, reopen triggers, and reopen-owner recovery on the visible refresh branch.'
        },
    ]

    source_only_request_ladder_sentence_map = {
        'request_contract': 'If the live source-only question is the paper-level promise itself, stop at the request-ladder rung public_request_contract (Synthesis~56).',
        'requestable_evidence_class_typing': 'If the live source-only question is which omitted-support family names the paper-level promise actually covers, stop at the request-ladder rung requestable_evidence_classes (Synthesis~57).',
        'request_fulfillment': 'If the live source-only question is whether one promised omitted-support family has actually been fully supplied, stop at the request-ladder rung request_fulfillment_certificates (Synthesis~58).',
        'request_status': 'If the live source-only question is the within-release public status token for that paper-level promise, stop at the request-ladder rung public_request_status_envelope (Synthesis~59).',
        'request_carryforward': 'If the live source-only question is how that paper-level status carries across releases, stop at the request-ladder rung public_request_carryforward_envelope (Synthesis~60).',
        'request_notice': 'If the live source-only question is the outward-facing source-only notice sentence itself, stop at the request-ladder rung public_request_notice (Synthesis~61).',
        'request_notice_normal_form': 'If the live source-only question is which canonical notice family sits behind that outward-facing source-only sentence, stop at the request-ladder rung public_request_notice_normal_form (Synthesis~62).',
        'request_notice_selection': 'If the live source-only question is which canonical source-only notice family was selected for this release, stop at the request-ladder rung public_request_notice_selection (Synthesis~63).',
        'response_menu': 'Once one follow-up class is fixed, stop at the request-ladder rung public_request_response_menu (Synthesis~64) for the smallest sufficient omitted-support handoff owner.',
        'response_packet': 'Once one follow-up class is fixed and the live issue is the bounded omitted-support slice itself, stop at the request-ladder rung public_request_response_packet (Synthesis~65).',
        'response_packet_carryforward': 'If the live source-only question is whether that exact bounded response packet survives, refreshes, or reopens across the successor release, stop at the request-ladder rung public_request_response_packet_carryforward (Synthesis~66).',
        'response_packet_delta': 'If the live source-only question is which packet-local field families refresh inside a reusable bounded response packet, stop at the request-ladder rung public_request_response_packet_delta (Synthesis~67).',
        'refresh_notice': 'If the live source-only question is the exact visible reissue sentence for a reusable response packet, stop at the request-ladder rung public_request_response_packet_refresh_notice (Synthesis~68).',
        'refresh_notice_normal_form': 'If the live source-only question is which canonical visible-refresh wrapper family sits behind that emitted reissue sentence, stop at the request-ladder rung public_request_response_packet_refresh_notice_normal_form (Synthesis~69).',
        'refresh_notice_selection': 'If the live source-only question is which canonical visible-refresh family was selected for the current reusable packet, stop at the request-ladder rung public_request_response_packet_refresh_notice_selection (Synthesis~70).',
        'refresh_response_menu': 'After one concrete follow-up about the visible refresh sentence is fixed, stop at the request-ladder rung public_request_response_packet_refresh_response_menu (Synthesis~71).',
        'refresh_response_packet': 'If the live source-only question is the exact successor-facing bounded packet for that visible-refresh follow-up, stop at the request-ladder rung public_request_response_packet_refresh_response_packet (Synthesis~72).',
        'refresh_response_packet_closure': 'If the live source-only question is whether that successor-facing refresh-response packet already closes the branch and what would reopen it, stop at the request-ladder rung public_request_response_packet_refresh_response_packet_closure (Synthesis~73).',
    }
    for rung in source_only_request_ladder:
        rung['rung_sentence_normal_form'] = source_only_request_ladder_sentence_map[rung['task_key']]
        rung['route_local_reopen_artifact'] = 'example_question_routes.json'
        rung['route_local_reopen_rule'] = f"If the rung label is still too coarse for the live question, reopen example_question_routes.json and stop at the first sufficient audience/question route that still instantiates {rung['task_key']} before widening further."

    review_menu_index = {entry['answer_review_menu_key']: entry for entry in answer_review_menus['answer_review_menus']}
    public_request_contract_entry = public_request_contracts['public_request_contracts'][0]
    request_fulfillment_certificate_keys = [entry['request_fulfillment_certificate_key'] for entry in request_fulfillment_certificates['request_fulfillment_certificates']]
    family_completion_map = {entry['family_key']: entry['completion_verdict'] for entry in request_fulfillment_certificates['request_fulfillment_certificates']}
    source_only_family_completion_mode_map = {entry['family_key']: entry['completion_verdict_mode'] for entry in request_fulfillment_certificates['request_fulfillment_certificates']}
    source_only_public_anchor_family_mode_map = {entry['family_key']: entry['public_anchor_family_vocabulary_mode'] for entry in public_request_contracts['public_request_contracts'][0]['public_anchor_families']}
    source_only_evidence_class_mode_map = {entry['evidence_class_key']: entry['evidence_class_vocabulary_mode'] for entry in requestable_evidence_classes['evidence_classes']}
    status_entry = public_request_status_envelope['public_request_status_envelopes'][0]
    carryforward_entry = public_request_carryforward_envelope['public_request_carryforward_envelopes'][0]
    release_obligation_profile_id = obligation_profile['obligation_profile_id']
    release_closure_ledger_id = closure_ledger['closure_ledger_id']
    publication_closure_verdict_id = publication_closure_verdict['closure_verdict_id']
    publication_closure_status = publication_closure_verdict['closure_status']
    successor_status_envelope_id = successor_status_envelope['status_envelope_id']
    successor_public_status_token = successor_status_envelope['public_status']
    successor_lineage_notice_id = lineage['notice_id']
    source_only_status_token_mode_map = {entry['public_request_status_envelope_key']: entry['public_request_status_token_mode'] for entry in public_request_status_envelope['public_request_status_envelopes']}
    source_only_carryforward_token_mode_map = {entry['public_request_carryforward_envelope_key']: entry['carryforward_token_mode'] for entry in public_request_carryforward_envelope['public_request_carryforward_envelopes']}
    source_only_notice_key_map = {entry['notice_kind']: entry['public_request_notice_key'] for entry in public_request_notice['public_request_notices']}
    source_only_notice_normal_form_map = {entry['notice_kind']: entry['public_request_notice_normal_form_key'] for entry in public_request_notice_normal_forms['public_request_notice_normal_forms']}
    source_only_notice_selection_keys = {entry['notice_kind']: entry['public_request_notice_selection_key'] for entry in public_request_notice_selections['public_request_notice_selections']}
    source_only_response_menu_keys = {entry['notice_kind']: entry['public_request_response_menu_key'] for entry in public_request_response_menus['public_request_response_menus']}
    source_only_response_menu_followup_class_mode_map = {entry['notice_kind']: entry['followup_class_vocabulary_mode'] for entry in public_request_response_menus['public_request_response_menus']}
    source_only_request_class_handoff_map = {
        entry['notice_kind']: {response_entry.get('request_class'): response_entry.get('selected_entry') for response_entry in entry.get('response_entries', [])}
        for entry in public_request_response_menus['public_request_response_menus']
    }
    source_only_request_class_owner_map = {
        entry['notice_kind']: {
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
        for entry in public_request_response_menus['public_request_response_menus']
    }
    source_only_response_packet_map = {}
    source_only_response_packet_scope_mode_map = {}
    source_only_response_packet_family_basis_map = {}
    source_only_response_packet_support_surface_map = {}
    source_only_response_packet_manifest_cut_map = {}
    source_only_response_packet_inventory_cut_map = {}
    for packet in public_request_response_packets['public_request_response_packets']:
        source_only_response_packet_map.setdefault(packet['notice_kind'], {})[packet['request_class']] = packet['public_request_response_packet_key']
        source_only_response_packet_scope_mode_map.setdefault(packet['notice_kind'], {})[packet['request_class']] = packet['packet_scope_mode']
        source_only_response_packet_family_basis_map.setdefault(packet['notice_kind'], {})[packet['request_class']] = extract_packet_family_basis(packet)
        source_only_response_packet_support_surface_map.setdefault(packet['notice_kind'], {})[packet['request_class']] = extract_packet_support_surface(packet)
        source_only_response_packet_manifest_cut_map.setdefault(packet['notice_kind'], {})[packet['request_class']] = extract_packet_manifest_cut(packet, support_manifest_index, support_manifest['manifest_id'])
        source_only_response_packet_inventory_cut_map.setdefault(packet['notice_kind'], {})[packet['request_class']] = extract_packet_inventory_cut(packet, inventory_index, inventory['inventory_id'])
    source_only_response_packet_carryforward_profile_map = {}
    source_only_response_packet_reuse_status_map = {}
    source_only_response_packet_refresh_family_mode_map = {}
    for profile in public_request_response_packet_carryforward_profiles['public_request_response_packet_carryforward_profiles']:
        source_only_response_packet_carryforward_profile_map.setdefault(profile['notice_kind'], {})[profile['request_class']] = profile['public_request_response_packet_carryforward_profile_key']
        source_only_response_packet_reuse_status_map.setdefault(profile['notice_kind'], {})[profile['request_class']] = profile['packet_maintenance_posture']['current_status']
        source_only_response_packet_refresh_family_mode_map.setdefault(profile['notice_kind'], {})[profile['request_class']] = profile['refreshable_field_family_mode']
    source_only_response_packet_delta_map = {}
    source_only_response_packet_delta_family_mode_map = {}
    for delta in public_request_response_packet_delta_ledgers['public_request_response_packet_delta_ledgers']:
        source_only_response_packet_delta_map.setdefault(delta['notice_kind'], {})[delta['request_class']] = delta['public_request_response_packet_delta_key']
        source_only_response_packet_delta_family_mode_map.setdefault(delta['notice_kind'], {})[delta['request_class']] = delta['changed_field_family_mode']
    source_only_refresh_notice_map = {}
    for notice in public_request_response_packet_refresh_notices['public_request_response_packet_refresh_notices']:
        source_only_refresh_notice_map.setdefault(notice['notice_kind'], {})[notice['request_class']] = notice['public_request_response_packet_refresh_notice_key']
    source_only_refresh_notice_normal_form_map = {}
    for normal_form in public_request_response_packet_refresh_notice_normal_forms['public_request_response_packet_refresh_notice_normal_forms']:
        source_only_refresh_notice_normal_form_map.setdefault(normal_form['notice_kind'], {})[normal_form['request_class']] = normal_form['public_request_response_packet_refresh_notice_normal_form_key']
    source_only_refresh_notice_selection_map = {}
    for selection in public_request_response_packet_refresh_notice_selections['public_request_response_packet_refresh_notice_selections']:
        source_only_refresh_notice_selection_map.setdefault(selection['notice_kind'], {})[selection['request_class']] = selection['public_request_response_packet_refresh_notice_selection_key']
    source_only_refresh_response_menu_map = {}
    for menu in public_request_response_packet_refresh_response_menus['public_request_response_packet_refresh_response_menus']:
        source_only_refresh_response_menu_map.setdefault(menu['notice_kind'], {})[menu['request_class']] = menu['public_request_response_packet_refresh_response_menu_key']
    source_only_refresh_followup_handoff_map = {}
    source_only_refresh_followup_owner_map = {}
    for menu in public_request_response_packet_refresh_response_menus['public_request_response_packet_refresh_response_menus']:
        source_only_refresh_followup_handoff_map.setdefault(menu['notice_kind'], {})[menu['request_class']] = {
            response_entry.get('request_class'): response_entry.get('selected_entry')
            for response_entry in menu.get('response_entries', [])
        }
        source_only_refresh_followup_owner_map.setdefault(menu['notice_kind'], {})[menu['request_class']] = {
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
    source_only_refresh_response_packet_map = {}
    source_only_refresh_response_packet_family_basis_map = {}
    source_only_refresh_response_packet_support_surface_map = {}
    source_only_refresh_response_packet_manifest_cut_map = {}
    source_only_refresh_response_packet_inventory_cut_map = {}
    source_only_refresh_response_packet_validation_mode_map = {}
    for packet in public_request_response_packet_refresh_response_packets['public_request_response_packet_refresh_response_packets']:
        source_only_refresh_response_packet_map.setdefault(packet['notice_kind'], {}).setdefault(packet['request_class'], {})[packet['successor_followup_class']] = packet['public_request_response_packet_refresh_response_packet_key']
        source_only_refresh_response_packet_family_basis_map.setdefault(packet['notice_kind'], {}).setdefault(packet['request_class'], {})[packet['successor_followup_class']] = extract_packet_family_basis(packet)
        source_only_refresh_response_packet_support_surface_map.setdefault(packet['notice_kind'], {}).setdefault(packet['request_class'], {})[packet['successor_followup_class']] = extract_packet_support_surface(packet)
        source_only_refresh_response_packet_manifest_cut_map.setdefault(packet['notice_kind'], {}).setdefault(packet['request_class'], {})[packet['successor_followup_class']] = extract_packet_manifest_cut(packet, support_manifest_index, support_manifest['manifest_id'])
        source_only_refresh_response_packet_inventory_cut_map.setdefault(packet['notice_kind'], {}).setdefault(packet['request_class'], {})[packet['successor_followup_class']] = extract_packet_inventory_cut(packet, inventory_index, inventory['inventory_id'])
        source_only_refresh_response_packet_validation_mode_map.setdefault(packet['notice_kind'], {}).setdefault(packet['request_class'], {})[packet['successor_followup_class']] = packet['validation_capsule_mode']
    source_only_refresh_response_packet_closure_map = {}
    source_only_refresh_response_packet_closure_status_map = {}
    source_only_refresh_response_packet_closure_scope_map = {}
    source_only_refresh_response_packet_reopen_trigger_map = {}
    source_only_refresh_response_packet_reopen_owner_map = {}
    for verdict in public_request_response_packet_refresh_response_packet_closure_verdicts['public_request_response_packet_refresh_response_packet_closure_verdicts']:
        source_only_refresh_response_packet_closure_map.setdefault(verdict['notice_kind'], {}).setdefault(verdict['request_class'], {})[verdict['successor_followup_class']] = verdict['public_request_response_packet_refresh_response_packet_closure_verdict_key']
        source_only_refresh_response_packet_closure_status_map.setdefault(verdict['notice_kind'], {}).setdefault(verdict['request_class'], {})[verdict['successor_followup_class']] = verdict['closure_status']
        source_only_refresh_response_packet_closure_scope_map.setdefault(verdict['notice_kind'], {}).setdefault(verdict['request_class'], {})[verdict['successor_followup_class']] = verdict['closure_basis_scope']
        source_only_refresh_response_packet_reopen_trigger_map.setdefault(verdict['notice_kind'], {}).setdefault(verdict['request_class'], {})[verdict['successor_followup_class']] = verdict.get('reopen_trigger_tokens', [])
        source_only_refresh_response_packet_reopen_owner_map.setdefault(verdict['notice_kind'], {}).setdefault(verdict['request_class'], {})[verdict['successor_followup_class']] = verdict.get('reopen_owner_map', {})
    disclosure_packet_support_surface_map = {}
    disclosure_packet_manifest_cut_map = {}
    disclosure_packet_inventory_cut_map = {}
    for packet in answer_disclosure_packets['answer_disclosure_packets']:
        disclosure_packet_support_surface_map[packet['answer_disclosure_packet_key']] = extract_disclosure_packet_support_surface(packet)
        disclosure_packet_manifest_cut_map[packet['answer_disclosure_packet_key']] = extract_disclosure_packet_manifest_cut(packet, support_manifest_index, support_manifest['manifest_id'])
        disclosure_packet_inventory_cut_map[packet['answer_disclosure_packet_key']] = extract_disclosure_packet_inventory_cut(packet, inventory_index, inventory['inventory_id'])
    for answer in answer_spines:
        answer.update({
            'release_obligation_profile_id': release_obligation_profile_id,
            'release_closure_ledger_id': release_closure_ledger_id,
            'publication_closure_verdict_id': publication_closure_verdict_id,
            'publication_closure_status': publication_closure_status,
            'successor_status_envelope_id': successor_status_envelope_id,
            'successor_public_status_token': successor_public_status_token,
            'successor_lineage_notice_id': successor_lineage_notice_id,
            'public_request_contract_key': public_request_contract_entry['public_request_contract_key'],
            'source_only_public_anchor_family_mode_map': source_only_public_anchor_family_mode_map,
            'source_only_request_fulfillment_certificate_keys': request_fulfillment_certificate_keys,
            'source_only_family_completion_map': family_completion_map,
            'source_only_family_completion_mode_map': source_only_family_completion_mode_map,
            'source_only_evidence_class_mode_map': source_only_evidence_class_mode_map,
            'source_only_status_envelope_key': status_entry['public_request_status_envelope_key'],
            'source_only_status_token': status_entry['public_request_status_token'],
            'source_only_status_token_mode_map': source_only_status_token_mode_map,
            'source_only_carryforward_envelope_key': carryforward_entry['public_request_carryforward_envelope_key'],
            'source_only_carryforward_token': carryforward_entry['carryforward_token'],
            'source_only_carryforward_token_mode_map': source_only_carryforward_token_mode_map,
            'source_only_notice_key_map': source_only_notice_key_map,
            'source_only_notice_normal_form_map': source_only_notice_normal_form_map,
            'source_only_notice_selection_keys': source_only_notice_selection_keys,
            'source_only_response_menu_keys': source_only_response_menu_keys,
            'source_only_response_menu_followup_class_mode_map': source_only_response_menu_followup_class_mode_map,
            'source_only_request_class_handoff_map': source_only_request_class_handoff_map,
            'source_only_request_class_owner_map': source_only_request_class_owner_map,
            'source_only_response_packet_map': source_only_response_packet_map,
            'source_only_response_packet_scope_mode_map': source_only_response_packet_scope_mode_map,
            'source_only_response_packet_family_basis_map': source_only_response_packet_family_basis_map,
            'source_only_response_packet_support_surface_map': source_only_response_packet_support_surface_map,
            'source_only_response_packet_manifest_cut_map': source_only_response_packet_manifest_cut_map,
            'source_only_response_packet_inventory_cut_map': source_only_response_packet_inventory_cut_map,
            'source_only_response_packet_carryforward_profile_map': source_only_response_packet_carryforward_profile_map,
            'source_only_response_packet_reuse_status_map': source_only_response_packet_reuse_status_map,
            'source_only_response_packet_refresh_family_mode_map': source_only_response_packet_refresh_family_mode_map,
            'source_only_response_packet_delta_map': source_only_response_packet_delta_map,
            'source_only_response_packet_delta_family_mode_map': source_only_response_packet_delta_family_mode_map,
            'source_only_refresh_notice_map': source_only_refresh_notice_map,
            'source_only_refresh_notice_normal_form_map': source_only_refresh_notice_normal_form_map,
            'source_only_refresh_notice_selection_map': source_only_refresh_notice_selection_map,
            'source_only_refresh_response_menu_map': source_only_refresh_response_menu_map,
            'source_only_refresh_followup_handoff_map': source_only_refresh_followup_handoff_map,
            'source_only_refresh_followup_owner_map': source_only_refresh_followup_owner_map,
            'source_only_refresh_response_packet_map': source_only_refresh_response_packet_map,
            'source_only_refresh_response_packet_family_basis_map': source_only_refresh_response_packet_family_basis_map,
            'source_only_refresh_response_packet_support_surface_map': source_only_refresh_response_packet_support_surface_map,
            'source_only_refresh_response_packet_manifest_cut_map': source_only_refresh_response_packet_manifest_cut_map,
            'source_only_refresh_response_packet_inventory_cut_map': source_only_refresh_response_packet_inventory_cut_map,
            'source_only_refresh_response_packet_validation_mode_map': source_only_refresh_response_packet_validation_mode_map,
            'source_only_refresh_response_packet_closure_map': source_only_refresh_response_packet_closure_map,
            'source_only_refresh_response_packet_closure_status_map': source_only_refresh_response_packet_closure_status_map,
            'source_only_refresh_response_packet_closure_scope_map': source_only_refresh_response_packet_closure_scope_map,
            'source_only_refresh_response_packet_reopen_trigger_map': source_only_refresh_response_packet_reopen_trigger_map,
            'source_only_refresh_response_packet_reopen_owner_map': source_only_refresh_response_packet_reopen_owner_map,
            'source_only_request_ladder': source_only_request_ladder,
            'disclosure_packet_support_surface': disclosure_packet_support_surface_map[answer['disclosure_packet_key']],
            'disclosure_packet_manifest_cut': disclosure_packet_manifest_cut_map[answer['disclosure_packet_key']],
            'disclosure_packet_inventory_cut': disclosure_packet_inventory_cut_map[answer['disclosure_packet_key']],
        })
        answer['why'] = 'One maintained answer bridge from its public anchor through the governing stop profile, emitted answer, sentence lock, inherited brief/expanded/exact/full-audit publication forms, the imported six-class request handoff map, the mirrored answer-review request-class vocabulary posture map, the mirrored answer-escalation-step vocabulary posture map, the mirrored release-stage-vocabulary posture map, the imported six-class request owner map, the exact release-obligation-profile / release-closure-ledger / publication-closure-verdict / successor-status-envelope / successor-lineage-notice key chain together with the imported public-status token it emits, the exact route-side disclosure-packet support-surface / manifest-cut / inventory-cut maps for the answer-side on-request archive slice, the paper-level source-only request contract together with the exact evidence-class key list plus mirrored public-anchor-family / evidence-class vocabulary maps, the imported family completion certificates plus paper-level source-only status/carryforward tokens, the imported source-only notice / canonical-notice-family / notice-selection / response-menu / source-only request-class handoff / owner / exact bounded response-packet / packet-carryforward-profile / packet-family-basis / packet-support-surface / packet-manifest-cut / packet-inventory-cut / packet-delta maps for omitted-support follow-up, the imported successor packet-reuse / packet-family-mode / delta / delta-family-mode / emitted-refresh-notice / canonical-refresh-family / refresh-notice-selection / refresh-response-menu / successor-followup handoff / owner / exact successor-facing packet / packet-family-basis / packet-support-surface / packet-manifest-cut / packet-inventory-cut / validation-posture / exact closure-verdict / closure / closure-scope / reopen-owner maps for the visible refresh branch, and the exact citation-docket / answer-carrier-slot / answer-audit-trail handoff seam, and the exact review menu for that audience/question handoff.'
    question_routes = {
        'question_routes_id': QUESTION_ROUTES_ID,
        'claim_id': compare_report['claim_id'],
        'release_id': compare_report['release_id'],
        'note_version': compare_report['note_version'],
        'series_spine_id': SERIES_SPINE_ID,
        'successor_challenge_answer_review_menus_id': answer_review_menus['challenge_answer_review_menus_id'],
        'successor_challenge_routes_id': routes['challenge_routes_id'],
        'successor_challenge_stop_profiles_id': stop_profiles['challenge_stop_profiles_id'],
        'successor_challenge_branches_id': branches['challenge_branches_id'],
        'requestable_evidence_classes_id': requestable_evidence_classes['requestable_evidence_classes_id'],
        'contract': {
            'generic_question_route_fields': ['route_key', 'question_examples', 'stop_kind', 'spine_segment', 'bucket_key', 'first_stop_owner', 'first_stop_artifact', 'next_route_keys_if_scope_widens', 'why'],
            'audience_question_route_fields': ['route_key', 'audience', 'question_key', 'challenge_route_key', 'stop_profile_key', 'minimal_public_anchor_path', 'sentence_family', 'answer_card_key', 'sentence_lock_key', 'sentence_reuse_status', 'default_inline_profile_key', 'default_visible_provenance_fields', 'answer_review_menu_key', 'answer_side_terminal_citation_normal_form', 'answer_side_terminal_sentence_normal_form', 'answer_side_terminal_stop_when', 'answer_side_terminal_widen_only_if', 'answer_side_terminal_reopen_artifact', 'answer_side_terminal_first_reopen_owner_map', 'answer_side_terminal_reopen_rule', 'publication_profile_key', 'publication_budget_map', 'answer_review_request_class_mode_map', 'answer_escalation_step_mode_map', 'paired_terminal_answer_reopen_request_classes', 'paired_terminal_cutover_mode', 'paired_terminal_widen_condition', 'paired_terminal_request_reopen_triggers', 'paired_terminal_cutover_sentence_normal_form', 'paired_terminal_stop_when', 'paired_terminal_request_terminal_artifact', 'paired_terminal_request_terminal_kind', 'paired_terminal_request_terminal_widen_only_if', 'paired_terminal_reopen_artifact', 'paired_terminal_fail_closed_reopen_rule', 'request_class_handoff_map', 'request_class_owner_map', 'release_obligation_profile_id', 'release_closure_ledger_id', 'publication_closure_verdict_id', 'publication_closure_status', 'successor_status_envelope_id', 'successor_public_status_token', 'successor_lineage_notice_id', 'public_request_contract_key', 'source_only_public_anchor_family_mode_map', 'source_only_request_fulfillment_certificate_keys', 'source_only_family_completion_map', 'source_only_family_completion_mode_map', 'source_only_evidence_class_mode_map', 'source_only_status_envelope_key', 'source_only_status_token', 'source_only_status_token_mode_map', 'source_only_carryforward_envelope_key', 'source_only_carryforward_token', 'source_only_carryforward_token_mode_map', 'source_only_notice_key_map', 'source_only_notice_normal_form_map', 'source_only_notice_selection_keys', 'source_only_response_menu_keys', 'source_only_response_menu_followup_class_mode_map', 'source_only_request_class_handoff_map', 'source_only_request_class_owner_map', 'source_only_response_packet_map', 'source_only_response_packet_scope_mode_map', 'source_only_response_packet_family_basis_map', 'source_only_response_packet_support_surface_map', 'source_only_response_packet_manifest_cut_map', 'source_only_response_packet_inventory_cut_map', 'source_only_response_packet_carryforward_profile_map', 'source_only_response_packet_reuse_status_map', 'source_only_response_packet_refresh_family_mode_map', 'source_only_response_packet_delta_map', 'source_only_response_packet_delta_family_mode_map', 'source_only_refresh_notice_map', 'source_only_refresh_notice_normal_form_map', 'source_only_refresh_notice_selection_map', 'source_only_refresh_response_menu_map', 'source_only_refresh_followup_handoff_map', 'source_only_refresh_followup_owner_map', 'source_only_refresh_response_packet_map', 'source_only_refresh_response_packet_family_basis_map', 'source_only_refresh_response_packet_support_surface_map', 'source_only_refresh_response_packet_manifest_cut_map', 'source_only_refresh_response_packet_inventory_cut_map', 'source_only_refresh_response_packet_validation_mode_map', 'source_only_refresh_response_packet_closure_map', 'source_only_refresh_response_packet_closure_status_map', 'source_only_refresh_response_packet_closure_scope_map', 'source_only_refresh_response_packet_reopen_trigger_map', 'source_only_refresh_response_packet_reopen_owner_map', 'source_only_request_ladder', 'citation_docket_key', 'answer_carrier_slot_key', 'answer_audit_trail_key', 'disclosure_packet_key', 'disclosure_packet_support_surface', 'disclosure_packet_manifest_cut', 'disclosure_packet_inventory_cut', 'evidence_class_keys', 'escalation_ladder_key', 'supporting_line_item_names', 'release_stage_families', 'release_stage_vocabulary_mode_map', 'available_request_classes', 'why'],
            'stable_ladder_fields': ['position', 'task_key', 'spine_segment', 'label', 'canonical_owner', 'artifact', 'question', 'stop_when', 'widen_only_if', 'why'],
            'source_only_request_ladder_fields': ['position', 'task_key', 'bucket_key', 'label', 'canonical_owner', 'note_range', 'artifact', 'question', 'rung_sentence_normal_form', 'route_local_reopen_artifact', 'route_local_reopen_rule', 'stop_when', 'widen_only_if', 'why'],
            'widening_rule': 'Question routing may move rightward only when the task actually widens: from theorem justification to receipt identification to replay to release status to the answer-side disclosure packet to review packaging, or from source-only promise to packetization to visible refresh to successor-facing closure.',
            'public_anchor_rule': 'Audience/question routes may start from one emitted public anchor path, but any challenge must widen through the maintained review menu rather than inventing a fresh handoff.',
            'audience_stop_rule': 'For one shipped public answer, the route is complete only when it names the governing public anchor, stop-profile key, emitted-answer / sentence-lock pair, exact publication-profile / citation-docket / answer-carrier-slot / answer-audit-trail / disclosure-packet / escalation-ladder / review-menu key chain, inherited brief/expanded/exact/full-audit publication-budget map, imported six-class request handoff map, the mirrored answer-review request-class vocabulary posture map, the mirrored answer-escalation-step vocabulary posture map, the mirrored release-stage-vocabulary posture map, imported six-class request-class owner map, the exact release-obligation-profile / release-closure-ledger / publication-closure-verdict / successor-status-envelope / successor-lineage-notice key chain together with the imported public-status token it emits, the paper-level source-only request contract, imported family completion certificates plus the mirrored evidence-class-vocabulary map and the paper-level source-only status/carryforward tokens and their vocabulary-mode maps, imported exact source-only notice / canonical-notice-family / notice-selection / response-menu / response-menu-followup-vocabulary / source-only request-class handoff / owner / bounded-response-packet / response-packet-scope / packet-carryforward-profile / packet-family-basis / packet-support-surface / packet-manifest-cut / packet-inventory-cut / packet-delta maps for omitted-support follow-up, imported exact successor packet-reuse / emitted-refresh-notice / canonical-refresh-family / refresh-notice-selection / refresh-response-menu / successor-followup handoff / owner / exact successor-facing packet / exact closure-verdict keys together with packet-family-mode / delta / delta-family-mode / packet-family-basis / packet-support-surface / packet-manifest-cut / packet-inventory-cut / validation-posture / closure / closure-scope / reopen-owner maps for the visible refresh branch, default inline-provenance mode, route-side citation docket / answer-audit-trail / disclosure packet / exact disclosure-packet support-surface / manifest-cut / inventory-cut maps / escalation ladder bundle, and review-menu path; semantic stop fields stay owned by the stop profile, checked wording stays owned by the answer-card-plus-sentence-lock pair, terse-publication packaging stays owned by the publication profile, repeated review request-class labels stay imported review-menu vocabulary, repeated reveal-step labels stay imported escalation-ladder vocabulary, repeated release-stage labels stay imported release-spine vocabulary, release-stage package completeness stays owned by the exact release-obligation-profile / release-closure-ledger / publication-closure-verdict / successor-status-envelope / successor-lineage-notice chain, the immediate owner of each request-class choice stays visible through the request-class owner map, paper-facing omitted-support promise scope stays owned by the public request contract, source-only completion stays owned by the request-fulfillment certificates and the paper-level status/carryforward envelopes, exact outward source-only visible sentence and canonical family stay owned by the imported notice / normal-form / selection ledgers, the immediate owner of each notice-keyed omitted-support follow-up choice stays visible through the imported source-only request-class owner map, exact outward source-only handoff slices stay owned by the imported response packets together with their carried support / manifest / inventory cuts and with the exact carryforward/delta owner chain kept visible, exact visible-refresh successor sentence and canonical family stay owned by the imported refresh-notice / refresh-normal-form / refresh-selection ledgers, the immediate owner of each successor-facing follow-up choice stays visible through the imported refresh-followup owner map, exact visible-refresh successor surfaces stay owned by the imported packet-carryforward / delta / refresh-response-menu / successor-packet / closure ledgers together with their carried support / manifest / inventory cut and derived validation posture, and request-class widening stays owned by the review menu.'
        },
        'stable_ladder': stable_bridge_ladder,
        'source_only_request_ladder': source_only_request_ladder,
        'generic_question_routes': [
            {
                'route_key': entry['task_key'],
                'question_examples': generic_question_examples.get(entry['task_key'], []),
                'stop_kind': entry['stop_kind'],
                'spine_segment': entry.get('spine_segment'),
                'bucket_key': entry.get('bucket_key'),
                'first_stop_owner': entry['canonical_owner'],
                'first_stop_artifact': entry['artifact'],
                'next_route_keys_if_scope_widens': widening_transitions.get(entry['task_key'], []),
                'why': entry['why'],
            }
            for entry in minimal_bridge_cuts
        ],
        'audience_question_routes': [
            {
                'route_key': f"{answer['audience']}__{answer['question_key']}",
                'audience': answer['audience'],
                'question_key': answer['question_key'],
                'challenge_route_key': answer['challenge_route_key'],
                'stop_profile_key': answer['stop_profile_key'],
                'minimal_public_anchor_path': answer['start_path'],
                'sentence_family': answer['sentence_family'],
                'answer_card_key': answer['answer_card_key'],
                'sentence_lock_key': answer['sentence_lock_key'],
                'sentence_reuse_status': answer.get('sentence_reuse_status'),
                'default_inline_profile_key': answer['default_inline_profile_key'],
                'default_visible_provenance_fields': answer['default_visible_provenance_fields'],
                'answer_review_menu_key': answer['answer_review_menu_key'],
                'answer_side_terminal_citation_normal_form': answer['answer_side_terminal_citation_normal_form'],
                'answer_side_terminal_sentence_normal_form': answer['answer_side_terminal_sentence_normal_form'],
                'answer_side_terminal_stop_when': answer['answer_side_terminal_stop_when'],
                'answer_side_terminal_widen_only_if': answer['answer_side_terminal_widen_only_if'],
                'answer_side_terminal_reopen_artifact': answer['answer_side_terminal_reopen_artifact'],
                'answer_side_terminal_first_reopen_owner_map': answer['answer_side_terminal_first_reopen_owner_map'],
                'answer_side_terminal_reopen_rule': answer['answer_side_terminal_reopen_rule'],
                'publication_profile_key': answer['publication_profile_key'],
                'publication_budget_map': answer['publication_budget_map'],
                'answer_review_request_class_mode_map': answer['answer_review_request_class_mode_map'],
                'answer_escalation_step_mode_map': answer['answer_escalation_step_mode_map'],
                'paired_terminal_answer_reopen_request_classes': answer['paired_terminal_answer_reopen_request_classes'],
                'paired_terminal_cutover_mode': answer['paired_terminal_cutover_mode'],
                'paired_terminal_widen_condition': answer['paired_terminal_widen_condition'],
                'paired_terminal_request_reopen_triggers': answer['paired_terminal_request_reopen_triggers'],
                'paired_terminal_cutover_sentence_normal_form': answer['paired_terminal_cutover_sentence_normal_form'],
                'paired_terminal_stop_when': answer['paired_terminal_stop_when'],
                'paired_terminal_request_terminal_artifact': answer['paired_terminal_request_terminal_artifact'],
                'paired_terminal_request_terminal_kind': answer['paired_terminal_request_terminal_kind'],
                'paired_terminal_request_terminal_widen_only_if': answer['paired_terminal_request_terminal_widen_only_if'],
                'paired_terminal_reopen_artifact': answer['paired_terminal_reopen_artifact'],
                'paired_terminal_fail_closed_reopen_rule': answer['paired_terminal_fail_closed_reopen_rule'],
                'request_class_handoff_map': answer['request_class_handoff_map'],
                'request_class_owner_map': answer['request_class_owner_map'],
                'release_obligation_profile_id': answer['release_obligation_profile_id'],
                'release_closure_ledger_id': answer['release_closure_ledger_id'],
                'publication_closure_verdict_id': answer['publication_closure_verdict_id'],
                'publication_closure_status': answer['publication_closure_status'],
                'successor_status_envelope_id': answer['successor_status_envelope_id'],
                'successor_public_status_token': answer['successor_public_status_token'],
                'successor_lineage_notice_id': answer['successor_lineage_notice_id'],
                'public_request_contract_key': answer['public_request_contract_key'],
                'source_only_public_anchor_family_mode_map': answer['source_only_public_anchor_family_mode_map'],
                'source_only_request_fulfillment_certificate_keys': answer['source_only_request_fulfillment_certificate_keys'],
                'source_only_family_completion_map': answer['source_only_family_completion_map'],
                'source_only_family_completion_mode_map': answer['source_only_family_completion_mode_map'],
                'source_only_evidence_class_mode_map': answer['source_only_evidence_class_mode_map'],
                'source_only_status_envelope_key': answer['source_only_status_envelope_key'],
                'source_only_status_token': answer['source_only_status_token'],
                'source_only_status_token_mode_map': answer['source_only_status_token_mode_map'],
                'source_only_carryforward_envelope_key': answer['source_only_carryforward_envelope_key'],
                'source_only_carryforward_token': answer['source_only_carryforward_token'],
                'source_only_carryforward_token_mode_map': answer['source_only_carryforward_token_mode_map'],
                'source_only_notice_key_map': answer['source_only_notice_key_map'],
                'source_only_notice_normal_form_map': answer['source_only_notice_normal_form_map'],
                'source_only_notice_selection_keys': answer['source_only_notice_selection_keys'],
                'source_only_response_menu_keys': answer['source_only_response_menu_keys'],
                'source_only_response_menu_followup_class_mode_map': answer['source_only_response_menu_followup_class_mode_map'],
                'source_only_request_class_handoff_map': answer['source_only_request_class_handoff_map'],
                'source_only_request_class_owner_map': answer['source_only_request_class_owner_map'],
                'source_only_response_packet_map': answer['source_only_response_packet_map'],
                'source_only_response_packet_scope_mode_map': answer['source_only_response_packet_scope_mode_map'],
                'source_only_response_packet_family_basis_map': answer['source_only_response_packet_family_basis_map'],
                'source_only_response_packet_support_surface_map': answer['source_only_response_packet_support_surface_map'],
                'source_only_response_packet_manifest_cut_map': answer['source_only_response_packet_manifest_cut_map'],
                'source_only_response_packet_inventory_cut_map': answer['source_only_response_packet_inventory_cut_map'],
                'source_only_response_packet_carryforward_profile_map': answer['source_only_response_packet_carryforward_profile_map'],
                'source_only_response_packet_reuse_status_map': answer['source_only_response_packet_reuse_status_map'],
                'source_only_response_packet_refresh_family_mode_map': answer['source_only_response_packet_refresh_family_mode_map'],
                'source_only_response_packet_delta_map': answer['source_only_response_packet_delta_map'],
                'source_only_response_packet_delta_family_mode_map': answer['source_only_response_packet_delta_family_mode_map'],
                'source_only_refresh_notice_map': answer['source_only_refresh_notice_map'],
                'source_only_refresh_notice_normal_form_map': answer['source_only_refresh_notice_normal_form_map'],
                'source_only_refresh_notice_selection_map': answer['source_only_refresh_notice_selection_map'],
                'source_only_refresh_response_menu_map': answer['source_only_refresh_response_menu_map'],
                'source_only_refresh_followup_handoff_map': answer['source_only_refresh_followup_handoff_map'],
                'source_only_refresh_followup_owner_map': answer['source_only_refresh_followup_owner_map'],
                'source_only_refresh_response_packet_map': answer['source_only_refresh_response_packet_map'],
                'source_only_refresh_response_packet_family_basis_map': answer['source_only_refresh_response_packet_family_basis_map'],
                'source_only_refresh_response_packet_support_surface_map': answer['source_only_refresh_response_packet_support_surface_map'],
                'source_only_refresh_response_packet_manifest_cut_map': answer['source_only_refresh_response_packet_manifest_cut_map'],
                'source_only_refresh_response_packet_inventory_cut_map': answer['source_only_refresh_response_packet_inventory_cut_map'],
                'source_only_refresh_response_packet_validation_mode_map': answer['source_only_refresh_response_packet_validation_mode_map'],
                'source_only_refresh_response_packet_closure_map': answer['source_only_refresh_response_packet_closure_map'],
                'source_only_refresh_response_packet_closure_status_map': answer['source_only_refresh_response_packet_closure_status_map'],
                'source_only_refresh_response_packet_closure_scope_map': answer['source_only_refresh_response_packet_closure_scope_map'],
                'source_only_refresh_response_packet_reopen_trigger_map': answer['source_only_refresh_response_packet_reopen_trigger_map'],
                'source_only_refresh_response_packet_reopen_owner_map': answer['source_only_refresh_response_packet_reopen_owner_map'],
                'source_only_request_ladder': answer['source_only_request_ladder'],
                'citation_docket_key': answer['citation_docket_key'],
                'answer_carrier_slot_key': answer['answer_carrier_slot_key'],
                'answer_audit_trail_key': answer['answer_audit_trail_key'],
                'disclosure_packet_key': answer['disclosure_packet_key'],
                'disclosure_packet_support_surface': answer['disclosure_packet_support_surface'],
                'disclosure_packet_manifest_cut': answer['disclosure_packet_manifest_cut'],
                'disclosure_packet_inventory_cut': answer['disclosure_packet_inventory_cut'],
                'evidence_class_keys': answer['evidence_class_keys'],
                'escalation_ladder_key': answer['escalation_ladder_key'],
                'supporting_line_item_names': answer['supporting_line_item_names'],
                'release_stage_families': answer['release_stage_families'],
                'release_stage_vocabulary_mode_map': answer['release_stage_vocabulary_mode_map'],
                'available_request_classes': [review_entry['request_class'] for review_entry in review_menu_index[answer['answer_review_menu_key']]['review_entries']],
                'why': answer['why'],
            }
            for answer in answer_spines
        ],
        'note': 'Derived question-to-first-stop routing catalog for the worked example. It keeps common question phrasings and the four shipped audience/question routes machine-readable by binding each public anchor to its governing stop profile, emitted answer card, sentence lock, exact publication-profile / citation-docket / answer-carrier-slot / answer-audit-trail / disclosure-packet / escalation-ladder / review-menu keys, inherited publication-budget map, imported six-class request handoff map, mirrored answer-review request-class vocabulary posture map, mirrored answer-escalation-step vocabulary posture map, mirrored release-stage-vocabulary posture map, imported six-class request-class owner map, exact release-obligation-profile / release-closure-ledger / publication-closure-verdict / successor-status-envelope / successor-lineage-notice keys together with the imported public-status token, the exact paper-level source-only request-contract key, the exact evidence-class key list, the exact family-scoped request-fulfillment-certificate key list, imported family completion certificates plus the mirrored evidence-class-vocabulary map, the exact paper-level source-only status-envelope key together with its mirrored status-token vocabulary map, the exact paper-level source-only carryforward-envelope key together with its mirrored carryforward-token vocabulary map, imported source-only notice keys / canonical-notice-family (notice-normal-form) keys / notice-selection keys, imported notice-keyed response-menu keys together with response-menu-followup-vocabulary tags, imported source-only request-class handoff / owner maps, imported exact bounded source-only response-packet keys together with response-packet-scope / packet-carryforward-profile / packet-family-basis / packet-support-surface / packet-manifest-cut / packet-inventory-cut / packet-delta maps for each notice/follow-up pair, imported source-only packet-reuse / packet-family-mode / packet-delta-family-mode / refresh-family-mode bridges for omitted-support follow-up, imported successor packet-reuse / refresh-notice keys / canonical-refresh-family (refresh-normal-form) keys / refresh-notice-selection / refresh-response-menu keys, imported successor-followup handoff / owner maps, imported exact successor-facing packet / packet-family-basis / packet-support-surface / packet-manifest-cut / packet-inventory-cut / validation-posture / closure-verdict / closure / closure-status / closure-scope / reopen-trigger / reopen-owner keys for the visible refresh branch, default inline-provenance mode, route-side citation docket, route-side answer carrier slot, route-side answer audit trail, route-side disclosure packet, exact route-side disclosure-packet support-surface / manifest-cut / inventory-cut maps, route-side escalation ladder, route-side review menu, and review-menu widening hook without creating any new owner beyond the maintained series spine, stop-profile, answer-card, sentence-lock, publication-profile, release-obligation-profile, release-closure-ledger, publication-closure-verdict, successor-status-envelope, successor-lineage-notice, citation-docket, answer-carrier-slot, answer-audit-trail, disclosure-packet, disclosure-packet support-surface / manifest-cut / inventory-cut maps, escalation-ladder, public-request-contract, request-fulfillment-certificate, public-request-status-envelope, public-request-carryforward-envelope, source-only notice / notice-normal-form / selection / response-menu / response-packet / packet-family-basis / packet-support-surface / packet-manifest-cut / packet-inventory-cut / packet-carryforward / packet-delta / refresh-notice / refresh-normal-form / refresh-selection / refresh-response-menu / successor-packet / successor-packet-family-basis / successor-packet-support-surface / successor-packet-manifest-cut / successor-packet-inventory-cut / successor-packet-validation-posture / closure-verdict, branch-map, and review-menu companions.'
    }

    series_spine = {
        'series_spine_id': SERIES_SPINE_ID,
        'claim_id': compare_report['claim_id'],
        'base_release_id': compare_report['base_release_id'],
        'release_id': compare_report['release_id'],
        'successor_release_id': compare_report['successor_release_id'],
        'compare_profile_id': compare_report['compare_profile_id'],
        'compare_report_id': compare_report['report_id'],
        'line_item_owner_map_id': line_item_owner_map['owner_map_id'],
        'release_spine_id': release_spine['spine_id'],
        'successor_challenge_answer_review_menus_id': answer_review_menus['challenge_answer_review_menus_id'],
        'successor_challenge_routes_id': routes['challenge_routes_id'],
        'successor_challenge_stop_profiles_id': stop_profiles['challenge_stop_profiles_id'],
        'successor_challenge_branches_id': branches['challenge_branches_id'],
        'requestable_evidence_classes_id': requestable_evidence_classes['requestable_evidence_classes_id'],
        'successor_public_request_contracts_id': public_request_contracts['public_request_contracts_id'],
        'successor_request_fulfillment_certificates_id': request_fulfillment_certificates['request_fulfillment_certificates_id'],
        'successor_public_request_status_envelopes_id': public_request_status_envelope['public_request_status_envelopes_id'],
        'successor_public_request_carryforward_envelopes_id': public_request_carryforward_envelope['public_request_carryforward_envelopes_id'],
        'successor_public_request_notices_id': public_request_notice['public_request_notices_id'],
        'successor_public_request_notice_normal_forms_id': public_request_notice_normal_forms['public_request_notice_normal_forms_id'],
        'successor_public_request_notice_selections_id': public_request_notice_selections['public_request_notice_selections_id'],
        'successor_public_request_response_menus_id': public_request_response_menus['public_request_response_menus_id'],
        'successor_public_request_response_packets_id': public_request_response_packets['public_request_response_packets_id'],
        'successor_public_request_response_packet_carryforward_profiles_id': public_request_response_packet_carryforward_profiles['public_request_response_packet_carryforward_profiles_id'],
        'successor_public_request_response_packet_delta_ledgers_id': public_request_response_packet_delta_ledgers['public_request_response_packet_delta_ledgers_id'],
        'successor_public_request_response_packet_refresh_notices_id': public_request_response_packet_refresh_notices['public_request_response_packet_refresh_notices_id'],
        'successor_public_request_response_packet_refresh_notice_normal_forms_id': public_request_response_packet_refresh_notice_normal_forms['public_request_response_packet_refresh_notice_normal_forms_id'],
        'successor_public_request_response_packet_refresh_notice_selections_id': public_request_response_packet_refresh_notice_selections['public_request_response_packet_refresh_notice_selections_id'],
        'successor_public_request_response_packet_refresh_response_menus_id': public_request_response_packet_refresh_response_menus['public_request_response_packet_refresh_response_menus_id'],
        'successor_public_request_response_packet_refresh_response_packets_id': public_request_response_packet_refresh_response_packets['public_request_response_packet_refresh_response_packets_id'],
        'successor_public_request_response_packet_refresh_response_packet_closure_verdicts_id': public_request_response_packet_refresh_response_packet_closure_verdicts['public_request_response_packet_refresh_response_packet_closure_verdicts_id'],
        'note_version': compare_report['note_version'],
        'series_spine_contract': {
            'line_item_spine_fields': ['line_item_name', 'math_roots', 'receipt_anchor', 'replay_anchor', 'release_anchor', 'review_anchor', 'packet_local_sentence_normal_form', 'stop_when', 'widen_only_if', 'route_local_reopen_artifact', 'route_local_reopen_rule', 'why'],
            'optional_variant_spine_fields': ['line_item_name', 'materialization_status', 'receipt_variant_file', 'evidence_id', 'receipt_anchor', 'owner_map_anchor', 'replay_anchor', 'support_anchor', 'variant_sentence_normal_form', 'stop_when', 'widen_only_if', 'route_local_reopen_artifact', 'route_local_reopen_rule', 'why'],
            'stable_ladder_fields': ['position', 'task_key', 'spine_segment', 'label', 'canonical_owner', 'artifact', 'question', 'stop_when', 'widen_only_if', 'why'],
            'source_only_request_ladder_fields': ['position', 'task_key', 'bucket_key', 'label', 'canonical_owner', 'note_range', 'artifact', 'question', 'rung_sentence_normal_form', 'route_local_reopen_artifact', 'route_local_reopen_rule', 'stop_when', 'widen_only_if', 'why'],
            'answer_spine_fields': ['audience', 'question_key', 'challenge_route_key', 'stop_profile_key', 'answer_review_menu_key', 'answer_side_terminal_citation_normal_form', 'answer_side_terminal_sentence_normal_form', 'answer_side_terminal_stop_when', 'answer_side_terminal_widen_only_if', 'answer_side_terminal_reopen_artifact', 'answer_side_terminal_first_reopen_owner_map', 'answer_side_terminal_reopen_rule', 'start_path', 'sentence_family', 'answer_card_key', 'sentence_lock_key', 'sentence_reuse_status', 'default_inline_profile_key', 'default_visible_provenance_fields', 'supporting_line_item_names', 'release_stage_families', 'release_stage_vocabulary_mode_map', 'publication_profile_key', 'publication_budget_map', 'answer_review_request_class_mode_map', 'answer_escalation_step_mode_map', 'paired_terminal_answer_reopen_request_classes', 'paired_terminal_cutover_mode', 'paired_terminal_widen_condition', 'paired_terminal_request_reopen_triggers', 'paired_terminal_cutover_sentence_normal_form', 'paired_terminal_stop_when', 'paired_terminal_request_terminal_artifact', 'paired_terminal_request_terminal_kind', 'paired_terminal_request_terminal_widen_only_if', 'paired_terminal_reopen_artifact', 'paired_terminal_fail_closed_reopen_rule', 'request_class_handoff_map', 'request_class_owner_map', 'release_obligation_profile_id', 'release_closure_ledger_id', 'publication_closure_verdict_id', 'publication_closure_status', 'successor_status_envelope_id', 'successor_public_status_token', 'successor_lineage_notice_id', 'public_request_contract_key', 'source_only_public_anchor_family_mode_map', 'source_only_request_fulfillment_certificate_keys', 'source_only_family_completion_map', 'source_only_family_completion_mode_map', 'source_only_evidence_class_mode_map', 'source_only_status_envelope_key', 'source_only_status_token', 'source_only_status_token_mode_map', 'source_only_carryforward_envelope_key', 'source_only_carryforward_token', 'source_only_carryforward_token_mode_map', 'source_only_notice_key_map', 'source_only_notice_normal_form_map', 'source_only_notice_selection_keys', 'source_only_response_menu_keys', 'source_only_response_menu_followup_class_mode_map', 'source_only_request_class_handoff_map', 'source_only_request_class_owner_map', 'source_only_response_packet_map', 'source_only_response_packet_scope_mode_map', 'source_only_response_packet_family_basis_map', 'source_only_response_packet_support_surface_map', 'source_only_response_packet_manifest_cut_map', 'source_only_response_packet_inventory_cut_map', 'source_only_response_packet_carryforward_profile_map', 'source_only_response_packet_reuse_status_map', 'source_only_response_packet_refresh_family_mode_map', 'source_only_response_packet_delta_map', 'source_only_response_packet_delta_family_mode_map', 'source_only_refresh_notice_map', 'source_only_refresh_notice_normal_form_map', 'source_only_refresh_notice_selection_map', 'source_only_refresh_response_menu_map', 'source_only_refresh_followup_handoff_map', 'source_only_refresh_followup_owner_map', 'source_only_refresh_response_packet_map', 'source_only_refresh_response_packet_family_basis_map', 'source_only_refresh_response_packet_support_surface_map', 'source_only_refresh_response_packet_manifest_cut_map', 'source_only_refresh_response_packet_inventory_cut_map', 'source_only_refresh_response_packet_validation_mode_map', 'source_only_refresh_response_packet_closure_map', 'source_only_refresh_response_packet_closure_status_map', 'source_only_refresh_response_packet_closure_scope_map', 'source_only_refresh_response_packet_reopen_trigger_map', 'source_only_refresh_response_packet_reopen_owner_map', 'source_only_request_ladder', 'citation_docket_key', 'answer_carrier_slot_key', 'answer_audit_trail_key', 'disclosure_packet_key', 'disclosure_packet_support_surface', 'disclosure_packet_manifest_cut', 'disclosure_packet_inventory_cut', 'evidence_class_keys', 'escalation_ladder_key', 'why'],
            'minimal_bridge_cut_fields': ['task_key', 'stop_kind', 'spine_segment', 'bucket_key', 'canonical_owner', 'artifact', 'question', 'bridge_cut_sentence_normal_form', 'bridge_cut_reopen_artifact', 'bridge_cut_reopen_rule', 'stop_when', 'widen_only_if', 'why'],
            'source_only_owner_bucket_fields': ['bucket_key', 'note_range', 'first_question', 'artifacts', 'bucket_sentence_normal_form', 'route_local_reopen_artifact', 'route_local_first_rung_owner', 'route_local_first_rung_artifact', 'route_local_reopen_rule', 'stop_when', 'widen_only_if', 'why'],
            'narrowing_rule': 'Series spines may move left-to-right only by narrowing the task from theorem content to public claim surface to replay path to release-evolution stage to the answer-side disclosure packet to review-handoff choice; later entries never silently replace earlier owners.',
            'challenge_reachability_rule': 'Every answer spine must resolve to one shipped review menu and to supporting line-item spines whose replay and receipt anchors can be walked leftward without guesswork.',
            'adjacent_owner_bucket_rule': 'If the question is source-only request or successor refresh packet machinery rather than theorem-to-review lineage, stop at the first sufficient owner bucket instead of stretching the series spine beyond its bridge role.'
        },
        'line_item_spines': line_item_spines,
        'optional_variant_spines': optional_variant_spines,
        'stable_ladder': stable_bridge_ladder,
        'source_only_request_ladder': source_only_request_ladder,
        'answer_spines': answer_spines,
        'minimal_bridge_cuts': minimal_bridge_cuts,
        'source_only_owner_buckets': source_only_owner_buckets,
        'note': 'Derived theorem-to-review bridge for the worked example. It ties mathematical roots, receipt anchors, replay anchors, release-stage anchors, the answer-side disclosure-packet anchor for the paper-facing archive cut, emitted-answer / sentence-lock reuse anchors, exact publication-profile / citation-docket / answer-carrier-slot / answer-audit-trail / disclosure-packet / escalation-ladder / review-menu keys, inherited publication-budget forms, imported six-class request handoff maps, the mirrored answer-review request-class vocabulary posture map, the mirrored answer-escalation-step vocabulary posture map, the mirrored release-stage-vocabulary posture map, imported six-class request-class owner maps, exact release-obligation-profile / release-closure-ledger / publication-closure-verdict / successor-status-envelope / successor-lineage-notice key chain together with the imported public-status token it emits, the exact paper-level source-only request-contract key together with the exact evidence-class key list plus the mirrored public-anchor-family / evidence-class vocabulary maps, the exact family-scoped request-fulfillment-certificate key list, imported family completion certificates plus the mirrored evidence-class-vocabulary map, the exact paper-level source-only status-envelope key together with its mirrored status-token vocabulary map, the exact paper-level source-only carryforward-envelope key together with its mirrored carryforward-token vocabulary map, imported exact source-only notice / canonical-notice-family / notice-normal-form / notice-selection / response-menu / request-class-owner / exact bounded response-packet keys together with response-menu-followup-vocabulary / response-packet-scope / packet-family-basis / packet-support-surface / packet-manifest-cut / packet-inventory-cut / packet-carryforward-profile / packet-delta maps for omitted-support follow-up, imported source-only packet-family-mode / packet-delta-family-mode / response-packet refresh-family-mode bridges, imported exact successor refresh-notice / canonical-refresh-family / refresh-normal-form / refresh-selection / refresh-response-menu / successor-followup-owner / exact successor-facing packet / exact closure-verdict keys together with packet-family-basis / packet-support-surface / packet-manifest-cut / packet-inventory-cut / validation-posture / closure / closure-scope / reopen-owner maps for the visible refresh branch, and answer-review anchors together without creating a new stage owner, while keeping the exact answer-side handoff chain visible before the later source-only request tail, while exporting optional profiling variant receipt spines beside--not inside--the base line-item ladders, and it records adjacent source-only owner buckets plus an explicit eighteen-step source-only request ladder for tasks that should stop beside rather than inside that bridge.'
    }

    digests = {}
    digests['example_compare_report.json'] = write_json('example_compare_report.json', compare_report)

    for lock in sentence_locks.get('locks', []):
        for obj in lock.get('comparison_anchor', {}).get('object_digests', []):
            if obj.get('artifact') == 'example_compare_report.json':
                obj['sha256'] = digests['example_compare_report.json']

    digests['example_successor_lineage_notice.json'] = write_json('example_successor_lineage_notice.json', lineage)
    digests['example_successor_derivation_graph.json'] = write_json('example_successor_derivation_graph.json', graph)
    digests['example_successor_challenge_coverage.json'] = write_json('example_successor_challenge_coverage.json', coverage)
    digests['example_successor_challenge_surface_hooks.json'] = write_json('example_successor_challenge_surface_hooks.json', surface_hooks)
    digests['example_successor_challenge_terminal_witnesses.json'] = write_json('example_successor_challenge_terminal_witnesses.json', terminal_witnesses)
    digests['example_successor_challenge_coverage_witness_cores.json'] = write_json('example_successor_challenge_coverage_witness_cores.json', coverage_witness_cores)
    digests['example_successor_challenge_coverage_witness_packs.json'] = write_json('example_successor_challenge_coverage_witness_packs.json', coverage_witness_packs)
    digests['example_successor_challenge_coverage_witness_slices.json'] = write_json('example_successor_challenge_coverage_witness_slices.json', coverage_witness_slices)
    digests['example_successor_challenge_answer_capsules.json'] = write_json('example_successor_challenge_answer_capsules.json', answer_capsules)
    digests['example_successor_challenge_answer_sheets.json'] = write_json('example_successor_challenge_answer_sheets.json', answer_sheets)
    digests['example_successor_challenge_answer_cards.json'] = write_json('example_successor_challenge_answer_cards.json', answer_cards)
    digests['example_successor_challenge_answer_carrier_slots.json'] = write_json('example_successor_challenge_answer_carrier_slots.json', answer_carrier_slots)
    digests['example_successor_challenge_answer_audit_trails.json'] = write_json('example_successor_challenge_answer_audit_trails.json', answer_audit_trails)
    digests['example_successor_challenge_answer_citation_dockets.json'] = write_json('example_successor_challenge_answer_citation_dockets.json', answer_citation_dockets)
    digests['example_successor_challenge_answer_publication_profiles.json'] = write_json('example_successor_challenge_answer_publication_profiles.json', answer_publication_profiles)
    digests['example_successor_challenge_answer_disclosure_packets.json'] = write_json('example_successor_challenge_answer_disclosure_packets.json', answer_disclosure_packets)
    digests['example_successor_challenge_answer_escalation_ladders.json'] = write_json('example_successor_challenge_answer_escalation_ladders.json', answer_escalation_ladders)
    digests['example_successor_challenge_answer_review_menus.json'] = write_json('example_successor_challenge_answer_review_menus.json', answer_review_menus)
    digests['example_requestable_evidence_classes.json'] = write_json('example_requestable_evidence_classes.json', requestable_evidence_classes)
    digests['example_public_request_contracts.json'] = write_json('example_public_request_contracts.json', public_request_contracts)
    digests['example_request_fulfillment_certificates.json'] = write_json('example_request_fulfillment_certificates.json', request_fulfillment_certificates)
    digests['example_public_request_status_envelope.json'] = write_json('example_public_request_status_envelope.json', public_request_status_envelope)
    digests['example_public_request_carryforward_envelope.json'] = write_json('example_public_request_carryforward_envelope.json', public_request_carryforward_envelope)
    digests['example_public_request_notice.json'] = write_json('example_public_request_notice.json', public_request_notice)
    digests['example_public_request_notice_normal_forms.json'] = write_json('example_public_request_notice_normal_forms.json', public_request_notice_normal_forms)
    digests['example_public_request_notice_selections.json'] = write_json('example_public_request_notice_selections.json', public_request_notice_selections)
    digests['example_public_request_response_menus.json'] = write_json('example_public_request_response_menus.json', public_request_response_menus)
    digests['example_public_request_response_packets.json'] = write_json('example_public_request_response_packets.json', public_request_response_packets)
    digests['example_public_request_response_packet_carryforward_profiles.json'] = write_json('example_public_request_response_packet_carryforward_profiles.json', public_request_response_packet_carryforward_profiles)
    digests['example_public_request_response_packet_delta_ledgers.json'] = write_json('example_public_request_response_packet_delta_ledgers.json', public_request_response_packet_delta_ledgers)
    digests['example_public_request_response_packet_refresh_notices.json'] = write_json('example_public_request_response_packet_refresh_notices.json', public_request_response_packet_refresh_notices)
    digests['example_public_request_response_packet_refresh_notice_normal_forms.json'] = write_json('example_public_request_response_packet_refresh_notice_normal_forms.json', public_request_response_packet_refresh_notice_normal_forms)
    digests['example_public_request_response_packet_refresh_notice_selections.json'] = write_json('example_public_request_response_packet_refresh_notice_selections.json', public_request_response_packet_refresh_notice_selections)
    digests['example_public_request_response_packet_refresh_response_menus.json'] = write_json('example_public_request_response_packet_refresh_response_menus.json', public_request_response_packet_refresh_response_menus)
    digests['example_public_request_response_packet_refresh_response_packets.json'] = write_json('example_public_request_response_packet_refresh_response_packets.json', public_request_response_packet_refresh_response_packets)
    digests['example_public_request_response_packet_refresh_response_packet_closure_verdicts.json'] = write_json('example_public_request_response_packet_refresh_response_packet_closure_verdicts.json', public_request_response_packet_refresh_response_packet_closure_verdicts)
    digests['example_series_spine.json'] = write_json('example_series_spine.json', series_spine)
    digests['example_question_routes.json'] = write_json('example_question_routes.json', question_routes)
    digests['example_successor_clause_pack.json'] = write_json('example_successor_clause_pack.json', clause_pack)
    digests['example_successor_quote_map.json'] = write_json('example_successor_quote_map.json', quote_map)
    digests['example_successor_sentence_locks.json'] = write_json('example_successor_sentence_locks.json', sentence_locks)
    digests['example_artifact_inventory.json'] = write_json('example_artifact_inventory.json', inventory)

    for path, sha in digests.items():
        upsert_manifest_entry(support_manifest['files'], path, sha)
    decorate_payload_pointer_manifest(support_manifest)
    write_json('support_manifest.json', support_manifest)


if __name__ == '__main__':
    main()
