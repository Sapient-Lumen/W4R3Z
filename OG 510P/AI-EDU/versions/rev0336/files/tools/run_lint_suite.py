#!/usr/bin/env python3
"""Run registered AI-EDU lint tools and registry-defined lanes.

The full validator order lives in CUBE_TOOLCHAIN_REGISTRY.json. Narrow lanes and
filters are for cloudtainer iteration only: they catch focused failures sooner
without becoming release approval or FT-0181 closure.
"""
from __future__ import annotations

import argparse
import atexit
import hashlib
import json
import runpy
import shutil
import signal
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'CUBE_TOOLCHAIN_REGISTRY.json'
FULL_TOKEN = 'ALL_REGISTERED_LINT_ORDER'
FIELD_ROOT = ROOT / 'scratch' / 'field' / 'ft0181'
FIXTURE_EXACT = {'validation', 'checks', 'releases'}
FIXTURE_PREFIXES = ('validation-', 'check-', 'smoke-', 'test-', 'fixture-', 'activation-source-validation-')
FIXTURE_SUFFIXES = ('-validation',)


def fixture_part(name: str) -> bool:
    lowered = name.lower()
    return (
        lowered in FIXTURE_EXACT
        or lowered.startswith(FIXTURE_PREFIXES)
        or lowered.endswith(FIXTURE_SUFFIXES)
    )


def cleanup_validation_fixture_lanes() -> None:
    if not FIELD_ROOT.exists():
        return
    for child in list(FIELD_ROOT.iterdir()):
        if not fixture_part(child.name):
            continue
        if child.is_dir():
            shutil.rmtree(child, ignore_errors=True)
        else:
            child.unlink(missing_ok=True)


def install_cleanup_handlers() -> None:
    """Remove validator-only field lanes on normal exit or interrupt."""
    atexit.register(cleanup_validation_fixture_lanes)

    def handle_signal(signum: int, _frame: object) -> None:
        cleanup_validation_fixture_lanes()
        raise SystemExit(128 + signum)

    for name in ('SIGTERM', 'SIGINT', 'SIGHUP'):
        signum = getattr(signal, name, None)
        if signum is not None:
            signal.signal(signum, handle_signal)


def live_field_snapshot() -> dict[str, str]:
    snapshot: dict[str, str] = {}
    if not FIELD_ROOT.exists():
        return snapshot
    for path in sorted(FIELD_ROOT.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(FIELD_ROOT)
        if any(fixture_part(part) for part in rel.parts):
            continue
        snapshot[rel.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return snapshot


def snapshot_delta(before: dict[str, str], after: dict[str, str]) -> list[str]:
    out: list[str] = []
    for path in sorted(set(before) | set(after)):
        if path not in before:
            out.append(f'added {path}')
        elif path not in after:
            out.append(f'removed {path}')
        elif before[path] != after[path]:
            out.append(f'changed {path}')
    return out


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding='utf-8'))


def lint_entries(registry: dict) -> list[dict]:
    return sorted(registry.get('lint_order', []), key=lambda row: row.get('order', 10**9))


def split_csv(values: list[str] | None) -> list[str]:
    items: list[str] = []
    for value in values or []:
        for part in value.split(','):
            part = part.strip()
            if part:
                items.append(part)
    return items


def lane_id(row: dict) -> str:
    return str(row.get('lane_id') or row.get('lane') or row.get('name') or '')


def lane_description(row: dict) -> str:
    return str(row.get('description') or row.get('purpose') or '')


def lane_map(registry: dict) -> dict[str, dict]:
    lanes = registry.get('lint_lanes') or []
    mapped = {lane_id(row): row for row in lanes if lane_id(row)}
    mapped.setdefault('full-release', {
        'lane_id': 'full-release',
        'description': 'Complete registered lint/generation order and final release gate.',
        'selection': 'all',
        'paths': [FULL_TOKEN],
    })
    return mapped


def select_by_lane(registry: dict, entries: list[dict], lane: str) -> list[dict]:
    lanes = lane_map(registry)
    if lane not in lanes:
        raise SystemExit(f"unknown lint lane {lane!r}; available lanes: {', '.join(sorted(lanes))}")
    lane_row = lanes[lane]
    selection = lane_row.get('selection')
    requested = lane_row.get('paths', [])
    if selection == 'all' or FULL_TOKEN in requested:
        return list(entries)
    if selection not in (None, 'paths'):
        raise SystemExit(f"lint lane {lane!r} has invalid selection {selection!r}")
    by_path = {row['path']: row for row in entries}
    missing = [path for path in requested if path not in by_path]
    if missing:
        raise SystemExit('lint lane references paths outside lint_order: ' + ', '.join(missing))
    requested_set = set(requested)
    return [row for row in entries if row['path'] in requested_set]


def apply_filters(entries: list[dict], args: argparse.Namespace) -> list[dict]:
    selected = list(entries)
    if args.start_order is not None:
        selected = [row for row in selected if row.get('order', 0) >= args.start_order]
    if args.end_order is not None:
        selected = [row for row in selected if row.get('order', 10**9) <= args.end_order]
    exact_paths = set(split_csv(args.only))
    if exact_paths:
        selected = [row for row in selected if row.get('path') in exact_paths or Path(row.get('path', '')).name in exact_paths]
    path_terms = [term.lower() for term in split_csv(args.path_contains)]
    if path_terms:
        selected = [row for row in selected if any(term in row.get('path', '').lower() for term in path_terms)]
    role_terms = [term.lower() for term in split_csv(args.role_contains)]
    if role_terms:
        selected = [row for row in selected if any(term in row.get('role', '').lower() for term in role_terms)]
    return selected


def run_entries(entries: list[dict]) -> None:
    seen: set[str] = set()
    for row in entries:
        tool_path = row.get('path')
        if not tool_path:
            raise SystemExit('lint registry row missing path')
        if tool_path in seen:
            raise SystemExit(f'duplicate lint tool in selected run: {tool_path}')
        seen.add(tool_path)
        path = ROOT / tool_path
        if not path.exists():
            raise SystemExit(f'lint tool missing: {tool_path}')
        print(f'== {path.name} ==', flush=True)
        old_argv = sys.argv[:]
        old_path = sys.path[:]
        try:
            sys.argv = [str(path)]
            for import_path in [str(path.parent), str(ROOT)]:
                if import_path not in sys.path:
                    sys.path.insert(0, import_path)
            runpy.run_path(str(path), run_name='__main__')
        finally:
            sys.argv = old_argv
            sys.path = old_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Run AI-EDU validators/generators from CUBE_TOOLCHAIN_REGISTRY.json.')
    parser.add_argument('--lane', default='full-release', help='Named lint_lanes entry to run; default: full-release')
    parser.add_argument('--start-order', type=int, help='Run lint entries with order >= this value after lane selection.')
    parser.add_argument('--end-order', type=int, help='Run lint entries with order <= this value after lane selection.')
    parser.add_argument('--only', action='append', help='Exact tools/path.py or filename entry to run; may be repeated or comma-separated.')
    parser.add_argument('--path-contains', action='append', help='Run entries whose path contains this text; may be repeated or comma-separated.')
    parser.add_argument('--role-contains', action='append', help='Run entries whose role contains this text; may be repeated or comma-separated.')
    parser.add_argument('--list', action='store_true', help='List selected tools without running them.')
    parser.add_argument('--list-lanes', action='store_true', help='List registered lanes without running them.')
    args = parser.parse_args(argv)

    registry = load_registry()
    lanes = lane_map(registry)
    if args.list_lanes:
        for name in sorted(lanes):
            print(f'{name}: {lane_description(lanes[name])}')
        return 0

    entries = lint_entries(registry)
    selected = apply_filters(select_by_lane(registry, entries, args.lane), args)
    if not selected:
        raise SystemExit('run_lint_suite: no tools matched the selected lane/filters')
    if args.list:
        for row in selected:
            print(f"{row.get('order')}: {row.get('path')} — {row.get('role')}")
        return 0
    cleanup_validation_fixture_lanes()
    install_cleanup_handlers()
    before = live_field_snapshot()
    print(f'run_lint_suite: lane={args.lane} tools={len(selected)}', flush=True)
    try:
        run_entries(selected)
    except BaseException:
        cleanup_validation_fixture_lanes()
        raise
    after = live_field_snapshot()
    cleanup_validation_fixture_lanes()
    delta = snapshot_delta(before, after)
    if delta:
        raise SystemExit('run_lint_suite: lint mutated live FT-0181 field state:\n' + '\n'.join(delta))
    print(f'run_lint_suite: OK lane={args.lane} tools={len(selected)} live-field=unchanged')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
