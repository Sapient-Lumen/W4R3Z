#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PERSISTENCE_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_persistence_snapshot_20260306.json'
HAZARD_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_hazard_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_publishability_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_publishability_snapshot_20260306.md'

HAZARD_BUDGET_THRESHOLD = 1000
MIN_CAP_COUNT = 4
SUB_0P01_LIMIT = 0.01


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


def _canonical_family_cores() -> list[dict[str, object]]:
    persistence = _load_json(PERSISTENCE_PATH)
    hazard = _load_json(HAZARD_PATH)
    ladder_rows = persistence['ladder_rows']
    hazard_rows = hazard['panel_hazard_rows_for_additional_budget_cap_1000']
    knife_edges = [float(row['leader_margin']) for row in hazard['knife_edge_rows']]
    hazard_intervals = [
        (
            float(row['hazard_interval_within_delta_le_0_02']['start_delta']),
            float(row['hazard_interval_within_delta_le_0_02']['end_delta']),
        )
        for row in hazard_rows
    ]

    canonical: dict[tuple[object, ...], dict[str, object]] = {}
    for row in ladder_rows:
        if int(row['covered_budget_cap_count']) < MIN_CAP_COUNT:
            continue
        key = (
            str(row['topology_code']),
            float(row['shared_core_start_delta']),
            float(row['shared_core_end_delta']),
        )
        current = canonical.get(key)
        if current is None or int(row['root_budget_cap_additional_paired_seeds']) < int(current['root_budget_cap_additional_paired_seeds']):
            canonical[key] = row

    core_rows: list[dict[str, object]] = []
    for row in canonical.values():
        start = float(row['shared_core_start_delta'])
        end = float(row['shared_core_end_delta'])
        anchor = float(row['shared_core_anchor_delta'])
        min_hazard_sep = min(_interval_distance(start, end, h0, h1) for h0, h1 in hazard_intervals)
        min_knife_sep = min(abs(anchor - edge) for edge in knife_edges)
        core_rows.append(
            {
                'root_budget_cap_additional_paired_seeds': int(row['root_budget_cap_additional_paired_seeds']),
                'covered_budget_caps': row['covered_budget_caps'],
                'covered_budget_cap_count': int(row['covered_budget_cap_count']),
                'covers_all_larger_declared_caps': bool(row['covers_all_larger_declared_caps']),
                'topology_code': str(row['topology_code']),
                'counts': row['counts'],
                'shared_core_start_delta': start,
                'shared_core_end_delta': end,
                'shared_core_width': float(row['shared_core_width']),
                'shared_core_gridpoint_count': int(row['shared_core_gridpoint_count']),
                'shared_core_anchor_delta': anchor,
                'shared_core_anchor_tie_count': int(row['shared_core_anchor_tie_count']),
                'shared_core_anchor_buffer_to_boundary': float(row['shared_core_anchor_buffer_to_boundary']),
                'single_grid_point_shared_core': bool(row['single_grid_point_shared_core']),
                'below_delta_0p01': end < SUB_0P01_LIMIT,
                'min_separation_to_knife_edge_delta': round(min_knife_sep, 6),
                'min_separation_to_hazard_band_for_additional_budget_cap_1000': round(min_hazard_sep, 6),
                'overlaps_hazard_band_for_additional_budget_cap_1000': min_hazard_sep == 0.0,
            }
        )

    core_rows.sort(
        key=lambda row: (
            float(row['shared_core_anchor_delta']),
            -float(row['shared_core_width']),
            int(row['root_budget_cap_additional_paired_seeds']),
            str(row['topology_code']),
        )
    )
    return core_rows


def _profile(name: str, rows: list[dict[str, object]], *, width_floor: float, sub_0p01_only: bool) -> dict[str, object]:
    candidates = [
        row for row in rows
        if float(row['shared_core_width']) >= width_floor
        and not bool(row['overlaps_hazard_band_for_additional_budget_cap_1000'])
        and (not sub_0p01_only or bool(row['below_delta_0p01']))
    ]
    return {
        'profile_name': name,
        'minimum_covered_budget_cap_count': MIN_CAP_COUNT,
        'minimum_shared_core_width': width_floor,
        'requires_no_overlap_with_hazard_band_for_additional_budget_cap': HAZARD_BUDGET_THRESHOLD,
        'sub_0p01_only': sub_0p01_only,
        'candidate_count': len(candidates),
        'candidate_rows': candidates,
    }


def _build_summary(rows: list[dict[str, object]]) -> dict[str, object]:
    profiles = [
        _profile('family4_width0p0005_hazard1000', rows, width_floor=0.0005, sub_0p01_only=False),
        _profile('family4_width0p0010_hazard1000', rows, width_floor=0.0010, sub_0p01_only=False),
        _profile('family4_width0p0010_hazard1000_sub0p01', rows, width_floor=0.0010, sub_0p01_only=True),
    ]
    by_name = {profile['profile_name']: profile for profile in profiles}
    broad = by_name['family4_width0p0005_hazard1000']
    strict = by_name['family4_width0p0010_hazard1000']
    low = by_name['family4_width0p0010_hazard1000_sub0p01']
    low_candidates = low['candidate_rows']
    strict_candidates = strict['candidate_rows']

    return {
        'focus': 'Collapse persistent rematch delta cores into a small publishable shortlist by applying explicit budget-family, width-floor, and hazard-avoidance guardrails instead of exposing every cap-local micro-island as a public constant.',
        'headline_findings': {
            'canonical_family_core_count_covering_at_least_four_caps': len(rows),
            'family4_width0p0005_hazard1000_candidate_count': int(broad['candidate_count']),
            'family4_width0p0010_hazard1000_candidate_count': int(strict['candidate_count']),
            'family4_width0p0010_hazard1000_sub0p01_candidate_count': int(low['candidate_count']),
            'family4_width0p0010_hazard1000_sub0p01_candidates': low_candidates,
            'strict_shortlist_min_hazard_separation': min(float(row['min_separation_to_hazard_band_for_additional_budget_cap_1000']) for row in strict_candidates),
            'strict_shortlist_max_root_budget_cap': max(int(row['root_budget_cap_additional_paired_seeds']) for row in strict_candidates),
            'interpretation': 'Once family persistence is already enforced, the active filter in this proxy is shared-core width rather than hazard avoidance: every width-qualified shortlist candidate already stays clear of the >1000 extra-seed hazard bands. A width floor of 0.001 therefore shrinks the family-core universe to three publishable anchors overall, and only two of those lie below delta 0.01.',
        },
        'method_note': 'Canonicalized the persistence ladders to one row per unique shared core (topology code plus exact shared-core interval), keeping the smallest root budget cap that still generates that family core. Then applied guardrail profiles requiring survival across at least four declared caps, no overlap with the >1000-extra-seed hazard bands, and one of two shared-core width floors (0.0005 or 0.0010).',
        'core_rows': rows,
        'guardrail_profiles': profiles,
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_persistence_snapshot_20260306.json',
            'artifacts/reports/rematch_proxy_delta_hazard_snapshot_20260306.json',
        ],
        'source_script': 'scripts/report/build_rematch_proxy_delta_publishability_snapshot.py',
    }


def _write_markdown(summary: dict[str, object]) -> None:
    findings = summary['headline_findings']
    low_candidates = findings['family4_width0p0010_hazard1000_sub0p01_candidates']
    strict = next(profile for profile in summary['guardrail_profiles'] if profile['profile_name'] == 'family4_width0p0010_hazard1000')

    lines = [
        '# Rematch-Proxy Delta Publishability Snapshot (2026-03-06)',
        '',
        'Method:',
        '- canonicalized the persistence ladders to one row per unique shared core (topology code plus exact shared-core interval)',
        '- kept the smallest root budget cap that still yields each family core',
        '- measured each family core against the existing `>1000` extra-paired-seed hazard bands',
        '- applied guardrail shortlists requiring survival across at least four declared caps plus a minimum shared-core width',
        '',
        'Headline findings:',
        f"- there are `{findings['canonical_family_core_count_covering_at_least_four_caps']}` canonical family cores that survive across at least four declared caps.",
        f"- requiring width `>= 0.0005` and no overlap with the `>1000`-extra-seed hazard bands leaves `{findings['family4_width0p0005_hazard1000_candidate_count']}` publishable candidates.",
        f"- tightening the width floor to `0.0010` collapses that shortlist to `{findings['family4_width0p0010_hazard1000_candidate_count']}` candidates overall, and only `{findings['family4_width0p0010_hazard1000_sub0p01_candidate_count']}` remain below `delta=0.01`.",
        f"- the strict shortlist stays at least `{float(findings['strict_shortlist_min_hazard_separation']):.6f}` away from any `>1000`-extra-seed hazard band, so width — not hazard overlap — is the active guardrail in the current proxy once family persistence has already been enforced.",
        '',
        'Strict sub-0.01 shortlist (width `>= 0.0010`, family persistence, no hazard overlap):',
    ]
    for row in low_candidates:
        counts = row['counts']
        lines.append(
            f"- `{row['topology_code']}` on `{float(row['shared_core_start_delta']):.5f}..{float(row['shared_core_end_delta']):.5f}` with anchor `{float(row['shared_core_anchor_delta']):.5f}`; caps `{', '.join(map(str, row['covered_budget_caps']))}`; counts `M={int(counts['material_leader'])}, T={int(counts['practical_tie'])}, U={int(counts['undecided'])}`."
        )
    lines.extend(['', 'Strict overall shortlist:'])
    for row in strict['candidate_rows']:
        lines.append(
            f"- `{row['topology_code']}` on `{float(row['shared_core_start_delta']):.5f}..{float(row['shared_core_end_delta']):.5f}` with anchor `{float(row['shared_core_anchor_delta']):.5f}`; width `{float(row['shared_core_width']):.5f}`; min hazard separation `{float(row['min_separation_to_hazard_band_for_additional_budget_cap_1000']):.6f}`."
        )
    lines.extend(
        [
            '',
            'Implementor consequence:',
            '- Do not publish every persistent micro-island as if it were equally benchmark-worthy.',
            '- Instead, expose a guardrail-filtered shortlist: one declared budget family, one width floor, one hazard threshold, and the resulting family-core anchors.',
            '- In the current proxy, a practical default is to treat the cap family `10, 20, 50, 100` plus width floor `0.0010` as the public shortlist contract. That yields one low-delta material-core anchor, one low-delta practical-tie anchor, and one high-delta fallback anchor.',
            '',
        ]
    )
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')


def main() -> int:
    rows = _canonical_family_cores()
    summary = _build_summary(rows)
    OUT_JSON.write_text(json.dumps(_round(summary), indent=2, sort_keys=True) + '\n', encoding='utf-8')
    _write_markdown(summary)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
