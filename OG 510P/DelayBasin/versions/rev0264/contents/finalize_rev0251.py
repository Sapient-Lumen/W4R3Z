from __future__ import annotations
import json
from copy import deepcopy
from pathlib import Path

ROOT=Path('.')
REV='rev0251'
PREV='rev0250'
STAMP='2026.03.28.00.18'
CREATED_AT='2026-03-28T00:18:00-04:00'
SLUG='scopedistribution-diffusionquarantine-clustercarry-weaveglass'
BUNDLE=f'DelayBasin-{REV}-{STAMP}-{SLUG}.zip'
NEW_DOC='docs/10-method/refresh-scope-distribution-witnesses-clustered-observed-spillover-dispersed-observed-spillover-and-distribution-gated-generalization.md'
NEW_FAMILY='refresh_scope_distribution_state'
NEW_QWS='QWS-0229'

def read(p):
    return (ROOT/p).read_text(encoding='utf-8')

def write_json(p,obj):
    (ROOT/p).write_text(json.dumps(obj, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

def append_item(path,item):
    obj=json.loads(read(path))
    if not any(x.get('id')==item.get('id') for x in obj['items']):
        obj['items'].append(item)
    obj['revision']=REV
    write_json(path,obj)
    return obj

transfer_item={
    'id':'TL-0156',
    'title':'refresh-scope-distribution evidence supports resolving OQ-0146 with one compact cluster-vs-spread card rather than a diffusion court',
    'state':'supporting-only',
    'reviewed_pattern':'clustered observed spillover vs dispersed observed spillover across widened families',
    'import_decision':'support a compact refresh-scope-distribution witness and resolve OQ-0146',
    'adopted_take':'DelayBasin should add one compact witness that says whether broader directly observed spillover is clustered-observed-spillover, dispersed-observed-spillover, distribution-gated-generalization, or honestly mixed',
    'supporting_only_take':'the current evidence cleanly supports a bounded refresh-scope-distribution witness without promoting broader refresh-distribution governance',
    'deferred_or_rejected_take':['refresh-distribution court','diffusion senate','spread governor'],
    'local_gap':'the archive still lacked one compact successor surface for whether broader directly observed spillover still clustered inside one named family or was already dispersed across several widened families',
    'anchor_surfaces':['docs/10-method/refresh-scope-extent-witnesses-single-observed-slice-patterned-observed-spillover-and-extent-gated-generalization.md','docs/20-constitution/open-question-registry.md','docs/00-meta/trajectory-map.md',f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}'],
    'open_question':'OQ-0147',
    'repair':'ordinary-continuation',
    'origin_revision':REV,
    'action_lane':'keep-compact',
    'gate_class':'concrete-evidence',
    'discharge':'reopen-only-if-refresh-scope-distribution-overflows',
    'revision':REV,
    'witness_surface':'DATACUBE-TRANSFER-LEDGER.json#TL-0156',
    'transfer_state':'supporting-only',
    'bounded_take':'Keep the archive compact by extracting one refresh-scope-distribution witness over the existing refresh-scope-extent, grouping, topology-domain, and failure-domain surfaces; do not promote a refresh-distribution court, diffusion senate, or spread governor.',
    'explicit_non_take':['no refresh-distribution court','no diffusion senate','no spread governor'],
    'open_transfer_question':'whether later passes should add a separate refresh-scope-axis witness once refresh scope distribution is explicit',
    'missing_support':'a later public check on whether one compact refresh-scope-distribution witness keeps sufficing',
    'current_support':['APPLICABILITY-LEDGER.json#AP-0145','FOREIGN-PRESSURE-LEDGER.json#FP-0150','DATACUBE-TRANSFER-LEDGER.json#TL-0156'],
    'discharge_path':'either show later that one compact refresh-scope-distribution witness keeps sufficing or promote broader refresh-distribution governance explicitly',
    'reviewed_datacubes':[
        {'datacube':'StatuspageComponentGroups-2026','surfaces':['REF-0946'],'pattern':'child components can remain inside one named component group','pressure':'DelayBasin should distinguish a local grouped family cluster from broader dispersed spread'},
        {'datacube':'AlertmanagerClusterGrouping-2026','surfaces':['REF-0947'],'pattern':'many exact alerts can still be grouped by cluster and alertname','pressure':'DelayBasin should distinguish clustered observed spillover from dispersed spread across several groups'},
        {'datacube':'GrafanaScopedGrouping-2026','surfaces':['REF-0948'],'pattern':'grouping depends on exact label matches and distinct team/service scopes','pressure':'DelayBasin should keep one grouped local family distinct from dispersed cross-scope spread'},
        {'datacube':'KubernetesTopologySpread-2026','surfaces':['REF-0949'],'pattern':'spread is evaluated across named topology domains','pressure':'DelayBasin should distinguish one local failure-domain cluster from dispersed multi-domain spread'},
        {'datacube':'GoogleCloudFailureDomains-2026','surfaces':['REF-0950'],'pattern':'zones and regions are used to separate correlated failures','pressure':'DelayBasin should distinguish one local correlated cluster from dispersed multi-zone or multi-region spread'}
    ]
}
transfer=json.loads(read('DATACUBE-TRANSFER-LEDGER.json'))
if not any(x.get('id')=='TL-0156' for x in transfer['items']):
    transfer['items'].append(transfer_item)
new_open_q='Whether a later pass should add one bounded refresh-scope-axis witness once refresh scope distribution is explicit, but only if one-axis dispersion keeps being mistaken for cross-axis corroborated diffusion in honest continuation work.'
if new_open_q not in transfer.get('open_questions',[]):
    transfer.setdefault('open_questions',[]).append(new_open_q)
transfer['revision']=REV
write_json('DATACUBE-TRANSFER-LEDGER.json',transfer)

append_item('RESOLUTION-LEDGER.json',{
    'id':'RS-0153','title':'resolve OQ-0146 with one compact refresh-scope-distribution witness rather than a diffusion governor','state':'resolved','closure_state':'resolved',
    'closure_reason':'rev0251 extracted one compact refresh-scope-distribution witness, kept the admitted refresh-scope-extent and grouping/domain analog surfaces narrow, and kept stronger refresh-distribution-governance stories quarantined.',
    'discharge':'reopen-only-if-refresh-scope-distribution-overflows','gate_class':'concrete-evidence','origin_revision':REV,
    'prior_state':'open gap: DelayBasin already had refresh-scope-extent truth but still lacked one compact successor surface for whether broader directly observed spillover still clustered inside one named family or was already dispersed across several widened families.',
    'question':'whether one compact refresh-scope-distribution witness over the existing refresh-scope-extent, grouping, topology-domain, and failure-domain surfaces is enough for honest clustered-vs-dispersed comparison',
    'reopen_trigger':'refresh-scope-distribution pressure overflows one compact successor surface',
    'reopen_triggers':['later revisions need standing governance over cluster admissibility, diffusion thresholds, spread authority, or broader dispersed-spillover policy that one compact refresh-scope-distribution witness cannot honestly absorb'],
    'repair':'ordinary-continuation','resolved_objects':['OQ-0146','AP-0145','FP-0150','TL-0156'],'revision':REV,'successor_surface':NEW_DOC,'target_surfaces':[NEW_DOC],'action_lane':'keep-compact','witness_surface':'RESOLUTION-LEDGER.json#RS-0153'})

append_item('RETROSPECTIVE-QUEUE.json',{
    'id':'RT-0140','title':'revisit whether refresh-scope-distribution pressure stayed bounded after rev0251','state':'cooling','candidate_surface':f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}',
    'cooldown_window':'keep the stronger refresh-distribution court, diffusion senate, or spread governor story cooled until at least one later revision shows that one compact refresh-scope-distribution witness is no longer enough.',
    'adjudication_family':'refresh scope distribution / cluster-vs-diffusion gating / spread-governance pressure','supersession_link':'OBLIGATION-LEDGER.json#OB-0146','origin_revision':REV,
    'discharge':'keep-cooling-unless-refresh-scope-distribution-overflows','action_lane':'keep-compact','gate_class':'overflow','witness_surface':'RETROSPECTIVE-QUEUE.json#RT-0140','revision':REV,'cooling_state':'cooling','disposition':'await-adjudication','repair':'keep-cooling'})

append_item('FIREBREAK-LEDGER.json',{
    'id':'FB-0147','title':'the refresh-scope-distribution import should count as one compact cluster-vs-spread repair, not as promotion of a diffusion court','state':'withheld','witness_surface':'FIREBREAK-LEDGER.json#FB-0147',
    'judged_property':'the rev0251 decision that DelayBasin should extract one compact refresh-scope-distribution witness over the existing refresh-scope-extent, grouping, topology-domain, and failure-domain surfaces and `refresh_scope_distribution_state` family while the broader refresh-distribution court / diffusion senate / spread governor story remains quarantined',
    'public_extract':[NEW_DOC,'docs/10-method/refresh-scope-extent-witnesses-single-observed-slice-patterned-observed-spillover-and-extent-gated-generalization.md','docs/20-constitution/open-question-registry.md','FOREIGN-PRESSURE-LEDGER.json#FP-0150','APPLICABILITY-LEDGER.json#AP-0145','REVISION-RECEIPT.json'],
    'withheld_trace_surface':'same-session drafting residue behind the compact refresh-scope-distribution-witness versus spread-governor decision','allowed_role':'bounded drafting aid only; not public support for a broader refresh-distribution court, diffusion senate, or spread governor',
    'exposure_rule':'expose or reintegrate only if later passes show that one compact refresh-scope-distribution witness cannot keep cluster-vs-dispersed truth bounded','trace_state':'withheld','repair':'ordinary-continuation','origin_revision':REV,'action_lane':'keep-compact','gate_class':'overflow','firebreak_surface':'FIREBREAK-LEDGER.json#FB-0147','discharge':'reopen-only-if-refresh-scope-distribution-overflows','revision':REV,'blocked_object':'standing refresh-distribution court, diffusion senate, or spread governor'})

vocab=json.loads(read('WITNESS-VOCABULARY.json'))
vocab['revision']=REV
vocab['families'][NEW_FAMILY]={
    'allowed':['clustered-observed-spillover','dispersed-observed-spillover','distribution-gated-generalization','mixed-refresh-scope-distribution'],
    'surfaces':['WITNESS-VOCABULARY.json','REVISION-RECEIPT.json',NEW_DOC],
    'excluded_synonyms':['many-nearby-hits-means-dispersed','one-group-counts-as-every-family','same-domain-spread-is-broad-enough','distribution-ish'],
    'comparability_budget':'refresh-scope-distribution truth is compared by token; the compact refresh-scope-distribution witness says whether broader directly observed spillover is still clustered inside one named widened family, already dispersed across several widened families, still distribution-gated from broader generalization, or honestly mixed, while exact component rosters, label matrices, topology-domain ids, zone names, and long diffusion narratives stay in surrounding prose'
}
write_json('WITNESS-VOCABULARY.json',vocab)

status=json.loads(read('SURFACE-STATUS.json'))
status['operational_head']['revision']=REV
status['status_lanes']['frozen_public_surface']=BUNDLE
status['status_lanes']['current_release_surface']=BUNDLE
status['citation_head']={'revision':REV,'surface':BUNDLE}
status['previous_citation_head']={'revision':PREV,'surface':'DelayBasin-rev0250-2026.03.27.23.59-scopeextent-patternquarantine-slicecarry-ridgeglass.zip'}
status['revision']=REV
status['stamp']=STAMP
status['slug']=SLUG
write_json('SURFACE-STATUS.json',status)

write_json('RELEASE-MANIFEST.json',{'project':'DelayBasin','revision':REV,'timestamp':STAMP,'slug':SLUG,'bundle':BUNDLE})

# receipt
receipt=json.loads(read('REVISION-RECEIPT.json'))
receipt['revision']=REV
receipt['previous_revision']=PREV
receipt['summary']='Resolved OQ-0146 with one compact refresh-scope-distribution witness that separates clustered observed spillover from dispersed observed spillover while keeping stronger refresh-distribution governance quarantined.'
receipt['canon_additions']=[NEW_DOC,'RS-0153 resolved OQ-0146 with one compact refresh-scope-distribution witness']
receipt['quarantine_additions']=[f'{NEW_QWS} — refresh-distribution court / diffusion senate / spread governor']
receipt['refs_used']=['REF-0946','REF-0947','REF-0948','REF-0949','REF-0950']
receipt['touched_surfaces']=[NEW_DOC,'docs/00-meta/bibliography.md','docs/00-meta/llm-runbook.md','docs/README.md','docs/20-constitution/claim-registry.md','docs/20-constitution/open-question-registry.md','docs/20-constitution/prompt-pair-registry.md','docs/00-meta/trajectory-map.md','docs/50-promptcraft/prompt-pairs.md','docs/90-quarantine/wild-speculations-2026-03-08.md','WITNESS-VOCABULARY.json','FOLLOWTHROUGH-QUEUE.json','ASSUMPTION-LEDGER.json','OBLIGATION-LEDGER.json','APPLICABILITY-LEDGER.json','FOREIGN-PRESSURE-LEDGER.json','DATACUBE-TRANSFER-LEDGER.json','RESOLUTION-LEDGER.json','RETROSPECTIVE-QUEUE.json','FIREBREAK-LEDGER.json','REVISION-RECEIPT.json','SURFACE-STATUS.json','RELEASE-MANIFEST.json','CHANGELOG.md','ARCHIVE_INDEX.md','tools/packet_contract_common.py','tools/check_refresh_scope_distribution_witness_contract.py']
receipt['packaged_bundle_filename']=BUNDLE
receipt['basis_witness'].update({'expected_head':PREV,'observed_head':PREV,'basis_surfaces':['docs/10-method/refresh-scope-extent-witnesses-single-observed-slice-patterned-observed-spillover-and-extent-gated-generalization.md','docs/00-meta/trajectory-map.md','docs/20-constitution/open-question-registry.md'],'basis_omission_basis':'broader refresh-distribution governance drafting was intentionally omitted from canon because the evidence only justified one bounded refresh-scope-distribution witness','basis_of_change':'rev0250 extends continuity law by distinguishing one newly observed widened slice from a broader observed spillover pattern, which opens the next question of whether broader observed spillover still clusters locally or is honestly dispersed across widened families.','revision_span':f'{PREV} -> {REV}'})
receipt['scope_witness'].update({'exact_target':'resolve OQ-0146 with one compact refresh-scope-distribution witness and keep stronger refresh-distribution governance honestly quarantined','scope_surfaces':[NEW_DOC,'docs/20-constitution/open-question-registry.md','docs/00-meta/trajectory-map.md','docs/90-quarantine/wild-speculations-2026-03-08.md'],'ambient_exclusions':['no refresh-distribution court','no diffusion senate','no spread governor'],'scope_of_change':'one compact successor witness plus one quarantined speculative move'})
receipt['status_witness']['frozen_public_surface']=BUNDLE
# newest witness objects
for key,path in [('retrospective_write_witness','RETROSPECTIVE-QUEUE.json'),('followthrough_witness','FOLLOWTHROUGH-QUEUE.json'),('assumption_witness','ASSUMPTION-LEDGER.json'),('obligation_witness','OBLIGATION-LEDGER.json'),('applicability_witness','APPLICABILITY-LEDGER.json'),('foreign_pressure_witness','FOREIGN-PRESSURE-LEDGER.json'),('transfer_witness','DATACUBE-TRANSFER-LEDGER.json'),('resolution_witness','RESOLUTION-LEDGER.json'),('reasoning_firebreak_witness','FIREBREAK-LEDGER.json'),('firebreak_witness','FIREBREAK-LEDGER.json')]:
    receipt[key]=json.loads(read(path))['items'][-1]
receipt['vocabulary_witness']={'witness_surface':'WITNESS-VOCABULARY.json','controlled_families':['action_lane','gate_class',NEW_FAMILY],'target_surfaces':['WITNESS-VOCABULARY.json','REVISION-RECEIPT.json',NEW_DOC],'ambient_synonyms_excluded':['many-nearby-hits-means-dispersed','one-group-counts-as-every-family','same-domain-spread-is-broad-enough','distribution-ish'],'comparability_budget':'refresh-scope-distribution truth is compared by token; the compact refresh-scope-distribution witness says whether broader directly observed spillover is still clustered inside one named widened family, already dispersed across several widened families, still distribution-gated from broader generalization, or honestly mixed, while exact component rosters, label matrices, topology-domain ids, zone names, and long diffusion narratives stay in surrounding prose','vocabulary_state':'locked','repair':'ordinary-continuation',NEW_FAMILY:'clustered-observed-spillover|dispersed-observed-spillover|distribution-gated-generalization|mixed-refresh-scope-distribution'}
receipt['counterfactual_shadow']={'status':'rejected-nearby-move','nearby_rejected_move':'broader refresh-distribution court / diffusion senate / spread governor','pivot_surface':f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}','rejection_reason':'current external pressure supports one compact cluster-vs-spread witness, not standing governance over diffusion or spread admissibility','still_live':f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}'}
receipt['summary_highlight']='clustercarry'
receipt['codename']='weaveglass'
receipt['created_at']=CREATED_AT
receipt['comparison_witness']={'previous_revision':PREV,'current_revision':REV,'current_pressure_id':'FP-0150','current_import_id':'TL-0156','basis_surface':'docs/10-method/refresh-scope-extent-witnesses-single-observed-slice-patterned-observed-spillover-and-extent-gated-generalization.md','delta_surface':NEW_DOC,'comparison_summary':'rev0251 adds one compact refresh-scope-distribution witness so broader directly observed spillover no longer stands in for dispersed spread when the evidence is still only a local named family cluster.'}
receipt['changes']=[{'kind':'canon','surface':NEW_DOC,'summary':'added one compact refresh-scope-distribution witness with clustered, dispersed, distribution-gated, and mixed states'},{'kind':'quarantine','surface':f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}','summary':'kept stronger refresh-distribution governance quarantined rather than promoting it into canon'},{'kind':'hygiene','surface':'tools/packet_contract_common.py','summary':'centralized refresh-scope-family validator entrypoints into one helper path'}]
receipt['receipt_freshness_witness']={'packaged_bundle_filename':BUNDLE,'manifest_timestamp_token':STAMP,'receipt_timestamp_token':STAMP,'bundle_stem_suffix_relation':'slug ends with clustercarry + weaveglass and remains aligned to the current summary/codename pair while preserving the diffusionquarantine middle token','current_import_id':'TL-0156','current_pressure_id':'FP-0150','change_anchor_surface':'CHANGELOG.md','freshness_state':'current-aligned','repair':'ordinary-continuation'}
receipt['question_posture_witness']={'resolution_surface':'RESOLUTION-LEDGER.json','registry_surface':'docs/20-constitution/open-question-registry.md','trajectory_surface':'docs/00-meta/trajectory-map.md','synced_resolved_questions':['OQ-0146'],'frontier_selection_rule':'resolved OQ-0146 is synchronized across resolution ledger, registry, and trajectory while frontier selection advances to OQ-0147','posture_state':'resolved-sync-current','repair':'ordinary-continuation'}
receipt['current_import_id']='TL-0156'
receipt['current_pressure_id']='FP-0150'
receipt['import_witness']=deepcopy(receipt['transfer_witness'])
receipt['new_classes_or_families']=[NEW_FAMILY]
receipt['quarantined_non_take']=['refresh-distribution court','diffusion senate','spread governor']
receipt['artifacts_touched']=list(receipt['touched_surfaces'])
receipt['refresh_scope_distribution_witness']={'witness_surface':NEW_DOC,'family':NEW_FAMILY,'state_tokens':['clustered-observed-spillover','dispersed-observed-spillover','distribution-gated-generalization','mixed-refresh-scope-distribution'],'overflow_rule':'reopen-only-if-refresh-scope-distribution-overflows'}
receipt['refresh_scope_distribution_witness_contract']={'family':NEW_FAMILY,'states':['clustered-observed-spillover','dispersed-observed-spillover','distribution-gated-generalization','mixed-refresh-scope-distribution']}
receipt['refresh_scope_distribution_witness_meta']={'checker':'tools/check_refresh_scope_distribution_witness_contract.py'}
write_json('REVISION-RECEIPT.json',receipt)

print('finalize_rev0251: OK')
