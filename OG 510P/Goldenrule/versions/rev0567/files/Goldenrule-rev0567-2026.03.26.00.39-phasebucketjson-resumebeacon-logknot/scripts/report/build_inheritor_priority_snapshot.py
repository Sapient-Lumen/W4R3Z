#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = ROOT / 'specs' / 'spec_ledger.yaml'
RISK_PATH = ROOT / 'specs' / 'risk_register.yaml'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'inheritor_priority_snapshot_20260316.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'inheritor_priority_snapshot_20260316.md'

PHASES = [
    {
        'id': 'phase_1',
        'title': 'Canonicalization contract first',
        'question_ids': ['SQ-003', 'SQ-004', 'SQ-005', 'SQ-006', 'SQ-007', 'SQ-008', 'SQ-009', 'SQ-010', 'SQ-011'],
        'risk_ids': ['RK-007', 'RK-008', 'RK-009', 'RK-010', 'RK-011', 'RK-012', 'RK-013', 'RK-014', 'RK-015'],
        'why_now': 'This layer defines what counts as the same policy family, when caches invalidate, and how planner metadata stays compact enough to vendor into engine-facing artifacts.',
        'deliverables': [
            'world-aware canonicalization contract',
            'planner manifest schema (minimal cache key + exact horizon)',
            'ordered zero-noise classifier contract plus validator coverage',
        ],
    },
    {
        'id': 'phase_2',
        'title': 'World telemetry and comparability contract second',
        'question_ids': ['SQ-012', 'SQ-013', 'SQ-014', 'SQ-015', 'SQ-016'],
        'risk_ids': ['RK-016', 'RK-017', 'RK-018', 'RK-019', 'RK-020', 'RK-021'],
        'why_now': 'This layer prevents false welfare and leaderboard stories by requiring explicit role policy, matched-vs-searching accounting, turnover tempo, and paired raw/in-match rankings before the engine surface widens.',
        'deliverables': [
            'explicit role-assignment and rematch-state fields',
            'occupancy + turnover report fields',
            'paired aggregate vs in-match leaderboard contract',
        ],
    },
    {
        'id': 'phase_3',
        'title': 'Compact decision contract third',
        'question_ids': ['SQ-017', 'SQ-018', 'SQ-019', 'SQ-020', 'SQ-021', 'SQ-022', 'SQ-023', 'SQ-024', 'SQ-025', 'SQ-026'],
        'risk_ids': ['RK-022', 'RK-023', 'RK-024', 'RK-025', 'RK-026', 'RK-027', 'RK-028', 'RK-029', 'RK-030'],
        'why_now': 'Ten open questions are already phrased as minimal machine-checkable artifact contracts, which means the archive can retire a large block of ambiguity through compact schema/report fields instead of bulky rerun tables.',
        'deliverables': [
            'delay-robustness + live-contender report contract',
            'winner-certification + budget-aware triage + materiality gate contract',
            'delta frontier/budget/hazard/admissibility/topology-stability contract',
        ],
    },
]


def _load(path: Path) -> list[dict[str, object]]:
    return json.loads(path.read_text(encoding='utf-8'))


def _rows_by_id(rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    return {str(row['id']): row for row in rows}


def build_snapshot() -> dict[str, object]:
    ledger = _load(LEDGER_PATH)
    risks = _load(RISK_PATH)
    ledger_by_id = _rows_by_id(ledger)
    risk_by_id = _rows_by_id(risks)

    open_gaps = [row for row in ledger if row['type'] == 'gap' and row['status'] == 'open']
    open_questions = [row for row in ledger if row['type'] == 'question' and row['status'] == 'open']
    open_assumptions = [row for row in ledger if row['type'] == 'assumption' and row['status'] == 'open']

    gap_rows: list[dict[str, object]] = []
    for gap in open_gaps:
        gid = str(gap['id'])
        assumptions = [str(row['id']) for row in open_assumptions if row.get('linked_gap') == gid]
        questions = [str(row['id']) for row in open_questions if row.get('related_gap') == gid]
        gap_rows.append(
            {
                'gap_id': gid,
                'summary': gap['summary'],
                'owner': gap['owner'],
                'target_resolution': gap['target_resolution'],
                'open_assumption_count': len(assumptions),
                'open_question_count': len(questions),
                'dependent_open_entry_count': len(assumptions) + len(questions),
                'question_ids': questions,
                'assumption_ids': assumptions,
            }
        )
    gap_rows.sort(key=lambda row: (int(row['dependent_open_entry_count']), str(row['gap_id'])), reverse=True)

    phase_rows: list[dict[str, object]] = []
    for phase in PHASES:
        question_rows = [ledger_by_id[qid] for qid in phase['question_ids']]
        risk_rows = [risk_by_id[rid] for rid in phase['risk_ids']]
        phase_rows.append(
            {
                'id': phase['id'],
                'title': phase['title'],
                'question_ids': phase['question_ids'],
                'risk_ids': phase['risk_ids'],
                'question_count': len(question_rows),
                'risk_count': len(risk_rows),
                'why_now': phase['why_now'],
                'deliverables': phase['deliverables'],
                'question_summaries': [str(row['summary']) for row in question_rows],
                'risk_summaries': [str(row['summary']) for row in risk_rows],
            }
        )

    sg3 = next(row for row in gap_rows if row['gap_id'] == 'SG-003')
    machine_checkable_questions = [
        str(row['id'])
        for row in open_questions
        if row.get('related_gap') == 'SG-003' and 'minimal machine-checkable' in str(row['summary']).lower()
    ]

    findings = [
        f"`SG-003` dominates the open ledger with {sg3['dependent_open_entry_count']} dependent open entries ({sg3['open_assumption_count']} assumptions + {sg3['open_question_count']} questions); the other two gaps each carry only 2 dependent open entries.",
        f"The final SG-003 tranche is already compact-contract-shaped: {len(machine_checkable_questions)} open questions are explicitly phrased as minimal machine-checkable artifact contracts rather than as requests for larger raw experiment dumps.",
        'The risk register already falls into the same three-layer order: canonicalization drift first, comparability/telemetry second, and compact decision contracts third.',
        'That means the next implementor should retire SG-003 by narrowing contracts in sequence, not by widening the archive with more undifferentiated benchmark tables.',
    ]

    recommendations = [
        'Land the planner-manifest and canonicalization contract before engine-level rematch search expands.',
        'Treat role policy, occupancy accounting, turnover tempo, and paired raw/in-match rankings as required report fields for the first endogenous rematch world.',
        'For the top-gap decision layer, prefer compact frontier metadata over storing dense delta grids or repeated full leaderboards.',
    ]

    return {
        'focus': 'prioritize the smallest set of inheritor-facing contracts that collapses the largest open rematch backlog without regrowing the archive',
        'snapshot_date': '2026-03-16',
        'open_gap_overview': gap_rows,
        'sg003_three_phase_plan': phase_rows,
        'headline_findings': findings,
        'recommendations': recommendations,
        'analysis_script': 'scripts/report/build_inheritor_priority_snapshot.py',
    }


def render_md(report: dict[str, object]) -> str:
    lines: list[str] = []
    lines.append('# Inheritor priority snapshot — 2026-03-16')
    lines.append('')
    lines.append(f"Focus: {report['focus']}")
    lines.append('')
    lines.append('## Headline findings')
    for item in report['headline_findings']:
        lines.append(f'- {item}')
    lines.append('')
    lines.append('## Open gap overview')
    lines.append('')
    lines.append('| gap | dependent open entries | assumptions | questions | target | summary |')
    lines.append('|---|---:|---:|---:|---|---|')
    for row in report['open_gap_overview']:
        lines.append(
            f"| `{row['gap_id']}` | `{row['dependent_open_entry_count']}` | `{row['open_assumption_count']}` | `{row['open_question_count']}` | `{row['target_resolution']}` | {row['summary']} |"
        )
    lines.append('')
    lines.append('## SG-003 should be retired in three compact layers')
    lines.append('')
    for phase in report['sg003_three_phase_plan']:
        lines.append(f"### {phase['title']}")
        lines.append('')
        lines.append(f"- questions: `{phase['question_count']}` -> {', '.join(f'`{qid}`' for qid in phase['question_ids'])}")
        lines.append(f"- linked risks: `{phase['risk_count']}` -> {', '.join(f'`{rid}`' for rid in phase['risk_ids'])}")
        lines.append(f"- why now: {phase['why_now']}")
        lines.append('- compact deliverables:')
        for item in phase['deliverables']:
            lines.append(f'  - {item}')
        lines.append('')
    lines.append('## Recommended order for the next implementor')
    for idx, item in enumerate(report['recommendations'], start=1):
        lines.append(f'{idx}. {item}')
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    report = build_snapshot()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(report) + '\n', encoding='utf-8')
    print(f'inheritor-priority: wrote {OUT_JSON}')
    print(f'inheritor-priority: wrote {OUT_MD}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
