# rev0016 C++ legal-menu differential harness

rev0016 adds:

```text
cpp/muc5_legal_menu.cpp
src/muc5/cpp_legal.py
scripts/run_rev0016_cpp_legal_diff.py
```

The C++ binary reads a flat tab-separated state summary and emits legal macro-action strings. Python remains authoritative; this is a differential oracle, not the official engine.

## Why this seam?

Legal-action enumeration is a stable, hot boundary:

```text
state summary -> legal macro-actions
```

It is also safety-critical. If the legal menu is wrong, every learning method is polluted. A C++ legal-menu kernel is therefore valuable only if it is compared against the Python reference over real game states.

## Differential run

The rev0016 run generated:

```text
72 public games
18,263 decision records
0 C++/Python legal-menu mismatches
max legal actions: 37
mean legal actions: about 2.06
```

Frames covered:

```text
MAIN
RESPONSE
ATTACK
BLOCK
```

Pending choices covered:

```text
discard
cleanup_discard
jace_brainstorm_putback
jace_legend
jace_plus2
```

The data lives at:

```text
data/rev0016_cpp_legal_diff_summary.json
data/rev0016_cpp_legal_diff_games.csv
data/rev0016_cpp_legal_diff_mismatches.json
```

## Current limitation

The C++ legal-menu kernel currently mirrors legal actions only. It does not apply actions, advance phases, draw cards, resolve combat, shuffle, or enforce hidden-information redaction. Those stay in Python.

The next C++ target should be **directed state-transition microcases**, not a full rollout engine.
