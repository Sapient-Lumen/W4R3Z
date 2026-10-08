# rev0010 public-frame fuzzing

The new fuzzing pass uses the safe public DecisionFrame interface, not the legacy trusted `GameState` agent interface.

Loop:

```text
start random seed-deck matchup
  -> build DecisionFrame
  -> choose random legal action index
  -> apply indexed action with revision guard
  -> check card conservation
  -> check observation/leakage shape for both players
```

Result from this revision:

```text
games: 300
decisions: 63667
invariant checks: 63857
observation checks: 1538243
failures: 0
terminal games: 190
truncations: 110
```

## Why fuzzing matters here

Learning methods will exploit any shortcut the simulator accidentally gives them. Fuzzing is a cheap way to catch broad classes of bad states before a policy discovers them as “strategy.” It is especially useful in this cloudtainer because we cannot rely on a huge external rules engine or compiled simulator; we need small repeatable guards around our own referee.

## What fuzzing does not prove

A zero-failure fuzz run does not mean the game is exact Magic. It means this set of random legal trajectories did not break card conservation, public observation shape, or the DecisionFrame/action-index contract.
