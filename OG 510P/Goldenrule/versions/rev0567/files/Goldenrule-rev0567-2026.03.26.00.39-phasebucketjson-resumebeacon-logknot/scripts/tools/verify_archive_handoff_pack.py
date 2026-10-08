#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'archive_handoff_pack.json'


def _canonical_sha256(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_verification() -> dict[str, Any]:
    if not REPORT_PATH.exists():
        raise FileNotFoundError(REPORT_PATH.relative_to(ROOT).as_posix())
    report = json.loads(REPORT_PATH.read_text(encoding='utf-8'))
    manifest_entries = report.get('manifest_entries', [])
    mismatches: list[dict[str, Any]] = []
    missing_paths: list[str] = []
    verified_entries: list[dict[str, Any]] = []
    for entry in manifest_entries:
        rel = str(entry['path'])
        path = ROOT / rel
        if not path.exists():
            missing_paths.append(rel)
            continue
        actual_bytes = path.stat().st_size
        actual_sha256 = _sha256(path)
        expected_bytes = int(entry['bytes'])
        expected_sha256 = str(entry['sha256'])
        if actual_bytes != expected_bytes or actual_sha256 != expected_sha256:
            mismatches.append(
                {
                    'path': rel,
                    'kind': entry.get('kind'),
                    'expected_bytes': expected_bytes,
                    'actual_bytes': actual_bytes,
                    'expected_sha256': expected_sha256,
                    'actual_sha256': actual_sha256,
                }
            )
            continue
        verified_entries.append(
            {
                'path': rel,
                'kind': entry.get('kind'),
                'bytes': actual_bytes,
                'sha256': actual_sha256,
                'group_id': entry.get('group_id'),
            }
        )

    manifest_sha256_actual = _canonical_sha256(manifest_entries)
    manifest_sha256_expected = str(report.get('pack_totals', {}).get('manifest_sha256', ''))
    manifest_sha256_matches = manifest_sha256_actual == manifest_sha256_expected
    all_ok = not missing_paths and not mismatches and manifest_sha256_matches
    return {
        'tool': 'verify_archive_handoff_pack',
        'root_name': ROOT.name,
        'report_path': REPORT_PATH.relative_to(ROOT).as_posix(),
        'primary_open_path': report.get('primary_open_path'),
        'primary_verify_command': report.get('primary_verify_command'),
        'handoff_pack_verify_command': 'python3 scripts/tools/verify_archive_handoff_pack.py',
        'manifest_file_count': len(manifest_entries),
        'verified_file_count': len(verified_entries),
        'missing_path_count': len(missing_paths),
        'mismatch_count': len(mismatches),
        'manifest_sha256_expected': manifest_sha256_expected,
        'manifest_sha256_actual': manifest_sha256_actual,
        'manifest_sha256_matches': manifest_sha256_matches,
        'missing_paths': missing_paths,
        'mismatches': mismatches,
        'verified_entries': verified_entries,
        'all_ok': all_ok,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Verify that the archive handoff pack manifest still matches the retained control-plane files.')
    parser.add_argument('--emit', choices=['json', 'summary', 'status'], default='summary')
    args = parser.parse_args()

    payload = build_verification()
    if args.emit == 'json':
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write('\n')
    elif args.emit == 'status':
        sys.stdout.write('ok\n' if payload['all_ok'] else 'drift\n')
    else:
        if payload['all_ok']:
            print(
                'archive-handoff-pack-verify: ok '
                f"(files={payload['verified_file_count']} manifest_sha256={payload['manifest_sha256_actual']})"
            )
        else:
            print(
                'archive-handoff-pack-verify: drift '
                f"(missing={payload['missing_path_count']} mismatches={payload['mismatch_count']} manifest_ok={payload['manifest_sha256_matches']})",
                file=sys.stderr,
            )
    return 0 if payload['all_ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
