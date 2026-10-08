# Refactor audit — rev0058

## Refactor performed

rev0058 extracts the ad-hoc terminal-mechanism parsing that existed inside `scripts/run_rev0057_mission_audit.py` into reusable source modules:

```text
src/muc5/terminal_mechanisms.py
src/muc5/terminal_decomposition.py
```

The new seam provides:

```text
loss_loser()
terminal_mechanism()
annotate_target_mechanism()
mechanism_profile_rows()
target_summary_rows()
rev0058_decomposition_arms()
decomposition_specs()
annotate_decomposition_rows()
```

## Why this matters

The project kept rediscovering the same question in reports: was a target winning by damage, by decking the opponent, by being decked, or by truncation?  That should not live as one-off script code.  It is now a reusable analytics layer for future claim cards and explanatory experiments.

## Waste correction

rev0058 also stops the latest experiment from adding another full raw transition CSV.  The live run generated `58172` transition rows and checked all of them with the C++ microkernel, but only ships a compact sample plus summary:

```text
data/rev0058_decomposition_cpp_transition_sample.csv
```

This is the first concrete application of the rev0057 maintenance policy.

## Tests

```text
tests/test_rev0058_decomposition_mechanisms.py
```

The test covers mechanism parsing, grouped summaries, arm construction, proportional 40/60 control decks, and C++ spec metadata contracts.

## Packaging cleanup

Before packaging rev0058, Python bytecode caches and `.pytest_cache` are removed from the linked working tree.  Build outputs are retained for now because inherited C++ smoke/audit paths still use them opportunistically, but cache files should not be treated as scientific evidence.
