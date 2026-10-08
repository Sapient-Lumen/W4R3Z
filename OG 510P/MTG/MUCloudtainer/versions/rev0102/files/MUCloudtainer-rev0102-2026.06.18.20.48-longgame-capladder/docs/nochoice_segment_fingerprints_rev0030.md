# rev0030 no-choice segment fingerprints

rev0029 measured forced-action runs. rev0030 records them as start/end fingerprinted segments so they can become a future C++ batching target.

A no-choice segment is a contiguous run of `DecisionFrame`s with exactly one legal action. The agent has no strategic choice during these frames, but previous loops still called the public agent each time. That is correct and simple, but it is not the long-haul high-throughput shape.

rev0030 emits rows like:

```text
game_id
segment_index
start_step
end_step
length
player_sequence
action_sequence
all_pass
start_frame
end_frame
start_fingerprint
end_fingerprint
```

Generated files:

```text
data/rev0030_nochoice_segment_games.csv
data/rev0030_nochoice_segment_fingerprints.csv
data/rev0030_nochoice_segment_fingerprint_summary.json
```

Smoke results:

```text
games:                              24
segments:                        1,086
total forced actions:             3,807
max segment length:                  26
mean segment length:              3.506
all-pass segment rate:            0.977
estimated compression ratio:      1.886
truncations:                         0
```

## C++ implication

The next safe C++ speed target is not a full tournament core. It is:

```text
Python start fingerprint
+ forced legal action sequence
  ↓
C++ applies segment
  ↓
C++ end SIGv2 must equal Python end fingerprint/signature
```

Only after segment parity is stable should no-choice segments be skipped or batched in live tournament loops.

## Fairness note

Skipping agent calls on forced frames changes how many random numbers a stochastic agent consumes. Because gameplay now has split agent/transition RNG, this cannot change transition randomness, but it can change later stochastic agent tie-breaks. So any future fast path must define this explicitly as a new public interface contract, not silently change legacy payoff semantics.
