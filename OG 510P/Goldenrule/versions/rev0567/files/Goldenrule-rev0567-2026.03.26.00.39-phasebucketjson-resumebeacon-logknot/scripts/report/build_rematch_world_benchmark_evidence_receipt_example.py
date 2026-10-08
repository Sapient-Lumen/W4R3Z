#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_evidence_receipt.py'
PACKET = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_packet.json'
OUT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_receipt.json'
SCRATCH = ROOT / 'examples' / 'scratch' / 'rematch_world_benchmark'


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [
            sys.executable,
            str(TOOL),
            str(PACKET),
            '--scratch-source', f'world_semantics_notes={SCRATCH / "source_world_semantics.json"}',
            '--scratch-source', f'policy_metrics_table={SCRATCH / "source_policy_metrics.tsv"}',
            '--scratch-source', f'leaderboard_table={SCRATCH / "source_leaderboard.csv"}',
            '--coverage', 'world_semantics_notes=world_semantics_contract,matching_state_contract',
            '--coverage', 'policy_metrics_table=occupancy_accounting_contract,turnover_tempo_contract',
            '--coverage', 'leaderboard_table=paired_ranking_views_contract',
            '--strict-coverage',
            '--output',
            str(OUT),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        print(proc.stdout, file=sys.stderr, end='')
        print(proc.stderr, file=sys.stderr, end='')
        return proc.returncode
    print(proc.stdout, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
