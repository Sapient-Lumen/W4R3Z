#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from chatgpt_browser_envelope_receipt import build_chatgpt_browser_envelope_receipt, evaluate_chatgpt_browser_envelope_receipt
except ModuleNotFoundError:  # pragma: no cover - import path differs under tests
    import importlib.util

    def _load(name: str, filename: str):
        path = Path(__file__).resolve().parent / filename
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    _BROWSER = _load('chatgpt_browser_envelope_receipt', 'chatgpt_browser_envelope_receipt.py')
    build_chatgpt_browser_envelope_receipt = _BROWSER.build_chatgpt_browser_envelope_receipt
    evaluate_chatgpt_browser_envelope_receipt = _BROWSER.evaluate_chatgpt_browser_envelope_receipt

ROOT = Path(__file__).resolve().parent.parent
ROOT_OUTPUT_PATH = ROOT / 'CHATGPT-RETENTION-ENVELOPE-RECEIPT.json'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-retention-envelope-receipt'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'chatgpt-retention-envelope-receipt-captures.json'
REPORT_COMMAND = 'python scripts/chatgpt-retention-envelope-receipt.py --pretty'
CAPTURE_COMMAND = 'python scripts/chatgpt-retention-envelope-receipt.py capture --output-dir validation/latest/chatgpt-retention-envelope-receipt'
HISTORY_COMMAND = 'python scripts/chatgpt-retention-envelope-receipt.py history --pretty'
WRITE_ROOT_COMMAND = 'python scripts/chatgpt-retention-envelope-receipt.py write-root'
EVALUATE_COMMAND = 'python scripts/chatgpt-retention-envelope-receipt.py evaluate --promotion path/to/promotion-window.json --pretty'

Payload = dict[str, Any]

HISTORY_MODE_ALIASES = {
    'saved-history': 'saved-history',
    'saved-history-available': 'saved-history',
    'persistent-history': 'saved-history',
    'standard-history': 'saved-history',
    'ephemeral-no-history': 'ephemeral-no-history',
    'temporary-no-history': 'ephemeral-no-history',
    'temporary-chat': 'ephemeral-no-history',
    'guest-no-saved-history': 'guest-no-saved-history',
    'ephemeral-no-saved-history': 'guest-no-saved-history',
    'logged-out-no-history': 'guest-no-saved-history',
}

MEMORY_MODE_ALIASES = {
    'memory-on': 'memory-on',
    'memory-enabled': 'memory-on',
    'reference-chat-history-on': 'memory-on',
    'memory-off': 'memory-off',
    'memory-disabled': 'memory-off',
    'reference-chat-history-off': 'memory-off',
    'temporary-no-memory': 'temporary-no-memory',
    'temporary-chat': 'temporary-no-memory',
    'unavailable': 'unavailable',
    'not-applicable': 'unavailable',
}

CONTEXT_MODE_ALIASES = {
    'fresh-context': 'fresh-context',
    'clean-context': 'fresh-context',
    'clean-profile': 'fresh-context',
    'non-persistent-context': 'fresh-context',
    'reused-storage-state': 'reused-storage-state',
    'storage-state': 'reused-storage-state',
    'persisted-auth-state': 'reused-storage-state',
    'manual-login-live': 'manual-login-live',
    'manual-login': 'manual-login-live',
    'live-login': 'manual-login-live',
}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _history_entries(path: Path) -> list[dict[str, Any]]:
    try:
        payload = _read_json(path)
    except Exception:
        return []
    entries = payload.get('entries') if isinstance(payload, dict) else None
    return [entry for entry in entries if isinstance(entry, dict)] if isinstance(entries, list) else []


def summarize_capture_history(path: Path | None = None) -> dict[str, Any]:
    history_path = path or DEFAULT_HISTORY_PATH
    entries = _history_entries(history_path)
    payload = _read_json(history_path) if history_path.exists() else None
    latest = entries[-1] if entries else None
    return {
        'path': str(history_path),
        'exists': history_path.exists(),
        'capture_count': len(entries),
        'latest_capture': latest,
        'history': payload,
    }


def _changed_fields(previous: dict[str, Any] | None, current: dict[str, Any]) -> list[str]:
    if not previous:
        return sorted(current.keys())
    return [key for key in sorted(set(previous) | set(current)) if previous.get(key) != current.get(key)]


def _history_payload(entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        'schema_version': 1,
        'updated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'capture_count': len(entries),
        'entries': entries,
    }


def _normalize_keyish(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower().replace('_', '-').replace(' ', '-')
    return normalized or None


def _normalize_text(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = ' '.join(value.strip().lower().split())
    return normalized or None


def _collect_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            if isinstance(item, str) and item.strip():
                out.append(item.strip())
        return out
    return []


def _window_payloads(promotion: Payload) -> list[Payload]:
    for key in ('proof_windows', 'windows', 'bundles', 'runs'):
        raw = promotion.get(key)
        if isinstance(raw, list):
            return [item for item in raw if isinstance(item, dict)]
    single = promotion.get('proof_window')
    if isinstance(single, dict):
        return [single]
    bundle = promotion.get('bundle')
    if isinstance(bundle, dict):
        return [bundle]
    return []


def _summary_lookup(browser_eval: Payload) -> dict[int, Payload]:
    raw = browser_eval.get('window_browser_profiles')
    out: dict[int, Payload] = {}
    if not isinstance(raw, list):
        return out
    for item in raw:
        if not isinstance(item, dict):
            continue
        idx = item.get('window_index')
        if isinstance(idx, int):
            out[idx - 1] = item
    return out


def _auth_profile_lookup(browser_eval: Payload) -> dict[int, Payload]:
    auth_eval = browser_eval.get('auth_workspace_evaluation') if isinstance(browser_eval.get('auth_workspace_evaluation'), dict) else {}
    raw = auth_eval.get('window_auth_profiles')
    out: dict[int, Payload] = {}
    if not isinstance(raw, list):
        return out
    for item in raw:
        if not isinstance(item, dict):
            continue
        idx = item.get('window_index')
        if isinstance(idx, int):
            out[idx - 1] = item
    return out


def _artifact_rows(window: Payload) -> list[Payload]:
    rows: list[Payload] = []
    for key in ('artifact_refs', 'artifacts', 'bundle_artifacts'):
        raw = window.get(key)
        if isinstance(raw, list):
            rows.extend(item for item in raw if isinstance(item, dict))
    return rows


def _artifact_hints(rows: list[Payload]) -> list[str]:
    hints: list[str] = []
    for row in rows:
        for field in ('kind', 'path', 'role'):
            value = row.get(field)
            if isinstance(value, str) and value.strip():
                hints.append(value.strip())
    return hints


def _window_strings(window: Payload) -> list[str]:
    strings: list[str] = []
    route = window.get('route_witness') if isinstance(window.get('route_witness'), dict) else {}
    for source in (window, route):
        if not isinstance(source, dict):
            continue
        for key in ('title', 'page_title', 'route_title', 'workspace_label', 'workspace_name'):
            strings.extend(_collect_strings(source.get(key)))
        for key in ('visible_text', 'main_region_text', 'surface_identity_text', 'workspace_labels'):
            strings.extend(_collect_strings(source.get(key)))
    strings.extend(_artifact_hints(_artifact_rows(window)))
    return strings


def _normalize_boolish(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    normalized = _normalize_keyish(value)
    if normalized in {'true', 'yes', 'on', 'temporary', 'temp'}:
        return True
    if normalized in {'false', 'no', 'off', 'standard', 'persistent'}:
        return False
    return None


def _temporary_chat_mode(window: Payload, auth_profile: Payload | None) -> str | None:
    for source in (window, window.get('route_witness') if isinstance(window.get('route_witness'), dict) else {}):
        if not isinstance(source, dict):
            continue
        for key in ('temporary_chat', 'is_temporary_chat', 'temporary_mode'):
            value = _normalize_boolish(source.get(key))
            if value is True:
                return 'temporary'
            if value is False:
                return 'not-temporary'
        for key in ('chat_mode', 'conversation_mode', 'history_mode', 'chat_history_mode'):
            value = _normalize_keyish(source.get(key))
            if value in {'temporary', 'temp', 'temporary-chat'}:
                return 'temporary'
            if value in {'standard', 'normal', 'default', 'saved-history', 'persistent-history'}:
                return 'not-temporary'
    joined = ' '.join((_normalize_text(item) or '') for item in _window_strings(window))
    if 'temporary chat' in joined:
        return 'temporary'
    if 'guest-home-single-thread' == _normalize_keyish((auth_profile or {}).get('matched_posture_key')):
        return 'not-temporary'
    if _normalize_keyish((auth_profile or {}).get('auth_posture')) == 'logged-out':
        return 'not-temporary'
    return None


def _history_retention_mode(window: Payload, auth_profile: Payload | None, temporary_chat_mode: str | None) -> str | None:
    for source in (window, window.get('route_witness') if isinstance(window.get('route_witness'), dict) else {}):
        if not isinstance(source, dict):
            continue
        for key in ('history_retention_mode', 'history_mode', 'chat_history_mode', 'history_availability'):
            value = HISTORY_MODE_ALIASES.get(_normalize_keyish(source.get(key)) or '')
            if value:
                return value
    if temporary_chat_mode == 'temporary':
        return 'ephemeral-no-history'
    auth_posture = _normalize_keyish((auth_profile or {}).get('auth_posture'))
    auth_history = HISTORY_MODE_ALIASES.get(_normalize_keyish((auth_profile or {}).get('history_mode')) or '')
    if auth_history:
        return auth_history
    if auth_posture == 'logged-out':
        return 'guest-no-saved-history'
    joined = ' '.join((_normalize_text(item) or '') for item in _window_strings(window))
    if "won't appear in your history" in joined or 'will not appear in your history' in joined:
        return 'ephemeral-no-history'
    if 'history search' in joined or 'saved history' in joined or 'sidebar search' in joined:
        return 'saved-history'
    return None


def _memory_mode(window: Payload, auth_profile: Payload | None, temporary_chat_mode: str | None) -> str | None:
    for source in (window, window.get('route_witness') if isinstance(window.get('route_witness'), dict) else {}):
        if not isinstance(source, dict):
            continue
        for key in ('memory_mode', 'reference_chat_history_mode', 'memory_setting'):
            value = MEMORY_MODE_ALIASES.get(_normalize_keyish(source.get(key)) or '')
            if value:
                return value
        for key in ('memory_enabled', 'reference_chat_history_enabled'):
            value = source.get(key)
            if value is True:
                return 'memory-on'
            if value is False:
                return 'memory-off'
    if temporary_chat_mode == 'temporary':
        return 'temporary-no-memory'
    if _normalize_keyish((auth_profile or {}).get('auth_posture')) == 'logged-out':
        return 'unavailable'
    joined = ' '.join((_normalize_text(item) or '') for item in _window_strings(window))
    if 'memory off' in joined or 'reference chat history off' in joined:
        return 'memory-off'
    if 'memory on' in joined or 'reference chat history on' in joined:
        return 'memory-on'
    return None


def _context_persistence_mode(window: Payload) -> str | None:
    for source in (window, window.get('route_witness') if isinstance(window.get('route_witness'), dict) else {}):
        if not isinstance(source, dict):
            continue
        for key in ('context_persistence_mode', 'browser_context_mode', 'storage_state_mode', 'auth_bootstrap_mode'):
            value = CONTEXT_MODE_ALIASES.get(_normalize_keyish(source.get(key)) or '')
            if value:
                return value
    joined = ' '.join((_normalize_text(item) or '') for item in _window_strings(window))
    if 'storage state' in joined or 'storage-state' in joined or 'persisted auth state' in joined:
        return 'reused-storage-state'
    if 'manual login' in joined or 'live login' in joined:
        return 'manual-login-live'
    if 'fresh context' in joined or 'clean profile' in joined or 'non-persistent context' in joined or 'newcontext' in joined:
        return 'fresh-context'
    if 'clean-profile' in joined and 'manual login' not in joined:
        return 'fresh-context'
    return None


def _window_retention_profile(index: int, window: Payload, browser_profile: Payload | None, auth_profile: Payload | None) -> Payload:
    temporary = _temporary_chat_mode(window, auth_profile)
    history = _history_retention_mode(window, auth_profile, temporary)
    memory = _memory_mode(window, auth_profile, temporary)
    context = _context_persistence_mode(window)
    return {
        'window_index': index,
        'proof_window_token': (browser_profile or {}).get('proof_window_token') or (auth_profile or {}).get('proof_window_token'),
        'browser_lane': (browser_profile or {}).get('browser_lane'),
        'auth_posture': (auth_profile or {}).get('auth_posture'),
        'workspace_kind': (auth_profile or {}).get('workspace_kind'),
        'temporary_chat_mode': temporary,
        'history_retention_mode': history,
        'memory_mode': memory,
        'context_persistence_mode': context,
        'retention_signature': '|'.join(str(item or 'unknown') for item in (temporary, history, memory, context)),
    }


def _reviewable_profiles(promotion: Payload, browser_eval: Payload) -> list[Payload]:
    windows = _window_payloads(promotion)
    browser_lookup = _summary_lookup(browser_eval)
    auth_lookup = _auth_profile_lookup(browser_eval)
    profiles: list[Payload] = []
    for index, window in enumerate(windows):
        if not isinstance(window, dict):
            continue
        browser_profile = browser_lookup.get(index)
        if not isinstance(browser_profile, dict):
            continue
        auth_profile = auth_lookup.get(index)
        profiles.append(_window_retention_profile(index + 1, window, browser_profile, auth_profile if isinstance(auth_profile, dict) else None))
    return profiles


def _unique(values: list[str | None]) -> list[str]:
    return list(dict.fromkeys([value for value in values if isinstance(value, str) and value]))


def _retention_scorecard(window_profiles: list[Payload], browser_eval: Payload) -> list[Payload]:
    browser_state = str(browser_eval.get('browser_envelope_readiness') or '')
    temporary_modes = [item.get('temporary_chat_mode') for item in window_profiles if item.get('temporary_chat_mode')]
    history_modes = [item.get('history_retention_mode') for item in window_profiles if item.get('history_retention_mode')]
    memory_modes = [item.get('memory_mode') for item in window_profiles if item.get('memory_mode')]
    context_modes = [item.get('context_persistence_mode') for item in window_profiles if item.get('context_persistence_mode')]
    signed_in = [item for item in window_profiles if item.get('auth_posture') == 'logged-in']
    temporary_windows = [item for item in window_profiles if item.get('temporary_chat_mode') == 'temporary']
    logged_out = [item for item in window_profiles if item.get('auth_posture') == 'logged-out']
    return [
        {
            'check_key': 'browser_envelope_ready',
            'required': True,
            'present': browser_state in {'experimental-browser-envelope', 'provisional-browser-envelope'},
            'detail': 'the retention envelope should only narrow a browser/auth/profile-bound proof story, not replace the earlier gates',
            'browser_envelope_readiness': browser_state,
        },
        {
            'check_key': 'temporary_chat_mode_explicit',
            'required': True,
            'present': bool(window_profiles) and len(temporary_modes) == len(window_profiles),
            'detail': 'each reviewable proof window should preserve whether it used Temporary Chat or a standard conversation lane',
            'temporary_chat_modes': temporary_modes,
        },
        {
            'check_key': 'history_retention_mode_explicit',
            'required': True,
            'present': bool(window_profiles) and len(history_modes) == len(window_profiles),
            'detail': 'each reviewable proof window should preserve whether the conversation was saved, temporary/no-history, or guest-no-saved-history',
            'history_retention_modes': history_modes,
        },
        {
            'check_key': 'memory_mode_explicit_when_signed_in',
            'required': bool(signed_in),
            'present': not signed_in or len(memory_modes) == len(window_profiles),
            'detail': 'signed-in proof should preserve whether memory/reference-chat-history was on, off, or bypassed by Temporary Chat',
            'memory_modes': memory_modes,
        },
        {
            'check_key': 'context_persistence_mode_explicit_when_signed_in',
            'required': bool(signed_in),
            'present': not signed_in or len(context_modes) == len(window_profiles),
            'detail': 'signed-in proof should preserve whether authentication came from a fresh context, manual login, or reused storage state',
            'context_persistence_modes': context_modes,
        },
        {
            'check_key': 'single_retention_envelope',
            'required': True,
            'present': bool(window_profiles)
            and len(set(temporary_modes)) <= 1
            and len(set(history_modes)) <= 1
            and len(set(memory_modes or ['unavailable'])) <= 1,
            'detail': 'one retention promotion should not silently mix saved-history, temporary-chat, and guest-no-history stories',
            'temporary_chat_modes': temporary_modes,
            'history_retention_modes': history_modes,
            'memory_modes': memory_modes,
        },
        {
            'check_key': 'temporary_no_history_boundary_preserved',
            'required': bool(temporary_windows),
            'present': not temporary_windows or all(item.get('history_retention_mode') == 'ephemeral-no-history' and item.get('memory_mode') == 'temporary-no-memory' for item in temporary_windows),
            'detail': 'temporary-chat proof should preserve its no-history and no-memory boundary instead of borrowing standard-chat behaviors',
        },
        {
            'check_key': 'guest_history_boundary_preserved',
            'required': bool(logged_out),
            'present': not logged_out or all(item.get('history_retention_mode') == 'guest-no-saved-history' for item in logged_out),
            'detail': 'logged-out proof should preserve the guest no-saved-history boundary instead of borrowing signed-in history semantics',
        },
    ]


def _retention_envelope(window_profiles: list[Payload], *, max_tier: str, caution_flags: list[str]) -> Payload:
    return {
        'max_support_tier': max_tier,
        'history_retention_scope': _unique([item.get('history_retention_mode') for item in window_profiles]),
        'temporary_chat_scope': _unique([item.get('temporary_chat_mode') for item in window_profiles]),
        'memory_mode_scope': _unique([item.get('memory_mode') for item in window_profiles]),
        'context_persistence_scope': _unique([item.get('context_persistence_mode') for item in window_profiles]),
        'window_count': len(window_profiles),
        'retention_signatures': _unique([item.get('retention_signature') for item in window_profiles]),
        'caution_flags': caution_flags,
    }


def evaluate_chatgpt_retention_envelope_receipt(promotion: Payload, *, root: Path = ROOT) -> Payload:
    spec = build_chatgpt_retention_envelope_receipt(root=root)
    browser_eval = evaluate_chatgpt_browser_envelope_receipt(promotion, root=root)
    profiles = _reviewable_profiles(promotion, browser_eval)
    scorecard = _retention_scorecard(profiles, browser_eval)
    present_checks = [item['check_key'] for item in scorecard if item.get('present')]
    missing_required = [item['check_key'] for item in scorecard if item.get('required') and not item.get('present')]
    missing_optional = [item['check_key'] for item in scorecard if not item.get('required') and not item.get('present')]
    caution_flags: list[str] = []
    if 'context_persistence_mode_explicit_when_signed_in' in missing_optional:
        caution_flags.append('missing-context-persistence-notes')

    if any(len(_unique([profile.get(key) for profile in profiles])) > 1 for key in ('temporary_chat_mode', 'history_retention_mode', 'memory_mode', 'context_persistence_mode')):
        readiness = 'stop'
        reason = 'the supplied proof windows mix incompatible history, temporary-chat, memory, or context-persistence stories and should be split into separate retention evidence lanes'
        tier = 'investigated'
        next_action = 'split the proof windows by conversation retention mode before phrasing support language'
    elif not profiles:
        if browser_eval.get('browser_envelope_readiness') == 'planning-only':
            readiness = 'planning-only'
            reason = 'no reviewable proof windows are attached yet, so the receipt still describes conversation-retention discipline rather than live evidence'
            tier = 'investigated'
            next_action = 'capture at least one reviewable ChatGPT proof window with explicit retention cues'
        else:
            readiness = 'investigated-only'
            reason = 'upstream proof planning exists, but there is still no reviewable conversation-retention-scoped ChatGPT proof window'
            tier = str(browser_eval.get('recommended_support_record_tier') or 'investigated')
            next_action = 'capture a reviewable ChatGPT proof window with explicit temporary/history/memory cues'
    elif missing_required:
        readiness = 'hold-for-retention-clarification'
        reason = 'proof exists, but the temporary-chat, history-retention, memory, or context-persistence envelope is still too fuzzy to phrase honestly'
        tier = str(browser_eval.get('recommended_support_record_tier') or 'experimental')
        next_action = 'preserve one explicit retention profile per proof window before widening support language around history, memory, or persistence semantics'
    else:
        upstream_tier = str(browser_eval.get('recommended_support_record_tier') or 'experimental')
        if len(profiles) >= 2 and upstream_tier == 'provisional':
            readiness = 'provisional-retention-envelope'
            reason = 'repeated proof windows stay on one coherent temporary/history/memory/context story, so the support story can stay provisionally retention-bound'
            tier = 'provisional'
            next_action = 'keep support wording bound to this conversation-retention envelope until separate standard, temporary, or storage-state proof exists'
        else:
            readiness = 'experimental-retention-envelope'
            reason = 'one reviewable retention-scoped proof window exists, but repeated proof or stronger upstream scope is still limited'
            tier = 'experimental'
            next_action = 'repeat the same route-first proof on a second window of the same retention envelope before strengthening support language'

    return {
        'project': 'GlassTTY',
        'surface_key': 'chatgpt',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'retention_envelope_evaluation_kind': 'chatgpt-routefirst-retention-envelope',
        'browser_envelope_evaluation': browser_eval,
        'window_retention_profiles': profiles,
        'field_scorecard': scorecard,
        'present_check_keys': present_checks,
        'missing_required_check_keys': missing_required,
        'missing_optional_check_keys': missing_optional,
        'retention_envelope_readiness': readiness,
        'retention_envelope_readiness_reason': reason,
        'recommended_support_record_tier': tier,
        'caution_flags': caution_flags,
        'retention_envelope': _retention_envelope(profiles, max_tier=tier, caution_flags=caution_flags),
        'recommended_next_action': next_action,
        'source_keys': spec.get('source_keys') or [],
    }


def _summary_markdown(payload: Payload) -> str:
    lines = [
        '# ChatGPT retention envelope receipt',
        '',
        f"- generated_at: `{payload.get('generated_at')}`",
        f"- target support tier: `{payload.get('target_support_tier')}`",
        '',
        '## Retention envelope axes',
        '',
    ]
    for item in payload.get('retention_envelope_axes') or []:
        lines.append(f"- {item.get('axis')}: {item.get('rule')}")
    lines.extend(['', '## Retention envelope readiness states', ''])
    for item in payload.get('retention_envelope_readiness_states') or []:
        lines.append(f"- {item.get('state')}: {item.get('rule')}")
    lines.append('')
    return '\n'.join(lines)


def build_chatgpt_retention_envelope_receipt(*, root: Path = ROOT) -> Payload:
    browser_spec = build_chatgpt_browser_envelope_receipt(root=root)
    payload = {
        'project': 'GlassTTY',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'surface_key': 'chatgpt',
        'purpose': 'bound the strongest honest ChatGPT conversation-retention envelope so repeated route-first proof does not silently mix standard saved-history chats, Temporary Chats, memory-off runs, or reused storage-state sessions',
        'target_support_tier': 'provisional',
        'design_principles': [
            'Standard saved-history chats, Temporary Chats, and guest/no-saved-history sessions should stay distinct support envelopes because their persistence and memory semantics differ materially.',
            'Signed-in proof should preserve whether memory/reference-chat-history was on, off, or bypassed by Temporary Chat before that evidence is used in support wording.',
            'Playwright context persistence matters for honest session claims: a fresh context, manual live login, and reused storage state should remain visible instead of collapsing into a generic signed-in story.',
        ],
        'retention_envelope_axes': [
            {'axis': 'conversation-mode', 'rule': 'standard chats and Temporary Chats should remain distinct support envelopes'},
            {'axis': 'history-retention', 'rule': 'saved-history, temporary/no-history, and guest-no-saved-history behavior should stay explicit instead of being inferred loosely'},
            {'axis': 'memory-mode', 'rule': 'memory-on, memory-off, temporary-no-memory, and unavailable states should remain visible in the evidence story'},
            {'axis': 'context-persistence', 'rule': 'fresh contexts, manual live logins, and reused storage-state sessions should remain distinct support envelopes when signed-in proof is reviewed'},
        ],
        'retention_envelope_readiness_states': [
            {'state': 'provisional-retention-envelope', 'rule': 'repeated proof windows justify only a provisional conversation-retention-bound support envelope'},
            {'state': 'experimental-retention-envelope', 'rule': 'current evidence can justify only an experimental conversation-retention-bound support envelope'},
            {'state': 'hold-for-retention-clarification', 'rule': 'proof exists, but the temporary-chat, history-retention, memory, or context-persistence envelope is still too fuzzy to phrase honestly'},
            {'state': 'investigated-only', 'rule': 'planning or thin proof artifacts exist, but they do not yet justify a live conversation-retention envelope'},
            {'state': 'planning-only', 'rule': 'the receipt still describes conversation-retention discipline rather than current live evidence'},
            {'state': 'stop', 'rule': 'the supplied proof windows mix incompatible conversation-retention stories and should be split into separate evidence lanes'},
        ],
        'commands': {
            'report': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
            'capture_history': HISTORY_COMMAND,
            'write_root': WRITE_ROOT_COMMAND,
            'evaluate': EVALUATE_COMMAND,
            'browser_envelope_receipt': 'python scripts/chatgpt-browser-envelope-receipt.py --pretty',
        },
        'source_keys': sorted(dict.fromkeys((browser_spec.get('source_keys') or []) + [
            'chatgpt-temporary-chat-faq',
            'chatgpt-memory-faq',
            'chatgpt-chat-file-retention',
            'playwright-authentication',
            'playwright-browsercontext',
        ])),
    }
    payload['summary_markdown'] = _summary_markdown(payload)
    return payload


def capture_chatgpt_retention_envelope_receipt(*, root: Path = ROOT, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH) -> Payload:
    payload = build_chatgpt_retention_envelope_receipt(root=root)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / 'chatgpt-retention-envelope-receipt.json'
    summary_path = output_dir / 'SUMMARY.md'
    _write_json(json_path, payload)
    summary_path.write_text(payload.get('summary_markdown', ''), encoding='utf-8')
    entries = _history_entries(history_path)
    previous = entries[-1] if entries else None
    current = {
        'captured_at': payload.get('generated_at'),
        'path': str(json_path),
        'summary_path': str(summary_path),
        'surface_key': payload.get('surface_key'),
        'source_key_count': len(payload.get('source_keys') or []),
        'readiness_state_count': len(payload.get('retention_envelope_readiness_states') or []),
    }
    current['changed_fields'] = _changed_fields(previous, current)
    entries.append(current)
    _write_json(history_path, _history_payload(entries))
    return {'receipt': payload, 'history_update': {'path': str(history_path), 'capture_count_after_write': len(entries), 'changed_fields_vs_previous': current['changed_fields']}}


def write_root_chatgpt_retention_envelope_receipt(*, root: Path = ROOT) -> Payload:
    payload = build_chatgpt_retention_envelope_receipt(root=root)
    _write_json(root / ROOT_OUTPUT_PATH.name, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Build or evaluate the ChatGPT retention envelope receipt.')
    parser.add_argument('--pretty', action='store_true')
    subparsers = parser.add_subparsers(dest='command')
    capture_parser = subparsers.add_parser('capture')
    capture_parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    capture_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    history_parser = subparsers.add_parser('history')
    history_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    history_parser.add_argument('--pretty', action='store_true')
    subparsers.add_parser('write-root')
    evaluate_parser = subparsers.add_parser('evaluate')
    evaluate_parser.add_argument('--promotion', required=True)
    evaluate_parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()

    if args.command == 'capture':
        payload = capture_chatgpt_retention_envelope_receipt(root=ROOT, output_dir=Path(args.output_dir), history_path=Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'history':
        payload = summarize_capture_history(Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'write-root':
        payload = write_root_chatgpt_retention_envelope_receipt(root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'evaluate':
        promotion = _read_json(Path(args.promotion))
        payload = evaluate_chatgpt_retention_envelope_receipt(promotion, root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return

    print(json.dumps(build_chatgpt_retention_envelope_receipt(root=ROOT), indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()
