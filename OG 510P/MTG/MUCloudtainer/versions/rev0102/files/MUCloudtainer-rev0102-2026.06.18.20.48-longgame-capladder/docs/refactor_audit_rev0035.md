# rev0035 refactor / audit note

Main refactor:

```text
src/muc5/action_budget.py
```

This separates high-branch action selection from the counterfactual collector.
The collector now accepts optional arguments:

```python
sample_high_action_frames=True
branch_action_budget=6
budget_rng_seed=...
```

Existing callers keep old behavior by default.  With the default arguments,
high-action frames above `max_actions_per_frame` are still skipped.  rev0035's
script opts into budgeted high-action sampling.

Audit focus:

```text
budgeted high-action frames entered the label corpus
subset labels are marked explicitly
rev0035 public-agent aliases load the JSON model
budgeted payoff rows pass promotion/statistical/replay gates
budgeted branch and payoff traffic pass C++ shadow checks
```

The audit also retains the older card-conservation, hidden-observation, replay,
reward, C++ transition, C++ segment, ranker, mulligan, and payoff gates inherited
from earlier revisions.
