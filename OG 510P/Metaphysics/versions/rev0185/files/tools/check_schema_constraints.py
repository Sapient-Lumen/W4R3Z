#!/usr/bin/env python3
from pathlib import Path
import sys, yaml

NEW_SCHEMA_PREFIXES = {
    'current-release','reader-journey','schema-constraint-profile','source-anchor','source-review','debt-taxonomy',
    'accessibility-test','comprehension-study','reader-task','glossary-usability','screen-reader-smoke-test',
    'keyboard-navigation-check','translation-readiness','export-readiness','discovery-backlog','concept-cube','cube-audit','concept-cube-refactor','concept-relation-map','concept-family-map','source-crosswalk-normalization','source-citation-index','source-family-map','source-relation-map','source-audit','source-cube-refactor','claim-observation-index','claim-relation-map','claim-audit','claim-cube-refactor','debt-observation-index','debt-lifecycle-policy','debt-relation-map','debt-audit','debt-cube-refactor'
}

def load(p):
    with open(p, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    failures = []
    version = (root/'VERSION').read_text(encoding='utf-8').strip()
    for fam in NEW_SCHEMA_PREFIXES:
        p = root/'REGISTERS'/'schemas'/f'{fam}-record-v1.yml'
        if not p.exists():
            failures.append(f'missing new schema: {p.relative_to(root)}')
            continue
        schema = load(p)
        if not schema.get('required_fields'):
            failures.append(f'{p.name}: required_fields missing')
        constraints = schema.get('field_constraints') or {}
        if 'archive_version' not in constraints or 'package' not in constraints:
            failures.append(f'{p.name}: current identity constraints missing')
    # Check new current records resolve their source_artifacts.
    for rec in sorted((root/'REGISTERS').glob(f'{version}-*.yml')):
        data = load(rec)
        for rel in data.get('source_artifacts', []) or []:
            if not (root/rel).exists():
                failures.append(f'{rec.name}: source artifact missing: {rel}')
    if failures:
        print('SCHEMA CONSTRAINT CHECK FAILED')
        for f in failures[:100]: print('-', f)
        return 1
    print('SCHEMA CONSTRAINT CHECK PASSED')
    print(f'new_schema_families: {len(NEW_SCHEMA_PREFIXES)}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
