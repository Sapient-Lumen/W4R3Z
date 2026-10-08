# rev0028 scout notes — operator routing, probabilistic routes, sparse runtimes

This revision stays on the performance-core charter. Security/trust/provenance remains a bounded side wing and did not drive new priorities.

## New live hypotheses

1. **Operator routing as architecture discovery.** Chiaroscuro/CHIAR-style spectral entropy routing is valuable because routing collapse can be evidence: if an operator is consistently rejected, the smaller operator menu may be the architecture. The caveat is strong: synthetic and small-data regimes can prefer uniform/full attention, so alias/high-frequency traps must be first-class.
2. **MoE subset exploration has a rare-expert purpose.** Probabilistic subset routing is not automatically better than deterministic top-k; it earns its keep only when rare experts, complementary experts, noisy logits, or drift make exploitation brittle.
3. **Route consistency can dominate reconstruction.** VSRAQ-style route-alignment thinking is now a quantization guard for MoE-ish probes.
4. **C++ activation sparsity should be judged by wall-proxy, not sparsity percentage.** Spike-aware execution may be useful, but dense INT8 remains a serious baseline when branch/cache/tiny-batch costs are counted.
5. **Head-wise routing is conditional.** It is promising only when attention heads carry separable factors; otherwise it is overhead/noise.

## New native probes

- `spectral_operator_routing.cpp`
- `probmoe_subset_exploration.cpp`
- `routing_consistent_quantization.cpp`
- `spike_sparse_cpu_runtime.cpp`
- `headwise_router_collision.cpp`

## Priority movement

P0 promotion is given only to **Spectral Operator Routing Frontier** and the new native phase-readiness report. The other lanes remain P1/P2 until they produce stronger non-oracle wins or become tiny-trained candidates.
