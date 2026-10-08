#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from doctor import build_report as build_doctor_report
from native_host_report import build_report as build_native_host_report
from profile_metadata import capture_history_path, profile_dir, summarize_capture_history, summarize_profile

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_ROOT = ROOT / 'validation' / 'latest'
PROFILE_LOCAL_ARTIFACTS = [
    'glasstty-profile.json',
    'glasstty-native-host.json',
    'DevToolsActivePort',
    'glasstty-mv3-worker-resume.json',
    'glasstty-mv3-worker-resume-summary.json',
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _saved_browser_path(profile_info: dict[str, Any]) -> str | None:
    last_launch = profile_info.get('last_launch') if isinstance(profile_info.get('last_launch'), dict) else None
    if not isinstance(last_launch, dict):
        return None
    chromium_bin = last_launch.get('chromium_bin')
    if isinstance(chromium_bin, str) and chromium_bin.strip():
        return chromium_bin.strip()
    browser = last_launch.get('browser') if isinstance(last_launch.get('browser'), dict) else None
    path = browser.get('path') if isinstance(browser, dict) else None
    return path.strip() if isinstance(path, str) and path.strip() else None


def _effective_browser_path(profile_info: dict[str, Any]) -> str | None:
    for key in ('reopen_plan', 'reopen_debug_plan'):
        plan = profile_info.get(key) if isinstance(profile_info.get(key), dict) else None
        browser = plan.get('effective_browser') if isinstance(plan, dict) and isinstance(plan.get('effective_browser'), dict) else None
        path = browser.get('path') if isinstance(browser, dict) else None
        if isinstance(path, str) and path.strip():
            return path.strip()
    return _saved_browser_path(profile_info)


def _copy_profile_local_artifacts(profile_path: Path, output_dir: Path) -> list[dict[str, Any]]:
    raw_dir = output_dir / 'profile-artifacts'
    raw_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    for name in PROFILE_LOCAL_ARTIFACTS:
        source = profile_path / name
        target = raw_dir / name
        entry: dict[str, Any] = {
            'name': name,
            'source_path': str(source),
            'copied_path': str(target),
            'exists': source.exists(),
        }
        if source.exists():
            shutil.copy2(source, target)
            entry['copied'] = True
        else:
            entry['copied'] = False
        results.append(entry)
    return results


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _capture_entry_from_bundle(bundle: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    profile = bundle.get('profile') if isinstance(bundle.get('profile'), dict) else {}
    cdp_hint = profile.get('cdp_endpoint_hint') if isinstance(profile.get('cdp_endpoint_hint'), dict) else {}
    resume_summary = profile.get('mv3_resume_summary') if isinstance(profile.get('mv3_resume_summary'), dict) else {}
    reopen_plan = profile.get('reopen_plan') if isinstance(profile.get('reopen_plan'), dict) else {}
    return {
        'captured_at': bundle.get('captured_at'),
        'profile_name': profile.get('name'),
        'output_dir': str(output_dir),
        'bundle_summary_path': str(output_dir / 'bundle-summary.json'),
        'summary_markdown_path': str(output_dir / 'SUMMARY.md'),
        'attach_ready': cdp_hint.get('attach_ready'),
        'cdp_endpoint': cdp_hint.get('preferred_endpoint'),
        'saved_browser_path': bundle.get('saved_browser_path'),
        'effective_browser_path': bundle.get('effective_browser_path'),
        'resume_proof_grade': resume_summary.get('proof_grade'),
        'resume_captured_at': resume_summary.get('captured_at'),
        'reopen_launchable_now': reopen_plan.get('launchable_now'),
        'doctor_hint_count': len(bundle.get('doctor', {}).get('hints') or []) if isinstance(bundle.get('doctor'), dict) else None,
        'copied_artifact_names': [item.get('name') for item in (bundle.get('copied_profile_artifacts') or []) if isinstance(item, dict) and item.get('copied')],
    }


def _read_capture_history_file(profile_path: Path) -> dict[str, Any] | None:
    path = capture_history_path(profile_path)
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError:
        return None
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _load_capture_entries(profile_path: Path) -> list[dict[str, Any]]:
    payload = _read_capture_history_file(profile_path)
    entries = payload.get('entries') if isinstance(payload, dict) else None
    return [entry for entry in entries if isinstance(entry, dict)] if isinstance(entries, list) else []


def _comparison_to_previous(previous: dict[str, Any] | None, current: dict[str, Any]) -> dict[str, Any]:
    comparison: dict[str, Any] = {
        'has_previous_capture': isinstance(previous, dict),
        'previous_captured_at': previous.get('captured_at') if isinstance(previous, dict) else None,
        'current_captured_at': current.get('captured_at'),
        'changed_fields': [],
    }
    if not isinstance(previous, dict):
        comparison['summary'] = 'no previous capture exists for this profile yet'
        return comparison

    tracked = {
        'attach_ready': (previous.get('attach_ready'), current.get('attach_ready')),
        'cdp_endpoint': (previous.get('cdp_endpoint'), current.get('cdp_endpoint')),
        'saved_browser_path': (previous.get('saved_browser_path'), current.get('saved_browser_path')),
        'effective_browser_path': (previous.get('effective_browser_path'), current.get('effective_browser_path')),
        'resume_proof_grade': (previous.get('resume_proof_grade'), current.get('resume_proof_grade')),
        'reopen_launchable_now': (previous.get('reopen_launchable_now'), current.get('reopen_launchable_now')),
        'output_dir': (previous.get('output_dir'), current.get('output_dir')),
    }
    for key, (before, after) in tracked.items():
        changed = before != after
        comparison[f'{key}_before'] = before
        comparison[f'{key}_after'] = after
        comparison[f'{key}_changed'] = changed
        if changed:
            comparison['changed_fields'].append(key)
    comparison['summary'] = 'capture drift detected' if comparison['changed_fields'] else 'capture matches the previous profile snapshot on the tracked fields'
    return comparison


def _history_payload(profile_name: str, profile_path: Path, entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        'schema_version': 1,
        'profile_name': profile_name,
        'profile_path': str(profile_path),
        'updated_at': utc_now_iso(),
        'capture_count': len(entries),
        'entries': entries,
    }


def _update_capture_history(profile_name: str, profile_path: Path, current_entry: dict[str, Any]) -> dict[str, Any]:
    entries = _load_capture_entries(profile_path)
    previous = entries[-1] if entries else None
    entries.append(current_entry)
    payload = _history_payload(profile_name, profile_path, entries)
    _write_json(capture_history_path(profile_path), payload)
    return {
        'path': str(capture_history_path(profile_path)),
        'capture_count_after_write': len(entries),
        'latest_capture': current_entry,
        'previous_capture': previous,
        'history': payload,
    }


def _render_summary_markdown(bundle: dict[str, Any]) -> str:
    profile = bundle['profile']
    commands = profile.get('commands') if isinstance(profile.get('commands'), dict) else {}
    cdp_hint = profile.get('cdp_endpoint_hint') if isinstance(profile.get('cdp_endpoint_hint'), dict) else {}
    reopen_plan = profile.get('reopen_plan') if isinstance(profile.get('reopen_plan'), dict) else {}
    resume_summary = profile.get('mv3_resume_summary') if isinstance(profile.get('mv3_resume_summary'), dict) else None
    native_saved = bundle.get('native_host_saved_browser') if isinstance(bundle.get('native_host_saved_browser'), dict) else None
    native_effective = bundle.get('native_host_effective_browser') if isinstance(bundle.get('native_host_effective_browser'), dict) else None
    capture_history = bundle.get('capture_history') if isinstance(bundle.get('capture_history'), dict) else {}
    comparison = bundle.get('comparison_to_previous_capture') if isinstance(bundle.get('comparison_to_previous_capture'), dict) else {}
    lines = [
        f"# GlassTTY profile capture: {profile.get('name')}",
        '',
        f"- captured_at: {bundle.get('captured_at')}",
        f"- profile_path: {profile.get('path')}",
        f"- attach_ready: {cdp_hint.get('attach_ready')}",
        f"- cdp_endpoint: {cdp_hint.get('preferred_endpoint')}",
        f"- reopen_launchable_now: {reopen_plan.get('launchable_now')}",
        f"- saved_browser_path: {bundle.get('saved_browser_path')}",
        f"- effective_browser_path: {bundle.get('effective_browser_path')}",
        f"- capture_history_count: {capture_history.get('capture_count_after_write')}",
    ]
    if resume_summary:
        lines.extend([
            f"- mv3_resume_proof_grade: {resume_summary.get('proof_grade')}",
            f"- mv3_resume_captured_at: {resume_summary.get('captured_at')}",
        ])
    lines.extend([
        '',
        '## Capture history',
        '',
        f"- ledger_path: `{capture_history.get('path')}`",
        f"- comparison_summary: {comparison.get('summary')}",
    ])
    if comparison.get('changed_fields'):
        lines.append(f"- changed_fields: {', '.join(str(item) for item in comparison.get('changed_fields') or [])}")
    lines.extend([
        '',
        '## Recommended commands',
        '',
    ])
    for key in ('info', 'captures', 'capture', 'reopen', 'reopen_portable', 'reopen_debug', 'reopen_debug_portable', 'resume_proof'):
        value = commands.get(key)
        if value:
            lines.append(f'- {key}: `{value}`')
    if native_saved:
        saved_install = native_saved.get('suggested_install_command') or next(iter(native_saved.get('suggested_install_commands') or []), None)
        if saved_install:
            lines.extend(['', '## Saved-browser native-host follow-up', '', f'- `{saved_install}`'])
    if native_effective:
        effective_install = native_effective.get('suggested_install_command') or next(iter(native_effective.get('suggested_install_commands') or []), None)
        saved_install = (native_saved or {}).get('suggested_install_command') or next(iter((native_saved or {}).get('suggested_install_commands') or []), None)
        if effective_install and effective_install != saved_install:
            lines.extend(['', '## Effective-browser native-host follow-up', '', f'- `{effective_install}`'])
    lines.extend([
        '',
        '## Bundle files',
        '',
        '- `bundle-summary.json`',
        '- `profile-info.json`',
        '- `doctor.json`',
        '- `native-host-current-browser.json`',
        '- `capture-history.json`',
        '- `capture-diff.json`',
    ])
    if native_saved:
        lines.append('- `native-host-saved-browser.json`')
    if native_effective:
        lines.append('- `native-host-effective-browser.json`')
    lines.append('- `profile-artifacts/`')
    return '\n'.join(lines) + '\n'


def build_capture_bundle(profile_name: str, *, output_dir: Path) -> dict[str, Any]:
    profile_path = profile_dir(profile_name)
    info = summarize_profile(profile_path)
    if not info.get('exists'):
        raise FileNotFoundError(f'profile {profile_name!r} does not exist under GLASSTTY_HOME')

    output_dir.mkdir(parents=True, exist_ok=True)
    doctor = build_doctor_report()
    saved_browser_path = _saved_browser_path(info)
    effective_browser_path = _effective_browser_path(info)
    native_current = build_native_host_report()
    native_saved = build_native_host_report(browser_bin=saved_browser_path) if saved_browser_path else None
    native_effective = build_native_host_report(browser_bin=effective_browser_path) if effective_browser_path else None
    copied = _copy_profile_local_artifacts(Path(info['path']), output_dir)

    bundle: dict[str, Any] = {
        'captured_at': utc_now_iso(),
        'profile': info,
        'doctor': doctor,
        'native_host_current_browser': native_current,
        'native_host_saved_browser': native_saved,
        'native_host_effective_browser': native_effective,
        'saved_browser_path': saved_browser_path,
        'effective_browser_path': effective_browser_path,
        'copied_profile_artifacts': copied,
        'paths': {
            'profile_info': str(output_dir / 'profile-info.json'),
            'doctor': str(output_dir / 'doctor.json'),
            'native_host_current_browser': str(output_dir / 'native-host-current-browser.json'),
            'native_host_saved_browser': str(output_dir / 'native-host-saved-browser.json') if native_saved else None,
            'native_host_effective_browser': str(output_dir / 'native-host-effective-browser.json') if native_effective else None,
            'capture_history': str(output_dir / 'capture-history.json'),
            'capture_diff': str(output_dir / 'capture-diff.json'),
            'bundle_summary': str(output_dir / 'bundle-summary.json'),
            'summary_markdown': str(output_dir / 'SUMMARY.md'),
        },
    }
    current_entry = _capture_entry_from_bundle(bundle, output_dir)
    history = _update_capture_history(profile_name, profile_path, current_entry)
    comparison = _comparison_to_previous(history.get('previous_capture') if isinstance(history, dict) else None, current_entry)
    bundle['capture_history'] = history
    bundle['comparison_to_previous_capture'] = comparison

    _write_json(output_dir / 'profile-info.json', summarize_profile(profile_path))
    _write_json(output_dir / 'doctor.json', doctor)
    _write_json(output_dir / 'native-host-current-browser.json', native_current)
    if native_saved is not None:
        _write_json(output_dir / 'native-host-saved-browser.json', native_saved)
    if native_effective is not None:
        _write_json(output_dir / 'native-host-effective-browser.json', native_effective)
    _write_json(output_dir / 'capture-history.json', history.get('history'))
    _write_json(output_dir / 'capture-diff.json', comparison)
    _write_json(output_dir / 'bundle-summary.json', bundle)
    (output_dir / 'SUMMARY.md').write_text(_render_summary_markdown(bundle), encoding='utf-8')
    return bundle


def main() -> None:
    parser = argparse.ArgumentParser(description='Capture a durable GlassTTY profile evidence bundle for later handoff or live-proof review.')
    parser.add_argument('profile', help='GlassTTY profile name to capture')
    parser.add_argument('--output-dir', help='Directory to write the bundle into (default: validation/latest/profile-capture-<name>)')
    parser.add_argument('--history-only', action='store_true', help='Print the profile-local capture ledger summary instead of writing a new bundle')
    parser.add_argument('--pretty', action='store_true', help='Pretty-print the final JSON to stdout')
    args = parser.parse_args()

    if args.history_only:
        payload = summarize_capture_history(profile_dir(args.profile))
    else:
        output_dir = Path(args.output_dir).expanduser() if args.output_dir else DEFAULT_OUTPUT_ROOT / f'profile-capture-{args.profile}'
        payload = build_capture_bundle(args.profile, output_dir=output_dir)
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()
