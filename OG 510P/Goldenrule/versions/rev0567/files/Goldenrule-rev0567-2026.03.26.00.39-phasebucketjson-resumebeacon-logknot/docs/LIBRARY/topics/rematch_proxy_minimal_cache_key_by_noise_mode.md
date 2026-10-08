# Rematch Proxy: Minimal Cache Key Depends on Noise Topology

Local result from `artifacts/reports/rematch_proxy_cache_regime_snapshot_20260306.md`:
- In the current leave/rematch proxy, canonicalization caches do **not** need one universal key shape.
- The exact quotient-set regime count is:
  - `17` in deterministic no-noise semantics,
  - `1` with opponent tremble,
  - `2` with focal tremble,
  - `1` with bilateral tremble.

What this changes for the inheritor:
- Treat cache-key design as a world-semantics problem, not just an entrant-signature problem.
- In the current proxy:
  - deterministic no-noise keeps the earlier `C`-only fast path, but later support still matters once initial-`D` entrants appear;
  - opponent-tremble and bilateral-tremble modes can key on noise mode alone;
  - focal-tremble mode can key on noise mode plus whether the entrant can initially defect.

Why this is plausible beyond the local proxy:
- Implementation-error semantics change which histories remain behaviorally relevant, so error models belong in the world contract rather than in an after-the-fact optimization layer (`RS-GR-010`).
- Restart / rematch worlds are already computationally nontrivial, so eliminating needless cache distinctions is worthwhile as long as the key stays sound (`RS-GR-009`).

Recommended next step:
- When the endogenous rematch world lands, specify cache keys explicitly as `(world_semantics, reachability_regime, entrant_support_class)` rather than keying blindly on full entrant genotype.
- Then test whether the current proxy's regime compression survives outside-option timing, endogenous partner pools, and non-support-level noise models.
