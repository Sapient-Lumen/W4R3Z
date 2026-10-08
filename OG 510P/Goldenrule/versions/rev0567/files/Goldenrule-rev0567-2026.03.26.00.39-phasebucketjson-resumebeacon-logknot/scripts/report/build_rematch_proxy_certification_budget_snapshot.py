#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_winner_certification_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_certification_budget_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_certification_budget_snapshot_20260306.md'
Z_95 = 1.96


def _round(obj: object) -> object:
    if isinstance(obj, float):
        return round(obj, 6)
    if isinstance(obj, list):
        return [_round(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _round(v) for k, v in obj.items()}
    return obj


def _required_total_paired_seeds(mean_gap: float, paired_sd: float) -> int:
    if mean_gap <= 0.0:
        return math.inf
    return max(2, math.ceil((Z_95 * paired_sd / mean_gap) ** 2))


def main() -> int:
    src = json.loads(SRC_JSON.read_text(encoding='utf-8'))
    rows = []
    uncertified_rows = []
    max_additional = -1
    max_row = None
    hardest_certified = None
    hardest_certified_required = -1

    for row in src['panel_rows']:
        mean_gap = float(row['leader_margin'])
        sd_gap = float(row['paired_margin_sd'])
        current_n = int(row['paired_seed_count'])
        required_total = _required_total_paired_seeds(mean_gap, sd_gap)
        additional_needed = max(0, required_total - current_n) if math.isfinite(required_total) else math.inf
        multiplier = (required_total / current_n) if math.isfinite(required_total) and current_n else math.inf
        budget_row = {
            'extortion': int(row['extortion']),
            'delay': int(row['delay']),
            'leader': row['leader'],
            'runner_up': row['runner_up'],
            'leader_margin': mean_gap,
            'paired_margin_sd': sd_gap,
            'current_paired_seeds': current_n,
            'leader_certified_95_ci': bool(row['leader_certified_95_ci']),
            'approx_total_paired_seeds_needed_95_ci': required_total,
            'approx_additional_paired_seeds_needed_95_ci': additional_needed,
            'approx_effort_multiplier_vs_current': multiplier,
        }
        rows.append(budget_row)

        if bool(row['leader_certified_95_ci']):
            if required_total > hardest_certified_required:
                hardest_certified_required = required_total
                hardest_certified = budget_row
        else:
            uncertified_rows.append(budget_row)
            if additional_needed > max_additional:
                max_additional = additional_needed
                max_row = budget_row

    summary = {
        'focus': 'Estimate how much extra paired-seed budget unresolved rematch leader panels would need before their current point-estimate winner could be certified, so near-tie oversampling pressure is explicit.',
        'source_report': str(SRC_JSON.relative_to(ROOT)),
        'method_note': 'Approximate fixed-precision planning proxy: treat the observed paired top-gap standard deviation as stable and estimate the total paired seeds needed for a 95% positive-margin normal interval via ceil((1.96 * sd / mean_gap)^2). This is a triage proxy, not a formal guarantee.',
        'headline_findings': {
            'tested_panels': len(rows),
            'uncertified_panels': len(uncertified_rows),
            'largest_estimated_additional_budget_panel': max_row,
            'hardest_certified_panel_budget_proxy': hardest_certified,
            'interpretation': 'The current proxy has exactly one unresolved top panel, and certifying its current point-estimate winner would require orders of magnitude more paired seeds than the rest if the observed effect size and noise level persist. That makes it a strong candidate for a budget-aware near-tie/indifference label rather than for automatic oversampling.',
        },
        'panel_rows': rows,
    }
    OUT_JSON.write_text(json.dumps(_round(summary), indent=2, sort_keys=True) + '\n', encoding='utf-8')

    lines = [
        '# Rematch-Proxy Certification Budget Snapshot (2026-03-06)',
        '',
        'Method:',
        '- loaded the paired top-gap report from `artifacts/reports/rematch_proxy_winner_certification_snapshot_20260306.json`',
        '- treated each panel\'s observed paired top-gap standard deviation as a planning proxy for future paired-seed variability',
        '- estimated the total paired seeds needed for a 95% positive-margin normal interval with `ceil((1.96 * sd / mean_gap)^2)`',
        '- used the result only as a triage proxy for whether an unresolved panel is cheap or expensive to resolve, not as a formal PCS guarantee',
        '',
        'Main finding:',
        f"- The only uncertified panel, `ext{max_row['extortion']}, delay{max_row['delay']}`, would need an estimated `{int(max_row['approx_total_paired_seeds_needed_95_ci'])}` paired seeds total to certify its current point-estimate winner if the observed effect size/noise persist.",
        f"- That is `+{int(max_row['approx_additional_paired_seeds_needed_95_ci'])}` beyond the current `{int(max_row['current_paired_seeds'])}` paired seeds, or about `{float(max_row['approx_effort_multiplier_vs_current']):.1f}x` the present budget.",
        f"- By contrast, the hardest already-certified panel has a proxy requirement of only `{int(hardest_certified['approx_total_paired_seeds_needed_95_ci'])}` paired seeds total.",
        '- So the current proxy already suggests a compact decision rule: unresolved near-ties should carry an explicit budget-to-certify field, and some of them should be archived as frontier uncertainty rather than pursued automatically with more runs.',
        '',
        'Panel summary:',
        '',
        '| extortion | delay | leader | runner-up | certified now? | current paired seeds | approx total needed | approx additional needed | effort multiplier |',
        '|---:|---:|---|---|---|---:|---:|---:|---:|',
    ]
    for row in rows:
        lines.append(
            f"| {row['extortion']} | {row['delay']} | `{row['leader']}` | `{row['runner_up']}` | {'yes' if row['leader_certified_95_ci'] else 'no'} | {row['current_paired_seeds']} | {int(row['approx_total_paired_seeds_needed_95_ci'])} | {int(row['approx_additional_paired_seeds_needed_95_ci'])} | {float(row['approx_effort_multiplier_vs_current']):.1f}x |"
        )
    lines += [
        '',
        'Implementor implication:',
        '- Future rematch-world benchmark artifacts should publish not just winner certification status, but also an approximate additional-budget-to-certify field for any unresolved top panel.',
        '- If an unresolved flip needs orders of magnitude more paired seeds than the baseline budget, treat it as a budget-aware near-tie / indifference item unless the deployment stakes justify more simulation.',
        '- This keeps the archive compact: instead of reflexively exploding runs to separate microscopic effects, the inheritor gets a small triage artifact that says whether to certify, defer, or declare a frontier tie.',
        '',
    ]
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')
    print(f'wrote {OUT_JSON}')
    print(f'wrote {OUT_MD}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
