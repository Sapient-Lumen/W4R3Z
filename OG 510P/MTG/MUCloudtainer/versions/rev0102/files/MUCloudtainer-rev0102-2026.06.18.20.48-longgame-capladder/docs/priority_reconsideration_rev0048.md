# rev0048 priority reconsideration

Previous priority:

```text
1. Reduce truncation in payoff panels before trusting ranker comparisons.
2. Improve decisive action-counterfactual labels per rollout spent.
3. Keep yield-screen queueing, with periodic matched audits.
4. Attach C++ transition shadow checks to every branch-heavy collector.
5. Promote policies only after clean nontruncated payoff tables.
```

rev0048 addresses priority 1 directly. The next priority should now shift back toward label quality.

Current best path:

```text
1. Use terminal-clean payoff settings as the default for ranker comparisons.
2. Increase decisive action-counterfactual labels per rollout spent.
3. Use yield-screen queueing, but keep matched queue audits beside changes.
4. Attach C++ transition shadow checks to every branch-heavy collector.
5. Add no-choice segment execution only when branch collection becomes speed-limited.
```

A useful rule going forward:

```text
A policy panel with nontrivial truncation is a diagnostic, not a promotion table.
```
