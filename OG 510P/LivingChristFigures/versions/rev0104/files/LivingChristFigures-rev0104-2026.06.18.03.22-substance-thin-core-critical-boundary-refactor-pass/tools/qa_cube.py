#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, importlib.util, json, os, re, sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


def read(p): return p.read_text(encoding='utf-8')


def has_frontmatter(p: Path) -> bool:
    txt = read(p)
    return txt.startswith('---\n') and '\n---\n' in txt[4:5000]


def parse_frontmatter(p: Path) -> dict[str, str]:
    txt = read(p)
    m = re.match(r'^---\n(.*?)\n---\n', txt, re.S)
    if not m:
        return {}
    out = {}
    current_key = None
    current_list = []
    for raw in m.group(1).splitlines():
        line = raw.rstrip()
        if line.startswith('  - '):
            if current_key:
                val = line[4:].strip().strip('"').replace('\\"', '"')
                current_list.append(val)
            continue
        if current_key and current_list:
            out[current_key] = '|'.join(current_list)
            current_key, current_list = None, []
        if ':' in line:
            k, v = line.split(':', 1)
            k = k.strip(); v = v.strip()
            if v == '':
                current_key = k; current_list = []
            else:
                out[k] = v.strip('"').replace('\\"', '"')
    if current_key and current_list:
        out[current_key] = '|'.join(current_list)
    return out


def csv_rows(root: Path, rel: str):
    p = root / rel
    if not p.exists():
        return []
    return list(csv.DictReader(p.open(encoding='utf-8')))


def _stable_checksum_files(root: Path) -> list[str]:
    files=[]
    for p in root.rglob('*'):
        if not p.is_file():
            continue
        rel=str(p.relative_to(root)).replace('\\','/')
        parts=rel.split('/')
        if rel in {'SHA256SUMS.txt','SHA256SUMS.txt.sig','QA-REPORT-current.txt'}:
            continue
        if p.suffix.lower()=='.zip':
            continue
        if '__pycache__' in parts or p.suffix.lower() in {'.pyc','.pyo'}:
            continue
        files.append(rel)
    return sorted(files)


def sha_check(root: Path):
    path=root/'SHA256SUMS.txt'
    if not path.exists(): return False, ['SHA256SUMS.txt missing']
    bad=[]; checked=0; observed=[]
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip(): continue
        try: digest, rel=line.split(None,1)
        except ValueError:
            bad.append(f'malformed line: {line[:80]}'); continue
        rel=rel.strip()
        if rel.startswith('./'): rel=rel[2:]
        observed.append(rel)
        f=root/rel
        if not f.exists(): bad.append(f'missing file in checksum: {rel}'); continue
        got=hashlib.sha256(f.read_bytes()).hexdigest()
        checked+=1
        if got!=digest: bad.append(f'checksum mismatch: {rel}')
    expected=_stable_checksum_files(root)
    missing=sorted(set(expected)-set(observed))
    extra=sorted(set(observed)-set(expected))
    dup=sorted({rel for rel in observed if observed.count(rel)>1})
    if missing:
        bad.append('SHA256SUMS missing stable files: ' + '; '.join(missing[:12]))
    if extra:
        bad.append('SHA256SUMS has entries outside stable package scope: ' + '; '.join(extra[:12]))
    if dup:
        bad.append('SHA256SUMS has duplicate paths: ' + '; '.join(dup[:12]))
    if observed != sorted(observed):
        bad.append('SHA256SUMS entries are not sorted lexicographically')
    return not bad, [f'checked {checked} files; expected stable files {len(expected)}'] + bad


def public_safe_identity_label(label: str) -> str:
    contact_context = re.compile(r'(?i)\b(hotline|helpline|lifeline|phone|call|text|sms|whatsapp|toll[- ]?free|emergency|crisis line|contact number|intake number)\b')
    contact_digits = re.compile(r'\b\d[\d\s().-]{2,}\d\b')
    if contact_context.search(label or ''):
        return contact_digits.sub('[public contact digits redacted]', label)
    return label


def identity_checks(root: Path):
    messages=[]
    ok=True
    cand_files=[p for p in (root/'CANDIDATES').glob('*.txt') if not p.name.startswith('_REFRESH')]
    fms={}
    for p in cand_files:
        fm=parse_frontmatter(p)
        cid=fm.get('candidate_id')
        if cid:
            fms[cid] = {'frontmatter': fm, 'path': str(p.relative_to(root))}
    cand_rows={r.get('candidate_id'): r for r in csv_rows(root,'Candidate-Ledger-current.csv')}
    missing_in_ledger=sorted(set(fms)-set(cand_rows))
    missing_files=sorted(set(cand_rows)-set(fms))
    if missing_in_ledger or missing_files:
        ok=False; messages.append(f'id set mismatch: missing_in_ledger={len(missing_in_ledger)} missing_files={len(missing_files)}')
    names=[r.get('name','') for r in cand_rows.values()]
    dup=[name for name,c in Counter(names).items() if name and c>1]
    if dup:
        ok=False; messages.append('duplicate candidate names: ' + '; '.join(dup[:5]))
    for cid, pack in fms.items():
        row=cand_rows.get(cid)
        if not row: continue
        fm=pack['frontmatter']
        for field in ['name','location','status_current','verification_state','capacity_state','source_use_scope']:
            if row.get(field,'') != fm.get(field,''):
                ok=False; messages.append(f'{cid}: Candidate-Ledger {field} disagrees with front matter')
        if row.get('file_path','') != pack['path']:
            ok=False; messages.append(f'{cid}: Candidate-Ledger file_path disagrees with actual path')
        # normalize boolean front matter against CSV string
        fm_lrs = fm.get('live_referral_safe','').lower()
        if row.get('live_referral_safe','') != fm_lrs:
            ok=False; messages.append(f'{cid}: live_referral_safe disagrees with front matter')
    id_to_name={cid:r.get('name','') for cid,r in cand_rows.items()}
    for rel in ['Claim-Ledger-current.csv','Evidence-Debt-current.csv','PUBLIC/Candidate-Index-public.csv']:
        for r in csv_rows(root, rel):
            cid=r.get('candidate_id')
            if cid in id_to_name:
                observed = r.get('candidate_name', r.get('name',''))
                allowed = {id_to_name[cid]}
                if rel.startswith('PUBLIC/'):
                    allowed.add(public_safe_identity_label(id_to_name[cid]))
                if observed not in allowed:
                    ok=False; messages.append(f'{rel}: {cid} display name disagrees with Candidate-Ledger/public-safe identity label')
    # Candidate-Index markdown and CUBE-MAP labels must agree with Candidate-Ledger labels.
    for rel in ['Candidate-Index-current.md','CUBE-MAP.md']:
        p=root/rel
        if not p.exists(): continue
        for line in p.read_text(encoding='utf-8').splitlines():
            m=re.search(r'`?(cand_[a-z0-9_]+)`?\s*\|\s*([^|]+)\s*\|', line)
            if rel == 'CUBE-MAP.md':
                m=re.search(r'`(cand_[^`]+)`\s+—\s+(.+)$', line)
            if m:
                cid=m.group(1); label=m.group(2).strip()
                if cid in id_to_name and label != id_to_name[cid]:
                    ok=False; messages.append(f'{rel}: {cid} label disagrees with Candidate-Ledger')
    if not messages:
        messages.append(f'candidate identity labels coherent across {len(cand_rows)} candidates')
    return ok, messages



def reference_integrity_checks(root: Path):
    messages=[]; ok=True
    cand_rows=csv_rows(root,'Candidate-Ledger-current.csv')
    office_rows=csv_rows(root,'Office-Card-Index-current.csv')
    claim_rows=csv_rows(root,'Claim-Ledger-current.csv')
    src_rows=csv_rows(root,'Source-Registry-current.csv')
    debt_rows=csv_rows(root,'Evidence-Debt-current.csv')
    refresh_rows=csv_rows(root,'Refresh-Index-current.csv')
    cand_ids=[r.get('candidate_id','') for r in cand_rows]
    cand_id_set=set(cand_ids)
    dup_cids=[cid for cid,c in Counter(cand_ids).items() if cid and c>1]
    if dup_cids:
        ok=False; messages.append('duplicate candidate_ids: ' + '; '.join(dup_cids[:5]))
    src_ids=[r.get('source_id','') for r in src_rows]
    src_id_set=set(src_ids)
    dup_src=[sid for sid,c in Counter(src_ids).items() if sid and c>1]
    if dup_src:
        ok=False; messages.append('duplicate source_ids: ' + '; '.join(dup_src[:5]))
    office_ids={r.get('office_id','') for r in office_rows}
    missing_off=[]
    for r in cand_rows:
        for oid in (r.get('office_ids','') or '').split('|'):
            if oid and oid not in office_ids:
                missing_off.append(f"{r.get('candidate_id')}->{oid}")
    if missing_off:
        ok=False; messages.append('candidate office_ids missing office cards: ' + '; '.join(missing_off[:5]))
    # Candidate front-matter office IDs must match candidate-ledger office IDs.
    for p in (root/'CANDIDATES').glob('*.txt'):
        if p.name.startswith('_REFRESH'): continue
        fm=parse_frontmatter(p); cid=fm.get('candidate_id')
        if not cid: continue
        row=next((r for r in cand_rows if r.get('candidate_id')==cid), None)
        if not row: continue
        fm_off=set((fm.get('office_ids','') or '').split('|')) - {''}
        row_off=set((row.get('office_ids','') or '').split('|')) - {''}
        if fm_off != row_off:
            ok=False; messages.append(f'{cid}: front-matter office_ids disagree with Candidate-Ledger')
    missing_src=[]
    for r in claim_rows:
        for sid in (r.get('evidence_source_ids','') or '').split('|'):
            if sid and sid not in src_id_set:
                missing_src.append(f"{r.get('claim_id')}->{sid}")
    if missing_src:
        ok=False; messages.append('claim source ids missing from Source-Registry: ' + '; '.join(missing_src[:5]))
    missing_cand_src=[]
    for r in cand_rows:
        for sid in (r.get('source_ids','') or '').split('|'):
            if sid and sid not in src_id_set:
                missing_cand_src.append(f"{r.get('candidate_id')}->{sid}")
    if missing_cand_src:
        ok=False; messages.append('candidate source_ids missing from Source-Registry: ' + '; '.join(missing_cand_src[:5]))
    bad_source_cids=[]
    for r in src_rows:
        for cid in (r.get('candidate_ids','') or '').split('|'):
            if cid and cid not in cand_id_set:
                bad_source_cids.append(f"{r.get('source_id')}->{cid}")
    if bad_source_cids:
        ok=False; messages.append('Source-Registry candidate_ids missing from Candidate-Ledger: ' + '; '.join(bad_source_cids[:5]))
    bad_debt_cids=[r.get('candidate_id') for r in debt_rows if r.get('candidate_id') and r.get('candidate_id') not in cand_id_set]
    if bad_debt_cids:
        ok=False; messages.append('Evidence-Debt candidate_ids missing from Candidate-Ledger: ' + '; '.join(bad_debt_cids[:5]))
    bad_refresh_cids=[]
    for r in refresh_rows:
        for cid in (r.get('related_candidate_ids','') or '').split('|'):
            if cid and cid not in cand_id_set:
                bad_refresh_cids.append(f"{r.get('refresh_id')}->{cid}")
    if bad_refresh_cids:
        ok=False; messages.append('Refresh-Index related_candidate_ids missing from Candidate-Ledger: ' + '; '.join(bad_refresh_cids[:5]))
    missing_seen=[]
    for r in src_rows:
        for rel in (r.get('seen_in_files','') or '').split('|'):
            if rel and not (root/rel).exists():
                missing_seen.append(f"{r.get('source_id')}->{rel}")
    if missing_seen:
        ok=False; messages.append('Source-Registry seen_in_files missing: ' + '; '.join(missing_seen[:5]))
    if not messages:
        messages.append('candidate, office, source, debt, refresh, and seen-in-file references are coherent')
    return ok, messages



def manifest_truth_checks(root: Path):
    messages=[]; ok=True
    p=root/'manifest.json'
    if not p.exists():
        return False, ['manifest.json missing']
    try:
        m=json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:
        return False, [f'manifest.json not valid JSON: {e}']
    def count_csv(rel):
        return len(csv_rows(root, rel))
    expected={
        'candidate_count': len([p for p in (root/'CANDIDATES').glob('*.txt') if not p.name.startswith('_REFRESH')]),
        'office_card_count': len(list((root/'OFFICE-CARDS').glob('*.txt'))),
        'refresh_note_count': len(list((root/'CANDIDATES').glob('_REFRESH*.txt'))),
        'claim_count': count_csv('Claim-Ledger-current.csv'),
        'source_registry_count': count_csv('Source-Registry-current.csv'),
        'evidence_debt_count': count_csv('Evidence-Debt-current.csv'),
        'longform_track_count': count_csv('Longform-Registry-current.csv'),
    }
    for k,v in expected.items():
        if str(m.get(k,'')) != str(v):
            ok=False; messages.append(f'{k} manifest={m.get(k)} actual={v}')
    rev=m.get('revision','')
    exp=m.get('export_name_without_zip','')
    if rev and rev not in exp:
        ok=False; messages.append(f'revision {rev} not present in export_name_without_zip')
    if m.get('archive_zips_bundled_in_this_export') is not False:
        ok=False; messages.append('archive_zips_bundled_in_this_export must be false')
    if not messages:
        messages.append('manifest counts, revision identity, and archive posture match package state')
    return ok, messages


def longform_registry_checks(root: Path):
    messages=[]; ok=True
    rows=csv_rows(root,'Longform-Registry-current.csv')
    tids=[r.get('track_id','') for r in rows]
    dup=[tid for tid,c in Counter(tids).items() if tid and c>1]
    if dup:
        ok=False; messages.append('duplicate longform track_id: ' + '; '.join(dup[:5]))
    json_path=root/'Longform-Registry-current.json'
    if json_path.exists():
        try:
            data=json.loads(json_path.read_text(encoding='utf-8'))
            if len(data)!=len(rows):
                ok=False; messages.append(f'Longform JSON row count {len(data)} != CSV row count {len(rows)}')
        except Exception as e:
            ok=False; messages.append(f'Longform JSON invalid: {e}')
    missing_seed=[]
    for r in rows:
        for rel in (r.get('seed_files','') or '').split('|'):
            if not rel or '*' in rel: continue
            if not (root/rel).exists():
                missing_seed.append(f"{r.get('track_id')}->{rel}")
    if missing_seed:
        ok=False; messages.append('Longform seed files missing: ' + '; '.join(missing_seed[:5]))
    if not messages:
        messages.append(f'longform registry has {len(rows)} unique tracks and existing concrete seed files')
    return ok, messages


def meta_instrument_checks(root: Path):
    messages=[]; ok=True
    required=[
        'META/README-meta-instruments-current.md',
        'META/Operator-Dissent-Ledger-current.csv','META/Operator-Dissent-Ledger-current.json','META/Operator-Dissent-Ledger-current.md',
        'META/Manifest-Audit-current.csv','META/Manifest-Audit-current.json','META/Manifest-Audit-current.md',
        'META/Source-Freshness-and-Provenance-Audit-current.csv','META/Source-Freshness-and-Provenance-Audit-current.json','META/Source-Freshness-and-Provenance-Audit-current.md',
        'META/Claim-Type-Taxonomy-current.csv','META/Claim-Type-Taxonomy-current.json','META/Claim-Type-Taxonomy-current.md',
        'META/Evidence-Debt-Dashboard-current.csv','META/Evidence-Debt-Dashboard-current.json','META/Evidence-Debt-Dashboard-current.md',
        'META/Boundary-Rule-Coverage-current.csv','META/Boundary-Rule-Coverage-current.json','META/Boundary-Rule-Coverage-current.md',
        'META/Public-Export-Checklist-current.md','META/Update-Behavior-Gate-current.md','META/MetaPass-Roadmap-current.md',
        'META/Redaction-Risk-Scan-current.csv','META/Redaction-Risk-Scan-current.json','META/Redaction-Risk-Scan-current.md',
        'META/Redaction-Risk-Open-Findings-current.csv','META/Redaction-Risk-Open-Findings-current.json','META/Redaction-Risk-Open-Findings-current.md',
        'META/Rule46-Scan-current.csv','META/Rule46-Scan-current.json','META/Rule46-Scan-current.md',
        'META/Claim-Evidence-Strength-current.csv','META/Claim-Evidence-Strength-current.json','META/Claim-Evidence-Strength-current.md',
        'META/Refresh-Priority-Queue-current.csv','META/Refresh-Priority-Queue-current.json','META/Refresh-Priority-Queue-current.md',
        'META/Evidence-Lifecycle-Policy-current.md',
        'META/Negative-Case-Ledger-current.csv','META/Negative-Case-Ledger-current.json','META/Negative-Case-Ledger-current.md',
        'META/Online-Research-Intake-current.csv','META/Online-Research-Intake-current.json','META/Online-Research-Intake-current.md',
        'META/Operator-Update-Audit-current.csv','META/Operator-Update-Audit-current.json','META/Operator-Update-Audit-current.md',
        'META/Source-Promotion-Decision-Ledger-current.csv','META/Source-Promotion-Decision-Ledger-current.json','META/Source-Promotion-Decision-Ledger-current.md',
        'META/Public-Claim-Quarantine-current.csv','META/Public-Claim-Quarantine-current.json','META/Public-Claim-Quarantine-current.md',
        'META/Refresh-Sprint-Decision-Matrix-current.csv','META/Refresh-Sprint-Decision-Matrix-current.json','META/Refresh-Sprint-Decision-Matrix-current.md',
        'META/Source-Promotion-Transaction-Audit-current.csv','META/Source-Promotion-Transaction-Audit-current.json','META/Source-Promotion-Transaction-Audit-current.md',
        'META/Public-Claim-Release-Ledger-current.csv','META/Public-Claim-Release-Ledger-current.json','META/Public-Claim-Release-Ledger-current.md',
        'META/Public-Export-Eligibility-current.csv','META/Public-Export-Eligibility-current.json','META/Public-Export-Eligibility-current.md',
        'META/Public-Source-Link-Review-current.csv','META/Public-Source-Link-Review-current.json','META/Public-Source-Link-Review-current.md',
        'META/Public-Release-Lint-current.csv','META/Public-Release-Lint-current.json','META/Public-Release-Lint-current.md',
        'META/Sensitive-Surface-Inventory-current.csv','META/Sensitive-Surface-Inventory-current.json','META/Sensitive-Surface-Inventory-current.md',
        'META/Candidate-Governance-Snapshot-current.csv','META/Candidate-Governance-Snapshot-current.json','META/Candidate-Governance-Snapshot-current.md',
        'META/Governance-Review-Queue-current.csv','META/Governance-Review-Queue-current.json','META/Governance-Review-Queue-current.md',
        'META/Generated-Artifact-Provenance-current.csv','META/Generated-Artifact-Provenance-current.json','META/Generated-Artifact-Provenance-current.md',
        'META/Revision-Surface-Audit-current.csv','META/Revision-Surface-Audit-current.json','META/Revision-Surface-Audit-current.md',
        'META/Release-Gate-Attestation-current.csv','META/Release-Gate-Attestation-current.json','META/Release-Gate-Attestation-current.md',
        'META/Public-Index-Parity-current.csv','META/Public-Index-Parity-current.json','META/Public-Index-Parity-current.md',
        'META/Governance-Consistency-Audit-current.csv','META/Governance-Consistency-Audit-current.json','META/Governance-Consistency-Audit-current.md',
        'META/Package-Dependency-Graph-current.csv','META/Package-Dependency-Graph-current.json','META/Package-Dependency-Graph-current.md',
        'META/Field-Schema-Consistency-Audit-current.csv','META/Field-Schema-Consistency-Audit-current.json','META/Field-Schema-Consistency-Audit-current.md',
        'META/Path-Reference-Audit-current.csv','META/Path-Reference-Audit-current.json','META/Path-Reference-Audit-current.md',
        'META/Rule-Gate-Traceability-current.csv','META/Rule-Gate-Traceability-current.json','META/Rule-Gate-Traceability-current.md',
        'META/Tool-Run-Matrix-current.csv','META/Tool-Run-Matrix-current.json','META/Tool-Run-Matrix-current.md',
        'META/Required-Document-Coverage-current.csv','META/Required-Document-Coverage-current.json','META/Required-Document-Coverage-current.md',
        'META/Audit-Selftest-current.csv','META/Audit-Selftest-current.json','META/Audit-Selftest-current.md',
        'META/Rebuild-Readiness-Audit-current.csv','META/Rebuild-Readiness-Audit-current.json','META/Rebuild-Readiness-Audit-current.md',
        'META/Policy-Assertion-Matrix-current.csv','META/Policy-Assertion-Matrix-current.json','META/Policy-Assertion-Matrix-current.md',
        'META/Regeneration-Sequence-Plan-current.csv','META/Regeneration-Sequence-Plan-current.json','META/Regeneration-Sequence-Plan-current.md',
        'META/Archive-Build-Manifest-current.csv','META/Archive-Build-Manifest-current.json','META/Archive-Build-Manifest-current.md',
        'META/Selftest-Coverage-Matrix-current.csv','META/Selftest-Coverage-Matrix-current.json','META/Selftest-Coverage-Matrix-current.md',
        'META/Checksum-Scope-Audit-current.csv','META/Checksum-Scope-Audit-current.json','META/Checksum-Scope-Audit-current.md',
        'META/Public-Negative-Corpus-current.csv','META/Public-Negative-Corpus-current.json','META/Public-Negative-Corpus-current.md',
        'META/Release-Evidence-Closure-current.csv','META/Release-Evidence-Closure-current.json','META/Release-Evidence-Closure-current.md',
        'META/Version-Lineage-Audit-current.csv','META/Version-Lineage-Audit-current.json','META/Version-Lineage-Audit-current.md',
        'META/Package-Delta-Manifest-current.csv','META/Package-Delta-Manifest-current.json','META/Package-Delta-Manifest-current.md',
        'META/Cross-Report-Reference-Audit-current.csv','META/Cross-Report-Reference-Audit-current.json','META/Cross-Report-Reference-Audit-current.md',
        'META/Handoff-Review-Digest-current.csv','META/Handoff-Review-Digest-current.json','META/Handoff-Review-Digest-current.md',
        'META/Dependency-Cycle-Audit-current.csv','META/Dependency-Cycle-Audit-current.json','META/Dependency-Cycle-Audit-current.md',
        'META/Handoff-Notice-Audit-current.csv','META/Handoff-Notice-Audit-current.json','META/Handoff-Notice-Audit-current.md',
        'META/Current-Surface-Registry-current.csv','META/Current-Surface-Registry-current.json','META/Current-Surface-Registry-current.md',
        'META/Manifest-Semantic-Coherence-Audit-current.csv','META/Manifest-Semantic-Coherence-Audit-current.json','META/Manifest-Semantic-Coherence-Audit-current.md',
        'META/JSON-Key-Uniqueness-Audit-current.csv','META/JSON-Key-Uniqueness-Audit-current.json','META/JSON-Key-Uniqueness-Audit-current.md',
        'META/Review-Role-Boundary-Audit-current.csv','META/Review-Role-Boundary-Audit-current.json','META/Review-Role-Boundary-Audit-current.md',
        'META/Tool-Executability-Audit-current.csv','META/Tool-Executability-Audit-current.json','META/Tool-Executability-Audit-current.md',
        'META/Boundary-Domain-Registry-current.csv','META/Boundary-Domain-Registry-current.json','META/Boundary-Domain-Registry-current.md',
        'META/Candidate-Boundary-Domain-Map-current.csv','META/Candidate-Boundary-Domain-Map-current.json','META/Candidate-Boundary-Domain-Map-current.md',
        'META/Boundary-Domain-Coverage-Audit-current.csv','META/Boundary-Domain-Coverage-Audit-current.json','META/Boundary-Domain-Coverage-Audit-current.md'
    ]
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing:
        ok=False; messages.append('missing meta files: ' + '; '.join(missing[:8]))
    op_rows=csv_rows(root,'META/Operator-Dissent-Ledger-current.csv')
    op_required={'dissent_id','date_logged','challenged_claim_or_pattern','behavior_change_required','status','public_export_safe'}
    if op_rows:
        missing_cols=op_required-set(op_rows[0].keys())
        if missing_cols:
            ok=False; messages.append('Operator-Dissent missing columns: ' + ','.join(sorted(missing_cols)))
        dup=[x for x,c in Counter(r.get('dissent_id','') for r in op_rows).items() if x and c>1]
        if dup:
            ok=False; messages.append('duplicate dissent_id: ' + '; '.join(dup[:5]))
        no_behavior=[r.get('dissent_id') for r in op_rows if not r.get('behavior_change_required')]
        if no_behavior:
            ok=False; messages.append('dissent rows missing behavior_change_required: ' + '; '.join(no_behavior[:5]))
    claim_types={r.get('claim_type','') for r in csv_rows(root,'Claim-Ledger-current.csv') if r.get('claim_type','')}
    tax_types={r.get('claim_type','') for r in csv_rows(root,'META/Claim-Type-Taxonomy-current.csv') if r.get('claim_type','')}
    missing_tax=sorted(claim_types-tax_types)
    if missing_tax:
        ok=False; messages.append('claim taxonomy missing claim types: ' + '; '.join(missing_tax[:8]))
    src_count=len(csv_rows(root,'Source-Registry-current.csv'))
    src_audit_count=len(csv_rows(root,'META/Source-Freshness-and-Provenance-Audit-current.csv'))
    if src_count!=src_audit_count:
        ok=False; messages.append(f'source provenance audit row count {src_audit_count} != Source-Registry row count {src_count}')
    boundary_rows=csv_rows(root,'META/Boundary-Rule-Coverage-current.csv')
    got_rules={r.get('rule_number','') for r in boundary_rows}
    for rn in [str(n) for n in range(15,93)]:
        if rn not in got_rules:
            ok=False; messages.append(f'Boundary-Rule-Coverage missing rule {rn}')
    incomplete=[r.get('rule_number','') for r in boundary_rows if r.get('rule_number','').isdigit() and 15 <= int(r.get('rule_number','')) <= 92 and any(not (r.get(c,'') or '').strip() for c in ['rule_name','trigger_subjects','candidate_sensitivity_signals','required_boundary_action','qa_status'])]
    if incomplete:
        ok=False; messages.append('Boundary-Rule-Coverage incomplete rows: ' + '; '.join(incomplete[:8]))
    neg_rows=csv_rows(root,'META/Negative-Case-Ledger-current.csv')
    if neg_rows:
        neg_required={'negative_case_id','case_type','decision','current_status','behavior_change','public_export_safe'}
        missing_cols=neg_required-set(neg_rows[0].keys())
        if missing_cols:
            ok=False; messages.append('Negative-Case-Ledger missing columns: ' + ','.join(sorted(missing_cols)))
        dup=[x for x,c in Counter(r.get('negative_case_id','') for r in neg_rows).items() if x and c>1]
        if dup:
            ok=False; messages.append('duplicate negative_case_id: ' + '; '.join(dup[:5]))
        no_behavior=[r.get('negative_case_id') for r in neg_rows if not r.get('behavior_change')]
        if no_behavior:
            ok=False; messages.append('negative-case rows missing behavior_change: ' + '; '.join(no_behavior[:5]))
    else:
        ok=False; messages.append('Negative-Case-Ledger has no rows')
    intake_rows=csv_rows(root,'META/Online-Research-Intake-current.csv')
    if intake_rows:
        intake_required={'intake_id','url','source_role','intake_status','what_it_supports','what_it_does_not_support','safety_caution'}
        missing_cols=intake_required-set(intake_rows[0].keys())
        if missing_cols:
            ok=False; messages.append('Online-Research-Intake missing columns: ' + ','.join(sorted(missing_cols)))
        dup=[x for x,c in Counter(r.get('intake_id','') for r in intake_rows).items() if x and c>1]
        if dup:
            ok=False; messages.append('duplicate online intake_id: ' + '; '.join(dup[:5]))
        promoted=[r.get('intake_id') for r in intake_rows if r.get('intake_status') not in {'not_promoted_to_source_registry','promoted_to_source_registry'}]
        if promoted:
            ok=False; messages.append('online intake rows with unknown status: ' + '; '.join(promoted[:5]))
    else:
        ok=False; messages.append('Online-Research-Intake has no rows')
    decision_rows=csv_rows(root,'META/Source-Promotion-Decision-Ledger-current.csv')
    if decision_rows:
        decision_required={'decision_id','intake_id','promote_to_source_registry','promotion_decision','operator_veto_effect','claim_effect','public_export_effect'}
        missing_cols=decision_required-set(decision_rows[0].keys())
        if missing_cols:
            ok=False; messages.append('Source-Promotion-Decision-Ledger missing columns: ' + ','.join(sorted(missing_cols)))
        dup=[x for x,c in Counter(r.get('decision_id','') for r in decision_rows).items() if x and c>1]
        if dup:
            ok=False; messages.append('duplicate source-promotion decision_id: ' + '; '.join(dup[:5]))
        intake_ids={r.get('intake_id','') for r in intake_rows}
        decision_intake_ids={r.get('intake_id','') for r in decision_rows}
        if intake_ids != decision_intake_ids:
            ok=False; messages.append(f'source-promotion intake coverage mismatch: intake_only={len(intake_ids-decision_intake_ids)} decision_only={len(decision_intake_ids-intake_ids)}')
        bad_bool=[r.get('decision_id') for r in decision_rows if r.get('promote_to_source_registry') not in {'yes','no','true','false'}]
        if bad_bool:
            ok=False; messages.append('source-promotion promote_to_source_registry not boolean-like: ' + '; '.join(bad_bool[:5]))
        if not any(r.get('operator_veto_effect') in {'true','yes'} for r in decision_rows):
            ok=False; messages.append('Source-Promotion-Decision-Ledger has no operator_veto_effect rows')
    else:
        ok=False; messages.append('Source-Promotion-Decision-Ledger has no rows')
    quarantine_rows=csv_rows(root,'META/Public-Claim-Quarantine-current.csv')
    if quarantine_rows:
        q_required={'quarantine_id','claim_id','candidate_id','public_wording_status','required_preconditions','allowed_public_use'}
        missing_cols=q_required-set(quarantine_rows[0].keys())
        if missing_cols:
            ok=False; messages.append('Public-Claim-Quarantine missing columns: ' + ','.join(sorted(missing_cols)))
        dup=[x for x,c in Counter(r.get('quarantine_id','') for r in quarantine_rows).items() if x and c>1]
        if dup:
            ok=False; messages.append('duplicate quarantine_id: ' + '; '.join(dup[:5]))
        lifecycle_now={r.get('claim_id','') for r in csv_rows(root,'META/Claim-Evidence-Strength-current.csv') if r.get('refresh_priority')=='now_or_before_any_public_claim'}
        q_ids={r.get('claim_id','') for r in quarantine_rows}
        if q_ids != lifecycle_now:
            ok=False; messages.append(f'quarantine coverage mismatch: lifecycle_now_only={len(lifecycle_now-q_ids)} quarantine_only={len(q_ids-lifecycle_now)}')
        if not all('blocked' in (r.get('public_wording_status','') or '') for r in quarantine_rows):
            ok=False; messages.append('Public-Claim-Quarantine has rows without blocked public_wording_status')
    else:
        ok=False; messages.append('Public-Claim-Quarantine has no rows')
    sprint_rows=csv_rows(root,'META/Refresh-Sprint-Decision-Matrix-current.csv')
    if sprint_rows:
        sprint_required={'sprint_id','priority','candidate_group','candidate_ids','current_decision','next_file'}
        missing_cols=sprint_required-set(sprint_rows[0].keys())
        if missing_cols:
            ok=False; messages.append('Refresh-Sprint-Decision-Matrix missing columns: ' + ','.join(sorted(missing_cols)))
        dup=[x for x,c in Counter(r.get('sprint_id','') for r in sprint_rows).items() if x and c>1]
        if dup:
            ok=False; messages.append('duplicate sprint_id: ' + '; '.join(dup[:5]))
        missing_files=[r.get('next_file') for r in sprint_rows if r.get('next_file') and not (root/r.get('next_file')).exists()]
        if missing_files:
            ok=False; messages.append('sprint next_file missing: ' + '; '.join(missing_files[:5]))
    else:
        ok=False; messages.append('Refresh-Sprint-Decision-Matrix has no rows')
    receipt_rows=csv_rows(root,'META/Operator-Update-Audit-current.csv')
    if receipt_rows:
        receipt_required={'receipt_id','dissent_id','after_behavior','files_changed','does_this_close_dissent','next_review_target'}
        missing_cols=receipt_required-set(receipt_rows[0].keys())
        if missing_cols:
            ok=False; messages.append('Operator-Update-Audit missing columns: ' + ','.join(sorted(missing_cols)))
        dup=[x for x,c in Counter(r.get('receipt_id','') for r in receipt_rows).items() if x and c>1]
        if dup:
            ok=False; messages.append('duplicate operator receipt_id: ' + '; '.join(dup[:5]))
        if not any(r.get('dissent_id')=='opdist_0001' for r in receipt_rows):
            ok=False; messages.append('Operator-Update-Audit lacks opdist_0001 receipt')
    else:
        ok=False; messages.append('Operator-Update-Audit has no rows')
    tx_rows=csv_rows(root,'META/Source-Promotion-Transaction-Audit-current.csv')
    if tx_rows:
        tx_required={'transaction_id','candidate_id','promoted_source_ids','claim_rows_changed','release_scope','remaining_blocks'}
        missing_cols=tx_required-set(tx_rows[0].keys())
        if missing_cols:
            ok=False; messages.append('Source-Promotion-Transaction-Audit missing columns: ' + ','.join(sorted(missing_cols)))
        dup=[x for x,c in Counter(r.get('transaction_id','') for r in tx_rows).items() if x and c>1]
        if dup:
            ok=False; messages.append('duplicate source-promotion transaction_id: ' + '; '.join(dup[:5]))
        src_ids={r.get('source_id','') for r in csv_rows(root,'Source-Registry-current.csv')}
        missing_tx_src=[]
        for r in tx_rows:
            for sid in (r.get('promoted_source_ids','') or '').split('|'):
                if sid and sid not in src_ids:
                    missing_tx_src.append(f"{r.get('transaction_id')}->{sid}")
        if missing_tx_src:
            ok=False; messages.append('transaction promoted_source_ids missing from Source-Registry: ' + '; '.join(missing_tx_src[:5]))
    else:
        ok=False; messages.append('Source-Promotion-Transaction-Audit has no rows')
    release_rows=csv_rows(root,'META/Public-Claim-Release-Ledger-current.csv')
    if release_rows:
        rel_required={'release_id','claim_id','candidate_id','release_scope','source_registry_ids','what_is_now_allowed','what_remains_blocked'}
        missing_cols=rel_required-set(release_rows[0].keys())
        if missing_cols:
            ok=False; messages.append('Public-Claim-Release-Ledger missing columns: ' + ','.join(sorted(missing_cols)))
        dup=[x for x,c in Counter(r.get('release_id','') for r in release_rows).items() if x and c>1]
        if dup:
            ok=False; messages.append('duplicate release_id: ' + '; '.join(dup[:5]))
        claim_ids={r.get('claim_id','') for r in csv_rows(root,'Claim-Ledger-current.csv')}
        quarantine_claim_ids={r.get('claim_id','') for r in csv_rows(root,'META/Public-Claim-Quarantine-current.csv')}
        src_ids={r.get('source_id','') for r in csv_rows(root,'Source-Registry-current.csv')}
        bad_release=[]; bad_release_src=[]; still_quarantined=[]
        for r in release_rows:
            cid=r.get('claim_id','')
            if cid not in claim_ids:
                bad_release.append(cid)
            if cid in quarantine_claim_ids:
                still_quarantined.append(cid)
            for sid in (r.get('source_registry_ids','') or '').split('|'):
                if sid and sid not in src_ids:
                    bad_release_src.append(f"{r.get('release_id')}->{sid}")
        if bad_release:
            ok=False; messages.append('release claim_id missing from Claim-Ledger: ' + '; '.join(bad_release[:5]))
        if still_quarantined:
            ok=False; messages.append('release claim_id still present in Public-Claim-Quarantine: ' + '; '.join(still_quarantined[:5]))
        if bad_release_src:
            ok=False; messages.append('release source_registry_ids missing from Source-Registry: ' + '; '.join(bad_release_src[:5]))
    else:
        ok=False; messages.append('Public-Claim-Release-Ledger has no rows')
    if not messages:
        messages.append('meta instruments present; dissent, claim taxonomy, source audit, boundary coverage, negative-case, online-intake, operator-update, promotion-transaction, and release checks pass')
    return ok, messages



def redaction_risk_checks(root: Path):
    messages=[]; ok=True
    required=[
        'META/Redaction-Risk-Scan-current.csv','META/Redaction-Risk-Scan-current.json','META/Redaction-Risk-Scan-current.md',
        'META/Redaction-Risk-Open-Findings-current.csv','META/Redaction-Risk-Open-Findings-current.json','META/Redaction-Risk-Open-Findings-current.md',
        'META/Rule46-Scan-current.csv','META/Rule46-Scan-current.json','META/Rule46-Scan-current.md',
        'tools/redaction_scan.py'
    ]
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing:
        return False, ['missing redaction scan files: ' + '; '.join(missing[:8])]
    # Reimplement the high-risk subset here so QA does not depend on import path tricks.
    text_exts={'.txt','.md','.csv','.json','.py'}
    contact_keywords=('helpline','hotline','toll-free','toll free','call centre','call center','phone','number','contact','intake','referral','consultation')
    long_phone_re=re.compile(r'(?<![\w/])(?:\+?\d{1,3}[\s.\-()]*)?(?:\(?\d{2,4}\)?[\s.\-]*){2,4}\d{2,4}(?![\w])')
    short_contact_re=re.compile(r'(?i)\b(?:toll[- ]free|helpline|hotline|call(?: |-)?centre|call(?: |-)?center)\s+(?:number\s+)?\d{3,6}\b')
    coord_re=re.compile(r'(?<!\d)[+-]?\d{1,3}\.\d{4,}\s*,\s*[+-]?\d{1,3}\.\d{4,}(?!\d)')
    email_re=re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
    grave_re=re.compile(r'(?i)\b(?:plot|grave|medical examiner|ME number|ME#|morgue case|case number)\s*[:#]?\s*(?=[A-Z0-9\-/.]*\d)[A-Z0-9][A-Z0-9\-/.]{3,}\b')
    date_like_re=re.compile(r'^(?:19|20)\d{2}[./-]\d{1,2}(?:[./-]\d{1,2})?(?:[./-]\d{1,2})?$')
    doi_like_re=re.compile(r'10\.\d{4,9}/|doi|PIIS\d|s\d{5}')
    placeholders=('redacted — non-referral cube','[redacted','number redacted')
    def ctx(txt,start,end,n=90): return txt[max(0,start-n):min(len(txt),end+n)].replace('\n',' ')
    def false_phone(s, c):
        stripped=s.strip(' ()'); digits=re.sub(r'\D','',s)
        if len(digits)<3 or len(digits)>15: return True
        if date_like_re.match(stripped): return True
        if doi_like_re.search(c): return True
        if 'rev00' in c or 'LivingChristFigures-rev' in c or 'timestamped export' in c.lower(): return True
        if not any(k in c.lower() for k in contact_keywords): return True
        if any(ph in c.lower() for ph in placeholders): return True
        return False
    high=[]
    for p in root.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in text_exts or p.name=='SHA256SUMS.txt':
            continue
        rel=str(p.relative_to(root))
        txt=p.read_text(encoding='utf-8', errors='ignore')
        skip_numeric_contact_scan = rel in {'META/Archive-Member-Manifest-current.csv','META/Archive-Member-Manifest-current.json','META/Package-File-Inventory-current.csv','META/Package-File-Inventory-current.json','META/Sensitive-Surface-Inventory-current.csv','META/Sensitive-Surface-Inventory-current.json','META/Sensitive-Surface-Inventory-current.md','META/Redaction-Risk-Scan-current.csv','META/Redaction-Risk-Scan-current.json','META/Redaction-Risk-Scan-current.md','META/Redaction-Risk-Open-Findings-current.csv','META/Redaction-Risk-Open-Findings-current.json','META/Redaction-Risk-Open-Findings-current.md','META/Previous-Release-Fingerprint-current.json'}
        for rx, typ in [(email_re,'email'),(coord_re,'coordinate'),(grave_re,'grave_or_case_id')]:
            for m in rx.finditer(txt):
                c=ctx(txt,m.start(),m.end())
                if any(ph in c.lower() for ph in placeholders): continue
                high.append(f'{typ}:{p.relative_to(root)}:{m.group(0)[:40]}')
        if skip_numeric_contact_scan:
            continue
        for m in long_phone_re.finditer(txt):
            c=ctx(txt,m.start(),m.end())
            if not false_phone(m.group(0), c):
                high.append(f'public_contact_number:{p.relative_to(root)}:{m.group(0)}')
        for m in short_contact_re.finditer(txt):
            c=ctx(txt,m.start(),m.end())
            if any(ph in c.lower() for ph in placeholders): continue
            high.append(f'short_public_contact_number:{p.relative_to(root)}:{m.group(0)}')
    if high:
        ok=False; messages.append('open high-risk redaction findings: ' + '; '.join(high[:8]))
    # The open findings report should also be empty if generated.
    try:
        data=json.loads((root/'META/Redaction-Risk-Open-Findings-current.json').read_text(encoding='utf-8'))
        high_rows=[r for r in data if r.get('severity')=='high']
        if high_rows:
            ok=False; messages.append(f'Redaction-Risk-Open-Findings-current.json has {len(high_rows)} high-risk rows')
    except Exception as e:
        ok=False; messages.append(f'Redaction open-findings JSON invalid: {e}')
    if not messages:
        messages.append('redaction scanner files present; zero open configured high-risk findings')
    return ok, messages




def evidence_lifecycle_checks(root: Path):
    messages=[]; ok=True
    required=[
        'META/Claim-Evidence-Strength-current.csv','META/Claim-Evidence-Strength-current.json','META/Claim-Evidence-Strength-current.md',
        'META/Refresh-Priority-Queue-current.csv','META/Refresh-Priority-Queue-current.json','META/Refresh-Priority-Queue-current.md',
        'META/Evidence-Lifecycle-Policy-current.md','tools/evidence_lifecycle.py'
    ]
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing:
        return False, ['missing evidence lifecycle files: ' + '; '.join(missing[:8])]
    claim_rows=csv_rows(root,'Claim-Ledger-current.csv')
    lifecycle=csv_rows(root,'META/Claim-Evidence-Strength-current.csv')
    queue=csv_rows(root,'META/Refresh-Priority-Queue-current.csv')
    cand_rows=csv_rows(root,'Candidate-Ledger-current.csv')
    if len(lifecycle)!=len(claim_rows):
        ok=False; messages.append(f'Claim-Evidence-Strength row count {len(lifecycle)} != claim count {len(claim_rows)}')
    if len(queue)!=len(cand_rows):
        ok=False; messages.append(f'Refresh-Priority-Queue row count {len(queue)} != candidate count {len(cand_rows)}')
    needed={'claim_id','candidate_id','evidence_strength','capacity_currentness_risk','refresh_priority','suggested_refresh_cadence','needs_human_review'}
    if lifecycle:
        missing_cols=needed-set(lifecycle[0].keys())
        if missing_cols:
            ok=False; messages.append('Claim-Evidence-Strength missing columns: '+','.join(sorted(missing_cols)))
    claim_ids={r.get('claim_id','') for r in claim_rows}
    life_ids={r.get('claim_id','') for r in lifecycle}
    if claim_ids!=life_ids:
        ok=False; messages.append(f'claim lifecycle id set mismatch: claim_only={len(claim_ids-life_ids)} lifecycle_only={len(life_ids-claim_ids)}')
    allowed_strength={'multi_source_supported_shape','single_primary_or_institutional_shape','single_source_supported_shape','critical_counterevidence_present','boundary_or_counterclaim','interpretive_not_fact_claim','unsupported_or_missing_source_link'}
    bad=[r.get('claim_id') for r in lifecycle if r.get('evidence_strength') not in allowed_strength]
    if bad:
        ok=False; messages.append('bad evidence_strength labels: '+ '; '.join(bad[:5]))
    now=sum(1 for r in lifecycle if r.get('refresh_priority')=='now_or_before_any_public_claim')
    if now == 0:
        ok=False; messages.append('expected at least one now_or_before_any_public_claim row; lifecycle classifier may be inert')
    if not messages:
        messages.append(f'evidence lifecycle reports present; {len(lifecycle)} claims classified; {now} rows require refresh before public claim')
    return ok, messages

def schema_contract_checks(root: Path):
    messages=[]; ok=True
    required=[
        'SCHEMA/README-schema-current.md',
        'SCHEMA/Frontmatter-Contract-current.json',
        'SCHEMA/Ledger-Contract-current.json',
        'SCHEMA/Source-Type-Controlled-Vocabulary-current.csv',
        'SCHEMA/Source-Type-Controlled-Vocabulary-current.json',
        'SCHEMA/Source-Type-Controlled-Vocabulary-current.md',
        'SCHEMA/Package-Release-Contract-current.json',
        'SCHEMA/Schema-Validation-Report-current.csv',
        'SCHEMA/Schema-Validation-Report-current.json',
        'SCHEMA/Schema-Validation-Report-current.md',
        'tools/schema_validate.py',
        'tools/render_public_safe_index.py',
        'tools/rule46_scan.py',
        'tools/public_contract_check.py',
        'tools/public_export_eligibility.py',
        'tools/public_source_link_review.py',
        'tools/public_release_lint.py',
        'tools/sensitive_surface_inventory.py',
        'tools/candidate_governance_snapshot.py',
        'SCHEMA/Harm-Proximity-Controlled-Vocabulary-current.csv',
        'SCHEMA/Public-Link-Policy-current.csv',
        'SCHEMA/Public-Allowed-Claim-Shapes-current.csv',
        'SCHEMA/Indigenous-Data-Governance-Fields-current.csv',
        'SCHEMA/Public-Export-Eligibility-Fields-current.csv',
        'SCHEMA/Governance-Decision-Fields-current.csv',
        'SCHEMA/Public-Source-Link-Review-Fields-current.csv',
        'SCHEMA/Public-Release-Lint-Fields-current.csv',
        'SCHEMA/Sensitive-Surface-Inventory-Fields-current.csv',
        'SCHEMA/Candidate-Governance-Snapshot-Fields-current.csv',
        'SCHEMA/Governance-Review-Queue-Fields-current.csv',
        'SCHEMA/Row-Validation-Contract-current.json',
        'SCHEMA/Row-Validation-Report-current.csv',
        'SCHEMA/Row-Validation-Report-current.json',
        'SCHEMA/Row-Validation-Report-current.md',
        'SCHEMA/Row-Validation-Report-Fields-current.csv',
        'SCHEMA/Revision-Surface-Audit-Fields-current.csv',
        'SCHEMA/Generated-Artifact-Provenance-Fields-current.csv',
        'SCHEMA/Release-Gate-Attestation-Fields-current.csv',
        'SCHEMA/Public-Index-Parity-Fields-current.csv',
        'SCHEMA/Governance-Consistency-Audit-Fields-current.csv',
        'SCHEMA/Package-Dependency-Graph-Fields-current.csv',
        'tools/public_index_parity.py',
        'tools/governance_consistency_audit.py',
        'tools/package_dependency_graph.py',
        'tools/row_validate.py',
        'tools/generated_artifact_provenance.py',
        'tools/revision_surface_audit.py',
        'tools/release_gate_attestation.py',
        'tools/field_schema_consistency.py',
        'SCHEMA/Audit-Selftest-Fields-current.csv',
        'SCHEMA/Rebuild-Readiness-Audit-Fields-current.csv',
        'tools/audit_selftest.py',
        'tools/rebuild_readiness_audit.py',
        'SCHEMA/Policy-Assertion-Matrix-Fields-current.csv',
        'SCHEMA/Regeneration-Sequence-Plan-Fields-current.csv',
        'SCHEMA/Archive-Build-Manifest-Fields-current.csv',
        'SCHEMA/Selftest-Coverage-Matrix-Fields-current.csv',
        'SCHEMA/Checksum-Scope-Audit-Fields-current.csv',
        'SCHEMA/Public-Negative-Corpus-Fields-current.csv',
        'SCHEMA/Release-Evidence-Closure-Fields-current.csv',
        'tools/policy_assertion_matrix.py',
        'tools/regeneration_sequence_plan.py',
        'tools/archive_build_manifest.py',
        'tools/selftest_coverage_matrix.py',
        'tools/checksum_scope_audit.py',
        'tools/public_negative_corpus.py',
        'tools/release_evidence_closure.py',
        'SCHEMA/Tool-Executability-Audit-Fields-current.csv',
        'SCHEMA/Boundary-Domain-Registry-Fields-current.csv',
        'SCHEMA/Candidate-Boundary-Domain-Map-Fields-current.csv',
        'SCHEMA/Boundary-Domain-Coverage-Audit-Fields-current.csv',
        'tools/tool_executability_audit.py',
        'tools/boundary_domain_map.py',
    ]
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing:
        return False, ['missing schema/contract files: ' + '; '.join(missing[:8])]
    try:
        spec=importlib.util.spec_from_file_location('schema_validate', root/'tools'/'schema_validate.py')
        mod=importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(mod)
        findings=mod.run(root)
    except Exception as e:
        return False, [f'schema validator could not run: {e}']
    high=[r for r in findings if r.get('severity')=='high']
    if high:
        ok=False
        messages.append('schema validator high findings: ' + '; '.join(f"{r.get('check')}:{r.get('file')}" for r in high[:6]))
    try:
        report=json.loads((root/'SCHEMA/Schema-Validation-Report-current.json').read_text(encoding='utf-8'))
        report_high=[r for r in report if r.get('severity')=='high']
        if report_high:
            ok=False; messages.append(f'Schema-Validation-Report-current.json has {len(report_high)} high findings')
    except Exception as e:
        ok=False; messages.append(f'Schema-Validation-Report-current.json invalid: {e}')
    # The public export manifest is a handoff artifact, so it must track the package revision.
    try:
        manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
        pub=json.loads((root/'PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json').read_text(encoding='utf-8'))
        if pub.get('revision') != manifest.get('revision'):
            ok=False; messages.append('PUBLIC-EXPORT-MANIFEST revision disagrees with manifest revision')
        if pub.get('package_revision') != manifest.get('revision'):
            ok=False; messages.append('PUBLIC-EXPORT-MANIFEST package_revision disagrees with manifest revision')
    except Exception as e:
        ok=False; messages.append(f'public manifest revision check failed: {e}')
    if not messages:
        messages.append('schema contracts, ledger headers, JSON mirrors, source-type vocabulary, and public manifest checks pass')
    return ok, messages



def governance_layer_checks(root: Path):
    messages=[]; ok=True
    required=[
        'CURRENT-SPINE.md',
        'GOVERNANCE/README-governance-current.md',
        'GOVERNANCE/Indigenous-Data-Governance-Protocol-current.md',
        'GOVERNANCE/Family-Consent-and-Case-Name-Use-Ledger-current.csv',
        'GOVERNANCE/Family-Consent-and-Case-Name-Use-Ledger-current.json',
        'GOVERNANCE/Family-Consent-and-Case-Name-Use-Ledger-current.md',
        'GOVERNANCE/Takedown-and-Reclassification-Protocol-current.md',
        'GOVERNANCE/Public-Export-Eligibility-Protocol-current.md',
        'GOVERNANCE/Governance-Decision-and-Review-Protocol-current.md',
        'GOVERNANCE/Governance-Decision-Ledger-current.csv',
        'GOVERNANCE/Governance-Decision-Ledger-current.json',
        'GOVERNANCE/Governance-Decision-Ledger-current.md',
        'GOVERNANCE/CARE-OCAP-UNDRIP-Crosswalk-current.csv',
        'GOVERNANCE/CARE-OCAP-UNDRIP-Crosswalk-current.json',
        'GOVERNANCE/CARE-OCAP-UNDRIP-Crosswalk-current.md',
        'PUBLIC/Public-Safe-Prose-Templates-current.md',
        'SCHEMA/Public-Allowed-Claim-Shapes-current.csv',
        'SCHEMA/Public-Link-Policy-current.csv',
        'SCHEMA/Harm-Proximity-Controlled-Vocabulary-current.csv',
        'SCHEMA/Indigenous-Data-Governance-Fields-current.csv',
        'SCHEMA/Public-Export-Eligibility-Fields-current.csv',
        'SCHEMA/Governance-Decision-Fields-current.csv',
        'SCHEMA/Public-Source-Link-Review-Fields-current.csv',
        'SCHEMA/Public-Release-Lint-Fields-current.csv',
        'SCHEMA/Sensitive-Surface-Inventory-Fields-current.csv',
        'SCHEMA/Candidate-Governance-Snapshot-Fields-current.csv',
        'SCHEMA/Governance-Review-Queue-Fields-current.csv',
        'SCHEMA/Row-Validation-Contract-current.json',
        'SCHEMA/Row-Validation-Report-current.csv',
        'SCHEMA/Row-Validation-Report-current.json',
        'SCHEMA/Row-Validation-Report-current.md',
        'SCHEMA/Row-Validation-Report-Fields-current.csv',
        'SCHEMA/Revision-Surface-Audit-Fields-current.csv',
        'SCHEMA/Generated-Artifact-Provenance-Fields-current.csv',
        'SCHEMA/Release-Gate-Attestation-Fields-current.csv',
        'SCHEMA/Public-Index-Parity-Fields-current.csv',
        'SCHEMA/Governance-Consistency-Audit-Fields-current.csv',
        'SCHEMA/Package-Dependency-Graph-Fields-current.csv',
        'tools/public_index_parity.py',
        'tools/governance_consistency_audit.py',
        'tools/package_dependency_graph.py',
        'tools/row_validate.py',
        'tools/generated_artifact_provenance.py',
        'tools/revision_surface_audit.py',
        'tools/release_gate_attestation.py',
        'tools/field_schema_consistency.py',
        'SCHEMA/Audit-Selftest-Fields-current.csv',
        'SCHEMA/Rebuild-Readiness-Audit-Fields-current.csv',
        'tools/audit_selftest.py',
        'tools/rebuild_readiness_audit.py',
        'SCHEMA/Policy-Assertion-Matrix-Fields-current.csv',
        'SCHEMA/Regeneration-Sequence-Plan-Fields-current.csv',
        'SCHEMA/Archive-Build-Manifest-Fields-current.csv',
        'SCHEMA/Selftest-Coverage-Matrix-Fields-current.csv',
        'SCHEMA/Checksum-Scope-Audit-Fields-current.csv',
        'SCHEMA/Public-Negative-Corpus-Fields-current.csv',
        'SCHEMA/Release-Evidence-Closure-Fields-current.csv',
        'tools/policy_assertion_matrix.py',
        'tools/regeneration_sequence_plan.py',
        'tools/archive_build_manifest.py',
        'tools/selftest_coverage_matrix.py',
        'tools/checksum_scope_audit.py',
        'tools/public_negative_corpus.py',
        'tools/release_evidence_closure.py',
    ]
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing:
        ok=False; messages.append('missing governance files: ' + '; '.join(missing[:8]))
    consent=csv_rows(root,'GOVERNANCE/Family-Consent-and-Case-Name-Use-Ledger-current.csv')
    if consent:
        needed={'governance_row_id','candidate_id','family_chosen_public_name_status','community_review_status','consent_basis','harm_proximity','public_reuse_allowed','public_link_allowed','image_use_allowed','do_not_extract_case_details'}
        missing_cols=needed-set(consent[0].keys())
        if missing_cols:
            ok=False; messages.append('Family-Consent ledger missing columns: '+','.join(sorted(missing_cols)))
        if not any(r.get('candidate_id')=='cand_bridget_tolley_fsis_mmiwg_canada' for r in consent):
            ok=False; messages.append('Family-Consent ledger lacks Bridget/FSIS governance row')
    else:
        ok=False; messages.append('Family-Consent ledger has no rows')
    source_rows=csv_rows(root,'Source-Registry-current.csv')
    missing_source_fields=[r.get('source_id','') for r in source_rows if not r.get('harm_proximity') or not r.get('public_link_policy')]
    if missing_source_fields:
        ok=False; messages.append('Source Registry rows missing governance fields: '+ '; '.join(missing_source_fields[:5]))
    try:
        contract=json.loads((root/'SCHEMA/Package-Release-Contract-current.json').read_text(encoding='utf-8'))
        allowed=set(contract.get('allowed_public_layer_files',[]))
        actual={str(p.relative_to(root)) for p in (root/'PUBLIC').glob('*') if p.is_file()}
        extra=sorted(actual-allowed); missing=sorted(allowed-actual)
        if extra or missing:
            ok=False; messages.append(f'public contract drift extra={len(extra)} missing={len(missing)}')
    except Exception as e:
        ok=False; messages.append(f'public contract check failed: {e}')

    eligibility=csv_rows(root,'META/Public-Export-Eligibility-current.csv')
    cand_ids={r.get('candidate_id','') for r in csv_rows(root,'Candidate-Ledger-current.csv')}
    elig_ids={r.get('candidate_id','') for r in eligibility}
    if cand_ids != elig_ids:
        ok=False; messages.append(f'Public-Export-Eligibility coverage mismatch candidate_only={len(cand_ids-elig_ids)} eligibility_only={len(elig_ids-cand_ids)}')
    if eligibility:
        needed_elig={'candidate_id','candidate_name','public_export_tier','public_shape_template','public_url_release','public_claim_release','required_review'}
        missing_cols=needed_elig-set(eligibility[0].keys())
        if missing_cols:
            ok=False; messages.append('Public-Export-Eligibility missing columns: '+','.join(sorted(missing_cols)))
        allowed_tiers={'public_index_shape_only','boundary_index_shape_only','policy_context_only','quarantined_no_public_expansion'}
        bad_tiers=[r.get('candidate_id') for r in eligibility if r.get('public_export_tier') not in allowed_tiers]
        if bad_tiers:
            ok=False; messages.append('Public-Export-Eligibility bad tiers: '+ '; '.join(bad_tiers[:5]))
        if not any(r.get('public_export_tier')=='quarantined_no_public_expansion' for r in eligibility):
            ok=False; messages.append('Public-Export-Eligibility lacks quarantined_no_public_expansion row')
    govdec=csv_rows(root,'GOVERNANCE/Governance-Decision-Ledger-current.csv')
    if not govdec:
        ok=False; messages.append('Governance-Decision-Ledger has no rows')
    elif not any(r.get('decision_class')=='public_release_blocked' for r in govdec):
        ok=False; messages.append('Governance-Decision-Ledger lacks public_release_blocked decision')

    link_review=csv_rows(root,'META/Public-Source-Link-Review-current.csv')
    source_ids={r.get('source_id','') for r in csv_rows(root,'Source-Registry-current.csv')}
    link_ids={r.get('source_id','') for r in link_review}
    if source_ids != link_ids:
        ok=False; messages.append(f'Public-Source-Link-Review coverage mismatch source_only={len(source_ids-link_ids)} review_only={len(link_ids-source_ids)}')
    if link_review:
        allowed_link_decisions={'block_public_url','manual_review_required_block_until_review','allow_only_with_boundary_note_after_manual_review','allow_after_context_review'}
        bad=[r.get('source_id') for r in link_review if r.get('public_url_release_decision') not in allowed_link_decisions]
        if bad:
            ok=False; messages.append('Public-Source-Link-Review bad decisions: '+ '; '.join(bad[:5]))
    if not messages:
        messages.append('governance layer present; consent ledger, eligibility/link-review ledgers, governance decisions, source harm/link fields, and public contract check pass')
    return ok, messages



def public_release_lint_checks(root: Path):
    messages=[]; ok=True
    required=['META/Public-Release-Lint-current.csv','META/Public-Release-Lint-current.json','META/Public-Release-Lint-current.md','tools/public_release_lint.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing:
        return False, ['missing public release lint files: ' + '; '.join(missing)]
    try:
        rows=json.loads((root/'META/Public-Release-Lint-current.json').read_text(encoding='utf-8'))
        high=[r for r in rows if r.get('severity')=='high']
        if high:
            ok=False; messages.append(f'Public-Release-Lint-current.json has {len(high)} high findings')
        public_files={str(p.relative_to(root)) for p in (root/'PUBLIC').glob('*') if p.is_file()}
        lint_files={r.get('file','') for r in rows}
        missing_coverage=sorted(public_files-lint_files)
        if missing_coverage:
            ok=False; messages.append('Public release lint missing files: ' + '; '.join(missing_coverage[:5]))
    except Exception as e:
        ok=False; messages.append(f'public release lint JSON invalid: {e}')
    if not messages:
        messages.append('public release lint files present; zero high findings and all PUBLIC files covered')
    return ok, messages


def sensitive_surface_inventory_checks(root: Path):
    messages=[]; ok=True
    required=['META/Sensitive-Surface-Inventory-current.csv','META/Sensitive-Surface-Inventory-current.json','META/Sensitive-Surface-Inventory-current.md','tools/sensitive_surface_inventory.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing:
        return False, ['missing sensitive surface inventory files: ' + '; '.join(missing)]
    try:
        rows=json.loads((root/'META/Sensitive-Surface-Inventory-current.json').read_text(encoding='utf-8'))
        public_high=[r for r in rows if r.get('file_scope')=='public' and r.get('severity')=='high']
        if public_high:
            ok=False; messages.append(f'Sensitive-Surface-Inventory has {len(public_high)} public high rows')
        if not rows:
            ok=False; messages.append('Sensitive-Surface-Inventory has no rows')
    except Exception as e:
        ok=False; messages.append(f'sensitive surface inventory JSON invalid: {e}')
    if not messages:
        messages.append('sensitive surface inventory files present; no high-risk public inventory rows')
    return ok, messages


def candidate_governance_snapshot_checks(root: Path):
    messages=[]; ok=True
    required=['META/Candidate-Governance-Snapshot-current.csv','META/Candidate-Governance-Snapshot-current.json','META/Candidate-Governance-Snapshot-current.md','META/Governance-Review-Queue-current.csv','META/Governance-Review-Queue-current.json','META/Governance-Review-Queue-current.md','tools/candidate_governance_snapshot.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing:
        return False, ['missing candidate governance snapshot files: ' + '; '.join(missing[:8])]
    cand_ids={r.get('candidate_id','') for r in csv_rows(root,'Candidate-Ledger-current.csv')}
    snap=csv_rows(root,'META/Candidate-Governance-Snapshot-current.csv')
    snap_ids={r.get('candidate_id','') for r in snap}
    if cand_ids != snap_ids:
        ok=False; messages.append(f'Candidate-Governance-Snapshot coverage mismatch candidate_only={len(cand_ids-snap_ids)} snapshot_only={len(snap_ids-cand_ids)}')
    queue=csv_rows(root,'META/Governance-Review-Queue-current.csv')
    if not queue:
        ok=False; messages.append('Governance-Review-Queue has no rows')
    if not any(r.get('candidate_id')=='cand_bridget_tolley_fsis_mmiwg_canada' and r.get('governance_quarantine')=='true' for r in snap):
        ok=False; messages.append('Candidate-Governance-Snapshot lacks Bridget/FSIS governance quarantine')
    if not messages:
        messages.append(f'candidate governance snapshot covers {len(snap_ids)} candidates; review queue has {len(queue)} rows')
    return ok, messages


def row_validation_checks(root: Path):
    messages=[]; ok=True
    required=['SCHEMA/Row-Validation-Contract-current.json','SCHEMA/Row-Validation-Report-current.csv','SCHEMA/Row-Validation-Report-current.json','SCHEMA/Row-Validation-Report-current.md','tools/row_validate.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing row-validation files: ' + '; '.join(missing[:8])]
    try:
        rows=json.loads((root/'SCHEMA/Row-Validation-Report-current.json').read_text(encoding='utf-8'))
        high=[r for r in rows if r.get('severity')=='high']
        if high:
            ok=False; messages.append(f'Row-Validation-Report-current.json has {len(high)} high findings')
    except Exception as e:
        ok=False; messages.append(f'row-validation JSON invalid: {e}')
    if not messages: messages.append('row-level validation files present; zero high findings')
    return ok, messages


def revision_surface_audit_checks(root: Path):
    messages=[]; ok=True
    required=['META/Revision-Surface-Audit-current.csv','META/Revision-Surface-Audit-current.json','META/Revision-Surface-Audit-current.md','tools/revision_surface_audit.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing revision-surface audit files: ' + '; '.join(missing[:8])]
    try:
        rows=json.loads((root/'META/Revision-Surface-Audit-current.json').read_text(encoding='utf-8'))
        high=[r for r in rows if r.get('severity')=='high']
        if high:
            ok=False; messages.append(f'Revision-Surface-Audit-current.json has {len(high)} high findings')
    except Exception as e:
        ok=False; messages.append(f'revision-surface audit JSON invalid: {e}')
    if not messages: messages.append('revision-surface audit files present; zero high findings')
    return ok, messages


def _sha256_file(path: Path):
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()


def _provenance_fingerprint(root: Path, rels):
    h=hashlib.sha256()
    for rel in sorted([x for x in rels if x]):
        p=root/rel
        h.update(rel.encode('utf-8')+b'\0')
        h.update(_sha256_file(p).encode('ascii') if p.exists() else b'MISSING')
    return h.hexdigest()


def generated_artifact_provenance_checks(root: Path):
    messages=[]; ok=True
    required=['META/Generated-Artifact-Provenance-current.csv','META/Generated-Artifact-Provenance-current.json','META/Generated-Artifact-Provenance-current.md','tools/generated_artifact_provenance.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing generated-artifact provenance files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Generated-Artifact-Provenance-current.csv')
    if not rows:
        ok=False; messages.append('Generated-Artifact-Provenance has no rows')
    bad_status=[r.get('artifact_path','') for r in rows if r.get('status')!='pass']
    if bad_status:
        ok=False; messages.append('generated-artifact provenance non-pass rows: ' + '; '.join(bad_status[:5]))
    hash_drift=[]; input_drift=[]
    for r in rows:
        art=root/r.get('artifact_path','')
        if not art.exists():
            hash_drift.append(r.get('artifact_path','')); continue
        if r.get('artifact_sha256') != _sha256_file(art):
            hash_drift.append(r.get('artifact_path',''))
        inputs=[x for x in (r.get('input_paths','') or '').split('|') if x]+[r.get('generator','')]
        if r.get('input_fingerprint') != _provenance_fingerprint(root, inputs):
            input_drift.append(r.get('artifact_path',''))
    if hash_drift:
        ok=False; messages.append('generated artifact hash drift: ' + '; '.join(hash_drift[:5]))
    if input_drift:
        ok=False; messages.append('generated artifact input fingerprint drift: ' + '; '.join(input_drift[:5]))
    if not messages: messages.append(f'generated-artifact provenance tracks {len(rows)} artifacts; hashes and input fingerprints verify')
    return ok, messages



def public_index_parity_checks(root: Path):
    messages=[]; ok=True
    required=['META/Public-Index-Parity-current.csv','META/Public-Index-Parity-current.json','META/Public-Index-Parity-current.md','SCHEMA/Public-Index-Parity-Fields-current.csv','tools/public_index_parity.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing public-index parity files: ' + '; '.join(missing[:8])]
    try:
        rows=json.loads((root/'META/Public-Index-Parity-current.json').read_text(encoding='utf-8'))
        high=[r for r in rows if r.get('severity')=='high']
        if high:
            ok=False; messages.append(f'Public-Index-Parity-current.json has {len(high)} high findings')
    except Exception as e:
        ok=False; messages.append(f'public-index parity JSON invalid: {e}')
    if not messages: messages.append('public index parity files present; zero high findings')
    return ok, messages


def public_index_semantic_audit_checks(root: Path):
    messages=[]; ok=True
    required=['META/Public-Index-Semantic-Audit-current.csv','META/Public-Index-Semantic-Audit-current.json','META/Public-Index-Semantic-Audit-current.md','SCHEMA/Public-Index-Semantic-Audit-Fields-current.csv','tools/public_index_semantic_audit.py','tools/public_template_policy.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing public-index semantic audit files: ' + '; '.join(missing[:8])]
    try:
        rows=json.loads((root/'META/Public-Index-Semantic-Audit-current.json').read_text(encoding='utf-8'))
        high=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
        if high:
            ok=False; messages.append(f'Public-Index-Semantic-Audit-current.json has {len(high)} blocking high findings')
        if not any(r.get('check')=='critical_template_quorum' and r.get('status')=='pass' for r in rows):
            ok=False; messages.append('public semantic audit lacks passing critical_template_quorum row')
    except Exception as e:
        ok=False; messages.append(f'public-index semantic audit JSON invalid: {e}')
    if not messages: messages.append('public index semantic audit files present; template-specific quarantine canaries pass with zero blocking high findings')
    return ok, messages


def governance_consistency_audit_checks(root: Path):
    messages=[]; ok=True
    required=['META/Governance-Consistency-Audit-current.csv','META/Governance-Consistency-Audit-current.json','META/Governance-Consistency-Audit-current.md','SCHEMA/Governance-Consistency-Audit-Fields-current.csv','tools/governance_consistency_audit.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing governance-consistency audit files: ' + '; '.join(missing[:8])]
    try:
        rows=json.loads((root/'META/Governance-Consistency-Audit-current.json').read_text(encoding='utf-8'))
        high=[r for r in rows if r.get('severity')=='high']
        if high:
            ok=False; messages.append(f'Governance-Consistency-Audit-current.json has {len(high)} high findings')
    except Exception as e:
        ok=False; messages.append(f'governance-consistency audit JSON invalid: {e}')
    if not messages: messages.append('governance consistency audit files present; zero high findings')
    return ok, messages


def package_dependency_graph_checks(root: Path):
    messages=[]; ok=True
    required=['META/Package-Dependency-Graph-current.csv','META/Package-Dependency-Graph-current.json','META/Package-Dependency-Graph-current.md','SCHEMA/Package-Dependency-Graph-Fields-current.csv','tools/package_dependency_graph.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing package-dependency graph files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Package-Dependency-Graph-current.csv')
    if not rows:
        ok=False; messages.append('Package-Dependency-Graph has no rows')
    missing_edges=[r.get('edge_id','') for r in rows if r.get('status')=='missing_dependency']
    if missing_edges:
        ok=False; messages.append('package dependency graph missing edges: ' + '; '.join(missing_edges[:8]))
    if not messages: messages.append(f'package dependency graph tracks {len(rows)} edges; no missing dependencies')
    return ok, messages



def csv_json_mirror_audit_checks(root: Path):
    messages=[]; ok=True
    required=['META/CSV-JSON-Mirror-Audit-current.csv','META/CSV-JSON-Mirror-Audit-current.json','META/CSV-JSON-Mirror-Audit-current.md','SCHEMA/CSV-JSON-Mirror-Audit-Fields-current.csv','tools/csv_json_mirror_audit.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing CSV/JSON mirror audit files: ' + '; '.join(missing[:8])]
    try:
        rows=json.loads((root/'META/CSV-JSON-Mirror-Audit-current.json').read_text(encoding='utf-8'))
        high=[r for r in rows if r.get('severity')=='high']
        if high:
            ok=False; messages.append(f'CSV-JSON-Mirror-Audit-current.json has {len(high)} high findings')
    except Exception as e:
        ok=False; messages.append(f'CSV/JSON mirror audit JSON invalid: {e}')
    if not messages: messages.append('CSV/JSON mirror audit files present; zero high findings')
    return ok, messages


def schema_coverage_audit_checks(root: Path):
    messages=[]; ok=True
    required=['META/Schema-Coverage-Audit-current.csv','META/Schema-Coverage-Audit-current.json','META/Schema-Coverage-Audit-current.md','SCHEMA/Schema-Coverage-Audit-Fields-current.csv','tools/schema_coverage_audit.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing schema-coverage audit files: ' + '; '.join(missing[:8])]
    try:
        rows=json.loads((root/'META/Schema-Coverage-Audit-current.json').read_text(encoding='utf-8'))
        high=[r for r in rows if r.get('severity')=='high']
        medium=[r for r in rows if r.get('severity')=='medium']
        if high:
            ok=False; messages.append(f'Schema-Coverage-Audit-current.json has {len(high)} high findings')
        if medium:
            ok=False; messages.append(f'Schema-Coverage-Audit-current.json has {len(medium)} medium backlog rows; rev0055 requires zero backlog')
        if not high and not medium:
            messages.append('schema coverage audit files present; zero high findings; zero medium backlog rows')
    except Exception as e:
        ok=False; messages.append(f'schema coverage audit JSON invalid: {e}')
    return ok, messages


def package_file_inventory_checks(root: Path):
    messages=[]; ok=True
    required=['META/Package-File-Inventory-current.csv','META/Package-File-Inventory-current.json','META/Package-File-Inventory-current.md','SCHEMA/Package-File-Inventory-Fields-current.csv','tools/package_file_inventory.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing package file inventory files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Package-File-Inventory-current.csv')
    if len(rows)<100:
        ok=False; messages.append(f'Package-File-Inventory has only {len(rows)} rows')
    zones={r.get('package_zone','') for r in rows}
    if 'public_layer' not in zones or 'schema_contract_layer' not in zones or 'tooling_layer' not in zones:
        ok=False; messages.append('Package-File-Inventory missing expected package zones')
    if not messages:
        messages.append(f'package file inventory covers {len(rows)} stable files across {len(zones)} zones')
    return ok, messages


def field_schema_consistency_checks(root: Path):
    messages=[]; ok=True
    required=['META/Field-Schema-Consistency-Audit-current.csv','META/Field-Schema-Consistency-Audit-current.json','META/Field-Schema-Consistency-Audit-current.md','SCHEMA/Field-Schema-Consistency-Audit-Fields-current.csv','tools/field_schema_consistency.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing field-schema consistency files: ' + '; '.join(missing[:8])]
    try:
        rows=json.loads((root/'META/Field-Schema-Consistency-Audit-current.json').read_text(encoding='utf-8'))
        high=[r for r in rows if r.get('severity')=='high']
        exact_pass=[r for r in rows if r.get('field_schema_status')=='pass']
        if high:
            ok=False; messages.append(f'Field-Schema-Consistency-Audit-current.json has {len(high)} high findings')
        if not exact_pass:
            ok=False; messages.append('Field-Schema-Consistency-Audit has no exact target pass rows')
    except Exception as e:
        ok=False; messages.append(f'field-schema consistency JSON invalid: {e}')
    if not messages: messages.append('field-schema consistency audit files present; zero high findings; exact field schemas matched targets')
    return ok, messages


def path_reference_audit_checks(root: Path):
    messages=[]; ok=True
    required=['META/Path-Reference-Audit-current.csv','META/Path-Reference-Audit-current.json','META/Path-Reference-Audit-current.md','SCHEMA/Path-Reference-Audit-Fields-current.csv','tools/path_reference_audit.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing path-reference audit files: ' + '; '.join(missing[:8])]
    try:
        rows=json.loads((root/'META/Path-Reference-Audit-current.json').read_text(encoding='utf-8'))
        high=[r for r in rows if r.get('severity')=='high']
        if high:
            ok=False; messages.append(f'Path-Reference-Audit-current.json has {len(high)} high findings')
    except Exception as e:
        ok=False; messages.append(f'path-reference audit JSON invalid: {e}')
    if not messages: messages.append('path-reference audit files present; zero high findings')
    return ok, messages


def rule_gate_traceability_checks(root: Path):
    messages=[]; ok=True
    required=['META/Rule-Gate-Traceability-current.csv','META/Rule-Gate-Traceability-current.json','META/Rule-Gate-Traceability-current.md','SCHEMA/Rule-Gate-Traceability-Fields-current.csv','tools/rule_gate_traceability.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing rule-gate traceability files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Rule-Gate-Traceability-current.csv')
    bad=[r.get('rule_number','') for r in rows if r.get('trace_status') in {'missing_boundary_coverage','missing_trace_file'}]
    if not rows:
        ok=False; messages.append('Rule-Gate-Traceability has no rows')
    if bad:
        ok=False; messages.append('Rule-Gate-Traceability missing trace rows: ' + '; '.join(bad[:8]))
    if not messages: messages.append(f'rule-gate traceability covers {len(rows)} rules with no missing trace-file rows')
    return ok, messages


def tool_run_matrix_checks(root: Path):
    messages=[]; ok=True
    required=['META/Tool-Run-Matrix-current.csv','META/Tool-Run-Matrix-current.json','META/Tool-Run-Matrix-current.md','SCHEMA/Tool-Run-Matrix-Fields-current.csv','tools/tool_run_matrix.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing tool-run matrix files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Tool-Run-Matrix-current.csv')
    bad=[r.get('tool_path','') for r in rows if r.get('status')!='pass']
    if not rows:
        ok=False; messages.append('Tool-Run-Matrix has no rows')
    if bad:
        ok=False; messages.append('Tool-Run-Matrix non-pass tools: ' + '; '.join(bad[:8]))
    if not messages: messages.append(f'tool-run matrix classifies {len(rows)} tools with no non-pass rows')
    return ok, messages


def required_document_coverage_checks(root: Path):
    messages=[]; ok=True
    required=['META/Required-Document-Coverage-current.csv','META/Required-Document-Coverage-current.json','META/Required-Document-Coverage-current.md','SCHEMA/Required-Document-Coverage-Fields-current.csv','tools/required_document_coverage.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing required-document coverage files: ' + '; '.join(missing[:8])]
    try:
        rows=json.loads((root/'META/Required-Document-Coverage-current.json').read_text(encoding='utf-8'))
        high=[r for r in rows if r.get('severity')=='high']
        if high:
            ok=False; messages.append(f'Required-Document-Coverage-current.json has {len(high)} high findings')
    except Exception as e:
        ok=False; messages.append(f'required-document coverage JSON invalid: {e}')
    if not messages: messages.append('required-document coverage files present; zero high findings')
    return ok, messages



def audit_selftest_checks(root: Path):
    messages=[]; ok=True
    required=['META/Audit-Selftest-current.csv','META/Audit-Selftest-current.json','META/Audit-Selftest-current.md','SCHEMA/Audit-Selftest-Fields-current.csv','tools/audit_selftest.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing audit selftest files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Audit-Selftest-current.csv')
    bad=[r.get('selftest_id','') for r in rows if r.get('status')!='pass']
    if len(rows)<6:
        ok=False; messages.append(f'Audit-Selftest has only {len(rows)} rows')
    if bad:
        ok=False; messages.append('Audit-Selftest failures: ' + '; '.join(bad[:8]))
    if not messages: messages.append(f'audit selftest proves {len(rows)} controlled mutations are caught')
    return ok, messages


def rebuild_readiness_audit_checks(root: Path):
    messages=[]; ok=True
    required=['META/Rebuild-Readiness-Audit-current.csv','META/Rebuild-Readiness-Audit-current.json','META/Rebuild-Readiness-Audit-current.md','SCHEMA/Rebuild-Readiness-Audit-Fields-current.csv','tools/rebuild_readiness_audit.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing rebuild-readiness audit files: ' + '; '.join(missing[:8])]
    try:
        rows=json.loads((root/'META/Rebuild-Readiness-Audit-current.json').read_text(encoding='utf-8'))
        high=[r for r in rows if r.get('severity')=='high']
        if high:
            ok=False; messages.append(f'Rebuild-Readiness-Audit-current.json has {len(high)} high findings')
        if not rows:
            ok=False; messages.append('Rebuild-Readiness-Audit has no rows')
    except Exception as e:
        ok=False; messages.append(f'rebuild-readiness audit JSON invalid: {e}')
    if not messages: messages.append('rebuild-readiness audit files present; zero high findings')
    return ok, messages


def policy_assertion_matrix_checks(root: Path):
    messages=[]; ok=True
    required=['META/Policy-Assertion-Matrix-current.csv','META/Policy-Assertion-Matrix-current.json','META/Policy-Assertion-Matrix-current.md','SCHEMA/Policy-Assertion-Matrix-Fields-current.csv','tools/policy_assertion_matrix.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing policy-assertion matrix files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Policy-Assertion-Matrix-current.csv')
    bad=[r.get('assertion_id','') for r in rows if r.get('status')!='pass']
    if not rows:
        ok=False; messages.append('Policy-Assertion-Matrix has no rows')
    if bad:
        ok=False; messages.append('Policy-Assertion-Matrix non-pass assertions: ' + '; '.join(bad[:8]))
    if not messages: messages.append(f'policy assertion matrix maps {len(rows)} claims to gates/tools/reports with all pass')
    return ok, messages


def regeneration_sequence_plan_checks(root: Path):
    messages=[]; ok=True
    required=['META/Regeneration-Sequence-Plan-current.csv','META/Regeneration-Sequence-Plan-current.json','META/Regeneration-Sequence-Plan-current.md','SCHEMA/Regeneration-Sequence-Plan-Fields-current.csv','tools/regeneration_sequence_plan.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing regeneration-sequence plan files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Regeneration-Sequence-Plan-current.csv')
    bad=[r.get('step_id','') for r in rows if r.get('dependency_status')!='pass']
    if not rows:
        ok=False; messages.append('Regeneration-Sequence-Plan has no rows')
    if bad:
        ok=False; messages.append('Regeneration-Sequence-Plan missing dependencies: ' + '; '.join(bad[:8]))
    if not messages: messages.append(f'regeneration sequence plan covers {len(rows)} generator steps with no missing dependencies')
    return ok, messages


def archive_build_manifest_checks(root: Path):
    messages=[]; ok=True
    required=['META/Archive-Build-Manifest-current.csv','META/Archive-Build-Manifest-current.json','META/Archive-Build-Manifest-current.md','SCHEMA/Archive-Build-Manifest-Fields-current.csv','tools/archive_build_manifest.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing archive-build manifest files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Archive-Build-Manifest-current.csv')
    bad=[r.get('build_check_id','') for r in rows if r.get('status')!='pass']
    if not rows:
        ok=False; messages.append('Archive-Build-Manifest has no rows')
    if bad:
        ok=False; messages.append('Archive-Build-Manifest non-pass checks: ' + '; '.join(bad[:8]))
    if not messages: messages.append(f'archive build manifest records {len(rows)} package/ZIP invariants with all pass')
    return ok, messages


def selftest_coverage_matrix_checks(root: Path):
    messages=[]; ok=True
    required=['META/Selftest-Coverage-Matrix-current.csv','META/Selftest-Coverage-Matrix-current.json','META/Selftest-Coverage-Matrix-current.md','SCHEMA/Selftest-Coverage-Matrix-Fields-current.csv','tools/selftest_coverage_matrix.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing selftest-coverage matrix files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Selftest-Coverage-Matrix-current.csv')
    bad=[r.get('coverage_id','') for r in rows if r.get('coverage_status')!='pass']
    if len(rows)<6:
        ok=False; messages.append(f'Selftest-Coverage-Matrix has only {len(rows)} rows')
    if bad:
        ok=False; messages.append('Selftest-Coverage-Matrix non-pass rows: ' + '; '.join(bad[:8]))
    if not messages: messages.append(f'selftest coverage matrix maps {len(rows)} critical gates to controlled mutations')
    return ok, messages


def checksum_scope_audit_checks(root: Path):
    messages=[]; ok=True
    required=['META/Checksum-Scope-Audit-current.csv','META/Checksum-Scope-Audit-current.json','META/Checksum-Scope-Audit-current.md','SCHEMA/Checksum-Scope-Audit-Fields-current.csv','tools/checksum_scope_audit.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing checksum-scope audit files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Checksum-Scope-Audit-current.csv')
    bad=[r.get('scope_check_id','') for r in rows if r.get('severity')=='high' or r.get('status')=='fail']
    if not rows:
        ok=False; messages.append('Checksum-Scope-Audit has no rows')
    if bad:
        ok=False; messages.append('Checksum-Scope-Audit high/fail rows: ' + '; '.join(bad[:8]))
    if not messages: messages.append('checksum-scope audit covers stable package scope with no high/fail rows')
    return ok, messages


def public_negative_corpus_checks(root: Path):
    messages=[]; ok=True
    required=['META/Public-Negative-Corpus-current.csv','META/Public-Negative-Corpus-current.json','META/Public-Negative-Corpus-current.md','SCHEMA/Public-Negative-Corpus-Fields-current.csv','tools/public_negative_corpus.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing public-negative-corpus files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Public-Negative-Corpus-current.csv')
    bad=[r.get('test_id','') for r in rows if r.get('status')!='pass']
    if len(rows)<8:
        ok=False; messages.append(f'Public-Negative-Corpus has only {len(rows)} fixtures')
    if bad:
        ok=False; messages.append('Public-Negative-Corpus failed fixtures: ' + '; '.join(bad[:8]))
    if not messages: messages.append(f'public negative corpus proves {len(rows)} unsafe fixtures are caught')
    return ok, messages


def release_evidence_closure_checks(root: Path):
    messages=[]; ok=True
    required=['META/Release-Evidence-Closure-current.csv','META/Release-Evidence-Closure-current.json','META/Release-Evidence-Closure-current.md','SCHEMA/Release-Evidence-Closure-Fields-current.csv','tools/release_evidence_closure.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing release-evidence-closure files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Release-Evidence-Closure-current.csv')
    bad=[r.get('closure_check_id','') for r in rows if r.get('severity')=='high' or r.get('status')=='fail']
    if not rows:
        ok=False; messages.append('Release-Evidence-Closure has no rows')
    if bad:
        ok=False; messages.append('Release-Evidence-Closure high/fail rows: ' + '; '.join(bad[:8]))
    if not messages: messages.append('release-evidence closure has no high/fail rows')
    return ok, messages


def archive_member_manifest_checks(root: Path):
    messages=[]; ok=True
    required=['META/Archive-Member-Manifest-current.csv','META/Archive-Member-Manifest-current.json','META/Archive-Member-Manifest-current.md','SCHEMA/Archive-Member-Manifest-Fields-current.csv','tools/archive_member_manifest.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing archive-member manifest files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Archive-Member-Manifest-current.csv')
    bad=[r.get('package_path','') for r in rows if r.get('status')!='pass']
    if len(rows)<100:
        ok=False; messages.append(f'Archive-Member-Manifest has only {len(rows)} rows')
    if bad:
        ok=False; messages.append('Archive-Member-Manifest non-pass rows: ' + '; '.join(bad[:8]))
    if not messages: messages.append(f'archive-member manifest records {len(rows)} intended ZIP members with all rows pass')
    return ok, messages


def unicode_path_audit_checks(root: Path):
    messages=[]; ok=True
    required=['META/Unicode-Path-Audit-current.csv','META/Unicode-Path-Audit-current.json','META/Unicode-Path-Audit-current.md','SCHEMA/Unicode-Path-Audit-Fields-current.csv','tools/unicode_path_audit.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing Unicode-path audit files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Unicode-Path-Audit-current.csv')
    bad=[r.get('check','') for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    if not rows:
        ok=False; messages.append('Unicode-Path-Audit has no rows')
    if bad:
        ok=False; messages.append('Unicode-Path-Audit high/fail rows: ' + '; '.join(bad[:8]))
    if not messages: messages.append('Unicode/path audit has zero high failures')
    return ok, messages


def package_identity_audit_checks(root: Path):
    messages=[]; ok=True
    required=['META/Package-Identity-Audit-current.csv','META/Package-Identity-Audit-current.json','META/Package-Identity-Audit-current.md','SCHEMA/Package-Identity-Audit-Fields-current.csv','tools/package_identity_audit.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing package-identity audit files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Package-Identity-Audit-current.csv')
    bad=[r.get('identity_check_id','') for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    if not rows:
        ok=False; messages.append('Package-Identity-Audit has no rows')
    if bad:
        ok=False; messages.append('Package-Identity-Audit high/fail rows: ' + '; '.join(bad[:8]))
    if not messages: messages.append('package identity audit has zero high failures')
    return ok, messages


def version_lineage_audit_checks(root: Path):
    messages=[]; ok=True
    required=['META/Version-Lineage-Audit-current.csv','META/Version-Lineage-Audit-current.json','META/Version-Lineage-Audit-current.md','tools/version_lineage_audit.py','META/Previous-Release-Fingerprint-current.json']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing version-lineage files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Version-Lineage-Audit-current.csv')
    bad=[r.get('lineage_check_id','') for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    if not rows: ok=False; messages.append('Version-Lineage-Audit has no rows')
    if bad: ok=False; messages.append('Version-Lineage-Audit high/fail rows: ' + '; '.join(bad[:8]))
    if not messages: messages.append('version lineage audit has zero high failures')
    return ok, messages

def package_delta_manifest_checks(root: Path):
    messages=[]; ok=True
    required=['META/Package-Delta-Manifest-current.csv','META/Package-Delta-Manifest-current.json','META/Package-Delta-Manifest-current.md','tools/package_delta_manifest.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing package-delta files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Package-Delta-Manifest-current.csv')
    removed=[r.get('path','') for r in rows if r.get('change_type')=='removed' or r.get('status')=='fail']
    added=sum(1 for r in rows if r.get('change_type')=='added')
    modified=sum(1 for r in rows if r.get('change_type')=='modified')
    if not rows: ok=False; messages.append('Package-Delta-Manifest has no rows')
    if removed: ok=False; messages.append('Package-Delta-Manifest removed/fail rows: ' + '; '.join(removed[:8]))
    if not messages: messages.append(f'package delta manifest has no removed rows; added={added} modified={modified}')
    return ok, messages

def cross_report_reference_audit_checks(root: Path):
    messages=[]; ok=True
    required=['META/Cross-Report-Reference-Audit-current.csv','META/Cross-Report-Reference-Audit-current.json','META/Cross-Report-Reference-Audit-current.md','tools/cross_report_reference_audit.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing cross-report reference files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Cross-Report-Reference-Audit-current.csv')
    bad=[r.get('reference_check_id','') for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    if not rows: ok=False; messages.append('Cross-Report-Reference-Audit has no rows')
    if bad: ok=False; messages.append('Cross-Report-Reference-Audit high/fail rows: ' + '; '.join(bad[:8]))
    if not messages: messages.append('cross-report reference audit has zero high failures')
    return ok, messages

def handoff_review_digest_checks(root: Path):
    messages=[]; ok=True
    required=['META/Handoff-Review-Digest-current.csv','META/Handoff-Review-Digest-current.json','META/Handoff-Review-Digest-current.md','tools/handoff_review_digest.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing handoff-review digest files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Handoff-Review-Digest-current.csv')
    bad=[r.get('digest_id','') for r in rows if r.get('status')!='pass']
    try:
        manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    except Exception:
        manifest={}
    expected_rev=manifest.get('revision','')
    expected_export=manifest.get('export_name_without_zip','')
    by_topic={r.get('topic',''):r.get('value','') for r in rows}
    stale=[]
    if expected_rev and by_topic.get('revision')!=expected_rev:
        stale.append(f"revision={by_topic.get('revision','')} expected {expected_rev}")
    if expected_export and by_topic.get('export_name_without_zip')!=expected_export:
        stale.append('export_name_without_zip mismatch')
    if not rows: ok=False; messages.append('Handoff-Review-Digest has no rows')
    if bad: ok=False; messages.append('Handoff-Review-Digest non-pass rows: ' + '; '.join(bad[:8]))
    if stale: ok=False; messages.append('Handoff-Review-Digest stale identity values: ' + '; '.join(stale[:4]))
    if not messages: messages.append('handoff review digest has no non-pass rows and matches manifest revision/export')
    return ok, messages

def dependency_cycle_audit_checks(root: Path):
    messages=[]; ok=True
    required=['META/Dependency-Cycle-Audit-current.csv','META/Dependency-Cycle-Audit-current.json','META/Dependency-Cycle-Audit-current.md','SCHEMA/Dependency-Cycle-Audit-Fields-current.csv','tools/dependency_cycle_audit.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing dependency-cycle audit files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Dependency-Cycle-Audit-current.csv')
    bad=[r.get('cycle_id','') for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    if not rows: ok=False; messages.append('Dependency-Cycle-Audit has no rows')
    if bad: ok=False; messages.append('Dependency-Cycle-Audit high/fail rows: ' + '; '.join(bad[:8]))
    if not messages: messages.append('dependency-cycle audit has zero high failures')
    return ok, messages


def handoff_notice_audit_checks(root: Path):
    messages=[]; ok=True
    required=['GOVERNANCE/Handoff-Use-Limits-and-Reviewer-Notice-current.md','META/Handoff-Notice-Audit-current.csv','META/Handoff-Notice-Audit-current.json','META/Handoff-Notice-Audit-current.md','SCHEMA/Handoff-Notice-Audit-Fields-current.csv','tools/handoff_notice_audit.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing handoff-notice audit files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Handoff-Notice-Audit-current.csv')
    bad=[r.get('notice_check_id','') for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    if not rows: ok=False; messages.append('Handoff-Notice-Audit has no rows')
    if bad: ok=False; messages.append('Handoff-Notice-Audit high/fail rows: ' + '; '.join(bad[:8]))
    if not messages: messages.append('handoff-notice audit has zero high failures')
    return ok, messages


def current_surface_registry_checks(root: Path):
    messages=[]; ok=True
    required=['META/Current-Surface-Registry-current.csv','META/Current-Surface-Registry-current.json','META/Current-Surface-Registry-current.md','SCHEMA/Current-Surface-Registry-Fields-current.csv','tools/current_surface_registry.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing current-surface registry files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Current-Surface-Registry-current.csv')
    bad=[r.get('surface_path','') for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    if not rows: ok=False; messages.append('Current-Surface-Registry has no rows')
    if bad: ok=False; messages.append('Current-Surface-Registry high/fail rows: ' + '; '.join(bad[:8]))
    if not messages: messages.append('current-surface registry has no unclassified/high-fail rows')
    return ok, messages




def current_surface_freshness_audit_checks(root: Path):
    messages=[]; ok=True
    required=['META/Current-Surface-Freshness-Audit-current.csv','META/Current-Surface-Freshness-Audit-current.json','META/Current-Surface-Freshness-Audit-current.md','SCHEMA/Current-Surface-Freshness-Audit-Fields-current.csv','SCHEMA/Current-Surface-Freshness-Audit-Fields-current.json','SCHEMA/Current-Surface-Freshness-Audit-Fields-current.md','tools/current_surface_freshness_audit.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing current-surface freshness audit files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Current-Surface-Freshness-Audit-current.csv')
    bad=[r.get('freshness_id','')+': '+r.get('surface_path','')+' '+r.get('check','') for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    if not rows: ok=False; messages.append('Current-Surface-Freshness-Audit has no rows')
    if bad: ok=False; messages.append('Current-Surface-Freshness-Audit high/fail rows: ' + '; '.join(bad[:8]))
    if not messages: messages.append(f'current-surface freshness audit has {len(rows)} rows and zero high failures')
    return ok, messages


def preservation_transfer_readiness_checks(root: Path):
    messages=[]; ok=True
    required=['META/Preservation-Transfer-Readiness-current.csv','META/Preservation-Transfer-Readiness-current.json','META/Preservation-Transfer-Readiness-current.md','SCHEMA/Preservation-Transfer-Readiness-Fields-current.csv','SCHEMA/Preservation-Transfer-Readiness-Fields-current.json','SCHEMA/Preservation-Transfer-Readiness-Fields-current.md','ro-crate-metadata.json','tools/preservation_transfer_readiness.py','tools/make_bagit_transfer_copy.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing preservation-transfer readiness files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Preservation-Transfer-Readiness-current.csv')
    bad=[r.get('readiness_id','')+': '+r.get('area','')+' '+r.get('check','') for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    if not rows: ok=False; messages.append('Preservation-Transfer-Readiness has no rows')
    if bad: ok=False; messages.append('Preservation-Transfer-Readiness high/fail rows: ' + '; '.join(bad[:8]))
    if not messages: messages.append(f'preservation-transfer readiness has {len(rows)} rows and zero high failures')
    return ok, messages


def regeneration_coverage_audit_checks(root: Path):
    messages=[]; ok=True
    required=['META/Regeneration-Coverage-Audit-current.csv','META/Regeneration-Coverage-Audit-current.json','META/Regeneration-Coverage-Audit-current.md','SCHEMA/Regeneration-Coverage-Audit-Fields-current.csv','SCHEMA/Regeneration-Coverage-Audit-Fields-current.json','SCHEMA/Regeneration-Coverage-Audit-Fields-current.md','tools/regeneration_coverage_audit.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing regeneration-coverage audit files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Regeneration-Coverage-Audit-current.csv')
    bad=[r.get('coverage_id','')+': '+r.get('surface_path','')+' '+r.get('coverage_class','') for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    summary=[r for r in rows if r.get('coverage_class')=='regeneration_coverage_summary']
    if not rows: ok=False; messages.append('Regeneration-Coverage-Audit has no rows')
    if bad: ok=False; messages.append('Regeneration-Coverage-Audit high/fail rows: ' + '; '.join(bad[:8]))
    if not summary: ok=False; messages.append('Regeneration-Coverage-Audit missing summary row')
    if not messages: messages.append(f'regeneration-coverage audit has {len(rows)} rows and zero high failures')
    return ok, messages

def manifest_semantic_coherence_audit_checks(root: Path):
    messages=[]; ok=True
    required=['META/Manifest-Semantic-Coherence-Audit-current.csv','META/Manifest-Semantic-Coherence-Audit-current.json','META/Manifest-Semantic-Coherence-Audit-current.md','SCHEMA/Manifest-Semantic-Coherence-Audit-Fields-current.csv','tools/manifest_semantic_coherence_audit.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing manifest-semantic coherence files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Manifest-Semantic-Coherence-Audit-current.csv')
    bad=[r.get('check_id','') for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    if not rows: ok=False; messages.append('Manifest-Semantic-Coherence-Audit has no rows')
    if bad: ok=False; messages.append('Manifest-Semantic-Coherence-Audit high/fail rows: ' + '; '.join(bad[:8]))
    if not messages: messages.append('manifest semantic coherence audit has zero high failures')
    return ok, messages


def json_key_uniqueness_audit_checks(root: Path):
    messages=[]; ok=True
    required=['META/JSON-Key-Uniqueness-Audit-current.csv','META/JSON-Key-Uniqueness-Audit-current.json','META/JSON-Key-Uniqueness-Audit-current.md','SCHEMA/JSON-Key-Uniqueness-Audit-Fields-current.csv','tools/json_key_uniqueness_audit.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing JSON-key uniqueness files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/JSON-Key-Uniqueness-Audit-current.csv')
    bad=[r.get('json_path','') for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    if not rows: ok=False; messages.append('JSON-Key-Uniqueness-Audit has no rows')
    if bad: ok=False; messages.append('JSON-Key-Uniqueness-Audit high/fail rows: ' + '; '.join(bad[:8]))
    if not messages: messages.append('JSON key uniqueness audit has zero high failures')
    return ok, messages


def review_role_boundary_audit_checks(root: Path):
    messages=[]; ok=True
    required=['GOVERNANCE/Review-Role-and-Handoff-Boundaries-current.md','META/Review-Role-Boundary-Audit-current.csv','META/Review-Role-Boundary-Audit-current.json','META/Review-Role-Boundary-Audit-current.md','SCHEMA/Review-Role-Boundary-Audit-Fields-current.csv','tools/review_role_boundary_audit.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing review-role boundary files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Review-Role-Boundary-Audit-current.csv')
    bad=[r.get('boundary_id','') for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    if not rows: ok=False; messages.append('Review-Role-Boundary-Audit has no rows')
    if bad: ok=False; messages.append('Review-Role-Boundary-Audit high/fail rows: ' + '; '.join(bad[:8]))
    if not messages: messages.append('review-role boundary audit has zero high failures')
    return ok, messages


def helper_adoption_audit_checks(root: Path):
    messages=[]; ok=True
    required=['META/Helper-Adoption-Audit-current.csv','META/Helper-Adoption-Audit-current.json','META/Helper-Adoption-Audit-current.md','SCHEMA/Helper-Adoption-Audit-Fields-current.csv','tools/helper_adoption_audit.py','tools/lib_cube.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing helper-adoption audit files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Helper-Adoption-Audit-current.csv')
    bad=[r.get('finding_id','') for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    if not rows: ok=False; messages.append('Helper-Adoption-Audit has no rows')
    if bad: ok=False; messages.append('Helper-Adoption-Audit high/fail rows: ' + '; '.join(bad[:8]))
    if not messages: messages.append('helper adoption audit has zero high failures')
    return ok, messages


def rev0065_hardening_checks(root: Path):
    messages=[]; ok=True
    required=[
        'RIGHTS-AND-USE-LIMITS.md','META/Data-Card-current.md','DATA-CARD-current.md','datapackage.json','BUILD-PROVENANCE-current.json','SIGNATURE-READINESS-current.md',
        'META/Archive-Roundtrip-Audit-current.csv','META/Current-Pointer-Coherence-Audit-current.csv','META/Source-Freshness-Preservation-current.csv','META/Evidence-Debt-Sprint-current.csv','GOVERNANCE/Permission-State-Ledger-current.csv','META/Office-Accountability-current.csv','META/Controlled-Vocabulary-Normalization-current.csv','META/Helper-Adoption-Scope-current.csv',
        'tools/archive_roundtrip_audit.py','tools/current_pointer_coherence_audit.py','tools/rev0065_governance_surfaces.py'
    ]
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing:
        ok=False; messages.append('missing rev0065 hardening files: '+ '; '.join(missing[:8]))
    for rel in ['META/Archive-Roundtrip-Audit-current.csv','META/Current-Pointer-Coherence-Audit-current.csv']:
        rows=csv_rows(root,rel)
        bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
        if not rows or bad:
            ok=False; messages.append(f'{rel} has high/fail rows or is empty')
    cand_ids={r.get('candidate_id','') for r in csv_rows(root,'Candidate-Ledger-current.csv')}
    perm_ids={r.get('candidate_id','') for r in csv_rows(root,'GOVERNANCE/Permission-State-Ledger-current.csv')}
    if cand_ids and cand_ids!=perm_ids:
        ok=False; messages.append(f'permission-state coverage mismatch: candidate_only={len(cand_ids-perm_ids)} permission_only={len(perm_ids-cand_ids)}')
    required_pairs={(r.get('candidate_id',''),oid) for r in csv_rows(root,'Candidate-Ledger-current.csv') for oid in (r.get('office_ids','') or '').split('|') if oid}
    acct_pairs={(r.get('candidate_id',''),r.get('office_id','')) for r in csv_rows(root,'META/Office-Accountability-current.csv')}
    if required_pairs and not required_pairs.issubset(acct_pairs):
        ok=False; messages.append(f'office-accountability missing pairs: {len(required_pairs-acct_pairs)}')
    source_ids={r.get('source_id','') for r in csv_rows(root,'Source-Registry-current.csv')}
    pres_ids={r.get('source_id','') for r in csv_rows(root,'META/Source-Freshness-Preservation-current.csv')}
    if source_ids and source_ids!=pres_ids:
        ok=False; messages.append(f'source preservation coverage mismatch: source_only={len(source_ids-pres_ids)} preservation_only={len(pres_ids-source_ids)}')
    if not messages:
        messages.append('rev0065 archive/governance/metadata hardening surfaces present and coherent')
    return ok, messages



def report_contract_registry_checks(root: Path):
    messages=[]; ok=True
    required=['META/Report-Contract-Registry-current.csv','META/Report-Contract-Registry-current.json','META/Report-Contract-Registry-current.md','META/Report-Contract-Audit-current.csv','META/Report-Contract-Audit-current.json','META/Report-Contract-Audit-current.md','SCHEMA/Report-Contract-Registry-Fields-current.csv','SCHEMA/Report-Contract-Audit-Fields-current.csv','tools/report_contract_registry.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing report-contract registry files: ' + '; '.join(missing[:8])]
    registry=csv_rows(root,'META/Report-Contract-Registry-current.csv')
    audit=csv_rows(root,'META/Report-Contract-Audit-current.csv')
    registry_bad=[r.get('surface_path','') for r in registry if r.get('status')!='pass']
    audit_bad=[r.get('audit_id','') for r in audit if r.get('severity')=='high' and r.get('status')!='pass']
    if not registry: ok=False; messages.append('Report-Contract-Registry has no rows')
    if not audit: ok=False; messages.append('Report-Contract-Audit has no rows')
    if registry_bad: ok=False; messages.append('Report-Contract-Registry non-pass rows: ' + '; '.join(registry_bad[:8]))
    if audit_bad: ok=False; messages.append('Report-Contract-Audit high/fail rows: ' + '; '.join(audit_bad[:8]))
    if not messages: messages.append(f'report-contract registry covers {len(registry)} current CSV surfaces with zero high failures')
    return ok, messages


def tool_executability_audit_checks(root: Path):
    messages=[]; ok=True
    required=['META/Tool-Executability-Audit-current.csv','META/Tool-Executability-Audit-current.json','META/Tool-Executability-Audit-current.md','SCHEMA/Tool-Executability-Audit-Fields-current.csv','tools/tool_executability_audit.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing tool-executability audit files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Tool-Executability-Audit-current.csv')
    bad=[r.get('tool_path','') for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    if not rows:
        ok=False; messages.append('Tool-Executability-Audit has no rows')
    if bad:
        ok=False; messages.append('Tool-Executability-Audit high/fail rows: ' + '; '.join(bad[:8]))
    if not messages: messages.append(f'tool-executability audit covers {len(rows)} packaged tools with zero high failures')
    return ok, messages


def boundary_domain_inheritance_checks(root: Path):
    messages=[]; ok=True
    required=['META/Boundary-Domain-Registry-current.csv','META/Boundary-Domain-Registry-current.json','META/Boundary-Domain-Registry-current.md','META/Candidate-Boundary-Domain-Map-current.csv','META/Candidate-Boundary-Domain-Map-current.json','META/Candidate-Boundary-Domain-Map-current.md','META/Boundary-Domain-Coverage-Audit-current.csv','META/Boundary-Domain-Coverage-Audit-current.json','META/Boundary-Domain-Coverage-Audit-current.md','SCHEMA/Boundary-Domain-Registry-Fields-current.csv','SCHEMA/Candidate-Boundary-Domain-Map-Fields-current.csv','SCHEMA/Boundary-Domain-Coverage-Audit-Fields-current.csv','tools/boundary_domain_map.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing boundary-domain inheritance files: ' + '; '.join(missing[:8])]
    registry=csv_rows(root,'META/Boundary-Domain-Registry-current.csv')
    mapping=csv_rows(root,'META/Candidate-Boundary-Domain-Map-current.csv')
    audit=csv_rows(root,'META/Boundary-Domain-Coverage-Audit-current.csv')
    bad=[r.get('audit_id','') for r in audit if r.get('severity')=='high' and r.get('status')!='pass']
    cand_ids={r.get('candidate_id','') for r in csv_rows(root,'Candidate-Ledger-current.csv')}
    mapped_ids={r.get('candidate_id','') for r in mapping}
    domain_ids={r.get('domain_id','') for r in registry}
    mapped_domains={r.get('domain_id','') for r in mapping}
    if len(registry)<8: ok=False; messages.append(f'Boundary-Domain-Registry has only {len(registry)} rows')
    if not mapping: ok=False; messages.append('Candidate-Boundary-Domain-Map has no rows')
    if cand_ids and cand_ids-mapped_ids: ok=False; messages.append(f'candidate ids without any boundary domain: {len(cand_ids-mapped_ids)}')
    if mapped_domains-domain_ids: ok=False; messages.append('map uses unknown domain ids: ' + '; '.join(sorted(mapped_domains-domain_ids)[:8]))
    if bad: ok=False; messages.append('Boundary-Domain-Coverage-Audit high/fail rows: ' + '; '.join(bad[:8]))
    if not messages: messages.append(f'boundary-domain inheritance maps {len(mapped_ids)} candidates into {len(domain_ids)} governed domains with zero high failures')
    return ok, messages


def identifier_namespace_audit_checks(root: Path):
    messages=[]; ok=True
    required=['META/Identifier-Registry-current.csv','META/Identifier-Registry-current.json','META/Identifier-Registry-current.md','META/Identifier-Convention-Audit-current.csv','META/Identifier-Convention-Audit-current.json','META/Identifier-Convention-Audit-current.md','SCHEMA/Identifier-Registry-Fields-current.csv','SCHEMA/Identifier-Convention-Audit-Fields-current.csv','tools/identifier_namespace_audit.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing identifier-namespace audit files: ' + '; '.join(missing[:8])]
    registry=csv_rows(root,'META/Identifier-Registry-current.csv')
    audit=csv_rows(root,'META/Identifier-Convention-Audit-current.csv')
    bad_registry=[r.get('identifier','') for r in registry if r.get('namespace_status')!='pass']
    bad_audit=[r.get('audit_id','') for r in audit if r.get('severity')=='high' and r.get('status')!='pass']
    kinds={r.get('identifier_kind','') for r in registry}
    required_kinds={'candidate_id','office_id','source_id','claim_id','debt_id','refresh_id','boundary_domain_id','release_gate_id'}
    missing_kinds=sorted(required_kinds-kinds)
    if not registry: ok=False; messages.append('Identifier-Registry has no rows')
    if not audit: ok=False; messages.append('Identifier-Convention-Audit has no rows')
    if bad_registry: ok=False; messages.append('identifier registry non-pass namespace rows: ' + '; '.join(bad_registry[:8]))
    if bad_audit: ok=False; messages.append('identifier convention audit high/fail rows: ' + '; '.join(bad_audit[:8]))
    if missing_kinds: ok=False; messages.append('identifier registry missing required kinds: ' + '; '.join(missing_kinds))
    if not messages: messages.append(f'identifier namespace audit tracks {len(registry)} identifiers across {len(kinds)} kinds with zero high failures')
    return ok, messages



def claim_source_boundary_audit_checks(root: Path):
    messages=[]; ok=True
    required=['META/Claim-Source-Boundary-Matrix-current.csv','META/Claim-Source-Boundary-Matrix-current.json','META/Claim-Source-Boundary-Matrix-current.md','META/Claim-Source-Boundary-Audit-current.csv','META/Claim-Source-Boundary-Audit-current.json','META/Claim-Source-Boundary-Audit-current.md','SCHEMA/Claim-Source-Boundary-Matrix-Fields-current.csv','SCHEMA/Claim-Source-Boundary-Audit-Fields-current.csv','tools/claim_source_boundary_audit.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing claim-source boundary audit files: ' + '; '.join(missing[:8])]
    matrix=csv_rows(root,'META/Claim-Source-Boundary-Matrix-current.csv')
    audit=csv_rows(root,'META/Claim-Source-Boundary-Audit-current.csv')
    matrix_bad=[r.get('matrix_id','') for r in matrix if r.get('status')!='pass']
    audit_bad=[r.get('audit_id','') for r in audit if r.get('severity')=='high' and r.get('status')!='pass']
    if not matrix: ok=False; messages.append('Claim-Source-Boundary-Matrix has no rows')
    if not audit: ok=False; messages.append('Claim-Source-Boundary-Audit has no rows')
    if matrix_bad: ok=False; messages.append('Claim-Source-Boundary-Matrix non-pass rows: ' + '; '.join(matrix_bad[:8]))
    if audit_bad: ok=False; messages.append('Claim-Source-Boundary-Audit high/fail rows: ' + '; '.join(audit_bad[:8]))
    if not messages: messages.append(f'claim-source boundary matrix tracks {len(matrix)} claim-source links with zero high failures')
    return ok, messages


def candidate_discovery_intake_audit_checks(root: Path):
    messages=[]; ok=True
    required=['META/Candidate-Discovery-Log-current.csv','META/Candidate-Discovery-Log-current.json','META/Candidate-Discovery-Log-current.md','META/Candidate-Discovery-Intake-Audit-current.csv','META/Candidate-Discovery-Intake-Audit-current.json','META/Candidate-Discovery-Intake-Audit-current.md','SCHEMA/Candidate-Discovery-Log-Fields-current.csv','SCHEMA/Candidate-Discovery-Intake-Audit-Fields-current.csv','tools/candidate_discovery_intake_audit.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing candidate-discovery intake files: ' + '; '.join(missing[:8])]
    log=csv_rows(root,'META/Candidate-Discovery-Log-current.csv')
    audit=csv_rows(root,'META/Candidate-Discovery-Intake-Audit-current.csv')
    audit_bad=[r.get('audit_id','') for r in audit if r.get('severity')=='high' and r.get('status')!='pass']
    promoted=[r.get('proposed_candidate_id','') for r in log if r.get('discovery_status')=='promoted_to_candidate']
    cand_ids={r.get('candidate_id','') for r in csv_rows(root,'Candidate-Ledger-current.csv')}
    missing_promoted=[cid for cid in promoted if cid not in cand_ids]
    if not log: ok=False; messages.append('Candidate-Discovery-Log has no rows')
    if not audit: ok=False; messages.append('Candidate-Discovery-Intake-Audit has no rows')
    if audit_bad: ok=False; messages.append('candidate-discovery intake high/fail rows: ' + '; '.join(audit_bad[:8]))
    if missing_promoted: ok=False; messages.append('promoted discovery candidates missing from Candidate-Ledger: ' + '; '.join(missing_promoted[:8]))
    if not messages: messages.append(f'candidate-discovery intake log records {len(log)} attempts with {len(promoted)} promoted candidate(s) and zero high failures')
    return ok, messages



def source_maintenance_priority_checks(root: Path):
    messages=[]; ok=True
    required=['META/Source-Maintenance-Priority-current.csv','META/Source-Maintenance-Priority-current.json','META/Source-Maintenance-Priority-current.md','META/Source-Preservation-Status-current.csv','META/Source-Preservation-Status-current.json','META/Source-Preservation-Status-current.md','META/Source-Safety-Nearmiss-Audit-current.csv','META/Source-Safety-Nearmiss-Audit-current.json','META/Source-Safety-Nearmiss-Audit-current.md','META/Source-URL-Integrity-Audit-current.csv','META/Source-URL-Integrity-Audit-current.json','META/Source-URL-Integrity-Audit-current.md','META/Source-Manual-Preservation-Decision-current.csv','META/Source-Manual-Preservation-Decision-current.json','META/Source-Manual-Preservation-Decision-current.md','SCHEMA/Source-Maintenance-Priority-Fields-current.csv','SCHEMA/Source-Preservation-Status-Fields-current.csv','SCHEMA/Source-Safety-Nearmiss-Audit-Fields-current.csv','SCHEMA/Source-URL-Integrity-Audit-Fields-current.csv','SCHEMA/Source-Manual-Preservation-Decision-Fields-current.csv','tools/source_maintenance_priority.py','tools/source_preservation_status.py','tools/source_freshness_preservation.py','tools/source_safety_nearmiss_audit.py','tools/source_url_integrity_audit.py','tools/source_manual_preservation_decision.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing source-maintenance/preservation files: ' + '; '.join(missing[:8])]
    source_ids={r.get('source_id','') for r in csv_rows(root,'Source-Registry-current.csv')}
    maint=csv_rows(root,'META/Source-Maintenance-Priority-current.csv')
    preserve=csv_rows(root,'META/Source-Preservation-Status-current.csv')
    freshness=csv_rows(root,'META/Source-Freshness-Preservation-current.csv')
    maint_ids={r.get('source_id','') for r in maint}
    preserve_ids={r.get('source_id','') for r in preserve}
    fresh_ids={r.get('source_id','') for r in freshness}
    nearmiss=csv_rows(root,'META/Source-Safety-Nearmiss-Audit-current.csv')
    url_integrity=csv_rows(root,'META/Source-URL-Integrity-Audit-current.csv')
    manual_decisions=csv_rows(root,'META/Source-Manual-Preservation-Decision-current.csv')
    if source_ids != maint_ids:
        ok=False; messages.append(f'source maintenance coverage mismatch source_only={len(source_ids-maint_ids)} maintenance_only={len(maint_ids-source_ids)}')
    if source_ids != preserve_ids:
        ok=False; messages.append(f'source preservation coverage mismatch source_only={len(source_ids-preserve_ids)} preservation_only={len(preserve_ids-source_ids)}')
    if source_ids != fresh_ids:
        ok=False; messages.append(f'source freshness coverage mismatch source_only={len(source_ids-fresh_ids)} freshness_only={len(fresh_ids-source_ids)}')
    url_ids={r.get('source_id','') for r in url_integrity}
    if source_ids != url_ids:
        ok=False; messages.append(f'source URL-integrity coverage mismatch source_only={len(source_ids-url_ids)} url_only={len(url_ids-source_ids)}')
    bad_maint=[r.get('source_id','') for r in maint if r.get('status')=='fail']
    bad_preserve=[r.get('source_id','') for r in preserve if r.get('status')=='fail']
    bad_fresh=[r.get('source_id','') for r in freshness if r.get('status')=='review_manual_recheck_policy']
    if bad_maint: ok=False; messages.append('source maintenance fail rows: ' + '; '.join(bad_maint[:8]))
    if bad_preserve: ok=False; messages.append('source preservation fail rows: ' + '; '.join(bad_preserve[:8]))
    if bad_fresh: ok=False; messages.append('source freshness manual-recheck policy errors: ' + '; '.join(bad_fresh[:8]))
    bad_nearmiss=[r.get('source_id','') for r in nearmiss if r.get('severity')=='high' and r.get('status')!='pass']
    if not nearmiss:
        ok=False; messages.append('source safety near-miss audit has no rows')
    if bad_nearmiss:
        ok=False; messages.append('source safety near-miss high failures: ' + '; '.join(bad_nearmiss[:8]))
    bad_url=[r.get('source_id','') for r in url_integrity if r.get('severity')=='high' and r.get('status')!='pass']
    bad_decisions=[r.get('source_id','') for r in manual_decisions if r.get('severity')=='high' and r.get('status')!='pass']
    if not manual_decisions:
        ok=False; messages.append('source manual-preservation-decision audit has no rows')
    if bad_decisions:
        ok=False; messages.append('source manual-preservation-decision high failures: ' + '; '.join(bad_decisions[:8]))
    if not url_integrity:
        ok=False; messages.append('source URL integrity audit has no rows')
    if bad_url:
        ok=False; messages.append('source URL integrity high failures: ' + '; '.join(bad_url[:8]))
    fresh_bytes=(root/'META/Source-Freshness-Preservation-current.csv').read_bytes()
    pres_bytes=(root/'META/Source-Preservation-Status-current.csv').read_bytes()
    if fresh_bytes == pres_bytes:
        ok=False; messages.append('Source-Preservation-Status is byte-identical to Source-Freshness-Preservation; refactor regression')
    p1=sum(1 for r in maint if (r.get('maintenance_priority','') or '').startswith('p1_'))
    p0=sum(1 for r in maint if (r.get('maintenance_priority','') or '').startswith('p0_'))
    if p0:
        ok=False; messages.append(f'source maintenance still has {p0} P0 repair rows')
    if not messages: messages.append(f'source maintenance queue covers {len(maint)} sources; P1 actionable rows={p1}; preservation/freshness reports are distinct; source-safety near-miss rows={len(nearmiss)}; URL-integrity rows={len(url_integrity)}; manual-preservation decisions={len(manual_decisions)}')
    return ok, messages

def candidate_source_diversity_audit_checks(root: Path):
    messages=[]; ok=True
    required=['META/Candidate-Source-Diversity-Audit-current.csv','META/Candidate-Source-Diversity-Audit-current.json','META/Candidate-Source-Diversity-Audit-current.md','SCHEMA/Candidate-Source-Diversity-Audit-Fields-current.csv','tools/candidate_source_diversity_audit.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing candidate-source diversity audit files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Candidate-Source-Diversity-Audit-current.csv')
    bad=[r.get('audit_id','') for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    promoted=[r.get('proposed_candidate_id','') for r in csv_rows(root,'META/Candidate-Discovery-Log-current.csv') if r.get('discovery_status')=='promoted_to_candidate']
    if not rows: ok=False; messages.append('Candidate-Source-Diversity-Audit has no rows')
    if bad: ok=False; messages.append('candidate-source diversity high/fail rows: ' + '; '.join(bad[:8]))
    if not messages: messages.append(f'candidate-source diversity audit covers {len(promoted)} promoted candidates with zero high failures')
    return ok, messages



def normalized_code_overlay_checks(root: Path):
    messages=[]; ok=True
    required=['META/Normalized-Code-Overlay-current.csv','META/Normalized-Code-Overlay-current.json','META/Normalized-Code-Overlay-current.md','META/Normalized-Code-Overlay-Audit-current.csv','META/Normalized-Code-Overlay-Audit-current.json','META/Normalized-Code-Overlay-Audit-current.md','META/Controlled-Vocabulary-Normalization-current.csv','SCHEMA/Normalized-Code-Overlay-Fields-current.csv','SCHEMA/Normalized-Code-Overlay-Audit-Fields-current.csv','tools/ledger_code_overlay.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing normalized-code overlay files: ' + '; '.join(missing[:8])]
    overlay=csv_rows(root,'META/Normalized-Code-Overlay-current.csv')
    audit=csv_rows(root,'META/Normalized-Code-Overlay-Audit-current.csv')
    bad=[r.get('audit_id','')+': '+r.get('check','') for r in audit if r.get('severity')=='high' and r.get('status')!='pass']
    required_fields={'candidate_status_code','capacity_claim_code','community_authority_status','boundary_lift_authority','public_surface_code','source_harm_proximity_code','claim_evidence_status_code'}
    observed={r.get('normalized_code_field','') for r in overlay}
    cand_count=len(csv_rows(root,'Candidate-Ledger-current.csv'))
    source_count=len(csv_rows(root,'Source-Registry-current.csv'))
    claim_count=len(csv_rows(root,'Claim-Ledger-current.csv'))
    expected_min=(cand_count*5)+source_count+claim_count
    if not overlay: ok=False; messages.append('Normalized-Code-Overlay has no rows')
    if len(overlay) < expected_min:
        ok=False; messages.append(f'normalized-code overlay rows too low: {len(overlay)} < expected {expected_min}')
    if not required_fields.issubset(observed):
        ok=False; messages.append('normalized-code overlay missing code fields: ' + '; '.join(sorted(required_fields-observed)))
    if not audit: ok=False; messages.append('Normalized-Code-Overlay-Audit has no rows')
    if bad: ok=False; messages.append('normalized-code overlay high failures: ' + '; '.join(bad[:8]))
    if not messages: messages.append(f'normalized-code overlay covers {len(overlay)} companion code rows across {len(observed)} code fields with zero high failures')
    return ok, messages

def release_change_review_checks(root: Path):
    messages=[]; ok=True
    required=['META/Release-Change-Review-current.csv','META/Release-Change-Review-current.json','META/Release-Change-Review-current.md','SCHEMA/Release-Change-Review-Fields-current.csv','tools/release_change_review.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing release-change review files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Release-Change-Review-current.csv')
    bad=[r.get('review_id','')+': '+r.get('subject_path','') for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    sig=[r for r in rows if r.get('review_check')=='signature_doc_current_revision_and_key' and r.get('status')=='pass']
    summary=[r for r in rows if r.get('review_check')=='release_change_summary']
    if not rows:
        ok=False; messages.append('Release-Change-Review has no rows')
    if bad:
        ok=False; messages.append('release-change review high failures: ' + '; '.join(bad[:8]))
    if len(sig) < 2:
        ok=False; messages.append('signature readiness/status current-key checks missing')
    if not summary:
        ok=False; messages.append('release-change summary row missing')
    if not messages: messages.append(f'release-change review covers {len(rows)} rows with zero high failures and {len(sig)} signature proof checks')
    return ok, messages

def ledger_relationship_audit_checks(root: Path):
    messages=[]; ok=True
    required=['META/Ledger-Relationship-Audit-current.csv','META/Ledger-Relationship-Audit-current.json','META/Ledger-Relationship-Audit-current.md','SCHEMA/Ledger-Relationship-Audit-Fields-current.csv','tools/ledger_relationship_audit.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing ledger-relationship audit files: ' + '; '.join(missing[:8])]
    rows=csv_rows(root,'META/Ledger-Relationship-Audit-current.csv')
    bad=[r.get('relationship_id','')+': '+r.get('relationship_family','') for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    summary=[r for r in rows if r.get('relationship_family')=='relationship_audit_summary' and r.get('status')=='pass']
    if not rows:
        ok=False; messages.append('Ledger-Relationship-Audit has no rows')
    if bad:
        ok=False; messages.append('ledger-relationship high failures: ' + '; '.join(bad[:8]))
    if not summary:
        ok=False; messages.append('ledger-relationship summary row missing')
    families={r.get('relationship_family','') for r in rows}
    required_families={'claim_source_join','candidate_source_join','source_seen_in_file_path','claim_release_quarantine_pointer','normalized_overlay_target_join'}
    if not required_families.issubset(families):
        ok=False; messages.append('ledger-relationship missing families: ' + '; '.join(sorted(required_families-families)))
    if not messages: messages.append(f'ledger-relationship audit covers {len(rows)} rows across {len(families)} relationship families with zero high failures')
    return ok, messages


def public_export_surface_checks(root: Path):
    rows=csv_rows(root,'META/Public-Export-Surface-Audit-current.csv')
    if not rows:
        return False, ['public export surface audit missing']
    bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    bundle=root/'PUBLIC/PUBLIC-BUNDLE-MANIFEST-current.json'
    manifest=root/'manifest.json'
    ok_bundle=bundle.exists()
    try:
        b=json.loads(bundle.read_text(encoding='utf-8'))
        m=json.loads(manifest.read_text(encoding='utf-8'))
        public_only=all(str(p).startswith('PUBLIC/') for p in b.get('public_payload_files',[]))
        current=b.get('revision')==m.get('revision') and b.get('export_name_without_zip')==m.get('export_name_without_zip')
    except Exception:
        public_only=False; current=False
    ok=not bad and ok_bundle and public_only and current
    msg=f'public-export-surface audit rows={len(rows)} high_fail={len(bad)}; bundle_public_only={public_only}; bundle_current={current}'
    return ok, [msg] if ok else [msg] + [f"{r.get('audit_id')}: {r.get('check')} {r.get('observed_value')}" for r in bad[:6]]

def release_gate_attestation_checks(root: Path):
    messages=[]; ok=True
    required=['META/Release-Gate-Attestation-current.csv','META/Release-Gate-Attestation-current.json','META/Release-Gate-Attestation-current.md','tools/release_gate_attestation.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing: return False, ['missing release-gate attestation files: ' + '; '.join(missing[:8])]
    try:
        rows=json.loads((root/'META/Release-Gate-Attestation-current.json').read_text(encoding='utf-8'))
        fails=[r.get('gate_id','') for r in rows if r.get('status')!='pass']
        if len(rows)<10:
            ok=False; messages.append(f'Release-Gate-Attestation has only {len(rows)} gates')
        if fails:
            ok=False; messages.append('release-gate failures: ' + '; '.join(fails[:8]))
    except Exception as e:
        ok=False; messages.append(f'release-gate attestation JSON invalid: {e}')
    if not messages: messages.append('release-gate attestation files present; all gates pass')
    return ok, messages

def rule46_scan_checks(root: Path):
    messages=[]; ok=True
    required=['META/Rule46-Scan-current.csv','META/Rule46-Scan-current.json','META/Rule46-Scan-current.md','tools/rule46_scan.py']
    missing=[rel for rel in required if not (root/rel).exists()]
    if missing:
        return False, ['missing rule46 scan files: ' + '; '.join(missing)]
    try:
        data=json.loads((root/'META/Rule46-Scan-current.json').read_text(encoding='utf-8'))
        high=[r for r in data if r.get('severity')=='high']
        if high:
            ok=False; messages.append(f'Rule46-Scan-current.json has {len(high)} high findings')
    except Exception as e:
        ok=False; messages.append(f'Rule46 scan JSON invalid: {e}')
    if not messages:
        messages.append('rule46 scanner files present; zero high-risk MMIWG2S+ extraction findings')
    return ok, messages

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('root', nargs='?', default='.')
    args=ap.parse_args()
    root=Path(args.root).resolve()
    results=[]
    def add(name, ok, detail=''):
        results.append((name, ok, detail))
    add('no archive/archive dirs', not any(p.is_dir() and p.name.lower() in {'archive','archives'} for p in root.rglob('*')))
    add('no bundled zip files', not any(p.suffix.lower()=='.zip' for p in root.rglob('*')))
    add('no Python bytecode/cache artifacts', not any(p.name == '__pycache__' or p.suffix in {'.pyc','.pyo'} for p in root.rglob('*')))
    cands=[p for p in (root/'CANDIDATES').glob('*.txt') if not p.name.startswith('_REFRESH')]
    offices=list((root/'OFFICE-CARDS').glob('*.txt'))
    refresh=[p for p in (root/'CANDIDATES').glob('_REFRESH*.txt')]
    add('candidate front matter', all(has_frontmatter(p) for p in cands), f'{sum(has_frontmatter(p) for p in cands)}/{len(cands)}')
    add('office-card front matter', all(has_frontmatter(p) for p in offices), f'{sum(has_frontmatter(p) for p in offices)}/{len(offices)}')
    add('refresh-note front matter', all(has_frontmatter(p) for p in refresh), f'{sum(has_frontmatter(p) for p in refresh)}/{len(refresh)}')
    for fn, expected in [('Candidate-Ledger-current.csv', len(cands)), ('Office-Card-Index-current.csv', len(offices)), ('Refresh-Index-current.csv', len(refresh))]:
        p=root/fn
        if not p.exists(): add(fn, False, 'missing'); continue
        rows=list(csv.DictReader(p.open(encoding='utf-8')))
        add(fn, len(rows)==expected, f'{len(rows)} rows; expected {expected}')
    for fn in ['Claim-Ledger-current.csv','Source-Registry-current.csv','Evidence-Debt-current.csv','CUBE-MAP.md','PUBLIC/README-public-edition.md','Longform-Registry-current.md','manifest.json']:
        add(fn, (root/fn).exists(), 'exists' if (root/fn).exists() else 'missing')
    ledger=root/'Candidate-Ledger-current.csv'
    if ledger.exists():
        rows=list(csv.DictReader(ledger.open(encoding='utf-8')))
        missing=[r.get('candidate_id','') for r in rows if r.get('live_referral_safe','') not in {'false','true'}]
        add('live_referral_safe field populated', not missing, f'missing/invalid: {len(missing)}')
    ok,msgs=identity_checks(root)
    add('identity-coherence checks', ok, '; '.join(msgs[:5]))
    ok,msgs=reference_integrity_checks(root)
    add('reference-integrity checks', ok, '; '.join(msgs[:5]))
    ok,msgs=manifest_truth_checks(root)
    add('manifest-truth checks', ok, '; '.join(msgs[:5]))
    ok,msgs=longform_registry_checks(root)
    add('longform-registry checks', ok, '; '.join(msgs[:5]))
    ok,msgs=meta_instrument_checks(root)
    add('meta-instrument checks', ok, '; '.join(msgs[:5]))
    ok,msgs=redaction_risk_checks(root)
    add('redaction-risk checks', ok, '; '.join(msgs[:5]))
    ok,msgs=evidence_lifecycle_checks(root)
    add('evidence-lifecycle checks', ok, '; '.join(msgs[:5]))
    ok,msgs=schema_contract_checks(root)
    add('schema-contract checks', ok, '; '.join(msgs[:5]))
    ok,msgs=governance_layer_checks(root)
    add('governance-layer checks', ok, '; '.join(msgs[:5]))
    ok,msgs=public_release_lint_checks(root)
    add('public-release-lint checks', ok, '; '.join(msgs[:5]))
    ok,msgs=sensitive_surface_inventory_checks(root)
    add('sensitive-surface-inventory checks', ok, '; '.join(msgs[:5]))
    ok,msgs=candidate_governance_snapshot_checks(root)
    add('candidate-governance-snapshot checks', ok, '; '.join(msgs[:5]))
    ok,msgs=row_validation_checks(root)
    add('row-validation checks', ok, '; '.join(msgs[:5]))
    ok,msgs=revision_surface_audit_checks(root)
    add('revision-surface-audit checks', ok, '; '.join(msgs[:5]))
    ok,msgs=generated_artifact_provenance_checks(root)
    add('generated-artifact-provenance checks', ok, '; '.join(msgs[:5]))
    ok,msgs=public_index_parity_checks(root)
    add('public-index-parity checks', ok, '; '.join(msgs[:5]))
    ok,msgs=public_index_semantic_audit_checks(root)
    add('public-index-semantic-audit checks', ok, '; '.join(msgs[:5]))
    ok,msgs=governance_consistency_audit_checks(root)
    add('governance-consistency-audit checks', ok, '; '.join(msgs[:5]))
    ok,msgs=package_dependency_graph_checks(root)
    add('package-dependency-graph checks', ok, '; '.join(msgs[:5]))
    ok,msgs=csv_json_mirror_audit_checks(root)
    add('csv-json-mirror-audit checks', ok, '; '.join(msgs[:5]))
    ok,msgs=schema_coverage_audit_checks(root)
    add('schema-coverage-audit checks', ok, '; '.join(msgs[:5]))
    ok,msgs=package_file_inventory_checks(root)
    add('package-file-inventory checks', ok, '; '.join(msgs[:5]))
    ok,msgs=field_schema_consistency_checks(root)
    add('field-schema-consistency checks', ok, '; '.join(msgs[:5]))
    ok,msgs=path_reference_audit_checks(root)
    add('path-reference-audit checks', ok, '; '.join(msgs[:5]))
    ok,msgs=rule_gate_traceability_checks(root)
    add('rule-gate-traceability checks', ok, '; '.join(msgs[:5]))
    ok,msgs=tool_run_matrix_checks(root)
    add('tool-run-matrix checks', ok, '; '.join(msgs[:5]))
    ok,msgs=required_document_coverage_checks(root)
    add('required-document-coverage checks', ok, '; '.join(msgs[:5]))
    ok,msgs=audit_selftest_checks(root)
    add('audit-selftest checks', ok, '; '.join(msgs[:5]))
    ok,msgs=rebuild_readiness_audit_checks(root)
    add('rebuild-readiness-audit checks', ok, '; '.join(msgs[:5]))
    ok,msgs=policy_assertion_matrix_checks(root)
    add('policy-assertion-matrix checks', ok, '; '.join(msgs[:5]))
    ok,msgs=regeneration_sequence_plan_checks(root)
    add('regeneration-sequence-plan checks', ok, '; '.join(msgs[:5]))
    ok,msgs=archive_build_manifest_checks(root)
    add('archive-build-manifest checks', ok, '; '.join(msgs[:5]))
    ok,msgs=selftest_coverage_matrix_checks(root)
    add('selftest-coverage-matrix checks', ok, '; '.join(msgs[:5]))
    ok,msgs=checksum_scope_audit_checks(root)
    add('checksum-scope-audit checks', ok, '; '.join(msgs[:5]))
    ok,msgs=public_negative_corpus_checks(root)
    add('public-negative-corpus checks', ok, '; '.join(msgs[:5]))
    ok,msgs=release_evidence_closure_checks(root)
    add('release-evidence-closure checks', ok, '; '.join(msgs[:5]))
    ok,msgs=archive_member_manifest_checks(root)
    add('archive-member-manifest checks', ok, '; '.join(msgs[:5]))
    ok,msgs=unicode_path_audit_checks(root)
    add('unicode-path-audit checks', ok, '; '.join(msgs[:5]))
    ok,msgs=package_identity_audit_checks(root)
    add('package-identity-audit checks', ok, '; '.join(msgs[:5]))
    ok,msgs=version_lineage_audit_checks(root)
    add('version-lineage-audit checks', ok, '; '.join(msgs[:5]))
    ok,msgs=package_delta_manifest_checks(root)
    add('package-delta-manifest checks', ok, '; '.join(msgs[:5]))
    ok,msgs=cross_report_reference_audit_checks(root)
    add('cross-report-reference-audit checks', ok, '; '.join(msgs[:5]))
    ok,msgs=handoff_review_digest_checks(root)
    add('handoff-review-digest checks', ok, '; '.join(msgs[:5]))
    ok,msgs=dependency_cycle_audit_checks(root)
    add('dependency-cycle-audit checks', ok, '; '.join(msgs[:5]))
    ok,msgs=handoff_notice_audit_checks(root)
    add('handoff-notice-audit checks', ok, '; '.join(msgs[:5]))
    ok,msgs=current_surface_registry_checks(root)
    add('current-surface-registry checks', ok, '; '.join(msgs[:5]))
    ok,msgs=current_surface_freshness_audit_checks(root)
    add('current-surface-freshness-audit checks', ok, '; '.join(msgs[:5]))
    ok,msgs=preservation_transfer_readiness_checks(root)
    add('preservation-transfer-readiness checks', ok, '; '.join(msgs[:5]))
    ok,msgs=regeneration_coverage_audit_checks(root)
    add('regeneration-coverage-audit checks', ok, '; '.join(msgs[:5]))
    ok,msgs=manifest_semantic_coherence_audit_checks(root)
    add('manifest-semantic-coherence-audit checks', ok, '; '.join(msgs[:5]))
    ok,msgs=json_key_uniqueness_audit_checks(root)
    add('json-key-uniqueness-audit checks', ok, '; '.join(msgs[:5]))
    ok,msgs=review_role_boundary_audit_checks(root)
    add('review-role-boundary-audit checks', ok, '; '.join(msgs[:5]))
    ok,msgs=helper_adoption_audit_checks(root)
    add('helper-adoption-audit checks', ok, '; '.join(msgs[:5]))
    ok,msgs=rev0065_hardening_checks(root)
    add('rev0065-hardening checks', ok, '; '.join(msgs[:5]))
    ok,msgs=report_contract_registry_checks(root)
    add('report-contract-registry checks', ok, '; '.join(msgs[:5]))
    ok,msgs=tool_executability_audit_checks(root)
    add('tool-executability-audit checks', ok, '; '.join(msgs[:5]))
    ok,msgs=boundary_domain_inheritance_checks(root)
    add('boundary-domain-inheritance checks', ok, '; '.join(msgs[:5]))
    ok,msgs=identifier_namespace_audit_checks(root)
    add('identifier-namespace-audit checks', ok, '; '.join(msgs[:5]))
    ok,msgs=claim_source_boundary_audit_checks(root)
    add('claim-source-boundary-audit checks', ok, '; '.join(msgs[:5]))
    ok,msgs=candidate_discovery_intake_audit_checks(root)
    add('candidate-discovery-intake checks', ok, '; '.join(msgs[:5]))
    ok,msgs=source_maintenance_priority_checks(root)
    add('source-maintenance-priority checks', ok, '; '.join(msgs[:5]))
    ok,msgs=candidate_source_diversity_audit_checks(root)
    add('candidate-source-diversity checks', ok, '; '.join(msgs[:5]))
    ok,msgs=normalized_code_overlay_checks(root)
    add('normalized-code-overlay checks', ok, '; '.join(msgs[:5]))
    ok,msgs=release_change_review_checks(root)
    add('release-change-review checks', ok, '; '.join(msgs[:5]))
    ok,msgs=ledger_relationship_audit_checks(root)
    add('ledger-relationship-audit checks', ok, '; '.join(msgs[:5]))
    ok,msgs=release_gate_attestation_checks(root)
    add('release-gate-attestation checks', ok, '; '.join(msgs[:5]))
    ok,msgs=rule46_scan_checks(root)
    add('rule46-scan checks', ok, '; '.join(msgs[:5]))
    ok,msgs=sha_check(root)
    add('SHA256SUMS verification', ok, '; '.join(msgs[:5]))
    for name, ok, detail in results:
        print(('PASS' if ok else 'FAIL') + ' ' + name + (f' — {detail}' if detail else ''))
    if not all(ok for _,ok,_ in results):
        sys.exit(1)
if __name__=='__main__': main()
