#!/usr/bin/env python3
from __future__ import annotations
import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
from lib_cube import read_csv_rows, write_csv_json_md_report

OVERLAY_FIELDS = [
    'overlay_id','target_surface','target_id_field','target_id','source_field','source_value',
    'normalized_code_field','normalized_code','controlled_vocabulary_source','derivation_rule',
    'review_posture','severity','status','note'
]
AUDIT_FIELDS = ['audit_id','check','surface_path','expected','observed','severity','status','note']
NORM_FIELDS = ['normalization_id','surface','prose_field','proposed_code_field','code_values','status','next_action']

CANDIDATE_STATUS_CODES = ['keep','provisional_keep','office_canon','quarantined_no_public_expansion','needs_review']
CAPACITY_CODES = ['no_capacity_claim','historical_capacity_only','current_capacity_unverified','current_capacity_supported_nonpublic','current_capacity_public_forbidden','not_applicable']
EVIDENCE_STATUS_CODES = ['supported_public_shape_not_referral_verified','interpretive_not_fact_claim','counterevidence_required','unsupported_or_debt_only']


def split_pipe(value: str) -> list[str]:
    return [x.strip() for x in (value or '').split('|') if x.strip()]


def code_from_status_categories(value: str) -> tuple[str, str]:
    cats = set(split_pipe(value.upper()))
    if 'OFFICE_CANON' in cats:
        return 'office_canon', 'status_categories contains OFFICE_CANON'
    if 'KEEP' in cats:
        return 'keep', 'status_categories contains KEEP'
    if 'PROVISIONAL_KEEP' in cats:
        return 'provisional_keep', 'status_categories contains PROVISIONAL_KEEP without KEEP'
    if 'HOLD' in cats or 'GAP_MARKER' in cats or 'SCOUT' in cats:
        return 'needs_review', 'status_categories contains HOLD/GAP_MARKER/SCOUT without KEEP'
    return 'needs_review', 'fallback for unrecognized status_categories'


def code_from_capacity(value: str) -> tuple[str, str]:
    v = (value or '').lower()
    if not v:
        return 'not_applicable', 'empty capacity_state'
    if 'not_capacity_claim' in v or 'not_service_capacity' in v or 'service_gap_or_absence' in v:
        return 'no_capacity_claim', 'capacity_state explicitly avoids service-capacity claim or marks gap/absence'
    if 'historical' in v:
        return 'historical_capacity_only', 'capacity_state is historical only'
    if 'public_service_shape_supported_but_no_live_referral' in v:
        return 'current_capacity_public_forbidden', 'service shape exists but live referral/capacity public use is forbidden'
    if 'current_capacity_unverified' in v or 'service_capacity_unverified' in v or 'implementation' in v or 'training_pool' in v or 'public_record_access' in v:
        return 'current_capacity_unverified', 'capacity-related surface is not verified for public/current referral use'
    return 'not_applicable', 'capacity_state did not assert public current capacity'


def code_from_claim_status(value: str) -> tuple[str, str]:
    v = (value or '').lower()
    if 'counterevidence' in v:
        return 'counterevidence_required', 'claim_status explicitly requires counterevidence/boundary debt'
    if 'caution' in v or 'debt' in v or 'scout_or_possible' in v or 'refresh_overlay' in v:
        return 'unsupported_or_debt_only', 'claim_status is caution, debt, scout, or refresh overlay'
    if v.startswith('interpretive') or v == 'boundary_assertion':
        return 'interpretive_not_fact_claim', 'claim_status is interpretive or an internal boundary assertion'
    if v.startswith('supported') or v.startswith('boundary_supported'):
        return 'supported_public_shape_not_referral_verified', 'claim_status is supported but remains non-referral/public-shape only'
    return 'unsupported_or_debt_only', 'fallback for unrecognized claim_status'


def vocabulary_values(root: Path, code_field: str) -> set[str]:
    values=set()
    for rel in ['SCHEMA/Boundary-Governance-Controlled-Vocabulary-current.csv']:
        for row in read_csv_rows(root/rel):
            if row.get('code_field') == code_field and row.get('status','').startswith(('active','legacy')):
                values.add(row.get('code',''))
    if code_field == 'candidate_status_code':
        values.update(CANDIDATE_STATUS_CODES)
    if code_field == 'capacity_claim_code':
        values.update(CAPACITY_CODES)
    if code_field == 'source_harm_proximity_code':
        for row in read_csv_rows(root/'SCHEMA/Harm-Proximity-Controlled-Vocabulary-current.csv'):
            if row.get('harm_proximity'):
                values.add(row.get('harm_proximity'))
    if code_field == 'claim_evidence_status_code':
        values.update(EVIDENCE_STATUS_CODES)
    return {v for v in values if v}


def add_overlay(rows, surface, id_field, target_id, source_field, source_value, code_field, code, vocab, rule, posture, severity='info', status='pass', note=''):
    rows.append({
        'overlay_id': f'norm_overlay_{len(rows)+1:05d}',
        'target_surface': surface,
        'target_id_field': id_field,
        'target_id': target_id,
        'source_field': source_field,
        'source_value': source_value,
        'normalized_code_field': code_field,
        'normalized_code': code,
        'controlled_vocabulary_source': vocab,
        'derivation_rule': rule,
        'review_posture': posture,
        'severity': severity,
        'status': status,
        'note': note,
    })


def build_overlay(root: Path) -> list[dict[str,str]]:
    rows=[]
    # Candidate-level companion codes from already-governed ledgers.
    for r in sorted(read_csv_rows(root/'Candidate-Ledger-current.csv'), key=lambda x: x.get('candidate_id','')):
        cid=r.get('candidate_id','')
        code, rule = code_from_status_categories(r.get('status_categories',''))
        add_overlay(rows,'Candidate-Ledger-current.csv','candidate_id',cid,'status_categories',r.get('status_categories',''),'candidate_status_code',code,'SCHEMA/Boundary-Governance-Controlled-Vocabulary-current.csv',rule,'companion_code_no_core_header_change')
        cap, cap_rule = code_from_capacity(r.get('capacity_state',''))
        add_overlay(rows,'Candidate-Ledger-current.csv','candidate_id',cid,'capacity_state',r.get('capacity_state',''),'capacity_claim_code',cap,'SCHEMA/Boundary-Governance-Controlled-Vocabulary-current.csv',cap_rule,'companion_code_no_core_header_change')
    # Permission and public-surface codes already exist as governance ledgers; expose them in one overlay for auditability.
    for r in sorted(read_csv_rows(root/'GOVERNANCE/Permission-State-Ledger-current.csv'), key=lambda x: x.get('candidate_id','')):
        cid=r.get('candidate_id','')
        add_overlay(rows,'GOVERNANCE/Permission-State-Ledger-current.csv','candidate_id',cid,'community_authority_status',r.get('community_authority_status',''),'community_authority_status',r.get('community_authority_status',''),'SCHEMA/Boundary-Governance-Controlled-Vocabulary-current.csv','direct companion copy from permission ledger','governance_code_already_curated')
        add_overlay(rows,'GOVERNANCE/Permission-State-Ledger-current.csv','candidate_id',cid,'boundary_lift_authority',r.get('boundary_lift_authority',''),'boundary_lift_authority',r.get('boundary_lift_authority',''),'SCHEMA/Boundary-Governance-Controlled-Vocabulary-current.csv','direct companion copy from permission ledger','governance_code_already_curated')
    for r in sorted(read_csv_rows(root/'META/Public-Export-Eligibility-current.csv'), key=lambda x: x.get('candidate_id','')):
        cid=r.get('candidate_id','')
        add_overlay(rows,'META/Public-Export-Eligibility-current.csv','candidate_id',cid,'public_export_tier',r.get('public_export_tier',''),'public_surface_code',r.get('public_export_tier',''),'SCHEMA/Boundary-Governance-Controlled-Vocabulary-current.csv','direct companion copy from public-export eligibility','derived_from_release_gate_surface')
    # Source harm proximity pipe-values stay pipe-values, but the controlled vocabulary is now checked for every token.
    for r in sorted(read_csv_rows(root/'Source-Registry-current.csv'), key=lambda x: x.get('source_id','')):
        sid=r.get('source_id','')
        hp=r.get('harm_proximity','')
        add_overlay(rows,'Source-Registry-current.csv','source_id',sid,'harm_proximity',hp,'source_harm_proximity_code',hp,'SCHEMA/Harm-Proximity-Controlled-Vocabulary-current.csv','pipe-preserving copy; each token must exist in harm-proximity vocabulary','source_safety_code_no_public_url_expansion')
    # Claim-status free text is collapsed to a conservative evidence-status bucket.
    for r in sorted(read_csv_rows(root/'Claim-Ledger-current.csv'), key=lambda x: x.get('claim_id','')):
        cid=r.get('claim_id','')
        code, rule = code_from_claim_status(r.get('claim_status',''))
        add_overlay(rows,'Claim-Ledger-current.csv','claim_id',cid,'claim_status',r.get('claim_status',''),'claim_evidence_status_code',code,'META/Controlled-Vocabulary-Normalization-current.csv',rule,'claim_lifecycle_companion_code_no_core_header_change')
    return rows


def add_audit(rows, check, surface, expected, observed, severity, status, note):
    rows.append({'audit_id': f'norm_audit_{len(rows)+1:04d}','check': check,'surface_path': surface,'expected': expected,'observed': observed,'severity': severity,'status': status,'note': note})


def build_audit(root: Path, overlay_rows: list[dict[str,str]]) -> list[dict[str,str]]:
    rows=[]
    # Coverage counts.
    counts=Counter((r['target_surface'], r['normalized_code_field']) for r in overlay_rows)
    candidate_count=len(read_csv_rows(root/'Candidate-Ledger-current.csv'))
    source_count=len(read_csv_rows(root/'Source-Registry-current.csv'))
    claim_count=len(read_csv_rows(root/'Claim-Ledger-current.csv'))
    expected_counts={
        ('Candidate-Ledger-current.csv','candidate_status_code'): candidate_count,
        ('Candidate-Ledger-current.csv','capacity_claim_code'): candidate_count,
        ('GOVERNANCE/Permission-State-Ledger-current.csv','community_authority_status'): candidate_count,
        ('GOVERNANCE/Permission-State-Ledger-current.csv','boundary_lift_authority'): candidate_count,
        ('META/Public-Export-Eligibility-current.csv','public_surface_code'): candidate_count,
        ('Source-Registry-current.csv','source_harm_proximity_code'): source_count,
        ('Claim-Ledger-current.csv','claim_evidence_status_code'): claim_count,
    }
    for key, expected in expected_counts.items():
        observed=counts.get(key,0)
        ok=observed==expected and expected>0
        add_audit(rows,'overlay_row_coverage',key[0],f'{key[1]} rows={expected}',str(observed),'info' if ok else 'high','pass' if ok else 'fail','one companion code row exists for every target ledger row')
    # Vocabulary membership.
    by_field={field:vocabulary_values(root, field) for field in sorted({r['normalized_code_field'] for r in overlay_rows})}
    for field, allowed in by_field.items():
        if not allowed:
            add_audit(rows,'controlled_vocabulary_present','.',field,'missing','high','fail','no controlled vocabulary values were available')
    bad=[]
    for r in overlay_rows:
        allowed=by_field.get(r['normalized_code_field'], set())
        values=split_pipe(r['normalized_code']) if r['normalized_code_field']=='source_harm_proximity_code' else [r['normalized_code']]
        for value in values:
            if value not in allowed:
                bad.append((r['target_surface'], r['target_id'], r['normalized_code_field'], value))
    add_audit(rows,'normalized_codes_in_vocabulary','.', 'all overlay codes are in their controlled vocabulary', str(len(bad)), 'info' if not bad else 'high', 'pass' if not bad else 'fail', '; '.join(f'{a}:{b}:{c}={d}' for a,b,c,d in bad[:10]) or 'all normalized codes are vocabulary members')
    # Conservative claims: no claim bucket may assert live referral/capacity suitability.
    risky=[r for r in overlay_rows if r['normalized_code_field']=='claim_evidence_status_code' and 'referral' in r['normalized_code'].lower() and r['normalized_code']!='supported_public_shape_not_referral_verified']
    add_audit(rows,'claim_code_referral_boundary','Claim-Ledger-current.csv','no live-referral/capacity claim code',str(len(risky)),'info' if not risky else 'high','pass' if not risky else 'fail','claim evidence code remains non-referral even when source shape is supported')
    high=sum(1 for r in rows if r.get('severity')=='high' and r.get('status')!='pass')
    add_audit(rows,'normalized_code_overlay_summary','META/Normalized-Code-Overlay-current.csv',f'overlay_rows={len(overlay_rows)} high_failures=0',f'overlay_rows={len(overlay_rows)} high_failures={high}','info','pass' if high==0 else 'fail','row-level normalized code overlay closes the old planning-only normalization debt without changing core ledger headers')
    return rows


def build_normalization_plan(root: Path) -> list[dict[str,str]]:
    harm_values='|'.join(r.get('harm_proximity','') for r in read_csv_rows(root/'SCHEMA/Harm-Proximity-Controlled-Vocabulary-current.csv') if r.get('harm_proximity'))
    rows=[
        {'normalization_id':'vocab_norm_001','surface':'Candidate-Ledger-current.csv','prose_field':'status_categories/status_current','proposed_code_field':'candidate_status_code','code_values':'|'.join(CANDIDATE_STATUS_CODES),'status':'implemented_companion_overlay_rev0096_no_header_change','next_action':'Use META/Normalized-Code-Overlay-current.* for row-level review; keep core ledger header unchanged until migration is explicitly authorized.'},
        {'normalization_id':'vocab_norm_002','surface':'Candidate-Ledger-current.csv','prose_field':'capacity_state','proposed_code_field':'capacity_claim_code','code_values':'|'.join(CAPACITY_CODES),'status':'implemented_companion_overlay_rev0096_no_header_change','next_action':'Use companion overlay to block capacity/referral drift without adding a core ledger column.'},
        {'normalization_id':'vocab_norm_003','surface':'Source-Registry-current.csv','prose_field':'harm_proximity','proposed_code_field':'source_harm_proximity_code','code_values':harm_values,'status':'implemented_companion_overlay_rev0096_no_header_change','next_action':'Audit every source harm-proximity token against SCHEMA/Harm-Proximity-Controlled-Vocabulary-current.csv.'},
        {'normalization_id':'vocab_norm_004','surface':'Claim-Ledger-current.csv','prose_field':'claim_status','proposed_code_field':'claim_evidence_status_code','code_values':'|'.join(EVIDENCE_STATUS_CODES),'status':'implemented_companion_overlay_rev0096_no_header_change','next_action':'Use conservative bucket mapping for claim lifecycle review; do not infer live-referral or capacity suitability.'},
        {'normalization_id':'vocab_norm_005','surface':'GOVERNANCE/Permission-State-Ledger-current.csv','prose_field':'community_authority_status|boundary_lift_authority','proposed_code_field':'community_authority_status|boundary_lift_authority','code_values':'see SCHEMA/Boundary-Governance-Controlled-Vocabulary-current.csv','status':'implemented_companion_overlay_rev0096_existing_governance_codes','next_action':'Keep permission/boundary authority codes visible in the overlay for release review.'},
        {'normalization_id':'vocab_norm_006','surface':'META/Public-Export-Eligibility-current.csv','prose_field':'public_export_tier','proposed_code_field':'public_surface_code','code_values':'public_policy_only|public_index_shape_only|boundary_index_shape_only|internal_only|quarantined_no_public_expansion','status':'implemented_companion_overlay_rev0096_existing_release_codes','next_action':'Use public_surface_code row coverage to catch candidate/public-tier drift.'},
    ]
    return rows


def write_field_schema(root: Path, rel: str, fields: list[str], meanings: dict[str,str]) -> None:
    schema_rel='SCHEMA/'+Path(rel).name[:-len('-current.csv')]+'-Fields-current.csv'
    rows=[]
    for field in fields:
        rows.append({'field':field,'required':'yes','allowed_values_or_pattern':'nonempty string unless explicitly blank','meaning':meanings.get(field, f'`{field}` column from `{rel}`')})
    write_csv_json_md_report(root, schema_rel, ['field','required','allowed_values_or_pattern','meaning'], rows, Path(schema_rel).name[:-4], 'tools/ledger_code_overlay.py', ['field','required','allowed_values_or_pattern','meaning'])


def write_schema_code_table(root: Path) -> None:
    rows=[
        {'field':'candidate_status_code','required':'recommended','allowed_values_or_pattern':'|'.join(CANDIDATE_STATUS_CODES),'meaning':'stable candidate status code companion to prose status fields; row-level coverage lives in META/Normalized-Code-Overlay-current.*'},
        {'field':'capacity_claim_code','required':'recommended','allowed_values_or_pattern':'|'.join(CAPACITY_CODES),'meaning':'stable capacity/currentness code that prevents live-referral drift'},
        {'field':'community_authority_status','required':'recommended_for_sensitive_rows','allowed_values_or_pattern':'no_authority_claimed|public_context_only|permission_required_for_expansion|do_not_expand|remove_if_contested','meaning':'permission state for Indigenous/family-led/survivor-side material'},
        {'field':'boundary_lift_authority','required':'recommended_for_sensitive_rows','allowed_values_or_pattern':'never_by_operator_only|requires_family_or_community_confirmation|requires_family_community_or_governance_confirmation|requires_governance_review|not_liftable','meaning':'who, if anyone, can loosen a boundary; rev0096 includes the actual governance-ledger code as a controlled value'},
        {'field':'public_surface_code','required':'recommended','allowed_values_or_pattern':'public_policy_only|public_index_shape_only|boundary_index_shape_only|internal_only|quarantined_no_public_expansion','meaning':'normalized public/internal/quarantine surface classification'},
        {'field':'source_harm_proximity_code','required':'recommended','allowed_values_or_pattern':'see SCHEMA/Harm-Proximity-Controlled-Vocabulary-current.csv','meaning':'pipe-preserving source harm-proximity code checked against the harm-proximity vocabulary'},
        {'field':'claim_evidence_status_code','required':'recommended','allowed_values_or_pattern':'|'.join(EVIDENCE_STATUS_CODES),'meaning':'conservative claim lifecycle bucket; never a live-referral or capacity assertion'},
    ]
    write_csv_json_md_report(root, 'SCHEMA/Normalized-Code-Overlay-current.csv', ['field','required','allowed_values_or_pattern','meaning'], rows, 'Normalized Code Overlay', 'tools/ledger_code_overlay.py', ['field','required','allowed_values_or_pattern','meaning'])


def update_boundary_vocab(root: Path) -> None:
    rel='SCHEMA/Boundary-Governance-Controlled-Vocabulary-current.csv'
    rows=read_csv_rows(root/rel)
    existing={(r.get('code_field'), r.get('code')) for r in rows}
    if ('boundary_lift_authority','requires_family_community_or_governance_confirmation') not in existing:
        max_id=0
        for r in rows:
            m=re.search(r'(\d+)$', r.get('vocabulary_id',''))
            if m:
                max_id=max(max_id, int(m.group(1)))
        rows.append({'vocabulary_id':f'vocab_{max_id+1:03d}','code_field':'boundary_lift_authority','code':'requires_family_community_or_governance_confirmation','meaning':'requires family, community, or governance confirmation','public_export_effect':'does not loosen public boundary; governs classification/review','status':'active_rev0096_actual_permission_ledger_code'})
    write_csv_json_md_report(root, rel, ['vocabulary_id','code_field','code','meaning','public_export_effect','status'], rows, 'Boundary Governance Controlled Vocabulary', 'tools/ledger_code_overlay.py', ['vocabulary_id','code_field','code','meaning','status'])


def write_reports(root: Path) -> None:
    update_boundary_vocab(root)
    overlay=build_overlay(root)
    audit=build_audit(root, overlay)
    write_csv_json_md_report(root, 'META/Normalized-Code-Overlay-current.csv', OVERLAY_FIELDS, overlay, 'Normalized Code Overlay', 'tools/ledger_code_overlay.py', ['target_surface','target_id','normalized_code_field','normalized_code','severity','status','note'], intro_lines=[f'Overlay rows: {len(overlay)}','Companion codes only; core ledger headers are unchanged.'], max_md_rows=280)
    write_csv_json_md_report(root, 'META/Normalized-Code-Overlay-Audit-current.csv', AUDIT_FIELDS, audit, 'Normalized Code Overlay Audit', 'tools/ledger_code_overlay.py', ['check','surface_path','expected','observed','severity','status','note'])
    write_csv_json_md_report(root, 'META/Controlled-Vocabulary-Normalization-current.csv', NORM_FIELDS, build_normalization_plan(root), 'Controlled Vocabulary Normalization', 'tools/ledger_code_overlay.py', ['normalization_id','surface','proposed_code_field','status','next_action'])
    write_schema_code_table(root)
    write_field_schema(root, 'META/Normalized-Code-Overlay-current.csv', OVERLAY_FIELDS, {
        'overlay_id':'stable overlay row identifier',
        'target_surface':'CSV surface receiving the companion code',
        'target_id_field':'identifier field in the target surface',
        'target_id':'identifier value in the target surface',
        'source_field':'prose/free-text field being normalized',
        'source_value':'source prose/free-text value used to derive the code',
        'normalized_code_field':'name of the companion normalized code field',
        'normalized_code':'normalized code or pipe-preserving code list',
        'controlled_vocabulary_source':'surface that defines the allowed code values',
        'derivation_rule':'deterministic rule used to derive or copy the code',
        'review_posture':'whether the row is derived, curated, or a no-header-change companion',
        'severity':'audit severity for the row',
        'status':'pass/fail status for the row',
        'note':'review note; never public-release permission',
    })
    write_field_schema(root, 'META/Normalized-Code-Overlay-Audit-current.csv', AUDIT_FIELDS, {
        'audit_id':'stable audit row identifier',
        'check':'audit check name',
        'surface_path':'surface being checked',
        'expected':'expected count or state',
        'observed':'observed count or state',
        'severity':'finding severity',
        'status':'pass/fail/review status',
        'note':'audit note',
    })
    write_field_schema(root, 'META/Controlled-Vocabulary-Normalization-current.csv', NORM_FIELDS, {
        'normalization_id':'normalization plan row id',
        'surface':'surface receiving a companion code overlay',
        'prose_field':'source prose/free-text field(s)',
        'proposed_code_field':'companion normalized code field(s)',
        'code_values':'allowed code values or vocabulary source',
        'status':'adoption status of the companion code overlay',
        'next_action':'bounded next action without changing public posture',
    })


def run(root: Path) -> tuple[list[dict[str,str]], list[dict[str,str]]]:
    overlay=build_overlay(root)
    audit=build_audit(root, overlay)
    return overlay, audit


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--write-report', action='store_true')
    ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args()
    root=Path(args.root).resolve()
    if args.write_report:
        write_reports(root)
    overlay, audit=run(root)
    high=[r for r in audit if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if high else 'PASS'} normalized code overlay rows={len(overlay)} audit_rows={len(audit)} high={len(high)}")
    for r in high[:20]:
        print(f"HIGH {r['check']} {r['surface_path']}: {r['note']}")
    if args.fail_on_high and high:
        sys.exit(1)

if __name__ == '__main__':
    main()
