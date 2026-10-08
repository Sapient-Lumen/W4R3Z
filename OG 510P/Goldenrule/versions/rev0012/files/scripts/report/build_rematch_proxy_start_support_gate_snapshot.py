#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from collections import Counter, defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_STEM = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_start_support_gate_snapshot_20260306'
EXTORTION_PATH = ROOT / 'examples' / 'strategies' / 'extortion_chi3.json'
GEN_TFT_PATH = ROOT / 'examples' / 'strategies' / 'mem1_generous_tft.json'
MAX_MATCH_ROUNDS = 50
STATE_INDEX = {
    None: 0,
    ('C', 'C'): 1,
    ('C', 'D'): 2,
    ('D', 'C'): 3,
    ('D', 'D'): 4,
}
DETERMINISTIC_CODES = [''.join(code) for code in itertools.product('CDE', repeat=5)]
SUPPORT_SIGNATURES = [''.join(code) for code in itertools.product('CDB', repeat=5)]
SUPPORT_MEANING = {
    'C': ['C'],
    'D': ['D'],
    'B': ['C', 'D'],
}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def _opp_support(spec: dict, prev: tuple[str, str] | None) -> tuple[str, ...]:
    family = spec['family']
    if family == 'memory_one':
        if prev is None:
            p = float(spec['p0'])
        else:
            key = {
                ('C', 'C'): 'p_cc',
                ('C', 'D'): 'p_cd',
                ('D', 'C'): 'p_dc',
                ('D', 'D'): 'p_dd',
            }[prev]
            p = float(spec[key])
        support = []
        if p > 0.0:
            support.append('C')
        if p < 1.0:
            support.append('D')
        return tuple(support)

    if family == 'memory_one_support':
        key = 's0' if prev is None else {
            ('C', 'C'): 's_cc',
            ('C', 'D'): 's_cd',
            ('D', 'C'): 's_dc',
            ('D', 'D'): 's_dd',
        }[prev]
        return tuple(SUPPORT_MEANING[spec[key]])

    raise ValueError(f'unsupported family: {family}')


def _focal_action(code: str, prev: tuple[str, str] | None) -> str:
    return code[STATE_INDEX[prev]]


def _consulted_indices(code: str, opponent: dict) -> set[int]:
    consulted = {0}
    queue: deque[tuple[tuple[str, str] | None, int]] = deque([(None, 0)])
    seen = {None}
    while queue:
        prev, depth = queue.popleft()
        if depth >= MAX_MATCH_ROUNDS:
            continue
        action = _focal_action(code, prev)
        if action == 'E':
            continue
        opp_prev = None if prev is None else (prev[1], prev[0])
        for opp_action in _opp_support(opponent, opp_prev):
            next_prev = (action, opp_action)
            consulted.add(STATE_INDEX[next_prev])
            if next_prev not in seen:
                seen.add(next_prev)
                queue.append((next_prev, depth + 1))
    return consulted


def _canonical_pattern(code: str, opponents: list[dict]) -> str:
    consulted: set[int] = set()
    for opponent in opponents:
        consulted |= _consulted_indices(code, opponent)
    return ''.join(ch if idx in consulted else '*' for idx, ch in enumerate(code))


def _family_count(opponents: list[dict]) -> int:
    return len({_canonical_pattern(code, opponents) for code in DETERMINISTIC_CODES})


def _support_opponent(signature: str) -> dict:
    return {
        'id': f'support_{signature.lower()}',
        'family': 'memory_one_support',
        's0': signature[0],
        's_cc': signature[1],
        's_cd': signature[2],
        's_dc': signature[3],
        's_dd': signature[4],
    }


def _round_obj(obj: object) -> object:
    if isinstance(obj, float):
        return round(obj, 6)
    if isinstance(obj, list):
        return [_round_obj(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _round_obj(v) for k, v in obj.items()}
    return obj


def _render_markdown(report: dict) -> str:
    lines = [
        '# Rematch-Proxy Start-Support Gate Snapshot (2026-03-06)',
        '',
        'Method:',
        f"- analyzed all `{report['world']['support_signature_count']}` memory-one support signatures over `{{C, D, both}}^5`",
        '- each signature acts as one extra entrant added to the current leave/rematch proxy pool (`extortion_chi3_v1`, `mem1_generous_tft_v1`)',
        '- canonicalized all `243` deterministic `memory_one_exit` focal codes by support-reachable consultation states before exit',
        f"- match horizon for reachability = `{report['world']['max_match_rounds']}` rounds",
        '',
        'Main finding:',
        f"- Every signature with `C`-only initial support (`{report['summary']['c_only_initial_signatures']}` of `{report['world']['support_signature_count']}`) leaves the quotient unchanged at `{report['summary']['current_family_count']}` families.",
        f"- Every signature whose initial support includes `D` (`{report['summary']['initial_d_signatures']}` of `{report['world']['support_signature_count']}`) invalidates that cache and raises the family count into `{report['summary']['initial_d_family_count_range'][0]}`–`{report['summary']['initial_d_family_count_range'][1]}`.",
        '- Pure-`D` and mixed-start (`both`) entrants have the same family-count histogram in this snapshot.',
        '',
        'Histogram by initial support:',
    ]
    for row in report['histogram_by_initial_support']:
        pairs = ', '.join(f"`{entry['family_count']}`→`{entry['signature_count']}`" for entry in row['histogram'])
        lines.append(f"- `{row['initial_support']}` initial support — {pairs}")
    lines.extend([
        '',
        'Representative support signatures:',
        f"- max safe reuse: `s0=C` family represented by `{report['representatives']['safe_c_only_representative']}`",
        f"- smallest invalidating family-count representative: `{report['representatives']['invalidating_min_representative']}` -> `{report['summary']['initial_d_family_count_range'][0]}` families",
        f"- largest invalidating family-count representative: `{report['representatives']['invalidating_max_representative']}` -> `{report['summary']['initial_d_family_count_range'][1]}` families",
        '',
        'Interpretation:',
        '- In the current deterministic no-noise proxy, the cheapest sound cache gate is an initial-support check: if a new entrant can open with `D`, the old cooperative-start quotient is no longer trustworthy.',
        '- That gate is only a trigger, not a replacement for recomputation. Later support decisions still determine whether the reopened quotient is `87`, `89`, `91`, `93`, `95`, or `99` families.',
        '',
        'Implementor implication:',
        '- Reuse the current rematch-proxy canonicalization cache only when every added entrant has `C`-only initial support under the current world semantics. Otherwise invalidate and recompute.',
        '',
    ])
    return '\n'.join(lines)


def main() -> int:
    extortion = _read_json(EXTORTION_PATH)
    generous_tft = _read_json(GEN_TFT_PATH)
    base_pool = [extortion, generous_tft]
    current_family_count = _family_count(base_pool)

    signature_rows = []
    for signature in SUPPORT_SIGNATURES:
        family_count = _family_count(base_pool + [_support_opponent(signature)])
        signature_rows.append(
            {
                'signature': signature,
                'initial_support': signature[0],
                'family_count': family_count,
                'includes_initial_d': signature[0] in {'D', 'B'},
            }
        )

    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in signature_rows:
        grouped[row['initial_support']].append(row)

    histogram_rows = []
    for initial_support in ('C', 'D', 'B'):
        histogram = Counter(row['family_count'] for row in grouped[initial_support])
        histogram_rows.append(
            {
                'initial_support': initial_support,
                'meaning': SUPPORT_MEANING[initial_support],
                'signature_count': len(grouped[initial_support]),
                'histogram': [
                    {'family_count': family_count, 'signature_count': count}
                    for family_count, count in sorted(histogram.items())
                ],
            }
        )

    invalidating = [row for row in signature_rows if row['includes_initial_d']]
    invalid_counts = sorted({row['family_count'] for row in invalidating})
    def _readable_signature(signature: str) -> tuple[int, str]:
        return (signature.count('B'), signature)

    representatives = {
        'safe_c_only_representative': sorted((row['signature'] for row in grouped['C']), key=_readable_signature)[0],
        'invalidating_min_representative': sorted((row['signature'] for row in invalidating if row['family_count'] == invalid_counts[0]), key=_readable_signature)[0],
        'invalidating_max_representative': sorted((row['signature'] for row in invalidating if row['family_count'] == invalid_counts[-1]), key=_readable_signature)[0],
    }

    report = {
        'world': {
            'kind': 'partner_choice_proxy_start_support_gate',
            'description': 'Current leave/rematch proxy quotient as a function of one extra entrant\'s memory-one action-support signature.',
            'current_proxy_members': [spec['id'] for spec in base_pool],
            'support_signature_count': len(SUPPORT_SIGNATURES),
            'deterministic_focal_codes': len(DETERMINISTIC_CODES),
            'max_match_rounds': MAX_MATCH_ROUNDS,
            'support_legend': {
                'C': ['C'],
                'D': ['D'],
                'B': ['C', 'D'],
            },
        },
        'summary': {
            'statement': 'In the current deterministic no-noise rematch proxy, every C-only initial support signature is cache-safe and every initial-D support signature invalidates the cooperative-start quotient.',
            'current_family_count': current_family_count,
            'c_only_initial_signatures': len(grouped['C']),
            'initial_d_signatures': len(invalidating),
            'initial_d_family_count_range': [invalid_counts[0], invalid_counts[-1]],
            'd_only_histogram_matches_mixed': histogram_rows[1]['histogram'] == histogram_rows[2]['histogram'],
        },
        'histogram_by_initial_support': histogram_rows,
        'representatives': representatives,
        'signature_rows': sorted(signature_rows, key=lambda row: (row['family_count'], row['signature'])),
    }

    REPORT_STEM.with_suffix('.json').write_text(json.dumps(_round_obj(report), indent=2) + '\n', encoding='utf-8')
    REPORT_STEM.with_suffix('.md').write_text(_render_markdown(report) + '\n', encoding='utf-8')
    print(f'wrote {REPORT_STEM.with_suffix(".json")}')
    print(f'wrote {REPORT_STEM.with_suffix(".md")}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
