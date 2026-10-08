#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts' / 'report' / 'build_rematch_world_benchmark_world_emission_card.py'
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_world_emission_card.json'
DOC = ROOT / 'docs' / 'REMATCH_WORLD_BENCHMARK_WORLD_EMISSION_CARD.md'


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-world-emission-card: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    for path in [SCRIPT, REPORT, DOC]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')

    proc = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return fail(f'builder exited nonzero: {proc.stderr or proc.stdout}')

    report = load_json(REPORT)
    if report['pending_native_section_count'] != 5:
        return fail(f"expected 5 pending native sections, got {report['pending_native_section_count']}")
    if report['copied_frozen_section_count'] != 8:
        return fail(f"expected 8 copied frozen sections, got {report['copied_frozen_section_count']}")
    if report['mutable_prefix_count'] != 12:
        return fail(f"expected 12 mutable prefixes, got {report['mutable_prefix_count']}")
    if report['frozen_prefix_count'] <= report['mutable_prefix_count']:
        return fail('frozen prefix count should exceed mutable prefix count')
    phase3 = report['phase3_emission']
    if not phase3['world_emission_ready']:
        return fail('phase-3 emission should be world_emission_ready=true')
    if phase3['emitted_question_id_count'] != 10:
        return fail(f"expected 10 emitted phase-3 question ids, got {phase3['emitted_question_id_count']}")
    if report['durable_publication_object_count'] != 6:
        return fail(f"expected 6 durable publication objects, got {report['durable_publication_object_count']}")
    if report['transient_exit_object_count'] != 4:
        return fail(f"expected 4 transient exit objects, got {report['transient_exit_object_count']}")
    if len(report['landing_steps']) != 10:
        return fail(f"expected 10 landing steps, got {len(report['landing_steps'])}")
    if not report['chain_status_counts']['overall_chain_ready']:
        return fail('overall_chain_ready should be true')
    if not report['package_status_counts']['package_ready']:
        return fail('package_ready should be true')
    pkg = report['package_policy_checks']
    for key in ['publication_chain_ready', 'post_prune_zip_ready', 'pdf_free_tree', 'scratch_tree_empty', 'pycache_free_tree']:
        if not pkg.get(key, False):
            return fail(f'package policy check should pass: {key}')

    text = DOC.read_text(encoding='utf-8')
    for needle in [
        '# Rematch-world benchmark world-emission card',
        '## Native fill targets',
        '## Frozen copied surface that should stay citation-first',
        '## Landing ladder',
        '## Durable publication objects after successful closeout',
    ]:
        if needle not in text:
            return fail(f'missing markdown section: {needle}')

    print('rematch-world-benchmark-world-emission-card: ok (one compact map now covers native fill targets, frozen copied surface, landing ladder, and package-closeout proof)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
