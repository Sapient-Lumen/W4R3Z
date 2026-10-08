#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
UNCERTAINTY_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_repeat_uncertainty_snapshot_20260307.json'
GUARDRAIL_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_guardrails_snapshot_20260308.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_lower_guarantee_three_cap_snapshot_20260308.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_lower_guarantee_three_cap_snapshot_20260308.md'

TARGET_GAIN_SHARE = 0.85
REFERENCE_REPEAT_VALUES = [0.15, 0.18, 0.25]
INTERVAL_RE = re.compile(r'(?P<kind>[a-z\-]+) (?P<start>\d+)–(?P<end>\d+)$')


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _transition_boundaries(interval_summary: str) -> list[int]:
    points: list[int] = []
    for chunk in interval_summary.split('; ')[1:]:
        match = INTERVAL_RE.fullmatch(chunk)
        if match is None:
            raise ValueError(f'unexpected interval chunk: {chunk!r}')
        points.append(int(match.group('start')))
    return points


def _contiguous_bands(values: list[int]) -> list[dict[str, int]]:
    if not values:
        return []
    bands: list[dict[str, int]] = []
    start = values[0]
    end = values[0]
    for value in values[1:]:
        if value == end + 1:
            end = value
            continue
        bands.append({
            'band_start_unique_appends': start,
            'band_end_unique_appends': end,
            'band_width_unique_appends': end - start + 1,
        })
        start = end = value
    bands.append({
        'band_start_unique_appends': start,
        'band_end_unique_appends': end,
        'band_width_unique_appends': end - start + 1,
    })
    return bands


def _build_summary() -> dict[str, Any]:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    frontier_builder = _load_module(FRONTIER_BUILDER_PATH, 'frontier_snapshot')
    uncertainty = _load(UNCERTAINTY_REPORT)
    old_guardrail = _load(GUARDRAIL_REPORT)

    deterministic_packets = frontier_builder._frontier_test_packets(packet)
    fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in deterministic_packets]
    pages = packet.fingerprint_catalog_pages(fingerprints, page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE)
    horizon_metrics = packet.fingerprint_catalog_compact_repeat_state_horizon_metrics(
        pages,
        max_unique_appends=256,
        page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
    )

    per_repeat_frontiers = {
        expected_repeat_lookups: packet.fingerprint_catalog_compact_repeat_state_min_dwell_frontier_from_metrics(
            horizon_metrics,
            expected_repeat_lookups=expected_repeat_lookups,
        )
        for expected_repeat_lookups in REFERENCE_REPEAT_VALUES
    }

    uncertainty_row = next(
        row for row in uncertainty['uncertainty_rows']
        if float(row['minimum_gain_share_of_full_dynamic_savings']) == TARGET_GAIN_SHARE
    )
    prior_guardrail_row = next(
        row for row in old_guardrail['guardrail_rows']
        if float(row['minimum_gain_share_of_full_dynamic_savings']) == TARGET_GAIN_SHARE
    )

    cap_rows: list[dict[str, Any]] = []
    exact_minimum_cap: int | None = None
    exact_bands: list[dict[str, int]] = []
    for cap in range(max(frontier['dynamic_transition_count'] for frontier in per_repeat_frontiers.values()) + 1):
        feasible_dwells: list[int] = []
        for dwell in range(1, int(horizon_metrics['max_unique_appends']) + 1):
            if dwell > int(uncertainty_row['minimum_dwell_overlap_end_unique_appends']):
                break
            if all(
                frontier['dwell_rows'][dwell - 1]['gain_share_of_full_dynamic_savings'] >= TARGET_GAIN_SHARE
                and frontier['dwell_rows'][dwell - 1]['selected_transition_count'] <= cap
                for frontier in per_repeat_frontiers.values()
            ):
                feasible_dwells.append(dwell)
        bands = _contiguous_bands(feasible_dwells)
        cap_row = {
            'candidate_hard_cap': cap,
            'feasible_dwell_count': len(feasible_dwells),
            'feasible_dwell_bands': bands,
            'is_feasible': bool(feasible_dwells),
        }
        if cap == 2:
            focal_best = max(
                (
                    row for row in per_repeat_frontiers[0.18]['dwell_rows']
                    if row['selected_transition_count'] <= 2
                ),
                key=lambda row: (
                    row['gain_share_of_full_dynamic_savings'],
                    -row['selected_transition_count'],
                    -row['minimum_dwell_unique_appends'],
                ),
            )
            cap_row['infeasibility_witness'] = {
                'expected_repeat_lookups': 0.18,
                'best_gain_share_of_full_dynamic_savings_under_cap': float(focal_best['gain_share_of_full_dynamic_savings']),
                'best_minimum_dwell_unique_appends_under_cap': int(focal_best['minimum_dwell_unique_appends']),
                'best_selected_transition_count_under_cap': int(focal_best['selected_transition_count']),
                'best_interval_summary_under_cap': str(focal_best['interval_summary']),
            }
        cap_rows.append(cap_row)
        if exact_minimum_cap is None and feasible_dwells:
            exact_minimum_cap = cap
            exact_bands = bands

    assert exact_minimum_cap is not None
    assert exact_bands
    promoted_band = max(
        exact_bands,
        key=lambda row: (row['band_width_unique_appends'], row['band_end_unique_appends']),
    )
    anchor = (promoted_band['band_start_unique_appends'] + promoted_band['band_end_unique_appends']) // 2
    margin = min(anchor - promoted_band['band_start_unique_appends'], promoted_band['band_end_unique_appends'] - anchor)

    lane_rows: list[dict[str, Any]] = []
    union_checkpoints: set[int] = set()
    for expected_repeat_lookups in REFERENCE_REPEAT_VALUES:
        dwell_row = per_repeat_frontiers[expected_repeat_lookups]['dwell_rows'][anchor - 1]
        checkpoints = _transition_boundaries(str(dwell_row['interval_summary']))
        union_checkpoints.update(checkpoints)
        lane_rows.append({
            'expected_repeat_lookups': expected_repeat_lookups,
            'selected_transition_count': int(dwell_row['selected_transition_count']),
            'gain_share_of_full_dynamic_savings': float(dwell_row['gain_share_of_full_dynamic_savings']),
            'regret_vs_unbounded_dynamic': float(dwell_row['regret_vs_unbounded_dynamic']),
            'interval_summary': str(dwell_row['interval_summary']),
            'transition_boundaries_unique_appends': checkpoints,
        })

    findings = {
        'target_minimum_gain_share_of_full_dynamic_savings': TARGET_GAIN_SHARE,
        'reference_expected_repeat_lookups_values': REFERENCE_REPEAT_VALUES,
        'promoted_exact_band_wide_hard_cap': exact_minimum_cap,
        'promoted_exact_band_start_unique_appends': promoted_band['band_start_unique_appends'],
        'promoted_exact_band_end_unique_appends': promoted_band['band_end_unique_appends'],
        'promoted_exact_band_width_unique_appends': promoted_band['band_width_unique_appends'],
        'promoted_exact_anchor_minimum_dwell_unique_appends': anchor,
        'promoted_exact_anchor_margin_unique_appends': margin,
        'anchor_worst_case_gain_share_of_full_dynamic_savings': min(
            row['gain_share_of_full_dynamic_savings'] for row in lane_rows
        ),
        'anchor_transition_range': {
            'minimum_selected_transition_count': min(row['selected_transition_count'] for row in lane_rows),
            'maximum_selected_transition_count': max(row['selected_transition_count'] for row in lane_rows),
        },
        'anchor_union_transition_checkpoints_unique_appends': sorted(union_checkpoints),
        'anchor_union_transition_checkpoint_count': len(union_checkpoints),
        'four_cap_expands_feasible_band': cap_rows[4]['feasible_dwell_bands'] != exact_bands,
        'prior_guardrail_status': str(prior_guardrail_row['band_wide_hard_cap_status']),
        'prior_guardrail_cap': int(prior_guardrail_row['certified_band_wide_feasible_hard_cap']),
        'main_rule': 'when the archive explicitly relaxes the uncertainty-safe guarantee to 0.85 on the current repeat reference band, promote dwell 19–32 from planning folklore to an exact three-transition lane; a four-transition budget buys no extra dwell coverage there.',
    }

    return {
        'focus': 'Close the last open compact repeat-sidecar operating-mode point by certifying the exact hard-cap floor for the lower-guarantee repeat-uncertainty lane instead of leaving it as a conservative planning inference.',
        'headline_findings': findings,
        'cap_feasibility_rows': cap_rows,
        'promoted_lane_rows': lane_rows,
        'decision_rules': [
            'If the archive is allowed to relax to gain share 0.85 across repeat budgets 0.15, 0.18, and 0.25, use dwell band 19–32 with representative anchor 25 and hard cap 3.',
            'Stop calling the lower-guarantee lane a conservative four-cap planning mode; on the saved frontier it is an exact three-cap certification.',
            'Do not promise a two-transition lower-guarantee lane on the current repeat band: the focal 0.18 frontier can only reach cap 2 after gain share has already fallen to 0.510201 at dwell 49.',
            'A four-transition budget adds nothing to the lower-guarantee lane on the saved frontier because the feasible dwell band under cap 4 is identical to the exact cap-3 band.',
        ],
        'source_reports': [
            str(UNCERTAINTY_REPORT.relative_to(ROOT)),
            str(GUARDRAIL_REPORT.relative_to(ROOT)),
        ],
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
            str(FRONTIER_BUILDER_PATH.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(report: dict[str, Any]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Lower-Guarantee Three-Cap Snapshot — 2026-03-08',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- the lower-guarantee uncertainty lane is now exact, not provisional: gain share `{findings['target_minimum_gain_share_of_full_dynamic_savings']}` across repeat budgets `{findings['reference_expected_repeat_lookups_values']}` can be kept with hard cap `{findings['promoted_exact_band_wide_hard_cap']}` on dwell band `{findings['promoted_exact_band_start_unique_appends']}`–`{findings['promoted_exact_band_end_unique_appends']}`.",
        f"- the representative anchor is dwell `{findings['promoted_exact_anchor_minimum_dwell_unique_appends']}` with ±`{findings['promoted_exact_anchor_margin_unique_appends']}` margin; its worst-case preserved gain share is `{findings['anchor_worst_case_gain_share_of_full_dynamic_savings']}` and its transition range across the current repeat band is `{findings['anchor_transition_range']['minimum_selected_transition_count']}`–`{findings['anchor_transition_range']['maximum_selected_transition_count']}`.",
        f"- the finite checkpoint union for that promoted lane is `{findings['anchor_union_transition_checkpoints_unique_appends']}`; only `{findings['anchor_union_transition_checkpoint_count']}` checkpoint values matter across the whole saved repeat band.",
        f"- cap `2` is impossible at this guarantee on the current frontier, while cap `4` buys no extra dwell coverage beyond cap `3`: `four_cap_expands_feasible_band = {findings['four_cap_expands_feasible_band']}`.",
        f"- this supersedes the prior guardrail status `{findings['prior_guardrail_status']}` with conservative cap `{findings['prior_guardrail_cap']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Cap feasibility by hard-cap budget',
        '| hard cap | feasible dwell bands at gain share 0.85 | feasible? | note |',
        '|---:|---|---|---|',
    ]
    for row in report['cap_feasibility_rows']:
        bands = ', '.join(
            f"{band['band_start_unique_appends']}–{band['band_end_unique_appends']}"
            for band in row['feasible_dwell_bands']
        ) or 'none'
        note = ''
        witness = row.get('infeasibility_witness')
        if witness is not None:
            note = (
                f"best focal 0.18 row under this cap is dwell {witness['best_minimum_dwell_unique_appends_under_cap']} "
                f"with gain share {witness['best_gain_share_of_full_dynamic_savings_under_cap']}"
            )
        lines.append(f"| {row['candidate_hard_cap']} | {bands} | {row['is_feasible']} | {note} |")
    lines.extend([
        '',
        '## Promoted exact lane at representative anchor',
        '| repeat budget | transitions | gain share | regret vs full dynamic | checkpoints | summary |',
        '|---:|---:|---:|---:|---|---|',
    ])
    for row in report['promoted_lane_rows']:
        lines.append(
            f"| {row['expected_repeat_lookups']} | {row['selected_transition_count']} | {row['gain_share_of_full_dynamic_savings']} | {row['regret_vs_unbounded_dynamic']} | {row['transition_boundaries_unique_appends']} | {row['interval_summary']} |"
        )
    lines.extend([
        '',
        '## Decision rules',
    ])
    for rule in report['decision_rules']:
        lines.append(f'- {rule}')
    lines.extend([
        '',
        '## Sources',
    ])
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    for source in report['sources']:
        lines.append(f'- `{source}`')
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = _build_summary()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    OUT_MD.write_text(_render_md(report))
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
