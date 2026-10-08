#!/usr/bin/env python3
"""Decide the next scratch-local teacher/tutor micro-pilot action.

This is an operator router, not evidence intake. It reads the generated packet
and readiness scorer, then writes a compact next-action brief in scratch so the
operator does not have to inspect every packet file or reopen governance tails.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from score_teacher_tutor_micro_pilot_readiness import DEFAULT_PACKET, ENTRY_READY_STATUS, OWNER_REVIEW_READY_STATUS, ROOT, score, safe_packet_path, write_markdown as write_score_markdown

RECEIPT = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
ROUTER_STATE = 'LOCAL_MICRO_PILOT_NEXT_ACTION_NOT_EVIDENCE'

DEFAULT_CONCEPT_COMMAND = (
    'make micro-pilot-pack '
    'CONCEPT_CODE=teacher-selected-concept '
    'CONCEPT="one teacher/tutor-selected misconception or reasoning move tied to current curriculum" '
    'SETTING="one teacher-owned practice group selected locally" '
    'DATE_RANGE="owner-selected bounded window" '
    'TRANSFER_CHECK="one no-AI transfer or explanation check selected before coach use" '
    'CONCEPT_KIT=generic '
    'OVERWRITE=1'
)

SOURCE_RESULT_CONFIRMATION = 'source-result-read-for-local-followthrough-not-evidence'


def fresh_packet_from_decision_command(result_path: Path) -> str:
    return (
        'make micro-pilot-followthrough-pack '
        f'SOURCE_RESULT="{rel(result_path)}" '
        f'CONFIRM={SOURCE_RESULT_CONFIRMATION} '
        'CONCEPT_CODE=<owner-selected-safe-slug> '
        'CONCEPT="<de-identified next concept or narrowing constraint from local OWNER-DECISION-MEMO.md>" '
        'SETTING="<fresh bounded setting/window from local owner discovery>" '
        'DATE_RANGE="<fresh bounded window>" '
        'TRANSFER_CHECK="<new no-AI transfer or explanation check selected before coach use>" '
        'CONCEPT_KIT=generic '
        'OVERWRITE=1'
    )


DECISION_FOLLOWTHROUGH = {
    'retire': {
        'decision_class': 'stop_without_repeat',
        'operator_action': 'Result decision is retire: stop this local line. Do not repeat, widen, import, publish, update service authority, or close FT-0181 from this receipt.',
        'fresh_packet_allowed': False,
        'command_templates': [],
    },
    'repeat-narrower': {
        'decision_class': 'fresh_narrower_packet_only',
        'operator_action': 'Result decision is repeat-narrower: only a source-linked fresh narrower owner-selected packet may follow. Do not append another cycle to the existing packet or treat repeated local cycles as evidence.',
        'fresh_packet_allowed': True,
        'command_templates': ['fresh_micro_pilot_pack'],
    },
    'continue-bounded': {
        'decision_class': 'one_fresh_bounded_cycle_only',
        'operator_action': 'Result decision is continue-bounded: at most one source-linked fresh bounded local cycle may follow after a new packet and owner-plan refresh. Do not pool cycles or infer trend/effect.',
        'fresh_packet_allowed': True,
        'command_templates': ['fresh_micro_pilot_pack'],
    },
    'escalate-to-pilot-review': {
        'decision_class': 'separate_future_gate_required',
        'operator_action': 'Result decision is escalate-to-pilot-review: stop the local micro-cycle lane. Escalation requires a separate future pilot-review route with pre-specified design, privacy/access review, and accepted custody; this router emits no evidence-import command.',
        'fresh_packet_allowed': False,
        'command_templates': [],
    },
}



def readiness_command(packet_dir: Path) -> str:
    return f'make micro-pilot-readiness PACKET={rel(packet_dir)} WRITE=1'


def dry_run_command(packet_dir: Path) -> str:
    return (
        'make micro-pilot-dry-run '
        f'PACKET={rel(packet_dir)} '
        'CONFIRM=synthetic-aggregate-dry-run-not-evidence '
        'DECISION=repeat-narrower '
        'OVERWRITE=1'
    )


def regenerate_command(packet_dir: Path) -> str:
    rel_path = rel(packet_dir)
    if rel_path.startswith('scratch/field-handoff/'):
        return 'make field-handoff-bundle OVERWRITE=1'
    return DEFAULT_CONCEPT_COMMAND

def owner_review_command(packet_dir: Path, decision: str | None) -> str:
    safe_decision = decision if decision in {'retire', 'repeat-narrower', 'continue-bounded', 'escalate-to-pilot-review'} else '<retire|repeat-narrower|continue-bounded|escalate-to-pilot-review>'
    return (
        'make micro-pilot-owner-review '
        f'PACKET={rel(packet_dir)} '
        'REVIEW_DATE=YYYY-MM-DD '
        'OWNER_ROLE="local teacher/tutor owner role only" '
        f'DECISION={safe_decision} '
        'CONFIRM=human-reviewed-local-micro-pilot-aggregate '
        'OVERWRITE=1'
    )


def result_command(packet_dir: Path) -> str:
    return (
        'make micro-pilot-result '
        f'PACKET={rel(packet_dir)} '
        f'OWNER_REVIEW={rel(packet_dir / "OWNER-REVIEW-STOP.json")} '
        'RECORD_DATE=YYYY-MM-DD '
        'OPERATOR_ROLE="local pilot operator role only" '
        'CONFIRM=human-recorded-local-micro-pilot-aggregate-result '
        'OVERWRITE=1'
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Decide the next scratch-local teacher/tutor micro-pilot action.')
    parser.add_argument('--packet-dir', default=str(DEFAULT_PACKET), help='Packet directory created by make micro-pilot-pack.')
    parser.add_argument('--write', action='store_true', help='Write MICRO-PILOT-NEXT-ACTION.json/.md in the packet directory, or in scratch/.../next-action if the packet is missing.')
    parser.add_argument('--json', action='store_true', help='Print the decision as JSON.')
    return parser.parse_args()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def load_result_followthrough(result_path: Path) -> dict:
    try:
        result = json.loads(result_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        return {
            'decision': 'unknown',
            'decision_class': 'unreadable_result_receipt',
            'operator_action': f'Result receipt exists but is unreadable JSON: {exc}. Stop and repair locally; do not import or publish.',
            'fresh_packet_allowed': False,
            'commands': [],
        }
    decision = str(result.get('decision') or '')
    stored = result.get('decision_followthrough') if isinstance(result.get('decision_followthrough'), dict) else None
    base = dict(DECISION_FOLLOWTHROUGH.get(decision, {
        'decision_class': 'unknown_result_decision',
        'operator_action': 'Result receipt exists but has no bounded recognized decision. Stop and inspect locally; do not import, publish, update service authority, or close FT-0181.',
        'fresh_packet_allowed': False,
        'command_templates': [],
    }))
    if stored:
        base.update({key: stored[key] for key in stored if key not in {'commands'}})
    templates = base.pop('command_templates', [])
    commands = [fresh_packet_from_decision_command(result_path) if item == 'fresh_micro_pilot_pack' else str(item) for item in templates]
    base['source_result_link_required'] = bool(commands)
    base['source_result_link_rule'] = 'fresh repeat/continue packets must be generated with SOURCE_RESULT and confirmation so the prior result is hash-linked but not imported as evidence or copied as seed text' if commands else 'no fresh packet source link emitted for this decision'
    return {'decision': decision or 'unknown', **base, 'commands': commands}


def write_router_markdown(path: Path, decision: dict) -> None:
    lines = [
        '# Teacher/tutor micro-pilot next-action brief',
        '',
        f"State: `{decision['router_state']}`",
        f"Revision: `{decision['revision']}`",
        f"Packet: `{decision['packet_dir']}`",
        f"Decision: `{decision['decision']}`",
        '',
        '## Operator action',
        '',
        decision['operator_action'],
        '',
    ]
    commands = decision.get('commands') or []
    if commands:
        lines.extend(['## Command(s)', ''])
        for command in commands:
            lines.extend(['```bash', command, '```', ''])
    if decision.get('readiness_status'):
        lines.extend(['## Readiness status', '', f"`{decision['readiness_status']}`", ''])
    if decision.get('readiness_next_actions'):
        lines.extend(['## Readiness next actions', ''])
        for item in decision['readiness_next_actions']:
            lines.append(f'- {item}')
        lines.append('')
    if decision.get('result_decision_followthrough'):
        lines.extend(['## Result decision follow-through', '', '```json', json.dumps(decision['result_decision_followthrough'], indent=2, sort_keys=True), '```', ''])
    lines.extend(['## Boundary', '', decision['claim_boundary'], ''])
    path.write_text('\n'.join(lines), encoding='utf-8')


def packet_missing_decision(packet_dir: Path) -> dict:
    return {
        'router_state': ROUTER_STATE,
        'revision': RECEIPT.get('revision'),
        'packet_dir': rel(packet_dir),
        'generated_at': utc_now(),
        'decision': 'PREPARE_PACKET',
        'readiness_status': None,
        'readiness_next_actions': [],
        'operator_action': 'No packet exists at this path. Prepare a fresh discovery-first, teacher-selected-concept packet before readiness scoring, optional dry-run, owner review, or evidence routing.',
        'commands': [DEFAULT_CONCEPT_COMMAND, readiness_command(packet_dir)],
        'write_dir': f"scratch/field-handoff/{RECEIPT.get('revision')}/teacher-tutor-micro-pilot/next-action",
        'claim_boundary': 'This router is local feasibility operator support only. Entry-ready status may support one locally approved teacher/tutor cycle outside the archive; it does not contact an owner, estimate efficacy, accept evidence, prove learning/access/safety/fairness/workload/effectiveness, authorize service use, support public claims, or close FT-0181. Result receipts remain descriptive local aggregate records only; non-retire repeat/continue decisions require a fresh source-result-linked packet seeded from local owner choices, not from a generic repeat command.',
    }


def decide(packet_dir: Path) -> dict:
    if not packet_dir.exists():
        return packet_missing_decision(packet_dir)
    card = score(packet_dir)
    status = card['status']
    result_followthrough = None
    if status == 'NOT_READY':
        action = 'Complete the cycle-entry fields before any learner-facing use. Do not fill post-cycle rows merely to satisfy the scorer; optional synthetic rehearsal belongs only on a disposable scratch packet.'
        commands = [readiness_command(packet_dir), dry_run_command(packet_dir), readiness_command(packet_dir)]
        decision = 'COMPLETE_ENTRY_PACKET_OR_OPTIONAL_DRY_RUN_COPY'
    elif status == ENTRY_READY_STATUS:
        action = 'The packet is ready for one locally approved teacher/tutor feasibility cycle. Run the cycle outside the archive under the completed owner plan and CYCLE-RUN-SHEET.md, then fill only aggregate post-cycle rows and rerun readiness before any owner-review stop record.'
        commands = [readiness_command(packet_dir)]
        decision = 'RUN_ONE_LOCAL_CYCLE_THEN_RERUN_READINESS'
    elif status == 'SYNTHETIC_READY_SMOKE_NOT_EVIDENCE':
        action = 'Synthetic rehearsal succeeded. Delete or regenerate this packet before any real owner work; do not hand a dry-run packet to a teacher/tutor owner.'
        commands = [f'rm -rf {rel(packet_dir)}', regenerate_command(packet_dir), readiness_command(packet_dir)]
        decision = 'DISCARD_SYNTHETIC_AND_REGENERATE'
    elif status == OWNER_REVIEW_READY_STATUS:
        result_path = packet_dir / 'MICRO-PILOT-RESULT.json'
        review_path = packet_dir / 'OWNER-REVIEW-STOP.json'
        if result_path.exists():
            result_followthrough = load_result_followthrough(result_path)
            action = result_followthrough['operator_action'] + ' The existing result remains local descriptive non-evidence and must not become a public claim, service authority change, evidence import, or FT-0181 closure artifact.'
            commands = result_followthrough.get('commands', [])
            decision = 'FOLLOW_LOCAL_RESULT_DECISION_NOT_EVIDENCE'
        elif review_path.exists():
            action = 'A human local owner-review stop record exists. Record the local descriptive feasibility result receipt only after confirming the packet still reflects that review; do not treat the receipt as accepted evidence or public-claim support.'
            commands = [result_command(packet_dir)]
            decision = 'RECORD_LOCAL_RESULT_RECEIPT_STOP'
        else:
            action = 'A fresh non-dry packet is coherent enough for local owner review of minimized aggregate rows. Stop at human review; after that review actually happens, record only the owner-review stop record. Do not import, publish, or update service authority without a separate accepted evidence route.'
            commands = [owner_review_command(packet_dir, card.get('owner_decision'))]
            decision = 'LOCAL_OWNER_REVIEW_STOP'
    else:
        action = 'Unknown readiness status; stop and inspect the packet locally without importing or publishing it.'
        commands = []
        decision = 'STOP_UNKNOWN_STATUS'
    return {
        'router_state': ROUTER_STATE,
        'revision': RECEIPT.get('revision'),
        'packet_dir': rel(packet_dir),
        'generated_at': utc_now(),
        'decision': decision,
        'readiness_status': status,
        'readiness_scorecard_state': card.get('scorecard_state'),
        'synthetic_dry_run': card.get('synthetic_dry_run'),
        'owner_decision': card.get('owner_decision'),
        'result_decision_followthrough': result_followthrough,
        'checks_passed': len([row for row in card.get('checks', []) if row.get('status') == 'pass']),
        'checks_total': len(card.get('checks', [])),
        'readiness_next_actions': card.get('next_actions', []),
        'operator_action': action,
        'commands': commands,
        'write_dir': rel(packet_dir),
        'claim_boundary': 'This router is local feasibility operator support only. Entry-ready status may support one locally approved teacher/tutor cycle outside the archive; it does not contact an owner, estimate efficacy, accept evidence, prove learning/access/safety/fairness/workload/effectiveness, authorize service use, support public claims, or close FT-0181. Result receipts remain descriptive local aggregate records only; non-retire repeat/continue decisions require a fresh source-result-linked packet seeded from local owner choices, not from a generic repeat command.',
    }


def main() -> None:
    args = parse_args()
    packet_dir = Path(args.packet_dir)
    if not packet_dir.is_absolute():
        packet_dir = ROOT / packet_dir
    safe_packet_path(packet_dir)
    decision = decide(packet_dir)
    if args.write:
        if packet_dir.exists():
            out_dir = packet_dir
            if decision.get('readiness_status'):
                card = score(packet_dir)
                (packet_dir / 'READINESS-SCORECARD.json').write_text(json.dumps(card, indent=2) + '\n', encoding='utf-8')
                write_score_markdown(packet_dir / 'READINESS-SCORECARD.md', card)
        else:
            out_dir = ROOT / 'scratch' / 'field-handoff' / RECEIPT.get('revision', 'unknown') / 'teacher-tutor-micro-pilot' / 'next-action'
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / 'MICRO-PILOT-NEXT-ACTION.json').write_text(json.dumps(decision, indent=2) + '\n', encoding='utf-8')
        write_router_markdown(out_dir / 'MICRO-PILOT-NEXT-ACTION.md', decision)
    if args.json:
        print(json.dumps(decision, indent=2))
    else:
        print(f"micro-pilot-next: {decision['decision']} for {decision['packet_dir']}")
        print(decision['operator_action'])
        for command in decision.get('commands', [])[:3]:
            print(f'- {command}')


if __name__ == '__main__':
    main()
