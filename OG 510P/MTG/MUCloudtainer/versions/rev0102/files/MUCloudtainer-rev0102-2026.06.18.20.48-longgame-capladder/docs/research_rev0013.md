# rev0013 research notes: fabulous things to test at this scale

The research direction has shifted from “train a big agent” to “make small strategy objects compete safely.” That fits MUC-5 unusually well because a strategy can be a bundle:

```text
deck construction + mulligan policy + pilot/controller
```

## 1. Code-Space Response Oracles

Code-Space Response Oracles reframe response-oracle generation as policy-code generation rather than opaque neural policy training. MUC-5 is a good tiny target because policies can be short Python score functions over `DecisionFrame`.

Near-term test:

```text
Can a readable code policy beat baseline public agents while still passing promotion/replay gates?
```

rev0013 implements the first non-LLM version by hand:

```text
code_jace_lock_rev0013
code_overlord_clock_rev0013
code_force_conservative_rev0013
```

## 2. Code World Models

Code World Models are interesting in the opposite direction: generate or distill executable environment code with legal actions, state transitions, and observations. For MUC-5, this is mostly a **test harness idea**, not a replacement for our engine.

Possible tiny experiment:

```text
Ask future code policies to predict next public observation after an action.
Compare predicted transition snippets against the referee replay trace.
```

This could become a “world-model-of-MUC-5” benchmark without letting generated code become the authoritative referee.

## 3. PSRO / empirical games

PSRO remains a strong population shape:

```text
start with strategy population
build payoff table
analyze meta-strategy
add approximate best response
repeat
```

MUC-5 can make the response oracle one of:

```text
mutation/evolution deck oracle
readable code-policy oracle
small neural policy oracle
search/determinization oracle
```

## 4. Alpha-Rank / intransitivity

Mean score may hide cycles:

```text
Jace-lock beats force-conservative
force-conservative beats Overlord-clock
Overlord-clock beats Jace-lock
```

Once payoff tables have higher reps, Alpha-Rank-style analysis can test whether the population has stable dominance or rock-paper-scissors structure.

## 5. MAP-Elites / quality diversity

A single best deck is less interesting than a map of good decks across descriptors:

```text
deck size: 40 / 60
land fraction
Force fraction
Jace fraction
Overlord fraction
mulligan aggressiveness
pilot style
20-life score
40-life score
```

A tiny MAP-Elites archive could preserve weird viable niches instead of collapsing to one champion.

## 6. ReBeL / public belief state and Deep CFR

ReBeL and Deep CFR are still later-stage. MUC-5 has hidden hands/libraries, so belief-state and regret ideas are relevant. But they should wait until:

```text
simulator beta gate passes
payoff statistics include confidence intervals
public observation/action encoders are stable
replay traces are attached to promoted surprises
```

## New questions worth asking

1. Does the best 20-life code policy become over-aggressive at 40 life?
2. Are 60-card Jace decks winning because of Jace strength or because 40-card decks self-mill under Overlord/Jace draw pressure?
3. Does Force of Will become worse when mulligan policies keep low-card hands?
4. Can a policy intentionally stall to improve draw-half reporting score, and can terminal-only reward stop it?
5. Are “known life” constructors brittle against unknown-life tournaments?
6. Does public-frame search outperform readable code policies enough to justify its complexity?
7. Can Alpha-Rank disagree with mean standings in the first 12-strategy population?
8. Can MAP-Elites find a land-light Force deck that is bad on average but crushes one common strategy?
9. Can an LLM-written policy enter the population without changing the referee or receiving hidden information?
10. Can we train a tiny value model only from replay traces and use it to explain policy mistakes?
