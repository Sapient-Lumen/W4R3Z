# rev0011 Simulator Status

## Status

```text
Automated beta simulator:      green
Learning-loop beta simulator:  yellow-green
Tournament-claim simulator:    yellow
```

rev0011 does not add many card rules.  It adds reproducibility and scoring guardrails, which are now more valuable than more features.

## What changed from rev0010

```text
+ deterministic replay trace layer
+ canonical state fingerprints
+ observation fingerprints
+ separated agent/transition RNG for trace-critical games
+ reward/truncation guard packet
+ question bank for next experiment priorities
```

## Why this matters

The simulator is becoming an optimization target.  Once agents learn, they will find simulator artifacts.  The answer is not to avoid learning; it is to make artifacts visible:

```text
state fingerprints
replay traces
explicit reward convention
truncation labels
construction context labels
```

## Next likely simulator builds

1. More directed rules scenarios: Jace +2 self/opponent, Jace zero putback order, Jace ultimate, combat into Jace, Force at low life.
2. Progress-loop diagnostics: detect repeated pass/no-change patterns before RL agents learn stalling.
3. Public-vs-omniscient benchmark: quantify hidden-information value.
4. Payoff-table promotion gate: reject rows without simulator revision, reward convention, and replay status.
