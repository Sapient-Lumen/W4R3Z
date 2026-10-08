# C++ core plan — rev0059

No new C++ surface is promoted in rev0059.

The useful near-term C++ work is still not a full engine rewrite.  It is a compact evidence path:

```text
1. keep Python as semantic authority;
2. keep C++ chosen-transition parity as the live shadow;
3. add transition-level feature summaries before adding more raw transition dumps;
4. only move larger rollout loops to C++ after those feature summaries prove the target bottleneck.
```

rev0059 reinforces the retention policy: generated transition rows are checked, summarized, sampled, and not shipped in full.
