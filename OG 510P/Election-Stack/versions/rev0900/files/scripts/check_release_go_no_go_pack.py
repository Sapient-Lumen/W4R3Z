#!/usr/bin/env python3
"""Validate release go/no-go, source burn-down, and offline-drill outputs."""
from __future__ import annotations
import csv, json, os, re, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT/'VERSION').read_text(encoding='utf-8').strip()
REG = ROOT/'artifacts/registries/release-go-no-go-criteria.csv'
REPORTS = ROOT/'artifacts/reports'
TOOL = ROOT/'tools/release_go_no_go_pack.py'
REQUIRED_HEADER = ['criterion_id','scope','decision','requirement','current_signal','evidence_refs','gate_refs','go_condition','no_go_condition','non_claims']
REQUIRED_IDS = {f'RGN-{i:03d}' for i in range(1, 16)}
ALLOWED_DECISIONS = {'GO_SYNTHETIC_RELEASE','CONDITIONAL_REVIEW','NO_GO_LIVE_PILOT','NO_GO_CERTIFICATION','NO_GO_CURRENT_AUTHORITY','NO_GO_LEGAL_USE'}
ALLOWED_SCOPES = {'release','live_pilot','source_review','legal','certification','offline_drill','ai_controls','non_voting_tech'}
ALLOWED_REF_PREFIXES = {'DOC':'docs/','SCRIPT':'scripts/','TOOL':'tools/','REG':'artifacts/registries/','EXAMPLE':'artifacts/examples/','REPORT':'artifacts/reports/','CHECK':'artifacts/checklists/','TEMPLATE':'artifacts/templates/'}
TOKEN_RE = re.compile(r'^(?P<typ>[A-Z]+):(?P<path>.+)$')
def read_csv(path: Path) -> list[dict[str,str]]:
    with path.open('r', encoding='utf-8', newline='') as f: return [{k:(v or '').strip() for k,v in row.items()} for row in csv.DictReader(f)]
def load_json(path: Path): return json.loads(path.read_text(encoding='utf-8'))
def toks(cell: str):
    for raw in (cell or '').split(';'):
        tok=raw.strip()
        if tok: yield tok
def validate_registry() -> list[str]:
    errors=[]
    if not REG.exists(): return ['missing artifacts/registries/release-go-no-go-criteria.csv']
    rows_raw=list(csv.reader(REG.open(encoding='utf-8', newline='')))
    if not rows_raw: return ['release-go-no-go-criteria.csv is empty']
    if [h.strip() for h in rows_raw[0]] != REQUIRED_HEADER: errors.append('header mismatch')
    seen=set(); decisions=set()
    for n,row in enumerate(read_csv(REG), start=2):
        cid=row.get('criterion_id','')
        if not re.fullmatch(r'RGN-\d{3}', cid): errors.append(f'L{n}: invalid criterion_id {cid!r}'); continue
        if cid in seen: errors.append(f'L{n}: duplicate criterion_id {cid}')
        seen.add(cid); decisions.add(row.get('decision',''))
        if row.get('scope','') not in ALLOWED_SCOPES: errors.append(f'L{n}: {cid} invalid scope {row.get("scope")!r}')
        if row.get('decision','') not in ALLOWED_DECISIONS: errors.append(f'L{n}: {cid} invalid decision {row.get("decision")!r}')
        for field in REQUIRED_HEADER[3:]:
            if not row.get(field): errors.append(f'L{n}: {cid} missing {field}')
        for field in ['evidence_refs','gate_refs']:
            for tok in toks(row.get(field,'')):
                m=TOKEN_RE.match(tok)
                if not m: errors.append(f'L{n}: {cid} unparseable ref token {tok!r}'); continue
                typ=m.group('typ'); rel=m.group('path'); pref=ALLOWED_REF_PREFIXES.get(typ)
                if not pref: errors.append(f'L{n}: {cid} unknown ref type {typ!r}'); continue
                if not rel.startswith(pref): errors.append(f'L{n}: {cid} {typ} ref must start with {pref!r}: {rel!r}'); continue
                if not (ROOT/rel).exists(): errors.append(f'L{n}: {cid} missing referenced file: {rel}')
        if 'not' not in (row.get('non_claims') or '').lower(): errors.append(f'L{n}: {cid} non_claims must explicitly state non-claims')
    miss=sorted(REQUIRED_IDS-seen)
    if miss: errors.append('missing required criterion ids: '+', '.join(miss))
    for req in ['GO_SYNTHETIC_RELEASE','NO_GO_LIVE_PILOT','NO_GO_CERTIFICATION','NO_GO_CURRENT_AUTHORITY','NO_GO_LEGAL_USE']:
        if req not in decisions: errors.append(f'release-go-no-go-criteria.csv missing decision {req}')
    return errors
def main() -> int:
    errors=[]
    for name in ['release-go-no-go-decision.json','release-go-no-go-decision.md','source-review-burndown-plan.json','source-review-burndown-plan.csv','offline-verification-drill-plan.md']:
        if not (REPORTS/name).exists(): errors.append(f'missing artifacts/reports/{name}')
    if errors:
        [print('ERROR:',e,file=sys.stderr) for e in errors]; return 2
    errors += validate_registry()
    decision=load_json(REPORTS/'release-go-no-go-decision.json'); source=load_json(REPORTS/'source-review-burndown-plan.json')
    report_release_date = str(decision.get('release_date') or '').strip()
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', report_release_date):
        errors.append('release-go-no-go-decision.json missing ISO release_date')
        report_release_date = ''
    if report_release_date and str(source.get('release_date') or '').strip() != report_release_date:
        errors.append('source-review-burndown-plan release_date does not match decision release_date')
    env = os.environ.copy()
    if report_release_date:
        env['ELECTION_STACK_RELEASE_DATE'] = report_release_date
    proc=subprocess.run([sys.executable, str(TOOL), '--json'], cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    if proc.returncode != 0:
        print('ERROR: tools/release_go_no_go_pack.py --json failed', file=sys.stderr); sys.stderr.write(proc.stdout); sys.stderr.write(proc.stderr); return 2
    try: gen=json.loads(proc.stdout)
    except Exception as exc: print(f'ERROR: generated go/no-go JSON parse failed: {exc}', file=sys.stderr); return 2
    if decision != gen.get('decision'): errors.append('release-go-no-go-decision.json is stale; run tools/release_go_no_go_pack.py --write')
    if source != gen.get('source_burndown'): errors.append('source-review-burndown-plan.json is stale; run tools/release_go_no_go_pack.py --write')
    if decision.get('archive_version') != VERSION: errors.append('go/no-go decision archive_version does not match VERSION')
    if decision.get('synthetic_only') is not True or decision.get('no_live_deployment_claim') is not True: errors.append('go/no-go decision missing synthetic/live-evidence boundary flags')
    if decision.get('topline_decision') != 'GO_SYNTHETIC_RELEASE_ONLY': errors.append('go/no-go topline must be GO_SYNTHETIC_RELEASE_ONLY')
    if not str(decision.get('live_pilot_decision') or '').startswith('NO_GO_LIVE_PILOT'): errors.append('live pilot decision must remain NO_GO')
    if not str(decision.get('certification_decision') or '').startswith('NO_GO_CERTIFICATION'): errors.append('certification decision must remain NO_GO')
    if not str(decision.get('current_authority_decision') or '').startswith('NO_GO_CURRENT_AUTHORITY'): errors.append('current-authority decision must remain NO_GO')
    sig = decision.get('current_signals') or {}
    if sig.get('mission_kernel_full_drill_decision') != 'DRILL_COMPLETE_NOT_LIVE_READY': errors.append('go/no-go full drill decision must remain DRILL_COMPLETE_NOT_LIVE_READY')
    if int(sig.get('mission_kernel_full_drill_valid_drill_object_count', -1)) != int(sig.get('mission_kernel_full_drill_required_evidence_class_count', -2)): errors.append('go/no-go full drill must validate every required drill evidence object')
    if int(sig.get('mission_kernel_full_drill_complete_item_count', -1)) != int(sig.get('mission_kernel_full_drill_work_item_count', -2)): errors.append('go/no-go full drill must complete all work items in drill mode')
    if int(sig.get('mission_kernel_full_drill_live_object_count', -1)) != 0: errors.append('go/no-go full drill live object count must remain zero')
    if int(sig.get('mission_kernel_full_drill_leak_count', -1)) != 0 or int(sig.get('mission_kernel_full_drill_overclaim_count', -1)) != 0: errors.append('go/no-go full drill must have zero leak and overclaim counts')
    if sig.get('cdf_export_replay_decision') != 'SYNTHETIC_CDF_REPLAY_PASS_NOT_CONFORMANCE': errors.append('go/no-go CDF replay decision must remain synthetic pass / not conformance')
    if int(sig.get('cdf_export_replay_error_count', -1)) != 0: errors.append('go/no-go CDF replay must report zero default errors')
    if sig.get('cdf_export_replay_no_full_nist_conformance_claim') is not True: errors.append('go/no-go CDF replay must preserve no-full-NIST-conformance flag')
    if sig.get('cdf_independent_replay_decision') != 'INDEPENDENT_SYNTHETIC_CDF_REPLAY_AGREES_NOT_CONFORMANCE': errors.append('go/no-go independent CDF replay decision must remain synthetic agreement / not conformance')
    if int(sig.get('cdf_independent_replay_error_count', -1)) != 0: errors.append('go/no-go independent CDF replay must report zero default errors')
    if sig.get('cdf_independent_replay_no_full_nist_conformance_claim') is not True: errors.append('go/no-go independent CDF replay must preserve no-full-NIST-conformance flag')
    if sig.get('cdf_independent_replay_primary_agrees') is not True or sig.get('cdf_independent_replay_cro_agrees') is not True: errors.append('go/no-go independent CDF replay must agree with primary report and CRO')
    if sig.get('ballot_accounting_reconciliation_decision') != 'SYNTHETIC_BALLOT_ACCOUNTING_RECONCILIATION_PASS_NOT_CUSTODY_EVIDENCE': errors.append('go/no-go ballot-accounting reconciliation decision must remain synthetic pass / not custody evidence')
    if int(sig.get('ballot_accounting_reconciliation_error_count', -1)) != 0: errors.append('go/no-go ballot-accounting reconciliation must report zero default errors')
    if sig.get('ballot_accounting_reconciliation_no_live_custody_claim') is not True: errors.append('go/no-go ballot-accounting reconciliation must preserve no-live-custody flag')
    if sig.get('event_log_reconciliation_decision') != 'SYNTHETIC_EVENT_LOG_CHAIN_PASS_NOT_LIVE_EEL': errors.append('go/no-go event-log reconciliation decision must remain synthetic pass / not live EEL evidence')
    if int(sig.get('event_log_reconciliation_error_count', -1)) != 0: errors.append('go/no-go event-log reconciliation must report zero default errors')
    if int(sig.get('event_log_reconciliation_missing_required_role_count', -1)) != 0: errors.append('go/no-go event-log reconciliation must have zero missing required roles')
    if sig.get('event_log_reconciliation_no_live_eel_claim') is not True: errors.append('go/no-go event-log reconciliation must preserve no-live-EEL flag')
    if source.get('archive_version') != VERSION: errors.append('source-review-burndown-plan archive_version does not match VERSION')
    if 'expired_review_count' not in source or int(source.get('expired_review_count')) != 0: errors.append('source-review-burndown-plan has expired source reviews')
    if 'missing_review_by_count' not in source or int(source.get('missing_review_by_count')) != 0: errors.append('source-review-burndown-plan has missing review_by rows')
    if 'due_within_30_days_count' not in source: errors.append('source-review-burndown-plan missing due_within_30_days_count')
    elif int(source.get('due_within_30_days_count') or 0) < 0: errors.append('source-review-burndown-plan due_within_30_days_count cannot be negative')
    rows=read_csv(REPORTS/'source-review-burndown-plan.csv'); lanes={r.get('lane_id') for r in rows}
    for lane in ['SRB-001','SRB-003','SRB-005','SRB-006','SRB-011']:
        if lane not in lanes: errors.append(f'source-review-burndown-plan.csv missing lane {lane}')
    if not all((r.get('non_claims') or '') for r in rows): errors.append('source-review-burndown rows must carry non_claims')
    md=(REPORTS/'release-go-no-go-decision.md').read_text(encoding='utf-8', errors='replace').lower()
    for phrase in ['synthetic-only','not live election evidence','not certification','no-go','not legal advice','full mission-kernel non-production drill replay']:
        if phrase not in md: errors.append(f'release-go-no-go-decision.md missing boundary phrase {phrase!r}')
    if 'certifies' in md or 'proves fraud' in md: errors.append('release-go-no-go-decision.md contains prohibited certification/fraud inference language')
    off_raw=(REPORTS/'offline-verification-drill-plan.md').read_text(encoding='utf-8', errors='replace')
    off=off_raw.lower()
    for phrase in ['verify_release_zip.py','extract_release_zip.py','verify_manifest.py','release_go_no_go_pack.py','check_mission_kernel_full_drill_replay.py','check_cdf_export_replay.py','check_cdf_independent_replay_verifier.py','check_ballot_accounting_reconciler.py','check_election_event_log_reconciler.py','not live election evidence']:
        if phrase not in off: errors.append(f'offline-verification-drill-plan.md missing phrase {phrase!r}')
    expected_release_prefix = f"The-Election-Stack-rev{int(VERSION.removeprefix('v')):04d}-"
    if expected_release_prefix not in off_raw:
        errors.append(f'offline-verification-drill-plan.md must use the current revision filename prefix {expected_release_prefix!r}')
    stale_release_refs = sorted(set(re.findall(r'The-Election-Stack-rev(?!' + re.escape(f"{int(VERSION.removeprefix('v')):04d}") + r')\d{4}-[^\s`]+\.zip', off_raw)))
    if stale_release_refs:
        errors.append('offline-verification-drill-plan.md contains stale release ZIP examples: ' + ', '.join(stale_release_refs[:5]))
    if 'truststatussnaprevocationgate.zip' in off:
        errors.append('offline-verification-drill-plan.md still contains the old rev0846 codename example')
    if errors:
        [print('ERROR:',e,file=sys.stderr) for e in errors]; return 2
    print(f"PASS: release go/no-go pack ({VERSION}, due30={source['due_within_30_days_count']})")
    return 0
if __name__ == '__main__': raise SystemExit(main())
