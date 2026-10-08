# rev0033 scout notes

Focus: routing mechanisms that are performance-core, not side-wing safety.

- Routing Absorption suggests learned sparse-attention gates can be absorbed by representation co-adaptation, making random gates hard to beat.
- Directional Routing suggests a router can matter as a shared coordination/suppression mechanism, not just a token selector.
- Self-Routing suggests hidden-state subspaces may replace learned router projections in some MoE regimes.
- Contribution Weights provides a geometry guard: attention mass ignores value norm and directional alignment.

Working split: token-selection routers are vulnerable to absorption; coordination routers may remain useful because they change inter-head computation rather than merely selecting entries.
