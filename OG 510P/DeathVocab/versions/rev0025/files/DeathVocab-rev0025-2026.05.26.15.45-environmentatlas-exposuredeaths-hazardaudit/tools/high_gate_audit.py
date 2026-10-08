#!/usr/bin/env python3
import json, re
from pathlib import Path
from collections import Counter, defaultdict
ROOT=Path(__file__).resolve().parents[1]

def text_of(x):
    vals=[]
    def walk(y):
        if isinstance(y, dict):
            for v in y.values(): walk(v)
        elif isinstance(y, list):
            for v in y: walk(v)
        elif y is not None:
            vals.append(str(y))
    walk(x)
    return ' '.join(vals).lower()

def detect(d):
    s=text_of({'title':d.get('title'), 'classes':d.get('record_classes'), 'axes':d.get('axes'), 'safety':d.get('safety')})
    doms=set(d.get('safety',{}).get('high_gate_domains',[]))
    if any(tok in s for tok in ['pediatric_high_gate','perinatal_loss','pediatric_and_perinatal','child_witness','child_private_material','stillbirth','neonatal','suid','sids','children at funerals','child visitor']): doms.add('pediatric_and_perinatal')
    if any(tok in s for tok in ['suicide','self_harm','suicide_safe']): doms.add('suicide_and_self_harm_aftermath')
    if any(tok in s for tok in ['overdose','substance_related','substance use','toxicology','naloxone']): doms.add('overdose_and_substance_related_death_aftermath')
    if any(tok in s for tok in ['custody','detention','prison','jail','immigration detention']): doms.add('death_in_custody_or_institutional_opacity')
    if re.search(r'\b(disaster|war|battlefield|violent)\b', s) or 'mass fatality' in s or 'contested death' in s: doms.add('violent_graphic_or_mass_death')
    if any(tok in s for tok in ['restricted_knowledge','indigenous_sovereignty','tukdam','sky burial']): doms.add('indigenous_or_restricted_tradition')
    if any(tok in s for tok in ['maid','medical aid in dying','vsed','death with dignity']): doms.add('chosen_or_hastened_dying_terms')
    if any(tok in s for tok in ['brain death','dcd','organ donation','opo','honor walk']): doms.add('organ_donation_brain_death_and_dcd')
    if any(tok in s for tok in ['unclaimed','unidentified','unrecovered','missing body','no body','no_bedside_witness','absence_unclaimed_unidentified_or_missing_body','case number','pending certificate']): doms.add('absence_unclaimed_unidentified_or_missing_body')
    if any(tok in s for tok in ['body_disposition_axis','body_disposition_autopsy_donation_or_disinterment','whole-body donation','anatomical gift','autopsy','post-mortem examination','disinterment','exhumation','alkaline hydrolysis','natural organic reduction']): doms.add('body_disposition_autopsy_donation_or_disinterment')
    return sorted(doms)

records=[]
for p in sorted((ROOT/'records'/'quarantine').glob('DV-REC-*.json')):
    records.append(json.loads(p.read_text(encoding='utf-8')))
counts=Counter(); not_blocked=[]; no_gate=[]
for d in records:
    doms=detect(d)
    for dom in doms: counts[dom]+=1
    if doms and d.get('review',{}).get('publication_review_state')!='blocked': not_blocked.append(d['record_id'])
    if doms and not d.get('safety',{}).get('publication_gate'): no_gate.append(d['record_id'])
report=json.loads((ROOT/'HIGH-GATE-COVERAGE-AUDIT.json').read_text(encoding='utf-8'))
if report.get('scope',{}).get('records_seen') != len(records):
    raise SystemExit('HIGH GATE AUDIT FAIL report count mismatch')
if report.get('publication_block_missing_count') != len(not_blocked):
    raise SystemExit('HIGH GATE AUDIT FAIL publication block count mismatch')
if not_blocked:
    raise SystemExit('HIGH GATE AUDIT FAIL unblocked high-gate records '+repr(not_blocked[:20]))
if no_gate:
    raise SystemExit('HIGH GATE AUDIT FAIL high-gate records without publication_gate '+repr(no_gate[:20]))
print('HIGH GATE AUDIT OK: %d records scanned; domains=%s' % (len(records), dict(counts)))
