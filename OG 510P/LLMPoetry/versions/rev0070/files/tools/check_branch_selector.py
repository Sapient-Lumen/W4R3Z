#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys
from pathlib import Path
WORD_RE=re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")
def final_word(text):
    words=WORD_RE.findall(text); return words[-1].lower() if words else ''
def add(checks,name,ok,detail=''): checks.append({'name':name,'ok':bool(ok),'detail':detail})
def validate_packet(root: Path, packet_rel: str, draft_rel: str, checks: list):
    packet_path=root/packet_rel; draft_path=root/draft_rel
    add(checks,f'{packet_rel}:exists',packet_path.exists()); add(checks,f'{draft_rel}:exists',draft_path.exists())
    if not packet_path.exists() or not draft_path.exists(): return
    try: packet=json.loads(packet_path.read_text(encoding='utf-8')); add(checks,f'{packet_rel}:parse',True)
    except Exception as e: add(checks,f'{packet_rel}:parse',False,str(e)); return
    draft_text=draft_path.read_text(encoding='utf-8',errors='replace'); claim=packet.get('selected_initials_claim',''); layers=packet.get('layers',[])
    expected_count=packet.get('candidate_count_per_layer') or (len(layers[0].get('candidates',[])) if layers else None)
    add(checks,f'{packet_rel}:same_turn_judgment_prohibited_flag',packet.get('same_turn_judgment_prohibited') is True)
    add(checks,f'{packet_rel}:layers_match_claim_length',len(layers)==len(claim),f'layers={len(layers)} claim={claim}')
    layer_ids=[]; selected=[]; selected_path=[]; ids=[]; candidate_count_ok=True; exactly_one_ok=True; unselected=[]
    for layer in layers:
        layer_ids.append(layer.get('layer_id')); candidates=layer.get('candidates',[])
        if expected_count is not None and len(candidates)!=expected_count: candidate_count_ok=False
        sels=[c for c in candidates if c.get('selected') is True]
        if len(sels)!=1: exactly_one_ok=False
        if sels: selected.append(sels[0].get('text','')); selected_path.append(sels[0].get('candidate_id'))
        for c in candidates:
            ids.append(c.get('candidate_id'))
            if c.get('selected') is not True: unselected.append(c.get('text',''))
    initials=''.join((s.strip()[:1] or '') for s in selected)
    add(checks,f'{packet_rel}:layer_ids_match_claim',''.join(layer_ids)==claim,f'layer_ids={layer_ids} claim={claim}')
    add(checks,f'{packet_rel}:candidate_count_per_layer',candidate_count_ok,f'expected={expected_count}')
    add(checks,f'{packet_rel}:exactly_one_selected_per_layer',exactly_one_ok)
    add(checks,f'{packet_rel}:selected_path_matches_packet',selected_path==packet.get('selected_path'),f'selected_path={selected_path}')
    add(checks,f'{packet_rel}:selected_line_initials_match_claim',initials==claim,initials)
    missing=[s for s in selected if s not in draft_text]; add(checks,f'{packet_rel}:selected_lines_in_draft',not missing,f'missing={missing}')
    prompt_text=packet.get('prompt_text',''); add(checks,f'{packet_rel}:prompt_text_in_draft',bool(prompt_text) and prompt_text in draft_text)
    add(checks,f'{packet_rel}:candidate_ids_unique',len(ids)==len(set(ids)))
    if packet.get('all_candidates_must_appear_in_draft') is True:
        missing_all=[c.get('text','') for layer in layers for c in layer.get('candidates',[]) if c.get('text','') not in draft_text]
        add(checks,f'{packet_rel}:all_candidates_in_draft',not missing_all,f'missing={missing_all[:5]}')
    if packet.get('unselected_final_words_claim'):
        shadow=' '.join(final_word(t) for t in unselected)
        add(checks,f'{packet_rel}:unselected_final_words_match_claim',shadow==packet.get('unselected_final_words_claim'),shadow)
        add(checks,f'{packet_rel}:unselected_shadow_sentence_in_draft',shadow in draft_text,shadow)
    if packet.get('selector_map_path'): add(checks,f'{packet_rel}:selector_map_exists',(root/packet.get('selector_map_path')).exists(),packet.get('selector_map_path'))
    if packet.get('draft_is_rendered_from_packet') is True: add(checks,f'{packet_rel}:render_script_exists',(root/packet.get('render_script','')).exists(),packet.get('render_script',''))
def run(root: Path):
    checks=[]; meta_path=root/'poems'/'P0001'/'metadata.json'
    try: meta=json.loads(meta_path.read_text(encoding='utf-8')); add(checks,'p0001_metadata_parse',True)
    except Exception as e: add(checks,'p0001_metadata_parse',False,str(e)); return checks
    add(checks,'p0001_status_draft_or_preflight',meta.get('status') in {'preflight','draft'},str(meta.get('status')))
    drafts=meta.get('drafts',[])
    if meta.get('status')!='draft': add(checks,'branch_selector_not_required_for_preflight',True); return checks
    add(checks,'p0001_has_draft_record',len(drafts)>=1); branch_drafts=[d for d in drafts if d.get('branch_packet_path')]
    add(checks,'p0001_has_branch_draft',len(branch_drafts)>=1)
    for d in branch_drafts: validate_packet(root,d.get('branch_packet_path'),d.get('path'),checks)
    return checks
def main(root='.'):
    checks=run(Path(root)); ok=all(c['ok'] for c in checks)
    print(json.dumps({'ok':ok,'checks':checks,'failed':[c for c in checks if not c['ok']]}, indent=2, ensure_ascii=False)); return 0 if ok else 1
if __name__=='__main__': sys.exit(main(sys.argv[1] if len(sys.argv)>1 else '.'))
