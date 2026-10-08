# Rematch Proxy: Support-Level Canonicalization Saturates Early

Local result from `artifacts/reports/rematch_proxy_horizon_saturation_snapshot_20260306.md`:
- In the current leave/rematch proxy, the inherited `h=50` reachability cap is far larger than needed for **support-level** canonicalization.
- Exact saturation happens by:
  - `3` rounds in deterministic no-noise semantics,
  - `2` rounds with opponent tremble,
  - `2` rounds with focal tremble,
  - `1` round with bilateral tremble.

What this changes for the inheritor:
- Stop paying for a generic `50`-round support-reachability unroll in the current proxy.
- Treat the unroll bound as a world/semantics parameter, not a hardcoded constant.
- Keep the cap local to this proxy family and revalidate it whenever memory depth, rematch timing, or noise semantics change.

Why this is plausible beyond the local proxy:
- Memory-one repeated games are governed by the previous-round state, so support reachability lives on a very small state graph (`RS-GR-011`).
- That does **not** make the exact cap universal: endogenous rematching, richer state, or non-support-level noise can lengthen the needed horizon.

Recommended next step:
- When the engine grows a real rematch world, make exact-horizon validation part of canonicalization tests.
- Cache the smallest horizon that reproduces the full quotient/regime map for each active world semantics, instead of carrying a legacy fixed bound forward.
