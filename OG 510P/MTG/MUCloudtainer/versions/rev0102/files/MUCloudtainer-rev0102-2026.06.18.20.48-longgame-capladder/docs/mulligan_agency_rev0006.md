# rev0006 — Mulligan agency

rev0005 added a London-mulligan scaffold. rev0006 promotes it to an agent-facing decision seam.

The long-term goal is not to hand-code opening-hand theory. The goal is:

```text
pregame observation
  ↓
legal mulligan/bottom actions
  ↓
agent chooses
  ↓
engine applies
```

This is the same referee/ML separation used during gameplay.

## Why this matters

Mulligans are not just a convenience rule in MUC-5. They interact with every construction dial:

```text
40 vs 60 cards
Island density
Force of Will pitch density
Jace/Overlord threat density
20 vs 40 starting life
known vs unknown tournament context
```

A constructor that expects good mulligan discipline may build differently from a constructor paired with a bad keep policy. A pilot that knows it can bottom redundant expensive cards may tolerate greedier opening distributions.

## Current action grammar

```text
MULLIGAN_KEEP
MULLIGAN_TAKE
MULLIGAN_BOTTOM(card)
```

`MULLIGAN_BOTTOM(card)` is emitted once per bottom-card choice after a player keeps. This is intentionally one card at a time so a future learned agent can learn bottom ordering and redundancy valuations.

## Observation

`MulliganObservation` currently exposes:

```text
player
stage = keep_or_mulligan | bottom
mulligans_taken
hand counts by card
hand_size
library_count
bottom_remaining
```

It does not expose the opponent's hand or library order.

## Baseline agents

The baseline `RuleMulliganAgent` wraps the existing deterministic policies:

```text
keep_always
land_band
land_band_business
```

These policies are intentionally weak. They exist to create stable regression data and a minimum baseline for future learned mulligan agents.

## Current results

`data/rev0006_mulligan_agency_probe_summary.json` summarizes 18,000 opening-hand samples and 20,700 explicit pregame decision events.

Policy-level summary:

```text
keep_always:          p(any mulligan)=0.000000, avg kept size=7.000000
land_band:            p(any mulligan)=0.099500, avg kept size=6.891667
land_band_business:   p(any mulligan)=0.106667, avg kept size=6.883333
```

The exact numbers are not strategic conclusions. They are regression targets and sanity checks.

## Future learned versions

Good next versions:

```text
contextual bandit mulligan policy
supervised imitation of a hand-scoring oracle
small policy network over keep/take/bottom actions
constructor-conditioned mulligan policy
PSRO population where opening-hand policies are part of the strategy identity
```

The important design rule: learned mulligan agents should use the same legal-action seam as rule agents. Do not special-case a neural agent with hidden access to deck order or opponent hand.
