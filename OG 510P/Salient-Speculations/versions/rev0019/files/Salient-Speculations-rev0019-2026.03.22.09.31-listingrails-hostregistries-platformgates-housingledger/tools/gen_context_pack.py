#!/usr/bin/env python3
from pathlib import Path
import json
import re
from collections import Counter

root = Path(__file__).resolve().parents[1]
reg = json.loads((root / 'SPECULATION_REGISTRY.json').read_text(encoding='utf-8'))
canon = [s for s in reg['speculations'] if s['status'] == 'canon']
quarantine = [s for s in reg['speculations'] if s['status'] == 'quarantine']
pattern_text = (root / 'docs/30-synthesis/pattern-language.md').read_text(encoding='utf-8')
portfolio_map_text = (root / 'docs/30-synthesis/portfolio-map.md').read_text(encoding='utf-8')
mechanism_families = [
    re.sub(r'^\d+\.\s*', '', heading).strip().lower()
    for heading in re.findall(r'^##\s+(.+)$', pattern_text, flags=re.MULTILINE)
    if re.match(r'^\d+\.', heading.strip())
]
meta_claim_match = re.search(r'\*\*(.+?)\*\*', portfolio_map_text, flags=re.DOTALL)
meta_claim = meta_claim_match.group(1).strip() if meta_claim_match else ''
domain_counts = Counter(s['domain'] for s in canon)
mechanism_counts = Counter(s['mechanism_family'] for s in canon)
context = {
    'project': 'Salient Speculations',
    'version': reg['version'],
    'read_first': [
        'START_HERE.md',
        'docs/00-meta/charter.md',
        'docs/10-method/salience-rubric.md',
        'docs/30-synthesis/pattern-language.md',
        'docs/30-synthesis/portfolio-map.md'
    ],
    'meta_claim': meta_claim,
    'mechanism_families': mechanism_families,
    'canon_count': len(canon),
    'quarantine_count': len(quarantine),
    'canonical_ids': [s['id'] for s in canon],
    'quarantine_ids': [s['id'] for s in quarantine],
    'canon_by_domain': dict(sorted(domain_counts.items())),
    'canon_by_mechanism_family': dict(sorted(mechanism_counts.items())),
    'updated_at': reg['updated_at']
}
(root / 'context-pack.json').write_text(json.dumps(context, indent=2) + '\n', encoding='utf-8')
print('Wrote context-pack.json')
