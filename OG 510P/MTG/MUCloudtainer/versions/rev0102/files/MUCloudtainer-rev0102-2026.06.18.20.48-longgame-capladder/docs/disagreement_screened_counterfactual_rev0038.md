# rev0038 — Disagreement-screened action counterfactuals

rev0038 changes the action-counterfactual sampler from "take the next manageable public frame" to "prefer frames where public-safe policies disagree."

The motivation is label quality.  Prior counterfactual revisions were often label-limited: many sampled frames were legal choices in name, but branch rollouts produced ties or near-ties.  A cheap way to spend budget more intelligently is to ask several public-safe policies what they would do from the same `DecisionFrame`.  If all of them choose the same slot, the frame is probably less informative.  If they split, the branch labeler has a better chance of seeing a real strategic fork.

The screening panel used in the smoke run:

```text
counter_happy
threat_rush
patient
code_jace_lock_rev0013
outcome_ranker_blend_counter_rev0025
```

The screeners receive only the public `DecisionFrame`:

```text
observation + legal_actions
```

They do not receive `GameState`, opponent hand, hidden library order, or branch outcomes.

## What is allowed to see hidden state?

Only the offline labeler/referee.  Once a public frame passes the disagreement screen, the collector copies the true simulator state and branches each selected legal action.  That hidden copy is not exposed to any agent; it is the same role the referee already plays when it adjudicates a game.

## What counts as a selected action?

Small menus are branched fully.  Larger menus use the existing budget selector, but rev0038 forces behavior-chosen and screen-voted actions into the selection priority before filling remaining diversity slots.

Rows now carry:

```text
screen_voted_action
screen_unique_votes
screen_vote_entropy_proxy
screen_vote_actions
budget_reason
branched_subset
```

Subset labels remain subset labels.  If a high-action menu is budgeted, `is_best_action` means best among the selected branch subset, not proof of full-menu optimality.

## Why this matters

The project is still not model-limited.  It is label-limited.  Better branch labels should come from better situation selection, not merely larger regressors.
