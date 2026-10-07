#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re, sys
from pathlib import Path

FIELDS=['closure_check_id','check','severity','status','scope','detail']

def read_csv(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))

def add(rows, check, sev, status, scope, detail):
    rows.append({'closure_check_id':f'release_closure_{len(rows)+1:03d}','check':check,'severity':sev,'status':status,'scope':scope,'detail':detail})

def split_paths(s: str): return [x for x in (s or '').split('|') if x]

def exists(root: Path, rel: str) -> bool:
    if rel in {'all gates'}: return True
    if rel.endswith('/'):
        return (root/rel).is_dir()
    return (root/rel).exists()

def normalize_generated(root: Path, rel: str) -> str:
    p=Path(rel)
    if p.suffix in {'.json','.md'}:
        candidate=str(p.with_suffix('.csv')).replace('\\','/')
        if (root/candidate).exists():
            return candidate
    return rel

def run(root: Path):
    rows=[]
    gates=read_csv(root/'META/Release-Gate-Attestation-current.csv')
    if not gates:
        add(rows,'release_gate_rows_present','high','fail','META/Release-Gate-Attestation-current.csv','Release gate attestation is missing or has no rows')
        return rows
    gate_ids=[g.get('gate_id','') for g in gates]
    # Gate 032 is this closure report's own attestation gate; including it here creates a
    # bootstrap loop.  Substantive closure failures still appear as high/fail rows below
    # and are checked directly by QA and the release gate.
    fail_gates=[g.get('gate_id','') for g in gates if g.get('status')!='pass' and g.get('gate_id','')!='gate_032']
    add(rows,'release_gates_all_pass','high' if fail_gates else 'info','fail' if fail_gates else 'pass','release_gate_attestation','Failed gates excluding self gate_032: '+ '; '.join(fail_gates[:12]) if fail_gates else f'All {len(gates)} release gates pass after excluding self gate_032')
    nums=[]
    for gid in gate_ids:
        m=re.fullmatch(r'gate_(\d{3})', gid or '')
        if m: nums.append(int(m.group(1)))
    contiguous=(nums==list(range(1, max(nums)+1))) if nums else False
    add(rows,'release_gate_ids_contiguous','high' if not contiguous else 'info','fail' if not contiguous else 'pass','release_gate_attestation',f'Gate IDs observed: {gate_ids[:4]}...{gate_ids[-4:]}' if contiguous else 'Gate IDs are not contiguous from gate_001')
    missing_evidence=[]
    evidence_paths=set()
    for g in gates:
        for rel in split_paths(g.get('evidence_files','')):
            evidence_paths.add(rel)
            if not exists(root, rel): missing_evidence.append(f"{g.get('gate_id')}->{rel}")
    add(rows,'release_gate_evidence_paths_resolve','high' if missing_evidence else 'info','fail' if missing_evidence else 'pass','release_gate_attestation','Missing evidence paths: '+ '; '.join(missing_evidence[:20]) if missing_evidence else f'{len(evidence_paths)} unique evidence paths/directories resolve')
    prov_paths={r.get('artifact_path','') for r in read_csv(root/'META/Generated-Artifact-Provenance-current.csv')}
    untracked_generated=[]
    for rel in sorted(evidence_paths):
        if rel.endswith('/') or rel in {'PUBLIC/','all gates'}:
            continue
        n=normalize_generated(root, rel)
        bootstrap={'SCHEMA/Schema-Validation-Report-current.csv','META/Generated-Artifact-Provenance-current.csv','META/Release-Gate-Attestation-current.csv','META/Release-Evidence-Closure-current.csv','META/Handoff-Review-Digest-current.csv','META/Candidate-Discovery-Log-current.csv','META/Public-Claim-Quarantine-current.csv'}
        if (n.startswith('META/') or n.startswith('SCHEMA/')) and n.endswith('-current.csv') and n not in prov_paths and n not in bootstrap:
            # Schema validation, generated-artifact provenance, and release-gate attestation are bootstrap/current reports outside Generated-Artifact-Provenance to avoid cyclic self-reference.
            untracked_generated.append(rel)
    add(rows,'generated_evidence_in_provenance_or_bootstrap','high' if untracked_generated else 'info','fail' if untracked_generated else 'pass','generated_evidence','Generated-looking evidence paths absent from provenance: '+ '; '.join(untracked_generated[:20]) if untracked_generated else 'Generated evidence files are either tracked in provenance or recognized bootstrap reports')
    policy=read_csv(root/'META/Policy-Assertion-Matrix-current.csv')
    policy_gate_refs={gid for r in policy for gid in split_paths(r.get('enforced_by_gates','')) if gid.startswith('gate_')}
    missing_policy_gates=sorted(policy_gate_refs-set(gate_ids))
    add(rows,'policy_assertion_gate_refs_exist','high' if missing_policy_gates else 'info','fail' if missing_policy_gates else 'pass','policy_assertion_matrix','Missing policy gate refs: '+ '; '.join(missing_policy_gates) if missing_policy_gates else f'{len(policy_gate_refs)} policy assertion gate refs resolve')
    selfcov=read_csv(root/'META/Selftest-Coverage-Matrix-current.csv')
    self_gate_refs={r.get('gate_id','') for r in selfcov if r.get('gate_id','')}
    missing_self_gates=sorted(self_gate_refs-set(gate_ids))
    add(rows,'selftest_coverage_gate_refs_exist','high' if missing_self_gates else 'info','fail' if missing_self_gates else 'pass','selftest_coverage_matrix','Missing selftest gate refs: '+ '; '.join(missing_self_gates) if missing_self_gates else f'{len(self_gate_refs)} selftest coverage gate refs resolve')
    inventory={r.get('file_path','') for r in read_csv(root/'META/Package-File-Inventory-current.csv')}
    inventory_exempt={
        'SHA256SUMS.txt','SHA256SUMS.txt.sig','QA-REPORT-current.txt',
        'META/Package-File-Inventory-current.csv','META/Package-File-Inventory-current.json','META/Package-File-Inventory-current.md',
        'META/Generated-Artifact-Provenance-current.csv','META/Generated-Artifact-Provenance-current.json','META/Generated-Artifact-Provenance-current.md',
        'META/Release-Gate-Attestation-current.csv','META/Release-Gate-Attestation-current.json','META/Release-Gate-Attestation-current.md',
        'META/Release-Evidence-Closure-current.csv','META/Release-Evidence-Closure-current.json','META/Release-Evidence-Closure-current.md',
        'META/Handoff-Review-Digest-current.csv','META/Handoff-Review-Digest-current.json','META/Handoff-Review-Digest-current.md',
        'SCHEMA/Schema-Validation-Report-current.csv','SCHEMA/Schema-Validation-Report-current.json','SCHEMA/Schema-Validation-Report-current.md',
    }
    missing_inv=[]
    exempt_seen=[]
    for rel in sorted(evidence_paths):
        if rel.endswith('/') or rel in {'PUBLIC/','all gates'}: continue
        if rel in inventory_exempt:
            exempt_seen.append(rel)
            continue
        if rel not in inventory and (root/rel).is_file(): missing_inv.append(rel)
    detail = ('Evidence files absent from package inventory: '+ '; '.join(missing_inv[:20])) if missing_inv else ('Release evidence files are classified in package inventory or recognized as recursive/integrity-report exemptions' + (f'; exemptions={len(exempt_seen)}' if exempt_seen else ''))
    add(rows,'release_evidence_in_file_inventory','medium' if missing_inv else 'info','review' if missing_inv else 'pass','package_file_inventory', detail)
    add(rows,'release_evidence_closure','info','pass','release_closure',f'Closure audit reviewed {len(gates)} gates, {len(evidence_paths)} evidence paths, {len(policy_gate_refs)} policy gate refs, and {len(self_gate_refs)} selftest gate refs')
    return rows

def write_reports(root: Path, rows):
    out=root/'META'; out.mkdir(exist_ok=True)
    with (out/'Release-Evidence-Closure-current.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows([{k:r.get(k,'') for k in FIELDS} for r in rows])
    (out/'Release-Evidence-Closure-current.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    high=sum(1 for r in rows if r.get('severity')=='high')
    nonpass=sum(1 for r in rows if r.get('status') not in {'pass'})
    lines=['# Release Evidence Closure — current','', 'Generated by `tools/release_evidence_closure.py`.', '', f'High findings: {high}', f'Non-pass rows: {nonpass}', '', 'This report closes the loop between release gates, evidence paths, policy-assertion gate references, selftest gate references, generated-artifact provenance, and package-file inventory.', '', '| check | severity | status | scope | detail |','|---|---|---|---|---|']
    for r in rows:
        detail=(r.get('detail','') or '').replace('|','/').replace('\n',' ')
        lines.append(f"| {r['check']} | {r['severity']} | {r['status']} | {r['scope']} | {detail} |")
    (out/'Release-Evidence-Closure-current.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    high=[r for r in rows if r.get('severity')=='high']
    print(f"{'FAIL' if high else 'PASS'} release evidence closure rows={len(rows)} high={len(high)}")
    for r in high[:20]: print(f"HIGH {r['check']}: {r['detail']}")
    if args.fail_on_high and high: sys.exit(1)
if __name__=='__main__': main()
