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


def sha_check(root: Path):
    path=root/'SHA256SUMS.txt'
    if not path.exists(): return False, ['SHA256SUMS.txt missing']
    bad=[]; checked=0
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip(): continue
        try: digest, rel=line.split(None,1)
        except ValueError:
            bad.append(f'malformed line: {line[:80]}'); continue
        rel=rel.strip()
        if rel.startswith('./'): rel=rel[2:]
        f=root/rel
        if not f.exists(): bad.append(f'missing file in checksum: {rel}'); continue
        got=hashlib.sha256(f.read_bytes()).hexdigest()
        checked+=1
        if got!=digest: bad.append(f'checksum mismatch: {rel}')
    return not bad, [f'checked {checked} files'] + bad


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
            if cid in id_to_name and r.get('candidate_name', r.get('name','')) != id_to_name[cid]:
                ok=False; messages.append(f'{rel}: {cid} display name disagrees with Candidate-Ledger')
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
        'META/Public-Claim-Release-Ledger-current.csv','META/Public-Claim-Release-Ledger-current.json','META/Public-Claim-Release-Ledger-current.md'
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
    for rn in [str(n) for n in range(15,47)]:
        if rn not in got_rules:
            ok=False; messages.append(f'Boundary-Rule-Coverage missing rule {rn}')
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
        txt=p.read_text(encoding='utf-8', errors='ignore')
        for rx, typ in [(email_re,'email'),(coord_re,'coordinate'),(grave_re,'grave_or_case_id')]:
            for m in rx.finditer(txt):
                c=ctx(txt,m.start(),m.end())
                if any(ph in c.lower() for ph in placeholders): continue
                high.append(f'{typ}:{p.relative_to(root)}:{m.group(0)[:40]}')
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
    except Exception as e:
        ok=False; messages.append(f'public manifest revision check failed: {e}')
    if not messages:
        messages.append('schema contracts, ledger headers, JSON mirrors, source-type vocabulary, and public manifest checks pass')
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
    ok,msgs=sha_check(root)
    add('SHA256SUMS verification', ok, '; '.join(msgs[:5]))
    for name, ok, detail in results:
        print(('PASS' if ok else 'FAIL') + ' ' + name + (f' — {detail}' if detail else ''))
    if not all(ok for _,ok,_ in results):
        sys.exit(1)
if __name__=='__main__': main()
