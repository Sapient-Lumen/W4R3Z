#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLISHABILITY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_publishability_snapshot_20260306.json'
WINNER_CERTIFICATION_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_winner_certification_snapshot_20260306.json'
WIDTH_PLATEAU_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_width_floor_plateau_snapshot_20260306.json'
CEILING_PLATEAU_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_ceiling_plateau_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_hazard_threshold_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_hazard_threshold_snapshot_20260306.md'
T_CRIT_90_DF5 = 2.015048
TARGET_FAMILY = [10, 20, 50, 100]
MIN_SHARED_CORE_WIDTH = 0.0010
SUB_0P01_LIMIT = 0.01
MAX_DELTA = 0.02
SAMPLED_HAZARD_CAPS = [100, 500, 1000, 10000]
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
        end_delta = min(MAX_DELTA, mean_gap + radius)
        if start_delta >= end_delta:
            continue
        intervals.append(
            {
                'extortion': int(row['extortion']),
                'delay': int(row['delay']),
                'leader': row['leader'],
                'runner_up': row['runner_up'],
                'leader_margin': mean_gap,
                'paired_margin_sd': sd_gap,
                'paired_seed_count': current_n,
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


def _base_rows(all_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = [
        row for row in all_rows
        if row['covered_budget_caps'] == TARGET_FAMILY
        and float(row['shared_core_width']) >= MIN_SHARED_CORE_WIDTH
        and float(row['shared_core_end_delta']) < SUB_0P01_LIMIT
    ]
    rows.sort(key=lambda row: (float(row['shared_core_anchor_delta']), str(row['topology_code'])))
    return rows


def _candidate_rows_for_hazard_cap(base_rows: list[dict[str, object]], panel_rows: list[dict[str, object]], additional_budget_cap: int) -> list[dict[str, object]]:
    intervals = _hazard_intervals(panel_rows, additional_budget_cap)
    out: list[dict[str, object]] = []
    for row in base_rows:
        start = float(row['shared_core_start_delta'])
        end = float(row['shared_core_end_delta'])
        best_distance = math.inf
        best_interval: dict[str, object] | None = None
        for interval in intervals:
            hazard = interval['hazard_interval_within_delta_le_0_02']
            distance = _interval_distance(start, end, float(hazard['start_delta']), float(hazard['end_delta']))
            if distance < best_distance:
                best_distance = distance
                best_interval = interval
        if best_distance == 0.0:
            continue
        candidate = dict(row)
        candidate['additional_budget_cap_for_hazard_guardrail'] = additional_budget_cap
        candidate['min_separation_to_hazard_band_for_additional_budget_cap'] = round(best_distance, 6)
        if best_interval is not None:
            candidate['binding_hazard_panel'] = {
                'extortion': int(best_interval['extortion']),
                'delay': int(best_interval['delay']),
                'leader': best_interval['leader'],
                'runner_up': best_interval['runner_up'],
                'leader_margin': best_interval['leader_margin'],
                'paired_margin_sd': best_interval['paired_margin_sd'],
                'paired_seed_count': int(best_interval['paired_seed_count']),
                'hazard_interval_within_delta_le_0_02': best_interval['hazard_interval_within_delta_le_0_02'],
            }
        out.append(candidate)
    out.sort(key=lambda row: (float(row['shared_core_anchor_delta']), str(row['topology_code'])))
    return out


def _row_can_ever_clear(row: dict[str, object], panel_rows: list[dict[str, object]]) -> bool:
    start = float(row['shared_core_start_delta'])
    end = float(row['shared_core_end_delta'])
    return all(not (start <= float(panel['leader_margin']) <= end) for panel in panel_rows)


def _first_clearance_cap(row: dict[str, object], panel_rows: list[dict[str, object]]) -> int | None:
    if not _row_can_ever_clear(row, panel_rows):
        return None
    for cap in range(0, 100000):
        survivors = _candidate_rows_for_hazard_cap([row], panel_rows, cap)
        if survivors:
            return cap
    raise ValueError(f'failed to find clearance cap for {row["topology_code"]}')


def _clearance_rows(base_rows: list[dict[str, object]], panel_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in base_rows:
        threshold = _first_clearance_cap(row, panel_rows)
        threshold_candidate = None
        threshold_minus_one_candidate = None
        if threshold is not None:
            threshold_candidate = _candidate_rows_for_hazard_cap([row], panel_rows, threshold)[0]
            if threshold > 0:
                prior = _candidate_rows_for_hazard_cap([row], panel_rows, threshold - 1)
                threshold_minus_one_candidate = prior[0] if prior else None
        rows.append(
            {
                'topology_code': row['topology_code'],
                'shared_core_anchor_delta': row['shared_core_anchor_delta'],
                'shared_core_start_delta': row['shared_core_start_delta'],
                'shared_core_end_delta': row['shared_core_end_delta'],
                'shared_core_width': row['shared_core_width'],
                'counts': row['counts'],
                'minimum_additional_budget_cap_to_clear_hazard_band': threshold,
                'candidate_row_at_threshold': threshold_candidate,
                'candidate_row_at_threshold_minus_one': threshold_minus_one_candidate,
            }
        )
    rows.sort(
        key=lambda row: (
            math.inf if row['minimum_additional_budget_cap_to_clear_hazard_band'] is None else int(row['minimum_additional_budget_cap_to_clear_hazard_band']),
            float(row['shared_core_anchor_delta']),
            str(row['topology_code']),
        )
    )
    return rows


def _hazard_cap_plateaus(base_rows: list[dict[str, object]], panel_rows: list[dict[str, object]], clearance_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    thresholds = sorted({int(row['minimum_additional_budget_cap_to_clear_hazard_band']) for row in clearance_rows if row['minimum_additional_budget_cap_to_clear_hazard_band'] is not None})
    plateaus: list[dict[str, object]] = []
    lower = 0
    for threshold in thresholds:
        if lower <= threshold - 1:
            candidate_rows = _candidate_rows_for_hazard_cap(base_rows, panel_rows, lower)
            outcomes = _priority_profile_outcomes(candidate_rows)
            distinct_winners = {
                (outcome['winner_topology_code'], outcome['winner_anchor_delta'])
                for outcome in outcomes if outcome['winner_topology_code'] is not None
            }
            plateaus.append(
                {
                    'hazard_cap_lower_inclusive': lower,
                    'hazard_cap_upper_inclusive': threshold - 1,
                    'hazard_cap_span': threshold - lower,
                    'candidate_count': len(candidate_rows),
                    'candidate_rows_at_lower_bound': candidate_rows,
                    'candidate_topology_codes': [row['topology_code'] for row in candidate_rows],
                    'candidate_anchor_deltas': [row['shared_core_anchor_delta'] for row in candidate_rows],
                    'priority_profile_outcomes': outcomes,
                    'distinct_priority_winner_count': len(distinct_winners),
                    'all_priority_profiles_agree': len(distinct_winners) <= 1,
                    'sampled_hazard_caps_inside_plateau': [cap for cap in SAMPLED_HAZARD_CAPS if lower <= cap <= threshold - 1],
                }
            )
        lower = threshold

    final_candidate_rows = _candidate_rows_for_hazard_cap(base_rows, panel_rows, lower)
    final_outcomes = _priority_profile_outcomes(final_candidate_rows)
    final_distinct_winners = {
        (outcome['winner_topology_code'], outcome['winner_anchor_delta'])
        for outcome in final_outcomes if outcome['winner_topology_code'] is not None
    }
    final_sampled_rows = {
        cap: _candidate_rows_for_hazard_cap(base_rows, panel_rows, cap)
        for cap in SAMPLED_HAZARD_CAPS
        if cap >= lower
    }
    plateaus.append(
        {
            'hazard_cap_lower_inclusive': lower,
            'hazard_cap_upper_inclusive': None,
            'hazard_cap_span': None,
            'candidate_count': len(final_candidate_rows),
            'candidate_rows_at_lower_bound': final_candidate_rows,
            'candidate_topology_codes': [row['topology_code'] for row in final_candidate_rows],
            'candidate_anchor_deltas': [row['shared_core_anchor_delta'] for row in final_candidate_rows],
            'priority_profile_outcomes': final_outcomes,
            'distinct_priority_winner_count': len(final_distinct_winners),
            'all_priority_profiles_agree': len(final_distinct_winners) <= 1,
            'sampled_hazard_caps_inside_plateau': [cap for cap in SAMPLED_HAZARD_CAPS if cap >= lower],
            'sampled_hazard_cap_candidate_rows': final_sampled_rows,
            'candidate_identity_invariant_across_sampled_hazard_caps': len({tuple((row['topology_code'], row['shared_core_anchor_delta']) for row in rows) for rows in final_sampled_rows.values()}) <= 1,
        }
    )
    return plateaus


def _two_candidate_width_plateau(width_snapshot: dict[str, object]) -> dict[str, object]:
    return width_snapshot['headline_findings']['caps_10_20_50_100_largest_two_candidate_plateau']


def _two_candidate_ceiling_plateau(ceiling_snapshot: dict[str, object]) -> dict[str, object]:
    return ceiling_snapshot['headline_findings']['caps_10_20_50_100_largest_two_candidate_plateau']


def _build_summary() -> dict[str, object]:
    publishability = _load_json(PUBLISHABILITY_PATH)
    winner_certification = _load_json(WINNER_CERTIFICATION_PATH)
    width_snapshot = _load_json(WIDTH_PLATEAU_PATH)
    ceiling_snapshot = _load_json(CEILING_PLATEAU_PATH)
    all_rows = publishability['core_rows']
    panel_rows = winner_certification['panel_rows']
    base_rows = _base_rows(all_rows)
    clearance_rows = _clearance_rows(base_rows, panel_rows)
    plateaus = _hazard_cap_plateaus(base_rows, panel_rows, clearance_rows)

    empty_plateau = next(row for row in plateaus if int(row['candidate_count']) == 0)
    singleton_plateau = next(row for row in plateaus if int(row['candidate_count']) == 1)
    full_plateau = next(row for row in plateaus if int(row['candidate_count']) == len(base_rows))

    material_first = next(outcome for outcome in full_plateau['priority_profile_outcomes'] if outcome['profile_name'] == 'material_first')
    stability_first = next(outcome for outcome in full_plateau['priority_profile_outcomes'] if outcome['profile_name'] == 'stability_first')
    closure_conservative = next(outcome for outcome in full_plateau['priority_profile_outcomes'] if outcome['profile_name'] == 'closure_conservative')

    width_two = _two_candidate_width_plateau(width_snapshot)
    ceiling_two = _two_candidate_ceiling_plateau(ceiling_snapshot)
    full_threshold = int(full_plateau['hazard_cap_lower_inclusive'])
    first_sampled_cap = min(SAMPLED_HAZARD_CAPS)

    return {
        'focus': 'Convert the sampled hazard-cap evidence into an exact monotone clearance threshold for the low-delta family10 shortlist, then combine that threshold with the previously derived width-floor and delta-ceiling plateaus into one publishable policy box.',
        'method_note': 'Started from the exact family `10/20/50/100` rows that already survive the width floor `0.0010` and strict sub-`0.01` ceiling in the publishability snapshot. Recomputed hazard-band overlap against the winner-certification panel margins for every integer additional-budget cap, used the monotone shrinking of the hazard intervals to identify the first cap at which each candidate clears, and then summarized the resulting hazard-cap plateaus. Finally linked the exact full-shortlist hazard threshold back to the previously derived width-floor and delta-ceiling two-candidate plateaus.',
        'headline_findings': {
            'base_candidate_rows_before_hazard_guardrail': base_rows,
            'largest_empty_hazard_cap_plateau': empty_plateau,
            'singleton_hazard_cap_plateau_before_full_shortlist': singleton_plateau,
            'full_shortlist_hazard_cap_plateau': full_plateau,
            'minimum_additional_budget_cap_for_tttmmmmuu': next(row for row in clearance_rows if row['topology_code'] == 'TTTMMMMUU'),
            'minimum_additional_budget_cap_for_tttmmmmmu': next(row for row in clearance_rows if row['topology_code'] == 'TTTMMMMMU'),
            'full_shortlist_exact_minimum_additional_budget_cap': full_threshold,
            'first_sampled_hazard_cap': first_sampled_cap,
            'first_sampled_hazard_cap_minus_exact_full_shortlist_threshold': first_sampled_cap - full_threshold,
            'first_sampled_hazard_cap_over_exact_full_shortlist_threshold_ratio': round(first_sampled_cap / full_threshold, 6),
            'material_first_winner_on_full_shortlist_plateau': material_first,
            'stability_first_winner_on_full_shortlist_plateau': stability_first,
            'closure_conservative_winner_on_full_shortlist_plateau': closure_conservative,
            'full_shortlist_policy_box': {
                'covered_budget_caps': TARGET_FAMILY,
                'width_floor_lower_exclusive': width_two['width_floor_lower_exclusive'],
                'width_floor_upper_inclusive': width_two['width_floor_upper_inclusive'],
                'minimum_additional_budget_cap_inclusive': full_threshold,
                'delta_ceiling_lower_exclusive': ceiling_two['delta_ceiling_lower_exclusive'],
                'delta_ceiling_upper_inclusive': ceiling_two['delta_ceiling_upper_inclusive'],
                'candidate_topology_codes': full_plateau['candidate_topology_codes'],
                'candidate_anchor_deltas': full_plateau['candidate_anchor_deltas'],
                'priority_profile_outcomes': full_plateau['priority_profile_outcomes'],
            },
            'interpretation': 'The hazard guardrail should be published as a minimum monotone clearance threshold, not just as a few sampled caps. In the current proxy, once the family is fixed to 10/20/50/100, the width floor is kept anywhere in (0.00026, 0.00129], and the delta ceiling stays anywhere in (0.00822, 0.01944], the exact two-anchor shortlist appears as soon as the additional paired-seed hazard cap reaches 10 and then persists for every larger cap. The previously sampled minimum cap 100 therefore overshot the exact full-shortlist threshold by 90 paired seeds and by a factor of 10.',
        },
        'clearance_rows': clearance_rows,
        'hazard_cap_plateau_rows': plateaus,
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_publishability_snapshot_20260306.json',
            'artifacts/reports/rematch_proxy_winner_certification_snapshot_20260306.json',
            'artifacts/reports/rematch_proxy_delta_width_floor_plateau_snapshot_20260306.json',
            'artifacts/reports/rematch_proxy_delta_ceiling_plateau_snapshot_20260306.json',
        ],
        'source_script': 'scripts/report/build_rematch_proxy_delta_hazard_threshold_snapshot.py',
    }


def _write_markdown(summary: dict[str, object]) -> None:
    findings = summary['headline_findings']
    empty_plateau = findings['largest_empty_hazard_cap_plateau']
    singleton_plateau = findings['singleton_hazard_cap_plateau_before_full_shortlist']
    full_plateau = findings['full_shortlist_hazard_cap_plateau']
    tttmmmmuu = findings['minimum_additional_budget_cap_for_tttmmmmuu']
    tttmmmmmu = findings['minimum_additional_budget_cap_for_tttmmmmmu']
    material_first = findings['material_first_winner_on_full_shortlist_plateau']
    stability_first = findings['stability_first_winner_on_full_shortlist_plateau']
    closure_conservative = findings['closure_conservative_winner_on_full_shortlist_plateau']
    policy_box = findings['full_shortlist_policy_box']

    lines = [
        '# Rematch-Proxy Delta Hazard-Threshold Snapshot (2026-03-06)',
        '',
        'Method:',
        '- started from the exact family `10/20/50/100` rows that already satisfy width floor `0.0010` and strict sub-`0.01` delta ceiling',
        '- recomputed hazard-band overlap against the winner-certification panel margins for every integer additional-budget cap',
        '- used monotone hazard-band shrinkage to identify the first cap at which each candidate clears',
        '- then linked the exact full-shortlist hazard threshold back to the previously derived width-floor and delta-ceiling two-candidate plateaus',
        '',
        'Headline findings:',
        f"- for caps `0` through `{int(empty_plateau['hazard_cap_upper_inclusive'])}`, the shortlist is empty.",
        f"- for caps `{int(singleton_plateau['hazard_cap_lower_inclusive'])}` through `{int(singleton_plateau['hazard_cap_upper_inclusive'])}`, the shortlist contains exactly one candidate: `{singleton_plateau['candidate_topology_codes'][0]}` at `{float(singleton_plateau['candidate_anchor_deltas'][0]):.5f}`.",
        f"- the full two-candidate shortlist first appears at hazard cap `{int(full_plateau['hazard_cap_lower_inclusive'])}` and then persists for all larger caps: `{full_plateau['candidate_topology_codes'][0]}` at `{float(full_plateau['candidate_anchor_deltas'][0]):.5f}` plus `{full_plateau['candidate_topology_codes'][1]}` at `{float(full_plateau['candidate_anchor_deltas'][1]):.5f}`.",
        f"- `{tttmmmmuu['topology_code']}` clears first at cap `{int(tttmmmmuu['minimum_additional_budget_cap_to_clear_hazard_band'])}`; `{tttmmmmmu['topology_code']}` clears at cap `{int(tttmmmmmu['minimum_additional_budget_cap_to_clear_hazard_band'])}`, which is the exact threshold needed to recover the full low-delta shortlist.",
        f"- the first previously sampled cap `{int(findings['first_sampled_hazard_cap'])}` overshot that exact full-shortlist threshold by `{int(findings['first_sampled_hazard_cap_minus_exact_full_shortlist_threshold'])}` paired seeds and by a factor of `{float(findings['first_sampled_hazard_cap_over_exact_full_shortlist_threshold_ratio']):.2f}`.",
        f"- on the full-shortlist plateau, `material_first` selects `{material_first['winner_topology_code']}` at `{float(material_first['winner_anchor_delta']):.5f}`, `stability_first` selects `{stability_first['winner_topology_code']}` at `{float(stability_first['winner_anchor_delta']):.5f}`, and `closure_conservative` again selects `{closure_conservative['winner_topology_code']}` at `{float(closure_conservative['winner_anchor_delta']):.5f}`.",
        f"- combining this hazard threshold with the previous plateau passes yields one compact policy box: family `10/20/50/100`, `{float(policy_box['width_floor_lower_exclusive']):.5f} < width floor <= {float(policy_box['width_floor_upper_inclusive']):.5f}`, hazard cap `>= {int(policy_box['minimum_additional_budget_cap_inclusive'])}`, and `{float(policy_box['delta_ceiling_lower_exclusive']):.5f} < delta ceiling <= {float(policy_box['delta_ceiling_upper_inclusive']):.5f}`. Anywhere inside that box the shortlist and priority winners are unchanged.",
        '',
        'Candidate clearance thresholds:',
    ]
    for row in summary['clearance_rows']:
        threshold = row['minimum_additional_budget_cap_to_clear_hazard_band']
        if threshold is None:
            lines.append(
                f"- `{row['topology_code']}@{float(row['shared_core_anchor_delta']):.5f}` never clears the hazard band." 
            )
            continue
        at_threshold = row['candidate_row_at_threshold']
        binding = at_threshold['binding_hazard_panel']
        lines.append(
            f"- `{row['topology_code']}@{float(row['shared_core_anchor_delta']):.5f}`: first clear at cap `{int(threshold)}`; binding panel `extortion={int(binding['extortion'])}, delay={int(binding['delay'])}, leader={binding['leader']}, runner_up={binding['runner_up']}`; first positive separation `{float(at_threshold['min_separation_to_hazard_band_for_additional_budget_cap']):.6f}`."
        )
    lines.extend([
        '',
        'Hazard-cap plateau map:',
    ])
    for plateau in summary['hazard_cap_plateau_rows']:
        if plateau['hazard_cap_upper_inclusive'] is None:
            band = f"cap >= {int(plateau['hazard_cap_lower_inclusive'])}"
        else:
            band = f"{int(plateau['hazard_cap_lower_inclusive'])} <= cap <= {int(plateau['hazard_cap_upper_inclusive'])}"
        winners = ', '.join(
            f"{outcome['profile_name']}->{outcome['winner_topology_code']}@{float(outcome['winner_anchor_delta']):.5f}"
            if outcome['winner_topology_code'] is not None
            else f"{outcome['profile_name']}->None"
            for outcome in plateau['priority_profile_outcomes']
        )
        anchors = ', '.join(
            f"{row['topology_code']}@{float(row['shared_core_anchor_delta']):.5f}[sep={float(row['min_separation_to_hazard_band_for_additional_budget_cap']):.6f}]"
            for row in plateau['candidate_rows_at_lower_bound']
        ) or 'none'
        sampled = plateau.get('sampled_hazard_caps_inside_plateau', [])
        sampled_suffix = f"; sampled caps inside plateau: {sampled}" if sampled else ''
        lines.append(
            f"- `{band}`: `{int(plateau['candidate_count'])}` candidates ({anchors}); distinct priority winners `{int(plateau['distinct_priority_winner_count'])}`; {winners}{sampled_suffix}."
        )
    lines.extend([
        '',
        'Interpretation:',
        '- the hazard guardrail is not merely “inactive across the sampled caps”; it has an exact entry threshold for the full low-delta shortlist, and that threshold is much lower than the first sampled cap',
        '- below cap `10`, the guardrail itself collapses the shortlist and silently removes the lower-delta material-first anchor',
        '- from cap `10` onward, the hazard dimension ceases to be the hidden selector inside the previously derived family10 width/ceiling plateau box',
    ])
    OUT_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main() -> None:
    summary = _build_summary()
    OUT_JSON.write_text(json.dumps(_round(summary), indent=2) + '\n', encoding='utf-8')
    _write_markdown(summary)
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
