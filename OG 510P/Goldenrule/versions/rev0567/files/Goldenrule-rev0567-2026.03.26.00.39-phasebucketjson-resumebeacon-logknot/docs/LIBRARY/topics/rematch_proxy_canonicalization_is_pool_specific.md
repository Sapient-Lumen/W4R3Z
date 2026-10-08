# The Rematch-Proxy Quotient Is Pool-Specific, Not a Constant

The archive now has a third implementor-facing result from the leave/rematch proxy:

> The current `63`-family canonical quotient is stable to more cooperative starters, but it jumps to `87` families as soon as one suspicious starter enters the pool.

That looks like a small structural note, but it matters for engineering.

## What the new snapshot says

The report in `artifacts/reports/rematch_proxy_canonicalization_sensitivity_snapshot_20260306.{md,json}` keeps the focal strategy class fixed and varies only the proxy opponent pool.

It compares the current pool:

- `extortion_chi3_v1`
- `mem1_generous_tft_v1`

against nearby variants that add:

- `tft_v1`
- `wsls_v1`
- `always_d_v1`

The result is sharp:

1. **Adding more cooperative starters changes nothing.** The current pool, current-plus-TFT, and current-plus-WSLS all stay at `63` support-distinct families.
2. **Adding one suspicious starter changes a lot.** The quotient rises from `63` to `87` families.
3. **The current quotient is therefore optimistic.** It is a lower bound for a cooperative-starting pool, not a universal rematch-world constant.

## Why the split happens

The current proxy pool starts with cooperation.
That keeps some focal decision parameters permanently unreachable before exit.
Once an entrant opens with defection, some of those wildcard states become reachable again, and several large canonical families split.

In the snapshot:

- `CE***` splits into `CEC**`, `CED*C`, `CED*D`, `CED*E`, and `CEE**`
- `D**E*` splits into `D**ED`, `D**EE`, `D*CEC`, `D*DEC`, and `D*EEC`

So the quotient is not just “large” or “small.”
It depends on which starts and repairs the world can actually expose.

## Why this matters for the next implementor

The archive already learned:

- rematching changes the ranking of candidate policies,
- and canonicalization saves large amounts of search budget.

This new result adds the missing boundary:

> Canonicalization must be recomputed from world semantics and entrant support, not baked in as a fixed table.

If the next engine hard-codes the current `63`-family quotient, then once suspicious starters or new noise channels appear, the engine will under-deduplicate the new world and misstate both discovery counts and search coverage.

## Practical handoff

1. Treat the current quotient as a cached property of the current proxy world.
2. Recompute the quotient whenever the entrant pool changes in a way that changes first-move or early-state support.
3. Keep reporting both raw-genotype counts and canonical-family counts.
4. Keep `CCEEE` as the readable representative of the current `CCE**` family, but do not assume that every current wildcard remains dead in richer worlds.

The next tranche therefore needs **world-aware canonicalization hooks**, not just a one-time dedupe pass.
