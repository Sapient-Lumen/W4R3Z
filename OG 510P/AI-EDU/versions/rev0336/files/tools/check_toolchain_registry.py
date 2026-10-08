import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / 'CUBE_TOOLCHAIN_REGISTRY.json'
RECEIPT_PATH = ROOT / 'REVISION_RECEIPT.json'
STATES = {'required', 'generated', 'utility'}
REQUIRED_LANES = {'full-release', 'fast-changed', 'release-controls', 'owner-reply-field'}


def fail(errors, msg):
    errors.append(msg)


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


errors = []
if not REGISTRY_PATH.exists():
    raise SystemExit('CUBE_TOOLCHAIN_REGISTRY.json missing')

registry = load_json(REGISTRY_PATH)
receipt = load_json(RECEIPT_PATH)

required_top = [
    'registry_id', 'revision', 'purpose', 'source_of_truth_rule',
    'lint_order', 'lint_lanes', 'generated_artifacts', 'utility_tools', 'coverage_rules'
]
for field in required_top:
    if field not in registry:
        fail(errors, f'missing {field}')
if errors:
    raise SystemExit('toolchain registry validation errors:\n' + '\n'.join(errors))

if not str(registry['registry_id']).startswith('TCR-'):
    fail(errors, 'registry_id must start TCR-')
if registry['revision'] != receipt['revision']:
    fail(errors, f'revision {registry["revision"]} does not match receipt {receipt["revision"]}')
if 'run_lint_suite.py' not in registry.get('source_of_truth_rule', ''):
    fail(errors, 'source_of_truth_rule must name run_lint_suite.py')
if 'hardcoded' not in registry.get('source_of_truth_rule', '').lower():
    fail(errors, 'source_of_truth_rule must explain hardcoded-list avoidance')
if 'lane' not in registry.get('source_of_truth_rule', '').lower():
    fail(errors, 'source_of_truth_rule must mention lint lanes')

lint_entries = registry.get('lint_order', [])
if not isinstance(lint_entries, list) or not lint_entries:
    fail(errors, 'lint_order must be a non-empty list')
orders = []
paths = []
for row in lint_entries:
    row_errors = False
    for field in ['order', 'path', 'role']:
        if field not in row:
            fail(errors, f'lint row missing {field}: {row}')
            row_errors = True
    if row_errors:
        continue
    orders.append(row['order'])
    path = row['path']
    paths.append(path)
    if not path.startswith('tools/') or not path.endswith('.py'):
        fail(errors, f'lint path must be tools/*.py: {path}')
    if not (ROOT / path).exists():
        fail(errors, f'lint path missing: {path}')
    if Path(path).name == 'run_lint_suite.py':
        fail(errors, 'run_lint_suite.py must not invoke itself')
    if not row.get('role'):
        fail(errors, f'lint row missing role text: {path}')

if sorted(orders) != list(range(1, len(orders) + 1)):
    fail(errors, 'lint_order orders must be contiguous starting at 1')
if len(paths) != len(set(paths)):
    dupes = sorted(p for p in set(paths) if paths.count(p) > 1)
    fail(errors, 'duplicate lint paths: ' + ', '.join(dupes))
path_set = set(paths)

lint_names = {Path(p).name for p in paths}
actual_tools = sorted(p for p in (ROOT / 'tools').glob('*.py'))
actual_tool_rels = {p.relative_to(ROOT).as_posix() for p in actual_tools}
check_tools = {p.relative_to(ROOT).as_posix() for p in actual_tools if p.name.startswith('check_')}
missing_checks = sorted(check_tools - path_set)
if missing_checks:
    fail(errors, 'check_*.py tools missing from lint_order: ' + ', '.join(missing_checks))

lanes = registry.get('lint_lanes', [])
if not isinstance(lanes, list) or not lanes:
    fail(errors, 'lint_lanes must be a non-empty list')
lane_ids = []
for lane in lanes:
    for field in ['lane_id', 'description', 'selection']:
        if field not in lane:
            fail(errors, f'lint lane missing {field}: {lane}')
    if any(field not in lane for field in ['lane_id', 'description', 'selection']):
        continue
    lane_id = lane['lane_id']
    lane_ids.append(lane_id)
    selection = lane['selection']
    if selection not in {'all', 'paths'}:
        fail(errors, f'lint lane {lane_id} has invalid selection')
        continue
    lane_paths = lane.get('paths', [])
    if selection == 'all':
        if lane_id != 'full-release':
            fail(errors, f'only full-release may use selection=all: {lane_id}')
        if lane_paths:
            fail(errors, f'all lane should not list explicit paths: {lane_id}')
    if selection == 'paths':
        if not lane_paths:
            fail(errors, f'paths lane must list at least one path: {lane_id}')
        if len(lane_paths) != len(set(lane_paths)):
            fail(errors, f'lint lane has duplicate paths: {lane_id}')
        for path in lane_paths:
            if path not in path_set:
                fail(errors, f'lint lane {lane_id} references path outside lint_order: {path}')
            if Path(path).name == 'run_lint_suite.py':
                fail(errors, f'lint lane {lane_id} must not invoke run_lint_suite.py')
if len(lane_ids) != len(set(lane_ids)):
    dupes = sorted(l for l in set(lane_ids) if lane_ids.count(l) > 1)
    fail(errors, 'duplicate lint lane ids: ' + ', '.join(dupes))
missing_lanes = sorted(REQUIRED_LANES - set(lane_ids))
if missing_lanes:
    fail(errors, 'missing required lint lanes: ' + ', '.join(missing_lanes))
for required in ['tools/check_toolchain_registry.py', 'tools/check_json.py']:
    for lane_id in ['fast-changed', 'full-release']:
        lane = next((row for row in lanes if row.get('lane_id') == lane_id), {})
        if lane.get('selection') == 'paths' and required not in lane.get('paths', []):
            fail(errors, f'{lane_id} lane must include {required}')
owner_lane = next((row for row in lanes if row.get('lane_id') == 'owner-reply-field'), {})
if owner_lane.get('selection') == 'paths':
    for required in ['tools/check_ft0181_owner_request_packet.py', 'tools/check_owner_reply_intake_bundle.py', 'tools/check_owner_reply_workbench_seed.py']:
        if required not in owner_lane.get('paths', []):
            fail(errors, f'owner-reply-field lane must include {required}')

utility_paths = []
for row in registry.get('utility_tools', []):
    row_errors = False
    for field in ['path', 'role']:
        if field not in row:
            fail(errors, f'utility row missing {field}: {row}')
            row_errors = True
    if row_errors:
        continue
    path = row['path']
    utility_paths.append(path)
    if not path.startswith('tools/') or not path.endswith('.py'):
        fail(errors, f'utility path must be tools/*.py: {path}')
    if not (ROOT / path).exists():
        fail(errors, f'utility path missing: {path}')
    if Path(path).name.startswith('check_'):
        fail(errors, f'check tool must be linted, not utility-only: {path}')
    if path in path_set:
        fail(errors, f'tool cannot be both lint and utility: {path}')

covered_tools = path_set | set(utility_paths)
missing_tools = sorted(actual_tool_rels - covered_tools)
extra_tools = sorted(covered_tools - actual_tool_rels)
if missing_tools:
    fail(errors, 'tools not covered by lint_order or utility_tools: ' + ', '.join(missing_tools))
if extra_tools:
    fail(errors, 'toolchain registry lists missing tools: ' + ', '.join(extra_tools))

for artifact in registry.get('generated_artifacts', []):
    row_errors = False
    for field in ['path', 'generated_by']:
        if field not in artifact:
            fail(errors, f'generated artifact row missing {field}: {artifact}')
            row_errors = True
    if row_errors:
        continue
    apath = ROOT / artifact['path']
    if not apath.exists():
        fail(errors, f'generated artifact missing: {artifact["path"]}')
    generator = artifact['generated_by']
    if generator.startswith('tools/') and not (ROOT / generator).exists():
        fail(errors, f'generated_by tool missing: {generator}')
    if generator.startswith('tools/') and Path(generator).name not in lint_names and generator not in utility_paths:
        fail(errors, f'generated_by tool not covered by toolchain registry: {generator}')

coverage = registry.get('coverage_rules', [])
joined_rules = ' '.join(str(x).lower() for x in coverage)
for phrase in ['every check_', 'utility_tools', 'no validator', 'lint_lanes']:
    if phrase not in joined_rules:
        fail(errors, f'coverage_rules must mention {phrase}')

if 'tools/check_toolchain_registry.py' not in path_set:
    fail(errors, 'check_toolchain_registry.py must be in lint_order')

if errors:
    raise SystemExit('toolchain registry validation errors:\n' + '\n'.join(errors))

print(f'check_toolchain_registry: OK ({len(paths)} lint tools, {len(utility_paths)} utility tools, {len(lanes)} lanes)')
