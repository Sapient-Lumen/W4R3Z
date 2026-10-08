# rev0021 scout notes — charter reset toward performance/surprise

This is not a broad paper-hunt revision. It is a steering correction.

The previous surface over-emphasized model security, memory poisoning, provenance, and state-trust boundaries. Those topics remain in the cube as a small side wing, but they are not the reason CloudtainerML exists.

## Corrected center of gravity

CloudtainerML is for finding high-performance options and surprising tiny-scale mechanisms:

- C++ microkernels and phase diagrams where high-volume sweeps matter.
- Equal-budget tests: bytes, latency, tokens, precision, recompute, and accuracy.
- Transformer/cache/memory alternatives that can be falsified cheaply.
- Tiny trained models only after symbolic/tensor probes identify a sharp question.
- Negative results that change intuition.

## Reprioritized core candidates

- Token/precision budget frontier.
- Residual stream vs KV object frontier.
- Move-query vs move-cache phase boundaries.
- LRKV/head-diversity low-rank residuals.
- SANTA/stochastic sparse-attention estimator tails.
- KV-CAT representation-compressibility proxy.
- DF-SSM scaffold/correction toy, if byte-normalized.
- Agentic DFS, SMT transition labels, FlowTrace credit, and RASP/weights-to-code for tiny trained escalation.

## Side wing retained but bounded

Memory poisoning, sycophancy, JANUS-style distortion, provenance-heavy safety, and trustworthy memory search stay available as side-wing probes. They can serve as acceptance tests when they invalidate a performance/correctness claim, but they should not dominate the P0 list.
