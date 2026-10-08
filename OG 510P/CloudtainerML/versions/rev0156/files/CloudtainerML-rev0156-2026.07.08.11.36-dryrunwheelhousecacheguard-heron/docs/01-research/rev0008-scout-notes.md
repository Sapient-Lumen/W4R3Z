# rev0008 scout notes — PCAF / IntentKV / latent-router / HIST

This revision adds five runnable probes and a metric-index refactor.

## Fresh source clusters

- **PCAF / gated sparse successor memory**: hash local successor records, retrieve bounded candidates, mix sparse cache with local model. Tiny test asks whether old facts survive hash collisions and local decoys.
- **IntentKV / cross-turn agent cache**: session QueryMemory, intent-aware scoring, and slot-map redirection suggest a new axis: prune history by task intent rather than token age alone.
- **Shared routing once**: token-sparse routing can be computed once and reused across layers if supports are stable; toy drift regimes test when that breaks.
- **Sliding-window no-PE order signal**: the outgoing token is recoverable from histogram-update deltas; useful as a tiny operational probe, not a universality proof.
- **Latent reasoning router**: token-wise choice among explicit tokens, deterministic latent steps, and flow-latent steps creates a cost/accuracy routing problem that can be tested without training.

## Research posture

P0 is now split into two adjacent fronts:

1. cache/memory/routing allocation; and
2. latent-compute routing / verification.

The cube should still avoid choosing a final project. The near-term goal is to identify which toy claims produce strong, non-oracle baselines.
