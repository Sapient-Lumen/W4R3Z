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
ROOT_OUTPUT_PATH = ROOT / 'CHATGPT-BROWSER-ENVELOPE-RECEIPT.json'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-browser-envelope-receipt'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'chatgpt-browser-envelope-receipt-captures.json'
REPORT_COMMAND = 'python scripts/chatgpt-browser-envelope-receipt.py --pretty'
CAPTURE_COMMAND = 'python scripts/chatgpt-browser-envelope-receipt.py capture --output-dir validation/latest/chatgpt-browser-envelope-receipt'
HISTORY_COMMAND = 'python scripts/chatgpt-browser-envelope-receipt.py history --pretty'
WRITE_ROOT_COMMAND = 'python scripts/chatgpt-browser-envelope-receipt.py write-root'
EVALUATE_COMMAND = 'python scripts/chatgpt-browser-envelope-receipt.py evaluate --promotion path/to/promotion-window.json --pretty'

Payload = dict[str, Any]


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


def _reviewable_summaries(auth_eval: Payload) -> list[Payload]:
    capability_eval = auth_eval.get('capability_evaluation') if isinstance(auth_eval.get('capability_evaluation'), dict) else {}
    claim_eval = capability_eval.get('claim_evaluation') if isinstance(capability_eval.get('claim_evaluation'), dict) else {}
    promotion_eval = claim_eval.get('promotion_evaluation') if isinstance(claim_eval.get('promotion_evaluation'), dict) else {}
    raw = promotion_eval.get('window_summaries')
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict) and item.get('proof_window_status') in {'coherent', 'coherent-with-caution'}]


def _summary_lookup(auth_eval: Payload) -> dict[int, Payload]:
    by_index: dict[int, Payload] = {}
    for item in _reviewable_summaries(auth_eval):
        idx = item.get('window_index')
        if isinstance(idx, int):
            by_index[idx - 1] = item
    return by_index


def _artifact_rows(window: Payload) -> list[Payload]:
    rows: list[Payload] = []
    for key in ('artifact_refs', 'artifacts', 'bundle_artifacts'):
        raw = window.get(key)
        if isinstance(raw, list):
            rows.extend(item for item in raw if isinstance(item, dict))
    return rows


def _artifact_hints(rows: list[Payload]) -> str:
    hints: list[str] = []
    for row in rows:
        for field in ('kind', 'path', 'role'):
            value = row.get(field)
            if isinstance(value, str) and value.strip():
                hints.append(value.strip())
    return ' '.join(hints).lower()


def _infer_browser_profile(lane: str | None) -> Payload:
    normalized = _normalize_keyish(lane) or ''
    engine = None
    brand = None
    device_class = None
    execution_mode = None
    if 'firefox' in normalized:
        engine = 'firefox'
        brand = 'firefox'
    elif 'webkit' in normalized or 'safari' in normalized:
        engine = 'webkit'
        brand = 'webkit'
    elif 'edge' in normalized:
        engine = 'chromium'
        brand = 'edge'
    elif 'chrome' in normalized and 'chromium' not in normalized:
        engine = 'chromium'
        brand = 'chrome'
    elif 'chromium' in normalized:
        engine = 'chromium'
        brand = 'chromium'
    if any(token in normalized for token in ('mobile', 'android', 'ios')):
        device_class = 'mobile-web'
    elif normalized:
        device_class = 'desktop-web'
    if 'headless' in normalized:
        execution_mode = 'headless'
    elif any(token in normalized for token in ('headed', 'live')):
        execution_mode = 'live'
    return {
        'browser_lane': normalized or None,
        'browser_engine': engine,
        'browser_brand': brand,
        'device_class': device_class,
        'execution_mode': execution_mode,
    }


def _browser_profile(window: Payload, summary: Payload | None) -> Payload:
    lane = None
    for source in [summary or {}, window, window.get('route_witness') if isinstance(window.get('route_witness'), dict) else {}]:
        if not isinstance(source, dict):
            continue
        for key in ('browser_lane', 'capture_lane', 'lane', 'project_name'):
            value = _normalize_keyish(source.get(key))
            if value:
                lane = value
                break
        if lane:
            break
    inferred = _infer_browser_profile(lane)
    return {
        'browser_lane': inferred.get('browser_lane'),
        'browser_engine': inferred.get('browser_engine'),
        'browser_brand': inferred.get('browser_brand'),
        'device_class': inferred.get('device_class'),
        'execution_mode': inferred.get('execution_mode'),
        'project_name': inferred.get('browser_lane'),
        'profile_signature': '|'.join(str(inferred.get(key) or 'unknown') for key in ('browser_lane', 'browser_engine', 'browser_brand', 'device_class', 'execution_mode')),
    }


def _unique(values: list[str | None]) -> list[str]:
    return list(dict.fromkeys([value for value in values if isinstance(value, str) and value]))


def _reviewable_profiles(promotion: Payload, auth_eval: Payload) -> list[Payload]:
    windows = _window_payloads(promotion)
    summary_lookup = _summary_lookup(auth_eval)
    profiles: list[Payload] = []
    for index, window in enumerate(windows):
        if not isinstance(window, dict):
            continue
        summary = summary_lookup.get(index)
        if not isinstance(summary, dict):
            continue
        profile = _browser_profile(window, summary)
        profile['window_index'] = index + 1
        profiles.append(profile)
    return profiles


def _interference_documented(window: Payload) -> bool:
    hints = _artifact_hints(_artifact_rows(window))
    if any(token in hints for token in ('incognito', 'private', 'clean-profile', 'extension', 'troubleshoot', 'network')):
        return True
    route = window.get('route_witness') if isinstance(window.get('route_witness'), dict) else {}
    for source in (window, route):
        if not isinstance(source, dict):
            continue
        for key in ('clean_profile', 'private_window', 'extensions_disabled', 'browser_troubleshooting_noted'):
            if source.get(key) is True:
                return True
    return False


def _field_scorecard(promotion: Payload, auth_eval: Payload, profiles: list[Payload]) -> list[Payload]:
    lanes = _unique([profile.get('browser_lane') for profile in profiles])
    engines = _unique([profile.get('browser_engine') for profile in profiles])
    brands = _unique([profile.get('browser_brand') for profile in profiles])
    devices = _unique([profile.get('device_class') for profile in profiles])
    executions = _unique([profile.get('execution_mode') for profile in profiles])
    windows = _window_payloads(promotion)
    return [
        {
            'check_key': 'reviewable_window_present',
            'required': True,
            'present': bool(profiles),
            'detail': 'a browser envelope should rest on at least one reviewable proof window rather than only planning objects',
            'actual_count': len(profiles),
        },
        {
            'check_key': 'browser_lane_explicit',
            'required': True,
            'present': bool(profiles) and len(lanes) == 1 and len(profiles) == sum(1 for item in profiles if item.get('browser_lane')),
            'detail': 'support language should stay anchored to one explicit browser lane instead of silently implying other Playwright projects or browsers',
            'browser_lanes': lanes,
        },
        {
            'check_key': 'browser_engine_explicit',
            'required': True,
            'present': bool(profiles) and len(engines) == 1 and len(profiles) == sum(1 for item in profiles if item.get('browser_engine')),
            'detail': 'browser engine should stay explicit because Playwright projects can target Chromium, Firefox, or WebKit separately',
            'browser_engines': engines,
        },
        {
            'check_key': 'browser_brand_explicit',
            'required': True,
            'present': bool(profiles) and len(brands) == 1 and len(profiles) == sum(1 for item in profiles if item.get('browser_brand')),
            'detail': 'brand/channel should stay explicit so one explicit browser lane does not silently imply other branded-browser coverage',
            'browser_brands': brands,
        },
        {
            'check_key': 'device_class_explicit',
            'required': True,
            'present': bool(profiles) and len(devices) == 1 and len(profiles) == sum(1 for item in profiles if item.get('device_class')),
            'detail': 'desktop-web and mobile-web runs should remain distinct support envelopes',
            'device_classes': devices,
        },
        {
            'check_key': 'execution_mode_explicit',
            'required': True,
            'present': bool(profiles) and len(executions) == 1 and len(profiles) == sum(1 for item in profiles if item.get('execution_mode')),
            'detail': 'headless and live/headed runs should remain distinct support envelopes',
            'execution_modes': executions,
        },
        {
            'check_key': 'project_profile_coherent',
            'required': True,
            'present': bool(profiles) and len({profile.get('profile_signature') for profile in profiles}) == 1,
            'detail': 'repeated proof windows should stay on one coherent browser project profile before support wording broadens',
            'profile_signatures': _unique([profile.get('profile_signature') for profile in profiles]),
        },
        {
            'check_key': 'browser_interference_posture_recorded',
            'required': False,
            'present': bool(profiles) and all(_interference_documented(window) for window in windows[: len(profiles)]),
            'detail': 'browser troubleshooting or clean-profile notes make later review of extensions, VPNs, or cache effects more honest',
        },
        {
            'check_key': 'auth_workspace_receipt_attached',
            'required': False,
            'present': isinstance(auth_eval.get('auth_workspace_evaluation_kind'), str),
            'detail': 'keep the browser envelope tied to the auth/workspace envelope so scope review stays auditable',
        },
    ]


def _browser_envelope(profiles: list[Payload], *, max_tier: str, caution_flags: list[str]) -> Payload:
    brands = _unique([profile.get('browser_brand') for profile in profiles])
    excluded = ['firefox', 'webkit', 'edge', 'chrome', 'mobile-web'] if brands == ['chromium'] else ['other-browser-lanes']
    return {
        'browser_lane_scope': _unique([profile.get('browser_lane') for profile in profiles]),
        'browser_engine_scope': _unique([profile.get('browser_engine') for profile in profiles]),
        'browser_brand_scope': brands,
        'device_class_scope': _unique([profile.get('device_class') for profile in profiles]),
        'execution_mode_scope': _unique([profile.get('execution_mode') for profile in profiles]),
        'tier_ceiling': max_tier,
        'caution_flags': caution_flags,
        'excluded_browser_scope': excluded,
    }


def evaluate_chatgpt_browser_envelope_receipt(promotion: Payload, *, root: Path = ROOT) -> Payload:
    spec = build_chatgpt_browser_envelope_receipt(root=root)
    auth_eval = evaluate_chatgpt_auth_workspace_receipt(promotion, root=root)
    profiles = _reviewable_profiles(promotion, auth_eval)
    scorecard = _field_scorecard(promotion, auth_eval, profiles)
    present_checks = [item['check_key'] for item in scorecard if item.get('present')]
    missing_required = [item['check_key'] for item in scorecard if item.get('required') and not item.get('present')]
    missing_optional = [item['check_key'] for item in scorecard if not item.get('required') and not item.get('present')]
    caution_flags: list[str] = []
    if 'browser_interference_posture_recorded' in missing_optional:
        caution_flags.append('missing-browser-troubleshooting-notes')

    if any(len(_unique([profile.get(key) for profile in profiles])) > 1 for key in ('browser_lane', 'browser_engine', 'browser_brand', 'device_class', 'execution_mode')):
        readiness = 'stop'
        reason = 'the supplied proof windows mix incompatible browser/project profiles and should be split into separate browser evidence lanes'
        tier = 'investigated'
        next_action = 'split the proof windows by browser/project profile before phrasing support language'
    elif not profiles:
        if auth_eval.get('auth_workspace_readiness') == 'planning-only':
            readiness = 'planning-only'
            reason = 'no reviewable proof windows are attached yet, so the receipt still describes browser-boundary discipline rather than live evidence'
            tier = 'investigated'
            next_action = 'capture at least one reviewable ChatGPT proof window with an explicit browser lane'
        else:
            readiness = 'investigated-only'
            reason = 'upstream proof planning exists, but there is still no reviewable browser-scoped ChatGPT proof window'
            tier = str(auth_eval.get('recommended_support_record_tier') or 'investigated')
            next_action = 'capture a reviewable ChatGPT proof window with explicit browser-lane metadata'
    elif missing_required:
        readiness = 'hold-for-browser-clarification'
        reason = 'proof exists, but the browser engine, brand, device class, or execution mode is still too fuzzy to phrase honestly'
        tier = str(auth_eval.get('recommended_support_record_tier') or 'experimental')
        next_action = 'preserve one explicit browser/project signature per proof window before widening support language'
    else:
        upstream_tier = str(auth_eval.get('recommended_support_record_tier') or 'experimental')
        if len(profiles) >= 2 and upstream_tier == 'provisional':
            readiness = 'provisional-browser-envelope'
            reason = 'repeated proof windows stay on one coherent browser project profile, so the support story can stay provisionally browser-bound'
            tier = 'provisional'
            next_action = 'keep support wording bound to this browser profile until separate Firefox, WebKit, Chrome, Edge, or mobile proof exists'
        else:
            readiness = 'experimental-browser-envelope'
            reason = 'one reviewable browser-scoped proof window exists, but repeated proof or stronger upstream scope is still limited'
            tier = 'experimental'
            next_action = 'repeat the same route-first proof on a second window of the same browser profile before strengthening support language'

    envelope = _browser_envelope(profiles, max_tier=tier, caution_flags=caution_flags)
    return {
        'project': 'GlassTTY',
        'surface_key': 'chatgpt',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'browser_envelope_evaluation_kind': 'chatgpt-routefirst-browser-envelope',
        'auth_workspace_evaluation': auth_eval,
        'window_browser_profiles': profiles,
        'field_scorecard': scorecard,
        'present_check_keys': present_checks,
        'missing_required_check_keys': missing_required,
        'missing_optional_check_keys': missing_optional,
        'browser_envelope_readiness': readiness,
        'browser_envelope_readiness_reason': reason,
        'recommended_support_record_tier': tier,
        'caution_flags': caution_flags,
        'browser_envelope': envelope,
        'recommended_next_action': next_action,
        'source_keys': spec.get('source_keys') or [],
    }


def _summary_markdown(payload: Payload) -> str:
    axes = payload.get('browser_envelope_axes') or []
    states = payload.get('browser_envelope_readiness_states') or []
    lines = [
        '# ChatGPT browser envelope receipt',
        '',
        f"- generated_at: `{payload.get('generated_at')}`",
        f"- target support tier: `{payload.get('target_support_tier')}`",
        '',
        '## Browser envelope axes',
        '',
    ]
    for item in axes:
        lines.append(f"- {item.get('axis')}: {item.get('rule')}")
    lines.extend(['', '## Browser envelope readiness states', ''])
    for item in states:
        lines.append(f"- {item.get('state')}: {item.get('rule')}")
    lines.append('')
    return '\n'.join(lines)


def build_chatgpt_browser_envelope_receipt(*, root: Path = ROOT) -> Payload:
    auth_spec = build_chatgpt_auth_workspace_receipt(root=root)
    payload = {
        'project': 'GlassTTY',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'surface_key': 'chatgpt',
        'purpose': 'bound the strongest honest ChatGPT browser/project envelope so repeated route-first proof does not silently expand one explicit browser lane into broader browser support',
        'target_support_tier': 'provisional',
        'design_principles': [
            'Repeated Chromium proof should stay distinct from Firefox, WebKit, Chrome, Edge, or mobile-web proof until those projects have their own evidence.',
            'Browser engine, brand/channel, device class, and execution mode should remain visible because ChatGPT behavior can vary with extensions, network posture, or browser-specific configuration.',
            'The browser envelope should narrow what current proof covers rather than silently inheriting a broader support story from a generic browser-lane string.',
        ],
        'browser_envelope_axes': [
            {'axis': 'browser-engine', 'rule': 'Chromium, Firefox, and WebKit proof should remain distinct support envelopes'},
            {'axis': 'browser-brand', 'rule': 'one explicit Chromium lane should not silently imply Chrome, Edge, or other branded-browser coverage'},
            {'axis': 'device-class', 'rule': 'desktop-web and mobile-web runs should remain separate until both have explicit proof'},
            {'axis': 'execution-profile', 'rule': 'headless and live/headed runs should stay visible in the evidence story'},
        ],
        'browser_envelope_readiness_states': [
            {'state': 'provisional-browser-envelope', 'rule': 'repeated proof windows justify only a provisional browser/project-bound support envelope'},
            {'state': 'experimental-browser-envelope', 'rule': 'current evidence can justify only an experimental browser/project-bound support envelope'},
            {'state': 'hold-for-browser-clarification', 'rule': 'proof exists, but the browser engine, brand, device class, or execution mode is still too fuzzy to phrase honestly'},
            {'state': 'investigated-only', 'rule': 'planning or thin proof artifacts exist, but they do not yet justify a live browser envelope'},
            {'state': 'planning-only', 'rule': 'the receipt still describes browser-boundary discipline rather than current live evidence'},
            {'state': 'stop', 'rule': 'the supplied proof windows mix incompatible browser/project profiles and should be split into separate evidence lanes'},
        ],
        'commands': {
            'report': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
            'capture_history': HISTORY_COMMAND,
            'write_root': WRITE_ROOT_COMMAND,
            'evaluate': EVALUATE_COMMAND,
            'auth_workspace_receipt': 'python scripts/chatgpt-auth-workspace-receipt.py --pretty',
        },
        'source_keys': sorted(dict.fromkeys((auth_spec.get('source_keys') or []) + ['chatgpt-troubleshooting-errors', 'playwright-browsers', 'playwright-projects'])),
    }
    payload['summary_markdown'] = _summary_markdown(payload)
    return payload


def capture_chatgpt_browser_envelope_receipt(*, root: Path = ROOT, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH) -> Payload:
    payload = build_chatgpt_browser_envelope_receipt(root=root)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / 'chatgpt-browser-envelope-receipt.json'
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
        'readiness_state_count': len(payload.get('browser_envelope_readiness_states') or []),
    }
    current['changed_fields'] = _changed_fields(previous, current)
    entries.append(current)
    _write_json(history_path, _history_payload(entries))
    return {'receipt': payload, 'history_update': {'path': str(history_path), 'capture_count_after_write': len(entries), 'changed_fields_vs_previous': current['changed_fields']}}


def write_root_chatgpt_browser_envelope_receipt(*, root: Path = ROOT) -> Payload:
    payload = build_chatgpt_browser_envelope_receipt(root=root)
    _write_json(root / ROOT_OUTPUT_PATH.name, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Build or evaluate the ChatGPT browser envelope receipt.')
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
        payload = capture_chatgpt_browser_envelope_receipt(root=ROOT, output_dir=Path(args.output_dir), history_path=Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'history':
        payload = summarize_capture_history(Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'write-root':
        payload = write_root_chatgpt_browser_envelope_receipt(root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'evaluate':
        promotion = _read_json(Path(args.promotion))
        payload = evaluate_chatgpt_browser_envelope_receipt(promotion, root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    payload = build_chatgpt_browser_envelope_receipt(root=ROOT)
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()
