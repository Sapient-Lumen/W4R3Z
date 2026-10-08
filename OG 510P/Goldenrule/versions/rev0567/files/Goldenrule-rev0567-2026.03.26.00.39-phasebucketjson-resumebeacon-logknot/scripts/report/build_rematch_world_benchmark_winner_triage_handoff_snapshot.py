#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_winner_triage_handoff.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_winner_triage_handoff_snapshot_20260317.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_winner_triage_handoff_snapshot_20260317.md'

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))

def render_md(report: dict[str, Any]) -> str:
    return '\n'.join([
        '# Rematch-world benchmark winner triage handoff snapshot — 2026-03-17',
        '',
        f"Focus: {report['focus']}",
        '',
        '## Local result',
        '',
        '- The benchmark seed now carries one compact winner-triage handoff copied from the proxy-era live-contender, winner-certification, and materiality reports.',
        f"- The copied handoff keeps the live contender union `{report['live_contender_set_union']}` and the observed leaders `{report['leaders_observed_anywhere_in_tested_band']}` without reopening the larger decision bundle.",
        f"- It also makes the key triage seam explicit: `{report['uncertified_panel_count']}` uncertified tested panel remains, while `{report['certified_practical_tie_count']}` certified panels already become practical ties at delta `0.005` and `{report['uncertified_practical_tie_count']}` uncertified panel becomes a practical tie at delta `0.01`.",
        '',
        '## Implementor guidance',
        '',
        '- Treat the copied handoff as the first benchmark-facing summary for `SQ-018` through `SQ-021`, not as a replacement for native winner outputs.',
        '- Keep only the compact live-contender union, dominated-policy summary, certification counts, one uncertified panel row, and materiality edge panels in the retained seed.',
        '- Replace the copied handoff once endogenous rematch worlds can emit native live-contender, certification, and materiality sections directly.',
        '',
    ])

def main() -> int:
    handoff = load_json(EXAMPLE)
    report = {
        'snapshot_date': '2026-03-17',
        'focus': 'wire a compact winner-triage summary directly into the rematch-world benchmark seed so future implementors can prioritize live contenders, uncertified flips, and practical ties from one frozen packet',
        'analysis_script': 'scripts/report/build_rematch_world_benchmark_winner_triage_handoff_snapshot.py',
        'live_contenders_report_path': handoff['live_contenders_report_path'],
        'live_contenders_report_sha256': handoff['live_contenders_report_sha256'],
        'winner_certification_report_path': handoff['winner_certification_report_path'],
        'winner_certification_report_sha256': handoff['winner_certification_report_sha256'],
        'materiality_gate_report_path': handoff['materiality_gate_report_path'],
        'materiality_gate_report_sha256': handoff['materiality_gate_report_sha256'],
        'decision_contract_path': handoff['decision_contract_path'],
        'decision_contract_sha256': handoff['decision_contract_sha256'],
        'live_contender_set_union': handoff['live_contender_set_union'],
        'leaders_observed_anywhere_in_tested_band': handoff['leaders_observed_anywhere_in_tested_band'],
        'uncertified_panel_count': len(handoff['uncertified_panel_rows']),
        'certified_practical_tie_count': handoff['materiality_summary']['certified_leader_but_practical_tie_at_delta_0_005_count'],
        'uncertified_practical_tie_count': handoff['materiality_summary']['uncertified_leader_but_practical_tie_at_delta_0_01_count'],
        'recommended_next_move': 'Keep the copied winner-triage handoff frozen in the benchmark seed and prioritize native replication of live-contender, certification, and materiality outputs before widening retained winner-side artifacts.',
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(report) + '\n', encoding='utf-8')
    print(f'rematch-world-benchmark-winner-triage-handoff-snapshot: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'rematch-world-benchmark-winner-triage-handoff-snapshot: wrote {OUT_MD.relative_to(ROOT)}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
