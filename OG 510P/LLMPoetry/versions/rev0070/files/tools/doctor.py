#!/usr/bin/env python3
"""Fast consolidated doctor for LLMPoetry."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
TOOLS_DIR=Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path: sys.path.insert(0,str(TOOLS_DIR))
from llmpoetry_validate import validate
from check_branch_selector import run as run_branch_selector
from check_selector_map import run as run_selector_map
from check_selector_vector import run as run_selector_vector
from check_surface_apparatus_split import run as run_surface_apparatus_split
from check_loss_budget import run as run_loss_budget
from check_state_switch import run as run_state_switch
from check_ergodic_traversal import run as run_ergodic_traversal
from check_zero_route import run as run_zero_route
from check_return_diff import run as run_return_diff
from check_patch_application import run as run_patch_application
from check_surface_freshness import run as run_surface_freshness
from check_revision_lineage_freshness import run as run_revision_lineage_freshness
from check_open_questions_canonical import run as run_open_questions_canonical
from check_source_health_coverage import run as run_source_health_coverage
from check_reader_state_object import run as run_reader_state_object
from check_external_material_pressure import run as run_external_material_pressure
from check_source_snapshots import run as run_source_snapshots
from check_release_surfaces import run as run_release_surfaces
from check_candidate_reader_packet import run as run_candidate_reader_packet
from check_reader_response_intake import run as run_reader_response_intake
from check_reader_handoff_bundle import run as run_reader_handoff_bundle
from check_candidate_pressure import run as run_candidate_pressure
from check_fallback_subtraction import run as run_fallback_subtraction
from check_judgment_firewall import run as run_judgment_firewall
from check_deep_surface_consistency import run as run_deep_surface_consistency
from check_pilot_queue import run as run_pilot_queue
from check_wal_poem import run as run_wal_poem
from check_oci_whiteout_poem import run as run_oci_whiteout
from check_bloom_false_positive_poem import run as run_bloom_false_positive
def load_json(path): return json.loads(path.read_text(encoding='utf-8'))
def add(checks,name,ok,detail=''): checks.append({'name':name,'ok':bool(ok),'detail':detail})
def run_doctor(root: Path):
    checks=[]; main=validate(root); add(checks,'main_validator_ok',main.get('ok') is True,f"check_count={len(main.get('checks', []))}")
    state=load_json(root/'STATE.json'); rev=state.get('revision'); turn=state.get('turn',{}).get('last_completed')
    dsc=run_deep_surface_consistency(root); add(checks,'deep_surface_consistency_ok',all(c.get('ok') for c in dsc),f'deep_surface_checks={len(dsc)}')
    pqs=run_pilot_queue(root); add(checks,'pilot_queue_semantics_ok',all(c.get('ok') for c in pqs),f'pilot_queue_checks={len(pqs)}')
    wp=run_wal_poem(root); add(checks,'wal_poem_ok',all(c.get('ok') for c in wp),f'wal_poem_checks={len(wp)}')
    ow=run_oci_whiteout(root); add(checks,'oci_whiteout_ok',all(c.get('ok') for c in ow),f'oci_whiteout_checks={len(ow)}')
    bf=run_bloom_false_positive(root); add(checks,'bloom_false_positive_ok',all(c.get('ok') for c in bf),f'bloom_false_positive_checks={len(bf)}')
    law=load_json(root/'registries/research_law.json'); add(checks,'research_law_absolute','every' in str(law.get('scope','')).lower() and 'all cases' in str(law.get('scope','')).lower()); add(checks,'research_law_blocks_unlogged_turns','missing pulse' in str(law.get('package_gate','')).lower() or law.get('unlogged_research_turn_valid') is False)
    pulses=load_json(root/'registries/research_entropy_ledger.json').get('pulses',[]); current=[p for p in pulses if p.get('revision')==rev and p.get('turn')==turn]; add(checks,'current_pulse_present',len(current)>=1,f'revision={rev} turn={turn}')
    src_ids={s.get('source_id') for s in load_json(root/'registries/source_registry.json').get('sources',[])}; pulse_ids={sid for p in current for sid in p.get('source_ids',[])}; add(checks,'current_pulse_sources_registered',pulse_ids <= src_ids,f'missing={sorted(pulse_ids-src_ids)}')
    qs=load_json(root/'registries/human_questions.json').get('questions',[]); add(checks,'human_questions_present',len(qs)>=1); add(checks,'human_questions_have_defaults',all(q.get('default_until_answered') for q in qs)); add(checks,'human_questions_nonblocking',all(q.get('blocks_work') is False for q in qs))
    pilots=load_json(root/'registries/pilot_queue.json').get('pilots',[]); rec=[p for p in pilots if p.get('status')=='recommended_next']; add(checks,'one_recommended_pilot',len(rec)==1,f'count={len(rec)}'); add(checks,'recommended_pilot_has_verification_path',bool(rec and rec[0].get('verification_path')))
    fw=load_json(root/'registries/style_firewall.json'); add(checks,'style_firewall_active',str(fw.get('status','')).startswith('active')); add(checks,'style_firewall_seed_not_style_target','replacement house style' in str(fw.get('purpose','')).lower() or fw.get('seed_specimens_may_be_used_as_style_targets') is False)
    p0001=load_json(root/'poems/P0001/metadata.json'); add(checks,'p0001_status_allowed',p0001.get('status') in {'preflight','draft'},p0001.get('status'))
    if p0001.get('status')=='draft':
        drafts=p0001.get('drafts',[]); add(checks,'p0001_has_draft',len(drafts)>=1); current_ids={d.get('draft_id') for d in drafts if d.get('created_turn')==turn}; judged=[(j.get('target_draft_id') or j.get('draft_id')) for j in p0001.get('judgments',[]) if (j.get('target_draft_id') or j.get('draft_id')) in current_ids]; add(checks,'p0001_current_drafts_unjudged',not judged,f'judged_current={judged}')
        br=run_branch_selector(root); add(checks,'p0001_branch_selector_ok',all(c.get('ok') for c in br),f'branch_checks={len(br)}')
        sm=run_selector_map(root); add(checks,'p0001_selector_map_ok',all(c.get('ok') for c in sm),f'selector_checks={len(sm)}')
        sv=run_selector_vector(root); add(checks,'p0001_selector_vector_ok',all(c.get('ok') for c in sv),f'selector_vector_checks={len(sv)}')
        sas=run_surface_apparatus_split(root); add(checks,'p0001_surface_apparatus_split_ok',all(c.get('ok') for c in sas),f'surface_apparatus_checks={len(sas)}')
        lb=run_loss_budget(root); add(checks,'p0001_loss_budget_ok',all(c.get('ok') for c in lb),f'loss_budget_checks={len(lb)}')
        ss=run_state_switch(root); add(checks,'p0001_state_switch_ok',all(c.get('ok') for c in ss),f'state_switch_checks={len(ss)}')
        et=run_ergodic_traversal(root); add(checks,'p0001_ergodic_traversal_ok',all(c.get('ok') for c in et),f'ergodic_traversal_checks={len(et)}')
        zr=run_zero_route(root); add(checks,'p0001_zero_route_ok',all(c.get('ok') for c in zr),f'zero_route_checks={len(zr)}')
        rd=run_return_diff(root); add(checks,'p0001_return_diff_ok',all(c.get('ok') for c in rd),f'return_diff_checks={len(rd)}')
        pa=run_patch_application(root); add(checks,'p0001_patch_application_ok',all(c.get('ok') for c in pa),f'patch_application_checks={len(pa)}')
        sf=run_surface_freshness(root); add(checks,'p0001_surface_freshness_ok',all(c.get('ok') for c in sf),f'surface_freshness_checks={len(sf)}')
        lf=run_revision_lineage_freshness(root); add(checks,'revision_lineage_freshness_ok',all(c.get('ok') for c in lf),f'lineage_checks={len(lf)}')
        oq=run_open_questions_canonical(root); add(checks,'open_questions_canonical_ok',all(c.get('ok') for c in oq),f'open_question_checks={len(oq)}')
        sh=run_source_health_coverage(root); add(checks,'source_health_coverage_ok',all(c.get('ok') for c in sh),f'source_health_checks={len(sh)}')
        rso=run_reader_state_object(root); add(checks,'reader_state_object_ok',all(c.get('ok') for c in rso),f'reader_state_checks={len(rso)}')
        emp=run_external_material_pressure(root); add(checks,'external_material_pressure_ok',all(c.get('ok') for c in emp),f'external_material_checks={len(emp)}')
        ssn=run_source_snapshots(root); add(checks,'source_snapshots_ok',all(c.get('ok') for c in ssn),f'source_snapshot_checks={len(ssn)}')
        rs=run_release_surfaces(root); add(checks,'release_surfaces_ok',all(c.get('ok') for c in rs),f'release_surface_checks={len(rs)}')
        crp=run_candidate_reader_packet(root); add(checks,'candidate_reader_packet_ok',all(c.get('ok') for c in crp),f'candidate_reader_checks={len(crp)}')
        rri=run_reader_response_intake(root); add(checks,'reader_response_intake_ok',all(c.get('ok') for c in rri),f'reader_response_intake_checks={len(rri)}')
        rhb=run_reader_handoff_bundle(root); add(checks,'reader_handoff_bundle_ok',all(c.get('ok') for c in rhb),f'reader_handoff_bundle_checks={len(rhb)}')
        cp=run_candidate_pressure(root); add(checks,'candidate_pressure_ok',all(c.get('ok') for c in cp),f'candidate_pressure_checks={len(cp)}')
        fs=run_fallback_subtraction(root); add(checks,'fallback_subtraction_ok',all(c.get('ok') for c in fs),f'fallback_subtraction_checks={len(fs)}')
        jf=run_judgment_firewall(root); add(checks,'judgment_firewall_ok',all(c.get('ok') for c in jf),f'judgment_firewall_checks={len(jf)}')
    else: add(checks,'p0001_preflight_no_drafts_yet',p0001.get('drafts',[])==[])
    browse=load_json(root/'LLM_BROWSE_INDEX.json'); expected_head=load_json(root/'SURFACE_STATUS.json').get('current_head')
    add(checks,'llm_browse_index_points_to_current_head',expected_head in json.dumps(browse),expected_head)
    ok=all(c['ok'] for c in checks); return {'project':'LLMPoetry','revision':rev,'turn':turn,'ok':ok,'check_count':len(checks),'failed':[c for c in checks if not c['ok']],'checks':checks}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--verbose',action='store_true'); args=ap.parse_args(); report=run_doctor(Path(args.root)); compact={k:report[k] for k in ('project','revision','turn','ok','check_count','failed')}; print(json.dumps(report if args.verbose else compact,indent=2,ensure_ascii=False)); raise SystemExit(0 if report['ok'] else 1)
if __name__=='__main__': main()
