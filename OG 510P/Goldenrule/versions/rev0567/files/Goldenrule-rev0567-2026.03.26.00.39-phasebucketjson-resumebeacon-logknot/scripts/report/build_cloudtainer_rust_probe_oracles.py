#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
QUEUE_PATH = ROOT / 'artifacts' / 'reports' / 'rust_external_test_queue.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'cloudtainer_rust_probe_oracles.json'
OUT_MD = ROOT / 'docs' / 'CLOUDTAINER_RUST_PROBE_ORACLES.md'

ACTION_C = 'c'
ACTION_D = 'd'
ACTION_EXIT = 'exit'
ACTIONS = (ACTION_C, ACTION_D, ACTION_EXIT)

CODE_ANCHORS = {
    'simple_standing_declared': 'crates/gr_engine/src/spec.rs:133-145',
    'task_default_standing': 'crates/gr_engine/src/spec.rs:300-314',
    'probe_expansion_task_new': 'crates/gr_engine/src/probe.rs:379-391',
    'sim_standing_bootstrap': 'crates/gr_engine/src/sim.rs:488-489,527-528',
    'sim_standing_update': 'crates/gr_engine/src/sim.rs:647-664',
    'sim_seed_streams': 'crates/gr_engine/src/sim.rs:505-522',
    'scaling_prefix_tasks': 'crates/gr_engine/src/metamorphic.rs:457-483,498-521',
}

SCALING_PREFIX_CONFIG = {
    'base_rounds': 20,
    'extended_rounds': 60,
}


@dataclass(frozen=True)
class PlayerState:
    last_self_intended: str | None = None
    last_opp_observed: str | None = None
    fsm_state: int | None = None


@dataclass(frozen=True)
class JointState:
    a: PlayerState
    b: PlayerState


def _round6(value: float) -> float:
    if math.isnan(value):
        return value
    return round(float(value), 6)


def _fmt_num(value: float) -> str:
    if isinstance(value, int):
        return str(value)
    if math.isnan(value):
        return 'nan'
    text = f'{value:.6f}'.rstrip('0').rstrip('.')
    return text if text else '0'


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _action_from_builtin(kind: str, obs: PlayerState, p_cooperate: float) -> list[tuple[str, float, int | None]]:
    if kind == 'always_c':
        return [(ACTION_C, 1.0, None)]
    if kind == 'always_d':
        return [(ACTION_D, 1.0, None)]
    if kind == 'tit_for_tat':
        if obs.last_opp_observed in (None, ACTION_EXIT):
            return [(ACTION_C, 1.0, None)]
        return [(obs.last_opp_observed, 1.0, None)]
    if kind == 'win_stay_lose_shift':
        last_self = obs.last_self_intended
        last_opp = obs.last_opp_observed
        if last_self is None or last_opp is None or ACTION_EXIT in (last_self, last_opp):
            return [(ACTION_C, 1.0, None)]
        win = (last_self, last_opp) in {(ACTION_C, ACTION_C), (ACTION_D, ACTION_C)}
        action = last_self if win else (ACTION_D if last_self == ACTION_C else ACTION_C)
        return [(action, 1.0, None)]
    if kind == 'random':
        p = max(0.0, min(1.0, float(p_cooperate)))
        if p == 0.0:
            return [(ACTION_D, 1.0, None)]
        if p == 1.0:
            return [(ACTION_C, 1.0, None)]
        return [(ACTION_C, p, None), (ACTION_D, 1.0 - p, None)]
    raise ValueError(f'unsupported builtin kind: {kind}')


def _memory_key(obs: PlayerState) -> str:
    pair = (obs.last_self_intended, obs.last_opp_observed)
    if pair == (None, None):
        return 'p0'
    if pair == (ACTION_C, ACTION_C):
        return 'p_cc'
    if pair == (ACTION_C, ACTION_D):
        return 'p_cd'
    if pair == (ACTION_D, ACTION_C):
        return 'p_dc'
    if pair == (ACTION_D, ACTION_D):
        return 'p_dd'
    return 'p0'


def _memory_exit_key(obs: PlayerState) -> str:
    pair = (obs.last_self_intended, obs.last_opp_observed)
    if pair == (None, None):
        return 'p0'
    if pair == (ACTION_C, ACTION_C):
        return 'p_cc'
    if pair == (ACTION_C, ACTION_D):
        return 'p_cd'
    if pair == (ACTION_D, ACTION_C):
        return 'p_dc'
    if pair == (ACTION_D, ACTION_D):
        return 'p_dd'
    return 'p0'


def _decision_distribution(strategy: dict[str, Any], obs: PlayerState) -> list[tuple[str, float, int | None]]:
    family = strategy['family']
    if family == 'builtin':
        params = strategy.get('params') or {}
        return _action_from_builtin(strategy['kind'], obs, float(params.get('p_cooperate', 1.0)))
    if family == 'memory_one':
        key = _memory_key(obs)
        p = max(0.0, min(1.0, float(strategy[key])))
        if p == 0.0:
            return [(ACTION_D, 1.0, None)]
        if p == 1.0:
            return [(ACTION_C, 1.0, None)]
        return [(ACTION_C, p, None), (ACTION_D, 1.0 - p, None)]
    if family == 'memory_one_exit':
        key = _memory_exit_key(obs)
        pc = float(strategy[f'{key}_c'])
        pd = float(strategy[f'{key}_d'])
        pe = max(0.0, 1.0 - pc - pd)
        out: list[tuple[str, float, int | None]] = []
        if pc > 0:
            out.append((ACTION_C, pc, None))
        if pd > 0:
            out.append((ACTION_D, pd, None))
        if pe > 0:
            out.append((ACTION_EXIT, pe, None))
        return out
    if family == 'fsm':
        current_state = strategy['initial_state'] if obs.fsm_state is None else obs.fsm_state
        state_map = {int(s['id']): s for s in strategy['states']}
        state = deepcopy(state_map[int(current_state)])
        transitioned_state = int(current_state)
        transitioned = False
        for trans in state.get('trans_signals') or []:
            signal = trans.get('signal', 'none')
            if signal == 'none':
                transitioned_state = int(trans['next_state'])
                transitioned = True
                break
        if not transitioned and obs.last_opp_observed is not None:
            if obs.last_opp_observed == ACTION_C:
                transitioned_state = int(state['trans_c'])
            elif obs.last_opp_observed == ACTION_D:
                transitioned_state = int(state['trans_d'])
            else:
                transitioned_state = int(state['trans_exit'])
        out_state = state_map.get(transitioned_state)
        if out_state is None:
            return [(ACTION_D, 1.0, transitioned_state)]
        p = max(0.0, min(1.0, float(out_state['output_c'])))
        if p == 0.0:
            return [(ACTION_D, 1.0, transitioned_state)]
        if p == 1.0:
            return [(ACTION_C, 1.0, transitioned_state)]
        return [(ACTION_C, p, transitioned_state), (ACTION_D, 1.0 - p, transitioned_state)]
    raise ValueError(f'unsupported strategy family: {family}')


def _impl_prob(noise: dict[str, Any], player: str) -> float:
    kind = noise.get('kind', 'none')
    if kind == 'none':
        return 0.0
    if kind == 'implementation_flip':
        return float(noise['p'])
    if kind == 'observation_flip':
        return 0.0
    if kind == 'iid':
        return float(noise['p_implementation'])
    if kind == 'asymmetric_iid':
        return float(noise['p_implementation_a'] if player == 'a' else noise['p_implementation_b'])
    raise ValueError(f'unsupported noise kind: {kind}')


def _obs_prob(noise: dict[str, Any], observer: str) -> float:
    kind = noise.get('kind', 'none')
    if kind == 'none':
        return 0.0
    if kind == 'implementation_flip':
        return 0.0
    if kind == 'observation_flip':
        return float(noise['p'])
    if kind == 'iid':
        return float(noise['p_observation'])
    if kind == 'asymmetric_iid':
        return float(noise['p_observation_a'] if observer == 'a' else noise['p_observation_b'])
    raise ValueError(f'unsupported noise kind: {kind}')


def _flip_distribution(action: str, p: float) -> list[tuple[str, float]]:
    p = max(0.0, min(1.0, float(p)))
    if action == ACTION_EXIT or p == 0.0:
        return [(action, 1.0)]
    flipped = ACTION_D if action == ACTION_C else ACTION_C
    if p == 1.0:
        return [(flipped, 1.0)]
    return [(action, 1.0 - p), (flipped, p)]


def _payoff(payoffs: dict[str, Any], a: str, b: str) -> tuple[float, float]:
    exit_payoff = float(payoffs.get('exit', 0.0))
    if a == ACTION_EXIT or b == ACTION_EXIT:
        return (exit_payoff, exit_payoff)
    if a == ACTION_C and b == ACTION_C:
        return (float(payoffs['r']), float(payoffs['r']))
    if a == ACTION_C and b == ACTION_D:
        return (float(payoffs['s']), float(payoffs['t']))
    if a == ACTION_D and b == ACTION_C:
        return (float(payoffs['t']), float(payoffs['s']))
    return (float(payoffs['p']), float(payoffs['p']))


def _update_standing(current: float, action: str, opp_standing: float, rule: Any) -> float:
    if rule == 'image_scoring':
        val = 1.0 if action == ACTION_C else 0.0
        return max(0.0, min(1.0, 0.9 * current + 0.1 * val))
    if isinstance(rule, dict) and 'standing_norm' in rule:
        threshold = float(rule['standing_norm']['threshold'])
        if action == ACTION_C:
            return min(1.0, current + 0.1)
        if action == ACTION_D:
            return max(0.0, current - 0.2) if opp_standing >= threshold else current
        return current
    raise ValueError(f'unsupported standing update rule: {rule!r}')


def _simulate_exact_path(probe: dict[str, Any]) -> dict[str, Any]:
    matchup = probe['matchups'][0]
    world = probe['world']
    rounds = int(world['termination']['rounds'])
    payoffs = world['game']['payoffs']
    noise = world.get('noise') or {'kind': 'none'}
    if noise.get('kind') != 'none':
        raise ValueError('exact path simulator only supports deterministic noise=none probes')

    reputation = world.get('reputation') or {'kind': 'none'}
    current_standing_a = 1.0
    current_standing_b = 1.0
    state = JointState(
        a=PlayerState(last_self_intended=None, last_opp_observed=None, fsm_state=matchup['strategy_a'].get('initial_state')),
        b=PlayerState(last_self_intended=None, last_opp_observed=None, fsm_state=matchup['strategy_b'].get('initial_state')),
    )
    trace: list[dict[str, Any]] = []
    total_a = 0.0
    total_b = 0.0
    coop_a = 0
    coop_b = 0
    mutual_c = 0
    mutual_d = 0
    executed_rounds = 0

    for round_idx in range(rounds):
        a_choices = _decision_distribution(matchup['strategy_a'], state.a)
        b_choices = _decision_distribution(matchup['strategy_b'], state.b)
        if len(a_choices) != 1 or len(b_choices) != 1 or a_choices[0][1] != 1.0 or b_choices[0][1] != 1.0:
            raise ValueError('exact path simulator encountered stochastic branch')
        a_intended, _, a_fsm = a_choices[0]
        b_intended, _, b_fsm = b_choices[0]
        a_exec = a_intended
        b_exec = b_intended
        a_obs = b_exec
        b_obs = a_exec
        pay_a, pay_b = _payoff(payoffs, a_exec, b_exec)

        total_a += pay_a
        total_b += pay_b
        coop_a += 1 if a_exec == ACTION_C else 0
        coop_b += 1 if b_exec == ACTION_C else 0
        mutual_c += 1 if a_exec == ACTION_C and b_exec == ACTION_C else 0
        mutual_d += 1 if a_exec == ACTION_D and b_exec == ACTION_D else 0
        executed_rounds += 1

        trace.append(
            {
                'round': round_idx,
                'standing_a_pre_update': _round6(current_standing_a),
                'standing_b_pre_update': _round6(current_standing_b),
                'a_intended': a_intended,
                'b_intended': b_intended,
                'a_executed': a_exec,
                'b_executed': b_exec,
                'a_observed_opp': a_obs,
                'b_observed_opp': b_obs,
                'payoff_a': _round6(pay_a),
                'payoff_b': _round6(pay_b),
            }
        )

        next_a_state = PlayerState(last_self_intended=a_intended, last_opp_observed=a_obs, fsm_state=a_fsm)
        next_b_state = PlayerState(last_self_intended=b_intended, last_opp_observed=b_obs, fsm_state=b_fsm)

        if reputation.get('kind') == 'simple_standing':
            rule = reputation['update_rule']
            next_standing_a = _update_standing(current_standing_a, a_exec, current_standing_b, rule)
            next_standing_b = _update_standing(current_standing_b, b_exec, current_standing_a, rule)
            trace[-1]['standing_a_post_update'] = _round6(next_standing_a)
            trace[-1]['standing_b_post_update'] = _round6(next_standing_b)
            current_standing_a = next_standing_a
            current_standing_b = next_standing_b

        state = JointState(a=next_a_state, b=next_b_state)
        if a_exec == ACTION_EXIT or b_exec == ACTION_EXIT:
            break

    denom = max(1, executed_rounds)
    stats = {
        'rounds': executed_rounds,
        'avg_payoff_a': _round6(total_a / denom),
        'avg_payoff_b': _round6(total_b / denom),
        'coop_rate_a': _round6(coop_a / denom),
        'coop_rate_b': _round6(coop_b / denom),
        'mutual_coop_rate': _round6(mutual_c / denom),
        'mutual_defect_rate': _round6(mutual_d / denom),
    }
    result = {
        'mode': 'exact_path',
        'probe_id': probe['id'],
        'matchup_id': matchup['id'],
        'replications': int(matchup['replications']),
        'rounds_per_replication': executed_rounds,
        'mean_stats': stats,
        'trace': trace,
        'trace_rounds_recorded': len(trace),
    }
    if reputation.get('kind') == 'simple_standing':
        result['standing_bootstrap'] = {
            'declared_initial_standing': _round6(float(reputation['initial_standing'])),
            'effective_task_initial_standing': 1.0,
            'warning': 'current probe expansion seeds TaskSpec standing_a/standing_b at 1.0, so declared world.reputation.initial_standing is inert for these probe seeds',
        }
    return result


def _initial_joint_state(matchup: dict[str, Any]) -> JointState:
    return JointState(
        a=PlayerState(last_self_intended=None, last_opp_observed=None, fsm_state=matchup['strategy_a'].get('initial_state')),
        b=PlayerState(last_self_intended=None, last_opp_observed=None, fsm_state=matchup['strategy_b'].get('initial_state')),
    )


def _simulate_exact_expectation(probe: dict[str, Any]) -> dict[str, Any]:
    matchup = probe['matchups'][0]
    world = probe['world']
    if world['termination']['kind'] != 'fixed':
        raise ValueError('expectation oracle only supports fixed horizons')
    rounds = int(world['termination']['rounds'])
    payoffs = world['game']['payoffs']
    noise = world.get('noise') or {'kind': 'none'}
    if (world.get('reputation') or {'kind': 'none'}).get('kind') != 'none':
        raise ValueError('expectation oracle currently assumes reputation=None')

    dist: dict[JointState, float] = {_initial_joint_state(matchup): 1.0}
    total_a = 0.0
    total_b = 0.0
    coop_a = 0.0
    coop_b = 0.0
    mutual_c = 0.0
    mutual_d = 0.0

    for _round_idx in range(rounds):
        next_dist: defaultdict[JointState, float] = defaultdict(float)
        for state, state_prob in dist.items():
            for a_intended, p_a, a_fsm in _decision_distribution(matchup['strategy_a'], state.a):
                for b_intended, p_b, b_fsm in _decision_distribution(matchup['strategy_b'], state.b):
                    branch_prob = state_prob * p_a * p_b
                    if branch_prob == 0.0:
                        continue
                    for a_exec, p_impl_a in _flip_distribution(a_intended, _impl_prob(noise, 'a')):
                        for b_exec, p_impl_b in _flip_distribution(b_intended, _impl_prob(noise, 'b')):
                            pb = branch_prob * p_impl_a * p_impl_b
                            if pb == 0.0:
                                continue
                            pay_a, pay_b = _payoff(payoffs, a_exec, b_exec)
                            total_a += pb * pay_a
                            total_b += pb * pay_b
                            coop_a += pb * (1.0 if a_exec == ACTION_C else 0.0)
                            coop_b += pb * (1.0 if b_exec == ACTION_C else 0.0)
                            mutual_c += pb * (1.0 if a_exec == ACTION_C and b_exec == ACTION_C else 0.0)
                            mutual_d += pb * (1.0 if a_exec == ACTION_D and b_exec == ACTION_D else 0.0)
                            if a_exec == ACTION_EXIT or b_exec == ACTION_EXIT:
                                raise ValueError('expectation oracle encountered early-exit branch')
                            for a_obs, p_obs_a in _flip_distribution(b_exec, _obs_prob(noise, 'a')):
                                for b_obs, p_obs_b in _flip_distribution(a_exec, _obs_prob(noise, 'b')):
                                    pnext = pb * p_obs_a * p_obs_b
                                    if pnext == 0.0:
                                        continue
                                    next_dist[
                                        JointState(
                                            a=PlayerState(last_self_intended=a_intended, last_opp_observed=a_obs, fsm_state=a_fsm),
                                            b=PlayerState(last_self_intended=b_intended, last_opp_observed=b_obs, fsm_state=b_fsm),
                                        )
                                    ] += pnext
        dist = dict(next_dist)

    total_mass = sum(dist.values())
    if not math.isclose(total_mass, 1.0, rel_tol=1e-12, abs_tol=1e-12):
        raise ValueError(f'probability mass drifted to {total_mass}')

    stats = {
        'rounds': rounds,
        'avg_payoff_a': _round6(total_a / rounds),
        'avg_payoff_b': _round6(total_b / rounds),
        'coop_rate_a': _round6(coop_a / rounds),
        'coop_rate_b': _round6(coop_b / rounds),
        'mutual_coop_rate': _round6(mutual_c / rounds),
        'mutual_defect_rate': _round6(mutual_d / rounds),
    }
    return {
        'mode': 'exact_expectation',
        'probe_id': probe['id'],
        'matchup_id': matchup['id'],
        'replications': int(matchup['replications']),
        'rounds_per_replication': rounds,
        'mean_stats': stats,
        'terminal_state_support': len(dist),
        'probability_mass': _round6(total_mass),
    }


def _seed_oracle_cache(queue: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cache: dict[str, dict[str, Any]] = {}
    for entry in queue['entries']:
        seed_path = entry['preferred_seed']['path']
        if seed_path in cache:
            continue
        probe = _load_json(ROOT / seed_path)
        reputation_kind = (probe['world'].get('reputation') or {'kind': 'none'}).get('kind', 'none')
        noise_kind = (probe['world'].get('noise') or {'kind': 'none'}).get('kind', 'none')
        families = {probe['matchups'][0]['strategy_a']['family'], probe['matchups'][0]['strategy_b']['family']}
        deterministic = noise_kind == 'none' and reputation_kind == 'simple_standing' or (
            noise_kind == 'none' and families <= {'builtin', 'fsm', 'memory_one_exit'} and probe['id'] in {
                'ipd_c_vs_d_smoke_v1',
                'mutual_defect_rate_guardrail_probe_v1',
                'fsm_grim_trigger_probe_v1',
                'memory_one_exit_after_break_probe_v1',
                'simple_standing_image_scoring_probe_v1',
                'simple_standing_standing_norm_probe_v1',
            }
        )
        if deterministic:
            cache[seed_path] = _simulate_exact_path(probe)
        else:
            cache[seed_path] = _simulate_exact_expectation(probe)
    return cache


def _row_from_entry(entry: dict[str, Any], oracle_cache: dict[str, dict[str, Any]]) -> dict[str, Any]:
    seed = entry['preferred_seed']
    oracle = deepcopy(oracle_cache[seed['path']])
    family = entry['family']
    variant = entry['variant']
    row = {
        'family': family,
        'variant': variant,
        'target_lane': entry['target_lane'],
        'proposed_test_name': entry['proposed_test_name'],
        'seed_path': seed['path'],
        'seed_example_id': seed.get('example_id'),
        'seed_line': seed.get('line'),
        'oracle_mode': oracle['mode'],
        'probe_id': oracle['probe_id'],
        'matchup_id': oracle['matchup_id'],
        'replications': oracle['replications'],
        'rounds_per_replication': oracle['rounds_per_replication'],
        'mean_stats': oracle['mean_stats'],
        'notes': [],
    }
    if oracle['mode'] == 'exact_path':
        row['path_trace_excerpt'] = oracle['trace'][: min(4, len(oracle['trace']))]
        if 'standing_bootstrap' in oracle:
            row['standing_bootstrap'] = oracle['standing_bootstrap']
            row['notes'].append(oracle['standing_bootstrap']['warning'])
    else:
        row['terminal_state_support'] = oracle['terminal_state_support']
        row['probability_mass'] = oracle['probability_mass']

    if family == 'metamorphic_kind' and variant == 'scaling_prefix_stability':
        row['oracle_mode'] = 'exact_expectation'
        row['metamorphic_prefix_witness'] = {
            'base_rounds': SCALING_PREFIX_CONFIG['base_rounds'],
            'extended_rounds': SCALING_PREFIX_CONFIG['extended_rounds'],
            'expected_pass': True,
            'reason': 'the probe seed uses fixed-horizon tasks with no exit-capable strategies, and the metamorphic check rebuilds both tasks from the same match_seed while asking both traces to record the same first base_rounds steps',
            'anchors': [CODE_ANCHORS['sim_seed_streams'], CODE_ANCHORS['scaling_prefix_tasks']],
        }
        row['notes'].append('same-seed fixed-horizon prefix coupling is exact here because neither side can exit and both tasks replay the same per-round RNG stream prefixes')
    if family == 'assertion_kind':
        if variant == 'avg_payoff_b_at_least':
            row['assertion_observed'] = row['mean_stats']['avg_payoff_b']
        elif variant == 'coop_rate_a_at_least':
            row['assertion_observed'] = row['mean_stats']['coop_rate_a']
        elif variant == 'coop_rate_b_at_least':
            row['assertion_observed'] = row['mean_stats']['coop_rate_b']
        elif variant == 'mutual_defect_rate_at_most':
            row['assertion_observed'] = row['mean_stats']['mutual_defect_rate']
    return row


def collect() -> dict[str, Any]:
    queue = _load_json(QUEUE_PATH)
    oracle_cache = _seed_oracle_cache(queue)
    rows = [_row_from_entry(entry, oracle_cache) for entry in queue['entries']]
    warnings = [row for row in rows if 'standing_bootstrap' in row]
    summary = {
        'queue_row_count': len(rows),
        'unique_preferred_probe_seed_count': len(oracle_cache),
        'exact_path_witness_rows': sum(1 for row in rows if row['oracle_mode'] == 'exact_path'),
        'exact_expectation_witness_rows': sum(1 for row in rows if row['oracle_mode'] == 'exact_expectation'),
        'rows_with_inert_initial_standing_warning': len(warnings),
        'inert_initial_standing_seed_paths': sorted({row['seed_path'] for row in warnings}),
    }
    return {
        'tool': 'build_cloudtainer_rust_probe_oracles',
        'generated_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source_queue_report': str(QUEUE_PATH.relative_to(ROOT)),
        'code_anchors': dict(CODE_ANCHORS),
        'summary': summary,
        'rows': rows,
    }


def _render_markdown(report: dict[str, Any]) -> str:
    summary = report['summary']
    lines = [
        '# Cloudtainer Rust Probe Oracles',
        '',
        'This card gives the blocked cloudtainer a compact semantic oracle surface for the current Rust comeback queue: exact path witnesses where the preferred probe seed is deterministic, and exact finite-horizon expectation witnesses where the preferred probe seed is stochastic.',
        '',
        '## Summary',
        '',
        f"- queue rows covered: `{summary['queue_row_count']}` from `artifacts/reports/rust_external_test_queue.json`",
        f"- unique preferred probe seeds: `{summary['unique_preferred_probe_seed_count']}`",
        f"- exact path witnesses: `{summary['exact_path_witness_rows']}` rows",
        f"- exact expectation witnesses: `{summary['exact_expectation_witness_rows']}` rows",
        f"- rows with inert `initial_standing` warning: `{summary['rows_with_inert_initial_standing_warning']}`",
        '',
        '## Why this exists',
        '',
        '- the archive already had the comeback queue, patch plan, and execution card, but a blocked session still lacked one compact place to see the expected semantics of the preferred probe seeds without `cargo`',
        f"- `ReputationModelSpec::SimpleStanding` declares `initial_standing`, but `TaskSpec::new(...)` still seeds `standing_a`/`standing_b` from a fixed `1.0`, probe expansion calls `TaskSpec::new(...)` directly, and `run_match(...)` bootstraps the live standing state from those task fields rather than from the world declaration: `{CODE_ANCHORS['simple_standing_declared']}`, `{CODE_ANCHORS['task_default_standing']}`, `{CODE_ANCHORS['probe_expansion_task_new']}`, `{CODE_ANCHORS['sim_standing_bootstrap']}`, `{CODE_ANCHORS['sim_standing_update']}`",
        '',
        '## Row-by-row witness table',
        '',
        '| Family | Variant | Lane | Oracle | Preferred seed | Witness headline |',
        '| --- | --- | --- | --- | --- | --- |',
    ]
    for row in report['rows']:
        stats = row['mean_stats']
        headline_bits = [
            f"avg_a={_fmt_num(stats['avg_payoff_a'])}",
            f"avg_b={_fmt_num(stats['avg_payoff_b'])}",
            f"coop_a={_fmt_num(stats['coop_rate_a'])}",
            f"coop_b={_fmt_num(stats['coop_rate_b'])}",
        ]
        if 'assertion_observed' in row:
            headline_bits.append(f"observed={_fmt_num(row['assertion_observed'])}")
        if 'standing_bootstrap' in row:
            headline_bits.append('declared initial_standing currently inert')
        if 'metamorphic_prefix_witness' in row:
            headline_bits.append('same-seed prefix pass is exact here')
        lines.append(
            f"| `{row['family']}` | `{row['variant']}` | `{row['target_lane']}` | `{row['oracle_mode']}` | `{row['seed_path']}` | {'; '.join(headline_bits)} |"
        )

    lines.extend(['', '## Witness details', ''])
    for row in report['rows']:
        lines.append(f"### `{row['proposed_test_name']}`")
        lines.append('')
        lines.append(f"- seed: `{row['seed_path']}` line `{row['seed_line']}` (`{row['seed_example_id']}`)")
        lines.append(f"- lane: `{row['target_lane']}`")
        lines.append(f"- oracle: `{row['oracle_mode']}` on probe `{row['probe_id']}` / matchup `{row['matchup_id']}`")
        stats = row['mean_stats']
        lines.append(
            '- witness stats: '
            + ', '.join(
                [
                    f"`avg_payoff_a={_fmt_num(stats['avg_payoff_a'])}`",
                    f"`avg_payoff_b={_fmt_num(stats['avg_payoff_b'])}`",
                    f"`coop_rate_a={_fmt_num(stats['coop_rate_a'])}`",
                    f"`coop_rate_b={_fmt_num(stats['coop_rate_b'])}`",
                    f"`mutual_coop_rate={_fmt_num(stats['mutual_coop_rate'])}`",
                    f"`mutual_defect_rate={_fmt_num(stats['mutual_defect_rate'])}`",
                ]
            )
        )
        if row['oracle_mode'] == 'exact_path':
            lines.append('- exact path excerpt (first recorded rounds):')
            for step in row['path_trace_excerpt']:
                round_bits = [
                    f"r{step['round']}",
                    f"pre=({_fmt_num(step['standing_a_pre_update'])},{_fmt_num(step['standing_b_pre_update'])})",
                    f"intend=({step['a_intended']},{step['b_intended']})",
                    f"exec=({step['a_executed']},{step['b_executed']})",
                    f"obs=({step['a_observed_opp']},{step['b_observed_opp']})",
                    f"pay=({_fmt_num(step['payoff_a'])},{_fmt_num(step['payoff_b'])})",
                ]
                if 'standing_a_post_update' in step:
                    round_bits.append(f"post=({_fmt_num(step['standing_a_post_update'])},{_fmt_num(step['standing_b_post_update'])})")
                lines.append(f"  - {'; '.join(round_bits)}")
        else:
            lines.append(f"- expectation support: `{row['terminal_state_support']}` terminal states with probability mass `{_fmt_num(row['probability_mass'])}`")
        if 'standing_bootstrap' in row:
            sb = row['standing_bootstrap']
            lines.append(
                f"- standing bootstrap warning: declared `initial_standing={_fmt_num(sb['declared_initial_standing'])}` but effective task start is `{_fmt_num(sb['effective_task_initial_standing'])}` under the current probe-expansion path"
            )
        if 'metamorphic_prefix_witness' in row:
            mpw = row['metamorphic_prefix_witness']
            lines.append(
                f"- scaling-prefix witness: base `{mpw['base_rounds']}` vs extended `{mpw['extended_rounds']}` is an exact pass here because both tasks reuse the same `match_seed`, both traces request the same first `{mpw['base_rounds']}` rounds, and neither strategy family can exit; anchors: `{mpw['anchors'][0]}`, `{mpw['anchors'][1]}`"
            )
        for note in row['notes']:
            lines.append(f"- note: {note}")
        lines.append('')

    lines.extend(
        [
            '## Practical use',
            '',
            '- while Rust is still blocked, use this card to decide whether a future external test should be asserting an exact path, an exact mean statistic, or an exact same-seed prefix property before the first Rust-capable inheritor touches `probe_run.rs` or `metamorphic_suite.rs`',
            '- once `cargo` exists again, the highest-value follow-up is still to land the queued external tests and then compare their live outputs to the witnesses recorded here rather than reopening the full code surface first',
            '',
        ]
    )
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Build the blocked-session exact/expectation oracle card for the Rust comeback probe seeds.')
    parser.add_argument('--write', action='store_true', help='write the markdown/json outputs instead of printing the JSON report')
    args = parser.parse_args()

    report = collect()
    if args.write:
        OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        OUT_MD.write_text(_render_markdown(report), encoding='utf-8')
        print(f'wrote {OUT_JSON.relative_to(ROOT)}')
        print(f'wrote {OUT_MD.relative_to(ROOT)}')
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
