#!/usr/bin/env python3
from __future__ import annotations
import contextlib, csv, io, runpy, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TOOLS=['tools/validate_nuclear_emergency_bvps_inert_fixture_policy_rev0364.py', 'tools/validate_nuclear_emergency_bvps_evidence_intake_contract_light_rev0370.py', 'tools/validate_nuclear_emergency_bvps_proofcut_status_light_rev0370.py', 'tools/validate_nuclear_emergency_bvps_ans_transition_gate_rev0368.py', 'tools/validate_nuclear_emergency_bvps_eof_ler_watch_rev0368.py', 'tools/validate_nuclear_emergency_bvps_closure_blocker_board_rev0368.py', 'tools/validate_nuclear_emergency_bvps_deadline_clock_rev0369.py', 'tools/validate_nuclear_emergency_bvps_records_templates_rev0369.py', 'tools/validate_nuclear_emergency_bvps_gap_to_request_map_rev0369.py', 'tools/validate_nuclear_emergency_bvps_proofchains_rev0369.py', 'tools/validate_nuclear_emergency_bvps_submission_packet_rev0370.py', 'tools/validate_nuclear_emergency_bvps_lockbox_rev0370.py', 'tools/validate_nuclear_emergency_bvps_route_verification_rev0370.py', 'tools/validate_nuclear_emergency_bvps_response_adjudication_rev0370.py', 'tools/validate_bvps_hotpath_artifacts_rev0370.py']
rows=[]; failures=[]
for i,rel in enumerate(TOOLS,1):
    start=time.time(); stdout=io.StringIO(); stderr=io.StringIO(); code=0
    print(f'START {i} {rel}', flush=True)
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            runpy.run_path(str(ROOT/rel), run_name='__main__')
    except SystemExit as exc:
        code=int(exc.code or 0) if isinstance(exc.code,int) else 1
    except Exception as exc:
        code=1; stderr.write(repr(exc))
    out=stdout.getvalue().strip(); err=stderr.getvalue().strip()
    tail=out.splitlines()[-1] if out else ''
    status='executed_pass' if code==0 else 'executed_fail'
    print(f'{rel}: exit={code} {tail}', flush=True)
    rows.append({'validator_id':f'VS-0370-{i:03d}','tool_path':rel,'status':status,'seconds':str(round(time.time()-start,3)),'stdout_tail':out[-500:],'stderr_tail':err[-500:]})
    if code!=0: failures.append(rel)
out_path=ROOT/'cube/bvps-current-risk-validator-audit-rev0370.csv'
with out_path.open('w', newline='', encoding='utf-8') as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
if failures:
    print('FAIL validator_sweep_rev0370 failures='+','.join(failures)); sys.exit(1)
print('PASS validator_sweep_rev0370 executed_passes='+str(len(TOOLS)))
