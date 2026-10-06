#!/usr/bin/env python3
"""Keep the product-profile default-key vocabulary small, flat, and wired.

Checks:
- spec/product.profile.schema.json explicitly allowlists default keys
- docs/501-product-profile-default-vocabulary-boundary.md carries the same key registry
- spec/examples/product.profiles.json uses only the allowlisted keys
- docs/411-product-profiles-as-compilation-target.md points to docs/501

This is intentionally conservative: it keeps the allowlisted vocabulary stable and also rejects
known-overlap keys that the archive has explicitly removed.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / 'spec' / 'product.profile.schema.json'
EXAMPLE = ROOT / 'spec' / 'examples' / 'product.profiles.json'
REGISTRY_DOC = ROOT / 'docs' / '501-product-profile-default-vocabulary-boundary.md'
PROFILE_DOC = ROOT / 'docs' / '411-product-profiles-as-compilation-target.md'
TELEMETRY_DOC = ROOT / 'docs' / '503-telemetry-is-not-a-product-profile-default-boundary.md'
START = '<!-- registry:start -->'
END = '<!-- registry:end -->'
KEY_RE = re.compile(r"^-\s+`(?P<key>[a-z_]+)`\s+—\s+.+$")


def _schema_keys() -> set[str]:
    obj = json.loads(SCHEMA.read_text(encoding='utf-8'))
    defaults = ((obj.get('properties') or {}).get('defaults') or {})
    if defaults.get('additionalProperties') is not False:
        raise SystemExit('spec/product.profile.schema.json: defaults.additionalProperties must be false')
    props = defaults.get('properties') or {}
    if not props:
        raise SystemExit('spec/product.profile.schema.json: defaults.properties is empty')
    bad = [k for k, v in props.items() if (v or {}).get('type') != 'string']
    if bad:
        raise SystemExit('spec/product.profile.schema.json: default-key properties must all be strings: ' + ', '.join(sorted(bad)))
    return set(props.keys())


def _registry_keys() -> set[str]:
    txt = REGISTRY_DOC.read_text(encoding='utf-8')
    if START not in txt or END not in txt:
        raise SystemExit(f'{REGISTRY_DOC.relative_to(ROOT)}: missing registry markers')
    block = txt.split(START, 1)[1].split(END, 1)[0]
    keys: list[str] = []
    for raw in block.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = KEY_RE.match(line)
        if not m:
            raise SystemExit(f'{REGISTRY_DOC.relative_to(ROOT)}: malformed registry line: {line}')
        keys.append(m.group('key'))
    if not keys:
        raise SystemExit(f'{REGISTRY_DOC.relative_to(ROOT)}: registry is empty')
    dupes = sorted({k for k in keys if keys.count(k) > 1})
    if dupes:
        raise SystemExit(f'{REGISTRY_DOC.relative_to(ROOT)}: duplicate registry keys: {", ".join(dupes)}')
    return set(keys)


def _example_keys() -> set[str]:
    obj = json.loads(EXAMPLE.read_text(encoding='utf-8'))
    keys: set[str] = set()
    for pid, profile in (obj.get('profiles') or {}).items():
        defaults = (profile or {}).get('defaults') or {}
        if not isinstance(defaults, dict):
            raise SystemExit(f'{EXAMPLE.relative_to(ROOT)}: profiles.{pid}.defaults must be an object')
        keys.update(defaults.keys())
    return keys


BANNED_KEYS = {"telemetry"}


def main() -> int:
    schema_keys = _schema_keys()
    registry_keys = _registry_keys()
    example_keys = _example_keys()

    problems: list[str] = []
    if schema_keys != registry_keys:
        problems.append('schema vs registry mismatch: only-in-schema=' + ', '.join(sorted(schema_keys - registry_keys)) + ' only-in-doc=' + ', '.join(sorted(registry_keys - schema_keys)))
    if example_keys - schema_keys:
        problems.append('example uses unknown default keys: ' + ', '.join(sorted(example_keys - schema_keys)))

    banned_hits = sorted((schema_keys | registry_keys | example_keys) & BANNED_KEYS)
    if banned_hits:
        problems.append('banned overlapping default keys reintroduced: ' + ', '.join(banned_hits))

    profile_doc = PROFILE_DOC.read_text(encoding='utf-8')
    if 'docs/501-product-profile-default-vocabulary-boundary.md' not in profile_doc:
        problems.append('docs/411-product-profiles-as-compilation-target.md must reference docs/501-product-profile-default-vocabulary-boundary.md')
    if 'docs/503-telemetry-is-not-a-product-profile-default-boundary.md' not in profile_doc:
        problems.append('docs/411-product-profiles-as-compilation-target.md must reference docs/503-telemetry-is-not-a-product-profile-default-boundary.md')

    telemetry_doc = TELEMETRY_DOC.read_text(encoding='utf-8')
    if 'docs/501-product-profile-default-vocabulary-boundary.md' not in telemetry_doc:
        problems.append('docs/503-telemetry-is-not-a-product-profile-default-boundary.md must reference docs/501-product-profile-default-vocabulary-boundary.md')

    if problems:
        print('Product-profile default vocabulary check FAILED')
        for p in problems:
            print('- ' + p)
        return 1

    print('Product-profile default vocabulary check OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
