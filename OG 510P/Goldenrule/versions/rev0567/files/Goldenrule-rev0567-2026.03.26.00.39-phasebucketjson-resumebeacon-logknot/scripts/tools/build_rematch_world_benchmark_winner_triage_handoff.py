#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
LIVE_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_live_contenders_snapshot_20260306.json'
WINNER_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_winner_certification_snapshot_20260306.json'
MATERIALITY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_materiality_gate_snapshot_20260306.json'
DECISION_CONTRACT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_winner_triage_handoff.schema.json'
LINKED_QUESTION_IDS = ['SQ-018', 'SQ-019', 'SQ-020', 'SQ-021']


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def sha256_json(node: Any) -> str:
    blob = json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(blob).hexdigest()


def _ordered_union(rows: list[list[str]]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for row in rows:
        for item in row:
            if item not in seen:
                seen.add(item)
                ordered.append(item)
    return ordered


def _compact_uncertified_panel(row: dict[str, Any]) -> dict[str, Any]:
    return {
        'extortion': row['extortion'],
        'delay': row['delay'],
        'leader': row['leader'],
        'runner_up': row['runner_up'],
        'leader_margin': row['leader_margin'],
        'leader_margin_ci_low': row['leader_margin_ci_low'],
        'leader_margin_ci_high': row['leader_margin_ci_high'],
    }


def _compact_materiality_panel(row: dict[str, Any]) -> dict[str, Any]:
    return {
        'extortion': row['extortion'],
        'delay': row['delay'],
        'leader': row['leader'],
        'runner_up': row['runner_up'],
        'leader_margin': row['leader_margin'],
        'leader_certified_95_ci': row['leader_certified_95_ci'],
        'smallest_equivalence_delta_supported_90': row['smallest_equivalence_delta_supported_90'],
        'largest_material_delta_supported_90': row['largest_material_delta_supported_90'],
        'delta_classifications': dict(row['delta_classifications']),
    }


def build_handoff(live_report: dict[str, Any], winner_report: dict[str, Any], materiality_report: dict[str, Any], decision_contract: dict[str, Any]) -> dict[str, Any]:
    extortion_rows = live_report['extortion_rows']
    tested_delay_values = sorted({panel['delay'] for row in extortion_rows for panel in row['tested_band_panel_rows']})
    tested_extortion_values = [row['extortion'] for row in extortion_rows]
    live_contender_union = _ordered_union([row['predicted_nonnegative_delay_live_contender_set'] for row in extortion_rows])

    dominated_rows_map: dict[str, list[str]] = {}
    for row in extortion_rows:
        for dom in row['strictly_dominated_policies']:
            dominated_rows_map.setdefault(dom['policy'], list(dom['dominated_by']))
    dominated_rows = [
        {'policy': policy, 'dominated_by': dominated_rows_map[policy]}
        for policy in sorted(dominated_rows_map)
    ]

    return {
        'contract_kind': 'rematch_world_benchmark_winner_triage_handoff',
        'contract_version': '2026-03-17.rematch_world_benchmark_winner_triage_handoff.v1',
        'planner_origin': 'copy the current proxy-era winner triage summary into the benchmark seed until native rematch worlds can emit live-contender, certification, and materiality outputs directly',
        'live_contenders_report_path': 'artifacts/reports/rematch_proxy_live_contenders_snapshot_20260306.json',
        'live_contenders_report_sha256': sha256_json(live_report),
        'winner_certification_report_path': 'artifacts/reports/rematch_proxy_winner_certification_snapshot_20260306.json',
        'winner_certification_report_sha256': sha256_json(winner_report),
        'materiality_gate_report_path': 'artifacts/reports/rematch_proxy_materiality_gate_snapshot_20260306.json',
        'materiality_gate_report_sha256': sha256_json(materiality_report),
        'decision_contract_path': 'artifacts/reports/rematch_decision_contract_snapshot_20260316.json',
        'decision_contract_sha256': sha256_json(decision_contract),
        'linked_question_ids': list(LINKED_QUESTION_IDS),
        'tested_extortion_values': tested_extortion_values,
        'tested_delay_values': tested_delay_values,
        'live_contender_set_union': live_contender_union,
        'leaders_observed_anywhere_in_tested_band': list(live_report['headline_findings']['leaders_observed_anywhere_in_tested_band']),
        'dominated_policy_rows': dominated_rows,
        'winner_certification_summary': {
            'tested_panels': winner_report['headline_findings']['tested_panels'],
            'certified_leaders_95_ci': winner_report['headline_findings']['certified_leaders_95_ci'],
            'uncertified_leaders_95_ci': winner_report['headline_findings']['uncertified_leaders_95_ci'],
            'smallest_certified_leader_margin_ci_low': winner_report['headline_findings']['smallest_certified_leader_margin_ci_low'],
        },
        'uncertified_panel_rows': [_compact_uncertified_panel(row) for row in winner_report['headline_findings']['uncertified_panels']],
        'materiality_summary': {
            'counts_by_delta': dict(materiality_report['headline_findings']['counts_by_delta']),
            'certified_leader_but_practical_tie_at_delta_0_005_count': len(materiality_report['headline_findings']['certified_leader_but_practical_tie_at_delta_0_005']),
            'uncertified_leader_but_practical_tie_at_delta_0_01_count': len(materiality_report['headline_findings']['uncertified_leader_but_practical_tie_at_delta_0_01']),
            'smallest_equivalence_delta_supported_panel': _compact_materiality_panel(materiality_report['headline_findings']['smallest_equivalence_delta_supported_panel']),
            'largest_equivalence_delta_supported_panel': _compact_materiality_panel(materiality_report['headline_findings']['largest_equivalence_delta_supported_panel']),
        },
        'upgrade_requirement': 'Replace this copied winner-triage handoff with world-native live-contender, winner-certification, and materiality outputs once endogenous rematch benchmarks can emit those sections directly from real runs.',
        'size_discipline_note': 'Carry only the live-contender union, dominated-policy summary, certification counts, one uncertified panel row, and the materiality edge panels inside the benchmark seed; keep wider per-panel tables in cited reports rather than copying them forward.',
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Build the compact winner-triage handoff section to copy into the rematch-world benchmark seed.')
    parser.add_argument('--live-report', default=str(LIVE_PATH), help='Path to the proxy live-contender snapshot JSON.')
    parser.add_argument('--winner-report', default=str(WINNER_PATH), help='Path to the proxy winner-certification snapshot JSON.')
    parser.add_argument('--materiality-report', default=str(MATERIALITY_PATH), help='Path to the proxy materiality snapshot JSON.')
    parser.add_argument('--decision-contract', default=str(DECISION_CONTRACT_PATH), help='Path to the standing compact decision contract JSON.')
    parser.add_argument('--output', help='Write the handoff JSON to this path instead of stdout.')
    parser.add_argument('--summary-json', action='store_true', help='Emit only a compact summary instead of the full handoff JSON.')
    args = parser.parse_args()

    def resolve(raw: str) -> Path:
        p = Path(raw)
        return p.resolve() if p.is_absolute() else (ROOT / p).resolve()

    handoff = build_handoff(
        load_json(resolve(args.live_report)),
        load_json(resolve(args.winner_report)),
        load_json(resolve(args.materiality_report)),
        load_json(resolve(args.decision_contract)),
    )
    schema = load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(handoff, schema)

    if args.summary_json:
        summary = {
            'live_contenders_report_sha256': handoff['live_contenders_report_sha256'],
            'winner_certification_report_sha256': handoff['winner_certification_report_sha256'],
            'materiality_gate_report_sha256': handoff['materiality_gate_report_sha256'],
            'decision_contract_sha256': handoff['decision_contract_sha256'],
            'live_contender_set_union': handoff['live_contender_set_union'],
            'leaders_observed_anywhere_in_tested_band': handoff['leaders_observed_anywhere_in_tested_band'],
            'uncertified_panel_count': len(handoff['uncertified_panel_rows']),
            'certified_leader_but_practical_tie_at_delta_0_005_count': handoff['materiality_summary']['certified_leader_but_practical_tie_at_delta_0_005_count'],
            'uncertified_leader_but_practical_tie_at_delta_0_01_count': handoff['materiality_summary']['uncertified_leader_but_practical_tie_at_delta_0_01_count'],
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    rendered = json.dumps(handoff, indent=2, sort_keys=True) + '\n'
    if args.output:
        out = resolve(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered, encoding='utf-8')
        print(f'rematch-world-benchmark-winner-triage-handoff: wrote {out.relative_to(ROOT).as_posix()}')
        return 0
    print(rendered, end='')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
