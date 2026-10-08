#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, NamedTuple
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
KIT_PATH = ROOT / 'CHATGPT-FIRST-PROOF-KIT.json'
DEFAULT_INPUT = ROOT / 'validation' / 'latest' / 'chatgpt-first-proof-capture.json'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-first-proof-evaluation'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'chatgpt-first-proof-evaluation-captures.json'

REVIEWABLE_VERDICT = 'reviewable-no-claim-widening'
BLOCKED_VERDICT = 'blocked'
REHEARSAL_VERDICT = 'rehearsal-harness-ok-not-live'
IMPLICIT_ATTEMPT_ID = '__implicit_attempt__'
ATTEMPT_KEYS = ('attempt_id', 'run_id', 'bundle_id', 'proof_id', 'session_id', 'capture_id')
CHATGPT_ADAPTER_VALUES = {'chatgpt'}
OPERATOR_SUBMIT_METHODS = {'sidepanel-operator-click', 'manual-operator-click', 'operator-click'}
SETTLED_GENERATION_STATES = {'settled-or-idle', 'settled', 'idle', 'complete', 'completed'}
EMAIL_RE = re.compile(r'(?<![\w.+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![\w.+-])')
TOKEN_HINT_RE = re.compile(r'(?i)\b(?:bearer\s+[A-Za-z0-9._~+/=-]{12,}|access[_-]?token|refresh[_-]?token|session[_-]?id|id[_-]?token|sk-[A-Za-z0-9]{12,})\b')
RAW_HTML_RE = re.compile(r'<(?:html|body|main|div|textarea|button|article|section|form|input|script|style)\b', re.IGNORECASE)
SCHEMA_VERSION = 20
REQUIRED_CHECKS = (
    'adapter_is_chatgpt',
    'host_is_chatgpt',
    'route_posture_is_plain_chat',
    'composer_write_readback_contains_probe',
    'submit_action_ok',
    'latest_turn_exact_reply',
    'transcript_latest_action_exact_reply',
    'ordered_write_submit_latest_sequence',
    'explicit_sequence_indices_monotonic',
    'ordered_sequence_has_chatgpt_action_witnesses',
    'post_submit_conversation_route_witness',
    'post_submit_conversation_route_transition',
    'proof_chain_same_tab_context',
    'post_latest_settled_witness_same_conversation_route',
    'operator_submit_attestation_present',
    'proof_live_gate_ok_before_submit',
    'submit_prompt_readback_matches_probe',
    'write_and_submit_readbacks_exact_probe',
    'post_latest_generation_settled_witness',
    'post_latest_settled_witness_sequence_and_surface',
    'transcript_latest_assistant_node_witness',
    'transcript_latest_witness_text_matches_reply',
    'transcript_latest_assistant_witness_not_aggregate_parent',
    'transcript_latest_user_turn_witness_text_matches_prompt',
    'transcript_latest_user_witness_not_aggregate_parent',
    'transcript_latest_user_before_assistant_witness_order',
    'transcript_latest_turn_pair_explicit_frame_context',
    'action_policy_supports_route_safe_submit',
    'privacy_redaction_review_present',
    'single_coherent_attempt_has_required_evidence',
    'no_cross_surface_conflicts',
)


GLOBAL_ONLY_CHECKS = (
    'privacy_redaction_review_present',
    'single_coherent_attempt_has_required_evidence',
    'no_cross_surface_conflicts',
)
ATTEMPT_SCOPED_CHECKS = tuple(key for key in REQUIRED_CHECKS if key not in GLOBAL_ONLY_CHECKS)


def duplicate_required_checks() -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for key in REQUIRED_CHECKS:
        if key in seen and key not in duplicates:
            duplicates.append(key)
        seen.add(key)
    return duplicates


def required_check_registry_audit() -> dict[str, Any]:
    required = list(REQUIRED_CHECKS)
    global_only = list(GLOBAL_ONLY_CHECKS)
    attempt_scoped = list(ATTEMPT_SCOPED_CHECKS)
    partition = set(global_only) | set(attempt_scoped)
    required_set = set(required)
    duplicates = duplicate_required_checks()
    unknown_global = [key for key in global_only if key not in required_set]
    missing_from_partition = [key for key in required if key not in partition]
    extra_in_partition = [key for key in global_only + attempt_scoped if key not in required_set]
    overlap = [key for key in global_only if key in attempt_scoped]
    ok = not (duplicates or unknown_global or missing_from_partition or extra_in_partition or overlap)
    return {
        'ok': ok,
        'required_check_count': len(required),
        'attempt_scoped_check_count': len(attempt_scoped),
        'global_only_check_count': len(global_only),
        'duplicates': duplicates,
        'unknown_global_only_checks': unknown_global,
        'missing_from_partition': missing_from_partition,
        'extra_in_partition': extra_in_partition,
        'overlap_between_global_and_attempt_scoped': overlap,
        'attempt_scoped_checks': attempt_scoped,
        'global_only_checks': global_only,
    }


def merge_required_checks(
    attempts: list[dict[str, Any]],
    *,
    winning_attempt: dict[str, Any] | None,
    global_no_conflicts: bool,
    global_privacy_redaction_review_present: bool,
) -> dict[str, bool]:
    global_values = {
        'privacy_redaction_review_present': global_privacy_redaction_review_present,
        'single_coherent_attempt_has_required_evidence': winning_attempt is not None,
        'no_cross_surface_conflicts': global_no_conflicts,
    }
    checks: dict[str, bool] = {}
    for key in REQUIRED_CHECKS:
        if key in global_values:
            checks[key] = bool(global_values[key])
        else:
            checks[key] = any(bool((attempt.get('checks') or {}).get(key)) for attempt in attempts)
    return checks


class EvidenceRecord(NamedTuple):
    item: dict[str, Any]
    attempt_id: str
    path: str
    ordinal: int


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()




def display_path(path: Path | None, *, root: Path = ROOT) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except Exception:
        return str(path)


def load_probe_contract(root: Path = ROOT) -> dict[str, str]:
    kit_path = root / 'CHATGPT-FIRST-PROOF-KIT.json'
    kit = read_json(kit_path)
    probe = kit.get('probe_prompt') if isinstance(kit, dict) else None
    if not isinstance(probe, dict):
        raise ValueError(f'{kit_path} missing probe_prompt object')
    text = str(probe.get('text') or '').strip()
    expected = str(probe.get('expected_exact_reply') or '').strip()
    if not text or not expected:
        raise ValueError(f'{kit_path} missing probe prompt text or expected_exact_reply')
    return {'probe_text': text, 'expected_exact_reply': expected}


def iter_dicts(value: Any) -> list[dict[str, Any]]:
    return [record.item for record in iter_evidence_records(value)]


def _attempt_id_from_dict(item: dict[str, Any]) -> str | None:
    for key in ATTEMPT_KEYS:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    metadata = item.get('metadata')
    if isinstance(metadata, dict):
        for key in ATTEMPT_KEYS:
            value = metadata.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    payload = item.get('payload')
    if isinstance(payload, dict):
        for key in ATTEMPT_KEYS:
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def iter_evidence_records(value: Any) -> list[EvidenceRecord]:
    records: list[EvidenceRecord] = []

    def walk(item: Any, attempt_id: str, path: str) -> None:
        if isinstance(item, dict):
            next_attempt = _attempt_id_from_dict(item) or attempt_id
            records.append(EvidenceRecord(item=item, attempt_id=next_attempt, path=path, ordinal=len(records)))
            for key, child in item.items():
                walk(child, next_attempt, f'{path}.{key}')
        elif isinstance(item, list):
            for index, child in enumerate(item):
                walk(child, attempt_id, f'{path}[{index}]')

    walk(value, IMPLICIT_ATTEMPT_ID, '$')
    return records


def compact(value: Any) -> str:
    if not isinstance(value, str):
        return ''
    return ' '.join(value.split()).strip()




def payload_declares_rehearsal(value: Any) -> bool:
    """Return True when a bundle is explicitly marked as an offline rehearsal.

    Rehearsals are useful for proving the evaluator/CLI path still works while
    live ChatGPT access is unavailable, but they must never be allowed to look
    like a live proof.  The scan is deliberately broad so a nested fixture flag
    cannot be hidden under captures/actions/artifacts.
    """
    if isinstance(value, dict):
        mode = compact(value.get('proof_mode') or value.get('mode') or value.get('run_mode')).lower()
        if truthy(value.get('rehearsal_only')) or truthy(value.get('dry_run')):
            return True
        if mode in {'offline-rehearsal', 'rehearsal', 'dry-run', 'fixture-rehearsal'}:
            return True
        return any(payload_declares_rehearsal(child) for child in value.values())
    if isinstance(value, list):
        return any(payload_declares_rehearsal(child) for child in value)
    return False

def dict_text(item: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return compact(value)
    return ''


def nested_text(item: dict[str, Any], *path: str) -> str:
    cur: Any = item
    for key in path:
        if not isinstance(cur, dict):
            return ''
        cur = cur.get(key)
    return compact(cur)


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {'true', 'yes', 'ok', 'success', 'succeeded', 'passed'}
    return bool(value)


def falsey(value: Any) -> bool:
    if isinstance(value, bool):
        return not value
    if isinstance(value, str):
        return value.strip().lower() in {'false', 'no', 'disabled', 'off'}
    return value is False


def collect_urls(dicts: list[dict[str, Any]]) -> list[str]:
    keys = {'url', 'page_url', 'active_url', 'route_url', 'current_url', 'payload_url'}
    urls: list[str] = []
    seen: set[str] = set()
    for item in dicts:
        for key, value in item.items():
            if key in keys and isinstance(value, str) and value.strip() and value not in seen:
                urls.append(value)
                seen.add(value)
    return urls


def host_is_chatgpt(url: str) -> bool:
    try:
        host = urlparse(url).hostname or ''
    except Exception:
        return False
    return host == 'chatgpt.com' or host.endswith('.chatgpt.com')


def chatgpt_conversation_route(url: str) -> bool:
    return chatgpt_conversation_path(url) is not None


def chatgpt_conversation_path(url: str) -> str | None:
    try:
        parsed = urlparse(url)
    except Exception:
        return None
    if not host_is_chatgpt(url):
        return None
    parts = [part for part in parsed.path.split('/') if part]
    if len(parts) >= 2 and parts[0] == 'c' and parts[1].strip():
        return f'/c/{parts[1]}'
    return None


def collect_adapters(dicts: list[dict[str, Any]]) -> list[str]:
    adapters: list[str] = []
    for item in dicts:
        for key in ('adapter', 'adapter_name', 'adapterName', 'surface_adapter', 'payload_adapter'):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                adapters.append(value.strip().lower())
    return adapters


def collect_route_postures(dicts: list[dict[str, Any]]) -> list[str]:
    postures: list[str] = []
    for item in dicts:
        direct = dict_text(item, 'route_posture', 'surface_posture')
        if direct:
            postures.append(direct.lower())
        metadata = item.get('metadata')
        if isinstance(metadata, dict):
            nested = dict_text(metadata, 'route_posture', 'surface_posture')
            if nested:
                postures.append(nested.lower())
    return postures


def action_type(item: dict[str, Any]) -> str:
    return dict_text(item, 'type', 'action', 'event', 'event_type', 'request_type', 'response_type').lower()


def action_ok(item: dict[str, Any]) -> bool:
    payload = item.get('payload') if isinstance(item.get('payload'), dict) else {}
    return truthy(item.get('ok')) or truthy(item.get('success')) or truthy(payload.get('ok'))



def _item_payload(item: dict[str, Any]) -> dict[str, Any]:
    payload = item.get('payload')
    return payload if isinstance(payload, dict) else {}


def _intish(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def record_sequence_index(record: EvidenceRecord) -> int | None:
    item = record.item
    payload = _item_payload(item)
    for value in (item.get('sequence_index'), item.get('sequenceIndex'), payload.get('sequence_index'), payload.get('sequenceIndex')):
        parsed = _intish(value)
        if parsed is not None:
            return parsed
    return None


def record_urls(item: dict[str, Any]) -> list[str]:
    keys = {'url', 'page_url', 'active_url', 'route_url', 'current_url', 'payload_url'}
    payload = _item_payload(item)
    urls: list[str] = []
    seen: set[str] = set()
    for container in (item, payload):
        for key, value in container.items():
            if key in keys and isinstance(value, str) and value.strip() and value not in seen:
                urls.append(value)
                seen.add(value)
    return urls


def record_adapters(item: dict[str, Any]) -> list[str]:
    keys = ('adapter', 'adapter_name', 'adapterName', 'surface_adapter', 'payload_adapter')
    payload = _item_payload(item)
    adapters: list[str] = []
    for container in (item, payload):
        for key in keys:
            value = container.get(key)
            if isinstance(value, str) and value.strip():
                adapters.append(value.strip().lower())
    return adapters


def record_tab_id(record: EvidenceRecord) -> int | None:
    item = record.item
    payload = _item_payload(item)
    metadata = item.get('metadata') if isinstance(item.get('metadata'), dict) else {}
    payload_metadata = payload.get('metadata') if isinstance(payload.get('metadata'), dict) else {}
    for container in (item, payload, metadata, payload_metadata):
        if not isinstance(container, dict):
            continue
        for key in ('tab_id', 'tabId', 'target_tab_id', 'targetTabId'):
            parsed = _intish(container.get(key))
            if parsed is not None and parsed >= 0:
                return parsed
    return None


def action_record_witness(record: EvidenceRecord) -> dict[str, Any]:
    urls = record_urls(record.item)
    adapters = record_adapters(record.item)
    tab_id = record_tab_id(record)
    conversation_paths = sorted({path for url in urls if (path := chatgpt_conversation_path(url))})
    return {
        'path': record.path,
        'type': action_type(record.item),
        'sequence_index': record_sequence_index(record),
        'tab_id': tab_id,
        'has_explicit_tab_id': isinstance(tab_id, int),
        'adapters': sorted(dict.fromkeys(adapters)),
        'urls': urls,
        'adapter_is_chatgpt': 'chatgpt' in adapters,
        'host_is_chatgpt': any(host_is_chatgpt(url) for url in urls),
        'conversation_route_is_chatgpt_chat': bool(conversation_paths),
        'conversation_route_paths': conversation_paths,
    }


def text_candidates(item: dict[str, Any], keys: set[str]) -> list[str]:
    values: list[str] = []
    for key in keys:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            values.append(compact(value))
    payload = item.get('payload')
    if isinstance(payload, dict):
        for key in keys:
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                values.append(compact(value))
    return values


def has_composer_write_readback(dicts: list[dict[str, Any]], probe_text: str) -> bool:
    probe = compact(probe_text)
    for item in dicts:
        item_type = action_type(item)
        if not action_ok(item):
            continue
        if 'write' not in item_type:
            continue
        texts = [
            dict_text(item, 'readback', 'composer_readback', 'written_text'),
            nested_text(item, 'payload', 'readback'),
            nested_text(item, 'payload', 'composer_readback'),
            nested_text(item, 'payload', 'written_text'),
        ]
        if any(text == probe or probe in text for text in texts if text):
            return True
    return False


def has_submit_ok(dicts: list[dict[str, Any]]) -> bool:
    for item in dicts:
        item_type = action_type(item)
        payload = item.get('payload') if isinstance(item.get('payload'), dict) else {}
        if action_ok(item) and ('submit' in item_type or item.get('submit_ok') is True or payload.get('submit_ok') is True):
            return True
    return False


def has_latest_exact_reply(dicts: list[dict[str, Any]], expected: str) -> bool:
    exact = compact(expected)
    candidate_keys = {
        'latest_output',
        'latest_turn',
        'assistant_text',
        'assistant_reply',
        'transcript_latest',
        'transcript',
        'output',
        'text',
    }
    for item in dicts:
        item_type = action_type(item)
        latest_context = 'latest' in item_type or 'transcript' in item_type or 'fixture' in item_type
        for key, value in item.items():
            if key not in candidate_keys or not isinstance(value, str):
                continue
            text = compact(value)
            if text == exact and (latest_context or key != 'text'):
                return True
        payload = item.get('payload') if isinstance(item.get('payload'), dict) else None
        if payload and latest_context:
            for key in candidate_keys:
                text = compact(payload.get(key))
                if text == exact:
                    return True
    return False


def transcript_latest_exact_records(records: list[EvidenceRecord], expected: str) -> list[EvidenceRecord]:
    exact = compact(expected)
    candidate_keys = {
        'latest_output',
        'latest_turn',
        'assistant_text',
        'assistant_reply',
        'transcript_latest',
        'transcript',
        'output',
        'text',
    }
    matches: list[EvidenceRecord] = []
    for record in records:
        item_type = action_type(record.item)
        if item_type != 'transcript.latest' and not (item_type.endswith('.latest') and 'transcript' in item_type):
            continue
        if any(text == exact for text in text_candidates(record.item, candidate_keys)):
            matches.append(record)
    return matches


def _latest_witness_dicts(item: dict[str, Any]) -> list[dict[str, Any]]:
    payload = _item_payload(item)
    metadata = item.get('metadata') if isinstance(item.get('metadata'), dict) else {}
    payload_metadata = payload.get('metadata') if isinstance(payload.get('metadata'), dict) else {}
    out: list[dict[str, Any]] = []
    for container in (item, payload, metadata, payload_metadata):
        if not isinstance(container, dict):
            continue
        witness = container.get('latest_output_witness')
        if isinstance(witness, dict):
            out.append(witness)
        # Older fixture captures placed witness facts directly in metadata. Keep
        # these as low-trust candidates only when they include the selector/policy
        # fields produced by the executable adapter.
        if any(key in container for key in ('latest_output_assistant_like', 'latest_output_author_role', 'latest_output_selector', 'latest_output_order_policy')):
            out.append(container)
    return out


def _witness_bool(value: Any) -> bool:
    return truthy(value)


def _latest_output_witness_is_assistant_like(witness: dict[str, Any]) -> bool:
    assistant_like = _witness_bool(witness.get('assistant_like')) or _witness_bool(witness.get('latest_output_assistant_like'))
    author_role = compact(witness.get('author_role') or witness.get('latest_output_author_role') or witness.get('data_message_author_role')).lower()
    selector = compact(witness.get('selector_hint') or witness.get('latest_output_selector'))
    policy = compact(witness.get('selection_policy') or witness.get('latest_output_order_policy')).lower()
    policy_ok = policy == 'latest-visible-assistant-like-node-in-dom-order'
    return bool(selector and policy_ok and (assistant_like or author_role == 'assistant'))


def _latest_output_witness_text(witness: dict[str, Any]) -> str:
    return compact(witness.get('text') or witness.get('latest_output_text') or witness.get('latest_output'))


def latest_output_assistant_witness(item: dict[str, Any]) -> bool:
    return any(_latest_output_witness_is_assistant_like(witness) for witness in _latest_witness_dicts(item))


def latest_output_assistant_witness_text_matches(item: dict[str, Any], expected: str) -> bool:
    exact = compact(expected)
    if not exact:
        return False
    for witness in _latest_witness_dicts(item):
        if _latest_output_witness_is_assistant_like(witness) and _latest_output_witness_text(witness) == exact:
            return True
    return False


def transcript_latest_assistant_witness_records(records: list[EvidenceRecord], expected: str) -> list[EvidenceRecord]:
    exact_records = set(id(record) for record in transcript_latest_exact_records(records, expected))
    return [record for record in records if id(record) in exact_records and latest_output_assistant_witness(record.item)]


def transcript_latest_assistant_witness_text_records(records: list[EvidenceRecord], expected: str) -> list[EvidenceRecord]:
    exact_records = set(id(record) for record in transcript_latest_exact_records(records, expected))
    return [record for record in records if id(record) in exact_records and latest_output_assistant_witness_text_matches(record.item, expected)]


def _latest_user_turn_witness_dicts(item: dict[str, Any]) -> list[dict[str, Any]]:
    payload = _item_payload(item)
    metadata = item.get('metadata') if isinstance(item.get('metadata'), dict) else {}
    payload_metadata = payload.get('metadata') if isinstance(payload.get('metadata'), dict) else {}
    out: list[dict[str, Any]] = []
    for container in (item, payload, metadata, payload_metadata):
        if not isinstance(container, dict):
            continue
        witness = container.get('latest_user_turn_witness') or container.get('user_turn_witness')
        if isinstance(witness, dict):
            out.append(witness)
        if any(key in container for key in ('latest_user_turn_user_like', 'latest_user_turn_author_role', 'latest_user_turn_selector', 'latest_user_turn_order_policy')):
            out.append(container)
    return out


def _latest_user_turn_witness_is_user_like(witness: dict[str, Any]) -> bool:
    user_like = _witness_bool(witness.get('user_like')) or _witness_bool(witness.get('latest_user_turn_user_like'))
    author_role = compact(witness.get('author_role') or witness.get('latest_user_turn_author_role') or witness.get('data_message_author_role')).lower()
    selector = compact(witness.get('selector_hint') or witness.get('latest_user_turn_selector'))
    policy = compact(witness.get('selection_policy') or witness.get('latest_user_turn_order_policy')).lower()
    policy_ok = policy == 'latest-visible-user-like-node-in-dom-order'
    return bool(selector and policy_ok and (user_like or author_role == 'user'))


def _latest_user_turn_witness_text(witness: dict[str, Any]) -> str:
    return compact(witness.get('text') or witness.get('latest_user_turn_text') or witness.get('user_turn_text') or witness.get('prompt'))


def latest_user_turn_witness_text_matches(item: dict[str, Any], probe_text: str) -> bool:
    probe = compact(probe_text)
    if not probe:
        return False
    for witness in _latest_user_turn_witness_dicts(item):
        if _latest_user_turn_witness_is_user_like(witness) and _latest_user_turn_witness_text(witness) == probe:
            return True
    return False


AGGREGATE_WITNESS_SCOPE_TOKENS = {
    'aggregate',
    'ancestor',
    'container',
    'conversation',
    'document',
    'main-region',
    'mixed',
    'parent',
    'thread',
    'turn-pair',
    'wrapper',
}


def _witness_declares_aggregate_scope(witness: dict[str, Any]) -> bool:
    if any(truthy(witness.get(key)) for key in (
        'aggregate_parent',
        'contains_counterpart_turn_text',
        'contains_user_turn_text',
        'contains_assistant_turn_text',
        'includes_user_turn',
        'includes_assistant_turn',
        'mixed_author_roles',
        'role_mixture_detected',
    )):
        return True
    for key in ('witness_scope', 'node_scope', 'selector_scope', 'capture_scope', 'selection_scope'):
        value = compact(witness.get(key)).lower()
        if value and any(token in value for token in AGGREGATE_WITNESS_SCOPE_TOKENS):
            return True
    return False


def _witness_visible_texts(witness: dict[str, Any]) -> list[str]:
    keys = (
        'text',
        'visible_text',
        'node_text',
        'outer_text',
        'inner_text',
        'text_content',
        'aria_text',
        'accessible_name',
        'latest_output_text',
        'latest_user_turn_text',
        'latest_output',
        'user_turn_text',
        'prompt',
    )
    texts: list[str] = []
    for key in keys:
        value = compact(witness.get(key))
        if value:
            texts.append(value)
    return texts


def _witness_not_aggregate_parent(witness: dict[str, Any], *, expected_text: str, counterpart_text: str, own_text: str) -> bool:
    if _witness_declares_aggregate_scope(witness):
        return False
    expected = compact(expected_text)
    counterpart = compact(counterpart_text)
    own = compact(own_text)
    for text in _witness_visible_texts(witness):
        if counterpart and expected and counterpart in text and expected in text and text != own:
            return False
    return True


def latest_output_assistant_witness_not_aggregate(item: dict[str, Any], expected: str, probe_text: str) -> bool:
    exact = compact(expected)
    if not exact:
        return False
    for witness in _latest_witness_dicts(item):
        if (
            _latest_output_witness_is_assistant_like(witness)
            and _latest_output_witness_text(witness) == exact
            and _witness_not_aggregate_parent(witness, expected_text=expected, counterpart_text=probe_text, own_text=exact)
        ):
            return True
    return False


def latest_user_turn_witness_not_aggregate(item: dict[str, Any], expected: str, probe_text: str) -> bool:
    probe = compact(probe_text)
    if not probe:
        return False
    for witness in _latest_user_turn_witness_dicts(item):
        if (
            _latest_user_turn_witness_is_user_like(witness)
            and _latest_user_turn_witness_text(witness) == probe
            and _witness_not_aggregate_parent(witness, expected_text=expected, counterpart_text=expected, own_text=probe)
        ):
            return True
    return False


def transcript_latest_assistant_not_aggregate_records(records: list[EvidenceRecord], expected: str, probe_text: str) -> list[EvidenceRecord]:
    exact_records = set(id(record) for record in transcript_latest_exact_records(records, expected))
    return [record for record in records if id(record) in exact_records and latest_output_assistant_witness_not_aggregate(record.item, expected, probe_text)]


def transcript_latest_user_not_aggregate_records(records: list[EvidenceRecord], expected: str, probe_text: str) -> list[EvidenceRecord]:
    exact_records = set(id(record) for record in transcript_latest_exact_records(records, expected))
    return [record for record in records if id(record) in exact_records and latest_user_turn_witness_not_aggregate(record.item, expected, probe_text)]


def transcript_latest_user_turn_witness_text_records(records: list[EvidenceRecord], expected: str, probe_text: str) -> list[EvidenceRecord]:
    exact_records = set(id(record) for record in transcript_latest_exact_records(records, expected))
    return [record for record in records if id(record) in exact_records and latest_user_turn_witness_text_matches(record.item, probe_text)]




def _witness_int(witness: dict[str, Any], *keys: str) -> int | None:
    for key in keys:
        parsed = _intish(witness.get(key))
        if parsed is not None:
            return parsed
    return None


def _witness_frame_tuple(witness: dict[str, Any], *, prefix: str = '') -> tuple[str, int | None]:
    frame_path_key = f'{prefix}_frame_path' if prefix else 'frame_path'
    frame_depth_key = f'{prefix}_frame_depth' if prefix else 'frame_depth'
    path = compact(witness.get(frame_path_key) or witness.get('frame_path'))
    depth = _witness_int(witness, frame_depth_key, 'frame_depth')
    return (path, depth)


def _explicit_witness_frame_tuple(witness: dict[str, Any], *, prefix: str = '') -> tuple[str, int] | None:
    frame_path_key = f'{prefix}_frame_path' if prefix else 'frame_path'
    frame_depth_key = f'{prefix}_frame_depth' if prefix else 'frame_depth'
    depth = _witness_int(witness, frame_depth_key, 'frame_depth')
    if depth is None or depth < 0:
        return None
    path = compact(witness.get(frame_path_key) or witness.get('frame_path'))
    if depth > 0 and not path:
        return None
    return (path or 'top', depth)


def latest_turn_user_before_assistant_witness_order(item: dict[str, Any], expected: str, probe_text: str) -> bool:
    exact = compact(expected)
    probe = compact(probe_text)
    if not exact or not probe:
        return False
    for assistant in _latest_witness_dicts(item):
        if not (_latest_output_witness_is_assistant_like(assistant) and _latest_output_witness_text(assistant) == exact):
            continue
        assistant_index = _witness_int(assistant, 'document_order_index', 'latest_output_document_order_index')
        if assistant_index is None:
            continue
        assistant_frame = _witness_frame_tuple(assistant, prefix='latest_output')
        for user in _latest_user_turn_witness_dicts(item):
            if not (_latest_user_turn_witness_is_user_like(user) and _latest_user_turn_witness_text(user) == probe):
                continue
            user_index = _witness_int(user, 'document_order_index', 'latest_user_turn_document_order_index')
            if user_index is None:
                continue
            user_frame = _witness_frame_tuple(user, prefix='latest_user_turn')
            if user_frame == assistant_frame and user_index < assistant_index:
                return True
    return False


def transcript_latest_user_before_assistant_witness_order_records(records: list[EvidenceRecord], expected: str, probe_text: str) -> list[EvidenceRecord]:
    exact_records = set(id(record) for record in transcript_latest_exact_records(records, expected))
    return [record for record in records if id(record) in exact_records and latest_turn_user_before_assistant_witness_order(record.item, expected, probe_text)]


def latest_turn_pair_explicit_same_frame_context(item: dict[str, Any], expected: str, probe_text: str) -> bool:
    exact = compact(expected)
    probe = compact(probe_text)
    if not exact or not probe:
        return False
    for assistant in _latest_witness_dicts(item):
        if not (_latest_output_witness_is_assistant_like(assistant) and _latest_output_witness_text(assistant) == exact):
            continue
        assistant_index = _witness_int(assistant, 'document_order_index', 'latest_output_document_order_index')
        assistant_frame = _explicit_witness_frame_tuple(assistant, prefix='latest_output')
        if assistant_index is None or assistant_frame is None:
            continue
        for user in _latest_user_turn_witness_dicts(item):
            if not (_latest_user_turn_witness_is_user_like(user) and _latest_user_turn_witness_text(user) == probe):
                continue
            user_index = _witness_int(user, 'document_order_index', 'latest_user_turn_document_order_index')
            user_frame = _explicit_witness_frame_tuple(user, prefix='latest_user_turn')
            if user_index is None or user_frame is None:
                continue
            if user_frame == assistant_frame and user_index < assistant_index:
                return True
    return False


def transcript_latest_turn_pair_explicit_frame_records(records: list[EvidenceRecord], expected: str, probe_text: str) -> list[EvidenceRecord]:
    exact_records = set(id(record) for record in transcript_latest_exact_records(records, expected))
    return [record for record in records if id(record) in exact_records and latest_turn_pair_explicit_same_frame_context(record.item, expected, probe_text)]


def write_readback_records(records: list[EvidenceRecord], probe_text: str) -> list[EvidenceRecord]:
    probe = compact(probe_text)
    matches: list[EvidenceRecord] = []
    for record in records:
        item = record.item
        item_type = action_type(item)
        if 'write' not in item_type or not action_ok(item):
            continue
        texts = [
            dict_text(item, 'readback', 'composer_readback', 'written_text'),
            nested_text(item, 'payload', 'readback'),
            nested_text(item, 'payload', 'composer_readback'),
            nested_text(item, 'payload', 'written_text'),
        ]
        if any(text == probe or probe in text for text in texts if text):
            matches.append(record)
    return matches


def submit_ok_records(records: list[EvidenceRecord]) -> list[EvidenceRecord]:
    matches: list[EvidenceRecord] = []
    for record in records:
        item = record.item
        item_type = action_type(item)
        payload = item.get('payload') if isinstance(item.get('payload'), dict) else {}
        if action_ok(item) and ('submit' in item_type or item.get('submit_ok') is True or payload.get('submit_ok') is True):
            matches.append(record)
    return matches



def first_container_value(item: dict[str, Any], *keys: str) -> Any:
    payload = _item_payload(item)
    metadata = item.get('metadata') if isinstance(item.get('metadata'), dict) else {}
    payload_metadata = payload.get('metadata') if isinstance(payload.get('metadata'), dict) else {}
    for container in (item, payload, metadata, payload_metadata):
        if not isinstance(container, dict):
            continue
        for key in keys:
            if key in container:
                return container.get(key)
    return None


def submit_operator_attestation_records(records: list[EvidenceRecord]) -> list[EvidenceRecord]:
    matches: list[EvidenceRecord] = []
    for record in submit_ok_records(records):
        confirmed = any(
            truthy(first_container_value(record.item, key))
            for key in ('operator_submit_confirmed', 'operator_confirmed', 'manual_submit_confirmed', 'human_confirmed')
        )
        method = compact(first_container_value(record.item, 'submit_method', 'operator_submit_method')).lower()
        action = compact(first_container_value(record.item, 'operator_action', 'operator_control')).lower()
        method_ok = method in OPERATOR_SUBMIT_METHODS or action == 'sidepanel-chatgpt-first-proof-submit-button'
        if confirmed and method_ok:
            matches.append(record)
    return matches


def proof_live_gate_ok_submit_records(records: list[EvidenceRecord]) -> list[EvidenceRecord]:
    matches: list[EvidenceRecord] = []
    for record in submit_ok_records(records):
        gate_ok = truthy(first_container_value(record.item, 'proof_live_gate_ok'))
        verdict = compact(first_container_value(record.item, 'proof_live_gate_verdict')).lower()
        if gate_ok and verdict == 'proof-live-gate-ok':
            matches.append(record)
    return matches


def submit_prompt_readback_records(records: list[EvidenceRecord], probe_text: str) -> list[EvidenceRecord]:
    probe = compact(probe_text)
    if not probe:
        return []
    keys = (
        'composer_readback_before_submit',
        'prompt_before_submit',
        'submitted_prompt',
        'submit_prompt_readback',
        'prompt_text_at_submit',
    )
    matches: list[EvidenceRecord] = []
    for record in submit_ok_records(records):
        for key in keys:
            text = compact(first_container_value(record.item, key))
            if text == probe or (text and probe in text):
                matches.append(record)
                break
    return matches


def _record_prompt_texts(record: EvidenceRecord, *keys: str) -> list[str]:
    texts: list[str] = []
    for key in keys:
        text = compact(first_container_value(record.item, key))
        if text:
            texts.append(text)
    return texts


def write_readback_exact_records(records: list[EvidenceRecord], probe_text: str) -> list[EvidenceRecord]:
    probe = compact(probe_text)
    if not probe:
        return []
    matches: list[EvidenceRecord] = []
    for record in write_readback_records(records, probe_text):
        texts = _record_prompt_texts(record, 'readback', 'composer_readback', 'written_text')
        if any(text == probe for text in texts):
            matches.append(record)
    return matches


def submit_prompt_readback_exact_records(records: list[EvidenceRecord], probe_text: str) -> list[EvidenceRecord]:
    probe = compact(probe_text)
    if not probe:
        return []
    matches: list[EvidenceRecord] = []
    keys = (
        'composer_readback_before_submit',
        'prompt_before_submit',
        'submitted_prompt',
        'submit_prompt_readback',
        'prompt_text_at_submit',
    )
    for record in submit_prompt_readback_records(records, probe_text):
        texts = _record_prompt_texts(record, *keys)
        if any(text == probe for text in texts):
            matches.append(record)
    return matches


def metadata_dicts(item: dict[str, Any]) -> list[dict[str, Any]]:
    payload = _item_payload(item)
    out: list[dict[str, Any]] = []
    for candidate in (item, item.get('metadata'), payload, payload.get('metadata')):
        if isinstance(candidate, dict):
            out.append(candidate)
    return out


def record_is_capture_or_snapshot(record: EvidenceRecord) -> bool:
    item_type = action_type(record.item)
    return item_type in {'fixture.capture', 'state.snapshot'} or item_type.endswith('.capture') or item_type.endswith('.snapshot')


def settled_generation_witness_records(
    records: list[EvidenceRecord],
    *,
    min_ordinal: int | None,
    min_sequence_index: int | None = None,
    require_capture_or_snapshot: bool = False,
    require_chatgpt_witness: bool = False,
    required_tab_id: int | None = None,
    required_conversation_paths: set[str] | None = None,
) -> list[EvidenceRecord]:
    matches: list[EvidenceRecord] = []
    for record in records:
        if min_ordinal is not None and record.ordinal <= min_ordinal:
            continue
        sequence_index = record_sequence_index(record)
        if min_sequence_index is not None and not (isinstance(sequence_index, int) and sequence_index > min_sequence_index):
            continue
        if require_capture_or_snapshot and not record_is_capture_or_snapshot(record):
            continue
        witness = action_record_witness(record)
        if require_chatgpt_witness and not (witness.get('adapter_is_chatgpt') and witness.get('host_is_chatgpt')):
            continue
        if required_tab_id is not None and witness.get('tab_id') != required_tab_id:
            continue
        if required_conversation_paths is not None:
            witness_paths = set(witness.get('conversation_route_paths') or [])
            if not witness_paths.intersection(required_conversation_paths):
                continue
        for metadata in metadata_dicts(record.item):
            state = compact(metadata.get('generation_state')).lower()
            if state not in SETTLED_GENERATION_STATES:
                continue
            if 'generation_stop_control_present' not in metadata:
                continue
            if not falsey(metadata.get('generation_stop_control_present')):
                continue
            matches.append(record)
            break
    return matches


def ordered_write_submit_latest_sequence(records: list[EvidenceRecord], contract: dict[str, str]) -> dict[str, Any]:
    writes = write_readback_records(records, contract['probe_text'])
    submits = submit_ok_records(records)
    latests = transcript_latest_exact_records(records, contract['expected_exact_reply'])
    ordered_candidates = 0
    index_order_candidates = 0
    witnessed_candidates = 0
    conversation_route_candidates = 0
    same_tab_candidates = 0
    first_ordered: dict[str, Any] | None = None
    first_index_gap: dict[str, Any] | None = None
    first_witness_gap: dict[str, Any] | None = None
    first_conversation_route_gap: dict[str, Any] | None = None
    first_tab_context_gap: dict[str, Any] | None = None

    for write in writes:
        for submit in submits:
            if submit.ordinal <= write.ordinal:
                continue
            for latest in latests:
                if latest.ordinal <= submit.ordinal:
                    continue
                ordered_candidates += 1
                witnesses = {
                    'write': action_record_witness(write),
                    'submit': action_record_witness(submit),
                    'latest': action_record_witness(latest),
                }
                indices = {
                    'write': witnesses['write']['sequence_index'],
                    'submit': witnesses['submit']['sequence_index'],
                    'latest': witnesses['latest']['sequence_index'],
                }
                explicit_indices_present = all(isinstance(value, int) for value in indices.values())
                sequence_index_order_ok = bool(explicit_indices_present and indices['write'] < indices['submit'] < indices['latest'])
                action_witnesses_ok = all(
                    bool(witness.get('adapter_is_chatgpt') and witness.get('host_is_chatgpt'))
                    for witness in witnesses.values()
                )
                latest_conversation_paths = list(witnesses['latest'].get('conversation_route_paths') or [])
                latest_conversation_route_ok = bool(latest_conversation_paths)
                pre_submit_urls = list(witnesses['write'].get('urls') or []) + list(witnesses['submit'].get('urls') or [])
                pre_submit_non_conversation_chatgpt_route_ok = any(
                    host_is_chatgpt(url) and not chatgpt_conversation_route(url)
                    for url in pre_submit_urls
                )
                conversation_route_transition_ok = bool(pre_submit_non_conversation_chatgpt_route_ok and latest_conversation_route_ok)
                tab_ids = {
                    'write': witnesses['write'].get('tab_id'),
                    'submit': witnesses['submit'].get('tab_id'),
                    'latest': witnesses['latest'].get('tab_id'),
                }
                explicit_tab_ids_present = all(isinstance(value, int) for value in tab_ids.values())
                same_tab_context_ok = bool(explicit_tab_ids_present and len(set(tab_ids.values())) == 1)
                candidate = {
                    'ok': bool(sequence_index_order_ok and action_witnesses_ok and latest_conversation_route_ok and same_tab_context_ok),
                    'ordinal_order_ok': True,
                    'explicit_sequence_indices_present': explicit_indices_present,
                    'sequence_index_order_ok': sequence_index_order_ok,
                    'action_witnesses_ok': action_witnesses_ok,
                    'latest_conversation_route_ok': latest_conversation_route_ok,
                    'post_submit_conversation_route_transition_ok': conversation_route_transition_ok,
                    'pre_submit_non_conversation_chatgpt_route_ok': pre_submit_non_conversation_chatgpt_route_ok,
                    'latest_conversation_route_paths': latest_conversation_paths,
                    'explicit_tab_ids_present': explicit_tab_ids_present,
                    'same_tab_context_ok': same_tab_context_ok,
                    'tab_ids': tab_ids,
                    'same_tab_id': tab_ids['write'] if same_tab_context_ok else None,
                    'write_path': write.path,
                    'submit_path': submit.path,
                    'latest_path': latest.path,
                    'write_ordinal': write.ordinal,
                    'submit_ordinal': submit.ordinal,
                    'latest_ordinal': latest.ordinal,
                    'sequence_indices': indices,
                    'action_witnesses': witnesses,
                }
                if first_ordered is None:
                    first_ordered = candidate
                if sequence_index_order_ok:
                    index_order_candidates += 1
                elif first_index_gap is None:
                    first_index_gap = candidate
                if action_witnesses_ok:
                    witnessed_candidates += 1
                elif first_witness_gap is None:
                    first_witness_gap = candidate
                if latest_conversation_route_ok:
                    conversation_route_candidates += 1
                elif first_conversation_route_gap is None:
                    first_conversation_route_gap = candidate
                if same_tab_context_ok:
                    same_tab_candidates += 1
                elif first_tab_context_gap is None:
                    first_tab_context_gap = candidate
                if candidate['ok']:
                    return candidate

    return {
        'ok': False,
        'ordinal_order_ok': ordered_candidates > 0,
        'explicit_sequence_indices_present': bool(first_ordered and first_ordered.get('explicit_sequence_indices_present')),
        'sequence_index_order_ok': index_order_candidates > 0,
        'action_witnesses_ok': witnessed_candidates > 0,
        'latest_conversation_route_ok': conversation_route_candidates > 0,
        'post_submit_conversation_route_transition_ok': False,
        'pre_submit_non_conversation_chatgpt_route_ok': False,
        'same_tab_context_ok': same_tab_candidates > 0,
        'write_count': len(writes),
        'submit_count': len(submits),
        'transcript_latest_exact_count': len(latests),
        'ordered_candidate_count': ordered_candidates,
        'sequence_index_order_candidate_count': index_order_candidates,
        'action_witness_candidate_count': witnessed_candidates,
        'conversation_route_candidate_count': conversation_route_candidates,
        'same_tab_candidate_count': same_tab_candidates,
        'first_ordered_candidate': first_ordered,
        'first_sequence_index_gap': first_index_gap,
        'first_action_witness_gap': first_witness_gap,
        'first_conversation_route_gap': first_conversation_route_gap,
        'first_tab_context_gap': first_tab_context_gap,
    }


def _policy_dicts(dicts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    policies: list[dict[str, Any]] = []
    for item in dicts:
        if isinstance(item.get('action_policy'), dict):
            policies.append(item['action_policy'])
        metadata = item.get('metadata')
        if isinstance(metadata, dict) and isinstance(metadata.get('action_policy'), dict):
            policies.append(metadata['action_policy'])
        payload = item.get('payload')
        if isinstance(payload, dict) and isinstance(payload.get('action_policy'), dict):
            policies.append(payload['action_policy'])
    return policies


def has_route_safe_submit_policy(dicts: list[dict[str, Any]]) -> bool:
    for policy in _policy_dicts(dicts):
        method = compact(policy.get('submit_method')).lower()
        min_score = policy.get('submit_button_min_score')
        score_ok = isinstance(min_score, (int, float)) and min_score >= 0.45
        if (
            method == 'button-click-only'
            and falsey(policy.get('keyboard_submit_enabled'))
            and truthy(policy.get('route_posture_allows_submit'))
            and truthy(policy.get('prompt_present_for_submit'))
            and truthy(policy.get('submit_button_found'))
            and score_ok
        ):
            return True
    return False


def collect_artifact_refs(dicts: list[dict[str, Any]]) -> dict[str, list[str]]:
    buckets = {'screenshots': [], 'traces': [], 'captures': []}
    for item in dicts:
        for key, value in item.items():
            if not isinstance(value, str) or not value.strip():
                continue
            lowered = value.lower()
            if key in {'screenshot', 'screenshot_path'} or lowered.endswith(('.png', '.jpg', '.jpeg', '.webp')):
                buckets['screenshots'].append(value)
            if key in {'trace', 'trace_path'} or lowered.endswith(('.zip', '.trace')) or 'trace' in key:
                buckets['traces'].append(value)
            if key in {'capture', 'capture_path', 'fixture_capture_path'} or 'capture' in key:
                buckets['captures'].append(value)
    return {key: sorted(dict.fromkeys(values)) for key, values in buckets.items()}


def _all_strings(value: Any) -> list[str]:
    strings: list[str] = []

    def walk(item: Any) -> None:
        if isinstance(item, str):
            strings.append(item)
        elif isinstance(item, dict):
            for child in item.values():
                walk(child)
        elif isinstance(item, list):
            for child in item:
                walk(child)

    walk(value)
    return strings


def privacy_review(payload: Any, artifacts: dict[str, list[str]]) -> dict[str, Any]:
    strings = _all_strings(payload)
    flags: dict[str, Any] = {
        'possible_email_address': sorted(dict.fromkeys(match.group(0) for text in strings for match in EMAIL_RE.finditer(text)))[:20],
        'possible_token_or_session_hint': any(TOKEN_HINT_RE.search(text) for text in strings),
        'raw_html_or_html_sample_present': any(RAW_HTML_RE.search(text) for text in strings),
        'screenshot_artifacts_present': bool(artifacts.get('screenshots')),
        'trace_artifacts_present': bool(artifacts.get('traces')),
    }
    review_required = any(bool(value) for value in flags.values()) or bool(artifacts.get('captures'))
    return {
        'scan_completed': True,
        'publishable_without_redaction_review': False,
        'review_required_before_publication': review_required,
        'flags': flags,
        'notes': [
            'Reviewability is local-only; screenshots, traces, HTML samples, account labels, and transcript text still need human redaction review before publication.',
            'This scanner is heuristic and intentionally conservative; it does not certify evidence as public-safe.',
        ],
    }




def privacy_redaction_review_record_present(payload: Any) -> bool:
    if not isinstance(payload, dict):
        return False
    review = payload.get('privacy_redaction_review')
    if not isinstance(review, dict):
        return False
    publishable = review.get('publishable_without_redaction_review')
    review_required = review.get('review_required_before_publication')
    return falsey(publishable) and isinstance(review_required, bool)


def surface_conflicts(dicts: list[dict[str, Any]]) -> dict[str, list[str]]:
    adapters = sorted({adapter for adapter in collect_adapters(dicts) if adapter not in CHATGPT_ADAPTER_VALUES})
    non_chatgpt_urls = sorted({url for url in collect_urls(dicts) if not host_is_chatgpt(url)})
    surface_keys = sorted({str(item.get('surface_key')).strip().lower() for item in dicts if isinstance(item.get('surface_key'), str) and str(item.get('surface_key')).strip().lower() not in {'chatgpt'}})
    return {
        'non_chatgpt_adapters': adapters,
        'non_chatgpt_urls': non_chatgpt_urls,
        'non_chatgpt_surface_keys': surface_keys,
    }


def no_surface_conflicts(dicts: list[dict[str, Any]]) -> bool:
    conflicts = surface_conflicts(dicts)
    return not any(conflicts.values())


def evaluate_attempt(attempt_id: str, records: list[EvidenceRecord], contract: dict[str, str]) -> dict[str, Any]:
    dicts = [record.item for record in records]
    urls = collect_urls(dicts)
    adapters = collect_adapters(dicts)
    route_postures = collect_route_postures(dicts)
    artifacts = collect_artifact_refs(dicts)
    sequence = ordered_write_submit_latest_sequence(records, contract)
    operator_submits = submit_operator_attestation_records(records)
    operator_submit_paths = {record.path for record in operator_submits}
    proof_live_gate_records = proof_live_gate_ok_submit_records(records)
    proof_live_gate_paths = {record.path for record in proof_live_gate_records}
    submit_prompt_readbacks = submit_prompt_readback_records(records, contract['probe_text'])
    submit_prompt_readback_paths = {record.path for record in submit_prompt_readbacks}
    write_readback_exact = write_readback_exact_records(records, contract['probe_text'])
    write_readback_exact_paths = {record.path for record in write_readback_exact}
    submit_prompt_readback_exact = submit_prompt_readback_exact_records(records, contract['probe_text'])
    submit_prompt_readback_exact_paths = {record.path for record in submit_prompt_readback_exact}
    assistant_not_aggregate_witnesses = transcript_latest_assistant_not_aggregate_records(records, contract['expected_exact_reply'], contract['probe_text'])
    assistant_not_aggregate_witness_paths = {record.path for record in assistant_not_aggregate_witnesses}
    user_turn_witnesses = transcript_latest_user_turn_witness_text_records(records, contract['expected_exact_reply'], contract['probe_text'])
    user_turn_witness_paths = {record.path for record in user_turn_witnesses}
    user_not_aggregate_witnesses = transcript_latest_user_not_aggregate_records(records, contract['expected_exact_reply'], contract['probe_text'])
    user_not_aggregate_witness_paths = {record.path for record in user_not_aggregate_witnesses}
    user_before_assistant_witnesses = transcript_latest_user_before_assistant_witness_order_records(records, contract['expected_exact_reply'], contract['probe_text'])
    user_before_assistant_witness_paths = {record.path for record in user_before_assistant_witnesses}
    explicit_frame_witnesses = transcript_latest_turn_pair_explicit_frame_records(records, contract['expected_exact_reply'], contract['probe_text'])
    explicit_frame_witness_paths = {record.path for record in explicit_frame_witnesses}
    sequence_write_path = sequence.get('write_path') if isinstance(sequence.get('write_path'), str) else None
    sequence_submit_path = sequence.get('submit_path') if isinstance(sequence.get('submit_path'), str) else None
    sequence_latest_path = sequence.get('latest_path') if isinstance(sequence.get('latest_path'), str) else None
    sequence_latest_ordinal = sequence.get('latest_ordinal') if isinstance(sequence.get('latest_ordinal'), int) else None
    sequence_indices = sequence.get('sequence_indices') if isinstance(sequence.get('sequence_indices'), dict) else {}
    sequence_latest_index = sequence_indices.get('latest') if isinstance(sequence_indices.get('latest'), int) else None
    sequence_same_tab_id = sequence.get('same_tab_id') if isinstance(sequence.get('same_tab_id'), int) else None
    sequence_latest_conversation_paths = {path for path in (sequence.get('latest_conversation_route_paths') or []) if isinstance(path, str) and path}
    settled_generation = settled_generation_witness_records(records, min_ordinal=sequence_latest_ordinal)
    settled_generation_sequence_surface = settled_generation_witness_records(
        records,
        min_ordinal=sequence_latest_ordinal,
        min_sequence_index=sequence_latest_index,
        require_capture_or_snapshot=True,
        require_chatgpt_witness=True,
    )
    settled_generation_sequence_surface_same_tab = settled_generation_witness_records(
        records,
        min_ordinal=sequence_latest_ordinal,
        min_sequence_index=sequence_latest_index,
        require_capture_or_snapshot=True,
        require_chatgpt_witness=True,
        required_tab_id=sequence_same_tab_id,
    ) if sequence_same_tab_id is not None else []
    settled_generation_sequence_surface_same_tab_conversation = settled_generation_witness_records(
        records,
        min_ordinal=sequence_latest_ordinal,
        min_sequence_index=sequence_latest_index,
        require_capture_or_snapshot=True,
        require_chatgpt_witness=True,
        required_tab_id=sequence_same_tab_id,
        required_conversation_paths=sequence_latest_conversation_paths,
    ) if sequence_same_tab_id is not None and sequence_latest_conversation_paths else []
    checks = {
        'adapter_is_chatgpt': 'chatgpt' in adapters or any(item.get('surface_key') == 'chatgpt' for item in dicts),
        'host_is_chatgpt': any(host_is_chatgpt(url) for url in urls),
        'route_posture_is_plain_chat': 'plain-chat' in route_postures,
        'composer_write_readback_contains_probe': has_composer_write_readback(dicts, contract['probe_text']),
        'submit_action_ok': has_submit_ok(dicts),
        'latest_turn_exact_reply': has_latest_exact_reply(dicts, contract['expected_exact_reply']),
        'transcript_latest_action_exact_reply': bool(transcript_latest_exact_records(records, contract['expected_exact_reply'])),
        'ordered_write_submit_latest_sequence': bool(sequence.get('ordinal_order_ok')),
        'explicit_sequence_indices_monotonic': bool(sequence.get('sequence_index_order_ok')),
        'ordered_sequence_has_chatgpt_action_witnesses': bool(sequence.get('action_witnesses_ok')),
        'post_submit_conversation_route_witness': bool(sequence.get('latest_conversation_route_ok')),
        'post_submit_conversation_route_transition': bool(sequence.get('post_submit_conversation_route_transition_ok')),
        'proof_chain_same_tab_context': bool(sequence.get('same_tab_context_ok') and settled_generation_sequence_surface_same_tab),
        'post_latest_settled_witness_same_conversation_route': bool(settled_generation_sequence_surface_same_tab_conversation),
        'operator_submit_attestation_present': bool(sequence_submit_path and sequence_submit_path in operator_submit_paths),
        'proof_live_gate_ok_before_submit': bool(sequence_submit_path and sequence_submit_path in proof_live_gate_paths),
        'submit_prompt_readback_matches_probe': bool(sequence_submit_path and sequence_submit_path in submit_prompt_readback_paths),
        'write_and_submit_readbacks_exact_probe': bool(sequence_write_path and sequence_write_path in write_readback_exact_paths and sequence_submit_path and sequence_submit_path in submit_prompt_readback_exact_paths),
        'post_latest_generation_settled_witness': bool(settled_generation),
        'post_latest_settled_witness_sequence_and_surface': bool(settled_generation_sequence_surface),
        'transcript_latest_assistant_node_witness': bool(transcript_latest_assistant_witness_records(records, contract['expected_exact_reply'])),
        'transcript_latest_witness_text_matches_reply': bool(transcript_latest_assistant_witness_text_records(records, contract['expected_exact_reply'])),
        'transcript_latest_assistant_witness_not_aggregate_parent': bool(sequence_latest_path and sequence_latest_path in assistant_not_aggregate_witness_paths),
        'transcript_latest_user_turn_witness_text_matches_prompt': bool(sequence_latest_path and sequence_latest_path in user_turn_witness_paths),
        'transcript_latest_user_witness_not_aggregate_parent': bool(sequence_latest_path and sequence_latest_path in user_not_aggregate_witness_paths),
        'transcript_latest_user_before_assistant_witness_order': bool(sequence_latest_path and sequence_latest_path in user_before_assistant_witness_paths),
        'transcript_latest_turn_pair_explicit_frame_context': bool(sequence_latest_path and sequence_latest_path in explicit_frame_witness_paths),
        'action_policy_supports_route_safe_submit': has_route_safe_submit_policy(dicts),
        'attempt_has_no_cross_surface_conflicts': no_surface_conflicts(dicts),
    }
    required_order = list(checks.keys())
    missing = [key for key in required_order if not checks.get(key)]
    return {
        'attempt_id': attempt_id,
        'ok': not missing,
        'checks': checks,
        'missing_required_checks': missing,
        'observed': {
            'adapters': sorted(dict.fromkeys(adapters)),
            'urls': urls,
            'route_postures': sorted(dict.fromkeys(route_postures)),
            'artifact_refs': artifacts,
            'record_count': len(records),
            'sample_paths': [record.path for record in records[:12]],
            'conflicts': surface_conflicts(dicts),
            'ordered_sequence': sequence,
            'operator_submit_attestation_paths': sorted(operator_submit_paths),
            'proof_live_gate_ok_submit_paths': sorted(proof_live_gate_paths),
            'submit_prompt_readback_paths': sorted(submit_prompt_readback_paths),
            'write_readback_exact_paths': sorted(write_readback_exact_paths),
            'submit_prompt_readback_exact_paths': sorted(submit_prompt_readback_exact_paths),
            'post_latest_generation_settled_witness_paths': [record.path for record in settled_generation],
            'post_latest_settled_witness_sequence_surface_paths': [record.path for record in settled_generation_sequence_surface],
            'post_latest_settled_witness_same_tab_paths': [record.path for record in settled_generation_sequence_surface_same_tab],
            'post_latest_settled_witness_same_conversation_paths': [record.path for record in settled_generation_sequence_surface_same_tab_conversation],
            'proof_chain_same_tab_id': sequence_same_tab_id,
            'proof_chain_latest_conversation_paths': sorted(sequence_latest_conversation_paths),
            'transcript_latest_assistant_witness_paths': [record.path for record in transcript_latest_assistant_witness_records(records, contract['expected_exact_reply'])],
            'transcript_latest_assistant_witness_text_match_paths': [record.path for record in transcript_latest_assistant_witness_text_records(records, contract['expected_exact_reply'])],
            'transcript_latest_assistant_not_aggregate_paths': sorted(assistant_not_aggregate_witness_paths),
            'transcript_latest_user_not_aggregate_paths': sorted(user_not_aggregate_witness_paths),
            'transcript_latest_user_before_assistant_witness_order_paths': sorted(user_before_assistant_witness_paths),
            'transcript_latest_turn_pair_explicit_frame_context_paths': sorted(explicit_frame_witness_paths),
        },
    }


def evaluate_payload(payload: Any, *, root: Path = ROOT, input_path: Path | None = None) -> dict[str, Any]:
    contract = load_probe_contract(root)
    records = iter_evidence_records(payload)
    dicts = [record.item for record in records]
    by_attempt: dict[str, list[EvidenceRecord]] = defaultdict(list)
    for record in records:
        by_attempt[record.attempt_id].append(record)

    attempts = [evaluate_attempt(attempt_id, attempt_records, contract) for attempt_id, attempt_records in sorted(by_attempt.items())]
    winning_attempt = next((attempt for attempt in attempts if attempt.get('ok')), None)
    artifacts = collect_artifact_refs(dicts)
    conflicts = surface_conflicts(dicts)
    global_no_conflicts = no_surface_conflicts(dicts)
    global_privacy_redaction_review_present = privacy_redaction_review_record_present(payload)
    registry_audit = required_check_registry_audit()
    checks = merge_required_checks(
        attempts,
        winning_attempt=winning_attempt,
        global_no_conflicts=global_no_conflicts,
        global_privacy_redaction_review_present=global_privacy_redaction_review_present,
    )
    required_order = list(REQUIRED_CHECKS)
    missing = [key for key in required_order if not checks.get(key)]
    is_rehearsal = payload_declares_rehearsal(payload)
    if missing:
        verdict = BLOCKED_VERDICT
    elif is_rehearsal:
        verdict = REHEARSAL_VERDICT
    else:
        verdict = REVIEWABLE_VERDICT
    observed_adapters = collect_adapters(dicts)
    observed_urls = collect_urls(dicts)
    observed_postures = collect_route_postures(dicts)
    privacy = privacy_review(payload, artifacts)
    return {
        'schema_version': SCHEMA_VERSION,
        'project': 'GlassTTY',
        'surface_key': 'chatgpt',
        'generated_at': utcnow(),
        'input_path': display_path(input_path, root=root),
        'input_sha256': sha256_file(input_path) if input_path and input_path.exists() else None,
        'probe_contract': contract,
        'verdict': verdict,
        'ok': verdict == REVIEWABLE_VERDICT,
        'harness_ok': verdict in {REVIEWABLE_VERDICT, REHEARSAL_VERDICT},
        'proof_mode': 'offline-rehearsal' if is_rehearsal else 'live-or-unknown',
        'rehearsal_only': is_rehearsal,
        'support_claim_effect': 'none; this evaluator never widens support claims or marks a public surface citable',
        'required_checks': checks,
        'missing_required_checks': missing,
        'check_registry_audit': registry_audit,
        'winning_attempt_id': winning_attempt.get('attempt_id') if winning_attempt else None,
        'attempts': attempts,
        'observed': {
            'adapters': sorted(dict.fromkeys(observed_adapters)),
            'urls': observed_urls,
            'route_postures': sorted(dict.fromkeys(observed_postures)),
            'artifact_refs': artifacts,
            'cross_surface_conflicts': conflicts,
            'attempt_count': len(attempts),
            'privacy_redaction_review_present': global_privacy_redaction_review_present,
            'rehearsal_only': is_rehearsal,
        },
        'privacy_review': privacy,
        'review_notes': [
            'A reviewable verdict means one coherent attempt has enough first-wedge evidence for human review; it is not a support promotion by itself.',
            'A rehearsal verdict means the harness/evaluator path passed using synthetic local evidence; it is intentionally not a live proof.',
            'The evaluator now rejects proof bundles whose required facts are split across unrelated attempts, adapters, hosts, out-of-order actions, missing sequence_index order, missing per-action ChatGPT URL/adapter witnesses, missing post-submit /c/ conversation-route latest-turn witness, missing root-to-/c/ route transition, missing operator-submit attestation, missing submit-time composer readback matching the checkpoint prompt, missing non-aggregate assistant witness, missing transcript.latest user-turn witness matching the checkpoint prompt, missing non-aggregate user witness, missing same-frame user-before-assistant witness order, missing explicit frame context for both turn-pair witnesses, missing same-conversation /c/ route continuity for the post-latest settled witness, write/submit readbacks that only contain but do not exactly equal the checkpoint prompt, missing post-latest settled-generation witness, missing later-sequenced ChatGPT fixture/snapshot witness for settled generation, missing transcript.latest assistant-node witness, witness text that does not exactly match the transcript.latest reply, or fixture-only prompt/latest echoes without a successful write/readback action and a later transcript.latest exact reply.',
            'Public-citable wording still requires the existing live-proof intake, verdict, publication, redaction, and support-truth gates.',
            'If screenshot or trace artifacts are absent, keep the evidence local-reviewable rather than public-citable.',
        ],
    }


def summary_markdown(result: dict[str, Any]) -> str:
    lines = [
        '# ChatGPT first proof evaluation',
        '',
        f"- generated_at: `{result.get('generated_at')}`",
        f"- verdict: `{result.get('verdict')}`",
        f"- winning_attempt_id: `{result.get('winning_attempt_id')}`",
        f"- input: `{result.get('input_path')}`",
        f"- input_sha256: `{result.get('input_sha256')}`",
        f"- support_claim_effect: `{result.get('support_claim_effect')}`",
        '',
        '## Required checks',
        '',
    ]
    for key, value in (result.get('required_checks') or {}).items():
        mark = 'PASS' if value else 'BLOCKED'
        lines.append(f'- {mark}: `{key}`')
    missing = result.get('missing_required_checks') or []
    if missing:
        lines.extend(['', '## Missing', ''])
        for key in missing:
            lines.append(f'- `{key}`')
    attempts = result.get('attempts') or []
    lines.extend(['', '## Attempts', ''])
    for attempt in attempts:
        lines.append(f"- {'PASS' if attempt.get('ok') else 'BLOCKED'}: `{attempt.get('attempt_id')}` missing={attempt.get('missing_required_checks')}")
    privacy = result.get('privacy_review') or {}
    lines.extend(['', '## Privacy review', ''])
    lines.append(f"- scan_completed: `{privacy.get('scan_completed')}`")
    lines.append(f"- publishable_without_redaction_review: `{privacy.get('publishable_without_redaction_review')}`")
    lines.append(f"- review_required_before_publication: `{privacy.get('review_required_before_publication')}`")
    flags = privacy.get('flags') if isinstance(privacy.get('flags'), dict) else {}
    for key, value in flags.items():
        lines.append(f'- {key}: `{value}`')
    lines.extend(['', '## Review notes', ''])
    for note in result.get('review_notes') or []:
        lines.append(f'- {note}')
    return '\n'.join(lines) + '\n'


def history_entries(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = read_json(path)
    except Exception:
        return []
    entries = payload.get('entries') if isinstance(payload, dict) else None
    return [entry for entry in entries if isinstance(entry, dict)] if isinstance(entries, list) else []


def append_history(path: Path, result: dict[str, Any]) -> dict[str, Any]:
    entries = history_entries(path)
    entry = {
        'captured_at': result.get('generated_at'),
        'verdict': result.get('verdict'),
        'ok': result.get('ok'),
        'input_path': result.get('input_path'),
        'input_sha256': result.get('input_sha256'),
        'winning_attempt_id': result.get('winning_attempt_id'),
        'missing_required_checks': result.get('missing_required_checks'),
        'privacy_review_required_before_publication': (result.get('privacy_review') or {}).get('review_required_before_publication'),
    }
    entries.append(entry)
    payload = {
        'schema_version': SCHEMA_VERSION,
        'updated_at': utcnow(),
        'capture_count': len(entries),
        'latest_capture': entry,
        'entries': entries,
    }
    write_json(path, payload)
    return payload


def evaluate_file(input_path: Path, *, root: Path = ROOT, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH) -> dict[str, Any]:
    payload = read_json(input_path)
    result = evaluate_payload(payload, root=root, input_path=input_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / 'chatgpt-first-proof-evaluation.json', result)
    (output_dir / 'SUMMARY.md').write_text(summary_markdown(result), encoding='utf-8')
    history = append_history(history_path, result)
    result['history_update'] = {
        'history_path': str(history_path),
        'capture_count_after_write': history['capture_count'],
    }
    write_json(output_dir / 'chatgpt-first-proof-evaluation.json', result)
    return result


def summarize_history(path: Path = DEFAULT_HISTORY_PATH) -> dict[str, Any]:
    if not path.exists():
        return {'path': str(path), 'exists': False, 'capture_count': 0, 'latest_capture': None}
    payload = read_json(path)
    entries = payload.get('entries') if isinstance(payload, dict) else []
    return {
        'path': str(path),
        'exists': True,
        'capture_count': len(entries) if isinstance(entries, list) else 0,
        'latest_capture': entries[-1] if isinstance(entries, list) and entries else None,
        'history': payload,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Evaluate a captured ChatGPT first-proof bundle without widening support claims.')
    parser.add_argument('--root', type=Path, default=ROOT)
    sub = parser.add_subparsers(dest='command')
    eval_cmd = sub.add_parser('evaluate', help='Evaluate a captured proof/capture JSON file')
    eval_cmd.add_argument('--input', type=Path, default=DEFAULT_INPUT)
    eval_cmd.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT_DIR)
    eval_cmd.add_argument('--history-path', type=Path, default=DEFAULT_HISTORY_PATH)
    eval_cmd.add_argument('--pretty', action='store_true')
    hist_cmd = sub.add_parser('history', help='Summarize evaluation history')
    hist_cmd.add_argument('--history-path', type=Path, default=DEFAULT_HISTORY_PATH)
    hist_cmd.add_argument('--pretty', action='store_true')
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command in (None, 'evaluate'):
        input_path = getattr(args, 'input', DEFAULT_INPUT)
        output_dir = getattr(args, 'output_dir', DEFAULT_OUTPUT_DIR)
        history_path = getattr(args, 'history_path', DEFAULT_HISTORY_PATH)
        result = evaluate_file(input_path, root=args.root, output_dir=output_dir, history_path=history_path)
        print(json.dumps(result, indent=2 if getattr(args, 'pretty', False) else None))
        return 0 if result.get('ok') else 1
    if args.command == 'history':
        payload = summarize_history(args.history_path)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return 0
    parser.error(f'unknown command {args.command}')
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
