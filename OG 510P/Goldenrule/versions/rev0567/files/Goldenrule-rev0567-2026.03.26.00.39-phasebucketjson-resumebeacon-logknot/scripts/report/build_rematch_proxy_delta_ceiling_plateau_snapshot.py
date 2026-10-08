#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLISHABILITY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_publishability_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_ceiling_plateau_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_ceiling_plateau_snapshot_20260306.md'
MIN_SHARED_CORE_WIDTH = 0.0010
MAX_DELTA_CEILING = 0.02
EXPECTED_FAMILIES = [
    ('caps_10_20_50_100_width0p0010_hazard1000', [10, 20, 50, 100]),
    ('caps_4_10_20_50_100_width0p0010_hazard1000', [4, 10, 20, 50, 100]),
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


def material_first_key(row: dict[str, object]) -> tuple[object, ...]:
    return (
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
    )


def stability_first_key(row: dict[str, object]) -> tuple[object, ...]:
    return (
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
        -float(row['min_separation_to_hazard_band_for_additional_budget_cap_1000']),
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
                'winner_min_separation_to_hazard_band_for_additional_budget_cap_1000': None,
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
                'winner_min_separation_to_hazard_band_for_additional_budget_cap_1000': winner['min_separation_to_hazard_band_for_additional_budget_cap_1000'],
                'winner_shared_core_anchor_tie_count': winner['shared_core_anchor_tie_count'],
                'ordered_topology_codes': [row['topology_code'] for row in ordered],
                'ordered_anchor_deltas': [row['shared_core_anchor_delta'] for row in ordered],
            }
        )
    return outcomes


def _select_plateau(profile: dict[str, object], candidate_count: int) -> dict[str, object] | None:
    eligible = [row for row in profile['plateau_rows'] if int(row['candidate_count']) == candidate_count]
    if not eligible:
        return None
    return max(
        eligible,
        key=lambda row: (
            float(row['delta_ceiling_span']),
            float(row['delta_ceiling_upper_inclusive']),
            -float(row['delta_ceiling_lower_exclusive']),
        ),
    )


def _build_family_profiles(all_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    profiles: list[dict[str, object]] = []
    for profile_name, caps in EXPECTED_FAMILIES:
        family_rows = sorted(
            [
                row for row in all_rows
                if row['covered_budget_caps'] == caps
                and float(row['shared_core_width']) >= MIN_SHARED_CORE_WIDTH
                and not bool(row['overlaps_hazard_band_for_additional_budget_cap_1000'])
            ],
            key=lambda row: (float(row['shared_core_end_delta']), float(row['shared_core_anchor_delta']), str(row['topology_code'])),
        )
        cutoffs = sorted({float(row['shared_core_end_delta']) for row in family_rows} | {MAX_DELTA_CEILING})
        plateau_rows: list[dict[str, object]] = []
        previous_cutoff = 0.0
        for index, cutoff in enumerate(cutoffs):
            candidate_rows = sorted(
                [row for row in family_rows if float(row['shared_core_end_delta']) < cutoff],
                key=lambda row: (float(row['shared_core_anchor_delta']), str(row['topology_code'])),
            )
            outcomes = _priority_profile_outcomes(candidate_rows)
            distinct_winners = {
                (outcome['winner_topology_code'], outcome['winner_anchor_delta'])
                for outcome in outcomes
                if outcome['winner_topology_code'] is not None
            }
            plateau_rows.append(
                {
                    'delta_ceiling_lower_exclusive': previous_cutoff,
                    'delta_ceiling_upper_inclusive': cutoff,
                    'delta_ceiling_span': cutoff - previous_cutoff,
                    'candidate_count': len(candidate_rows),
                    'candidate_rows': candidate_rows,
                    'candidate_topology_codes': [row['topology_code'] for row in candidate_rows],
                    'candidate_anchor_deltas': [row['shared_core_anchor_delta'] for row in candidate_rows],
                    'priority_profile_outcomes': outcomes,
                    'distinct_priority_winner_count': len(distinct_winners),
                    'all_priority_profiles_agree': len(distinct_winners) <= 1,
                }
            )
            previous_cutoff = cutoff

        profiles.append(
            {
                'profile_name': profile_name,
                'covered_budget_caps': list(caps),
                'minimum_shared_core_width': MIN_SHARED_CORE_WIDTH,
                'hazard_guardrail_additional_budget_cap': 1000,
                'candidate_rows_before_delta_ceiling': sorted(
                    family_rows,
                    key=lambda row: (float(row['shared_core_anchor_delta']), str(row['topology_code'])),
                ),
                'candidate_count_before_delta_ceiling': len(family_rows),
                'plateau_rows': plateau_rows,
            }
        )
    return profiles


def _build_summary() -> dict[str, object]:
    publishability = _load_json(PUBLISHABILITY_PATH)
    all_rows = publishability['core_rows']
    family_profiles = _build_family_profiles(all_rows)
    by_name = {profile['profile_name']: profile for profile in family_profiles}

    family10 = by_name['caps_10_20_50_100_width0p0010_hazard1000']
    family4 = by_name['caps_4_10_20_50_100_width0p0010_hazard1000']
    family10_two = _select_plateau(family10, 2)
    family10_one = _select_plateau(family10, 1)
    family10_three = _select_plateau(family10, 3)
    family4_zero = _select_plateau(family4, 0)
    if family10_two is None or family10_one is None or family10_three is None or family4_zero is None:
        raise ValueError('expected plateau counts were not found')

    material_first = next(outcome for outcome in family10_two['priority_profile_outcomes'] if outcome['profile_name'] == 'material_first')
    stability_first = next(outcome for outcome in family10_two['priority_profile_outcomes'] if outcome['profile_name'] == 'stability_first')
    closure_conservative = next(outcome for outcome in family10_two['priority_profile_outcomes'] if outcome['profile_name'] == 'closure_conservative')
    family10_three_stability = next(outcome for outcome in family10_three['priority_profile_outcomes'] if outcome['profile_name'] == 'stability_first')

    return {
        'focus': 'Expose delta-ceiling plateaus for the width-qualified hazard-clear families so the archive can publish a stable low-delta band instead of pretending one scalar cutoff like 0.01 is uniquely canonical.',
        'method_note': 'Started from the publishability snapshot, fixed the width floor at 0.0010, kept only hazard-clear cores under the >1000-extra-seed guardrail, and then converted each family\'s shared-core end deltas into exact ceiling plateaus on which the surviving shortlist is constant. Reported the surviving anchors and declared priority-profile winners on each plateau.',
        'headline_findings': {
            'caps_10_20_50_100_largest_two_candidate_plateau': family10_two,
            'caps_10_20_50_100_largest_one_candidate_plateau': family10_one,
            'caps_10_20_50_100_largest_three_candidate_plateau': family10_three,
            'caps_4_10_20_50_100_only_zero_candidate_plateau': family4_zero,
            'current_sub0p01_ceiling_lies_inside_family10_two_candidate_plateau': (
                float(family10_two['delta_ceiling_lower_exclusive']) < 0.01 <= float(family10_two['delta_ceiling_upper_inclusive'])
            ),
            'family10_two_candidate_plateau_slack_above_current_sub0p01_ceiling': round(float(family10_two['delta_ceiling_upper_inclusive']) - 0.01, 6),
            'family10_two_candidate_plateau_span_over_one_candidate_plateau_span': round(float(family10_two['delta_ceiling_span']) / float(family10_one['delta_ceiling_span']), 6),
            'family10_material_first_winner_on_two_candidate_plateau': material_first,
            'family10_stability_first_winner_on_two_candidate_plateau': stability_first,
            'family10_closure_conservative_winner_on_two_candidate_plateau': closure_conservative,
            'family10_stability_first_winner_after_third_candidate_enters': family10_three_stability,
            'interpretation': 'The low-delta ceiling should be published as a band choice, not as one magical scalar such as 0.01. In the current proxy, once family 10/20/50/100, width floor 0.0010, and the hazard-clear guardrail are fixed, any ceiling in (0.00822, 0.01944] yields the exact same two-candidate shortlist and the same material-first / closure-conservative winners. Only above 0.01944 does a third high-delta candidate appear and let stability-first flip to a different anchor.',
        },
        'family_profiles': family_profiles,
        'source_report': 'artifacts/reports/rematch_proxy_delta_publishability_snapshot_20260306.json',
        'source_script': 'scripts/report/build_rematch_proxy_delta_ceiling_plateau_snapshot.py',
    }


def _write_markdown(summary: dict[str, object]) -> None:
    findings = summary['headline_findings']
    family_profiles = summary['family_profiles']
    family10_two = findings['caps_10_20_50_100_largest_two_candidate_plateau']
    family10_one = findings['caps_10_20_50_100_largest_one_candidate_plateau']
    family10_three = findings['caps_10_20_50_100_largest_three_candidate_plateau']
    family4_zero = findings['caps_4_10_20_50_100_only_zero_candidate_plateau']
    material_first = findings['family10_material_first_winner_on_two_candidate_plateau']
    stability_first = findings['family10_stability_first_winner_on_two_candidate_plateau']
    closure_conservative = findings['family10_closure_conservative_winner_on_two_candidate_plateau']
    stability_after_three = findings['family10_stability_first_winner_after_third_candidate_enters']

    lines = [
        '# Rematch-Proxy Delta Ceiling Plateau Snapshot (2026-03-06)',
        '',
        'Method:',
        '- started from the publishability snapshot rather than reopening the raw sweep',
        '- fixed the width floor at `0.0010` and kept only cores that remain outside the `>1000`-extra-seed hazard bands',
        '- converted the observed shared-core end deltas into exact ceiling plateaus on which the surviving shortlist is unchanged',
        '- reported the declared priority-profile winners on each plateau so future inheritors can see where the ceiling itself changes the choice contract',
        '',
        'Headline findings:',
        f"- for family `10/20/50/100`, the largest one-candidate plateau is `{float(family10_one['delta_ceiling_lower_exclusive']):.5f} < ceiling <= {float(family10_one['delta_ceiling_upper_inclusive']):.5f}`, containing only `TTTMMMMMU@0.00602`.",
        f"- the largest two-candidate plateau is `{float(family10_two['delta_ceiling_lower_exclusive']):.5f} < ceiling <= {float(family10_two['delta_ceiling_upper_inclusive']):.5f}` with span `{float(family10_two['delta_ceiling_span']):.5f}`; throughout that whole band the shortlist is exactly `TTTMMMMMU@0.00602` plus `TTTMMMMUU@0.00744`.",
        f"- the inherited `0.01` ceiling lies inside that two-candidate plateau, with `{float(findings['family10_two_candidate_plateau_slack_above_current_sub0p01_ceiling']):.5f}` of extra headroom before a third candidate can enter.",
        f"- the two-candidate plateau is `{float(findings['family10_two_candidate_plateau_span_over_one_candidate_plateau_span']):.3f}x` wider than the family10 one-candidate plateau below it, so the cutoff is substantially less knife-edge than the archive currently implies.",
        f"- on the whole two-candidate plateau, `material_first` selects `{material_first['winner_topology_code']}` at `{float(material_first['winner_anchor_delta']):.5f}`, `stability_first` selects `{stability_first['winner_topology_code']}` at `{float(stability_first['winner_anchor_delta']):.5f}`, and `closure_conservative` selects `{closure_conservative['winner_topology_code']}` at `{float(closure_conservative['winner_anchor_delta']):.5f}`.",
        f"- above `{float(family10_three['delta_ceiling_lower_exclusive']):.5f}`, a third candidate `TTTTTTMUT@0.01845` appears; then `stability_first` flips to `{stability_after_three['winner_topology_code']}` at `{float(stability_after_three['winner_anchor_delta']):.5f}` while the other two profiles remain on the lower-delta material core.",
        f"- for family `4/10/20/50/100`, the only plateau on `[0, 0.02]` is `{float(family4_zero['delta_ceiling_lower_exclusive']):.5f} < ceiling <= {float(family4_zero['delta_ceiling_upper_inclusive']):.5f}` with `0` width-qualified hazard-clear candidates, so ceiling adjustments cannot rescue that family once width is fixed at `0.0010`.",
        '',
        'Per-family plateau map:',
    ]
    for profile in family_profiles:
        caps = '/'.join(str(cap) for cap in profile['covered_budget_caps'])
        lines.append(f"- `{profile['profile_name']}` (caps {caps}):")
        lines.append(f"  - width floor fixed at `{float(profile['minimum_shared_core_width']):.4f}`; hazard guardrail uses additional budget cap `{int(profile['hazard_guardrail_additional_budget_cap'])}`.")
        lines.append(f"  - candidates before applying a delta ceiling: `{int(profile['candidate_count_before_delta_ceiling'])}`.")
        for plateau in profile['plateau_rows']:
            winners = ', '.join(
                f"{outcome['profile_name']}->{outcome['winner_topology_code']}@{float(outcome['winner_anchor_delta']):.5f}"
                if outcome['winner_topology_code'] is not None
                else f"{outcome['profile_name']}->none"
                for outcome in plateau['priority_profile_outcomes']
            )
            anchors = ', '.join(
                f"{row['topology_code']}@{float(row['shared_core_anchor_delta']):.5f}[end={float(row['shared_core_end_delta']):.5f}]"
                for row in plateau['candidate_rows']
            ) or 'none'
            lines.append(
                f"  - `{float(plateau['delta_ceiling_lower_exclusive']):.5f} < ceiling <= {float(plateau['delta_ceiling_upper_inclusive']):.5f}`: `{int(plateau['candidate_count'])}` candidates ({anchors}); distinct priority winners `{int(plateau['distinct_priority_winner_count'])}`; {winners}."
            )
        lines.append('')

    lines.extend([
        'Why this matters for the archive:',
        '- The archive should still declare its low-delta ceiling explicitly, because that ceiling is a real modeling choice.',
        '- But the archive should not act as if `0.01` is uniquely canonical when a much broader ceiling band leaves the shortlisted anchors unchanged.',
        '- In the current proxy, the meaningful ceiling boundary for the width-qualified family10 shortlist is `0.01944`, not `0.01`; below that boundary the shortlist stays low-delta and compact, while above it stability-first can pivot to a much higher-delta anchor.',
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
