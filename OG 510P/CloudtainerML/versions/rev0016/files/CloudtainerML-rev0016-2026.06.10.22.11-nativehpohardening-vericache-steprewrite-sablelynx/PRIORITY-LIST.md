# CloudtainerML priority list — rev0016

## P0

1. Verified lossy-cache guard and catastrophic divergence metrics.
2. Periodic reasoning-step cache rewrite.
3. Persistent-memory provenance/correction phase diagram.
4. Native C++ phase-diagram lane and HPO-guided sweeps.
5. Residual stream / KV object frontier.
6. Query movement vs cache movement phase boundaries.
7. Lossless acceptance metrics for lossy cache probes.
8. Agentic DFS / TRACE / SMT tiny-trained escalation.

## P1

- Tensor Memory fixed-state object frontier.
- CSR / asynchronous state reconciliation.
- Learned history gate versus always-history.
- Reasoning Cache iterative response-summary loop.
- Conversation-level agentic scheduler toy.
- Hybrid head-type compression and multimodal token regimes.

## Current recommendation

Use rev0016 to stop judging cache probes only by mean error. Add exact-output / catastrophic-tail metrics to older lossy probes, then harden either the VeriCache guard thresholds or the periodic rewrite event detector.
