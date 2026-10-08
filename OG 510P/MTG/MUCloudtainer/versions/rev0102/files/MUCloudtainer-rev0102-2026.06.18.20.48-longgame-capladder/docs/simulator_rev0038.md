# Simulator status at rev0038

The simulator is still Python-authoritative.  C++ is a parity-checked accelerator candidate, not the rules authority.

rev0038 does not change game rules.  It changes how offline action-counterfactual labels are collected:

```text
run public behavior game
build DecisionFrame
ask public-safe screeners for votes
if votes disagree, branch selected legal actions offline
roll out each branch
record candidate-action labels
C++ shadow-check every transition
```

No legal-action semantics were changed.  No hidden information is added to gameplay policies.

Current trust status:

```text
automated public games: working
replay gates: working
C++ transition shadow: working on rev0038 traffic
branch-label collection: working, still label-budget limited
strategic claims: still smoke-scale unless tables are denser and nontruncated
```
