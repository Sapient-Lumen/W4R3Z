#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, importlib.util, json, re, sys
from collections import Counter
from pathlib import Path

FIELDS=['finding_id','severity','check','file','row','detail','readiness_status']
NONDETERMINISM_PATTERNS=[r'\bdatetime\.now\b', r'\bdate\.today\b', r'\btime\.time\b', r'\brandom\.', r'\buuid\.uuid4\b', r'\bmktemp\b']


def add(rows, sev, check, file, row, detail, status):
    rows.append({'finding_id':f'rra_{len(rows)+1:04d}','severity':sev,'check':check,'file':file,'row':str(row),'detail':detail,'readiness_status':status})


def read_artifacts(root: Path):
    gp=root/'tools/generated_artifact_provenance.py'
    try:
        spec=importlib.util.spec_from_file_location('gap_for_rebuild_readiness', gp)
        mod=importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(mod)
        return list(getattr(mod,'ARTIFACTS',[]))
    except Exception:
        rows=[]
        p=root/'META/Generated-Artifact-Provenance-current.csv'
        if p.exists():
            with p.open(encoding='utf-8', newline='') as f:
                for r in csv.DictReader(f): rows.append((r.get('artifact_path',''), r.get('generator',''), [x for x in r.get('input_paths','').split('|') if x]))
        return rows


def script_text(root: Path, rel: str) -> str:
    p=root/rel
    return p.read_text(encoding='utf-8', errors='ignore') if p.exists() else ''


def run(root: Path):
    rows=[]
    arts=read_artifacts(root)
    if not arts:
        add(rows,'high','artifact_spec_present','tools/generated_artifact_provenance.py',0,'No generated artifact specs could be read','missing_artifact_specs')
        return rows
    art_paths=[a for a,_g,_i in arts]
    dup=[p for p,c in Counter(art_paths).items() if p and c>1]
    if dup:
        add(rows,'high','artifact_path_unique','tools/generated_artifact_provenance.py',0,'Duplicate artifact paths: '+ '; '.join(dup[:8]),'duplicate_artifact')
    else:
        add(rows,'info','artifact_path_unique','tools/generated_artifact_provenance.py',0,f'{len(art_paths)} artifact paths unique','pass')
    generators=sorted(set(g for _a,g,_i in arts if g))
    for rel in generators:
        p=root/rel
        if not p.exists():
            add(rows,'high','generator_exists',rel,0,'generator path missing','missing_generator')
            continue
        txt=script_text(root, rel)
        has_cli='if __name__' in txt and 'main()' in txt
        has_write=('--write-report' in txt) or ('--write' in txt)
        add(rows,'info' if has_cli else 'high','generator_cli_entrypoint',rel,0,'CLI entry point present' if has_cli else 'CLI entry point missing','pass' if has_cli else 'missing_cli')
        add(rows,'info' if has_write else 'medium','generator_write_mode',rel,0,'write/report mode present' if has_write else 'no explicit --write or --write-report flag detected','pass' if has_write else 'manual_or_checker')
    for idx,(artifact, gen, inputs) in enumerate(arts, start=1):
        if not (root/artifact).exists():
            add(rows,'high','artifact_exists',artifact,idx,'tracked artifact is missing','missing_artifact')
        else:
            add(rows,'info','artifact_exists',artifact,idx,'tracked artifact exists','pass')
        if gen and not (root/gen).exists():
            add(rows,'high','artifact_generator_exists',artifact,idx,f'generator missing: {gen}','missing_generator')
        missing_inputs=[rel for rel in inputs if not (root/rel).exists()]
        if missing_inputs:
            add(rows,'high','artifact_inputs_exist',artifact,idx,'missing inputs: '+ '; '.join(missing_inputs[:8]),'missing_input')
        else:
            add(rows,'info','artifact_inputs_exist',artifact,idx,f'{len(inputs)} inputs exist','pass')
        if artifact.endswith('-current.csv'):
            base=artifact[:-4]
            missing_comp=[base+'.json', base+'.md']
            missing_comp=[rel for rel in missing_comp if not (root/rel).exists()]
            add(rows,'info' if not missing_comp else 'high','artifact_companion_triad',artifact,idx,'csv/json/md companions present' if not missing_comp else 'missing companions: '+ '; '.join(missing_comp),'pass' if not missing_comp else 'missing_companion')
    # Detect obvious nondeterministic primitives in generator/checker scripts. Temporary-directory usage is allowed only in audit_selftest.
    for p in sorted((root/'tools').glob('*.py')):
        rel=str(p.relative_to(root)); txt=script_text(root, rel)
        for pat in NONDETERMINISM_PATTERNS:
            if rel=='tools/audit_selftest.py' and 'temp' in pat:
                continue
            if re.search(pat, txt):
                add(rows,'medium','potential_nondeterminism',rel,0,f'pattern {pat} found','review_required')
    if not any(r['severity']=='high' for r in rows):
        add(rows,'info','rebuild_readiness_audit','.',0,f'PASS {len(arts)} artifacts, {len(generators)} generators, and companion/input checks reviewed','pass')
    return rows


def write_reports(root: Path, rows):
    out=root/'META'; out.mkdir(exist_ok=True)
    with (out/'Rebuild-Readiness-Audit-current.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows([{k:r.get(k,'') for k in FIELDS} for r in rows])
    (out/'Rebuild-Readiness-Audit-current.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    high=sum(1 for r in rows if r.get('severity')=='high')
    med=sum(1 for r in rows if r.get('severity')=='medium')
    lines=['# Rebuild Readiness Audit — current','', 'Generated by `tools/rebuild_readiness_audit.py`.', '', f'High findings: {high}', f'Medium findings: {med}', '', 'This is a deterministic-regeneration readiness check. It verifies tracked artifact specs, generator paths, input paths, companion triads, CLI/write modes, duplicate artifact paths, and obvious nondeterministic primitives.', '', '| finding_id | severity | check | file | status | detail |','|---|---|---|---|---|---|']
    for r in rows[:260]: lines.append(f"| {r['finding_id']} | {r['severity']} | {r['check']} | `{r['file']}` | {r['readiness_status']} | {(r['detail'] or '').replace('|','/')} |")
    if len(rows)>260: lines.append(f'\n... {len(rows)-260} additional rows omitted from Markdown view; see CSV/JSON.')
    (out/'Rebuild-Readiness-Audit-current.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    high=[r for r in rows if r.get('severity')=='high']
    print(f"{'FAIL' if high else 'PASS'} rebuild readiness rows={len(rows)} high={len(high)}")
    for r in high[:20]: print(f"HIGH {r['check']} {r['file']}: {r['detail']}")
    if args.fail_on_high and high: sys.exit(1)
if __name__=='__main__': main()
