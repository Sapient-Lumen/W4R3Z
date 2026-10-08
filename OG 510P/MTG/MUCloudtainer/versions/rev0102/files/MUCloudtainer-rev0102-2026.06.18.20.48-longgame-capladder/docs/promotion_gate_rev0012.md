# rev0012 promotion gate

A payoff table is not a promotion table until it passes a provenance/reward/replay gate.

The current promotion gate asks a small but important set of questions:

```text
Did every row record simulator_revision?
Did every row record the public/omniscient interface?
Did every row record reward_convention?
Did every row expose truncation status?
Do p0_score and p1_score sum to 1?
Are terminal win columns separated from draw-half reporting score?
Is truncation rate below the gate threshold?
Did a replay sample pass?
```

This is partly a reward-hacking defense and partly a future-sandperson defense. If a future revision opens the archive and sees a strategy promoted, they should be able to answer: which simulator produced it, what the agent was allowed to observe, how draws/truncations were scored, and whether sample games were replayable.

## New files

```text
src/muc5/promotion.py
scripts/run_rev0012_public_payoff_promotion.py
data/rev0012_public_payoff_games.csv
data/rev0012_public_payoff_aggregate.csv
data/rev0012_public_payoff_standings.csv
data/rev0012_public_payoff_replay_traces.jsonl
data/rev0012_public_payoff_replay_results.json
data/rev0012_public_payoff_summary.json
```

## Gate result in this revision

The rev0012 public payoff smoke table ran:

```text
9 strategy bundles
20 and 40 starting life
both starting-player settings
324 games
6 replay samples
```

The promotion gate passed for this smoke table. It did emit a warning because a small number of games hit max-decisions truncation. That warning is intentional: draw-half is allowed for reporting, but truncation should not silently become a training target.

## What this is not

This is not a statistical confidence system yet. It does not prove a strategy is strong. It proves that a set of rows is sufficiently labelled and replay-sampled that we are allowed to start discussing them.

Next likely upgrades:

```text
confidence intervals for row means
minimum games per matchup cell
promotion gate separates smoke / beta / claim levels
cross-seed replay sample
stall-progress diagnostics
```
