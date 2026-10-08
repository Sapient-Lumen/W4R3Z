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
ROOT_OUTPUT_PATH = ROOT / 'CHATGPT-PLATFORM-ENVELOPE-RECEIPT.json'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-platform-envelope-receipt'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'chatgpt-platform-envelope-receipt-captures.json'
REPORT_COMMAND = 'python scripts/chatgpt-platform-envelope-receipt.py --pretty'
CAPTURE_COMMAND = 'python scripts/chatgpt-platform-envelope-receipt.py capture --output-dir validation/latest/chatgpt-platform-envelope-receipt'
HISTORY_COMMAND = 'python scripts/chatgpt-platform-envelope-receipt.py history --pretty'
WRITE_ROOT_COMMAND = 'python scripts/chatgpt-platform-envelope-receipt.py write-root'
EVALUATE_COMMAND = 'python scripts/chatgpt-platform-envelope-receipt.py evaluate --promotion path/to/promotion-window.json --pretty'

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


def _reviewable_profiles(browser_eval: Payload) -> list[Payload]:
    raw = browser_eval.get('window_browser_profiles')
    return [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []


def _browser_lookup(browser_eval: Payload) -> dict[int, Payload]:
    out: dict[int, Payload] = {}
    for item in _reviewable_profiles(browser_eval):
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


def _collect_strings(window: Payload) -> list[str]:
    strings: list[str] = []
    route = window.get('route_witness') if isinstance(window.get('route_witness'), dict) else {}
    for source in (window, route):
        if not isinstance(source, dict):
            continue
        for key in ('title', 'page_title', 'route_title', 'platform_surface', 'platform_family', 'client_platform', 'app_platform', 'runtime', 'surface_identity_text', 'visible_text', 'main_region_text'):
            value = source.get(key)
            if isinstance(value, str) and value.strip():
                strings.append(value.strip())
            elif isinstance(value, list):
                strings.extend(item.strip() for item in value if isinstance(item, str) and item.strip())
    strings.extend(_artifact_hints(_artifact_rows(window)))
    return strings


def _infer_from_strings(strings: list[str]) -> tuple[str | None, str | None, str | None, str | None]:
    joined = ' '.join((_normalize_text(item) or '') for item in strings)
    if 'windows app' in joined or 'companion window' in joined or 'microsoft store' in joined:
        return 'windows-app', 'native-app', 'desktop', 'windows-native'
    if 'macos app' in joined or 'chatgpt for macos' in joined or 'chatgpt for mac' in joined:
        return 'macos-app', 'native-app', 'desktop', 'macos-native'
    if 'ios app' in joined or 'iphone app' in joined or 'ipad app' in joined:
        return 'ios-app', 'native-app', 'tablet' if 'ipad' in joined else 'phone', 'ios-native'
    if 'android app' in joined or 'google play' in joined:
        return 'android-app', 'native-app', 'phone', 'android-native'
    if 'mobile safari' in joined or 'mobile chrome' in joined or 'iphone' in joined or 'pixel 5' in joined:
        return 'mobile-web', 'web', 'phone', 'chatgpt-web'
    if 'ipad' in joined or 'tablet' in joined:
        return 'tablet-web', 'web', 'tablet', 'chatgpt-web'
    return None, None, None, None


def _explicit_platform_profile(window: Payload) -> tuple[str | None, str | None, str | None, str | None]:
    route = window.get('route_witness') if isinstance(window.get('route_witness'), dict) else {}
    surface = family = form = runtime = None
    for source in (window, route):
        if not isinstance(source, dict):
            continue
        for key in ('platform_surface', 'surface_platform', 'client_platform', 'app_platform', 'platform_scope'):
            value = _normalize_keyish(source.get(key))
            if value:
                surface = value
                break
        for key in ('platform_family', 'surface_family'):
            value = _normalize_keyish(source.get(key))
            if value:
                family = value
                break
        for key in ('form_factor', 'device_form_factor'):
            value = _normalize_keyish(source.get(key))
            if value:
                form = value
                break
        for key in ('platform_runtime', 'runtime', 'surface_runtime', 'app_runtime'):
            value = _normalize_keyish(source.get(key))
            if value:
                runtime = value
                break
    inferred_surface, inferred_family, inferred_form, inferred_runtime = _infer_from_strings(_collect_strings(window))
    return surface or inferred_surface, family or inferred_family, form or inferred_form, runtime or inferred_runtime


def _platform_profile(window: Payload, browser_profile: Payload | None) -> Payload:
    route = window.get('route_witness') if isinstance(window.get('route_witness'), dict) else {}
    surface, family, form, runtime = _explicit_platform_profile(window)
    host = _normalize_keyish(route.get('host') or window.get('host'))
    path = route.get('path') if isinstance(route.get('path'), str) else window.get('path')
    browser_device = _normalize_keyish((browser_profile or {}).get('device_class'))
    browser_lane = _normalize_keyish((browser_profile or {}).get('browser_lane'))

    if not surface and host in {'chatgpt.com', 'www.chatgpt.com'}:
        if browser_device == 'mobile-web':
            surface = 'mobile-web'
        elif browser_lane and 'tablet' in browser_lane:
            surface = 'tablet-web'
        else:
            surface = 'desktop-web'
    if not family and surface:
        family = 'web' if surface.endswith('-web') else 'native-app'
    if not form:
        if surface in {'desktop-web', 'windows-app', 'macos-app'}:
            form = 'desktop'
        elif surface in {'ios-app', 'android-app', 'mobile-web'}:
            form = 'phone'
        elif surface == 'tablet-web':
            form = 'tablet'
    if not runtime:
        runtime = {
            'desktop-web': 'chatgpt-web',
            'mobile-web': 'chatgpt-web',
            'tablet-web': 'chatgpt-web',
            'windows-app': 'windows-native',
            'macos-app': 'macos-native',
            'ios-app': 'ios-native',
            'android-app': 'android-native',
        }.get(surface)
    return {
        'platform_surface': surface,
        'platform_family': family,
        'form_factor': form,
        'app_runtime': runtime,
        'route_host': host,
        'route_path': path,
        'browser_lane': browser_lane,
        'profile_signature': '|'.join(str(value or 'unknown') for value in (surface, family, form, runtime)),
    }


def _unique(values: list[str | None]) -> list[str]:
    return list(dict.fromkeys([value for value in values if isinstance(value, str) and value]))


def _reviewable_platform_profiles(promotion: Payload, browser_eval: Payload) -> list[Payload]:
    windows = _window_payloads(promotion)
    browser_lookup = _browser_lookup(browser_eval)
    profiles: list[Payload] = []
    for index, window in enumerate(windows):
        if not isinstance(window, dict):
            continue
        browser_profile = browser_lookup.get(index)
        if not isinstance(browser_profile, dict):
            continue
        profile = _platform_profile(window, browser_profile)
        profile['window_index'] = index + 1
        profiles.append(profile)
    return profiles


def _field_scorecard(browser_eval: Payload, profiles: list[Payload]) -> list[Payload]:
    surfaces = _unique([profile.get('platform_surface') for profile in profiles])
    families = _unique([profile.get('platform_family') for profile in profiles])
    forms = _unique([profile.get('form_factor') for profile in profiles])
    runtimes = _unique([profile.get('app_runtime') for profile in profiles])
    hosts = _unique([profile.get('route_host') for profile in profiles])
    return [
        {'check_key': 'reviewable_window_present', 'required': True, 'present': bool(profiles), 'detail': 'a platform envelope should rest on at least one reviewable proof window rather than only planning objects', 'actual_count': len(profiles)},
        {'check_key': 'platform_surface_explicit', 'required': True, 'present': bool(profiles) and len(surfaces) == 1 and len(profiles) == sum(1 for item in profiles if item.get('platform_surface')), 'detail': 'support language should stay anchored to one explicit platform surface instead of silently implying desktop web, mobile web, and native apps all at once', 'platform_surfaces': surfaces},
        {'check_key': 'platform_family_explicit', 'required': True, 'present': bool(profiles) and len(families) == 1 and len(profiles) == sum(1 for item in profiles if item.get('platform_family')), 'detail': 'web and native-app evidence should remain distinct support envelopes', 'platform_families': families},
        {'check_key': 'form_factor_explicit', 'required': True, 'present': bool(profiles) and len(forms) == 1 and len(profiles) == sum(1 for item in profiles if item.get('form_factor')), 'detail': 'desktop, tablet, and phone form factors should remain distinct support envelopes', 'form_factors': forms},
        {'check_key': 'app_runtime_explicit', 'required': True, 'present': bool(profiles) and len(runtimes) == 1 and len(profiles) == sum(1 for item in profiles if item.get('app_runtime')), 'detail': 'the evidence should say whether the proof came from chatgpt.com web, Windows app, macOS app, iOS app, or Android app before the support story broadens', 'app_runtimes': runtimes},
        {'check_key': 'chatgpt_web_host_explicit_when_web', 'required': True, 'present': all(profile.get('platform_family') != 'web' or profile.get('route_host') in {'chatgpt.com', 'www.chatgpt.com'} for profile in profiles), 'detail': 'web platform proof should stay visibly bound to chatgpt.com rather than silently implying desktop or mobile app shells', 'route_hosts': hosts},
        {'check_key': 'platform_profile_coherent', 'required': True, 'present': bool(profiles) and len({profile.get('profile_signature') for profile in profiles}) == 1, 'detail': 'repeated proof windows should stay on one coherent platform profile before support wording broadens', 'profile_signatures': _unique([profile.get('profile_signature') for profile in profiles])},
        {'check_key': 'browser_envelope_attached', 'required': False, 'present': isinstance(browser_eval.get('browser_envelope_evaluation_kind'), str), 'detail': 'keep the platform envelope tied to the browser envelope so lane review stays auditable'},
    ]


def _platform_envelope(profiles: list[Payload], *, max_tier: str, caution_flags: list[str]) -> Payload:
    scope = _unique([profile.get('platform_surface') for profile in profiles])
    excluded = {
        ('desktop-web',): ['mobile-web', 'windows-app', 'macos-app', 'ios-app', 'android-app'],
        ('mobile-web',): ['desktop-web', 'windows-app', 'macos-app', 'ios-app', 'android-app'],
        ('windows-app',): ['desktop-web', 'mobile-web', 'macos-app', 'ios-app', 'android-app'],
        ('macos-app',): ['desktop-web', 'mobile-web', 'windows-app', 'ios-app', 'android-app'],
    }.get(tuple(scope), ['other-platform-surfaces'])
    return {
        'platform_surface_scope': scope,
        'platform_family_scope': _unique([profile.get('platform_family') for profile in profiles]),
        'form_factor_scope': _unique([profile.get('form_factor') for profile in profiles]),
        'app_runtime_scope': _unique([profile.get('app_runtime') for profile in profiles]),
        'tier_ceiling': max_tier,
        'caution_flags': caution_flags,
        'excluded_platform_scope': excluded,
    }


def evaluate_chatgpt_platform_envelope_receipt(promotion: Payload, *, root: Path = ROOT) -> Payload:
    spec = build_chatgpt_platform_envelope_receipt(root=root)
    browser_eval = evaluate_chatgpt_browser_envelope_receipt(promotion, root=root)
    profiles = _reviewable_platform_profiles(promotion, browser_eval)
    scorecard = _field_scorecard(browser_eval, profiles)
    present_checks = [item['check_key'] for item in scorecard if item.get('present')]
    missing_required = [item['check_key'] for item in scorecard if item.get('required') and not item.get('present')]
    missing_optional = [item['check_key'] for item in scorecard if not item.get('required') and not item.get('present')]
    caution_flags: list[str] = []

    if any(len(_unique([profile.get(key) for profile in profiles])) > 1 for key in ('platform_surface', 'platform_family', 'form_factor', 'app_runtime')):
        readiness = 'stop'
        reason = 'the supplied proof windows mix incompatible product-surface profiles and should be split into separate platform evidence lanes'
        tier = 'investigated'
        next_action = 'split the proof windows by product surface before phrasing support language'
    elif not profiles:
        browser_readiness = str(browser_eval.get('browser_envelope_readiness') or '')
        if browser_readiness == 'planning-only':
            readiness = 'planning-only'
            reason = 'no reviewable proof windows are attached yet, so the receipt still describes platform-boundary discipline rather than live evidence'
            tier = 'investigated'
            next_action = 'capture at least one reviewable ChatGPT proof window with explicit platform metadata'
        else:
            readiness = 'investigated-only'
            reason = 'upstream browser-scoped proof planning exists, but there is still no reviewable platform-scoped ChatGPT proof window'
            tier = str(browser_eval.get('recommended_support_record_tier') or 'investigated')
            next_action = 'capture a reviewable ChatGPT proof window with explicit product-surface metadata'
    elif missing_required:
        readiness = 'hold-for-platform-clarification'
        reason = 'proof exists, but the product surface, runtime shell, or form factor is still too fuzzy to phrase honestly'
        tier = str(browser_eval.get('recommended_support_record_tier') or 'experimental')
        next_action = 'preserve one explicit product-surface signature per proof window before widening support language'
    else:
        upstream_tier = str(browser_eval.get('recommended_support_record_tier') or 'experimental')
        if len(profiles) >= 2 and upstream_tier == 'provisional':
            readiness = 'provisional-platform-envelope'
            reason = 'repeated proof windows stay on one coherent product surface, so the support story can stay provisionally platform-bound'
            tier = 'provisional'
            next_action = 'keep support wording bound to this product surface until separate desktop web, mobile web, Windows, macOS, iOS, or Android proof exists'
        else:
            readiness = 'experimental-platform-envelope'
            reason = 'one reviewable platform-scoped proof window exists, but repeated proof or stronger upstream scope is still limited'
            tier = 'experimental'
            next_action = 'repeat the same route-first proof on a second window of the same platform profile before strengthening support language'

    envelope = _platform_envelope(profiles, max_tier=tier, caution_flags=caution_flags)
    return {
        'project': 'GlassTTY',
        'surface_key': 'chatgpt',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'platform_envelope_evaluation_kind': 'chatgpt-routefirst-platform-envelope',
        'browser_evaluation': browser_eval,
        'window_platform_profiles': profiles,
        'field_scorecard': scorecard,
        'present_check_keys': present_checks,
        'missing_required_check_keys': missing_required,
        'missing_optional_check_keys': missing_optional,
        'platform_envelope_readiness': readiness,
        'platform_envelope_readiness_reason': reason,
        'recommended_support_record_tier': tier,
        'caution_flags': caution_flags,
        'platform_envelope': envelope,
        'recommended_next_action': next_action,
        'source_keys': spec.get('source_keys') or [],
    }


def _summary_markdown(payload: Payload) -> str:
    lines = ['# ChatGPT platform envelope receipt', '', f"- generated_at: `{payload.get('generated_at')}`", f"- target support tier: `{payload.get('target_support_tier')}`", '', '## Platform envelope axes', '']
    for item in payload.get('platform_envelope_axes') or []:
        lines.append(f"- {item.get('axis')}: {item.get('rule')}")
    lines.extend(['', '## Platform envelope readiness states', ''])
    for item in payload.get('platform_envelope_readiness_states') or []:
        lines.append(f"- {item.get('state')}: {item.get('rule')}")
    lines.append('')
    return '\n'.join(lines)


def build_chatgpt_platform_envelope_receipt(*, root: Path = ROOT) -> Payload:
    browser_spec = build_chatgpt_browser_envelope_receipt(root=root)
    payload = {
        'project': 'GlassTTY',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'surface_key': 'chatgpt',
        'purpose': 'bound the strongest honest ChatGPT product-surface envelope so repeated desktop web proof does not silently expand into Windows app, macOS app, iOS, Android, or mobile-web support',
        'target_support_tier': 'provisional',
        'design_principles': [
            'Desktop web proof should stay distinct from desktop app, mobile app, and mobile-web proof until those product surfaces have their own evidence.',
            'Platform surface, runtime shell, and form factor should remain visible because ChatGPT features and parity can vary across web, desktop-app, and mobile-app surfaces.',
            'The platform envelope should narrow what current proof covers rather than silently inheriting a broader cross-device support story from one successful browser lane.',
        ],
        'platform_envelope_axes': [
            {'axis': 'product-surface', 'rule': 'desktop web, mobile web, Windows app, macOS app, iOS app, and Android app proof should remain distinct support envelopes'},
            {'axis': 'runtime-shell', 'rule': 'chatgpt.com web and native desktop or mobile shells should remain explicit instead of inheriting parity by default'},
            {'axis': 'form-factor', 'rule': 'desktop, tablet, and phone proof should remain distinct until each has explicit evidence'},
            {'axis': 'parity-story', 'rule': 'feature parity differences across surfaces should remain outside the support wording unless the product surface is named explicitly'},
        ],
        'platform_envelope_readiness_states': [
            {'state': 'provisional-platform-envelope', 'rule': 'repeated proof windows justify only a provisional platform-bound support envelope'},
            {'state': 'experimental-platform-envelope', 'rule': 'current evidence can justify only an experimental platform-bound support envelope'},
            {'state': 'hold-for-platform-clarification', 'rule': 'proof exists, but the product surface, runtime shell, or form factor is still too fuzzy to phrase honestly'},
            {'state': 'investigated-only', 'rule': 'planning or thin proof artifacts exist, but they do not yet justify a live platform envelope'},
            {'state': 'planning-only', 'rule': 'the receipt still describes platform-boundary discipline rather than current live evidence'},
            {'state': 'stop', 'rule': 'the supplied proof windows mix incompatible product surfaces and should be split into separate evidence lanes'},
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
            'chatgpt-home-page', 'chatgpt-apps-with-sync', 'chatgpt-company-knowledge', 'chatgpt-tasks', 'chatgpt-windows-app', 'chatgpt-subscription-another-device', 'playwright-emulation', 'playwright-projects'
        ])),
    }
    payload['summary_markdown'] = _summary_markdown(payload)
    return payload


def capture_chatgpt_platform_envelope_receipt(*, root: Path = ROOT, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH) -> Payload:
    payload = build_chatgpt_platform_envelope_receipt(root=root)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / 'chatgpt-platform-envelope-receipt.json'
    summary_path = output_dir / 'SUMMARY.md'
    _write_json(json_path, payload)
    summary_path.write_text(payload.get('summary_markdown', ''), encoding='utf-8')
    entries = _history_entries(history_path)
    previous = entries[-1] if entries else None
    current = {'captured_at': payload.get('generated_at'), 'path': str(json_path), 'summary_path': str(summary_path), 'surface_key': payload.get('surface_key'), 'source_key_count': len(payload.get('source_keys') or []), 'readiness_state_count': len(payload.get('platform_envelope_readiness_states') or [])}
    current['changed_fields'] = _changed_fields(previous, current)
    entries.append(current)
    _write_json(history_path, _history_payload(entries))
    return {'receipt': payload, 'history_update': {'path': str(history_path), 'capture_count_after_write': len(entries), 'changed_fields_vs_previous': current['changed_fields']}}


def write_root_chatgpt_platform_envelope_receipt(*, root: Path = ROOT) -> Payload:
    payload = build_chatgpt_platform_envelope_receipt(root=root)
    _write_json(root / ROOT_OUTPUT_PATH.name, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Build or evaluate the ChatGPT platform envelope receipt.')
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
        print(json.dumps(capture_chatgpt_platform_envelope_receipt(root=ROOT, output_dir=Path(args.output_dir), history_path=Path(args.history_path)), indent=2 if args.pretty else None)); return
    if args.command == 'history':
        print(json.dumps(summarize_capture_history(Path(args.history_path)), indent=2 if args.pretty else None)); return
    if args.command == 'write-root':
        print(json.dumps(write_root_chatgpt_platform_envelope_receipt(root=ROOT), indent=2 if args.pretty else None)); return
    if args.command == 'evaluate':
        print(json.dumps(evaluate_chatgpt_platform_envelope_receipt(_read_json(Path(args.promotion)), root=ROOT), indent=2 if args.pretty else None)); return
    print(json.dumps(build_chatgpt_platform_envelope_receipt(root=ROOT), indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()
