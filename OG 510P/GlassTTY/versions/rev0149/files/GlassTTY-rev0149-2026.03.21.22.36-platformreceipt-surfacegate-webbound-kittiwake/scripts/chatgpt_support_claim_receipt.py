#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from chatgpt_promotion_stability_receipt import build_chatgpt_promotion_stability_receipt, evaluate_chatgpt_promotion_stability_receipt
except ModuleNotFoundError:  # pragma: no cover - import path differs under tests
    import importlib.util

    def _load(name: str, filename: str):
        path = Path(__file__).resolve().parent / filename
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    _PROMOTION = _load('chatgpt_promotion_stability_receipt', 'chatgpt_promotion_stability_receipt.py')
    build_chatgpt_promotion_stability_receipt = _PROMOTION.build_chatgpt_promotion_stability_receipt
    evaluate_chatgpt_promotion_stability_receipt = _PROMOTION.evaluate_chatgpt_promotion_stability_receipt

ROOT = Path(__file__).resolve().parent.parent
ROOT_OUTPUT_PATH = ROOT / 'CHATGPT-SUPPORT-CLAIM-RECEIPT.json'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-support-claim-receipt'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'chatgpt-support-claim-receipt-captures.json'
REPORT_COMMAND = 'python scripts/chatgpt-support-claim-receipt.py --pretty'
CAPTURE_COMMAND = 'python scripts/chatgpt-support-claim-receipt.py capture --output-dir validation/latest/chatgpt-support-claim-receipt'
HISTORY_COMMAND = 'python scripts/chatgpt-support-claim-receipt.py history --pretty'
WRITE_ROOT_COMMAND = 'python scripts/chatgpt-support-claim-receipt.py write-root'
EVALUATE_COMMAND = 'python scripts/chatgpt-support-claim-receipt.py evaluate --promotion path/to/promotion-window.json --pretty'

Payload = dict[str, Any]
BRANCH_NEEDLES = ('project', 'projects', 'canvas', 'gpt', 'gpts', 'history-search', 'history_search', 'sidebar-search')
OUT_OF_SCOPE_BRANCHES = ['projects', 'canvas', 'gpts-builder', 'sidebar-history-search', 'group-chats', 'record-mode']
OUT_OF_SCOPE_BROWSERS = ['firefox', 'webkit', 'mobile-web', 'ios', 'android']


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


def _reviewable_summaries(promotion_eval: Payload) -> list[Payload]:
    raw = promotion_eval.get('window_summaries')
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict) and item.get('bundle_readiness') in {'ready-for-held', 'ready-with-caution'}]


def _browser_lanes(promotion: Payload, windows: list[Payload]) -> list[str]:
    lanes: list[str] = []
    for key in ('browser_lane', 'capture_lane', 'lane'):
        value = promotion.get(key)
        if isinstance(value, str) and value.strip():
            lanes.append(value.strip())
    for window in windows:
        if not isinstance(window, dict):
            continue
        for key in ('browser_lane', 'capture_lane', 'lane'):
            value = window.get(key)
            if isinstance(value, str) and value.strip():
                lanes.append(value.strip())
    return list(dict.fromkeys(lanes))


def _branch_scope_key(summary: Payload) -> str | None:
    posture_key = _normalize_keyish(summary.get('matched_posture_key'))
    if posture_key:
        return posture_key
    route_path = _normalize_keyish(summary.get('route_path'))
    return route_path


def _branch_is_plain_route(summary: Payload) -> bool:
    key = _branch_scope_key(summary) or ''
    if any(needle in key for needle in BRANCH_NEEDLES):
        return False
    route_path = str(summary.get('route_path') or '').strip()
    if not route_path:
        return False
    return route_path.startswith('/')


def _probe_signatures(reviewable: list[Payload]) -> list[str]:
    values: list[str] = []
    for item in reviewable:
        probe = _normalize_text(item.get('probe_signature'))
        if probe:
            values.append(probe)
    return values


def _claim_scorecard(promotion: Payload, promotion_eval: Payload, windows: list[Payload], reviewable: list[Payload]) -> list[Payload]:
    lanes = _browser_lanes(promotion, windows)
    auths = [item.get('auth_posture') for item in reviewable if isinstance(item.get('auth_posture'), str) and str(item.get('auth_posture')).strip()]
    branches = [_branch_scope_key(item) for item in reviewable if _branch_scope_key(item)]
    probe_signatures = _probe_signatures(reviewable)
    return [
        {
            'check_key': 'reviewable_window_present',
            'required': True,
            'present': bool(reviewable),
            'detail': 'any lane-bound support claim should rest on at least one reviewable proof window rather than planning objects alone',
            'actual_count': len(reviewable),
        },
        {
            'check_key': 'browser_lane_explicit',
            'required': True,
            'present': bool(lanes) and len(lanes) == 1,
            'detail': 'support claims should stay anchored to one explicit browser lane instead of silently implying other browsers or devices',
            'browser_lanes': lanes,
        },
        {
            'check_key': 'auth_scope_explicit',
            'required': True,
            'present': bool(reviewable) and len(auths) == len(reviewable),
            'detail': 'logged-in and logged-out ChatGPT can differ, so the evidence should preserve the auth posture for every reviewable window',
            'auth_postures': auths,
        },
        {
            'check_key': 'plain_route_branch_only',
            'required': True,
            'present': bool(reviewable) and all(_branch_is_plain_route(item) for item in reviewable),
            'detail': 'the claim envelope should stop if the proof windows drift into Projects, Canvas, GPT builder, or sidebar-only history search instead of the plain route-first lane',
            'branch_scope_keys': branches,
        },
        {
            'check_key': 'workflow_slice_complete',
            'required': True,
            'present': bool(reviewable) and all(item.get('bundle_readiness') in {'ready-for-held', 'ready-with-caution'} for item in reviewable),
            'detail': 'support claims should only describe the route/composer/submit/latest-turn slice that the proof-bundle receipt already held together',
        },
        {
            'check_key': 'stable_probe_signature',
            'required': False,
            'present': bool(reviewable) and len(probe_signatures) == len(reviewable) and len(set(probe_signatures)) == 1,
            'detail': 'a stable benign probe/readback signature makes the allowed support wording more reviewable',
            'probe_signatures': probe_signatures,
        },
        {
            'check_key': 'support_record_and_candidate_bundle_attached',
            'required': False,
            'present': bool((promotion_eval.get('source_keys') or [])),
            'detail': 'keeping the claim envelope tied to the support record and candidate bundle makes later support-language review auditable',
        },
    ]


def _scope_summary(promotion: Payload, windows: list[Payload], reviewable: list[Payload]) -> Payload:
    lanes = _browser_lanes(promotion, windows)
    auths = list(dict.fromkeys(str(item.get('auth_posture')).strip() for item in reviewable if isinstance(item.get('auth_posture'), str) and str(item.get('auth_posture')).strip()))
    paths = list(dict.fromkeys(str(item.get('route_path')).strip() for item in reviewable if isinstance(item.get('route_path'), str) and str(item.get('route_path')).strip()))
    branches = list(dict.fromkeys(item for item in (_branch_scope_key(summary) for summary in reviewable) if item))
    return {
        'browser_lanes': lanes,
        'auth_postures': auths,
        'route_paths': paths,
        'branch_scope_keys': branches,
        'supported_workflows': ['surface-detect', 'receiver-resolve', 'composer-write', 'turn-submit', 'latest-turn-read'] if reviewable else [],
    }


def _claim_envelope(scope: Payload, *, max_tier: str, caution_flags: list[str]) -> Payload:
    lane = ', '.join(scope.get('browser_lanes') or []) or 'unspecified lane'
    auth = ', '.join(scope.get('auth_postures') or []) or 'unspecified auth posture'
    route_paths = scope.get('route_paths') or []
    route_scope = 'plain chatgpt.com route-first lane'
    if route_paths:
        route_scope = f"plain chatgpt.com route-first lane ({', '.join(route_paths)})"
    supported_claims = [
        f'GlassTTY has evidence only for the {lane} ChatGPT route-first lane, not for all browsers or devices.',
        f'The current claim envelope only covers the {auth} posture(s) captured in the proof windows.',
        'The supported workflow slice is limited to route detection, receiver resolution, composer writability, submit, and latest-turn readback.',
    ]
    if max_tier == 'provisional':
        supported_claims.append('Repeated proof windows justify a provisional but still lane-bound ChatGPT support claim.')
    elif max_tier == 'experimental':
        supported_claims.append('Current evidence can justify only an experimental lane-bound ChatGPT support claim.')
    else:
        supported_claims.append('Current evidence does not justify a live ChatGPT support claim beyond investigated planning artifacts.')
    excluded_claims = [
        'Do not claim cross-browser parity from Chromium-only proof windows.',
        'Do not claim Projects, Canvas, GPT builder, or sidebar history search support from the route-first baseline.',
        'Do not claim broader publication-ready support when the envelope still carries caution or missing-scope flags.',
    ]
    return {
        'tier_ceiling': max_tier,
        'browser_lane_scope': scope.get('browser_lanes') or [],
        'auth_posture_scope': scope.get('auth_postures') or [],
        'route_scope': route_scope,
        'workflow_scope': scope.get('supported_workflows') or [],
        'supported_claims': supported_claims,
        'excluded_claims': excluded_claims,
        'out_of_scope_branches': list(OUT_OF_SCOPE_BRANCHES),
        'out_of_scope_browser_families': list(OUT_OF_SCOPE_BROWSERS),
        'required_caveats': caution_flags,
    }


def evaluate_chatgpt_support_claim_receipt(promotion: Payload, *, root: Path = ROOT) -> Payload:
    spec = build_chatgpt_support_claim_receipt(root=root)
    promotion_eval = evaluate_chatgpt_promotion_stability_receipt(promotion, root=root)
    windows = _window_payloads(promotion)
    reviewable = _reviewable_summaries(promotion_eval)
    scorecard = _claim_scorecard(promotion, promotion_eval, windows, reviewable)
    present_checks = [item['check_key'] for item in scorecard if item.get('present')]
    missing_required = [item['check_key'] for item in scorecard if item.get('required') and not item.get('present')]
    missing_optional = [item['check_key'] for item in scorecard if not item.get('required') and not item.get('present')]
    scope = _scope_summary(promotion, windows, reviewable)

    caution_flags: list[str] = []
    for flag in promotion_eval.get('caution_flags') or []:
        if isinstance(flag, str) and flag not in caution_flags:
            caution_flags.append(flag)
    if 'stable_probe_signature' in missing_optional and reviewable:
        caution_flags.append('missing-stable-probe-envelope')

    promotion_state = str(promotion_eval.get('stability_readiness') or '')
    if promotion_state == 'stop' or ('plain_route_branch_only' in missing_required and reviewable):
        readiness = 'stop'
        reason = 'the supplied proof windows drift into a richer branch or off-lane posture, so the support claim should stop rather than over-generalize the baseline'
        recommended_tier = 'investigated'
    elif not reviewable:
        if promotion_state == 'planning-only':
            readiness = 'planning-only'
            reason = 'the receipt still describes claim-discipline for ChatGPT and does not yet have reviewable proof windows to bound support language'
        else:
            readiness = 'investigated-only'
            reason = 'some proof objects exist, but they are not reviewable enough to justify a live ChatGPT support claim beyond investigated status'
        recommended_tier = 'investigated'
    elif 'browser_lane_explicit' in missing_required or 'auth_scope_explicit' in missing_required:
        readiness = 'hold-for-scope-expansion'
        reason = 'the proof windows are partly reviewable, but the browser-lane or auth-posture boundary is still too fuzzy to turn the evidence into honest support language'
        recommended_tier = 'investigated'
    elif promotion_state == 'ready-for-provisional' and not missing_required:
        readiness = 'provisional-lane-bound'
        reason = 'repeated proof windows are stable enough for provisional support, but only within one explicitly bounded browser/auth/route envelope'
        recommended_tier = 'provisional'
    elif promotion_state in {'ready-with-caution', 'hold-for-recapture', 'blocked', 'blocked-by-route', 'blocked-by-composer'}:
        if reviewable and not missing_required and promotion_state in {'ready-with-caution', 'hold-for-recapture'}:
            readiness = 'experimental-lane-bound'
            if promotion_state == 'ready-with-caution':
                reason = 'the evidence can justify an experimental lane-bound claim, but the attached cautions and replay gaps still need to travel with it'
            else:
                reason = 'one held-quality proof window can justify an experimental lane-bound claim, but broader provisional support still needs a second repeated window'
            recommended_tier = 'experimental'
        else:
            readiness = 'hold-for-scope-expansion'
            reason = 'the current proof is not yet strong enough to widen support language, so the claim should remain held while scope or proof quality is repaired'
            recommended_tier = 'investigated'
    else:
        readiness = 'experimental-lane-bound'
        reason = 'one held-quality proof window can justify an experimental lane-bound claim, but not broader provisional support'
        recommended_tier = 'experimental'

    if readiness == 'planning-only':
        next_action = 'capture one live route-first ChatGPT proof window before trying to phrase any live support claim'
    elif readiness == 'investigated-only':
        next_action = 'repair the upstream receipts until at least one proof window becomes reviewable, then re-evaluate the claim envelope'
    elif readiness == 'hold-for-scope-expansion':
        next_action = 'make the browser lane, auth posture, and route scope explicit on the proof windows before widening ChatGPT support language'
    elif readiness == 'experimental-lane-bound':
        next_action = 'keep the support language explicitly lane-bound and preserve the caution flags while gathering the second repeated proof window'
    elif readiness == 'provisional-lane-bound':
        next_action = 'promote the ChatGPT story only to a provisional lane-bound claim and keep the out-of-scope branches and browser families explicit'
    else:
        next_action = 'return to the plain chatgpt.com baseline and avoid claiming support for richer ChatGPT workspaces from this evidence'

    envelope = _claim_envelope(scope, max_tier=recommended_tier, caution_flags=caution_flags)
    return {
        'project': 'GlassTTY',
        'surface_key': 'chatgpt',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'claim_evaluation_kind': 'chatgpt-routefirst-support-claim-envelope',
        'promotion_evaluation': promotion_eval,
        'window_scope_summary': scope,
        'field_scorecard': scorecard,
        'present_check_keys': present_checks,
        'missing_required_check_keys': missing_required,
        'missing_optional_check_keys': missing_optional,
        'claim_readiness': readiness,
        'claim_readiness_reason': reason,
        'recommended_support_record_tier': recommended_tier,
        'caution_flags': caution_flags,
        'claim_envelope': envelope,
        'recommended_next_action': next_action,
        'source_keys': spec.get('source_keys') or [],
    }


def _summary_markdown(payload: Payload) -> str:
    states = payload.get('claim_readiness_states') or []
    axes = payload.get('claim_axes') or []
    lines = [
        '# ChatGPT support claim receipt',
        '',
        f"- generated_at: `{payload.get('generated_at')}`",
        f"- target support tier: `{payload.get('target_support_tier')}`",
        '',
        '## Claim axes',
        '',
    ]
    for item in axes:
        lines.append(f"- {item.get('axis')}: {item.get('rule')}")
    lines.extend(['', '## Claim readiness states', ''])
    for item in states:
        lines.append(f"- {item.get('state')}: {item.get('rule')}")
    return '\n'.join(lines) + '\n'


def build_chatgpt_support_claim_receipt(*, root: Path = ROOT) -> Payload:
    promotion_spec = build_chatgpt_promotion_stability_receipt(root=root)
    source_keys = sorted(dict.fromkeys([*(promotion_spec.get('source_keys') or []), 'chatgpt-projects', 'chatgpt-canvas-feature', 'chatgpt-gpts-builder', 'chatgpt-history-search']))
    payload: Payload = {
        'project': 'GlassTTY',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'surface_key': 'chatgpt',
        'purpose': 'bound the strongest honest ChatGPT support claim so repeated proof windows do not silently expand into broader browser or workspace guarantees',
        'target_support_tier': 'provisional',
        'design_principles': [
            'Repeated Chromium proof should not silently imply Firefox, WebKit, mobile, or richer ChatGPT workspaces.',
            'Support wording should preserve explicit browser-lane, auth-posture, and route-branch boundaries rather than bury them in caveats.',
            'The claim envelope should describe what the current evidence covers and also what it explicitly does not cover.',
        ],
        'claim_axes': [
            {'axis': 'browser-lane', 'rule': 'one repeated proof lane should only justify claims for the explicit browser lane it was captured on'},
            {'axis': 'auth-posture', 'rule': 'logged-in and logged-out proof should remain distinguishable in the support story'},
            {'axis': 'route-branch', 'rule': 'plain route-first proof should not be generalized to Projects, Canvas, GPT builder, or sidebar history search'},
            {'axis': 'workflow-slice', 'rule': 'the supported slice should stay limited to route/composer/submit/latest-turn behavior already proved by receipts'},
        ],
        'claim_readiness_states': [
            {'state': 'provisional-lane-bound', 'rule': 'repeated proof windows justify provisional support, but only within one explicit browser/auth/route envelope'},
            {'state': 'experimental-lane-bound', 'rule': 'the evidence can support only an experimental lane-bound claim, usually because only one reviewable window exists or caution still travels with it'},
            {'state': 'hold-for-scope-expansion', 'rule': 'proof exists, but the scope boundaries are still too fuzzy to phrase an honest support claim'},
            {'state': 'investigated-only', 'rule': 'planning or thin proof artifacts exist, but they do not yet justify a live support claim'},
            {'state': 'planning-only', 'rule': 'the receipt still describes claim discipline rather than current live evidence'},
            {'state': 'stop', 'rule': 'the proof windows drifted into a richer or off-lane branch and should not be generalized into baseline support language'},
        ],
        'commands': {
            'report': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
            'capture_history': HISTORY_COMMAND,
            'write_root': WRITE_ROOT_COMMAND,
            'evaluate': EVALUATE_COMMAND,
            'promotion_stability_receipt': 'python scripts/chatgpt-promotion-stability-receipt.py --pretty',
        },
        'source_keys': source_keys,
    }
    payload['summary_markdown'] = _summary_markdown(payload)
    return payload


def capture_chatgpt_support_claim_receipt(*, root: Path = ROOT, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH) -> Payload:
    payload = build_chatgpt_support_claim_receipt(root=root)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'chatgpt-support-claim-receipt.json'
    summary_path = output_dir / 'SUMMARY.md'
    _write_json(output_path, payload)
    summary_path.write_text(payload.get('summary_markdown', ''), encoding='utf-8')

    entries = _history_entries(history_path)
    previous = entries[-1] if entries else None
    entry = {
        'captured_at': payload.get('generated_at'),
        'path': str(output_path),
        'summary_path': str(summary_path),
        'target_support_tier': payload.get('target_support_tier'),
        'claim_readiness_states': [item.get('state') for item in payload.get('claim_readiness_states') or []],
        'source_keys': payload.get('source_keys') or [],
    }
    entries.append(entry)
    _write_json(history_path, _history_payload(entries))
    return {
        'receipt': payload,
        'output_path': str(output_path),
        'summary_path': str(summary_path),
        'history_update': {
            'history_path': str(history_path),
            'capture_count_after_write': len(entries),
            'changed_fields': _changed_fields(previous, entry),
        },
    }


def write_root_chatgpt_support_claim_receipt(*, root: Path = ROOT) -> Payload:
    payload = build_chatgpt_support_claim_receipt(root=root)
    _write_json(root / ROOT_OUTPUT_PATH.name, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Build or evaluate a ChatGPT support-claim envelope receipt.')
    parser.add_argument('--pretty', action='store_true')
    subparsers = parser.add_subparsers(dest='command')
    capture_parser = subparsers.add_parser('capture')
    capture_parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    capture_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    history_parser = subparsers.add_parser('history')
    history_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    history_parser.add_argument('--pretty', action='store_true')
    write_root_parser = subparsers.add_parser('write-root')
    write_root_parser.add_argument('--pretty', action='store_true')
    evaluate_parser = subparsers.add_parser('evaluate')
    evaluate_parser.add_argument('--promotion', required=True)
    evaluate_parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()

    if args.command == 'capture':
        payload = capture_chatgpt_support_claim_receipt(root=ROOT, output_dir=Path(args.output_dir), history_path=Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'history':
        payload = summarize_capture_history(Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'write-root':
        payload = write_root_chatgpt_support_claim_receipt(root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'evaluate':
        promotion = _read_json(Path(args.promotion))
        payload = evaluate_chatgpt_support_claim_receipt(promotion, root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    print(json.dumps(build_chatgpt_support_claim_receipt(root=ROOT), indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()
