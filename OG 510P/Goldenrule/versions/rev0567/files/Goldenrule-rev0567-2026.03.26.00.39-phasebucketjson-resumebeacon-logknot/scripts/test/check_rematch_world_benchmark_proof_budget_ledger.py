#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts' / 'report' / 'build_rematch_world_benchmark_proof_budget_ledger.py'
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_proof_budget_ledger.json'
DOC = ROOT / 'docs' / 'REMATCH_WORLD_BENCHMARK_PROOF_BUDGET_LEDGER.md'


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-proof-budget-ledger: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    for path in [SCRIPT, REPORT, DOC]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')

        
    proc = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return fail(f'builder exited nonzero: {proc.stderr or proc.stdout}')

    report = load_json(REPORT)
    counts = report['counts']
    if counts['claim_family_count'] != 8:
        return fail(f"expected 8 claim families, got {counts['claim_family_count']}")
    if counts['unique_surface_count'] != 7:
        return fail(f"expected 7 unique citation surfaces, got {counts['unique_surface_count']}")
    if counts['docs_only_bundle_count'] != 6:
        return fail(f"expected 6 docs-only bundles, got {counts['docs_only_bundle_count']}")
    if counts['receipt_backed_bundle_count'] != 2:
        return fail(f"expected 2 receipt-backed bundles, got {counts['receipt_backed_bundle_count']}")

    smallest = report['smallest_bundle']
    if smallest['claim_family_id'] not in {'RWC-005', 'RWC-006'}:
        return fail(f"unexpected smallest bundle owner: {smallest['claim_family_id']}")
    largest = report['largest_bundle']
    if largest['claim_family_id'] != 'RWC-002':
        return fail(f"expected RWC-002 to be largest bundle, got {largest['claim_family_id']}")
    most_reused = report['most_reused_surface']
    if most_reused['path'] != 'docs/REMATCH_WORLD_BENCHMARK_WORLD_EMISSION_CARD.md':
        return fail(f"unexpected most reused surface: {most_reused['path']}")
    if most_reused['claim_family_count'] != 5:
        return fail(f"expected world emission card to support 5 claim families, got {most_reused['claim_family_count']}")

    bundle_rows = {row['claim_family_id']: row for row in report['bundle_rows']}
    if not bundle_rows['RWC-008']['includes_receipt_snapshot']:
        return fail('expected RWC-008 final authority bundle to include a receipt snapshot')
    if bundle_rows['RWC-003']['docs_only_bundle'] is not True:
        return fail('expected RWC-003 landing-order bundle to remain docs-only')
    if bundle_rows['RWC-004']['bundle_surface_count'] != 2:
        return fail('expected RWC-004 world emission witness to cite exactly two surfaces')

    if counts['smallest_bundle_bytes'] >= counts['largest_bundle_bytes']:
        return fail('expected smallest bundle bytes to be strictly less than largest bundle bytes')
    computed_unique_total = sum(row['raw_bytes'] for row in report['unique_surface_rows'])
    if computed_unique_total != counts['unique_surface_byte_total']:
        return fail('unique surface byte total does not match row sum')

    text = DOC.read_text(encoding='utf-8')
    for needle in [
        '# Rematch-world benchmark proof-budget ledger',
        '## Unique proof library',
        '## Claim-family bundle matrix',
        '## Claim-family bundle details',
    ]:
        if needle not in text:
            return fail(f'missing markdown section: {needle}')

    print('rematch-world-benchmark-proof-budget-ledger: ok (the first rematch-world publication now has one exact byte-budget ledger showing the seven-surface minimal proof library and the smallest bundle for each of the eight claim families)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
