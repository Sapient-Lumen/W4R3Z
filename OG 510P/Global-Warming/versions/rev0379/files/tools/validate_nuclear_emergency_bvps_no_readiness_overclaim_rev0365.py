#!/usr/bin/env python3
"""Scan current-risk BVPS files for affirmative readiness-overclaim language."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
patterns=[
    'proved local readiness', 'local readiness proved', 'certified ready', 'passed the exercise',
    'exercise passed', 'readiness proof achieved', 'readiness closure granted',
    'release eligibility granted', 'alert success assumed', 'protective action success assumed'
]
scan_rels=[
    '572-nuclear-emergency-preparedness-chaincustody-intakecli-fieldkitpointers-refactor-compact-canon.md',
    '571-nuclear-emergency-preparedness-realevidencegate-fixtureinert-statusvocab-refactor-compact-canon.md',
    'README.md','CHANGELOG-rev0365.md','structural-audit-rev0365.md',
    'cube/nuclear-emergency-bvps-evidence-packet-contract-rev0365.csv',
    'cube/nuclear-emergency-bvps-chain-of-custody-intake-ledger-rev0365.csv',
    'cube/nuclear-emergency-bvps-evidence-intake-fixture-ledger-rev0365.csv',
    'cube/nuclear-emergency-bvps-minimum-evidence-proofcut-rev0365.csv',
    'cube/bvps-fieldkit-copy-policy-rev0365.csv',
    'field-kits/bvps-rev0365/fieldkit-pointer-manifest-rev0365.csv',
]
errors=[]
for rel in scan_rels:
    p=ROOT/rel
    if not p.exists():
        errors.append('missing_scan_target:'+rel); continue
    text=p.read_text(encoding='utf-8', errors='ignore').lower()
    for pat in patterns:
        if pat in text:
            errors.append(f'forbidden_phrase:{pat}:{rel}')
if errors:
    print('FAIL no_readiness_overclaim ' + ';'.join(errors[:20])); sys.exit(1)
print(f'PASS no_readiness_overclaim scanned={len(scan_rels)} patterns={len(patterns)}')
