# rev0013 code-policy oracles

rev0013 adds a small **readable code-policy** interface.

The purpose is not to execute arbitrary code from strangers. The purpose is to make a future Code-Space Response Oracle style loop possible inside the cloudtainer:

```text
public DecisionFrame
  -> readable Python scoring function
  -> legal action index
  -> promotion-gated payoff table
  -> replay samples
```

## New files

```text
src/muc5/code_policy.py
src/muc5/public_payoff.py
scripts/run_rev0013_code_policy_payoff.py
tests/test_rev0013_code_policy_gap.py
```

## Built-in code policies

```text
code_jace_lock_rev0013
  Resolve/protect Jace; prioritize Jace ultimate and Jace defense.

code_overlord_clock_rev0013
  Deploy Overlord pressure and convert life totals into a clock.

code_force_conservative_rev0013
  Use Force sparingly; prefer Counterspell and protect life/cards.
```

Each policy is a human-readable score function over:

```text
observation: Mapping[str, object]
action: Action
```

The agent wrapper receives only a `DecisionFrame`. It does not receive `GameState`, opponent hand, opponent library, or hidden pending-choice data.

## Generated rev0013 table

```text
data/rev0013_code_policy_payoff_games.csv
data/rev0013_code_policy_payoff_aggregate.csv
data/rev0013_code_policy_payoff_standings.csv
data/rev0013_code_policy_lint.csv
data/rev0013_code_policy_replay_traces.jsonl
data/rev0013_code_policy_replay_results.json
data/rev0013_code_policy_payoff_summary.json
```

Smoke dimensions:

```text
6 strategy bundles
20 and 40 life
both starting-player settings
144 public DecisionFrame games
6 deterministic replay samples
```

The promotion gate passed, with a truncation warning. The warning is expected and useful: truncation can be reported as draw-half, but should not be silently used as training reward.

## Safety boundary

This is not a security sandbox. A Python policy inside the archive can still do Python things. The MUC-5 method boundary is instead:

```text
promotion/tournament code must pass DecisionFrame, not GameState
policy code must return an action index into the provided legal list
promotion rows must record interface, reward convention, truncation, and simulator revision
sample games must replay
```

Future sandpeople can add new readable policies by adding a score function and catalog entry in `src/muc5/code_policy.py`. If arbitrary file loading is added later, it should be quarantined behind stricter import rules and never bypass `DecisionFrame`.
