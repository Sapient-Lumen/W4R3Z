#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_matching_state_interpretation_handoff.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_matching_state_interpretation_handoff_snapshot_20260317.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_matching_state_interpretation_handoff_snapshot_20260317.md'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def render_md(report: dict[str, Any]) -> str:
    return '\n'.join([
        '# Rematch-world benchmark matching-state interpretation handoff snapshot — 2026-03-17',
        '',
        f"Focus: {report['focus']}",
        '',
        '## Local result',
        '',
        '- The benchmark seed now carries one compact matching-state interpretation handoff copied from the proxy matching-friction and occupancy-accounting reports.',
        f"- The copied handoff keeps the delay-tax headline directly: all `{report['tested_cells']}` tested policy/extortion cells are monotone in delay, with `{report['largest_mean_delay_tax_policy']}` as the largest mean delay-tax policy and `{report['smallest_mean_delay_tax_policy']}` as the smallest.",
        f"- It also keeps the comparability seam explicit: the mean share of delay loss explained by shrinking matched-round share is `{report['mean_share_component_fraction_of_delay_loss']}` while max in-match drift is only `{report['max_abs_in_match_payoff_drift_delay0_to_delay2']}`.",
        '',
        '## Implementor guidance',
        '',
        '- Treat the copied handoff as the first benchmark-facing summary for `SQ-013`, not as a replacement for native matching-state outputs.',
        '- Keep delay/search dead-time separate from matching-efficiency interpretation and require both search-state fields and matched-state fields when filling the native matching-state section.',
        '- Replace the copied handoff once endogenous rematch worlds can emit matched-vs-searching state and delay/efficiency semantics directly.',
        '',
    ])


def main() -> int:
    handoff = load_json(EXAMPLE)
    report = {
        'snapshot_date': '2026-03-17',
        'focus': 'wire a compact matching-state interpretation summary directly into the rematch-world benchmark seed so future implementors can cite one frozen packet for delay-tax semantics and the matched-vs-search split',
        'analysis_script': 'scripts/report/build_rematch_world_benchmark_matching_state_interpretation_handoff_snapshot.py',
        'matching_friction_report_path': handoff['matching_friction_report_path'],
        'matching_friction_report_sha256': handoff['matching_friction_report_sha256'],
        'occupancy_accounting_report_path': handoff['occupancy_accounting_report_path'],
        'occupancy_accounting_report_sha256': handoff['occupancy_accounting_report_sha256'],
        'tested_cells': handoff['delay_tax_summary']['tested_cells'],
        'tested_policy_ids': handoff['tested_policy_ids'],
        'largest_mean_delay_tax_policy': handoff['delay_tax_summary']['largest_mean_delay_tax_policy'],
        'smallest_mean_delay_tax_policy': handoff['delay_tax_summary']['smallest_mean_delay_tax_policy'],
        'mean_share_component_fraction_of_delay_loss': handoff['occupancy_accounting_summary']['mean_share_component_fraction_of_delay_loss'],
        'max_abs_in_match_payoff_drift_delay0_to_delay2': handoff['occupancy_accounting_summary']['max_abs_in_match_payoff_drift_delay0_to_delay2'],
        'required_search_state_fields': handoff['matching_state_contract_guidance']['required_search_state_fields'],
        'required_matched_state_fields': handoff['matching_state_contract_guidance']['required_matched_state_fields'],
        'recommended_next_move': 'Keep the copied matching-state interpretation handoff frozen in the benchmark seed and prioritize native emission of matched-vs-searching state before widening retained matching-side artifacts.',
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(report) + '\n', encoding='utf-8')
    print(f'rematch-world-benchmark-matching-state-interpretation-handoff-snapshot: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'rematch-world-benchmark-matching-state-interpretation-handoff-snapshot: wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
