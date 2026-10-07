#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re, sys
from pathlib import Path
sys.dont_write_bytecode = True

FIELDS=['check_id','check','artifact','expected','observed','severity','status','note']

def read_json(path: Path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return {}

def read_csv(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))

def add(rows, check, artifact, expected, observed, sev, status, note):
    rows.append({'check_id':f'msc_{len(rows)+1:04d}','check':check,'artifact':artifact,'expected':expected,'observed':observed,'severity':sev,'status':status,'note':note})

def text(path: Path) -> str:
    try: return path.read_text(encoding='utf-8')
    except Exception: return ''

def run(root: Path):
    rows=[]
    manifest=read_json(root/'manifest.json')
    pub=read_json(root/'PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json')
    contract=read_json(root/'SCHEMA/Package-Release-Contract-current.json')
    cur=manifest.get('revision','')
    slug=manifest.get('release_slug','') or manifest.get('codename','') or manifest.get('pass_type','') or ''
    # Revision/token checks on machine-readable manifests.
    expected=cur or 'current revision recorded in manifest.json'
    observed=f"manifest={manifest.get('revision','')} public={pub.get('revision','')} package={pub.get('package_revision','')} contract={contract.get('package_revision','')}"
    add(rows,'machine_revision_fields_align','manifest/public/contract',expected,observed,'high','pass' if cur and pub.get('revision')==cur and pub.get('package_revision')==cur and contract.get('package_revision')==cur else 'fail','machine-readable package-current revision fields must align')
    for rel, keys in [('manifest.json',['title','description','revision','central_sentence','notes','release_note','pass_type']),('PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json',['title','description','release_note','revision','package_revision']),('SCHEMA/Package-Release-Contract-current.json',['title','release_note','package_revision','notes'])]:
        obj=read_json(root/rel)
        blob='\n'.join(str(obj.get(k,'')) for k in keys)
        stale=sorted(set(re.findall(r'rev\d{4}', blob)) - {cur})
        add(rows,'machine_text_no_stale_revision_tokens',rel,f'only {cur}', '|'.join(stale) if stale else 'none','high','fail' if stale else 'pass','front-door machine text must not advertise an older package revision as current')
        has_cur=cur in blob
        add(rows,'machine_text_mentions_current_revision',rel,cur,'present' if has_cur else 'missing','high','pass' if has_cur else 'fail','machine text should mention the current package revision')
    # Human front-door files were the stale-prose failure class in rev0085, so test them directly.
    frontdoor=['000-START-HERE.txt','CURRENT-SPINE.md','DATA-CARD-current.md','LivingChristFigures.txt','PUBLIC/README-public-edition.md','META/Data-Card-current.md','CUBE-MAP.md']
    signals=[tok for tok in re.split(r'[_\-\s]+', slug) if tok] or [cur]
    for rel in frontdoor:
        body=text(root/rel)
        lower=body.lower()
        stale=sorted(set(re.findall(r'rev\d{4}', body)) - {cur})
        has_cur=cur in body
        has_signal=any(sig.lower() in lower for sig in signals)
        add(rows,'frontdoor_mentions_current_revision',rel,cur,'present' if has_cur else 'missing','high','pass' if has_cur else 'fail','front-door prose must carry the package-current revision')
        add(rows,'frontdoor_mentions_current_pass_shape',rel,'current pass-shape signal from manifest pass_type/release slug','present' if has_signal else 'missing','high','pass' if has_signal else 'fail','front-door prose must state the current pass shape, not only inherited historical context')
        add(rows,'frontdoor_no_stale_revision_tokens',rel,f'only {cur} in current front-door prose; history belongs in explicitly historical surfaces', '|'.join(stale[:12]) if stale else 'none','high','fail' if stale else 'pass','four-digit stale revision tokens in current front-door prose are blocking')
    refresh_rows=read_csv(root/'Refresh-Index-current.csv')
    refresh_ids='|'.join(r.get('refresh_id','') for r in refresh_rows[-8:])
    declared=(manifest.get('new_refresh_files') or [''])[0]
    expected_refresh=''
    if declared:
        for r in refresh_rows:
            if r.get('file_path','')==declared:
                expected_refresh=r.get('refresh_id','')
                break
        refresh_status='pass' if expected_refresh and any(r.get('refresh_id','')==expected_refresh for r in refresh_rows) else 'fail'
        refresh_expected=expected_refresh or declared
        refresh_note='declared refresh note must be indexed'
    else:
        refresh_status='pass'
        refresh_expected='none declared for non-refresh revision'
        refresh_note='a mission/package correction revision may explicitly declare no candidate refresh note'
    add(rows,'refresh_index_contains_current_marker','Refresh-Index-current.csv',refresh_expected,refresh_ids,'high',refresh_status,refresh_note)
    if not rows:
        add(rows,'manifest_semantic_coherence','.', 'all checks', 'none', 'info', 'pass', 'No manifest semantic checks configured')
    return rows

def write_reports(root: Path, rows):
    out=root/'META'; out.mkdir(exist_ok=True)
    with (out/'Manifest-Semantic-Coherence-Audit-current.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows([{k:r.get(k,'') for k in FIELDS} for r in rows])
    (out/'Manifest-Semantic-Coherence-Audit-current.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    high=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    lines=['# Manifest Semantic Coherence Audit — current','', 'Generated by `tools/manifest_semantic_coherence_audit.py`.', '', f'Checks: {len(rows)}', f'High findings: {len(high)}', '', 'This audit catches stale semantic metadata and front-door prose that can pass simple revision-field checks.', '', '| check | artifact | severity | status | expected | observed | note |','|---|---|---|---|---|---|---|']
    for r in rows:
        lines.append(f"| {r['check']} | {r['artifact']} | {r['severity']} | {r['status']} | {r['expected']} | {r['observed']} | {r['note']} |")
    (out/'Manifest-Semantic-Coherence-Audit-current.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-fail', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    high=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if high else 'PASS'} manifest semantic coherence rows={len(rows)} high={len(high)}")
    if args.fail_on_fail and high: sys.exit(1)
if __name__=='__main__': main()
