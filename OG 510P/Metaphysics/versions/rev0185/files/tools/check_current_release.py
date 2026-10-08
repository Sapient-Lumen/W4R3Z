#!/usr/bin/env python3
from pathlib import Path
import sys, yaml

def load(p):
    with open(p, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    failures = []
    version = (root/'VERSION').read_text(encoding='utf-8').strip() if (root/'VERSION').exists() else None
    cur = load(root/'CURRENT_RELEASE.yml') if (root/'CURRENT_RELEASE.yml').exists() else {}
    if not cur:
        failures.append('missing CURRENT_RELEASE.yml')
    if version != cur.get('archive_version'):
        failures.append(f'VERSION/CURRENT_RELEASE mismatch: {version!r} vs {cur.get("archive_version")!r}')
    package = cur.get('package')
    if not package or version not in package:
        failures.append('current package does not contain current version token')
    final_doc = cur.get('final_numbered_doc')
    current_doc = (cur.get('current_layer') or {}).get('doc')
    if not isinstance(final_doc, int) or not current_doc or not (root/current_doc).exists():
        failures.append('current final doc missing or invalid')
    elif not Path(current_doc).name.startswith(f'{final_doc}-'):
        failures.append('current final doc path does not match final_numbered_doc')
    for rel in cur.get('front_door_artifacts', []):
        if not (root/rel).exists():
            failures.append(f'front-door artifact missing: {rel}')
    for rel in cur.get('validation_tools', []):
        if not (root/rel).exists():
            failures.append(f'validation tool missing: {rel}')
    # Check top-level package/archive fields that are declaring current release identity.
    for p in sorted(root.glob('*.yml')):
        if p.name == 'MANIFEST.sha256':
            continue
        data = load(p)
        if not isinstance(data, dict):
            continue
        if 'archive_version' in data and data['archive_version'] != version:
            failures.append(f'{p.name}: archive_version={data["archive_version"]!r} expected {version!r}')
        if 'package' in data and data['package'] != package:
            failures.append(f'{p.name}: package does not match CURRENT_RELEASE.yml')
    if failures:
        print('CURRENT RELEASE CHECK FAILED')
        for f in failures:
            print('-', f)
        return 1
    print('CURRENT RELEASE CHECK PASSED')
    print(f'version: {version}')
    print(f'package: {package}')
    print(f'final_doc: {final_doc}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
