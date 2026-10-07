#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, importlib.util, json, sys
from collections import OrderedDict
from pathlib import Path

FIELDS=['step_id','phase','tool_path','command','declared_outputs','declared_inputs','dependency_status','execution_mode','note']

BOOTSTRAP_LATE_STEPS=[
    ('07_release_identity_closure','tools/schema_validate.py',['SCHEMA/Schema-Validation-Report-current.csv','SCHEMA/Schema-Validation-Report-current.json','SCHEMA/Schema-Validation-Report-current.md'],['SCHEMA/Frontmatter-Contract-current.json','SCHEMA/Ledger-Contract-current.json','SCHEMA/Package-Release-Contract-current.json']),
    ('07_release_identity_closure','tools/release_gate_attestation.py',['META/Release-Gate-Attestation-current.csv','META/Release-Gate-Attestation-current.json','META/Release-Gate-Attestation-current.md'],['manifest.json','META/Handoff-Review-Digest-current.csv','META/Version-Lineage-Audit-current.csv']),
    ('07_release_identity_closure','tools/release_evidence_closure.py',['META/Release-Evidence-Closure-current.csv','META/Release-Evidence-Closure-current.json','META/Release-Evidence-Closure-current.md'],['META/Release-Gate-Attestation-current.csv','META/Generated-Artifact-Provenance-current.csv','META/Package-File-Inventory-current.csv']),
    ('08_provenance_digest_closure','tools/handoff_review_digest.py',['META/Handoff-Review-Digest-current.csv','META/Handoff-Review-Digest-current.json','META/Handoff-Review-Digest-current.md'],['manifest.json','META/Package-Delta-Manifest-current.csv','META/Version-Lineage-Audit-current.csv','META/Release-Gate-Attestation-current.csv']),
    ('08_provenance_digest_closure','tools/generated_artifact_provenance.py',['META/Generated-Artifact-Provenance-current.csv','META/Generated-Artifact-Provenance-current.json','META/Generated-Artifact-Provenance-current.md'],['tools/generated_artifact_provenance.py','META/Handoff-Review-Digest-current.csv','META/Regeneration-Sequence-Plan-current.csv']),
]

def load_artifacts(root: Path):
    tool=root/'tools/generated_artifact_provenance.py'
    spec=importlib.util.spec_from_file_location('gap_for_regeneration_sequence', tool)
    mod=importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return list(getattr(mod,'ARTIFACTS',[]))

def command_for(tool: str) -> str:
    if tool.endswith('render_public_safe_index.py'):
        return f'python {tool} . --write'
    return f'python {tool} . --write-report'

def phase_for(tool: str) -> str:
    if 'public_export_eligibility' in tool or 'public_source_link_review' in tool: return '01_governance_inputs'
    if 'render_public_safe_index' in tool: return '02_public_render'
    if any(x in tool for x in ['public_release_lint','sensitive_surface_inventory','redaction_scan','rule46_scan']): return '03_safety_scans'
    if any(x in tool for x in ['archive_member','unicode_path']): return '05a_packaging_preclosure'
    if 'package_identity' in tool: return '07_release_identity_closure'
    if any(x in tool for x in ['evidence_lifecycle','candidate_governance_snapshot','governance_consistency','public_index_parity','public_index_semantic']): return '04_lifecycle_governance'
    if any(x in tool for x in ['row_validate','csv_json_mirror','schema_coverage','field_schema','path_reference','rule_gate','tool_run','required_document','audit_selftest','rebuild_readiness','policy_assertion','regeneration_sequence','archive_build','selftest_coverage','checksum_scope','public_negative_corpus','release_evidence_closure','version_lineage','package_delta','cross_report_reference','handoff_review_digest']): return '05_validation_meta'
    if any(x in tool for x in ['package_dependency_graph','package_file_inventory','generated_artifact_provenance']): return '06_inventory_provenance'
    return '05_validation_meta'

def run(root: Path):
    rows=[]
    grouped=OrderedDict()
    for artifact, tool, inputs in load_artifacts(root):
        grouped.setdefault(tool, {'outputs':[], 'inputs':[]})
        grouped[tool]['outputs'].append(artifact)
        for inp in inputs:
            if inp not in grouped[tool]['inputs']: grouped[tool]['inputs'].append(inp)
    ordered=sorted(grouped.items(), key=lambda kv: (phase_for(kv[0]), kv[0]))
    late_outputs={out for _phase,_tool,outs,_ins in BOOTSTRAP_LATE_STEPS for out in outs}
    ordered=[(tool,spec) for tool,spec in ordered if not any(out in late_outputs for out in spec['outputs'])]
    for idx,(tool, spec) in enumerate(ordered, start=1):
        paths=[tool]+spec['outputs']+spec['inputs']
        missing=[rel for rel in paths if rel and not (root/rel).exists()]
        status='pass' if not missing else 'missing_dependency'
        note='all declared tool/output/input paths exist' if not missing else 'missing: '+ '; '.join(missing[:8])
        rows.append({'step_id':f'regen_{idx:03d}','phase':phase_for(tool),'tool_path':tool,'command':command_for(tool),'declared_outputs':'|'.join(spec['outputs']),'declared_inputs':'|'.join(spec['inputs']),'dependency_status':status,'execution_mode':'plan_only_deterministic_order','note':note})
    idx=len(rows)
    for phase,tool,outputs,inputs in BOOTSTRAP_LATE_STEPS:
        idx+=1
        paths=[tool]+outputs+inputs
        missing=[rel for rel in paths if rel and not (root/rel).exists()]
        status='pass' if not missing else 'missing_dependency'
        note='all declared late-closure paths exist' if not missing else 'missing: '+ '; '.join(missing[:8])
        rows.append({'step_id':f'regen_{idx:03d}','phase':phase,'tool_path':tool,'command':command_for(tool),'declared_outputs':'|'.join(outputs),'declared_inputs':'|'.join(inputs),'dependency_status':status,'execution_mode':'plan_only_deterministic_order','note':note})
    return rows

def write_reports(root: Path, rows):
    out=root/'META'; out.mkdir(exist_ok=True)
    with (out/'Regeneration-Sequence-Plan-current.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows([{k:r.get(k,'') for k in FIELDS} for r in rows])
    (out/'Regeneration-Sequence-Plan-current.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    bad=[r for r in rows if r.get('dependency_status')!='pass']
    lines=['# Regeneration Sequence Plan — current','', 'Generated by `tools/regeneration_sequence_plan.py`.', '', f'Steps: {len(rows)}', f'Non-pass dependency rows: {len(bad)}', '', 'This is a deterministic plan, not a background runner. It locks a reviewable command order for regenerating tracked artifacts from named inputs.', '', '| step | phase | command | outputs | status |','|---|---|---|---|---|']
    for r in rows:
        lines.append(f"| {r['step_id']} | {r['phase']} | `{r['command']}` | `{r['declared_outputs']}` | {r['dependency_status']} |")
    (out/'Regeneration-Sequence-Plan-current.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-missing', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    bad=[r for r in rows if r.get('dependency_status')!='pass']
    print(f"{'FAIL' if bad else 'PASS'} regeneration sequence steps={len(rows)} missing={len(bad)}")
    if args.fail_on_missing and bad: sys.exit(1)
if __name__=='__main__': main()
