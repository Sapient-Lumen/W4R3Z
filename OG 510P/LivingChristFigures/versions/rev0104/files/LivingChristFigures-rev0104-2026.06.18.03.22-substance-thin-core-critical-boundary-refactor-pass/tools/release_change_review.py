#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, importlib.util, json, re, sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
from lib_cube import write_csv_json_md_report

FIELDS = ['review_id','subject_path','review_check','change_type','review_area','expected_basis','observed_state','review_required','severity','status','note']
CORE_PAYLOAD = {
    'Candidate-Ledger-current.csv','Candidate-Ledger-current.json','Candidate-Ledger-current.md',
    'Claim-Ledger-current.csv','Claim-Ledger-current.json','Claim-Ledger-current.md',
    'Source-Registry-current.csv','Source-Registry-current.json','Source-Registry-current.md',
    'Evidence-Debt-current.csv','Evidence-Debt-current.json','Evidence-Debt-current.md',
    'Office-Card-Index-current.csv','Office-Card-Index-current.json','Office-Card-Index-current.md',
}
SIGNATURE_DOCS = {'SIGNATURE-STATUS-current.md','SIGNATURE-READINESS-current.md'}
EXPECTED_IDENTITY = {'manifest.json','BUILD-PROVENANCE-current.json','datapackage.json','ro-crate-metadata.json','SCHEMA/Package-Release-Contract-current.json','PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json'}


def read_json(path: Path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return None


def read_csv(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))


def artifact_specs(root: Path) -> set[str]:
    tool = root / 'tools/generated_artifact_provenance.py'
    out=set()
    try:
        spec=importlib.util.spec_from_file_location('gap_for_release_change_review', tool)
        mod=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(mod)
        for artifact, _generator, _inputs in getattr(mod, 'ARTIFACTS', []): out.add(str(artifact))
    except Exception:
        for row in read_csv(root/'META/Generated-Artifact-Provenance-current.csv'):
            if row.get('artifact_path'): out.add(row.get('artifact_path',''))
    return out


def current_rev_export(root: Path):
    manifest=read_json(root/'manifest.json') or {}
    return str(manifest.get('revision','')), str(manifest.get('export_name_without_zip','')), manifest


def add(rows, path, check, change_type, area, basis, observed, review_required, severity, status, note):
    rows.append({
        'review_id': f'release_change_{len(rows)+1:04d}',
        'subject_path': path,
        'review_check': check,
        'change_type': change_type,
        'review_area': area,
        'expected_basis': basis,
        'observed_state': observed,
        'review_required': review_required,
        'severity': severity,
        'status': status,
        'note': note,
    })


def classify_path(path: str, change: str, manifest: dict, artifacts: set[str]) -> tuple[str,str,str,str,str]:
    """Return area, expected_basis, review_required, severity, status."""
    new_sets=set(manifest.get('new_refresh_files',[]) or []) | set(manifest.get('new_meta_files',[]) or []) | set(manifest.get('new_other_files',[]) or []) | set(manifest.get('new_candidate_files',[]) or []) | set(manifest.get('new_office_cards',[]) or [])
    if change == 'removed':
        return 'removed_stable_file','no removed stable files expected','yes','high','fail'
    if path in CORE_PAYLOAD:
        return 'core_payload_ledger','core candidate/source/claim/evidence/office payload closed this pass','yes','high','fail'
    if path.startswith('CANDIDATES/') and not Path(path).name.startswith('_REFRESH-'):
        if path in set(manifest.get('new_candidate_files',[]) or []):
            return 'candidate_payload_addition','manifest new_candidate_files','yes','high','fail'
        return 'candidate_payload_unexpected','no candidate payload changes expected','yes','high','fail'
    if path.startswith('CANDIDATES/_REFRESH-'):
        return 'refresh_note', 'manifest new_refresh_files' if path in new_sets else 'historical refresh/index churn', 'yes' if path in new_sets else 'no', 'info', 'pass'
    if path in SIGNATURE_DOCS or re.fullmatch(r'SIGNING-PUBLIC-KEY-rev\d{4}\.pem', path) or path == 'RELEASE-PUBLIC-KEY.asc':
        return 'signature_proof_surface','current revision signature proof correction','yes','info','pass'
    if path in EXPECTED_IDENTITY:
        return 'identity_or_descriptor','revision identity update','yes','info','pass'
    if path.startswith('PUBLIC/'):
        return 'public_boundary_surface','public layer remains closed; identity/boundary text may refresh','yes','info','pass'
    if path.startswith('GOVERNANCE/'):
        return 'governance_surface','governance/reference surface; no public-release permission','yes','info','pass'
    if path.startswith('SCHEMA/'):
        return 'schema_or_contract_surface','schema/field contract update' if path in new_sets or path in artifacts else 'schema contract refresh', 'yes' if path in new_sets or change == 'added' else 'no', 'info', 'pass'
    if path.startswith('META/'):
        if path in artifacts or path in new_sets:
            return 'generated_or_registered_meta_surface','tracked/generated or manifest-listed report surface','yes' if change=='added' else 'no','info','pass'
        if 'Candidate-Discovery-Log-current' in path:
            return 'curated_no_promotion_log','rev0097 no-promotion log row','yes','info','pass'
        return 'meta_audit_or_review_surface','meta proof/report surface; review for churn only','no','info','pass'
    if path.startswith('tools/'):
        return 'tooling_refactor','tool or audit refactor; must remain executable and provenance-covered when generating reports','yes','info','pass'
    if path.startswith('REASONING-NOTE-') or path.startswith('REVISION-SUMMARY-'):
        return 'revision_note','manifest new_other_files/revision note','yes','info','pass'
    if path in {'000-START-HERE.txt','CURRENT-SPINE.md','DATA-CARD-current.md','META/Data-Card-current.md','LivingChristFigures.txt','CUBE-MAP.md','CUBE-RULES.txt'}:
        return 'front_door_current_surface','front-door current text refreshed for the current revision','yes','info','pass'
    if path in new_sets:
        return 'manifest_listed_addition','manifest new file list','yes','info','pass'
    return 'ordinary_stable_surface','stable package surface changed/added; no core payload movement detected by path class','yes' if change=='added' else 'no','info','pass'


def signature_doc_check(root: Path, rows, current_rev: str, manifest: dict):
    key=str(manifest.get('signature_public_key','')) or f'SIGNING-PUBLIC-KEY-{current_rev}.pem'
    stale_rev_re=re.compile(r'\brev\d{4}\b')
    stale_key_re=re.compile(r'SIGNING-PUBLIC-KEY-rev\d{4}\.pem')
    for rel in sorted(SIGNATURE_DOCS):
        p=root/rel
        body=p.read_text(encoding='utf-8', errors='ignore') if p.exists() else ''
        stale_revs=sorted({m.group(0) for m in stale_rev_re.finditer(body) if m.group(0)!=current_rev})
        stale_keys=sorted({m.group(0) for m in stale_key_re.finditer(body) if m.group(0)!=key})
        ok=bool(body) and current_rev in body and key in body and not stale_revs and not stale_keys
        observed='current' if ok else f'missing_or_stale stale_revs={"|".join(stale_revs) or "none"} stale_keys={"|".join(stale_keys) or "none"}'
        add(rows, rel, 'signature_doc_current_revision_and_key', 'proof_check', 'signature_proof_surface', f'{current_rev} and {key}; no non-current rev/key tokens', observed, 'yes', 'high', 'pass' if ok else 'fail', 'signature readiness/status must not advertise any older revision or verification key')


def run(root: Path):
    rows=[]
    current_rev, export, manifest=current_rev_export(root)
    artifacts=artifact_specs(root)
    delta=read_csv(root/'META/Package-Delta-Manifest-current.csv')
    if not delta:
        add(rows,'META/Package-Delta-Manifest-current.csv','delta_manifest_available','missing','release_delta','present','missing','yes','high','fail','release change review requires a package delta manifest')
        return rows
    changed=[r for r in delta if r.get('change_type')!='unchanged']
    for d in changed:
        path=d.get('path','')
        change=d.get('change_type','')
        area,basis,review,severity,status=classify_path(path, change, manifest, artifacts)
        add(rows,path,'delta_row_triage',change,area,basis,f'{change}; previous_size={d.get("previous_size_bytes","")}; current_size={d.get("current_size_bytes","")}',review,severity,status,'changed stable file is classified for reviewer burden and payload-risk triage')
    signature_doc_check(root, rows, current_rev, manifest)
    counts=Counter(r.get('change_type','') for r in changed)
    core_bad=[r for r in rows if r['review_area'].startswith('core_payload') and r['status']!='pass']
    high_bad=[r for r in rows if r['severity']=='high' and r['status']!='pass']
    add(rows,'.','release_change_summary','summary','release_delta',f'current={current_rev}; export={export}',f'changed={len(changed)} added={counts.get("added",0)} modified={counts.get("modified",0)} removed={counts.get("removed",0)} high_failures={len(high_bad)}','yes','info','pass' if not high_bad else 'fail','summary of release-change review; high failures block release through gate_080')
    add(rows,'.','core_payload_change_summary','summary','core_payload','no candidate/source/claim/evidence/office payload changes expected',f'core_payload_blocking_rows={len(core_bad)}','yes','high' if core_bad else 'info','fail' if core_bad else 'pass','core payload changes are intentionally blocked in this relationship-integrity/release-change pass')
    return rows


def write_reports(root: Path, rows):
    bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    write_csv_json_md_report(
        root=root,
        csv_rel='META/Release-Change-Review-current.csv',
        fields=FIELDS,
        rows=rows,
        title='Release Change Review',
        generated_by='tools/release_change_review.py',
        columns=['subject_path','review_check','change_type','review_area','review_required','severity','status','note'],
        intro_lines=[
            f'High failures: {len(bad)}',
            'This report converts raw package-delta rows into reviewer-burden and payload-risk triage. It also checks that signature readiness/status documents identify the current revision and signing key.',
        ],
        max_md_rows=320,
    )


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if bad else 'PASS'} release change review rows={len(rows)} high_fail={len(bad)}")
    for r in bad[:20]: print(f"HIGH {r['subject_path']} {r['review_check']}: {r['note']}")
    if args.fail_on_high and bad: sys.exit(1)

if __name__ == '__main__': main()
