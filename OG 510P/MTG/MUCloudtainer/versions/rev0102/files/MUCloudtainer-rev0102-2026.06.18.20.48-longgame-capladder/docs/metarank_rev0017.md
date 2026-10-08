# rev0017 meta-rank adapter

rev0017 adds `src/muc5/metarank.py`, a small payoff-table ranking adapter inspired by Alpha-Rank-style population analysis.

It is not a full OpenSpiel Alpha-Rank implementation. It is a cloudtainer-friendly tool for asking a better question than raw average score:

> If strategies can replace each other based on pairwise performance, where does stationary population mass concentrate?

## Input

The adapter consumes aggregate payoff rows with:

```text
strategy0
strategy1
starting_life
p0_mean_score_draw_half
games
```

`matrix[i, j]` is the expected score of strategy `i` as player 0 against strategy `j` as player 1.

## Replacement dynamic

For resident strategy `i` and challenger `j`, the adapter compares:

```text
challenger payoff: matrix[j, i]
resident payoff:   matrix[i, j]
```

A logistic replacement weight increases when `j` does better against `i` than `i` does against `j`. A tiny mutation floor keeps the Markov chain ergodic for smoke tables with ties.

## Outputs

rev0017 writes:

```text
data/rev0017_metarank_all.csv
data/rev0017_metarank_life20.csv
data/rev0017_metarank_life40.csv
data/rev0017_metarank_rank_disagreement.csv
```

This lets us compare:

```text
statistical-standings rank by lower confidence bound
vs.
meta-rank stationary mass
```

A disagreement can be interesting: it may indicate cycles, specialization, or just small-sample noise. The stat gate and promotion gate still decide what can be claimed.
