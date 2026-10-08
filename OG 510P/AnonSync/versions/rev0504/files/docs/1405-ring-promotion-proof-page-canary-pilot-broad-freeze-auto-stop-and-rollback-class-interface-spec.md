# Ring-promotion proof page: canary, pilot, broad, freeze, auto-stop, and rollback class interface spec

## Purpose

The rollout contract sheet says how a rollout is structured.
This page proves *why* promotion from one ring to the next is allowed, blocked, frozen, or rolled back.

## Core decision

AnonSync must require a **Ring-promotion proof** whenever a user or automation tries to:

- advance from canary to pilot
- advance from pilot to broad
- thaw a frozen rollout
- keep a rollout broad despite newly armed stop conditions
- trigger or cancel rollback

## Proof layout

1. **Promotion headline**
2. **Input ring evidence**
3. **Gate and stop proof stack**
4. **Outcome verdict**
5. **Blocked stronger sentence**

### 1) Promotion headline

Show:

- from ring
- to ring
- current verdict
- strongest safe sentence
- blocked stronger sentence
- proof freshness

Supported verdicts:

- `promotion-allowed`
- `promotion-allowed-with-holdbacks`
- `freeze-required`
- `rollback-required`
- `manual-review-required`
- `unknown`

### 2) Input ring evidence

The proof must summarize what happened in the source ring:

- ring population
- completed activations
- cold-apply completions
- continuity-preserving moves
- world-fork moves
- newly created waivers
- newly armed stop conditions
- evidence freshness

The operator must be able to answer:

> what actually happened in the smaller ring, not just whether we wish it had gone well?

### 3) Gate and stop proof stack

Supported proof rows must include:

- `all required gates passed`
- `gates passed only for subset`
- `no new governing blocker`
- `no mixed-major linked risk introduced`
- `cold-apply complete where required`
- `rollback path still valid`
- `feature claim remains truthful at next ring`
- `unknown evidence remains below threshold`

Each row must show:

- proof verdict
- governing evidence
- affected subjects
- impact on promotion

### 4) Outcome verdict

Supported outcomes:

- `promote whole next ring`
- `promote partial next ring`
- `freeze at current ring`
- `rollback current ring`
- `reclassify some subjects to holdback`
- `require more evidence`

Each outcome must show:

- exact moved subject count
- exact held-back subject count
- exact rollback subject count
- rollback class if relevant
- next review trigger

### 5) Blocked stronger sentence

Examples:

- `Pilot promotion is safe for all remaining subjects` blocked because one service branch still requires clean install.
- `Broad rollout preserves continuity` blocked because some subjects moved via rebind into another world.
- `This successor is now the live default` blocked because holdback and rollback cohorts still exist.

## Hard rules

- a promotion proof must use observed ring outcomes, not only planned intent
- newly armed stop conditions must be printed even when the immediate outcome is only a freeze
- partial promotion must remain explicit and count-based
- rollback class must stay attached to the outcome, not buried in notes
- `promote broad` must never be available when the truthful result is only `promote subset`
