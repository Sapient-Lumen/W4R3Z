# Priority Reconsideration rev0054

rev0054 deepened the first concrete matchup candidate.  The result is not merely “cf34 good”; it is more specific:

```text
cf34_counter_wall vs pub_threat_overlord
  positive overall
  much stronger at 40 life than 20 life in this sample
```

Current best path:

1. Treat `cf34_counter_wall` vs `pub_threat_overlord` as a life-sensitive claim candidate, not a life-stable claim.
2. Deepen the life-specific cells separately, especially the 20-life cell where the confidence interval still crosses 0.5.
3. Build a small claim dossier format for future concrete matchup cells so we can compare claims consistently.
4. Keep terminal-clean max_decisions=900 as the default for claim work.
5. Keep C++ transition shadow checks attached to payoff-heavy and branch-heavy work.
6. Return to yield-screened label collection after the current matchup-claim agenda is less ambiguous.

No gameplay policy should be promoted from rev0054 alone.
