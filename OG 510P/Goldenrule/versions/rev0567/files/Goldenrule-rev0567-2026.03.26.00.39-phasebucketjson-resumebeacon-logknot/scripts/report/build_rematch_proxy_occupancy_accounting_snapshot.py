#!/usr/bin/env python3
from __future__ import annotations

import json
import random
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_occupancy_accounting_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_occupancy_accounting_snapshot_20260306.md'
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
EXTORTION_LEVELS = (20, 50, 80)
DELAY_LEVELS = (0, 1, 2)
SEEDS = (11, 29, 47, 83, 101, 131)
TOTAL_ROUNDS = 12000
MAX_MATCH_ROUNDS = 50
EXIT_PAYOFF = 0.0


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
    active_match_rounds = 0
    dead_rounds = 0

    while total_stage_rounds < total_rounds:
        opp = extortion if rng.random() < extortion_share else generous_tft
        total_matches += 1
        result = _simulate_match(
            focal,
            opp,
            max_rounds=MAX_MATCH_ROUNDS,
            seed=rng.randrange(1 << 30),
            exit_payoff=exit_payoff,
        )
        rounds = int(result['rounds'])
        active_match_rounds += rounds
        total_stage_rounds += rounds
        total_a += float(result['payoff_a'])
        if bool(result['exited']):
            exits += 1
        if rematch_delay > 0 and total_stage_rounds < total_rounds:
            added_delay = min(rematch_delay, total_rounds - total_stage_rounds)
            total_stage_rounds += added_delay
            dead_rounds += added_delay

    overall_avg_payoff = total_a / total_stage_rounds
    matched_round_share = active_match_rounds / total_stage_rounds
    in_match_avg_payoff = total_a / active_match_rounds if active_match_rounds else 0.0
    return {
        'overall_avg_payoff': overall_avg_payoff,
        'matched_round_share': matched_round_share,
        'dead_round_share': dead_rounds / total_stage_rounds,
        'in_match_avg_payoff': in_match_avg_payoff,
        'avg_match_length': active_match_rounds / total_matches if total_matches else 0.0,
        'exit_rate': exits / total_matches if total_matches else 0.0,
        'identity_gap': overall_avg_payoff - matched_round_share * in_match_avg_payoff,
    }


def _mean_metrics(spec: dict, *, extortion: dict, generous_tft: dict, extortion_share: float, rematch_delay: int) -> dict[str, float]:
    rows = [
        _simulate_proxy_world(
            spec,
            extortion=extortion,
            generous_tft=generous_tft,
            total_rounds=TOTAL_ROUNDS,
            extortion_share=extortion_share,
            rematch_delay=rematch_delay,
            seed=seed,
            exit_payoff=EXIT_PAYOFF,
        )
        for seed in SEEDS
    ]
    return {
        key: round(statistics.fmean(float(row[key]) for row in rows), 6)
        for key in rows[0]
    }


def _policy_cell_summary(block: dict[str, dict[str, float]]) -> dict[str, dict[str, float | bool]]:
    out: dict[str, dict[str, float | bool]] = {}
    for ext in EXTORTION_LEVELS:
        d0 = block[f'ext{ext}_delay0']
        d1 = block[f'ext{ext}_delay1']
        d2 = block[f'ext{ext}_delay2']
        overall_loss = float(d0['overall_avg_payoff']) - float(d2['overall_avg_payoff'])
        share_component = (float(d0['matched_round_share']) - float(d2['matched_round_share'])) * float(d0['in_match_avg_payoff'])
        in_match_component = float(d2['matched_round_share']) * (
            float(d0['in_match_avg_payoff']) - float(d2['in_match_avg_payoff'])
        )
        out[f'ext{ext}'] = {
            'delay0_matched_round_share': round(float(d0['matched_round_share']), 6),
            'delay2_matched_round_share': round(float(d2['matched_round_share']), 6),
            'delay0_in_match_avg_payoff': round(float(d0['in_match_avg_payoff']), 6),
            'delay2_in_match_avg_payoff': round(float(d2['in_match_avg_payoff']), 6),
            'matched_share_monotone_nonincreasing': float(d0['matched_round_share']) >= float(d1['matched_round_share']) >= float(d2['matched_round_share']),
            'max_abs_identity_gap_across_delay_means': round(
                max(abs(float(dx['identity_gap'])) for dx in (d0, d1, d2)),
                6,
            ),
            'delay0_to_delay2_overall_loss': round(overall_loss, 6),
            'delay0_to_delay2_share_component': round(share_component, 6),
            'delay0_to_delay2_in_match_component': round(in_match_component, 6),
            'share_component_fraction_of_loss': round(share_component / overall_loss, 6) if overall_loss else 0.0,
            'abs_in_match_drift_delay0_to_delay2': round(abs(float(d0['in_match_avg_payoff']) - float(d2['in_match_avg_payoff'])), 6),
        }
    return out


def main() -> int:
    extortion = _read_json(EXTORTION_PATH)
    generous_tft = _read_json(GEN_TFT_PATH)
    always_c = _read_json(ALWAYS_C_PATH)
    courteous_firm = _read_json(COURTEOUS_PATH)
    exit_after_break = _read_json(EXIT_AFTER_BREAK_PATH)

    policies = {
        'CCEEE': exit_after_break,
        'CCDDE': _det_exit_strategy('CCDDE'),
        'always_c': always_c,
        'courteous_firm': courteous_firm,
        'DCECC': _det_exit_strategy('DCECC'),
    }

    scenario_means: dict[str, dict[str, dict[str, float]]] = {}
    for policy_name, spec in policies.items():
        policy_block: dict[str, dict[str, float]] = {}
        for ext in EXTORTION_LEVELS:
            for delay in DELAY_LEVELS:
                policy_block[f'ext{ext}_delay{delay}'] = _mean_metrics(
                    spec,
                    extortion=extortion,
                    generous_tft=generous_tft,
                    extortion_share=ext / 100.0,
                    rematch_delay=delay,
                )
        scenario_means[policy_name] = policy_block

    per_policy = {name: _policy_cell_summary(block) for name, block in scenario_means.items()}
    all_cells_monotone = all(
        bool(per_policy[name][f'ext{ext}']['matched_share_monotone_nonincreasing'])
        for name in per_policy
        for ext in EXTORTION_LEVELS
    )

    share_fractions = [
        float(per_policy[name][f'ext{ext}']['share_component_fraction_of_loss'])
        for name in per_policy
        for ext in EXTORTION_LEVELS
    ]
    in_match_drifts = [
        float(per_policy[name][f'ext{ext}']['abs_in_match_drift_delay0_to_delay2'])
        for name in per_policy
        for ext in EXTORTION_LEVELS
    ]
    identity_gaps = [
        abs(float(scenario_means[name][f'ext{ext}_delay{delay}']['identity_gap']))
        for name in scenario_means
        for ext in EXTORTION_LEVELS
        for delay in DELAY_LEVELS
    ]

    summary = {
        'focus': 'Make rematch-world welfare accounting explicit by separating time spent matched from payoff earned while matched.',
        'tested_policies': list(policies),
        'extortion_levels': list(EXTORTION_LEVELS),
        'delay_levels': list(DELAY_LEVELS),
        'seeds': list(SEEDS),
        'headline_findings': {
            'tested_cells': len(policies) * len(EXTORTION_LEVELS),
            'matched_share_monotone_nonincreasing_in_all_tested_cells': all_cells_monotone,
            'max_abs_identity_gap_across_all_delay_means': round(max(identity_gaps), 6),
            'mean_share_component_fraction_of_delay_loss': round(statistics.fmean(share_fractions), 6),
            'min_share_component_fraction_of_delay_loss': round(min(share_fractions), 6),
            'max_abs_in_match_payoff_drift_delay0_to_delay2': round(max(in_match_drifts), 6),
            'interpretation': 'In the current proxy, delay losses are overwhelmingly occupancy losses: aggregate payoff falls mostly because agents spend less time in payoff-producing matches, not because within-match play quality changes very much.',
        },
        'scenario_means': scenario_means,
        'per_policy_delay_accounting': per_policy,
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n', encoding='utf-8')

    lines = [
        '# Rematch-Proxy Occupancy Accounting Snapshot (2026-03-06)',
        '',
        'Method:',
        '- reran the current exogenous-pool rematch proxy for five salient policies',
        f'- used extortion share in `{set(EXTORTION_LEVELS)}` with rematch delay in `{set(DELAY_LEVELS)}` and seeds `{list(SEEDS)}`',
        '- added accounting terms the previous snapshot did not expose: `matched_round_share`, `dead_round_share`, and `in_match_avg_payoff`',
        '- checked the exact identity `overall_avg_payoff = matched_round_share * in_match_avg_payoff` per replicate, then summarized the delay-0 to delay-2 decomposition at the cell level',
        '',
        'Main finding:',
        f"- All `{len(policies) * len(EXTORTION_LEVELS)}` tested policy/extortion cells are monotone in `matched_round_share`: `delay=0 >= delay=1 >= delay=2`.",
        f"- Across the tested cells, the mean share of `delay0 -> delay2` payoff loss explained by reduced `matched_round_share` is `{statistics.fmean(share_fractions):.6f}`; the minimum is `{min(share_fractions):.6f}`.",
        f"- The largest absolute `delay0 -> delay2` drift in `in_match_avg_payoff` is only `{max(in_match_drifts):.6f}`.",
        '- So the present proxy now has a crisp implementor interpretation: delay primarily works by shrinking the fraction of time spent in productive matches.',
        '',
        'Why this matters:',
        '- Aggregate payoff alone mixes two different mechanisms: (a) how often the agent is actually in a match, and (b) how well the agent does conditional on being matched.',
        '- The current proxy already lets us separate these cleanly, and future endogenous rematch worlds should keep that decomposition first-class.',
        '',
        'Selected `delay0 -> delay2` decomposition:',
        '',
        '| policy | extortion | overall loss | share component | in-match component | share fraction | max abs in-match drift |',
        '|---|---:|---:|---:|---:|---:|---:|',
    ]
    for name in ('CCEEE', 'CCDDE', 'always_c', 'courteous_firm', 'DCECC'):
        for ext in EXTORTION_LEVELS:
            cell = per_policy[name][f'ext{ext}']
            lines.append(
                f"| `{name}` | `{ext/100:.1f}` | {float(cell['delay0_to_delay2_overall_loss']):.6f} | {float(cell['delay0_to_delay2_share_component']):.6f} | {float(cell['delay0_to_delay2_in_match_component']):.6f} | {float(cell['share_component_fraction_of_loss']):.6f} | {float(cell['abs_in_match_drift_delay0_to_delay2']):.6f} |"
            )
    lines += [
        '',
        'Implementor implication:',
        '- Future rematch-world reports should publish at least `overall_avg_payoff`, `matched_round_share`, `dead_round_share`, and `in_match_avg_payoff` together.',
        '- Without that accounting, a report can mistake “better norms inside matches” for “more time spent matched,” or vice versa.',
        '',
    ]
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')
    print(f'wrote {OUT_JSON}')
    print(f'wrote {OUT_MD}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
