"""
Universalization frontier analysis for memory-one strategies.

The Golden Rule's universalization test asks: if everyone played this strategy,
would the resulting world be one you would endorse?

Formally, a strategy passes the universalization test if:
  1. self_play_payoff >= threshold  (the universalized world is cooperative)
  2. payoff_gap_vs_extortion <= 0   (does not feed the vampire)
  3. always_c_exploitation <= epsilon (does not exploit the unconditionally cooperative)

This script samples the memory-one space and maps the frontier.
"""
import sys, os, json, random, math
sys.path.insert(0, '/tmp/rev0028/scripts/analysis')
from ipd_sim import run_match_replicated, EXTORTION_CHI3, ALWAYS_C, TFT, WSLS, ALWAYS_D

ROUNDS = 200
REPS = 30
NOISE = 0.0

# The three axes of the tradeoff (from memory_one_tradeoff_against_extortion.md)
# 1. self_play >= 2.5  (cooperative self-play)
# 2. payoff_gap vs extortion <= 0  (nonnegative fairness)
# 3. always_c_exploitation <= 0.1  (does not exploit cooperators)

def evaluate(s, reps=REPS):
    self_a, _    = run_match_replicated(s, s,             ROUNDS, reps)
    vs_e_a, vs_e_b = run_match_replicated(s, EXTORTION_CHI3, ROUNDS, reps)
    vs_ac_a, vs_ac_b = run_match_replicated(s, ALWAYS_C, ROUNDS, reps)

    payoff_gap      = vs_e_b - vs_e_a          # positive = vampire wins
    ac_exploitation = vs_ac_a - vs_ac_b        # positive = exploiting cooperator

    return {
        'self_play':        round(self_a, 4),
        'vs_extortion_own': round(vs_e_a, 4),
        'payoff_gap':       round(payoff_gap, 4),
        'ac_exploitation':  round(ac_exploitation, 4),
        'passes_self_play': self_a >= 2.5,
        'passes_fairness':  payoff_gap <= 0.0,
        'passes_ac_test':   ac_exploitation <= 0.1,
    }


def passes_all(ev):
    return ev['passes_self_play'] and ev['passes_fairness'] and ev['passes_ac_test']


def sample_mem1_space(n=5000, seed=42):
    rng = random.Random(seed)
    strategies = []
    for _ in range(n):
        strategies.append(tuple(rng.random() for _ in range(5)))
    return strategies


def named_strategies():
    return {
        'TFT':        (1.0, 1.0, 0.0, 1.0, 0.0),
        'WSLS':       (1.0, 1.0, 0.0, 0.0, 1.0),
        'AlwaysC':    (1.0, 1.0, 1.0, 1.0, 1.0),
        'AlwaysD':    (0.0, 0.0, 0.0, 0.0, 0.0),
        'Extortion3': EXTORTION_CHI3,
        'GRIM':       (1.0, 1.0, 0.0, 0.0, 0.0),
        'GenTFT_0.9': (1.0, 1.0, 0.1, 1.0, 0.0),
    }


if __name__ == '__main__':
    print("=== Named strategy evaluations ===")
    named = named_strategies()
    named_results = {}
    for name, s in named.items():
        ev = evaluate(s)
        named_results[name] = ev
        flag = '✓ PASSES ALL' if passes_all(ev) else ''
        print(f"{name:15s}  self={ev['self_play']:.3f}  gap={ev['payoff_gap']:+.3f}  "
              f"ac_exploit={ev['ac_exploitation']:+.3f}  {flag}")

    print("\n=== Random sample: searching for strategies that pass all three criteria ===")
    sample = sample_mem1_space(8000)
    passers = []
    for s in sample:
        ev = evaluate(s, reps=15)
        if passes_all(ev):
            passers.append((s, ev))

    n = len(sample)
    print(f"Sampled {n} random memory-one strategies")
    print(f"Passed all three criteria: {len(passers)} ({100*len(passers)/n:.1f}%)")

    if passers:
        print("\nTop passers by self-play payoff:")
        passers.sort(key=lambda x: -x[1]['self_play'])
        for s, ev in passers[:5]:
            print(f"  p=({s[0]:.3f},{s[1]:.3f},{s[2]:.3f},{s[3]:.3f},{s[4]:.3f})  "
                  f"self={ev['self_play']:.3f}  gap={ev['payoff_gap']:+.3f}  "
                  f"ac_exploit={ev['ac_exploitation']:+.3f}")
    else:
        print("\nNo strategies passed all three criteria in this sample.")
        print("Re-examining with relaxed fairness threshold (gap <= 0.5)...")
        near_passers = [(s, evaluate(s, reps=20))
                        for s in random.Random(99).sample(sample, 500)]
        near_passers = [(s,e) for s,e in near_passers
                        if e['passes_self_play'] and e['ac_exploitation'] <= 0.1]
        near_passers.sort(key=lambda x: x[1]['payoff_gap'])
        print(f"  Best 5 by payoff_gap among self-play + ac-test passers:")
        for s, ev in near_passers[:5]:
            print(f"    self={ev['self_play']:.3f}  gap={ev['payoff_gap']:+.3f}  "
                  f"ac_exploit={ev['ac_exploitation']:+.3f}")

    result = {
        'named': named_results,
        'sample_size': n,
        'passers_count': len(passers),
        'passers_rate': round(len(passers)/n, 4),
        'criteria': {
            'self_play_threshold': 2.5,
            'fairness_threshold': 0.0,
            'ac_exploitation_threshold': 0.1,
        },
        'top_passers': [
            {'params': list(s), 'eval': ev}
            for s, ev in passers[:10]
        ]
    }
    out = '/tmp/rev0028/artifacts/reports/universalization_frontier_snapshot.json'
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\nResult written to {out}")
