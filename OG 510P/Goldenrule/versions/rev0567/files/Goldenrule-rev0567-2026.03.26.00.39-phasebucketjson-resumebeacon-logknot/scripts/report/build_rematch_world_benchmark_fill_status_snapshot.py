#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.tools.rematch_world_benchmark_completion_gate import (
    DEFAULT_ARTIFACT,
    DEFAULT_DECISION_CONTRACT,
    summarize_completion_status,
    load_json,
)

PUBLICATION_CONTRACT = ROOT / 'artifacts' / 'reports' / 'rematch_world_publication_contract_snapshot_20260316.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_fill_status_snapshot_20260316.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_fill_status_snapshot_20260316.md'
SCHEMA_PATH = 'schemas/rematch_world_benchmark_fill_status.schema.json'
VALIDATOR_PATH = 'scripts/test/check_rematch_world_benchmark_fill_status.py'
SECTION_ORDER = [
    'benchmark_metadata',
    'world_semantics_contract',
    'matching_state_contract',
    'occupancy_accounting_contract',
    'turnover_tempo_contract',
    'paired_ranking_views_contract',
]
SECTION_TITLES = {
    'benchmark_metadata': 'Artifact metadata',
    'world_semantics_contract': 'World semantics contract',
    'matching_state_contract': 'Matching state contract',
    'occupancy_accounting_contract': 'Occupancy accounting contract',
    'turnover_tempo_contract': 'Turnover tempo contract',
    'paired_ranking_views_contract': 'Paired ranking views contract',
}


def build_snapshot() -> dict[str, Any]:
    seed = load_json(DEFAULT_ARTIFACT)
    decision = load_json(DEFAULT_DECISION_CONTRACT)
    publication = load_json(PUBLICATION_CONTRACT)
    status = summarize_completion_status(seed, decision)

    blocker_rows = [
        row for row in status['blocking_slot_rows'] if row['blocker_kind'] in {'template_string', 'null_fill_required'}
    ]

    section_rows: list[dict[str, Any]] = []
    for section in SECTION_ORDER:
        section_blockers = [row for row in blocker_rows if row['section'] == section]
        template_count = sum(1 for row in section_blockers if row['blocker_kind'] == 'template_string')
        null_count = sum(1 for row in section_blockers if row['blocker_kind'] == 'null_fill_required')
        linked_questions = sorted({qid for row in section_blockers for qid in row['linked_question_ids']})
        section_rows.append(
            {
                'section': section,
                'title': SECTION_TITLES[section],
                'linked_question_ids': linked_questions,
                'blocking_slot_count': len(section_blockers),
                'template_blocker_count': template_count,
                'null_blocker_count': null_count,
                'status_transition_required': section != 'benchmark_metadata',
            }
        )

    findings = [
        f"The retained seed is a {status['status_counts']['blocking_slot_count']}-slot fill job rather than a request for new report families: {status['status_counts']['template_blocker_count']} template strings and {status['status_counts']['null_blocker_count']} measured nulls remain outside the copied compact decision bundle.",
        f"Exactly {status['status_counts']['allowed_decision_null_count']} nulls survive inside the copied compact decision bundle, and all of them are legitimate open-ended `end_delay` intervals rather than completion blockers.",
        'A finished endogenous rematch benchmark therefore needs in-place replacement of world-dependent placeholders plus five section-status flips, not a rewrite of the standing compact phase-3 contract.',
        'The next inheritor should use the completion gate to reject accidental placeholder carryover while preserving the copied open-ended delay intervals that already encode current phase-3 semantics.',
    ]

    return {
        'focus': 'turn the one-artifact rematch-world benchmark seed into a measurable fill job with an explicit completion gate',
        'snapshot_date': '2026-03-16',
        'seed_artifact_path': DEFAULT_ARTIFACT.relative_to(ROOT).as_posix(),
        'decision_contract_path': DEFAULT_DECISION_CONTRACT.relative_to(ROOT).as_posix(),
        'publication_contract_path': PUBLICATION_CONTRACT.relative_to(ROOT).as_posix(),
        'completion_ready': status['completion_ready'],
        'completion_gate_rules': [
            'artifact_state must change from `seed_template` to `filled_benchmark` before publication.',
            'World-dependent sections must contain no `TEMPLATE_*` strings and no null telemetry fields.',
            'The five world-dependent section statuses must flip from `pending_fill` to `filled`.',
            'The copied `compact_decision_bundle` must remain identical to the standing compact decision contract unless that contract is intentionally revised at the source.',
            'Open-ended `end_delay: null` intervals that originate inside the copied compact decision bundle are allowed and should not be overwritten just to satisfy a blanket no-null rule.',
        ],
        'section_rows': section_rows,
        'blocking_slot_rows': blocker_rows,
        'allowed_decision_null_rows': status['allowed_decision_null_rows'],
        'status_counts': status['status_counts'],
        'main_findings': findings,
        'recommended_next_move': 'Fill the 24 remaining seed slots in place, flip the five world-section statuses to `filled`, and use the completion gate to ensure the first endogenous benchmark clears placeholders without mutating the copied compact decision bundle.',
        'analysis_script': 'scripts/report/build_rematch_world_benchmark_fill_status_snapshot.py',
        'schema_path': SCHEMA_PATH,
        'validator_path': VALIDATOR_PATH,
        'source_artifacts': [
            publication['analysis_script'],
            publication['validator_path'],
            'scripts/tools/rematch_world_benchmark_completion_gate.py',
        ],
    }


def render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Rematch world benchmark fill-status snapshot — 2026-03-16')
    lines.append('')
    lines.append(f"Focus: {report['focus']}")
    lines.append('')
    lines.append('## Main findings')
    for item in report['main_findings']:
        lines.append(f'- {item}')
    lines.append('')
    lines.append('## Completion gate rules')
    for idx, rule in enumerate(report['completion_gate_rules'], start=1):
        lines.append(f'{idx}. {rule}')
    lines.append('')
    lines.append('## Section fill counts')
    lines.append('')
    lines.append('| section | linked questions | blocking slots | template strings | null fills | status flip required |')
    lines.append('|---|---|---:|---:|---:|---|')
    for row in report['section_rows']:
        linked = ', '.join(f'`{qid}`' for qid in row['linked_question_ids']) if row['linked_question_ids'] else '—'
        lines.append(
            f"| {row['title']} | {linked} | `{row['blocking_slot_count']}` | `{row['template_blocker_count']}` | `{row['null_blocker_count']}` | {'yes' if row['status_transition_required'] else 'no'} |"
        )
    lines.append('')
    lines.append('## Allowed nulls inside the copied compact decision bundle')
    lines.append('')
    for row in report['allowed_decision_null_rows']:
        lines.append(f"- `{row['path']}` — {row['reason']}")
    lines.append('')
    lines.append('## Recommended next move')
    lines.append('')
    lines.append(report['recommended_next_move'])
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    report = build_snapshot()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(report) + '\n', encoding='utf-8')
    print(f'rematch-world-benchmark-fill-status: wrote {OUT_JSON}')
    print(f'rematch-world-benchmark-fill-status: wrote {OUT_MD}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
