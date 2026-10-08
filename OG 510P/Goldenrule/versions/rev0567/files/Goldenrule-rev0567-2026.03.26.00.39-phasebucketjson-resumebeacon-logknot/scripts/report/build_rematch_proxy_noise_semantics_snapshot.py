#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from collections import Counter, defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_STEM = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_noise_semantics_snapshot_20260306'
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
NOISE_MODES = [
    {
        'id': 'none',
        'label': 'deterministic no-noise',
        'focal_tremble': False,
        'opponent_tremble': False,
    },
    {
        'id': 'opponent_tremble',
        'label': 'opponent support tremble',
        'focal_tremble': False,
        'opponent_tremble': True,
    },
    {
        'id': 'focal_tremble',
        'label': 'focal support tremble',
        'focal_tremble': True,
        'opponent_tremble': False,
    },
    {
        'id': 'bilateral_tremble',
        'label': 'bilateral support tremble',
        'focal_tremble': True,
        'opponent_tremble': True,
    },
]


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def _opp_support(spec: dict, prev: tuple[str, str] | None, tremble: bool) -> tuple[str, ...]:
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
        if tremble:
            return ('C', 'D')
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
        base = tuple(SUPPORT_MEANING[spec[key]])
        if tremble and base:
            return ('C', 'D')
        return base

    raise ValueError(f'unsupported family: {family}')


def _focal_support(action: str, tremble: bool) -> tuple[str, ...]:
    if action == 'E':
        return ('E',)
    if tremble:
        return ('C', 'D')
    return (action,)


def _focal_action(code: str, prev: tuple[str, str] | None) -> str:
    return code[STATE_INDEX[prev]]


def _consulted_indices(code: str, opponent: dict, *, focal_tremble: bool, opponent_tremble: bool) -> set[int]:
    consulted = {0}
    queue: deque[tuple[tuple[str, str] | None, int]] = deque([(None, 0)])
    seen = {None}
    while queue:
        prev, depth = queue.popleft()
        if depth >= MAX_MATCH_ROUNDS:
            continue
        intended = _focal_action(code, prev)
        for action in _focal_support(intended, focal_tremble):
            if action == 'E':
                continue
            opp_prev = None if prev is None else (prev[1], prev[0])
            for opp_action in _opp_support(opponent, opp_prev, opponent_tremble):
                next_prev = (action, opp_action)
                consulted.add(STATE_INDEX[next_prev])
                if next_prev not in seen:
                    seen.add(next_prev)
                    queue.append((next_prev, depth + 1))
    return consulted


def _canonical_pattern(code: str, opponents: list[dict], *, focal_tremble: bool, opponent_tremble: bool) -> str:
    consulted: set[int] = set()
    for opponent in opponents:
        consulted |= _consulted_indices(
            code,
            opponent,
            focal_tremble=focal_tremble,
            opponent_tremble=opponent_tremble,
        )
    return ''.join(ch if idx in consulted else '*' for idx, ch in enumerate(code))


def _family_count(opponents: list[dict], *, focal_tremble: bool, opponent_tremble: bool) -> int:
    return len(
        {
            _canonical_pattern(
                code,
                opponents,
                focal_tremble=focal_tremble,
                opponent_tremble=opponent_tremble,
            )
            for code in DETERMINISTIC_CODES
        }
    )


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
        '# Rematch-Proxy Noise-Semantics Snapshot (2026-03-06)',
        '',
        'Method:',
        f"- analyzed all `{report['world']['deterministic_focal_codes']}` deterministic `memory_one_exit` codes in the current leave/rematch proxy",
        '- compared support-reachable canonical families under four action-support semantics: deterministic no-noise, opponent tremble, focal tremble, and bilateral tremble',
        '- each tremble mode is a support-level model of any nonzero action error: once a non-exit action is intended, both `C` and `D` are treated as reachable',
        f"- also reran the prior start-support sweep over `{report['world']['support_signature_count']}` entrant signatures inside each noise mode",
        f"- match horizon for reachability = `{report['world']['max_match_rounds']}` rounds",
        '',
        'Main findings:',
        f"- The zero-noise cooperative-pool quotient is `{report['summary']['base_family_counts']['none']}` families.",
        f"- Opponent tremble alone raises it to `{report['summary']['base_family_counts']['opponent_tremble']}` families, which already matches the strongest invalidation seen in the prior zero-noise start-support scan.",
        f"- Focal tremble alone raises it further to `{report['summary']['base_family_counts']['focal_tremble']}` families.",
        f"- Bilateral tremble yields `{report['summary']['base_family_counts']['bilateral_tremble']}` families.",
        '',
        'Base quotient by noise mode:',
    ]
    for row in report['mode_rows']:
        lines.append(
            f"- `{row['label']}` — base quotient `{row['base_family_count']}`; `C`-only additions `{row['c_only_family_range'][0]}`–`{row['c_only_family_range'][1]}`; initial-`D` additions `{row['initial_d_family_range'][0]}`–`{row['initial_d_family_range'][1]}`"
        )
    lines.extend([
        '',
        'Interpretation:',
        '- The earlier start-support cache gate is real, but it is a zero-noise result. As soon as tremble semantics are admitted, the cache key must widen from entrant support alone to entrant support plus noise semantics.',
        '- Opponent tremble is the sharpest counterexample: once the current cooperative pool itself can emit either opening action through error support, every extra entrant signature collapses to the same `99`-family quotient.',
        '- Focal tremble keeps a weaker gate (`147` for `C`-only additions, `163` for initial-`D` additions), so actor-side error semantics matter too.',
        '',
        'Implementor implication:',
        '- Treat any nonzero action-tremble semantics as an immediate invalidation of the zero-noise rematch canonicalization cache. Recompute under the active tremble model before ranking discoveries.',
        '',
    ])
    return '\n'.join(lines)


def main() -> int:
    extortion = _read_json(EXTORTION_PATH)
    generous_tft = _read_json(GEN_TFT_PATH)
    base_pool = [extortion, generous_tft]

    mode_rows = []
    for mode in NOISE_MODES:
        signature_rows = []
        base_family_count = _family_count(
            base_pool,
            focal_tremble=mode['focal_tremble'],
            opponent_tremble=mode['opponent_tremble'],
        )
        for signature in SUPPORT_SIGNATURES:
            family_count = _family_count(
                base_pool + [_support_opponent(signature)],
                focal_tremble=mode['focal_tremble'],
                opponent_tremble=mode['opponent_tremble'],
            )
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
        def _range(rows: list[dict]) -> list[int]:
            values = sorted({row['family_count'] for row in rows})
            return [values[0], values[-1]]
        mode_rows.append(
            {
                'id': mode['id'],
                'label': mode['label'],
                'focal_tremble': mode['focal_tremble'],
                'opponent_tremble': mode['opponent_tremble'],
                'base_family_count': base_family_count,
                'c_only_family_range': _range(grouped['C']),
                'initial_d_family_range': _range([row for row in signature_rows if row['includes_initial_d']]),
                'histogram_by_initial_support': {
                    support: [
                        {'family_count': family_count, 'signature_count': count}
                        for family_count, count in sorted(Counter(row['family_count'] for row in grouped[support]).items())
                    ]
                    for support in ('C', 'D', 'B')
                },
                'signature_rows': sorted(signature_rows, key=lambda row: (row['family_count'], row['signature'])),
            }
        )

    row_by_id = {row['id']: row for row in mode_rows}
    report = {
        'world': {
            'kind': 'partner_choice_proxy_noise_semantics',
            'description': 'Support-reachable canonical family counts for deterministic memory_one_exit policies in the current leave/rematch proxy under different action-tremble semantics.',
            'current_proxy_members': [spec['id'] for spec in base_pool],
            'support_signature_count': len(SUPPORT_SIGNATURES),
            'deterministic_focal_codes': len(DETERMINISTIC_CODES),
            'max_match_rounds': MAX_MATCH_ROUNDS,
            'tremble_semantics': 'Support-level nonzero action error: any intended non-exit action may realize as either C or D.',
        },
        'summary': {
            'statement': 'The current start-support cache gate is a zero-noise artifact; once tremble semantics are introduced, the rematch canonical quotient must be keyed on noise semantics as well as entrant support.',
            'base_family_counts': {
                row['id']: row['base_family_count'] for row in mode_rows
            },
            'zero_noise_to_opponent_tremble_delta': row_by_id['opponent_tremble']['base_family_count'] - row_by_id['none']['base_family_count'],
            'zero_noise_to_focal_tremble_delta': row_by_id['focal_tremble']['base_family_count'] - row_by_id['none']['base_family_count'],
            'zero_noise_to_bilateral_tremble_delta': row_by_id['bilateral_tremble']['base_family_count'] - row_by_id['none']['base_family_count'],
            'opponent_tremble_eliminates_entrant_gate': row_by_id['opponent_tremble']['c_only_family_range'] == row_by_id['opponent_tremble']['initial_d_family_range'],
            'bilateral_tremble_eliminates_entrant_gate': row_by_id['bilateral_tremble']['c_only_family_range'] == row_by_id['bilateral_tremble']['initial_d_family_range'],
            'focal_tremble_retains_weaker_gate': row_by_id['focal_tremble']['c_only_family_range'] != row_by_id['focal_tremble']['initial_d_family_range'],
        },
        'mode_rows': mode_rows,
    }

    REPORT_STEM.with_suffix('.json').write_text(json.dumps(_round_obj(report), indent=2) + '\n', encoding='utf-8')
    REPORT_STEM.with_suffix('.md').write_text(_render_markdown(report) + '\n', encoding='utf-8')
    print(f'wrote {REPORT_STEM.with_suffix(".json")}')
    print(f'wrote {REPORT_STEM.with_suffix(".md")}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
