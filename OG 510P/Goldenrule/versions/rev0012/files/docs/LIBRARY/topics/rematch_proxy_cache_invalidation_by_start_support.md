# Rematch-Proxy Cache Invalidation by Start Support

The new support-signature sweep in `artifacts/reports/rematch_proxy_start_support_gate_snapshot_20260306.{md,json}` sharpens the current rematch-proxy handoff into one implementable gate.

## Local result

Against the current proxy pool (`extortion_chi3_v1`, `mem1_generous_tft_v1`):

- all `81` memory-one entrant support signatures with `C`-only initial support leave the canonical quotient unchanged at `63` families,
- all `162` support signatures whose initial support includes `D` invalidate that cache,
- the reopened quotient then lands somewhere in `87`–`99` families depending on later support.

This is stronger than the previous deterministic-opponent note because it covers mixed-start support as well as pure `D`-openers.

## Why this matters

The current proxy already showed that canonicalization is pool-specific. This pass adds a cheap first trigger for the implementor:

1. inspect the initial action support of any newly admitted entrant,
2. if every entrant is `C`-only on the first move, the current cooperative-start quotient is still safe to reuse in this proxy,
3. if any entrant can open with `D`, invalidate the cache and recompute.

That is a useful engineering win because rematch/restart worlds are already computationally nontrivial in the literature; even deciding optimal restart-style equilibria can be hard, so cheap sound cache gates are worth preserving. See Berker & Conitzer (2024), *Computing Optimal Equilibria in Repeated Games with Restarts* (`RS-GR-009`).

## Boundary

This is still a proxy-world rule, not a universal theorem.

- It is tied to the current deterministic no-noise leave/rematch proxy.
- It should be treated as a conservative gate for cache reuse, not as permission to replace recomputation with a fixed “D-start quotient”.
- Once the endogenous rematch world lands, the same start-support check should be rerun under the real outside-option and matching semantics.

## What the inheritor should build next

- Put an initial-support gate into the rematch-world canonicalization cache.
- Make the cache key depend on support semantics, not just named strategies.
- Recompute the quotient whenever the entrant pool gains first-move `D` support or when noise/outside-option semantics can create equivalent reachability drift.
