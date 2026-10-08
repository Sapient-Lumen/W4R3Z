#!/usr/bin/env python3
"""Triage an FT-0181 eight-row owner reply CSV before workbench import.

This tool is deliberately local and conservative. It does not certify evidence,
close FT-0181, or decide service claims. It only classifies a returned CSV as
ready to stage, needing one clarification, blocked, or absent.
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

from ft0181_field_guards import returned_owner_csv_source_block, returned_owner_csv_source_truth_class

EXPECTED_COLUMNS = [
    'row_id',
    'required_owner_reply',
    'owner_response',
    'local_only_check',
    'intake_note',
]
EXPECTED_ROW_IDS = [str(i) for i in range(1, 9)]
ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / 'fixtures'
SMOKE_LABELS = [
    'synthetic smoke fixture',
    'not a returned owner packet',
    'not src2+ evidence',
    'not closure evidence',
]

OUTCOME_ORDER = [
    'BLOCK-SECURITY',
    'BLOCK-PROTECTED',
    'BLOCK-OVERBROAD',
    'BLOCK-AUTHORITY',
    'BLOCK-EVIDENCE',
    'NO-OWNER-PACKET',
    'RE-ASK-ONCE',
    'PROCEED-STAGED',
]

PATTERNS = {
    'BLOCK-SECURITY': [
        r'api\s*key', r'credential', r'password', r'secret', r'system prompt',
        r'prompt injection', r'exploit', r'raw payload', r'tool payload', r'token=',
    ],
    'BLOCK-PROTECTED': [
        r'diagnos', r'disab', r'accommodation', r'\b504\b', r'\biep\b',
        r'safeguard', r'counsel', r'discipline', r'hardship', r'immigration',
        r'language[- ]access', r'wellbeing', r'family support', r'protected status',
        r'small[- ]cell', r'subgroup cut', r'protected[- ]status cut',
        r'(?<![A-Za-z0-9_])n\s*(?:=|<|:)\s*[1-9](?![0-9])', r'cell\s+(?:count|size)\s*(?:=|<|:)\s*[1-9](?![0-9])',
    ],
    'BLOCK-OVERBROAD': [
        r'full export', r'unrestricted export', r'data lake', r'all rows',
        r'row-level', r'learner-level', r'raw lms', r'raw learner', r'raw message',
        r'chat transcript', r'screenshot bundle', r'vendor dashboard', r'telemetry dump',
        r'gradebook export', r'attendance history',
    ],
}

SUPPORTED_UNKNOWN = {'unknown', 'not known', 'not available', 'n/a', 'na'}

NEXT_ACTIONS = {
    'PROCEED-STAGED': {
        'outcome': 'PROCEED-STAGED',
        'summary': 'Generate the proceed-staged note, then copy only minimized surviving answers into the owner packet workbench.',
        'next_artifact': 'templates/ft0181-proceed-staged-note-template.md',
        'ceiling': 'Staging note only; this is not closure evidence and cannot support public effectiveness claims.',
    },
    'RE-ASK-ONCE': {
        'outcome': 'RE-ASK-ONCE',
        'summary': 'Send one clarification using the re-ask template, then stage or block; do not widen the request.',
        'next_artifact': 'templates/ft0181-owner-reask-once-message.md',
        'ceiling': 'One clarification only; no full export, no added owner roster, and no new registry.',
    },
    'NO-OWNER-PACKET': {
        'outcome': 'NO-OWNER-PACKET',
        'summary': 'Record no viable owner packet after the response clock and keep FT-0181 live.',
        'next_artifact': 'templates/ft0181-triage-outcome-note-template.md',
        'ceiling': 'Do not create a new control, infer refusal meaning, or close FT-0181 from silence.',
    },
    'BLOCK-OVERBROAD': {
        'outcome': 'BLOCK-OVERBROAD',
        'summary': 'Record an overbroad-transfer block and do not accept a full export or raw trace bundle.',
        'next_artifact': 'templates/ft0181-triage-outcome-note-template.md',
        'ceiling': 'Keep the broad material local or delete/quarantine per local process; import no raw rows.',
    },
    'BLOCK-PROTECTED': {
        'outcome': 'BLOCK-PROTECTED',
        'summary': 'Record a protected-material block and keep protected facts, small cells, or route details local.',
        'next_artifact': 'templates/ft0181-triage-outcome-note-template.md',
        'ceiling': 'Import only an abstract block note if needed; do not transfer protected facts.',
    },
    'BLOCK-SECURITY': {
        'outcome': 'BLOCK-SECURITY',
        'summary': 'Record a security-material block and quarantine credentials, payloads, prompts, or exploit strings locally.',
        'next_artifact': 'templates/ft0181-triage-outcome-note-template.md',
        'ceiling': 'Import only abstract security class and owner action if safe; no raw payloads.',
    },
    'BLOCK-AUTHORITY': {
        'outcome': 'BLOCK-AUTHORITY',
        'summary': 'Record an authority block because draft-only, rollback, no-write, no-penalty, or local-control boundaries are not confirmed.',
        'next_artifact': 'templates/ft0181-triage-outcome-note-template.md',
        'ceiling': 'Do not start live-window work until a local accountable owner can bound action authority.',
    },
    'BLOCK-EVIDENCE': {
        'outcome': 'BLOCK-EVIDENCE',
        'summary': 'Record an evidence block because the reply is not owner-attested real operational material or makes unsupported claims.',
        'next_artifact': 'templates/ft0181-triage-outcome-note-template.md',
        'ceiling': 'Do not upgrade source truth, claim family, or closure posture from this reply.',
    },
}


def build_result(outcome, stage, is_real_packet, reasons, row_status):
    route = NEXT_ACTIONS[outcome]
    return {
        'outcome': outcome,
        'stage_to_workbench': stage,
        'is_real_packet': is_real_packet,
        'reasons': reasons,
        'row_status': row_status,
        'next_step': route['summary'],
        'next_action': route,
    }


def load_rows(path: Path):
    with path.open(newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    return reader.fieldnames or [], rows


def is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def has_smoke_labels(rows) -> bool:
    joined = ' '.join((row.get('owner_response') or '').lower() for row in rows)
    return any(label in joined for label in SMOKE_LABELS)


def source_truth_class(path: Path, rows, allow_src0_smoke: bool = False) -> str:
    # Use the shared returned-owner input classifier so direct triage, receipt,
    # staging, intake, and the field router enforce the same archive/source
    # boundary. Keep the row-label fallback for historical smoke CSV copies.
    src_class = returned_owner_csv_source_truth_class(path, archive_root=ROOT, allow_src0_smoke=allow_src0_smoke)
    if src_class == 'UNVERIFIED-OWNER-REPLY' and has_smoke_labels(rows):
        return 'SRC0-SMOKE'
    return src_class


def row_presence_status(responses: dict) -> list:
    statuses = []
    for i in range(1, 9):
        rid = str(i)
        value = responses.get(rid, '')
        if not value:
            status = 'blank'
        elif is_unknown(value):
            status = 'explicit_unknown'
        else:
            status = 'answered'
        statuses.append({'row_id': rid, 'status': status})
    return statuses


def contains_any(text: str, patterns):
    hits = []
    guarded = {'removed', 'withheld', 'kept local', 'excluded', 'suppressed', 'not include', 'no '}
    chunks = re.split(r'[.;\n]+', text)
    for pattern in patterns:
        for chunk in chunks:
            lower = chunk.lower()
            if re.search(pattern, chunk, flags=re.IGNORECASE):
                if any(word in lower for word in guarded):
                    continue
                hits.append(pattern)
                break
    return hits


def norm(value):
    return (value or '').strip()


def row_by_id(rows, row_id):
    for row in rows:
        if norm(row.get('row_id')) == str(row_id):
            return row
    return {}


def is_unknown(value):
    lowered = norm(value).lower()
    return lowered in SUPPORTED_UNKNOWN or lowered.startswith('unknown')


def authority_confirmed(text: str) -> bool:
    t = text.lower()
    has_draft = 'draft' in t or 'queue note' in t or 'staff note' in t
    no_auto = any(x in t for x in ['no automatic', 'not automatic', 'manual send', 'human sent', 'human-sent', 'human sends'])
    no_write = any(x in t for x in ['no durable write', 'no write', 'not write', 'no posting', 'not posted'])
    no_penalty = any(x in t for x in ['no penalty', 'not penalty', 'no grade', 'no grading'])
    no_protected = any(x in t for x in ['no protected', 'not infer protected', 'no protected-status', 'no status inference'])
    return has_draft and no_auto and no_write and no_penalty and no_protected



def vendor_only_rollback(text: str) -> bool:
    t = text.lower()
    if 'vendor' not in t:
        return False
    local_owner_terms = ['rollback owner is', 'course operations lead', 'human fallback', 'internal owner']
    vendor_only_terms = [
        'vendor only', 'vendor-only', 'vendor action alone', 'requires vendor',
        'must ask vendor', 'vendor must', 'no local rollback', 'cannot roll back locally',
        'not locally roll back', 'vendor-controlled rollback',
    ]
    return any(term in t for term in vendor_only_terms) and not any(term in t for term in local_owner_terms)


def evidence_attested(text: str) -> bool:
    t = text.lower()
    if any(x in t for x in ['mock', 'rehearsal only', 'template only', 'vendor only', 'vendor-only', 'unreviewed analytics']):
        return False
    return 'real' in t and ('owner' in t or 'attest' in t) and any(x in t for x in ['redact', 'withheld', 'kept local', 'removed'])


def unsupported_claim_language(text: str):
    t = text.lower()
    bad = []
    positive_claims = [
        ('learning', ['improved learning', 'raises learning', 'learning gains', 'proves learning']),
        ('effectiveness', ['effective', 'effectiveness proven', 'works better', 'proves it works']),
        ('safety', ['safe for all', 'proves safe', 'safety proven']),
        ('access', ['improves access', 'equitable for all', 'access proven']),
        ('workload', ['reduces workload', 'saves time', 'workload reduction proven']),
        ('compliance', ['compliant', 'compliance proven']),
        ('scale', ['ready to scale', 'scale-ready', 'scalable across']),
    ]
    for label, phrases in positive_claims:
        for phrase in phrases:
            if phrase in t and not any(guard in t for guard in ['do not claim', 'cannot claim', 'no claim', 'not claim', 'not enough']):
                bad.append(label)
                break
    return sorted(set(bad))


def triage_csv(path: Path, allow_src0_smoke: bool = False):
    fieldnames, rows = load_rows(path)
    reasons = []
    row_status = []
    flags = []

    if fieldnames != EXPECTED_COLUMNS:
        return build_result(
            'RE-ASK-ONCE',
            False,
            False,
            [f'CSV columns must exactly match {EXPECTED_COLUMNS}; received {fieldnames}'],
            [],
        )

    row_ids = [norm(row.get('row_id')) for row in rows]
    if len(rows) != 8 or row_ids != EXPECTED_ROW_IDS:
        return build_result(
            'RE-ASK-ONCE',
            False,
            False,
            ['CSV must contain exactly eight rows with row_id values 1 through 8.'],
            [],
        )

    responses = {str(i): norm(row_by_id(rows, i).get('owner_response')) for i in range(1, 9)}
    response_text = ' '.join(responses.values())
    blank_rows = [rid for rid, value in responses.items() if not value]
    unknown_rows = [rid for rid, value in responses.items() if is_unknown(value)]

    src_class = source_truth_class(Path(path), rows, allow_src0_smoke=allow_src0_smoke)
    source_block = returned_owner_csv_source_block(Path(path), archive_root=ROOT, allow_src0_smoke=allow_src0_smoke)
    if source_block:
        result = build_result(
            'BLOCK-EVIDENCE',
            False,
            False,
            [f'BLOCK-EVIDENCE: CSV source is archive-controlled ({source_block}), not a returned owner packet. Use a local scratch or external returned-owner CSV path routed through make owner-field-next.'],
            row_presence_status(responses),
        )
        result['source_truth_class'] = src_class
        return result

    if src_class == 'SRC0-SMOKE' and not allow_src0_smoke:
        result = build_result(
            'BLOCK-EVIDENCE',
            False,
            False,
            ['BLOCK-EVIDENCE: CSV is labelled or located as an SRC0 smoke fixture, not a returned owner packet. Use make owner-reply-smoke for plumbing checks only.'],
            row_presence_status(responses),
        )
        result['source_truth_class'] = src_class
        return result

    if not response_text.strip():
        result = build_result(
            'NO-OWNER-PACKET',
            False,
            False,
            ['No owner_response values are present; treat the file as a blank template or no returned packet.'],
            [{'row_id': str(i), 'status': 'blank'} for i in range(1, 9)],
        )
        result['source_truth_class'] = src_class
        return result

    for outcome, patterns in PATTERNS.items():
        matches = contains_any(response_text, patterns)
        if matches:
            flags.append(outcome)
            reasons.append(f'{outcome}: owner_response contains local-only or blocked terms: ' + ', '.join(matches[:5]))

    if len(blank_rows) > 2:
        flags.append('NO-OWNER-PACKET')
        reasons.append(f'NO-OWNER-PACKET: more than two required rows are blank: {", ".join(blank_rows)}')
    elif blank_rows:
        flags.append('RE-ASK-ONCE')
        reasons.append(f'RE-ASK-ONCE: one or two rows are blank: {", ".join(blank_rows)}')

    mandatory_not_unknown = ['1', '3', '7', '8']
    impossible_unknown = [rid for rid in mandatory_not_unknown if rid in unknown_rows]
    if impossible_unknown:
        flags.append('RE-ASK-ONCE')
        reasons.append('RE-ASK-ONCE: rows 1, 3, 7, and 8 need a substantive owner answer, not unknown: ' + ', '.join(impossible_unknown))

    if responses['3'] and not is_unknown(responses['3']) and not authority_confirmed(responses['3']):
        flags.append('BLOCK-AUTHORITY')
        reasons.append('BLOCK-AUTHORITY: row 3 does not clearly confirm draft-only, no automatic send, no durable write, no penalty, and no protected-status inference.')

    if responses['4'] and not is_unknown(responses['4']) and vendor_only_rollback(responses['4']):
        flags.append('BLOCK-AUTHORITY')
        reasons.append('BLOCK-AUTHORITY: row 4 makes fallback or rollback depend on vendor-only action without a local accountable rollback owner.')

    if responses['8'] and not is_unknown(responses['8']) and not evidence_attested(responses['8']):
        flags.append('BLOCK-EVIDENCE')
        reasons.append('BLOCK-EVIDENCE: row 8 does not clearly attest real owner-reviewed operational material with raw/protected/small-cell/security material removed, withheld, or kept local.')

    unsupported = unsupported_claim_language(responses['7'])
    if unsupported:
        flags.append('BLOCK-EVIDENCE')
        reasons.append('BLOCK-EVIDENCE: row 7 appears to assert unsupported public claim families: ' + ', '.join(unsupported))

    if not flags:
        flags.append('PROCEED-STAGED')
        reasons.append('All eight rows are present or allowable unknowns, no local-only content was detected, and staging can proceed to the owner packet workbench.')

    outcome = sorted(set(flags), key=lambda x: OUTCOME_ORDER.index(x))[0]
    stage = outcome == 'PROCEED-STAGED'

    row_status = row_presence_status(responses)
    result = build_result(outcome, stage, stage and src_class != 'SRC0-SMOKE', reasons, row_status)
    result['source_truth_class'] = src_class
    if src_class == 'SRC0-SMOKE' and allow_src0_smoke:
        result['reasons'].append('SRC0-SMOKE: fixture or smoke-labelled content was allowed only for the smoke harness and remains non-evidence.')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description='Triage an FT-0181 eight-row owner reply CSV before workbench import.')
    parser.add_argument('csv_path', type=Path)
    parser.add_argument('--json', action='store_true', help='Emit machine-readable JSON only.')
    parser.add_argument('--allow-src0-smoke', action='store_true', help='Internal smoke-harness opt-in only; normal triage blocks smoke fixtures and smoke-labelled CSVs.')
    args = parser.parse_args(argv)
    result = triage_csv(args.csv_path, allow_src0_smoke=args.allow_src0_smoke)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"outcome: {result['outcome']}")
        print(f"stage_to_workbench: {str(result['stage_to_workbench']).lower()}")
        next_action = result.get('next_action', {})
        if next_action.get('next_artifact'):
            print(f"next_artifact: {next_action['next_artifact']}")
        if next_action.get('summary'):
            print(f"next_step: {next_action['summary']}")
        for reason in result['reasons']:
            print(f'- {reason}')
    return 0 if result['outcome'] in {'PROCEED-STAGED', 'RE-ASK-ONCE', 'NO-OWNER-PACKET'} else 2


if __name__ == '__main__':
    raise SystemExit(main())
