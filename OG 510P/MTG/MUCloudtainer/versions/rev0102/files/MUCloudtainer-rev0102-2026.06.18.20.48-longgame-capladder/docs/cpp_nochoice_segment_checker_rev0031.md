# rev0031 C++ no-choice segment checker

rev0030 recorded start/end fingerprints for forced-action runs. rev0031 makes that C++-checked.

A no-choice segment is a contiguous run of public `DecisionFrame`s where exactly one legal action exists. In the current MUC-5 traffic these are usually pass-only priority/resolution runs, cleanup/discard continuations, or forced choice continuations after a prior strategic decision. They are attractive for future acceleration because the agent is not doing policy work inside the run.

The new executable is:

```text
cpp/muc5_transition_segment.cpp
```

It includes the existing one-action transition microkernel and adds a grouping main:

```text
segment_id + TransitionMicroRecord action 1
segment_id + TransitionMicroRecord action 2
...
  ↓
C++ parses the first row's state
C++ applies the actions sequentially
C++ emits one final SIGv2 for the segment
```

Python remains the semantic reference. The segment checker is not yet a C++ tournament core; it is a parity harness that asks whether C++ can carry state across a forced run without drifting from Python.

rev0031 smoke result:

```text
games:                         48
decisions:                 10,620
segments:                   1,903
forced actions:             7,104
checked segments:           1,903
skipped C++ events:             0
C++ segment mismatches:         0
max segment length:            28
mean segment length:         3.73
all-pass segment rate:      98.9%
estimated compression:      ~1.98x
truncations:                   0
```

This is a stronger cutover step than per-action shadow checks because C++ is now responsible for multiple successive transitions from a single start state. The next C++ acceleration target should be a batch segment runner that the Python rollout loop can call for forced runs, guarded by pre/post SIGv2 fingerprints.
