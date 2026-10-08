#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_canonicalization_handoff.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_canonicalization_handoff_snapshot_20260317.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_canonicalization_handoff_snapshot_20260317.md'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def render_md(report: dict[str, Any]) -> str:
    return '\n'.join([
        '# Rematch-world benchmark canonicalization handoff snapshot — 2026-03-17',
        '',
        f"Focus: {report['focus']}",
        '',
        '## Local result',
        '',
        f"- The benchmark seed now carries a compact native canonicalization handoff copied from the SG-003 bridge receipt, so compiled benchmark artifacts can cite one embedded planner surface instead of making inheritors rediscover the proxy-local cache contract.",
        f"- The copied handoff stays small: `{report['mode_count']}` planner rows, exact horizons `{report['mode_horizons']}`, and the zero-noise dispatch compression summary `{report['ordered_rule_count']}/{report['support_signature_count']}` (`{report['dispatch_surface_reduction_factor']}x`).",
        f"- The handoff keeps archive discipline by embedding one bridge digest plus `{report['invalidation_trigger_count']}` invalidation triggers instead of wide canonicalization tables or report excerpts.",
        '',
        '## Implementor guidance',
        '',
        '- Treat the copied handoff as a frozen inheritor-facing citation surface inside the benchmark seed until a world-native planner manifest exists.',
        '- Replace the copied bridge-derived rows only when engine-measured endogenous rematch semantics can emit a native planner manifest and corresponding conformance tests.',
        '- Keep wide signature maps scratch-only; the benchmark artifact should retain only compact mode rows, bridge hashes, and the invalidation checklist.',
        '',
    ])


def main() -> int:
    handoff = load_json(EXAMPLE)
    mode_horizons = {row['mode_id']: row['minimal_exact_horizon'] for row in handoff['mode_rows']}
    report = {
        'snapshot_date': '2026-03-17',
        'focus': 'wire a compact canonicalization/planner handoff directly into the rematch-world benchmark seed so future compiled artifacts carry the SG-003 bridge surface natively',
        'analysis_script': 'scripts/report/build_rematch_world_benchmark_canonicalization_handoff_snapshot.py',
        'bridge_receipt_path': handoff['bridge_receipt_path'],
        'bridge_receipt_sha256': handoff['bridge_receipt_sha256'],
        'mode_count': len(handoff['mode_rows']),
        'mode_horizons': mode_horizons,
        'ordered_rule_count': handoff['zero_noise_dispatch_contract']['ordered_rule_count'],
        'support_signature_count': handoff['zero_noise_dispatch_contract']['support_signature_count'],
        'dispatch_surface_reduction_factor': handoff['zero_noise_dispatch_contract']['dispatch_surface_reduction_factor'],
        'invalidation_trigger_count': len(handoff['invalidation_triggers']),
        'recommended_next_move': 'Keep the copied handoff frozen in the benchmark seed and use it as the inheritor-facing planner citation surface until engine-owned world manifests replace it.',
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(report) + '\n', encoding='utf-8')
    print(f'rematch-world-benchmark-canonicalization-handoff-snapshot: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'rematch-world-benchmark-canonicalization-handoff-snapshot: wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
