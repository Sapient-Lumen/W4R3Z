#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import re
import struct
import zlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from chatgpt_first_proof_artifact_ledger import ARTIFACT_SLOTS, build_artifact_ledger
from chatgpt_first_proof_bundle_audit import build_bundle_audit
from chatgpt_first_proof_evaluator import evaluate_payload, payload_declares_rehearsal
from chatgpt_first_proof_kit import EXPECTED_REPLY, PROBE_TEXT
from chatgpt_first_proof_schema_validation import DEFAULT_SCHEMA, read_json as read_json_file, sha256_file, validate_payload

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = ROOT / 'validation' / 'latest' / 'chatgpt-proof-rehearsal.json'
DEFAULT_PACK_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-proof-rehearsal-evidence-pack'
DEFAULT_SUMMARY = ROOT / 'validation' / 'latest' / 'chatgpt-proof-pack-export-summary.json'
EXPORTER_SCHEMA_VERSION = 1
ATTEMPT_KEYS = ('attempt_id', 'run_id', 'bundle_id', 'proof_id', 'session_id', 'capture_id')

JsonDict = dict[str, Any]


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def display_path(path: Path, *, root: Path = ROOT) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except Exception:
        return str(path)


def compact(value: Any) -> str:
    if not isinstance(value, str):
        return ''
    return ' '.join(value.split()).strip()


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {'1', 'true', 'yes', 'ok', 'passed', 'pass'}
    if isinstance(value, (int, float)):
        return bool(value)
    return False


def payload(item: JsonDict | None) -> JsonDict:
    if isinstance(item, dict) and isinstance(item.get('payload'), dict):
        return item['payload']  # type: ignore[return-value]
    return {}


def action_type(item: JsonDict | None) -> str:
    if not isinstance(item, dict):
        return ''
    value = item.get('type') or item.get('request_type') or payload(item).get('type')
    return compact(value)


def action_url(item: JsonDict | None) -> str:
    if not isinstance(item, dict):
        return ''
    for container in (item, payload(item)):
        url = container.get('url') or container.get('payload_url')
        if isinstance(url, str) and url.strip():
            return url.strip()
    return ''


def action_adapter(item: JsonDict | None) -> str:
    if not isinstance(item, dict):
        return ''
    for container in (item, payload(item)):
        adapter = container.get('adapter') or container.get('payload_adapter')
        if isinstance(adapter, str) and adapter.strip():
            return adapter.strip()
    return ''


def action_tab_id(item: JsonDict | None) -> int | None:
    if not isinstance(item, dict):
        return None
    for container in (item, payload(item)):
        for key in ('tab_id', 'tabId'):
            value = container.get(key)
            if isinstance(value, int) and value >= 0:
                return value
    return None


def conversation_path(url: str) -> str | None:
    try:
        parsed = urlparse(url)
    except Exception:
        return None
    if not parsed.netloc.endswith('chatgpt.com'):
        return None
    if re.match(r'^/c/[^/?#]+$', parsed.path):
        return parsed.path
    return None


def first_action(actions: list[JsonDict], kind: str) -> JsonDict | None:
    for action in actions:
        if action_type(action) == kind:
            return action
    return None


def actions_after(actions: list[JsonDict], sequence_index: int | None) -> list[JsonDict]:
    if sequence_index is None:
        return []
    out = []
    for action in actions:
        value = action.get('sequence_index')
        if isinstance(value, int) and value > sequence_index:
            out.append(action)
    return out


def action_sequence(action: JsonDict | None) -> int | None:
    if isinstance(action, dict) and isinstance(action.get('sequence_index'), int):
        return action['sequence_index']  # type: ignore[return-value]
    return None


def action_ok(action: JsonDict | None) -> bool:
    if not isinstance(action, dict):
        return False
    if isinstance(action.get('ok'), bool):
        return action['ok']  # type: ignore[return-value]
    if isinstance(payload(action).get('ok'), bool):
        return payload(action)['ok']  # type: ignore[return-value]
    return False


def normalized_action(action: JsonDict, attempt_id: str) -> JsonDict:
    row = copy.deepcopy(action)
    row.setdefault('attempt_id', attempt_id)
    row.setdefault('adapter', action_adapter(row) or 'chatgpt')
    row.setdefault('url', action_url(row) or 'https://chatgpt.com/')
    tab_id = action_tab_id(row)
    if tab_id is not None:
        row.setdefault('tab_id', tab_id)
    return row


def infer_attempt_id(source: JsonDict, actions: list[JsonDict]) -> str:
    for container in [source, *(actions or [])]:
        if not isinstance(container, dict):
            continue
        for key in ATTEMPT_KEYS:
            value = container.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return 'chatgpt-proof-exported-attempt'


def find_witness(action: JsonDict | None, *names: str) -> JsonDict:
    if not isinstance(action, dict):
        return {}
    containers = [action, payload(action)]
    for container in containers:
        for name in names:
            value = container.get(name)
            if isinstance(value, dict):
                return value
    return {}


def screenshot_bytes_from_source(source: JsonDict) -> tuple[bytes | None, str]:
    candidates: list[Any] = []
    for key in ('surface_screenshot_data_url', 'screenshot_data_url', 'visible_tab_screenshot_data_url'):
        candidates.append(source.get(key))
    captures = source.get('captures')
    if isinstance(captures, dict):
        for capture in captures.values():
            if isinstance(capture, dict):
                for key in ('surface_screenshot_data_url', 'screenshot_data_url', 'visible_tab_screenshot_data_url'):
                    candidates.append(capture.get(key))
    actions = source.get('actions')
    if isinstance(actions, list):
        for action in actions:
            if isinstance(action, dict):
                for container in (action, payload(action)):
                    for key in ('surface_screenshot_data_url', 'screenshot_data_url', 'visible_tab_screenshot_data_url'):
                        candidates.append(container.get(key))
    for candidate in candidates:
        if not isinstance(candidate, str):
            continue
        raw = candidate.strip()
        if raw.startswith('data:image/png;base64,'):
            return base64.b64decode(raw.split(',', 1)[1]), 'source-data-url'
    return None, 'missing'


def png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)


def placeholder_png() -> bytes:
    width = 1
    height = 1
    # Filter byte + RGBA pixel. A visible red pixel makes accidental publication less likely than transparent.
    raw = b'\x00\xff\x00\x00\xff'
    return b'\x89PNG\r\n\x1a\n' + png_chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)) + png_chunk(b'IDAT', zlib.compress(raw)) + png_chunk(b'IEND', b'')


def route_witness(source: JsonDict, actions: list[JsonDict], attempt_id: str) -> JsonDict:
    source_route = source.get('route_witness') if isinstance(source.get('route_witness'), dict) else {}
    write = first_action(actions, 'prompt.write') or (actions[0] if actions else {})
    url = source_route.get('url') or action_url(write) or 'https://chatgpt.com/'
    return {
        'schema_version': 1,
        'attempt_id': attempt_id,
        'adapter': source_route.get('adapter') or action_adapter(write) or 'chatgpt',
        'url': url,
        'host': urlparse(str(url)).netloc if isinstance(url, str) and url else 'chatgpt.com',
        'tab_id': source_route.get('tab_id') if isinstance(source_route.get('tab_id'), int) else action_tab_id(write),
        'route_posture': source_route.get('route_posture') or 'plain-chat',
        'source': 'exported-from-sidepanel-capture-or-rehearsal',
    }


def route_posture_note(source: JsonDict) -> str:
    rehearsal = payload_declares_rehearsal(source)
    mode = 'offline rehearsal' if rehearsal else 'operator-supplied live capture'
    return (
        '# Receiver posture\n\n'
        f'- source mode: `{mode}`\n'
        '- expected surface: ChatGPT plain chat only\n'
        '- excluded branches: Search, Projects, GPTs, Canvas, files, voice, apps, agent/task mode, shared links, data analysis, image generation, desktop apps, and mobile surfaces\n'
        '- publication/support effect: none without live evaluator pass and human privacy review\n'
    )


def selected_prompt_selector(write: JsonDict | None, source: JsonDict) -> str | None:
    if isinstance(write, dict):
        for key in ('selector_hint', 'prompt_selector'):
            value = write.get(key) or payload(write).get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    contract = source.get('surface_contract') if isinstance(source.get('surface_contract'), dict) else None
    if contract:
        required = contract.get('required') if isinstance(contract.get('required'), dict) else {}
        value = required.get('prompt_selector')
        if isinstance(value, str):
            return value
    return '#prompt-textarea'


def selected_send_selector(submit: JsonDict | None, source: JsonDict) -> str | None:
    if isinstance(submit, dict):
        for key in ('submit_selector', 'observed_live_send_selector'):
            value = submit.get(key) or payload(submit).get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        observed = submit.get('proof_live_gate_observed') or payload(submit).get('proof_live_gate_observed')
        if isinstance(observed, dict):
            value = observed.get('submit_selector')
            if isinstance(value, str) and value.strip():
                return value.strip()
    contract = source.get('surface_contract') if isinstance(source.get('surface_contract'), dict) else None
    if contract:
        required = contract.get('required') if isinstance(contract.get('required'), dict) else {}
        strict_send = required.get('strict_send') if isinstance(required.get('strict_send'), dict) else {}
        value = strict_send.get('selector')
        if isinstance(value, str):
            return value
    return '#composer-submit-button'


def write_sidecar_manifest(pack_dir: Path) -> list[JsonDict]:
    rows = []
    for slot in ARTIFACT_SLOTS:
        path = pack_dir / slot.filename
        rows.append({
            'order': slot.order,
            'filename': slot.filename,
            'phase': slot.phase,
            'artifact_type': slot.artifact_type,
            'required_for': slot.required_for,
            'exists': path.exists(),
            'size': path.stat().st_size if path.exists() else None,
            'sha256': sha256_file(path) if path.exists() else None,
        })
    return rows


def build_manifest(source: JsonDict, actions: list[JsonDict], attempt_id: str, route: JsonDict, pack_dir: Path) -> JsonDict:
    normalized_actions = [normalized_action(action, attempt_id) for action in actions]
    source_artifacts = source.get('artifacts') if isinstance(source.get('artifacts'), dict) else {}
    manifest = {
        'schema_version': 1,
        'bundle_schema': 'chatgpt-first-proof-bundle/v1',
        'surface_key': 'chatgpt',
        'attempt_id': attempt_id,
        'run_id': source.get('run_id') or attempt_id,
        'capture_kind': source.get('capture_kind') or source.get('proof_mode') or 'sidepanel-chatgpt-first-proof',
        'proof_mode': source.get('proof_mode') or ('offline-rehearsal' if payload_declares_rehearsal(source) else 'live-or-unknown'),
        'rehearsal_only': payload_declares_rehearsal(source),
        'probe_prompt': {
            'text': PROBE_TEXT,
            'expected_exact_reply': EXPECTED_REPLY,
        },
        'route_witness': route,
        'privacy_redaction_review': source.get('privacy_redaction_review') if isinstance(source.get('privacy_redaction_review'), dict) else {
            'review_required_before_publication': True,
            'publishable_without_redaction_review': False,
            'reviewer': 'pending-human-review',
            'notes': ['Generated evidence pack still requires human privacy review before publication.'],
        },
        'actions': normalized_actions,
        'captures': source.get('captures') if isinstance(source.get('captures'), dict) else {},
        'operator_transfer': source.get('operator_transfer') if isinstance(source.get('operator_transfer'), dict) else {},
        'artifacts': {
            **source_artifacts,
            'pack_dir': display_path(pack_dir),
            'artifact_slots': write_sidecar_manifest(pack_dir),
            'source_bundle_sha256': source.get('source_bundle_sha256'),
            'exported_from': source.get('tool') or source.get('capture_kind') or 'unknown-source',
        },
        'operator_notes': [
            'This manifest is assembled from material evidence-pack artifacts and can be passed to schema validation, bundle audit, and evaluator scripts.',
            'If proof_mode is offline-rehearsal, the evaluator must return rehearsal-harness-ok-not-live rather than a live reviewable verdict.',
        ],
    }
    return manifest


def export_pack(source_path: Path, pack_dir: Path = DEFAULT_PACK_DIR, *, summary_path: Path = DEFAULT_SUMMARY, clean: bool = False, allow_placeholder_screenshot: bool | None = None) -> JsonDict:
    source = read_json(source_path)
    if not isinstance(source, dict):
        raise ValueError(f'{source_path} must contain a JSON object')
    source = copy.deepcopy(source)
    source['source_bundle_sha256'] = sha256_file(source_path)
    actions = [action for action in source.get('actions', []) if isinstance(action, dict)] if isinstance(source.get('actions'), list) else []
    attempt_id = infer_attempt_id(source, actions)
    rehearsal = payload_declares_rehearsal(source)
    if allow_placeholder_screenshot is None:
        allow_placeholder_screenshot = rehearsal
    if clean and pack_dir.exists():
        for child in sorted(pack_dir.iterdir(), reverse=True):
            if child.is_dir():
                for nested in sorted(child.rglob('*'), reverse=True):
                    if nested.is_file():
                        nested.unlink()
                    elif nested.is_dir():
                        nested.rmdir()
                child.rmdir()
            else:
                child.unlink()
    pack_dir.mkdir(parents=True, exist_ok=True)

    write = first_action(actions, 'prompt.write')
    submit = first_action(actions, 'prompt.submit')
    latest = first_action(actions, 'transcript.latest')
    latest_seq = action_sequence(latest)
    settled_candidates = [action for action in actions_after(actions, latest_seq) if action_type(action) in {'fixture.capture', 'state.snapshot'}]
    settled = settled_candidates[0] if settled_candidates else first_action(actions, 'fixture.capture') or first_action(actions, 'state.snapshot')
    route = route_witness(source, actions, attempt_id)
    prompt_selector = selected_prompt_selector(write, source)
    send_selector = selected_send_selector(submit, source)
    assistant = find_witness(latest, 'latest_output_witness')
    user = find_witness(latest, 'latest_user_turn_witness', 'user_turn_witness')
    write_readback = compact((write or {}).get('readback') or payload(write or {}).get('readback'))
    submit_readback = compact((submit or {}).get('composer_readback_before_submit') or (submit or {}).get('prompt_before_submit') or (submit or {}).get('submitted_prompt') or payload(submit or {}).get('composer_readback_before_submit'))
    latest_text = compact(payload(latest or {}).get('text') or (latest or {}).get('text'))

    write_json(pack_dir / 'route-witness.json', route)
    screenshot, screenshot_source = screenshot_bytes_from_source(source)
    screenshot_placeholder = False
    if screenshot is None and allow_placeholder_screenshot:
        screenshot = placeholder_png()
        screenshot_source = 'generated-placeholder-not-live'
        screenshot_placeholder = True
    if screenshot is not None:
        (pack_dir / 'surface-screenshot.png').write_bytes(screenshot)
    write_json(pack_dir / 'surface-screenshot.metadata.json', {
        'schema_version': 1,
        'attempt_id': attempt_id,
        'source': screenshot_source,
        'placeholder_not_live': screenshot_placeholder,
        'sha256': sha256_bytes(screenshot) if screenshot else None,
        'operator_note': 'A generated placeholder is acceptable only for offline rehearsal/exporter tests. Live proof requires an actual local screenshot plus human redaction review.',
    })
    write_text(pack_dir / 'receiver-posture.md', route_posture_note(source))
    write_json(pack_dir / 'composer-candidates.json', {
        'schema_version': 1,
        'attempt_id': attempt_id,
        'selected': {'selector': prompt_selector, 'source': 'write-action-or-contract'},
        'rejected': [
            {'selector': '#composer-plus-btn', 'reason': 'non-send composer control; add-files/plus button'},
            {'selector': 'textarea[name="prompt-textarea"]', 'reason': 'fallback textarea may be hidden; prefer visible #prompt-textarea when available'},
        ],
        'source_write_action': write,
    })
    write_text(pack_dir / 'composer-before.txt', (compact((write or {}).get('composer_before') or payload(write or {}).get('composer_before')) or '[empty]') + '\n')
    write_text(pack_dir / 'composer-after.txt', write_readback + '\n')
    write_json(pack_dir / 'composer-witness-receipt.json', {
        'schema_version': 1,
        'attempt_id': attempt_id,
        'prompt_selector': prompt_selector,
        'readback': write_readback,
        'readback_exact_probe': write_readback == PROBE_TEXT,
        'write_action': write,
    })
    write_text(pack_dir / 'probe-prompt.txt', PROBE_TEXT + '\n')
    write_json(pack_dir / 'submit-evidence.json', {
        'schema_version': 1,
        'attempt_id': attempt_id,
        'submit_selector': send_selector,
        'operator_submit_confirmed': truthy((submit or {}).get('operator_submit_confirmed') or payload(submit or {}).get('operator_submit_confirmed')),
        'submit_method': (submit or {}).get('submit_method') or payload(submit or {}).get('submit_method'),
        'proof_live_gate_ok': truthy((submit or {}).get('proof_live_gate_ok') or payload(submit or {}).get('proof_live_gate_ok')),
        'proof_live_gate_verdict': (submit or {}).get('proof_live_gate_verdict') or payload(submit or {}).get('proof_live_gate_verdict'),
        'submit_action': submit,
    })
    write_json(pack_dir / 'submit-prompt-readback.json', {
        'schema_version': 1,
        'attempt_id': attempt_id,
        'readback': submit_readback,
        'readback_exact_probe': submit_readback == PROBE_TEXT,
        'fields': {
            'composer_readback_before_submit': (submit or {}).get('composer_readback_before_submit') or payload(submit or {}).get('composer_readback_before_submit'),
            'prompt_before_submit': (submit or {}).get('prompt_before_submit') or payload(submit or {}).get('prompt_before_submit'),
            'submitted_prompt': (submit or {}).get('submitted_prompt') or payload(submit or {}).get('submitted_prompt'),
        },
    })
    write_json(pack_dir / 'generation-timeline.json', {
        'schema_version': 1,
        'attempt_id': attempt_id,
        'events': [
            {
                'sequence_index': action.get('sequence_index'),
                'type': action_type(action),
                'url': action_url(action),
                'conversation_route_path': conversation_path(action_url(action)),
                'generation_state': (payload(action).get('metadata') if isinstance(payload(action).get('metadata'), dict) else {}).get('generation_state') or payload(action).get('generation_state') or action.get('generation_state'),
            }
            for action in actions
        ],
    })
    write_json(pack_dir / 'transcript-latest-action.json', {
        'schema_version': 1,
        'attempt_id': attempt_id,
        'latest_text': latest_text,
        'expected_exact_reply': EXPECTED_REPLY,
        'exact_reply': latest_text == EXPECTED_REPLY,
        'latest_action': latest,
    })
    write_json(pack_dir / 'assistant-output-witness.json', {'schema_version': 1, 'attempt_id': attempt_id, 'witness': assistant})
    write_json(pack_dir / 'assistant-output-text-coherence.json', {
        'schema_version': 1,
        'attempt_id': attempt_id,
        'latest_text': latest_text,
        'witness_text': compact(assistant.get('text')),
        'matches_latest_text': compact(assistant.get('text')) == latest_text,
        'matches_expected_reply': compact(assistant.get('text')) == EXPECTED_REPLY,
    })
    write_json(pack_dir / 'assistant-witness-scope.json', {
        'schema_version': 1,
        'attempt_id': attempt_id,
        'witness_scope': assistant.get('witness_scope'),
        'role_mixture_detected': assistant.get('role_mixture_detected'),
        'contains_user_turn_text': assistant.get('contains_user_turn_text'),
        'contains_assistant_turn_text': assistant.get('contains_assistant_turn_text'),
        'not_aggregate_parent': assistant.get('witness_scope') == 'leaf-turn' and not truthy(assistant.get('role_mixture_detected')),
    })
    write_json(pack_dir / 'user-turn-witness.json', {'schema_version': 1, 'attempt_id': attempt_id, 'witness': user})
    write_json(pack_dir / 'user-witness-scope.json', {
        'schema_version': 1,
        'attempt_id': attempt_id,
        'witness_scope': user.get('witness_scope'),
        'role_mixture_detected': user.get('role_mixture_detected'),
        'contains_user_turn_text': user.get('contains_user_turn_text'),
        'contains_assistant_turn_text': user.get('contains_assistant_turn_text'),
        'not_aggregate_parent': user.get('witness_scope') == 'leaf-turn' and not truthy(user.get('role_mixture_detected')),
    })
    assistant_order = assistant.get('document_order_index') if isinstance(assistant.get('document_order_index'), int) else None
    user_order = user.get('document_order_index') if isinstance(user.get('document_order_index'), int) else None
    write_json(pack_dir / 'turn-pair-order-witness.json', {
        'schema_version': 1,
        'attempt_id': attempt_id,
        'user_document_order_index': user_order,
        'assistant_document_order_index': assistant_order,
        'user_before_assistant': isinstance(user_order, int) and isinstance(assistant_order, int) and user_order < assistant_order,
    })
    write_json(pack_dir / 'turn-pair-frame-context-witness.json', {
        'schema_version': 1,
        'attempt_id': attempt_id,
        'user_frame_depth': user.get('frame_depth'),
        'user_frame_path': user.get('frame_path'),
        'assistant_frame_depth': assistant.get('frame_depth'),
        'assistant_frame_path': assistant.get('frame_path'),
        'same_frame_context': user.get('frame_depth') == assistant.get('frame_depth') and user.get('frame_path') == assistant.get('frame_path'),
    })
    tab_ids = sorted({tab for tab in (action_tab_id(action) for action in actions) if isinstance(tab, int)})
    write_json(pack_dir / 'same-tab-context-witness.json', {'schema_version': 1, 'attempt_id': attempt_id, 'tab_ids': tab_ids, 'same_tab_context': len(tab_ids) == 1})
    latest_paths = sorted({path for path in (conversation_path(action_url(action)) for action in actions if action_type(action) == 'transcript.latest') if path})
    settled_paths = sorted({path for path in (conversation_path(action_url(action)) for action in actions if action_type(action) in {'fixture.capture', 'state.snapshot'}) if path})
    write_json(pack_dir / 'same-conversation-route-witness.json', {'schema_version': 1, 'attempt_id': attempt_id, 'latest_conversation_paths': latest_paths, 'settled_conversation_paths': settled_paths, 'same_conversation_route_after_latest': bool(set(latest_paths).intersection(settled_paths))})
    pre_submit_urls = [action_url(action) for action in actions if (action_sequence(action) or -1) <= (action_sequence(submit) or -1)]
    write_json(pack_dir / 'route-transition-witness.json', {
        'schema_version': 1,
        'attempt_id': attempt_id,
        'pre_submit_urls': pre_submit_urls,
        'post_submit_conversation_paths': latest_paths,
        'root_to_conversation_route_transition': bool(any(url.startswith('https://chatgpt.com/') and conversation_path(url) is None for url in pre_submit_urls) and latest_paths),
    })
    write_json(pack_dir / 'exact-readback-witness.json', {
        'schema_version': 1,
        'attempt_id': attempt_id,
        'write_readback': write_readback,
        'submit_readback': submit_readback,
        'probe_text': PROBE_TEXT,
        'write_exact': write_readback == PROBE_TEXT,
        'submit_exact': submit_readback == PROBE_TEXT,
        'both_exact': write_readback == PROBE_TEXT and submit_readback == PROBE_TEXT,
    })
    settled_metadata = payload(settled or {}).get('metadata') if isinstance(payload(settled or {}).get('metadata'), dict) else {}
    write_json(pack_dir / 'settled-generation-witness.json', {
        'schema_version': 1,
        'attempt_id': attempt_id,
        'settled_action': settled,
        'generation_state': settled_metadata.get('generation_state') or payload(settled or {}).get('generation_state'),
        'generation_stop_control_present': settled_metadata.get('generation_stop_control_present') if 'generation_stop_control_present' in settled_metadata else payload(settled or {}).get('generation_stop_control_present'),
    })
    write_json(pack_dir / 'settled-generation-sequence-witness.json', {
        'schema_version': 1,
        'attempt_id': attempt_id,
        'latest_sequence_index': latest_seq,
        'settled_sequence_index': action_sequence(settled),
        'settled_after_latest': isinstance(latest_seq, int) and isinstance(action_sequence(settled), int) and action_sequence(settled) > latest_seq,
        'adapter': action_adapter(settled) if settled else None,
        'url': action_url(settled) if settled else None,
        'tab_id': action_tab_id(settled) if settled else None,
    })

    # Slot 30 before manifest so the manifest artifact list sees it.
    write_text(pack_dir / 'privacy-redaction-review.md', (
        '# Privacy/redaction review\n\n'
        '- status: pending human review\n'
        f'- source proof mode: `{source.get("proof_mode") or ("offline-rehearsal" if rehearsal else "live-or-unknown")}`\n'
        '- publishable_without_redaction_review: false\n'
        '- note: Generated by local exporter. Live publication requires human review of screenshots, transcript text, and any visible account/UI details.\n'
    ))

    manifest = build_manifest(source, actions, attempt_id, route, pack_dir)
    write_json(pack_dir / 'bundle-manifest.json', manifest)
    schema = read_json_file(DEFAULT_SCHEMA)
    validation_core = validate_payload(manifest, schema if isinstance(schema, dict) else {})
    validation_report = {
        'schema_version': 1,
        'validation_key': 'chatgpt-first-proof-bundle-schema-validation',
        'generated_at': utcnow(),
        'project': 'GlassTTY',
        'surface_key': 'chatgpt',
        'input_path': display_path(pack_dir / 'bundle-manifest.json'),
        'input_sha256': sha256_file(pack_dir / 'bundle-manifest.json'),
        'schema_path': display_path(DEFAULT_SCHEMA),
        'schema_sha256': sha256_file(DEFAULT_SCHEMA),
        **validation_core,
        'support_claim_effect': 'none; schema validation is local structural evidence and never widens support claims',
    }
    write_json(pack_dir / 'bundle-schema-validation.json', validation_report)
    audit = build_bundle_audit(manifest, root=ROOT, input_path=pack_dir / 'bundle-manifest.json')
    write_json(pack_dir / 'chatgpt-first-proof-bundle-audit.json', audit)
    evaluation = evaluate_payload(manifest, root=ROOT, input_path=pack_dir / 'bundle-manifest.json')
    write_json(pack_dir / 'chatgpt-first-proof-evaluation.json', evaluation)
    ledger = build_artifact_ledger(pack_dir, readiness_level='review-ready')
    write_json(pack_dir / 'artifact-ledger.json', ledger)

    summary = {
        'schema_version': EXPORTER_SCHEMA_VERSION,
        'tool': 'glasstty-chatgpt-proof-pack-exporter',
        'generated_at': utcnow(),
        'ok': bool(validation_report.get('ok') and evaluation.get('harness_ok') and ledger.get('ready')),
        'live_proof': not rehearsal,
        'rehearsal_only': rehearsal,
        'verdict': 'exported-rehearsal-evidence-pack-not-live' if rehearsal else 'exported-live-or-unknown-evidence-pack',
        'source_path': display_path(source_path),
        'source_sha256': sha256_file(source_path),
        'pack_dir': display_path(pack_dir),
        'attempt_id': attempt_id,
        'artifact_count': len([slot for slot in ARTIFACT_SLOTS if (pack_dir / slot.filename).exists()]),
        'expected_artifact_count': len(ARTIFACT_SLOTS),
        'screenshot_source': screenshot_source,
        'screenshot_placeholder_not_live': screenshot_placeholder,
        'schema_validation_ok': validation_report.get('ok'),
        'evaluator_verdict': evaluation.get('verdict'),
        'evaluator_harness_ok': evaluation.get('harness_ok'),
        'evaluator_missing_required_checks': evaluation.get('missing_required_checks'),
        'ledger_ready_review_level': ledger.get('ready'),
        'ledger_missing_required': ledger.get('missing_required_artifacts'),
        'operator_next_steps': [
            'For live use, run the side-panel proof helper, save the assembled JSON, then run proof-export-pack against that live capture.',
            'Do not treat a rehearsal pack as live evidence; it exists to prove the exporter/ledger/schema/audit/evaluator chain is wired.',
            'Replace placeholder screenshots with a real local screenshot before live review.',
        ],
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(summary_path, summary)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Export a ChatGPT first-proof capture/rehearsal JSON into the 30-slot evidence-pack layout.')
    parser.add_argument('--input', type=Path, default=DEFAULT_INPUT, help='Side-panel capture or rehearsal bundle JSON')
    parser.add_argument('--pack-dir', type=Path, default=DEFAULT_PACK_DIR, help='Directory to write the 30-slot evidence pack')
    parser.add_argument('--summary-out', type=Path, default=DEFAULT_SUMMARY, help='Summary JSON path')
    parser.add_argument('--clean', action='store_true', help='Delete existing files in the pack directory before export')
    parser.add_argument('--allow-placeholder-screenshot', action='store_true', help='Permit a generated non-live placeholder screenshot when the source lacks one')
    parser.add_argument('--no-placeholder-screenshot', action='store_true', help='Do not generate a placeholder screenshot even for rehearsals')
    parser.add_argument('--pretty', action='store_true')
    parser.add_argument('--require-ok', action='store_true')
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    allow: bool | None = None
    if args.allow_placeholder_screenshot:
        allow = True
    if args.no_placeholder_screenshot:
        allow = False
    summary = export_pack(args.input, args.pack_dir, summary_path=args.summary_out, clean=args.clean, allow_placeholder_screenshot=allow)
    print(json.dumps(summary, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)))
    if args.require_ok and not summary.get('ok'):
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
