# rev0031 refactor/audit

Refactor focus:

```text
cpp/muc5_transition_segment.cpp
src/muc5/cpp_segment.py
scripts/run_rev0031_cpp_segment_check.py
scripts/run_rev0031_repeated_cf_scale.py
```

The main refactor is a new C++ seam that reuses the existing transition microkernel instead of duplicating transition logic. The segment executable includes `muc5_transition_micro.cpp` with its main function renamed, then adds a segment-grouping main.

Audit additions check:

```text
C++ segment tool builds locally with g++
rev0031 segment game/row counts match summary
all no-choice segments were C++ checked
zero skipped C++ events
zero segment mismatches
compression ratio remains above 1.0
scaled repeated counterfactual rows match summary
scaled repeated counterfactual C++ checks have zero skipped/mismatched events
required rev0031 docs/scripts/tests/data exist
```

This revision also keeps the inherited replay, promotion, statgate, C++ trace, mulligan, ranker, and simulator checks.
