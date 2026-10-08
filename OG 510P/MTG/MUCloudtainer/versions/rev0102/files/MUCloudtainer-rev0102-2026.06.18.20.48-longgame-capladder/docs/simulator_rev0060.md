# Simulator note rev0060

rev0060 is a forensics/refactor revision.  It does not change card legality, stack resolution, hidden-information observations, mulligans, terminal loss rules, or deck construction semantics.

Changed:

```text
Corrected applied-decision counting in public-agent and C++ shadow rollout loops.
Added compact trajectory forensics for life-20 A/B claim explanation.
```

Validation target:

```text
Winners/scores/loss reasons from historical life-20 A/B rows must reproduce exactly.
New decision counts report applied decisions; legacy row decision counts are retained only as an audit compatibility field.
```
