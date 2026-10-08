# rev0019 scout notes

This turn continued the cache/memory hunt but focused on hardening rather than only adding candidates.

## Freshly promoted sources

- **VeriCache** — promotes exact-output / catastrophic-divergence checking for lossy KV methods. The key CloudtainerML interpretation is that good short-output accuracy or average reconstruction error is not enough if long decode, code, or tool calls diverge.
- **Periodic KV Cache Consolidation / Bottlenecked Transformers** — treats reasoning-step boundaries as events where cache can be rewritten/consolidated rather than passively evicted.
- **Tensor Memory** — adds a fixed-size recurrent tensor/grid state to the object frontier beside KV rows, residual checkpoints, and fast-weight matrices.
- **CSR / ASR** — frames infinite-horizon real-time policies around prefix stability, incremental extensibility, and asynchronous state reconciliation.
- **Gated Memory Policy** — reinforces the idea that history can hurt Markovian tasks; the relevant question is when to recall, not only what to recall.
- **Reasoning Cache** — iterative response/summary state as a long-horizon reasoning mechanism.

## New runnable hardening probes

- `experiments/vericache_guard/vericache_guard_probe.cpp`
- `experiments/periodic_cache_rewrite/step_rewrite_probe.cpp`
- `experiments/memory_provenance_phase/memory_provenance_phase.cpp`

These are synthetic probes, not paper reproductions. They are intended to find failure modes and phase boundaries before any tiny trained model escalation.

## Priority change

P0 now includes **lossless acceptance metrics** for lossy cache probes. The cube should track catastrophic divergence tails and exact-output mismatch, not only MSE or average utility.
