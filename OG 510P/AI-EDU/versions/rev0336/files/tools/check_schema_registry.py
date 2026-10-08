import glob
import json
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, exceptions as jsonschema_exceptions
except Exception as exc:  # pragma: no cover - lint environment guard
    raise SystemExit(
        'schema registry validation requires the jsonschema package: ' + str(exc)
    )

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / 'CUBE_SCHEMA_REGISTRY.json'
RECEIPT_PATH = ROOT / 'REVISION_RECEIPT.json'
TOOLCHAIN_PATH = ROOT / 'CUBE_TOOLCHAIN_REGISTRY.json'
SURFACES_PATH = ROOT / 'SURFACES.json'
STATES = {'active', 'generated', 'release-control', 'root-control'}
MAX_SCHEMA_INSTANCE_ERRORS = 80


def fail(errors, msg):
    errors.append(msg)


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def format_error_path(error) -> str:
    parts = [str(part) for part in error.absolute_path]
    return '/' + '/'.join(parts) if parts else '<root>'


errors = []
if not REGISTRY_PATH.exists():
    raise SystemExit('CUBE_SCHEMA_REGISTRY.json missing')

registry = load_json(REGISTRY_PATH)
receipt = load_json(RECEIPT_PATH)
toolchain = load_json(TOOLCHAIN_PATH)
surfaces = load_json(SURFACES_PATH)

required_top = [
    'registry_id', 'revision', 'purpose', 'source_of_truth_rule',
    'coverage_rules', 'schemas'
]
for field in required_top:
    if field not in registry:
        fail(errors, f'missing {field}')
if errors:
    raise SystemExit('schema registry validation errors:\n' + '\n'.join(errors))

if not str(registry['registry_id']).startswith('SCR-'):
    fail(errors, 'registry_id must start SCR-')
if registry['revision'] != receipt['revision']:
    fail(errors, f'revision {registry["revision"]} does not match receipt {receipt["revision"]}')
if 'schemas/*.schema.json' not in registry.get('source_of_truth_rule', ''):
    fail(errors, 'source_of_truth_rule must name schemas/*.schema.json coverage')
if 'CUBE_TOOLCHAIN_REGISTRY.json' not in registry.get('source_of_truth_rule', ''):
    fail(errors, 'source_of_truth_rule must name CUBE_TOOLCHAIN_REGISTRY.json')

rules_text = ' '.join(registry.get('coverage_rules', [])).lower()
for phrase in ['ft-0181', 'does not close', 'examples/**/*.json', 'validator']:
    if phrase not in rules_text:
        fail(errors, f'coverage_rules missing phrase: {phrase}')
for phrase in ['validate', 'schema']:
    if phrase not in rules_text:
        fail(errors, f'coverage_rules missing schema-conformance phrase: {phrase}')

entries = registry.get('schemas', [])
if not isinstance(entries, list) or not entries:
    fail(errors, 'schemas must be a non-empty list')

lint_paths = {row.get('path') for row in toolchain.get('lint_order', [])}
surface_paths = {row.get('path') for row in surfaces.get('surfaces', [])}
actual_schema_paths = {rel(p) for p in (ROOT / 'schemas').glob('*.schema.json')}
registered_schema_paths = []
schema_ids = []
covered_examples = {}
covered_instances = {}
validated_instances = 0
schema_instance_errors = []

for row in entries:
    for field in ['schema_id', 'schema_path', 'instance_globs', 'validator', 'doc_surface', 'status', 'closure_boundary']:
        if field not in row:
            fail(errors, f'schema row missing {field}: {row}')
    if any(field not in row for field in ['schema_id', 'schema_path', 'instance_globs', 'validator', 'doc_surface', 'status', 'closure_boundary']):
        continue
    schema_ids.append(row['schema_id'])
    spath = row['schema_path']
    registered_schema_paths.append(spath)
    schema_file = ROOT / spath
    schema = None
    schema_validator = None
    if not spath.startswith('schemas/') or not spath.endswith('.schema.json'):
        fail(errors, f'invalid schema_path: {spath}')
    elif not schema_file.exists():
        fail(errors, f'schema_path missing: {spath}')
    else:
        schema = load_json(schema_file)
        if not schema.get('title'):
            fail(errors, f'schema has no title: {spath}')
        if schema.get('type') != 'object':
            fail(errors, f'schema top-level type should be object: {spath}')
        try:
            Draft202012Validator.check_schema(schema)
            schema_validator = Draft202012Validator(schema)
        except jsonschema_exceptions.SchemaError as exc:
            fail(errors, f'schema is not Draft 2020-12 valid: {spath}: {exc.message}')

    validator = row['validator']
    if validator not in lint_paths:
        fail(errors, f'validator not wired into lint_order: {validator}')
    if not (ROOT / validator).exists():
        fail(errors, f'validator missing: {validator}')

    doc_surface = row['doc_surface']
    if not (ROOT / doc_surface).exists():
        fail(errors, f'doc_surface missing: {doc_surface}')
    if doc_surface.endswith('.md') and doc_surface not in surface_paths:
        fail(errors, f'doc_surface not indexed in SURFACES.json: {doc_surface}')

    if row['status'] not in STATES:
        fail(errors, f'status invalid for {spath}: {row["status"]}')

    boundary = row.get('closure_boundary', '').lower()
    close_ok = 'does not close ft-0181' in boundary or 'do not close ft-0181' in boundary
    prove_ok = 'does not prove' in boundary or 'do not prove' in boundary
    if not close_ok:
        fail(errors, f'closure_boundary for {spath} must say it does not close FT-0181')
    if not prove_ok:
        fail(errors, f'closure_boundary for {spath} must say it does not prove service claims')

    globs = row.get('instance_globs', [])
    if not isinstance(globs, list) or not globs:
        fail(errors, f'instance_globs must be a non-empty list for {spath}')
        continue
    matches = []
    for pattern in globs:
        found = sorted(Path(p) for p in glob.glob(str(ROOT / pattern)))
        if not found:
            fail(errors, f'instance_glob matched no files for {spath}: {pattern}')
        for path in found:
            if path.is_dir():
                continue
            r = rel(path)
            if not r.endswith('.json'):
                fail(errors, f'instance_glob matched non-json file for {spath}: {r}')
            matches.append(r)
            covered_instances.setdefault(r, []).append(spath)
            if r.startswith('examples/'):
                covered_examples.setdefault(r, []).append(spath)
            if schema_validator is not None and r.endswith('.json'):
                instance = load_json(path)
                instance_errors = sorted(schema_validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
                if instance_errors:
                    for error in instance_errors[:5]:
                        schema_instance_errors.append(
                            f'{r} violates {spath} at {format_error_path(error)}: {error.message}'
                        )
                    if len(instance_errors) > 5:
                        schema_instance_errors.append(
                            f'{r} violates {spath}: {len(instance_errors) - 5} additional schema errors omitted'
                        )
                else:
                    validated_instances += 1
    if not matches:
        fail(errors, f'no instances matched for {spath}')

if len(schema_ids) != len(set(schema_ids)):
    dupes = sorted(s for s in set(schema_ids) if schema_ids.count(s) > 1)
    fail(errors, 'duplicate schema_id values: ' + ', '.join(dupes))
if len(registered_schema_paths) != len(set(registered_schema_paths)):
    dupes = sorted(s for s in set(registered_schema_paths) if registered_schema_paths.count(s) > 1)
    fail(errors, 'duplicate schema_path values: ' + ', '.join(dupes))

missing = sorted(actual_schema_paths - set(registered_schema_paths))
extra = sorted(set(registered_schema_paths) - actual_schema_paths)
if missing:
    fail(errors, 'schemas missing from registry: ' + ', '.join(missing))
if extra:
    fail(errors, 'registry names missing schema files: ' + ', '.join(extra))

all_examples = {rel(p) for p in (ROOT / 'examples').rglob('*.json')}
missing_examples = sorted(all_examples - set(covered_examples))
if missing_examples:
    fail(errors, 'examples json missing schema coverage: ' + ', '.join(missing_examples))

dupe_examples = sorted(path for path, owners in covered_examples.items() if len(owners) != 1)
if dupe_examples:
    fail(errors, 'examples json covered by multiple schema rows: ' + ', '.join(dupe_examples))

dupe_instances = sorted(path for path, owners in covered_instances.items() if len(owners) != 1)
if dupe_instances:
    fail(errors, 'instance json covered by multiple schema rows: ' + ', '.join(dupe_instances))

# Root controls with schemas should be explicit, not accidental examples.
for required_root in ['BRANCH_FAMILY_INDEX.json', 'CUBE_TOOLCHAIN_REGISTRY.json', 'CUBE_SCHEMA_REGISTRY.json', 'CUBE_SURFACE_CONTRACTS.json']:
    if required_root not in covered_instances:
        fail(errors, f'root structured control missing schema coverage: {required_root}')

if schema_instance_errors:
    errors.extend(schema_instance_errors[:MAX_SCHEMA_INSTANCE_ERRORS])
    if len(schema_instance_errors) > MAX_SCHEMA_INSTANCE_ERRORS:
        errors.append(f'{len(schema_instance_errors) - MAX_SCHEMA_INSTANCE_ERRORS} additional schema instance errors omitted')

if errors:
    raise SystemExit('schema registry validation errors:\n' + '\n'.join(errors))
print(f'check_schema_registry: OK ({len(entries)} schemas, {len(all_examples)} example instances, {validated_instances} schema-valid instances)')
