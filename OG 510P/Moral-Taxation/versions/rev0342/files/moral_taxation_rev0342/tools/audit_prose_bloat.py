#!/usr/bin/env python3
import json, pathlib, re, sys
root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
errors=[]
version=(root/'VERSION').read_text(encoding='utf-8').strip()
cube=json.loads((root/'cube-index.json').read_text(encoding='utf-8'))
profiles={p['route_id'] for p in json.loads((root/'docs/00-meta/actor-accountability-profiles.json').read_text(encoding='utf-8')).get('profiles',[])}
path_to_id={rec['path']:rec['id'] for rec in cube.get('route_records',[])}
route_paths=[root/'docs/20-calibration', root/'docs/10-framework']
texts=[]
for base in route_paths:
    if base.exists():
        for p in base.glob('*.md'):
            texts.append((p, p.read_text(encoding='utf-8')))
full='\n'.join(t for _,t in texts)
if re.search(r'^## Rev\d{4} accountability map$', full, re.M):
    errors.append('legacy Rev#### accountability-map headings remain; use Accountability capsule sections')
if '| Question | Default accountability answer |' in full:
    errors.append('legacy accountability-map table header remains')
legacy_phrase='route should now be read as a control, benefit, bottleneck, evidence, and fallback-duty map rather than a broad doctrinal category'
if legacy_phrase in full:
    errors.append('legacy accountability-map boilerplate remains')
profile_link_fail=[]
route_id_fail=[]
long_capsules=[]
capsule_count=0
for p,text in texts:
    rel=p.relative_to(root).as_posix()
    for m in re.finditer(r'\n## Accountability capsule\n([\s\S]*?)(?=\n## |\Z)', text):
        capsule_count += 1
        section=m.group(1)
        if 'actor-accountability-profiles.json' not in section:
            profile_link_fail.append(rel)
        rid=path_to_id.get(rel)
        if rid and f'`{rid}`' not in section:
            route_id_fail.append(rel)
        elif rid and rid not in profiles:
            route_id_fail.append(rel)
        size=len(m.group(0).encode('utf-8'))
        if size > 1200:
            long_capsules.append(f'{rel}:{size}')
if profile_link_fail:
    errors.append('accountability capsules missing profile link: '+', '.join(sorted(set(profile_link_fail))[:10]))
if route_id_fail:
    errors.append('accountability capsules missing matching route id/profile: '+', '.join(sorted(set(route_id_fail))[:10]))
if long_capsules:
    errors.append('accountability capsules exceed 1200 bytes: '+', '.join(long_capsules[:10]))
summary=cube.get('audit_summary',{})
if summary.get('prose_bloat_audit_required') is not True:
    errors.append('cube audit_summary must mark prose_bloat_audit_required=True')
metrics=summary.get('prose_bloat_metrics',{})
expected={
    'legacy_accountability_map_headings_remaining': len(re.findall(r'^## Rev\d{4} accountability map$', full, re.M)),
    'legacy_accountability_table_headers_remaining': full.count('| Question | Default accountability answer |'),
    'legacy_accountability_boilerplate_remaining': full.count(legacy_phrase),
    'accountability_capsule_count': capsule_count,
}
for k,v in expected.items():
    if metrics.get(k) != v:
        errors.append(f'prose-bloat metric {k} stale: expected {v}, got {metrics.get(k)!r}')
if expected['legacy_accountability_map_headings_remaining'] != 0 or expected['legacy_accountability_table_headers_remaining'] != 0 or expected['legacy_accountability_boilerplate_remaining'] != 0:
    errors.append('legacy accountability prose artifacts must be zero')
if capsule_count < 100:
    errors.append(f'expected at least 100 accountability capsules after controller-AI pass, got {capsule_count}')

def family_texts(family):
    paths=[rec['path'] for rec in cube.get('route_records',[]) if rec.get('family')==family]
    out=[]
    for rel in paths:
        p=root/rel
        if p.exists():
            out.append((rel,p.read_text(encoding='utf-8'),p.stat().st_size))
    return out

# Rev0307 family-specific bloat gate: public-finance docs should delegate failure taxonomies and change triggers to cube axes.
pf_texts=family_texts('public_finance_core')
pf_full='\n'.join(t for _,t,_ in pf_texts)
pf_metrics={
    'public_finance_legacy_antipattern_sections_remaining': len(re.findall(r'^## Anti-patterns$', pf_full, re.M)),
    'public_finance_legacy_change_trigger_sections_remaining': len(re.findall(r'^## What would change the recommendation$', pf_full, re.M)),
    'public_finance_failure_mode_capsules': len(re.findall(r'^## Failure-mode capsule$', pf_full, re.M)),
    'public_finance_recalibration_trigger_capsules': len(re.findall(r'^## Recalibration trigger capsule$', pf_full, re.M)),
    'public_finance_route_memo_total_bytes_after': sum(size for _,_,size in pf_texts),
}
for k,v in pf_metrics.items():
    if metrics.get(k) != v:
        errors.append(f'public-finance prose metric {k} stale: expected {v}, got {metrics.get(k)!r}')
if pf_metrics['public_finance_legacy_antipattern_sections_remaining'] != 0:
    errors.append('public-finance route memos must use Failure-mode capsule, not legacy Anti-patterns sections')
if pf_metrics['public_finance_legacy_change_trigger_sections_remaining'] != 0:
    errors.append('public-finance route memos must use Recalibration trigger capsule, not legacy change-trigger sections')
if pf_metrics['public_finance_route_memo_total_bytes_after'] > 315000:
    errors.append(f'public-finance route memos total {pf_metrics["public_finance_route_memo_total_bytes_after"]} bytes; expected <=315000 after rev0307 compactness pass')

# Rev0308 controller-AI bloat gate: controller docs should delegate failure/trigger/accountability maps to cube axes and profiles.
ca_texts=family_texts('controller_ai')
ca_full='\n'.join(t for _,t,_ in ca_texts)
ca_metrics={
    'controller_ai_legacy_antipattern_sections_remaining': len(re.findall(r'^## Anti-patterns$', ca_full, re.M)),
    'controller_ai_legacy_change_trigger_sections_remaining': len(re.findall(r'^## What would change the recommendation$', ca_full, re.M)),
    'controller_ai_legacy_accountability_map_sections_remaining': len(re.findall(r'^## Accountability map$', ca_full, re.M)),
    'controller_ai_failure_mode_capsules': len(re.findall(r'^## Failure-mode capsule$', ca_full, re.M)),
    'controller_ai_recalibration_trigger_capsules': len(re.findall(r'^## Recalibration trigger capsule$', ca_full, re.M)),
    'controller_ai_accountability_capsules': len(re.findall(r'^## Accountability capsule$', ca_full, re.M)),
    'controller_ai_route_memo_total_bytes_after': sum(size for _,_,size in ca_texts),
}
for k,v in ca_metrics.items():
    if metrics.get(k) != v:
        errors.append(f'controller-AI prose metric {k} stale: expected {v}, got {metrics.get(k)!r}')
if ca_metrics['controller_ai_legacy_antipattern_sections_remaining'] != 0:
    errors.append('controller-AI route memos must use Failure-mode capsule, not legacy Anti-patterns sections')
if ca_metrics['controller_ai_legacy_change_trigger_sections_remaining'] != 0:
    errors.append('controller-AI route memos must use Recalibration trigger capsule, not legacy change-trigger sections')
if ca_metrics['controller_ai_legacy_accountability_map_sections_remaining'] != 0:
    errors.append('controller-AI route memos must use Accountability capsule, not legacy Accountability map sections')
if ca_metrics['controller_ai_accountability_capsules'] != len(ca_texts):
    errors.append(f'every controller-AI route memo needs one accountability capsule: expected {len(ca_texts)}, got {ca_metrics["controller_ai_accountability_capsules"]}')
if ca_metrics['controller_ai_route_memo_total_bytes_after'] > 188000:
    errors.append(f'controller-AI route memos total {ca_metrics["controller_ai_route_memo_total_bytes_after"]} bytes; expected <=188000 after rev0308 compactness pass')

# Rev0309 tax-administration bloat gate: tax-admin docs should delegate failure/trigger/accountability maps to cube axes and profiles.
ta_texts=family_texts('tax_administration_access')
ta_full='\n'.join(t for _,t,_ in ta_texts)
ta_metrics={
    'tax_admin_legacy_antipattern_sections_remaining': len(re.findall(r'^## Anti-patterns$', ta_full, re.M)),
    'tax_admin_legacy_change_trigger_sections_remaining': len(re.findall(r'^## What would change the recommendation$', ta_full, re.M)),
    'tax_admin_legacy_accountability_map_sections_remaining': len(re.findall(r'^## Accountability map$', ta_full, re.M)),
    'tax_admin_failure_mode_capsules': len(re.findall(r'^## Failure-mode capsule$', ta_full, re.M)),
    'tax_admin_recalibration_trigger_capsules': len(re.findall(r'^## Recalibration trigger capsule$', ta_full, re.M)),
    'tax_admin_accountability_capsules': len(re.findall(r'^## Accountability capsule$', ta_full, re.M)),
    'tax_admin_route_memo_total_bytes_after': sum(size for _,_,size in ta_texts),
}
for k,v in ta_metrics.items():
    if metrics.get(k) != v:
        errors.append(f'tax-administration prose metric {k} stale: expected {v}, got {metrics.get(k)!r}')
if ta_metrics['tax_admin_legacy_antipattern_sections_remaining'] != 0:
    errors.append('tax-administration route memos must use Failure-mode capsule, not legacy Anti-patterns sections')
if ta_metrics['tax_admin_legacy_change_trigger_sections_remaining'] != 0:
    errors.append('tax-administration route memos must use Recalibration trigger capsule, not legacy change-trigger sections')
if ta_metrics['tax_admin_legacy_accountability_map_sections_remaining'] != 0:
    errors.append('tax-administration route memos must use Accountability capsule, not legacy Accountability map sections')
if ta_metrics['tax_admin_accountability_capsules'] != len(ta_texts):
    errors.append(f'every tax-administration route memo needs one accountability capsule: expected {len(ta_texts)}, got {ta_metrics["tax_admin_accountability_capsules"]}')
if ta_metrics['tax_admin_route_memo_total_bytes_after'] > 144000:
    errors.append(f'tax-administration route memos total {ta_metrics["tax_admin_route_memo_total_bytes_after"]} bytes; expected <=144000 after rev0309 compactness pass')

# Rev0310 legal-enforcement bloat gate: coercive route memos should delegate failure/trigger/accountability maps to cube axes and profiles.
le_texts=family_texts('legal_enforcement_penalty')
le_full='\n'.join(t for _,t,_ in le_texts)
le_metrics={
    'legal_enforcement_legacy_antipattern_sections_remaining': len(re.findall(r'^## Anti-patterns$', le_full, re.M)),
    'legal_enforcement_legacy_change_trigger_sections_remaining': len(re.findall(r'^## What would change the recommendation$', le_full, re.M)),
    'legal_enforcement_failure_mode_capsules': len(re.findall(r'^## Failure-mode capsule$', le_full, re.M)),
    'legal_enforcement_recalibration_trigger_capsules': len(re.findall(r'^## Recalibration trigger capsule$', le_full, re.M)),
    'legal_enforcement_accountability_capsules': len(re.findall(r'^## Accountability capsule$', le_full, re.M)),
    'legal_enforcement_route_memo_total_bytes_after': sum(size for _,_,size in le_texts),
}
for k,v in le_metrics.items():
    if metrics.get(k) != v:
        errors.append(f'legal-enforcement prose metric {k} stale: expected {v}, got {metrics.get(k)!r}')
if le_metrics['legal_enforcement_legacy_antipattern_sections_remaining'] != 0:
    errors.append('legal-enforcement route memos must use Failure-mode capsule, not legacy Anti-patterns sections')
if le_metrics['legal_enforcement_legacy_change_trigger_sections_remaining'] != 0:
    errors.append('legal-enforcement route memos must use Recalibration trigger capsule, not legacy change-trigger sections')
if le_metrics['legal_enforcement_accountability_capsules'] != len(le_texts):
    errors.append(f'every legal-enforcement route memo needs one accountability capsule: expected {len(le_texts)}, got {le_metrics["legal_enforcement_accountability_capsules"]}')
if le_metrics['legal_enforcement_failure_mode_capsules'] != len(le_texts):
    errors.append(f'every legal-enforcement route memo needs one Failure-mode capsule: expected {len(le_texts)}, got {le_metrics["legal_enforcement_failure_mode_capsules"]}')
if le_metrics['legal_enforcement_recalibration_trigger_capsules'] != len(le_texts):
    errors.append(f'every legal-enforcement route memo needs one Recalibration trigger capsule: expected {len(le_texts)}, got {le_metrics["legal_enforcement_recalibration_trigger_capsules"]}')
if le_metrics['legal_enforcement_route_memo_total_bytes_after'] > 93000:
    errors.append(f'legal-enforcement route memos total {le_metrics["legal_enforcement_route_memo_total_bytes_after"]} bytes; expected <=93000 after rev0310 compactness pass')

# Rev0311 labor/care bloat gate: labor/care route memos should delegate repeated failure/trigger taxonomies to cube axes and profiles.
lb_texts=family_texts('labor_care_benefits')
lb_full='\n'.join(t for _,t,_ in lb_texts)
lb_metrics={
    'labor_care_legacy_antipattern_sections_remaining': len(re.findall(r'^## Anti-patterns$', lb_full, re.M)),
    'labor_care_legacy_antipattern_definition_sections_remaining': len(re.findall(r'^## Anti-pattern definitions$', lb_full, re.M)),
    'labor_care_legacy_change_trigger_sections_remaining': len(re.findall(r'^## What would change the recommendation$', lb_full, re.M)),
    'labor_care_failure_mode_capsules': len(re.findall(r'^## Failure-mode capsule$', lb_full, re.M)),
    'labor_care_recalibration_trigger_capsules': len(re.findall(r'^## Recalibration trigger capsule$', lb_full, re.M)),
    'labor_care_accountability_capsules': len(re.findall(r'^## Accountability capsule$', lb_full, re.M)),
    'labor_care_route_memo_total_bytes_after': sum(size for _,_,size in lb_texts),
}
for k,v in lb_metrics.items():
    if metrics.get(k) != v:
        errors.append(f'labor/care prose metric {k} stale: expected {v}, got {metrics.get(k)!r}')
if lb_metrics['labor_care_legacy_antipattern_sections_remaining'] != 0:
    errors.append('labor/care route memos must use Failure-mode capsule, not legacy Anti-patterns sections')
if lb_metrics['labor_care_legacy_antipattern_definition_sections_remaining'] != 0:
    errors.append('labor/care route memos must use Failure-mode capsule, not legacy Anti-pattern definitions sections')
if lb_metrics['labor_care_legacy_change_trigger_sections_remaining'] != 0:
    errors.append('labor/care route memos must use Recalibration trigger capsule, not legacy change-trigger sections')
if lb_metrics['labor_care_accountability_capsules'] != len(lb_texts):
    errors.append(f'every labor/care route memo needs one accountability capsule: expected {len(lb_texts)}, got {lb_metrics["labor_care_accountability_capsules"]}')
if lb_metrics['labor_care_failure_mode_capsules'] != len(lb_texts):
    errors.append(f'every labor/care route memo needs one Failure-mode capsule: expected {len(lb_texts)}, got {lb_metrics["labor_care_failure_mode_capsules"]}')
if lb_metrics['labor_care_recalibration_trigger_capsules'] != len(lb_texts):
    errors.append(f'every labor/care route memo needs one Recalibration trigger capsule: expected {len(lb_texts)}, got {lb_metrics["labor_care_recalibration_trigger_capsules"]}')
if lb_metrics['labor_care_route_memo_total_bytes_after'] > 80000:
    errors.append(f'labor/care route memos total {lb_metrics["labor_care_route_memo_total_bytes_after"]} bytes; expected <=80000 after rev0311 compactness pass')

# Rev0312 environment/climate bloat gate: environment route memos should delegate repeated failure/trigger taxonomies to cube axes and profiles.
env_texts=family_texts('environment_climate_commons')
env_full='\n'.join(t for _,t,_ in env_texts)
env_metrics={
    'environment_legacy_antipattern_sections_remaining': len(re.findall(r'^## Anti-patterns$', env_full, re.M)),
    'environment_legacy_antipattern_definition_sections_remaining': len(re.findall(r'^## Anti-pattern definitions$', env_full, re.M)),
    'environment_legacy_change_trigger_sections_remaining': len(re.findall(r'^## What would change the recommendation$', env_full, re.M)),
    'environment_failure_mode_capsules': len(re.findall(r'^## Failure-mode capsule$', env_full, re.M)),
    'environment_recalibration_trigger_capsules': len(re.findall(r'^## Recalibration trigger capsule$', env_full, re.M)),
    'environment_accountability_capsules': len(re.findall(r'^## Accountability capsule$', env_full, re.M)),
    'environment_route_memo_total_bytes_after': sum(size for _,_,size in env_texts),
}
for k,v in env_metrics.items():
    if metrics.get(k) != v:
        errors.append(f'environment/climate prose metric {k} stale: expected {v}, got {metrics.get(k)!r}')
if env_metrics['environment_legacy_antipattern_sections_remaining'] != 0:
    errors.append('environment/climate route memos must use Failure-mode capsule, not legacy Anti-patterns sections')
if env_metrics['environment_legacy_antipattern_definition_sections_remaining'] != 0:
    errors.append('environment/climate route memos must use Failure-mode capsule, not legacy Anti-pattern definitions sections')
if env_metrics['environment_legacy_change_trigger_sections_remaining'] != 0:
    errors.append('environment/climate route memos must use Recalibration trigger capsule, not legacy change-trigger sections')
if env_metrics['environment_accountability_capsules'] != len(env_texts):
    errors.append(f'every environment/climate route memo needs one accountability capsule: expected {len(env_texts)}, got {env_metrics["environment_accountability_capsules"]}')
if env_metrics['environment_failure_mode_capsules'] != len(env_texts):
    errors.append(f'every environment/climate route memo needs one Failure-mode capsule: expected {len(env_texts)}, got {env_metrics["environment_failure_mode_capsules"]}')
if env_metrics['environment_recalibration_trigger_capsules'] != len(env_texts):
    errors.append(f'every environment/climate route memo needs one Recalibration trigger capsule: expected {len(env_texts)}, got {env_metrics["environment_recalibration_trigger_capsules"]}')
if env_metrics['environment_route_memo_total_bytes_after'] > 51500:
    errors.append(f'environment/climate route memos total {env_metrics["environment_route_memo_total_bytes_after"]} bytes; expected <=51500 after rev0312 compactness pass')


# Rev0313 financial-system bloat gate: financial route memos should delegate guarantee/reserve/de-risking/fiscal/priority failure taxonomies to cube axes and profiles.
fs_texts=family_texts('financial_system_risk')
fs_full='\n'.join(t for _,t,_ in fs_texts)
fs_metrics={
    'financial_system_legacy_antipattern_sections_remaining': len(re.findall(r'^## Anti-patterns$', fs_full, re.M)),
    'financial_system_legacy_antipattern_definition_sections_remaining': len(re.findall(r'^## Anti-pattern definitions$', fs_full, re.M)),
    'financial_system_legacy_three_antipatterns_sections_remaining': len(re.findall(r'^## Three anti-patterns$', fs_full, re.M)),
    'financial_system_legacy_change_trigger_sections_remaining': len(re.findall(r'^## What would change the recommendation$', fs_full, re.M)),
    'financial_system_failure_mode_capsules': len(re.findall(r'^## Failure-mode capsule$', fs_full, re.M)),
    'financial_system_recalibration_trigger_capsules': len(re.findall(r'^## Recalibration trigger capsule$', fs_full, re.M)),
    'financial_system_accountability_capsules': len(re.findall(r'^## Accountability capsule$', fs_full, re.M)),
    'financial_system_route_memo_total_bytes_after': sum(size for _,_,size in fs_texts),
}
for k,v in fs_metrics.items():
    if metrics.get(k) != v:
        errors.append(f'financial-system prose metric {k} stale: expected {v}, got {metrics.get(k)!r}')
if fs_metrics['financial_system_legacy_antipattern_sections_remaining'] != 0:
    errors.append('financial-system route memos must use Failure-mode capsule, not legacy Anti-patterns sections')
if fs_metrics['financial_system_legacy_antipattern_definition_sections_remaining'] != 0:
    errors.append('financial-system route memos must use Failure-mode capsule, not legacy Anti-pattern definitions sections')
if fs_metrics['financial_system_legacy_three_antipatterns_sections_remaining'] != 0:
    errors.append('financial-system route memos must use Failure-mode capsule, not legacy Three anti-patterns sections')
if fs_metrics['financial_system_legacy_change_trigger_sections_remaining'] != 0:
    errors.append('financial-system route memos must use Recalibration trigger capsule, not legacy change-trigger sections')
if fs_metrics['financial_system_accountability_capsules'] != len(fs_texts):
    errors.append(f'every financial-system route memo needs one accountability capsule: expected {len(fs_texts)}, got {fs_metrics["financial_system_accountability_capsules"]}')
if fs_metrics['financial_system_failure_mode_capsules'] != len(fs_texts):
    errors.append(f'every financial-system route memo needs one Failure-mode capsule: expected {len(fs_texts)}, got {fs_metrics["financial_system_failure_mode_capsules"]}')
if fs_metrics['financial_system_recalibration_trigger_capsules'] != len(fs_texts):
    errors.append(f'every financial-system route memo needs one Recalibration trigger capsule: expected {len(fs_texts)}, got {fs_metrics["financial_system_recalibration_trigger_capsules"]}')
if fs_metrics['financial_system_route_memo_total_bytes_after'] > 47000:
    errors.append(f'financial-system route memos total {fs_metrics["financial_system_route_memo_total_bytes_after"]} bytes; expected <=47000 after rev0313 compactness pass')


# Rev0314 wealth/property and procurement bloat gate: these route memos should delegate failure and reopening taxonomies to cube axes and profiles.
wp_texts=family_texts('wealth_property_rent')
wp_full='\n'.join(t for _,t,_ in wp_texts)
wp_metrics={
    'wealth_property_legacy_antipattern_sections_remaining': len(re.findall(r'^## Anti-patterns$', wp_full, re.M)),
    'wealth_property_legacy_antipattern_definition_sections_remaining': len(re.findall(r'^## Anti-pattern definitions$', wp_full, re.M)),
    'wealth_property_legacy_three_antipatterns_sections_remaining': len(re.findall(r'^## Three anti-patterns$', wp_full, re.M)),
    'wealth_property_legacy_change_trigger_sections_remaining': len(re.findall(r'^## What would change the recommendation$', wp_full, re.M)),
    'wealth_property_failure_mode_capsules': len(re.findall(r'^## Failure-mode capsule$', wp_full, re.M)),
    'wealth_property_recalibration_trigger_capsules': len(re.findall(r'^## Recalibration trigger capsule$', wp_full, re.M)),
    'wealth_property_accountability_capsules': len(re.findall(r'^## Accountability capsule$', wp_full, re.M)),
    'wealth_property_route_memo_total_bytes_after': sum(size for _,_,size in wp_texts),
}
for k,v in wp_metrics.items():
    if metrics.get(k) != v:
        errors.append(f'wealth/property prose metric {k} stale: expected {v}, got {metrics.get(k)!r}')
if wp_metrics['wealth_property_legacy_antipattern_sections_remaining'] != 0:
    errors.append('wealth/property route memos must use Failure-mode capsule, not legacy Anti-patterns sections')
if wp_metrics['wealth_property_legacy_antipattern_definition_sections_remaining'] != 0:
    errors.append('wealth/property route memos must use Failure-mode capsule, not legacy Anti-pattern definitions sections')
if wp_metrics['wealth_property_legacy_three_antipatterns_sections_remaining'] != 0:
    errors.append('wealth/property route memos must use Failure-mode capsule, not legacy Three anti-patterns sections')
if wp_metrics['wealth_property_legacy_change_trigger_sections_remaining'] != 0:
    errors.append('wealth/property route memos must use Recalibration trigger capsule, not legacy change-trigger sections')
if wp_metrics['wealth_property_accountability_capsules'] != len(wp_texts):
    errors.append(f'every wealth/property route memo needs one accountability capsule: expected {len(wp_texts)}, got {wp_metrics["wealth_property_accountability_capsules"]}')
if wp_metrics['wealth_property_failure_mode_capsules'] != len(wp_texts):
    errors.append(f'every wealth/property route memo needs one Failure-mode capsule: expected {len(wp_texts)}, got {wp_metrics["wealth_property_failure_mode_capsules"]}')
if wp_metrics['wealth_property_recalibration_trigger_capsules'] != len(wp_texts):
    errors.append(f'every wealth/property route memo needs one Recalibration trigger capsule: expected {len(wp_texts)}, got {wp_metrics["wealth_property_recalibration_trigger_capsules"]}')
if wp_metrics['wealth_property_route_memo_total_bytes_after'] > 45500:
    errors.append(f'wealth/property route memos total {wp_metrics["wealth_property_route_memo_total_bytes_after"]} bytes; expected <=45500 after rev0314 compactness pass')

pr_texts=family_texts('public_procurement_industrial_policy')
pr_full='\n'.join(t for _,t,_ in pr_texts)
pr_metrics={
    'procurement_legacy_antipattern_sections_remaining': len(re.findall(r'^## Anti-patterns$', pr_full, re.M)),
    'procurement_legacy_antipattern_definition_sections_remaining': len(re.findall(r'^## Anti-pattern definitions$', pr_full, re.M)),
    'procurement_legacy_three_antipatterns_sections_remaining': len(re.findall(r'^## Three anti-patterns$', pr_full, re.M)),
    'procurement_legacy_change_trigger_sections_remaining': len(re.findall(r'^## What would change the recommendation$', pr_full, re.M)),
    'procurement_failure_mode_capsules': len(re.findall(r'^## Failure-mode capsule$', pr_full, re.M)),
    'procurement_recalibration_trigger_capsules': len(re.findall(r'^## Recalibration trigger capsule$', pr_full, re.M)),
    'procurement_accountability_capsules': len(re.findall(r'^## Accountability capsule$', pr_full, re.M)),
    'procurement_route_memo_total_bytes_after': sum(size for _,_,size in pr_texts),
}
for k,v in pr_metrics.items():
    if metrics.get(k) != v:
        errors.append(f'procurement prose metric {k} stale: expected {v}, got {metrics.get(k)!r}')
if pr_metrics['procurement_legacy_antipattern_sections_remaining'] != 0:
    errors.append('procurement route memos must use Failure-mode capsule, not legacy Anti-patterns sections')
if pr_metrics['procurement_legacy_antipattern_definition_sections_remaining'] != 0:
    errors.append('procurement route memos must use Failure-mode capsule, not legacy Anti-pattern definitions sections')
if pr_metrics['procurement_legacy_three_antipatterns_sections_remaining'] != 0:
    errors.append('procurement route memos must use Failure-mode capsule, not legacy Three anti-patterns sections')
if pr_metrics['procurement_legacy_change_trigger_sections_remaining'] != 0:
    errors.append('procurement route memos must use Recalibration trigger capsule, not legacy change-trigger sections')
if pr_metrics['procurement_accountability_capsules'] != len(pr_texts):
    errors.append(f'every procurement route memo needs one accountability capsule: expected {len(pr_texts)}, got {pr_metrics["procurement_accountability_capsules"]}')
if pr_metrics['procurement_failure_mode_capsules'] != len(pr_texts):
    errors.append(f'every procurement route memo needs one Failure-mode capsule: expected {len(pr_texts)}, got {pr_metrics["procurement_failure_mode_capsules"]}')
if pr_metrics['procurement_recalibration_trigger_capsules'] != len(pr_texts):
    errors.append(f'every procurement route memo needs one Recalibration trigger capsule: expected {len(pr_texts)}, got {pr_metrics["procurement_recalibration_trigger_capsules"]}')
if pr_metrics['procurement_route_memo_total_bytes_after'] > 26000:
    errors.append(f'procurement route memos total {pr_metrics["procurement_route_memo_total_bytes_after"]} bytes; expected <=26000 after rev0314 compactness pass')

report_rel=cube.get('prose_bloat_audit_report_path')
if not report_rel or not (root/report_rel).exists():
    errors.append('cube-index.json prose_bloat_audit_report_path must point to an existing report')
elif version not in (root/report_rel).read_text(encoding='utf-8')[:200]:
    errors.append('prose-bloat audit report opening must name the active revision')
if errors:
    raise SystemExit('\n'.join(errors))
print('prose bloat audit ok')
