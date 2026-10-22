#!/usr/bin/env python3
"""Validate Helm rev0221 portal-net audit/export fixture.

Audit/export surfaces carry proof across contexts, but they do not become
consent, SlopOS admission, current truth, verdict, replay permission, or source
receipt mutation.
"""
from __future__ import annotations
import json, subprocess
from pathlib import Path
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/'fixtures'/'portal-net-consent-export'
PACK=FIX/'audit-export-pack.json'
SEAM=FIX/'companion-seam-pack.json'
APPEAL=FIX/'appeal-correction-pack.json'
PINS=ROOT/'fixtures'/'release-readiness'/'classification-pins.json'
REV='rev0221'
REQUIRED_POSTURES={
 'audit_export_bound','proof_bundle_non_authority','missing_export_manifest_blocked','bundle_digest_mismatch_quarantined','redaction_sweep_required','chain_gap_refused','cross_tenant_export_blocked','support_package_least_privilege','offline_bundle_stale_badged','machine_readable_summary_not_verdict','third_party_attestation_non_authority','reimport_requires_rebind'}
FORBIDDEN={
 'treat_audit_export_as_authority','treat_proof_bundle_as_consent','claim_audit_summary_is_verdict','hide_export_manifest','hide_bundle_digest_mismatch','hide_redaction_sweep','hide_chain_gap','export_cross_tenant_without_warrant','include_replay_material_in_support_package','drop_stale_badge_on_offline_bundle','treat_machine_readable_summary_as_completion','treat_third_party_attestation_as_slopos_admission','reimport_without_actor_rebind','reimport_without_namespace_rebind','reimport_without_digest_recheck','reimport_without_retention_recheck','mutate_source_receipt_from_export','erase_omitted_refs_from_manifest','let_export_bundle_arm_action','let_external_auditor_override_slopos','hide_omitted_material_refs','hide_export_data_class','hide_export_recipient','hide_export_retention_budget','include_secret_payload_in_audit_export','flatten_redacted_and_unredacted_copies','claim_export_is_current_truth','claim_portability_means_transferable_permission','skip_support_package_minimization','hide_attestation_source'}
NON_AUTHORITY={'audit_export_strip','audit_bundle','audit_manifest','machine_readable_summary','third_party_attestation','support_package','offline_bundle','redaction_sweep_witness','bundle_digest','chain_gap_marker','omitted_refs_list','export_recipient','external_auditor_note','reimport_candidate','proof_portability_index','retention_index','policy','runtime_authority','slopos_admission','user_consent','current_truth','settlement_receipt','appeal_receipt','notification_receipt'}
INVARIANTS={'audit_export_strip_is_not_authority','audit_bundle_is_not_consent','audit_summary_is_not_verdict','manifest_required_for_export','bundle_digest_must_match_manifest','redaction_sweep_required_for_sensitive_export','chain_gap_blocks_complete_export','cross_tenant_export_requires_fresh_warrant','support_package_is_least_privilege','offline_bundle_must_show_stale_badge','third_party_attestation_is_non_authority','reimport_requires_rebind'}
REQUIRED_CONTEXT={'observed_at','surface_kind','source_appeal_case_id','target_action_case_id','export_requested','export_manifest_ref','export_manifest_present','export_manifest_is_authority','bundle_digest_ref','bundle_digest_matches_manifest','source_receipt_chain_complete','omitted_refs_declared','omitted_refs_are_authority','redaction_profile','redaction_sweep_witness_ref','recipient_binding','recipient_binding_matches_namespace','cross_tenant_export','support_package','support_package_least_privilege','offline_bundle','offline_bundle_stale_badge_visible','machine_readable_summary_ref','machine_readable_summary_is_verdict','third_party_attestation_ref','third_party_attestation_is_authority','reimport_candidate','reimport_actor_rebound','reimport_namespace_rebound','reimport_digest_rechecked','reimport_retention_rechecked','source_receipt_mutated','remote_effect_created','slopos_admission_claimed','current_truth_claimed','portable_permission_claimed','state_label'}
class CheckError(Exception): pass
def require(cond,msg):
    if not cond: raise CheckError(msg)
def load(path): return json.loads(path.read_text(encoding='utf-8'))
def parse_time(s,label):
    try: datetime.fromisoformat(s)
    except Exception as exc: raise CheckError(f'{label}: bad timestamp {s!r}: {exc}')

def main():
    proc=subprocess.run(['python3', str(ROOT/'tools'/'check_classification_pins.py')], cwd=ROOT, text=True, capture_output=True)
    if proc.returncode!=0: raise CheckError('check_classification_pins.py failed:\n'+proc.stdout+proc.stderr)
    pack=load(PACK); seam=load(SEAM); appeal=load(APPEAL); pins=load(PINS)
    require(pack.get('revision')==seam.get('revision')==appeal.get('revision')==REV, 'audit export fixtures must be rev0221')
    require(pack.get('specimen_id')==seam.get('specimen_id')==appeal.get('specimen_id')=='portal-net-consent-export', 'specimen mismatch')
    require(seam.get('audit_export_refs'), 'companion seam missing audit export refs')
    pol=pack.get('audit_export_policy',{})
    expected_flags={
      'audit_export_strip_is_authority':False,'export_bundle_is_authority':False,'audit_manifest_is_authority':False,'audit_summary_is_verdict':False,'third_party_attestation_is_authority':False,'proof_portability_transfers_permission':False,'reimport_is_authority_without_rebind':False,'source_receipts_may_be_mutated_by_export':False,'remote_effects_may_be_created_by_export':False,'manifest_required_for_export':True,'digest_match_required':True,'redaction_sweep_required_for_sensitive_export':True,'chain_gap_must_be_labeled_or_refused':True,'recipient_namespace_binding_required':True,'support_package_must_be_least_privilege':True,'reimport_requires_actor_namespace_digest_retention_rebind':True}
    for flag,val in expected_flags.items(): require(pol.get(flag) is val, f'policy {flag} must be {val}')
    require(set(pol.get('required_audit_export_postures',[]))==REQUIRED_POSTURES, 'required audit export postures mismatch')
    require(FORBIDDEN.issubset(set(pol.get('forbidden_effects',[]))), 'policy forbidden effects too weak')
    require(NON_AUTHORITY.issubset(set(pol.get('non_authority_for',[]))), 'policy non-authority too weak')
    require(INVARIANTS.issubset(set(pol.get('invariants',[]))), 'policy invariants too weak')
    schemes={s['scheme_id']:s for s in pins.get('schemes',[])}
    require('helm.portal_audit_export_posture' in schemes, 'missing audit export pins')
    pinned={m['member_id'] for m in schemes['helm.portal_audit_export_posture'].get('members',[])}
    require(REQUIRED_POSTURES.issubset(pinned), f'missing audit export pins {sorted(REQUIRED_POSTURES-pinned)}')
    action_ids={a['case_id'] for a in seam.get('actions',[])}
    appeal_ids={c['case_id'] for c in appeal.get('cases',[])}
    for a in seam.get('actions',[]):
        refs=a.get('audit_export_refs',{})
        for key,val in {'audit_export_strip_is_authority':False,'export_bundle_is_authority':False,'audit_summary_is_verdict':False,'third_party_attestation_is_authority':False,'proof_portability_transfers_permission':False,'reimport_requires_rebind':True,'manifest_digest_required':True,'redaction_sweep_required_for_sensitive_export':True}.items():
            require(refs.get(key) is val, f'{a.get("case_id")}: audit export ref {key} must be {val}')
    cases=pack.get('cases',[])
    require(len(cases)==12, 'expected twelve audit/export cases')
    seen=set(); postures=set(); targeted=set()
    for c in cases:
        cid=c.get('case_id'); posture=c.get('audit_export_posture')
        require(cid and cid not in seen, f'{cid}: duplicate/missing case id')
        seen.add(cid); postures.add(posture); targeted.add(c.get('target_action_case_id'))
        require(c.get('target_action_case_id') in action_ids, f'{cid}: unknown target action')
        require(c.get('source_appeal_case_id') in appeal_ids, f'{cid}: unknown appeal case')
        require(posture in REQUIRED_POSTURES, f'{cid}: bad posture {posture}')
        for key in ['operator_copy_short','operator_copy_exact','screen_reader_copy']:
            require(c.get(key), f'{cid}: missing {key}')
        require('not authority' in c['operator_copy_short'].lower() or 'not authority' in c['operator_copy_exact'].lower(), f'{cid}: copy must name non-authority')
        ctx=c.get('audit_export_context',{}); missing=REQUIRED_CONTEXT-set(ctx)
        require(not missing, f'{cid}: missing context {sorted(missing)}')
        parse_time(ctx['observed_at'], f'{cid}.observed_at')
        for k in ['export_manifest_is_authority','omitted_refs_are_authority','machine_readable_summary_is_verdict','third_party_attestation_is_authority','source_receipt_mutated','remote_effect_created','slopos_admission_claimed','current_truth_claimed','portable_permission_claimed']:
            require(ctx[k] is False, f'{cid}: {k} must be false')
        if posture=='missing_export_manifest_blocked': require(ctx['export_manifest_present'] is False and ctx['export_manifest_ref'] is None, f'{cid}: manifest should be missing')
        else: require(ctx['export_manifest_present'] is True and ctx['export_manifest_ref'], f'{cid}: manifest required')
        if posture=='bundle_digest_mismatch_quarantined': require(ctx['bundle_digest_matches_manifest'] is False, f'{cid}: digest mismatch required')
        else: require(ctx['bundle_digest_matches_manifest'] is True, f'{cid}: digest should match')
        if posture=='chain_gap_refused': require(ctx['source_receipt_chain_complete'] is False, f'{cid}: chain gap required')
        if posture=='cross_tenant_export_blocked': require(ctx['recipient_binding_matches_namespace'] is False and ctx['cross_tenant_export'] is True, f'{cid}: cross-tenant block required')
        if posture=='support_package_least_privilege': require(ctx['support_package'] is True and ctx['support_package_least_privilege'] is True, f'{cid}: support package least privilege required')
        if posture=='offline_bundle_stale_badged': require(ctx['offline_bundle'] is True and ctx['offline_bundle_stale_badge_visible'] is True, f'{cid}: stale badge required')
        if posture=='machine_readable_summary_not_verdict': require(ctx['machine_readable_summary_ref'] and ctx['machine_readable_summary_is_verdict'] is False, f'{cid}: summary non-verdict required')
        if posture=='third_party_attestation_non_authority': require(ctx['third_party_attestation_ref'] and ctx['third_party_attestation_is_authority'] is False, f'{cid}: attestation non-authority required')
        if posture=='reimport_requires_rebind':
            for k in ['reimport_actor_rebound','reimport_namespace_rebound','reimport_digest_rechecked','reimport_retention_rechecked']:
                require(ctx[k] is False, f'{cid}: reimport must show missing {k}')
        gate=c.get('audit_export_gate',{})
        for k in ['gate_is_authority','may_treat_export_as_consent','may_treat_export_as_verdict','may_treat_export_as_current_truth','may_treat_attestation_as_slopos_admission','may_include_replay_material']:
            require(gate.get(k) is False, f'{cid}: gate {k} must be false')
        for k in ['requires_manifest','requires_digest_match','requires_redaction_sweep_for_sensitive_copy','requires_chain_completeness_or_gap_label','requires_recipient_namespace_binding','requires_rebind_on_reimport']:
            require(gate.get(k) is True, f'{cid}: gate {k} must be true')
        strip=c.get('audit_export_strip',{})
        for k in ['strip_is_authority','export_bundle_is_authority','audit_summary_is_verdict','external_attestation_is_authority','reimport_is_rebinded_authority','proof_portability_is_permission_transfer']:
            require(strip.get(k) is False, f'{cid}: strip {k} must be false')
        ret=c.get('retention_posture',{})
        require(ret.get('retention_posture_is_authority') is False, f'{cid}: retention posture must be non-authority')
        require(ret.get('minimization_transform') in {'digest_and_redacted_summary','redacted_summary'}, f'{cid}: minimization required')
        parse_time(ret.get('expires_at',''), f'{cid}.retention.expires_at')
        require(INVARIANTS.issubset(set(c.get('invariants',[]))), f'{cid}: invariants too weak')
        require(FORBIDDEN.issubset(set(c.get('must_not',[]))), f'{cid}: must_not too weak')
        require(NON_AUTHORITY.issubset(set(c.get('non_authority_for',[]))), f'{cid}: non_authority too weak')
        require(f'helm.portal_audit_export_posture/{posture}' in c.get('classification_refs',[]), f'{cid}: missing classification ref')
    require(postures==REQUIRED_POSTURES, 'posture coverage mismatch')
    require(len(targeted)>=5, 'audit export should cover multiple companion actions')
    print('ok: 12 portal-net audit export cases validated')
if __name__=='__main__':
    try:
        main()
    except CheckError as exc:
        raise SystemExit(f'ERROR: {exc}')
