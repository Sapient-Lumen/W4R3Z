#!/usr/bin/env python3
"""Prepare one scratch-only field handoff bundle for the live AI-EDU moves.

This is an operator aid, not evidence. It composes the existing FT-0181 owner
request packet and a discovery-first teacher/tutor move-coach feasibility packet into a
single local bundle so the next human actions can happen without reopening the
registry/governance tail. It does not send messages, run a pilot, accept source
truth, create custody, update service authority, support public claims, or close
FT-0181.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
REVISION = RECEIPT.get('revision', 'unknown')
DEFAULT_OUT = ROOT / 'scratch' / 'field-handoff' / REVISION
OWNER_DIR_NAME = 'ft0181-owner-request'
PILOT_ROOT_NAME = 'teacher-tutor-micro-pilot'

FORBIDDEN_ARG_TERMS = [
    'student id', 'learner id', 'student name', 'learner name', 'full name', 'email address',
    'ssn', 'social security', 'iep', '504 plan', 'disability facts', 'accommodation facts',
    'protected status', 'gradebook row', 'raw work', 'screenshot', 'recording', 'chat transcript',
    'discipline record', 'risk score', 'api key', 'credential', 'raw lms export', 'vendor dashboard',
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Prepare a scratch-only AI-EDU field handoff bundle.')
    parser.add_argument('--output-dir', default=str(DEFAULT_OUT), help='Scratch/external output directory for the composed handoff bundle.')
    parser.add_argument('--service-label', default='AIEDU-SR-003 draft reminder pilot')
    parser.add_argument('--owner-role', default='accountable service owner')
    parser.add_argument('--source-record-set', default='local service record set or source system, to be named by the owner')
    parser.add_argument('--date-range', default='owner-named date range')
    parser.add_argument('--return-date', default='', help='Optional YYYY-MM-DD return date for the owner request; default remains the bounded first-contact clock.')
    parser.add_argument('--concept-code', default='teacher-selected-concept')
    parser.add_argument('--concept', default='one teacher/tutor-selected misconception or reasoning move tied to current curriculum')
    parser.add_argument('--setting', default='one teacher-owned practice group selected locally')
    parser.add_argument('--pilot-owner-role', default='classroom teacher or tutoring lead')
    parser.add_argument('--pilot-date-range', default='owner-selected bounded window')
    parser.add_argument('--fallback', default='ordinary non-AI practice and teacher/tutor support without penalty')
    parser.add_argument('--transfer-check', default='one no-AI transfer or explanation check selected before coach use')
    parser.add_argument('--approved-vocabulary', default='owner-approved vocabulary and current-curriculum boundary')
    parser.add_argument('--concept-kit', default='generic', choices=['generic', 'equality-one-step'])
    parser.add_argument('--overwrite', action='store_true')
    parser.add_argument('--json', action='store_true', help='Print the bundle manifest as JSON.')
    return parser.parse_args()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def slugify(value: str) -> str:
    slug = re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')
    slug = re.sub(r'-{2,}', '-', slug)
    return slug[:80] or 'one-concept-move-coach'


def forbidden_reason(values: Iterable[str]) -> str | None:
    combined = ' '.join(values).lower()
    if '@' in combined:
        return 'email-like address marker @'
    for term in FORBIDDEN_ARG_TERMS:
        if term in combined:
            return term
    return None


def output_allowed(path: Path) -> None:
    resolved = path.resolve()
    scratch = (ROOT / 'scratch').resolve()
    try:
        resolved.relative_to(scratch)
        return
    except ValueError:
        pass
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        return
    raise SystemExit('output-dir must be under scratch/ or outside the repository; refuse release-path field handoff')


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if proc.returncode != 0:
        rendered = ' '.join(cmd)
        raise SystemExit(f'field handoff subcommand failed ({rendered})\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}')
    return proc


def write_handoff_md(path: Path, manifest: dict) -> None:
    owner = manifest['owner_packet']
    pilot = manifest['micro_pilot_packet']
    lines = [
        '# AI-EDU field handoff bundle',
        '',
        f"Bundle state: `{manifest['bundle_state']}`",
        f"Revision: `{manifest['revision']}`",
        f"Output: `{manifest['output_dir']}`",
        '',
        'This is the one-place handoff for the teacher/tutor discovery rail. The owner-evidence rail is secondary and should not displace the first local educator conversation.',
        '',
        '## First rail: teacher/tutor discovery contact',
        '',
        f"Open `{pilot['discovery_ask']}` first.",
        f"Use it to secure one real educator conversation and choose a local concept before editing `{pilot['owner_plan']}`.",
        f"Then open `{pilot['cycle_run_sheet']}`, `{pilot['run_checklist']}`, and `{pilot['measure_card']}`.",
        f"Complete every discovery, intervention-version, participation, fallback, numeric small-cell threshold, protected-review field, and prompt-unchanged attestation in `{pilot['owner_plan']}` before learner-facing work.",
        'Run readiness before the cycle. `READY_FOR_LOCAL_CYCLE_NOT_EVIDENCE` now also means the generated discovery card, coach prompt, checklist, measure card, and run sheet still match their generation-time hashes; it is not evidence or owner-review readiness.',
        f"After that cycle actually happens, fill descriptive aggregate rows in `{pilot['session_log']}` and `{pilot['final_readout']}`. Use ISO dates ordered baseline <= coach-use <= transfer; owner review must be on or after the latest session row. Mask small-cell counts/rates in any receipt, and rerun readiness.",
        'Run readiness and next-action routing:',
        '',
        '```bash',
        manifest['commands']['micro_pilot_readiness'],
        manifest['commands']['micro_pilot_next'],
        '```',
        '',
        'If readiness reaches `READY_FOR_LOCAL_OWNER_REVIEW_NOT_EVIDENCE` and a human owner actually reviews the aggregate readout, use the emitted owner-review stop command; that record hash-locks the run-defining prompt/checklist/run-sheet files and refuses a review date before the latest session row before any result receipt can be recorded. After a result exists, run the next-action router again and follow only the bounded decision map: retire stops, repeat/continue require a fresh packet, and escalation requires a separate future accepted route.',
        '',
        '## Secondary rail: owner evidence boundary',
        '',
        f"Open `{owner['send_now_brief']}` only if a real accountable owner route exists.",
        f"Copy the subject/body from `{owner['email']}` and attach only `{owner['reply_template']}` after a human has confirmed the route.",
        'After the human send or adaptation actually happens, run the router and execute only the dated command it emits:',
        '',
        '```bash',
        manifest['commands']['owner_after_send_router'],
        '```',
        '',
        'If no accountable owner route exists, do not record a send log. Use the route-block command in the send-now brief.',
        '',
        '## Boundary',
        '',
        manifest['claim_boundary'],
        '',
        '## What not to open first',
        '',
        'Do not start with broad governance profiles, branch-family history, public-claim lexicons, release examples, or FT-0181 administration. Open those only after a real returned owner packet, a real local owner-reviewed micro-pilot packet, or a validator failure requires them.',
        '',
    ]
    path.write_text('\n'.join(lines), encoding='utf-8')

def write_next_commands(path: Path, manifest: dict) -> None:
    lines = [
        '# Field handoff next commands',
        '',
        'Run these from the repository root. Replace `YYYY-MM-DD` only after the human event actually happens.',
        '',
        '## Micro-pilot rail first',
        '',
        '```bash',
        manifest['commands']['micro_pilot_readiness'],
        manifest['commands']['micro_pilot_next'],
        '```',
        '',
        '`NOT_READY` means entry fields are incomplete/unsafe or partially filled post-cycle rows need repair, including numeric small-cell threshold, run-definition hash stability, and event chronology. `READY_FOR_LOCAL_CYCLE_NOT_EVIDENCE` means use `CYCLE-RUN-SHEET.md` for exactly one locally approved cycle, then fill aggregate post-cycle rows with ISO dates ordered baseline <= coach-use <= transfer and mask small-cell receipt values. `READY_FOR_LOCAL_OWNER_REVIEW_NOT_EVIDENCE` means stop for human owner review dated on or after the latest session row. Once `MICRO-PILOT-RESULT.json` exists, router output must follow `decision_followthrough` rather than treating the receipt as evidence or a service decision.',
        '',
        '## Owner rail only after a real route exists',
        '',
        '```bash',
        manifest['commands']['owner_after_send_router'],
        f"make owner-field-next CSV=/path/to/returned-owner-reply.csv OUT=scratch/field/ft0181/ft0181-field-next-action/returned-owner-reply",
        '```',
        '',
    ]
    path.write_text('\n'.join(lines), encoding='utf-8')

def build(args: argparse.Namespace) -> dict:
    reason = forbidden_reason([
        args.service_label, args.owner_role, args.source_record_set, args.date_range, args.return_date,
        args.concept_code, args.concept, args.setting, args.pilot_owner_role, args.pilot_date_range,
        args.fallback, args.transfer_check, args.approved_vocabulary,
    ])
    if reason:
        raise SystemExit(f'refuse field handoff bundle args containing raw/protected/identifying material: {reason}')

    out = Path(args.output_dir)
    if not out.is_absolute():
        out = ROOT / out
    output_allowed(out)
    if out.exists() and any(out.iterdir()):
        if not args.overwrite:
            raise SystemExit(f'output exists; pass --overwrite to replace: {rel(out)}')
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    owner_dir = out / OWNER_DIR_NAME
    pilot_root = out / PILOT_ROOT_NAME
    concept_code = slugify(args.concept_code)
    pilot_dir = pilot_root / concept_code

    owner_cmd = [
        sys.executable, 'tools/prepare_ft0181_owner_request_packet.py',
        '--output-dir', str(owner_dir),
        '--service-label', args.service_label,
        '--owner-role', args.owner_role,
        '--source-record-set', args.source_record_set,
        '--date-range', args.date_range,
        '--overwrite',
    ]
    if args.return_date:
        owner_cmd.extend(['--return-date', args.return_date])
    pilot_cmd = [
        sys.executable, 'tools/prepare_teacher_tutor_micro_pilot_pack.py',
        '--output-root', str(pilot_root),
        '--concept-code', args.concept_code,
        '--concept', args.concept,
        '--setting', args.setting,
        '--owner-role', args.pilot_owner_role,
        '--date-range', args.pilot_date_range,
        '--fallback', args.fallback,
        '--transfer-check', args.transfer_check,
        '--approved-vocabulary', args.approved_vocabulary,
        '--concept-kit', args.concept_kit,
        '--overwrite',
    ]
    run(owner_cmd)
    run(pilot_cmd)
    run([sys.executable, 'tools/score_teacher_tutor_micro_pilot_readiness.py', '--packet-dir', str(pilot_dir), '--write'])
    run([sys.executable, 'tools/decide_teacher_tutor_micro_pilot_next_action.py', '--packet-dir', str(pilot_dir), '--write'])

    owner_manifest_path = owner_dir / 'packet-manifest.json'
    pilot_manifest_path = pilot_dir / 'PACK-MANIFEST.json'
    owner_manifest = json.loads(owner_manifest_path.read_text(encoding='utf-8'))
    pilot_manifest = json.loads(pilot_manifest_path.read_text(encoding='utf-8'))

    manifest_path = out / 'FIELD-HANDOFF-BUNDLE.json'
    md_path = out / 'FIELD-HANDOFF.md'
    command_path = out / 'NEXT-COMMANDS.md'
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    manifest = {
        'bundle_state': 'PREPARED_FIELD_HANDOFF_NOT_EVIDENCE',
        'revision': REVISION,
        'generated_at': generated_at,
        'output_dir': rel(out),
        'owner_packet': {
            'dir': rel(owner_dir),
            'manifest': rel(owner_manifest_path),
            'email': rel(owner_dir / 'AIEDU-SR-003-owner-request-email.txt'),
            'reply_template': rel(owner_dir / 'AIEDU-SR-003-eight-row-owner-reply-template.csv'),
            'send_now_brief': rel(owner_dir / 'SEND-NOW-BRIEF.md'),
            'packet_state': owner_manifest.get('packet_state'),
            'evidence_state': owner_manifest.get('evidence_state'),
        },
        'micro_pilot_packet': {
            'dir': rel(pilot_dir),
            'manifest': rel(pilot_manifest_path),
            'readiness_scorecard': rel(pilot_dir / 'READINESS-SCORECARD.json'),
            'next_action_brief': rel(pilot_dir / 'MICRO-PILOT-NEXT-ACTION.md'),
            'discovery_ask': rel(pilot_dir / 'DISCOVERY-FIRST-CONTACT.md'),
            'owner_plan': rel(pilot_dir / 'OWNER-PLAN.md'),
            'session_log': rel(pilot_dir / 'SESSION-LOG.csv'),
            'final_readout': rel(pilot_dir / 'FINAL-READOUT.csv'),
            'run_checklist': rel(pilot_dir / 'RUN-CHECKLIST.md'),
            'measure_card': rel(pilot_dir / 'MEASURE-CARD.md'),
            'cycle_run_sheet': rel(pilot_dir / 'CYCLE-RUN-SHEET.md'),
            'packet_state': pilot_manifest.get('packet_state'),
            'evidence_state': pilot_manifest.get('evidence_state'),
            'evaluation_class': pilot_manifest.get('evaluation_class'),
            'concept_selection_rule': pilot_manifest.get('concept_selection_rule'),
        },
        'commands': {
            'owner_after_send_router': 'make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/aiedu-sr-003-after-send',
            'micro_pilot_readiness': f'make micro-pilot-readiness PACKET={rel(pilot_dir)} WRITE=1',
            'micro_pilot_next': f'make micro-pilot-next PACKET={rel(pilot_dir)} WRITE=1',
        },
        'claim_boundary': 'The field handoff bundle is local operator support only. Its pedagogical rail prepares discovery and one bounded feasibility/usability cycle, not efficacy evaluation. It sends nothing, runs no cycle, records no human review or result, masks no real data because none exists, accepts no evidence, creates no custody, upgrades no service authority, supports no public claim, treats any future result decision as bounded local follow-through only, and does not close FT-0181. Generated contents remain scratch/external artifacts excluded from release packaging unless a future explicit accepted route changes that rule.',
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    write_handoff_md(md_path, manifest)
    write_next_commands(command_path, manifest)
    manifest['bundle_manifest'] = rel(manifest_path)
    manifest['handoff_markdown'] = rel(md_path)
    manifest['next_commands'] = rel(command_path)
    # Re-write with the self-references after the files exist. Do not hash-lock scratch output.
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


def main() -> None:
    args = parse_args()
    manifest = build(args)
    if args.json:
        print(json.dumps(manifest, indent=2))
    else:
        print(f"prepare_field_handoff_bundle: wrote {manifest['output_dir']}")
        print('state: PREPARED_FIELD_HANDOFF_NOT_EVIDENCE; no send, no run, no evidence, no closure')
        print(f"open: {manifest['handoff_markdown']}")


if __name__ == '__main__':
    main()
