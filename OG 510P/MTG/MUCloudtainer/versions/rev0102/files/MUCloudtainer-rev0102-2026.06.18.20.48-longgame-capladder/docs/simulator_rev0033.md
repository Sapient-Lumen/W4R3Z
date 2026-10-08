# simulator rev0033

rev0033 does not change Python engine semantics. It adds an offline branch-label generator over existing public `DecisionFrame`s and fixes one C++ parity bug.

The new branch path is:

```text
run normal public behavior game
  ↓
find a choice frame with manageable legal menu
  ↓
copy the true referee state
  ↓
for each legal action:
    apply that action in a branch
    roll out with public agents
    record actor outcome
  ↓
train/evaluate action rankers from branch values
```

This remains hidden-information-correct for agents because the true state is used only by the offline referee/labeler, never by the acting policy.

C++ shadow status:

```text
branch collection transitions: 19,342 checked, 0 skipped, 0 mismatches
payoff evaluation transitions: 39,000 checked, 0 skipped, 0 mismatches
```
