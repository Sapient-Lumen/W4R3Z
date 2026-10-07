#!/usr/bin/env python3
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

sys.dont_write_bytecode = True
from lib_cube import read_csv_rows, write_csv_json_md_report

MATRIX_FIELDS = [
    'matrix_id','claim_id','candidate_id','candidate_name','claim_type','claim_status','overclaim_risk',
    'source_id','source_defined','source_type','evidence_roles','harm_proximity','public_link_policy',
    'safe_to_recheck_automatically','source_owner_type','source_candidate_reciprocity',
    'candidate_canonical_source_status','public_use_posture','capacity_or_referral_risk','status','note'
]

AUDIT_FIELDS = [
    'audit_id','check','claim_id','candidate_id','source_id','severity','status','detail','recommendation'
]

CONTACT_NEAR_POLICIES = {'internal_only_contact_rich','internal_only_image_sensitive','internal_only_case_or_family_sensitive'}
CAPACITY_PAT = re.compile(r'(?i)\b(current|capacity|available|availability|referral|refer|intake|hotline|helpline|shelter|safe house|service capacity|support path|legal advice|counsel(?:ling|ing)?)\b')


def split_pipe(value: str) -> list[str]:
    return [part for part in (value or '').split('|') if part]


def public_use_posture(source: dict[str, str]) -> str:
    policy = source.get('public_link_policy','')
    harm = source.get('harm_proximity','')
    if policy.startswith('internal_only'):
        return 'internal_evidence_only_no_public_url'
    if harm in {'contact_path_near','image_or_vigil_near','case_or_family_near'}:
        return 'manual_review_required_before_public_use'
    if policy == 'public_link_allowed_with_boundary_note':
        return 'boundary_note_required_before_public_link'
    if not policy:
        return 'unknown_policy_manual_review'
    return 'policy_bound_manual_review'


def source_reciprocity(source: dict[str, str], candidate_id: str) -> str:
    cids = set(split_pipe(source.get('candidate_ids','')))
    if not cids:
        return 'no_candidate_scope_declared'
    if candidate_id in cids:
        return 'pass'
    return 'fail_candidate_not_listed_on_source'


def canonical_source_status(candidate: dict[str, str], source_id: str) -> str:
    return 'pass' if source_id in set(split_pipe(candidate.get('source_ids',''))) else 'fail_source_not_listed_in_candidate_canonical_source_ids'


def capacity_risk(claim: dict[str, str], source: dict[str, str] | None) -> str:
    text = ' '.join([claim.get('claim_text',''), claim.get('evidence_text',''), claim.get('claim_status',''), claim.get('notes','')])
    source_policy = (source or {}).get('public_link_policy','')
    if CAPACITY_PAT.search(text) and source_policy.startswith('internal_only'):
        return 'capacity_or_referral_language_with_internal_only_source_boundary'
    if CAPACITY_PAT.search(text):
        return 'capacity_or_referral_language_requires_boundary_review'
    if source_policy.startswith('internal_only'):
        return 'internal_only_source_boundary_present'
    return 'no_configured_capacity_or_referral_signal'


def run(root: Path):
    claims = read_csv_rows(root/'Claim-Ledger-current.csv')
    candidates = {r.get('candidate_id',''): r for r in read_csv_rows(root/'Candidate-Ledger-current.csv')}
    sources = {r.get('source_id',''): r for r in read_csv_rows(root/'Source-Registry-current.csv')}
    link_review = {r.get('source_id',''): r for r in read_csv_rows(root/'META/Public-Source-Link-Review-current.csv')}

    matrix=[]
    audit=[]
    def add_audit(check: str, claim_id: str, candidate_id: str, source_id: str, severity: str, status: str, detail: str, recommendation: str):
        audit.append({
            'audit_id': f'claim_source_audit_{len(audit)+1:04d}',
            'check': check,
            'claim_id': claim_id,
            'candidate_id': candidate_id,
            'source_id': source_id,
            'severity': severity,
            'status': status,
            'detail': detail,
            'recommendation': recommendation,
        })

    for claim in claims:
        claim_id = claim.get('claim_id','')
        candidate_id = claim.get('candidate_id','')
        candidate = candidates.get(candidate_id, {})
        source_ids = split_pipe(claim.get('evidence_source_ids',''))
        if not source_ids:
            add_audit('claim_has_evidence_source_ids', claim_id, candidate_id, '', 'high', 'fail', 'claim has no evidence_source_ids', 'add source ids or explicitly quarantine the claim from release')
            continue
        else:
            add_audit('claim_has_evidence_source_ids', claim_id, candidate_id, '', 'info', 'pass', f'{len(source_ids)} source id(s) declared', 'keep claim-source evidence explicit')
        for source_id in source_ids:
            source = sources.get(source_id)
            if not source:
                matrix.append({
                    'matrix_id': f'claim_source_matrix_{len(matrix)+1:05d}',
                    'claim_id': claim_id,
                    'candidate_id': candidate_id,
                    'candidate_name': claim.get('candidate_name',''),
                    'claim_type': claim.get('claim_type',''),
                    'claim_status': claim.get('claim_status',''),
                    'overclaim_risk': claim.get('overclaim_risk',''),
                    'source_id': source_id,
                    'source_defined': 'false',
                    'source_type': '',
                    'evidence_roles': '',
                    'harm_proximity': '',
                    'public_link_policy': '',
                    'safe_to_recheck_automatically': '',
                    'source_owner_type': '',
                    'source_candidate_reciprocity': 'fail_source_missing',
                    'candidate_canonical_source_status': canonical_source_status(candidate, source_id) if candidate else 'candidate_missing',
                    'public_use_posture': 'source_missing_no_public_use',
                    'capacity_or_referral_risk': capacity_risk(claim, None),
                    'status': 'fail',
                    'note': 'source id referenced by claim is absent from Source-Registry-current.csv',
                })
                add_audit('claim_source_id_defined', claim_id, candidate_id, source_id, 'high', 'fail', 'source id is absent from Source-Registry-current.csv', 'add or correct Source Registry row before handoff')
                continue
            recip = source_reciprocity(source, candidate_id)
            canon = canonical_source_status(candidate, source_id) if candidate else 'candidate_missing'
            posture = public_use_posture(source)
            caprisk = capacity_risk(claim, source)
            link_decision = link_review.get(source_id, {}).get('public_url_release_decision','')
            status = 'pass'
            note_bits=[]
            if recip.startswith('fail'):
                status='fail'; note_bits.append('source candidate_ids do not include claim candidate')
            if canon.startswith('fail') or canon == 'candidate_missing':
                status='fail'; note_bits.append('candidate source_ids do not include claim source')
            if source.get('public_link_policy','').startswith('internal_only') and link_decision and not link_decision.startswith('block'):
                status='fail'; note_bits.append('internal-only source is not blocked by public source link review')
            matrix.append({
                'matrix_id': f'claim_source_matrix_{len(matrix)+1:05d}',
                'claim_id': claim_id,
                'candidate_id': candidate_id,
                'candidate_name': claim.get('candidate_name',''),
                'claim_type': claim.get('claim_type',''),
                'claim_status': claim.get('claim_status',''),
                'overclaim_risk': claim.get('overclaim_risk',''),
                'source_id': source_id,
                'source_defined': 'true',
                'source_type': source.get('source_type',''),
                'evidence_roles': source.get('evidence_roles',''),
                'harm_proximity': source.get('harm_proximity',''),
                'public_link_policy': source.get('public_link_policy',''),
                'safe_to_recheck_automatically': source.get('safe_to_recheck_automatically',''),
                'source_owner_type': source.get('source_owner_type',''),
                'source_candidate_reciprocity': recip,
                'candidate_canonical_source_status': canon,
                'public_use_posture': posture,
                'capacity_or_referral_risk': caprisk,
                'status': status,
                'note': '; '.join(note_bits) if note_bits else 'claim-source boundary posture is explicit',
            })
            add_audit('claim_source_id_defined', claim_id, candidate_id, source_id, 'info', 'pass', 'source id exists in Source Registry', 'keep source registry and claim ledger synchronized')
            add_audit('source_candidate_reciprocity', claim_id, candidate_id, source_id, 'high' if recip.startswith('fail') else 'info', 'fail' if recip.startswith('fail') else 'pass', recip, 'update Source Registry candidate_ids or claim evidence_source_ids')
            add_audit('candidate_canonical_source_includes_claim_source', claim_id, candidate_id, source_id, 'high' if canon.startswith('fail') or canon == 'candidate_missing' else 'info', 'fail' if canon.startswith('fail') or canon == 'candidate_missing' else 'pass', canon, 'include all claim evidence sources in Candidate-Ledger source_ids')
            if source.get('public_link_policy','').startswith('internal_only'):
                ok = link_decision.startswith('block') if link_decision else True
                add_audit('internal_only_source_public_link_blocked', claim_id, candidate_id, source_id, 'high' if not ok else 'info', 'pass' if ok else 'fail', f'public_link_policy={source.get("public_link_policy","")}; public_url_release_decision={link_decision or "not_recorded"}', 'block public URLs for internal-only sources')
            if 'capacity_or_referral' in caprisk:
                add_audit('capacity_or_referral_language_boundary_visible', claim_id, candidate_id, source_id, 'info', 'pass', caprisk, 'do not convert claim evidence into current capacity, contact, or referral instructions')

    # Summary closure rows make the audit self-describing.
    high_fail = [r for r in audit if r.get('severity')=='high' and r.get('status')!='pass']
    matrix_fail = [r for r in matrix if r.get('status')!='pass']
    add_audit('claim_source_boundary_summary', '', '', '', 'info' if not high_fail and not matrix_fail else 'high', 'pass' if not high_fail and not matrix_fail else 'fail', f'{len(claims)} claims, {len(matrix)} claim-source links, matrix_fail={len(matrix_fail)}, high_fail={len(high_fail)}', 'zero high failures and zero matrix failures required before handoff')
    return matrix, audit


def write_reports(root: Path, matrix, audit):
    write_csv_json_md_report(
        root,
        'META/Claim-Source-Boundary-Matrix-current.csv',
        MATRIX_FIELDS,
        matrix,
        'Claim Source Boundary Matrix',
        'tools/claim_source_boundary_audit.py',
        columns=['claim_id','candidate_id','source_id','harm_proximity','public_link_policy','public_use_posture','candidate_canonical_source_status','status'],
        intro_lines=[
            f'Claim-source links: {len(matrix)}',
            'This matrix joins every claim evidence source to Source Registry harm/link/public-use posture. It is an internal audit surface, not public URL release permission.',
        ],
        max_md_rows=260,
    )
    high=sum(1 for r in audit if r.get('severity')=='high' and r.get('status')!='pass')
    write_csv_json_md_report(
        root,
        'META/Claim-Source-Boundary-Audit-current.csv',
        AUDIT_FIELDS,
        audit,
        'Claim Source Boundary Audit',
        'tools/claim_source_boundary_audit.py',
        columns=['check','claim_id','candidate_id','source_id','severity','status','detail'],
        intro_lines=[
            f'Audit rows: {len(audit)}',
            f'High failures: {high}',
            'The blocking checks are source definition, reciprocal source/candidate scope, canonical candidate source-list inclusion, and internal-only public-link blocking.',
        ],
        max_md_rows=260,
    )


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--write-report', action='store_true')
    ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args()
    root=Path(args.root).resolve()
    matrix, audit = run(root)
    if args.write_report:
        write_reports(root, matrix, audit)
    high=[r for r in audit if r.get('severity')=='high' and r.get('status')!='pass']
    matrix_fail=[r for r in matrix if r.get('status')!='pass']
    print(f"{'FAIL' if high or matrix_fail else 'PASS'} claim-source boundary matrix links={len(matrix)} audit_rows={len(audit)} high_fail={len(high)} matrix_fail={len(matrix_fail)}")
    for r in high[:20]:
        print(f"HIGH {r['check']} {r['claim_id']} {r['candidate_id']} {r['source_id']}: {r['detail']}")
    if args.fail_on_high and (high or matrix_fail):
        sys.exit(1)

if __name__=='__main__':
    main()
