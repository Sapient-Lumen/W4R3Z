# rev0019 experiment matrix additions

## C++ trace equivalence

Question:

```text
Can C++ reproduce Python one-action transitions across real recorded public games?
```

Current smoke answer:

```text
yes, for 8,149 / 8,153 events in the rev0019 trace set
no mismatches on supported events
unsupported events were Jace ultimate only
```

## Jace ultimate transport

Question:

```text
Should C++ implement Jace ultimate by consuming an explicit shuffle order from Python, or should ultimate remain a Python-only transition until full RNG parity exists?
```

Options:

```text
A. Explicit shuffle transcript: Python trace records post-shuffle order; C++ verifies deterministic state update.
B. Shared RNG algorithm: C++ reproduces Python random shuffle exactly. Harder and brittle.
C. Python-only ultimate: acceptable if rare, but blocks full C++ rollout equivalence.
```

Recommendation for next revision: use option A for transition checking, not for authoritative play. That lets C++ verify the state transformation without pretending to own Python RNG.

## Imitation/ranker prep

Question:

```text
Can we train a tiny action ranker from public DecisionFrame features to imitate the current promoted/code policies?
```

This should wait until after the C++ trace checker is stable, because training datasets should be generated only from replayable and promotion-gated traces.
