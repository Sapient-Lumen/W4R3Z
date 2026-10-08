# Claim card — cf34_counter_wall vs pub_threat_overlord — rev0057

## Claim scope

This is a MUC-5 local claim, not a general Magic claim.

```text
target:   cf34_counter_wall
opponent: pub_threat_overlord
source:   rev0056 seed-disjoint terminal-clean holdout
status:   replicated life-cell claim candidate, mechanism audited in rev0057
```

## Evidence inherited from rev0056

```text
holdout games: 192
life 20 holdout score: 0.78125
life 40 holdout score: 0.83333
C++ transition rows profiled: 54475
terminal-clean truncations: 0
```

## Mechanism found in rev0057

```text
target wins by opponent library-out: 151
target wins by opponent life-total loss: 4
target losses by target library-out: 26
target losses by target life-total loss: 11
```

## Interpretation

The replicated signal is best described as an endurance/library-out claim. The 40-life cell strengthens the target because extra life appears to reduce the target's life-loss failure mode while the opponent remains vulnerable to drawing out.

## Required before promotion or broad generalization

```text
same-deck pilot swap
same-pilot deck shell swap
40-vs-40 deck-size control
60-vs-60 deck-size control
Jace/Brainstorm draw-pressure ablation
mulligan-policy crossover
new seed-disjoint holdout after explanation
```

## Files

```text
data/rev0057_claim_mechanism_summary.json
data/rev0057_claim_mechanism_profile.csv
data/rev0057_claim_action_profile.csv
```
