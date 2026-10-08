# rev0014 research notes

The research priority shifted from “more agents” to “safer comparison.” The simulator is now good enough to run games, but not every game row should influence promotion.

## Statistical comparison before learning

Wilson intervals are a better small-sample binomial default than naive normal intervals. MUC-5 uses Wilson for terminal win rates. For draw-half scores, which are bounded rewards rather than pure Bernoulli wins, rev0014 uses a conservative Hoeffding interval.

Future option: add sequential tests. A sequential probability ratio test can terminate early when evidence is strong, which could matter once best-response search creates many candidate policies. For now, fixed-rep tables are simpler and more reproducible.

## Empirical game-theoretic analysis

MUC-5 is becoming an empirical game-theoretic analysis setup: a simulator produces noisy payoff samples, and we infer an empirical game over strategy bundles. That framing is cleaner than pretending a single mean win-rate table solves the metagame.

## Population analysis

Alpha-Rank remains a near-term target because OpenSpiel supports Alpha-Rank from payoff tables / heuristic payoff tables, and MUC-5 may have intransitive cycles.

PSRO remains the right later loop:

```text
population payoff table
  ↓
find response oracle
  ↓
add deck + mulligan + pilot bundle
  ↓
rerun selected payoff cells
```

## MAP-Elites / quality diversity

Quality-diversity search remains one of the most attractive “fabulous at small scale” directions. Unlike one-champion search, MAP-Elites illuminates a descriptor grid and keeps elites per cell. In MUC-5, that means we can preserve land-light Force decks, 60-card Jace shells, Overlord-clock shells, and robust unknown-life decks even before they are top overall.

## Rating systems later

Glicko and TrueSkill are worth remembering for bot-league presentation because they model uncertainty. They are not a replacement for payoff tables or Alpha-Rank, but they could make the gametable league legible to humans.

## Questions added in rev0014

1. Does lower-confidence-bound ranking change the apparent best strategy from raw mean ranking?
2. Which payoff cells stay uncertain even after 3 reps, and are they near true strategic boundaries?
3. Does the public-agent Force/block parameter fix materially alter standings?
4. Which MAP-Elites deck cells are not represented by current seed decks?
5. Can we pick one elite per cell and cheaply discover counterexamples to current code policies?
6. Should truncation be punished in training or only used as a table-exclusion criterion?
7. Can a future response oracle intentionally exploit Hoeffding/Wilson gates by forcing draws?
8. Does 40-life construction create distinct MAP-Elites cells or merely shift priors slightly?
