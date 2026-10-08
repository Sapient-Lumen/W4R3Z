# Rev0007 scout notes

## New hot sources

- ReasonAlloc: hierarchical decoding-time KV budget allocation with architecture-specific Reasoning Wave plus online head routing.
- Attention Amnesia: CoT SFT damages long-context recall in hybrid models through Q/K routing; QK restore is training-free.
- FlashMemory: lookahead sparse attention with a separate neural memory indexer.
- You Only Index Once: shared cross-layer routing index for sparse attention in KV-sharing architectures.
- Louver: range-search framing for sparse attention with zero-false-negative threshold retrieval.
- Echo-Infinity: learned evolving memory queries updated as history leaves the local window.

## Shape update

The baby datacube should probably separate **memory form** from **allocation policy**. Token eviction, precision allocation, layer allocation, head allocation, routing index, QK restoration, and cross-call state are different knobs even if all reduce context cost.
