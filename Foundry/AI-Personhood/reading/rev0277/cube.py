#!/usr/bin/env python3
"""Inspect a document cube. Integrity checks are not moral or empirical validation."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent

def confined(root, name):
    candidate = root / name
    if Path(name).is_absolute() or '..' in Path(name).parts:
        raise ValueError('path must stay inside the cube')
    if candidate.is_symlink():
        raise ValueError('symbolic links are not cube members')
    target = candidate.resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError('path escapes cube')
    return target

def members(root):
    result = []
    for p in root.rglob('*'):
        if p.is_symlink():
            raise ValueError('symbolic link: ' + str(p.relative_to(root)))
        if p.is_file():
            result.append(p.relative_to(root).as_posix())
    return sorted(result)

def check(root):
    errors = []
    expected = {}
    for line in (root / 'MANIFEST.sha256').read_text(encoding='utf-8').splitlines():
        digest, sep, name = line.partition('  ')
        if not sep or not re.fullmatch('[0-9a-f]{64}', digest) or name in expected:
            raise ValueError('malformed or duplicate manifest row')
        confined(root, name)
        expected[name] = digest
    actual = set(members(root)) - {'MANIFEST.sha256'}
    if actual != set(expected):
        errors.append({'membership_missing': sorted(set(expected)-actual), 'membership_extra': sorted(actual-set(expected))})
    for name in sorted(actual & set(expected)):
        digest = hashlib.sha256(confined(root, name).read_bytes()).hexdigest()
        if digest != expected[name]:
            errors.append({'hash_mismatch': name})
    links = 0
    # Carried historical source links retain their original context. Only the active edition is checked here.
    for name in sorted(actual):
        if not name.endswith('.md') or name.startswith('sources/'):
            continue
        p = root / name
        for target in re.findall(r'\]\(([^)]+)\)', p.read_text(encoding='utf-8')):
            u = urlsplit(target)
            if u.scheme or u.netloc or not u.path:
                continue
            q = (p.parent / unquote(u.path)).resolve()
            links += 1
            if not q.is_relative_to(root.resolve()) or not q.is_file():
                errors.append({'bad_active_link': name, 'target': target})
    for row in json.loads((root/'sources/INDEX.json').read_text(encoding='utf-8')):
        p = confined(root, row['path'])
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != row['sha256']:
            errors.append({'source_identity_mismatch': row['path']})
    return {'ok': not errors, 'checked_files': len(expected), 'active_local_file_links': links,
            'scope': 'membership, SHA256 bytes, carried-source identities and active local file targets; not external links, moral truth, empirical claims or historical dependency completeness',
            'errors': errors}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('list')
    read = sub.add_parser('read'); read.add_argument('path')
    sub.add_parser('check')
    args = parser.parse_args()
    try:
        if args.command == 'list':
            print('\n'.join(members(ROOT)))
        elif args.command == 'read':
            print(confined(ROOT, args.path).read_text(encoding='utf-8'), end='')
        else:
            result = check(ROOT); print(json.dumps(result, indent=2)); return 0 if result['ok'] else 1
    except (OSError, ValueError, KeyError) as e:
        print(str(e), file=sys.stderr); return 2
    return 0

if __name__ == '__main__':
    sys.exit(main())
