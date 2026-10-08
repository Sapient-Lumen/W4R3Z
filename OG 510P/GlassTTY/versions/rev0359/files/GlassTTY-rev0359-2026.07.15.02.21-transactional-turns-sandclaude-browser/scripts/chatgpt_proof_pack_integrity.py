#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from chatgpt_first_proof_artifact_ledger import ARTIFACT_SLOTS, build_artifact_ledger, sha256_file

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PACK_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-proof-rehearsal-evidence-pack'
DEFAULT_SUMMARY = ROOT / 'validation' / 'latest' / 'chatgpt-proof-pack-integrity-summary.json'
INTEGRITY_FILENAME = 'evidence-pack-integrity.json'
SCHEMA_VERSION = 1

JsonDict = dict[str, Any]


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def display_path(path: Path | None, *, root: Path = ROOT) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except Exception:
        return str(path)


def inventory_pack(pack_dir: Path, *, include_integrity_file: bool = False) -> list[JsonDict]:
    rows: list[JsonDict] = []
    if not pack_dir.exists():
        return rows
    for path in sorted(pack_dir.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(pack_dir).as_posix()
        if rel == INTEGRITY_FILENAME and not include_integrity_file:
            continue
        rows.append({
            'path': rel,
            'bytes': path.stat().st_size,
            'sha256': sha256_file(path),
        })
    return rows


def _rows_by_filename(rows: list[JsonDict]) -> dict[str, JsonDict]:
    out: dict[str, JsonDict] = {}
    for row in rows:
        name = row.get('filename') or row.get('path')
        if isinstance(name, str):
            out[name] = row
    return out


def _read_json_or_error(path: Path) -> tuple[Any | None, str | None]:
    try:
        return read_json(path), None
    except Exception as exc:  # pragma: no cover - parser details are not important here
        return None, str(exc)


def _artifact_ledger_rows(ledger: Any) -> list[JsonDict]:
    if not isinstance(ledger, dict):
        return []
    rows = ledger.get('slots')
    if isinstance(rows, list):
        return [row for row in rows if isinstance(row, dict)]
    rows = ledger.get('artifacts')
    if isinstance(rows, list):
        return [row for row in rows if isinstance(row, dict)]
    return []


def compare_artifact_ledger(pack_dir: Path, inventory_by_path: dict[str, JsonDict]) -> JsonDict:
    ledger_path = pack_dir / 'artifact-ledger.json'
    ledger, error = _read_json_or_error(ledger_path)
    result: JsonDict = {
        'present': ledger_path.exists(),
        'parse_ok': error is None,
        'parse_error': error,
        'stale_rows': [],
        'missing_rows': [],
        'extra_slot_rows': [],
        'ok': False,
    }
    if error is not None or not isinstance(ledger, dict):
        return result
    expected_slot_names = {slot.filename for slot in ARTIFACT_SLOTS}
    rows = _artifact_ledger_rows(ledger)
    ledger_by_name = _rows_by_filename(rows)
    stale: list[JsonDict] = []
    missing: list[str] = []
    for slot in ARTIFACT_SLOTS:
        row = ledger_by_name.get(slot.filename)
        actual = inventory_by_path.get(slot.filename)
        if row is None:
            missing.append(slot.filename)
            continue
        expected_exists = bool(actual)
        row_exists = bool(row.get('exists'))
        if row_exists != expected_exists:
            stale.append({'filename': slot.filename, 'field': 'exists', 'ledger': row_exists, 'actual': expected_exists})
            continue
        if not actual:
            continue
        if row.get('size') != actual.get('bytes'):
            stale.append({'filename': slot.filename, 'field': 'size', 'ledger': row.get('size'), 'actual': actual.get('bytes')})
        if row.get('sha256') != actual.get('sha256'):
            stale.append({'filename': slot.filename, 'field': 'sha256', 'ledger': row.get('sha256'), 'actual': actual.get('sha256')})
    extras = sorted(name for name in ledger_by_name if name not in expected_slot_names)
    result.update({
        'stale_rows': stale,
        'missing_rows': missing,
        'extra_slot_rows': extras,
        'ok': not stale and not missing,
        'ledger_ready': ledger.get('ready'),
        'ledger_generated_at': ledger.get('generated_at'),
    })
    return result


def compare_existing_integrity(pack_dir: Path, current_inventory: list[JsonDict]) -> JsonDict:
    integrity_path = pack_dir / INTEGRITY_FILENAME
    previous, error = _read_json_or_error(integrity_path)
    result: JsonDict = {
        'present': integrity_path.exists(),
        'parse_ok': error is None,
        'parse_error': error,
        'inventory_matches_current': None,
        'mismatches': [],
        'ok': False,
    }
    if error is not None or not isinstance(previous, dict):
        return result
    previous_inventory = previous.get('inventory') if isinstance(previous.get('inventory'), list) else []
    previous_by_path = _rows_by_filename([row for row in previous_inventory if isinstance(row, dict)])
    current_by_path = _rows_by_filename(current_inventory)
    mismatches: list[JsonDict] = []
    for path in sorted(set(previous_by_path) | set(current_by_path)):
        prev = previous_by_path.get(path)
        curr = current_by_path.get(path)
        if prev is None or curr is None:
            mismatches.append({'path': path, 'previous_present': prev is not None, 'current_present': curr is not None})
            continue
        if prev.get('bytes') != curr.get('bytes') or prev.get('sha256') != curr.get('sha256'):
            mismatches.append({'path': path, 'previous': {'bytes': prev.get('bytes'), 'sha256': prev.get('sha256')}, 'current': {'bytes': curr.get('bytes'), 'sha256': curr.get('sha256')}})
    result.update({
        'inventory_matches_current': not mismatches,
        'mismatches': mismatches,
        'previous_generated_at': previous.get('generated_at'),
        'previous_pack_dir': previous.get('pack_dir'),
        'ok': not mismatches,
    })
    return result


def build_pack_integrity(
    pack_dir: Path = DEFAULT_PACK_DIR,
    *,
    summary_path: Path | None = DEFAULT_SUMMARY,
    write_pack_file: bool = False,
    refresh_ledger: bool = False,
    require_existing: bool = False,
    require_existing_match: bool = False,
) -> JsonDict:
    pack_dir = pack_dir.resolve()
    blockers: list[str] = []
    warnings: list[str] = []
    recommendations: list[str] = []
    if not pack_dir.exists():
        blockers.append('pack directory is missing')
    if refresh_ledger and pack_dir.exists():
        refreshed = build_artifact_ledger(pack_dir, readiness_level='publication-review-ready')
        write_json(pack_dir / 'artifact-ledger.json', refreshed)
    inventory = inventory_pack(pack_dir)
    inventory_by_path = _rows_by_filename(inventory)
    expected_slot_names = [slot.filename for slot in ARTIFACT_SLOTS]
    missing_slots = [name for name in expected_slot_names if name not in inventory_by_path]
    if missing_slots:
        blockers.append(f'missing canonical artifact slots: {", ".join(missing_slots)}')
    ledger_check = compare_artifact_ledger(pack_dir, inventory_by_path) if pack_dir.exists() else {'ok': False, 'present': False}
    if not ledger_check.get('present'):
        blockers.append('artifact-ledger.json is missing')
    elif not ledger_check.get('parse_ok'):
        blockers.append(f'artifact-ledger.json failed to parse: {ledger_check.get("parse_error")}')
    elif not ledger_check.get('ok'):
        stale = ledger_check.get('stale_rows') if isinstance(ledger_check.get('stale_rows'), list) else []
        missing = ledger_check.get('missing_rows') if isinstance(ledger_check.get('missing_rows'), list) else []
        if stale:
            blockers.append(f'artifact-ledger.json is stale for {len(stale)} slot fields')
        if missing:
            blockers.append(f'artifact-ledger.json is missing {len(missing)} canonical slot rows')
        recommendations.append('Rerun proof-pack-integrity with --refresh-ledger --write-pack-file after all mutable review artifacts are finalized.')
    existing_check = compare_existing_integrity(pack_dir, inventory) if pack_dir.exists() else {'ok': False, 'present': False}
    if require_existing and not existing_check.get('present'):
        blockers.append(f'{INTEGRITY_FILENAME} is missing')
    if require_existing_match and not write_pack_file:
        if not existing_check.get('present'):
            blockers.append(f'{INTEGRITY_FILENAME} is missing')
        elif not existing_check.get('parse_ok'):
            blockers.append(f'{INTEGRITY_FILENAME} failed to parse: {existing_check.get("parse_error")}')
        elif not existing_check.get('inventory_matches_current'):
            blockers.append(f'{INTEGRITY_FILENAME} does not match current pack files')
    if not inventory:
        blockers.append('pack inventory is empty')
    ok = not blockers
    verdict = 'proof-pack-integrity-ok' if ok else 'proof-pack-integrity-blocked'
    report: JsonDict = {
        'schema_version': SCHEMA_VERSION,
        'tool': 'glasstty-chatgpt-proof-pack-integrity',
        'generated_at': utcnow(),
        'ok': ok,
        'verdict': verdict,
        'pack_dir': display_path(pack_dir),
        'write_pack_file': write_pack_file,
        'refresh_ledger': refresh_ledger,
        'require_existing': require_existing,
        'require_existing_match': require_existing_match,
        'expected_canonical_slot_count': len(ARTIFACT_SLOTS),
        'present_canonical_slot_count': len([name for name in expected_slot_names if name in inventory_by_path]),
        'file_count_excluding_integrity_file': len(inventory),
        'inventory': inventory,
        'artifact_ledger_check': ledger_check,
        'existing_integrity_check': existing_check,
        'blockers': blockers,
        'warnings': warnings,
        'recommendations': recommendations or [
            'Keep this file with the evidence pack. Rerun proof-pack-integrity after any artifact changes.',
            'For live support bundles, verify the transferred zip with proof-publish-verify as the final handoff gate.',
        ],
    }
    if write_pack_file and pack_dir.exists():
        write_json(pack_dir / INTEGRITY_FILENAME, report)
        report['pack_integrity_path'] = display_path(pack_dir / INTEGRITY_FILENAME)
        report['existing_integrity_after_write'] = {
            'present': True,
            'inventory_matches_current': True,
            'note': 'current report was just written from this inventory; the integrity file excludes itself from inventory hashing',
        }
    if summary_path:
        write_json(summary_path, report)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Create or verify an internal integrity manifest for a ChatGPT proof evidence pack.')
    parser.add_argument('--pack-dir', type=Path, default=DEFAULT_PACK_DIR)
    parser.add_argument('--summary-out', type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument('--write-pack-file', action='store_true', help=f'Write {INTEGRITY_FILENAME} into the evidence pack')
    parser.add_argument('--refresh-ledger', action='store_true', help='Refresh artifact-ledger.json before computing integrity')
    parser.add_argument('--require-existing', action='store_true', help=f'Require {INTEGRITY_FILENAME} to already exist')
    parser.add_argument('--require-existing-match', action='store_true', help=f'Require existing {INTEGRITY_FILENAME} to match current pack bytes')
    parser.add_argument('--pretty', action='store_true')
    parser.add_argument('--require-ok', action='store_true')
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_pack_integrity(
        args.pack_dir,
        summary_path=args.summary_out,
        write_pack_file=args.write_pack_file,
        refresh_ledger=args.refresh_ledger,
        require_existing=args.require_existing,
        require_existing_match=args.require_existing_match,
    )
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)))
    return 0 if (not args.require_ok or report.get('ok')) else 2


if __name__ == '__main__':
    raise SystemExit(main())
