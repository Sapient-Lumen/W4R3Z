#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / 'scripts' / 'tools' / 'verify_authoritative_archive_zip.py'


def fail(message: str) -> int:
    print(f'authoritative-archive-zip-verify-tool: {message}', file=sys.stderr)
    return 1


def main() -> int:
    if not TOOL.exists():
        return fail('missing tool')
    proc = subprocess.run(['python3', str(TOOL), '--emit', 'json'], cwd=ROOT, text=True, capture_output=True)
    if proc.returncode != 0:
        if proc.stdout:
            print(proc.stdout, end='', file=sys.stderr)
        if proc.stderr:
            print(proc.stderr, end='', file=sys.stderr)
        return fail('tool failed')
    payload = json.loads(proc.stdout)
    if payload.get('tool') != 'verify_authoritative_archive_zip':
        return fail('tool id mismatch')
    if payload.get('all_ok') is not True:
        return fail(f"expected all_ok true, failed={len(payload.get('failed_checks', []))}")
    if payload.get('check_count', 0) < 20:
        return fail('check_count unexpectedly low')
    selected = payload.get('selected_zip') or {}
    if len(str(selected.get('sha256', ''))) != 64:
        return fail('selected sha256 malformed')
    if int(selected.get('size_bytes', 0)) <= 0:
        return fail('selected size bytes must stay positive')
    status = subprocess.run(['python3', str(TOOL), '--emit', 'status'], cwd=ROOT, text=True, capture_output=True)
    if status.returncode != 0 or status.stdout.strip() != 'ok':
        return fail('status emit drifted')
    summary = subprocess.run(['python3', str(TOOL), '--emit', 'summary'], cwd=ROOT, text=True, capture_output=True)
    if summary.returncode != 0 or 'authoritative-archive-zip-verify: ok' not in summary.stdout:
        return fail('summary emit drifted')
    print(f"authoritative-archive-zip-verify-tool: ok (checks={payload['check_count']})")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
