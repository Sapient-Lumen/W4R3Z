#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, sys
from pathlib import Path

sys.dont_write_bytecode = True
from lib_cube import (
    current_csv_surfaces,
    expected_field_schema_path,
    package_rel,
    read_csv_header,
    read_csv_rows,
    read_generated_artifact_specs,
    read_json,
    safe_md,
    csv_row_count,
    write_csv_json_md_report,
)

REGISTRY_FIELDS=[
    'contract_id','surface_path','package_zone','surface_family','csv_path','json_path','markdown_path','schema_path',
    'schema_contract_type','generator_or_owner','row_count','json_row_count','companion_policy','public_boundary','status','note'
]
AUDIT_FIELDS=['audit_id','check','severity','status','surface_path','expected_path','detail']
CORE_LEDGER_OWNERS={
 'Candidate-Ledger-current.csv':'ledger_contract',
 'Claim-Ledger-current.csv':'ledger_contract',
 'Source-Registry-current.csv':'ledger_contract',
 'Evidence-Debt-current.csv':'ledger_contract',
 'Office-Card-Index-current.csv':'ledger_contract',
 'Refresh-Index-current.csv':'ledger_contract',
 'Longform-Registry-current.csv':'ledger_contract',
 'PUBLIC/Candidate-Index-public.csv':'ledger_contract',
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
}
BOOTSTRAP={
 'META/Generated-Artifact-Provenance-current.csv':'bootstrap_generated_artifact_provenance',
 'META/Release-Gate-Attestation-current.csv':'bootstrap_release_gate_attestation',
 'SCHEMA/Schema-Validation-Report-current.csv':'bootstrap_schema_validation_report',
 'META/Release-Evidence-Closure-current.csv':'bootstrap_release_evidence_closure',
 'META/Handoff-Review-Digest-current.csv':'bootstrap_handoff_review_digest',
 'META/Report-Contract-Registry-current.csv':'bootstrap_report_contract_registry_self',
 'META/Report-Contract-Audit-current.csv':'bootstrap_report_contract_audit_self',
}

def zone_for(rel: str) -> str:
    if rel.startswith('META/'): return 'meta'
    if rel.startswith('SCHEMA/'): return 'schema'
    if rel.startswith('GOVERNANCE/'): return 'governance'
    if rel.startswith('PUBLIC/'): return 'public'
    return 'root'

def family_for(rel: str) -> str:
    name=Path(rel).name
    if name.endswith('-current.csv'): return name[:-len('-current.csv')]
    return name[:-4] if name.endswith('.csv') else name

def public_boundary(rel: str) -> str:
    if rel.startswith('PUBLIC/'):
        return 'public_layer_closed_index_policy_only'
    if rel.startswith('GOVERNANCE/'):
        return 'governance_internal_no_public_expansion'
    if rel.startswith('META/') or rel.startswith('SCHEMA/'):
        return 'audit_or_schema_surface_not_public_payload'
    return 'internal_working_surface_not_public_payload'

def schema_contract(root: Path, rel: str, ledger_paths: set[str]) -> tuple[str,str]:
    fs=expected_field_schema_path(rel)
    if (root/fs).exists(): return fs, 'dedicated_field_schema'
    if rel in ledger_paths or rel in CORE_LEDGER_OWNERS: return 'SCHEMA/Ledger-Contract-current.json', 'ledger_contract'
    if rel.startswith('SCHEMA/') and rel.endswith('-Fields-current.csv'): return rel, 'field_schema_self_describing'
    if rel.startswith('SCHEMA/') and ('Controlled-Vocabulary' in rel or rel.endswith('Public-Allowed-Claim-Shapes-current.csv') or rel.endswith('Public-Link-Policy-current.csv') or rel.endswith('Harm-Proximity-Controlled-Vocabulary-current.csv') or rel.endswith('Normalized-Code-Overlay-current.csv')):
        return 'SCHEMA/README-schema-current.md', 'schema_layer_controlled_vocabulary'
    return '', 'missing_or_manual_contract'

def owner_for(root: Path, rel: str, genmap: dict[str,str]) -> str:
    if rel in genmap: return genmap[rel]
    if rel in BOOTSTRAP: return BOOTSTRAP[rel]
    if rel in CORE_LEDGER_OWNERS: return CORE_LEDGER_OWNERS[rel]
    if rel in MANUAL_META: return MANUAL_META[rel]
    if rel.startswith('SCHEMA/') and rel.endswith('-Fields-current.csv'): return 'schema_layer'
    if rel.startswith('SCHEMA/') and ('Controlled-Vocabulary' in rel or rel.endswith('Public-Allowed-Claim-Shapes-current.csv') or rel.endswith('Public-Link-Policy-current.csv') or rel.endswith('Harm-Proximity-Controlled-Vocabulary-current.csv') or rel.endswith('Normalized-Code-Overlay-current.csv')): return 'schema_layer'
    if rel.startswith('GOVERNANCE/'): return 'governance_layer'
    return ''

def json_count_and_keys(root: Path, rel: str) -> tuple[int,list[str],str]:
    jp=root/rel.replace('.csv','.json')
    data=read_json(jp)
    if not isinstance(data, list): return 0, [], 'json_not_list'
    if not data: return 0, [], 'json_empty_list_ok'
    if isinstance(data[0], dict): return len(data), list(data[0].keys()), 'json_list_of_objects'
    return len(data), [], 'json_list_non_object'

def build_registry(root: Path):
    ledgers=read_json(root/'SCHEMA/Ledger-Contract-current.json') or {}
    ledger_paths=set((ledgers.get('ledgers') or {}).keys())
    genmap=read_generated_artifact_specs(root)
    rows=[]
    for rel in current_csv_surfaces(root):
        csv_path=root/rel
        jp=rel[:-4]+'.json'
        mp=rel[:-4]+'.md'
        schema_path, schema_type=schema_contract(root, rel, ledger_paths)
        owner=owner_for(root, rel, genmap)
        row_count=csv_row_count(csv_path)
        json_count, _json_keys, json_kind=json_count_and_keys(root, rel)
        companion_policy='csv_json_required'
        if rel.startswith(('META/','SCHEMA/','GOVERNANCE/','PUBLIC/')):
            companion_policy='csv_json_md_required'
        elif (root/mp).exists():
            companion_policy='csv_json_md_present_root_optional'
        status='pass'
        notes=[]
        if not (root/jp).exists():
            status='fail'; notes.append('missing JSON mirror')
        if companion_policy=='csv_json_md_required' and not (root/mp).exists():
            status='fail'; notes.append('missing Markdown companion')
        if schema_type=='missing_or_manual_contract' and not owner:
            status='fail'; notes.append('no schema contract and no owner classification')
        elif schema_type=='missing_or_manual_contract':
            notes.append('manual/owner-governed surface without dedicated field schema')
        if owner=='':
            status='fail'; notes.append('missing generator/owner classification')
        if (root/jp).exists() and json_kind=='json_list_of_objects' and json_count!=row_count:
            status='fail'; notes.append(f'CSV/JSON row count mismatch csv={row_count} json={json_count}')
        rows.append({
            'contract_id':f'report_contract_{len(rows)+1:04d}',
            'surface_path':rel,
            'package_zone':zone_for(rel),
            'surface_family':family_for(rel),
            'csv_path':rel,
            'json_path':jp if (root/jp).exists() else '',
            'markdown_path':mp if (root/mp).exists() else '',
            'schema_path':schema_path,
            'schema_contract_type':schema_type,
            'generator_or_owner':owner,
            'row_count':str(row_count),
            'json_row_count':str(json_count),
            'companion_policy':companion_policy,
            'public_boundary':public_boundary(rel),
            'status':status,
            'note':'; '.join(notes) if notes else 'report surface contract is explicit enough for handoff audit',
        })
    return rows

def add_audit(rows, check, severity, status, surface, expected, detail):
    rows.append({'audit_id':f'report_contract_audit_{len(rows)+1:04d}','check':check,'severity':severity,'status':status,'surface_path':surface,'expected_path':expected,'detail':detail})

def build_audit(root: Path, registry_rows):
    rows=[]
    surfaces=set(current_csv_surfaces(root))
    reg_surfaces={r['surface_path'] for r in registry_rows}
    missing=sorted(surfaces-reg_surfaces)
    extra=sorted(reg_surfaces-surfaces)
    add_audit(rows,'registry_covers_current_csv_surfaces','high' if missing or extra else 'info','fail' if missing or extra else 'pass','.', 'META/Report-Contract-Registry-current.csv', f'missing={len(missing)} extra={len(extra)}')
    for r in registry_rows:
        rel=r['surface_path']; p=root/rel
        header=read_csv_header(p)
        json_rel=rel[:-4]+'.json'; md_rel=rel[:-4]+'.md'
        if not (root/json_rel).exists():
            add_audit(rows,'json_mirror_present','high','fail',rel,json_rel,'missing JSON mirror')
        else:
            json_count, json_keys, kind=json_count_and_keys(root, rel)
            if kind not in {'json_list_of_objects','json_empty_list_ok'}:
                add_audit(rows,'json_mirror_shape','high','fail',rel,json_rel,f'JSON mirror is {kind}')
            elif json_count!=int(r['row_count']):
                add_audit(rows,'json_row_count_matches_csv','high','fail',rel,json_rel,f'csv={r["row_count"]} json={json_count}')
            elif json_keys and header and json_keys!=header:
                add_audit(rows,'json_key_order_matches_csv_header','high','fail',rel,json_rel,'JSON object keys differ from CSV header')
            else:
                add_audit(rows,'json_mirror_contract','info','pass',rel,json_rel,'JSON mirror exists, row count matches, and key order matches CSV header')
        if r['companion_policy']=='csv_json_md_required' and not (root/md_rel).exists():
            add_audit(rows,'markdown_companion_present','high','fail',rel,md_rel,'missing Markdown companion required for package zone')
        elif r['companion_policy'].startswith('csv_json_md'):
            add_audit(rows,'markdown_companion_present','info','pass',rel,md_rel,'Markdown companion policy satisfied')
        else:
            add_audit(rows,'markdown_companion_policy','info','pass',rel,md_rel,'Markdown companion not required for root/core ledger surface')
        schema=r.get('schema_path','')
        if not schema:
            add_audit(rows,'schema_or_ledger_contract_present','medium' if r.get('generator_or_owner') else 'high','review' if r.get('generator_or_owner') else 'fail',rel,'SCHEMA/*-Fields-current.csv or Ledger-Contract','no dedicated schema/ledger contract; owner classification is reviewable')
        elif schema!=rel and not (root/schema).exists():
            add_audit(rows,'schema_or_ledger_contract_present','high','fail',rel,schema,'declared schema path missing')
        else:
            add_audit(rows,'schema_or_ledger_contract_present','info','pass',rel,schema,'schema/ledger/self contract present')
        if not r.get('generator_or_owner'):
            add_audit(rows,'generator_or_owner_classified','high','fail',rel,'tools/* or manual owner','missing owner')
        else:
            add_audit(rows,'generator_or_owner_classified','info','pass',rel,r.get('generator_or_owner'), 'generator or deliberate owner is explicit')
        if r.get('status')!='pass':
            add_audit(rows,'registry_row_status','high','fail',rel,'status=pass',r.get('note',''))
    if not any(a['severity']=='high' and a['status']!='pass' for a in rows):
        add_audit(rows,'report_contract_audit_summary','info','pass','.', 'META/Report-Contract-Audit-current.csv', f'PASS report contracts for {len(registry_rows)} current CSV surfaces; high failures=0')
    return rows

def write_reports(root: Path, registry_rows, audit_rows):
    write_csv_json_md_report(
        root=root,
        csv_rel='META/Report-Contract-Registry-current.csv',
        fields=REGISTRY_FIELDS,
        rows=registry_rows,
        title='Report Contract Registry',
        generated_by='tools/report_contract_registry.py',
        columns=['surface_path','schema_contract_type','generator_or_owner','companion_policy','status','note'],
        intro_lines=[
            f'Current CSV surfaces registered: {len(registry_rows)}',
            f'Non-pass registry rows: {sum(1 for r in registry_rows if r.get("status")!="pass")}',
            'This registry makes report ownership/schema/companion expectations explicit; it does not loosen the public layer.',
        ],
        max_md_rows=320,
    )
    write_csv_json_md_report(
        root=root,
        csv_rel='META/Report-Contract-Audit-current.csv',
        fields=AUDIT_FIELDS,
        rows=audit_rows,
        title='Report Contract Audit',
        generated_by='tools/report_contract_registry.py',
        columns=['check','severity','status','surface_path','expected_path','detail'],
        intro_lines=[
            f'High failures: {sum(1 for r in audit_rows if r.get("severity")=="high" and r.get("status")!="pass")}',
            f'Review rows: {sum(1 for r in audit_rows if r.get("status")=="review")}',
            'High failures block handoff; medium review rows are visible debt unless promoted by a later gate.',
        ],
        max_md_rows=360,
    )

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve()
    registry=build_registry(root); audit=build_audit(root, registry)
    if args.write_report: write_reports(root, registry, audit)
    high=[r for r in audit if r.get('severity')=='high' and r.get('status')!='pass']
    review=[r for r in audit if r.get('status')=='review']
    print(f"{'FAIL' if high else 'PASS'} report contract registry surfaces={len(registry)} audit_rows={len(audit)} high={len(high)} review={len(review)}")
    for r in high[:20]: print(f"HIGH {r['check']} {r['surface_path']}: {r['detail']}")
    if args.fail_on_high and high: sys.exit(1)
if __name__=='__main__': main()
