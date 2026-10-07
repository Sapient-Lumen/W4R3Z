#!/usr/bin/env python3
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

sys.dont_write_bytecode = True
from lib_cube import read_csv_rows, write_csv_json_md_report

WORK_ORDER_FIELDS = [
    'work_order_id','work_order_rank','packet_id','packet_rank','priority_band','risk_lane',
    'candidate_id','candidate_name','critical_debt_count','high_debt_count','execution_ids','debt_ids','claim_ids',
    'work_order_type','work_goal','first_30_minute_action','evidence_to_seek','stop_if_found','do_not_do',
    'completion_evidence_target','handoff_note','status'
]
TRACE_FIELDS = [
    'trace_id','execution_id','work_order_id','packet_id','packet_rank','debt_id','debt_priority','risk_lane',
    'candidate_id','candidate_name','claim_ids','queue_execution_order','queue_action','packet_completion_slot',
    'trace_status','note'
]
AUDIT_FIELDS = ['audit_id','check','severity','status','subject_id','expected','observed','note']

URL_RE = re.compile(r'https?://|www\.', re.I)
EMAIL_RE = re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', re.I)
# Only treat long, phone-shaped strings as leakage; IDs like claim_0250 are not matched.
PHONE_RE = re.compile(r'(?<![\w_])(?:\+?\d[\d\s().-]{7,}\d)(?![\w_])')


def split_pipe(value: str) -> list[str]:
    out = []
    for part in (value or '').split('|'):
        part = part.strip()
        if part and part not in out:
            out.append(part)
    return out


def compact(values: list[str], limit: int = 4) -> str:
    out=[]
    for value in values:
        value=(value or '').strip()
        if value and value not in out:
            out.append(value)
    if not out:
        return ''
    if len(out) <= limit:
        return ' | '.join(out)
    return ' | '.join(out[:limit]) + f' | … {len(out)-limit} more; see packet/queue trace rows'


def classify_order_type(packet: dict[str,str]) -> str:
    if packet.get('priority_band') == 'critical':
        return 'critical_manual_first_blocker'
    if packet.get('risk_lane') == 'lane_1_high_sensitive_boundary':
        return 'sensitive_boundary_manual_review'
    return 'source_balance_or_claim_support_review'


def goal_for(packet: dict[str,str]) -> str:
    if packet.get('priority_band') == 'critical':
        return 'Close or re-quarantine the critical blocker before any public wording/source expansion is considered.'
    if packet.get('risk_lane') == 'lane_1_high_sensitive_boundary':
        return 'Make a bounded manual decision on sensitive evidence debt, preserving no-public-expansion and no-contact-route posture.'
    return 'Resolve source-balance or claim-support debt enough to choose support, continued queue, or re-quarantine.'


def first_action(packet: dict[str,str]) -> str:
    raw = packet.get('first_manual_step') or packet.get('acceptable_source_classes') or ''
    if raw.strip():
        return 'Open the listed debt/claim rows, then seek only high-level, non-operational sources in this source class: ' + raw.strip()
    return 'Open the listed debt/claim rows and record whether the packet requires support, continued queue, or re-quarantine.'


def evidence_to_seek(packet: dict[str,str]) -> str:
    base = packet.get('acceptable_source_classes') or ''
    if base.strip():
        return base.strip()
    return 'High-level policy, audit, annual-report, governance, or carefully sourced independent reporting; no contact paths or live-service checks.'


def stop_condition(packet: dict[str,str]) -> str:
    if packet.get('priority_band') == 'critical':
        return 'Stop after one bounded finding: verified high-level support, explicit no-update reason, or strengthened quarantine decision.'
    if packet.get('risk_lane') == 'lane_1_high_sensitive_boundary':
        return 'Stop when source class, affected claims, boundary decision, and forbidden details reviewed are recorded.'
    return 'Stop when the reviewer can record source-support outcome and remaining debt status without public wording changes.'


def do_not_do(packet: dict[str,str]) -> str:
    raw = packet.get('blocked_extraction_modes') or ''
    baseline = 'No public URLs, contacts, routes, referrals, service-capacity checks, case/client details, person-level story extraction, images, testimony, legal guidance, or medical guidance.'
    return (raw.strip() + ' | ' + baseline) if raw.strip() else baseline


def write_field_schema(root: Path, rel: str, fields: list[str], meanings: dict[str,str]) -> None:
    rows=[]
    for field in fields:
        rows.append({
            'field': field,
            'required': 'yes',
            'allowed_values_or_pattern': 'nonempty text' if field not in {'claim_ids'} else 'pipe-separated claim_id values; may be blank only when no claim mapping exists',
            'meaning': meanings.get(field, field),
        })
    write_csv_json_md_report(
        root, rel, ['field','required','allowed_values_or_pattern','meaning'], rows,
        Path(rel).name[:-4].replace('-', ' '), 'tools/evidence_debt_critical_path_work_order.py',
        columns=['field','required','allowed_values_or_pattern','meaning'], max_md_rows=120,
    )


def run(root: Path):
    packets = read_csv_rows(root / 'META/Evidence-Debt-Work-Packet-current.csv')
    queue = read_csv_rows(root / 'META/Evidence-Debt-Execution-Queue-current.csv')
    debts = {r.get('debt_id',''): r for r in read_csv_rows(root / 'Evidence-Debt-current.csv')}
    packet_by_exec = {}
    for packet in packets:
        for eid in split_pipe(packet.get('execution_ids','')):
            packet_by_exec.setdefault(eid, []).append(packet)

    work_orders=[]
    for idx, packet in enumerate(sorted(packets, key=lambda p: int(p.get('packet_rank') or '999999')), start=1):
        work_orders.append({
            'work_order_id': f'work_order_{idx:04d}',
            'work_order_rank': str(idx),
            'packet_id': packet.get('packet_id',''),
            'packet_rank': packet.get('packet_rank',''),
            'priority_band': packet.get('priority_band',''),
            'risk_lane': packet.get('risk_lane',''),
            'candidate_id': packet.get('candidate_id',''),
            'candidate_name': packet.get('candidate_name',''),
            'critical_debt_count': packet.get('critical_debt_count',''),
            'high_debt_count': packet.get('high_debt_count',''),
            'execution_ids': packet.get('execution_ids',''),
            'debt_ids': packet.get('debt_ids',''),
            'claim_ids': packet.get('claim_ids',''),
            'work_order_type': classify_order_type(packet),
            'work_goal': goal_for(packet),
            'first_30_minute_action': first_action(packet),
            'evidence_to_seek': evidence_to_seek(packet),
            'stop_if_found': stop_condition(packet),
            'do_not_do': do_not_do(packet),
            'completion_evidence_target': packet.get('completion_evidence_slot',''),
            'handoff_note': 'Record completion only in the future manual completion ledger; this work order is not public-release permission.',
            'status': 'ready_for_manual_execution',
        })

    order_by_packet = {row['packet_id']: row for row in work_orders}
    trace=[]
    for q in sorted(queue, key=lambda r: int(r.get('execution_order') or '999999')):
        eid=q.get('execution_id','')
        packet_list=packet_by_exec.get(eid, [])
        packet=packet_list[0] if packet_list else {}
        order=order_by_packet.get(packet.get('packet_id',''), {})
        debt=debts.get(q.get('debt_id',''), {})
        trace.append({
            'trace_id': f'work_trace_{len(trace)+1:04d}',
            'execution_id': eid,
            'work_order_id': order.get('work_order_id',''),
            'packet_id': packet.get('packet_id',''),
            'packet_rank': packet.get('packet_rank',''),
            'debt_id': q.get('debt_id',''),
            'debt_priority': debt.get('priority') or q.get('priority',''),
            'risk_lane': q.get('risk_lane',''),
            'candidate_id': q.get('candidate_id',''),
            'candidate_name': q.get('candidate_name',''),
            'claim_ids': q.get('target_claim_ids',''),
            'queue_execution_order': q.get('execution_order',''),
            'queue_action': q.get('next_concrete_action',''),
            'packet_completion_slot': packet.get('completion_evidence_slot',''),
            'trace_status': 'pass' if len(packet_list)==1 and order else 'fail',
            'note': 'Each execution queue row must map to exactly one packet and one work order; trace is internal execution evidence only.',
        })

    audit=[]
    def add(check, severity, status, subject, expected, observed, note):
        audit.append({
            'audit_id': f'critical_path_audit_{len(audit)+1:04d}',
            'check': check,
            'severity': severity,
            'status': status,
            'subject_id': subject,
            'expected': expected,
            'observed': observed,
            'note': note,
        })

    packet_ids=[p.get('packet_id','') for p in packets if p.get('packet_id')]
    order_packet_ids=[o.get('packet_id','') for o in work_orders if o.get('packet_id')]
    missing_packets=sorted(set(packet_ids)-set(order_packet_ids))
    extra_packets=sorted(set(order_packet_ids)-set(packet_ids))
    dup_order_packets=sorted({pid for pid in order_packet_ids if order_packet_ids.count(pid)>1})
    add('all_packets_have_one_work_order', 'high' if missing_packets or extra_packets or dup_order_packets else 'info', 'fail' if missing_packets or extra_packets or dup_order_packets else 'pass', 'META/Evidence-Debt-Work-Packet-current.csv', 'each packet maps to exactly one work order', f'missing={len(missing_packets)} extra={len(extra_packets)} duplicate={len(dup_order_packets)}', 'work orders must not lose or duplicate packet execution units')

    queue_exec_ids=[q.get('execution_id','') for q in queue if q.get('execution_id')]
    trace_exec_ids=[t.get('execution_id','') for t in trace if t.get('execution_id')]
    missing_exec=sorted(set(queue_exec_ids)-set(trace_exec_ids))
    extra_exec=sorted(set(trace_exec_ids)-set(queue_exec_ids))
    dup_trace=sorted({eid for eid in trace_exec_ids if trace_exec_ids.count(eid)>1})
    trace_fail=[t.get('execution_id','') for t in trace if t.get('trace_status')!='pass']
    add('all_execution_rows_trace_to_work_order', 'high' if missing_exec or extra_exec or dup_trace or trace_fail else 'info', 'fail' if missing_exec or extra_exec or dup_trace or trace_fail else 'pass', 'META/Evidence-Debt-Execution-Queue-current.csv', 'each execution row maps to one packet and one work order', f'missing={len(missing_exec)} extra={len(extra_exec)} duplicate={len(dup_trace)} trace_fail={len(trace_fail)}', 'queue rows must be actionable from the work-order layer without ad hoc reconstruction')

    crit_orders=[o for o in work_orders if o.get('priority_band')=='critical']
    crit_late=[o.get('work_order_id') for o in crit_orders if int(o.get('work_order_rank','999999')) > max(1, len(crit_orders))]
    critical_debts=[q for q in queue if q.get('priority')=='critical']
    add('critical_debt_first_ordering', 'high' if critical_debts and (not crit_orders or crit_late) else 'info', 'fail' if critical_debts and (not crit_orders or crit_late) else 'pass', 'priority=critical', 'critical work orders must be ranked first', f'critical_debts={len(critical_debts)} critical_orders={len(crit_orders)} late={len(crit_late)}', 'critical blockers must be acted on before high-priority refinement work')

    missing_core=[]
    for o in work_orders:
        for field in ['work_goal','first_30_minute_action','evidence_to_seek','stop_if_found','do_not_do','completion_evidence_target','handoff_note']:
            if not (o.get(field) or '').strip():
                missing_core.append(o.get('work_order_id','')+':'+field)
    add('actionable_fields_present', 'high' if missing_core else 'info', 'fail' if missing_core else 'pass', 'META/Evidence-Debt-Critical-Path-Work-Order-current.csv', 'all work orders carry action, evidence, stop, boundary, and completion fields', f'missing_fields={len(missing_core)}', 'manual execution must not rely on reviewer memory or whole-cube reconstruction')

    bad_completion=[o.get('work_order_id','') for o in work_orders if not o.get('completion_evidence_target','').startswith('META/Evidence-Debt-Manual-Completion-Ledger-future.csv::')]
    add('completion_targets_stay_future_manual_ledger', 'high' if bad_completion else 'info', 'fail' if bad_completion else 'pass', 'completion_evidence_target', 'future manual completion ledger only', f'bad_targets={len(bad_completion)}', 'completion slots must not imply automatic package mutation or public release')

    leakage=[]
    leak_fields=['work_goal','first_30_minute_action','evidence_to_seek','stop_if_found','do_not_do','handoff_note','queue_action']
    for row in work_orders + trace:
        rid=row.get('work_order_id') or row.get('trace_id')
        for field in leak_fields:
            text=row.get(field,'')
            if URL_RE.search(text) or EMAIL_RE.search(text) or PHONE_RE.search(text):
                leakage.append(rid+':'+field)
    add('no_url_email_or_phone_like_leakage', 'high' if leakage else 'info', 'fail' if leakage else 'pass', 'work_order_and_trace_text', 'no URLs, emails, or phone-like details in execution surfaces', f'leakage={len(leakage)}', 'actionable work surfaces must remain non-operational and non-contact-bearing')

    boundary_bad=[o.get('work_order_id','') for o in work_orders if 'public' not in (o.get('do_not_do','')+o.get('handoff_note','')).lower() or 'permission' not in o.get('handoff_note','').lower()]
    add('no_public_expansion_boundary_explicit', 'high' if boundary_bad else 'info', 'fail' if boundary_bad else 'pass', 'work_order_boundary_text', 'each work order has explicit no-public-permission boundary', f'boundary_missing={len(boundary_bad)}', 'manual execution cannot be confused with public publication or referral permission')

    order_mismatch=[o.get('work_order_id','') for o in work_orders if o.get('work_order_rank') != o.get('packet_rank')]
    add('work_order_rank_matches_packet_rank', 'high' if order_mismatch else 'info', 'fail' if order_mismatch else 'pass', 'packet_rank', 'work order order follows packet order exactly', f'mismatch={len(order_mismatch)}', 'ordering refactor must not silently reorder packets outside the audited packet ranking')

    return work_orders, trace, audit


def write_reports(root: Path, work_orders, trace, audit):
    write_field_schema(root, 'SCHEMA/Evidence-Debt-Critical-Path-Work-Order-Fields-current.csv', WORK_ORDER_FIELDS, {
        'work_order_id': 'stable work-order identifier',
        'work_order_rank': 'manual execution rank; follows packet rank',
        'packet_id': 'source evidence-debt work packet',
        'work_goal': 'bounded objective for this manual packet',
        'first_30_minute_action': 'initial action for a reviewer without needing to scan the whole cube',
        'evidence_to_seek': 'allowed high-level source classes only',
        'stop_if_found': 'stop condition to prevent over-collection',
        'do_not_do': 'blocked extraction modes and safety boundary',
        'completion_evidence_target': 'future manual completion ledger slot',
        'handoff_note': 'explicit non-public-release boundary',
    })
    write_field_schema(root, 'SCHEMA/Evidence-Debt-Work-Packet-Trace-Fields-current.csv', TRACE_FIELDS, {
        'trace_id': 'stable trace row identifier',
        'execution_id': 'source execution-queue row',
        'work_order_id': 'work order that makes the execution row actionable',
        'packet_id': 'work packet containing the execution row',
        'trace_status': 'pass only when queue row maps to exactly one packet and one work order',
    })
    write_field_schema(root, 'SCHEMA/Evidence-Debt-Critical-Path-Audit-Fields-current.csv', AUDIT_FIELDS, {
        'audit_id': 'stable audit identifier',
        'check': 'audit check name',
        'severity': 'high when release-blocking if failed; info otherwise',
        'status': 'pass or fail',
        'observed': 'observed count or mismatch summary',
    })
    write_csv_json_md_report(
        root, 'META/Evidence-Debt-Critical-Path-Work-Order-current.csv', WORK_ORDER_FIELDS, work_orders,
        'Evidence Debt Critical Path Work Order', 'tools/evidence_debt_critical_path_work_order.py',
        columns=['work_order_id','work_order_rank','packet_id','priority_band','risk_lane','candidate_id','work_order_type','status'], max_md_rows=100,
        intro_lines=['Manual execution driver for the critical/high evidence-debt packet layer. It is not public-release permission.'],
    )
    write_csv_json_md_report(
        root, 'META/Evidence-Debt-Work-Packet-Trace-current.csv', TRACE_FIELDS, trace,
        'Evidence Debt Work Packet Trace', 'tools/evidence_debt_critical_path_work_order.py',
        columns=['trace_id','execution_id','work_order_id','packet_id','debt_id','debt_priority','trace_status'], max_md_rows=160,
        intro_lines=['Traceability bridge from every execution-queue row to a packet and work order.'],
    )
    write_csv_json_md_report(
        root, 'META/Evidence-Debt-Critical-Path-Audit-current.csv', AUDIT_FIELDS, audit,
        'Evidence Debt Critical Path Audit', 'tools/evidence_debt_critical_path_work_order.py',
        columns=['audit_id','check','severity','status','observed','note'], max_md_rows=80,
        intro_lines=['Release-blocking audit for work-order coverage, traceability, critical-first order, and non-operational boundary.'],
    )


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-fail', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve()
    work_orders, trace, audit = run(root)
    if args.write_report:
        write_reports(root, work_orders, trace, audit)
    bad=[r for r in audit if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if bad else 'PASS'} evidence debt critical-path work order rows={len(work_orders)} trace_rows={len(trace)} audit_rows={len(audit)} high_failures={len(bad)}")
    if args.fail_on_fail and bad:
        for r in bad:
            print('FAIL', r)
        sys.exit(1)
if __name__ == '__main__':
    main()
