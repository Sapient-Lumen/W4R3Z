#!/usr/bin/env python3
"""Score a scratch-only teacher/tutor micro-pilot packet for local run readiness.

This tool reads the packet created by prepare_teacher_tutor_micro_pilot_pack.py and
writes a local scratch scorecard. It separates entry readiness for one bounded local
cycle from post-cycle readiness for owner review, because a packet should not need
post-cycle data before the first real teacher/tutor use can begin. It does not
accept evidence, update a service record, support a public claim, create custody,
or close FT-0181.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
DEFAULT_PACKET = ROOT / 'scratch' / 'field-handoff' / RECEIPT.get('revision', 'unknown') / 'teacher-tutor-micro-pilot' / 'teacher-selected-concept'
SAFE_STATUS = 'LOCAL_READINESS_ONLY_NOT_EVIDENCE'
DRY_RUN_TRACE = 'DRY-RUN-TRACE.json'
DRY_RUN_STATE = 'SYNTHETIC_AGGREGATE_DRY_RUN_NOT_EVIDENCE'
ENTRY_READY_STATUS = 'READY_FOR_LOCAL_CYCLE_NOT_EVIDENCE'
OWNER_REVIEW_READY_STATUS = 'READY_FOR_LOCAL_OWNER_REVIEW_NOT_EVIDENCE'
SYNTHETIC_READY_STATUS = 'SYNTHETIC_READY_SMOKE_NOT_EVIDENCE'
NOT_READY_STATUS = 'NOT_READY'
ALLOWED_DECISIONS = {'retire', 'repeat-narrower', 'continue-bounded', 'escalate-to-pilot-review'}
ALLOWED_FOLLOWTHROUGH_SOURCE_DECISIONS = {'repeat-narrower', 'continue-bounded'}
FOLLOWTHROUGH_SOURCE_STATE = 'FRESH_PACKET_SOURCE_RESULT_LINK_NOT_EVIDENCE'
NON_RETIRE_FOLLOWTHROUGH_DECISIONS = {'repeat-narrower', 'continue-bounded', 'escalate-to-pilot-review'}
FOLLOWTHROUGH_SPEC_LABELS = [
    'Next packet concept or narrowing constraint without identifiers',
    'One change required before any repeat or continue',
    'Fresh-packet rule acknowledged',
]
MIN_SMALL_CELL_THRESHOLD = 3
NUMBER_WORDS = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10}
REQUIRED_FILES = [
    'PACK-MANIFEST.json',
    'OWNER-PLAN.md',
    'SESSION-LOG.csv',
    'FINAL-READOUT.csv',
    'COACH-PROMPT.md',
    'RUN-CHECKLIST.md',
    'MEASURE-CARD.md',
    'OWNER-DECISION-MEMO.md',
    'CYCLE-RUN-SHEET.md',
]
SESSION_REQUIRED_PHASES = {'D1-baseline', 'D2-D3-coach-use', 'D4-transfer'}
SESSION_PHASE_ORDER = ['D1-baseline', 'D2-D3-coach-use', 'D4-transfer']
FINAL_REQUIRED_ROWS = {'1', '2', '3', '4', '5', '6', '7', '8'}
RUN_DEFINITION_HASH_ROLES = {
    'discovery_ask': 'DISCOVERY-FIRST-CONTACT.md',
    'coach_prompt': 'COACH-PROMPT.md',
    'run_checklist': 'RUN-CHECKLIST.md',
    'measure_card': 'MEASURE-CARD.md',
    'cycle_run_sheet': 'CYCLE-RUN-SHEET.md',
}
ENTRY_CHECK_IDS = {
    'packet-files-present',
    'cycle-run-sheet-present',
    'packet-is-prepared-not-run',
    'feasibility-method-boundary-present',
    'raw-protected-text-absent',
    'owner-plan-completed',
    'small-cell-threshold-usable',
    'run-definition-hash-stable',
    'followthrough-source-result-link-valid',
}
POST_CYCLE_CHECK_IDS = {
    'session-log-has-baseline-coach-transfer',
    'session-log-dates-valid-and-ordered',
    'final-readout-eight-rows-filled',
    'stop-triggers-clear',
    'owner-decision-recorded',
    'decision-followthrough-spec-recorded',
}
FORBIDDEN_TEXT_TERMS = [
    'student id', 'learner id', 'student name', 'learner name', 'full name', 'email address',
    'ssn', 'social security', 'iep', '504 plan', 'disability facts', 'accommodation facts',
    'protected status', 'gradebook row', 'raw work', 'screenshot', 'recording', 'chat transcript',
    'discipline record', 'risk score', 'api key', 'credential',
]
PLACEHOLDER_PATTERNS = [
    r'owner fills', r'owner-selected', r'owner-named', r'\[human writes', r'\bTBD\b', r'\bTODO\b',
    r'Owner signature or local attestation:\s*$', r'Decision:\s*$', r'Reason without identifiers:\s*$',
    r'Next packet concept or narrowing constraint without identifiers:\s*$',
    r'One change required before any repeat or continue:\s*$',
    r'Fresh-packet rule acknowledged:\s*$',
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Score a scratch-only teacher/tutor micro-pilot packet for local readiness.')
    parser.add_argument('--packet-dir', default=str(DEFAULT_PACKET), help='Packet directory created by make micro-pilot-pack.')
    parser.add_argument('--write', action='store_true', help='Write READINESS-SCORECARD.json and READINESS-SCORECARD.md in the packet directory.')
    parser.add_argument('--json', action='store_true', help='Print the scorecard as JSON.')
    return parser.parse_args()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def safe_packet_path(packet_dir: Path) -> None:
    resolved = packet_dir.resolve()
    try:
        resolved.relative_to((ROOT / 'scratch').resolve())
    except ValueError:
        try:
            resolved.relative_to(ROOT.resolve())
        except ValueError:
            return
        raise SystemExit('packet-dir must be under scratch/ or outside the repository; refuse release-path readiness scoring')


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8') if path.exists() else ''


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def owner_plan_prompt_sha(owner_plan: str) -> tuple[str | None, str]:
    value = owner_plan_line_value(owner_plan, 'Prompt-card SHA-256 at packet generation')
    if not value:
        return None, 'owner plan missing prompt-card SHA-256'
    match = re.search(r'\b[a-fA-F0-9]{64}\b', value)
    if not match:
        return None, 'owner plan prompt-card SHA-256 is not a 64-character digest'
    return match.group(0).lower(), 'owner plan prompt-card SHA-256 recorded'


def run_definition_hash_status(packet_dir: Path, manifest: dict, owner_plan: str) -> tuple[bool, str]:
    """Check immutable run-definition files against generation-time hashes.

    The owner plan, session log, final readout, and decision memo are intentionally
    fillable after generation. The discovery card, coach prompt, checklist, measure
    card, and one-cycle run sheet are not: if any of them drift, regenerate the
    packet so the prompt hash and reviewed run instructions stay provenance-bound.
    """
    manifest_rows = manifest.get('files') if isinstance(manifest, dict) else None
    if not isinstance(manifest_rows, list):
        return False, 'manifest missing files[] hash rows'
    by_role = {row.get('role'): row for row in manifest_rows if isinstance(row, dict)}
    problems: list[str] = []
    for role, expected_name in RUN_DEFINITION_HASH_ROLES.items():
        row = by_role.get(role)
        if not row:
            problems.append(f'manifest missing role {role}')
            continue
        rel_path = str(row.get('path') or '')
        expected_hash = str(row.get('sha256') or '').lower()
        if not expected_hash:
            problems.append(f'manifest role {role} missing sha256')
            continue
        path = ROOT / rel_path if rel_path else packet_dir / expected_name
        if not path.exists():
            problems.append(f'{expected_name} missing at manifest path')
            continue
        if path.name != expected_name:
            problems.append(f'manifest role {role} points to {path.name}, expected {expected_name}')
            continue
        current_hash = sha256_file(path)
        if current_hash != expected_hash:
            problems.append(f'{expected_name} hash drifted from PACK-MANIFEST.json')
    prompt_hash, prompt_detail = owner_plan_prompt_sha(owner_plan)
    prompt_path = packet_dir / 'COACH-PROMPT.md'
    if prompt_hash is None:
        problems.append(prompt_detail)
    elif not prompt_path.exists():
        problems.append('COACH-PROMPT.md missing for owner-plan prompt hash comparison')
    elif sha256_file(prompt_path) != prompt_hash:
        problems.append('COACH-PROMPT.md hash does not match OWNER-PLAN.md prompt-card SHA-256')
    prompt_change_value = owner_plan_line_value(owner_plan, 'Owner confirms whether the prompt card changed after generation').lower()
    if prompt_change_value and not any(marker in prompt_change_value for marker in ['unchanged', 'no change', 'did not change', 'not changed']):
        problems.append('owner plan must confirm the prompt card stayed unchanged; regenerate the packet if prompt instructions changed')
    if problems:
        return False, '; '.join(problems[:8])
    return True, 'discovery card, coach prompt, checklist, measure card, run sheet, and owner-plan prompt hash match generation-time hashes'



def followthrough_source_status(packet_dir: Path, manifest: dict) -> tuple[bool, str]:
    """Validate an optional prior-result source link for fresh follow-through packets.

    Ordinary first-cycle packets do not have this file. When it exists, the file
    must hash-link to a prior local non-evidence result with a repeat/continue
    decision; otherwise a fresh packet could hide a generic repeat or source drift.
    """
    source_path = packet_dir / 'FOLLOWTHROUGH-SOURCE-RESULT.json'
    if not source_path.exists():
        if manifest.get('fresh_packet_source_state') not in (None, 'NO_PRIOR_RESULT_SOURCE'):
            return False, 'manifest declares a follow-through source but FOLLOWTHROUGH-SOURCE-RESULT.json is missing'
        return True, 'no prior result source link; packet is first-cycle/discovery-start'
    try:
        data = json.loads(source_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        return False, f'FOLLOWTHROUGH-SOURCE-RESULT.json is unreadable JSON: {exc}'
    problems: list[str] = []
    if data.get('source_state') != FOLLOWTHROUGH_SOURCE_STATE:
        problems.append('source_state is not FRESH_PACKET_SOURCE_RESULT_LINK_NOT_EVIDENCE')
    if data.get('source_decision') not in ALLOWED_FOLLOWTHROUGH_SOURCE_DECISIONS:
        problems.append('source_decision must be repeat-narrower or continue-bounded')
    if data.get('fresh_packet_required') is not True:
        problems.append('fresh_packet_required must be true')
    if data.get('source_values_copied') is not False:
        problems.append('source_values_copied must be false')
    if 'not evidence' not in str(data.get('claim_boundary', '')).lower():
        problems.append('claim_boundary must preserve not-evidence status')
    source_result_rel = str(data.get('source_result_path') or '')
    source_sha = str(data.get('source_result_sha256') or '').lower()
    if not re.fullmatch(r'[a-f0-9]{64}', source_sha):
        problems.append('source_result_sha256 must be a 64-character lowercase digest')
    if source_result_rel:
        source_result_path = ROOT / source_result_rel
        if source_result_path.exists():
            if sha256_file(source_result_path) != source_sha:
                problems.append('source result hash no longer matches FOLLOWTHROUGH-SOURCE-RESULT.json')
        else:
            problems.append('source result path no longer exists locally for hash verification')
    else:
        problems.append('source_result_path missing')
    manifest_rows = manifest.get('files') if isinstance(manifest, dict) else []
    by_role = {row.get('role'): row for row in manifest_rows if isinstance(row, dict)}
    row = by_role.get('followthrough_source_result_json')
    if not row:
        problems.append('PACK-MANIFEST.json missing followthrough_source_result_json row')
    else:
        expected_hash = str(row.get('sha256') or '').lower()
        if expected_hash != sha256_file(source_path):
            problems.append('FOLLOWTHROUGH-SOURCE-RESULT.json hash drifted from PACK-MANIFEST.json')
    manifest_source = manifest.get('source_result_link') if isinstance(manifest.get('source_result_link'), dict) else {}
    if manifest.get('fresh_packet_source_state') != FOLLOWTHROUGH_SOURCE_STATE:
        problems.append('PACK-MANIFEST.json fresh_packet_source_state does not match source link')
    if manifest_source and manifest_source.get('source_result_sha256') != data.get('source_result_sha256'):
        problems.append('PACK-MANIFEST.json source result hash disagrees with source link file')
    if problems:
        return False, '; '.join(problems[:8])
    return True, 'fresh follow-through packet is hash-linked to a prior local non-evidence repeat/continue result without copying seed text'

def forbidden_hits(texts: Iterable[str]) -> list[str]:
    joined = '\n'.join(texts).lower()
    hits = [term for term in FORBIDDEN_TEXT_TERMS if term in joined]
    if '@' in joined:
        hits.append('email-like address marker @')
    return sorted(set(hits))



def owner_plan_line_value(text: str, label: str) -> str:
    prefix = label.lower()
    for line in text.splitlines():
        stripped = line.strip()
        lowered = stripped.lower()
        if lowered.startswith(prefix) and ':' in stripped:
            return stripped.split(':', 1)[1].strip()
    return ''


def memo_line_value(text: str, label: str) -> str:
    prefix = label.lower()
    for line in text.splitlines():
        stripped = line.strip()
        lowered = stripped.lower()
        if lowered.startswith(prefix) and ':' in stripped:
            return stripped.split(':', 1)[1].strip()
    return ''


def decision_followthrough_spec(memo: str, decision: str | None) -> dict[str, object]:
    """Check whether the source-result hash-linked fresh-packet is recorded.

    The scorer intentionally returns only status/detail and label names, not the
    memo values themselves. The values may guide a local fresh packet, but they
    must not be copied into a traveling result receipt or treated as cumulative
    evidence.
    """
    if decision not in ALLOWED_DECISIONS:
        return {
            'status': 'not_recorded',
            'required': False,
            'detail': 'decision must be recorded before follow-through seed can be checked',
            'labels_checked': FOLLOWTHROUGH_SPEC_LABELS,
        }
    values = {label: memo_line_value(memo, label) for label in FOLLOWTHROUGH_SPEC_LABELS}
    missing = [label for label, value in values.items() if not value]
    placeholder_like = [
        label for label, value in values.items()
        if value and re.search(r'owner fills|\bTBD\b|\bTODO\b|\[human writes', value, flags=re.IGNORECASE)
    ]
    not_applicable = [label for label, value in values.items() if value and re.search(r'not applicable|n/a|none', value, flags=re.IGNORECASE)]
    if decision in NON_RETIRE_FOLLOWTHROUGH_DECISIONS and not_applicable:
        return {
            'status': 'not_recorded',
            'required': True,
            'detail': 'non-retire decisions require a real de-identified follow-through seed; not-applicable values appear in: ' + ', '.join(not_applicable),
            'labels_checked': FOLLOWTHROUGH_SPEC_LABELS,
        }
    if missing or placeholder_like:
        parts = []
        if missing:
            parts.append('missing labels: ' + ', '.join(missing))
        if placeholder_like:
            parts.append('placeholder-like labels: ' + ', '.join(placeholder_like))
        return {
            'status': 'not_recorded',
            'required': decision in NON_RETIRE_FOLLOWTHROUGH_DECISIONS,
            'detail': '; '.join(parts),
            'labels_checked': FOLLOWTHROUGH_SPEC_LABELS,
        }
    if decision == 'retire':
        detail = 'retire decision includes a completed follow-through section; any fresh work still requires new discovery'
    elif decision == 'escalate-to-pilot-review':
        detail = 'separate pilot-review intent recorded without granting evidence import or pilot authority'
    else:
        detail = 'fresh-packet follow-through seed recorded without copying local details into the scorecard'
    return {
        'status': 'recorded',
        'required': decision in NON_RETIRE_FOLLOWTHROUGH_DECISIONS,
        'detail': detail,
        'labels_checked': FOLLOWTHROUGH_SPEC_LABELS,
        'values_copied_to_scorecard': False,
    }


def small_cell_threshold(owner_plan: str) -> tuple[int | None, str]:
    """Extract the local release/suppression floor from OWNER-PLAN.md.

    The packet may stay local, but the result receipt is an artifact that can travel.
    Requiring a numeric threshold before cycle entry prevents a completed cycle from
    producing exact tiny counts or rates that should have remained local only.
    """
    value = owner_plan_line_value(owner_plan, 'Local small-cell/suppression threshold')
    if not value:
        return None, 'missing Local small-cell/suppression threshold value'
    if re.search(r'owner fills|\bTBD\b|\bTODO\b', value, flags=re.IGNORECASE):
        return None, 'threshold still has a placeholder value'
    match = re.search(r'\b(\d+)\b', value)
    if match:
        threshold = int(match.group(1))
    else:
        word_match = re.search(r'\b(' + '|'.join(NUMBER_WORDS) + r')\b', value.lower())
        if not word_match:
            return None, 'threshold must include an integer cell floor'
        threshold = NUMBER_WORDS[word_match.group(1)]
    if threshold < MIN_SMALL_CELL_THRESHOLD:
        return threshold, f'threshold {threshold} is below the release-suppression floor {MIN_SMALL_CELL_THRESHOLD}'
    return threshold, f'threshold {threshold} recorded'

def placeholder_hits(text: str) -> list[str]:
    hits = []
    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
            hits.append(pattern)
    return hits


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        return [], []
    with path.open(newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        return list(reader.fieldnames or []), [dict(row) for row in reader]




def session_log_chronology(rows: list[dict[str, str]]) -> tuple[bool, str, dict[str, object]]:
    """Validate local event chronology from SESSION-LOG.csv rows.

    The first legitimate field cycle depends on an event sequence that actually
    could have happened: baseline before coach use, coach use before transfer,
    and local owner review/result recording after the dated cycle rows. This
    helper intentionally checks only aggregate row dates; it does not put raw
    learner records or protected local schedules into the release archive.
    """
    invalid: list[str] = []
    missing: list[str] = []
    by_phase: dict[str, list[date]] = {phase: [] for phase in SESSION_PHASE_ORDER}
    dated_rows: list[tuple[date, str, int]] = []
    for row_index, row in enumerate(rows, start=2):
        if not any(nonempty(value) for value in row.values()):
            continue
        phase = (row.get('phase') or '').strip()
        raw_date = (row.get('date') or '').strip()
        if not raw_date:
            missing.append(f'row {row_index} date')
            continue
        try:
            parsed = date.fromisoformat(raw_date)
        except ValueError:
            invalid.append(f'row {row_index} date {raw_date!r}')
            continue
        dated_rows.append((parsed, phase, row_index))
        if phase in by_phase:
            by_phase[phase].append(parsed)
    if missing or invalid:
        parts = []
        if missing:
            parts.append('missing dates: ' + ', '.join(missing[:8]))
        if invalid:
            parts.append('invalid ISO dates: ' + ', '.join(invalid[:8]))
        return False, '; '.join(parts), {'missing_dates': missing, 'invalid_dates': invalid}
    if not dated_rows:
        return False, 'no dated session rows present', {}
    missing_phase_dates = [phase for phase in SESSION_PHASE_ORDER if not by_phase.get(phase)]
    if missing_phase_dates:
        return False, 'missing dated required phases: ' + ', '.join(missing_phase_dates), {
            'missing_phase_dates': missing_phase_dates,
            'phase_date_bounds': {},
        }
    bounds: dict[str, dict[str, str]] = {}
    for phase in SESSION_PHASE_ORDER:
        values = sorted(by_phase[phase])
        bounds[phase] = {'first': values[0].isoformat(), 'last': values[-1].isoformat()}
    ordering_errors: list[str] = []
    for earlier, later in zip(SESSION_PHASE_ORDER, SESSION_PHASE_ORDER[1:]):
        earlier_last = max(by_phase[earlier])
        later_first = min(by_phase[later])
        if earlier_last > later_first:
            ordering_errors.append(f'{earlier} latest {earlier_last.isoformat()} is after {later} earliest {later_first.isoformat()}')
    latest = max(parsed for parsed, _, _ in dated_rows)
    earliest = min(parsed for parsed, _, _ in dated_rows)
    summary = {
        'earliest_session_date': earliest.isoformat(),
        'latest_session_date': latest.isoformat(),
        'phase_date_bounds': bounds,
        'row_count_with_dates': len(dated_rows),
        'chronology_rule': 'D1-baseline <= D2-D3-coach-use <= D4-transfer; owner review and result recording must occur on or after the latest session date',
    }
    if ordering_errors:
        summary['ordering_errors'] = ordering_errors
        return False, '; '.join(ordering_errors), summary
    return True, f'session dates are ISO and ordered; latest session date is {latest.isoformat()}', summary

def field_payload_lines(text: str) -> list[str]:
    """Return likely operator-entered values, not boilerplate boundary warnings."""
    values: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(('#', '-', '|', '```')):
            continue
        lowered = stripped.lower()
        if any(marker in lowered for marker in ['do not ', 'without ', 'no names', 'not evidence', 'public claim ceiling']):
            continue
        if ':' in stripped:
            _, value = stripped.split(':', 1)
            if value.strip():
                values.append(value.strip())
        elif stripped.startswith('Decision') or stripped.startswith('Reason'):
            values.append(stripped)
    return values


def csv_payload_values(rows: list[dict[str, str]]) -> list[str]:
    values: list[str] = []
    for row in rows:
        for value in row.values():
            if value and value.strip():
                lowered = value.strip().lower()
                if any(marker in lowered for marker in ['do not ', 'without ', 'no names', 'no learner', 'no raw', 'not evidence']):
                    continue
                values.append(value.strip())
    return values


def as_int(value: str) -> int | None:
    value = (value or '').strip()
    if value == '':
        return None
    try:
        return int(value)
    except ValueError:
        return None


def nonempty(value: str | None) -> bool:
    return bool((value or '').strip())


def check_stage(check_id: str) -> str:
    if check_id in ENTRY_CHECK_IDS:
        return 'entry'
    if check_id in POST_CYCLE_CHECK_IDS:
        return 'post_cycle'
    return 'unknown'


def score(packet_dir: Path) -> dict:
    paths = {name: packet_dir / name for name in REQUIRED_FILES}
    missing = [name for name, path in paths.items() if not path.exists()]
    manifest = {}
    if paths['PACK-MANIFEST.json'].exists():
        manifest = json.loads(paths['PACK-MANIFEST.json'].read_text(encoding='utf-8'))
    dry_run_trace = {}
    dry_run_path = packet_dir / DRY_RUN_TRACE
    if dry_run_path.exists():
        dry_run_trace = json.loads(dry_run_path.read_text(encoding='utf-8'))
    is_synthetic_dry_run = dry_run_trace.get('dry_run_state') == DRY_RUN_STATE

    owner_plan = read_text(paths['OWNER-PLAN.md'])
    memo = read_text(paths['OWNER-DECISION-MEMO.md'])
    plan_placeholders = placeholder_hits(owner_plan)
    memo_placeholders = placeholder_hits(memo)
    threshold_value, threshold_detail = small_cell_threshold(owner_plan)
    run_definition_ok, run_definition_detail = run_definition_hash_status(packet_dir, manifest, owner_plan)
    source_link_ok, source_link_detail = followthrough_source_status(packet_dir, manifest)

    session_fields, session_rows = read_csv_rows(paths['SESSION-LOG.csv'])
    session_chronology_ok, session_chronology_detail, session_chronology_summary = session_log_chronology(session_rows)
    final_fields, final_rows = read_csv_rows(paths['FINAL-READOUT.csv'])
    payload_texts = field_payload_lines(owner_plan) + field_payload_lines(memo) + csv_payload_values(session_rows) + csv_payload_values(final_rows)
    forbidden = forbidden_hits(payload_texts)

    phases_present = {row.get('phase', '').strip() for row in session_rows if row.get('phase', '').strip()}
    missing_session_phases = sorted(SESSION_REQUIRED_PHASES - phases_present)
    session_numeric_rows = []
    stop_trigger_counts = {'access_issue_count': 0, 'answer_leakage_count': 0, 'inappropriate_action_count': 0}
    phase_attempt_totals = {phase: 0 for phase in SESSION_REQUIRED_PHASES}
    invalid_numeric = []
    for idx, row in enumerate(session_rows, start=2):
        if not any(nonempty(v) for v in row.values()):
            continue
        numeric_present = False
        for field in ['aggregate_attempt_count', 'aggregate_success_or_mastery_count', 'owner_review_minutes', 'correction_minutes', 'fallback_or_optout_count', 'access_issue_count', 'answer_leakage_count', 'inappropriate_action_count']:
            raw = row.get(field, '')
            parsed = as_int(raw)
            if nonempty(raw) and parsed is None:
                invalid_numeric.append(f'SESSION-LOG.csv row {idx} field {field}')
            if parsed is not None:
                numeric_present = True
                if field == 'aggregate_attempt_count':
                    phase = (row.get('phase') or '').strip()
                    if phase in phase_attempt_totals:
                        phase_attempt_totals[phase] += parsed
        for field in stop_trigger_counts:
            parsed = as_int(row.get(field, ''))
            if parsed is not None:
                stop_trigger_counts[field] += parsed
        if numeric_present:
            session_numeric_rows.append(idx)

    missing_attempt_phases = sorted(phase for phase, attempts in phase_attempt_totals.items() if attempts <= 0)

    final_row_ids = {row.get('row_id', '').strip() for row in final_rows if row.get('row_id', '').strip()}
    missing_final_rows = sorted(FINAL_REQUIRED_ROWS - final_row_ids)
    final_incomplete = []
    decision_value = None
    for idx, row in enumerate(final_rows, start=2):
        row_id = row.get('row_id', '').strip()
        if row_id in FINAL_REQUIRED_ROWS:
            if not nonempty(row.get('aggregate_value')):
                final_incomplete.append(f'row {row_id} aggregate_value')
            if not nonempty(row.get('method_note')):
                final_incomplete.append(f'row {row_id} method_note')
            if row_id == '8':
                decision_value = (row.get('aggregate_value') or '').strip()

    final_payload_values = [((row.get('aggregate_value') or '').strip(), (row.get('method_note') or '').strip()) for row in final_rows]
    final_payload_attempted = any(value for pair in final_payload_values for value in pair if value and 'fill locally' not in value.lower() and 'aggregate-only' not in value.lower())

    memo_decision = None
    m = re.search(r'^Decision:\s*(\S+)\s*$', memo, flags=re.IGNORECASE | re.MULTILINE)
    if m:
        memo_decision = m.group(1).strip()
    followthrough_spec = decision_followthrough_spec(memo, memo_decision)
    followthrough_spec_ok = followthrough_spec.get('status') == 'recorded'

    checks = [
        {
            'id': 'packet-files-present',
            'stage': 'entry',
            'status': 'pass' if not missing else 'fail',
            'detail': 'all required packet files are present' if not missing else 'missing: ' + ', '.join(missing),
        },
        {
            'id': 'cycle-run-sheet-present',
            'stage': 'entry',
            'status': 'pass' if paths.get('CYCLE-RUN-SHEET.md', packet_dir / 'CYCLE-RUN-SHEET.md').exists() else 'fail',
            'detail': 'one-cycle run sheet is present to convert entry readiness into exactly one bounded local cycle' if paths.get('CYCLE-RUN-SHEET.md', packet_dir / 'CYCLE-RUN-SHEET.md').exists() else 'CYCLE-RUN-SHEET.md missing; regenerate the packet before local use',
        },
        {
            'id': 'packet-is-prepared-not-run',
            'stage': 'entry',
            'status': 'pass' if manifest.get('packet_state') == 'PREPARED_NOT_RUN' and manifest.get('evidence_state') == 'NOT_EVIDENCE' else 'fail',
            'detail': 'manifest preserves prepared/not-evidence boundary' if manifest else 'manifest missing or unreadable',
        },
        {
            'id': 'feasibility-method-boundary-present',
            'stage': 'entry',
            'status': 'pass' if manifest.get('evaluation_class') == 'FEASIBILITY_AND_USABILITY_ONLY' and 'Tool/provider:' in owner_plan and 'Local small-cell/suppression threshold:' in owner_plan and 'Method boundary:' in owner_plan else 'fail',
            'detail': 'packet records feasibility-only class, intervention identity, privacy threshold, and no-efficacy boundary' if owner_plan else 'owner plan missing or method boundary absent',
        },
        {
            'id': 'raw-protected-text-absent',
            'stage': 'entry',
            'status': 'pass' if not forbidden else 'fail',
            'detail': 'no forbidden raw/protected/identifying markers detected' if not forbidden else 'detected: ' + ', '.join(forbidden),
        },
        {
            'id': 'owner-plan-completed',
            'stage': 'entry',
            'status': 'pass' if owner_plan and not plan_placeholders else 'fail',
            'detail': 'owner plan appears locally completed for cycle entry' if owner_plan and not plan_placeholders else 'owner plan still has placeholders/blanks: ' + ', '.join(plan_placeholders[:8]),
        },
        {
            'id': 'small-cell-threshold-usable',
            'stage': 'entry',
            'status': 'pass' if threshold_value is not None and threshold_value >= MIN_SMALL_CELL_THRESHOLD else 'fail',
            'detail': 'numeric local suppression threshold is usable for result redaction: ' + threshold_detail if threshold_value is not None and threshold_value >= MIN_SMALL_CELL_THRESHOLD else threshold_detail,
        },
        {
            'id': 'run-definition-hash-stable',
            'stage': 'entry',
            'status': 'pass' if run_definition_ok else 'fail',
            'detail': run_definition_detail,
        },
        {
            'id': 'followthrough-source-result-link-valid',
            'stage': 'entry',
            'status': 'pass' if source_link_ok else 'fail',
            'detail': source_link_detail,
        },
        {
            'id': 'session-log-has-baseline-coach-transfer',
            'stage': 'post_cycle',
            'status': 'pass' if not missing_session_phases and not missing_attempt_phases and session_numeric_rows and not invalid_numeric else 'fail',
            'detail': 'session log has required phases and nonzero aggregate attempt rows' if not missing_session_phases and not missing_attempt_phases and session_numeric_rows and not invalid_numeric else 'missing phases: ' + ', '.join(missing_session_phases) + '; zero-attempt phases: ' + ', '.join(missing_attempt_phases) + '; invalid numeric: ' + ', '.join(invalid_numeric[:8]),
        },
        {
            'id': 'session-log-dates-valid-and-ordered',
            'stage': 'post_cycle',
            'status': 'pass' if session_chronology_ok else 'fail',
            'detail': session_chronology_detail,
        },
        {
            'id': 'final-readout-eight-rows-filled',
            'stage': 'post_cycle',
            'status': 'pass' if not missing_final_rows and not final_incomplete else 'fail',
            'detail': 'final readout has all eight aggregate rows filled' if not missing_final_rows and not final_incomplete else 'missing rows: ' + ', '.join(missing_final_rows) + '; incomplete: ' + ', '.join(final_incomplete[:12]),
        },
        {
            'id': 'stop-triggers-clear',
            'stage': 'post_cycle',
            'status': 'pass' if all(v == 0 for v in stop_trigger_counts.values()) and session_numeric_rows else 'fail',
            'detail': 'access/answer-leakage/inappropriate-action counts are zero' if all(v == 0 for v in stop_trigger_counts.values()) and session_numeric_rows else 'stop-trigger counts: ' + json.dumps(stop_trigger_counts, sort_keys=True),
        },
        {
            'id': 'owner-decision-recorded',
            'stage': 'post_cycle',
            'status': 'pass' if (decision_value in ALLOWED_DECISIONS and memo_decision in ALLOWED_DECISIONS and not memo_placeholders) else 'fail',
            'detail': 'owner decision is one of the allowed bounded decisions' if (decision_value in ALLOWED_DECISIONS and memo_decision in ALLOWED_DECISIONS and not memo_placeholders) else f'final decision={decision_value!r}; memo decision={memo_decision!r}; memo placeholders={memo_placeholders[:6]}',
        },
        {
            'id': 'decision-followthrough-spec-recorded',
            'stage': 'post_cycle',
            'status': 'pass' if followthrough_spec_ok else 'fail',
            'detail': str(followthrough_spec.get('detail')),
        },
    ]
    entry_failures = [row for row in checks if row['stage'] == 'entry' and row['status'] != 'pass']
    post_cycle_failures = [row for row in checks if row['stage'] == 'post_cycle' and row['status'] != 'pass']
    post_cycle_payload_attempted = bool(session_numeric_rows or final_payload_attempted or memo_decision)
    if entry_failures:
        status = NOT_READY_STATUS
        readiness_stage = 'needs_entry_completion'
    elif post_cycle_failures:
        if post_cycle_payload_attempted:
            status = NOT_READY_STATUS
            readiness_stage = 'post_cycle_repair_needed'
        else:
            status = NOT_READY_STATUS if is_synthetic_dry_run else ENTRY_READY_STATUS
            readiness_stage = 'cycle_entry_ready' if not is_synthetic_dry_run else 'synthetic_incomplete'
    elif is_synthetic_dry_run:
        status = SYNTHETIC_READY_STATUS
        readiness_stage = 'synthetic_complete_rehearsal'
    else:
        status = OWNER_REVIEW_READY_STATUS
        readiness_stage = 'post_cycle_owner_review_ready'

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    next_actions: list[str] = []
    if status == NOT_READY_STATUS:
        if entry_failures:
            if any(c['id'] == 'owner-plan-completed' and c['status'] != 'pass' for c in checks):
                next_actions.append('Complete discovery, intervention identity, participation, privacy, fallback, numeric small-cell threshold, any prior-result source link, and protected local review fields in OWNER-PLAN.md before learner-facing work.')
            if any(c['id'] == 'raw-protected-text-absent' and c['status'] != 'pass' for c in checks):
                next_actions.append('Remove raw/protected/identifying material before any further use.')
            if any(c['id'] in {'run-definition-hash-stable', 'followthrough-source-result-link-valid'} and c['status'] != 'pass' for c in checks):
                next_actions.append('Regenerate the packet if the discovery card, coach prompt, run checklist, measure card, cycle run sheet, or follow-through source link changed after generation; do not locally patch run-defining instructions.')
            missing_entry_ids = [row['id'] for row in entry_failures if row['id'] not in {'owner-plan-completed', 'raw-protected-text-absent', 'run-definition-hash-stable', 'followthrough-source-result-link-valid'}]
            if missing_entry_ids:
                next_actions.append('Repair entry packet structure before any local cycle: ' + ', '.join(missing_entry_ids) + '.')
        else:
            if readiness_stage == 'post_cycle_repair_needed':
                next_actions.append('Repair or clear partially recorded post-cycle rows before proceeding; dated session rows must be ISO, baseline/coach/transfer ordered, owner-review/result dates must follow the latest session date, and non-retire decisions must include a completed fresh-packet follow-through seed.')
            else:
                next_actions.append('Synthetic dry-run trace is present but post-cycle rehearsal fields are incomplete; regenerate or discard this rehearsal packet before real work.')
    elif status == ENTRY_READY_STATUS:
        next_actions.append('Run at most one locally approved teacher/tutor feasibility cycle using the completed OWNER-PLAN.md, CYCLE-RUN-SHEET.md, RUN-CHECKLIST.md, and COACH-PROMPT.md; human review remains mandatory before any learner-facing use.')
        next_actions.append('After the cycle, record aggregate baseline, coach-use, descriptive no-AI transfer, stop-trigger, workload, fallback/opt-out, and learner-voice counts in SESSION-LOG.csv and FINAL-READOUT.csv; then rerun readiness.')
        next_actions.append('Do not record owner-review stop, result receipt, evidence import, service update, or public claim from entry readiness alone.')
    elif status == SYNTHETIC_READY_STATUS:
        next_actions.append('Synthetic dry-run path is coherent; delete it and generate a fresh packet before any real local cycle.')
    else:
        next_actions.append('Owner may review the minimized descriptive feasibility readout locally; do not infer efficacy, import, publish, or update service authority without a separate accepted evidence route.')

    return {
        'scorecard_state': SAFE_STATUS,
        'revision': RECEIPT.get('revision'),
        'packet_dir': rel(packet_dir),
        'generated_at': generated_at,
        'status': status,
        'readiness_stage': readiness_stage,
        'synthetic_dry_run': is_synthetic_dry_run,
        'dry_run_trace': rel(dry_run_path) if is_synthetic_dry_run else None,
        'owner_decision': decision_value,
        'memo_decision': memo_decision,
        'decision_followthrough_spec': followthrough_spec,
        'checks': checks,
        'entry_checks_passed': len([row for row in checks if row['stage'] == 'entry' and row['status'] == 'pass']),
        'entry_checks_total': len([row for row in checks if row['stage'] == 'entry']),
        'post_cycle_checks_passed': len([row for row in checks if row['stage'] == 'post_cycle' and row['status'] == 'pass']),
        'post_cycle_checks_total': len([row for row in checks if row['stage'] == 'post_cycle']),
        'small_cell_threshold': threshold_value,
        'small_cell_threshold_detail': threshold_detail,
        'minimum_release_suppression_threshold': MIN_SMALL_CELL_THRESHOLD,
        'stop_trigger_counts': stop_trigger_counts,
        'session_chronology': session_chronology_summary,
        'session_chronology_detail': session_chronology_detail,
        'next_actions': next_actions,
        'claim_boundary': 'This scorecard is local feasibility-readiness support only. Entry readiness means the packet may support one locally approved teacher/tutor cycle; it is not post-cycle review, evidence, custody, deployment authority, public-claim support, or FT-0181 closure. A synthetic dry-run scorecard is rehearsal only. The run-definition hash check protects prompt/run provenance but does not estimate efficacy or prove learning/access/safety/fairness/workload/effectiveness.',
    }


def write_markdown(path: Path, card: dict) -> None:
    lines = [
        '# Teacher/tutor micro-pilot readiness scorecard',
        '',
        f"State: `{card['scorecard_state']}`",
        f"Revision: `{card['revision']}`",
        f"Packet: `{card['packet_dir']}`",
        f"Status: `{card['status']}`",
        f"Readiness stage: `{card.get('readiness_stage')}`",
        f"Synthetic dry run: `{card.get('synthetic_dry_run')}`",
        '',
        '## Checks',
        '',
        '| Stage | Check | Status | Detail |',
        '|---|---|---|---|',
    ]
    for row in card['checks']:
        detail = str(row['detail']).replace('|', '\\|')
        lines.append(f"| `{row.get('stage', check_stage(row['id']))}` | `{row['id']}` | `{row['status']}` | {detail} |")
    lines.extend(['', '## Session chronology', '', '```json', json.dumps(card.get('session_chronology', {}), indent=2, sort_keys=True), '```', '', '## Next actions', ''])
    for action in card['next_actions']:
        lines.append(f'- {action}')
    lines.extend(['', '## Boundary', '', card['claim_boundary'], ''])
    path.write_text('\n'.join(lines), encoding='utf-8')


def main() -> None:
    args = parse_args()
    packet_dir = Path(args.packet_dir)
    if not packet_dir.is_absolute():
        packet_dir = ROOT / packet_dir
    safe_packet_path(packet_dir)
    if not packet_dir.exists():
        raise SystemExit(f'packet directory missing: {rel(packet_dir)}')
    card = score(packet_dir)
    if args.write:
        (packet_dir / 'READINESS-SCORECARD.json').write_text(json.dumps(card, indent=2) + '\n', encoding='utf-8')
        write_markdown(packet_dir / 'READINESS-SCORECARD.md', card)
    if args.json:
        print(json.dumps(card, indent=2))
    else:
        passed = len([c for c in card['checks'] if c['status'] == 'pass'])
        print(f"micro-pilot-readiness: {card['status']} ({passed}/{len(card['checks'])} checks pass; entry {card['entry_checks_passed']}/{card['entry_checks_total']}) for {rel(packet_dir)}")
        for action in card['next_actions'][:6]:
            print(f'- {action}')


if __name__ == '__main__':
    main()
