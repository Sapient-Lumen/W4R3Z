# rev0055 life-cell claim results

rev0055 produced a cleaner split of the rev0054 life-sensitive matchup dossier.

## Fresh rev0055 evidence

```text
life 20:
  games: 128
  mean score: 0.65625
  score LCB 95: 0.53621
  label: positive_life_cell_watch

life 40:
  games: 128
  mean score: 0.77344
  score LCB 95: 0.65340
  label: positive_life_cell_watch
```

The fresh run has zero truncations and clean C++ transition shadow checks.

## Cumulative rev0054 + rev0055 evidence

```text
life 20:
  games: 208
  mean score: 0.63462
  score LCB 95: 0.54045
  label: life_cell_claim_candidate

life 40:
  games: 208
  mean score: 0.78365
  score LCB 95: 0.68949
  label: life_cell_claim_candidate
```

This upgrades the matchup from an averaged life-sensitive candidate into two separate life-cell candidates.  The life-40 cell remains much stronger, but life 20 no longer looks merely uncertain after cumulative evidence.

## Interpretation

The current best wording is:

```text
cf34_counter_wall appears favored against pub_threat_overlord at both 20 and 40 life under the current terminal-clean, public-agent, C++-shadowed dossier protocol; the advantage is larger at 40 life.
```

This is still not a final theorem.  It is the first matchup where both life cells now have their own dossier-quality evidence.
