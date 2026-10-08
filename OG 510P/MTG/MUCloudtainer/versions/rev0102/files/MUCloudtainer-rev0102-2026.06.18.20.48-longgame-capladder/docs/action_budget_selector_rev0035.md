# rev0035 action-budget selector

`src/muc5/action_budget.py` is a small refactor seam for expensive
counterfactual rollouts.  It is not a gameplay policy and not a source of MUC
strategy.  It is an offline label-budget allocator.

Contract:

```text
DecisionFrame + chosen action index + budget + RNG
  -> original legal-action indices to branch
  -> reason label for every selected action
```

The selector is intentionally stable and semantic rather than smart.  It groups
actions by coarse diversity keys:

```text
PASS
PLAY_ISLAND
CAST(card/payment/pitch/mode)
ACTIVATE_JACE(mode/target)
ATTACK(shape)
BLOCK(shape)
CHOOSE_FOR_EFFECT(effect/card-ish payload)
```

Why this matters:

1. Full branch enumeration is clean but can ignore high-action frames when capped.
2. Random subset branching is cheap but may miss important action families.
3. A diverse budget makes high-action frames visible while keeping labels honest.

The selector always includes the behavior action.  That keeps regret-style rows
well-defined even when the rest of the menu is sampled.

The selector does not know hidden state beyond what the offline labeler already
has for branching, and it is not used by agents during tournament play.
