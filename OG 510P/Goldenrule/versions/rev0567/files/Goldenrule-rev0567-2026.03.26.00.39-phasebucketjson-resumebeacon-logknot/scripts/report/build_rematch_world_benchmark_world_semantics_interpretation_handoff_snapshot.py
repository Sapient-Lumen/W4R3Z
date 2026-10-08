#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_world_semantics_interpretation_handoff.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_world_semantics_interpretation_handoff_snapshot_20260317.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_world_semantics_interpretation_handoff_snapshot_20260317.md'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def render_md(report: dict[str, Any]) -> str:
    return '\n'.join([
        '# Rematch-world benchmark world-semantics interpretation handoff snapshot — 2026-03-17',
        '',
        f"Focus: {report['focus']}",
        '',
        '## Local result',
        '',
        '- The benchmark seed now carries one compact world-semantics interpretation handoff copied from the standing publication contract and role-assignment notes.',
        f"- The copied handoff keeps the key SQ-012 boundary explicit: `{report['minimal_world_semantics_field_count']}` minimal disclosure fields and `{report['section_publication_field_count']}` publication fields must be named before rematch-world claims are treated as comparable.",
        '- It also keeps the conservative posture explicit: run one fixed-role benchmark, run one role-swapped companion benchmark when asymmetry is in play, and treat materially changing claims as provisional rather than general.',
        '',
        '## Implementor guidance',
        '',
        '- Treat the copied handoff as the first benchmark-facing summary for SQ-012, not as a replacement for native world semantics output.',
        '- Keep role assignment, asymmetry triggers, carry, reset, and role-swapped companion policy together inside the world semantics section so seat effects do not disappear into engine defaults.',
        '- Replace the copied handoff once endogenous rematch worlds emit world-owned role and carry/reset semantics directly.',
        '',
    ])


def main() -> int:
    handoff = load_json(EXAMPLE)
    report = {
        'snapshot_date': '2026-03-17',
        'focus': 'wire a compact world-semantics interpretation summary directly into the rematch-world benchmark seed so future implementors can cite one frozen packet for role assignment, state carry, and companion-run disclosure',
        'analysis_script': 'scripts/report/build_rematch_world_benchmark_world_semantics_interpretation_handoff_snapshot.py',
        'publication_contract_report_path': handoff['publication_contract_report_path'],
        'publication_contract_report_sha256': handoff['publication_contract_report_sha256'],
        'role_assignment_note_path': handoff['role_assignment_note_path'],
        'role_assignment_note_sha256': handoff['role_assignment_note_sha256'],
        'inheritor_brief_path': handoff['inheritor_brief_path'],
        'inheritor_brief_sha256': handoff['inheritor_brief_sha256'],
        'minimal_world_semantics_field_count': len(handoff['disclosure_boundary_summary']['minimal_world_semantics_fields']),
        'section_publication_field_count': len(handoff['disclosure_boundary_summary']['section_publication_fields']),
        'role_swapped_companion_required_when_asymmetry_is_in_play': handoff['role_semantics_interpretation']['role_swapped_companion_required_when_asymmetry_is_in_play'],
        'recommended_next_move': 'Keep the copied world-semantics interpretation handoff frozen in the benchmark seed and use it to guide the native world semantics fill until endogenous rematch runs can emit role/carry semantics directly.',
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(report) + '\n', encoding='utf-8')
    print(f'rematch-world-benchmark-world-semantics-interpretation-handoff-snapshot: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'rematch-world-benchmark-world-semantics-interpretation-handoff-snapshot: wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
