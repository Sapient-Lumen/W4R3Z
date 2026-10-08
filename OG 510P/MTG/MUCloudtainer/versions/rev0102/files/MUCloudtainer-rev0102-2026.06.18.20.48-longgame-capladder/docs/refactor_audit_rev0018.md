# rev0018 refactor and audit notes

## Main refactor

`src/muc5/cpp_transition.py` now uses a stricter signature transport:

```text
SIGv1 -> SIGv2
```

`SIGv2` adds:

```text
ordered library CSV for both players
pending-choice player/kind/resume fields
pending Overlord trigger count
Jace legend old/new loyalty payload
Jace +2 target player payload
```

The refactor makes the C++ microkernel less count-only and more state-exact. This is necessary before we can trust C++ on stack resolution, Brainstorm putbacks, Jace fateseal bottoming, and Overlord trigger chains.

## Added audit artifacts

```text
data/rev0018_cpp_transition_diff_summary.json
data/rev0018_cpp_transition_cases.csv
data/rev0018_cpp_transition_mismatches.json
data/rev0018_cpp_transition_coverage_summary.json
data/rev0018_cpp_transition_coverage_rows.csv
```

## Audit stance

The audit deliberately does not claim that C++ is now the engine. The claim is narrower:

```text
For every transition in the rev0018 directed/sample set,
C++ and Python produce identical SIGv2 post-state signatures.
```

The archive should keep making claims of this form until a full C++ rollout engine is justified.
