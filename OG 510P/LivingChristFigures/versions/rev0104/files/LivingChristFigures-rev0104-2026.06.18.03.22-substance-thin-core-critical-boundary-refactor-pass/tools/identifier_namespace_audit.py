#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
from lib_cube import write_csv_json_md_report

REGISTRY_FIELDS=[
    'identifier_kind','identifier','surface_path','row_locator','display_label','expected_pattern',
    'namespace_status','reference_count','definition_status','note'
]
AUDIT_FIELDS=['audit_id','check','severity','status','identifier_kind','identifier','surface_path','detail']

NAMESPACES={
    'candidate_id': {
        'path':'Candidate-Ledger-current.csv', 'column':'candidate_id', 'label':'name',
        'pattern':r'cand_[a-z0-9_]+', 'required': True,
    },
    'office_id': {
        'path':'Office-Card-Index-current.csv', 'column':'office_id', 'label':'office_label',
        'pattern':r'office_[a-z0-9_]+', 'required': True,
    },
    'source_id': {
        'path':'Source-Registry-current.csv', 'column':'source_id', 'label':'domain',
        'pattern':r'src_[a-z0-9_]+_[0-9a-f]{8}', 'required': True,
    },
    'claim_id': {
        'path':'Claim-Ledger-current.csv', 'column':'claim_id', 'label':'claim_type',
        'pattern':r'claim_[0-9]{4}', 'required': True,
    },
    'debt_id': {
        'path':'Evidence-Debt-current.csv', 'column':'debt_id', 'label':'debt_type',
        'pattern':r'debt_[0-9]{4}', 'required': True,
    },
    'refresh_id': {
        'path':'Refresh-Index-current.csv', 'column':'refresh_id', 'label':'file_path',
        'pattern':r'refresh_[a-z0-9_]+', 'required': True,
    },
    'boundary_domain_id': {
        'path':'META/Boundary-Domain-Registry-current.csv', 'column':'domain_id', 'label':'domain_label',
        'pattern':r'boundary_[a-z0-9_]+', 'required': True,
    },
    'release_gate_id': {
        'path':'META/Release-Gate-Attestation-current.csv', 'column':'gate_id', 'label':'gate_name',
        'pattern':r'gate_[0-9]{3}', 'required': True,
    },
}

REFERENCE_COLUMNS={
    'candidate_id': [
        ('Candidate-Ledger-current.csv','candidate_id'),('Claim-Ledger-current.csv','candidate_id'),('Evidence-Debt-current.csv','candidate_id'),
        ('Source-Registry-current.csv','candidate_ids'),('Refresh-Index-current.csv','related_candidate_ids'),('PUBLIC/Candidate-Index-public.csv','candidate_id'),
        ('META/Public-Export-Eligibility-current.csv','candidate_id'),('META/Candidate-Governance-Snapshot-current.csv','candidate_id'),
        ('META/Governance-Review-Queue-current.csv','candidate_id'),('GOVERNANCE/Permission-State-Ledger-current.csv','candidate_id'),
        ('META/Candidate-Boundary-Domain-Map-current.csv','candidate_id'),('META/Office-Accountability-current.csv','candidate_id'),
    ],
    'office_id': [
        ('Office-Card-Index-current.csv','office_id'),('Candidate-Ledger-current.csv','office_ids'),
        ('META/Office-Accountability-current.csv','office_id'),
    ],
    'source_id': [
        ('Source-Registry-current.csv','source_id'),('Candidate-Ledger-current.csv','source_ids'),('Claim-Ledger-current.csv','evidence_source_ids'),
        ('META/Public-Source-Link-Review-current.csv','source_id'),('META/Source-Freshness-Preservation-current.csv','source_id'),
        ('META/Source-Preservation-Status-current.csv','source_id'),
    ],
    'claim_id': [
        ('Claim-Ledger-current.csv','claim_id'),('META/Claim-Evidence-Strength-current.csv','claim_id'),
        ('META/Public-Claim-Quarantine-current.csv','claim_id'),('META/Public-Claim-Release-Ledger-current.csv','claim_id'),
    ],
    'debt_id': [('Evidence-Debt-current.csv','debt_id'),('META/Evidence-Debt-Sprint-current.csv','debt_id')],
    'refresh_id': [('Refresh-Index-current.csv','refresh_id'),('Source-Registry-current.csv','refresh_ids')],
    'boundary_domain_id': [('META/Boundary-Domain-Registry-current.csv','domain_id'),('META/Candidate-Boundary-Domain-Map-current.csv','domain_id')],
    'release_gate_id': [('META/Release-Gate-Attestation-current.csv','gate_id'),('META/Policy-Assertion-Matrix-current.csv','enforced_by_gates'),('META/Selftest-Coverage-Matrix-current.csv','gate_id')],
}

def read_rows(root: Path, rel: str) -> list[dict[str,str]]:
    p=root/rel
    if not p.exists(): return []
    with p.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))

def split_refs(value: str) -> list[str]:
    if value is None: return []
    out=[]
    for piece in str(value).replace(';','|').split('|'):
        piece=piece.strip()
        if piece: out.append(piece)
    return out

def package_files_text(root: Path) -> dict[str,str]:
    out={}
    for p in root.rglob('*'):
        if not p.is_file(): continue
        rel=str(p.relative_to(root)).replace('\\','/')
        if '__pycache__' in rel.split('/') or p.suffix.lower() in {'.pyc','.pyo','.zip','.sig'}:
            continue
        if p.suffix.lower() in {'.csv','.json','.md','.txt'} or p.name in {'manifest.json','datapackage.json'}:
            try: out[rel]=p.read_text(encoding='utf-8', errors='ignore')
            except Exception: pass
    return out

def build_definitions(root: Path):
    definitions=[]
    for kind,spec in NAMESPACES.items():
        rows=read_rows(root, spec['path'])
        for idx,row in enumerate(rows, start=2):
            identifier=row.get(spec['column'],'')
            definitions.append((kind, identifier, spec, row, idx))
    return definitions

def reference_counts(root: Path, definitions):
    counts=defaultdict(int)
    for kind, pairs in REFERENCE_COLUMNS.items():
        for rel,col in pairs:
            for row in read_rows(root, rel):
                for ident in split_refs(row.get(col,'')):
                    counts[(kind, ident)] += 1
    # Also count literal occurrences in front-matter/prose surfaces so text-file-only references do not look orphaned.
    texts=package_files_text(root)
    defined_by_kind=defaultdict(set)
    for kind, identifier, _spec, _row, _idx in definitions:
        if identifier: defined_by_kind[kind].add(identifier)
    blob='\n'.join(texts.values())
    for kind, ids in defined_by_kind.items():
        for ident in ids:
            # Count at most one package-text occurrence beyond tabular references; this is a signal, not a grep report.
            if ident and ident in blob:
                counts[(kind, ident)] += 1
    return counts

def build_registry(root: Path):
    definitions=build_definitions(root)
    counts=reference_counts(root, definitions)
    duplicate_counts=Counter((kind, identifier) for kind,identifier,_spec,_row,_idx in definitions)
    rows=[]
    for kind, identifier, spec, row, idx in definitions:
        pattern=spec['pattern']
        pattern_ok=bool(re.fullmatch(pattern, identifier or ''))
        dup=duplicate_counts[(kind, identifier)]>1
        status='pass' if pattern_ok and not dup and identifier else 'fail'
        note=[]
        if not identifier: note.append('empty identifier')
        if not pattern_ok: note.append('identifier does not match namespace pattern')
        if dup: note.append('duplicate identifier inside namespace')
        if not note: note.append('identifier is defined in its namespace and matches the current pattern')
        rows.append({
            'identifier_kind':kind,
            'identifier':identifier,
            'surface_path':spec['path'],
            'row_locator':f'row {idx}',
            'display_label':row.get(spec['label'],'') or row.get('name','') or row.get('gate_name',''),
            'expected_pattern':pattern,
            'namespace_status':status,
            'reference_count':str(counts.get((kind, identifier),0)),
            'definition_status':'duplicate_definition' if dup else ('defined' if identifier else 'missing_identifier'),
            'note':'; '.join(note),
        })
    return rows

def add(audit, check, severity, status, kind, identifier, surface, detail):
    audit.append({'audit_id':f'identifier_audit_{len(audit)+1:04d}','check':check,'severity':severity,'status':status,'identifier_kind':kind,'identifier':identifier,'surface_path':surface,'detail':detail})

def build_audit(root: Path, registry_rows):
    audit=[]
    # Namespace pattern/duplication checks.
    for kind,spec in NAMESPACES.items():
        rows=[r for r in registry_rows if r['identifier_kind']==kind]
        add(audit,'namespace_has_rows','high','pass' if rows else 'fail',kind,'',spec['path'],f'{len(rows)} definitions observed')
        bad=[r for r in rows if r['namespace_status']!='pass']
        add(audit,'namespace_pattern_and_uniqueness','high','pass' if not bad else 'fail',kind,'',spec['path'],f'bad definitions={len(bad)}')
        ids=[r['identifier'] for r in rows]
        if kind in {'claim_id','debt_id','release_gate_id'} and ids:
            nums=[]
            for ident in ids:
                m=re.search(r'_(\d{3,4})$', ident)
                if m: nums.append(int(m.group(1)))
            contiguous = nums==list(range(min(nums), max(nums)+1)) if nums else True
            add(audit,'numeric_namespace_contiguous','high' if kind=='release_gate_id' else 'medium','pass' if contiguous else 'review',kind,'',spec['path'],f'numeric ids span {min(nums) if nums else 0}..{max(nums) if nums else 0}; count={len(nums)}')
    # Crosslink coherence beyond basic ID existence.
    src_by_id={r.get('source_id',''):r for r in read_rows(root,'Source-Registry-current.csv')}
    candidate_ids={r.get('candidate_id','') for r in read_rows(root,'Candidate-Ledger-current.csv')}
    office_ids={r.get('office_id','') for r in read_rows(root,'Office-Card-Index-current.csv')}
    source_ids=set(src_by_id)
    claim_ids={r.get('claim_id','') for r in read_rows(root,'Claim-Ledger-current.csv')}
    debt_ids={r.get('debt_id','') for r in read_rows(root,'Evidence-Debt-current.csv')}
    boundary_ids={r.get('domain_id','') for r in read_rows(root,'META/Boundary-Domain-Registry-current.csv')}
    gate_ids={r.get('gate_id','') for r in read_rows(root,'META/Release-Gate-Attestation-current.csv')}

    for row in read_rows(root,'Candidate-Ledger-current.csv'):
        cid=row.get('candidate_id','')
        missing_off=[oid for oid in split_refs(row.get('office_ids','')) if oid not in office_ids]
        add(audit,'candidate_office_ids_resolve','high','pass' if not missing_off else 'fail','candidate_id',cid,'Candidate-Ledger-current.csv','missing office ids: '+ '; '.join(missing_off) if missing_off else 'candidate office_ids resolve')
        missing_src=[sid for sid in split_refs(row.get('source_ids','')) if sid not in source_ids]
        add(audit,'candidate_source_ids_resolve','high','pass' if not missing_src else 'fail','candidate_id',cid,'Candidate-Ledger-current.csv','missing source ids: '+ '; '.join(missing_src) if missing_src else 'candidate source_ids resolve')
        bad_back=[]
        for sid in split_refs(row.get('source_ids','')):
            cids=set(split_refs(src_by_id.get(sid,{}).get('candidate_ids','')))
            if sid in src_by_id and cid not in cids: bad_back.append(sid)
        add(audit,'candidate_source_backlinks_include_candidate','high','pass' if not bad_back else 'fail','candidate_id',cid,'Source-Registry-current.csv','source rows missing candidate backlink: '+ '; '.join(bad_back) if bad_back else 'candidate source rows backlink to candidate')

    for row in read_rows(root,'Claim-Ledger-current.csv'):
        cid=row.get('candidate_id',''); claim=row.get('claim_id','')
        add(audit,'claim_candidate_id_resolves','high','pass' if cid in candidate_ids else 'fail','claim_id',claim,'Claim-Ledger-current.csv',f'candidate_id={cid}')
        missing=[sid for sid in split_refs(row.get('evidence_source_ids','')) if sid not in source_ids]
        add(audit,'claim_evidence_sources_resolve','high','pass' if not missing else 'fail','claim_id',claim,'Claim-Ledger-current.csv','missing evidence source ids: '+ '; '.join(missing) if missing else 'claim evidence sources resolve')
        bad=[]
        for sid in split_refs(row.get('evidence_source_ids','')):
            cids=set(split_refs(src_by_id.get(sid,{}).get('candidate_ids','')))
            if sid in src_by_id and cid not in cids: bad.append(sid)
        add(audit,'claim_source_candidate_backlinks_align','high','pass' if not bad else 'fail','claim_id',claim,'Source-Registry-current.csv','source rows not linked to claim candidate: '+ '; '.join(bad) if bad else 'claim evidence sources backlink to the same candidate')

    for row in read_rows(root,'Evidence-Debt-current.csv'):
        cid=row.get('candidate_id',''); debt=row.get('debt_id','')
        add(audit,'debt_candidate_id_resolves','high','pass' if cid in candidate_ids else 'fail','debt_id',debt,'Evidence-Debt-current.csv',f'candidate_id={cid}')
    for row in read_rows(root,'META/Evidence-Debt-Sprint-current.csv'):
        did=row.get('debt_id','')
        add(audit,'evidence_debt_sprint_debt_id_resolves','high','pass' if did in debt_ids else 'fail','debt_id',did,'META/Evidence-Debt-Sprint-current.csv',f'debt_id={did}')
    for row in read_rows(root,'META/Candidate-Boundary-Domain-Map-current.csv'):
        cid=row.get('candidate_id',''); bid=row.get('domain_id','')
        add(audit,'boundary_map_candidate_id_resolves','high','pass' if cid in candidate_ids else 'fail','candidate_id',cid,'META/Candidate-Boundary-Domain-Map-current.csv',f'candidate_id={cid}')
        add(audit,'boundary_map_domain_id_resolves','high','pass' if bid in boundary_ids else 'fail','boundary_domain_id',bid,'META/Candidate-Boundary-Domain-Map-current.csv',f'domain_id={bid}')
    for row in read_rows(root,'META/Policy-Assertion-Matrix-current.csv'):
        pid=row.get('policy_id','') or row.get('assertion_id','')
        missing=[gid for gid in split_refs(row.get('enforced_by_gates','')) if gid.startswith('gate_') and gid not in gate_ids]
        add(audit,'policy_assertion_gate_ids_resolve','high','pass' if not missing else 'fail','release_gate_id',pid,'META/Policy-Assertion-Matrix-current.csv','missing gates: '+ '; '.join(missing) if missing else 'policy assertion gate references resolve')
    # Registry summary.
    high_fail=[r for r in audit if r['severity']=='high' and r['status']!='pass']
    add(audit,'identifier_namespace_audit_summary','info','pass' if not high_fail else 'fail','package','.', 'META/Identifier-Convention-Audit-current.csv', f'high_failures={len(high_fail)}; registry_rows={len(registry_rows)}')
    return audit

def write_field_schema(root: Path, rel: str, fields: list[str], meanings: dict[str,str]):
    rows=[{'field':f,'required':'yes','allowed_values_or_pattern':meanings.get(f,{}).get('allowed','string'),'meaning':meanings.get(f,{}).get('meaning',f)} for f in fields]
    write_csv_json_md_report(root, rel, ['field','required','allowed_values_or_pattern','meaning'], rows, Path(rel).name[:-len('-Fields-current.csv')].replace('-', ' '), 'tools/identifier_namespace_audit.py', columns=['field','required','allowed_values_or_pattern','meaning'])

def write_reports(root: Path, registry_rows, audit_rows):
    write_csv_json_md_report(
        root, 'META/Identifier-Registry-current.csv', REGISTRY_FIELDS, registry_rows,
        'Identifier Registry', 'tools/identifier_namespace_audit.py',
        columns=['identifier_kind','identifier','surface_path','expected_pattern','namespace_status','reference_count','definition_status','note'],
        intro_lines=[
            f'Identifier definitions registered: {len(registry_rows)}',
            f'Non-pass namespace rows: {sum(1 for r in registry_rows if r.get("namespace_status")!="pass")}',
            'This registry makes ID namespaces and crosslinks inspectable without changing candidate/public claims.',
        ],
        max_md_rows=420,
    )
    write_csv_json_md_report(
        root, 'META/Identifier-Convention-Audit-current.csv', AUDIT_FIELDS, audit_rows,
        'Identifier Convention Audit', 'tools/identifier_namespace_audit.py',
        columns=['check','severity','status','identifier_kind','identifier','surface_path','detail'],
        intro_lines=[
            f'High failures: {sum(1 for r in audit_rows if r.get("severity")=="high" and r.get("status")!="pass")}',
            f'Audit rows: {len(audit_rows)}',
            'High failures block handoff; medium review rows preserve visible sequencing debt without loosening public boundaries.',
        ],
        max_md_rows=520,
    )
    write_field_schema(root, 'SCHEMA/Identifier-Registry-Fields-current.csv', REGISTRY_FIELDS, {
        'identifier_kind': {'allowed':'candidate_id|office_id|source_id|claim_id|debt_id|refresh_id|boundary_domain_id|release_gate_id', 'meaning':'namespace/type of identifier'},
        'identifier': {'allowed':'namespace-specific normalized id pattern', 'meaning':'identifier value'},
        'surface_path': {'allowed':'package-relative path', 'meaning':'surface where the identifier is defined'},
        'row_locator': {'allowed':'row N', 'meaning':'human locator for the defining row'},
        'display_label': {'allowed':'free text', 'meaning':'human label for review context'},
        'expected_pattern': {'allowed':'regular expression', 'meaning':'namespace pattern expected for the identifier'},
        'namespace_status': {'allowed':'pass|fail', 'meaning':'whether the definition matches namespace pattern and uniqueness checks'},
        'reference_count': {'allowed':'integer', 'meaning':'approximate count of tabular/text references to the identifier'},
        'definition_status': {'allowed':'defined|duplicate_definition|missing_identifier', 'meaning':'definition status inside the namespace'},
        'note': {'allowed':'free text', 'meaning':'audit note'},
    })
    write_field_schema(root, 'SCHEMA/Identifier-Convention-Audit-Fields-current.csv', AUDIT_FIELDS, {
        'audit_id': {'allowed':'identifier_audit_[0-9]{4}', 'meaning':'stable audit row id'},
        'check': {'allowed':'string', 'meaning':'check name'},
        'severity': {'allowed':'info|medium|high', 'meaning':'finding severity'},
        'status': {'allowed':'pass|review|fail', 'meaning':'finding status'},
        'identifier_kind': {'allowed':'namespace or package', 'meaning':'identifier namespace under test'},
        'identifier': {'allowed':'identifier value or summary token', 'meaning':'identifier or package summary value'},
        'surface_path': {'allowed':'package-relative path', 'meaning':'surface being checked'},
        'detail': {'allowed':'free text', 'meaning':'finding details'},
    })

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve()
    registry=build_registry(root); audit=build_audit(root, registry)
    if args.write_report: write_reports(root, registry, audit)
    high=[r for r in audit if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if high else 'PASS'} identifier namespace audit registry_rows={len(registry)} audit_rows={len(audit)} high={len(high)}")
    for r in high[:20]: print(f"HIGH {r['check']} {r['identifier_kind']} {r['identifier']}: {r['detail']}")
    if args.fail_on_high and high: sys.exit(1)
if __name__=='__main__': main()
