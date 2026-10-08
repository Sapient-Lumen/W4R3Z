import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECL_DIR = ROOT / 'examples' / 'synthetic-example-declarations'
SCHEMA_PATH = ROOT / 'schemas' / 'synthetic-example-declaration.schema.json'
SRC = {'SRC0', 'SRC1', 'SRC2', 'SRC3', 'SRC4', 'SRCX'}

receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))


def example_paths():
    paths = []
    for path in (ROOT / 'examples').rglob('*.json'):
        rel = path.relative_to(ROOT).as_posix()
        if '/synthetic-example-declarations/' in rel:
            continue
        paths.append(rel)
    return sorted(paths)


def fail(errors, rel, msg):
    errors.append(f'{rel}: {msg}')


def parse_date(value, errors, rel, field):
    try:
        date.fromisoformat(value)
    except Exception:
        fail(errors, rel, f'{field} must be ISO date')


def validate(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    errors = []
    data = json.loads(path.read_text(encoding='utf-8'))
    required = [
        'declaration_id', 'revision', 'scope', 'source_truth_classes',
        'records', 'blanket_rule', 'promotion_rule', 'last_reviewed'
    ]
    for field in required:
        if field not in data:
            fail(errors, rel, f'missing {field}')
    if errors:
        return errors

    if data['revision'] != receipt['revision']:
        fail(errors, rel, 'revision does not match receipt')
    if not data['declaration_id'].startswith('SED-'):
        fail(errors, rel, 'declaration_id must start SED-')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')
    if set(data.get('source_truth_classes', [])) != SRC:
        fail(errors, rel, 'source_truth_classes must list SRC0, SRC1, SRC2, SRC3, SRC4, SRCX')

    declared = []
    for row in data.get('records', []):
        for field in ['path', 'source_truth_class', 'example_role', 'allowed_use', 'prohibited_claims', 'may_close_ft0181']:
            if field not in row:
                fail(errors, rel, f'record missing {field}')
        if errors:
            continue
        declared.append(row['path'])
        if row['source_truth_class'] not in SRC:
            fail(errors, rel, f'invalid source_truth_class for {row["path"]}')
        if not (ROOT / row['path']).exists():
            fail(errors, rel, f'declared path missing: {row["path"]}')
        if row.get('may_close_ft0181') and row.get('source_truth_class') not in {'SRC2', 'SRC3', 'SRC4'}:
            fail(errors, rel, f'{row["path"]} may_close_ft0181 without SRC2+')
        prohibited = ' '.join(row.get('prohibited_claims', [])).lower()
        if 'effectiveness' not in prohibited and row.get('source_truth_class') in {'SRC0', 'SRC1'}:
            fail(errors, rel, f'{row["path"]} must prohibit effectiveness claims')

    expected = example_paths()
    if sorted(declared) != expected:
        missing = sorted(set(expected) - set(declared))
        extra = sorted(set(declared) - set(expected))
        if missing:
            fail(errors, rel, 'undeclared examples: ' + ', '.join(missing))
        if extra:
            fail(errors, rel, 'declaration lists non-example paths: ' + ', '.join(extra))
    if 'real pilot evidence' not in data.get('blanket_rule', '').lower():
        fail(errors, rel, 'blanket_rule must mention real pilot evidence')
    if 'src2+' not in data.get('promotion_rule', '').lower():
        fail(errors, rel, 'promotion_rule must mention SRC2+')
    return errors


schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU synthetic example source-status declaration':
    raise SystemExit('synthetic example declaration schema title mismatch')

paths = sorted(DECL_DIR.glob('*.json'))
if not paths:
    raise SystemExit('no synthetic example declarations found')

all_errors = []
for path in paths:
    all_errors.extend(validate(path))

if all_errors:
    raise SystemExit('synthetic example declaration validation errors:\n' + '\n'.join(all_errors))
print(f'check_synthetic_example_declarations: OK ({len(paths)} declarations, {len(example_paths())} examples)')
