# rev0009 Performance Notes

rev0008 showed that duplicate validation and logging have measurable cost. rev0009 keeps the speed work but routes it through a safer interface.

## New benchmark

```text
scripts/profile_decisionframe_rev0009.py
```

It writes:

```text
data/rev0009_decisionframe_profile_summary.json
```

It compares:

```text
trusted_state_agent_fastpath
trusted_state_agent_validated
public_decision_frame
```

The public DecisionFrame path is expected to be slightly slower than a trusted baseline in some runs because it allocates a frame object and observation packet. That overhead is acceptable: it blocks a much larger hidden-information mistake.

## Current optimization priorities

1. Keep logs off during bulk rollouts.
2. Avoid validating twice when action came from a legal DecisionFrame.
3. Avoid passing omniscient state to learned agents.
4. Reduce repeated observation dict construction after the interface stabilizes.
5. Consider compact integer/counted state encodings for neural policies.
6. Consider NumPy batch probability probes and vectorized deck filtering.
7. Consider Numba only after a stable measured hotspot dominates.

## Why not jump to Cython/Rust?

The archive must remain cloudtainer-operable. Cython may be present, but compiled extensions create portability and build-state problems for future archive openers. The project should earn that complexity by measurement.

EnvPool-style systems show how serious RL projects can become environment-throughput bound, but MUC-5 is still in the hundreds of games/sec range in pure Python. The right move now is to design fair fast-path seams before heavy learning uses them.
