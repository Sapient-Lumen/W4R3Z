# Rev0011 scout notes

The hunt added three code-backed lanes rather than only more paper rows:

1. **Entropy-guided budget allocation** — EntropyInfer and head-aware cache papers suggest head/segment budgets should be online and context-shaped.
2. **Reasoning cache sharing + early exit** — RKSC-style branch sharing is promising but has obvious near-miss and confidence-trap failure modes.
3. **Agentic DFS normal form** — tree search/backtracking is a clean mechanistic toy for specialized action-trace and failure-trace heads.

Secondary additions: STaR-KV spatio-temporal cache drift, exact linear attention kernel tests, context-intensive extraction stressors, and systems sharding analogies.

## Reconsidered stance

The cube should not escalate directly to a baby language model. The next trained-model candidate should be a tiny agentic/search or SMT-style memory updater only after the symbolic probes show nontrivial separation.
