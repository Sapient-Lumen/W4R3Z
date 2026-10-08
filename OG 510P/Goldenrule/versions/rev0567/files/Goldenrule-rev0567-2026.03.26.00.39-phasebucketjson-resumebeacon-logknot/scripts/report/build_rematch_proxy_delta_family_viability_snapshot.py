#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLISHABILITY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_publishability_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_family_viability_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_family_viability_snapshot_20260306.md'

WIDTH_FLOORS = [0.00025, 0.0005, 0.0010]
FAMILY_PROFILES = [
    {
        'profile_name': 'caps_10_20_50_100_sub0p01',
        'covered_budget_caps': [10, 20, 50, 100],
        'label': 'caps 10/20/50/100',
    },
    {
        'profile_name': 'caps_4_10_20_50_100_sub0p01',
        'covered_budget_caps': [4, 10, 20, 50, 100],
        'label': 'caps 4/10/20/50/100',
    },
]


def _round(obj: object) -> object:
    if isinstance(obj, float):
        return round(obj, 6)
    if isinstance(obj, list):
        return [_round(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _round(v) for k, v in obj.items()}
    return obj


def _load_rows() -> list[dict[str, object]]:
    report = json.loads(PUBLISHABILITY_PATH.read_text(encoding='utf-8'))
    rows = report['core_rows']
    return [
        row for row in rows
        if bool(row['below_delta_0p01'])
        and not bool(row['overlaps_hazard_band_for_additional_budget_cap_1000'])
    ]


def _sort_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return sorted(
        rows,
        key=lambda row: (
            -float(row['shared_core_width']),
            float(row['shared_core_anchor_delta']),
            str(row['topology_code']),
        ),
    )


def _width_survival(rows: list[dict[str, object]], *, minimum_candidate_count: int) -> float:
    widths = sorted((float(row['shared_core_width']) for row in rows), reverse=True)
    if len(widths) < minimum_candidate_count:
        return 0.0
    return widths[minimum_candidate_count - 1]


def _family_profile(rows: list[dict[str, object]], spec: dict[str, object]) -> dict[str, object]:
    family_rows = _sort_rows([row for row in rows if row['covered_budget_caps'] == spec['covered_budget_caps']])
    widths = [float(row['shared_core_width']) for row in family_rows]
    candidate_counts = []
    for floor in WIDTH_FLOORS:
        candidate_counts.append(
            {
                'minimum_shared_core_width': floor,
                'candidate_count': sum(width >= floor for width in widths),
                'candidate_rows': [row for row in family_rows if float(row['shared_core_width']) >= floor],
            }
        )
    return {
        'profile_name': spec['profile_name'],
        'covered_budget_caps': spec['covered_budget_caps'],
        'label': spec['label'],
        'candidate_count_before_width_floor': len(family_rows),
        'candidate_rows_before_width_floor': family_rows,
        'maximum_width_floor_preserving_at_least_one_candidate': _width_survival(family_rows, minimum_candidate_count=1),
        'maximum_width_floor_preserving_at_least_two_candidates': _width_survival(family_rows, minimum_candidate_count=2),
        'width_floor_profiles': candidate_counts,
    }


def _profile_lookup(profiles: list[dict[str, object]], name: str) -> dict[str, object]:
    return next(profile for profile in profiles if profile['profile_name'] == name)


def _count_at_floor(profile: dict[str, object], floor: float) -> int:
    row = next(item for item in profile['width_floor_profiles'] if abs(float(item['minimum_shared_core_width']) - floor) <= 1e-12)
    return int(row['candidate_count'])


def _build_summary(rows: list[dict[str, object]]) -> dict[str, object]:
    profiles = [_family_profile(rows, spec) for spec in FAMILY_PROFILES]
    family10 = _profile_lookup(profiles, 'caps_10_20_50_100_sub0p01')
    family4 = _profile_lookup(profiles, 'caps_4_10_20_50_100_sub0p01')
    max1_ratio = float(family10['maximum_width_floor_preserving_at_least_one_candidate']) / float(family4['maximum_width_floor_preserving_at_least_one_candidate'])
    max2_ratio = float(family10['maximum_width_floor_preserving_at_least_two_candidates']) / float(family4['maximum_width_floor_preserving_at_least_two_candidates'])
    return {
        'focus': 'Show that the declared budget family is itself a substantive choice: the same low-delta rematch cores can be comfortably publishable under one family of caps and completely non-viable under another, even before any priority profile is applied.',
        'headline_findings': {
            'caps_10_20_50_100_sub0p01_candidate_count_before_width_floor': int(family10['candidate_count_before_width_floor']),
            'caps_4_10_20_50_100_sub0p01_candidate_count_before_width_floor': int(family4['candidate_count_before_width_floor']),
            'caps_10_20_50_100_sub0p01_candidate_count_at_width_0p0010': _count_at_floor(family10, 0.0010),
            'caps_4_10_20_50_100_sub0p01_candidate_count_at_width_0p0010': _count_at_floor(family4, 0.0010),
            'caps_10_20_50_100_maximum_width_floor_preserving_at_least_one_candidate': float(family10['maximum_width_floor_preserving_at_least_one_candidate']),
            'caps_4_10_20_50_100_maximum_width_floor_preserving_at_least_one_candidate': float(family4['maximum_width_floor_preserving_at_least_one_candidate']),
            'caps_10_20_50_100_maximum_width_floor_preserving_at_least_two_candidates': float(family10['maximum_width_floor_preserving_at_least_two_candidates']),
            'caps_4_10_20_50_100_maximum_width_floor_preserving_at_least_two_candidates': float(family4['maximum_width_floor_preserving_at_least_two_candidates']),
            'single_candidate_width_floor_ratio_family10_over_family4': round(max1_ratio, 6),
            'two_candidate_width_floor_ratio_family10_over_family4': round(max2_ratio, 6),
            'interpretation': 'The budget-family declaration is not harmless metadata. In the current proxy, both exact families expose four hazard-clear sub-0.01 cores before width filtering, but the cap-4-inclusive family only supports micro-islands: no candidate survives a 0.0010 width floor, whereas the 10/20/50/100 family still supports two. So a low-delta benchmark constant is only available after the archive declares which cap family actually matters.',
        },
        'method_note': 'Started from the canonical family cores in the publishability snapshot, restricted to sub-0.01 cores with no overlap with the >1000-extra-seed hazard bands. Then compared two exact budget-family declarations already present in the data: caps 10/20/50/100 versus caps 4/10/20/50/100. For each family, recorded how many candidates survive a few representative width floors plus the largest width floor that still preserves at least one and at least two candidates.',
        'family_profiles': profiles,
        'source_report': 'artifacts/reports/rematch_proxy_delta_publishability_snapshot_20260306.json',
        'source_script': 'scripts/report/build_rematch_proxy_delta_family_viability_snapshot.py',
    }


def _write_markdown(summary: dict[str, object]) -> None:
    findings = summary['headline_findings']
    profiles = summary['family_profiles']
    lines = [
        '# Rematch-Proxy Delta Family Viability Snapshot (2026-03-06)',
        '',
        'Method:',
        '- started from the canonical family cores in the publishability snapshot',
        '- restricted to hazard-clear sub-`0.01` candidates',
        '- compared two exact budget-family declarations already present in the data: `10/20/50/100` versus `4/10/20/50/100`',
        '- measured how much shared-core width each family can support before no candidates remain',
        '',
        'Headline findings:',
        f"- before width filtering, both exact families expose `{findings['caps_10_20_50_100_sub0p01_candidate_count_before_width_floor']}` hazard-clear sub-`0.01` candidates.",
        f"- at width floor `0.0010`, the `10/20/50/100` family still has `{findings['caps_10_20_50_100_sub0p01_candidate_count_at_width_0p0010']}` candidates, while the `4/10/20/50/100` family has `{findings['caps_4_10_20_50_100_sub0p01_candidate_count_at_width_0p0010']}`.",
        f"- the largest width floor that still preserves at least one candidate is `{float(findings['caps_10_20_50_100_maximum_width_floor_preserving_at_least_one_candidate']):.5f}` for `10/20/50/100` versus `{float(findings['caps_4_10_20_50_100_maximum_width_floor_preserving_at_least_one_candidate']):.5f}` for `4/10/20/50/100` (`{float(findings['single_candidate_width_floor_ratio_family10_over_family4']):.3f}x` larger).",
        f"- the largest width floor that still preserves at least two candidates is `{float(findings['caps_10_20_50_100_maximum_width_floor_preserving_at_least_two_candidates']):.5f}` for `10/20/50/100` versus `{float(findings['caps_4_10_20_50_100_maximum_width_floor_preserving_at_least_two_candidates']):.5f}` for `4/10/20/50/100` (`{float(findings['two_candidate_width_floor_ratio_family10_over_family4']):.3f}x` larger).",
        '',
        'Exact family profiles:',
    ]
    for profile in profiles:
        lines.append(f"- `{profile['profile_name']}` ({profile['label']}): `{profile['candidate_count_before_width_floor']}` candidates before width filtering; max floor preserving >=1 candidate `{float(profile['maximum_width_floor_preserving_at_least_one_candidate']):.5f}`; max floor preserving >=2 candidates `{float(profile['maximum_width_floor_preserving_at_least_two_candidates']):.5f}`.")
        for floor_profile in profile['width_floor_profiles']:
            lines.append(f"  - width `>= {float(floor_profile['minimum_shared_core_width']):.5f}` -> `{int(floor_profile['candidate_count'])}` candidates.")
    lines.extend([
        '',
        'Why this matters for the archive:',
        '- The budget-family declaration itself belongs in the public contract. It should be justified before the archive starts talking about width floors, guardrail shortlists, or priority profiles.',
        '- In this proxy, saying "the family is everything from cap 4 upward" effectively forbids a robust low-delta constant under the current width floor, even though the `10/20/50/100` family still supports one.',
        '- So future inheritors should resist the temptation to treat the family as an implicit byproduct of which caps happened to be tested. It changes whether a scalar anchor exists at all.',
        '',
    ])
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')


def main() -> None:
    rows = _load_rows()
    summary = _build_summary(rows)
    OUT_JSON.write_text(json.dumps(_round(summary), indent=2, sort_keys=True) + '\n', encoding='utf-8')
    _write_markdown(summary)
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
