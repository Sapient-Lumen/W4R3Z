# rev0083 refactor audit

rev0083 adds a concrete counterprobe layer rather than another registry-only revision.

## Code changes

- `src/muc5/public_agents.py`
  - Adds `counter_life20_stabilizer`, a public-information-only profile targeted at the rev0082 deficient life-20 closure cell.
  - Registers aliases through `make_public_agent`.

- `src/muc5/population_counterprobe.py`
  - Adds narrow deficient-cell arm construction.
  - Adds seed-paired C++ rollout spec generation so legacy, guard, and repair policies face the same target-seat / starting-player / rep seed grid.
  - Adds compact rescue and policy-delta summarizers.

- `scripts/run_rev0083_deficient_cell_counterprobe.py`
  - Runs the targeted 192-game probe.
  - Writes compact game, summary, frontier, rescue, seed-balance, paired-outcome-delta, mechanism, and C++ sample artifacts.
  - Marks rows as targeted/adaptive and not broad-pool eligible.

## Risk removed

The previous rescue-envelope label could have been misread as “the current counter set is definitely too narrow.” rev0083 shows that the label was sensitive to small fine-cell sample size: a seed-paired 64-game-per-policy probe makes the same cell upper-bound-rescuable, but still not certified.

## Remaining risk

The run is targeted after observing the weak cell, so it cannot be pooled into broad promotion evidence. It is a triage/probe result only.
