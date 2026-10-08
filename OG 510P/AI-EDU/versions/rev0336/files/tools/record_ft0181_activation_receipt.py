#!/usr/bin/env python3
"""Record a local FT-0181 real-packet activation receipt.

This is the executable firebreak between a ready_for_real_packet ticket and an
active_change ticket. It records only hashes, counts, route classes, and boolean
confirmations after a human has a real owner-reviewed SRC2+ packet, and it
requires that packet hash to match the returned CSV hash preserved through the
intake/workbench/decision chain. It copies no
owner answers, learner data, protected facts, security payloads, or contact
details. The receipt is local/scratch only: not evidence, not custody evidence,
not closure evidence, and not public-summary support.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ft0181_field_guards import (
    activation_receipt_integrity_error,
    archive_relative,
    field_scratch_lane_error,
    decision_chain_source_csv_snapshot,
    output_allowed,
    owner_first_packet_decision_integrity_error,
    source_packet_path_allowed,
)

ROOT = Path(__file__).resolve().parents[1]
REVISION = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8')).get('revision', 'unknown')
DEFAULT_OUTPUT_ROOT = ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-activation-receipts'
OPERATOR_CONFIRMATION = 'human-confirmed-real-packet-accepted-for-active-change'
CLAIM_CEILING = (
    'Activation receipt only; not evidence, not SRC2+ acceptance by itself, not custody evidence, '
    'not closure evidence, not public-summary support, and not proof of learning, safety, access, '
    'workload, compliance, scale, or effectiveness.'
)
SOURCE_TRUTH_CHOICES = {'SRC2', 'SRC3', 'SRC4'}
FORBIDDEN_TERMS = {
    'student id',
    'learner id',
    'student name',
    'learner name',
    'email address',
    '@',
    'raw lms export',
    'gradebook row',
    'screenshot',
    'chat transcript',
    'api key',
    'credential',
    'accommodation facts',
    'disability facts',
    'discipline record',
    'safeguarding record',
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Record a local FT-0181 activation receipt before active_change ticketing.')
    parser.add_argument('--decision', required=True, type=Path, help='scratch/.../first-packet-decision.json produced by owner-first-packet-decision.')
    parser.add_argument('--source-packet', required=True, type=Path, help='Existing local real owner-reviewed packet file; must be the same returned CSV/file hash preserved by the decision source chain and must be outside archive-controlled surfaces or deliberately under scratch/field/ft0181/.')
    parser.add_argument('--source-truth-class', required=True, choices=sorted(SOURCE_TRUTH_CHOICES), help='Accepted source class for the packet: SRC2/SRC3/SRC4 only.')
    parser.add_argument('--accepted-field-count', required=True, type=int, help='Count of accepted usable fields, 1-8; no values copied.')
    parser.add_argument('--reviewer-role-count', required=True, type=int, help='Reviewer role count, 2-5.')
    parser.add_argument('--dictionary-or-map-ref-count', required=True, type=int, help='Count of dictionary/import-map references checked, 1-10; IDs not copied into this receipt.')
    parser.add_argument('--blocked-or-trimmed-field-count', type=int, default=0, help='Count of blocked/trimmed fields, 0-8; no values copied.')
    parser.add_argument('--operator-confirmation', required=True, help='Exact local confirmation token emitted by the router/wait gate.')
    parser.add_argument('--output-dir', type=Path, help='Local/scratch output directory for the activation receipt.')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing receipt directory.')
    parser.add_argument('--json', action='store_true', help='Print machine-readable result.')
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


def source_ref(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def default_output_dir(decision_path: Path, packet_path: Path) -> Path:
    digest = hashlib.sha256((sha256_file(decision_path) + sha256_file(packet_path)).encode('utf-8')).hexdigest()[:12]
    return DEFAULT_OUTPUT_ROOT / f'aiedu-sr-003-{digest}'


def forbidden_argument_term(*values: str) -> str | None:
    text = ' '.join(value for value in values if value).lower()
    for term in sorted(FORBIDDEN_TERMS):
        if term in text:
            return term
    return None


def bounded_count_error(value: int, field: str, upper: int, *, minimum: int = 0) -> str | None:
    if value < minimum:
        return f'{field} must be at least {minimum}'
    if value > upper:
        return f'{field} cannot exceed {upper}'
    return None


def source_decision_snapshot(decision_path: Path, decision_data: dict[str, Any]) -> dict[str, Any]:
    return {
        'reference': relative_to_root(decision_path),
        'decision_sha256': sha256_file(decision_path),
        'board_state': decision_data.get('board_state'),
        'acceptance_state': decision_data.get('acceptance_state'),
        'evidence_state': decision_data.get('evidence_state'),
        'changed_slice_count': decision_data.get('changed_slice_count'),
        'rollback_owner_role_count': decision_data.get('rollback_owner_role_count'),
        'decision_slices': decision_data.get('decision_slices'),
        'change_ticket_effect': decision_data.get('change_ticket_effect'),
        'revalidated_for_activation_receipt': True,
    }


def build_summary(record: dict[str, Any]) -> str:
    counts = record['activation_counts']
    confirms = record['activation_confirmations']
    return f"""# FT-0181 active-change activation receipt

| Field | Value |
|---|---|
| Activation state | `{record['activation_state']}` |
| Source truth class | `{record['source_truth_class']}` |
| Acceptance state | `{record['acceptance_state']}` |
| Evidence state | `{record['evidence_state']}` |
| Source decision | `{record['source_first_packet_decision']['reference']}` |
| Source packet boundary | `{record['source_packet']['path_boundary']}` |
| Source packet matches decision-chain CSV hash | `{record['source_packet']['matches_decision_chain_source_csv_sha256']}` |
| Decision-chain source CSV hash | `{record['decision_source_chain']['source_csv_sha256']}` |
| Decision-chain workbench seed | `{record['decision_source_chain']['workbench_seed_reference']}` |
| Accepted field count | `{counts['accepted_field_count']}` |
| Reviewer role count | `{counts['reviewer_role_count']}` |
| Dictionary/map reference count | `{counts['dictionary_or_map_ref_count']}` |
| Blocked or trimmed field count | `{counts['blocked_or_trimmed_field_count']}` |
| Owner reviewed packet | `{confirms['owner_reviewed_packet']}` |
| Two-role review confirmed | `{confirms['two_role_review_confirmed']}` |
| Protected/security exclusions confirmed | `{confirms['protected_security_exclusions_confirmed']}` |
| No public claim upgrade | `{confirms['no_public_claim_upgrade']}` |

## Boundary

This receipt records that a real owner-reviewed source packet has been accepted
for the narrow purpose of creating an `active_change` ticket. It stores only the
source packet hash, source class, decision-chain source CSV hash, counts, decision hash, and confirmations. It is
not evidence by itself, not custody evidence, not closure evidence, and not
public-summary support. Do not paste owner answers, raw rows, learner identifiers,
protected facts, small cells, contact details, security payloads, or claim
language into this receipt.
"""


def build_activation_receipt(
    *,
    decision: Path,
    source_packet: Path,
    source_truth_class: str,
    accepted_field_count: int,
    reviewer_role_count: int,
    dictionary_or_map_ref_count: int,
    blocked_or_trimmed_field_count: int = 0,
    operator_confirmation: str,
    output_dir: Path | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    decision_path = decision if decision.is_absolute() else ROOT / decision
    decision_path = decision_path.resolve()
    inside, parts = archive_relative(decision_path, archive_root=ROOT)
    lane_error = field_scratch_lane_error(decision_path, archive_root=ROOT, field_name='decision')
    if lane_error or decision_path.name != 'first-packet-decision.json':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'ACTIVATION-RECEIPT-DECISION-BLOCKED',
            'message': 'Activation receipt requires a scratch-local first-packet-decision.json source.',
            'decision': relative_to_root(decision_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if not decision_path.exists() or not decision_path.is_file():
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'ACTIVATION-RECEIPT-DECISION-MISSING',
            'message': 'Referenced first-packet decision does not exist.',
            'decision': relative_to_root(decision_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    try:
        decision_data = load_json(decision_path)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'ACTIVATION-RECEIPT-DECISION-BLOCKED',
            'message': 'Referenced first-packet decision is not readable JSON.',
            'error': str(exc),
            'decision': relative_to_root(decision_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    decision_error = owner_first_packet_decision_integrity_error(decision_data, archive_root=ROOT)
    if decision_error:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'ACTIVATION-RECEIPT-DECISION-BLOCKED',
            'message': 'Referenced first-packet decision failed integrity checks: ' + decision_error,
            'decision': relative_to_root(decision_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    decision_source_chain, chain_error = decision_chain_source_csv_snapshot(decision_path, decision_data, archive_root=ROOT)
    if chain_error or decision_source_chain is None:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'ACTIVATION-RECEIPT-SOURCE-LINEAGE-BLOCKED',
            'message': 'First-packet decision does not preserve a valid returned-CSV hash lineage: ' + str(chain_error),
            'decision': relative_to_root(decision_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    packet_path = source_packet if source_packet.is_absolute() else ROOT / source_packet
    packet_path = packet_path.resolve()
    if not packet_path.exists() or not packet_path.is_file():
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'ACTIVATION-RECEIPT-SOURCE-PACKET-MISSING',
            'message': 'Referenced source packet does not exist as a local file.',
            'source_packet': source_ref(packet_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    allowed, boundary = source_packet_path_allowed(packet_path, archive_root=ROOT)
    if not allowed:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'ACTIVATION-RECEIPT-SOURCE-PACKET-BLOCKED',
            'message': f'Real source packet must be outside archive-controlled surfaces or under scratch/: {boundary}',
            'source_packet': source_ref(packet_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    packet_sha256 = sha256_file(packet_path)
    expected_source_sha256 = str(decision_source_chain.get('source_csv_sha256') or '')
    if packet_sha256 != expected_source_sha256:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'ACTIVATION-RECEIPT-SOURCE-LINEAGE-BLOCKED',
            'message': 'Activation source packet hash must match the returned CSV hash preserved by the intake/workbench/decision chain.',
            'source_packet': source_ref(packet_path),
            'source_packet_sha256': packet_sha256,
            'decision_chain_source_csv_sha256': expected_source_sha256,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if source_truth_class not in SOURCE_TRUTH_CHOICES:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'ACTIVATION-RECEIPT-SOURCE-TRUTH-BLOCKED',
            'message': 'Activation receipt source truth must be SRC2/SRC3/SRC4.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    forbidden = forbidden_argument_term(source_truth_class, operator_confirmation, source_ref(packet_path))
    if forbidden:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'ACTIVATION-RECEIPT-ARGUMENT-BLOCKED',
            'message': f'Activation receipt arguments include forbidden raw/protected/contact term: {forbidden}',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if operator_confirmation.strip() != OPERATOR_CONFIRMATION:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'ACTIVATION-RECEIPT-CONFIRMATION-BLOCKED',
            'message': f'operator-confirmation must be {OPERATOR_CONFIRMATION!r}',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    for field, value, upper, minimum in [
        ('accepted-field-count', accepted_field_count, 8, 1),
        ('reviewer-role-count', reviewer_role_count, 5, 2),
        ('dictionary-or-map-ref-count', dictionary_or_map_ref_count, 10, 1),
        ('blocked-or-trimmed-field-count', blocked_or_trimmed_field_count, 8, 0),
    ]:
        err = bounded_count_error(value, field, upper, minimum=minimum)
        if err:
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'ACTIVATION-RECEIPT-COUNT-BLOCKED',
                'message': err,
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))

    out_dir = output_dir or default_output_dir(decision_path, packet_path)
    out_dir = out_dir if out_dir.is_absolute() else ROOT / out_dir
    out_allowed, out_boundary = output_allowed(out_dir, archive_root=ROOT)
    if not out_allowed:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'ACTIVATION-RECEIPT-OUTPUT-BLOCKED',
            'message': f'Output directory is not allowed for local activation receipts: {out_boundary}',
            'output_dir': relative_to_root(out_dir),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if out_dir.exists():
        if not overwrite:
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'ACTIVATION-RECEIPT-OUTPUT-EXISTS',
                'message': 'Output directory already exists; pass --overwrite to regenerate local scratch output.',
                'output_dir': relative_to_root(out_dir),
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    record = {
        'receipt_type': 'FT-0181-active-change-activation-receipt',
        'receipt_version': REVISION,
        'created_at_utc': now,
        'followthrough_id': 'FT-0181',
        'service_record_id': 'AIEDU-SR-003',
        'activation_state': 'REAL_PACKET_ACCEPTED_FOR_ACTIVE_CHANGE',
        'source_truth_class': source_truth_class,
        'acceptance_state': 'ACTIVATION_RECEIPT_ONLY',
        'evidence_state': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'operator_confirmation': operator_confirmation,
        'source_first_packet_decision': source_decision_snapshot(decision_path, decision_data),
        'decision_source_chain': decision_source_chain,
        'source_packet': {
            'reference': source_ref(packet_path),
            'sha256': packet_sha256,
            'path_boundary': boundary,
            'source_truth_class': source_truth_class,
            'decision_chain_source_csv_sha256': expected_source_sha256,
            'matches_decision_chain_source_csv_sha256': True,
        },
        'activation_counts': {
            'accepted_field_count': accepted_field_count,
            'reviewer_role_count': reviewer_role_count,
            'dictionary_or_map_ref_count': dictionary_or_map_ref_count,
            'blocked_or_trimmed_field_count': blocked_or_trimmed_field_count,
        },
        'activation_confirmations': {
            'owner_reviewed_packet': True,
            'source_packet_hash_recorded': True,
            'dictionary_or_map_reviewed': True,
            'protected_security_exclusions_confirmed': True,
            'two_role_review_confirmed': True,
            'no_contact_details_stored': True,
            'no_raw_or_protected_material_copied': True,
            'no_public_claim_upgrade': True,
        },
        'claim_ceiling': CLAIM_CEILING,
        'required_next_surface': 'docs/30-operations/ft0181-post-decision-change-ticket.md',
        'change_ticket_effect': 'may_source_active_change_ticket_only',
    }
    receipt_error = activation_receipt_integrity_error(record, archive_root=ROOT)
    if receipt_error:
        shutil.rmtree(out_dir)
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'ACTIVATION-RECEIPT-INTEGRITY-BLOCKED',
            'message': 'Generated activation receipt failed integrity checks: ' + receipt_error,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    receipt_path = out_dir / 'activation-receipt.json'
    summary_path = out_dir / 'ACTIVATION-RECEIPT-SUMMARY.md'
    receipt_path.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    summary_path.write_text(build_summary(record), encoding='utf-8')
    return {
        'ok': True,
        'outcome': 'ACTIVATION-RECEIPT-RECORDED',
        'source_truth_class': source_truth_class,
        'output_dir': relative_to_root(out_dir),
        'receipt_path': relative_to_root(receipt_path),
        'summary_path': relative_to_root(summary_path),
        'required_next_surface': record['required_next_surface'],
        'claim_ceiling': CLAIM_CEILING,
    }


def main() -> int:
    args = parse_args()
    try:
        result = build_activation_receipt(
            decision=args.decision,
            source_packet=args.source_packet,
            source_truth_class=args.source_truth_class,
            accepted_field_count=args.accepted_field_count,
            reviewer_role_count=args.reviewer_role_count,
            dictionary_or_map_ref_count=args.dictionary_or_map_ref_count,
            blocked_or_trimmed_field_count=args.blocked_or_trimmed_field_count,
            operator_confirmation=args.operator_confirmation,
            output_dir=args.output_dir,
            overwrite=args.overwrite,
        )
    except ValueError as exc:
        print(str(exc))
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"record_ft0181_activation_receipt: {result['outcome']} -> {result['receipt_path']}")
        print(f"required_next_surface: {result['required_next_surface']}")
        print(f"claim_ceiling: {CLAIM_CEILING}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
