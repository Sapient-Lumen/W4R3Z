#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, importlib.util, json, sys
from pathlib import Path

FIELDS=['surface_id','surface_path','package_zone','surface_role','generator_or_owner','schema_path','row_count','severity','status','note']
CORE_LEDGER_OWNERS={
 'Candidate-Ledger-current.csv':'ledger_contract',
 'Claim-Ledger-current.csv':'ledger_contract',
 'Source-Registry-current.csv':'ledger_contract',
 'Evidence-Debt-current.csv':'ledger_contract',
 'Office-Card-Index-current.csv':'ledger_contract',
 'Refresh-Index-current.csv':'ledger_contract',
 'Longform-Registry-current.csv':'ledger_contract',
}
MANUAL_META={
 'META/Boundary-Rule-Coverage-current.csv':'manual_rule_coverage',
 'META/Claim-Type-Taxonomy-current.csv':'manual_taxonomy',
 'META/Evidence-Debt-Dashboard-current.csv':'manual_dashboard',
 'META/Manifest-Audit-current.csv':'manual_meta_audit',
 'META/Negative-Case-Ledger-current.csv':'manual_negative_case_ledger',
 'META/Online-Research-Intake-current.csv':'manual_online_intake',
 'META/Operator-Dissent-Ledger-current.csv':'manual_operator_ledger',
 'META/Operator-Update-Audit-current.csv':'manual_operator_audit',
 'META/Public-Claim-Quarantine-current.csv':'manual_public_claim_quarantine',
 'META/Public-Claim-Release-Ledger-current.csv':'manual_public_claim_release',
 'META/Refresh-Sprint-Decision-Matrix-current.csv':'manual_refresh_decision_matrix',
 'META/Source-Freshness-and-Provenance-Audit-current.csv':'manual_source_freshness_audit',
 'META/Source-Promotion-Decision-Ledger-current.csv':'manual_source_promotion_decision',
 'META/Source-Promotion-Transaction-Audit-current.csv':'manual_source_promotion_transaction',
 'META/Clean-Extract-Archive-QA-current.csv':'manual_clean_extract_archive_qa_policy',
 'META/Path-Rename-Ledger-current.csv':'manual_path_rename_ledger',
 'META/Cloudtainer-Deep-Read-Audit-current.csv':'manual_cloudtainer_deep_read_audit',

 'META/Public-Lint-Allowed-Contexts-current.csv':'manual_public_lint_allowed_contexts',
 'META/Helper-Golden-Output-Audit-current.csv':'manual_helper_golden_output_audit',
 'META/Source-Preservation-Status-current.csv':'manual_source_preservation_status_alias',
 'META/Normalized-Code-Overlay-current.csv':'manual_normalized_code_overlay',
 'META/Candidate-Discovery-Log-current.csv':'manual_candidate_discovery_log',
 'META/Report-Contract-Registry-current.csv':'generated_report_contract_registry',
 'META/Report-Contract-Audit-current.csv':'generated_report_contract_audit',
}
BOOTSTRAP={
 'META/Generated-Artifact-Provenance-current.csv':('bootstrap_generated_artifact_provenance','tools/generated_artifact_provenance.py'),
 'META/Release-Gate-Attestation-current.csv':('bootstrap_release_gate_attestation','tools/release_gate_attestation.py'),
 'SCHEMA/Schema-Validation-Report-current.csv':('bootstrap_schema_validation_report','tools/schema_validate.py'),
 'META/Release-Evidence-Closure-current.csv':('bootstrap_release_evidence_closure','tools/release_evidence_closure.py'),
 'META/Handoff-Review-Digest-current.csv':('bootstrap_handoff_review_digest','tools/handoff_review_digest.py'),
}

def read_csv(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))


def generated_specs(root: Path):
    gp=root/'tools/generated_artifact_provenance.py'; out={}
    try:
        spec=importlib.util.spec_from_file_location('gap_for_surface_registry', gp)
        mod=importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(mod)
        for art, gen, _inputs in getattr(mod,'ARTIFACTS',[]): out[art]=gen
    except Exception:
        for r in read_csv(root/'META/Generated-Artifact-Provenance-current.csv'):
            out[r.get('artifact_path','')]=r.get('generator','')
    return out


def row_count(path: Path) -> int:
    try:
        with path.open(encoding='utf-8', newline='') as f:
            return max(0, sum(1 for _ in csv.reader(f))-1)
    except Exception: return 0


def expected_schema(root: Path, rel: str) -> str:
    name=Path(rel).name
    if name.endswith('-current.csv'):
        candidate='SCHEMA/'+name[:-len('-current.csv')]+'-Fields-current.csv'
        if (root/candidate).exists(): return candidate
    return ''


def zone_for(rel: str) -> str:
    if rel.startswith('META/'): return 'meta'
    if rel.startswith('SCHEMA/'): return 'schema'
    if rel.startswith('GOVERNANCE/'): return 'governance'
    if rel.startswith('PUBLIC/'): return 'public'
    return 'root'


def classify(root: Path, rel: str, genmap: dict):
    if rel in genmap: return 'generated_artifact', genmap[rel]
    if rel in BOOTSTRAP: return BOOTSTRAP[rel]
    if rel in CORE_LEDGER_OWNERS: return 'core_ledger_contract', CORE_LEDGER_OWNERS[rel]
    if rel in MANUAL_META: return MANUAL_META[rel], 'manual_curated_meta_instrument'
    if rel.startswith('SCHEMA/') and rel.endswith('-Fields-current.csv'): return 'field_schema', 'schema_layer'
    if rel.startswith('SCHEMA/') and ('Controlled-Vocabulary-current.csv' in rel or rel.endswith('Public-Allowed-Claim-Shapes-current.csv') or rel.endswith('Public-Link-Policy-current.csv') or rel.endswith('Harm-Proximity-Controlled-Vocabulary-current.csv') or rel.endswith('Normalized-Code-Overlay-current.csv')): return 'controlled_vocabulary_or_claim_shape_table','schema_layer'
    if rel.startswith('GOVERNANCE/'): return 'governance_static_or_review_ledger','governance_layer'
    if rel.startswith('PUBLIC/') and rel in {'PUBLIC/Candidate-Index-public.csv'}: return 'public_generated_index','tools/render_public_safe_index.py'
    return 'unclassified_current_surface',''


def run(root: Path):
    genmap=generated_specs(root)
    rows=[]
    paths=[]
    for base in [root, root/'META', root/'SCHEMA', root/'GOVERNANCE', root/'PUBLIC']:
        if not base.exists(): continue
    for p in sorted(root.rglob('*-current.csv')):
        rel=str(p.relative_to(root)).replace('\\','/')
        if '__pycache__' in rel.split('/'): continue
        role, owner=classify(root, rel, genmap)
        schema=expected_schema(root, rel)
        status='pass'; sev='info'; note='current CSV surface is classified'
        if role=='unclassified_current_surface': status='fail'; sev='high'; note='current CSV surface lacks generated/bootstrap/manual/schema classification'
        if role not in {'field_schema','controlled_vocabulary_or_claim_shape_table','core_ledger_contract'} and not schema and rel not in {'SCHEMA/Schema-Validation-Report-current.csv'}:
            # Schema-coverage audit is authoritative; here we surface review-only absence.
            if status=='pass': note+='; no dedicated field schema found, covered elsewhere or manual'
        rows.append({'surface_id':f'surface_{len(rows)+1:04d}','surface_path':rel,'package_zone':zone_for(rel),'surface_role':role,'generator_or_owner':owner,'schema_path':schema,'row_count':str(row_count(p)),'severity':sev,'status':status,'note':note})
    if not any(r['status']=='fail' for r in rows):
        rows.append({'surface_id':f'surface_{len(rows)+1:04d}','surface_path':'.','package_zone':'package','surface_role':'current_surface_registry_summary','generator_or_owner':'tools/current_surface_registry.py','schema_path':'SCHEMA/Current-Surface-Registry-Fields-current.csv','row_count':str(len(rows)),'severity':'info','status':'pass','note':f'all {len(rows)} current CSV surfaces classified'})
    return rows


def write_reports(root: Path, rows):
    out=root/'META'; out.mkdir(exist_ok=True)
    with (out/'Current-Surface-Registry-current.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows([{k:r.get(k,'') for k in FIELDS} for r in rows])
    (out/'Current-Surface-Registry-current.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    lines=['# Current Surface Registry — current','', 'Generated by `tools/current_surface_registry.py`.', '', f'Rows: {len(rows)}', f'High failures: {len(bad)}', '', 'This report classifies every `*-current.csv` surface as generated, bootstrap, schema, core-ledger, governance, public, or deliberate manual META material.', '', '| surface_path | role | owner | status | note |','|---|---|---|---|---|']
    for r in rows[:260]: lines.append(f"| `{r['surface_path']}` | {r['surface_role']} | `{r['generator_or_owner']}` | {r['status']} | {r['note'].replace('|','/')} |")
    if len(rows)>260: lines.append(f'\n... {len(rows)-260} additional rows omitted from Markdown view; see CSV/JSON.')
    (out/'Current-Surface-Registry-current.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if bad else 'PASS'} current surface registry rows={len(rows)} high={len(bad)}")
    for r in bad[:20]: print(f"HIGH {r['surface_path']}: {r['note']}")
    if args.fail_on_high and bad: sys.exit(1)
if __name__=='__main__': main()
