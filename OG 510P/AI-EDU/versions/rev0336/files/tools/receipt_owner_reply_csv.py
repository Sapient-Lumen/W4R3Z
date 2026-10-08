#!/usr/bin/env python3
"""Create a local, content-minimized receipt for an FT-0181 owner reply CSV.

The receipt is a custody aid, not evidence. It stores file fingerprints,
row-presence metadata, triage outcome, and the next action without copying owner
answers into an archive surface. Normal use refuses SRC0 smoke fixtures.
"""
import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from ft0181_field_guards import output_allowed, returned_owner_csv_source_block, returned_owner_csv_source_truth_class
from triage_owner_reply_csv import EXPECTED_COLUMNS, triage_csv

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / 'fixtures'
ARCHIVE_OUTPUT_BLOCK_ROOTS = {'docs', 'examples', 'fixtures', 'schemas', 'templates', 'tools'}
SMOKE_LABELS = [
    'synthetic smoke fixture',
    'not a returned owner packet',
    'not src2+ evidence',
    'not closure evidence',
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def relative_to_root(path: Path) -> str | None:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return None


def read_rows(path: Path):
    with path.open(newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        return reader.fieldnames or [], list(reader)


def has_smoke_labels(rows) -> bool:
    joined = ' '.join((row.get('owner_response') or '').lower() for row in rows)
    return any(label in joined for label in SMOKE_LABELS)


def source_truth_class(path: Path, rows, allow_src0_smoke: bool = False) -> str:
    src_class = returned_owner_csv_source_truth_class(path, archive_root=ROOT, allow_src0_smoke=allow_src0_smoke)
    if src_class == 'UNVERIFIED-OWNER-REPLY' and has_smoke_labels(rows):
        return 'SRC0-SMOKE'
    return src_class


def safe_source_reference(path: Path) -> dict:
    rel = relative_to_root(path)
    if rel:
        return {
            'path_scope': 'inside_archive_tree',
            'source_reference': rel,
            'source_basename': path.name,
        }
    return {
        'path_scope': 'external_local_path',
        'source_reference': '[local path withheld; basename only]',
        'source_basename': path.name,
    }


def is_archive_output_path(path: Path) -> bool:
    try:
        rel = path.resolve().relative_to(ROOT)
    except ValueError:
        return False
    if not rel.parts:
        return True
    return rel.parts[0] in ARCHIVE_OUTPUT_BLOCK_ROOTS or len(rel.parts) == 1


def response_presence(rows) -> dict:
    present = []
    blank = []
    unknown = []
    for row in rows:
        rid = (row.get('row_id') or '').strip()
        value = (row.get('owner_response') or '').strip()
        if not rid:
            continue
        if value:
            present.append(rid)
            if value.lower() in {'unknown', 'not known', 'not available', 'n/a', 'na'} or value.lower().startswith('unknown'):
                unknown.append(rid)
        else:
            blank.append(rid)
    return {
        'nonempty_owner_response_row_ids': present,
        'blank_owner_response_row_ids': blank,
        'unknown_owner_response_row_ids': unknown,
        'owner_response_nonempty_count': len(present),
    }


def build_receipt(path: Path, allow_src0_smoke: bool = False) -> dict:
    resolved = path.resolve()
    if not resolved.exists():
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'RECEIPT-BLOCKED',
            'message': f'CSV path not found: {path}',
        }, indent=2))

    fieldnames, rows = read_rows(resolved)
    src_class = source_truth_class(resolved, rows, allow_src0_smoke=allow_src0_smoke)
    if src_class == 'SRC0-SMOKE' and not allow_src0_smoke:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'SRC0-RECEIPT-BLOCKED',
            'source_truth_class': src_class,
            'source_reference': relative_to_root(resolved) or '[local path withheld; basename only]',
            'message': 'Synthetic smoke fixtures cannot receive normal owner-reply receipts. Use make owner-reply-smoke for plumbing checks only; do not receipt smoke as owner evidence.',
        }, indent=2))
    source_block = returned_owner_csv_source_block(resolved, archive_root=ROOT, allow_src0_smoke=allow_src0_smoke)
    if source_block:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'RETURNED-CSV-SOURCE-BLOCKED',
            'source_truth_class': src_class,
            'source_reference': relative_to_root(resolved) or '[local path withheld; basename only]',
            'message': f'Archive-controlled CSV source is not a returned owner packet ({source_block}). Route a local scratch/external returned CSV through make owner-field-next before receipt or intake.',
        }, indent=2))

    triage = triage_csv(resolved, allow_src0_smoke=allow_src0_smoke)
    source_ref = safe_source_reference(resolved)
    receipt = {
        'receipt_type': 'FT-0181-owner-reply-local-receipt',
        'receipt_version': 'rev0262',
        'created_at_utc': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'source_truth_class': src_class,
        'source_fingerprint': {
            **source_ref,
            'sha256': sha256_file(resolved),
            'size_bytes': resolved.stat().st_size,
            'columns': fieldnames,
            'row_count': len(rows),
        },
        'content_minimization': {
            'raw_owner_answers_copied': False,
            'row_answer_hashes_included': False,
            'owner_identifiers_copied': False,
            'allowed_archive_use': 'metadata-only local receipt; do not paste raw owner answers, protected facts, small cells, credentials, or learner rows into release surfaces',
        },
        'row_presence': response_presence(rows),
        'triage': {
            'outcome': triage.get('outcome'),
            'stage_to_workbench': triage.get('stage_to_workbench'),
            'is_real_packet': triage.get('is_real_packet'),
            'next_action': triage.get('next_action'),
            'reason_count': len(triage.get('reasons', [])),
        },
        'claim_ceiling': 'Local receipt only; not SRC2+ acceptance, not closure evidence, not public summary support, and not proof of learning, safety, access, workload, compliance, scale, or effectiveness.',
        'ft0181_status': 'live',
    }
    if fieldnames != EXPECTED_COLUMNS:
        receipt['content_minimization']['warning'] = 'CSV columns do not match the eight-row owner reply template; do not stage before re-ask or block.'
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description='Create a content-minimized local receipt for an FT-0181 owner-reply CSV.')
    parser.add_argument('csv_path', type=Path)
    parser.add_argument('--output', type=Path, help='Optional JSON output path. Use scratch/ or an external local path; archive-controlled paths are refused.')
    parser.add_argument('--allow-src0-smoke', action='store_true', help='Internal test opt-in only; never use for real owner receipt.')
    args = parser.parse_args(argv)
    try:
        receipt = build_receipt(args.csv_path, allow_src0_smoke=args.allow_src0_smoke)
        text = json.dumps(receipt, indent=2) + '\n'
        if args.output:
            out = args.output if args.output.is_absolute() else ROOT / args.output
            allowed, output_boundary = output_allowed(out, archive_root=ROOT)
            if not allowed:
                raise ValueError(json.dumps({
                    'ok': False,
                    'outcome': 'RECEIPT-OUTPUT-BLOCKED',
                    'output_boundary': output_boundary,
                    'message': 'Owner-reply receipts are local/scratch metadata and cannot be written into the release archive outside scratch or to controlled release surfaces.',
                    'claim_ceiling': receipt['claim_ceiling'],
                }, indent=2))
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text, encoding='utf-8')
            print(out.as_posix())
        else:
            print(text, end='')
    except ValueError as exc:
        print(str(exc))
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
