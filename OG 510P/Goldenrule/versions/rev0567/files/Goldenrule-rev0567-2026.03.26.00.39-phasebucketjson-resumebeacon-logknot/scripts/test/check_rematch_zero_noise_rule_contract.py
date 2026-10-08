#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RULE_REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_zero_noise_rule_classifier_snapshot_20260306.json'
CACHE_PLAN_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_cache_plan_snapshot_20260306.json'
EXPECTED_RULE_COUNT = 17
EXPECTED_SIGNATURE_COUNT = 243
EXPECTED_REGIME_COUNT = 17


def fail(msg: str) -> int:
    print(f'zero-noise-rule-contract: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise SystemExit(fail(f'invalid JSON in {path.relative_to(ROOT)}: {exc}'))


def compile_pattern(pattern: str) -> re.Pattern[str]:
    body = ''.join('.' if ch == '*' else ch for ch in pattern)
    return re.compile(f'^{body}$')


def main() -> int:
    if not RULE_REPORT_PATH.exists():
        return fail(f'missing {RULE_REPORT_PATH.relative_to(ROOT)}')
    if not CACHE_PLAN_PATH.exists():
        return fail(f'missing {CACHE_PLAN_PATH.relative_to(ROOT)}')

    report = load_json(RULE_REPORT_PATH)
    cache_plan = load_json(CACHE_PLAN_PATH)
    if not isinstance(report, dict):
        return fail('rule report root must be object')
    if not isinstance(cache_plan, dict):
        return fail('cache plan root must be object')

    world = report.get('world')
    rule_rows = report.get('rule_rows')
    summary = report.get('summary')
    if not isinstance(world, dict):
        return fail('world must be object')
    if not isinstance(rule_rows, list) or not rule_rows:
        return fail('rule_rows must be non-empty list')
    if not isinstance(summary, dict):
        return fail('summary must be object')

    if world.get('kind') != 'rematch_proxy_zero_noise_rule_classifier':
        return fail(f"unexpected world.kind: {world.get('kind')}")
    if world.get('support_signature_count') != EXPECTED_SIGNATURE_COUNT:
        return fail('unexpected support_signature_count')
    if world.get('regime_count') != EXPECTED_REGIME_COUNT:
        return fail('unexpected regime_count')
    if len(rule_rows) != EXPECTED_RULE_COUNT:
        return fail('unexpected rule count')
    if summary.get('ordered_rule_count') != EXPECTED_RULE_COUNT:
        return fail('summary ordered_rule_count mismatch')
    if summary.get('lookup_signature_count') != EXPECTED_SIGNATURE_COUNT:
        return fail('summary lookup_signature_count mismatch')
    if summary.get('exact_match') is not True:
        return fail('summary exact_match must be true')

    none_row = next((row for row in cache_plan.get('mode_rows', []) if row.get('id') == 'none'), None)
    if not isinstance(none_row, dict):
        return fail('cache plan missing none mode row')
    signature_to_regime = none_row.get('signature_to_regime')
    regime_rows = {row['regime_id']: row for row in none_row.get('regime_rows', [])}
    if not isinstance(signature_to_regime, dict) or len(signature_to_regime) != EXPECTED_SIGNATURE_COUNT:
        return fail('cache plan none.signature_to_regime must cover all support signatures')

    seen_rule_ids = set()
    claimed = {}
    for row in rule_rows:
        if not isinstance(row, dict):
            return fail('each rule row must be object')
        rule_id = row.get('rule_id')
        pattern = row.get('pattern')
        regime_id = row.get('regime_id')
        if rule_id in seen_rule_ids:
            return fail('duplicate rule_id')
        seen_rule_ids.add(rule_id)
        if regime_id not in regime_rows:
            return fail(f'{rule_id}: unknown regime_id {regime_id}')
        regex = compile_pattern(pattern)
        matches = sorted(sig for sig in signature_to_regime if sig not in claimed and regex.fullmatch(sig))
        if not matches:
            return fail(f'{rule_id}: matched no new signatures')
        if any(signature_to_regime[sig] != regime_id for sig in matches):
            return fail(f'{rule_id}: pattern crosses regimes')
        if row.get('signature_count') != len(matches):
            return fail(f'{rule_id}: signature_count mismatch')
        if row.get('quotient_family_count') != regime_rows[regime_id].get('quotient_family_count'):
            return fail(f'{rule_id}: quotient_family_count mismatch')
        expected_examples = regime_rows[regime_id].get('quotient_family_examples')
        if row.get('quotient_family_examples') != expected_examples:
            return fail(f'{rule_id}: quotient_family_examples mismatch')
        reps = row.get('representative_signatures')
        if not isinstance(reps, list) or reps != matches[:len(reps)]:
            return fail(f'{rule_id}: representative_signatures mismatch')
        for sig in matches:
            claimed[sig] = rule_id

    if set(claimed) != set(signature_to_regime):
        return fail('ordered rules do not cover all support signatures exactly once')

    largest = max(rule_rows, key=lambda row: row['signature_count'])
    smallest = min(rule_rows, key=lambda row: row['signature_count'])
    if summary.get('largest_rule_id') != largest['rule_id']:
        return fail('largest_rule_id mismatch')
    if summary.get('largest_pattern') != largest['pattern']:
        return fail('largest_pattern mismatch')
    if summary.get('largest_rule_signature_count') != largest['signature_count']:
        return fail('largest_rule_signature_count mismatch')
    if summary.get('smallest_rule_id') != smallest['rule_id']:
        return fail('smallest_rule_id mismatch')
    if summary.get('smallest_pattern') != smallest['pattern']:
        return fail('smallest_pattern mismatch')
    if summary.get('smallest_rule_signature_count') != smallest['signature_count']:
        return fail('smallest_rule_signature_count mismatch')

    print(f'zero-noise-rule-contract: ok ({EXPECTED_RULE_COUNT} rules, {EXPECTED_SIGNATURE_COUNT} signatures)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
