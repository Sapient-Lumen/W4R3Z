#!/usr/bin/env python3
"""Validate resumability/integrity surfaces for LLMPoetry."""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path
try:
    from check_surface_freshness import run as run_surface_freshness
except Exception:
    run_surface_freshness = None
try:
    from check_revision_lineage_freshness import run as run_revision_lineage_freshness
except Exception:
    run_revision_lineage_freshness = None
try:
    from check_open_questions_canonical import run as run_open_questions_canonical
except Exception:
    run_open_questions_canonical = None
try:
    from check_source_health_coverage import run as run_source_health_coverage
except Exception:
    run_source_health_coverage = None

try:
    from check_reader_state_object import run as run_reader_state_object
except Exception:
    run_reader_state_object = None
try:
    from check_external_material_pressure import run as run_external_material_pressure
except Exception:
    run_external_material_pressure = None
try:
    from check_source_snapshots import run as run_source_snapshots
except Exception:
    run_source_snapshots = None

try:
    from check_release_surfaces import run as run_release_surfaces
except Exception:
    run_release_surfaces = None

try:
    from check_candidate_reader_packet import run as run_candidate_reader_packet
except Exception:
    run_candidate_reader_packet = None

try:
    from check_reader_response_intake import run as run_reader_response_intake
except Exception:
    run_reader_response_intake = None

try:
    from check_reader_handoff_bundle import run as run_reader_handoff_bundle
except Exception:
    run_reader_handoff_bundle = None
try:
    from check_candidate_pressure import run as run_candidate_pressure
except Exception:
    run_candidate_pressure = None

try:
    from check_fallback_subtraction import run as run_fallback_subtraction
except Exception:
    run_fallback_subtraction = None

try:
    from check_judgment_firewall import run as run_judgment_firewall
except Exception:
    run_judgment_firewall = None

try:
    from check_deep_surface_consistency import run as run_deep_surface_consistency
except Exception:
    run_deep_surface_consistency = None
try:
    from check_pilot_queue import run as run_pilot_queue
except Exception:
    run_pilot_queue = None
try:
    from check_wal_poem import run as run_wal_poem
except Exception:
    run_wal_poem = None
try:
    from check_oci_whiteout_poem import run as run_oci_whiteout
except Exception:
    run_oci_whiteout = None
try:
    from check_bloom_false_positive_poem import run as run_bloom_false_positive
except Exception:
    run_bloom_false_positive = None
try:
    from release_tree import MANIFEST_EXCLUDE, collect_files
except Exception:
    MANIFEST_EXCLUDE = None
    collect_files = None

REQUIRED_ROOT = ['START_HERE.md','README.md','AGENTS.md','LLM_BROWSE_INDEX.json','HUMAN_QUESTIONS.md','STATE.json','CONTEXT_PACK.json','REENTRY_CONTRACT.json','REVISION_LINEAGE.json','REVISION_RECEIPT.json','SURFACE_STATUS.json','VALIDATION_INDEX.json','VALIDATION_TOOLCHAIN_MANIFEST.json','MANIFEST.json','MANIFEST.sha256','CHECKSUMS.sha256','COMPACT_SURFACE_BUNDLE.json','REPLAY_CAPSULE.json','FRONTIER_TICKET.json','INNOVATION_PACKET.json','CANARY_PROTOCOL.json','CANARY_RUNS.json','ARCHIVE_INVARIANTS.json','PRUNED_TRANSIENT.paths']
REQUIRED_REGISTRIES = ['poem_index.json','source_registry.json','specimen_registry.json','teacher_patterns.json','open_questions.json','banlist.json','research_law.json','quote_search_receipts.json','source_receipts.json','source_health.json','claim_registry.json','human_questions.json','pilot_queue.json','style_firewall.json','source_taxonomy.json','disclosure_test_templates.json','human_intervention_log.json','source_snapshot_registry.json','research_pulse_index.json']
REQUIRED_SCHEMAS = ['poem.schema.json','draft.schema.json','judgment.schema.json','source.schema.json','revision.schema.json','form.schema.json','validation_report.schema.json','quote_search_receipt.schema.json','source_receipt.schema.json','research_pulse.schema.json','canary_run.schema.json','research_law.schema.json','human_question.schema.json','pilot_queue.schema.json','style_firewall.schema.json','source_taxonomy.schema.json','disclosure_test.schema.json','branch_selector.schema.json','human_intervention_log.schema.json','selector_map.schema.json','render_receipt.schema.json','loss_budget.schema.json','state_switch.schema.json','ergodic_traversal.schema.json','zero_route.schema.json','return_diff.schema.json','patch_application.schema.json','reader_state_object.schema.json','external_material_packet.schema.json','source_snapshot.schema.json','candidate_reader_packet.schema.json','reader_response_intake.schema.json']
EXCLUDE_SELF = {'MANIFEST.json','MANIFEST.sha256','CHECKSUMS.sha256','reports/validation_report.json'}
WORD_RE=re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")
def final_word(text):
    words=WORD_RE.findall(text); return words[-1].lower() if words else ''
def sha256_file(path: Path) -> str:
    h=hashlib.sha256();
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()
def add(checks,name,ok,detail=''): checks.append({'name':name,'ok':bool(ok),'detail':detail})
def load_json(path): return json.loads(path.read_text(encoding='utf-8'))
def validate(root: Path):
    checks=[]; state={}
    try: state=load_json(root/'STATE.json'); add(checks,'state_parse',True)
    except Exception as e: add(checks,'state_parse',False,str(e))
    current_rev=state.get('revision','UNKNOWN'); current_turn=state.get('turn',{}).get('last_completed')
    for rel in REQUIRED_ROOT: add(checks,f'required_root:{rel}',(root/rel).exists())
    for rel in REQUIRED_REGISTRIES: add(checks,f'required_registry:{rel}',(root/'registries'/rel).exists())
    for rel in REQUIRED_SCHEMAS: add(checks,f'required_schema:{rel}',(root/'schemas'/rel).exists())
    for p in [p for p in root.rglob('*.json') if p.is_file()]:
        try: json.loads(p.read_text(encoding='utf-8')); add(checks,f'json_parse:{p.relative_to(root).as_posix()}',True)
        except Exception as e: add(checks,f'json_parse:{p.relative_to(root).as_posix()}',False,str(e))
    add(checks,'no_source_seed_dir',not (root/'source_seed').exists())
    add(checks,'no_embedded_fable_specimen_poem_text_dir',not (root/'specimens'/'Fable-Claude-F5P').exists())
    add(checks,'seed_receipt_present',(root/'seed'/'SEED_INPUT_RECEIPT.json').exists())
    add(checks,'seed_doctrine_digest_present',(root/'docs'/'20-seed'/'SEED_DOCTRINE_DIGEST.md').exists())
    try:
        spec=load_json(root/'registries/specimen_registry.json'); specimens=spec.get('specimens',[])
        add(checks,'specimen_count_15',len(specimens)==15,f'count={len(specimens)}')
        add(checks,'specimens_text_not_embedded',spec.get('embedded_text') is False and all(s.get('embedded_text') is False for s in specimens))
        add(checks,'specimens_all_quarantined',all(str(s.get('status','')).startswith('quarantined') for s in specimens))
    except Exception as e: add(checks,'specimen_registry_policy',False,str(e))
    try:
        poem_index=load_json(root/'registries/poem_index.json'); admitted=[p for p in poem_index.get('poems',[]) if p.get('status') in {'admitted','evidence_candidate'}]
        add(checks,'no_admitted_or_evidence_poems_current_revision',len(admitted)==0,f'admitted_or_evidence={len(admitted)}')
    except Exception as e: add(checks,'poem_index_policy',False,str(e))
    try:
        law=load_json(root/'registries/research_law.json'); add(checks,'research_law_id',law.get('law_id')=='LAW-R1')
        surfaces=law.get('propagation_surfaces',[]); missing=[s for s in surfaces if not (root/s).exists()]
        add(checks,'research_law_surfaces_exist',not missing,f'missing={missing}')
        for rel in surfaces:
            text=(root/rel).read_text(errors='ignore') if (root/rel).exists() else ''
            add(checks,f'research_law_mentioned:{rel}','web' in text.lower() and ('turn' in text.lower() or 'pulse' in text.lower()))
    except Exception as e: add(checks,'research_law_policy',False,str(e))
    try:
        src=load_json(root/'registries/source_registry.json'); ids=[s.get('source_id') for s in src.get('sources',[])]
        add(checks,'source_ids_unique',len(ids)==len(set(ids)))
    except Exception as e: add(checks,'source_registry_policy',False,str(e))
    try:
        ledger=load_json(root/'registries/research_entropy_ledger.json'); pulses=ledger.get('pulses',[]); current=[p for p in pulses if p.get('revision')==current_rev and p.get('turn')==current_turn]
        add(checks,'research_ledger_revision_matches_state',ledger.get('revision')==current_rev,ledger.get('revision'))
        add(checks,'current_revision_turn_research_pulse_present',len(current)>=1,f'rev={current_rev} turn={current_turn}')
        source_ids={s.get('source_id') for s in load_json(root/'registries/source_registry.json').get('sources',[])}
        missing=sorted({sid for p in current for sid in p.get('source_ids',[]) if sid not in source_ids})
        add(checks,'current_research_pulse_sources_registered',not missing,f'missing={missing}')
        pulse_index=load_json(root/'registries/research_pulse_index.json')
        idx_pulses=pulse_index.get('pulses',[])
        add(checks,'research_pulse_index_revision_matches_state',pulse_index.get('revision')==current_rev,pulse_index.get('revision'))
        add(checks,'research_pulse_index_synchronized_with_ledger',[p.get('pulse_id') for p in idx_pulses]==[p.get('pulse_id') for p in pulses],f"index={len(idx_pulses)} ledger={len(pulses)}")
        add(checks,'research_pulse_index_current_pulse_present',any(p.get('revision')==current_rev and p.get('turn')==current_turn for p in idx_pulses),f'rev={current_rev} turn={current_turn}')
    except Exception as e: add(checks,'research_pulse_policy',False,str(e))
    try:
        hq=load_json(root/'registries/human_questions.json').get('questions',[])
        add(checks,'human_questions_have_defaults',all(q.get('default_until_answered') for q in hq))
        add(checks,'human_questions_nonblocking_or_reasoned',all(q.get('blocks_work') is False or q.get('blocking_reason') for q in hq))
    except Exception as e: add(checks,'human_questions_policy',False,str(e))
    try:
        pq=load_json(root/'registries/pilot_queue.json').get('pilots',[]); rec=[p for p in pq if p.get('status')=='recommended_next']
        add(checks,'pilot_queue_one_recommended_next',len(rec)==1,f'count={len(rec)}')
        add(checks,'pilot_queue_verification_paths',all(p.get('verification_path') for p in pq))
        form_ids={f.get('form_id') for f in load_json(root/'registries/form_registry.json').get('forms',[])}
        missing_forms=[p.get('pilot_id') for p in pq if p.get('form_id') not in form_ids]
        add(checks,'pilot_queue_form_ids_registered',not missing_forms,f'missing={missing_forms}')
    except Exception as e: add(checks,'pilot_queue_policy',False,str(e))
    try:
        fw=load_json(root/'registries/style_firewall.json'); add(checks,'style_firewall_active',str(fw.get('status','')).startswith('active')); add(checks,'style_firewall_watchlist_present',bool(fw.get('lexical_watchlist')))
    except Exception as e: add(checks,'style_firewall_policy',False,str(e))
    try:
        problems=[]
        for d in (root/'poems').iterdir():
            if d.is_dir() and re.match(r'P\d{4}',d.name):
                meta=d/'metadata.json'
                if not meta.exists(): problems.append(f'{d}:missing_metadata')
                else:
                    obj=load_json(meta)
                    for dr in obj.get('drafts',[]):
                        if not (root/dr.get('path','')).exists(): problems.append(f'{d}:missing_draft:{dr.get("path")}')
        add(checks,'poem_records_consistent',not problems,f'problems={problems[:5]}')
    except Exception as e: add(checks,'poem_records_policy',False,str(e))
    try:
        p0001=load_json(root/'poems/P0001/metadata.json')
        if p0001.get('status')=='draft':
            drafts=p0001.get('drafts',[]); add(checks,'p0001_has_draft_record',len(drafts)>=1)
            draft_turns={d.get('draft_id'):d.get('created_turn') for d in drafts}; current_ids={d.get('draft_id') for d in drafts if d.get('created_turn')==current_turn}
            judged_current=[]; bad_temporal=[]
            for j in p0001.get('judgments',[]):
                target=j.get('target_draft_id') or j.get('draft_id')
                jt=j.get('judged_turn') or j.get('created_turn')
                if target in current_ids: judged_current.append(target)
                if target in draft_turns and isinstance(jt,int) and isinstance(draft_turns.get(target),int) and jt <= draft_turns[target]: bad_temporal.append(j.get('judgment_id',target))
            add(checks,'p0001_no_same_turn_judgment_of_current_drafts',not judged_current,f'judged_current={judged_current}')
            add(checks,'p0001_judgments_satisfy_temporal_firewall',not bad_temporal,f'bad={bad_temporal}')
            for d in drafts:
                draft_path=root/d.get('path',''); add(checks,f'p0001_draft_file_exists:{d.get("draft_id")}',draft_path.exists(),d.get('path',''))
                if d.get('metrics_path'): add(checks,f'p0001_metrics_exists:{d.get("draft_id")}',(root/d.get('metrics_path')).exists(),d.get('metrics_path',''))
                packet_rel=d.get('branch_packet_path')
                if packet_rel:
                    packet_path=root/packet_rel; add(checks,f'p0001_branch_packet_exists:{d.get("draft_id")}',packet_path.exists(),packet_rel)
                    if packet_path.exists() and draft_path.exists():
                        packet=load_json(packet_path); text=draft_path.read_text(encoding='utf-8',errors='replace'); layers=packet.get('layers',[]); claim=packet.get('selected_initials_claim',''); expected=packet.get('candidate_count_per_layer') or (len(layers[0].get('candidates',[])) if layers else None)
                        selected=[]; selected_path=[]; ids=[]; unselected=[]; count_ok=True; one_ok=True
                        for layer in layers:
                            cands=layer.get('candidates',[])
                            if expected is not None and len(cands)!=expected: count_ok=False
                            sels=[c for c in cands if c.get('selected') is True]
                            if len(sels)!=1: one_ok=False
                            if sels: selected.append(sels[0].get('text','')); selected_path.append(sels[0].get('candidate_id'))
                            for c in cands:
                                ids.append(c.get('candidate_id'))
                                if c.get('selected') is not True: unselected.append(c.get('text',''))
                        initials=''.join((s.strip()[:1] or '') for s in selected)
                        add(checks,f'p0001_branch_selector_layers_match_claim:{d.get("draft_id")}',len(layers)==len(claim),f'count={len(layers)} claim={claim}')
                        add(checks,f'p0001_branch_selector_candidate_count:{d.get("draft_id")}',count_ok)
                        add(checks,f'p0001_branch_selector_one_selected_per_layer:{d.get("draft_id")}',one_ok)
                        add(checks,f'p0001_branch_selector_path_matches:{d.get("draft_id")}',selected_path==packet.get('selected_path'),f'selected_path={selected_path}')
                        add(checks,f'p0001_branch_selector_initials_match_claim:{d.get("draft_id")}',initials==claim,initials)
                        add(checks,f'p0001_branch_selector_lines_in_draft:{d.get("draft_id")}',all(s in text for s in selected))
                        add(checks,f'p0001_branch_selector_prompt_in_draft:{d.get("draft_id")}',packet.get('prompt_text','') in text)
                        add(checks,f'p0001_candidate_ids_unique:{d.get("draft_id")}',len(ids)==len(set(ids)))
                        if packet.get('all_candidates_must_appear_in_draft') is True: add(checks,f'p0001_all_candidates_in_draft:{d.get("draft_id")}',all(c.get('text','') in text for layer in layers for c in layer.get('candidates',[])))
                        if packet.get('unselected_final_words_claim'):
                            shadow=' '.join(final_word(t) for t in unselected)
                            add(checks,f'p0001_unselected_final_words_match_claim:{d.get("draft_id")}',shadow==packet.get('unselected_final_words_claim'),shadow)
                            add(checks,f'p0001_unselected_shadow_in_draft:{d.get("draft_id")}',shadow in text,shadow)
                        if packet.get('selector_map_path'): add(checks,f'p0001_selector_map_exists:{d.get("draft_id")}',(root/packet.get('selector_map_path')).exists(),packet.get('selector_map_path'))
                        if packet.get('selector_vector_path'): add(checks,f'p0001_selector_vector_exists:{d.get("draft_id")}',(root/packet.get('selector_vector_path')).exists(),packet.get('selector_vector_path'))
                        if packet.get('state_switch_path'): add(checks,f'p0001_state_switch_exists:{d.get("draft_id")}',(root/packet.get('state_switch_path')).exists(),packet.get('state_switch_path'))
                        if d.get('state_switch_path'): add(checks,f'p0001_state_switch_metadata_exists:{d.get("draft_id")}',(root/d.get('state_switch_path')).exists(),d.get('state_switch_path'))
                        if d.get('ergodic_traversal_path'): add(checks,f'p0001_ergodic_traversal_metadata_exists:{d.get("draft_id")}',(root/d.get('ergodic_traversal_path')).exists(),d.get('ergodic_traversal_path'))
                        if d.get('zero_route_path'): add(checks,f'p0001_zero_route_metadata_exists:{d.get("draft_id")}',(root/d.get('zero_route_path')).exists(),d.get('zero_route_path'))
                        if d.get('return_diff_path'): add(checks,f'p0001_return_diff_metadata_exists:{d.get("draft_id")}',(root/d.get('return_diff_path')).exists(),d.get('return_diff_path'))
                        if d.get('patch_application_path'): add(checks,f'p0001_patch_application_metadata_exists:{d.get("draft_id")}',(root/d.get('patch_application_path')).exists(),d.get('patch_application_path'))
                        if d.get('render_receipt_path'): add(checks,f'p0001_render_receipt_exists:{d.get("draft_id")}',(root/d.get('render_receipt_path')).exists(),d.get('render_receipt_path'))
        else: add(checks,'p0001_not_draft_or_preflight_ok',p0001.get('status')=='preflight',str(p0001.get('status')))
    except Exception as e: add(checks,'p0001_branch_selector_policy',False,str(e))

    # Current-surface and cross-registry freshness checks are intentionally part of validate,
    # not only separate make targets, because stale compact state was a rev0022 failure mode.
    for label, runner in [
        ('deep_surface_consistency', run_deep_surface_consistency),
        ('pilot_queue_semantics', run_pilot_queue),
        ('surface_freshness', run_surface_freshness),
        ('revision_lineage_freshness', run_revision_lineage_freshness),
        ('open_questions_canonical', run_open_questions_canonical),
        ('source_health_coverage', run_source_health_coverage),
        ('reader_state_object', run_reader_state_object),
        ('external_material_pressure', run_external_material_pressure),
        ('wal_poem', run_wal_poem),
        ('oci_whiteout', run_oci_whiteout),
        ('bloom_false_positive', run_bloom_false_positive),
        ('source_snapshots', run_source_snapshots),
        ('release_surfaces', run_release_surfaces),
        ('candidate_reader_packet', run_candidate_reader_packet),
        ('reader_response_intake', run_reader_response_intake),
        ('reader_handoff_bundle', run_reader_handoff_bundle),
        ('candidate_pressure', run_candidate_pressure),
        ('fallback_subtraction', run_fallback_subtraction),
        ('judgment_firewall', run_judgment_firewall),
    ]:
        if runner is None:
            add(checks, f'{label}_runner_imported', False, 'import failed')
            continue
        try:
            subchecks = runner(root)
            add(checks, f'{label}_ok', all(c.get('ok') for c in subchecks), f'check_count={len(subchecks)}')
            for c in subchecks:
                add(checks, f'{label}:{c.get("name")}', c.get('ok'), c.get('detail',''))
        except Exception as e:
            add(checks, f'{label}_ok', False, str(e))

    try:
        manifest=load_json(root/'MANIFEST.json'); entries={e['path']:e for e in manifest.get('files',[])}
        if collect_files is None or MANIFEST_EXCLUDE is None:
            raise RuntimeError('shared release_tree policy import failed')
        expected=[rel for _path, rel in collect_files(root, exclude=MANIFEST_EXCLUDE)]
        missing=sorted(set(expected)-set(entries)); extra=sorted(set(entries)-set(expected))
        add(checks,'manifest_coverage',not missing and not extra,f'missing={len(missing)} extra={len(extra)}')
        bad=[]
        for rel,e in entries.items():
            p=root/rel
            if p.exists() and (sha256_file(p)!=e.get('sha256') or p.stat().st_size!=e.get('size')): bad.append(rel)
        add(checks,'manifest_hashes',len(bad)==0,f'bad={bad[:5]} count={len(bad)}')
        recorded=(root/'MANIFEST.sha256').read_text(encoding='utf-8').split()[0]
        add(checks,'manifest_sha256_sidecar',recorded==sha256_file(root/'MANIFEST.json'))
    except Exception as e: add(checks,'manifest_integrity',False,str(e))
    ok=all(c['ok'] for c in checks); return {'project':'LLMPoetry','revision':current_rev,'ok':ok,'checks':checks}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--write-report',action='store_true'); ap.add_argument('--verbose',action='store_true'); args=ap.parse_args(); root=Path(args.root); report=validate(root)
    if args.write_report:
        out=root/'reports/validation_report.json'; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    failed=[c for c in report.get('checks',[]) if not c.get('ok')]
    print(json.dumps(report if args.verbose else {'project':report.get('project'),'revision':report.get('revision'),'ok':report.get('ok'),'check_count':len(report.get('checks',[])),'failed_count':len(failed),'failed':failed[:20]}, indent=2, ensure_ascii=False))
    raise SystemExit(0 if report['ok'] else 1)
if __name__=='__main__': main()
