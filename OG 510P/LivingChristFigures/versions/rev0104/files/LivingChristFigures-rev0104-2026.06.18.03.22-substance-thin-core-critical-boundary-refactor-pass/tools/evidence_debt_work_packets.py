#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re, sys
from collections import defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
from lib_cube import read_csv_rows, write_csv_json_md_report

PACKET_FIELDS = [
    'packet_id','packet_rank','priority_band','risk_lane','candidate_id','candidate_name',
    'debt_count','critical_debt_count','high_debt_count','execution_ids','debt_ids','claim_ids',
    'packet_goal','first_manual_step','acceptable_source_classes','blocked_extraction_modes',
    'acceptance_criteria','completion_evidence_slot','public_boundary_after_completion',
    'reviewer_role','status','note'
]
AUDIT_FIELDS = ['audit_id','check','severity','status','subject_id','expected','observed','note']

URL_RE = re.compile(r'https?://|www\.', re.I)
EMAIL_RE = re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', re.I)
PHONE_RE = re.compile(r'(?<!\w)(?:\+?\d[\d\s().-]{6,}\d)(?!\w)')
PRIORITY_WEIGHT = {'critical': 0, 'high': 1, 'medium': 2, 'standard': 3, '': 9}
LANE_WEIGHT = {'lane_0_critical_manual_first': 0, 'lane_1_high_sensitive_boundary': 1, 'lane_2_high_source_balance_or_claim_support': 2}


def split_pipe(value: str) -> list[str]:
    seen = []
    for part in (value or '').split('|'):
        part = part.strip()
        if part and part not in seen:
            seen.append(part)
    return seen


def write_field_schema(root: Path, rel: str, fields: list[str], meanings: dict[str, str]) -> None:
    rows = []
    for field in fields:
        rows.append({
            'field': field,
            'required': 'yes',
            'allowed_values_or_pattern': 'nonempty text' if field not in {'claim_ids'} else 'pipe-separated claim_id values; may be blank only when no claim mapping exists',
            'meaning': meanings.get(field, field),
        })
    write_csv_json_md_report(
        root, rel, ['field','required','allowed_values_or_pattern','meaning'], rows,
        Path(rel).name[:-4].replace('-', ' '), 'tools/evidence_debt_work_packets.py',
        columns=['field','required','allowed_values_or_pattern','meaning'], max_md_rows=80,
    )


def compact_join(values: list[str], limit: int = 5) -> str:
    out = []
    for value in values:
        value = (value or '').strip()
        if value and value not in out:
            out.append(value)
    if len(out) <= limit:
        return ' | '.join(out)
    return ' | '.join(out[:limit]) + f' | … {len(out)-limit} more; see execution rows'


def packet_goal(priority: str, lane: str, debt_count: int) -> str:
    if priority == 'critical':
        return 'Resolve or explicitly re-quarantine the critical evidence blocker before any public wording, source expansion, or claim promotion is attempted.'
    if lane == 'lane_1_high_sensitive_boundary':
        return 'Convert sensitive high-priority debt into a documented boundary decision: safe source class, affected claims, and no-public-expansion outcome.'
    return 'Confirm whether the source-balance or claim-support debt can move toward support, remain queued, or require re-quarantine.'


def acceptance_criteria(priority: str, lane: str) -> str:
    if priority == 'critical':
        return 'Manual reviewer records one of: verified high-level non-operational support; explicit no-update with reason; or strengthened quarantine. Evidence update must avoid URLs/contact paths/case details and must name affected claim ids.'
    if lane == 'lane_1_high_sensitive_boundary':
        return 'Manual reviewer records source class, affected claims, boundary decision, and forbidden details reviewed; public posture stays closed unless a separate governance ledger row changes.'
    return 'Manual reviewer records source class, claim-support outcome, and remaining debt status; no public link or public wording changes are implied by completion.'


def blocked_modes(rows: list[dict[str, str]]) -> str:
    base = []
    for row in rows:
        for item in split_pipe(row.get('forbidden_modes','')):
            base.append(item)
    if not base:
        base = ['No public URLs, contact paths, case lists, person-level stories, images, testimony, routes, live-capacity claims, referrals, legal advice, or medical advice.']
    return compact_join(base, limit=4)


def run(root: Path):
    queue = read_csv_rows(root / 'META/Evidence-Debt-Execution-Queue-current.csv')
    debts = {r.get('debt_id',''): r for r in read_csv_rows(root / 'Evidence-Debt-current.csv')}
    claims = {r.get('claim_id',''): r for r in read_csv_rows(root / 'Claim-Ledger-current.csv')}
    by_key: dict[tuple[str,str,str], list[dict[str,str]]] = defaultdict(list)
    for row in queue:
        key = (row.get('priority',''), row.get('risk_lane',''), row.get('candidate_id',''))
        by_key[key].append(row)

    packets = []
    ordered = sorted(
        by_key.items(),
        key=lambda kv: (
            PRIORITY_WEIGHT.get(kv[0][0], 9),
            LANE_WEIGHT.get(kv[0][1], 9),
            min(int(r.get('execution_order') or '999999') for r in kv[1]),
            kv[0][2],
        ),
    )
    for idx, ((priority, lane, cid), rows) in enumerate(ordered, start=1):
        rows = sorted(rows, key=lambda r: int(r.get('execution_order') or '999999'))
        debt_ids = [r.get('debt_id','') for r in rows if r.get('debt_id')]
        exec_ids = [r.get('execution_id','') for r in rows if r.get('execution_id')]
        claim_ids = []
        source_classes = []
        actions = []
        for row in rows:
            claim_ids.extend(split_pipe(row.get('target_claim_ids','')))
            source_classes.append(row.get('source_need',''))
            actions.append(row.get('next_concrete_action',''))
        crit = sum(1 for d in debt_ids if debts.get(d,{}).get('priority') == 'critical')
        high = sum(1 for d in debt_ids if debts.get(d,{}).get('priority') == 'high')
        cid_label = rows[0].get('candidate_name','')
        packets.append({
            'packet_id': f'work_packet_{idx:04d}',
            'packet_rank': str(idx),
            'priority_band': priority,
            'risk_lane': lane,
            'candidate_id': cid,
            'candidate_name': cid_label,
            'debt_count': str(len(debt_ids)),
            'critical_debt_count': str(crit),
            'high_debt_count': str(high),
            'execution_ids': '|'.join(exec_ids),
            'debt_ids': '|'.join(debt_ids),
            'claim_ids': '|'.join([x for x in dict.fromkeys(claim_ids) if x in claims]),
            'packet_goal': packet_goal(priority, lane, len(debt_ids)),
            'first_manual_step': actions[0] if actions else 'manual triage required before execution',
            'acceptable_source_classes': compact_join(source_classes, limit=4),
            'blocked_extraction_modes': blocked_modes(rows),
            'acceptance_criteria': acceptance_criteria(priority, lane),
            'completion_evidence_slot': f'META/Evidence-Debt-Manual-Completion-Ledger-future.csv::{cid}::{"+".join(debt_ids[:3])}',
            'public_boundary_after_completion': 'completion_is_internal_evidence_work_only_no_public_release_or_contact_authorization',
            'reviewer_role': 'manual_boundary_reviewer_required' if priority == 'critical' or lane == 'lane_1_high_sensitive_boundary' else 'manual_evidence_reviewer_required',
            'status': 'ready_for_manual_packet_execution',
            'note': 'Generated from Evidence-Debt-Execution-Queue-current.csv to make the backlog executable in grouped human work packets; not a publication permission.',
        })

    audit = []
    def add(check, severity, status, subject, expected, observed, note):
        audit.append({
            'audit_id': f'evidence_work_packet_audit_{len(audit)+1:04d}',
            'check': check,
            'severity': severity,
            'status': status,
            'subject_id': subject,
            'expected': expected,
            'observed': observed,
            'note': note,
        })

    queue_exec_ids = [r.get('execution_id','') for r in queue if r.get('execution_id')]
    packet_exec_ids = []
    for packet in packets:
        packet_exec_ids.extend(split_pipe(packet.get('execution_ids','')))
    qset, pset = set(queue_exec_ids), set(packet_exec_ids)
    dup_exec = sorted({eid for eid in packet_exec_ids if packet_exec_ids.count(eid) > 1})
    missing = sorted(qset - pset)
    extra = sorted(pset - qset)
    add('queue_rows_assigned_exactly_once', 'high' if missing or extra or dup_exec else 'info', 'fail' if missing or extra or dup_exec else 'pass', 'META/Evidence-Debt-Execution-Queue-current.csv', 'all execution_ids assigned exactly once to packets', f'missing={len(missing)} extra={len(extra)} duplicate={len(dup_exec)}', 'work packets must cover the full execution queue without silently losing or duplicating rows')

    crit_packets = [p for p in packets if p.get('priority_band') == 'critical']
    crit_queue = [r for r in queue if r.get('priority') == 'critical']
    crit_late = [p.get('packet_id') for p in crit_packets if int(p.get('packet_rank','9999')) > len(crit_packets)]
    add('critical_packets_ordered_first', 'high' if crit_late or not crit_packets or len(crit_queue) and not crit_packets else 'info', 'fail' if crit_late or (crit_queue and not crit_packets) else 'pass', 'priority=critical', 'critical work packets rank first', f'critical_packets={len(crit_packets)} late={len(crit_late)}', 'critical evidence blockers must not be buried beneath high-priority packets')

    missing_criteria = []
    for p in packets:
        for field in ['packet_goal','first_manual_step','acceptable_source_classes','blocked_extraction_modes','acceptance_criteria','completion_evidence_slot','public_boundary_after_completion','reviewer_role']:
            if not p.get(field):
                missing_criteria.append(p.get('packet_id') + ':' + field)
    add('packet_execution_fields_present', 'high' if missing_criteria else 'info', 'fail' if missing_criteria else 'pass', 'work packets', 'goal, first step, source class, blocked modes, acceptance, completion slot, boundary, reviewer role', str(len(missing_criteria)), 'packets must be executable enough for a manual reviewer without reading all underlying queue rows first')

    unsafe = []
    for p in packets:
        blob = ' '.join(p.values())
        if URL_RE.search(blob) or EMAIL_RE.search(blob) or PHONE_RE.search(blob):
            unsafe.append(p.get('packet_id'))
    add('packets_contain_no_direct_contacts_or_urls', 'high' if unsafe else 'info', 'fail' if unsafe else 'pass', 'work packets', 'no URL/email/phone-like strings', str(len(unsafe)), 'work packet text must not smuggle public source links, contact paths, or phone-like details into the manual handoff')

    public_bad = [p.get('packet_id') for p in packets if 'no_public_release' not in p.get('public_boundary_after_completion','')]
    add('completion_does_not_authorize_public_release', 'high' if public_bad else 'info', 'fail' if public_bad else 'pass', 'public boundary', 'completion is internal-only and not a public release authorization', str(len(public_bad)), 'finishing evidence work must not be confused with permission to publish, contact, refer, or route')

    bad_claims = []
    for p in packets:
        for claim_id in split_pipe(p.get('claim_ids','')):
            if claim_id not in claims:
                bad_claims.append(p.get('packet_id') + ':' + claim_id)
    add('packet_claim_ids_resolve', 'high' if bad_claims else 'info', 'fail' if bad_claims else 'pass', 'Claim-Ledger-current.csv', 'all packet claim_ids resolve or are blank', str(len(bad_claims)), 'packet claim links must remain reviewable against the claim ledger')

    no_packet = 'pass' if packets else 'fail'
    high_fail = sum(1 for r in audit if r.get('severity') == 'high' and r.get('status') != 'pass')
    add('evidence_debt_work_packet_audit_summary', 'info' if packets and not high_fail else 'high', 'pass' if packets and not high_fail else 'fail', '.', 'packets present and high failures=0', f'packets={len(packets)} high_failures={high_fail}', 'summary row for release gate')
    return packets, audit


def write_reports(root: Path, packets, audit) -> None:
    write_field_schema(root, 'SCHEMA/Evidence-Debt-Work-Packet-Fields-current.csv', PACKET_FIELDS, {
        'packet_id': 'Stable generated work-packet id.',
        'packet_rank': 'Priority ordering for manual execution.',
        'priority_band': 'Highest debt priority represented in the packet.',
        'risk_lane': 'Execution lane inherited from the evidence-debt execution queue.',
        'candidate_id': 'Candidate associated with this packet.',
        'candidate_name': 'Human-readable candidate label.',
        'debt_count': 'Number of evidence-debt rows grouped into this packet.',
        'critical_debt_count': 'Number of critical debt rows in the packet.',
        'high_debt_count': 'Number of high-priority debt rows in the packet.',
        'execution_ids': 'Execution queue ids assigned to this packet.',
        'debt_ids': 'Evidence-Debt ids assigned to this packet.',
        'claim_ids': 'Related claim ids for reviewer orientation.',
        'packet_goal': 'Concrete risk-reduction goal.',
        'first_manual_step': 'First safe manual action to take.',
        'acceptable_source_classes': 'Allowed classes of evidence/source context.',
        'blocked_extraction_modes': 'Details or behaviors that remain forbidden.',
        'acceptance_criteria': 'Conditions for marking the packet complete.',
        'completion_evidence_slot': 'Future internal ledger slot where completion evidence should be recorded.',
        'public_boundary_after_completion': 'Explicit statement that completion is not public-release permission.',
        'reviewer_role': 'Human review role required before acting on the packet.',
        'status': 'Packet execution status.',
        'note': 'Reviewer-facing note.',
    })
    write_field_schema(root, 'SCHEMA/Evidence-Debt-Work-Packet-Audit-Fields-current.csv', AUDIT_FIELDS, {
        'audit_id': 'Stable audit row id.',
        'check': 'Audit check name.',
        'severity': 'Finding severity.',
        'status': 'pass/fail status.',
        'subject_id': 'File, field, or relationship being tested.',
        'expected': 'Expected condition.',
        'observed': 'Observed condition.',
        'note': 'Reviewer-facing explanation.',
    })
    write_csv_json_md_report(
        root, 'META/Evidence-Debt-Work-Packet-current.csv', PACKET_FIELDS, packets,
        'Evidence Debt Work Packets', 'tools/evidence_debt_work_packets.py',
        columns=['packet_id','packet_rank','priority_band','risk_lane','candidate_id','debt_count','claim_ids','first_manual_step','acceptance_criteria','status'],
        intro_lines=[
            f'Work packets: {len(packets)}',
            'Groups the full critical/high evidence-debt execution queue into reviewer-sized packets with acceptance criteria and no-public-expansion boundaries.',
        ], max_md_rows=120,
    )
    write_csv_json_md_report(
        root, 'META/Evidence-Debt-Work-Packet-Audit-current.csv', AUDIT_FIELDS, audit,
        'Evidence Debt Work Packet Audit', 'tools/evidence_debt_work_packets.py',
        columns=['check','severity','status','subject_id','expected','observed','note'],
        intro_lines=[
            f'High failures: {sum(1 for r in audit if r.get("severity") == "high" and r.get("status") != "pass")}',
            'Blocks release if execution queue rows are lost, critical packets are buried, safety criteria are missing, or public/contact details leak into work packets.',
        ], max_md_rows=80,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--write-report', action='store_true')
    ap.add_argument('--fail-on-high', action='store_true')
    args = ap.parse_args()
    root = Path(args.root).resolve()
    packets, audit = run(root)
    if args.write_report:
        write_reports(root, packets, audit)
    high = [r for r in audit if r.get('severity') == 'high' and r.get('status') != 'pass']
    print(f"{'FAIL' if high else 'PASS'} evidence-debt work packets packets={len(packets)} high_fail={len(high)}")
    for r in high[:20]:
        print(f"HIGH {r.get('check')} {r.get('subject_id')}: {r.get('observed')}")
    if args.fail_on_high and high:
        sys.exit(1)


if __name__ == '__main__':
    main()
