# rev0011 Reward Guard

## Problem

The simulator is about to become an optimization target.  Once agents optimize, every accidental proxy becomes an opportunity for specification gaming.

The cleanest immediate trap is:

```text
max_decisions reached
  -> scorer gives both players 0.5
  -> losing agent learns to stall
```

That is not a theoretical nit.  MUC-5 has Jace, long counter wars, 40/60-card decking pressure, and 20/40-life modes.  Long games can be legitimate, but truncation cannot silently become a training reward.

## New rule

rev0011 separates:

```text
terminal_win / terminal_loss
nonterminal draw
truncation
reporting score under draw-half convention
terminal-only training score
```

Implemented in:

```text
src/muc5/reward_guard.py
scripts/audit_reward_guard_rev0011.py
```

## Training recommendation

For early learning:

```text
terminal win:  1.0
terminal loss: 0.0
truncation:    no terminal-only label
```

For reporting:

```text
win/loss/draw-half can be shown, but must be labeled.
```

For adversarial diagnostics:

```text
track truncation rate
track decision count
track pass ratio later
track repeated no-progress loops later
track whether a strategy's score improves when max_decisions decreases/increases
```

## Reward-hack watchlist

1. **Stall hacking**: draw-half scoring makes losing positions worth stalling.
2. **Short-game hacking**: if speed becomes reward, agents may choose reckless lines that terminate fast.
3. **Hidden-state leakage**: trusted-state baselines are upper-bound/debug tools, not fair learned agents.
4. **Constructor leakage**: known vs unknown life/decklist/opponent-pool contexts must be tagged.
5. **Mulligan leakage**: opening-hand decisions must not see future draws.
6. **Action-list leakage**: legal action menus may reveal information only if the real player could infer it from public rules and private own hand.
7. **Truncation horizon overfit**: a policy can learn the exact `max_decisions` boundary.

## Artifact summary

```text
data/rev0011_reward_guard_packets.csv
data/rev0011_reward_guard_summary.json
```
