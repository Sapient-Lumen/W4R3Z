#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re, sys
from pathlib import Path

FIELDS=['reference_check_id','file','check','severity','status','observed','detail']
ALLOWED_BASELINE_PREFIXES=('META/Previous-Release-Fingerprint-current.json','META/Previous-Release-Fingerprint-current.md','META/Package-Delta-Manifest-current.csv','META/Package-Delta-Manifest-current.json','META/Package-Delta-Manifest-current.md','META/Version-Lineage-Audit-current.csv','META/Version-Lineage-Audit-current.json','META/Version-Lineage-Audit-current.md','META/Cross-Report-Reference-Audit-current.csv','META/Cross-Report-Reference-Audit-current.json','META/Cross-Report-Reference-Audit-current.md','META/Archive-Member-Manifest-current.csv','META/Archive-Member-Manifest-current.json','META/Archive-Member-Manifest-current.md','META/Current-Surface-Freshness-Audit-current.csv','META/Current-Surface-Freshness-Audit-current.json','META/Current-Surface-Freshness-Audit-current.md','META/Current-Pointer-Coherence-Audit-current.csv','META/Current-Pointer-Coherence-Audit-current.json','META/Current-Pointer-Coherence-Audit-current.md','META/Handoff-Review-Digest-current.csv','META/Handoff-Review-Digest-current.json','META/Handoff-Review-Digest-current.md','META/Manifest-Semantic-Coherence-Audit-current.csv','META/Manifest-Semantic-Coherence-Audit-current.json','META/Manifest-Semantic-Coherence-Audit-current.md','META/Package-Identity-Audit-current.csv','META/Package-Identity-Audit-current.json','META/Package-Identity-Audit-current.md','META/Preservation-Transfer-Readiness-current.csv','META/Preservation-Transfer-Readiness-current.json','META/Preservation-Transfer-Readiness-current.md','META/Public-Export-Surface-Audit-current.csv','META/Public-Export-Surface-Audit-current.json','META/Public-Export-Surface-Audit-current.md','META/Release-Change-Review-current.csv','META/Release-Change-Review-current.json','META/Release-Change-Review-current.md')
FRONT_DOOR=['000-START-HERE.txt','CURRENT-SPINE.md','CUBE-MAP.md','PUBLIC/README-public-edition.md','PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json','PUBLIC/PUBLIC-BUNDLE-MANIFEST-current.json','SCHEMA/Package-Release-Contract-current.json','SCHEMA/README-schema-current.md','tools/README.md','manifest.json']

def read_json(path: Path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return {}

def add(rows, rel, check, sev, ok, observed, detail):
    rows.append({'reference_check_id':f'ref_{len(rows)+1:04d}','file':rel,'check':check,'severity':sev if not ok else 'info','status':'pass' if ok else 'fail','observed':observed,'detail':detail})

def text_files(root: Path):
    exts={'.txt','.md','.csv','.json'}
    for p in sorted(root.rglob('*')):
        if not p.is_file() or p.suffix.lower() not in exts: continue
        rel=str(p.relative_to(root)).replace('\\','/')
        if rel=='SHA256SUMS.txt': continue
        yield rel,p

def run(root: Path):
    rows=[]
    m=read_json(root/'manifest.json'); prev=read_json(root/'META/Previous-Release-Fingerprint-current.json')
    rev=m.get('revision',''); prev_rev=prev.get('baseline_revision',''); export=m.get('export_name_without_zip',''); prev_export=prev.get('baseline_export_name_without_zip','')
    current_patterns=[re.compile(rf'CURRENT REVISION:\s*{re.escape(prev_rev)}',re.I), re.compile(rf'current\s+{re.escape(prev_rev)}',re.I), re.compile(rf'current revision[^\n]{{0,40}}{re.escape(prev_rev)}',re.I), re.compile(rf'"package_revision"\s*:\s*"{re.escape(prev_rev)}"'), re.compile(rf'"revision_updated"\s*:\s*"{re.escape(prev_rev)}"')]
    for rel in FRONT_DOOR:
        p=root/rel
        if not p.exists():
            add(rows, rel, 'front_door_file_present','high',False,'missing','front-door/current-reference surface is missing')
            continue
        text=p.read_text(encoding='utf-8', errors='replace')
        bad=[]
        for pat in current_patterns:
            if pat.search(text): bad.append(pat.pattern)
        if prev_export and prev_export in text and rel not in {'manifest.json'}:
            bad.append('previous export name appears in front-door current surface')
        add(rows, rel, 'front_door_not_stale_previous_current','high',not bad,'; '.join(bad[:6]),'front-door current surfaces must not identify previous revision/export as current')
    generated_current=[]
    for rel,p in text_files(root):
        if not (rel.startswith('META/') or rel.startswith('SCHEMA/') or rel.startswith('PUBLIC/')): continue
        if not (Path(rel).name.endswith(('-current.csv','-current.json','-current.md')) or rel in {'PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json','PUBLIC/PUBLIC-BUNDLE-MANIFEST-current.json'}): continue
        if rel.startswith(ALLOWED_BASELINE_PREFIXES): continue
        text=p.read_text(encoding='utf-8', errors='replace')
        bad=False; obs=[]
        if prev_export and prev_export in text:
            bad=True; obs.append('previous_export_name')
        for pat in current_patterns:
            if pat.search(text): bad=True; obs.append('stale_current_revision_pattern')
        if bad:
            generated_current.append(f"{rel}:{','.join(obs)}")
    add(rows,'.','generated_current_surfaces_not_stale','high',not generated_current,'; '.join(generated_current[:12]),'current generated/public/schema surfaces must not carry stale current-revision or previous-export identity outside explicit baseline/delta files')
    accountability_paths=['META/Previous-Release-Fingerprint-current.json','META/Previous-Release-Fingerprint-current.md','META/Package-Delta-Manifest-current.csv']
    acc='\n'.join((root/r).read_text(encoding='utf-8', errors='replace') for r in accountability_paths if (root/r).exists())
    add(rows,'.','previous_revision_only_accountability_surface','medium',bool(prev_rev and prev_rev in acc),prev_rev,'previous-release revision should remain visible in explicit accountability surfaces')
    start=(root/'000-START-HERE.txt').read_text(encoding='utf-8', errors='replace') if (root/'000-START-HERE.txt').exists() else ''
    add(rows,'.','current_revision_visible','high',bool(rev and rev in start and rev in export),f'{rev} / {export}','current revision must be visible in start-here and export name')
    return rows

def write_reports(root: Path, rows):
    out=root/'META'; out.mkdir(exist_ok=True)
    with (out/'Cross-Report-Reference-Audit-current.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows([{k:r.get(k,'') for k in FIELDS} for r in rows])
    (out/'Cross-Report-Reference-Audit-current.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    high=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    lines=['# Cross-Report Reference Audit — current','', 'Generated by `tools/cross_report_reference_audit.py`.', '', f'Checks: {len(rows)}', f'High failures: {len(high)}', '', 'This audit catches stale previous-release identity leaking into front-door/current report surfaces while allowing explicit baseline/delta accountability files to mention the previous release.', '', '| file | check | severity | status | observed |','|---|---|---|---|---|']
    for r in rows:
        lines.append(f"| `{r['file']}` | {r['check']} | {r['severity']} | {r['status']} | {str(r['observed']).replace('|','/')} |")
    (out/'Cross-Report-Reference-Audit-current.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    high=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if high else 'PASS'} cross-report reference rows={len(rows)} high_fail={len(high)}")
    if args.fail_on_high and high: sys.exit(1)
if __name__=='__main__': main()
