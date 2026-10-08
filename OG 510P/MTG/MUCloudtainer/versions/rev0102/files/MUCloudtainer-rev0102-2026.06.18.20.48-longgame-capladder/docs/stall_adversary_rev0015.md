# rev0015 stall adversary and reward/truncation gate

rev0015 adds an intentionally hostile public policy profile:

```text
public_stall_rev0015 / stall / turtle / draw_adversary
```

It is not meant to be good Magic. It is meant to probe whether our scoring and promotion gates can be tricked by behavior that avoids losing rather than wins.

## Behavior

The stall policy:

```text
plays Islands
passes in main phases
refuses to cast Jace or Overlord proactively
counters public Jace/Overlord threats when possible
blocks to prolong the game
discards proactive threats before counters/lands
avoids Jace ultimate if it somehow has Jace
```

This intentionally attacks the draw-half reporting convention. If a losing or non-winning policy can force `max_decisions_reached`, then a raw 0.5 draw score can become a reward hack.

## Diagnostic result

The script:

```bash
python scripts/run_rev0015_stall_adversary.py
```

generated:

```text
data/rev0015_stall_adversary_games.csv
data/rev0015_stall_adversary_aggregate.csv
data/rev0015_stall_adversary_standings.csv
data/rev0015_stall_adversary_pairwise.csv
data/rev0015_stall_adversary_summary.json
```

The strict promotion gate is expected to fail when truncations occur. That is the point. The result is an adversarial diagnostic table, not a promotable strategic payoff table.

## Rule for later learning

Training reward should remain terminal-only unless a method explicitly declares how it treats truncations. Draw-half score is useful for reporting, not as an unqualified training signal.
