# Simulator status through rev0027

The simulator remains a working automated beta for MUC-5:

```text
five-card card pool
40/60 card construction
20/40 starting life
London mulligans
public DecisionFrame gameplay
promotion/statistical/replay gates
batched C++ trace parity checks
```

rev0027 does not change core card rules.  It changes how the tournament layer treats learned mulligan agents and how outcome data is collected from pregame choices.

## Simulator trust status

```text
automated play:       green
learning-loop beta:   green/yellow
strategic claims:     still yellow
```

The game engine can support learned/evolved experiments, but strategic claims still need promoted, nontruncated, replayable, statistically labeled payoff tables.

## New learned pregame policy

```text
mulligan_outcome_ranker_rev0027
```

This agent is accepted by the same `make_mulligan_agent(...)` factory used by replay and payoff scripts.

## No C++ authority change

C++ remains a shadow/parity layer.  rev0027 confirms that the new learned-mulligan traffic can still pass C++ trace checks, but does not promote C++ to semantic authority.
