# rev0025 refactor/audit notes

## Refactor

The main new seam is:

```text
src/muc5/outcome_training.py
```

It separates terminal-outcome row collection from generic imitation collection.  That keeps the old imitation dataset stable while adding a new outcome-weighted training surface.

Other touched seams:

```text
src/muc5/ranker_policy.py      outcome-ranker default model loaders
src/muc5/public_agents.py      public factory names for outcome rankers
src/muc5/strategy_sets.py      rev0025 outcome-ranker evaluation panel
scripts/audit_cube.py          rev0025 audit checks
```

## Audit focus

rev0025 audit checks that:

```text
outcome ranker model exists
outcome training dataset exists and has terminal labels
truncation rows carry zero positive training signal
outcome payoff table passed promotion/statistical gates
C++ trace summary has zero skipped events and mismatches
new docs/scripts/tests are present
```

## Known limitation

This is weighted behavior cloning, not RL.  It cannot discover the value of unchosen legal alternatives.  Its role is to bridge from imitation toward outcome-aware policy improvement while keeping all gates intact.
