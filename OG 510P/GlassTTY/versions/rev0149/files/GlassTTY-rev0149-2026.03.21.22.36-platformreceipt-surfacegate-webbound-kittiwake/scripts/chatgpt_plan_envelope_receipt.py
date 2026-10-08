#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from chatgpt_auth_workspace_receipt import build_chatgpt_auth_workspace_receipt, evaluate_chatgpt_auth_workspace_receipt
except ModuleNotFoundError:  # pragma: no cover - import path differs under tests
    import importlib.util

    def _load(name: str, filename: str):
        path = Path(__file__).resolve().parent / filename
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    _AUTH = _load('chatgpt_auth_workspace_receipt', 'chatgpt_auth_workspace_receipt.py')
    build_chatgpt_auth_workspace_receipt = _AUTH.build_chatgpt_auth_workspace_receipt
    evaluate_chatgpt_auth_workspace_receipt = _AUTH.evaluate_chatgpt_auth_workspace_receipt

ROOT = Path(__file__).resolve().parent.parent
ROOT_OUTPUT_PATH = ROOT / 'CHATGPT-PLAN-ENVELOPE-RECEIPT.json'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-plan-envelope-receipt'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'chatgpt-plan-envelope-receipt-captures.json'
REPORT_COMMAND = 'python scripts/chatgpt-plan-envelope-receipt.py --pretty'
CAPTURE_COMMAND = 'python scripts/chatgpt-plan-envelope-receipt.py capture --output-dir validation/latest/chatgpt-plan-envelope-receipt'
HISTORY_COMMAND = 'python scripts/chatgpt-plan-envelope-receipt.py history --pretty'
WRITE_ROOT_COMMAND = 'python scripts/chatgpt-plan-envelope-receipt.py write-root'
EVALUATE_COMMAND = 'python scripts/chatgpt-plan-envelope-receipt.py evaluate --promotion path/to/promotion-window.json --pretty'

Payload = dict[str, Any]
PLAN_ALIASES = {
    'guest': 'free-guest',
    'logged-out': 'free-guest',
    'free-guest': 'free-guest',
    'free-tier-guest': 'free-guest',
    'free': 'free',
    'free-tier': 'free',
    'chatgpt-free': 'free',
    'plus': 'plus',
    'chatgpt-plus': 'plus',
    'plus-plan': 'plus',
    'pro': 'pro',
    'chatgpt-pro': 'pro',
    'pro-plan': 'pro',
    'business': 'business',
    'chatgpt-business': 'business',
    'team': 'business',
    'chatgpt-team': 'business',
    'enterprise': 'enterprise',
    'chatgpt-enterprise': 'enterprise',
    'edu': 'edu',
    'chatgpt-edu': 'edu',
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
        return [item.strip() for item in value if isinstance(item, str) and item.strip()]
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


def _summary_lookup(auth_eval: Payload) -> dict[int, Payload]:
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


def _plan_from_strings(strings: list[str]) -> str | None:
    joined = ' '.join((_normalize_text(item) or '') for item in strings)
    if any(token in joined for token in ('chatgpt enterprise', 'enterprise workspace', 'enterprise plan')):
        return 'enterprise'
    if any(token in joined for token in ('chatgpt business', 'business workspace', 'business plan', 'chatgpt team', 'team workspace')):
        return 'business'
    if any(token in joined for token in ('chatgpt edu', 'edu workspace', 'edu plan')):
        return 'edu'
    if any(token in joined for token in ('chatgpt pro', 'pro plan', 'subscription: pro')):
        return 'pro'
    if any(token in joined for token in ('chatgpt plus', 'plus plan', 'subscription: plus')):
        return 'plus'
    if any(token in joined for token in ('chatgpt free', 'free plan', 'subscription: free')):
        return 'free'
    return None


def _explicit_plan(window: Payload) -> str | None:
    route = window.get('route_witness') if isinstance(window.get('route_witness'), dict) else {}
    for source in (window, route):
        if not isinstance(source, dict):
            continue
        for key in ('plan_tier', 'subscription_plan', 'account_plan', 'plan_name', 'plan_type', 'subscription_tier', 'chatgpt_plan'):
            normalized = _normalize_keyish(source.get(key))
            if normalized and normalized in PLAN_ALIASES:
                return PLAN_ALIASES[normalized]
    strings: list[str] = []
    for source in (window, route):
        if not isinstance(source, dict):
            continue
        for key in ('title', 'page_title', 'route_title', 'account_label', 'plan_label', 'workspace_label', 'visible_text', 'main_region_text', 'surface_identity_text'):
            strings.extend(_collect_strings(source.get(key)))
    strings.extend(_artifact_hints(_artifact_rows(window)))
    return _plan_from_strings(strings)


def _infer_plan(window: Payload, auth_profile: Payload | None) -> str | None:
    explicit = _explicit_plan(window)
    if explicit:
        return explicit
    auth_posture = _normalize_keyish((auth_profile or {}).get('auth_posture'))
    workspace_kind = _normalize_keyish((auth_profile or {}).get('workspace_kind'))
    if auth_posture == 'logged-out' or workspace_kind == 'guest':
        return 'free-guest'
    if workspace_kind in {'business', 'enterprise', 'edu'}:
        return workspace_kind
    return None


def _plan_profile(index: int, window: Payload, auth_profile: Payload | None) -> Payload:
    plan_tier = _infer_plan(window, auth_profile)
    return {
        'window_index': index,
        'proof_window_token': (auth_profile or {}).get('proof_window_token'),
        'bundle_readiness': (auth_profile or {}).get('bundle_readiness'),
        'auth_posture': (auth_profile or {}).get('auth_posture'),
        'workspace_kind': (auth_profile or {}).get('workspace_kind'),
        'history_mode': (auth_profile or {}).get('history_mode'),
        'plan_tier': plan_tier,
        'plan_source': 'explicit-or-inferred' if plan_tier else 'missing',
        'route_path': (auth_profile or {}).get('route_path'),
    }


def _scorecard(plan_profiles: list[Payload], auth_eval: Payload) -> list[Payload]:
    auth_state = str(auth_eval.get('auth_workspace_readiness') or '')
    plans = [item.get('plan_tier') for item in plan_profiles if item.get('plan_tier')]
    guests = [item for item in plan_profiles if item.get('auth_posture') == 'logged-out' or item.get('workspace_kind') == 'guest']
    personals = [item for item in plan_profiles if item.get('auth_posture') == 'logged-in' and item.get('workspace_kind') == 'personal']
    workspace_bound = [item for item in plan_profiles if item.get('workspace_kind') in {'business', 'enterprise', 'edu'}]
    return [
        {
            'check_key': 'auth_workspace_envelope_ready',
            'required': True,
            'present': auth_state in {'experimental-auth-envelope', 'provisional-auth-envelope'},
            'detail': 'the plan envelope should only narrow an already reviewable auth/workspace envelope',
            'auth_workspace_readiness': auth_state,
        },
        {
            'check_key': 'reviewable_window_present',
            'required': True,
            'present': bool(plan_profiles),
            'detail': 'a plan envelope should rest on at least one reviewable proof window rather than planning objects alone',
            'actual_count': len(plan_profiles),
        },
        {
            'check_key': 'plan_tier_explicit',
            'required': True,
            'present': bool(plan_profiles) and len(plans) == len(plan_profiles),
            'detail': 'each reviewable proof window should preserve the subscription tier instead of assuming one from sparse cues',
            'plan_tiers': plans,
        },
        {
            'check_key': 'single_plan_envelope',
            'required': True,
            'present': bool(plans) and len(set(plans)) == 1,
            'detail': 'one promotion-ready plan envelope should stay bound to one explicit subscription tier',
            'plan_tiers': plans,
        },
        {
            'check_key': 'guest_plan_boundary_preserved',
            'required': bool(guests),
            'present': not guests or all(item.get('plan_tier') == 'free-guest' for item in guests),
            'detail': 'logged-out proof should stay bound to the guest/free posture instead of borrowing paid-plan semantics',
        },
        {
            'check_key': 'workspace_bound_plan_alignment',
            'required': bool(workspace_bound),
            'present': not workspace_bound or all(item.get('plan_tier') == item.get('workspace_kind') for item in workspace_bound),
            'detail': 'Business, Enterprise, and Edu workspace evidence should keep the corresponding workspace plan explicit rather than drifting into a generic paid tier',
        },
        {
            'check_key': 'signed_in_personal_plan_explicit',
            'required': bool(personals),
            'present': not personals or all(item.get('plan_tier') in {'free', 'plus', 'pro'} for item in personals),
            'detail': 'signed-in personal proof should preserve whether the account is Free, Plus, or Pro before support wording broadens across personal plans',
            'plan_tiers': [item.get('plan_tier') for item in personals],
        },
    ]


def _scope_summary(plan_profiles: list[Payload]) -> Payload:
    return {
        'plan_tiers': list(dict.fromkeys(item.get('plan_tier') for item in plan_profiles if item.get('plan_tier'))),
        'auth_postures': list(dict.fromkeys(item.get('auth_posture') for item in plan_profiles if item.get('auth_posture'))),
        'workspace_kinds': list(dict.fromkeys(item.get('workspace_kind') for item in plan_profiles if item.get('workspace_kind'))),
        'route_paths': list(dict.fromkeys(item.get('route_path') for item in plan_profiles if item.get('route_path'))),
    }


def _plan_envelope(scope: Payload, *, max_tier: str, caution_flags: list[str]) -> Payload:
    plan_scope = scope.get('plan_tiers') or []
    workspace_scope = scope.get('workspace_kinds') or []
    routes = ', '.join(scope.get('route_paths') or []) or 'unspecified route path'
    plan_label = ', '.join(plan_scope) or 'unspecified plan tier'
    workspace_label = ', '.join(workspace_scope) or 'unspecified workspace scope'
    supported_claims = [
        f'GlassTTY has evidence only for the `{plan_label}` ChatGPT plan envelope on {routes}.',
        f'The current support wording only covers the `{workspace_label}` workspace/account scope preserved in the reviewable proof windows.',
        'The supported workflow slice remains the plain route/composer/submit/latest-turn baseline, not plan-specific tools or higher-tier capabilities beyond what the envelope names.',
    ]
    if max_tier == 'provisional':
        supported_claims.append('Repeated proof windows justify only a provisional subscription-bound envelope inside that named plan tier.')
    elif max_tier == 'experimental':
        supported_claims.append('Current evidence can justify only an experimental subscription-bound envelope.')
    else:
        supported_claims.append('Current evidence does not justify a live subscription-plan claim beyond investigated planning artifacts.')
    excluded_claims = [
        'Do not let guest or Free evidence silently imply Plus, Pro, Business, Enterprise, or Edu tool or limit coverage.',
        'Do not let Plus or Pro personal-account evidence silently imply Business, Enterprise, or Edu workspace semantics or admin-controlled features.',
        'Do not merge multiple subscription tiers into one promotion-ready plan story; split them into separate evidence lanes instead.',
    ]
    if caution_flags:
        excluded_claims.append('Keep caution flags attached so thin account-menu or billing cues do not broaden the subscription claim.')
    return {
        'tier_ceiling': max_tier,
        'plan_tier_scope': plan_scope,
        'auth_posture_scope': scope.get('auth_postures') or [],
        'workspace_kind_scope': workspace_scope,
        'route_scope': scope.get('route_paths') or [],
        'supported_claims': supported_claims,
        'excluded_claims': excluded_claims,
    }


def evaluate_chatgpt_plan_envelope_receipt(promotion: Payload, *, root: Path = ROOT) -> Payload:
    spec = build_chatgpt_plan_envelope_receipt(root=root)
    auth_eval = evaluate_chatgpt_auth_workspace_receipt(promotion, root=root)
    windows = _window_payloads(promotion)
    summary_by_index = _summary_lookup(auth_eval)
    plan_profiles = [_plan_profile(index + 1, window, summary_by_index.get(index)) for index, window in enumerate(windows) if summary_by_index.get(index)]
    scorecard = _scorecard(plan_profiles, auth_eval)
    present_checks = [item['check_key'] for item in scorecard if item.get('present')]
    missing_required = [item['check_key'] for item in scorecard if item.get('required') and not item.get('present')]
    missing_optional = [item['check_key'] for item in scorecard if not item.get('required') and not item.get('present')]
    scope = _scope_summary(plan_profiles)
    caution_flags: list[str] = []
    if 'signed_in_personal_plan_explicit' in missing_required:
        caution_flags.append('personal-plan-unspecified')
    if 'guest_plan_boundary_preserved' in missing_required:
        caution_flags.append('guest-plan-mismatch')
    if scope.get('plan_tiers') == ['free']:
        caution_flags.append('free-plan-limits-may-differ')
    stop = False
    if len(scope.get('plan_tiers') or []) > 1:
        stop = True
    if any(item.get('workspace_kind') == 'guest' and item.get('plan_tier') != 'free-guest' for item in plan_profiles):
        stop = True
    if any(item.get('workspace_kind') in {'business', 'enterprise', 'edu'} and item.get('plan_tier') != item.get('workspace_kind') for item in plan_profiles):
        stop = True

    auth_state = str(auth_eval.get('auth_workspace_readiness') or '')
    tier = 'investigated'
    readiness = 'planning-only'
    next_action = 'capture a reviewable ChatGPT proof window first, then preserve account or workspace plan cues before widening support wording across subscription tiers'
    if not plan_profiles and auth_state not in {'experimental-auth-envelope', 'provisional-auth-envelope'}:
        readiness = 'planning-only'
    elif stop:
        readiness = 'stop'
        next_action = 'split the supplied proof windows by subscription tier or workspace plan before reusing them for one support claim'
    elif missing_required:
        readiness = 'hold-for-plan-clarification'
        next_action = 'preserve explicit plan or billing cues for each proof window before widening support language across Free, Plus, Pro, Business, Enterprise, or Edu tiers'
    elif auth_state == 'provisional-auth-envelope' and plan_profiles:
        readiness = 'provisional-plan-envelope'
        tier = 'provisional'
        next_action = 'keep the current support wording subscription-bound and capture a separate lane before claiming any other plan tier'
    elif auth_state == 'experimental-auth-envelope' and plan_profiles:
        readiness = 'experimental-plan-envelope'
        tier = 'experimental'
        next_action = 'repeat the same plan-bound proof window on a second distinct capture before considering provisional wording'
    elif plan_profiles:
        readiness = 'investigated-only'
        next_action = 'keep the subscription story investigated-only until the upstream auth/workspace envelope is reviewable'

    return {
        'project': spec.get('project'),
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'surface_key': spec.get('surface_key'),
        'target_support_tier': spec.get('target_support_tier'),
        'auth_workspace_readiness': auth_state,
        'auth_workspace_evaluation': auth_eval,
        'window_plan_profiles': plan_profiles,
        'field_scorecard': scorecard,
        'present_check_keys': present_checks,
        'missing_required_check_keys': missing_required,
        'missing_optional_check_keys': missing_optional,
        'plan_envelope_readiness': readiness,
        'recommended_support_record_tier': tier,
        'caution_flags': caution_flags,
        'plan_envelope': _plan_envelope(scope, max_tier=tier, caution_flags=caution_flags),
        'recommended_next_action': next_action,
        'source_keys': spec.get('source_keys') or [],
    }


def _summary_markdown(payload: Payload) -> str:
    lines = [
        '# ChatGPT plan envelope receipt',
        '',
        f"- generated_at: `{payload.get('generated_at')}`",
        f"- target support tier: `{payload.get('target_support_tier')}`",
        '',
        '## Plan envelope axes',
        '',
    ]
    for item in payload.get('plan_envelope_axes') or []:
        lines.append(f"- {item.get('axis')}: {item.get('rule')}")
    lines.extend(['', '## Plan envelope readiness states', ''])
    for item in payload.get('plan_envelope_readiness_states') or []:
        lines.append(f"- {item.get('state')}: {item.get('rule')}")
    lines.append('')
    return '\n'.join(lines)


def build_chatgpt_plan_envelope_receipt(*, root: Path = ROOT) -> Payload:
    auth_spec = build_chatgpt_auth_workspace_receipt(root=root)
    payload = {
        'project': 'GlassTTY',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'surface_key': 'chatgpt',
        'purpose': 'bound the strongest honest ChatGPT subscription-plan envelope so repeated route-first proof does not silently mix guest, Free, Plus, Pro, Business, Enterprise, or Edu plan stories',
        'target_support_tier': 'provisional',
        'design_principles': [
            'Guest, Free, Plus, Pro, Business, Enterprise, and Edu evidence should remain distinct plan envelopes because available tools, limits, and workspace semantics vary by plan.',
            'Signed-in personal proof should preserve whether the account is Free, Plus, or Pro instead of collapsing all personal-account evidence into one generic paid tier.',
            'Workspace-bound proof should keep Business, Enterprise, and Edu plan semantics explicit rather than borrowing personal-account or guest assumptions.',
        ],
        'plan_envelope_axes': [
            {'axis': 'account-tier', 'rule': 'guest, Free, Plus, and Pro personal-account evidence should remain distinct support envelopes'},
            {'axis': 'workspace-plan', 'rule': 'Business, Enterprise, and Edu workspace evidence should remain explicit instead of collapsing into a generic paid tier'},
            {'axis': 'tool-limit-story', 'rule': 'plan-varying tools or limits should stay outside the support wording unless the plan envelope names them explicitly'},
        ],
        'plan_envelope_readiness_states': [
            {'state': 'provisional-plan-envelope', 'rule': 'repeated proof windows justify only a provisional subscription-bound support envelope'},
            {'state': 'experimental-plan-envelope', 'rule': 'current evidence can justify only an experimental subscription-bound support envelope'},
            {'state': 'hold-for-plan-clarification', 'rule': 'proof exists, but the subscription tier is still too fuzzy to phrase honestly'},
            {'state': 'investigated-only', 'rule': 'planning or thin proof artifacts exist, but they do not yet justify a live subscription-plan envelope'},
            {'state': 'planning-only', 'rule': 'the receipt still describes subscription-boundary discipline rather than current live evidence'},
            {'state': 'stop', 'rule': 'the supplied proof windows mix incompatible subscription tiers and should be split into separate evidence lanes'},
        ],
        'commands': {
            'report': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
            'capture_history': HISTORY_COMMAND,
            'write_root': WRITE_ROOT_COMMAND,
            'evaluate': EVALUATE_COMMAND,
            'auth_workspace_receipt': 'python scripts/chatgpt-auth-workspace-receipt.py --pretty',
        },
        'source_keys': sorted(dict.fromkeys((auth_spec.get('source_keys') or []) + [
            'chatgpt-what-is-faq',
            'chatgpt-plus-plan',
            'chatgpt-pro-plan',
            'chatgpt-business-plan',
            'chatgpt-enterprise-plan',
            'chatgpt-apps-in-chatgpt',
            'playwright-authentication',
        ])),
    }
    payload['summary_markdown'] = _summary_markdown(payload)
    return payload


def capture_chatgpt_plan_envelope_receipt(*, root: Path = ROOT, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH) -> Payload:
    payload = build_chatgpt_plan_envelope_receipt(root=root)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / 'chatgpt-plan-envelope-receipt.json'
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
        'readiness_state_count': len(payload.get('plan_envelope_readiness_states') or []),
    }
    current['changed_fields'] = _changed_fields(previous, current)
    entries.append(current)
    _write_json(history_path, _history_payload(entries))
    return {'receipt': payload, 'history_update': {'path': str(history_path), 'capture_count_after_write': len(entries), 'changed_fields_vs_previous': current['changed_fields']}}


def write_root_chatgpt_plan_envelope_receipt(*, root: Path = ROOT) -> Payload:
    payload = build_chatgpt_plan_envelope_receipt(root=root)
    _write_json(root / ROOT_OUTPUT_PATH.name, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Build or evaluate the ChatGPT plan envelope receipt.')
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
        payload = capture_chatgpt_plan_envelope_receipt(root=ROOT, output_dir=Path(args.output_dir), history_path=Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'history':
        payload = summarize_capture_history(Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'write-root':
        payload = write_root_chatgpt_plan_envelope_receipt(root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'evaluate':
        promotion = _read_json(Path(args.promotion))
        payload = evaluate_chatgpt_plan_envelope_receipt(promotion, root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return

    print(json.dumps(build_chatgpt_plan_envelope_receipt(root=ROOT), indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()
