#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_STEM = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_canonicalization_sensitivity_snapshot_20260306'
EXTORTION_PATH = ROOT / 'examples' / 'strategies' / 'extortion_chi3.json'
GEN_TFT_PATH = ROOT / 'examples' / 'strategies' / 'mem1_generous_tft.json'
ALWAYS_D_PATH = ROOT / 'examples' / 'strategies' / 'always_d.json'
TFT_PATH = ROOT / 'examples' / 'strategies' / 'tft.json'
WSLS_PATH = ROOT / 'examples' / 'strategies' / 'wsls.json'
MAX_MATCH_ROUNDS = 50
DETERMINISTIC_CODES = [''.join(code) for code in itertools.product('CDE', repeat=5)]
STATE_INDEX = {
    None: 0,
    ('C', 'C'): 1,
    ('C', 'D'): 2,
    ('D', 'C'): 3,
    ('D', 'D'): 4,
}


SCENARIOS = [
    {
        'id': 'proxy_current',
        'label': 'Current proxy pool',
        'members': ['extortion_chi3_v1', 'mem1_generous_tft_v1'],
        'interpretation': 'Current leave/rematch proxy used in the archive.',
    },
    {
        'id': 'proxy_plus_tft',
        'label': 'Current pool + Tit-for-Tat',
        'members': ['extortion_chi3_v1', 'mem1_generous_tft_v1', 'tft_v1'],
        'interpretation': 'Adds another cooperative starter with retaliatory structure.',
    },
    {
        'id': 'proxy_plus_wsls',
        'label': 'Current pool + WSLS',
        'members': ['extortion_chi3_v1', 'mem1_generous_tft_v1', 'wsls_v1'],
        'interpretation': 'Adds another cooperative starter with a different deterministic repair rule.',
    },
    {
        'id': 'proxy_plus_alld',
        'label': 'Current pool + suspicious starter',
        'members': ['extortion_chi3_v1', 'mem1_generous_tft_v1', 'always_d_v1'],
        'interpretation': 'Adds one entrant that opens with defection immediately.',
    },
    {
        'id': 'proxy_mixed',
        'label': 'Mixed pool',
        'members': ['extortion_chi3_v1', 'mem1_generous_tft_v1', 'always_d_v1', 'tft_v1', 'wsls_v1'],
        'interpretation': 'Shows the current proxy plus one suspicious starter and two cooperative starters.',
    },
]


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

    if family == 'builtin':
        kind = spec['kind']
        if kind == 'always_c':
            return ('C',)
        if kind == 'always_d':
            return ('D',)
        if kind == 'tit_for_tat':
            if prev is None:
                return ('C',)
            return (prev[1],)
        if kind == 'win_stay_lose_shift':
            if prev is None:
                return ('C',)
            last_self, last_opp = prev
            win = (last_self, last_opp) in (('C', 'C'), ('D', 'C'))
            action = last_self if win else ('D' if last_self == 'C' else 'C')
            return (action,)
        raise ValueError(f'unsupported builtin kind: {kind}')

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


def _build_family_map(opponents: list[dict]) -> dict[str, list[str]]:
    families: dict[str, list[str]] = defaultdict(list)
    for code in DETERMINISTIC_CODES:
        families[_canonical_pattern(code, opponents)].append(code)
    return {k: sorted(v) for k, v in families.items()}


def _scenario_result(scenario: dict, registry: dict[str, dict], current_families: dict[str, list[str]]) -> dict:
    opponents = [registry[member] for member in scenario['members']]
    families = _build_family_map(opponents)
    count = len(families)
    reduction = 100.0 * (1.0 - (count / len(DETERMINISTIC_CODES)))
    largest_pattern, largest_members = sorted(families.items(), key=lambda kv: (-len(kv[1]), kv[0]))[0]
    split_from_current = []
    for pattern, members in current_families.items():
        observed = sorted({_canonical_pattern(code, opponents) for code in members})
        if len(observed) > 1:
            split_from_current.append(
                {
                    'from_pattern': pattern,
                    'into_patterns': observed,
                    'current_family_size': len(members),
                }
            )
    split_from_current.sort(key=lambda entry: (-entry['current_family_size'], entry['from_pattern']))
    return {
        'id': scenario['id'],
        'label': scenario['label'],
        'members': scenario['members'],
        'interpretation': scenario['interpretation'],
        'canonical_family_count': count,
        'reduction_percent': reduction,
        'compression_ratio': len(DETERMINISTIC_CODES) / count,
        'largest_family': {
            'pattern': largest_pattern,
            'size': len(largest_members),
            'representative': largest_members[0],
        },
        'splits_from_current': split_from_current[:8],
        'families': families,
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
    current = report['scenario_table'][0]
    suspicious = next(row for row in report['scenario_table'] if row['id'] == 'proxy_plus_alld')
    lines = [
        '# Rematch-Proxy Canonicalization Sensitivity Snapshot (2026-03-06)',
        '',
        'Method:',
        f"- analyzed all `{report['world']['raw_codes']}` deterministic `memory_one_exit` codes",
        '- canonicalized each code by the decision parameters that are support-reachable before exit',
        '- varied only the opponent pool; the focal strategy class and reachability horizon stayed fixed',
        f"- match horizon for reachability = `{report['world']['max_match_rounds']}` rounds",
        '',
        'Main finding:',
        f"- The current proxy quotient (`{current['canonical_family_count']}` families) is not stable to a hostile entrant.",
        f"- Adding one suspicious starter (`always_d_v1`) raises the count to `{suspicious['canonical_family_count']}` families.",
        f"- That is `{report['summary']['extra_families_vs_current']}` extra families, or `{report['summary']['growth_vs_current_percent']:.1f}%` more than the current proxy quotient.",
        '- Adding more cooperative starters (`tit_for_tat_v1`, `win_stay_lose_shift_v1`) leaves the quotient unchanged in this snapshot.',
        '',
        'Scenario table:',
    ]
    for row in report['scenario_table']:
        lines.append(
            f"- `{row['label']}` — `{row['canonical_family_count']}` families, `{row['reduction_percent']:.1f}%` raw-space reduction, largest family `{row['largest_family']['pattern']}` (`{row['largest_family']['size']}` codes)"
        )
    lines.extend([
        '',
        'Families that split once a suspicious starter is added:',
    ])
    for entry in suspicious['splits_from_current'][:6]:
        into = ', '.join(f"`{pattern}`" for pattern in entry['into_patterns'])
        lines.append(f"- Current family `{entry['from_pattern']}` (size `{entry['current_family_size']}`) splits into {into}.")
    lines.extend([
        '',
        'Interpretation:',
        '- The current `63`-family quotient is best treated as an optimistic lower bound tied to a cooperative-starting pool, not as a universal property of rematch worlds.',
        '- Cooperative-starting additions are cheap from a search-geometry perspective here; suspicious starters are the structural event that reopens wildcard states.',
        '- This means canonicalization must be world-aware and pool-aware. A cached quotient from one pool can under-deduplicate a richer pool and distort discovery counts.',
        '',
        'Implementor implication:',
        '- When the endogenous rematch world lands, recompute the canonicalization map whenever the entrant pool or start-state support changes. Do not freeze the current proxy quotient into the engine.',
        '',
    ])
    return '\n'.join(lines)


def main() -> int:
    registry = {}
    for path in [EXTORTION_PATH, GEN_TFT_PATH, ALWAYS_D_PATH, TFT_PATH, WSLS_PATH]:
        spec = _read_json(path)
        registry[spec['id']] = spec

    current_families = _build_family_map([registry['extortion_chi3_v1'], registry['mem1_generous_tft_v1']])
    scenario_rows = [_scenario_result(scenario, registry, current_families) for scenario in SCENARIOS]

    current = scenario_rows[0]
    suspicious = next(row for row in scenario_rows if row['id'] == 'proxy_plus_alld')

    report = {
        'world': {
            'kind': 'partner_choice_proxy_canonicalization_sensitivity',
            'description': 'Sensitivity of deterministic memory_one_exit canonicalization to the opponent pool in the current leave/rematch proxy.',
            'raw_codes': len(DETERMINISTIC_CODES),
            'max_match_rounds': MAX_MATCH_ROUNDS,
        },
        'summary': {
            'statement': 'The current rematch-proxy quotient is pool-specific: cooperative-starting additions leave the 63-family quotient unchanged in this snapshot, but a single suspicious starter reopens the space to 87 support-distinct families.',
            'current_family_count': current['canonical_family_count'],
            'suspicious_pool_family_count': suspicious['canonical_family_count'],
            'extra_families_vs_current': suspicious['canonical_family_count'] - current['canonical_family_count'],
            'growth_vs_current_percent': 100.0 * ((suspicious['canonical_family_count'] - current['canonical_family_count']) / current['canonical_family_count']),
        },
        'scenario_table': [
            {
                'id': row['id'],
                'label': row['label'],
                'members': row['members'],
                'interpretation': row['interpretation'],
                'canonical_family_count': row['canonical_family_count'],
                'reduction_percent': row['reduction_percent'],
                'compression_ratio': row['compression_ratio'],
                'largest_family': row['largest_family'],
                'splits_from_current': row['splits_from_current'],
            }
            for row in scenario_rows
        ],
        'notable_splits_under_suspicious_entry': suspicious['splits_from_current'][:8],
        'handoff': {
            'keep_readable_representative': 'CCEEE',
            'current_proxy_pattern': 'CCE**',
            'current_proxy_family_size': len(current_families['CCE**']),
            'message': 'Treat the current quotient as a world-specific cache. Recompute it when suspicious starters or new noise channels enter the pool.',
        },
        'notes': [
            'This is a structural support analysis, not a payoff-ranking pass.',
            'The same raw strategy can move between canonical families when the opponent pool changes.',
            'The current snapshot only varies the pool, not noise semantics or outside-option payoffs.',
        ],
    }

    REPORT_STEM.with_suffix('.json').write_text(json.dumps(_round_obj(report), indent=2) + '\n', encoding='utf-8')
    REPORT_STEM.with_suffix('.md').write_text(_render_markdown(_round_obj(report)), encoding='utf-8')
    print(f'wrote {REPORT_STEM.with_suffix(".json")}')
    print(f'wrote {REPORT_STEM.with_suffix(".md")}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
