#!/usr/bin/env python3
"""Run bounded FT-0181 returned-owner-reply local work.

This helper compresses the local work that follows an actual returned owner CSV:
source-provenance-gated intake, and only when the triage outcome is
PROCEED-STAGED, workbench-seed creation plus a one-screen workbench review brief.
It deliberately does not perform or simulate the human workbench review,
evidence custody, acceptance, public-claim support, live-window movement, or
FT-0181 closure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REVISION = json.loads((Path(__file__).resolve().parents[1] / 'REVISION_RECEIPT.json').read_text(encoding='utf-8')).get('revision', 'rev0000')

from ft0181_field_guards import output_allowed
from intake_owner_reply_csv import CLAIM_CEILING, bundle_intake
from prepare_ft0181_workbench_review_brief import build_review_brief
from seed_owner_packet_workbench import build_seed

ROOT = Path(__file__).resolve().parents[1]
SERVICE_ID = 'aiedu-sr-003'
DEFAULT_SESSION_ROOT = ROOT / 'scratch' / 'field' / 'ft0181' / 'returned-reply-work'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='After a real returned FT-0181 owner CSV exists, run bounded local intake and, only for PROCEED-STAGED, create the workbench seed.'
    )
    parser.add_argument('--csv', '--returned-csv', dest='csv_path', required=True, type=Path, help='Actual returned owner CSV/source packet path; must be scratch/external, not archive-controlled fixture/template/docs.')
    parser.add_argument('--source-contact-status', type=Path, help='Scratch contact-status.json from active SENT_AWAITING_REPLY or REASK_AWAITING_REPLY clock.')
    parser.add_argument('--source-post-readout-context-receipt', type=Path, help='Scratch post-readout-context-receipt.json tied to the same returned owner context CSV.')
    parser.add_argument('--output-dir', type=Path, help='Local session output directory. Defaults to scratch/field/ft0181/returned-reply-work/<csv-stem>-<sha>.')
    parser.add_argument('--intake-dir', type=Path, help='Local owner-reply intake output directory. Defaults to scratch/field/ft0181/owner-reply-intakes/<csv-stem>-<sha>.')
    parser.add_argument('--seed-dir', type=Path, help='Local workbench seed output directory. Defaults to scratch/field/ft0181/owner-reply-workbench-seeds/<csv-stem>-<sha>.')
    parser.add_argument('--review-brief-dir', type=Path, help='Local review brief output directory. Defaults to scratch/field/ft0181/owner-workbench-review-briefs/<csv-stem>-<sha>.')
    parser.add_argument('--overwrite', action='store_true', help='Replace existing session/intake/seed directories.')
    parser.add_argument('--json', action='store_true', help='Print machine-readable result.')
    return parser.parse_args()


def resolve_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def default_session_dir(csv_path: Path) -> Path:
    source = resolve_path(csv_path).resolve()
    digest = sha256_file(source)[:12] if source.exists() and source.is_file() else 'missing-csv'
    stem = source.stem.replace(' ', '-').replace('/', '-')[:48] or 'returned-owner-reply'
    return DEFAULT_SESSION_ROOT / f'{stem}-{digest}'


def default_intake_dir(csv_path: Path) -> Path:
    source = resolve_path(csv_path).resolve()
    digest = sha256_file(source)[:12] if source.exists() and source.is_file() else 'missing-csv'
    stem = source.stem.replace(' ', '-').replace('/', '-')[:48] or 'owner-reply'
    return ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-reply-intakes' / f'{stem}-{digest}'


def default_seed_dir(csv_path: Path) -> Path:
    source = resolve_path(csv_path).resolve()
    digest = sha256_file(source)[:12] if source.exists() and source.is_file() else 'missing-csv'
    stem = source.stem.replace(' ', '-').replace('/', '-')[:48] or 'owner-reply'
    return ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-reply-workbench-seeds' / f'{stem}-{digest}'


def default_review_brief_dir(csv_path: Path) -> Path:
    source = resolve_path(csv_path).resolve()
    digest = sha256_file(source)[:12] if source.exists() and source.is_file() else 'missing-csv'
    stem = source.stem.replace(' ', '-').replace('/', '-')[:48] or 'owner-reply'
    return ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-workbench-review-briefs' / f'{stem}-{digest}'


def clean_or_block_dir(path: Path, *, overwrite: bool) -> tuple[bool, str]:
    allowed, boundary = output_allowed(path, archive_root=ROOT)
    if not allowed:
        return False, boundary
    if path.exists() and any(path.iterdir()):
        if not overwrite:
            return False, 'use --overwrite or choose an empty directory'
        for child in path.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    path.mkdir(parents=True, exist_ok=True)
    return True, boundary


def session_markdown(session: dict[str, Any]) -> str:
    intake = session.get('intake_result', {}) if isinstance(session.get('intake_result'), dict) else {}
    seed = session.get('seed_result', {}) if isinstance(session.get('seed_result'), dict) else {}
    review_brief = session.get('review_brief_result', {}) if isinstance(session.get('review_brief_result'), dict) else {}
    lines = [
        '# FT-0181 returned-reply local work session',
        '',
        f"Session state: `{session.get('session_state')}`",
        'Evidence effect: `not_evidence`',
        'Closure effect: `does_not_close_ft0181`',
        'Public claim effect: `none`',
        '',
        'This session compresses only local handling after a real returned owner CSV/source packet exists.',
        'It runs bounded intake and creates a workbench seed only when the intake outcome is PROCEED-STAGED.',
        'It does not review, accept, normalize, custody-stage, publish, activate, or close anything.',
        '',
        '## Source and provenance',
        '',
        f"Returned CSV: `{session.get('source_csv_ref')}`",
        f"Returned CSV SHA-256: `{session.get('source_csv_sha256')}`",
        f"Source contact status: `{session.get('source_contact_status') or 'none'}`",
        f"Source post-readout context receipt: `{session.get('source_post_readout_context_receipt') or 'none'}`",
        '',
        '## Intake result',
        '',
        f"Intake output: `{intake.get('output_dir', 'none')}`",
        f"Triage outcome: `{intake.get('triage_outcome', 'none')}`",
        f"Next local artifact: `{intake.get('next_local_artifact', 'none')}`",
    ]
    if seed:
        lines.extend([
            '',
            '## Workbench seed result',
            '',
            f"Seed path: `{seed.get('seed_path', 'none')}`",
            f"Acceptance state: `{seed.get('acceptance_state', 'none')}`",
            f"Required next surface: `{seed.get('required_next_surface', 'none')}`",
        ])
    if review_brief:
        lines.extend([
            '',
            '## Workbench review brief result',
            '',
            f"Brief path: `{review_brief.get('brief_path', 'none')}`",
            f"Review effect: `{review_brief.get('review_effect', 'none')}`",
            f"Required next surface: `{review_brief.get('required_next_surface', 'none')}`",
        ])
    lines.extend([
        '',
        '## Next action',
        '',
        str(session.get('recommended_next_action') or 'Open the local intake outcome and follow the router; do not widen the request.'),
        '',
        '## Hard boundary',
        '',
        '- Do not paste raw owner answers, learner rows, protected facts, small cells, route details, screenshots, vendor dashboards, transcripts, prompts, credentials, or security payloads into release surfaces.',
        '- Do not treat this session, the intake bundle, or the seed as SRC2+ acceptance, evidence custody, public-summary support, live-window authorization, lifecycle movement, or closure.',
        '- If the intake does not proceed, use the generated outcome note or one bounded re-ask; do not create a new registry/control family to compensate.',
        '',
    ])
    return '\n'.join(lines)


def build_returned_reply_work(
    *,
    csv_path: Path,
    source_contact_status: Path | None = None,
    source_post_readout_context_receipt: Path | None = None,
    output_dir: Path | None = None,
    intake_dir: Path | None = None,
    seed_dir: Path | None = None,
    review_brief_dir: Path | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    source = resolve_path(csv_path).resolve()
    if bool(source_contact_status) == bool(source_post_readout_context_receipt):
        return {
            'ok': False,
            'outcome': 'RETURNED-REPLY-WORK-SOURCE-PROVENANCE-BLOCKED',
            'reason': 'Provide exactly one source provenance: source-contact-status or source-post-readout-context-receipt.',
            'claim_ceiling': CLAIM_CEILING,
        }
    if not source.exists() or not source.is_file():
        return {
            'ok': False,
            'outcome': 'RETURNED-REPLY-WORK-CSV-MISSING',
            'reason': f'CSV path not found: {csv_path}',
            'claim_ceiling': CLAIM_CEILING,
        }

    session_dir = resolve_path(output_dir) if output_dir is not None else default_session_dir(source)
    intake_out = resolve_path(intake_dir) if intake_dir is not None else default_intake_dir(source)
    seed_out = resolve_path(seed_dir) if seed_dir is not None else default_seed_dir(source)
    review_brief_out = resolve_path(review_brief_dir) if review_brief_dir is not None else default_review_brief_dir(source)

    session_ok, session_boundary = clean_or_block_dir(session_dir, overwrite=overwrite)
    if not session_ok:
        return {
            'ok': False,
            'outcome': 'RETURNED-REPLY-WORK-OUTPUT-BLOCKED',
            'reason': session_boundary,
            'output_dir': relative(session_dir),
            'claim_ceiling': CLAIM_CEILING,
        }

    created = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    try:
        intake_result = bundle_intake(
            source,
            output_dir=intake_out,
            source_contact_status=source_contact_status,
            source_post_readout_context_receipt=source_post_readout_context_receipt,
        )
    except ValueError as exc:
        session = {
            'ok': False,
            'session_type': 'FT-0181-returned-reply-local-work',
            'session_version': REVISION,
            'created_at_utc': created,
            'session_state': 'intake-blocked',
            'outcome': 'RETURNED-REPLY-WORK-INTAKE-BLOCKED',
            'reason': str(exc),
            'source_csv_ref': relative(source),
            'source_csv_sha256': sha256_file(source),
            'source_contact_status': relative(resolve_path(source_contact_status).resolve()) if source_contact_status else None,
            'source_post_readout_context_receipt': relative(resolve_path(source_post_readout_context_receipt).resolve()) if source_post_readout_context_receipt else None,
            'claim_ceiling': CLAIM_CEILING,
            'evidence_effect': 'not_evidence',
            'closure_effect': 'does_not_close_ft0181',
            'public_claim_effect': 'none',
        }
        (session_dir / 'returned-reply-work-session.json').write_text(json.dumps(session, indent=2) + '\n', encoding='utf-8')
        (session_dir / 'RETURNED-REPLY-WORK-SESSION.md').write_text(session_markdown(session), encoding='utf-8')
        session['output_dir'] = relative(session_dir)
        session['session_artifact'] = relative(session_dir / 'returned-reply-work-session.json')
        return session

    seed_result: dict[str, Any] | None = None
    review_brief_result: dict[str, Any] | None = None
    session_state = 'intake-routed-non-proceed'
    recommended = 'Open the local intake outcome note; follow the bounded re-ask/block/no-owner route and do not widen the request.'
    if intake_result.get('triage_outcome') == 'PROCEED-STAGED':
        try:
            seed_result = build_seed(Path(intake_result['output_dir']), output_dir=seed_out)
        except ValueError as exc:
            session_state = 'seed-blocked-after-proceed-intake'
            recommended = 'Inspect the seed block and rerun owner-reply-workbench-seed only from the unedited intake bundle; do not copy answers into release surfaces.'
            seed_result = {
                'ok': False,
                'outcome': 'WORKBENCH-SEED-BLOCKED',
                'reason': str(exc),
                'claim_ceiling': CLAIM_CEILING,
            }
        else:
            try:
                review_brief_result = build_review_brief(
                    seed=Path(seed_result['seed_path']),
                    output_dir=review_brief_out,
                    overwrite=overwrite,
                )
            except Exception as exc:
                session_state = 'review-brief-blocked-after-seed'
                recommended = (
                    'Inspect the review-brief block and rerun owner-workbench-review-brief only from the unedited '
                    'NOT_ACCEPTED seed; do not copy answers into release surfaces.'
                )
                review_brief_result = {
                    'ok': False,
                    'outcome': 'WORKBENCH-REVIEW-BRIEF-BLOCKED',
                    'reason': str(exc),
                    'claim_ceiling': CLAIM_CEILING,
                }
            else:
                session_state = 'review-brief-created-human-review-required'
                recommended = (
                    f"Open {review_brief_result.get('summary_path')} and docs/30-operations/ft0181-owner-packet-workbench.md; "
                    'a human must choose one bounded route and fill counts before running owner-workbench-review. '
                    'No custody, acceptance, claim upgrade, live-window movement, or closure is authorized by this brief.'
                )

    session = {
        'ok': bool(intake_result.get('ok')) and (seed_result is None or bool(seed_result.get('ok'))) and (review_brief_result is None or bool(review_brief_result.get('ok'))),
        'session_type': 'FT-0181-returned-reply-local-work',
        'session_version': REVISION,
        'created_at_utc': created,
        'session_state': session_state,
        'source_csv_ref': relative(source),
        'source_csv_sha256': sha256_file(source),
        'source_contact_status': relative(resolve_path(source_contact_status).resolve()) if source_contact_status else None,
        'source_post_readout_context_receipt': relative(resolve_path(source_post_readout_context_receipt).resolve()) if source_post_readout_context_receipt else None,
        'intake_result': intake_result,
        'seed_result': seed_result,
        'review_brief_result': review_brief_result,
        'recommended_next_action': recommended,
        'claim_ceiling': CLAIM_CEILING,
        'evidence_effect': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'forbidden_effects': [
            'human-review-automation',
            'raw-answer-copy-to-release',
            'custody-or-acceptance',
            'service-record-edit',
            'public-claim-upgrade',
            'live-window-activation',
            'lifecycle-or-closure',
        ],
    }
    (session_dir / 'returned-reply-work-session.json').write_text(json.dumps(session, indent=2) + '\n', encoding='utf-8')
    (session_dir / 'RETURNED-REPLY-WORK-SESSION.md').write_text(session_markdown(session), encoding='utf-8')
    session['output_dir'] = relative(session_dir)
    session['session_artifact'] = relative(session_dir / 'returned-reply-work-session.json')
    return session


def main() -> int:
    args = parse_args()
    result = build_returned_reply_work(
        csv_path=args.csv_path,
        source_contact_status=args.source_contact_status,
        source_post_readout_context_receipt=args.source_post_readout_context_receipt,
        output_dir=args.output_dir,
        intake_dir=args.intake_dir,
        seed_dir=args.seed_dir,
        review_brief_dir=args.review_brief_dir,
        overwrite=args.overwrite,
    )
    if args.json:
        print(json.dumps(result, indent=2))
    elif result.get('ok'):
        print(f"run_ft0181_returned_reply_work: OK ({result['session_state']})")
        print(f"output_dir: {result.get('output_dir')}")
        print(f"recommended_next_action: {result.get('recommended_next_action')}")
    else:
        raise SystemExit(f"run_ft0181_returned_reply_work: {result.get('outcome')} ({result.get('reason')})")
    return 0 if result.get('ok') else 2


if __name__ == '__main__':
    raise SystemExit(main())
