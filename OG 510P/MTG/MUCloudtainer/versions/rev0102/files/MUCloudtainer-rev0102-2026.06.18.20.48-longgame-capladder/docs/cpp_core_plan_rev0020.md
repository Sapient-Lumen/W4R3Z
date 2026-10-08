# rev0020 C++ core plan

The C++ direction is now a ladder, not a rewrite.

## Current completed seams

```text
rev0015: C++ deck probability probe kernel
rev0016: C++ legal-menu differential harness
rev0017: C++ one-action transition microkernel, first directed/sample cases
rev0018: C++ stack/choice transition expansion and sampled coverage probe
rev0019: C++ recorded public-trace checker
rev0020: C++ Jace ultimate support through explicit shuffle transport
```

## Authority model

Python remains authoritative for:

```text
rules semantics
hidden-information observation boundary
replay trace generation
promotion/statistical/reward gates
random-transition outcome generation
analytics and docs
```

C++ is trusted only after:

```text
1. a stable seam is identified
2. Python projects states/actions into a flat transport
3. C++ reproduces directed cases
4. C++ reproduces sampled gameplay cases
5. C++ reproduces recorded public traces
6. coverage debt is explicit
```

## Randomness contract

rev0020 establishes the current random-transition pattern:

```text
Python RNG creates the random outcome
C++ receives the outcome transcript
C++ applies deterministic state changes from that transcript
```

For Jace ultimate, the transcript is the ordered new target library.

This is enough for differential checking. It is not necessarily the final tournament-speed C++ RNG design.

## Next C++ target

The next useful target is a **batch-transition benchmark**:

```text
read recorded trace rows
project supported transitions
batch them through C++
measure transport overhead vs C++ work
```

This will answer whether Python/C++ boundary overhead is already the bottleneck. If it is, a full C++ stateful rollout core becomes more attractive. If not, keep porting seam-by-seam.
