#!/usr/bin/env python3
import gzip
import hashlib
import json
import math
from fractions import Fraction
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts'
RELEASE_ID = 'worked-example-draft-199'
NOTE_VERSION = '1.99'


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
            try:
                return {'path': path, 'sha256': sha256_bytes(logical_artifact_bytes(path))}
            except Exception:
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


def canon_sha256_id(obj) -> str:
    return "sha256:" + sha256_bytes(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8"))


POINTER_FORMAT = 'worked-example-json-payload-pointer-v1'


def logical_artifact_bytes(name: str) -> bytes:
    """Return logical artifact bytes, resolving offloaded JSON payload pointers.

    The public worked example used to ship very large generated JSON files
    directly on the hot path.  Pointer files keep the original logical path and
    SHA-256 stable while storing the byte-heavy payload as deterministic gzip.
    Validators must hash the logical decompressed bytes, not the small pointer.
    """
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
    payload_path = ART / str(pointer.get('payload_path', ''))
    payload_bytes = payload_path.read_bytes()
    if sha256_bytes(payload_bytes) != pointer.get('payload_sha256'):
        raise ValueError(f'offloaded payload storage digest mismatch for {name}')
    if pointer.get('encoding') != 'gzip-json-utf8-mtime0':
        raise ValueError(f'unsupported offloaded payload encoding for {name}: {pointer.get("encoding")}')
    logical = gzip.decompress(payload_bytes)
    if sha256_bytes(logical) != pointer.get('logical_sha256'):
        raise ValueError(f'offloaded payload logical digest mismatch for {name}')
    if len(logical) != int(pointer.get('logical_bytes', -1)):
        raise ValueError(f'offloaded payload logical byte count mismatch for {name}')
    return logical


def load_json(name: str):
    data = logical_artifact_bytes(name)
    return json.loads(data), sha256_bytes(data)


def check_support_manifest_file_rows(support_manifest):
    archive_root = ROOT.parents[2]
    failures = []
    seen_paths = set()

    def expected_repo_relative(entry):
        raw = entry.get('path')
        base = entry.get('base')
        if not isinstance(raw, str):
            return None
        if base == 'artifact_root':
            return (ART / raw).resolve().relative_to(archive_root).as_posix()
        if base == 'paper_root':
            normalized = raw[3:] if raw.startswith('../') else raw
            return (ROOT / normalized).resolve().relative_to(archive_root).as_posix()
        if base == 'repo_root':
            return raw
        return None

    for idx, entry in enumerate(support_manifest.get('files', [])):
        if not isinstance(entry, dict):
            failures.append({'index': idx, 'problem': 'entry-not-object'})
            continue
        raw = entry.get('path')
        declared = entry.get('sha256')
        base = entry.get('base')
        repo_rel = entry.get('repo_relative_path')
        if not isinstance(raw, str) or not raw:
            failures.append({'index': idx, 'problem': 'missing-path'})
            continue
        if raw in seen_paths:
            failures.append({'path': raw, 'problem': 'duplicate-path'})
        seen_paths.add(raw)
        if base not in {'artifact_root', 'paper_root', 'repo_root'}:
            failures.append({'path': raw, 'problem': 'missing-or-invalid-base', 'base': base})
        expected_rel = expected_repo_relative(entry)
        legacy_rel = (ART / raw).resolve().relative_to(archive_root).as_posix()
        if not isinstance(repo_rel, str) or not repo_rel:
            failures.append({'path': raw, 'problem': 'missing-repo-relative-path', 'legacy_inferred': legacy_rel})
            repo_rel = expected_rel or legacy_rel
        if expected_rel is not None and repo_rel != expected_rel:
            failures.append({'path': raw, 'problem': 'base-repo-relative-path-mismatch', 'repo_relative_path': repo_rel, 'expected': expected_rel})
        target = (archive_root / repo_rel).resolve()
        try:
            target.relative_to(archive_root.resolve())
        except Exception:
            failures.append({'path': raw, 'problem': 'resolved-path-escapes-root', 'repo_relative_path': repo_rel})
            continue
        if not target.exists() or not target.is_file():
            failures.append({'path': raw, 'problem': 'resolved-file-missing', 'repo_relative_path': repo_rel})
            continue
        try:
            if base == 'artifact_root':
                actual = sha256_bytes(logical_artifact_bytes(raw))
                pointer_bytes = target.read_bytes()
                try:
                    pointer = json.loads(pointer_bytes)
                except Exception:
                    pointer = {}
                if isinstance(pointer, dict) and pointer.get('offloaded_payload_pointer') is True:
                    storage_path = ART / str(pointer.get('payload_path', ''))
                    if not storage_path.exists() or sha256_bytes(storage_path.read_bytes()) != pointer.get('payload_sha256'):
                        failures.append({'path': raw, 'problem': 'payload-storage-digest-mismatch', 'repo_relative_path': repo_rel, 'payload_path': pointer.get('payload_path')})
            else:
                actual = sha256_bytes(target.read_bytes())
        except Exception as exc:
            failures.append({'path': raw, 'problem': 'logical-artifact-resolution-failed', 'repo_relative_path': repo_rel, 'detail': str(exc)})
            continue
        if actual != declared:
            failures.append({'path': raw, 'problem': 'sha256-mismatch', 'repo_relative_path': repo_rel, 'declared': declared, 'actual': actual})
    return failures


def extract_paper_version(text: str):
    m = re.search(r'Unified archive note v([0-9]+\.[0-9]+)', text)
    return m.group(1) if m else None


def extract_paper_cut_identity(text: str):
    note_match = re.search(r'note_version=([0-9]+\.[0-9]+)', text)
    release_match = re.search(r'release_id=(worked-example-draft-[0-9]+)', text)
    return {
        'artifact_note_version': note_match.group(1) if note_match else None,
        'release_id': release_match.group(1) if release_match else None,
    }


def main() -> None:
    receipt, receipt_digest = load_json('example_receipt.json')
    uvi, _ = load_json('example_uvi.json')
    abom, _ = load_json('example_abom.json')
    release_receipt, _ = load_json('example_release_receipt.json')
    compare_report, compare_report_digest = load_json('example_compare_report.json')
    compare_profile, _ = load_json('example_compare_profile.json')
    support_manifest, _ = load_json('support_manifest.json')
    support_bundle_map, _ = load_json('example_support_bundle_map.json')
    replay_plans, _ = load_json('example_replay_plans.json')
    state_decl, _ = load_json('example_state_decl.json')
    line_item_owner_map, _ = load_json('example_line_item_owner_map.json')
    artifact_inventory, artifact_inventory_digest = load_json('example_artifact_inventory.json')
    verifier_report, verifier_report_digest = load_json('example_verifier_report.json')
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
    profiling_evidence, profiling_evidence_digest = load_json('example_profiling_evidence.json')
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
        checks.append({'name': name, 'ok': bool(ok), 'detail': detail})

    paper_text = (ROOT / 'paper.tex').read_text(encoding='utf-8')
    paper_version = extract_paper_version(paper_text)
    paper_cut = extract_paper_cut_identity(paper_text)
    readme_text = (ROOT / 'README.md').read_text(encoding='utf-8')

    record('paper wrapper version present', paper_version is not None, f'paper_wrapper_version={paper_version}')
    record('paper artifact cut aligned', paper_cut.get('artifact_note_version') == NOTE_VERSION and paper_cut.get('release_id') == RELEASE_ID, f"paper_wrapper_version={paper_version}; paper_release_id={paper_cut.get('release_id')}; paper_artifact_note_version={paper_cut.get('artifact_note_version')}; expected_release_id={RELEASE_ID}; expected_note_version={NOTE_VERSION}")
    expected_readme_cut = f'Current maintained cut: {RELEASE_ID} / note_version {NOTE_VERSION}'
    record('README current cut aligned', expected_readme_cut in readme_text, expected_readme_cut)
    record('support manifest identity', support_manifest.get('manifest_id') == 'worked-example-support-manifest-v1' and support_manifest.get('release_id') == RELEASE_ID and support_manifest.get('note_version') == NOTE_VERSION, f"manifest_id={support_manifest.get('manifest_id')}; release_id={support_manifest.get('release_id')}; note_version={support_manifest.get('note_version')}")

    support_manifest_file_row_failures = check_support_manifest_file_rows(support_manifest)
    record('support manifest full file digest integrity', not support_manifest_file_row_failures, f"rows={len(support_manifest.get('files', []))}; failures={support_manifest_file_row_failures}")

    abom_receipt_digest = next((entry.get('sha256') for entry in abom.get('artifacts', []) if entry.get('name') == 'example_receipt.json'), None)
    record('receipt digest cross-artifact coherence', all(value == receipt_digest for value in [uvi.get('receipt_digest'), release_receipt.get('receipt_digest'), abom_receipt_digest]), f"receipt_sha256={receipt_digest}; uvi={uvi.get('receipt_digest')}; release_receipt={release_receipt.get('receipt_digest')}; abom={abom_receipt_digest}")

    claim_id = receipt.get('claim_id') or compare_report.get('claim_id')
    repo_root = ROOT.parents[2]

    def queue_note_for_source(source_tex: str) -> str:
        """Resolve the one active queue note without coupling validation to queue state."""
        matches = []
        source_line = f"- Source paper: `{source_tex}`"
        for state in ('candidates', 'published_ready', 'hold', 'published'):
            queue_dir = repo_root / 'release_queue' / state
            if not queue_dir.exists():
                continue
            for note in queue_dir.glob('*.md'):
                if source_line in note.read_text(encoding='utf-8', errors='replace'):
                    matches.append(note.relative_to(repo_root).as_posix())
        if len(matches) != 1:
            raise RuntimeError(f"expected one active queue note for {source_tex}, found {matches}")
        return matches[0]
    active_digest_paths = [
        'series/evaluation_series/paper1_notarized_anonymity_certificates/paper.tex',
        'series/evaluation_series/paper1A_notarized_certificates_addendum/paper.tex',
        'series/evaluation_series/paper2_advantage_contracts_stealth_audits/paper.tex',
        'series/synthesis/paper20_auditor_replay_recipe/paper.tex',
        'series/synthesis/paper76_theorem_to_publication_spines_terse_anonymity_papers/paper.tex',
        'release_queue/candidates/2026.03.16-paper1A-notarized-addendum-candidate.md',
        'release_queue/candidates/2026.03.16-paper2-advantage-contracts-candidate.md',
    ]
    stale_digest_prefixes = ['c9a6b4d4', '79e10476']
    digest_ref_failures = []
    for rel in active_digest_paths:
        active_text = (repo_root / rel).read_text(encoding='utf-8')
        current_present = receipt_digest in active_text or f'{receipt_digest[:8]}\\ldots {receipt_digest[-4:]}' in active_text
        stale_present = [prefix for prefix in stale_digest_prefixes if prefix in active_text]
        if not current_present or stale_present:
            digest_ref_failures.append({'path': rel, 'current_present': current_present, 'stale_present': stale_present})
    record('active worked-route receipt digest references', not digest_ref_failures, f'receipt_sha256={receipt_digest}; stale_prefixes={stale_digest_prefixes}; failures={digest_ref_failures}')

    advantage_carrier_paths = [
        'series/evaluation_series/paper2_advantage_contracts_stealth_audits/paper.tex',
        'release_queue/candidates/2026.03.16-paper2-advantage-contracts-candidate.md',
    ]
    required_advantage_rows = {
        'receipt digest': receipt_digest,
        'release id': RELEASE_ID,
        'artifact note version': NOTE_VERSION,
        'exposure normal form': 'enf:audit-rtt-v2',
        'detector recipe': 'det:rtt-threshold-v1',
        'TV budget': '0.04',
        'audited metric': '0.78',
        'live interval': '[0.74,0.82]',
    }
    advantage_failures = []
    for rel in advantage_carrier_paths:
        active_text = (repo_root / rel).read_text(encoding='utf-8')
        missing = [name for name, needle in required_advantage_rows.items() if needle not in active_text]
        if missing:
            advantage_failures.append({'path': rel, 'missing': missing})
    record('active Eval2 advantage-carrier rows', not advantage_failures, f'paths={advantage_carrier_paths}; failures={advantage_failures}')

    notary_packet = verifier_report.get('notary_replay_packet', {})
    expected_plan_spec = 'sha256:e9168dbec2cabd9115a7f3ea9aebe0a75ff910d2295e450a340716cc7e541193'
    expected_fallback_output = verifier_report.get('recomputed', {}).get('fallback_contact_bits_per_lookup')
    notary_packet_ok = bool(
        notary_packet.get('packet_id') == 'notary_replay_packet'
        and notary_packet.get('claim_id') == claim_id
        and notary_packet.get('receipt_digest') == receipt_digest
        and notary_packet.get('release_id') == RELEASE_ID
        and notary_packet.get('note_version') == NOTE_VERSION
        and notary_packet.get('line_item_name') == 'fallback_contact_surface'
        and notary_packet.get('plan_id') == 'eval-fallback-cct-v1'
        and notary_packet.get('plan_spec_id') == expected_plan_spec
        and notary_packet.get('attempts_present') == [1, 2]
        and notary_packet.get('first_passing_attempt') == 2
        and notary_packet.get('retry_budget') == '1e-6 total across sched.delta.4step.v1'
        and notary_packet.get('metric_family_size') == 5
        and notary_packet.get('bonferroni_threshold') == '6e-8'
        and notary_packet.get('reported_p_value') == '4e-8'
        and notary_packet.get('support_bundle') == 'bundle://worked-example/fallback-cct'
        and notary_packet.get('support_pointer') == 'support://fallback/notarized-attempt-log.example'
        and notary_packet.get('optional_support_packet') == 'example_uvi.json'
        and notary_packet.get('release_handoff_role') == 'fresh_replay_verdict'
        and notary_packet.get('quotable_output', {}).get('fallback_contact_bits_per_lookup') == expected_fallback_output
    )
    record('verifier notary replay packet content', notary_packet_ok, f"packet_id={notary_packet.get('packet_id')}; plan_id={notary_packet.get('plan_id')}; receipt_digest={notary_packet.get('receipt_digest')}; output={notary_packet.get('quotable_output', {}).get('fallback_contact_bits_per_lookup')}")

    notary_carrier_paths = [
        'series/evaluation_series/paper1_notarized_anonymity_certificates/paper.tex',
        'release_queue/published_ready/2026.03.17-paper1-notarized-certificates-published-ready.md',
    ]
    required_notary_rows = {
        'receipt digest': receipt_digest,
        'release id': RELEASE_ID,
        'artifact note version': NOTE_VERSION,
        'notary packet': 'notary_replay_packet',
        'replay hook': 'eval-fallback-cct-v1',
        'plan spec': expected_plan_spec,
        'attempt prefix': 'attempts_present=[1,2]',
        'first passing attempt': 'first_passing_attempt=2',
        'retry budget': '1e-6 total across sched.delta.4step.v1',
        'Bonferroni threshold': '6e-8',
        'reported p-value': 'reported_p_value=4e-8',
        'support bundle': 'bundle://worked-example/fallback-cct',
        'support pointer': 'support://fallback/notarized-attempt-log.example',
        'support required artifacts': 'support_required_artifacts=[example_receipt.json,example_state_decl.json]',
        'release handoff': 'fresh_replay_verdict',
        'quotable output': 'fallback_contact_bits_per_lookup=0.04653341',
    }
    notary_failures = []
    for rel in notary_carrier_paths:
        active_text = (repo_root / rel).read_text(encoding='utf-8')
        missing = [name for name, needle in required_notary_rows.items() if needle not in active_text]
        if missing:
            notary_failures.append({'path': rel, 'missing': missing})
    record('active Eval1 notary-carrier rows', not notary_failures, f'paths={notary_carrier_paths}; failures={notary_failures}')

    support_carrier_paths = [
        'series/evaluation_series/paper1A_notarized_certificates_addendum/paper.tex',
        'release_queue/candidates/2026.03.16-paper1A-notarized-addendum-candidate.md',
    ]
    required_support_rows = {
        'receipt digest': receipt_digest,
        'release id': RELEASE_ID,
        'artifact note version': NOTE_VERSION,
        'log id': 'example-transparency-log',
        'checkpoint': 'tree_size=42 root=EXAMPLE_ONLY',
        'proof pointer': 'consistency://example-transparency-log/41-42',
        'replay hook': 'eval-fallback-cct-v1',
        'plan spec': expected_plan_spec,
        'support bundle': 'bundle://worked-example/fallback-cct',
        'support pointer': 'support://fallback/notarized-attempt-log.example',
    }
    support_failures = []
    for rel in support_carrier_paths:
        active_text = (repo_root / rel).read_text(encoding='utf-8')
        missing = [name for name, needle in required_support_rows.items() if needle not in active_text]
        if missing:
            support_failures.append({'path': rel, 'missing': missing})
    record('active Eval1A support-carrier rows', not support_failures, f'paths={support_carrier_paths}; failures={support_failures}')

    fallback_vector_item = next((item for item in receipt.get('line_items', []) if item.get('name') == 'fallback_tiered_vector'), {})
    fallback_vector_hook = fallback_vector_item.get('replay_hook', {})
    vector_knobs = fallback_vector_item.get('knobs', {})
    expected_vector_plan_spec = 'sha256:38fd8a9252730b1eca7bb12cdd552a00cf50c98204615d197b1436fc061d72b5'
    expected_state_decl = 'sha256:ddfbb55199a6ecdb225cbafc60a74c234ae3334fb40528fde0a2ec2ce6de3f20'
    expected_vector_output = verifier_report.get('recomputed', {}).get('fallback_summary_bits_per_lookup')
    vector_bundle = next((bundle for bundle in support_bundle_map.get('bundles', []) if bundle.get('bundle_id') == 'bundle://worked-example/fallback-vector'), {})
    retired_mceq_fields = {'mc_eq_session_T', 'per_step_epsilon_t', 'conditional_independence_assumption'}
    calibration_packet_ok = bool(
        fallback_vector_item.get('name') == 'fallback_tiered_vector'
        and fallback_vector_item.get('budget_type') == 'tiered_MaxL_summary'
        and fallback_vector_item.get('budget_value') == expected_vector_output
        and fallback_vector_item.get('usage') == 'Q<=500/24h'
        and vector_knobs.get('state_decl_id') == expected_state_decl
        and vector_knobs.get('semantic_scope') == 'illustrative_tiered_observation_attenuation_not_mceq'
        and vector_knobs.get('composition_evidence_status') == 'assumption_only_no_joint_channel_witness'
        and vector_knobs.get('publication_eligible') is False
        and not (retired_mceq_fields & set(vector_knobs))
        and fallback_vector_hook.get('plan_id') == 'eval-fallback-vector-v1'
        and fallback_vector_hook.get('plan_spec_id') == expected_vector_plan_spec
        and fallback_vector_hook.get('artifact_bundle') == 'bundle://worked-example/fallback-vector'
        and vector_bundle.get('consumed_by') == ['eval-fallback-vector-v1']
        and vector_bundle.get('required_artifacts') == ['example_receipt.json', 'example_state_decl.json', 'example_support_bundle_map.json']
        and vector_bundle.get('support_pointers') == ['support://fallback/timing-certificates.example', 'support://fallback/observation-attenuation-slice.example']
    )
    record('verifier fallback-vector non-MC-EQ semantic guard', calibration_packet_ok, f"line_item={fallback_vector_item.get('name')}; plan_id={fallback_vector_hook.get('plan_id')}; semantic_scope={vector_knobs.get('semantic_scope')}; composition_evidence={vector_knobs.get('composition_evidence_status')}; output={expected_vector_output}")

    calibration_carrier_paths = [
        'series/anondht_state_series/paper1A_state_dependent_anonymity_calibration_addendum/paper.tex',
        'release_queue/candidates/2026.03.16-paper1A-state-calibration-addendum-candidate.md',
    ]
    required_calibration_rows = {
        'receipt digest': receipt_digest,
        'release id': RELEASE_ID,
        'artifact note version': NOTE_VERSION,
        'line item': 'fallback_tiered_vector',
        'budget type': 'tiered_MaxL_summary',
        'budget value': str(expected_vector_output),
        'usage': 'Q<=500/24h',
        'state declaration': expected_state_decl,
        'replay hook': 'eval-fallback-vector-v1',
        'plan spec': expected_vector_plan_spec,
        'support bundle': 'bundle://worked-example/fallback-vector',
        'timing pointer': 'support://fallback/timing-certificates.example',
        'observation pointer': 'support://fallback/observation-attenuation-slice.example',
        'semantic scope': 'illustrative_tiered_observation_attenuation_not_mceq',
        'publication eligibility': 'publication_eligible=false',
        'composition evidence': 'assumption_only_no_joint_channel_witness',
        'quotable output': f'fallback_summary_bits_per_lookup={expected_vector_output}',
    }
    calibration_failures = []
    for rel in calibration_carrier_paths:
        active_text = (repo_root / rel).read_text(encoding='utf-8')
        missing = [name for name, needle in required_calibration_rows.items() if needle not in active_text]
        if missing:
            calibration_failures.append({'path': rel, 'missing': missing})
    record('active State1A observation-carrier rows', not calibration_failures, f'paths={calibration_carrier_paths}; failures={calibration_failures}')

    bossfight_rho = 0.05
    bossfight_m = 40
    bossfight_budget_bits = 0.01
    bossfight_independent_any_hit = 1.0 - (1.0 - bossfight_rho) ** bossfight_m
    bossfight_dummy_fraction = bossfight_independent_any_hit / (
        (2.0 ** bossfight_budget_bits) - 1.0 + bossfight_independent_any_hit
    )
    bossfight_row_ok = (
        abs(bossfight_independent_any_hit - 0.8714878434348969) < 1e-15
        and round(bossfight_dummy_fraction, 3) == 0.992
        and bossfight_rho <= bossfight_independent_any_hit <= min(1.0, bossfight_m * bossfight_rho)
    )
    record(
        'verifier BossFight independent-control arithmetic',
        bossfight_row_ok,
        f'rho={bossfight_rho}; m={bossfight_m}; b={bossfight_budget_bits}; '
        f'independent_any_hit={bossfight_independent_any_hit:.12f}; '
        f'equal_marginal_range=[{bossfight_rho:.12f},{min(1.0, bossfight_m * bossfight_rho):.12f}]; '
        f'independent_erasure_dummy_fraction={bossfight_dummy_fraction:.12f}',
    )

    bossfight_source = 'series/bossfight_series/paperB_addendum_evidence_tables/paper.tex'
    bossfight_note = queue_note_for_source(bossfight_source)
    bossfight_source_text = (repo_root / bossfight_source).read_text(encoding='utf-8')
    required_bossfight_source_rows = {
        'independent-contact assumption': 'independent contact-compromise events',
        'representative independent value': '0.05 & 40 & 0.871488',
        'equal-marginal range theorem': '\\rho\\le p_{\\mathsf{hit}}\\le\\min(1,m\\rho)',
        'independent-erasure assumption': 'independent erasure gate',
        'budget row': '0.01 & 0.590 & 0.878 & 0.966 & 0.986',
        'non-certificate boundary': 'No row is a deployment certificate',
        'invalid chained inference': 'The former packet first computed',
    }
    bossfight_source_missing = [
        name for name, needle in required_bossfight_source_rows.items()
        if needle not in bossfight_source_text
    ]
    bossfight_note_text = (repo_root / bossfight_note).read_text(encoding='utf-8')
    required_bossfight_note_rows = {
        'hold verdict': 'Hold / publication-blocked',
        'control-model scope': 'control-model regressions',
        'missing joint law': 'joint contact laws',
        'missing observer mapping': 'observer-channel mapping',
    }
    bossfight_note_missing = [
        name for name, needle in required_bossfight_note_rows.items()
        if needle not in bossfight_note_text
    ]
    bossfight_failures = []
    if bossfight_source_missing:
        bossfight_failures.append({'path': bossfight_source, 'missing': bossfight_source_missing})
    if bossfight_note_missing:
        bossfight_failures.append({'path': bossfight_note, 'missing': bossfight_note_missing})
    record(
        'active BossFight control-model rows and hold posture',
        not bossfight_failures,
        f'source={bossfight_source}; queue_note={bossfight_note}; failures={bossfight_failures}',
    )

    cppc_paper_path = 'series/anondht_state_series/paper3A_cppc_addendum/paper.tex'
    cppc_candidate_path = 'release_queue/candidates/2026.03.16-paper3A-cppc-addendum-candidate.md'
    cppc_paper_text = (repo_root / cppc_paper_path).read_text(encoding='utf-8')
    cppc_required_fields = [
        'schema_version',
        'witness_channels_present',
        'cadence',
        'view_accountant',
        'budget_beacon',
        'transparency',
        'compliance',
    ]
    cppc_linter_needles = [
        'require_keys(card, [',
        'assert subset(card["witness_channels_present"], ALLOWED_CHANNEL_ENUM)',
        'assert exists_under(ROOT, artifact)',
        'assert sha256_matches(ROOT, artifact, declared_sha256(card, artifact))',
        'warn_if_missing(card["transparency"], "log")',
        'warn_if_missing(card["transparency"], "signatures")',
    ]
    cppc_linter_ok = (
        all(field in cppc_paper_text for field in cppc_required_fields)
        and all(needle in cppc_paper_text for needle in cppc_linter_needles)
        and 'tools/cppc_lint.py' not in cppc_paper_text
    )
    record('verifier CPPC inline-linter excerpt content', cppc_linter_ok, f'required_fields={cppc_required_fields}; missing_linter_needles={[needle for needle in cppc_linter_needles if needle not in cppc_paper_text]}; false_tool_path_present={"tools/cppc_lint.py" in cppc_paper_text}')

    cppc_support_paths = [cppc_paper_path, cppc_candidate_path]
    required_cppc_rows = {
        'support packet': 'support packet',
        'many-detector note': 'many-detector',
        'schema version': 'schema_version',
        'field witness channels': 'witness_channels_present',
        'field cadence': 'cadence',
        'field view accountant': 'view_accountant',
        'field budget beacon': 'budget_beacon',
        'field transparency': 'transparency',
        'field compliance': 'compliance',
        'enum check': 'enum',
        'artifact existence/hash check': 'artifact',
        'State3 owner': 'State~3',
        'Eval1 owner': 'Eval~1',
        'OperationalB owner': 'Operational~B',
        'ReleaseA owner': 'Release~A',
    }
    cppc_failures = []
    for rel in cppc_support_paths:
        active_text = (repo_root / rel).read_text(encoding='utf-8')
        missing = [name for name, needle in required_cppc_rows.items() if needle not in active_text]
        if missing:
            cppc_failures.append({'path': rel, 'missing': missing})
    record('active CPPC addendum schema-linter rows', not cppc_failures, f'paths={cppc_support_paths}; failures={cppc_failures}')

    pscq_paper_path = 'series/congestion_series/paper2A_psc_q_microstudies_addendum/paper.tex'
    pscq_candidate_path = 'release_queue/candidates/2026.03.16-paper2A-psc-q-addendum-candidate.md'
    pscq_paper_text = (repo_root / pscq_paper_path).read_text(encoding='utf-8')
    pscq_paper_norm = pscq_paper_text.replace('\\_', '_')
    pscq_roster_files = [
        'fig_padding_worsens_tv.pdf',
        'fig_idle_padding_partial_tv.pdf',
        'fig_service_bias_substitution.pdf',
        'fig_spectral_dither_attenuation.pdf',
        'fig_utilization_range_optimizer.pdf',
    ]
    pscq_failure_needles = {
        'utilization-knee caution': 'utilization-knee caution',
        'partial-idle-filling claim': 'partial-idle-filling claim',
        'service-bias pitfall': 'service-bias pitfall',
        'spectral-tier caution': 'spectral-tier',
        'utilization-range compilation caution': 'utilization-range compilation caution',
    }
    pscq_checklist_needles = [
        'Cover occupies only otherwise-idle service opportunities',
        'cover is cancelled or deferred',
        'never delays real work',
    ]
    pscq_roster_ok = (
        len(pscq_roster_files) == len(set(pscq_roster_files))
        and all(name in pscq_paper_norm for name in pscq_roster_files)
        and all(needle in pscq_paper_norm for needle in pscq_checklist_needles)
        and all(needle in pscq_paper_norm for needle in pscq_failure_needles.values())
        and 'bounded head-of-line blocking' in pscq_paper_norm
    )
    record('verifier PSCQ support-roster packet content', pscq_roster_ok, f'files={pscq_roster_files}; checklist_needles={pscq_checklist_needles}; failure_needles={list(pscq_failure_needles.values())}')

    pscq_support_paths = [pscq_paper_path, pscq_candidate_path]
    required_pscq_rows = {
        'packet claim': 'support packet',
        'five-file roster': 'five-file support roster',
        'padding worsens TV figure': 'fig_padding_worsens_tv.pdf',
        'idle padding partial TV figure': 'fig_idle_padding_partial_tv.pdf',
        'service bias substitution figure': 'fig_service_bias_substitution.pdf',
        'spectral dither attenuation figure': 'fig_spectral_dither_attenuation.pdf',
        'utilization range optimizer figure': 'fig_utilization_range_optimizer.pdf',
        'checklist anchor': 'cover is cancelled or deferred',
        'utilization knee caution': 'utilization-knee',
        'partial idle filling caution': 'partial-idle-filling',
        'service bias caution': 'service-bias',
        'spectral tier caution': 'spectral-tier',
        'utilization range caution': 'utilization-range',
        'CongestionEQ owner': 'Congestion-EQ',
        'PSCQ owner': 'PSC-Q',
        'W-CongestionEQ owner': 'W-Congestion-EQ',
        'Eval1 owner': 'Eval~1',
        'OperationalB owner': 'Operational~B',
        'ReleaseA owner': 'Release~A',
    }
    pscq_failures = []
    for rel in pscq_support_paths:
        active_text = (repo_root / rel).read_text(encoding='utf-8').replace('\\_', '_')
        missing = [name for name, needle in required_pscq_rows.items() if needle not in active_text]
        if missing:
            pscq_failures.append({'path': rel, 'missing': missing})
    record('active PSCQ addendum support-roster rows', not pscq_failures, f'paths={pscq_support_paths}; failures={pscq_failures}')

    owner_map_entries = list(line_item_owner_map.get('entries', [])) + list(line_item_owner_map.get('variant_entries', []))
    owner_map_names = {entry.get('name') for entry in owner_map_entries if isinstance(entry, dict)}
    receipt_names = {entry.get('name') for entry in receipt.get('line_items', []) if isinstance(entry, dict)}
    support_bundle_ids = {entry.get('bundle_id') for entry in support_bundle_map.get('bundles', []) if isinstance(entry, dict)}
    congestion_boundary_ok = (
        'congestion_epoch_contract' in owner_map_names
        and 'pscq_mechanism_packet' in owner_map_names
        and 'congestion_epoch_contract' not in receipt_names
        and 'pscq_mechanism_packet' not in receipt_names
        and 'bundle://worked-example/congestion-eq' not in support_bundle_ids
        and 'bundle://worked-example/pscq' not in support_bundle_ids
        and 'congestion_replay_packet' not in verifier_report
    )
    record('verifier congestion owner-map boundary content', congestion_boundary_ok, f'owner_map_names={sorted(name for name in owner_map_names if name in {"congestion_epoch_contract", "pscq_mechanism_packet"})}; receipt_names={sorted(receipt_names)}; support_bundle_ids={sorted(support_bundle_ids)}; verifier_report_keys={sorted(verifier_report.keys())}')

    congestion_boundary_paths = [
        'series/congestion_series/paper1_congestion_eq/paper.tex',
        'series/congestion_series/paper2_psc_q/paper.tex',
        'series/congestion_series/paper3_w_congestion_eq/paper.tex',
        'series/synthesis/paper17_worked_example_receipt_interlock/paper.tex',
        'series/synthesis/paper55_series_spines_math_to_review_handoffs/paper.tex',
        queue_note_for_source('series/congestion_series/paper1_congestion_eq/paper.tex'),
        queue_note_for_source('series/congestion_series/paper2_psc_q/paper.tex'),
        queue_note_for_source('series/congestion_series/paper3_w_congestion_eq/paper.tex'),
        'release_queue/hold/2026.03.16-paper17-worked-example-hold.md',
        'release_queue/hold/2026.03.19-paper55-series-spines-hold.md',
    ]
    congestion_required_rows = {
        'owner map route': 'owner-map',
        'line item owner map': 'example_line_item_owner_map.json',
        'receipt non-emission boundary': 'not',
    }
    forbidden_congestion_positive_snippets = [
        'now also ships one exact congestion replay packet',
        'now carries one exact replay packet in `example_verifier_report.json` under `congestion_replay_packet`',
        'now also carries one exact `pscq_mechanism_packet` in `example_receipt.json`',
        'in \nolinkurl{example_receipt.json}, \nolinkurl{pscq_mechanism_packet} fixes',
        'example_support_bundle_map.json} resolves \nolinkurl{bundle://worked-example/pscq}',
        'example_support_bundle_map.json} resolves \nolinkurl{bundle://worked-example/congestion-eq}',
        'exports \nolinkurl{congestion_epoch_contract} in \nolinkurl{example_receipt.json}',
        'carries \nolinkurl{congestion_replay_packet} in \nolinkurl{example_verifier_report.json}',
    ]
    congestion_failures = []
    for rel in congestion_boundary_paths:
        active_text = (repo_root / rel).read_text(encoding='utf-8')
        active_norm = active_text.replace('\\_', '_').replace('owner map', 'owner-map')
        missing = [name for name, needle in congestion_required_rows.items() if needle not in active_norm]
        forbidden = [snippet for snippet in forbidden_congestion_positive_snippets if snippet in active_text or snippet in active_norm]
        if missing or forbidden:
            congestion_failures.append({'path': rel, 'missing': missing, 'forbidden': forbidden})
    record('active congestion owner-map boundary rows', not congestion_failures, f'paths={congestion_boundary_paths}; failures={congestion_failures}')

    owner_map_spine_only_names = {
        'retry_schedule_packet': {
            'plan_id': 'eval-retry-schedule-v1',
            'bundle_id': 'bundle://worked-example/retry-schedule',
            'verifier_key': 'retry_schedule_packet',
        },
        'runtime_conformance_packet': {
            'plan_id': 'eval-runtime-conformance-v1',
            'bundle_id': 'bundle://worked-example/runtime-conformance',
            'verifier_key': 'runtime_conformance_packet',
        },
        'calibration_recipe_packet': {
            'plan_id': 'eval-calibration-recipe-v1',
            'bundle_id': 'bundle://worked-example/calibration-recipe',
            'verifier_key': 'calibration_recipe_packet',
        },
        'congestion_epoch_contract': {
            'plan_id': 'eval-congestion-eq-v1',
            'bundle_id': 'bundle://worked-example/congestion-eq',
            'verifier_key': 'congestion_replay_packet',
        },
        'pscq_mechanism_packet': {
            'plan_id': 'eval-pscq-v1',
            'bundle_id': 'bundle://worked-example/pscq',
            'verifier_key': 'pscq_mechanism_packet',
        },
        'bossfight_dialsheet_packet': {
            'plan_id': 'eval-bossfight-dialsheet-v1',
            'bundle_id': 'bundle://worked-example/bossfight-dialsheet',
            'verifier_key': 'bossfight_dialsheet_packet',
        },
        'bossfight_verifier_bundle': {
            'plan_id': 'eval-bossfight-verifier-v1',
            'bundle_id': 'bundle://worked-example/bossfight-verifier',
            'verifier_key': 'bossfight_verifier_packet',
        },
        'routing_signature_manifest': {
            'plan_id': 'eval-routing-signature-v1',
            'bundle_id': 'bundle://worked-example/routing-signature',
            'verifier_key': 'routing_signature_manifest',
        },
    }
    plan_catalog_ids = {entry.get('plan_id') for entry in replay_plans.get('plans', []) if isinstance(entry, dict)}
    line_item_spine_index = {entry.get('line_item_name'): entry for entry in series_spine.get('line_item_spines', []) if isinstance(entry, dict)}
    owner_map_spine_only_failures = []
    for name, spec in owner_map_spine_only_names.items():
        spine_entry = line_item_spine_index.get(name, {})
        receipt_anchor = spine_entry.get('receipt_anchor', {}) if isinstance(spine_entry, dict) else {}
        replay_anchor = spine_entry.get('replay_anchor', {}) if isinstance(spine_entry, dict) else {}
        problems = []
        if name not in owner_map_names:
            problems.append('missing-owner-map-row')
        if name in receipt_names:
            problems.append('unexpected-receipt-line-item')
        if spec['plan_id'] in plan_catalog_ids:
            problems.append('unexpected-plan-catalog-row')
        if spec['bundle_id'] in support_bundle_ids:
            problems.append('unexpected-support-bundle')
        if spec['verifier_key'] in verifier_report:
            problems.append('unexpected-verifier-packet')
        if receipt_anchor.get('materialization_status') != 'owner_map_spine_only_current_cut':
            problems.append('spine-receipt-anchor-status-not-owner-map-only')
        if receipt_anchor.get('artifact') != 'example_line_item_owner_map.json':
            problems.append('spine-receipt-anchor-not-owner-map')
        if replay_anchor.get('plan_catalog_status') != 'not_materialized_current_cut':
            problems.append('spine-replay-anchor-status-not-unmaterialized')
        if problems:
            owner_map_spine_only_failures.append({'name': name, 'problems': problems})
    record('verifier nonmaterialized owner-map route boundary content', not owner_map_spine_only_failures, f'failures={owner_map_spine_only_failures}; receipt_names={sorted(receipt_names)}; plan_catalog_ids={sorted(plan_catalog_ids)}; support_bundle_ids={sorted(support_bundle_ids)}; verifier_report_keys={sorted(verifier_report.keys())}')

    owner_map_entry_index = {entry.get('name'): entry for entry in owner_map_entries if isinstance(entry, dict)}
    required_materialized_in = ['example_line_item_owner_map.json', 'example_series_spine.json']
    required_nonpacket_fields = {
        'current_cut_role': 'owner_map_series_spine_boundary',
        'materialization_status': 'owner_map_spine_only_current_cut',
        'replay_plan_id_status': 'route_target_only_not_plan_catalog_row_current_cut',
        'public_objects_status': 'route_context_only_not_packet_materialization_evidence',
    }
    required_not_materialized_subset = {
        'example_receipt.json',
        'example_uvi.json',
        'example_verifier_report.json',
        'example_replay_plans.json',
        'example_support_bundle_map.json',
    }
    owner_map_row_status_failures = []
    for name in owner_map_spine_only_names:
        row = owner_map_entry_index.get(name, {})
        problems = []
        for field, expected in required_nonpacket_fields.items():
            if row.get(field) != expected:
                problems.append(f'{field}-mismatch')
        if row.get('materialized_in_current_cut') != required_materialized_in:
            problems.append('materialized-in-current-cut-mismatch')
        not_materialized_set = set(row.get('not_materialized_as_packet_in', []))
        if not required_not_materialized_subset.issubset(not_materialized_set):
            problems.append('not-materialized-subset-missing')
        if 'route-context labels, not evidence' not in row.get('boundary_note', ''):
            problems.append('boundary-note-missing-context-warning')
        spine_entry = line_item_spine_index.get(name, {})
        receipt_anchor = spine_entry.get('receipt_anchor', {}) if isinstance(spine_entry, dict) else {}
        replay_anchor = spine_entry.get('replay_anchor', {}) if isinstance(spine_entry, dict) else {}
        if receipt_anchor.get('public_objects_status') != 'route_context_only_not_packet_materialization_evidence':
            problems.append('spine-receipt-anchor-public-objects-status-mismatch')
        if replay_anchor.get('replay_plan_id_status') != 'route_target_only_not_plan_catalog_row_current_cut':
            problems.append('spine-replay-anchor-plan-id-status-mismatch')
        if problems:
            owner_map_row_status_failures.append({'name': name, 'problems': problems})
    record('verifier owner-map row status fields', not owner_map_row_status_failures, f'failures={owner_map_row_status_failures}')

    receipt_item_index = {entry.get('name'): entry for entry in receipt.get('line_items', []) if isinstance(entry, dict)}
    replay_plan_index = {entry.get('plan_id'): entry for entry in replay_plans.get('plans', []) if isinstance(entry, dict)}
    support_bundle_index = {entry.get('bundle_id'): entry for entry in support_bundle_map.get('bundles', []) if isinstance(entry, dict)}
    base_receipt_specs = {
        'primary_path_declaration': {
            'plan_id': 'eval-primary-v1',
            'bundle_id': 'bundle://worked-example/primary',
            'required_public': {'example_receipt.json', 'example_release_receipt.json', 'example_primary_surface_manifest.json', 'example_state_decl.json', 'example_replay_plans.json', 'example_support_bundle_map.json'},
            'required_artifacts': ['example_receipt.json', 'example_release_receipt.json', 'example_primary_surface_manifest.json'],
        },
        'fallback_contact_surface': {
            'plan_id': 'eval-fallback-cct-v1',
            'bundle_id': 'bundle://worked-example/fallback-cct',
            'required_public': {'example_receipt.json', 'example_state_decl.json', 'example_effective_surface_resolution.json', 'example_replay_plans.json', 'example_support_bundle_map.json'},
            'required_artifacts': ['example_receipt.json', 'example_state_decl.json'],
        },
        'fallback_tiered_vector': {
            'plan_id': 'eval-fallback-vector-v1',
            'bundle_id': 'bundle://worked-example/fallback-vector',
            'required_public': {'example_receipt.json', 'example_state_decl.json', 'example_replay_plans.json', 'example_support_bundle_map.json'},
            'required_artifacts': ['example_receipt.json', 'example_state_decl.json', 'example_support_bundle_map.json'],
        },
        'path_selection_indicator': {
            'plan_id': 'eval-pathselect-v1',
            'bundle_id': 'bundle://worked-example/pathselect',
            'required_public': {'example_receipt.json', 'example_state_decl.json', 'example_change_control.json', 'example_compare_profile.json', 'example_replay_plans.json', 'example_support_bundle_map.json'},
            'required_artifacts': ['example_receipt.json', 'example_state_decl.json', 'example_change_control.json'],
        },
        'profiling_equalization': {
            'plan_id': 'eval-profiling-eq-v1',
            'bundle_id': 'bundle://worked-example/profiling-eq',
            'required_public': {'example_receipt.json', 'example_profiling_evidence.json', 'example_replay_plans.json', 'example_support_bundle_map.json'},
            'required_artifacts': ['example_receipt.json', 'example_profiling_evidence.json'],
        },
    }
    base_receipt_owner_failures = []
    for name, spec in base_receipt_specs.items():
        row = owner_map_entry_index.get(name, {})
        item = receipt_item_index.get(name, {})
        spine_entry = line_item_spine_index.get(name, {})
        receipt_anchor = spine_entry.get('receipt_anchor', {}) if isinstance(spine_entry, dict) else {}
        replay_anchor = spine_entry.get('replay_anchor', {}) if isinstance(spine_entry, dict) else {}
        support_anchor = spine_entry.get('support_anchor', {}) if isinstance(spine_entry, dict) else {}
        bundle = support_bundle_index.get(spec['bundle_id'], {})
        hook = item.get('replay_hook', {}) if isinstance(item, dict) else {}
        problems = []
        if not row:
            problems.append('missing-owner-map-row')
        if not item:
            problems.append('missing-receipt-line-item')
        if row.get('materialization_status') != 'base_receipt_current_cut':
            problems.append('owner-materialization-status')
        if row.get('receipt_file') != 'example_receipt.json':
            problems.append('owner-receipt-file')
        if row.get('replay_plan_id') != spec['plan_id']:
            problems.append('owner-replay-plan-id')
        if row.get('support_bundle_id') != spec['bundle_id']:
            problems.append('owner-support-bundle-id')
        expected_plan_spec_id = replay_plan_index.get(spec['plan_id'], {}).get('plan_spec_id')
        if row.get('plan_spec_id') != expected_plan_spec_id:
            problems.append('owner-plan-spec-id')
        if row.get('support_consumed_by') != [spec['plan_id']]:
            problems.append('owner-support-consumed-by')
        if row.get('support_required_artifacts') != spec['required_artifacts']:
            problems.append('owner-support-required-artifacts')
        if row.get('support_pointers') != bundle.get('support_pointers'):
            problems.append('owner-support-pointers')
        missing_public = sorted(spec['required_public'] - set(row.get('public_objects', [])))
        if missing_public:
            problems.append(f'owner-public-objects-missing:{missing_public}')
        if hook.get('plan_id') != spec['plan_id']:
            problems.append('receipt-hook-plan-id')
        if hook.get('artifact_bundle') != spec['bundle_id']:
            problems.append('receipt-hook-artifact-bundle')
        if hook.get('plan_spec_id') != row.get('plan_spec_id'):
            problems.append('receipt-hook-owner-plan-spec-mismatch')
        if spec['plan_id'] not in replay_plan_index:
            problems.append('missing-replay-plan-catalog-row')
        if bundle.get('consumed_by') != [spec['plan_id']]:
            problems.append('support-consumed-by')
        if bundle.get('required_artifacts') != spec['required_artifacts']:
            problems.append('support-required-artifacts')
        if receipt_anchor.get('artifact') != 'example_receipt.json':
            problems.append('spine-receipt-anchor-artifact')
        if receipt_anchor.get('materialization_status') != 'base_receipt_current_cut':
            problems.append('spine-receipt-anchor-status')
        if receipt_anchor.get('support_bundle_id') != spec['bundle_id']:
            problems.append('spine-receipt-anchor-support-bundle')
        if replay_anchor.get('support_bundle_id') != spec['bundle_id'] or replay_anchor.get('artifact_bundle') != spec['bundle_id']:
            problems.append('spine-replay-anchor-support-bundle')
        if replay_anchor.get('plan_spec_id') != row.get('plan_spec_id'):
            problems.append('spine-replay-anchor-plan-spec-id')
        if support_anchor.get('support_bundle_id') != spec['bundle_id']:
            problems.append('spine-support-anchor-bundle')
        if support_anchor.get('required_artifacts') != spec['required_artifacts']:
            problems.append('spine-support-anchor-required-artifacts')
        if support_anchor.get('support_pointers') != row.get('support_pointers'):
            problems.append('spine-support-anchor-support-pointers')
        if problems:
            base_receipt_owner_failures.append({'name': name, 'problems': problems})
    record('verifier base receipt owner-map support rows', not base_receipt_owner_failures, f'failures={base_receipt_owner_failures}')

    verifier_plan_rows = [entry for entry in verifier_report.get('plans_checked', []) if isinstance(entry, dict)]
    verifier_plan_ids = [entry.get('plan_id') for entry in verifier_plan_rows]
    verifier_plan_by_id = {entry.get('plan_id'): entry for entry in verifier_plan_rows}
    verifier_plan_spec_by_id = {
        plan_id: entry.get('plan_spec_id')
        for plan_id, entry in verifier_plan_by_id.items()
    }
    verifier_support_artifacts = verifier_report.get('support_artifacts', {}) if isinstance(verifier_report, dict) else {}
    base_plan_closure_failures = []
    for name, spec in base_receipt_specs.items():
        plan_id = spec['plan_id']
        expected_plan_spec_id = replay_plan_index.get(plan_id, {}).get('plan_spec_id')
        if plan_id not in verifier_plan_ids:
            base_plan_closure_failures.append({'name': name, 'problem': 'missing-from-verifier-plans_checked', 'plan_id': plan_id})
        elif verifier_plan_spec_by_id.get(plan_id) != expected_plan_spec_id:
            base_plan_closure_failures.append({'name': name, 'problem': 'verifier-plan-spec-mismatch', 'plan_id': plan_id, 'actual': verifier_plan_spec_by_id.get(plan_id), 'expected': expected_plan_spec_id})
    if verifier_support_artifacts.get('profiling_evidence_digest') != profiling_evidence_digest:
        base_plan_closure_failures.append({'name': 'profiling_equalization', 'problem': 'profiling-evidence-digest-missing-or-mismatch', 'actual': verifier_support_artifacts.get('profiling_evidence_digest'), 'expected': profiling_evidence_digest})
    record('verifier base receipt plans-checked closure', not base_plan_closure_failures, f'plans_checked={verifier_plan_ids}; profiling_evidence_digest={profiling_evidence_digest}; failures={base_plan_closure_failures}')

    base_plan_payload_failures = []
    for name, spec in base_receipt_specs.items():
        plan_id = spec['plan_id']
        verifier_entry = verifier_plan_by_id.get(plan_id, {})
        owner_row = owner_map_entry_index.get(name, {})
        bundle = support_bundle_index.get(spec['bundle_id'], {})
        expected_payload = {
            'line_item_name': name,
            'receipt_file': 'example_receipt.json',
            'support_bundle_id': spec['bundle_id'],
            'support_consumed_by': bundle.get('consumed_by'),
            'support_required_artifacts': bundle.get('required_artifacts'),
            'support_pointers': bundle.get('support_pointers'),
            'public_objects': owner_row.get('public_objects'),
        }
        problems = []
        if not verifier_entry:
            problems.append('missing-verifier-plan-entry')
        for field, expected in expected_payload.items():
            if verifier_entry.get(field) != expected:
                problems.append(f'{field}:{verifier_entry.get(field)}!={expected}')
        if set(verifier_entry.get('support_required_artifacts', [])) - set(verifier_entry.get('public_objects', [])):
            problems.append('verifier-support-required-artifacts-not-public')
        if verifier_entry.get('support_required_artifacts') != owner_row.get('support_required_artifacts'):
            problems.append('verifier-owner-support-required-artifacts-mismatch')
        if verifier_entry.get('support_pointers') != owner_row.get('support_pointers'):
            problems.append('verifier-owner-support-pointers-mismatch')
        if problems:
            base_plan_payload_failures.append({'name': name, 'plan_id': plan_id, 'problems': problems})
    record('verifier base receipt plans-checked support payload closure', not base_plan_payload_failures, f'failures={base_plan_payload_failures}')

    base_plan_digest_failures = []
    def expected_public_object_digest_entries(paths):
        entries = []
        for relpath in paths:
            path = ART / relpath
            entries.append({
                'path': relpath,
                'sha256': sha256_bytes(path.read_bytes()) if path.exists() else None,
            })
        return entries
    for name, spec in base_receipt_specs.items():
        plan_id = spec['plan_id']
        verifier_entry = verifier_plan_by_id.get(plan_id, {})
        public_objects = verifier_entry.get('public_objects', [])
        actual_digest_entries = verifier_entry.get('public_object_digest_entries')
        expected_digest_entries = expected_public_object_digest_entries(public_objects)
        problems = []
        if actual_digest_entries != expected_digest_entries:
            problems.append({'public_object_digest_entries': actual_digest_entries, 'expected': expected_digest_entries})
        missing_digest_paths = [entry.get('path') for entry in actual_digest_entries or [] if not entry.get('sha256')]
        if missing_digest_paths:
            problems.append({'missing_digest_paths': missing_digest_paths})
        if problems:
            base_plan_digest_failures.append({'name': name, 'plan_id': plan_id, 'problems': problems})
    record('verifier base receipt public-object digest closure', not base_plan_digest_failures, f'failures={base_plan_digest_failures}')

    def expected_verifier_contract(entry):
        plan_id = entry.get('plan_id')
        return {
            'contract_version': 'worked-example-verifier-contract-v2',
            'proof_carrying_status': 'formal_exact_rational_budget_closure_log_endpoint_derivations_and_profiling_cp_union_bound_present',
            'arithmetic_mode': 'exact_rational_decimal_budget_closure plus exact_rational_integer_series_log_endpoint_derivations plus exact_rational_binomial_tail_profiling_envelope; python3_json_float_diagnostic_smoke excluded from formal proof',
            'formal_acceptance_rule': 'The formal_rational_verifier_bundle parses public decimal budget endpoints as exact fractions, transcendental_endpoint_derivation_bundle proves maintained log2 endpoint upper bounds with integer/rational series certificates, and profiling_statistical_derivation_bundle proves the base profiling eta/delta envelope with exact binomial-tail and log-ratio inequalities under a fixed-sample stop/refresh lock; host-float recomputation remains diagnostic smoke.',
            'log_units': 'bits_log2_where_numeric_budget_rows_are_used',
            'canonical_input_order': entry.get('public_objects', []),
            'public_object_digest_binding': 'public_object_digest_entries',
            'evaluator_source': '../tools/validate_example.py',
            'evaluator_source_sha256': sha256_bytes((ROOT / 'tools/validate_example.py').read_bytes()),
            'materializer_source': '../tools/materialize_example.py',
            'materializer_source_sha256': sha256_bytes((ROOT / 'tools/materialize_example.py').read_bytes()),
            'plan_spec_id': entry.get('plan_spec_id'),
            'support_pointer_status': 'on_request_support_pointers_not_in_archive',
        }

    base_plan_contract_failures = []
    for name, spec in base_receipt_specs.items():
        plan_id = spec['plan_id']
        verifier_entry = verifier_plan_by_id.get(plan_id, {})
        problems = []
        if not verifier_entry:
            problems.append('missing-verifier-plan-entry')
        else:
            contract = verifier_entry.get('verifier_contract')
            expected_contract = expected_verifier_contract(verifier_entry)
            if contract != expected_contract:
                problems.append({'verifier_contract': contract, 'expected': expected_contract})
            if contract and contract.get('canonical_input_order') != verifier_entry.get('public_objects'):
                problems.append('canonical-input-order-public-objects-mismatch')
            if contract and contract.get('public_object_digest_binding') != 'public_object_digest_entries':
                problems.append('public-object-digest-binding-token')
        if problems:
            base_plan_contract_failures.append({'name': name, 'plan_id': plan_id, 'problems': problems})
    record('verifier base receipt contract boundary closure', not base_plan_contract_failures, f'failures={base_plan_contract_failures}')

    def dec_fraction(value):
        if not isinstance(value, str) or not re.fullmatch(r'-?\d+(?:\.\d+)?', value):
            raise ValueError(f'not-a-decimal-string:{value!r}')
        return Fraction(value)

    def payload_fraction(payload):
        if not isinstance(payload, dict):
            raise ValueError(f'not-a-fraction-payload:{payload!r}')
        return Fraction(int(payload.get('numerator')), int(payload.get('denominator')))

    def fraction_payload(value):
        return {'numerator': str(value.numerator), 'denominator': str(value.denominator)}

    def ln2_bounds_via_atanh(terms):
        partial = Fraction(0)
        for k in range(terms):
            partial += Fraction(1, (2 * k + 1) * (3 ** (2 * k + 1)))
        n = terms
        tail = Fraction(1, (2 * n + 1) * (3 ** (2 * n + 1))) * Fraction(9, 8)
        return 2 * partial, 2 * (partial + tail)

    def ln1p_upper_alt(x, terms):
        if terms % 2 == 0:
            terms += 1
        acc = Fraction(0)
        power = x
        for k in range(1, terms + 1):
            term = power / k
            acc = acc + term if k % 2 else acc - term
            power *= x
        return acc

    def exp_upper_taylor(x, terms):
        acc = Fraction(1)
        term = Fraction(1)
        for k in range(1, terms + 1):
            term *= x
            term /= k
            acc += term
        first_omitted = term * x / Fraction(terms + 1)
        ratio_bound = x / Fraction(terms + 2)
        if not ratio_bound < 1:
            raise ValueError('exp-tail-ratio-not-less-than-one')
        return acc + first_omitted / (1 - ratio_bound)

    def ln_ratio_upper_atanh(numerator, denominator, terms):
        if not numerator >= denominator > 0:
            raise ValueError('ln-ratio-domain')
        z = (numerator - denominator) / (numerator + denominator)
        partial = Fraction(0)
        for k in range(terms):
            partial += Fraction(2, 1) * (z ** (2 * k + 1)) / (2 * k + 1)
        tail = Fraction(2, 1) * (z ** (2 * terms + 1)) / ((2 * terms + 1) * (1 - z * z))
        return partial + tail

    def binomial_tail_ge_le_alpha_decimal(n, x, p_decimal, alpha_num=1, alpha_den=3000):
        frac = dec_fraction(p_decimal)
        if frac == 0:
            return x > 0
        if frac == 1:
            return x <= 0 and alpha_den <= alpha_num
        a = frac.numerator
        d = frac.denominator
        q = d - a
        term = pow(q, n)
        total = 0
        denom_pow = pow(d, n)
        for i in range(0, n + 1):
            if i >= x:
                total += term
            if i == n:
                break
            term = term * (n - i) * a // ((i + 1) * q)
        return total * alpha_den <= alpha_num * denom_pow

    def binomial_cdf_le_alpha_decimal(n, x, p_decimal, alpha_num=1, alpha_den=3000):
        frac = dec_fraction(p_decimal)
        if frac == 0:
            return x < 0 and alpha_den <= alpha_num
        if frac == 1:
            return x >= n and alpha_den <= alpha_num
        a = frac.numerator
        d = frac.denominator
        q = d - a
        term = pow(q, n)
        total = 0
        denom_pow = pow(d, n)
        for i in range(0, n + 1):
            if i <= x:
                total += term
            else:
                break
            if i == n:
                break
            term = term * (n - i) * a // ((i + 1) * q)
        return total * alpha_den <= alpha_num * denom_pow

    def pow2_witness_upper_fraction(witness):
        exponent = payload_fraction(witness.get('exponent_fraction'))
        bits = int(witness.get('upper_dyadic_denominator_power_of_two'))
        numerator = int(witness.get('upper_dyadic_numerator'))
        if not pow(numerator, exponent.denominator) >= (1 << (exponent.numerator + bits * exponent.denominator)):
            raise ValueError('pow2-upper-integer-witness-failed')
        return Fraction(numerator, 1 << bits)

    formal_bundle = verifier_report.get('formal_rational_verifier_bundle', {}) if isinstance(verifier_report, dict) else {}
    formal_failures = []
    if formal_bundle.get('bundle_id') != 'worked-example-rational-budget-closure-v1':
        formal_failures.append({'bundle_id': formal_bundle.get('bundle_id')})
    if formal_bundle.get('arithmetic_mode') != 'exact_rational_decimal_strings_no_float_tolerance':
        formal_failures.append({'arithmetic_mode': formal_bundle.get('arithmetic_mode')})
    if formal_bundle.get('proof_carrying_status') != 'formal_exact_rational_budget_closure_log_endpoint_derivations_and_profiling_cp_union_bound_present':
        formal_failures.append({'proof_carrying_status': formal_bundle.get('proof_carrying_status')})
    if formal_bundle.get('accepted') is not True:
        formal_failures.append({'accepted': formal_bundle.get('accepted')})
    receipt_by_name = {row.get('name'): row for row in receipt.get('line_items', []) if isinstance(row, dict)}
    expected_scalar = {
        'primary_path_declaration': ('eval-primary-v1', '0.000000000000'),
        'fallback_contact_surface': ('eval-fallback-cct-v1', '0.046533410000'),
        'path_selection_indicator': ('eval-pathselect-v1', '0.263034405834'),
    }
    expected_summary = ('eval-total-summary-v1', '0.265904562929')
    scalar_by_name = {row.get('line_item_name'): row for row in formal_bundle.get('scalar_rows', []) if isinstance(row, dict)}
    for name, (plan_id, expected_decimal) in expected_scalar.items():
        row = scalar_by_name.get(name, {})
        try:
            p_plus = dec_fraction(row.get('p_plus_decimal'))
            declared = dec_fraction(row.get('declared_upper_decimal'))
            receipt_decimal = dec_fraction(row.get('receipt_budget_decimal'))
            receipt_budget = receipt_by_name.get(name, {}).get('budget_value')
            receipt_budget_fraction = dec_fraction(str(receipt_budget))
            expected = dec_fraction(expected_decimal)
            if not (row.get('plan_id') == plan_id and p_plus <= declared <= receipt_decimal and receipt_decimal == receipt_budget_fraction == expected and row.get('accepted') is True):
                formal_failures.append({'scalar_row': name, 'row': row, 'receipt_budget': receipt_budget})
        except Exception as exc:
            formal_failures.append({'scalar_row': name, 'exception': str(exc), 'row': row})
    summary_row = scalar_by_name.get('release_summary_envelope', {})
    try:
        p_plus = dec_fraction(summary_row.get('p_plus_decimal'))
        declared = dec_fraction(summary_row.get('declared_upper_decimal'))
        receipt_decimal = dec_fraction(summary_row.get('receipt_budget_decimal'))
        expected = dec_fraction(expected_summary[1])
        if not (summary_row.get('plan_id') == expected_summary[0] and p_plus <= declared <= receipt_decimal and receipt_decimal == expected and summary_row.get('accepted') is True):
            formal_failures.append({'summary_row': summary_row})
    except Exception as exc:
        formal_failures.append({'summary_row_exception': str(exc), 'row': summary_row})

    vector_rows = formal_bundle.get('vector_rows', [])
    vector_row = vector_rows[0] if len(vector_rows) == 1 and isinstance(vector_rows[0], dict) else {}
    try:
        terms = [dec_fraction(x) for x in vector_row.get('term_upper_decimals', [])]
        declared = dec_fraction(vector_row.get('declared_upper_decimal'))
        receipt_decimal = dec_fraction(vector_row.get('receipt_budget_decimal'))
        receipt_budget = dec_fraction(str(receipt_by_name.get('fallback_tiered_vector', {}).get('budget_value')))
        if not (vector_row.get('plan_id') == 'eval-fallback-vector-v1' and sum(terms, Fraction(0)) == declared <= receipt_decimal == receipt_budget == dec_fraction('0.056345507023') and vector_row.get('accepted') is True):
            formal_failures.append({'vector_row': vector_row, 'receipt_budget': str(receipt_by_name.get('fallback_tiered_vector', {}).get('budget_value'))})
    except Exception as exc:
        formal_failures.append({'vector_row_exception': str(exc), 'row': vector_row})

    eta_rows = formal_bundle.get('eta_delta_rows', [])
    eta_row = eta_rows[0] if len(eta_rows) == 1 and isinstance(eta_rows[0], dict) else {}
    try:
        eta_plus = dec_fraction(eta_row.get('eta_plus_decimal'))
        eta_receipt = dec_fraction(eta_row.get('eta_receipt_decimal'))
        delta_plus = dec_fraction(eta_row.get('delta_plus_decimal'))
        delta_receipt = dec_fraction(eta_row.get('delta_receipt_decimal'))
        profiling_budget = receipt_by_name.get('profiling_equalization', {}).get('budget_value', {})
        if not (eta_row.get('plan_id') == 'eval-profiling-eq-v1' and eta_plus <= eta_receipt == dec_fraction(str(profiling_budget.get('eta_bits'))) == dec_fraction('0.82176') and delta_plus <= delta_receipt == dec_fraction(str(profiling_budget.get('delta'))) and eta_row.get('accepted') is True):
            formal_failures.append({'eta_delta_row': eta_row, 'profiling_budget': profiling_budget})
    except Exception as exc:
        formal_failures.append({'eta_delta_row_exception': str(exc), 'row': eta_row})

    tool_digests = formal_bundle.get('tool_source_digests', {}) if isinstance(formal_bundle, dict) else {}
    if tool_digests.get('evaluator_source_sha256') != sha256_bytes((ROOT / 'tools/validate_example.py').read_bytes()):
        formal_failures.append('formal-bundle-evaluator-digest-mismatch')
    if tool_digests.get('materializer_source_sha256') != sha256_bytes((ROOT / 'tools/materialize_example.py').read_bytes()):
        formal_failures.append('formal-bundle-materializer-digest-mismatch')
    record('verifier formal rational budget-closure certificate', not formal_failures, f'failures={formal_failures}')

    transcendental_bundle = verifier_report.get('transcendental_endpoint_derivation_bundle', {}) if isinstance(verifier_report, dict) else {}
    transcendental_failures = []
    try:
        if transcendental_bundle.get('bundle_id') != 'worked-example-log-endpoint-derivation-v1':
            transcendental_failures.append({'bundle_id': transcendental_bundle.get('bundle_id')})
        if transcendental_bundle.get('arithmetic_mode') != 'exact_rational_integer_series_bounds_no_float_tolerance':
            transcendental_failures.append({'arithmetic_mode': transcendental_bundle.get('arithmetic_mode')})
        if transcendental_bundle.get('proof_carrying_status') != 'formal_exact_rational_budget_closure_log_endpoint_derivations_and_profiling_cp_union_bound_present':
            transcendental_failures.append({'proof_carrying_status': transcendental_bundle.get('proof_carrying_status')})
        ln2_bound = transcendental_bundle.get('ln2_bound', {})
        ln2_terms = ln2_bound.get('terms')
        ln2_lower, ln2_upper = ln2_bounds_via_atanh(int(ln2_terms))
        if payload_fraction(ln2_bound.get('lower_bound_fraction')) != ln2_lower:
            transcendental_failures.append('ln2-lower-bound-mismatch')
        if payload_fraction(ln2_bound.get('upper_bound_fraction')) != ln2_upper:
            transcendental_failures.append('ln2-upper-bound-mismatch')

        expected_raw_rows = {
            'CSET': ('1.4', '0.046533410000'),
            'TIME': ('0.3', '0.006654049337'),
            'CONG': ('0.15', '0.003158047686'),
        }
        raw_rows = {row.get('tier'): row for row in transcendental_bundle.get('raw_fallback_rows', []) if isinstance(row, dict)}
        for tier, (raw_decimal, upper_decimal) in expected_raw_rows.items():
            row = raw_rows.get(tier, {})
            pow2_upper = pow2_witness_upper_fraction(row.get('pow2_raw_b_upper_witness', {}))
            y_upper = dec_fraction('0.02') * (pow2_upper - 1)
            log1p_terms = int(row.get('log1p_upper_terms'))
            lhs = ln1p_upper_alt(y_upper, log1p_terms)
            rhs = dec_fraction(upper_decimal) * ln2_lower
            if not (row.get('raw_b_decimal') in {raw_decimal, str(float(raw_decimal))} and row.get('public_effective_bits_upper_decimal') == upper_decimal and payload_fraction(row.get('y_upper_fraction')) == y_upper and lhs <= rhs and row.get('accepted') is True):
                transcendental_failures.append({'raw_row': tier, 'row': row, 'lhs_le_rhs': lhs <= rhs})

        selection_row = transcendental_bundle.get('selection_tax_row', {})
        selection_y = dec_fraction('0.2')
        selection_lhs = ln1p_upper_alt(selection_y, int(selection_row.get('log1p_upper_terms')))
        selection_rhs = dec_fraction('0.263034405834') * ln2_lower
        if not (selection_row.get('selection_tax_bits_upper_decimal') == '0.263034405834' and payload_fraction(selection_row.get('y_upper_fraction')) == selection_y and selection_lhs <= selection_rhs and selection_row.get('accepted') is True):
            transcendental_failures.append({'selection_row': selection_row, 'lhs_le_rhs': selection_lhs <= selection_rhs})

        total_row = transcendental_bundle.get('total_summary_row', {})
        fallback_summary_upper = dec_fraction('0.056345507023')
        selection_upper = dec_fraction('0.263034405834')
        total_upper = dec_fraction('0.265904562929')
        residual_bits = total_upper - selection_upper
        exp_argument_upper = fallback_summary_upper * ln2_upper
        exp_upper = exp_upper_taylor(exp_argument_upper, int(total_row.get('exp_upper_terms')))
        total_y_upper = dec_fraction('0.05') * (exp_upper - 1)
        total_lhs = ln1p_upper_alt(total_y_upper, int(total_row.get('log1p_upper_terms')))
        total_rhs = residual_bits * ln2_lower
        if not (payload_fraction(total_row.get('exp_argument_upper_fraction')) == exp_argument_upper and payload_fraction(total_row.get('exp_fallback_summary_upper_fraction')) == exp_upper and payload_fraction(total_row.get('y_upper_fraction')) == total_y_upper and total_lhs <= total_rhs and total_row.get('accepted') is True):
            transcendental_failures.append({'total_summary_row': total_row, 'lhs_le_rhs': total_lhs <= total_rhs})
        if transcendental_bundle.get('accepted') is not True:
            transcendental_failures.append({'accepted': transcendental_bundle.get('accepted')})
    except Exception as exc:
        transcendental_failures.append({'exception': str(exc)})
    record('verifier transcendental endpoint derivation certificate', not transcendental_failures, f'failures={transcendental_failures}')

    profiling_bundle = verifier_report.get('profiling_statistical_derivation_bundle', {}) if isinstance(verifier_report, dict) else {}
    profiling_stat_failures = []
    try:
        if profiling_bundle.get('bundle_id') != 'worked-example-profiling-cp-union-bound-v1':
            profiling_stat_failures.append({'bundle_id': profiling_bundle.get('bundle_id')})
        if profiling_bundle.get('arithmetic_mode') != 'exact_rational_binomial_tail_and_log_ratio_bounds_no_float_tolerance':
            profiling_stat_failures.append({'arithmetic_mode': profiling_bundle.get('arithmetic_mode')})
        if profiling_bundle.get('proof_carrying_status') != 'formal_exact_rational_budget_closure_log_endpoint_derivations_and_profiling_cp_union_bound_present':
            profiling_stat_failures.append({'proof_carrying_status': profiling_bundle.get('proof_carrying_status')})
        if profiling_bundle.get('projection') != 'retry_bucket_trace':
            profiling_stat_failures.append({'projection': profiling_bundle.get('projection')})

        profiling_evidence_body = profiling_evidence.get('evidence', {}) if isinstance(profiling_evidence, dict) else {}
        profiling_summary = profiling_evidence_body.get('certificate_summary', {}) if isinstance(profiling_evidence_body, dict) else {}
        classes = sorted((profiling_evidence_body.get('classes') or {}).keys())
        table = profiling_evidence_body.get('table', []) if isinstance(profiling_evidence_body.get('table'), list) else []
        bin_names = [row.get('bin') for row in table if isinstance(row, dict)]
        cell_count = len(classes) * len(bin_names)
        if profiling_bundle.get('cell_count') != cell_count:
            profiling_stat_failures.append({'cell_count': profiling_bundle.get('cell_count'), 'expected': cell_count})
        alpha_per_cell = payload_fraction(profiling_bundle.get('alpha_per_cell_fraction'))
        tail_alpha = payload_fraction(profiling_bundle.get('two_sided_tail_alpha_fraction'))
        delta_stat = payload_fraction(profiling_bundle.get('delta_stat_fraction'))
        if not (alpha_per_cell == Fraction(1, 1500) and tail_alpha == Fraction(1, 3000) and delta_stat == Fraction(1, 100) and cell_count * alpha_per_cell <= delta_stat and profiling_bundle.get('union_bound_accepted') is True):
            profiling_stat_failures.append({'union_bound': {'cell_count': cell_count, 'alpha_per_cell': str(alpha_per_cell), 'tail_alpha': str(tail_alpha), 'delta_stat': str(delta_stat), 'accepted': profiling_bundle.get('union_bound_accepted')}})

        interval_rows = {row.get('row_id'): row for row in profiling_bundle.get('interval_rows', []) if isinstance(row, dict)}
        lower_by_class_bin = {}
        upper_by_class_bin = {}
        for ev_row in table:
            if not isinstance(ev_row, dict):
                continue
            bin_name = ev_row.get('bin')
            counts = ev_row.get('count', {}) if isinstance(ev_row.get('count'), dict) else {}
            decs = ev_row.get('cp_interval_decimal', {}) if isinstance(ev_row.get('cp_interval_decimal'), dict) else {}
            for klass in classes:
                row_id = f'{klass}:{bin_name}'
                cert = interval_rows.get(row_id, {})
                pair = decs.get(klass)
                if not (isinstance(pair, list) and len(pair) == 2):
                    profiling_stat_failures.append({'interval_decimal_missing': row_id})
                    continue
                lo_s, hi_s = pair
                count = int(counts.get(klass))
                n = int((profiling_evidence_body.get('classes', {}).get(klass, {}) or {}).get('n'))
                lower_ok = count == 0 or binomial_tail_ge_le_alpha_decimal(n, count, lo_s)
                upper_ok = count == n or binomial_cdf_le_alpha_decimal(n, count, hi_s)
                lower_by_class_bin[(klass, bin_name)] = dec_fraction(lo_s)
                upper_by_class_bin[(klass, bin_name)] = dec_fraction(hi_s)
                if not (cert.get('class') == klass and cert.get('bin') == bin_name and cert.get('n') == n and cert.get('count') == count and cert.get('lower_decimal') == lo_s and cert.get('upper_decimal') == hi_s and lower_ok and upper_ok and cert.get('accepted') is True):
                    profiling_stat_failures.append({'interval_row': row_id, 'cert': cert, 'lower_ok': lower_ok, 'upper_ok': upper_ok})

        rare_bins = []
        for bin_name in bin_names:
            if min(lower_by_class_bin[(klass, bin_name)] for klass in classes) == 0:
                rare_bins.append(bin_name)
        rare_support = profiling_bundle.get('rare_support', {}) if isinstance(profiling_bundle.get('rare_support'), dict) else {}
        if rare_support.get('rare_bins') != rare_bins or profiling_summary.get('rare_bins') != rare_bins:
            profiling_stat_failures.append({'rare_bins': rare_support.get('rare_bins'), 'summary': profiling_summary.get('rare_bins'), 'expected': rare_bins})
        rare_mass_rows = {row.get('class'): row for row in rare_support.get('rare_mass_rows', []) if isinstance(row, dict)}
        delta_plus = max(sum(upper_by_class_bin[(klass, bin_name)] for bin_name in rare_bins) for klass in classes)
        delta_plus_public = dec_fraction(rare_support.get('delta_plus_decimal'))
        delta_public = dec_fraction(rare_support.get('delta_public_decimal'))
        receipt_profile_budget = receipt_by_name.get('profiling_equalization', {}).get('budget_value', {})
        if not (delta_plus <= delta_plus_public <= delta_public == dec_fraction(str(receipt_profile_budget.get('delta'))) == dec_fraction('0.007464') and rare_support.get('accepted') is True):
            profiling_stat_failures.append({'delta': {'computed': str(delta_plus), 'plus': rare_support.get('delta_plus_decimal'), 'public': rare_support.get('delta_public_decimal'), 'receipt': receipt_profile_budget}})
        for klass in classes:
            mass = sum(upper_by_class_bin[(klass, bin_name)] for bin_name in rare_bins)
            row = rare_mass_rows.get(klass, {})
            if dec_fraction(row.get('rare_mass_upper_decimal')) != mass:
                profiling_stat_failures.append({'rare_mass_row': klass, 'row': row, 'expected': str(mass)})

        ln2_bound = profiling_bundle.get('ln2_bound', {})
        ln2_lower, _ln2_upper = ln2_bounds_via_atanh(int(ln2_bound.get('terms')))
        if payload_fraction(ln2_bound.get('lower_bound_fraction')) != ln2_lower:
            profiling_stat_failures.append('profiling-ln2-lower-bound-mismatch')
        ratio_rows = {row.get('row_id'): row for row in profiling_bundle.get('ratio_rows', []) if isinstance(row, dict)}
        eta_public = dec_fraction(profiling_bundle.get('eta_public_decimal'))
        eta_rhs = eta_public * ln2_lower
        expected_ratio_ids = []
        for bin_name in bin_names:
            if bin_name in rare_bins:
                continue
            for numerator_class in classes:
                for denominator_class in classes:
                    if numerator_class == denominator_class:
                        continue
                    row_id = f'{numerator_class}_over_{denominator_class}:{bin_name}'
                    expected_ratio_ids.append(row_id)
                    row = ratio_rows.get(row_id, {})
                    numerator_upper = upper_by_class_bin[(numerator_class, bin_name)]
                    denominator_lower = lower_by_class_bin[(denominator_class, bin_name)]
                    lhs = ln_ratio_upper_atanh(numerator_upper, denominator_lower, int(row.get('ln_ratio_upper_terms', 0)))
                    if not (row.get('bin') == bin_name and row.get('numerator_class') == numerator_class and row.get('denominator_class') == denominator_class and dec_fraction(row.get('numerator_upper_decimal')) == numerator_upper and dec_fraction(row.get('denominator_lower_decimal')) == denominator_lower and dec_fraction(row.get('eta_public_decimal')) == eta_public and lhs <= eta_rhs and row.get('accepted') is True):
                        profiling_stat_failures.append({'ratio_row': row_id, 'row': row, 'lhs_le_rhs': lhs <= eta_rhs})
        if sorted(ratio_rows) != sorted(expected_ratio_ids):
            profiling_stat_failures.append({'ratio_row_ids': sorted(ratio_rows), 'expected': sorted(expected_ratio_ids)})
        if not (eta_public == dec_fraction(str(receipt_profile_budget.get('eta_bits'))) == dec_fraction('0.82176') and profiling_summary.get('eta_plus_decimal') == '0.821760'):
            profiling_stat_failures.append({'eta_public': profiling_bundle.get('eta_public_decimal'), 'receipt': receipt_profile_budget, 'summary': profiling_summary})
        if profiling_bundle.get('accepted') is not True:
            profiling_stat_failures.append({'accepted': profiling_bundle.get('accepted')})
    except Exception as exc:
        profiling_stat_failures.append({'exception': str(exc)})
    record('verifier profiling statistical CP/union-bound certificate', not profiling_stat_failures, f'failures={profiling_stat_failures}')

    profiling_stop_failures = []
    try:
        profiling_evidence_body = profiling_evidence.get('evidence', {}) if isinstance(profiling_evidence, dict) else {}
        table = profiling_evidence_body.get('table', []) if isinstance(profiling_evidence_body.get('table'), list) else []
        classes = sorted((profiling_evidence_body.get('classes') or {}).keys())
        bin_names = [row.get('bin') for row in table if isinstance(row, dict)]
        count_table_core = {
            'classes': classes,
            'bins': bin_names,
            'counts': {klass: [int((row.get('count') or {}).get(klass)) for row in table] for klass in classes},
            'n_per_class': {klass: int((profiling_evidence_body.get('classes', {}).get(klass, {}) or {}).get('n')) for klass in classes},
        }
        count_digest = canon_sha256_id(count_table_core)
        sampling_plan = profiling_evidence_body.get('sampling_plan', {}) if isinstance(profiling_evidence_body.get('sampling_plan'), dict) else {}
        fixed_rule = profiling_bundle.get('fixed_sample_stop_rule', {}) if isinstance(profiling_bundle.get('fixed_sample_stop_rule'), dict) else {}
        required_token = 'successor_evidence_id_or_time_uniform_certificate_required'
        if profiling_evidence_body.get('count_table_digest') != count_digest:
            profiling_stop_failures.append({'evidence_count_table_digest': profiling_evidence_body.get('count_table_digest'), 'expected': count_digest})
        if not (sampling_plan.get('sampling_plan_id') == fixed_rule.get('sampling_plan_id') == 'worked-example-profiling-fixed-sample-lock-v1'):
            profiling_stop_failures.append({'sampling_plan_id': sampling_plan.get('sampling_plan_id'), 'fixed_rule': fixed_rule.get('sampling_plan_id')})
        if not (sampling_plan.get('count_table_digest') == fixed_rule.get('count_table_digest') == count_digest):
            profiling_stop_failures.append({'sampling_plan_count_digest': sampling_plan.get('count_table_digest'), 'fixed_rule_count_digest': fixed_rule.get('count_table_digest'), 'expected': count_digest})
        if not (sampling_plan.get('look_count_allowed') == fixed_rule.get('look_count_allowed') == 1 and sampling_plan.get('look_index') == fixed_rule.get('look_index') == 1):
            profiling_stop_failures.append({'look_fields': {'sampling': {k: sampling_plan.get(k) for k in ('look_count_allowed','look_index')}, 'fixed_rule': {k: fixed_rule.get(k) for k in ('look_count_allowed','look_index')}}})
        if sampling_plan.get('time_uniform_status') != 'not_time_uniform_fixed_sample_only' or fixed_rule.get('time_uniform_status') != 'not_time_uniform_fixed_sample_only':
            profiling_stop_failures.append({'time_uniform_status': {'sampling': sampling_plan.get('time_uniform_status'), 'fixed_rule': fixed_rule.get('time_uniform_status')}})
        if sampling_plan.get('optional_stopping_status') != 'disallowed_by_certificate' or fixed_rule.get('optional_stopping_status') != 'disallowed_by_certificate':
            profiling_stop_failures.append({'optional_stopping_status': {'sampling': sampling_plan.get('optional_stopping_status'), 'fixed_rule': fixed_rule.get('optional_stopping_status')}})
        if sampling_plan.get('future_refresh_policy') != required_token or fixed_rule.get('future_refresh_policy') != required_token:
            profiling_stop_failures.append({'future_refresh_policy': {'sampling': sampling_plan.get('future_refresh_policy'), 'fixed_rule': fixed_rule.get('future_refresh_policy')}})
        if fixed_rule.get('evidence_id') != profiling_evidence.get('evidence_id') or fixed_rule.get('evidence_file') != 'example_profiling_evidence.json':
            profiling_stop_failures.append({'fixed_rule_evidence_binding': {'evidence_id': fixed_rule.get('evidence_id'), 'expected': profiling_evidence.get('evidence_id'), 'file': fixed_rule.get('evidence_file')}})
        invalidators = set(sampling_plan.get('invalidators', [])) | set(fixed_rule.get('invalidators', []))
        if not any('refreshing counts' in item for item in invalidators) or not any('peeking' in item for item in invalidators):
            profiling_stop_failures.append({'invalidators': sorted(invalidators)})
        if fixed_rule.get('accepted') is not True:
            profiling_stop_failures.append({'accepted': fixed_rule.get('accepted')})
    except Exception as exc:
        profiling_stop_failures.append({'exception': str(exc)})
    record('verifier profiling fixed-sample stop/refresh lock', not profiling_stop_failures, f'failures={profiling_stop_failures}')

    notary_owner = owner_map_entry_index.get('notary_replay_packet', {})
    notary_packet = verifier_report.get('notary_replay_packet', {}) if isinstance(verifier_report, dict) else {}
    notary_spine = line_item_spine_index.get('notary_replay_packet', {})
    notary_receipt_anchor = notary_spine.get('receipt_anchor', {}) if isinstance(notary_spine, dict) else {}
    notary_replay_anchor = notary_spine.get('replay_anchor', {}) if isinstance(notary_spine, dict) else {}
    notary_support_anchor = notary_spine.get('support_anchor', {}) if isinstance(notary_spine, dict) else {}
    notary_bundle = support_bundle_index.get('bundle://worked-example/fallback-cct', {})
    notary_failures = []
    def notary_equal(label, actual, expected):
        if actual != expected:
            notary_failures.append(f'{label}:{actual}!={expected}')
    notary_equal('owner-status', notary_owner.get('materialization_status'), 'verifier_report_current_cut')
    notary_equal('owner-verifier-file', notary_owner.get('verifier_report_file'), 'example_verifier_report.json')
    notary_equal('owner-plan', notary_owner.get('replay_plan_id'), 'eval-fallback-cct-v1')
    notary_equal('owner-plan-spec', notary_owner.get('plan_spec_id'), expected_plan_spec)
    notary_equal('owner-bundle', notary_owner.get('support_bundle_id'), 'bundle://worked-example/fallback-cct')
    notary_equal('owner-support-consumed-by', notary_owner.get('support_consumed_by'), ['eval-fallback-cct-v1'])
    notary_equal('owner-support-required-artifacts', notary_owner.get('support_required_artifacts'), notary_bundle.get('required_artifacts'))
    notary_equal('owner-support-pointers', notary_owner.get('support_pointers'), notary_bundle.get('support_pointers'))
    for required in ['example_receipt.json', 'example_state_decl.json', 'example_verifier_report.json', 'example_replay_plans.json', 'example_support_bundle_map.json', 'example_uvi.json', 'example_release_closure_ledger.json']:
        if required not in notary_owner.get('public_objects', []):
            notary_failures.append(f'owner-public-missing:{required}')
    notary_equal('packet-id', notary_packet.get('packet_id'), 'notary_replay_packet')
    notary_equal('packet-plan', notary_packet.get('plan_id'), 'eval-fallback-cct-v1')
    notary_equal('packet-bundle', notary_packet.get('support_bundle'), 'bundle://worked-example/fallback-cct')
    notary_equal('packet-pointer', notary_packet.get('support_pointer'), 'support://fallback/notarized-attempt-log.example')
    notary_equal('spine-artifact', notary_receipt_anchor.get('artifact'), 'example_verifier_report.json')
    notary_equal('spine-status', notary_receipt_anchor.get('materialization_status'), 'verifier_report_current_cut')
    notary_equal('spine-bundle', notary_receipt_anchor.get('support_bundle_id'), 'bundle://worked-example/fallback-cct')
    notary_equal('spine-replay-bundle', notary_replay_anchor.get('support_bundle_id'), 'bundle://worked-example/fallback-cct')
    notary_equal('spine-replay-plan-spec', notary_replay_anchor.get('plan_spec_id'), expected_plan_spec)
    notary_equal('spine-support-bundle', notary_support_anchor.get('support_bundle_id'), 'bundle://worked-example/fallback-cct')
    notary_equal('spine-support-required-artifacts', notary_support_anchor.get('required_artifacts'), notary_bundle.get('required_artifacts'))
    notary_equal('spine-support-pointers', notary_support_anchor.get('support_pointers'), notary_owner.get('support_pointers'))
    record('verifier notary replay owner-map support row', not notary_failures, f'failures={notary_failures}; owner_row={notary_owner}')

    public_object_closure_failures = []
    materialized_statuses = {'base_receipt_current_cut', 'verifier_report_current_cut', 'optional_variant_receipt_current_cut'}
    for row in owner_map_entries:
        if row.get('materialization_status') not in materialized_statuses:
            continue
        support_required = set(row.get('support_required_artifacts', []))
        public_objects = set(row.get('public_objects', []))
        missing = sorted(support_required - public_objects)
        if missing:
            public_object_closure_failures.append({'name': row.get('name'), 'missing_support_required_artifacts_in_public_objects': missing})
    record('verifier materialized owner-map public-object support closure', not public_object_closure_failures, f'failures={public_object_closure_failures}')

    paper17_text = (repo_root / 'series/synthesis/paper17_worked_example_receipt_interlock/paper.tex').read_text(encoding='utf-8')
    paper55_text = (repo_root / 'series/synthesis/paper55_series_spines_math_to_review_handoffs/paper.tex').read_text(encoding='utf-8')
    paper17_norm = paper17_text.replace('\\_', '_')
    paper55_norm = paper55_text.replace('\\_', '_')
    owner_map_prose_required = {
        'paper17 line-item-facing paragraph': 'Line-item-facing worked-surface reuse' in paper17_norm,
        'paper17 status field': 'materialization_status=owner_map_spine_only_current_cut' in paper17_norm,
        'paper17 plan status field': 'replay_plan_id_status=route_target_only_not_plan_catalog_row_current_cut' in paper17_norm,
        'paper17 public objects status field': 'public_objects_status=route_context_only_not_packet_materialization_evidence' in paper17_norm,
        'paper17 routing-signature boundary item': 'routing_signature_manifest} is only an owner-map / series-spine boundary row' in paper17_norm,
        'paper55 owner-map boundary row': 'Synthesis~17 owner-map-only boundary row' in paper55_norm,
        'paper55 owner-map status field': 'materialization_status=owner_map_spine_only_current_cut' in paper55_norm,
        'paper55 public objects status field': 'public_objects_status=route_context_only_not_packet_materialization_evidence' in paper55_norm,
        'paper55 packet-local materialized example': 'line_item_spines.fallback_contact_surface' in paper55_norm and 'line_item_spines.fallback_tiered_vector' in paper55_norm,
    }
    owner_map_prose_forbidden = {
        'paper17 operational carried packets': 'operational carried packets now have stable packet-local ladders' in paper17_norm,
        'paper17 routing-signature publishes exact carried card': 'routing_signature_manifest} publishes one exact raw-$M$' in paper17_norm,
        'paper55 retry/runtime as packet-local examples': 'line_item_spines.retry_schedule_packet} or' in paper55_norm and 'line_item_spines.runtime_conformance_packet}---rather than reopen' in paper55_norm,
        'paper55 operational exact carried packet claim': 'abstract operational route and only needs to point at the exact carried packet' in paper55_norm,
    }
    owner_map_prose_failures = {
        'missing_required': [name for name, ok in owner_map_prose_required.items() if not ok],
        'forbidden_present': [name for name, present in owner_map_prose_forbidden.items() if present],
    }
    owner_map_prose_ok = not owner_map_prose_failures['missing_required'] and not owner_map_prose_failures['forbidden_present']
    record('active owner-map-only versus packet-local prose boundary', owner_map_prose_ok, f'failures={owner_map_prose_failures}')

    materialized_owner_prose_required = {
        'paper17 base receipt owner-map paragraph': 'Base receipt owner-map support rows' in paper17_norm,
        'paper17 base receipt status': 'materialization_status=base_receipt_current_cut' in paper17_norm,
        'paper17 primary support bundle': 'support_bundle_id=bundle://worked-example/primary' in paper17_norm,
        'paper17 fallback cct support bundle': 'support_bundle_id=bundle://worked-example/fallback-cct' in paper17_norm,
        'paper17 fallback vector support bundle': 'support_bundle_id=bundle://worked-example/fallback-vector' in paper17_norm,
        'paper17 pathselect support bundle': 'support_bundle_id=bundle://worked-example/pathselect' in paper17_norm,
        'paper17 notary verifier status': 'materialization_status=verifier_report_current_cut' in paper17_norm and 'notary_replay_packet' in paper17_norm,
        'paper17 notary verifier file': 'example_verifier_report.json' in paper17_norm,
        'paper17 owner-map plan/support payload fields': 'plan_spec_id' in paper17_norm and 'support_required_artifacts' in paper17_norm and 'support_pointers' in paper17_norm,
        'paper17 verifier plans-checked support payload': 'plans_checked rows now mirror support_bundle_id' in paper17_norm and 'support_required_artifacts' in paper17_norm and 'support_pointers' in paper17_norm,
        'paper17 verifier public-object digest entries': 'public_object_digest_entries' in paper17_norm and 'binds every named verifier public object to its current in-archive SHA-256 digest' in paper17_norm,
        'paper17 verifier contract boundary': 'verifier_contract' in paper17_norm and 'formal_exact_rational_budget_closure_log_endpoint_derivations_and_profiling_cp_union_bound_present' in paper17_norm and 'canonical_input_order' in paper17_norm and 'transcendental endpoint derivation bundle' in paper17_norm and 'profiling_statistical_derivation_bundle' in paper17_norm and 'fixed-sample stop/refresh lock' in paper17_norm,
        'paper17 public-object support closure': 'support_required_artifacts are a subset of public_objects' in paper17_norm,
        'paper17 support-bundle resolver multiplicity': 'resolved_owner_map_row_names' in paper17_norm and 'resolved_owner_map_rows' in paper17_norm and 'fallback_contact_surface' in paper17_norm and 'notary_replay_packet' in paper17_norm,
        'paper55 materialized support distinction': 'base_receipt_current_cut' in paper55_norm and 'verifier_report_current_cut' in paper55_norm,
        'paper55 plan/support payload split': 'plan_spec_id' in paper55_norm and 'support_required_artifacts' in paper55_norm and 'support_pointers' in paper55_norm,
        'paper55 verifier plans-checked support payload': 'plans_checked rows mirror support_bundle_id' in paper55_norm and 'support_required_artifacts' in paper55_norm and 'support_pointers' in paper55_norm,
        'paper55 verifier public-object digest entries': 'public_object_digest_entries' in paper55_norm and 'binds every named public object to a current in-archive SHA-256 digest' in paper55_norm,
        'paper55 public-object support closure': 'support_required_artifacts are a subset of public_objects' in paper55_norm,
        'paper55 support-bundle resolver multiplicity': 'resolved_owner_map_row_names' in paper55_norm and 'resolved_owner_map_rows' in paper55_norm and 'fallback_contact_surface' in paper55_norm and 'notary_replay_packet' in paper55_norm,
    }
    materialized_owner_prose_failures = [name for name, ok in materialized_owner_prose_required.items() if not ok]
    record('active materialized owner-map support prose rows', not materialized_owner_prose_failures, f'failures={materialized_owner_prose_failures}')

    certifiedb_boundary_paths = [
        'series/certified_series/paperB_routing_signature_compression/paper.tex',
        queue_note_for_source('series/certified_series/paperB_routing_signature_compression/paper.tex'),
        'release_queue/hold/2026.03.16-paper17-worked-example-hold.md',
        'release_queue/hold/2026.03.19-paper55-series-spines-hold.md',
    ]
    required_certifiedb_needles = {
        'routing-signature row name': 'routing_signature_manifest',
        'line-item owner map': 'example_line_item_owner_map.json',
        'receipt absence object': 'example_receipt.json',
        'replay-plan absence object': 'example_replay_plans.json',
        'missing replay plan id': 'eval-routing-signature-v1',
        'support-map absence object': 'example_support_bundle_map.json',
        'missing support bundle': 'bundle://worked-example/routing-signature',
    }
    certifiedb_boundary_failures = []
    for rel in certifiedb_boundary_paths:
        active_text = (repo_root / rel).read_text(encoding='utf-8')
        active_norm = active_text.replace(r'\_', '_').replace(r'\nolinkurl{', '').replace('}', '').replace('owner map', 'owner-map').replace('series spine', 'series-spine')
        missing = [name for name, needle in required_certifiedb_needles.items() if needle not in active_norm]
        has_owner_map_boundary = 'owner-map' in active_norm and 'series-spine' in active_norm
        if not has_owner_map_boundary:
            missing.append('owner-map / series-spine boundary language')
        has_negative_receipt = 'example_receipt.json' in active_norm and any(needle in active_norm for needle in [
            'does not emit',
            'does not contain',
            'does not ship',
            'not emitted',
            'not materialized',
            'not a new receipt',
        ])
        has_negative_replay = 'eval-routing-signature-v1' in active_norm and any(needle in active_norm for needle in [
            'does not include',
            'does not contain',
            'not include',
            'not plan catalog',
            'not materialized',
            'not emit',
        ])
        has_negative_support = 'bundle://worked-example/routing-signature' in active_norm and any(needle in active_norm for needle in [
            'does not resolve',
            'not resolve',
            'does not ship',
            'not materialized',
            'missing worked receipt, replay-plan row, or support-bundle carrier',
        ])
        if not has_negative_receipt:
            missing.append('negative routing-signature receipt boundary')
        if not has_negative_replay:
            missing.append('negative routing-signature replay-plan boundary')
        if not has_negative_support:
            missing.append('negative routing-signature support-bundle boundary')
        forbidden = []
        for snippet in [
            'exact worked-packet route',
            'exact worked packet route',
            'exact compression packet',
            'worked example now carries one exact Certified~B signature-manifest packet',
            'maintained receipt / owner-map / replay-plan / support-bundle surfaces now expose',
            'resolves bundle://worked-example/routing-signature',
        ]:
            if snippet in active_text or snippet in active_norm:
                forbidden.append(snippet)
        if missing or forbidden:
            certifiedb_boundary_failures.append({'path': rel, 'missing': missing, 'forbidden': forbidden})
    record('active CertifiedB routing-signature boundary rows', not certifiedb_boundary_failures, f'paths={certifiedb_boundary_paths}; failures={certifiedb_boundary_failures}')

    recertification_source_files = [
        'example_change_control.json',
        'example_compare_report.json',
        'example_drift_cases.json',
        'example_release_action_matrix.json',
    ]
    recertification_absence_failures = []
    for rel_source in recertification_source_files:
        if not (ART / rel_source).exists():
            recertification_absence_failures.append(f'missing-source-object:{rel_source}')
    if 'bundle://worked-example/recertification' in support_bundle_ids:
        recertification_absence_failures.append('unexpected-recertification-support-bundle')
    if 'eval-recertification-v1' in plan_catalog_ids:
        recertification_absence_failures.append('unexpected-recertification-replay-plan')
    if any(key in verifier_report for key in ['recertification_packet', 'certified_recertification_packet']):
        recertification_absence_failures.append('unexpected-verifier-recertification-packet')
    record('verifier CertifiedC recertification source-boundary content', not recertification_absence_failures, f'failures={recertification_absence_failures}; source_files={recertification_source_files}; plan_catalog_ids={sorted(plan_catalog_ids)}; support_bundle_ids={sorted(support_bundle_ids)}; verifier_report_keys={sorted(verifier_report.keys())}')

    certified_c_path = 'series/certified_series/paperC_disagreement_gated_recertification/paper.tex'
    certified_c_queue_path = 'release_queue/published_ready/2026.03.17-paperC-disagreement-recertification-published-ready.md'
    recertification_boundary_paths = [
        certified_c_path,
        'series/synthesis/paper17_worked_example_receipt_interlock/paper.tex',
        'series/synthesis/paper55_series_spines_math_to_review_handoffs/paper.tex',
        certified_c_queue_path,
        'release_queue/hold/2026.03.16-paper17-worked-example-hold.md',
        'release_queue/hold/2026.03.19-paper55-series-spines-hold.md',
    ]
    required_recertification_needles = {
        'change control source': 'example_change_control.json',
        'compare report source': 'example_compare_report.json',
        'drift cases source': 'example_drift_cases.json',
        'release action matrix source': 'example_release_action_matrix.json',
        'missing recertification bundle name': 'bundle://worked-example/recertification',
    }
    recertification_prose_failures = []
    for rel in recertification_boundary_paths:
        active_text = (repo_root / rel).read_text(encoding='utf-8')
        active_norm = active_text.replace('\\_', '_')
        missing = [name for name, needle in required_recertification_needles.items() if needle not in active_norm]
        has_negative_bundle_boundary = (
            'does not resolve' in active_norm
            or 'not resolve' in active_norm
            or 'unmaterialized' in active_norm
            or 'without materializing' in active_norm
            or 'must not cite' in active_norm
        ) and 'bundle://worked-example/recertification' in active_norm
        if not has_negative_bundle_boundary:
            missing.append('negative recertification bundle boundary')
        forbidden = []
        for snippet in [
            'resolves bundle://worked-example/recertification',
            'materializes that third stop as bundle://worked-example/recertification',
            'exact maintained downstream carrier route as bundle://worked-example/recertification',
            'maintained recertification bundle owns the exact guard/classification/case-ladder route',
        ]:
            if snippet in active_norm:
                forbidden.append(snippet)
        if missing or forbidden:
            recertification_prose_failures.append({'path': rel, 'missing': missing, 'forbidden': forbidden})
    record('active CertifiedC recertification source-boundary rows', not recertification_prose_failures, f'paths={recertification_boundary_paths}; failures={recertification_prose_failures}')


    # profiling_evidence and profiling_evidence_digest were loaded near the top so
    # verifier-report support_artifacts can be checked against the same object.
    profiling_item = next((item for item in receipt.get('line_items', []) if item.get('name') == 'profiling_equalization'), {})
    profiling_evidence_body = profiling_evidence.get('evidence', {}) if isinstance(profiling_evidence, dict) else {}
    profiling_summary = profiling_evidence_body.get('certificate_summary', {}) if isinstance(profiling_evidence_body, dict) else {}
    profiling_plan = next((entry for entry in replay_plans.get('plans', []) if entry.get('plan_id') == 'eval-profiling-eq-v1'), {})
    profiling_bundle = next((entry for entry in support_bundle_map.get('bundles', []) if entry.get('bundle_id') == 'bundle://worked-example/profiling-eq'), {})
    profiling_owner = owner_map_entry_index.get('profiling_equalization', {})
    profiling_failures = []
    def check_equal(label, actual, expected):
        if actual != expected:
            profiling_failures.append(f'{label}:{actual}!={expected}')
    def check_float_equal(label, actual, expected):
        try:
            ok = math.isclose(float(actual), float(expected), rel_tol=0, abs_tol=1e-12)
        except (TypeError, ValueError):
            ok = False
        if not ok:
            profiling_failures.append(f'{label}:{actual}!={expected}')
    check_equal('line-item-evidence-id', profiling_item.get('evidence_id'), profiling_evidence.get('evidence_id'))
    check_equal('owner-map-evidence-id', profiling_owner.get('evidence_id'), profiling_evidence.get('evidence_id'))
    check_equal('line-item-exposure-nf', profiling_item.get('exposure_nf_id'), profiling_evidence_body.get('exposure_nf_id'))
    check_equal('owner-map-exposure-nf', profiling_owner.get('exposure_nf_id'), profiling_evidence_body.get('exposure_nf_id'))
    check_equal('line-item-tw', profiling_item.get('tw_id'), profiling_evidence_body.get('tw_id'))
    check_float_equal('eta-bits', (profiling_item.get('budget_value') or {}).get('eta_bits'), profiling_summary.get('eta_bits'))
    check_float_equal('delta-slack', (profiling_item.get('budget_value') or {}).get('delta'), profiling_summary.get('delta_slack'))
    profiling_hook = profiling_item.get('replay_hook', {}) if isinstance(profiling_item, dict) else {}
    check_equal('plan-id', profiling_hook.get('plan_id'), 'eval-profiling-eq-v1')
    check_equal('plan-spec-id', profiling_hook.get('plan_spec_id'), 'sha256:db245ce4f3c200322eea17a42a2c64cf9dc28bdeb18fa24e5d3643b51eb1e6f6')
    check_equal('artifact-bundle', profiling_hook.get('artifact_bundle'), 'bundle://worked-example/profiling-eq')
    check_equal('plan-required-inputs', profiling_plan.get('plan_spec', {}).get('required_inputs'), ['example_receipt.json', 'example_profiling_evidence.json'])
    check_equal('support-required-artifacts', profiling_bundle.get('required_artifacts'), ['example_receipt.json', 'example_profiling_evidence.json'])
    check_equal('support-consumed-by', profiling_bundle.get('consumed_by'), ['eval-profiling-eq-v1'])
    if 'support://profiling/log-slice.example' not in profiling_bundle.get('support_pointers', []):
        profiling_failures.append('missing-support-pointer')
    required_profiling_public_objects = {
        'example_receipt.json',
        'example_profiling_evidence.json',
        'example_replay_plans.json',
        'example_support_bundle_map.json',
    }
    if not required_profiling_public_objects.issubset(set(profiling_owner.get('public_objects', []))):
        profiling_failures.append('owner-map-public-objects-missing')
    record('verifier AnonymityB profiling carrier content', not profiling_failures, f"evidence_id={profiling_evidence.get('evidence_id')}; plan_id={profiling_hook.get('plan_id')}; bundle={profiling_hook.get('artifact_bundle')}; owner_status={profiling_owner.get('materialization_status')}; failures={profiling_failures}")

    profiling_owner_support_failures = []
    def owner_support_equal(label, actual, expected):
        if actual != expected:
            profiling_owner_support_failures.append(f'{label}:{actual}!={expected}')
    owner_support_equal('materialization-status', profiling_owner.get('materialization_status'), 'base_receipt_current_cut')
    owner_support_equal('receipt-file', profiling_owner.get('receipt_file'), 'example_receipt.json')
    owner_support_equal('evidence-id', profiling_owner.get('evidence_id'), profiling_evidence.get('evidence_id'))
    owner_support_equal('replay-plan-id', profiling_owner.get('replay_plan_id'), 'eval-profiling-eq-v1')
    owner_support_equal('plan-spec-id', profiling_owner.get('plan_spec_id'), 'sha256:db245ce4f3c200322eea17a42a2c64cf9dc28bdeb18fa24e5d3643b51eb1e6f6')
    owner_support_equal('support-bundle-id', profiling_owner.get('support_bundle_id'), 'bundle://worked-example/profiling-eq')
    owner_support_equal('support-consumed-by', profiling_owner.get('support_consumed_by'), ['eval-profiling-eq-v1'])
    owner_support_equal('support-required-artifacts', profiling_owner.get('support_required_artifacts'), ['example_receipt.json', 'example_profiling_evidence.json'])
    owner_support_equal('support-pointers', profiling_owner.get('support_pointers'), ['support://profiling/log-slice.example'])
    missing_owner_public = sorted(required_profiling_public_objects - set(profiling_owner.get('public_objects', [])))
    if missing_owner_public:
        profiling_owner_support_failures.append(f'public-objects-missing:{missing_owner_public}')
    record('verifier AnonymityB profiling base owner-map support content', not profiling_owner_support_failures, f"failures={profiling_owner_support_failures}; owner_row={profiling_owner}")

    profiling_active_paths = [
        'series/anonymity_series/paperB_anonymous_dht_profiling/paper.tex',
        'series/synthesis/paper17_worked_example_receipt_interlock/paper.tex',
        'release_queue/published_ready/2026.03.16-paperB-anondht-profiling-published-ready.md',
        'release_queue/hold/2026.03.16-paper17-worked-example-hold.md',
    ]
    profiling_active_needles = {
        'line item': 'profiling_equalization',
        'evidence id': profiling_evidence.get('evidence_id'),
        'replay hook': 'eval-profiling-eq-v1',
        'plan spec': 'sha256:db245ce4f3c200322eea17a42a2c64cf9dc28bdeb18fa24e5d3643b51eb1e6f6',
        'support bundle': 'bundle://worked-example/profiling-eq',
        'support pointer': 'support://profiling/log-slice.example',
        'verifier plans_checked': 'plans_checked',
        'verifier public-object digest entries': 'public_object_digest_entries',
        'verifier support artifact digest': 'profiling_evidence_digest',
    }
    profiling_active_failures = []
    stale_profiling_digest = 'sha256:19265adeef60080b26c2b85ef6dbc83e6ca4a15a32c474a154046e6299d4ede7'
    for rel in profiling_active_paths:
        active_text = (repo_root / rel).read_text(encoding='utf-8')
        active_norm = active_text.replace('\\_', '_')
        missing = [name for name, needle in profiling_active_needles.items() if needle not in active_norm]
        forbidden = [stale_profiling_digest] if stale_profiling_digest in active_norm else []
        if missing or forbidden:
            profiling_active_failures.append({'path': rel, 'missing': missing, 'forbidden': forbidden})
    record('active AnonymityB profiling-carrier rows', not profiling_active_failures, f'paths={profiling_active_paths}; failures={profiling_active_failures}')

    profiling_variant_specs = [
        {
            'receipt_file': 'example_receipt_prefixfetch_variant.json',
            'evidence_file': 'example_profiling_evidence_prefixfetch.json',
            'line_item_name': 'profiling_equalization_prefixfetch',
            'evidence_id': 'sha256:887e6706ae2e1b982f28dbafdbe7796e59b06ab2dbeb5f4db43fe9e667268f61',
            'eta_bits': 0.292597,
            'delta': 0.004483,
            'plan_id': 'eval-profiling-prefixfetch-v1',
            'plan_spec_id': 'sha256:147407f2dc29e851ddb5e01de325a1c6dc94a1c93e3fd9ea058f47ba3f0bbba4',
            'bundle_id': 'bundle://worked-example/profiling-prefixfetch',
            'support_pointer': 'support://profiling/prefixfetch-log-slice.example',
            'required_inputs': ['example_receipt_prefixfetch_variant.json', 'example_profiling_evidence_prefixfetch.json'],
        },
        {
            'receipt_file': 'example_receipt_prefixfetch_statecond_variant.json',
            'evidence_file': 'example_profiling_evidence_prefixfetch_statecond.json',
            'line_item_name': 'profiling_equalization_prefixfetch_statecond',
            'evidence_id': 'sha256:348176a3e0bdaede5a67f8497ed1c31effd1d64f34eae12e9e9b46154b0b6bd3',
            'eta_bits': 0.459923,
            'delta': 0.007146,
            'plan_id': 'eval-profiling-prefixfetch-statecond-v1',
            'plan_spec_id': 'sha256:e24e82848c1071cb2c498e44682173c3ebaca80083d59c4ad23e04a9a6b306ec',
            'bundle_id': 'bundle://worked-example/profiling-prefixfetch-statecond',
            'support_pointer': 'support://profiling/prefixfetch-statecond-log-slice.example',
            'required_inputs': ['example_receipt_prefixfetch_statecond_variant.json', 'example_profiling_evidence_prefixfetch_statecond.json'],
        },
        {
            'receipt_file': 'example_receipt_contact_coarsened_variant.json',
            'evidence_file': 'example_profiling_evidence_contact_coarsened.json',
            'line_item_name': 'profiling_equalization_contact_coarsened',
            'evidence_id': 'sha256:22666e9853213a11356f4b863aa9e0dba88bcdd56306ac345acd80e1f09d36fa',
            'eta_bits': 0.391684,
            'delta': 0.0,
            'plan_id': 'eval-profiling-contact-coarsened-v1',
            'plan_spec_id': 'sha256:9a06cba8d0929527408ef3216ce5b21c5acbf199ca1393c46fce3324ff67da2f',
            'bundle_id': 'bundle://worked-example/profiling-contact-coarsened',
            'support_pointer': 'support://profiling/contactset-hash.example',
            'required_inputs': ['example_receipt_contact_coarsened_variant.json', 'example_profiling_evidence_contact_coarsened.json', 'example_coarsening_map_contact.json'],
            'coarsening_map_id': 'sha256:4c447e40d9e29e41ffa313f41edd5b2d54ad296c5a9f58b01d26ac220db5bbc1',
        },
    ]
    profiling_variant_failures = []
    profiling_variant_owner_failures = []
    for spec in profiling_variant_specs:
        variant_receipt, _ = load_json(spec['receipt_file'])
        variant_evidence, _ = load_json(spec['evidence_file'])
        variant_evidence_body = variant_evidence.get('evidence', {}) if isinstance(variant_evidence, dict) else {}
        variant_summary = variant_evidence_body.get('certificate_summary', {}) if isinstance(variant_evidence_body, dict) else {}
        variant_item = next((item for item in variant_receipt.get('line_items', []) if item.get('name') == spec['line_item_name']), {})
        variant_plan = next((entry for entry in replay_plans.get('plans', []) if entry.get('plan_id') == spec['plan_id']), {})
        variant_bundle = next((entry for entry in support_bundle_map.get('bundles', []) if entry.get('bundle_id') == spec['bundle_id']), {})
        variant_owner = owner_map_entry_index.get(spec['line_item_name'], {})
        variant_hook = variant_item.get('replay_hook', {}) if isinstance(variant_item, dict) else {}
        problems = []
        def v_equal(label, actual, expected):
            if actual != expected:
                problems.append(f'{label}:{actual}!={expected}')
        def v_float(label, actual, expected):
            try:
                ok = math.isclose(float(actual), float(expected), rel_tol=0, abs_tol=1e-12)
            except (TypeError, ValueError):
                ok = False
            if not ok:
                problems.append(f'{label}:{actual}!={expected}')
        v_equal('evidence-id', variant_item.get('evidence_id'), variant_evidence.get('evidence_id'))
        v_equal('expected-evidence-id', variant_evidence.get('evidence_id'), spec['evidence_id'])
        v_equal('exposure-nf', variant_item.get('exposure_nf_id'), variant_evidence_body.get('exposure_nf_id'))
        v_equal('owner-map-exposure-nf', variant_owner.get('exposure_nf_id'), variant_evidence_body.get('exposure_nf_id'))
        v_float('eta-bits', (variant_item.get('budget_value') or {}).get('eta_bits'), spec['eta_bits'])
        v_float('eta-bits-summary', variant_summary.get('eta_bits'), spec['eta_bits'])
        v_float('delta', (variant_item.get('budget_value') or {}).get('delta'), spec['delta'])
        v_float('delta-summary', variant_summary.get('delta_slack'), spec['delta'])
        v_equal('plan-id', variant_hook.get('plan_id'), spec['plan_id'])
        v_equal('plan-spec-id', variant_hook.get('plan_spec_id'), spec['plan_spec_id'])
        v_equal('artifact-bundle', variant_hook.get('artifact_bundle'), spec['bundle_id'])
        v_equal('plan-required-inputs', variant_plan.get('plan_spec', {}).get('required_inputs'), spec['required_inputs'])
        v_equal('support-required-artifacts', variant_bundle.get('required_artifacts'), spec['required_inputs'])
        v_equal('support-consumed-by', variant_bundle.get('consumed_by'), [spec['plan_id']])
        if spec['support_pointer'] not in variant_bundle.get('support_pointers', []):
            problems.append('support-pointer-missing')
        if variant_owner.get('replay_plan_id') != spec['plan_id']:
            problems.append('owner-map-replay-plan-mismatch')
        owner_problems = []
        def owner_equal(label, actual, expected):
            if actual != expected:
                owner_problems.append(f'{label}:{actual}!={expected}')
        owner_equal('materialization-status', variant_owner.get('materialization_status'), 'optional_variant_receipt_current_cut')
        owner_equal('receipt-variant-file', variant_owner.get('receipt_variant_file'), spec['receipt_file'])
        owner_equal('evidence-id', variant_owner.get('evidence_id'), spec['evidence_id'])
        owner_equal('replay-plan-id', variant_owner.get('replay_plan_id'), spec['plan_id'])
        owner_equal('plan-spec-id', variant_owner.get('plan_spec_id'), spec['plan_spec_id'])
        owner_equal('support-bundle-id', variant_owner.get('support_bundle_id'), spec['bundle_id'])
        owner_equal('support-consumed-by', variant_owner.get('support_consumed_by'), [spec['plan_id']])
        owner_equal('support-required-artifacts', variant_owner.get('support_required_artifacts'), spec['required_inputs'])
        owner_equal('support-pointers', variant_owner.get('support_pointers'), [spec['support_pointer']])
        required_public_objects = set(spec['required_inputs']) | {'example_replay_plans.json', 'example_support_bundle_map.json'}
        missing_public_objects = sorted(required_public_objects - set(variant_owner.get('public_objects', [])))
        if missing_public_objects:
            owner_problems.append(f'public-objects-missing:{missing_public_objects}')
        if 'coarsening_map_id' in spec:
            owner_equal('coarsening-map-id', variant_owner.get('coarsening_map_id'), spec['coarsening_map_id'])
        if owner_problems:
            profiling_variant_owner_failures.append({'name': spec['line_item_name'], 'problems': owner_problems})
        if 'coarsening_map_id' in spec:
            v_equal('item-coarsening-map-id', (variant_item.get('knobs') or {}).get('coarsening_map_id'), spec['coarsening_map_id'])
            v_equal('evidence-coarsening-map-id', variant_evidence_body.get('coarsening_map_id'), spec['coarsening_map_id'])
        if problems:
            profiling_variant_failures.append({'name': spec['line_item_name'], 'problems': problems})
    record('verifier profiling variant bundle content', not profiling_variant_failures, f'failures={profiling_variant_failures}')
    record('verifier profiling variant owner-map rows', not profiling_variant_owner_failures, f'failures={profiling_variant_owner_failures}')

    optional_variant_plan_rows = [entry for entry in verifier_report.get('optional_variant_plans_checked', []) if isinstance(entry, dict)]
    optional_variant_plan_by_id = {entry.get('plan_id'): entry for entry in optional_variant_plan_rows}
    optional_variant_verifier_failures = []
    for spec in profiling_variant_specs:
        plan_id = spec['plan_id']
        entry = optional_variant_plan_by_id.get(plan_id, {})
        owner_row = owner_map_entry_index.get(spec['line_item_name'], {})
        expected_public_objects = owner_row.get('public_objects', [])
        expected_payload = {
            'line_item_name': spec['line_item_name'],
            'plan_id': plan_id,
            'plan_spec_id': spec['plan_spec_id'],
            'receipt_variant_file': spec['receipt_file'],
            'evidence_id': spec['evidence_id'],
            'support_bundle_id': spec['bundle_id'],
            'support_consumed_by': [plan_id],
            'support_required_artifacts': spec['required_inputs'],
            'support_pointers': [spec['support_pointer']],
            'public_objects': expected_public_objects,
            'public_object_digest_entries': expected_public_object_digest_entries(expected_public_objects),
        }
        expected_payload['verifier_contract'] = expected_verifier_contract(entry) if entry else None
        if 'coarsening_map_id' in spec:
            expected_payload['coarsening_map_id'] = spec['coarsening_map_id']
        problems = []
        if not entry:
            problems.append('missing-optional-variant-verifier-plan-entry')
        for field, expected in expected_payload.items():
            if entry.get(field) != expected:
                problems.append(f'{field}:{entry.get(field)}!={expected}')
        if plan_id in verifier_plan_ids:
            problems.append('optional-variant-plan-leaked-into-base-plans_checked')
        if set(entry.get('support_required_artifacts', [])) - set(entry.get('public_objects', [])):
            problems.append('variant-verifier-support-required-artifacts-not-public')
        if problems:
            optional_variant_verifier_failures.append({'name': spec['line_item_name'], 'plan_id': plan_id, 'problems': problems})
    record('verifier optional profiling variant plans-checked closure', not optional_variant_verifier_failures, f'optional_variant_plans_checked={[entry.get("plan_id") for entry in optional_variant_plan_rows]}; failures={optional_variant_verifier_failures}')

    materialized_payload_failures = []
    for row in owner_map_entries:
        if not isinstance(row, dict):
            continue
        if row.get('materialization_status') not in {'base_receipt_current_cut', 'verifier_report_current_cut', 'optional_variant_receipt_current_cut'}:
            continue
        plan = replay_plan_index.get(row.get('replay_plan_id'), {})
        bundle = support_bundle_index.get(row.get('support_bundle_id'), {})
        row_failures = []
        if not plan:
            row_failures.append('missing-replay-plan')
        if not bundle:
            row_failures.append('missing-support-bundle')
        if row.get('plan_spec_id') != plan.get('plan_spec_id'):
            row_failures.append('plan-spec-id-mismatch')
        if row.get('support_consumed_by') != bundle.get('consumed_by'):
            row_failures.append('support-consumed-by-mismatch')
        if row.get('support_required_artifacts') != bundle.get('required_artifacts'):
            row_failures.append('support-required-artifacts-mismatch')
        if row.get('support_pointers') != bundle.get('support_pointers'):
            row_failures.append('support-pointers-mismatch')
        if row_failures:
            materialized_payload_failures.append({'name': row.get('name'), 'failures': row_failures})
    record('verifier materialized owner-map replay/support payload fields', not materialized_payload_failures, f'failures={materialized_payload_failures}')

    support_resolver_failures = []
    resolver_rows_by_bundle = {}
    for row in owner_map_entries:
        if not isinstance(row, dict):
            continue
        if row.get('materialization_status') not in {'base_receipt_current_cut', 'verifier_report_current_cut', 'optional_variant_receipt_current_cut'}:
            continue
        resolver_rows_by_bundle.setdefault(row.get('support_bundle_id'), []).append(row)

    def expected_support_resolver_payload(owner_row, bundle_row):
        payload = {
            'line_item_name': owner_row.get('name'),
            'materialization_status': owner_row.get('materialization_status'),
            'support_bundle_id': owner_row.get('support_bundle_id'),
            'replay_plan_id': owner_row.get('replay_plan_id'),
            'plan_spec_id': replay_plan_index.get(owner_row.get('replay_plan_id'), {}).get('plan_spec_id'),
            'support_consumed_by': bundle_row.get('consumed_by', []),
            'support_required_artifacts': bundle_row.get('required_artifacts', []),
            'support_pointers': bundle_row.get('support_pointers', []),
            'public_objects': owner_row.get('public_objects', []),
        }
        for key in ['receipt_file', 'receipt_variant_file', 'verifier_report_file', 'evidence_id', 'coarsening_map_id', 'contact_surface_id']:
            if owner_row.get(key) is not None:
                payload[key] = owner_row.get(key)
        return payload

    legacy_singleton_resolver_fields = {
        'line_item_name',
        'materialization_status',
        'receipt_file',
        'receipt_variant_file',
        'verifier_report_file',
        'replay_plan_id',
        'plan_spec_id',
        'public_objects',
        'evidence_id',
        'coarsening_map_id',
    }
    for bundle_row in support_bundle_map.get('bundles', []):
        if not isinstance(bundle_row, dict):
            continue
        bundle_id = bundle_row.get('bundle_id')
        expected_owner_rows = resolver_rows_by_bundle.get(bundle_id, [])
        if not expected_owner_rows:
            continue
        problems = []
        expected_names = [row.get('name') for row in expected_owner_rows]
        expected_rows = [expected_support_resolver_payload(row, bundle_row) for row in expected_owner_rows]
        if bundle_row.get('resolved_owner_map_row_names') != expected_names:
            problems.append(f'resolved-names:{bundle_row.get("resolved_owner_map_row_names")}!={expected_names}')
        if bundle_row.get('resolved_owner_map_rows') != expected_rows:
            problems.append('resolved-rows-payload-mismatch')
        if len(bundle_row.get('resolved_owner_map_rows', [])) != len(expected_owner_rows):
            problems.append('resolved-row-count-mismatch')
        leaked_singletons = sorted(legacy_singleton_resolver_fields & set(bundle_row.keys()))
        if leaked_singletons:
            problems.append(f'legacy-singleton-fields-present:{leaked_singletons}')
        if bundle_id == 'bundle://worked-example/fallback-cct' and expected_names != ['fallback_contact_surface', 'notary_replay_packet']:
            problems.append(f'fallback-cct-multiplicity-not-preserved:{expected_names}')
        if problems:
            support_resolver_failures.append({'bundle_id': bundle_id, 'problems': problems})
    record('verifier support-bundle resolver owner-row multiplicity closure', not support_resolver_failures, f'failures={support_resolver_failures}')

    optional_variant_spines = series_spine.get('optional_variant_spines', [])
    optional_variant_spine_index = {entry.get('line_item_name'): entry for entry in optional_variant_spines if isinstance(entry, dict)}
    base_line_item_spine_names = {entry.get('line_item_name') for entry in series_spine.get('line_item_spines', []) if isinstance(entry, dict)}
    profiling_variant_spine_failures = []
    for spec in profiling_variant_specs:
        spine = optional_variant_spine_index.get(spec['line_item_name'], {})
        receipt_anchor = spine.get('receipt_anchor', {}) if isinstance(spine, dict) else {}
        owner_anchor = spine.get('owner_map_anchor', {}) if isinstance(spine, dict) else {}
        replay_anchor = spine.get('replay_anchor', {}) if isinstance(spine, dict) else {}
        support_anchor = spine.get('support_anchor', {}) if isinstance(spine, dict) else {}
        sentence = spine.get('variant_sentence_normal_form', {}) if isinstance(spine, dict) else {}
        problems = []
        if spec['line_item_name'] in base_line_item_spine_names:
            problems.append('variant-unexpectedly-in-base-line-item-spines')
        def spine_equal(label, actual, expected):
            if actual != expected:
                problems.append(f'{label}:{actual}!={expected}')
        spine_equal('materialization-status', spine.get('materialization_status'), 'optional_variant_receipt_current_cut')
        spine_equal('receipt-variant-file', spine.get('receipt_variant_file'), spec['receipt_file'])
        spine_equal('evidence-id', spine.get('evidence_id'), spec['evidence_id'])
        spine_equal('receipt-anchor-artifact', receipt_anchor.get('artifact'), spec['receipt_file'])
        spine_equal('receipt-anchor-line-item', receipt_anchor.get('line_item_name'), spec['line_item_name'])
        spine_equal('owner-map-section', owner_anchor.get('section'), 'variant_entries')
        spine_equal('owner-map-support-bundle-id', owner_anchor.get('support_bundle_id'), spec['bundle_id'])
        spine_equal('replay-plan-id', replay_anchor.get('plan_id'), spec['plan_id'])
        spine_equal('replay-plan-spec-id', replay_anchor.get('plan_spec_id'), spec['plan_spec_id'])
        spine_equal('replay-artifact-bundle', replay_anchor.get('artifact_bundle'), spec['bundle_id'])
        spine_equal('support-bundle-id', support_anchor.get('support_bundle_id'), spec['bundle_id'])
        spine_equal('support-required-artifacts', support_anchor.get('required_artifacts'), spec['required_inputs'])
        if spec['support_pointer'] not in support_anchor.get('support_pointers', []):
            problems.append('support-anchor-pointer-missing')
        if not sentence.get('surface_text') or spec['receipt_file'] not in sentence.get('surface_text') or spec['line_item_name'] not in sentence.get('surface_text'):
            problems.append('variant-sentence-normal-form-missing-receipt-or-name')
        if spine.get('route_local_reopen_artifact') != 'example_question_routes.json' or not spine.get('route_local_reopen_rule'):
            problems.append('route-local-reopen-not-explicit')
        if 'coarsening_map_id' in spec:
            spine_equal('spine-coarsening-map-id', spine.get('coarsening_map_id'), spec['coarsening_map_id'])
            spine_equal('owner-map-coarsening-map-id', owner_anchor.get('coarsening_map_id'), spec['coarsening_map_id'])
        if problems:
            profiling_variant_spine_failures.append({'name': spec['line_item_name'], 'problems': problems})
    record('verifier profiling variant spine rows', not profiling_variant_spine_failures, f'failures={profiling_variant_spine_failures}; optional_variant_spines={list(optional_variant_spine_index.keys())}')

    profiling_variant_text = paper17_norm
    profiling_variant_needles = {
        'prefix line item': 'profiling_equalization_prefixfetch',
        'prefix evidence id': 'sha256:887e6706ae2e1b982f28dbafdbe7796e59b06ab2dbeb5f4db43fe9e667268f61',
        'prefix hook': 'eval-profiling-prefixfetch-v1',
        'prefix bundle': 'bundle://worked-example/profiling-prefixfetch',
        'statecond line item': 'profiling_equalization_prefixfetch_statecond',
        'statecond evidence id': 'sha256:348176a3e0bdaede5a67f8497ed1c31effd1d64f34eae12e9e9b46154b0b6bd3',
        'statecond hook': 'eval-profiling-prefixfetch-statecond-v1',
        'statecond bundle': 'bundle://worked-example/profiling-prefixfetch-statecond',
        'coarsened line item': 'profiling_equalization_contact_coarsened',
        'coarsened evidence id': 'sha256:22666e9853213a11356f4b863aa9e0dba88bcdd56306ac345acd80e1f09d36fa',
        'coarsening map id': 'sha256:4c447e40d9e29e41ffa313f41edd5b2d54ad296c5a9f58b01d26ac220db5bbc1',
        'coarsened hook': 'eval-profiling-contact-coarsened-v1',
        'coarsened bundle': 'bundle://worked-example/profiling-contact-coarsened',
        'variant owner-map status': 'optional_variant_receipt_current_cut',
        'prefix receipt file': 'example_receipt_prefixfetch_variant.json',
        'statecond receipt file': 'example_receipt_prefixfetch_statecond_variant.json',
        'coarsened receipt file': 'example_receipt_contact_coarsened_variant.json',
        'variant owner-map support field': 'support_bundle_id',
        'variant plan-spec field': 'plan_spec_id',
        'variant support artifact field': 'support_required_artifacts',
        'variant support pointer field': 'support_pointers',
        'variant spine export': 'optional_variant_spines',
        'variant verifier export': 'optional_variant_plans_checked',
        'variant verifier digest export': 'public_object_digest_entries',
        'variant spine sentence field': 'variant_sentence_normal_form',
    }
    profiling_variant_missing = [name for name, needle in profiling_variant_needles.items() if needle not in profiling_variant_text]
    record('active Synthesis17 profiling variant rows', not profiling_variant_missing, f'missing={profiling_variant_missing}')

    state_decl_text = json.dumps(state_decl, sort_keys=True)
    cppc_absence_failures = []
    if 'monitoring_contract_packet' in state_decl_text:
        cppc_absence_failures.append('unexpected-state-decl-monitoring-contract-packet')
    if 'monitoring_contract_packet' in json.dumps(verifier_report, sort_keys=True):
        cppc_absence_failures.append('unexpected-verifier-monitoring-contract-packet')
    if 'eval-cppc-v1' in plan_catalog_ids:
        cppc_absence_failures.append('unexpected-cppc-replay-plan')
    if 'bundle://worked-example/cppc' in support_bundle_ids:
        cppc_absence_failures.append('unexpected-cppc-support-bundle')
    record('verifier CPPC monitoring-packet absence boundary content', not cppc_absence_failures, f'failures={cppc_absence_failures}; plan_catalog_ids={sorted(plan_catalog_ids)}; support_bundle_ids={sorted(support_bundle_ids)}')

    manifest_paths = {entry['path']: entry['sha256'] for entry in support_manifest.get('files', [])}
    manifest_index = {path: {'path': path, 'sha256': sha} for path, sha in manifest_paths.items()}
    inventory_index = {entry['path']: {**entry, 'group': group.get('group'), 'visibility': group.get('visibility')} for group in artifact_inventory.get('groups', []) for entry in group.get('entries', [])}
    expected_digests = {
        'example_receipt.json': receipt_digest,
        'example_compare_report.json': compare_report_digest,
        'example_artifact_inventory.json': artifact_inventory_digest,
        'example_verifier_report.json': verifier_report_digest,
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
    record('support manifest digest bindings', manifest_ok, 'manifest includes digests for receipt, compare report, inventory, verifier report, release spine, release stage walkthrough, derivation graph, lineage notice, publication closure verdict, public request contract/certificate/status/carryforward/notice/notice-normal-form/notice-selection/response-menu/response-packet/response-packet-carryforward/response-packet-delta/response-packet-refresh-notice/packet-refresh-notice-normal-form/packet-refresh-notice-selection, packet-refresh-response-menu, packet-refresh-response-packet, packet-refresh-response-packet-closure-verdict, answer-disclosure-packet artifacts, series spine, and question-routing catalog')

    inventory_paths = {entry.get('path') for group in artifact_inventory.get('groups', []) for entry in group.get('entries', [])}
    record('artifact inventory includes new public request artifacts', {'example_public_request_status_envelope.json', 'example_public_request_carryforward_envelope.json', 'example_public_request_notice.json', 'example_public_request_notice_normal_forms.json', 'example_public_request_notice_selections.json', 'example_public_request_response_menus.json', 'example_public_request_response_packets.json', 'example_public_request_response_packet_carryforward_profiles.json', 'example_public_request_response_packet_delta_ledgers.json', 'example_public_request_response_packet_refresh_notices.json', 'example_public_request_response_packet_refresh_notice_normal_forms.json', 'example_public_request_response_packet_refresh_notice_selections.json', 'example_public_request_response_packet_refresh_response_menus.json', 'example_public_request_response_packet_refresh_response_packets.json', 'example_public_request_response_packet_refresh_response_packet_closure_verdicts.json', 'example_release_spine.json', 'example_release_stage_walkthrough.json', 'example_question_routes.json'}.issubset(inventory_paths), f'missing={sorted(set(["example_public_request_status_envelope.json", "example_public_request_carryforward_envelope.json", "example_public_request_notice.json", "example_public_request_notice_normal_forms.json", "example_public_request_notice_selections.json", "example_public_request_response_menus.json", "example_public_request_response_packets.json", "example_public_request_response_packet_carryforward_profiles.json", "example_public_request_response_packet_delta_ledgers.json", "example_public_request_response_packet_refresh_notices.json", "example_public_request_response_packet_refresh_notice_normal_forms.json", "example_public_request_response_packet_refresh_notice_selections.json", "example_public_request_response_packet_refresh_response_menus.json", "example_public_request_response_packet_refresh_response_packets.json", "example_public_request_response_packet_refresh_response_packet_closure_verdicts.json", "example_release_spine.json", "example_release_stage_walkthrough.json", "example_question_routes.json"]) - inventory_paths)}')

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
    line_item_spines = series_spine.get('line_item_spines', [])
    line_item_spine_stop_rules_ok = all(entry.get('stop_when') and entry.get('widen_only_if') for entry in line_item_spines)
    record('series spine line-item stop rules', line_item_spine_stop_rules_ok, 'every packet-local ladder carries explicit stop_when and widen_only_if rules')
    line_item_spine_route_targets_ok = all(entry.get('route_local_reopen_artifact') == 'example_question_routes.json' for entry in line_item_spines)
    record('series spine line-item route-local reopen targets', line_item_spine_route_targets_ok, 'every packet-local ladder points widening back to example_question_routes.json')
    line_item_spine_sentence_rules_ok = all(
        isinstance(entry.get('packet_local_sentence_normal_form'), dict)
        and entry.get('packet_local_sentence_normal_form', {}).get('surface_text')
        and entry.get('packet_local_sentence_normal_form', {}).get('reopen_artifact') == 'example_question_routes.json'
        and entry.get('route_local_reopen_rule')
        for entry in line_item_spines
    )
    record('series spine line-item sentence/reopen rules', line_item_spine_sentence_rules_ok, f"line_item_spines={[entry.get('line_item_name') for entry in line_item_spines]}")
    minimal_bridge_stop_rules_ok = all(entry.get('stop_when') and entry.get('widen_only_if') for entry in series_spine.get('minimal_bridge_cuts', []))
    record('series spine minimal bridge stop rules', minimal_bridge_stop_rules_ok, f"minimal_bridge_tasks={[entry.get('task_key') for entry in series_spine.get('minimal_bridge_cuts', [])]}")
    minimal_bridge_sentence_rules_ok = all(entry.get('bridge_cut_sentence_normal_form') and entry.get('bridge_cut_reopen_artifact') == 'example_question_routes.json' and entry.get('bridge_cut_reopen_rule') for entry in series_spine.get('minimal_bridge_cuts', []))
    record('series spine minimal bridge sentence/reopen rules', minimal_bridge_sentence_rules_ok, f"minimal_bridge_tasks={[entry.get('task_key') for entry in series_spine.get('minimal_bridge_cuts', [])]}")
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
        and all(entry.get('canonical_owner') and entry.get('label') and entry.get('question') and entry.get('rung_sentence_normal_form') and entry.get('route_local_reopen_artifact') and entry.get('route_local_reopen_rule') and entry.get('stop_when') and entry.get('widen_only_if') and entry.get('why') for entry in source_only_request_ladder)
    )
    record('series spine source-only request ladder', source_only_ladder_ok, f"source_only_request_ladder={[entry.get('task_key') for entry in source_only_request_ladder]}")

    source_only_ladder_route_targets_ok = all(entry.get('route_local_reopen_artifact') == 'example_question_routes.json' for entry in source_only_request_ladder)
    record('series spine source-only request ladder route-local reopen targets', source_only_ladder_route_targets_ok, f"source_only_request_ladder={[entry.get('task_key') for entry in source_only_request_ladder]}")

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
        expected_terminal_citation_normal_form = {
            'anchor_order': ['public_anchor', 'checked_answer_card', 'answer_disclosure_packet', 'answer_review_menu'],
            'anchors': [
                {
                    'anchor_kind': 'public_anchor',
                    'cite_path': route.get('minimal_public_anchor_path'),
                    'object_kind': 'public_anchor',
                    'object_key': route.get('minimal_public_anchor_path'),
                },
                {
                    'anchor_kind': 'checked_answer_card',
                    'cite_path': 'example_successor_challenge_answer_cards.json',
                    'object_kind': 'answer_card',
                    'object_key': route.get('answer_card_key'),
                },
                {
                    'anchor_kind': 'answer_disclosure_packet',
                    'cite_path': 'example_successor_challenge_answer_disclosure_packets.json',
                    'object_kind': 'answer_disclosure_packet',
                    'object_key': route.get('disclosure_packet_key'),
                },
                {
                    'anchor_kind': 'answer_review_menu',
                    'cite_path': 'example_successor_challenge_answer_review_menus.json',
                    'object_kind': 'answer_review_menu',
                    'object_key': route.get('answer_review_menu_key'),
                },
            ],
            'default_inline_profile_key': route.get('default_inline_profile_key'),
            'default_visible_provenance_fields': route.get('default_visible_provenance_fields'),
            'reopen_if_request_classes': route.get('paired_terminal_answer_reopen_request_classes'),
            'widen_only_if': route.get('paired_terminal_widen_condition'),
            'why': 'This is the smallest maintained four-anchor checked-answer stop for the audience/question pair: public anchor, exact checked answer, exact answer-side omitted-support cut, and exact terminal referee handoff owner.',
        }
        expected_terminal_sentence_normal_form = {
            'surface_text': f"For the checked-answer path, stop at: {route.get('minimal_public_anchor_path')} -> {route.get('answer_card_key')} -> {route.get('disclosure_packet_key')} -> {route.get('answer_review_menu_key')}.",
            'anchor_order': ['public_anchor', 'checked_answer_card', 'answer_disclosure_packet', 'answer_review_menu'],
            'reopen_if_request_classes': route.get('paired_terminal_answer_reopen_request_classes'),
            'widen_only_if': route.get('paired_terminal_widen_condition'),
            'why': 'This sentence adds no new owner; it is only the one-clause rendering of the already-owned four-anchor answer-side terminal citation normal form.',
        }
        expected_answer_side_first_reopen_owner_map = {
            request_class: review_owner_index[request_class]
            for request_class in ['exact_location_check', 'full_audit_check', 'reveal_order_check']
            if request_class in review_owner_index
        }
        expected_paired_terminal_cutover_sentence_normal_form = {
            'surface_text': 'For the paired-terminal cutover, stop at the answer-side terminal form while the checked-answer path still exhausts the live question; widen exactly once to the adjacent request-side terminal form only after the live question has crossed the answer-side archive cut, the first sufficient adjacent owner bucket and exact request rung are already fixed, and the shipped request-side closure still stands; otherwise fail closed and reopen the named owner.',
            'request_terminal_artifact': 'example_public_request_response_packet_refresh_response_packet_closure_verdicts.json',
            'reopen_artifact': 'example_question_routes.json',
            'why': 'This is the smallest maintained cutover card for later terse papers: it does not re-own either terminal form, but it states when the paired shortcut still stops, when it may widen once, and when it must fail closed.'
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
            ('answer_side_terminal_citation_normal_form', route.get('answer_side_terminal_citation_normal_form') == (answer or {}).get('answer_side_terminal_citation_normal_form') == (review_menu or {}).get('answer_side_terminal_citation_normal_form') == expected_terminal_citation_normal_form),
            ('answer_side_terminal_sentence_normal_form', route.get('answer_side_terminal_sentence_normal_form') == (answer or {}).get('answer_side_terminal_sentence_normal_form') == (review_menu or {}).get('answer_side_terminal_sentence_normal_form') == expected_terminal_sentence_normal_form),
            ('answer_side_terminal_stop_when', route.get('answer_side_terminal_stop_when') == (answer or {}).get('answer_side_terminal_stop_when') == 'The live question is still exhausted by the checked answer, its answer-side disclosure-packet cut, and the review-menu handoff, so exact-location, full-audit, reveal-order, or a genuine crossing into the adjacent source-only branch has not yet become the live issue.'),
            ('answer_side_terminal_widen_only_if', route.get('answer_side_terminal_widen_only_if') == (answer or {}).get('answer_side_terminal_widen_only_if') == 'Widen only if the live question has genuinely crossed the answer-side archive cut into the adjacent source-only branch and the first sufficient adjacent owner bucket has already been fixed.'),
            ('answer_side_terminal_reopen_artifact', route.get('answer_side_terminal_reopen_artifact') == (answer or {}).get('answer_side_terminal_reopen_artifact') == 'example_question_routes.json'),
            ('answer_side_terminal_first_reopen_owner_map', route.get('answer_side_terminal_first_reopen_owner_map') == (answer or {}).get('answer_side_terminal_first_reopen_owner_map') == expected_answer_side_first_reopen_owner_map),
            ('answer_side_terminal_reopen_rule', route.get('answer_side_terminal_reopen_rule') == (answer or {}).get('answer_side_terminal_reopen_rule') == 'If exact-location, full-audit, or reveal-order becomes live, reopen example_question_routes.json and follow answer_side_terminal_first_reopen_owner_map to the first sufficient imported answer-side owner instead of staying at the terminal sentence.'),
            ('paired_terminal_cutover_sentence_normal_form', route.get('paired_terminal_cutover_sentence_normal_form') == (answer or {}).get('paired_terminal_cutover_sentence_normal_form') == expected_paired_terminal_cutover_sentence_normal_form),
            ('paired_terminal_stop_when', route.get('paired_terminal_stop_when') == (answer or {}).get('paired_terminal_stop_when') == 'The live issue is the cutover judgment itself: whether one branch still stops at the answer-side terminal form, may widen exactly once to the adjacent request-side terminal form, or must fail closed to a reopened owner.'),
            ('paired_terminal_request_terminal_artifact', route.get('paired_terminal_request_terminal_artifact') == (answer or {}).get('paired_terminal_request_terminal_artifact') == 'example_public_request_response_packet_refresh_response_packet_closure_verdicts.json'),
            ('paired_terminal_request_terminal_kind', route.get('paired_terminal_request_terminal_kind') == (answer or {}).get('paired_terminal_request_terminal_kind') == 'public_request_response_packet_refresh_response_packet_closure_verdict'),
            ('paired_terminal_request_terminal_widen_only_if', route.get('paired_terminal_request_terminal_widen_only_if') == (answer or {}).get('paired_terminal_request_terminal_widen_only_if') == 'Widen only if the live question has already fixed the first sufficient adjacent owner bucket and the first sufficient exact request rung, and the shipped request-side closure still stands with no named request-side reopen trigger fired.'),
            ('paired_terminal_reopen_artifact', route.get('paired_terminal_reopen_artifact') == (answer or {}).get('paired_terminal_reopen_artifact') == 'example_question_routes.json'),
            ('paired_terminal_fail_closed_reopen_rule', route.get('paired_terminal_fail_closed_reopen_rule') == (answer or {}).get('paired_terminal_fail_closed_reopen_rule') == "If exact-location, full-audit, reveal-order, followup_taxonomy_expands, packet_reuse_reopens, or visible_refresh_sentence_rebinds_to_new_delta_family becomes live, reopen example_question_routes.json and follow the answer-side first-reopen owner or the request-side closure verdict's reopen-owner map instead of citing a terminal shortcut."),
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
    record('answer review menu contract fields', bool(answer_review_menus.get('answer_review_menu_contract', {}).get('answer_review_menu_fields') == ['answer_review_menu_key', 'audience', 'question_key', 'sentence_family', 'answer_publication_profile_key', 'answer_citation_docket_key', 'answer_disclosure_packet_key', 'answer_escalation_ladder_key', 'answer_side_terminal_citation_normal_form', 'answer_side_terminal_sentence_normal_form', 'review_entries', 'start_path', 'minimal_path', 'why']), 'answer review menus now carry explicit four-anchor answer-side terminal citation and sentence normal-form fields in addition to the imported menu-selection fields')

    record('question routing contract fields', bool(question_routes.get('question_routes_id') == 'worked-example-question-routes-v1' and question_routes.get('series_spine_id') == series_spine.get('series_spine_id') and question_routes.get('successor_challenge_answer_review_menus_id') == answer_review_menus.get('challenge_answer_review_menus_id') and question_routes.get('successor_challenge_routes_id') == challenge_routes.get('challenge_routes_id') and question_routes.get('successor_challenge_stop_profiles_id') == challenge_stop_profiles.get('challenge_stop_profiles_id') and question_routes.get('successor_challenge_branches_id') == challenge_branches.get('challenge_branches_id') and question_routes.get('requestable_evidence_classes_id') == requestable_evidence_classes.get('requestable_evidence_classes_id') and question_routes.get('source_only_request_ladder') == series_spine.get('source_only_request_ladder') and question_contract.get('generic_question_route_fields') == ['route_key', 'question_examples', 'stop_kind', 'spine_segment', 'bucket_key', 'first_stop_owner', 'first_stop_artifact', 'next_route_keys_if_scope_widens', 'why'] and question_contract.get('audience_question_route_fields') == ['route_key', 'audience', 'question_key', 'challenge_route_key', 'stop_profile_key', 'minimal_public_anchor_path', 'sentence_family', 'answer_card_key', 'sentence_lock_key', 'sentence_reuse_status', 'default_inline_profile_key', 'default_visible_provenance_fields', 'answer_review_menu_key', 'answer_side_terminal_citation_normal_form', 'answer_side_terminal_sentence_normal_form', 'answer_side_terminal_stop_when', 'answer_side_terminal_widen_only_if', 'answer_side_terminal_reopen_artifact', 'answer_side_terminal_first_reopen_owner_map', 'answer_side_terminal_reopen_rule', 'publication_profile_key', 'publication_budget_map', 'answer_review_request_class_mode_map', 'answer_escalation_step_mode_map', 'paired_terminal_answer_reopen_request_classes', 'paired_terminal_cutover_mode', 'paired_terminal_widen_condition', 'paired_terminal_request_reopen_triggers', 'paired_terminal_cutover_sentence_normal_form', 'paired_terminal_stop_when', 'paired_terminal_request_terminal_artifact', 'paired_terminal_request_terminal_kind', 'paired_terminal_request_terminal_widen_only_if', 'paired_terminal_reopen_artifact', 'paired_terminal_fail_closed_reopen_rule', 'request_class_handoff_map', 'request_class_owner_map', 'release_obligation_profile_id', 'release_closure_ledger_id', 'publication_closure_verdict_id', 'publication_closure_status', 'successor_status_envelope_id', 'successor_public_status_token', 'successor_lineage_notice_id', 'public_request_contract_key', 'source_only_public_anchor_family_mode_map', 'source_only_request_fulfillment_certificate_keys', 'source_only_family_completion_map', 'source_only_family_completion_mode_map', 'source_only_evidence_class_mode_map', 'source_only_status_envelope_key', 'source_only_status_token', 'source_only_status_token_mode_map', 'source_only_carryforward_envelope_key', 'source_only_carryforward_token', 'source_only_carryforward_token_mode_map', 'source_only_notice_key_map', 'source_only_notice_normal_form_map', 'source_only_notice_selection_keys', 'source_only_response_menu_keys', 'source_only_response_menu_followup_class_mode_map', 'source_only_request_class_handoff_map', 'source_only_request_class_owner_map', 'source_only_response_packet_map', 'source_only_response_packet_scope_mode_map', 'source_only_response_packet_family_basis_map', 'source_only_response_packet_support_surface_map', 'source_only_response_packet_manifest_cut_map', 'source_only_response_packet_inventory_cut_map', 'source_only_response_packet_carryforward_profile_map', 'source_only_response_packet_reuse_status_map', 'source_only_response_packet_refresh_family_mode_map', 'source_only_response_packet_delta_map', 'source_only_response_packet_delta_family_mode_map', 'source_only_refresh_notice_map', 'source_only_refresh_notice_normal_form_map', 'source_only_refresh_notice_selection_map', 'source_only_refresh_response_menu_map', 'source_only_refresh_followup_handoff_map', 'source_only_refresh_followup_owner_map', 'source_only_refresh_response_packet_map', 'source_only_refresh_response_packet_family_basis_map', 'source_only_refresh_response_packet_support_surface_map', 'source_only_refresh_response_packet_manifest_cut_map', 'source_only_refresh_response_packet_inventory_cut_map', 'source_only_refresh_response_packet_validation_mode_map', 'source_only_refresh_response_packet_closure_map', 'source_only_refresh_response_packet_closure_status_map', 'source_only_refresh_response_packet_closure_scope_map', 'source_only_refresh_response_packet_reopen_trigger_map', 'source_only_refresh_response_packet_reopen_owner_map', 'source_only_request_ladder', 'citation_docket_key', 'answer_carrier_slot_key', 'answer_audit_trail_key', 'disclosure_packet_key', 'disclosure_packet_support_surface', 'disclosure_packet_manifest_cut', 'disclosure_packet_inventory_cut', 'evidence_class_keys', 'escalation_ladder_key', 'supporting_line_item_names', 'release_stage_families', 'release_stage_vocabulary_mode_map', 'available_request_classes', 'why'] and question_contract.get('stable_ladder_fields') == ['position', 'task_key', 'spine_segment', 'label', 'canonical_owner', 'artifact', 'question', 'stop_when', 'widen_only_if', 'why'] and question_contract.get('source_only_request_ladder_fields') == ['position', 'task_key', 'bucket_key', 'label', 'canonical_owner', 'note_range', 'artifact', 'question', 'rung_sentence_normal_form', 'route_local_reopen_artifact', 'route_local_reopen_rule', 'stop_when', 'widen_only_if', 'why'] and question_contract.get('widening_rule') and question_contract.get('public_anchor_rule') and question_contract.get('audience_stop_rule')), 'question routing catalog links the series spine, stop profiles, answer cards, sentence locks, publication-budget maps, six-class request handoff maps, mirrored answer-review request-class / answer-escalation-step / release-stage vocabulary posture maps, six-class request owner maps, route-side release-obligation-profile / release-closure-ledger / publication-closure-verdict / successor-status-envelope / successor-lineage-notice bindings plus the imported public-status token, the paper-level source-only request contract, route-side public-anchor-family-vocabulary / fulfillment-certificate / family-completion-vocabulary / evidence-class-vocabulary / status-token / carryforward-token bridges plus status-token / carryforward-token vocabulary maps, source-only notice / canonical-notice-family / notice-selection surfaces, notice-keyed source-only response menus plus source-only response-menu followup-vocabulary maps, source-only request-class handoff / owner maps, exact bounded source-only response packets plus response-packet-scope / packet-family-basis / packet-support-surface / packet-manifest-cut / packet-inventory-cut maps together with packet-reuse / packet-family-mode / packet-delta / packet-delta-family-mode / refresh-family-mode bridges, successor refresh-notice / canonical-refresh-family / refresh-notice-selection / refresh-response-menu / successor-followup handoff / owner maps, exact successor packets plus successor-packet-family-basis / successor-packet-support-surface / successor-packet-manifest-cut / successor-packet-inventory-cut / successor-packet-validation-posture / closure / closure-status / closure-scope / reopen-trigger / reopen-owner maps, citation dockets, answer carrier slots, answer audit trails, disclosure packets plus disclosure-packet support-surface / manifest-cut / inventory-cut bindings, escalation ladders, branch maps, review menus together with explicit answer-side terminal normal-form fields, evidence classes, and both route-field contracts')

    contract = series_spine.get('series_spine_contract', {})
    record('series spine contract fields', bool(contract.get('line_item_spine_fields') == ['line_item_name', 'math_roots', 'receipt_anchor', 'replay_anchor', 'release_anchor', 'review_anchor', 'packet_local_sentence_normal_form', 'stop_when', 'widen_only_if', 'route_local_reopen_artifact', 'route_local_reopen_rule', 'why'] and contract.get('optional_variant_spine_fields') == ['line_item_name', 'materialization_status', 'receipt_variant_file', 'evidence_id', 'receipt_anchor', 'owner_map_anchor', 'replay_anchor', 'support_anchor', 'variant_sentence_normal_form', 'stop_when', 'widen_only_if', 'route_local_reopen_artifact', 'route_local_reopen_rule', 'why'] and contract.get('answer_spine_fields') == ['audience', 'question_key', 'challenge_route_key', 'stop_profile_key', 'answer_review_menu_key', 'answer_side_terminal_citation_normal_form', 'answer_side_terminal_sentence_normal_form', 'answer_side_terminal_stop_when', 'answer_side_terminal_widen_only_if', 'answer_side_terminal_reopen_artifact', 'answer_side_terminal_first_reopen_owner_map', 'answer_side_terminal_reopen_rule', 'start_path', 'sentence_family', 'answer_card_key', 'sentence_lock_key', 'sentence_reuse_status', 'default_inline_profile_key', 'default_visible_provenance_fields', 'supporting_line_item_names', 'release_stage_families', 'release_stage_vocabulary_mode_map', 'publication_profile_key', 'publication_budget_map', 'answer_review_request_class_mode_map', 'answer_escalation_step_mode_map', 'paired_terminal_answer_reopen_request_classes', 'paired_terminal_cutover_mode', 'paired_terminal_widen_condition', 'paired_terminal_request_reopen_triggers', 'paired_terminal_cutover_sentence_normal_form', 'paired_terminal_stop_when', 'paired_terminal_request_terminal_artifact', 'paired_terminal_request_terminal_kind', 'paired_terminal_request_terminal_widen_only_if', 'paired_terminal_reopen_artifact', 'paired_terminal_fail_closed_reopen_rule', 'request_class_handoff_map', 'request_class_owner_map', 'release_obligation_profile_id', 'release_closure_ledger_id', 'publication_closure_verdict_id', 'publication_closure_status', 'successor_status_envelope_id', 'successor_public_status_token', 'successor_lineage_notice_id', 'public_request_contract_key', 'source_only_public_anchor_family_mode_map', 'source_only_request_fulfillment_certificate_keys', 'source_only_family_completion_map', 'source_only_family_completion_mode_map', 'source_only_evidence_class_mode_map', 'source_only_status_envelope_key', 'source_only_status_token', 'source_only_status_token_mode_map', 'source_only_carryforward_envelope_key', 'source_only_carryforward_token', 'source_only_carryforward_token_mode_map', 'source_only_notice_key_map', 'source_only_notice_normal_form_map', 'source_only_notice_selection_keys', 'source_only_response_menu_keys', 'source_only_response_menu_followup_class_mode_map', 'source_only_request_class_handoff_map', 'source_only_request_class_owner_map', 'source_only_response_packet_map', 'source_only_response_packet_scope_mode_map', 'source_only_response_packet_family_basis_map', 'source_only_response_packet_support_surface_map', 'source_only_response_packet_manifest_cut_map', 'source_only_response_packet_inventory_cut_map', 'source_only_response_packet_carryforward_profile_map', 'source_only_response_packet_reuse_status_map', 'source_only_response_packet_refresh_family_mode_map', 'source_only_response_packet_delta_map', 'source_only_response_packet_delta_family_mode_map', 'source_only_refresh_notice_map', 'source_only_refresh_notice_normal_form_map', 'source_only_refresh_notice_selection_map', 'source_only_refresh_response_menu_map', 'source_only_refresh_followup_handoff_map', 'source_only_refresh_followup_owner_map', 'source_only_refresh_response_packet_map', 'source_only_refresh_response_packet_family_basis_map', 'source_only_refresh_response_packet_support_surface_map', 'source_only_refresh_response_packet_manifest_cut_map', 'source_only_refresh_response_packet_inventory_cut_map', 'source_only_refresh_response_packet_validation_mode_map', 'source_only_refresh_response_packet_closure_map', 'source_only_refresh_response_packet_closure_status_map', 'source_only_refresh_response_packet_closure_scope_map', 'source_only_refresh_response_packet_reopen_trigger_map', 'source_only_refresh_response_packet_reopen_owner_map', 'source_only_request_ladder', 'citation_docket_key', 'answer_carrier_slot_key', 'answer_audit_trail_key', 'disclosure_packet_key', 'disclosure_packet_support_surface', 'disclosure_packet_manifest_cut', 'disclosure_packet_inventory_cut', 'evidence_class_keys', 'escalation_ladder_key', 'why'] and contract.get('stable_ladder_fields') == ['position', 'task_key', 'spine_segment', 'label', 'canonical_owner', 'artifact', 'question', 'stop_when', 'widen_only_if', 'why'] and contract.get('source_only_request_ladder_fields') == ['position', 'task_key', 'bucket_key', 'label', 'canonical_owner', 'note_range', 'artifact', 'question', 'rung_sentence_normal_form', 'route_local_reopen_artifact', 'route_local_reopen_rule', 'stop_when', 'widen_only_if', 'why'] and contract.get('minimal_bridge_cut_fields') == ['task_key', 'stop_kind', 'spine_segment', 'bucket_key', 'canonical_owner', 'artifact', 'question', 'bridge_cut_sentence_normal_form', 'bridge_cut_reopen_artifact', 'bridge_cut_reopen_rule', 'stop_when', 'widen_only_if', 'why'] and contract.get('source_only_owner_bucket_fields') == ['bucket_key', 'note_range', 'first_question', 'artifacts', 'bucket_sentence_normal_form', 'route_local_reopen_artifact', 'route_local_first_rung_owner', 'route_local_first_rung_artifact', 'route_local_reopen_rule', 'stop_when', 'widen_only_if', 'why'] and contract.get('adjacent_owner_bucket_rule')), 'series spine contract names line-item spine fields with explicit packet-local stop/widen/reopen targets, optional variant spine fields with receipt/evidence/replay/support anchors, answer-spine fields, explicit answer-side terminal normal-form fields, publication-budget-map fields, six-class request handoff-map fields, mirrored answer-escalation-step vocabulary fields, mirrored release-stage-vocabulary posture-map fields, six-class request owner-map fields, release-obligation / closure-ledger / closure-verdict / status-envelope / lineage-notice bridge fields, public-request-contract / public-anchor-family-vocabulary / fulfillment-certificate / family-completion-vocabulary / evidence-class-vocabulary / status-token / carryforward-token / status-token-vocabulary / carryforward-token-vocabulary / notice / canonical-notice-family / notice-normal-form / notice-selection / response-menu / response-menu-followup-vocabulary / source-only request-class handoff / source-only request-class owner / bounded-response-packet / response-packet-scope / packet-family-basis / packet-support-surface / packet-manifest-cut / packet-inventory-cut / packet-carryforward / packet-family-mode / packet-delta / delta-family-mode / refresh-notice / canonical-refresh-family / refresh-normal-form / refresh-selection / refresh-response-menu / successor-followup handoff / successor-followup owner / successor-packet / successor-packet-family-basis / successor-packet-support-surface / successor-packet-manifest-cut / successor-packet-inventory-cut / successor-packet-validation-posture / closure / closure-status / closure-scope / reopen-trigger / reopen-owner fields, disclosure-packet support-surface / disclosure-packet manifest-cut / disclosure-packet inventory-cut fields, minimal-bridge-cut sentence/reopen fields, source-only-owner-bucket sentence/reopen fields, and the adjacent owner-bucket stop rule plus the explicit source-only-request-ladder field contract')

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
        'note': 'Validation report for the worked example support bundle, including the theorem-to-review series-spine routing cuts, question-routing catalog, emitted-answer / sentence-lock reuse bindings, route-side citation-docket / disclosure-packet / disclosure-packet support-surface / disclosure-packet manifest-cut / disclosure-packet inventory-cut / escalation-ladder bindings, imported six-class request handoff maps, route-side release-obligation-profile / release-closure-ledger / publication-closure-verdict / successor-status-envelope / successor-lineage-notice bindings plus the imported public-status token, source-only owner buckets with explicit bucket-sentence / route-local-reopen fields, the route-side notice / canonical-notice-family / notice-normal-form / selection bridge, the route-side successor packet-reuse posture / delta / refresh-notice / canonical-refresh-family / refresh-normal-form / refresh-selection / refresh-response-menu / successor-packet / successor-packet-family-basis / successor-packet-support-surface / successor-packet-manifest-cut / successor-packet-inventory-cut / successor-packet-validation-posture / closure maps, and the public-request fulfillment-certificate, family-completion-vocabulary, status, carryforward, status-token-vocabulary, carryforward-token-vocabulary, notice, notice-normal-form, notice-selection, response-menu, response-packet, response-packet-carryforward, response-packet-delta, packet-refresh-notice, packet-refresh-notice-normal-form, packet-refresh-notice-selection, packet-refresh-response-menu, packet-refresh-response-packet, packet-refresh-response-packet-closure-verdict, and route-level response-menu followup-vocabulary / response-packet-scope / packet-reuse posture / closure-status / closure-scope / reopen-trigger / packet-manifest-cut / packet-inventory-cut / disclosure-packet manifest-cut / disclosure-packet inventory-cut bindings now mirrored beside the explicit source-only successor-packet validation-posture bridge, including the shared-versus-family-local source-only evidence split, the mirrored source-only evidence-class-vocabulary map, the mirrored source-only response-menu-followup-vocabulary and response-packet-scope maps, the mirrored source-only packet-family-mode and packet-delta-family-mode maps, explicit stop-here / widen-only-if bridge rules for both the release-spine stage-order rows, the six-stop stable ladder, and the eighteen-step source-only request ladder, the answer-side disclosure-packet first-stop route, the mirrored source-only packet reuse status map, the mirrored visible-refresh branch closure status map, the mirrored visible-refresh branch closure scope map, the mirrored visible-refresh reopen-trigger map, the mirrored visible-refresh reopen-owner map, and the README current-cut guard.'
    }
    (ART / 'example_validation_report.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    if not ok:
        failed = [c['name'] for c in checks if not c['ok']]
        print('validation failed:', '; '.join(failed), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
