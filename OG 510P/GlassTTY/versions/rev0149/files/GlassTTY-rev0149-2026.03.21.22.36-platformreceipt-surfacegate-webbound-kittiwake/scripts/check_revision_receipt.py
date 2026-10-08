#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from truth_surface_register import build_truth_surface_register
except ModuleNotFoundError:  # pragma: no cover - import path differs under tests
    import importlib.util

    _REGISTER_PATH = Path(__file__).resolve().parent / 'truth_surface_register.py'
    _REGISTER_SPEC = importlib.util.spec_from_file_location('truth_surface_register', _REGISTER_PATH)
    _REGISTER_MODULE = importlib.util.module_from_spec(_REGISTER_SPEC)
    assert _REGISTER_SPEC.loader is not None
    _REGISTER_SPEC.loader.exec_module(_REGISTER_MODULE)
    build_truth_surface_register = _REGISTER_MODULE.build_truth_surface_register

ROOT = Path(__file__).resolve().parent.parent
RECEIPT_PATH = ROOT / 'REVISION-RECEIPT.json'
CONFORMANCE_PATH = ROOT / 'REVISION-RECEIPT-CONFORMANCE.json'
REPORT_COMMAND = 'python scripts/check-revision-receipt.py --pretty'
WRITE_ROOT_COMMAND = 'python scripts/check-revision-receipt.py write-root'


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def build_revision_receipt_conformance(*, root: Path = ROOT) -> dict[str, Any]:
    receipt = _read_json(root / 'REVISION-RECEIPT.json')
    manifest = _read_json(root / 'ARCHIVE_MANIFEST.json')
    truth_register = build_truth_surface_register(root=root)
    checks: list[dict[str, Any]] = []

    def add_check(name: str, ok: bool, detail: str) -> None:
        checks.append({'name': name, 'ok': ok, 'detail': detail})

    add_check('project_matches_manifest', receipt.get('project') == manifest.get('project'), f"receipt={receipt.get('project')} manifest={manifest.get('project')}")
    add_check('revision_matches_manifest', int(receipt.get('revision') or -1) == int(manifest.get('archive_revision') or -1), f"receipt={receipt.get('revision')} manifest={manifest.get('archive_revision')}")
    add_check('archive_name_matches_manifest', receipt.get('archive_name') == manifest.get('archive_name'), f"receipt={receipt.get('archive_name')} manifest={manifest.get('archive_name')}")
    add_check('codename_matches_manifest', receipt.get('codename') == manifest.get('codename'), f"receipt={receipt.get('codename')} manifest={manifest.get('codename')}")
    add_check('summary_matches_manifest', receipt.get('summary_key') == manifest.get('summary'), f"receipt={receipt.get('summary_key')} manifest={manifest.get('summary')}")
    add_check('previous_archive_matches_manifest_base', receipt.get('previous_archive') == manifest.get('base_archive'), f"receipt={receipt.get('previous_archive')} manifest={manifest.get('base_archive')}")
    add_check('truth_surface_counts_match_current_register', receipt.get('truth_surface_counts') == truth_register.get('counts'), f"receipt={receipt.get('truth_surface_counts')} register={truth_register.get('counts')}")

    canon_files = [Path(path) for path in receipt.get('top_level_canon_paths') or []]
    add_check('top_level_canon_paths_exist', all((root / path).exists() for path in canon_files), 'all top-level canon paths listed in the receipt should exist')

    added_paths = [Path(path) for path in receipt.get('added_paths') or []]
    add_check('added_paths_exist', all((root / path).exists() for path in added_paths), 'all added paths listed in the receipt should exist')

    imported_patterns = receipt.get('imported_patterns') or []
    add_check('imported_patterns_declared', len(imported_patterns) >= 1, 'at least one imported pattern should be named explicitly')

    blocking = [item for item in checks if not item['ok']]
    return {
        'project': manifest.get('project', 'GlassTTY'),
        'root': str(root),
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'all_valid': not blocking,
        'check_count': len(checks),
        'failed_check_count': len(blocking),
        'checks': checks,
        'commands': {
            'report': REPORT_COMMAND,
            'write_root': WRITE_ROOT_COMMAND,
        },
    }


def write_root_conformance(*, root: Path = ROOT) -> dict[str, Any]:
    payload = build_revision_receipt_conformance(root=root)
    _write_json(root / 'REVISION-RECEIPT-CONFORMANCE.json', payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Check REVISION-RECEIPT.json against the current archive identity and truth-surface register.')
    parser.add_argument('--pretty', action='store_true')
    subparsers = parser.add_subparsers(dest='command')
    subparsers.add_parser('write-root', help='Refresh REVISION-RECEIPT-CONFORMANCE.json at the repo root.')
    args = parser.parse_args()
    if args.command == 'write-root':
        payload = write_root_conformance(root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    payload = build_revision_receipt_conformance(root=ROOT)
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()
