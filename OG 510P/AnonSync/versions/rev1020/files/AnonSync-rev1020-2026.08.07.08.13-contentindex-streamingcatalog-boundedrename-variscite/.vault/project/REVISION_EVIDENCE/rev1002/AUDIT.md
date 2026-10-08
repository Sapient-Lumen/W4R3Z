# Rev1002 audit

Rev1002 bounds local delta-copy source reads independently of wire framing. Same-path predecessor and current-visible cross-file reuse share one 32 MiB source-read frontier per reconciliation apply, with each targeted read capped at 4 MiB and charged by actual bytes read. The durable staged prefix can resume inside one adaptive chunk after service reconstruction.

The adjacent audit corrected a subtle authenticated-suffix hazard: when local reuse advanced into a wire range, the receiver once risked dropping the already authenticated suffix. The retained implementation validates the complete wire range first, accounts fully covered ranges, trims only the committed prefix of a partial overlap, and independently hashes and stages the advancing suffix. Gaps fail closed.

The design remains acceleration rather than publication authority. Exact targeted source observation, per-range SHA-256, durable prefix state, final whole-target SHA-256, and causal admission remain mandatory. Same-path predecessor-manifest construction and terminal whole-target verification are still complete-file owner operations and are named as the next multi-terabyte scheduling boundaries.
