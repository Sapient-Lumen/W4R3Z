#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLISHABILITY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_publishability_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_width_floor_plateau_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_width_floor_plateau_snapshot_20260306.md'


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


def _profile_name(caps: list[int]) -> str:
    return 'caps_' + '_'.join(str(cap) for cap in caps) + '_sub0p01_hazard1000'


PROFILES: list[dict[str, object]] = [
    {
        'profile_name': 'material_first',
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


def _priority_profile_outcomes(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    outcomes: list[dict[str, object]] = []
    for profile in PROFILES:
        ordered = sorted(rows, key=profile['sort_key'])
        winner = ordered[0]
        outcomes.append(
            {
                'profile_name': profile['profile_name'],
                'winner_topology_code': winner['topology_code'],
                'winner_anchor_delta': winner['shared_core_anchor_delta'],
                'winner_counts': winner['counts'],
                'winner_shared_core_width': winner['shared_core_width'],
                'winner_shared_core_anchor_buffer_to_boundary': winner['shared_core_anchor_buffer_to_boundary'],
                'winner_shared_core_anchor_tie_count': winner['shared_core_anchor_tie_count'],
                'ordered_topology_codes': [row['topology_code'] for row in ordered],
                'ordered_anchor_deltas': [row['shared_core_anchor_delta'] for row in ordered],
            }
        )
    return outcomes


def _rows() -> list[dict[str, object]]:
    publishability = _load_json(PUBLISHABILITY_PATH)
    rows = [
        row for row in publishability['core_rows']
        if bool(row['below_delta_0p01']) and not bool(row['overlaps_hazard_band_for_additional_budget_cap_1000'])
    ]
    rows.sort(key=lambda row: (tuple(row['covered_budget_caps']), float(row['shared_core_anchor_delta']), str(row['topology_code'])))
    return rows


def _build_plateaus(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_family: dict[tuple[int, ...], list[dict[str, object]]] = {}
    for row in rows:
        by_family.setdefault(tuple(row['covered_budget_caps']), []).append(row)

    family_profiles: list[dict[str, object]] = []
    for caps, family_rows in sorted(by_family.items()):
        cutoffs = sorted({float(row['shared_core_width']) for row in family_rows})
        plateau_rows: list[dict[str, object]] = []
        previous_cutoff = 0.0
        for index, cutoff in enumerate(cutoffs):
            candidate_rows = sorted(
                [row for row in family_rows if float(row['shared_core_width']) >= cutoff],
                key=lambda row: (float(row['shared_core_anchor_delta']), str(row['topology_code'])),
            )
            priority_profile_outcomes = _priority_profile_outcomes(candidate_rows)
            distinct_winners = sorted({(outcome['winner_topology_code'], float(outcome['winner_anchor_delta'])) for outcome in priority_profile_outcomes})
            plateau_rows.append(
                {
                    'plateau_index': index + 1,
                    'width_floor_lower_exclusive': previous_cutoff if index > 0 else 0.0,
                    'width_floor_lower_inclusive': index == 0,
                    'width_floor_upper_inclusive': cutoff,
                    'width_floor_span': cutoff - previous_cutoff,
                    'candidate_count': len(candidate_rows),
                    'candidate_rows': candidate_rows,
                    'candidate_topology_codes': [row['topology_code'] for row in candidate_rows],
                    'candidate_anchor_deltas': [row['shared_core_anchor_delta'] for row in candidate_rows],
                    'distinct_candidate_topology_count': len({str(row['topology_code']) for row in candidate_rows}),
                    'priority_profile_outcomes': priority_profile_outcomes,
                    'distinct_priority_winner_count': len(distinct_winners),
                    'all_priority_profiles_agree': len(distinct_winners) == 1,
                    'contains_material_core_candidate': any(int(row['counts']['material_leader']) > 0 for row in candidate_rows),
                }
            )
            previous_cutoff = cutoff

        family_profiles.append(
            {
                'profile_name': _profile_name(list(caps)),
                'covered_budget_caps': list(caps),
                'candidate_rows_before_width_floor': sorted(
                    family_rows,
                    key=lambda row: (float(row['shared_core_anchor_delta']), str(row['topology_code'])),
                ),
                'plateau_rows': plateau_rows,
            }
        )
    return family_profiles


def _select_plateau(profile: dict[str, object], candidate_count: int) -> dict[str, object]:
    eligible = [row for row in profile['plateau_rows'] if int(row['candidate_count']) == candidate_count]
    if not eligible:
        raise ValueError(f'no plateau with candidate_count == {candidate_count} for {profile["profile_name"]}')
    return max(
        eligible,
        key=lambda row: (float(row['width_floor_span']), float(row['width_floor_upper_inclusive']), -float(row['width_floor_lower_exclusive'])),
    )


def _build_summary(rows: list[dict[str, object]]) -> dict[str, object]:
    family_profiles = _build_plateaus(rows)
    by_name = {profile['profile_name']: profile for profile in family_profiles}

    family10 = by_name['caps_10_20_50_100_sub0p01_hazard1000']
    family4 = by_name['caps_4_10_20_50_100_sub0p01_hazard1000']
    family10_two = _select_plateau(family10, 2)
    family4_two = _select_plateau(family4, 2)
    family10_one = _select_plateau(family10, 1)
    family4_one = _select_plateau(family4, 1)

    material_first = next(outcome for outcome in family10_two['priority_profile_outcomes'] if outcome['profile_name'] == 'material_first')
    stability_first = next(outcome for outcome in family10_two['priority_profile_outcomes'] if outcome['profile_name'] == 'stability_first')
    closure_conservative = next(outcome for outcome in family10_two['priority_profile_outcomes'] if outcome['profile_name'] == 'closure_conservative')

    return {
        'focus': 'Expose width-floor plateaus for exact budget families so the archive can publish a stable shortlist band instead of pretending one hand-picked minimum-width threshold is canonical.',
        'method_note': 'Started from the hazard-clear sub-0.01 family cores in the publishability snapshot. For each exact budget-family declaration already present in the data, sorted the surviving shared-core widths and converted those cutoffs into width-floor plateaus on which the shortlist is constant. Reported plateau span, surviving anchors, and the winner under the same three declared priority profiles used in the strict shortlist preference pass.',
        'headline_findings': {
            'caps_10_20_50_100_largest_two_candidate_plateau': family10_two,
            'caps_4_10_20_50_100_largest_two_candidate_plateau': family4_two,
            'caps_10_20_50_100_largest_one_candidate_plateau': family10_one,
            'caps_4_10_20_50_100_largest_one_candidate_plateau': family4_one,
            'two_candidate_plateau_span_ratio_family10_over_family4': round(float(family10_two['width_floor_span']) / float(family4_two['width_floor_span']), 6),
            'family10_material_first_winner_on_two_candidate_plateau': material_first,
            'family10_stability_first_winner_on_two_candidate_plateau': stability_first,
            'family10_closure_conservative_winner_on_two_candidate_plateau': closure_conservative,
            'family4_tttmmmmmu_survives_only_up_to_width_floor': next(
                float(row['shared_core_width'])
                for row in family4['candidate_rows_before_width_floor']
                if str(row['topology_code']) == 'TTTMMMMMU'
            ),
            'interpretation': 'The width-floor decision should be published as a band choice, not as one lucky scalar floor. In the current proxy the 10/20/50/100 family has a broad two-candidate plateau where the shortlist is unchanged, while the 4/10/20/50/100 family has only a thin micro-band before all viable low-delta candidates disappear. Choosing a floor inside the family10 plateau still does not resolve the final anchor choice; the remaining disagreement is now purely about declared priority profile.',
        },
        'family_profiles': family_profiles,
        'source_report': 'artifacts/reports/rematch_proxy_delta_publishability_snapshot_20260306.json',
        'source_script': 'scripts/report/build_rematch_proxy_delta_width_floor_plateau_snapshot.py',
    }


def _write_markdown(summary: dict[str, object]) -> None:
    findings = summary['headline_findings']
    family_profiles = summary['family_profiles']
    family10_two = findings['caps_10_20_50_100_largest_two_candidate_plateau']
    family4_two = findings['caps_4_10_20_50_100_largest_two_candidate_plateau']
    material_first = findings['family10_material_first_winner_on_two_candidate_plateau']
    stability_first = findings['family10_stability_first_winner_on_two_candidate_plateau']
    closure_conservative = findings['family10_closure_conservative_winner_on_two_candidate_plateau']

    lines = [
        '# Rematch-Proxy Delta Width-Floor Plateau Snapshot (2026-03-06)',
        '',
        'Method:',
        '- started from the hazard-clear sub-`0.01` family cores already exposed in the publishability snapshot',
        '- grouped them by exact declared budget family rather than mixing caps implicitly',
        '- converted the observed shared-core widths into exact width-floor plateaus on which the shortlist is unchanged',
        '- reported the surviving anchors and the declared priority-profile winners on each plateau',
        '',
        'Headline findings:',
        f"- the exact family `10/20/50/100` has a largest two-candidate plateau on `{float(family10_two['width_floor_lower_exclusive']):.5f} < floor <= {float(family10_two['width_floor_upper_inclusive']):.5f}` with span `{float(family10_two['width_floor_span']):.5f}`; throughout that whole band the shortlist is exactly `{family10_two['candidate_topology_codes'][0]}` at `{float(family10_two['candidate_anchor_deltas'][0]):.5f}` plus `{family10_two['candidate_topology_codes'][1]}` at `{float(family10_two['candidate_anchor_deltas'][1]):.5f}`.",
        f"- the exact family `4/10/20/50/100` has a largest two-candidate plateau on `{float(family4_two['width_floor_lower_exclusive']):.5f} < floor <= {float(family4_two['width_floor_upper_inclusive']):.5f}` with span `{float(family4_two['width_floor_span']):.5f}`; both survivors there are fragmented `{family4_two['candidate_topology_codes'][0]}` practical-tie anchors at `{float(family4_two['candidate_anchor_deltas'][0]):.5f}` and `{float(family4_two['candidate_anchor_deltas'][1]):.5f}`.",
        f"- the family10 two-candidate plateau is `{float(findings['two_candidate_plateau_span_ratio_family10_over_family4']):.3f}x` wider than the family4 one.",
        f"- across the entire family10 two-candidate plateau, `material_first` selects `{material_first['winner_topology_code']}` at `{float(material_first['winner_anchor_delta']):.5f}`, `stability_first` selects `{stability_first['winner_topology_code']}` at `{float(stability_first['winner_anchor_delta']):.5f}`, and `closure_conservative` again selects `{closure_conservative['winner_topology_code']}` at `{float(closure_conservative['winner_anchor_delta']):.5f}`.",
        f"- in the `4/10/20/50/100` family, the lone `TTTMMMMMU` material-core anchor survives only up to width floor `{float(findings['family4_tttmmmmmu_survives_only_up_to_width_floor']):.5f}`; above that, only practical-tie fragments remain before the shortlist disappears entirely.",
        '',
        'Per-family plateau map:',
    ]
    for profile in family_profiles:
        caps_label = '/'.join(str(cap) for cap in profile['covered_budget_caps'])
        lines.append(f"- `{profile['profile_name']}` (caps {caps_label}):")
        for plateau in profile['plateau_rows']:
            winners = ', '.join(
                f"{outcome['profile_name']}->{outcome['winner_topology_code']}@{float(outcome['winner_anchor_delta']):.5f}"
                for outcome in plateau['priority_profile_outcomes']
            )
            band = (
                f"0.00000 <= floor <= {float(plateau['width_floor_upper_inclusive']):.5f}"
                if bool(plateau['width_floor_lower_inclusive'])
                else f"{float(plateau['width_floor_lower_exclusive']):.5f} < floor <= {float(plateau['width_floor_upper_inclusive']):.5f}"
            )
            anchors = ', '.join(
                f"{row['topology_code']}@{float(row['shared_core_anchor_delta']):.5f}[w={float(row['shared_core_width']):.5f}]"
                for row in plateau['candidate_rows']
            )
            lines.append(
                f"  - `{band}`: `{int(plateau['candidate_count'])}` candidates ({anchors}); distinct priority winners `{int(plateau['distinct_priority_winner_count'])}`; {winners}."
            )
    lines.extend([
        '',
        'Why this matters for the archive:',
        '- The width-floor contract should be expressed as a stable band whenever possible, not as one arbitrary scalar that happens to work in one run.',
        '- In the current proxy, any floor inside the family `10/20/50/100` plateau above `0.00026` and at most `0.00129` yields the same two-candidate low-delta shortlist, so the remaining judgment is no longer about width but about declared priority profile.',
        '- By contrast, folding cap `4` into the required family leaves only thin practical-tie fragments and no robust floor band at ordinary width thresholds. That is another way to see cap `4` as a fragmentation regime rather than just a stricter version of the same benchmark family.',
        '',
    ])
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')


def main() -> None:
    rows = _rows()
    summary = _build_summary(rows)
    OUT_JSON.write_text(json.dumps(_round(summary), indent=2, sort_keys=True) + '\n', encoding='utf-8')
    _write_markdown(summary)
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
