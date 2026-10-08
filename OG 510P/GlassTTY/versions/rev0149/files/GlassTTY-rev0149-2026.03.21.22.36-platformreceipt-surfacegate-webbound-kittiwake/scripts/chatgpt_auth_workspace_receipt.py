#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from chatgpt_capability_profile_receipt import build_chatgpt_capability_profile_receipt, evaluate_chatgpt_capability_profile_receipt
except ModuleNotFoundError:  # pragma: no cover - import path differs under tests
    import importlib.util

    def _load(name: str, filename: str):
        path = Path(__file__).resolve().parent / filename
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    _CAPABILITY = _load('chatgpt_capability_profile_receipt', 'chatgpt_capability_profile_receipt.py')
    build_chatgpt_capability_profile_receipt = _CAPABILITY.build_chatgpt_capability_profile_receipt
    evaluate_chatgpt_capability_profile_receipt = _CAPABILITY.evaluate_chatgpt_capability_profile_receipt

ROOT = Path(__file__).resolve().parent.parent
ROOT_OUTPUT_PATH = ROOT / 'CHATGPT-AUTH-WORKSPACE-RECEIPT.json'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-auth-workspace-receipt'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'chatgpt-auth-workspace-receipt-captures.json'
REPORT_COMMAND = 'python scripts/chatgpt-auth-workspace-receipt.py --pretty'
CAPTURE_COMMAND = 'python scripts/chatgpt-auth-workspace-receipt.py capture --output-dir validation/latest/chatgpt-auth-workspace-receipt'
HISTORY_COMMAND = 'python scripts/chatgpt-auth-workspace-receipt.py history --pretty'
WRITE_ROOT_COMMAND = 'python scripts/chatgpt-auth-workspace-receipt.py write-root'
EVALUATE_COMMAND = 'python scripts/chatgpt-auth-workspace-receipt.py evaluate --promotion path/to/promotion-window.json --pretty'

Payload = dict[str, Any]
WORKSPACE_ALIASES = {
    'guest': 'guest',
    'logged-out': 'guest',
    'signed-out': 'guest',
    'anonymous': 'guest',
    'personal': 'personal',
    'personal-workspace': 'personal',
    'personal-account': 'personal',
    'business': 'business',
    'chatgpt-business': 'business',
    'team': 'business',
    'chatgpt-team': 'business',
    'business-workspace': 'business',
    'enterprise': 'enterprise',
    'enterprise-workspace': 'enterprise',
    'edu': 'edu',
    'education': 'edu',
    'edu-workspace': 'edu',
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


def _reviewable_summaries(capability_eval: Payload) -> list[Payload]:
    claim_eval = capability_eval.get('claim_evaluation') if isinstance(capability_eval.get('claim_evaluation'), dict) else {}
    promotion_eval = claim_eval.get('promotion_evaluation') if isinstance(claim_eval.get('promotion_evaluation'), dict) else {}
    raw = promotion_eval.get('window_summaries')
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict) and item.get('bundle_readiness') in {'ready-for-held', 'ready-with-caution'}]


def _summary_lookup(capability_eval: Payload) -> dict[int, Payload]:
    by_index: dict[int, Payload] = {}
    for item in _reviewable_summaries(capability_eval):
        idx = item.get('window_index')
        if isinstance(idx, int):
            by_index[idx - 1] = item
    return by_index


def _artifact_rows(window: Payload) -> list[Payload]:
    rows: list[Payload] = []
    for key in ('artifact_refs', 'artifacts', 'bundle_artifacts'):
        raw = window.get(key)
        if isinstance(raw, list):
            for item in raw:
                if isinstance(item, dict):
                    rows.append(item)
    return rows


def _artifact_hints(rows: list[Payload]) -> list[str]:
    hints: list[str] = []
    for row in rows:
        for field in ('kind', 'path', 'role'):
            value = row.get(field)
            if isinstance(value, str) and value.strip():
                hints.append(value.strip())
    return hints


def _auth_posture(window: Payload, summary: Payload | None) -> str | None:
    if summary:
        value = _normalize_keyish(summary.get('auth_posture'))
        if value:
            return value
    for key in ('auth_posture', 'login_state', 'session_auth_posture'):
        value = _normalize_keyish(window.get(key))
        if value:
            return value
    route = window.get('route_witness') if isinstance(window.get('route_witness'), dict) else {}
    for key in ('auth_posture', 'login_state'):
        value = _normalize_keyish(route.get(key))
        if value:
            return value
    return None


def _workspace_kind_from_text(strings: list[str]) -> str | None:
    normalized = [_normalize_text(item) or '' for item in strings]
    joined = ' '.join(normalized)
    if 'enterprise workspace' in joined or 'chatgpt enterprise' in joined:
        return 'enterprise'
    if 'business workspace' in joined or 'chatgpt business' in joined or 'team workspace' in joined or 'chatgpt team' in joined:
        return 'business'
    if 'personal workspace' in joined:
        return 'personal'
    return None


def _workspace_kind(window: Payload, summary: Payload | None) -> str | None:
    auth = _auth_posture(window, summary)
    for source in [window, window.get('route_witness') if isinstance(window.get('route_witness'), dict) else {}]:
        if not isinstance(source, dict):
            continue
        for key in ('workspace_kind', 'workspace_scope', 'workspace_type', 'account_workspace_kind', 'account_scope'):
            value = _normalize_keyish(source.get(key))
            if value and value in WORKSPACE_ALIASES:
                return WORKSPACE_ALIASES[value]
    if auth == 'logged-out':
        return 'guest'
    strings: list[str] = []
    for key in ('workspace_label', 'workspace_name', 'account_label', 'title', 'page_title', 'route_title'):
        strings.extend(_collect_strings(window.get(key)))
    route = window.get('route_witness') if isinstance(window.get('route_witness'), dict) else {}
    for key in ('title', 'page_title'):
        strings.extend(_collect_strings(route.get(key)))
    for key in ('visible_text', 'main_region_text', 'surface_identity_text', 'workspace_labels'):
        strings.extend(_collect_strings(route.get(key)))
        strings.extend(_collect_strings(window.get(key)))
    strings.extend(_artifact_hints(_artifact_rows(window)))
    return _workspace_kind_from_text(strings)


def _history_mode(window: Payload, summary: Payload | None, *, auth_posture: str | None) -> str | None:
    for source in [window, window.get('route_witness') if isinstance(window.get('route_witness'), dict) else {}]:
        if not isinstance(source, dict):
            continue
        for key in ('history_mode', 'history_availability', 'chat_history_mode'):
            value = _normalize_keyish(source.get(key))
            if value:
                return value
    posture_key = _normalize_keyish((summary or {}).get('matched_posture_key'))
    if auth_posture == 'logged-out' or posture_key == 'guest-home-single-thread':
        return 'ephemeral-no-saved-history'
    strings: list[str] = []
    route = window.get('route_witness') if isinstance(window.get('route_witness'), dict) else {}
    for key in ('visible_text', 'main_region_text', 'surface_identity_text', 'workspace_labels'):
        strings.extend(_collect_strings(route.get(key)))
        strings.extend(_collect_strings(window.get(key)))
    strings.extend(_artifact_hints(_artifact_rows(window)))
    normalized = ' '.join((_normalize_text(item) or '') for item in strings)
    if 'search magnifying glass in the left sidebar' in normalized or 'history search' in normalized or 'sidebar search' in normalized:
        return 'saved-history-available'
    return None


def _workspace_switcher_visible(window: Payload, summary: Payload | None) -> bool | None:
    for source in [window, window.get('route_witness') if isinstance(window.get('route_witness'), dict) else {}]:
        if not isinstance(source, dict):
            continue
        for key in ('workspace_switcher_visible', 'multiple_workspaces_visible', 'can_switch_workspaces'):
            value = source.get(key)
            if isinstance(value, bool):
                return value
    strings: list[str] = []
    for key in ('workspace_label', 'workspace_name', 'account_label', 'visible_text', 'surface_identity_text', 'workspace_labels'):
        strings.extend(_collect_strings(window.get(key)))
    route = window.get('route_witness') if isinstance(window.get('route_witness'), dict) else {}
    for key in ('visible_text', 'main_region_text', 'surface_identity_text', 'workspace_labels'):
        strings.extend(_collect_strings(route.get(key)))
    strings.extend(_artifact_hints(_artifact_rows(window)))
    normalized = ' '.join((_normalize_text(item) or '') for item in strings)
    if any(token in normalized for token in ('switch workspace', 'switch workspaces', 'personal workspace', 'business workspace', 'enterprise workspace')):
        return True
    return None


def _window_auth_profile(index: int, window: Payload, summary: Payload | None) -> Payload:
    auth = _auth_posture(window, summary)
    workspace = _workspace_kind(window, summary)
    history_mode = _history_mode(window, summary, auth_posture=auth)
    switcher = _workspace_switcher_visible(window, summary)
    return {
        'window_index': index,
        'proof_window_token': (summary or {}).get('proof_window_token'),
        'bundle_readiness': (summary or {}).get('bundle_readiness'),
        'auth_posture': auth,
        'workspace_kind': workspace,
        'history_mode': history_mode,
        'workspace_switcher_visible': switcher,
        'route_path': (summary or {}).get('route_path'),
        'matched_posture_key': (summary or {}).get('matched_posture_key'),
    }


def _auth_scorecard(window_profiles: list[Payload], capability_eval: Payload) -> list[Payload]:
    capability_state = str(capability_eval.get('capability_readiness') or '')
    auths = [item.get('auth_posture') for item in window_profiles if item.get('auth_posture')]
    workspaces = [item.get('workspace_kind') for item in window_profiles if item.get('workspace_kind')]
    logged_out_windows = [item for item in window_profiles if item.get('auth_posture') == 'logged-out']
    logged_in_windows = [item for item in window_profiles if item.get('auth_posture') == 'logged-in']
    return [
        {
            'check_key': 'capability_envelope_ready',
            'required': True,
            'present': capability_state in {'experimental-text-profile', 'provisional-text-profile'},
            'detail': 'the auth/workspace envelope should only narrow a text-only lane-bound capability story, not replace the route/tool/profile gates',
            'capability_readiness': capability_state,
        },
        {
            'check_key': 'auth_posture_explicit',
            'required': True,
            'present': bool(window_profiles) and len(auths) == len(window_profiles),
            'detail': 'each reviewable proof window should preserve whether the user was logged out or logged in',
            'auth_postures': auths,
        },
        {
            'check_key': 'workspace_kind_explicit',
            'required': True,
            'present': bool(window_profiles) and len(workspaces) == len(window_profiles),
            'detail': 'each reviewable proof window should preserve whether the envelope is guest, personal, business, enterprise, or edu instead of assuming one from sparse cues',
            'workspace_kinds': workspaces,
        },
        {
            'check_key': 'single_auth_posture_envelope',
            'required': True,
            'present': bool(window_profiles) and len(set(auths)) == 1,
            'detail': 'one promotion-ready auth envelope should not silently mix guest and signed-in proof windows',
            'auth_postures': auths,
        },
        {
            'check_key': 'single_workspace_kind_envelope',
            'required': True,
            'present': bool(window_profiles) and len(set(workspaces)) == 1,
            'detail': 'one promotion-ready auth envelope should stay bound to one workspace kind instead of mixing personal, business, or enterprise evidence',
            'workspace_kinds': workspaces,
        },
        {
            'check_key': 'logged_out_history_boundary_preserved',
            'required': bool(logged_out_windows),
            'present': bool(logged_out_windows) and all(item.get('history_mode') == 'ephemeral-no-saved-history' for item in logged_out_windows),
            'detail': 'logged-out proof should keep the one-conversation, no-saved-history boundary explicit rather than borrowing signed-in history behaviors',
            'history_modes': [item.get('history_mode') for item in logged_out_windows],
        },
        {
            'check_key': 'workspace_switcher_reviewable_when_logged_in',
            'required': False,
            'present': not logged_in_windows or any(item.get('workspace_switcher_visible') is not None for item in logged_in_windows),
            'detail': 'for signed-in proof, preserving whether a workspace switcher was visible makes later personal-vs-business review more auditable',
        },
    ]


def _scope_summary(window_profiles: list[Payload]) -> Payload:
    return {
        'auth_postures': list(dict.fromkeys(item.get('auth_posture') for item in window_profiles if item.get('auth_posture'))),
        'workspace_kinds': list(dict.fromkeys(item.get('workspace_kind') for item in window_profiles if item.get('workspace_kind'))),
        'history_modes': list(dict.fromkeys(item.get('history_mode') for item in window_profiles if item.get('history_mode'))),
        'route_paths': list(dict.fromkeys(item.get('route_path') for item in window_profiles if item.get('route_path'))),
        'switcher_visibility': [
            {'window_index': item.get('window_index'), 'workspace_switcher_visible': item.get('workspace_switcher_visible')}
            for item in window_profiles if item.get('workspace_switcher_visible') is not None
        ],
    }


def _auth_envelope(scope: Payload, *, max_tier: str, caution_flags: list[str]) -> Payload:
    auth_scope = scope.get('auth_postures') or []
    workspace_scope = scope.get('workspace_kinds') or []
    history_scope = scope.get('history_modes') or []
    routes = ', '.join(scope.get('route_paths') or []) or 'unspecified route path'
    auth_label = ', '.join(auth_scope) or 'unspecified auth posture'
    workspace_label = ', '.join(workspace_scope) or 'unspecified workspace kind'
    supported_claims = [
        f'GlassTTY has evidence only for the {auth_label} ChatGPT route-first envelope on {routes}.',
        f'The current auth/workspace envelope only covers the `{workspace_label}` workspace scope preserved in the reviewable proof windows.',
        'The supported workflow slice remains the plain text-only route/composer/submit/latest-turn baseline, not richer workspace behaviors.',
    ]
    if history_scope:
        supported_claims.append(f'The preserved history boundary is `{", ".join(history_scope)}` and should travel with the support wording.')
    if max_tier == 'provisional':
        supported_claims.append('Repeated proof windows justify a provisional auth/workspace envelope only within that preserved session scope.')
    elif max_tier == 'experimental':
        supported_claims.append('Current evidence can justify only an experimental auth/workspace envelope.')
    else:
        supported_claims.append('Current evidence does not justify a live auth/workspace claim beyond investigated planning artifacts.')
    excluded_claims = [
        'Do not claim that logged-out proof implies signed-in chat history, export, sharing, or workspace features.',
        'Do not claim that personal-workspace proof implies Business, Enterprise, or Edu workspace behavior or admin controls.',
        'Do not combine guest and signed-in proof windows into one promotion-ready session story; split them into separate evidence lanes instead.',
    ]
    if caution_flags:
        excluded_claims.append('Keep caution flags attached so sparse session cues do not broaden the auth/workspace claim.')
    return {
        'tier_ceiling': max_tier,
        'auth_posture_scope': auth_scope,
        'workspace_kind_scope': workspace_scope,
        'history_mode_scope': history_scope,
        'route_scope': scope.get('route_paths') or [],
        'supported_claims': supported_claims,
        'excluded_claims': excluded_claims,
    }


def evaluate_chatgpt_auth_workspace_receipt(promotion: Payload, *, root: Path = ROOT) -> Payload:
    spec = build_chatgpt_auth_workspace_receipt(root=root)
    capability_eval = evaluate_chatgpt_capability_profile_receipt(promotion, root=root)
    windows = _window_payloads(promotion)
    summary_by_index = _summary_lookup(capability_eval)
    window_profiles = [_window_auth_profile(index + 1, window, summary_by_index.get(index)) for index, window in enumerate(windows) if summary_by_index.get(index)]
    scorecard = _auth_scorecard(window_profiles, capability_eval)
    present_checks = [item['check_key'] for item in scorecard if item.get('present')]
    missing_required = [item['check_key'] for item in scorecard if item.get('required') and not item.get('present')]
    missing_optional = [item['check_key'] for item in scorecard if not item.get('required') and not item.get('present')]
    scope = _scope_summary(window_profiles)

    caution_flags: list[str] = list(dict.fromkeys(str(item) for item in (capability_eval.get('caution_flags') or []) if isinstance(item, str)))
    if 'workspace_switcher_reviewable_when_logged_in' in missing_optional:
        caution_flags.append('workspace-switcher-not-captured')

    capability_state = str(capability_eval.get('capability_readiness') or '')
    auth_set = {item.get('auth_posture') for item in window_profiles if item.get('auth_posture')}
    workspace_set = {item.get('workspace_kind') for item in window_profiles if item.get('workspace_kind')}

    recommended_tier = 'investigated'
    if capability_state == 'planning-only':
        readiness = 'planning-only'
        reason = 'the receipt still describes session-boundary discipline and does not yet have reviewable proof windows to narrow'
    elif capability_state == 'investigated-only':
        readiness = 'investigated-only'
        reason = 'some planning or thin proof artifacts exist, but they do not yet justify a live auth/workspace envelope'
    elif len(auth_set) > 1 or len(workspace_set) > 1:
        readiness = 'stop'
        reason = 'the supplied proof windows mix distinct auth or workspace envelopes, so they should be split into separate support lanes instead of promoted together'
    elif missing_required:
        readiness = 'hold-for-auth-clarification'
        reason = 'proof exists, but the auth posture, workspace kind, logged-out history boundary, or upstream text-only capability scope is still too fuzzy to phrase honestly'
    elif len(window_profiles) >= 2:
        readiness = 'provisional-auth-envelope'
        reason = 'repeated plain-text proof windows preserve one explicit auth/workspace envelope strongly enough for provisional lane-bound support wording'
        recommended_tier = 'provisional'
    else:
        readiness = 'experimental-auth-envelope'
        reason = 'the evidence can justify an experimental auth/workspace envelope, but it still needs a second repeated proof window to strengthen the session story'
        recommended_tier = 'experimental'

    if readiness == 'planning-only':
        next_action = 'capture one live route-first ChatGPT proof window before trying to phrase any auth or workspace envelope'
    elif readiness == 'investigated-only':
        next_action = 'repair the upstream route/composer/submit/claim/profile receipts until at least one reviewable text-only proof window exists'
    elif readiness == 'hold-for-auth-clarification':
        next_action = 'preserve explicit login state, workspace kind, and logged-out history boundary details before widening session-scoped support language'
    elif readiness == 'experimental-auth-envelope':
        next_action = 'keep the support wording explicitly guest/personal/workspace-bound and gather the second repeated proof window with the same session envelope'
    elif readiness == 'provisional-auth-envelope':
        next_action = 'promote only to a provisional session-bound envelope and keep guest, personal, business, and enterprise claims explicitly separated'
    else:
        next_action = 'split mixed guest/signed-in or mixed-workspace proof into separate evidence lanes instead of promoting one combined session story'

    envelope = _auth_envelope(scope, max_tier=recommended_tier, caution_flags=caution_flags)
    return {
        'project': 'GlassTTY',
        'surface_key': 'chatgpt',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'auth_workspace_evaluation_kind': 'chatgpt-routefirst-auth-workspace-envelope',
        'capability_evaluation': capability_eval,
        'window_auth_profiles': window_profiles,
        'field_scorecard': scorecard,
        'present_check_keys': present_checks,
        'missing_required_check_keys': missing_required,
        'missing_optional_check_keys': missing_optional,
        'auth_workspace_readiness': readiness,
        'auth_workspace_readiness_reason': reason,
        'recommended_support_record_tier': recommended_tier,
        'caution_flags': caution_flags,
        'auth_workspace_envelope': envelope,
        'recommended_next_action': next_action,
        'source_keys': spec.get('source_keys') or [],
    }


def _summary_markdown(payload: Payload) -> str:
    axes = payload.get('auth_workspace_axes') or []
    states = payload.get('auth_workspace_readiness_states') or []
    lines = [
        '# ChatGPT auth/workspace receipt',
        '',
        f"- generated_at: `{payload.get('generated_at')}`",
        f"- target support tier: `{payload.get('target_support_tier')}`",
        '',
        '## Auth/workspace axes',
        '',
    ]
    for item in axes:
        lines.append(f"- {item.get('axis')}: {item.get('rule')}")
    lines.extend(['', '## Auth/workspace readiness states', ''])
    for item in states:
        lines.append(f"- {item.get('state')}: {item.get('rule')}")
    lines.append('')
    return '\n'.join(lines)


def build_chatgpt_auth_workspace_receipt(*, root: Path = ROOT) -> Payload:
    capability_spec = build_chatgpt_capability_profile_receipt(root=root)
    payload = {
        'project': 'GlassTTY',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'surface_key': 'chatgpt',
        'purpose': 'bound the strongest honest ChatGPT auth/workspace envelope so repeated route-first proof does not silently mix guest, personal, business, enterprise, or edu session stories',
        'target_support_tier': 'provisional',
        'design_principles': [
            'Logged-out proof should stay separate from signed-in proof because history, export, and workspace behaviors differ by session posture.',
            'Signed-in personal proof should not silently imply ChatGPT Business, Enterprise, or Edu workspace behavior or admin-controlled features.',
            'The auth/workspace envelope should describe both what the current evidence covers and what session or workspace stories it explicitly does not cover.',
        ],
        'auth_workspace_axes': [
            {'axis': 'auth-posture', 'rule': 'logged-out and logged-in proof should remain distinct in the support story'},
            {'axis': 'workspace-kind', 'rule': 'guest, personal, business, enterprise, and edu scopes should stay explicit instead of being assumed from sparse cues'},
            {'axis': 'history-boundary', 'rule': 'logged-out one-conversation/no-saved-history behavior should remain distinct from signed-in chat history and search'},
            {'axis': 'workspace-switching', 'rule': 'multi-workspace switching cues should travel with signed-in evidence so personal-vs-business review stays auditable'},
        ],
        'auth_workspace_readiness_states': [
            {'state': 'provisional-auth-envelope', 'rule': 'repeated text-only proof windows justify only a provisional guest-or-workspace-bound session envelope'},
            {'state': 'experimental-auth-envelope', 'rule': 'current evidence can justify only an experimental guest-or-workspace-bound session envelope'},
            {'state': 'hold-for-auth-clarification', 'rule': 'proof exists, but auth posture, workspace kind, or logged-out history limits are still too fuzzy to phrase honestly'},
            {'state': 'investigated-only', 'rule': 'planning or thin proof artifacts exist, but they do not yet justify a live auth/workspace envelope'},
            {'state': 'planning-only', 'rule': 'the receipt still describes session-boundary discipline rather than current live evidence'},
            {'state': 'stop', 'rule': 'the supplied proof windows mix incompatible auth or workspace envelopes and should be split into separate evidence lanes'},
        ],
        'commands': {
            'report': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
            'capture_history': HISTORY_COMMAND,
            'write_root': WRITE_ROOT_COMMAND,
            'evaluate': EVALUATE_COMMAND,
            'capability_profile_receipt': 'python scripts/chatgpt-capability-profile-receipt.py --pretty',
        },
        'source_keys': sorted(dict.fromkeys((capability_spec.get('source_keys') or []) + ['chatgpt-data-controls', 'chatgpt-workspace-access'])),
    }
    payload['summary_markdown'] = _summary_markdown(payload)
    return payload


def capture_chatgpt_auth_workspace_receipt(*, root: Path = ROOT, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH) -> Payload:
    payload = build_chatgpt_auth_workspace_receipt(root=root)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / 'chatgpt-auth-workspace-receipt.json'
    summary_path = output_dir / 'SUMMARY.md'
    _write_json(json_path, payload)
    summary_path.write_text(payload.get('summary_markdown', ''), encoding='utf-8')
    entries = _history_entries(history_path)
    previous = entries[-1] if entries else None
    current = {
        'captured_at': payload.get('generated_at'),
        'path': str(json_path),
        'summary_path': str(summary_path),
        'source_keys': payload.get('source_keys') or [],
        'auth_workspace_readiness_states': [item.get('state') for item in payload.get('auth_workspace_readiness_states') or []],
    }
    changed_fields = _changed_fields(previous, current)
    current['changed_fields'] = changed_fields
    entries.append(current)
    _write_json(history_path, _history_payload(entries))
    return {
        'receipt': payload,
        'output_dir': str(output_dir),
        'json_path': str(json_path),
        'summary_path': str(summary_path),
        'history_update': {
            'history_path': str(history_path),
            'capture_count_after_write': len(entries),
            'changed_fields': changed_fields,
        },
    }


def write_root_chatgpt_auth_workspace_receipt(*, root: Path = ROOT) -> Payload:
    payload = build_chatgpt_auth_workspace_receipt(root=root)
    _write_json(root / ROOT_OUTPUT_PATH.name, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Build or evaluate the ChatGPT auth/workspace receipt.')
    subparsers = parser.add_subparsers(dest='command')
    capture_parser = subparsers.add_parser('capture')
    capture_parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    capture_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    history_parser = subparsers.add_parser('history')
    history_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    subparsers.add_parser('write-root')
    eval_parser = subparsers.add_parser('evaluate')
    eval_parser.add_argument('--promotion', required=True)
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()

    if args.command == 'capture':
        payload = capture_chatgpt_auth_workspace_receipt(output_dir=Path(args.output_dir), history_path=Path(args.history_path))
    elif args.command == 'history':
        payload = summarize_capture_history(Path(args.history_path))
    elif args.command == 'write-root':
        payload = write_root_chatgpt_auth_workspace_receipt()
    elif args.command == 'evaluate':
        payload = evaluate_chatgpt_auth_workspace_receipt(_read_json(Path(args.promotion)))
    else:
        payload = build_chatgpt_auth_workspace_receipt()
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()
