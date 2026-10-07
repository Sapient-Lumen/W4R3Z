#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, sys, importlib.util
from pathlib import Path

FIELDS=['edge_id','edge_type','source_path','target_path','generator','status','note']

def read_csv(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))

def read_json(path: Path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return None

def status_for(root: Path, source: str, target: str, generator: str=''):
    missing=[]
    for rel in [source, target, generator]:
        if rel and not (root/rel).exists(): missing.append(rel)
    return ('missing_dependency' if missing else 'pass', ('missing: '+ '; '.join(missing)) if missing else 'edge paths exist')

def add(rows, root: Path, edge_type: str, source: str, target: str, generator: str='', note: str=''):
    st, n=status_for(root, source, target, generator)
    rows.append({'edge_id':f'dep_{len(rows)+1:05d}','edge_type':edge_type,'source_path':source,'target_path':target,'generator':generator,'status':st,'note':note or n})

def generated_artifact_specs(root: Path):
    tool=root/'tools/generated_artifact_provenance.py'
    if tool.exists():
        try:
            spec=importlib.util.spec_from_file_location('generated_artifact_provenance_for_graph', tool)
            mod=importlib.util.module_from_spec(spec)
            assert spec and spec.loader
            spec.loader.exec_module(mod)
            return [{'artifact_path':a,'generator':g,'input_paths':'|'.join(i)} for a,g,i in getattr(mod,'ARTIFACTS',[])]
        except Exception:
            pass
    return read_csv(root/'META/Generated-Artifact-Provenance-current.csv')

def run(root: Path):
    rows=[]
    # Generated-artifact edges are the primary release dependency graph.
    generated_rows=generated_artifact_specs(root)
    for r in generated_rows:
        art=r.get('artifact_path',''); gen=r.get('generator','')
        if gen and art:
            add(rows, root, 'tool_generates_artifact', gen, art, gen, 'generator produces tracked artifact')
        for inp in [x for x in (r.get('input_paths','') or '').split('|') if x]:
            add(rows, root, 'input_feeds_generated_artifact', inp, art, gen, 'tracked input participates in artifact fingerprint')
    # Public release contract edges: every public file must be explicitly allowed by the contract.
    contract=read_json(root/'SCHEMA/Package-Release-Contract-current.json') or {}
    for rel in contract.get('allowed_public_layer_files',[]):
        add(rows, root, 'public_contract_allows_file', 'SCHEMA/Package-Release-Contract-current.json', rel, '', 'public file is explicitly allowlisted')
    # Ledger-to-JSON mirror edges from Ledger-Contract.
    ledgers=read_json(root/'SCHEMA/Ledger-Contract-current.json') or {}
    for rel,spec in ledgers.get('ledgers',{}).items():
        mirror=spec.get('json_mirror')
        if mirror: add(rows, root, 'ledger_mirrors_json', rel, mirror, '', 'CSV/JSON mirror relationship declared in ledger contract')
    # Frontmatter contract applies to current candidate/office/refresh text surfaces.
    for p in sorted((root/'CANDIDATES').glob('*.txt')):
        kind='frontmatter_contract_applies_refresh' if p.name.startswith('_REFRESH') else 'frontmatter_contract_applies_candidate'
        add(rows, root, kind, 'SCHEMA/Frontmatter-Contract-current.json', str(p.relative_to(root)), '', 'front matter schema applies to this text file')
    for p in sorted((root/'OFFICE-CARDS').glob('*.txt')):
        add(rows, root, 'frontmatter_contract_applies_office_card', 'SCHEMA/Frontmatter-Contract-current.json', str(p.relative_to(root)), '', 'front matter schema applies to this text file')
    # Tool inventory edges mark non-generator tools as deliberate package tools, not accidental artifacts.
    generated_tools={r.get('generator','') for r in generated_rows if r.get('generator')}
    for p in sorted((root/'tools').glob('*.py')):
        rel=str(p.relative_to(root))
        if rel not in generated_tools:
            add(rows, root, 'tool_inventory_untracked_generator_or_checker', 'tools/README.md', rel, '', 'tool is present and documented as a checker or helper outside generated-artifact table')
    if not rows:
        rows.append({'edge_id':'dep_00001','edge_type':'package_dependency_graph','source_path':'.','target_path':'.','generator':'tools/package_dependency_graph.py','status':'info','note':'no configured dependency edges found'})
    return rows

def write_reports(root: Path, rows):
    out=root/'META'; out.mkdir(exist_ok=True)
    with (out/'Package-Dependency-Graph-current.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows([{k:r.get(k,'') for k in FIELDS} for r in rows])
    (out/'Package-Dependency-Graph-current.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    missing=sum(1 for r in rows if r.get('status')=='missing_dependency')
    by_type={}
    for r in rows: by_type[r.get('edge_type','')]=by_type.get(r.get('edge_type',''),0)+1
    lines=['# Package Dependency Graph — current','', 'Generated by `tools/package_dependency_graph.py`.', '', f'Edges: {len(rows)}', f'Missing-dependency edges: {missing}', '', '## Edge counts', '']
    for k in sorted(by_type): lines.append(f'- `{k}`: {by_type[k]}')
    if missing:
        lines += ['', '## Missing dependency edges']
        for r in rows:
            if r.get('status')=='missing_dependency': lines.append(f"- `{r.get('edge_id')}` `{r.get('source_path')}` → `{r.get('target_path')}` — {r.get('note')}")
    else:
        lines += ['', 'PASS: all configured dependency edges point to existing package paths.']
    (out/'Package-Dependency-Graph-current.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-missing', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    missing=[r for r in rows if r.get('status')=='missing_dependency']
    for r in rows[:80]: print(f"{r.get('status','?').upper()} {r.get('edge_type')} {r.get('source_path')} -> {r.get('target_path')}")
    if len(rows)>80: print(f'... {len(rows)-80} more edges')
    if args.fail_on_missing and missing: sys.exit(1)
if __name__=='__main__': main()
