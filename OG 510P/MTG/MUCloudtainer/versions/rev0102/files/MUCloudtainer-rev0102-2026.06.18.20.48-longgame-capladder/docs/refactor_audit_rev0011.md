# rev0011 Refactor / Audit Notes

## Refactor performed

Added an audit-only replay layer:

```text
src/muc5/replay.py
```

This layer owns:

```text
canonical_state_snapshot
state_fingerprint
observation_fingerprint
record_public_decision_trace
replay_public_decision_trace
```

It does not replace the engine.  It wraps the public DecisionFrame path.

## Why this is a refactor, not just a script

The old profiling/simulation paths were good for throughput, but not enough for later science.  If a tournament row claims a weird win, future work needs a stable way to say:

```text
same deck
same seed
same initial config
same legal action menus
same action indices
same final state
```

rev0011 adds that seam.

## Audit added

```text
scripts/run_rev0011_replay_probe.py
scripts/audit_reward_guard_rev0011.py
scripts/build_rev0011_question_bank.py
```

`audit_cube.py` now checks:

```text
24 replay traces generated
sample trace replays
reward guard artifacts exist
forced truncation is detected
question bank exists
live replay smoke passes
```

## Remaining concerns

1. Old trusted-state agents still exist and are useful as baselines, but learned agents should use DecisionFrames.
2. Replay traces are simulator-revision-specific; old traces may fail after intentional rules fixes.
3. The state fingerprint is not a storage-efficient delta format.  It is audit-first, not performance-first.
4. Future high-volume learning should not write full traces for every game.  Use sampling: trace all promoted surprises, trace a small percentage of bulk rollouts.
