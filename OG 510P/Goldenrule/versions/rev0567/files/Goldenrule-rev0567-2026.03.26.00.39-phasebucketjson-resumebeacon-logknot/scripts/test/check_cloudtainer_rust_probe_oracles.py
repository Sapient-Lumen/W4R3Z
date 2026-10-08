#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'cloudtainer_rust_probe_oracles.json'
QUEUE = ROOT / 'artifacts' / 'reports' / 'rust_external_test_queue.json'

EXPECTED_DETERMINISTIC_VARIANTS = {
    ('assertion_kind', 'coop_rate_a_at_least'),
    ('assertion_kind', 'coop_rate_b_at_least'),
    ('assertion_kind', 'mutual_defect_rate_at_most'),
    ('reputation_kind', 'simple_standing'),
    ('standing_update_rule', 'image_scoring'),
    ('standing_update_rule', 'standing_norm'),
    ('strategy_family', 'fsm'),
    ('strategy_family', 'memory_one_exit'),
}


def main() -> int:
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    queue = json.loads(QUEUE.read_text(encoding='utf-8'))
    rows = report.get('rows') or []
    summary = report.get('summary') or {}
    if len(rows) != len(queue.get('entries') or []):
        print('cloudtainer-rust-probe-oracles: row count mismatch', file=sys.stderr)
        return 1

    if int(summary.get('queue_row_count', -1)) != len(rows):
        print('cloudtainer-rust-probe-oracles: queue summary mismatch', file=sys.stderr)
        return 1

    unique_seed_paths = {row['seed_path'] for row in rows}
    if int(summary.get('unique_preferred_probe_seed_count', -1)) != len(unique_seed_paths):
        print('cloudtainer-rust-probe-oracles: unique seed count mismatch', file=sys.stderr)
        return 1

    exact_path = [row for row in rows if row.get('oracle_mode') == 'exact_path']
    exact_expectation = [row for row in rows if row.get('oracle_mode') == 'exact_expectation']
    if int(summary.get('exact_path_witness_rows', -1)) != len(exact_path):
        print('cloudtainer-rust-probe-oracles: exact path summary mismatch', file=sys.stderr)
        return 1
    if int(summary.get('exact_expectation_witness_rows', -1)) != len(exact_expectation):
        print('cloudtainer-rust-probe-oracles: exact expectation summary mismatch', file=sys.stderr)
        return 1

    deterministic_pairs = {(row['family'], row['variant']) for row in exact_path}
    if deterministic_pairs != EXPECTED_DETERMINISTIC_VARIANTS:
        print('cloudtainer-rust-probe-oracles: deterministic witness set drifted', file=sys.stderr)
        return 1

    standing_rows = [row for row in rows if 'standing_bootstrap' in row]
    if len(standing_rows) != 3:
        print('cloudtainer-rust-probe-oracles: expected exactly three standing bootstrap warnings', file=sys.stderr)
        return 1
    if int(summary.get('rows_with_inert_initial_standing_warning', -1)) != len(standing_rows):
        print('cloudtainer-rust-probe-oracles: standing warning summary mismatch', file=sys.stderr)
        return 1

    by_variant = {(row['family'], row['variant']): row for row in rows}
    coop_a = by_variant[('assertion_kind', 'coop_rate_a_at_least')]['mean_stats']['coop_rate_a']
    coop_b = by_variant[('assertion_kind', 'coop_rate_b_at_least')]['mean_stats']['coop_rate_b']
    mutual_d = by_variant[('assertion_kind', 'mutual_defect_rate_at_most')]['mean_stats']['mutual_defect_rate']
    if not math.isclose(coop_a, 1.0, rel_tol=0.0, abs_tol=1e-9):
        print('cloudtainer-rust-probe-oracles: expected coop_rate_a_at_least witness to be 1.0', file=sys.stderr)
        return 1
    if not math.isclose(coop_b, 0.0, rel_tol=0.0, abs_tol=1e-9):
        print('cloudtainer-rust-probe-oracles: expected coop_rate_b_at_least witness to be 0.0', file=sys.stderr)
        return 1
    if not math.isclose(mutual_d, 0.0, rel_tol=0.0, abs_tol=1e-9):
        print('cloudtainer-rust-probe-oracles: expected mutual_defect_rate_at_most witness to be 0.0', file=sys.stderr)
        return 1

    scaling = by_variant[('metamorphic_kind', 'scaling_prefix_stability')]
    mpw = scaling.get('metamorphic_prefix_witness') or {}
    if not mpw.get('expected_pass', False):
        print('cloudtainer-rust-probe-oracles: scaling prefix witness no longer reports exact pass', file=sys.stderr)
        return 1

    print(
        'cloudtainer-rust-probe-oracles: ok '
        f"(rows={len(rows)} exact_path={len(exact_path)} exact_expectation={len(exact_expectation)} standing_warnings={len(standing_rows)})"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
