# Research scout notes — rev0025

The hunt stayed performance-first. The most useful new sources cluster around routing, sparsity, and cheap-screen reliability.

## Sources added

- `SRC-0294` DOT-MoE: balanced transport for dense-to-MoE conversion.
- `SRC-0295` HASTE: group-shared sparse fan-in / dense-head sparse-tail with hardware-aware speed claims.
- `SRC-0296` Sparse Frontier: sparse attention trade-offs are task/phase dependent, especially prefill versus decode.
- `SRC-0297` PolyStep: forward-only optimization for hard routers, argmax attention, int8, and other non-differentiable components.
- `SRC-0298` Task-structure reversal: state-encoding profiles are task+architecture properties.
- `SRC-0299` Generic triple-latent compression: possible compression-vs-recall split.
- `SRC-0300` STOF sparse inference: systems reminder that sparse masks need kernel/fusion realization.

## New code lanes

Five C++ probes were added. The strongest P0 candidate is probably `sparse_frontier_isoflops`, because it can unify several older sparse/cache/real-speed concerns under an equal-budget phase diagram.

## Fresh questions

- Does transport assignment help only under capacity/rare/shifting regimes?
- Does sparse output speed require feature reuse more than sparsity?
- Should prefill and decode be treated as separate datacube phase cells?
- Can dynamic short convolution be rescued by explicit bypass/gating?
- When is forward-only optimization worth its query cost?
