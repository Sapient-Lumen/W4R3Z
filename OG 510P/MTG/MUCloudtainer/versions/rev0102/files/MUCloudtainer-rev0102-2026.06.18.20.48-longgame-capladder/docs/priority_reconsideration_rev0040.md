# Priority reconsideration after rev0040

rev0040 gives a mild negative/neutral result: the hybrid selector was safe under the smoke audit, but it did not outperform simpler selectors because the branch budget was not binding hard enough in the sampled frames.

Current priority order:

```text
1. Deliberately screen for high-action, high-margin frames where selector choice matters.
2. Combine hybrid selection with adaptive extra rollouts instead of fixed rollouts.
3. Keep matched selector audits beside every new label selector.
4. Use C++ no-choice segment batching when branch collection clearly becomes speed-limited.
5. Promote policies only after nontruncated payoff tables and replay/C++ gates stay clean.
```

The limiting resource is still decisive labels, not model class. The next selector should be evaluated on frames where the union of plausible actions is larger than the branch budget and branch outcomes actually separate.
