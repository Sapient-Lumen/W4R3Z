#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_publication_bundle_receipt.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_phase3_emission_snapshot_20260317.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_phase3_emission_snapshot_20260317.md'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def render_md(report: dict[str, Any]) -> str:
    section_map = ', '.join(f"`{row['section']}`:{row['question_id_count']}" for row in report['emitted_sections'])
    return '\n'.join([
        '# Rematch-world benchmark phase-3 emission snapshot — 2026-03-17',
        '',
        f"Focus: {report['focus']}",
        '',
        '## Local result',
        '',
        f"- The retained publication bundle now carries an explicit phase-3 world-emission proof: `world_emission_ready={str(report['world_emission_ready']).lower()}` and `bundle_matches_standing_contract={str(report['bundle_matches_standing_contract']).lower()}`.",
        f"- The proof is compact: `{report['emitted_question_id_count']}` covered question ids across {section_map}, plus `{report['allowed_open_interval_count']}` allowed open-ended winner intervals that survive by contract rather than by omission.",
        f"- This means the inheritor can cite one retained bundle receipt instead of reopening the compiled benchmark artifact to confirm that `delay_contract`, `winner_contract`, and `delta_contract` are all really emitted.",
        '',
        '## Implementor guidance',
        '',
        '- Treat explicit phase-3 emission as a publication-spine property, not just as an accidental fact about one compiled artifact dump.',
        '- Keep this proof in the retained bundle receipt whenever the benchmark seed copies forward the standing compact decision contract.',
        '- If the decision contract is ever intentionally revised at the source, refresh the emitted question list and digest here instead of adding another bulky benchmark-side note.',
        '',
    ])


def main() -> int:
    receipt = load_json(EXAMPLE)
    report = {
        'snapshot_date': '2026-03-17',
        'focus': 'make phase-3 world emission explicit in the retained publication bundle so the first endogenous rematch benchmark can be cited as an actual SG-003 emission surface, not just as an inferred one',
        'analysis_script': 'scripts/report/build_rematch_world_benchmark_phase3_emission_snapshot.py',
        'bundle_receipt_path': 'examples/snapshots/rematch_world_benchmark_publication_bundle_receipt.json',
        'decision_contract_sha256': receipt['decision_contract_sha256'],
        'world_emission_ready': receipt['decision_emission']['world_emission_ready'],
        'bundle_matches_standing_contract': receipt['decision_emission']['bundle_matches_standing_contract'],
        'emitted_question_id_count': receipt['decision_emission']['emitted_question_id_count'],
        'emitted_question_ids': receipt['decision_emission']['emitted_question_ids'],
        'emitted_sections': receipt['decision_emission']['emitted_sections'],
        'allowed_open_interval_count': receipt['decision_emission']['allowed_open_interval_count'],
        'recommended_next_move': 'Use the retained publication bundle receipt as the inheritor-facing citation surface for SG-003 phase-3 emission until a world-native decision contract replaces the copied proxy-derived bundle.',
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(report) + '\n', encoding='utf-8')
    print(f'rematch-world-benchmark-phase3-emission-snapshot: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'rematch-world-benchmark-phase3-emission-snapshot: wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
