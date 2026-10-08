# rev0047 Priority Reconsideration

The highest-value path is still label quality, not model class.

Current priority:

```text
1. Reduce truncation in payoff panels before trusting ranker comparisons.
2. Improve decisive action-counterfactual labels per rollout spent.
3. Keep yield-screen queueing, but audit it against hard/margin screens periodically.
4. Use C++ transition shadow checks for every branch-heavy collector.
5. Promote gameplay policies only after nontruncated payoff tables and replay/C++ gates stay clean.
```

The rev0047 ranker is technically cleaner than prior one-off scripts because training has been factored into a reusable helper. But the payoff panel had many truncations, and the new yield-screen label set was still sparse. Next work should target label density and truncation behavior before a larger population claim.

