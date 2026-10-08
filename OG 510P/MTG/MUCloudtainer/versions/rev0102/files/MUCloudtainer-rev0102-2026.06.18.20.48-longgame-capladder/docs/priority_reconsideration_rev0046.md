# rev0046 priority reconsideration

The main bottleneck remains label quality, not model class.

The yield screen performed better than the hard queue and slightly better than the margin queue in the smoke matched audit.  That makes it worth keeping, but the result is not strong enough to stop auditing alternative selectors.

## Current priority order

```text
1. Use yield-screen queueing for the next larger action-counterfactual collection.
2. Keep matched hard/margin/yield queue audits beside future selector changes.
3. Train a new counterfactual gameplay ranker only after decisive labels increase.
4. Attach C++ transition shadow checks to every branch-heavy collector.
5. Promote gameplay policies only after nontruncated payoff tables and replay/C++ gates stay clean.
```

The next policy-relevant revision should probably collect a larger yield-screened branch dataset and train a rev0047 counterfactual ranker from it.
