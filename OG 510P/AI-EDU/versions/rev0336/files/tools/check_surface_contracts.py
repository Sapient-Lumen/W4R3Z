import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_PATH = ROOT / 'CUBE_SURFACE_CONTRACTS.json'
SURFACES_PATH = ROOT / 'SURFACES.json'
RECEIPT_PATH = ROOT / 'REVISION_RECEIPT.json'


def fail(errors, message):
    errors.append(message)


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


errors = []
if not CONTRACTS_PATH.exists():
    raise SystemExit('CUBE_SURFACE_CONTRACTS.json missing')

contracts = load(CONTRACTS_PATH)
surfaces_payload = load(SURFACES_PATH)
receipt = load(RECEIPT_PATH)
rows = {row['path']: row for row in surfaces_payload.get('surfaces', [])}

required_top = ['registry_id', 'revision', 'purpose', 'source_of_truth_rule', 'coverage_rules', 'contracts']
for field in required_top:
    if field not in contracts:
        fail(errors, f'missing top-level field: {field}')

if contracts.get('revision') != receipt.get('revision'):
    fail(errors, f"revision {contracts.get('revision')} does not match receipt {receipt.get('revision')}")
if not str(contracts.get('registry_id', '')).startswith('SCON-'):
    fail(errors, 'registry_id must start SCON-')
if 'SURFACES.json' not in contracts.get('source_of_truth_rule', ''):
    fail(errors, 'source_of_truth_rule must name SURFACES.json')
if 'FT-0181' not in ' '.join(contracts.get('coverage_rules', [])):
    fail(errors, 'coverage_rules must keep FT-0181 boundary visible')

seen = []
for idx, contract in enumerate(contracts.get('contracts', [])):
    for field in [
        'path', 'contract_class', 'expected_type', 'expected_lifecycle', 'expected_owner',
        'expected_authority', 'expected_portability', 'required_evidence_levels',
        'required_tags', 'forbidden_tags', 'required_quality', 'closure_boundary'
    ]:
        if field not in contract:
            fail(errors, f'contract {idx} missing field: {field}')
    if any(field not in contract for field in ['path', 'contract_class', 'closure_boundary']):
        continue
    path = contract['path']
    seen.append(path)
    if path not in rows:
        fail(errors, f'contract path not present in SURFACES.json: {path}')
        continue
    if not (ROOT / path).exists():
        fail(errors, f'contract path missing on disk: {path}')
        continue
    row = rows[path]
    exact_fields = {
        'type': 'expected_type',
        'lifecycle': 'expected_lifecycle',
        'owner': 'expected_owner',
        'authority': 'expected_authority',
        'portability': 'expected_portability',
        'classification_quality': 'required_quality',
    }
    for row_field, contract_field in exact_fields.items():
        expected = contract.get(contract_field)
        if expected and row.get(row_field) != expected:
            fail(errors, f'{path}: {row_field} expected {expected}, found {row.get(row_field)}')
    for value in contract.get('required_evidence_levels', []):
        if value not in row.get('evidence_level', []):
            fail(errors, f'{path}: missing evidence level {value}')
    for value in contract.get('required_tags', []):
        if value not in row.get('tags', []):
            fail(errors, f'{path}: missing tag {value}')
    for value in contract.get('forbidden_tags', []):
        if value in row.get('tags', []):
            fail(errors, f'{path}: forbidden tag present: {value}')
    boundary = contract.get('closure_boundary', '').lower()
    if 'does not close ft-0181' not in boundary and 'do not close ft-0181' not in boundary:
        fail(errors, f'{path}: closure_boundary must say it does not close FT-0181')
    if contract.get('contract_class') in {'meta_registry', 'meta_audit', 'reentry'}:
        if 'branch-archive' in row.get('tags', []):
            fail(errors, f'{path}: meta/reentry contract cannot carry branch-archive tag')
        if row.get('lifecycle') == 'branch_archive':
            fail(errors, f'{path}: meta/reentry contract cannot have branch_archive lifecycle')

if len(seen) != len(set(seen)):
    dupes = sorted(path for path in set(seen) if seen.count(path) > 1)
    fail(errors, 'duplicate surface contracts: ' + ', '.join(dupes))

if len(contracts.get('contracts', [])) < 25:
    fail(errors, 'surface contracts should cover at least 25 canonical surfaces')

if errors:
    raise SystemExit('surface contract validation errors:\n' + '\n'.join(errors))

classes = sorted({c.get('contract_class') for c in contracts.get('contracts', [])})
print(f'check_surface_contracts: OK ({len(contracts.get("contracts", []))} contracts, classes {", ".join(classes)})')
