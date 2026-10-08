# rev0010 directed rules scenarios

This revision adds a small directed rules-scenario suite. It is not a full Magic oracle. It is a regression suite for the five-card MUC-5 rules surfaces most likely to corrupt learning if wrong.

## Scenario checks

1. **Overlord attack triggers resolve sequentially.**
   Earlier revisions aggregated multiple attacking Overlord triggers as draw `2N`, then discard `N`. That gives the agent extra future-card information before the first discard. rev0010 resolves each trigger as draw two, discard one, then continues to the next trigger.

2. **Jace -1 targets a specific creature state.**
   Earlier aggregation meant Jace always bounced a ready Overlord first. rev0010 exposes `target_state=ready|sick|tapped` for actual Overlord creatures and does not expose impending Overlords as creature targets.

3. **Counter war: Force protects Jace from Counterspell.**
   The scenario checks stack order: Force of Will counters Counterspell, then Jace resolves.

4. **Force at one life is legal but fatal.**
   Paying one life as a Force alternative cost at exactly one life is legal, then state-based checking causes that player to lose before Force resolves.

5. **Jace ultimate uses real card IDs.**
   The target library is exiled as actual card counts, and the target hand is shuffled into the new library, preserving card conservation.

Generated files:

```text
data/rev0010_rules_scenarios.csv
data/rev0010_rules_scenarios_summary.json
data/rev0010_rules_scenarios_stdout.txt
```
