# rev0055 — restartchaos-effectseal-fuzzshrink

This revision keeps the cube in the no-network, risk-first public-edge lane. It treats a crash/restart window, a final local side-effect seal, and fuzz-corpus compaction as protocol boundaries rather than cleanup tasks.

Strong sentence:

```text
A restarted public edge is not safe because replay, quench, fuzz, or journal evidence passed separately; it is safe only when crash-cut memory, shrink evidence, and the final effect seal bind to one exact boundary.
```

New surfaces:

- `restartchaos.py` — signed crash-cut observations across handler replay, side-effect journal, handler quench, and fuzz ledger.
- `effectseal.py` — final exact-boundary no-network seal after restart and fuzz evidence agree.
- `fuzzshrink.py` — coverage compaction that preserves required mutation evidence and diversity.
- `restartfold.py` — audit/refactor fold preserving rev0054 `replayfold` predecessor history.

Verification path: `tests/test_rev0055_restartchaos_effectseal_fuzzshrink.py`.
