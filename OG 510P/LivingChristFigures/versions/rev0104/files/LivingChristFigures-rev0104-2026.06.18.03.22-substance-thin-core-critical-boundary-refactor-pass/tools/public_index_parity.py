#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re, sys
from pathlib import Path

FIELDS=['finding_id','severity','check','file','row','field','detail','remediation']
RAW_URL_RE=re.compile(r'https?://|www\.', re.I)
EMAIL_RE=re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', re.I)

def read_csv(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))

def read_json(path: Path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return None

def finding(rows, severity, check, file, row, field, detail, remediation):
    rows.append({'finding_id':f'pip_{len(rows)+1:04d}','severity':severity,'check':check,'file':file,'row':str(row),'field':field,'detail':detail,'remediation':remediation})

def md_candidate_ids(md: str) -> list[str]:
    ids=[]
    for line in md.splitlines():
        if not line.startswith('| cand_'): continue
        parts=[p.strip() for p in line.strip().strip('|').split('|')]
        if parts and parts[0].startswith('cand_'): ids.append(parts[0])
    return ids

def run(root: Path):
    rows=[]
    csv_path=root/'PUBLIC/Candidate-Index-public.csv'
    json_path=root/'PUBLIC/Candidate-Index-public.json'
    md_path=root/'PUBLIC/Candidate-Index-public.md'
    man_path=root/'PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json'
    elig_path=root/'META/Public-Export-Eligibility-current.csv'
    for p in [csv_path,json_path,md_path,man_path,elig_path]:
        if not p.exists():
            finding(rows,'high','public_index_file_exists',str(p.relative_to(root)),0,'','missing','Regenerate public index and required gate files before handoff.')
    if rows: return rows
    csv_rows=read_csv(csv_path)
    json_rows=read_json(json_path)
    eligibility={r.get('candidate_id',''):r for r in read_csv(elig_path)}
    if not isinstance(json_rows, list):
        finding(rows,'high','public_json_list',str(json_path.relative_to(root)),0,'','JSON is not a list','Regenerate public JSON from tools/render_public_safe_index.py.')
        json_rows=[]
    if len(csv_rows)!=len(json_rows):
        finding(rows,'high','public_csv_json_count',str(json_path.relative_to(root)),0,'',f'CSV rows {len(csv_rows)} != JSON rows {len(json_rows)}','Regenerate public CSV/JSON together from the renderer.')
    else:
        for i,(cr,jr) in enumerate(zip(csv_rows,json_rows), start=2):
            norm_j={k:str(v) for k,v in jr.items()}
            if cr != norm_j:
                finding(rows,'high','public_csv_json_row_parity',str(json_path.relative_to(root)),i,'',f'row for {cr.get("candidate_id","")} differs between CSV and JSON','Regenerate public CSV/JSON from a single renderer run.')
                break
    csv_ids=[r.get('candidate_id','') for r in csv_rows]
    json_ids=[r.get('candidate_id','') for r in json_rows]
    md_ids=md_candidate_ids(md_path.read_text(encoding='utf-8'))
    if csv_ids != json_ids:
        finding(rows,'high','public_json_order',str(json_path.relative_to(root)),0,'candidate_id','JSON order differs from CSV','Regenerate public JSON from renderer.')
    if csv_ids != md_ids:
        finding(rows,'high','public_markdown_order',str(md_path.relative_to(root)),0,'candidate_id',f'Markdown ids/order differ; csv={len(csv_ids)} md={len(md_ids)}','Regenerate Markdown from renderer and avoid hand edits.')
    manifest=read_json(man_path) or {}
    if str(manifest.get('candidate_count_public_index','')) != str(len(csv_rows)):
        finding(rows,'high','public_manifest_index_count',str(man_path.relative_to(root)),0,'candidate_count_public_index',f"manifest has {manifest.get('candidate_count_public_index')} but CSV has {len(csv_rows)}",'Update public manifest after rendering public index.')
    for idx,r in enumerate(csv_rows, start=2):
        cid=r.get('candidate_id','')
        elig=eligibility.get(cid)
        if not elig:
            finding(rows,'high','public_index_candidate_has_eligibility',str(csv_path.relative_to(root)),idx,'candidate_id',f'{cid} missing eligibility row','Regenerate Public-Export-Eligibility before rendering public index.')
            continue
        for field in ['public_export_tier','public_shape_template']:
            if r.get(field) != elig.get(field):
                finding(rows,'high','public_index_eligibility_parity',str(csv_path.relative_to(root)),idx,field,f'{cid} public {field}={r.get(field)!r} eligibility={elig.get(field)!r}','Regenerate public index from eligibility ledger.')
        if r.get('status_current') != 'public_safe_boundary_index_row_not_release_approval':
            finding(rows,'high','public_index_status_sentinel',str(csv_path.relative_to(root)),idx,'status_current',f'{cid} has {r.get("status_current")!r}','Public index must carry the non-release status sentinel only.')
        if r.get('capacity_state') != 'not_a_public_capacity_claim':
            finding(rows,'high','public_index_capacity_sentinel',str(csv_path.relative_to(root)),idx,'capacity_state',f'{cid} has {r.get("capacity_state")!r}','Public index must not expose working capacity-state labels.')
        if str(r.get('live_referral_safe','')).lower() != 'false':
            finding(rows,'high','public_index_live_referral_false',str(csv_path.relative_to(root)),idx,'live_referral_safe',f'{cid} is not false','Public index rows must be non-referral by default.')
        for field,val in r.items():
            text=str(val or '')
            if RAW_URL_RE.search(text):
                finding(rows,'high','public_index_raw_url',str(csv_path.relative_to(root)),idx,field,f'{cid} has raw URL-like text','Public index must not expose raw URLs; use link-review gate outside public rows.')
            if EMAIL_RE.search(text):
                finding(rows,'high','public_index_email',str(csv_path.relative_to(root)),idx,field,f'{cid} has email-like text','Public index must not expose contact paths.')
        if r.get('public_export_tier')=='quarantined_no_public_expansion':
            note = r.get('public_use_note','')
            if not any(marker in note for marker in ['Governance-quarantined', 'boundary shape only', 'Boundary index only', 'Policy/context index only']):
                finding(rows,'high','public_quarantine_note',str(csv_path.relative_to(root)),idx,'public_use_note',f'{cid} lacks quarantine/boundary-only note','Renderer must use quarantine-safe template-specific public-use note.')
    if not rows:
        finding(rows,'info','public_index_parity','PUBLIC/Candidate-Index-public.*',0,'','PASS public CSV/JSON/Markdown, manifest count, eligibility fields, and non-release sentinels agree','No action required.')
    return rows

def write_reports(root: Path, rows):
    out=root/'META'; out.mkdir(exist_ok=True)
    with (out/'Public-Index-Parity-current.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows([{k:r.get(k,'') for k in FIELDS} for r in rows])
    (out/'Public-Index-Parity-current.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    high=sum(1 for r in rows if r.get('severity')=='high')
    med=sum(1 for r in rows if r.get('severity')=='medium')
    lines=['# Public Index Parity — current','', 'Generated by `tools/public_index_parity.py`.', '', f'High findings: {high}', f'Medium findings: {med}', '']
    if high or med:
        lines.append('## Findings')
        for r in rows:
            if r.get('severity')!='info':
                lines.append(f"- **{r.get('severity')}** `{r.get('check')}` `{r.get('file')}` row {r.get('row')} field `{r.get('field')}` — {r.get('detail')}")
    else:
        lines.append('PASS: public index render surfaces agree with eligibility, manifest count, and non-release sentinels.')
    (out/'Public-Index-Parity-current.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    for r in rows[:80]: print(f"{r.get('severity','?').upper()} {r.get('check')} {r.get('file')}: {r.get('detail')}")
    if len(rows)>80: print(f'... {len(rows)-80} more rows')
    if args.fail_on_high and any(r.get('severity')=='high' for r in rows): sys.exit(1)
if __name__=='__main__': main()
