#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
import random
import statistics
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_STEM = ROOT / 'artifacts' / 'reports' / 'partner_choice_proxy_snapshot_20260306'
EXTORTION_PATH = ROOT / 'examples' / 'strategies' / 'extortion_chi3.json'
GEN_TFT_PATH = ROOT / 'examples' / 'strategies' / 'mem1_generous_tft.json'
ALWAYS_C_PATH = ROOT / 'examples' / 'strategies' / 'always_c.json'
COURTEOUS_PATH = ROOT / 'examples' / 'strategies' / 'mem1_courteous_firm.json'
EXIT_AFTER_BREAK_PATH = ROOT / 'examples' / 'strategies' / 'mem1_exit_after_break.json'

PAYOFFS = {
    ('C', 'C'): (3.0, 3.0),
    ('C', 'D'): (0.0, 5.0),
    ('D', 'C'): (5.0, 0.0),
    ('D', 'D'): (1.0, 1.0),
}
DETERMINISTIC_CODES = [''.join(code) for code in itertools.product('CDE', repeat=5)]
SCENARIOS = [
    {'extortion_share': 0.2, 'rematch_delay': 0},
    {'extortion_share': 0.5, 'rematch_delay': 0},
    {'extortion_share': 0.8, 'rematch_delay': 0},
    {'extortion_share': 0.2, 'rematch_delay': 1},
    {'extortion_share': 0.5, 'rematch_delay': 1},
    {'extortion_share': 0.8, 'rematch_delay': 1},
    {'extortion_share': 0.2, 'rematch_delay': 2},
    {'extortion_share': 0.5, 'rematch_delay': 2},
    {'extortion_share': 0.8, 'rematch_delay': 2},
]
SCREEN_TOTAL_ROUNDS = 3000
FINAL_TOTAL_ROUNDS = 12000
FINAL_SEEDS = [11, 29]
MAX_MATCH_ROUNDS = 50
EXPLOIT_MAX = 0.1
GOOD_PAY_MIN = 2.95
TOP_K = 5


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


def _simulate_match(spec_a: dict, spec_b: dict, *, max_rounds: int, seed: int, exit_payoff: float) -> dict[str, float | bool]:
    rng = random.Random(seed)
    prev: tuple[str, str] | None = None
    total_a = 0.0
    total_b = 0.0
    executed = 0
    for _ in range(max_rounds):
        probs_a = _action_probs(spec_a, prev)
        prev_b = None if prev is None else (prev[1], prev[0])
        probs_b = _action_probs(spec_b, prev_b)
        action_a = _sample_action(probs_a, rng)
        action_b = _sample_action(probs_b, rng)
        executed += 1
        if action_a == 'E' or action_b == 'E':
            total_a += exit_payoff
            total_b += exit_payoff
            return {'payoff_a': total_a, 'payoff_b': total_b, 'rounds': float(executed), 'exited': True}
        pay_a, pay_b = PAYOFFS[(action_a, action_b)]
        total_a += pay_a
        total_b += pay_b
        prev = (action_a, action_b)
    return {'payoff_a': total_a, 'payoff_b': total_b, 'rounds': float(executed), 'exited': False}


def _det_exit_strategy(code: str) -> dict:
    spec = {'family': 'memory_one_exit', 'id': f'det_exit_{code.lower()}'}
    for stem, action in zip(('p0', 'p_cc', 'p_cd', 'p_dc', 'p_dd'), code):
        spec[f'{stem}_c'] = 1.0 if action == 'C' else 0.0
        spec[f'{stem}_d'] = 1.0 if action == 'D' else 0.0
    return spec


def _simulate_proxy_world(
    focal: dict,
    *,
    extortion: dict,
    generous_tft: dict,
    total_rounds: int,
    extortion_share: float,
    rematch_delay: int,
    seed: int,
    exit_payoff: float,
) -> dict[str, float]:
    rng = random.Random(seed)
    total_a = 0.0
    total_stage_rounds = 0
    total_matches = 0
    exits = 0
    extortion_pay_a = 0.0
    extortion_pay_b = 0.0
    extortion_rounds = 0.0
    good_pay_a = 0.0
    good_rounds = 0.0

    while total_stage_rounds < total_rounds:
        opp_name = 'extortion' if rng.random() < extortion_share else 'generous_tft'
        opp = extortion if opp_name == 'extortion' else generous_tft
        total_matches += 1
        result = _simulate_match(
            focal,
            opp,
            max_rounds=MAX_MATCH_ROUNDS,
            seed=rng.randrange(1 << 30),
            exit_payoff=exit_payoff,
        )
        rounds = int(result['rounds'])
        total_stage_rounds += rounds
        total_a += float(result['payoff_a'])
        if bool(result['exited']):
            exits += 1
        if opp_name == 'extortion':
            extortion_pay_a += float(result['payoff_a'])
            extortion_pay_b += float(result['payoff_b'])
            extortion_rounds += float(result['rounds'])
        else:
            good_pay_a += float(result['payoff_a'])
            good_rounds += float(result['rounds'])
        if rematch_delay > 0 and total_stage_rounds < total_rounds:
            total_stage_rounds += min(rematch_delay, total_rounds - total_stage_rounds)

    return {
        'overall_avg_payoff': total_a / total_stage_rounds,
        'extortion_gap': (extortion_pay_a - extortion_pay_b) / extortion_rounds if extortion_rounds else 0.0,
        'extortion_avg_payoff': extortion_pay_a / extortion_rounds if extortion_rounds else 0.0,
        'good_partner_avg_payoff': good_pay_a / good_rounds if good_rounds else 0.0,
        'exit_rate': exits / total_matches if total_matches else 0.0,
    }


def _dyad_metrics(spec: dict, *, extortion: dict, always_c: dict, exit_payoff: float) -> dict[str, float]:
    ext_a = 0.0
    ext_b = 0.0
    for i in range(400):
        res = _simulate_match(spec, extortion, max_rounds=MAX_MATCH_ROUNDS, seed=100000 + i, exit_payoff=exit_payoff)
        ext_a += float(res['payoff_a']) / float(res['rounds'])
        ext_b += float(res['payoff_b']) / float(res['rounds'])

    allc_a = 0.0
    allc_b = 0.0
    for i in range(150):
        res = _simulate_match(spec, always_c, max_rounds=MAX_MATCH_ROUNDS, seed=200000 + i, exit_payoff=exit_payoff)
        allc_a += float(res['payoff_a']) / float(res['rounds'])
        allc_b += float(res['payoff_b']) / float(res['rounds'])

    self_a = 0.0
    for i in range(150):
        res = _simulate_match(spec, spec, max_rounds=MAX_MATCH_ROUNDS, seed=300000 + i, exit_payoff=exit_payoff)
        self_a += float(res['payoff_a']) / float(res['rounds'])

    return {
        'fairness_vs_extortion': ext_a / 400.0 - ext_b / 400.0,
        'exploit_gain_vs_allC': allc_a / 150.0 - allc_b / 150.0,
        'self_payoff': self_a / 150.0,
    }


def _scenario_key(scenario: dict[str, int | float]) -> str:
    return f"ext{int(round(float(scenario['extortion_share']) * 100)):02d}_delay{int(scenario['rematch_delay'])}"


def _mean_round(values: list[float]) -> float:
    return round(statistics.fmean(values), 6)


def _round_obj(obj: object) -> object:
    if isinstance(obj, float):
        return round(obj, 6)
    if isinstance(obj, list):
        return [_round_obj(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _round_obj(v) for k, v in obj.items()}
    return obj


def main() -> int:
    started = time.time()
    extortion = _read_json(EXTORTION_PATH)
    generous_tft = _read_json(GEN_TFT_PATH)
    always_c = _read_json(ALWAYS_C_PATH)
    courteous_firm = _read_json(COURTEOUS_PATH)
    exit_after_break = _read_json(EXIT_AFTER_BREAK_PATH)
    exit_payoff = 0.0

    screen_records = []
    for code in DETERMINISTIC_CODES:
        spec = _det_exit_strategy(code)
        dyad = _dyad_metrics(spec, extortion=extortion, always_c=always_c, exit_payoff=exit_payoff)
        scenario_metrics = {}
        scenario_values = []
        for scenario in SCENARIOS:
            metrics = _simulate_proxy_world(
                spec,
                extortion=extortion,
                generous_tft=generous_tft,
                total_rounds=SCREEN_TOTAL_ROUNDS,
                extortion_share=float(scenario['extortion_share']),
                rematch_delay=int(scenario['rematch_delay']),
                seed=7,
                exit_payoff=exit_payoff,
            )
            scenario_metrics[_scenario_key(scenario)] = metrics
            scenario_values.append(metrics['overall_avg_payoff'])
        screen_records.append(
            {
                'code': code,
                'spec': spec,
                'dyad': dyad,
                'screen_proxy': scenario_metrics,
                'screen_proxy_min_overall': min(scenario_values),
                'screen_proxy_mean_overall': statistics.fmean(scenario_values),
                'nice_start': code[0] == 'C',
                'nonexploit': dyad['exploit_gain_vs_allC'] <= EXPLOIT_MAX,
                'good_partner_preserving': min(
                    metrics['good_partner_avg_payoff'] for metrics in scenario_metrics.values()
                ) >= GOOD_PAY_MIN,
            }
        )

    top_proxy = sorted(
        screen_records,
        key=lambda rec: (rec['screen_proxy_min_overall'], rec['screen_proxy_mean_overall']),
        reverse=True,
    )[:TOP_K]
    top_balanced_nice = sorted(
        (
            rec for rec in screen_records
            if rec['nice_start'] and rec['nonexploit'] and rec['good_partner_preserving']
        ),
        key=lambda rec: (rec['screen_proxy_min_overall'], rec['screen_proxy_mean_overall']),
        reverse=True,
    )[:TOP_K]

    finalists = {rec['code']: rec for rec in top_proxy + top_balanced_nice}
    reevaluated = []
    for code, rec in finalists.items():
        scenario_metrics = {}
        all_values = []
        for scenario in SCENARIOS:
            per_seed = []
            for seed in FINAL_SEEDS:
                per_seed.append(
                    _simulate_proxy_world(
                        rec['spec'],
                        extortion=extortion,
                        generous_tft=generous_tft,
                        total_rounds=FINAL_TOTAL_ROUNDS,
                        extortion_share=float(scenario['extortion_share']),
                        rematch_delay=int(scenario['rematch_delay']),
                        seed=seed,
                        exit_payoff=exit_payoff,
                    )
                )
            scenario_metrics[_scenario_key(scenario)] = {
                key: _mean_round([float(seed_metrics[key]) for seed_metrics in per_seed])
                for key in ('overall_avg_payoff', 'extortion_gap', 'extortion_avg_payoff', 'good_partner_avg_payoff', 'exit_rate')
            }
            all_values.append(statistics.fmean(seed_metrics['overall_avg_payoff'] for seed_metrics in per_seed))
        reevaluated.append(
            {
                'code': code,
                'spec': rec['spec'],
                'dyad': rec['dyad'],
                'proxy': scenario_metrics,
                'proxy_min_overall': min(all_values),
                'proxy_mean_overall': statistics.fmean(all_values),
                'nice_start': rec['nice_start'],
                'nonexploit': rec['nonexploit'],
                'good_partner_preserving': rec['good_partner_preserving'],
            }
        )

    reevaluated_by_code = {rec['code']: rec for rec in reevaluated}
    top_proxy_final = sorted(
        (reevaluated_by_code[rec['code']] for rec in top_proxy),
        key=lambda rec: (rec['proxy_min_overall'], rec['proxy_mean_overall']),
        reverse=True,
    )
    top_balanced_nice_final = sorted(
        (reevaluated_by_code[rec['code']] for rec in top_balanced_nice),
        key=lambda rec: (rec['proxy_min_overall'], rec['proxy_mean_overall']),
        reverse=True,
    )

    best_proxy = top_proxy_final[0]
    best_balanced_nice = top_balanced_nice_final[0]

    baseline_specs = {
        'always_cooperate': always_c,
        'courteous_firm': courteous_firm,
        'first_defect_exit_trap': _det_exit_strategy('DCECC'),
        'leave_after_break': exit_after_break,
    }
    baseline_table = {}
    for name, spec in baseline_specs.items():
        baseline_table[name] = {}
        for scenario in SCENARIOS:
            per_seed = []
            for seed in FINAL_SEEDS:
                per_seed.append(
                    _simulate_proxy_world(
                        spec,
                        extortion=extortion,
                        generous_tft=generous_tft,
                        total_rounds=FINAL_TOTAL_ROUNDS,
                        extortion_share=float(scenario['extortion_share']),
                        rematch_delay=int(scenario['rematch_delay']),
                        seed=seed,
                        exit_payoff=exit_payoff,
                    )
                )
            baseline_table[name][_scenario_key(scenario)] = {
                key: _mean_round([float(seed_metrics[key]) for seed_metrics in per_seed])
                for key in ('overall_avg_payoff', 'extortion_gap', 'extortion_avg_payoff', 'good_partner_avg_payoff', 'exit_rate')
            }

    top_family = [rec['code'] for rec in top_balanced_nice_final if abs(rec['proxy_min_overall'] - best_balanced_nice['proxy_min_overall']) < 1e-9]
    canonical_tied_family = [code for code in DETERMINISTIC_CODES if code.startswith('CCE')]

    result = {
        'world': {
            'kind': 'partner_choice_proxy',
            'description': 'Focal-agent leave/rematch proxy with an exogenous pool of extortion and generous-TFT partners.',
            'max_match_rounds': MAX_MATCH_ROUNDS,
            'scenarios': SCENARIOS,
            'screen_total_rounds': SCREEN_TOTAL_ROUNDS,
            'final_total_rounds': FINAL_TOTAL_ROUNDS,
            'final_seeds': FINAL_SEEDS,
        },
        'evaluated_family': 'deterministic_memory_one_exit',
        'deterministic_candidates': len(DETERMINISTIC_CODES),
        'filters': {
            'nice_start': 'first move must be C',
            'nonexploit': f'exploit_gain_vs_allC <= {EXPLOIT_MAX}',
            'good_partner_preserving': f'min good_partner_avg_payoff across scenarios >= {GOOD_PAY_MIN}',
        },
        'findings': {
            'best_proxy_candidate': {
                'code': best_proxy['code'],
                'proxy_min_overall': best_proxy['proxy_min_overall'],
                'proxy_mean_overall': best_proxy['proxy_mean_overall'],
                'dyad': best_proxy['dyad'],
                'proxy': best_proxy['proxy'],
            },
            'best_balanced_nice_candidate': {
                'code': best_balanced_nice['code'],
                'proxy_min_overall': best_balanced_nice['proxy_min_overall'],
                'proxy_mean_overall': best_balanced_nice['proxy_mean_overall'],
                'dyad': best_balanced_nice['dyad'],
                'proxy': best_balanced_nice['proxy'],
            },
            'balanced_nice_top_codes': [rec['code'] for rec in top_balanced_nice_final],
            'proxy_summary': (
                'In the minimal leave/rematch proxy, the best balanced nice-start code in this scan is CCDDE, while the simpler leave_after_break baseline CCEEE remains close and beats Always-Cooperate, the fixed-dyad courteous-firm baseline, and the first-defect exit trap DCECC across the tested grid.'
            ),
            'interpretation': (
                'This is evidence that world mechanics matter: the same policy shape that looks weak in a fixed dyad can become strong once rematching exists. '
                'It is not yet evidence of endogenous partner choice, because the partner pool is exogenous and there is no population assortment or reputation.'
            ),
            'canonical_handoff_baseline': 'CCEEE',
            'canonical_tied_family_prefix': 'CCE**',
            'canonical_tied_family_example_codes': canonical_tied_family[:9],
        },
        'top_proxy_candidates': [
            {
                'code': rec['code'],
                'proxy_min_overall': rec['proxy_min_overall'],
                'proxy_mean_overall': rec['proxy_mean_overall'],
                'dyad': rec['dyad'],
            }
            for rec in top_proxy_final
        ],
        'top_balanced_nice_candidates': [
            {
                'code': rec['code'],
                'proxy_min_overall': rec['proxy_min_overall'],
                'proxy_mean_overall': rec['proxy_mean_overall'],
                'dyad': rec['dyad'],
            }
            for rec in top_balanced_nice_final
        ],
        'baseline_comparison': baseline_table,
        'limitations': [
            'This is a focal-agent proxy, not a full endogenous partner-choice world.',
            'The pool is exogenous and limited to extortion_chi3_v1 and mem1_generous_tft_v1.',
            'The report only covers deterministic memory_one_exit policies.',
            'No reputation, market thickness, or mutual matching dynamics are modeled here.',
        ],
        'timing_seconds': time.time() - started,
    }

    REPORT_STEM.with_suffix('.json').write_text(
        json.dumps(_round_obj(result), indent=2, sort_keys=True) + '\n',
        encoding='utf-8',
    )

    scen = baseline_table
    lines = [
        '# Partner-Choice Proxy Snapshot (2026-03-06)',
        '',
        'Method:',
        '- evaluated all `243` deterministic `memory_one_exit` policies in a minimal leave/rematch proxy world',
        '- pool = extortion (`extortion_chi3_v1`) or cooperative partner (`mem1_generous_tft_v1`)',
        '- when a match ends or someone exits, the focal agent rematches from the exogenous pool after a configurable rematch delay',
        '- scenario grid: extortion share in `{0.2, 0.5, 0.8}` × rematch delay in `{0, 1, 2}` stage rounds',
        '- balanced nice filter = starts with C, exploit gain vs Always-Cooperate <= 0.1, preserves >= 2.95 average payoff with generous-TFT partners across scenarios',
        '',
        'Main finding:',
        '- Once rematching exists, nice-start exit policies become genuinely competitive in this proxy.',
        '- The best balanced nice-start code in this scan is `CCDDE`, while the simpler handoff baseline `CCEEE` remains close and easier to reason about.',
        '- The handoff baseline `CCEEE` beats three salient baselines across the tested grid: `always_c`, `mem1_courteous_firm_v1`, and the first-defect exit trap `DCECC`.',
        '- This is still **not** full partner choice: the pool is exogenous, with no endogenous assortment or reputation.',
        '',
        'Best balanced nice-start candidate in this scan:',
        f"- code: `{best_balanced_nice['code']}`",
        f"- robust minimum overall payoff across grid: `{best_balanced_nice['proxy_min_overall']:.6f}`",
        f"- mean overall payoff across grid: `{best_balanced_nice['proxy_mean_overall']:.6f}`",
        f"- fixed-dyad fairness vs extortion: `{best_balanced_nice['dyad']['fairness_vs_extortion']:.6f}`",
        f"- fixed-dyad exploit gain vs Always-Cooperate: `{best_balanced_nice['dyad']['exploit_gain_vs_allC']:.6f}`",
        f"- fixed-dyad self-play payoff: `{best_balanced_nice['dyad']['self_payoff']:.6f}`",
        '',
        'Compact handoff baseline (`CCEEE` = leave_after_break):',
        f"- robust minimum overall payoff across grid: `{min(scen['leave_after_break'][_scenario_key(sc)]['overall_avg_payoff'] for sc in SCENARIOS):.6f}`",
        f"- mean overall payoff across grid: `{statistics.fmean(scen['leave_after_break'][_scenario_key(sc)]['overall_avg_payoff'] for sc in SCENARIOS):.6f}`",
        '- policy shape: cooperate initially, cooperate after mutual cooperation, leave after any non-CC outcome.',
        '',
        'Interpretation:',
        '- The earlier fixed-dyad result remains true: unilateral exit alone is not partner choice.',
        '- But adding even a small rematch channel changes the ranking enough that a nice-start leave-after-break policy becomes better than both naive cooperation and first-defect trap policies in this proxy.',
        '- This means the next implementor should promote rematching from “future prose” to an engine-supported world surface.',
        '',
        'Baseline comparison (overall payoff by scenario):',
        '',
        '| scenario | leave_after_break (`CCEEE`) | courteous_firm | always_c | first_defect_exit_trap (`DCECC`) |',
        '|---|---:|---:|---:|---:|',
    ]
    for scenario in SCENARIOS:
        key = _scenario_key(scenario)
        label = f"extortion={scenario['extortion_share']:.1f}, delay={scenario['rematch_delay']}"
        lines.append(
            f"| `{label}` | {scen['leave_after_break'][key]['overall_avg_payoff']:.6f} | {scen['courteous_firm'][key]['overall_avg_payoff']:.6f} | {scen['always_cooperate'][key]['overall_avg_payoff']:.6f} | {scen['first_defect_exit_trap'][key]['overall_avg_payoff']:.6f} |"
        )

    lines.extend(
        [
            '',
            'Why the proxy winner is compactly meaningful:',
            '- It preserves mutual cooperation with generous-TFT partners (3.0 across the tested grid).',
            '- It caps extortion exposure by turning the first broken cooperative signal into rematching, not into a 50-round sink.',
            '- It is Golden-Rule-shaped in a minimal sense: start cooperative, stay while cooperation remains intact, leave when it does not.',
            '',
            'Search-space caution:',
            '- One strong deterministic family collapses to a behaviorally equivalent prefix `CCE**` under this proxy. Once the policy leaves after a non-CC signal, later transition parameters are unreachable.',
            '- That is a small but real implementor hint: rematch-enabled search spaces should canonicalize unreachable post-exit parameters instead of treating them as distinct discoveries.',
            '',
            'Immediate implementor implication:',
            '- Promote this proxy to an engine-supported world with explicit rematching/outside-option semantics, then test whether the same `leave_after_break` shape still survives once the pool becomes endogenous.',
        ]
    )
    REPORT_STEM.with_suffix('.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'wrote {REPORT_STEM.with_suffix(".json")}')
    print(f'wrote {REPORT_STEM.with_suffix(".md")}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
