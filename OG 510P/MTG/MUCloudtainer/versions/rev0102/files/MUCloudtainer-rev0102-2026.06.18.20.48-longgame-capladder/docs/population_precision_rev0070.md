# Population precision gate — rev0070

rev0070 converts the rev0069 population frontier from a one-rep pilot into a doubled, preregistered precision gate.

## Run shape

```text
counter policies: legacy_cf34_counter_ranker, public_counter_guard
threat policies:  library_aware_threat_closure_targetguarded, jace_pressure_threat_response, face_protect_threat_surge
size/life cells:  3 size axes × 2 life totals = 6 population cells
replication:      2 reps per seat/start-player combination
raw games:        288
min games/cell:   8 per counter-policy × threat-policy matrix entry
C++ shadowing:    30,000 evenly sampled supported transitions from 51,750 generated transitions
```

## Result

The population matrix stayed complete and operationally clean, but the precision gate rejected every cell:

```text
complete population cells: 6/6
terminal games:            288/288
truncations:               0
Python errors:             0
C++ mismatches:            0 / 30,000 sampled transitions
precision-gate passed:     0/6 cells
precision blocker:         confidence_interval_width_too_wide in all 6 cells
```

This is the right failure mode. rev0069 showed the matrix could be made complete. rev0070 shows that even a doubled run is not yet precise enough for strategic promotion. The lowest conservative lower-bound floors are still zero, and the widest observed confidence interval width is 0.9603.

## Interpretation

The main scientific outcome is negative but useful: **do not promote `public_counter_guard` as a security solution yet**. It remains the mean best pure row in the rev0070 run, but its conservative lower-bound floor is far below the promotion threshold. The next substantive route is either a much larger batched run or a faster simulator path; adding another named hand-written policy before that would repeat the response treadmill.
