# rev0017 C++ transition microkernel

rev0017 adds `cpp/muc5_transition_micro.cpp` and `src/muc5/cpp_transition.py`.

The purpose is not to replace Python yet. The purpose is to establish a safe C++ migration pattern:

```text
Python GameState + legal Action
  ↓
flat TransitionMicroRecord
  ↓
C++ applies one selected deterministic transition
  ↓
Python and C++ compare compact post-state signatures
```

## Covered transitions

The current microkernel covers deterministic one-action transitions that do not require library draws, hidden choice payloads, stack resolution, or shuffling:

```text
PLAY_ISLAND
CAST Jace from MAIN
CAST Overlord from MAIN, impending and full-cost modes
CAST Counterspell from RESPONSE
CAST Force of Will from RESPONSE, mana and pitch modes
Jace -1 targeting ready/sick/tapped Overlord creatures
PASS from precombat MAIN to ATTACK
PASS from ATTACK to postcombat MAIN
PASS/BLOCK in BLOCK frame, including combat damage and Jace death
```

It intentionally does not yet cover:

```text
stack resolution
Overlord draw/discard trigger choices
Jace +2 private top-card choice
Jace Brainstorm putback choice
Jace ultimate shuffle
cleanup discard continuation
turn advancement / impending counter tick
```

Those are future microcase families.

## Why this is valuable

The simulator may eventually bottleneck learning. C++ can help, but only if it preserves the exact legal/referee semantics. The project rule is:

```text
C++ does not become authoritative until it can match Python on directed edge cases and sampled gameplay states.
```

rev0017 generated:

```text
5,017 transition cases
17 directed edge cases
5,000 sampled gameplay cases
0 mismatches
```

## Office constraint

This cloudtainer has `g++`, so C++ is available. But the archive must remain understandable and runnable by future cloudtainer users. Keep C++ kernels narrow, documented, and differential-tested. Avoid large native build systems until profiling proves the need.
