# Priority reconsideration — rev0042

The current bottleneck is still label quality, not model class.

rev0042 shows that adaptive prefix racing can save rollout budget on hard frames, but it can also change labels when it stops before seeing all later rollout samples.  That is exactly the tradeoff future online collectors need to expose rather than hide.

Current priority order:

```text
1. Build an online hard-frame adaptive collector that spends extra branch rollouts live.
2. Track decisive labels per rollout spent as a first-class metric.
3. Preserve matched fixed-vs-adaptive audits beside every new branch labeler.
4. Use C++ no-choice segment batching when branch collection becomes speed-limited.
5. Promote policies only after nontruncated payoff tables and replay/C++ gates stay clean.
```

No new policy should be promoted purely from rev0042.  The result is a label-density and audit improvement.
