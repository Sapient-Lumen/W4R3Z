#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_winner_certification_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_materiality_gate_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_materiality_gate_snapshot_20260306.md'
T_CRIT_90_DF5 = 2.015048
CANDIDATE_DELTAS = [0.005, 0.01]


def _round(obj: object) -> object:
    if isinstance(obj, float):
        return round(obj, 6)
    if isinstance(obj, list):
        return [_round(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _round(v) for k, v in obj.items()}
    return obj


def _classify(ci_low_90: float, ci_high_90: float, delta: float) -> str:
    if ci_low_90 > delta:
        return 'material_leader'
    if ci_low_90 > -delta and ci_high_90 < delta:
        return 'practical_tie'
    return 'undecided'


def main() -> int:
    src = json.loads(SRC_JSON.read_text(encoding='utf-8'))

    panel_rows: list[dict[str, object]] = []
    counts_by_delta = {str(delta): {'material_leader': 0, 'practical_tie': 0, 'undecided': 0} for delta in CANDIDATE_DELTAS}
    certified_and_tied_at_005: list[dict[str, object]] = []
    uncertified_but_tied_at_001: list[dict[str, object]] = []
    smallest_equivalence_delta_panel = None
    smallest_equivalence_delta = None
    largest_equivalence_delta_panel = None
    largest_equivalence_delta = None

    for row in src['panel_rows']:
        mean_gap = float(row['leader_margin'])
        se_gap = float(row['paired_margin_se'])
        ci_low_90 = mean_gap - T_CRIT_90_DF5 * se_gap
        ci_high_90 = mean_gap + T_CRIT_90_DF5 * se_gap
        largest_material_delta_supported = max(0.0, ci_low_90)
        smallest_equivalence_delta_supported = max(abs(ci_low_90), abs(ci_high_90))
        classes: dict[str, str] = {}
        for delta in CANDIDATE_DELTAS:
            label = str(delta)
            cls = _classify(ci_low_90, ci_high_90, delta)
            counts_by_delta[label][cls] += 1
            classes[label] = cls

        out_row = {
            'extortion': int(row['extortion']),
            'delay': int(row['delay']),
            'leader': row['leader'],
            'runner_up': row['runner_up'],
            'leader_certified_95_ci': bool(row['leader_certified_95_ci']),
            'leader_margin': mean_gap,
            'paired_margin_ci_low_90': ci_low_90,
            'paired_margin_ci_high_90': ci_high_90,
            'largest_material_delta_supported_90': largest_material_delta_supported,
            'smallest_equivalence_delta_supported_90': smallest_equivalence_delta_supported,
            'delta_classifications': classes,
        }
        panel_rows.append(out_row)

        if bool(row['leader_certified_95_ci']) and classes[str(0.005)] == 'practical_tie':
            certified_and_tied_at_005.append(
                {
                    'extortion': int(row['extortion']),
                    'delay': int(row['delay']),
                    'leader': row['leader'],
                    'runner_up': row['runner_up'],
                    'leader_margin': mean_gap,
                }
            )
        if (not bool(row['leader_certified_95_ci'])) and classes[str(0.01)] == 'practical_tie':
            uncertified_but_tied_at_001.append(
                {
                    'extortion': int(row['extortion']),
                    'delay': int(row['delay']),
                    'leader': row['leader'],
                    'runner_up': row['runner_up'],
                    'leader_margin': mean_gap,
                }
            )

        if smallest_equivalence_delta is None or smallest_equivalence_delta_supported < smallest_equivalence_delta:
            smallest_equivalence_delta = smallest_equivalence_delta_supported
            smallest_equivalence_delta_panel = out_row
        if largest_equivalence_delta is None or smallest_equivalence_delta_supported > largest_equivalence_delta:
            largest_equivalence_delta = smallest_equivalence_delta_supported
            largest_equivalence_delta_panel = out_row

    summary = {
        'focus': 'Separate statistical winner certification from practical materiality by mapping each rematch top-gap panel into material-leader / practical-tie / undecided regions under a declared smallest effect of interest.',
        'source_report': str(SRC_JSON.relative_to(ROOT)),
        'method_note': 'Used the paired top-gap mean and SE from the winner-certification snapshot to form 90% t-intervals (df=5). For a declared practical margin delta, classify each panel as material_leader when the 90% interval lies entirely above delta, practical_tie when it lies entirely within [-delta, delta], and undecided otherwise.',
        'headline_findings': {
            'tested_panels': len(panel_rows),
            'counts_by_delta': counts_by_delta,
            'certified_leader_but_practical_tie_at_delta_0_005': certified_and_tied_at_005,
            'uncertified_leader_but_practical_tie_at_delta_0_01': uncertified_but_tied_at_001,
            'smallest_equivalence_delta_supported_panel': smallest_equivalence_delta_panel,
            'largest_equivalence_delta_supported_panel': largest_equivalence_delta_panel,
            'interpretation': 'Winner certification and practical materiality are different gates. In the current proxy, several statistically certified leaders become practical ties under a modest smallest effect of interest, and the only uncertified leader flip already becomes a practical tie once the indifference zone reaches roughly one hundredth of payoff.',
        },
        'panel_rows': panel_rows,
    }
    OUT_JSON.write_text(json.dumps(_round(summary), indent=2, sort_keys=True) + '\n', encoding='utf-8')

    lines = [
        '# Rematch-Proxy Materiality-Gate Snapshot (2026-03-06)',
        '',
        'Method:',
        '- loaded the paired top-gap means and SEs from `artifacts/reports/rematch_proxy_winner_certification_snapshot_20260306.json`',
        '- formed 90% paired t-intervals (`df=5`) for the top-vs-runner-up gap so a declared smallest effect of interest `delta` can be used as an indifference zone',
        '- classified each panel as `material_leader` when the full 90% interval lies above `delta`, `practical_tie` when the full 90% interval lies inside `[-delta, delta]`, and `undecided` otherwise',
        '- reported the largest `delta` still compatible with a materially better leader and the smallest `delta` that would already certify a practical tie',
        '',
        'Main finding:',
        '- Winner certification and practical materiality are not the same gate in the current proxy.',
        '- At `delta=0.005`, there are `5` materially separated panels, `3` practical ties, and `1` undecided panel; the three practical ties are all extortion-20 panels whose leaders are statistically certified but too small to be materially distinct at that threshold.',
        '- At `delta=0.01`, there are `3` materially separated panels, `4` practical ties, and `2` undecided panels; the only uncertified leader flip (`ext80, delay2`) is already a practical tie at that threshold.',
        '- For `ext80, delay2`, the current six paired seeds already support a practical-tie declaration for any `delta >= 0.008233`, even though certifying a winner there would require orders of magnitude more simulation.',
        '',
        'Panel summary:',
        '',
        '| extortion | delay | leader | runner-up | 90% CI low | 90% CI high | largest material delta | smallest tie delta | class @ 0.005 | class @ 0.01 |',
        '|---:|---:|---|---|---:|---:|---:|---:|---|---|',
    ]
    for row in panel_rows:
        lines.append(
            f"| {row['extortion']} | {row['delay']} | `{row['leader']}` | `{row['runner_up']}` | {float(row['paired_margin_ci_low_90']):.6f} | {float(row['paired_margin_ci_high_90']):.6f} | {float(row['largest_material_delta_supported_90']):.6f} | {float(row['smallest_equivalence_delta_supported_90']):.6f} | {row['delta_classifications']['0.005']} | {row['delta_classifications']['0.01']} |"
        )

    lines += [
        '',
        'Implementor implication:',
        '- Future rematch-world benchmark artifacts should publish a declared smallest effect of interest (`delta`) for the top-vs-runner-up gap, plus a practical-equivalence status alongside winner certification.',
        '- The compact decision lattice is then mechanical: if the 90% interval is above `delta`, ship a materially better leader; if it is inside `[-delta, delta]`, ship a practical tie; otherwise mark the panel undecided and only then consult the certification-budget field.',
        '- This keeps the archive smaller and more decision-relevant: some statistically real winners are too small to matter, and some uncertified flips are already cheap to close as practical ties without more runs.',
        '',
    ]
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')
    print(f'wrote {OUT_JSON}')
    print(f'wrote {OUT_MD}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
