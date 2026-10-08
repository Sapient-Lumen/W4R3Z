#!/usr/bin/env python3
"""Prepare a scratch-only teacher/tutor micro-pilot work packet.

The packet is an execution aid for one bounded teacher/tutor move-coach cycle. It
creates fillable local files in scratch, but it does not run a pilot, accept
evidence, update a service record, or support public claims.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
REVISION = RECEIPT.get('revision', 'unknown')
DEFAULT_OUTPUT_ROOT = ROOT / 'scratch' / 'field-handoff' / REVISION / 'teacher-tutor-micro-pilot'
OWNER_PLAN_TEMPLATE = ROOT / 'templates' / 'teacher-tutor-micro-pilot-owner-plan.md'
SESSION_LOG_TEMPLATE = ROOT / 'templates' / 'teacher-tutor-micro-pilot-session-log.csv'
FINAL_READOUT_TEMPLATE = ROOT / 'templates' / 'teacher-tutor-augmentation-micro-pilot-template.csv'

SESSION_COLUMNS = [
    'date',
    'phase',
    'concept_code',
    'aggregate_attempt_count',
    'aggregate_success_or_mastery_count',
    'move_type_used',
    'owner_review_minutes',
    'correction_minutes',
    'fallback_or_optout_count',
    'access_issue_count',
    'answer_leakage_count',
    'inappropriate_action_count',
    'notes_without_identifiers',
    'stop_continue_decision',
]
FINAL_COLUMNS = [
    'row_id',
    'phase',
    'measure_family',
    'aggregate_value',
    'method_note',
    'owner_role',
    'decision_effect',
    'do_not_import_note',
]
FINAL_ROW_IDS = [str(i) for i in range(1, 9)]
SAFE_CONFIRMATION = 'prepared-not-run-scratch-only'
SOURCE_RESULT_CONFIRMATION = 'source-result-read-for-local-followthrough-not-evidence'
FOLLOWTHROUGH_SOURCE_STATE = 'FRESH_PACKET_SOURCE_RESULT_LINK_NOT_EVIDENCE'
ALLOWED_SOURCE_DECISIONS = {'repeat-narrower', 'continue-bounded'}
FORBIDDEN_TEXT_TERMS = [
    'student id',
    'learner id',
    'student name',
    'learner name',
    'full name',
    'email address',
    'ssn',
    'social security',
    'iep',
    '504 plan',
    'disability facts',
    'accommodation facts',
    'protected status',
    'gradebook row',
    'raw work',
    'screenshot',
    'recording',
    'chat transcript',
    'discipline record',
    'risk score',
    'api key',
    'credential',
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Prepare one scratch-only teacher/tutor micro-pilot work packet.')
    parser.add_argument('--concept-code', default='teacher-selected-concept', help='Lowercase safe slug for the locally selected concept/cycle.')
    parser.add_argument('--concept', default='one teacher/tutor-selected misconception or reasoning move tied to current curriculum')
    parser.add_argument('--setting', default='one class, section, tutoring room, or practice group selected by the owner')
    parser.add_argument('--owner-role', default='classroom teacher or tutoring lead')
    parser.add_argument('--date-range', default='owner-selected bounded window')
    parser.add_argument('--fallback', default='ordinary non-AI practice and teacher/tutor support without penalty')
    parser.add_argument('--transfer-check', default='one no-AI transfer or explanation check selected before coach use')
    parser.add_argument('--approved-vocabulary', default='owner-approved vocabulary and curriculum boundary')
    parser.add_argument('--concept-kit', default='generic', choices=['generic', 'equality-one-step'], help='Optional concrete measure-card kit to include in the scratch packet.')
    parser.add_argument('--output-root', default=str(DEFAULT_OUTPUT_ROOT), help='Scratch/external output root; package_release excludes scratch.')
    parser.add_argument('--source-result', default='', help='Optional MICRO-PILOT-RESULT.json from a prior local result when preparing a fresh follow-through packet.')
    parser.add_argument('--source-result-confirmation', default='', help=f'Required token when --source-result is used: {SOURCE_RESULT_CONFIRMATION}')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing concept packet directory.')
    parser.add_argument('--json', action='store_true', help='Print the manifest as JSON instead of a short note.')
    return parser.parse_args()


def slugify(value: str) -> str:
    slug = re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')
    slug = re.sub(r'-{2,}', '-', slug)
    return slug[:80] or 'teacher-selected-concept'


def forbidden_reason(values: Iterable[str]) -> str | None:
    joined = ' '.join(values).lower()
    if '@' in joined:
        return 'email-like address marker @'
    for term in FORBIDDEN_TEXT_TERMS:
        if term in joined:
            return term
    return None


def ensure_templates() -> None:
    for path in [OWNER_PLAN_TEMPLATE, SESSION_LOG_TEMPLATE, FINAL_READOUT_TEMPLATE]:
        if not path.exists():
            raise SystemExit(f'template missing: {path.relative_to(ROOT)}')
    owner_template = OWNER_PLAN_TEMPLATE.read_text(encoding='utf-8')
    for marker in ['Intervention identity', 'Participation, access, and protected local review', 'Method boundary:']:
        if marker not in owner_template:
            raise SystemExit(f'teacher/tutor owner-plan template missing required marker: {marker}')
    with SESSION_LOG_TEMPLATE.open(newline='', encoding='utf-8') as fh:
        reader = csv.reader(fh)
        header = next(reader, [])
    if header != SESSION_COLUMNS:
        raise SystemExit('teacher/tutor session log template columns changed; refuse packet prep')
    with FINAL_READOUT_TEMPLATE.open(newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    if reader.fieldnames != FINAL_COLUMNS:
        raise SystemExit('teacher/tutor final readout template columns changed; refuse packet prep')
    if [row.get('row_id') for row in rows] != FINAL_ROW_IDS:
        raise SystemExit('teacher/tutor final readout template row ids changed; refuse packet prep')


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


def load_followthrough_source(source_result_arg: str, confirmation: str) -> dict[str, object] | None:
    """Validate a prior local result receipt as a source for one fresh packet.

    The prior result may tell the operator *that* a new packet is allowed, but it
    must not be imported as evidence, pooled with the new cycle, or used to copy
    local seed text into the release archive. The fresh packet gets only a
    hash-linked source receipt and the human-supplied new concept/setting args.
    """
    if not source_result_arg:
        if confirmation:
            raise SystemExit('--source-result-confirmation is only valid with --source-result')
        return None
    if confirmation != SOURCE_RESULT_CONFIRMATION:
        raise SystemExit(f'--source-result-confirmation required when --source-result is used: {SOURCE_RESULT_CONFIRMATION}')
    source_path = Path(source_result_arg)
    if not source_path.is_absolute():
        source_path = ROOT / source_path
    source_resolved = source_path.resolve()
    try:
        source_resolved.relative_to(ROOT.resolve())
    except ValueError:
        pass
    else:
        try:
            source_resolved.relative_to((ROOT / 'scratch').resolve())
        except ValueError as exc:
            raise SystemExit('source result must be under scratch/ or outside the repository; refuse release-path source result') from exc
    if not source_path.exists():
        raise SystemExit(f'source result missing: {rel(source_path)}')
    try:
        data = json.loads(source_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise SystemExit(f'source result is not valid JSON: {rel(source_path)}: {exc}') from exc
    errors: list[str] = []
    if data.get('result_state') != 'LOCAL_MICRO_PILOT_RESULT_RECORDED_NOT_EVIDENCE':
        errors.append('source result_state is not LOCAL_MICRO_PILOT_RESULT_RECORDED_NOT_EVIDENCE')
    decision = str(data.get('decision') or '')
    if decision not in ALLOWED_SOURCE_DECISIONS:
        errors.append(f'source decision must be repeat-narrower or continue-bounded, not {decision!r}')
    for field, expected in [
        ('evidence_effect', 'not_evidence'),
        ('custody_effect', 'none'),
        ('service_authority_effect', 'none'),
        ('public_claim_effect', 'none'),
    ]:
        if data.get(field) != expected:
            errors.append(f'source {field} must be {expected!r}')
    followthrough = data.get('decision_followthrough') if isinstance(data.get('decision_followthrough'), dict) else {}
    if followthrough.get('fresh_packet_required') is not True:
        errors.append('source decision_followthrough must require a fresh packet')
    if followthrough.get('evidence_escalation_allowed') is not False:
        errors.append('source decision_followthrough must not allow evidence escalation')
    preflight = data.get('fresh_packet_preflight') if isinstance(data.get('fresh_packet_preflight'), dict) else {}
    if preflight.get('required_for_non_retire') is not True:
        errors.append('source fresh_packet_preflight must be required for non-retire')
    if preflight.get('receipt_copies_seed_text') is not False:
        errors.append('source fresh_packet_preflight must confirm seed text was not copied')
    spec = data.get('decision_followthrough_spec') if isinstance(data.get('decision_followthrough_spec'), dict) else {}
    if spec.get('status') != 'recorded':
        errors.append('source decision_followthrough_spec must be recorded')
    if spec.get('values_copied_to_scorecard') is not False:
        errors.append('source decision_followthrough_spec must confirm values were not copied')
    if errors:
        raise SystemExit('source result cannot seed a fresh packet:\n- ' + '\n- '.join(errors))
    return {
        'source_state': FOLLOWTHROUGH_SOURCE_STATE,
        'source_result_path': rel(source_path),
        'source_result_sha256': sha256(source_path),
        'source_result_revision': data.get('revision'),
        'source_result_date': data.get('record_date'),
        'source_owner_review_date': data.get('owner_review_date'),
        'source_packet_dir': data.get('packet_dir'),
        'source_decision': decision,
        'source_decision_class': followthrough.get('decision_class'),
        'fresh_packet_required': True,
        'source_values_copied': False,
        'source_reuse_rule': 'prior result is local learning context only; do not pool, average, import, publish, update service authority, or claim trend/effect from this follow-through packet',
        'claim_boundary': 'This source link authorizes only one fresh local feasibility packet from human-supplied new arguments. It is not evidence, custody, service authority, public-claim support, or FT-0181 closure material.',
    }


def write_followthrough_source(path_json: Path, path_md: Path, source: dict[str, object]) -> None:
    path_json.write_text(json.dumps(source, indent=2) + '\n', encoding='utf-8')
    lines = [
        '# Fresh-packet follow-through source link',
        '',
        f"State: `{source['source_state']}`",
        f"Source decision: `{source['source_decision']}`",
        f"Source result SHA-256: `{source['source_result_sha256']}`",
        '',
        'This file intentionally records a hash-linked source result and decision class only. It does not copy the owner\'s local follow-through seed text, learner counts, protected facts, raw work, owner contact details, or previous local observations into the fresh packet.',
        '',
        '## Boundary',
        '',
        str(source['claim_boundary']),
        '',
    ]
    path_md.write_text('\n'.join(lines), encoding='utf-8')


def source_result_note(source: dict[str, object] | None) -> str:
    if not source:
        return 'not applicable — first local cycle or discovery-start packet'
    return (
        f"fresh follow-through from hash-linked local result `{source['source_result_sha256']}` "
        f"with decision `{source['source_decision']}`; source result is not evidence and cannot be pooled or copied"
    )


def write_owner_plan(path: Path, *, concept: str, setting: str, owner_role: str, date_range: str, fallback: str, transfer_check: str, approved_vocabulary: str, prompt_sha256: str, source_result_note: str) -> None:
    text = f"""# Teacher/tutor move-coach feasibility owner plan

Packet state: `PREPARED_NOT_RUN`
Evidence state: `NOT_EVIDENCE`
Evaluation class: `FEASIBILITY_AND_USABILITY_ONLY`
Revision: `{REVISION}`

Owner role: {owner_role}

Local instructional problem and why it matters now: owner fills locally from an observed need.

Concept selected by the local owner: {concept}

Setting and bounded window: {setting}; {date_range}

Fresh-packet follow-through source: {source_result_note}

Learner group description without identifiers: owner fills locally without names, ids, protected facts, or small cells.

Approved vocabulary or curriculum boundary: {approved_vocabulary}

Baseline item or observation chosen before coach use: owner fills locally.

No-AI transfer or explanation check chosen before coach use: {transfer_check}

Ordinary non-AI fallback: {fallback}

## Intervention identity

Tool/provider: owner fills locally.

Model/version or dated product version: owner fills locally.

Configuration or feature mode: owner fills locally.

Prompt-card SHA-256 at packet generation: `{prompt_sha256}`

Owner confirms whether the prompt card changed after generation: owner fills locally with `unchanged`; regenerate the packet if the prompt card changed.

Run date or dates: owner fills locally.

Event chronology rule: baseline date must be on/before coach-use date, coach-use date must be on/before transfer date, owner review must be on/after the latest `SESSION-LOG.csv` date, and result receipt date must be on/after owner review.

## Participation, access, and protected local review

Age-appropriate notice, assent/consent, or participation rule under local policy: owner fills locally.

How access, language support, accommodation, fallback, and opt-out will work without penalty: owner fills locally.

Aggregate learner-voice prompt and categories: owner fills locally using no free-text learner quotes; suggested categories are helped me think, neutral, confused me, or preferred the non-AI route.

Local small-cell/suppression threshold: owner fills locally as an integer release/suppression floor of at least 3; exact counts below this threshold stay local and must be masked in any result receipt.

Protected local subgroup/access review owner role and storage route: owner fills locally; keep any protected disaggregation outside this packet and release archive.

Expected teacher/tutor preparation, review, and correction time: owner estimates before the cycle and records actual aggregate minutes in `SESSION-LOG.csv`.

Stop triggers selected for this cycle: final-answer leakage; grade/record/discipline/risk/disability inference; owner cannot review before use; workload worse than the ordinary route; access/fallback failure; model/configuration drift; obvious transfer harm; participation rule not met.

Primary feasibility question: can the owner use the packet, find at least one move instructionally useful, maintain acceptable burden, preserve fallback and human review, and avoid an obvious stop trigger?

Public claim that remains prohibited: any claim that the coach improves learning, saves time, is safe or fair at scale, or is ready for student-facing use.

Post-cycle local attestation route selected before the cycle: owner fills locally with a route title only; no signature, contact details, names, or protected facts enter this packet.

Method boundary: transfer and learner voice are descriptive signals for stop/redesign decisions. This bounded cycle cannot estimate efficacy or a causal learning effect.
"""
    path.write_text(text, encoding='utf-8')



def write_discovery_ask(path: Path, *, concept: str, setting: str, owner_role: str, transfer_check: str) -> None:
    text = f"""# Teacher/tutor discovery first-contact card

Packet state: `PREPARED_NOT_RUN`
Evidence state: `NOT_EVIDENCE`
Evaluation class: `FEASIBILITY_AND_USABILITY_ONLY`
Revision: `{REVISION}`

Use this one-page card before filling the packet. Its job is to secure one real educator
conversation and a locally chosen problem, not to explain the whole cube.

## Fifteen-minute ask

Ask a {owner_role} for one bounded conversation about whether a teacher/tutor move-coach could help
with one current instructional friction point. Do not ask for learner names, raw work, grades,
protected facts, screenshots, transcripts, or roster exports.

Suggested opener:

```text
Could we spend 15 minutes choosing one current concept or misconception where a teacher/tutor would
like better next-move suggestions after a learner attempt? The first step is only local feasibility:
we would define the problem, fallback, participation rule, tool/version, and stop triggers before any
learner-facing use. We will not claim learning impact from this.
```

## Questions that must be answered before readiness can pass

1. What local instructional problem matters now, and what concept should the owner select?
2. What baseline item and no-AI transfer/explanation check will be chosen before coach use?
3. Is the proposed setting acceptable under local participation, notice, and access rules?
4. What ordinary non-AI fallback or opt-out path exists without penalty?
5. What tool/provider, model/version, configuration, and run date would be used?
6. What date order will the owner use for baseline, coach-use, transfer, owner review, and result recording?
7. What numeric local small-cell threshold (at least 3) and protected access/equity review route apply?
8. What would make the owner stop immediately: answer leakage, access failure, excess burden,
   model drift, prompt/run-sheet drift, participation failure, or apparent transfer harm?

## Minimum outcome

After the conversation, choose exactly one local next step:

- `no-route-now`: do not continue; record nothing as evidence.
- `complete-owner-plan`: fill `OWNER-PLAN.md` locally and rerun readiness.
- `choose-different-concept`: regenerate the packet for the locally selected concept.

Current placeholder concept: {concept}
Current placeholder setting: {setting}
Current placeholder transfer check: {transfer_check}

## Boundary

This card is a human-discovery aid only. It does not contact anyone, authorize learner-facing use,
collect evidence, import data, support public claims, or close `FT-0181`.
"""
    path.write_text(text, encoding='utf-8')

def write_session_log(path: Path, concept_code: str) -> None:
    with path.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=SESSION_COLUMNS)
        writer.writeheader()
        writer.writerow({
            'phase': 'D1-baseline',
            'concept_code': concept_code,
            'notes_without_identifiers': 'aggregate only; no names/raw work/protected facts/small cells',
            'stop_continue_decision': 'not-started',
        })


def write_final_readout(path: Path, owner_role: str) -> None:
    with FINAL_READOUT_TEMPLATE.open(newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    for row in rows:
        row['owner_role'] = owner_role
    with path.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=FINAL_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def write_coach_prompt(path: Path, *, concept: str, transfer_check: str, approved_vocabulary: str) -> None:
    text = f"""# Teacher/tutor move coach prompt card

Use only after a learner attempt has happened and the human owner has written a de-identified summary.
Do not paste learner names, raw work, protected facts, screenshots, recordings, gradebook rows, or small cells.

```text
Given this concept: {concept}
Approved vocabulary/curriculum boundary: {approved_vocabulary}
No-AI proof item kept separate: {transfer_check}
De-identified learner attempted-step summary: [human writes a brief aggregate/de-identified summary]

Suggest three next instructional moves for the human teacher/tutor to review:
1. one probing question;
2. one misconception check;
3. one smallest-useful hint.

Do not give the final answer, write a grade, classify ability/motivation/risk/disability,
write a learner-facing message without teacher review, or create a record.
```

Human owner rule: choose, edit, or reject every move before any learner-facing use.
"""
    path.write_text(text, encoding='utf-8')


def write_measure_card(path: Path, *, concept_code: str, concept: str, concept_kit: str, transfer_check: str, approved_vocabulary: str) -> None:
    if concept_kit == 'equality-one-step':
        text = f"""# Optional equality one-step feasibility measure card

Packet state: `PREPARED_NOT_RUN`
Evidence state: `NOT_EVIDENCE`
Evaluation class: `FEASIBILITY_AND_USABILITY_ONLY`
Concept code: `{concept_code}`

This is an optional worked kit, not the project default and not evidence that equality is the local
priority. Use it only when the local owner chooses this construct: {concept}.

## Construct

Learners preserve equality while solving one-step equations and explain why the same inverse
operation applies to both sides. Approved vocabulary boundary: {approved_vocabulary}

## Baseline before coach use

Use two or three locally selected curriculum-matched items without the coach. Keep raw work local.
Capture only aggregate attempt/success counts and owner minutes above the local privacy threshold; exact counts/rates below the threshold must be masked in any result receipt.

## Coach-use session

After a learner attempt, the human owner may request exactly three reviewable moves: one probing
question, one misconception check, and one smallest-useful hint. The human edits or rejects each move
before learner-facing use.

## Descriptive no-AI transfer check

Keep the proof item separate from coach use: {transfer_check}

The transfer count is descriptive. It can trigger stopping or redesign but cannot estimate efficacy,
a causal effect, or general learning improvement.

## Data and equity boundary

Record only aggregate counts/minutes above local thresholds and mask exact counts/rates below threshold in any result receipt. Keep names, raw work, screenshots,
individual scores, transcripts, protected facts, and protected subgroup disaggregation outside the
packet. A named local role must review any subgroup/access concern through a protected local route.

## Feasibility decision

Consider at most another bounded cycle only when the owner can use the packet, at least one move is
instructionally useful, human review and fallback work, burden is acceptable, no stop trigger occurs,
and transfer is not obviously worse. Otherwise retire or redesign. No effectiveness claim follows.
"""
    else:
        text = f"""# Teacher/tutor move-coach feasibility measure card

Packet state: `PREPARED_NOT_RUN`
Evidence state: `NOT_EVIDENCE`
Evaluation class: `FEASIBILITY_AND_USABILITY_ONLY`
Concept code: `{concept_code}`

Concept selected by the local owner: {concept}

Approved vocabulary boundary: {approved_vocabulary}

## Before coach use

The owner documents the observed instructional problem, writes one local baseline item, chooses the
no-AI transfer check, identifies the tool/model/version and prompt-card hash, settles participation
and privacy rules, and confirms the ordinary non-AI fallback.

## During coach use

After a learner attempt, ask only for a probing question, misconception check, and smallest-useful
hint. The human owner reviews, edits, or rejects every move.

## Descriptive transfer check

No-AI transfer or explanation check: {transfer_check}

Transfer is a descriptive stop/redesign signal, not an effect estimate.

## Data, participation, and equity boundary

Capture aggregate counts/minutes and predefined aggregate learner-voice categories only; mask exact counts/rates below the local threshold in any result receipt. No names,
raw work, screenshots, gradebook rows, protected facts, small cells, free-text learner quotes, or
transcripts enter the packet. Keep protected local disaggregation with the named local reviewer.

## Feasibility decision

Consider another bounded cycle only if the owner can use the packet, at least one move is useful,
review and fallback work, burden is acceptable, no stop trigger occurs, and transfer is not obviously
worse. No learning, effectiveness, safety-at-scale, fairness-at-scale, or time-saving claim follows.
"""
    path.write_text(text, encoding='utf-8')


def write_cycle_run_sheet(path: Path, *, concept_code: str, concept: str, transfer_check: str) -> None:
    text = f"""# One-cycle local run sheet

Packet state: `PREPARED_NOT_RUN`
Evidence state: `NOT_EVIDENCE`
Evaluation class: `FEASIBILITY_AND_USABILITY_ONLY`
Concept code: `{concept_code}`

Use this sheet only after `READINESS-SCORECARD.json` reports
`READY_FOR_LOCAL_CYCLE_NOT_EVIDENCE`. It converts a completed discovery/owner plan into one
bounded local feasibility cycle. It is not a permission slip for deployment, evidence import, or
public claims.

## Entry confirmation

Before the cycle starts, the local owner confirms each item using local records only:

1. The instructional problem is current and locally selected: {concept}
2. The baseline item and no-AI transfer/explanation check were selected before coach use.
3. The tool/provider, model/version, configuration, run date, prompt-card hash, coach prompt, checklist, measure card, and run sheet are fixed from packet generation.
4. The owner will date `SESSION-LOG.csv` rows in actual event order: baseline <= coach-use <= transfer.
5. Participation, notice/consent/assent, fallback, opt-out, access, and accommodation handling are acceptable locally.
6. The numeric small-cell threshold is at least 3, the protected local access/equity review route is set, and the run-definition hash check remains stable.
7. The post-cycle attestation route is set without putting a signature, name, email, or contact route in this packet.

## Run exactly one local cycle

1. Collect the local baseline or observation without the coach. Keep raw work outside this packet.
2. After a learner attempt, let the teacher/tutor ask `COACH-PROMPT.md` for three reviewable moves only.
3. The human owner edits, rejects, or uses the moves; no unreviewed learner-facing output is allowed.
4. Use the separate no-AI transfer/explanation check: {transfer_check}
5. Record only aggregate counts and minutes in `SESSION-LOG.csv` and `FINAL-READOUT.csv`; session dates must be ISO `YYYY-MM-DD` and ordered baseline <= coach-use <= transfer. Any result receipt must mask exact counts/rates below the configured local threshold.

## Stop immediately

Stop, do not record a result receipt, and redesign or retire if there is final-answer leakage,
participation failure, access/fallback failure, owner-review failure, model/configuration or prompt/run-sheet drift,
unacceptable burden, grade/record/discipline/risk/disability inference, raw/protected material in
the packet, a small-cell problem, or obvious transfer harm.

## Exit

After the one cycle, fill the owner decision memo, including the source-result hash-linked fresh-packet for any non-retire decision, then rerun readiness. If session rows are partially filled, misdated, or the follow-through seed is missing, repair them locally before owner review. If the status becomes
`READY_FOR_LOCAL_OWNER_REVIEW_NOT_EVIDENCE`, stop for local owner review. After result recording,
follow the owner decision as a bounded local action only: `retire` stops, `repeat-narrower` and
`continue-bounded` require a fresh packet and cannot pool cycles as evidence, and
`escalate-to-pilot-review` requires a separate future gate. Do not import, publish, update service
authority, generalize to other groups, or claim learning/workload/access/safety/fairness benefit from
this cycle.
"""
    path.write_text(text, encoding='utf-8')

def write_owner_decision_memo(path: Path, *, concept_code: str) -> None:
    text = f"""# Teacher/tutor move-coach feasibility decision memo

Packet state: `PREPARED_NOT_RUN`
Evidence state: `NOT_EVIDENCE`
Evaluation class: `FEASIBILITY_AND_USABILITY_ONLY`
Concept code: `{concept_code}`

Fill after the local cycle. Keep names, raw work, protected facts, screenshots, transcripts, small
cells, gradebook rows, free-text learner quotes, and owner contact details out of this memo.

## Owner questions

1. What local instructional problem was tested, and was it still the right problem?
2. Which generated move, if any, was instructionally useful after human editing?
3. Did independent no-AI transfer or explanation appear better, flat, worse, or uninterpretable?
4. What were the aggregate learner-voice category counts, above the local threshold?
5. Did access, language support, accommodation, fallback, or opt-out become harder?
6. After preparation, review, correction, and escalation time, was burden acceptable?
7. Did the tool/model/version/configuration or prompt card change during the cycle?
8. Did answer leakage, record/grade/discipline/risk/disability inference, participation failure, or any other stop trigger occur?
9. Did the protected local reviewer identify a subgroup/access concern that requires stop or redesign? Record only the decision, not protected facts.
10. Which public claim remains prohibited?

## Decision

Choose exactly one: `retire`, `repeat-narrower`, `continue-bounded`, or `escalate-to-pilot-review`.

Decision meanings:

- `retire`: stop this local line; do not repeat without new discovery.
- `repeat-narrower`: generate a fresh narrower packet; do not append a second cycle to this packet.
- `continue-bounded`: allow at most one fresh bounded local cycle after a new owner-plan refresh; do not pool cycles or infer trend/effect.
- `escalate-to-pilot-review`: stop the local micro-cycle lane and require a separate future pilot-review gate; this packet/result is not accepted evidence.

Decision: 

Reason without identifiers: 

## Source-result hash-linked fresh-packet

Fill this before local owner review so a non-retire decision cannot become a vague repeat loop. Keep it de-identified and high-level; do not copy counts, learner text, protected facts, or owner contact details here. For `retire`, write `not applicable — retire` on each line.

Next packet concept or narrowing constraint without identifiers: 

One change required before any repeat or continue: 

Fresh-packet rule acknowledged: 

Tool/model/version confirmed stable for the recorded cycle: owner fills locally.

Protected local access/equity review decision: owner fills locally with no protected facts.

Public claim ceiling: this feasibility cycle supports no causal learning, time-saving, safety,
fairness, access, compliance, scale, or effectiveness claim. A later efficacy question requires a
separate pre-specified design and accepted evidence route.
"""
    path.write_text(text, encoding='utf-8')

def write_run_checklist(path: Path, *, concept_code: str) -> None:
    text = f"""# Teacher/tutor move-coach feasibility checklist

Packet state: `PREPARED_NOT_RUN`
Evidence state: `NOT_EVIDENCE`
Evaluation class: `FEASIBILITY_AND_USABILITY_ONLY`
Concept code: `{concept_code}`

## Before any learner-facing use

1. Owner completes every discovery field in `OWNER-PLAN.md` from a real local need.
2. Owner selects the concept, baseline, and no-AI transfer/explanation check before coach use.
3. Owner records tool/provider, model/version, configuration, run date, and prompt-card hash, leaves generated run-definition files unchanged, and plans dated baseline/coach-use/transfer rows in event order.
4. Owner confirms age-appropriate participation rules, ordinary non-AI fallback, and no-penalty opt-out.
5. Owner defines a numeric local small-cell threshold of at least 3 and the protected local subgroup/access review role.
6. Owner defines aggregate learner-voice categories without free-text quotes.
7. Owner confirms no names, raw work, protected facts, screenshots, recordings, gradebook rows, transcripts, or small cells will enter this packet.

## During the cycle

1. Use `COACH-PROMPT.md` only for teacher/tutor-facing move suggestions after a learner attempt.
2. Human reviews, edits, or rejects every move before use.
3. Record only permitted aggregate counts/minutes in `SESSION-LOG.csv`; mask result-receipt counts/rates below the local threshold and keep learner voice as thresholded category counts in the memo or protected local system.
4. Stop for answer leakage, record/grade/discipline/risk/disability inference, access or participation failure, unacceptable burden, model/configuration or prompt/run-sheet drift, or obvious transfer harm.

## After the cycle

1. Fill the eight aggregate rows in `FINAL-READOUT.csv` as descriptive feasibility observations, using suppression language instead of exact small-cell values where required.
2. Complete `OWNER-DECISION-MEMO.md` and choose retire, repeat narrower, continue bounded, or escalate to formal pilot review.
3. Confirm `SESSION-LOG.csv` dates are ISO `YYYY-MM-DD` and ordered baseline <= coach-use <= transfer before owner review.
4. Run `make micro-pilot-readiness PACKET={rel(path.parent)} WRITE=1`.
5. Before owner review, fill the source-result hash-linked fresh-packet in `OWNER-DECISION-MEMO.md`; non-retire decisions need a de-identified next-packet constraint and one required change, or readiness remains repair-needed.
6. After result recording, apply the decision boundary: retire stops; repeat/continue require a fresh packet and cannot become cumulative evidence; escalation requires a separate future accepted route.
7. Do not edit a service record, upgrade a public claim, infer efficacy, or import evidence without a separate accepted route.
7. Keep this packet in scratch/external storage unless a future explicit route accepts a minimized owner-attested readout.
"""
    path.write_text(text, encoding='utf-8')

def main() -> None:
    args = parse_args()
    reason = forbidden_reason([
        args.concept_code,
        args.concept,
        args.setting,
        args.owner_role,
        args.date_range,
        args.fallback,
        args.transfer_check,
        args.approved_vocabulary,
        args.concept_kit,
    ])
    if reason:
        raise SystemExit(f'refuse micro-pilot packet args containing raw/protected/identifying material: {reason}')
    ensure_templates()
    source_result = load_followthrough_source(args.source_result, args.source_result_confirmation)
    concept_code = slugify(args.concept_code)
    output_root = Path(args.output_root)
    if not output_root.is_absolute():
        output_root = ROOT / output_root
    output_dir = output_root / concept_code
    try:
        output_dir.resolve().relative_to(ROOT.resolve() / 'scratch')
    except ValueError:
        # External paths are allowed, but repository non-scratch paths are not.
        try:
            output_dir.resolve().relative_to(ROOT.resolve())
        except ValueError:
            pass
        else:
            raise SystemExit('output must be under scratch/ or outside the repository; refuse release-path packet')
    if output_dir.exists():
        if not args.overwrite:
            raise SystemExit(f'output exists; pass --overwrite to replace: {rel(output_dir)}')
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    files = {
        'discovery_ask': output_dir / 'DISCOVERY-FIRST-CONTACT.md',
        'owner_plan': output_dir / 'OWNER-PLAN.md',
        'session_log': output_dir / 'SESSION-LOG.csv',
        'final_readout': output_dir / 'FINAL-READOUT.csv',
        'coach_prompt': output_dir / 'COACH-PROMPT.md',
        'run_checklist': output_dir / 'RUN-CHECKLIST.md',
        'measure_card': output_dir / 'MEASURE-CARD.md',
        'owner_decision_memo': output_dir / 'OWNER-DECISION-MEMO.md',
        'cycle_run_sheet': output_dir / 'CYCLE-RUN-SHEET.md',
    }
    if source_result:
        files['followthrough_source_result_json'] = output_dir / 'FOLLOWTHROUGH-SOURCE-RESULT.json'
        files['followthrough_source_result_md'] = output_dir / 'FOLLOWTHROUGH-SOURCE-RESULT.md'
        write_followthrough_source(files['followthrough_source_result_json'], files['followthrough_source_result_md'], source_result)
    write_discovery_ask(files['discovery_ask'], concept=args.concept, setting=args.setting, owner_role=args.owner_role, transfer_check=args.transfer_check)
    write_coach_prompt(files['coach_prompt'], concept=args.concept, transfer_check=args.transfer_check, approved_vocabulary=args.approved_vocabulary)
    write_owner_plan(
        files['owner_plan'],
        concept=args.concept,
        setting=args.setting,
        owner_role=args.owner_role,
        date_range=args.date_range,
        fallback=args.fallback,
        transfer_check=args.transfer_check,
        approved_vocabulary=args.approved_vocabulary,
        prompt_sha256=sha256(files['coach_prompt']),
        source_result_note=source_result_note(source_result),
    )
    write_session_log(files['session_log'], concept_code)
    write_final_readout(files['final_readout'], args.owner_role)
    write_run_checklist(files['run_checklist'], concept_code=concept_code)
    write_measure_card(files['measure_card'], concept_code=concept_code, concept=args.concept, concept_kit=args.concept_kit, transfer_check=args.transfer_check, approved_vocabulary=args.approved_vocabulary)
    write_owner_decision_memo(files['owner_decision_memo'], concept_code=concept_code)
    write_cycle_run_sheet(files['cycle_run_sheet'], concept_code=concept_code, concept=args.concept, transfer_check=args.transfer_check)

    manifest_path = output_dir / 'PACK-MANIFEST.json'
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    manifest = {
        'packet_id': f'TT-MICRO-PILOT-{concept_code.upper()}',
        'revision': REVISION,
        'packet_state': 'PREPARED_NOT_RUN',
        'evidence_state': 'NOT_EVIDENCE',
        'operator_confirmation': SAFE_CONFIRMATION,
        'concept_code': concept_code,
        'owner_role': args.owner_role,
        'date_range': args.date_range,
        'concept_kit': args.concept_kit,
        'evaluation_class': 'FEASIBILITY_AND_USABILITY_ONLY',
        'concept_selection_rule': 'local_owner_required',
        'micro_cycle_claim_class': 'descriptive_feasibility_not_efficacy',
        'fresh_packet_source_state': source_result.get('source_state') if source_result else 'NO_PRIOR_RESULT_SOURCE',
        'source_result_link': source_result or None,
        'source_result_copy_rule': 'source result hash/decision may be linked, but local seed text and prior local observations are not copied; new packet args must be supplied by the human owner',
        'result_receipt_suppression_rule': 'mask exact counts and rates below the numeric local threshold; floor must be at least 3',
        'default_concept_is_local_placeholder': args.concept_kit == 'generic',
        'output_dir': rel(output_dir),
        'generated_at': generated_at,
        'files': [
            {'role': role, 'path': rel(path), 'sha256': sha256(path)}
            for role, path in files.items()
        ],
        'conversion_sheet': rel(files['cycle_run_sheet']),
        'claim_boundary': 'This packet prepares a feasibility/usability cycle only. It does not run a cycle, accept evidence, estimate efficacy, prove learning/access/safety/fairness/workload/effectiveness, authorize service use, upgrade public claims, create custody, or close FT-0181; use score_teacher_tutor_micro_pilot_readiness.py only for scratch-local readiness feedback, mask small cells in any local result receipt, require a de-identified follow-through seed before non-retire owner decisions, require any repeat/continue packet to be hash-linked to a prior non-evidence result through --source-result, and treat retire/repeat/continue/escalate decisions as bounded local next-step guidance rather than evidence.',
    }
    manifest['manifest_note'] = 'The manifest does not include a self-hash; file hashes cover the generated work packet files only.'
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')

    if args.json:
        print(json.dumps(manifest, indent=2))
    else:
        print(f'prepare_teacher_tutor_micro_pilot_pack: wrote {rel(output_dir)}')
        print('state: PREPARED_NOT_RUN; not evidence; keep raw/protected/identifying material out')


if __name__ == '__main__':
    main()
