#!/usr/bin/env python3
"""Run the bounded FT-0181 owner-reply local intake bundle.

This utility keeps the practical path compact after a real owner CSV arrives:
receipt -> triage -> routed local artifact. It deliberately writes only to a
scratch/external directory and never promotes a returned CSV, local receipt,
triage JSON, or staging note to evidence, release, or closure surfaces.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from ft0181_field_guards import (
    archive_relative,
    field_scratch_lane_error,
    output_allowed,
    owner_contact_status_integrity_error,
    owner_post_readout_context_receipt_integrity_error,
    returned_owner_csv_source_block,
    returned_owner_csv_source_truth_class,
)
from receipt_owner_reply_csv import build_receipt, sha256_file
from stage_owner_reply_csv import staged_note
from triage_owner_reply_csv import triage_csv

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_OUTPUT_BLOCK_ROOTS = {'docs', 'examples', 'fixtures', 'schemas', 'templates', 'tools'}
OUTCOME_TEMPLATE = 'templates/ft0181-triage-outcome-note-template.md'
REASK_TEMPLATE = 'templates/ft0181-owner-reask-once-message.md'
STAGING_TEMPLATE = 'templates/ft0181-proceed-staged-note-template.md'
CLAIM_CEILING = (
    'Local intake bundle only; not SRC2+ acceptance, not custody evidence, '
    'not closure evidence, not public summary support, and not proof of learning, '
    'safety, access, workload, compliance, scale, or effectiveness.'
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def is_archive_output_path(path: Path) -> bool:
    try:
        rel = path.resolve().relative_to(ROOT)
    except ValueError:
        return False
    if not rel.parts:
        return True
    return rel.parts[0] in ARCHIVE_OUTPUT_BLOCK_ROOTS or len(rel.parts) == 1


def relative_to_root(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def default_output_dir(csv_path: Path) -> Path:
    digest = sha256_file(csv_path.resolve())[:12]
    stem = csv_path.stem.replace(' ', '-').replace('/', '-')[:48] or 'owner-reply'
    return ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-reply-intakes' / f'{stem}-{digest}'


def write_json(path: Path, data: dict) -> dict:
    text = json.dumps(data, indent=2) + '\n'
    path.write_text(text, encoding='utf-8')
    return {'path': relative_to_root(path), 'sha256': sha256_text(text), 'size_bytes': len(text.encode('utf-8'))}


def write_text(path: Path, text: str) -> dict:
    if not text.endswith('\n'):
        text += '\n'
    path.write_text(text, encoding='utf-8')
    return {'path': relative_to_root(path), 'sha256': sha256_text(text), 'size_bytes': len(text.encode('utf-8'))}



def resolve_archive_or_absolute(path: Path) -> Path:
    if path.is_absolute():
        return path
    return ROOT / path


def load_json(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def validate_source_contact_status(source_contact_status: Path | None) -> tuple[dict, str]:
    """Validate the local contact clock that makes a first returned CSV plausible."""
    if source_contact_status is None:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'INTAKE-SOURCE-PROVENANCE-BLOCKED',
            'message': 'Either SOURCE_CONTACT_STATUS or SOURCE_POST_READOUT_CONTEXT_RECEIPT is required. Use the exact owner-field-next emitted command for first-contact replies or post-readout new context.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    status_path = resolve_archive_or_absolute(source_contact_status).resolve()
    inside, parts = archive_relative(status_path, archive_root=ROOT)
    if not inside or not parts or parts[0] != 'scratch':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'INTAKE-SOURCE-CONTACT-STATUS-BLOCKED',
            'source_contact_status': source_contact_status.as_posix(),
            'message': 'SOURCE_CONTACT_STATUS must resolve to a local scratch contact-status.json emitted by owner-contact-status.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    lane_error = field_scratch_lane_error(status_path, archive_root=ROOT, field_name='SOURCE_CONTACT_STATUS')
    if lane_error:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'INTAKE-SOURCE-CONTACT-STATUS-BLOCKED',
            'source_contact_status': relative_to_root(status_path),
            'message': lane_error,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if status_path.name != 'contact-status.json' or not status_path.exists() or not status_path.is_file():
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'INTAKE-SOURCE-CONTACT-STATUS-BLOCKED',
            'source_contact_status': relative_to_root(status_path),
            'message': 'SOURCE_CONTACT_STATUS must point to an existing contact-status.json file.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    status_data = load_json(status_path)
    if status_data is None:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'INTAKE-SOURCE-CONTACT-STATUS-BLOCKED',
            'source_contact_status': relative_to_root(status_path),
            'message': 'SOURCE_CONTACT_STATUS is not readable JSON.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    integrity_error = owner_contact_status_integrity_error(status_data, archive_root=ROOT)
    if integrity_error:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'INTAKE-SOURCE-CONTACT-STATUS-BLOCKED',
            'source_contact_status': relative_to_root(status_path),
            'message': f'SOURCE_CONTACT_STATUS cannot source returned-CSV intake: {integrity_error}',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    return status_data, relative_to_root(status_path)


def validate_source_post_readout_context_receipt(source_context_receipt: Path | None, csv_path: Path) -> tuple[dict, str]:
    """Validate a post-readout context receipt that links a recheck to this CSV."""
    if source_context_receipt is None:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'INTAKE-SOURCE-PROVENANCE-BLOCKED',
            'message': 'Either SOURCE_CONTACT_STATUS or SOURCE_POST_READOUT_CONTEXT_RECEIPT is required. Use the exact owner-field-next emitted command for first-contact replies or post-readout new context.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    receipt_path = resolve_archive_or_absolute(source_context_receipt).resolve()
    inside, parts = archive_relative(receipt_path, archive_root=ROOT)
    if not inside or not parts or parts[0] != 'scratch':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'INTAKE-SOURCE-POST-READOUT-CONTEXT-RECEIPT-BLOCKED',
            'source_post_readout_context_receipt': source_context_receipt.as_posix(),
            'message': 'SOURCE_POST_READOUT_CONTEXT_RECEIPT must resolve to a local scratch post-readout-context-receipt.json.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    lane_error = field_scratch_lane_error(receipt_path, archive_root=ROOT, field_name='SOURCE_POST_READOUT_CONTEXT_RECEIPT')
    if lane_error:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'INTAKE-SOURCE-POST-READOUT-CONTEXT-RECEIPT-BLOCKED',
            'source_post_readout_context_receipt': relative_to_root(receipt_path),
            'message': lane_error,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if receipt_path.name != 'post-readout-context-receipt.json' or not receipt_path.exists() or not receipt_path.is_file():
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'INTAKE-SOURCE-POST-READOUT-CONTEXT-RECEIPT-BLOCKED',
            'source_post_readout_context_receipt': relative_to_root(receipt_path),
            'message': 'SOURCE_POST_READOUT_CONTEXT_RECEIPT must point to an existing post-readout-context-receipt.json file.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    receipt_data = load_json(receipt_path)
    if receipt_data is None:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'INTAKE-SOURCE-POST-READOUT-CONTEXT-RECEIPT-BLOCKED',
            'source_post_readout_context_receipt': relative_to_root(receipt_path),
            'message': 'SOURCE_POST_READOUT_CONTEXT_RECEIPT is not readable JSON.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    integrity_error = owner_post_readout_context_receipt_integrity_error(receipt_data, archive_root=ROOT)
    if integrity_error:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'INTAKE-SOURCE-POST-READOUT-CONTEXT-RECEIPT-BLOCKED',
            'source_post_readout_context_receipt': relative_to_root(receipt_path),
            'message': f'SOURCE_POST_READOUT_CONTEXT_RECEIPT cannot source returned-CSV intake: {integrity_error}',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    csv_sha = sha256_file(csv_path.resolve())
    if receipt_data.get('source_csv', {}).get('sha256') != csv_sha:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'INTAKE-SOURCE-POST-READOUT-CONTEXT-HASH-BLOCKED',
            'source_post_readout_context_receipt': relative_to_root(receipt_path),
            'message': 'The CSV hash does not match SOURCE_POST_READOUT_CONTEXT_RECEIPT; use the same returned owner context that was receipted from the post-readout recheck.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    return receipt_data, relative_to_root(receipt_path)


def outcome_note(triage: dict, source_sha256: str) -> str:
    outcome = triage.get('outcome', 'UNKNOWN')
    next_action = triage.get('next_action', {})
    next_artifact = next_action.get('next_artifact') or OUTCOME_TEMPLATE
    return '\n'.join([
        '# FT-0181 owner-reply local intake outcome note',
        '',
        f'Created UTC: {datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")}',
        f'Triage outcome: {outcome}',
        f'Source CSV SHA-256: {source_sha256}',
        f'Next artifact: {next_artifact}',
        '',
        '## Boundary',
        '',
        CLAIM_CEILING,
        '',
        'This note is a local routing artifact. It intentionally does not copy owner answers, raw learner rows, protected facts, small cells, security payloads, screenshots, vendor dashboards, or evidence claims.',
        '',
        '## Next step',
        '',
        f"{next_action.get('summary', 'Route according to the triage outcome without widening the request.')}",
        '',
        '## No-widening rule',
        '',
        '- Do not request a full export, raw learner data, screenshots, vendor telemetry, gradebook rows, or a new source system.',
        '- Do not create a new registry or control because this intake did not proceed.',
        '- Keep `FT-0181` live unless later real `SRC2+` custody and closure gates pass.',
        '',
    ])


def bundle_intake(csv_path: Path, output_dir: Path | None = None, source_contact_status: Path | None = None, source_post_readout_context_receipt: Path | None = None) -> dict:
    source = csv_path if csv_path.is_absolute() else Path.cwd() / csv_path
    source = source.resolve()
    if not source.exists():
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'INTAKE-BLOCKED',
            'message': f'CSV path not found: {csv_path}',
        }, indent=2))

    if bool(source_contact_status) == bool(source_post_readout_context_receipt):
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'INTAKE-SOURCE-PROVENANCE-BLOCKED',
            'message': 'Provide exactly one source provenance: SOURCE_CONTACT_STATUS for first/reask replies, or SOURCE_POST_READOUT_CONTEXT_RECEIPT for post-readout new owner context.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    source_contact_data = None
    source_contact_ref = None
    source_context_data = None
    source_context_ref = None
    if source_contact_status:
        source_contact_data, source_contact_ref = validate_source_contact_status(source_contact_status)
    else:
        source_context_data, source_context_ref = validate_source_post_readout_context_receipt(source_post_readout_context_receipt, source)

    src_class = returned_owner_csv_source_truth_class(source, archive_root=ROOT)
    if src_class == 'SRC0-SMOKE':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'SRC0-RECEIPT-BLOCKED',
            'source_truth_class': src_class,
            'source_reference': relative_to_root(source),
            'message': 'Synthetic smoke fixtures cannot receive normal owner-reply intake. Use make owner-reply-smoke for plumbing checks only; do not intake smoke as owner evidence.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    source_block = returned_owner_csv_source_block(source, archive_root=ROOT)
    if source_block:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'RETURNED-CSV-SOURCE-BLOCKED',
            'source_truth_class': src_class,
            'source_reference': relative_to_root(source),
            'message': f'Archive-controlled CSV source is not a returned owner packet ({source_block}). Route a local scratch/external returned CSV through make owner-field-next before intake.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    out = output_dir if output_dir is not None else default_output_dir(source)
    out = out if out.is_absolute() else ROOT / out
    allowed, output_boundary = output_allowed(out, archive_root=ROOT)
    if not allowed:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'INTAKE-OUTPUT-BLOCKED',
            'output_dir': relative_to_root(out),
            'output_boundary': output_boundary,
            'message': 'Owner-reply intake bundles are local/scratch artifacts and cannot be written into the release archive outside scratch or to controlled release surfaces.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    out.mkdir(parents=True, exist_ok=True)

    receipt = build_receipt(source, allow_src0_smoke=False)
    triage = triage_csv(source)
    source_hash = receipt['source_fingerprint']['sha256']
    created = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')

    receipt_meta = write_json(out / 'receipt.json', receipt)
    triage_for_write = {
        'triage_type': 'FT-0181-owner-reply-local-triage',
        'created_at_utc': created,
        'source_csv_sha256': source_hash,
        'outcome': triage.get('outcome'),
        'stage_to_workbench': triage.get('stage_to_workbench'),
        'is_real_packet': triage.get('is_real_packet'),
        'row_status': triage.get('row_status', []),
        'reason_count': len(triage.get('reasons', [])),
        'reasons': triage.get('reasons', []),
        'next_action': triage.get('next_action'),
        'claim_ceiling': CLAIM_CEILING,
        'content_minimization': {
            'raw_owner_answers_copied': False,
            'owner_identifiers_copied': False,
            'stage_note_may_contain_minimized_owner_answers_only_when_outcome_is_proceed_staged': True,
        },
    }
    triage_meta = write_json(out / 'triage.json', triage_for_write)

    artifacts = {
        'receipt': receipt_meta,
        'triage': triage_meta,
    }
    if triage.get('outcome') == 'PROCEED-STAGED':
        note = staged_note(source)
        artifacts['proceed_staged_note'] = write_text(out / 'proceed-staged.md', note)
        next_local_artifact = 'proceed-staged.md'
    else:
        note = outcome_note(triage, source_hash)
        artifacts['outcome_note'] = write_text(out / 'outcome-note.md', note)
        next_local_artifact = 'outcome-note.md'

    manifest = {
        'bundle_type': 'FT-0181-owner-reply-local-intake-bundle',
        'bundle_version': 'rev0262',
        'created_at_utc': created,
        'source_truth_class': receipt.get('source_truth_class'),
        'source_csv': {
            'basename': source.name,
            'sha256': source_hash,
            'reference': receipt.get('source_fingerprint', {}).get('source_reference'),
            'path_scope': receipt.get('source_fingerprint', {}).get('path_scope'),
        },
        'source_contact_status': ({
            'reference': source_contact_ref,
            'contact_status': source_contact_data.get('contact_status'),
            'sent_date': source_contact_data.get('sent_date'),
            'response_due_date': source_contact_data.get('response_due_date'),
            'status_date': source_contact_data.get('status_date'),
            'attempt_count': source_contact_data.get('attempt_count'),
            'evidence_state': source_contact_data.get('evidence_state'),
            'claim_effect': 'none; provenance gate only',
        } if source_contact_data is not None else None),
        'source_post_readout_context_receipt': ({
            'reference': source_context_ref,
            'receipt_state': source_context_data.get('receipt_state'),
            'source_post_readout_recheck': source_context_data.get('source_post_readout_recheck'),
            'source_csv_sha256': source_context_data.get('source_csv', {}).get('sha256'),
            'source_truth_class': source_context_data.get('source_truth_class'),
            'evidence_state': source_context_data.get('evidence_state'),
            'claim_effect': 'none; post-readout provenance gate only',
        } if source_context_data is not None else None),
        'triage_outcome': triage.get('outcome'),
        'next_action': triage.get('next_action'),
        'next_local_artifact': next_local_artifact,
        'artifacts': artifacts,
        'content_minimization': {
            'receipt_copies_owner_answers': False,
            'triage_json_copies_owner_answers': False,
            'manifest_copies_owner_answers': False,
            'proceed_staged_note_may_hold_minimized_surviving_answers': triage.get('outcome') == 'PROCEED-STAGED',
            'archive_controlled_output_allowed': False,
            'source_contact_status_required': source_contact_data is not None,
            'source_post_readout_context_receipt_required': source_context_data is not None,
        },
        'claim_ceiling': CLAIM_CEILING,
        'ft0181_status': 'live',
    }
    # Write the final manifest once. Do not embed the manifest's own hash inside
    # the manifest: that creates a stale self-reference because adding the hash
    # mutates the bytes that were just hashed. The CLI response returns the
    # manifest hash out-of-band instead.
    manifest['self_hash_policy'] = 'bundle-manifest SHA-256 is returned out-of-band by the CLI and not embedded in bundle-manifest.json to avoid stale self-hash mutation.'
    manifest_meta = write_json(out / 'bundle-manifest.json', manifest)

    return {
        'ok': True,
        'output_dir': relative_to_root(out),
        'triage_outcome': triage.get('outcome'),
        'source_truth_class': receipt.get('source_truth_class'),
        'source_csv_sha256': source_hash,
        'next_local_artifact': next_local_artifact,
        'source_contact_status': source_contact_ref,
        'source_post_readout_context_receipt': source_context_ref,
        'artifacts': {**manifest['artifacts'], 'bundle_manifest': manifest_meta},
        'claim_ceiling': CLAIM_CEILING,
        'ft0181_status': 'live',
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description='Run the bounded FT-0181 owner-reply receipt/triage/staging intake bundle locally.')
    parser.add_argument('csv_path', type=Path)
    parser.add_argument('--output-dir', type=Path, help='Directory for local bundle outputs. Defaults to scratch/field/ft0181/owner-reply-intakes/<csv-stem>-<sha>.')
    parser.add_argument('--source-contact-status', type=Path, help='Scratch contact-status.json from the active SENT_AWAITING_REPLY or REASK_AWAITING_REPLY clock that produced this returned CSV route.')
    parser.add_argument('--source-post-readout-context-receipt', type=Path, help='Scratch post-readout-context-receipt.json linking a new-context recheck to this same returned CSV/source packet.')
    parser.add_argument('--json', action='store_true', help='Emit machine-readable JSON only.')
    args = parser.parse_args(argv)
    try:
        result = bundle_intake(args.csv_path, args.output_dir, args.source_contact_status, args.source_post_readout_context_receipt)
    except ValueError as exc:
        print(str(exc))
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"ok: {str(result['ok']).lower()}")
        print(f"output_dir: {result['output_dir']}")
        print(f"triage_outcome: {result['triage_outcome']}")
        print(f"source_truth_class: {result['source_truth_class']}")
        print(f"next_local_artifact: {result['next_local_artifact']}")
        print(f"source_contact_status: {result['source_contact_status']}")
        print(f"claim_ceiling: {result['claim_ceiling']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
