# rev0042 label-racing audit seam

`src/muc5/action_race_audit.py` is a pure label-budget module.  It does not run games and does not expose hidden state to agents.

Input:

```text
branch rollout rows
  situation_id
  action_index
  rollout
  actor_score
```

Output:

```text
rev0042_hard_racing_label_methods.csv
rev0042_hard_racing_label_pivot.csv
rev0042_hard_racing_summary.json
```

Compared methods:

```text
fixed_equal_3
  consumes three rollout samples per candidate action

adaptive_race_prefix
  consumes one rollout sample per candidate action
  spends extra budget on current top contenders
  stops early if best-minus-second margin is large enough
```

The module deliberately uses only prefix samples per action.  This avoids a subtle offline-labeling cheat where the labeler would look at all rollouts and then pretend it saved work.

## Audit constraints

A valid rev0042 label audit should satisfy:

```text
race_situations == selected_hard_situations
label-method rows == 2 * race_situations
adaptive_rollout_savings > 0
0 <= best_set_agreement_rate <= 1
branch_truncations == 0
```

The result should not be read as policy strength.  It is about label density and rollout allocation.
