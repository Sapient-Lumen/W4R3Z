#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, importlib.util, json, sys
from pathlib import Path

FIELDS=['file_path','size_bytes','sha256','package_zone','file_role','currentness','generated_by','public_release_scope','notes']
SELF_OUTPUTS={'META/Package-File-Inventory-current.csv','META/Package-File-Inventory-current.json','META/Package-File-Inventory-current.md'}
EXCLUDED={'SHA256SUMS.txt','SHA256SUMS.txt.sig','QA-REPORT-current.txt','META/Generated-Artifact-Provenance-current.csv','META/Generated-Artifact-Provenance-current.json','META/Generated-Artifact-Provenance-current.md','META/Release-Gate-Attestation-current.csv','META/Release-Gate-Attestation-current.json','META/Release-Gate-Attestation-current.md','SCHEMA/Schema-Validation-Report-current.csv','SCHEMA/Schema-Validation-Report-current.json','SCHEMA/Schema-Validation-Report-current.md','META/Release-Evidence-Closure-current.csv','META/Release-Evidence-Closure-current.json','META/Release-Evidence-Closure-current.md','META/Handoff-Review-Digest-current.csv','META/Handoff-Review-Digest-current.json','META/Handoff-Review-Digest-current.md'} | SELF_OUTPUTS


def sha(path: Path) -> str:
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()


def read_generated_map(root: Path):
    out={}
    tool=root/'tools/generated_artifact_provenance.py'
    if tool.exists():
        try:
            spec=importlib.util.spec_from_file_location('generated_artifact_provenance_for_inventory', tool)
            mod=importlib.util.module_from_spec(spec)
            assert spec and spec.loader
            spec.loader.exec_module(mod)
            for artifact, generator, _inputs in getattr(mod, 'ARTIFACTS', []):
                if artifact and generator:
                    out[artifact]=generator
            return out
        except Exception:
            pass
    p=root/'META/Generated-Artifact-Provenance-current.csv'
    if not p.exists(): return out
    with p.open(encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f):
            if r.get('artifact_path') and r.get('generator'):
                out[r['artifact_path']]=r['generator']
    return out


def classify_zone(rel: str) -> str:
    if rel.startswith('PUBLIC/'): return 'public_layer'
    if rel.startswith('GOVERNANCE/'): return 'governance_layer'
    if rel.startswith('META/'): return 'meta_audit_layer'
    if rel.startswith('SCHEMA/'): return 'schema_contract_layer'
    if rel.startswith('tools/'): return 'tooling_layer'
    if rel.startswith('CANDIDATES/'): return 'candidate_layer'
    if rel.startswith('OFFICE-CARDS/'): return 'office_card_layer'
    if rel.startswith('LONGFORM/'): return 'longform_layer'
    return 'root_handoff_layer'


def classify_role(rel: str) -> str:
    name=Path(rel).name
    if rel.startswith('tools/') and name.endswith('.py'): return 'tool_script'
    if name.endswith('.csv'): return 'csv_table'
    if name.endswith('.json'): return 'json_data_or_contract'
    if name.endswith('.md'): return 'markdown_documentation_or_report'
    if name.endswith('.txt') and rel.startswith('CANDIDATES/_REFRESH'): return 'refresh_note'
    if name.endswith('.txt') and rel.startswith('CANDIDATES/'): return 'candidate_note'
    if name.endswith('.txt') and rel.startswith('OFFICE-CARDS/'): return 'office_card_note'
    if name.startswith('QA-REPORT-'): return 'qa_report'
    if name.startswith('REASONING-NOTE-'): return 'reasoning_note'
    if name.startswith('SearchTrail-'): return 'search_trail'
    return 'handoff_text_or_other'


def currentness(rel: str) -> str:
    name=Path(rel).name
    if '-current' in name or name in {'manifest.json','CURRENT-SPINE.md','CUBE-MAP.md','CUBE-RULES.txt','000-START-HERE.txt','LivingChristFigures.txt','DOOR-ETHICS.txt','README.md','SHA256SUMS.txt'}:
        return 'current_surface'
    if any(x in name for x in ['rev0054','rev0053','rev0052','rev0051','rev0050']):
        return 'recent_revision_record'
    if 'rev' in name:
        return 'historical_revision_record'
    return 'current_or_static'


def public_scope(rel: str) -> str:
    if rel.startswith('PUBLIC/'):
        return 'public_layer_file_allowlist_required'
    return 'not_public_layer'


def run(root: Path):
    gen_map=read_generated_map(root)
    rows=[]
    for p in sorted(x for x in root.rglob('*') if x.is_file()):
        rel=str(p.relative_to(root))
        if rel in EXCLUDED: continue
        if '/__pycache__/' in rel or rel.endswith(('.pyc','.pyo','.zip')) or Path(rel).name.startswith('QA-REPORT-'): continue
        rows.append({
            'file_path':rel,
            'size_bytes':str(p.stat().st_size),
            'sha256':sha(p),
            'package_zone':classify_zone(rel),
            'file_role':classify_role(rel),
            'currentness':currentness(rel),
            'generated_by':gen_map.get(rel,''),
            'public_release_scope':public_scope(rel),
            'notes':'self inventory excludes SHA256SUMS, SHA256SUMS signatures, QA reports, self outputs, generated-provenance, schema-validation, release-gate, release-evidence, and handoff-digest reports to avoid recursive hash drift',
        })
    return rows


def write_reports(root: Path, rows):
    out=root/'META'; out.mkdir(exist_ok=True)
    with (out/'Package-File-Inventory-current.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows([{k:r.get(k,'') for k in FIELDS} for r in rows])
    (out/'Package-File-Inventory-current.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    by_zone={}
    for r in rows: by_zone[r['package_zone']]=by_zone.get(r['package_zone'],0)+1
    lines=['# Package File Inventory — current','', 'Generated by `tools/package_file_inventory.py`.', '', f'Files inventoried: {len(rows)}', '', 'The inventory excludes `SHA256SUMS.txt`, `SHA256SUMS.txt.sig`, QA reports, its own three output files, and self-referential late-gate reports to avoid recursive hash drift. Final package integrity is still checked by `SHA256SUMS.txt` and QA.', '', '## Counts by zone', '']
    for z in sorted(by_zone): lines.append(f'- `{z}`: {by_zone[z]}')
    lines += ['', '| file_path | zone | role | currentness | generated_by |','|---|---|---|---|---|']
    for r in rows[:240]:
        lines.append(f"| `{r['file_path']}` | {r['package_zone']} | {r['file_role']} | {r['currentness']} | `{r['generated_by']}` |")
    if len(rows)>240: lines.append(f'\n... {len(rows)-240} additional files omitted from Markdown view; see CSV/JSON.')
    (out/'Package-File-Inventory-current.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


def verify(root: Path):
    rows=run(root)
    got={r['file_path']: r['sha256'] for r in rows}
    p=root/'META/Package-File-Inventory-current.csv'
    if not p.exists(): return ['missing package file inventory CSV']
    stored={}
    with p.open(encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f): stored[r.get('file_path','')]=r.get('sha256','')
    missing=sorted(set(got)-set(stored)); extra=sorted(set(stored)-set(got)); drift=sorted(k for k in set(got)&set(stored) if got[k]!=stored[k])
    out=[]
    if missing: out.append('inventory missing files: '+'; '.join(missing[:10]))
    if extra: out.append('inventory extra files: '+'; '.join(extra[:10]))
    if drift: out.append('inventory hash drift: '+'; '.join(drift[:10]))
    return out


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--verify', action='store_true'); ap.add_argument('--fail-on-drift', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve()
    if args.verify:
        drift=verify(root)
        if drift:
            for d in drift: print('DRIFT '+d)
            if args.fail_on_drift: sys.exit(1)
        else: print('PASS package file inventory verifies against current files')
        return
    rows=run(root)
    if args.write_report: write_reports(root, rows)
    print(f'PASS package file inventory rows: {len(rows)}')
if __name__=='__main__': main()
