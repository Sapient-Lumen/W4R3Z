# rev0012 experiment matrix additions

New experimental axes now explicitly represented or planned:

```text
interface:
  trusted_state_debug
  public_decision_frame

promotion level:
  smoke
  beta
  claim

strategy bundle:
  deck
  mulligan policy/agent
  pilot/controller

oracle source:
  seed strategy
  static prior
  local mutation
  random plausible
  code policy
  learned policy

reward convention:
  draw_half_reporting_terminal_only_training
  terminal_only
  explicit_truncation_penalty
```

Immediate next matrix worth running after rev0012:

```text
public payoff table
  strategies: seed bundles + oracle candidates
  life: 20, 40
  start player: both
  reps: 8+
  replay sample: 5-10%
  promotion gate: beta
```

The current rev0012 tables are smoke-scale only.
