#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_canonical_anchor_labels_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_canonical_anchor_labels_snapshot_20260308.md'
TOLERANCE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_tolerance_staircase_snapshot_20260308.json'
OVERLAP_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_repeat_uncertainty_snapshot_20260307.json'

ORDER = ['near_exact', 'near_optimal', 'lower_guarantee']


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _centers(start: int, end: int) -> list[int]:
    width = end - start + 1
    if width % 2 == 1:
        return [(start + end) // 2]
    midpoint = (start + end) / 2
    return [int(midpoint - 0.5), int(midpoint + 0.5)]


def _prior_overlap_rows() -> dict[float, dict[str, Any]]:
    overlap = _load(OVERLAP_REPORT)
    return {
        float(row['minimum_gain_share_of_full_dynamic_savings']): row
        for row in overlap['uncertainty_rows']
    }


def _tier_rows() -> list[dict[str, Any]]:
    tolerance = _load(TOLERANCE_REPORT)
    prior_rows = _prior_overlap_rows()
    rows: list[dict[str, Any]] = []
    for row in tolerance['tier_rows']:
        guarantee = float(row['minimum_gain_share_of_full_dynamic_savings'])
        start = int(row['exact_dwell_band_start_unique_appends'])
        end = int(row['exact_dwell_band_end_unique_appends'])
        candidates = _centers(start, end)
        canonical = min(candidates)
        prior = prior_rows[guarantee]
        prior_anchor = int(prior['anchor_minimum_dwell_unique_appends'])
        rows.append(
            {
                'tier': str(row['tier']),
                'minimum_gain_share_of_full_dynamic_savings': guarantee,
                'exact_dwell_band_start_unique_appends': start,
                'exact_dwell_band_end_unique_appends': end,
                'exact_dwell_band_width_unique_appends': int(row['exact_dwell_band_width_unique_appends']),
                'center_candidates_unique_appends': candidates,
                'center_candidate_count': len(candidates),
                'canonical_anchor_minimum_dwell_unique_appends': canonical,
                'canonical_anchor_rule': 'single_exact_center' if len(candidates) == 1 else 'lower_of_two_tied_exact_centers',
                'minimum_anchor_slack_unique_appends': int(row['minimum_anchor_slack_unique_appends']),
                'prior_overlap_anchor_minimum_dwell_unique_appends': prior_anchor,
                'canonical_shift_vs_prior_overlap_anchor_unique_appends': canonical - prior_anchor,
            }
        )
    rows.sort(key=lambda item: ORDER.index(item['tier']))
    return rows


def _headline(rows: list[dict[str, Any]]) -> dict[str, Any]:
    indexed = {row['tier']: row for row in rows}
    return {
        'near_exact_canonical_anchor_minimum_dwell_unique_appends': indexed['near_exact']['canonical_anchor_minimum_dwell_unique_appends'],
        'near_optimal_canonical_anchor_minimum_dwell_unique_appends': indexed['near_optimal']['canonical_anchor_minimum_dwell_unique_appends'],
        'lower_guarantee_canonical_anchor_minimum_dwell_unique_appends': indexed['lower_guarantee']['canonical_anchor_minimum_dwell_unique_appends'],
        'near_optimal_has_unique_exact_center': indexed['near_optimal']['center_candidate_count'] == 1,
        'lower_guarantee_tied_exact_centers_unique_appends': indexed['lower_guarantee']['center_candidates_unique_appends'],
        'exact_certification_supersedes_prior_overlap_midpoints': {
            row['tier']: {
                'prior_overlap_anchor_minimum_dwell_unique_appends': row['prior_overlap_anchor_minimum_dwell_unique_appends'],
                'canonical_anchor_minimum_dwell_unique_appends': row['canonical_anchor_minimum_dwell_unique_appends'],
                'canonical_shift_unique_appends': row['canonical_shift_vs_prior_overlap_anchor_unique_appends'],
            }
            for row in rows
        },
        'main_rule': 'name the current exact uncertainty tiers by the lower Chebyshev center of each exact certified dwell band, not by the older midpoint of the looser overlap band; that stabilizes the canonical labels at dwell 2, 13, and 25.',
    }


def _decision_rules() -> list[str]:
    return [
        'When an uncertainty tier has an exact certified dwell band, derive its stable label from the center of that exact band rather than from the older midpoint of the broader overlap band.',
        'Use dwell 13 as the canonical label for the exact 0.95 tier because 8-18 has a unique exact center at 13, which also maximizes the minimum slack on both sides of the band.',
        'Use dwell 25 as the canonical label for the exact 0.85 tier because 19-32 has two tied exact centers, 25 and 26, and the archive should break that tie deterministically toward the lower dwell.',
        'Treat dwell 2 as the canonical label for the exact 0.99 precision tier because its exact band has width 1 and no representative ambiguity.',
        'Treat the older overlap anchors 1, 9, and 16 as historical scaffolding only; once the exact bands are certified, the stable inheritor-facing labels are 2, 13, and 25.',
    ]


def _build_report() -> dict[str, Any]:
    rows = _tier_rows()
    return {
        'focus': 'Stabilize the exact uncertainty-tier names by deriving canonical anchors from the centers of the exact certified dwell bands, so future inheritors stop mixing the newer exact labels with the older overlap-midpoint labels.',
        'headline_findings': _headline(rows),
        'decision_rules': _decision_rules(),
        'tier_rows': rows,
        'source_reports': [
            str(TOLERANCE_REPORT.relative_to(ROOT)),
            str(OVERLAP_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state canonical anchor labels snapshot — 2026-03-08')
    lines.append('')
    lines.append(f"Focus: {report['focus']}")
    lines.append('')
    lines.append('## Headline findings')
    for key, value in report['headline_findings'].items():
        lines.append(f'- **{key}**: `{json.dumps(value, ensure_ascii=False)}`')
    lines.append('')
    lines.append('## Tier rows')
    for row in report['tier_rows']:
        lines.append(
            '- '
            f"{row['tier']}: guarantee `{row['minimum_gain_share_of_full_dynamic_savings']}`; "
            f"exact band `{row['exact_dwell_band_start_unique_appends']}-{row['exact_dwell_band_end_unique_appends']}`; "
            f"center candidates `{row['center_candidates_unique_appends']}`; "
            f"canonical anchor `{row['canonical_anchor_minimum_dwell_unique_appends']}` via `{row['canonical_anchor_rule']}`; "
            f"prior overlap anchor `{row['prior_overlap_anchor_minimum_dwell_unique_appends']}`; "
            f"shift `{row['canonical_shift_vs_prior_overlap_anchor_unique_appends']:+d}`"
        )
    lines.append('')
    lines.append('## Decision rules')
    for rule in report['decision_rules']:
        lines.append(f'- {rule}')
    lines.append('')
    lines.append('## Sources')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['source_script']}`")
    lines.append('')
    return '\n'.join(lines)


def main() -> None:
    report = _build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    OUT_MD.write_text(_render_md(report))
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
