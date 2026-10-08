import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADAPTER_DIR = ROOT / 'examples' / 'sector-adapters'
PROFILE_DIR = ROOT / 'examples' / 'redaction-profiles'
SERVICE_DIR = ROOT / 'examples' / 'service-records'

AA_ORDER = {f'AA{i}': i for i in range(7)}
M_ORDER = {f'M{i}': i for i in range(4)}
REQUIRED = [
    'adapter_id', 'sector_family', 'trigger_terms', 'required_owner_fields',
    'minimum_action_ceiling', 'maximum_default_memory', 'required_public_redaction_profiles',
    'default_redaction_profile', 'extra_public_notice_requirements', 'hard_stop_conditions',
    'renewal_or_evidence_overrides', 'record_separation_rules'
]

def fail(errors, path, msg):
    errors.append(f'{path}: {msg}')

def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))

profile_ids = {load_json(p)['profile_id'] for p in PROFILE_DIR.glob('*.json')}
adapter_paths = sorted(ADAPTER_DIR.glob('*.json'))
if not adapter_paths:
    raise SystemExit('no sector adapters found')

errors=[]
adapters={}
for path in adapter_paths:
    rel=path.relative_to(ROOT).as_posix()
    adapter=load_json(path)
    for field in REQUIRED:
        if field not in adapter or adapter[field] in ('', [], None):
            fail(errors, rel, f'missing or empty {field}')
    aid=adapter.get('adapter_id','')
    if not aid.startswith('ADAPT-'):
        fail(errors, rel, 'adapter_id must start with ADAPT-')
    if aid in adapters:
        fail(errors, rel, f'duplicate adapter_id {aid}')
    adapters[aid]=adapter
    if adapter.get('minimum_action_ceiling') not in AA_ORDER:
        fail(errors, rel, 'minimum_action_ceiling must be AA0-AA6')
    if adapter.get('maximum_default_memory') not in M_ORDER:
        fail(errors, rel, 'maximum_default_memory must be M0-M3')
    profile_refs=set(adapter.get('required_public_redaction_profiles',[])+[adapter.get('default_redaction_profile','')])
    bad=sorted(profile_refs-profile_ids)
    if bad:
        fail(errors, rel, 'undefined redaction profiles: '+', '.join(bad))
    if adapter.get('default_redaction_profile') not in adapter.get('required_public_redaction_profiles',[]):
        fail(errors, rel, 'default_redaction_profile must be required_public_redaction_profiles')

# Trigger checks against service records.
def norm(value):
    return str(value).lower().replace('-', '_').replace(' ', '_')

def has_any(values, terms):
    vals={norm(v) for v in values}
    terms={norm(t) for t in terms}
    return bool(vals & terms)

for path in sorted(SERVICE_DIR.glob('*.json')):
    rel=path.relative_to(ROOT).as_posix()
    record=load_json(path)
    overlay=record.get('publication_and_adapters', {})
    refs=set(overlay.get('sector_adapter_ids', []))
    bad=sorted(refs-set(adapters))
    if bad:
        fail(errors, rel, 'undefined sector adapters: '+', '.join(bad))
    sector=record.get('use_case',{}).get('sector',[])
    ages=record.get('use_case',{}).get('age_bands',[])
    stakes=record.get('use_case',{}).get('highest_stakes_touched',[])
    memory=record.get('memory',{}).get('max_memory_class','')
    support_owner=record.get('accessibility_and_protected_support',{}).get('protected_route_owner','').lower()
    triggers=[]
    if has_any(ages+sector, ['primary','secondary','minor','k12','k-12']):
        triggers.append('ADAPT-K12-MINORS')
    if has_any(sector+stakes, ['higher_ed','postsecondary','course_credit','credit']):
        triggers.append('ADAPT-HIGHER-ED-CREDIT')
    if has_any(sector+stakes, ['public_workforce','workforce','public_benefit','eligibility','recognition']):
        triggers.append('ADAPT-PUBLIC-WORKFORCE-RECOGNITION')
    if has_any(stakes+[memory], ['accessibility','accommodation','disability','language_access','protected','m3']):
        triggers.append('ADAPT-ACCESSIBILITY-PROTECTED')
    missing=sorted(set(triggers)-refs)
    if missing:
        fail(errors, rel, 'missing required sector adapters: '+', '.join(missing))

if errors:
    raise SystemExit('sector adapter validation errors:\n'+'\n'.join(errors))
print(f'check_sector_adapters: OK ({len(adapters)} adapters)')
