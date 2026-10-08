#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_STEM = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_cache_plan_snapshot_20260306'
EXTORTION_PATH = ROOT / 'examples' / 'strategies' / 'extortion_chi3.json'
GEN_TFT_PATH = ROOT / 'examples' / 'strategies' / 'mem1_generous_tft.json'
FINAL_HORIZON = 50
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


def _consulted_indices(
    code: str,
    opponent: dict,
    *,
    focal_tremble: bool,
    opponent_tremble: bool,
    max_match_rounds: int,
) -> set[int]:
    consulted = {0}
    queue: deque[tuple[tuple[str, str] | None, int]] = deque([(None, 0)])
    seen = {None}
    while queue:
        prev, depth = queue.popleft()
        if depth >= max_match_rounds:
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


def _canonical_pattern(
    code: str,
    opponents: list[dict],
    *,
    focal_tremble: bool,
    opponent_tremble: bool,
    max_match_rounds: int,
) -> str:
    consulted: set[int] = set()
    for opponent in opponents:
        consulted |= _consulted_indices(
            code,
            opponent,
            focal_tremble=focal_tremble,
            opponent_tremble=opponent_tremble,
            max_match_rounds=max_match_rounds,
        )
    return ''.join(ch if idx in consulted else '*' for idx, ch in enumerate(code))


def _quotient_set(
    opponents: list[dict],
    *,
    focal_tremble: bool,
    opponent_tremble: bool,
    max_match_rounds: int,
) -> tuple[str, ...]:
    return tuple(sorted({
        _canonical_pattern(
            code,
            opponents,
            focal_tremble=focal_tremble,
            opponent_tremble=opponent_tremble,
            max_match_rounds=max_match_rounds,
        )
        for code in DETERMINISTIC_CODES
    }))


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


def _supports_initial_d(signature: str) -> bool:
    return signature[0] in {'D', 'B'}


def _minimal_exact_horizon(base_pool: list[dict], *, focal_tremble: bool, opponent_tremble: bool) -> int:
    final_group_map = defaultdict(list)
    for signature in SUPPORT_SIGNATURES:
        quotient = _quotient_set(
            base_pool + [_support_opponent(signature)],
            focal_tremble=focal_tremble,
            opponent_tremble=opponent_tremble,
            max_match_rounds=FINAL_HORIZON,
        )
        final_group_map[quotient].append(signature)
    final_keys = set(final_group_map.keys())
    for horizon in (1, 2, 3):
        group_map = defaultdict(list)
        for signature in SUPPORT_SIGNATURES:
            quotient = _quotient_set(
                base_pool + [_support_opponent(signature)],
                focal_tremble=focal_tremble,
                opponent_tremble=opponent_tremble,
                max_match_rounds=horizon,
            )
            group_map[quotient].append(signature)
        if set(group_map.keys()) == final_keys:
            return horizon
    raise AssertionError('expected saturation by horizon 3 in current proxy')


def _round_obj(obj: object) -> object:
    if isinstance(obj, float):
        return round(obj, 6)
    if isinstance(obj, list):
        return [_round_obj(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _round_obj(v) for k, v in obj.items()}
    return obj


def _mode_plan(mode_id: str, regime_rows: list[dict]) -> tuple[str, list[str], str]:
    if mode_id == 'none':
        return (
            'lookup-table',
            ['noise_mode', 'support_regime_id'],
            'Use the explicit 17-bucket support-regime lookup in the JSON artifact; full entrant support would over-key this proxy.',
        )
    if mode_id == 'opponent_tremble':
        return (
            'single-bucket',
            ['noise_mode'],
            'All entrant support signatures share one exact quotient regime in this mode.',
        )
    if mode_id == 'focal_tremble':
        return (
            'boolean-gate',
            ['noise_mode', 'entrant_initial_support_includes_D'],
            'The exact quotient regime is fully determined by whether the entrant can initially defect.',
        )
    if mode_id == 'bilateral_tremble':
        return (
            'single-bucket',
            ['noise_mode'],
            'All entrant support signatures share one exact quotient regime once both sides tremble.',
        )
    raise ValueError(mode_id)


def _render_markdown(report: dict) -> str:
    naive = report['world']['naive_cache_plan']
    lines = [
        '# Rematch-Proxy Cache Plan Snapshot (2026-03-06)',
        '',
        'Method:',
        f"- analyzed all `{report['world']['support_signature_count']}` entrant support signatures over `{{C, D, both}}^5` in the current leave/rematch proxy",
        f"- compared the inherited naive canonicalization plan of full entrant-signature keying plus `h={naive['horizon']}` against exact quotient regimes and exact horizons",
        f"- base proxy pool remains `{', '.join(report['world']['base_pool'])}` over `{report['world']['deterministic_focal_codes']}` deterministic `memory_one_exit` focal codes",
        '',
        'Main findings:',
    ]
    for row in report['mode_rows']:
        lines.append(
            f"- `{row['label']}` can be compiled to `{row['regime_count']}` cache bucket(s) at exact horizon `{row['minimal_exact_horizon']}`; that reduces naive key-depth slots from `{naive['key_depth_slots']}` to `{row['optimized_key_depth_slots']}` (`{row['key_depth_reduction_factor']:.1f}x` smaller)."
        )
    lines.extend([
        '',
        'Recommended provisional planner:',
    ])
    for row in report['mode_rows']:
        lines.append(
            f"- `{row['label']}` — key `{row['recommended_key_fields']}`, horizon `{row['minimal_exact_horizon']}`, planner kind `{row['planner_kind']}`. {row['planner_note']}"
        )
    lines.extend([
        '',
        'Zero-noise regime manifest:',
        '- The JSON artifact includes an explicit `signature_to_regime` lookup for all 243 entrant support signatures. The largest bucket is the cooperative-start bucket; the rest split only once initial D support appears.',
    ])
    zero_noise = next(row for row in report['mode_rows'] if row['id'] == 'none')
    for regime in zero_noise['regime_rows']:
        reps = ', '.join(f'`{sig}`' for sig in regime['representative_signatures'])
        lines.append(
            f"- `{regime['regime_id']}` — `{regime['signature_count']}` signatures, family count `{regime['quotient_family_count']}`, representatives: {reps}"
        )
    lines.extend([
        '',
        'Interpretation:',
        '- The current proxy now supports a compact machine-readable canonicalization planner rather than a vague recommendation to “be world-aware.”',
        '- Most of the inherited naive plan is dead weight here: exact cache planning is not only safer than full-signature reuse, it is orders of magnitude cheaper.',
        '',
        'Implementor implication:',
        '- Treat this report JSON as a provisional compile-time planner for the current proxy only. Vendor the table if useful, but regenerate it whenever the real rematch world changes entrant support, noise topology, outside-option timing, or memory depth.',
        '',
    ])
    return '\n'.join(lines)


def main() -> int:
    extortion = _read_json(EXTORTION_PATH)
    generous_tft = _read_json(GEN_TFT_PATH)
    base_pool = [extortion, generous_tft]
    naive_signature_slots = len(SUPPORT_SIGNATURES)
    naive_key_depth_slots = naive_signature_slots * FINAL_HORIZON

    mode_rows = []
    for mode in NOISE_MODES:
        quotient_to_signatures: dict[tuple[str, ...], list[str]] = defaultdict(list)
        for signature in SUPPORT_SIGNATURES:
            quotient = _quotient_set(
                base_pool + [_support_opponent(signature)],
                focal_tremble=mode['focal_tremble'],
                opponent_tremble=mode['opponent_tremble'],
                max_match_rounds=FINAL_HORIZON,
            )
            quotient_to_signatures[quotient].append(signature)
        sorted_groups = sorted(
            quotient_to_signatures.items(),
            key=lambda kv: (-len(kv[1]), kv[1][0]),
        )
        regime_rows = []
        signature_to_regime = {}
        for index, (quotient, signatures) in enumerate(sorted_groups):
            regime_id = f"{mode['id']}_r{index:02d}"
            for signature in signatures:
                signature_to_regime[signature] = regime_id
            regime_rows.append(
                {
                    'regime_id': regime_id,
                    'signature_count': len(signatures),
                    'representative_signatures': signatures[:3],
                    'contains_initial_d_support': any(_supports_initial_d(sig) for sig in signatures),
                    'all_initial_c_only': all(not _supports_initial_d(sig) for sig in signatures),
                    'quotient_family_count': len(quotient),
                    'quotient_family_examples': list(quotient[:5]),
                }
            )
        minimal_horizon = _minimal_exact_horizon(
            base_pool,
            focal_tremble=mode['focal_tremble'],
            opponent_tremble=mode['opponent_tremble'],
        )
        planner_kind, recommended_key_fields, planner_note = _mode_plan(mode['id'], regime_rows)
        regime_count = len(regime_rows)
        optimized_key_depth_slots = regime_count * minimal_horizon
        mode_rows.append(
            {
                'id': mode['id'],
                'label': mode['label'],
                'focal_tremble': mode['focal_tremble'],
                'opponent_tremble': mode['opponent_tremble'],
                'regime_count': regime_count,
                'minimal_exact_horizon': minimal_horizon,
                'planner_kind': planner_kind,
                'recommended_key_fields': recommended_key_fields,
                'planner_note': planner_note,
                'naive_signature_slots': naive_signature_slots,
                'optimized_signature_slots': regime_count,
                'signature_slot_reduction_factor': naive_signature_slots / regime_count,
                'naive_key_depth_slots': naive_key_depth_slots,
                'optimized_key_depth_slots': optimized_key_depth_slots,
                'key_depth_reduction_factor': naive_key_depth_slots / optimized_key_depth_slots,
                'regime_rows': regime_rows,
                'signature_to_regime': signature_to_regime,
            }
        )

    report = {
        'world': {
            'kind': 'rematch_proxy_cache_plan',
            'description': 'Mode-specific provisional canonicalization planner for the current leave/rematch proxy.',
            'base_pool': [spec['id'] for spec in base_pool],
            'deterministic_focal_codes': len(DETERMINISTIC_CODES),
            'support_signature_count': len(SUPPORT_SIGNATURES),
            'state_count': 5,
            'state_index': {
                'start': 0,
                'CC': 1,
                'CD': 2,
                'DC': 3,
                'DD': 4,
            },
            'naive_cache_plan': {
                'key_fields': ['noise_mode', 'entrant_support_signature'],
                'horizon': FINAL_HORIZON,
                'signature_slots': naive_signature_slots,
                'key_depth_slots': naive_key_depth_slots,
            },
        },
        'mode_rows': mode_rows,
        'summary': {
            'optimized_key_depth_slots_by_mode': {row['id']: row['optimized_key_depth_slots'] for row in mode_rows},
            'key_depth_reduction_factor_by_mode': {row['id']: row['key_depth_reduction_factor'] for row in mode_rows},
            'regime_count_by_mode': {row['id']: row['regime_count'] for row in mode_rows},
            'minimal_exact_horizon_by_mode': {row['id']: row['minimal_exact_horizon'] for row in mode_rows},
            'largest_reduction_factor': max(row['key_depth_reduction_factor'] for row in mode_rows),
            'smallest_reduction_factor': min(row['key_depth_reduction_factor'] for row in mode_rows),
        },
    }
    report = _round_obj(report)
    REPORT_STEM.with_suffix('.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    REPORT_STEM.with_suffix('.md').write_text(_render_markdown(report) + '\n', encoding='utf-8')
    print(f'wrote {REPORT_STEM.with_suffix(".json")} and {REPORT_STEM.with_suffix(".md")}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
