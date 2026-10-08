import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICE_DIR = ROOT / 'examples' / 'service-records'
ACCEPTANCE_DIR = ROOT / 'examples' / 'real-import-acceptance'
READY_DIR = ROOT / 'examples' / 'import-readiness'

closure_acceptance = []
if ACCEPTANCE_DIR.exists():
    for path in ACCEPTANCE_DIR.glob('*.json'):
        data = json.loads(path.read_text(encoding='utf-8'))
        if data.get('closure_permitted'):
            closure_acceptance.append(data.get('acceptance_id'))

closure_readiness = []
if READY_DIR.exists():
    for path in READY_DIR.glob('*.json'):
        data = json.loads(path.read_text(encoding='utf-8'))
        if data.get('closure_permitted'):
            closure_readiness.append(data.get('manifest_id'))

errors = []
for path in SERVICE_DIR.glob('*.json'):
    rel = path.relative_to(ROOT).as_posix()
    record = json.loads(path.read_text(encoding='utf-8'))
    pub = record.get('publication_and_adapters', {})
    source_status = pub.get('source_record_status')
    import_status = pub.get('real_record_import_status')
    confidence = pub.get('source_record_confidence')
    real_claim = source_status == 'real_pilot_imported' or import_status in {'imported_and_verified', 'imported_needs_review'}
    if real_claim:
        if not closure_acceptance:
            errors.append(f'{rel}: real import claim without closure-ready acceptance packet')
        if not closure_readiness:
            errors.append(f'{rel}: real import claim without closure-ready readiness manifest')
        if confidence not in {'record_owner_verified', 'learner_facing_confirmed'}:
            errors.append(f'{rel}: real import claim requires record_owner_verified or learner_facing_confirmed confidence')
    if source_status in {'realistic_example', 'synthetic_backtest', 'template_only'} and import_status != 'not_applicable_example':
        errors.append(f'{rel}: example/template record must use real_record_import_status=not_applicable_example')
    if source_status == 'realistic_example' and confidence != 'example_only':
        errors.append(f'{rel}: realistic example must use source_record_confidence=example_only')

if errors:
    raise SystemExit('fake real import guard errors:\n' + '\n'.join(errors))
print(f'check_no_fake_real_import: OK ({len(list(SERVICE_DIR.glob("*.json")))} records, {len(closure_acceptance)} closure-ready acceptance packets)')
