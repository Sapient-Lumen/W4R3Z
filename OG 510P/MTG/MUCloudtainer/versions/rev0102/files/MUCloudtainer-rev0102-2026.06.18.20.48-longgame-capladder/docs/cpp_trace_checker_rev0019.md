# rev0019 C++ trace checker

rev0019 adds a bridge between the Python replay lab and the C++ transition microkernel.

The contract is deliberately conservative:

```text
Python records public DecisionFrame trace
Python replays authoritative state
for each recorded action:
  if C++ microkernel supports the action:
    project pre-state + action into flat TransitionMicroRecord
    run C++ one-action transition
    compare C++ SIGv2 to Python post-action SIGv2
  else:
    record explicit coverage debt
```

This is **not** a full C++ simulator. It is a batch differential checker over real recorded public-agent games. Python remains the semantic authority until C++ has enough transition coverage and replay confidence to justify a full rollout core.

## Why this matters

Earlier C++ checks tested sampled one-action states. That is good, but it does not prove that C++ can follow realistic recorded game traffic end-to-end. rev0019 checks C++ against entire public traces, while preserving the hidden-information boundary: traces are generated from public DecisionFrames, not omniscient agent state.

## Current result

The rev0019 trace check generated 30 public traces:

```text
8,153 recorded public decisions
8,149 supported C++ transition checks
4 unsupported events
0 C++ mismatches
0 Python replay errors
support rate: about 99.95%
```

The unsupported events were all Jace ultimate activations. This is intentional for now. Jace ultimate includes a shuffle, so it should remain outside the C++ transition kernel until RNG/shuffle transport is made explicit.

## New artifacts

```text
src/muc5/cpp_trace.py
scripts/run_rev0019_cpp_trace_check.py
tests/test_rev0019_cpptrace.py

data/rev0019_public_traces.jsonl
data/rev0019_cpp_trace_rows.csv
data/rev0019_cpp_trace_summary.json
```

## C++ cutover rule

C++ can be trusted only through gates, not vibes:

```text
1. Python reference implementation exists.
2. C++ implements one stable seam.
3. Python projects states/actions into a flat transport.
4. C++ output matches Python on directed cases.
5. C++ output matches Python on sampled gameplay cases.
6. C++ output matches Python across recorded public traces.
7. Unsupported coverage debt is explicit and small.
8. Only then may that seam be used in bulk evaluation.
```

rev0019 reaches step 6 for the currently supported transition subset.
