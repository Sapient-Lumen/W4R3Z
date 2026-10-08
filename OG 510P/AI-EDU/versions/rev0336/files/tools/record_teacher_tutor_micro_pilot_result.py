#!/usr/bin/env python3
"""Record a scratch-local teacher/tutor micro-pilot aggregate result.

This utility runs only after a completed packet has passed readiness and a human
local owner-review stop record exists. It summarizes aggregate packet rows and
hash-locks the owner-reviewed packet so an operator has one result receipt, but
it does not accept evidence, create custody, update service authority, support a
public claim, or close FT-0181.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from score_teacher_tutor_micro_pilot_readiness import (
    DEFAULT_PACKET,
    ROOT,
    MIN_SMALL_CELL_THRESHOLD,
    score,
    safe_packet_path,
    small_cell_threshold,
    field_payload_lines,
    csv_payload_values,
    read_csv_rows,
    session_log_chronology,
)
from record_teacher_tutor_micro_pilot_owner_review import (
    REVIEW_STATE,
    packet_hashes,
    rel,
    safe_output_path,
    no_identity_or_raw_text,
)

RECEIPT = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
RESULT_STATE = 'LOCAL_MICRO_PILOT_RESULT_RECORDED_NOT_EVIDENCE'
CONFIRMATION = 'human-recorded-local-micro-pilot-aggregate-result'
ALLOWED_DECISIONS = {'retire', 'repeat-narrower', 'continue-bounded', 'escalate-to-pilot-review'}

DECISION_FOLLOWTHROUGH = {
    'retire': {
        'decision_class': 'stop_without_repeat',
        'operator_action': 'Stop this local line. Do not repeat, widen, import, publish, or reopen from this result unless a new discovery conversation identifies a different local problem and generates a fresh packet.',
        'fresh_packet_required': False,
        'evidence_escalation_allowed': False,
        'claim_boundary': 'Retire is a local stop/redesign decision only, not evidence of harm or ineffectiveness at scale.',
    },
    'repeat-narrower': {
        'decision_class': 'fresh_narrower_packet_only',
        'operator_action': 'Repeat only by generating a fresh packet for a narrower owner-selected problem, with a new owner plan, run-definition hashes, baseline/transfer choice, threshold, and chronology. Do not append another cycle to this receipt as cumulative evidence.',
        'fresh_packet_required': True,
        'evidence_escalation_allowed': False,
        'claim_boundary': 'A repeat-narrower decision may guide one redesigned local feasibility cycle only; it is not a learning, workload, safety, access, or effectiveness claim.',
    },
    'continue-bounded': {
        'decision_class': 'one_fresh_bounded_cycle_only',
        'operator_action': 'Continue only as one fresh bounded local feasibility cycle after a new source-result-linked packet and owner-plan refresh. Do not pool cycles, average results, or infer trend/effect without a separate pre-specified accepted evidence route.',
        'fresh_packet_required': True,
        'evidence_escalation_allowed': False,
        'claim_boundary': 'Continue-bounded is local workflow permission for one next feasibility cycle only; it is not efficacy evidence or service authority.',
    },
    'escalate-to-pilot-review': {
        'decision_class': 'separate_future_gate_required',
        'operator_action': 'Stop the local micro-cycle lane and prepare a separate future pilot-review gate only if an accountable owner supplies an accepted route, pre-specified design, privacy/access review, and evidence-custody plan. This result receipt cannot itself escalate, import, or authorize a pilot.',
        'fresh_packet_required': None,
        'evidence_escalation_allowed': False,
        'claim_boundary': 'Escalate-to-pilot-review records interest in a separate review; it is not accepted SRC2+ evidence, not deployment approval, and not public-claim support.',
    },
}
SESSION_REQUIRED_PHASES = {'D1-baseline', 'D2-D3-coach-use', 'D4-transfer'}
SENSITIVE_FINAL_ROW_IDS = {'1', '2', '3', '4', '6', '7'}
NUMBER_WORDS = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10}
FORBIDDEN_TEXT_TERMS = [
    'student id', 'learner id', 'student name', 'learner name', 'full name', 'email address',
    'ssn', 'social security', 'iep', '504 plan', 'disability facts', 'accommodation facts',
    'protected status', 'gradebook row', 'raw work', 'screenshot', 'recording', 'chat transcript',
    'discipline record', 'risk score', 'api key', 'credential',
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Record a local aggregate teacher/tutor micro-pilot result after owner review.')
    parser.add_argument('--packet-dir', default=str(DEFAULT_PACKET), help='Packet directory created by make micro-pilot-pack and completed locally.')
    parser.add_argument('--owner-review-record', default='', help='OWNER-REVIEW-STOP.json path. Defaults to PACKET/OWNER-REVIEW-STOP.json.')
    parser.add_argument('--record-date', required=True, help='Date this local result receipt is recorded, YYYY-MM-DD.')
    parser.add_argument('--operator-role', default='local pilot operator role', help='Role-only recorder label; no names or email addresses.')
    parser.add_argument('--operator-confirmation', required=True, help=f'Required token: {CONFIRMATION}')
    parser.add_argument('--output-dir', help='Optional scratch/external directory for MICRO-PILOT-RESULT.*; defaults to the packet directory.')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing MICRO-PILOT-RESULT files.')
    parser.add_argument('--json', action='store_true', help='Print the result record as JSON.')
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def validate_iso_date(value: str, field: str) -> str:
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise SystemExit(f'{field} must be YYYY-MM-DD') from exc
    return value


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise SystemExit(f'cannot parse JSON {rel(path)}: {exc}') from exc


def as_int(value: str | None, *, field: str, row_index: int) -> int:
    raw = (value or '').strip()
    if raw == '':
        raise SystemExit(f'SESSION-LOG.csv row {row_index} missing {field}')
    try:
        parsed = int(raw)
    except ValueError as exc:
        raise SystemExit(f'SESSION-LOG.csv row {row_index} invalid integer {field}: {raw!r}') from exc
    if parsed < 0:
        raise SystemExit(f'SESSION-LOG.csv row {row_index} negative {field}: {raw!r}')
    return parsed


def forbidden_hits(values: list[str]) -> list[str]:
    joined = '\n'.join(values).lower()
    hits = [term for term in FORBIDDEN_TEXT_TERMS if term in joined]
    if '@' in joined:
        hits.append('email-like address marker @')
    return sorted(set(hits))


def read_session_rows(packet_dir: Path) -> list[dict[str, str]]:
    path = packet_dir / 'SESSION-LOG.csv'
    if not path.exists():
        raise SystemExit('missing SESSION-LOG.csv')
    with path.open(newline='', encoding='utf-8') as fh:
        return [dict(row) for row in csv.DictReader(fh)]


def read_final_rows(packet_dir: Path) -> list[dict[str, str]]:
    path = packet_dir / 'FINAL-READOUT.csv'
    if not path.exists():
        raise SystemExit('missing FINAL-READOUT.csv')
    with path.open(newline='', encoding='utf-8') as fh:
        return [dict(row) for row in csv.DictReader(fh)]


def suppressible_int(value: int, threshold: int) -> int | str:
    if value == 0:
        return 0
    if value < threshold:
        return 'suppressed_below_threshold'
    return value


def summarize_session(rows: list[dict[str, str]], threshold: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    phases_seen = set()
    summaries: list[dict[str, Any]] = []
    raw_stop_totals = {'fallback_or_optout_count': 0, 'access_issue_count': 0, 'answer_leakage_count': 0, 'inappropriate_action_count': 0}
    for row_index, row in enumerate(rows, start=2):
        if not any((value or '').strip() for value in row.values()):
            continue
        phase = (row.get('phase') or '').strip()
        if phase:
            phases_seen.add(phase)
        attempts = as_int(row.get('aggregate_attempt_count'), field='aggregate_attempt_count', row_index=row_index)
        successes = as_int(row.get('aggregate_success_or_mastery_count'), field='aggregate_success_or_mastery_count', row_index=row_index)
        if successes > attempts:
            raise SystemExit(f'SESSION-LOG.csv row {row_index} success/mastery count exceeds attempt count')
        review_minutes = as_int(row.get('owner_review_minutes'), field='owner_review_minutes', row_index=row_index)
        correction_minutes = as_int(row.get('correction_minutes'), field='correction_minutes', row_index=row_index)
        row_stop_raw = {}
        for field in raw_stop_totals:
            value = as_int(row.get(field), field=field, row_index=row_index)
            row_stop_raw[field] = value
            raw_stop_totals[field] += value
        below_threshold = attempts < threshold
        if below_threshold:
            attempt_out: int | str = 'suppressed_below_threshold'
            success_out: int | str = 'suppressed_below_threshold'
            rate_out: float | None = None
            row_stop_out = {field: suppressible_int(value, threshold) for field, value in row_stop_raw.items()}
        else:
            attempt_out = attempts
            success_out = successes
            rate_out = round(successes / attempts, 4) if attempts else None
            row_stop_out = row_stop_raw
        summaries.append({
            'phase': phase,
            'aggregate_attempt_count': attempt_out,
            'aggregate_success_or_mastery_count': success_out,
            'success_or_mastery_rate': rate_out,
            'suppression_applied': below_threshold,
            'suppression_reason': f'phase attempt count below threshold {threshold}' if below_threshold else None,
            'owner_review_minutes': review_minutes,
            'correction_minutes': correction_minutes,
            'move_type_used': (row.get('move_type_used') or '').strip(),
            'stop_continue_decision': (row.get('stop_continue_decision') or '').strip(),
            'stop_counts': row_stop_out,
        })
    missing = sorted(SESSION_REQUIRED_PHASES - phases_seen)
    if missing:
        raise SystemExit('SESSION-LOG.csv missing required phases: ' + ', '.join(missing))
    stop_totals: dict[str, Any] = {}
    for field, value in raw_stop_totals.items():
        stop_totals[field] = suppressible_int(value, threshold)
    return summaries, stop_totals


def has_numeric_or_small_word(value: str, threshold: int) -> bool:
    lowered = (value or '').lower()
    if not lowered.strip():
        return False
    if re.search(r'(?<![\w.])\d+(?:\.\d+)?\s*%|(?<![\w.])\d+\s*/\s*\d+|\bn\s*[=<>]\s*\d+|\b(rate|percent|percentage|count|counts|sample|sampled)\b', lowered):
        return True
    for word, number in NUMBER_WORDS.items():
        if 0 < number < threshold and re.search(rf'\b{word}\b', lowered):
            return True
    for match in re.finditer(r'(?<![\w.])\d+(?![\w.])', lowered):
        number = int(match.group(0))
        if number != 0 or threshold <= 1:
            return True
    return False


def redact_final_field(value: str, *, row_id: str, field: str, threshold: int) -> tuple[str, bool]:
    text = (value or '').strip()
    if not text:
        return text, False
    if row_id == '8' and field == 'aggregate_value':
        return text, False
    if row_id in SENSITIVE_FINAL_ROW_IDS and has_numeric_or_small_word(text, threshold):
        return 'masked_in_result_receipt; see thresholded session_summary or local protected packet', True
    if row_id != '5' and has_numeric_or_small_word(text, threshold):
        return 'masked_in_result_receipt; see local protected packet', True
    return text, False


def summarize_final(rows: list[dict[str, str]], threshold: int) -> tuple[list[dict[str, Any]], str, list[dict[str, str]]]:
    compact: list[dict[str, Any]] = []
    decision = ''
    suppressed: list[dict[str, str]] = []
    for row in rows:
        row_id = (row.get('row_id') or '').strip()
        if not row_id:
            continue
        row_out: dict[str, Any] = {
            'row_id': row_id,
            'phase': (row.get('phase') or '').strip(),
            'measure_family': (row.get('measure_family') or '').strip(),
        }
        row_suppressed = False
        for field in ['aggregate_value', 'method_note', 'decision_effect']:
            original = (row.get(field) or '').strip()
            redacted, was_redacted = redact_final_field(original, row_id=row_id, field=field, threshold=threshold)
            row_out[field] = redacted
            if was_redacted:
                row_suppressed = True
                suppressed.append({'row_id': row_id, 'field': field, 'reason': f'numeric or small-cell-sensitive final-readout text suppressed at threshold {threshold}'})
        row_out['suppression_applied'] = row_suppressed
        compact.append(row_out)
        if row_id == '8':
            decision = (row.get('aggregate_value') or '').strip()
    if decision not in ALLOWED_DECISIONS:
        raise SystemExit(f'FINAL-READOUT.csv row 8 decision must be one of {sorted(ALLOWED_DECISIONS)}; found {decision!r}')
    return compact, decision, suppressed


def packet_text_payload(packet_dir: Path, session_rows: list[dict[str, str]], final_rows: list[dict[str, str]], operator_role: str) -> list[str]:
    """Return likely operator-entered payload, not boilerplate warning text."""
    values: list[str] = [operator_role]
    for name in ['OWNER-PLAN.md', 'OWNER-DECISION-MEMO.md']:
        path = packet_dir / name
        if path.exists():
            values.extend(field_payload_lines(path.read_text(encoding='utf-8')))
    values.extend(csv_payload_values(session_rows))
    values.extend(csv_payload_values(final_rows))
    return values



def session_chronology_for_packet(packet_dir: Path) -> tuple[dict[str, object], str]:
    _, rows = read_csv_rows(packet_dir / 'SESSION-LOG.csv')
    ok, detail, summary = session_log_chronology(rows)
    if not ok:
        raise SystemExit('SESSION-LOG.csv chronology invalid at result record: ' + detail)
    latest = summary.get('latest_session_date')
    if not isinstance(latest, str) or not latest:
        raise SystemExit('SESSION-LOG.csv chronology missing latest session date')
    return summary, detail

def validate_owner_review(packet_dir: Path, owner_review_path: Path) -> dict[str, Any]:
    if not owner_review_path.exists():
        raise SystemExit(f'owner review record missing: {rel(owner_review_path)}')
    review = load_json(owner_review_path)
    if review.get('review_state') != REVIEW_STATE:
        raise SystemExit(f'owner review record state must be {REVIEW_STATE}')
    expected_packet = rel(packet_dir)
    if review.get('packet_dir') != expected_packet:
        raise SystemExit(f'owner review packet mismatch: expected {expected_packet}, found {review.get("packet_dir")!r}')
    current_hashes = packet_hashes(packet_dir)
    recorded_hashes = review.get('packet_hashes') or {}
    mismatches = []
    for name, value in recorded_hashes.items():
        if current_hashes.get(name) != value:
            mismatches.append(name)
    if mismatches:
        raise SystemExit('packet files changed after owner review: ' + ', '.join(sorted(mismatches)))
    if review.get('decision') not in ALLOWED_DECISIONS:
        raise SystemExit('owner review decision is not bounded')
    return review


def visible_rate(row: dict[str, Any] | None) -> float | None:
    if not row or row.get('suppression_applied'):
        return None
    rate = row.get('success_or_mastery_rate')
    return rate if isinstance(rate, (int, float)) else None


def local_delta(session_summary: list[dict[str, Any]], threshold: int) -> dict[str, Any]:
    by_phase = {row['phase']: row for row in session_summary}
    baseline = by_phase.get('D1-baseline')
    transfer = by_phase.get('D4-transfer')
    coach = by_phase.get('D2-D3-coach-use')
    base_rate = visible_rate(baseline)
    transfer_rate = visible_rate(transfer)
    coach_rate = visible_rate(coach)
    delta = None
    suppressed = any(row.get('suppression_applied') for row in [baseline, transfer, coach] if row)
    if base_rate is not None and transfer_rate is not None:
        delta = round(transfer_rate - base_rate, 4)
    return {
        'baseline_success_or_mastery_rate': base_rate,
        'coach_use_success_or_mastery_rate': coach_rate,
        'transfer_success_or_mastery_rate': transfer_rate,
        'transfer_minus_baseline_rate_delta': delta,
        'suppression_applied': suppressed,
        'suppression_threshold': threshold,
        'suppression_note': 'small cells are masked; hidden exact counts/rates must remain local and outside this receipt' if suppressed else 'no phase rate was masked by the configured threshold',
        'interpretation_boundary': 'descriptive local aggregate only; not causal evidence, not accepted SRC2+, and not a public learning claim',
    }



def decision_followthrough(decision: str) -> dict[str, Any]:
    """Return the bounded local next-step map for a result decision."""
    try:
        row = DECISION_FOLLOWTHROUGH[decision]
    except KeyError as exc:
        raise SystemExit(f'unsupported local decision for follow-through: {decision!r}') from exc
    return {
        'decision': decision,
        **row,
        'previous_result_reuse_rule': 'The completed packet/result may be read for local learning only. Any repeat or continue requires a new source-result-linked packet, and any escalation requires a separate route; this result must not be reused as accepted evidence, cumulative effect data, service authority, public-claim support, or FT-0181 closure material.',
    }

def claim_boundary(decision: str) -> str:
    return (
        'This micro-pilot result receipt is local operator support only. It summarizes an owner-reviewed aggregate packet, masks configured small cells, and hash-locks the local result path, but it does not accept evidence, create custody, prove learning/access/safety/workload/effectiveness, authorize service use, support public claims, or close FT-0181. '
        f'The local decision `{decision}` may guide the next local cycle only; escalation, public statements, service-record authority changes, or evidence acceptance require a separate future route.'
    )


def build_result(packet_dir: Path, *, owner_review_path: Path, record_date: str, operator_role: str, out_dir: Path) -> dict[str, Any]:
    card = score(packet_dir)
    owner_plan = (packet_dir / 'OWNER-PLAN.md').read_text(encoding='utf-8') if (packet_dir / 'OWNER-PLAN.md').exists() else ''
    threshold, threshold_detail = small_cell_threshold(owner_plan)
    if threshold is None or threshold < MIN_SMALL_CELL_THRESHOLD:
        raise SystemExit(f'owner plan must contain numeric small-cell threshold >= {MIN_SMALL_CELL_THRESHOLD}: {threshold_detail}')
    if card.get('status') != 'READY_FOR_LOCAL_OWNER_REVIEW_NOT_EVIDENCE':
        raise SystemExit(f'packet readiness must remain READY_FOR_LOCAL_OWNER_REVIEW_NOT_EVIDENCE; found {card.get("status")}')
    if card.get('synthetic_dry_run') or (packet_dir / 'DRY-RUN-TRACE.json').exists():
        raise SystemExit('refuse to record a local result for a synthetic dry-run packet')
    review = validate_owner_review(packet_dir, owner_review_path)
    session_chronology, session_chronology_detail = session_chronology_for_packet(packet_dir)
    latest_session_date = str(session_chronology['latest_session_date'])
    if date.fromisoformat(review['review_date']) < date.fromisoformat(latest_session_date):
        raise SystemExit(f'owner review date {review["review_date"]} is before latest SESSION-LOG.csv date {latest_session_date}')
    if date.fromisoformat(record_date) < date.fromisoformat(review['review_date']):
        raise SystemExit('record-date must be on or after owner review date')
    if date.fromisoformat(record_date) < date.fromisoformat(latest_session_date):
        raise SystemExit(f'record-date {record_date} must be on or after latest SESSION-LOG.csv date {latest_session_date}')
    session_rows = read_session_rows(packet_dir)
    final_rows = read_final_rows(packet_dir)
    hits = forbidden_hits(packet_text_payload(packet_dir, session_rows, final_rows, operator_role))
    if hits:
        raise SystemExit('refuse result record with raw/protected/identifying markers: ' + ', '.join(hits))
    session_summary, stop_totals = summarize_session(session_rows, threshold)
    final_summary, final_decision, final_readout_suppressed_fields = summarize_final(final_rows, threshold)
    if final_decision != review.get('decision'):
        raise SystemExit(f'final decision {final_decision!r} does not match owner review {review.get("decision")!r}')
    followthrough = decision_followthrough(final_decision)
    record = {
        'result_state': RESULT_STATE,
        'revision': RECEIPT.get('revision'),
        'generated_at': utc_now(),
        'record_date': record_date,
        'packet_dir': rel(packet_dir),
        'output_dir': rel(out_dir),
        'owner_review_record': rel(owner_review_path),
        'owner_review_state': review.get('review_state'),
        'owner_review_date': review.get('review_date'),
        'latest_session_date': latest_session_date,
        'event_chronology_rule': 'session row dates must be ordered baseline <= coach-use <= transfer; owner review must be on/after latest session date; result record must be on/after owner review',
        'session_chronology': session_chronology,
        'session_chronology_detail': session_chronology_detail,
        'operator_role': operator_role,
        'decision': final_decision,
        'readiness_status': card.get('status'),
        'session_summary': session_summary,
        'final_readout_summary': final_summary,
        'final_readout_suppressed_fields': final_readout_suppressed_fields,
        'final_readout_receipt_rule': 'numeric/small-cell-sensitive final-readout free text is suppressed in this receipt; use session_summary for thresholded aggregates and keep exact local details outside the archive',
        'local_descriptive_delta': local_delta(session_summary, threshold),
        'small_cell_threshold': threshold,
        'suppression_effect': 'counts and rates below the local threshold are masked in this receipt; exact small-cell values remain local only',
        'stop_trigger_totals': stop_totals,
        'packet_hashes_at_result': packet_hashes(packet_dir),
        'owner_review_packet_hashes': review.get('packet_hashes'),
        'operator_confirmation_recorded': True,
        'evidence_effect': 'not_evidence',
        'custody_effect': 'none',
        'service_authority_effect': 'none',
        'public_claim_effect': 'none',
        'closure_effect': 'does_not_close_ft0181',
        'decision_followthrough_spec': card.get('decision_followthrough_spec', {}),
        'decision_followthrough_seed_rule': 'the owner memo follow-through seed was required before review but its local text is not copied into this result receipt',
        'fresh_packet_preflight': {
            'required_for_non_retire': final_decision in {'repeat-narrower', 'continue-bounded', 'escalate-to-pilot-review'},
            'source': 'OWNER-DECISION-MEMO.md source-result hash-linked fresh-packet, read locally only',
            'receipt_copies_seed_text': False,
            'minimum_before_any_new_packet': [
                'owner selects the next concept or narrowing constraint without identifiers',
                'owner names one required change before repeat or continue',
                'operator generates a fresh packet with SOURCE_RESULT pointing to this result receipt rather than appending to this result',
                'no cycles are pooled as evidence without a separate accepted route',
            ],
        },
        'decision_followthrough': followthrough,
        'next_action': followthrough['operator_action'],
        'claim_boundary': claim_boundary(final_decision) + ' ' + followthrough['previous_result_reuse_rule'],
    }
    return record


def write_markdown(path: Path, record: dict[str, Any]) -> None:
    lines = [
        '# Teacher/tutor micro-pilot local result receipt',
        '',
        f"State: `{record['result_state']}`",
        f"Revision: `{record['revision']}`",
        f"Packet: `{record['packet_dir']}`",
        f"Owner review: `{record['owner_review_record']}`",
        f"Record date: `{record['record_date']}`",
        f"Latest session date: `{record.get('latest_session_date')}`",
        f"Decision: `{record['decision']}`",
        f"Small-cell threshold: `{record.get('small_cell_threshold')}`",
        '',
        '## Event chronology',
        '',
        record.get('event_chronology_rule', 'not recorded'),
        '',
        '```json',
        json.dumps(record.get('session_chronology', {}), indent=2, sort_keys=True),
        '```',
        '',
        '## Final-readout receipt rule',
        '',
        record.get('final_readout_receipt_rule', 'not recorded'),
        '',
        '## Final-readout suppressed fields',
        '',
        '```json',
        json.dumps(record.get('final_readout_suppressed_fields', []), indent=2, sort_keys=True),
        '```',
        '',
        '## Descriptive local delta',
        '',
        '```json',
        json.dumps(record['local_descriptive_delta'], indent=2, sort_keys=True),
        '```',
        '',
        '## Suppression effect',
        '',
        record.get('suppression_effect', 'not recorded'),
        '',
        '## Decision follow-through seed',
        '',
        record.get('decision_followthrough_seed_rule', 'not recorded'),
        '',
        '```json',
        json.dumps(record.get('decision_followthrough_spec', {}), indent=2, sort_keys=True),
        '```',
        '',
        '## Fresh-packet preflight',
        '',
        '```json',
        json.dumps(record.get('fresh_packet_preflight', {}), indent=2, sort_keys=True),
        '```',
        '',
        '## Decision follow-through',
        '',
        '```json',
        json.dumps(record.get('decision_followthrough', {}), indent=2, sort_keys=True),
        '```',
        '',
        '## Stop-trigger totals',
        '',
        '```json',
        json.dumps(record['stop_trigger_totals'], indent=2, sort_keys=True),
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
    record_date = validate_iso_date(args.record_date, 'record-date')
    operator_role = args.operator_role.strip()
    no_identity_or_raw_text(operator_role, 'operator-role')
    packet_dir = Path(args.packet_dir)
    if not packet_dir.is_absolute():
        packet_dir = ROOT / packet_dir
    safe_packet_path(packet_dir)
    if not packet_dir.exists():
        raise SystemExit(f'packet directory missing: {rel(packet_dir)}')
    owner_review_path = Path(args.owner_review_record) if args.owner_review_record else packet_dir / 'OWNER-REVIEW-STOP.json'
    if not owner_review_path.is_absolute():
        owner_review_path = ROOT / owner_review_path
    safe_packet_path(owner_review_path.parent)
    out_dir = Path(args.output_dir) if args.output_dir else packet_dir
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    safe_output_path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / 'MICRO-PILOT-RESULT.json'
    md_path = out_dir / 'MICRO-PILOT-RESULT.md'
    if (json_path.exists() or md_path.exists()) and not args.overwrite:
        raise SystemExit('MICRO-PILOT-RESULT files already exist; pass --overwrite to replace them')
    record = build_result(packet_dir, owner_review_path=owner_review_path, record_date=record_date, operator_role=operator_role, out_dir=out_dir)
    json_path.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    write_markdown(md_path, record)
    if args.json:
        print(json.dumps(record, indent=2))
    else:
        print(f"micro-pilot-result: {record['result_state']} for {record['packet_dir']}")
        print(record['next_action'])


if __name__ == '__main__':
    main()
