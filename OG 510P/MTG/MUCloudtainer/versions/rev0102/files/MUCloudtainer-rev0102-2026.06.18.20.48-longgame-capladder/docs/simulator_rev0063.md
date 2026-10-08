# rev0063 simulator scope note

rev0063 does not change MUC-5 game rules, terminal semantics, legal actions, mulligan mechanics, C++ transition parity, or reward reporting.

The only gameplay-adjacent addition is a new public policy profile, `threat_closure`, used as an audit/control pilot.  It is available through `make_public_agent("threat_closure")` and observes the same public decision frame used by `threat_rush`, `counter_happy`, `patient`, and the learned ranker wrappers.

The revision's claim is therefore about evaluation hygiene:

```text
Some previous threat-shell losses to inert controls were caused by pilot overdraw and under-closure, not by game rules or by a robust all-Island strategy.
```

The result should not be read as a promotion of `threat_closure` into the main population.  It should be used next as a stronger opponent-control baseline for the counter-wall/library-buffer claim family.
