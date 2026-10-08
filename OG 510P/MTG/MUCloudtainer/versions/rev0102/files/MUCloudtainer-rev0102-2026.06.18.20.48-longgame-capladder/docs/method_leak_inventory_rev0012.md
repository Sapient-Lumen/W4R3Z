# rev0012 method leak and reward-hack inventory

This file lists ways learning methods can accidentally get advantages or optimize the wrong thing.

## 1. Omniscient state leak

Bad:

```text
agent receives GameState
agent can inspect opponent hand/library
```

Good:

```text
agent receives DecisionFrame only
```

Trusted-state agents remain useful for debugging, but public agents and future learning should use the DecisionFrame path.

## 2. Mask contains strategy instead of legality

The legal-action mask should exclude only actually illegal macro-actions. It must not hide legal-but-bad plays like tapping out or pitching an important card. Otherwise the referee teaches strategy instead of legality.

## 3. Truncation as reward

If `max_decisions_reached` gives `0.5`, a losing agent may learn to stall. rev0011/rev0012 therefore separate terminal wins, nonterminal draws, truncation flags, and draw-half reporting score.

## 4. Life-total construction leakage

Gameplay must know the actual life total. Construction experiments must label whether the constructor knew the life total before registration. A robust-unknown constructor should not silently receive the realized life setting.

## 5. Mulligan policy accidentally global

A strategy bundle is:

```text
deck + mulligan policy/agent + pilot/controller
```

Payoff scripts must allow seat-specific mulligan policies.

## 6. Dynamic action-index instability

A model trained on raw slot index may overfit menu order. Longer term, action featurization should describe action kind/card/target/mode in addition to its slot.

## 7. Seed/order overfit

Promotion tables should vary seeds, starting player, life total, and seat assignment. A future oracle must not be allowed to tune to one fixed seed schedule.

## 8. Deck-name leakage

A learned pilot may receive its own deck vector, but should not receive arbitrary deck names like `oracle_seed_02_threat_business` unless we intentionally test name-conditioned play.

## 9. Speed as hidden objective

Simulator throughput is a diagnostic. It must not appear in the reward unless we explicitly create a “fast-win” side objective.

## 10. Replay drift

A payoff table produced by one simulator revision should not be treated as equivalent after a rules change. Rows now carry `simulator_revision`; replay traces carry fingerprints.
