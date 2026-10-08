#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_STEM = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_cache_regime_snapshot_20260306'
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


def _family_set(opponents: list[dict], *, focal_tremble: bool, opponent_tremble: bool) -> tuple[str, ...]:
    return tuple(
        sorted(
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


def _readable_signature(signature: str) -> tuple[int, str]:
    return (signature.count('B'), signature)


def _regime_note(mode_id: str, regime_count: int, rows: list[dict]) -> str:
    if mode_id == 'opponent_tremble':
        return 'Cache key can ignore entrant support entirely; noise mode alone determines the quotient in this proxy.'
    if mode_id == 'bilateral_tremble':
        return 'Cache key can ignore entrant support entirely once both sides have nonzero action-error support.'
    if mode_id == 'focal_tremble':
        return 'Cache key collapses to noise mode plus whether the entrant can initially defect.'
    if mode_id == 'none' and regime_count == 17:
        return 'C-only entrants share one safe cache bucket, but once initial D support appears the quotient splinters into 16 additional regimes.'
    return 'Entrant support remains relevant to quotient selection in this mode.'


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
        '# Rematch-Proxy Cache-Regime Snapshot (2026-03-06)',
        '',
        'Method:',
        f"- analyzed all `{report['world']['support_signature_count']}` entrant support signatures over `{{C, D, both}}^5`",
        f"- for each noise mode, computed the full canonical family set over all `{report['world']['deterministic_focal_codes']}` deterministic `memory_one_exit` focal codes",
        '- grouped entrant signatures by exact quotient-set equality, not just by family-count equality',
        f"- current proxy pool remains `{', '.join(report['world']['base_pool'])}` with reachability horizon `{report['world']['max_match_rounds']}`",
        '',
        'Main findings:',
    ]
    for row in report['mode_rows']:
        lines.append(
            f"- `{row['label']}` has `{row['unique_quotient_sets']}` exact quotient regime(s): family-count range `{row['family_count_range'][0]}`–`{row['family_count_range'][1]}`. {row['cache_note']}"
        )
    lines.extend([
        '',
        'Mode-specific cache guidance:',
    ])
    for row in report['mode_rows']:
        lines.append(f"- `{row['label']}` — {row['cache_key_guidance']}")
    lines.extend([
        '',
        'Representative regime structure:',
    ])
    for row in report['mode_rows']:
        regime_parts = []
        for regime in row['regimes'][:4]:
            initials = ','.join(regime['initial_supports'])
            regime_parts.append(
                f"`{regime['representative_signature']}` ({regime['signature_count']} sigs; init `{initials}`; `{regime['family_count']}` families)"
            )
        lines.append(f"- `{row['label']}` — " + '; '.join(regime_parts))
    lines.extend([
        '',
        'Interpretation:',
        '- The current proxy does not just have a noise-sensitive cache; it has a small number of distinct cache regimes, and those regimes depend strongly on which side can tremble.',
        '- This means the next rematch-world engine should separate cache-key design into correctness-critical fields (noise topology, initial-defect reachability where relevant) and avoid paying for unnecessary full-signature cache keys in regimes where entrant support is already washed out.',
        '',
    ])
    return '\n'.join(lines)


def main() -> int:
    extortion = _read_json(EXTORTION_PATH)
    generous_tft = _read_json(GEN_TFT_PATH)
    base_pool = [extortion, generous_tft]

    mode_rows = []
    for mode in NOISE_MODES:
        groups: dict[tuple[str, ...], list[str]] = defaultdict(list)
        for signature in SUPPORT_SIGNATURES:
            quotient_set = _family_set(
                base_pool + [_support_opponent(signature)],
                focal_tremble=mode['focal_tremble'],
                opponent_tremble=mode['opponent_tremble'],
            )
            groups[quotient_set].append(signature)

        regimes = []
        for quotient_set, signatures in groups.items():
            signatures = sorted(signatures, key=_readable_signature)
            regimes.append(
                {
                    'representative_signature': signatures[0],
                    'signature_count': len(signatures),
                    'initial_supports': sorted({signature[0] for signature in signatures}),
                    'family_count': len(quotient_set),
                    'quotient_preview': list(quotient_set[:8]),
                }
            )
        regimes.sort(key=lambda row: (-row['signature_count'], row['representative_signature']))
        family_counts = sorted({regime['family_count'] for regime in regimes})
        unique_regimes = len(regimes)

        if mode['id'] == 'opponent_tremble':
            cache_key_guidance = 'Key on noise mode only; entrant support does not change the quotient in this proxy.'
        elif mode['id'] == 'bilateral_tremble':
            cache_key_guidance = 'Key on noise mode only; entrant support does not change the quotient once both sides tremble.'
        elif mode['id'] == 'focal_tremble':
            cache_key_guidance = 'Key on noise mode plus whether the entrant has initial-D support.'
        else:
            cache_key_guidance = 'Keep the C-only fast path, but after initial-D support appears do not collapse to a single coarse key; later support still splits the quotient.'

        mode_rows.append(
            {
                'id': mode['id'],
                'label': mode['label'],
                'focal_tremble': mode['focal_tremble'],
                'opponent_tremble': mode['opponent_tremble'],
                'unique_quotient_sets': unique_regimes,
                'family_count_range': [family_counts[0], family_counts[-1]],
                'cache_note': _regime_note(mode['id'], unique_regimes, regimes),
                'cache_key_guidance': cache_key_guidance,
                'regimes': regimes,
            }
        )

    report = {
        'world': {
            'kind': 'partner_choice_proxy_cache_regimes',
            'description': 'Exact quotient-set regimes for deterministic memory_one_exit canonicalization under the current leave/rematch proxy.',
            'base_pool': [spec['id'] for spec in base_pool],
            'support_signature_count': len(SUPPORT_SIGNATURES),
            'deterministic_focal_codes': len(DETERMINISTIC_CODES),
            'max_match_rounds': MAX_MATCH_ROUNDS,
        },
        'summary': {
            'statement': 'The current rematch proxy has a small number of exact canonicalization-cache regimes, and the minimal safe cache key depends sharply on which side has nonzero tremble support.',
            'noise_mode_to_unique_quotient_sets': {
                row['id']: row['unique_quotient_sets'] for row in mode_rows
            },
            'noise_mode_to_guidance': {
                row['id']: row['cache_key_guidance'] for row in mode_rows
            },
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
