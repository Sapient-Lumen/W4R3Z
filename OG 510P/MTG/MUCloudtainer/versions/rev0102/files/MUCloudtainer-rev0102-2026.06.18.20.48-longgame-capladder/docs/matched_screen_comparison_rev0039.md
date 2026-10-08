# rev0039 matched screen comparison

rev0039 tests a label-selection question rather than promoting a new player:

```text
same public DecisionFrame
same hidden true referee state, used only by the offline labeler
same branch rollout outcomes
  ↓
unscreened budget selector
vs.
disagreement-screened vote-budget selector
```

The disagreement screen is useful only if it helps spend branch rollouts on legal actions that matter.  rev0038 showed that public-policy vote disagreement finds more interesting frames.  rev0039 asks a stricter question: when the unscreened selector and screened selector are applied to the same positions, does vote priority actually keep better candidate actions?

## Methods compared

`unscreened_budget` uses the older behavior-chosen plus diversity budget selector.  It does not care which public policies voted for which legal action.

`screened_vote_budget` still keeps the behavior action, but it gives priority to actions chosen by public-safe screening policies before filling the remaining budget with diversity representatives.

Both methods are compared against the union of branched actions.  This is not the full legal menu when the menu is large; it is the best action within the audited union.

## Important boundary

Screeners receive only:

```text
DecisionFrame.observation
DecisionFrame.legal_actions
```

They do not see opponent hand, hidden library order, or branch outcomes.  Hidden state is used only by the offline referee to build matched counterfactual branches from an identical state.

## Why this matters

Action-counterfactual data is expensive.  We should not spend rollout budget merely to produce more rows.  We want rows where the label can teach a future policy something about an unchosen legal alternative.

rev0039 found that a very tight vote-prioritized budget can sometimes drop a useful diversity action.  That is a useful negative result: disagreement screening is good for finding frames, but vote priority alone should not become the whole branch selector.
