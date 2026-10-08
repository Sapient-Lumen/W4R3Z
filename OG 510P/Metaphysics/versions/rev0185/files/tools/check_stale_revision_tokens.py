#!/usr/bin/env python3
from pathlib import Path
import sys, re, yaml

PRIOR_RE = re.compile(r'\brev(?:016[0-9]|017[0-9]|018[0-4])\b')
ALLOW_KEYS = {'predecessor_version','predecessor_package','carried_forward_from','historical_note','lineage_notes','source_history','migration_history','evidence_from_prior_release','first_added_revision','source_version','from_version','rollback_target'}
BLOCKING_KEYS = {'archive_version','package','current_release_version','allowed_claim_language','boundary_statement'}

def load(p):
    with open(p, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    version = (root/'VERSION').read_text(encoding='utf-8').strip()
    blocking = []
    warnings = []
    # This checker blocks stale tokens only in current identity/claim-bearing top-level fields.
    for p in sorted(root.glob('*.yml')):
        if p.name in {'MANIFEST.sha256'}:
            continue
        data = load(p)
        if not isinstance(data, dict):
            continue
        for k, v in data.items():
            if isinstance(v, str) and PRIOR_RE.search(v):
                if k in ALLOW_KEYS:
                    warnings.append({'file': p.name, 'field': k, 'token_context': 'allowed_historical_reference'})
                elif k in BLOCKING_KEYS or k.endswith('_version'):
                    blocking.append({'file': p.name, 'field': k, 'value': v[:160]})
                else:
                    warnings.append({'file': p.name, 'field': k, 'token_context': 'review_nested_or_historical_context'})
    readme = root/'README.md'
    if readme.exists():
        first = '\n'.join(readme.read_text(encoding='utf-8', errors='ignore').splitlines()[:40])
        if version not in first:
            blocking.append({'file':'README.md','field':'first_40_lines','value':'current version missing from front door'})
        if re.search(r'^Version:\s*rev017|^Version:\s*rev018[0-3]', first, re.M):
            blocking.append({'file':'README.md','field':'first_40_lines','value':'front door opens with stale Version line'})
    if blocking:
        print('STALE REVISION TOKEN CHECK FAILED')
        print(yaml.safe_dump({'blocking': blocking, 'warnings': warnings[:50]}, sort_keys=False).rstrip())
        return 1
    print('STALE REVISION TOKEN CHECK PASSED')
    print(yaml.safe_dump({'warnings_reviewed_count': len(warnings), 'scope': 'top-level current identity and current-claim fields block; historical references warn only'}, sort_keys=False).rstrip())
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
