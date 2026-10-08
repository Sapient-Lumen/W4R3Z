# rev0006 research notes — mulligans, action masks, imperfect information

## London mulligan as a real decision surface

The official London mulligan gives repeated seven-card looks, then requires a player who keeps after taking mulligans to put cards on the bottom of their library equal to the number of mulligans taken. That structure makes MUC-5 mulligans a natural two-stage decision problem: keep/take, then bottom-card selection.

For our purposes, this is not just a rules detail. It is an opening-hand policy problem that may change what deck construction is viable.

## Keep the action-mask seam

PettingZoo's action-masking tutorial frames masks as the natural way to prevent invalid moves in games where legal actions depend on state. MUC-5 now uses that idea in two places:

```text
gameplay: legal macro-actions
pregame: legal mulligan/bottom actions
```

This avoids wasting model capacity on impossible outputs.

## Imperfect-information roadmap

OpenSpiel remains a useful reference because it supports perfect and imperfect information games, turn-taking and simultaneous moves, and algorithms such as CFR, NFSP, PSRO, AlphaZero, and Alpha-Rank.

Near-term, MUC-5 should stay environment-first:

```text
1. stable legal-action referee
2. deterministic/random baselines
3. payoff tables
4. constructor/pilot population
5. action-masked policy learning
6. imperfect-information search/CFR branch
```

Deep CFR is relevant later because it replaces some manual abstraction with neural approximators for counterfactual regret minimization. ReBeL is relevant later because it combines deep RL and search for imperfect-information games. Both are too heavy for the immediate rev0006 implementation, but they help shape the API: observations must respect hidden information, and payoff tables/populations should be saved cleanly.

## PSRO/Alpha-Rank fit

PSRO is a strong future framework because a MUC-5 strategy is not just a policy; it can be a bundle:

```text
deck constructor
mulligan policy
pilot policy
life-context assumptions
```

A single champion can be brittle. A population/payoff-table view should preserve weird specialists: anti-Jace decks, Force-heavy tempo decks, 60-card decking decks, aggressive Overlord decks, and robust unknown-life constructors.

## Pushback retained

Mulligans matter, but avoid adding many mulligan-rule variants. The current cube should compare policies under one rule system: London mulligan. Otherwise deck size, life total, known/unknown construction, pilot policy, and mulligan rule multiply into too many noisy tournament contexts.
