import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
legacy_fixture_path = ROOT / 'examples/negative-test-fixture-sealed-annex-laundering.json'
fixture_dir = ROOT / 'fixtures' / 'negative-tests'
report_path = ROOT / 'examples/fixture-run-report-negative-suite.json'
suite_path = ROOT / 'examples/fixture-suite-profile-red-team-v1.json'

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

fixture_paths = [legacy_fixture_path] + sorted(fixture_dir.glob('*.json'))
fixtures = {load(path).get('fixture_id'): (path, load(path)) for path in fixture_paths}
if None in fixtures:
    raise SystemExit('one fixture lacks fixture_id')
if len(fixtures) != len(fixture_paths):
    raise SystemExit('duplicate fixture_id in fixture corpus')

report = load(report_path)
suite = load(suite_path)

if Draft202012Validator is not None:
    schema_map = {
        'negative-test-fixture.schema.json': fixture_paths,
        'fixture-run-report.schema.json': [report_path],
        'fixture-suite-profile.schema.json': [suite_path],
    }
    for schema_name, data_paths in schema_map.items():
        schema = load(ROOT / 'schemas' / schema_name)
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        for path in data_paths:
            data = load(path)
            errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
            if errors:
                raise SystemExit(f'{path.relative_to(ROOT)} fails {schema_name}: {errors[0].message}')

# Suite references must resolve exactly.
suite_ids = []
for entry in suite.get('fixtures', []):
    fid = entry.get('fixture_id')
    suite_ids.append(fid)
    if fid not in fixtures:
        raise SystemExit(f'suite references missing fixture_id: {fid}')
    path = ROOT / entry.get('path', '')
    if not path.exists():
        raise SystemExit(f'suite references missing fixture path: {entry.get("path")}')
    actual = load(path).get('fixture_id')
    if actual != fid:
        raise SystemExit(f'suite fixture path/id mismatch: {entry.get("path")} has {actual}, expected {fid}')

if len(suite_ids) < 5:
    raise SystemExit('fixture suite too small for core corpus')

# Report should reference known fixtures and exactly cover the suite profile.
report_entries = report.get('fixtures_run', [])
report_ids = [f.get('fixture_id') for f in report_entries]
if not report_ids:
    raise SystemExit('fixture-run report has no fixtures_run')
if None in report_ids:
    raise SystemExit('fixture-run report has an entry without fixture_id')
if len(report_ids) != len(set(report_ids)):
    dupes = sorted({fid for fid in report_ids if report_ids.count(fid) > 1})
    raise SystemExit(f'fixture-run report has duplicate fixture ids: {dupes}')
unknown = sorted(fid for fid in report_ids if fid not in fixtures)
if unknown:
    raise SystemExit(f'fixture-run report references unknown fixtures: {unknown}')
if len(suite_ids) != len(set(suite_ids)):
    dupes = sorted({fid for fid in suite_ids if suite_ids.count(fid) > 1})
    raise SystemExit(f'fixture suite has duplicate fixture ids: {dupes}')
missing_from_report = sorted(set(suite_ids) - set(report_ids))
extra_in_report = sorted(set(report_ids) - set(suite_ids))
if missing_from_report or extra_in_report:
    raise SystemExit(f'fixture-run report/suite mismatch: missing={missing_from_report}; extra={extra_in_report}')

blocking_results = [f for f in report.get('fixtures_run', []) if f.get('result') == 'blocking-failure']
for item in blocking_results:
    if not item.get('expected_blocking_failures'):
        raise SystemExit('blocking fixture result lacks expected blocking failures')
if blocking_results and report.get('reliance_effect') not in {'blocked', 'stayed', 'downgraded', 'invalidated'}:
    raise SystemExit('blocking fixture did not produce a blocking or downgrading reliance effect')
if not report.get('regression_actions'):
    raise SystemExit('fixture-run report lacks regression actions')

# Every high-critical suite fixture must carry regression duty.
for fid in suite_ids:
    data = fixtures[fid][1]
    if data.get('severity') in {'high', 'critical'} and not data.get('regression', {}).get('required'):
        raise SystemExit(f'high/critical fixture lacks regression duty: {fid}')

print('run_fixture_examples: OK')
