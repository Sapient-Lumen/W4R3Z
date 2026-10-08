#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from doctor import build_report as build_doctor_report
from profile_metadata import fleet_capture_history_path, summarize_fleet_capture_history, summarize_profiles, triage_profiles

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_ROOT = ROOT / 'validation' / 'latest'


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _compact_ranked_profile(item: dict[str, Any]) -> dict[str, Any]:
    return {
        'name': item.get('name'),
        'tier': item.get('tier'),
        'score': item.get('score'),
        'next_command': item.get('next_command'),
        'next_step': item.get('next_step'),
        'attach_ready': item.get('attach_ready'),
        'capture_count': item.get('capture_count'),
        'proof_grade': item.get('proof_grade'),
        'used_discovered_browser_fallback': item.get('used_discovered_browser_fallback'),
        'warnings': list(item.get('warnings') or []),
    }


def _snapshot_entry_from_bundle(bundle: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    triage = bundle.get('triage') if isinstance(bundle.get('triage'), dict) else {}
    ranked = [item for item in (triage.get('ranked_profiles') or []) if isinstance(item, dict)]
    best = triage.get('best_profile') if isinstance(triage.get('best_profile'), dict) else {}
    compact_ranked = [_compact_ranked_profile(item) for item in ranked]
    attach_ready_count = sum(1 for item in ranked if item.get('attach_ready'))
    return {
        'captured_at': bundle.get('captured_at'),
        'output_dir': str(output_dir),
        'bundle_summary_path': str(output_dir / 'bundle-summary.json'),
        'summary_markdown_path': str(output_dir / 'SUMMARY.md'),
        'profile_count': triage.get('profile_count'),
        'attach_ready_count': attach_ready_count,
        'best_profile_name': best.get('name'),
        'best_profile_tier': best.get('tier'),
        'best_profile_score': best.get('score'),
        'best_next_command': best.get('next_command'),
        'doctor_hint_count': len(bundle.get('doctor', {}).get('hints') or []) if isinstance(bundle.get('doctor'), dict) else None,
        'ranked_profiles': compact_ranked,
    }


def _read_history_file() -> dict[str, Any] | None:
    path = fleet_capture_history_path()
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError:
        return None
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _load_history_entries() -> list[dict[str, Any]]:
    payload = _read_history_file()
    entries = payload.get('entries') if isinstance(payload, dict) else None
    return [entry for entry in entries if isinstance(entry, dict)] if isinstance(entries, list) else []


def _history_payload(entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        'schema_version': 1,
        'updated_at': utc_now_iso(),
        'capture_count': len(entries),
        'entries': entries,
    }


def _update_history(current_entry: dict[str, Any]) -> dict[str, Any]:
    path = fleet_capture_history_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    entries = _load_history_entries()
    previous = entries[-1] if entries else None
    entries.append(current_entry)
    payload = _history_payload(entries)
    _write_json(path, payload)
    return {
        'path': str(path),
        'capture_count_after_write': len(entries),
        'latest_capture': current_entry,
        'previous_capture': previous,
        'history': payload,
    }


def _comparison_to_previous(previous: dict[str, Any] | None, current: dict[str, Any]) -> dict[str, Any]:
    comparison: dict[str, Any] = {
        'has_previous_capture': isinstance(previous, dict),
        'previous_captured_at': previous.get('captured_at') if isinstance(previous, dict) else None,
        'current_captured_at': current.get('captured_at'),
        'changed_fields': [],
    }
    if not isinstance(previous, dict):
        comparison['summary'] = 'no previous fleet snapshot exists yet'
        return comparison

    tracked = {
        'profile_count': (previous.get('profile_count'), current.get('profile_count')),
        'attach_ready_count': (previous.get('attach_ready_count'), current.get('attach_ready_count')),
        'best_profile_name': (previous.get('best_profile_name'), current.get('best_profile_name')),
        'best_profile_tier': (previous.get('best_profile_tier'), current.get('best_profile_tier')),
        'best_profile_score': (previous.get('best_profile_score'), current.get('best_profile_score')),
        'best_next_command': (previous.get('best_next_command'), current.get('best_next_command')),
    }
    for key, (before, after) in tracked.items():
        changed = before != after
        comparison[f'{key}_before'] = before
        comparison[f'{key}_after'] = after
        comparison[f'{key}_changed'] = changed
        if changed:
            comparison['changed_fields'].append(key)

    previous_ranked = {str(item.get('name')): item for item in (previous.get('ranked_profiles') or []) if isinstance(item, dict) and item.get('name')}
    current_ranked = {str(item.get('name')): item for item in (current.get('ranked_profiles') or []) if isinstance(item, dict) and item.get('name')}
    previous_names = sorted(previous_ranked)
    current_names = sorted(current_ranked)
    added = [name for name in current_names if name not in previous_ranked]
    removed = [name for name in previous_names if name not in current_ranked]
    per_profile_changes: list[dict[str, Any]] = []
    for name in sorted(set(previous_names) & set(current_names)):
        before = previous_ranked[name]
        after = current_ranked[name]
        changed: dict[str, Any] = {'name': name, 'changed_fields': []}
        for key in ('tier', 'score', 'next_command', 'attach_ready', 'capture_count', 'proof_grade', 'used_discovered_browser_fallback'):
            if before.get(key) != after.get(key):
                changed[f'{key}_before'] = before.get(key)
                changed[f'{key}_after'] = after.get(key)
                changed['changed_fields'].append(key)
        if changed['changed_fields']:
            per_profile_changes.append(changed)

    comparison['added_profiles'] = added
    comparison['removed_profiles'] = removed
    comparison['per_profile_changes'] = per_profile_changes
    if added:
        comparison['changed_fields'].append('added_profiles')
    if removed:
        comparison['changed_fields'].append('removed_profiles')
    if per_profile_changes:
        comparison['changed_fields'].append('per_profile_changes')
    comparison['summary'] = 'fleet drift detected' if comparison['changed_fields'] else 'fleet snapshot matches the previous one on tracked fields'
    return comparison


def _render_summary_markdown(bundle: dict[str, Any]) -> str:
    triage = bundle.get('triage') if isinstance(bundle.get('triage'), dict) else {}
    best = triage.get('best_profile') if isinstance(triage.get('best_profile'), dict) else {}
    ranked = [item for item in (triage.get('ranked_profiles') or []) if isinstance(item, dict)]
    history = bundle.get('fleet_capture_history') if isinstance(bundle.get('fleet_capture_history'), dict) else {}
    comparison = bundle.get('comparison_to_previous_capture') if isinstance(bundle.get('comparison_to_previous_capture'), dict) else {}
    commands = triage.get('commands') if isinstance(triage.get('commands'), dict) else {}
    lines = [
        '# GlassTTY profile fleet capture',
        '',
        f"- captured_at: {bundle.get('captured_at')}",
        f"- profile_count: {triage.get('profile_count')}",
        f"- best_profile: {best.get('name')}",
        f"- best_tier: {best.get('tier')}",
        f"- best_score: {best.get('score')}",
        f"- best_next_command: {best.get('next_command')}",
        f"- fleet_capture_count: {history.get('capture_count_after_write')}",
        '',
        '## Ranked profiles',
        '',
    ]
    for item in ranked:
        lines.append(f"- {item.get('name')}: tier={item.get('tier')} score={item.get('score')} next=`{item.get('next_command')}`")
    lines.extend([
        '',
        '## Fleet history',
        '',
        f"- ledger_path: `{history.get('path')}`",
        f"- comparison_summary: {comparison.get('summary')}",
    ])
    if comparison.get('added_profiles'):
        lines.append(f"- added_profiles: {', '.join(str(item) for item in comparison.get('added_profiles') or [])}")
    if comparison.get('removed_profiles'):
        lines.append(f"- removed_profiles: {', '.join(str(item) for item in comparison.get('removed_profiles') or [])}")
    if comparison.get('per_profile_changes'):
        changed_profiles = ', '.join(str(item.get('name')) for item in comparison.get('per_profile_changes') or [] if isinstance(item, dict) and item.get('name'))
        if changed_profiles:
            lines.append(f"- changed_profiles: {changed_profiles}")
    lines.extend([
        '',
        '## Recommended commands',
        '',
    ])
    for key in ('triage', 'fleet_capture', 'fleet_captures', 'doctor'):
        value = commands.get(key)
        if value:
            lines.append(f'- {key}: `{value}`')
    if best.get('next_command'):
        lines.append(f"- best_profile_next: `{best.get('next_command')}`")
    lines.extend([
        '',
        '## Bundle files',
        '',
        '- `fleet-triage.json`',
        '- `profiles.json`',
        '- `doctor.json`',
        '- `fleet-history.json`',
        '- `fleet-diff.json`',
        '- `bundle-summary.json`',
    ])
    return '\n'.join(lines) + '\n'


def build_fleet_capture_bundle(*, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    triage = triage_profiles()
    profiles = summarize_profiles()
    doctor = build_doctor_report()
    bundle: dict[str, Any] = {
        'captured_at': utc_now_iso(),
        'triage': triage,
        'profiles': profiles,
        'doctor': doctor,
        'paths': {
            'triage': str(output_dir / 'fleet-triage.json'),
            'profiles': str(output_dir / 'profiles.json'),
            'doctor': str(output_dir / 'doctor.json'),
            'history': str(output_dir / 'fleet-history.json'),
            'diff': str(output_dir / 'fleet-diff.json'),
            'bundle_summary': str(output_dir / 'bundle-summary.json'),
            'summary_markdown': str(output_dir / 'SUMMARY.md'),
        },
    }
    current_entry = _snapshot_entry_from_bundle(bundle, output_dir)
    history = _update_history(current_entry)
    comparison = _comparison_to_previous(history.get('previous_capture') if isinstance(history, dict) else None, current_entry)
    bundle['fleet_capture_history'] = history
    bundle['comparison_to_previous_capture'] = comparison
    _write_json(output_dir / 'fleet-triage.json', triage)
    _write_json(output_dir / 'profiles.json', profiles)
    _write_json(output_dir / 'doctor.json', doctor)
    _write_json(output_dir / 'fleet-history.json', history.get('history'))
    _write_json(output_dir / 'fleet-diff.json', comparison)
    _write_json(output_dir / 'bundle-summary.json', bundle)
    (output_dir / 'SUMMARY.md').write_text(_render_summary_markdown(bundle), encoding='utf-8')
    return bundle


def main() -> None:
    parser = argparse.ArgumentParser(description='Capture a durable GlassTTY fleet-level profile triage snapshot for later handoff or comparison.')
    parser.add_argument('--output-dir', help='Directory to write the bundle into (default: validation/latest/profile-fleet-capture)')
    parser.add_argument('--history-only', action='store_true', help='Print the fleet-level capture ledger summary instead of writing a new bundle')
    parser.add_argument('--pretty', action='store_true', help='Pretty-print the final JSON to stdout')
    args = parser.parse_args()

    if args.history_only:
        payload = summarize_fleet_capture_history()
    else:
        output_dir = Path(args.output_dir).expanduser() if args.output_dir else DEFAULT_OUTPUT_ROOT / 'profile-fleet-capture'
        payload = build_fleet_capture_bundle(output_dir=output_dir)
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()
