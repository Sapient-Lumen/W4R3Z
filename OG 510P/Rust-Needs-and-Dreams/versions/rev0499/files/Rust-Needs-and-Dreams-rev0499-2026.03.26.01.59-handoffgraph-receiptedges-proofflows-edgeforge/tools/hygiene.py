#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    commands = [
        [sys.executable, str(ROOT / 'tools' / 'check_cargo_report_pack_contract.py')],
        [sys.executable, str(ROOT / 'tools' / 'check_portfolio_envelope_contract.py')],
        [sys.executable, str(ROOT / 'tools' / 'check_proving_ground_matrix.py')],
        [sys.executable, str(ROOT / 'tools' / 'check_anchor_corpus.py')],
        [sys.executable, str(ROOT / 'tools' / 'check_exemplar_federation.py')],
        [sys.executable, str(ROOT / 'tools' / 'check_hypothesis_ledger.py')],
        [sys.executable, str(ROOT / 'tools' / 'check_launch_wedges.py')],
        [sys.executable, str(ROOT / 'tools' / 'check_decision_journeys.py')],
        [sys.executable, str(ROOT / 'tools' / 'check_kernel_shipsets.py')],
        [sys.executable, str(ROOT / 'tools' / 'check_handoff_graph.py')],
        [sys.executable, str(ROOT / 'tools' / 'check_source_atlas.py')],
        [sys.executable, str(ROOT / 'tools' / 'check_kernel_fixture_packs.py')],
        [sys.executable, str(ROOT / 'tools' / 'check_kernel_artifact_schemas.py')],
        [sys.executable, str(ROOT / 'tools' / 'check_contribution_shapes.py')],
    ]
    for cmd in commands:
        code = subprocess.call(cmd, cwd=ROOT)
        if code != 0:
            return code
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
