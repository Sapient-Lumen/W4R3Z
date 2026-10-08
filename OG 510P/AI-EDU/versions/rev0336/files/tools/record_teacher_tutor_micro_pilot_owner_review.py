#!/usr/bin/env python3
"""Record a scratch-local teacher/tutor micro-pilot owner-review stop.

This records that a human local owner reviewed a completed aggregate packet.
It refuses blank packets, synthetic dry-runs, raw/protected payload markers, and
release-path outputs. The record is an operator boundary artifact only: it is not
evidence intake, custody, service authorization, public-claim support, or FT-0181
closure.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable

from score_teacher_tutor_micro_pilot_readiness import DEFAULT_PACKET, ROOT, read_csv_rows, score, safe_packet_path, session_log_chronology

RECEIPT = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
REVIEW_STATE = 'LOCAL_OWNER_REVIEW_STOP_RECORDED_NOT_EVIDENCE'
CONFIRMATION = 'human-reviewed-local-micro-pilot-aggregate'
ALLOWED_DECISIONS = {'retire', 'repeat-narrower', 'continue-bounded', 'escalate-to-pilot-review'}
PACKET_HASH_FILES = [
    'PACK-MANIFEST.json',
    'DISCOVERY-FIRST-CONTACT.md',
    'OWNER-PLAN.md',
    'SESSION-LOG.csv',
    'FINAL-READOUT.csv',
    'COACH-PROMPT.md',
    'RUN-CHECKLIST.md',
    'MEASURE-CARD.md',
    'OWNER-DECISION-MEMO.md',
    'CYCLE-RUN-SHEET.md',
    'READINESS-SCORECARD.json',
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Record a local owner-review stop for a completed teacher/tutor micro-pilot aggregate packet.')
    parser.add_argument('--packet-dir', default=str(DEFAULT_PACKET), help='Packet directory created by make micro-pilot-pack and completed locally.')
    parser.add_argument('--review-date', required=True, help='Human local owner review date, YYYY-MM-DD.')
    parser.add_argument('--owner-role', required=True, help='Role of the local reviewing owner; no personal names or email addresses.')
    parser.add_argument('--decision', required=True, choices=sorted(ALLOWED_DECISIONS), help='Owner decision recorded in the packet and final readout.')
    parser.add_argument('--operator-confirmation', required=True, help=f'Required token: {CONFIRMATION}')
    parser.add_argument('--output-dir', help='Optional scratch/external directory for OWNER-REVIEW-STOP.*; defaults to the packet directory.')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing OWNER-REVIEW-STOP files.')
    parser.add_argument('--json', action='store_true', help='Print the record as JSON.')
    return parser.parse_args()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def validate_iso_date(value: str, field: str) -> str:
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise SystemExit(f'{field} must be YYYY-MM-DD') from exc
    return value


def safe_output_path(out_dir: Path) -> None:
    resolved = out_dir.resolve()
    try:
        resolved.relative_to((ROOT / 'scratch').resolve())
        return
    except ValueError:
        pass
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        return
    raise SystemExit('output-dir must be under scratch/ or outside the repository; refuse release-path owner-review record')


def no_identity_or_raw_text(value: str, field: str) -> None:
    lowered = value.lower()
    forbidden = ['@', 'student name', 'learner name', 'full name', 'email address', 'student id', 'learner id', 'raw work', 'gradebook', 'iep', '504 plan', 'protected status']
    hits = [term for term in forbidden if term in lowered]
    if hits:
        raise SystemExit(f'{field} must not contain identifying/raw/protected markers: ' + ', '.join(hits))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def packet_hashes(packet_dir: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for name in PACKET_HASH_FILES:
        path = packet_dir / name
        if path.exists():
            hashes[name] = sha256(path)
    return hashes


def read_final_decision(packet_dir: Path) -> str | None:
    path = packet_dir / 'FINAL-READOUT.csv'
    if not path.exists():
        return None
    with path.open(newline='', encoding='utf-8') as fh:
        for row in csv.DictReader(fh):
            if (row.get('row_id') or '').strip() == '8':
                return (row.get('aggregate_value') or '').strip()
    return None


def read_memo_decision(packet_dir: Path) -> str | None:
    path = packet_dir / 'OWNER-DECISION-MEMO.md'
    if not path.exists():
        return None
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.lower().startswith('decision:'):
            return line.split(':', 1)[1].strip().split()[0]
    return None



def session_chronology_for_packet(packet_dir: Path) -> tuple[dict[str, object], str]:
    _, rows = read_csv_rows(packet_dir / 'SESSION-LOG.csv')
    ok, detail, summary = session_log_chronology(rows)
    if not ok:
        raise SystemExit('SESSION-LOG.csv chronology invalid at owner review: ' + detail)
    latest = summary.get('latest_session_date')
    if not isinstance(latest, str) or not latest:
        raise SystemExit('SESSION-LOG.csv chronology missing latest session date')
    return summary, detail

def claim_boundary(decision: str) -> str:
    return (
        'This owner-review stop record is local operator support only. It records that a human local owner may review a minimized aggregate packet, but it does not import evidence, create custody, prove learning/access/safety/workload/effectiveness, authorize service use, support public claims, or close FT-0181. '
        f'The recorded decision `{decision}` may guide local next planning only; any escalation, public statement, service-record authority change, or evidence acceptance requires a separate future route.'
    )


def build_record(packet_dir: Path, *, review_date: str, owner_role: str, decision: str, out_dir: Path) -> dict:
    card = score(packet_dir)
    status = card.get('status')
    if status != 'READY_FOR_LOCAL_OWNER_REVIEW_NOT_EVIDENCE':
        raise SystemExit(f'packet readiness must be READY_FOR_LOCAL_OWNER_REVIEW_NOT_EVIDENCE; found {status}')
    if card.get('synthetic_dry_run') or (packet_dir / 'DRY-RUN-TRACE.json').exists():
        raise SystemExit('refuse to record owner review for a synthetic dry-run packet')
    final_decision = read_final_decision(packet_dir)
    memo_decision = read_memo_decision(packet_dir)
    if final_decision != decision or memo_decision != decision:
        raise SystemExit(f'decision mismatch: CLI={decision!r}, FINAL-READOUT={final_decision!r}, OWNER-DECISION-MEMO={memo_decision!r}')
    session_chronology, session_chronology_detail = session_chronology_for_packet(packet_dir)
    latest_session_date = str(session_chronology['latest_session_date'])
    if date.fromisoformat(review_date) < date.fromisoformat(latest_session_date):
        raise SystemExit(f'review-date {review_date} must be on or after latest SESSION-LOG.csv date {latest_session_date}')
    return {
        'review_state': REVIEW_STATE,
        'revision': RECEIPT.get('revision'),
        'generated_at': utc_now(),
        'packet_dir': rel(packet_dir),
        'output_dir': rel(out_dir),
        'review_date': review_date,
        'latest_session_date': latest_session_date,
        'event_chronology_rule': 'owner review must occur on or after the latest dated SESSION-LOG.csv row; result recording must occur on or after owner review',
        'session_chronology': session_chronology,
        'session_chronology_detail': session_chronology_detail,
        'owner_role': owner_role,
        'decision': decision,
        'readiness_status': status,
        'readiness_scorecard_state': card.get('scorecard_state'),
        'checks_passed': len([row for row in card.get('checks', []) if row.get('status') == 'pass']),
        'checks_total': len(card.get('checks', [])),
        'small_cell_threshold': card.get('small_cell_threshold'),
        'result_receipt_suppression_rule': 'mask exact counts and rates below the local threshold before any receipt travels',
        'decision_followthrough_spec': card.get('decision_followthrough_spec', {}),
        'decision_followthrough_seed_rule': 'the source-result hash-linked fresh-packet was checked for presence but its local text is not copied into the owner-review record',
        'stop_trigger_counts': card.get('stop_trigger_counts', {}),
        'packet_hash_scope': 'owner-reviewed packet files including discovery card, coach prompt, checklist, measure card, cycle run sheet, owner plan, session log, final readout, decision memo, manifest, and readiness scorecard',
        'packet_hashes': packet_hashes(packet_dir),
        'operator_confirmation_recorded': True,
        'next_action': 'Stop at local human owner review. Do not import, publish, update service authority, or close FT-0181 from this record.',
        'claim_boundary': claim_boundary(decision),
    }


def write_markdown(path: Path, record: dict) -> None:
    lines = [
        '# Teacher/tutor micro-pilot owner-review stop record',
        '',
        f"State: `{record['review_state']}`",
        f"Revision: `{record['revision']}`",
        f"Packet: `{record['packet_dir']}`",
        f"Review date: `{record['review_date']}`",
        f"Latest session date: `{record.get('latest_session_date')}`",
        f"Owner role: {record['owner_role']}",
        f"Decision: `{record['decision']}`",
        f"Small-cell threshold: `{record.get('small_cell_threshold')}`",
        f"Readiness: `{record['readiness_status']}` ({record['checks_passed']}/{record['checks_total']} checks pass)",
        '',
        '## Result receipt suppression rule',
        '',
        record.get('result_receipt_suppression_rule', 'not recorded'),
        '',
        '## Decision follow-through seed',
        '',
        record.get('decision_followthrough_seed_rule', 'not recorded'),
        '',
        '```json',
        json.dumps(record.get('decision_followthrough_spec', {}), indent=2, sort_keys=True),
        '```',
        '',
        '## Packet hash scope',
        '',
        record.get('packet_hash_scope', 'not recorded'),
        '',
        '## Event chronology',
        '',
        record.get('event_chronology_rule', 'not recorded'),
        '',
        '```json',
        json.dumps(record.get('session_chronology', {}), indent=2, sort_keys=True),
        '```',
        '',
        '## Stop-trigger counts',
        '',
        '```json',
        json.dumps(record.get('stop_trigger_counts', {}), indent=2, sort_keys=True),
        '```',
        '',
        '## Next action',
        '',
        record['next_action'],
        '',
        '## Boundary',
        '',
        record['claim_boundary'],
        '',
    ]
    path.write_text('\n'.join(lines), encoding='utf-8')


def main() -> None:
    args = parse_args()
    if args.operator_confirmation != CONFIRMATION:
        raise SystemExit(f'operator-confirmation must be exactly {CONFIRMATION}')
    review_date = validate_iso_date(args.review_date, 'review-date')
    owner_role = args.owner_role.strip()
    no_identity_or_raw_text(owner_role, 'owner-role')
    packet_dir = Path(args.packet_dir)
    if not packet_dir.is_absolute():
        packet_dir = ROOT / packet_dir
    safe_packet_path(packet_dir)
    if not packet_dir.exists():
        raise SystemExit(f'packet directory missing: {rel(packet_dir)}')
    out_dir = Path(args.output_dir) if args.output_dir else packet_dir
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    safe_output_path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / 'OWNER-REVIEW-STOP.json'
    md_path = out_dir / 'OWNER-REVIEW-STOP.md'
    if (json_path.exists() or md_path.exists()) and not args.overwrite:
        raise SystemExit('OWNER-REVIEW-STOP files already exist; pass --overwrite to replace them')
    record = build_record(packet_dir, review_date=review_date, owner_role=owner_role, decision=args.decision, out_dir=out_dir)
    json_path.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    write_markdown(md_path, record)
    if args.json:
        print(json.dumps(record, indent=2))
    else:
        print(f"micro-pilot-owner-review: {record['review_state']} for {record['packet_dir']}")
        print(record['next_action'])


if __name__ == '__main__':
    main()
