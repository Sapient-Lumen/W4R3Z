# Simulator status through rev0028

The simulator remains a Python semantic reference with C++ shadow parity for stable transition seams.

rev0028 adds explicit-pregame game construction for diagnostics:

```text
start_game_from_pregame_state(...)
```

This makes the simulator suitable for opening-hand counterfactuals where a normal `start_game(...)` call would entangle mulligan RNG and opponent pregame construction.

## Status

```text
automated public DecisionFrame games: working
learned gameplay rankers: working as experimental public agents
learned mulligan rankers: working as experimental pregame agents
opening-hand counterfactual probes: working smoke path
C++ transition shadow checks: passing on rev0028 traffic
full C++ tournament core: not yet
```

## rev0028 validation data

```text
72 paired openings
144 branch games
36,342 C++-checked transitions
0 mismatches
0 truncations
```

The simulator is now strong enough for diagnostic counterfactual data generation.  It is still not a reason to overclaim strategy conclusions from small smoke tables.
