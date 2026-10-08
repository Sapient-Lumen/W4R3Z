# Priority reconsideration after rev0041

rev0041 successfully targeted high-action public frames, but selector separation is still weak. The best next path is:

```text
1. Attach adaptive/racing branch allocation to the hard-frame queue.
2. Track decisive labels per rollout spent, not just total candidate rows.
3. Keep matched selector audits beside every new selector.
4. Use C++ no-choice segment batching only when branch collection becomes clearly speed-limited.
5. Promote policies only after nontruncated payoff tables and replay/C++ gates stay clean.
```

The current limiting resource is still decisive labels. We are not model-limited yet.
