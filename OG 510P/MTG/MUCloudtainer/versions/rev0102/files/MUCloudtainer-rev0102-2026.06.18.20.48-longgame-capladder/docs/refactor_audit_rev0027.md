# rev0027 refactor/audit notes

## Refactor

The main refactor is in `public_payoff.py`:

```text
old:
  cache gameplay agents
  rebuild mulligan agents per game

new:
  cache gameplay agents
  cache mulligan agents
  pass cached mulligan agents into play_public_strategy_pair_row
```

This matters because learned mulligan policies are JSON-backed and should not reload from disk once per payoff row.

## New audited surface

rev0027 adds:

```text
src/muc5/mulligan_outcome_training.py
scripts/run_rev0027_mulligan_outcome_ranker.py
tests/test_rev0027_mulligan_outcome.py
```

The audit checks:

```text
outcome mulligan model JSON exists
model feature count matches the public mulligan feature interface
factory can load mulligan_outcome_ranker_rev0027
training collection has terminal games and no truncation-weight leakage
payoff table has 900 rows
promotion gate passes
statistical gate passes
replay samples pass
C++ trace samples have zero skipped events and zero mismatches
required rev0027 docs/scripts/tests exist
```

## Caveat

The model is outcome-weighted behavior cloning.  It can favor mulligan choices seen in winning games, but it still cannot assign true counterfactual value to unchosen choices from the same opening hand.
