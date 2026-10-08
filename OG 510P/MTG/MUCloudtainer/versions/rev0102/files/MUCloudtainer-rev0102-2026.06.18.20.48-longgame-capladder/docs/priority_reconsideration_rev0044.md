# rev0044 priority reconsideration

Current priority order:

```text
1. Matched comparison: margin-screen queue vs older hard-frame queue.
2. Increase decisive labels per rollout, not total candidate rows.
3. Keep online adaptive allocation and C++ shadow checks attached to every branch-heavy collector.
4. Add no-choice segment execution only when branch collection is clearly speed-limited.
5. Promote policies only after nontruncated payoff tables and replay/C++ gates stay clean.
```

The main lesson remains: we are label-quality limited. The margin screen is a small step toward predicting which public frames are worth branching before paying the rollout cost.
