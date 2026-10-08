# rev0011 Replay Lab

Codename: `replaylab-rewardguard`

## Why this exists

MUC-5 is now past "does the engine run?" and into "can we trust artifacts produced by learning/search/evolution?"  A strange payoff row is not useful unless future sandpeople can reproduce the exact game that produced it.

rev0011 adds deterministic replay as a promotion gate:

```text
record public DecisionFrame game
  -> write action indices + legal action menus + state fingerprints
  -> replay from initial deck/seed/config
  -> require every pre/post fingerprint to match
```

The replay trace is omniscient for auditing but not for agents.  The agent still receives only:

```text
public/own observation
legal macro-actions
chosen legal action index
```

## Important refactor

The replay recorder separates two random streams:

```text
agent_rng       tie-breaks / random policy choices
transition_rng  state-transition randomness such as Jace ultimate shuffles
```

This matters because replaying a trace should not depend on how many random numbers a policy consumed while ranking actions.  A replay applies recorded action indices directly, so it must reproduce only transition randomness.

Existing arena paths still work, but future trace-critical runners should prefer the replay module's separated-rng path.

## New files

```text
src/muc5/replay.py
scripts/run_rev0011_replay_probe.py
tests/test_rev0011_replay_rewardguard.py
```

New artifacts:

```text
data/rev0011_replay_traces.jsonl
data/rev0011_replay_probe.csv
data/rev0011_replay_probe_summary.json
```

## Trace schema

Each JSONL row contains:

```text
schema
config
initial_fingerprint
events[]
final
```

Each event contains:

```text
step
player
state_revision
pre_fingerprint
observation_fingerprint
legal_action_count
legal_actions
action_index
action
post_fingerprint
post_revision
```

## Promotion rule

A result row is not considered trustworthy enough for later theory unless:

```text
simulator revision recorded
trace replay passes
reward convention recorded
truncation status recorded
construction context recorded
```

rev0011 only fully implements the replay part of this promotion rule.
