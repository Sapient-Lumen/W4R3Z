#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLISHABILITY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_publishability_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_preference_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_preference_snapshot_20260306.md'

PROFILE_NAME = 'family4_width0p0010_hazard1000_sub0p01'


def _round(obj: object) -> object:
    if isinstance(obj, float):
        return round(obj, 6)
    if isinstance(obj, list):
        return [_round(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _round(v) for k, v in obj.items()}
    return obj


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding='utf-8'))


def _strict_sub_0p01_candidates() -> list[dict[str, object]]:
    publishability = _load_json(PUBLISHABILITY_PATH)
    for profile in publishability['guardrail_profiles']:
        if profile['profile_name'] == PROFILE_NAME:
            rows = profile['candidate_rows']
            rows.sort(key=lambda row: (float(row['shared_core_anchor_delta']), str(row['topology_code'])))
            return rows
    raise SystemExit(f'missing profile {PROFILE_NAME}')


def _dominates(a: dict[str, object], b: dict[str, object]) -> bool:
    comparisons = {
        'lower_anchor_delta': float(a['shared_core_anchor_delta']) <= float(b['shared_core_anchor_delta']),
        'wider_shared_core': float(a['shared_core_width']) >= float(b['shared_core_width']),
        'larger_anchor_buffer': float(a['shared_core_anchor_buffer_to_boundary']) >= float(b['shared_core_anchor_buffer_to_boundary']),
        'larger_knife_edge_separation': float(a['min_separation_to_knife_edge_delta']) >= float(b['min_separation_to_knife_edge_delta']),
        'larger_hazard_separation': float(a['min_separation_to_hazard_band_for_additional_budget_cap_1000']) >= float(b['min_separation_to_hazard_band_for_additional_budget_cap_1000']),
        'more_material_leaders': int(a['counts']['material_leader']) >= int(b['counts']['material_leader']),
        'fewer_undecided': int(a['counts']['undecided']) <= int(b['counts']['undecided']),
        'no_more_anchor_ties': int(a['shared_core_anchor_tie_count']) <= int(b['shared_core_anchor_tie_count']),
        'no_higher_root_budget_cap': int(a['root_budget_cap_additional_paired_seeds']) <= int(b['root_budget_cap_additional_paired_seeds']),
    }
    if not all(comparisons.values()):
        return False
    strictly_better = (
        float(a['shared_core_anchor_delta']) < float(b['shared_core_anchor_delta'])
        or float(a['shared_core_width']) > float(b['shared_core_width'])
        or float(a['shared_core_anchor_buffer_to_boundary']) > float(b['shared_core_anchor_buffer_to_boundary'])
        or float(a['min_separation_to_knife_edge_delta']) > float(b['min_separation_to_knife_edge_delta'])
        or float(a['min_separation_to_hazard_band_for_additional_budget_cap_1000']) > float(b['min_separation_to_hazard_band_for_additional_budget_cap_1000'])
        or int(a['counts']['material_leader']) > int(b['counts']['material_leader'])
        or int(a['counts']['undecided']) < int(b['counts']['undecided'])
        or int(a['shared_core_anchor_tie_count']) < int(b['shared_core_anchor_tie_count'])
        or int(a['root_budget_cap_additional_paired_seeds']) < int(b['root_budget_cap_additional_paired_seeds'])
    )
    return strictly_better


PROFILES: list[dict[str, object]] = [
    {
        'profile_name': 'material_first',
        'priority_explanation': 'Prefer the smallest delta that preserves the most material-leader panels and the fewest unresolved panels; only then use robustness fields as tie-breakers.',
        'sort_key': lambda row: (
            -int(row['counts']['material_leader']),
            int(row['counts']['undecided']),
            float(row['shared_core_anchor_delta']),
            int(row['shared_core_anchor_tie_count']),
            -float(row['shared_core_width']),
            -float(row['shared_core_anchor_buffer_to_boundary']),
            -float(row['min_separation_to_knife_edge_delta']),
            -float(row['min_separation_to_hazard_band_for_additional_budget_cap_1000']),
            int(row['root_budget_cap_additional_paired_seeds']),
            str(row['topology_code']),
        ),
    },
    {
        'profile_name': 'stability_first',
        'priority_explanation': 'Prefer the most robust shared core by width and interior buffer, then maximize distance from knife-edge deltas before considering how low the anchor sits.',
        'sort_key': lambda row: (
            -float(row['shared_core_width']),
            -float(row['shared_core_anchor_buffer_to_boundary']),
            -float(row['min_separation_to_knife_edge_delta']),
            -float(row['min_separation_to_hazard_band_for_additional_budget_cap_1000']),
            int(row['shared_core_anchor_tie_count']),
            float(row['shared_core_anchor_delta']),
            -int(row['counts']['material_leader']),
            int(row['counts']['undecided']),
            int(row['root_budget_cap_additional_paired_seeds']),
            str(row['topology_code']),
        ),
    },
    {
        'profile_name': 'closure_conservative',
        'priority_explanation': 'Prefer the anchor with fewer unresolved panels and a unique discrete center, then keep delta as low as possible while preserving material panels.',
        'sort_key': lambda row: (
            int(row['counts']['undecided']),
            int(row['shared_core_anchor_tie_count']),
            float(row['shared_core_anchor_delta']),
            -int(row['counts']['material_leader']),
            int(row['root_budget_cap_additional_paired_seeds']),
            -float(row['shared_core_width']),
            -float(row['shared_core_anchor_buffer_to_boundary']),
            -float(row['min_separation_to_knife_edge_delta']),
            -float(row['min_separation_to_hazard_band_for_additional_budget_cap_1000']),
            str(row['topology_code']),
        ),
    },
]


def _profile_outcomes(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    outcomes: list[dict[str, object]] = []
    for profile in PROFILES:
        ordered = sorted(rows, key=profile['sort_key'])
        winner = ordered[0]
        outcomes.append(
            {
                'profile_name': profile['profile_name'],
                'priority_explanation': profile['priority_explanation'],
                'winner_topology_code': winner['topology_code'],
                'winner_anchor_delta': winner['shared_core_anchor_delta'],
                'winner_counts': winner['counts'],
                'winner_shared_core_width': winner['shared_core_width'],
                'winner_shared_core_anchor_buffer_to_boundary': winner['shared_core_anchor_buffer_to_boundary'],
                'winner_min_separation_to_knife_edge_delta': winner['min_separation_to_knife_edge_delta'],
                'winner_min_separation_to_hazard_band_for_additional_budget_cap_1000': winner['min_separation_to_hazard_band_for_additional_budget_cap_1000'],
                'winner_shared_core_anchor_tie_count': winner['shared_core_anchor_tie_count'],
                'ordered_topology_codes': [row['topology_code'] for row in ordered],
                'ordered_anchor_deltas': [row['shared_core_anchor_delta'] for row in ordered],
            }
        )
    return outcomes


def _tradeoff_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for i, left in enumerate(rows):
        dominated_by = []
        better_than = []
        favorable_axes: list[str] = []
        unfavorable_axes: list[str] = []
        incomparable_with: list[str] = []
        for j, right in enumerate(rows):
            if i == j:
                continue
            if _dominates(right, left):
                dominated_by.append(right['topology_code'])
            elif _dominates(left, right):
                better_than.append(right['topology_code'])
            else:
                incomparable_with.append(right['topology_code'])
                if float(left['shared_core_anchor_delta']) < float(right['shared_core_anchor_delta']):
                    favorable_axes.append(f'lower_delta_than_{right["topology_code"]}')
                elif float(left['shared_core_anchor_delta']) > float(right['shared_core_anchor_delta']):
                    unfavorable_axes.append(f'lower_delta_than_{right["topology_code"]}')
                if int(left['counts']['material_leader']) > int(right['counts']['material_leader']):
                    favorable_axes.append(f'more_material_leaders_than_{right["topology_code"]}')
                elif int(left['counts']['material_leader']) < int(right['counts']['material_leader']):
                    unfavorable_axes.append(f'more_material_leaders_than_{right["topology_code"]}')
                if int(left['counts']['undecided']) < int(right['counts']['undecided']):
                    favorable_axes.append(f'fewer_undecided_than_{right["topology_code"]}')
                elif int(left['counts']['undecided']) > int(right['counts']['undecided']):
                    unfavorable_axes.append(f'fewer_undecided_than_{right["topology_code"]}')
                if float(left['shared_core_width']) > float(right['shared_core_width']):
                    favorable_axes.append(f'wider_shared_core_than_{right["topology_code"]}')
                elif float(left['shared_core_width']) < float(right['shared_core_width']):
                    unfavorable_axes.append(f'wider_shared_core_than_{right["topology_code"]}')
                if float(left['shared_core_anchor_buffer_to_boundary']) > float(right['shared_core_anchor_buffer_to_boundary']):
                    favorable_axes.append(f'larger_anchor_buffer_than_{right["topology_code"]}')
                elif float(left['shared_core_anchor_buffer_to_boundary']) < float(right['shared_core_anchor_buffer_to_boundary']):
                    unfavorable_axes.append(f'larger_anchor_buffer_than_{right["topology_code"]}')
                if float(left['min_separation_to_knife_edge_delta']) > float(right['min_separation_to_knife_edge_delta']):
                    favorable_axes.append(f'larger_knife_edge_separation_than_{right["topology_code"]}')
                elif float(left['min_separation_to_knife_edge_delta']) < float(right['min_separation_to_knife_edge_delta']):
                    unfavorable_axes.append(f'larger_knife_edge_separation_than_{right["topology_code"]}')
        out.append(
            {
                'topology_code': left['topology_code'],
                'anchor_delta': left['shared_core_anchor_delta'],
                'counts': left['counts'],
                'shared_core_width': left['shared_core_width'],
                'shared_core_anchor_buffer_to_boundary': left['shared_core_anchor_buffer_to_boundary'],
                'min_separation_to_knife_edge_delta': left['min_separation_to_knife_edge_delta'],
                'min_separation_to_hazard_band_for_additional_budget_cap_1000': left['min_separation_to_hazard_band_for_additional_budget_cap_1000'],
                'shared_core_anchor_tie_count': left['shared_core_anchor_tie_count'],
                'root_budget_cap_additional_paired_seeds': left['root_budget_cap_additional_paired_seeds'],
                'dominated_by': dominated_by,
                'dominates': better_than,
                'pareto_nondominated': not dominated_by,
                'incomparable_with': incomparable_with,
                'favorable_axes_vs_incomparables': favorable_axes,
                'unfavorable_axes_vs_incomparables': unfavorable_axes,
            }
        )
    return out


def _build_summary(rows: list[dict[str, object]]) -> dict[str, object]:
    tradeoff_rows = _tradeoff_rows(rows)
    pareto_rows = [row for row in tradeoff_rows if row['pareto_nondominated']]
    profile_outcomes = _profile_outcomes(rows)
    winners = {outcome['winner_topology_code'] for outcome in profile_outcomes}
    return {
        'focus': 'Turn the strict low-delta rematch shortlist into a reproducible choice contract by exposing which anchors are genuinely non-dominated and which declared priority profiles select each one.',
        'headline_findings': {
            'strict_sub0p01_candidate_count': len(rows),
            'strict_sub0p01_pareto_nondominated_count': len(pareto_rows),
            'strict_sub0p01_unique_dominant_anchor_exists': len(pareto_rows) == 1,
            'material_first_winner': next(outcome for outcome in profile_outcomes if outcome['profile_name'] == 'material_first'),
            'stability_first_winner': next(outcome for outcome in profile_outcomes if outcome['profile_name'] == 'stability_first'),
            'closure_conservative_winner': next(outcome for outcome in profile_outcomes if outcome['profile_name'] == 'closure_conservative'),
            'distinct_profile_winner_count': len(winners),
            'interpretation': 'The strict sub-0.01 shortlist does not collapse to one universally best anchor. Both surviving candidates are Pareto-nondominated: the lower-delta core preserves more material-leader panels and fewer unresolved panels, while the higher-delta core offers more shared-core width and interior buffer. A publishable scalar constant therefore needs an explicit priority profile, not an implicit claim that the shortlist secretly has a unique winner.',
        },
        'method_note': 'Started from the strict sub-0.01 publishability shortlist (family persistence across caps 10/20/50/100, width floor 0.0010, and no overlap with the >1000-extra-seed hazard bands). Compared the surviving anchors on delta level, shared-core robustness, and panel-status counts, then reported Pareto nondominance plus outcomes under three declared lexicographic priority profiles.',
        'candidate_rows': rows,
        'tradeoff_rows': tradeoff_rows,
        'priority_profile_outcomes': profile_outcomes,
        'source_report': 'artifacts/reports/rematch_proxy_delta_publishability_snapshot_20260306.json',
        'source_script': 'scripts/report/build_rematch_proxy_delta_preference_snapshot.py',
    }


def _write_markdown(summary: dict[str, object]) -> None:
    findings = summary['headline_findings']
    tradeoff_rows = summary['tradeoff_rows']
    profile_outcomes = summary['priority_profile_outcomes']
    lines = [
        '# Rematch-Proxy Delta Preference Snapshot (2026-03-06)',
        '',
        'Method:',
        '- started from the strict sub-`0.01` publishability shortlist (`family4_width0p0010_hazard1000_sub0p01`)',
        '- compared the surviving anchors on delta level, panel-status counts, shared-core width, anchor buffer, and separation from knife-edge / hazard deltas',
        '- marked Pareto-nondominated anchors rather than forcing a synthetic scalar score',
        '- then evaluated three declared lexicographic priority profiles so future inheritors can make the choice reproducibly',
        '',
        'Headline findings:',
        f"- the strict sub-`0.01` shortlist contains `{findings['strict_sub0p01_candidate_count']}` candidates, and `{findings['strict_sub0p01_pareto_nondominated_count']}` of them are Pareto-nondominated.",
        f"- a unique dominant anchor exists: `{findings['strict_sub0p01_unique_dominant_anchor_exists']}`.",
        f"- the `material_first` profile selects `{findings['material_first_winner']['winner_topology_code']}` at `{float(findings['material_first_winner']['winner_anchor_delta']):.5f}`.",
        f"- the `stability_first` profile selects `{findings['stability_first_winner']['winner_topology_code']}` at `{float(findings['stability_first_winner']['winner_anchor_delta']):.5f}`.",
        f"- the `closure_conservative` profile selects `{findings['closure_conservative_winner']['winner_topology_code']}` at `{float(findings['closure_conservative_winner']['winner_anchor_delta']):.5f}`.",
        f"- across the three declared profiles there are `{findings['distinct_profile_winner_count']}` distinct winners, so the shortlist only becomes a scalar benchmark constant after the archive declares which priority order it is actually using.",
        '',
        'Candidate tradeoffs:',
    ]
    for row in tradeoff_rows:
        counts = row['counts']
        lines.append(
            f"- `{row['topology_code']}` at `{float(row['anchor_delta']):.5f}`: `M={int(counts['material_leader'])}, T={int(counts['practical_tie'])}, U={int(counts['undecided'])}`, width `{float(row['shared_core_width']):.5f}`, buffer `{float(row['shared_core_anchor_buffer_to_boundary']):.5f}`, knife-edge separation `{float(row['min_separation_to_knife_edge_delta']):.6f}`, hazard separation `{float(row['min_separation_to_hazard_band_for_additional_budget_cap_1000']):.6f}`, Pareto-nondominated `{bool(row['pareto_nondominated'])}`."
        )
    lines.extend(['', 'Priority profile outcomes:'])
    for outcome in profile_outcomes:
        counts = outcome['winner_counts']
        lines.append(
            f"- `{outcome['profile_name']}` -> `{outcome['winner_topology_code']}` at `{float(outcome['winner_anchor_delta']):.5f}` (`M={int(counts['material_leader'])}, T={int(counts['practical_tie'])}, U={int(counts['undecided'])}`, width `{float(outcome['winner_shared_core_width']):.5f}`, buffer `{float(outcome['winner_shared_core_anchor_buffer_to_boundary']):.5f}`)."
        )
    lines.extend(
        [
            '',
            'Why this matters for the archive:',
            '- A guardrail shortlist is not yet a unique recommendation. The final anchor still depends on which scientific virtue is primary: lower declared practical margin, fewer unresolved panels, or more geometric robustness against later budget revisions.',
            '- That priority order should be published explicitly. Otherwise the archive is still performing hidden judgment, just one layer later than before.',
            '- In the current proxy, a defensible default is to export the whole strict shortlist plus the declared priority profile that would break the tie, rather than pretending the tie never existed.',
            '',
        ]
    )
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')


def main() -> None:
    rows = _strict_sub_0p01_candidates()
    summary = _build_summary(rows)
    OUT_JSON.write_text(json.dumps(_round(summary), indent=2, sort_keys=True) + '\n', encoding='utf-8')
    _write_markdown(summary)
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
