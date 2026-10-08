# rev0041 refactor/audit

New code:

```text
src/muc5/action_hard_frame.py
scripts/run_rev0041_hard_frame_selector.py
tests/test_rev0041_hard_frame.py
```

The refactor separates public-frame screening from branch execution.

Old shape:

```text
encounter frame in behavior game
immediately decide whether to branch
```

New rev0041 shape:

```text
encounter many public frames
score frames using public-only hard-frame signals
cap selected frames per behavior game
branch the highest-scoring frames
compare selector methods on shared branch outcomes
```

The cap per behavior game matters. An initial top-k version over-selected one long game and produced many high-looking but outcome-tied labels. The current collector applies a per-game cap before filling any remaining slots.

Audit guarantees added:

```text
rev0041 selected-frame rows exist
high-action frame selection is nonzero
selector methods appear for each selected situation
branch truncations are zero
C++ skipped transitions are zero
C++ mismatches are zero
rev0041 docs/scripts/tests exist
```
