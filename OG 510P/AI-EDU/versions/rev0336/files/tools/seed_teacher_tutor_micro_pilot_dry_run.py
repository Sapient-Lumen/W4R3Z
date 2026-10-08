#!/usr/bin/env python3
"""Seed a teacher/tutor micro-pilot packet with synthetic aggregate dry-run values.

This is a rehearsal harness for the packet and readiness scorer. It writes only
synthetic aggregate values into a scratch/external packet created by
prepare_teacher_tutor_micro_pilot_pack.py. It does not run a real micro-pilot,
accept evidence, create custody, update service records, support public claims,
or close FT-0181.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
DRY_RUN_STATE = 'SYNTHETIC_AGGREGATE_DRY_RUN_NOT_EVIDENCE'
CONFIRMATION = 'synthetic-aggregate-dry-run-not-evidence'
ALLOWED_DECISIONS = {'retire', 'repeat-narrower', 'continue-bounded', 'escalate-to-pilot-review'}
REQUIRED_FILES = [
    'PACK-MANIFEST.json',
    'OWNER-PLAN.md',
    'SESSION-LOG.csv',
    'FINAL-READOUT.csv',
    'OWNER-DECISION-MEMO.md',
    'CYCLE-RUN-SHEET.md',
]
SESSION_COLUMNS = [
    'date', 'phase', 'concept_code', 'aggregate_attempt_count',
    'aggregate_success_or_mastery_count', 'move_type_used', 'owner_review_minutes',
    'correction_minutes', 'fallback_or_optout_count', 'access_issue_count',
    'answer_leakage_count', 'inappropriate_action_count', 'notes_without_identifiers',
    'stop_continue_decision',
]
FINAL_COLUMNS = [
    'row_id', 'phase', 'measure_family', 'aggregate_value', 'method_note',
    'owner_role', 'decision_effect', 'do_not_import_note',
]
FORBIDDEN_TEXT_TERMS = [
    'student id', 'learner id', 'student name', 'learner name', 'full name', 'email address',
    'ssn', 'social security', 'iep', '504 plan', 'disability facts', 'accommodation facts',
    'protected status', 'gradebook row', 'raw work', 'screenshot', 'recording', 'chat transcript',
    'discipline record', 'risk score', 'api key', 'credential',
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Seed a scratch-only teacher/tutor micro-pilot packet with synthetic aggregate dry-run values.')
    parser.add_argument('--packet-dir', required=True, help='Packet directory created by make micro-pilot-pack.')
    parser.add_argument('--operator-confirmation', required=True, help=f'Required token: {CONFIRMATION}')
    parser.add_argument('--decision', default='repeat-narrower', choices=sorted(ALLOWED_DECISIONS), help='Synthetic owner decision to record in the rehearsal packet.')
    parser.add_argument('--overwrite', action='store_true', help='Replace existing filled packet files or dry-run trace.')
    parser.add_argument('--json', action='store_true', help='Print the dry-run trace as JSON.')
    return parser.parse_args()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def safe_packet_path(packet_dir: Path) -> None:
    resolved = packet_dir.resolve()
    try:
        resolved.relative_to((ROOT / 'scratch').resolve())
        return
    except ValueError:
        pass
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        return
    raise SystemExit('packet-dir must be under scratch/ or outside the repository; refuse release-path dry-run seeding')


def forbidden_reason(values: Iterable[str]) -> str | None:
    joined = ' '.join(values).lower()
    if '@' in joined:
        return 'email-like address marker @'
    for term in FORBIDDEN_TEXT_TERMS:
        if term in joined:
            return term
    return None


def load_manifest(packet_dir: Path) -> dict:
    path = packet_dir / 'PACK-MANIFEST.json'
    if not path.exists():
        raise SystemExit(f'missing PACK-MANIFEST.json in {rel(packet_dir)}')
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('packet_state') != 'PREPARED_NOT_RUN' or data.get('evidence_state') != 'NOT_EVIDENCE':
        raise SystemExit('packet manifest must preserve PREPARED_NOT_RUN and NOT_EVIDENCE before dry-run seeding')
    return data


def require_files(packet_dir: Path) -> None:
    missing = [name for name in REQUIRED_FILES if not (packet_dir / name).exists()]
    if missing:
        raise SystemExit('packet missing required files: ' + ', '.join(missing))


def existing_run_guard(packet_dir: Path, overwrite: bool) -> None:
    trace = packet_dir / 'DRY-RUN-TRACE.json'
    if trace.exists() and not overwrite:
        raise SystemExit('dry-run trace already exists; pass --overwrite to replace it')
    readiness = packet_dir / 'READINESS-SCORECARD.json'
    if readiness.exists() and not overwrite:
        raise SystemExit('readiness scorecard already exists; pass --overwrite to rehearse over it')


def backup_packet(packet_dir: Path) -> Path:
    backup_dir = packet_dir / '.dry-run-backup'
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    backup_dir.mkdir()
    for name in REQUIRED_FILES:
        src = packet_dir / name
        if src.exists():
            shutil.copy2(src, backup_dir / name)
    return backup_dir


def write_owner_plan(path: Path, *, manifest: dict) -> None:
    owner_role = manifest.get('owner_role', 'classroom teacher or tutoring lead')
    concept_code = manifest.get('concept_code', 'teacher-selected-concept')
    prompt_hash = next((row.get('sha256') for row in manifest.get('files', []) if row.get('role') == 'coach_prompt'), 'synthetic-hash-unavailable')
    text = f"""# Teacher/tutor move-coach feasibility owner plan

Packet state: `SYNTHETIC_DRY_RUN`
Evidence state: `NOT_EVIDENCE`
Evaluation class: `FEASIBILITY_AND_USABILITY_ONLY`
Revision: `{RECEIPT.get('revision')}`

Owner role: {owner_role}

Local instructional problem and why it matters now: synthetic rehearsal of a locally selected reasoning-move problem.

Concept selected by the local owner: synthetic rehearsal for {concept_code}.

Setting and bounded window: synthetic demonstration group; synthetic bounded window.

Learner group description without identifiers: aggregate demonstration group of twelve hypothetical attempts.

Approved vocabulary or curriculum boundary: synthetic owner-approved current-curriculum vocabulary.

Baseline item or observation chosen before coach use: synthetic baseline contains twelve aggregate attempts.

No-AI transfer or explanation check chosen before coach use: synthetic independent explanation check selected before coach use.

Ordinary non-AI fallback: ordinary teacher/tutor explanation and practice without the coach.

## Intervention identity

Tool/provider: synthetic rehearsal provider.

Model/version or dated product version: synthetic-model-v0.

Configuration or feature mode: teacher-facing move suggestions only.

Prompt-card SHA-256 at packet generation: `{prompt_hash}`

Owner confirms whether the prompt card changed after generation: unchanged in synthetic rehearsal.

Run date or dates: 2026-06-18 synthetic rehearsal.

Event chronology rule: synthetic rows use one ISO date in baseline <= coach-use <= transfer order; no real owner review or result evidence exists.

## Participation, access, and protected local review

Age-appropriate notice, assent/consent, or participation rule under local policy: synthetic rehearsal only; no learners participated.

How access, language support, accommodation, fallback, and opt-out will work without penalty: synthetic rehearsal assumes the ordinary fallback remains available.

Aggregate learner-voice prompt and categories: synthetic thresholded categories only; no free-text learner quotes.

Local small-cell/suppression threshold: synthetic minimum cell size of five.

Protected local subgroup/access review owner role and storage route: synthetic local access reviewer; no protected facts stored in the packet.

Expected teacher/tutor preparation, review, and correction time: synthetic aggregate minutes are recorded in `SESSION-LOG.csv`.

Stop triggers selected for this cycle: final-answer leakage; grade/record/discipline/risk/disability inference; unavailable human review; unacceptable burden; access/fallback failure; model/configuration drift; obvious transfer harm; participation rule not met.

Primary feasibility question: can the synthetic packet and readiness path execute while preserving the stated boundaries?

Public claim that remains prohibited: all learning, time-saving, safety, fairness, access, scale, and effectiveness claims.

Post-cycle local attestation route selected before the cycle: synthetic rehearsal route only; no human owner attestation, names, contact details, or protected facts enter this packet.

Method boundary: transfer and learner voice are descriptive rehearsal fields. This dry run cannot estimate efficacy or a causal learning effect.

Dry-run note: this file was seeded by `tools/seed_teacher_tutor_micro_pilot_dry_run.py` and must be replaced by a fresh packet for real local work.
"""
    reason = forbidden_reason([text])
    if reason:
        raise SystemExit(f'refuse to write dry-run owner plan with forbidden marker: {reason}')
    path.write_text(text, encoding='utf-8')


def write_session_log(path: Path, concept_code: str) -> None:
    rows = [
        {
            'date': '2026-06-18',
            'phase': 'D1-baseline',
            'concept_code': concept_code,
            'aggregate_attempt_count': '12',
            'aggregate_success_or_mastery_count': '5',
            'move_type_used': 'none',
            'owner_review_minutes': '10',
            'correction_minutes': '0',
            'fallback_or_optout_count': '0',
            'access_issue_count': '0',
            'answer_leakage_count': '0',
            'inappropriate_action_count': '0',
            'notes_without_identifiers': 'synthetic aggregate baseline rehearsal',
            'stop_continue_decision': 'continue',
        },
        {
            'date': '2026-06-18',
            'phase': 'D2-D3-coach-use',
            'concept_code': concept_code,
            'aggregate_attempt_count': '12',
            'aggregate_success_or_mastery_count': '7',
            'move_type_used': 'probing-question; misconception-check; smallest-useful-hint',
            'owner_review_minutes': '18',
            'correction_minutes': '4',
            'fallback_or_optout_count': '0',
            'access_issue_count': '0',
            'answer_leakage_count': '0',
            'inappropriate_action_count': '0',
            'notes_without_identifiers': 'synthetic aggregate coach-use rehearsal',
            'stop_continue_decision': 'continue',
        },
        {
            'date': '2026-06-18',
            'phase': 'D4-transfer',
            'concept_code': concept_code,
            'aggregate_attempt_count': '12',
            'aggregate_success_or_mastery_count': '7',
            'move_type_used': 'no-ai-transfer-check',
            'owner_review_minutes': '8',
            'correction_minutes': '0',
            'fallback_or_optout_count': '0',
            'access_issue_count': '0',
            'answer_leakage_count': '0',
            'inappropriate_action_count': '0',
            'notes_without_identifiers': 'synthetic aggregate transfer rehearsal',
            'stop_continue_decision': 'repeat-narrower',
        },
    ]
    with path.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=SESSION_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def write_final_readout(path: Path, owner_role: str, decision: str) -> None:
    rows = [
        {'row_id': '1', 'phase': 'D1-baseline', 'measure_family': 'learning_attempt_mastery', 'aggregate_value': '12 attempts; 5 success/mastery', 'method_note': 'synthetic aggregate baseline rehearsal', 'owner_role': owner_role, 'decision_effect': 'comparison only', 'do_not_import_note': 'synthetic dry run only'},
        {'row_id': '2', 'phase': 'D2-D3-coach-use', 'measure_family': 'learning_attempt_mastery', 'aggregate_value': '12 attempts; 7 success/mastery', 'method_note': 'synthetic aggregate coach-use rehearsal', 'owner_role': owner_role, 'decision_effect': 'comparison only', 'do_not_import_note': 'synthetic dry run only'},
        {'row_id': '3', 'phase': 'D4-transfer', 'measure_family': 'independent_transfer_or_explanation', 'aggregate_value': '12 attempts; 7 success/mastery', 'method_note': 'synthetic no-AI transfer rehearsal', 'owner_role': owner_role, 'decision_effect': 'requires real owner review before any claim', 'do_not_import_note': 'synthetic dry run only'},
        {'row_id': '4', 'phase': 'D2-D3-move-sample', 'measure_family': 'tutor_move_quality', 'aggregate_value': '3 move types reviewed; 0 final-answer leaks', 'method_note': 'synthetic reviewed move count', 'owner_role': owner_role, 'decision_effect': 'local rehearsal only', 'do_not_import_note': 'synthetic dry run only'},
        {'row_id': '5', 'phase': 'D0-D5-workload', 'measure_family': 'minutes_by_phase', 'aggregate_value': '10 baseline review; 18 coach review; 4 correction; 8 transfer review', 'method_note': 'synthetic workload accounting', 'owner_role': owner_role, 'decision_effect': 'workload not yet proved', 'do_not_import_note': 'synthetic dry run only'},
        {'row_id': '6', 'phase': 'D0-D5-access', 'measure_family': 'fallback_optout_access_issue_count', 'aggregate_value': '0 fallback/opt-out barriers; 0 access issues', 'method_note': 'synthetic access rehearsal', 'owner_role': owner_role, 'decision_effect': 'access not yet proved', 'do_not_import_note': 'synthetic dry run only'},
        {'row_id': '7', 'phase': 'D0-D5-safety', 'measure_family': 'answer_giving_or_inappropriate_action_count', 'aggregate_value': '0 answer leakage; 0 inappropriate actions', 'method_note': 'synthetic stop-trigger rehearsal', 'owner_role': owner_role, 'decision_effect': 'safety not yet proved', 'do_not_import_note': 'synthetic dry run only'},
        {'row_id': '8', 'phase': 'D5-decision', 'measure_family': 'continue_narrow_repeat_retire', 'aggregate_value': decision, 'method_note': 'synthetic owner-decision rehearsal', 'owner_role': owner_role, 'decision_effect': 'train packet path only', 'do_not_import_note': 'synthetic dry run only'},
    ]
    with path.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=FINAL_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def write_owner_decision(path: Path, *, concept_code: str, decision: str) -> None:
    text = f"""# Teacher/tutor move-coach feasibility decision memo

Packet state: `SYNTHETIC_DRY_RUN`
Evidence state: `NOT_EVIDENCE`
Evaluation class: `FEASIBILITY_AND_USABILITY_ONLY`
Concept code: `{concept_code}`

## Six owner questions

1. What changed in teacher/tutor moves, if anything? Synthetic rehearsal shows the packet can record aggregate move-type review.
2. Did independent no-AI transfer or explanation improve, stay flat, or worsen? Synthetic rehearsal is flat-to-better but proves nothing.
3. Did any access, language, accommodation, fallback, or opt-out route get worse? Synthetic rehearsal records zero access issues.
4. After counting review and correction time, was workload lower, flat, or higher? Synthetic rehearsal records review and correction minutes separately.
5. Did answer leakage, record/grade/risk/disability inference, or any other stop trigger occur? Synthetic rehearsal records zero stop triggers.
6. Which public claim remains prohibited? Learning, workload, access, safety, compliance, scale, and effectiveness claims remain prohibited.

## Decision

Choose exactly one: `retire`, `repeat-narrower`, `continue-bounded`, or `escalate-to-pilot-review`.

Decision: {decision}

Reason without identifiers: synthetic rehearsal demonstrates the packet and readiness scorer path only; a real owner must run a fresh local cycle before any review.

Tool/model/version confirmed stable for the recorded cycle: synthetic-model-v0 remained stable.

Protected local access/equity review decision: synthetic rehearsal only; no protected facts.

## Source-result hash-linked fresh-packet

Next packet concept or narrowing constraint without identifiers: synthetic narrower follow-through seed for rehearsal only.

One change required before any repeat or continue: synthetic fresh packet must use a locally selected narrower problem.

Fresh-packet rule acknowledged: synthetic rehearsal acknowledges any repeat or continue requires a fresh packet and cannot pool cycles as evidence.

Public claim ceiling: no learning, time-saving, safety, fairness, access, compliance, scale, or effectiveness claim may be made from this rehearsal.
"""
    reason = forbidden_reason([text])
    if reason:
        raise SystemExit(f'refuse to write dry-run owner decision with forbidden marker: {reason}')
    path.write_text(text, encoding='utf-8')


def main() -> None:
    args = parse_args()
    if args.operator_confirmation != CONFIRMATION:
        raise SystemExit(f'operator-confirmation must be exactly {CONFIRMATION!r}')
    packet_dir = Path(args.packet_dir)
    if not packet_dir.is_absolute():
        packet_dir = ROOT / packet_dir
    safe_packet_path(packet_dir)
    if not packet_dir.exists():
        raise SystemExit(f'packet directory missing: {rel(packet_dir)}')
    require_files(packet_dir)
    manifest = load_manifest(packet_dir)
    existing_run_guard(packet_dir, args.overwrite)
    concept_code = str(manifest.get('concept_code') or packet_dir.name)
    owner_role = str(manifest.get('owner_role') or 'classroom teacher or tutoring lead')
    backup_dir = backup_packet(packet_dir)

    write_owner_plan(packet_dir / 'OWNER-PLAN.md', manifest=manifest)
    write_session_log(packet_dir / 'SESSION-LOG.csv', concept_code)
    write_final_readout(packet_dir / 'FINAL-READOUT.csv', owner_role, args.decision)
    write_owner_decision(packet_dir / 'OWNER-DECISION-MEMO.md', concept_code=concept_code, decision=args.decision)

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    changed = ['OWNER-PLAN.md', 'SESSION-LOG.csv', 'FINAL-READOUT.csv', 'OWNER-DECISION-MEMO.md']
    trace = {
        'dry_run_state': DRY_RUN_STATE,
        'revision': RECEIPT.get('revision'),
        'packet_dir': rel(packet_dir),
        'generated_at': generated_at,
        'operator_confirmation': args.operator_confirmation,
        'source_packet_manifest_revision': manifest.get('revision'),
        'decision': args.decision,
        'changed_files': [{'path': rel(packet_dir / name), 'sha256': sha256(packet_dir / name)} for name in changed],
        'backup_dir': rel(backup_dir),
        'claim_boundary': 'Synthetic aggregate feasibility rehearsal only. It does not run a real cycle, estimate efficacy, accept evidence, prove learning/access/safety/fairness/workload/effectiveness, create custody, edit service records, authorize service use, support public claims, or close FT-0181.',
        'next_action': 'Delete this dry-run packet and generate a fresh packet before any real local teacher/tutor cycle.',
    }
    trace_path = packet_dir / 'DRY-RUN-TRACE.json'
    trace_path.write_text(json.dumps(trace, indent=2) + '\n', encoding='utf-8')
    if args.json:
        print(json.dumps(trace, indent=2))
    else:
        print(f'seed_teacher_tutor_micro_pilot_dry_run: wrote synthetic aggregate rehearsal in {rel(packet_dir)}')
        print('state: SYNTHETIC_AGGREGATE_DRY_RUN_NOT_EVIDENCE; use a fresh packet for real work')


if __name__ == '__main__':
    main()
