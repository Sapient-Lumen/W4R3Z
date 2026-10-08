# rev0006 refactor/audit

## Refactor performed

`src/muc5/mulligan.py` was refactored from a deterministic helper into a small pregame action system.

New names:

```text
MulliganObservation
MulliganAgent
RuleMulliganAgent
MULLIGAN_KEEP
MULLIGAN_TAKE
MULLIGAN_BOTTOM(card)
legal_mulligan_actions
legal_bottom_actions
london_mulligan_agent_opening_hand
```

`engine.py`, `env.py`, and `agents.py` were updated to pass `mulligan_agents` through without breaking existing `mulligan_policy` usage.

## Tests added

```text
tests/test_rev0006_mulligan_agency.py
```

Coverage includes:

```text
explicit keep/take legal actions
card-specific bottom actions
rule-agent event logs
start_game(mulligan_agents=...)
MUC5SlotEnv(..., mulligan_agents=...)
```

## Data audits added

```text
rev0006_mulligan_agency_probe
rev0006_mulligan_life_arena
rev0006_audit
```

The cube audit now checks row counts, summary counts, and that a `MUC5SlotEnv` game started with `mulligan_agents` produces nonempty `mulligan_decision_log` while preserving card conservation.

## Current validation

```text
31 passed
rev0006 audit passed
zip integrity test passed
```

## Remaining risks

The mulligan policies are still crude. They do not know matchup, deck identity beyond the current hand, play/draw, life total, opponent deck size, or opponent public mulligans. Future learned versions should condition on those where available.
