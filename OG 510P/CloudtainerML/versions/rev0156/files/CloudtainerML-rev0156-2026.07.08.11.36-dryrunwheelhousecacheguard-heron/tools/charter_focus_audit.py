#!/usr/bin/env python3
from __future__ import annotations
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT/'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision','rev0000'); REVUP = REV.upper()
AUDIT_DIR = ROOT/'artifacts'/'audit'; AUDIT_DIR.mkdir(parents=True, exist_ok=True)
CORE_TERMS = ['performance','architecture','phase diagram','phase-diagram','native c++','equal-budget','surprise','falsifiable','tiny-scale','mechanism','latency','bytes','precision']
SIDE_TERMS = ['security','trust','poison','provenance','sycophancy','janus','admissibility','safety','distortion']
REQUIRED_SURFACES = ['PROJECT-CHARTER.md','PRIORITY-LIST.md','START_HERE.md','README.md','CONTEXT-PACK.md','AGENTS.md','NEXT-TURN-PROMPT.md','BABY-DATACUBE-CANDIDATE.json','SURFACE-STATUS.json','REENTRY-CONTRACT.json']

def read(rel: str) -> str:
    p = ROOT/rel
    if not p.exists(): return ''
    return p.read_text(encoding='utf-8', errors='replace').lower()

def count_terms(text: str, terms: list[str]) -> int:
    return sum(len(re.findall(re.escape(t.lower()), text)) for t in terms)

def main() -> int:
    docs = {rel: read(rel) for rel in REQUIRED_SURFACES}
    rows=[]; missing=[]; issues=[]
    for rel, txt in docs.items():
        if not txt:
            missing.append(rel); issues.append(f'missing {rel}'); continue
        core = count_terms(txt, CORE_TERMS)
        side = count_terms(txt, SIDE_TERMS)
        has_side_wing = 'side wing' in txt or 'bounded side' in txt
        has_not_security_project = 'not primarily a model-security project' in txt or 'not a model-security project' in txt or 'not the project center' in txt
        rows.append({'surface': rel, 'core_terms': core, 'side_terms': side, 'mentions_side_wing': has_side_wing, 'explicit_not_security_project': has_not_security_project})
        if rel in {'PROJECT-CHARTER.md','PRIORITY-LIST.md','START_HERE.md'} and core < side:
            issues.append(f'{rel} has more side-wing terms than core-performance terms')
    # P0 fraction among cells/ideas/sources.
    cells=json.loads((ROOT/'EXPERIMENT-MATRIX.json').read_text(encoding='utf-8'))['cells']
    ideas=json.loads((ROOT/'IDEA-LEDGER.json').read_text(encoding='utf-8'))['ideas']
    sources=json.loads((ROOT/'RESEARCH-SOURCE-REGISTRY.json').read_text(encoding='utf-8'))['sources']
    def sideish(obj):
        text=' '.join(str(obj.get(k,'')) for k in ['name','title','question','family','cheap_first_run']).lower()
        return any(t in text for t in SIDE_TERMS)
    p0_cells=[c for c in cells if c.get('priority')=='P0']
    side_p0_cells=[c for c in p0_cells if sideish(c)]
    p0_ideas=[i for i in ideas if i.get('priority')=='P0']
    side_p0_ideas=[i for i in p0_ideas if sideish(i)]
    p0_sources=[s for s in sources if s.get('priority')=='P0']
    side_p0_sources=[s for s in p0_sources if sideish(s)]
    cell_frac = len(side_p0_cells)/max(1,len(p0_cells))
    idea_frac = len(side_p0_ideas)/max(1,len(p0_ideas))
    source_frac = len(side_p0_sources)/max(1,len(p0_sources))
    if cell_frac > 0.20: issues.append(f'side-wing P0 cell fraction too high: {cell_frac:.3f}')
    if idea_frac > 0.20: issues.append(f'side-wing P0 idea fraction too high: {idea_frac:.3f}')
    # Required explicit phrases.
    charter_text=docs.get('PROJECT-CHARTER.md','') + docs.get('PRIORITY-LIST.md','')
    if 'tiny-scale' not in charter_text or 'performance' not in charter_text or 'surprise' not in charter_text:
        issues.append('charter/root priority missing tiny-scale/performance/surprise triad')
    if 'side wing' not in charter_text:
        issues.append('charter/root priority missing side wing framing')
    status = 'pass' if not issues else 'fail'
    report={
        'project':'CloudtainerML','revision':REV,'status':status,
        'summary':{
            'surface_count':len(rows),'missing_surface_count':len(missing),'p0_cell_count':len(p0_cells),'side_p0_cell_count':len(side_p0_cells),'side_p0_cell_fraction':round(cell_frac,4),
            'p0_idea_count':len(p0_ideas),'side_p0_idea_count':len(side_p0_ideas),'side_p0_idea_fraction':round(idea_frac,4),
            'p0_source_count':len(p0_sources),'side_p0_source_count':len(side_p0_sources),'side_p0_source_fraction':round(source_frac,4),
            'primary_charter':'tiny-scale performance/architecture/surprise lab; security/trust is side wing'
        },
        'issues':issues,
        'surface_rows':rows,
        'side_p0_cells':[c['cell_id']+': '+c.get('name','') for c in side_p0_cells],
        'side_p0_ideas':[i['id']+': '+i.get('name','') for i in side_p0_ideas],
        'side_p0_sources':[s['id']+': '+s.get('title','') for s in side_p0_sources]
    }
    (AUDIT_DIR/f'{REVUP}_CHARTER_FOCUS_AUDIT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    md=[f'# Charter focus audit — {REV}','',f'Status: **{status}**','', '## Summary','']
    for k,v in report['summary'].items(): md.append(f'- {k}: {v}')
    md.extend(['','## Issues',''])
    md.extend([f'- {x}' for x in issues] or ['- none'])
    md.extend(['','## Side-wing P0 cells',''])
    md.extend([f'- {x}' for x in report['side_p0_cells']] or ['- none'])
    md.extend(['','## Surface term counts','','| surface | core terms | side terms | side-wing framing | not-security-project |','|---|---:|---:|---|---|'])
    for r in rows: md.append(f"| `{r['surface']}` | {r['core_terms']} | {r['side_terms']} | {r['mentions_side_wing']} | {r['explicit_not_security_project']} |")
    (AUDIT_DIR/f'{REVUP}_CHARTER_FOCUS_AUDIT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(json.dumps({'status':status, **report['summary'], 'issues':len(issues)}, indent=2))
    return 0 if status == 'pass' else 1
if __name__ == '__main__':
    raise SystemExit(main())
