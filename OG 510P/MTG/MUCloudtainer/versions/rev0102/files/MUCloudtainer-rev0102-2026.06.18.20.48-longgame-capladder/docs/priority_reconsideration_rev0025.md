# rev0025 priority reconsideration

The previous priority was outcome-weighted gameplay policy improvement.  That is now built as a first conservative version.

## Revised priority

```text
1. C++ batch rollout sketch under Python fingerprint gates.
2. Learned mulligan improvement from actual terminal game outcomes.
3. Larger MAP-Elites races including outcome-weighted and learned-mulligan policies.
4. Meta-rank over denser promoted, nontruncated payoff tables.
5. Policy-improvement loops that use outcome labels or search targets, not imitation alone.
```

## Why not jump straight to PPO/CFR?

The current outcome ranker already shows the main danger: labels and reward conventions matter more than model class.  Before heavier learning, the cube needs a clean path for outcome datasets, replayable games, and C++-checked traffic.

## What would count as progress next?

A useful next revision would run a larger sequential race where outcome-ranker variants, MLP variants, code policies, and MAP-Elites decks are evaluated under the same learned-mulligan and promotion gates.  The C++ batch-rollout sketch should remain a parity tool first, not an authority switch.
