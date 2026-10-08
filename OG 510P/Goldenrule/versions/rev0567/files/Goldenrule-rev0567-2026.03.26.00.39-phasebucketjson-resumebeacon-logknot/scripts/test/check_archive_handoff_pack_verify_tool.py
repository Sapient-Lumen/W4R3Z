#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / 'scripts' / 'tools' / 'verify_archive_handoff_pack.py'
HANDOFF_REPORT = ROOT / 'artifacts' / 'reports' / 'archive_handoff_pack.json'


def fail(message: str) -> int:
    print(f'archive-handoff-pack-verify-tool: {message}', file=sys.stderr)
    return 1


def main() -> int:
    if not TOOL.exists():
        return fail('missing tool script')
    if not HANDOFF_REPORT.exists():
        return fail('missing archive_handoff_pack.json')

    proc = subprocess.run(
        ['python3', str(TOOL), '--emit', 'json'],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        if proc.stdout:
            print(proc.stdout, end='', file=sys.stderr)
        if proc.stderr:
            print(proc.stderr, end='', file=sys.stderr)
        return fail('tool returned non-zero on the settled tree')
    payload = json.loads(proc.stdout)
    if payload.get('tool') != 'verify_archive_handoff_pack':
        return fail('tool id drifted')
    if payload.get('handoff_pack_verify_command') != 'python3 scripts/tools/verify_archive_handoff_pack.py':
        return fail('verify command drifted')
    if payload.get('primary_open_path') != 'docs/ARCHIVE_REENTRY_CARD.md':
        return fail('primary open path drifted')
    if payload.get('manifest_file_count', 0) < 20:
        return fail('manifest file count unexpectedly low')
    if payload.get('verified_file_count') != payload.get('manifest_file_count'):
        return fail('verified file count should match manifest file count on the settled tree')
    if payload.get('missing_path_count') != 0 or payload.get('mismatch_count') != 0:
        return fail('settled tree should have no missing paths or mismatches')
    if not payload.get('manifest_sha256_matches'):
        return fail('manifest sha256 should match on the settled tree')
    if not payload.get('all_ok'):
        return fail('all_ok should be true on the settled tree')
    if len(str(payload.get('manifest_sha256_actual', ''))) != 64:
        return fail('manifest sha256 malformed')

    print(
        'archive-handoff-pack-verify-tool: ok '
        f"(files={payload['verified_file_count']} manifest_sha256={payload['manifest_sha256_actual']})"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
