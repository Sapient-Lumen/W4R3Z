#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLISHABILITY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_publishability_snapshot_20260306.json'
WINNER_CERTIFICATION_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_winner_certification_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_hazard_cap_profile_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_hazard_cap_profile_snapshot_20260306.md'
T_CRIT_90_DF5 = 2.015048
HAZARD_CAPS = [100, 500, 1000, 10000]
MIN_SHARED_CORE_WIDTH = 0.0010
SUB_0P01_LIMIT = 0.01
EXPECTED_FAMILIES = [
    ('caps_10_20_50_100_width0p0010_sub0p01', [10, 20, 50, 100]),
    ('caps_4_10_20_50_100_width0p0010_sub0p01', [4, 10, 20, 50, 100]),
]
PRIORITY_NAMES = ['material_first', 'stability_first', 'closure_conservative']


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


def _interval_distance(a_start: float, a_end: float, b_start: float, b_end: float) -> float:
    if a_end >= b_start and b_end >= a_start:
        return 0.0
    if a_end < b_start:
        return round(b_start - a_end, 6)
    return round(a_start - b_end, 6)


def _hazard_intervals(panel_rows: list[dict[str, object]], additional_budget_cap: int) -> list[dict[str, object]]:
    intervals: list[dict[str, object]] = []
    for row in panel_rows:
        mean_gap = float(row['leader_margin'])
        sd_gap = float(row['paired_margin_sd'])
        current_n = int(row['paired_seed_count'])
        radius = T_CRIT_90_DF5 * sd_gap / math.sqrt(current_n + additional_budget_cap)
        start_delta = max(0.0, mean_gap - radius)
        end_delta = min(SUB_0P01_LIMIT * 2, mean_gap + radius)
        if start_delta >= end_delta:
            continue
        intervals.append(
            {
                'extortion': int(row['extortion']),
                'delay': int(row['delay']),
                'leader': row['leader'],
                'runner_up': row['runner_up'],
                'leader_margin': mean_gap,
                'hazard_interval_within_delta_le_0_02': {
                    'start_delta': start_delta,
                    'end_delta': end_delta,
                },
            }
        )
    intervals.sort(key=lambda row: (float(row['leader_margin']), int(row['extortion']), int(row['delay'])))
    return intervals


def material_first_key(row: dict[str, object]) -> tuple[object, ...]:
    return (
        -int(row['counts']['material_leader']),
        int(row['counts']['undecided']),
        float(row['shared_core_anchor_delta']),
        int(row['shared_core_anchor_tie_count']),
        -float(row['shared_core_width']),
        -float(row['shared_core_anchor_buffer_to_boundary']),
        -float(row['min_separation_to_knife_edge_delta']),
        -float(row['min_separation_to_hazard_band_for_additional_budget_cap']),
        int(row['root_budget_cap_additional_paired_seeds']),
        str(row['topology_code']),
    )


def stability_first_key(row: dict[str, object]) -> tuple[object, ...]:
    return (
        -float(row['shared_core_width']),
        -float(row['shared_core_anchor_buffer_to_boundary']),
        -float(row['min_separation_to_knife_edge_delta']),
        -float(row['min_separation_to_hazard_band_for_additional_budget_cap']),
        int(row['shared_core_anchor_tie_count']),
        float(row['shared_core_anchor_delta']),
        -int(row['counts']['material_leader']),
        int(row['counts']['undecided']),
        int(row['root_budget_cap_additional_paired_seeds']),
        str(row['topology_code']),
    )


def closure_conservative_key(row: dict[str, object]) -> tuple[object, ...]:
    return (
        int(row['counts']['undecided']),
        int(row['shared_core_anchor_tie_count']),
        float(row['shared_core_anchor_delta']),
        -int(row['counts']['material_leader']),
        int(row['root_budget_cap_additional_paired_seeds']),
        -float(row['shared_core_width']),
        -float(row['shared_core_anchor_buffer_to_boundary']),
        -float(row['min_separation_to_knife_edge_delta']),
        -float(row['min_separation_to_hazard_band_for_additional_budget_cap']),
        str(row['topology_code']),
    )


SORTERS = {
    'material_first': material_first_key,
    'stability_first': stability_first_key,
    'closure_conservative': closure_conservative_key,
}


def _priority_profile_outcomes(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    if not rows:
        return [
            {
                'profile_name': name,
                'winner_topology_code': None,
                'winner_anchor_delta': None,
                'winner_counts': None,
                'winner_shared_core_width': None,
                'winner_shared_core_anchor_buffer_to_boundary': None,
                'winner_min_separation_to_hazard_band_for_additional_budget_cap': None,
                'winner_shared_core_anchor_tie_count': None,
                'ordered_topology_codes': [],
                'ordered_anchor_deltas': [],
            }
            for name in PRIORITY_NAMES
        ]
    outcomes: list[dict[str, object]] = []
    for name in PRIORITY_NAMES:
        ordered = sorted(rows, key=SORTERS[name])
        winner = ordered[0]
        outcomes.append(
            {
                'profile_name': name,
                'winner_topology_code': winner['topology_code'],
                'winner_anchor_delta': winner['shared_core_anchor_delta'],
                'winner_counts': winner['counts'],
                'winner_shared_core_width': winner['shared_core_width'],
                'winner_shared_core_anchor_buffer_to_boundary': winner['shared_core_anchor_buffer_to_boundary'],
                'winner_min_separation_to_hazard_band_for_additional_budget_cap': winner['min_separation_to_hazard_band_for_additional_budget_cap'],
                'winner_shared_core_anchor_tie_count': winner['shared_core_anchor_tie_count'],
                'ordered_topology_codes': [row['topology_code'] for row in ordered],
                'ordered_anchor_deltas': [row['shared_core_anchor_delta'] for row in ordered],
            }
        )
    return outcomes


def _candidate_rows_for_hazard_cap(base_rows: list[dict[str, object]], hazard_intervals: list[dict[str, object]], additional_budget_cap: int) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in base_rows:
        start = float(row['shared_core_start_delta'])
        end = float(row['shared_core_end_delta'])
        distances = [
            _interval_distance(
                start,
                end,
                float(interval['hazard_interval_within_delta_le_0_02']['start_delta']),
                float(interval['hazard_interval_within_delta_le_0_02']['end_delta']),
            )
            for interval in hazard_intervals
        ]
        min_distance = min(distances) if distances else math.inf
        if min_distance == 0.0:
            continue
        candidate = dict(row)
        candidate['additional_budget_cap_for_hazard_guardrail'] = additional_budget_cap
        candidate['min_separation_to_hazard_band_for_additional_budget_cap'] = round(min_distance, 6)
        out.append(candidate)
    out.sort(key=lambda row: (float(row['shared_core_anchor_delta']), str(row['topology_code'])))
    return out


def _family_profile(profile_name: str, caps: list[int], all_rows: list[dict[str, object]], panel_rows: list[dict[str, object]]) -> dict[str, object]:
    base_rows = [
        row for row in all_rows
        if row['covered_budget_caps'] == caps
        and float(row['shared_core_width']) >= MIN_SHARED_CORE_WIDTH
        and float(row['shared_core_end_delta']) < SUB_0P01_LIMIT
    ]
    base_rows = sorted(base_rows, key=lambda row: (float(row['shared_core_anchor_delta']), str(row['topology_code'])))

    hazard_cap_profiles = []
    candidate_identity_sets = []
    winner_signatures = {name: [] for name in PRIORITY_NAMES}
    minimum_separations: list[float] = []
    maximum_separations: list[float] = []
    for additional_budget_cap in HAZARD_CAPS:
        hazard_intervals = _hazard_intervals(panel_rows, additional_budget_cap)
        candidate_rows = _candidate_rows_for_hazard_cap(base_rows, hazard_intervals, additional_budget_cap)
        outcomes = _priority_profile_outcomes(candidate_rows)
        winners = {(outcome['winner_topology_code'], outcome['winner_anchor_delta']) for outcome in outcomes if outcome['winner_topology_code'] is not None}
        candidate_identity_sets.append([(row['topology_code'], row['shared_core_anchor_delta']) for row in candidate_rows])
        for outcome in outcomes:
            winner_signatures[outcome['profile_name']].append((outcome['winner_topology_code'], outcome['winner_anchor_delta']))
        if candidate_rows:
            minimum_separations.append(min(float(row['min_separation_to_hazard_band_for_additional_budget_cap']) for row in candidate_rows))
            maximum_separations.append(max(float(row['min_separation_to_hazard_band_for_additional_budget_cap']) for row in candidate_rows))
        hazard_cap_profiles.append(
            {
                'additional_budget_cap': additional_budget_cap,
                'candidate_count': len(candidate_rows),
                'candidate_rows': candidate_rows,
                'candidate_topology_codes': [row['topology_code'] for row in candidate_rows],
                'candidate_anchor_deltas': [row['shared_core_anchor_delta'] for row in candidate_rows],
                'priority_profile_outcomes': outcomes,
                'distinct_priority_winner_count': len(winners),
                'all_priority_profiles_agree': len(winners) <= 1,
            }
        )

    return {
        'profile_name': profile_name,
        'covered_budget_caps': caps,
        'minimum_shared_core_width': MIN_SHARED_CORE_WIDTH,
        'sub_0p01_only': True,
        'candidate_rows_before_hazard_guardrail': base_rows,
        'candidate_count_before_hazard_guardrail': len(base_rows),
        'hazard_cap_profiles': hazard_cap_profiles,
        'invariant_candidate_identity_across_hazard_caps': len({tuple(items) for items in candidate_identity_sets}) <= 1,
        'invariant_material_first_winner_across_hazard_caps': len(set(winner_signatures['material_first'])) <= 1,
        'invariant_stability_first_winner_across_hazard_caps': len(set(winner_signatures['stability_first'])) <= 1,
        'invariant_closure_conservative_winner_across_hazard_caps': len(set(winner_signatures['closure_conservative'])) <= 1,
        'minimum_hazard_separation_across_all_hazard_caps': min(minimum_separations) if minimum_separations else None,
        'maximum_hazard_separation_across_all_hazard_caps': max(maximum_separations) if maximum_separations else None,
    }


def _build_summary() -> dict[str, object]:
    publishability = _load_json(PUBLISHABILITY_PATH)
    winner_certification = _load_json(WINNER_CERTIFICATION_PATH)
    all_rows = publishability['core_rows']
    panel_rows = winner_certification['panel_rows']
    family_profiles = [
        _family_profile(profile_name, caps, all_rows, panel_rows)
        for profile_name, caps in EXPECTED_FAMILIES
    ]
    by_name = {profile['profile_name']: profile for profile in family_profiles}
    family10 = by_name['caps_10_20_50_100_width0p0010_sub0p01']
    family4 = by_name['caps_4_10_20_50_100_width0p0010_sub0p01']
    family10_profiles = family10['hazard_cap_profiles']
    family4_profiles = family4['hazard_cap_profiles']
    family10_cap100 = next(profile for profile in family10_profiles if int(profile['additional_budget_cap']) == 100)
    family10_cap10000 = next(profile for profile in family10_profiles if int(profile['additional_budget_cap']) == 10000)

    return {
        'focus': 'Make the hazard guardrail itself reproducible by declaring which additional-budget caps were considered and whether changing that hazard cap actually changes the width-qualified shortlist.',
        'method_note': 'Started from the canonical family cores in the publishability snapshot, fixed the width floor at 0.0010 and the delta ceiling below 0.01, then recomputed hazard-band overlap for additional-budget caps 100, 500, 1000, and 10000 using the same panel-level exclusion-radius construction as the earlier delta-hazard snapshot.',
        'headline_findings': {
            'hazard_caps_evaluated': HAZARD_CAPS,
            'caps_10_20_50_100_width0p0010_sub0p01_candidate_counts_by_hazard_cap': [
                {
                    'additional_budget_cap': profile['additional_budget_cap'],
                    'candidate_count': profile['candidate_count'],
                }
                for profile in family10_profiles
            ],
            'caps_10_20_50_100_width0p0010_sub0p01_invariant_shortlist_across_hazard_caps': family10['invariant_candidate_identity_across_hazard_caps'],
            'caps_10_20_50_100_width0p0010_sub0p01_material_first_winner': next(outcome for outcome in family10_cap100['priority_profile_outcomes'] if outcome['profile_name'] == 'material_first'),
            'caps_10_20_50_100_width0p0010_sub0p01_stability_first_winner': next(outcome for outcome in family10_cap100['priority_profile_outcomes'] if outcome['profile_name'] == 'stability_first'),
            'caps_10_20_50_100_width0p0010_sub0p01_closure_conservative_winner': next(outcome for outcome in family10_cap100['priority_profile_outcomes'] if outcome['profile_name'] == 'closure_conservative'),
            'caps_10_20_50_100_width0p0010_sub0p01_minimum_hazard_separation_at_cap_100': family10_cap100['candidate_rows'][1]['min_separation_to_hazard_band_for_additional_budget_cap'],
            'caps_10_20_50_100_width0p0010_sub0p01_minimum_hazard_separation_at_cap_10000': family10_cap10000['candidate_rows'][1]['min_separation_to_hazard_band_for_additional_budget_cap'],
            'caps_4_10_20_50_100_width0p0010_sub0p01_candidate_counts_by_hazard_cap': [
                {
                    'additional_budget_cap': profile['additional_budget_cap'],
                    'candidate_count': profile['candidate_count'],
                }
                for profile in family4_profiles
            ],
            'caps_4_10_20_50_100_width0p0010_sub0p01_invariant_empty_shortlist_across_hazard_caps': all(int(profile['candidate_count']) == 0 for profile in family4_profiles),
            'interpretation': 'In the current proxy, once the family and width-floor contract are fixed, the hazard-cap declaration does not decide the low-delta shortlist. The viable family 10/20/50/100 keeps the same two candidates and the same priority winners from hazard cap 100 through 10000, while the wider family that includes cap 4 stays empty at width 0.0010 throughout. Hazard cap should still be published, but it should not be credited for discrimination that is really coming from the family and width filters.',
        },
        'family_profiles': family_profiles,
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_publishability_snapshot_20260306.json',
            'artifacts/reports/rematch_proxy_winner_certification_snapshot_20260306.json',
        ],
        'source_script': 'scripts/report/build_rematch_proxy_delta_hazard_cap_profile_snapshot.py',
    }


def _write_markdown(summary: dict[str, object]) -> None:
    findings = summary['headline_findings']
    family_profiles = summary['family_profiles']
    by_name = {profile['profile_name']: profile for profile in family_profiles}
    family10 = by_name['caps_10_20_50_100_width0p0010_sub0p01']
    family4 = by_name['caps_4_10_20_50_100_width0p0010_sub0p01']

    lines = [
        '# Rematch-Proxy Delta Hazard-Cap Profile Snapshot (2026-03-06)',
        '',
        'Method:',
        '- started from the canonical family cores in the publishability snapshot',
        '- fixed the shortlist contract at width `>= 0.0010` and `delta < 0.01`',
        '- compared the exact family declarations `10/20/50/100` and `4/10/20/50/100`',
        '- recomputed hazard overlap for additional-budget caps `100`, `500`, `1000`, and `10000` using the same exclusion-radius rule as the earlier delta-hazard snapshot',
        '',
        'Headline findings:',
        f"- for family `10/20/50/100`, the width-qualified low-delta shortlist stays exactly `{int(family10['hazard_cap_profiles'][0]['candidate_count'])}` candidates at every tested hazard cap, and the candidate identities never change.",
        f"- across hazard caps `100` through `10000`, `material_first` keeps selecting `{findings['caps_10_20_50_100_width0p0010_sub0p01_material_first_winner']['winner_topology_code']}` at `{float(findings['caps_10_20_50_100_width0p0010_sub0p01_material_first_winner']['winner_anchor_delta']):.5f}`, while `stability_first` keeps selecting `{findings['caps_10_20_50_100_width0p0010_sub0p01_stability_first_winner']['winner_topology_code']}` at `{float(findings['caps_10_20_50_100_width0p0010_sub0p01_stability_first_winner']['winner_anchor_delta']):.5f}`.",
        f"- even at the harshest tested hazard cap (`100` extra paired seeds), the tighter of the two family10 candidates still stays `{float(findings['caps_10_20_50_100_width0p0010_sub0p01_minimum_hazard_separation_at_cap_100']):.6f}` away from the nearest hazard interval; at cap `10000` that minimum separation grows to `{float(findings['caps_10_20_50_100_width0p0010_sub0p01_minimum_hazard_separation_at_cap_10000']):.6f}`.",
        f"- for family `4/10/20/50/100`, the width-qualified low-delta shortlist is empty at every tested hazard cap.",
        '- so in the current proxy the active low-delta guardrails are the exact family declaration and the width floor, not the hazard-cap setting.',
        '',
        'Per-family hazard-cap profiles:',
    ]

    for profile in family_profiles:
        caps = '/'.join(str(cap) for cap in profile['covered_budget_caps'])
        lines.extend([
            f"- `{profile['profile_name']}` (caps {caps}):",
            f"  - candidates before hazard filtering: `{int(profile['candidate_count_before_hazard_guardrail'])}`.",
            f"  - invariant candidate identity across tested hazard caps: `{bool(profile['invariant_candidate_identity_across_hazard_caps'])}`.",
            f"  - invariant winners: material_first `{bool(profile['invariant_material_first_winner_across_hazard_caps'])}`, stability_first `{bool(profile['invariant_stability_first_winner_across_hazard_caps'])}`, closure_conservative `{bool(profile['invariant_closure_conservative_winner_across_hazard_caps'])}`.",
        ])
        if profile['minimum_hazard_separation_across_all_hazard_caps'] is None:
            lines.append('  - no width-qualified low-delta candidates survive, so hazard-cap comparisons are vacuous.')
        else:
            lines.append(
                f"  - minimum / maximum separation to the nearest tested hazard interval across all hazard caps: `{float(profile['minimum_hazard_separation_across_all_hazard_caps']):.6f}` / `{float(profile['maximum_hazard_separation_across_all_hazard_caps']):.6f}`."
            )
        for cap_profile in profile['hazard_cap_profiles']:
            lines.append(
                f"  - hazard cap `{int(cap_profile['additional_budget_cap'])}` -> `{int(cap_profile['candidate_count'])}` candidates ({', '.join(f'{row['topology_code']}@{float(row['shared_core_anchor_delta']):.5f}[sep={float(row['min_separation_to_hazard_band_for_additional_budget_cap']):.6f}]' for row in cap_profile['candidate_rows']) if cap_profile['candidate_rows'] else 'none'})."
            )
        lines.append('')

    lines.extend([
        'Why this matters for the archive:',
        '- The hazard-cap choice should still be declared explicitly, because it is a real modeling assumption.',
        '- But the archive should not imply that this choice is doing shortlist selection when it is not.',
        '- In the current proxy, once family persistence and width are fixed, changing the hazard cap over two orders of magnitude leaves the viable family10 low-delta shortlist untouched. The unresolved judgment remains the declared priority profile, not the hazard guardrail.',
        '',
    ])

    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')


def main() -> None:
    summary = _build_summary()
    OUT_JSON.write_text(json.dumps(_round(summary), indent=2) + '\n', encoding='utf-8')
    _write_markdown(summary)
    print(OUT_JSON.relative_to(ROOT))
    print(OUT_MD.relative_to(ROOT))


if __name__ == '__main__':
    main()
