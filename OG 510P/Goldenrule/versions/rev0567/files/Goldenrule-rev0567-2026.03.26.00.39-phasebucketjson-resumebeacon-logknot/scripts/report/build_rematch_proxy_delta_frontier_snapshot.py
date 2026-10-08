#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_materiality_gate_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_frontier_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_frontier_snapshot_20260306.md'
REFERENCE_DELTAS = [0.005, 0.01]


def _round(obj: object) -> object:
    if isinstance(obj, float):
        return round(obj, 6)
    if isinstance(obj, list):
        return [_round(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _round(v) for k, v in obj.items()}
    return obj


def _classify(material_cut: float, tie_cut: float, delta: float) -> str:
    if delta < material_cut:
        return 'material_leader'
    if delta >= tie_cut:
        return 'practical_tie'
    return 'undecided'


def main() -> int:
    src = json.loads(SRC_JSON.read_text(encoding='utf-8'))
    panel_rows: list[dict[str, object]] = []
    counts_by_delta = {str(delta): {'material_leader': 0, 'practical_tie': 0, 'undecided': 0} for delta in REFERENCE_DELTAS}

    closest_tie_panel: dict[str, object] | None = None
    widest_band_panel: dict[str, object] | None = None
    widest_band_width = -1.0
    tie_by_001 = 0
    material_at_001 = 0
    undecided_at_001 = 0
    certified_band_widths: list[float] = []

    for row in src['panel_rows']:
        material_cut = float(row['largest_material_delta_supported_90'])
        tie_cut = float(row['smallest_equivalence_delta_supported_90'])
        band_width = tie_cut - material_cut
        out_row = {
            'extortion': int(row['extortion']),
            'delay': int(row['delay']),
            'leader': row['leader'],
            'runner_up': row['runner_up'],
            'leader_certified_95_ci': bool(row['leader_certified_95_ci']),
            'leader_margin': float(row['leader_margin']),
            'material_leader_when_delta_lt': material_cut,
            'practical_tie_when_delta_ge': tie_cut,
            'undecided_delta_band_width': band_width,
            'delta_frontier_rule': {
                'material_leader': f'delta < {material_cut:.6f}',
                'undecided': f'{material_cut:.6f} <= delta < {tie_cut:.6f}',
                'practical_tie': f'delta >= {tie_cut:.6f}',
            },
        }
        panel_rows.append(out_row)

        for delta in REFERENCE_DELTAS:
            cls = _classify(material_cut, tie_cut, delta)
            counts_by_delta[str(delta)][cls] += 1
        cls_001 = _classify(material_cut, tie_cut, 0.01)
        if cls_001 == 'material_leader':
            material_at_001 += 1
        elif cls_001 == 'practical_tie':
            tie_by_001 += 1
        else:
            undecided_at_001 += 1

        if bool(row['leader_certified_95_ci']):
            certified_band_widths.append(band_width)
        if closest_tie_panel is None or tie_cut < float(closest_tie_panel['practical_tie_when_delta_ge']):
            closest_tie_panel = out_row
        if band_width > widest_band_width:
            widest_band_width = band_width
            widest_band_panel = out_row

    panel_rows.sort(key=lambda r: (int(r['extortion']), int(r['delay'])))
    mean_cert_band_width = sum(certified_band_widths) / len(certified_band_widths)

    assert closest_tie_panel is not None
    assert widest_band_panel is not None

    summary = {
        'focus': 'Compress rematch materiality decisions into per-panel delta frontiers so any declared smallest effect of interest can be applied without rerunning or archiving bulky multi-delta label tables.',
        'source_report': str(SRC_JSON.relative_to(ROOT)),
        'method_note': "Loaded each panel's largest material delta and smallest practical-tie delta from the materiality-gate snapshot, then treated the interval between them as the only delta-sensitive band. For any chosen delta: material_leader if delta is below the lower cutoff, practical_tie if delta is at or above the upper cutoff, undecided otherwise.",
        'headline_findings': {
            'tested_panels': len(panel_rows),
            'counts_by_delta': counts_by_delta,
            'panels_already_practical_ties_at_delta_0_01': tie_by_001,
            'panels_still_material_leaders_at_delta_0_01': material_at_001,
            'panels_undecided_at_delta_0_01': undecided_at_001,
            'smallest_practical_tie_delta_panel': closest_tie_panel,
            'widest_delta_sensitivity_band_panel': widest_band_panel,
            'mean_certified_panel_undecided_band_width': mean_cert_band_width,
            'interpretation': 'Each panel can be compressed to two delta cutoffs: a largest delta that still supports a materially better leader and a smallest delta that already supports a practical tie. Publishing those frontiers avoids storing or debating ad hoc labels at many different deltas.',
        },
        'panel_rows': panel_rows,
    }
    OUT_JSON.write_text(json.dumps(_round(summary), indent=2, sort_keys=True) + '\n', encoding='utf-8')

    lines = [
        '# Rematch-Proxy Delta-Frontier Snapshot (2026-03-06)',
        '',
        'Method:',
        '- loaded `largest_material_delta_supported_90` and `smallest_equivalence_delta_supported_90` from `artifacts/reports/rematch_proxy_materiality_gate_snapshot_20260306.json`',
        '- treated those two cutoffs as a compact frontier over the declared smallest effect of interest `delta`',
        '- classified each panel mechanically: `material_leader` for `delta` below the lower cutoff, `practical_tie` for `delta` at or above the upper cutoff, and `undecided` only in the band between them',
        '',
        'Main finding:',
        '- The current proxy does not need bulky per-delta materiality tables: every tested panel collapses to two thresholds.',
        f"- At `delta=0.01`, there are `{material_at_001}` material leaders, `{tie_by_001}` practical ties, and `{undecided_at_001}` undecided panels, and those counts are recoverable directly from the frontier cutoffs without recomputation.",
        f"- The earliest practical-tie closure is `ext{closest_tie_panel['extortion']}, delay{closest_tie_panel['delay']}` at `delta >= {float(closest_tie_panel['practical_tie_when_delta_ge']):.6f}`.",
        f"- The widest delta-sensitivity band is `ext{widest_band_panel['extortion']}, delay{widest_band_panel['delay']}` with width `{float(widest_band_panel['undecided_delta_band_width']):.6f}`; the mean width across already-certified panels is `{mean_cert_band_width:.6f}`.",
        '',
        'Panel summary:',
        '',
        '| extortion | delay | leader | runner-up | material if delta < | tie if delta >= | undecided band width |',
        '|---:|---:|---|---|---:|---:|---:|',
    ]
    for row in panel_rows:
        lines.append(
            f"| {row['extortion']} | {row['delay']} | `{row['leader']}` | `{row['runner_up']}` | {float(row['material_leader_when_delta_lt']):.6f} | {float(row['practical_tie_when_delta_ge']):.6f} | {float(row['undecided_delta_band_width']):.6f} |"
        )
    lines += [
        '',
        'Implementor implication:',
        '- Future rematch-world benchmark artifacts should publish per-panel delta frontiers (`largest_material_delta_supported`, `smallest_equivalence_delta_supported`) instead of only a few ad hoc classifications at hand-picked delta values.',
        '- Once those two numbers are present, downstream users can recover the decision for any declared `delta` without rerunning simulations or storing large threshold grids.',
        '- This keeps the archive tight while making threshold sensitivity explicit enough to prevent post hoc cherry-picking of an indifference zone.',
        '',
    ]
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')
    print(f'wrote {OUT_JSON}')
    print(f'wrote {OUT_MD}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
