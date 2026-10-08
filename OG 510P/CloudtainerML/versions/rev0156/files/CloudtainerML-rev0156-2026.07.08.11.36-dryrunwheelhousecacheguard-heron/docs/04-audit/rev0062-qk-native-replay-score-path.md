# rev0062 — QK native replay score-path audit

rev0062 addresses a concrete evidence gap: rev0061 measured only materialized-score consumption.  Scores were already present, so QK score construction was still an unmeasured blocker.

The new probe captures a Q/K/V trace packet from the local tiny trained transformer, exports it to a native binary format, and compares dense online attention against two sparse schedules:

1. **Materialized histogram:** computes all QK scores, stores the score row, bins by score mass, then reads selected values.
2. **Streaming recompute histogram:** avoids storing scores but pays repeated QK passes for max, histogram, sparse denominator, and accumulation.

## Result

The materialized histogram selected fewer values, but did not beat dense once QK construction was included.  The streaming no-score-storage path was much slower because recomputation dominates.

This closes the local QK replay gap but keeps promotion blocked.  Remaining blockers are public/pretrained traces, GPU/fused-kernel timing, and a strict materialization-free sparse schedule with measured speedup.
