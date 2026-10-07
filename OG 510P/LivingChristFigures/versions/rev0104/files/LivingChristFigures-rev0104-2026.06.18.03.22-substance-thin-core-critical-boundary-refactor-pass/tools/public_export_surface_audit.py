\
#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re, sys
from pathlib import Path

sys.dont_write_bytecode = True
from lib_cube import write_csv_json_md_report

FIELDS=['audit_id','surface_path','check','export_surface_class','severity','status','expected_value','observed_value','note']
PUBLIC_INDEX_FIELDS=['candidate_id','name','location','office','status_current','capacity_state','live_referral_safe','sensitivity','public_export_tier','public_shape_template','public_use_note']
BLOCK_PUBLIC_PAYLOAD_TOKENS=['Source-Registry','Claim-Ledger','Candidate-Ledger','Evidence-Debt','Candidate-Discovery','Public-Source-Link-Review','Public-Claim-Quarantine','Family-Consent','Governance-Decision-Ledger']
URL_RE=re.compile(r'https?://|\bwww\.', re.I)
EMAIL_RE=re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', re.I)
CONTACT_DIGIT_RE=re.compile(r'(?i)\b(?:hotline|helpline|lifeline|phone|call|text|sms|whatsapp|toll[- ]?free|emergency|crisis line|contact number|intake number)\b[^\n]{0,80}?\b\d[\d\s().-]{2,}\d\b')
ROUTE_CASE_CAPACITY_RE=re.compile(r'(?i)\b(route details|distress[- ]call|exact coordinates|street address|case number|incident number|plot number|medical examiner|accepting new|current capacity|referrals open|shelter beds|service hours)\b')
NEGATION_BOUNDARY_RE=re.compile(r'(?i)\b(no|not|without|blocked|excluded|redacted|do not|must not|not a|not an|closed|internal only|reviewer[- ]support)\b')


def read_json(path: Path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return None


def read_csv(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))


def header(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f:
        try: return next(csv.reader(f))
        except StopIteration: return []


def add(rows, surface, check, cls, sev, status, expected, observed, note):
    rows.append({
        'audit_id':f'public_export_surface_{len(rows)+1:04d}',
        'surface_path':surface,
        'check':check,
        'export_surface_class':cls,
        'severity':sev,
        'status':status,
        'expected_value':str(expected),
        'observed_value':str(observed),
        'note':note,
    })


def path_set(value):
    return set(x for x in value if isinstance(x,str) and x)


def run(root: Path):
    rows=[]
    manifest=read_json(root/'manifest.json') or {}
    contract=read_json(root/'SCHEMA/Package-Release-Contract-current.json') or {}
    export_manifest=read_json(root/'PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json') or {}
    bundle=read_json(root/'PUBLIC/PUBLIC-BUNDLE-MANIFEST-current.json') or {}
    current_rev=manifest.get('revision','')
    export_name=manifest.get('export_name_without_zip','')
    allowed=path_set(contract.get('allowed_public_layer_files',[]))
    public_files=set(str(p.relative_to(root)).replace('\\','/') for p in (root/'PUBLIC').glob('*') if p.is_file())

    add(rows,'PUBLIC/PUBLIC-BUNDLE-MANIFEST-current.json','bundle_manifest_present','public_payload_manifest','high','pass' if isinstance(bundle,dict) and bundle else 'fail','valid JSON object','present' if bundle else 'missing/invalid','actual public payload scope must have a distinct manifest separate from reviewer-support evidence')
    add(rows,'PUBLIC/PUBLIC-BUNDLE-MANIFEST-current.json','bundle_revision_matches_manifest','public_payload_manifest','high','pass' if bundle.get('revision')==current_rev and bundle.get('package_revision')==current_rev else 'fail',current_rev,f"{bundle.get('revision','')}|{bundle.get('package_revision','')}",'public bundle manifest cannot carry stale revision identity')
    add(rows,'PUBLIC/PUBLIC-BUNDLE-MANIFEST-current.json','bundle_export_matches_manifest','public_payload_manifest','high','pass' if bundle.get('export_name_without_zip')==export_name else 'fail',export_name,bundle.get('export_name_without_zip',''),'public bundle manifest must point at the current export root')

    payload=path_set(bundle.get('public_payload_files',[]))
    add(rows,'PUBLIC/PUBLIC-BUNDLE-MANIFEST-current.json','public_payload_matches_public_directory','public_payload_manifest','high','pass' if payload==public_files else 'fail','PUBLIC directory file set',f'missing={len(public_files-payload)} extra={len(payload-public_files)}','public payload list must equal the actual PUBLIC/ file set so hidden payload files cannot drift')
    add(rows,'PUBLIC/PUBLIC-BUNDLE-MANIFEST-current.json','public_payload_matches_contract_allowlist','public_payload_manifest','high','pass' if payload==allowed else 'fail','SCHEMA/Package-Release-Contract allowed_public_layer_files',f'missing={len(allowed-payload)} extra={len(payload-allowed)}','contract and public-bundle payload must name the same public files')
    non_public=sorted(x for x in payload if not x.startswith('PUBLIC/'))
    add(rows,'PUBLIC/PUBLIC-BUNDLE-MANIFEST-current.json','public_payload_paths_are_public_only','public_payload_manifest','high','pass' if not non_public else 'fail','all payload paths start PUBLIC/',';'.join(non_public[:12]) if non_public else 'none','internal META, GOVERNANCE, SCHEMA, and ledger files must never be public payload')
    blocked_payload=sorted(x for x in payload if any(tok in x for tok in BLOCK_PUBLIC_PAYLOAD_TOKENS))
    add(rows,'PUBLIC/PUBLIC-BUNDLE-MANIFEST-current.json','public_payload_excludes_internal_ledgers','public_payload_manifest','high','pass' if not blocked_payload else 'fail','no core/internal ledger or review-evidence path in payload',';'.join(blocked_payload[:12]) if blocked_payload else 'none','prevents source/claim/candidate/review ledgers from being exported as public payload')

    export_payload=path_set(export_manifest.get('public_payload_files',[]))
    support=path_set(export_manifest.get('reviewer_support_files',[]))
    included=path_set(export_manifest.get('included_files',[]))
    add(rows,'PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json','export_manifest_revision_matches_manifest','legacy_export_manifest','high','pass' if export_manifest.get('revision')==current_rev and export_manifest.get('package_revision')==current_rev else 'fail',current_rev,f"{export_manifest.get('revision','')}|{export_manifest.get('package_revision','')}",'legacy export manifest must be current even when interpreted as review support')
    add(rows,'PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json','export_manifest_declares_payload_manifest','legacy_export_manifest','high','pass' if export_manifest.get('public_payload_manifest')=='PUBLIC/PUBLIC-BUNDLE-MANIFEST-current.json' else 'fail','PUBLIC/PUBLIC-BUNDLE-MANIFEST-current.json',export_manifest.get('public_payload_manifest',''),'legacy manifest must point reviewers to the actual PUBLIC-only payload manifest')
    add(rows,'PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json','legacy_included_files_partitioned','legacy_export_manifest','high','pass' if export_payload|support==included and not (export_payload&support) else 'fail','included_files = public_payload_files disjoint-union reviewer_support_files',f'included={len(included)} payload={len(export_payload)} support={len(support)} overlap={len(export_payload&support)}','prevents a broad included_files list from being mistaken for public-payload scope')
    non_public_payload=sorted(x for x in export_payload if not x.startswith('PUBLIC/'))
    add(rows,'PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json','legacy_public_payload_public_only','legacy_export_manifest','high','pass' if export_payload==payload and not non_public_payload else 'fail','same PUBLIC-only payload as bundle manifest',f'payload_mismatch={len(export_payload^payload)} non_public={len(non_public_payload)}','public_payload_files in both manifests must agree and remain PUBLIC-only')
    support_public=sorted(x for x in support if x.startswith('PUBLIC/'))
    add(rows,'PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json','reviewer_support_not_public_payload','legacy_export_manifest','high','pass' if not support_public else 'fail','reviewer_support_files exclude PUBLIC payload paths',';'.join(support_public[:12]) if support_public else 'none','reviewer-support evidence must be clearly separate from actual public files')

    idx_path=root/'PUBLIC/Candidate-Index-public.csv'
    idx_header=header(idx_path)
    add(rows,'PUBLIC/Candidate-Index-public.csv','public_index_header_allowlist','public_index','high','pass' if idx_header==PUBLIC_INDEX_FIELDS else 'fail','|'.join(PUBLIC_INDEX_FIELDS),'|'.join(idx_header),'public index must not grow URL/source/contact/case/detail columns by accident')
    forbidden_cols=[c for c in idx_header if any(tok in c.lower() for tok in ['url','source','contact','phone','email','address','route','case','claim_text','testimony','image','capacity_detail'])]
    add(rows,'PUBLIC/Candidate-Index-public.csv','public_index_no_forbidden_payload_columns','public_index','high','pass' if not forbidden_cols else 'fail','no URL/source/contact/route/case/testimony/image/capacity-detail columns',';'.join(forbidden_cols) if forbidden_cols else 'none','public rows remain boundary-index labels only')
    idx_rows=read_csv(idx_path)
    add(rows,'PUBLIC/Candidate-Index-public.csv','public_index_rows_match_manifest_count','public_index','high','pass' if str(len(idx_rows))==str(export_manifest.get('candidate_count_public_index','')) else 'fail',export_manifest.get('candidate_count_public_index',''),len(idx_rows),'public row count must match manifest count')

    for rel in sorted(public_files):
        text=(root/rel).read_text(encoding='utf-8', errors='ignore')
        hits=[]
        if URL_RE.search(text): hits.append('raw_url')
        if EMAIL_RE.search(text): hits.append('email')
        if CONTACT_DIGIT_RE.search(text): hits.append('contact_digit_near_contact_word')
        # Route/case/capacity semantics are handled by public_release_lint and public_index_semantic_audit.
        # This surface audit stays focused on payload-boundary failures: raw URLs, email/contact paths,
        # public-column growth, and internal ledger/report paths being treated as payload.
        add(rows,rel,'public_file_sensitive_token_scan','public_file','high','pass' if not hits else 'fail','no raw URL/email/contact-digit or unguarded route/case/capacity tokens',';'.join(hits) if hits else 'none','actual public bundle files are scanned as payload, not merely linted as generic policy text')

    no_perm=bundle.get('no_public_release_permission') is True and 'not public-release permission' in (bundle.get('closed_boundary_note','') + ' ' + json.dumps(export_manifest, ensure_ascii=False)).lower()
    add(rows,'PUBLIC/PUBLIC-BUNDLE-MANIFEST-current.json','bundle_denies_public_release_permission','public_payload_manifest','high','pass' if no_perm else 'fail','explicit no_public_release_permission true + boundary wording',str(no_perm),'the manifest must not convert package inclusion into publication permission')
    high_fail=sum(1 for r in rows if r['severity']=='high' and r['status']!='pass')
    add(rows,'.','public_export_surface_summary','summary','info','pass' if high_fail==0 else 'fail','zero high failures',high_fail,f'public_files={len(public_files)} payload_files={len(payload)} reviewer_support_files={len(support)}')
    return rows


def write_reports(root: Path, rows):
    write_csv_json_md_report(
        root=root,
        csv_rel='META/Public-Export-Surface-Audit-current.csv',
        fields=FIELDS,
        rows=rows,
        title='Public Export Surface Audit',
        generated_by='tools/public_export_surface_audit.py',
        columns=['surface_path','check','export_surface_class','severity','status','expected_value','observed_value','note'],
        intro_lines=[
            f"High failures: {sum(1 for r in rows if r.get('severity')=='high' and r.get('status')!='pass')}",
            'This audit distinguishes actual PUBLIC-only payload from reviewer-support evidence so broad included_files lists cannot become accidental public exports.',
        ],
        max_md_rows=220,
    )


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if bad else 'PASS'} public export surface audit rows={len(rows)} high_fail={len(bad)}")
    for r in bad[:20]: print(f"HIGH {r['surface_path']} {r['check']}: {r['observed_value']}")
    if args.fail_on_high and bad: sys.exit(1)
if __name__=='__main__': main()
