import hashlib
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_DIR = ROOT / 'examples' / 'release-audit-manifests'
SCHEMA_PATH = ROOT / 'schemas' / 'release-audit-manifest.schema.json'
STATES = {'RA0', 'RA1', 'RA2', 'RA3', 'RA4', 'RAX'}

receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
ft_items = json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']
live_ft = sorted(item['id'] for item in ft_items if item.get('state') != 'done')


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def count_files(suffix=None):
    count = 0
    for path in ROOT.rglob('*'):
        if path.is_dir() or '__pycache__' in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith('.') or rel.endswith('.zip'):
            continue
        if rel == 'scratch' or rel.startswith('scratch/'):
            continue
        if suffix is None or path.suffix == suffix:
            count += 1
    return count


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
        'manifest_id', 'revision', 'base_revision', 'audit_state',
        'claims_all_followthrough_closed', 'live_followthrough_ids',
        'file_inventory', 'generated_artifacts', 'required_commands',
        'hash_targets', 'excluded_from_hash', 'claims_bit_reproducible_zip',
        'audit_limits', 'last_reviewed'
    ]
    for field in required:
        if field not in data:
            fail(errors, rel, f'missing {field}')
    if errors:
        return errors

    if not data['manifest_id'].startswith('RA-'):
        fail(errors, rel, 'manifest_id must start RA-')
    if data['revision'] != receipt['revision']:
        fail(errors, rel, 'revision does not match receipt')
    if data['audit_state'] not in STATES:
        fail(errors, rel, 'audit_state invalid')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')
    if sorted(data.get('live_followthrough_ids', [])) != live_ft:
        fail(errors, rel, 'live_followthrough_ids do not match queue')
    if live_ft and data.get('claims_all_followthrough_closed'):
        fail(errors, rel, 'cannot claim all followthrough closed while live items remain')
    if data.get('claims_bit_reproducible_zip') is not False:
        fail(errors, rel, 'manifest must not claim bit-for-bit reproducible zip')

    inv = data.get('file_inventory', {})
    expected_counts = {
        'total_tracked_files': count_files(),
        'markdown_files': count_files('.md'),
        'json_files': count_files('.json'),
        'python_tools': len(list((ROOT / 'tools').glob('*.py'))),
    }
    for key, expected in expected_counts.items():
        if inv.get(key) != expected:
            fail(errors, rel, f'file_inventory {key}={inv.get(key)} expected {expected}')

    commands = '\n'.join(data.get('required_commands', []))
    if 'tools/run_lint_suite.py' not in commands:
        fail(errors, rel, 'required_commands must include tools/run_lint_suite.py')
    if 'handoff-release' not in commands:
        fail(errors, rel, 'required_commands must include handoff-release')

    for generated in data.get('generated_artifacts', []):
        if not (ROOT / generated).exists():
            fail(errors, rel, f'generated artifact missing: {generated}')

    if 'RELEASE-MANIFEST.json' not in data.get('excluded_from_hash', []):
        fail(errors, rel, 'RELEASE-MANIFEST.json should be excluded from audit hashes')

    for target in data.get('hash_targets', []):
        tpath = ROOT / target.get('path', '')
        if not tpath.exists():
            fail(errors, rel, f'hash target missing: {target.get("path")}')
            continue
        actual = sha256(tpath)
        if target.get('sha256') != actual:
            fail(errors, rel, f'hash mismatch for {target.get("path")}')

    limits = ' '.join(data.get('audit_limits', [])).lower()
    for phrase in ['does not prove learning', 'does not close ft-0181', 'not real pilot evidence']:
        if phrase not in limits:
            fail(errors, rel, f'audit_limits missing phrase: {phrase}')
    return errors


schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU release audit manifest':
    raise SystemExit('release audit schema title mismatch')

paths = sorted(MANIFEST_DIR.glob('*.json'))
if not paths:
    raise SystemExit('no release audit manifests found')

all_errors = []
for path in paths:
    all_errors.extend(validate(path))

if all_errors:
    raise SystemExit('release audit manifest validation errors:\n' + '\n'.join(all_errors))
print(f'check_release_audit_manifest: OK ({len(paths)} manifests)')
