#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / 'examples' / 'snapshots' / 'rematch_world_canonicalization_bridge_receipt.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_canonicalization_bridge_snapshot_20260317.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_world_canonicalization_bridge_snapshot_20260317.md'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def render_md(report: dict[str, Any]) -> str:
    return '\n'.join([
        '# Rematch-world canonicalization bridge snapshot — 2026-03-17',
        '',
        f"Focus: {report['focus']}",
        '',
        '## Local result',
        '',
        f"- One retained bridge receipt now links `{report['linked_open_item_count']}` SG-003 canonicalization-layer open items (`{report['assumption_count']}` assumptions + `{report['question_count']}` questions + `{report['risk_count']}` risks) to the exact proxy-local planner and classifier contracts the next implementor can actually reuse.",
        f"- The receipt cites `{report['retained_artifact_count']}` retained artifacts totaling `{report['retained_artifact_bytes']}` bytes instead of duplicating the larger proxy reports, while still carrying the exact mode-specific horizons `{report['mode_horizons']}` and the zero-noise ordered-rule compression from `{report['flat_lookup_rows']}` dispatch rows down to `{report['ordered_rule_count']}` rules (`{report['dispatch_surface_reduction_factor']}x` smaller).",
        f"- The strongest currently validated proxy-local cache-depth win remains `{report['largest_key_depth_reduction_factor']}x`, which is why the inheritor should promote planner fields into engine-owned world contracts before widening rematch search or benchmark storage.",
        '',
        '## Implementor guidance',
        '',
        '- Treat the bridge receipt as the compact citation target for the canonicalization-first SG-003 layer rather than rereading several March 6 proxy reports every session.',
        '- Preserve the rule that noise topology comes first, exact horizon comes second, and only then does the smallest validated entrant discriminator enter the cache key.',
        '- Convert the receipt into engine-owned conformance checks when the first real rematch world lands, then let the proxy-only bridge artifact remain archival context rather than a live dependency.',
        '',
    ])


def main() -> int:
    receipt = load_json(EXAMPLE)
    planner_modes = receipt['planner_contract']['mode_rows']
    mode_horizons = {row['id']: row['minimal_exact_horizon'] for row in planner_modes}
    report = {
        'snapshot_date': '2026-03-17',
        'focus': 'collapse the proxy-local SG-003 canonicalization layer into one tiny inheritor-facing bridge receipt instead of spreading the handoff across several larger reports',
        'analysis_script': 'scripts/report/build_rematch_world_canonicalization_bridge_snapshot.py',
        'linked_open_item_count': receipt['scope']['linked_open_item_count'],
        'assumption_count': len(receipt['linked_open_items']['assumptions']),
        'question_count': len(receipt['linked_open_items']['questions']),
        'risk_count': len(receipt['linked_open_items']['risks']),
        'retained_artifact_count': len(receipt['retained_artifacts']),
        'retained_artifact_bytes': sum(item['bytes'] for item in receipt['retained_artifacts']),
        'mode_horizons': mode_horizons,
        'largest_key_depth_reduction_factor': max(row['key_depth_reduction_factor'] for row in planner_modes),
        'ordered_rule_count': receipt['zero_noise_classifier_contract']['ordered_rule_count'],
        'flat_lookup_rows': receipt['zero_noise_classifier_contract']['support_signature_count'],
        'dispatch_surface_reduction_factor': receipt['zero_noise_classifier_contract']['dispatch_surface_reduction_factor'],
        'recommended_next_move': receipt['recommended_next_moves'][0],
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(report) + '\n', encoding='utf-8')
    print(f'rematch-world-canonicalization-bridge-snapshot: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'rematch-world-canonicalization-bridge-snapshot: wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
