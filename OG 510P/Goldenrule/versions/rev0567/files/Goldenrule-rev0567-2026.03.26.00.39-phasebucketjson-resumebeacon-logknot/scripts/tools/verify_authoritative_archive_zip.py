#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts' / 'tools'))
from audit_archive_zip_lineage import _default_scan_dir
from inspect_authoritative_archive_zip import inspect_authoritative_archive_zip
from resolve_authoritative_archive_zip import resolve_authoritative_archive_zip


def build_verification(scan_dir: Path) -> dict[str, Any]:
    resolved = resolve_authoritative_archive_zip(scan_dir)
    inspected = inspect_authoritative_archive_zip(scan_dir)
    selected = inspected.get('selected_zip')
    current = resolved.get('current_archive', {})
    head = resolved.get('authoritative_external_head', {})
    recommended = resolved.get('recommended_resume', {})

    checks: list[dict[str, Any]] = []

    def add(name: str, ok: bool, detail: Any) -> None:
        checks.append({'name': name, 'ok': bool(ok), 'detail': detail})

    add('scan_dir_exists', scan_dir.exists(), scan_dir.as_posix())
    add('scan_dir_is_dir', scan_dir.is_dir(), scan_dir.as_posix())
    add('resolved_current_archive_present', bool(current), current.get('root_name'))
    add('resolved_authoritative_external_head_present', bool(head), head.get('zip_name'))
    add('selected_zip_present', selected is not None, None if selected is None else selected.get('zip_name'))

    selected_path = None if selected is None else Path(selected['zip_path'])
    add('selected_zip_path_exists', selected_path is not None and selected_path.exists(), None if selected_path is None else selected_path.as_posix())
    add('selected_zip_path_is_file', selected_path is not None and selected_path.is_file(), None if selected_path is None else selected_path.as_posix())
    add('selected_zip_name_matches_path', selected is not None and selected_path is not None and selected_path.name == selected['zip_name'], None if selected is None else selected.get('zip_name'))
    add('selected_zip_name_matches_recommended_resume', selected is not None and selected.get('zip_name') == recommended.get('selected_zip_name'), {'selected': None if selected is None else selected.get('zip_name'), 'recommended': recommended.get('selected_zip_name')})
    add('selected_zip_path_matches_recommended_resume', selected is not None and selected.get('zip_path') == recommended.get('selected_zip_path'), {'selected': None if selected is None else selected.get('zip_path'), 'recommended': recommended.get('selected_zip_path')})
    add('selected_zip_name_matches_authoritative_head', selected is not None and selected.get('zip_name') == head.get('zip_name'), {'selected': None if selected is None else selected.get('zip_name'), 'head': head.get('zip_name')})
    add('selected_zip_revision_matches_authoritative_head', bool(current) and bool(head) and current.get('revision') == head.get('revision'), {'current_revision': current.get('revision'), 'head_revision': head.get('revision')})
    add('exact_current_zip_present', bool(resolved.get('exact_current_zip_present')), resolved.get('exact_current_zip_present'))
    add('current_root_vs_authoritative_head_aligned', bool(resolved.get('current_root_vs_authoritative_head_aligned')), resolved.get('current_root_vs_authoritative_head_aligned'))
    add('selected_zip_size_positive', selected is not None and int(selected.get('size_bytes', 0)) > 0, None if selected is None else selected.get('size_bytes'))
    add('selected_zip_sha256_length', selected is not None and len(str(selected.get('sha256', ''))) == 64, None if selected is None else selected.get('sha256'))

    def run_emit(flag: str) -> tuple[bool, str]:
        proc = subprocess.run(
            ['python3', 'scripts/tools/inspect_authoritative_archive_zip.py', '--scan-dir', scan_dir.as_posix(), '--emit', flag],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        return proc.returncode == 0, proc.stdout.strip() if proc.returncode == 0 else (proc.stderr.strip() or proc.stdout.strip())

    ok, out = run_emit('zip-path')
    add('emit_zip_path_command_ok', ok, out)
    add('emit_zip_path_matches_selected', ok and selected is not None and out == selected.get('zip_path'), {'emitted': out, 'selected': None if selected is None else selected.get('zip_path')})
    ok, out = run_emit('zip-name')
    add('emit_zip_name_command_ok', ok, out)
    add('emit_zip_name_matches_selected', ok and selected is not None and out == selected.get('zip_name'), {'emitted': out, 'selected': None if selected is None else selected.get('zip_name')})
    ok, out = run_emit('size-bytes')
    add('emit_size_bytes_command_ok', ok, out)
    add('emit_size_bytes_matches_selected', ok and selected is not None and out == str(selected.get('size_bytes')), {'emitted': out, 'selected': None if selected is None else str(selected.get('size_bytes'))})
    ok, out = run_emit('sha256')
    add('emit_sha256_command_ok', ok, out)
    add('emit_sha256_matches_selected', ok and selected is not None and out == selected.get('sha256'), {'emitted': out, 'selected': None if selected is None else selected.get('sha256')})

    failed = [row for row in checks if not row['ok']]
    return {
        'tool': 'verify_authoritative_archive_zip',
        'root_name': ROOT.name,
        'scan_dir': scan_dir.as_posix(),
        'selected_zip': selected,
        'current_archive': current,
        'authoritative_external_head': head,
        'recommended_resume': recommended,
        'check_count': len(checks),
        'checks': checks,
        'failed_checks': failed,
        'all_ok': not failed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Verify that the authoritative sibling Golden Rule zip exists and still matches the live authority rule, selected path, and bytes.')
    parser.add_argument('--scan-dir', default=_default_scan_dir().as_posix(), help='directory containing sibling Golden Rule revision zips')
    parser.add_argument('--emit', choices=['json', 'summary', 'status'], default='summary')
    args = parser.parse_args()
    scan_dir = Path(args.scan_dir).expanduser().resolve()
    try:
        payload = build_verification(scan_dir)
    except Exception as exc:  # noqa: BLE001
        print(f'verify-authoritative-archive-zip: {exc}', file=sys.stderr)
        return 1

    if args.emit == 'json':
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write('\n')
    elif args.emit == 'status':
        sys.stdout.write('ok\n' if payload['all_ok'] else 'drift\n')
    else:
        if payload['all_ok']:
            print(
                'authoritative-archive-zip-verify: ok '
                f"(checks={payload['check_count']} zip={payload['selected_zip']['zip_name']} sha256={payload['selected_zip']['sha256']})"
            )
        else:
            print(
                'authoritative-archive-zip-verify: drift '
                f"(failed={len(payload['failed_checks'])} checks={payload['check_count']})",
                file=sys.stderr,
            )
    return 0 if payload['all_ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
