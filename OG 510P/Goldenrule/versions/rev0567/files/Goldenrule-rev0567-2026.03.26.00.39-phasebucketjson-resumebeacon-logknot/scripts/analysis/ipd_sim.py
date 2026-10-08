"""
Pure-Python IPD simulation mirroring gr_engine/src/sim.rs semantics.
Used for analysis when the Rust engine is not compiled.

Standard payoffs: (C,C)=3, (C,D)=0, (D,C)=5, (D,D)=1
Memory-one strategy: (p0, p_cc, p_cd, p_dc, p_dd)
"""
import random
from typing import NamedTuple, Tuple


PAYOFFS = {
    ('C','C'): (3.0, 3.0),
    ('C','D'): (0.0, 5.0),
    ('D','C'): (5.0, 0.0),
    ('D','D'): (1.0, 1.0),
}

EXTORTION_CHI3 = (1.0, 1.0, 0.0, 1/3, 0.0)   # chi=3 extortion strategy from examples
TFT            = (1.0, 1.0, 0.0, 1.0, 0.0)
ALWAYS_C       = (1.0, 1.0, 1.0, 1.0, 1.0)
ALWAYS_D       = (0.0, 0.0, 0.0, 0.0, 0.0)
WSLS           = (1.0, 1.0, 0.0, 0.0, 1.0)


def mem1_action(params, last_self, last_opp, rng):
    p0, p_cc, p_cd, p_dc, p_dd = params
    if last_self is None:
        p = p0
    elif last_self == 'C' and last_opp == 'C':
        p = p_cc
    elif last_self == 'C' and last_opp == 'D':
        p = p_cd
    elif last_self == 'D' and last_opp == 'C':
        p = p_dc
    else:
        p = p_dd
    return 'C' if rng.random() < p else 'D'


def run_match(strat_a, strat_b, rounds=200, seed=None, noise=0.0):
    rng = random.Random(seed)
    last_a, last_b = None, None
    total_a = total_b = 0.0
    for _ in range(rounds):
        a = mem1_action(strat_a, last_a, last_b, rng)
        b = mem1_action(strat_b, last_b, last_a, rng)
        # implementation noise
        if noise > 0:
            if rng.random() < noise: a = 'D' if a == 'C' else 'C'
            if rng.random() < noise: b = 'D' if b == 'C' else 'C'
        pa, pb = PAYOFFS[(a, b)]
        total_a += pa
        total_b += pb
        last_a, last_b = a, b
    return total_a / rounds, total_b / rounds


def run_match_replicated(strat_a, strat_b, rounds=200, reps=20, noise=0.0):
    results = [run_match(strat_a, strat_b, rounds, seed=i*1000+7, noise=noise)
               for i in range(reps)]
    avg_a = sum(r[0] for r in results) / reps
    avg_b = sum(r[1] for r in results) / reps
    return avg_a, avg_b
