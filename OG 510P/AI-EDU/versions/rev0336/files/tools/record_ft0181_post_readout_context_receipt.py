#!/usr/bin/env python3
"""Record a bounded FT-0181 post-readout owner-context receipt.

A post-readout recheck may say that new owner context exists outside the archive.
This tool links that recheck to the actual returned CSV/source packet hash before
any intake step. It is scratch-only local metadata: it does not copy owner
answers and does not accept evidence, create custody, edit service records, move
lifecycle state, upgrade public language, or close FT-0181.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ft0181_field_guards import (
    archive_relative,
    field_scratch_lane_error,
    output_allowed,
    owner_post_readout_context_receipt_integrity_error,
    owner_post_readout_recheck_integrity_error,
    returned_owner_csv_allowed,
    returned_owner_csv_marker_block,
    returned_owner_csv_source_truth_class,
)

ROOT = Path(__file__).resolve().parents[1]
REVISION = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8')).get('revision', 'unknown')
DEFAULT_OUTPUT_ROOT = ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-post-readout-context-receipts'
OPERATOR_CONFIRMATION = 'human-linked-post-readout-owner-context-receipt'
CLAIM_CEILING = (
    'Post-readout owner-context receipt only; not evidence, not SRC2+ acceptance, '
    'not custody evidence, not closure evidence, and not public-summary support.'
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Record a bounded FT-0181 post-readout owner-context receipt.')
    parser.add_argument('--recheck', required=True, type=Path, help='scratch/.../post-readout-recheck.json with outcome new_owner_context_available.')
    parser.add_argument('--csv', required=True, type=Path, help='Actual returned owner-context CSV/source packet to hash and route to intake.')
    parser.add_argument('--reviewer-role-count', type=int, required=True, help='2-5 roles confirming the link between recheck and actual returned context.')
    parser.add_argument('--operator-confirmation', required=True, help=f'Exact token: {OPERATOR_CONFIRMATION}')
    parser.add_argument('--no-expansion-confirmed', action='store_true')
    parser.add_argument('--no-public-claim-upgrade', action='store_true')
    parser.add_argument('--no-service-record-edit', action='store_true')
    parser.add_argument('--no-lifecycle-change', action='store_true')
    parser.add_argument('--no-closure-from-context-receipt', action='store_true')
    parser.add_argument('--raw-learner-data-present', action='store_true')
    parser.add_argument('--protected-facts-present', action='store_true')
    parser.add_argument('--security-payloads-present', action='store_true')
    parser.add_argument('--public-claim-upgrade-requested', action='store_true')
    parser.add_argument('--output-dir', type=Path, help='Local/scratch output directory for the context receipt.')
    parser.add_argument('--overwrite', action='store_true')
    parser.add_argument('--json', action='store_true')
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def relative_to_root(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def read_csv_shape(path: Path) -> tuple[list[str], int]:
    with path.open(newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    return list(reader.fieldnames or []), len(rows)


def source_recheck_snapshot(recheck_path: Path, recheck_data: dict[str, Any]) -> dict[str, Any]:
    return {
        'reference': relative_to_root(recheck_path),
        'recheck_sha256': sha256_file(recheck_path),
        'recheck_state': recheck_data.get('recheck_state'),
        'recheck_outcome': recheck_data.get('recheck_outcome'),
        'check_date': recheck_data.get('check_date'),
        'source_truth_class': recheck_data.get('source_truth_class'),
        'acceptance_state': recheck_data.get('acceptance_state'),
        'evidence_state': recheck_data.get('evidence_state'),
        'closure_effect': recheck_data.get('closure_effect'),
        'post_readout_recheck_effect': recheck_data.get('post_readout_recheck_effect'),
        'source_post_readout_action': recheck_data.get('source_post_readout_action'),
        'revalidated_for_post_readout_context_receipt': True,
    }


def safe_source_reference(csv_path: Path) -> dict[str, str]:
    inside, parts = archive_relative(csv_path.resolve(), archive_root=ROOT)
    if inside and parts and parts[0] == 'scratch':
        return {
            'path_scope': 'scratch_returned_csv',
            'source_reference': relative_to_root(csv_path),
            'source_basename': csv_path.name,
        }
    return {
        'path_scope': 'external_local_path',
        'source_reference': '[local path withheld; basename only]',
        'source_basename': csv_path.name,
    }


def default_output_dir(recheck_path: Path, csv_path: Path) -> Path:
    digest = sha256_file(recheck_path)[:10] + '-' + sha256_file(csv_path)[:10]
    stem = csv_path.stem.replace(' ', '-').replace('/', '-')[:48] or 'post-readout-owner-context'
    return DEFAULT_OUTPUT_ROOT / f'{stem}-{digest}'


def build_summary(record: dict[str, Any]) -> str:
    source = record['source_post_readout_recheck']
    csv_meta = record['source_csv']
    return f"""# FT-0181 post-readout owner-context receipt

| Field | Value |
|---|---|
| Receipt state | `{record['receipt_state']}` |
| Source recheck | `{source['reference']}` |
| Source recheck outcome | `{source['recheck_outcome']}` |
| CSV basename | `{csv_meta['basename']}` |
| CSV SHA-256 | `{csv_meta['sha256']}` |
| CSV path scope | `{csv_meta['path_scope']}` |
| Reviewer role count | `{record['context_counts']['reviewer_role_count']}` |
| Required next action | `{record['required_next_action']}` |

## Boundary

This local receipt links a post-readout new-context recheck to the actual returned
owner-context CSV hash before intake. It does not copy owner answers or raw rows.
It is not evidence, not accepted `SRC2+`, not custody, not a service-record edit,
not lifecycle movement, not public-summary support, and not `FT-0181` closure.
"""


def build_post_readout_context_receipt(
    *,
    recheck: Path,
    csv_path: Path,
    reviewer_role_count: int,
    operator_confirmation: str,
    no_expansion_confirmed: bool,
    no_public_claim_upgrade: bool,
    no_service_record_edit: bool,
    no_lifecycle_change: bool,
    no_closure_from_context_receipt: bool,
    raw_learner_data_present: bool,
    protected_facts_present: bool,
    security_payloads_present: bool,
    public_claim_upgrade_requested: bool,
    output_dir: Path | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    recheck_path = recheck if recheck.is_absolute() else ROOT / recheck
    recheck_path = recheck_path.resolve()
    inside, parts = archive_relative(recheck_path, archive_root=ROOT)
    lane_error = field_scratch_lane_error(recheck_path, archive_root=ROOT, field_name='recheck')
    if lane_error or recheck_path.name != 'post-readout-recheck.json':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-CONTEXT-RECEIPT-SOURCE-BLOCKED',
            'message': 'Context receipt requires a scratch-local post-readout-recheck.json source.',
            'recheck': relative_to_root(recheck_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if not recheck_path.exists() or not recheck_path.is_file():
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-CONTEXT-RECEIPT-SOURCE-MISSING',
            'message': 'Referenced post-readout recheck does not exist.',
            'recheck': relative_to_root(recheck_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    try:
        recheck_data = load_json(recheck_path)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-CONTEXT-RECEIPT-SOURCE-BLOCKED',
            'message': 'Referenced post-readout recheck is not readable JSON.',
            'error': str(exc),
            'recheck': relative_to_root(recheck_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    recheck_error = owner_post_readout_recheck_integrity_error(recheck_data, archive_root=ROOT)
    if recheck_error:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-CONTEXT-RECEIPT-SOURCE-BLOCKED',
            'message': 'Referenced post-readout recheck failed integrity checks: ' + recheck_error,
            'recheck': relative_to_root(recheck_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if recheck_data.get('recheck_outcome') != 'new_owner_context_available':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-CONTEXT-RECEIPT-OUTCOME-BLOCKED',
            'message': 'Context receipt is allowed only after a post-readout recheck with outcome new_owner_context_available.',
            'recheck_outcome': recheck_data.get('recheck_outcome'),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    source = csv_path if csv_path.is_absolute() else Path.cwd() / csv_path
    source = source.resolve()
    if not source.exists() or not source.is_file():
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-CONTEXT-CSV-MISSING',
            'message': f'CSV path not found: {csv_path}',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    allowed, source_boundary = returned_owner_csv_allowed(source, archive_root=ROOT)
    if not allowed:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-CONTEXT-CSV-SOURCE-BLOCKED',
            'message': 'CSV/source packet must be a scratch or external local returned owner context, not a controlled archive surface.',
            'source_boundary': source_boundary,
            'source_reference': relative_to_root(source),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    marker = returned_owner_csv_marker_block(source)
    if marker:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-CONTEXT-CSV-SMOKE-BLOCKED',
            'message': f'Returned owner context includes non-field smoke/fixture marker: {marker}',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    src_class = returned_owner_csv_source_truth_class(source, archive_root=ROOT)
    if src_class != 'UNVERIFIED-OWNER-REPLY':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-CONTEXT-SOURCE-CLASS-BLOCKED',
            'message': 'Post-readout context receipt requires an unverified owner-reply CSV/source packet, not SRC0 or archive-controlled content.',
            'source_truth_class': src_class,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if operator_confirmation.strip() != OPERATOR_CONFIRMATION:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-CONTEXT-RECEIPT-CONFIRMATION-BLOCKED',
            'message': f'operator-confirmation must be {OPERATOR_CONFIRMATION!r}',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if not (no_expansion_confirmed and no_public_claim_upgrade and no_service_record_edit and no_lifecycle_change and no_closure_from_context_receipt):
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-CONTEXT-RECEIPT-FIREBREAK-BLOCKED',
            'message': 'Context receipt requires no-expansion/no-public/no-service/no-lifecycle/no-closure confirmations.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if any([raw_learner_data_present, protected_facts_present, security_payloads_present, public_claim_upgrade_requested]):
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-CONTEXT-RECEIPT-RISK-FLAG-BLOCKED',
            'message': 'Post-readout context receipt cannot proceed with raw/protected/security/public-claim-upgrade flags.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    out_dir = output_dir or default_output_dir(recheck_path, source)
    out_dir = out_dir if out_dir.is_absolute() else ROOT / out_dir
    allowed_out, output_boundary = output_allowed(out_dir, archive_root=ROOT)
    if not allowed_out:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-CONTEXT-RECEIPT-OUTPUT-BLOCKED',
            'message': f'Output directory is not allowed for local post-readout context receipts: {output_boundary}',
            'output_dir': relative_to_root(out_dir),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if out_dir.exists():
        if not overwrite:
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'POST-READOUT-CONTEXT-RECEIPT-OUTPUT-EXISTS',
                'message': 'Output directory already exists; pass --overwrite to regenerate local scratch output.',
                'output_dir': relative_to_root(out_dir),
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    columns, row_count = read_csv_shape(source)
    source_ref = safe_source_reference(source)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    record = {
        'receipt_type': 'FT-0181-post-readout-owner-context-receipt',
        'receipt_version': REVISION,
        'created_at_utc': now,
        'followthrough_id': 'FT-0181',
        'service_record_id': 'AIEDU-SR-003',
        'receipt_state': 'POST_READOUT_OWNER_CONTEXT_RECEIPTED_NOT_INTAKEN',
        'source_truth_class': 'UNVERIFIED-OWNER-REPLY',
        'acceptance_state': 'NOT_ACCEPTED',
        'evidence_state': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'does_not_upgrade_public_claims',
        'service_record_effect': 'does_not_edit_service_records_from_context_receipt',
        'lifecycle_effect': 'does_not_change_lifecycle_from_context_receipt',
        'ft0181_status': 'live',
        'operator_confirmation': operator_confirmation,
        'source_post_readout_recheck': source_recheck_snapshot(recheck_path, recheck_data),
        'source_csv': {
            'basename': source.name,
            'sha256': sha256_file(source),
            'size_bytes': source.stat().st_size,
            'columns': columns or ['[unreadable-header]'],
            **source_ref,
        },
        'context_counts': {
            'returned_context_count': 1,
            'row_count': row_count,
            'reviewer_role_count': reviewer_role_count,
        },
        'required_next_action': 'run owner-reply-intake with the actual CSV and SOURCE_POST_READOUT_CONTEXT_RECEIPT pointing to this receipt; do not source intake from the recheck or an old contact clock',
        'allowed_next_steps': [
            'owner-reply-intake-with-source-post-readout-context-receipt',
            'rerun-owner-field-next-with-same-csv-and-this-receipt',
        ],
        'prohibited_next_steps': [
            'service-record-edit-from-context-receipt',
            'public-claim-upgrade-from-context-receipt',
            'lifecycle-change-from-context-receipt',
            'custody-or-acceptance-from-context-receipt',
            'ft0181-closure-from-context-receipt',
            'copy-owner-answers-into-context-receipt',
        ],
        'no_expansion_confirmation': True,
        'no_public_claim_upgrade': True,
        'no_service_record_edit_from_context_receipt': True,
        'no_lifecycle_change_from_context_receipt': True,
        'no_closure_from_context_receipt': True,
        'risk_flags': {
            'raw_learner_data_present': False,
            'protected_facts_present': False,
            'security_payloads_present': False,
            'public_claim_upgrade_requested': False,
        },
        'content_minimization': {
            'copies_owner_answers': False,
            'copies_raw_csv_rows': False,
            'copies_live_window_notes': False,
            'copies_contact_details': False,
            'copies_public_claim_text': False,
            'contains_context_hashes_and_counts_only': True,
            'source_post_readout_recheck_revalidated': True,
            'actual_context_must_be_intaken_separately': True,
        },
        'claim_ceiling': CLAIM_CEILING,
        'post_readout_context_receipt_effect': 'may_source_owner_reply_intake_only',
        'closure_boundary': 'This local post-readout context receipt does not close FT-0181 and does not prove service claims, learning, safety, access, workload, compliance, scale, or effectiveness.',
        'output_boundary': output_boundary,
    }
    integrity_error = owner_post_readout_context_receipt_integrity_error(record, archive_root=ROOT)
    if integrity_error:
        shutil.rmtree(out_dir, ignore_errors=True)
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-CONTEXT-RECEIPT-INTEGRITY-BLOCKED',
            'message': integrity_error,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    (out_dir / 'post-readout-context-receipt.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    (out_dir / 'POST-READOUT-CONTEXT-RECEIPT-SUMMARY.md').write_text(build_summary(record), encoding='utf-8')
    return {
        'ok': True,
        'outcome': 'POST-READOUT-CONTEXT-RECEIPT-RECORDED',
        'post_readout_context_receipt': relative_to_root(out_dir / 'post-readout-context-receipt.json'),
        'summary': relative_to_root(out_dir / 'POST-READOUT-CONTEXT-RECEIPT-SUMMARY.md'),
        'source_post_readout_recheck': relative_to_root(recheck_path),
        'source_csv_sha256': record['source_csv']['sha256'],
        'claim_ceiling': CLAIM_CEILING,
    }


def main() -> None:
    args = parse_args()
    try:
        result = build_post_readout_context_receipt(
            recheck=args.recheck,
            csv_path=args.csv,
            reviewer_role_count=args.reviewer_role_count,
            operator_confirmation=args.operator_confirmation,
            no_expansion_confirmed=args.no_expansion_confirmed,
            no_public_claim_upgrade=args.no_public_claim_upgrade,
            no_service_record_edit=args.no_service_record_edit,
            no_lifecycle_change=args.no_lifecycle_change,
            no_closure_from_context_receipt=args.no_closure_from_context_receipt,
            raw_learner_data_present=args.raw_learner_data_present,
            protected_facts_present=args.protected_facts_present,
            security_payloads_present=args.security_payloads_present,
            public_claim_upgrade_requested=args.public_claim_upgrade_requested,
            output_dir=args.output_dir,
            overwrite=args.overwrite,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
