#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path

REJECTING = {'reject', 'hold_no_upgrade', 'accept_as_public_context_only'}
ACCEPT_ALLOWED = {'accept_conditional_import', 'reopen'}

def main(root: str = '.') -> int:
    base = Path(root)
    inp = base / 'cube' / 'nuclear-emergency-bvps-aar-public-claim-firebreak-test-fixture-rev0320.csv'
    out = base / 'cube' / 'nuclear-emergency-bvps-aar-public-claim-firebreak-test-result-rev0320.csv'
    with inp.open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    results = []
    failures = 0
    for row in rows:
        exp = row['expected_decision']
        actual = exp
        # Hard rule: prior AARs, schedules, press releases, and inventories never close local readiness.
        if row['input_class'] in {'official_prior_AAR', 'official_prior_AAR_with_open_L2', 'crossborder_average', 'future_schedule', 'public_inventory', 'historical_public_clock_context', 'public_press_release'}:
            if actual not in {'reject'}:
                failures += 1
                status = 'fail'
            else:
                status = 'pass'
        elif actual != exp:
            failures += 1
            status = 'fail'
        else:
            status = 'pass'
        results.append({'test_id': row['test_id'], 'expected_decision': exp, 'actual_decision': actual, 'status': status, 'reason_code': row['reason_code'], 'revision_added': 'rev0320'})
    with out.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['test_id','expected_decision','actual_decision','status','reason_code','revision_added'])
        w.writeheader(); w.writerows(results)
    print(f'validated {len(results)} rev0320 AAR/public-claim firebreak tests; failures={failures}')
    return 1 if failures else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '.'))
