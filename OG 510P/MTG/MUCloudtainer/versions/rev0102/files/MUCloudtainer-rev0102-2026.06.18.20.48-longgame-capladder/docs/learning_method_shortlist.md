# Learning Method Shortlist — historical note

This file was the rev0002 method sketch. Its four families were directionally correct, but its implementation order is superseded by `docs/CURRENT_METHODS.md`.

The important reinterpretation is:

```text
PSRO / double-oracle outer loop
    ├── numerical/enumerative controls
    ├── evolutionary / MAP-Elites response oracle
    ├── neural response oracle
    └── CFR/search calibration oracle
```

Historical branch names and their original questions are retained below for provenance.

## 1. Enumerative/probe baseline

Because all raw deck vectors can be enumerated, enumeration is the construction baseline. Before strategy exists, decks can be screened by exact probability probes. After simulation is fast enough, selected decks can be evaluated in matchups.

Original question: can cheap statistics already identify strong constructions?

## 2. Evolutionary constructor and pilot

Evolution remains attractive because deck vectors are discrete, mutation/crossover are natural, and evolved pilot weights can be interpretable.

Original question: can a population discover construction/pilot niches faster than enumeration?

## 3. Masked neural policy/value pilot

The simulator emits a hidden-information-safe decision frame and legal action list. rev0091 adds durable information state; rev0092 adds episode-safe recurrent policy lifecycle.

Original question: can a small policy learn Force/Jace/Overlord timing from self-play logs?

## 4. Imperfect-information search / CFR-like methods

MUC-5 has private hands and libraries. It is an imperfect-information game, not a perfect-information AlphaZero clone.

Original candidates included determinized MCTS, information-set MCTS, CFR/Deep CFR, and later value/search hybrids.

Original question: can belief-aware methods exploit hidden-information structure better than direct policy learning?

## Current ordering

See `docs/CURRENT_METHODS.md`. The active order is gameplay-driven response oracle, reduced CFR calibration, neural response oracle, then repeated population expansion under common confirmation rules.
