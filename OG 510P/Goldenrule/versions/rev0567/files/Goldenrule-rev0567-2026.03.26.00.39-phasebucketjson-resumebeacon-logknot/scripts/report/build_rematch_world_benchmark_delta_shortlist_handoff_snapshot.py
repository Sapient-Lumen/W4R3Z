#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_delta_shortlist_handoff.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_delta_shortlist_handoff_snapshot_20260317.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_delta_shortlist_handoff_snapshot_20260317.md'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def render_md(report: dict[str, Any]) -> str:
    anchors = ', '.join(f"`{delta}`" for delta in report['primary_anchor_deltas'])
    topologies = ', '.join(f"`{code}`" for code in report['primary_topology_codes'])
    return '\n'.join([
        '# Rematch-world benchmark delta shortlist handoff snapshot — 2026-03-17',
        '',
        f"Focus: {report['focus']}",
        '',
        '## Local result',
        '',
        '- The benchmark seed now carries one compact publishable-delta shortlist handoff copied from the strict proxy-era guardrail profile instead of forcing inheritors to reopen the wider SESOI frontier, hazard, and persistence reports.',
        f"- The copied shortlist stays tight: `{report['primary_shortlist_count']}` primary rows across the declared budget family `{report['declared_budget_family_caps']}`, with anchors {anchors} and topology codes {topologies}.",
        f"- The handoff keeps only the strict sub-`0.01` shortlist while still recording that the broader width-qualified profile had `{report['broader_profile_candidate_count']}` total candidates before the sub-`0.01` filter.",
        '',
        '## Implementor guidance',
        '',
        '- Treat the copied shortlist as the first benchmark-constant menu for `SQ-022` through `SQ-026`, not as a replacement for native world outputs.',
        '- Keep the shortlist frozen until endogenous rematch benchmarks can emit their own practical-margin frontier, budget-admissible band, and topology-stable anchor surfaces.',
        '- Retain only the shortlist rows and digests in benchmark artifacts; keep wider hazard maps and ladder tables scratch-only or in cited reports.',
        '',
    ])


def main() -> int:
    handoff = load_json(EXAMPLE)
    report = {
        'snapshot_date': '2026-03-17',
        'focus': 'wire a compact publishable-delta shortlist directly into the rematch-world benchmark seed so future implementors can start SESOI planning from one frozen handoff packet',
        'analysis_script': 'scripts/report/build_rematch_world_benchmark_delta_shortlist_handoff_snapshot.py',
        'publishability_report_path': handoff['publishability_report_path'],
        'publishability_report_sha256': handoff['publishability_report_sha256'],
        'decision_contract_path': handoff['decision_contract_path'],
        'decision_contract_sha256': handoff['decision_contract_sha256'],
        'primary_shortlist_count': len(handoff['primary_shortlist_rows']),
        'declared_budget_family_caps': handoff['declared_budget_family_caps'],
        'primary_anchor_deltas': [row['shared_core_anchor_delta'] for row in handoff['primary_shortlist_rows']],
        'primary_topology_codes': [row['topology_code'] for row in handoff['primary_shortlist_rows']],
        'broader_profile_candidate_count': handoff['broader_profile_candidate_count'],
        'recommended_next_move': 'Keep the copied shortlist frozen in the benchmark seed and prefer these strict-profile anchors first until endogenous rematch worlds can emit native SESOI-band outputs.',
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(report) + '\n', encoding='utf-8')
    print(f'rematch-world-benchmark-delta-shortlist-handoff-snapshot: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'rematch-world-benchmark-delta-shortlist-handoff-snapshot: wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
