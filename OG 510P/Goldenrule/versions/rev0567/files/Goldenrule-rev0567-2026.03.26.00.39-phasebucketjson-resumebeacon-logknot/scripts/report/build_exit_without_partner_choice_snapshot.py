#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
import random
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_STEM = ROOT / 'artifacts' / 'reports' / 'exit_without_partner_choice_snapshot_20260306'
WORLD_PATH = ROOT / 'examples' / 'worlds' / 'ipd_core.json'
EXTORTION_PATH = ROOT / 'examples' / 'strategies' / 'extortion_chi3.json'
ALWAYS_C_PATH = ROOT / 'examples' / 'strategies' / 'always_c.json'
GEN_TFT_PATH = ROOT / 'examples' / 'strategies' / 'mem1_generous_tft.json'

PAYOFFS = {
    ('C', 'C'): (3.0, 3.0),
    ('C', 'D'): (0.0, 5.0),
    ('D', 'C'): (5.0, 0.0),
    ('D', 'D'): (1.0, 1.0),
}
PREV_STATES = [None, ('C', 'C'), ('C', 'D'), ('D', 'C'), ('D', 'D')]
DETERMINISTIC_CODES = list(itertools.product('CDE', repeat=5))
BALANCED_SELF_MIN = 2.5
BALANCED_EXPLOIT_MAX = 0.1
TOP_K = 5
NICE_START = 'C'


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def _action_probs(spec: dict, prev: tuple[str, str] | None) -> dict[str, float]:
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
        return {'C': p, 'D': 1.0 - p, 'E': 0.0}

    if family == 'memory_one_exit':
        if prev is None:
            pc = float(spec['p0_c'])
            pd = float(spec['p0_d'])
        else:
            kc, kd = {
                ('C', 'C'): ('p_cc_c', 'p_cc_d'),
                ('C', 'D'): ('p_cd_c', 'p_cd_d'),
                ('D', 'C'): ('p_dc_c', 'p_dc_d'),
                ('D', 'D'): ('p_dd_c', 'p_dd_d'),
            }[prev]
            pc = float(spec[kc])
            pd = float(spec[kd])
        return {'C': pc, 'D': pd, 'E': max(0.0, 1.0 - pc - pd)}

    if family == 'builtin':
        kind = spec['kind']
        if kind == 'always_c':
            return {'C': 1.0, 'D': 0.0, 'E': 0.0}
        if kind == 'always_d':
            return {'C': 0.0, 'D': 1.0, 'E': 0.0}
        if kind == 'tit_for_tat':
            if prev is None:
                return {'C': 1.0, 'D': 0.0, 'E': 0.0}
            opp = prev[1]
            return {'C': 1.0 if opp == 'C' else 0.0, 'D': 1.0 if opp == 'D' else 0.0, 'E': 0.0}
        if kind == 'win_stay_lose_shift':
            if prev is None:
                return {'C': 1.0, 'D': 0.0, 'E': 0.0}
            last_self, last_opp = prev
            win = (last_self, last_opp) in (('C', 'C'), ('D', 'C'))
            action = last_self if win else ('D' if last_self == 'C' else 'C')
            return {'C': 1.0 if action == 'C' else 0.0, 'D': 1.0 if action == 'D' else 0.0, 'E': 0.0}
        raise ValueError(f'unsupported builtin kind: {kind}')

    raise ValueError(f'unsupported family: {family}')


def _sample_action(probs: dict[str, float], rng: random.Random) -> str:
    r = rng.random()
    acc = 0.0
    for action in ('C', 'D', 'E'):
        acc += probs[action]
        if r <= acc + 1e-12:
            return action
    return 'E'


def _simulate(spec_a: dict, spec_b: dict, rounds: int, exit_payoff: float, reps: int, seed: int) -> tuple[float, float]:
    rng = random.Random(seed)
    avg_a = 0.0
    avg_b = 0.0
    for _ in range(reps):
        prev: tuple[str, str] | None = None
        total_a = 0.0
        total_b = 0.0
        executed = 0
        for _round in range(rounds):
            probs_a = _action_probs(spec_a, prev)
            prev_b = None if prev is None else (prev[1], prev[0])
            probs_b = _action_probs(spec_b, prev_b)
            action_a = _sample_action(probs_a, rng)
            action_b = _sample_action(probs_b, rng)
            executed += 1
            if action_a == 'E' or action_b == 'E':
                total_a += exit_payoff
                total_b += exit_payoff
                break
            pay_a, pay_b = PAYOFFS[(action_a, action_b)]
            total_a += pay_a
            total_b += pay_b
            prev = (action_a, action_b)
        denom = float(max(1, executed))
        avg_a += total_a / denom
        avg_b += total_b / denom
    return avg_a / reps, avg_b / reps


def _det_exit_strategy(code: tuple[str, ...]) -> dict:
    spec = {'family': 'memory_one_exit', 'id': f'det_exit_{"".join(code).lower()}'}
    for stem, action in zip(('p0', 'p_cc', 'p_cd', 'p_dc', 'p_dd'), code):
        spec[f'{stem}_c'] = 1.0 if action == 'C' else 0.0
        spec[f'{stem}_d'] = 1.0 if action == 'D' else 0.0
    return spec


def _uses_exit(code: str) -> bool:
    return 'E' in code


def _evaluate(spec: dict, *, world_rounds: int, exit_payoff: float, ext_reps: int, other_reps: int) -> dict:
    vs_ext_a, vs_ext_b = _simulate(spec, EXTORTION, world_rounds, exit_payoff, ext_reps, seed=1)
    self_a, _self_b = _simulate(spec, spec, world_rounds, exit_payoff, other_reps, seed=2)
    vs_allc_a, vs_allc_b = _simulate(spec, ALWAYS_C, world_rounds, exit_payoff, other_reps, seed=3)
    vs_gtft_a, vs_gtft_b = _simulate(spec, GENEROUS_TFT, world_rounds, exit_payoff, other_reps, seed=4)
    return {
        'fairness_vs_extortion': vs_ext_a - vs_ext_b,
        'self_payoff': self_a,
        'exploit_gain_vs_allC': vs_allc_a - vs_allc_b,
        'vs_extortion': {'avg_payoff_a': vs_ext_a, 'avg_payoff_b': vs_ext_b},
        'vs_allC': {'avg_payoff_a': vs_allc_a, 'avg_payoff_b': vs_allc_b},
        'vs_generous_tft': {'avg_payoff_a': vs_gtft_a, 'avg_payoff_b': vs_gtft_b},
    }


def _round_metrics(metrics: dict) -> dict:
    out = {}
    for key, value in metrics.items():
        if isinstance(value, dict):
            out[key] = {k: round(float(v), 6) for k, v in value.items()}
        else:
            out[key] = round(float(value), 6)
    return out


def main() -> int:
    started = time.time()
    world = _read_json(WORLD_PATH)
    rounds = int(world['termination']['rounds'])
    exit_payoff = float(world['game']['payoffs'].get('exit', 0.0))

    coarse = []
    for code in DETERMINISTIC_CODES:
        spec = _det_exit_strategy(code)
        metrics = _evaluate(spec, world_rounds=rounds, exit_payoff=exit_payoff, ext_reps=1000, other_reps=200)
        coarse.append({'code': ''.join(code), 'uses_exit': _uses_exit(''.join(code)), 'spec': spec, 'metrics': metrics})

    top_overall = sorted(
        coarse,
        key=lambda rec: (rec['metrics']['fairness_vs_extortion'], rec['metrics']['self_payoff']),
        reverse=True,
    )[:TOP_K]

    balanced_pool = [
        rec for rec in coarse
        if rec['metrics']['self_payoff'] >= BALANCED_SELF_MIN
        and rec['metrics']['exploit_gain_vs_allC'] <= BALANCED_EXPLOIT_MAX
    ]
    top_balanced = sorted(
        balanced_pool,
        key=lambda rec: (rec['metrics']['fairness_vs_extortion'], rec['metrics']['self_payoff']),
        reverse=True,
    )[:TOP_K]

    nice_balanced_pool = [rec for rec in balanced_pool if rec['code'][0] == NICE_START]
    top_balanced_nice = sorted(
        nice_balanced_pool,
        key=lambda rec: (rec['metrics']['fairness_vs_extortion'], rec['metrics']['self_payoff']),
        reverse=True,
    )[:TOP_K]

    finalists = {rec['code']: rec for rec in top_overall + top_balanced + top_balanced_nice}
    reevaluated = []
    for code, rec in finalists.items():
        metrics = _evaluate(rec['spec'], world_rounds=rounds, exit_payoff=exit_payoff, ext_reps=50000, other_reps=5000)
        reevaluated.append({'code': code, 'uses_exit': rec['uses_exit'], 'spec': rec['spec'], 'metrics': metrics})
    reevaluated_by_code = {rec['code']: rec for rec in reevaluated}

    top_overall_final = sorted(
        (reevaluated_by_code[rec['code']] for rec in top_overall),
        key=lambda rec: (rec['metrics']['fairness_vs_extortion'], rec['metrics']['self_payoff']),
        reverse=True,
    )
    top_balanced_final = sorted(
        (reevaluated_by_code[rec['code']] for rec in top_balanced),
        key=lambda rec: (rec['metrics']['fairness_vs_extortion'], rec['metrics']['self_payoff']),
        reverse=True,
    )
    top_balanced_nice_final = sorted(
        (reevaluated_by_code[rec['code']] for rec in top_balanced_nice),
        key=lambda rec: (rec['metrics']['fairness_vs_extortion'], rec['metrics']['self_payoff']),
        reverse=True,
    )

    best_overall = top_overall_final[0]
    best_balanced = top_balanced_final[0]
    best_balanced_nice = top_balanced_nice_final[0]

    result = {
        'world': world['id'],
        'evaluated_family': 'deterministic_memory_one_exit',
        'deterministic_candidates': len(DETERMINISTIC_CODES),
        'balanced_criteria': {
            'self_payoff_min': BALANCED_SELF_MIN,
            'exploit_gain_vs_allC_max': BALANCED_EXPLOIT_MAX,
        },
        'screening': {
            'extortion_reps': 1000,
            'other_reps': 200,
            'finalist_extortion_reps': 50000,
            'finalist_other_reps': 5000,
        },
        'findings': {
            'best_overall_fairness_candidate': {
                'code': best_overall['code'],
                'uses_exit': best_overall['uses_exit'],
                'metrics': _round_metrics(best_overall['metrics']),
            },
            'best_balanced_candidate': {
                'code': best_balanced['code'],
                'uses_exit': best_balanced['uses_exit'],
                'metrics': _round_metrics(best_balanced['metrics']),
            },
            'best_balanced_nice_start_candidate': {
                'code': best_balanced_nice['code'],
                'uses_exit': best_balanced_nice['uses_exit'],
                'metrics': _round_metrics(best_balanced_nice['metrics']),
            },
            'balanced_frontier_exists_with_nonnegative_fairness': any(
                rec['metrics']['fairness_vs_extortion'] >= 0.0 for rec in top_balanced_final
            ),
            'balanced_nice_start_frontier_exists_with_nonnegative_fairness': any(
                rec['metrics']['fairness_vs_extortion'] >= 0.0 for rec in top_balanced_nice_final
            ),
            'best_balanced_candidate_uses_exit': best_balanced['uses_exit'],
            'best_balanced_nice_start_candidate_uses_exit': best_balanced_nice['uses_exit'],
            'summary': (
                'In the deterministic memory_one_exit family under ipd_core_v1, a near-fair balanced candidate exists only by defecting first and then using exit as a trap; '
                'once we impose a minimal nice-start filter, the best balanced candidate no longer uses exit and fairness remains negative.'
            ),
        },
        'top_overall_fairness': [
            {
                'code': rec['code'],
                'uses_exit': rec['uses_exit'],
                'metrics': _round_metrics(rec['metrics']),
            }
            for rec in top_overall_final
        ],
        'top_balanced': [
            {
                'code': rec['code'],
                'uses_exit': rec['uses_exit'],
                'metrics': _round_metrics(rec['metrics']),
            }
            for rec in top_balanced_final
        ],
        'top_balanced_nice_start': [
            {
                'code': rec['code'],
                'uses_exit': rec['uses_exit'],
                'metrics': _round_metrics(rec['metrics']),
            }
            for rec in top_balanced_nice_final
        ],
        'runtime_seconds': round(time.time() - started, 3),
        'limitations': [
            'This snapshot only covers deterministic memory_one_exit policies.',
            'The world is ipd_core_v1 (fixed 50 rounds, no noise, no rematching, exit payoff floor 0).',
            'This is therefore evidence that unilateral exit alone is not yet partner choice, not a claim about richer rematch worlds.',
        ],
    }

    md_lines = [
        '# Exit Without Partner Choice Snapshot (2026-03-06)',
        '',
        'Method:',
        f"- evaluated all `{len(DETERMINISTIC_CODES)}` deterministic `memory_one_exit` policies in `{world['id']}`",
        '- scorecard opponents: extortion, self-play, Always-Cooperate, Generous TFT',
        '- coarse screen with fixed seeds, then high-rep reevaluation of finalists',
        '',
        'Main finding:',
        '- In this deterministic exit-enabled family, a near-fair balanced candidate exists, but it achieves that only by defecting on the first move and then using exit as a trap.',
        '- Once we impose a minimal nice-start filter, the best balanced candidate no longer uses exit and fairness stays negative.',
        '- This is a local warning that `memory_one_exit` without rematching/outside-option mechanics is not the same as partner choice.',
        '',
        'Best fairness-only candidate:',
        f"- code: `{best_overall['code']}`",
        f"- uses exit: `{str(best_overall['uses_exit']).lower()}`",
        f"- fairness vs extortion: {best_overall['metrics']['fairness_vs_extortion']:.6f}",
        f"- self-play payoff: {best_overall['metrics']['self_payoff']:.6f}",
        f"- exploit gain vs Always-Cooperate: {best_overall['metrics']['exploit_gain_vs_allC']:.6f}",
        '',
        'Best balanced candidate (self-play >= 2.5, exploit gain <= 0.1):',
        f"- code: `{best_balanced['code']}`",
        f"- uses exit: `{str(best_balanced['uses_exit']).lower()}`",
        f"- fairness vs extortion: {best_balanced['metrics']['fairness_vs_extortion']:.6f}",
        f"- self-play payoff: {best_balanced['metrics']['self_payoff']:.6f}",
        f"- exploit gain vs Always-Cooperate: {best_balanced['metrics']['exploit_gain_vs_allC']:.6f}",
        '',
        'Best balanced nice-start candidate (same thresholds, plus first move = cooperate):',
        f"- code: `{best_balanced_nice['code']}`",
        f"- uses exit: `{str(best_balanced_nice['uses_exit']).lower()}`",
        f"- fairness vs extortion: {best_balanced_nice['metrics']['fairness_vs_extortion']:.6f}",
        f"- self-play payoff: {best_balanced_nice['metrics']['self_payoff']:.6f}",
        f"- exploit gain vs Always-Cooperate: {best_balanced_nice['metrics']['exploit_gain_vs_allC']:.6f}",
        '',
        'Balanced frontier witnesses:',
        '',
        '| code | uses exit | fairness vs extortion | self-play | exploit gain vs allC |',
        '|---|---:|---:|---:|---:|',
    ]
    for rec in top_balanced_final:
        m = rec['metrics']
        md_lines.append(
            f"| `{rec['code']}` | {str(rec['uses_exit']).lower()} | {m['fairness_vs_extortion']:.6f} | {m['self_payoff']:.6f} | {m['exploit_gain_vs_allC']:.6f} |"
        )
    md_lines.extend([
        '',
        'Interpretation:',
        '- If a policy gets fairness by defecting first and cashing out, the scorecard should reject it as non-Golden-Rule-like.',
        '- The nice-start filter is a minimal proxy for Golden-Rule shape. Under that filter, exit does not rescue the deterministic frontier.',
        '- That points back to the missing **world mechanic** (leave-and-rematch / outside option), not merely the action alphabet.',
        '',
        'Immediate implementor implication:',
        '- Do not treat `memory_one_exit` as a substitute for partner choice. Add one explicit rematch / outside-option world before expanding exit-heavy search.',
    ])

    REPORT_STEM.with_suffix('.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    REPORT_STEM.with_suffix('.md').write_text('\n'.join(md_lines) + '\n', encoding='utf-8')
    print(json.dumps({
        'report_json': str(REPORT_STEM.with_suffix('.json').relative_to(ROOT)),
        'report_md': str(REPORT_STEM.with_suffix('.md').relative_to(ROOT)),
        'best_overall': best_overall['code'],
        'best_balanced': best_balanced['code'],
        'best_balanced_nice': best_balanced_nice['code'],
        'runtime_seconds': result['runtime_seconds'],
    }, indent=2))
    return 0


WORLD = _read_json(WORLD_PATH)
EXTORTION = _read_json(EXTORTION_PATH)
ALWAYS_C = _read_json(ALWAYS_C_PATH)
GENEROUS_TFT = _read_json(GEN_TFT_PATH)


if __name__ == '__main__':
    raise SystemExit(main())
