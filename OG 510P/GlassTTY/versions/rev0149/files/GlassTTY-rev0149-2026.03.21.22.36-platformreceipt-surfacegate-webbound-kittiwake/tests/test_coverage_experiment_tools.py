from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'compare-coverage-experiments.py'
FIXTURES = ROOT / 'fixtures' / 'coverage-experiments'


def run_compare(*argv: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *argv],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)



def test_compare_coverage_experiments_matches_prediction() -> None:
    report = run_compare(
        str(FIXTURES / 'about-blank-before-probe.json'),
        str(FIXTURES / 'about-blank-after-probe.json'),
    )
    assert report['comparison']['experimentId'] == 'manifest_match_about_blank'
    assert report['comparison']['predictionStatus'] == 'matched_exactly'
    assert report['comparison']['observed']['candidateGapFrameCount'] == 0
    assert report['comparison']['warnings'] == []





def test_compare_coverage_experiments_detects_count_only_shape_match() -> None:
    report = run_compare(
        str(FIXTURES / 'about-blank-before-probe.json'),
        str(FIXTURES / 'runtime-priming-count-only-after-probe.json'),
    )
    assert report['comparison']['experimentId'] == 'current_runtime_priming'
    assert report['comparison']['predictionStatus'] == 'matched_exactly'
    assert report['comparison']['shapeComparison']['stableSignatureStatus'] == 'matched_counts_but_shapes_differ'
    warnings = '\n'.join(report['comparison']['warnings'])
    assert 'count-only match' in warnings
    assert 'unexpected remaining gap shapes' in warnings


def test_compare_coverage_experiments_warns_about_missing_reload() -> None:
    report = run_compare(
        str(FIXTURES / 'about-blank-before-probe.json'),
        str(FIXTURES / 'origin-fallback-after-no-reload-probe.json'),
    )
    assert report['comparison']['experimentId'] == 'manifest_match_origin_as_fallback'
    assert report['comparison']['predictionStatus'] == 'no_change'
    warnings = '\n'.join(report['comparison']['warnings'])
    assert 'reloaded or renavigated' in warnings
    assert 'widened one or more narrower match paths to /*' in warnings
