#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'cloudtainer_standing_bootstrap_delta.json'
DOC = ROOT / 'docs' / 'CLOUDTAINER_STANDING_BOOTSTRAP_DELTA.md'


def main() -> int:
    if not REPORT.exists() or not DOC.exists():
        print('cloudtainer-standing-bootstrap-delta: missing report or doc', file=sys.stderr)
        return 1

    report = json.loads(REPORT.read_text(encoding='utf-8'))
    summary = report.get('summary', {})
    seeds = report.get('seeds', [])
    if summary.get('affected_queue_rows') != 3:
        print('cloudtainer-standing-bootstrap-delta: expected exactly three affected queue rows', file=sys.stderr)
        return 1
    if summary.get('affected_unique_seed_count') != 2:
        print('cloudtainer-standing-bootstrap-delta: expected exactly two affected seeds', file=sys.stderr)
        return 1
    if summary.get('mean_stats_invariant_rows') != 3 or summary.get('trace_only_rows') != 3:
        print('cloudtainer-standing-bootstrap-delta: expected all affected rows to stay trace-only/stat-invariant', file=sys.stderr)
        return 1
    if summary.get('action_sensitive_rows') != 0 or summary.get('payoff_sensitive_rows') != 0:
        print('cloudtainer-standing-bootstrap-delta: expected no action/payoff-sensitive rows yet', file=sys.stderr)
        return 1
    if summary.get('first_standing_diff_round_min') != 0:
        print('cloudtainer-standing-bootstrap-delta: expected standing drift to begin at round 0', file=sys.stderr)
        return 1

    seed_paths = {seed['seed_path'] for seed in seeds}
    expected_paths = {
        'examples/probes/simple_standing_image_scoring_probe.json',
        'examples/probes/simple_standing_standing_norm_probe.json',
    }
    if seed_paths != expected_paths:
        print('cloudtainer-standing-bootstrap-delta: affected seed set drifted', file=sys.stderr)
        return 1

    for seed in seeds:
        if not seed.get('mean_stats_invariant'):
            print('cloudtainer-standing-bootstrap-delta: a seed is no longer mean-stat invariant', file=sys.stderr)
            return 1
        delta = seed.get('trace_delta', {})
        if delta.get('first_standing_diff_round') != 0 or not delta.get('standing_stream_changed'):
            print('cloudtainer-standing-bootstrap-delta: expected standing drift from round 0', file=sys.stderr)
            return 1
        if delta.get('action_stream_changed') or delta.get('payoff_stream_changed'):
            print('cloudtainer-standing-bootstrap-delta: unexpected action/payoff drift detected', file=sys.stderr)
            return 1
        if seed.get('classification') != 'trace_only':
            print('cloudtainer-standing-bootstrap-delta: expected trace_only classification', file=sys.stderr)
            return 1

    text = DOC.read_text(encoding='utf-8')
    required_phrases = [
        'trace-only',
        'opponent_standing',
        'first recorded standing values equal the declared',
    ]
    for phrase in required_phrases:
        if phrase not in text:
            print(f'cloudtainer-standing-bootstrap-delta: doc missing phrase: {phrase}', file=sys.stderr)
            return 1

    print('cloudtainer-standing-bootstrap-delta: ok rows=3 seeds=2 trace_only=3')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
