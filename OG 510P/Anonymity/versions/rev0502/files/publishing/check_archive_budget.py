#!/usr/bin/env python3
"""Fail-closed archive budget and hygiene check."""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding='utf-8'))


def check(root: pathlib.Path) -> dict:
    policy = load_json(root / 'publishing' / 'archive_budget_policy.json')
    files = [p for p in root.rglob('*') if p.is_file()]
    total_bytes = sum(p.stat().st_size for p in files)
    file_count = len(files)
    root_file_count = len([p for p in root.iterdir() if p.is_file()])
    report_file_count = len([p for p in (root / 'reports').glob('*.json')])
    schema_file_count = len([p for p in (root / 'schemas').glob('*.schema.json')])
    forbidden_pattern = re.compile(policy['forbidden_series_render_dir_regex'])
    series_render_dirs = sorted(
        p.relative_to(root).as_posix()
        for p in root.rglob('*')
        if p.is_dir() and forbidden_pattern.match(p.relative_to(root).as_posix())
    )
    checks = []

    def record(name: str, ok: bool, details: str):
        checks.append({'name': name, 'status': 'pass' if ok else 'fail', 'details': details})

    record('total_bytes_within_budget', total_bytes <= policy['max_total_bytes'], f"bytes={total_bytes} max={policy['max_total_bytes']}")
    record('file_count_within_budget', file_count <= policy['max_file_count'], f"files={file_count} max={policy['max_file_count']}")
    record('root_file_count_within_budget', root_file_count <= policy['max_root_file_count'], f"root_files={root_file_count} max={policy['max_root_file_count']}")
    record('report_file_count_within_budget', report_file_count <= policy['max_report_file_count'], f"report_files={report_file_count} max={policy['max_report_file_count']}")
    record('schema_file_count_within_budget', schema_file_count <= policy['max_schema_file_count'], f"schema_files={schema_file_count} max={policy['max_schema_file_count']}")
    record('no_series_render_dirs_shipped', not series_render_dirs, 'series_render_dirs=' + (', '.join(series_render_dirs) if series_render_dirs else 'none'))

    failed = [c for c in checks if c['status'] == 'fail']
    return {
        'status': 'pass' if not failed else 'fail',
        'checked_root': '.',
        'policy_path': 'publishing/archive_budget_policy.json',
        'checks': checks,
        'summary': {
            'checks_passed': len(checks) - len(failed),
            'checks_failed': len(failed),
            'bytes': total_bytes,
            'file_count': file_count,
            'root_file_count': root_file_count,
            'report_file_count': report_file_count,
            'schema_file_count': schema_file_count,
            'series_render_dir_count': len(series_render_dirs),
        },
        'fail_closed_rule': 'If this report fails, default to no publication and reduce archive sprawl or prune shipped review-render clutter before trusting the bundle.'
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--write-report', default='')
    args = ap.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = (root / args.write_report).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding='utf-8')
    sys.stdout.write(text)
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
