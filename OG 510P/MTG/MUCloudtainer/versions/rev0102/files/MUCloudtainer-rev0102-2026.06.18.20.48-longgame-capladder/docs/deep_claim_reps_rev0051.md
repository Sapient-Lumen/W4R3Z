# rev0051 — Deep claim repetitions

rev0050 produced a terminal-clean claim ledger over the eight-strategy yield-ranker panel.  rev0051 treats that ledger as an evaluation agenda rather than a conclusion.

The new script selects the first three claim-ledger targets matching:

```text
robust_candidate
life_sensitive_candidate
```

and runs extra terminal-clean repetitions for every ordered pair where at least one seat is a target.

```text
8 strategy population
3 target strategies
ordered pairs touching target: 39
life totals: 20 and 40
starting players: 0 and 1
reps: 2
raw games: 312
max_decisions: 900
```

Every row is annotated with:

```text
focus_targets
focus_kind
```

so downstream analysis can tell whether the row was target-vs-target, target-as-player-0, target-as-player-1, or field-only.  The panel is focused; it is not a replacement for a full all-pairs table.

The new files are:

```text
src/muc5/terminal_deep.py
scripts/run_rev0051_deep_claim_reps.py
tests/test_rev0051_terminal_deep.py
```

The important design point is that no new gameplay policy is promoted.  This revision spends samples where the previous claim ledger said uncertainty mattered most.
