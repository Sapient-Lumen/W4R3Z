#!/usr/bin/env python3
"""Create a local FT-0181 owner-packet workbench seed from an intake bundle.

This utility consumes only bundle metadata after a returned owner CSV has already
been receipted, triaged, and routed. It never upgrades the packet to SRC2+,
never copies owner answers from the CSV or proceed-staged note, and never writes
into archive-controlled directories. Its purpose is to make the next human step
explicit: open the owner packet workbench with source hashes and a NOT_ACCEPTED
boundary already in hand.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from ft0181_field_guards import field_scratch_lane_error, archive_relative, output_allowed, owner_contact_status_integrity_error, owner_post_readout_context_receipt_integrity_error

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_OUTPUT_BLOCK_ROOTS = {'docs', 'examples', 'fixtures', 'schemas', 'templates', 'tools'}
WORKBENCH_SURFACE = 'docs/30-operations/ft0181-owner-packet-workbench.md'
CLAIM_CEILING = (
    'Workbench seed only; not SRC2+ acceptance, not custody evidence, not closure evidence, '
    'not public-summary support, and not proof of learning, safety, access, workload, '
    'compliance, scale, or effectiveness.'
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def relative_to_root(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def is_archive_output_path(path: Path) -> bool:
    try:
        rel = path.resolve().relative_to(ROOT)
    except ValueError:
        return False
    if not rel.parts:
        return True
    return rel.parts[0] in ARCHIVE_OUTPUT_BLOCK_ROOTS or len(rel.parts) == 1


def default_output_dir(bundle_dir: Path) -> Path:
    manifest = bundle_dir / 'bundle-manifest.json'
    digest = sha256_file(manifest)[:12] if manifest.exists() else 'missingmanifest'
    stem = bundle_dir.name.replace(' ', '-').replace('/', '-')[:48] or 'owner-reply-bundle'
    return ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-reply-workbench-seeds' / f'{stem}-{digest}'


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def artifact_path(bundle_dir: Path, artifact: dict) -> Path:
    raw = artifact.get('path')
    if not raw:
        raise ValueError('artifact missing path')
    path = ROOT / raw if not Path(raw).is_absolute() else Path(raw)
    if not path.exists():
        alt = bundle_dir / Path(raw).name
        if alt.exists():
            path = alt
    return path


def verify_artifact(bundle_dir: Path, name: str, artifact: dict) -> dict:
    path = artifact_path(bundle_dir, artifact)
    if not path.exists():
        raise ValueError(f'{name} artifact missing on disk: {artifact.get("path")}')
    digest = sha256_file(path)
    expected = artifact.get('sha256')
    if expected and digest != expected:
        raise ValueError(f'{name} artifact hash mismatch: expected {expected}, got {digest}')
    return {'path': relative_to_root(path), 'sha256': digest, 'size_bytes': path.stat().st_size}


def seed_block(message: str, **extra) -> ValueError:
    payload = {
        'ok': False,
        'outcome': 'WORKBENCH-SEED-SOURCE-CLOCK-BLOCKED',
        'message': message,
        'claim_ceiling': CLAIM_CEILING,
    }
    payload.update(extra)
    return ValueError(json.dumps(payload, indent=2))


def validate_bundle_source_contact_status(manifest: dict) -> dict:
    """Revalidate the contact clock preserved by the intake bundle.

    Rev0273 made returned CSV intake depend on an active local contact clock. The
    workbench seed must not trust a hand-edited bundle manifest, because that
    would re-open the same false-progress path one step later. This re-check is
    provenance only: the contact clock remains not-evidence and cannot support
    public claims or close FT-0181.
    """
    if manifest.get('content_minimization', {}).get('source_contact_status_required') is not True:
        raise seed_block('Intake bundle does not preserve source_contact_status_required=true; rerun owner-reply intake through owner-field-next.')
    source = manifest.get('source_contact_status')
    if not isinstance(source, dict):
        raise seed_block('Intake bundle missing source_contact_status provenance; rerun owner-reply intake through owner-field-next.')
    ref = source.get('reference')
    if not isinstance(ref, str) or not ref:
        raise seed_block('source_contact_status.reference must be a non-empty archive-relative scratch path.')
    status_path = (ROOT / ref).resolve()
    inside, parts = archive_relative(status_path, archive_root=ROOT)
    if not inside or not parts or parts[0] != 'scratch':
        raise seed_block('source_contact_status.reference must resolve under archive scratch/.', source_contact_status_ref=ref)
    lane_error = field_scratch_lane_error(status_path, archive_root=ROOT, field_name='source_contact_status.reference')
    if lane_error:
        raise seed_block(lane_error, source_contact_status_ref=ref)
    if status_path.name != 'contact-status.json' or not status_path.exists() or not status_path.is_file():
        raise seed_block('source_contact_status.reference must point to an existing contact-status.json file.', source_contact_status_ref=ref)
    try:
        status_data = load_json(status_path)
    except (OSError, json.JSONDecodeError) as exc:
        raise seed_block('source_contact_status.reference is not readable JSON.', source_contact_status_ref=ref, error=str(exc))
    integrity_error = owner_contact_status_integrity_error(status_data, archive_root=ROOT)
    if integrity_error:
        raise seed_block('source_contact_status cannot source workbench seed: ' + integrity_error, source_contact_status_ref=relative_to_root(status_path))
    expected_pairs = {
        'contact_status': status_data.get('contact_status'),
        'sent_date': status_data.get('sent_date'),
        'response_due_date': status_data.get('response_due_date'),
        'status_date': status_data.get('status_date'),
        'attempt_count': status_data.get('attempt_count'),
        'evidence_state': status_data.get('evidence_state'),
    }
    for key, expected in expected_pairs.items():
        if source.get(key) != expected:
            raise seed_block(
                f'source_contact_status.{key} does not match referenced contact-status.json',
                source_contact_status_ref=relative_to_root(status_path),
                expected=expected,
                actual=source.get(key),
            )
    if source.get('claim_effect') != 'none; provenance gate only':
        raise seed_block('source_contact_status.claim_effect must remain provenance-only.', source_contact_status_ref=relative_to_root(status_path))
    return {
        'reference': relative_to_root(status_path),
        'contact_status': status_data.get('contact_status'),
        'sent_date': status_data.get('sent_date'),
        'response_due_date': status_data.get('response_due_date'),
        'status_date': status_data.get('status_date'),
        'attempt_count': status_data.get('attempt_count'),
        'evidence_state': status_data.get('evidence_state'),
        'claim_effect': 'none; provenance gate only',
        'revalidated_for_seed': True,
    }




def validate_bundle_source_post_readout_context_receipt(manifest: dict) -> dict:
    """Revalidate the post-readout context receipt preserved by intake."""
    if manifest.get('content_minimization', {}).get('source_post_readout_context_receipt_required') is not True:
        raise seed_block('Intake bundle does not preserve source_post_readout_context_receipt_required=true; rerun owner-reply intake from the post-readout context receipt command.')
    source = manifest.get('source_post_readout_context_receipt')
    if not isinstance(source, dict):
        raise seed_block('Intake bundle missing source_post_readout_context_receipt provenance; rerun owner-reply intake from the post-readout context receipt command.')
    ref = source.get('reference')
    if not isinstance(ref, str) or not ref:
        raise seed_block('source_post_readout_context_receipt.reference must be a non-empty archive-relative scratch path.')
    receipt_path = (ROOT / ref).resolve()
    inside, parts = archive_relative(receipt_path, archive_root=ROOT)
    if not inside or not parts or parts[0] != 'scratch':
        raise seed_block('source_post_readout_context_receipt.reference must resolve under archive scratch/.', source_post_readout_context_receipt_ref=ref)
    lane_error = field_scratch_lane_error(receipt_path, archive_root=ROOT, field_name='source_post_readout_context_receipt.reference')
    if lane_error:
        raise seed_block(lane_error, source_post_readout_context_receipt_ref=ref)
    if receipt_path.name != 'post-readout-context-receipt.json' or not receipt_path.exists() or not receipt_path.is_file():
        raise seed_block('source_post_readout_context_receipt.reference must point to an existing post-readout-context-receipt.json file.', source_post_readout_context_receipt_ref=ref)
    try:
        receipt_data = load_json(receipt_path)
    except (OSError, json.JSONDecodeError) as exc:
        raise seed_block('source_post_readout_context_receipt.reference is not readable JSON.', source_post_readout_context_receipt_ref=ref, error=str(exc))
    integrity_error = owner_post_readout_context_receipt_integrity_error(receipt_data, archive_root=ROOT)
    if integrity_error:
        raise seed_block('source_post_readout_context_receipt cannot source workbench seed: ' + integrity_error, source_post_readout_context_receipt_ref=relative_to_root(receipt_path))
    if source.get('source_csv_sha256') != manifest.get('source_csv', {}).get('sha256'):
        raise seed_block('source_post_readout_context_receipt.source_csv_sha256 must match intake bundle source_csv.sha256.', source_post_readout_context_receipt_ref=relative_to_root(receipt_path))
    expected_pairs = {
        'receipt_state': receipt_data.get('receipt_state'),
        'source_truth_class': receipt_data.get('source_truth_class'),
        'evidence_state': receipt_data.get('evidence_state'),
    }
    for key, expected in expected_pairs.items():
        if source.get(key) != expected:
            raise seed_block(
                f'source_post_readout_context_receipt.{key} does not match referenced post-readout-context-receipt.json',
                source_post_readout_context_receipt_ref=relative_to_root(receipt_path),
                expected=expected,
                actual=source.get(key),
            )
    if source.get('claim_effect') != 'none; post-readout provenance gate only':
        raise seed_block('source_post_readout_context_receipt.claim_effect must remain post-readout provenance-only.', source_post_readout_context_receipt_ref=relative_to_root(receipt_path))
    return {
        'reference': relative_to_root(receipt_path),
        'receipt_state': receipt_data.get('receipt_state'),
        'source_post_readout_recheck': receipt_data.get('source_post_readout_recheck'),
        'source_csv_sha256': receipt_data.get('source_csv', {}).get('sha256'),
        'source_truth_class': receipt_data.get('source_truth_class'),
        'evidence_state': receipt_data.get('evidence_state'),
        'claim_effect': 'none; post-readout provenance gate only',
        'revalidated_for_seed': True,
    }

def build_seed(bundle_dir: Path, output_dir: Path | None = None) -> dict:
    bdir = bundle_dir if bundle_dir.is_absolute() else Path.cwd() / bundle_dir
    bdir = bdir.resolve()
    manifest_path = bdir / 'bundle-manifest.json'
    if not manifest_path.exists():
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'WORKBENCH-SEED-BLOCKED',
            'message': 'bundle-manifest.json is required before creating a workbench seed.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    out = output_dir if output_dir is not None else default_output_dir(bdir)
    out = out if out.is_absolute() else ROOT / out
    allowed, output_boundary = output_allowed(out, archive_root=ROOT)
    if not allowed:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'WORKBENCH-SEED-OUTPUT-BLOCKED',
            'output_dir': relative_to_root(out),
            'output_boundary': output_boundary,
            'message': 'Workbench seeds are local/scratch artifacts and cannot be written into the release archive outside scratch or to controlled release surfaces.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    manifest = load_json(manifest_path)
    if manifest.get('bundle_type') != 'FT-0181-owner-reply-local-intake-bundle':
        raise ValueError('input is not an FT-0181 owner-reply local intake bundle')
    if manifest.get('bundle_version') == 'rev0250' and 'self_hash_policy' not in manifest:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'WORKBENCH-SEED-BLOCKED',
            'message': 'Intake bundle manifest uses the pre-rev0251 stale self-hash pattern; rerun tools/intake_owner_reply_csv.py before seeding the workbench.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if manifest.get('triage_outcome') != 'PROCEED-STAGED':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'WORKBENCH-SEED-BLOCKED',
            'triage_outcome': manifest.get('triage_outcome'),
            'message': 'Only PROCEED-STAGED local intake bundles may create a workbench seed. Use the routed outcome note/re-ask path instead.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if manifest.get('source_truth_class') == 'SRC0-SMOKE':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'WORKBENCH-SEED-SMOKE-BLOCKED',
            'source_truth_class': 'SRC0-SMOKE',
            'message': 'SRC0 smoke bundles cannot seed the owner packet workbench.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if manifest.get('ft0181_status') != 'live':
        raise ValueError('FT-0181 status must remain live in the intake bundle')
    source_contact_status = None
    source_post_readout_context_receipt = None
    source_contact_required = manifest.get('content_minimization', {}).get('source_contact_status_required') is True
    source_context_required = manifest.get('content_minimization', {}).get('source_post_readout_context_receipt_required') is True
    if source_contact_required == source_context_required:
        raise seed_block('Intake bundle must preserve exactly one source provenance gate: source_contact_status or source_post_readout_context_receipt.')
    if source_contact_required:
        source_contact_status = validate_bundle_source_contact_status(manifest)
    else:
        source_post_readout_context_receipt = validate_bundle_source_post_readout_context_receipt(manifest)

    artifacts = manifest.get('artifacts', {})
    required = ['receipt', 'triage', 'proceed_staged_note']
    missing = [name for name in required if name not in artifacts]
    if missing:
        raise ValueError('intake bundle missing required artifacts for workbench seed: ' + ', '.join(missing))

    verified = {name: verify_artifact(bdir, name, artifacts[name]) for name in required}
    receipt = load_json(artifact_path(bdir, artifacts['receipt']))
    triage = load_json(artifact_path(bdir, artifacts['triage']))
    source_hash = manifest.get('source_csv', {}).get('sha256')
    if receipt.get('source_fingerprint', {}).get('sha256') != source_hash:
        raise ValueError('receipt source hash does not match bundle manifest')
    if triage.get('source_csv_sha256') != source_hash:
        raise ValueError('triage source hash does not match bundle manifest')
    if triage.get('outcome') != 'PROCEED-STAGED':
        raise ValueError('triage JSON does not preserve PROCEED-STAGED outcome')

    stage_note = artifact_path(bdir, artifacts['proceed_staged_note']).read_text(encoding='utf-8')
    if source_hash not in stage_note:
        raise ValueError('proceed-staged note does not cite source CSV hash')
    for forbidden in ['SRC0-SMOKE', 'Synthetic smoke fixture']:
        if forbidden.lower() in stage_note.lower():
            raise ValueError('proceed-staged note is smoke-labeled and cannot seed workbench')

    created = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    seed = {
        'seed_type': 'FT-0181-owner-packet-workbench-seed',
        'seed_version': 'rev0275',
        'created_at_utc': created,
        'input_bundle': {
            'path': relative_to_root(bdir),
            'bundle_manifest_sha256': sha256_file(manifest_path),
            'receipt_sha256': verified['receipt']['sha256'],
            'triage_sha256': verified['triage']['sha256'],
            'proceed_staged_note_sha256': verified['proceed_staged_note']['sha256'],
        },
        'source_csv': {
            'basename': manifest.get('source_csv', {}).get('basename'),
            'sha256': source_hash,
            'reference': manifest.get('source_csv', {}).get('reference'),
            'path_scope': manifest.get('source_csv', {}).get('path_scope'),
        },
        'source_contact_status': source_contact_status,
        'source_post_readout_context_receipt': source_post_readout_context_receipt,
        'triage_outcome': 'PROCEED-STAGED',
        'source_truth_status': 'UNVERIFIED_OWNER_REPLY_PENDING_CUSTODY',
        'acceptance_state': 'NOT_ACCEPTED',
        'required_next_surface': WORKBENCH_SURFACE,
        'manual_workbench_step': 'Open the owner packet workbench and copy only minimized surviving row answers from the proceed-staged note after confirming the source is a real owner reply. Do not copy raw CSV content from the bundle manifest, receipt, or triage JSON.',
        'gates_before_any_acceptance': [
            'confirm the source path is a real owner-returned CSV and not SRC0/SRC1 rehearsal content',
            'confirm the source owner path, date range, source system, redaction assertion, and public claim ceiling still match the eight-row reply',
            'complete field-survival review in the owner packet workbench before mapping to dictionaries, import maps, custody, acceptance, public summaries, live windows, signoff, or closeout',
            'keep raw learner data, protected facts, small cells, security payloads, screenshots, gradebook rows, and vendor-only analytics local or quarantined',
        ],
        'content_minimization': {
            'copies_owner_answers': False,
            'copies_raw_csv_rows': False,
            'copies_proceed_staged_row_text': False,
            'copies_contact_details': False,
            'source_contact_status_revalidated': source_contact_status is not None,
            'source_post_readout_context_receipt_revalidated': source_post_readout_context_receipt is not None,
            'contains_hashes_and_next_steps_only': True,
        },
        'claim_ceiling': CLAIM_CEILING,
        'ft0181_status': 'live',
    }
    out.mkdir(parents=True, exist_ok=True)
    seed_text = json.dumps(seed, indent=2) + '\n'
    seed_path = out / 'workbench-seed.json'
    seed_path.write_text(seed_text, encoding='utf-8')
    return {
        'ok': True,
        'output_dir': relative_to_root(out),
        'seed_path': relative_to_root(seed_path),
        'seed_sha256': sha256_text(seed_text),
        'triage_outcome': 'PROCEED-STAGED',
        'acceptance_state': 'NOT_ACCEPTED',
        'required_next_surface': WORKBENCH_SURFACE,
        'claim_ceiling': CLAIM_CEILING,
        'ft0181_status': 'live',
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description='Create a local FT-0181 owner-packet workbench seed from a bounded owner-reply intake bundle.')
    parser.add_argument('bundle_dir', type=Path)
    parser.add_argument('--output-dir', type=Path, help='Directory for the local workbench seed. Defaults to scratch/field/ft0181/owner-reply-workbench-seeds/<bundle>-<manifest-sha>.')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    try:
        result = build_seed(args.bundle_dir, args.output_dir)
    except ValueError as exc:
        print(str(exc))
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"ok: {str(result['ok']).lower()}")
        print(f"seed_path: {result['seed_path']}")
        print(f"acceptance_state: {result['acceptance_state']}")
        print(f"required_next_surface: {result['required_next_surface']}")
        print(f"claim_ceiling: {result['claim_ceiling']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
